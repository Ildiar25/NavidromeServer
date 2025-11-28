from pathlib import Path
from typing import Optional, Any, TypeVar, Type
from unittest.mock import MagicMock

from .base_mock_helper import BaseMock


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


class FileMock(BaseMock):
    """
    Simulates different behaviours when working with files.

    Operations covered:
    -------------------
    - Reading files:
        - read_text
        - read_bytes
    - Writing/replacing files:
        - write
        - replace
    - Removing files:
        - unlink
    - Removing directories:
        - rmdir

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    - FileNotFoundError
    - PermissionError
    - (Optional) DirectoryNotEmptyError (OSError) for rmdir
    """

    # ------------------------- #
    # Pathlib module
    # ------------------------- #

    @classmethod
    def open_text_file_pathlib_success(cls, data: str = "Fake data") -> MagicMock:
        return cls._mock_pathlib_helper('read_text', data)

    @classmethod
    def open_text_file_pathlib_with_file_not_found_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('read_text', error_name=FileNotFoundError)

    @classmethod
    def open_text_file_pathlib_with_permission_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('read_text', error_name=PermissionError)

    @classmethod
    def open_bytes_file_pathlib_success(cls, data: bytes = b"Fake data") -> MagicMock:
        return cls._mock_pathlib_helper('read_bytes', data)

    @classmethod
    def open_bytes_file_pathlib_with_file_not_found_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('read_bytes', error_name=FileNotFoundError)

    @classmethod
    def open_bytes_file_pathlib_with_permission_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('read_bytes', error_name=PermissionError)

    @classmethod
    def open_bytes_file_pathlib_with_exception_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('read_bytes', error_name=Exception)

    @classmethod
    def write_bytes_file_pathlib_success(cls) -> MagicMock:
        return cls._mock_pathlib_helper('write_bytes')

    @classmethod
    def write_bytes_file_pathlib_with_permission_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('write_bytes', error_name=PermissionError)

    @classmethod
    def write_bytes_file_pathlib_with_exception_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('write_bytes', error_name=Exception)

    @classmethod
    def replace_file_pathlib_success(cls) -> MagicMock:
        return cls._mock_pathlib_helper('replace', cls.create_mock(Path))

    @classmethod
    def replace_file_pathlib_with_file_not_found_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('replace', error_name=FileNotFoundError)

    @classmethod
    def replace_file_pathlib_with_permission_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('replace', error_name=PermissionError)

    @classmethod
    def replace_file_pathlib_with_exception_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('replace', error_name=Exception)

    @classmethod
    def remove_file_pathlib_success(cls) -> MagicMock:
        return cls._mock_pathlib_helper('unlink')

    @classmethod
    def remove_file_pathlib_with_file_not_found_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('unlink', error_name=FileNotFoundError)

    @classmethod
    def remove_file_pathlib_with_permission_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('unlink', error_name=PermissionError)

    @classmethod
    def remove_file_pathlib_with_exception_error(cls) -> MagicMock:
        return cls._mock_pathlib_helper('unlink', error_name=Exception)

    @classmethod
    def _mock_pathlib_helper(
            cls,
            method_name: str,
            return_value: Optional[Any] = None,
            error_name: Type[ExceptionType] | None = None,
            message: str | None = None
    ) -> MagicMock:

        pathlib_mock_path = cls.create_mock(Path)
        method_mock = getattr(pathlib_mock_path, method_name)

        if error_name:
            method_mock.side_effect = cls.simulate_error(error_name, message)

        else:
            method_mock.return_value = return_value

        return pathlib_mock_path
    