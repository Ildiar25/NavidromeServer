import base64
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

    def __init__(self, str_bytes_image: str, image_type: ImageType = ImageType.PNG) -> None:
        self.raw_image = str_bytes_image

        # TODO: Utilizar un mapeo de servicio para poder cambiar de tipo de imagen.
        self.image_type = image_type
        self._pil_image = None

    def save_to_bytes(self, width: int, height: int) -> str:
        processor = self._get_image_processor(self._get_pil_image())
        image_to_encode = processor.center_image().with_size(width, height).to_bytes()
        return base64_encode(image_to_encode)

    def save_to_file(self, width: int, height: int, str_file_path: str) -> None:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot save the file. The path is not valid: '{str_file_path}'.")
            raise InvalidPathError("File path does not exist. A valid path must be set before saving.")

        output_path = Path(str_file_path).with_suffix(f'.{self.image_type.value}')

        processor = self._get_image_processor(self._get_pil_image())
        processor.center_image().with_size(width, height).to_file(output_path)

    def _get_image_processor(self, image: Image.Image) -> ImageProcessor:

        # NOTE: No utilizar match, utilizar un mapeo para facilitar la búsqueda de servicios a futuro.
        match self.image_type:
            case ImageType.PNG:
                return ImageToPNG(image)

            case _:
                raise ImageServiceError("Unsupported image processor type")

    def _get_pil_image(self) -> Image.Image:
        if not self._pil_image:
            decoded_image = base64_decode(self.raw_image)
            self.mime_type = magic.from_buffer(decoded_image, mime=True)

            if not self.mime_type.startswith('image/'):
                raise InvalidImageFormatError(f"Invalid MIME type: '{self.mime_type}'.")

            self._pil_image = self._load_image(io.BytesIO(decoded_image))

        return self._pil_image

    @staticmethod
    def _load_image(image_stream: io.BytesIO) -> Image.Image | None:
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
