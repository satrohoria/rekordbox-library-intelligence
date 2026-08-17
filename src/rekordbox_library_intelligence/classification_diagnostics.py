from collections import Counter
from dataclasses import dataclass

from .classification import (
    ClassificationSuggestion,
)
from .classification_benchmark import (
    GroundTruth,
)


@dataclass(slots=True)
class FieldDiagnostics:
    field: str
    evaluated: int
    predictions_present: int
    correct: int
    missing_predictions: int
    mismatch_pairs: Counter


@dataclass(slots=True)
class ClassificationDiagnostics:
    energy: FieldDiagnostics
    function: FieldDiagnostics


def _normalize(
    value: str | None,
) -> str:
    if value is None:
        return ""

    return value.strip().casefold()


def _field_diagnostics(
    field: str,
    suggestions: list[
        ClassificationSuggestion
    ],
    ground_truth: dict[
        int,
        GroundTruth
    ],
) -> FieldDiagnostics:
    evaluated = 0
    predictions_present = 0
    correct = 0
    missing_predictions = 0

    mismatch_pairs = Counter()

    for suggestion in suggestions:
        truth = ground_truth.get(
            suggestion.track_id
        )

        if truth is None:
            continue

        expected = getattr(
            truth,
            field,
        )

        if expected is None:
            continue

        evaluated += 1

        predicted = getattr(
            suggestion,
            field,
        )

        if predicted:
            predictions_present += 1
        else:
            missing_predictions += 1

        if (
            _normalize(predicted)
            == _normalize(expected)
        ):
            correct += 1
            continue

        mismatch_pairs[
            (
                expected,
                predicted or "-",
            )
        ] += 1

    return FieldDiagnostics(
        field=field.upper(),
        evaluated=evaluated,
        predictions_present=(
            predictions_present
        ),
        correct=correct,
        missing_predictions=(
            missing_predictions
        ),
        mismatch_pairs=mismatch_pairs,
    )


def build_classification_diagnostics(
    suggestions: list[
        ClassificationSuggestion
    ],
    ground_truth: dict[
        int,
        GroundTruth
    ],
) -> ClassificationDiagnostics:
    return ClassificationDiagnostics(
        energy=_field_diagnostics(
            "energy",
            suggestions,
            ground_truth,
        ),
        function=_field_diagnostics(
            "function",
            suggestions,
            ground_truth,
        ),
    )


def format_field_diagnostics(
    diagnostics: FieldDiagnostics,
    top_limit: int = 15,
) -> str:
    if diagnostics.evaluated:
        accuracy = (
            diagnostics.correct
            / diagnostics.evaluated
            * 100
        )

        coverage = (
            diagnostics.predictions_present
            / diagnostics.evaluated
            * 100
        )
    else:
        accuracy = 0.0
        coverage = 0.0

    lines = [
        diagnostics.field,
        "=" * len(diagnostics.field),
        "",
        (
            "Evaluated:            "
            f"{diagnostics.evaluated}"
        ),
        (
            "Predictions present:  "
            f"{diagnostics.predictions_present}"
        ),
        (
            "Missing predictions:  "
            f"{diagnostics.missing_predictions}"
        ),
        (
            "Correct:              "
            f"{diagnostics.correct}"
        ),
        (
            "Coverage:             "
            f"{coverage:.1f}%"
        ),
        (
            "Accuracy:             "
            f"{accuracy:.1f}%"
        ),
        "",
        "TOP MISMATCHES",
    ]

    if not diagnostics.mismatch_pairs:
        lines.append(
            "No mismatches."
        )

        return "\n".join(lines)

    for (
        expected,
        predicted,
    ), count in (
        diagnostics
        .mismatch_pairs
        .most_common(top_limit)
    ):
        lines.append(
            f"{count:4d}  "
            f"{expected} -> {predicted}"
        )

    return "\n".join(lines)


def format_classification_diagnostics(
    diagnostics: ClassificationDiagnostics,
    top_limit: int = 15,
) -> str:
    return "\n\n".join(
        [
            "Classification Diagnostics\n"
            "==========================",
            format_field_diagnostics(
                diagnostics.energy,
                top_limit,
            ),
            format_field_diagnostics(
                diagnostics.function,
                top_limit,
            ),
        ]
    )