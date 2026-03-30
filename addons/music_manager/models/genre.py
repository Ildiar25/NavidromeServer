# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import AccessError, UserError
from odoo.models import Model
from odoo.fields import Binary, Char, Html, Integer, Many2one, One2many

from .mixins.process_image_mixin import ProcessImageMixin


class Genre(Model, ProcessImageMixin):
    _name = 'music_manager.genre'
    _description = 'genre_table'
    _parent_name = "parent_id"
    _parent_store = True
    _order = 'complete_name'
    _rec_name = 'complete_name'
    _sql_constraints = [
        ('check_genre_name', 'UNIQUE(name)', _("Genre name must be unique.")),
    ]

    # Default fields
    description = Html(string=_("Description"))
    name = Char(string=_("Name"), required=True)
    parent_path = Char(string=_("Parent path"), index=True, unaccent=False)
    picture = Binary(string=_("Picture"))

    # Relationships
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='genre_id', string=_("Album(s)"))
    parent_id = Many2one(comodel_name='music_manager.genre', string=_("Parent genre"), index=True, ondelete='cascade')
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='genre_id', string=_("Track(s)"))

    # Computed fields
    complete_name = Char(string=_("Full hierarchy"), compute='_compute_complete_name', recursive=True, store=True)
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', default=0)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)

    # Technical fields
    custom_owner_id = Many2one(
        comodel_name='res.users',
        string="Owner",
        default=lambda self: self.env.user,
        required=True
    )

    @api.model_create_multi
    def create(self, list_vals):
        for vals in list_vals:
            self._process_picture_image(vals)

        return super().create(list_vals)

    def write(self, vals):
        for genre in self:
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if genre.custom_owner_id != self.env.user:
                    raise AccessError(_("\nCannot update this genre because you are not the owner. 🤷"))

        self._process_picture_image(vals)

        return super().write(vals)  # type: ignore[arg-type]

    def unlink(self):
        for genre in self:
            if not self.env.user.has_group('music_manager.group_music_manager_user_admin'):
                if genre.custom_owner_id != self.env.user:
                    raise AccessError(_("\nCannot delete '%s' genre because you are not the owner. 🤷", genre.name))

        track_model = self.env['music_manager.track'].sudo()
        album_model = self.env['music_manager.album'].sudo()

        related_tracks = track_model.search_count([('genre_id', 'in', self.ids)], limit=1)
        related_albums = album_model.search_count([('genre_id', 'in', self.ids)], limit=1)

        if related_tracks > 0 or related_albums > 0:
            raise UserError(_("\nGenre(s) cannot be deleted as they are still in use. 🤷"))

        return super().unlink()

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self) -> None:
        for genre in self:
            if genre.parent_id:
                genre.complete_name = f"{genre.parent_id.complete_name} · {genre.name}"

            else:
                genre.complete_name = genre.name

    @api.depends('album_ids')
    def _compute_disk_amount(self) -> None:
        album_model = self.env['music_manager.album']

        total_albums = album_model.read_group(
            domain=[('genre_id', 'in', self.ids)],
            fields=['genre_id'],
            groupby=['genre_id'],
        )

        mapped_data = {
            result['genre_id'][0]: result['genre_id_count'] for result in total_albums if result.get('genre_id')
        }

        for genre in self:
            genre.disk_amount = mapped_data.get(genre.id, 0)

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        track_model = self.env['music_manager.track']

        total_tracks = track_model.read_group(
            domain=[('genre_id', 'in', self.ids)],
            fields=['genre_id'],
            groupby=['genre_id'],
        )

        mapped_data = {
            result['genre_id'][0]: result['genre_id_count'] for result in total_tracks if result.get('genre_id')
        }

        for genre in self:
            genre.track_amount = mapped_data.get(genre.id, 0)

    def action_view_genre_albums(self):
        self.ensure_one()
        return {
            'name': _("Albums of %s", self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.album',
            'view_mode': 'tree,form',
            'domain': [('genre_id', 'child_of', self.id)],
            'context': {'default_genre_id': self.id},
        }

    def action_view_genre_tracks(self):
        self.ensure_one()
        return {
            'name': _("Tracks of %s", self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'music_manager.track',
            'view_mode': 'tree,form',
            'domain': [('genre_id', 'child_of', self.id)],
            'context': {'default_genre_id': self.id},
        }

    def update_songs(self):
        self.ensure_one()

        if not self.track_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Music Manager says:"),
                    'message': _("This genre has not any tracks to update!"),
                    'type': 'info',
                    'sticky': False,
                }
            }

        total_success_count = 0
        total_failure_messages = []

        for track in self.track_ids:
            # noinspection PyProtectedMember
            results = track._perform_save_changes()
            total_success_count += results['success']

            if results['messages']:
                total_failure_messages.extend(results['messages'])

        final_message = []

        if total_success_count == len(self.track_ids):
            final_message.append(
                _("All tracks from this genre have been updated!")
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
