from pathlib import Path
from rekordbox_library_intelligence.parser import parse_collection

SAMPLE = Path("examples/sample_collection.xml")

def test_parse_collection_track_count():
    assert len(parse_collection(SAMPLE)) == 8

def test_parse_collection_metadata():
    track = parse_collection(SAMPLE)[0]
    assert track.artist == "Nova City"
    assert track.title == "Midnight Avenue"
    assert track.bpm == 124.0
    assert track.play_count == 4
