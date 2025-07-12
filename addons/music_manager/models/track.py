# -*- coding: utf-8 -*-
import base64
import io
import logging

# noinspection PyPackageRequirements
import magic
from urllib.parse import urlparse

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import ValidationError
from odoo.fields import Binary, Boolean, Char, Many2many, Many2one, Selection
from odoo.models import Model

from ..services.download_service import YTDLPAdapter, YoutubeDownload
from ..services.metadata_service import MP3File
from ..utils.exceptions import DownloadServiceError, InvalidMetadataServiceError, MusicManagerError


_logger = logging.getLogger(__name__)


class Track(Model):

    _name = 'music_manager.track'
    _description = 'track_table'

    # Default fields
    name = Char(string=_("Song title"))
    year = Char(string=_("Year"))
    track_no = Char(string=_("Track no"))
    disk_no = Char(string=_("Disk no"))
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

    # # Computed fields
    # display_title = Char(string=_("Display title"), compute='_compute_display_title_form', store=True)

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
                    if track.url:
                        self._convert_to_mp3()

                    self._update_fields()

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

    def save_changes(self) -> None:
        pass

    @api.constrains('file', 'url')
    def _check_fields(self) -> None:
        for track in self:

            if not track.file and not track.url:
                _logger.info(f"CONSTRAINT CHECK | file: {bool(track.file)} | url: {bool(track.url)}")
                raise ValidationError(_("Must add an URL or a file to proceed."))

            if track.file and track.url:
                _logger.info(f"CONSTRAINT CHECK | file: {bool(track.file)} | url: {bool(track.url)}")
                raise ValidationError(
                    _("Only one file can be added at the same time. Please, delete one of them to continue.")
                )

    @api.constrains('file')
    def _validate_file_type(self) -> None:
        for track in self:
            if track.file and isinstance(track.file, bytes):

                file_data = base64.b64decode(track.file)
                mime_type = magic.from_buffer(file_data, mime=True)

                if mime_type not in ["audio/mpeg", "audio/mpg", "audio/x-mpeg"]:
                    raise ValidationError(_("Actually only MP3 files are allowed: %s", mime_type))

    @api.constrains('url')
    def _validate_url_path(self) -> None:
        for track in self:
            if track.url and isinstance(track.url, str):

                parsed_url = urlparse(track.url)

                if not (parsed_url.netloc.endswith('youtube.com') or parsed_url.netloc.endswith('youtu.be')):
                    raise ValidationError(_("The URL must be a valid YouTube URL."))

    def _convert_to_mp3(self) -> None:
        for track in self:
            if track.url and isinstance(track.url, str):
                try:
                    buffer = io.BytesIO()
                    adapter = YTDLPAdapter(url=track.url)
                    downloader = YoutubeDownload()

                    bytes_file = downloader.set_stream_to_buffer(adapter, buffer)
                    mime_type = magic.from_buffer(bytes_file, mime=True)
                    _logger.info(f"Download bytes length: {len(bytes_file)} | MIME type: {mime_type}\n")

                    track.write(
                        {
                            'url': False,
                            'file': base64.b64encode(bytes_file)
                        }
                    )

                except DownloadServiceError as video_error:
                    _logger.error(f"Failed to process YouTube URL {track.url}: {video_error}")
                    raise ValidationError(_("Invalid YouTube URL or video is not accessible."))

                except MusicManagerError as unknown_error:
                    _logger.error(f"Unexpected error while validating URL {track.url}: {unknown_error}")
                    raise ValidationError(_("Sorry, something went wrong while validating URL."))

    def _update_fields(self) -> None:
        for track in self:
            try:
                metadata = MP3File().get_metadata(io.BytesIO(base64.b64decode(track.file)))

                track.name = metadata.TIT2
                track.year = metadata.TDRC
                track.track_no = metadata.TRCK
                track.disk_no = metadata.TPOS

            except InvalidMetadataServiceError as invalid_metadata:
                _logger.error(f"Failed to process file metadata: {invalid_metadata}")
                raise ValidationError(_("Invalid metadata founded on file."))

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while processing metadata file: {unknown_error}")
                raise ValidationError(_("Sorry, something went wrong while loading metadata file."))
