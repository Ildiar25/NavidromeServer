# -*- coding: utf-8 -*-
import logging
from pathlib import Path

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Binary, Boolean, Char, Integer, Many2many, Many2one
from odoo.models import Model

from .mixins.process_image_mixin import ProcessImageMixin
from ..adapters import FileServiceAdapter, TrackServiceAdapter
from ..utils.exceptions import FilePersistenceError, MusicManagerError, InvalidPathError


_logger = logging.getLogger(__name__)


class Track(Model, ProcessImageMixin):
    _name = 'music_manager.track'
    _description = 'track_table'
    _order = 'album_name, disk_no, track_no'

    # Basic fields
    picture = Binary(string=_("Picture"), attachment=True)
    disk_no = Integer(string=_("Disk no"))
    name = Char(string=_("Title"))
    total_disk = Integer(string=_("Total disk no"))
    total_track = Integer(string=_("Total track no"))
    track_no = Integer(string=_("Track no"))
    year = Char(string=_("Year"))

    # Readonly fields
    bitrate = Integer(string=_("Kbps"), default=0, readonly=True)
    channels = Char(string=_("Channels"), default="Stereo", readonly=True)
    codec = Char(string=_("Codec"), default="Unknown", readonly=True)
    duration = Char(string=_("Duration (min)"), default="0:00", readonly=True)
    mime_type = Char(string=_("MIME"), default="Unknown", readonly=True)
    sample_rate = Integer(string=_("Frequency (Hz)"), default=0, readonly=True)

    # Relational fields
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"), copy=False)
    album_id = Many2one(comodel_name='music_manager.album', string=_("Album"), ondelete='cascade')
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
    original_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Original artist"))
    track_artist_ids = Many2many(comodel_name='music_manager.artist', string=_("Track artist(s)"))

    # Computed fields
    collection = Boolean(
        string=_("Part of a collection"),
        compute='_compute_collection_value',
        inverse='_inverse_collection_value',
        default=False,
    )
    display_artist_names = Char(string=_("Display artist name"), compute='_compute_display_artist_name', store=False)
    is_deleted = Boolean(
        string=_("Is deleted"), compute='_compute_file_is_deleted', search='_search_is_deleted', store=False
    )
    file_path = Char(string=_("File path"), compute='_compute_file_path', store=True)
    old_path = Char(string=_("Old path"), copy=False, store=True)

    # Related fields
    album_name = Char(string="Album name", related='album_id.name', store=True)

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
        file_paths = [(track.file_path, track.is_deleted) for track in self]
        check_albums = self.mapped('album_id')

        file_service = self._get_file_service_adapter()

        res = super().unlink()

        for album in check_albums:
            if not self.env['music_manager.track'].search([('album_id', '=', album.id)]):
                album.unlink()

        is_admin = self.env.user.has_group('music_manager.group_music_manager_user_admin')

        for path, is_deleted in file_paths:
            if not is_deleted:
                still_used = self.env['music_manager.track'].sudo().search_count([('file_path', '=', path)])

                if is_admin or still_used == 0:
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
    def _compute_collection_value(self) -> None:
        for track in self:
            if track.album_artist_id and track.album_artist_id.name.lower() == 'various artists':
                track.collection = True

            else:
                track.collection = False

    def _inverse_collection_value(self) -> None:
        for track in self:
            if track.collection:
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

    @api.onchange('collection')
    def _display_album_artist_changes(self) -> None:
        for track in self:
            if track.collection:
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
            artist = artists.search([('name', 'ilike', artist_name)])

            if artist:
                return artist.id

            else:
                return artists.create([{'name': artist_name}]).id

        elif fallback_ids:
            return fallback_ids[0]

        return False

    def _get_file_service_adapter(self):
        settings = self.env['music_manager.audio_settings'].search([], limit=1)

        root = settings.root_dir if settings else '/music'
        file_extension = settings.sound_format if settings else 'mp3'

        return FileServiceAdapter(str_root_dir=root, file_extension=file_extension)

    def _perform_save_changes(self):
        failure_messages = []
        success_counter = 0

        file_service = self._get_file_service_adapter()

        for track in self:
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
                file_service.update_file_path(track.old_path, track.file_path)
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

            if success_counter > 0:
                self._update_metadata()
                track.old_path = track.file_path

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
        if not self.owner:
            return

        if not (self.album_id.name or self.album_name):
            return

        if self.album_id and self.album_id.owner == self.owner:
            return

        album_class = self.env['music_manager.album']
        found_album = album_class.search([('owner', '=', self.owner.id)], limit=1)

        if not found_album:
            found_album = album_class.create(
                {
                    'name': self.album_id.name,
                    'owner': self.owner.id,
                    'album_artist_id': self.album_artist_id.id if self.album_artist_id else False,
                    'genre_id': self.genre_id.id if self.genre_id else False,
                }
            )

        self.album_id = found_album.id

    def _update_metadata(self) -> None:
        for track in self:
            metadata = {
                'TIT2': track.name,
                'TPE1': track.display_artist_names,
                'TPE2': "Various Artists" if track.collection else track.album_artist_id.name,
                'TOPE': track.original_artist_id.name,
                'TALB': track.album_id.name,
                'TCMP': track.collection,
                'TRCK': (track.track_no, track.total_track),
                'TPOS': (track.disk_no, track.total_disk),
                'TDRC': track.year,
                'TCON': track.genre_id.name,
                'APIC': track.picture,
            }

            TrackServiceAdapter().write_metadata(track.file_path, metadata)

    @staticmethod
    def file_exists(filepath: str) -> bool:
        if not isinstance(filepath, str):
            return False

        return Path(filepath).exists()
