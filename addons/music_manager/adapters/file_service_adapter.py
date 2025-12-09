# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path
from unidecode import unidecode

from ..services.file_service import FolderManager
from ..utils.constants import SYMBOL_MAP
from ..utils.enums import FileType
from ..utils.exceptions import InvalidFileFormatError, InvalidPathError


_logger = logging.getLogger(__name__)


class FileServiceAdapter:

    def __init__(self, str_root_dir: str = "/music", file_extension: str = 'mp3') -> None:
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
            _logger.error(f"File not found or it is not a file: '{file_path}'.")
            raise InvalidPathError(f"File not found or it is not a file. Try another one.")

        self._folder_manager.delete_file(file_path)

    def set_new_path(self, artist: str, album: str, track: str, title: str) -> str:
        new_artist = self.__clean_path_name(artist)
        new_album = self.__clean_path_name(album)
        new_track = self.__clean_path_name(track).zfill(2)
        new_title = self.__clean_path_name(title)

        return self._folder_manager.set_path(new_artist, new_album, new_track, new_title).as_posix()

    def is_valid_path(self, path: str) -> bool:
        artist = r'\w+'
        album = r'\w+'
        track_no = r'[0-9]{2}'
        title = r'\w+'
        extension = r'[a-zA-Z0-9]{3,4}'

        pattern = fr'{re.escape(self.root_dir.as_posix())}\/{artist}\/{album}\/{track_no}_{title}\.{extension}'

        return bool(re.fullmatch(pattern, path))

    def set_new_extension(self, new_extension: str) -> None:
        self.file_extension = self._check_file_extension(new_extension)
        self._folder_manager = FolderManager(self.root_dir, self.file_extension)

    def set_new_root_dir(self, new_root_dir: str) -> None:
        self.root_dir = self._check_root_dir(new_root_dir)
        self._folder_manager = FolderManager(self.root_dir, self.file_extension)

    def __clean_path_name(self, name: str) -> str:
        normalized_name = self.__normalize_characters(name)
        mapped_characters = self.__map_special_characters(normalized_name)
        new_name = re.sub(pattern=r'[^a-z0-9]', repl='_', string=mapped_characters)
        return re.sub(pattern=r'_+', repl='_', string=new_name).strip('_')

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

    @staticmethod
    def __map_special_characters(string: str) -> str:
        pattern = re.compile("|".join(re.escape(symbol_key) for symbol_key in SYMBOL_MAP.keys()))
        return pattern.sub(lambda match_pattern: SYMBOL_MAP[match_pattern.group(0)], string)

    @staticmethod
    def __normalize_characters(string: str) -> str:
        return unidecode(string).lower()
