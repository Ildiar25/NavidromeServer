import io
import yt_dlp
from abc import ABC, abstractmethod
from pytube import Stream
from typing import Protocol
import logging


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
        ydl_opts = {
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(
                [self.__url]
            )

    def stream_to_buffer(self, buffer: io.BytesIO) -> None:
        pass


# ---- Donwload service ---- #
class DownloadTrack(ABC):

    @abstractmethod
    def set_stream_to_file(self, stream: StreamProtocol, output_path: str) -> None:
        ...

    @abstractmethod
    def set_stream_to_buffer(self, stream: StreamProtocol, buffer: io.BytesIO) -> io.BytesIO:
        ...


class YoutubeDownload(DownloadTrack):

    def set_stream_to_file(self, stream: StreamProtocol, output_path: str) -> None:
        stream.stream_to_file(output_path)

    def set_stream_to_buffer(self, stream: StreamProtocol, buffer: io.BytesIO) -> io.BytesIO:
        stream.stream_to_buffer(buffer)
        buffer.seek(0)
        return buffer
