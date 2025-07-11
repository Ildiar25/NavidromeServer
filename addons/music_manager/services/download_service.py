import io
import hashlib
import logging
import os
import yt_dlp
from abc import ABC, abstractmethod
from pytube import Stream
from typing import Protocol


_logger = logging.getLogger(__name__)


# ---- Protocol ---- #
class StreamProtocol(Protocol):
    def stream_to_file(self, output_path: str) -> None:
        ...

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        ...


# ---- Adapters ---- #
class PyTubeAdapter:  # ❌ No updated -> It does not work
    def __init__(self, stream: Stream) -> None:
        self.__stream = stream

    def stream_to_file(self, output_path: str) -> None:
        self.__stream.download(output_path)

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        self.__stream.stream_to_buffer(buffer)


class YTDLPAdapter:
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

        with yt_dlp.YoutubeDL(options) as yotube_dl:
            yotube_dl.download(
                [self.__url]
            )

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

        with yt_dlp.YoutubeDL(options) as yotube_dl:
            yotube_dl.download(
                [self.__url]
            )

        with open(f'{tmp_path}.mp3', 'rb') as new_song:
            track = new_song.read()
            buffer.write(track)

        os.remove(f'{tmp_path}.mp3')


# ---- Donwload service ---- #
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
