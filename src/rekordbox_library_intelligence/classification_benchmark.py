import csv
from dataclasses import dataclass
from pathlib import Path

from .classification import (
    ClassificationSuggestion,
)


@dataclass(slots=True)
class GroundTruth:
    track_id: int

    style: str | None
    elements: tuple[str, ...]
    energy: str | None
    function: str | None


@dataclass(slots=True)
class FieldBenchmark:
    evaluated: int
    correct: int
    accuracy: float | None


@dataclass(slots=True)
class ConfidenceBenchmark:
    confidence: str
    evaluated: int
    fully_correct: int
    accuracy: float | None


@dataclass(slots=True)
class ClassificationBenchmark:
    matched_tracks: int
    missing_ground_truth: int

    style: FieldBenchmark
    elements: FieldBenchmark
    energy: FieldBenchmark
    function: FieldBenchmark

    confidence_results: list[
        ConfidenceBenchmark
    ]


def _normalize(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    return value.casefold()


def _normalize_elements(
    values: tuple[str, ...],
) -> set[str]:
    return {
        value.strip().casefold()
        for value in values
        if value.strip()
    }


def _parse_elements(
    value: str | None,
) -> tuple[str, ...]:
    if not value:
        return ()

    return tuple(
        item.strip()
        for item in value.split(";")
        if item.strip()
    )


def load_ground_truth(
    csv_path: str | Path,
) -> dict[int, GroundTruth]:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Ground truth CSV not found: {path}"
        )

    results = {}

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            track_id = int(
                row["track_id"]
            )

            results[track_id] = GroundTruth(
                track_id=track_id,
                style=(
                    row.get("style")
                    or None
                ),
                elements=_parse_elements(
                    row.get("elements")
                ),
                energy=(
                    row.get("energy")
                    or None
                ),
                function=(
                    row.get("function")
                    or None
                ),
            )

    return results


def _field_result(
    evaluated: int,
    correct: int,
) -> FieldBenchmark:
    accuracy = (
        correct / evaluated * 100
        if evaluated
        else None
    )

    return FieldBenchmark(
        evaluated=evaluated,
        correct=correct,
        accuracy=accuracy,
    )


def benchmark_classifications(
    suggestions: list[
        ClassificationSuggestion
    ],
    ground_truth: dict[
        int,
        GroundTruth
    ],
) -> ClassificationBenchmark:
    style_evaluated = 0
    style_correct = 0

    elements_evaluated = 0
    elements_correct = 0

    energy_evaluated = 0
    energy_correct = 0

    function_evaluated = 0
    function_correct = 0

    matched_tracks = 0
    missing_ground_truth = 0

    confidence_totals = {
        "HIGH": [0, 0],
        "MEDIUM": [0, 0],
        "LOW": [0, 0],
        "REVIEW": [0, 0],
    }

    for suggestion in suggestions:
        truth = ground_truth.get(
            suggestion.track_id
        )

        if truth is None:
            missing_ground_truth += 1
            continue

        matched_tracks += 1

        field_matches = []

        if truth.style is not None:
            style_evaluated += 1

            match = (
                _normalize(
                    suggestion.style
                )
                == _normalize(
                    truth.style
                )
            )

            field_matches.append(match)

            if match:
                style_correct += 1

        if truth.elements:
            elements_evaluated += 1

            match = (
                _normalize_elements(
                    suggestion.elements
                )
                == _normalize_elements(
                    truth.elements
                )
            )

            field_matches.append(match)

            if match:
                elements_correct += 1

        if truth.energy is not None:
            energy_evaluated += 1

            match = (
                _normalize(
                    suggestion.energy
                )
                == _normalize(
                    truth.energy
                )
            )

            field_matches.append(match)

            if match:
                energy_correct += 1

        if truth.function is not None:
            function_evaluated += 1

            match = (
                _normalize(
                    suggestion.function
                )
                == _normalize(
                    truth.function
                )
            )

            field_matches.append(match)

            if match:
                function_correct += 1

        confidence = (
            suggestion.confidence
        )

        if field_matches:
            confidence_totals[
                confidence
            ][0] += 1

            if all(field_matches):
                confidence_totals[
                    confidence
                ][1] += 1

    confidence_results = []

    for confidence in (
        "HIGH",
        "MEDIUM",
        "LOW",
        "REVIEW",
    ):
        evaluated, correct = (
            confidence_totals[
                confidence
            ]
        )

        accuracy = (
            correct / evaluated * 100
            if evaluated
            else None
        )

        confidence_results.append(
            ConfidenceBenchmark(
                confidence=confidence,
                evaluated=evaluated,
                fully_correct=correct,
                accuracy=accuracy,
            )
        )

    return ClassificationBenchmark(
        matched_tracks=matched_tracks,
        missing_ground_truth=(
            missing_ground_truth
        ),
        style=_field_result(
            style_evaluated,
            style_correct,
        ),
        elements=_field_result(
            elements_evaluated,
            elements_correct,
        ),
        energy=_field_result(
            energy_evaluated,
            energy_correct,
        ),
        function=_field_result(
            function_evaluated,
            function_correct,
        ),
        confidence_results=(
            confidence_results
        ),
    )


def format_classification_benchmark(
    benchmark: ClassificationBenchmark,
) -> str:
    def accuracy(
        field: FieldBenchmark,
    ) -> str:
        if field.accuracy is None:
            return "N/A"

        return (
            f"{field.accuracy:.1f}% "
            f"({field.correct}/"
            f"{field.evaluated})"
        )

    lines = [
        "Rekordbox Library Intelligence",
        "=" * 32,
        "Classification Benchmark",
        "",
        (
            "Matched tracks:       "
            f"{benchmark.matched_tracks}"
        ),
        (
            "Without ground truth: "
            f"{benchmark.missing_ground_truth}"
        ),
        "",
        "FIELD ACCURACY",
        (
            f"STYLE:    "
            f"{accuracy(benchmark.style)}"
        ),
        (
            f"ELEMENTS: "
            f"{accuracy(benchmark.elements)}"
        ),
        (
            f"ENERGY:   "
            f"{accuracy(benchmark.energy)}"
        ),
        (
            f"FUNCTION: "
            f"{accuracy(benchmark.function)}"
        ),
        "",
        "CONFIDENCE ACCURACY",
    ]

    for item in (
        benchmark.confidence_results
    ):
        if item.accuracy is None:
            result = "N/A"
        else:
            result = (
                f"{item.accuracy:.1f}% "
                f"({item.fully_correct}/"
                f"{item.evaluated})"
            )

        lines.append(
            f"{item.confidence:7s}: "
            f"{result}"
        )

    return "\n".join(lines)