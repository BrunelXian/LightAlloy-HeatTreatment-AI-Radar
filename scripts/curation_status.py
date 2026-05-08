from collections import Counter
from pathlib import Path

from utils import ensure_dir, load_json


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ["CORE", "CURATED", "MAYBE", "REJECT"]


def _ids(records):
    return {record.get("paper_id") for record in records if record.get("paper_id")}


def build_status(screened, curated, rejected):
    machine_counts = Counter(paper.get("screening_decision", "REJECT") for paper in screened)
    curated_ids = _ids(curated)
    rejected_ids = _ids(rejected)
    reviewed_ids = curated_ids | rejected_ids
    human_counts = Counter(record.get("manual_status", "curated") for record in curated)
    rejected_count = sum(1 for record in rejected if record.get("manual_status") == "rejected")

    unreviewed = {}
    for decision in ["CORE", "CURATED", "MAYBE"]:
        unreviewed[decision] = sum(
            1
            for paper in screened
            if paper.get("screening_decision") == decision and paper.get("paper_id") not in reviewed_ids
        )

    return {
        "total_screened": len(screened),
        "machine_counts": {decision: machine_counts.get(decision, 0) for decision in DECISIONS},
        "human_curated_count": human_counts.get("curated", 0),
        "human_core_count": human_counts.get("core", 0),
        "human_rejected_count": rejected_count,
        "unreviewed_core_candidates": unreviewed["CORE"],
        "unreviewed_curated_candidates": unreviewed["CURATED"],
        "unreviewed_maybe_candidates": unreviewed["MAYBE"],
    }


def status_markdown(status):
    lines = [
        "# Curation Status",
        "",
        f"- Total screened papers: {status['total_screened']}",
        f"- CORE: {status['machine_counts']['CORE']}",
        f"- CURATED: {status['machine_counts']['CURATED']}",
        f"- MAYBE: {status['machine_counts']['MAYBE']}",
        f"- REJECT: {status['machine_counts']['REJECT']}",
        f"- Human curated count: {status['human_curated_count']}",
        f"- Human core count: {status['human_core_count']}",
        f"- Human rejected count: {status['human_rejected_count']}",
        f"- Unreviewed CORE candidates: {status['unreviewed_core_candidates']}",
        f"- Unreviewed CURATED candidates: {status['unreviewed_curated_candidates']}",
        f"- Unreviewed MAYBE candidates: {status['unreviewed_maybe_candidates']}",
        "",
    ]
    return "\n".join(lines)


def run():
    screened = load_json(ROOT / "data" / "processed" / "screened_papers.json", [])
    curated = load_json(ROOT / "data" / "curated" / "curated_papers.json", [])
    rejected = load_json(ROOT / "data" / "curated" / "rejected_papers.json", [])
    status = build_status(screened, curated, rejected)
    markdown = status_markdown(status)
    output_path = ROOT / "outputs" / "curation_status.md"
    ensure_dir(output_path.parent)
    output_path.write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"Curation status written: {output_path}")
    return status


if __name__ == "__main__":
    run()
