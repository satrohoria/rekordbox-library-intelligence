from pathlib import Path
from rekordbox_library_intelligence.parser import parse_collection
from rekordbox_library_intelligence.audit import audit_tracks

SAMPLE = Path("examples/sample_collection.xml")

def test_audit_summary():
    summary = audit_tracks(parse_collection(SAMPLE))
    assert summary.total_tracks == 8
    assert summary.missing_artist == 1
    assert summary.missing_title == 0
    assert summary.missing_bpm == 1
    assert summary.low_bitrate == 2
    assert summary.played_tracks == 6
    assert summary.total_plays == 19
