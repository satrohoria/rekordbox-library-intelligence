import csv

import pytest

from rekordbox_library_intelligence.ground_truth_template import (
    select_ground_truth_sample,
    write_ground_truth_template,
)
from rekordbox_library_intelligence.parser import Track


def make_track(
    track_id: int,
) -> Track:
    return Track(
        track_id=track_id,
        title=f"Track {track_id}",
        artist=f"Artist {track_id}",
        bpm=120 + track_id,
        bitrate=320,
        play_count=track_id,
        rating=204,
        location=(
            f"file://localhost/"
            f"C:/Music/{track_id}.mp3"
        ),
        genre="House",
    )


def build_tracks(
    count: int = 20,
) -> list[Track]:
    return [
        make_track(track_id)
        for track_id in range(
            1,
            count + 1,
        )
    ]


def test_sample_has_requested_size():
    tracks = build_tracks(20)

    selected = select_ground_truth_sample(
        tracks,
        sample_size=5,
        seed=42,
    )

    assert len(selected) == 5


def test_sample_is_reproducible():
    tracks = build_tracks(30)

    first = select_ground_truth_sample(
        tracks,
        sample_size=10,
        seed=42,
    )

    second = select_ground_truth_sample(
        tracks,
        sample_size=10,
        seed=42,
    )

    assert [
        track.track_id
        for track in first
    ] == [
        track.track_id
        for track in second
    ]


def test_sample_larger_than_library():
    tracks = build_tracks(5)

    selected = select_ground_truth_sample(
        tracks,
        sample_size=50,
        seed=42,
    )

    assert len(selected) == 5


def test_invalid_sample_size():
    tracks = build_tracks(10)

    with pytest.raises(ValueError):
        select_ground_truth_sample(
            tracks,
            sample_size=0,
        )


def test_write_ground_truth_template(
    tmp_path,
):
    tracks = build_tracks(10)

    destination = (
        tmp_path
        / "ground_truth.csv"
    )

    generated = write_ground_truth_template(
        tracks,
        destination,
        sample_size=5,
        seed=42,
    )

    assert generated.exists()

    with generated.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 5

    assert "track_id" in rows[0]
    assert "artist" in rows[0]
    assert "title" in rows[0]
    assert "bpm" in rows[0]
    assert "genre" in rows[0]
    assert "play_count" in rows[0]
    assert "rating" in rows[0]

    assert "style" in rows[0]
    assert "elements" in rows[0]
    assert "energy" in rows[0]
    assert "function" in rows[0]

    assert rows[0]["style"] == ""
    assert rows[0]["energy"] == ""