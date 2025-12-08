import io
from pathlib import Path
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from ..adapters.download_service_adapter import DownloadServiceAdapter
from ..services.download_service import DownloadTrack, StreamProtocol
from ..utils.enums import AdapterType
from ..utils.exceptions import InvalidPathError, DownloadServiceError


class TestAdapterImageService(TransactionCase):

    def setUp(self) -> None:
        self.fake_url = "https://www.fake-url.com/"
        self.fake_path = "/test/fake/directory"

        self.given_data = b'Fake mp3'

        # Testing with default value: YTDLPAdapter
        self.with_ytdlp_adapter = DownloadServiceAdapter(self.fake_url)

        # Testing with PyTube adapter
        self.with_pytbe_adapter = DownloadServiceAdapter(self.fake_url, AdapterType.PYTUBE)

        # Testing without given adapter
        self.no_adapter = MagicMock(spec=AdapterType)
        self.with_none_adapter = DownloadServiceAdapter(self.fake_url, self.no_adapter)

    def tearDown(self) -> None:
        pass

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_url_instance(self) -> None:
        self.assertIsNotNone(self.with_ytdlp_adapter.video_url, msg="URL is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.with_ytdlp_adapter.video_url,
            str,
            msg=f"URL must be a 'str' instance, got '{type(self.with_ytdlp_adapter.video_url)}' instead."
        )

    def test_init_adapter_type_instance(self) -> None:
        self.assertIsNotNone(
            self.with_ytdlp_adapter.adapter_type, msg=f"AdapterType is mandatory before instantiate the adapter."
        )
        self.assertIsInstance(
            self.with_ytdlp_adapter.adapter_type,
            AdapterType,
            msg=f"Adapter must be 'AdapterType' instance, got '{type(self.with_ytdlp_adapter.adapter_type)}' instead."
        )

    def test_init_downloader_instance(self) -> None:
        self.assertIsNotNone(
            self.with_ytdlp_adapter._downloader, msg="Downloader is mandatory before instantiate the adapter."
        )
        self.assertIsInstance(
            self.with_ytdlp_adapter._downloader,
            DownloadTrack,
            msg=(f"Downloader must be a 'DownloadTrack' instance, "
                 f"got '{type(self.with_ytdlp_adapter._downloader)}' instead.")
        )

    # =========================================================================================
    # Testing for 'to_file'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.download_service_adapter.PyTubeAdapter')
    def test_pytube_to_file_success(self, pytbeadapter_class_mock: MagicMock) -> None:
        pytube_adapter_mock = MagicMock(spec=StreamProtocol)
        pytbeadapter_class_mock.return_value = pytube_adapter_mock

        self.with_pytbe_adapter.to_file(self.fake_path)

        pytbeadapter_class_mock.assert_called_once_with(self.fake_url)
        pytube_adapter_mock.stream_to_file.assert_called_once_with(Path(self.fake_path))

    @patch('odoo.addons.music_manager.adapters.download_service_adapter.YTDLPAdapter')
    def test_ytdlp_to_file_success(self, ytdlpadapter_class_mock: MagicMock) -> None:
        ytdlp_adapter_mock = MagicMock(spec=StreamProtocol)
        ytdlpadapter_class_mock.return_value = ytdlp_adapter_mock

        self.with_ytdlp_adapter.to_file(self.fake_path)

        ytdlpadapter_class_mock.assert_called_once_with(self.fake_url)
        ytdlp_adapter_mock.stream_to_file.assert_called_once_with(Path(self.fake_path))

    @patch('odoo.addons.music_manager.adapters.download_service_adapter.PyTubeAdapter')
    def test_pytube_to_file_with_invalid_path_error(self, pytbeadapter_class_mock: MagicMock) -> None:
        pytube_adapter_mock = MagicMock(spec=StreamProtocol)
        pytbeadapter_class_mock.return_value = pytube_adapter_mock

        with self.assertRaises(InvalidPathError) as caught_error:
            self.with_pytbe_adapter.to_file(123456789)

        pytbeadapter_class_mock.assert_called_once_with(self.fake_url)
        pytube_adapter_mock.stream_to_file.assert_not_called()
        self.assertIsInstance(caught_error.exception, InvalidPathError)

    @patch('odoo.addons.music_manager.adapters.download_service_adapter.YTDLPAdapter')
    def test_ytdlp_to_file_with_invalid_path_error(self, ytdlpadapter_class_mock: MagicMock) -> None:
        ytdlp_adapter_mock = MagicMock(spec=StreamProtocol)
        ytdlpadapter_class_mock.return_value = ytdlp_adapter_mock

        with self.assertRaises(InvalidPathError) as caught_error:
            self.with_ytdlp_adapter.to_file(123456789)

        ytdlpadapter_class_mock.assert_called_once_with(self.fake_url)
        ytdlp_adapter_mock.stream_to_file.assert_not_called()
        self.assertIsInstance(caught_error.exception, InvalidPathError)

    # =========================================================================================
    # Testing for 'to_buffer'
    # =========================================================================================

    @patch('odoo.addons.music_manager.adapters.download_service_adapter.PyTubeAdapter')
    def test_pytube_to_buffer_success(self, pytbeadapter_class_mock: MagicMock) -> None:
        expected_data = b'Fake mp3'

        pytube_adapter_mock = MagicMock(spec=StreamProtocol)
        pytube_adapter_mock.stream_to_buffer.side_effect = self.write_example_bytes

        pytbeadapter_class_mock.return_value = pytube_adapter_mock

        result = self.with_pytbe_adapter.to_buffer()

        pytbeadapter_class_mock.assert_called_once_with(self.fake_url)
        pytube_adapter_mock.stream_to_buffer.assert_called_once()
        self.assertEqual(result, expected_data)

    @patch('odoo.addons.music_manager.adapters.download_service_adapter.YTDLPAdapter')
    def test_ytdlp_to_buffer_success(self, ytdlpadapter_class_mock: MagicMock) -> None:
        expected_data = b'Fake mp3'

        ytdlp_adapter_mock = MagicMock(spec=StreamProtocol)
        ytdlp_adapter_mock.stream_to_buffer.side_effect = self.write_example_bytes

        ytdlpadapter_class_mock.return_value = ytdlp_adapter_mock

        result = self.with_ytdlp_adapter.to_buffer()

        ytdlpadapter_class_mock.assert_called_once_with(self.fake_url)
        ytdlp_adapter_mock.stream_to_buffer.assert_called_once()
        self.assertEqual(result, expected_data)

    # =========================================================================================
    # Testing for NO ADAPTER
    # =========================================================================================

    def test_without_given_adapter(self) -> None:
        with (
            patch.object(
                DownloadServiceAdapter, '_get_download_adapter', wraps=self.with_none_adapter._get_download_adapter
            )
        ) as mocked_method:

            with self.assertRaises(DownloadServiceError) as caught_error:
                self.with_none_adapter.to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, DownloadServiceError)

        mocked_method.assert_called_once()

    def write_example_bytes(self, buffer: io.BytesIO):
        buffer.write(self.given_data)
