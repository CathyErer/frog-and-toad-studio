"""Audit the 20 Frog and Toad Vocabulary tabs after synchronization."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from sync_vocabulary_to_html import load_config, parse_chunk_notes, parse_vocab_notes


class BalanceParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag not in self.stack:
            self.errors.append(f"unexpected </{tag}>")
            return
        while self.stack:
            if self.stack.pop() == tag:
                break


def html_title(path: Path) -> str:
    name = path.name.removesuffix(" 关键词地图.html")
    return name.split(" - ", 1)[1] if " - " in name else name


def main() -> None:
    course_root, obsidian_dir = load_config()
    vocab = parse_vocab_notes(obsidian_dir)
    chunks = parse_chunk_notes(obsidian_dir)
    html_files = sorted(course_root.glob("[1-4].*/*/*关键词地图.html"))
    errors: list[str] = []

    if len(html_files) != 20:
        errors.append(f"expected 20 HTML files, found {len(html_files)}")
    for path in html_files:
        title = html_title(path)
        text = path.read_text(encoding="utf-8")
        parser = BalanceParser()
        parser.feed(text)
        checks = {
            "Story Word cards": text.count('class="vocab-card wob"') == 10,
            "Useful Chunk cards": text.count('class="chunk-card wob"') == 8,
            "CORE labels": text.count('class="chunk-level">CORE</span>') == 5,
            "STORY labels": text.count('class="chunk-level story">STORY</span>') == 3,
            "mode buttons": text.count('class="vocab-mode') == 2,
            "panels": text.count('class="vocab-panel') == 2,
            "switch JavaScript": "document.querySelectorAll('.vocab-mode')" in text,
            "no In the story": "In the story:" not in text,
            "no How to use": "How to use" not in text,
            "no That means": "That means" not in text,
            "balanced HTML": not parser.stack and not parser.errors,
            "10 note words": len(vocab.get(title, [])) == 10,
            "8 note chunks": len(chunks.get(title, [])) == 8,
        }
        for label, passed in checks.items():
            if not passed:
                errors.append(f"{title}: {label} failed")

        for src in re.findall(r'<img[^>]+src=["\']([^"\']+)', text, re.I):
            if not re.match(r"(?:https?:|data:)", src) and not (path.parent / src).resolve().exists():
                errors.append(f"{title}: missing image {src}")

    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: 20 lessons; 200 Story Words; 160 Useful Chunks; all structural checks passed.")


if __name__ == "__main__":
    main()
