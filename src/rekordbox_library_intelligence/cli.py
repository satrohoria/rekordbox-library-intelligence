import argparse

from .analytics import (
    calculate_library_analytics,
    format_library_analytics,
)
from .audit import (
    audit_tracks,
    format_audit,
)
from .benchmark_reports import (
    generate_benchmark_reports,
)
from .classification import (
    classify_collection,
    format_classification_preview,
)
from .classification_benchmark import (
    benchmark_classifications,
    format_classification_benchmark,
    load_ground_truth,
)
from .classification_diagnostics import (
    build_classification_diagnostics,
    format_classification_diagnostics,
)
from .classification_mismatches import (
    find_classification_mismatches,
    format_classification_mismatches,
)
from .classification_reports import (
    write_classification_csv,
)
from .console import (
    configure_console_encoding,
)
from .duplicates import find_duplicates
from .ground_truth_template import (
    write_ground_truth_template,
)
from .history import (
    find_history_sessions,
    format_history_sessions,
)
from .history_intelligence import (
    analyze_history_intelligence,
    format_history_intelligence,
)
from .history_reports import (
    generate_history_reports,
)
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
from .playlists import (
    generate_segment_playlists,
)
from .rekordbox_ground_truth import (
    build_rekordbox_ground_truth,
    grouping_to_labels,
    write_rekordbox_ground_truth_csv,
)
from .rekordbox_playlists import (
    parse_playlists,
)
from .reports import (
    generate_reports,
)
from .segments import (
    segment_tracks,
)


