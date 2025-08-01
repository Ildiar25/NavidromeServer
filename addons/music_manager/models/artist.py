# -*- coding: utf-8 -*-
import base64
import io
import logging
from typing import Any

import magic
# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import ValidationError
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Date, Integer, Many2many, Many2one, One2many

from ..services.image_service import ImageToPNG
from ..utils.exceptions import ImageServiceError, MusicManagerError


_logger = logging.getLogger(__name__)


class Artist(Model):

    _name = 'music_manager.artist'
    _description = 'artist_table'

    # Basic fields
    birthdate = Date(string=_("Birthdate"))
    name = Char(string=_("Name"))
    picture = Binary(string=_("Profile"))
    real_name = Char(string=_("Real name"), compute='_compute_artist_name', default="Unknown", readonly=False)
    is_favorite = Boolean(string=_("Favorite"), default=False)

    # Relational fields
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='album_artist_id', string=_("Album(s)"))
    track_ids = Many2many(comodel_name='music_manager.track', string=_("Track(s)"))

    # Computed fields
    album_amount = Integer(string=_("Album amount"), compute='_compute_album_amount', default=0, store=True)
    display_title = Char(string=_("Display title"), compute='_compute_display_title_form', store=True)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0, store=True)

    # Technical fields
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, list_vals: list[dict[str, Any]]):
        for vals in list_vals:
            self._process_picture_image(vals)

        return super().create(list_vals)

    def write(self, vals: dict[str, Any]):
        self._process_picture_image(vals)
        return super().write(vals)

    @api.depends('album_ids')
    def _compute_album_amount(self) -> None:
        for artist in self:
            artist.album_amount = len(artist.album_ids)

    @api.depends('name')
    def _compute_artist_name(self) -> None:
        for artist in self:
            artist.real_name = artist.name

    @api.depends('name')
    def _compute_display_title_form(self) -> None:
        for artist in self:
            if not artist.id:
                artist.display_title = _("Edit artist")
            else:
                artist.display_title = _("Artist - %s", artist.name)

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for artist in self:
            artist.track_amount = len(artist.track_ids)

    @api.onchange('picture')
    def _validate_picture_image(self) -> dict[str, dict[str, str]] | None:
        for artist in self:
            if not (artist.picture and isinstance(artist.picture, (str, bytes))):
                continue

            image = base64.b64decode(artist.picture)
            mime_type = magic.from_buffer(image, mime=True)

            if mime_type == 'image/webp':
                artist.picture = False
                return {
                    'warning': {
                        'title': _("Not today! ❌"),
                        'message': _(
                            "\nI'm sooo sorry but, actually WEBP image format is not admited: %s. 🤷", mime_type
                        )
                    }
                }

        return None

    def set_favorite(self) -> None:
        for artist in self:
            artist.is_favorite = not artist.is_favorite

    @staticmethod
    def _process_picture_image(value: dict[str, Any]) -> None:
        if 'picture' in value and value['picture']:
            try:
                if isinstance(value['picture'], (str, bytes)):
                    image = base64.b64decode(value['picture'])
                    mime_type = magic.from_buffer(image, mime=True)

                    if mime_type == 'image/webp':
                        raise ValidationError(_("\nThis artist picture has an invalid format: %s", mime_type))

                    picture = ImageToPNG(io.BytesIO(image)).center_image().with_size(width=250, height=250).build()
                    value['picture'] = base64.b64encode(picture)

            except ImageServiceError as service_error:
                _logger.error(f"Failed to process cover image: {service_error}")
                raise ValidationError(_("\nSomething went wrong while processing cover image: %s", service_error))

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while processing image: {unknown_error}")
                raise ValidationError(
                    _("\nImageServiceError: Sorry, something went wrong while processing cover image")
                )
