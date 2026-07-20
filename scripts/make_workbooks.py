#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Frog and Toad Workbook generator (student version + answer key).

Usage: copy this script next to your working files, edit/add config dicts
at the bottom, run it. One config -> two .docx (Workbook + 答案版), ONE page each.

Verify page count after generating:
  soffice --headless --convert-to pdf --outdir /tmp/wb "<file>.docx"
  python3 -c "import pypdfium2 as p; print(len(p.PdfDocument('/tmp/wb/<file>.pdf')))"

House rules baked in:
- Letter size, 0.5in top/bottom + 1.0in side margins, Arial everywhere (incl. eastAsia)
- Part 1 story-map table: FIXED layout, columns 4380/600/4380 twips,
  cue column shaded F6EAD8, answer column E9EDF5, arrow middle column
- Answer key: answers red CC0000 + bold + underline; title gets " ANSWER KEY"
  in red and a right-tab "Lesson N"; NO emoji anywhere in docx
- 6 rows in the story map, 6-word word bank, moral has exactly 2 blanks
- Every cue quote must be VERBATIM from the book
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

RED = RGBColor(0xCC, 0x00, 0x00)
FONT = "Arial"

def set_font(run, size, bold=False, red=False):
    run.font.name = FONT
    rF = run._element.rPr.get_or_add_rFonts()
    rF.set(qn('w:ascii'), FONT); rF.set(qn('w:hAnsi'), FONT); rF.set(qn('w:eastAsia'), FONT)
    run.font.size = Pt(size)
    run.font.bold = bold
    if red:
        run.font.color.rgb = RED
        run.font.bold = True
        run.font.underline = True

def add_borders(tbl, sz=8):
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single'); el.set(qn('w:sz'), str(sz))
        el.set(qn('w:space'), '0'); el.set(qn('w:color'), '4A4433')
        borders.append(el)
    tblPr.append(borders)

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill)
    tcPr.append(shd)

def mixed(par, parts, size=12, base_bold=False):
    for text, is_ans in parts:
        r = par.add_run(text)
        set_font(r, size, bold=base_bold or is_ans, red=bool(is_ans))

def build(cfg, A, path):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    s.top_margin = s.bottom_margin = Inches(0.5)
    s.left_margin = s.right_margin = Inches(1.0)

    def blank_or(word):
        return (f" {word} ", 1) if A else ("______________", 0)

    p = doc.add_paragraph()
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(cfg["title"]); set_font(r, 18, bold=True)
    if A:
        r = p.add_run("  ANSWER KEY"); set_font(r, 18, red=True)
        r = p.add_run(f"\t{cfg['lesson']}"); set_font(r, 12, bold=True)
    else:
        r = p.add_run("\tName: ________  Date: ________"); set_font(r, 18, bold=True)

    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Part 1 · The Story Map"); set_font(r, 13, bold=True)

    wb = doc.add_table(rows=1, cols=1); add_borders(wb)
    wb.alignment = WD_TABLE_ALIGNMENT.CENTER
    r = wb.rows[0].cells[0].paragraphs[0].add_run("Word Bank:   " + "     ".join(cfg["bank"]))
    set_font(r, 12, bold=True)

    doc.add_paragraph().paragraph_format.space_after = Pt(0)

    rows = [("The story says…", None, "Action words")] + [
        (cue, [(pre, 0), blank_or(word), (post, 0)]) for cue, pre, word, post in cfg["rows"]
    ]
    t = doc.add_table(rows=len(rows), cols=3); add_borders(t)
    t.autofit = False
    layout = OxmlElement('w:tblLayout'); layout.set(qn('w:type'), 'fixed')
    t._tbl.tblPr.append(layout)
    for col, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), ('4380', '600', '4380')):
        col.set(qn('w:w'), w)
    widths = (Inches(3.05), Inches(0.42), Inches(3.05))
    for ri, row in enumerate(rows):
        cells = t.rows[ri].cells
        for ci, w in enumerate(widths):
            cells[ci].width = w
        shade(cells[0], 'F6EAD8'); shade(cells[2], 'E9EDF5')
        if ri == 0:
            r = cells[0].paragraphs[0].add_run(row[0]); set_font(r, 12, bold=True)
            r = cells[2].paragraphs[0].add_run(row[2]); set_font(r, 12, bold=True)
        else:
            r = cells[0].paragraphs[0].add_run(row[0]); set_font(r, 11)
            r = cells[1].paragraphs[0].add_run("→"); set_font(r, 12, bold=True)
            mixed(cells[2].paragraphs[0], row[1], size=11)

    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4); p.paragraph_format.space_before = Pt(6)
    r = p.add_run(cfg["closing"]); set_font(r, 12)

    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Part 2 · Think!  " + cfg["think_q"]); set_font(r, 13, bold=True)
    if A:
        p = doc.add_paragraph()
        r = p.add_run(cfg["think_a"]); set_font(r, 12, red=True)
    else:
        for _ in range(2):
            p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
            r = p.add_run("_"*70); set_font(r, 12)

    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Part 3 · The story teaches us:"); set_font(r, 13, bold=True)
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6)
    if A:
        mixed(p, cfg["moral_ans"], size=14, base_bold=True)
    else:
        r = p.add_run(cfg["moral_blank"]); set_font(r, 14, bold=True)

    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    r = p.add_run("Part 4 · Draw!  " + cfg["draw"]); set_font(r, 13, bold=True)
    if A:
        p = doc.add_paragraph()
        r = p.add_run(cfg["draw_note"]); set_font(r, 12, red=True)
    else:
        box = doc.add_table(rows=1, cols=1); add_borders(box)
        trPr = box.rows[0]._tr.get_or_add_trPr()
        h = OxmlElement('w:trHeight'); h.set(qn('w:val'), '2900'); trPr.append(h)
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(6)
        r = p.add_run(cfg["draw_line"]); set_font(r, 12)

    doc.save(path)
    print("saved", path)

