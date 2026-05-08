from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from utils import ensure_dir, load_json


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ["CORE", "CURATED", "MAYBE", "REJECT"]
KEEP_DECISIONS = {"CORE", "CURATED", "MAYBE"}


def _matched_keywords(paper):
    positive = paper.get("matched_positive_keywords") or []
    negative = paper.get("matched_negative_keywords") or []
    parts = []
    if positive:
        parts.append("positive: " + ", ".join(positive))
    if negative:
        parts.append("negative: " + ", ".join(negative))
    return "; ".join(parts) if parts else paper.get("screening_reason", "")


def _query_key(paper):
    group = paper.get("query_group") or "unknown"
    query = paper.get("query") or "unknown query"
    return group, query


def generate_report(papers):
    counts = Counter(paper.get("screening_decision", "REJECT") for paper in papers)
    lines = [
        f"# Query Quality Report - {date.today().isoformat()}",
        "",
        "## Overall Counts",
        f"- Total papers: {len(papers)}",
    ]
    for decision in DECISIONS:
        lines.append(f"- {decision}: {counts.get(decision, 0)}")
    lines.append("")

    lines.extend(["## Top 20 Papers by Relevance Score", ""])
    top = sorted(papers, key=lambda item: item.get("relevance_score", 0), reverse=True)[:20]
    if not top:
        lines.extend(["No screened papers available.", ""])
    for paper in top:
        lines.extend(
            [
                f"### {paper.get('title', 'Untitled')}",
                f"- Score: {paper.get('relevance_score', 0)}",
                f"- Screening decision: {paper.get('screening_decision', 'unreviewed')}",
                f"- Matched keywords: {_matched_keywords(paper)}",
                f"- URL: {paper.get('url', '')}",
                "",
            ]
        )

    grouped = defaultdict(lambda: {"fetched": 0, "kept": 0, "rejected": 0})
    for paper in papers:
        key = _query_key(paper)
        grouped[key]["fetched"] += 1
        if paper.get("screening_decision") in KEEP_DECISIONS:
            grouped[key]["kept"] += 1
        if paper.get("screening_decision") == "REJECT":
            grouped[key]["rejected"] += 1

    lines.extend(["## Query Group Performance", ""])
    if not grouped:
        lines.extend(["No query performance data available.", ""])
    else:
        lines.extend(["| Query group | Query | Fetched count | Kept count | Reject count | Keep ratio |", "| --- | --- | ---: | ---: | ---: | ---: |"])
        for (group, query), stats in sorted(grouped.items()):
            fetched = stats["fetched"]
            kept = stats["kept"]
            ratio = kept / fetched if fetched else 0
            safe_query = query.replace("|", "\\|")
            lines.append(
                f"| {group} | {safe_query} | {fetched} | {kept} | {stats['rejected']} | {ratio:.2f} |"
            )
        lines.append("")

    lines.extend(["## Warning", ""])
    if counts.get("CORE", 0) + counts.get("CURATED", 0) == 0:
        lines.append(
            "WARNING: No CORE or CURATED papers were found. Do not tune thresholds downward before improving query precision or adding better sources."
        )
    else:
        lines.append("CORE or CURATED papers were found. Review them manually before treating them as curated assets.")
    lines.append("")
    return "\n".join(lines)


def run():
    papers = load_json(ROOT / "data" / "processed" / "screened_papers.json", [])
    outputs = ROOT / "outputs"
    ensure_dir(outputs)
    report = generate_report(papers)
    report_path = outputs / "query_quality_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Query quality report written: {report_path}")
    return report


if __name__ == "__main__":
    run()
