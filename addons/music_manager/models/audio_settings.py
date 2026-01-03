from typing import Any, Dict

# noinspection PyProtectedMember
from odoo import _
from odoo.models import Model
from odoo.fields import Char, Integer, Selection


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
