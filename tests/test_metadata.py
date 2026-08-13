import csv

from rekordbox_library_intelligence.metadata import (
    MetadataCorrection,
    build_metadata_plan,
    format_metadata_plan,
    load_corrections,
)


def test_load_only_high_confidence(tmp_path):
    csv_file = tmp_path / "corrections.csv"

    with csv_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "track_id",
                "artist",
                "title",
                "location",
                "confidence",
            ],
        )

        writer.writeheader()

        writer.writerow(
            {
                "track_id": 1,
                "artist": "Example Artist",
                "title": "Example Track",
                "location": "C:/Music/example.mp3",
                "confidence": "HIGH",
            }
        )

        writer.writerow(
            {
                "track_id": 2,
                "artist": "Maybe Artist",
                "title": "Maybe Track",
                "location": "C:/Music/maybe.mp3",
                "confidence": "MEDIUM",
            }
        )

    corrections = load_corrections(csv_file)

    assert len(corrections) == 1
    assert corrections[0].track_id == 1


def test_metadata_plan_ready_without_file_check():
    corrections = [
        MetadataCorrection(
            track_id=1,
            artist="Example Artist",
            title="Example Track",
            location=(
                "file://localhost/"
                "C:/Music/example.mp3"
            ),
        )
    ]

    plan = build_metadata_plan(
        corrections,
        check_files=False,
    )

    assert len(plan) == 1
    assert plan[0].status == "READY"


def test_metadata_plan_rejects_missing_artist():
    corrections = [
        MetadataCorrection(
            track_id=1,
            artist="",
            title="Example Track",
            location="C:/Music/example.mp3",
        )
    ]

    plan = build_metadata_plan(
        corrections,
        check_files=False,
    )

    assert plan[0].status == "SKIP"
    assert (
        plan[0].message
        == "missing proposed artist"
    )


def test_metadata_preview_is_non_destructive():
    corrections = [
        MetadataCorrection(
            track_id=1,
            artist="Example Artist",
            title="Example Track",
            location="C:/Music/example.mp3",
        )
    ]

    plan = build_metadata_plan(
        corrections,
        check_files=False,
    )

    output = format_metadata_plan(plan)

    assert "READY:   1" in output
    assert "DRY-RUN ONLY" in output
    assert "No audio files were modified." in output