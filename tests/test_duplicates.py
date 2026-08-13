from rekordbox_library_intelligence.duplicates import (
    find_duplicates,
    normalize_text,
)
from rekordbox_library_intelligence.parser import Track


def make_track(
    track_id: int,
    artist: str,
    title: str,
    bitrate: int = 320,
    play_count: int = 0,
    rating: int = 0,
) -> Track:
    return Track(
        track_id=track_id,
        title=title,
        artist=artist,
        bpm=126.0,
        bitrate=bitrate,
        play_count=play_count,
        rating=rating,
        location=f"file://localhost/C:/Music/{track_id}.mp3",
        genre="House",
    )


def test_normalize_text():
    assert normalize_text("Beyoncé - Déjà Vu!") == "beyonce deja vu"


def test_find_exact_duplicate():
    tracks = [
        make_track(
            1,
            "Madonna",
            "Music (Extended Mix)",
        ),
        make_track(
            2,
            "MADONNA",
            "Music - Extended Mix",
        ),
    ]

    duplicates = find_duplicates(tracks)

    assert len(duplicates) == 1


def test_recommend_higher_play_count():
    tracks = [
        make_track(
            1,
            "Madonna",
            "Music",
            bitrate=320,
            play_count=0,
        ),
        make_track(
            2,
            "Madonna",
            "Music",
            bitrate=128,
            play_count=4,
        ),
    ]

    duplicates = find_duplicates(tracks)

    assert len(duplicates) == 1
    assert duplicates[0].keep_track_id == 2
    assert duplicates[0].reason == "higher DJ play count"


def test_different_tracks_are_not_duplicates():
    tracks = [
        make_track(
            1,
            "Madonna",
            "Music",
        ),
        make_track(
            2,
            "Madonna",
            "Hung Up",
        ),
    ]

    duplicates = find_duplicates(tracks)

    assert duplicates == []