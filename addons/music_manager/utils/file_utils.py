import magic

from ..utils.data_encoding import base64_decode
from ..utils.exceptions import InvalidFileFormatError


def get_mime_file(file_encoded: bytes) -> str:
    data_encoded = base64_decode(file_encoded)
    mime_type = magic.from_buffer(data_encoded, mime=True)

    if not mime_type:
        raise InvalidFileFormatError("Unable to read file type")

    return mime_type


def validate_allowed_mimes(file_data: bytes, allowed_mimes: set[str]) -> str:
    mime_type = get_mime_file(file_data)

    if mime_type not in allowed_mimes:
        raise InvalidFileFormatError(f"Unsupported file format: '{mime_type}'")

    return mime_type
