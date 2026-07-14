#!/usr/bin/env python3
"""
Convert Chinese markdown paper to LaTeX for arXiv submission.
Handles:
  - [[N]] citations -> \cite{refN}
  - ## and ### headers -> \section{}, \subsection{}
  - Tables (convert markdown tables to LaTeX)
  - Code blocks and fenced code blocks
  - Math preservation (inline $...$ and display $$...$$)
  - Bullet lists -> itemize environment
  - Horizontal rules --- -> \bigskip
  - Bold/italic text
  - Blockquotes -> quote environment
"""

import re
import sys
import os

def convert_table(text):
    """Convert a markdown table to LaTeX table environment."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if line is a table header (contains |)
        if '|' in line and line.strip().startswith('|'):
            # Count columns
            cols = [c.strip() for c in line.split('|') if c.strip()]
            ncols = len(cols)

            # Check if next line is separator (--- | ---)
            if i + 1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i+1]):
                # Skip separator line
                i += 2

                # Build LaTeX table
                latex_lines = []
                latex_lines.append('\\begin{tabular}{' + '|' + '|'.join(['c'] * ncols) + '|}')
                latex_lines.append('\\hline')

                # Header row
                header = ' & '.join(cols) + ' \\\\'
                latex_lines.append(header)
                latex_lines.append('\\hline')

                # Data rows
                while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                    row_cols = [c.strip() for c in lines[i].split('|') if c.strip()]
                    if len(row_cols) == ncols:
                        row = ' & '.join(row_cols) + ' \\\\'
                        latex_lines.append(row)
                    i += 1

                latex_lines.append('\\hline')
                latex_lines.append('\\end{tabular}')
                result.append('\n'.join(latex_lines))
                continue
        i += 1
        result.append(line)
    return '\n'.join(result)


def convert_list_item(text):
    """Convert bullet points to LaTeX itemize items."""
    # Handle **bold** list items
    line = re.sub(r'\*\*(.+?)\*\*', r'{\\textbf{\1}}', text)
    return '  \\item ' + line


def convert_markdown_to_latex(md_text):
    """Convert markdown text to LaTeX."""
    lines = md_text.split('\n')
    result = []
    in_code = False
    in_quote = False
    ref_section = False
    bib_entries = []
    bib_map = {}  # ref number -> LaTeX citation text
    current_section_title = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip horizontal rules (but keep track of logical sections)
        if re.match(r'^-{3,}$', line.strip()):
            result.append('')
            i += 1
            continue

        # Reference section header detection
        if line.strip() == '## 参考文献' or line.strip() == '## References' or line.strip() == '## 参考文献':
            ref_section = True
            result.append('')
            result.append(r'\begin{thebibliography}{99}')
            i += 1
            continue

        if ref_section and re.match(r'^\[(\d+[a-z]?)\]', line.strip()):
            # Parse reference: [N] Citation text
            m = re.match(r'^\[(\d+[a-z]?)\]\s*(.+)$', line.strip())
            if m:
                ref_id = m.group(1)
                ref_text = m.group(2)
                # Clean up ref text - remove markdown formatting
                ref_text = ref_text.replace('*', '').replace('**', '')
                bib_entries.append((ref_id, ref_text))
                bib_map[ref_id] = ref_text
            i += 1
            continue

        if ref_section:
            if line.strip() == '' or line.startswith('##') or line.startswith('#'):
                # End of reference section
                if bib_entries:
                    result.append(r'\end{thebibliography}')
                    bib_entries = []
                ref_section = False
                # Fall through to process this line as normal

        # Skip code fences
        if line.strip().startswith('```'):
            if in_code:
                result.append('')
                in_code = False
            else:
                result.append('')
                in_code = True
            i += 1
            continue

        if in_code:
            result.append(line)
            i += 1
            continue

        # Blockquote
        if line.strip().startswith('> '):
            if not in_quote:
                result.append(r'\begin{quote}')
                in_quote = True
            quote_text = line.strip()[2:]
            quote_text = quote_text.replace('*', '').replace('**', '')
            result.append(quote_text)
            i += 1
            continue
        elif in_quote:
            result.append(r'\end{quote}')
            in_quote = False

        # Title
        if re.match(r'^# \s*$', line.strip()):
            continue  # skip empty title line

        # Main title (only one at top)
        m = re.match(r'^# (.+)$', line)
        if m and not current_section_title and result == []:
            title_text = m.group(1).replace('*', '')
            result.append(r'\title{' + title_text + r'}')
            result.append(r'\author{A researcher}')
            result.append(r'\date{\today}')
            result.append(r'\maketitle')
            result.append('')
            result.append(r'\begin{abstract}')
            continue

        # Section headers (## Chapter)
        m = re.match(r'^## (.+)$', line)
        if m:
            # Close abstract if open
            if result and not any(r in '\n'.join(result[-10:]) for r in ['\end{abstract}', r'\end{thebibliography}']):
                result.append(r'\end{abstract}')
                result.append('')

            section_text = m.group(1).replace('*', '')
            result.append(r'\section{' + section_text + r'}')
            result.append('')
            current_section_title = section_text
            i += 1
            continue

        # Subsection headers (### Title)
        m = re.match(r'^### (.+)$', line)
        if m:
            section_text = m.group(1).replace('*', '')
            result.append(r'\subsection{' + section_text + r'}')
            result.append('')
            i += 1
            continue

        # Sub-subsection (####)
        m = re.match(r'^#### (.+)$', line)
        if m:
            section_text = m.group(1).replace('*', '')
            result.append(r'\subsubsection{' + section_text + r'}')
            result.append('')
            i += 1
            continue

        # Table conversion
        if '|' in line and line.strip().startswith('|'):
            # Collect table block
            table_lines = []
            while i < len(lines) and ('|' in lines[i] and lines[i].strip().startswith('|')):
                table_lines.append(lines[i])
                i += 1
            # Convert table
            table_text = '\n'.join(table_lines)
            converted = convert_table(table_text)
            if converted:
                result.append(converted)
                result.append('')
            continue

        # Check if next line is a table separator
        if '|' in line and i + 1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i+1]):
            # Collect table block
            table_lines = []
            while i < len(lines) and ('|' in lines[i] and lines[i].strip().startswith('|')):
                table_lines.append(lines[i])
                i += 1
            table_text = '\n'.join(table_lines)
            converted = convert_table(table_text)
            if converted:
                result.append(converted)
                result.append('')
            continue

        # Bullet list
        m = re.match(r'^[-*]\s+(.+)$', line)
        if m and not line.startswith('---'):
            item_text = m.group(1)
            # Handle **bold** within bullet
            if '**' in item_text:
                item_text = re.sub(r'\*\*(.+?)\*\*', r'{\\textbf{\1}}', item_text)
            result.append(convert_list_item(item_text))
            i += 1
            continue

        # Numbered list (1., 2., etc.)
        m = re.match(r'^(\d+)\.\s+(.+)$', line)
        if m:
            num = m.group(1)
            text = m.group(2)
            if '**' in text:
                text = re.sub(r'\*\*(.+?)\*\*', r'{\\textbf{\1}}', text)
            result.append(r'\item[' + num + r'] ' + text)
            i += 1
            continue

        # Empty line
        if line.strip() == '':
            result.append('')
            i += 1
            continue

        # Regular text - process inline formatting
        # Replace [[N]] citations
        processed = re.sub(r'\[\[(\d+[a-z]?\.?)\]\]', r'\\cite{ref\1}', line)

        # Replace **bold**
        processed = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', processed)

        # Replace single *italic* (but not LaTeX math)
        # Be careful with italic - don't replace inside $...$
        processed = re.sub(r'(?<!\$)\*(.+?)\*(?!\$)', r'\\textit{\1}', processed)

        # Replace inline code `...`
        processed = re.sub(r'`(.+?)`', r'\\texttt{\1}', processed)

        result.append(processed)
        i += 1

    if in_quote:
        result.append(r'\end{quote}')

    if bib_entries and r'\end{thebibliography}' not in '\n'.join(result):
        result.append(r'\end{thebibliography}')

    return '\n'.join(result)


def generate_bib_entries(bib_map, tex_body):
    """Generate LaTeX bibitem entries for each citation."""
    entries = []
    for ref_id in sorted(bib_map.keys(), key=lambda x: (
        0 if x[:-1].isdigit() else 10,
        int(x[:-1]) if x[:-1].isdigit() else 99,
        x[-1] if len(x) > 1 and x[-1].isalpha() else 'z'
    )):
        ref_text = bib_map[ref_id]
        # Escape special chars for LaTeX
        ref_text = ref_text.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
        ref_text = ref_text.replace('_', '\\_').replace('$', '\\$').replace('{', '\\{').replace('}', '\\}')
        ref_text = ref_text.replace('^', '\\textasciicircum ').replace('~', '\\textasciitilde ')
        ref_text = ref_text.replace('\\', '\\textbackslash ').replace('{', '\\{').replace('}', '\\}')
        entries.append(r'\bibitem{ref' + ref_id + r'} ' + ref_text)
    return '\n'.join(entries)


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_markdown_to_latex.py <input.md> [output.tex]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Default output: same directory as input, name main-paper.tex
    if output_path is None:
        base = os.path.basename(input_path)
        name = os.path.splitext(base)[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{name}.tex")

    # Read markdown
    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to LaTeX body
    latex_body = convert_markdown_to_latex(md_text)

    # LaTeX preamble with XeLaTeX + Chinese support
    preamble = r'''\documentclass[12pt,a4paper]{article}
\usepackage{xeCJK}
\setCJKmainfont{Songti SC}
\setCJKsansfont{Heiti SC}
\setCJKmonofont{FangSong}
\setmainfont{Times New Roman}

\usepackage{amsmath, amssymb, amsthm}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=blue}
\usepackage{mathptmx}
\usepackage{indentfirst}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.5em}

\begin{document}
'''

    # Find and extract bibliography entries from the markdown
    bib_map = {}
    ref_pattern = re.compile(r'^\[(\d+[a-z]?)\]\s*(.+)$', re.MULTILINE)
    for m in ref_pattern.finditer(md_text):
        ref_id = m.group(1)
        ref_text = m.group(2)
        bib_map[ref_id] = ref_text

    # Generate bib items
    bib_items = generate_bib_entries(bib_map, latex_body)

    # Wrap everything together
    # The body might already have \begin{abstract} etc.
    # Check if body starts with abstract content
    full_tex = preamble

    # The body should already have \title, \author, \date, \maketitle, abstract
    # But let's make sure we have proper structure
    full_tex += latex_body + '\n'

    # Don't add duplicate thebibliography if already in body
    if r'\begin{thebibliography}' not in latex_body:
        full_tex += r'\begin{thebibliography}{99}\n' + bib_items + r'\n\end{thebibliography}\n'

    full_tex += r'\end{document}\n'

    # Write output
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_tex)

    print(f"Generated: {output_path}")
    print(f"Bibliography entries: {len(bib_map)}")

    # Check for citation patterns in body
    uncited = re.findall(r'\[\[(\d+[a-z]?)\]\]', md_text)
    print(f"Inline citations found: {len(uncited)}")


if __name__ == '__main__':
    main()
