import csv
import json
from pathlib import Path

from .history import HistorySession
from .history_intelligence import (
    HistoryIntelligence,
    TrackSessionStats,
)


def _track_reference(track):
    if track is None:
        return None

    return {
        "track_id": track.track_id,
        "artist": track.artist,
        "title": track.title,
        "bpm": track.bpm,
    }


def _track_stats_to_dict(
    items: list[TrackSessionStats],
) -> list[dict]:
    return [
        {
            "track_id": item.track.track_id,
            "artist": item.track.artist,
            "title": item.track.title,
            "bpm": item.track.bpm,
            "session_count": item.session_count,
        }
        for item in items
    ]


def history_to_dict(
    sessions: list[HistorySession],
    intelligence: HistoryIntelligence,
) -> dict:
    transitions = intelligence.transitions

    return {
        "summary": {
            "sessions_analyzed": (
                intelligence.sessions_analyzed
            ),
            "unique_tracks": (
                intelligence.unique_tracks
            ),
            "average_opening_bpm": (
                round(
                    intelligence.average_opening_bpm,
                    2,
                )
                if intelligence.average_opening_bpm
                is not None
                else None
            ),
            "average_session_bpm": (
                round(
                    intelligence.average_session_bpm,
                    2,
                )
                if intelligence.average_session_bpm
                is not None
                else None
            ),
            "average_closing_bpm": (
                round(
                    intelligence.average_closing_bpm,
                    2,
                )
                if intelligence.average_closing_bpm
                is not None
                else None
            ),
            "transitions": {
                "count": (
                    transitions.transition_count
                ),
                "average_change": (
                    round(
                        transitions.average_change,
                        2,
                    )
                    if transitions.average_change
                    is not None
                    else None
                ),
                "average_absolute_change": (
                    round(
                        transitions.average_absolute_change,
                        2,
                    )
                    if transitions.average_absolute_change
                    is not None
                    else None
                ),
                "largest_increase": (
                    transitions.largest_increase
                ),
                "largest_decrease": (
                    transitions.largest_decrease
                ),
            },
        },
        "sessions": [
            {
                "name": session.name,
                "folder_path": session.folder_path,
                "track_count": session.track_count,
                "start_bpm": session.start_bpm,
                "average_bpm": (
                    round(
                        session.average_bpm,
                        2,
                    )
                    if session.average_bpm
                    is not None
                    else None
                ),
                "end_bpm": session.end_bpm,
                "minimum_bpm": session.minimum_bpm,
                "maximum_bpm": session.maximum_bpm,
                "opener": _track_reference(
                    session.opener
                ),
                "closer": _track_reference(
                    session.closer
                ),
            }
            for session in sessions
        ],
        "repeated_tracks": (
            _track_stats_to_dict(
                intelligence.repeated_tracks
            )
        ),
        "openers": (
            _track_stats_to_dict(
                intelligence.top_openers
            )
        ),
        "closers": (
            _track_stats_to_dict(
                intelligence.top_closers
            )
        ),
    }


def write_history_json(
    sessions: list[HistorySession],
    intelligence: HistoryIntelligence,
    destination: str | Path,
) -> Path:
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = history_to_dict(
        sessions,
        intelligence,
    )

    destination.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return destination


