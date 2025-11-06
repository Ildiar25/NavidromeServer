# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict

# noinspection PyProtectedMember
from odoo import _, api
from odoo.exceptions import ValidationError
from odoo.models import AbstractModel

from ...adapters.image_service_adapter import ImageServiceAdapter
from ...utils.constants import ALLOWED_IMAGE_FORMAT
from ...utils.custom_types import CustomWarningMessage
from ...utils.exceptions import InvalidFileFormatError, InvalidImageFormatError, ImagePersistenceError, MusicManagerError
from ...utils.file_utils import validate_allowed_mimes


_logger = logging.getLogger(__name__)


class ProcessImageMixin(AbstractModel):
    _name = 'music_manager.process_image_mixin'
    _description = 'shared_process_image_method'

    @api.onchange('picture')
    def _validate_picture_image(self) -> CustomWarningMessage | None:
        for record in self:
            if not record.picture and not isinstance(record.picture, (str, bytes)):
                continue

            try:
                validate_allowed_mimes(record.picture, ALLOWED_IMAGE_FORMAT)

            except InvalidFileFormatError as invalid_file:
                record.picture = False
                return {
                    'warning': {
                        'title': _("Not today! ❌️"),
                        'message': _(
                            "\nI'm sooo sorry but, actually PNG or JPEG image format is allowed: \n%s. 🤷", invalid_file
                        )
                    }
                }

        return None

    @staticmethod
    def _process_picture_image(values: Dict[str, Any]) -> None:
        if not 'picture' in values or not values['picture']:
            return

        if not isinstance(values['picture'], str):
            _logger.warning(f"Image is not an encoded string. Will be ignored: {type(values['picture'])}.")
            return

        try:
            validate_allowed_mimes(values['picture'], ALLOWED_IMAGE_FORMAT)

        except InvalidFileFormatError as invalid_file:
            raise ValidationError(
                _("\nThis image has an invalid format! \n%s.", invalid_file)
            )

        try:
            image = ImageServiceAdapter(values['picture'])
            values['picture'] = image.save_to_bytes(width=400, height=400)

        except InvalidImageFormatError as format_error:
            _logger.error(f"Image has an invalid format or file is corrupt: {format_error}.")
            raise ValidationError(_("\nThe uploaded image has an invalid format or is corrupt."))

        except ImagePersistenceError as service_error:
            _logger.error(f"Failed to process cover image: {service_error}.")
            raise ValidationError(
                _("\nAn internal issue ocurred while processing the image. Please, try a different file.")
            )

        except MusicManagerError as unknown_error:
            _logger.error(f"Unexpected error while processing image: {unknown_error}.")
            raise ValidationError(
                _("\nDamn! Something went wrong while processing the image.\nPlease, contact with your Admin.")
            )
