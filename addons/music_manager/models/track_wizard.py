# -*- coding: utf-8 -*-
import logging

from urllib.parse import urlparse
# noinspection PyProtectedMember
from odoo import _, api, Command
from odoo.exceptions import ValidationError
from odoo.fields import Binary, Boolean, Char, Integer, Selection, Many2many, Many2one
from odoo.models import TransientModel

from .mixins.process_image_mixin import ProcessImageMixin
from ..adapters.download_service_adapter import DownloadServiceAdapter
from ..adapters.file_service_adapter import FileServiceAdapter
from ..adapters.track_service_adapter import TrackServiceAdapter
from ..utils.constants import ALLOWED_MUSIC_FORMAT
from ..utils.custom_types import CustomWarningMessage
from ..utils.data_encoding import base64_decode, base64_encode
from ..utils.exceptions import (
    ClientPlatformError,
    FilePersistenceError,
    InvalidFileFormatError,
    InvalidPathError,
    MusicManagerError,
    VideoProcessingError,
)
from ..utils.file_utils import validate_allowed_mimes


_logger = logging.getLogger(__name__)


class TrackWizard(TransientModel, ProcessImageMixin):
    _name = 'music_manager.track_wizard'
    _description = 'track_wizard_table'

    # Basic fields
    file = Binary(string=_("File"))
    picture = Binary(string=_("Picture"))
    tmp_album = Char(string=_("Album found"))
    tmp_album_artist = Char(string=_("Album artist found"))
    tmp_artists = Char(string=_("Track artist(s) found"))
    tmp_collection = Boolean(string="Part of a collection")
    tmp_disk_no = Integer(string=_("Disk number found"))
    tmp_genre = Char(string=_("Genre found"))
    tmp_name = Char(string=_("Title found"))
    tmp_original_artist = Char(string=_("Original artist found"))
    tmp_track_no = Integer(string=_("Track number found"))
    tmp_total_disk = Integer(string=_("Total disk number found"))
    tmp_total_track = Integer(string=_("Total track number found"))
    tmp_year = Char(string=_("Year found"))
    url = Char(string=_("Youtube URL"))

    # Readonly fields
    bitrate = Char(string=_("Bit rate"), default="Unknown", readonly=True)
    channels = Char(string=_("Channels"), default="Stereo", readonly=True)
    codec = Char(string=_("Codec"), default="Unknown", readonly=True)
    duration = Char(string=_("Duration (min)"), default="0:00", readonly=True)
    mime_type = Char(string=_("MIME"), default="Unknown", readonly=True)
    sample_rate = Char(string=_("Sample rate"), default="Unknown", readonly=True)

    # Relational fields
    possible_album_id = Many2one(comodel_name='music_manager.album', string="Matched album")
    possible_album_artist_id = Many2one(comodel_name='music_manager.artist', string="Matched album artist")
    possible_artist_ids = Many2many(comodel_name='music_manager.artist', string="Matched artist(s)")
    possible_genre_id = Many2one(comodel_name='music_manager.genre', string="Matched genre")
    possible_original_artist_id = Many2one(comodel_name='music_manager.artist', string="Matched original artist")

    # Computed fields
    file_path = Char(string=_("File path"), compute='_compute_file_path', store=True)
    has_valid_path = Boolean(string=_("Valid path"), compute='_compute_has_valid_path', default=False)

    # Technical fields
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

    @api.depends('tmp_name', 'possible_album_artist_id', 'possible_album_id', 'tmp_track_no')
    def _compute_file_path(self) -> None:
        file_service = self._get_file_service_adapter()

        for wizard in self:
            wizard.file_path = file_service.set_new_path(
                artist=wizard.possible_album_artist_id.name or '',
                album=wizard.possible_album_id.name or '',
                track=str(wizard.tmp_track_no) or '',
                title=wizard.tmp_name or '',
            )

    @api.depends('file_path')
    def _compute_has_valid_path(self) -> None:
        file_service = self._get_file_service_adapter()

        for wizard in self:
            if not (wizard.file_path and isinstance(wizard.file_path, str)):
                continue

            wizard.has_valid_path = file_service.is_valid(wizard.file_path)

    @api.constrains('file', 'url', 'file_path')
    def _check_fields(self) -> None:
        for wizard in self:
            if wizard.file_path and wizard.has_valid_path:
                continue

            if not wizard.file and not wizard.url:
                _logger.info(f"CONSTRAINT CHECK | file: {bool(wizard.file)} | url: {bool(wizard.url)}")
                raise ValidationError(_("\nMust add an URL or upload a file to proceed."))

            if wizard.file and wizard.url:
                _logger.info(f"CONSTRAINT CHECK | file: {bool(wizard.file)} | url: {bool(wizard.url)}")
                raise ValidationError(
                    _("\nOnly one field can be added at the same time. Please, delete one of them to continue.")
                )

    @api.onchange('file')
    def _validate_file_type(self) -> CustomWarningMessage | None:
        for wizard in self:
            if not (wizard.file and isinstance(wizard.file, bytes)):
                continue

            try:
                validate_allowed_mimes(wizard.file, ALLOWED_MUSIC_FORMAT)

            except InvalidFileFormatError as invalid_file:
                wizard.file = False
                return {
                    'warning': {
                        'title': _("Wait a minute! 👮"),
                        'message': _(
                            "\nActually only MP3 files are allowed. Don't f*ck the system! \n%s.", invalid_file
                        )
                    }
                }

        return None

    @api.onchange('url')
    def _validate_url_path(self) -> CustomWarningMessage | None:
        for wizard in self:
            if not (wizard.url and isinstance(wizard.url, str)):
                continue

            parsed_url = urlparse(wizard.url)

            if not (parsed_url.netloc.endswith('youtube.com') or parsed_url.netloc.endswith('youtu.be')):
                return {
                    'warning': {
                        'title': _("C'mon dude! 🙄"),
                        'message': _("\nThe web address has to be valid and we both know it is not.")
                    }
                }

        return None

    def action_back(self) -> dict[str, str]:
        self.ensure_one()

        states = ['start', 'uploaded', 'metadata', 'done', 'added']
        current_index = states.index(self.state)

        if current_index > 0:
            self.state = states[current_index - 1]

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.track_wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_next(self) -> dict[str, str]:
        self.ensure_one()

        match self.state:
            case 'start':
                self.state = 'uploaded'
                if self.url:
                    self._convert_to_mp3()

                self._update_fields()

            case 'uploaded':
                self.state = 'metadata'

            case 'metadata':
                self.state = 'done'

            case 'added':
                return {'type': 'ir.actions.act_window_close'}

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.track_wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def match_all_metadata(self) -> None:
        self._match_album_id()
        self._match_album_artist_id()
        self._match_artist_ids()
        self._match_genre_id()
        self._match_original_artist_id()

    def save_file(self):
        file_service = self._get_file_service_adapter()

        for wizard in self:  # type:ignore
            if not (isinstance(wizard.file, bytes) and wizard.has_valid_path):
                continue

            song = base64_decode(wizard.file)

            try:
                file_service.save_file(wizard.file_path, song)

            except InvalidPathError as invalid_path:
                _logger.error(f"There was an issue with file path: {invalid_path}")
                raise ValidationError(_("\nActually, the file path of this record is not valid."))

            except FilePersistenceError as not_allowed:
                _logger.error(f"Cannot write the file: {not_allowed}")
                raise ValidationError(
                    _("\nAn internal issue ocurred while trying to save the file."
                      "\nPlease, try it again with a different one.")
                )

            except MusicManagerError as unknown_error:
                _logger.error(f"Unespected error while trying to save the file: {unknown_error}")
                raise ValidationError(
                    _("\nDamn! Something went wrong while saving the file.\nPlease, contact with your Admin.")
                )

            # ⬇️ HERE creates a new TRACK record ⬇️

            track = self.env['music_manager.track'].create({
                'picture': wizard.picture,
                'disk_no': wizard.tmp_disk_no,
                'name': wizard.tmp_name,
                'total_disk': wizard.tmp_total_disk,
                'total_track': wizard.tmp_total_track,
                'track_no': wizard.tmp_track_no,
                'year': wizard.tmp_year,
                'album_artist_id': wizard.possible_album_artist_id.id,
                'album_id': wizard.possible_album_id.id,
                'genre_id': wizard.possible_genre_id.id,
                'original_artist_id': wizard.possible_original_artist_id.id,
                'track_artist_ids': [Command.set(wizard.possible_artist_ids.ids)],
                'collection': wizard.tmp_collection,
                'file_path': wizard.file_path,
                'old_path': wizard.file_path,
                'is_saved': True,
                'bitrate': wizard.bitrate,
                'channels': wizard.channels,
                'codec': wizard.codec,
                'duration': wizard.duration,
                'mime_type': wizard.mime_type,
                'sample_rate': wizard.sample_rate,
            })

            return {
                'name': _('New Track'),
                'view_mode': 'form',
                'res_model': 'music_manager.track',
                'res_id': track.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

        return None

    def _convert_to_mp3(self) -> None:
        for wizard in self:
            if not (wizard.url and isinstance(wizard.url, str)):
                continue

            try:
                download_service = self._get_download_service_adapter(wizard.url)
                bytes_file = download_service.to_buffer()

                wizard.write(
                    {
                        'url': False,
                        'file': base64_encode(bytes_file)
                    }
                )

            except ClientPlatformError as download_error:
                _logger.error(f"Failed to process YouTube URL '{wizard.url}': {download_error}")
                raise ValidationError(_("\nInvalid YouTube URL or video is not accessible."))

            except VideoProcessingError as video_error:
                _logger.error(f"Failed to process downloaded video: {video_error}")
                raise ValidationError(
                    _("\nAn internal issue ocurred while processing the video. Please, try a different URL.")
                )

            except InvalidPathError as invalid_path:
                _logger.error(f"There was an issue with file path: {invalid_path}")
                raise ValidationError(_("\nActually, the final path where to save file is not valid."))

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while processing video URL '{wizard.url}': {unknown_error}")
                raise ValidationError(
                    _("\nDamn! Something went wrong while validating URL.\nPlease, contact with your Admin.")
                )

    def _get_download_service_adapter(self, video_url: str):
        settings = self.env['music_manager.audio_settings'].search([], limit=1)

        adapter_type = settings.available_adapters if settings else 'ytdlp'
        config = {
            'format': settings.sound_format if settings else 'mp3',
            'quality': settings.bitrate if settings else '192',
        }

        return DownloadServiceAdapter(video_url=video_url, adapter_type=adapter_type, config=config)

    def _get_file_service_adapter(self):
        settings = self.env['music_manager.audio_settings'].search([], limit=1)

        root = settings.root_dir if settings else '/music'
        file_extension = settings.sound_format if settings else 'mp3'

        return FileServiceAdapter(str_root_dir=root, file_extension=file_extension)

    def _get_track_service_adapter(self):
        settings = self.env['music_manager.audio_settings'].search([], limit=1)

        file_extension = settings.sound_format if settings else 'mp3'

        return TrackServiceAdapter(file_type=file_extension)

    def _match_album_id(self) -> None:
        for wizard in self:
            wizard.possible_album_id = False
            _logger.info(f"TMP_ALBUM: {wizard.tmp_album}")

            if not wizard.tmp_album:
                _logger.info(f"OPS: Not tmp album: {wizard.tmp_album}")
                continue

            found = self.env['music_manager.album'].search([('name', 'ilike', wizard.tmp_album)], limit=1)
            _logger.info(f"ALBUM FOUNDED: {found.name} | ID: {found.id}")
            wizard.possible_album_id = found.id

    def _match_album_artist_id(self) -> None:
        for wizard in self:
            wizard.possible_album_artist_id = False

            if not wizard.tmp_album_artist:
                continue

            found = self.env['music_manager.artist'].search([('name', 'ilike', wizard.tmp_album_artist)], limit=1)
            wizard.possible_album_artist_id = found.id

    def _match_artist_ids(self) -> None:
        for wizard in self:
            wizard.possible_artist_ids = [Command.clear()]

            if not wizard.tmp_artists:
                continue

            names = [name.strip() for name in wizard.tmp_artists.split(",")]
            artist_ids = []

            for name in names:
                found = self.env['music_manager.artist'].search([('name', 'ilike', name)], limit=1)

                if not found:
                    continue

                artist_ids.append(found.id)

            wizard.possible_artist_ids = [Command.set(artist_ids)]

    def _match_genre_id(self) -> None:
        for wizard in self:
            wizard.possible_genre_id = False

            if not wizard.tmp_genre:
                continue

            found = self.env['music_manager.genre'].search([('name', 'ilike', wizard.tmp_genre)], limit=1)
            wizard.possible_genre_id = found.id

    def _match_original_artist_id(self) -> None:
        for wizard in self:
            wizard.possible_original_artist_id = False

            if not wizard.tmp_original_artist:
                continue

            found = self.env['music_manager.artist'].search([('name', 'ilike', wizard.tmp_original_artist)], limit=1)
            wizard.possible_original_artist_id = found.id

    def _update_fields(self) -> None:
        track_service = self._get_track_service_adapter()

        for wizard in self:
            audio_info = track_service.read_audio_info(wizard.file)

            for attr_name, value in audio_info.items():
                if hasattr(wizard, attr_name):
                    setattr(wizard, attr_name, value)

            wizard.match_all_metadata()
