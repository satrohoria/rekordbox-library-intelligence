# Rekordbox Library Intelligence

> A safety-first Python toolkit for auditing, analyzing and organizing exported Rekordbox DJ libraries.
>
> **Built from a real DJ workflow, validated against a real DJ library.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![CI](https://github.com/satrohoria/rekordbox-library-intelligence/actions/workflows/tests.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-122%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/badge/release-v0.1.1-brightgreen)

---

## Overview

**Rekordbox Library Intelligence** is a Python command-line toolkit for analyzing exported Rekordbox XML libraries without modifying the Rekordbox database directly.

It was created from practical library-management problems in my own Rekordbox collection, used in my work as DJ **Lenny Santiago**.

Years of collecting, preparing and performing with music created the same problems this toolkit now analyzes:

- duplicate tracks;
- incomplete or inconsistent metadata;
- underused music;
- inconsistent DJ classifications;
- limited visibility into actual library usage;
- playlist maintenance;
- risky bulk metadata changes.

Instead of creating a synthetic portfolio problem, I built the project around workflows I actually needed for my own DJ library.

---

## Development Approach

This project was developed through a **human-led, AI-assisted engineering workflow**.

I defined the requirements, supplied the DJ and Rekordbox domain knowledge, executed and validated the implementation, tested the application against my own real music library, reviewed benchmark results and made the final technical decisions.

Generative AI tools were used collaboratively to assist with:

- code drafting and refactoring;
- debugging and troubleshooting;
- automated test generation;
- CLI design;
- documentation;
- classification rule exploration;
- benchmark analysis.

Generated code and suggestions were not treated as automatically correct. Proposed changes were executed locally, tested, benchmarked and reviewed before being incorporated into the project.

The goal was to use AI as a development accelerator while keeping engineering judgment, validation and final decisions human-led.

---

## Core Principles

### Safety first

Analysis commands are read-only.

Metadata-changing commands require:

- explicit commands;
- backups;
- execution logs;
- confirmation flags.

Rollback support is available for metadata changes.

### Rekordbox database isolation

The toolkit works from exported Rekordbox XML files.

It does **not** modify the Rekordbox database directly.

### Reproducibility

Analytics, reports and classification benchmarks can be regenerated from the same source data.

### Explainable classification

Classification suggestions include confidence and reasoning instead of returning unexplained labels.

### Privacy by design

Real Rekordbox exports, private ground truth, generated reports, backups and logs are excluded from version control.

---

# Features

## Library Audit

Inspect a Rekordbox XML export for common library issues.

```powershell
rekordbox-intelligence audit collection.xml
```

The audit can identify:

- missing artists;
- missing titles;
- missing BPM;
- low bitrate tracks;
- tracks never played;
- total DJ plays.

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

The tool can also recommend which copy to retain based on available quality and usage signals.

---

## Library Segmentation

Segment tracks into operational DJ-library groups:

- `CORE`
- `ROTATION`
- `DISCOVERY`
- `UNASSIGNED`

```powershell
rekordbox-intelligence segments collection.xml
```

---

## Playlist Generation

Generate M3U8 playlists from the segmentation engine.

```powershell
rekordbox-intelligence playlists collection.xml
```

Generated files:

```text
output/
â”œâ”€â”€ CORE.m3u8
â”œâ”€â”€ ROTATION.m3u8
â””â”€â”€ DISCOVERY.m3u8
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

Export analytics to JSON and CSV.

```powershell
rekordbox-intelligence report collection.xml
```

These reports can be reused in spreadsheets, dashboards or additional analysis.

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
- minimum and maximum BPM;
- opening track;
- closing track.

---

## Cross-session Intelligence

```powershell
rekordbox-intelligence history-intelligence collection.xml
```

This analyzes patterns across multiple DJ sessions, including:

- repeated tracks;
- frequently used openers;
- frequently used closers;
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

The project contains an explainable classification engine that infers DJ-oriented attributes from available track metadata.

Classification dimensions include:

- `STYLE`
- `ELEMENTS`
- `ENERGY`
- `FUNCTION`

---

## STYLE

Examples:

- House
- Tech House
- Disco / Nu Disco
- Vocal House
- Classic House
- Pop Remix

---

## ELEMENTS

Examples:

- Vocal
- Piano
- Sax
- Percussion
- Bassline

---

## ENERGY

Current BPM-based ENERGY model:

```text
BPM < 120        -> Warm
120 <= BPM < 123 -> Groove
123 <= BPM < 126 -> Lift
126 <= BPM < 129 -> Strong
BPM >= 129       -> Peak
```

Explicit semantic cues such as `closer`, `last call`, `reset` and `breakdown` can override the BPM model where appropriate.

---

## FUNCTION

FUNCTION uses a hierarchical model.

Explicit semantic cues have priority:

```text
opening / opener / intro -> Opener
bridge                   -> Bridge
singalong                -> Singalong
anthem                   -> Anthem
weapon                   -> Weapon
rescue                   -> Rescue
closing / closer         -> Closer
```

When no explicit semantic cue exists, ENERGY can provide contextual fallback:

```text
Warm   -> Opener
Peak   -> Weapon
Closer -> Closer
```

---

## Classification Preview

Preview classification suggestions without modifying Rekordbox data.

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

Export classification suggestions:

```powershell
rekordbox-intelligence classify-report collection.xml
```

Default output:

```text
output/classification/classification.csv
```

---

# Ground Truth and Benchmarking

Classification quality can be measured against validated ground truth.

## Reproducible Validation Template

Generate a reproducible sample for manual classification:

```powershell
rekordbox-intelligence ground-truth-template collection.xml `
    --sample-size 50 `
    --seed 42
```

---

## Rekordbox Grouping Ground Truth

The project can convert structured Rekordbox `Grouping` metadata into validation labels:

```powershell
rekordbox-intelligence rekordbox-ground-truth collection.xml
```

`Grouping` is used only as a source of validation labels.

It is **not used as an input feature by the classifier**, which prevents direct target leakage.

---

# Real DJ Library Validation

The classification engine was evaluated against a validation dataset derived from **my own real Rekordbox DJ library**, used in my work as DJ **Lenny Santiago**.

This makes the benchmark representative of an actual long-running DJ workflow rather than a purely synthetic dataset.

Where applicable, structured Rekordbox `Grouping` metadata was used to derive validation labels. Because `Grouping` is not used by the classifier itself, the benchmark avoids direct target leakage.

### Validation dataset

```text
Source:               Personal Rekordbox DJ library
DJ project:           Lenny Santiago
Library tracks:       996
Ground-truth tracks:  989
```

---

## ENERGY Benchmark

```text
Evaluated:            989
Predictions present:  989
Missing predictions:    0
Correct:              937

Coverage:           100.0%
Accuracy:            94.7%
```

The original ENERGY model achieved **77.8% accuracy**.

Analysis of real-library distributions revealed two dominant mismatch patterns:

```text
Strong -> Peak
Lift   -> Groove
```

After recalibrating the BPM boundaries, ENERGY accuracy improved to:

```text
77.8% -> 94.7%
```

while maintaining:

```text
100.0% prediction coverage
```

A later candidate optimization was intentionally not adopted because it risked overfitting the same validation dataset.

---

## FUNCTION Benchmark

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

The original FUNCTION model produced almost no useful predictions.

A hierarchical approach using semantic rules plus ENERGY fallback significantly improved practical coverage while preserving explainability.

---

## Benchmark Command

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

Detailed mismatches:

```powershell
rekordbox-intelligence classify-benchmark `
    collection.xml `
    ground_truth.csv `
    --show-track-mismatches
```

---

## Reproducible Benchmark Reports

Export benchmark results automatically:

```powershell
rekordbox-intelligence classify-benchmark `
    collection.xml `
    ground_truth.csv `
    --report-dir output/benchmarks
```

Generated files:

```text
output/benchmarks/
â”œâ”€â”€ benchmark_summary.json
â”œâ”€â”€ energy_mismatches.csv
â””â”€â”€ function_mismatches.csv
```

---

# Metadata Correction Workflow

The toolkit supports controlled Artist and Title metadata corrections.

## Preview

```powershell
rekordbox-intelligence metadata-preview corrections.csv
```

This is a dry run.

No audio files are modified.

---

## Apply

```powershell
rekordbox-intelligence metadata-apply corrections.csv --yes
```

Before modification, the application creates backups and writes an execution log.

Default locations:

```text
output/metadata_backups/
output/metadata_apply_log.csv
```

---

## Rollback

Restore metadata changes from a previous execution log:

```powershell
rekordbox-intelligence metadata-rollback `
    output/metadata_apply_log.csv `
    --yes
```

Before restoring original metadata, the currently modified files are preserved in a safety backup.

---

# Windows and Unicode Support

DJ libraries frequently contain international artist names, accented characters and Unicode symbols.

The CLI configures UTF-8 output streams to avoid legacy Windows encoding failures.

Redirected PowerShell output is supported:

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

Run the full automated test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Current validated status:

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
â”‚
â”œâ”€â”€ docs/
â”œâ”€â”€ examples/
â”œâ”€â”€ output/
â”œâ”€â”€ src/
â”‚   â””â”€â”€ rekordbox_library_intelligence/
â”‚       â”œâ”€â”€ analytics.py
â”‚       â”œâ”€â”€ audit.py
â”‚       â”œâ”€â”€ benchmark_reports.py
â”‚       â”œâ”€â”€ classification.py
â”‚       â”œâ”€â”€ classification_benchmark.py
â”‚       â”œâ”€â”€ classification_diagnostics.py
â”‚       â”œâ”€â”€ classification_mismatches.py
â”‚       â”œâ”€â”€ classification_reports.py
â”‚       â”œâ”€â”€ cli.py
â”‚       â”œâ”€â”€ console.py
â”‚       â”œâ”€â”€ duplicates.py
â”‚       â”œâ”€â”€ ground_truth_template.py
â”‚       â”œâ”€â”€ history.py
â”‚       â”œâ”€â”€ history_intelligence.py
â”‚       â”œâ”€â”€ history_reports.py
â”‚       â”œâ”€â”€ metadata.py
â”‚       â”œâ”€â”€ metadata_apply.py
â”‚       â”œâ”€â”€ metadata_rollback.py
â”‚       â”œâ”€â”€ parser.py
â”‚       â”œâ”€â”€ playlists.py
â”‚       â”œâ”€â”€ rekordbox_ground_truth.py
â”‚       â”œâ”€â”€ rekordbox_playlists.py
â”‚       â”œâ”€â”€ reports.py
â”‚       â””â”€â”€ segments.py
â”‚
â”œâ”€â”€ tests/
â”œâ”€â”€ README.md
â”œâ”€â”€ LICENSE
â”œâ”€â”€ pyproject.toml
â””â”€â”€ requirements.txt
```

---

# Safety Model

| Category | Examples | Modifies audio files |
|---|---|---|
| Analysis | audit, analytics, history, classification | No |
| Reports | report, classify-report, benchmark reports | No |
| Metadata | metadata-apply, metadata-rollback | Yes, with backup |

The project never modifies the Rekordbox database directly.

---

# Testing

The project currently contains **122 automated tests** covering:

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

# AI-Assisted Engineering

Generative AI was used as a development partner throughout this project.

The working process followed an iterative cycle:

```text
Problem definition
        â†“
AI-assisted implementation
        â†“
Local execution
        â†“
Automated tests
        â†“
Real-library validation
        â†“
Benchmark analysis
        â†“
Human review and decision
```

The benchmark calibration process is one example of this workflow.

ENERGY accuracy improved from:

```text
77.8% -> 94.7%
```

A further candidate optimization was deliberately rejected after analysis indicated a risk of overfitting the validation dataset.

This project therefore documents not only AI-assisted implementation, but also the validation and engineering judgment required to decide when **not** to accept an optimization.

---

# Privacy

Real Rekordbox collections may contain:

- private file paths;
- listening and performance history;
- personal library metadata;
- validation labels;
- metadata backups.

Real library exports and private validation datasets are intentionally excluded from version control.

The repository contains synthetic example data for reproducibility.

---

# Roadmap

The current release focuses on reliable library intelligence, explainable classification and reproducible analysis.

Potential future work includes:

- independent validation datasets;
- classification calibration experiments;
- additional DJ transition analytics;
- visualization dashboards;
- richer playlist recommendation models;
- support for additional library export formats.

Experimental classification rules should be validated on independent datasets before being incorporated into the production classifier.

---

# Acknowledgments

This project was developed by **Lenilson Nunes / DJ Lenny Santiago** with the assistance of generative AI tools used for collaborative coding, debugging, testing and documentation.

Project requirements, DJ/Rekordbox domain decisions, local execution, validation and final implementation decisions were human-led.

---

# License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.

---

## Project Status

**Stable release: v0.1.1**

```text
ENERGY accuracy:    94.7%
ENERGY coverage:   100.0%

FUNCTION accuracy:  79.2%
FUNCTION coverage:  82.5%

Automated tests:    122 passing
```

The next development focus is independent validation and future analytical improvements.
