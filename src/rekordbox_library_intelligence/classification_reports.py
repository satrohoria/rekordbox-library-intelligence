import csv
from pathlib import Path

from .classification import (
    ClassificationSuggestion,
    filter_classifications,
)


def write_classification_csv(
    suggestions: list[ClassificationSuggestion],
    destination: str | Path,
    minimum_confidence: str = "REVIEW",
) -> Path:
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    filtered = filter_classifications(
        suggestions,
        minimum_confidence,
    )

    with destination.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "track_id",
                "artist",
                "title",
                "style",
                "elements",
                "energy",
                "function",
                "confidence",
                "reasons",
            ],
        )

        writer.writeheader()

        for suggestion in filtered:
            writer.writerow(
                {
                    "track_id": suggestion.track_id,
                    "artist": suggestion.artist,
                    "title": suggestion.title,
                    "style": suggestion.style or "",
                    "elements": "; ".join(
                        suggestion.elements
                    ),
                    "energy": suggestion.energy or "",
                    "function": suggestion.function or "",
                    "confidence": suggestion.confidence,
                    "reasons": "; ".join(
                        suggestion.reasons
                    ),
                }
            )

    return destination