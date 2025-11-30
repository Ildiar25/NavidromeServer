from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Iterator

from .base_mock_helper import BaseMock


class PathMock(BaseMock):
    """
    Simulates different Path behaviours.

    Operations covered:
    -------------------
    - Unlink

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    - FileNotFoundError
    - PermissionError
    """

    UNLINK_METHOD = 'odoo.addons.music_manager.services.download_service.Path.unlink'

    @classmethod
    @contextmanager
    def success(cls) -> Iterator[None]:
        with patch(cls.UNLINK_METHOD, return_value=None):
            yield


    @classmethod
    @contextmanager
    def with_file_not_found_error(cls) -> Iterator[None]:
        with patch(cls.UNLINK_METHOD, side_effect=FileNotFoundError("SIMULATING ERROR || FileNotFound ||")):
            yield

    @classmethod
    @contextmanager
    def with_permission_error(cls) -> Iterator[None]:
        with patch(cls.UNLINK_METHOD, side_effect=PermissionError("SIMULATING ERROR || PermissionError ||")):
            yield
