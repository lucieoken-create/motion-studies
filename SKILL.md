---
name: motion-studies
description: Add a scroll-driven motion study (card unfold, card flip) to a web page and restyle it to the project's brand. Use when someone asks for one of these animations by name or wants a scroll animation that reveals an image or card.
---

# motion-studies

Each study in this repo is one self-contained HTML file: a sticky stage inside a tall scroll section, with a small script that turns scroll progress (0 to 1) into CSS transforms. No libraries.

| Study | File | What happens |
| --- | --- | --- |
| Card unfold | `card-unfold/index.html` | A card folded in three opens flap by flap, then grows to fill the screen |
| Card flip | `card-flip/index.html` | A wide photo splits into four strips that flip into playing cards, then fan out |

## Adding a study to a project

1. **Read the study file first.** Keep its structure: the tall section (`height: 420vh`), the sticky `.stage`, and the `render()` function that reads scroll progress.
2. **Map the theme variables to the project's tokens.** Every color and font comes from the variables at the top of the stylesheet (`--bg`, `--ink`, `--surface`, `--accent`, `--accent-2`, `--muted`, `--dark`, the three `--font-*` variables, `--back-mark`). Point them at the project's own tokens; don't hard-code new colors further down. If the project has a design system or DESIGN.md, read it before choosing values.
3. **Swap the content.** Card unfold: edit the `<template id="sheetTpl">` (three rows, one per panel). Card flip: set `PHOTO` to a wide image, about 3:1, and change `N` for more or fewer cards (also extend `FAN_R` and `FAN_Y` to match).
4. **Port it into the project's stack.** In React or Vue, render the markup in a component and run the same `render()` logic in an effect on scroll and resize, with cleanup. Keep `requestAnimationFrame` throttling. Scope the class names if they could collide.
5. **Retime only through the timing block.** Each step is `ease(seg(p, start, end))`. Overlapping ranges make steps blend; gaps make pauses.
6. **Keep reduced motion.** When `prefers-reduced-motion: reduce` is set, render the end state and skip the animation.

## Check before handing back

- Scroll through the whole section at desktop and phone widths and look at the start, the middle of each step and the end.
- When the pieces sit flat, there are no visible seams or gaps between slices.
- Text inside the card stays readable at every size the card passes through.
- Nothing else on the page jumps when the sticky stage starts and ends.
