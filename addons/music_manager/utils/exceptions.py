
# ---- Main exception ---- #
class MusicManagerError(Exception):
    """Base exception for MusicManager errors."""
    ...


# ---- General exceptions ---- #
class MetadataServiceError(MusicManagerError):
    """General exception for metadata errors."""
    ...


class DownloadServiceError(MusicManagerError):
    """General exception for donwload errors."""
    ...


class ImageServiceError(MusicManagerError):
    """General exception for image errors."""
    ...
