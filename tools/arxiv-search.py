#!/usr/bin/env python3
"""
arXiv automated search tool for Ralph Loop information gathering.
Searches arXiv API, extracts metadata, and classifies relevance via LLM.

Usage:
    python arxiv-search.py search "<keywords>" [--top N]
    python arxiv-search.py rss "<keywords>" [--monitor]
    python arxiv-search.py classify <results.json>
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from xml.etree import ElementTree

# arXiv API endpoint
ARXIV_API = "http://api.arxiv.org/v2/"
ATOM_NS = "http://www.w3.org/2005/Atom"
RELEVANCE_THRESHOLDS = {
    "must-read": 0.85,
    "recommended": 0.65,
    "reference": 0.40,
}

# Default search keywords for gravitational wave / optical lattice clock research
DEFAULT_KEYWORDS = [
    "optical lattice clock gravitational wave",
    "OLC GW detection",
    "space clock network gravitational waves",
    "atomic clock general relativity",
    "stellar interferometry gravitational waves",
]


def search_arxiv(query, max_results=20):
    """Search arXiv API and return results as list of dicts."""
    encoded_query = urllib.parse.quote(f'"{query}"') if ' ' in query else urllib.parse.quote(query)
    url = f"{ARXIV_API}search/?query={encoded_query}&max_results={max_results}&sortBy=submittedDate"

    req = urllib.request.Request(url, headers={"User-Agent": "RalphLoop/1.0 (research; contact: team@ralphloop.org)"})
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            xml_data = resp.read().decode("utf-8")
            break
        except urllib.error.HTTPError as e:
            if e.code == 502 and attempt < 2:
                time.sleep(3 * (attempt + 1))
                print(f"  arXiv API 502, retry {attempt+1}/3...", file=sys.stderr)
                continue
            raise

    root = ElementTree.fromstring(xml_data)
    entries_ns = {"atom": ATOM_NS, "arxiv": "http://arxiv.org/schemas/atom"}

    results = []
    for entry in root.findall(f"atom:entry", entries_ns):
        title = entry.find("atom:title", entries_ns).text.strip()
        summary = entry.find("atom:summary", entries_ns).text.strip()
        authors = [a.find("atom:name", entries_ns).text for a in entry.findall("atom:author", entries_ns)]

        published = entry.find("atom:published", entries_ns).text
        updated = entry.find("atom:updated", entries_ns).text

        arxiv_id = entry.find("atom:id", entries_ns).text
        pdf_url = None
        for link in entry.findall("atom:link", entries_ns):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
                break

        # arXiv categories
        categories = [c.get("term") for c in entry.findall("arxiv:primary_category", entries_ns)]
        for cat in entry.findall("atom:category", entries_ns):
            if "term" in cat.get("term", ""):
                if cat.get("term") not in categories:
                    categories.append(cat.get("term"))

        results.append({
            "title": title.replace("\n", " "),
            "summary": summary.replace("\n", " "),
            "authors": authors,
            "published": published,
            "updated": updated,
            "arxiv_id": arxiv_id.split("v/")[-1] if "v/" in arxiv_id else arxiv_id,
            "pdf_url": pdf_url,
            "categories": categories,
            "source": "arxiv",
        })

    return results


def classify_relevance(papers, query, llm_api_key=None):
    """
    Classify papers by relevance to the query.
    Uses LLM if API key provided, otherwise heuristic classification.
    """
    if llm_api_key:
        return classify_with_llm(papers, query, llm_api_key)
    else:
        return classify_heuristic(papers, query)


def classify_heuristic(papers, query):
    """Heuristic classification based on keyword matching in title/summary."""
    keywords = query.lower().split()
    classified = []

    for paper in papers:
        text = (paper["title"] + " " + paper["summary"]).lower()
        matches = sum(1 for kw in keywords if kw in text)
        score = matches / max(len(keywords), 1)

        if score >= RELEVANCE_THRESHOLDS["must-read"]:
            level = "must-read"
        elif score >= RELEVANCE_THRESHOLDS["recommended"]:
            level = "recommended"
        elif score >= RELEVANCE_THRESHOLDS["reference"]:
            level = "reference"
        else:
            level = "skip"

        classified.append({**paper, "relevance_score": round(score, 3), "relevance_level": level})

    return classified


def classify_with_llm(papers, query, api_key):
    """
    LLM-based relevance classification.
    Sends paper summaries to Claude for relevance judgment.
    """
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        messages = []
        for i, paper in enumerate(papers[:30]):  # Claude limit
            messages.append(f"\n--- Paper {i+1} ---\nTitle: {paper['title']}\nSummary: {paper['summary']}\nCategories: {', '.join(paper['categories'])}")

        prompt = f"""Relevance scoring for arXiv papers related to: {query}

