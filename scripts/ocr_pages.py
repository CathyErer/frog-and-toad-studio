#!/usr/bin/env python3
"""Turn a scanned picture-book PDF into plain text, for checking your typed sentences.

Usage:  python3 scripts/ocr_pages.py <book.pdf> <out.txt> [--split]
--split  cut every page into a left and a right half first (use it for two-page spreads)
Needs:  pip install pypdfium2 pillow  and the tesseract command (brew install tesseract / apt install tesseract-ocr)
"""
import sys, subprocess, tempfile, pathlib
import pypdfium2 as pdfium

if len(sys.argv) < 3:
    sys.exit(__doc__)
pdf = pdfium.PdfDocument(sys.argv[1])
split = "--split" in sys.argv
out = []
with tempfile.TemporaryDirectory() as tmp:
    for i in range(len(pdf)):
        im = pdf[i].render(scale=2.5).to_pil()
        parts = [im.crop((0, 0, im.width // 2, im.height)), im.crop((im.width // 2, 0, im.width, im.height))] if split else [im]
        for j, p in enumerate(parts):
            f = pathlib.Path(tmp) / f"p{i}_{j}.png"
            p.save(f)
            txt = subprocess.run(["tesseract", str(f), "-", "--psm", "4"], capture_output=True, text=True).stdout
            out.append(f"=== page {i + 1}{'ab'[j] if split else ''} ===\n{txt.strip()}\n")
pathlib.Path(sys.argv[2]).write_text("\n".join(out), encoding="utf-8")
print(f"wrote {sys.argv[2]}  ({len(out)} page parts)")
