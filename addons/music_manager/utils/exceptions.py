
# ---- Main exception ---- #
class MusicManagerError(Exception):
    """Base exception for MusicManager errors."""
    ...


# ---- General exceptions ---- #
class DownloadServiceError(MusicManagerError):
    """General exception for donwload errors."""
    ...

class FileServiceError(MusicManagerError):
    """General exception for file management errors."""
    ...

class ImageServiceError(MusicManagerError):
    """General exception for image errors."""
    ...

class MetadataServiceError(MusicManagerError):
    """General exception for metadata errors."""
    ...


# ---- Specific DOWNLOAD SERVICE exceptions ---- #
class VideoProcessingError(DownloadServiceError):
    """Raised when video is unreadable or cannot be processed."""
    ...

class ClientPlatformError(DownloadServiceError):
    """Raised when client denies connection or download is unavailable."""
    ...


# ---- Specific FILE SERVICE exceptions ---- #


# ---- Specific IMAGE SERVICE exceptions ---- #
class InvalidImageFormatError(ImageServiceError):
    """Raised when an image is unreadable or has an invalid format."""
    ...

class ImagePersistenceError(ImageServiceError):
    """Raised when an image cannot be saved."""
    ...


# ---- Specific METADATA SERVICE exceptions ---- #
