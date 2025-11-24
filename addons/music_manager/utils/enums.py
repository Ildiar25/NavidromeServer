from enum import Enum


class FileType(Enum):
    MP3 = 'mp3'


class ImageType(Enum):
    PNG = 'png'


class AdapterType(Enum):
    PYTUBE = 'pytube'
    YTDLP = 'ytdlp'
