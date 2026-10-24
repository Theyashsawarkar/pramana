# 2. Themed like the desktop, but nothing can be made hard to read

**Status:** Accepted  
**Date:** 2026-10-24

## Context

A password window should look like the rest of the desktop, or people learn to distrust the real one and accept odd-looking fakes. But the user's theme (varna's `~/.local/state/varna/palette.json`, and GTK CSS in `~/.config`) is a file any program running as the user can write: loaded as-is, it could make polkit's message unreadable or the Cancel button vanish.

## Decision

pramana uses anumati's theme module (`lib/theme.py`, the same code): Vyom's layout, and the palette's colours read as data, plain `#rrggbb` only, never as CSS. The palette is used only if the text is readable (4.5:1) on every surface it's drawn on, else pramana's own colours; status colours that aren't readable are replaced by the text colour. The installed code is root-owned and runs with `python -I`, loading the theme module by path from its own directory.

## Consequences

- A tampered palette can change tints, never hide what's asking.
- The two password windows on the desktop, pramana's and anumati's, look alike; a fix to the theme module goes to both repos.
- The checks are pure Python and tested in CI without GTK.
