import argparse
import re
import time
from pathlib import Path

import requests

from utils import deduplicate_papers, ensure_dir, load_json, load_yaml, paper_dedupe_key, save_json


ROOT = Path(__file__).resolve().parents[1]
CROSSREF_WORKS_URL = "https://api.crossref.org/works"


def _first(value, default=""):
    if isinstance(value, list) and value:
        return value[0]
    return value if value is not None else default


def _date_from_parts(value):
    parts = value.get("date-parts", []) if isinstance(value, dict) else []
    if not parts or not parts[0]:
        return "", None
    date_parts = parts[0]
    year = date_parts[0] if len(date_parts) > 0 else None
    month = date_parts[1] if len(date_parts) > 1 else 1
    day = date_parts[2] if len(date_parts) > 2 else 1
    return f"{year:04d}-{month:02d}-{day:02d}" if year else "", year


def _best_date(item):
    for key in ["published-print", "published-online", "published", "issued", "created"]:
        date_text, year = _date_from_parts(item.get(key, {}))
        if date_text or year:
            return date_text, year
    return "", None


def _authors(item):
    authors = []
    for author in item.get("author", []) or []:
        given = author.get("given", "")
        family = author.get("family", "")
        name = " ".join(part for part in [given, family] if part).strip()
        if name:
            authors.append(name)
    return authors


def _clean_abstract(abstract):
    if not abstract:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(abstract))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def crossref_item_to_paper(item, query_group, query):
    published_date, year = _best_date(item)
    doi = item.get("DOI", "") or ""
    url = item.get("URL", "") or (f"https://doi.org/{doi}" if doi else "")
    return {
        "title": _first(item.get("title", []), ""),
        "authors": _authors(item),
        "year": year,
        "venue": _first(item.get("container-title", []), ""),
        "doi": doi,
        "arxiv_id": "",
        "url": url,
        "abstract": _clean_abstract(item.get("abstract", "")),
        "source": "Crossref",
        "published_date": published_date,
        "updated_date": item.get("indexed", {}).get("date-time", ""),
        "query_group": query_group,
        "query": query,
        "query_mode": "crossref_query",
    }


def iter_crossref_queries(query_config):
    for query_group, queries in query_config.items():
        if query_group == "arxiv_advanced":
            continue
        for query in queries:
            yield query_group, query


def fetch_query(query, rows, mailto=""):
    params = {
        "query.bibliographic": query,
        "rows": rows,
        "sort": "published",
        "order": "desc",
    }
    if mailto:
        params["mailto"] = mailto
    try:
        response = requests.get(CROSSREF_WORKS_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"WARNING: Crossref query skipped after {exc.__class__.__name__}: {query[:120]}")
        return []
    return response.json().get("message", {}).get("items", [])


def source_settings():
    config = load_yaml(ROOT / "config" / "source_config.yaml")
    return config.get("sources", {}).get("crossref", {})


def run(rows=20, delay_seconds=1.0, enabled=None, mailto=None):
    settings = source_settings()
    if enabled is None:
        enabled = bool(settings.get("enabled", True))
    if not enabled:
        print("Crossref source disabled.")
        return load_json(ROOT / "data" / "raw" / "raw_papers.json", [])

    rows = int(settings.get("rows_per_query", rows))
    delay_seconds = float(settings.get("delay_seconds", delay_seconds))
    mailto = settings.get("mailto", mailto or "")

    query_config = load_yaml(ROOT / "config" / "search_queries.yaml")
    raw_path = ROOT / "data" / "raw" / "raw_papers.json"
    seen_path = ROOT / "data" / "checkpoints" / "seen_papers.json"

    ensure_dir(raw_path.parent)
    ensure_dir(seen_path.parent)

    existing = load_json(raw_path, [])
    seen = {paper_dedupe_key(paper) for paper in existing if paper_dedupe_key(paper)}
    seen.update(load_json(seen_path, []))

    fetched_count = 0
    new_records = []

    for query_group, query in iter_crossref_queries(query_config):
        items = fetch_query(query, rows=rows, mailto=mailto)
        fetched_count += len(items)
        for item in items:
            paper = crossref_item_to_paper(item, query_group=query_group, query=query)
            key = paper_dedupe_key(paper)
            if key and key not in seen:
                seen.add(key)
                new_records.append(paper)
        time.sleep(delay_seconds)

    combined = deduplicate_papers(existing + new_records)
    save_json(raw_path, combined)
    save_json(seen_path, sorted(seen))

    print(f"Crossref fetched records: {fetched_count}")
    print(f"Crossref new records: {len(new_records)}")
    print(f"Total raw saved: {len(combined)}")
    return combined


def main():
    parser = argparse.ArgumentParser(description="Search Crossref and append raw paper metadata.")
    parser.add_argument("--rows", type=int, default=20)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--disable", action="store_true")
    args = parser.parse_args()
    run(rows=args.rows, delay_seconds=args.delay_seconds, enabled=not args.disable)


if __name__ == "__main__":
    main()
