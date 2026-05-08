import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from crossref_scanner import crossref_item_to_paper, iter_crossref_queries, passes_precision_filter
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


def test_crossref_high_precision_query_loading():
    source_config = {
        "sources": {"crossref": {"query_mode": "high_precision"}},
        "crossref_queries": {
            "high_precision": [
                '"aluminum alloy" "heat treatment" "machine learning"',
                '"Al-Mg-Si" ageing "machine learning"',
            ]
        },
    }
    fallback = {"core": ["broad fallback query"]}

    queries = list(iter_crossref_queries(source_config, fallback))

    assert queries == [
        ("crossref_high_precision", '"aluminum alloy" "heat treatment" "machine learning"'),
        ("crossref_high_precision", '"Al-Mg-Si" ageing "machine learning"'),
    ]


def test_precision_filter_keeps_valid_aluminium_heat_treatment_ml_paper():
    paper = {
        "title": "Machine learning prediction of aging response in aluminum alloy 6061",
        "abstract": "The model predicts heat treatment outcomes after artificial aging.",
        "venue": "Materials Informatics",
        "query": '"6061" aging "machine learning"',
    }

    assert passes_precision_filter(paper)


def test_precision_filter_rejects_corrosion_alloy_design_without_heat_treatment_focus():
    paper = {
        "title": "Corrosion resistant aluminum alloy design through machine learning",
        "abstract": "The study optimizes corrosion performance and mechanical properties.",
        "venue": "Corrosion Science",
        "query": "aluminum alloy machine learning",
    }

    assert not passes_precision_filter(paper)


def test_precision_filter_rejects_generic_ml_without_aluminium_context():
    paper = {
        "title": "Deep learning for image classification",
        "abstract": "A neural network benchmark for generic machine learning tasks.",
        "venue": "Computer Vision Letters",
        "query": "deep learning optimization",
    }

    assert not passes_precision_filter(paper)
