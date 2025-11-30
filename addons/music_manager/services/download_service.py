# -*- coding: utf-8 -*-
import io
import hashlib
import logging
import subprocess
from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Protocol

from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, MaxDownloadsReached, RegexNotFoundError, UnavailableVideoError, YoutubeDLError

from ..utils.custom_types import OptionDownloadSettings
from ..utils.exceptions import ClientPlatformError, VideoProcessingError, MusicManagerError


_logger = logging.getLogger(__name__)


# ---- Protocol ---- #
class StreamProtocol(Protocol):
    def stream_to_file(self, output_path: Path) -> None:
        ...

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        ...


# ---- Adapters ---- #
class PyTubeAdapter(StreamProtocol):  # ❌️ Library no updated -> It does not work
    def __init__(self, url: str) -> None:
        self._url = url
        self._tmp_path = Path('/tmp')

    @property
    def url(self) -> str:
        return self._url

    @property
    def tmp_path(self) -> Path:
        return self._tmp_path

    def stream_to_file(self, output_path: Path) -> None:
        filename = hashlib.sha256(self._url.encode()).hexdigest()
        download_path = self._download_track(self._tmp_path, filename)

        self._subprocess_track_to_mp3(download_path, output_path)
        self._clean_temp_file(download_path)

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        filename = hashlib.sha256(self._url.encode()).hexdigest()
        download_path = self._download_track(self._tmp_path, filename)
        final_path = self._tmp_path / f'{filename}.mp3'

        self._subprocess_track_to_mp3(download_path, final_path)

        try:
            with open(final_path, 'rb') as new_song:
                buffer.write(new_song.read())

        except FileNotFoundError as not_found:
            _logger.error(f"Failed to open file '{final_path}': {not_found}")
            raise VideoProcessingError(not_found)

        self._clean_temp_file(download_path)
        self._clean_temp_file(final_path)

    def _download_track(self, tmp_path: Path, filename: str) -> Path:
        try:
            video = YouTube(self._url)
            stream = video.streams.filter(only_audio=True).first()
            download_path = stream.download(output_path=f'{tmp_path}', filename=filename)
            return Path(download_path)

        except (RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as video_error:
            _logger.error(f"Failed to process YouTube URL '{self._url}': {video_error}")
            raise ClientPlatformError(video_error)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while processing the download: {unknown_error}")
            raise MusicManagerError(unknown_error)

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

    @staticmethod
    def _subprocess_track_to_mp3(download_path: Path, output_path: Path) -> None:
        result = subprocess.run(
            args=['ffmpeg', '-i', f'{download_path}', '-vn', '-ab', '192k', '-ar', '44100', '-y', f'{output_path}'],
            capture_output=True,
        )

        if result.returncode != 0:
            _logger.error(f"FFmpeg failed: {result.stderr.decode()}")
            raise VideoProcessingError(result.stderr.decode())


class YTDLPAdapter(StreamProtocol):

    DEFAULT_OPTIONS = {
        'format': 'bestaudio/best',
        'quiet': False,
        'keepvideo': False,
        'noplaylist': True,
        'no_warnings': True,
        'prefer_ffmpeg': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            },
            {
                'key': 'FFmpegMetadata'
            },
        ]
    }

    def __init__(self, url: str, options: OptionDownloadSettings | None = None) -> None:
        self._url = url
        self._options = deepcopy(self.DEFAULT_OPTIONS)
        self._tmp_path = Path('/tmp')

        if options:
            self._options.update(options)

    def stream_to_file(self, output_path: Path) -> None:
        options = self._get_download_options(output_path)
        self._download_track(options)

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        filename = hashlib.sha256(self._url.encode()).hexdigest()
        tmp_path = self._tmp_path / filename
        final_path = self._tmp_path / f'{filename}.mp3'

        options = self._get_download_options(tmp_path)
        self._download_track(options)

        try:
            with open(final_path, 'rb') as new_song:
                buffer.write(new_song.read())

        except FileNotFoundError as not_found:
            _logger.error(f"Failed to open file '{final_path}': {not_found}")
            raise VideoProcessingError(not_found)

        self._clean_temp_file(final_path)

    def _download_track(self, options: OptionDownloadSettings) -> None:
        try:
            with YoutubeDL(options) as youtube_dl:
                youtube_dl.download([self._url])

        except RegexNotFoundError as invalid_url:
            _logger.error(f"Failed to process YouTube URL '{self._url}': {invalid_url}")
            raise ClientPlatformError(invalid_url)

        except (DownloadError, MaxDownloadsReached, UnavailableVideoError) as download_error:
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
