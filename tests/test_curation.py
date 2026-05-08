import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from curation_apply import apply_curation


def _write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _paths(tmp_path):
    screened_path = tmp_path / "screened_papers.json"
    curated_path = tmp_path / "curated_papers.json"
    rejected_path = tmp_path / "rejected_papers.json"
    _write_json(
        screened_path,
        [
            {
                "paper_id": "paper-1",
                "title": "Machine learning for aluminium alloy ageing",
                "authors": ["A. Researcher"],
                "year": 2026,
                "url": "https://example.test/paper-1",
                "abstract": "A test paper.",
                "screening_decision": "CORE",
                "relevance_score": 15,
                "screening_reason": "positive: aluminium, alloy, ageing, machine learning",
                "alloy_system": ["Aluminium alloy"],
                "heat_treatment_process": ["Artificial ageing"],
                "property_target": ["Hardness"],
                "ml_method": ["Neural network"],
                "research_position": ["Property prediction"],
                "manual_status": "unreviewed",
                "manual_notes": "",
            }
        ],
    )
    _write_json(curated_path, [])
    _write_json(rejected_path, [])
    return screened_path, curated_path, rejected_path


def test_applying_curated_status_adds_one_record(tmp_path):
    screened_path, curated_path, rejected_path = _paths(tmp_path)

    record, curated, rejected = apply_curation(
        "paper-1",
        "curated",
        notes="good candidate",
        screened_path=screened_path,
        curated_path=curated_path,
        rejected_path=rejected_path,
        curation_date="2026-05-08",
    )

    assert record["manual_status"] == "curated"
    assert len(curated) == 1
    assert len(rejected) == 0
    assert _read_json(curated_path)[0]["paper_id"] == "paper-1"


def test_applying_rejected_status_adds_one_record(tmp_path):
    screened_path, curated_path, rejected_path = _paths(tmp_path)

    record, curated, rejected = apply_curation(
        "paper-1",
        "rejected",
        notes="not heat treatment",
        screened_path=screened_path,
        curated_path=curated_path,
        rejected_path=rejected_path,
        curation_date="2026-05-08",
    )

    assert record["manual_status"] == "rejected"
    assert len(curated) == 0
    assert len(rejected) == 1
    assert _read_json(rejected_path)[0]["paper_id"] == "paper-1"


def test_reapplying_same_paper_does_not_create_duplicates(tmp_path):
    screened_path, curated_path, rejected_path = _paths(tmp_path)

    for notes in ["first note", "updated note"]:
        apply_curation(
            "paper-1",
            "curated",
            notes=notes,
            screened_path=screened_path,
            curated_path=curated_path,
            rejected_path=rejected_path,
            curation_date="2026-05-08",
        )

    curated = _read_json(curated_path)
    assert len(curated) == 1
    assert curated[0]["manual_notes"] == "updated note"


def test_moving_from_rejected_to_curated_removes_from_rejected(tmp_path):
    screened_path, curated_path, rejected_path = _paths(tmp_path)

    apply_curation(
        "paper-1",
        "rejected",
        notes="initial reject",
        screened_path=screened_path,
        curated_path=curated_path,
        rejected_path=rejected_path,
        curation_date="2026-05-08",
    )
    apply_curation(
        "paper-1",
        "curated",
        notes="manual correction",
        screened_path=screened_path,
        curated_path=curated_path,
        rejected_path=rejected_path,
        curation_date="2026-05-08",
    )

    curated = _read_json(curated_path)
    rejected = _read_json(rejected_path)
    assert len(curated) == 1
    assert len(rejected) == 0
    assert curated[0]["manual_status"] == "curated"


def test_manual_status_and_notes_are_set_correctly(tmp_path):
    screened_path, curated_path, rejected_path = _paths(tmp_path)

    record, _, _ = apply_curation(
        "paper-1",
        "core",
        notes="must read",
        screened_path=screened_path,
        curated_path=curated_path,
        rejected_path=rejected_path,
        curation_date="2026-05-08",
    )

    assert record["manual_status"] == "core"
    assert record["manual_notes"] == "must read"
    assert record["curation_date"] == "2026-05-08"
