---
name: frog-and-toad-illustration-style
description: Generate consistent Frog and Toad course illustrations in the established square watercolor storybook style. Use when the user asks to generate images, 插画, 画图, sidecar illustrations, workbook icons, emotion cards, or courseware visuals for Frog and Toad chapters, especially from a chapter prompt markdown file such as "*画图.md".
---

# Frog and Toad Illustration Style

## Bundled Prompt Library

`prompts/` ships ready-made prompt lists for all 20 chapters, named in teaching order:
`01-tomorrow.md` … `05-alone.md` (Days with Frog and Toad), `06-down-the-hill.md` … `10-christmas-eve.md` (All Year), `11-a-list.md` … `15-the-dream.md` (Together), `16-spring.md` … `20-the-letter.md` (Are Friends).

When the user asks for a chapter's illustrations without supplying their own prompt file, use the matching bundled file as the source prompt list. A user-supplied `*画图.md` file always takes priority over the bundled copy.

Generating images requires the agent to have an image-generation capability (built-in tool, MCP image server, or API). If none is available, tell the user instead of silently skipping.

## Core Style

Use the built-in image generation workflow by default. Generate raster PNG illustrations, not SVGs.

Apply this style base to every prompt unless the user explicitly changes it:

```text
Square 1:1 children's storybook illustration. Clean white background with lots of empty space. Hand-drawn slightly wobbly black outlines filled with soft warm watercolor colors: olive green, warm brown, tan, cream, soft orange. Simple, uncluttered, friendly, gentle. No text, no words, no labels.
```

Keep the drawings classroom-friendly: readable action, clear facial expression, minimal props, and generous white space.

## Character Model

Keep the two characters visually consistent:

```text
FROG: a tall slim green frog with a friendly face, wearing a green jacket and white-and-green striped trousers.
TOAD: a short plump brown toad with a round belly and big expressive eyes, wearing a brown-and-tan suit jacket and trousers.
```

Use Frog for problem-pointing scenes unless the prompt says otherwise. Use Toad for solution-action scenes and emotion cards unless the prompt says otherwise.

## Workflow

1. Read the user's source prompt file completely.
2. Identify each requested image slot, usually headings like `A1`, `B5`, or `C3`.
3. Preserve the user's scene intent and action verb. Normalize each prompt into a structured image-generation prompt that includes:
   - use case: `illustration-story`
   - asset type: square storybook courseware illustration, workbook icon, or reusable emotion card
   - primary request and scene
   - subject, style, composition, palette, constraints, and avoid list
4. Generate one image per slot. Do not combine distinct slots into one generation request.
5. Save finished images into the relevant chapter folder under `illustrations/`.
6. Name files consistently:

```text
<chapter-id>-<slot>-<short-kebab-description>.png
```

Example:

```text
01-Tomorrow-B5-watered.png
```

7. If the source prompt asks to paste images into an Obsidian Sidecar, create or update that Sidecar with Obsidian embeds:

```text
![[relative/path/to/image.png]]
```

8. If a workbook small image is meant to reuse an existing slot, embed the same image again and label it as reused.

## Prompt Rules

Never put readable text inside the image unless the user explicitly asks for it. For quoted emotions such as `"Drat!"` or `"Now I feel better!"`, show the emotion visually and omit the words.

For Problem boards:

```text
Frog points with one finger at the messy or unfinished item. Frog looks mildly concerned. Keep the problem object visually obvious and remove unrelated room clutter.
```

For Solution boards:

```text
Toad performs the target action. Make the verb visible through pose, motion lines, before/after contrast, arrows, bubbles, dust clouds, water drops, or other small visual cues.
```

For emotion cards:

```text
Toad is the main focus. Use a simple portrait or full-body pose with one small symbolic cue, such as a red scribble cloud, sweat drop, rain cloud, lightning spark, or heart.
```

## Quality Check

Before finishing, verify:

- Every requested slot exists as one PNG.
- Each image is square and has no text.
- Frog remains tall/slim/green; Toad remains short/plump/brown.
- A scenes clearly show Frog pointing.
- B scenes clearly show Toad doing the action.
- C scenes clearly show the intended emotion.
- Files are saved inside the project, not only in the default generated-images folder.
- Sidecar embeds point to the saved project files.

Report the saved folder, the Sidecar path if created, and any reused image such as `B5` for workbook use.
