# -*- coding: utf-8 -*-
import base64
import logging
# noinspection PyPackageRequirements
import magic
from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable
from urllib.parse import urlparse


# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import ValidationError
from odoo.fields import Binary, Boolean, Char, Integer, Many2many, Many2one, Selection
from odoo.models import Model


_logger = logging.getLogger(__name__)


class Track(Model):

    _name = 'music_manager.track'
    _description = 'track_table'

    # Default fields
    name = Char(string=_("Song title"))
    year = Char(string=_("Year"))
    track_nu = Integer(string=_("Track no"))
    disk_nu = Integer(string=_("Disk no"))
    collection = Boolean(string=_("Part of a collection"))
    duration = Char(string=_("Duration (min)"), readonly=True)
    file = Binary(string=_("File"))
    url = Char(string=_("Youtube URL"))
    file_path = Char(string=_("File path"))
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

    def action_back(self) -> None:
        for track in self:
            if track.state == 'done':
                track.state = 'metadata'

    def save_file(self) -> None:
        for track in self:
            if isinstance(track.file, bytes):
                picture = base64.b64decode(track.file)

                name = track.name
                with open(f"/music/{name}.mp3", "wb") as file_test:
                    file_test.write(picture)

                track.file = False

    def save_changes(self) -> None:
        pass

    @api.constrains('file', 'url')
    def _check_fields(self) -> None:
        for track in self:
            if not track.file and not track.url:
                raise ValidationError(_("Must add an URL or a file to proceed."))

    @api.constrains('file')
    def _validate_file_type(self) -> None:
        for track in self:
            if track.file and isinstance(track.file, bytes):

                file_data = base64.b64decode(track.file)
                mime_type = magic.from_buffer(file_data, mime=True)

                if mime_type != 'audio/mpeg':
                    raise ValidationError(_(f"Actually only MP3 files are allowed: {mime_type}."))

    @api.constrains('url')
    def _validate_url_path(self) -> None:
        for track in self:
            if track.url and isinstance(track.url, str):

                parsed_url = urlparse(track.url)

                if not (parsed_url.netloc.endswith('youtube.com') or parsed_url.netloc.endswith('youtu.be')):
                    raise ValidationError(_("URL must be a valid YouTube URL."))

                try:
                    video = YouTube(track.url).streams.get_audio_only()

                except (RegexMatchError, VideoPrivate, VideoRegionBlocked, VideoUnavailable) as video_error:
                    _logger.warning(f"Failed to process YouTube URL {track.url}: {video_error}")
                    raise ValidationError(_("Invalid YouTube URLL or video is not accessible."))

                except Exception as unkown_error:
                    _logger.error(f"Unexpected error while validating URL {track.url}: {unkown_error}")
                    raise ValidationError(_("Sorry, something went wrong while validating URL."))
