# -*- coding: utf-8 -*-
from typing import Any, Dict, Final, Iterable, Self

from ...utils.custom_types import CustomWarningMessage


class ProcessImageMixin:
    """
    Helps to process any image used by inherited models.
    Manages basic image data like cover or artist picture and validates file format.
    """

    _name: Final[str]
    _description: str | None


    def _validate_picture_image(self: Iterable[Self]) -> CustomWarningMessage | None:
        """Checks picture image format. If image format does not in allowed formats, clears the field `picture`
        and returns a warning message.
        :return: Warning Message (dict) | None
        """

    @staticmethod
    def _process_picture_image(values: Dict[str, Any]) -> None:
        """Ensure value 'picture' is in given dictionary. Then process the image with default values (400x400)
        and assign the result to the given dictionary.
        :param values: Dictionary with vals to write
        :return: None
        """
