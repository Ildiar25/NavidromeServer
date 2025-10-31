from datetime import date
from typing import Dict, List, Literal, Sequence, Tuple, TypeAlias, TypedDict


class AlbumVals(TypedDict, total=False):
    name: str
    album_artist_id: int | None
    genre_id: int | None
    track_ids: Sequence[int]
    cover: bytes
    disk_amount: int
    track_amount: int
    year: str
    user_id: int


class ArtistVals(TypedDict, total=False):
    birthdate: date
    name: str
    picture: bytes
    real_name: str
    is_favorite: bool
    album_ids: Sequence[int]
    track_ids: Sequence[int]
    album_amount: int
    display_title: str
    track_amount: int
    user_id: int


class GenreVals(TypedDict, total=False):
    name: str
    track_ids: Sequence[int]
    album_ids: Sequence[int]
    track_amount: int
    disk_amount: int


class TrackVals(TypedDict, total=False):
    cover: bytes | None
    disk_no: int | None
    duration: str | None
    file_type: str | None
    name: str | None
    total_disk: int | None
    total_track: int | None
    track_no: int | None
    year: str
    album_artist_id: int | None
    album_id: int | None
    genre_id: int | None
    original_artist_id: int | None
    track_artist_ids: Sequence[int]
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
    user_id: int


# Custom types
MessageCounter: TypeAlias = Dict[str, int | List[str]]
CustomWarningMessage: TypeAlias = Dict[str, Dict[str, str]]
DisplayNotification: TypeAlias = Dict[str, str | Dict[str, str | bool]]
ReplaceItemCommand: TypeAlias = Tuple[int, int, List[int]]
DomainCustomFilter: TypeAlias = List[Tuple[str, str, List[int]]]
