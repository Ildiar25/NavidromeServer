import logging

# noinspection PyProtectedMember
from odoo import _
from odoo.exceptions import ValidationError

from .image_service_adapter import ImageServiceAdapter
from ..services.metadata_service import MP3File
from ..utils.enums import FileType
from ..utils.exceptions import (
    InvalidFileFormatError, MetadataServiceError, MetadataPersistenceError, MusicManagerError, ReadingFileError
)


_logger = logging.getLogger(__name__)


class MetadataServiceAdapter:

    def __init__(self, file_type: FileType = FileType.MP3) -> None:

        self._metadata_service = None

        match file_type:
            case FileType.MP3:
                self._metadata_service = MP3File()

        if not self._metadata_service:
            raise MetadataServiceError("Metadata service is not selected")

    def read_metadata(self, track: bytes) -> dict[str, str | int | None]:
        try:
            metadata = self._metadata_service.get_metadata(track)

            return {
                'name': metadata.TIT2,
                'tmp_artists': metadata.TPE1,
                'tmp_album': metadata.TALB,
                'duration': self._format_track_duration(metadata.DUR),
                'tmp_genre': metadata.TCON,
                'tmp_album_artist': metadata.TPE2,
                'tmp_original_artist': metadata.TOPE,
                'year': metadata.TDRC,
                'track_no': metadata.TRCK[0],
                'total_track': metadata.TRCK[1],
                'disk_no': metadata.TPOS[0],
                'total_disk': metadata.TPOS[1],
                'file_type': metadata.MIME,
                'collection': metadata.TCMP,
                'picture': ImageServiceAdapter.encode_data(metadata.APIC) if metadata.APIC else None,
            }

        except InvalidFileFormatError as corrupt_file:
            _logger.error(f"There was a problem reading the file metadata: {corrupt_file}")
            raise ValidationError(
                _("\nThe uploaded file has an invalid format or is corrupt.")
            )

        except ReadingFileError as invalid_metadata:
            _logger.error(f"Failed to process file metadata: {invalid_metadata}")
            raise ValidationError(
                _("\nAn internal issue ocurred while processing metadata. Please, try a different file.")
            )

        except MusicManagerError as unknown_error:
            _logger.error(f"Unexpected error while processing the file: {unknown_error}")
            raise ValidationError(
                _("\nDamn! Something went wrong while processing metadata file.\nPlease, contact with your Admin.")
            )

    def write_metadata(self, file_path: str, track: dict[str, str | int | None]) -> None:
        metadata = {
            'TIT2': track['TIT2'],
            'TPE1': track['TPE1'],
            'TPE2': track['TPE2'],
            'TOPE': track['TOPE'],
            'TALB': track['TALB'],
            'TCMP': track['TCMP'],
            'TRCK': track['TRCK'],
            'TPOS': track['TPOS'],
            'TDRC': track['TDRC'],
            'TCON': track['TCON'],
            'APIC': ImageServiceAdapter.decode_data(track['APIC']) if track['APIC'] else None,
        }

        try:
            self._metadata_service.set_metadata(file_path, metadata)

        except ReadingFileError as invalid_metadata:
            _logger.error(f"Failed to process file metadata: {invalid_metadata}")
            raise ValidationError(
                _("\nAn internal issue ocurred while processing metadata. Please, try a different file.")
            )

        except MetadataPersistenceError as not_allowed:
            _logger.error(f"Failed to save metadata into file: {not_allowed}")
            raise ValidationError(
                _("\nUnable to write metadata. Please check your permissions or ensure there is enough disk space.")
            )

        except MusicManagerError as unknown_error:
            _logger.error(f"Unexpected error while processing metadata file: {unknown_error}")
            raise ValidationError(
                _("\nDamn! Something went wrong while processing metadata file.\nPlease, contact with your Admin.")
            )

    @staticmethod
    def _format_track_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        return f"{minutes:02}:{seconds:02}"
