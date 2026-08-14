<div align="center">

# 🎧 Rekordbox Library Intelligence

### Safe automation and analytics for Rekordbox DJ libraries

**Python toolkit for auditing, analyzing, organizing and safely maintaining exported Rekordbox libraries.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-33%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active%20development-orange)

</div>

---

## Overview

**Rekordbox Library Intelligence** is a Python command-line toolkit designed to automate common maintenance and analysis tasks in large Rekordbox DJ libraries.

The project started from a real-world need to organize a growing music collection containing inconsistent metadata, duplicate tracks, different file qualities, historical DJ play data and manually maintained playlists.

Instead of directly modifying the Rekordbox database, the application works primarily with exported XML files and follows a **safety-first, non-destructive workflow**.

---

## The Problem

Large DJ libraries naturally accumulate technical and organizational issues over time:

- Missing Artist or Title metadata
- Duplicate tracks
- Multiple versions of the same song
- Low bitrate files
- Tracks that were never played
- Frequently used tracks mixed with experimental tracks
- Inconsistent ratings
- Manual playlist maintenance
- Risky bulk metadata corrections
- Lack of visibility into historical DJ usage

Managing these issues manually becomes increasingly difficult as the collection grows.

**Rekordbox Library Intelligence automates this analysis while keeping destructive operations controlled and reversible.**

---

## Features

| Feature | Description | Safety Model |
|---|---|---|
| 🔍 **Library Audit** | Detect metadata problems, missing BPM and low bitrate files | Read-only |
| ♻️ **Duplicate Detection** | Detect high-confidence duplicate candidates | No automatic deletion |
| 🎯 **Library Segmentation** | Create CORE, ROTATION and DISCOVERY groups | Read-only |
| 🎵 **Playlist Generator** | Generate M3U8 playlists automatically | Creates new files only |
| 📝 **Metadata Preview** | Validate proposed Artist / Title changes | Dry-run only |
| 💾 **Metadata Apply** | Safely modify ID3 Artist / Title fields | Mandatory backup |
| ↩️ **Metadata Rollback** | Restore files from a previous apply operation | Safety backup before restore |
| 🧪 **Automated Tests** | Validate parsing, CLI, metadata and recovery workflows | Temporary test files only |

---

## Quick Start

After installation:

```powershell
rekordbox-intelligence --help
```

Audit a Rekordbox library:

```powershell
rekordbox-intelligence audit collection.xml
```

Find duplicate tracks:

```powershell
rekordbox-intelligence duplicates collection.xml
```

Analyze library usage:

```powershell
rekordbox-intelligence segments collection.xml
```

Generate playlists:

```powershell
rekordbox-intelligence playlists collection.xml
```

---

# 🔍 Library Audit

The audit command analyzes an exported Rekordbox XML collection without modifying it.

```powershell
rekordbox-intelligence audit collection.xml
```

The audit currently checks:

- Total number of tracks
- Missing Artist
- Missing Title
- Missing BPM
- Low bitrate files
- Tracks played at least once
- Total DJ play count

### Example

```text
Rekordbox Library Intelligence
================================

Tracks: 1000
Missing artist: 12
Missing title: 2
Missing BPM: 4
Low bitrate (< 256 kbps): 36
Tracks played at least once: 421
Total DJ plays: 973
```

The bitrate threshold can also be changed:

```powershell
rekordbox-intelligence audit collection.xml --low-bitrate 320
```

---

# ♻️ Duplicate Detection

The duplicate engine detects high-confidence duplicate candidates using normalized:

```text
Artist + Title
```

Example:

```powershell
rekordbox-intelligence duplicates collection.xml
```

The engine does **not delete files**.

Instead, it recommends which version should be kept.

### Decision priority

When two duplicate candidates are found, the current recommendation logic considers:

1. DJ play count
2. Bitrate
3. Rekordbox rating
4. Metadata completeness
5. Manual review when still tied

### Example output

```text
Potential duplicate pairs: 2

[1]

A: TrackID 1001 | Example Artist - Example Track
   Bitrate: 128 kbps
   DJ plays: 0
   Rating: 102

B: TrackID 1002 | Example Artist - Example Track
   Bitrate: 320 kbps
   DJ plays: 4
   Rating: 204

Recommendation: KEEP TrackID 1002
Reason: higher DJ play count
```

This follows a **decision-support approach**, rather than automatically deleting media.

---

# 🎯 Library Segmentation

The segmentation engine separates tracks based on historical DJ usage and rating.

```powershell
rekordbox-intelligence segments collection.xml
```

## CORE

Tracks that have already proven useful during DJ sets.

```text
PlayCount >= 3
```

## ROTATION

