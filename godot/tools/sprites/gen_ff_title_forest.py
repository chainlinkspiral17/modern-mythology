#!/usr/bin/env python3
"""FEY FAIRE · full-bleed title backdrop · the overgrown gate.

Authored against the user's reference interpretation: a ruined
faire gate deep in fir forest — mossy broken columns, a string-lit
crossbeam, hanging vines, mist behind the gate, ferns and glowing
mushrooms below, a tiny fey seated on the beam, and the kid in the
yellow raincoat watching from the right. 320x180, displayed
full-screen (1280x720). Deterministic; run twice, diff clean.

Emits: resources/games/vol7/fey_faire/hero_images/title_forest_gate.json
Run from repo root: python3 godot/tools/sprites/gen_ff_title_forest.py
"""
import json, os

W, H = 320, 180
OUT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "resources", "games", "vol7", "fey_faire", "hero_images",
    "title_forest_gate.json"))

PAL = [
    "#222c22",  # 0 deep forest
    "#a8b4b0",  # 1 mist sky
    "#39493a",  # 2 mid fir
    "#28352a",  # 3 dark fir
    "#7e908c",  # 4 distant fir in mist
    "#b0aa98",  # 5 column bone
    "#8a8474",  # 6 column shade
    "#7a4a30",  # 7 rust / beam
    "#46603c",  # 8 vine green
    "#5c7a48",  # 9 leaf light
    "#f2d070",  # 10 string light warm
    "#1c2418",  # 11 ground dark
    "#4a6a40",  # 12 fern
    "#6f9455",  # 13 fern tip
    "#58e0c8",  # 14 glow teal
    "#e8c040",  # 15 raincoat yellow
    "#2a2430",  # 16 kid pants / dark accent
    "#f4ecd8",  # 17 fey cream / sparkle
    "#c88848",  # 18 warm mushroom
]

L = []


def add(**op):
    L.append(op)


