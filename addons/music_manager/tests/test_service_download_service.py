import io
import hashlib
from pathlib import Path
from unittest.mock import mock_open, patch

from odoo.tests.common import TransactionCase

from .mocks.download_mock import DownloadMock, PytubeAdapterMock
from ..services.download_service import YoutubeDownload, PyTubeAdapter
from ..utils.exceptions import ClientPlatformError, VideoProcessingError


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


class TestPyTubeAdapter(TransactionCase):

    def setUp(self) -> None:
        self.fake_download_path = Path("/fake/video.mp4")
        self.fake_path = Path("/fake/output/path.mp3")

        self.fake_url = "https://www.fake-url.com/"
        self.tmp_path = Path('/tmp')
        self.buffer = io.BytesIO()

        self.pytube_adapter = PyTubeAdapter(self.fake_url)

    def tearDown(self) -> None:
        self.buffer.close()

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_url_instance(self) -> None:
        self.assertIsInstance(self.pytube_adapter.url, str, "URL path must be a 'str' instance.")

    def test_init_temp_path_instance(self) -> None:
        self.assertIsInstance(self.pytube_adapter.tmp_path, Path, "Temp path must be a 'Path' instance." )

    # =========================================================================================
    # Testing for 'stream_to_file'
    # =========================================================================================

    def test_pytube_stream_to_file_success(self) -> None:
        with (
            PytubeAdapterMock.stream_to_success(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            self.pytube_adapter.stream_to_file(self.fake_path)

            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, self.fake_path)
            mock_clean.assert_called_once_with(self.fake_download_path)

    def test_pytube_stream_to_file_with_regex_match_error(self) -> None:
        with (
            PytubeAdapterMock.stream_to_with_regex_match_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_clean.assert_not_called()

    def test_pytube_stream_to_file_with_video_private_error(self) -> None:
        with (
            PytubeAdapterMock.stream_to_with_video_private_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_clean.assert_not_called()

    def test_pytube_stream_to_file_with_video_region_blocked_error(self) -> None:
        with (
            PytubeAdapterMock.stream_to_with_video_region_blocked_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_clean.assert_not_called()

    def test_pytube_stream_to_file_with_video_unavailable_error(self) -> None:
        with (
            PytubeAdapterMock.stream_to_with_video_unavailable_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_clean.assert_not_called()

    def test_pytube_stream_to_file_with_ffmpeg_process_error(self) -> None:
        with (
            PytubeAdapterMock.stream_to_with_subprocess_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, VideoProcessingError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, self.fake_path)
            mock_clean.assert_not_called()

    def test_pytube_stream_to_file_with_file_not_found_error(self) -> None:
        with (
            PytubeAdapterMock.stream_to_with_file_not_found_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, VideoProcessingError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, self.fake_path)
            mock_clean.assert_called_once_with(self.fake_download_path)

    def test_pytube_stream_to_file_with_permission_error(self) -> None:
        with (
            PytubeAdapterMock.stream_to_with_permission_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            self.assertIsInstance(caught_error.exception, VideoProcessingError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, self.fake_path)
            mock_clean.assert_called_once_with(self.fake_download_path)

    # =========================================================================================
    # Testing for 'stream_to_buffer'
    # =========================================================================================

    def test_pytube_stream_to_buffer_success(self) -> None:
        expected_data = b"Fake mp3"
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_success(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()
            final_path = self.tmp_path / f'{filename}.mp3'

            self.pytube_adapter.stream_to_buffer(self.buffer)

            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, final_path)
            mock_open_method.assert_called_once_with(final_path, 'rb')
            self.assertEqual(
                mock_clean.call_count,
                2,
                f"Method '_clean_temp_file' must called twice. Called {mock_clean.call_count} time(s)."
            )
            self.assertEqual(self.buffer.getvalue(), expected_data, f"Return value must be {expected_data}.")

    def test_pytube_stream_to_buffer_with_regex_match_error(self) -> None:
        expected_data = b""
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_with_regex_match_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_open_method.assert_not_called()
            mock_clean.assert_not_called()

            self.assertEqual(
                self.buffer.getvalue(), expected_data, f"Return value must be empty, got {self.buffer.getvalue()}."
            )

    def test_pytube_stream_to_buffer_with_video_private_error(self) -> None:
        expected_data = b""
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_with_video_private_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_open_method.assert_not_called()
            mock_clean.assert_not_called()
            self.assertEqual(
                self.buffer.getvalue(), expected_data, f"Return value must be empty, got {self.buffer.getvalue()}."
            )

    def test_pytube_stream_to_buffer_with_video_region_blocked_error(self) -> None:
        expected_data = b""
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_with_video_region_blocked_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_open_method.assert_not_called()
            mock_clean.assert_not_called()
            self.assertEqual(
                self.buffer.getvalue(), expected_data, f"Return value must be empty, got {self.buffer.getvalue()}."
            )

    def test_pytube_stream_to_buffer_with_video_unavailable_error(self) -> None:
        expected_data = b""
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_with_video_unavailable_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()

            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            self.assertIsInstance(caught_error.exception, ClientPlatformError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_not_called()
            mock_open_method.assert_not_called()
            mock_clean.assert_not_called()
            self.assertEqual(
                self.buffer.getvalue(), expected_data, f"Return value must be empty, got {self.buffer.getvalue()}."
            )

    def test_pytube_stream_to_buffer_with_ffmpeg_process_error(self) -> None:
        expected_data = b""
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_with_subprocess_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()
            final_path = self.tmp_path / f'{filename}.mp3'

            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            self.assertIsInstance(caught_error.exception, VideoProcessingError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, final_path)
            mock_open_method.assert_not_called()
            mock_clean.assert_not_called()
            self.assertEqual(
                self.buffer.getvalue(), expected_data, f"Return value must be empty, got {self.buffer.getvalue()}."
            )

    def test_pytube_stream_to_buffer_with_file_not_found_error(self) -> None:
        expected_data = b""
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_with_file_not_found_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()
            final_path = self.tmp_path / f'{filename}.mp3'

            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            self.assertIsInstance(caught_error.exception, VideoProcessingError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, final_path)
            mock_open_method.assert_called_once_with(final_path, 'rb')
            mock_clean.assert_called_once_with(self.fake_download_path)
            self.assertEqual(
                self.buffer.getvalue(), expected_data, f"Return value must be empty, got {self.buffer.getvalue()}."
            )

    def test_pytube_stream_to_buffer_with_permission_error(self) -> None:
        expected_data = b""
        open_mock_method = mock_open(read_data=expected_data)

        with (
            PytubeAdapterMock.stream_to_with_permission_error(),
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock_method) as mock_open_method
        ):

            filename = hashlib.sha256(self.fake_url.encode()).hexdigest()
            final_path = self.tmp_path / f'{filename}.mp3'

            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            self.assertIsInstance(caught_error.exception, VideoProcessingError)
            mock_download.assert_called_once_with(self.tmp_path, filename)
            mock_subprocess.assert_called_once_with(self.fake_download_path, final_path)
            mock_open_method.assert_called_once_with(final_path, 'rb')
            mock_clean.assert_called_once_with(self.fake_download_path)
            self.assertEqual(
                self.buffer.getvalue(), expected_data, f"Return value must be empty, got {self.buffer.getvalue()}."
            )


class TestYTDLPAdapter(TransactionCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass
