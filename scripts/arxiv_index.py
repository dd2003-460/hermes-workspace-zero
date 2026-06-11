#!/usr/bin/env python3
"""
arxiv_index.py — 全局论文索引构建器

遍历 projects/ 下所有 D1 项目，收集论文信息并生成索引报告。
输出到 stdout 的 Markdown 格式可用于 TASKS.md / ACADEMIC-STATUS.md / DASHBOARD.md 更新。

运行: python3 arxiv_index.py [--json] [--markdown] [--latex]

--json      JSON 输出（程序化消费）
--markdown  Markdown 表格输出（默认）
--latex     LaTeX 参考文献表格（用于论文附录）
"""

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

PROJECTS_DIR = Path(__file__).parent.parent / "projects"


@dataclass
class PaperInfo:
    """论文信息"""
    project: str
    title: str
    version: str
    pages: int = 0
    pdf_size_kb: int = 0
    status: str = "unknown"  # arxiv-ready / drafting / blocked / complete
    arxiv_id: str = ""
    figures: int = 0
    tex_files: list = None
    pdf_files: list = None
    tarball: str = ""
    tarball_size_kb: int = 0
    issues: list = None
    last_modified: str = ""
    progress: int = 0  # 0-100

    def __post_init__(self):
        if self.tex_files is None:
            self.tex_files = []
        if self.pdf_files is None:
            self.pdf_files = []
        if self.issues is None:
            self.issues = []


def parse_tex_pages(tex_file):
    """从 .tex 文件估算页数"""
    try:
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count pages using \end{document} structure
        if '\\end{document}' not in content and '\\end{thebibliography}' not in content:
            return {'pages': 1, 'figures': 0, 'refs': 0, 'issues': ['no end-document found']}

        # Estimate from line count (rough: ~50 lines per page)
        lines = content.split('\n')
        text_lines = [l for l in lines if l.strip() and not l.strip().startswith('%')]
        pages = max(1, len(text_lines) // 45)

        # Count figures
        figures = len(re.findall(r'\\begin\{figure\}', content))

        # Count references
        refs = len(re.findall(r'\\cite\{', content))

        # Check for errors/warnings
        tex_base = os.path.splitext(tex_file)[0]
        log_file = tex_base + '.log'
        issues = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                if 'error' in log_content.lower():
                    issues.append('errors in compilation log')
                if 'overfull' in log_content:
                    issues.append('overfull boxes')

        return {'pages': pages, 'figures': figures, 'refs': refs, 'issues': issues}
    except Exception:
        return {'pages': 0, 'figures': 0, 'refs': 0, 'issues': ['parse error']}


def scan_project(proj_dir):
    """扫描项目目录收集论文信息"""
    proj_name = os.path.basename(proj_dir)
    if not proj_name.startswith('D1-'):
        return None

    papers = []

    # Find .tex files
    tex_files = list(Path(proj_dir).rglob('*.tex'))
    # Filter out .tex files inside non-project directories
    tex_files = [f for f in tex_files if 'latex-pandoc' not in str(f)]

    pdf_files = list(Path(proj_dir).rglob('*.pdf'))
    tarballs = list(Path(proj_dir).rglob('*.tar.gz'))

    # Skip non-paper directories
    if not tex_files and not pdf_files:
        return None

    for tex_file in tex_files:
        info = parse_tex_pages(tex_file)
        pages = info['pages']
        figures = info['figures']

        # Find associated PDF
        pdf_base = tex_file.stem
        pdf_path = tex_file.parent / (pdf_base + '.pdf')
        has_pdf = pdf_path.exists() and pdf_path in pdf_files

        # Status detection
        status = 'drafting'
        if has_pdf and not info['issues']:
            status = 'arxiv-ready'
            progress = 100
        elif has_pdf:
            status = 'arxiv-ready'
            progress = 90
        else:
            progress = 0  # No compiled PDF = can't estimate progress

        paper = PaperInfo(
            project=proj_name,
            title=os.path.basename(tex_file).replace('.tex', ''),
            version='v0',  # Unknown without git tag
            pages=pages,
            pdf_size_kb=os.path.getsize(pdf_path) // 1024 if has_pdf else 0,
            status=status,
            figures=figures,
            tex_files=[str(tex_file)],
            pdf_files=[str(pdf_path)] if has_pdf else [],
            issues=info['issues'],
            progress=progress,
        )
        papers.append(paper)

    # Add tarballs
    for tb in tarballs:
        # Find the paper this tarball belongs to
        tb_name = os.path.basename(tb)
        for paper in papers:
            if any(kw in tb_name.lower() for kw in ['arxiv', 'submission', 'tar']):
                paper.tarball = str(tb)
                paper.tarball_size_kb = os.path.getsize(tb) // 1024
                break

    return papers if papers else None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='ArXiv paper index builder')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('--markdown', action='store_true', help='Markdown output (default)')
    parser.add_argument('--latex', action='store_true', help='LaTeX bibtable output')
    parser.add_argument('--project', type=str, help='Scan specific project only')
    args = parser.parse_args()

    # Scan all projects
    all_papers = []
    projects = [PROJECTS_DIR / d for d in os.listdir(PROJECTS_DIR)
                if os.path.isdir(PROJECTS_DIR / d) and d.startswith('D1-')]

    for proj in projects:
        if args.project and proj.name != args.project:
            continue
        result = scan_project(proj)
        if result:
            all_papers.extend(result)

    if not all_papers:
        print("No papers found.", file=sys.stderr)
        sys.exit(1)

    # Sort by project then pages
    all_papers.sort(key=lambda p: (p.project, -p.pages))

    # Output
    if args.json:
        print(json.dumps([asdict(p) for p in all_papers], indent=2, ensure_ascii=False))
    elif args.markdown or args.latex:
        print_markdown(all_papers)
    else:
        print_markdown(all_papers)


