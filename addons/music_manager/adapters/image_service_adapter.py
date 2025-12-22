import io
import logging
from pathlib import Path

# noinspection PyPackageRequirements
import magic
from PIL import Image, UnidentifiedImageError

from ..services.image_service import ImageProcessor, ImageToPNG
from ..utils.data_encoding import base64_decode, base64_encode
from ..utils.enums import ImageType
from ..utils.exceptions import ImageServiceError, InvalidImageFormatError, InvalidPathError, MusicManagerError


_logger = logging.getLogger(__name__)


class ImageServiceAdapter:

    IMAGE_FORMATS = {
        ImageType.PNG: ImageToPNG,
    }

    def __init__(self, str_bytes_image: str, image_type: str, square_size: str) -> None:
        self.raw_image = str_bytes_image
        self.image_type = self._check_image_format(image_type)
        self.square_size = self._check_image_size(square_size)
        self.mime_type = None

        self._pil_image = None
        self._processor = None

    def save_to_bytes(self) -> str:
        processor = self._get_processor()
        image_to_encode = processor.center_image().with_size(self.square_size, self.square_size).to_bytes()
        return base64_encode(image_to_encode)

    def save_to_file(self, str_file_path: str) -> None:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot save the file. The path is not valid: '{str_file_path}'.")
            raise InvalidPathError("File path does not exist. A valid path must be set before saving.")

        output_path = Path(str_file_path).with_suffix(f'.{self.image_type.value}')

        processor = self._get_processor()
        processor.center_image().with_size(self.square_size, self.square_size).to_file(output_path)

    def _get_pil_image(self) -> Image.Image:
        if not self._pil_image:
            decoded_image = base64_decode(self.raw_image)
            self.mime_type = magic.from_buffer(decoded_image, mime=True)

            if not self.mime_type.startswith('image/'):
                self.mime_type = None
                raise InvalidImageFormatError(f"Invalid MIME type: '{self.mime_type}'.")

            self._pil_image = self._load_pil_image(io.BytesIO(decoded_image))

        return self._pil_image

    def _get_processor(self) -> ImageProcessor:
        if not self._processor:
            self._processor = self._select_image_processor(self._get_pil_image())

        return self._processor

    def _select_image_processor(self, image: Image.Image) -> ImageProcessor:
        image_processor = self.IMAGE_FORMATS.get(self.image_type, None)

        if not image_processor:
            raise ImageServiceError("Unsupported image processor type")

        return image_processor(image)

    @staticmethod
    def _check_image_format(image_type: str) -> ImageType | None:
        if image_type not in (extension.value for extension in ImageType):
            _logger.error(f"Cannot find the image extension: '{image_type}'.")
            raise InvalidImageFormatError(f"The file extension '{image_type}' is not valid.")

        return ImageType(image_type)

    @staticmethod
    def _check_image_size(size: str) -> int:
        if not isinstance(size, str):
            raise InvalidImageFormatError(f"The image size '{size}' is not valid.")

        try:
            size = int(size)
            return size

        except ValueError as caught_error:
            _logger.error(f"The image size is not a valid size: {caught_error}")
            raise InvalidImageFormatError(f"The image size is not a valid size: {caught_error}")

    @staticmethod
    def _load_pil_image(image_stream: io.BytesIO) -> Image.Image:
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
