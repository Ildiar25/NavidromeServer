from dataclasses import dataclass


@dataclass()
class TrackMetadata:
    TIT2: str = "N/A"               # Title
    TPE1: str = "N/A"               # Track artist
    TPE2: str = "N/A"               # Album artist
    TOPE: str = "N/A"               # Original artist
    TALB: str = "N/A"               # Album
    TRCK: str = "1"                 # Track no
    TPOS: str = "1"                 # Disk no
    TDRC: str = "N/A"               # Year
    TCON: str = "N/A"               # Genre
    APIC: bytes | None = None       # Cover
