from rekordbox_library_intelligence.analytics import (
    calculate_bpm_distribution,
    calculate_library_analytics,
    calculate_rating_distribution,
    calculate_top_artists,
    format_library_analytics,
)
from rekordbox_library_intelligence.parser import Track


def make_track(
    track_id: int,
    artist: str,
    title: str,
    play_count: int,
    rating: int = 0,
    bpm: float | None = 126.0,
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


def test_library_utilization():
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
            1,
        ),
        make_track(
            3,
            "Artist C",
            "Track C",
            0,
        ),
        make_track(
            4,
            "Artist D",
            "Track D",
            0,
        ),
    ]

    analytics = calculate_library_analytics(
        tracks
    )

    assert analytics.total_tracks == 4
    assert analytics.played_tracks == 2
    assert analytics.unplayed_tracks == 2
    assert analytics.total_plays == 6
    assert analytics.utilization_percent == 50.0


def test_top_tracks():
    tracks = [
        make_track(
            1,
            "Artist A",
            "Track A",
            2,
        ),
        make_track(
            2,
            "Artist B",
            "Track B",
            10,
        ),
        make_track(
            3,
            "Artist C",
            "Track C",
            5,
        ),
    ]

    analytics = calculate_library_analytics(
        tracks
    )

    assert analytics.top_tracks[0].track_id == 2
    assert analytics.top_tracks[1].track_id == 3
    assert analytics.top_tracks[2].track_id == 1


def test_top_artists_aggregates_multiple_tracks():
    tracks = [
        make_track(
            1,
            "Artist A",
            "Track 1",
            4,
        ),
        make_track(
            2,
            "Artist A",
            "Track 2",
            3,
        ),
        make_track(
            3,
            "Artist B",
            "Track 3",
            5,
        ),
    ]

    artists = calculate_top_artists(
        tracks
    )

    assert artists[0].artist == "Artist A"
    assert artists[0].total_plays == 7
    assert artists[0].track_count == 2

    assert artists[1].artist == "Artist B"
    assert artists[1].total_plays == 5


def test_rating_distribution():
    tracks = [
        make_track(
            1,
            "A",
            "A",
            0,
            rating=0,
        ),
        make_track(
            2,
            "B",
            "B",
            0,
            rating=153,
        ),
        make_track(
            3,
            "C",
            "C",
            0,
            rating=204,
        ),
        make_track(
            4,
            "D",
            "D",
            0,
            rating=204,
        ),
    ]

    distribution = (
        calculate_rating_distribution(
            tracks
        )
    )

    assert distribution[0] == 1
    assert distribution[3] == 1
    assert distribution[4] == 2


def test_bpm_distribution():
    tracks = [
        make_track(
            1,
            "A",
            "A",
            0,
            bpm=108,
        ),
        make_track(
            2,
            "B",
            "B",
            0,
            bpm=118,
        ),
        make_track(
            3,
            "C",
            "C",
            0,
            bpm=123,
        ),
        make_track(
            4,
            "D",
            "D",
            0,
            bpm=127,
        ),
        make_track(
            5,
            "E",
            "E",
            0,
            bpm=132,
        ),
        make_track(
            6,
            "F",
            "F",
            0,
            bpm=145,
        ),
    ]

    distribution = (
        calculate_bpm_distribution(
            tracks
        )
    )

    assert distribution["< 110"] == 1
    assert distribution["110-119"] == 1
    assert distribution["120-124"] == 1
    assert distribution["125-129"] == 1
    assert distribution["130-139"] == 1
    assert distribution["140+"] == 1
def test_format_library_analytics():
    tracks = [
        make_track(
            1,
            "Artist A",
            "Track A",
            5,
            rating=204,
            bpm=126,
        ),
        make_track(
            2,
            "Artist B",
            "Track B",
            0,
            rating=153,
            bpm=124,
        ),
    ]

    analytics = calculate_library_analytics(
        tracks
    )

    output = format_library_analytics(
        analytics
    )

    assert "DJ Library Analytics" in output
    assert "Total tracks:        2" in output
    assert "Played tracks:       1" in output
    assert "Library utilization: 50.0%" in output
    assert "Total DJ plays:      5" in output
    assert "Artist A - Track A" in output
    assert "TOP ARTISTS" in output
    assert "BPM DISTRIBUTION" in output
    assert "RATING DISTRIBUTION" in output