import argparse
from .parser import parse_collection
from .audit import audit_tracks, format_audit

def main():
    parser = argparse.ArgumentParser(
        prog="rekordbox-intelligence",
        description="Audit exported Rekordbox XML libraries safely."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    audit_p = sub.add_parser("audit", help="Run a non-destructive library audit.")
    audit_p.add_argument("xml")
    audit_p.add_argument("--low-bitrate", type=int, default=256, metavar="KBPS")
    args = parser.parse_args()

    if args.command == "audit":
        tracks = parse_collection(args.xml)
        summary = audit_tracks(tracks, args.low_bitrate)
        print(format_audit(summary, args.low_bitrate))

if __name__ == "__main__":
    main()
