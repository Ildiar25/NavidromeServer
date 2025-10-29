# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path
from unidecode import unidecode

from ..file_service import FolderManager
from ...utils.exceptions import PathNotFoundError

_logger = logging.getLogger(__name__)


class FileServiceAdapter:


    def __init__(self, str_root_dir: str = "/music", str_file_extension: str = "mp3") -> None:
        self.root_dir = Path(str_root_dir)
        self.folder_manager = FolderManager(self.root_dir, str_file_extension)

    def save_file(self, str_file_path: str, data: bytes) -> None:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot save the file. The path is not valid: {str_file_path}")
            raise PathNotFoundError("File path does not exist. Must be set before saving.")

        file_path = Path(str_file_path)

        self.folder_manager.create_folders(file_path).save_file(file_path, data)

    def read_file(self, str_file_path) -> bytes:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot read the file. The path is not valid: {str_file_path}")
            raise PathNotFoundError("File path does not exist. Must be set before reading.")

        file_path = Path(str_file_path)

        return self.folder_manager.read_file(file_path)

    def update_file_path(self, old_str_path: str, new_str_path: str) -> None:
        if not isinstance(old_str_path, str) or not isinstance(new_str_path, str):
            _logger.error(f"Cannot move the file. One of the paths is not valid: {old_str_path} & {new_str_path}")
            raise PathNotFoundError("File path does not exist. Must be set before saving.")

        old_path = Path(old_str_path)
        new_path = Path(new_str_path)

        if not old_path.exists() and new_path.exists():
            raise PathNotFoundError(f"Both paths must be valid: '{old_path}' & '{new_path}'.")

        self.folder_manager.update_file_path(old_path, new_path)

    def delete_file(self, str_file_path) -> None:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot delete the file. The path is not valid: {str_file_path}")
            raise PathNotFoundError("File path does not exist. Must be set before deleting.")

        file_path = Path(str_file_path)

        if not file_path.is_file():
            raise PathNotFoundError(f"File not found or it is not a file: '{file_path}'.")

        self.folder_manager.delete_file(file_path)

    def set_new_path(self, artist: str, album: str, track: str, title: str) -> str:
        new_artist = self.__clean_path_name(artist)
        new_album = self.__clean_path_name(album)
        new_track = self.__clean_path_name(track).zfill(2)
        new_title = self.__clean_path_name(title)

        return self.folder_manager.set_path(new_artist, new_album, new_track, new_title).as_posix()

    def is_valid_path(self, path: str) -> bool:
        artist = r'\w+'
        album = r'\w+'
        track_no = r'[0-9]{2}'
        title = r'\w+'
        extension = r'[a-zA-Z0-9]{3,4}'

        pattern = fr'{re.escape(self.root_dir.as_posix())}\/{artist}\/{album}\/{track_no}_{title}\.{extension}'

        return bool(re.fullmatch(pattern, path))

    @staticmethod
    def __clean_path_name(name: str) -> str:
        name = unidecode(name).lower()
        name = re.sub(pattern=r'[^a-z0-9]', repl='_', string=name)
        return re.sub(pattern=r'_+', repl='_', string=name).strip('_')
