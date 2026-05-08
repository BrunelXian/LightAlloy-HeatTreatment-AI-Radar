from pathlib import Path

from utils import contains_keyword, load_json, load_yaml, save_json


ROOT = Path(__file__).resolve().parents[1]
VALID_DECISIONS = {"CORE", "CURATED", "MAYBE", "REJECT"}


def score_paper(paper, rules):
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
    score = 0
    matched_positive = []
    matched_negative = []

    for keyword, weight in rules.get("positive_keywords", {}).items():
        if contains_keyword(text, keyword):
            score += int(weight)
            matched_positive.append(keyword)

    for keyword, weight in rules.get("negative_keywords", {}).items():
        if contains_keyword(text, keyword):
            score += int(weight)
            matched_negative.append(keyword)

    return score, matched_positive, matched_negative


def decision_from_score(score, thresholds):
    if score >= int(thresholds.get("core", 12)):
        return "CORE"
    if score >= int(thresholds.get("curated", 8)):
        return "CURATED"
    if score >= int(thresholds.get("maybe", 5)):
        return "MAYBE"
    return "REJECT"


def screening_reason(positive, negative):
    parts = []
    if positive:
        parts.append("positive: " + ", ".join(positive))
    if negative:
        parts.append("negative: " + ", ".join(negative))
    return "; ".join(parts) if parts else "no screening keywords matched"


def query_source_quality(paper, score, thresholds):
    maybe_threshold = int(thresholds.get("maybe", 5))
    if paper.get("query_mode") == "arxiv_advanced" and score >= maybe_threshold:
        return "high"
    if paper.get("query_mode") == "plain" and score < maybe_threshold:
        return "low"
    return "medium"


def screen_papers(papers, rules):
    thresholds = rules.get("decision_thresholds", {})
    screened = []
    for paper in papers:
        paper = dict(paper)
        score, positive, negative = score_paper(paper, rules)
        paper["relevance_score"] = score
        paper["screening_decision"] = decision_from_score(score, thresholds)
        paper["screening_reason"] = screening_reason(positive, negative)
        paper["matched_positive_keywords"] = positive
        paper["matched_negative_keywords"] = negative
        paper["query_source_quality"] = query_source_quality(paper, score, thresholds)
        screened.append(paper)
    return screened


def run():
    papers = load_json(ROOT / "data" / "processed" / "normalized_papers.json", [])
    rules = load_yaml(ROOT / "config" / "screening_rules.yaml")
    screened = screen_papers(papers, rules)
    save_json(ROOT / "data" / "processed" / "screened_papers.json", screened)
    counts = {label: 0 for label in sorted(VALID_DECISIONS)}
    for paper in screened:
        counts[paper["screening_decision"]] += 1
    print(f"Screened papers: {len(screened)}")
    print("Decision counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return screened


if __name__ == "__main__":
    run()
