import logging
from pathlib import Path

# noinspection PyProtectedMember
from odoo import _
from odoo.exceptions import ValidationError

from ..services.metadata_service import FileMetadata, MP3File
from ..utils.data_encoding import base64_decode, base64_encode
from ..utils.enums import FileType
from ..utils.exceptions import (
    InvalidFileFormatError,
    InvalidPathError,
    MetadataServiceError,
    MetadataPersistenceError,
    MusicManagerError,
    ReadingFileError
)


_logger = logging.getLogger(__name__)


class MetadataServiceAdapter:

    METADATA_SERVICES = {
        FileType.MP3, MP3File,
    }

    def __init__(self, file_type: str = 'mp3') -> None:
        self.file_type = self._check_file_extension(file_type)

        # TODO: Crear un mapeo de servicio en este método
        self._service = self._get_metadata_service()

    def read_metadata(self, track: bytes) -> dict[str, str | int | None]:
        try:
            metadata = self._service.get_metadata(track)

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
                'picture': base64_encode(metadata.APIC) if metadata.APIC else None,
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

    def write_metadata(self, str_file_path: str | None, track: dict[str, str | int | None]) -> None:
        if not isinstance(str_file_path, str):
            _logger.error(f"Cannot save metadata. The path is not valid: '{str_file_path}'.")
            raise InvalidPathError("File path does not exist. A valid path must be set before saving.")

        output_path = Path(str_file_path).with_suffix(f'.{self.file_type.value}')

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
            'APIC': base64_decode(track['APIC']) if track['APIC'] else None,
        }

        try:
            self._service.set_metadata(output_path, metadata)

        except ReadingFileError as invalid_metadata:
            _logger.error(f"Failed to process file metadata: {invalid_metadata}")
            raise ValidationError(
                _("\nAn internal issue ocurred while processing metadata. Please, try a different file.")
            )

        except InvalidPathError as invalid_path:
            _logger.error(f"There was an issue with file path: {invalid_path}")
            raise ValidationError(_("\nActually, the file path of this record is not valid."))

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

    def _get_metadata_service(self) -> FileMetadata:

        # NOTE: No utilizar match, utilizar un mapeo para facilitar la búsqueda de servicios a futuro.
        match self.file_type:
            case FileType.MP3:
                return MP3File()

            case _:
                raise MetadataServiceError("Unsupported metadata file type")

    @staticmethod
    def _check_file_extension(extension: str) -> FileType:
        if extension not in (file.value for file in FileType):
            _logger.error(f"Cannot find the file extension: '{extension}'.")
            raise InvalidFileFormatError(f"The file extension '{extension}' is not valid.")

        return FileType(extension)

    @staticmethod
    def _format_track_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        return f"{minutes:02}:{seconds:02}"
