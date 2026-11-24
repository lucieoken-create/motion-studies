---
name: motion-studies
description: Add a scroll-driven motion study (card unfold, card flip, stripe swell, type cascade, fluid blobs, ribbon twist, cell fill, corner bounce, line visualizer) to a web page and restyle it to the project's brand. Use when someone asks for one of these animations by name, wants a scroll animation that reveals an image or card, or wants a moving hero background.
---

# motion-studies

Each study in this repo is one self-contained HTML file: a sticky stage inside a tall scroll section, with a small script that turns scroll progress (0 to 1) into CSS transforms. No libraries.

| Study | File | What happens |
| --- | --- | --- |
| Card unfold | `card-unfold/index.html` | A card folded in three opens flap by flap, then grows to fill the screen |
| Card flip | `card-flip/index.html` | A wide photo splits into four strips that flip into playing cards, then fan out |
| Stripe swell | `stripe-swell/index.html` | A column of stripes swells and pinches, then widens to fill the screen |
| Type cascade | `type-cascade/index.html` | A repeated word swirls inside merging liquid shapes; the pointer pushes words away |
| Fluid blobs | `fluid-blobs/index.html` | Drifting circles melt together into thick blobs with blended colors; the pointer is a circle too |
| Ribbon twist | `ribbon-twist/index.html` | A ribbon of color bands glides down the page, then turns over |
| Cell fill | `cell-fill/index.html` | A fixed spreadsheet grid animates through cell colors alone; one cell follows the pointer |
| Corner bounce | `corner-bounce/index.html` | An icon, word or image bounces around the stage, changing color at each edge; swiping nudges it |
| Line visualizer | `line-visualizer/index.html` | Thin lines with trails form strands, rings and loops; scroll switches pattern, the pointer is the focus |

The two card studies move DOM elements with CSS transforms and only change when the page scrolls. The other five draw on a `<canvas>`: `draw(p, t)` takes scroll progress `p` (0 to 1) and the time `t` in seconds, so they keep drifting between scrolls. Type cascade, cell fill and corner bounce ignore `p`: their sections are one screen tall, and they only play and react to the pointer.

## Adding a study to a project

1. **Read the study file first.** Keep its structure: the tall section (`height: 420vh`), the sticky `.stage`, and the `render()` function that reads scroll progress.
2. **Map the theme variables to the project's tokens.** Every color and font comes from the variables at the top of the stylesheet (`--bg`, `--ink`, `--surface`, `--accent`, `--accent-2`, `--muted`, `--dark`, the three `--font-*` variables, `--back-mark`). Point them at the project's own tokens; don't hard-code new colors further down. If the project has a design system or DESIGN.md, read it before choosing values.
3. **Swap the content.** Card unfold: edit the `<template id="sheetTpl">` (three rows, one per panel). Card flip: set the `PHOTOS` entry for your theme to a wide image, about 3:1, and change `N` for more or fewer cards (also extend `FAN_R` and `FAN_Y` to match).
4. **Port it into the project's stack.** In React or Vue, render the markup in a component and run the same `render()` logic in an effect on scroll and resize, with cleanup. Keep `requestAnimationFrame` throttling. Scope the class names if they could collide.
4a. **Canvas studies.** Keep `readTheme()`, `size()`, `draw(p, t)` and the `frame()` loop together. Colors come from `C`, which `readTheme()` fills from the CSS variables, so call it again whenever the project's theme changes. Content is the constants at the top of the study script (`K`, `N`, `WORDS`, `TURNS`, `PER_COLOR`), and `LOOP` is the number of seconds before the motion repeats. To use one as a background with no scroll section, call `draw()` with a fixed `p` and the running time. In a component, cancel the `requestAnimationFrame` loop and remove the pointer listeners on cleanup.
5. **Retime only through the timing block.** Each step is `ease(seg(p, start, end))`. Overlapping ranges make steps blend; gaps make pauses.
6. **Keep reduced motion.** When `prefers-reduced-motion: reduce` is set, render the end state and skip the animation.

## Check before handing back

- Scroll through the whole section at desktop and phone widths and look at the start, the middle of each step and the end.
- When the pieces sit flat, there are no visible seams or gaps between slices.
- Text inside the card stays readable at every size the card passes through.
- Nothing else on the page jumps when the sticky stage starts and ends.
- Canvas studies: the drawing is sharp on a high-density screen, it stops redrawing once it's scrolled off screen, and type cascade and fluid blobs hold a smooth frame rate (raise `PX` if they don't).
