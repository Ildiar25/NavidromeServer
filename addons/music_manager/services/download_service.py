# -*- coding: utf-8 -*-
import io
import hashlib
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol

from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, MaxDownloadsReached, RegexNotFoundError, UnavailableVideoError, YoutubeDLError

from ..utils.exceptions import DownloadServiceError, MusicManagerError


_logger = logging.getLogger(__name__)


# ---- Protocol ---- #
class StreamProtocol(Protocol):
    def stream_to_file(self, output_path: str) -> None:
        ...

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        ...


# ---- Adapters ---- #
class PyTubeAdapter(StreamProtocol):  # ❌ Library no updated -> It does not work
    def __init__(self, url: str) -> None:
        self.__url = url

    def stream_to_file(self, output_path: str) -> None:

        filename = hashlib.sha256(self.__url.encode()).hexdigest()
        tmp_path = '/tmp/'

        try:
            video = YouTube(self.__url)
            stream = video.streams.filter(only_audio=True).first()
            download_path = stream.download(output_path=tmp_path, filename=filename)

        except (RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as video_error:
            _logger.warning(f"Failed to process YouTube URL {self.__url}: {video_error}")
            raise DownloadServiceError(video_error)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while validating URL {self.__url}: {unknown_error}")
            raise MusicManagerError(unknown_error)

        result = subprocess.run(
                args=['ffmpeg', '-i', download_path, '-vn', '-ab', '192k', '-ar', '44100', '-y', f'{output_path}.mp3'],
                capture_output=True
            )

        if result.returncode != 0:
            _logger.error(f"FFmpeg failed: {result.stderr.decode()}")
            raise DownloadServiceError(result.stderr.decode())

        try:
            os.remove(f'{download_path}')

        except PermissionError as permission_error:
            _logger.info(f"Can not delete file '{download_path}.mp3': {permission_error}")
            raise DownloadServiceError(permission_error)

        except FileNotFoundError as not_found:
            _logger.info(f"Failed to delete file '{download_path}.mp3': {not_found}")
            raise DownloadServiceError(not_found)

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:

        filename = hashlib.sha256(self.__url.encode()).hexdigest()
        tmp_path = Path('/tmp/')

        try:
            video = YouTube(self.__url)
            stream = video.streams.filter(only_audio=True).first()
            download_path = stream.download(output_path=tmp_path, filename=filename)

        except (RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as video_error:
            _logger.warning(f"Failed to process YouTube URL {self.__url}: {video_error}")
            raise DownloadServiceError(video_error)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while validating URL {self.__url}: {unknown_error}")
            raise MusicManagerError(unknown_error)

        result = subprocess.run(
            args=['ffmpeg', '-i', download_path, '-vn', '-ab', '192k',
                  '-ar', '44100', '-y', f'{tmp_path.joinpath(filename)}.mp3'],
            capture_output=True
        )

        if result.returncode != 0:
            _logger.error(f"FFmpeg failed: {result.stderr.decode()}")
            raise DownloadServiceError(result.stderr.decode())

        try:
            with open(f'{tmp_path.joinpath(filename)}.mp3', 'rb') as new_song:
                track = new_song.read()
                buffer.write(track)

        except FileNotFoundError as not_found:
            _logger.info(f"Failed to open file '{tmp_path}.mp3': {not_found}")
            raise DownloadServiceError(not_found)

        try:
            os.remove(f'{download_path}')

        except PermissionError as permission_error:
            _logger.info(f"Can not delete file '{download_path}.mp3': {permission_error}")
            raise DownloadServiceError(permission_error)

        except FileNotFoundError as not_found:
            _logger.info(f"Failed to delete file '{download_path}.mp3': {not_found}")
            raise DownloadServiceError(not_found)


class YTDLPAdapter(StreamProtocol):
    def __init__(self, url: str) -> None:
        self.__url = url

    def stream_to_file(self, output_path: str) -> None:
        options = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': True,
            'prefer_ffmpeg': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                },
            ]
        }

        try:
            with YoutubeDL(options) as yotube_dl:
                yotube_dl.download(
                    [self.__url]
                )
        except (DownloadError, MaxDownloadsReached, UnavailableVideoError, YoutubeDLError) as video_error:
            _logger.warning(f"Failed to process YouTube download {self.__url}: {video_error}")
            raise DownloadServiceError(video_error)

        except RegexNotFoundError as invalid_url:
            _logger.warning(f"Failed to process YouTube URL {self.__url}: {invalid_url}")
            raise DownloadServiceError(invalid_url)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while validating URL {self.__url}: {unknown_error}")
            raise MusicManagerError(unknown_error)

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:

        filename = hashlib.sha256(self.__url.encode()).hexdigest()
        tmp_path = f'/tmp/{filename}'

        options = {
            'format': 'bestaudio/best',
            'outtmpl': tmp_path,
            'quiet': False,
            'no_warnings': True,
            'prefer_ffmpeg': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                },
            ]
        }

        try:
            with YoutubeDL(options) as yotube_dl:
                yotube_dl.download(
                    [self.__url]
                )

        except (DownloadError, MaxDownloadsReached, UnavailableVideoError, YoutubeDLError) as video_error:
            _logger.warning(f"Failed to process YouTube download {self.__url}: {video_error}")
            raise DownloadServiceError(video_error)

        except RegexNotFoundError as invalid_url:
            _logger.warning(f"Failed to process YouTube URL {self.__url}: {invalid_url}")
            raise DownloadServiceError(invalid_url)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error while validating URL {self.__url}: {unknown_error}")
            raise MusicManagerError(unknown_error)

        try:
            with open(f'{tmp_path}.mp3', 'rb') as new_song:
                track = new_song.read()
                buffer.write(track)

        except FileNotFoundError as not_found:
            _logger.info(f"Failed to open file '{tmp_path}.mp3': {not_found}")
            raise DownloadServiceError(not_found)

        try:
            os.remove(f'{tmp_path}.mp3')

        except PermissionError as permission_error:
            _logger.info(f"Can not delete file '{tmp_path}.mp3': {permission_error}")
            raise DownloadServiceError(permission_error)

        except FileNotFoundError as not_found:
            _logger.info(f"Failed to delete file '{tmp_path}.mp3': {not_found}")
            raise DownloadServiceError(not_found)


# ---- Download service ---- #
class DownloadTrack(ABC):

    @abstractmethod
    def set_stream_to_file(self, stream: StreamProtocol, output_path: str) -> None:
        ...

    @abstractmethod
    def set_stream_to_buffer(self, stream: StreamProtocol, buffer: io.BytesIO) -> bytes:
        ...


class YoutubeDownload(DownloadTrack):

    def set_stream_to_file(self, stream: StreamProtocol, output_path: str) -> None:
        stream.stream_to_file(output_path)

    def set_stream_to_buffer(self, stream: StreamProtocol, buffer: io.BytesIO) -> bytes:
        stream.stream_to_buffer(buffer)
        buffer.seek(0)
        return buffer.read()
