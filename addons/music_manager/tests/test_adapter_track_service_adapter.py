from unittest.mock import patch

from odoo.tests.common import TransactionCase

from .mocks.mp3_mock import MP3Mock
from ..adapters.track_service_adapter import TrackServiceAdapter
from ..utils.enums import FileType


class TestMetadataServiceAdapter(TransactionCase):

    def setUp(self) -> None:
        self.adapter = TrackServiceAdapter()

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_file_type(self):
        self.assertIsNotNone(self.adapter.file_type, msg="File type is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.adapter.file_type,
            FileType,
            msg=f"File type must be a 'FileType' instance, got '{type(self.adapter.file_type)}' instead."
        )

    def test_init_metadata_service(self) -> None:
        self.assertIsNone(self.adapter._service, msg="Service must be None when instantiate the adapter.")

    # =========================================================================================
    # Testing for 'read_metadata'
    # =========================================================================================
