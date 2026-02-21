# -*- coding: utf-8 -*-
import logging
from pathlib import Path

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Binary, Boolean, Char, Integer, Many2many, Many2one, Selection
from odoo.models import Model

from .mixins.process_image_mixin import ProcessImageMixin
from ..adapters import FileServiceAdapter, TrackServiceAdapter
from ..utils.exceptions import FilePersistenceError, MusicManagerError, InvalidPathError
from ..utils.file_utils import get_years_list


_logger = logging.getLogger(__name__)


class Track(Model, ProcessImageMixin):
    _name = 'music_manager.track'
    _description = 'track_table'
    _order = 'album_artist, album_name, disk_no, track_no'
    _sql_constraints = [
        ('unique_track_no', 'UNIQUE(album_id, disk_no, track_no)', _("This track number already exists in this disk.")),
    ]

    # Basic fields
    picture = Binary(string=_("Picture"), attachment=True)
    disk_no = Integer(string=_("Disk no"))
    name = Char(string=_("Title"), required=True)
    total_disk = Integer(string=_("Total disk no"))
    total_track = Integer(string=_("Total track no"))
    track_no = Integer(string=_("Track no"), required=True)
    year = Selection(string=_("Year"), selection='_get_years_list')

    # Readonly fields
    bitrate = Integer(string=_("Bitrate"), default=0, readonly=True)
    channels = Char(string=_("Channels"), default="Stereo", readonly=True)
    codec = Char(string=_("Codec"), default="Unknown", readonly=True)
    duration = Integer(string=_("Duration (sec)"), default=0, readonly=True)
    mime_type = Char(string=_("MIME"), default="Unknown", readonly=True)
    sample_rate = Integer(string=_("Sample rate"), default=0, readonly=True)

    # Relational fields
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"), copy=False, required=True)
    album_id = Many2one(comodel_name='music_manager.album', string=_("Album"), ondelete='cascade', required=True)
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
    original_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Original artist"))
    track_artist_ids = Many2many(comodel_name='music_manager.artist', string=_("Track artist(s)"))

    # Computed fields
    compilation = Boolean(
        string=_("Part of a compilation"),
        compute='_compute_compilation_value',
        inverse='_inverse_compilation_value',
        default=False,
    )
    display_artist_names = Char(string=_("Display artist names"), compute='_compute_display_artist_name', store=False)
    display_bitrate = Char(string=_("Display bitrate"), compute='_compute_display_bitrate', store=False)
    display_duration = Char(string=_("Display duration (min)"), compute='_compute_display_duration', store=False)
    display_sample_rate = Char(string=_("Display sample rate"), compute='_compute_display_sample_rate', store=False)
    is_deleted = Boolean(
        string=_("Is deleted"), compute='_compute_file_is_deleted', search='_search_is_deleted', store=False
    )
    file_path = Char(string=_("File path"), compute='_compute_file_path', store=True)
    old_path = Char(string=_("Old path"), copy=False, store=True)

    # Related fields
    album_name = Char(string="Album name", related='album_id.name', store=True)
    album_artist = Char(string="Album artist", related='album_artist_id.name', store=True)

    # Technical fields
    has_valid_path = Boolean(string=_("Valid path"), default=False, readonly=True)
    is_saved = Boolean(string=_("Is saved"), default=False, readonly=True)
    owner = Many2one(comodel_name='res.users', string="Owner", default=lambda self: self.env.user, required=True)

    @api.model_create_multi
    def create(self, list_vals):
        for vals in list_vals:
            self._process_picture_image(vals)

        tracks = super().create(list_vals)

        for track in tracks:
            # noinspection PyProtectedMember
            track._sync_album_with_artist()
            # noinspection PyProtectedMember
            track._sync_album_with_genre()

        return tracks

    def write(self, vals):
        self._process_picture_image(vals)

        res = super().write(vals)

        for track in self:
            if track.is_deleted:
                raise UserError(_("You cannot modify a deleted file."))
            # noinspection PyProtectedMember
            track._sync_album_with_artist()
            # noinspection PyProtectedMember
            track._sync_album_with_genre()
            # noinspection PyProtectedMember
            track._sync_album_with_owner()

        return res

    def unlink(self):
        settings = self.env['music_manager.audio_settings'].search([], limit=1)
        delete_files = settings.to_delete if settings else False
        file_service = self._get_file_service_adapter()

        # Check DB info
        files_to_check = [(track.file_path, track.is_deleted) for track in self]
        potential_empty_albums = self.mapped('album_id')

        # Delete track records
        res = super().unlink()

        # Look for empty albums
        tracks_still_in_db = self.env['music_manager.track'].sudo().search([
            ('album_id', 'in', potential_empty_albums.ids)
        ])

        album_ids_with_content = tracks_still_in_db.mapped('album_id').ids
        albums_to_delete = potential_empty_albums.filtered(lambda album: album.id not in album_ids_with_content)

        if albums_to_delete:
            albums_to_delete.sudo().with_context(skip_album_sync=True).unlink()

        if not delete_files:
            return res

        # File cleaning
        for path, is_deleted in files_to_check:
            if not path or is_deleted:
                continue

            still_used = self.env['music_manager.track'].sudo().search_count([('file_path', '=', path)])

            if still_used == 0:
                try:
                    file_service.delete_file(path)

                except InvalidPathError as invalid_path:
                    _logger.warning(f"File to delete not found, continuing: {invalid_path}")
                    continue

                except FilePersistenceError as not_allowed:
                    _logger.error(f"Cannot delete the file: {not_allowed}")
                    raise ValidationError(
                        _("\nAn internal issue ocurred while trying to delete the file."
                          "\nPlease, try it again with a different record.")
                    )

                except MusicManagerError as unknown_error:
                    _logger.error(f"Unespected error while trying to delete the file: {unknown_error}")
                    raise ValidationError(
                        _("\nDamn! Something went wrong while deleting the file."
                          "\nPlease, contact with your Admin.")
                    )

        return res

    @api.depends('track_artist_ids.name')
    def _compute_display_artist_name(self) -> None:
        for track in self:
            artist_names = track.track_artist_ids.mapped('name')
            track.display_artist_names = ", ".join(artist_names) if artist_names else ""

    @api.depends('bitrate')
    def _compute_display_bitrate(self):
        for track in self:
            track.display_bitrate = f"{track.bitrate} kbps"

    @api.depends('duration')
    def _compute_display_duration(self):
        for track in self:
            minutes, seconds = divmod(track.duration, 60)
            track.display_duration = f"{minutes:02}:{seconds:02}"

    @api.depends('sample_rate')
    def _compute_display_sample_rate(self):
        for track in self:
            track.display_sample_rate = f"{track.sample_rate} kHz"

    @api.depends('old_path')
    def _compute_file_is_deleted(self) -> None:
        for track in self:
            if track.old_path and isinstance(track.old_path, str):
                track.is_deleted = not track.file_exists(track.old_path)

            else:
                track.is_deleted = False

    @api.depends('name', 'album_artist_id.name', 'album_id.name', 'track_no')
    def _compute_file_path(self) -> None:
        file_service = self._get_file_service_adapter()

        for track in self:
            track.file_path = file_service.set_new_path(
                artist=track.album_artist_id.name or '',
                album=track.album_id.name or '',
                track=str(track.track_no) or '',
                title=track.name or '',
            )

    @api.depends('album_artist_id')
    def _compute_compilation_value(self) -> None:
        for track in self:
            if track.album_artist_id and track.album_artist_id.name.lower() == 'various artists':
                track.compilation = True

            else:
                track.compilation = False

    def _inverse_compilation_value(self) -> None:
        for track in self:
            if track.compilation:
                # noinspection PyProtectedMember
                track.album_artist_id = track._find_or_create_single_artist("Various Artists", [])

            else:
                # noinspection PyProtectedMember
                track.album_artist_id = track._find_or_create_single_artist(
                    track.original_artist_id.name, track.track_artist_ids
                )

    def _search_is_deleted(self, operator, value):
        matching_ids = []
        saved_records = self.search([('is_saved', operator, True)])

        for track in saved_records:
            deleted = not track.file_exists(track.old_path)

            if (value and deleted) or (not value and not deleted):
                matching_ids.append(track.id)

        return [("id", "in", matching_ids)]

    @api.constrains('name', 'track_artist_ids', 'owner')
    def _check_track_name(self) -> None:
        for current_track in self:  # type:ignore
            if not current_track.track_artist_ids:
                continue

            existing_tracks = self.search([
                ('id', '!=', current_track.id),
                ('name', '=', current_track.name),
                ('owner', '=', current_track.owner.id)
            ])

            for track in existing_tracks:  # type:ignore
                if set(current_track.track_artist_ids.ids) == set(track.track_artist_ids.ids):
                    raise ValidationError(
                        _("\nThe track '%s' already exists with the same artist(s).", current_track.name)
                    )

    @api.constrains('file_path')
    def _validate_file_path(self) -> None:

        file_service = self._get_file_service_adapter()

        for track in self:
            if not (track.file_path and isinstance(track.file_path, str)):
                continue

            track.has_valid_path = file_service.is_valid(track.file_path)

    @api.onchange('compilation')
    def _display_album_artist_changes(self) -> None:
        for track in self:
            if track.compilation:
                # noinspection PyProtectedMember
                track.album_artist_id = track._find_or_create_single_artist("Various Artists", [])

            else:
                # noinspection PyProtectedMember
                track.album_artist_id = track._find_or_create_single_artist(
                    track.original_artist_id.name, track.track_artist_ids
                )

    def save_changes(self):
        track = self.ensure_one()

        # noinspection PyProtectedMember
        results = track._perform_save_changes()
        final_message = []

        if results['success'] > 0:
            final_message.append(
                _("Metadata from '%s' has been updated!", track.name)
            )

        if results['messages']:
            final_message.append(
                _("Failed to update metadata for '%s' track!", track.name)
            )

        if not final_message:  # This message will never be shown.
            final_message.append(
                _("No changes applied to '%s' track!", track.name)
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Music Manager says:"),
                'message': "\n".join(final_message),
                'type': 'warning' if results['messages'] else 'success',
                'sticky': False,
            }
        }

    def _find_or_create_single_artist(self, artist_name: str, fallback_ids: list[int]):
        artists = self.env['music_manager.artist']

        if artist_name and artist_name.lower() != 'unknown':
            artist = artists.search([('name', '=', artist_name)], limit=1)

            if artist:
                return artist.id

            else:
                return artists.create([{'name': artist_name}]).id

        elif fallback_ids:
            return fallback_ids[0]

        return False

    def _get_file_service_adapter(self) -> FileServiceAdapter:
        settings = self.env['music_manager.audio_settings'].search([], limit=1)

        root = settings.root_dir if settings else '/music'
        file_extension = settings.sound_format if settings else 'mp3'

        return FileServiceAdapter(str_root_dir=root, file_extension=file_extension)

    def _get_track_service_adapter(self) -> TrackServiceAdapter:
        settings = self.env['music_manager.audio_settings'].search([], limit=1)

        file_extension = settings.sound_format if settings else 'mp3'

        return TrackServiceAdapter(file_type=file_extension)

    def _ensure_optional_fields(self):
        self.ensure_one()

        protected_fields = [
            ('track_artist_ids', _("Track artist(s)")),
            ('genre_id', _("Genre")),
            ('original_artist_id', _("Original artist")),
            ('year', _("Year")),
        ]

        for field, label in protected_fields:
            value = getattr(self, field, None)

            if not value:
                raise ValidationError(
                    _("Field '%s' cannot be empty. Please fill it or restore previous value.", label)
                )

    def _perform_save_changes(self):
        failure_messages = []
        success_counter = 0

        file_service = self._get_file_service_adapter()

        for track in self:
            # noinspection PyProtectedMember
            track._ensure_optional_fields()

            if not isinstance(track.old_path, str):
                failure_messages.append(
                    _("Track '%s' was skipped because it is not saved into your library.", track.name)
                )
                continue

            if not (isinstance(track.file_path, str) and track.has_valid_path):
                failure_messages.append(
                    _("Track '%s' was skipped because it has an invalid path.", track.name)
                )
                continue

            try:
                # noinspection PyProtectedMember
                track._update_metadata()

                if track.old_path != track.file_path:
                    file_service.update_file_path(track.old_path, track.file_path)

                track.old_path = track.file_path
                success_counter += 1

            except InvalidPathError as invalid_path:
                _logger.error(f"There was an issue with file path: {invalid_path}")
                raise ValidationError(_("\nActually, the file path of '%s' is not valid.", track.name))

            except FilePersistenceError as not_allowed:
                _logger.error(f"Cannot update the file: {not_allowed}")
                raise ValidationError(
                    _("\nAn internal issue ocurred while trying to update the file '%s'."
                      "\nPlease, try it again with a different record.", track.name)
                )

            except MusicManagerError as unknown_error:
                _logger.error(f"Unespected error while trying to update the file: {unknown_error}")
                raise ValidationError(
                    _("\nDamn! Something went wrong while updating the file '%s'."
                      "\nPlease, contact with your Admin.", track.name)
                )

        return {
            'success': success_counter,
            'messages': failure_messages
        }

    def _sync_album_with_artist(self) -> None:
        self.ensure_one()
        if self.album_id and self.album_artist_id:
            if self.album_id.album_artist_id != self.album_artist_id:
                self.album_id.write(
                    {'album_artist_id': self.album_artist_id.id}
                )

    def _sync_album_with_genre(self) -> None:
        self.ensure_one()
        if self.album_id and self.genre_id:
            if self.album_id.genre_id != self.genre_id:
                self.album_id.write(
                    {'genre_id': self.genre_id.id}
                )

    def _sync_album_with_owner(self) -> None:
        self.ensure_one()

        if not self.owner or not self.album_id:
            return

        if self.owner in self.album_id.owner_ids:
            return

        album_class = self.env['music_manager.album']
        found_album = album_class.search([
            ('name', '=', self.album_id.name),
            ('album_artist_id', '=', self.album_artist_id.id),
        ], limit=1)

        if not found_album:
            found_album = album_class.create(
                {
                    'name': self.album_id.name,
                    'album_artist_id': self.album_artist_id.id if self.album_artist_id else False,
                    'genre_id': self.genre_id.id if self.genre_id else False,
                }
            )

        old_album = self.album_id
        if found_album != old_album:
            self.album_id = found_album.id

        if old_album and not old_album.exists().track_ids:
            old_album.unlink()

    def _update_metadata(self) -> None:

        track_service = self._get_track_service_adapter()

        for track in self:
            metadata = {
                'TIT2': track.name or "",
                'TPE1': [record.name for record in track.track_artist_ids] if track.track_artist_ids else [],
                'TPE2': ("Various Artists" if track.compilation else track.album_artist_id.name) or "",
                'TALB': track.album_id.name or "",
                'TRCK': (track.track_no or 0, track.total_track or 0),
                'TOPE': track.original_artist_id.name,
                'TCMP': track.compilation,
                'TPOS': (track.disk_no or 0, track.total_disk or 0),
                'TDRC': track.year,
                'TCON': track.genre_id.name,
                'APIC': track.picture,
            }

            track_service.write_metadata(track.old_path, metadata)

    @staticmethod
    def file_exists(filepath: str) -> bool:
        if not isinstance(filepath, str):
            return False

        return Path(filepath).exists()

    @staticmethod
    def _get_years_list():
        return get_years_list()
