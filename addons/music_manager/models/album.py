# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Binary, Char, Date, Integer, Many2one, One2many


class Album(Model):

    _name = 'music_manager.album'

    # Default fields
    name = Char(string=_("Album title"))
    year = Date(string=_("Year"))
    total_tracks = Integer(string=_("Total tracks"))
    disk_nu = Integer(string=_("Disk no"))
    total_disks = Integer(string=_("Total disks"))
    cover = Binary(string=_("Cover"))

    # Relationships
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
