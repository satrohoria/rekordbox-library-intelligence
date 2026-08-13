from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_XML = PROJECT_ROOT / "examples" / "sample_collection.xml"


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