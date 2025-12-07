from typing import ContextManager
from unittest.mock import MagicMock, patch

from .base_mock_helper import BaseMock


class PathMock(BaseMock):
    """
    Simulates different Path behaviours ONLY in DOWNLOAD SERVICE.

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
    def success(cls) -> ContextManager[MagicMock]:
        return patch(cls.UNLINK_METHOD, return_value=None)

    @classmethod
    def with_file_not_found_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.UNLINK_METHOD, side_effect=cls.simulate_error(FileNotFoundError))

    @classmethod
    def with_permission_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.UNLINK_METHOD, side_effect=cls.simulate_error(PermissionError))

    @classmethod
    def with_unknown_error(cls) -> ContextManager[MagicMock]:
        return patch(cls.UNLINK_METHOD, side_effect=cls.simulate_error(Exception))
