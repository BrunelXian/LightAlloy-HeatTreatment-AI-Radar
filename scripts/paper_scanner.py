import argparse
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests

from utils import deduplicate_papers, ensure_dir, load_json, load_yaml, normalize_text, save_json


ROOT = Path(__file__).resolve().parents[1]
ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _text(element, path, default=""):
    found = element.find(path, ATOM_NS)
    if found is None or found.text is None:
        return default
    return re.sub(r"\s+", " ", found.text).strip()


def _year(date_text):
    if not date_text:
        return None
    try:
        return datetime.fromisoformat(date_text.replace("Z", "+00:00")).year
    except ValueError:
        match = re.search(r"\d{4}", date_text)
        return int(match.group(0)) if match else None


def _arxiv_id(entry_id):
    if not entry_id:
        return ""
    return entry_id.rstrip("/").split("/")[-1]


def _doi(entry):
    doi = _text(entry, "arxiv:doi")
    return doi


def parse_arxiv_feed(xml_text, query_group, query, query_mode):
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall("atom:entry", ATOM_NS):
        entry_id = _text(entry, "atom:id")
        published = _text(entry, "atom:published")
        updated = _text(entry, "atom:updated")
        authors = [
            _text(author, "atom:name")
            for author in entry.findall("atom:author", ATOM_NS)
            if _text(author, "atom:name")
        ]
        paper = {
            "title": _text(entry, "atom:title"),
            "authors": authors,
            "year": _year(published),
            "venue": "arXiv",
            "doi": _doi(entry),
            "arxiv_id": _arxiv_id(entry_id),
            "url": entry_id,
            "abstract": _text(entry, "atom:summary"),
            "source": "arXiv",
            "published_date": published,
            "updated_date": updated,
            "query_group": query_group,
            "query": query,
            "query_mode": query_mode,
        }
        papers.append(paper)
    return papers


def build_search_query(query, query_mode):
    if query_mode == "arxiv_advanced":
        return query
    return f'all:"{query}"'


def fetch_query(query, max_results, query_mode):
    params = {
        "search_query": build_search_query(query, query_mode),
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    response = requests.get(ARXIV_API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.text


def paper_seen_key(paper):
    doi = normalize_text(paper.get("doi"))
    arxiv_id = normalize_text(paper.get("arxiv_id"))
    title = normalize_text(paper.get("title"))
    if doi:
        return f"doi:{doi}"
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    return f"title:{title}"


def iter_queries(query_config, mode):
    if mode == "arxiv_advanced":
        for query in query_config.get("arxiv_advanced", []):
            yield "arxiv_advanced", query, "arxiv_advanced"
        return
    if mode == "plain":
        for query_group, queries in query_config.items():
            if query_group == "arxiv_advanced":
                continue
            for query in queries:
                yield query_group, query, "plain"
        return
    for query_group, queries in query_config.items():
        query_mode = "arxiv_advanced" if query_group == "arxiv_advanced" else "plain"
        for query in queries:
            yield query_group, query, query_mode


def run(max_results=20, delay_seconds=3.0, mode="arxiv_advanced"):
    query_config = load_yaml(ROOT / "config" / "search_queries.yaml")
    raw_path = ROOT / "data" / "raw" / "raw_papers.json"
    seen_path = ROOT / "data" / "checkpoints" / "seen_papers.json"

    ensure_dir(raw_path.parent)
    ensure_dir(seen_path.parent)

    existing = load_json(raw_path, [])
    seen = set(load_json(seen_path, []))
    fetched_count = 0
    new_records = []

    for query_group, query, query_mode in iter_queries(query_config, mode):
        xml_text = fetch_query(query, max_results=max_results, query_mode=query_mode)
        papers = parse_arxiv_feed(xml_text, query_group=query_group, query=query, query_mode=query_mode)
        fetched_count += len(papers)
        for paper in papers:
            key = paper_seen_key(paper)
            if key and key not in seen:
                seen.add(key)
                new_records.append(paper)
        time.sleep(delay_seconds)

    combined = deduplicate_papers(existing + new_records)
    save_json(raw_path, combined)
    save_json(seen_path, sorted(seen))

    print(f"Fetched records: {fetched_count}")
    print(f"New records: {len(new_records)}")
    print(f"Total raw saved: {len(combined)}")
    return combined


def main():
    parser = argparse.ArgumentParser(description="Search arXiv and save raw paper metadata.")
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--delay-seconds", type=float, default=3.0)
    parser.add_argument("--mode", choices=["arxiv_advanced", "plain", "all"], default="arxiv_advanced")
    args = parser.parse_args()
    run(max_results=args.max_results, delay_seconds=args.delay_seconds, mode=args.mode)


if __name__ == "__main__":
    main()
