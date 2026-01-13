import datetime
import magic
import re
from typing import List, Tuple
from unidecode import unidecode

from ..utils.constants import SYMBOL_MAP
from ..utils.data_encoding import base64_decode
from ..utils.exceptions import InvalidFileFormatError


    # =========================================================================================
    # Utils for MIME type
    # =========================================================================================


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


    # =========================================================================================
    # Utils for path naming
    # =========================================================================================


def clean_path_section(section: str) -> str:
    mapped_chars = _map_special_characters(section)
    normalized = _normalize_characters(mapped_chars)
    cleaned = re.sub(pattern=r'[^a-z0-9]', repl='_', string=normalized)
    return re.sub(pattern=r'_+', repl='_', string=cleaned).strip('_')


def is_valid_path(path: str, root_dir: str) -> bool:
    artist = r'\w+'
    album = r'\w+'
    track_no = r'[0-9]{2}'
    title = r'\w+'
    extension = r'[a-zA-Z0-9]{3,4}'

    pattern = fr'{re.escape(root_dir)}\/{artist}\/{album}\/{track_no}_{title}\.{extension}'

    return bool(re.fullmatch(pattern, path))


def _map_special_characters(string: str) -> str:
    pattern = re.compile("|".join(re.escape(symbol_key) for symbol_key in SYMBOL_MAP.keys()))
    return pattern.sub(lambda match_pattern: SYMBOL_MAP[match_pattern.group(0)], string)


def _normalize_characters(string: str) -> str:
    return unidecode(string).lower()


    # =========================================================================================
    # Utils for dates
    # =========================================================================================


def get_years_list() -> List[Tuple[str, str]]:
    current_year = datetime.datetime.now().year
    return [(str(year), str(year)) for year in range(current_year, 1299, -1)]
