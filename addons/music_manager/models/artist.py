# -*- coding: utf-8 -*-
import base64
import io
import logging

# noinspection PyPackageRequirements
import magic
# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import ValidationError
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Date, Integer, Many2many, Many2one, One2many, Text

from ..services.image_service import ImageToPNG
from ..utils.custom_types import CustomWarningMessage, ArtistVals
from ..utils.exceptions import ImagePersistenceError, InvalidImageFormatError, MusicManagerError

_logger = logging.getLogger(__name__)


class Artist(Model):

    _name = 'music_manager.artist'
    _description = 'artist_table'
    _order = 'to_delete, name'

    # Basic fields
    birthdate = Date(string=_("Birthdate"))
    name = Char(string=_("Name"), required=True)
    picture = Binary(string=_("Profile"))
    real_name = Text(string=_("Real name"), compute='_compute_artist_name', readonly=False, store=True)

    # Relational fields
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='album_artist_id', string=_("Album(s)"))
    track_ids = Many2many(comodel_name='music_manager.track', string=_("Track(s)"))

    # Computed fields
    album_amount = Integer(string=_("Album amount"), compute='_compute_album_amount', default=0, store=False)
    display_title = Char(string=_("Display title"), compute='_compute_display_title_form', store=True)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0, store=False)

    # Technical fields
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, list_vals: list[ArtistVals]) -> 'Artist':
        for vals in list_vals:
            self._process_picture_image(vals)

        return super().create(list_vals)

    def write(self, vals: ArtistVals) -> bool:
        self._process_picture_image(vals)
        return super().write(vals)

    @api.depends('album_ids')
    def _compute_album_amount(self) -> None:
        for artist in self:
            artist.album_amount = len(artist.album_ids) if artist.album_ids else 0

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
            artist.track_amount = len(artist.track_ids) if artist.track_ids else 0

    @api.depends('name')
    def _compute_artist_name(self) -> None:
        for artist in self:
            if isinstance(artist.name, str):
                artist.real_name = artist.name

    @api.onchange('picture')
    def _validate_picture_image(self) -> CustomWarningMessage | None:
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

    def update_songs(self):
        if not self.track_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Music Manager says:"),
                    'message': _("There are not any tracks to update!"),
                    'type': 'info',
                    'sticky': False,
                }
            }

        for artist in self:  # type:ignore
            if artist.track_ids:
                for track in artist.track_ids:
                    track.save_changes()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Music Manager says:"),
                    'message': _("All metadata tracks are been updated!"),
                    'type': 'success',
                    'sticky': False,
                }
            }

        return None

    @staticmethod
    def _process_picture_image(value: ArtistVals) -> None:
        if 'picture' in value and value['picture']:
            try:
                if isinstance(value['picture'], (str, bytes)):
                    image = base64.b64decode(value['picture'])
                    mime_type = magic.from_buffer(image, mime=True)

                    if mime_type == 'image/webp':
                        raise ValidationError(_("\nThis artist picture has an invalid format: %s", mime_type))

                    picture = ImageToPNG(io.BytesIO(image)).center_image().with_size(width=250, height=250).build()
                    value['picture'] = base64.b64encode(picture)

            except InvalidImageFormatError as format_error:
                _logger.error(f"Image has an invalid format or file is corrupt: {format_error}.")
                raise ValidationError(_("\nThe uploaded file has an invalid format or is corrupt."))

            except ImagePersistenceError as service_error:
                _logger.error(f"Failed to process cover image: {service_error}.")
                raise ValidationError(
                    _("\nAn internal issue ocurred while processing the image. Please, try a different file.")
                )

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while processing image: {unknown_error}.")
                raise ValidationError(
                    _("\nImageServiceError: Sorry, something went wrong while processing cover image.")
                )
