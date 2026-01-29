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

        str_file_paths = [str(file_path) for file_path in file_service.get_all_file_paths()]

        if not str_file_paths:
            return self._notify_user(_("Root folder is empty, add some files first!"), 'info')

        existing_tracks = self.env['music_manager.track'].search_read(
            [('file_path', 'in', str_file_paths)], ['file_path']
        )
        existing_queue = self.env['music_manager.music_import_queue'].search_read(
            [('file_path', 'in', str_file_paths), ('state', 'in', ['pending', 'error'])], ['file_path']
        )

        processed_paths = {track['file_path'] for track in existing_tracks}
        pending_paths = {track['file_path'] for track in existing_queue}

        to_enqueue = [path for path in str_file_paths if path not in processed_paths and path not in pending_paths]

        if not to_enqueue:
            return self._notify_user(_("All files are already in the library."), 'info')

        self.env['music_manager.music_import_queue'].create(
            [{'file_path': path, 'state': 'pending'} for path in to_enqueue],
        )

        return self._notify_user(
            _("Root folder scan finished! • Found %s new files. Processing in background...", len(to_enqueue)),
            'success'
        )

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
