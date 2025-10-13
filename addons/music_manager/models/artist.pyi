# -*- coding: utf-8 -*-
from collections.abc import Callable
from datetime import date
from typing import Final, Iterable, Self, Sequence, Literal

from odoo.addons.base.models.res_users import Users

from .album import Album
from .track import Track
from ..utils.custom_types import ArtistVals, DisplayNotification, CustomWarningMessage


class Artist:
    """
    Represents an Artist model into the system.
    Manage basic artist data like profile picture, birthdate, name, real name, albums & tracks.
    """

    _name: Final[str]
    _description: str | None
    _order: str | None
    _sql_constraints: list[tuple[str, str, str]] | None
    id: int
    ensure_one: Callable[[], Self]

    birthdate: date | None
    name: str
    picture: bytes | None
    real_name: str | None
    to_delete: bool
    album_ids: Sequence[Album]
    track_ids: Sequence[Track]
    album_amount: int
    display_title: str | None
    track_amount: int
    user_id: Users

    def create(self, list_vals: list[ArtistVals]) -> Self:
        """Overrides 'create' method to process the profile picture if it exists.
        :param list_vals: Dictionary list with artist information to create new records.
        :return: Created artist records.
        """

    def write(self, vals: ArtistVals) -> Literal[True]:
        """Overrides 'write' method to process the profile picture if it exists before
        update an artist record.
        :param vals: Dictionary with artist values to update.
        :return: Confirms updated artist record.
        """

    def _compute_album_amount(self: Iterable[Self]) -> None:
        """Calculates album amount linked to this artist record.
        Result is saved into `album_amount` field.
        :return: None
        """

    def _compute_display_title_form(self: Iterable[Self]) -> None:
        """Calculates the form title (display_title). It shows "Edit artist" when creating a new
        record and changes to "Edit <artist's name>" once the record has been created.
        :return: None
        """

    def _compute_track_amount(self: Iterable[Self]) -> None:
        """Calculates track amount linked to this artist record.
        Result is saved into `track_amount` field.
        :return: None
        """

    def _compute_artist_name(self: Iterable[Self]) -> None:
        """Calculates `real_name` field copying `name` value if it exists.
        :return: None
        """

    def _validate_picture_image(self: Iterable[Self]) -> CustomWarningMessage | None:
        """Checks profile image format. If image is WEBP format, clears the field `picture`
        and returns a warning message.
        :return: Warning Message (dict) | None
        """

    def update_songs(self) -> DisplayNotification | None:
        """Update track metadata linked to this artist. It calls to the `save_changes()` method for each track.
        :return: None | Dictionary with UI information
        """

    @staticmethod
    def _process_picture_image(value: ArtistVals) -> None:
        """Process & normalizes profile picture before create or update records. It converts
        the image into PNG format, center it & scale it to 250x250 px. An error is raised if
        image has an invalid format.
        :param value: Dictionary with album values, 'picture' field could be included.
        :return: None
        """