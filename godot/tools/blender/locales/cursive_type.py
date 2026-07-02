"""
cursive_type.py
══════════════════════════════════════════════════════════════════
A Bezier-based cursive type tool. Each glyph is defined as a list
of "strokes" (continuous pen movements), each stroke is a list of
cubic Bezier segments (p0, c1, c2, p3). The renderer samples each
segment at high resolution and emits tube segments between
consecutive samples via a caller-provided draw_tube callback.

Coordinates are in "cap-height units": baseline at y=0, capital
height at y=1.0. Lowercase x-height is ~0.62. Descenders go below
y=0 (down to -0.20 typically). Ascenders rise above x-height up
to 1.0 (matching capital height).

Letter advance widths and kerning are explicit so the script
auto-spaces correctly — no more hand-tweaking each letter's start.

Distinct from the earlier hand-traced polyline approach: real
smooth curves, no kinks, consistent stroke width via the caller's
tube radius.
══════════════════════════════════════════════════════════════════
"""

import math


# Each glyph:
#   advance: distance to advance the pen after drawing (in cap units)
#   strokes: list of strokes. Each stroke is a list of cubic Beziers.
#            Each Bezier is ((p0x, p0y), (c1x, c1y), (c2x, c2y), (p3x, p3y))
GLYPHS = {

    # ── CAPITAL D ───────────────────────────────────────────────
    "D": {
        "advance": 0.55,
        "strokes": [
            # Spine — slight cursive lean to the right
            [
                ((0.04, 0.00), (0.04, 0.33), (0.06, 0.66), (0.08, 1.00)),
            ],
            # Right loop — cubic Bezier sweeping right then back to baseline
            [
                ((0.08, 1.00), (0.40, 1.02), (0.52, 0.78), (0.52, 0.50)),
                ((0.52, 0.50), (0.52, 0.22), (0.40, -0.02), (0.08, 0.00)),
            ],
        ],
    },

    # ── APOSTROPHE ─────────────────────────────────────────────
    "'": {
        "advance": 0.16,
        "strokes": [
            # Short hook above x-height
            [
                ((0.04, 0.90), (0.08, 1.18), (0.14, 1.20), (0.14, 1.00)),
            ],
        ],
    },

    # ── CAPITAL A (cursive style — slight curves on the legs) ──
    "A": {
        "advance": 0.58,
        "strokes": [
            # Left leg, slight inward curve
            [
                ((0.02, 0.00), (0.10, 0.35), (0.18, 0.70), (0.28, 1.00)),
            ],
            # Right leg, slight outward curve
            [
                ((0.28, 1.00), (0.38, 0.70), (0.46, 0.35), (0.55, 0.00)),
            ],
            # Crossbar
            [
                ((0.14, 0.44), (0.21, 0.44), (0.36, 0.44), (0.42, 0.44)),
            ],
        ],
    },

    # ── LOWERCASE m — three humps as one continuous wave ───────
    "m": {
        "advance": 0.75,
        "strokes": [
            # Single continuous wave: up-down-up-down-up-down
            [
                ((0.00, 0.00), (0.00, 0.35), (0.03, 0.58), (0.12, 0.58)),
                ((0.12, 0.58), (0.20, 0.58), (0.20, 0.00), (0.22, 0.00)),
                ((0.22, 0.00), (0.22, 0.35), (0.25, 0.58), (0.34, 0.58)),
                ((0.34, 0.58), (0.42, 0.58), (0.42, 0.00), (0.44, 0.00)),
                ((0.44, 0.00), (0.44, 0.35), (0.47, 0.58), (0.56, 0.58)),
                ((0.56, 0.58), (0.64, 0.58), (0.64, 0.00), (0.66, 0.00)),
            ],
        ],
    },

    # ── LOWERCASE b ────────────────────────────────────────────
    "b": {
        "advance": 0.45,
        "strokes": [
            # Tall stem
            [
                ((0.02, 0.00), (0.02, 0.35), (0.04, 0.70), (0.05, 1.00)),
            ],
            # Bottom bowl — closed loop
            [
                ((0.05, 0.30), (0.05, 0.45), (0.18, 0.55), (0.30, 0.50)),
                ((0.30, 0.50), (0.40, 0.45), (0.42, 0.30), (0.40, 0.18)),
                ((0.40, 0.18), (0.38, 0.05), (0.20, -0.02), (0.05, 0.04)),
            ],
        ],
    },

    # ── LOWERCASE r — short stem + small flag ──────────────────
    "r": {
        "advance": 0.30,
        "strokes": [
            # Stem
            [
                ((0.02, 0.00), (0.02, 0.20), (0.04, 0.45), (0.06, 0.58)),
            ],
            # Small flag/hook at the top
            [
                ((0.06, 0.58), (0.14, 0.65), (0.22, 0.60), (0.26, 0.50)),
            ],
        ],
    },

    # ── LOWERCASE o — closed oval ──────────────────────────────
    "o": {
        "advance": 0.42,
        "strokes": [
            [
                ((0.04, 0.30), (0.04, 0.52), (0.14, 0.62), (0.23, 0.62)),
                ((0.23, 0.62), (0.32, 0.62), (0.38, 0.52), (0.38, 0.30)),
                ((0.38, 0.30), (0.38, 0.08), (0.32, 0.00), (0.23, 0.00)),
                ((0.23, 0.00), (0.14, 0.00), (0.04, 0.08), (0.04, 0.30)),
            ],
        ],
    },

    # ── LOWERCASE s — cursive S shape ──────────────────────────
    # A forward 's' has its middle diagonal running UPPER-LEFT to
    # LOWER-RIGHT ("\\" direction). The previous version had the
    # diagonal going upper-RIGHT to lower-LEFT, which read as a
    # backwards/reversed S — user explicitly called this out twice.
    # Now the top arch ENDS at the LEFT (upper portion), the diagonal
    # descends to the RIGHT, and the bottom arch starts there.
    "s": {
        "advance": 0.32,
        "strokes": [
            [
                # Top arch — over the top, anchored both ends at z=0.40,
                # peak at z=0.62. Forms the top loop of the S.
                ((0.04, 0.40), (0.04, 0.62), (0.24, 0.62), (0.24, 0.40)),
                # Middle diagonal — UPPER-LEFT to LOWER-RIGHT (forward S)
                ((0.04, 0.40), (0.08, 0.30), (0.20, 0.30), (0.24, 0.20)),
                # Bottom arch — under the bottom, anchored both ends at z=0.20,
                # dip at z=0.0. Forms the bottom loop of the S.
                ((0.04, 0.20), (0.04, 0.0), (0.24, 0.0), (0.24, 0.20)),
            ],
        ],
    },

    # ── LOWERCASE i — short stem + tittle ──────────────────────
    "i": {
        "advance": 0.16,
        "strokes": [
            # Stem
            [
                ((0.05, 0.00), (0.05, 0.20), (0.07, 0.45), (0.08, 0.58)),
            ],
            # Tittle (dot above) — small closed loop
            [
                ((0.04, 0.82), (0.04, 0.92), (0.12, 0.92), (0.12, 0.82)),
                ((0.12, 0.82), (0.12, 0.74), (0.04, 0.74), (0.04, 0.82)),
            ],
        ],
    },
}


