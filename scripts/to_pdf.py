#!/usr/bin/env python3
"""Convert workbook .docx files to PDF with LibreOffice and check each one is exactly 2 pages.

Usage:  python3 scripts/to_pdf.py <folder>      (converts every .docx inside, recursively)
Needs:  LibreOffice (soffice) and  pip install pypdfium2
"""
import sys, subprocess, pathlib
import pypdfium2 as pdfium

if len(sys.argv) < 2:
    sys.exit(__doc__)
bad = 0
for f in sorted(pathlib.Path(sys.argv[1]).rglob("*.docx")):
    if f.name.startswith("~$"):
        continue
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(f.parent), str(f)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    n = len(pdfium.PdfDocument(str(f.with_suffix(".pdf"))))
    bad += n != 2
    print(n, f.name, "" if n == 2 else "  <<< NOT 2 PAGES")
sys.exit(1 if bad else 0)
