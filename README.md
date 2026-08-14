# \# Rekordbox Library Intelligence

# 

# A safe Python toolkit for auditing, analyzing and organizing exported Rekordbox DJ libraries.

# 

# The project was created to solve practical problems found in large DJ music collections, including inconsistent metadata, duplicate tracks, unused songs, playlist maintenance and risky bulk metadata changes.

# 

# The application follows a \*\*non-destructive and safety-first workflow\*\*. Rekordbox databases are never modified directly.

# 

# \---

# 

# \## Features

# 

# \### Library Audit

# 

# Analyze an exported Rekordbox XML library and identify:

# 

# \- Missing artists

# \- Missing titles

# \- Missing BPM information

# \- Low bitrate files

# \- Played vs. unplayed tracks

# \- Total DJ play count

# 

# Example:

# 

# ```bash

# rekordbox-intelligence audit collection.xml

# ```

# 

# \---

# 

# \### Duplicate Detection

# 

# Detect high-confidence duplicate tracks using normalized Artist and Title metadata.

# 

# The engine can recommend which version to keep based on:

# 

# 1\. DJ play count

# 2\. Bitrate

# 3\. Rating

# 4\. Metadata completeness

# 

# Example:

# 

# ```bash

# rekordbox-intelligence duplicates collection.xml

# ```

# 

# The tool never deletes duplicate files automatically.

# 

# \---

# 

# \### Library Segmentation

# 

# Automatically organize tracks into usage-based segments:

# 

# \#### CORE

# 

# Tracks frequently used by the DJ.

# 

# ```text

# PlayCount >= 3

# ```

# 

# \#### ROTATION

# 

# Tracks already tested but still developing.

# 

# ```text

# PlayCount = 1-2

# Rating >= 3 stars

# ```

# 

# \#### DISCOVERY

# 

# Highly rated tracks that have not yet been played.

# 

# ```text

# PlayCount = 0

# Rating >= 4 stars

# ```

# 

# Example:

# 

# ```bash

# rekordbox-intelligence segments collection.xml

# ```

# 

# \---

# 

# \### M3U8 Playlist Generation

# 

# Generate playlists automatically from library segmentation:

# 

# ```bash

# rekordbox-intelligence playlists collection.xml

# ```

# 

# Generated files:

# 

# ```text

# output/

# ├── CORE.m3u8

# ├── ROTATION.m3u8

# └── DISCOVERY.m3u8

# ```

# 

# The original Rekordbox library and audio files remain untouched.

# 

# \---

# 

# \## Safe Metadata Correction

# 

# Metadata corrections use a controlled CSV workflow.

# 

# Example:

# 

# ```csv

# track\_id,artist,title,location,confidence

# 1001,Example Artist,Example Track,C:/Music/example.mp3,HIGH

# ```

# 

# \### Preview

# 

# Always review corrections first:

# 

# ```bash

# rekordbox-intelligence metadata-preview corrections.csv

# ```

# 

# Example output:

# 

# ```text

# Metadata correction preview

# 

# READY:   10

# SKIPPED: 2

# MISSING: 1

# 

# DRY-RUN ONLY

# No audio files were modified.

# ```

# 

# \---

# 

# \### Apply Metadata

# 

# Real modifications require explicit confirmation:

# 

# ```bash

# rekordbox-intelligence metadata-apply corrections.csv --yes

# ```

# 

# Before modifying each MP3 file, the program automatically:

# 

# 1\. Reads the existing Artist and Title

# 2\. Creates a backup of the original file

# 3\. Updates only Artist and Title

# 4\. Records the previous and new values

# 5\. Generates a CSV execution log

# 

# Without `--yes`, the operation is blocked.

# 

# \---

# 

# \## Metadata Rollback

# 

# Every successful metadata operation can be reversed.

# 

# ```bash

# rekordbox-intelligence metadata-rollback output/metadata\_apply\_log.csv --yes

# ```

# 

# Before restoring the original file, the currently modified version is also backed up.

# 

# This makes the rollback itself reversible.

# 

# \---

# 

# \## Safety Model

# 

# The project follows several safety principles:

# 

# \- Rekordbox databases are never modified directly

# \- XML exports are treated as read-only input

# \- Duplicate detection never deletes files

# \- Metadata preview is non-destructive

# \- Metadata changes require explicit `--yes`

# \- Original MP3 files are backed up before modification

# \- Every change is logged

# \- Metadata changes can be rolled back

# \- Rollback operations also create safety backups

# \- Personal Rekordbox XML files and audio files are excluded from Git

# 

# \---

# 

# \## Installation

# 

# \### Requirements

# 

# \- Python 3.11+

# \- Windows, macOS or Linux

