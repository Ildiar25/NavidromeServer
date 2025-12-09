from enum import Enum


class FileType(Enum):
    MP3 = 'mp3'
    FLAC = 'flac'


class ImageType(Enum):
    PNG = 'png'
    JPG = 'jpg'


class AdapterType(Enum):
    PYTUBE = 'pytube'
    YTDLP = 'ytdlp'
