#!/usr/bin/env python3
"""Generate the 22 TAROT GAUNTLET arcana bookend cards.

Deterministic HeroImage JSONs — one card per major arcana — used by
TarotGauntletGame as the scenario title card and as the end-screen
art fallback when a finale CG hasn't been generated (which previously
leaked dev placeholder text to the player).

Card: 110x170. Dark face, double border in the arcana accent, roman
numeral at top, geometric motif center, name plate at bottom. Accents
mirror GauntletCardFace._ARCANA_ACCENT — keep the two tables in sync.

Output: godot/resources/games/gauntlet_cards/<arcana>.json
Run twice → identical bytes (no RNG).
"""
import json
import math
import os

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
    "../../resources/games/gauntlet_cards"))

W, H = 110, 170

# name → (roman, display, accent rgb 0-255)
ARCANA = {
    "fool":             ("0",     "THE FOOL",       (217, 173, 71)),
    "magician":         ("I",     "THE MAGICIAN",   (199, 82, 66)),
    "priestess":        ("II",    "PRIESTESS",      (87, 133, 184)),
    "empress":          ("III",   "THE EMPRESS",    (97, 158, 97)),
    "emperor":          ("IV",    "THE EMPEROR",    (158, 158, 173)),
    "hierophant":       ("V",     "HIEROPHANT",     (194, 173, 107)),
    "lovers":           ("VI",    "THE LOVERS",     (199, 117, 133)),
    "chariot":          ("VII",   "THE CHARIOT",    (133, 153, 173)),
    "strength":         ("VIII",  "STRENGTH",       (209, 107, 61)),
    "hermit":           ("IX",    "THE HERMIT",     (148, 143, 112)),
    "wheel_of_fortune": ("X",     "THE WHEEL",      (92, 148, 143)),
    "justice":          ("XI",    "JUSTICE",        (117, 138, 163)),
    "hanged_man":       ("XII",   "HANGED MAN",     (107, 148, 153)),
    "death":            ("XIII",  "DEATH",          (122, 51, 61)),
    "temperance":       ("XIV",   "TEMPERANCE",     (143, 122, 168)),
    "devil":            ("XV",    "THE DEVIL",      (153, 56, 66)),
    "tower":            ("XVI",   "THE TOWER",      (214, 112, 56)),
    "star":             ("XVII",  "THE STAR",       (92, 143, 204)),
    "moon":             ("XVIII", "THE MOON",       (153, 163, 189)),
    "sun":              ("XIX",   "THE SUN",        (230, 189, 77)),
    "judgement":        ("XX",    "JUDGEMENT",      (204, 148, 107)),
    "world":            ("XXI",   "THE WORLD",      (92, 148, 128)),
}


def hexc(rgb):
    return "#%02x%02x%02x" % rgb


def scaled(rgb, f):
    return tuple(min(255, max(0, int(c * f))) for c in rgb)


# op helpers (indices resolved per-card palette)
def fill(c): return {"op": "fill", "color": c}
def rect(x, y, w, h, c): return {"op": "rect", "xywh": [x, y, w, h], "color": c}
def hline(y, x0, x1, c): return {"op": "hline", "y": y, "x_range": [x0, x1], "color": c}
def vline(x, y0, y1, c): return {"op": "vline", "x": x, "y_range": [y0, y1], "color": c}
def dot(x, y, c, s=1): return {"op": "dot", "xy": [x, y], "size": s, "color": c}
def poly(pts, c): return {"op": "poly", "points": pts, "color": c}
def pline(pts, c): return {"op": "polyline", "points": pts, "color": c}
def text(x, y, s, c): return {"op": "text", "xy": [x, y], "s": s, "color": c}
def disk(x, y, r, c): return {"op": "disk", "xy": [x, y], "r": r, "color": c}
def ring(x, y, r, c): return {"op": "ring", "xy": [x, y], "r": r, "color": c}
def noise(x, y, w, h, d, c, seed=7):
    return {"op": "noise", "xywh": [x, y, w, h], "density": d, "seed": seed, "color": c}
def shade(x, y, w, h, a, c):
    return {"op": "shade", "xywh": [x, y, w, h], "amount": a, "color": c}


# Palette slots per card:
# 0 near-black bg  1 face dark  2 accent  3 accent dim  4 accent bright
# 5 parchment text 6 deep shadow
CX, CY = W // 2, 92          # motif center