For each paper, score relevance from 0.0 to 1.0:
- must-read (>={RELEVANCE_THRESHOLDS['must-read']}): directly related to the research question
- recommended (>={RELEVANCE_THRESHOLDS['recommended']}): tangentially related, useful background
- reference (>={RELEVANCE_THRESHOLDS['reference']}): methodology or citation of interest
- skip (<{RELEVANCE_THRESHOLDS['reference']}): not relevant

Return JSON array with: id (0-indexed), score (float), level (must-read/recommended/reference/skip)

Papers:
{chr(10).join(messages)}"""

        response = client.messages.create(
            model="claude-sonnet-4-5-20260401",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response (expecting JSON)
        content = response.content.text
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            classifications = json.loads(content[start:end])
            return classifications
        return []

    except ImportError:
        print("Warning: anthropic package not installed, falling back to heuristic classification", file=sys.stderr)
        return classify_heuristic(papers, query)
    except Exception as e:
        print(f"Warning: LLM classification failed ({e}), falling back to heuristic", file=sys.stderr)
        return classify_heuristic(papers, query)


def search_and_save(keywords, top=20, output_dir="note"):
    """Search arXiv for all keywords and save results."""
    all_results = []
    for kw in keywords:
        print(f"Searching: {kw}")
        papers = search_arxiv(kw, max_results=top)
        all_results.extend(papers)
        time.sleep(3)  # Rate limiting

    # Deduplicate by arxiv_id
    seen = set()
    unique_results = []
    for p in all_results:
        if p["arxiv_id"] not in seen:
            seen.add(p["arxiv_id"])
            unique_results.append(p)

    # Classify
    combined_query = " ".join(keywords)
    classified = classify_heuristic(unique_results, combined_query)

    # Separate by level
    must_read = [p for p in classified if p["relevance_level"] == "must-read"]
    recommended = [p for p in classified if p["relevance_level"] == "recommended"]
    reference = [p for p in classified if p["relevance_level"] == "reference"]

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"arxiv-results-{datetime.now().strftime('%Y%m%d')}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "search_date": datetime.now(timezone.utc).isoformat(),
            "query": combined_query,
            "keywords": keywords,
            "total_found": len(unique_results),
            "classified": len(classified),
            "must_read": must_read,
            "recommended": recommended,
            "reference": reference,
            "all_results": classified,
        }, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to {output_file}")
    print(f"  Must-read: {len(must_read)}")
    print(f"  Recommended: {len(recommended)}")
    print(f"  Reference: {len(reference)}")

    return output_file


def setup_rss_monitor(keywords, interval_hours=24):
    """Set up arXiv RSS monitoring for keywords."""
    rss_dir = "note/rss-monitors"
    os.makedirs(rss_dir, exist_ok=True)

    monitors = []
    for kw in keywords:
        monitor_file = os.path.join(rss_dir, f"{urllib.parse.quote(kw)}.json")
        monitor = {
            "keyword": kw,
            "rss_url": f"https://rss.arxiv.org/rss/cs.CV+gr-qc",  # Will be customized per keyword
            "interval_hours": interval_hours,
            "last_check": None,
            "new_papers": [],
        }
        with open(monitor_file, "w") as f:
            json.dump(monitor, f, indent=2)
        monitors.append(monitor_file)
        print(f"Monitor created: {monitor_file}")

    return monitors


def main():
    parser = argparse.ArgumentParser(description="arXiv search tool for Ralph Loop")
    subparsers = parser.add_subparsers(dest="command")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search arXiv")
    search_parser.add_argument("keywords", nargs="+", help="Search keywords")
    search_parser.add_argument("--top", type=int, default=20, help="Max results per keyword")
    search_parser.add_argument("--output-dir", default="note", help="Output directory")

    # RSS monitor command
    rss_parser = subparsers.add_parser("rss", help="Setup RSS monitoring")
    rss_parser.add_argument("keywords", nargs="+", help="Keywords to monitor")
    rss_parser.add_argument("--interval", type=int, default=24, help="Check interval in hours")

    # Classify command
    classify_parser = subparsers.add_parser("classify", help="Classify existing results")
    classify_parser.add_argument("input_file", help="Input JSON file from search")
    classify_parser.add_argument("--query", required=True, help="Original search query")

    args = parser.parse_args()

    if args.command == "search":
        search_and_save(args.keywords, args.top, args.output_dir)
    elif args.command == "rss":
        setup_rss_monitor(args.keywords, args.interval)
    elif args.command == "classify":
        with open(args.input_file) as f:
            data = json.load(f)
        classified = classify_heuristic(data["all_results"], args.query)
        data["classified"] = len(classified)
        with open(args.input_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Classified {len(classified)} papers")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