def format_duplicates(duplicates) -> str:
    lines = [
        "Rekordbox Library Intelligence",
        "=" * 32,
        (
            "Potential duplicate pairs: "
            f"{len(duplicates)}"
        ),
    ]

    if not duplicates:
        lines.append("")
        lines.append(
            "No high-confidence duplicates found."
        )
        return "\n".join(lines)

    for index, duplicate in enumerate(
        duplicates,
        1,
    ):
        track_a = duplicate.track_a
        track_b = duplicate.track_b

        lines.extend(
            [
                "",
                f"[{index}]",
                (
                    f"A: TrackID {track_a.track_id} | "
                    f"{track_a.artist} - "
                    f"{track_a.title}"
                ),
                (
                    f"   Bitrate: "
                    f"{track_a.bitrate or 'N/A'} kbps | "
                    f"DJ plays: {track_a.play_count} | "
                    f"Rating: {track_a.rating}"
                ),
                (
                    f"B: TrackID {track_b.track_id} | "
                    f"{track_b.artist} - "
                    f"{track_b.title}"
                ),
                (
                    f"   Bitrate: "
                    f"{track_b.bitrate or 'N/A'} kbps | "
                    f"DJ plays: {track_b.play_count} | "
                    f"Rating: {track_b.rating}"
                ),
            ]
        )

        if duplicate.keep_track_id is None:
            lines.append(
                "Recommendation: REVIEW MANUALLY"
            )
        else:
            lines.append(
                "Recommendation: KEEP TrackID "
                f"{duplicate.keep_track_id}"
            )

        lines.append(
            f"Reason: {duplicate.reason}"
        )

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
    configure_console_encoding()

    parser = argparse.ArgumentParser(
        prog="rekordbox-intelligence",
        description=(
            "Audit and analyze exported Rekordbox "
            "XML libraries safely."
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
        help=(
            "Segment tracks into CORE, ROTATION "
            "and DISCOVERY."
        ),
    )

    segments_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    # PLAYLISTS
    playlists_p = sub.add_parser(
        "playlists",
        help=(
            "Generate CORE, ROTATION and DISCOVERY "
            "M3U8 playlists."
        ),
    )

    playlists_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    playlists_p.add_argument(
        "--output-dir",
        default="output",
        help="Directory where playlists are saved.",
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
        help="Number of top tracks and artists.",
    )

    # REPORT
    report_p = sub.add_parser(
        "report",
        help="Generate JSON and CSV analytics reports.",
    )

    report_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    report_p.add_argument(
        "--output-dir",
        default="output/reports",
        help="Report destination directory.",
    )

    report_p.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top tracks and artists.",
    )

    # HISTORY
    history_p = sub.add_parser(
        "history",
        help=(
            "Analyze Rekordbox HISTORY playlists "
            "as DJ sessions."
        ),
    )

    history_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    # HISTORY INTELLIGENCE
    history_intelligence_p = sub.add_parser(
        "history-intelligence",
        help=(
            "Compare HISTORY sessions and analyze "
            "cross-session DJ behavior."
        ),
    )

    history_intelligence_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    history_intelligence_p.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of ranked results.",
    )

    # HISTORY REPORT
    history_report_p = sub.add_parser(
        "history-report",
        help=(
            "Generate JSON and CSV reports from "
            "Rekordbox HISTORY sessions."
        ),
    )

    history_report_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    history_report_p.add_argument(
        "--output-dir",
        default="output/history_reports",
        help="History report directory.",
    )

    history_report_p.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of ranked results.",
    )

    # CLASSIFY PREVIEW
    classify_preview_p = sub.add_parser(
        "classify-preview",
        help=(
            "Preview STYLE, ELEMENTS, ENERGY and "
            "FUNCTION classification suggestions."
        ),
    )

    classify_preview_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    classify_preview_p.add_argument(
        "--minimum-confidence",
        choices=[
            "REVIEW",
            "LOW",
            "MEDIUM",
            "HIGH",
        ],
        default="REVIEW",
    )

    classify_preview_p.add_argument(
        "--limit",
        type=int,
        default=None,
    )

    # CLASSIFY REPORT
    classify_report_p = sub.add_parser(
        "classify-report",
        help="Export classification suggestions to CSV.",
    )

    classify_report_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    classify_report_p.add_argument(
        "--output",
        default=(
            "output/classification/"
            "classification.csv"
        ),
    )

    classify_report_p.add_argument(
        "--minimum-confidence",
        choices=[
            "REVIEW",
            "LOW",
            "MEDIUM",
            "HIGH",
        ],
        default="REVIEW",
    )

    # CLASSIFY BENCHMARK
    classify_benchmark_p = sub.add_parser(
        "classify-benchmark",
        help=(
            "Compare classification suggestions "
            "against ground truth."
        ),
    )

    classify_benchmark_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    classify_benchmark_p.add_argument(
        "ground_truth",
        help="Validated ground truth CSV.",
    )

    classify_benchmark_p.add_argument(
        "--top-mismatches",
        type=int,
        default=15,
        help=(
            "Number of aggregate mismatch pairs "
            "shown per field."
        ),
    )

    classify_benchmark_p.add_argument(
        "--show-track-mismatches",
        action="store_true",
        help=(
            "Also display individual tracks "
            "with classification mismatches."
        ),
    )

    classify_benchmark_p.add_argument(
        "--track-mismatch-limit",
        type=int,
        default=20,
        help=(
            "Maximum number of individual mismatch "
            "tracks to display."
        ),
    )

    classify_benchmark_p.add_argument(
        "--report-dir",
        default=None,
        metavar="DIR",
        help=(
            "Generate reproducible benchmark JSON "
            "and CSV reports in this directory."
        ),
    )

    # GROUND TRUTH TEMPLATE
    ground_truth_p = sub.add_parser(
        "ground-truth-template",
        help=(
            "Generate a reproducible sample for "
            "manual classification validation."
        ),
    )

    ground_truth_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    ground_truth_p.add_argument(
        "--output",
        default=(
            "output/ground_truth/"
            "ground_truth_template.csv"
        ),
    )

    ground_truth_p.add_argument(
        "--sample-size",
        type=int,
        default=50,
    )

    ground_truth_p.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    # REKORDBOX GROUND TRUTH
    rekordbox_ground_truth_p = sub.add_parser(
        "rekordbox-ground-truth",
        help=(
            "Build classification ground truth "
            "from Rekordbox Grouping metadata."
        ),
    )

    rekordbox_ground_truth_p.add_argument(
        "xml",
        help="Rekordbox XML export.",
    )

    rekordbox_ground_truth_p.add_argument(
        "--output",
        default=(
            "output/ground_truth/"
            "rekordbox_ground_truth.csv"
        ),
    )

    # METADATA PREVIEW
    metadata_preview_p = sub.add_parser(
        "metadata-preview",
        help=(
            "Preview metadata corrections without "
            "modifying audio files."
        ),
    )

    metadata_preview_p.add_argument(
        "csv",
    )

    metadata_preview_p.add_argument(
        "--minimum-confidence",
        choices=[
            "HIGH",
            "MEDIUM",
            "LOW",
        ],
        default="HIGH",
    )

    metadata_preview_p.add_argument(
        "--skip-file-check",
        action="store_true",
    )

    # METADATA APPLY
    metadata_apply_p = sub.add_parser(
        "metadata-apply",
        help=(
            "Apply Artist and Title corrections "
            "with mandatory backups."
        ),
    )

    metadata_apply_p.add_argument(
        "csv",
    )

    metadata_apply_p.add_argument(
        "--minimum-confidence",
        choices=[
            "HIGH",
            "MEDIUM",
            "LOW",
        ],
        default="HIGH",
    )

    metadata_apply_p.add_argument(
        "--backup-dir",
        default="output/metadata_backups",
    )

    metadata_apply_p.add_argument(
        "--log",
        default="output/metadata_apply_log.csv",
    )

    metadata_apply_p.add_argument(
        "--yes",
        action="store_true",
    )

    # METADATA ROLLBACK
    metadata_rollback_p = sub.add_parser(
        "metadata-rollback",
        help=(
            "Restore metadata changes from a "
            "previous apply log."
        ),
    )

    metadata_rollback_p.add_argument(
        "execution_log",
    )

    metadata_rollback_p.add_argument(
        "--safety-backup-dir",
        default="output/rollback_safety_backups",
    )

    metadata_rollback_p.add_argument(
        "--log",
        default="output/metadata_rollback_log.csv",
    )

    metadata_rollback_p.add_argument(
        "--yes",
        action="store_true",
    )

    args = parser.parse_args()

    # AUDIT
    if args.command == "audit":
        tracks = parse_collection(
            args.xml
        )

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

    # DUPLICATES
    elif args.command == "duplicates":
        tracks = parse_collection(
            args.xml
        )

        duplicates = find_duplicates(
            tracks
        )

        print(
            format_duplicates(
                duplicates
            )
        )

    # SEGMENTS
    elif args.command == "segments":
        tracks = parse_collection(
            args.xml
        )

        segments = segment_tracks(
            tracks
        )

        print(
            format_segments(
                segments
            )
        )

    # PLAYLISTS
    elif args.command == "playlists":
        tracks = parse_collection(
            args.xml
        )

        segments = segment_tracks(
            tracks
        )

        generated = generate_segment_playlists(
            segments,
            args.output_dir,
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Generated playlists")
        print("")

        for name, (
            path,
            count,
        ) in generated.items():
            print(
                f"{name:10s} "
                f"{count:4d} tracks -> {path}"
            )

        print("")
        print(
            "No Rekordbox database or audio "
            "files were modified."
        )

    # ANALYTICS
    elif args.command == "analytics":
        tracks = parse_collection(
            args.xml
        )

        analytics = calculate_library_analytics(
            tracks,
            top_limit=args.top,
        )

        print(
            format_library_analytics(
                analytics
            )
        )

    # REPORT
    elif args.command == "report":
        tracks = parse_collection(
            args.xml
        )

        analytics = calculate_library_analytics(
            tracks,
            top_limit=args.top,
        )

        generated = generate_reports(
            analytics,
            args.output_dir,
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Analytics Reports")
        print("")

        for name, path in generated.items():
            print(
                f"{name:20s} -> {path}"
            )

        print("")
        print(
            "No Rekordbox database or audio "
            "files were modified."
        )

    # HISTORY
    elif args.command == "history":
        tracks = parse_collection(
            args.xml
        )

        playlists = parse_playlists(
            args.xml
        )

        sessions = find_history_sessions(
            playlists,
            tracks,
        )

        print(
            format_history_sessions(
                sessions
            )
        )

    # HISTORY INTELLIGENCE
    elif args.command == "history-intelligence":
        tracks = parse_collection(
            args.xml
        )

        playlists = parse_playlists(
            args.xml
        )

        sessions = find_history_sessions(
            playlists,
            tracks,
        )

        intelligence = analyze_history_intelligence(
            sessions,
            top_limit=args.top,
        )

        print(
            format_history_intelligence(
                intelligence
            )
        )

    # HISTORY REPORT
    elif args.command == "history-report":
        tracks = parse_collection(
            args.xml
        )

        playlists = parse_playlists(
            args.xml
        )

        sessions = find_history_sessions(
            playlists,
            tracks,
        )

        intelligence = analyze_history_intelligence(
            sessions,
            top_limit=args.top,
        )

        generated = generate_history_reports(
            sessions,
            intelligence,
            args.output_dir,
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("History Reports")
        print("")
        print(
            f"Sessions analyzed: {len(sessions)}"
        )
        print("")

        for name, path in generated.items():
            print(
                f"{name:20s} -> {path}"
            )

        print("")
        print(
            "No Rekordbox database or audio "
            "files were modified."
        )

    # CLASSIFY PREVIEW
    elif args.command == "classify-preview":
        tracks = parse_collection(
            args.xml
        )

        suggestions = classify_collection(
            tracks
        )

        print(
            format_classification_preview(
                suggestions,
                minimum_confidence=(
                    args.minimum_confidence
                ),
                limit=args.limit,
            )
        )

    # CLASSIFY REPORT
    elif args.command == "classify-report":
        tracks = parse_collection(
            args.xml
        )

        suggestions = classify_collection(
            tracks
        )

        destination = write_classification_csv(
            suggestions,
            args.output,
            minimum_confidence=(
                args.minimum_confidence
            ),
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Classification Report")
        print("")
        print(
            f"Tracks analyzed: {len(tracks)}"
        )
        print(
            f"CSV: {destination}"
        )
        print("")
        print(
            "No Rekordbox data or audio files "
            "were modified."
        )

    # CLASSIFY BENCHMARK
    elif args.command == "classify-benchmark":
        tracks = parse_collection(
            args.xml
        )

        suggestions = classify_collection(
            tracks
        )

        ground_truth = load_ground_truth(
            args.ground_truth
        )

        benchmark = benchmark_classifications(
            suggestions,
            ground_truth,
        )

        diagnostics = (
            build_classification_diagnostics(
                suggestions,
                ground_truth,
            )
        )

        mismatches = (
            find_classification_mismatches(
                suggestions,
                ground_truth,
            )
        )

        print(
            format_classification_benchmark(
                benchmark
            )
        )

        print("")

        print(
            format_classification_diagnostics(
                diagnostics,
                top_limit=args.top_mismatches,
            )
        )

        print("")
        print(
            "Track mismatches: "
            f"{len(mismatches)}"
        )

        if not args.show_track_mismatches:
            print(
                "Detailed track mismatches hidden. "
                "Use --show-track-mismatches "
                "to display them."
            )
        else:
            limit = max(
                args.track_mismatch_limit,
                0,
            )

            selected = (
                mismatches[:limit]
                if limit
                else []
            )

            print("")

            print(
                format_classification_mismatches(
                    selected
                )
            )

            if len(mismatches) > len(selected):
                print("")
                print(
                    "Additional mismatch tracks "
                    "not displayed: "
                    f"{len(mismatches) - len(selected)}"
                )

        if args.report_dir:
            generated = generate_benchmark_reports(
                diagnostics,
                args.report_dir,
                dataset_tracks=len(tracks),
                ground_truth_tracks=len(
                    ground_truth
                ),
            )

            print("")
            print("Benchmark Reports")
            print("=" * 17)

            for name, path in generated.items():
                print(
                    f"{name:20s} -> {path}"
                )

    # GROUND TRUTH TEMPLATE
    elif args.command == "ground-truth-template":
        tracks = parse_collection(
            args.xml
        )

        destination = write_ground_truth_template(
            tracks,
            args.output,
            sample_size=args.sample_size,
            seed=args.seed,
        )

        selected_count = min(
            args.sample_size,
            len(tracks),
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Ground Truth Template")
        print("")
        print(
            f"Tracks available: {len(tracks)}"
        )
        print(
            f"Tracks selected:  {selected_count}"
        )
        print(
            f"Random seed:      {args.seed}"
        )
        print("")
        print(
            f"CSV: {destination}"
        )
        print("")
        print(
            "Fill STYLE, ELEMENTS, ENERGY and "
            "FUNCTION manually before benchmarking."
        )
        print("")
        print(
            "No Rekordbox data or audio files "
            "were modified."
        )

    # REKORDBOX GROUND TRUTH
    elif args.command == "rekordbox-ground-truth":
        tracks = parse_collection(
            args.xml
        )

        ground_truth = (
            build_rekordbox_ground_truth(
                tracks
            )
        )

        destination = (
            write_rekordbox_ground_truth_csv(
                tracks,
                args.output,
            )
        )

        tracks_with_grouping = [
            track
            for track in tracks
            if track.grouping.strip()
        ]

        unmapped_tracks = []
        unmapped_values = set()

        for track in tracks_with_grouping:
            energy, function = grouping_to_labels(
                track.grouping
            )

            if (
                energy is None
                and function is None
            ):
                unmapped_tracks.append(
                    track
                )

                unmapped_values.add(
                    track.grouping.strip()
                )

        energy_labels = sum(
            truth.energy is not None
            for truth in ground_truth.values()
        )

        function_labels = sum(
            truth.function is not None
            for truth in ground_truth.values()
        )

        coverage = (
            len(ground_truth)
            / len(tracks)
            * 100
            if tracks
            else 0.0
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Rekordbox Ground Truth")
        print("")

        print(
            "Tracks in library:          "
            f"{len(tracks)}"
        )

        print(
            "Tracks with Grouping:       "
            f"{len(tracks_with_grouping)}"
        )

        print(
            "Ground truth tracks:        "
            f"{len(ground_truth)}"
        )

        print(
            "Coverage:                   "
            f"{coverage:.1f}%"
        )

        print("")

        print(
            "ENERGY labels:              "
            f"{energy_labels}"
        )

        print(
            "FUNCTION labels:            "
            f"{function_labels}"
        )

        print("")

        print(
            "Unmapped Grouping tracks:   "
            f"{len(unmapped_tracks)}"
        )

        print(
            "Unmapped Grouping values:   "
            f"{len(unmapped_values)}"
        )

        if unmapped_values:
            print("")
            print("UNMAPPED VALUES")

            for value in sorted(
                unmapped_values
            ):
                print(
                    f"- {value}"
                )

        print("")
        print(
            f"CSV: {destination}"
        )
        print("")
        print(
            "No Rekordbox data or audio files "
            "were modified."
        )

    # METADATA PREVIEW
    elif args.command == "metadata-preview":
        corrections = load_corrections(
            args.csv,
            minimum_confidence=(
                args.minimum_confidence
            ),
        )

        plan = build_metadata_plan(
            corrections,
            check_files=(
                not args.skip_file_check
            ),
        )

        print(
            format_metadata_plan(
                plan
            )
        )

    # METADATA APPLY
    elif args.command == "metadata-apply":
        corrections = load_corrections(
            args.csv,
            minimum_confidence=(
                args.minimum_confidence
            ),
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
        print(
            f"Backup directory: "
            f"{args.backup_dir}"
        )
        print(
            f"Execution log:    "
            f"{args.log}"
        )
        print("")

        if ready == 0:
            print("Nothing to apply.")
            return

        if not args.yes:
            print("SAFETY BLOCK")
            print("")
            print(
                "No files were modified because "
                "--yes was not provided."
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

        updated = sum(
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
        print(f"UPDATED: {updated}")
        print(f"SKIPPED: {skipped}")
        print(f"ERRORS:  {errors}")
        print("")
        print(f"Log: {log_path}")

    # METADATA ROLLBACK
    elif args.command == "metadata-rollback":
        plan = load_rollback_plan(
            args.execution_log
        )

        print("Rekordbox Library Intelligence")
        print("=" * 32)
        print("Metadata Rollback")
        print("")

        print(
            "Eligible files for rollback: "
            f"{len(plan)}"
        )

        print(
            "Safety backup directory: "
            f"{args.safety_backup_dir}"
        )

        print(
            "Rollback log:            "
            f"{args.log}"
        )

        print("")

        if not plan:
            print("Nothing to rollback.")
            return

        if not args.yes:
            print("SAFETY BLOCK")
            print("")
            print(
                "No files were restored because "
                "--yes was not provided."
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