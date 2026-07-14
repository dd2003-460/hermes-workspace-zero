#!/usr/bin/env python3
"""
Convert Chinese markdown paper to LaTeX for arXiv submission.
- [[N]] -> \cite{refN}
- Headers -> \section{}/\subsection{}
- Tables -> LaTeX tabular
- Lists -> itemize
- Preserves LaTeX math ($...$, $$...$$)
- Handles bibliography separately
"""

import re
import sys
import os


def clean_md(text):
    """Remove markdown formatting but keep LaTeX math."""
    # Remove **bold** wrapper (keep content)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    return text


def convert_table_block(lines):
    """Convert a block of markdown table lines to LaTeX tabular."""
    if not lines:
        return None
    # Determine column count from header
    header = [c.strip() for c in lines[0].split('|') if c.strip()]
    ncols = len(header)
    col_spec = '|' + '|'.join(['c'] * ncols) + '|'

    latex = []
    latex.append('\\begin{tabular}{' + col_spec + '}')
    latex.append('\\hline')
    latex.append(' & '.join(header) + ' \\\\')
    latex.append('\\hline')

    for line in lines[1:]:
        if re.match(r'^[\s|:-]+$', line):
            continue  # separator
        cols = [c.strip() for c in line.split('|') if c.strip()]
        if len(cols) == ncols:
            latex.append(' & '.join(cols) + ' \\\\')

    latex.append('\\hline')
    latex.append('\\end{tabular}')
    return '\n'.join(latex)


def convert_inline(text):
    """Process inline formatting: citations, bold, italic, code."""
    # [[N]] -> \cite{refN}
    text = re.sub(r'\[\[(\d+[a-z]?)\]\]', r'\\cite{ref\1}', text)
    # **bold** -> \textbf{}
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # `code` -> \texttt{}
    text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)
    return text


def extract_references(text):
    """Extract all reference entries from the markdown text.
    Returns dict of ref_id -> clean citation text.
    """
    refs = {}
    # Match lines like "[7] Schaffrath et al..." or "[5a] ..."
    pattern = re.compile(r'^\s*\[(\d+[a-z]?\.?)\]\s+(.+?)$', re.MULTILINE)
    for m in pattern.finditer(text):
        ref_id = m.group(1)
        ref_text = m.group(2)
        # Clean: remove * markdown, keep LaTeX math
        ref_text = ref_text.replace('*', '').replace('**', '')
        if ref_id not in refs:
            refs[ref_id] = ref_text
    return refs


