# -*- coding: utf-8 -*-
from collections.abc import Callable, Sequence
from typing import Final, Literal, Self

from odoo.addons.base.models.res_users import Users
from odoo.api import Environment

from .artist import Artist
from .genre import Genre
from .track import Track
from ..utils.custom_types import AlbumVals, CustomWarningMessage, DisplayNotification, WindowActionView, YearValue


class Album:
    """
    Represents an Album model into the system.
    Manage basic album data like cover, year, genre, artist & tracks.
    """

    _name: Final[str]
    _description: str | None
    _order: str | None

    # Base model fields necessaries for context
    id: int
    env: Environment
    ensure_one: Callable[[], Self]
    exists: Callable[[], bool | Self]
    sudo: Callable[[], bool | Self]
    with_context: Callable[..., Self]

    # Custom fields
    name: str

    album_artist_id: Artist | int | Literal[False]
    genre_id: Genre | int | Literal[False]
    track_ids: Sequence[Track] | Sequence[int]

    album_type: Literal['uncategorized', 'album', 'compilation', 'ep', 'single']
    display_duration: str | Literal[False]
    disk_amount: int
    duration: int
    is_complete: bool
    picture: bytes | Literal[False]
    progress: int
    track_amount: int
    year: YearValue | Literal[False]

    custom_owner_ids: Sequence[Users] | Sequence[int]
    all_track_ids: Sequence[Track] | Sequence[int]

    def create(self, list_vals: list[AlbumVals]) -> Self:
        """Overrides 'create' method to process cover album & propagate to linked tracks, genre or artist records.
        :param list_vals: Dictionary list with album information to create new records.
        :return: Created album records.
        """

    def write(self: Self, vals: AlbumVals) -> Literal[True]:
        """Overrides 'write' method to update cover album & propagate to linked tracks, genre, or artist records.
        :param vals: Dictionary with album values to update.
        :return: Confirms updated album record.
        """

    def unlink(self: Self) -> Literal[True]:
        """Overrides 'unlink' method to delete all linked tracks before delete itself.
        :return: Deleted records.
        """

    def _compute_album_owners(self: Self) -> None:
        """Calculates album owners.
        :return: None
        """

    def _compute_album_picture(self: Self) -> None:
        """Calculates album cover. If cover image is not available for the album, it falls back to the cover
        of the first track with an available cover.
        :return: None
        """

    def _inverse_album_picture(self: Self) -> None:
        """Propagates the album cover to all linked tracks. If the album cover is not set, it clears
        the cover of the tracks.
        :return: None
        """

    def _compute_album_progress(self: Self) -> None:
        """Calculates album complete progress
        :return: None
        """

    def _compute_album_type(self: Self) -> None:
        """Calculates album type according to track amount & time duration.
        :return: None
        """

    def _compute_album_year(self: Self) -> None:
        """Computes album year. If year is not available for the album, it falls back to the `year` field
        of the first track with an available year.
        :return: None
        """

    def _inverse_album_year(self: Self) -> None:
        """Propagates the album year to all linked tracks. If the album year is not set, it clears
        the year of the tracks.
        :return: None
        """

    def _compute_all_track_ids(self: Self) -> None:
        """Calculates all track ids.
        :return: None
        """

    def _compute_display_duration(self: Self) -> None:
        """Calculates displayed album total duration according to disk duration.
        :return: None
        """

    def _compute_display_name(self: Self) -> None:
        """Calculates the display name. It shows context info like artist's name or album type.
        :return: None
        """

    def _compute_disk_amount(self: Self) -> None:
        """Calculates disk amount linked to itself according to track metadata.
        Result is saved into `disk_amount` field.
        :return: None
        """

    def _compute_disk_duration(self: Self) -> None:
        """Calculates album total duration in minutes according to all track durations.
        :return: None
        """

    def _compute_is_complete(self: Self) -> None:
        """Calculates if an album is complete or not
        :return: None
        """

    def _compute_track_amount(self: Self) -> None:
        """Calculates track amount linked to this album record.
        Result is saved into `track_amount` field.
        :return: None
        """

    def action_view_album_content(self: Self) -> WindowActionView:
        """Open a list of tracks that belong to the album record.
        :return: A new window action with environment context
        """

    def update_songs(self: Self) -> DisplayNotification | None:
        """Update track metadata linked to this album. It calls to the `save_changes()` method for each track.
        :return: None | Dictionary with UI information
        """

    def _get_years_list(self: Self) -> list[YearValue]:
        """Calls 'get_years_list' method from file_utils.py to get a years list.
        :return: Complete years list
        """

    # ------------------------------------------------------------------------ #
    # Inherit Methods
    # ------------------------------------------------------------------------ #

    def _validate_picture_image(self: Self) -> CustomWarningMessage | None:
        """MIXIN: See process_image_mixin documentation.
        """

    def _process_picture_image(self, vals: AlbumVals) -> None:
        """MIXIN: See process_image_mixin documentation.
        :param vals: Dictionary with vals to write
        :return: None
        """
