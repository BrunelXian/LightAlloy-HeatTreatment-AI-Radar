import argparse
from copy import deepcopy
from datetime import date
from pathlib import Path

from utils import load_json, save_json


ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {"curated", "core", "rejected"}


def _upsert(records, paper):
    paper_id = paper.get("paper_id")
    updated = []
    inserted = False
    for record in records:
        if record.get("paper_id") == paper_id:
            updated.append(paper)
            inserted = True
        else:
            updated.append(record)
    if not inserted:
        updated.append(paper)
    return updated


def _remove(records, paper_id):
    return [record for record in records if record.get("paper_id") != paper_id]


def find_paper(screened, paper_id):
    for paper in screened:
        if paper.get("paper_id") == paper_id:
            return paper
    return None


def apply_curation(
    paper_id,
    status,
    notes=None,
    screened_path=None,
    curated_path=None,
    rejected_path=None,
    curation_date=None,
):
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")

    screened_path = Path(screened_path or ROOT / "data" / "processed" / "screened_papers.json")
    curated_path = Path(curated_path or ROOT / "data" / "curated" / "curated_papers.json")
    rejected_path = Path(rejected_path or ROOT / "data" / "curated" / "rejected_papers.json")
    curation_date = curation_date or date.today().isoformat()

    screened = load_json(screened_path, [])
    curated = load_json(curated_path, [])
    rejected = load_json(rejected_path, [])

    source = find_paper(screened, paper_id)
    if source is None:
        raise ValueError(f"paper_id not found in screened papers: {paper_id}")

    existing = find_paper(curated, paper_id) or find_paper(rejected, paper_id) or {}
    record = deepcopy(source)
    record["manual_status"] = status
    if notes is not None:
        record["manual_notes"] = notes
    else:
        record["manual_notes"] = existing.get("manual_notes", record.get("manual_notes", ""))
    record["curation_date"] = curation_date

    if status in {"curated", "core"}:
        curated = _upsert(curated, record)
        rejected = _remove(rejected, paper_id)
    else:
        rejected = _upsert(rejected, record)
        curated = _remove(curated, paper_id)

    save_json(curated_path, curated)
    save_json(rejected_path, rejected)

    print(f"Applied manual status '{status}' to paper_id {paper_id}")
    print(f"Curated records: {len(curated)}")
    print(f"Rejected records: {len(rejected)}")
    return record, curated, rejected


def list_top(limit, screened_path=None):
    screened_path = Path(screened_path or ROOT / "data" / "processed" / "screened_papers.json")
    screened = load_json(screened_path, [])
    candidates = [
        paper
        for paper in screened
        if paper.get("screening_decision") in {"CORE", "CURATED", "MAYBE"}
    ]
    candidates = sorted(candidates, key=lambda paper: paper.get("relevance_score", 0), reverse=True)[:limit]
    for paper in candidates:
        print(
            f"{paper.get('paper_id')} | {paper.get('screening_decision')} | "
            f"{paper.get('relevance_score')} | {paper.get('title')}"
        )
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Apply a human curation decision to a screened paper.")
    parser.add_argument("--paper-id")
    parser.add_argument("--status", choices=sorted(VALID_STATUSES))
    parser.add_argument("--notes")
    parser.add_argument("--list-top", type=int)
    args = parser.parse_args()

    if args.list_top is not None:
        list_top(args.list_top)
        return

    if not args.paper_id or not args.status:
        parser.error("--paper-id and --status are required unless --list-top is used")

    apply_curation(args.paper_id, args.status, notes=args.notes)


if __name__ == "__main__":
    main()
