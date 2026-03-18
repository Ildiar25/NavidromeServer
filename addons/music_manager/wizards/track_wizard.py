# -*- coding: utf-8 -*-
import logging
from typing import List, Literal

from urllib.parse import urlparse
# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import ValidationError
from odoo.fields import Binary, Boolean, Char, Integer, Selection, Many2many, Many2one
from odoo.models import TransientModel

from ..models.mixins.process_image_mixin import ProcessImageMixin
from ..adapters.download_service_adapter import DownloadServiceAdapter
from ..adapters.file_service_adapter import FileServiceAdapter
from ..adapters.track_service_adapter import TrackServiceAdapter
from ..utils.constants import ALLOWED_MUSIC_FORMAT
from ..utils.data_encoding import base64_decode, base64_encode
from ..utils.exceptions import (
    ClientPlatformError,
    FilePersistenceError,
    InvalidFileFormatError,
    InvalidPathError,
    MusicManagerError,
    VideoProcessingError,
)
from ..utils.file_utils import validate_allowed_mimes, get_years_list


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
    tmp_disk_no = Integer(string=_("Disk number found"))
    tmp_genre = Char(string=_("Genre found"))
    tmp_name = Char(string=_("Title found"))
    tmp_original_artist = Char(string=_("Original artist found"))
    tmp_track_no = Integer(string=_("Track number found"))
    tmp_total_disk = Integer(string=_("Total disk number found"))
    tmp_total_track = Integer(string=_("Total track number found"))
    tmp_year = Char(string=_("Year found"))
    year = Selection(string=_("Year"), selection='_get_years_list')
    url = Char(string=_("Youtube URL"))

    # Readonly fields
    bitrate = Integer(string=_("Bitrate"), default=0, readonly=True)
    channels = Char(string=_("Channels"), default="Stereo", readonly=True)
    codec = Char(string=_("Codec"), default="Unknown", readonly=True)
    duration = Integer(string=_("Duration (sec)"), default=0, readonly=True)
    mime_type = Char(string=_("MIME"), default="Unknown", readonly=True)
    sample_rate = Integer(string=_("Sample rate"), default=0, readonly=True)

    # Relational fields
    possible_album_id = Many2one(comodel_name='music_manager.album', string=_("Matched album"))
    possible_album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Matched album artist"))
    possible_artist_ids = Many2many(comodel_name='music_manager.artist', string=_("Matched artist(s)"))
    possible_genre_id = Many2one(comodel_name='music_manager.genre', string=_("Matched genre"))
    possible_original_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Matched original artist"))

    # Computed fields
    file_path = Char(string=_("File path"), compute='_compute_file_path', store=True)
    has_valid_path = Boolean(string=_("Valid path"), compute='_compute_has_valid_path', default=False)
    tmp_compilation = Boolean(string=_("Part of a compilation"), default=False)

    # Technical fields
    state = Selection(
        selection=[
            ('start', _("Start")),
            ('uploaded', _("Uploaded")),
            ('metadata', _("Metadata Editing")),
            ('done', _("Done")),
        ],
        string=_("State"),
        default='start'
    )

    @api.depends('tmp_name', 'possible_album_artist_id', 'possible_album_id', 'tmp_track_no', 'tmp_disk_no')
    def _compute_file_path(self) -> None:
        self.ensure_one()
        file_service = self._get_file_service_adapter()

        self.file_path = file_service.set_new_path(
            artist=self.possible_album_artist_id.name or '',
            album=self.possible_album_id.name or '',
            disk=str(self.tmp_disk_no) or '',
            track=str(self.tmp_track_no) or '',
            title=str(self.tmp_name) or '',
        )

    @api.depends('file_path')
    def _compute_has_valid_path(self) -> None:
        self.ensure_one()
        file_service = self._get_file_service_adapter()

        if not (self.file_path and isinstance(self.file_path, str)):
            return

        self.has_valid_path = file_service.is_valid(self.file_path)

    @api.constrains('file', 'url', 'file_path')
    def _check_fields(self) -> None:
        self.ensure_one()
        if self.file_path and self.has_valid_path:
            return

        if not self.file and not self.url:
            _logger.info(f"CONSTRAINT CHECK | file: {bool(self.file)} | url: {bool(self.url)}")
            raise ValidationError(_("\nMust add an URL or upload a file to proceed."))

        if self.file and self.url:
            _logger.info(f"CONSTRAINT CHECK | file: {bool(self.file)} | url: {bool(self.url)}")
            raise ValidationError(
                _("\nOnly one field can be added at the same time. Please, delete one of them to continue.")
            )

    @api.onchange('possible_album_artist_id')
    def _compute_compilation_value(self) -> None:
        self.ensure_one()
        if self.possible_album_artist_id and self.possible_album_artist_id.name.lower() == 'various artists':
            self.tmp_compilation = True

        else:
            self.tmp_compilation = False

    @api.onchange('tmp_compilation')
    def _compute_inverse_compilation_value(self) -> None:
        self.ensure_one()

        if self.tmp_compilation:
            target_name = "Various Artists"
            fallback_artists = self.env['music_manager.artist']

        else:
            target_name = self.possible_original_artist_id.name if self.possible_original_artist_id else ""
            fallback_artists = self.possible_artist_ids

        self.possible_album_artist_id = self._find_or_create_single_artist(target_name, fallback_artists)

    @api.onchange('file')
    def _validate_file_type(self):
        self.ensure_one()
        if not (self.file and isinstance(self.file, bytes)):
            return None

        try:
            validate_allowed_mimes(self.file, ALLOWED_MUSIC_FORMAT)

        except InvalidFileFormatError as invalid_file:
            self.file = False

            return {
                'warning': {
                    'title': _("Wait a minute! 👮"),
                    'message': _(
                        "\nActually only MP3 files are allowed. Don't f*ck the system! \n%s.", invalid_file
                    )
                }
            }

    @api.onchange('url')
    def _validate_url_path(self):
        self.ensure_one()
        if not (self.url and isinstance(self.url, str)):
            return None

        parsed_url = urlparse(self.url)

        if not (parsed_url.netloc.endswith('youtube.com') or parsed_url.netloc.endswith('youtu.be')):
            return {
                'warning': {
                    'title': _("C'mon dude! 🙄"),
                    'message': _("\nThe web address has to be valid and we both know it is not.")
                }
            }

        return None

    def action_back(self):
        self.ensure_one()

        states: List[Literal['start', 'uploaded', 'metadata', 'done']] = ['start', 'uploaded', 'metadata', 'done']
        current_index = states.index(self.state)

        if current_index > 0:
            self.state = states[current_index - 1]

        return {
            'name': _("Track Wizard"),
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.track_wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_next(self):
        self.ensure_one()

        match self.state:
            case 'start':
                self._reset_fields()
                self.state = 'uploaded'

                if self.url:
                    self._download_file()

                self._update_fields()

            case 'uploaded':
                self.state = 'metadata'

            case 'metadata':
                self.state = 'done'

        return {
            'name': _("Track Wizard"),
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.track_wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }

    def match_all_metadata(self) -> None:
        self._match_album_id()
        self._match_album_artist_id()
        self._match_artist_ids()
        self._match_genre_id()
        self._match_original_artist_id()
        self._match_track_year()

    def save_file(self):
        self.ensure_one()
        self._ensure_optional_fields()

        file_service = self._get_file_service_adapter()

        if not (isinstance(self.file, bytes) and self.has_valid_path):
            return None

        song = base64_decode(self.file)

        try:
            self._check_already_exists()
            file_service.save_file(str(self.file_path), song)

            # ⬇️ HERE creates a new TRACK record ⬇️
            track_info = self._create_new_track_record()

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

        if not track_info:
            return None

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Music Manager says:"),
                'message': _("Nice! Your new song '%s' has been added into the library.", track_info['name']),
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'music_manager.track',
                    'res_id': track_info['id'],
                    'name': _('New Track'),
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'target': 'current',
                },
            }
        }

    def _download_file(self) -> None:
        self.ensure_one()
        if not (self.url and isinstance(self.url, str)):
            return

        try:
            download_service = self._get_download_service_adapter(self.url)
            bytes_file = download_service.to_buffer()

            self.write(
                {
                    'url': False,
                    'file': base64_encode(bytes_file)
                }
            )

        except ClientPlatformError as download_error:
            _logger.error(f"Failed to process YouTube URL '{self.url}': {download_error}")
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
            _logger.error(f"Unexpected error while processing video URL '{self.url}': {unknown_error}")
            raise ValidationError(
                _("\nDamn! Something went wrong while validating URL.\nPlease, contact with your Admin.")
            )

    def _create_new_track_record(self):
        self.ensure_one()

        track_vals = {
            'picture': self.picture,
            'disk_no': self.tmp_disk_no,
            'name': self.tmp_name,
            'total_disk': self.tmp_total_disk,
            'total_track': self.tmp_total_track,
            'track_no': self.tmp_track_no,
            'year': self.year,
            'album_artist_id': self.possible_album_artist_id.id,
            'album_id': self.possible_album_id.id,
            'genre_id': self.possible_genre_id.id,
            'original_artist_id': self.possible_original_artist_id.id,
            'track_artist_ids': getattr(self.possible_artist_ids, 'ids', []),
            'compilation': self.tmp_compilation,
            'file_path': self.file_path,
            'old_path': self.file_path,
            'is_saved': True,
            'bitrate': self.bitrate,
            'channels': self.channels,
            'codec': self.codec,
            'duration': self.duration,
            'mime_type': self.mime_type,
            'sample_rate': self.sample_rate,
        }

        track = self.env['music_manager.track'].create(track_vals)

        # noinspection PyProtectedMember
        track._update_metadata()

        return {'id': track.id, 'name': track.name} if track else None

    def _check_already_exists(self) -> None:
        self.ensure_one()

        if not self.possible_album_id or not self.possible_album_artist_id:
            return

        domain = [
            ('album_id', '=', self.possible_album_id.id),
            ('album_artist_id', '=', self.possible_album_artist_id.id),
            ('track_no', '=', self.tmp_track_no),
            ('disk_no', '=', self.tmp_disk_no),
        ]

        if self.env['music_manager.track'].search_count(domain) > 0:
            raise ValidationError(_("\nThis track number already exists on this disk."))

    def _ensure_optional_fields(self):
        self.ensure_one()

        protected_fields = [
            ('possible_artist_ids', _("Track artist(s)")),
            ('possible_genre_id', _("Genre")),
            ('possible_original_artist_id', _("Original artist")),
            ('year', _("Year")),
        ]

        for field, label in protected_fields:
            value = getattr(self, field, None)

            if not value:
                raise ValidationError(
                    _("Field '%s' cannot be empty. Please fill it or restore previous value.", label)
                )

    def _find_or_create_single_artist(self, artist_name, fallback_artists):
        if not artist_name or artist_name.lower() == 'unknown':
            return fallback_artists[:1]

        artist_model = self.env['music_manager.artist']
        artist = artist_model.search([('name', '=', artist_name)], limit=1)

        if artist:
            return artist

        return artist_model.create({'name': artist_name})

    def _get_download_service_adapter(self, video_url):
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
        self.ensure_one()
        album_model = self.env['music_manager.album']

        self.possible_album_id = False

        if not self.tmp_album:
            _logger.info(f"There is no TMP ALBUM: {self.tmp_album}")
            return

        found = album_model.search([('name', '=', self.tmp_album)], limit=1)
        self.possible_album_id = found

    def _match_album_artist_id(self) -> None:
        self.ensure_one()
        artist_model = self.env['music_manager.artist']

        self.possible_album_artist_id = False

        if not self.tmp_album_artist:
            _logger.info(f"There is no TMP ALBUM ARTIST: {self.tmp_album}")
            return

        found = artist_model.search([('name', '=', self.tmp_album_artist)], limit=1)
        self.possible_album_artist_id = found

    def _match_artist_ids(self) -> None:
        self.ensure_one()
        artist_model = self.env['music_manager.artist']

        self.possible_artist_ids = artist_model.browse()

        if not self.tmp_artists:
            _logger.info(f"There is no TMP ARTISTS: {self.tmp_album}")
            return

        names = [name.strip() for name in self.tmp_artists.split(",")]
        found_artists = artist_model.search([('name', 'in', names)])

        self.possible_artist_ids = found_artists

    def _match_genre_id(self) -> None:
        self.ensure_one()
        genre_model = self.env['music_manager.genre']

        self.possible_genre_id = False

        if not self.tmp_genre:
            return

        found = genre_model.search([('name', '=', self.tmp_genre)], limit=1)
        self.possible_genre_id = found

    def _match_original_artist_id(self) -> None:
        self.ensure_one()
        artist_model = self.env['music_manager.artist']

        self.possible_original_artist_id = False

        if not self.tmp_original_artist:
            return

        found = artist_model.search([('name', '=', self.tmp_original_artist)], limit=1)
        self.possible_original_artist_id = found

    def _match_track_year(self) -> None:
        self.ensure_one()
        self.year = False

        if not self.tmp_year:
            return

        allowed_years = [year[0] for year in get_years_list()]

        if self.tmp_year in allowed_years:
            self.year = self.tmp_year

    def _update_fields(self) -> None:
        self.ensure_one()

        if isinstance(self.file, bytes):
            track_service = self._get_track_service_adapter()
            audio_info = track_service.read_audio_info(self.file)

            for attr_name, value in audio_info.items():
                if hasattr(self, attr_name):
                    setattr(self, attr_name, value)

        self.match_all_metadata()

    def _reset_fields(self) -> None:
        self.ensure_one()

        # Fields with temporary metadata
        self.tmp_album = False
        self.tmp_album_artist = False
        self.tmp_artists = False
        self.tmp_disk_no = 0
        self.tmp_genre = False
        self.tmp_name = False
        self.tmp_original_artist = False
        self.tmp_track_no = 0
        self.tmp_year = False

        # Relational fields (Matched)
        self.possible_album_id = False
        self.possible_album_artist_id = False
        self.possible_artist_ids = self.env['music_manager.artist'].browse()  # Clean Many2many
        self.possible_genre_id = False
        self.possible_original_artist_id = False

        # Technical audio metadata
        self.bitrate = 0
        self.duration = 0
        self.year = False

    @staticmethod
    def _get_years_list():
        return get_years_list()