Tracks that have been played before and have a reasonable rating.

```text
PlayCount = 1-2
Rating >= 3 stars
```

## DISCOVERY

Highly rated tracks that have not yet been used.

```text
PlayCount = 0
Rating >= 4 stars
```

## UNASSIGNED

Tracks that currently do not meet any of the rules above.

### Example

```text
Library Segmentation

CORE:       126
ROTATION:   84
DISCOVERY:  61
UNASSIGNED: 729

Total tracks: 1000
```

---

# 🎵 M3U8 Playlist Generation

The segmentation results can automatically become playlists.

```powershell
rekordbox-intelligence playlists collection.xml
```

Generated structure:

```text
output/
├── CORE.m3u8
├── ROTATION.m3u8
└── DISCOVERY.m3u8
```

Example output:

```text
Generated playlists

CORE        126 tracks -> output\CORE.m3u8
ROTATION     84 tracks -> output\ROTATION.m3u8
DISCOVERY    61 tracks -> output\DISCOVERY.m3u8

No Rekordbox database or audio files were modified.
```

A custom output directory can also be used:

```powershell
rekordbox-intelligence playlists collection.xml --output-dir playlists
```

---

# 📝 Safe Metadata Correction

Metadata correction follows a separate, controlled workflow.

The application does **not automatically rewrite metadata discovered during an audit**.

Corrections must first be provided through a CSV file.

## CSV format

```csv
track_id,artist,title,location,confidence
1001,Example Artist,Example Track,C:/Music/example.mp3,HIGH
1002,Another Artist,Another Track,C:/Music/another.mp3,HIGH
1003,Maybe Artist,Maybe Track,C:/Music/maybe.mp3,MEDIUM
```

Supported confidence levels:

```text
HIGH
MEDIUM
LOW
```

By default, only `HIGH` confidence corrections are processed.

---

## Metadata Preview

Always preview corrections before applying them.

```powershell
rekordbox-intelligence metadata-preview corrections.csv
```

Example:

```text
Metadata correction preview

READY:   10
SKIPPED: 2
MISSING: 1

[READY] TrackID 1001 | Example Artist - Example Track
[READY] TrackID 1002 | Another Artist - Another Track

DRY-RUN ONLY
No audio files were modified.
```

To include medium-confidence corrections:

```powershell
rekordbox-intelligence metadata-preview corrections.csv --minimum-confidence MEDIUM
```

A preview can also ignore filesystem validation:

```powershell
rekordbox-intelligence metadata-preview corrections.csv --skip-file-check
```

---

# 💾 Metadata Apply

Metadata modification is an explicit operation.

```powershell
rekordbox-intelligence metadata-apply corrections.csv
```

Without confirmation, the program blocks the operation:

```text
SAFETY BLOCK

No files were modified because --yes was not provided.
```

Real modification requires:

```powershell
rekordbox-intelligence metadata-apply corrections.csv --yes
```

## Before modifying each MP3

The application:

1. Validates the correction
2. Confirms the audio file exists
3. Reads the existing Artist and Title
4. Creates a backup of the original file
5. Updates only Artist and Title
6. Records old and new values
7. Generates an execution log

Default backup location:

```text
output/metadata_backups/
```

Default execution log:

```text
output/metadata_apply_log.csv
```

Custom locations can be used:

```powershell
rekordbox-intelligence metadata-apply corrections.csv `
    --backup-dir backups `
    --log logs/metadata.csv `
    --yes
```

---

# ↩️ Metadata Rollback

Metadata changes are reversible.

The execution log generated by `metadata-apply` can be used to restore the original files.

```powershell
rekordbox-intelligence metadata-rollback output/metadata_apply_log.csv
```

Rollback is also protected.

Without:

```text
--yes
```

no file is restored.

To perform the rollback:

```powershell
rekordbox-intelligence metadata-rollback `
    output/metadata_apply_log.csv `
    --yes
```

## Rollback safety model

Before restoring the original file, the application creates another backup containing the **currently modified version**.

The workflow is therefore:

```text
Original MP3
     |
     | metadata-apply
     v
Backup Original
     +
Modified MP3
     |
     | metadata-rollback
     v
Safety Backup of Modified Version
     +
