# -*- coding: utf-8 -*-
import base64
import io
import logging
import re
from unidecode import unidecode
from typing import Any

# noinspection PyPackageRequirements
import magic
from urllib.parse import urlparse

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import ValidationError
from odoo.fields import Binary, Boolean, Char, Many2many, Many2one, Selection
from odoo.models import Model

from ..services.download_service import YTDLPAdapter, YoutubeDownload
from ..services.file_service import FileManager
from ..services.image_service import ImageToPNG
from ..services.metadata_service import MP3File
from ..utils.exceptions import DownloadServiceError, ImageServiceError, MetadataServiceError, MusicManagerError


_logger = logging.getLogger(__name__)


class Track(Model):

    _name = 'music_manager.track'
    _description = 'track_table'

    # Basic fields
    bpm = Char(string=_("BTM"), readonly=True)
    collection = Boolean(string=_("Part of a collection"))
    cover = Binary(string=_("Cover"), attachment=True)
    disk_no = Char(string=_("Disk no"))
    duration = Char(string=_("Duration (min)"), readonly=True)
    file_type = Char(string=_("Type"), readonly=True)
    name = Char(string=_("Title"))
    track_no = Char(string=_("Track no"))
    year = Char(string=_("Year"))

    # Relational fields
    album_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Album artist"))
    album_id = Many2one(comodel_name='music_manager.album', string=_("Album"))
    genre_id = Many2one(comodel_name='music_manager.genre', string=_("Genre"))
    original_artist_id = Many2one(comodel_name='music_manager.artist', string=_("Original artist"))
    track_artist_ids = Many2many(comodel_name='music_manager.artist', string=_("Track artist(s)"))

    # Temporal fields
    file = Binary(string=_("File"))
    tmp_album = Char(string=_("Album"))
    tmp_album_artist = Char(string=_("Album artist"))
    tmp_artists = Char(string=_("Track artist(s)"))
    tmp_genre = Char(string=_("Genre"))
    tmp_original_artist = Char(string=_("Original artist"))
    url = Char(string=_("Youtube URL"))

    # Computed fields
    display_artist_names = Char(string=_("Display artist name"), compute='_compute_display_artist_name', store=True)
    file_path = Char(string=_("File path"), compute='_compute_file_path', store=True)
    old_path = Char(string=_("Old path"), copy=False, store=True)

    # Related fields

    # Technical fields
    has_valid_path = Boolean(string=_("Valid path"), default=False, readonly=True)
    is_saved = Boolean(string=_("Is saved"), default=False, readonly=True)
    state = Selection(
        selection=[
            ('start', _("Start")),
            ('uploaded', _("Uploaded")),
            ('metadata', _("Metadata Editing")),
            ('done', _("Done")),
            ('added', _("Added")),
        ],
        string=_("State"),
        default='start'
    )
    user_id = Many2one(comodel_name='res.users', string=_("Owner"), default=lambda self: self.env.user, required=True)

    @api.model_create_multi
    def create(self, list_vals: list[dict[str, Any]]):
        for vals in list_vals:
            self._process_cover_image(vals)

        return super().create(list_vals)

    def write(self, vals: dict[str, Any]) -> None:
        self._process_cover_image(vals)
        return super().write(vals)

    @api.depends('track_artist_ids')
    def _compute_display_artist_name(self) -> None:
        for track in self:
            if not track.track_artist_ids:
                continue

            artist_names = track.track_artist_ids.mapped('name')
            track.display_artist_names = ", ".join(artist_names if artist_names else "")

    @api.depends('name', 'album_artist_id.name', 'album_id.name', 'track_no')
    def _compute_file_path(self) -> None:
        for track in self:
            artist = self._clean_for_path(track.album_artist_id.name or '')
            album = self._clean_for_path(track.album_id.name or '')

            if track.track_no and len(track.track_no) == 1:
                track_no = f"0{self._clean_for_path(track.track_no)}"
            else:
                track_no = self._clean_for_path(track.track_no or '')

            title = self._clean_for_path(track.name or '')

            track.file_path = f"/music/{artist}/{album}/{track_no}_{title}.mp3"

    @api.constrains('file', 'url', 'file_path')
    def _check_fields(self) -> None:
        for track in self:
            if not track.file_path:
                if not track.file and not track.url:
                    _logger.info(f"CONSTRAINT CHECK | file: {bool(track.file)} | url: {bool(track.url)}")
                    raise ValidationError(_("\nMust add an URL or update a file to proceed."))

                if track.file and track.url:
                    _logger.info(f"CONSTRAINT CHECK | file: {bool(track.file)} | url: {bool(track.url)}")
                    raise ValidationError(
                        _("\nOnly one field can be added at the same time. Please, delete one of them to continue.")
                    )

    @api.constrains('file_path')
    def _validate_file_path(self) -> None:

        artist = r'\w+'
        album = r'\w+'
        track_no = r'[0-9]{2}'
        title = r'\w+'
        extension = r'[a-zA-Z0-9]{3,4}$'

        pattern = fr'^\/music\/{artist}\/{album}\/{track_no}_{title}\.{extension}'

        for track in self:
            if not (track.file_path and isinstance(track.file_path, str)):
                continue

            track.has_valid_path = bool(re.match(pattern, track.file_path))

    @api.onchange('file')
    def _validate_file_type(self) -> dict[str, dict[str, str]] | None:
        for track in self:
            if not (track.file and isinstance(track.file, bytes)):
                continue

            file_data = base64.b64decode(track.file)
            mime_type = magic.from_buffer(file_data, mime=True)

            if mime_type not in ["audio/mpeg", "audio/mpg", "audio/x-mpeg"]:
                track.file = False
                return {
                    'warning': {
                        'title': _("Wait a minute! 👮"),
                        'message': _("\nActually only MP3 files are allowed. Don't f*ck the system: %s", mime_type)
                    }
                }

        return None

    @api.onchange('url')
    def _validate_url_path(self) -> dict[str, dict[str, str]] | None:
        for track in self:
            if not (track.url and isinstance(track.url, str)):
                continue

            parsed_url = urlparse(track.url)

            if not (parsed_url.netloc.endswith('youtube.com') or parsed_url.netloc.endswith('youtu.be')):
                return {
                    'warning': {
                        'title': _("C'mon dude! 🙄"),
                        'message': _("\nThe web address has to be valid and we both know it isn't.")
                    }
                }

        return None

    @api.onchange('cover')
    def _validate_cover_image(self) -> dict[str, dict[str, str]] | None:
        for track in self:
            if not (track.cover and isinstance(track.cover, (str, bytes))):
                continue

            image = base64.b64decode(track.cover)
            mime_type = magic.from_buffer(image, mime=True)

            if mime_type == 'image/webp':
                track.cover = False
                return {
                    'warning': {
                        'title': _("Not today! ❌"),
                        'message': _(
                            "\nI'm sooo sorry but, actually WEBP image format is not admited: %s. 🤷", mime_type
                        )
                    }
                }

        return None

    def action_back(self) -> None:
        for track in self:
            if track.state == 'done':
                track.state = 'metadata'

    def action_next(self) -> None:
        for track in self:
            match track.state:
                case 'start':
                    track.state = 'uploaded'
                    if track.url:
                        self._convert_to_mp3()

                    self._update_fields()

                case 'uploaded':
                    track.state = 'metadata'

                case 'metadata':
                    track.state = 'done'

    def save_changes(self) -> None:
        for track in self:
            if not (isinstance(track.file_path, str) and track.has_valid_path):
                continue

            path = FileManager(track.file_path).create_folders()
            path.update_path(track.old_path)
            self._update_metadata(track.file_path)
            track.old_path = track.file_path

    def save_file(self) -> None:
        for track in self:
            if not (isinstance(track.file, bytes) and track.has_valid_path):
                continue

            song = base64.b64decode(track.file)
            FileManager(track.file_path).create_folders().save(song)
            self._update_metadata(track.file_path)

            track.old_path = track.file_path
            track.write(
                {
                    'is_saved': True,
                    'state': 'added',
                    'file': False,
                }
            )

    def _convert_to_mp3(self) -> None:
        for track in self:
            if not (track.url and isinstance(track.url, str)):
                continue

            try:
                buffer = io.BytesIO()
                adapter = YTDLPAdapter(url=track.url)
                downloader = YoutubeDownload()

                bytes_file = downloader.set_stream_to_buffer(adapter, buffer)
                mime_type = magic.from_buffer(bytes_file, mime=True)
                _logger.info(f"Download bytes length: {len(bytes_file)} | MIME type: {mime_type}\n")

                track.write(
                    {
                        'url': False,
                        'file': base64.b64encode(bytes_file)
                    }
                )

            except DownloadServiceError as video_error:
                _logger.error(f"Failed to process YouTube URL {track.url}: {video_error}")
                raise ValidationError(_("\nInvalid YouTube URL or video is not accessible."))

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while validating URL {track.url}: {unknown_error}")
                raise ValidationError(
                    _("\nDownloadService Error: Sorry, something went wrong while validating URL.")
                )

    def _find_or_create_album(self, album_name: str) -> int | bool:

        albums = self.env['music_manager.album']

        if album_name and album_name.lower() != 'unknown':
            album = albums.search([('name', 'ilike', album_name)], limit=1)

            if album:
                return album.id

            else:
                return albums.create({'name': album_name}).id

        return False

    def _find_or_create_artist(self, artist_names: str) -> list[tuple[int, int, list[int]]]:

        artists = self.env['music_manager.artist']
        artist_ids = []

        if artist_names and artist_names.lower() != 'unknown':
            names_list = (name.strip() for name in artist_names.split(','))

            for name in names_list:
                artist = artists.search([('name', 'ilike', name)], limit=1)

                if artist:
                    artist_ids.append(artist.id)

                else:
                    new_artist = artists.create({'name': name})
                    artist_ids.append(new_artist.id)

        return [(6, 0, artist_ids)]

    def _find_or_create_genre(self, genre_name: str) -> int | bool:

        genres = self.env['music_manager.genre']

        if genre_name and genre_name.lower() != 'unknown':
            genre = genres.search([('name', 'ilike', genre_name)], limit=1)

            if genre:
                return genre.id

            else:
                return genres.create({'name': genre_name}).id

        return False

    def _find_or_create_single_artist(self, artist_name: str, fallback_ids: list[int]) -> int | bool:

        artists = self.env['music_manager.artist']

        if artist_name and artist_name.lower() != 'unknown':
            artist = artists.search([('name', 'ilike', artist_name)])

            if artist:
                return artist.id

            else:
                return artists.create({'name': artist_name}).id

        elif fallback_ids:
            return fallback_ids[0]

        return False

    def _update_fields(self) -> None:
        for track in self:
            try:
                metadata = MP3File().get_metadata(io.BytesIO(base64.b64decode(track.file)))

                mapping_fields = {
                    'name': metadata.TIT2,
                    'tmp_artists': metadata.TPE1,
                    'tmp_album': metadata.TALB,
                    'duration': self._format_track_duration(metadata.DUR),
                    'tmp_genre': metadata.TCON,
                    'tmp_album_artist': metadata.TPE2,
                    'tmp_original_artist': metadata.TOPE,
                    'year': metadata.TDRC,
                    'track_no': metadata.TRCK[0],
                    'disk_no': metadata.TPOS[0],
                    'file_type': metadata.MIME,
                }

                for attr_name, value in mapping_fields.items():
                    setattr(track, attr_name, value)

                if metadata.APIC:
                    track.cover = base64.b64encode(metadata.APIC)

                track.track_artist_ids = self._find_or_create_artist(metadata.TPE1)
                track.album_id = self._find_or_create_album(metadata.TALB)
                track.genre_id = self._find_or_create_genre(metadata.TCON)
                track.album_artist_id = self._find_or_create_single_artist(metadata.TPE2, track.track_artist_ids.ids)
                track.original_artist_id = self._find_or_create_single_artist(metadata.TOPE, track.track_artist_ids.ids)

            except MetadataServiceError as invalid_metadata:
                _logger.error(f"Failed to process file metadata: {invalid_metadata}")
                raise ValidationError(_("\nInvalid metadata founded on file."))

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while processing metadata file: {unknown_error}")
                raise ValidationError(
                    _("\nMetadataServiceError: Sorry, something went wrong while loading metadata file.")
                )

    def _update_metadata(self, path: str) -> None:
        for track in self:
            metadata = {
                'TIT2': track.name,
                'TPE1': track.display_artist_names,
                'TPE2': track.album_artist_id.name,
                'TOPE': track.original_artist_id.name,
                'TALB': track.album_id.name,
                'TRCK': (track.track_no, "1"),
                'TPOS': (track.disk_no, "1"),
                'TDRC': track.year,
                'TCON': track.genre_id.name,
                'APIC': base64.b64decode(track.cover) if track.cover else None,
            }

            try:
                MP3File().set_metadata(path, metadata)

            except MetadataServiceError as invalid_metadata:
                _logger.error(f"Failed to process file metadata: {invalid_metadata}")

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while processing metadata file: {unknown_error}")
                raise ValidationError(
                    _("\nMetadataServiceError: Sorry, something went wrong while loading metadata file.")
                )

    @staticmethod
    def _clean_for_path(text: str) -> str:
        text = unidecode(text).lower()
        text = re.sub(pattern=r'[^a-z0-9]', repl='_', string=text)
        return re.sub(pattern=r'_+', repl='_', string=text).strip('_')

    @staticmethod
    def _format_track_duration(duration: int) -> str:
        minutes, seconds = divmod(duration, 60)
        return f"{minutes:02}:{seconds:02}"

    @staticmethod
    def _process_cover_image(value: dict[str, Any]) -> None:
        if 'cover' in value and value['cover']:
            try:
                if isinstance(value['cover'], (str, bytes)):
                    image = base64.b64decode(value['cover'])
                    mime_type = magic.from_buffer(image, mime=True)

                    if mime_type == 'image/webp':
                        raise ValidationError(_("\nThis track cover has an invalid format: %s", mime_type))

                    cover = ImageToPNG(io.BytesIO(image)).center_image().with_size(width=200, height=200).build()
                    value['cover'] = base64.b64encode(cover)

            except ImageServiceError as service_error:
                _logger.error(f"Failed to process cover image: {service_error}")
                raise ValidationError(_("\nSomething went wrong while processing cover image: %s", service_error))

            except MusicManagerError as unknown_error:
                _logger.error(f"Unexpected error while processing image: {unknown_error}")
                raise ValidationError(
                    _("\nImageServiceError: Sorry, something went wrong while processing cover image")
                )
