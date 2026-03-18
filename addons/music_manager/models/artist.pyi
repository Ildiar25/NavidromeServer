# -*- coding: utf-8 -*-
from collections.abc import Callable, Sequence
from typing import Final, Literal, Self

from odoo.addons.base.models.res_country import Country
from odoo.addons.base.models.res_users import Users
from odoo.api import Environment

from .album import Album
from .track import Track
from ..utils.custom_types import ArtistVals, DisplayNotification, CustomWarningMessage, YearValue


class Artist:
    """
    Represents an Artist model into the system.
    Manage basic artist data like profile picture, birthdate, name, real name, albums & tracks.
    """

    _name: Final[str]
    _description: str | None
    _order: str | None

    # Base model fields necessaries for context
    id: int
    env: Environment
    ensure_one: Callable[[], Self]

    # Custom fields
    biography: str | Literal[False]
    is_group: bool | Literal[False]
    name: str
    picture: bytes | Literal[False]
    real_name: str | Literal[False]
    start_year: YearValue | Literal[False]
    website: str | Literal[False]
    album_ids: Sequence[Album] | Sequence[int]
    country_id: Country | int | Literal[False]
    group_ids: Sequence[Artist] | Sequence[int]
    member_ids: Sequence[Artist] | Sequence[int]
    track_ids: Sequence[Track] | Sequence[int]
    album_amount: int
    display_title: str | Literal[False]
    track_amount: int
    country_code: str | Literal[False]
    custom_owner_id: Users | int

    def create(self, list_vals: list[ArtistVals]) -> Self:
        """Overrides 'create' method to process the profile picture if it exists.
        :param list_vals: Dictionary list with artist information to create new records.
        :return: Created artist records.
        """

    def write(self: Self, vals: ArtistVals) -> Literal[True]:
        """Overrides 'write' method to process the profile picture if it exists before
        update an artist record and ensures only owner can update records.
        :param vals: Dictionary with artist values to update.
        :return: Confirms updated artist record.
        """

    def unlink(self: Self) -> Literal[True]:
        """Overrides 'unlink' method to ensure only owner can delete records.
        :return: Confirms deleted artist record.
        """

    def _compute_display_name(self: Self) -> None:
        """Calculates the display name. It shows context info like artist's debut year or his country.
        :return: None
        """

    def _compute_album_amount(self: Self) -> None:
        """Calculates album amount linked to this artist record.
        Result is saved into `album_amount` field.
        :return: None
        """

    def _compute_display_title_form(self: Self) -> None:
        """Calculates the form title (display_title). It shows "Edit artist" when creating a new
        record and changes to "Edit <artist's name>" once the record has been created.
        :return: None
        """

    def _compute_track_amount(self: Self) -> None:
        """Calculates track amount linked to this artist record.
        Result is saved into `track_amount` field.
        :return: None
        """

    def update_songs(self: Self) -> DisplayNotification | None:
        """Update track metadata linked to this artist. It calls to the `save_changes()` method for each track.
        :return: None | Dictionary with UI information
        """

    def _get_years_list(self: Self) -> list[YearValue]:
        """Calls 'get_years_list' method from file_utils.py to get a years list.
        :return: Complete years list
        """

    def _validate_picture_image(self: Self) -> CustomWarningMessage | None:
        """MIXIN: See process_image_mixin documentation.
        """

    def _process_picture_image(self, vals: ArtistVals) -> None:
        """MIXIN: See process_image_mixin documentation.
        :param vals: Dictionary with vals to write
        :return: None
        """
