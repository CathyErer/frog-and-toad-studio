# Close-reading courseware

One story = one folder = one offline HTML. Start from a copy of `assets/sample/the-puddle/`.

```
<book folder>/
├── 00 <Book Title> 课件入口.html          ← scripts/make_entry.py
└── <NN-Story>/
    ├── NN - <Story> 点读精读课件.html        ← scripts/build.py (do not edit by hand)
    ├── source/content.json                ← all the content
    ├── source/workbook.json               ← workbook questions (references/workbook.md)
    ├── assets/story.mp3                   ← optional book recording
    ├── assets/images/01.png … 09.png      ← optional scene pictures (transparent PNG)
    ├── assets/decor/*.png                 ← optional small decorations
    └── assets/web/…                       ← small WebP copies made by scripts/make_webp.py
```

## The five tabs

| Tab | What it shows | Comes from |
|---|---|---|
| Words | Story Words (10 cards) and Useful Chunks (8 cards); tap to hear | `words`, `chunks` |
| Read | Picture on the left, text on the right; every sentence and every word is tappable; a Think question under the picture | `scenes` |
| Retell | One card per page: picture + sequence word + WHO → DID WHAT keywords; keywords can be hidden | `scenes[].retell` |
| Theme | Moral, core inference question with answer, a question about the student, "find it in the story" | `theme` |
| Quiz | 5 questions, one per reading skill, with "find it in the story" | `quiz` |

Every tab supports notes (pen, highlighter, text box, eraser, clear page, clear all, undo), class profiles, the 中英 / EN switch and PDF export. These live in the template; never rebuild them.

## Planning one story (show this to the teacher before building)

**Pages.** About 9 pages per story (7–10 is fine). Cut where the picture would change. Every sentence of the story appears exactly once, in order.

**Think question (one per page).** Short, answerable from that page, mixing types across the story: who / what / why / how does … feel / what does … mean / how is the end like the beginning. The answer is one sentence. Evidence = the 1–3 sentences that prove it.

**Retell (one card per page).**
- `seq`: First, Then, Next, But, So, After that, Meanwhile, That night, Finally… (the first page is "First", the last is "Finally").
- `rows`: one row per character who acts on that page; `who` is the name, `did` is 1–4 keyword fragments. Fragments are verb-led and short ("ran to the store", "two big cones"), never a full sentence. A short quote in “ ” is fine when the words matter.

**Words.** 10 story words with a child-friendly English meaning, a Chinese meaning and an example sentence the teacher wrote (not from the book). 8 useful chunks (phrases that appear in the story) with Chinese meaning and the book line as the example. For the 20 Frog and Toad stories, use the 10 words listed in `course-map.md` unless the teacher changes them.

**Theme.** The moral (short, child-friendly, with Chinese), the core inference question (`why`) with a 1–2 sentence answer (`because`), and a "you" question that links to the student's life. Evidence = the sentence that best supports the answer. For the 20 stories, take the moral and core question from `course-map.md`.

**Quiz.** Exactly 5 questions, in this order, three options each, the correct option first (the page rotates them):

| # | Skill | Asks about | CCSS · IXL (planning only, never shown) |
|---|---|---|---|
| 1 | Key details | a fact stated in the text | RL.1.1 · II.1 |
| 2 | Sequence | what happened first / next / last | RL.1.2 · DD.1 |
| 3 | Character | what an action or line shows about a character | RL.1.3 · CC.3 |
| 4 | Inference | why something happened (not stated directly) | RL.1.4, RL.1.7 · AA.3 |
| 5 | Theme | what the story teaches | RL.1.2 · AA.5 |

Wrong options are plausible and the same kind of thing as the answer. Do not repeat a Think question as a quiz question. The Theme question needs no evidence.

## content.json

```json
{
  "book": "Frog and Toad Are Friends",
  "story": "Spring", "storyZh": "春天",
  "num": "01", "lesson": 1,
  "home": "../00 Frog and Toad Are Friends 课件入口.html",
  "proper": ["i", "frog", "toad", "toad's", "frog's"],
  "scenes": [{
    "title": "…", "zh": "…", "image": "01",
    "question": "…", "qzh": "…", "answer": "…", "azh": "…",
    "evidence": ["s3"],
    "lines": [{"id": "s1", "text": "…exact book sentence…", "zh": "…", "start": 7.6, "end": 9.2}],
    "retell": {"seq": "First", "rows": [{"who": "Toad", "did": ["woke up", "house is a mess"]}]},
    "overlay": {"box": [36, 13, 34], "lines": ["#Heading", "~crossed-out line", "plain line"]}
  }],
  "glossary": [{"word": "mess", "zh": "…", "en": "…", "variants": ["was a mess"]}],
  "words":  [{"w": "mess", "zh": "…", "en": "…", "ex": "…"}],
  "chunks": [{"w": "be a mess", "zh": "…", "ex": "“…the exact book line…”"}],
  "theme": {"image": "09", "ask": "What does this story teach us?", "askZh": "…",
            "moral": "…", "moralZh": "…", "why": "…", "whyZh": "…",
            "because": "…", "becauseZh": "…", "you": "…", "youZh": "…",
            "evidence": ["s46"], "find": "Find it in the story", "findZh": "回原文找依据"},
  "quiz": [{"skill": "Key details", "skillZh": "关键细节", "ccss": "RL.1.1", "ixl": "II.1",
            "q": "…", "options": ["correct", "wrong", "wrong"], "evidence": ["s10"]}]
}
```

Notes:
- `id`s run s1, s2, … through the whole story. One `lines` entry = one sentence (a long sentence with a quote may be split at a natural break).
- `start` / `end` are seconds in `assets/story.mp3`; `scripts/align_audio.py` fills them. Leave them out when there is no recording.
- `home` is the path from the courseware HTML to the entry page.
- `proper` lists words that stay capitalised when a word is read alone.
- `glossary` drives the underlined words in Read: one entry per story word and chunk; `variants` are the forms that actually appear in the text ("fell asleep" for "fall asleep", "cheer him up" for "cheer someone up").
- `overlay` (optional) prints text on a blank note or list in the picture: `box` = left %, top %, width % of the picture; a line starting with `#` is a heading, `~` is crossed out.
- Chinese (`zh`, `qzh`, `azh`…) is shown only in 中英 mode.

## Checks before handing over

- `scripts/check_text.py` shows no unexplained difference from the book.
- `scripts/build.py` prints no missing pictures you did not expect.
- Open the HTML: no errors in the browser console; each tab looks right; tapping a Think question highlights its evidence and does not start the audio; draw a line and erase part of it; export the notes PDF.
- If there is a recording: say clearly that sentence timing was aligned automatically and list the sentences the aligner could not match, so the teacher can listen to those.
