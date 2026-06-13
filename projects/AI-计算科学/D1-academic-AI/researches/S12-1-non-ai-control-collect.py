#!/usr/bin/env python3
"""
S12-1 Non-AI Control Group Data Collection

Collects arXiv papers for 5 non-AI control categories and performs
the same co-discovery cluster analysis (CV of discovery intervals)
used for the CoT study.

Control categories:
1. math.DS   - Dynamical Systems (all+dynamics+AND+all+stable)
2. math.CO   - Combinatorics (all+combinatorics+AND+all+proof)
3. physics.flu-dyn - Fluid Dynamics (all+turbulence+OR+all+Navier-Stokes)
4. math.AG   - Algebraic Geometry (all+moduli+AND+all+space)
5. math.GT   - Geometric Topology (all+knot+AND+all+invariant)

Rate-limited: 3 queries per 3 seconds per arXiv API policy.
"""

import urllib.request
import xml.etree.ElementTree as ET
import time
import json
import re
import sys
from datetime import datetime
from collections import defaultdict
import math

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom", "opensearch": "http://a9.com/-/spec/opensearch/1.1/"}

CONTROL_GROUPS = {
    "math.DS": {
        "name": "Dynamical Systems",
        "query": "all%3Adynamics+AND+all%3Astable",
    },
    "math.CO": {
        "name": "Combinatorics",
        "query": "all%3Acombinatorics+AND+all%3Aproof",
    },
    "physics.flu-dyn": {
        "name": "Fluid Dynamics",
        "query": "all%3Aturbulence+OR+all%3ANavier-Stokes",
    },
    "math.AG": {
        "name": "Algebraic Geometry",
        "query": "all%3Amoduli+AND+all%3Aspace",
    },
    "math.GT": {
        "name": "Geometric Topology",
        "query": "all%3Aknot+AND+all%3Ainvariant",
    },
}

MAX_RESULTS = 2000  # max per query (arXiv API limit)
OUTPUT_FILE = "researches/S12-1-non-ai-control-results.json"


