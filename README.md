# Rekordbox Library Intelligence

> A safety-first Python toolkit for auditing, analyzing and organizing exported Rekordbox DJ libraries.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-122%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-v0.1.0%20RC-blue)

---

## Overview

**Rekordbox Library Intelligence** is a Python command-line toolkit designed to analyze exported Rekordbox XML libraries without modifying the Rekordbox database directly.

The project was created to solve practical problems found in large DJ music collections, including:

- inconsistent metadata;
- duplicate tracks;
- underused music;
- library segmentation;
- playlist generation;
- DJ history analysis;
- classification of track energy and function;
- metadata correction workflows;
- classification benchmarking;
- reproducible analytics reports.

The application follows a **non-destructive and safety-first workflow**.

Rekordbox databases are never modified directly.

---

## Development Approach

This project was developed through a **human-led, AI-assisted engineering workflow**.

The project owner defined the requirements, provided the DJ and Rekordbox domain knowledge, executed and validated the implementation, tested the application against a real music library, reviewed classification results, and made the final technical decisions.

Generative AI tools were used collaboratively during development to assist with:

- code drafting and refactoring;
- debugging and troubleshooting;
- automated test generation;
- CLI design;
- documentation;
- classification rule exploration;
- benchmark analysis.

All proposed changes were executed, tested and evaluated by the project owner before being incorporated into the project.

The goal of using AI in this project was not to replace engineering judgment, but to use it as a development accelerator while maintaining a test-driven and evidence-based workflow.

---

## Why this project exists

Large DJ libraries tend to accumulate inconsistencies over time.

A collection may contain hundreds or thousands of tracks with:

- incomplete artists;
- inconsistent titles;
- duplicate files;
- old or unused tracks;
- mixed bitrate quality;
- inconsistent classifications;
- limited visibility into actual DJ usage.

Rekordbox provides powerful tools for performance and library management, but complex collection analysis often requires additional workflows.

This project provides those workflows through a reproducible Python CLI.

---

## Core principles

### Safety first

Library analysis is read-only unless a command explicitly performs a metadata operation.

Metadata modifications require:

- explicit commands;
- backups;
- execution logs;
- confirmation flags.

Rollback support is available for metadata changes.

### Rekordbox database isolation

The toolkit works from exported Rekordbox XML files.

It does **not** directly modify the Rekordbox database.

### Reproducibility

Analytics, classification benchmarks and reports can be regenerated from the same source data.

### Explainable classification

Classification suggestions include reasoning and confidence instead of returning unexplained labels.

---

# Features

## Library Audit

Inspect a Rekordbox XML export and report common library issues.

The audit currently identifies:

- missing artists;
- missing titles;
- missing BPM values;
- low bitrate tracks;
- tracks never played;
- total DJ plays.

Example:

```powershell
rekordbox-intelligence audit collection.xml
```

Custom bitrate threshold:

```powershell
rekordbox-intelligence audit collection.xml --low-bitrate 320
```

---

## Duplicate Detection

Detect high-confidence duplicate tracks using library metadata.

```powershell
rekordbox-intelligence duplicates collection.xml
```

The tool can also suggest which copy should be retained based on available metadata and usage signals.

---

## Library Segmentation

Tracks can be divided into operational DJ-library segments:

- `CORE`
- `ROTATION`
- `DISCOVERY`
- `UNASSIGNED`

```powershell
rekordbox-intelligence segments collection.xml
```

This makes it easier to identify actively used tracks while separating discovery material and less frequently used music.

---

## Playlist Generation

Generate M3U8 playlists from the segmentation engine.

```powershell
rekordbox-intelligence playlists collection.xml
```

Generated files:

```text
output/
├── CORE.m3u8
├── ROTATION.m3u8
└── DISCOVERY.m3u8
```

Audio files are not modified.

---

# Analytics

## Library Analytics

Analyze how the collection is actually used.

```powershell
rekordbox-intelligence analytics collection.xml
```

Metrics include:

- library utilization;
- total DJ plays;
- average BPM;
- top tracks;
- top artists;
- BPM distribution;
- rating distribution.

Example:

```powershell
rekordbox-intelligence analytics collection.xml --top 20
```

---

## Analytics Reports

Export analytics to machine-readable formats.

```powershell
rekordbox-intelligence report collection.xml
```

Reports include JSON and CSV files that can be used in spreadsheets, dashboards or additional analysis.

---

# Rekordbox HISTORY Intelligence

Rekordbox HISTORY playlists can be interpreted as DJ sessions.

## Session Analysis

```powershell
rekordbox-intelligence history collection.xml
```

Session metrics include:

- number of tracks;
- starting BPM;
- average BPM;
- ending BPM;
- minimum BPM;
- maximum BPM;
- opening track;
- closing track.

---

## Cross-session Intelligence

```powershell
rekordbox-intelligence history-intelligence collection.xml
```

This analyzes patterns across multiple DJ sessions.

Examples include:

- repeated tracks;
- frequently used opening tracks;
- frequently used closing tracks;
- BPM behavior;
- transition behavior.

---

## HISTORY Reports

