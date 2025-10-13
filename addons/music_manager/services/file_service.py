# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path
from unidecode import unidecode

from ..utils.exceptions import FilePersistenceError, PathNotFoundError, MusicManagerError


_logger = logging.getLogger(__name__)


class FolderManager:
    def __init__(self, file_path: str | None = None, root_folder: str = '/music', file_extension: str = 'mp3') -> None:
        self.__root_folder = Path(root_folder)
        self.__extension = file_extension

        if file_path:
            self.file_path = Path(file_path)

        else:
            self.file_path = file_path

    def create_folders(self) -> 'FolderManager':
        if isinstance(self.file_path, Path) and not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

        return self

    def save(self, data: bytes) -> None:
        if not self.file_path or not isinstance(self.file_path, Path):
            _logger.error(f"Cannot save the file. The path is not valid: {self.file_path}")
            raise PathNotFoundError("File path does not exist. Must be set before saving.")

        try:
            self.file_path.write_bytes(data)

        except PermissionError as not_allowed:
            _logger.error(f"Is not allowed to write file: {not_allowed}")
            raise FilePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while saving the file: {unknown_error}")
            raise MusicManagerError(unknown_error)

    def set_path(self, artist: str, album: str, track: str, title: str) -> str:
        clean_artist = self.__clean_path_name(artist)
        clean_album = self.__clean_path_name(album)
        clean_title = self.__clean_path_name(title)

        if len(track) == 1:
            clean_track = f"0{self.__clean_path_name(track)}"
        else:
            clean_track = self.__clean_path_name(track)

        return str(self.__root_folder / clean_artist / clean_album / f"{clean_track}_{clean_title}.{self.__extension}")

    def update_file_path(self, path: str) -> None:
        old_path = Path(path)

        if not old_path.exists():
            raise PathNotFoundError(f"Source file not found at: '{path}'.")

        try:
            old_path.replace(self.file_path)

        except PermissionError as not_allowed:
            _logger.error(f"Do not have permissions to delete files: {not_allowed}")
            raise FilePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while deleting file: {unknown_error}")
            raise MusicManagerError(unknown_error)

        self._clean_empty_dirs(old_path.parent)

    def delete_file(self, path: str) -> None:
        file_path = Path(path)

        if not file_path.is_file():
            raise PathNotFoundError(f"File not found or it is not a file: '{path}'.")

        try:
            file_path.unlink()

        except PermissionError as not_allowed:
            _logger.error(f"Do not have permissions to delete files: {not_allowed}")
            raise FilePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while deleting file: {unknown_error}")
            raise MusicManagerError(unknown_error)

        self._clean_empty_dirs(file_path.parent)

    def _clean_empty_dirs(self, path: Path) -> None:
        current_path = path

        if current_path == self.__root_folder:
            return

        try:
            if any(current_path.iterdir()):
                return

            current_path.rmdir()

        except PermissionError as no_permission:
            _logger.error(f"Do not have permissions to delete folders: {no_permission}")
            return

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while deleting folders: {unknown_error}")
            return

        self._clean_empty_dirs(current_path.parent)

    @staticmethod
    def is_valid_path(path: str) -> bool:
        artist = r'\w+'
        album = r'\w+'
        track_no = r'[0-9]{2}'
        title = r'\w+'
        extension = r'[a-zA-Z0-9]{3,4}$'

        pattern = fr'^\/music\/{artist}\/{album}\/{track_no}_{title}\.{extension}'

        return bool(re.match(pattern, path))

    @staticmethod
    def __clean_path_name(name: str) -> str:
        name = unidecode(name).lower()
        name = re.sub(pattern=r'[^a-z0-9]', repl='_', string=name)
        return re.sub(pattern=r'_+', repl='_', string=name).strip('_')