def print_markdown(papers):
    """Markdown table output"""

    print("# 全局 ArXiv 论文索引")
    print()
    print(f"> 自动生成: {len(papers)} 篇论文 across {len(set(p.project for p in papers))} 个项目")
    print()

    # Summary
    ready = [p for p in papers if p.status == 'arxiv-ready']
    drafting = [p for p in papers if p.status == 'drafting']

    print("## 论文状态汇总")
    print()
    print(f"| 状态 | 数量 |")
    print(f"|------|------|")
    print(f"| 🟢 arXiv 就绪 | {len(ready)} |")
    print(f"| 🟡 撰写中 | {len(drafting)} |")
    print()

    # Per-project details
    for proj_name in sorted(set(p.project for p in papers)):
        proj_papers = [p for p in papers if p.project == proj_name]
        print(f"### {proj_name}")
        print()
        print("| 论文 | 版本 | 状态 | PDF | Figures | 进度 |")
        print("|------|------|------|-----|---------|------|")
        for p in proj_papers:
            status_icon = "🟢" if p.status == 'arxiv-ready' else "🟡"
            pdf_display = f"{p.pdf_size_kb}K/{p.pages}p" if p.pdf_size_kb > 0 else f"—/{p.pages}p"
            print(f"| {p.title} | {p.version} | {status_icon} {p.status} | {pdf_display} | {p.figures} | {p.progress}% |")
        print()

    # Blocked papers
    blocked = [p for p in papers if any('error' in i for i in p.issues)]
    if blocked:
        print("## 阻塞论文")
        print()
        for p in blocked:
            print(f"- **{p.title}**: {', '.join(p.issues)}")
        print()

    # Tools check
    tools_dir = Path(__file__).parent
    tools_tools_dir = Path(__file__).parent.parent / "tools"

    print("## 工具链状态")
    print()
    print("| 工具 | 路径 | 状态 |")
    print("|------|------|------|")
    for tool in ['arxiv_submit.sh', 'arxiv_submission_checklist.sh', 'arxiv_cat.py',
                 'arxiv_cats.py', 'arxiv_prepare.py', 'papers_readiness.sh',
                 'project_health_check.sh', 'index_verifier.py']:
        path = tools_dir / tool
        status = "✅" if path.exists() else "❌"
        print(f"| {tool} | /scripts/ | {status} |")
    for tool in ['search_web.py', 'wiki-search.py', 'wiki-embed.py']:
        path = tools_tools_dir / tool
        status = "✅" if path.exists() else "❌"
        print(f"| {tool} | /tools/ | {status} |")
    print()


if __name__ == "__main__":
    main()
