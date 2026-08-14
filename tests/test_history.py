from rekordbox_library_intelligence.history import (
    analyze_history_playlist,
    find_history_sessions,
    format_history_sessions,
    is_history_playlist,
)
from rekordbox_library_intelligence.parser import Track
from rekordbox_library_intelligence.rekordbox_playlists import (
    RekordboxPlaylist,
)


def make_track(
    track_id: int,
    artist: str,
    title: str,
    bpm: float | None,
) -> Track:
    return Track(
        track_id=track_id,
        title=title,
        artist=artist,
        bpm=bpm,
        bitrate=320,
        play_count=1,
        rating=204,
        location=(
            f"file://localhost/"
            f"C:/Music/{track_id}.mp3"
        ),
        genre="House",
    )


def make_collection():
    return [
        make_track(
            1,
            "Artist A",
            "Opening Track",
            120.0,
        ),
        make_track(
            2,
            "Artist B",
            "Middle Track",
            124.0,
        ),
        make_track(
            3,
            "Artist C",
            "Peak Track",
            128.0,
        ),
        make_track(
            4,
            "Artist D",
            "Closing Track",
            126.0,
        ),
    ]


def test_is_history_playlist():
    history = RekordboxPlaylist(
        name="HISTORY 001",
        folder_path="Histories",
        track_ids=[1, 2],
    )

    normal = RekordboxPlaylist(
        name="House Playlist",
        folder_path="Playlists",
        track_ids=[1, 2],
    )

    assert is_history_playlist(history)
    assert not is_history_playlist(normal)


def test_analyze_history_playlist():
    collection = make_collection()

    playlist = RekordboxPlaylist(
        name="HISTORY 001",
        folder_path="Histories",
        track_ids=[1, 2, 3, 4],
    )

    session = analyze_history_playlist(
        playlist,
        collection,
    )

    assert session.track_count == 4

    assert session.start_bpm == 120.0
    assert session.average_bpm == 124.5
    assert session.end_bpm == 126.0

    assert session.minimum_bpm == 120.0
    assert session.maximum_bpm == 128.0

    assert session.opener is not None
    assert session.opener.track_id == 1

    assert session.closer is not None
    assert session.closer.track_id == 4


def test_history_preserves_track_order():
    collection = make_collection()

    playlist = RekordboxPlaylist(
        name="HISTORY 001",
        folder_path="Histories",
        track_ids=[3, 1, 4, 2],
    )

    session = analyze_history_playlist(
        playlist,
        collection,
    )

    assert [
        track.track_id
        for track in session.tracks
    ] == [3, 1, 4, 2]

    assert session.opener is not None
    assert session.opener.track_id == 3

    assert session.closer is not None
    assert session.closer.track_id == 2


def test_find_only_history_sessions():
    collection = make_collection()

    playlists = [
        RekordboxPlaylist(
            name="HISTORY 001",
            folder_path="Histories",
            track_ids=[1, 2],
        ),
        RekordboxPlaylist(
            name="House Playlist",
            folder_path="Playlists",
            track_ids=[2, 3],
        ),
        RekordboxPlaylist(
            name="HISTORY 002",
            folder_path="Histories",
            track_ids=[3, 4],
        ),
    ]

    sessions = find_history_sessions(
        playlists,
        collection,
    )

    assert len(sessions) == 2

    assert sessions[0].name == "HISTORY 001"
    assert sessions[1].name == "HISTORY 002"


def test_format_history_sessions():
    collection = make_collection()

    playlists = [
        RekordboxPlaylist(
            name="HISTORY 001",
            folder_path="Histories",
            track_ids=[1, 2, 3, 4],
        )
    ]

    sessions = find_history_sessions(
        playlists,
        collection,
    )

    output = format_history_sessions(
        sessions
    )

    assert "DJ History Sessions" in output
    assert "Sessions found: 1" in output
    assert "HISTORY 001" in output

    assert "Tracks:      4" in output
    assert "Start BPM:   120.0" in output
    assert "Average BPM: 124.5" in output
    assert "End BPM:     126.0" in output

    assert (
        "Artist A - Opening Track"
        in output
    )

    assert (
        "Artist D - Closing Track"
        in output
    )