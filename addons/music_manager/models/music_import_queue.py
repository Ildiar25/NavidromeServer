# -*- coding: utf-8 -*-
import logging
import traceback
from datetime import timedelta

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
                music_file.write({
                    'state': 'error',
                    'error_message': _("Message: %s", str(unknown_error))
                })

    @api.model
    def _cron_garbage_collector(self) -> None:
        limit = Datetime.now() - timedelta(hours=24)
        records_to_delete = self.search([('state', '=', 'processed'), ('write_date', '<', limit)])

        if records_to_delete:
            records_to_delete.unlink()

    def create_track_from_scan(self, file_path, data) -> None:
        track_model = self.env['music_manager.track']

        found_year = self._match_track_year(data.get('tmp_year', ""))
        album_artist_id = self._match_artist_id(data.get('tmp_album_artist', "Unknown"))
        album_id = self._match_album_id(data.get('tmp_album', "Unknown"), album_artist_id)
        genre_id = self._match_genre_id(data.get('tmp_genre', "Unknown"))
        original_artist_id = self._match_artist_id(data.get('tmp_original_artist', "Unknown"))
        artist_ids = self._match_various_artists_ids(data.get('tmp_artists', "Unknown"))

        track_vals = {
            'picture': data.get('picture', False),
            'disk_no': data.get('tmp_disk_no', 1),
            'name': data.get('tmp_name', "Unknown"),
            'total_disk': data.get('tmp_total_disk', 1),
            'total_track': data.get('tmp_total_track', 1),
            'track_no': data.get('tmp_track_no', 1),
            'year': found_year,
            'album_artist_id': album_artist_id.id,
            'album_id': album_id.id,
            'genre_id': genre_id.id,
            'original_artist_id': original_artist_id.id,
            'track_artist_ids': getattr(artist_ids, 'ids', []),
            'compilation': data.get('tmp_compilation', False),
            'file_path': file_path,
            'old_path': file_path,
            'is_saved': True,
            'bitrate': data.get('bitrate', 0),
            'channels': data.get('channels', "Stereo"),
            'codec': data.get('codec', "Unknown"),
            'duration': data.get('duration', 0),
            'mime_type': data.get('mime_type', "Unknown"),
            'sample_rate': data.get('sample_rate', 0),
        }

        # ⬇️ HERE creates a new TRACK record ⬇️
        track_model.create(track_vals)

    def _match_album_id(self, album_name, album_artist):
        album_model = self.env['music_manager.album']
        found = album_model.search([('name', '=', album_name), ('album_artist_id', '=', album_artist.id)], limit=1)

        if not found:
            new_album = album_model.create({'name': album_name, 'album_artist_id': album_artist.id})
            return new_album

        return found

    def _match_artist_id(self, artist_name):
        artist_model = self.env['music_manager.artist']
        found = artist_model.search([('name', '=', artist_name)], limit=1)

        if not found:
            new_artist = artist_model.create({'name': artist_name})
            return new_artist

        return found

    def _match_various_artists_ids(self, artist_names):
        artist_model = self.env['music_manager.artist']

        names = [name.strip() for name in artist_names.split(",")]
        artist_ids = []

        for name in names:
            found = artist_model.search([('name', '=', name)], limit=1)

            if not found:
                new_artist = artist_model.create({'name': name,})
                artist_ids.append(new_artist.id)

                continue

            artist_ids.append(found.id)

        return artist_model.browse(artist_ids)

    def _match_genre_id(self, genre_name):
        genre_model = self.env['music_manager.genre']
        found = genre_model.search([('name', '=', genre_name)], limit=1)

        if not found:
            new_genre = genre_model.create({'name': genre_name})
            return new_genre

        return found

    @staticmethod
    def _match_track_year(year: str):
        allowed_years = [year[0] for year in get_years_list()]

        if not isinstance(year, str):
            year = str(year)

        return year if year in allowed_years else ""

    @staticmethod
    def _get_years_list():
        return get_years_list()
