from collections import defaultdict
from dataclasses import dataclass

from .parser import Track
from .segments import rating_to_stars


@dataclass(slots=True)
class ArtistStats:
    artist: str
    total_plays: int
    track_count: int


@dataclass(slots=True)
class LibraryAnalytics:
    total_tracks: int
    played_tracks: int
    unplayed_tracks: int
    total_plays: int
    utilization_percent: float
    average_bpm: float | None
    top_tracks: list[Track]
    top_artists: list[ArtistStats]
    rating_distribution: dict[int, int]
    bpm_distribution: dict[str, int]


def calculate_bpm_distribution(
    tracks: list[Track],
) -> dict[str, int]:
    buckets = {
        "< 110": 0,
        "110-119": 0,
        "120-124": 0,
        "125-129": 0,
        "130-139": 0,
        "140+": 0,
    }

    for track in tracks:
        if track.bpm is None or track.bpm <= 0:
            continue

        bpm = track.bpm

        if bpm < 110:
            buckets["< 110"] += 1
        elif bpm < 120:
            buckets["110-119"] += 1
        elif bpm < 125:
            buckets["120-124"] += 1
        elif bpm < 130:
            buckets["125-129"] += 1
        elif bpm < 140:
            buckets["130-139"] += 1
        else:
            buckets["140+"] += 1

    return buckets


def calculate_rating_distribution(
    tracks: list[Track],
) -> dict[int, int]:
    distribution = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    }

    for track in tracks:
        stars = rating_to_stars(
            track.rating
        )

        distribution[stars] += 1

    return distribution


def calculate_top_artists(
    tracks: list[Track],
    limit: int = 10,
) -> list[ArtistStats]:
    plays = defaultdict(int)
    track_ids = defaultdict(set)

    for track in tracks:
        artist = track.artist.strip()

        if not artist:
            artist = "Unknown Artist"

        plays[artist] += track.play_count
        track_ids[artist].add(
            track.track_id
        )

    artists = [
        ArtistStats(
            artist=artist,
            total_plays=plays[artist],
            track_count=len(
                track_ids[artist]
            ),
        )
        for artist in plays
    ]

    artists.sort(
        key=lambda item: (
            -item.total_plays,
            -item.track_count,
            item.artist.lower(),
        )
    )

    return artists[:limit]


def calculate_library_analytics(
    tracks: list[Track],
    top_limit: int = 10,
) -> LibraryAnalytics:
    total_tracks = len(tracks)

    played_tracks = sum(
        track.play_count > 0
        for track in tracks
    )

    unplayed_tracks = (
        total_tracks - played_tracks
    )

    total_plays = sum(
        track.play_count
        for track in tracks
    )

    if total_tracks:
        utilization_percent = (
            played_tracks
            / total_tracks
            * 100
        )
    else:
        utilization_percent = 0.0

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
    else:
        average_bpm = None

    top_tracks = sorted(
        tracks,
        key=lambda track: (
            -track.play_count,
            track.artist.lower(),
            track.title.lower(),
        ),
    )[:top_limit]

    return LibraryAnalytics(
        total_tracks=total_tracks,
        played_tracks=played_tracks,
        unplayed_tracks=unplayed_tracks,
        total_plays=total_plays,
        utilization_percent=(
            utilization_percent
        ),
        average_bpm=average_bpm,
        top_tracks=top_tracks,
        top_artists=calculate_top_artists(
            tracks,
            top_limit,
        ),
        rating_distribution=(
            calculate_rating_distribution(
                tracks
            )
        ),
        bpm_distribution=(
            calculate_bpm_distribution(
                tracks
            )
        ),
    )
def format_library_analytics(
    analytics: LibraryAnalytics,
) -> str:
    if analytics.average_bpm is None:
        average_bpm = "N/A"
    else:
        average_bpm = (
            f"{analytics.average_bpm:.1f}"
        )

    lines = [
        "Rekordbox Library Intelligence",
        "=" * 32,
        "DJ Library Analytics",
        "",
        f"Total tracks:        {analytics.total_tracks}",
        f"Played tracks:       {analytics.played_tracks}",
        f"Unplayed tracks:     {analytics.unplayed_tracks}",
        (
            "Library utilization: "
            f"{analytics.utilization_percent:.1f}%"
        ),
        f"Total DJ plays:      {analytics.total_plays}",
        f"Average BPM:         {average_bpm}",
        "",
        "TOP TRACKS",
    ]

    if not analytics.top_tracks:
        lines.append("No tracks available.")
    else:
        for index, track in enumerate(
            analytics.top_tracks,
            1,
        ):
            lines.append(
                f"{index:>2}. "
                f"{track.artist} - {track.title} "
                f"({track.play_count} plays)"
            )

    lines.extend(
        [
            "",
            "TOP ARTISTS",
        ]
    )

    if not analytics.top_artists:
        lines.append("No artists available.")
    else:
        for index, artist in enumerate(
            analytics.top_artists,
            1,
        ):
            lines.append(
                f"{index:>2}. "
                f"{artist.artist} "
                f"({artist.total_plays} plays, "
                f"{artist.track_count} tracks)"
            )

    lines.extend(
        [
            "",
            "BPM DISTRIBUTION",
        ]
    )

    for bucket, count in (
        analytics.bpm_distribution.items()
    ):
        lines.append(
            f"{bucket:>7}: {count}"
        )

    lines.extend(
        [
            "",
            "RATING DISTRIBUTION",
        ]
    )

    for stars, count in (
        analytics.rating_distribution.items()
    ):
        label = (
            "Unrated"
            if stars == 0
            else f"{stars} star"
            if stars == 1
            else f"{stars} stars"
        )

        lines.append(
            f"{label:>8}: {count}"
        )

    return "\n".join(lines)