def fir(x, base_y, w, h, color):
    """A fir as three stacked poly triangles."""
    for tier in range(3):
        ty = base_y - h + tier * (h // 3)
        tw = w * (tier + 2) // 4
        add(op="poly", color=color,
            points=[[x, ty], [x - tw, ty + h // 3 + 2], [x + tw, ty + h // 3 + 2]])
    add(op="vline", x=x, y_range=[base_y - 4, base_y + 4], color=7)


# ── sky + mist ──
add(op="fill", color=0)
add(op="vgrad", y_range=[0, 110], x_range=[16, 304], stops=[1, 1, 4])
# distant firs in the mist
for i, (fx, fh) in enumerate([(120, 30), (150, 38), (185, 32), (215, 40), (95, 26)]):
    fir(fx, 96, 10, fh, 4)

# ── framing forest, both sides ──
for fx, fh, c in [(18, 120, 3), (40, 100, 2), (60, 110, 3),
                  (300, 120, 3), (278, 104, 2), (258, 112, 3)]:
    fir(fx, 130, 22, fh, c)

# ── the gate · two column pairs, broken tops ──
for cx, top in [(74, 26), (104, 40), (216, 40), (246, 26)]:
    add(op="rect", xywh=[cx - 5, top, 10, 120 - top], color=5)
    add(op="rect", xywh=[cx + 2, top, 3, 120 - top], color=6)        # shaded edge
    add(op="rect", xywh=[cx - 5, top, 10, 3], color=6)               # broken cap
    add(op="noise", xywh=[cx - 5, top + 6, 10, 100 - top], color=8,  # moss
        density=0.22, seed=cx)
    add(op="noise", xywh=[cx - 5, top + 30, 10, 60], color=7,        # rust streak
        density=0.08, seed=cx + 1)

# ── crossbeam + string lights ──
add(op="rect", xywh=[70, 34, 180, 4], color=7)
add(op="hline", y=34, x_range=[70, 250], color=6)
# candle bulbs standing on the beam
for i in range(7):
    bx = 82 + i * 26
    add(op="dot", xy=[bx, 32], size=2, color=10)
    add(op="dot", xy=[bx, 30], size=1, color=17)
# a drooping string of lights below
for i in range(11):
    sx = 78 + i * 16
    droop = 8 + (4 if 2 < i < 8 else 1)
    add(op="dot", xy=[sx, 38 + droop], size=2, color=10)
add(op="polyline", color=8, points=[[74, 40], [110, 52], [160, 56], [210, 52], [246, 40]])

# ── vines off the beam ──
for vx, vlen in [(96, 44), (128, 62), (150, 36), (176, 70), (204, 48), (230, 30)]:
    add(op="polyline", color=8,
        points=[[vx, 38], [vx - 2, 38 + vlen // 2], [vx + 1, 38 + vlen]])
    add(op="dot", xy=[vx - 2, 38 + vlen // 3], size=1, color=9)
    add(op="dot", xy=[vx + 1, 38 + vlen - 4], size=1, color=9)

# ── mist behind the gate footing ──
add(op="shade", xywh=[60, 88, 200, 22], color=1, amount=0.35)

# ── ground · ferns ──
add(op="rect", xywh=[0, 118, 320, 62], color=11)
add(op="noise", xywh=[0, 118, 320, 62], color=3, density=0.20, seed=91)
for i in range(22):
    fx = 8 + i * 14
    fy = 128 + (i * 7) % 40
    add(op="polyline", color=12,
        points=[[fx, fy + 10], [fx + 3, fy + 4], [fx + 7, fy]])
    add(op="polyline", color=12,
        points=[[fx + 6, fy + 10], [fx + 3, fy + 4]])
    add(op="dot", xy=[fx + 7, fy], size=1, color=13)
# the path to the gate
add(op="poly", color=3, points=[[150, 118], [170, 118], [200, 180], [120, 180]])
add(op="noise", xywh=[130, 120, 60, 60], color=6, density=0.05, seed=95)

# ── glowing mushrooms ──
add(op="shade", xywh=[28, 124, 22, 16], color=14, amount=0.18)
for mx, my in [(34, 132), (40, 136), (30, 138)]:
    add(op="dot", xy=[mx, my], size=2, color=14)
    add(op="vline", x=mx, y_range=[my + 1, my + 3], color=6)
for mx, my in [(288, 158), (294, 161)]:
    add(op="dot", xy=[mx, my], size=2, color=18)
    add(op="vline", x=mx, y_range=[my + 1, my + 3], color=7)

# ── the fey, seated on the left beam end ──
add(op="dot", xy=[92, 28], size=2, color=17)          # head
add(op="rect", xywh=[91, 30, 3, 4], color=9)          # little green body
add(op="dot", xy=[89, 28], size=1, color=17)          # wing
add(op="dot", xy=[95, 27], size=1, color=17)          # wing
add(op="dot", xy=[92, 26], size=1, color=17)   # a mote of her light

# ── the kid in the yellow raincoat, right foreground ──
add(op="rect", xywh=[286, 120, 10, 8], color=15)      # hood
add(op="rect", xywh=[288, 122, 6, 4], color=16)       # hood shadow (facing away)
add(op="rect", xywh=[285, 128, 12, 14], color=15)     # coat
add(op="vline", x=296, y_range=[128, 141], color=10)  # lit edge
add(op="rect", xywh=[287, 142, 3, 8], color=16)       # legs
add(op="rect", xywh=[292, 142, 3, 8], color=16)
# a sparkle he is looking toward
add(op="dot", xy=[308, 150], size=2, color=17)
add(op="vline", x=308, y_range=[146, 154], color=17)
add(op="hline", y=150, x_range=[304, 312], color=17)

doc = {"id": "title_forest_gate", "w": W, "h": H, "palette": PAL, "layers": L}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
print("wrote", OUT, "layers:", len(L))
