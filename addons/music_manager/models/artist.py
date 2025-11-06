# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import UserError
from odoo.models import Model
from odoo.fields import Binary, Char, Date, Integer, Many2many, One2many, Text

from .mixins.process_image_mixin import ProcessImageMixin
from ..utils.custom_types import ArtistVals


_logger = logging.getLogger(__name__)


class Artist(Model, ProcessImageMixin):

    _name = 'music_manager.artist'
    _description = 'artist_table'
    _order = 'name'

    # Basic fields
    founded_in = Date(string=_("Founded in"))
    name = Char(string=_("Name"), required=True)
    picture = Binary(string=_("Profile"))
    real_name = Text(string=_("Real name"), compute='_compute_artist_name', readonly=False, store=True)

    # Relational fields
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='album_artist_id', string=_("Album(s)"))
    track_ids = Many2many(comodel_name='music_manager.track', string=_("Track(s)"))

    # Computed fields
    album_amount = Integer(string=_("Album amount"), compute='_compute_album_amount', default=0, store=False)
    display_title = Char(string=_("Display title"), compute='_compute_display_title_form', store=True)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0, store=False)

    @api.model_create_multi
    def create(self, list_vals: list[ArtistVals]):
        for vals in list_vals:
            self._process_picture_image(vals)

        return super().create(list_vals)

    def write(self, vals: ArtistVals):
        for artist in self:  # type:ignore
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if artist.create_uid != self.env.user:
                    raise UserError(_("\nCannot update this artist because you are not the owner. 🤷"))

        self._process_picture_image(vals)

        return super().write(vals)

    def unlink(self):
        for artist in self:  # type:ignore
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if artist.create_uid != self.env.user:
                    raise UserError(_("\nCannot delete this artist because you are not the owner. 🤷"))

                related_tracks = self.env['music_manager.track'].sudo().search(
                    [('original_artist_id', '=', artist.id)], limit=1
                )
                related_albums = self.env['music_manager.album'].sudo().search(
                    [('album_artist_id', '=', artist.id)], limit=1
                )

                if related_tracks or related_albums:
                    raise UserError(_("\nCannot delete this artist because it is in use by other users. 🤷"))

        return super().unlink()

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

    @api.depends('name')
    def _compute_artist_name(self) -> None:
        for artist in self:
            if isinstance(artist.name, str):
                artist.real_name = artist.name

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
