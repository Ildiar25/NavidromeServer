# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Binary, Char, Integer, Many2one, One2many


_logger = logging.getLogger(__name__)


class Album(Model):

    _name = 'music_manager.album'
    _description = 'album_table'

    # Basic fields
    name = Char(string=_("Album title"))
    year = Char(string=_("Year"))
    cover = Binary(string=_("Cover"))

    # Relational fields
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='album_id', string=_("Tracks"))

    # Computed fields
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', default=0)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)

    # Technical fields
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user)

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for album in self:
            album.track_amount = len(album.track_ids) if album.track_ids else 0

    @api.depends('track_ids.total_disk')
    def _compute_disk_amount(self) -> None:
        for album in self:
            disk_amount = album.track_ids.mapped('total_disk')

            album.disk_amount = max(disk_amount) if disk_amount else 0
