# LightAlloy-HeatTreatment-AI-Radar

[![Project Type](https://img.shields.io/badge/project-research%20radar-blue)](#)
[![Focus](https://img.shields.io/badge/focus-AI%20for%20Manufacturing-important)](#)
[![Scope](https://img.shields.io/badge/scope-processes%2C%20control%2C%20digital%20twin-success)](#)
[![Status](https://img.shields.io/badge/status-active%20development-orange)](#)

> A structured research radar for AI/ML-driven heat treatment of aluminium and light alloys.

[中文说明](README_CN.MD)

## What This Project Is

`LightAlloy-HeatTreatment-AI-Radar` is a maintainable literature radar for tracking, screening, curating, and reusing research knowledge in AI/ML-assisted heat treatment of aluminium and light alloys.

It is not a static paper list or a PDF storage repository. The goal is to transform scattered literature into structured, review-ready knowledge.

```text
Papers -> Structured Knowledge -> Manual Curation -> Review Assets
```

## Current Phase

The repository currently supports a Phase 1 workflow:

- Search arXiv as the primary daily discovery source.
- Normalize paper metadata into a stable schema.
- Deduplicate records by DOI first, then normalized title.
- Screen papers with deterministic keyword rules.
- Assign material/process/property/model tags.
- Generate daily digest and query/source quality reports.
- Export curation candidates for human review.
- Persist human decisions in curated/rejected JSON assets.
- Generate paper cards and a core reading queue for literature review work.
- Run a daily GitHub Actions scan and upload generated runtime outputs as artifacts.

Crossref support exists in the codebase but is disabled by default for daily discovery because it is currently too noisy. It may be reused later for DOI, venue, and publisher metadata enrichment or manual diagnostics.

## Quick Start

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
python scripts/curation_export.py --limit 20
python scripts/curation_status.py
python scripts/generate_paper_cards.py
```

## Main Outputs

Runtime outputs, ignored by git:

- `data/raw/raw_papers.json`
- `data/processed/normalized_papers.json`
- `data/processed/screened_papers.json`
- `outputs/daily_digest.md`
- `outputs/query_quality_report.md`
- `outputs/source_quality_report.md`
- `outputs/curation_candidates.md`
- `outputs/curation_status.md`

Persistent research assets, tracked by git:

- `data/curated/curated_papers.json`
- `data/curated/rejected_papers.json`
- `review/core_reading_queue.md`
- `review/paper_cards/*.md`

## Manual Curation Workflow

Machine screening is only a first pass. Human decisions are stored separately.

```bash
python scripts/run_pipeline.py
python scripts/curation_export.py --limit 20
python scripts/curation_apply.py --paper-id PAPER_ID --status core --notes "Must-read paper for heat-treatment ML review."
python scripts/curation_apply.py --paper-id PAPER_ID --status curated --notes "Relevant candidate for process-property modelling."
python scripts/curation_apply.py --paper-id PAPER_ID --status rejected --notes "False positive: not focused on aluminium/light-alloy heat treatment."
python scripts/curation_status.py
```

- `screening_decision` is machine-generated.
- `manual_status` is the human decision layer.
- `curated_papers.json` is the persistent reviewed library.
- `rejected_papers.json` prevents repeated review of low-value papers.

## Paper Cards and Reading Queue

Curated papers can be converted into reusable review notes:

```bash
python scripts/generate_paper_cards.py
```

This generates:

- `review/core_reading_queue.md`
- `review/paper_cards/<paper_id>.md`

Each paper card contains deterministic metadata, tags, screening information, abstract, review placement hints, and a stable `Human Reading Notes` section for manual literature-review notes.

Existing manual notes in paper cards are preserved when cards are regenerated.

## Daily Automation

GitHub Actions runs the daily literature radar scan and also supports manual dispatch.

The workflow:

- installs dependencies
- runs the pipeline
- exports curation candidates
- generates curation status
- runs tests
- uploads runtime outputs as the `literature-radar-output` artifact

Generated raw, processed, and output files are not committed automatically. Human curation remains manual.

## Data Versioning Policy

Runtime files are ignored by default:

- `data/raw/*.json`
- `data/processed/*.json`
- `data/checkpoints/*.json`
- `outputs/*.md`

Curated JSON files and review paper cards are the durable research assets.

## Repository Structure

```text
LightAlloy-HeatTreatment-AI-Radar/
  config/
  data/
    raw/
    processed/
    curated/
    checkpoints/
  outputs/
  review/
    core_reading_queue.md
    paper_cards/
  scripts/
  tests/
  .github/workflows/
  README.md
  README_CN.MD
```

## Research Questions

1. What has already been solved in heat-treatment ML?
2. What are the main data bottlenecks?
3. Where does physics-informed ML outperform pure data-driven ML?
4. How can reliable surrogate models be built for process-property prediction?
5. How can uncertainty-aware prediction be introduced?
6. How can the field move toward optimisation, closed-loop control, and digital twins?

## Author

Xian
