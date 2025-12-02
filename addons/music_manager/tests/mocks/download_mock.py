import io
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Type, TypeVar
from unittest.mock import MagicMock

from .base_mock_helper import BaseMock
from .ffmpeg_mock import FFmpegMock
from .path_mock import PathMock
from .youtube_mock import YouTubeMock
from ...utils.custom_types import StreamToFileContext
from ...services.download_service import StreamProtocol


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


class DownloadMock(BaseMock):
    """
    Simulates different behaviours when downloading files.

    Operations covered:
    -------------------
    - stream_to_buffer
    - stream_to_file

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    """

    @classmethod
    def stream_to_buffer_success(cls) -> MagicMock:
        stream_mock = cls._mock_stream_protocol_helper('stream_to_buffer')

        def write_example_bytes(buffer: io.BytesIO):
            buffer.write(b"Fake mp3")

        stream_mock.stream_to_buffer.side_effect = write_example_bytes
        return stream_mock

    @classmethod
    def stream_to_file_success(cls) -> MagicMock:
        return cls._mock_stream_protocol_helper('stream_to_file')

    @classmethod
    def _mock_stream_protocol_helper(
            cls,
            method_name: str,
            return_value: Optional[Any] = None,
            error_name: Type[ExceptionType] | None = None,
            message: str | None = None
    ) -> MagicMock:

        stream_protocol_mock = cls.create_mock(StreamProtocol)
        method_mock = getattr(stream_protocol_mock, method_name)

        if error_name:
            method_mock.side_effect = cls.simulate_error(error_name, message)

        else:
            method_mock.return_value = return_value

        return stream_protocol_mock


class PytubeAdapterMock(BaseMock):
    """
    Simulates different PyTube behaviours.

    Operations covered:
    -------------------
    - stream_to (default class behaviour)

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    - RegexMatchError
    - VideoPrivate
    - VideoRegionBlocked
    - VideoUnavailable
    - FileNotFoundError
    - PermissionError
    """

    @classmethod
    @contextmanager
    def stream_to_success(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.success() as youtube_mock,
            FFmpegMock.success() as ffmpeg_mock,
            PathMock.success() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }

    @classmethod
    @contextmanager
    def stream_to_with_regex_match_error(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.with_regex_match_error() as youtube_mock,
            FFmpegMock.success() as ffmpeg_mock,
            PathMock.success() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }

    @classmethod
    @contextmanager
    def stream_to_with_video_private_error(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.with_video_private_error() as youtube_mock,
            FFmpegMock.success() as ffmpeg_mock,
            PathMock.success() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }

    @classmethod
    @contextmanager
    def stream_to_with_video_region_blocked_error(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.with_video_region_blocked_error() as youtube_mock,
            FFmpegMock.success() as ffmpeg_mock,
            PathMock.success() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }

    @classmethod
    @contextmanager
    def stream_to_with_video_unavailable_error(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.with_video_unavailable_error() as youtube_mock,
            FFmpegMock.success() as ffmpeg_mock,
            PathMock.success() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }

    @classmethod
    @contextmanager
    def stream_to_with_subprocess_error(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.success() as youtube_mock,
            FFmpegMock.error() as ffmpeg_mock,
            PathMock.success() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }

    @classmethod
    @contextmanager
    def stream_to_with_file_not_found_error(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.success() as youtube_mock,
            FFmpegMock.success() as ffmpeg_mock,
            PathMock.with_file_not_found_error() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }

    @classmethod
    @contextmanager
    def stream_to_with_permission_error(cls) -> Iterator[StreamToFileContext]:
        with (
            YouTubeMock.success() as youtube_mock,
            FFmpegMock.success() as ffmpeg_mock,
            PathMock.with_permission_error() as path_mock
        ):
            yield {
                'youtube': youtube_mock,
                'ffmpeg': ffmpeg_mock,
                'unlink': path_mock
            }


class YTDLPAdapterMock(BaseMock):
    """
    Simulates different YTDLP behaviours.

    Operations covered:
    -------------------
    - stream_to_buffer
    - stream_to_file

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    """

    @classmethod
    def _mock_ytdpl_helper(
            cls,
            method_name: str,
            return_value: Optional[Any] = None,
            error_name: Type[ExceptionType] | None = None,
            message: str | None = None
    ) -> MagicMock:
        pass