# EXAMPLE CONFIG (copy this shape for a new chapter)
# NOTE: the cue texts below are ORIGINAL sample copy that only shows the format.
# In a real chapter config, every quoted cue must be transcribed VERBATIM from
# your own copy of the book (see SKILL.md step 5: 逐字核对).
EXAMPLE = {
    "title": "Spring", "lesson": "Lesson 1",
    "bank": ["knocked", "pushed", "slept", "tore", "climbed", "ran"],
    "rows": [
        ("Wake up — spring is here!", "Frog ", "knocked", " on the door."),
        ("The light was too bright for Toad.", "Frog ", "pushed", " Toad out of the house."),
        ("Toad wanted to stay in bed much longer.", "He had ", "slept", " all winter long."),
        ("Frog did not want to wait alone.", "He ", "tore", " off the calendar pages, one by one."),
        ("The May page was on top.", "Toad ", "climbed", " out of bed."),
        ("It must be May now!", "Then they ", "ran", " outside to see the spring."),
    ],
    "closing": ("A whole new year together — play in the meadow, explore the woods, "
                "splash in the river, and watch the stars."),
    "think_q": "Why did Frog tear the calendar pages?",
    "think_a": ("Frog did not want to wait alone for spring. He tore off the pages so the "
                'calendar said "May" — then Toad would wake up and they could enjoy the spring together!'),
    "moral_ans": [("Being with your ",0),(" friend ",1),(" is better than ",0),(" sleeping ",1),(" !",0)],
    "moral_blank": "Being with your ____________ is better than ____________ !",
    "draw": "It is spring! Draw what YOU want to do with your friend!",
    "draw_note": "(Drawings will vary. Student draws a spring plan and says: “This spring, my friend and I will ___!”)",
    "draw_line": "This spring, my friend and I will ______________________________ !",
}

if __name__ == "__main__":
    # Per chapter, edit and run:
    # BASE = "<素材文件夹>/<N.book>/<M-Chapter>/"
    # build(EXAMPLE, False, BASE + "0M - <Chapter> Workbook.docx")
    # build(EXAMPLE, True,  BASE + "0M - <Chapter> Workbook 答案版.docx")
    pass
