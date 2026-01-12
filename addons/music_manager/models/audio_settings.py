# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict

# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Boolean, Char, Integer, Selection

from ..adapters.file_service_adapter import FileServiceAdapter
from ..adapters.track_service_adapter import TrackServiceAdapter
from ..utils.custom_types import DisplayNotification
from ..utils.data_encoding import base64_encode_in_bytes
from ..utils.file_utils import get_years_list


_logger = logging.getLogger(__name__)


class AudioSettings(Model):
    _name = 'music_manager.audio_settings'
    _description = 'audio_settings_table'
    _rec_name = 'name'
    _sql_constraints = [
        ('single_record', 'UNIQUE(single_record)', _("Settings record already exists!")),
    ]

    # Basic fields
    available_adapters = Selection(
        selection=[
            ('pytube', _("PyTube")),
            ('ytdlp', _("YouTube DLP"))
        ],
        string=_("Available adapters"),
        default='ytdlp',
        required=True,
    )
    sound_format = Selection(
        selection=[
            ('mp3', _("MP3")),
        ],
        string=_("General sound format"),
        default='mp3',
        required=True,
    )
    bitrate = Selection(
        selection=[
            ('128', _("128 kbps")),
            ('192', _("192 kbps")),
            ('320', _("320 kbps")),
        ],
        string=_("Global bitrate"),
        default='192',
        required=True,
    )
    image_format = Selection(
        selection=[
            ('png', _("PNG")),
        ],
        string=_("General image format"),
        default='png',
        required=True,
    )
    image_size = Selection(
        selection=[
            ('300', _("300x300 px")),
            ('400', _("400x400 px")),
            ('600', _("600x600 px")),
            ('1000', _("1000x1000 px")),
        ],
        string=_("General image size"),
        default='400',
        required=True,
    )
    root_dir = Char(string="Root directory", default="/music", readonly=True, required=True)
    to_delete = Boolean(string=_("Delete files"), default=False, required=True)

    # Technical fields
    name = Char(string="", default=' ', readonly=True, required=True)
    single_record = Integer(string="", default=1, required=True)

    def action_open_settings(self) -> Dict[str, Any]:
        settings = self.search([], limit=1)

        if not settings:
            settings = self.sudo().create({})

        return {
            'type': 'ir.actions.act_window',
            'name': _("Audio Settings"),
            'res_model': 'music_manager.audio_settings',
            'view_mode': 'form',
            'res_id': settings.id,
            'target': 'current',
        }

    def action_read_root_folder(self):
        self.ensure_one()

        file_service = FileServiceAdapter(self.root_dir, self.sound_format)
        track_service = TrackServiceAdapter(self.sound_format)

        str_file_paths = [str(file_path) for file_path in file_service.get_all_file_paths()]

        if not str_file_paths:
            return self._notify_user(_("Root folder is empty, add some files first!"), 'info')

        track_records = self.env['music_manager.track'].search_read(
            [('file_path', 'in', str_file_paths)],
            ['file_path'],
        )

        existing_paths = [record['file_path'] for record in track_records]
        paths_to_process = [path for path in str_file_paths if path not in existing_paths]

        if not paths_to_process:
            return self._notify_user(_("All files are already in the library."), 'info')

        total = 0
        for str_path in paths_to_process:

            file_bytes = file_service.read_file(str_path)
            track_data = track_service.read_audio_info(base64_encode_in_bytes(file_bytes))

            self.create_track_from_scan(str_path, track_data)
            _logger.info(f"CREATED RECORDS FOR: {str_path}")
            total += 1

        return self._notify_user(
            _("Root folder scan finished! • %s new tracks added to the library.", total), 'success'
        )

    def create_track_from_scan(self, file_path: str, data: Dict[str, str | int | None]) -> None:

        album_artist_id = self._match_artist_id(data['tmp_album_artist'])

        self.env['music_manager.track'].create({
            'picture': data['picture'],
            'disk_no': data['tmp_disk_no'],
            'name': data['tmp_name'],
            'total_disk': data['tmp_total_disk'],
            'total_track': data['tmp_total_track'],
            'track_no': data['tmp_track_no'],
            'year': self._match_track_year(data['tmp_year']),
            'album_artist_id': album_artist_id,
            'album_id': self._match_album_id(data['tmp_album'], album_artist_id),
            'genre_id': self._match_genre_id(data['tmp_genre']),
            'original_artist_id': self._match_artist_id(data['tmp_original_artist']),
            'track_artist_ids': [(6, 0, self._match_various_artists_ids(data['tmp_artists']))],
            'collection': data['tmp_collection'],
            'file_path': file_path,
            'old_path': file_path,
            'is_saved': True,
            'bitrate': data['bitrate'],
            'channels': data['channels'],
            'codec': data['codec'],
            'duration': data['duration'],
            'mime_type': data['mime_type'],
            'sample_rate': data['sample_rate'],
        })

    def _match_album_id(self, album_name: str, album_artist_id: int):
        album_id = self.env['music_manager.album'].search(
            [('name', '=', album_name), ('album_artist_id', '=', album_artist_id)],
            limit=1
        )

        if not album_id:
            album_id = self.env['music_manager.album'].create({
                'name': album_name,
                'album_artist_id': album_artist_id,
            })

        return album_id.id

    def _match_artist_id(self, artist_name: str):
        artist_id = self.env['music_manager.artist'].search([('name', '=', artist_name)], limit=1)

        if not artist_id:
            artist_id = self.env['music_manager.artist'].create({
                'name': artist_name,
            })

        return artist_id.id

    def _match_various_artists_ids(self, artist_names: str):
        names = [name.strip() for name in artist_names.split(",")]
        artist_ids = []

        for name in names:
            found = self.env['music_manager.artist'].search([('name', '=', name)], limit=1)

            if not found:
                new_artist = self.env['music_manager.artist'].create({
                    'name': name,
                })
                artist_ids.append(new_artist.id)

                continue

            artist_ids.append(found.id)

        return artist_ids

    def _match_genre_id(self, genre_name: str):
        genre_id = self.env['music_manager.genre'].search([('name', '=', genre_name)], limit=1)

        if not genre_id:
            genre_id = self.env['music_manager.genre'].create({
                'name': genre_name,
            })

        return genre_id.id

    @staticmethod
    def _match_track_year(year: str):
        allowed_years = [year[0] for year in get_years_list()]

        if not isinstance(year, str):
            year = str(year)

        return year if year in allowed_years else ""

    @staticmethod
    def _get_years_list():
        return get_years_list()

    @staticmethod
    def _notify_user(message: str, style: str, sticky: bool = False) -> DisplayNotification:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Music Manager says:"),
                'message': message,
                'type': style,
                'sticky': sticky,
            }
        }
