from typing import Any, Type, TypeVar
from unittest.mock import MagicMock


E = TypeVar("E", bound=BaseException)


class BaseMock:

    """
    Provides reusable mock objects and functions for testing different service dependencies.
    """

    @classmethod
    def create_mock(cls, mock_class: Type[Any] | None = None, **kwargs) -> MagicMock:
        mock = MagicMock(spec=mock_class)

        for name, value in kwargs.items():
            setattr(mock, name, value)

        return mock

    @classmethod
    def simulate_error(cls, error_type: Type[E], message: str | None = None) -> E:
        msg = message or f"SIMULATING ERROR || {error_type.__name__} ||"

        return error_type(msg)


# def fake_open_plain_text_file_without_errors(data: str = "Fake data") -> MagicMock:
#     mock_file = mock_open(read_data=data)
#     return mock_file
#
# def fake_open_bytes_file_without_errors(data: bytes = b"Fake data") -> MagicMock:
#     mock_file = mock_open()
#     mock_file.return_value.read.return_value = data
#     return mock_file
#
# def fake_open_with_file_not_found_error() -> MagicMock:
#     mock_file = mock_open()
#     mock_file.side_effect = FileNotFoundError
#     return mock_file
#
# def fake_open_with_permission_error() -> MagicMock:
#     mock_file = mock_open()
#     mock_file.side_effect = PermissionError
#     return mock_file
#
# # OS Module
#
# def fake_os_rename_without_errors() -> MagicMock:
#     return MagicMock()
#
# def fake_os_rename_with_file_not_found_error() -> MagicMock:
#     mock_file = MagicMock()
#     mock_file.side_effect = FileNotFoundError
#     return mock_file
#
# def fake_os_rename_with_permission_error() -> MagicMock:
#     mock_file = MagicMock()
#     mock_file.side_effect = PermissionError
#     return mock_file
#
# def fake_os_remove_without_errors() -> MagicMock:
#     return MagicMock()
#
# def fake_os_remove_with_file_not_found_error() -> MagicMock:
#     mock_file = MagicMock()
#     mock_file.side_effect = FileNotFoundError
#     return mock_file
#
# def fake_os_remove_with_permission_error() -> MagicMock:
#     mock_file = MagicMock()
#     mock_file.side_effect = PermissionError
#     return mock_file
#
# def fake_os_remove_dir_without_errors() -> MagicMock:
#     return MagicMock()
#
# def fake_os_remove_dir_with_file_not_found_error() -> MagicMock:
#     mock_dir = MagicMock()
#     mock_dir.side_effect = FileNotFoundError
#     return mock_dir
#
# def fake_os_remove_dir_with_permission_error() -> MagicMock:
#     mock_dir = MagicMock()
#     mock_dir.side_effect = PermissionError
#     return mock_dir
#
#
# class MockHelper:
#     """Provides reusable mock objects and functions for testing different service dependencies."""
#
#     # ----- File System ----- #
#
#     @staticmethod
#     def fake_open_text(data: str = "file data") -> MagicMock:
#         """Simulates opening and reading a plain text file.
#         :param data: Fake data in plain text.
#         :return: A MagicMock simulating the built-in 'open' function for plain text mode ('r').
#         """
#         return mock_open(read_data=data)
#
#     @staticmethod
#     def fake_open_bytes(data: bytes = b"file data") -> MagicMock:
#         """Simulates opening and reading a binary file.
#         :param data: Fake data in bytes.
#         :return: A MagicMock simulating the built-in 'open' function for binary mode ('rb').
#         """
#         mock_file = io.BytesIO(data)
#         mock_open_file = MagicMock()
#         mock_open_file.return_value = mock_file
#         return mock_open_file
#
#     @staticmethod
#     def fake_os_remove_without_errors() -> MagicMock:
#         """Simulates deleting a file without errors.
#         :return: A MagicMock simulating the deleting function (e.g., 'os.remove').
#         """
#         return MagicMock()
#
#     @staticmethod
#     def fake_os_rename() -> MagicMock:
#         """Simulates moving/renaming a file between directories without errors.
#         :return: A MagicMock simulating the renaming function (e.g., 'path.replace').
#         """
#         return MagicMock()
#
#     # ----- Data Buffering ----- #
#
#     @staticmethod
#     def fake_buffering(initial_data: bytes = b"") -> io.BytesIO:
#         """Simulates loading binary data in memory.
#         :param initial_data: Fake binary initial data.
#         :return: An in-memory binary buffer (io.BytesIO) with optional initial data.
#         """
#         return io.BytesIO(initial_data)
#
#     # ----- Subprocesses & System commands ----- #
#
#     @staticmethod
#     def fake_subprocess_run(success: bool = True) -> MagicMock:
#         """Simulates the result of 'subprocess.run()'.
#         :param success: If True, simulates a successful execution (returncode 0). Otherwise, an error (returncode 1).
#         :return: A MagicMock simulating the callable 'subprocess.run' which returns a 'CompletedProcess' object.
#         """
#         mock_result = MagicMock(
#             returncode = 0 if success else 1,
#             stdout = b"Command output" if success else b"",
#             stderr = b"" if success else b"There was an error."
#         )
#
#         return MagicMock(return_value=mock_result)
#
#     # ----- Image manipulation ----- #
#
#     @staticmethod
#     def fake_image_open(img_format: str = 'JPEG') -> MagicMock:
#         """Simulates opening and reading an image file (e.g., PIL.Image.open).
#         :param img_format: Set image format (JPEG by default)
#         :return: A MagicMock simulating the built-in 'open' function for binary mode ('rb').
#         """
#         mock_image = MagicMock()
#         mock_image.format = img_format
#         return MagicMock(return_value=mock_image)
#
#     @staticmethod
#     def fake_save_image() -> MagicMock:
#         """Simulates file writing (e.g., the image object's 'save' method).
#         :return: A MagicMock with a mockable 'save' method, simulating the image writer object.
#         """
#         return MagicMock()
#
#     # ----- Metadata editing ----- #
#
#     @staticmethod
#     def fake_metadata_reader() -> MagicMock:
#         """Simulates metadata reading (e.g., the audio object's 'read' method).
#         :return: A MagicMock with a mockable 'read' method, simulating the audio reader object.
#         """
#         mock_audio = MagicMock()
#         fake_tags = mutagen.id3.ID3()
#
#         fake_tags['TIT2'] = mutagen.id3.TIT2(encoding=3, text=["Unknown"])      # Fake Title
#         fake_tags['TPE1'] = mutagen.id3.TPE1(encoding=3, text=["Unknown"])      # Fake Track artist
#         fake_tags['TPE2'] = mutagen.id3.TPE2(encoding=3, text=["Unknown"])      # Fake Album artist
#         fake_tags['TOPE'] = mutagen.id3.TOPE(encoding=3, text=["Unknown"])      # Fake Original artist
#         fake_tags['TALB'] = mutagen.id3.TALB(encoding=3, text=["Unknown"])      # Fake Album
#         fake_tags['TCMP'] = mutagen.id3.TCMP(encoding=3, text=["0"])            # Fake Compilation
#         fake_tags['TRCK'] = mutagen.id3.TRCK(encoding=3, text=["1"])            # Fake Track no
#         fake_tags['TPOS'] = mutagen.id3.TPOS(encoding=3, text=["1"])            # Fake Disk no
#         fake_tags['TDRC'] = mutagen.id3.TDRC(encoding=3, text=["Unknown"])      # Fake Year
#         fake_tags['TCON'] = mutagen.id3.TCON(encoding=3, text=["Unknown"])      # Fake Genre
#         fake_tags['APIC'] = mutagen.id3.APIC(                                   # Fake Cover
#             encoding=3,
#             mime='image/png',
#             type=3,
#             desc='Cover',
#             data=[b"fake_image_bytes"]
#         )
#
#         mock_audio.tags = fake_tags
#         return MagicMock(return_value=mock_audio)
#
#     @staticmethod
#     def fake_metadata_writer() -> MagicMock:
#         """Simulates metadata writing (e.g., the audio object's 'save' method).
#         :return: A MagicMock with a mockable 'save' method, simulating the audio writer object.
#         """
#         mock_writer = MagicMock()
#         mock_writer.save = MagicMock()
#         return mock_writer
#
#     # ----- External entities ----- #
#
#     @staticmethod
#     def fake_pytube_adapter() -> MagicMock:
#         """Simulates a successful video stream download using a Pytube-like object.
#         :return: A MagicMock simulating the Pytube 'YouTube' object, configured to return a successful download path.
#         """
#         mock_video = MagicMock()
#         mock_stream = MagicMock()
#         mock_stream.download.return_value = "/tmp/fake_download"
#         mock_video.streams.filter.return_value.first.return_value = mock_stream
#         return MagicMock(return_value=mock_video)
#
#     @staticmethod
#     def fake_ytdlp_adapter() -> tuple[MagicMock, MagicMock]:
#         """Simulates a 'yt-dlp' download manager instance used in a context manager ('with').
#         :return: A tuple of (Mocked yt_dlp callable, Mocked yt-dlp instance object).
#         """
#         mock_dl_instance = MagicMock()
#         mock_dl = MagicMock()
#         mock_dl.return_value.__enter__.return_value = mock_dl_instance
#         return mock_dl, mock_dl_instance
