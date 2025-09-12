# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Char, Integer, One2many


class Genre(Model):

    _name = 'music_manager.genre'
    _order = 'name'

    # Default fields
    name = Char(string=_("Name"))

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

    def update_songs(self) -> None:
        for genre in self:
            if genre.track_ids:
                for track in genre.track_ids:
                    track.save_changes()
