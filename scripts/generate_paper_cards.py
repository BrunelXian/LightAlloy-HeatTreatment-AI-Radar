import argparse
import re
from pathlib import Path

from utils import ensure_dir, load_json


ROOT = Path(__file__).resolve().parents[1]
STATUS_PRIORITY = {"core": 0, "curated": 1}
HUMAN_NOTES_HEADING = "## Human Reading Notes"
DEFAULT_HUMAN_NOTES = """## Human Reading Notes

### Key contribution
<!-- Fill manually -->

### Method / model
<!-- Fill manually -->

### Dataset / material system
<!-- Fill manually -->

### Heat-treatment relevance
<!-- Fill manually -->

### Evidence useful for review
<!-- Fill manually -->

### Limitations
<!-- Fill manually -->

### Possible citation sentence
<!-- Fill manually -->
"""


def list_text(values):
    return ", ".join(values) if values else ""


def authors_text(authors):
    return ", ".join(authors or [])


def safe_filename(value):
    value = value or "unknown"
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def infer_why_it_matters(paper):
    methods = set(paper.get("ml_method", []))
    positions = set(paper.get("research_position", []))
    properties = set(paper.get("property_target", []))
    processes = set(paper.get("heat_treatment_process", []))
    alloys = set(paper.get("alloy_system", []))

    if "Process optimisation" in positions:
        return "Connects heat-treatment knowledge to process optimisation and decision support."
    if properties and methods:
        return "Links alloy processing or condition data to property prediction with data-driven modelling."
    if processes and alloys:
        return "Provides evidence for process-microstructure-property relationships in light alloys."
    if methods:
        return "Contributes modelling methods that may support future heat-treatment radar baselines."
    return "Curated as potentially useful background for the heat-treatment AI/ML review."


def infer_review_section(paper):
    positions = set(paper.get("research_position", []))
    methods = set(paper.get("ml_method", []))
    properties = set(paper.get("property_target", []))
    processes = set(paper.get("heat_treatment_process", []))

    if "Process optimisation" in positions:
        return "Process optimisation and decision support"
    if "Physics-informed ML" in methods:
        return "Physics-informed and hybrid modelling"
    if "Surrogate model" in methods:
        return "Surrogate modelling for heat-treatment design"
    if properties:
        return "Property prediction and model validation"
    if processes:
        return "Heat-treatment process and microstructure evolution"
    return "Background and related materials informatics"


def infer_reading_priority(paper):
    status = paper.get("manual_status", "")
    score = int(paper.get("relevance_score", 0) or 0)
    if status == "core":
        return "High"
    if score >= 12:
        return "High"
    if score >= 8:
        return "Medium"
    return "Low"


def sorted_reading_queue(records):
    eligible = [paper for paper in records if paper.get("manual_status") in STATUS_PRIORITY]
    return sorted(
        eligible,
        key=lambda paper: (
            STATUS_PRIORITY.get(paper.get("manual_status"), 99),
            -int(paper.get("relevance_score", 0) or 0),
            -int(paper.get("year", 0) or 0),
            paper.get("title", ""),
        ),
    )


