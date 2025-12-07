from odoo.tests.common import TransactionCase

from ..adapters.image_service_adapter import ImageServiceAdapter
from ..utils.constants import PNG_ENCODED_IMAGE


class TestAdapterImageService(TransactionCase):

    def setUp(self) -> None:
        self.adapter = ImageServiceAdapter(str_bytes_image=PNG_ENCODED_IMAGE)

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

