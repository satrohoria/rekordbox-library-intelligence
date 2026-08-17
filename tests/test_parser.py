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
def test_parser_reads_grouping(
    tmp_path,
):
    xml_path = (
        tmp_path
        / "grouping.xml"
    )

    xml_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<DJ_PLAYLISTS Version="1.0.0">
    <COLLECTION Entries="1">
        <TRACK
            TrackID="9001"
            Name="Example Track"
            Artist="Example Artist"
            AverageBpm="126.0"
            BitRate="320"
            PlayCount="4"
            Rating="204"
            Location="file://localhost/C:/Music/example.mp3"
            Genre="House"
            Grouping="Peak / bomba"
        />
    </COLLECTION>
</DJ_PLAYLISTS>
""",
        encoding="utf-8",
    )

    tracks = parse_collection(
        xml_path
    )

    assert len(tracks) == 1

    assert (
        tracks[0].grouping
        == "Peak / bomba"
    )


def test_parser_preserves_utf8_grouping(
    tmp_path,
):
    xml_path = (
        tmp_path
        / "utf8_grouping.xml"
    )

    xml_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<DJ_PLAYLISTS Version="1.0.0">
    <COLLECTION Entries="1">
        <TRACK
            TrackID="9002"
            Name="UTF8 Track"
            Artist="Example Artist"
            AverageBpm="124.0"
            BitRate="320"
            PlayCount="1"
            Rating="153"
            Location="file://localhost/C:/Music/utf8.mp3"
            Genre="House"
            Grouping="Construção"
        />
    </COLLECTION>
</DJ_PLAYLISTS>
""",
        encoding="utf-8",
    )

    tracks = parse_collection(
        xml_path
    )

    assert (
        tracks[0].grouping
        == "Construção"
    )
