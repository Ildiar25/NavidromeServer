
# ---- Main exception ---- #
class MusicManagerError(Exception):
    """Base exception for MusicManager errors."""
    ...


# ---- General exceptions ---- #
class InvalidMetadataServiceError(MusicManagerError):
    """General exception for metadata errors."""
    ...


class DownloadServiceError(MusicManagerError):
    """General exception for donwload errors."""
    ...
