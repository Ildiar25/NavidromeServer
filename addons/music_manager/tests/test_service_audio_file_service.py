import io
from pathlib import Path
from unittest.mock import patch, ANY, MagicMock
from typing import Dict

from mutagen.id3 import ID3
from odoo.tests.common import TransactionCase

from .mocks.mp3_mock import MP3Mock
from ..services.audio_file_service import MP3AudioFileService
from ..utils.exceptions import InvalidFileFormatError, MusicManagerError, ReadingFileError
from ..utils.track_data import FullTrackData, TrackMetadata


class TestMP3AudioService(TransactionCase):

    def setUp(self) -> None:
        self.mime_type = 'audio/mpeg'
        self.service = MP3AudioFileService()
        self.fake_bytes = io.BytesIO(b'SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IG9mIGJ5dGVzLg==')
        self.fake_path = Path("/fake/directory/file.mp3")

        self.MOCK_TAG_VALUES = {
            'TIT2': "Title",
            'TPE1': "Track artist",
            'TPE2': "Album artist",
            'TOPE': "Original artist",
            'TALB': "Album",
            'TCMP': False,
            'TRCK': (1, 1),
            'TPOS': (1, 1),
            'TDRC': "2025",
            'TCON': "Genre",
            'APIC': b"Cover Image",
        }

    def tearDown(self) -> None:
        self.fake_bytes.close()

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_mime_type_instance(self) -> None:
        self.assertIsNotNone(self.service.MIME_TYPE, msg="MIME type is mandatory before instanctiate the service.")
        self.assertIsInstance(
            self.service.MIME_TYPE,
            str,
            msg=f"MIME type must be a 'str' instance, got {type(self.service.ID3_TAG_MAPPING)} instead."
        )

    def test_init_id3_mapping_instance(self) -> None:
        self.assertIsNotNone(
            self.service.ID3_TAG_MAPPING, msg="Tag mapping is mandatory before instantiate the service."
        )
        self.assertIsInstance(
            self.service.ID3_TAG_MAPPING,
            Dict,
            msg=f"Tag mapping must be a 'dict' instance, got {type(self.service.ID3_TAG_MAPPING)} instead."
        )

    # =========================================================================================
    # Testing for 'get_metadata'
    # =========================================================================================

    def test_get_metadata_success(self) -> None:
        with MP3Mock.read_mp3_file_success() as mock:
            audio_info = self.service.get_full_data(self.fake_bytes)

        mock.assert_called_once_with(ANY, ID3=ID3)

        self.assertIsInstance(
            audio_info,
            FullTrackData,
            msg=f"Return value must be a 'FullTrackData' instance, got '{type(audio_info)}' instead."
        )
        self.assertEqual(self.MOCK_TAG_VALUES, audio_info.metadata.__dict__)

    # FIXME: Este test contiene un mock que lanza un side effect que debería devolver una instancia nueva de mp3.
    # def test_get_metadata_with_id3_no_header_error(self) -> None:
    #     with MP3Mock.read_mp3_with_id3_no_header_error() as mock:
    #         audio_info = self.service.get_full_data(self.fake_bytes)
    #
    #         self.assertIsInstance(
    #             audio_info,
    #             FullTrackData,
    #             msg=f"Return value must be a 'FullTrackData' instance, got '{type(audio_info)}' instead."
    #         )
    #         self.assertDictEqual(audio_info.metadata.__dict__, TrackMetadata.__dict__)
    #
    #     mock.assert_called_once_with(ANY, ID3=ID3)

    def test_get_metadata_with_header_not_found_error(self) -> None:
        with MP3Mock.read_mp3_with_header_not_found_error() as mock:
            audio_info = None

            with self.assertRaises(InvalidFileFormatError) as caught_error:
                audio_info = self.service.get_full_data(self.fake_bytes)

            self.assertIsInstance(caught_error.exception, InvalidFileFormatError)
            self.assertIsNone(audio_info, msg=f"Return value must be 'None', got '{type(audio_info)}' instead.")

        mock.assert_called_once_with(ANY, ID3=ID3)

    def test_get_metadata_with_unknown_error(self) -> None:
        with MP3Mock.read_mp3_with_unknown_error() as mock:
            audio_info = None

            with self.assertRaises(MusicManagerError) as caught_error:
                audio_info = self.service.get_full_data(self.fake_bytes)

            self.assertIsInstance(caught_error.exception, MusicManagerError)
            self.assertIsNone(audio_info, msg=f"Return value must be 'None', got '{type(audio_info)}' instead.")

        mock.assert_called_once_with(ANY, ID3=ID3)

    # =========================================================================================
    # Testing for 'set_metadata'
    # =========================================================================================

    # def test_set_metadata_success(self) -> None:
    #     metadata_to_save = {
    #         'TIT2': "New title",
    #         'TPE1': "New track artist",
    #         'TPE2': "New album artist",
    #         'TOPE': "New original artist",
    #         'TALB': "New album",
    #         'TCMP': True,
    #         'TRCK': (3, 5),
    #         'TPOS': (2, 4),
    #         'TDRC': "2019",
    #         'TCON': "New genre",
    #         'APIC': b"New Cover Image",
    #     }
    #
    #     with MP3Mock.save_mp3_file_success() as mock:
    #         self.service.set_metadata(self.fake_path, metadata_to_save)
    #
    #     print(MP3Mock.normalize_saved_tags())
