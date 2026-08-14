import json

from rekordbox_library_intelligence.analytics import (
    calculate_library_analytics,
)
from rekordbox_library_intelligence.parser import Track
from rekordbox_library_intelligence.reports import (
    analytics_to_dict,
    generate_reports,
    write_json_report,
)


def make_track(
    track_id: int,
    artist: str,
    title: str,
    play_count: int,
    rating: int = 204,
    bpm: float = 126.0,
) -> Track:
    return Track(
        track_id=track_id,
        title=title,
        artist=artist,
        bpm=bpm,
        bitrate=320,
        play_count=play_count,
        rating=rating,
        location=(
            f"file://localhost/"
            f"C:/Music/{track_id}.mp3"
        ),
        genre="House",
    )


def test_analytics_to_dict():
    tracks = [
        make_track(
            1,
            "Artist A",
            "Track A",
            5,
        ),
        make_track(
            2,
            "Artist B",
            "Track B",
            0,
        ),
    ]

    analytics = calculate_library_analytics(
        tracks
    )

    data = analytics_to_dict(
        analytics
    )

    assert data["summary"]["total_tracks"] == 2
    assert data["summary"]["played_tracks"] == 1
    assert data["summary"]["total_plays"] == 5
    assert len(data["top_tracks"]) == 2


def test_write_json_report(tmp_path):
    tracks = [
        make_track(
            1,
            "Artist A",
            "Track A",
            5,
        )
    ]

    analytics = calculate_library_analytics(
        tracks
    )

    destination = (
        tmp_path
        / "analytics.json"
    )

    write_json_report(
        analytics,
        destination,
    )

    assert destination.exists()

    data = json.loads(
        destination.read_text(
            encoding="utf-8"
        )
    )

    assert data["summary"]["total_tracks"] == 1
    assert data["top_tracks"][0]["artist"] == "Artist A"


def test_generate_reports_creates_files(
    tmp_path,
):
    tracks = [
        make_track(
            1,
            "Artist A",
            "Track A",
            5,
            bpm=126,
        ),
        make_track(
            2,
            "Artist B",
            "Track B",
            2,
            bpm=124,
        ),
    ]

    analytics = calculate_library_analytics(
        tracks
    )

    reports = generate_reports(
        analytics,
        tmp_path,
    )

    assert reports["json"].exists()
    assert reports["top_tracks"].exists()
    assert reports["top_artists"].exists()
    assert reports["bpm_distribution"].exists()
    assert reports["rating_distribution"].exists()


def test_csv_reports_have_expected_content(
    tmp_path,
):
    tracks = [
        make_track(
            1,
            "Artist A",
            "Track A",
            5,
        )
    ]

    analytics = calculate_library_analytics(
        tracks
    )

    reports = generate_reports(
        analytics,
        tmp_path,
    )

    tracks_csv = reports[
        "top_tracks"
    ].read_text(
        encoding="utf-8-sig"
    )

    artists_csv = reports[
        "top_artists"
    ].read_text(
        encoding="utf-8-sig"
    )

    assert "Artist A" in tracks_csv
    assert "Track A" in tracks_csv
    assert "play_count" in tracks_csv

    assert "Artist A" in artists_csv
    assert "total_plays" in artists_csv