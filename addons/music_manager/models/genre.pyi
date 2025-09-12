# -*- coding: utf-8 -*-
from typing import Final, Iterable, Self, Sequence

from .album import Album
from .track import Track


class Genre:

    _name: Final[str]
    _order: str | None
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

    def update_songs(self: Iterable[Self]) -> None:
        """Update track metadata linked to this genre. It calls to the `save_changes()` method for each track.
        :return: None
        """
