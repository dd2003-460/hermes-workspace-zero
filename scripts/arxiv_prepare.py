#!/usr/bin/env python3
"""Generate arXiv submission package for a paper.

Checks that all required files exist and creates a submission-ready directory.

Usage:
    python3 arxiv_prepare.py <paper-directory> <output-directory>
    python3 arxiv_prepare.py /path/to/papers /tmp/arxiv-submission
"""
import os
import sys
import shutil
import re
from pathlib import Path

def extract_braced(content, cmd):
    """Extract content of \\cmd{...} with balanced brace matching."""
    pattern = rf'\\{cmd}\{{'
    m = re.search(pattern, content)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    return content[start:i-1] if depth == 0 else None

def strip_latex_formatting(s):
    """Remove LaTeX formatting commands from text."""
    # Strip \textbf{...}, \textit{...}, \texttt{...}, \emph{...} -> keep content
    for cmd in ('textbf', 'textit', 'texttt', 'emph'):
        pat = r'\\' + cmd + r'\{[^}]*\}'
        s = re.sub(pat, lambda m: m.group(0).split('{', 1)[1].rstrip('}'), s)
    s = re.sub(r'\\vspace\{[^}]*\}', '', s)
    s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\textcolor\{[^}]*\}\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\\\\s*', ' ', s)
    s = re.sub(r'[{}\n\r]', ' ', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

def extract_metadata(tex_file):
    """Extract title, author, keywords from .tex file."""
    meta = {}
    with open(tex_file, 'r') as f:
        content = f.read()

    # Title (balanced brace matching)
    title_raw = extract_braced(content, 'title')
    if title_raw:
        meta['title'] = strip_latex_formatting(title_raw)

    # Author (balanced brace matching)
    author_raw = extract_braced(content, 'author')
    if author_raw:
        meta['author'] = strip_latex_formatting(author_raw)

    # Keywords
    keyword_match = re.search(r'\\textbf\{\s*关键词.*?\}:?\s*(.+?)(?:\n|$)', content, re.DOTALL)
    if keyword_match:
        meta['keywords'] = keyword_match.group(1).strip()

    # License
    license_match = re.search(r'(?:License|许可证).*?(CC\s*(?:BY|BY-SA|BY-NC|BY-ND).*?(?:4\.0|3\.0))', content, re.IGNORECASE | re.DOTALL)
    if license_match:
        meta['license'] = license_match.group(1).strip()

    return meta

def scan_assets(directory):
    """Scan for paper assets."""
    assets = {
        'tex': [],
        'pdf': [],
        'figures': [],
        'bib': [],
        'supplementary': []
    }
    for f in Path(directory).rglob('*'):
        if f.is_file():
            ext = f.suffix.lower()
            if ext == '.tex' and 'log' not in f.name:
                assets['tex'].append(f.name)
            elif ext == '.pdf':
                assets['pdf'].append(f.name)
            elif ext in ('.png', '.jpg', '.jpeg', '.pdf', '.eps'):
                assets['figures'].append(f.name)
            elif ext == '.bib':
                assets['bib'].append(f.name)
            elif ext in ('.txt', '.md', '.csv', '.json'):
                assets['supplementary'].append(f.name)
    return assets

def prepare_submission(paper_dir, output_dir):
    """Prepare arXiv submission package."""
    paper_dir = Path(paper_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find .tex files
    tex_files = list(paper_dir.rglob('*.tex'))
    if not tex_files:
        print(f"ERROR: No .tex file found in {paper_dir}")
        return False

    tex_file = tex_files[0]
    print(f"Processing: {tex_file.name}")

    # Extract metadata
    meta = extract_metadata(tex_file)
    if meta.get('title'):
        print(f"  Title: {meta['title'][:80]}")
    if meta.get('author'):
        print(f"  Author: {meta['author'][:60]}")
    if meta.get('license'):
        print(f"  License: {meta['license']}")

    # Scan assets
    assets = scan_assets(paper_dir)
    print(f"\n  Found assets:")
    print(f"    .tex files: {len(assets['tex'])}")
    print(f"    PDFs: {len(assets['pdf'])}")
    print(f"    Figures: {len(assets['figures'])}")
    print(f"    .bib files: {len(assets['bib'])}")
    print(f"    Supplementary: {len(assets['supplementary'])}")

    # Create submission directory
    src_dir = output_dir / 'source'
    src_dir.mkdir(exist_ok=True)

    # Copy essential files
    for f in tex_files:
        shutil.copy2(f, src_dir)

    # Copy figures
    fig_dir = src_dir / 'figures'
    fig_dir.mkdir(exist_ok=True)
    for f in assets['figures']:
        src = paper_dir / f
        if src.exists():
            shutil.copy2(src, fig_dir / f)

    # Copy .bib files
    if assets['bib']:
        bib_dir = src_dir / 'bib'
        bib_dir.mkdir(exist_ok=True)
        for f in assets['bib']:
            src = paper_dir / f
            if src.exists():
                shutil.copy2(src, bib_dir / f)

    # Write manifest
    manifest = src_dir / 'SUBMISSION.manifest.txt'
    with open(manifest, 'w') as mf:
        mf.write(f"# arXiv Submission Manifest\n")
        mf.write(f"# Generated: {Path.home()}\n\n")
        if meta.get('title'):
            mf.write(f"Title: {meta['title']}\n")
        if meta.get('author'):
            mf.write(f"Author: {meta['author']}\n")
        if meta.get('keywords'):
            mf.write(f"Keywords: {meta['keywords']}\n")
        if meta.get('license'):
            mf.write(f"License: {meta['license']}\n")
        mf.write(f"\n# Files to upload to arXiv:\n")
        mf.write(f"  Primary .tex: {tex_file.name}\n")
        mf.write(f"  Figures: {', '.join(assets['figures']) if assets['figures'] else 'NONE'}\n")
        mf.write(f"  .bib: {', '.join(assets['bib']) if assets['bib'] else 'NONE (using thebibliography)'}\n")
        mf.write(f"  PDF (for preview): {', '.join(assets['pdf']) if assets['pdf'] else 'Compile .tex first'}\n")
        mf.write(f"\n# arXiv categories:\n")
        mf.write(f"  [NEEDS MANUAL SELECTION]\n")

    print(f"\n  Submission package: {src_dir}")
    print(f"  Manifest: {manifest}")
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 arxiv_prepare.py <paper-directory> <output-directory>")
        print("Example: python3 arxiv_prepare.py papers/2026-GW-BacQFT /tmp/arxiv-submission")
        sys.exit(1)

    paper_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(paper_dir):
        print(f"ERROR: {paper_dir} is not a directory")
        sys.exit(1)

    success = prepare_submission(paper_dir, output_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
