from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from utils import ensure_dir, load_json


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ["CORE", "CURATED", "MAYBE", "REJECT"]
KEEP_DECISIONS = {"CORE", "CURATED", "MAYBE"}
SOURCE_ORDER = ["arXiv", "Crossref", "unknown"]


def source_name(paper):
    return paper.get("source") or "unknown"


def ratio(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def group_by_source(papers):
    grouped = defaultdict(list)
    for paper in papers:
        grouped[source_name(paper)].append(paper)
    for source in SOURCE_ORDER:
        grouped.setdefault(source, [])
    return dict(grouped)


def source_metrics(papers):
    total = len(papers)
    counts = Counter(paper.get("screening_decision", "REJECT") for paper in papers)
    keep_count = sum(counts.get(decision, 0) for decision in KEEP_DECISIONS)
    score_sum = sum(float(paper.get("relevance_score", 0) or 0) for paper in papers)
    doi_count = sum(1 for paper in papers if paper.get("doi"))
    abstract_count = sum(1 for paper in papers if paper.get("abstract"))
    return {
        "total": total,
        "CORE": counts.get("CORE", 0),
        "CURATED": counts.get("CURATED", 0),
        "MAYBE": counts.get("MAYBE", 0),
        "REJECT": counts.get("REJECT", 0),
        "keep_ratio": ratio(keep_count, total),
        "average_relevance_score": ratio(score_sum, total),
        "doi_coverage_ratio": ratio(doi_count, total),
        "abstract_coverage_ratio": ratio(abstract_count, total),
    }


def _format_keywords(paper):
    keywords = paper.get("matched_positive_keywords") or []
    return ", ".join(keywords) if keywords else ""


def _yes_no(value):
    return "yes" if value else "no"


def _ordered_sources(grouped):
    ordered = [source for source in SOURCE_ORDER if source in grouped]
    ordered.extend(sorted(source for source in grouped if source not in SOURCE_ORDER))
    return ordered


def generate_report(papers):
    grouped = group_by_source(papers)
    lines = [
        f"# Source Quality Report - {date.today().isoformat()}",
        "",
        "## Source Summary",
        "",
        "| Source | Total | CORE | CURATED | MAYBE | REJECT | Keep ratio | Avg relevance | DOI coverage | Abstract coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for source in _ordered_sources(grouped):
        metrics = source_metrics(grouped[source])
        lines.append(
            f"| {source} | {metrics['total']} | {metrics['CORE']} | {metrics['CURATED']} | "
            f"{metrics['MAYBE']} | {metrics['REJECT']} | {metrics['keep_ratio']:.2f} | "
            f"{metrics['average_relevance_score']:.2f} | {metrics['doi_coverage_ratio']:.2f} | "
            f"{metrics['abstract_coverage_ratio']:.2f} |"
        )
    lines.append("")

    crossref = sorted(
        grouped.get("Crossref", []),
        key=lambda paper: paper.get("relevance_score", 0),
        reverse=True,
    )[:20]
    lines.extend(["## Top Crossref Candidates", ""])
    if not crossref:
        lines.extend(["No Crossref records available.", ""])
        return "\n".join(lines)

    for paper in crossref:
        lines.extend(
            [
                f"### {paper.get('title', 'Untitled')}",
                f"- Year: {paper.get('year') or ''}",
                f"- Venue: {paper.get('venue') or ''}",
                f"- DOI: {paper.get('doi') or ''}",
                f"- URL: {paper.get('url') or ''}",
                f"- Screening decision: {paper.get('screening_decision') or ''}",
                f"- Relevance score: {paper.get('relevance_score', 0)}",
                f"- Matched positive keywords: {_format_keywords(paper)}",
                f"- Abstract availability: {_yes_no(paper.get('abstract'))}",
                "",
            ]
        )
    return "\n".join(lines)


def run():
    papers = load_json(ROOT / "data" / "processed" / "screened_papers.json", [])
    outputs = ROOT / "outputs"
    ensure_dir(outputs)
    report = generate_report(papers)
    report_path = outputs / "source_quality_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Source quality report written: {report_path}")
    return report


if __name__ == "__main__":
    run()
