import logging
from abc import ABC, abstractmethod
from pathlib import Path

import mutagen.mp3 as exception
from mutagen.mp3 import MP3

from ..utils.track_data import TrackInfo
from ..utils.exceptions import InvalidFileFormatError, MusicManagerError


_logger = logging.getLogger(__name__)


class AudioInfoService(ABC):

    @abstractmethod
    def get_track_info(self, file_path: Path) -> TrackInfo:
        ...


class MP3AudioInfoService(AudioInfoService):

    def get_track_info(self, file_path: Path) -> TrackInfo:
        track = self._load_mp3_audio(file_path)

        return TrackInfo(
            duration=round(track.info.length),
            bitrate=track.info.bitrate,
            sample_rate=track.info.sample_rate,
            channels=track.info.channels,
            mode=track.info.mode,
            codec=track.info.codec,
            version=track.info.version,
            layer=track.info.layer,
            total_frames=track.info.total_frames,
            constant_bitrate=track.info.constant_bitrate,
        )

    @staticmethod
    def _load_mp3_audio(track_file: Path) -> MP3:
        try:
            return MP3(track_file)

        except exception.HeaderNotFoundError as corrupt_file:
            _logger.error(f"There was a problem with the file: {corrupt_file}")
            raise InvalidFileFormatError(corrupt_file)

        except Exception as unknown_error:
            _logger.error(f"Something went wrong while analyzing file info: {unknown_error}")
            raise MusicManagerError(unknown_error)
