#!/usr/bin/env python3
"""
procgen_ps_items.py — generate 16x16 SlowstockSprite JSON icons
for Pirate Summer's duffel items.

Each item icon: transparent background, opaque item silhouette
centered.  Deterministic patterns; no Random.random.

Output path:
  godot/resources/games/vol7/pirate_summer/sprites/items/<id>.json
"""

import json
import os

OUTDIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'resources', 'games', 'vol7', 'pirate_summer', 'sprites', 'items',
)

W, H = 16, 16


def blank():
    return [0] * (W * H)


def px(d, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        d[y * W + x] = c


def rect(d, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(d, x, y, c)


def hline(d, x0, x1, y, c):
    for x in range(x0, x1 + 1):
        px(d, x, y, c)


def vline(d, x, y0, y1, c):
    for y in range(y0, y1 + 1):
        px(d, x, y, c)


def item_smooth_river_stone():
    pal = ["#5a5a5a", "#8a8a8a", "#3a3a3a", "#c8c8c8"]
    d = blank()
    # Oval blob roughly 10x6 in center
    rect(d, 4, 6, 11, 9, 1)
    rect(d, 3, 7, 12, 8, 1)
    px(d, 4, 8, 3)  # highlight
    # dark rim
    for (x, y) in [(3,7),(3,8),(12,7),(12,8),(4,6),(11,6),(4,9),(11,9),(5,10),(10,10)]:
        px(d, x, y, 2)
    return pal, d


def item_used_lens_cap():
    pal = ["#2a2a2a", "#4a4a4a", "#1a1a1a", "#8a8a8a"]
    d = blank()
    # Circle-ish cap
    rect(d, 4, 4, 11, 11, 0)
    rect(d, 3, 5, 12, 10, 0)
    rect(d, 5, 3, 10, 12, 0)
    # inner ring
    rect(d, 6, 6, 9, 9, 1)
    px(d, 7, 7, 3)
    return pal, d


def item_pencil_good_point():
    pal = ["#e0c060", "#8a6a20", "#2a2a2a", "#c8a840"]
    d = blank()
    # Pencil body diagonal-ish · runs from bottom-left to top-right
    for i in range(11):
        x = 2 + i; y = 12 - i
        px(d, x, y, 0)
        if y - 1 >= 0: px(d, x, y - 1, 3)
        if y + 1 < H: px(d, x, y + 1, 1)
    # Tip
    px(d, 12, 1, 2)
    px(d, 13, 2, 2)
    return pal, d


def item_seashell_unbroken():
    pal = ["#e8d0a0", "#c8a870", "#a88450", "#f8e0c0"]
    d = blank()
    # Fan shape
    for y in range(4, 12):
        w = min(y - 3, 12 - y)
        for x in range(8 - w, 8 + w):
            px(d, x, y, 0)
    # Ridges
    for y in [6, 8, 10]:
        for x in range(4, 12):
            if (x + y) % 2 == 0:
                px(d, x, y, 1)
    # Highlight
    px(d, 8, 4, 3)
    px(d, 7, 5, 3)
    return pal, d


def item_bookmark_any():
    pal = ["#2a6a3a", "#1a4a24", "#3a8a50", "#0a2810"]
    d = blank()
    # Leaf-shaped bookmark
    rect(d, 6, 2, 9, 13, 0)
    rect(d, 5, 4, 10, 11, 0)
    rect(d, 7, 1, 8, 14, 0)
    # Veins
    vline(d, 7, 3, 12, 2)
    for y in [5, 8, 11]:
        px(d, 6, y, 2)
        px(d, 9, y, 2)
    return pal, d


def item_lucky_penny():
    pal = ["#b8724a", "#8a5030", "#e0946a", "#4a2810"]
    d = blank()
    # Round penny with highlight
    rect(d, 5, 5, 10, 10, 0)
    rect(d, 4, 6, 11, 9, 0)
    rect(d, 6, 4, 9, 11, 0)
    # Highlight
    for (x, y) in [(5, 5),(6, 4),(7, 5)]:
        px(d, x, y, 2)
    # Shadow
    for (x, y) in [(10, 10),(9, 11),(11, 9)]:
        px(d, x, y, 1)
    # Small figure hint
    px(d, 7, 7, 3)
    px(d, 8, 7, 3)
    px(d, 8, 8, 3)
    return pal, d


def item_field_guide_minerals():
    pal = ["#6a4e2e", "#4a3218", "#a8946a", "#e0d0a0"]
    d = blank()
    # Book (spine on left)
    rect(d, 3, 3, 12, 12, 0)
    # Cover text lines
    hline(d, 5, 10, 6, 3)
    hline(d, 5, 10, 8, 3)
    hline(d, 5, 8, 10, 3)
    # Spine detail
    vline(d, 3, 3, 12, 1)
    vline(d, 4, 3, 12, 2)
    return pal, d


def item_bird_call_whistle():
    pal = ["#8a6a3e", "#5a3e18", "#c8a870", "#3a2810"]
    d = blank()
    # Tube shape
    rect(d, 4, 7, 12, 9, 0)
    # Mouthpiece
    rect(d, 3, 7, 3, 9, 1)
    px(d, 2, 8, 1)
    # Highlight
    hline(d, 4, 12, 7, 2)
    # Air hole
    px(d, 8, 8, 3)
    return pal, d


def item_tide_table_pamphlet():
    pal = ["#e0d8c0", "#a89880", "#3a4a68", "#8a7a60"]
    d = blank()
    # Folded pamphlet body
    rect(d, 3, 3, 12, 13, 0)
    # Fold line
    vline(d, 8, 3, 13, 3)
    # Text rows
    for y in [5, 7, 9, 11]:
        hline(d, 4, 7, y, 1)
        hline(d, 9, 12, y, 1)
    # Header
    hline(d, 4, 12, 4, 2)
    return pal, d


def item_joke_book():
    pal = ["#c84a3a", "#8a2a1a", "#e8e0d0", "#3a1010"]
    d = blank()
    # Red hardcover
    rect(d, 3, 2, 12, 13, 0)
    # Cover text
    hline(d, 5, 10, 5, 2)
    hline(d, 5, 10, 7, 2)
    hline(d, 6, 9, 9, 2)
    # Spine
    vline(d, 3, 2, 13, 1)
    # Corner shadow
    px(d, 12, 13, 3)
    px(d, 12, 12, 3)
    return pal, d


def item_sunflower_seeds():
    pal = ["#c8a842", "#8a6a20", "#e8d090", "#3a2810"]
    d = blank()
    # Bag shape
    rect(d, 4, 4, 11, 13, 0)
    rect(d, 5, 3, 10, 4, 0)
    # Bag top ridge
    hline(d, 5, 10, 3, 1)
    # Seed grid pattern
    for y in [6, 9, 12]:
        for x in [5, 7, 9]:
            px(d, x, y, 1)
    # Highlight
    hline(d, 5, 10, 4, 2)
    return pal, d


def item_portuguese_postcard():
    pal = ["#e8d0a0", "#a88450", "#3a4a68", "#c8a870"]
    d = blank()
    # Postcard body
    rect(d, 2, 4, 13, 12, 0)
    # Border
    for (x, y) in [(2, 4),(13, 4),(2, 12),(13, 12)]:
        px(d, x, y, 1)
    # Small scene sketch (a building silhouette)
    rect(d, 4, 6, 8, 9, 2)
    px(d, 5, 5, 2)
    # Text lines on right
    hline(d, 10, 12, 7, 3)
    hline(d, 10, 12, 9, 3)
    return pal, d


def item_graph_notebook():
    pal = ["#e8e8d8", "#a8a898", "#4a4a5a", "#c8c8b8"]
    d = blank()
    # Notebook body
    rect(d, 3, 2, 12, 13, 0)
    # Grid lines
    for x in [4, 6, 8, 10, 12]:
        vline(d, x, 3, 12, 1)
    for y in [4, 6, 8, 10, 12]:
        hline(d, 3, 12, y, 1)
    # Spiral holes
    for y in [3, 6, 9, 12]:
        px(d, 3, y, 2)
    return pal, d


def item_friendship_bracelet():
    pal = ["#3a6a94", "#2a4a68", "#68a8c8", "#3a884a"]
    d = blank()
    # Circular braid
    for y in [6, 7, 8, 9]:
        for x in range(4, 12):
            c = 0 if (x + y) % 2 == 0 else 3
            px(d, x, y, c)
    # Rim
    for (x, y) in [(3, 7),(3, 8),(12, 7),(12, 8)]:
        px(d, x, y, 1)
    return pal, d


def item_the_treasure_map():
    pal = ["#c8a870", "#8a6a3e", "#3a2818", "#c84a3a"]
    d = blank()
    # Aged paper
    rect(d, 2, 3, 13, 12, 0)
    # Fold creases
    hline(d, 2, 13, 7, 1)
    vline(d, 8, 3, 12, 1)
    # Coastline squiggle
    for (x, y) in [(3, 5),(4, 5),(5, 6),(6, 6),(7, 5),(4, 9),(5, 10),(6, 10),(9, 6),(10, 6),(11, 5),(12, 5),(9, 10),(10, 11),(11, 10)]:
        px(d, x, y, 2)
    # Red X
    px(d, 8, 9, 3)
    px(d, 9, 10, 3)
    px(d, 7, 10, 3)
    px(d, 6, 11, 3)
    return pal, d


def item_old_ships_rope():
    pal = ["#8a6a3e", "#5a4218", "#c8a870", "#3a2810"]
    d = blank()
    # Coiled rope · concentric circles
    for r in [1, 3, 5]:
        cx, cy = 8, 8
        for x in range(W):
            for y in range(H):
                if abs(x - cx) + abs(y - cy) == r + 1:
                    px(d, x, y, 0)
                elif abs(x - cx) + abs(y - cy) == r:
                    px(d, x, y, 2)
    return pal, d


def item_the_leather_satchel():
    pal = ["#8a5e2e", "#5a3618", "#a87e48", "#3a2010"]
    d = blank()
    # Bag body
    rect(d, 3, 5, 12, 13, 0)
    # Flap
    rect(d, 3, 4, 12, 7, 0)
    hline(d, 3, 12, 7, 1)
    # Strap
    vline(d, 4, 2, 5, 1)
    vline(d, 11, 2, 5, 1)
    hline(d, 4, 11, 2, 1)
    # Buckle
    rect(d, 7, 7, 8, 8, 3)
    # Highlight
    hline(d, 4, 11, 5, 2)
    return pal, d


ITEMS = {
    "smooth_river_stone":   item_smooth_river_stone,
    "used_lens_cap":        item_used_lens_cap,
    "pencil_good_point":    item_pencil_good_point,
    "seashell_unbroken":    item_seashell_unbroken,
    "bookmark_any":         item_bookmark_any,
    "lucky_penny":          item_lucky_penny,
    "field_guide_minerals": item_field_guide_minerals,
    "bird_call_whistle":    item_bird_call_whistle,
    "tide_table_pamphlet":  item_tide_table_pamphlet,
    "joke_book":            item_joke_book,
    "sunflower_seeds":      item_sunflower_seeds,
    "portuguese_postcard":  item_portuguese_postcard,
    "graph_notebook":       item_graph_notebook,
    "friendship_bracelet":  item_friendship_bracelet,
    "the_treasure_map":     item_the_treasure_map,
    "old_ships_rope":       item_old_ships_rope,
    "the_leather_satchel":  item_the_leather_satchel,
}


def emit_all():
    os.makedirs(OUTDIR, exist_ok=True)
    for name, fn in ITEMS.items():
        pal_hex, data = fn()
        pal_out = [""] + list(pal_hex)
        data_shifted = [c + 1 for c in data]
        obj = {
            "id": name,
            "notes": f"Procgen item · {name} · generated by procgen_ps_items.py.",
            "palette": pal_out,
            "w": W,
            "h": H,
            "origin": [0, H],
            "data": data_shifted,
        }
        path = os.path.join(OUTDIR, name + ".json")
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        print("wrote", path)


if __name__ == "__main__":
    emit_all()
