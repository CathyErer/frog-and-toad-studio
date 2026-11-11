#!/usr/bin/env python3
"""Build one close-reading courseware HTML (single offline file).

Usage:  python3 scripts/build.py <courseware_dir>

<courseware_dir>/
  source/content.json        required  (schema: references/close-reading.md)
  source/template.html       optional  (defaults to the skill's assets/template.html)
  assets/web/images/*.webp   optional  (scene pictures; else assets/images/*.png|jpg)
  assets/web/decor/*.webp    optional  (small decorations; else assets/decor/*.png)
  assets/story.mp3           optional  (book recording; without it sentences use the browser voice)
  assets/words/*.mp3         optional  (word audio; without it words use the browser voice)
Writes  <courseware_dir>/<NN - Story 点读精读课件>.html  and  source/wordlist.json
"""
import base64, json, re, sys, pathlib

SKILL = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) < 2:
    sys.exit(__doc__)
ROOT = pathlib.Path(sys.argv[1]).resolve()
SRC = ROOT / "source"
data = json.loads((SRC / "content.json").read_text(encoding="utf-8"))
PROPER = set(data.get("proper", ["i"]))
MIME = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def norm(s):
    return s.lower().replace("’", "'").replace("‘", "'")


def slug(s):
    return re.sub(r"[^a-z]+", "_", norm(s)).strip("_")


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def pick(kind):
    web = sorted((ROOT / "assets/web" / kind).glob("*.webp"))
    if web:
        return web
    files = {}
    for ext in (".jpg", ".jpeg", ".png"):
        for p in sorted((ROOT / "assets" / kind).glob("*" + ext)):
            files[p.stem] = p
    return list(files.values())


items = {}
for sc in data["scenes"]:
    for line in sc["lines"]:
        for w in re.findall(r"[A-Za-z]+(?:[’'][A-Za-z]+)*", line["text"]):
            k = norm(w)
            items.setdefault(slug(k), k.capitalize() if k in PROPER else k)
for x in data.get("words", []) + data.get("chunks", []):
    items.setdefault(slug(x["w"]), x["w"])
for g in data.get("glossary", []):
    for v in [g["word"], *g.get("variants", [])]:
        items.setdefault(slug(v), v)
wordlist = [{"slug": s, "text": t} for s, t in sorted(items.items())]
(SRC / "wordlist.json").write_text(json.dumps(wordlist, ensure_ascii=False, indent=1), encoding="utf-8")

images = {p.stem: b64(p, MIME[p.suffix.lower()]) for p in pick("images")}
decor = [b64(p, MIME[p.suffix.lower()]) for p in pick("decor")]
words = {p.stem: b64(p, "audio/mpeg") for p in sorted((ROOT / "assets/words").glob("*.mp3"))}
story = ROOT / "assets/story.mp3"

tpl = SRC / "template.html"
if not tpl.exists():
    tpl = SKILL / "assets/template.html"
html = (tpl.read_text(encoding="utf-8")
        .replace("__STORY__", data["story"])
        .replace("__CONTENT__", json.dumps(data, ensure_ascii=False))
        .replace("__IMAGES__", json.dumps(images))
        .replace("__DECOR__", json.dumps(decor))
        .replace("__WORD_AUDIO__", json.dumps(words))
        .replace("__STORY_AUDIO__", b64(story, "audio/mpeg") if story.exists() else ""))
out = ROOT / f"{data['num']} - {data['story']} 点读精读课件.html"
out.write_text(html, encoding="utf-8")
missing_img = [s["image"] for s in data["scenes"] if s.get("image") and s["image"] not in images]
print(f"built {out.name}  {out.stat().st_size/1e6:.1f} MB")
print(f"pictures: {len(images)}  decorations: {len(decor)}  missing pictures: {missing_img or 'none'}")
print("sentence audio:", "book recording" if story.exists() else "browser voice (no assets/story.mp3)")
print(f"word audio files: {len(words)} of {len(wordlist)} (the rest use the browser voice)")
