from collections import Counter
from datetime import date
from pathlib import Path

from utils import ensure_dir, load_json


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ["CORE", "CURATED", "MAYBE", "REJECT"]


def _authors_year(paper):
    authors = paper.get("authors") or []
    if len(authors) > 3:
        author_text = ", ".join(authors[:3]) + " et al."
    else:
        author_text = ", ".join(authors)
    return f"{author_text} ({paper.get('year') or 'n.d.'})"


def _tag_summary(paper):
    groups = [
        ("alloy", paper.get("alloy_system", [])),
        ("process", paper.get("heat_treatment_process", [])),
        ("property", paper.get("property_target", [])),
        ("method", paper.get("ml_method", [])),
        ("position", paper.get("research_position", [])),
    ]
    parts = []
    for label, values in groups:
        if values:
            parts.append(f"{label}: {', '.join(values)}")
    return "; ".join(parts) if parts else "no tags assigned"


def _why_it_matters(paper):
    tags = []
    for field in ["alloy_system", "heat_treatment_process", "property_target", "ml_method", "research_position"]:
        tags.extend(paper.get(field, []))
    if tags:
        return "Connects " + ", ".join(tags[:4]) + " for the radar knowledge base."
    return "Potentially relevant to the literature radar based on keyword screening."


def _section(title, papers, limit=20):
    lines = [f"## {title}", ""]
    if not papers:
        lines.extend(["No papers in this section.", ""])
        return lines
    for paper in sorted(papers, key=lambda item: item.get("relevance_score", 0), reverse=True)[:limit]:
        lines.extend(
            [
                f"### {paper.get('title', 'Untitled')}",
                "",
                f"- Authors/year: {_authors_year(paper)}",
                f"- URL: {paper.get('url', '')}",
                f"- Relevance score: {paper.get('relevance_score', 0)}",
                f"- Tags: {_tag_summary(paper)}",
                f"- Screening reason: {paper.get('screening_reason', '')}",
                f"- Why it matters: {_why_it_matters(paper)}",
                "",
            ]
        )
    return lines


def generate_daily_digest(papers):
    counts = Counter(paper.get("screening_decision", "REJECT") for paper in papers)
    by_decision = {decision: [] for decision in DECISIONS}
    for paper in papers:
        by_decision.setdefault(paper.get("screening_decision", "REJECT"), []).append(paper)

    lines = [
        f"# Daily Digest - {date.today().isoformat()}",
        "",
        "## Summary",
        f"- Total papers: {len(papers)}",
    ]
    for decision in DECISIONS:
        lines.append(f"- {decision}: {counts.get(decision, 0)}")
    lines.append("")

    lines.extend(_section("CORE Papers", by_decision["CORE"]))
    lines.extend(_section("CURATED Candidates", by_decision["CURATED"]))
    lines.extend(_section("MAYBE Papers", by_decision["MAYBE"]))
    lines.extend(_section("Rejected Papers", by_decision["REJECT"]))
    return "\n".join(lines)


def generate_weekly_summary(papers):
    top = [
        paper
        for paper in sorted(papers, key=lambda item: item.get("relevance_score", 0), reverse=True)
        if paper.get("screening_decision") in {"CORE", "CURATED"}
    ][:20]
    lines = [
        f"# Weekly Summary - {date.today().isoformat()}",
        "",
        "This placeholder weekly summary lists the top CORE/CURATED papers from the current screened dataset.",
        "",
    ]
    if not top:
        lines.append("No CORE or CURATED papers available yet.")
    for paper in top:
        lines.extend(
            [
                f"## {paper.get('title', 'Untitled')}",
                f"- Decision: {paper.get('screening_decision')}",
                f"- Score: {paper.get('relevance_score', 0)}",
                f"- URL: {paper.get('url', '')}",
                f"- Tags: {_tag_summary(paper)}",
                "",
            ]
        )
    return "\n".join(lines)


def run():
    papers = load_json(ROOT / "data" / "processed" / "screened_papers.json", [])
    outputs = ROOT / "outputs"
    ensure_dir(outputs)
    daily = generate_daily_digest(papers)
    weekly = generate_weekly_summary(papers)
    (outputs / "daily_digest.md").write_text(daily, encoding="utf-8")
    (outputs / "weekly_summary.md").write_text(weekly, encoding="utf-8")
    print(f"Daily digest written: {outputs / 'daily_digest.md'}")
    print(f"Weekly summary written: {outputs / 'weekly_summary.md'}")
    return daily, weekly


if __name__ == "__main__":
    run()
