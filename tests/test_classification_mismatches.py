from rekordbox_library_intelligence.classification import (
    classify_collection,
)
from rekordbox_library_intelligence.classification_benchmark import (
    load_ground_truth,
)
from rekordbox_library_intelligence.classification_mismatches import (
    find_classification_mismatches,
    format_classification_mismatches,
)
from rekordbox_library_intelligence.parser import (
    parse_collection,
)


def build_data():
    tracks = parse_collection(
        "examples/sample_collection.xml"
    )

    suggestions = classify_collection(
        tracks
    )

    truth = load_ground_truth(
        "examples/"
        "sample_classification_ground_truth.csv"
    )

    return suggestions, truth


def test_find_mismatches():
    suggestions, truth = build_data()

    mismatches = (
        find_classification_mismatches(
            suggestions,
            truth,
        )
    )

    assert len(mismatches) == 1

    assert (
        mismatches[0].track_id
        == 1007
    )


def test_detect_energy_mismatch():
    suggestions, truth = build_data()

    mismatches = (
        find_classification_mismatches(
            suggestions,
            truth,
        )
    )

    mismatch = (
        mismatches[0]
        .mismatches[0]
    )

    assert (
        mismatch.field
        == "ENERGY"
    )

    assert (
        mismatch.expected
        == "Low"
    )

    assert (
        mismatch.predicted
        == "-"
    )


def test_mismatch_keeps_confidence():
    suggestions, truth = build_data()

    mismatches = (
        find_classification_mismatches(
            suggestions,
            truth,
        )
    )

    assert (
        mismatches[0].confidence
        == "LOW"
    )


def test_format_mismatches():
    suggestions, truth = build_data()

    mismatches = (
        find_classification_mismatches(
            suggestions,
            truth,
        )
    )

    output = (
        format_classification_mismatches(
            mismatches
        )
    )

    assert (
        "Classification Mismatches"
        in output
    )

    assert (
        "Tracks with mismatches: 1"
        in output
    )

    assert (
        "TrackID 1007"
        in output
    )

    assert (
        "Night Assembly - Golden Room"
        in output
    )

    assert (
        "Confidence: LOW"
        in output
    )

    assert (
        "ENERGY"
        in output
    )

    assert (
        "Expected:  Low"
        in output
    )

    assert (
        "Predicted: -"
        in output
    )