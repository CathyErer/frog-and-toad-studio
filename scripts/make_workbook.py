#!/usr/bin/env python3
"""Make the two-page colour workbook (student + answer key .docx) for one story.

Usage:  python3 scripts/make_workbook.py <courseware_dir> [workbook.json]
Reads   <courseware_dir>/source/workbook.json (questions; format in references/workbook.md)
        <courseware_dir>/source/content.json  (the story text, used to check quotes and verbs)
        optional pictures: header picture (workbook.json "header_image"), assets/decor/*, assets/images/*
Writes  <courseware_dir>/../<Title> Workbook/NN - <Title> Workbook.docx  and  ... Workbook 答案版.docx
Then run scripts/to_pdf.py on that folder.
Needs:  pip install python-docx pillow
"""
import os, io, re, sys, json, glob
from PIL import Image
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

RED = RGBColor(0xC0, 0x00, 0x00); GRAY = RGBColor(0x6B, 0x5B, 0x4A)
GREEN = RGBColor(0x4F, 0x7A, 0x35); BROWN = RGBColor(0x7A, 0x4E, 0x24)
GREEN_HEX, BROWN_HEX, YELLOW_HEX = '4F7A35', '7A4E24', 'FFF1BF'
FONT = 'Arial'
PERMS = [[2, 4, 0, 3, 1], [3, 0, 4, 1, 2], [1, 3, 0, 4, 2], [4, 2, 1, 0, 3]]
SEQ_PERMS = [[2, 0, 3, 1], [1, 3, 0, 2], [3, 1, 0, 2], [2, 3, 1, 0]]
BANK_PERMS = [[3, 2, 0, 1], [1, 3, 0, 2], [2, 0, 3, 1]]

def img(path, crop=True, maxpx=900):
    im = Image.open(path).convert('RGBA')
    if crop and im.getchannel('A').getbbox(): im = im.crop(im.getchannel('A').getbbox())
    bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    im = bg.convert('RGB'); im.thumbnail((maxpx, maxpx)); size = im.size
    b = io.BytesIO(); im.save(b, 'JPEG', quality=88); b.seek(0); return b, size

def add_icon(p, path, h=0.3, maxw=0.55):
    b, (w, hh) = img(path, maxpx=300)
    if w / hh * h > maxw: p.add_run().add_picture(b, width=Inches(maxw))
    else: p.add_run().add_picture(b, height=Inches(h))

def run(p, text, size=13, bold=False, color=None, underline=False):
    r = p.add_run(text); f = r.font; f.name = FONT; f.size = Pt(size); f.bold = bold
    r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color: f.color.rgb = color
    if underline: f.underline = True
    return r

def para(c, after=4, before=0, align=None):
    p = c.add_paragraph(); pf = p.paragraph_format
    pf.space_after = Pt(after); pf.space_before = Pt(before)
    if align: p.alignment = align
    return p

def shade(cell, fill):
    sh = OxmlElement('w:shd')
    for k, v in (('val', 'clear'), ('color', 'auto'), ('fill', fill)): sh.set(qn('w:' + k), v)
    cell._element.get_or_add_tcPr().append(sh)

def borders(cell, on=True, sz=8, color=BROWN_HEX):
    tcPr = cell._element.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
    for e in ('top', 'left', 'bottom', 'right'):
        x = OxmlElement('w:' + e); x.set(qn('w:val'), 'single' if on else 'nil')
        x.set(qn('w:sz'), str(sz)); x.set(qn('w:color'), color); b.append(x)
    tcPr.append(b)

