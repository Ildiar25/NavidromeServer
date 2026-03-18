from typing import Any, Dict, List, Literal, Sequence, Tuple, TypeAlias, TypedDict, TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from odoo.addons.base.models.res_country import Country
    from odoo.addons.base.models.res_users import Users

    from ..models import Album, Artist, Genre, Track


class AlbumVals(TypedDict, total=False):
    name: str | Literal[False]
    album_artist_id: 'Artist | int | Literal[False]'
    genre_id: 'Genre | int | Literal[False]'
    track_ids: 'Sequence[Track] | Sequence[int] | Literal[False]'
    album_type: str | Literal[False]
    disk_amount: int
    display_duration: str | Literal[False]
    duration: int
    is_complete: bool
    picture: bytes | Literal[False]
    progress: int
    track_amount: int
    year: str | Literal[False]
    custom_owner_ids: 'Sequence[Users] | Sequence[int] | Literal[False]'
    all_track_ids: 'Sequence[Track] | Sequence[int] | Literal[False]'


class ArtistVals(TypedDict, total=False):
    biography: str | Literal[False]
    is_group: bool
    name: str | Literal[False]
    picture: bytes | Literal[False]
    real_name: str | Literal[False]
    start_year: str | Literal[False]
    website: str | Literal[False]
    album_ids: 'Sequence[Album] | Sequence[int] | Literal[False]'
    country_id: 'Country | int | Literal[False]'
    group_ids: 'Sequence[Artist] | Sequence[int] | Literal[False]'
    member_ids: 'Sequence[Artist] | Sequence[int] | Literal[False]'
    track_ids: 'Sequence[Track] | Sequence[int] | Literal[False]'
    album_amount: int
    display_title: str | Literal[False]
    track_amount: int
    country_code: str | Literal[False]
    custom_owner_id: 'Users | int'


class GenreVals(TypedDict, total=False):
    name: str | Literal[False]
    description: str | Literal[False]
    picture: bytes | Literal[False]
    track_ids: 'Sequence[Track] | Sequence[int] | Literal[False]'
    album_ids: 'Sequence[Album] | Sequence[int] | Literal[False]'
    track_amount: int
    disk_amount: int
    custom_owner_id: 'Users | int'


class TrackVals(TypedDict, total=False):
    picture: bytes | Literal[False]
    disk_no: int | Literal[False]
    name: str | Literal[False]
    total_disk: int | Literal[False]
    total_track: int | Literal[False]
    track_no: int | Literal[False]
    year: str | Literal[False]
    bitrate: int
    channels: str
    codec: str
    duration: int
    mime_type: str
    sample_rate: int
    album_artist_id: 'Artist | int | Literal[False]'
    album_id: 'Album | int | Literal[False]'
    genre_id: 'Genre | int | Literal[False]'
    original_artist_id: 'Artist | int | Literal[False]'
    track_artist_ids: 'Sequence[Artist] | Sequence[int] | Literal[False]'
    compilation: bool
    display_artist_names: str | Literal[False]
    display_bitrate: str | Literal[False]
    display_duration: str | Literal[False]
    display_sample_rate: str | Literal[False]
    is_deleted: bool | Literal[False]
    file_path: str | Literal[False]
    old_path: str | Literal[False]
    album_name: str | Literal[False]
    album_artist: str | Literal[False]
    has_valid_path: Literal[False]
    is_saved: bool
    custom_owner_id: 'Users | int'


class TrackWizardVals(TypedDict, total=False):
    file: bytes | Literal[False]
    picture: bytes | Literal[False]
    tmp_album: str | Literal[False]
    tmp_album_artist: str | Literal[False]
    tmp_artists: str | Literal[False]
    tmp_disk_no: int | Literal[False]
    tmp_genre: str | Literal[False]
    tmp_name: str | Literal[False]
    tmp_original_artist: str | Literal[False]
    tmp_track_no: int | Literal[False]
    tmp_total_disk: int | Literal[False]
    tmp_total_track: int | Literal[False]
    tmp_year: str | Literal[False]
    year: str | Literal[False]
    url: str | Literal[False]
    bitrate: int
    channels: str
    codec: str
    duration: int
    mime_type: str
    sample_rate: int
    possible_album_id: 'Album | int | Literal[False]'
    possible_album_artist_id: 'Artist | int | Literal[False]'
    possible_artist_ids: 'Sequence[Artist] | Sequence[int] | Literal[False]'
    possible_genre_id: 'Genre | int | Literal[False]'
    possible_original_artist_id: 'Artist | int | Literal[False]'
    file_path: str | Literal[False]
    has_valid_path: bool
    tmp_compilation: bool
    state: str


# Custom Odoo types
CustomWarningMessage: TypeAlias = Dict[str, Dict[str, str]]
DisplayNotification: TypeAlias = Dict[str, str | Dict[str, str | bool]]
DomainCustomFilter: TypeAlias = List[Tuple[str, str, List[int]]]
MessageCounter: TypeAlias = Dict[str, int | List[str]]
OptionDownloadSettings: TypeAlias = Dict[str, str | bool | List[Dict[str, str]]]
ReplaceItemCommand: TypeAlias = Tuple[int, int, List[int]]
WindowActionView: TypeAlias = Dict[str, str | int | Dict[Any, Any]]

# Techincal custom types
StreamToFileContext: TypeAlias = Dict[str, MagicMock | List[MagicMock]]
YearValue: TypeAlias = str
