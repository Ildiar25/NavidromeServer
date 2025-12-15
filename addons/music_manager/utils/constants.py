from typing import Final, Dict, Set


# Root music directory
ROOT_DIR: Final[str] = "/music"


# Main file extension
TRACK_EXTENSION: Final[str] = "mp3"


# Admitted files:
ALLOWED_MUSIC_FORMAT: Final[Set[str]] = {"audio/mpeg", "audio/mpg", "audio/x-mpeg"}
ALLOWED_IMAGE_FORMAT: Final[Set[str]] = {"image/jpeg", "image/png"}

# Option structure:
OPTIONS_STRUCTURE: Final[Set[str]] = {
    'format', 'quiet', 'keepvideo', 'noplaylist', 'no_warnings', 'prefer_ffmpeg', 'postprocessors', 'outtmpl'
}


# File persistence pattern
PATH_PATTERN: Final[str] = rf'^\{ROOT_DIR}\/\w+\/\w+\/[0-9]{2}_\w+\.[a-zA-Z0-9]{3,4}$'


# Symbol dictionary
SYMBOL_MAP: Final[Dict[str, str]] = {
    "$": "s",
    "&": "_and_",
    "+": "_plus_",
    "@": "_at_",
    "!!!": "_three_exclamation_marks_",
}
