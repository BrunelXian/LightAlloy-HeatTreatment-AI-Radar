from pathlib import Path

from utils import deduplicate_papers, load_json, save_json, stable_paper_id


ROOT = Path(__file__).resolve().parents[1]


SCHEMA_DEFAULTS = {
    "paper_id": "",
    "title": "",
    "authors": [],
    "year": None,
    "venue": "",
    "doi": "",
    "arxiv_id": "",
    "url": "",
    "abstract": "",
    "source": "",
    "published_date": "",
    "updated_date": "",
    "query_group": "",
    "query": "",
    "query_mode": "",
    "query_source_quality": "",
    "keywords": [],
    "alloy_system": [],
    "heat_treatment_process": [],
    "property_target": [],
    "ml_method": [],
    "research_position": [],
    "relevance_score": 0,
    "screening_decision": "unreviewed",
    "screening_reason": "",
    "matched_positive_keywords": [],
    "matched_negative_keywords": [],
    "summary_short": "",
    "manual_status": "unreviewed",
    "manual_notes": "",
}


def normalize_paper(raw):
    paper = dict(SCHEMA_DEFAULTS)
    for key in paper:
        if key in raw and raw[key] is not None:
            paper[key] = raw[key]
    paper["authors"] = raw.get("authors") or []
    if isinstance(paper["authors"], str):
        paper["authors"] = [paper["authors"]]
    paper["paper_id"] = stable_paper_id(
        title=paper["title"],
        year=paper["year"],
        doi=paper["doi"],
        arxiv_id=paper["arxiv_id"],
    )
    return paper


def run():
    raw = load_json(ROOT / "data" / "raw" / "raw_papers.json", [])
    normalized = [normalize_paper(paper) for paper in raw]
    normalized = deduplicate_papers(normalized)
    save_json(ROOT / "data" / "processed" / "normalized_papers.json", normalized)
    print(f"Normalized papers: {len(normalized)}")
    return normalized


if __name__ == "__main__":
    run()
