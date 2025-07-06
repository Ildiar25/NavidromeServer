# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Char, One2many


class Genre(Model):

    _name = 'music_manager.genre'

    # Default fields
    name = Char(string=_("Name"))

    # Relationships
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='genre_id', string=_("Album(s)"))
