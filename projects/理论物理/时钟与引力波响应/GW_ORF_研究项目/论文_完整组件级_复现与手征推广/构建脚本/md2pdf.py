#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown(含 $...$/$$...$$ 数学) -> PDF。
彻底剥离 MathJax \tag 产生的 100% 宽度 SVG 异常，确保 svglib 生成 100% 合规的 PDF 流。
行内上下标使用 ReportLab 原生 <sup>/<sub> HTML 标签。"""
import json, re, subprocess, sys, io, html

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Image, Table, TableStyle, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from svglib.svglib import svg2rlg
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
CJK = 'STSong-Light'

NODE = ['node', '/home/user/-orf/.build_pdf/render_math.js']
PAGE_W, PAGE_H = A4
ML, MR, MT, MB = 20*mm, 20*mm, 22*mm, 20*mm
USABLE_W = PAGE_W - ML - MR

def node_render(tex, display):
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
        return vb[2], vb[3]
    return (float(w.group(1)) if w else 10, float(h.group(1)) if h else 10)

def math_flowable_clean(tex):
    # 彻底提取并去除 \tag{...}，防止 MathJax 输出百分比 width="100%" 导致 svglib 损坏 PDF
    tags = re.findall(r'\\tag\{([^}]*)\}', tex)
    tex_clean = re.sub(r'\\tag\{[^}]*\}', '', tex).strip()
    tag_str = f"({tags[0]})" if tags else ""

    svg = node_render(tex_clean, True)
    Wv, Hv = _svg_size(svg)
    svg = re.sub(r'width="[\d\.]+ex"', f'width="{Wv:.3f}"', svg, count=1)
    svg = re.sub(r'height="[\d\.]+ex"', f'height="{Hv:.3f}"', svg, count=1)
    
    fn = f'/home/user/-orf/.build_pdf/eq_{_svg_counter[0]}.svg'
    _svg_counter[0] += 1
    open(fn, 'w', encoding='utf-8').write(svg)
    
    drawing = svg2rlg(fn)
    fontsize = 12.0
    scale = fontsize / 1000.0
    w_pt, h_pt = Wv * scale, Hv * scale
    
    if w_pt > USABLE_W:
        scale *= (USABLE_W / w_pt)
        w_pt, h_pt = USABLE_W, h_pt * (USABLE_W / w_pt)
        
    drawing.width = max(w_pt, 1)
    drawing.height = max(h_pt, 1)
    drawing.scale(scale, scale)
    drawing.hAlign = 'CENTER'

    if tag_str:
        num_style = ParagraphStyle('eqnum', fontName=CJK, fontSize=9.5, leading=12, alignment=TA_RIGHT)
        num_para = Paragraph(f"<font color=\"#444444\"><b>{tag_str}</b></font>", num_style)
        return [drawing, Spacer(1, 1), num_para]
    else:
        return [drawing]

def tex_to_inline(tex):
    """行内公式 -> ReportLab HTML <sup>/<sub> 精细转换。"""
    s = tex
    repls = [
        (r'\\rmone', 'one'), (r'\\rmtwo', 'two'), (r'\\GbLI', 'GbLI'), (r'\\SbLI', 'SbLI'), (r'\\PTA', 'PTA'),
        (r'\\uhat', 'û'), (r'\\vhat', 'v̂'), (r'\\shat', 'ŝ'), (r'\\nhat', 'n̂'), (r'\\dhat', 'd̂'),
        (r'\\thetahat', 'θ̂'), (r'\\phihat', 'φ̂'),
        (r'\\cu', 'c<sub>u</sub>'), (r'\\cv', 'c<sub>v</sub>'), (r'\\cg', 'c<sub>γ</sub>'), (r'\\Ei', 'Ei'),
        (r'\\mathrm\{([^}]*)\}', r'\1'), (r'\\text\{([^}]*)\}', r'\1'), (r'\\mathbf\{([^}]*)\}', r'\1'),
        (r'\\hat\{?([a-zA-Z])\}?', r'\1̂'), (r'\\tilde\{?([a-zA-Z])\}?', r'\1̃'), (r'\\bar\{?([a-zA-Z])\}?', r'\1̄'),
        (r'\\vec\{([^}]*)\}', r'\1'), (r'\\boldsymbol\{([^}]*)\}', r'\1'), (r'\\mathcal\{([^}]*)\}', r'\1'),
        (r'\\alpha', 'α'), (r'\\beta', 'β'), (r'\\gamma', 'γ'), (r'\\delta', 'δ'),
        (r'\\epsilon', 'ε'), (r'\\varepsilon', 'ε'), (r'\\theta', 'θ'), (r'\\phi', 'φ'), (r'\\zeta', 'ζ'),
        (r'\\sigma', 'σ'), (r'\\lambda', 'λ'), (r'\\mu', 'μ'), (r'\\pi', 'π'), (r'\\kappa', 'κ'),
        (r'\\Delta', 'Δ'), (r'\\Gamma', 'Γ'), (r'\\Sigma', 'Σ'), (r'\\Omega', 'Ω'),
        (r'\\times', '×'), (r'\\cdot', '·'), (r'\\cdots', '⋯'), (r'\\ldots', '…'),
        (r'\\infty', '∞'), (r'\\pm', '±'), (r'\\mp', '∓'), (r'\\neq', '≠'),
        (r'\\leq', '≤'), (r'\\geq', '≥'), (r'\\ll', '≪'), (r'\\gg', '≫'),
        (r'\\approx', '≈'), (r'\\equiv', '≡'), (r'\\sim', '∼'), (r'\\propto', '∝'),
        (r'\\rightarrow', '→'), (r'\\to', '→'), (r'\\Rightarrow', '⇒'), (r'\\leftrightarrow', '↔'),
        (r'\\langle', '⟨'), (r'\\rangle', '⟩'), (r'\\sqrt', '√'), (r'\\partial', '∂'),
        (r'\\,', ' '), (r'\\;', ' '), (r'\\!', ''), (r'\\:', ' '), (r'\\ ', ' '),
        (r'\\big', ''), (r'\\Big', ''), (r'\\left', ''), (r'\\right', ''),
        (r'\\underbrace\{([^}]*)\}_\{[^}]*\}', r'\1'),
    ]
    for a, b in repls:
        s = re.sub(a, b, s)

    s = re.sub(r'\^\{([^{}]*)\}', r'<sup>\1</sup>', s)
    s = re.sub(r'_\{([^{}]*)\}', r'<sub>\1</sub>', s)
    s = re.sub(r'\^([A-Za-z0-9+\-])', r'<sup>\1</sup>', s)
    s = re.sub(r'_([A-Za-z0-9+\-])', r'<sub>\1</sub>', s)
    s = re.sub(r'\\([a-zA-Z]+)', r'\1', s)
    s = s.replace('{', '').replace('}', '')
    return s

def prepare_inline(text):
    def repl(m):
        return tex_to_inline(m.group(1))
    text = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', repl, text)
    return text

def md_inline(text):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'&lt;sup&gt;(.*?)&lt;/sup&gt;', r'<sup>\1</sup>', text)
    text = re.sub(r'&lt;sub&gt;(.*?)&lt;/sub&gt;', r'<sub>\1</sub>', text)
    text = re.sub(r'&lt;img ([^&]*?)/&gt;', r'<img \1/>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+?)`', r'<font face="Courier">\1</font>', text)
    return text

def mkstyle(name, **kw):
    base = dict(fontName=CJK, fontSize=10.5, leading=16.5, textColor=colors.black,
                spaceAfter=5, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)

styles = {
    'h1': mkstyle('h1', fontSize=18, leading=24, spaceBefore=16, spaceAfter=10, textColor=colors.HexColor('#0b3d6b'), alignment=TA_CENTER),
    'h2': mkstyle('h2', fontSize=14, leading=19, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor('#11508a')),
    'h3': mkstyle('h3', fontSize=12, leading=17, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor('#1a5f9e')),
    'body': mkstyle('body', fontSize=10.5, leading=16.5, alignment=TA_JUSTIFY),
    'quote': mkstyle('quote', fontSize=10, leading=15, leftIndent=16, rightIndent=16, textColor=colors.HexColor('#333333'), backColor=colors.HexColor('#f7f9fa'), spaceBefore=6, spaceAfter=6),
    'code': mkstyle('code', fontName='Courier', fontSize=8.5, leading=11, backColor=colors.HexColor('#f2f3f5'), leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=6),
}

def parse(md):
    flow = []
    lines = md.split('\n')
    i = 0
    while i < len(lines):
        ln = lines[i]
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
            items = math_flowable_clean(tex.strip())
            for item in items:
                flow.append(item)
            flow.append(Spacer(1, 5))
            continue
        if ln.strip().startswith('```'):
            i += 1; code = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i += 1
            i += 1
            code_txt = html.escape('\n'.join(code)).replace('\n', '<br/>')
            flow.append(Paragraph(code_txt, styles['code']))
            continue
        if ln.strip().startswith('|') and i+1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                tbl.append(cells); i += 1
            header = tbl[0]; body = tbl[2:]
            def cell(c):
                c = prepare_inline(c)
                return Paragraph(md_inline(c), mkstyle('cell', fontSize=9.0, leading=13))
            data = [[cell(c) for c in header]] + [[cell(c) for c in row] for row in body]
            ncol = len(header)
            colw = USABLE_W / ncol
            t = Table(data, colWidths=[colw]*ncol, repeatRows=1)
            t.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), CJK),
                ('FONTSIZE', (0,0), (-1,-1), 9.0),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8f1f9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#a0b8d0')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ]))
            flow.append(Spacer(1, 4)); flow.append(t); flow.append(Spacer(1, 6))
            continue
        m = re.match(r'^(#{1,3})\s+(.*)', ln)
        if m:
            lvl = len(m.group(1)); txt = m.group(2).strip()
            flow.append(Paragraph(md_inline(prepare_inline(txt)), styles[f'h{lvl}']))
            i += 1; continue
        if ln.strip().startswith('>'):
            buf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i])); i += 1
            flow.append(Paragraph(md_inline(prepare_inline(' '.join(buf))), styles['quote']))
            continue
        if not ln.strip():
            i += 1; continue
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
                          title='手征（圆偏振）SGWB 重叠约化函数精确留数法解析推导与组件对比')
    frame = Frame(ML, MB, USABLE_W, PAGE_H - MT - MB, id='main')
    def footer(cv, d):
        cv.setFont(CJK, 9); cv.setFillColor(colors.HexColor('#555555'))
        cv.drawCentredString(PAGE_W / 2, 12 * mm, f'第 {d.page} 页')
        cv.setStrokeColor(colors.HexColor('#cccccc'))
        cv.setLineWidth(0.5)
        cv.line(ML, PAGE_H - 15 * mm, PAGE_W - MR, PAGE_H - 15 * mm)
        cv.setFont(CJK, 8)
        cv.drawString(ML, PAGE_H - 12 * mm, '手征 SGWB 重叠约化函数：精确留数法推广与组件级对比')
    doc.addPageTemplates([PageTemplate(id='all', frames=[frame], onPage=footer)])
    doc.build(story)
    print('PDF written:', pdf_path)

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
