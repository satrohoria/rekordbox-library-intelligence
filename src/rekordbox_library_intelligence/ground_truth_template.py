import csv
import random
from pathlib import Path

from .parser import Track


def select_ground_truth_sample(
    tracks: list[Track],
    sample_size: int = 50,
    seed: int = 42,
) -> list[Track]:
    if sample_size <= 0:
        raise ValueError(
            "sample_size must be greater than zero."
        )

    if not tracks:
        return []

    if sample_size >= len(tracks):
        return list(tracks)

    rng = random.Random(seed)

    indexes = sorted(
        rng.sample(
            range(len(tracks)),
            sample_size,
        )
    )

    return [
        tracks[index]
        for index in indexes
    ]


def write_ground_truth_template(
    tracks: list[Track],
    destination: str | Path,
    sample_size: int = 50,
    seed: int = 42,
) -> Path:
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    selected = select_ground_truth_sample(
        tracks,
        sample_size=sample_size,
        seed=seed,
    )

    fields = [
        "track_id",
        "artist",
        "title",
        "bpm",
        "genre",
        "play_count",
        "rating",
        "style",
        "elements",
        "energy",
        "function",
    ]

    with destination.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for track in selected:
            writer.writerow(
                {
                    "track_id": track.track_id,
                    "artist": track.artist,
                    "title": track.title,
                    "bpm": (
                        track.bpm
                        if track.bpm is not None
                        else ""
                    ),
                    "genre": track.genre,
                    "play_count": track.play_count,
                    "rating": track.rating,
                    "style": "",
                    "elements": "",
                    "energy": "",
                    "function": "",
                }
            )

    return destination