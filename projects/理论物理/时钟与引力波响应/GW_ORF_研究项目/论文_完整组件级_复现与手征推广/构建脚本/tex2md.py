#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paper.tex -> Markdown (全自动建立章节/公式/文献编号，无冗余文字)。"""
import re, sys

def convert(tex):
    t = tex
    t = re.sub(r'(?m)(?<!\\)%.*$', '', t)
    t = t.split('\\begin{document}', 1)[1] if '\\begin{document}' in t else t
    t = t.split('\\end{document}')[0]

    # ========== 1) 预建立章节、公式与文献编号 ==========
    eq_labels = {}
    sec_labels = {}
    cite_labels = {}

    # 预扫描章节编号
    sec_num = [0, 0, 0]
    for line in t.split('\n'):
        m_sec = re.match(r'\\section\{([^}]*)\}', line)
        if m_sec:
            sec_num[0] += 1; sec_num[1] = 0; sec_num[2] = 0
            lbl = re.search(r'\\label\{([^}]*)\}', line)
            if lbl: sec_labels[lbl.group(1)] = str(sec_num[0])
            continue
        m_subsec = re.match(r'\\subsection\{([^}]*)\}', line)
        if m_subsec:
            sec_num[1] += 1; sec_num[2] = 0
            lbl = re.search(r'\\label\{([^}]*)\}', line)
            if lbl: sec_labels[lbl.group(1)] = f"{sec_num[0]}.{sec_num[1]}"
            continue

    # 预扫描文献
    if '\\bibitem' in t:
        bibs = re.findall(r'\\bibitem\{([^}]*)\}', t)
        for idx, b in enumerate(bibs):
            cite_labels[b] = str(idx + 1)

    # 预扫描公式编号
    eq_count = [1]
    math_store = []
    def stow(math):
        math_store.append(math)
        return f'@@MATH{len(math_store)-1}@@'

    def process_display(m):
        env, body = m.group(1), m.group(2)
        labels = re.findall(r'\\label\{([^}]*)\}', body)
        body_clean = re.sub(r'\\label\{[^}]*\}', '', body).strip()
        body_clean = body_clean.replace('\\notag', '').replace('\\nonumber', '')
        
        c_num = eq_count[0]
        eq_count[0] += 1
        for lbl in labels:
            eq_labels[lbl] = str(c_num)

        tag_str = f'\\tag{{{c_num}}}'
        if env.startswith('align'):
            body_clean = '\\begin{aligned}' + body_clean + '\\end{aligned} ' + tag_str
        else:
            body_clean = body_clean + ' ' + tag_str

        return stow('\n$$\n' + body_clean + '\n$$\n')

    t = re.sub(r'\\begin\{(equation\*?|align\*?|eqnarray\*?)\}(.*?)\\end\{\1\}', process_display, t, flags=re.S)
    t = re.sub(r'\\\[(.*?)\\\]', lambda m: stow('\n$$\n' + m.group(1).strip() + '\n$$\n'), t, flags=re.S)

    # 行内数学中的显式分式改为 display 数学，避免挤压
    def fix_inline_frac(m):
        mbody = m.group(1)
        if r'\frac' in mbody or r'\oint' in mbody or r'\sum' in mbody:
            return stow('\n$$\n' + mbody + '\n$$\n')
        return stow('$' + mbody + '$')

    t = re.sub(r'\\\((.*?)\\\)', fix_inline_frac, t, flags=re.S)
    t = re.sub(r'\$([^$]+)\$', fix_inline_frac, t)

    # ========== 2) 替换交叉引用 (纯数字，无多余词) ==========
    # 替换 式~\eqref{eq:foo} 或 \eqref{eq:foo}
    t = re.sub(r'式\s*~?\\eqref\{([^}]*)\}', lambda m: f"式 ({eq_labels.get(m.group(1), m.group(1))})", t)
    t = re.sub(r'\\eqref\{([^}]*)\}', lambda m: f"({eq_labels.get(m.group(1), m.group(1))})", t)

    # 替换 \ref{sec:foo}
    t = re.sub(r'\\ref\{([^}]*)\}', lambda m: sec_labels.get(m.group(1), eq_labels.get(m.group(1), m.group(1))), t)

    # 替换 \cite{foo}
    def repl_cite(m):
        lbls = m.group(1).split(',')
        nums = [cite_labels.get(l.strip(), l.strip()) for l in lbls]
        return f"[{', '.join(nums)}]"
    t = re.sub(r'\\cite\{([^}]*)\}', repl_cite, t)

    # ========== 3) 章节与结构清理 ==========
    t = re.sub(r'\\title\{([^}]*)\}', lambda m: '# ' + m.group(1) + '\n', t)
    t = re.sub(r'\\author\{([^}]*)\}', lambda m: '\n*' + m.group(1) + '*\n', t)
    t = re.sub(r'\\affiliation\{([^}]*)\}', lambda m: '*' + m.group(1) + '*\n', t)
    t = re.sub(r'\\date\{[^}]*\}', '', t)
    t = t.replace('\\maketitle', '')
    t = t.replace('\\begin{abstract}', '\n> **摘要**\n>\n> ').replace('\\end{abstract}', '\n')
    t = t.replace('\\begin{acknowledgments}', '\n## 致谢\n').replace('\\end{acknowledgments}', '')
    t = t.replace('\\appendix', '\n# 附录\n')

    # 章节标题（去除内部 \label）
    def clean_sec_title(m, prefix):
        title = re.sub(r'\\label\{[^}]*\}', '', m.group(1)).strip()
        return f"\n{prefix} {title}\n"

    t = re.sub(r'\\section\{([^}]*)\}', lambda m: clean_sec_title(m, '##'), t)
    t = re.sub(r'\\subsection\{([^}]*)\}', lambda m: clean_sec_title(m, '###'), t)
    t = re.sub(r'\\subsubsection\{([^}]*)\}', lambda m: clean_sec_title(m, '####'), t)
    t = re.sub(r'\\paragraph\{([^}]*)\}', lambda m: '\n**' + m.group(1) + '** ', t)

    # 参考文献列表
    if '\\bibitem' in t:
        head = t.split('\\bibitem')[0]
        bibs = re.findall(r'\\bibitem\{[^}]*\}(.*?)(?=\\bibitem|\\end\{thebibliography\})', t, flags=re.S)
        out = '\n## 参考文献\n\n'
        for i, b in enumerate(bibs):
            b = re.sub(r'\\[a-zA-Z]+\*?', '', b)
            b = b.replace('{', '').replace('}', '').replace('~', ' ').replace('\\\\', ' ')
            b = re.sub(r'\s+', ' ', b).strip()
            out += f"{i+1}. {b}\n\n"
        t = head + out

    # 表格解析
    t = conv_tables(t)
    t = re.sub(r'\\begin\{table\*?\}|\\end\{table\*?\}', '', t)
    t = re.sub(r'\\caption\{([^}]*)\}', lambda m: '\n**' + m.group(1) + '**\n', t)

    # 列表
    t = t.replace('\\begin{enumerate}', '').replace('\\end{enumerate}', '')
    t = t.replace('\\begin{itemize}', '').replace('\\end{itemize}', '')
    t = re.sub(r'\\item\s*', '\n- ', t)

    # 清理残留文本宏
    t = re.sub(r'\\url\{([^}]*)\}', r'\1', t)
    t = re.sub(r'\\emph\{([^}]*)\}', r'*\1*', t)
    t = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', t)
    t = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', t)
    t = re.sub(r'\\texttt\{([^}]*)\}', r'`\1`', t)
    t = t.replace('\\\\', '  \n')
    t = re.sub(r'\\noindent\s*', '', t)
    t = re.sub(r'\\begin\{[^}]*\}|\\end\{[^}]*\}', '', t)
    t = re.sub(r'\\[a-zA-Z]+\*?', '', t)
    for _ in range(3):
        t = re.sub(r'(?<!\\)\{([^{}]*)\}', r'\1', t)

    # ========== 4) 还原数学块 ==========
    def restore(m):
        return math_store[int(m.group(1))]
    t = re.sub(r'@@MATH(\d+)@@', restore, t)

    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip() + '\n'

def conv_tables(t):
    def one_table(m):
        block = m.group(0)
        cap = re.search(r'\\caption\{([^}]*)\}', block)
        rows = re.search(r'\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}', block, re.S)
        if not rows: return ''
        lines = [ln.strip() for ln in rows.group(1).split('\\\\') if ln.strip()]
        md = []
        for idx, ln in enumerate(lines):
            cells = [re.sub(r'\s+', ' ', c.strip()) for c in re.split(r'&', ln)]
            md.append('| ' + ' | '.join(cells) + ' |')
            if idx == 0:
                md.append('|' + '---|' * len(cells))
        captxt = ('\n\n**' + cap.group(1) + '**\n\n') if cap else '\n\n'
        return captxt + '\n'.join(md) + '\n\n'
    return re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', one_table, t, flags=re.S)

if __name__ == '__main__':
    tex = open(sys.argv[1], encoding='utf-8').read()
    md = convert(tex)
    open(sys.argv[2], 'w', encoding='utf-8').write(md)
    print('wrote', sys.argv[2], len(md), 'chars,', md.count('$$') // 2, 'display eqs')
