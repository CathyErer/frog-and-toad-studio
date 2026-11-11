# Frog and Toad Studio · 点读精读课

An agent skill that turns one *Frog and Toad* story (Arnold Lobel, I Can Read Level 2) into two finished teaching materials for ESL Grade 1:

1. **Close-reading courseware** — one offline HTML per story: **Words → Read → Retell → Theme → Quiz**. Tap any sentence or word to hear it, draw and highlight anywhere, keep separate notes for each class, switch 中英 / EN, export the notes as a PDF for parents. Plus one entry page per book.
2. **Colour workbook** — two pages (one sheet), student version and answer key, .docx and .pdf. Six parts: Words, Key Details, Sequence + retell, Character, Think, Theme & Me.

一个故事进去，两样成品出来：点读精读课件（离线 HTML）和配套的彩色两页练习册（学生版 + 答案版）。把书发给装了这个 skill 的 Claude / Codex，说"做这个故事的课件和练习册"就行。

> **v2 (2026-11)** replaces the v1 keyword-map skill. v1 is kept under the git tag [`v1-keyword-map`](../../tree/v1-keyword-map).

Follows the open [Agent Skills](https://agentskills.io) format (`SKILL.md` + YAML front matter), so the same folder works in Claude (claude.ai, Claude Code), OpenAI Codex and other agents that support it.

## Install · 安装

The whole repository is one skill folder. 整个仓库就是一个 skill 文件夹。

**Claude.ai / Claude desktop**: download the repository as a zip (Code → Download ZIP), then Settings → Capabilities → Skills → upload it.

**Claude Code / Codex**:

```bash
# Claude Code
git clone https://github.com/CathyErer/frog-and-toad-studio.git ~/.claude/skills/frog-and-toad-studio
# OpenAI Codex
git clone https://github.com/CathyErer/frog-and-toad-studio.git ~/.agents/skills/frog-and-toad-studio
```

**Update · 更新到最新版**: `git pull` inside that folder, or download the zip again and replace the old skill.

## Use · 用法

Send the book (PDF or photos) and say which story, for example:

- "Make the courseware and workbook for *A Lost Button*." 
- 「这是 Frog and Toad Together，帮我做 The Garden 的点读精读课件和练习册。」

The agent will: read the text (OCR for scans) → show you a page-by-page plan (pages, Think questions, retell keywords, theme, quiz) → build the courseware → make the workbook → check everything. 先给你看逐页方案，你确认后再生成。

## What is inside

```
SKILL.md                     ← entry point: when to use, workflow, fixed rules
references/close-reading.md  ← courseware: tabs, planning rules, content.json schema, checks
references/workbook.md       ← workbook: six parts, question rules, workbook.json, layout
references/illustration.md   ← optional clay-style picture prompts and checks
references/course-map.md     ← all 20 stories: moral, core inference question, 10 story words
assets/template.html         ← locked courseware template
assets/entry_template.html   ← book entry page template
assets/sample/the-puddle/    ← an original sample story (not from the books) to copy and test
scripts/                     ← build.py, make_webp.py, align_audio.py, ocr_pages.py, check_text.py,
                               make_entry.py, make_workbook.py, to_pdf.py
```

Try it with the sample:

```bash
python3 scripts/build.py assets/sample/the-puddle
python3 scripts/make_workbook.py assets/sample/the-puddle
python3 scripts/to_pdf.py "assets/sample/The Puddle Workbook"
```

Needs Python 3 with `pillow`, `python-docx`, `pypdfium2`; LibreOffice for PDF; `tesseract` for OCR.

## Copyright · 版权

This repository contains **no text, pictures or recordings from the Frog and Toad books**. Use your own copy of the book; keep the courseware you make for your own classes. The sample story is original. 仓库里不含原书的文字、插图和录音，请用你自己的书。

## License

MIT
