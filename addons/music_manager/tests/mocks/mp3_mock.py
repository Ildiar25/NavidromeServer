from typing import Any, ContextManager, Optional, Type, TypeVar
from unittest.mock import MagicMock, patch

import mutagen.id3 as mutagen_tags
import mutagen.mp3 as mutagen_mp3

from .base_mock_helper import BaseMock
from ...utils.track_data import TrackMetadata


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


class MP3Mock(BaseMock):

    LAST_SAVED_TAGS = {}

    MOCK_TAG_VALUES = {
        'TIT2': "Title",
        'TPE1': "Track artist",
        'TPE2': "Album artist",
        'TOPE': "Original artist",
        'TALB': "Album",
        'TCMP': "0",
        'TRCK': "1/1",
        'TPOS': "1/1",
        'TDRC': "2025",
        'TCON': "Genre",
        'APIC': b"Cover Image",
    }

    MP3_CONSTRUCTOR = 'odoo.addons.music_manager.services.metadata_service.MP3'

    @classmethod
    def read_mp3_file_success(cls) -> ContextManager[MagicMock]:
        mp3_mocked = cls._mp3_mock_helper()
        return patch(cls.MP3_CONSTRUCTOR, return_value=mp3_mocked)

    @classmethod
    def read_mp3_with_id3_no_header_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.MP3_CONSTRUCTOR, side_effect=cls.simulate_error(mutagen_tags.ID3NoHeaderError))

    @classmethod
    def read_mp3_with_header_not_found_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.MP3_CONSTRUCTOR, side_effect=cls.simulate_error(mutagen_mp3.HeaderNotFoundError))

    @classmethod
    def read_mp3_with_unknown_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.MP3_CONSTRUCTOR, side_effect=cls.simulate_error(Exception))

    @classmethod
    def save_mp3_file_success(cls) -> ContextManager[MagicMock]:
        cls.LAST_SAVED_TAGS.clear()
        mp3_mocked = cls._mp3_mock_helper()
        return patch(cls.MP3_CONSTRUCTOR, return_value=mp3_mocked)

    @classmethod
    def normalize_saved_tags(cls) -> TrackMetadata:
        metadata = {}

        for key, frame in cls.LAST_SAVED_TAGS.items():
            if key == 'APIC' and frame.type == 3:
                metadata['APIC'] = frame.data

            elif hasattr(frame, 'text'):
                value = frame.text[0]

                if key == 'TRCK' or key == 'TPOS':
                    if '/' in value:
                        trck_no, total = value.split('/')
                        metadata[key] = int(trck_no), int(total)
                    else:
                        metadata[key] = int(value), 1

                elif key == 'TCMP':
                    metadata[key] = value == "1"

                else:
                    metadata[key] = value

        return TrackMetadata(**metadata)

    @classmethod
    def _create_text_frame(cls, text: str) -> MagicMock:
        text_frame = cls.create_mock(mutagen_tags.Frame)
        text_frame.text = [text]
        return text_frame

    @classmethod
    def _create_image_frame(cls, image: bytes) -> MagicMock:
        image_frame = cls.create_mock(mutagen_tags.Frame)
        image_frame.data = image
        image_frame.type = 3
        return image_frame

    @classmethod
    def _mp3_mock_helper(
            cls,
            method_name: str | None = None,
            return_value: Optional[Any] = None,
            error_name: Type[ExceptionType] | None = None,
            message: str | None = None,
            **kwargs: Any
    ) -> MagicMock:

        tag_storage = {}
        id3_mock = cls.create_mock(mutagen_tags.ID3)

        def add_method_side_effect(frame):
            frame_id = frame.__class__.__name__
            tag_storage[frame_id] = frame
            cls.LAST_SAVED_TAGS[frame_id] = frame

        id3_mock.add.side_effect = add_method_side_effect
        id3_mock.clear.side_effect = tag_storage.clear()
        id3_mock.items.side_effect = lambda: tag_storage.items()
        id3_mock.__iter__.side_effect = lambda: iter(tag_storage.items())
        id3_mock.__len__.side_effect = lambda: len(tag_storage)

        for key, value in cls.MOCK_TAG_VALUES.items():
            if key == 'APIC':
                tag_storage[key] = cls._create_image_frame(value)
            else:
                tag_storage[key] = cls._create_text_frame(value)

        mp3_music_mock = cls.create_mock(mutagen_mp3.MP3)
        mp3_music_mock.tags = id3_mock

        def add_tags_side_effect():
            mp3_music_mock.tags = id3_mock

        mp3_music_mock.tags.side_effect = add_tags_side_effect

        if method_name:
            method_name = getattr(mp3_music_mock, method_name)

            if error_name:
                method_name.side_effect = cls.simulate_error(error_name, message, **kwargs)

            else:
                method_name.return_value = return_value

        return mp3_music_mock
