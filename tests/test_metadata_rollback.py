import csv
import shutil

from mutagen.id3 import ID3, TIT2, TPE1

from rekordbox_library_intelligence.metadata_rollback import (
    apply_rollback_plan,
    load_rollback_plan,
    write_rollback_log,
)


def create_test_mp3(
    path,
    artist,
    title,
):
    tags = ID3()

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

    tags.save(path)


def read_metadata(path):
    tags = ID3(path)

    return (
        str(tags["TPE1"].text[0]),
        str(tags["TIT2"].text[0]),
    )


def create_execution_log(
    path,
    audio_file,
    backup_file,
):
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "track_id",
                "file_path",
                "status",
                "backup_path",
            ],
        )

        writer.writeheader()

        writer.writerow(
            {
                "track_id": 1001,
                "file_path": str(audio_file),
                "status": "OK",
                "backup_path": str(backup_file),
            }
        )


def test_load_rollback_plan(tmp_path):
    audio_file = tmp_path / "current.mp3"
    backup_file = tmp_path / "original.mp3"
    log_file = tmp_path / "apply.csv"

    create_execution_log(
        log_file,
        audio_file,
        backup_file,
    )

    plan = load_rollback_plan(
        log_file
    )

    assert len(plan) == 1
    assert plan[0].track_id == 1001
    assert plan[0].file_path == audio_file
    assert plan[0].backup_path == backup_file


def test_rollback_restores_original_metadata(
    tmp_path,
):
    audio_file = tmp_path / "current.mp3"
    backup_file = tmp_path / "original.mp3"
    log_file = tmp_path / "apply.csv"
    safety_dir = tmp_path / "safety"

    create_test_mp3(
        audio_file,
        "New Artist",
        "New Title",
    )

    create_test_mp3(
        backup_file,
        "Old Artist",
        "Old Title",
    )

    create_execution_log(
        log_file,
        audio_file,
        backup_file,
    )

    plan = load_rollback_plan(
        log_file
    )

    results = apply_rollback_plan(
        plan,
        safety_dir,
    )

    assert len(results) == 1
    assert results[0].status == "OK"

    artist, title = read_metadata(
        audio_file
    )

    assert artist == "Old Artist"
    assert title == "Old Title"

    # The modified version must also be preserved.
    assert results[0].safety_backup is not None
    assert results[0].safety_backup.exists()

    safety_artist, safety_title = (
        read_metadata(
            results[0].safety_backup
        )
    )

    assert safety_artist == "New Artist"
    assert safety_title == "New Title"


def test_write_rollback_log(tmp_path):
    audio_file = tmp_path / "current.mp3"
    backup_file = tmp_path / "original.mp3"
    apply_log = tmp_path / "apply.csv"
    rollback_log = tmp_path / "rollback.csv"
    safety_dir = tmp_path / "safety"

    create_test_mp3(
        audio_file,
        "New Artist",
        "New Title",
    )

    create_test_mp3(
        backup_file,
        "Old Artist",
        "Old Title",
    )

    create_execution_log(
        apply_log,
        audio_file,
        backup_file,
    )

    plan = load_rollback_plan(
        apply_log
    )

    results = apply_rollback_plan(
        plan,
        safety_dir,
    )

    generated = write_rollback_log(
        results,
        rollback_log,
    )

    assert generated.exists()

    content = generated.read_text(
        encoding="utf-8-sig"
    )

    assert "1001" in content
    assert "OK" in content
    assert "original file restored" in content