#!/usr/bin/env python3
"""T-PUB-1 主会稿 md -> tex -> pdf 可复现构建。
6 个 markdown 章节 + 2 图 + 6 篇 ref 组装成 main-conference-20261123.tex，xelatex+xeCJK 编译。
md 任何改动后: python3 build_tex.py  即可同步 .tex + .pdf。
"""
import re, os, subprocess, json, sys

BASE = os.path.dirname(os.path.abspath(__file__))
def rd(f): return open(os.path.join(BASE, f)).read()

# ---- math-aware escape: keep $...$ intact, escape the rest ----
def esc_text(s):
    s = s.replace('`', '')
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = s.replace('\\|', '∣')          # markdown-escaped pipe -> unicode (safe in tabular)
    s = s.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$')
    s = s.replace('_', r'\_').replace('#', r'\#').replace('^', r'\^')
    s = s.replace('{', r'\{').replace('}', r'\}')
    return s

def esc(s):
    parts = re.split(r'(\$[^$]+\$)', s)
    return ''.join(p if (p.startswith('$') and p.endswith('$') and len(p) > 2) else esc_text(p) for p in parts)

def split_row(line):
    line = line.strip()
    if line.startswith('|'): line = line[1:]
    if line.endswith('|'): line = line[:-1]
    return [c.strip() for c in re.split(r'(?<!\\)\|', line)]

def is_sep(line): return bool(re.match(r'^\|[\s\-|]+\|$', line.strip()))

def md_body(text, start_marker, end_markers):
    lines = text.split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith(start_marker))
    end = len(lines)
    for em in end_markers:
        for j in range(start + 1, len(lines)):
            if lines[j].startswith(em):
                end = min(end, j)
    return lines[start + 1:end]

def blocks(lines):
    out, i = [], 0
    while i < len(lines):
        l = lines[i].strip()
        if not l:
            i += 1; continue
        if l.startswith('## '):
            out.append(('sub', l[3:].strip())); i += 1; continue
        if l.startswith('|') and i + 1 < len(lines) and is_sep(lines[i+1]):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                if not is_sep(lines[i]): rows.append(split_row(lines[i]))
                i += 1
            if rows:
                ncol = len(rows[0])
                norm = [(r + ['']*(ncol-len(r)))[:ncol] for r in rows]
                out.append(('table', norm))
            continue
        if l.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:]); i += 1
            out.append(('list', items)); continue
        para = [l]; i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('## ', '|', '- ')):
            para.append(lines[i].strip()); i += 1
        out.append(('para', ' '.join(para)))
    return out

def render(blocks):
    tex = []
    for typ, content in blocks:
        if typ == 'sub':
            tex.append('\\subsection*{' + esc(content) + '}\n')
        elif typ == 'para':
            tex.append(esc(content) + '\n\n')
        elif typ == 'list':
            tex.append('\\begin{itemize}\n' + '\n'.join('  \\item ' + esc(x) for x in content) + '\n\\end{itemize}\n\n')
        elif typ == 'table':
            rows = content
            cols = 'l' * len(rows[0])
            tab = '\\begin{tabular}{' + cols + '}\n'
            tab += ' \\\\\n'.join(' & '.join(esc(c) for c in r) for r in rows)
            tab += '\n\\end{tabular}'
            tex.append('\\begin{table}[h]\n\\centering\n' + tab + '\n\\end{table}\n\n')
    return '\n'.join(tex)

# ---- refs: real arXiv titles from research json (source-verified) ----
def build_refs():
    d = json.load(open(os.path.join(BASE, '..', '..', 'research', 'related-work-arxiv-20261123.json')))
    titles = {}
    for cat, blk in d.items():
        for it in blk.get('items', []):
            iid = it.get('id', '').split('v')[0]
            if iid in ('2603.05399','2610.30512','2609.13824','2510.09738','2606.15029','2610.05452'):
                titles[iid] = it.get('title', '')
    order = [('dev2026jrh','2603.05399'),('arena2026hard','2610.30512'),('consistency2026','2609.13824'),
             ('verdict2025','2510.09738'),('metric2026','2606.15029'),('vera2026','2610.05452')]
    lines = [r'\section*{References}', r'\small', r'\begin{thebibliography}{9}']
    for key, aid in order:
        lines.append('\\bibitem{%s} %s. arXiv:%s.' % (key, esc(titles[aid]), aid))
    lines.append(r'\end{thebibliography}')
    return '\n'.join(lines)

