# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Boolean, Char, Integer, One2many, Many2one


class Genre(Model):

    _name = 'music_manager.genre'
    _description = 'genre_table'
    _order = 'to_delete, name'
    _sql_constraints = [
        ('check_genre_name', 'UNIQUE(name)', _("The genre name must be unique.")),
    ]

    # Default fields
    name = Char(string=_("Name"), required=True)
    to_delete = Boolean(string=_("To delete"), default=False)

    # Relationships
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='genre_id', string=_("Song(s)"))
    album_ids = One2many(comodel_name='music_manager.album', inverse_name='genre_id', string=_("Album(s)"))

    # Computed fields
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', default=0)

    # Technical fields
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user)

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for genre in self:
            genre.track_amount = len(genre.track_ids) if genre.track_ids else 0

    @api.depends('album_ids')
    def _compute_disk_amount(self) -> None:
        for genre in self:
            genre.disk_amount = len(genre.album_ids) if genre.album_ids else 0

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
                _("Some tracks has been ignored:")
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
