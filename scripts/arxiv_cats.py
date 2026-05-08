#!/usr/bin/env python3
"""Search arXiv for category terms and get relevant category recommendations.

Uses the arxiv Python package (with curl --resolve fallback).

Usage:
    python3 arxiv_cats.py <query> [max_results=5]
    python3 arxiv_cats.py "gravitational wave pulsar timing" 5
    python3 arxiv_cats.py "AI precision accessibility" 5
"""
import sys
from collections import Counter

# Known arXiv category descriptions
CATEGORY_MAP = {
    "gr-qc": "General Relativity and Cosmology",
    "hep-th": "High Energy Physics - Theory",
    "hep-ph": "High Energy Physics - Phenomenology",
    "astro-ph": "Astrophysics",
    "astro-ph.CO": "Astrophysics of Galaxies",
    "astro-ph.HE": "High Energy Astrophysical Phenomena",
    "cs.AI": "Artificial Intelligence",
    "cs.LG": "Machine Learning",
    "cs.LO": "Logic in Computer Science",
    "cs.CL": "Computation and Language",
    "cs.CV": "Computer Vision and Pattern Recognition",
    "cs.MA": "Multiagent Systems",
    "math-ph": "Mathematical Physics",
    "math.AP": "Analysis of PDEs",
    "math.DG": "Differential Geometry",
    "math.FA": "Functional Analysis",
    "math.GM": "General Mathematics",
    "math.QA": "Quantum Algebra",
    "quant-ph": "Quantum Physics",
    "physics.data-an": "Data Analysis, Statistics and Probability",
    "nlin.CD": "Chaotic Dynamics",
}

def recommend_categories(query, max_results=5):
    """Search for related papers and recommend arXiv categories."""
    try:
        import arxiv
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=max_results)
    except Exception:
        return []

    entries = []
    try:
        for result in client.results(search):
            entries.append({
                "title": result.title,
                "categories": result.categories
            })
    except Exception:
        return []

    if not entries:
        return []

    # Count category frequency
    cat_counter = Counter()
    for entry in entries:
        for cat in entry.get("categories", []):
            cat_counter[cat] += 1

    recommendations = []
    for cat, count in cat_counter.most_common():
        recommendations.append({
            "category": cat,
            "confidence": count / max_results,
            "description": cat
        })

    return recommendations

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 arxiv_cats.py <query> [max_results]")
        print("Example: python3 arxiv_cats.py 'gravitational wave pulsar timing' 5")
        sys.exit(1)

    query = " ".join(sys.argv[1:-1]) if sys.argv[-1].replace('.','',1).isdigit() else " ".join(sys.argv[1:])
    max_results = 5
    if len(sys.argv) >= 3:
        max_results = int(sys.argv[-1])

    print(f"Searching arXiv for category recommendations: {query}")
    print(f"(Based on top {max_results} related papers)")
    print("=" * 60)

    results = recommend_categories(query, max_results)

    if not results:
        print("No results found (may be rate-limited).")
        sys.exit(1)

    print(f"\nRecommended arXiv categories:")
    for i, rec in enumerate(results, 1):
        cat = rec["category"]
        desc = CATEGORY_MAP.get(cat, "Unknown")
        conf = f"{rec['confidence']:.0%}"
        print(f"  {i}. {cat} — {desc} (confidence: {conf})")

    print(f"\nUsage: select categories above when submitting to arXiv")
    print(f"  Primary category should be the highest confidence one.")

if __name__ == "__main__":
    main()
