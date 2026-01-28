# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Integer, Many2many, Many2one, One2many, Selection

from .mixins.process_image_mixin import ProcessImageMixin
from ..utils.custom_types import AlbumVals
from ..utils.file_utils import get_years_list


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
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', store=False)
    display_duration = Char(string=_("Duration (min)"), compute='_compute_display_duration', store=False, readonly=True)
    duration = Integer(string=_("Duration (sec)"), compute='_compute_disk_duration', store=False)
    picture = Binary(
        string=_("Picture"),
        compute='_compute_album_picture',
        inverse='_inverse_album_picture',
        store=False,
    )
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)
    year = Selection(
        string=_("Debut year"),
        selection='_get_years_list',
        compute='_compute_album_year',
        inverse='_inverse_album_year',
        store=True,
    )

    # Techincal fields
    owner_ids = Many2many(comodel_name='res.users', string=_("Owners"), compute='_compute_album_owners', store=True)
    all_track_ids = Many2many(comodel_name='music_manager.track', string=_("All tracks"), compute='_compute_all_track_ids')

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

    def write(self, vals):
        self._process_picture_image(vals)

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

    def unlink(self):
        if self.env.context.get('skip_album_sync'):
            return super().unlink()

        for album in self:
            own_tracks = album.track_ids.filtered(lambda track: track.owner.id == self.env.user.id)

            if own_tracks:
                own_tracks.unlink()

            if album.exists():
                remaining_tracks = self.env['music_manager.track'].sudo().search_count([
                    ('album_id', '=', album.id)
                ])

                if remaining_tracks == 0:
                    super(Album, album).sudo().unlink()

        return True

    @api.depends('track_ids.owner')
    def _compute_album_owners(self) -> None:
        for album in self:
            album.owner_ids = album.track_ids.mapped('owner')

    @api.depends('track_ids')
    def _compute_all_track_ids(self) -> None:
        for album in self:
            all_tracks = self.env['music_manager.track'].sudo().search([
                ('album_id', '=', album.id)
            ])
            album.all_track_ids = all_tracks

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for album in self:
            album.track_amount = len(album.track_ids) if album.track_ids else 0

    @api.depends('track_ids.total_disk')
    def _compute_disk_amount(self) -> None:
        for album in self:
            disk_amount = album.track_ids.mapped('total_disk')
            album.disk_amount = max(disk_amount) if disk_amount else 0

    @api.depends('track_ids.duration')
    def _compute_disk_duration(self) -> None:
        for album in self:
            disk_duration = album.track_ids.mapped('duration')
            album.duration = sum(disk_duration) if disk_duration else 0

    @api.depends('duration')
    def _compute_display_duration(self) -> None:
        for album in self:
            hours, remainder = divmod(album.duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            album.display_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

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

    @api.depends('track_ids.year')
    def _compute_album_year(self) -> None:
        for album in self:
            tracks_with_year = album.track_ids.filtered(lambda track: track.year)

            if tracks_with_year:
                album.year = tracks_with_year[0].year

            else:
                album.year = False

    def _inverse_album_year(self) -> None:
        for album in self:
            album.track_ids.write({'year': album.year})

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

    @staticmethod
    def _get_years_list():
        return get_years_list()
