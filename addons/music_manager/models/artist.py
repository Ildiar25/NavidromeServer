# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import AccessError, UserError
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Date, Html, Integer, Many2many, Many2one, One2many, Selection, Text

from .mixins.process_image_mixin import ProcessImageMixin
from ..utils.custom_types import ArtistVals
from ..utils.file_utils import get_years_list


_logger = logging.getLogger(__name__)


class Artist(Model, ProcessImageMixin):
    _name = 'music_manager.artist'
    _description = 'artist_table'
    _order = 'is_group, name'

    # Basic fields
    biography = Html(string=_("Biography"))
    is_group = Boolean(string=_("Is group"))
    name = Char(string=_("Name"), required=True)
    picture = Binary(string=_("Picture"))
    real_name = Char(string=_("Real name"))
    start_year = Selection(string=_("Artist year"), selection='_get_years_list')
    website = Char(string=_("Website"))

    # Relational fields
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='album_artist_id', string=_("Album(s)"))
    country_id = Many2one(comodel_name='res.country', string=_("Country"))
    group_ids = Many2many(
        comodel_name='music_manager.artist',
        relation='music_manager_artist_relatives',
        column1='child_id',
        column2='parent_id',
        string=_("Music groups"),
        readonly=True,
    )
    member_ids = Many2many(
        comodel_name='music_manager.artist',
        relation='music_manager_artist_relatives',
        column1='parent_id',
        column2='child_id',
        string=_("Members")
    )
    track_ids = Many2many(comodel_name='music_manager.track', string=_("Track(s)"))

    # Computed fields
    album_amount = Integer(string=_("Album amount"), compute='_compute_album_amount', default=0, store=False)
    display_title = Char(string=_("Display title"), compute='_compute_display_title_form', store=True)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0, store=False)

    # Related fields
    country_code = Char(related='country_id.code', string=_("Country code"))

    # Technical fields
    custom_owner_id = Many2one(comodel_name='res.users', string="Owner", default=lambda self: self.env.user, required=True)

    @api.model_create_multi
    def create(self, list_vals: list[ArtistVals]):
        for vals in list_vals:
            self._process_picture_image(vals)

        return super().create(list_vals)

    def write(self, vals: ArtistVals):
        for artist in self:  # type:ignore
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if artist.custom_owner_id != self.env.user:
                    raise AccessError(_("\nCannot update this artist because you are not the owner. 🤷"))

        self._process_picture_image(vals)

        return super().write(vals)

    def unlink(self):
        for artist in self:  # type:ignore
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if artist.custom_owner_id != self.env.user:
                    raise AccessError(_("\nCannot delete this artist because you are not the owner. 🤷"))

                related_track = self.env['music_manager.track'].sudo().search(
                    [('original_artist_id', '=', artist.id)], limit=1
                )
                related_album = self.env['music_manager.album'].sudo().search(
                    [('album_artist_id', '=', artist.id)], limit=1
                )

                if related_track or related_album:
                    raise UserError(_("\nCannot delete this artist because it is in use by other users. 🤷"))

        return super().unlink()

    @api.depends('name', 'start_year', 'country_id')
    def _compute_display_name(self):
        for artist in self:
            name = artist.name
            data = []

            if artist.start_year:
                data.append(artist.start_year)

            if artist.country_id:
                data.append(artist.country_id.code)

            suffix = f" ({' · '.join(data)})" if data else ""
            artist.display_name = f"{name}{suffix}"

    @api.depends('album_ids')
    def _compute_album_amount(self) -> None:
        for artist in self:
            artist.album_amount = len(artist.album_ids) if artist.album_ids else 0

    @api.depends('name')
    def _compute_display_title_form(self) -> None:
        for artist in self:
            if not artist.id:
                artist.display_title = _("New artist")

            else:
                artist.display_title = _("Artist - %s", artist.name)

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for artist in self:
            artist.track_amount = len(artist.track_ids) if artist.track_ids else 0

    def update_songs(self):
        self.ensure_one()

        if not self.track_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Music Manager says:"),
                    'message': _("This artist has not any tracks to update!"),
                    'type': 'info',
                    'sticky': False,
                }
            }

        total_success_count = 0
        total_failure_messages = []

        for track in self.track_ids:
            results = track._perform_save_changes()
            total_success_count += results['success']

            if results['messages']:
                total_failure_messages.extend(results['messages'])

        final_message = []

        if total_success_count == len(self.track_ids):
            final_message.append(
                _("All tracks from this artist have been updated!")
            )

        if total_failure_messages:
            final_message.append(
                _("Some tracks have been ignored:")
            )
            final_message.extend(total_failure_messages)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Music Manager says:"),
                'message': " • ".join(final_message),
                'type': 'warning' if total_failure_messages else 'success',
                'sticky': False,
            }
        }

    @staticmethod
    def _get_years_list():
        return get_years_list()
