# -*- coding: utf-8 -*-
from collections.abc import Callable, Iterable, Sequence
from typing import Final, Literal, Self

from odoo.addons.base.models.res_users import Users
from odoo.api import Environment

from .album import Album
from .track import Track
from ..utils.custom_types import GenreVals, DisplayNotification


class Genre:

    _name: Final[str]
    _description: str | None
    _order: str | None
    _sql_constraints: list[tuple[str, str, str]] | None
    id: int
    env: Environment
    ensure_one: Callable[[], Self]

    name: str
    track_ids: Sequence[Track]
    album_ids: Sequence[Album]
    track_amount: int
    disk_amount: int
    owner: Users

    def write(self, vals: GenreVals) -> Literal[True]:
        """Overrides 'write' method to ensure only owner can update records.
        :param vals: Dictionary with artist values to update.
        :return: Confirms updated artist record.
        """

    def unlink(self) -> Literal[True]:
        """Overrides 'unlink' method to ensure only owner can delete records.
        :return: Confirms deleted genre record.
        """

    def _compute_track_amount(self: Iterable[Self]) -> None:
        """Calculates track amount linked to this genre record.
        Result is saved into `track_amount` field.
        :return: None
        """

    def _compute_disk_amount(self: Iterable[Self]) -> None:
        """Calculates disk amount linked to this genre record.
        Result is saved into `disk_amount` field.
        :return: None
        """

    def update_songs(self) -> DisplayNotification | None:
        """Update track metadata linked to this genre. It calls to the `save_changes()` method for each track.
        :return: None | Dictionary with UI information
        """
