from unittest.mock import patch, MagicMock

from PIL import Image

from odoo.tests.common import TransactionCase

from .mocks.image_mock import ImageMock
from ..services.image_service import ImageToPNG
from ..utils.exceptions import ImagePersistenceError, InvalidImageFormatError, MusicManagerError


class TestImageService(TransactionCase):

    def setUp(self) -> None:
        self.initial_image = ImageMock.create_mock(Image.Image, size=(400, 200))
        self.image_service = ImageToPNG(self.initial_image)

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_with_initial_image(self) -> None:
        self.assertIsInstance(self.image_service.image, Image.Image, "Initial image must be an 'Image' instance.")
        self.assertEqual(self.image_service.image, self.initial_image, f"Image must be '{self.initial_image}'.")

    def test_init_initial_size(self) -> None:
        initial_size = (400, 200)
        self.assertEqual(self.image_service.size, initial_size, f"Size must be '{initial_size}'.")

    # =========================================================================================
    # Testing for 'center_image'
    # =========================================================================================

    def test_center_image_success(self) -> None:
        original_size = (400, 200)
        expected_size = (200, 200)

        image_mock = ImageMock.crop_image_success(new_size=expected_size)
        image_mock.size = original_size

        fake_image_service = ImageToPNG(image_mock)
        result = fake_image_service.center_image()

        width, height = original_size
        min_dimension = min(width, height)

        expected_box = (
            (width - min_dimension) / 2,
            (height - min_dimension) / 2,
            (width + min_dimension) / 2,
            (height + min_dimension) / 2,
        )

        image_mock.crop.assert_called_once_with(box=expected_box)
        self.assertEqual(image_mock.crop.return_value.size, expected_size, f"New size must be '{expected_size}'.")
        self.assertIs(result, fake_image_service)

    # =========================================================================================
    # Testing for 'with_size'
    # =========================================================================================

    def test_with_size_success(self) -> None:
        original_size = (200, 200)
        expected_size = (400, 400)

        image_mock = ImageMock.resize_image_success(new_size=expected_size)
        image_mock.size = original_size

        fake_image_service = ImageToPNG(image_mock)
        result = fake_image_service.with_size(400, 400)

        image_mock.resize.assert_called_once_with(size=expected_size)
        self.assertEqual(image_mock.resize.return_value.size, expected_size, f"New size must be '{expected_size}'.")
        self.assertIs(result, fake_image_service)

    # =========================================================================================
    # Testing for 'to_bytes'
    # =========================================================================================

    @patch('odoo.addons.music_manager.services.image_service.io.BytesIO')
    def test_save_to_bytes_success(self, fake_bytes_io_class: MagicMock) -> None:
        image_mock = ImageMock.save_image_success()
        fake_bytes_io = fake_bytes_io_class.return_value

        fake_bytes_io.read.return_value = b"Fake data"

        fake_image_service = ImageToPNG(image_mock)
        result_bytes = fake_image_service.to_bytes()

        image_mock.save.assert_called_once_with(fake_bytes_io, format='png')

        fake_bytes_io.seek.assert_called_once_with(0)
        fake_bytes_io.read.assert_called_once()

        self.assertEqual(b"Fake data", result_bytes)

    @patch('odoo.addons.music_manager.services.image_service.io.BytesIO')
    def test_save_to_bytes_with_os_error(self, fake_bytes_io_class: MagicMock) -> None:
        image_mock = ImageMock.save_image_with_os_error()
        fake_bytes_io = fake_bytes_io_class.return_value

        fake_image_service = ImageToPNG(image_mock)

        with self.assertRaises(InvalidImageFormatError) as caught_error:
            fake_image_service.to_bytes()

        self.assertIn("OSError", str(caught_error.exception))
        fake_bytes_io.seek.assert_not_called()
        fake_bytes_io.read.assert_not_called()

    # =========================================================================================
    # Testing for 'to_file'
    # =========================================================================================

    def test_save_to_file_success(self) -> None:
        image_mock = ImageMock.save_image_success()

        fake_path = "/testing/fake/format.png"

        fake_image_service = ImageToPNG(image_mock)
        fake_image_service.to_file(fake_path)

        image_mock.save.assert_called_once_with(fake_path)

    def test_save_to_file_with_invalid_format_image_error(self) -> None:
        image_mock = ImageMock.save_image_success()

        fake_path = "/testing/bad/format.jpg"

        fake_image_service = ImageToPNG(image_mock)

        with self.assertRaises(InvalidImageFormatError) as caught_error:
            fake_image_service.to_file(fake_path)

        self.assertIn("Image must have 'PNG' extension", str(caught_error.exception))
        image_mock.save.assert_not_called()

    def test_save_to_file_with_permission_error(self) -> None:
        image_mock = ImageMock.save_image_with_permission_error()

        fake_path = "/testing/fake/format.png"

        fake_image_service = ImageToPNG(image_mock)

        with self.assertRaises(ImagePersistenceError) as caught_error:
            fake_image_service.to_file(fake_path)

        self.assertIn("PermissionError", str(caught_error.exception))
        image_mock.save.assert_called_once_with(fake_path)

    def test_save_to_file_with_file_exists_error(self) -> None:
        image_mock = ImageMock.save_image_with_file_exists_error()

        fake_path = "/testing/fake/format.png"

        fake_image_service = ImageToPNG(image_mock)

        with self.assertRaises(ImagePersistenceError) as caught_error:
            fake_image_service.to_file(fake_path)

        self.assertIn("FileExistsError", str(caught_error.exception))
        image_mock.save.assert_called_once_with(fake_path)

    def test_save_to_file_with_exception_error(self) -> None:
        image_mock = ImageMock.save_image_with_exception_error()

        fake_path = "/testing/fake/format.png"

        fake_image_service = ImageToPNG(image_mock)

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_image_service.to_file(fake_path)

        self.assertIn("Exception", str(caught_error.exception))
        image_mock.save.assert_called_once_with(fake_path)

    def test_save_to_file_with_unknown_error(self) -> None:
        image_mock = ImageMock.save_image_with_os_error()

        fake_path = "/testing/fake/format.png"

        fake_image_service = ImageToPNG(image_mock)

        with self.assertRaises(MusicManagerError) as caught_error:
            fake_image_service.to_file(fake_path)

        self.assertIn("OSError", str(caught_error.exception))
        image_mock.save.assert_called_once_with(fake_path)
