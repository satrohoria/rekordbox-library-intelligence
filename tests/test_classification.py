from rekordbox_library_intelligence.classification import (
    classify_function,
    classify_energy,
    classify_collection,
    classify_track,
    filter_classifications,
    format_classification_preview,
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
            bpm=129,
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
        bpm=129,
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
def test_filter_classifications_by_confidence():
    tracks = [
        make_track(
            1,
            "Last Call",
            genre="House",
            bpm=124,
        ),
        make_track(
            2,
            "House Track",
            genre="House",
            bpm=126,
        ),
        make_track(
            3,
            "Piano",
            genre="",
            bpm=None,
        ),
        make_track(
            4,
            "Unknown",
            genre="",
            bpm=None,
        ),
    ]

    suggestions = classify_collection(
        tracks
    )

    filtered = filter_classifications(
        suggestions,
        minimum_confidence="MEDIUM",
    )

    assert all(
        suggestion.confidence
        in ("HIGH", "MEDIUM")
        for suggestion in filtered
    )

    assert len(filtered) == 2


def test_format_classification_preview():
    tracks = [
        make_track(
            1,
            "Last Call",
            genre="House",
            bpm=124,
        ),
        make_track(
            2,
            "Unknown",
            genre="",
            bpm=None,
        ),
    ]

    suggestions = classify_collection(
        tracks
    )

    output = format_classification_preview(
        suggestions
    )

    assert (
        "Classification Preview"
        in output
    )

    assert (
        "Tracks analyzed: 2"
        in output
    )

    assert (
        "CONFIDENCE SUMMARY"
        in output
    )

    assert "STYLE:" in output
    assert "ELEMENTS:" in output
    assert "ENERGY:" in output
    assert "FUNCTION:" in output
    assert "CONFIDENCE:" in output

    assert "DRY-RUN ONLY" in output

    assert (
        "No Rekordbox data or audio files "
        "were modified."
        in output
    )
def test_energy_calibrated_bpm_boundaries():
    cases = [
        (119.9, "Warm"),
        (120.0, "Groove"),
        (122.9, "Groove"),
        (123.0, "Lift"),
        (125.9, "Lift"),
        (126.0, "Strong"),
        (128.9, "Strong"),
        (129.0, "Peak"),
    ]

    for bpm, expected in cases:
        track = Track(
            track_id=9999,
            title="Calibration Track",
            artist="Calibration Artist",
            bpm=bpm,
            bitrate=320,
            play_count=0,
            rating=0,
            location="",
            genre="House",
        )

        energy, reason = classify_energy(
            track
        )

        assert energy == expected
        assert reason == f"BPM {bpm:.1f}"
def test_function_energy_fallback():
    peak_track = make_track(
        9001,
        "Regular Club Track",
        genre="House",
        bpm=129,
        play_count=0,
        rating=0,
    )

    warm_track = make_track(
        9002,
        "Early Evening Track",
        genre="House",
        bpm=118,
        play_count=0,
        rating=0,
    )

    strong_track = make_track(
        9003,
        "Regular Strong Track",
        genre="House",
        bpm=127,
        play_count=0,
        rating=0,
    )

    peak_function = classify_function(
        peak_track,
        "Peak",
    )

    warm_function = classify_function(
        warm_track,
        "Warm",
    )

    strong_function = classify_function(
        strong_track,
        "Strong",
    )

    assert peak_function == (
        "Weapon",
        "Peak energy suggests Weapon",
        False,
    )

    assert warm_function == (
        "Opener",
        "Warm energy suggests Opener",
        False,
    )

    assert strong_function == (
        None,
        None,
        False,
    )


def test_direct_function_overrides_energy_fallback():
    track = make_track(
        9004,
        "Midnight Bridge Tool",
        genre="House",
        bpm=129,
        play_count=0,
        rating=0,
    )

    function = classify_function(
        track,
        "Peak",
    )

    assert function == (
        "Bridge",
        "keyword suggests Bridge",
        True,
    )