```powershell
rekordbox-intelligence history-report collection.xml
```

Generated reports can include:

```text
history_summary.json
sessions.csv
repeated_tracks.csv
openers.csv
closers.csv
transitions.csv
```

---

# Track Classification

The project contains an explainable classification engine that can infer DJ-oriented attributes from available track metadata.

Classification dimensions include:

### STYLE

Examples:

- House
- Tech House
- Disco / Nu Disco
- Vocal House
- Classic House
- Pop Remix

### ELEMENTS

Examples:

- Vocal
- Piano
- Sax
- Percussion
- Bassline

### ENERGY

Current ENERGY model:

```text
BPM < 120        -> Warm
120 <= BPM < 123 -> Groove
123 <= BPM < 126 -> Lift
126 <= BPM < 129 -> Strong
BPM >= 129       -> Peak
```

Explicit semantic signals such as `closer`, `last call`, `reset` and `breakdown` can override the BPM model.

### FUNCTION

FUNCTION uses a hierarchical model.

Explicit semantic signals have priority.

Examples:

```text
opening / opener / intro -> Opener
bridge                   -> Bridge
singalong                -> Singalong
anthem                   -> Anthem
weapon                   -> Weapon
rescue                   -> Rescue
closing / closer         -> Closer
```

When no explicit signal exists, ENERGY can provide contextual fallback:

```text
Warm   -> Opener
Peak   -> Weapon
Closer -> Closer
```

---

## Classification Preview

Preview classifications without modifying Rekordbox data.

```powershell
rekordbox-intelligence classify-preview collection.xml
```

Filter by confidence:

```powershell
rekordbox-intelligence classify-preview collection.xml `
    --minimum-confidence MEDIUM
```

Limit the output:

```powershell
rekordbox-intelligence classify-preview collection.xml `
    --limit 50
```

---

## Classification CSV Report

```powershell
rekordbox-intelligence classify-report collection.xml
```

Default output:

```text
output/classification/classification.csv
```

---

# Ground Truth

Classification quality can be measured using manually validated ground-truth datasets.

## Generate a validation template

```powershell
rekordbox-intelligence ground-truth-template collection.xml `
    --sample-size 50 `
    --seed 42
```

This creates a reproducible random sample that can be classified manually.

---

## Rekordbox Grouping Ground Truth

The project can also convert structured Rekordbox `Grouping` metadata into classification ground truth.

```powershell
rekordbox-intelligence rekordbox-ground-truth collection.xml
```

This functionality is intended for collections where Grouping already represents manually validated DJ classifications.

Importantly, **Grouping is used only as validation ground truth and is not used as an input feature by the classifier**.

This prevents classification data leakage.

---

# Classification Benchmark

Compare generated classifications against validated ground truth.

```powershell
rekordbox-intelligence classify-benchmark `
    collection.xml `
    ground_truth.csv
```

The benchmark reports:

- matched tracks;
- tracks without ground truth;
- field accuracy;
- confidence accuracy;
- prediction coverage;
- missing predictions;
- aggregate mismatch patterns.

Individual mismatches can also be displayed:

```powershell
rekordbox-intelligence classify-benchmark `
    collection.xml `
    ground_truth.csv `
    --show-track-mismatches
```

---

## Reproducible Benchmark Reports

Benchmark results can be exported automatically:

```powershell
rekordbox-intelligence classify-benchmark `
    collection.xml `
    ground_truth.csv `
    --report-dir output/benchmarks
```

Generated files:

```text
output/benchmarks/
├── benchmark_summary.json
├── energy_mismatches.csv
└── function_mismatches.csv
```

This makes benchmark evolution reproducible and easier to review.

---

# Real-library Benchmark

The classification engine was validated against a real Rekordbox collection.

Dataset:

```text
Library tracks:       996
Ground-truth tracks:  989
```

## ENERGY

```text
Evaluated:            989
Predictions present:  989
Missing predictions:    0
Correct:              937

Coverage:           100.0%
Accuracy:            94.7%
```

The ENERGY model originally achieved **77.8% accuracy**.

Analysis of real-library BPM distributions revealed two dominant classification errors:

```text
Strong -> Peak
Lift   -> Groove
```

After recalibrating the BPM boundaries, accuracy increased to:

```text
77.8% -> 94.7%
```

while maintaining:

```text
100% prediction coverage
```

---

## FUNCTION

Validated FUNCTION labels:

```text
120
```

Current result:

```text
Predictions present:  99
Correct:              95

Coverage:            82.5%
Accuracy:            79.2%
```

The original FUNCTION model produced almost no predictions.

A hierarchical approach using semantic rules and ENERGY fallback increased useful FUNCTION coverage substantially.

---

# AI-Assisted Development

Generative AI was used as a development partner throughout this project.

Rather than treating generated code as automatically correct, the development process followed an iterative workflow:

```text
Problem definition
        ↓
AI-assisted implementation
        ↓
Local execution
        ↓
Automated tests
        ↓
Real-library validation
        ↓
Benchmark analysis
        ↓
Human review and decision
```

Classification rules were not accepted solely because they appeared reasonable. They were evaluated against manually validated Rekordbox metadata and benchmarked against real library data.

