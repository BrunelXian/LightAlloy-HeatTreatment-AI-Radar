import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from paper_screener import VALID_DECISIONS, screen_papers


RULES = {
    "positive_keywords": {
        "aluminium": 3,
        "alloy": 2,
        "heat treatment": 4,
        "machine learning": 4,
        "aging": 3,
    },
    "negative_keywords": {
        "concrete": -3,
    },
    "decision_thresholds": {
        "core": 12,
        "curated": 8,
        "maybe": 5,
        "reject": 0,
    },
}


def test_relevant_paper_scores_higher_than_unrelated_paper():
    papers = [
        {
            "title": "Machine learning for aluminium alloy heat treatment",
            "abstract": "Aging and heat treatment of aluminium alloy are modelled using machine learning.",
        },
        {
            "title": "Concrete bridge inspection",
            "abstract": "A civil engineering inspection workflow.",
        },
    ]
    screened = screen_papers(papers, RULES)
    assert screened[0]["relevance_score"] > screened[1]["relevance_score"]
    assert screened[0]["screening_decision"] == "CORE"


def test_decision_labels_are_valid():
    papers = [
        {"title": "Aluminium alloy", "abstract": ""},
        {"title": "Unrelated topic", "abstract": ""},
        {"title": "Heat treatment machine learning", "abstract": ""},
    ]
    screened = screen_papers(papers, RULES)
    assert {paper["screening_decision"] for paper in screened}.issubset(VALID_DECISIONS)
