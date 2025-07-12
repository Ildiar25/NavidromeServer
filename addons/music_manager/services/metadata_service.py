# -*- coding: utf-8 -*-
import io
import logging
from abc import ABC, abstractmethod

import mutagen.id3 as tag_type
from mutagen.mp3 import MP3
from mutagen.id3 import ID3


_logger = logging.getLogger(__name__)


class FileMetadata(ABC):

    @abstractmethod
    def get_metadata(self, file_path: str | io.BytesIO) -> None:
        ...

    @abstractmethod
    def set_metadata(self, file_path: str | io.BytesIO, new_data: dict) -> None:
        ...

    @abstractmethod
    def reset_metadata(self, file_path: str | io.BytesIO) -> None:
        ...


class MP3File(FileMetadata):

    def get_metadata(self, file_path: str | io.BytesIO) -> dict:
        file_metadata = {}
        try:
            track = MP3(file_path, ID3=ID3)

        except tag_type.ID3NoHeaderError as no_tags:
            _logger.error(f"No tags founded in this file: {no_tags}")

        except Exception as unknown:
            _logger.error(f"Something went wrong while analyzing file metadata: {unknown}")

        else:
            if track.tags:
                title = track.tags.get('TIT2')
                artist = track.tags.get('TPE1')
                album_artist = track.tags.get('TPE2')
                album = track.tags.get('TALB')
                track_info = track.tags.get('TRCK')
                year = track.tags.get('TDRC')
                genre = track.tags.get('TCON')

                track_data = self._get_track_data(track_info.text[0])

                file_metadata['title'] = title.text[0] if title else "N/A"
                file_metadata['artist'] = artist.text[0] if artist else "N/A"
                file_metadata['album_artist'] = album_artist.text[0] if album_artist else "N/A"
                file_metadata['album'] = album.text[0] if album else "N/A"
                file_metadata['track_no'] = track_data[0] if track_data else "1"
                file_metadata['disk_no'] = track_data[1] if track_data else "1"
                file_metadata['year'] = year.text[0] if year else "N/A"
                file_metadata['genre'] = genre.text[0] if genre else "N/A"

        return file_metadata

    def set_metadata(self, file_path: str | io.BytesIO, new_data: dict) -> None:
        try:
            track = MP3(file_path, ID3=ID3)

        except tag_type.ID3NoHeaderError as no_tags:
            _logger.error(f"No tags founded in this file: {no_tags}")

        except Exception as unknown:
            _logger.error(f"Something went wrong while analyzing file metadata: {unknown}")

        else:
            track.tags.add(tag_type.TIT2(encoding=3, text=[new_data.get('title', "N/A")]))
            track.tags.add(tag_type.TPE1(encoding=3, text=[new_data.get('artist', "N/A")]))
            track.tags.add(tag_type.TPE2(encoding=3, text=[new_data.get('album_artist', "N/A")]))
            track.tags.add(tag_type.TALB(encoding=3, text=[new_data.get('album', "N/A")]))
            track.tags.add(tag_type.TRCK(encoding=3, text=[
                self._set_track_data(new_data.get('track_no', ('1', '1')))
            ]))
            track.tags.add(tag_type.TDRC(encoding=3, text=[new_data.get('year', "N/A")]))
            track.tags.add(tag_type.TCON(encoding=3, text=[new_data.get('genre', "N/A")]))

            track.save()

    def reset_metadata(self, file_path: str | io.BytesIO) -> None:
        track = MP3(file_path)
        if track.tags:
            track.tags.clear()
        else:
            track.add_tags()
        track.save()

    @staticmethod
    def _get_track_data(data: str | None) -> tuple[str, str] | None:
        if data:
            track, disk = data.split("/")
            return track, disk

        return data

    @staticmethod
    def _set_track_data(track_data: tuple[str, str] | None) -> str | None:
        if track_data:
            data = "/".join(track_data)
            return data

        return track_data

