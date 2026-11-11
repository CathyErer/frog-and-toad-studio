#!/usr/bin/env python3
"""Give every sentence in content.json a start/end time in the book recording.

Usage:  python3 scripts/align_audio.py <courseware_dir> <transcript.json>
transcript.json = word-level timestamps from Whisper (or any tool) in the form
  {"segments": [{"words": [{"word": "Toad", "start": 7.6, "end": 7.9}, ...]}, ...]}
The script matches the words of your sentences to the transcript words (difflib),
writes start/end into source/content.json and lists every sentence it could not match.
Sentences it could not match get the gap between their neighbours: check them by ear.
"""
import sys, json, re, difflib, pathlib

if len(sys.argv) < 3:
    sys.exit(__doc__)
ROOT = pathlib.Path(sys.argv[1]).resolve()
cj = ROOT / "source/content.json"
data = json.loads(cj.read_text(encoding="utf-8"))
tr = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
W = lambda s: [w.lower().replace("’", "'") for w in re.findall(r"[A-Za-z]+(?:[’'][A-Za-z]+)*", s)]
lines = [l for sc in data["scenes"] for l in sc["lines"]]
mine = [(w, l["id"]) for l in lines for w in W(l["text"])]
aw = [(re.sub(r"[^a-z']", "", x["word"].lower().replace("’", "'")), x["start"], x["end"])
      for sg in tr["segments"] for x in sg.get("words", [])]
aw = [x for x in aw if x[0]]
sm = difflib.SequenceMatcher(None, [w for w, _ in mine], [w for w, _, _ in aw], autojunk=False)
tm = {}
for a, b, size in sm.get_matching_blocks():
    for k in range(size):
        lid = mine[a + k][1]
        st, en = aw[b + k][1], aw[b + k][2]
        cur = tm.get(lid)
        tm[lid] = [min(cur[0], st), max(cur[1], en)] if cur else [st, en]
problems = []
for i, l in enumerate(lines):
    if l["id"] not in tm:
        prev = tm[lines[i - 1]["id"]][1] if i else 0
        nxt = next((tm[x["id"]][0] for x in lines[i + 1:] if x["id"] in tm), prev + 1.6)
        tm[l["id"]] = [prev + .08, max(prev + .5, nxt - .08)]
        problems.append(f"not found in recording: {l['id']}  {l['text'][:50]}")
for i, l in enumerate(lines):
    st, en = tm[l["id"]]
    if i and st < tm[lines[i - 1]["id"]][1] - .6:
        problems.append(f"overlaps the previous sentence: {l['id']}  {l['text'][:50]}")
    l["start"], l["end"] = round(max(0, st - .08), 2), round(en + .1, 2)
cj.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
matched = sum(s for _, _, s in sm.get_matching_blocks())
print(f"{len(lines)} sentences, {matched}/{len(mine)} words matched")
print("\n".join(problems) or "every sentence matched")
