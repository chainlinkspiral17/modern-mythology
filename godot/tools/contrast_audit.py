#!/usr/bin/env python3
"""contrast_audit.py — measure text contrast across the slowstick UIs.

The Earthman fix (2026-07-30) proved the failure mode: a palette that
LOOKS moody in the editor measures 1.5:1 in the field ("the color
scheme is nightmarish"). Eyeballs lie about contrast; WCAG math does
not. This walks every game scene, pairs each file's BACKGROUND-ish
color constants with its TEXT-ish constants, and prints every pair
below threshold.

Heuristic classification by constant name — a lead generator, not a
verdict: a flagged pair means "open the file and look", because some
constants never render as text on that background. Zero output means
the palette CANNOT produce an unreadable text-on-panel pair, which is
the state to keep.

Usage:  python3 godot/tools/contrast_audit.py [--all] [dir ...]
        default scans godot/scenes/games; --all lists passing pairs too
"""
import os, re, sys

BG_HINTS   = ("BG", "PANEL", "DARK", "SHELF", "INK", "CORTEX", "BASE")
TEXT_HINTS = ("TXT", "TEXT", "CREAM", "BONE", "LABEL", "GOLD", "ACCENT",
              "AMBER", "WHITE", "ROSE", "MAUVE", "DIM", "SILVER", "FOAM",
              "GREEN", "RED", "YELLOW", "CYAN", "RUST", "SEA", "SAND")
# Names that are paint, not type — skip as "text" even if they match a
# hint (e.g. C_SEA is the bay fill in Salmonberry).
NEVER_TEXT = ("BG", "PANEL", "SHELF", "RIVER", "ROAD", "ROOF", "WOOD",
              "FIR", "GROUND", "SKY", "CART")

BODY_MIN  = 4.5
LARGE_MIN = 3.0    # for *_DIM / de-emphasis names we accept large-text bar

RX = re.compile(
    r'const\s+(C_[A-Z0-9_]+)\s*:?=\s*Color\(\s*'
    r'(?:"([0-9a-fA-F]{6,8})"|([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+))')


def lum(rgb):
    def ch(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_colors(path):
    out = {}
    for m in RX.finditer(open(path, encoding="utf-8").read()):
        name = m.group(1)
        if m.group(2):
            h = m.group(2)
            rgb = tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        else:
            rgb = (float(m.group(3)), float(m.group(4)), float(m.group(5)))
        out[name] = rgb
    return out


def classify(name):
    core = name[2:]  # strip C_
    is_bg = any(h in core for h in BG_HINTS)
    is_text = (any(h in core for h in TEXT_HINTS)
               and not any(h in core for h in NEVER_TEXT))
    return is_bg, is_text


def is_paint_split(name, colors):
    """A NAME with a NAME_TXT sibling has explicitly split type from
    paint — the base constant is paint and exempt from the text audit
    (the _TXT sibling is what gets judged)."""
    return not name.endswith("_TXT") and (name + "_TXT") in colors


def main():
    show_all = "--all" in sys.argv
    roots = [a for a in sys.argv[1:] if not a.startswith("--")] \
        or ["godot/scenes/games"]
    fails = 0
    files = 0
    for root in roots:
        for dp, _, fns in os.walk(root):
            for fn in sorted(fns):
                if not fn.endswith(".gd"):
                    continue
                path = os.path.join(dp, fn)
                colors = parse_colors(path)
                bgs = {n: c for n, c in colors.items() if classify(n)[0]}
                txts = {n: c for n, c in colors.items() if classify(n)[1]}
                if not bgs or not txts:
                    continue
                files += 1
                # text is judged against the DARKEST background in the
                # file — the panel the type most plausibly sits on.
                bg_name = min(bgs, key=lambda n: lum(bgs[n]))
                bg = bgs[bg_name]
                if lum(bg) > 0.5:
                    continue   # light-paper UIs need the inverse audit
                for tn, tc in sorted(txts.items()):
                    if is_paint_split(tn, colors):
                        continue
                    ratio = contrast(tc, bg)
                    need = LARGE_MIN if "DIM" in tn or "THIN" in tn else BODY_MIN
                    if ratio < need:
                        fails += 1
                        print("%-72s %-12s on %-10s %5.2f:1  (need %.1f)"
                              % (path, tn, bg_name, ratio, need))
                    elif show_all:
                        print("%-72s %-12s on %-10s %5.2f:1  ok"
                              % (path, tn, bg_name, ratio))
    print("\n%d file(s) with palettes · %d failing pair(s)" % (files, fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
