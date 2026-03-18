# -*- coding: utf-8 -*-
from collections.abc import Callable, Sequence
from typing import Final, Literal, Self

from odoo.addons.base.models.res_users import Users
from odoo.api import Environment

from .album import Album
from .artist import Artist
from .genre import Genre
from ..adapters import FileServiceAdapter, TrackServiceAdapter
from ..utils.custom_types import CustomWarningMessage, DisplayNotification, DomainCustomFilter, MessageCounter, YearValue, TrackVals


class Track:
    """
    Represents a Track model into the system.
    Manage basic track data like cover, track no, album_id, file_path & others.
    """

    _name: Final[str]
    _description: str | None
    _order: str | None
    _sql_constraints: list[tuple[str, str, str]] | None

    # Base model fields necessaries for context
    id: int
    env: Environment
    ensure_one: Callable[[], Self]

    # Custom fields
    picture: bytes | Literal[False]
    disk_no: int | Literal[False]
    name: str
    total_disk: int | Literal[False]
    total_track: int | Literal[False]
    track_no: int
    year: YearValue | Literal[False]
    bitrate: int
    channels: str
    codec: str
    duration: int
    mime_type: str
    sample_rate: int
    album_artist_id: Artist | int | Literal[False]
    album_id: Album | int | Literal[False]
    genre_id: Genre | int | Literal[False]
    original_artist_id: Artist | int | Literal[False]
    track_artist_ids: Sequence[Artist] | Sequence[int]
    compilation: bool
    display_artist_names: str | Literal[False]
    display_bitrate: str | Literal[False]
    display_duration: str | Literal[False]
    display_sample_rate: str | Literal[False]
    is_deleted: bool | Literal[False]
    file_path: str | Literal[False]
    old_path: str | Literal[False]
    album_name: str | Literal[False]
    album_artist: str | Literal[False]
    has_valid_path: bool
    is_saved: bool
    custom_owner_id: Users | int

    def create(self, list_vals: list[TrackVals]) -> Self:
        """Overrides 'create' method to process cover track & syncronizes with album & artist ids.
        :param list_vals: Dictionary list with track information to create new records.
        :return: Created track records.
        """

    def write(self: Self, vals: TrackVals) -> Literal[True]:
        """Overrides 'write' method to update cover track & syncronizes with album & artist ids.
        :param vals: Dictionary with track values to update.
        :return: Confirms updated album record.
        """

    def unlink(self: Self) -> Literal[True]:
        """Overrides the 'unlink' method to delete all linked albums and genres that no longer have
        associated tracks. It also deletes the track's file path before the record itself is deleted.
        The MP3 file is also removed if the user has the necessary permissions.
        :return: Deleted records.
        """

    def _compute_display_artist_name(self: Self) -> None:
        """Calculates artist names separated by commas.
        :return: None
        """

    def _compute_display_bitrate(self: Self) -> None:
        """Calculates bitrate in kbps.
        :return: None
        """

    def _compute_display_duration(self: Self) -> None:
        """Calculates duration in minutes.
        :return: None
        """

    def _compute_display_sample_rate(self: Self) -> None:
        """Calculates sample rate in kHz.
        :return: None
        """

    def _compute_file_is_deleted(self: Self) -> None:
        """Determines if the file no longer exists.
        :return: None
        """

    def _compute_file_path(self: Self) -> None:
        """Calculates file path according to artist name, album title, disk number, track number & track name.
        :return: None
        """

    def _compute_compilation_value(self: Self) -> None:
        """Toggles `collection` field according to album artist name.
        :return: None
        """

    def _inverse_compilation_value(self: Self) -> None:
        """Sets artist name as 'various artists' if `collection` field is True.
        :return: None
        """

    def _search_is_deleted(self: Self, operator: str, value: bool) -> DomainCustomFilter:
        """This method returns a record list according to the given filter.
        :param operator: Representative string from different operators like '=' or '!='.
        :param value: Boolean value
        :return: List with diferent records according to filter.
        """

    def _check_track_name(self: Self) -> None:
        """Checks track title, album name & track artist to avoid duplicates.
        :return: None
        """

    def _validate_file_path(self: Self) -> None:
        """Toggles `has_valid_path` field according to a given pattern.
        :return: None
        """

    def _display_album_artist_changes(self: Self) -> None:
        """Updates album artist name visuals.
        :return: None
        """

    def save_changes(self: Self) -> DisplayNotification:
        """Updates track metadata & path file.
        :return: Dictionary with notification data
        """

    def _find_or_create_single_artist(self: Self, artist_name: str, fallback_artists: Sequence[Artist]) -> Artist | Literal[False]:
        """Tries to find a given single artist name. If there is not any, sets the first one finded on fall back list.
        :param artist_name: Artist name
        :param fallback_artists: A list with various Artists
        :return: Artist (created or finded) | False if there is not any name
        """

    def _get_file_service_adapter(self: Self) -> FileServiceAdapter:
        """Ensure file adapter has its settings updated
        :return: FileServiceAdapter with updated settings
        """

    def _get_track_service_adapter(self: Self) -> TrackServiceAdapter:
        """Ensure track service adapter has its settings updated
        :return: TrackServiceAdapter with updated settings
        """

    def _ensure_optional_fields(self: Self) -> None:
        """Check if all metadata fields are filled
        :return: None
        """

    def _perform_save_changes(self: Self) -> MessageCounter | None:
        """Create a custom dictionary to count failures while tracks are updating.
        :return: Custom dictonary
        """

    def _sync_album_with_artist(self: Self) -> None:
        """Syncronizes album ID with artist ID.
        :return: None
        """

    def _sync_album_with_genre(self: Self) -> None:
        """Syncronizes album ID with genre ID.
        :return: None
        """

    def _sync_album_with_owner(self: Self) -> None:
        """Syncronizes album owner ID with owner ID if album exists else creates a new one.
        :return: None
        """

    def _update_metadata(self: Self) -> None:
        """Send metadata to track service
        :return: None
        """

    def file_exists(self: Self) -> bool:
        """Checks if the file exists.
        :return: Boolean
        """

    def _get_years_list(self: Self) -> list[YearValue]:
        """Calls 'get_years_list' method from file_utils.py to get a years list.
        :return: Complete years list
        """

    def _validate_picture_image(self: Self) -> CustomWarningMessage | None:
        """MIXIN: See process_image_mixin documentation.
        """

    def _process_picture_image(self, vals: TrackVals) -> None:
        """MIXIN: See process_image_mixin documentation.
        :param vals: Dictionary with vals to write
        :return: None
        """
