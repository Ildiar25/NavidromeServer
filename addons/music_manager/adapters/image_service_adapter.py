import base64
import io
import logging

# noinspection PyPackageRequirements
import magic
from PIL import Image, UnidentifiedImageError

from ..services.image_service import ImageToPNG
from ..utils.exceptions import InvalidImageFormatError, MusicManagerError


_logger = logging.getLogger(__name__)


class ImageServiceAdapter:

    def __init__(self, str_bytes_image: str) -> None:
        decoded_image = self.decode_data(str_bytes_image)
        image_stream = io.BytesIO(decoded_image)
        pil_image = self.__load_image(image_stream)

        self.mime_type = magic.from_buffer(decoded_image, mime=True)
        self._image_processor = ImageToPNG(pil_image)

    def save_to_bytes(self, width: int, height: int) -> str:
        image_to_encode = self._image_processor.center_image().with_size(width, height).to_bytes()
        return self.encode_data(image_to_encode)

    def save_to_file(self, width: int, height: int, path: str) -> None:
        self._image_processor.center_image().with_size(width, height).to_file(path)

    @staticmethod
    def encode_data(bytes_image: bytes) -> str:
        return base64.b64encode(bytes_image).decode()

    @staticmethod
    def decode_data(str_bytes_image: str) -> bytes:
        return base64.b64decode(str_bytes_image)

    @staticmethod
    def __load_image(image_stream: io.BytesIO) -> Image.Image | None:
        try:
            return Image.open(image_stream)

        except UnidentifiedImageError as corrupt_file:
            _logger.error(f"Failed to open image (invalid format or corrupted): {corrupt_file}")
            raise InvalidImageFormatError(corrupt_file)

        except OSError as system_error:
            _logger.error(f"An OS error ocurred while reading image: {system_error}")
            raise MusicManagerError(system_error)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while reading image: {unknown_error}")
            raise MusicManagerError(unknown_error)
