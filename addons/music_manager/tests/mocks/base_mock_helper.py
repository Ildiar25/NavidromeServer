from typing import Any, Type, TypeVar
from unittest.mock import MagicMock


E = TypeVar("E", bound=BaseException)


class BaseMock:

    """
    Provides reusable mock objects and functions for testing different service dependencies.
    """

    @classmethod
    def create_mock(cls, mock_class: Type[Any] | None = None, **kwargs) -> MagicMock:
        mock = MagicMock(spec=mock_class)

        for name, value in kwargs.items():
            setattr(mock, name, value)

        return mock

    @classmethod
    def simulate_error(cls, error_type: Type[E], message: str | None = None) -> E:
        msg = message or f"SIMULATING ERROR || {error_type.__name__} ||"

        return error_type(msg)
