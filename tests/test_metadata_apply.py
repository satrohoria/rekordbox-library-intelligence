from mutagen.id3 import ID3, TIT2, TPE1

from rekordbox_library_intelligence.metadata import (
    MetadataCorrection,
    MetadataPlanItem,
)
from rekordbox_library_intelligence.metadata_apply import (
    apply_metadata_plan,
    create_backup,
    read_artist_title,
    write_artist_title,
    write_execution_log,
)


def create_test_mp3(
    path,
    artist="Old Artist",
    title="Old Title",
):
    """
    Creates a small ID3-only test file.

    It is sufficient for testing metadata operations
    without requiring a real audio file.
    """
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


def test_read_and_write_artist_title(tmp_path):
    audio_file = tmp_path / "test.mp3"

    create_test_mp3(audio_file)

    artist, title = read_artist_title(audio_file)

    assert artist == "Old Artist"
    assert title == "Old Title"

    write_artist_title(
        audio_file,
        "New Artist",
        "New Title",
    )

    artist, title = read_artist_title(audio_file)

    assert artist == "New Artist"
    assert title == "New Title"


def test_create_backup_preserves_original_metadata(tmp_path):
    audio_file = tmp_path / "test.mp3"
    backup_dir = tmp_path / "backup"

    create_test_mp3(
        audio_file,
        artist="Original Artist",
        title="Original Title",
    )

    backup_path = create_backup(
        audio_file,
        backup_dir,
    )

    assert backup_path.exists()

    artist, title = read_artist_title(
        backup_path
    )

    assert artist == "Original Artist"
    assert title == "Original Title"


def test_apply_metadata_plan_creates_backup(tmp_path):
    audio_file = tmp_path / "test.mp3"
    backup_dir = tmp_path / "backup"

    create_test_mp3(
        audio_file,
        artist="Old Artist",
        title="Old Title",
    )

    correction = MetadataCorrection(
        track_id=1001,
        artist="New Artist",
        title="New Title",
        location=str(audio_file),
        confidence="HIGH",
    )

    plan_item = MetadataPlanItem(
        correction=correction,
        file_path=audio_file,
        status="READY",
        message="safe to process",
    )

    results = apply_metadata_plan(
        [plan_item],
        backup_dir,
    )

    assert len(results) == 1

    result = results[0]

    assert result.status == "OK"
    assert result.old_artist == "Old Artist"
    assert result.old_title == "Old Title"
    assert result.new_artist == "New Artist"
    assert result.new_title == "New Title"

    assert result.backup_path is not None
    assert result.backup_path.exists()

    # Current file must contain the new metadata.
    artist, title = read_artist_title(
        audio_file
    )

    assert artist == "New Artist"
    assert title == "New Title"

    # Backup must still contain the original metadata.
    backup_artist, backup_title = (
        read_artist_title(
            result.backup_path
        )
    )

    assert backup_artist == "Old Artist"
    assert backup_title == "Old Title"


def test_write_execution_log(tmp_path):
    audio_file = tmp_path / "test.mp3"
    backup_dir = tmp_path / "backup"
    log_file = tmp_path / "execution.csv"

    create_test_mp3(audio_file)

    correction = MetadataCorrection(
        track_id=1001,
        artist="New Artist",
        title="New Title",
        location=str(audio_file),
        confidence="HIGH",
    )

    plan_item = MetadataPlanItem(
        correction=correction,
        file_path=audio_file,
        status="READY",
        message="safe to process",
    )

    results = apply_metadata_plan(
        [plan_item],
        backup_dir,
    )

    generated_log = write_execution_log(
        results,
        log_file,
    )

    assert generated_log.exists()

    content = generated_log.read_text(
        encoding="utf-8-sig"
    )

    assert "track_id" in content
    assert "1001" in content
    assert "Old Artist" in content
    assert "New Artist" in content
    assert "Old Title" in content
    assert "New Title" in content
    assert "OK" in content