Restored Original MP3
```

This makes the rollback itself reversible.

---

# 🛡️ Safety Model

Safety is a central design principle of this project.

### Read-only operations

The following operations never modify the Rekordbox database or audio files:

```text
audit
duplicates
segments
metadata-preview
```

### Generated output only

```text
playlists
```

creates new `.m3u8` files without modifying the source library.

### Protected write operations

```text
metadata-apply
metadata-rollback
```

require explicit:

```text
--yes
```

before any file operation occurs.

### Additional protections

- Rekordbox databases are never edited directly
- XML exports are treated as read-only input
- Duplicate detection never deletes tracks
- Original MP3 files are backed up before modification
- Metadata writes currently target only Artist and Title
- Every metadata operation generates a CSV log
- Metadata operations can be rolled back
- Rollback creates an additional safety backup
- Real Rekordbox XML files are excluded from Git
- Audio files are excluded from Git
- Generated output is excluded from Git

---

# 🧪 Automated Testing

The project uses `pytest`.

Run all tests:

```powershell
pytest
```

or:

```powershell
python -m pytest
```

Current status:

```text
33 tests passing
```

The test suite covers:

- XML parsing
- Invalid XML handling
- Library auditing
- Duplicate normalization
- Duplicate detection
- Duplicate keep recommendations
- Rekordbox rating conversion
- CORE segmentation
- ROTATION segmentation
- DISCOVERY segmentation
- M3U8 generation
- File URI conversion
- CLI integration
- Metadata CSV parsing
- Confidence filtering
- Dry-run metadata planning
- ID3 Artist / Title reading
- ID3 Artist / Title writing
- Backup creation
- Metadata execution logging
- Apply safety blocking
- Metadata application
- Rollback plan loading
- Original file restoration
- Rollback safety backup
- Rollback execution logging
- Rollback CLI safety blocking

Automated tests use temporary files created by `pytest`.

**Real user audio files are never required by the test suite.**

---

# 🏗️ Architecture

```text
                     Rekordbox
                         |
                         |
                    Export XML
                         |
                         v
                +----------------+
                |   XML Parser   |
                +-------+--------+
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
     +---------+   +-----------+   +-----------+
     |  Audit  |   |Duplicates |   | Segments  |
     +---------+   +-----------+   +-----+-----+
                                        |
                                        v
                                +---------------+
                                | M3U8 Generator |
                                +---------------+


                 Metadata Corrections CSV
                         |
                         v
                +------------------+
                | Metadata Preview |
                +--------+---------+
                         |
                         v
                +------------------+
                | Safety Validation|
                +--------+---------+
                         |
                         v
                +------------------+
                | Original Backup  |
                +--------+---------+
                         |
                         v
                +------------------+
                |    ID3 Apply     |
                +--------+---------+
                         |
                         v
                +------------------+
                |  Execution Log   |
                +--------+---------+
                         |
                         v
                +------------------+
                | Rollback Engine  |
                +--------+---------+
                         |
                         v
                +------------------+
                |  Safety Backup   |
                +------------------+
```

---

# 📁 Project Structure

```text
rekordbox-library-intelligence/
│
├── src/
│   └── rekordbox_library_intelligence/
│       ├── __init__.py
│       ├── __main__.py
│       ├── parser.py
│       ├── audit.py
│       ├── duplicates.py
│       ├── segments.py
│       ├── playlists.py
│       ├── metadata.py
│       ├── metadata_apply.py
│       ├── metadata_rollback.py
│       └── cli.py
│
├── tests/
│   ├── test_parser.py
│   ├── test_audit.py
│   ├── test_duplicates.py
│   ├── test_segments.py
│   ├── test_playlists.py
│   ├── test_metadata.py
│   ├── test_metadata_apply.py
│   ├── test_metadata_rollback.py
│   └── test_cli.py
│
├── examples/
│   ├── sample_collection.xml
│   ├── sample_duplicates.xml
│   └── sample_corrections.csv
│
├── docs/
│
├── output/
│   └── .gitkeep
│
├── .gitignore
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## Requirements

- Python 3.11+
- Git
- Rekordbox XML export

Clone the repository:

