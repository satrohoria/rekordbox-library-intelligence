from dataclasses import dataclass

from .parser import Track
from .rekordbox_playlists import (
    RekordboxPlaylist,
    resolve_playlist_tracks,
)


@dataclass(slots=True)
class HistorySession:
    name: str
    folder_path: str
    tracks: list[Track]
    track_count: int

    start_bpm: float | None
    average_bpm: float | None
    end_bpm: float | None
    minimum_bpm: float | None
    maximum_bpm: float | None

    opener: Track | None
    closer: Track | None


def is_history_playlist(
    playlist: RekordboxPlaylist,
) -> bool:
    """
    Determine whether a Rekordbox playlist represents
    a HISTORY session.
    """
    name = playlist.name.strip().upper()

    return name.startswith("HISTORY")


def analyze_history_playlist(
    playlist: RekordboxPlaylist,
    collection: list[Track],
) -> HistorySession:
    tracks = resolve_playlist_tracks(
        playlist,
        collection,
    )

    valid_bpms = [
        track.bpm
        for track in tracks
        if track.bpm is not None
        and track.bpm > 0
    ]

    if valid_bpms:
        average_bpm = (
            sum(valid_bpms)
            / len(valid_bpms)
        )

        minimum_bpm = min(valid_bpms)
        maximum_bpm = max(valid_bpms)
    else:
        average_bpm = None
        minimum_bpm = None
        maximum_bpm = None

    start_bpm = None

    for track in tracks:
        if track.bpm is not None and track.bpm > 0:
            start_bpm = track.bpm
            break

    end_bpm = None

    for track in reversed(tracks):
        if track.bpm is not None and track.bpm > 0:
            end_bpm = track.bpm
            break

    opener = tracks[0] if tracks else None
    closer = tracks[-1] if tracks else None

    return HistorySession(
        name=playlist.name,
        folder_path=playlist.folder_path,
        tracks=tracks,
        track_count=len(tracks),
        start_bpm=start_bpm,
        average_bpm=average_bpm,
        end_bpm=end_bpm,
        minimum_bpm=minimum_bpm,
        maximum_bpm=maximum_bpm,
        opener=opener,
        closer=closer,
    )


def find_history_sessions(
    playlists: list[RekordboxPlaylist],
    collection: list[Track],
) -> list[HistorySession]:
    sessions = []

    for playlist in playlists:
        if not is_history_playlist(
            playlist
        ):
            continue

        sessions.append(
            analyze_history_playlist(
                playlist,
                collection,
            )
        )

    return sessions


def format_history_session(
    session: HistorySession,
) -> str:
    def format_bpm(
        value: float | None,
    ) -> str:
        if value is None:
            return "N/A"

        return f"{value:.1f}"

    lines = [
        session.name,
        "=" * len(session.name),
        "",
        f"Tracks:      {session.track_count}",
        f"Start BPM:   {format_bpm(session.start_bpm)}",
        f"Average BPM: {format_bpm(session.average_bpm)}",
        f"End BPM:     {format_bpm(session.end_bpm)}",
        f"Minimum BPM: {format_bpm(session.minimum_bpm)}",
        f"Maximum BPM: {format_bpm(session.maximum_bpm)}",
        "",
    ]

    if session.opener is not None:
        lines.append(
            "Opening:     "
            f"{session.opener.artist} - "
            f"{session.opener.title}"
        )
    else:
        lines.append(
            "Opening:     N/A"
        )

    if session.closer is not None:
        lines.append(
            "Closing:     "
            f"{session.closer.artist} - "
            f"{session.closer.title}"
        )
    else:
        lines.append(
            "Closing:     N/A"
        )

    return "\n".join(lines)


def format_history_sessions(
    sessions: list[HistorySession],
) -> str:
    lines = [
        "Rekordbox Library Intelligence",
        "=" * 32,
        "DJ History Sessions",
        "",
        f"Sessions found: {len(sessions)}",
    ]

    if not sessions:
        lines.extend(
            [
                "",
                "No HISTORY playlists were found.",
            ]
        )

        return "\n".join(lines)

    for session in sessions:
        lines.extend(
            [
                "",
                format_history_session(
                    session
                ),
            ]
        )

    return "\n".join(lines)