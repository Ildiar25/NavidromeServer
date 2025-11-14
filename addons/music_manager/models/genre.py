# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import UserError
from odoo.models import Model
from odoo.fields import Char, Integer, Many2one, One2many

from ..utils.custom_types import GenreVals


class Genre(Model):

    _name = 'music_manager.genre'
    _description = 'genre_table'
    _order = 'name'
    _sql_constraints = [
        ('check_genre_name', 'UNIQUE(name)', _("Genre name must be unique.")),
    ]

    # Default fields
    name = Char(string=_("Name"), required=True)

    # Relationships
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='genre_id', string=_("Track(s)"))
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='genre_id', string=_("Album(s)"))

    # Computed fields
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', default=0)

    # Technical fields
    owner = Many2one(comodel_name='res.users', string="Owner", default=lambda self: self.env.user, required=True)

    def write(self, vals: GenreVals):
        for genre in self:  # type:ignore
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if genre.owner != self.env.user:
                    raise UserError(_("\nCannot update this genre because you are not the owner. 🤷"))

        return super().write(vals)

    def unlink(self):
        for genre in self:  # type:ignore
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if genre.owner != self.env.user:
                    raise UserError(_("\nCannot delete this genre because you are not the owner. 🤷"))

                related_tracks = self.env['music_manager.track'].sudo().search(
                    [('genre_id', '=', genre.id)], limit=1
                )
                related_albums = self.env['music_manager.album'].sudo().search(
                    [('genre_id', '=', genre.id)], limit=1
                )

                if related_tracks or related_albums:
                    raise UserError(_("\nCannot delete this genre because it is in use by other users. 🤷"))

        return super().unlink()

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for genre in self:
            genre.track_amount = len(genre.track_ids) if genre.track_ids else 0

    @api.depends('album_ids')
    def _compute_disk_amount(self) -> None:
        for genre in self:
            genre.disk_amount = len(genre.album_ids) if genre.album_ids else 0

    def update_songs(self):
        self.ensure_one()

        if not self.track_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Music Manager says:"),
                    'message': _("This genre has not any tracks to update!"),
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
                _("All tracks from this genre have been updated!")
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
