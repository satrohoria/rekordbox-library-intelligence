import csv
import json
from pathlib import Path

from .analytics import LibraryAnalytics


def analytics_to_dict(
    analytics: LibraryAnalytics,
) -> dict:
    return {
        "summary": {
            "total_tracks": analytics.total_tracks,
            "played_tracks": analytics.played_tracks,
            "unplayed_tracks": analytics.unplayed_tracks,
            "total_plays": analytics.total_plays,
            "utilization_percent": round(
                analytics.utilization_percent,
                2,
            ),
            "average_bpm": (
                round(analytics.average_bpm, 2)
                if analytics.average_bpm is not None
                else None
            ),
        },
        "top_tracks": [
            {
                "track_id": track.track_id,
                "artist": track.artist,
                "title": track.title,
                "play_count": track.play_count,
                "bpm": track.bpm,
            }
            for track in analytics.top_tracks
        ],
        "top_artists": [
            {
                "artist": artist.artist,
                "total_plays": artist.total_plays,
                "track_count": artist.track_count,
            }
            for artist in analytics.top_artists
        ],
        "bpm_distribution": (
            analytics.bpm_distribution
        ),
        "rating_distribution": {
            str(stars): count
            for stars, count
            in analytics.rating_distribution.items()
        },
    }


def write_json_report(
    analytics: LibraryAnalytics,
    destination: str | Path,
) -> Path:
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = analytics_to_dict(
        analytics
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


def write_top_tracks_csv(
    analytics: LibraryAnalytics,
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
                "play_count",
                "bpm",
            ],
        )

        writer.writeheader()

        for rank, track in enumerate(
            analytics.top_tracks,
            1,
        ):
            writer.writerow(
                {
                    "rank": rank,
                    "track_id": track.track_id,
                    "artist": track.artist,
                    "title": track.title,
                    "play_count": track.play_count,
                    "bpm": track.bpm or "",
                }
            )

    return destination


def write_top_artists_csv(
    analytics: LibraryAnalytics,
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
                "artist",
                "total_plays",
                "track_count",
            ],
        )

        writer.writeheader()

        for rank, artist in enumerate(
            analytics.top_artists,
            1,
        ):
            writer.writerow(
                {
                    "rank": rank,
                    "artist": artist.artist,
                    "total_plays": artist.total_plays,
                    "track_count": artist.track_count,
                }
            )

    return destination


def write_distribution_csv(
    distribution: dict,
    destination: str | Path,
    key_name: str,
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
                key_name,
                "count",
            ],
        )

        writer.writeheader()

        for key, count in distribution.items():
            writer.writerow(
                {
                    key_name: key,
                    "count": count,
                }
            )

    return destination


def generate_reports(
    analytics: LibraryAnalytics,
    output_dir: str | Path = "output/reports",
) -> dict[str, Path]:
    output_dir = Path(output_dir)

    reports = {
        "json": write_json_report(
            analytics,
            output_dir / "analytics_summary.json",
        ),
        "top_tracks": write_top_tracks_csv(
            analytics,
            output_dir / "top_tracks.csv",
        ),
        "top_artists": write_top_artists_csv(
            analytics,
            output_dir / "top_artists.csv",
        ),
        "bpm_distribution": write_distribution_csv(
            analytics.bpm_distribution,
            output_dir / "bpm_distribution.csv",
            "bpm_range",
        ),
        "rating_distribution": write_distribution_csv(
            analytics.rating_distribution,
            output_dir / "rating_distribution.csv",
            "stars",
        ),
    }

    return reports