# \- Rekordbox XML export

# 

# Clone the repository and create a virtual environment:

# 

# ```bash

# python -m venv .venv

# ```

# 

# Windows:

# 

# ```powershell

# .\\.venv\\Scripts\\activate

# ```

# 

# Install the project:

# 

# ```bash

# pip install -e ".\[dev]"

# ```

# 

# \---

# 

# \## Command Line Interface

# 

# Display all available commands:

# 

# ```bash

# rekordbox-intelligence --help

# ```

# 

# Current commands:

# 

# ```text

# audit

# duplicates

# segments

# playlists

# metadata-preview

# metadata-apply

# metadata-rollback

# ```

# 

# \---

# 

# \## Tests

# 

# Run the automated test suite:

# 

# ```bash

# pytest

# ```

# 

# Current project status:

# 

# ```text

# 33 automated tests passing

# ```

# 

# Tests include:

# 

# \- Rekordbox XML parsing

# \- Library auditing

# \- Duplicate detection

# \- Library segmentation

# \- M3U8 generation

# \- CLI integration

# \- Metadata validation

# \- ID3 read/write

# \- Backup creation

# \- Metadata apply safety lock

# \- Execution logging

# \- Metadata rollback

# \- Rollback safety backup

# 

# Real user audio files are never used by the automated tests.

# 

# \---

# 

# \## Project Architecture

# 

# ```text

# Rekordbox XML

# &#x20;     |

# &#x20;     v

# +-------------+

# | XML Parser  |

# +------+------+

# &#x20;      |

# &#x20;      +--------------------+

# &#x20;      |                    |

# &#x20;      v                    v

# +-------------+      +-------------+

# | Audit       |      | Duplicates  |

# +-------------+      +-------------+

# &#x20;      |

# &#x20;      v

# +--------------------+

# | Library Segments   |

# | CORE / ROTATION /  |

# | DISCOVERY          |

# +---------+----------+

# &#x20;         |

# &#x20;         v

# +--------------------+

# | M3U8 Generator     |

# +--------------------+

# 

# Corrections CSV

# &#x20;     |

# &#x20;     v

# +--------------------+

# | Metadata Preview   |

# +---------+----------+

# &#x20;         |

# &#x20;         v

# +--------------------+

# | Safety Validation  |

# +---------+----------+

# &#x20;         |

# &#x20;         v

# +--------------------+

# | Backup + ID3 Apply |

# +---------+----------+

# &#x20;         |

# &#x20;         v

# +--------------------+

# | Execution Log      |

# +---------+----------+

# &#x20;         |

# &#x20;         v

# +--------------------+

# | Rollback Engine    |

# +--------------------+

# ```

# 

# \---

# 

# \## Project Structure

# 

# ```text

# rekordbox-library-intelligence/

# │

# ├── src/

# │   └── rekordbox\_library\_intelligence/

# │       ├── parser.py

# │       ├── audit.py

# │       ├── duplicates.py

# │       ├── segments.py

# │       ├── playlists.py

# │       ├── metadata.py

# │       ├── metadata\_apply.py

# │       ├── metadata\_rollback.py

# │       └── cli.py

# │

# ├── tests/

# ├── examples/

# ├── docs/

# ├── output/

# ├── pyproject.toml

# ├── requirements.txt

# ├── LICENSE

# └── README.md

# ```

# 

# \---

# 

# \## Privacy

# 

# Real Rekordbox XML exports, playlists, databases and audio files are intentionally excluded from the repository.

# 

# Only fictitious sample data is included for demonstration and automated testing.

# 

# \---

# 

# \## Roadmap

# 

# \### Completed

# 

# \- XML parser

# \- Library audit

# \- Duplicate detection

# \- Keep recommendations

# \- CORE / ROTATION / DISCOVERY segmentation

# \- M3U8 playlist generation

# \- Metadata dry-run preview

# \- Confidence-based correction filtering

# \- Automatic MP3 backups

# \- ID3 Artist / Title correction

# \- Execution logging

# \- Metadata rollback

# \- Rollback safety backups

# \- Automated CLI tests

# 

# \### Planned

# 

# \- Advanced metadata quality analysis

# \- DJ history analytics

# \- STYLE / ENERGY / ELEMENTS / FUNCTION classification

# \- Configurable classification rules

# \- CSV and JSON reports

# \- Rekordbox UI automation experiments

# 

# \---

# 

# \## Technology

# 

# \- Python

# \- XML / ElementTree

# \- Mutagen / ID3

# \- CSV

# \- M3U8

# \- argparse

# \- dataclasses

# \- pytest

# \- Git / GitHub

# 

# \---

# 

# \## License

# 

# MIT License

