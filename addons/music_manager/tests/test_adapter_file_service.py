from pathlib import Path
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from .mocks.base_mock_helper import BaseMock
from ..adapters.file_service_adapter import FileServiceAdapter
from ..services.file_service import FolderManager
from ..utils.exceptions import PathNotFoundError


ROOT_DIR = "/music"
EXTENSION = "mp3"


class TestAdapterFileService(TransactionCase):

    def setUp(self) -> None:
        self.adapter = FileServiceAdapter(str_root_dir=ROOT_DIR, str_file_extension=EXTENSION)

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_with_default_str_root_dir_value(self) -> None:
        self.assertIsInstance(self.adapter.root_dir, Path, f"Root dir value must be a 'Path' instance.")
        self.assertEqual(ROOT_DIR, self.adapter.root_dir.as_posix(), f"Root dir default value must be '{ROOT_DIR}'.")

    def test_init_with_default_str_file_extension_value(self) -> None:
        self.assertIsInstance(
            self.adapter.folder_manager.file_extension, str, f"File extension value must be a 'str' instance."
        )
        self.assertEqual(
            EXTENSION, self.adapter.folder_manager.file_extension, f"File extension default value must be '{EXTENSION}'."
        )

    def test_init_with_other_str_root_dir_value(self) -> None:
        new_adapter = FileServiceAdapter(str_root_dir="/mogambo", str_file_extension="flac")

        self.assertIsInstance(new_adapter.root_dir, Path, f"Root dir value must be a 'Path' instance.")
        self.assertNotEqual(
            ROOT_DIR, new_adapter.root_dir.as_posix(), f"Root dir default value must be different to '{ROOT_DIR}'."
        )

    def test_init_with_other_str_file_extension_value(self) -> None:
        new_adapter = FileServiceAdapter(str_root_dir="/mogambo", str_file_extension="flac")

        self.assertIsInstance(
            new_adapter.folder_manager.file_extension, str, f"File extension value must be a 'str' instance."
        )
        self.assertNotEqual(
            EXTENSION, new_adapter.folder_manager.file_extension,
            f"File extension default value must be different to '{EXTENSION}'."
        )

    # =========================================================================================
    # Testing for 'save_file'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_save_file_success(self, fake_folder_manager: MagicMock) -> None:
        pass

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_save_file_with_path_not_found_error(self, fake_folder_manager: MagicMock) -> None:
        pass

    # =========================================================================================
    # Testing for 'read_file'
    # =========================================================================================

    # =========================================================================================
    # Testing for 'update_file_path'
    # =========================================================================================

    # =========================================================================================
    # Testing for 'delete_path'
    # =========================================================================================

    # =========================================================================================
    # Testing for 'set_new_path'
    # =========================================================================================

    # =========================================================================================
    # Testing for 'is_valid_path'
    # =========================================================================================

    def test_is_valid_path_success(self) -> None:
        pattern = r'^\/music\/\w+\/\w+\/[0-9]{2}_\w+\.[a-zA-Z0-9]{3,4}$'

        artist = "Test Band"
        album = "Epic Album Vol.II (Mega Mix Edition)"
        track = "18"
        title = "The lowest song (ft. Someone Important)"

        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertTrue(self.adapter.is_valid_path(result_path), f"Path must have next pattern: {pattern}")

    def test_is_valid_path_fail_with_track_number(self) -> None:
        pattern = r'^\/music\/\w+\/\w+\/[0-9]{2}_\w+\.[a-zA-Z0-9]{3,4}$'

        artist = "Test Band"
        album = "Epic Album Vol.II (Mega Mix Edition)"
        track = "253"
        title = "The lowest song (ft. Someone Important)"

        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertFalse(self.adapter.is_valid_path(result_path), f"Path must have next pattern: {pattern}")

    def test_is_valid_path_fail_with_extension(self) -> None:
        pattern = r'^\/music\/\w+\/\w+\/[0-9]{2}_\w+\.[a-zA-Z0-9]{3,4}$'

        artist = "Test Band"
        album = "Epic Album Vol.II (Mega Mix Edition)"
        track = "3"
        title = "The lowest song (ft. Someone Important)"

        manager_with_bad_extension = FileServiceAdapter(str_file_extension="mogambo")
        result_path = manager_with_bad_extension.set_new_path(artist, album, track, title)

        self.assertFalse(
            manager_with_bad_extension.is_valid_path(result_path), f"Path must have next pattern: {pattern}"
        )

    # =========================================================================================
    # Testing for '__clean_path_name'
    # =========================================================================================

    def test_clean_artist_name(self) -> None:
        artist = "Пустота"
        album = "B"
        track = "1"
        title = "C"

        expected_path = f"{ROOT_DIR}/pustota/b/01_c.{EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_clean_album_name(self) -> None:
        artist = "A"
        album = "<|º_º|>"
        track = "1"
        title = "C"

        expected_path = f"{ROOT_DIR}/a/o_o/01_c.{EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_clean_one_number_track(self) -> None:
        artist = "A"
        album = "B"
        track = "5"
        title = "C"

        expected_path = f"{ROOT_DIR}/a/b/05_c.{EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_clean_two_number_track(self) -> None:
        artist = "A"
        album = "B"
        track = "25"
        title = "C"

        expected_path = f"{ROOT_DIR}/a/b/25_c.{EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_clean_title_name(self) -> None:
        artist = "A"
        album = "B"
        track = "5"
        title = "Páth! Súb/tle?"

        expected_path = f"{ROOT_DIR}/a/b/05_path_sub_tle.{EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")
