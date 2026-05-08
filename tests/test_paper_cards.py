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
    card = card_path.read_text(encoding="utf-8")
    assert "Heat treatment ML paper" in card
    assert "## Human Reading Notes" in card
    assert "### Key contribution" in card
    assert "<!-- Fill manually -->" in card


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


def test_existing_human_reading_notes_are_preserved_after_regeneration(tmp_path):
    curated_path = tmp_path / "curated_papers.json"
    review_dir = tmp_path / "review"
    records = [_paper("paper-3", "Original title", "core", 12, 2025)]
    curated_path.write_text(json.dumps(records), encoding="utf-8")
    _, paper_cards_dir, _ = generate_paper_cards(curated_path=curated_path, review_dir=review_dir)

    card_path = paper_cards_dir / "paper-3.md"
    card = card_path.read_text(encoding="utf-8")
    custom_notes = """## Human Reading Notes

### Key contribution
Manual synthesis already written.

### Method / model
Manual method note.
"""
    card_path.write_text(card.split("## Human Reading Notes", 1)[0] + custom_notes, encoding="utf-8")

    updated = [_paper("paper-3", "Updated deterministic title", "core", 15, 2026)]
    curated_path.write_text(json.dumps(updated), encoding="utf-8")
    generate_paper_cards(curated_path=curated_path, review_dir=review_dir)
    regenerated = card_path.read_text(encoding="utf-8")

    assert "Updated deterministic title" in regenerated
    assert "Relevance score: 15" in regenerated
    assert "Manual synthesis already written." in regenerated
    assert "Manual method note." in regenerated


def test_core_reading_queue_generation_still_works(tmp_path):
    curated_path = tmp_path / "curated_papers.json"
    review_dir = tmp_path / "review"
    records = [
        _paper("paper-4", "Queue core", "core", 11, 2024),
        _paper("paper-5", "Queue curated", "curated", 10, 2025),
    ]
    curated_path.write_text(json.dumps(records), encoding="utf-8")

    queue_path, _, queue = generate_paper_cards(curated_path=curated_path, review_dir=review_dir)

    assert queue_path.exists()
    assert len(queue) == 2
    queue_text = queue_path.read_text(encoding="utf-8")
    assert "Queue core" in queue_text
    assert "Queue curated" in queue_text
