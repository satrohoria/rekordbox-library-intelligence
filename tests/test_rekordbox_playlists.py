from rekordbox_library_intelligence.rekordbox_playlists import (
    parse_playlists,
    resolve_playlist_tracks,
)
from rekordbox_library_intelligence.parser import (
    parse_collection,
)


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<DJ_PLAYLISTS Version="1.0.0">

  <COLLECTION Entries="3">

    <TRACK
      TrackID="1"
      Name="Opening Track"
      Artist="Artist A"
      AverageBpm="122.0"
      BitRate="320"
      PlayCount="3"
      Rating="204"
      Location="file://localhost/C:/Music/1.mp3"
    />

    <TRACK
      TrackID="2"
      Name="Peak Track"
      Artist="Artist B"
      AverageBpm="126.0"
      BitRate="320"
      PlayCount="5"
      Rating="255"
      Location="file://localhost/C:/Music/2.mp3"
    />

    <TRACK
      TrackID="3"
      Name="Closing Track"
      Artist="Artist C"
      AverageBpm="124.0"
      BitRate="320"
      PlayCount="2"
      Rating="204"
      Location="file://localhost/C:/Music/3.mp3"
    />

  </COLLECTION>

  <PLAYLISTS>
    <NODE
      Type="0"
      Name="ROOT"
      Count="1"
    >
      <NODE
        Type="0"
        Name="Histories"
        Count="2"
      >

        <NODE
          Type="1"
          Name="HISTORY 001"
          Entries="3"
          KeyType="0"
        >
          <TRACK Key="1"/>
          <TRACK Key="2"/>
          <TRACK Key="3"/>
        </NODE>

        <NODE
          Type="1"
          Name="HISTORY 002"
          Entries="2"
          KeyType="0"
        >
          <TRACK Key="2"/>
          <TRACK Key="3"/>
        </NODE>

      </NODE>
    </NODE>
  </PLAYLISTS>

</DJ_PLAYLISTS>
"""


def create_xml(tmp_path):
    xml_file = tmp_path / "history.xml"

    xml_file.write_text(
        SAMPLE_XML,
        encoding="utf-8",
    )

    return xml_file


def test_parse_playlists(tmp_path):
    xml_file = create_xml(tmp_path)

    playlists = parse_playlists(
        xml_file
    )

    assert len(playlists) == 2

    assert playlists[0].name == "HISTORY 001"
    assert playlists[0].folder_path == "Histories"
    assert playlists[0].track_ids == [1, 2, 3]

    assert playlists[1].name == "HISTORY 002"
    assert playlists[1].track_ids == [2, 3]


def test_resolve_playlist_tracks(tmp_path):
    xml_file = create_xml(tmp_path)

    collection = parse_collection(
        xml_file
    )

    playlists = parse_playlists(
        xml_file
    )

    tracks = resolve_playlist_tracks(
        playlists[0],
        collection,
    )

    assert len(tracks) == 3

    assert tracks[0].title == "Opening Track"
    assert tracks[1].title == "Peak Track"
    assert tracks[2].title == "Closing Track"


def test_playlist_order_is_preserved(
    tmp_path,
):
    xml_file = create_xml(tmp_path)

    collection = parse_collection(
        xml_file
    )

    playlists = parse_playlists(
        xml_file
    )

    tracks = resolve_playlist_tracks(
        playlists[0],
        collection,
    )

    assert [
        track.track_id
        for track in tracks
    ] == [1, 2, 3]


def test_missing_playlists_returns_empty(
    tmp_path,
):
    xml_file = tmp_path / "collection.xml"

    xml_file.write_text(
        """<?xml version="1.0"?>
        <DJ_PLAYLISTS>
            <COLLECTION Entries="0"/>
        </DJ_PLAYLISTS>
        """,
        encoding="utf-8",
    )

    playlists = parse_playlists(
        xml_file
    )

    assert playlists == []