```bash
git clone <repository-url>
cd rekordbox-library-intelligence
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install:

```powershell
python -m pip install -e ".[dev]"
```

### Linux / macOS

Activate:

```bash
source .venv/bin/activate
```

Install:

```bash
python -m pip install -e ".[dev]"
```

---

# 💻 CLI

After installation:

```powershell
rekordbox-intelligence --help
```

Current commands:

| Command | Purpose |
|---|---|
| `audit` | Audit Rekordbox XML |
| `duplicates` | Find duplicate candidates |
| `segments` | Build CORE / ROTATION / DISCOVERY |
| `playlists` | Generate M3U8 playlists |
| `metadata-preview` | Preview metadata corrections |
| `metadata-apply` | Apply approved metadata corrections |
| `metadata-rollback` | Restore previous metadata state |

---

# 🧠 Engineering Highlights

Although the project focuses on DJ library management, it also demonstrates general software engineering and automation concepts relevant to infrastructure and operations.

### Python Engineering

- Modular package architecture
- Dataclasses
- Type hints
- Command-line interfaces
- File processing
- XML parsing
- CSV processing
- URI normalization

### Automation

- Rule-based library segmentation
- Automated playlist generation
- Metadata validation pipelines
- Safe file operations
- Backup automation
- Rollback automation

### Data Quality

- Missing metadata detection
- Duplicate identification
- Bitrate validation
- Confidence-based processing
- Metadata normalization

### Reliability

- Dry-run workflow
- Explicit destructive-action confirmation
- Automatic backups
- Execution logs
- Recovery procedures
- Automated tests

### Development Practices

- Git
- GitHub
- Incremental feature development
- Semantic-style commit messages
- Automated testing with pytest
- Editable Python packaging
- Dependency management with `pyproject.toml`

---

# 🔐 Privacy

The repository intentionally excludes personal Rekordbox and music data.

The following are ignored:

```text
*.xml
*.m3u
*.m3u8
*.edb
master.db
master.backup.db
*.mp3
*.wav
*.aif
*.aiff
*.flac
*.m4a
*.aac
```

Only explicitly approved fictitious examples are included.

This prevents the public repository from exposing:

- Personal music libraries
- Local filesystem paths
- DJ histories
- Private playlists
- Rekordbox databases
- Audio files

---

# 🗺️ Roadmap

## ✅ Completed

### v0.1 — Library Foundation

- Rekordbox XML parser
- Library audit
- CLI foundation
- Automated tests

### v0.2 — Duplicate Intelligence

- Metadata normalization
- High-confidence duplicate detection
- Keep recommendations
- Duplicate CLI

### v0.3 — Library Organization

- CORE segmentation
- ROTATION segmentation
- DISCOVERY segmentation
- Rekordbox rating normalization
- M3U8 playlist generation

### v0.4 — Metadata Safety Pipeline

- CSV correction import
- Confidence filtering
- Metadata preview
- Dry-run workflow
- ID3 Artist / Title updates
- Mandatory original backup
- Execution logs
- Explicit `--yes` safety lock
- Metadata rollback
- Rollback safety backup
- Rollback execution logs
- End-to-end CLI tests

---

## 🚧 Planned

### v0.5 — DJ History Analytics

Planned analytics include:

- Most played tracks
- Most played artists
- BPM distribution
- Rating distribution
- Played vs. unplayed ratio
- Library utilization
- Historical set behavior

### v0.6 — Classification Engine

Planned classification model:

```text
STYLE
├── House
├── Disco / Nu Disco
├── Vocal House
├── Tech House
├── Afro House
├── Pop Remix
├── Classic House
└── Brasileiras Remix

ENERGY
├── Warm
├── Groove
├── Lift
├── Strong
├── Peak
├── Reset
└── Closer

ELEMENTS
├── Vocal
├── Instrumental
├── Piano
├── Sax
├── Percussion
├── Bassline
└── Acapella

FUNCTION
├── Opener
├── Bridge
├── Singalong
├── Anthem
├── Weapon
├── Rescue
└── Closer
```

Planned confidence model:

```text
HIGH
MEDIUM
LOW
REVIEW
```

### v0.7 — Advanced Automation

Possible experiments:

- Playlist cleanup automation
- Rekordbox UI automation
- Additional metadata quality rules
- JSON reports
- CSV analytics reports
- Configurable YAML rules
- Improved duplicate similarity scoring

---

# 🧰 Technology Stack

| Technology | Usage |
|---|---|
| **Python** | Core application |
| **ElementTree** | Rekordbox XML parsing |
| **Mutagen** | ID3 metadata processing |
| **CSV** | Correction and execution logs |
| **M3U8** | Playlist generation |
| **argparse** | Command-line interface |
| **dataclasses** | Data models |
| **pytest** | Automated testing |
| **setuptools** | Python package build |
| **Git** | Version control |
| **GitHub** | Source repository and portfolio |

---

# 💡 Project Philosophy

The project follows a simple principle:

> **Automate analysis aggressively. Automate destructive actions conservatively.**

The software can freely analyze, classify and recommend.

Operations that modify files require:

```text
validation
    +
preview
    +
explicit confirmation
    +
backup
    +
logging
    +
rollback
```

This design keeps automation useful without sacrificing recoverability.

---

# Disclaimer

Rekordbox Library Intelligence is an independent open-source project.

It is not affiliated with, endorsed by, or sponsored by AlphaTheta Corporation or Pioneer DJ.

Rekordbox is a trademark of its respective owner.

---

# License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

<div align="center">

### 🎧 Built with Python, automation and a real-world DJ workflow.

**Rekordbox Library Intelligence**

</div>