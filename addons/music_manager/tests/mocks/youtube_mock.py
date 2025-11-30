from typing import Any, List, ContextManager, Type
from unittest.mock import MagicMock, patch

from pytube import YouTube, Stream, StreamQuery
from pytube.exceptions import RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable

from .base_mock_helper import BaseMock


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
    """

    YT_CONSTRUCTOR = 'odoo.addons.music_manager.services.download_service.YouTube'
    EXTRACT_VIDEO_ID = 'pytube.extract.video_id'

    @classmethod
    def success(cls) -> ContextManager[List[MagicMock]]:
        stream_mock = cls.create_mock(Stream)
        stream_mock.download.return_value = '/fake/video.mp4'

        youtube_mock = cls.create_mock(YouTube, streams=cls.create_mock(StreamQuery))
        youtube_mock.streams.filter.return_value.first.return_value = stream_mock

        patch_video = patch(cls.EXTRACT_VIDEO_ID, return_value="Fake video ID")
        patch_youtube = patch(cls.YT_CONSTRUCTOR, return_value=youtube_mock)

        return cls._stack(patch_video, patch_youtube)

    @classmethod
    def with_regex_match_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.EXTRACT_VIDEO_ID, side_effect=RegexMatchError(caller='Fake caller', pattern='Fake pattern'))

    @classmethod
    def with_video_private_error(cls):
        patch_video = patch(cls.EXTRACT_VIDEO_ID, return_value="Fake video ID")
        patch_youtube = patch(cls.YT_CONSTRUCTOR, side_effect=cls.simulate_error(VideoPrivate))

        return cls._stack(patch_video, patch_youtube)

    @classmethod
    def with_video_region_blocked_error(cls) -> ContextManager[List[MagicMock]]:
        patch_video = patch(cls.EXTRACT_VIDEO_ID, return_value="Fake video ID")
        patch_youtube = patch(cls.YT_CONSTRUCTOR, side_effect=cls.simulate_error(VideoRegionBlocked))

        return cls._stack(patch_video, patch_youtube)

    @classmethod
    def with_video_unavailable_error(cls) -> ContextManager[List[MagicMock]]:
        patch_video = patch(cls.EXTRACT_VIDEO_ID, return_value="Fake video ID")
        patch_youtube = patch(cls.YT_CONSTRUCTOR, side_effect=cls.simulate_error(VideoUnavailable))

        return cls._stack(patch_video, patch_youtube)

    @classmethod
    def _stack(cls, *patchers) -> ContextManager[Any]:
        class _Context:
            def __enter__(self) -> List[Any]:
                self.started = [new_patch.start() for new_patch in patchers]
                return self.started

            def __exit__(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: Any | None) -> None:
                for new_patch in patchers:
                    new_patch.stop()

        return _Context()
