#!/usr/bin/env python3
"""
S12-1 Bootstrap Confidence Intervals for CV, f_C, and C_max.
Collects inter-event times from arXiv API, applies chain-clustering,
computes bootstrap CIs via 10,000 resamples.
With retry logic for SSL failures.
"""

import json
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime

import numpy as np

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
OPENSEARCH_NS = {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"}

# All topics with correct arXiv API query encoding
# Using space as AND (default arXiv behavior)
TOPICS = {
    "CoT (AI)": {"query": "all:chain+AND+all:thought", "max_papers": 500},
    "Emergent Ability": {"query": "all:emergent+AND+all:ability", "max_papers": 500},
    "Free Energy (brain)": {"query": "all:free+AND+all:energy+AND+all:brain", "max_papers": 500},
    "Info Geometry": {"query": "all:information+AND+all:geometry", "max_papers": 500},
    "Phase Transition ML": {"query": "all:phase+AND+all:transition+AND+all:neural", "max_papers": 500},
    "math.DS": {"query": "all:dynamics+AND+all:stable", "max_papers": 500},
    "math.CO": {"query": "all:combinatorics+AND+all:proof", "max_papers": 500},
    "physics.flu-dyn": {"query": "all:turbulence+OR+all:Navier-Stokes", "max_papers": 500},
    "math.AG": {"query": "all:moduli+AND+all:space", "max_papers": 500},
    "math.GT": {"query": "all:knot+AND+all:invariant", "max_papers": 500},
}

TAU_DAYS = 14  # chain-clustering threshold
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def fetch_arxiv(query, max_papers=500):
    """Fetch papers from arXiv API with retry logic."""
    papers = []
    start = 0
    batch_size = 200
    total_fetched = 0

    while total_fetched < max_papers:
        url = (
            "https://export.arxiv.org/api/query?"
            f"search_query={query}&start={start}&max_results={batch_size}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "S12-1-research/1.0"})

        for attempt in range(MAX_RETRIES):
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    data = response.read().decode("utf-8")
                break
            except (urllib.error.URLError, ConnectionError) as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"    Retry {attempt+1}/{MAX_RETRIES}: {e}")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    print(f"    FAILED after {MAX_RETRIES} retries: {e}")
                    return []

        root = ET.fromstring(data)
        entries = root.findall("atom:entry", ATOM_NS)
        if not entries:
            break

        for entry in entries:
            title_el = entry.find("atom:title", ATOM_NS)
            published_el = entry.find("atom:published", ATOM_NS)
            if title_el is not None and published_el is not None:
                title = title_el.text.strip().replace("\n", " ")
                published = published_el.text[:10]  # YYYY-MM-DD
                papers.append((published, title))
                total_fetched += 1
                if total_fetched >= max_papers:
                    break

        start += batch_size
        time.sleep(3.0)  # rate limiting: 3 queries per 3 seconds

    return papers


def compute_inter_event_times(papers):
    """Sort papers by date and compute inter-event times in days."""
    if len(papers) < 2:
        return []
    dates = sorted([datetime.strptime(p[0], "%Y-%m-%d") for p in papers])
    return [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]


def chain_cluster(iet, tau=TAU_DAYS):
    """Chain-clustering: papers within tau days are in same cluster."""
    if not iet:
        return []
    clusters = []
    current_size = 1
    for t in iet:
        if t <= tau:
            current_size += 1
        else:
            if current_size > 1:
                clusters.append(current_size)
            current_size = 1
    if current_size > 1:
        clusters.append(current_size)
    return clusters


def compute_metrics(iet, clusters):
    """Compute CV, f_C, C_max from inter-event times and clusters."""
    n = len(iet) + 1  # number of papers = inter-event times + 1
    cv = float(np.std(iet)) / float(np.mean(iet)) if len(iet) > 0 and np.mean(iet) > 0 else 0
    c_max = max(clusters) if clusters else 1
    n_cluster_papers = sum(clusters)
    f_c = n_cluster_papers / n if n > 0 else 0
    return {"cv": cv, "f_c": f_c, "c_max": c_max, "n_papers": n}


def bootstrap_metrics(iet, clusters, n_bootstrap=10000, seed=None):
    """Bootstrap resample inter-event times, compute CI for CV, f_C, C_max."""
    rng = np.random.default_rng(seed)
    stat_cv = []
    stat_fc = []
    stat_cm = []

    n = len(iet) + 1
    for _ in range(n_bootstrap):
        # Resample inter-event times with replacement
        resample = rng.choice(iet, size=len(iet), replace=True)
        # Re-cluster
        res_clusters = chain_cluster(resample.tolist(), tau=TAU_DAYS)
        cv = float(np.std(resample)) / float(np.mean(resample)) if np.mean(resample) > 0 else 0
        c_max = max(res_clusters) if res_clusters else 1
        n_cluster = sum(res_clusters)
        f_c = n_cluster / n
        stat_cv.append(cv)
        stat_fc.append(f_c)
        stat_cm.append(c_max)

    return {
        "cv_ci": (np.percentile(stat_cv, 2.5), np.percentile(stat_cv, 97.5)),
        "f_c_ci": (np.percentile(stat_fc, 2.5), np.percentile(stat_fc, 97.5)),
        "c_max_ci": (np.percentile(stat_cm, 2.5), np.percentile(stat_cm, 97.5)),
        "cv_median": float(np.median(stat_cv)),
        "fc_median": float(np.median(stat_fc)),
    }


def main():
    print("S12-1 Bootstrap Confidence Intervals")
    print("=" * 60)

    results = {}
    for topic, config in TOPICS.items():
        print(f"\nFetching: {topic} (max {config['max_papers']} papers)")
        papers = fetch_arxiv(config["query"], config["max_papers"])
        if not papers:
            print(f"  No papers fetched, skipping.")
            continue

        iet = compute_inter_event_times(papers)
        clusters = chain_cluster(iet)
        metrics = compute_metrics(iet, clusters)
        print(f"  Papers: {metrics['n_papers']}, IET samples: {len(iet)}")
        print(f"  CV={metrics['cv']:.2f}, f_C={metrics['f_c']:.3f}, C_max={metrics['c_max']}")
        print(f"  Clusters: {len(clusters)}")

        # Bootstrap
        print(f"  Bootstrapping {10000} samples...")
        ci = bootstrap_metrics(iet, clusters, n_bootstrap=10000, seed=42)
        metrics["ci"] = ci
        results[topic] = metrics

        print(f"  CV 95% CI: [{ci['cv_ci'][0]:.2f}, {ci['cv_ci'][1]:.2f}] (est={metrics['cv']:.2f})")
        print(f"  f_C 95% CI: [{ci['f_c_ci'][0]:.3f}, {ci['f_c_ci'][1]:.3f}] (est={metrics['f_c']:.3f})")
        print(f"  C_max 95% CI: [{ci['c_max_ci'][0]:.0f}, {ci['c_max_ci'][1]:.0f}] (est={metrics['c_max']:.0f})")

    # Save results
    output = {"bootstrap_ci": results}
    path = "researches/S12-1-bootstrap-ci-results.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {path}")

    # Summary table for paper
    print("\n" + "=" * 60)
    print("SUMMARY TABLE FOR PAPER")
    print("=" * 60)
    print(f"{'Topic':<25} {'N':>4} {'CV':>7} {'CV CI':>14} {'f_C':>6} {'f_C CI':>12} {'C_max':>6}")
    print("-" * 80)
    for topic, m in sorted(results.items(), key=lambda x: x[1]["cv"], reverse=True):
        ci = m["ci"]
        print(f"{topic:<25} {m['n_papers']:>4} {m['cv']:>7.2f} "
              f"[{ci['cv_ci'][0]:.2f}-{ci['cv_ci'][1]:.2f}] "
              f"{m['f_c']:>6.3f} "
              f"[{ci['f_c_ci'][0]:.3f}-{ci['f_c_ci'][1]:.3f}] "
              f"{m['c_max']:>6.0f}")


if __name__ == "__main__":
    main()
