# -*- coding: utf-8 -*-
from typing import Final, Iterable, Optional, Self, Sequence

from .album import Album
from .track import Track
from ..utils.custom_types import DisplayNotification


class Genre:

    _name: Final[str]
    _order: str | None
    _sql_constraints: list[tuple[str, str, str]] | None
    id: int

    name: str
    track_ids: Sequence[Track]
    album_ids: Sequence[Album]
    track_amount: int
    disk_amount: int

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
