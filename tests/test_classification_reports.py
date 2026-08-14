import csv

from rekordbox_library_intelligence.classification import (
    classify_collection,
)
from rekordbox_library_intelligence.classification_reports import (
    write_classification_csv,
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


def test_write_classification_csv(
    tmp_path,
):
    tracks = [
        make_track(
            1,
            "Piano Anthem",
            genre="Vocal House",
            bpm=126,
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

    destination = (
        tmp_path
        / "classification.csv"
    )

    generated = write_classification_csv(
        suggestions,
        destination,
    )

    assert generated.exists()

    content = generated.read_text(
        encoding="utf-8-sig"
    )

    assert "track_id" in content
    assert "style" in content
    assert "elements" in content
    assert "energy" in content
    assert "function" in content
    assert "confidence" in content
    assert "reasons" in content

    assert "Vocal House" in content
    assert "Piano" in content


def test_classification_csv_filter(
    tmp_path,
):
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

    destination = (
        tmp_path
        / "classification.csv"
    )

    write_classification_csv(
        suggestions,
        destination,
        minimum_confidence="MEDIUM",
    )

    with destination.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 1
    assert rows[0]["track_id"] == "1"

    assert rows[0]["confidence"] in (
        "HIGH",
        "MEDIUM",
    )


def test_elements_are_exported(
    tmp_path,
):
    track = make_track(
        10,
        "Piano Vocal Anthem",
        genre="Vocal House",
        bpm=126,
    )

    suggestions = classify_collection(
        [track]
    )

    destination = (
        tmp_path
        / "classification.csv"
    )

    write_classification_csv(
        suggestions,
        destination,
    )

    with destination.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 1

    elements = rows[0]["elements"]

    assert "Piano" in elements
    assert "Vocal" in elements
    assert rows[0]["function"] == "Anthem"