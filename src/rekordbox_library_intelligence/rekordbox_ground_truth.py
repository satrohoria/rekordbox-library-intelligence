import csv
import unicodedata
from pathlib import Path

from .classification_benchmark import (
    GroundTruth,
)
from .parser import Track


GROUPING_RULES = {
    "forte": {
        "energy": "Strong",
        "function": None,
    },
    "construcao": {
        "energy": "Lift",
        "function": None,
    },
    "groove": {
        "energy": "Groove",
        "function": None,
    },
    "peak / bomba": {
        "energy": "Peak",
        "function": "Weapon",
    },
    "warm / inicio": {
        "energy": "Warm",
        "function": "Opener",
    },
    "closer / especial": {
        "energy": "Closer",
        "function": "Closer",
    },
}


def _normalize_grouping(
    value: str | None,
) -> str:
    if not value:
        return ""

    value = unicodedata.normalize(
        "NFKD",
        value,
    )

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(
            character
        )
    )

    value = " ".join(
        value.strip().casefold().split()
    )

    return value


def grouping_to_labels(
    grouping: str | None,
) -> tuple[str | None, str | None]:
    normalized = _normalize_grouping(
        grouping
    )

    rule = GROUPING_RULES.get(
        normalized
    )

    if rule is None:
        return None, None

    return (
        rule["energy"],
        rule["function"],
    )


def build_rekordbox_ground_truth(
    tracks: list[Track],
) -> dict[int, GroundTruth]:
    results = {}

    for track in tracks:
        energy, function = (
            grouping_to_labels(
                track.grouping
            )
        )

        if (
            energy is None
            and function is None
        ):
            continue

        results[track.track_id] = (
            GroundTruth(
                track_id=track.track_id,
                style=None,
                elements=(),
                energy=energy,
                function=function,
            )
        )

    return results


def write_rekordbox_ground_truth_csv(
    tracks: list[Track],
    destination: str | Path,
) -> Path:
    destination = Path(destination)

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
                "track_id",
                "artist",
                "title",
                "source_grouping",
                "style",
                "elements",
                "energy",
                "function",
            ],
        )

        writer.writeheader()

        for track in tracks:
            energy, function = (
                grouping_to_labels(
                    track.grouping
                )
            )

            if (
                energy is None
                and function is None
            ):
                continue

            writer.writerow(
                {
                    "track_id": track.track_id,
                    "artist": track.artist,
                    "title": track.title,
                    "source_grouping": (
                        track.grouping
                    ),
                    "style": "",
                    "elements": "",
                    "energy": (
                        energy or ""
                    ),
                    "function": (
                        function or ""
                    ),
                }
            )

    return destination