# ════════════════════════════════════════════════════════════════
# BLOCK GLYPHS — big chunky letters for signage that needs to read
# at distance through the screen post-process. Cursive at this
# resolution smears to illegibility; block letters made of straight
# strokes survive the ASCII/dither/scanline cascade much better.
# ════════════════════════════════════════════════════════════════

BLOCK_GLYPHS = {
    "D": {
        "advance": 0.60,
        "strokes": [
            [(0.00, 0.00), (0.00, 1.00), (0.45, 1.00),
             (0.55, 0.85), (0.55, 0.15), (0.45, 0.00),
             (0.00, 0.00)],
        ],
    },
    "'": {
        "advance": 0.14,
        "strokes": [
            [(0.04, 0.85), (0.10, 1.10), (0.12, 1.05)],
        ],
    },
    "A": {
        "advance": 0.62,
        "strokes": [
            [(0.00, 0.00), (0.30, 1.00), (0.60, 0.00)],
            [(0.12, 0.40), (0.48, 0.40)],
        ],
    },
    "M": {
        "advance": 0.72,
        "strokes": [
            [(0.00, 0.00), (0.00, 1.00), (0.34, 0.30),
             (0.68, 1.00), (0.68, 0.00)],
        ],
    },
    "B": {
        "advance": 0.55,
        "strokes": [
            [(0.00, 0.00), (0.00, 1.00), (0.40, 1.00),
             (0.52, 0.88), (0.52, 0.62), (0.40, 0.50),
             (0.00, 0.50)],
            [(0.40, 0.50), (0.52, 0.40), (0.52, 0.12),
             (0.40, 0.00), (0.00, 0.00)],
        ],
    },
    "R": {
        "advance": 0.55,
        "strokes": [
            [(0.00, 0.00), (0.00, 1.00), (0.42, 1.00),
             (0.52, 0.88), (0.52, 0.62), (0.42, 0.50),
             (0.00, 0.50)],
            [(0.25, 0.50), (0.55, 0.00)],
        ],
    },
    "O": {
        "advance": 0.60,
        "strokes": [
            [(0.10, 1.00), (0.40, 1.00), (0.55, 0.85),
             (0.55, 0.15), (0.40, 0.00), (0.10, 0.00),
             (-0.05, 0.15), (-0.05, 0.85), (0.10, 1.00)],
        ],
    },
    "S": {
        "advance": 0.55,
        "strokes": [
            [(0.52, 0.92), (0.38, 1.00), (0.10, 1.00),
             (0.00, 0.88), (0.00, 0.68), (0.10, 0.56),
             (0.42, 0.50), (0.52, 0.42), (0.52, 0.10),
             (0.42, 0.00), (0.10, 0.00), (0.00, 0.10)],
        ],
    },
    "I": {
        "advance": 0.10,
        "strokes": [
            [(0.05, 0.00), (0.05, 1.00)],
        ],
    },
    "N": {
        "advance": 0.62,
        "strokes": [
            [(0.00, 0.00), (0.00, 1.00), (0.58, 0.00), (0.58, 1.00)],
        ],
    },
    "E": {
        "advance": 0.50,
        "strokes": [
            [(0.50, 1.00), (0.00, 1.00), (0.00, 0.00), (0.50, 0.00)],
            [(0.00, 0.50), (0.40, 0.50)],
        ],
    },
    "T": {
        "advance": 0.50,
        "strokes": [
            [(0.00, 1.00), (0.50, 1.00)],
            [(0.25, 1.00), (0.25, 0.00)],
        ],
    },
    "W": {
        "advance": 0.78,
        "strokes": [
            [(0.00, 1.00), (0.18, 0.00), (0.38, 0.60),
             (0.58, 0.00), (0.76, 1.00)],
        ],
    },
    "L": {
        "advance": 0.46,
        "strokes": [
            [(0.00, 1.00), (0.00, 0.00), (0.46, 0.00)],
        ],
    },
    "C": {
        "advance": 0.55,
        "strokes": [
            [(0.52, 0.92), (0.40, 1.00), (0.10, 1.00),
             (-0.05, 0.85), (-0.05, 0.15), (0.10, 0.00),
             (0.40, 0.00), (0.52, 0.08)],
        ],
    },
    "H": {
        "advance": 0.58,
        "strokes": [
            [(0.00, 0.00), (0.00, 1.00)],
            [(0.58, 0.00), (0.58, 1.00)],
            [(0.00, 0.50), (0.58, 0.50)],
        ],
    },
    "Q": {
        "advance": 0.62,
        "strokes": [
            [(0.10, 1.00), (0.40, 1.00), (0.55, 0.85),
             (0.55, 0.15), (0.40, 0.00), (0.10, 0.00),
             (-0.05, 0.15), (-0.05, 0.85), (0.10, 1.00)],
            [(0.35, 0.20), (0.60, -0.10)],
        ],
    },
    "U": {
        "advance": 0.58,
        "strokes": [
            [(0.00, 1.00), (0.00, 0.20), (0.10, 0.00),
             (0.48, 0.00), (0.58, 0.20), (0.58, 1.00)],
        ],
    },
}