def motif(name):
    """Geometric center-piece per arcana, colors 2/3/4."""
    L = []
    if name == "fool":
        # the cliff edge + the low sun + the first step
        L += [poly([[16, 118], [58, 104], [58, 130], [16, 130]], 3),
              vline(58, 104, 130, 2),
              disk(78, 72, 10, 4), ring(78, 72, 13, 3),
              pline([[58, 104], [66, 96]], 2), dot(66, 96, 4, 2)]
    elif name == "magician":
        # the lemniscate over the workbench line
        L += [ring(CX - 10, 84, 9, 2), ring(CX + 10, 84, 9, 2),
              hline(112, 26, 84, 3), dot(CX, 84, 4, 2)]
    elif name == "priestess":
        # two pillars + the veil moon
        L += [rect(28, 64, 8, 56, 3), rect(74, 64, 8, 56, 3),
              disk(CX, 74, 9, 4), disk(CX + 4, 72, 8, 1),
              hline(120, 24, 86, 2)]
    elif name == "empress":
        # the wheat field + venus circle-cross
        L += [ring(CX, 74, 10, 2), vline(CX, 84, 96, 2), hline(90, CX - 6, CX + 7, 2)] + \
             [pline([[26 + i * 12, 122], [30 + i * 12, 104]], 3) for i in range(6)] + \
             [dot(30 + i * 12, 103, 4, 2) for i in range(6)]
    elif name == "emperor":
        # the throne — square, high back, hard angles
        L += [rect(38, 66, 34, 8, 3), rect(40, 74, 8, 40, 3), rect(62, 74, 8, 40, 3),
              rect(40, 100, 30, 8, 2), dot(42, 70, 4, 3), dot(68, 70, 4, 3)]
    elif name == "hierophant":
        # the crossed keys
        L += [pline([[38, 68], [70, 112]], 2), pline([[70, 68], [38, 112]], 2),
              ring(38, 66, 5, 4), ring(70, 66, 5, 4),
              rect(66, 108, 8, 4, 3), rect(34, 108, 8, 4, 3)]
    elif name == "lovers":
        # two interlocked rings under a small sun
        L += [ring(CX - 8, 92, 11, 2), ring(CX + 8, 92, 11, 4), disk(CX, 62, 6, 3)]
    elif name == "chariot":
        # the canopy + two wheels
        L += [rect(32, 66, 46, 6, 3), vline(34, 72, 96, 3), vline(75, 72, 96, 3),
              rect(32, 94, 46, 12, 2),
              ring(40, 116, 8, 4), ring(70, 116, 8, 4),
              dot(40, 116, 2, 2), dot(70, 116, 2, 2)]
    elif name == "strength":
        # the mane — concentric warmth around a steady eye
        L += [ring(CX, 88, 16, 2), ring(CX, 88, 12, 3), ring(CX, 88, 20, 3),
              disk(CX, 88, 5, 4),
              pline([[CX - 26, 112], [CX + 26, 112]], 3)]
    elif name == "hermit":
        # the lantern on the staff, one lit dot
        L += [vline(64, 62, 122, 3),
              rect(38, 76, 16, 20, 3), disk(46, 86, 4, 4),
              pline([[46, 70], [46, 76]], 2), pline([[38, 96], [54, 96]], 2)]
    elif name == "wheel_of_fortune":
        # the wheel — spokes at eighths
        L += [ring(CX, 88, 22, 2), ring(CX, 88, 8, 4)]
        for k in range(8):
            a = k * math.pi / 4.0
            L.append(pline([[CX + int(8 * math.cos(a)), 88 + int(8 * math.sin(a))],
                            [CX + int(22 * math.cos(a)), 88 + int(22 * math.sin(a))]], 3))
    elif name == "justice":
        # the scales, level
        L += [vline(CX, 62, 108, 2), hline(70, CX - 22, CX + 23, 2),
              pline([[CX - 22, 70], [CX - 26, 84]], 3), pline([[CX - 18, 70], [CX - 14, 84]], 3),
              pline([[CX + 22, 70], [CX + 18, 84]], 3), pline([[CX + 26, 70], [CX + 30, 84]], 3),
              rect(CX - 28, 84, 16, 3, 4), rect(CX + 14, 84, 16, 3, 4),
              rect(CX - 10, 108, 20, 4, 3)]
    elif name == "hanged_man":
        # the gallows + the inverted triangle (stillness)
        L += [hline(64, 30, 80, 3), vline(30, 64, 122, 3),
              pline([[62, 64], [62, 76]], 2),
              poly([[50, 78], [74, 78], [62, 102]], 2),
              ring(62, 108, 5, 4)]
    elif name == "death":
        # the scythe arc + the horizon it clears
        L += [pline([[36, 116], [76, 116]], 3),
              vline(66, 66, 112, 3),
              poly([[66, 66], [40, 72], [34, 84], [52, 78], [66, 74]], 2),
              dot(36, 116, 4, 2), dot(50, 116, 4, 2), dot(64, 116, 4, 2)]
    elif name == "temperance":
        # two cups, the pour between them
        L += [rect(34, 74, 16, 12, 3), rect(60, 96, 16, 12, 3),
              pline([[50, 80], [58, 88], [60, 96]], 4),
              pline([[52, 82], [60, 90]], 2),
              hline(86, 34, 50, 4), hline(108, 60, 76, 4)]
    elif name == "devil":
        # the horns + the chain links below
        L += [pline([[40, 66], [36, 84], [44, 92]], 2), pline([[70, 66], [74, 84], [66, 92]], 2),
              disk(CX, 92, 8, 3),
              ring(47, 114, 5, 4), ring(57, 118, 5, 4), ring(67, 114, 5, 4)]
    elif name == "tower":
        # the tower + the bolt
        L += [rect(46, 74, 18, 46, 3), rect(44, 70, 22, 6, 2),
              dot(50, 66, 2, 2), dot(55, 64, 2, 2), dot(60, 66, 2, 2),
              pline([[78, 56], [64, 76], [72, 78], [58, 98]], 4),
              dot(50, 88, 1, 6), dot(58, 100, 1, 6)]
    elif name == "star":
        # the eight-ray star + the small one
        L += [disk(CX, 84, 4, 4),
              pline([[CX, 62], [CX, 106]], 2), pline([[CX - 20, 84], [CX + 20, 84]], 2),
              pline([[CX - 13, 71], [CX + 13, 97]], 3), pline([[CX + 13, 71], [CX - 13, 97]], 3),
              dot(76, 64, 4, 2), dot(34, 108, 3, 1)]
    elif name == "moon":
        # crescent + the falling drops
        L += [disk(CX, 80, 15, 4), disk(CX + 8, 76, 13, 1),
              dot(40, 108, 3, 2), dot(55, 114, 3, 2), dot(70, 108, 3, 2),
              pline([[30, 122], [80, 122]], 3)]
    elif name == "sun":
        # the radiant disk
        L += [disk(CX, 86, 12, 4), ring(CX, 86, 15, 2)]
        for k in range(8):
            a = k * math.pi / 4.0
            L.append(pline([[CX + int(19 * math.cos(a)), 86 + int(19 * math.sin(a))],
                            [CX + int(26 * math.cos(a)), 86 + int(26 * math.sin(a))]], 2))
    elif name == "judgement":
        # the trumpet, angled, with the sound-rays
        L += [pline([[40, 106], [66, 78]], 3), pline([[42, 108], [68, 80]], 3),
              poly([[66, 78], [78, 66], [82, 74], [70, 84]], 2),
              pline([[84, 60], [88, 56]], 4), pline([[88, 68], [93, 66]], 4),
              pline([[80, 54], [82, 49]], 4)]
    elif name == "world":
        # the wreath — an oval of leaves
        for k in range(12):
            a = k * math.pi / 6.0
            x = CX + int(20 * math.cos(a))
            y = 88 + int(26 * math.sin(a))
            L.append(dot(x, y, 2 if k % 2 else 3, 2))
        L += [ring(CX, 88, 6, 4)]
    return L


