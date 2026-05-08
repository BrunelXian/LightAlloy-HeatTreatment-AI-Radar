import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from source_quality_report import group_by_source, source_metrics


def test_group_by_source_includes_known_and_unknown_sources():
    papers = [
        {"source": "arXiv", "screening_decision": "CORE"},
        {"source": "Crossref", "screening_decision": "REJECT"},
        {"screening_decision": "MAYBE"},
    ]

    grouped = group_by_source(papers)

    assert len(grouped["arXiv"]) == 1
    assert len(grouped["Crossref"]) == 1
    assert len(grouped["unknown"]) == 1


def test_source_metrics_calculates_ratios_and_average_score():
    papers = [
        {
            "screening_decision": "CORE",
            "relevance_score": 10,
            "doi": "10.1/example",
            "abstract": "available",
        },
        {
            "screening_decision": "MAYBE",
            "relevance_score": 5,
            "doi": "",
            "abstract": "",
        },
        {
            "screening_decision": "REJECT",
            "relevance_score": 0,
            "doi": "10.2/example",
            "abstract": "available",
        },
    ]

    metrics = source_metrics(papers)

    assert metrics["total"] == 3
    assert metrics["CORE"] == 1
    assert metrics["MAYBE"] == 1
    assert metrics["REJECT"] == 1
    assert metrics["keep_ratio"] == 2 / 3
    assert metrics["average_relevance_score"] == 5
    assert metrics["doi_coverage_ratio"] == 2 / 3
    assert metrics["abstract_coverage_ratio"] == 2 / 3


def test_source_metrics_handles_empty_source_group():
    metrics = source_metrics([])

    assert metrics["total"] == 0
    assert metrics["keep_ratio"] == 0
    assert metrics["average_relevance_score"] == 0
    assert metrics["doi_coverage_ratio"] == 0
    assert metrics["abstract_coverage_ratio"] == 0
