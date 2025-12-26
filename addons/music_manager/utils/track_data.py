from dataclasses import dataclass


@dataclass()
class TrackMetadata:
    TIT2: str = "Unknown"               # Title
    TPE1: str = "Unknown"               # Track artist
    TPE2: str = "Unknown"               # Album artist
    TOPE: str = "Unknown"               # Original artist
    TALB: str = "Unknown"               # Album
    TCMP: bool = False                  # Compilation
    TRCK: tuple[int, int] = (1, 1)      # Track no / Total tracks
    TPOS: tuple[int, int] = (1, 1)      # Disk no / Total disks
    TDRC: str = "Unknown"               # Year
    TCON: str = "Unknown"               # Genre
    APIC: bytes | None = None           # Cover


@dataclass()
class TrackInfo:
    bitrate: int = 0                    # Bitrate (in seconds)
    channels: int = 0                   # Mono (1), stereo (2), ...
    codec: str = "Unknown"              # MPEG (mp3)
    duration: int = 0                   # Duration (in seconds)
    mime_type: str = "Unknown"          # MIME type
    sample_rate: int = 0                # Hertz frequency (Hz)


@dataclass()
class FullTrackData:
    info: TrackInfo
    metadata: TrackMetadata
