#!/usr/bin/env python3
"""Search arXiv API using the arxiv Python package.

Falls back to curl --resolve if the arxiv package fails (DNS/rate limit).

Usage:
    python3 arxiv_cat.py <query> [max_results=10]
    python3 arxiv_cat.py "precision accessibility AI" 5
    python3 arxiv_cat.py "gravitational wave PTA" 3
"""
import subprocess
import sys
import re

ARXIV_IP = "151.101.135.42"

def search_via_curl(query, max_results=10):
    """Search arXiv using curl --resolve to bypass DNS issues."""
    keywords = query.split()
    ti_and = "+AND+".join([f"ti:{k}" for k in keywords])
    abs_or = "+OR+".join([f"abs:{k}" for k in keywords])
    search_query = f"({ti_and})+OR+({abs_or})"
    cmd = [
        "curl", "--resolve", f"export.arxiv.org:443:{ARXIV_IP}",
        "-s",
        f"https://export.arxiv.org/api/query?search_query={search_query}&max_results={max_results}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def parse_arxiv_xml(xml_content):
    """Parse arXiv Atom XML entries."""
    entries = []
    if not xml_content:
        return entries

    titles = re.findall(r'<title>(.*?)</title>', xml_content, re.DOTALL)
    summs = re.findall(r'<summary>(.*?)</summary>', xml_content, re.DOTALL)
    dates = re.findall(r'<published>(.*?)</published>', xml_content, re.DOTALL)
    cats = re.findall(r'<category\s+term="([^"]*)"', xml_content, re.DOTALL)

    for i in range(min(len(titles), len(summs))):
        title = re.sub(r'\n', ' ', titles[i]).strip()
        summary = re.sub(r'\n', ' ', summs[i]).strip()[:500]
        date = dates[i][:10] if i < len(dates) else "N/A"
        entry_cats = [c for j, c in enumerate(cats) if j >= i * 2 and j < i * 2 + 4]

        entries.append({
            "title": title,
            "summary": summary,
            "date": date,
            "categories": entry_cats[:5]
        })
    return entries

def search_arxiv(query, max_results=10):
    """Search arXiv, trying arxiv package first then curl fallback."""
    # Method 1: Try arxiv package
    try:
        import arxiv
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=max_results)

        entries = []
        for result in client.results(search):
            entries.append({
                "title": result.title.replace("\n", " ").strip()[:500],
                "summary": result.summary.replace("\n", " ").strip()[:500],
                "date": str(result.published)[:10],
                "categories": result.categories[:5]
            })

        if entries:
            return entries
    except Exception:
        pass  # Fall through to curl

    # Method 2: Fallback to curl --resolve
    xml_content = search_via_curl(query, max_results)
    if xml_content:
        return parse_arxiv_xml(xml_content)

    return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 arxiv_cat.py <query> [max_results]")
        print("Example: python3 arxiv_cat.py 'precision accessibility AI' 5")
        sys.exit(1)

    query = " ".join(sys.argv[1:-1]) if sys.argv[-1].replace('.','',1).isdigit() else " ".join(sys.argv[1:])
    max_results = 10
    if len(sys.argv) >= 3:
        max_results = int(sys.argv[-1])

    print(f"Searching arXiv for: {query} (max {max_results})")
    print("=" * 60)

    results = search_arxiv(query, max_results)

    if not results:
        print("No results found.")
        sys.exit(1)

    for i, entry in enumerate(results, 1):
        print(f"\n[{i}/{len(results)}] [{entry['date']}] {entry['title']}")
        print(f"  Categories: {', '.join(entry['categories']) if entry['categories'] else 'N/A'}")
        print(f"  Abstract: {entry['summary'][:300]}...")
        print("-" * 60)

    print(f"\nTotal: {len(results)} results")

if __name__ == "__main__":
    main()
