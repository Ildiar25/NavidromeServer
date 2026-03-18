# -*- coding: utf-8 -*-
from collections.abc import Callable, Sequence
from typing import Dict, Final, Literal, Self

from addons.music_manager.adapters import DownloadServiceAdapter, FileServiceAdapter, TrackServiceAdapter
from odoo.api import Environment

from addons.music_manager.models import Album, Artist, Genre
from addons.music_manager.utils.custom_types import YearValue, CustomWarningMessage, WindowActionView, TrackVals


class TrackWizard:
    """
    Represents a Track Wizard model into the system.
    Manage basic temporal data found in the given track like cover, track no, album_id, file_path & others.
    """

    _name: Final[str]
    _description: str | None

    # Base model fields necessaries for context
    id: int
    env: Environment
    ensure_one: Callable[[], Self]

    # Custom fields
    file: bytes | Literal[False]
    picture: bytes | Literal[False]
    tmp_album: str | Literal[False]
    tmp_album_artist: str | Literal[False]
    tmp_artists: str | Literal[False]
    tmp_disk_no: int | Literal[False]
    tmp_genre: str | Literal[False]
    tmp_name: str | Literal[False]
    tmp_original_artist: str | Literal[False]
    tmp_track_no: int | Literal[False]
    tmp_total_disk: int | Literal[False]
    tmp_total_track: int | Literal[False]
    tmp_year: str | Literal[False]
    year: YearValue | Literal[False]
    url: str | Literal[False]
    bitrate: int
    channels: str
    codec: str
    duration: int
    mime_type: str
    sample_rate: int
    possible_album_id: Album | int | Literal[False]
    possible_album_artist_id: Artist | int | Literal[False]
    possible_artist_ids: Sequence[Artist] | Sequence[int]
    possible_genre_id: Genre | int | Literal[False]
    possible_original_artist_id: Artist | int | Literal[False]
    file_path: str | Literal[False]
    has_valid_path: bool
    tmp_compilation: bool
    state: Literal['start', 'uploaded', 'metadata', 'done']

    def _compute_file_path(self: Self) -> None:
        """Calculates the file path where the track will be saved.
        :return: None
        """

    def _compute_has_valid_path(self: Self) -> None:
        """Calculates if the path has the mandatory fields like artist, album, disk number, track number and title.
        :return: None
        """

    def _check_fields(self: Self) -> None:
        """Force the user to give a url or upload a file. But just one of them.
        :return: None
        """

    def _compute_compilation_value(self: Self) -> None:
        """Calculates if a track belongs to a compilation or not according to album artist.
        :return: None
        """

    def _compute_inverse_compilation_value(self: Self) -> None:
        """Sets artist name as 'various artists' if `collection` field is True or set
        'album artist' as 'original artist'.
        :return: None
        """

    def _validate_file_type(self: Self) -> CustomWarningMessage | None:
        """Validates file type according to admited file formats.
        :return: Warning Message (dict) | None
        """

    def _validate_url_path(self: Self) -> CustomWarningMessage | None:
        """Validates given url according to YouTube url standar.
        :return: Warning Message (dict) | None
        """

    def action_back(self: Self) -> WindowActionView:
        """Allows User to move between wizard states.
        :return: Window view UI
        """

    def action_next(self: Self) -> WindowActionView:
        """Allows User to move between wizard states.
        :return: Window view UI
        """

    def match_all_metadata(self: Self) -> None:
        """Centralizes match comparison between found metadata & database.
        :return: None
        """

    def save_file(self: Self) -> WindowActionView | None:
        """Saves the uploaded file into the system & creates new record into the database.
        :return: Window view UI | None
        """

    def _download_file(self: Self) -> None:
        """Downloads file from a griven url & writes it to 'file' field.
        :return: None
        """

    def _create_new_track_record(self: Self) -> Dict[str, str | int] | None:
        """Prepares metadata to create new Track record into the database.
        :return: A dictionary with generic recordset values as ID & name | None
        """

    def _check_already_exists(self: Self) -> None:
        """Checks if the track already exists in the database.
        :return: None
        """

    def _ensure_optional_fields(self: Self) -> None:
        """Check if all metadata fields are filled
        :return: None
        """

    def _find_or_create_single_artist(self: Self, artist_name: str, fallback_artists: Sequence[Artist]) -> Artist | Literal[False]:
        """Tries to find a given single artist name. If there is not any, sets the first one finded on fall back list.
        :param artist_name: Artist name
        :param fallback_artists: A list with various Artists
        :return: Artist (created or finded) | False if there is not any name
        """

    def _get_download_service_adapter(self: Self, video_url: str) -> DownloadServiceAdapter:
        """Ensure download adapter has its settings updated.
        :return: DownloadServiceAdapter with updated settings
        """

    def _get_file_service_adapter(self: Self) -> FileServiceAdapter:
        """Ensure file adapter has its settings updated
        :return: FileServiceAdapter with updated settings
        """

    def _get_track_service_adapter(self: Self) -> TrackServiceAdapter:
        """Ensure track service adapter has its settings updated
        :return: TrackServiceAdapter with updated settings
        """

    def _match_album_id(self: Self) -> None:
        """Matches album ID with given temporary album name.
        :return: None
        """

    def _match_album_artist_id(self: Self) -> None:
        """Matches album artist ID with given temporary album artist name.
        :return: None
        """

    def _match_artist_ids(self: Self) -> None:
        """Matches all track artists IDs with given temporary track artist names separated with commas.
        :return: None
        """

    def _match_genre_id(self: Self) -> None:
        """Matches genre ID with given temporary genre name.
        :return: None
        """

    def _match_original_artist_id(self: Self) -> None:
        """Matches original artist ID with given temporary original artist name.
        :return: None
        """

    def _match_track_year(self: Self) -> None:
        """Matches year according to years' list.
        :return: None
        """

    def _update_fields(self: Self) -> None:
        """Updates all fields according to track metadata.
        :return:
        """

    def _reset_fields(self: Self) -> None:
        """Resets all fields to an empty state.
        :return: None
        """

    def _get_years_list(self: Self) -> None:
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
