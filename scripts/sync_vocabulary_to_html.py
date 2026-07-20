"""Sync vocabulary notes into course HTML files using per-machine configuration."""

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


def html_title(path: Path) -> str:
    name = path.name.removesuffix(" 关键词地图.html")
    if " - " in name:
        return name.split(" - ", 1)[1]
    return name


def build_vocab_section(entries: list[dict[str, str]]) -> str:
    cards = []
    for index, entry in enumerate(entries, start=1):
        word = html.escape(entry["word"])
        en_meaning = html.escape(entry["en"])
        zh_meaning = html.escape(entry["zh"])
        example = html.escape(entry["example"])
        cards.append(
            f"""    <div class="vocab-card wob">
      <div class="vocab-num">{index:02d}</div>
      <h3>{word}</h3>
      <p><b>EN:</b> {en_meaning}</p>
      <p><span class="zh"><b>中文：</b>{zh_meaning}</span></p>
      <p class="example">Example: {example}</p>
    </div>"""
        )

    return f"""<!-- Vocabulary -->
<section class="tab" id="vocab">
  <h2 class="sec">Vocabulary <span class="zh">10 个核心词汇</span></h2>
  <p class="hint">Read the word, say the meaning, then make your own sentence. <span class="zh">读词 → 说意思 → 造句。EN only 会隐藏中文解释。</span></p>
  <div class="vocab-grid">
{chr(10).join(cards)}
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


def main() -> None:
    course_root, obsidian_dir = load_config()
    lesson_vocab = parse_vocab_notes(obsidian_dir)
    html_files = sorted(course_root.glob("[1-4].*/*/*关键词地图.html"))
    updated = []

    for path in html_files:
        title = html_title(path)
        entries = lesson_vocab.get(title)
        if not entries:
            raise ValueError(f"No vocabulary found for {title}: {path}")
        if len(entries) != 10:
            raise ValueError(f"Expected 10 vocabulary entries for {title}, got {len(entries)}")

        text = path.read_text(encoding="utf-8")
        text = ensure_vocab_css(text)
        text = ensure_vocab_nav(text)
        text = replace_or_insert_vocab_section(text, build_vocab_section(entries))
        path.write_text(text, encoding="utf-8")
        updated.append(path)

    if len(updated) != 20:
        raise ValueError(f"Expected to update 20 HTML files, updated {len(updated)}")

    print(f"Updated {len(updated)} HTML files with Vocabulary tabs.")


if __name__ == "__main__":
    main()