def main():
    intro_setup = rd('intro-setup-draft-20261123.md')
    intro_lines = md_body(intro_setup, '## §1 Introduction', ['## §2 Setup'])
    setup_lines = md_body(intro_setup, '## §2 Setup', [])
    findings_lines = [l for l in rd('findings-draft-20261123.md').split('\n') if not l.startswith('#')]
    related_lines = [l for l in rd('related-work-draft-20261123.md').split('\n') if not l.startswith('#')]
    impl_lines = [l for l in rd('implications-limitations-draft-20261123.md').split('\n') if not l.startswith('#')]
    appendix_lines = [l for l in rd('appendix-draft-20261123.md').split('\n') if not l.startswith('#')]

    ab_lines = rd('abstract-draft-20261123.md').split('\n')
    ab_start = next(i for i, l in enumerate(ab_lines) if l.startswith('# Abstract'))
    abstract = ' '.join(l for l in ab_lines[ab_start+1:] if l.strip() and not l.startswith('#'))

    figs = set(os.listdir(os.path.join(BASE, 'figures')))
    fig_tex = ''
    if 'fig1-format-reliability.png' in figs:
        fig_tex += '\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{figures/fig1-format-reliability.png}\n\\caption{Format failure rate (bars) and verdict flip rate (line) across the three prompt variants. The mechanical judge (dashed) fails on 0\\% of calls.}\n\\end{figure}\n\n'
    if 'fig2-mechanism.png' in figs:
        fig_tex += '\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{figures/fig2-mechanism.png}\n\\caption{Mechanism probe: the six V1 failure cases re-judged at max\\_tokens 500 vs 2000. Recovery is determined by whether the reasoning chain converges, not by max\\_tokens itself.}\n\\end{figure}\n\n'
    if 'fig3-guess-bound.png' in figs:
        fig_tex += '\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{figures/fig3-guess-bound.png}\n\\caption{Analytic upper bound on the probability of guessing all checkpoints correct, per task. Full-rank tasks (blue) sit at 1e-10 to 1e-7; rank-deficient tasks (red) at 1e-6 to 3.3e-5. All are far below the 1e-4 threshold, and 2000 seeded simulations produced 0 full-guess successes.}\n\\end{figure}\n\n'

    preamble = r'''\documentclass[10pt,twocolumn]{article}
\usepackage[margin=0.9in,columnsep=0.33in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Songti SC}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt plus 1pt}
\title{\textbf{Mechanical Judges as an Exact Reference: Measuring LLM Judge Reliability on the Formalizable Core}}
\author{Anonymous (double-blind)}
\date{}
\begin{document}
\maketitle
'''

    doc = preamble
    doc += '\\begin{abstract}\n' + esc(abstract) + '\n\\end{abstract}\n\n'
    doc += '\\section{Introduction}\n' + render(blocks(intro_lines))
    doc += '\\section{Setup \\& Method}\n' + render(blocks(setup_lines))
    doc += '\\section{Findings}\n' + fig_tex + render(blocks(findings_lines))
    doc += '\\section{Related Work}\n' + render(blocks(related_lines))
    doc += '\\section{Implications \\& Limitations}\n' + render(blocks(impl_lines))
    doc += '\n' + build_refs()
    doc += '\n\\appendix\n'
    doc += render(blocks(appendix_lines))
    doc += '\n\\end{document}\n'

    out = os.path.join(BASE, 'main-conference-20261123.tex')
    open(out, 'w').write(doc)
    print('wrote', len(doc), 'chars ->', out)

    r = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', 'main-conference-20261123.tex'],
                       cwd=BASE, capture_output=True, text=True, timeout=180)
    print('xelatex exit:', r.returncode)
    if r.returncode != 0:
        log = open(os.path.join(BASE, 'main-conference-20261123.log')).read()
        for l in log.split('\n'):
            if l.startswith('!'): print('ERR:', l)
        sys.exit(1)
    log = open(os.path.join(BASE, 'main-conference-20261123.log')).read()
    m = re.search(r'Output written on .*?(\d+) pages', log)
    print('PDF pages:', m.group(1) if m else '?')

if __name__ == '__main__':
    main()