def paper_card_markdown(paper):
    lines = [
        f"# {paper.get('title', 'Untitled')}",
        "",
        "## Metadata",
        f"- Paper ID: `{paper.get('paper_id', '')}`",
        f"- Title: {paper.get('title', '')}",
        f"- Authors: {authors_text(paper.get('authors', []))}",
        f"- Year: {paper.get('year') or ''}",
        f"- Venue: {paper.get('venue') or ''}",
        f"- DOI: {paper.get('doi') or ''}",
        f"- URL: {paper.get('url') or ''}",
        f"- Source: {paper.get('source') or ''}",
        f"- Manual status: {paper.get('manual_status') or ''}",
        f"- Manual notes: {paper.get('manual_notes') or ''}",
        f"- Machine screening decision: {paper.get('screening_decision') or ''}",
        f"- Relevance score: {paper.get('relevance_score', 0)}",
        f"- Screening reason: {paper.get('screening_reason') or ''}",
        "",
        "## Tags",
        f"- alloy_system: {list_text(paper.get('alloy_system', []))}",
        f"- heat_treatment_process: {list_text(paper.get('heat_treatment_process', []))}",
        f"- property_target: {list_text(paper.get('property_target', []))}",
        f"- ml_method: {list_text(paper.get('ml_method', []))}",
        f"- research_position: {list_text(paper.get('research_position', []))}",
        "",
        "## Abstract",
        "",
        paper.get("abstract") or "",
        "",
        "## Review Notes",
        f"- Why it matters: {infer_why_it_matters(paper)}",
        f"- Potential review section: {infer_review_section(paper)}",
        f"- Reading priority: {infer_reading_priority(paper)}",
        "",
    ]
    return "\n".join(lines)


def extract_human_notes(existing_markdown):
    marker_index = existing_markdown.find(HUMAN_NOTES_HEADING)
    if marker_index == -1:
        return ""
    return existing_markdown[marker_index:].strip() + "\n"


def merge_card_with_human_notes(new_card, existing_card):
    existing_notes = extract_human_notes(existing_card or "")
    human_notes = existing_notes or DEFAULT_HUMAN_NOTES
    deterministic = new_card.split(HUMAN_NOTES_HEADING, 1)[0].rstrip()
    return deterministic + "\n\n" + human_notes.rstrip() + "\n"


def reading_queue_markdown(records):
    queue = sorted_reading_queue(records)
    lines = [
        "# Core Reading Queue",
        "",
        "Manual `core` papers are listed first, followed by `curated` papers. Within each group, papers are sorted by relevance score and year.",
        "",
        "| Status | Priority | Score | Year | Title | Paper card |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    if not queue:
        lines.append("| - | - | - | - | No curated papers available. | - |")
        return "\n".join(lines) + "\n"

    for paper in queue:
        paper_id = paper.get("paper_id", "")
        card_path = f"paper_cards/{safe_filename(paper_id)}.md"
        title = (paper.get("title") or "").replace("|", "\\|")
        lines.append(
            f"| {paper.get('manual_status', '')} | {infer_reading_priority(paper)} | "
            f"{paper.get('relevance_score', 0)} | {paper.get('year') or ''} | "
            f"{title} | [{paper_id}]({card_path}) |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_paper_cards(curated_path=None, review_dir=None):
    curated_path = Path(curated_path or ROOT / "data" / "curated" / "curated_papers.json")
    review_dir = Path(review_dir or ROOT / "review")
    paper_cards_dir = review_dir / "paper_cards"
    ensure_dir(paper_cards_dir)

    records = load_json(curated_path, [])
    queue = sorted_reading_queue(records)

    for paper in queue:
        paper_id = safe_filename(paper.get("paper_id"))
        card_path = paper_cards_dir / f"{paper_id}.md"
        existing_card = card_path.read_text(encoding="utf-8") if card_path.exists() else ""
        new_card = paper_card_markdown(paper)
        card_path.write_text(merge_card_with_human_notes(new_card, existing_card), encoding="utf-8")

    queue_path = review_dir / "core_reading_queue.md"
    queue_path.write_text(reading_queue_markdown(records), encoding="utf-8")

    print(f"Paper cards written: {paper_cards_dir}")
    print(f"Core reading queue written: {queue_path}")
    print(f"Paper card count: {len(queue)}")
    return queue_path, paper_cards_dir, queue


def main():
    parser = argparse.ArgumentParser(description="Generate paper cards and a core reading queue.")
    parser.add_argument("--curated-path")
    parser.add_argument("--review-dir")
    args = parser.parse_args()
    generate_paper_cards(curated_path=args.curated_path, review_dir=args.review_dir)


if __name__ == "__main__":
    main()
