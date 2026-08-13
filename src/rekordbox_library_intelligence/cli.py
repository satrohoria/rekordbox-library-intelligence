import argparse

from .audit import audit_tracks, format_audit
from .duplicates import find_duplicates
from .parser import parse_collection
from .playlists import generate_segment_playlists
from .segments import segment_tracks


def format_duplicates(duplicates) -> str:
    lines = [
        "Rekordbox Library Intelligence",
        "=" * 32,
        f"Potential duplicate pairs: {len(duplicates)}",
    ]

    if not duplicates:
        lines.append("")
        lines.append("No high-confidence duplicates found.")
        return "\n".join(lines)

    for index, duplicate in enumerate(duplicates, 1):
        track_a = duplicate.track_a
        track_b = duplicate.track_b

        lines.extend(
            [
                "",
                f"[{index}]",
                (
                    f"A: TrackID {track_a.track_id} | "
                    f"{track_a.artist} - {track_a.title}"
                ),
                (
                    f"   Bitrate: {track_a.bitrate or 'N/A'} kbps | "
                    f"DJ plays: {track_a.play_count} | "
                    f"Rating: {track_a.rating}"
                ),
                (
                    f"B: TrackID {track_b.track_id} | "
                    f"{track_b.artist} - {track_b.title}"
                ),
                (
                    f"   Bitrate: {track_b.bitrate or 'N/A'} kbps | "
                    f"DJ plays: {track_b.play_count} | "
                    f"Rating: {track_b.rating}"
                ),
            ]
        )

        if duplicate.keep_track_id is None:
            lines.append("Recommendation: REVIEW MANUALLY")
        else:
            lines.append(
                f"Recommendation: KEEP TrackID {duplicate.keep_track_id}"
            )

        lines.append(f"Reason: {duplicate.reason}")

    return "\n".join(lines)


def format_segments(segments) -> str:
    total = (
        len(segments.core)
        + len(segments.rotation)
        + len(segments.discovery)
        + len(segments.unassigned)
    )

    return "\n".join(
        [
            "Rekordbox Library Intelligence",
            "=" * 32,
            "Library Segmentation",
            "",
            f"CORE:       {len(segments.core)}",
            f"ROTATION:   {len(segments.rotation)}",
            f"DISCOVERY:  {len(segments.discovery)}",
            f"UNASSIGNED: {len(segments.unassigned)}",
            "",
            f"Total tracks: {total}",
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        prog="rekordbox-intelligence",
        description=(
            "Audit and analyze exported Rekordbox XML libraries safely."
        ),
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Audit
    audit_p = sub.add_parser(
        "audit",
        help="Run a non-destructive library audit.",
    )
    audit_p.add_argument("xml")
    audit_p.add_argument(
        "--low-bitrate",
        type=int,
        default=256,
        metavar="KBPS",
    )

    # Duplicates
    duplicates_p = sub.add_parser(
        "duplicates",
        help="Detect high-confidence duplicate tracks.",
    )
    duplicates_p.add_argument("xml")

    # Segments
    segments_p = sub.add_parser(
        "segments",
        help="Segment tracks into CORE, ROTATION and DISCOVERY.",
    )
    segments_p.add_argument("xml")

    # Playlists
    playlists_p = sub.add_parser(
        "playlists",
        help="Generate CORE, ROTATION and DISCOVERY M3U8 playlists.",
    )
    playlists_p.add_argument("xml")
    playlists_p.add_argument(
        "--output-dir",
        default="output",
        help="Directory where generated playlists will be saved.",
    )

    args = parser.parse_args()

    tracks = parse_collection(args.xml)

    if args.command == "audit":
        summary = audit_tracks(
            tracks,
            args.low_bitrate,
        )

        print(
            format_audit(
                summary,
                args.low_bitrate,
            )
        )

    elif args.command == "duplicates":
        duplicates = find_duplicates(tracks)
        print(format_duplicates(duplicates))

    elif args.command == "segments":
        segments = segment_tracks(tracks)
        print(format_segments(segments))

    elif args.command == "playlists":
        segments = segment_tracks(tracks)

        generated = generate_segment_playlists(
            segments,
            args.output_dir,
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Generated playlists")
        print("")

        for name, (path, count) in generated.items():
            print(
                f"{name:10s} {count:4d} tracks -> {path}"
            )

        print("")
        print(
            "No Rekordbox database or audio files were modified."
        )


if __name__ == "__main__":
    main()