# -*- coding: utf-8 -*-
import logging
from pathlib import Path


_logger = logging.getLogger(__name__)


class FileManager:

    def __init__(self, path: str) -> None:
        self.__path = Path(path)

    def load_file(self) -> bytes:
        return self.__path.read_bytes()

    def create_folders(self) -> 'FileManager':
        if not self.__path.parent.exists():
            self.__path.parent.mkdir(parents=True, exist_ok=True)

        return self

    def update_path(self, old_path: str) -> None:
        old_path = Path(old_path)
        old_path.replace(self.__path)

    def save(self, data: bytes) -> None:
        try:
            self.__path.write_bytes(data)

        except PermissionError as no_permission:
            _logger.error(f"Do not have permissions to write file: {no_permission}")

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while saving the file: {unknown_error}")
