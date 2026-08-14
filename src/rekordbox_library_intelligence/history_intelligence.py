from collections import Counter
from dataclasses import dataclass

from .history import HistorySession
from .parser import Track


@dataclass(slots=True)
class TrackSessionStats:
    track: Track
    session_count: int


@dataclass(slots=True)
class TransitionStats:
    transition_count: int
    average_change: float | None
    average_absolute_change: float | None
    largest_increase: float | None
    largest_decrease: float | None


@dataclass(slots=True)
class HistoryIntelligence:
    sessions_analyzed: int
    unique_tracks: int

    repeated_tracks: list[TrackSessionStats]
    top_openers: list[TrackSessionStats]
    top_closers: list[TrackSessionStats]

    average_opening_bpm: float | None
    average_session_bpm: float | None
    average_closing_bpm: float | None

    transitions: TransitionStats


def _average(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return sum(values) / len(values)


def _build_track_stats(
    counter: Counter,
    track_lookup: dict[int, Track],
    limit: int,
    minimum_count: int = 1,
) -> list[TrackSessionStats]:
    results = []

    for track_id, count in counter.items():
        if count < minimum_count:
            continue

        track = track_lookup.get(
            track_id
        )

        if track is None:
            continue

        results.append(
            TrackSessionStats(
                track=track,
                session_count=count,
            )
        )

    results.sort(
        key=lambda item: (
            -item.session_count,
            item.track.artist.lower(),
            item.track.title.lower(),
        )
    )

    return results[:limit]


def calculate_transition_stats(
    sessions: list[HistorySession],
) -> TransitionStats:
    changes = []

    for session in sessions:
        for current, following in zip(
            session.tracks,
            session.tracks[1:],
        ):
            if (
                current.bpm is None
                or following.bpm is None
                or current.bpm <= 0
                or following.bpm <= 0
            ):
                continue

            changes.append(
                following.bpm
                - current.bpm
            )

    if not changes:
        return TransitionStats(
            transition_count=0,
            average_change=None,
            average_absolute_change=None,
            largest_increase=None,
            largest_decrease=None,
        )

    increases = [
        change
        for change in changes
        if change > 0
    ]

    decreases = [
        change
        for change in changes
        if change < 0
    ]

    return TransitionStats(
        transition_count=len(changes),
        average_change=(
            sum(changes)
            / len(changes)
        ),
        average_absolute_change=(
            sum(abs(change) for change in changes)
            / len(changes)
        ),
        largest_increase=(
            max(increases)
            if increases
            else None
        ),
        largest_decrease=(
            min(decreases)
            if decreases
            else None
        ),
    )


def analyze_history_intelligence(
    sessions: list[HistorySession],
    top_limit: int = 10,
) -> HistoryIntelligence:
    track_lookup: dict[int, Track] = {}

    session_usage = Counter()
    opener_usage = Counter()
    closer_usage = Counter()

    unique_track_ids = set()

    opening_bpms = []
    session_bpms = []
    closing_bpms = []

    for session in sessions:
        session_track_ids = set()

        for track in session.tracks:
            track_lookup[
                track.track_id
            ] = track

            unique_track_ids.add(
                track.track_id
            )

            session_track_ids.add(
                track.track_id
            )

        # Count a track only once per session.
        for track_id in session_track_ids:
            session_usage[
                track_id
            ] += 1

        if session.opener is not None:
            track_lookup[
                session.opener.track_id
            ] = session.opener

            opener_usage[
                session.opener.track_id
            ] += 1

        if session.closer is not None:
            track_lookup[
                session.closer.track_id
            ] = session.closer

            closer_usage[
                session.closer.track_id
            ] += 1

        if session.start_bpm is not None:
            opening_bpms.append(
                session.start_bpm
            )

        if session.average_bpm is not None:
            session_bpms.append(
                session.average_bpm
            )

        if session.end_bpm is not None:
            closing_bpms.append(
                session.end_bpm
            )

    repeated_tracks = _build_track_stats(
        session_usage,
        track_lookup,
        limit=top_limit,
        minimum_count=2,
    )

    top_openers = _build_track_stats(
        opener_usage,
        track_lookup,
        limit=top_limit,
    )

    top_closers = _build_track_stats(
        closer_usage,
        track_lookup,
        limit=top_limit,
    )

    return HistoryIntelligence(
        sessions_analyzed=len(sessions),
        unique_tracks=len(
            unique_track_ids
        ),
        repeated_tracks=repeated_tracks,
        top_openers=top_openers,
        top_closers=top_closers,
        average_opening_bpm=_average(
            opening_bpms
        ),
        average_session_bpm=_average(
            session_bpms
        ),
        average_closing_bpm=_average(
            closing_bpms
        ),
        transitions=(
            calculate_transition_stats(
                sessions
            )
        ),
    )


def format_history_intelligence(
    intelligence: HistoryIntelligence,
) -> str:
    def bpm(
        value: float | None,
    ) -> str:
        if value is None:
            return "N/A"

        return f"{value:.1f}"

    lines = [
        "Rekordbox Library Intelligence",
        "=" * 32,
        "History Intelligence",
        "",
        (
            "Sessions analyzed: "
            f"{intelligence.sessions_analyzed}"
        ),
        (
            "Unique tracks played: "
            f"{intelligence.unique_tracks}"
        ),
        "",
        "MOST REPEATED TRACKS",
    ]

    if intelligence.repeated_tracks:
        for index, item in enumerate(
            intelligence.repeated_tracks,
            1,
        ):
            lines.append(
                f"{index:>2}. "
                f"{item.track.artist} - "
                f"{item.track.title} "
                f"({item.session_count} sets)"
            )
    else:
        lines.append(
            "No tracks repeated across sessions."
        )

    lines.extend(
        [
            "",
            "MOST USED OPENERS",
        ]
    )

    if intelligence.top_openers:
        for index, item in enumerate(
            intelligence.top_openers,
            1,
        ):
            lines.append(
                f"{index:>2}. "
                f"{item.track.artist} - "
                f"{item.track.title} "
                f"({item.session_count}x)"
            )
    else:
        lines.append(
            "No opener data available."
        )

    lines.extend(
        [
            "",
            "MOST USED CLOSERS",
        ]
    )

    if intelligence.top_closers:
        for index, item in enumerate(
            intelligence.top_closers,
            1,
        ):
            lines.append(
                f"{index:>2}. "
                f"{item.track.artist} - "
                f"{item.track.title} "
                f"({item.session_count}x)"
            )
    else:
        lines.append(
            "No closer data available."
        )

    lines.extend(
        [
            "",
            "BPM BEHAVIOR",
            (
                "Average opening BPM: "
                f"{bpm(intelligence.average_opening_bpm)}"
            ),
            (
                "Average session BPM: "
                f"{bpm(intelligence.average_session_bpm)}"
            ),
            (
                "Average closing BPM: "
                f"{bpm(intelligence.average_closing_bpm)}"
            ),
            "",
            "TRANSITIONS",
            (
                "Transitions analyzed: "
                f"{intelligence.transitions.transition_count}"
            ),
            (
                "Average BPM change: "
                f"{bpm(intelligence.transitions.average_change)}"
            ),
            (
                "Average absolute change: "
                f"{bpm(intelligence.transitions.average_absolute_change)}"
            ),
            (
                "Largest increase: "
                f"{bpm(intelligence.transitions.largest_increase)}"
            ),
            (
                "Largest decrease: "
                f"{bpm(intelligence.transitions.largest_decrease)}"
            ),
        ]
    )

    return "\n".join(lines)