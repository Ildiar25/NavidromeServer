from unittest.mock import patch

from PIL import Image

from odoo.tests.common import TransactionCase

from .mocks.image_mock import ImageMock
from ..services.image_service import ImageToPNG


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