def fetch_arxiv(category, query, max_results=MAX_RESULTS, start=0):
    """Fetch arXiv papers matching query, rate-limited."""
    url = (
        f"https://export.arxiv.org/api/query?"
        f"search_query={query}&"
        f"start={start}&"
        f"max_results={max_results}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"  Error fetching {query} at start={start}: {e}", file=sys.stderr)
        return None


def parse_entries(xml_text):
    """Parse arXiv Atom feed entries."""
    if xml_text is None:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    entries = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title_elem = entry.find("atom:title", ATOM_NS)
        published_elem = entry.find("atom:published", ATOM_NS)
        updated_elem = entry.find("atom:updated", ATOM_NS)
        arxiv_id = entry.find("atom:id", ATOM_NS)

        if title_elem is None or published_elem is None:
            continue

        published_str = published_elem.text
        try:
            pub_date = datetime.strptime(published_str[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue

        title = title_elem.text.replace("\n", " ").strip()
        arxiv_id_str = arxiv_id.text if arxiv_id is not None else ""

        entries.append({
            "title": title,
            "published": published_str,
            "date": pub_date,
            "arxiv_id": arxiv_id_str,
        })
    return entries


def total_count_from_api(xml_text):
    """Get total number of results from arXiv API."""
    if xml_text is None:
        return 0
    try:
        root = ET.fromstring(xml_text)
        op_elem = root.find("opensearch:totalResults", ATOM_NS)
        return int(op_elem.text) if op_elem is not None else 0
    except (ET.ParseError, ValueError):
        return 0


def compute_cv(date_list, window_days=365):
    """
    Compute coefficient of variation of discovery intervals.

    Groups papers into windows of `window_days` days and counts discoveries per window.
    CV = std(counts) / mean(counts). CV >> 1 indicates bursty discovery (simultaneous discoveries).
    """
    if len(date_list) < 3:
        return None, 0, 0

    dates = sorted(date_list)
    t_min = dates[0]
    t_max = dates[-1]
    total_days = (t_max - t_min).total_seconds() / 86400
    if total_days <= 0:
        return None, 0, 0

    num_windows = max(1, int(total_days / window_days))
    bin_size = total_days / num_windows

    counts = defaultdict(int)
    for d in dates:
        idx = min(int((d - t_min).total_seconds() / 86400 / bin_size), num_windows - 1)
        counts[idx] += 1

    # Include zero bins
    all_counts = [counts.get(i, 0) for i in range(num_windows)]

    n = len(all_counts)
    mean_c = sum(all_counts) / n
    if mean_c == 0:
        return None, 0, 0

    var_c = sum((c - mean_c) ** 2 for c in all_counts) / n
    std_c = math.sqrt(var_c)
    cv = std_c / mean_c if mean_c > 0 else 0

    return cv, mean_c, n


def run_cluster_analysis(dates, year_range=(2010, 2025)):
    """
    Full cluster analysis as in the S12-1 paper.

    Uses tau=14 days clustering threshold to find co-discovery clusters.
    Reports:
    - CV of discoveries per year
    - Number of single-discovery clusters
    - Cluster quality (fraction of papers in clusters)
    """
    # Filter by year range
    dates_filtered = [d for d in dates if year_range[0] <= d.year <= year_range[1]]

    if len(dates_filtered) < 3:
        return {"error": "too few papers", "paper_count": len(dates_filtered)}

    # Compute CV
    cv, mean_c, num_windows = compute_cv(dates_filtered)

    # Cluster analysis with tau=14 days
    dates_sorted = sorted(dates_filtered)
    clusters = []
    current_cluster = [dates_sorted[0]]

    for i in range(1, len(dates_sorted)):
        gap = (dates_sorted[i] - dates_sorted[i - 1]).total_seconds() / 86400
        if gap <= 14:  # tau = 14 days
            current_cluster.append(dates_sorted[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [dates_sorted[i]]
    clusters.append(current_cluster)

    # Single-discovery clusters (singletons)
    singletons = sum(1 for c in clusters if len(c) == 1)
    multi_clusters = sum(1 for c in clusters if len(c) > 1)

    papers_in_clusters = sum(len(c) for c in clusters if len(c) > 1)
    total_papers = len(dates_sorted)
    cluster_quality = papers_in_clusters / total_papers if total_papers > 0 else 0

    # Compute acceleration: papers/year in last 5 years vs previous 5 years
    recent = [d for d in dates_sorted if d.year >= 2020]
    older = [d for d in dates_sorted if 2015 <= d.year < 2020]

    recent_rate = len(recent) / 5.0 if recent else 0
    older_rate = len(older) / 5.0 if older else 0
    acceleration = recent_rate / older_rate if older_rate > 0 else float("inf")

    return {
        "paper_count": total_papers,
        "years_covered": f"{dates_sorted[0].year}-{dates_sorted[-1].year}",
        "cv": round(cv, 4) if cv is not None else None,
        "mean_papers_per_window": round(mean_c, 4),
        "num_windows": num_windows,
        "single_clusters": singletons,
        "multi_clusters": multi_clusters,
        "cluster_quality": round(cluster_quality, 4),
        "papers_in_clusters": papers_in_clusters,
        "acceleration_5y": round(acceleration, 4),
        "recent_papers_2020_2024": len(recent),
        "older_papers_2015_2019": len(older),
    }


def main():
    print("=" * 60)
    print("S12-1 Non-AI Control Group Data Collection")
    print("=" * 60)

    results = {}

    for category, info in CONTROL_GROUPS.items():
        print(f"\nProcessing {category}: {info['name']}")
        print(f"  Query: {info['query']}")

        all_entries = []
        start = 0

        # Fetch papers in batches of 2000 (arXiv limit)
        while True:
            xml_text = fetch_arxiv(category, info["query"], start=start)
            if xml_text is None:
                break

            if start == 0:
                total = total_count_from_api(xml_text)
                print(f"  Total results: {total}")
                if total == 0:
                    print(f"  No results. Skipping.")
                    break

            entries = parse_entries(xml_text)
            if not entries:
                print(f"  No entries parsed. Stopping.")
                break

            print(f"  Fetched {len(entries)} entries (start={start})")
            all_entries.extend(entries)

            if len(all_entries) >= min(total, MAX_RESULTS):
                break

            start += len(entries)
            if start >= total:
                break

            # Rate limiting: 3 queries per 3 seconds
            time.sleep(3.5)

        if not all_entries:
            results[category] = {"error": "no data"}
            continue

        # Extract dates
        dates = [e["date"] for e in all_entries]

        # Run cluster analysis
        analysis = run_cluster_analysis(dates)
        analysis["category"] = category
        analysis["field_name"] = info["name"]
        analysis["query"] = info["query"]
        analysis["raw_papers_fetched"] = len(all_entries)

        results[category] = analysis
        print(f"  CV = {analysis.get('cv', 'N/A')}")
        print(f"  Papers in clusters = {analysis.get('papers_in_clusters', 0)}/{analysis.get('paper_count', 0)}")
        print(f"  Acceleration (2020-2024 vs 2015-2019) = {analysis.get('acceleration_5y', 'N/A')}x")

        # Save after each category
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"  Saved to {OUTPUT_FILE}")

        # Rate limit between categories
        time.sleep(4)

    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Category':<25} {'Papers':<10} {'CV':<10} {'Cluster%':<12} {'Acceleration'}")
    print("-" * 70)

    co_t_cv = 8.87  # from the S12-1 paper
    co_t_acc = 125  # from the S12-1 paper (updated to 16x in later iterations)

    for cat, r in results.items():
        cv = r.get("cv", "N/A")
        pq = r.get("papers_in_clusters", 0)
        pc = r.get("paper_count", 0)
        clust_pct = f"{100*pq/pc:.1f}%" if pc > 0 else "N/A"
        acc = r.get("acceleration_5y", "N/A")
        print(f"{cat:<25} {pc:<10} {str(cv):<10} {clust_pct:<12} {acc}")

    print(f"\n{'CoT (paper)':<25} {'N/A':<10} {co_t_cv:<10} {'97.6%':<12} 16x (daily rate)")
    print(f"\nCoT CV = {co_t_cv} >> 1 (bursty discovery)")
    print("Control CV should be much lower if CoT burstiness is AI-specific.")

    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
