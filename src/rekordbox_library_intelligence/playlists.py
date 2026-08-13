from pathlib import Path
from urllib.parse import unquote

from .parser import Track
from .segments import LibrarySegments


def location_to_path(location: str) -> str:
    """
    Convert a Rekordbox file URI into a local filesystem path.

    Example:
        file://localhost/C:/Music/example.mp3
        -> C:\\Music\\example.mp3
    """
    if location.startswith("file://localhost/"):
        value = location[len("file://localhost/"):]
    elif location.startswith("file:///"):
        value = location[len("file:///"):]
    else:
        value = location

    value = unquote(value)

    if len(value) > 1 and value[1] == ":":
        value = value.replace("/", "\\")

    return value


def write_m3u8(
    tracks: list[Track],
    destination: str | Path,
) -> int:
    """
    Write tracks to an UTF-8 M3U8 playlist.

    Returns the number of tracks written.
    """
    destination = Path(destination)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = ["#EXTM3U"]
    written = 0

    for track in tracks:
        if not track.location:
            continue

        label = f"{track.artist} - {track.title}".strip(" -")
        path = location_to_path(track.location)

        lines.append(f"#EXTINF:-1,{label}")
        lines.append(path)

        written += 1

    destination.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8-sig",
    )

    return written


def generate_segment_playlists(
    segments: LibrarySegments,
    output_dir: str | Path = "output",
) -> dict[str, tuple[Path, int]]:
    """
    Generate CORE, ROTATION and DISCOVERY playlists.

    Rekordbox databases and audio files are never modified.
    """
    output_dir = Path(output_dir)

    definitions = {
        "CORE": segments.core,
        "ROTATION": segments.rotation,
        "DISCOVERY": segments.discovery,
    }

    generated = {}

    for name, tracks in definitions.items():
        destination = output_dir / f"{name}.m3u8"

        count = write_m3u8(
            tracks,
            destination,
        )

        generated[name] = (
            destination,
            count,
        )

    return generated