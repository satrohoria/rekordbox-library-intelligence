from rekordbox_library_intelligence.classification import (
    classify_collection,
    classify_track,
)
from rekordbox_library_intelligence.parser import Track


def make_track(
    track_id: int,
    title: str,
    genre: str = "",
    bpm: float | None = 126.0,
    play_count: int = 0,
    rating: int = 0,
    artist: str = "Example Artist",
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
        genre=genre,
    )


def test_specific_house_style_wins():
    track = make_track(
        1,
        "Example Track",
        genre="Tech House",
    )

    suggestion = classify_track(
        track
    )

    assert (
        suggestion.style
        == "Tech House"
    )

    assert (
        suggestion.energy
        == "Strong"
    )

    assert (
        suggestion.confidence
        == "MEDIUM"
    )


def test_disco_and_piano_elements():
    track = make_track(
        2,
        "Piano Groove",
        genre="Nu Disco",
        bpm=124,
    )

    suggestion = classify_track(
        track
    )

    assert (
        suggestion.style
        == "Disco / Nu Disco"
    )

    assert (
        "Piano"
        in suggestion.elements
    )

    assert (
        suggestion.energy
        == "Lift"
    )


def test_energy_buckets():
    warm = classify_track(
        make_track(
            1,
            "Warm",
            bpm=118,
        )
    )

    groove = classify_track(
        make_track(
            2,
            "Groove",
            bpm=122,
        )
    )

    lift = classify_track(
        make_track(
            3,
            "Lift",
            bpm=125,
        )
    )

    strong = classify_track(
        make_track(
            4,
            "Strong",
            bpm=127,
        )
    )

    peak = classify_track(
        make_track(
            5,
            "Peak",
            bpm=128,
        )
    )

    assert warm.energy == "Warm"
    assert groove.energy == "Groove"
    assert lift.energy == "Lift"
    assert strong.energy == "Strong"
    assert peak.energy == "Peak"


def test_direct_closer_detection():
    track = make_track(
        3,
        "Last Call",
        genre="House",
        bpm=124,
    )

    suggestion = classify_track(
        track
    )

    assert (
        suggestion.energy
        == "Closer"
    )

    assert (
        suggestion.function
        == "Closer"
    )

    assert (
        suggestion.confidence
        == "HIGH"
    )


def test_peak_weapon_inference():
    track = make_track(
        4,
        "Main Floor Tool",
        genre="House",
        bpm=128,
        play_count=5,
        rating=204,
    )

    suggestion = classify_track(
        track
    )

    assert (
        suggestion.energy
        == "Peak"
    )

    assert (
        suggestion.function
        == "Weapon"
    )

    assert (
        "repeated DJ use"
        in " ".join(
            suggestion.reasons
        )
    )


def test_unknown_track_requires_review():
    track = make_track(
        5,
        "Unknown",
        genre="",
        bpm=None,
    )

    suggestion = classify_track(
        track
    )

    assert suggestion.style is None
    assert suggestion.energy is None
    assert suggestion.function is None

    assert (
        suggestion.elements
        == ()
    )

    assert (
        suggestion.confidence
        == "REVIEW"
    )


def test_classify_collection_preserves_order():
    tracks = [
        make_track(
            10,
            "Track A",
            genre="House",
        ),
        make_track(
            20,
            "Track B",
            genre="Tech House",
        ),
    ]

    results = classify_collection(
        tracks
    )

    assert len(results) == 2

    assert [
        result.track_id
        for result in results
    ] == [10, 20]