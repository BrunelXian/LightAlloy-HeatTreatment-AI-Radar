from pathlib import Path

from utils import contains_keyword, load_json, load_yaml, save_json


ROOT = Path(__file__).resolve().parents[1]
FIELD_MAP = {
    "material": "alloy_system",
    "process": "heat_treatment_process",
    "property": "property_target",
    "ml_method": "ml_method",
    "research_position": "research_position",
}


def match_tags(text, rules):
    matched = []
    for tag, keywords in rules.items():
        for keyword in keywords:
            if contains_keyword(text, keyword):
                matched.append(tag)
                break
    return matched


def assign_tags(papers, tag_rules):
    tagged = []
    for paper in papers:
        paper = dict(paper)
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        for rule_group, field in FIELD_MAP.items():
            paper[field] = match_tags(text, tag_rules.get(rule_group, {}))
        tagged.append(paper)
    return tagged


def run():
    screened_path = ROOT / "data" / "processed" / "screened_papers.json"
    curated_path = ROOT / "data" / "curated" / "curated_papers.json"
    papers = load_json(screened_path, [])
    tag_rules = load_yaml(ROOT / "config" / "tag_rules.yaml")

    existing_curated = load_json(curated_path, [])
    manual_by_id = {
        paper.get("paper_id"): {
            "manual_status": paper.get("manual_status", "unreviewed"),
            "manual_notes": paper.get("manual_notes", ""),
        }
        for paper in existing_curated
        if paper.get("paper_id")
    }

    tagged = assign_tags(papers, tag_rules)
    for paper in tagged:
        manual = manual_by_id.get(paper.get("paper_id"))
        if manual:
            paper["manual_status"] = manual["manual_status"]
            paper["manual_notes"] = manual["manual_notes"]

    save_json(screened_path, tagged)
    if not curated_path.exists():
        save_json(curated_path, [])

    print(f"Tagged papers: {len(tagged)}")
    print(f"Curated file initialized: {curated_path.exists()}")
    return tagged


if __name__ == "__main__":
    run()
