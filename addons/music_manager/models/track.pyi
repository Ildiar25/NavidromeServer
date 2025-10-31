# -*- coding: utf-8 -*-
from collections.abc import Callable
from typing import Final, Iterable, Literal, Optional, Self, Sequence

from odoo.api import Environment

from .album import Album
from .artist import Artist
from .genre import Genre
from ..utils.custom_types import (
    CustomWarningMessage,
    DisplayNotification,
    DomainCustomFilter,
    MessageCounter,
    ReplaceItemCommand,
    TrackVals
)


class Track:
    """
    Represents a Track model into the system.
    Manage basic track data like cover, track no, album_id, file_path & others.
    """

    _name: Final[str]
    _description: str | None
    _order: str | None
    id: int
    env: Environment
    mapped: Callable[[str], Iterable[Self]]
    ensure_one: Callable[[], Self]
    search: Callable[..., Self]

    cover: bytes | None
    disk_no: int | None
    duration: str | None
    file_type: str | None
    name: str | None
    total_disk: int | None
    total_track: int | None
    track_no: int | None
    year: str
    album_artist_id: Optional[Artist]
    album_id: Optional[Album]
    genre_id: Optional[Genre]
    original_artist_id: Optional[Artist]
    track_artist_ids: Sequence[Artist]
    file: bytes | None
    tmp_album: str | None
    tmp_album_artist: str | None
    tmp_artists: str | None
    tmp_genre: str | None
    tmp_original_artist: str | None
    url: str | None
    collection: bool
    display_artist_names: str | None
    is_deleted: bool | None
    file_path: str | None
    old_path: str | None
    album_name: str | None
    has_valid_path: bool
    is_saved: bool
    state: Literal['start', 'uploaded', 'metadata', 'done', 'added']

    def create(self, list_vals: list[TrackVals]) -> Self:
        """Overrides 'create' method to process cover track & syncronizes with album & artist ids.
        :param list_vals: Dictionary list with track information to create new records.
        :return: Created track records.
        """

    def write(self, vals: TrackVals) -> Literal[True]:
        """Overrides 'write' method to update cover track & syncronizes with album & artist ids.
        :param vals: Dictionary with track values to update.
        :return: Confirms updated album record.
        """

    def unlink(self) -> Self:
        """Overrides the 'unlink' method to delete all linked albums and genres that no longer have
        associated tracks. It also deletes the track's file path before the record itself is deleted.
        The MP3 file is also removed if the user has the necessary permissions.
        :return: Deleted records.
        """

    def _compute_display_artist_name(self: Iterable[Self]) -> None:
        """Calculates artist names separated by commas.
        :return: None
        """

    def _compute_file_is_deleted(self: Iterable[Self]) -> None:
        """Determines if the file no longer exists.
        :return: None
        """

    def _compute_file_path(self: Iterable[Self]) -> None:
        """Calculates file path according to artist name, album title, track number & track name.
        :return: None
        """

    def _compute_collection_value(self: Iterable[Self]) -> None:
        """Toggles `collection` field according to artist name.
        :return: None
        """

    def _inverse_collection_value(self: Iterable[Self]) -> None:
        """Sets artist name as 'various artists' if `collection` field is True.
        :return: None
        """

    def _search_is_deleted(self: Iterable[Self], operator: str, value: bool) -> DomainCustomFilter:
        """This method returns a record list according to the given filter.
        :param operator: Representative string from different operators like '=' or '!='.
        :param value: Boolean value
        :return: List with diferent records according to filter.
        """

    def _check_fields(self: Iterable[Self]) -> None:
        """Checks if there is at least one of both fields (`file` or `url`) before proceed.
        :return: None
        """

    def _check_track_name(self) -> None:
        """Checks track title & track artist to avoid duplicates.
        :return: None
        """

    def _validate_file_path(self: Iterable[Self]) -> None:
        """Toggles `has_valid_path` field according to a given pattern.
        :return: None
        """

    def _validate_file_type(self: Iterable[Self]) -> CustomWarningMessage | None:
        """Checks if file has a valid format. If file is not MP3 format, clears the field `file`
        and returns a warning message.
        :return: Warning Message (dict) | None
        """

    def _validate_url_path(self: Iterable[Self]) -> CustomWarningMessage | None:
        """Checks if url path has a valid pattern. If URL pattern does not belong to YouTube,
        clears the field `url_path` and returns a warning message.
        :return: Warning Message (dict) | None
        """

    def _validate_cover_image(self: Iterable[Self]) -> CustomWarningMessage | None:
        """Checks cover image format. If image is WEBP format, clears the field `cover` and returns a warning message.
        :return: Warning Message (dict) | None
        """

    def _display_album_artist_changes(self: Iterable[Self]) -> None:
        """Updates album artist name visuals.
        :return: None
        """

    def action_back(self) -> None:
        """Changes work flow steps (`state` field) to backward when the user click on the back button.
        :return: None
        """

    def action_next(self) -> None:
        """Changes work flow steps (`state` field) to forward when the user click on the next button.
        :return: None
        """

    def save_changes(self) -> DisplayNotification:
        """Updates track metadata & path file.
        :return: Dictionary with notification data
        """

    def save_file(self) -> None:
        """Saves file into necessary folders & updates metadata track.
        :return: None
        """

    def _convert_to_mp3(self: Iterable[Self]) -> None:
        """Downloads & converts a YouTube video to MP3 format.
        :return: None
        """

    def _find_or_create_album(self, album_name: str) -> int | bool:
        """Tries to find a given album name. If there is not any, creates new record.
        :param album_name: Album name
        :return: Album ID (created or finded) | False if there is not any name
        """

    def _find_or_create_artist(self, artist_names: str) -> list[ReplaceItemCommand]:
        """Tries to find a given artist names. If there is not any, creates new record.
        :param artist_names: Artist names (individual or names separated by commas)
        :return: Artist IDs (created or finded) | False if there is not any name
        """

    def _find_or_create_genre(self, genre_name: str) -> int | bool:
        """Tries to find a given genre name. If there is not any, creates new record.
        :param genre_name: Genre name
        :return: Genre ID (created or finded) | False if there is not any name
        """

    def _find_or_create_single_artist(self, artist_name: str, fallback_ids: list[int]) -> int | bool:
        """Tries to find a given single artist name. If there is not any, sets the first one finded on fall back list.
        :param artist_name: Artist name
        :param fallback_ids: A list with various artist IDs
        :return: Artist ID (created or finded) | False if there is not any name
        """

    def _perform_save_changes(self: Iterable[Self]) -> MessageCounter:
        """Create a custom dictionary to count failures while tracks are updating.
        :return: Custom dictonary
        """

    def _sync_album_with_artist(self) -> None:
        """Syncronizes album ID with artist ID.
        :return: None
        """

    def _sync_album_with_genre(self) -> None:
        """Syncronizes album ID with genre ID.
        :return: None
        """

    def _update_fields(self) -> None:
        """Updates form fields according to track metadata.
        :return: None
        """

    def _update_metadata(self: Iterable[Self], path: str) -> None:
        """Updates track metadata according to field values.
        :param path:
        :return: None
        """

    @staticmethod
    def _format_track_duration(duration: int) -> str:
        """Gives a format to track duration.
        :param duration: Total seconds
        :return: An string with MM:SS format
        """

    @staticmethod
    def _process_cover_image(value: TrackVals) -> None:
        """Process & normalize cover image before create or update records. It converts the image into PNG format,
        center it & scale it to 350x350 px. An error is raised if image has an invalid format.
        :param value: Dictionary with track values, 'cover' field could be included.
        :return: None
        """