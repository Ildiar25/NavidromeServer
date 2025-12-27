from typing import Any, ContextManager, Optional, Type, TypeVar
from unittest.mock import MagicMock, patch

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, MaxDownloadsReached, RegexNotFoundError, UnavailableVideoError, YoutubeDLError

from .base_mock_helper import BaseMock


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


class YouTubeDLMock(BaseMock):
    """
    Simulates different YouTubeDL behaviors.

    Operations covered:
    -------------------
    - Download

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    - RegexNotFoundError
    - MaxDownloadsReached
    - UnavailableVideoError
    - DownloadError
    - YoutubeDLError
    """

    YT_CONSTRUCTOR = 'odoo.addons.music_manager.services.download_service.YoutubeDL'

    @classmethod
    def success(cls) -> ContextManager[MagicMock]:
        youtube_dl_mock = cls._youtube_dl_mock_helper('download')
        return patch(cls.YT_CONSTRUCTOR, new=youtube_dl_mock)

    @classmethod
    def with_regex_not_found_error(cls) -> ContextManager[MagicMock]:
        youtube_dl_mock = cls._youtube_dl_mock_helper('download', error_name=RegexNotFoundError)
        return patch(cls.YT_CONSTRUCTOR, new=youtube_dl_mock)

    @classmethod
    def with_max_downloads_reached_error(cls) -> ContextManager[MagicMock]:
        youtube_dl_mock = cls._youtube_dl_mock_helper('download', error_name=MaxDownloadsReached)
        return patch(cls.YT_CONSTRUCTOR, new=youtube_dl_mock)

    @classmethod
    def with_unavailable_video_error(cls) -> ContextManager[MagicMock]:
        youtube_dl_mock = cls._youtube_dl_mock_helper('download', error_name=UnavailableVideoError)
        return patch(cls.YT_CONSTRUCTOR, new=youtube_dl_mock)

    @classmethod
    def with_download_error(cls) -> ContextManager[MagicMock]:
        youtube_dl_mock = cls._youtube_dl_mock_helper('download', error_name=DownloadError)
        return patch(cls.YT_CONSTRUCTOR, new=youtube_dl_mock)

    @classmethod
    def with_youtube_dl_error(cls) -> ContextManager[MagicMock]:
        youtube_dl_mock = cls._youtube_dl_mock_helper('download', error_name=YoutubeDLError)
        return patch(cls.YT_CONSTRUCTOR, new=youtube_dl_mock)

    @classmethod
    def with_unknown_error(cls) -> ContextManager[MagicMock]:
        youtube_dl_mock = cls._youtube_dl_mock_helper('download', error_name=Exception)
        return patch(cls.YT_CONSTRUCTOR, new=youtube_dl_mock)

    @classmethod
    def _youtube_dl_mock_helper(
            cls,
            method_name: str,
            return_value: Optional[Any] = None,
            error_name: Type[ExceptionType] | None = None,
            message: str | None = None,
            **kwargs: Any
    ) -> MagicMock:

        youtube_dl_mock = cls.create_mock(YoutubeDL)
        youtube_dl_mock.return_value = youtube_dl_mock

        method_mock = getattr(youtube_dl_mock, method_name)

        if error_name:
            method_mock.side_effect = cls.simulate_error(error_name, message, **kwargs)

        else:
            method_mock.return_value = return_value

        youtube_dl_mock.__enter__.return_value = youtube_dl_mock
        youtube_dl_mock.__exit__.return_value = False

        return youtube_dl_mock
