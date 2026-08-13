from dataclasses import dataclass

from .parser import Track


@dataclass(slots=True)
class LibrarySegments:
    core: list[Track]
    rotation: list[Track]
    discovery: list[Track]
    unassigned: list[Track]


def rating_to_stars(rating: int) -> int:
    """
    Convert Rekordbox rating values to 0-5 stars.

    Rekordbox XML commonly stores ratings as:
    0, 51, 102, 153, 204, 255
    """
    if rating <= 0:
        return 0

    stars = round(rating / 51)

    return max(0, min(5, stars))


def segment_tracks(tracks: list[Track]) -> LibrarySegments:
    core: list[Track] = []
    rotation: list[Track] = []
    discovery: list[Track] = []
    unassigned: list[Track] = []

    for track in tracks:
        stars = rating_to_stars(track.rating)

        if track.play_count >= 3:
            core.append(track)

        elif 1 <= track.play_count <= 2 and stars >= 3:
            rotation.append(track)

        elif track.play_count == 0 and stars >= 4:
            discovery.append(track)

        else:
            unassigned.append(track)

    return LibrarySegments(
        core=core,
        rotation=rotation,
        discovery=discovery,
        unassigned=unassigned,
    )