import base64
import binascii

from .exceptions import InvalidFileFormatError, ReadingFileError


def _is_base64_encoded(data: bytes | str) -> bool:
    if isinstance(data, bytes):
        try:
            data = data.decode('ascii')

        except UnicodeDecodeError:
            return False

    if not isinstance(data, str):
        return False

    try:
        base64.b64decode(data, validate=True)
        return True

    except (binascii.Error, ValueError):
        return False


def base64_encode(decoded_data: bytes) -> str:
    if not decoded_data:
        raise ReadingFileError("No data provided!")

    if not isinstance(decoded_data, bytes):
        raise InvalidFileFormatError(f"Invalid datatype: {type(decoded_data)}.")

    if _is_base64_encoded(decoded_data):
        raise InvalidFileFormatError("Already base64-encoded file")

    return base64.b64encode(decoded_data).decode()


def base64_decode(encoded_data: bytes | str) -> bytes:
    if not encoded_data:
        raise ReadingFileError("No data provided!")

    if not isinstance(encoded_data, (bytes, str)):
        raise InvalidFileFormatError(f"Invalid datatype: {type(encoded_data)}.")

    if not _is_base64_encoded(encoded_data):
        raise InvalidFileFormatError("Invalid base64-encoded file")

    return base64.b64decode(encoded_data)
