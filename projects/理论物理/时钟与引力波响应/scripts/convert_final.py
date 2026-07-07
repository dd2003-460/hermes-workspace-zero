#!/usr/bin/env python3
"""
Convert Chinese markdown paper to LaTeX for arXiv submission.
Uses a block-based approach: split by --- separators, identify blocks, convert.
"""

import re
import sys
import os


def convert_inline(text):
    """Process inline formatting."""
    # Unicode superscripts → \textsuperscript{} (safe in text mode)
    text = re.sub(r'([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)',
                  lambda m: _to_textsup(m.group(0)), text)
    text = re.sub(r'\[\[(\d+[a-z]?)\]\]', r'\\cite{ref\1}', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)
    return text


def _to_textsup(s):
    """Convert Unicode superscript string to \textsuperscript{...}."""
    sup_map = {'⁻': '-', '⁰': '0', '¹': '1', '²': '2', '³': '3',
               '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
    converted = ''.join(sup_map.get(c, c) for c in s)
    return r'\textsuperscript{' + converted + '}'


def split_table_row(line):
    """Split a markdown table row on | but respecting $...$ math mode boundaries."""
    parts = []
    current = []
    in_math = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '$' and (i == 0 or line[i-1] != '\\'):
            in_math = not in_math
            current.append(ch)
        elif ch == '|' and not in_math:
            parts.append(''.join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    parts.append(''.join(current))
    return [p.strip() for p in parts if p.strip()]


def convert_table_block(lines):
    """Convert markdown table lines to LaTeX tabular."""
    if not lines:
        return None
    header = split_table_row(lines[0])
    ncols = len(header)
    col_spec = '|' + '|'.join(['c'] * ncols) + '|'
    latex = ['\\begin{tabular}{' + col_spec + '}', '\\hline']
    latex.append(' & '.join(header) + ' \\\\')
    latex.append('\\hline')
    for line in lines[1:]:
        if re.match(r'^[\s|:-]+$', line):
            continue
        cols = split_table_row(line)
        if len(cols) == ncols:
            latex.append(' & '.join(cols) + ' \\\\')
    latex.extend(['\\hline', '\\end{tabular}'])
    return '\n'.join(latex)


def extract_refs(text):
    """Extract ALL references from text (multiple chapters + final list).
    Also converts Unicode superscripts to LaTeX math notation via placeholders.
    """
    # Unicode superscript placeholders — resolved in bibitem loop after all escaping
    sup_digits_P = {'⁰': r'\P0\E', '¹': r'\P1\E', '²': r'\P2\E', '³': r'\P3\E',
                    '⁴': r'\P4\E', '⁵': r'\P5\E', '⁶': r'\P6\E', '⁷': r'\P7\E',
                    '⁸': r'\P8\E', '⁹': r'\P9\E', '⁻': r'\P-\E'}
    refs = {}
    for m in re.finditer(r'^\s*\[(\d+[a-z]?)\]\s+(.+?)$', text, re.MULTILINE):
        ref_id = m.group(1)
        ref_text = m.group(2).replace('*', '').replace('**', '')
        # Replace Unicode superscripts with placeholders (no { or } to avoid conflicts)
        for sup, platex in sup_digits_P.items():
            ref_text = ref_text.replace(sup, platex)
        if ref_id not in refs:
            refs[ref_id] = ref_text
    return refs


def convert_content_lines(lines):
    """Convert content lines to LaTeX (no title/abstract/TOC/ref headers)."""
    result = []
    in_itemize = False
    in_chapter_ref = False
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Chapter reference header: "## 参考文献（第X章）" or "## 参考文献"
        if re.match(r'^##\s+参考文献', stripped):
            in_chapter_ref = True
            i += 1
            continue
        if in_chapter_ref:
            if re.match(r'^\s*\[\d', stripped):
                i += 1
                continue
            if stripped == '':
                i += 1
                continue
            in_chapter_ref = False
            # Fall through

        # Skip horizontal rules and code fences
        if re.match(r'^-{3,}$', stripped):
            i += 1
            continue
        if stripped.startswith('```'):
            i += 1
            continue

        # Section headers
        m = re.match(r'^(#{1,4})\s+(.+)$', line)
        if m and not stripped.startswith('>'):
            if in_itemize:
                result.append('\\end{itemize}')
                in_itemize = False
            level = len(m.group(1))
            title = convert_inline(m.group(2).strip())
            if level == 1:
                result.append(r'\section{' + title + '}')
            elif level == 2:
                result.append(r'\subsection{' + title + '}')
            elif level == 3:
                result.append(r'\subsubsection{' + title + '}')
            result.append('')
            i += 1
            continue

        # Tables
        if stripped.startswith('|'):
            table_lines = []
            while i < n and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            tab = convert_table_block(table_lines)
            if tab:
                result.append(tab)
                result.append('')
            continue

        # Bullet list
        m = re.match(r'^[-*]\s+(.+)$', line)
        if m and not re.match(r'^-{3,}$', m.group(1)):
            if not in_itemize:
                result.append('\\begin{itemize}')
                in_itemize = True
            item_text = convert_inline(m.group(1))
            item_text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', item_text)
            result.append('  \\item ' + item_text)
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.+)$', line)
        if m:
            if not in_itemize:
                result.append('\\begin{itemize}')
                in_itemize = True
            text = convert_inline(m.group(2))
            text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
            result.append('  \\item[' + m.group(1) + r'] ' + text)
            i += 1
            continue

        # Empty line
        if stripped == '':
            result.append('')
            i += 1
            continue

        # Blockquote
        if stripped.startswith('> '):
            result.append(convert_inline(stripped[2:]))
            i += 1
            continue

        result.append(convert_inline(stripped))
        i += 1

    if in_itemize:
        result.append('\\end{itemize}')

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_final.py <input.md> [output.tex]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if output_path is None:
        base = os.path.basename(input_path)
        output_path = os.path.join(os.path.dirname(input_path), os.path.splitext(base)[0] + '.tex')

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    lines = md_text.split('\n')

    # Extract metadata from original
    title_m = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else "OLC Network GW Detection"

    abs_m = re.search(r'> \*\*摘要\*\*[:：]\s*(.+?)(?=\n)', md_text, re.DOTALL)
    abs_text = ''
    if abs_m:
        abs_text = abs_m.group(1).strip().replace('*', '').replace('**', '')
        abs_text = re.sub(r'\n+', ' ', abs_text)

    refs = extract_refs(md_text)
    print(f"Title: {title}")
    print(f"References: {len(refs)}")

    # Process line by line, identifying and skipping preamble blocks
    i = 0
    n = len(lines)

    def skip_blanks():
        nonlocal i
        while i < n and lines[i].strip() == '':
            i += 1

    # SKIP title
    if i < n and lines[i].strip().startswith('# ') and not lines[i].strip().startswith('## '):
        i += 1
    skip_blanks()

    # SKIP abstract blockquote (> **摘要**...)
    if i < n and lines[i].strip().startswith('> '):
        i += 1
    skip_blanks()

    # Skip first --- separator
    if i < n and lines[i].strip() == '---':
        i += 1
    skip_blanks()

    # SKIP entire TOC block (from ## 目录 through ---)
    if i < n and '目录' in lines[i]:
        # Skip everything until next ---
        while i < n and lines[i].strip() != '---':
            i += 1
        if i < n:
            i += 1  # skip the ---
        skip_blanks()

    # Now i should point to "# 第 1 章：引言" or content
    body_latex = convert_content_lines(lines[i:])

    # Assemble document
    out = []
    out.append(r'\documentclass[12pt,a4paper]{article}')
    out.append(r'\usepackage{xeCJK}')
    out.append(r'\setCJKmainfont{Songti SC}')
    out.append(r'\setCJKsansfont{Heiti SC}')
    out.append(r'\setCJKmonofont{FangSong}')
    out.append(r'\setmainfont{Times New Roman}')
    out.append(r'\usepackage{amsmath, amssymb, amsthm}')
    out.append(r'\usepackage{geometry}')
    out.append(r'\geometry{margin=1in}')
    out.append(r'\usepackage{graphicx}')
    out.append(r'\usepackage{booktabs}')
    out.append(r'\usepackage{hyperref}')
    out.append(r'\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=blue}')
    out.append(r'\usepackage{mathptmx}')
    out.append(r'\usepackage{indentfirst}')
    out.append(r'\setlength{\parindent}{2em}')
    out.append(r'\setlength{\parskip}{0.5em}')
    out.append(r'\begin{document}')
    out.append(r'\title{' + title + r'}')
    out.append(r'\author{Chenglu}')
    out.append(r'\date{}')
    out.append(r'\maketitle')
    out.append(r'\begin{abstract}')
    out.append(abs_text)
    out.append(r'\end{abstract}')
    out.append('')
    out.extend(body_latex)
    out.append('')
    out.append(r'\begin{thebibliography}{99}')

    def ref_key(rid):
        if rid[-1].isalpha():
            return (1, int(rid[:-1]), rid[-1])
        return (0, int(rid), 'z')

    # Placeholders → LaTeX math superscripts (after all escaping)
    sup_digits_latex = {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
                        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '-': '\\mathrm{-}'}

    for rid in sorted(refs.keys(), key=ref_key):
        rt = refs[rid]
        # Escape backslash FIRST to avoid double-escaping \& etc.
        rt = rt.replace('\\', '\\textbackslash{}')
        rt = rt.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
        rt = rt.replace('_', '\\_').replace('$', '\\$')
        rt = rt.replace('{', '\\{').replace('}', '\\}')
        rt = rt.replace('^', '\\textasciicircum{}').replace('~', '\\textasciitilde{}')
        # Resolve placeholders: \P-\E → \textsuperscript{-}, \P1\E → \textsuperscript{1}
        rt = rt.replace(r'\P-\E', r'\textsuperscript{-}')
        for asc in '0123456789':
            rt = rt.replace(r'\P' + asc + r'\E', r'\textsuperscript{' + asc + '}')
        out.append(r'\bibitem{ref' + rid + '} ' + rt)

    out.append(r'\end{thebibliography}')
    out.append(r'\end{document}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')

    print(f"Generated: {output_path}")


if __name__ == '__main__':
    main()
