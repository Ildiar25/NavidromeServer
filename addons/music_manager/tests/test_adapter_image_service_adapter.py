import io
import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image
from odoo.tests.common import TransactionCase

from ..adapters.image_service_adapter import ImageServiceAdapter
from ..services.image_service import ImageToPNG
from ..utils.enums import ImageType
from ..utils.exceptions import (
    ImageServiceError,
    InvalidFileFormatError,
    InvalidImageFormatError,
    InvalidPathError,
    MusicManagerError,
)


class TestAdapterImageService(TransactionCase):

    patch_path = 'odoo.addons.music_manager.adapters.image_service_adapter.ImageServiceAdapter.IMAGE_FORMATS'

    def setUp(self) -> None:
        self.png_img = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
        self.corrupt_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAC0lEQVR42mP8/x8AAwMCAO+ip1s=="
        self.pdf_mime = "JVBERi0xLjAKJWVPZgo="

        self.fake_path = "/test/fake/directory"
        self.decoded_image = Image.open(io.BytesIO(base64.b64decode(self.png_img)))

        self.adapter = ImageServiceAdapter(str_bytes_image=self.png_img)

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_raw_image_instance(self) -> None:
        self.assertIsNotNone(self.adapter.raw_image, msg="Raw image is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.adapter.raw_image,
            str,
            msg=f"Raw image must be a 'str' instance, got '{type(self.adapter.raw_image)}' instead."
        )

    def test_init_image_type_instance(self) -> None:
        self.assertIsNotNone(self.adapter.image_type, msg="Image type is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.adapter.image_type,
            ImageType,
            msg=f"Image type must be 'ImageType' instance, got {type(self.adapter.image_type)} instead."
        )

    def test_init_mime_type_instance(self) -> None:
        self.assertIsNone(self.adapter.mime_type, msg="Mime type must be empty before instantiate the adapter.")

    def test_init_pil_image_instance(self) -> None:
        self.assertIsNone(self.adapter._pil_image, msg="Pil image must be None when instantiate the adapter.")

    def test_init_procesor_instance(self) -> None:
        self.assertIsNone(self.adapter._processor, msg="Processor must be None when instantiate the adapter.")

    def test_init_with_invalid_format_error(self) -> None:
        new_adapter = None

        with self.assertRaises(InvalidImageFormatError) as caught_error:
            new_adapter = ImageServiceAdapter(str_bytes_image=self.png_img, image_type='gif')

        self.assertIsInstance(caught_error.exception, InvalidImageFormatError)
        self.assertIsNone(new_adapter, msg="New adapter should be None. Adapter not initialized.")

    # =========================================================================================
    # Testing for 'save_to_file'
    # =========================================================================================

    @patch.dict(patch_path,{ImageType.PNG: MagicMock(spec=ImageToPNG)})
    def test_save_to_file_success(self) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)
        image_processor_mock.center_image.return_value = image_processor_mock
        image_processor_mock.with_size.return_value = image_processor_mock

        ImageServiceAdapter.IMAGE_FORMATS[ImageType.PNG].return_value = image_processor_mock

        self.adapter.save_to_file(width=200, height=200, str_file_path=self.fake_path)

        ImageServiceAdapter.IMAGE_FORMATS[ImageType.PNG].assert_called_once_with(self.decoded_image)
        image_processor_mock.center_image.return_value.with_size.assert_called_with(200, 200)
        image_processor_mock.center_image.return_value.with_size.return_value.to_file.assert_called_once_with(
            Path(self.fake_path).with_suffix('.png')
        )

    @patch.dict(patch_path, {ImageType.PNG: MagicMock(spec=ImageToPNG)})
    def test_save_to_file_with_invalid_path_error(self) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)

        ImageServiceAdapter.IMAGE_FORMATS[ImageType.PNG].return_value = image_processor_mock

        with self.assertRaises(InvalidPathError) as caught_error:
            self.adapter.save_to_file(width=200, height=200, str_file_path=123456789)

        image_processor_mock.assert_not_called()
        self.assertIsInstance(caught_error.exception, InvalidPathError)

    @patch.dict(patch_path, {ImageType.PNG: MagicMock(spec=ImageToPNG)})
    def test_save_to_file_with_invalid_file_format_error(self) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)

        ImageServiceAdapter.IMAGE_FORMATS[ImageType.PNG].return_value = image_processor_mock

        new_adapter = ImageServiceAdapter(str_bytes_image=self.corrupt_image)

        with self.assertRaises(MusicManagerError) as caught_error:
            new_adapter.save_to_file(200, 200, self.fake_path)

        image_processor_mock.center_image.return_value.with_size.assert_not_called()
        image_processor_mock.center_image.return_value.with_size.return_value.to_file.assert_not_called()
        self.assertIsInstance(caught_error.exception, MusicManagerError)

    @patch.dict(patch_path, {ImageType.PNG: None})
    def test_save_to_file_with_no_processor(self) -> None:
        new_adapter = ImageServiceAdapter(str_bytes_image=self.png_img)

        with self.assertRaises(ImageServiceError) as caught_error:
            new_adapter.save_to_file(200, 200, self.fake_path)

        self.assertIsInstance(caught_error.exception, ImageServiceError)
        self.assertIsNone(new_adapter._processor, msg="Processor must be None when there is not selected processor.")

    @patch.dict(patch_path, {ImageType.PNG: MagicMock(spec=ImageToPNG)})
    def test_save_to_file_with_mime_type_error(self) -> None:
        new_adapter = ImageServiceAdapter(str_bytes_image=self.pdf_mime)

        with self.assertRaises(InvalidImageFormatError) as caught_error:
            new_adapter.save_to_file(200, 200, self.fake_path)

        self.assertIsInstance(caught_error.exception, InvalidImageFormatError)
        self.assertIsNone(new_adapter.mime_type, msg="MIME type must be None when '_get_pil_image' method fails.")

    # =========================================================================================
    # Testing for 'save_to_buffer'
    # =========================================================================================

    @patch.dict(patch_path, {ImageType.PNG: MagicMock(spec=ImageToPNG)})
    def test_save_to_buffer_success(self) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)
        image_processor_mock.center_image.return_value = image_processor_mock
        image_processor_mock.with_size.return_value = image_processor_mock
        image_processor_mock.to_bytes.return_value = io.BytesIO(base64.b64decode(self.png_img)).read()

        ImageServiceAdapter.IMAGE_FORMATS[ImageType.PNG].return_value = image_processor_mock

        result = self.adapter.save_to_bytes(200, 200)

        ImageServiceAdapter.IMAGE_FORMATS[ImageType.PNG].assert_called_once_with(self.decoded_image)
        image_processor_mock.center_image.return_value.with_size.assert_called_with(200, 200)
        self.assertEqual(self.png_img, result)

    @patch.dict(patch_path, {ImageType.PNG: MagicMock(spec=ImageToPNG)})
    def test_save_to_buffer_with_invalid_file_format_error(self) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)

        ImageServiceAdapter.IMAGE_FORMATS[ImageType.PNG].return_value = image_processor_mock

        new_adapter = ImageServiceAdapter(str_bytes_image=self.corrupt_image)

        with self.assertRaises(MusicManagerError) as caught_error:
            new_adapter.save_to_bytes(200, 200)

        image_processor_mock.center_image.return_value.with_size.assert_not_called()
        image_processor_mock.center_image.return_value.with_size.return_value.to_bytes.assert_not_called()
        self.assertIsInstance(caught_error.exception, MusicManagerError)

    @patch.dict(patch_path, {ImageType.PNG: None})
    def test_save_to_buffer_with_no_processor(self) -> None:
        new_adapter = ImageServiceAdapter(str_bytes_image=self.png_img)

        with self.assertRaises(ImageServiceError) as caught_error:
            new_adapter.save_to_bytes(200, 200)

        self.assertIsInstance(caught_error.exception, ImageServiceError)
        self.assertIsNone(new_adapter._processor, msg="Processor must be None when there is not selected processor.")

    @patch.dict(patch_path, {ImageType.PNG: MagicMock(spec=ImageToPNG)})
    def test_save_to_buffer_with_mime_type_error(self) -> None:
        new_adapter = ImageServiceAdapter(str_bytes_image=self.pdf_mime)

        with self.assertRaises(InvalidImageFormatError) as caught_error:
            new_adapter.save_to_bytes(200, 200)

        self.assertIsInstance(caught_error.exception, InvalidImageFormatError)
        self.assertIsNone(new_adapter.mime_type, msg="MIME type must be None when '_get_pil_image' method fails.")
