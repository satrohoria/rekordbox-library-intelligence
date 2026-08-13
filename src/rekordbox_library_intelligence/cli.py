import argparse

from .parser import parse_collection
from .audit import audit_tracks, format_audit
from .duplicates import find_duplicates


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


if __name__ == "__main__":
    main()