One ENERGY calibration improved measured accuracy from:

```text
77.8% -> 94.7%
```

A proposed additional optimization was deliberately not adopted after analysis indicated a risk of overfitting the validation dataset.

This workflow demonstrates how AI-assisted software development can be combined with testing, domain expertise and engineering judgment.

---

# Metadata Correction Workflow

The toolkit also supports controlled Artist and Title metadata corrections.

## Preview

```powershell
rekordbox-intelligence metadata-preview corrections.csv
```

The preview is a dry run.

No audio files are modified.

---

## Apply

```powershell
rekordbox-intelligence metadata-apply corrections.csv --yes
```

Before modification, the application creates backups.

An execution log is also generated.

Default locations:

```text
output/metadata_backups/
output/metadata_apply_log.csv
```

---

## Rollback

Changes can be restored using the execution log.

```powershell
rekordbox-intelligence metadata-rollback `
    output/metadata_apply_log.csv `
    --yes
```

Before restoring the original metadata, the currently modified files are preserved in a safety backup.

---

# Windows and Unicode Support

DJ libraries frequently contain international artist names, accented characters and Unicode symbols.

The CLI explicitly configures UTF-8 output streams to avoid legacy Windows encoding failures.

This includes redirected PowerShell output such as:

```powershell
rekordbox-intelligence classify-benchmark `
    collection.xml `
    ground_truth.csv `
    --show-track-mismatches |
Out-File benchmark.txt -Encoding utf8
```

This prevents failures such as:

```text
UnicodeEncodeError: 'charmap' codec can't encode character
```

---

# Installation

## Requirements

```text
Python >= 3.11
```

Clone the repository:

```powershell
git clone https://github.com/satrohoria/rekordbox-library-intelligence.git
cd rekordbox-library-intelligence
```

Create a virtual environment:

```powershell
py -m venv .venv
```

Install the project and development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Verify the CLI:

```powershell
.\.venv\Scripts\rekordbox-intelligence.exe --help
```

---

# Development

Run the complete test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Current status:

```text
122 passed
```

Compile an individual module:

```powershell
.\.venv\Scripts\python.exe -m py_compile `
    .\src\rekordbox_library_intelligence\classification.py
```

---

# Project Structure

```text
rekordbox-library-intelligence/
│
├── examples/
├── output/
├── src/
│   └── rekordbox_library_intelligence/
│       ├── analytics.py
│       ├── audit.py
│       ├── benchmark_reports.py
│       ├── classification.py
│       ├── classification_benchmark.py
│       ├── classification_diagnostics.py
│       ├── classification_mismatches.py
│       ├── classification_reports.py
│       ├── cli.py
│       ├── console.py
│       ├── duplicates.py
│       ├── ground_truth_template.py
│       ├── history.py
│       ├── history_intelligence.py
│       ├── history_reports.py
│       ├── metadata.py
│       ├── metadata_apply.py
│       ├── metadata_rollback.py
│       ├── parser.py
│       ├── playlists.py
│       ├── rekordbox_ground_truth.py
│       ├── rekordbox_playlists.py
│       ├── reports.py
│       └── segments.py
│
├── tests/
├── README.md
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

---

# Safety Model

Commands can be divided into three categories.

| Category | Examples | Modifies audio files |
|---|---|---|
| Analysis | audit, analytics, history, classification | No |
| Reports | report, classify-report, benchmark reports | No |
| Metadata | metadata-apply, metadata-rollback | Yes, with backup |

The project never modifies the Rekordbox database directly.

---

# Testing

The project currently contains **122 automated tests** covering areas including:

- XML parsing;
- audits;
- duplicate detection;
- segmentation;
- playlist generation;
- analytics;
- HISTORY analysis;
- classification;
- classification benchmarks;
- classification diagnostics;
- ground truth generation;
- metadata modification;
- rollback;
- report generation;
- Windows UTF-8 console behavior;
- CLI integration.

---

# Roadmap

The current `v0.1.0` focuses on reliable library intelligence and reproducible analysis.

Potential future work includes:

- independent validation datasets;
- classification calibration experiments;
- additional DJ transition analytics;
- visualization dashboards;
- richer playlist recommendation models;
- support for additional library export formats.

Experimental classification rules should be validated on independent datasets before being incorporated into the production classifier.

---

# Privacy

Real Rekordbox collections may contain private file paths, listening history and personal library metadata.

Real library exports and validation datasets should **not** be committed to the repository.

Example files in this repository use synthetic data.

---

# Acknowledgments

This project was developed by **Lenilson Nunes** with the assistance of generative AI tools used for collaborative coding, debugging, testing and documentation.

Project requirements, DJ/Rekordbox domain decisions, validation, execution and final implementation decisions were human-led.

---

# License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.

---

## Project status

**v0.1.0 — Release Candidate**

```text
ENERGY accuracy:   94.7%
ENERGY coverage:  100.0%

FUNCTION accuracy: 79.2%
FUNCTION coverage: 82.5%

Automated tests:   122 passing
```

The current development focus is release hardening, documentation and repository cleanup.
