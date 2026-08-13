from rekordbox_library_intelligence.parser import Track
from rekordbox_library_intelligence.segments import (
    rating_to_stars,
    segment_tracks,
)


def make_track(
    track_id: int,
    play_count: int,
    rating: int,
) -> Track:
    return Track(
        track_id=track_id,
        title=f"Track {track_id}",
        artist="Example Artist",
        bpm=126.0,
        bitrate=320,
        play_count=play_count,
        rating=rating,
        location=f"file://localhost/C:/Music/{track_id}.mp3",
        genre="House",
    )


def test_rating_to_stars():
    assert rating_to_stars(0) == 0
    assert rating_to_stars(51) == 1
    assert rating_to_stars(102) == 2
    assert rating_to_stars(153) == 3
    assert rating_to_stars(204) == 4
    assert rating_to_stars(255) == 5


def test_core_segment():
    tracks = [
        make_track(1, play_count=3, rating=102),
        make_track(2, play_count=5, rating=51),
    ]

    result = segment_tracks(tracks)

    assert len(result.core) == 2


def test_rotation_segment():
    tracks = [
        make_track(1, play_count=1, rating=153),
        make_track(2, play_count=2, rating=204),
    ]

    result = segment_tracks(tracks)

    assert len(result.rotation) == 2


def test_discovery_segment():
    tracks = [
        make_track(1, play_count=0, rating=204),
        make_track(2, play_count=0, rating=255),
    ]

    result = segment_tracks(tracks)

    assert len(result.discovery) == 2


def test_unassigned_segment():
    tracks = [
        make_track(1, play_count=0, rating=102),
        make_track(2, play_count=1, rating=102),
    ]

    result = segment_tracks(tracks)

    assert len(result.unassigned) == 2