def render_block_text(text, x_start, y_baseline, cap_height, draw_tube,
                       kerning=0.10, name_prefix="blk"):
    """Render `text` in block letters using BLOCK_GLYPHS. Each stroke
    is a polyline of straight segments — connected via the caller's
    draw_tube callback. Returns the final pen x position."""
    pen_x = x_start
    for ci, char in enumerate(text):
        if char == " ":
            pen_x += 0.30 * cap_height
            continue
        glyph = BLOCK_GLYPHS.get(char.upper())
        if glyph is None:
            pen_x += 0.40 * cap_height
            continue
        for si, stroke in enumerate(glyph["strokes"]):
            for sli in range(len(stroke) - 1):
                a = stroke[sli]
                b = stroke[sli + 1]
                ax = pen_x + a[0] * cap_height
                az = y_baseline + a[1] * cap_height
                bx = pen_x + b[0] * cap_height
                bz = y_baseline + b[1] * cap_height
                draw_tube(f"{name_prefix}_{ci:02d}_{char}_{si}_{sli:02d}",
                          (ax, az), (bx, bz))
        pen_x += glyph["advance"] * cap_height + kerning * cap_height
    return pen_x


def block_text_width(text, cap_height, kerning=0.10):
    """Width of a string when rendered with BLOCK_GLYPHS."""
    w = 0.0
    for char in text:
        if char == " ":
            w += 0.30 * cap_height
            continue
        glyph = BLOCK_GLYPHS.get(char.upper())
        if glyph is None:
            w += 0.40 * cap_height
            continue
        w += glyph["advance"] * cap_height + kerning * cap_height
    if text:
        w -= kerning * cap_height
    return w


