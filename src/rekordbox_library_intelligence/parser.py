from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

@dataclass(slots=True)
class Track:
    track_id: int
    title: str
    artist: str
    bpm: float | None
    bitrate: int | None
    play_count: int
    rating: int
    location: str
    genre: str

def _to_int(value, default=0):
    try:
        return int(value) if value not in (None, "") else default
    except ValueError:
        return default

def _to_float(value):
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None

def parse_collection(xml_path: str | Path) -> list[Track]:
    path = Path(xml_path)
    if not path.exists():
        raise FileNotFoundError(f"XML file not found: {path}")

    root = ET.parse(path).getroot()
    collection = root.find("COLLECTION")
    if collection is None:
        raise ValueError("Invalid Rekordbox XML: COLLECTION element was not found.")

    tracks = []
    for item in collection.findall("TRACK"):
        tracks.append(Track(
            track_id=_to_int(item.get("TrackID")),
            title=(item.get("Name") or "").strip(),
            artist=(item.get("Artist") or "").strip(),
            bpm=_to_float(item.get("AverageBpm")),
            bitrate=_to_int(item.get("BitRate"), 0) or None,
            play_count=_to_int(item.get("PlayCount")),
            rating=_to_int(item.get("Rating")),
            location=(item.get("Location") or "").strip(),
            genre=(item.get("Genre") or "").strip(),
        ))
    return tracks
