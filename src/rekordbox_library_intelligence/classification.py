from dataclasses import dataclass

from .parser import Track
from .segments import rating_to_stars


@dataclass(slots=True)
class ClassificationSuggestion:
    track_id: int
    artist: str
    title: str

    style: str | None
    elements: tuple[str, ...]
    energy: str | None
    function: str | None

    confidence: str
    reasons: tuple[str, ...]


def _normalize(value: str | None) -> str:
    if not value:
        return ""

    return (
        value
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def _combined_text(track: Track) -> str:
    return " ".join(
        part
        for part in [
            _normalize(track.artist),
            _normalize(track.title),
            _normalize(track.genre),
        ]
        if part
    )


def classify_style(
    track: Track,
) -> tuple[str | None, str | None]:
    text = _combined_text(track)
    genre = _normalize(track.genre)

    # More specific rules must come first.
    if (
        "brasileir" in text
        or "brazilian" in text
    ) and "remix" in text:
        return (
            "Brasileiras Remix",
            "Brazilian/remix keywords",
        )

    if "afro house" in genre:
        return (
            "Afro House",
            "genre contains Afro House",
        )

    if "tech house" in genre:
        return (
            "Tech House",
            "genre contains Tech House",
        )

    if (
        "nu disco" in genre
        or "disco house" in genre
        or genre == "disco"
    ):
        return (
            "Disco / Nu Disco",
            "genre indicates Disco / Nu Disco",
        )

    if "vocal house" in genre:
        return (
            "Vocal House",
            "genre contains Vocal House",
        )

    if "classic house" in genre:
        return (
            "Classic House",
            "genre contains Classic House",
        )

    if (
        "pop" in text
        and "remix" in text
    ):
        return (
            "Pop Remix",
            "pop/remix keywords",
        )

    if "house" in genre:
        return (
            "House",
            "genre contains House",
        )

    return None, None


def classify_elements(
    track: Track,
) -> tuple[
    tuple[str, ...],
    list[str],
]:
    text = _combined_text(track)

    elements = []
    reasons = []

    rules = [
        (
            ("acapella", "a cappella"),
            "Acapella",
        ),
        (
            ("instrumental",),
            "Instrumental",
        ),
        (
            ("vocal",),
            "Vocal",
        ),
        (
            ("piano",),
            "Piano",
        ),
        (
            ("sax", "saxophone"),
            "Sax",
        ),
        (
            ("percussion", "percussive"),
            "Percussion",
        ),
        (
            ("bassline", "bass line"),
            "Bassline",
        ),
    ]

    for keywords, label in rules:
        if any(
            keyword in text
            for keyword in keywords
        ):
            elements.append(label)
            reasons.append(
                f"keyword suggests {label}"
            )

    return tuple(elements), reasons


def classify_energy(
    track: Track,
) -> tuple[str | None, str | None]:
    text = _combined_text(track)

    # Explicit semantic clues override BPM.
    if any(
        keyword in text
        for keyword in (
            "last call",
            "closing",
            "closer",
        )
    ):
        return (
            "Closer",
            "closing keyword",
        )

    if any(
        keyword in text
        for keyword in (
            "reset",
            "breakdown",
        )
    ):
        return (
            "Reset",
            "reset/breakdown keyword",
        )

    bpm = track.bpm

    if bpm is None or bpm <= 0:
        return None, None

    if bpm < 120:
        return (
            "Warm",
            f"BPM {bpm:.1f}",
        )

    if bpm < 124:
        return (
            "Groove",
            f"BPM {bpm:.1f}",
        )

    if bpm < 126:
        return (
            "Lift",
            f"BPM {bpm:.1f}",
        )

    if bpm < 128:
        return (
            "Strong",
            f"BPM {bpm:.1f}",
        )

    return (
        "Peak",
        f"BPM {bpm:.1f}",
    )


def classify_function(
    track: Track,
    energy: str | None,
) -> tuple[
    str | None,
    str | None,
    bool,
]:
    text = _combined_text(track)

    direct_rules = [
        (
            ("opening", "opener", "intro"),
            "Opener",
        ),
        (
            ("bridge",),
            "Bridge",
        ),
        (
            ("singalong", "sing along"),
            "Singalong",
        ),
        (
            ("anthem",),
            "Anthem",
        ),
        (
            ("weapon",),
            "Weapon",
        ),
        (
            ("rescue",),
            "Rescue",
        ),
        (
            ("last call", "closing", "closer"),
            "Closer",
        ),
    ]

    for keywords, label in direct_rules:
        if any(
            keyword in text
            for keyword in keywords
        ):
            return (
                label,
                f"keyword suggests {label}",
                True,
            )

    # Conservative usage-based inference.
    stars = rating_to_stars(
        track.rating
    )

    if (
        energy == "Peak"
        and track.play_count >= 3
        and stars >= 4
    ):
        return (
            "Weapon",
            (
                "Peak energy + repeated DJ use "
                "+ high rating"
            ),
            False,
        )

    return None, None, False


def _confidence_from_score(
    score: int,
) -> str:
    if score >= 5:
        return "HIGH"

    if score >= 3:
        return "MEDIUM"

    if score >= 1:
        return "LOW"

    return "REVIEW"


def classify_track(
    track: Track,
) -> ClassificationSuggestion:
    score = 0
    reasons = []

    style, style_reason = (
        classify_style(track)
    )

    if style is not None:
        score += 2

        if style_reason:
            reasons.append(
                style_reason
            )

    elements, element_reasons = (
        classify_elements(track)
    )

    if elements:
        score += 1
        reasons.extend(
            element_reasons
        )

    energy, energy_reason = (
        classify_energy(track)
    )

    if energy is not None:
        score += 1

        if energy_reason:
            reasons.append(
                energy_reason
            )

    (
        function,
        function_reason,
        direct_function,
    ) = classify_function(
        track,
        energy,
    )

    if function is not None:
        score += (
            2
            if direct_function
            else 1
        )

        if function_reason:
            reasons.append(
                function_reason
            )

    return ClassificationSuggestion(
        track_id=track.track_id,
        artist=track.artist,
        title=track.title,
        style=style,
        elements=elements,
        energy=energy,
        function=function,
        confidence=(
            _confidence_from_score(
                score
            )
        ),
        reasons=tuple(reasons),
    )


def classify_collection(
    tracks: list[Track],
) -> list[ClassificationSuggestion]:
    return [
        classify_track(track)
        for track in tracks
    ]