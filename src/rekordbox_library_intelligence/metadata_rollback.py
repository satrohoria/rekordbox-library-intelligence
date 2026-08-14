from dataclasses import dataclass
import csv
from datetime import datetime
from pathlib import Path
import shutil


@dataclass(slots=True)
class RollbackItem:
    track_id: int
    file_path: Path
    backup_path: Path


@dataclass(slots=True)
class RollbackResult:
    track_id: int
    file_path: Path
    status: str
    source_backup: Path
    safety_backup: Path | None
    message: str


def load_rollback_plan(
    execution_log: str | Path,
) -> list[RollbackItem]:
    """
    Load successful metadata changes from an execution log.

    Only rows with status=OK are eligible for rollback.
    """
    execution_log = Path(execution_log)

    if not execution_log.exists():
        raise FileNotFoundError(
            f"Execution log not found: {execution_log}"
        )

    plan = []

    with execution_log.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required = {
            "track_id",
            "file_path",
            "status",
            "backup_path",
        }

        missing = required - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                "Missing log columns: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            if (row["status"] or "").strip().upper() != "OK":
                continue

            backup_path = (
                row["backup_path"] or ""
            ).strip()

            file_path = (
                row["file_path"] or ""
            ).strip()

            if not backup_path or not file_path:
                continue

            plan.append(
                RollbackItem(
                    track_id=int(row["track_id"]),
                    file_path=Path(file_path),
                    backup_path=Path(backup_path),
                )
            )

    return plan


def _create_safety_backup(
    file_path: Path,
    safety_backup_dir: Path,
) -> Path:
    """
    Backup the currently modified file before restoring
    the original version.
    """
    safety_backup_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        safety_backup_dir
        / file_path.name
    )

    counter = 1

    while destination.exists():
        destination = (
            safety_backup_dir
            / f"{file_path.stem}_{counter}"
            f"{file_path.suffix}"
        )
        counter += 1

    shutil.copy2(
        file_path,
        destination,
    )

    return destination


def apply_rollback_plan(
    plan: list[RollbackItem],
    safety_backup_dir: str | Path,
) -> list[RollbackResult]:
    """
    Restore original files from metadata backups.

    Before restoring, the currently modified version is also
    backed up so the rollback itself remains reversible.
    """
    safety_backup_dir = Path(
        safety_backup_dir
    )

    results = []

    for item in plan:
        if not item.backup_path.exists():
            results.append(
                RollbackResult(
                    track_id=item.track_id,
                    file_path=item.file_path,
                    status="ERROR",
                    source_backup=item.backup_path,
                    safety_backup=None,
                    message="original backup not found",
                )
            )
            continue

        if not item.file_path.exists():
            results.append(
                RollbackResult(
                    track_id=item.track_id,
                    file_path=item.file_path,
                    status="ERROR",
                    source_backup=item.backup_path,
                    safety_backup=None,
                    message="current audio file not found",
                )
            )
            continue

        try:
            safety_backup = _create_safety_backup(
                item.file_path,
                safety_backup_dir,
            )

            shutil.copy2(
                item.backup_path,
                item.file_path,
            )

            results.append(
                RollbackResult(
                    track_id=item.track_id,
                    file_path=item.file_path,
                    status="OK",
                    source_backup=item.backup_path,
                    safety_backup=safety_backup,
                    message="original file restored",
                )
            )

        except Exception as exc:
            results.append(
                RollbackResult(
                    track_id=item.track_id,
                    file_path=item.file_path,
                    status="ERROR",
                    source_backup=item.backup_path,
                    safety_backup=None,
                    message=str(exc),
                )
            )

    return results


def write_rollback_log(
    results: list[RollbackResult],
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
                "source_backup",
                "safety_backup",
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
                    "source_backup": (
                        result.source_backup
                    ),
                    "safety_backup": (
                        result.safety_backup or ""
                    ),
                    "message": result.message,
                }
            )

    return log_path