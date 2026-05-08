# LightAlloy-HeatTreatment-AI-Radar

[![Project Type](https://img.shields.io/badge/project-research%20radar-blue)](#)
[![Focus](https://img.shields.io/badge/focus-AI%20for%20Manufacturing-important)](#)
[![Scope](https://img.shields.io/badge/scope-processes%2C%20control%2C%20digital%20twin-success)](#)
[![Status](https://img.shields.io/badge/status-active%20development-orange)](#)

> A structured research radar for AI/ML-driven heat treatment of aluminium and light alloys.

[中文说明](README_CN.MD)

## What This Project Is

`LightAlloy-HeatTreatment-AI-Radar` is a continuously evolving intelligence system for tracking, structuring, and reusing research knowledge in AI/ML-assisted heat treatment of light alloys.

It is not just a paper list. The long-term goal is to transform fragmented literature into structured knowledge that supports modelling, process optimisation, and future closed-loop control.

```text
Papers -> Structured Knowledge -> Modelling -> Optimisation
```

## Why It Matters

Heat treatment of aluminium and light alloys is industrially important, data-rich, and still heavily dependent on experience-based rules. Meanwhile, AI/ML studies in this area are scattered across materials science, manufacturing, modelling, and control.

This project aims to connect:

- heat-treatment processes
- alloy systems and microstructure evolution
- mechanical properties
- machine learning and physics-informed models
- optimisation and digital twin workflows

## System Modules

| Module | Purpose |
| --- | --- |
| Data pipeline | Collect papers, extract metadata, screen relevance, and store structured records. |
| Knowledge structuring | Decompose papers into process, material, property, method, and dataset information. |
| Research outputs | Generate digests, reference notes, review-ready summaries, and curated datasets. |
| Modelling foundation | Prepare data and baselines for ML, surrogate modelling, and physics-informed learning. |
| Optimisation layer | Support process optimisation, uncertainty-aware prediction, and future closed-loop control. |

## Knowledge Schema

Each paper is expected to be organized around:

- **Process**: solution treatment, ageing, quenching, deformation, thermomechanical routes
- **Material**: alloy system, composition, initial condition, processing history
- **Target**: hardness, strength, elongation, microstructure, precipitation behaviour
- **Method**: ML model, physics-informed model, surrogate model, optimisation algorithm
- **Data**: dataset source, feature variables, target variables, evaluation metrics

## Repository Structure

```text
LightAlloy-HeatTreatment-AI-Radar/
  data/
    raw_papers.json
    screened_papers.json
    curated_papers.json

  refs/
    aluminium_alloys.md
    heat_treatment_process.md
    ml_models.md
    physics_informed_ml.md

  scripts/
    paper_scanner.py
    paper_screener.py
    tag_assigner.py
    summary_generator.py

  outputs/
    daily_digest.md
    weekly_summary.md

  review/
    outline.md
    sections/

  README.md
  README_CN.MD
```

## Research Questions

1. What has already been solved in heat-treatment ML?
2. What are the main data bottlenecks in this field?
3. Where does physics-informed ML outperform pure data-driven ML?
4. How can reliable surrogate models be built for heat-treatment process-property prediction?
5. How can uncertainty-aware prediction be introduced?
6. How can the field move toward process optimisation and closed-loop control?

## Roadmap

- Build a structured paper collection and screening workflow.
- Create curated metadata and tagging standards.
- Generate daily or weekly research digests.
- Prepare review-ready summaries and reference notes.
- Build ML-ready datasets for process-property modelling.
- Explore physics-informed ML and surrogate modelling.
- Move toward RL-based optimisation and digital twin integration.

## Status

This repository is under active development. Daily or weekly research updates are planned.

## Author

Xian
