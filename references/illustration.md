# Pictures (optional)

The courseware works without pictures (each page shows "picture coming soon"). If the teacher has an image model (Codex, ChatGPT, Midjourney…), write the prompts with these rules. The agent itself does not need to draw. Do not copy, trace or scan the book's own illustrations; make new pictures in your own style.

## House style: clay miniatures

Put this paragraph in front of every prompt:

```
Photographed handmade polymer-clay stop-motion miniature, tactile matte clay with small handmade impressions, soft warm natural light, gentle shadows. Not a flat drawing, not glossy plastic, not chibi. Palette: moss green, sage green, ochre brown, cream white, small touches of warm orange. Transparent background PNG: only the subject and its immediate set pieces, no backdrop, no frame, no border. No text, letters, labels or watermarks anywhere. Use the attached character reference sheet: every character must match it exactly in body shape, skin colour, eyes and clothing.
Anatomy check: every character has exactly two arms, two legs, one head. Each hand is attached to its own arm. If a character points, it points with ONE hand only. Do not draw motion-blur copies or ghost duplicates of a character. Draw only the characters named in the prompt.
```

## Steps

1. **Character sheet first.** Write a short description of each main character (body shape, skin colour, face, everyday clothes, night clothes) and generate one reference sheet with front and side views and four expressions. Attach this sheet to every later prompt.
2. **Clothing per story.** Before writing prompts for a story, decide what each character wears on each page (pyjamas in bed, winter coat in snow…) and write it into every prompt. If you leave it out, the model changes the clothes from page to page.
3. **One prompt per page**, named `01.png` … `09.png`. List what must be visible: everything the text on that page mentions (five messy things, three robins, torn calendar pages…).
4. **Layout freedom.** A page can be one scene, two or three connected scenes, or a 4-panel grid; panels are joined by curves, not straight lines. Pictures have irregular outlines and parts can stick out past the edge (a kite, a tree top, a splash).
5. **Imagined scenes** (a story inside the story, a dream, a worry, a plan) go inside a cloud-shaped outline.
6. **No text in pictures.** Draw notes, lists, letters and signs blank; the courseware prints the words on top with `scene.overlay`.
7. **Decorations.** 4–8 small objects from the story, each a separate transparent PNG in `assets/decor/` (a leaf, a button, a teacup…).
8. **Check every picture** against the page text and the anatomy rules before using it: extra hands, extra characters, ghost copies, changed clothes, missing objects. List the ones to redraw with a corrected prompt.

Then run `scripts/make_webp.py <courseware_dir>` and rebuild.
