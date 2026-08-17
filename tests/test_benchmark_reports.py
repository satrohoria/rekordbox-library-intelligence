import csv
import json
from collections import Counter

from rekordbox_library_intelligence.benchmark_reports import (
    generate_benchmark_reports,
)
from rekordbox_library_intelligence.classification_diagnostics import (
    ClassificationDiagnostics,
    FieldDiagnostics,
)


def make_diagnostics():
    energy = FieldDiagnostics(
        field="ENERGY",
        evaluated=100,
        predictions_present=100,
        correct=95,
        missing_predictions=0,
        mismatch_pairs=Counter(
            {
                (
                    "Peak",
                    "Strong",
                ): 3,
                (
                    "Groove",
                    "Warm",
                ): 2,
            }
        ),
    )

    function = FieldDiagnostics(
        field="FUNCTION",
        evaluated=20,
        predictions_present=16,
        correct=15,
        missing_predictions=4,
        mismatch_pairs=Counter(
            {
                (
                    "Weapon",
                    "-",
                ): 3,
                (
                    "Closer",
                    "Opener",
                ): 2,
            }
        ),
    )

    return ClassificationDiagnostics(
        energy=energy,
        function=function,
    )


def test_generate_benchmark_report_files(
    tmp_path,
):
    diagnostics = make_diagnostics()

    generated = generate_benchmark_reports(
        diagnostics,
        tmp_path,
        dataset_tracks=120,
        ground_truth_tracks=100,
    )

    assert generated["summary"].exists()

    assert (
        generated["energy_mismatches"]
        .exists()
    )

    assert (
        generated["function_mismatches"]
        .exists()
    )


def test_benchmark_summary_json(
    tmp_path,
):
    diagnostics = make_diagnostics()

    generated = generate_benchmark_reports(
        diagnostics,
        tmp_path,
        dataset_tracks=120,
        ground_truth_tracks=100,
    )

    with generated["summary"].open(
        "r",
        encoding="utf-8",
    ) as file:
        summary = json.load(file)

    assert (
        summary["schema_version"]
        == "1.0"
    )

    assert (
        summary["dataset"]["tracks"]
        == 120
    )

    assert (
        summary[
            "dataset"
        ][
            "ground_truth_tracks"
        ]
        == 100
    )

    assert (
        summary["energy"]["correct"]
        == 95
    )

    assert (
        summary[
            "energy"
        ][
            "accuracy_percent"
        ]
        == 95.0
    )

    assert (
        summary[
            "energy"
        ][
            "coverage_percent"
        ]
        == 100.0
    )

    assert (
        summary["function"]["correct"]
        == 15
    )

    assert (
        summary[
            "function"
        ][
            "accuracy_percent"
        ]
        == 75.0
    )

    assert (
        summary[
            "function"
        ][
            "coverage_percent"
        ]
        == 80.0
    )


def test_energy_mismatch_csv(
    tmp_path,
):
    diagnostics = make_diagnostics()

    generated = generate_benchmark_reports(
        diagnostics,
        tmp_path,
        dataset_tracks=120,
        ground_truth_tracks=100,
    )

    with generated[
        "energy_mismatches"
    ].open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 2

    assert rows[0] == {
        "expected": "Peak",
        "predicted": "Strong",
        "count": "3",
    }

    assert rows[1] == {
        "expected": "Groove",
        "predicted": "Warm",
        "count": "2",
    }


def test_calibration_versions_are_recorded(
    tmp_path,
):
    diagnostics = make_diagnostics()

    generated = generate_benchmark_reports(
        diagnostics,
        tmp_path,
        dataset_tracks=120,
        ground_truth_tracks=100,
        energy_calibration=(
            "energy_v1"
        ),
        function_calibration=(
            "function_v1"
        ),
    )

    with generated["summary"].open(
        "r",
        encoding="utf-8",
    ) as file:
        summary = json.load(file)

    assert (
        summary[
            "calibration"
        ][
            "energy"
        ]
        == "energy_v1"
    )

    assert (
        summary[
            "calibration"
        ][
            "function"
        ]
        == "function_v1"
    )