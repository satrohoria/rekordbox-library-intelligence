# Rekordbox Library Intelligence

A Python toolkit for auditing, analyzing, and organizing Rekordbox DJ libraries.

The project follows a **safe, non-destructive workflow**: it reads exported Rekordbox XML files and generates reports or playlist files without directly modifying the Rekordbox database.

## Current features — v0.1
- Parse Rekordbox XML exports
- Audit missing Artist / Title / BPM
- Detect low-bitrate files
- Summarize play counts and ratings
- Unit tests with pytest

## Planned features
- Duplicate candidate detection
- CORE / ROTATION / DISCOVERY segmentation
- STYLE / ENERGY / ELEMENTS / FUNCTION classification
- Confidence scoring
- M3U8 batch playlist generation
- DJ History analytics
- CSV reporting

## Safety
This project does **not** directly modify the Rekordbox database.
Destructive actions are never performed automatically.

## Installation
Python 3.11+ is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements.txt
```

## Usage
```powershell
python -m rekordbox_library_intelligence audit examples/sample_collection.xml
```

## Tests
```powershell
pytest
```

## Privacy
Do not commit real Rekordbox XML exports, audio files, histories, backups, databases, or playlists containing local file paths.

## Tech stack
Python · XML · ElementTree · Dataclasses · CLI · Pytest · Git · GitHub

## Roadmap
- v0.1 — XML parser and audit
- v0.2 — Duplicate detection and metadata validation
- v0.3 — CORE / ROTATION / DISCOVERY
- v0.4 — Rule-based classification
- v0.5 — DJ History analytics
- v1.0 — Stable public release

## License
MIT
