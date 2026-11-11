#!/usr/bin/env python3
"""Compare the sentences in content.json with the OCR text of the book, word by word.

Usage:  python3 scripts/check_text.py <courseware_dir> <ocr.txt>
Prints every place where your text and the book differ. OCR mistakes are common
(capital I read as T, page numbers, stray marks): explain each difference before you trust it.
"""
import sys, json, re, difflib, pathlib

if len(sys.argv) < 3:
    sys.exit(__doc__)
W = lambda s: re.findall(r"[a-z]+(?:'[a-z]+)*", s.lower().replace("’", "'").replace("‘", "'"))
data = json.loads((pathlib.Path(sys.argv[1]) / "source/content.json").read_text(encoding="utf-8"))
mine = W(" ".join(l["text"] for sc in data["scenes"] for l in sc["lines"]))
ocr = W(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
sm = difflib.SequenceMatcher(None, mine, ocr, autojunk=False)
blocks = [b for b in sm.get_matching_blocks() if b.size >= 4]
if not blocks:
    sys.exit("could not find this story in the OCR text")
seg = ocr[blocks[0].b: blocks[-1].b + blocks[-1].size]
sm = difflib.SequenceMatcher(None, mine, seg, autojunk=False)
diffs = [(t, " ".join(mine[a:b]), " ".join(seg[c:d])) for t, a, b, c, d in sm.get_opcodes() if t != "equal"]
print(f"{len(mine)} words checked, {len(diffs)} difference(s)")
for t, a, b in diffs:
    print(f"  {t:7}  yours: {a or '-':30}  book: {b or '-'}")
