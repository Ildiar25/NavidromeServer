# -*- coding: utf-8 -*-
import io
import logging
from abc import ABC, abstractmethod
from typing import Type, TypeVar

from PIL import Image, UnidentifiedImageError

from ..utils.exceptions import ImagePersistenceError, InvalidImageFormatError, MusicManagerError


_logger = logging.getLogger(__name__)


I = TypeVar("I", bound='ImageProcessor')


# ---- Image service ---- #
class ImageProcessor(ABC):

    def __init__(self, image: Image.Image) -> None:
        self._image = image

    def center_image(self) -> I:
        width, height = self._image.size
        min_dimension = min(width, height)

        left = (width - min_dimension) / 2
        top = (height - min_dimension) / 2
        right = (width + min_dimension) / 2
        bottom = (height + min_dimension) / 2

        self._image = self._image.crop(box=(left, top, right, bottom))
        return self

    def with_size(self, width: int, height: int) -> I:
        self._image = self._image.resize(size=(width, height))
        return self

    @abstractmethod
    def to_bytes(self) -> bytes:
        ...

    @abstractmethod
    def to_file(self, output_path) -> None:
        ...


class ImageToPNG(ImageProcessor):

    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        self._image.save(buffer, format='png')
        buffer.seek(0)
        return buffer.read()

    def to_file(self, output_path: str) -> None:
        if not output_path.lower().endswith('.png'):
            raise InvalidImageFormatError(f"Image must have 'PNG' extension.")

        try:
            self._image.save(output_path.lower())

        except (PermissionError, FileExistsError) as not_allowed:
            _logger.error(f"File already exists or is not allowed to write file: {not_allowed}")
            raise ImagePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while saving image: {unknown_error}")
            raise MusicManagerError(unknown_error)
