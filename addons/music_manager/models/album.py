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
from odoo.fields import Binary, Boolean, Char, Integer, Many2one, One2many

from ..services.image_service import ImageToPNG
from ..utils.custom_types import CustomWarningMessage, AlbumVals
from ..utils.exceptions import ImagePersistenceError, InvalidImageFormatError, MusicManagerError


_logger = logging.getLogger(__name__)


class Album(Model):

    _name = 'music_manager.album'
    _description = 'album_table'
    _order = 'is_favorite desc, name'

    # Basic fields
    name = Char(string=_("Album title"), required=True)
    is_favorite = Boolean(string=_("Favorite"), default=False)

    # Relational fields
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='album_id', string=_("Tracks"))

    # Computed fields
    cover = Binary(
        string=_("Cover"),
        compute='_compute_album_cover',
        inverse='_inverse_album_cover',
        store=True,
    )
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', default=0)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)
    year = Char(string=_("Year"), compute='_compute_album_year', inverse='_inverse_album_year', store=True)

    # Technical fields
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, list_vals: list[AlbumVals]) -> 'Album':
        for vals in list_vals:
            self._process_cover_image(vals)

        # noinspection PyNoneFunctionAssignment
        albums = super().create(list_vals)

        for album in albums:  # type:ignore
            if album.track_ids:
                update_vals = {}

                if album.genre_id:
                    update_vals['genre_id'] = album.genre_id.id

                if album.album_artist_id:
                    update_vals['album_artist_id'] = album.album_artist_id.id

                if update_vals:
                    album.track_ids.write(update_vals)

        return albums

    def write(self, vals: AlbumVals) -> bool:
        self._process_cover_image(vals)

        res = super().write(vals)

        for album in self:  # type: ignore
            update_vals = {}

            if 'genre_id' in vals:
                update_vals['genre_id'] = vals['genre_id']

            if 'album_artist_id' in vals:
                update_vals['album_artist_id'] = vals['album_artist_id']

            if update_vals and album.track_ids:
                album.track_ids.write(update_vals)

        return res

    def unlink(self) -> 'Album':

        for album in self:
            album.track_ids.unlink()

        return super().unlink()

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for album in self:
            album.track_amount = len(album.track_ids) if album.track_ids else 0

    @api.depends('track_ids.total_disk')
    def _compute_disk_amount(self) -> None:
        for album in self:
            disk_amount = album.track_ids.mapped('total_disk')
            album.disk_amount = max(disk_amount) if disk_amount else 0

    @api.depends('track_ids', 'track_ids.cover')
    def _compute_album_cover(self) -> None:
        for album in self:
            if not album.cover:
                track_cover = next((t.cover for t in album.track_ids if t.cover), False)
                album.cover = track_cover

    def _inverse_album_cover(self) -> None:
        for album in self:
            if album.cover:
                album.track_ids.write({'cover': album.cover})

            else:
                album.track_ids.write({'cover': False})

    @api.depends('track_ids', 'track_ids.year')
    def _compute_album_year(self) -> None:
        for album in self:
            if not album.year:
                track_year = next((t.year for t in album.track_ids if t.year), False)
                album.year = track_year

    def _inverse_album_year(self) -> None:
        for album in self:
            if album.year:
                album.track_ids.write({'year': album.year})

            else:
                album.track_ids.write({'year': False})

    @api.onchange('cover')
    def _validate_cover_image(self) -> CustomWarningMessage | None:
        for album in self:
            if not (album.cover and isinstance(album.cover, (str, bytes))):
                continue

            image = base64.b64decode(album.cover)
            mime_type = magic.from_buffer(image, mime=True)

            if mime_type == 'image/webp':
                album.cover = False
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
        for album in self:
            album.is_favorite = not album.is_favorite

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

        for album in self:  # type:ignore
            if album.track_ids:
                for track in album.track_ids:
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
    def _process_cover_image(value: AlbumVals) -> None:
        if 'cover' in value and value['cover']:
            try:
                if isinstance(value['cover'], (str, bytes)):
                    image = base64.b64decode(value['cover'])
                    mime_type = magic.from_buffer(image, mime=True)

                    if mime_type == 'image/webp':
                        raise ValidationError(_("\nThis track cover has an invalid format: %s", mime_type))

                    cover = ImageToPNG(io.BytesIO(image)).center_image().with_size(width=350, height=350).build()
                    value['cover'] = base64.b64encode(cover)

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
