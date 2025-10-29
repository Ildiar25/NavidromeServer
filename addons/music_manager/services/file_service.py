# -*- coding: utf-8 -*-
import logging
from pathlib import Path

from ..utils.exceptions import FilePersistenceError, PathNotFoundError, MusicManagerError


_logger = logging.getLogger(__name__)


class FolderManager:

    def __init__(self, root_dir: Path, file_extension: str) -> None:
        self.__root_dir = root_dir
        self.__file_extension = file_extension

    @property
    def root_dir(self) -> str:
        return self.__root_dir.as_posix()

    @property
    def file_extension(self) -> str:
        return self.__file_extension

    def create_folders(self, file_path: Path) -> 'FolderManager':
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)

        return self

    def set_path(self, artist: str, album: str, track: str, title: str) -> Path:
        return self.__root_dir / artist / album / f"{track}_{title}.{self.__file_extension}"

    def _clean_empty_dirs(self, path: Path) -> None:
        if path == self.__root_dir:
            return

        try:
            if any(path.iterdir()):
                return

            path.rmdir()
            _logger.debug(f"Removed empty directory: {path}")

        except PermissionError as no_permission:
            _logger.error(f"Do not have permissions to delete folders: {no_permission}")
            return

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while deleting folders: {unknown_error}")
            return

        self._clean_empty_dirs(path.parent)

    @staticmethod
    def save_file(file_path: Path, data: bytes) -> None:
        try:
            file_path.write_bytes(data)

        except PermissionError as not_allowed:
            _logger.error(f"Is not allowed to write file: {not_allowed}")
            raise FilePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while saving the file: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def read_file(file_path: Path) -> bytes:
        try:
            return file_path.read_bytes()

        except FileNotFoundError as not_found:
            _logger.error(f"File not found. Impossible to read: {not_found}")
            raise PathNotFoundError(not_found)

        except PermissionError as not_allowed:
            _logger.error(f"Is not allowed to read file: {not_allowed}")
            raise FilePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while reading the file: {unknown_error}")
            raise MusicManagerError(unknown_error)

    def update_file_path(self, old_path: Path, new_path: Path) -> None:
        try:
            self.create_folders(new_path)
            old_path.replace(new_path)
            self._clean_empty_dirs(old_path.parent)

        except FileNotFoundError as not_found:
            _logger.error(f"File not found. Impossible to update: {not_found}")
            raise PathNotFoundError(not_found)

        except PermissionError as not_allowed:
            _logger.error(f"Do not have permissions to move files: {not_allowed}")
            raise FilePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while moving file: {unknown_error}")
            raise MusicManagerError(unknown_error)

    def delete_file(self, file_path: Path) -> None:
        try:
            file_path.unlink()
            self._clean_empty_dirs(file_path.parent)

        except FileNotFoundError as not_found:
            _logger.error(f"File not found. Impossible to delete: {not_found}")
            raise PathNotFoundError(not_found)

        except PermissionError as not_allowed:
            _logger.error(f"Do not have permissions to delete files: {not_allowed}")
            raise FilePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while deleting file: {unknown_error}")
            raise MusicManagerError(unknown_error)
