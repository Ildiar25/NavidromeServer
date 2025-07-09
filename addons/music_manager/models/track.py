# -*- coding: utf-8 -*-
import base64

# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Integer, Many2many, Many2one, Selection


class Track(Model):

    _name = 'music_manager.track'

    # Default fields
    name = Char(string=_("Song title"))
    year = Char(string=_("Year"))
    track_nu = Integer(string=_("Track no"))
    disk_nu = Integer(string=_("Disk no"))
    collection = Boolean(string=_("Part of a collection"))
    duration = Char(string=_("Duration (min)"), readonly=True)
    file = Binary(string=_("File"))
    url = Char(string=_("Youtube URL"))
    cover = Binary(string=_("Cover"))
    state = Selection(
        selection=[
            ('start', _("Start")),
            ('uploaded', _("Uploaded")),
            ('metadata', _("Metadata Editing")),
            ('done', _("Done")),
            ('added', _("Added")),
        ],
        string=_("State"),
        default='start'
    )

    # Relationships
    track_artist_ids = Many2many(comodel_name='music_manager.artist', string=_("Track artist(s)"))
    album_id = Many2one(comodel_name='music_manager.album', string=_("Album"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
    original_artist = Many2one(comodel_name='music_manager.artist', string=_("Original artist"))
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user)

    def action_next(self) -> None:
        for track in self:
            match track.state:
                case 'start':
                    track.state = 'uploaded'

                case 'uploaded':
                    track.state = 'metadata'

                case 'metadata':
                    track.state = 'done'

                case 'done':
                    track.state = 'added'

    def save_file(self) -> None:
        for track in self:
            if not track.file:
                continue

            picture = base64.b64decode(track.file)

            name = track.name
            with open(f"/music/{name}.png", "wb") as file_test:
                file_test.write(picture)

            track.file = False
