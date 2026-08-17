import csv
from pathlib import Path
import subprocess
import sys

from mutagen.id3 import ID3, TIT2, TPE1


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SAMPLE_XML = (
    PROJECT_ROOT
    / "examples"
    / "sample_collection.xml"
)


def create_test_mp3(
    path,
    artist="Old Artist",
    title="Old Title",
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


def read_test_metadata(path):
    tags = ID3(path)

    artist = str(tags["TPE1"].text[0])
    title = str(tags["TIT2"].text[0])

    return artist, title


def create_corrections_csv(
    path,
    audio_file,
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
                "artist",
                "title",
                "location",
                "confidence",
            ],
        )

        writer.writeheader()

        writer.writerow(
            {
                "track_id": 1001,
                "artist": "New Artist",
                "title": "New Title",
                "location": str(audio_file),
                "confidence": "HIGH",
            }
        )


def test_cli_help():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "--help",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "audit" in result.stdout
    assert "duplicates" in result.stdout
    assert "segments" in result.stdout
    assert "playlists" in result.stdout
    assert "metadata-preview" in result.stdout
    assert "metadata-apply" in result.stdout


def test_cli_playlists(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "playlists",
            str(SAMPLE_XML),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert "Generated playlists" in result.stdout
    assert "CORE" in result.stdout
    assert "ROTATION" in result.stdout
    assert "DISCOVERY" in result.stdout

    assert (tmp_path / "CORE.m3u8").exists()
    assert (tmp_path / "ROTATION.m3u8").exists()
    assert (tmp_path / "DISCOVERY.m3u8").exists()


def test_cli_metadata_preview():
    corrections_csv = (
        PROJECT_ROOT
        / "examples"
        / "sample_corrections.csv"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "metadata-preview",
            str(corrections_csv),
            "--skip-file-check",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Metadata correction preview" in result.stdout
    assert "READY:   2" in result.stdout
    assert "SKIPPED: 0" in result.stdout
    assert "MISSING: 0" in result.stdout
    assert "DRY-RUN ONLY" in result.stdout
    assert "No audio files were modified." in result.stdout


def test_cli_metadata_apply_without_yes_is_blocked(
    tmp_path,
):
    audio_file = tmp_path / "test.mp3"
    corrections_csv = tmp_path / "corrections.csv"
    backup_dir = tmp_path / "backups"
    log_file = tmp_path / "apply_log.csv"

    create_test_mp3(
        audio_file,
        artist="Old Artist",
        title="Old Title",
    )

    create_corrections_csv(
        corrections_csv,
        audio_file,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "metadata-apply",
            str(corrections_csv),
            "--backup-dir",
            str(backup_dir),
            "--log",
            str(log_file),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "READY:   1" in result.stdout
    assert "SAFETY BLOCK" in result.stdout
    assert (
        "No files were modified"
        in result.stdout
    )

    artist, title = read_test_metadata(
        audio_file
    )

    assert artist == "Old Artist"
    assert title == "Old Title"

    assert not backup_dir.exists()
    assert not log_file.exists()


def test_cli_metadata_apply_with_yes(
    tmp_path,
):
    audio_file = tmp_path / "test.mp3"
    corrections_csv = tmp_path / "corrections.csv"
    backup_dir = tmp_path / "backups"
    log_file = tmp_path / "apply_log.csv"

    create_test_mp3(
        audio_file,
        artist="Old Artist",
        title="Old Title",
    )

    create_corrections_csv(
        corrections_csv,
        audio_file,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "metadata-apply",
            str(corrections_csv),
            "--backup-dir",
            str(backup_dir),
            "--log",
            str(log_file),
            "--yes",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert "Execution complete" in result.stdout
    assert "UPDATED: 1" in result.stdout
    assert "ERRORS:  0" in result.stdout

    # Current file now has new metadata.
    artist, title = read_test_metadata(
        audio_file
    )

    assert artist == "New Artist"
    assert title == "New Title"

    # Execution log must exist.
    assert log_file.exists()

    log_content = log_file.read_text(
        encoding="utf-8-sig"
    )

    assert "Old Artist" in log_content
    assert "New Artist" in log_content
    assert "Old Title" in log_content
    assert "New Title" in log_content
    assert "OK" in log_content

    # Backup must exist.
    backups = list(
        backup_dir.glob("*.mp3")
    )

    assert len(backups) == 1

    # Backup must still contain old metadata.
    backup_artist, backup_title = (
        read_test_metadata(backups[0])
    )

    assert backup_artist == "Old Artist"
    assert backup_title == "Old Title"
def test_cli_metadata_rollback_without_yes_is_blocked(
    tmp_path,
):
    audio_file = tmp_path / "test.mp3"
    corrections_csv = tmp_path / "corrections.csv"
    backup_dir = tmp_path / "backups"
    apply_log = tmp_path / "apply_log.csv"
    safety_dir = tmp_path / "rollback_safety"
    rollback_log = tmp_path / "rollback_log.csv"

    create_test_mp3(
        audio_file,
        artist="Old Artist",
        title="Old Title",
    )

    create_corrections_csv(
        corrections_csv,
        audio_file,
    )

    apply_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "metadata-apply",
            str(corrections_csv),
            "--backup-dir",
            str(backup_dir),
            "--log",
            str(apply_log),
            "--yes",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert apply_result.returncode == 0

    artist, title = read_test_metadata(
        audio_file
    )

    assert artist == "New Artist"
    assert title == "New Title"

    rollback_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "metadata-rollback",
            str(apply_log),
            "--safety-backup-dir",
            str(safety_dir),
            "--log",
            str(rollback_log),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert rollback_result.returncode == 0
    assert "SAFETY BLOCK" in rollback_result.stdout

    artist, title = read_test_metadata(
        audio_file
    )

    assert artist == "New Artist"
    assert title == "New Title"

    assert not safety_dir.exists()
    assert not rollback_log.exists()


def test_cli_metadata_rollback_with_yes(
    tmp_path,
):
    audio_file = tmp_path / "test.mp3"
    corrections_csv = tmp_path / "corrections.csv"
    backup_dir = tmp_path / "backups"
    apply_log = tmp_path / "apply_log.csv"
    safety_dir = tmp_path / "rollback_safety"
    rollback_log = tmp_path / "rollback_log.csv"

    create_test_mp3(
        audio_file,
        artist="Old Artist",
        title="Old Title",
    )

    create_corrections_csv(
        corrections_csv,
        audio_file,
    )

    apply_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "metadata-apply",
            str(corrections_csv),
            "--backup-dir",
            str(backup_dir),
            "--log",
            str(apply_log),
            "--yes",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert apply_result.returncode == 0

    artist, title = read_test_metadata(
        audio_file
    )

    assert artist == "New Artist"
    assert title == "New Title"

    rollback_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "metadata-rollback",
            str(apply_log),
            "--safety-backup-dir",
            str(safety_dir),
            "--log",
            str(rollback_log),
            "--yes",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert rollback_result.returncode == 0
    assert "Rollback complete" in rollback_result.stdout
    assert "RESTORED: 1" in rollback_result.stdout
    assert "ERRORS:   0" in rollback_result.stdout

    artist, title = read_test_metadata(
        audio_file
    )

    assert artist == "Old Artist"
    assert title == "Old Title"

    assert rollback_log.exists()

    safety_files = list(
        safety_dir.glob("*.mp3")
    )

    assert len(safety_files) == 1

    safety_artist, safety_title = (
        read_test_metadata(
            safety_files[0]
        )
    )

    assert safety_artist == "New Artist"
    assert safety_title == "New Title"
def test_cli_analytics():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "analytics",
            str(SAMPLE_XML),
            "--top",
            "3",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "DJ Library Analytics" in result.stdout
    assert "Total tracks:" in result.stdout
    assert "Library utilization:" in result.stdout
    assert "TOP TRACKS" in result.stdout
    assert "TOP ARTISTS" in result.stdout
    assert "BPM DISTRIBUTION" in result.stdout
    assert "RATING DISTRIBUTION" in result.stdout
def test_cli_report(tmp_path):
    report_dir = (
        tmp_path
        / "reports"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "report",
            str(SAMPLE_XML),
            "--output-dir",
            str(report_dir),
            "--top",
            "3",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Analytics Reports" in result.stdout

    assert (
        report_dir
        / "analytics_summary.json"
    ).exists()

    assert (
        report_dir
        / "top_tracks.csv"
    ).exists()

    assert (
        report_dir
        / "top_artists.csv"
    ).exists()

    assert (
        report_dir
        / "bpm_distribution.csv"
    ).exists()

    assert (
        report_dir
        / "rating_distribution.csv"
    ).exists()
def test_cli_history():
    history_xml = (
        PROJECT_ROOT
        / "examples"
        / "sample_history.xml"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "history",
            str(history_xml),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert "DJ History Sessions" in result.stdout
    assert "Sessions found: 2" in result.stdout

    assert "HISTORY 001" in result.stdout
    assert "HISTORY 002" in result.stdout

    assert "Tracks:      5" in result.stdout
    assert "Start BPM:   120.0" in result.stdout
    assert "Average BPM: 124.2" in result.stdout
    assert "End BPM:     124.0" in result.stdout

    assert (
        "Aurora Drive - Sunrise Intro"
        in result.stdout
    )

    assert (
        "Velvet Room - Last Call"
        in result.stdout
    )
def test_cli_history_intelligence():
    history_xml = (
        PROJECT_ROOT
        / "examples"
        / "sample_history.xml"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "history-intelligence",
            str(history_xml),
            "--top",
            "3",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert "History Intelligence" in result.stdout
    assert "Sessions analyzed: 2" in result.stdout
    assert "Unique tracks played: 5" in result.stdout

    assert "MOST REPEATED TRACKS" in result.stdout

    assert (
        "Coastal Drive - After Midnight (2 sets)"
        in result.stdout
    )

    assert (
        "Nova District - City Lights (2 sets)"
        in result.stdout
    )

    assert (
        "Silver Echo - Neon Hearts (2 sets)"
        in result.stdout
    )

    assert "MOST USED OPENERS" in result.stdout
    assert "MOST USED CLOSERS" in result.stdout

    assert "BPM BEHAVIOR" in result.stdout
    assert "Average opening BPM: 121.5" in result.stdout
    assert "Average closing BPM: 126.0" in result.stdout

    assert "TRANSITIONS" in result.stdout
    assert "Transitions analyzed: 6" in result.stdout
    assert "Largest increase: 3.0" in result.stdout
    assert "Largest decrease: -4.0" in result.stdout
def test_cli_history_report(tmp_path):
    history_xml = (
        PROJECT_ROOT
        / "examples"
        / "sample_history.xml"
    )

    output_dir = (
        tmp_path
        / "history_reports"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "history-report",
            str(history_xml),
            "--output-dir",
            str(output_dir),
            "--top",
            "3",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert (
        "History Reports"
        in result.stdout
    )

    assert (
        "Sessions analyzed: 2"
        in result.stdout
    )

    assert (
        output_dir
        / "history_summary.json"
    ).exists()

    assert (
        output_dir
        / "sessions.csv"
    ).exists()

    assert (
        output_dir
        / "repeated_tracks.csv"
    ).exists()

    assert (
        output_dir
        / "openers.csv"
    ).exists()

    assert (
        output_dir
        / "closers.csv"
    ).exists()

    assert (
        output_dir
        / "transitions.csv"
    ).exists()
def test_cli_classify_preview():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "classify-preview",
            str(SAMPLE_XML),
            "--limit",
            "3",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert (
        "Classification Preview"
        in result.stdout
    )

    assert (
        "Tracks analyzed: 8"
        in result.stdout
    )

    assert (
        "CONFIDENCE SUMMARY"
        in result.stdout
    )

    assert "STYLE:" in result.stdout
    assert "ENERGY:" in result.stdout
    assert "CONFIDENCE:" in result.stdout

    assert (
        "DRY-RUN ONLY"
        in result.stdout
    )
def test_cli_classify_report(
    tmp_path,
):
    output_file = (
        tmp_path
        / "classification.csv"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "classify-report",
            str(SAMPLE_XML),
            "--output",
            str(output_file),
            "--minimum-confidence",
            "MEDIUM",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert (
        "Classification Report"
        in result.stdout
    )

    assert (
        "Tracks analyzed: 8"
        in result.stdout
    )

    assert output_file.exists()

    content = output_file.read_text(
        encoding="utf-8-sig"
    )

    assert "track_id" in content
    assert "artist" in content
    assert "title" in content
    assert "style" in content
    assert "elements" in content
    assert "energy" in content
    assert "function" in content
    assert "confidence" in content
    assert "reasons" in content

    assert (
        "No Rekordbox data or audio files "
        "were modified."
        in result.stdout
    )
def test_cli_classify_benchmark():
    ground_truth = (
        PROJECT_ROOT
        / "examples"
        / "sample_classification_ground_truth.csv"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "classify-benchmark",
            str(SAMPLE_XML),
            str(ground_truth),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert (
        "Classification Benchmark"
        in result.stdout
    )

    assert (
        "Matched tracks:       8"
        in result.stdout
    )

    assert (
        "Without ground truth: 0"
        in result.stdout
    )

    assert (
        "FIELD ACCURACY"
        in result.stdout
    )

    assert (
        "CONFIDENCE ACCURACY"
        in result.stdout
    )

    assert "STYLE:" in result.stdout
    assert "ELEMENTS:" in result.stdout
    assert "ENERGY:" in result.stdout
    assert "FUNCTION:" in result.stdout
def test_cli_classify_benchmark_shows_mismatches():
    ground_truth = (
        PROJECT_ROOT
        / "examples"
        / "sample_classification_ground_truth.csv"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "classify-benchmark",
            str(SAMPLE_XML),
            str(ground_truth),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert (
        "Classification Benchmark"
        in result.stdout
    )

    assert (
        "Classification Mismatches"
        in result.stdout
    )

    assert (
        "Tracks with mismatches: 1"
        in result.stdout
    )

    assert (
        "TrackID 1007"
        in result.stdout
    )

    assert (
        "Night Assembly - Golden Room"
        in result.stdout
    )

    assert (
        "Confidence: LOW"
        in result.stdout
    )

    assert (
        "Expected:  Low"
        in result.stdout
    )

    assert (
        "Predicted: -"
        in result.stdout
    )
def test_cli_ground_truth_template(
    tmp_path,
):
    output_file = (
        tmp_path
        / "ground_truth.csv"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "rekordbox_library_intelligence",
            "ground-truth-template",
            str(SAMPLE_XML),
            "--output",
            str(output_file),
            "--sample-size",
            "5",
            "--seed",
            "42",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    assert (
        "Ground Truth Template"
        in result.stdout
    )

    assert (
        "Tracks available: 8"
        in result.stdout
    )

    assert (
        "Tracks selected:  5"
        in result.stdout
    )

    assert (
        "Random seed:      42"
        in result.stdout
    )

    assert output_file.exists()

    content = output_file.read_text(
        encoding="utf-8-sig"
    )

    assert "track_id" in content
    assert "artist" in content
    assert "title" in content
    assert "style" in content
    assert "elements" in content
    assert "energy" in content
    assert "function" in content

    assert (
        "No Rekordbox data or audio files "
        "were modified."
        in result.stdout
    )