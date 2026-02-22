# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _, api
from odoo.models import Model
from odoo.fields import Binary, Boolean, Char, Integer, Many2many, Many2one, One2many, Selection

from .mixins.process_image_mixin import ProcessImageMixin
from ..utils.file_utils import get_years_list


_logger = logging.getLogger(__name__)


class Album(Model, ProcessImageMixin):
    _name = 'music_manager.album'
    _description = 'album_table'
    _order = 'is_complete desc, name'

    # Basic fields
    name = Char(string=_("Album title"), required=True)

    # Relational fields
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
    track_ids = One2many(comodel_name='music_manager.track', inverse_name='album_id', string=_("Tracks"))

    # Computed fields
    album_type = Selection(
        string=_("Album type"),
        selection=[
            ('album', _("Album")),
            ('compilation', _("Compilation")),
            ('ep', _("EP")),
            ('single', _("Single")),
        ],
        compute='_compute_album_type',
        default='album',
        store=True,
    )
    disk_amount = Integer(string=_("Disk amount"), compute='_compute_disk_amount', store=False)
    display_duration = Char(string=_("Duration (min)"), compute='_compute_display_duration', store=False, readonly=True)
    duration = Integer(string=_("Duration (sec)"), compute='_compute_disk_duration', store=False)
    is_complete = Boolean(
        string=_("Album complete"), compute='_compute_is_complete', store=True, readonly=True, default=False
    )
    picture = Binary(
        string=_("Picture"),
        compute='_compute_album_picture',
        inverse='_inverse_album_picture',
        store=False,
    )
    progress = Integer(string=_("Progress"), compute='_compute_album_progress', default=0, readonly=True, store=False)
    track_amount = Integer(string=_("Track amount"), compute='_compute_track_amount', default=0)
    year = Selection(
        string=_("Debut year"),
        selection='_get_years_list',
        compute='_compute_album_year',
        inverse='_inverse_album_year',
        store=True,
    )

    # Techincal fields
    owner_ids = Many2many(comodel_name='res.users', string=_("Owners"), compute='_compute_album_owners', store=True)
    all_track_ids = Many2many(comodel_name='music_manager.track', string=_("All tracks"), compute='_compute_all_track_ids')

    @api.model_create_multi
    def create(self, list_vals):
        for vals in list_vals:
            self._process_picture_image(vals)

        # noinspection PyNoneFunctionAssignment
        albums = super().create(list_vals)

        for album in albums:  # type:ignore
            if album.track_ids:
                update_vals = {}

                if album.genre_id:
                    update_vals['genre_id'] = album.genre_id.id

                if album.album_artist_id:
                    update_vals['album_artist_id'] = album.album_artist_id.id

                if update_vals:
                    album.track_ids.write(update_vals)

        return albums

    def write(self, vals):
        self._process_picture_image(vals)

        res = super().write(vals)

        for album in self:  # type: ignore
            update_vals = {}

            if 'genre_id' in vals:
                update_vals['genre_id'] = vals['genre_id']

            if 'album_artist_id' in vals:
                update_vals['album_artist_id'] = vals['album_artist_id']

            if update_vals and album.track_ids:
                album.track_ids.write(update_vals)

        return res

    def unlink(self):
        if self.env.context.get('skip_album_sync'):
            return super().unlink()

        tracks_to_delete = self.mapped('track_ids').filtered(lambda track: track.owner.id == self.env.user.id)

        if tracks_to_delete:
            tracks_to_delete.unlink()

        empty_albums = self.exists().filtered(lambda act_album: not act_album.track_ids)

        if empty_albums:
            return super(Album, empty_albums.with_context(skip_album_sync=True)).sudo().unlink()

        return True

    @api.depends()
    def _compute_album_progress(self) -> None:
        for album in self:
            if not album.track_ids:
                album.progress = 0
                continue

            max_track_per_disk = {}

            for track in album.track_ids:
                disk_no = track.disk_no
                total_track = track.total_track

                if disk_no not in max_track_per_disk or total_track > max_track_per_disk[disk_no]:
                    max_track_per_disk[disk_no] = total_track

            total_album_tracks = sum(max_track_per_disk.values())
            total_real = len(album.track_ids)

            if total_album_tracks > 0:
                percentage = (total_real / total_album_tracks) * 100
                album.progress = min(int(percentage), 100)

            else:
                album.progress = 0

    @api.depends('name', 'album_type', 'album_artist_id')
    def _compute_display_name(self):
        album_categories = dict(self._fields['album_type']._description_selection(self.env))

        for album in self:
            if not album.is_complete:
                album.display_name = album.name
                continue

            name = album.name
            album_type_label = album_categories.get(album.album_type, "")

            if album.album_type == 'album' or album.album_type == 'compilation':
                album_type_label = ""

            else:
                album_type_label = f" ({album_type_label})"

            artist_name = album.album_artist_id.name if album.album_artist_id else ""
            artist_label = _(" · By %(artist_name)s", artist_name=artist_name) if artist_name else ""

            album.display_name = f"{name}{album_type_label}{artist_label}"

    @api.depends('track_ids.owner')
    def _compute_album_owners(self) -> None:
        for album in self:
            album.owner_ids = album.track_ids.mapped('owner')

    @api.depends('track_ids', 'track_ids.compilation', 'track_ids.duration', 'track_amount', 'duration')
    def _compute_album_type(self) -> None:
        for album in self:
            trck_dur = album.track_ids.mapped('duration')
            total_trck = album.track_amount
            album_dur = album.duration

            if any(album.track_ids.mapped('compilation')):
                album.album_type = 'compilation'

            elif (total_trck >= 7) or (total_trck < 7 and album_dur > 1800):
                album.album_type = 'album'

            elif (4 <= total_trck <= 6 and album_dur < 1800) or (1 <= total_trck <= 3 and any(map(lambda dur: dur > 600, trck_dur))):
                album.album_type = 'ep'

            elif (1 <= total_trck <= 3 and album_dur < 1800) or (any(map(lambda dur: dur > 600, trck_dur))):
                album.album_type = 'single'

    @api.depends('track_ids')
    def _compute_all_track_ids(self) -> None:
        for album in self:
            all_tracks = self.env['music_manager.track'].sudo().search([
                ('album_id', '=', album.id)
            ])
            album.all_track_ids = all_tracks

    @api.depends(
        'track_ids', 'track_ids.track_no', 'track_ids.disk_no', 'track_ids.total_track', 'track_ids.total_disk'
    )
    def _compute_is_complete(self) -> None:
        for album in self:
            if not album.track_ids:
                album.is_complete = False
                continue

            total_expected_disks = max(album.track_ids.mapped('total_disk'))
            max_track_per_disk = {}

            for track in album.track_ids:
                disk_no = track.disk_no
                total_track = track.total_track

                if disk_no not in max_track_per_disk or total_track > max_track_per_disk[disk_no]:
                    max_track_per_disk[disk_no] = total_track

            total_album_tracks = sum(max_track_per_disk.values())

            has_all_disks = len(max_track_per_disk) == total_expected_disks
            match_track_amount = len(album.track_ids) == total_album_tracks

            album.is_complete = has_all_disks and match_track_amount

    @api.depends('track_ids')
    def _compute_track_amount(self) -> None:
        for album in self:
            album.track_amount = len(album.track_ids) if album.track_ids else 0

    @api.depends('track_ids.total_disk')
    def _compute_disk_amount(self) -> None:
        for album in self:
            disk_amount = album.track_ids.mapped('total_disk')
            album.disk_amount = max(disk_amount) if disk_amount else 0

    @api.depends('track_ids.duration')
    def _compute_disk_duration(self) -> None:
        for album in self:
            disk_duration = album.track_ids.mapped('duration')
            album.duration = sum(disk_duration) if disk_duration else 0

    @api.depends('duration')
    def _compute_display_duration(self) -> None:
        for album in self:
            hours, remainder = divmod(album.duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            album.display_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

    @api.depends('track_ids.picture')
    def _compute_album_picture(self) -> None:
        for album in self:
            tracks_with_pic = album.track_ids.filtered(lambda track: track.picture)

            if tracks_with_pic:
                album.picture = tracks_with_pic[0].picture

            else:
                album.picture = False

    def _inverse_album_picture(self) -> None:
        for album in self:
            album.track_ids.write({'picture': album.picture})

    @api.depends('track_ids.year')
    def _compute_album_year(self) -> None:
        for album in self:
            tracks_with_year = album.track_ids.filtered(lambda track: track.year)

            if tracks_with_year:
                album.year = tracks_with_year[0].year

            else:
                album.year = False

    def _inverse_album_year(self) -> None:
        for album in self:
            album.track_ids.write({'year': album.year})

    def update_songs(self):
        self.ensure_one()

        if not self.track_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Music Manager says:"),
                    'message': _("This album has not any tracks to update!"),
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
                _("All tracks from this album have been updated!")
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
