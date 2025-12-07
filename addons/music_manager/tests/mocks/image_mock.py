from typing import Optional, Any, TypeVar, Type
from unittest.mock import MagicMock

from PIL import Image

from .base_mock_helper import BaseMock


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


class ImageMock(BaseMock):
    """
    Simulates different behaviours when working with images.

    Operations covered:
    -------------------
    - Crop
    - Resize
    - Save

    For each operation, mocks are provided for:
    -------------------------------------------
    - Success case
    - PermissionError
    - FileExistsError
    - Exception
    """

    @classmethod
    def crop_image_success(cls, new_size: tuple[int, int] | None = None) -> MagicMock:
        new_image_size_mock = cls.create_mock(Image.Image)
        new_image_size_mock.size = new_size
        return cls._mock_image_helper('crop', return_value=new_image_size_mock)

    @classmethod
    def resize_image_success(cls, new_size: tuple[int, int] | None = None) -> MagicMock:
        new_image_size_mock = cls.create_mock(Image.Image)
        new_image_size_mock.size = new_size
        return cls._mock_image_helper('resize', return_value=new_image_size_mock)

    @classmethod
    def save_image_success(cls) -> MagicMock:
        return cls._mock_image_helper('save')

    @classmethod
    def save_image_with_os_error(cls) -> MagicMock:
        return cls._mock_image_helper('save', error_name=OSError)

    @classmethod
    def save_image_with_permission_error(cls) -> MagicMock:
        return cls._mock_image_helper('save', error_name=PermissionError)

    @classmethod
    def save_image_with_file_exists_error(cls) -> MagicMock:
        return cls._mock_image_helper('save', error_name=FileExistsError)

    @classmethod
    def save_image_with_exception_error(cls) -> MagicMock:
        return cls._mock_image_helper('save', error_name=Exception)

    @classmethod
    def _mock_image_helper(
            cls,
            method_name: str,
            return_value: Optional[Any] = None,
            error_name: Type[ExceptionType] | None = None,
            message: str | None = None,
            **kwargs
    ) -> MagicMock:

        image_mock = cls.create_mock(Image.Image)
        method_mock = getattr(image_mock, method_name)

        if error_name:
            method_mock.side_effect = cls.simulate_error(error_name, message, **kwargs)

        else:
            method_mock.return_value = return_value

        return image_mock
