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
    "s": {
        "advance": 0.32,
        "strokes": [
            [
                # Top loop curve
                ((0.04, 0.45), (0.04, 0.62), (0.18, 0.62), (0.24, 0.52)),
                # Diagonal across middle
                ((0.24, 0.52), (0.20, 0.42), (0.06, 0.34), (0.10, 0.20)),
                # Bottom curl
                ((0.10, 0.20), (0.14, 0.06), (0.26, 0.00), (0.30, 0.10)),
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
