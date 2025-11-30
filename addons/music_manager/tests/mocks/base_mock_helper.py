from typing import Any, Type, TypeVar
from unittest.mock import MagicMock


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


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
    def simulate_error(cls, error_type: Type[ExceptionType], message: str | None = None) -> ExceptionType:
        msg = message or f"SIMULATING ERROR || {error_type.__name__} ||"

        return error_type(msg)

# class MockHelper:
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
