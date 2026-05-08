import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from crossref_scanner import crossref_item_to_paper
from paper_normalizer import normalize_paper
from utils import deduplicate_papers


def test_crossref_item_normalizes_to_existing_schema():
    item = {
        "title": ["Machine learning for aluminium alloy heat treatment"],
        "author": [{"given": "Ada", "family": "Lovelace"}],
        "container-title": ["Journal of Alloy Informatics"],
        "DOI": "10.1234/example",
        "URL": "https://doi.org/10.1234/example",
        "abstract": "<jats:p>Predicts ageing response in aluminium alloys.</jats:p>",
        "published-print": {"date-parts": [[2026, 5, 8]]},
        "indexed": {"date-time": "2026-05-09T00:00:00Z"},
    }

    raw = crossref_item_to_paper(item, query_group="core", query="aluminium alloy")
    normalized = normalize_paper(raw)

    assert normalized["source"] == "Crossref"
    assert normalized["doi"] == "10.1234/example"
    assert normalized["authors"] == ["Ada Lovelace"]
    assert normalized["year"] == 2026
    assert normalized["venue"] == "Journal of Alloy Informatics"
    assert normalized["abstract"] == "Predicts ageing response in aluminium alloys."
    assert normalized["query_mode"] == "crossref_query"


def test_deduplicate_prefers_doi_across_arxiv_and_crossref():
    papers = [
        {
            "title": "Aluminium alloy heat treatment with machine learning",
            "doi": "10.1234/shared",
            "source": "arXiv",
        },
        {
            "title": "Different Crossref title for same DOI",
            "doi": "10.1234/shared",
            "source": "Crossref",
        },
    ]

    deduped = deduplicate_papers(papers)

    assert len(deduped) == 1
    assert deduped[0]["source"] == "arXiv"


def test_deduplicate_falls_back_to_normalized_title():
    papers = [
        {
            "title": " Hardness Prediction of Age-Hardening Aluminum Alloy ",
            "doi": "",
            "source": "arXiv",
        },
        {
            "title": "hardness prediction of age-hardening aluminum alloy",
            "doi": "",
            "source": "Crossref",
        },
    ]

    deduped = deduplicate_papers(papers)

    assert len(deduped) == 1
    assert deduped[0]["source"] == "arXiv"
