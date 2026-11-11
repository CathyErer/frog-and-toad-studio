#!/usr/bin/env python3
"""Build the book entry page: one card per story, linking to each courseware HTML.

Usage:  python3 scripts/make_entry.py <book_dir> "<Book Title>" [book number]
Finds every courseware under <book_dir> (a folder with source/content.json and a built HTML),
orders them by content.json "num", and writes <book_dir>/00 <Book Title> 课件入口.html.
The card picture is the first scene picture, if there is one.
"""
import sys, io, json, base64, pathlib, urllib.parse

if len(sys.argv) < 3:
    sys.exit(__doc__)
SKILL = pathlib.Path(__file__).resolve().parent.parent
BOOK = pathlib.Path(sys.argv[1]).resolve()
TITLE = sys.argv[2]
NUM = sys.argv[3] if len(sys.argv) > 3 else ""
items = []
for cj in BOOK.rglob("source/content.json"):
    root = cj.parent.parent
    html = sorted(root.glob("*点读精读课件.html"))
    if html:
        items.append((json.loads(cj.read_text(encoding="utf-8")), root, html[0]))
items.sort(key=lambda x: x[0]["num"])
cards = []
for i, (c, root, html) in enumerate(items, 1):
    href = urllib.parse.quote(str(html.relative_to(BOOK)))
    pics = sorted((root / "assets/web/images").glob("*.webp")) or sorted((root / "assets/images").glob("*.png"))
    if pics:
        from PIL import Image
        im = Image.open(pics[0]).convert("RGBA")
        im.thumbnail((520, 400))
        b = io.BytesIO()
        im.save(b, "WEBP", quality=78)
        pic = f'<img src="data:image/webp;base64,{base64.b64encode(b.getvalue()).decode()}" alt="">'
    else:
        pic = f'<div class="ph">{c["story"]}</div>'
    t = c["theme"]
    cards.append(f'<a class="card" href="{href}"><div class="pic">{pic}<span class="num">{i}</span></div>'
                 f'<h3>{c["story"]} <span class="zh">{c.get("storyZh", "")}</span></h3>'
                 f'<p>{t["moral"]}<span class="zh">{t.get("moralZh", "")}</span></p><span class="go">Open →</span></a>')
sub = f'Close Reading <span class="zh">精读课{" · 第 " + NUM + " 本" if NUM else ""} · {len(cards)} 个故事</span>'
page = ((SKILL / "assets/entry_template.html").read_text(encoding="utf-8")
        .replace("__TITLE__", TITLE).replace("__SUBTITLE__", sub).replace("__CARDS__", "".join(cards)))
out = BOOK / f"00 {TITLE} 课件入口.html"
out.write_text(page, encoding="utf-8")
print(f"wrote {out.name} with {len(cards)} stories")
