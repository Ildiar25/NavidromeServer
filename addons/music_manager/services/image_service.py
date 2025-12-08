# -*- coding: utf-8 -*-
import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar

from PIL.Image import Image

from ..utils.enums import ImageType
from ..utils.exceptions import ImagePersistenceError, InvalidImageFormatError, MusicManagerError


_logger = logging.getLogger(__name__)


ImgProcessor = TypeVar("ImgProcessor", bound='ImageProcessor')


# ---- Image service ---- #
class ImageProcessor(ABC):

    def __init__(self, image: Image) -> None:
        self._image = image

    @property
    def image(self) -> Image:
        return self._image

    @property
    def size(self) -> tuple[int, int]:
        return self._image.size

    def center_image(self) -> ImgProcessor:
        width, height = self._image.size
        min_dimension = min(width, height)

        left = (width - min_dimension) / 2
        top = (height - min_dimension) / 2
        right = (width + min_dimension) / 2
        bottom = (height + min_dimension) / 2

        self._image = self._image.crop(box=(left, top, right, bottom))
        return self

    def with_size(self, width: int, height: int) -> ImgProcessor:
        self._image = self._image.resize(size=(width, height))
        return self

    @abstractmethod
    def to_bytes(self) -> bytes:
        ...

    @abstractmethod
    def to_file(self, output_path: Path) -> None:
        ...


class ImageToPNG(ImageProcessor):

    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()

        try:
            self._image.save(buffer, format=ImageType.PNG.value)

        except OSError as coding_error:
            _logger.error(f"There was a problem while coding image: {coding_error}")
            raise InvalidImageFormatError(coding_error)

        buffer.seek(0)
        return buffer.read()

    def to_file(self, output_path: Path) -> None:
        try:
            self._image.save(output_path)

        except (PermissionError, FileExistsError) as not_allowed:
            _logger.error(f"File already exists or is not allowed to write file: {not_allowed}")
            raise ImagePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while saving image: {unknown_error}")
            raise MusicManagerError(unknown_error)
