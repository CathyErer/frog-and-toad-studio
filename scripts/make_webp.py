#!/usr/bin/env python3
"""Shrink full-size pictures into small transparent WebP copies that build.py embeds.

Usage:  python3 scripts/make_webp.py <courseware_dir>
Reads   assets/images/*.png|jpg (scene pictures) and assets/decor/*.png (decorations)
Writes  assets/web/images/*.webp (max 1280 px wide) and assets/web/decor/*.webp (max 420 px wide)
The originals are never changed. Transparent borders are trimmed.
"""
import sys, pathlib
from PIL import Image

if len(sys.argv) < 2:
    sys.exit(__doc__)
ROOT = pathlib.Path(sys.argv[1]).resolve()
n = 0
for kind, width in (("images", 1280), ("decor", 420)):
    out = ROOT / "assets/web" / kind
    out.mkdir(parents=True, exist_ok=True)
    for f in sorted((ROOT / "assets" / kind).iterdir()) if (ROOT / "assets" / kind).exists() else []:
        if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        o = out / (f.stem + ".webp")
        if o.exists() and o.stat().st_mtime > f.stat().st_mtime:
            continue
        im = Image.open(f).convert("RGBA")
        box = im.getchannel("A").getbbox()
        if box:
            im = im.crop(box)
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(o, "WEBP", quality=80, method=4)
        n += 1
print(f"wrote {n} webp file(s)")
