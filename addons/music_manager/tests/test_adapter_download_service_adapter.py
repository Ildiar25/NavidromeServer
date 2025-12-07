from odoo.tests.common import TransactionCase

from ..services.download_service import DownloadTrack
from ..adapters.download_service_adapter import DownloadServiceAdapter


class TestAdapterImageService(TransactionCase):

    def setUp(self) -> None:
        self.fake_url = "https://www.fake-url.com/"

        # Testing with default value: YTDLPAdapter
        self.adapter = DownloadServiceAdapter(self.fake_url)

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_downloader_instance(self) -> None:
        self.assertIsInstance(self.adapter._downloader, DownloadTrack, msg=f"")