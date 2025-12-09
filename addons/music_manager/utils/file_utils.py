import base64

import magic

from ..utils.exceptions import InvalidFileFormatError


def get_mime_file(file_encoded: bytes) -> str:
    if not file_encoded:
        raise InvalidFileFormatError("No file data provided")

    if isinstance(file_encoded, bytes):
        try:
            file_encoded = base64.b64decode(file_encoded)

        except Exception:
            raise InvalidFileFormatError("Invalid base64-encoded file")

    mime_type = magic.from_buffer(file_encoded, mime=True)

    if not mime_type:
        raise InvalidFileFormatError("Unable to read file type")

    return mime_type


def validate_allowed_mimes(file_data: bytes, allowed_mimes: set[str]) -> str:
    mime_type = get_mime_file(file_data)

    if mime_type not in allowed_mimes:
        raise InvalidFileFormatError(f"Unsupported file format: '{mime_type}'")

    return mime_type
