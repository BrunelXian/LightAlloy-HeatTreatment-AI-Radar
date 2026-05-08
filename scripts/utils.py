import hashlib
import json
import re
from pathlib import Path

import yaml


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_yaml(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def normalize_text(text):
    if text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\-.]", "", text)
    return text.strip()


def contains_keyword(text, keyword):
    normalized_text = normalize_text(text)
    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False
    pattern = r"(?<!\w)" + re.escape(normalized_keyword) + r"(?!\w)"
    return re.search(pattern, normalized_text) is not None


def stable_paper_id(title, year=None, doi=None, arxiv_id=None):
    if doi:
        key = f"doi:{normalize_text(doi)}"
    elif arxiv_id:
        key = f"arxiv:{normalize_text(arxiv_id)}"
    else:
        key = f"title:{normalize_text(title)}:{year or ''}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def paper_dedupe_key(paper):
    doi = normalize_text(paper.get("doi"))
    title = normalize_text(paper.get("title"))
    if doi:
        return f"doi:{doi}"
    if title:
        return f"title:{title}"
    arxiv_id = normalize_text(paper.get("arxiv_id"))
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return ""


def deduplicate_papers(papers):
    deduped = []
    seen = set()
    for paper in papers:
        key = paper_dedupe_key(paper)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(paper)
    return deduped