def write_sessions_csv(
    sessions: list[HistorySession],
    destination: str | Path,
) -> Path:
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "session",
        "folder_path",
        "track_count",
        "start_bpm",
        "average_bpm",
        "end_bpm",
        "minimum_bpm",
        "maximum_bpm",
        "opener_artist",
        "opener_title",
        "closer_artist",
        "closer_title",
    ]

    with destination.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for session in sessions:
            writer.writerow(
                {
                    "session": session.name,
                    "folder_path": (
                        session.folder_path
                    ),
                    "track_count": (
                        session.track_count
                    ),
                    "start_bpm": (
                        session.start_bpm
                        if session.start_bpm
                        is not None
                        else ""
                    ),
                    "average_bpm": (
                        round(
                            session.average_bpm,
                            2,
                        )
                        if session.average_bpm
                        is not None
                        else ""
                    ),
                    "end_bpm": (
                        session.end_bpm
                        if session.end_bpm
                        is not None
                        else ""
                    ),
                    "minimum_bpm": (
                        session.minimum_bpm
                        if session.minimum_bpm
                        is not None
                        else ""
                    ),
                    "maximum_bpm": (
                        session.maximum_bpm
                        if session.maximum_bpm
                        is not None
                        else ""
                    ),
                    "opener_artist": (
                        session.opener.artist
                        if session.opener
                        else ""
                    ),
                    "opener_title": (
                        session.opener.title
                        if session.opener
                        else ""
                    ),
                    "closer_artist": (
                        session.closer.artist
                        if session.closer
                        else ""
                    ),
                    "closer_title": (
                        session.closer.title
                        if session.closer
                        else ""
                    ),
                }
            )

    return destination


def write_track_stats_csv(
    items: list[TrackSessionStats],
    destination: str | Path,
) -> Path:
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with destination.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "rank",
                "track_id",
                "artist",
                "title",
                "bpm",
                "session_count",
            ],
        )

        writer.writeheader()

        for rank, item in enumerate(
            items,
            1,
        ):
            writer.writerow(
                {
                    "rank": rank,
                    "track_id": (
                        item.track.track_id
                    ),
                    "artist": (
                        item.track.artist
                    ),
                    "title": (
                        item.track.title
                    ),
                    "bpm": (
                        item.track.bpm
                        if item.track.bpm
                        is not None
                        else ""
                    ),
                    "session_count": (
                        item.session_count
                    ),
                }
            )

    return destination


def write_transitions_csv(
    sessions: list[HistorySession],
    destination: str | Path,
) -> Path:
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "session",
        "position",
        "from_track_id",
        "from_artist",
        "from_title",
        "from_bpm",
        "to_track_id",
        "to_artist",
        "to_title",
        "to_bpm",
        "bpm_change",
        "absolute_change",
    ]

    with destination.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for session in sessions:
            for position, (
                current,
                following,
            ) in enumerate(
                zip(
                    session.tracks,
                    session.tracks[1:],
                ),
                1,
            ):
                if (
                    current.bpm is None
                    or following.bpm is None
                    or current.bpm <= 0
                    or following.bpm <= 0
                ):
                    continue

                change = (
                    following.bpm
                    - current.bpm
                )

                writer.writerow(
                    {
                        "session": (
                            session.name
                        ),
                        "position": position,
                        "from_track_id": (
                            current.track_id
                        ),
                        "from_artist": (
                            current.artist
                        ),
                        "from_title": (
                            current.title
                        ),
                        "from_bpm": (
                            current.bpm
                        ),
                        "to_track_id": (
                            following.track_id
                        ),
                        "to_artist": (
                            following.artist
                        ),
                        "to_title": (
                            following.title
                        ),
                        "to_bpm": (
                            following.bpm
                        ),
                        "bpm_change": (
                            change
                        ),
                        "absolute_change": (
                            abs(change)
                        ),
                    }
                )

    return destination


def generate_history_reports(
    sessions: list[HistorySession],
    intelligence: HistoryIntelligence,
    output_dir: str | Path = (
        "output/history_reports"
    ),
) -> dict[str, Path]:
    output_dir = Path(output_dir)

    reports = {
        "summary": write_history_json(
            sessions,
            intelligence,
            output_dir
            / "history_summary.json",
        ),
        "sessions": write_sessions_csv(
            sessions,
            output_dir
            / "sessions.csv",
        ),
        "repeated_tracks": (
            write_track_stats_csv(
                intelligence.repeated_tracks,
                output_dir
                / "repeated_tracks.csv",
            )
        ),
        "openers": write_track_stats_csv(
            intelligence.top_openers,
            output_dir
            / "openers.csv",
        ),
        "closers": write_track_stats_csv(
            intelligence.top_closers,
            output_dir
            / "closers.csv",
        ),
        "transitions": (
            write_transitions_csv(
                sessions,
                output_dir
                / "transitions.csv",
            )
        ),
    }

    return reports