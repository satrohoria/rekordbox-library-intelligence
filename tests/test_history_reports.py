import json

from rekordbox_library_intelligence.history import (
    HistorySession,
)
from rekordbox_library_intelligence.history_intelligence import (
    analyze_history_intelligence,
)
from rekordbox_library_intelligence.history_reports import (
    generate_history_reports,
    history_to_dict,
)
from rekordbox_library_intelligence.parser import Track


def make_track(
    track_id: int,
    artist: str,
    title: str,
    bpm: float,
) -> Track:
    return Track(
        track_id=track_id,
        artist=artist,
        title=title,
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


def make_session(
    name: str,
    tracks: list[Track],
) -> HistorySession:
    bpms = [
        track.bpm
        for track in tracks
        if track.bpm is not None
        and track.bpm > 0
    ]

    return HistorySession(
        name=name,
        folder_path="Histories",
        tracks=tracks,
        track_count=len(tracks),
        start_bpm=bpms[0],
        average_bpm=(
            sum(bpms) / len(bpms)
        ),
        end_bpm=bpms[-1],
        minimum_bpm=min(bpms),
        maximum_bpm=max(bpms),
        opener=tracks[0],
        closer=tracks[-1],
    )


def build_data():
    track_1 = make_track(
        1,
        "Artist A",
        "Opening Track",
        120,
    )

    track_2 = make_track(
        2,
        "Artist B",
        "Middle Track",
        124,
    )

    track_3 = make_track(
        3,
        "Artist C",
        "Closing Track",
        126,
    )

    sessions = [
        make_session(
            "HISTORY 001",
            [
                track_1,
                track_2,
                track_3,
            ],
        ),
        make_session(
            "HISTORY 002",
            [
                track_1,
                track_3,
            ],
        ),
    ]

    intelligence = (
        analyze_history_intelligence(
            sessions
        )
    )

    return sessions, intelligence


def test_history_to_dict():
    sessions, intelligence = (
        build_data()
    )

    data = history_to_dict(
        sessions,
        intelligence,
    )

    assert (
        data["summary"][
            "sessions_analyzed"
        ]
        == 2
    )

    assert (
        data["summary"][
            "unique_tracks"
        ]
        == 3
    )

    assert len(
        data["sessions"]
    ) == 2

    assert (
        data["sessions"][0]["name"]
        == "HISTORY 001"
    )


def test_generate_history_reports(
    tmp_path,
):
    sessions, intelligence = (
        build_data()
    )

    reports = generate_history_reports(
        sessions,
        intelligence,
        tmp_path,
    )

    assert reports["summary"].exists()
    assert reports["sessions"].exists()
    assert reports[
        "repeated_tracks"
    ].exists()
    assert reports["openers"].exists()
    assert reports["closers"].exists()
    assert reports["transitions"].exists()


def test_history_json_content(
    tmp_path,
):
    sessions, intelligence = (
        build_data()
    )

    reports = generate_history_reports(
        sessions,
        intelligence,
        tmp_path,
    )

    data = json.loads(
        reports["summary"].read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["summary"][
            "sessions_analyzed"
        ]
        == 2
    )

    assert (
        data["summary"][
            "transitions"
        ]["count"]
        == 3
    )


def test_sessions_csv_content(
    tmp_path,
):
    sessions, intelligence = (
        build_data()
    )

    reports = generate_history_reports(
        sessions,
        intelligence,
        tmp_path,
    )

    content = reports[
        "sessions"
    ].read_text(
        encoding="utf-8-sig"
    )

    assert "HISTORY 001" in content
    assert "HISTORY 002" in content

    assert "Artist A" in content
    assert "Opening Track" in content


def test_transitions_csv_content(
    tmp_path,
):
    sessions, intelligence = (
        build_data()
    )

    reports = generate_history_reports(
        sessions,
        intelligence,
        tmp_path,
    )

    content = reports[
        "transitions"
    ].read_text(
        encoding="utf-8-sig"
    )

    assert "bpm_change" in content

    assert "Opening Track" in content
    assert "Middle Track" in content
    assert "Closing Track" in content

    assert "4" in content
    assert "2" in content
    assert "6" in content