def table(doc, rows, widths):
    t = doc.add_table(rows=rows, cols=len(widths)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._element.tblPr.append(lay)
    for g, w in zip(t._element.tblGrid.findall(qn('w:gridCol')), widths): g.set(qn('w:w'), str(int(w * 1440)))
    for r in t.rows:
        for i, w in enumerate(widths):
            r.cells[i].width = Inches(w); borders(r.cells[i], False)
            r.cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            r.cells[i].paragraphs[0].paragraph_format.space_after = Pt(0)
    return t

def heading(doc, n, name, direction, icon=None):
    p = para(doc, after=3, before=9)
    r = run(p, f' {n} ', 13, True); run(p, f' {name}', 14, True, BROWN); run(p, '   ' + direction, 11.5, color=GRAY)
    if icon: run(p, '  '); add_icon(p, icon)
    pPr = p._element.get_or_add_pPr(); bd = OxmlElement('w:pBdr'); bt = OxmlElement('w:bottom')
    for k, v in (('val', 'single'), ('sz', '10'), ('space', '2'), ('color', GREEN_HEX)): bt.set(qn('w:' + k), v)
    bd.append(bt); pPr.append(bd)
    shd = OxmlElement('w:shd')
    for k, v in (('val', 'clear'), ('color', 'auto'), ('fill', GREEN_HEX)): shd.set(qn('w:' + k), v)
    r._element.rPr.append(shd); r.font.color.rgb = RGBColor(255, 255, 255)

def blank(p, ans, key, n=12, size=13):
    if key: run(p, ' ' + ans + ' ', size, True, RED, True)
    else: run(p, '_' * n, size)

def choices(p, opts, correct, key, size=13):
    for i, o in enumerate(opts):
        if i: run(p, '      ', size)
        if key and i == correct: run(p, o, size, True, RED, True)
        else: run(p, o, size, True)

def numbox(cell, n, key):
    borders(cell, True, 12)
    p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if key: run(p, str(n), 15, True, RED)

def find_pic(cw, kind, name=None):
    pats = [os.path.join(cw, 'assets', kind, '*'), os.path.join(cw, 'assets', 'web', kind, '*')]
    files = sorted(f for p in pats for f in glob.glob(p) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')))
    if name is None: return files
    for f in files:
        if os.path.splitext(os.path.basename(f))[0] == name: return f
    return None

def build(c, idx, cw, key, path):
    num = int(c.get('num', 1))
    decor = [f for f in find_pic(cw, 'decor') if 'peek' not in os.path.basename(f)]
    seen = set(); decor = [f for f in decor if not (os.path.splitext(os.path.basename(f))[0] in seen or seen.add(os.path.splitext(os.path.basename(f))[0]))]
    if c.get('decor_order'): decor = [p for p in (find_pic(cw, 'decor', n) for n in c['decor_order']) if p]
    ico = lambda i: decor[i] if i < len(decor) else None
    hdr = c.get('header_image')
    if hdr and not os.path.isabs(hdr): hdr = os.path.join(cw, hdr)
    if hdr and not os.path.exists(hdr): hdr = None
    SP = c.get('speakers', ['Frog', 'Toad'])
    doc = Document(); s = doc.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    s.top_margin = s.bottom_margin = Inches(0.55); s.left_margin = s.right_margin = Inches(0.75)
    doc.styles['Normal'].font.name = FONT
    doc._body.clear_content()

    # ---------- 页眉 ----------
    t = table(doc, 1, [5.2, 1.8] if hdr else [7.0, 0.01]); L, R = t.rows[0].cells
    p = L.paragraphs[0]; run(p, c['title'], 30, True, GREEN)
    if key: run(p, '   ANSWER KEY', 15, True, RED)
    p = para(L, after=6); run(p, f"{c['bname']}  ·  Story {num}", 11.5, color=GRAY)
    p = para(L, after=0); run(p, 'Name: __________________     Date: ____________', 12)
    if hdr:
        p = R.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.add_run().add_picture(img(hdr)[0], width=Inches(1.7))

    # ---------- 1 Words ----------
    heading(doc, 1, 'Words', 'Draw a line from the word to its meaning.', ico(0))
    order = PERMS[idx % len(PERMS)]
    t = table(doc, 5, [2.0, 0.9, 4.1])
    for i, (w, _) in enumerate(c['words']):
        cells = t.rows[i].cells; t.rows[i].height = Inches(0.36)
        p = cells[0].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run(p, w, 14, True); run(p, '   ●', 10, color=GREEN)
        p = cells[2].paragraphs[0]; run(p, '●   ', 10, color=GREEN); run(p, c['words'][order[i]][1], 13)
    if key:
        p = para(doc, after=0, before=4)
        run(p, 'Key:  ' + ';  '.join(f'{w} = {m}' for w, m in c['words']), 10, True, RED)

    # ---------- 2 Key Details ----------
    heading(doc, 2, 'Key Details', 'Circle the right answer.')
    for i, (q, opts, a) in enumerate(c['details']):
        p = para(doc, after=5); run(p, f'{i+1}.  {q}      '); choices(p, opts, a, key)

    # ---------- 3 Sequence ----------
    if c.get('pics'):
        heading(doc, 3, 'Sequence', 'What happened first? Write 1, 2, 3, 4 in the boxes.')
        t = table(doc, 2, [1.75] * 4); t.rows[1].height = Inches(0.42); t.rows[1].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        for i, (name, n) in enumerate(c['pics']):
            p = t.rows[0].cells[i].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(3)
            p.add_run().add_picture(img(find_pic(cw, 'images', name), crop=False, maxpx=700)[0], width=Inches(1.62))
            numbox(t.rows[1].cells[i], n, key)
    else:
        heading(doc, 3, 'Sequence', 'What happened first? Write 1, 2, 3, 4 in the boxes.')
        sp = SEQ_PERMS[idx % len(SEQ_PERMS)]
        t = table(doc, 4, [0.55, 0.15, 6.3])
        for i, j in enumerate(sp):
            t.rows[i].height = Inches(0.4); t.rows[i].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            numbox(t.rows[i].cells[0], j + 1, key)
            run(t.rows[i].cells[2].paragraphs[0], c['seq'][j], 13)

    p = para(doc, after=6, before=10); run(p, 'Now retell the story. Use the words in the box.', 11.5, color=GRAY)
    t = table(doc, 1, [5.0]); cell = t.rows[0].cells[0]; borders(cell, True, 8); shade(cell, YELLOW_HEX)
    p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(3)
    bp = BANK_PERMS[idx % len(BANK_PERMS)]
    run(p, '        '.join(c['retell'][j][1] for j in bp), 13, True)
    for i, (a, w, b) in enumerate(c['retell']):
        p = para(doc, after=10, before=9 if i == 0 else 0); run(p, a); blank(p, w, key); run(p, b)

    # ================= 第 2 页 =================
    p = para(doc, after=0); p.paragraph_format.page_break_before = True
    run(p, c['title'], 16, True, GREEN); run(p, '   ·   page 2   ', 11, color=GRAY)
    if ico(3): add_icon(p, ico(3), h=0.42, maxw=0.8)
    if key: run(p, '   ANSWER KEY', 12, True, RED)

    # ---------- 4 Character ----------
    heading(doc, 4, 'Character', f'Who said it? Circle {SP[0]} or {SP[1]}.')
    t = table(doc, 5, [4.6, 2.4])
    for i, (q, a) in enumerate(c['quotes']):
        t.rows[i].height = Inches(0.36); cells = t.rows[i].cells
        run(cells[0].paragraphs[0], f'{i+1}.  {q}', 13)
        choices(cells[1].paragraphs[0], SP, a, key)

    # ---------- 5 Think ----------
    heading(doc, 5, 'Think', 'Read, think, and write.', ico(1))
    for i, it in enumerate(c['think']):
        p = para(doc, after=3 if it.get('fr') else 10, before=0 if i == 0 else 4)
        run(p, f"{i+1}.  {it['q']}", 13, True)
        if it.get('ch'): run(p, '      '); choices(p, it['ch'][0], it['ch'][1], key)
        if it.get('fr'):
            a, w, b = it['fr']; p = para(doc, after=6, before=4); run(p, '     ' + a); blank(p, w, key, 14); run(p, b)

    # ---------- 6 Theme & Me ----------
    heading(doc, 6, 'Theme & Me', 'What does the story teach us?', ico(2))
    a, w1, m, w2, b = c['theme']
    bank = [w2, w1] if idx % 2 == 0 else [w1, w2]
    p = para(doc, after=6, before=3); run(p, 'Word box:   ', 11.5, color=GRAY); run(p, '      '.join(bank), 13, True, BROWN)
    p = para(doc, after=10); run(p, a); blank(p, w1, key); run(p, m); blank(p, w2, key); run(p, b)
    prompt, pre, sample, post = c['draw']
    p = para(doc, after=4); run(p, prompt, 13, True)
    t = table(doc, 1, [7.0]); cell = t.rows[0].cells[0]; borders(cell, True, 12)
    t.rows[0].height = Inches(3.2); t.rows[0].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    if key: run(cell.paragraphs[0], ' Drawings will vary.', 11, True, RED)
    p = para(doc, after=0, before=12); run(p, pre)
    if key: run(p, f' (answers will vary, e.g. {sample}) ', 12, True, RED, True)
    else: run(p, '_' * (14 if len(pre) + len(post) > 40 else 30))
    run(p, post)
    doc.save(path)

def norm(s): return re.sub(r'[“”"]', '', s).replace('’', "'").strip()

def validate(c, cw):
    d = json.load(open(os.path.join(cw, 'source', 'content.json')))
    text = norm(' '.join(l['text'] for s in d['scenes'] for l in s['lines']))
    bad = []
    for q, _ in c['quotes']:
        core = norm(q).rstrip('.!?,')
        if core not in text: bad.append('QUOTE: ' + q)
    for a, w, b in c['retell']:
        if not re.search(r'\b' + re.escape(w) + r'\b', text): bad.append('RETELL word not in story: ' + w)
    assert len(c['words']) == 5 and len(c['details']) == 3 and len(c['seq']) == 4 and len(c['quotes']) == 5
    return bad

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    cw = os.path.abspath(sys.argv[1])
    data = sys.argv[2] if len(sys.argv) > 2 else os.path.join(cw, 'source', 'workbook.json')
    c = json.load(open(data, encoding='utf-8'))
    for k in ('words', 'details', 'retell', 'quotes', 'think'):
        c[k] = [tuple(x) if isinstance(x, list) else x for x in c[k]]
    c['details'] = [(q, o, a) for q, o, a in c['details']]
    bad = validate(c, cw)
    for b in bad: print('!!', b)
    num = int(c.get('num', 1))
    out = os.path.join(os.path.dirname(cw), f"{c['title']} Workbook"); os.makedirs(out, exist_ok=True)
    base = os.path.join(out, f"{num:02d} - {c['title']} Workbook")
    build(c, 0, cw, False, base + '.docx'); build(c, 0, cw, True, base + ' 答案版.docx')
    print('wrote', base + '.docx', 'and the answer key')
    sys.exit(1 if bad else 0)
