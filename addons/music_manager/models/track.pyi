# -*- coding: utf-8 -*-
from collections.abc import Callable
from typing import Final, Iterable, Literal, Optional, Self, Sequence

from odoo.api import Environment
from odoo.addons.base.models.res_users import Users

from .album import Album
from .artist import Artist
from .genre import Genre
from ..utils.custom_types import CustomMessage, ReplaceItemCommand, TrackVals


class Track:
    """

    """

    _name: Final[str]
    _description: str | None
    _order: str | None
    id: int
    env: Environment
    mapped: Callable[[str], Iterable[Self]]
    ensure_one: Callable[[], Self]

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
    user_id: Users

    def create(self, list_vals: list[TrackVals]) -> Self:
        """
        :param list_vals:
        :return:
        """

    def write(self, vals: TrackVals) -> bool:
        """
        :param vals:
        :return:
        """

    def unlink(self) -> Self:
        """
        :return:
        """

    def _compute_display_artist_name(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _compute_file_is_deleted(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _compute_file_path(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _compute_collection_value(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _inverse_collection_value(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _check_fields(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _validate_file_path(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _validate_file_type(self: Iterable[Self]) -> CustomMessage | None:
        """
        :return:
        """

    def _validate_url_path(self: Iterable[Self]) -> CustomMessage | None:
        """
        :return:
        """

    def _validate_cover_image(self: Iterable[Self]) -> CustomMessage | None:
        """
        :return:
        """

    def _display_album_artist_changes(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def action_back(self) -> None:
        """
        :return: None
        """

    def action_next(self) -> None:
        """
        :return: None
        """

    def save_changes(self) -> None:
        """
        :return: None
        """

    def save_file(self) -> None:
        """
        :return: None
        """

    def _convert_to_mp3(self: Iterable[Self]) -> None:
        """
        :return: None
        """

    def _find_or_create_album(self, album_name: str) -> int | bool:
        """
        :param album_name:
        :return:
        """

    def _find_or_create_artist(self, artist_names: str) -> list[ReplaceItemCommand]:
        """
        :param artist_names:
        :return:
        """

    def _find_or_create_genre(self, genre_name: str) -> int | bool:
        """
        :param genre_name:
        :return:
        """

    def _find_or_create_single_artist(self, artist_name: str, fallback_ids: list[int]) -> int | bool:
        """
        :param artist_name:
        :param fallback_ids:
        :return:
        """

    def _sync_album_with_artist(self) -> None:
        """
        :return: None
        """

    def _sync_album_with_genre(self) -> None:
        """
        :return: None
        """

    def _update_fields(self) -> None:
        """
        :return: None
        """

    def _update_metadata(self: Iterable[Self], path: str) -> None:
        """
        :param path:
        :return: None
        """

    @staticmethod
    def _format_track_duration(duration: int) -> str:
        """
        :param duration:
        :return:
        """

    @staticmethod
    def _process_cover_image(value: TrackVals) -> None:
        """
        :param value:
        :return: None
        """