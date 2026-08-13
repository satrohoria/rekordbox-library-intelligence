from dataclasses import dataclass
import re
import unicodedata

from .parser import Track


@dataclass(slots=True)
class DuplicateCandidate:
    track_a: Track
    track_b: Track
    keep_track_id: int | None
    reason: str


def normalize_text(value: str) -> str:
    """
    Normaliza texto para comparação conservadora.

    Exemplo:
        "Madonna - MUSIC!" -> "madonna music"
    """
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _metadata_score(track: Track) -> int:
    score = 0

    if track.artist:
        score += 1
    if track.title:
        score += 1
    if track.genre:
        score += 1
    if track.bpm is not None:
        score += 1
    if track.bitrate is not None:
        score += 1

    return score


def recommend_track_to_keep(
    track_a: Track,
    track_b: Track,
) -> tuple[int | None, str]:

    # 1. Prioriza histórico real de uso pelo DJ.
    if track_a.play_count != track_b.play_count:
        winner = (
            track_a
            if track_a.play_count > track_b.play_count
            else track_b
        )
        return winner.track_id, "higher DJ play count"

    # 2. Depois prioriza qualidade do arquivo.
    bitrate_a = track_a.bitrate or 0
    bitrate_b = track_b.bitrate or 0

    if bitrate_a != bitrate_b:
        winner = track_a if bitrate_a > bitrate_b else track_b
        return winner.track_id, "higher bitrate"

    # 3. Depois classificação do DJ.
    if track_a.rating != track_b.rating:
        winner = track_a if track_a.rating > track_b.rating else track_b
        return winner.track_id, "higher rating"

    # 4. Depois metadata mais completa.
    metadata_a = _metadata_score(track_a)
    metadata_b = _metadata_score(track_b)

    if metadata_a != metadata_b:
        winner = track_a if metadata_a > metadata_b else track_b
        return winner.track_id, "more complete metadata"

    # Não decide automaticamente em empate.
    return None, "manual review required"


def find_duplicates(tracks: list[Track]) -> list[DuplicateCandidate]:
    """
    Detecta somente duplicatas de alta confiança.

    Nesta primeira versão, Artist e Title precisam ser iguais
    depois da normalização.
    """
    groups: dict[tuple[str, str], list[Track]] = {}

    for track in tracks:
        artist = normalize_text(track.artist)
        title = normalize_text(track.title)

        # Evita falsos positivos quando metadata está ausente.
        if not artist or not title:
            continue

        key = (artist, title)
        groups.setdefault(key, []).append(track)

    candidates: list[DuplicateCandidate] = []

    for group in groups.values():
        if len(group) < 2:
            continue

        # Compara todas as combinações dentro do grupo.
        for index, track_a in enumerate(group):
            for track_b in group[index + 1:]:
                keep_track_id, reason = recommend_track_to_keep(
                    track_a,
                    track_b,
                )

                candidates.append(
                    DuplicateCandidate(
                        track_a=track_a,
                        track_b=track_b,
                        keep_track_id=keep_track_id,
                        reason=reason,
                    )
                )

    return candidates