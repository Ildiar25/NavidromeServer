from pathlib import Path

from odoo.tests.common import TransactionCase

from .mocks.file_mock import FileMock
from ..services.file_service import FolderManager
from ..utils.constants import ROOT_DIR, TRACK_EXTENSION
from ..utils.enums import FileType
from ..utils.exceptions import FilePersistenceError, InvalidPathError, MusicManagerError


class TestFileService(TransactionCase):

    def setUp(self) -> None:
        self.initial_path = Path(f"{ROOT_DIR}/artist/album/01_title.{TRACK_EXTENSION}")
        self.manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_with_initial_root(self) -> None:
        self.assertIsInstance(self.manager.root_dir, str, "Root path must be returned as a 'str' instance.")
        self.assertEqual(self.manager.root_dir, ROOT_DIR, f"Root path must be '{ROOT_DIR}'.")

    def test_init_with_initial_extension(self) -> None:
        self.assertIsInstance(self.manager.file_extension, str, "Extension must be an 'str' instance.")
        self.assertEqual(self.manager.file_extension, TRACK_EXTENSION, f"Extension must be '{TRACK_EXTENSION}'.")

    # =========================================================================================
    # Testing for 'create_folders'
    # =========================================================================================

    def test_create_folders_if_parent_exists(self) -> None:
        pathlib_mock = FileMock.create_mock(Path)
        pathlib_mock.parent.exists.return_value = True

        self.manager.create_folders(pathlib_mock)

        pathlib_mock.parent.mkdir.assert_not_called()

    def test_create_folders_if_parent_not_exists(self) -> None:
        pathlib_mock = FileMock.create_mock(Path)
        pathlib_mock.parent.exists.return_value = False

        self.manager.create_folders(pathlib_mock)

        pathlib_mock.parent.mkdir.assert_called_once()

    # =========================================================================================
    # Testing for 'set_path'
    # =========================================================================================

    def test_set_path_sucess(self) -> None:
        artist = "artist"
        album = "album"
        track = "01"
        title = "title"

        expected_path = f"{ROOT_DIR}/artist/album/01_title.{TRACK_EXTENSION}"
        result_path = self.manager.set_path(artist, album, track, title)

        self.assertIsInstance(result_path, Path, "Path must be a 'Path' instance.")
        self.assertEqual(result_path.as_posix(), expected_path, f"Path must be equal to '{expected_path}'.")

    def test_set_path_fail(self) -> None:
        artist = "artist"
        album = "album"
        track = "01"
        title = "title"

        expected_path = "/root/artist/album/01_title.flac"
        result_path = self.manager.set_path(artist, album, track, title)

        self.assertIsInstance(result_path, Path, "Path must be a 'Path' instance.")
        self.assertNotEqual(
            result_path.as_posix(), expected_path, f"Path must be other extension and root folder: '{expected_path}'."
        )

    # =========================================================================================
    # Testing for '_clean_empty_dirs'
    # =========================================================================================

    def test_clean_empty_dirs_success(self) -> None:
        pathlib_mock = FileMock.create_mock(Path, parent=Path(ROOT_DIR))
        pathlib_mock.iterdir.return_value = []
        pathlib_mock.rmdir.return_value = None

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        fake_manager._clean_empty_dirs(pathlib_mock)

        pathlib_mock.rmdir.assert_called_once_with()

    def test_clean_empty_dirs_fails_if_not_empty(self) -> None:
        pathlib_mock = FileMock.create_mock(Path, parent=Path(ROOT_DIR))
        pathlib_mock.iterdir.return_value = [FileMock.create_mock(Path)]
        pathlib_mock.rmdir.return_value = None

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        fake_manager._clean_empty_dirs(pathlib_mock)

        pathlib_mock.rmdir.assert_not_called()

    def test_clean_empty_dirs_stops_at_root_dir(self) -> None:
        pathlib_mock = FileMock.create_mock(Path, parent=Path(ROOT_DIR))
        pathlib_mock.iterdir.return_value = []
        pathlib_mock.rmdir.return_value = None

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        fake_manager._clean_empty_dirs(Path(ROOT_DIR))

        pathlib_mock.rmdir.assert_not_called()

    def test_clean_empty_dirs_with_permission_error(self):
        pathlib_mock = FileMock.create_mock(Path, parent=Path(ROOT_DIR))
        pathlib_mock.iterdir.return_value = []
        pathlib_mock.rmdir.side_effect = PermissionError("SIMULATING ERROR || PermissionError ||")

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        fake_manager._clean_empty_dirs(pathlib_mock)

        pathlib_mock.rmdir.assert_called_once()

    def test_clean_empty_dirs_with_exception_error(self):
        pathlib_mock = FileMock.create_mock(Path, parent=Path(ROOT_DIR))
        pathlib_mock.iterdir.return_value = []
        pathlib_mock.rmdir.side_effect = Exception("SIMULATING ERROR || Exception ||")

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        fake_manager._clean_empty_dirs(pathlib_mock)

        pathlib_mock.rmdir.assert_called_once()

    # =========================================================================================
    # Testing for 'save_file'
    # =========================================================================================

    def test_save_file_success(self) -> None:
        pathlib_mock = FileMock.write_bytes_file_pathlib_success()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        data_to_save = b"Fake data"

        fake_manager.save_file(file_path=pathlib_mock, data=data_to_save)

        pathlib_mock.write_bytes.assert_called_once_with(data_to_save)

    def test_save_file_with_permission_error(self) -> None:
        pathlib_mock = FileMock.write_bytes_file_pathlib_with_permission_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        data_to_save = b"Fake data"

        with self.assertRaises(FilePersistenceError) as caught_error:
            fake_manager.save_file(file_path=pathlib_mock, data=data_to_save)

        self.assertIn("Permission", str(caught_error.exception))
        pathlib_mock.write_bytes.assert_called_once_with(data_to_save)

    def test_save_file_with_exception_error(self) -> None:
        pathlib_mock = FileMock.write_bytes_file_pathlib_with_exception_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        data_to_save = b"Fake data"

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.save_file(file_path=pathlib_mock, data=data_to_save)

        self.assertIn("Exception", str(caught_error.exception))
        pathlib_mock.write_bytes.assert_called_once_with(data_to_save)

    def test_save_file_with_unknown_error(self) -> None:
        pathlib_mock = FileMock.create_mock(Path)
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        data_to_save = b"Fake data"
        pathlib_mock.write_bytes.side_effect = OSError("SIMULATING ERROR || OSError ||")

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.save_file(file_path=pathlib_mock, data=data_to_save)

        self.assertIn("OSError", str(caught_error.exception))
        pathlib_mock.write_bytes.assert_called_once_with(data_to_save)

    # =========================================================================================
    # Testing for 'read_file'
    # =========================================================================================

    def test_read_file_success(self) -> None:
        pathlib_mock = FileMock.open_bytes_file_pathlib_success()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        expected_data = b"Fake data"

        result_data = fake_manager.read_file(pathlib_mock)

        self.assertEqual(expected_data, result_data, f"Data must be equal: {expected_data} & {result_data}")

    def test_read_file_with_file_not_found_error(self) -> None:
        pathlib_mock = FileMock.open_bytes_file_pathlib_with_file_not_found_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(InvalidPathError) as caught_error:
            fake_manager.read_file(pathlib_mock)

        self.assertIn("FileNotFound", str(caught_error.exception))
        pathlib_mock.read_bytes.assert_called_once()

    def test_read_file_with_permission_error(self) -> None:
        pathlib_mock = FileMock.open_bytes_file_pathlib_with_permission_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(FilePersistenceError) as caught_error:
            fake_manager.read_file(pathlib_mock)

        self.assertIn("PermissionError", str(caught_error.exception))
        pathlib_mock.read_bytes.assert_called_once()

    def test_read_file_with_exception_error(self) -> None:
        pathlib_mock = FileMock.open_bytes_file_pathlib_with_exception_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.read_file(pathlib_mock)

        self.assertIn("Exception", str(caught_error.exception))
        pathlib_mock.read_bytes.assert_called_once()

    def test_read_file_with_unknown_error(self) -> None:
        pathlib_mock = FileMock.create_mock(Path)
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        pathlib_mock.read_bytes.side_effect = OSError("SIMULATING ERROR || OSError ||")

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.read_file(pathlib_mock)

        self.assertIn("OSError", str(caught_error.exception))
        pathlib_mock.read_bytes.assert_called_once()

    # =========================================================================================
    # Testing for 'update_file_path'
    # =========================================================================================

    def test_update_file_success(self) -> None:
        old_path_mock = FileMock.replace_file_pathlib_success()
        new_path_mock = FileMock.create_mock(Path)

        parent_mock = FileMock.create_mock(mock_class=Path, parent=Path(ROOT_DIR))
        parent_mock.iterdir.return_value = []
        parent_mock.rmdir.return_value = None

        old_path_mock.parent = parent_mock
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        fake_manager.update_file_path(old_path_mock, new_path_mock)

        old_path_mock.replace.assert_called_once()
        parent_mock.rmdir.assert_called_once()

    def test_update_file_with_invalid_path_error(self) -> None:
        old_path_mock = FileMock.replace_file_pathlib_with_file_not_found_error()
        new_path_mock = FileMock.create_mock(Path)

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(InvalidPathError) as caught_error:
            fake_manager.update_file_path(old_path_mock, new_path_mock)

        self.assertIn("FileNotFound", str(caught_error.exception))
        old_path_mock.replace.assert_called_once_with(new_path_mock)

    def test_update_file_with_permission_error(self) -> None:
        old_path_mock = FileMock.replace_file_pathlib_with_permission_error()
        new_path_mock = FileMock.create_mock(Path)

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(FilePersistenceError) as caught_error:
            fake_manager.update_file_path(old_path_mock, new_path_mock)

        self.assertIn("PermissionError", str(caught_error.exception))
        old_path_mock.replace.assert_called_once_with(new_path_mock)

    def test_update_file_with_exception_error(self) -> None:
        old_path_mock = FileMock.replace_file_pathlib_with_exception_error()
        new_path_mock = FileMock.create_mock(Path)

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.update_file_path(old_path_mock, new_path_mock)

        self.assertIn("Exception", str(caught_error.exception))
        old_path_mock.replace.assert_called_once_with(new_path_mock)

    def test_update_file_with_unknown_error(self) -> None:
        old_path_mock = FileMock.create_mock(Path)
        new_path_mock = FileMock.create_mock(Path)

        old_path_mock.replace.side_effect = OSError("SIMULATING ERROR || OSError ||")

        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.update_file_path(old_path_mock, new_path_mock)

        self.assertIn("OSError", str(caught_error.exception))
        old_path_mock.replace.assert_called_once_with(new_path_mock)

    # =========================================================================================
    # Testing for 'delete_file'
    # =========================================================================================

    def test_delete_file_with_success(self) -> None:
        pathlib_mock = FileMock.remove_file_pathlib_success()

        parent_mock = FileMock.create_mock(mock_class=Path, parent=Path(ROOT_DIR))
        parent_mock.iterdir.return_value = []
        parent_mock.rmdir.return_value = None

        pathlib_mock.parent = parent_mock
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        fake_manager.delete_file(pathlib_mock)

        pathlib_mock.unlink.assert_called_once()
        parent_mock.rmdir.assert_called_once()

    def test_delete_file_with_file_not_found_error(self) -> None:
        pathlib_mock = FileMock.remove_file_pathlib_with_file_not_found_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(InvalidPathError) as caught_error:
            fake_manager.delete_file(pathlib_mock)

        self.assertIn("FileNotFound", str(caught_error.exception))
        pathlib_mock.unlink.assert_called_once()

    def test_delete_file_with_permission_error(self) -> None:
        pathlib_mock = FileMock.remove_file_pathlib_with_permission_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(FilePersistenceError) as caught_error:
            fake_manager.delete_file(pathlib_mock)

        self.assertIn("PermissionError", str(caught_error.exception))
        pathlib_mock.unlink.assert_called_once()

    def test_delete_file_with_exception_error(self) -> None:
        pathlib_mock = FileMock.remove_file_pathlib_with_exception_error()
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.delete_file(pathlib_mock)

        self.assertIn("Exception", str(caught_error.exception))
        pathlib_mock.unlink.assert_called_once()

    def test_delete_file_with_unknown_error(self) -> None:
        pathlib_mock = FileMock.create_mock(Path)
        fake_manager = FolderManager(root_dir=Path(ROOT_DIR), file_extension=FileType(TRACK_EXTENSION))

        pathlib_mock.unlink.side_effect = OSError("SIMULATING ERROR || OSError ||")

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_manager.delete_file(pathlib_mock)

        self.assertIn("OSError", str(caught_error.exception))
        pathlib_mock.unlink.assert_called_once()
