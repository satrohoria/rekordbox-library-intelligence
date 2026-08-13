from dataclasses import dataclass
from .parser import Track

@dataclass(slots=True)
class AuditSummary:
    total_tracks: int
    missing_artist: int
    missing_title: int
    missing_bpm: int
    low_bitrate: int
    played_tracks: int
    total_plays: int

def audit_tracks(tracks: list[Track], low_bitrate_threshold: int = 256) -> AuditSummary:
    return AuditSummary(
        total_tracks=len(tracks),
        missing_artist=sum(not t.artist for t in tracks),
        missing_title=sum(not t.title for t in tracks),
        missing_bpm=sum(t.bpm is None or t.bpm <= 0 for t in tracks),
        low_bitrate=sum(t.bitrate is not None and t.bitrate < low_bitrate_threshold for t in tracks),
        played_tracks=sum(t.play_count > 0 for t in tracks),
        total_plays=sum(t.play_count for t in tracks),
    )

def format_audit(summary: AuditSummary, low_bitrate_threshold: int = 256) -> str:
    return "\n".join([
        "Rekordbox Library Intelligence",
        "=" * 32,
        f"Tracks: {summary.total_tracks}",
        f"Missing artist: {summary.missing_artist}",
        f"Missing title: {summary.missing_title}",
        f"Missing BPM: {summary.missing_bpm}",
        f"Low bitrate (< {low_bitrate_threshold} kbps): {summary.low_bitrate}",
        f"Tracks played at least once: {summary.played_tracks}",
        f"Total DJ plays: {summary.total_plays}",
    ])
