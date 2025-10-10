# -*- coding: utf-8 -*-
from typing import Final, Iterable, Optional, Self, Sequence, Literal

from odoo.addons.base.models.res_users import Users

from .artist import Artist
from .genre import Genre
from .track import Track
from ..utils.custom_types import AlbumVals, CustomWarningMessage, DisplayNotification


class Album:
    """
    Represents an Album model into the system.
    Manage basic album data like cover, year, genre, artist & tracks.
    """

    _name: Final[str]
    _description: str | None
    _order: str | None
    _sql_constraints: list[tuple[str, str, str]] | None
    id: int

    name: str
    is_favorite: bool
    album_artist_id: Optional[Artist]
    genre_id: Optional[Genre]
    track_ids: Sequence[Track]
    cover: bytes | None
    disk_amount: int
    track_amount: int
    year: str | None
    user_id: Users

    def create(self, list_vals: list[AlbumVals]) -> Self:
        """Overrides 'create' method to process cover album & propagate to linked tracks, genre or artist records.
        :param list_vals: Dictionary list with album information to create new records.
        :return: Created album records.
        """

    def write(self, vals: AlbumVals) -> Literal[True]:
        """Overrides 'write' method to update cover album & propagate to linked tracks, genre, or artist records.
        :param vals: Dictionary with album values to update.
        :return: Confirms updated album record.
        """

    def unlink(self: Iterable[Self]) -> Self:
        """Overrides 'unlink' method to delete all linked tracks before delete itself.
        :return: Deleted records.
        """

    def _compute_track_amount(self: Iterable[Self]) -> None:
        """Calculates track amount linked to this album record.
        Result is saved into `track_amount` field.
        :return: None
        """

    def _compute_disk_amount(self: Iterable[Self]) -> None:
        """Calculates disk amount linked to itself according to track metadata.
        Result is saved into `disk_amount` field.
        :return: None
        """

    def _compute_album_cover(self: Iterable[Self]) -> None:
        """Calculates album cover. If cover image is not available for the album, it falls back to the cover
        of the first track with an available cover.
        :return: None
        """

    def _inverse_album_cover(self: Iterable[Self]) -> None:
        """Propagates the album cover to all linked tracks. If the album cover is not set, it clears
        the cover of the tracks.
        :return: None
        """

    def _compute_album_year(self: Iterable[Self]) -> None:
        """Computes album year. If year is not available for the album, it falls back to the `year` field
        of the first track with an available year.
        :return: None
        """

    def _inverse_album_year(self: Iterable[Self]) -> None:
        """Propagates the album year to all linked tracks. If the album year is not set, it clears
        the year of the tracks.
        :return: None
        """

    def _validate_cover_image(self: Iterable[Self]) -> CustomWarningMessage | None:
        """Checks cover image format. If image is WEBP format, clears the field `cover` and returns a warning message.
        :return: Warning Message (dict) | None
        """

    def set_favorite(self: Iterable[Self]) -> None:
        """Toggles the 'is_favorite' field for each album.
        :return: None
        """

    def update_songs(self) -> DisplayNotification | None:
        """Update track metadata linked to this album. It calls to the `save_changes()` method for each track.
        :return: None | Dictionary with UI information
        """

    @staticmethod
    def _process_cover_image(value: AlbumVals) -> None:
        """Process & normalize cover image before create or update records. It converts the image into PNG format,
        center it & scale it to 350x350 px. An error is raised if image has an invalid format.
        :param value: Dictionary with album values, 'cover' field could be included.
        :return: None
        """