def sample_bezier(p0, c1, c2, p3, n_samples):
    """Sample a cubic Bezier at n_samples+1 points (including endpoints).
    Returns [(x, y), ...]."""
    pts = []
    for i in range(n_samples + 1):
        t = i / n_samples
        u = 1.0 - t
        b0 = u * u * u
        b1 = 3.0 * u * u * t
        b2 = 3.0 * u * t * t
        b3 = t * t * t
        x = b0 * p0[0] + b1 * c1[0] + b2 * c2[0] + b3 * p3[0]
        y = b0 * p0[1] + b1 * c1[1] + b2 * c2[1] + b3 * p3[1]
        pts.append((x, y))
    return pts


def render_text(text, x_start, y_baseline, cap_height, draw_tube,
                samples_per_segment=10, kerning=0.04, name_prefix="cur"):
    """Render `text` starting at (x_start, y_baseline). cap_height
    scales the normalized glyph coords to world units. draw_tube
    is a callback `draw_tube(name, (x1, y1), (x2, y2))` invoked for
    every tube segment.

    Returns the final pen x position (useful for placing an underline)."""
    pen_x = x_start
    seg_count = 0
    for ci, char in enumerate(text):
        if char == " ":
            pen_x += 0.30 * cap_height
            continue
        glyph = GLYPHS.get(char)
        if glyph is None:
            pen_x += 0.40 * cap_height
            continue
        for si, stroke in enumerate(glyph["strokes"]):
            for bi, segment in enumerate(stroke):
                p0, c1, c2, p3 = segment
                pts = sample_bezier(p0, c1, c2, p3, samples_per_segment)
                for k in range(len(pts) - 1):
                    a = pts[k]
                    b = pts[k + 1]
                    ax = pen_x + a[0] * cap_height
                    az = y_baseline + a[1] * cap_height
                    bx = pen_x + b[0] * cap_height
                    bz = y_baseline + b[1] * cap_height
                    draw_tube(
                        f"{name_prefix}_{ci:02d}_{char}_{si}_{bi}_{k:02d}",
                        (ax, az), (bx, bz),
                    )
                    seg_count += 1
        pen_x += glyph["advance"] * cap_height + kerning * cap_height
    return pen_x


def text_width(text, cap_height, kerning=0.04):
    """Pre-compute the total width of a string at the given cap_height.
    Useful for centring the text on a panel."""
    w = 0.0
    for char in text:
        if char == " ":
            w += 0.30 * cap_height
            continue
        glyph = GLYPHS.get(char)
        if glyph is None:
            w += 0.40 * cap_height
            continue
        w += glyph["advance"] * cap_height + kerning * cap_height
    # Trailing kerning isn't needed
    if text:
        w -= kerning * cap_height
    return w
