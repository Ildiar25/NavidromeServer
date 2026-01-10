# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from typing import List

from ..services.file_service import FolderManager
from ..utils.file_utils import clean_path_section, is_valid_path
from ..utils.enums import FileType
from ..utils.exceptions import InvalidFileFormatError, InvalidPathError


_logger = logging.getLogger(__name__)


class FileServiceAdapter:

    def __init__(self, str_root_dir: str, file_extension: str) -> None:
        self.root_dir = self._check_root_dir(str_root_dir)
        self.file_extension = self._check_file_extension(file_extension)
        self._folder_manager = FolderManager(self.root_dir, self.file_extension)

    def save_file(self, str_file_path: str, data: bytes) -> None:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot save the file. The path is not valid: '{str_file_path}'.")
            raise InvalidPathError("File path does not exist. Must be set before saving.")

        if not isinstance(data, bytes):
            _logger.error(f"Cannot save the file. The data is not valid: '{type(data).__name__}'.")
            raise InvalidPathError("Data to save is not valid. Must be 'bytes' instead.")

        file_path = Path(str_file_path)

        self._folder_manager.create_folders(file_path).save_file(file_path, data)

    def read_file(self, str_file_path: str | None) -> bytes:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot read the file. The path is not valid: '{str_file_path}'.")
            raise InvalidPathError("File path does not exist. Must be set before reading.")

        file_path = Path(str_file_path)

        if not file_path.is_file():
            _logger.error(f"Cannot read the file. File not found or it is not a file: '{file_path}'.")
            raise InvalidPathError(f"Unavailable to read the file: not found or it is not a file. Try another one.")

        return self._folder_manager.read_file(file_path)

    def update_file_path(self, old_str_path: str | None, new_str_path: str | None) -> None:
        if not isinstance(old_str_path, str) or not isinstance(new_str_path, str):
            _logger.error(f"Cannot move the file. One of the paths is not valid: '{old_str_path}' & '{new_str_path}'.")
            raise InvalidPathError("File path does not exist. Must be set before saving.")

        old_path = Path(old_str_path)
        new_path = Path(new_str_path)

        if old_path == new_path:
            _logger.warning(f"Both paths are equals: '{old_path}' & '{new_path}'.")
            return

        if not old_path.exists():
            _logger.error(f"Old path does not exist: '{old_path}'.")
            raise InvalidPathError("Old path does not exist. Must be set before moving.")

        if new_path.exists():
            _logger.error(f"New path already exists: '{new_path}'.")
            raise InvalidPathError("New path already exists. Must be an empty path.")

        self._folder_manager.update_file_path(old_path, new_path)

    def delete_file(self, str_file_path: str | None) -> None:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot delete the file. The path is not valid: '{str_file_path}'.")
            raise InvalidPathError("File path does not exist. Must be set before deleting.")

        file_path = Path(str_file_path)

        if not file_path.is_file():
            _logger.error(f"Cannot delete the file. File not found or it is not a file: '{file_path}'.")
            raise InvalidPathError(f"Unavailable to delete the file: not found or it is not a file. Try another one.")

        self._folder_manager.delete_file(file_path)

    def get_all_file_paths(self) -> List[Path]:
        return self._folder_manager.get_all_file_paths()

    def set_new_extension(self, new_extension: str) -> None:
        self.file_extension = self._check_file_extension(new_extension)
        self._folder_manager = FolderManager(self.root_dir, self.file_extension)

    def set_new_path(self, artist: str, album: str, track: str, title: str) -> str:
        cln_artist = clean_path_section(artist)
        cln_album = clean_path_section(album)
        cln_track = clean_path_section(track).zfill(2)
        cln_title = clean_path_section(title)

        return str(self._folder_manager.set_path(cln_artist, cln_album, cln_track, cln_title))

    def set_new_root_dir(self, new_root_dir: str) -> None:
        self.root_dir = self._check_root_dir(new_root_dir)
        self._folder_manager = FolderManager(self.root_dir, self.file_extension)

    def is_valid(self, path: str) -> bool:
        return is_valid_path(path, str(self.root_dir))

    @staticmethod
    def _check_file_extension(extension: str) -> FileType | None:
        if extension not in (file.value for file in FileType):
            _logger.error(f"Cannot find the file extension: '{extension}'.")
            raise InvalidFileFormatError(f"The file extension '{extension}' is not valid.")

        return FileType(extension)

    @staticmethod
    def _check_root_dir(root_dir: str) -> Path | None:
        if not isinstance(root_dir, str):
            _logger.error(f"Root dir is not a valid path: '{root_dir}'.")
            raise InvalidPathError(f"Root dir is not a valid path: '{root_dir}'.")

        root_dir = Path(root_dir)

        if not root_dir.is_dir():
            _logger.error(f"Root dir is not a valid directory: '{root_dir}'.")
            raise InvalidPathError(f"Root dir must exist as a valid directory: '{root_dir}'.")

        return root_dir
