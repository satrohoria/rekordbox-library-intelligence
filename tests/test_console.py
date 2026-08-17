from rekordbox_library_intelligence.console import (
    configure_console_encoding,
)


class FakeStream:
    def __init__(self):
        self.encoding_requested = None
        self.errors_requested = None

    def reconfigure(
        self,
        *,
        encoding=None,
        errors=None,
    ):
        self.encoding_requested = encoding
        self.errors_requested = errors


class StreamWithoutReconfigure:
    pass


class BrokenStream:
    def reconfigure(
        self,
        *,
        encoding=None,
        errors=None,
    ):
        raise ValueError(
            "stream cannot be reconfigured"
        )


def test_configure_console_encoding_uses_utf8():
    stdout = FakeStream()
    stderr = FakeStream()

    configure_console_encoding(
        stdout,
        stderr,
    )

    assert (
        stdout.encoding_requested
        == "utf-8"
    )

    assert (
        stdout.errors_requested
        == "replace"
    )

    assert (
        stderr.encoding_requested
        == "utf-8"
    )

    assert (
        stderr.errors_requested
        == "replace"
    )


def test_console_without_reconfigure_is_supported():
    stdout = StreamWithoutReconfigure()
    stderr = StreamWithoutReconfigure()

    configure_console_encoding(
        stdout,
        stderr,
    )


def test_broken_console_does_not_crash():
    stdout = BrokenStream()
    stderr = BrokenStream()

    configure_console_encoding(
        stdout,
        stderr,
    )