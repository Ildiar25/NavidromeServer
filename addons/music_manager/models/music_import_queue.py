# -*- coding: utf-8 -*-
import logging
import traceback
from datetime import timedelta
from typing import Dict

# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Char, Datetime, Selection, Text

from ..adapters.file_service_adapter import FileServiceAdapter
from ..adapters.track_service_adapter import TrackServiceAdapter
from ..utils.data_encoding import base64_encode_in_bytes
from ..utils.file_utils import get_years_list


_logger = logging.getLogger(__name__)


class MusicImportQueue(Model):
    _name = 'music_manager.music_import_queue'
    _description = 'music_import_queue_table'

    # Basic fields
    error_message = Text(string=_("Error message"))
    file_path = Char(string=_("File path"), required=True)
    state = Selection(
        string=_("State"),
        selection=[
            ('pending', _("Pending")),
            ('processed', _("Processed")),
            ('error', _("Error")),
        ],
        default='pending'
    )

    @api.model
    def _cron_process_music_queue(self) -> None:
        settings = self.env['music_manager.audio_settings'].search([], limit=1)

        root = settings.root_dir if settings else '/music'
        file_extension = settings.sound_format if settings else 'mp3'

        files = self.search([('state', '=', 'pending')], limit=50)

        file_service = FileServiceAdapter(root, file_extension)
        track_service = TrackServiceAdapter(file_extension)

        for music_file in files:
            try:
                file_bytes = file_service.read_file(music_file.file_path)
                track_data = track_service.read_audio_info(base64_encode_in_bytes(file_bytes))

                self.create_track_from_scan(music_file.file_path, track_data)

                music_file.state = 'processed'
                self.env.cr.commit()

            except Exception as unknown_error:

                traceback_error = traceback.format_exc()
                _logger.error(traceback_error)

                self.env.cr.rollback()
                music_file.write({'state': 'error', 'error_message': f"Message: {str(unknown_error)}"})

    @api.model
    def _cron_garbage_collector(self) -> None:
        limit = Datetime.now() - timedelta(hours=24)
        records_to_delete = self.search(
            [('state', '=', 'processed'), ('write_date', '<', limit)]
            , limit=1)

        if records_to_delete:
            records_to_delete.unlink()

    def create_track_from_scan(self, file_path: str, data: Dict[str, str | int | None]) -> None:

        _logger.info(f"Path: {file_path}")
        _logger.info(f"Dictionari received: {data}")
        album_artist_id = self._match_artist_id(data['tmp_album_artist'])

        _logger.info(f"Album Artist ID: {album_artist_id}")

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
        _logger.info("|||| MATCH ALBUM ID ||||")
        album_id = self.env['music_manager.album'].search(
            [('name', '=', album_name), ('album_artist_id', '=', album_artist_id)],
            limit=1
        )

        if not album_id:
            album_id = self.env['music_manager.album'].create({
                'name': album_name,
                'album_artist_id': album_artist_id,
            })
        _logger.info(f"Album ID: {album_id} | Album name: {album_id.name}")
        return album_id.id

    def _match_artist_id(self, artist_name: str):
        _logger.info("|||| MATCH ARTIST ID ||||")
        artist_id = self.env['music_manager.artist'].search([('name', '=', artist_name)], limit=1)

        if not artist_id:
            artist_id = self.env['music_manager.artist'].create({
                'name': artist_name,
            })
        _logger.info(f"Artist ID: {artist_id} | Artist name: {artist_id.name}")
        return artist_id.id

    def _match_various_artists_ids(self, artist_names: str):
        _logger.info("|||| MATCH VARIOUS ARTISTS ID ||||")
        names = [name.strip() for name in artist_names.split(",")]
        artist_ids = []

        _logger.info(f"Names founded: {names}")
        for name in names:
            found = self.env['music_manager.artist'].search([('name', '=', name)], limit=1)

            if not found:
                new_artist = self.env['music_manager.artist'].create({
                    'name': name,
                })
                artist_ids.append(new_artist.id)
                _logger.info(f"Artist ID Created: {new_artist} | Artist name: {new_artist.name}")
                continue

            _logger.info(f"Artist ID Founded: {found} | Artist name: {found.name}")
            artist_ids.append(found.id)

        _logger.info(f"Artist IDS: {artist_ids}")
        return artist_ids

    def _match_genre_id(self, genre_name: str):
        _logger.info("|||| MATCH GENRE ID ||||")
        genre_id = self.env['music_manager.genre'].search([('name', '=', genre_name)], limit=1)

        if not genre_id:
            genre_id = self.env['music_manager.genre'].create({
                'name': genre_name,
            })
        _logger.info(f"Genre ID: {genre_id} | Genre name: {genre_id.name}")
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
