# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Binary, Char, Date, Many2one


class Album(Model):

    _name = 'music_manager.album'

    # Default fields
    name = Char(string=_("Album title"))
    year = Date(string=_("Year"))
    total_disks = Char(string=_("Total disks"), readonly=True)
    cover = Binary(string=_("Cover"))
    genre = Char(string=_("Genre"), readonly=True)

    # Relationships
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
