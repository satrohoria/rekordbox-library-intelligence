import csv

from rekordbox_library_intelligence.rekordbox_ground_truth import (
    build_rekordbox_ground_truth,
    grouping_to_labels,
    write_rekordbox_ground_truth_csv,
)
from rekordbox_library_intelligence.parser import Track


def make_track(
    track_id: int,
    grouping: str,
) -> Track:
    return Track(
        track_id=track_id,
        title=f"Track {track_id}",
        artist=f"Artist {track_id}",
        bpm=126.0,
        bitrate=320,
        play_count=1,
        rating=204,
        location=(
            f"file://localhost/"
            f"C:/Music/{track_id}.mp3"
        ),
        genre="House",
        grouping=grouping,
    )


def test_grouping_energy_mapping():
    assert grouping_to_labels(
        "Forte"
    ) == (
        "Strong",
        None,
    )

    assert grouping_to_labels(
        "Construção"
    ) == (
        "Lift",
        None,
    )

    assert grouping_to_labels(
        "Groove"
    ) == (
        "Groove",
        None,
    )


def test_grouping_function_mapping():
    assert grouping_to_labels(
        "Peak / bomba"
    ) == (
        "Peak",
        "Weapon",
    )

    assert grouping_to_labels(
        "Warm / início"
    ) == (
        "Warm",
        "Opener",
    )

    assert grouping_to_labels(
        "Closer / especial"
    ) == (
        "Closer",
        "Closer",
    )


def test_grouping_normalization():
    assert grouping_to_labels(
        "  CONSTRUÇÃO  "
    ) == (
        "Lift",
        None,
    )

    assert grouping_to_labels(
        "Warm / INÍCIO"
    ) == (
        "Warm",
        "Opener",
    )


def test_unknown_grouping_is_ignored():
    assert grouping_to_labels(
        ""
    ) == (
        None,
        None,
    )

    assert grouping_to_labels(
        "Unknown"
    ) == (
        None,
        None,
    )


def test_build_rekordbox_ground_truth():
    tracks = [
        make_track(
            1,
            "Forte",
        ),
        make_track(
            2,
            "Peak / bomba",
        ),
        make_track(
            3,
            "",
        ),
        make_track(
            4,
            "Unknown",
        ),
    ]

    truth = (
        build_rekordbox_ground_truth(
            tracks
        )
    )

    assert len(truth) == 2

    assert (
        truth[1].energy
        == "Strong"
    )

    assert (
        truth[1].function
        is None
    )

    assert (
        truth[2].energy
        == "Peak"
    )

    assert (
        truth[2].function
        == "Weapon"
    )


def test_write_rekordbox_ground_truth_csv(
    tmp_path,
):
    tracks = [
        make_track(
            1,
            "Forte",
        ),
        make_track(
            2,
            "Construção",
        ),
        make_track(
            3,
            "Peak / bomba",
        ),
        make_track(
            4,
            "",
        ),
    ]

    destination = (
        tmp_path
        / "ground_truth.csv"
    )

    generated = (
        write_rekordbox_ground_truth_csv(
            tracks,
            destination,
        )
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

    assert len(rows) == 3

    assert (
        rows[0]["source_grouping"]
        == "Forte"
    )

    assert (
        rows[0]["energy"]
        == "Strong"
    )

    assert (
        rows[0]["function"]
        == ""
    )

    assert (
        rows[1]["source_grouping"]
        == "Construção"
    )

    assert (
        rows[1]["energy"]
        == "Lift"
    )

    assert (
        rows[2]["source_grouping"]
        == "Peak / bomba"
    )

    assert (
        rows[2]["energy"]
        == "Peak"
    )

    assert (
        rows[2]["function"]
        == "Weapon"
    )