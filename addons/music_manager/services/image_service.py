# -*- coding: utf-8 -*-
import io
import logging
from abc import ABC, abstractmethod

from PIL import Image, UnidentifiedImageError

from ..utils.exceptions import ImagePersistenceError, InvalidImageFormatError, MusicManagerError


_logger = logging.getLogger(__name__)


# ---- Image service ---- #
class ImageFile(ABC):

    def center_image(self) -> 'ImageFile':
        ...

    def with_size(self, width: int, height: int) -> 'ImageFile':
        ...

    @abstractmethod
    def build(self, output_path: str | None = None) -> bytes | None:
        ...


class ImageToPNG(ImageFile):

    def __init__(self, img: io.BytesIO) -> None:
        self.__img: Image = self.__load_image(img)

    def center_image(self) -> 'ImageFile':

        width, height = self.__img.size
        min_dimension = min(width, height)

        left = (width - min_dimension) / 2
        top = (height - min_dimension) / 2
        right = (width + min_dimension) / 2
        bottom = (height + min_dimension) / 2

        self.__img = self.__img.crop((left, top, right, bottom))

        return self

    def with_size(self, width: int, height: int) -> 'ImageFile':
        self.__img = self.__img.resize((width, height))
        return self

    def build(self, output_path: str | None = None) -> bytes | None:

        if not output_path:
            buffer = io.BytesIO()
            self.__img.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer.read()

        if not output_path.lower().endswith('.png'):
            raise InvalidImageFormatError("Image must have PNG extension")

        try:
            self.__img.save(output_path)
            return None

        except (PermissionError, FileExistsError) as not_allowed:
            _logger.error(f"File already exists or no permission to write file: {not_allowed}")
            raise ImagePersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while saving image: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def __load_image(img: io.BytesIO) -> Image:
        try:
            return Image.open(img)

        except UnidentifiedImageError as corrupt_file:
            _logger.error(f"Failed to open image (invalid format or corrupted): {corrupt_file}")
            raise InvalidImageFormatError(corrupt_file)

        except OSError as system_error:
            _logger.error(f"An OS error ocurred while reading image: {system_error}")
            raise MusicManagerError(system_error)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while reading image: {unknown_error}")
            raise MusicManagerError(unknown_error)
