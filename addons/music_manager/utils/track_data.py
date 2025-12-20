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
    duration: int = 0                   # Duration (in seconds)
    bitrate: int = 0                    # Bitrate (in seconds)
    sample_rate: int = 0                # Hertz frequency (Hz)
    channels: int = 0                   # Mono (1) or stereo (2)
    mode: str = "Unknown"               # Flow mode ('stereo', 'mono', 'joint stereo', ...)
    codec: str = "Unknown"              # MPEG (mp3)
    version: int = 0                    # Codec version
    layer: int = 0                      # Codec layer (3 for mp3)
    total_frames: int = 0               # Total file frames
    constant_bitrate: bool = True       # True if CBR, False if VBR
