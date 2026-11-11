# Workbook (colour, two pages)

Each story gets a student workbook and an answer key, as .docx and .pdf, US Letter, exactly two pages (one sheet, front and back). Make it **after** the courseware: every question comes from that story's `source/content.json`.

Run:

```bash
python3 scripts/make_workbook.py <courseware_dir>          # reads <courseware_dir>/source/workbook.json
python3 scripts/to_pdf.py "<courseware_dir>/../<Title> Workbook"
```

Fix every line starting with `!!` (a quote that is not word for word in the story, or a retell verb that is not in the story) and make sure each PDF is 2 pages.

## Six parts, fixed order

| Part | Task | Items | CCSS (planning only) |
|---|---|---|---|
| 1 Words | match the word to its meaning (right column is shuffled) | 5 | L.1.4 |
| 2 Key Details | circle one of two answers | 3 | RL.1.1 |
| 3 Sequence | number 4 events 1–4, then fill a verb from the word box into 4 retell sentences (First / Then / Next / Finally) | 4 + 4 | RL.1.2 |
| 4 Character | who said it? circle one of the two names | 5 | RL.1.3, RL.1.6 |
| 5 Think | inference questions with a sentence frame (one word to write), optionally a Yes/No circle | 2 | RL.1.1 |
| 6 Theme & Me | moral with two blanks + word box; drawing box + one sentence about the student | 1 + 1 | RL.1.2, W.1.8 |

Only the skill names appear on the page. Never print CCSS or IXL codes.

## Question rules

- **ESL support**: circling, matching, word boxes and sentence frames. Students write at most one word per item; only the last sentence asks for a short phrase.
- **Words**: 5 of the story words, with a meaning a Grade 1 reader understands (about 38 characters or fewer, so it fits on one line).
- **Key Details**: the answer is stated in the text; the wrong option is the same kind of thing. Do not repeat the courseware quiz.
- **Sequence**: 4 short sentences about 4 different events (or 4 pictures, if the story has scene pictures: set `pics`). Use different events from the retell sentences so one does not give away the other.
- **Retell sentences**: each hides one verb; the verb must appear in the story in exactly that form. The 4 verbs go into the word box.
- **Character**: quotes copied word for word from `content.json` (only a final comma may become a full stop). Pick lines only one of the two characters says. Do not capitalise a fragment that starts in lower case; choose another line.
- **Think**: one "why" question and one "is it true / how did they feel" question. The answer needs inference but uses easy words.
- **Theme**: the moral from `content.json`, with two key words blanked.
- **Draw**: a question about the student's own life + a sentence frame; the answer key shows example answers.

## workbook.json

```json
{
  "title": "The Puddle", "bname": "Sample Book", "num": 1,
  "speakers": ["Frog", "Toad"],
  "header_image": "assets/decor/frog-toad-peek.png",
  "decor_order": ["sprout", "sun", "flowers", "calendar-page"],
  "words":   [["puddle", "water on the ground after rain"], "… 5 pairs"],
  "details": [["When did it rain?", ["all day", "all night"], 1], "… 3 items, last number = index of the answer"],
  "seq":     ["4 events in the right order (the page shuffles them)"],
  "pics":    [["03", 2], "optional: [image name, correct number] × 4, replaces seq"],
  "retell":  [["First, Duck ", "looked", " out of the window."], "… 4 items: before, hidden verb, after"],
  "quotes":  [["“What a fine puddle!”", 0], "… 5 items, number = index in speakers"],
  "think":   [{"q": "Why …?", "fr": ["He did not want to get ", "wet", "."]},
              {"q": "Was … happy?", "ch": [["Yes", "No"], 0], "fr": ["…", "friend", "."]}],
  "theme":   ["A good ", "friend", " finds a way to ", "help", "!"],
  "draw":    ["How can YOU help a friend? Draw and write.", "I can help my friend ", "share my umbrella / tie a shoe", "."]
}
```

`header_image` and `decor_order` are optional. Decorations come from the story's own `assets/decor/` (they appear after Part 1, Part 5, Part 6 and on the page 2 header); if the story has none, none are used. See `assets/sample/the-puddle/source/workbook.json` for a complete example.

## Locked layout (in scripts/make_workbook.py)

- US Letter; margins 0.55 in top/bottom, 0.75 in left/right; Arial 13 pt; no emoji in the .docx.
- Colours: green `4F7A35` (title, part number box, dots, rules), brown `7A4E24` (part names, borders, moral word box), pale yellow `FFF1BF` (retell word box), grey-brown `6B5B4A` (directions). The drawing box stays white so children can colour.
- Header: story title 30 pt green + "<Book> · Story N" + Name / Date; optional header picture on the right.
- Tables use fixed layout and set `tblGrid` column widths (otherwise LibreOffice renders equal widths and lines wrap).
- Page 2 starts with a page-break-before paragraph; the drawing box row is exactly 3.2 in high.
- Answer key: red "ANSWER KEY" next to the title; answers red `C00000`, bold, underlined; a key line under the matching table; red numbers in the sequence boxes; "Drawings will vary" in the drawing box.

## Checks before handing over

- No `!!` lines from `make_workbook.py`.
- Every PDF is exactly 2 pages (student and answer key).
- Look at both pages of the student PDF: no wrapped lines, nothing cut off.
- If you merge a whole book, merge the student PDFs and the answer-key PDFs separately, in story order.
