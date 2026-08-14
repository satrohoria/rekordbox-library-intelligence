from rekordbox_library_intelligence.classification import (
    classify_collection,
)
from rekordbox_library_intelligence.classification_benchmark import (
    benchmark_classifications,
    format_classification_benchmark,
    load_ground_truth,
)
from rekordbox_library_intelligence.parser import (
    parse_collection,
)


def test_load_ground_truth():
    truth = load_ground_truth(
        "examples/"
        "sample_classification_ground_truth.csv"
    )

    assert len(truth) == 8

    assert (
        truth[1002].style
        == "Vocal House"
    )

    assert (
        truth[1002].elements
        == ("Vocal",)
    )


def test_benchmark_matches_tracks():
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

    benchmark = benchmark_classifications(
        suggestions,
        truth,
    )

    assert (
        benchmark.matched_tracks
        == 8
    )

    assert (
        benchmark.missing_ground_truth
        == 0
    )


def test_style_accuracy():
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

    benchmark = benchmark_classifications(
        suggestions,
        truth,
    )

    assert benchmark.style.evaluated == 8

    assert (
        benchmark.style.accuracy
        is not None
    )

    assert (
        benchmark.style.accuracy
        > 80
    )


def test_benchmark_detects_difference():
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

    benchmark = benchmark_classifications(
        suggestions,
        truth,
    )

    assert (
        benchmark.energy.correct
        < benchmark.energy.evaluated
    )


def test_format_benchmark():
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

    benchmark = benchmark_classifications(
        suggestions,
        truth,
    )

    output = format_classification_benchmark(
        benchmark
    )

    assert (
        "Classification Benchmark"
        in output
    )

    assert (
        "FIELD ACCURACY"
        in output
    )

    assert (
        "CONFIDENCE ACCURACY"
        in output
    )

    assert "STYLE:" in output
    assert "ENERGY:" in output
    assert "HIGH" in output
    assert "MEDIUM" in output