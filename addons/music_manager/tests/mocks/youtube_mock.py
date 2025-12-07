import io
from typing import ContextManager, Type, TypeVar
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from pytube import YouTube, Stream, StreamQuery
from pytube.exceptions import RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable

from .base_mock_helper import BaseMock


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


class YouTubeMock(BaseMock):
    """
    Simulates different YouTube behaviours.

    Operations covered:
    -------------------
    - Instantiation
    - Streams
    - Download

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    - RegexMatchError
    - VideoPrivate
    - VideoRegionBlocked
    - VideoUnavailable
    - HTTPError
    - OSError
    """

    YT_CONSTRUCTOR = 'odoo.addons.music_manager.services.download_service.YouTube'

    @classmethod
    def success(cls) -> ContextManager[MagicMock]:
        youtube_mocked = cls._youtube_mock_helper()
        return patch(cls.YT_CONSTRUCTOR, return_value=youtube_mocked)

    @classmethod
    def with_regex_match_error(cls) -> ContextManager[MagicMock]:
        return patch(
            cls.YT_CONSTRUCTOR,
            side_effect=cls.simulate_error(RegexMatchError, caller='Fake caller', pattern='Fake pattern')
        )

    @classmethod
    def with_video_private_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.YT_CONSTRUCTOR, side_effect=cls.simulate_error(VideoPrivate))

    @classmethod
    def with_video_region_blocked_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.YT_CONSTRUCTOR, side_effect=cls.simulate_error(VideoRegionBlocked))

    @classmethod
    def with_video_unavailable_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.YT_CONSTRUCTOR, side_effect=cls.simulate_error(VideoUnavailable))

    @classmethod
    def with_http_error(cls) -> ContextManager[MagicMock]:
        youtube_mocked = cls._youtube_mock_helper(
            error_name=HTTPError,
            url="https://www.testing.com/",
            code=404,
            msg="Test file not found",
            hdrs={'Content-Type': 'text/plain'},
            fp=io.BytesIO(b'File not found')
        )
        return patch(cls.YT_CONSTRUCTOR, return_value=youtube_mocked)

    @classmethod
    def with_os_error(cls) -> ContextManager[MagicMock]:
        youtube_mocked = cls._youtube_mock_helper(error_name=OSError)
        return patch(cls.YT_CONSTRUCTOR, return_value=youtube_mocked)

    @classmethod
    def _youtube_mock_helper(
            cls,
            error_name: Type[ExceptionType] | None = None,
            message: str | None = None,
            **kwargs,
    ) -> MagicMock:

        stream_instance = cls.create_mock(Stream)

        if error_name:
            stream_instance.download.side_effect = cls.simulate_error(error_name, message, **kwargs)

        else:
            stream_instance.download.return_value = '/fake/video/path.mp4'

        stream_query = cls.create_mock(StreamQuery)
        stream_query.filter.return_value.first.return_value = stream_instance

        return cls.create_mock(YouTube, streams=stream_query)
