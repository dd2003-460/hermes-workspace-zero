#!/usr/bin/env python3
"""
Convert Chinese markdown paper to LaTeX for arXiv submission.
Approach: Extract title/abstract/refs separately, then convert body.
"""

import re
import sys
import os


def convert_inline(text):
    """Process inline formatting."""
    text = re.sub(r'\[\[(\d+[a-z]?)\]\]', r'\\cite{ref\1}', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)
    return text


def convert_table_block(lines):
    """Convert markdown table lines to LaTeX tabular."""
    if not lines:
        return None
    header = [c.strip() for c in lines[0].split('|') if c.strip()]
    ncols = len(header)
    col_spec = '|' + '|'.join(['c'] * ncols) + '|'
    latex = ['\\begin{tabular}{' + col_spec + '}', '\\hline']
    latex.append(' & '.join(header) + ' \\\\')
    latex.append('\\hline')
    for line in lines[1:]:
        if re.match(r'^[\s|:-]+$', line):
            continue
        cols = [c.strip() for c in line.split('|') if c.strip()]
        if len(cols) == ncols:
            latex.append(' & '.join(cols) + ' \\\\')
    latex.extend(['\\hline', '\\end{tabular}'])
    return '\n'.join(latex)


def extract_refs(text):
    """Extract references: returns {ref_id: text}."""
    refs = {}
    for m in re.finditer(r'^\s*\[(\d+[a-z]?)\]\s+(.+?)$', text, re.MULTILINE):
        ref_id = m.group(1)
        ref_text = m.group(2).replace('*', '').replace('**', '')
        if ref_id not in refs:
            refs[ref_id] = ref_text
    return refs


def convert_body_lines(lines):
    """Convert body lines (no title/abstract/refs) to LaTeX."""
    result = []
    in_itemize = False

    for line in lines:
        stripped = line.strip()

        # Skip horizontal rules and code fences
        if re.match(r'^-{3,}$', stripped):
            continue
        if stripped.startswith('```'):
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
            continue

        # Tables
        if stripped.startswith('|'):
            table_lines = []
            while lines and lines[0].strip().startswith('|'):
                table_lines.append(lines.pop(0))
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
            continue

        # Empty line
        if stripped == '':
            result.append('')
            continue

        # Regular text
        result.append(convert_inline(stripped))

    if in_itemize:
        result.append('\\end{itemize}')

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_to_latex2.py <input.md> [output.tex]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if output_path is None:
        base = os.path.basename(input_path)
        output_path = os.path.join(os.path.dirname(input_path), os.path.splitext(base)[0] + '.tex')

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Extract metadata
    title_m = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else "OLC Network GW Detection"

    abs_m = re.search(r'> \*\*摘要\*\*[:：]\s*(.+?)(?=---|\n\n##|\Z)', md_text, re.DOTALL)
    abs_text = ''
    if abs_m:
        abs_text = abs_m.group(1).strip().replace('*', '').replace('**', '')
        abs_text = re.sub(r'\n+', ' ', abs_text)

    refs = extract_refs(md_text)
    print(f"Title: {title}")
    print(f"References: {len(refs)}")

    # Remove title, abstract, TOC, and references from body
    body_text = md_text

    # Remove title
    body_text = re.sub(r'^#\s+.+\n', '', body_text, count=1)

    # Remove abstract blockquote
    body_text = re.sub(r'^> \*\*摘要\*\*[:：].+?(?=---)', '', body_text, count=1, flags=re.DOTALL)

    # Remove TOC
    body_text = re.sub(r'\n---\n## 目录\n.*?(?=\n---)', '\n', body_text, count=1, flags=re.DOTALL)

    # Remove references section (last occurrence of ## 参考文献 ... end)
    body_text = re.sub(r'\n## 参考文献\s*\n.*$', '', body_text, count=1, flags=re.DOTALL)

    lines = body_text.split('\n')
    body_latex = convert_body_lines(lines)

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

    for rid in sorted(refs.keys(), key=ref_key):
        rt = refs[rid]
        rt = rt.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
        rt = rt.replace('_', '\\_').replace('$', '\\$')
        rt = rt.replace('{', '\\{').replace('}', '\\}')
        rt = rt.replace('^', '\\textasciicircum{}').replace('~', '\\textasciitilde{}')
        rt = rt.replace('\\', '\\textbackslash{}')
        out.append(r'\bibitem{ref' + rid + '} ' + rt)

    out.append(r'\end{thebibliography}')
    out.append(r'\end{document}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')

    print(f"Generated: {output_path}")


if __name__ == '__main__':
    main()
