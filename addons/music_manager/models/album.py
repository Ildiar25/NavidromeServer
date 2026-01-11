# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Integer, Many2one, One2many

from .mixins.process_image_mixin import ProcessImageMixin
from ..utils.custom_types import AlbumVals


_logger = logging.getLogger(__name__)


class Album(Model, ProcessImageMixin):
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
    picture = Binary(
        string=_("Picture"),
        compute='_compute_album_picture',
        inverse='_inverse_album_picture',
        store=False,
    )
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', default=0)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)
    year = Char(string=_("Year"), compute='_compute_album_year', inverse='_inverse_album_year', store=True)

    # Techincal fields
    owner = Many2one(comodel_name='res.users', string="Owner", default=lambda self: self.env.user, required=True)

    @api.model_create_multi
    def create(self, list_vals: list[AlbumVals]):
        for vals in list_vals:
            self._process_picture_image(vals)

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

    def write(self, vals: AlbumVals):
        self._process_picture_image(vals)

        res = super().write(vals)

        for album in self:  # type: ignore
            update_vals = {}

            if 'genre_id' in vals:
                update_vals['genre_id'] = vals['genre_id']

            if 'album_artist_id' in vals:
                update_vals['album_artist_id'] = vals['album_artist_id']

            if 'owner' in vals:
                update_vals['owner'] = vals['owner']

            if update_vals and album.track_ids:
                album.track_ids.write(update_vals)

        return res

    def unlink(self):

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

    @api.depends('track_ids.picture')
    def _compute_album_picture(self) -> None:
        for album in self:
            tracks_with_pic = album.track_ids.filtered(lambda track: track.picture)

            if tracks_with_pic:
                album.picture = tracks_with_pic[0].picture

            else:
                album.picture = False

    def _inverse_album_picture(self) -> None:
        for album in self:
            album.track_ids.write({'picture': album.picture})

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

    def set_favorite(self) -> None:
        for album in self:
            album.is_favorite = not album.is_favorite

    def update_songs(self):
        self.ensure_one()

        if not self.track_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Music Manager says:"),
                    'message': _("This album has not any tracks to update!"),
                    'type': 'info',
                    'sticky': False,
                }
            }

        total_success_count = 0
        total_failure_messages = []

        for track in self.track_ids:
            results = track._perform_save_changes()
            total_success_count += results['success']

            if results['messages']:
                total_failure_messages.extend(results['messages'])

        final_message = []

        if total_success_count == len(self.track_ids):
            final_message.append(
                _("All tracks from this album have been updated!")
            )

        if total_failure_messages:
            final_message.append(
                _("Some tracks have been ignored:")
            )
            final_message.extend(total_failure_messages)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Music Manager says:"),
                'message': " • ".join(final_message),
                'type': 'warning' if total_failure_messages else 'success',
                'sticky': False,
            }
        }
