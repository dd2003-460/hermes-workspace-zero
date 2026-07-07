#!/usr/bin/env python3
"""
LLM-assisted review pipeline — browser rendering + Claude visual analysis.
For T10: implements Markdown/PDF/code review via Playwright + Claude.

Usage:
    python llm-review-pipeline.py markdown <input.md> [options]
    python llm-review-pipeline.py pdf <input.pdf> [options]
    python llm-review-pipeline.py code <file.py> [options]
    python llm-review-pipeline.py review <screenshot.png> "[CLAUDE_API_KEY]"
    python llm-review-pipeline.py full <input.md> "[CLAUDE_API_KEY]"
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


def install_playwright():
    """Install Playwright browsers if needed."""
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])


def render_markdown(md_file, output_html=None):
    """Convert Markdown to HTML for browser rendering."""
    try:
        import markdown
    except ImportError:
        print("Installing markdown...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "markdown-it-py"])
        import markdown

    if output_html is None:
        output_html = str(Path(md_file).with_suffix('.rendered.html'))

    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert with LaTeX support
    html = markdown.make_html(md_text, extension=['tables', 'fenced_code', 'codehilite'])

    # Wrap in full HTML with MathJax
    template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{Path(md_file).name}</title>
<style>
body {{ max-width: 800px; margin: 40px auto; padding: 0 20px; font-family: serif; line-height: 1.6; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
pre {{ background: #f4f4f4; padding: 16px; border-radius: 5px; overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f4f4f4; }}
</style>
<script>
MathJax = {{
    tex: {{ inlineMath: [['$', '$'], ['\\(', '\\)']] }},
    svg: {{ fontCache: 'global' }}
}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
</head>
<body>
{html}
</body>
</html>"""

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"Rendered: {output_html}")
    return output_html


def capture_screenshot(html_file, output_png, full_page=True, selector='body'):
    """Use Playwright to render HTML and capture screenshot."""
    if not PLAYWRIGHT_AVAILABLE:
        print("Installing Playwright...")
        install_playwright()
        from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        file_url = f"file://{os.path.abspath(html_file)}"
        print(f"Opening: {file_url}")
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_selector(selector, timeout=10000)

        # Wait for MathJax typesetting
        time.sleep(3)

        if full_page:
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)

        page.screenshot(path=output_png, full_page=full_page)
        browser.close()

    print(f"Screenshot: {output_png}")
    return output_png


def analyze_with_claude(screenshot_path, prompt, api_key):
    """Send screenshot to Claude for visual analysis."""
    try:
        import anthropic
    except ImportError:
        print("Installing anthropic...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
        import anthropic

    if not api_key:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set")
            return None

    with open(screenshot_path, 'rb') as f:
        img_data = f.read()

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model='claude-sonnet-4-5-20260401',
        max_tokens=2000,
        messages=[{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': prompt or 'Review this document for formatting, rendering, and quality issues.'},
                {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': 'image/png',
                        'data': img_data.decode('base64') if isinstance(img_data, bytes) else img_data,
                    }
                }
            ]
        }]
    )

    review = msg.content[0].text if msg.content else None
    return review


def review_markdown(md_file, api_key=None, output_dir='note/reviews'):
    """Full pipeline for Markdown review."""
    os.makedirs(output_dir, exist_ok=True)
    basename = Path(md_file).stem

    html_file = f"{basename}.rendered.html"
    screenshot = f"{basename}-review.png"
    review_file = f"{basename}-review.txt"

    print("=== Step 1: Render Markdown ===")
    render_markdown(md_file, html_file)

    print("\n=== Step 2: Capture screenshot ===")
    capture_screenshot(html_file, screenshot)

    if api_key:
        print("\n=== Step 3: Claude visual review ===")
        prompt = """Review this academic document screenshot:
1. Formatting: margins, spacing, alignment
2. Equations: rendering quality, numbering, cross-page breaks
3. Tables/charts: readability, labeling
4. Overall: visual hierarchy, consistency, professionalism
5. Specific issues and improvement suggestions"""

        review = analyze_with_claude(screenshot, prompt, api_key)
        if review:
            with open(review_file, 'w', encoding='utf-8') as f:
                f.write(f"Date: {datetime.now(timezone.utc).isoformat()}\nInput: {md_file}\n\n{review}")
            print(f"Review saved: {review_file}")
            return review
    else:
        print("\nSkip Claude review (no API key). Screenshot saved for manual review.")

    return None


def review_pdf(pdf_file, api_key=None, output_dir='note/reviews'):
    """Review PDF by converting to images via browser."""
    os.makedirs(output_dir, exist_ok=True)

    # Convert PDF pages to images using browser
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("Installing pdf2image...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdf2image"])
        from pdf2image import convert_from_path

    basename = Path(pdf_file).stem
    pages = convert_from_path(pdf_file, dpi=150)

    reviews = []
    for i, page in enumerate(pages):
        page_img = f"{basename}-page-{i+1}.png"
        page.review = f"{basename}-page-{i+1}-review.txt"
        page.save(page_img)
        print(f"Page {i+1} screenshot: {page_img}")

        if api_key:
            review = analyze_with_claude(page_img, f"Review page {i+1} of this academic document.", api_key)
            if review:
                with open(page.review, 'w', encoding='utf-8') as f:
                    f.write(f"Page {i+1}\n\n{review}")
                reviews.append(review)

    return reviews


def main():
    parser = argparse.ArgumentParser(description='LLM-assisted review pipeline (T10)')
    sub = parser.add_subparsers(dest='command')

    # Markdown command
    md_cmd = sub.add_parser('markdown', help='Review Markdown document')
    md_cmd.add_argument('input', help='Input Markdown file')
    md_cmd.add_argument('--api-key', help='Claude API key')
    md_cmd.add_argument('--output-dir', default='note/reviews')

    # PDF command
    pdf_cmd = sub.add_parser('pdf', help='Review PDF document')
    pdf_cmd.add_argument('input', help='Input PDF file')
    pdf_cmd.add_argument('--api-key', help='Claude API key')
    pdf_cmd.add_argument('--output-dir', default='note/reviews')

    # Full pipeline command
    full_cmd = sub.add_parser('full', help='Full review pipeline')
    full_cmd.add_argument('input', help='Input file (md/pdf/html)')
    full_cmd.add_argument('--api-key', help='Claude API key')
    full_cmd.add_argument('--output-dir', default='note/reviews')

    args = parser.parse_args()

    if args.command == 'markdown':
        review_markdown(args.input, args.api_key, args.output_dir)
    elif args.command == 'pdf':
        review_pdf(args.input, args.api_key, args.output_dir)
    elif args.command == 'full':
        # Auto-detect file type
        ext = Path(args.input).suffix.lower()
        if ext == '.md':
            review_markdown(args.input, args.api_key, args.output_dir)
        elif ext == '.pdf':
            review_pdf(args.input, args.api_key, args.output_dir)
        else:
            print(f"Unsupported file type: {ext}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
