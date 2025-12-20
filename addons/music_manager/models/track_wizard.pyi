# -*- coding: utf-8 -*-
from collections.abc import Callable, Iterable, Sequence
from typing import Final, Literal, Optional, Self


class TrackWizard:
    """
    Represents a Track Wizard model into the system.
    Manage basic temporal data found in the given track like cover, track no, album_id, file_path & others.
    """

    _name: Final[str]
    _description: str | None

    file: bytes | None
    tmp_album: str | None
    tmp_album_artist: str | None
    tmp_artists: str | None
    tmp_collection: bool
    tmp_genre: str | None
    tmp_original_artist: str | None
    url: str | None

    state: Literal['start', 'uploaded', 'metadata', 'done', 'added']