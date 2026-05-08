import argparse
from pathlib import Path

from daily_digest import _authors_year, _tag_summary
from utils import ensure_dir, load_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = {"CORE", "CURATED", "MAYBE"}
ALL_DECISIONS = {"CORE", "CURATED", "MAYBE", "REJECT"}


def _list_value(values):
    return ", ".join(values) if values else ""


def select_candidates(papers, include_rejects=False, decision=None, limit=None):
    allowed = set(ALL_DECISIONS if include_rejects else DEFAULT_DECISIONS)
    if decision:
        allowed = {decision}
    selected = [paper for paper in papers if paper.get("screening_decision") in allowed]
    selected = sorted(selected, key=lambda paper: paper.get("relevance_score", 0), reverse=True)
    if limit is not None:
        selected = selected[:limit]
    return selected


def generate_markdown(papers):
    lines = [
        "# Curation Candidates",
        "",
        "Review candidates below, then apply a human decision with `scripts/curation_apply.py`.",
        "",
        f"Total candidates: {len(papers)}",
        "",
    ]
    if not papers:
        lines.append("No candidates matched the selected filters.")
        lines.append("")
        return "\n".join(lines)

    for index, paper in enumerate(papers, start=1):
        paper_id = paper.get("paper_id", "")
        lines.extend(
            [
                f"## {index}. {paper.get('title', 'Untitled')}",
                "",
                f"- paper_id: `{paper_id}`",
                f"- authors/year: {_authors_year(paper)}",
                f"- url: {paper.get('url', '')}",
                f"- screening_decision: {paper.get('screening_decision', '')}",
                f"- relevance_score: {paper.get('relevance_score', 0)}",
                f"- query_group: {paper.get('query_group', '')}",
                f"- query_mode: {paper.get('query_mode', '')}",
                f"- alloy_system: {_list_value(paper.get('alloy_system', []))}",
                f"- heat_treatment_process: {_list_value(paper.get('heat_treatment_process', []))}",
                f"- property_target: {_list_value(paper.get('property_target', []))}",
                f"- ml_method: {_list_value(paper.get('ml_method', []))}",
                f"- research_position: {_list_value(paper.get('research_position', []))}",
                f"- screening_reason: {paper.get('screening_reason', '')}",
                "",
                "### Abstract",
                "",
                paper.get("abstract", ""),
                "",
                "### Suggested Manual Command",
                "",
                "```bash",
                f'python scripts/curation_apply.py --paper-id {paper_id} --status curated --notes "..."',
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def run(include_rejects=False, limit=None, decision=None):
    papers = load_json(ROOT / "data" / "processed" / "screened_papers.json", [])
    candidates = select_candidates(papers, include_rejects=include_rejects, decision=decision, limit=limit)
    markdown = generate_markdown(candidates)
    output_path = ROOT / "outputs" / "curation_candidates.md"
    ensure_dir(output_path.parent)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Curation candidates written: {output_path}")
    print(f"Candidate count: {len(candidates)}")
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Export machine-screened papers for manual curation.")
    parser.add_argument("--include-rejects", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--decision", choices=sorted(ALL_DECISIONS))
    args = parser.parse_args()
    run(include_rejects=args.include_rejects, limit=args.limit, decision=args.decision)


if __name__ == "__main__":
    main()
