# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Date, Integer, Many2many, Many2one


class Track(Model):

    _name = 'music_manager.track'

    # Default fields
    name = Char(string=_("Song title"))
    year = Date(string=_("Year"))
    track_nu = Integer(string=_("Track no"))
    disk_nu = Integer(string=_("Disk no"))
    collection = Boolean(string=_("Part of a collection"))
    duration = Char(string=_("Duration (min)"), readonly=True)
    file = Binary(string=_("File"))
    url = Char(string=_("Youtube URL"))

    # Relationships
    track_artist_ids = Many2many(
        comodel_name='music_manager.artist',
        string=_("Track artist(s)")
    )
    original_artist = Many2one(
        comodel_name='music_manager.artist',
        string=_("Original artist")
    )
    album_id = Many2one(comodel_name='music_manager.album', string=_("Album"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
