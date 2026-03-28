# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import AccessError, UserError
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Html, Integer, Many2many, Many2one, One2many, Selection

from .mixins.process_image_mixin import ProcessImageMixin
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
    def create(self, list_vals):
        for vals in list_vals:
            self._process_picture_image(vals)

        return super().create(list_vals)

    def write(self, vals):
        for artist in self:
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if artist.custom_owner_id != self.env.user:
                    raise AccessError(_("\nCannot update this artist because you are not the owner. 🤷"))

        self._process_picture_image(vals)

        return super().write(vals)  # type: ignore[arg-type]

    def unlink(self):
        for artist in self:
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if artist.custom_owner_id != self.env.user:
                    raise AccessError(_("\nCannot delete '%s' artist because you are not the owner. 🤷", artist.name))

        track_model = self.env['music_manager.track'].sudo()
        album_model = self.env['music_manager.album'].sudo()

        related_tracks = track_model.search_count([
                '|', '|',
                ('original_artist_id', 'in', self.ids),
                ('album_artist_id', 'in', self.ids),
                ('track_artist_ids', 'in', self.ids)
            ], limit=1)
        related_albums = album_model.search_count([('album_artist_id', 'in', self.ids)], limit=1)

        if related_tracks > 0 or related_albums > 0:
            raise UserError(_("\nArtist(s) cannot be deleted as they are still in use. 🤷"))

        return super().unlink()

    @api.depends('name', 'start_year', 'country_id')
    def _compute_display_name(self) -> None:
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
        album_model = self.env['music_manager.album']

        total_albums = album_model.read_group(
            domain=[('album_artist_id', 'in', self.ids)],
            fields=['album_artist_id'],
            groupby=['album_artist_id'],
        )

        mapped_data = {
            result['album_artist_id'][0]: result['album_artist_id_count'] for result in total_albums if result.get('album_artist_id')
        }

        for artist in self:
            artist.album_amount = mapped_data.get(artist.id, 0)

    @api.depends('name')
    def _compute_display_title_form(self) -> None:
        for artist in self:
            if not artist.id:
                artist.display_title = _("New artist")

            else:
                artist.display_title = _("Artist - %s", artist.name)

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        # noinspection PyProtectedMember
        track_field = self.env['music_manager.track']._fields['track_artist_ids']

        m2m_table = track_field.relation
        col_track = track_field.column1
        col_artist = track_field.column2

        query = f"""
            SELECT {col_artist}, COUNT({col_track})
            FROM {m2m_table}
            WHERE {col_artist} IN %s
            GROUP BY {col_artist}
        """

        self.env.cr.execute(query, (tuple(self.ids), ))

        mapped_data = dict(self.env.cr.fetchall())

        for artist in self:
            artist.track_amount = mapped_data.get(artist.id, 0)

    def action_view_artist_tracks(self):
        self.ensure_one()
        return {
            'name': _("Tracks of %s", self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.track',
            'view_mode': 'tree,form',
            'domain': ['|', ('original_artist_id', '=', self.id), ('track_artist_ids', 'in', self.ids)],
            'context': {'default_original_artist_id': self.id},
        }

    def action_view_artist_albums(self):
        self.ensure_one()
        return {
            'name': _("Albums of %s", self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.album',
            'view_mode': 'tree,form',
            'domain': [('album_artist_id', '=', self.id)],
            'context': {'default_album_artist_id': self.id},
        }

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
