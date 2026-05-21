#!/usr/bin/env python3
r"""Verify all \bibitem entries in a .tex file have inline \cite{} references.

Usage:
    verify_citations.py <paper.tex>

Returns 0 if all bibitems have citations, 1 if any are uncited.
"""
import re
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_citations.py <paper.tex>")
        sys.exit(2)

    paper_path = sys.argv[1]
    with open(paper_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all bibitem labels
    bibitems = set(re.findall(r'\\bibitem\{([^}]+)\}', content))

    # Extract all cite references (split multi-cite entries)
    cites_raw = re.findall(r'\\cite\{([^}]+)\}', content)
    cites = set()
    for c in cites_raw:
        for item in c.split(','):
            cites.add(item.strip())

    uncited = set()
    for bib in sorted(bibitems):
        if bib not in cites:
            uncited.add(bib)

    print(f"Total {len(bibitems)} bibitems, {len(cites)} inline cite refs")

    if uncited:
        print(f"\nUncited ({len(uncited)}):")
        for u in sorted(uncited):
            print(f"  - {u}")
        print(f"\nSTATUS: FAIL — {len(uncited)} uncited reference(s)")
        sys.exit(1)
    else:
        print(f"STATUS: PASS — all {len(bibitems)} references cited")
        sys.exit(0)

if __name__ == '__main__':
    main()
