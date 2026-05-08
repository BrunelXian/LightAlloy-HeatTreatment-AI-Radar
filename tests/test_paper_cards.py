import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_paper_cards import generate_paper_cards


def _paper(paper_id, title, status, score, year):
    return {
        "paper_id": paper_id,
        "title": title,
        "authors": ["Ada Lovelace", "Grace Hopper"],
        "year": year,
        "venue": "Journal of Heat Treatment AI",
        "doi": f"10.1234/{paper_id}",
        "url": f"https://example.test/{paper_id}",
        "source": "arXiv",
        "manual_status": status,
        "manual_notes": f"manual note for {paper_id}",
        "screening_decision": "CORE" if status == "core" else "CURATED",
        "relevance_score": score,
        "screening_reason": "positive: aluminium, heat treatment, machine learning",
        "alloy_system": ["Aluminium alloy"],
        "heat_treatment_process": ["Artificial ageing"],
        "property_target": ["Hardness"],
        "ml_method": ["Neural network"],
        "research_position": ["Property prediction"],
        "abstract": "A curated abstract.",
    }


def test_paper_card_generated_for_one_curated_record(tmp_path):
    curated_path = tmp_path / "curated_papers.json"
    review_dir = tmp_path / "review"
    records = [_paper("paper-1", "Heat treatment ML paper", "curated", 10, 2026)]
    curated_path.write_text(json.dumps(records), encoding="utf-8")

    _, paper_cards_dir, _ = generate_paper_cards(curated_path=curated_path, review_dir=review_dir)

    card_path = paper_cards_dir / "paper-1.md"
    assert card_path.exists()
    assert "Heat treatment ML paper" in card_path.read_text(encoding="utf-8")


def test_core_papers_appear_before_curated_papers_in_queue(tmp_path):
    curated_path = tmp_path / "curated_papers.json"
    review_dir = tmp_path / "review"
    records = [
        _paper("curated-1", "Curated paper", "curated", 99, 2026),
        _paper("core-1", "Core paper", "core", 1, 2020),
    ]
    curated_path.write_text(json.dumps(records), encoding="utf-8")

    queue_path, _, _ = generate_paper_cards(curated_path=curated_path, review_dir=review_dir)
    queue = queue_path.read_text(encoding="utf-8")

    assert queue.index("Core paper") < queue.index("Curated paper")


def test_generated_markdown_includes_metadata_notes_and_tags(tmp_path):
    curated_path = tmp_path / "curated_papers.json"
    review_dir = tmp_path / "review"
    records = [_paper("paper-2", "Tagged paper", "core", 12, 2025)]
    curated_path.write_text(json.dumps(records), encoding="utf-8")

    _, paper_cards_dir, _ = generate_paper_cards(curated_path=curated_path, review_dir=review_dir)
    card = (paper_cards_dir / "paper-2.md").read_text(encoding="utf-8")

    assert "Tagged paper" in card
    assert "10.1234/paper-2" in card
    assert "manual note for paper-2" in card
    assert "alloy_system: Aluminium alloy" in card
    assert "heat_treatment_process: Artificial ageing" in card
    assert "ml_method: Neural network" in card