def build_card(name, roman, display, accent):
    pal = ["#0b0a10", "#16141c", hexc(accent), hexc(scaled(accent, 0.55)),
           hexc(scaled(accent, 1.35)), "#d8cfba", "#060608"]
    layers = [
        fill(0),
        rect(4, 4, W - 8, H - 8, 1),
        # double border
        hline(6, 6, W - 6, 2), hline(H - 7, 6, W - 6, 2),
        vline(6, 6, H - 6, 2), vline(W - 7, 6, H - 6, 2),
        hline(10, 10, W - 10, 3), hline(H - 11, 10, W - 10, 3),
        vline(10, 10, H - 10, 3), vline(W - 11, 10, H - 10, 3),
        # corner ticks
        dot(8, 8, 4, 2), dot(W - 9, 8, 4, 2), dot(8, H - 9, 4, 2), dot(W - 9, H - 9, 4, 2),
        # face texture
        noise(11, 11, W - 22, H - 22, 0.05, 0, 3),
        noise(11, 11, W - 22, H - 22, 0.02, 3, 11),
        # roman numeral, centered-ish
        text(CX - len(roman) * 2, 20, roman, 5),
        hline(30, 30, W - 30, 3),
        # motif field vignette
        shade(14, 40, W - 28, 96, 0.12, 6),
    ]
    layers += motif(name)
    # name plate
    layers += [
        hline(138, 20, W - 20, 3),
        rect(14, 144, W - 28, 14, 6),
        text(CX - len(display) * 2, 148, display, 2),
    ]
    return {"id": "arcana_" + name, "w": W, "h": H, "palette": pal, "layers": layers}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (roman, display, accent) in sorted(ARCANA.items()):
        card = build_card(name, roman, display, accent)
        path = os.path.join(OUT, name + ".json")
        with open(path, "w") as f:
            json.dump(card, f, indent=1)
            f.write("\n")
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
