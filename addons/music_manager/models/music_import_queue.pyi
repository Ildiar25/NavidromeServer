from collections.abc import Sequence
from typing import Dict, Final, Literal, Self

from .album import Album
from .artist import Artist
from .genre import Genre


class MusicImportQueue:
    """
    Represents a MusicImportQueue model into the system.
    Manage basic track data import and link or create metadata found to the system records.
    """

    _name: Final[str]
    _description: str | None

    # Custom fields
    error_message: str | Literal[False]
    file_path: str | Literal[False]
    state: Literal['pending', 'processed', 'error'] | Literal[False]

    def create_track_from_scan(self: Self, file_path: str, data: Dict[str, str | bytes | int | bool | None]) -> None:
        """Creates new record automatically according to metadata found in file_path.
        :param file_path: Actual file path found when main folder was scanned
        :param data: Data dictionary according to metadata found
        :return: None
        """

    def _cron_garbage_collector(self: Self) -> None:
        """Delete records which write date is over than 24h.
        :return: None
        """

    def _cron_process_music_queue(self: Self) -> None:
        """Each 2 minutes create 50 new records into the system.
        :return: None
        """

    def _match_album_id(self: Self, album_name: str, album_artist: Artist) -> Album:
        """Matches album ID with given temporary album name & artist ID.
        :param album_name: Album name found in metadata
        :param album_artist: Artist object to interact with
        :return: An album object
        """

    def _match_artist_id(self: Self, artist_name: str) -> Artist:
        """Matches album artist ID with given temporary album artist name.
        :param artist_name: Artist name found in metadata
        :return: An artist object
        """

    def _match_genre_id(self: Self, genre_name: str) -> Genre:
        """Matches genre ID with given temporary genre name.
        :param genre_name: Genre name found in metadata
        :return: A genre object
        """

    def _match_various_artists_ids(self: Self, artist_names: str) -> Sequence[Artist]:
        """Matches all track artists IDs with given temporary track artist names separated with commas.
        :param artist_names: Artist names found in metadata separated with commas.
        :return: A sequence of artists objects
        """

    def _notify_user(self: Self, error_count: int = 0) -> None:
        """Sends a UI notification. Reports the user if there are encountered errors or a successful importation.
        :param error_count: Error amount
        :return: None
        """

    def _match_track_year(self: Self, year: str) -> str:
        """Matches the year found in metadata according to years' list.
        :return: Year in string format as "YYYY" | Empty string if no year found
        """
