import io
import hashlib
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Dict
from unittest.mock import mock_open, patch

from odoo.tests.common import TransactionCase

from .mocks.download_mock import DownloadMock, PytubeAdapterMock, YTDLPAdapterMock
from ..services.download_service import PyTubeAdapter, YoutubeDownload, YTDLPAdapter
from ..utils.exceptions import ClientPlatformError, VideoProcessingError, MusicManagerError


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
        self.fake_download_path = Path('/fake/video/path.mp4')
        self.fake_path = Path('/fake/output/path.mp3')
        self.fake_url = "https://www.fake-url.com/"

        self.tmp_path = Path('/tmp')
        self.buffer = io.BytesIO()
        self.filename = hashlib.sha256(self.fake_url.encode()).hexdigest()
        self.final_path = self.tmp_path / f'{self.filename}.mp3'

        self.given_data = b'Fake mp3'

        self.config = {
            'format': "mp3",
            'quality': "192",
        }

        self.pytube_adapter = PyTubeAdapter(self.fake_url, self.config)

    def tearDown(self) -> None:
        self.buffer.close()

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_url_instance(self) -> None:
        self.assertIsNotNone(self.pytube_adapter._url, msg="URL is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.pytube_adapter._url,
            str,
            msg=f"URL path must be a 'str' instance, got {type(self.pytube_adapter.url)} instead."
        )

    def test_init_path_instance(self) -> None:
        self.assertIsNotNone(self.pytube_adapter._tmp_path, msg="Path is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.pytube_adapter._tmp_path,
            Path,
            msg=f"Path must be a 'Path' instance, got {type(self.pytube_adapter.tmp_path)} instead."
        )

    def test_init_with_config_instance(self) -> None:
        self.assertIsNotNone(self.pytube_adapter._options, msg="Options is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.pytube_adapter._options,
            Dict,
            msg=f"Options must be a 'Dict' instance, got {type(self.pytube_adapter.options)} instead."
        )
        self.assertTrue('format' in self.pytube_adapter.options.keys(), msg="Options must have 'format' key.")
        self.assertTrue('quality' in self.pytube_adapter.options.keys(), msg="Options must have 'quality' key.")

    def test_init_with_given_url(self) -> None:
        self.assertIsInstance(self.pytube_adapter.url, str, msg=f"URL must be returned as 'str' instance.")
        self.assertEqual(self.pytube_adapter.url, self.fake_url, msg=f"URL must be {self.fake_url}")

    def test_init_with_initial_path(self) -> None:
        self.assertIsInstance(self.pytube_adapter.tmp_path, str, msg=f"Path must be returned as 'str' instance.")
        self.assertEqual(self.pytube_adapter.tmp_path, str(self.tmp_path), msg=f"Path must be {self.tmp_path}.")

    def test_init_with_given_config(self) -> None:
        self.assertIsInstance(self.pytube_adapter.options['format'], str, msg="Format must be a 'str' instance.")
        self.assertEqual(
            self.pytube_adapter.options['format'],
            self.config['format'],
            msg=f"Format must be {self.config['format']}"
        )
        self.assertIsInstance(self.pytube_adapter.options['quality'], str, msg="Quality must be a 'str' instance.")
        self.assertEqual(
            self.pytube_adapter.options['quality'],
            self.config['quality'],
            msg=f"Format must be {self.config['quality']}"
        )

    # =========================================================================================
    # Testing for 'stream_to_file'
    # =========================================================================================

    def test_pytube_stream_to_file_success(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_success()) as mock:
            self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.fake_path)
            mock['clean'].assert_called_once_with(self.fake_download_path)

    def test_pytube_stream_to_file_with_regex_match_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_regex_match_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_pytube_stream_to_file_with_video_private_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_video_private_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_pytube_stream_to_file_with_video_region_blocked_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_video_region_blocked_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_pytube_stream_to_file_with_video_unavailable_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_video_unavailable_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_pytube_stream_to_file_with_http_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_http_error()) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, MusicManagerError)

    def test_pytube_stream_to_file_with_os_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_os_error()) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, MusicManagerError)

    def test_pytube_stream_to_file_with_ffmpeg_process_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_subprocess_error()) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.fake_path)
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)

    def test_pytube_stream_to_file_with_file_not_found_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_file_not_found_error()) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.fake_path)
            mock['clean'].assert_called_once_with(self.fake_download_path)

        self.assertIsInstance(caught_error.exception, VideoProcessingError)

    def test_pytube_stream_to_file_with_permission_error(self) -> None:
        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_with_permission_error()) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_file(self.fake_path)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.fake_path)
            mock['clean'].assert_called_once_with(self.fake_download_path)

        self.assertIsInstance(caught_error.exception, VideoProcessingError)

    # =========================================================================================
    # Testing for 'stream_to_buffer'
    # =========================================================================================

    def test_pytube_stream_to_buffer_success(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            self.assertEqual(
                mock['clean'].call_count,
                2,
                f"Method '_clean_temp_file' must called twice. Called {mock['clean'].call_count} time(s)."
            )

        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_pytube_stream_to_buffer_with_regex_match_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_regex_match_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_pytube_stream_to_buffer_with_video_private_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_video_private_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_pytube_stream_to_buffer_with_video_region_blocked_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_video_region_blocked_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_pytube_stream_to_buffer_with_video_unavailable_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_video_unavailable_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_not_called()
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_pytube_stream_to_buffer_with_ffmpeg_process_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_subprocess_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_pytube_stream_to_buffer_with_file_not_found_error_while_deleting_tmp_file(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_file_not_found_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_called_once_with(self.fake_download_path)

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_pytube_stream_to_buffer_with_permission_error_while_deleting_tmp_file(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_permission_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_called_once_with(self.fake_download_path)

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_pytube_stream_to_buffer_with_unknown_error_while_deleting_tmp_file(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)

        with self.create_context(
                mock_factory=PytubeAdapterMock.stream_to_with_unknown_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_called_once_with(self.fake_download_path)

        self.assertIsInstance(caught_error.exception, MusicManagerError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_pytube_stream_to_buffer_with_file_not_found_error_while_reading_downloaded_file(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        open_mock.side_effect = FileNotFoundError

        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_pytube_stream_to_buffer_with_permission_error_while_reading_downloaded_file(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        open_mock.side_effect = PermissionError

        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_pytube_stream_to_buffer_with_unknown_error_while_reading_downloaded_file(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        open_mock.side_effect = Exception

        with self.create_context(mock_factory=PytubeAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.pytube_adapter.stream_to_buffer(self.buffer)

            mock['download'].assert_called_once_with(self.tmp_path, self.filename)
            mock['subprocess'].assert_called_once_with(self.fake_download_path, self.final_path)
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, MusicManagerError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )


    @contextmanager
    def create_context(self, mock_factory, open_mock = None):
        with (
            mock_factory,
            patch.object(
                PyTubeAdapter, '_clean_temp_file', wraps=self.pytube_adapter._clean_temp_file
            ) as mock_clean,
            patch.object(
                PyTubeAdapter, '_download_track', wraps=self.pytube_adapter._download_track
            ) as mock_download,
            patch.object(
                PyTubeAdapter, '_subprocess_track_to_mp3', wraps=self.pytube_adapter._subprocess_track_to_mp3
            ) as mock_subprocess,
            patch('builtins.open', open_mock) if open_mock else nullcontext()
        ):
            yield {
                'clean': mock_clean,
                'download': mock_download,
                'subprocess': mock_subprocess,
                'open': open_mock
            }


class TestYTDLPAdapter(TransactionCase):

    def setUp(self) -> None:
        self.fake_download_path = Path('/fake/video/path')
        self.fake_url = "https://www.fake-url.com/"

        self.tmp_path = Path('/tmp')
        self.buffer = io.BytesIO()
        self.filename = hashlib.sha256(self.fake_url.encode()).hexdigest()
        self.final_path = self.tmp_path / f'{self.filename}.mp3'

        self.given_data = b'Fake mp3'

        self.config = {
            'format': "mp3",
            'quality': "192",
        }

        self.ytdlp_adapter = YTDLPAdapter(self.fake_url, self.config)

    def tearDown(self) -> None:
        self.buffer.close()

    # =========================================================================================
    # Testing for '__init__'
    # =========================================================================================

    def test_init_url_instance(self) -> None:
        self.assertIsNotNone(self.ytdlp_adapter._url, msg="URL is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.ytdlp_adapter._url,
            str,
            msg=f"URL path must be a 'str' instance, got '{type(self.ytdlp_adapter._url)}' instead."
        )

    def test_init_options_instance(self) -> None:
        self.assertIsNotNone(self.ytdlp_adapter._options, msg="Options is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.ytdlp_adapter._options,
            Dict,
            msg=f"Options must be a 'Dict' instance, got '{type(self.ytdlp_adapter._options)}' instead."
        )

    def test_init_tmp_path_instance(self) -> None:
        self.assertIsNotNone(self.ytdlp_adapter._tmp_path, msg="Temp Path is mandatory before instantiate the adapter.")
        self.assertIsInstance(
            self.ytdlp_adapter._tmp_path,
            Path,
            msg=f"Tmp Path must be a 'Path' instance, got '{type(self.ytdlp_adapter._options)}' instead."
        )

    def test_init_with_given_url(self) -> None:
        self.assertIsInstance(self.ytdlp_adapter.url, str, msg="URL must be returned as 'str' instance.")
        self.assertEqual(self.ytdlp_adapter.url, self.fake_url, msg=f"URL must be '{self.fake_url}'.")

    def test_init_with_initial_path(self) -> None:
        self.assertIsInstance(self.ytdlp_adapter.tmp_path, str, msg="Path must be returned as 'str' instance.")
        self.assertEqual(self.ytdlp_adapter.tmp_path, str(self.tmp_path), msg=f"Path must be '{self.tmp_path}'.")

    def test_init_with_given_config(self) -> None:
        self.assertIsInstance(
            self.ytdlp_adapter.options['postprocessors'][0]['preferredcodec'],
            str,
            msg="Format must be a 'str' instance."
        )
        self.assertEqual(
            self.ytdlp_adapter.options['postprocessors'][0]['preferredcodec'],
            self.config['format'],
            msg=f"Format must be {self.config['format']}"
        )
        self.assertIsInstance(
            self.ytdlp_adapter.options['postprocessors'][0]['preferredquality'],
            str,
            msg="Quality must be a 'str' instance."
        )
        self.assertEqual(
            self.ytdlp_adapter.options['postprocessors'][0]['preferredquality'],
            self.config['quality'],
            msg=f"Format must be {self.config['quality']}"
        )

    # =========================================================================================
    # Testing for 'stream_to_file'
    # =========================================================================================

    def test_ytdlp_stream_to_file_success(self) -> None:
        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_success()) as mock:
            self.ytdlp_adapter.stream_to_file(self.fake_download_path)

            mock['options'].assert_called_once_with(self.fake_download_path)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['clean'].assert_not_called()

    def test_ytdlp_stream_to_file_with_regex_not_found_error(self) -> None:
        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_with_regex_not_found_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_file(self.fake_download_path)

            mock['options'].assert_called_once_with(self.fake_download_path)
            mock['youtube'].download.assert_called_once_with([self.fake_url])

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_ytdlp_stream_to_file_with_max_downloads_reached_error(self) -> None:
        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_with_max_downloads_reached_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_file(self.fake_download_path)

            mock['options'].assert_called_once_with(self.fake_download_path)
            mock['youtube'].download.assert_called_once_with([self.fake_url])

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_ytdlp_stream_to_file_with_unavailable_video_error(self) -> None:
        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_with_unavailable_video_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_file(self.fake_download_path)

            mock['options'].assert_called_once_with(self.fake_download_path)
            mock['youtube'].download.assert_called_once_with([self.fake_url])

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_ytdlp_stream_to_file_with_download_error(self) -> None:
        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_with_download_error()) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_file(self.fake_download_path)

            mock['options'].assert_called_once_with(self.fake_download_path)
            mock['youtube'].download.assert_called_once_with([self.fake_url])

        self.assertIsInstance(caught_error.exception, ClientPlatformError)

    def test_ytdlp_stream_to_file_with_youtubedl_error(self) -> None:
        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_with_youtube_dl_error()) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.ytdlp_adapter.stream_to_file(self.fake_download_path)

            mock['options'].assert_called_once_with(self.fake_download_path)
            mock['youtube'].download.assert_called_once_with([self.fake_url])

        self.assertIsInstance(caught_error.exception, VideoProcessingError)

    def test_ytdlp_stream_to_file_with_unkown_error(self) -> None:
        with self.create_context(mock_factory=YTDLPAdapterMock.download_stream_to_with_unknown_error()) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.ytdlp_adapter.stream_to_file(self.fake_download_path)

            mock['options'].assert_called_once_with(self.fake_download_path)
            mock['youtube'].download.assert_called_once_with([self.fake_url])

        self.assertIsInstance(caught_error.exception, MusicManagerError)

    # =========================================================================================
    # Testing for 'stream_to_buffer'
    # =========================================================================================

    def test_ytdlp_stream_to_buffer_success(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_called_once()

        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_ytdlp_stream_to_buffer_with_regex_not_found_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_regex_not_found_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_max_downloads_reached_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_max_downloads_reached_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_unavailable_video_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_unavailable_video_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_download_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_download_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(ClientPlatformError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, ClientPlatformError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_youtubedl_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_youtube_dl_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_unkown_error(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.download_stream_to_with_unknown_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_not_called()
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, MusicManagerError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_file_not_found_error_while_deleting_tmp_file(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_file_not_found_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_called_once()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_ytdlp_stream_to_buffer_with_permission_error_while_deleting_tmp_file(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_permission_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_called_once()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_ytdlp_stream_to_buffer_with_unknown_error_while_deleting_tmp_file(self) -> None:
        expected_data = b'Fake mp3'
        open_mock = mock_open(read_data=self.given_data)
        download_filename = self.tmp_path / self.filename

        with self.create_context(
                mock_factory=YTDLPAdapterMock.stream_to_with_permission_error(), open_mock=open_mock
        ) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_called_once()

        self.assertIsInstance(caught_error.exception, MusicManagerError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be '{expected_data}', got {self.buffer.getvalue()} instead."
        )

    def test_ytdlp_stream_to_buffer_with_file_not_found_error_while_reading_downloaded_file(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        open_mock.side_effect = FileNotFoundError
        download_filename = self.tmp_path / self.filename

        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_permission_error_while_reading_downloaded_file(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        open_mock.side_effect = PermissionError
        download_filename = self.tmp_path / self.filename

        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            with self.assertRaises(VideoProcessingError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, VideoProcessingError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    def test_ytdlp_stream_to_buffer_with_unknown_error_while_reading_downloaded_file(self) -> None:
        expected_data = b''
        open_mock = mock_open(read_data=self.given_data)
        open_mock.side_effect = Exception("SIMULATING ERROR || Exception ||")
        download_filename = self.tmp_path / self.filename

        with self.create_context(mock_factory=YTDLPAdapterMock.stream_to_success(), open_mock=open_mock) as mock:
            with self.assertRaises(MusicManagerError) as caught_error:
                self.ytdlp_adapter.stream_to_buffer(self.buffer)

            mock['options'].assert_called_once_with(download_filename)
            mock['youtube'].download.assert_called_once_with([self.fake_url])
            mock['open'].assert_called_once_with(self.final_path, 'rb')
            mock['clean'].assert_not_called()

        self.assertIsInstance(caught_error.exception, MusicManagerError)
        self.assertEqual(
            self.buffer.getvalue(),
            expected_data,
            msg=f"Return value must be empty, got '{self.buffer.getvalue()}' instead."
        )

    @contextmanager
    def create_context(self, mock_factory, open_mock = None):
        with (
            mock_factory as mock_result,
            patch.object(
                YTDLPAdapter, '_get_download_options', wraps=self.ytdlp_adapter._get_download_options
            ) as mock_options,
            patch.object(
                YTDLPAdapter, '_clean_temp_file', wraps=self.ytdlp_adapter._clean_temp_file
            ) as mock_clean,
            patch('builtins.open', open_mock) if open_mock else nullcontext()
        ):
            yield {
                'youtube': mock_result['youtube'],
                'unlink': mock_result['unlink'],
                'options': mock_options,
                'clean': mock_clean,
                'open': open_mock
            }
