# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Binary, Char, Many2many, Many2one, One2many


class Artist(Model):

    _name = 'music_manager.artist'

    # Default fields
    name = Char(string=_("Artist(s)"))
    picture = Binary(string=_("Profile"))

    # Relationships
    track_ids = Many2many(comodel_name='music_manager.track', string=_("Track(s)"))
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='album_artist_id', string=_("Album(s)"))
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user)
