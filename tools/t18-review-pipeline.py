#!/usr/bin/env python3
"""
T18: End-to-end paper upload to web LLM for external review.
Integrates arXiv search + download + web LLM review pipeline.

Usage:
    python tools/t18-review-pipeline.py search "<keywords>" --service claude
    python tools/t18-review-pipeline.py download <paper_id> --output-dir ./papers
    python tools/t18-review-pipeline.py review <pdf_file> --service claude --prompt "review prompt"
    python tools/t18-review-pipeline.py batch <papers_dir> --service claude
    python tools/t18-review-pipeline.py results <session_dir>

Requires:
    - Playwright (for web LLM interaction)
    - Edge browser (for session reuse)
    - Optional: CLAUDE_API_KEY (as backup if web LLM unavailable)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ─── arXiv Search (inline to avoid external dependencies) ──────────

ARXIV_API = "http://api.arxiv.org/v2/"
ATOM_NS = "http://www.w3.org/2005/Atom"


def search_arxiv(query, max_results=10):
    """Search arXiv API and return results."""
    import urllib.request
    import urllib.parse
    import urllib.error
    from xml.etree import ElementTree

    encoded = urllib.parse.quote(query)
    url = f"{ARXIV_API}search/?query=abs:{encoded}&max_results={max_results}&sortBy=submittedDate"

    req = urllib.request.Request(url, headers={"User-Agent": "T18Pipeline/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        xml_data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"arXiv search failed: {e}", file=sys.stderr)
        return []

    root = ElementTree.fromstring(xml_data)
    entries_ns = {"atom": ATOM_NS, "arxiv": "http://arxiv.org/schemas/atom"}

    results = []
    for entry in root.findall("atom:entry", entries_ns):
        title = entry.find("atom:title", entries_ns).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", entries_ns).text.strip().replace("\n", " ")
        arxiv_id = entry.find("atom:id", entries_ns).text
        pdf_url = None
        for link in entry.findall("atom:link", entries_ns):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
                break

        results.append({
            "arxiv_id": arxiv_id.split("v/")[-1] if "v/" in arxiv_id else arxiv_id,
            "title": title,
            "summary": summary,
            "pdf_url": pdf_url,
            "authors": [a.find("atom:name", entries_ns).text for a in entry.findall("atom:author", entries_ns)],
            "categories": list(set(
                [c.get("term") for c in entry.findall("atom:category", entries_ns) if "term" in c.get("term", "")]
            )),
        })

    return results


def download_pdf(arxiv_id, output_dir):
    """Download PDF from arXiv."""
    import urllib.request

    # Try API PDF
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    filename = f"{arxiv_id}.pdf"
    filepath = os.path.join(output_dir, filename)

    print(f"  Downloading: {pdf_url}")
    try:
        urllib.request.urlretrieve(pdf_url, filepath)
        # Verify it's a PDF
        with open(filepath, 'rb') as f:
            if f.read(5) != b'%PDF-':
                print(f"  Warning: downloaded file is not a valid PDF, removing")
                os.remove(filepath)
                return None
        print(f"  Saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"  Download failed: {e}", file=sys.stderr)
        return None


# ─── Web LLM Review via Node.js tool ────────────────────────────────

def run_web_llm_review(pdf_path, service, prompt=None):
    """Run web-llm-review.js to upload a paper for review."""
    cmd = [
        "node",
        os.path.join(os.path.dirname(__file__), "web-llm-review.js"),
        "upload",
        pdf_path,
        "--service", service,
    ]
    if prompt:
        cmd.extend(["--prompt", prompt])

    print(f"  Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min timeout for web LLM
        )
        if result.returncode != 0:
            print(f"  Error: {result.stderr}", file=sys.stderr)
            return None

        # Parse JSON output
        output = result.stdout.strip()
        # Extract JSON from output (may have log lines before JSON)
        json_start = output.find("{")
        if json_start >= 0:
            return json.loads(output[json_start:])

        return {"status": "completed", "raw_output": output}

    except subprocess.TimeoutExpired:
        print(f"  Timeout: web LLM review took too long", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Error running review: {e}", file=sys.stderr)
        return None


# ─── Claude API Fallback ────────────────────────────────────────────

def review_with_claude_api(pdf_path, prompt):
    """Fallback: use Claude API directly (requires ANTHROPIC_API_KEY)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        # Read PDF as base64 (Claude supports PDF upload via SDK)
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        # For now, just send a text prompt (Claude API doesn't directly support PDF in messages)
        # In practice, users would convert PDF to images or use document upload API
        msg = client.messages.create(
            model="claude-sonnet-4-5-20260401",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Please review this paper. Title and abstract:

{prompt}

Please provide a review covering:
1. Technical accuracy and methodology
2. Clarity of exposition
3. Originality and significance
4. Specific issues or improvements""",
            }],
        )
        return msg.content[0].text if msg.content else None

    except ImportError:
        return None
    except Exception as e:
        print(f"  Claude API error: {e}", file=sys.stderr)
        return None


# ─── Main Pipeline ──────────────────────────────────────────────────

def cmd_search(args):
    """Search arXiv and download top results for review."""
    papers = search_arxiv(" ".join(args.keywords), max_results=args.top)
    if not papers:
        print("No papers found.")
        return

    print(f"\nFound {len(papers)} paper(s) for: {' '.join(args.keywords)}\n")
    for i, p in enumerate(papers):
        print(f"  [{i}] {p['title'][:60]}...")
        print(f"      arXiv: {p['arxiv_id']}")

    if args.download:
        os.makedirs(args.output_dir, exist_ok=True)
        for p in papers:
            filepath = download_pdf(p["arxiv_id"], args.output_dir)
            if filepath:
                print(f"\n  Reviewing: {p['title']}")
                result = review(args, filepath)
                if result:
                    print(f"  Review result saved.")

    # Save search results
    output_file = os.path.join(args.output_dir, f"arxiv-search-{datetime.now().strftime('%Y%m%d')}.json")
    with open(output_file, "w") as f:
        json.dump({"search_date": datetime.now(timezone.utc).isoformat(), "query": " ".join(args.keywords), "papers": papers}, f, indent=2)
    print(f"\nSearch results saved to: {output_file}")


def cmd_download(args):
    """Download a single paper from arXiv."""
    os.makedirs(args.output_dir, exist_ok=True)
    filepath = download_pdf(args.paper_id, args.output_dir)
    if filepath:
        print(f"\nDownloaded: {filepath}")
    else:
        print("Download failed.")


def cmd_review(args):
    """Review a single paper."""
    if not os.path.exists(args.pdf):
        print(f"Error: file not found: {args.pdf}")
        return

    result = None

    # Try web LLM first
    print(f"\n  === Web LLM Review ({args.service}) ===")
    result = run_web_llm_review(args.pdf, args.service, args.prompt)

    # Fallback to Claude API if web LLM failed
    if result is None:
        print(f"\n  === Fallback: Claude API Review ===")
        result = review_with_claude_api(args.pdf, args.prompt)

    if result:
        # Save result
        output_dir = args.output_dir or "note/t18-results"
        os.makedirs(output_dir, exist_ok=True)
        filename = Path(args.pdf).stem
        result_file = os.path.join(output_dir, f"{filename}-review-{datetime.now().strftime('%Y%m%d')}.json")
        with open(result_file, "w") as f:
            json.dump({"pdf": args.pdf, "review": result, "timestamp": datetime.now(timezone.utc).isoformat()}, f, indent=2, ensure_ascii=False)
        print(f"\n  Review saved to: {result_file}")
    else:
        print("\n  Review failed.")


def cmd_batch(args):
    """Review all PDFs in a directory."""
    pdf_dir = args.papers_dir
    if not os.path.isdir(pdf_dir):
        print(f"Error: not a directory: {pdf_dir}")
        return

    pdfs = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"No PDFs found in: {pdf_dir}")
        return

    print(f"\n  Found {len(pdfs)} PDF(s) to review\n")

    results = []
    for pdf in pdfs:
        print(f"\n  === Reviewing: {os.path.basename(pdf)} ===")
        result = run_web_llm_review(pdf, args.service, args.prompt)
        results.append({"pdf": pdf, "result": result, "timestamp": datetime.now(timezone.utc).isoformat()})

        if args.parallel:
            # Simple sequential for now (parallel requires browser pool)
            pass

    # Save batch results
    output_file = os.path.join(args.output_dir or "note/t18-results", f"batch-review-{datetime.now().strftime('%Y%m%d')}.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump({"batch_date": datetime.now(timezone.utc).isoformat(), "service": args.service, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"\n  Batch results saved to: {output_file}")


def cmd_results(args):
    """Display review results."""
    session_dir = args.session_dir
    if not os.path.exists(session_dir):
        print(f"Error: directory not found: {session_dir}")
        return

    results = []
    for f in os.listdir(session_dir):
        if f.endswith(".json"):
            with open(os.path.join(session_dir, f)) as fp:
                results.append(json.load(fp))

    if not results:
        print("No results found.")
        return

    for r in results:
        print(f"\n  === {r.get('pdf', 'unknown')} ===")
        review = r.get('review', r.get('raw_output', 'No review content'))
        if isinstance(review, dict):
            review = json.dumps(review, indent=2)
        print(f"  {str(review)[:500]}...")


def review(args, pdf_path):
    """Unified review function used by both search and direct review."""
    return run_web_llm_review(pdf_path, args.service, args.prompt)


def main():
    parser = argparse.ArgumentParser(description="T18: Paper upload to web LLM for external review")
    sub = parser.add_subparsers(dest="command")

    # search
    search_p = sub.add_parser("search", help="Search arXiv and optionally download+review")
    search_p.add_argument("keywords", nargs="+", help="Search keywords")
    search_p.add_argument("--top", type=int, default=5, help="Max results")
    search_p.add_argument("--service", default="claude", choices=["claude", "chatgpt"])
    search_p.add_argument("--download", action="store_true", help="Download and review")
    search_p.add_argument("--output-dir", default="note/t18-results")
    search_p.add_argument("--prompt", help="Review prompt")

    # download
    dl_p = sub.add_parser("download", help="Download a single paper")
    dl_p.add_argument("paper_id", help="arXiv paper ID")
    dl_p.add_argument("--output-dir", default="note/t18-results")

    # review
    rev_p = sub.add_parser("review", help="Review a single PDF")
    rev_p.add_argument("pdf", help="PDF file path")
    rev_p.add_argument("--service", default="claude", choices=["claude", "chatgpt"])
    rev_p.add_argument("--prompt", help="Review prompt")
    rev_p.add_argument("--output-dir", default="note/t18-results")

    # batch
    batch_p = sub.add_parser("batch", help="Review all PDFs in directory")
    batch_p.add_argument("papers_dir", help="Directory with PDFs")
    batch_p.add_argument("--service", default="claude", choices=["claude", "chatgpt"])
    batch_p.add_argument("--prompt", help="Review prompt")
    batch_p.add_argument("--output-dir", default="note/t18-results")

    # results
    res_p = sub.add_parser("results", help="Display review results")
    res_p.add_argument("session_dir", help="Directory with results")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "review":
        cmd_review(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "results":
        cmd_results(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
