from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from .parser import Track, parse_collection


@dataclass(slots=True)
class RekordboxPlaylist:
    name: str
    folder_path: str
    track_ids: list[int]


def _parse_track_id(value: str | None) -> int | None:
    if value in (None, ""):
        return None

    try:
        return int(value)
    except ValueError:
        return None


def _walk_nodes(
    node: ET.Element,
    parent_path: str,
    playlists: list[RekordboxPlaylist],
) -> None:
    node_type = node.get("Type")
    name = (node.get("Name") or "").strip()

    # Folder
    if node_type == "0":
        if name and name.upper() != "ROOT":
            current_path = (
                f"{parent_path}/{name}"
                if parent_path
                else name
            )
        else:
            current_path = parent_path

        for child in node.findall("NODE"):
            _walk_nodes(
                child,
                current_path,
                playlists,
            )

        return

    # Playlist
    if node_type == "1":
        key_type = node.get("KeyType", "0")

        # First version supports TrackID references.
        if key_type != "0":
            return

        track_ids = []

        for track_element in node.findall("TRACK"):
            track_id = _parse_track_id(
                track_element.get("Key")
            )

            if track_id is not None:
                track_ids.append(track_id)

        playlists.append(
            RekordboxPlaylist(
                name=name,
                folder_path=parent_path,
                track_ids=track_ids,
            )
        )


def parse_playlists(
    xml_path: str | Path,
) -> list[RekordboxPlaylist]:
    path = Path(xml_path)

    if not path.exists():
        raise FileNotFoundError(
            f"XML file not found: {path}"
        )

    root = ET.parse(path).getroot()

    playlists_element = root.find("PLAYLISTS")

    if playlists_element is None:
        return []

    playlists: list[RekordboxPlaylist] = []

    root_node = playlists_element.find("NODE")

    if root_node is None:
        return playlists

    _walk_nodes(
        root_node,
        "",
        playlists,
    )

    return playlists


def resolve_playlist_tracks(
    playlist: RekordboxPlaylist,
    collection: list[Track],
) -> list[Track]:
    by_id = {
        track.track_id: track
        for track in collection
    }

    return [
        by_id[track_id]
        for track_id in playlist.track_ids
        if track_id in by_id
    ]


def load_playlists_with_collection(
    xml_path: str | Path,
) -> tuple[
    list[Track],
    list[RekordboxPlaylist],
]:
    tracks = parse_collection(xml_path)
    playlists = parse_playlists(xml_path)

    return tracks, playlists