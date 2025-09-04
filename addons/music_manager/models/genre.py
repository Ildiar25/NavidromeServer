# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Char, One2many


class Genre(Model):

    _name = 'music_manager.genre'
    _order = 'name'

    # Default fields
    name = Char(string=_("Name"))

    # Relationships
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='genre_id', string=_("Song(s)"))
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='genre_id', string=_("Album(s)"))
