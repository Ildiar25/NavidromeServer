import io
from pathlib import Path
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from ..adapters.download_service_adapter import DownloadServiceAdapter
from ..services.download_service import DownloadTrack, StreamProtocol, PyTubeAdapter, YTDLPAdapter
from ..utils.enums import AdapterType
from ..utils.exceptions import InvalidPathError, DownloadServiceError


class TestAdapterImageService(TransactionCase):

    patch_path = (
        'odoo.addons.music_manager.adapters.download_service_adapter.DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE'
    )

    def setUp(self) -> None:
        self.fake_url = "https://www.fake-url.com/"
        self.fake_path = "/test/fake/directory"

        self.given_data = b'Fake mp3'

        # Testing with default value: YTDLPAdapter
        self.with_ytdlp_adapter = DownloadServiceAdapter(self.fake_url)

        # Testing with PyTube adapter
        self.with_pytbe_adapter = DownloadServiceAdapter(self.fake_url, 'pytube')

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

    def test_init_invalid_adapter_type(self) -> None:
        new_adapter = None

        with self.assertRaises(DownloadServiceError) as caught_error:
            new_adapter = DownloadServiceAdapter(self.fake_url, 'invalid_adapter')

        self.assertIsInstance(caught_error.exception, DownloadServiceError)
        self.assertIsNone(new_adapter, msg="New adapter should be None. Adapter not initialized.")

    # =========================================================================================
    # Testing for 'to_file' (PYTUBE)
    # =========================================================================================

    @patch.dict(patch_path, {AdapterType.PYTUBE: MagicMock(spec=PyTubeAdapter)})
    def test_pytube_to_file_success(self) -> None:
        pytube_adapter_mock = MagicMock(spec=StreamProtocol)
        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.PYTUBE].return_value = pytube_adapter_mock

        self.with_pytbe_adapter.to_file(self.fake_path)

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.PYTUBE].assert_called_once_with(self.fake_url)
        pytube_adapter_mock.stream_to_file.assert_called_once_with(Path(self.fake_path))

    @patch.dict(patch_path, {AdapterType.PYTUBE: MagicMock(spec=PyTubeAdapter)})
    def test_pytube_to_file_with_invalid_path_error(self) -> None:
        pytube_adapter_mock = MagicMock(spec=StreamProtocol)
        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.PYTUBE].return_value = pytube_adapter_mock

        with self.assertRaises(InvalidPathError) as caught_error:
            self.with_pytbe_adapter.to_file(123456789)

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.PYTUBE].assert_called_once_with(self.fake_url)
        pytube_adapter_mock.stream_to_file.assert_not_called()
        self.assertIsInstance(caught_error.exception, InvalidPathError)

    # =========================================================================================
    # Testing for 'to_file' (YTDLP)
    # =========================================================================================

    @patch.dict(patch_path, {AdapterType.YTDLP: MagicMock(spec=YTDLPAdapter)})
    def test_ytdlp_to_file_success(self) -> None:
        ytdlp_adapter_mock = MagicMock(spec=StreamProtocol)
        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.YTDLP].return_value = ytdlp_adapter_mock

        self.with_ytdlp_adapter.to_file(self.fake_path)

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.YTDLP].assert_called_once_with(self.fake_url)
        ytdlp_adapter_mock.stream_to_file.assert_called_once_with(Path(self.fake_path))

    @patch.dict(patch_path, {AdapterType.YTDLP: MagicMock(spec=YTDLPAdapter)})
    def test_ytdlp_to_file_with_invalid_path_error(self) -> None:
        ytdlp_adapter_mock = MagicMock(spec=StreamProtocol)
        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.YTDLP].return_value = ytdlp_adapter_mock

        with self.assertRaises(InvalidPathError) as caught_error:
            self.with_ytdlp_adapter.to_file(123456789)

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.YTDLP].assert_called_once_with(self.fake_url)
        ytdlp_adapter_mock.stream_to_file.assert_not_called()
        self.assertIsInstance(caught_error.exception, InvalidPathError)

    # =========================================================================================
    # Testing for 'to_buffer' (PYTUBE)
    # =========================================================================================

    @patch.dict(patch_path, {AdapterType.PYTUBE: MagicMock(spec=PyTubeAdapter)})
    def test_pytube_to_buffer_success(self) -> None:
        expected_data = b'Fake mp3'

        pytube_adapter_mock = MagicMock(spec=StreamProtocol)
        pytube_adapter_mock.stream_to_buffer.side_effect = self.write_example_bytes

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.PYTUBE].return_value = pytube_adapter_mock

        result = self.with_pytbe_adapter.to_buffer()

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.PYTUBE].assert_called_once_with(self.fake_url)
        pytube_adapter_mock.stream_to_buffer.assert_called_once()
        self.assertEqual(result, expected_data)

    # =========================================================================================
    # Testing for 'to_buffer' (YTDLP)
    # =========================================================================================

    @patch.dict(patch_path, {AdapterType.YTDLP: MagicMock(spec=YTDLPAdapter)})
    def test_ytdlp_to_buffer_success(self) -> None:
        expected_data = b'Fake mp3'

        ytdlp_adapter_mock = MagicMock(spec=StreamProtocol)
        ytdlp_adapter_mock.stream_to_buffer.side_effect = self.write_example_bytes

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.YTDLP].return_value = ytdlp_adapter_mock

        result = self.with_ytdlp_adapter.to_buffer()

        DownloadServiceAdapter.DOWNLOAD_ADAPTER_TYPE[AdapterType.YTDLP].assert_called_once_with(self.fake_url)
        ytdlp_adapter_mock.stream_to_buffer.assert_called_once()
        self.assertEqual(result, expected_data)

    # =========================================================================================
    # Testing for NO ADAPTER
    # =========================================================================================

    @patch.dict(patch_path, {AdapterType.YTDLP: None})
    def test_with_no_adapter(self) -> None:
        new_adapter = DownloadServiceAdapter(self.fake_url)

        with self.assertRaises(DownloadServiceError) as caught_to_file_error:
            new_adapter.to_file(self.fake_path)

        with self.assertRaises(DownloadServiceError) as caught_to_buffer_error:
            new_adapter.to_buffer()

        self.assertIsInstance(caught_to_file_error.exception, DownloadServiceError)
        self.assertIsInstance(caught_to_buffer_error.exception, DownloadServiceError)

    def write_example_bytes(self, buffer: io.BytesIO):
        buffer.write(self.given_data)
