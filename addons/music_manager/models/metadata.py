from dataclasses import dataclass


@dataclass()
class TrackMetadata:
    TIT2: str = "Unknown"               # Title
    TPE1: str = "Unknown"               # Track artist
    TPE2: str = "Unknown"               # Album artist
    TOPE: str = "Unknown"               # Original artist
    TALB: str = "Unknown"               # Album
    TRCK: tuple[str, str] = ("1", "1")  # Track no / Total tracks
    TPOS: tuple[str, str] = ("1", "1")  # Disk no / Total disks
    TDRC: str = "Unknown"               # Year
    TCON: str = "Unknown"               # Genre
    APIC: bytes | None = None           # Cover
