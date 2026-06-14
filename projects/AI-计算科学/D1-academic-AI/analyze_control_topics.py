#!/usr/bin/env python3
"""S12-1 Extended: Non-AI Control Topics for Selection Bias Mitigation

Addresses sub-brain critique #1: All 5 original topics are AI/ML-adjacent.
Add 3 non-AI topics (cond-mat, astro-ph, q-bio) to test generalizability.
"""

import json
import os
import urllib.request
import urllib.parse
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "papers", "s12-1-co-discovery-phase-transition")


def fetch_arxiv_papers(query, max_results=500, max_days=7300):
    """Fetch arXiv papers via API.

    Args:
        query: arXiv search query (e.g., 'all+cosmology')
        max_results: maximum number of papers to fetch
        max_days: lookback in days (default 7300 = 20 years)

    Returns:
        list of dicts with 'id', 'published', 'title'
    """
    base_url = "http://export.arxiv.org/api/query"
    search_query = f"({query}) AND (SUB:astro-ph OR SUB:cond-mat OR SUB:q-bio OR SUB:stat.ML OR SUB:cs.LG OR SUB:cs.AI OR SUB:math-ph OR SUB:physics.data-an)"
    start_param = 0
    all_results = []

    for attempt in range(3):
        params = urllib.parse.urlencode({
            "search_query": search_query,
            "start": start_param,
            "max_results": min(200, max_results - len(all_results)),
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending",
        })

        url = f"{base_url}?{params}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read().decode("utf-8")
                import xml.etree.ElementTree as ET
                root = ET.fromstring(data)

                ns = {
                    "atom": "http://www.w3.org/2005/Atom",
                    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
                }

                total = root.find("opensearch:totalResults", ns)
                if total is not None:
                    print(f"  Total matching: {total.text}")

                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns).text.strip()
                    published = entry.find("atom:published", ns).text.strip()
                    paper_id = entry.find("atom:id", ns).text.strip()

                    all_results.append({
                        "id": paper_id,
                        "published": published,
                        "title": title,
                    })

                if len(all_results) >= max_results:
                    break
                start_param += 200

        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            import time
            time.sleep(5)
            continue

    return all_results


def compute_metrics(papers, tau=14):
    """Compute discovery dynamics metrics for a topic."""
    if not papers:
        return None

    # Sort by publication date
    papers_sorted = sorted(papers, key=lambda p: p["published"])
    n = len(papers_sorted)

    if n < 10:
        return None

    # Compute inter-publication intervals
    from datetime import datetime
    dates = []
    for p in papers_sorted:
        try:
            dt = datetime.strptime(p["published"][:10], "%Y-%m-%d")
            dates.append(dt)
        except:
            continue

    if len(dates) < 3:
        return None

    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    intervals = np.array(intervals, dtype=float)

    # CV
    cv = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0

    # Cluster detection (chain clustering)
    clusters = []
    current_cluster = [0]
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days <= tau:
            current_cluster.append(i)
        else:
            clusters.append(current_cluster)
            current_cluster = [i]
    clusters.append(current_cluster)

    # Metrics
    max_cluster = max(len(c) for c in clusters)
    f_c = sum(len(c) for c in clusters if len(c) >= 2) / n

    # Quarterly rate analysis
    year_quarters = {}
    for i, d in enumerate(dates):
        q = (d.month - 1) // 3 + 1
        y = d.year
        key = (y, q)
        if key not in year_quarters:
            year_quarters[key] = 0
        year_quarters[key] += 1

    return {
        "n_papers": n,
        "cv": float(cv),
        "max_cluster": max_cluster,
        "f_c": float(f_c),
        "n_clusters": len(clusters),
        "yearly_quarterly": year_quarters,
        "mean_interval": float(np.mean(intervals)),
        "clusters_by_size": sorted([len(c) for c in clusters if len(c) >= 2], reverse=True)[:10],
    }


def main():
    print("=" * 70)
    print("S12-1 Extended: Non-AI Control Topics")
    print("=" * 70)

    # Non-AI topics to add
    control_topics = {
        "cond-mat (condensed matter)": {"query": "all+condensed+matter", "arxiv_sub": "cond-mat", "max_results": 500},
        "astro-ph (astrophysics)": {"query": "all+galaxy", "arxiv_sub": "astro-ph", "max_results": 500},
        "q-bio (quantitative biology)": {"query": "all+genome", "arxiv_sub": "q-bio", "max_results": 300},
    }

    results = {}

    for topic_name, config in control_topics.items():
        print(f"\nFetching {topic_name}...")
        papers = fetch_arxiv_papers(config["query"], max_results=config["max_results"])
        print(f"  Fetched {len(papers)} papers")

        metrics = compute_metrics(papers)
        if metrics:
            results[topic_name] = metrics
            print(f"  CV = {metrics['cv']:.2f}, Cmax = {metrics['max_cluster']}, fC = {metrics['f_c']:.3f}")
            print(f"  Mean inter-publication interval = {metrics['mean_interval']:.1f} days")
        else:
            print(f"  Insufficient data ({len(papers)} papers)")

    # Compare with original AI topics
    print("\n" + "-" * 70)
    print("Cross-Topic Comparison (Extended)")
    print("-" * 70)

    # Original AI topics (from paper)
    original = {
        "CoT (AI)": {"cv": 8.87, "max_cluster": 358, "f_c": 0.976, "n": 500},
        "Info Geometry": {"cv": 1.72, "max_cluster": 11, "f_c": 0.700, "n": 300},
        "Phase Transition ML": {"cv": 1.51, "max_cluster": 12, "f_c": 0.663, "n": 300},
        "Emergent Ability": {"cv": 2.68, "max_cluster": 21, "f_c": 0.773, "n": 300},
        "Free Energy": {"cv": 2.31, "max_cluster": 9, "f_c": 0.607, "n": 300},
    }

    all_results = {**original, **{k: {"cv": v["cv"], "max_cluster": v["max_cluster"], "f_c": v["f_c"], "n": v["n_papers"]} for k, v in results.items()}}

    for topic, m in all_results.items():
        print(f"  {topic:<30} CV={m['cv']:6.2f}  Cmax={m['max_cluster']:4d}  fC={m['f_c']:.3f}  N={m['n']}")

    # Save full results
    full_results = {"control_topics": results, "original_ai_topics": original}
    output_path = os.path.join(OUTPUT_DIR, "s12-1_extended_results.json")
    json.dump(full_results, open(output_path, "w"), indent=2)
    print(f"\n  Results saved to: {output_path}")


if __name__ == "__main__":
    main()
