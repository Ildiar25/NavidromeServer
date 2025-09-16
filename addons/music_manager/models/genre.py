# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Char, Integer, One2many


class Genre(Model):

    _name = 'music_manager.genre'
    _description = 'genre_table'
    _order = 'name'
    _sql_constraints = [
        ('check_genre_name', 'UNIQUE(name)', _("The genre name must be unique.")),
    ]

    # Default fields
    name = Char(string=_("Name"), required=True)

    # Relationships
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='genre_id', string=_("Song(s)"))
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='genre_id', string=_("Album(s)"))

    # Computed fields
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', default=0)

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for genre in self:
            genre.track_amount = len(genre.track_ids) if genre.track_ids else 0

    @api.depends('album_ids')
    def _compute_disk_amount(self) -> None:
        for genre in self:
            genre.disk_amount = len(genre.album_ids) if genre.album_ids else 0

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

        for genre in self:  # type:ignore
            if genre.track_ids:
                for track in genre.track_ids:
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
