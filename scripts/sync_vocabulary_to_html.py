"""Sync Story Words and Useful Chunks into course HTML files."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = SKILL_DIR / "config.local.json"

KEYWORD_NOTES = [
    "01 - Days with Frog and Toad 关键词地图.md",
    "02 - Frog and Toad All Year 关键词地图.md",
    "03 - Frog and Toad Together 关键词地图.md",
    "04 - Frog and Toad Are Friends 关键词地图.md",
]


VOCAB_CSS = r"""

/* ================= vocabulary ================= */
.vocab-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:16px;
}
@media(max-width:820px){.vocab-grid{grid-template-columns:1fr;}}
.vocab-card{
  position:relative;
  padding:18px 20px 16px 64px;
  background:#fffdf4;
  min-height:156px;
}
.vocab-card:nth-child(4n+1){background:var(--frog-wash); transform:rotate(-.35deg);}
.vocab-card:nth-child(4n+2){background:var(--toad-wash); transform:rotate(.35deg);}
.vocab-card:nth-child(4n+3){background:#fff8e9; transform:rotate(.2deg);}
.vocab-card:nth-child(4n+4){background:#f3f0df; transform:rotate(-.2deg);}
.vocab-num{
  position:absolute;
  left:18px;
  top:18px;
  width:34px;
  height:34px;
  border:2.5px solid var(--ink);
  border-radius:50%;
  background:var(--sun);
  color:#fff;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:800;
  box-shadow:var(--shadow);
}
.vocab-card h3{
  font-size:1.45rem;
  color:var(--frog-deep);
  line-height:1.1;
  margin-bottom:8px;
}
.vocab-card p{
  font-size:1.06rem;
  line-height:1.45;
  font-weight:650;
  margin:5px 0;
}
.vocab-card .example{
  font-family:"Patrick Hand","PingFang SC",cursive;
  font-size:1.18rem;
  color:var(--toad-deep);
}
"""


USEFUL_CHUNKS_CSS = r"""

/* ================= useful chunks ================= */
.vocab-switcher{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 20px;}
.vocab-mode{font-family:inherit;font-size:1.12rem;font-weight:800;color:var(--ink);background:#fffdf4;border:3px solid var(--ink);border-radius:225px 14px 255px 14px / 14px 255px 14px 225px;padding:9px 20px;cursor:pointer;box-shadow:var(--shadow);}
.vocab-mode:nth-child(odd){transform:rotate(-.5deg);}
.vocab-mode:nth-child(even){transform:rotate(.5deg);}
.vocab-mode.active{color:#fff;background:var(--frog);border-color:var(--frog-deep);}
.vocab-panel{display:none;}
.vocab-panel.show{display:block;animation:pop .25s ease;}
.chunk-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;}
@media(max-width:860px){.chunk-grid{grid-template-columns:1fr;}}
.chunk-card{position:relative;padding:20px 22px 18px;min-height:250px;background:#fffdf4;}
.chunk-card:nth-child(4n+1){background:var(--frog-wash);transform:rotate(-.25deg);}
.chunk-card:nth-child(4n+2){background:var(--toad-wash);transform:rotate(.25deg);}
.chunk-card:nth-child(4n+3){background:#fff8e9;transform:rotate(.15deg);}
.chunk-card:nth-child(4n+4){background:#f3f0df;transform:rotate(-.15deg);}
.chunk-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:8px;}
.chunk-card h3{color:var(--frog-deep);font-size:1.5rem;line-height:1.2;}
.chunk-level{flex:0 0 auto;padding:3px 10px;color:#fff;background:var(--toad-deep);border:2px solid var(--ink);border-radius:999px;font-size:.78rem;font-weight:800;letter-spacing:.04em;}
.chunk-level.story{background:var(--sun-deep);}
.chunk-meaning{font-size:1.05rem;font-weight:700;line-height:1.45;margin:7px 0 11px;}
.chunk-line{padding:9px 12px;margin-top:8px;background:rgba(255,253,244,.88);border-left:5px solid var(--frog);border-radius:7px;font-size:1.05rem;font-weight:650;line-height:1.5;}
.chunk-line.try{border-left-color:var(--sun);font-family:"Patrick Hand","PingFang SC",cursive;font-size:1.16rem;}
.chunk-line b{color:var(--toad-deep);}
"""


def resolve_config_path(value: str, config_path: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = config_path.parent / path
    return path.resolve()


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> tuple[Path, Path]:
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Missing local configuration: {config_path}. "
            "Copy config.example.json to config.local.json and fill in your paths."
        )

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc

    missing = [key for key in ("course_root", "obsidian_dir") if not config.get(key)]
    if missing:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing)}")

    course_root = resolve_config_path(config["course_root"], config_path)
    obsidian_dir = resolve_config_path(config["obsidian_dir"], config_path)

    for label, path in (("course_root", course_root), ("obsidian_dir", obsidian_dir)):
        if not path.is_dir():
            raise FileNotFoundError(f"Configured {label} directory does not exist: {path}")

    return course_root, obsidian_dir


def parse_vocab_notes(obsidian_dir: Path) -> dict[str, list[dict[str, str]]]:
    lesson_vocab: dict[str, list[dict[str, str]]] = {}
    lesson_re = re.compile(r"^## Lesson \d+ · (.+?)(?:（|\(|✅|🌸|📖|🔘|🩱|💌|📝|🌱|🍪|🐉|🎭|❄️|🌧️|🍦|🍂|🎄|$)")
    item_re = re.compile(
        r"^\d+\. \*\*(.+?)\*\* — EN: (.*?) 中文：(.*?)。Example: (.*)$"
    )

    for note_name in KEYWORD_NOTES:
        note_path = obsidian_dir / note_name
        if not note_path.is_file():
            raise FileNotFoundError(f"Missing vocabulary note: {note_path}")
        text = note_path.read_text(encoding="utf-8")
        current_title: str | None = None
        in_vocab = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            lesson_match = lesson_re.match(line)
            if lesson_match:
                current_title = lesson_match.group(1).strip()
                lesson_vocab.setdefault(current_title, [])
                in_vocab = False
                continue

            if line.startswith("**10 个词汇"):
                in_vocab = True
                continue

            if in_vocab and line.startswith("**关键词复述线"):
                in_vocab = False
                continue

            if in_vocab and current_title:
                item_match = item_re.match(line)
                if item_match:
                    word, en_meaning, zh_meaning, example = item_match.groups()
                    lesson_vocab[current_title].append(
                        {
                            "word": word.strip(),
                            "en": en_meaning.strip(),
                            "zh": zh_meaning.strip(),
                            "example": example.strip(),
                        }
                    )

    return lesson_vocab


def parse_chunk_notes(obsidian_dir: Path) -> dict[str, list[dict[str, str]]]:
    lesson_chunks: dict[str, list[dict[str, str]]] = {}
    lesson_re = re.compile(r"^## Lesson \d+ · (.+?)(?:（|\(|✅|🌸|📖|🔘|🩱|💌|📝|🌱|🍪|🐉|🎭|❄️|🌧️|🍦|🍂|🎄|$)")
    item_re = re.compile(r"^\d+\. \*\*(.+?)\*\* — (CORE|STORY)$")

    for note_name in KEYWORD_NOTES:
        note_path = obsidian_dir / note_name
        if not note_path.is_file():
            raise FileNotFoundError(f"Missing useful-chunks note: {note_path}")
        current_title: str | None = None
        current_entry: dict[str, str] | None = None
        in_chunks = False

        for raw_line in note_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            lesson_match = lesson_re.match(line)
            if lesson_match:
                current_title = lesson_match.group(1).strip()
                lesson_chunks.setdefault(current_title, [])
                current_entry = None
                in_chunks = False
                continue

            if line.startswith("**Useful Chunks（8 个固定搭配"):
                if not current_title:
                    raise ValueError(f"Useful Chunks block appears before lesson heading: {note_path}")
                in_chunks = True
                current_entry = None
                continue

            if in_chunks and line.startswith("**关键词复述线"):
                in_chunks = False
                current_entry = None
                continue

            if not in_chunks or not current_title or not line:
                continue

            item_match = item_re.match(line)
            if item_match:
                phrase, level = item_match.groups()
                current_entry = {"phrase": phrase.strip(), "level": level}
                lesson_chunks[current_title].append(current_entry)
                continue

            if not current_entry or not line.startswith("-"):
                continue
            value = line[1:].strip()
            if value.startswith("中文："):
                current_entry["zh"] = value.removeprefix("中文：").strip()
            elif value.startswith("Try it:"):
                current_entry["example"] = value.removeprefix("Try it:").strip()
            elif "source" not in current_entry:
                current_entry["source"] = value

    return lesson_chunks


def html_title(path: Path) -> str:
    name = path.name.removesuffix(" 关键词地图.html")
    if " - " in name:
        return name.split(" - ", 1)[1]
    return name


def build_vocab_section(
    vocab_entries: list[dict[str, str]], chunk_entries: list[dict[str, str]]
) -> str:
    vocab_cards = []
    for index, entry in enumerate(vocab_entries, start=1):
        word = html.escape(entry["word"])
        en_meaning = html.escape(entry["en"])
        zh_meaning = html.escape(entry["zh"])
        example = html.escape(entry["example"])
        vocab_cards.append(
            f"""    <div class="vocab-card wob">
      <div class="vocab-num">{index:02d}</div>
      <h3>{word}</h3>
      <p><b>EN:</b> {en_meaning}</p>
      <p><span class="zh"><b>中文：</b>{zh_meaning}</span></p>
      <p class="example">Example: {example}</p>
    </div>"""
        )

    chunk_cards = []
    for entry in chunk_entries:
        phrase = html.escape(entry["phrase"])
        level = entry["level"]
        level_class = " story" if level == "STORY" else ""
        zh_meaning = html.escape(entry["zh"])
        source = html.escape(entry["source"])
        example = html.escape(entry["example"])
        chunk_cards.append(
            f"""      <article class="chunk-card wob">
        <div class="chunk-top"><h3>{phrase}</h3><span class="chunk-level{level_class}">{level}</span></div>
        <p class="chunk-meaning zh">{zh_meaning}</p>
        <p class="chunk-line">{source}</p>
        <p class="chunk-line try"><b>Try it:</b> {example}</p>
      </article>"""
        )

    return f"""<!-- Vocabulary -->
<section class="tab" id="vocab">
  <h2 class="sec">Vocabulary <span class="zh">故事词汇 + 固定搭配</span></h2>
  <p class="hint">Choose a set. Learn the story words, then meet each useful chunk in a real situation. <span class="zh">选择一组：先学故事词汇，再用自然的小情境理解整块语言。</span></p>
  <div class="vocab-switcher" role="tablist" aria-label="Vocabulary sets">
    <button class="vocab-mode active" data-vocab-view="words" role="tab" aria-selected="true">Story Words <span class="zh">10 个故事词汇</span></button>
    <button class="vocab-mode" data-vocab-view="chunks" role="tab" aria-selected="false">Useful Chunks <span class="zh">8 个固定搭配</span></button>
  </div>

  <div class="vocab-panel show" data-vocab-panel="words" role="tabpanel">
    <div class="vocab-grid">
{chr(10).join(vocab_cards)}
    </div>
  </div>

  <div class="vocab-panel" data-vocab-panel="chunks" role="tabpanel">
    <div class="chunk-grid">
{chr(10).join(chunk_cards)}
    </div>
  </div>
</section>

"""


def replace_or_insert_vocab_section(text: str, section: str) -> str:
    section_re = re.compile(
        r"<!-- Vocabulary -->\n<section class=\"tab\" id=\"vocab\">.*?</section>\n\n",
        re.S,
    )
    if section_re.search(text):
        return section_re.sub(section, text)

    theme_marker = "<!-- ④ theme -->"
    if theme_marker in text:
        return text.replace(theme_marker, section + theme_marker, 1)

    theme_section = '<section class="tab" id="theme">'
    if theme_section in text:
        return text.replace(theme_section, section + theme_section, 1)

    raise ValueError("Could not find Theme section insertion point")


def ensure_vocab_nav(text: str) -> str:
    button = '    <button class="tabbtn" data-tab="vocab">Vocabulary <span class="zh">词汇</span></button>\n'
    text = re.sub(r"    <button class=\"tabbtn\" data-tab=\"vocab\">.*?</button>\n", "", text)
    warmup_button = re.search(r"    <button class=\"tabbtn active\" data-tab=\"warmup\">.*?</button>\n", text)
    if warmup_button:
        return text[: warmup_button.end()] + button + text[warmup_button.end() :]
    nav_right = '    <div class="nav-right"><button id="langBtn">EN only</button></div>'
    if nav_right not in text:
        raise ValueError("Could not find nav-right insertion point")
    return text.replace(nav_right, button + nav_right, 1)


def ensure_vocab_css(text: str) -> str:
    if "/* ================= vocabulary ================= */" in text:
        return text
    theme_marker = "/* ================= theme ================= */"
    if theme_marker in text:
        return text.replace(theme_marker, VOCAB_CSS + "\n" + theme_marker, 1)

    footer_marker = "footer{"
    if footer_marker in text:
        return text.replace(footer_marker, VOCAB_CSS + "\n" + footer_marker, 1)

    raise ValueError("Could not find CSS insertion point")


def ensure_useful_chunks_css(text: str) -> str:
    if "/* ================= useful chunks ================= */" in text:
        return text
    theme_marker = "/* ================= theme ================= */"
    if theme_marker in text:
        return text.replace(theme_marker, USEFUL_CHUNKS_CSS + "\n" + theme_marker, 1)
    footer_marker = "footer{"
    if footer_marker in text:
        return text.replace(footer_marker, USEFUL_CHUNKS_CSS + "\n" + footer_marker, 1)
    raise ValueError("Could not find Useful Chunks CSS insertion point")


def ensure_vocab_switch_js(text: str) -> str:
    if "document.querySelectorAll('.vocab-mode')" in text:
        return text
    switch_js = """
document.querySelectorAll('.vocab-mode').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.vocab-mode').forEach(b=>{
      b.classList.remove('active');
      b.setAttribute('aria-selected','false');
    });
    document.querySelectorAll('.vocab-panel').forEach(panel=>panel.classList.remove('show'));
    btn.classList.add('active');
    btn.setAttribute('aria-selected','true');
    document.querySelector(`[data-vocab-panel="${btn.dataset.vocabView}"]`).classList.add('show');
  });
});
"""
    if "</script>" not in text:
        raise ValueError("Could not find script closing tag")
    return text.replace("</script>", switch_js + "</script>", 1)


def bump_content_version(text: str) -> str:
    marker = "<!-- contentVersion: 2026-09-02-useful-chunks-v1 -->"
    if re.search(r"<!-- contentVersion: .*? -->", text):
        return re.sub(r"<!-- contentVersion: .*? -->", marker, text, count=1)
    if "</title>" in text:
        return text.replace("</title>", "</title>\n" + marker, 1)
    return text


def main() -> None:
    course_root, obsidian_dir = load_config()
    lesson_vocab = parse_vocab_notes(obsidian_dir)
    lesson_chunks = parse_chunk_notes(obsidian_dir)
    html_files = sorted(course_root.glob("[1-4].*/*/*关键词地图.html"))
    updated = []

    for path in html_files:
        title = html_title(path)
        entries = lesson_vocab.get(title)
        if not entries:
            raise ValueError(f"No vocabulary found for {title}: {path}")
        if len(entries) != 10:
            raise ValueError(f"Expected 10 vocabulary entries for {title}, got {len(entries)}")
        chunks = lesson_chunks.get(title)
        if not chunks:
            raise ValueError(f"No Useful Chunks found for {title}: {path}")
        if len(chunks) != 8:
            raise ValueError(f"Expected 8 Useful Chunks for {title}, got {len(chunks)}")
        levels = [entry.get("level") for entry in chunks]
        if levels.count("CORE") != 5 or levels.count("STORY") != 3:
            raise ValueError(f"Expected 5 CORE and 3 STORY chunks for {title}, got {levels}")
        for chunk in chunks:
            missing = [field for field in ("phrase", "level", "zh", "source", "example") if not chunk.get(field)]
            if missing:
                raise ValueError(f"Incomplete Useful Chunk for {title}: missing {missing} in {chunk}")

        text = path.read_text(encoding="utf-8")
        text = ensure_vocab_css(text)
        text = ensure_useful_chunks_css(text)
        text = ensure_vocab_nav(text)
        text = replace_or_insert_vocab_section(text, build_vocab_section(entries, chunks))
        text = ensure_vocab_switch_js(text)
        text = bump_content_version(text)
        path.write_text(text, encoding="utf-8")
        updated.append(path)

    if len(updated) != 20:
        raise ValueError(f"Expected to update 20 HTML files, updated {len(updated)}")

    print(f"Updated {len(updated)} HTML files with Story Words and Useful Chunks.")


if __name__ == "__main__":
    main()
