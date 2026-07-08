#!/usr/bin/env python3
"""
procgen_ps_tiles.py — generate 16x16 SlowstockSprite JSON tiles
for Pirate Summer's overworld.

Each tile has a small palette (index 0 = transparent by convention;
we use it for opaque colors here since tiles are opaque) and a
16x16 = 256 int data array.  Patterns are deterministic (no
Random.random) so re-runs produce the same output.

Output path:
  godot/resources/games/vol7/pirate_summer/sprites/tiles/<id>.json

Pattern language (short):
  - fill(c) · every pixel = c
  - noise(base, dots, spacing) · fill base then place dots on a lattice
  - hbands(colors) · horizontal stripes cycling through colors
  - vbands(colors) · vertical stripes
  - grain(base, dark) · fine horizontal-grain wood look
  - mottled(a, b, c) · a 3-color low-frequency mottling
  - triangle_dots(base, dark) · scattered small shapes for foliage
"""

import json
import os
import sys

OUTDIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'resources', 'games', 'vol7', 'pirate_summer', 'sprites', 'tiles',
)

W, H = 16, 16


def blank():
    return [0] * (W * H)


def fill(data, c):
    for i in range(W * H):
        data[i] = c


def set_pixel(data, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        data[y * W + x] = c


def dots(data, c, positions):
    for (x, y) in positions:
        set_pixel(data, x, y, c)


def hbands(data, colors):
    for y in range(H):
        col = colors[y % len(colors)]
        for x in range(W):
            data[y * W + x] = col


def vbands(data, colors):
    for x in range(W):
        col = colors[x % len(colors)]
        for y in range(H):
            data[y * W + x] = col


# ── Tile definitions ───────────────────────────────────────────────

def tile_grass():
    # deep forest floor · dark green with occasional lighter blade
    pal = ['#3a5c2c', '#4c6e3a', '#26401e', '#5a7c40']
    d = blank()
    fill(d, 0)
    # scattered lighter blades at fixed positions
    dots(d, 1, [(2,1),(9,2),(4,4),(13,3),(1,6),(7,7),(11,8),(3,10),(14,11),(6,13),(12,14),(0,12),(8,15)])
    # darker specks
    dots(d, 2, [(5,2),(10,5),(2,9),(15,10),(4,14)])
    # rare brightest blade
    dots(d, 3, [(6,3),(12,11)])
    return pal, d


def tile_sand():
    # warm tan with scattered darker specks (pebbles) and shell hints
    pal = ['#c4a874', '#a88854', '#dcc890', '#8a6a3c']
    d = blank()
    fill(d, 0)
    dots(d, 1, [(3,2),(11,4),(6,7),(14,9),(2,12),(9,13),(1,5),(15,15)])
    dots(d, 2, [(5,1),(12,6),(8,9),(4,15),(13,13)])
    dots(d, 3, [(7,4),(2,14)])
    return pal, d


def tile_path():
    # packed dirt · warm brown with pebble specks
    pal = ['#8c7a54', '#6a5a3e', '#a8946a', '#4a3e2a']
    d = blank()
    fill(d, 0)
    dots(d, 1, [(2,3),(9,5),(6,1),(12,7),(4,10),(13,12),(0,14),(10,14),(15,3)])
    dots(d, 2, [(5,6),(11,2),(3,11),(8,15)])
    dots(d, 3, [(7,8),(14,9)])
    return pal, d


def tile_water_deep():
    # dark blue with subtle horizontal ripple lines
    pal = ['#243848', '#1a2a38', '#2e4658']
    d = blank()
    fill(d, 0)
    # every fourth row · a slight lift on odd columns for a ripple hint
    for y in [3, 7, 11, 15]:
        for x in range(W):
            d[y * W + x] = 2
    # occasional deeper spot
    dots(d, 1, [(2,1),(9,5),(14,9),(6,13)])
    return pal, d


def tile_water_shallow():
    # lighter blue-green · you can see the bottom
    pal = ['#4a6a7a', '#3a5a68', '#6a8a98', '#8aa8b4']
    d = blank()
    fill(d, 0)
    for y in [2, 6, 10, 14]:
        for x in range(W):
            d[y * W + x] = 2
    dots(d, 3, [(3,4),(8,8),(12,3),(6,12),(14,13),(1,9)])
    dots(d, 1, [(11,7),(5,5),(2,15)])
    return pal, d


def tile_dock():
    # wooden dock · horizontal-grain planks with subtle nails
    pal = ['#8c6a3e', '#6a4e2e', '#a4844a', '#3a2a1a']
    d = blank()
    # Base plank color · alternating slightly per row for grain
    for y in range(H):
        c = 0 if y % 2 == 0 else 1
        for x in range(W):
            d[y * W + x] = c
    # A gap line every 4 rows for plank edge
    for y in [3, 7, 11, 15]:
        for x in range(W):
            d[y * W + x] = 3
    # A couple nails
    dots(d, 3, [(2,5),(13,5),(2,13),(13,13)])
    return pal, d


def tile_wood_floor():
    # cabin floor · warm brown with wood grain
    pal = ['#7c5c34', '#6a4a24', '#8c6c44', '#4a3220']
    d = blank()
    fill(d, 0)
    # horizontal grain stripes
    for y in [1, 5, 9, 13]:
        for x in range(W):
            d[y * W + x] = 1
    for y in [3, 7, 11, 15]:
        for x in range(W):
            d[y * W + x] = 2
    dots(d, 3, [(4,4),(12,8),(2,12)])
    return pal, d


def tile_rock_wall():
    # dark rock wall · mottled dark grays
    pal = ['#1a1410', '#2a2018', '#3a3028', '#0e0a08']
    d = blank()
    fill(d, 0)
    # mottled blobs
    for (x, y) in [(3,2),(4,2),(3,3),(10,4),(11,4),(10,5),
                    (6,7),(7,7),(7,8),(13,9),(14,9),(14,10),
                    (2,11),(3,11),(3,12),(9,13),(10,13)]:
        set_pixel(d, x, y, 1)
    for (x, y) in [(5,1),(12,6),(1,8),(8,10),(14,13),(6,14)]:
        set_pixel(d, x, y, 2)
    for (x, y) in [(9,3),(2,6),(11,11),(4,15)]:
        set_pixel(d, x, y, 3)
    return pal, d


def tile_cabin_wall():
    # cabin exterior · horizontal plank pattern
    pal = ['#4a3826', '#3a2a1c', '#5c4a34', '#241814']
    d = blank()
    # planks with slight color per band
    for y in range(H):
        band = (y // 4) % 3
        c = [0, 2, 1][band]
        for x in range(W):
            d[y * W + x] = c
    # plank edges every 4 rows
    for y in [3, 7, 11, 15]:
        for x in range(W):
            d[y * W + x] = 3
    return pal, d


def tile_tree_top():
    # dark forest tree canopy · very dark with darker shadow
    pal = ['#1a3a1c', '#0a1e10', '#264a24', '#000000']
    d = blank()
    fill(d, 0)
    # inner darker shadow triangles
    for (x, y) in [(2,3),(3,3),(3,4),(10,5),(11,5),(11,6),
                    (6,9),(7,9),(6,10),(13,11),(13,12)]:
        set_pixel(d, x, y, 1)
    # highlights
    for (x, y) in [(5,1),(12,2),(1,6),(8,4),(14,7),(3,12),(10,14)]:
        set_pixel(d, x, y, 2)
    return pal, d


def tile_brush():
    # chest-high salal · mid-green with brighter tips
    pal = ['#2a4a1e', '#1a3a14', '#4a6c30', '#0a1a08']
    d = blank()
    fill(d, 0)
    for (x, y) in [(2,2),(5,3),(11,2),(14,4),(3,7),(9,6),(13,9),
                    (1,10),(7,11),(11,12),(4,14),(15,14)]:
        set_pixel(d, x, y, 2)
    for (x, y) in [(6,4),(8,8),(2,12),(12,6),(14,11)]:
        set_pixel(d, x, y, 1)
    for (x, y) in [(10,10),(4,5),(13,2)]:
        set_pixel(d, x, y, 3)
    return pal, d


def tile_dune_grass():
    # long dune grass · warm khaki with horizontal strokes
    pal = ['#a4a878', '#8c9060', '#c0c090', '#6a6e48']
    d = blank()
    fill(d, 0)
    for y in [2, 4, 7, 10, 13]:
        for x in range(W):
            d[y * W + x] = 1
    for y in [5, 11]:
        for x in range(W):
            d[y * W + x] = 2
    dots(d, 3, [(3,1),(9,3),(13,8),(6,12),(11,15)])
    return pal, d


def tile_boulder():
    # gray boulder · rounded shape with highlight
    pal = ['#6a6a6a', '#5a5a5a', '#8a8a8a', '#4a4a4a']
    d = blank()
    fill(d, 0)
    # darker outer ring
    for (x, y) in [(0,y) for y in range(H)] + [(15,y) for y in range(H)]:
        set_pixel(d, x, y, 3)
    for x in range(W):
        set_pixel(d, x, 0, 3)
        set_pixel(d, x, 15, 3)
    # highlight on upper-left
    for (x, y) in [(3,2),(4,2),(3,3),(2,4),(4,3)]:
        set_pixel(d, x, y, 2)
    # shadow on lower-right
    for (x, y) in [(11,12),(12,12),(11,13),(13,12),(12,13),(13,13)]:
        set_pixel(d, x, y, 1)
    return pal, d


def tile_bunk():
    # wooden bunk · similar to wood floor but with a mattress hint
    pal = ['#6a4e30', '#5a3e20', '#8a6a4a', '#3a2818']
    d = blank()
    # frame · wood grain
    for y in range(H):
        for x in range(W):
            data_y = y % 4
            d[y * W + x] = 0 if data_y != 2 else 1
    # top-half mattress hint (lighter)
    for y in range(0, 6):
        for x in range(2, 14):
            d[y * W + x] = 2
    # frame edges
    for x in range(W):
        d[0 * W + x] = 3
        d[15 * W + x] = 3
    for y in range(H):
        d[y * W + 0] = 3
        d[y * W + 15] = 3
    return pal, d


def tile_deck_wood():
    # ghost ship deck · deep wood
    pal = ['#5a3e26', '#4a2e18', '#6a4e34', '#241408']
    d = blank()
    for y in range(H):
        c = 0 if y % 3 != 0 else 1
        for x in range(W):
            d[y * W + x] = c
    # plank gaps
    for y in [4, 9, 14]:
        for x in range(W):
            d[y * W + x] = 3
    return pal, d


def tile_fire():
    # small campfire · warm orange with brighter core
    pal = ['#e88030', '#c85818', '#f8b060', '#4a1808']
    d = blank()
    fill(d, 3)  # dark base (embers)
    # flame core column
    for (x, y) in [(7,4),(8,4),(7,5),(8,5),(6,6),(7,6),(8,6),(9,6),
                    (6,7),(7,7),(8,7),(9,7),(5,8),(6,8),(7,8),(8,8),
                    (9,8),(10,8),(5,9),(6,9),(9,9),(10,9)]:
        set_pixel(d, x, y, 0)
    for (x, y) in [(7,3),(8,3),(7,4),(8,4),(6,5),(9,5),(7,6),(8,6)]:
        set_pixel(d, x, y, 2)
    # base logs
    for (x, y) in [(4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),
                    (5,13),(6,13),(9,13),(10,13)]:
        set_pixel(d, x, y, 1)
    return pal, d


def tile_window():
    # Interior window · light blue with wooden frame
    pal = ['#8ea6b0', '#6c8894', '#a8bec6', '#4a3826']
    d = blank()
    fill(d, 0)
    # Frame border
    for x in range(W):
        set_pixel(d, x, 0, 3)
        set_pixel(d, x, H-1, 3)
    for y in range(H):
        set_pixel(d, 0, y, 3)
        set_pixel(d, W-1, y, 3)
    # Muntin bars (cross)
    for y in range(H):
        set_pixel(d, 7, y, 3)
        set_pixel(d, 8, y, 3)
    for x in range(W):
        set_pixel(d, x, 7, 3)
        set_pixel(d, x, 8, 3)
    # Slight highlight
    for (x, y) in [(3,3),(11,3),(3,11),(11,11)]:
        set_pixel(d, x, y, 2)
    return pal, d


def tile_sign():
    # Wooden sign · yellow-tinted post with plaque
    pal = ['#c8a842', '#8c6a2a', '#e0c060', '#3a2818']
    d = blank()
    fill(d, 0)
    # Plaque body slightly darker at bottom, brighter on top
    for y in range(6):
        for x in range(2, 14):
            d[y * W + x] = 2
    for y in range(6, 10):
        for x in range(2, 14):
            d[y * W + x] = 0
    # Frame
    for x in range(2, 14):
        set_pixel(d, x, 0, 3)
        set_pixel(d, x, 9, 3)
    for y in range(10):
        set_pixel(d, 2, y, 3)
        set_pixel(d, 13, y, 3)
    # Post
    for y in range(10, H):
        set_pixel(d, 7, y, 1)
        set_pixel(d, 8, y, 1)
    return pal, d


def tile_chest():
    # Wooden chest · dark wood with iron bands + lock hint
    pal = ['#3a2818', '#241408', '#5a3e26', '#8a8a94']
    d = blank()
    # Body
    for y in range(3, 14):
        for x in range(1, 15):
            d[y * W + x] = 0
    # Lid line
    for x in range(1, 15):
        d[3 * W + x] = 1
    # Iron bands (top/bottom of body)
    for x in range(1, 15):
        d[4 * W + x] = 3
        d[13 * W + x] = 3
    # Lock plate
    for y in range(6, 10):
        for x in range(7, 10):
            d[y * W + x] = 3
    for (x, y) in [(8, 7)]:
        set_pixel(d, x, y, 1)  # keyhole
    # Wood highlights
    for (x, y) in [(2,5),(12,8),(4,11)]:
        set_pixel(d, x, y, 2)
    return pal, d


def tile_dock_edge():
    # Dock plank overhanging water · top half wood, bottom half water hint
    pal = ['#8c6a3e', '#6a4e2e', '#3a5a68', '#243848']
    d = blank()
    # Top: wood
    for y in range(0, 10):
        for x in range(W):
            d[y * W + x] = 0 if y % 2 == 0 else 1
    # Bottom: water
    for y in range(10, H):
        for x in range(W):
            d[y * W + x] = 2 if y % 2 == 0 else 3
    # Plank edges every 4 rows in top half
    for y in [3, 7]:
        for x in range(W):
            d[y * W + x] = 1
    return pal, d


def tile_seaweed():
    # Underwater seaweed · dark green with slight vertical wave
    pal = ['#1a3a1c', '#0a2010', '#345a2c', '#243848']
    d = blank()
    fill(d, 3)  # water base
    # Fronds — vertical clusters
    for x in [3, 4, 8, 9, 12, 13]:
        for y in range(4, 16):
            if (x + y) % 3 != 0:
                set_pixel(d, x, y, 0)
    # Frond highlights
    for (x, y) in [(3,7),(9,5),(13,9),(4,12),(8,14)]:
        set_pixel(d, x, y, 2)
    # Base shadow
    for x in [3,4,8,9,12,13]:
        set_pixel(d, x, 15, 1)
    return pal, d


def tile_mattress():
    # Bunk mattress · light stripes
    pal = ['#c4a878', '#a88854', '#dcc890', '#6a4e2e']
    d = blank()
    fill(d, 0)
    # Vertical stripes
    for x in range(W):
        for y in range(H):
            if (x // 3) % 2 == 0:
                d[y * W + x] = 0
            else:
                d[y * W + x] = 1
    # Frame edge top+bottom
    for x in range(W):
        set_pixel(d, x, 0, 3)
        set_pixel(d, x, H-1, 3)
    # Highlight along top
    for x in range(2, 14):
        set_pixel(d, x, 1, 2)
    return pal, d


def tile_kitchen_range():
    # Dark cast-iron range · black with occasional red-embers hint
    pal = ['#2a1e18', '#181008', '#3a2a1e', '#a04020']
    d = blank()
    fill(d, 0)
    # Top surface · darker
    for x in range(W):
        for y in range(2):
            d[y * W + x] = 1
    # Burner rings (two)
    for (cx, cy) in [(4, 5), (11, 5)]:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) == 2:
                    set_pixel(d, cx+dx, cy+dy, 2)
    # A tiny ember hint
    dots(d, 3, [(4, 5), (11, 5)])
    # Oven door
    for x in range(2, 14):
        set_pixel(d, x, 12, 2)
        set_pixel(d, x, 13, 1)
    # Handle
    for x in range(6, 10):
        set_pixel(d, x, 11, 2)
    return pal, d


def tile_bulletin_board():
    # Cork board with pinned paper hints
    pal = ['#8c6a3e', '#6a4a2e', '#e4d0a0', '#c84a3a']
    d = blank()
    fill(d, 0)
    # Frame
    for x in range(W):
        set_pixel(d, x, 0, 1)
        set_pixel(d, x, H-1, 1)
    for y in range(H):
        set_pixel(d, 0, y, 1)
        set_pixel(d, W-1, y, 1)
    # Pinned papers
    for (x0, y0, w0, h0) in [(2, 2, 4, 3), (9, 3, 5, 4), (3, 10, 5, 3), (10, 10, 4, 4)]:
        for dy in range(h0):
            for dx in range(w0):
                set_pixel(d, x0 + dx, y0 + dy, 2)
        # Red pin at top-center
        set_pixel(d, x0 + w0 // 2, y0, 3)
    return pal, d


TILES = {
    'grass':           tile_grass,
    'sand':            tile_sand,
    'path':            tile_path,
    'water_deep':      tile_water_deep,
    'water_shallow':   tile_water_shallow,
    'dock':            tile_dock,
    'wood_floor':      tile_wood_floor,
    'rock_wall':       tile_rock_wall,
    'cabin_wall':      tile_cabin_wall,
    'tree_top':        tile_tree_top,
    'brush':           tile_brush,
    'dune_grass':      tile_dune_grass,
    'boulder':         tile_boulder,
    'bunk':            tile_bunk,
    'deck_wood':       tile_deck_wood,
    'fire':            tile_fire,
    'window':          tile_window,
    'sign':            tile_sign,
    'chest':           tile_chest,
    'dock_edge':       tile_dock_edge,
    'seaweed':         tile_seaweed,
    'mattress':        tile_mattress,
    'kitchen_range':   tile_kitchen_range,
    'bulletin_board':  tile_bulletin_board,
}


def emit_all():
    os.makedirs(OUTDIR, exist_ok=True)
    for name, fn in TILES.items():
        pal_hex, data = fn()
        # SlowstockSprite convention: index 0 is transparent.  Our
        # tiles want an opaque base color at index 0.  Prepend a
        # transparent slot at index 0 and shift all indices +1.
        pal_out = [""] + list(pal_hex)
        data_shifted = [c + 1 for c in data]
        obj = {
            "id": name,
            "notes": f"Procgen tile · {name} · generated by procgen_ps_tiles.py.  16x16 palette-indexed.  Regenerate with procgen_ps_tiles.py.",
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
