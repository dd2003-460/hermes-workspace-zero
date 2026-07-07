#!/usr/bin/env python3
"""
ADS citation graph tool for Ralph Loop.
Uses NASA ADS API to fetch citation networks.

Usage:
    python adscite-graph.py search "<query>" [--top N]
    python adscite-graph.py cites "<arxiv_id>" [--depth N]
    python adscite-graph.py citedby "<doi>" [--depth N]
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# NASA ADS API
ADS_API = "https://api.adsabs.harvard.edu/v2/search/"
# Fallback: use arXiv for papers not yet in ADS
ARXIV_API = "http://api.arxiv.org/v2/"


def ads_search(query, max_results=20):
    """Search NASA ADS API."""
    # ADS v2 API requires API key via header
    ads_key = os.environ.get("ADS_QTOKEN")
    if not ads_key:
        print("Warning: ADS_QTOKEN environment variable not set", file=sys.stderr)
        print("Falling back to arXiv search", file=sys.stderr)
        return None

    url = f"{ADS_API}query/"
    data = urllib.parse.urlencode({"q": query, "rows": max_results}).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Bearer {ads_key}")

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"ADS API error: {e}", file=sys.stderr)
        return None


def ads_get_citations(bibcode):
    """Get citations for a paper by bibcode."""
    ads_key = os.environ.get("ADS_QTOKEN")
    if not ads_key:
        return []

    url = f"{ADS_API}/bibcode/{bibcode}/citations"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ads_key}")

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("citations", [])
    except Exception as e:
        print(f"Error fetching citations: {e}", file=sys.stderr)
        return []


def ads_get_references(bibcode):
    """Get references for a paper by bibcode."""
    ads_key = os.environ.get("ADS_QTOKEN")
    if not ads_key:
        return []

    url = f"{ADS_API}/bibcode/{bibcode}/references"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ads_key}")

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("references", [])
    except Exception as e:
        print(f"Error fetching references: {e}", file=sys.stderr)
        return []


def fetch_via_arxiv(title, max_results=5):
    """Fallback: search arXiv by title."""
    title_query = urllib.parse.quote(title[:100])
    url = f"{ARXIV_API}search/?query=ti:{title_query}&max_results={max_results}"

    req = urllib.request.Request(url, headers={"User-Agent": "RalphLoop/1.0"})
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read().decode("utf-8"))


def build_citation_graph(seed_papers, max_depth=2, max_per_node=5):
    """Build a citation graph starting from seed papers."""
    graph = {"nodes": [], "edges": []}
    visited = set()
    queue = [(paper, 0) for paper in seed_papers]

    while queue and len(graph["nodes"]) < 100:
        paper, depth = queue.pop(0)

        bibcode = paper.get("bibcode")
        if not bibcode or bibcode in visited:
            continue

        visited.add(bibcode)
        graph["nodes"].append({
            "bibcode": bibcode,
            "title": paper.get("title", [""])[0] if paper.get("title") else "Unknown",
            "authors": paper.get("author", [])[:10],
            "year": paper.get("year", [None])[0] if paper.get("year") else None,
            "depth": depth,
        })

        if depth < max_depth:
            citations = ads_get_citations(bibcode)[:max_per_node]
            for cit in citations:
                cit_bibcode = cit.get("bibcode")
                if cit_bibcode and cit_bibcode not in visited:
                    graph["edges"].append({
                        "from": bibcode,
                        "to": cit_bibcode,
                        "type": "citation",
                    })
                    queue.append((cit, depth + 1))

    return graph


def save_graph(graph, output_dir="note"):
    """Save citation graph to file."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"citation-graph-{datetime.now().strftime('%Y%m%d')}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    print(f"Citation graph saved to {output_file}")
    print(f"  Nodes: {len(graph['nodes'])}")
    print(f"  Edges: {len(graph['edges'])}")

    return output_file


def main():
    parser = argparse.ArgumentParser(description="ADS citation graph tool for Ralph Loop")
    subparsers = parser.add_subparsers(dest="command")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search ADS")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--top", type=int, default=20, help="Max results")

    # Cites command
    cites_parser = subparsers.add_parser("cites", help="Get citations for a paper")
    cites_parser.add_argument("bibcode", help="Bibcode of the paper")

    # Graph command
    graph_parser = subparsers.add_parser("graph", help="Build citation graph")
    graph_parser.add_argument("seed_file", help="JSON file with seed papers")
    graph_parser.add_argument("--depth", type=int, default=2, help="Max citation depth")
    graph_parser.add_argument("--max-per-node", type=int, default=5, help="Max citations per node")

    args = parser.parse_args()

    if args.command == "search":
        results = ads_search(args.query, args.top)
        if results:
            print(json.dumps(results, indent=2))
            save_graph({"nodes": results.get("docs", []), "edges": []})
        else:
            print("ADS search failed, try setting ADS_QTOKEN")

    elif args.command == "cites":
        citations = ads_get_citations(args.bibcode)
        print(json.dumps(citations, indent=2))

    elif args.command == "graph":
        with open(args.seed_file) as f:
            seeds = json.load(f)
        graph = build_citation_graph(seeds, args.depth, args.max_per_node)
        save_graph(graph)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
