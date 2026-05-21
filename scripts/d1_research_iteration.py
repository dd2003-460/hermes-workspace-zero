#!/usr/bin/env python3
"""
Pre-computation script for D1 research iteration cron job.
Collects project state, identifies priority actions, and outputs a structured summary.

Usage: Called as part of cron job via `script` parameter.
Output is injected into the cron prompt as context.
"""
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = "/Users/a1-6/Desktop/workspace"
PROJECTS_DIR = os.path.join(WORKSPACE, "projects")
STATE_FILE = os.path.join(PROJECTS_DIR, "tasks", "iteration_state.json")

def git_log(path, max_commits=3):
    """Get recent git log for a path."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", str(max_commits), "--", path],
            cwd=WORKSPACE, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else ["no commits found"]
    except Exception:
        return ["git log failed"]

def check_paper_compilation(tex_dir):
    """Check if papers in a directory compile."""
    results = []
    for f in Path(tex_dir).glob("*.tex"):
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", str(f)],
                cwd=tex_dir, capture_output=True, text=True, timeout=120
            )
            # Check output
            pdf = f.with_suffix('.pdf')
            if pdf.exists():
                size_kb = pdf.stat().st_size / 1024
                pages = subprocess.run(
                    ["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=5
                )
                for line in pages.stdout.split('\n'):
                    if 'Pages:' in line:
                        page_count = line.split(':')[1].strip()
                        results.append(f"{f.name}: OK ({page_count} pages, {size_kb:.0f}KB)")
                        break
                else:
                    results.append(f"{f.name}: OK ({size_kb:.0f}KB)")
            else:
                results.append(f"{f.name}: COMPILE FAILED")
        except Exception as e:
            results.append(f"{f.name}: ERROR ({str(e)[:60]})")
    return results

def analyze_project(name):
    """Analyze a single project."""
    proj_dir = os.path.join(PROJECTS_DIR, name)
    if not os.path.isdir(proj_dir):
        return None

    status = {
        "name": name,
        "modified": subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", proj_dir],
            cwd=WORKSPACE, capture_output=True, text=True, timeout=10
        ).stdout.strip() if os.path.isdir(proj_dir) else "never",
        "recent_commits": git_log(proj_dir),
        "papers": [],
        "tex_files": [],
    }

    # Find papers
    papers_dir = os.path.join(proj_dir, "papers")
    if os.path.isdir(papers_dir):
        for tex in Path(papers_dir).glob("*.tex"):
            status["tex_files"].append(str(tex))
            status["papers"].append(tex.name)

    # Compilation check
    if status["tex_files"]:
        try:
            status["compilation"] = check_paper_compilation(papers_dir)
        except:
            status["compilation"] = ["compilation check failed"]

    # Check tasks
    tasks_dir = os.path.join(proj_dir, "tasks")
    if os.path.isdir(tasks_dir):
        for f in Path(tasks_dir).glob("*.md"):
            content = f.read_text()[:500]
            if "pending" in content.lower() or "todo" in content.lower():
                status["has_pending_tasks"] = True
                break
        else:
            status["has_pending_tasks"] = False

    return status

def main():
    print("=" * 60)
    print("D1 RESEARCH ITERATION STATE REPORT")
    print(f"Generated: {datetime.now().isoformat()}")
    print("=" * 60)

    # Check workspace cleanliness
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=WORKSPACE, capture_output=True, text=True, timeout=10
    )
    modified = [line for line in result.stdout.split('\n') if line.strip()]
    print(f"\nWorkspace changes: {len(modified)} modified/added/deleted files")
    for m in modified[:10]:
        print(f"  {m}")
    if len(modified) > 10:
        print(f"  ... and {len(modified) - 10} more")

    print(f"\nD1 iteration state: {json.dumps({'exists': os.path.exists(STATE_FILE)})}")

    # Analyze key projects
    key_projects = [p for p in os.listdir(PROJECTS_DIR)
                   if p.startswith("D1-") and os.path.isdir(os.path.join(PROJECTS_DIR, p))]

    print(f"\nKey projects: {len(key_projects)}")
    for name in sorted(key_projects):
        info = analyze_project(name)
        if info:
            papers_str = ", ".join(info["papers"]) if info["papers"] else "no papers"
            tex_str = f", {len(info['tex_files'])} tex" if info["tex_files"] else ""
            print(f"\n  {name}:")
            print(f"    Papers: {papers_str}")
            print(f"    Recent commits: {' | '.join(info['recent_commits'][:2])}")
            if info.get("compilation"):
                for c in info["compilation"][:3]:
                    print(f"    Compilation: {c}")

    # Identify potential improvement targets
    print("\n" + "=" * 60)
    print("POTENTIAL IMPROVEMENT TARGETS")
    print("=" * 60)
    for name in sorted(key_projects):
        info = analyze_project(name)
        if info and info.get("compilation"):
            for c in info["compilation"]:
                if "FAILED" in c or "ERROR" in c:
                    print(f"  NEEDS FIX: {name} - {c}")
                if "0 pages" in c or "OK (1 pages" in c:
                    print(f"  TOO SHORT: {name} - {c}")
                if "pages" in c:
                    pages = c.split('(')[-1].split(' ')[0]
                    try:
                        if int(pages) < 8:
                            print(f"  NEEDS EXPANSION: {name} - {pages} pages")
                    except:
                        pass

    print("\nSTATE FILE READ:")
    if os.path.exists(STATE_FILE):
        state = json.load(open(STATE_FILE))
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        print("(state file not found)")

if __name__ == "__main__":
    main()
