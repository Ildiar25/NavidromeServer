# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path
from unidecode import unidecode


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
        if isinstance(self.file_path, Path):
            if not self.file_path.parent.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)

        return self

    def save(self, data: bytes) -> None:
        try:
            if isinstance(self.file_path, Path):
                if not self.file_path:
                    raise ValueError("Path does not exist")

                self.file_path.write_bytes(data)

        except ValueError as no_path:
            _logger.error(f"Cannot save the file: {no_path}")

        except PermissionError as no_permission:
            _logger.error(f"Do not have permissions to write file: {no_permission}")

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while saving the file: {unknown_error}")

    def set_path(self, artist: str, album: str, track: str, title: str) -> str:
        clean_artist = self.__clean_path_name(artist)
        clean_album = self.__clean_path_name(album)
        clean_title = self.__clean_path_name(title)

        if len(track) == 1:
            clean_track = f"0{self.__clean_path_name(track)}"
        else:
            clean_track = self.__clean_path_name(track)

        return str(self.__root_folder / clean_artist / clean_album / f"{clean_track}_{clean_title}.{self.__extension}")

    def update_file_path(self, path: str) -> 'FolderManager':
        old_path = Path(path)
        old_path.replace(self.file_path)
        self._clean_empty_dirs(old_path.parent)
        return self

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
    def __clean_path_name(name: str) -> str:
        name = unidecode(name).lower()
        name = re.sub(pattern=r'[^a-z0-9]', repl='_', string=name)
        return re.sub(pattern=r'_+', repl='_', string=name).strip('_')
