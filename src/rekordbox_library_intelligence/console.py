import sys
from typing import TextIO


def configure_console_encoding(
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> None:
    """
    Configure CLI output streams for robust UTF-8 output.

    Rekordbox libraries may contain artist and track names
    with characters that cannot be represented by legacy
    Windows encodings such as cp1252.

    Streams that do not support reconfigure() are left
    unchanged.
    """
    streams = (
        stdout if stdout is not None else sys.stdout,
        stderr if stderr is not None else sys.stderr,
    )

    for stream in streams:
        reconfigure = getattr(
            stream,
            "reconfigure",
            None,
        )

        if not callable(reconfigure):
            continue

        try:
            reconfigure(
                encoding="utf-8",
                errors="replace",
            )
        except (
            AttributeError,
            OSError,
            ValueError,
        ):
            # Some redirected, detached or custom streams
            # cannot be reconfigured. CLI execution should
            # continue instead of failing during startup.
            continue