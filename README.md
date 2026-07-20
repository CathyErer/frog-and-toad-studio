# frog-and-toad-studio

**Frog and Toad 精读课 studio** — a Claude- and Codex-compatible skill that generates per-chapter teaching materials for Arnold Lobel's *Frog and Toad* series (I Can Read Level 2, ESL Grade 1).

> An AI-agent skill compatible with Claude and Codex for generating a complete per-chapter "三件套" (three-piece set): a projection keyword-map HTML, a one-page Student Workbook .docx, and an Answer Key .docx — plus WeChat-ready lesson summaries and Obsidian sync.

## What it generates

Each story = one lesson = one 三件套:

1. **关键词地图 HTML** — projection lesson plan in a locked cream-paper hand-drawn style, 5 tabs (Warm-up · Vocabulary · Story Map · Characters · Theme), with a bilingual → English-only toggle
2. **Student Workbook .docx** — one page, 4 fixed parts (Story Map verb fill-in · Think! inference · moral fill-in · Draw!)
3. **Answer Key .docx** — same page with answers in red, bold, underlined

Plus, on demand: per-lesson **课程总结与作业（微信版）** paragraphs and **Obsidian** tracking-note sync.

## Repository layout

```
frog-and-toad-studio/
├── SKILL.md                        ← main skill: trigger rules + 7-step workflow
├── config.example.json             ← portable path-configuration template
├── sync-config.md                  ← portable path variables & sync rules
├── sync-checklist.md               ← checklist used on every "检查同步" run
├── assets/
│   └── template_keyword_map.html   ← locked HTML template (Spring layout, original sample text), copy & replace content only
├── references/
│   └── course-map.md               ← all 20 lessons: moral / inference question / verb bank
├── scripts/
│   ├── make_workbooks.py           ← Workbook generator (student + answer key, 1 page each)
│   └── sync_vocabulary_to_html.py  ← sync Vocabulary tab from Obsidian notes into the HTMLs
└── skills/
    └── frog-and-toad-illustration-style/
        ├── SKILL.md                ← sub-skill: consistent watercolor illustration style
        ├── prompts/                ← ready-made illustration prompt lists for all 20 chapters
        └── agents/openai.yaml
```

## First-time path setup

The repository never stores a user's home-folder path. Before running the Obsidian vocabulary sync:

1. Copy `config.example.json` to `config.local.json`.
2. Set `course_root` to the local Frog and Toad course-library folder.
3. Set `obsidian_dir` to the local Frog and Toad tracking folder inside the Obsidian vault.

Example:

```json
{
  "course_root": "/path/to/Frog and Toad精读课",
  "obsidian_dir": "/path/to/Obsidian Vault/课程升级追踪/桥梁/Frog and Toad"
}
```

`config.local.json` is ignored by Git, so private machine paths are never included in the public repository. If the file or either directory is missing, the sync script stops with a clear setup error instead of guessing a path.

## Course coverage

20 lessons across the four books, in folder/book order: *Days with Frog and Toad* (01–05) → *Frog and Toad All Year* (06–10) → *Frog and Toad Together* (11–15) → *Frog and Toad Are Friends* (16–20). See `references/course-map.md` for the full table.

## Hard rules baked into the workflow

- **Verbatim quotes only** — every quote in the HTML / Workbook must match the book word-for-word
- **Keywords confirmed first** — the keyword list is sent to the teacher for confirmation before anything is generated
- **Never invent a new layout** — copy `assets/template_keyword_map.html` and replace content only
- **Workbooks must be exactly 1 page** — verified by converting to PDF and asserting page count
- HTML tag balance is self-checked with Python's HTMLParser before delivery

## Notes

- Local course-library and Obsidian paths are supplied through an untracked `config.local.json` file. The Obsidian sync and WeChat lesson-summary steps are optional — skip them if you don't use those tools.
- Book PDFs, generated courseware, audio, and lesson-summary documents are **not** included in this repository — only the skill itself.

## License

[MIT](LICENSE).

*Frog and Toad* is © Arnold Lobel / HarperCollins. This repository distributes **no text from the books**: the HTML template ships with original placeholder sample text that only demonstrates the layout. When you build real lessons, quotes are transcribed from your own copy of the book and stay in your local course library — they are never committed here.
