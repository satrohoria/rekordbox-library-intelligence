from dataclasses import dataclass

from .classification import (
    ClassificationSuggestion,
)
from .classification_benchmark import (
    GroundTruth,
)


@dataclass(slots=True)
class FieldMismatch:
    field: str
    expected: str
    predicted: str


@dataclass(slots=True)
class TrackMismatch:
    track_id: int
    artist: str
    title: str
    confidence: str
    mismatches: tuple[FieldMismatch, ...]


def _normalize(
    value: str | None,
) -> str:
    if value is None:
        return ""

    return value.strip().casefold()


def _normalize_elements(
    values: tuple[str, ...],
) -> set[str]:
    return {
        value.strip().casefold()
        for value in values
        if value.strip()
    }


def find_classification_mismatches(
    suggestions: list[ClassificationSuggestion],
    ground_truth: dict[int, GroundTruth],
) -> list[TrackMismatch]:
    results = []

    for suggestion in suggestions:
        truth = ground_truth.get(
            suggestion.track_id
        )

        if truth is None:
            continue

        differences = []

        if truth.style is not None:
            if (
                _normalize(suggestion.style)
                != _normalize(truth.style)
            ):
                differences.append(
                    FieldMismatch(
                        field="STYLE",
                        expected=truth.style,
                        predicted=(
                            suggestion.style
                            or "-"
                        ),
                    )
                )

        if truth.elements:
            if (
                _normalize_elements(
                    suggestion.elements
                )
                != _normalize_elements(
                    truth.elements
                )
            ):
                differences.append(
                    FieldMismatch(
                        field="ELEMENTS",
                        expected="; ".join(
                            truth.elements
                        ),
                        predicted=(
                            "; ".join(
                                suggestion.elements
                            )
                            or "-"
                        ),
                    )
                )

        if truth.energy is not None:
            if (
                _normalize(suggestion.energy)
                != _normalize(truth.energy)
            ):
                differences.append(
                    FieldMismatch(
                        field="ENERGY",
                        expected=truth.energy,
                        predicted=(
                            suggestion.energy
                            or "-"
                        ),
                    )
                )

        if truth.function is not None:
            if (
                _normalize(suggestion.function)
                != _normalize(truth.function)
            ):
                differences.append(
                    FieldMismatch(
                        field="FUNCTION",
                        expected=truth.function,
                        predicted=(
                            suggestion.function
                            or "-"
                        ),
                    )
                )

        if differences:
            results.append(
                TrackMismatch(
                    track_id=(
                        suggestion.track_id
                    ),
                    artist=(
                        suggestion.artist
                    ),
                    title=(
                        suggestion.title
                    ),
                    confidence=(
                        suggestion.confidence
                    ),
                    mismatches=tuple(
                        differences
                    ),
                )
            )

    return results


def format_classification_mismatches(
    mismatches: list[TrackMismatch],
) -> str:
    lines = [
        "Classification Mismatches",
        "=" * 25,
        "",
        f"Tracks with mismatches: {len(mismatches)}",
    ]

    if not mismatches:
        lines.extend(
            [
                "",
                "No mismatches found.",
            ]
        )

        return "\n".join(lines)

    for item in mismatches:
        lines.extend(
            [
                "",
                f"TrackID {item.track_id}",
                (
                    f"{item.artist} - "
                    f"{item.title}"
                ),
                (
                    f"Confidence: "
                    f"{item.confidence}"
                ),
            ]
        )

        for mismatch in item.mismatches:
            lines.extend(
                [
                    "",
                    mismatch.field,
                    (
                        f"Expected:  "
                        f"{mismatch.expected}"
                    ),
                    (
                        f"Predicted: "
                        f"{mismatch.predicted}"
                    ),
                ]
            )

    return "\n".join(lines)