from rekordbox_library_intelligence.parser import Track
from rekordbox_library_intelligence.playlists import (
    generate_segment_playlists,
    location_to_path,
    write_m3u8,
)
from rekordbox_library_intelligence.segments import LibrarySegments


def make_track(
    track_id: int,
    artist: str = "Example Artist",
    title: str = "Example Track",
) -> Track:
    return Track(
        track_id=track_id,
        title=title,
        artist=artist,
        bpm=126.0,
        bitrate=320,
        play_count=0,
        rating=204,
        location=(
            f"file://localhost/C:/Music/"
            f"example%20track%20{track_id}.mp3"
        ),
        genre="House",
    )


def test_location_to_path():
    result = location_to_path(
        "file://localhost/C:/Music/My%20Song.mp3"
    )

    assert result == r"C:\Music\My Song.mp3"


def test_write_m3u8(tmp_path):
    tracks = [
        make_track(
            1,
            artist="Example DJ",
            title="Example Groove",
        )
    ]

    destination = tmp_path / "test.m3u8"

    count = write_m3u8(
        tracks,
        destination,
    )

    content = destination.read_text(
        encoding="utf-8-sig",
    )

    assert count == 1
    assert "#EXTM3U" in content
    assert "Example DJ - Example Groove" in content
    assert r"C:\Music\example track 1.mp3" in content


def test_generate_segment_playlists(tmp_path):
    segments = LibrarySegments(
        core=[make_track(1)],
        rotation=[make_track(2)],
        discovery=[make_track(3)],
        unassigned=[make_track(4)],
    )

    generated = generate_segment_playlists(
        segments,
        tmp_path,
    )

    assert (tmp_path / "CORE.m3u8").exists()
    assert (tmp_path / "ROTATION.m3u8").exists()
    assert (tmp_path / "DISCOVERY.m3u8").exists()

    assert generated["CORE"][1] == 1
    assert generated["ROTATION"][1] == 1
    assert generated["DISCOVERY"][1] == 1