# -*- coding: utf-8 -*-
import io
import logging
from abc import ABC, abstractmethod

import mutagen.id3 as tag_type
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

from ..models.metadata import TrackMetadata
from ..utils.exceptions import InvalidMetadataServiceError, MusicManagerError


_logger = logging.getLogger(__name__)


class FileMetadata(ABC):

    @abstractmethod
    def get_metadata(self, file_path: str | io.BytesIO) -> None:
        ...

    @abstractmethod
    def set_metadata(self, file_path: str | io.BytesIO, new_data: TrackMetadata) -> None:
        ...

    @abstractmethod
    def reset_metadata(self, file_path: str | io.BytesIO) -> None:
        ...


class MP3File(FileMetadata):

    def get_metadata(self, file_path: str | io.BytesIO) -> TrackMetadata:

        track = self.__load_track(file_path)

        if track.tags:

            metadata = {}
            metadata_fields = TrackMetadata().__dict__.keys()

            for key, value in track.tags.items():
                if key in metadata_fields and hasattr(value, 'text'):
                    if key == 'TRCK' and '/' in value.text[0]:
                        trck, tpos = self.__parse_track_string(value.text[0])
                        metadata['TRCK'] = trck
                        metadata['TPOS'] = tpos
                    else:
                        metadata[key] = value.text[0]

            return TrackMetadata(**metadata)

        return TrackMetadata()

    def set_metadata(self, file_path: str | io.BytesIO, new_data: TrackMetadata) -> None:
        pass

    def reset_metadata(self, file_path: str | io.BytesIO) -> None:

        track = MP3(file_path)

        if track.tags:
            track.tags.clear()
        else:
            track.add_tags()

        track.save()

    @staticmethod
    def __load_track(file: str | io.BytesIO) -> MP3:
        try:
            return MP3(file, ID3=ID3)

        except tag_type.ID3NoHeaderError as no_tags:
            _logger.error(f"No tags founded in this file: {no_tags}")
            raise InvalidMetadataServiceError(no_tags)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while analyzing file metadata: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def __parse_track_string(data: str) -> tuple[str, str] | str:
        if "/" in data:
            track, disk = data.split("/")
            return track, disk

        return data

    @staticmethod
    def __format_track_tuple(track_tuple: tuple[str, str] | str) -> str:
        if isinstance(track_tuple, tuple):
            data = "/".join(track_tuple)
            return data

        return track_tuple

