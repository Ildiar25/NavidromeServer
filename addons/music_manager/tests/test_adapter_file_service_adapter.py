from pathlib import Path
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from ..adapters.file_service_adapter import FileServiceAdapter, FolderManager
from ..utils.constants import ROOT_DIR, TRACK_EXTENSION, PATH_PATTERN
from ..utils.enums import FileType
from ..utils.exceptions import InvalidPathError, InvalidFileFormatError


class TestAdapterFileService(TransactionCase):

    def setUp(self) -> None:
        self.adapter = FileServiceAdapter()

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_root_dir_instance(self) -> None:
        self.assertIsNotNone(self.adapter.root_dir, msg="Root dir is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.adapter.root_dir,
            Path,
            msg=f"Root dir must be a 'Path' instance, got '{type(self.adapter.root_dir)}' instead."
        )

    def test_init_file_extension_instance(self) -> None:
        self.assertIsNotNone(self.adapter.file_extension, msg="Root dir is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.adapter.file_extension,
            FileType,
            msg=f"File extension must be a 'FileType' instance, got '{type(self.adapter.root_dir)}' instead."
        )

    def test_init_adapter_instance(self) -> None:
        self.assertIsNotNone(
            self.adapter._folder_manager, msg="Folder manager is mandatory before instantiate the adapter."
        )
        self.assertIsInstance(
            self.adapter._folder_manager,
            FolderManager,
            msg=f"Folder manager must be 'FolderManager' instance, got {type(self.adapter._folder_manager)} instead."
        )

    def test_init_with_default_str_file_extension_value(self) -> None:
        self.assertIsInstance(
            self.adapter._folder_manager.file_extension,
            str,
            msg=(f"File extension value must be returned as a 'str' instance, "
                 f"got '{type(self.adapter._folder_manager.file_extension)}' instead.")
        )
        self.assertEqual(
            TRACK_EXTENSION,
            self.adapter._folder_manager.file_extension,
            msg=(f"File extension default value must be '{TRACK_EXTENSION}', "
                 f"got {self.adapter._folder_manager.file_extension} instead.")
        )

    def test_init_update_root_dir_success(self) -> None:
        new_adapter = FileServiceAdapter()

        with patch('odoo.addons.music_manager.adapters.file_service_adapter.Path.is_dir', return_value=True):
            new_adapter.set_new_root_dir("/mogambo")

        self.assertEqual(
            new_adapter.root_dir,
            Path("/mogambo"),
            msg=f"New path must be '/mogambo', got '{new_adapter.root_dir}' instead."
        )
        self.assertIsInstance(
            new_adapter.root_dir,
            Path,
            msg=f"Root dir must be a 'Path' instance, got '{type(self.adapter.root_dir)}' instead."
        )

    def test_init_update_root_dir_with_invalid_path_error(self) -> None:
        new_adapter = FileServiceAdapter()

        with self.assertRaises(InvalidPathError) as caught_error:
            new_adapter.set_new_root_dir('/mogambo')

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        self.assertEqual(
            new_adapter.root_dir,
            Path('/music'),
            msg=f"Root dir must be '/music', got '{new_adapter.root_dir}' instead."
        )

    def test_init_update_file_extension_success(self) -> None:
        new_adapter = FileServiceAdapter()

        new_adapter.set_new_extension('flac')

        self.assertEqual(
            new_adapter.file_extension,
            FileType.FLAC,
            msg=f"New extension must be 'flac', got '{new_adapter.file_extension.value}' instead."
        )
        self.assertIsInstance(
            new_adapter.file_extension,
            FileType,
            msg=f"File extension must be a 'FileType' instance, got '{type(self.adapter.root_dir)}' instead."
        )

    def test_init_update_file_extension_with_invalid_file_format_error(self) -> None:
        new_adapter = FileServiceAdapter()

        with self.assertRaises(InvalidFileFormatError) as caught_error:
            new_adapter.set_new_extension('wav')

        self.assertIsInstance(caught_error.exception, InvalidFileFormatError)
        self.assertEqual(
            new_adapter.file_extension,
            FileType.MP3,
            msg=f"File extension must be 'mp3', got '{new_adapter.file_extension.value}' instead."
        )

    # =========================================================================================
    # Testing for 'save_file'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_save_file_success(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = "/testing/fake/dir.mp3"
        fake_data = b"Fake data"

        fake_folder_manager = fake_folder_manager_class.return_value
        fake_save_method = fake_folder_manager.create_folders.return_value

        adapter = FileServiceAdapter()

        adapter.save_file(fake_path, fake_data)

        fake_folder_manager.create_folders.assert_called_once_with(Path(fake_path))
        fake_save_method.save_file.assert_called_once_with(Path(fake_path), fake_data)

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_save_file_without_path(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = None
        fake_data = b"Fake data"

        fake_folder_manager = fake_folder_manager_class.return_value
        fake_save_method = fake_folder_manager.create_folders.return_value

        adapter = FileServiceAdapter()

        with self.assertRaises(InvalidPathError) as caught_error:
            adapter.save_file(fake_path, fake_data)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.create_folders.assert_not_called()
        fake_save_method.save_file.assert_not_called()

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_save_file_with_no_data(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = "/testing/fake/dir.mp3"
        fake_data = None

        fake_folder_manager = fake_folder_manager_class.return_value
        fake_save_method = fake_folder_manager.create_folders.return_value

        adapter = FileServiceAdapter()

        with self.assertRaises(InvalidPathError) as caught_error:
            adapter.save_file(fake_path, fake_data)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.create_folders.assert_not_called()
        fake_save_method.save_file.assert_not_called()

    # =========================================================================================
    # Testing for 'read_file'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_read_file_success(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = "/testing/fake/dir.mp3"
        fake_data = b"Fake data"

        fake_folder_manager = fake_folder_manager_class.return_value
        fake_folder_manager.read_file.return_value = fake_data

        adapter = FileServiceAdapter()

        with patch.object(Path, 'is_file', return_value=True):
            data_read = adapter.read_file(fake_path)

        fake_folder_manager.read_file.assert_called_once_with(Path(fake_path))
        self.assertEqual(data_read, fake_data)

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_read_file_with_invalid_path_error(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = None

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with self.assertRaises(InvalidPathError) as caught_error:
            adapter.read_file(fake_path)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.read_file.assert_not_called()

    # =========================================================================================
    # Testing for 'update_file_path'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_update_file_path_success(self, fake_folder_manager_class: MagicMock) -> None:
        fake_old_path = "/fake/old/path.mp3"
        fake_new_path = "/fake/new/path.mp3"

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with patch.object(Path, 'exists', side_effect=[True, False]):
            adapter.update_file_path(fake_old_path, fake_new_path)

        fake_folder_manager.update_file_path.assert_called_once_with(Path(fake_old_path), Path(fake_new_path))

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_update_file_path_with_old_path_instance_error(self, fake_folder_manager_class: MagicMock) -> None:
        fake_old_path = None
        fake_new_path = "/fake/new/path.mp3"

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with self.assertRaises(InvalidPathError) as caught_error:
            adapter.update_file_path(fake_old_path, fake_new_path)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.update_file_path.assert_not_called()

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_update_file_path_with_new_path_instance_error(self, fake_folder_manager_class: MagicMock) -> None:
        fake_old_path = "/fake/old/path.mp3"
        fake_new_path = None

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with self.assertRaises(InvalidPathError) as caught_error:
            adapter.update_file_path(fake_old_path, fake_new_path)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.update_file_path.assert_not_called()

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_update_file_path_equal_paths(self, fake_folder_manager_class: MagicMock) -> None:
        fake_old_path = "/fake/equal/path.mp3"
        fake_new_path = "/fake/equal/path.mp3"

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()
        adapter.update_file_path(fake_old_path, fake_new_path)

        fake_folder_manager.update_file_path.assert_not_called()

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_update_file_path_old_path_with_invalid_path_error(self, fake_folder_manager_class: MagicMock) -> None:
        fake_old_path = "/fake/old/path.mp3"
        fake_new_path = "/fake/new/path.mp3"

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with patch.object(Path, 'exists', side_effect=[False, False]):
            with self.assertRaises(InvalidPathError) as caught_error:
                adapter.update_file_path(fake_old_path, fake_new_path)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.update_file_path.assert_not_called()

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_update_file_path_new_path_with_invalid_path_error(self, fake_folder_manager_class: MagicMock) -> None:
        fake_old_path = "/fake/old/path.mp3"
        fake_new_path = "/fake/new/path.mp3"

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with patch.object(Path, 'exists', side_effect=[True, True]):
            with self.assertRaises(InvalidPathError) as caught_error:
                adapter.update_file_path(fake_old_path, fake_new_path)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.update_file_path.assert_not_called()

    # =========================================================================================
    # Testing for 'delete_path'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_delete_file_success(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = "/testing/fake/dir.mp3"

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with patch.object(Path, 'is_file', return_value=True):
            adapter.delete_file(fake_path)

        fake_folder_manager.delete_file.assert_called_once_with(Path(fake_path))

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_delete_file_with_instance_error(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = None

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with self.assertRaises(InvalidPathError) as caught_error:
            adapter.delete_file(fake_path)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.delete_file.assert_not_called()

    @patch('odoo.addons.music_manager.adapters.file_service_adapter.FolderManager')
    def test_delete_file_with_is_file_error(self, fake_folder_manager_class: MagicMock) -> None:
        fake_path = "this is not a path or file"

        fake_folder_manager = fake_folder_manager_class.return_value

        adapter = FileServiceAdapter()

        with patch.object(Path, 'is_file', return_value=False):
            with self.assertRaises(InvalidPathError) as caught_error:
                adapter.delete_file(fake_path)

        self.assertIsInstance(caught_error.exception, InvalidPathError)
        fake_folder_manager.delete_file.assert_not_called()

    # =========================================================================================
    # Testing for 'set_new_path'
    # =========================================================================================

    def test_set_new_path_with_normal_characters(self) -> None:
        artist = "Shakira"
        album = "Laundry Service"
        track = "2"
        title = "Underneath Your Clothes"

        expected_path = f"{ROOT_DIR}/shakira/laundry_service/02_underneath_your_clothes.{TRACK_EXTENSION}"

        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(expected_path, result_path, f"Paths must be equals: '{expected_path}' & '{result_path}'.")

    def test_set_new_path_with_special_characters(self) -> None:
        artist = "K(no)w Name ft. Ke$ha"
        album = "A + B"
        track = "1"
        title = "R&B - !!!"

        expected_path = f"{ROOT_DIR}/k_no_w_name_ft_kesha/a_plus_b/01_r_and_b_three_exclamation_marks.{TRACK_EXTENSION}"

        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(expected_path, result_path, f"Paths must be equals: '{expected_path}' & '{result_path}'.")

    def test_set_new_path_clean_artist_name(self) -> None:
        artist = "Пустота"
        album = "B"
        track = "1"
        title = "C"

        expected_path = f"{ROOT_DIR}/pustota/b/01_c.{TRACK_EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_set_new_path_clean_album_name(self) -> None:
        artist = "A"
        album = "<|º_º|>"
        track = "1"
        title = "C"

        expected_path = f"{ROOT_DIR}/a/o_o/01_c.{TRACK_EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_set_new_path_clean_one_number_track(self) -> None:
        artist = "A"
        album = "B"
        track = "5"
        title = "C"

        expected_path = f"{ROOT_DIR}/a/b/05_c.{TRACK_EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_set_new_path_clean_two_number_track(self) -> None:
        artist = "A"
        album = "B"
        track = "25"
        title = "C"

        expected_path = f"{ROOT_DIR}/a/b/25_c.{TRACK_EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    def test_set_new_path_clean_title_name(self) -> None:
        artist = "A"
        album = "B"
        track = "5"
        title = "Páth! Súb/tle?"

        expected_path = f"{ROOT_DIR}/a/b/05_path_sub_tle.{TRACK_EXTENSION}"
        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertEqual(result_path, expected_path, f"Path must be equal to '{expected_path}'.")

    # =========================================================================================
    # Testing for 'is_valid_path'
    # =========================================================================================

    def test_is_valid_path_success(self) -> None:
        artist = "Test Band"
        album = "Epic Album Vol.II (Mega Mix Edition)"
        track = "18"
        title = "The lowest song (ft. Someone Important)"

        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertTrue(self.adapter.is_valid(result_path), f"Path must have next pattern: {PATH_PATTERN}")

    def test_is_valid_path_fail_with_track_number(self) -> None:
        artist = "Test Band"
        album = "Epic Album Vol.II (Mega Mix Edition)"
        track = "253"
        title = "The lowest song (ft. Someone Important)"

        result_path = self.adapter.set_new_path(artist, album, track, title)

        self.assertFalse(self.adapter.is_valid(result_path), f"Path must have next pattern: {PATH_PATTERN}")
