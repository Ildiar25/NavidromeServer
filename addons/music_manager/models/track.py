# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Boolean, Char, Integer, Many2many, Many2one


class Track(Model):

    _name = 'music_manager.track'

    # Default fields
    name = Char(string=_("Song title"))
    year = Char(string=_("Year"), readonly=True)
    track_nu = Integer(string=_("Track no"))
    disk_nu = Char(string=_("Disk no"), readonly=True)
    collection = Boolean(string=_("Part of a collection"))
    duration = Char(string=_("Duration (min)"), readonly=True)
    genre = Char(string=_("Genre"), readonly=True)

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
