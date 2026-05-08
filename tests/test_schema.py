import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from paper_normalizer import SCHEMA_DEFAULTS, normalize_paper
from utils import stable_paper_id


def test_normalized_paper_contains_all_schema_keys():
    raw = {
        "title": "Machine learning for aluminium alloy heat treatment",
        "authors": ["A. Researcher"],
        "year": 2026,
        "abstract": "A test abstract.",
    }
    normalized = normalize_paper(raw)
    assert set(SCHEMA_DEFAULTS).issubset(normalized.keys())
    assert normalized["paper_id"]


def test_stable_paper_id_is_deterministic():
    first = stable_paper_id("A title", year=2024, doi="10.1000/example")
    second = stable_paper_id("A title", year=2024, doi="10.1000/example")
    assert first == second
