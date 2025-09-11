# -*- coding: utf-8 -*-
from typing import Final, Sequence

from .album import Album
from .track import Track


class Genre:

    _name: Final[str]
    _order: str | None
    id: int

    name: str
    track_ids: Sequence[Track]
    album_ids: Sequence[Album]