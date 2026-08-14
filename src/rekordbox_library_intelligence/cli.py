import argparse

from .analytics import (
    calculate_library_analytics,
    format_library_analytics,
)

from .audit import audit_tracks, format_audit
from .duplicates import find_duplicates
from .metadata import (
    build_metadata_plan,
    format_metadata_plan,
    load_corrections,
)
from .metadata_apply import (
    apply_metadata_plan,
    write_execution_log,
)
from .metadata_rollback import (
    apply_rollback_plan,
    load_rollback_plan,
    write_rollback_log,
)
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

    # AUDIT
    audit_p = sub.add_parser(
        "audit",
        help="Run a non-destructive library audit.",
    )

    audit_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    audit_p.add_argument(
        "--low-bitrate",
        type=int,
        default=256,
        metavar="KBPS",
        help="Bitrate threshold used by the audit.",
    )

    # DUPLICATES
    duplicates_p = sub.add_parser(
        "duplicates",
        help="Detect high-confidence duplicate tracks.",
    )

    duplicates_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    # SEGMENTS
    segments_p = sub.add_parser(
        "segments",
        help="Segment tracks into CORE, ROTATION and DISCOVERY.",
    )

    segments_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    # PLAYLISTS
    playlists_p = sub.add_parser(
        "playlists",
        help="Generate CORE, ROTATION and DISCOVERY M3U8 playlists.",
    )

    playlists_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    playlists_p.add_argument(
        "--output-dir",
        default="output",
        help="Directory where generated playlists will be saved.",
    )
    # ANALYTICS
    analytics_p = sub.add_parser(
        "analytics",
        help="Analyze DJ library usage and statistics.",
    )

    analytics_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    analytics_p.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top tracks and artists to display.",
    )
    # METADATA PREVIEW
    metadata_preview_p = sub.add_parser(
        "metadata-preview",
        help=(
            "Preview metadata corrections without modifying "
            "audio files."
        ),
    )

    metadata_preview_p.add_argument(
        "csv",
        help="CSV file containing proposed metadata corrections.",
    )

    metadata_preview_p.add_argument(
        "--minimum-confidence",
        choices=["HIGH", "MEDIUM", "LOW"],
        default="HIGH",
        help="Minimum confidence level to include.",
    )

    metadata_preview_p.add_argument(
        "--skip-file-check",
        action="store_true",
        help="Do not verify whether audio files exist.",
    )

    # METADATA APPLY
    metadata_apply_p = sub.add_parser(
        "metadata-apply",
        help="Apply Artist and Title corrections with mandatory backups.",
    )

    metadata_apply_p.add_argument(
        "csv",
        help="CSV file containing approved metadata corrections.",
    )

    metadata_apply_p.add_argument(
        "--minimum-confidence",
        choices=["HIGH", "MEDIUM", "LOW"],
        default="HIGH",
        help="Minimum confidence level to apply.",
    )

    metadata_apply_p.add_argument(
        "--backup-dir",
        default="output/metadata_backups",
        help="Directory where original audio files are backed up.",
    )

    metadata_apply_p.add_argument(
        "--log",
        default="output/metadata_apply_log.csv",
        help="CSV execution log.",
    )

    metadata_apply_p.add_argument(
        "--yes",
        action="store_true",
        help="Required confirmation for modifying audio metadata.",
    )

    # METADATA ROLLBACK
    metadata_rollback_p = sub.add_parser(
        "metadata-rollback",
        help="Restore metadata changes from a previous apply log.",
    )

    metadata_rollback_p.add_argument(
        "execution_log",
        help="Execution log generated by metadata-apply.",
    )

    metadata_rollback_p.add_argument(
        "--safety-backup-dir",
        default="output/rollback_safety_backups",
        help=(
            "Directory used to preserve the currently modified "
            "files before rollback."
        ),
    )

    metadata_rollback_p.add_argument(
        "--log",
        default="output/metadata_rollback_log.csv",
        help="CSV rollback execution log.",
    )

    metadata_rollback_p.add_argument(
        "--yes",
        action="store_true",
        help="Required confirmation for restoring original files.",
    )

    args = parser.parse_args()

    if args.command == "audit":
        tracks = parse_collection(args.xml)

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
        tracks = parse_collection(args.xml)

        duplicates = find_duplicates(tracks)

        print(format_duplicates(duplicates))

    elif args.command == "segments":
        tracks = parse_collection(args.xml)

        segments = segment_tracks(tracks)

        print(format_segments(segments))

    elif args.command == "playlists":
        tracks = parse_collection(args.xml)

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
                f"{name:10s} "
                f"{count:4d} tracks -> {path}"
            )

        print("")
        print(
            "No Rekordbox database or audio files were modified."
        )
    elif args.command == "analytics":
        tracks = parse_collection(
            args.xml
        )

        analytics = (
            calculate_library_analytics(
                tracks,
                top_limit=args.top,
            )
        )

        print(
            format_library_analytics(
                analytics
            )
        )
    elif args.command == "metadata-preview":
        corrections = load_corrections(
            args.csv,
            minimum_confidence=args.minimum_confidence,
        )

        plan = build_metadata_plan(
            corrections,
            check_files=not args.skip_file_check,
        )

        print(format_metadata_plan(plan))

    elif args.command == "metadata-apply":
        corrections = load_corrections(
            args.csv,
            minimum_confidence=args.minimum_confidence,
        )

        plan = build_metadata_plan(
            corrections,
            check_files=True,
        )

        ready = sum(
            item.status == "READY"
            for item in plan
        )

        blocked = len(plan) - ready

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Metadata Apply")
        print("")
        print(f"READY:   {ready}")
        print(f"BLOCKED: {blocked}")
        print("")
        print(f"Backup directory: {args.backup_dir}")
        print(f"Execution log:    {args.log}")
        print("")

        if ready == 0:
            print("Nothing to apply.")
            return

        if not args.yes:
            print("SAFETY BLOCK")
            print("")
            print(
                "No files were modified because --yes "
                "was not provided."
            )
            return

        results = apply_metadata_plan(
            plan,
            args.backup_dir,
        )

        log_path = write_execution_log(
            results,
            args.log,
        )

        ok = sum(
            result.status == "OK"
            for result in results
        )

        skipped = sum(
            result.status == "SKIPPED"
            for result in results
        )

        errors = sum(
            result.status == "ERROR"
            for result in results
        )

        print("Execution complete")
        print("")
        print(f"UPDATED: {ok}")
        print(f"SKIPPED: {skipped}")
        print(f"ERRORS:  {errors}")
        print("")
        print(f"Log: {log_path}")

    elif args.command == "metadata-rollback":
        plan = load_rollback_plan(
            args.execution_log
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Metadata Rollback")
        print("")
        print(
            f"Eligible files for rollback: {len(plan)}"
        )
        print(
            f"Safety backup directory: "
            f"{args.safety_backup_dir}"
        )
        print(
            f"Rollback log:            {args.log}"
        )
        print("")

        if not plan:
            print("Nothing to rollback.")
            return

        if not args.yes:
            print("SAFETY BLOCK")
            print("")
            print(
                "No files were restored because --yes "
                "was not provided."
            )
            return

        results = apply_rollback_plan(
            plan,
            args.safety_backup_dir,
        )

        log_path = write_rollback_log(
            results,
            args.log,
        )

        restored = sum(
            result.status == "OK"
            for result in results
        )

        errors = sum(
            result.status == "ERROR"
            for result in results
        )

        print("Rollback complete")
        print("")
        print(f"RESTORED: {restored}")
        print(f"ERRORS:   {errors}")
        print("")
        print(f"Log: {log_path}")


if __name__ == "__main__":
    main()