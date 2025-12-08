import io
import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image
from odoo.tests.common import TransactionCase

from ..adapters.image_service_adapter import ImageServiceAdapter
from ..services.image_service import ImageToPNG
from ..utils.enums import ImageType
from ..utils.constants import PNG_ENCODED_IMAGE
from ..utils.exceptions import InvalidPathError


class TestAdapterImageService(TransactionCase):

    def setUp(self) -> None:
        self.fake_path = "/test/fake/directory"
        self.decoded_image = Image.open(io.BytesIO(base64.b64decode(PNG_ENCODED_IMAGE)))

        self.adapter = ImageServiceAdapter(str_bytes_image=PNG_ENCODED_IMAGE)

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

    def test_init_without_pil_image(self) -> None:
        self.assertIsNone(self.adapter._pil_image, msg="Pil image must be None when instantiate the adapter.")

    # =========================================================================================
    # Testing for 'save_to_file'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.image_service_adapter.ImageToPNG')
    def test_save_to_file_success(self, imagetopng_class_mock: MagicMock) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)
        image_processor_mock.center_image.return_value = image_processor_mock

        imagetopng_class_mock.return_value = image_processor_mock

        self.adapter.save_to_file(width=200, height=200, str_file_path=self.fake_path)

        imagetopng_class_mock.assert_called_once_with(self.decoded_image)
        image_processor_mock.center_image.return_value.with_size.assert_called_with(200, 200)
        image_processor_mock.center_image.return_value.with_size.return_value.to_file.assert_called_once_with(
            Path(self.fake_path).with_suffix('.png')
        )

    @patch('odoo.addons.music_manager.adapters.image_service_adapter.ImageToPNG')
    def test_save_to_file_with_invalid_path_error(self, imagetopng_class_mock: MagicMock) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)

        imagetopng_class_mock.return_value = image_processor_mock

        with self.assertRaises(InvalidPathError) as caught_error:
            self.adapter.save_to_file(width=200, height=200, str_file_path=123456789)

        image_processor_mock.assert_not_called()
        self.assertIsInstance(caught_error.exception, InvalidPathError)

    # =========================================================================================
    # Testing for 'save_to_buffer'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.image_service_adapter.ImageToPNG')
    def test_save_to_buffer_success(self, imagetopng_class_mock: MagicMock) -> None:
        image_processor_mock = MagicMock(spec=ImageToPNG)
        image_processor_mock.center_image.return_value.with_size.return_value.to_bytes.return_value = io.BytesIO(
            base64.b64decode(PNG_ENCODED_IMAGE)
        ).read()

        imagetopng_class_mock.return_value = image_processor_mock

        result = self.adapter.save_to_bytes(200, 200)

        imagetopng_class_mock.assert_called_once_with(self.decoded_image)
        image_processor_mock.center_image.return_value.with_size.assert_called_with(200, 200)
        self.assertEqual(PNG_ENCODED_IMAGE, result)
