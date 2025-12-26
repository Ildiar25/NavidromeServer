
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


class AudioInfoServiceError(MusicManagerError):
    """General exception for metadata errors."""
    ...


# ---- Specific DOWNLOAD SERVICE exceptions ---- #

class ClientPlatformError(DownloadServiceError):
    """Raised when client denies connection or download is unavailable."""
    ...


class VideoProcessingError(DownloadServiceError):
    """Raised when video is unreadable or cannot be processed."""
    ...


# ---- Specific FILE SERVICE exceptions ---- #

class FilePersistenceError(FileServiceError):
    """Raised when file cannot be saved."""
    ...


class InvalidFileFormatError(FileServiceError):
    """Raised when file has no header or is a corrupt file."""
    ...


class InvalidPathError(FileServiceError):
    """Raised when file has an invalid path or is not found."""
    ...


# ---- Specific IMAGE SERVICE exceptions ---- #

class ImagePersistenceError(ImageServiceError):
    """Raised when an image cannot be saved."""
    ...


class InvalidImageFormatError(ImageServiceError):
    """Raised when an image is unreadable or has an invalid format."""
    ...


# ---- Specific AUDIOINFO SERVICE exceptions ---- #

class MetadataPersistenceError(AudioInfoServiceError):
    """Raised when metadata cannot be saved."""
    ...


class ReadingFileError(AudioInfoServiceError):
    """Raised when file is unreadable or has not any tag."""
    ...