def convert_body(lines, refs):
    """Convert markdown lines to LaTeX, skipping the reference section."""
    result = []
    in_abstract = False
    abstract_text = []
    in_itemize = False
    has_abstract = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for reference section
        stripped = line.strip()
        if stripped in ('## 参考文献', '## References', '## 参考文献'):
            # Close any open environments
            if in_abstract:
                # We'll handle abstract separately
                pass
            if in_itemize:
                result.append('\\end{itemize}')
                in_itemize = False
            break  # Stop processing body

        # Title line at very start
        if stripped == '# ' and result == []:
            result.append('_title_placeholder_')
            i += 1
            continue

        # Abstract blockquote (comes right after title)
        if stripped == '> **摘要**：' or (stripped.startswith('> **摘要**') and not has_abstract):
            in_abstract = True
            has_abstract = True
            quote_content = clean_md(stripped[2:])
            abstract_text.append(quote_content)
            i += 1
            continue

        if in_abstract:
            if stripped.startswith('> '):
                abstract_text.append(clean_md(stripped[2:]))
            elif stripped == '':
                # Empty line might end abstract
                pass
            else:
                # Non-quote line ends abstract
                in_abstract = False
                abs_str = ' '.join(abstract_text)
                result.append('_abstract_end_')
                result.append(abs_str)
                result.append('_abstract_body_start_')
                # Fall through to process this line
            if in_abstract:
                i += 1
                continue
            # Check if we just finished the abstract
            if result and result[-1] == '_abstract_end_':
                abs_str = ' '.join(abstract_text)
                result.pop()  # remove _abstract_end_
                result.append(abs_str)
                abstract_text = []

        # Skip the TOC section
        if stripped == '## 目录' or stripped == '## Table of Contents':
            # Skip until next ## header or ---
            i += 1
            while i < len(lines) and lines[i].strip() != '' and not lines[i].startswith('## '):
                i += 1
            continue

        # Horizontal rule
        if re.match(r'^-{3,}$', stripped):
            i += 1
            continue

        # Code fences
        if stripped.startswith('```'):
            i += 1
            continue  # skip code blocks

        # Section headers
        m = re.match(r'^#{1,4}\s+(.+)$', line)
        if m and not line.startswith('>'):
            # Close itemize if open
            if in_itemize:
                result.append('\\end{itemize}')
                in_itemize = False

            level = len(re.match(r'^(#+)', line).group(1))
            title = convert_inline(clean_md(m.group(1)))

            if level == 1:
                result.append(r'\section{' + title + '}')
                result.append('')
            elif level == 2:
                result.append(r'\subsection{' + title + '}')
                result.append('')
            elif level == 3:
                result.append(r'\subsubsection{' + title + '}')
                result.append('')
            i += 1
            continue

        # Table
        if stripped.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
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
            item_text = convert_inline(clean_md(m.group(1)))
            # Handle **bold** in bullets
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
            num = m.group(1)
            text = convert_inline(clean_md(m.group(2)))
            text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
            result.append('  \\item[' + num + r'] ' + text)
            i += 1
            continue

        # Empty line
        if stripped == '':
            result.append('')
            i += 1
            continue

        # Regular text
        if in_itemize:
            # Check if this looks like it belongs to a previous item
            # (not a new section, not empty)
            pass  # keep in itemize
        result.append(convert_inline(clean_md(line)))
        i += 1

    if in_itemize:
        result.append('\\end{itemize}')

    return result, has_abstract


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_to_latex.py <input.md> [output.tex]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if output_path is None:
        base = os.path.basename(input_path)
        name = os.path.splitext(base)[0]
        output_path = os.path.join(os.path.dirname(input_path), name + '.tex')

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_lines = md_text.split('\n')

    # Extract references
    refs = extract_references(md_text)
    print(f"Found {len(refs)} unique references")

    # Convert body
    body_result, has_abstract = convert_body(md_lines, refs)

    # Build LaTeX document
    tex_lines = []

    # Preamble
    tex_lines.append('\\documentclass[12pt,a4paper]{article}')
    tex_lines.append('\\usepackage{xeCJK}')
    tex_lines.append('\\setCJKmainfont{Songti SC}')
    tex_lines.append('\\setCJKsansfont{Heiti SC}')
    tex_lines.append('\\setCJKmonofont{FangSong}')
    tex_lines.append('\\setmainfont{Times New Roman}')
    tex_lines.append('')
    tex_lines.append('\\usepackage{amsmath, amssymb, amsthm}')
    tex_lines.append('\\usepackage{geometry}')
    tex_lines.append('\\geometry{margin=1in}')
    tex_lines.append('\\usepackage{graphicx}')
    tex_lines.append('\\usepackage{booktabs}')
    tex_lines.append('\\usepackage{hyperref}')
    tex_lines.append('\\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=blue}')
    tex_lines.append('\\usepackage{mathptmx}')
    tex_lines.append('\\usepackage{indentfirst}')
    tex_lines.append('\\setlength{\\parindent}{2em}')
    tex_lines.append('\\setlength{\\parskip}{0.5em}')
    tex_lines.append('')
    tex_lines.append('\\begin{document}')

    # Title and abstract
    # The body_result starts with the content after title placeholder
    # Find abstract markers
    abstract_text = ''
    body_start = 0
    for idx, item in enumerate(body_result):
        if item == '_abstract_body_start_':
            # Next item is the abstract text
            body_start = idx + 2  # skip marker + abstract text
            break

    # Find title and abstract from original markdown
    # Title
    title_match = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "OLC Network GW Detection"
    tex_lines.append('\\title{' + title + '}')
    tex_lines.append('\\author{Chenglu}')
    tex_lines.append('\\date{}')
    tex_lines.append('\\maketitle')

    # Abstract
    abs_match = re.search(r'> \\*\\*摘要\\*\\*：(.+?)(?=---|$)', md_text, re.DOTALL)
    if abs_match:
        abs_text = abs_match.group(1).strip()
        abs_text = abs_text.replace('**', '').replace('*', '')
        abs_text = re.sub(r'\n+', ' ', abs_text)
        tex_lines.append('')
        tex_lines.append('\\begin{abstract}')
        tex_lines.append(abs_text)
        tex_lines.append('\\end{abstract}')
        tex_lines.append('')

    # Body (skip title placeholder and abstract markers)
    for item in body_result:
        if item in ('_title_placeholder_', '_abstract_body_start_', '_abstract_end_'):
            continue
        # Skip lines between markers
        if item == '' and body_result and body_result[body_result.index(item)-1] == '_abstract_end_' if '_abstract_end_' in body_result else True:
            pass
        tex_lines.append(item)

    # Bibliography
    tex_lines.append('')
    tex_lines.append('\\begin{thebibliography}{99}')

    # Sort references: numeric first, then alphanumeric
    def ref_sort_key(ref_id):
        if ref_id[-1].isalpha():
            return (1, int(ref_id[:-1]), ref_id[-1])
        return (0, int(ref_id), 'z')

    for ref_id in sorted(refs.keys(), key=ref_sort_key):
        ref_text = refs[ref_id]
        # Escape special LaTeX chars
        ref_text = ref_text.replace('&', '\\&')
        ref_text = ref_text.replace('%', '\\%')
        ref_text = ref_text.replace('#', '\\#')
        ref_text = ref_text.replace('_', '\\_')
        ref_text = ref_text.replace('$', '\\$')
        ref_text = ref_text.replace('{', '\\{')
        ref_text = ref_text.replace('}', '\\}')
        ref_text = ref_text.replace('^', '\\textasciicircum{}')
        ref_text = ref_text.replace('~', '\\textasciitilde{}')
        ref_text = ref_text.replace('\\', '\\textbackslash{}')
        tex_lines.append('\\bibitem{ref' + ref_id + '} ' + ref_text)

    tex_lines.append('\\end{thebibliography}')
    tex_lines.append('\\end{document}')

    output = '\n'.join(tex_lines) + '\n'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Generated: {output_path} ({len(tex_lines)} lines)")


if __name__ == '__main__':
    main()
