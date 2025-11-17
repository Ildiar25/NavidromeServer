from unittest.mock import MagicMock
from typing import Optional, Any, TypeVar, Type

from .base_mock_helper import BaseMock


E = TypeVar("E", bound=BaseException)


class DownloadMock(BaseMock):
    """
    Simulates different behaviours when downloading files.

    Operations covered:
    -------------------


    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    """

    # ------------------------- #
    # PyTube module
    # ------------------------- #



    # ------------------------- #
    # YT-DLP module
    # ------------------------- #

    @classmethod
    def _mock_pytube_helper(
            cls,
            method_name: str,
            return_value: Optional[Any] = None,
            error_name: Type[E] | None = None,
            message: str | None = None
    ) -> MagicMock:
        pass

    @classmethod
    def _mock_ytdpl_helper(
            cls,
            method_name: str,
            return_value: Optional[Any] = None,
            error_name: Type[E] | None = None,
            message: str | None = None
    ) -> MagicMock:
        pass
