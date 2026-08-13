from dataclasses import dataclass
import csv
from datetime import datetime
from pathlib import Path
import shutil

from mutagen.id3 import (
    ID3,
    ID3NoHeaderError,
    TIT2,
    TPE1,
)

from .metadata import MetadataPlanItem


@dataclass(slots=True)
class MetadataApplyResult:
    track_id: int
    file_path: Path
    status: str
    old_artist: str
    old_title: str
    new_artist: str
    new_title: str
    backup_path: Path | None
    message: str


def _read_text_frame(tags: ID3, frame_name: str) -> str:
    frame = tags.get(frame_name)

    if frame is None or not frame.text:
        return ""

    return str(frame.text[0])


def read_artist_title(
    file_path: str | Path,
) -> tuple[str, str]:
    file_path = Path(file_path)

    try:
        tags = ID3(file_path)
    except ID3NoHeaderError:
        return "", ""

    artist = _read_text_frame(tags, "TPE1")
    title = _read_text_frame(tags, "TIT2")

    return artist, title


def create_backup(
    file_path: str | Path,
    backup_dir: str | Path,
) -> Path:
    file_path = Path(file_path)
    backup_dir = Path(backup_dir)

    backup_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        backup_dir
        / f"{file_path.stem}_{file_path.stat().st_size}"
        f"{file_path.suffix}"
    )

    counter = 1

    while destination.exists():
        destination = (
            backup_dir
            / f"{file_path.stem}_{file_path.stat().st_size}"
            f"_{counter}{file_path.suffix}"
        )
        counter += 1

    shutil.copy2(
        file_path,
        destination,
    )

    return destination


def write_artist_title(
    file_path: str | Path,
    artist: str,
    title: str,
) -> None:
    file_path = Path(file_path)

    try:
        tags = ID3(file_path)
    except ID3NoHeaderError:
        tags = ID3()

    tags.delall("TPE1")
    tags.delall("TIT2")

    tags.add(
        TPE1(
            encoding=3,
            text=[artist],
        )
    )

    tags.add(
        TIT2(
            encoding=3,
            text=[title],
        )
    )

    tags.save(file_path)


def apply_metadata_plan(
    plan: list[MetadataPlanItem],
    backup_dir: str | Path,
) -> list[MetadataApplyResult]:

    results = []

    for item in plan:
        correction = item.correction

        if item.status != "READY":
            results.append(
                MetadataApplyResult(
                    track_id=correction.track_id,
                    file_path=item.file_path,
                    status="SKIPPED",
                    old_artist="",
                    old_title="",
                    new_artist=correction.artist,
                    new_title=correction.title,
                    backup_path=None,
                    message=item.message,
                )
            )
            continue

        if item.file_path.suffix.lower() != ".mp3":
            results.append(
                MetadataApplyResult(
                    track_id=correction.track_id,
                    file_path=item.file_path,
                    status="SKIPPED",
                    old_artist="",
                    old_title="",
                    new_artist=correction.artist,
                    new_title=correction.title,
                    backup_path=None,
                    message="only MP3 files are supported",
                )
            )
            continue

        try:
            old_artist, old_title = read_artist_title(
                item.file_path
            )

            backup_path = create_backup(
                item.file_path,
                backup_dir,
            )

            write_artist_title(
                item.file_path,
                correction.artist,
                correction.title,
            )

            results.append(
                MetadataApplyResult(
                    track_id=correction.track_id,
                    file_path=item.file_path,
                    status="OK",
                    old_artist=old_artist,
                    old_title=old_title,
                    new_artist=correction.artist,
                    new_title=correction.title,
                    backup_path=backup_path,
                    message="metadata updated",
                )
            )

        except Exception as exc:
            results.append(
                MetadataApplyResult(
                    track_id=correction.track_id,
                    file_path=item.file_path,
                    status="ERROR",
                    old_artist="",
                    old_title="",
                    new_artist=correction.artist,
                    new_title=correction.title,
                    backup_path=None,
                    message=str(exc),
                )
            )

    return results


def write_execution_log(
    results: list[MetadataApplyResult],
    log_path: str | Path,
) -> Path:
    log_path = Path(log_path)

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with log_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "track_id",
                "file_path",
                "status",
                "old_artist",
                "old_title",
                "new_artist",
                "new_title",
                "backup_path",
                "message",
            ],
        )

        writer.writeheader()

        timestamp = datetime.now().isoformat(
            timespec="seconds"
        )

        for result in results:
            writer.writerow(
                {
                    "timestamp": timestamp,
                    "track_id": result.track_id,
                    "file_path": result.file_path,
                    "status": result.status,
                    "old_artist": result.old_artist,
                    "old_title": result.old_title,
                    "new_artist": result.new_artist,
                    "new_title": result.new_title,
                    "backup_path": (
                        result.backup_path or ""
                    ),
                    "message": result.message,
                }
            )

    return log_path