# -*- coding: utf-8 -*-
import hashlib
import io
import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Protocol

from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, MaxDownloadsReached, RegexNotFoundError, UnavailableVideoError, YoutubeDLError

from ..utils.custom_types import OptionDownloadSettings
from ..utils.exceptions import ClientPlatformError, MusicManagerError, VideoProcessingError


_logger = logging.getLogger(__name__)


# ---- Protocol ---- #
class StreamProtocol(Protocol):
    def stream_to_file(self, output_path: Path) -> None:
        ...

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        ...


# ---- Adapters ---- #
class PyTubeAdapter(StreamProtocol):  # ❌️ Library no updated -> It does not work
    def __init__(self, url: str, config: Dict[str, str]) -> None:
        self._url = url
        self._tmp_path = Path('/tmp')
        self._options = self._get_pytube_options(config)

    @property
    def url(self) -> str:
        return self._url

    @property
    def tmp_path(self) -> str:
        return str(self._tmp_path)

    @property
    def options(self) -> Dict[str, str]:
        return self._options

    def stream_to_file(self, output_path: Path) -> None:
        filename = hashlib.sha256(self._url.encode()).hexdigest()
        download_path = self._download_track(self._tmp_path, filename)

        self._subprocess_track_to_mp3(download_path, output_path)
        self._clean_temp_file(download_path)

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        filename = hashlib.sha256(self._url.encode()).hexdigest()
        download_path = self._download_track(self._tmp_path, filename)
        final_path = self._tmp_path / f"{filename}.{self._options['format']}"

        self._subprocess_track_to_mp3(download_path, final_path)

        try:
            with open(final_path, 'rb') as new_song:
                buffer.write(new_song.read())

        except (FileNotFoundError, PermissionError) as not_allowed:
            _logger.error(f"Failed to open file '{final_path}': {not_allowed}")
            raise VideoProcessingError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while reading downloaded file: {unknown_error}")
            raise MusicManagerError(unknown_error)

        self._clean_temp_file(download_path)
        self._clean_temp_file(final_path)

    def _download_track(self, tmp_path: Path, filename: str) -> Path:
        try:
            video = YouTube(self._url)
            stream = video.streams.filter(only_audio=True).order_by('abr').desc().first()
            download_path = stream.download(output_path=f'{tmp_path}', filename=filename)
            return Path(download_path)

        except (RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as video_error:
            _logger.error(f"Failed to process YouTube URL '{self._url}': {video_error}")
            raise ClientPlatformError(video_error)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while processing the download: {unknown_error}")
            raise MusicManagerError(unknown_error)

    def _get_ffmpeg_args(self, download_path: Path, output_path: Path) -> List[str]:

        quality = self._options.get('quality')
        file_format = self._options.get('format')
        args = ["ffmpeg", "-i", f"{download_path}", "-vn"]

        if quality and quality != '0':
            args.extend(["-ab", f"{self._options['quality']}k"])

        elif quality == '0' and file_format == 'mp3':
            args.extend(["-q:a", "0"])

        args.extend(["-y", f"{output_path}"])
        return args

    @staticmethod
    def _get_pytube_options(config: Dict[str, str]) -> OptionDownloadSettings:

        file_format = config.get('format', 'mp3')
        bitrate = config.get('quality', '192')

        is_lossless = file_format in ('wav', 'flac')

        return {
            'format': file_format,
            'quality': '0' if is_lossless else bitrate,
        }

    @staticmethod
    def _clean_temp_file(filepath: Path) -> None:
        try:
            filepath.unlink()

        except (PermissionError, FileNotFoundError) as system_error:
            _logger.error(f"File not found or no permission to delete: {system_error}")
            raise VideoProcessingError(system_error)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while deleting path '{filepath}': {unknown_error}")
            raise MusicManagerError(unknown_error)

    def _subprocess_track_to_mp3(self, download_path: Path, output_path: Path) -> None:
        result = subprocess.run(
            args=self._get_ffmpeg_args(download_path, output_path),
            capture_output=True,
        )

        if result.returncode != 0:
            _logger.error(f"FFmpeg failed: {result.stderr.decode()}")
            raise VideoProcessingError(result.stderr.decode())


class YTDLPAdapter(StreamProtocol):

    def __init__(self, url: str, config: Dict[str, str]) -> None:
        self._url = url
        self._options = self._get_ytdlp_options(config)
        self._tmp_path = Path('/tmp')

    @property
    def url(self) -> str:
        return self._url

    @property
    def options(self) -> OptionDownloadSettings:
        return self._options

    @property
    def tmp_path(self) -> str:
        return str(self._tmp_path)

    def stream_to_file(self, output_path: Path) -> None:
        options = self._get_download_options(output_path)
        self._download_track(options)

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        filename = hashlib.sha256(self._url.encode()).hexdigest()
        file_format = self._options['postprocessors'][0]['preferredcodec']

        tmp_path = self._tmp_path / filename
        final_path = self._tmp_path / f"{filename}.{file_format}"

        options = self._get_download_options(tmp_path)
        self._download_track(options)

        try:
            with open(final_path, 'rb') as new_song:
                buffer.write(new_song.read())

        except (FileNotFoundError, PermissionError) as not_allowed:
            _logger.error(f"Failed to open file '{final_path}': {not_allowed}")
            raise VideoProcessingError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while reading downloaded file: {unknown_error}")
            raise MusicManagerError(unknown_error)

        self._clean_temp_file(final_path)

    def _download_track(self, options: OptionDownloadSettings) -> None:
        try:
            with YoutubeDL(options) as youtube_dl:
                youtube_dl.download([self._url])

        except RegexNotFoundError as invalid_url:
            _logger.error(f"Failed to process YouTube URL '{self._url}': {invalid_url}")
            raise ClientPlatformError(invalid_url)

        except (MaxDownloadsReached, UnavailableVideoError, DownloadError) as download_error:
            _logger.error(f"Failed to download '{self._url}': {download_error}")
            raise ClientPlatformError(download_error)

        except YoutubeDLError as service_error:
            _logger.error(f"Something went wrong while processing the video: {service_error}")
            raise VideoProcessingError(service_error)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while processing the download: {unknown_error}")
            raise MusicManagerError(unknown_error)

    def _get_download_options(self, file_path: Path) -> OptionDownloadSettings:
        options = self._options.copy()
        options['outtmpl'] = str(file_path.with_suffix(".%(ext)s"))
        return options

    @staticmethod
    def _get_ytdlp_options(config: Dict[str, str]) -> OptionDownloadSettings:
        file_format = config.get('format', 'mp3')
        bitrate = config.get('quality', '192')

        is_lossless = file_format in ('wav', 'flac')

        return {
            'format': 'bestaudio/best',
            'quiet': False,
            'keepvideo': False,
            'noplaylist': True,
            'no_warnings': True,
            'prefer_ffmpeg': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': file_format,
                    'preferredquality': '0' if is_lossless else bitrate,
                },
                {
                    'key': 'FFmpegMetadata'
                },
            ]
        }

    @staticmethod
    def _clean_temp_file(file_path: Path) -> None:
        try:
            file_path.unlink()

        except (PermissionError, FileNotFoundError) as system_error:
            _logger.error(f"File not found or no permission to delete: {system_error}")
            raise VideoProcessingError(system_error)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while deleting path '{file_path}': {unknown_error}")
            raise MusicManagerError(unknown_error)


# ---- Download service ---- #
class DownloadTrack(ABC):

    @abstractmethod
    def set_stream_to_file(self, stream: StreamProtocol, output_path: Path) -> None:
        ...

    @abstractmethod
    def set_stream_to_buffer(self, stream: StreamProtocol, buffer: io.BytesIO) -> bytes:
        ...


class YoutubeDownload(DownloadTrack):

    def set_stream_to_file(self, stream: StreamProtocol, output_path: Path) -> None:
        stream.stream_to_file(output_path)

    def set_stream_to_buffer(self, stream: StreamProtocol, buffer: io.BytesIO) -> bytes:
        stream.stream_to_buffer(buffer)
        buffer.seek(0)
        return buffer.read()
