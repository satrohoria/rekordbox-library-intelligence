import csv
import json
from pathlib import Path

from .classification_diagnostics import (
    ClassificationDiagnostics,
    FieldDiagnostics,
)


def _safe_percentage(
    numerator: int,
    denominator: int,
) -> float:
    if denominator == 0:
        return 0.0

    return round(
        numerator / denominator * 100,
        1,
    )


def _field_summary(
    diagnostics: FieldDiagnostics,
) -> dict:
    return {
        "evaluated": diagnostics.evaluated,
        "predictions_present": (
            diagnostics.predictions_present
        ),
        "missing_predictions": (
            diagnostics.missing_predictions
        ),
        "correct": diagnostics.correct,
        "incorrect": (
            diagnostics.evaluated
            - diagnostics.correct
        ),
        "coverage_percent": _safe_percentage(
            diagnostics.predictions_present,
            diagnostics.evaluated,
        ),
        "accuracy_percent": _safe_percentage(
            diagnostics.correct,
            diagnostics.evaluated,
        ),
    }


def _write_mismatch_csv(
    diagnostics: FieldDiagnostics,
    destination: Path,
) -> Path:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with destination.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "expected",
                "predicted",
                "count",
            ],
        )

        writer.writeheader()

        for (
            expected,
            predicted,
        ), count in (
            diagnostics
            .mismatch_pairs
            .most_common()
        ):
            writer.writerow(
                {
                    "expected": expected,
                    "predicted": predicted,
                    "count": count,
                }
            )

    return destination


def generate_benchmark_reports(
    diagnostics: ClassificationDiagnostics,
    output_dir: str | Path,
    *,
    dataset_tracks: int,
    ground_truth_tracks: int,
    energy_calibration: str = "energy_v1",
    function_calibration: str = "function_v1",
) -> dict[str, Path]:
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        output_dir
        / "benchmark_summary.json"
    )

    energy_path = (
        output_dir
        / "energy_mismatches.csv"
    )

    function_path = (
        output_dir
        / "function_mismatches.csv"
    )

    summary = {
        "schema_version": "1.0",
        "dataset": {
            "tracks": dataset_tracks,
            "ground_truth_tracks": (
                ground_truth_tracks
            ),
        },
        "calibration": {
            "energy": energy_calibration,
            "function": function_calibration,
        },
        "energy": _field_summary(
            diagnostics.energy
        ),
        "function": _field_summary(
            diagnostics.function
        ),
    }

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2,
        )

        file.write("\n")

    _write_mismatch_csv(
        diagnostics.energy,
        energy_path,
    )

    _write_mismatch_csv(
        diagnostics.function,
        function_path,
    )

    return {
        "summary": summary_path,
        "energy_mismatches": energy_path,
        "function_mismatches": function_path,
    }