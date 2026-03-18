# -*- coding: utf-8 -*-
from collections.abc import Callable, Sequence
from typing import Final, Literal, Self

from odoo.addons.base.models.res_users import Users
from odoo.api import Environment

from .album import Album
from .track import Track
from ..utils.custom_types import CustomWarningMessage, DisplayNotification, GenreVals


class Genre:
    """
    Represents a Genre model into the system.
    Manage basic genre data like name, description and track amount.
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
    name: str
    description: str | Literal[False]
    picture: bytes | Literal[False]
    track_ids: Sequence[Track] | Sequence[int]
    album_ids: Sequence[Album] | Sequence[int]
    track_amount: int
    disk_amount: int
    custom_owner_id: Users | int

    def create(self, list_vals: list[GenreVals]) -> Self:
        """Overrides 'create' method to process the genre picture if it exists.
        :param list_vals: Dictionary list with genre information to create new records.
        :return: Created genre records.
        """

    def write(self: Self, vals: GenreVals) -> Literal[True]:
        """Overrides 'write' method to ensure only owner can update records.
        :param vals: Dictionary with artist values to update.
        :return: Confirms updated artist record.
        """

    def unlink(self: Self) -> Literal[True]:
        """Overrides 'unlink' method to ensure only owner can delete records.
        :return: Confirms deleted genre record.
        """

    def _compute_track_amount(self: Self) -> None:
        """Calculates track amount linked to this genre record.
        Result is saved into `track_amount` field.
        :return: None
        """

    def _compute_disk_amount(self: Self) -> None:
        """Calculates disk amount linked to this genre record.
        Result is saved into `disk_amount` field.
        :return: None
        """

    def update_songs(self) -> DisplayNotification | None:
        """Update track metadata linked to this genre. It calls to the `save_changes()` method for each track.
        :return: None | Dictionary with UI information
        """

    def _validate_picture_image(self: Self) -> CustomWarningMessage | None:
        """MIXIN: See process_image_mixin documentation.
        """

    def _process_picture_image(self, vals: GenreVals) -> None:
        """MIXIN: See process_image_mixin documentation.
        :param vals: Dictionary with vals to write
        :return: None
        """
