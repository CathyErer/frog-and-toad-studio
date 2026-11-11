---
name: frog-and-toad-studio
description: "Makes Frog and Toad (Arnold Lobel, I Can Read Level 2) close-reading lessons for ESL Grade 1: one offline click-to-read courseware HTML per story (Words → Read → Retell → Theme → Quiz, pen and highlighter notes, class profiles, PDF export) plus a matching colour two-page workbook and answer key. Use it whenever someone uploads or names a Frog and Toad book or story (Frog and Toad Are Friends / Together / All Year / Days with Frog and Toad; Spring, The Kite, A Lost Button, Cookies…) and asks for 课件、精读、点读、教案、workbook、练习册、答案版 or any teaching material for it. 用户发来 Frog and Toad 的书或某个故事并要课件、精读课、点读、练习册时使用。"
---

# Frog and Toad Studio · 点读精读课

One story in, two finished things out:

1. **Close-reading courseware** — one self-contained offline HTML per story, plus one entry page per book.
2. **Workbook** — a colour two-page student workbook and an answer key (.docx and .pdf).

When the user sends a Frog and Toad book or story, make **these two things in this format**. Do not make keyword maps, slide decks, generic lesson plans, worksheets in another layout or a new design: the templates in `assets/` and the scripts in `scripts/` are locked. Change content, not layout, unless the user explicitly asks for a design change.

Reply to the user in the language they write in (most users write Chinese). Keep English story text exactly as printed in the book.

## What to read

| Task | Read |
|---|---|
| Courseware (always first) | `references/close-reading.md` |
| Workbook (after the courseware content is final) | `references/workbook.md` |
| Pictures (optional; needs an image model) | `references/illustration.md` |
| Default moral, core question and 10 words for each of the 20 stories | `references/course-map.md` |

## Workflow

1. **Get the text.** Ask for the book PDF or photos if you do not have them. For a scanned PDF run `scripts/ocr_pages.py` (use `--split` for two-page spreads). Never type the story from memory.
2. **Plan the story and show the plan before building.** Split it into about 9 pages; for each page write the title, the picture idea, one Think question with answer and evidence sentence(s), and the retell keywords. Add the Theme (take the moral and core question from `references/course-map.md`), 10 words + 8 useful chunks, and 5 quiz questions in the fixed skill order. Show this plan as a table and let the teacher change it.
3. **Build the content file.** Copy `assets/sample/the-puddle/` as a starting folder, write `source/content.json` (schema in `references/close-reading.md`), then run `scripts/check_text.py` against the OCR text and explain every difference.
4. **Audio (optional).** If the teacher has the book recording, save it as `assets/story.mp3`, get word timestamps (for example with Whisper) and run `scripts/align_audio.py`. Without a recording the courseware reads sentences with the browser voice.
5. **Pictures (optional).** Without pictures the page shows a placeholder. With pictures, put them in `assets/images/01.png`… and decorations in `assets/decor/`, then run `scripts/make_webp.py`.
6. **Build** with `scripts/build.py <courseware_dir>`. Open the HTML and check every tab: Words, Read, Retell, Theme, Quiz.
7. **Entry page.** When a book has more than one story, run `scripts/make_entry.py <book_dir> "<Book Title>"`.
8. **Workbook.** Write `source/workbook.json` from the final `content.json` (rules in `references/workbook.md`), run `scripts/make_workbook.py`, then `scripts/to_pdf.py`. Every PDF must be exactly 2 pages.
9. **Report** what was made, what was checked, and what still needs the teacher (listening to the audio timing, looking at pictures).

## Fixed rules (do not break)

- Five tabs in this order: **Words → Read → Retell → Theme → Quiz**.
- Quiz = 5 questions in this order: **Key details → Sequence → Character → Inference → Theme**. Show only the skill name on the page; never print CCSS or IXL codes for students or parents.
- Story sentences, quotes and evidence must match the book word for word.
- Think, Theme and Quiz "find it in the story" buttons only highlight the evidence; they do not play audio by themselves.
- Highlights use a background colour only, never a side bar or vertical line.
- Rounded font (Baloo 2), green as the main colour mixed with cream, brown and yellow; few or no emoji.
- Notes: pen, highlighter, text box, a real eraser (erases only what it touches), clear page, clear all (two clicks), undo; saved per class; PDF export shows exactly what is on the screen and never adds translations.
- Pictures never contain text; notes, lists and letters are drawn blank and the text is overlaid by the courseware (`scene.overlay`).
- Do not copy the book's pictures. Do not put the book text, recordings or pictures in any public place.

## Requirements

Python 3 with `pillow`; `python-docx` and `pypdfium2` for the workbook; LibreOffice (`soffice`) for PDF; `tesseract` for OCR. The courseware itself needs only a browser; the font loads from Google Fonts when online and falls back to a system rounded font offline.
