import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import mutagen.id3 as tag_type
import mutagen.mp3 as exception
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from ..utils.track_data import FullTrackData, TrackInfo, TrackMetadata
from ..utils.exceptions import InvalidFileFormatError, MetadataPersistenceError, MusicManagerError, ReadingFileError


_logger = logging.getLogger(__name__)


class AudioFileService(ABC):

    @abstractmethod
    def get_full_data(self, buffered_file: io.BytesIO) -> FullTrackData:
        ...

    @abstractmethod
    def set_track_metadata(self, output_path: Path, new_data: Dict[str, str | int | None]) -> None:
        ...


class MP3AudioFileService(AudioFileService):

    MIME_TYPE = "audio/mpeg"

    ID3_TAG_MAPPING = {
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

    def get_full_data(self, buffered_file: io.BytesIO) -> FullTrackData:

        track = self._open_mp3_file(buffered_file)
        metadata = self._extract_metadata(track)

        info = TrackInfo(
            bitrate=track.info.bitrate // 1000,
            channels=track.info.channels,
            codec="MP3",
            duration=round(track.info.length),
            mime_type=self.MIME_TYPE,
            sample_rate=track.info.sample_rate,
        )

        return FullTrackData(info=info, metadata=metadata)

    def set_track_metadata(
            self, output_path: Path, new_metadata: Dict[str, str | int | None], preserve_unknown_tags: bool = False
    ) -> None:
        tag_writers = {
            'APIC': self._write_apic_image,
            'TRCK': self._write_numeric_pair,
            'TPOS': self._write_numeric_pair,
            'TCMP': self._write_is_compilation,
        }

        track = self._open_mp3_file(output_path)

        if not preserve_unknown_tags:  # If in a future we want to save unknown metadata
            self._normalize_metadata(track)

        new_data = TrackMetadata(**new_metadata)

        for name, tag in self.ID3_TAG_MAPPING.items():
            value = getattr(new_data, name)

            if value is None:
                continue

            writer = tag_writers.get(name, self._write_text)
            writer(track, tag, value)

        self._save(track)

    def _extract_metadata(self, track: MP3) -> TrackMetadata:
        tag_parsers = {
            'APIC': self._parse_apic_image,
            'TDRC': self._parse_datetime,
            'TRCK': self._parse_numeric_pair,
            'TPOS': self._parse_numeric_pair,
            'TCMP': self._parse_is_compilation,
        }

        if not track.tags:
            return TrackMetadata()

        metadata = {}

        for key, value in track.tags.items():
            base_key = key[:4]

            if base_key not in TrackMetadata.__annotations__:
                continue

            parser = tag_parsers.get(base_key, self._parse_text)
            parsed_value = parser(value)

            if parsed_value:
                metadata[base_key] = parsed_value

        return TrackMetadata(**metadata)

    def _parse_numeric_pair(self, value: Any) -> tuple[int, int]:
        text: str = value.text[0]
        if "/" in text:
            return self._parse_track_string(text)

        else:
            return int(text) if text.isdigit() else 1, 1

    def _write_numeric_pair(self, track: MP3, tag: Any, value: tuple[int, int]) -> None:
        text = self._format_track_tuple(value)
        track.tags.add(tag(encoding=3, text=text))

    @staticmethod
    def _format_track_tuple(track_tuple: tuple[int, int]) -> str:
        str_tuple = map(str, track_tuple)
        data = "/".join(str_tuple)
        return data

    @staticmethod
    def _parse_apic_image(value: Any) -> bytes | None:
        return value.data if value.type == 3 else None

    @staticmethod
    def _parse_datetime(value: Any) -> str:
        return value.text[0] if getattr(value, "text", None) else None

    @staticmethod
    def _parse_is_compilation(value: Any) -> bool:
        return value.text[0] == "1"

    @staticmethod
    def _parse_text(value: Any) -> str:
        return ", ".join(value.text) if getattr(value, "text", None) else ""

    @staticmethod
    def _parse_track_string(data: str) -> tuple[int, int]:
        track, total_track = data.split("/")
        return int(track), int(total_track)

    def _normalize_metadata(self, track: MP3) -> None:
        if track.tags:
            track.tags.clear()

        else:
            track.add_tags()

        self._save(track)

    @staticmethod
    def _open_mp3_file(track_file: Path | io.BytesIO) -> MP3:
        try:
            return MP3(track_file, ID3=ID3)

        except tag_type.ID3NoHeaderError as no_tags:
            _logger.warning(f"No tags founded in this file: {no_tags}. Adding new tags...")
            mp3_audio = MP3(track_file)
            mp3_audio.add_tags()
            return mp3_audio

        except exception.HeaderNotFoundError as corrupt_file:
            _logger.error(f"There was a problem with the file: {corrupt_file}")
            raise InvalidFileFormatError(corrupt_file)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while analyzing file metadata: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def _save(track: MP3) -> None:
        try:
            track.save()

        except (PermissionError, OSError) as not_allowed:
            _logger.error(f"Cannot save metadata to file: {not_allowed}")
            raise MetadataPersistenceError(not_allowed)

        except Exception as unknown_error:
            _logger.error(f"Unexpected error during metadata writing: {unknown_error}")
            raise MusicManagerError(unknown_error)

    @staticmethod
    def _write_apic_image(track: MP3, tag: Any, value: bytes) -> None:
        track.tags.add(
            tag(
                encoding=3,

                # INFO: Actualmene solo se admite PNG pero si en el futuro se quiere cambiar el formato se debe actualizar
                mime='image/png',
                type=3,
                data=value
            )
        )

    @staticmethod
    def _write_is_compilation(track: MP3, tag: Any, value: bool) -> None:
        track.tags.add(tag(encoding=3, text="1" if value else "0"))

    @staticmethod
    def _write_text(track: MP3, tag: Any, value: str) -> None:
        track.tags.add(tag(encoding=3, text=value))
