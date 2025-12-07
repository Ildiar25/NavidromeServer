# -*- coding: utf-8 -*-
import base64
import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

# noinspection PyPackageRequirements
import magic
import mutagen.id3 as tag_type
import mutagen.mp3 as exception
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

from ..utils.exceptions import InvalidFileFormatError, MetadataPersistenceError, MusicManagerError, ReadingFileError
from ..utils.metadata_schema import TrackMetadata


_logger = logging.getLogger(__name__)


class FileMetadata(ABC):

    tag_mapping = {
        'TIT2': tag_type.TIT2,
        'TPE1': tag_type.TPE1,
        'TPE2': tag_type.TPE2,
        'TOPE': tag_type.TOPE,
        'TALB': tag_type.TALB,
        'TCMP': tag_type.TCMP,
        'TRCK': tag_type.TRCK,
        'TPOS': tag_type.TPOS,
        'TDRC': tag_type.TDRC,
        'TCON': tag_type.TCON,
        'APIC': tag_type.APIC,
    }

    @staticmethod
    def decode_bytes(encoded_bytes_file: bytes) -> io.BytesIO:
        if not isinstance(encoded_bytes_file, bytes):
            raise ReadingFileError(f"Invalid file type: {type(encoded_bytes_file)}")

        decoded_bytes = base64.b64decode(encoded_bytes_file)
        buffer = io.BytesIO(decoded_bytes)
        buffer.seek(0)
        return buffer

    @abstractmethod
    def get_metadata(self, encoded_bytes_file: bytes) -> TrackMetadata:
        ...

    @abstractmethod
    def set_metadata(self, output_path: Path, new_data: Dict[str, str | int | None]) -> None:
        ...


class MP3File(FileMetadata):

    def get_metadata(self, encoded_bytes_file: bytes) -> TrackMetadata:
        buffered_file = self.decode_bytes(encoded_bytes_file)
        track = self.__load_metadata_tags(buffered_file)

        if not track.tags:
            return TrackMetadata()

        metadata = {}
        metadata_fields = TrackMetadata().__dict__.keys()

        for key, value in track.tags.items():
            if key.startswith('APIC'):
                if value.type == 3:
                    metadata['APIC'] = value.data

            elif key in metadata_fields and hasattr(value, 'text'):
                if key == 'TRCK':
                    if '/' in value.text[0]:
                        trck_no, total = self.__parse_track_string(value.text[0])
                        metadata['TRCK'] = trck_no, total
                    else:
                        metadata['TRCK'] = int(value.text[0]) if value.text[0].isdigit() else 1, 1

                elif key == 'TPOS':
                    if '/' in value.text[0]:
                        dsk_no, total = self.__parse_track_string(value.text[0])
                        metadata['TPOS'] = dsk_no, total
                    else:
                        metadata['TPOS'] = int(value.text[0]) if value.text[0].isdigit() else 1, 1

                elif key == 'TCMP':
                    metadata['TCMP'] = value.text[0] == '1'

                else:
                    metadata[key] = value.text[0]

        track_data = TrackMetadata(**metadata)

        try:
            track_data.DUR = round(track.info.length)
            track_data.MIME = magic.from_buffer(buffered_file.getvalue(), mime=True)

        except Exception as unknown_error:
            _logger.warning(f"There was an issue while trying to read MIME type or track duration: {unknown_error}")

        return track_data

    def set_metadata(self, output_path: Path, new_metadata: Dict[str, str | int | None]) -> None:
        track = self.__load_metadata_tags(output_path)
        self.__reset_metadata(track)

        new_data = TrackMetadata(**new_metadata)

        for name, tag in self.tag_mapping.items():
            value = getattr(new_data, name)

            if name == 'TRCK' or name == 'TPOS':
                track.tags.add(tag(encoding=3, text=self.__format_track_tuple(value)))

            if name == 'TCMP':
                if value is True:
                    track.tags.add(tag(encoding=3, text='1'))
                else:
                    track.tags.add(tag(encoding=3, text='0'))

            elif name == 'APIC' and value is not None:
                track.tags.add(
                    tag(
                        encoding=3,
                        mime='image/png',
                        type=3,
                        data=value
                    )
                )

            elif isinstance(value, str):
                track.tags.add(tag(encoding=3, text=value))

        try:
            track.save()

        except (PermissionError, OSError) as not_allowed:
            _logger.error(f"Cannot save metadata to file: {not_allowed}")
            raise MetadataPersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error during metadata writing: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def __reset_metadata(track: MP3) -> None:
        if track.tags:
            track.tags.clear()

        else:
            track.add_tags()

        try:
            track.save()

        except (PermissionError, OSError) as not_allowed:
            _logger.error(f"Cannot save metadata to file: {not_allowed}")
            raise MetadataPersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error during metadata writing: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def __load_metadata_tags(track_file: Path | io.BytesIO) -> MP3:
        try:
            return MP3(track_file, ID3=ID3)

        except tag_type.ID3NoHeaderError as no_tags:
            _logger.warning(f"No tags founded in this file: {no_tags}")
            raise ReadingFileError(no_tags)

        except exception.HeaderNotFoundError as corrupt_file:
            _logger.error(f"There was a problem with the file: {corrupt_file}")
            raise InvalidFileFormatError(corrupt_file)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while analyzing file metadata: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def __parse_track_string(data: str) -> tuple[int, int]:
        track, total_track = data.split("/")
        return int(track), int(total_track)

    @staticmethod
    def __format_track_tuple(track_tuple: tuple[int, int]) -> str:
        str_tuple = map(str, track_tuple)
        data = "/".join(str_tuple)
        return data
