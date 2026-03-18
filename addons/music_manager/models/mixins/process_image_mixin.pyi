# -*- coding: utf-8 -*-
from typing import Any, Dict, Final, Self

from ...adapters import ImageServiceAdapter
from ...utils.custom_types import CustomWarningMessage


class ProcessImageMixin:
    """
    Helps to process any image used by inherited models.
    Manages basic image data like cover or artist picture and validates file format.
    """

    _name: Final[str]
    _description: str | None

    def _validate_picture_image(self: Self) -> CustomWarningMessage | None:
        """Checks picture image format. If image format does not in allowed formats, clears the field `picture`
        and returns a warning message.
        :return: Warning Message (dict) | None
        """

    def _get_image_service_adapter(self: Self, image: str) -> ImageServiceAdapter:
        """Ensure image service adapter has its settings updated
        :param image: Image bytes in string format
        :return: ImageServiceAdapter with updated settings
        """

    @staticmethod
    def _process_picture_image(values: Dict[str, Any]) -> None:
        """Ensure value 'picture' is in given dictionary. Then process the image with default values (400x400)
        and assign the result to the given dictionary.
        :param values: Dictionary with vals to write
        :return: None
        """
