from dataclasses import dataclass
import csv
from pathlib import Path

from .playlists import location_to_path


@dataclass(slots=True)
class MetadataCorrection:
    track_id: int
    artist: str
    title: str
    location: str
    confidence: str = "HIGH"


@dataclass(slots=True)
class MetadataPlanItem:
    correction: MetadataCorrection
    file_path: Path
    status: str
    message: str


def load_corrections(
    csv_path: str | Path,
    minimum_confidence: str = "HIGH",
) -> list[MetadataCorrection]:
    """
    Load metadata corrections from CSV.

    Expected columns:
        track_id
        artist
        title
        location
        confidence
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Corrections file not found: {csv_path}"
        )

    corrections = []

    allowed_confidence = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    minimum = allowed_confidence.get(
        minimum_confidence.upper()
    )

    if minimum is None:
        raise ValueError(
            "minimum_confidence must be HIGH, MEDIUM or LOW"
        )

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required = {
            "track_id",
            "artist",
            "title",
            "location",
            "confidence",
        }

        missing = required - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                "Missing CSV columns: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            confidence = (
                row["confidence"] or ""
            ).strip().upper()

            level = allowed_confidence.get(confidence, 0)

            if level < minimum:
                continue

            corrections.append(
                MetadataCorrection(
                    track_id=int(row["track_id"]),
                    artist=(row["artist"] or "").strip(),
                    title=(row["title"] or "").strip(),
                    location=(row["location"] or "").strip(),
                    confidence=confidence,
                )
            )

    return corrections


def build_metadata_plan(
    corrections: list[MetadataCorrection],
    check_files: bool = True,
) -> list[MetadataPlanItem]:
    """
    Build a safe execution plan without modifying files.
    """
    plan = []

    for correction in corrections:
        file_path = Path(
            location_to_path(
                correction.location
            )
        )

        if not correction.artist:
            status = "SKIP"
            message = "missing proposed artist"

        elif not correction.title:
            status = "SKIP"
            message = "missing proposed title"

        elif (
            check_files
            and not file_path.exists()
        ):
            status = "MISSING"
            message = "audio file not found"

        else:
            status = "READY"
            message = "safe to process"

        plan.append(
            MetadataPlanItem(
                correction=correction,
                file_path=file_path,
                status=status,
                message=message,
            )
        )

    return plan


def format_metadata_plan(
    plan: list[MetadataPlanItem],
) -> str:
    ready = sum(
        item.status == "READY"
        for item in plan
    )

    skipped = sum(
        item.status == "SKIP"
        for item in plan
    )

    missing = sum(
        item.status == "MISSING"
        for item in plan
    )

    lines = [
        "Rekordbox Library Intelligence",
        "=" * 32,
        "Metadata correction preview",
        "",
        f"READY:   {ready}",
        f"SKIPPED: {skipped}",
        f"MISSING: {missing}",
        "",
    ]

    for item in plan:
        correction = item.correction

        lines.append(
            f"[{item.status}] "
            f"TrackID {correction.track_id} | "
            f"{correction.artist} - {correction.title}"
        )

        if item.status != "READY":
            lines.append(
                f"    Reason: {item.message}"
            )

    lines.extend(
        [
            "",
            "DRY-RUN ONLY",
            "No audio files were modified.",
        ]
    )

    return "\n".join(lines)