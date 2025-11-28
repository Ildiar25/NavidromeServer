import io
from pathlib import Path
from unittest.mock import patch

from odoo.tests.common import TransactionCase

from .mocks.download_mock import DownloadMock
from ..services.download_service import YoutubeDownload


class TestDownloadService(TransactionCase):

    def setUp(self) -> None:
        self.buffer = io.BytesIO()
        self.output_path = Path("/fake/path/dir.mp3")
        self.downloader = YoutubeDownload()

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_with_downloader(self) -> None:
        self.assertIsInstance(
            self.downloader, YoutubeDownload, "Initial downloader must be an 'YoutubeDownload' instance."
        )

    # =========================================================================================
    # Testing for 'stream_to_file'
    # =========================================================================================

    def test_download_to_file_success(self) -> None:
        stream_mock = DownloadMock.stream_to_file_success()

        self.downloader.set_stream_to_file(stream_mock, self.output_path)
        stream_mock.stream_to_file.assert_called_once_with(self.output_path)

    # =========================================================================================
    # Testing for 'stream_to_buffer'
    # =========================================================================================

    def test_download_to_buffer_success(self) -> None:
        stream_mock = DownloadMock.stream_to_buffer_success()
        expected_data = b"Fake mp3"

        result = self.downloader.set_stream_to_buffer(stream_mock, self.buffer)
        stream_mock.stream_to_buffer.assert_called_once_with(self.buffer)
        self.assertEqual(result, expected_data)


class TestPyTUbeAdapter(TransactionCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass


class TestYTDLPAdapter(TransactionCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass
