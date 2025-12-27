# -*- coding: utf-8 -*-
from collections.abc import Iterable, Sequence
from typing import Any, Dict, Final, List, Optional, Self

from odoo.addons.base.models.res_users import Users

from .album import Album
from .artist import Artist
from .genre import Genre
from ..utils.custom_types import CustomWarningMessage


class Track:
    """
    Represents a Track model into the system.
    Manage basic track data like cover, track no, album_id, file_path & others.
    """

    _name: Final[str]
    _description: str | None
    _order: str | None
    id: int

    picture: str | None
    disk_no: int | None
    duration: str | None
    mime_type: str | None
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

    collection: bool
    display_artist_names: str | None
    is_deleted: bool | None
    file_path: str | None
    old_path: str | None

    album_name: str | None

    has_valid_path: bool

    is_saved: bool
    owner: Users

    def create(self, list_vals: List[Dict[str, Any]]) -> Self:
        """Overrides 'create' method to process cover track & syncronizes with album & artist ids.
        :param list_vals: Dictionary list with track information to create new records.
        :return: Created track records.
        """

    # def write(self, vals: Dict[str, Any]):
    #     """Overrides 'write' method to update cover track & syncronizes with album & artist ids.
    #     :param vals: Dictionary with track values to update.
    #     :return: Confirms updated album record.
    #     """

    # def unlink(self) -> Self:
    #     """Overrides the 'unlink' method to delete all linked albums and genres that no longer have
    #     associated tracks. It also deletes the track's file path before the record itself is deleted.
    #     The MP3 file is also removed if the user has the necessary permissions.
    #     :return: Deleted records.
    #     """

    def _compute_display_artist_name(self: Iterable[Self]) -> None:
        """Calculates artist names separated by commas.
        :return: None
        """

    def _compute_file_is_deleted(self: Iterable[Self]) -> None:
        """Determines if the file no longer exists.
        :return: None
        """

    # def _compute_file_path(self: Iterable[Self]) -> None:
    #     """Calculates file path according to artist name, album title, track number & track name.
    #     :return: None
    #     """

    def _compute_collection_value(self: Iterable[Self]) -> None:
        """Toggles `collection` field according to artist name.
        :return: None
        """

    def _inverse_collection_value(self: Iterable[Self]) -> None:
        """Sets artist name as 'various artists' if `collection` field is True.
        :return: None
        """

    # def _search_is_deleted(self: Iterable[Self], operator: str, value: bool) -> DomainCustomFilter:
    #     """This method returns a record list according to the given filter.
    #     :param operator: Representative string from different operators like '=' or '!='.
    #     :param value: Boolean value
    #     :return: List with diferent records according to filter.
    #     """

    # def _check_track_name(self) -> None:
    #     """Checks track title & track artist to avoid duplicates.
    #     :return: None
    #     """

    # def _validate_file_path(self: Iterable[Self]) -> None:
    #     """Toggles `has_valid_path` field according to a given pattern.
    #     :return: None
    #     """

    def _display_album_artist_changes(self: Iterable[Self]) -> None:
        """Updates album artist name visuals.
        :return: None
        """

    # def save_changes(self) -> DisplayNotification:
    #     """Updates track metadata & path file.
    #     :return: Dictionary with notification data
    #     """

    # def _find_or_create_single_artist(self, artist_name: str, fallback_ids: list[int]) -> int | bool:
    #     """Tries to find a given single artist name. If there is not any, sets the first one finded on fall back list.
    #     :param artist_name: Artist name
    #     :param fallback_ids: A list with various artist IDs
    #     :return: Artist ID (created or finded) | False if there is not any name
    #     """

    # def _get_file_service_adapter(self) -> FileServiceAdapter:
    #     """Ensure file adapter has settings updated
    #     :return: FileServiceAdapter
    #     """

    # def _perform_save_changes(self: Iterable[Self]) -> MessageCounter:
    #     """Create a custom dictionary to count failures while tracks are updating.
    #     :return: Custom dictonary
    #     """

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


    def _validate_picture_image(self: Iterable[Self]) -> CustomWarningMessage | None:
        """MIXIN: See process_image_mixin documentation.
        """

    def _process_picture_image(self, vals: Dict[str, Any]) -> None:
        """MIXIN: See process_image_mixin documentation.
        :param vals: Dictionary with vals to write
        :return: None
        """
