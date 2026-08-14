from rekordbox_library_intelligence.history import (
    HistorySession,
)
from rekordbox_library_intelligence.history_intelligence import (
    analyze_history_intelligence,
    calculate_transition_stats,
    format_history_intelligence,
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
        start_bpm=(
            bpms[0]
            if bpms
            else None
        ),
        average_bpm=(
            sum(bpms) / len(bpms)
            if bpms
            else None
        ),
        end_bpm=(
            bpms[-1]
            if bpms
            else None
        ),
        minimum_bpm=(
            min(bpms)
            if bpms
            else None
        ),
        maximum_bpm=(
            max(bpms)
            if bpms
            else None
        ),
        opener=(
            tracks[0]
            if tracks
            else None
        ),
        closer=(
            tracks[-1]
            if tracks
            else None
        ),
    )


def test_repeated_tracks_across_sessions():
    track_1 = make_track(
        1,
        "Artist A",
        "Track A",
        120,
    )

    track_2 = make_track(
        2,
        "Artist B",
        "Track B",
        124,
    )

    track_3 = make_track(
        3,
        "Artist C",
        "Track C",
        128,
    )

    sessions = [
        make_session(
            "HISTORY 001",
            [
                track_1,
                track_2,
            ],
        ),
        make_session(
            "HISTORY 002",
            [
                track_2,
                track_3,
            ],
        ),
    ]

    intelligence = (
        analyze_history_intelligence(
            sessions
        )
    )

    assert (
        intelligence.sessions_analyzed
        == 2
    )

    assert (
        intelligence.unique_tracks
        == 3
    )

    assert (
        len(
            intelligence.repeated_tracks
        )
        == 1
    )

    repeated = (
        intelligence.repeated_tracks[0]
    )

    assert repeated.track.track_id == 2
    assert repeated.session_count == 2


def test_openers_and_closers():
    opener = make_track(
        1,
        "Artist A",
        "Opening Track",
        120,
    )

    middle = make_track(
        2,
        "Artist B",
        "Middle Track",
        124,
    )

    closer = make_track(
        3,
        "Artist C",
        "Closing Track",
        126,
    )

    sessions = [
        make_session(
            "HISTORY 001",
            [
                opener,
                middle,
                closer,
            ],
        ),
        make_session(
            "HISTORY 002",
            [
                opener,
                closer,
            ],
        ),
    ]

    intelligence = (
        analyze_history_intelligence(
            sessions
        )
    )

    assert (
        intelligence.top_openers[0]
        .track.track_id
        == 1
    )

    assert (
        intelligence.top_openers[0]
        .session_count
        == 2
    )

    assert (
        intelligence.top_closers[0]
        .track.track_id
        == 3
    )

    assert (
        intelligence.top_closers[0]
        .session_count
        == 2
    )


def test_average_history_bpms():
    session_1 = make_session(
        "HISTORY 001",
        [
            make_track(
                1,
                "A",
                "A",
                120,
            ),
            make_track(
                2,
                "B",
                "B",
                124,
            ),
        ],
    )

    session_2 = make_session(
        "HISTORY 002",
        [
            make_track(
                3,
                "C",
                "C",
                122,
            ),
            make_track(
                4,
                "D",
                "D",
                128,
            ),
        ],
    )

    intelligence = (
        analyze_history_intelligence(
            [
                session_1,
                session_2,
            ]
        )
    )

    assert (
        intelligence.average_opening_bpm
        == 121.0
    )

    assert (
        intelligence.average_session_bpm
        == 123.5
    )

    assert (
        intelligence.average_closing_bpm
        == 126.0
    )


def test_transition_statistics():
    session = make_session(
        "HISTORY 001",
        [
            make_track(
                1,
                "A",
                "A",
                120,
            ),
            make_track(
                2,
                "B",
                "B",
                124,
            ),
            make_track(
                3,
                "C",
                "C",
                122,
            ),
            make_track(
                4,
                "D",
                "D",
                128,
            ),
        ],
    )

    stats = calculate_transition_stats(
        [session]
    )

    # Changes:
    # 120 -> 124 = +4
    # 124 -> 122 = -2
    # 122 -> 128 = +6

    assert stats.transition_count == 3

    assert stats.average_change == (
        8 / 3
    )

    assert (
        stats.average_absolute_change
        == 4.0
    )

    assert stats.largest_increase == 6
    assert stats.largest_decrease == -2


def test_track_counts_once_per_session():
    repeated = make_track(
        1,
        "Artist A",
        "Repeated Track",
        124,
    )

    session = make_session(
        "HISTORY 001",
        [
            repeated,
            repeated,
            repeated,
        ],
    )

    intelligence = (
        analyze_history_intelligence(
            [session]
        )
    )

    # Repeated three times inside one session
    # must NOT count as three sessions.
    assert (
        intelligence.repeated_tracks
        == []
    )


def test_format_history_intelligence():
    track_1 = make_track(
        1,
        "Artist A",
        "Track A",
        120,
    )

    track_2 = make_track(
        2,
        "Artist B",
        "Track B",
        124,
    )

    sessions = [
        make_session(
            "HISTORY 001",
            [
                track_1,
                track_2,
            ],
        ),
        make_session(
            "HISTORY 002",
            [
                track_1,
                track_2,
            ],
        ),
    ]

    intelligence = (
        analyze_history_intelligence(
            sessions
        )
    )

    output = (
        format_history_intelligence(
            intelligence
        )
    )

    assert (
        "History Intelligence"
        in output
    )

    assert (
        "Sessions analyzed: 2"
        in output
    )

    assert (
        "Unique tracks played: 2"
        in output
    )

    assert (
        "MOST REPEATED TRACKS"
        in output
    )

    assert (
        "MOST USED OPENERS"
        in output
    )

    assert (
        "MOST USED CLOSERS"
        in output
    )

    assert (
        "BPM BEHAVIOR"
        in output
    )

    assert (
        "TRANSITIONS"
        in output
    )