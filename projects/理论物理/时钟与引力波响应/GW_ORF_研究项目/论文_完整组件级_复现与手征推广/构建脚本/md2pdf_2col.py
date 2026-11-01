#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown(含 $...$/$$...$$ 数学) -> PDF。
数学用 Node + mathjax-full 服务端渲染为 SVG，再用 svglib 转 reportlab drawing。
中文用 reportlab 内置 Adobe CID 字体 STSong-Light（无需外部字体文件）。"""
import json, re, subprocess, sys, io, html

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Image, Table, TableStyle, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from svglib.svglib import svg2rlg
from reportlab.lib.enums import TA_LEFT, TA_CENTER

pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
CJK = 'STSong-Light'

NODE = ['node', '/home/user/-orf/.build_pdf/render_math.js']
PAGE_W, PAGE_H = A4
ML, MR, MT, MB = 15*mm, 15*mm, 18*mm, 16*mm
GUTTER = 7*mm
USABLE_W = (PAGE_W - ML - MR - GUTTER)/2.0   # 单栏宽

_proc = None
def node_render(tex, display):
    global _proc
    payload = json.dumps({'mode': 'display' if display else 'inline', 'tex': tex})
    r = subprocess.run(NODE, input=payload.encode('utf-8'),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='/home/user/-orf/.build_pdf')
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode('utf-8', 'replace')[:2000] + '\n')
        raise RuntimeError('math render failed: ' + tex[:80])
    return r.stdout.decode('utf-8')

_svg_counter = [0]
def _svg_size(svg):
    mw = re.search(r'viewBox="([\d\.\s-]+)"', svg)
    w = re.search(r'width="([\d\.]+)ex"', svg)
    h = re.search(r'height="([\d\.]+)ex"', svg)
    if mw:
        vb = [float(x) for x in mw.group(1).split()]
        return vb[2], vb[3]  # viewbox width,height in svg units (ex-scaled ~ pixels at 60dpi)
    return (float(w.group(1)) if w else 10, float(h.group(1)) if h else 10)

def math_flowable(tex, display):
    _is_full = '@@FULLWIDTH@@' in tex
    tex = tex.replace('@@FULLWIDTH@@','').replace('@@/FULLWIDTH@@','')
    if display:
        # \tag 必须在 aligned 环境外：抽出编号，放到 \end{aligned} 之后（或公式末尾）
        tags = re.findall(r'\\tag\{([^}]*)\}', tex)
        tex = re.sub(r'\\tag\{[^}]*\}', '', tex)
        if tags:
            tagtxt = ' '.join(r'\\tag{%s}' % t for t in tags)
            if r'\end{aligned}' in tex:
                tex = tex.replace(r'\end{aligned}', r'\end{aligned}' + tagtxt, 1)
            else:
                tex = tex + tagtxt
    svg = node_render(tex, display)
    Wv, Hv = _svg_size(svg)
    svg = re.sub(r'width="[\d\.]+ex"', f'width="{Wv:.3f}"', svg, count=1)
    svg = re.sub(r'height="[\d\.]+ex"', f'height="{Hv:.3f}"', svg, count=1)
    fn = f'/home/user/-orf/.build_pdf/eq_{_svg_counter[0]}.svg'
    _svg_counter[0] += 1
    open(fn, 'w', encoding='utf-8').write(svg)
    drawing = svg2rlg(fn)
    W, H = Wv, Hv
    fontsize = 12.5 if display else 10.5
    scale = fontsize/1000.0  # MathJax viewBox: 1em≈1000 单位
    w_pt, h_pt = W*scale, H*scale
    full_page_w = PAGE_W - ML - MR
    if display and w_pt > USABLE_W:
        if getattr(drawing, '_full', False):
            target = full_page_w
        else:
            target = USABLE_W
        if w_pt > target:
            k = target/w_pt
            scale *= k; w_pt, h_pt = target, h_pt*k
    drawing.width = max(w_pt,1)
    drawing.height = max(h_pt,1)
    drawing.scale(scale, scale)
    if display:
        drawing.hAlign = 'CENTER'
    if _is_full: drawing._full = True
    return drawing

# ---------- 行内数学处理：用占位符把 <svg/> 流与文字混排 ----------
# reportlab 不支持行内图。行内公式用 <img .../> 标签（Paragraph 支持 <img>）。
def tex_to_inline(tex):
    """行内公式 -> 可读 Unicode 近似（PDF 正文用；显示公式另行 SVG 渲染）。"""
    s = tex
    repls = [
        (r'\\mathrm\{([^}]*)\}', r'\1'), (r'\\text\{([^}]*)\}', r'\1'),
        (r'\\hat\{?([a-zA-Z])\}?', r'\1̂'), (r'\\tilde\{?([a-zA-Z])\}?', r'\1̃'),
        (r'\\bar\{?([a-zA-Z])\}?', r'\1̄'), (r'\\vec\{([^}]*)\}', r'\1'),
        (r'\\boldsymbol\{([^}]*)\}', r'\1'),
        (r'\\alpha', 'α'), (r'\\beta', 'β'), (r'\\gamma', 'γ'), (r'\\delta', 'δ'),
        (r'\\epsilon', 'ε'), (r'\\varepsilon', 'ε'), (r'\\theta', 'θ'), (r'\\phi', 'φ'),
        (r'\\sigma', 'σ'), (r'\\lambda', 'λ'), (r'\\mu', 'μ'), (r'\\pi', 'π'),
        (r'\\Delta', 'Δ'), (r'\\Gamma', 'Γ'), (r'\\Sigma', 'Σ'), (r'\\Omega', 'Ω'),
        (r'\\times', '×'), (r'\\cdot', '·'), (r'\\cdots', '⋯'), (r'\\ldots', '…'),
        (r'\\infty', '∞'), (r'\\pm', '±'), (r'\\mp', '∓'), (r'\\neq', '≠'),
        (r'\\leq', '≤'), (r'\\geq', '≥'), (r'\\ll', '≪'), (r'\\gg', '≫'),
        (r'\\approx', '≈'), (r'\\equiv', '≡'), (r'\\sim', '∼'), (r'\\propto', '∝'),
        (r'\\rightarrow', '→'), (r'\\to', '→'), (r'\\Rightarrow', '⇒'), (r'\\leftrightarrow', '↔'),
        (r'\\langle', '⟨'), (r'\\rangle', '⟩'), (r'\\sqrt', '√'),
        (r'\\,', ' '), (r'\\;', ' '), (r'\\!', ''), (r'\\:', ' '), (r'\\ ', ' '),
        (r'\\big', ''), (r'\\Big', ''), (r'\\left', ''), (r'\\right', ''),
        (r'\\underbrace\{([^}]*)\}_\{[^}]*\}', r'\1'),
    ]
    for a,b in repls:
        s = re.sub(a,b,s)
    # 简单上下标：^{...} _{...}
    s = re.sub(r'\^\{([^{}]*)\}', lambda m: to_sup(m.group(1)), s)
    s = re.sub(r'_\{([^{}]*)\}', lambda m: to_sub(m.group(1)), s)
    s = re.sub(r'\^([A-Za-z0-9+\-])', lambda m: to_sup(m.group(1)), s)
    s = re.sub(r'_([A-Za-z0-9+\-])', lambda m: to_sub(m.group(1)), s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)  # 去掉残余命令名
    s = s.replace('{','').replace('}','')
    return s

_SUP = str.maketrans('0123456789+-=()ABDEGHIJKLMNOPRTUVWabcdefghijklmnoprstuvwxyz',
                     '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ')
_SUB = str.maketrans('0123456789+-=()aeoxhklmnpstuv',
                     '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜᵤᵥ')
def to_sup(x): return x.translate(_SUP)
def to_sub(x): return x.translate(_SUB)

_inline_imgs = []
def prepare_inline(text):
    def repl(m):
        return tex_to_inline(m.group(1))
    text = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', repl, text)
    return text

def md_inline(text):
    # 转义 reportlab 标签特殊字符，但保留我们自己生成的 <img>
    # 先处理粗体 **..** 和斜体
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # <img ...> 被转义了，需要还原
    text = re.sub(r'&lt;img ([^&]*?)/&gt;', r'<img \1/>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+?)`', r'<font face="Courier">\1</font>', text)
    return text

# 样式
def mkstyle(name, **kw):
    base = dict(fontName=CJK, fontSize=10.5, leading=16, textColor=colors.black,
                spaceAfter=5, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)

styles = {
    'h1': mkstyle('h1', fontSize=17, leading=23, spaceBefore=14, spaceAfter=9, textColor=colors.HexColor('#0b3d6b')),
    'h2': mkstyle('h2', fontSize=14, leading=19, spaceBefore=11, spaceAfter=7, textColor=colors.HexColor('#11508a')),
    'h3': mkstyle('h3', fontSize=12, leading=17, spaceBefore=8, spaceAfter=5, textColor=colors.HexColor('#1a5f9e')),
    'body': mkstyle('body', fontSize=10.5, leading=16.5),
    'quote': mkstyle('quote', fontSize=10, leading=15, leftIndent=14, textColor=colors.HexColor('#444444')),
    'code': mkstyle('code', fontName='Courier', fontSize=8.4, leading=11, backColor=colors.HexColor('#f2f3f5'),
                    leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=6),
}

def parse(md):
    flow = []
    lines = md.split('\n')
    i = 0
    while i < len(lines):
        ln = lines[i]
        # 显示数学 $$...$$ 或 \[ ... \] 或 fenced
        if ln.strip().startswith('$$'):
            buf = [ln.strip()[2:]]
            if ln.strip().endswith('$$') and len(ln.strip()) > 2:
                tex = ln.strip()[2:-2]
                i += 1
            else:
                i += 1
                while i < len(lines) and '$$' not in lines[i]:
                    buf.append(lines[i]); i += 1
                if i < len(lines):
                    buf.append(lines[i].split('$$')[0]); i += 1
                tex = '\n'.join(buf)
            flow.append(Spacer(1, 3))
            flow.append(math_flowable(tex.strip(), True))
            flow.append(Spacer(1, 6))
            continue
        # 代码块
        if ln.strip().startswith('```'):
            i += 1; code = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i += 1
            i += 1
            code_txt = html.escape('\n'.join(code)).replace('\n', '<br/>')
            flow.append(Paragraph(code_txt, styles['code']))
            continue
        # 表格 | ... |
        if ln.strip().startswith('|') and i+1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                tbl.append(cells); i += 1
            # 去掉分隔行 tbl[1]
            header = tbl[0]; body = tbl[2:]
            def cell(c):
                c = prepare_inline(c)
                return Paragraph(md_inline(c), mkstyle('cell', fontSize=8.6, leading=12))
            data = [[cell(c) for c in header]] + [[cell(c) for c in row] for row in body]
            ncol = len(header)
            colw = USABLE_W / ncol  # 单栏宽（双栏）
            t = Table(data, colWidths=[colw]*ncol, repeatRows=1)
            t.setStyle(TableStyle([
                ('FONTNAME',(0,0),(-1,-1),CJK),
                ('FONTSIZE',(0,0),(-1,-1),8.6),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce8f5')),
                ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#9db4cc')),
                ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
                ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
            ]))
            flow.append(Spacer(1,3)); flow.append(t); flow.append(Spacer(1,7))
            continue
        # 标题
        m = re.match(r'^(#{1,3})\s+(.*)', ln)
        if m:
            lvl = len(m.group(1)); txt = m.group(2).strip()
            flow.append(Paragraph(md_inline(prepare_inline(txt)), styles[f'h{lvl}']))
            i += 1; continue
        # 引用
        if ln.strip().startswith('>'):
            buf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i])); i += 1
            flow.append(Paragraph(md_inline(prepare_inline(' '.join(buf))), styles['quote']))
            continue
        # 空行
        if not ln.strip():
            i += 1; continue
        # 列表项
        if re.match(r'^\s*[-*]\s+', ln):
            txt = re.sub(r'^\s*[-*]\s+', '• ', ln)
            flow.append(Paragraph(md_inline(prepare_inline(txt)),
                                  mkstyle('li', leftIndent=12, spaceAfter=3, fontSize=10.5, leading=16)))
            i += 1; continue
        if re.match(r'^\s*\d+\.\s+', ln):
            txt = re.sub(r'^(\s*)(\d+)\.\s+', r'\1\2. ', ln)
            flow.append(Paragraph(md_inline(prepare_inline(txt)),
                                  mkstyle('li', leftIndent=12, spaceAfter=3, fontSize=10.5, leading=16)))
            i += 1; continue
        # 普通段落（合并连续行）
        buf = [ln]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,3}\s|\s*[-*]\s|\s*\d+\.\s|>|```|\$\$|\|)', lines[i]):
            buf.append(lines[i]); i += 1
        para = ' '.join(b.strip() for b in buf)
        flow.append(Paragraph(md_inline(prepare_inline(para)), styles['body']))
    return flow

def build(md_path, pdf_path):
    md = open(md_path, encoding='utf-8').read()
    story = parse(md)
    doc = BaseDocTemplate(pdf_path, pagesize=A4,
                          leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
                          title='ORF 精确留数法：复现与手征推广')
    colw = USABLE_W
    fL = Frame(ML, MB, colw, PAGE_H-MT-MB, id='L', leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    fR = Frame(ML+colw+GUTTER, MB, colw, PAGE_H-MT-MB, id='R', leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    def footer(cv, d):
        cv.setFont(CJK, 8); cv.setFillColor(colors.grey)
        cv.drawCentredString(PAGE_W/2, 9*mm, f'- {d.page} -')
        cv.setLineWidth(0.3); cv.setStrokeColor(colors.HexColor('#888888'))
        cv.line(ML, PAGE_H-13*mm, PAGE_W-MR, PAGE_H-13*mm)
    doc.addPageTemplates([PageTemplate(id='all', frames=[fL,fR], onPage=footer)])
    doc.build(story)
    print('PDF written:', pdf_path)

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
