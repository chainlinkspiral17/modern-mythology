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


def h01(x, y, s=0):
    """Deterministic per-pixel hash in [0,1). Same everywhere, forever."""
    n = (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF) / 65536.0


def mottle(data, choices, seed=0, cell=1):
    """Dense hash mottling: choices is [(color, threshold), ...] checked
    in order against the pixel hash; the last entry should have
    threshold 1.0 (the base tone). cell>1 samples chunkier clumps.
    Dense low-contrast texture hides the tile-repeat far better than
    a flat fill plus a few bright dots (2026-07 graphics pass)."""
    for y in range(H):
        for x in range(W):
            r = h01(x // cell, y // cell, seed)
            for c, th in choices:
                if r < th:
                    data[y * W + x] = c
                    break


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
    # deep forest floor · dense three-tone mottle, blades on top
    pal = ['#3a5c2c', '#4c6e3a', '#26401e', '#5a7c40']
    d = blank()
    mottle(d, [(2, 0.16), (1, 0.40), (0, 1.0)], seed=1)
    # rare brightest blade
    dots(d, 3, [(6,3),(12,11),(2,8)])
    return pal, d


def tile_sand():
    # warm tan · dense grain mottle with pebble specks
    pal = ['#c4a874', '#a88854', '#dcc890', '#8a6a3c']
    d = blank()
    mottle(d, [(1, 0.14), (2, 0.34), (0, 1.0)], seed=2)
    dots(d, 3, [(5,1),(12,6),(8,9),(4,15)])
    return pal, d


def tile_path():
    # packed dirt · dense mottle, worn lighter center line
    pal = ['#8c7a54', '#6a5a3e', '#a8946a', '#4a3e2a']
    d = blank()
    mottle(d, [(1, 0.18), (2, 0.36), (0, 1.0)], seed=3)
    dots(d, 3, [(5,6),(11,2),(3,11),(8,15)])
    return pal, d


def tile_water_deep():
    # dark blue · mottled swell, broken dashed ripples (a straight
    # full-width line repeats hard when tiled; dashes don't)
    pal = ['#243848', '#1a2a38', '#2e4658']
    d = blank()
    mottle(d, [(1, 0.22), (0, 1.0)], seed=4, cell=2)
    for y in [3, 7, 11, 15]:
        for x in range(W):
            if h01(x, y, 44) > 0.35:
                d[((y + (1 if (x // 5) % 2 == 1 else 0)) % H) * W + x] = 2
    return pal, d


def tile_water_shallow():
    # lighter blue-green · you can see the bottom
    pal = ['#4a6a7a', '#3a5a68', '#6a8a98', '#8aa8b4']
    d = blank()
    mottle(d, [(1, 0.20), (0, 1.0)], seed=5, cell=2)
    for y in [2, 6, 10, 14]:
        for x in range(W):
            if h01(x, y, 55) > 0.4:
                d[((y + (1 if (x // 4) % 2 == 1 else 0)) % H) * W + x] = 2
    # sun glints on the bottom
    dots(d, 3, [(3,4),(8,8),(12,3),(6,12),(14,13)])
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
    # grain flecks so the planks don't read as flat stripes
    for y in range(H):
        for x in range(W):
            if h01(x, y, 9) > 0.92 and d[y * W + x] != 3:
                d[y * W + x] = 1 if d[y * W + x] == 0 else 0
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
    for y in range(H):
        for x in range(W):
            if h01(x, y, 10) > 0.93:
                d[y * W + x] = 1
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
    for y in range(H):
        for x in range(W):
            if h01(x, y, 11) > 0.93 and d[y * W + x] != 3:
                d[y * W + x] = 1
    return pal, d


def tile_tree_top():
    # dark forest tree canopy · chunky clump mottle reads as boughs
    pal = ['#1a3a1c', '#0a1e10', '#264a24', '#000000']
    d = blank()
    mottle(d, [(1, 0.30), (2, 0.48), (0, 1.0)], seed=6, cell=2)
    # deepest shadow pockets
    dots(d, 3, [(4,5),(11,9),(7,13)])
    return pal, d


def tile_brush():
    # chest-high salal · dense leaf-clump mottle
    pal = ['#2a4a1e', '#1a3a14', '#4a6c30', '#0a1a08']
    d = blank()
    mottle(d, [(1, 0.24), (2, 0.46), (0, 1.0)], seed=7, cell=2)
    dots(d, 3, [(10,10),(4,5),(13,2)])
    return pal, d


def tile_dune_grass():
    # long dune grass · stroke rows broken per-column so the tiling
    # doesn't read as ruled paper
    pal = ['#a4a878', '#8c9060', '#c0c090', '#6a6e48']
    d = blank()
    mottle(d, [(1, 0.18), (0, 1.0)], seed=8)
    for y in [2, 4, 7, 10, 13]:
        for x in range(W):
            if h01(x, y, 88) > 0.25:
                d[y * W + x] = 1
    for y in [5, 11]:
        for x in range(W):
            if h01(x, y, 89) > 0.45:
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
    for y in range(H):
        for x in range(W):
            if h01(x, y, 12) > 0.93 and d[y * W + x] != 3:
                d[y * W + x] = 2
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


def tile_grass_flower():
    # Grass with a small wildflower at center
    pal, d = tile_grass()
    # Ensure palette has a flower color · add if needed (yellow-white)
    pal = list(pal) + ['#f0e0a0', '#e04868']
    fi = len(pal) - 2  # flower petal color index
    ri = len(pal) - 1  # red center
    # Plant a small flower · petals + center
    for (x, y) in [(7,6),(9,6),(6,7),(10,7),(7,8),(9,8)]:
        set_pixel(d, x, y, fi)
    set_pixel(d, 8, 7, ri)
    return pal, d


def tile_grass_thick():
    # Grass with denser blades
    pal, d = tile_grass()
    for (x, y) in [(3,5),(6,4),(10,6),(4,8),(11,7),(8,9),(2,11),(13,10),(5,13),(10,13),(1,7)]:
        set_pixel(d, x, y, 1)
    for (x, y) in [(5,2),(11,4),(1,9),(14,12)]:
        set_pixel(d, x, y, 3)
    return pal, d


def tile_sand_shell():
    # Sand with a distinct small shell
    pal, d = tile_sand()
    pal = list(pal) + ['#f4e4c0', '#a86840']
    fi = len(pal) - 2
    ri = len(pal) - 1
    # Small fan shell at center
    for (x, y) in [(7,8),(8,8),(9,8),(7,9),(8,9),(9,9),(6,10),(7,10),(8,10),(9,10),(10,10)]:
        set_pixel(d, x, y, fi)
    for (x, y) in [(6,10),(10,10),(8,7)]:
        set_pixel(d, x, y, ri)
    return pal, d


def tile_path_pebble():
    # Path with a visible pebble cluster
    pal, d = tile_path()
    pal = list(pal) + ['#a4a4a4', '#5a5a5a']
    pi = len(pal) - 2
    di = len(pal) - 1
    for (x, y) in [(7,7),(8,7),(9,7),(7,8),(8,8),(9,8)]:
        set_pixel(d, x, y, pi)
    for (x, y) in [(7,8),(9,7)]:
        set_pixel(d, x, y, di)
    return pal, d


def tile_brush_berry():
    # Brush with a red berry cluster
    pal, d = tile_brush()
    pal = list(pal) + ['#c8283a', '#8a1020']
    bi = len(pal) - 2
    di = len(pal) - 1
    for (x, y) in [(7,6),(8,6),(9,6),(7,7),(8,7),(9,7)]:
        set_pixel(d, x, y, bi)
    for (x, y) in [(8,6),(9,7)]:
        set_pixel(d, x, y, di)
    return pal, d


def tile_rock_wall_moss():
    # Rock wall with green moss patches
    pal, d = tile_rock_wall()
    pal = list(pal) + ['#3a6a2a', '#588c40']
    mi = len(pal) - 2
    li = len(pal) - 1
    for (x, y) in [(2,2),(3,2),(2,3),(11,11),(12,11),(11,12),(12,12),(6,14),(7,14)]:
        set_pixel(d, x, y, mi)
    for (x, y) in [(3,2),(12,11),(7,14)]:
        set_pixel(d, x, y, li)
    return pal, d


def tile_tree_short():
    # A smaller tree · Sitka spruce more compact
    pal = ['#1a3a1c', '#0a1e10', '#264a24', '#000000']
    d = blank()
    fill(d, 0)
    # Trunk hint bottom center
    for y in [13, 14, 15]:
        set_pixel(d, 7, y, 3)
        set_pixel(d, 8, y, 3)
    # Small canopy
    for (x, y) in [(6, 8),(7, 8),(8, 8),(9, 8),(5, 9),(10, 9),(6, 9),(7, 9),(8, 9),(9, 9),
                    (5, 10),(10, 10),(6, 10),(7, 10),(8, 10),(9, 10),(6, 11),(9, 11),(7, 11),(8, 11)]:
        set_pixel(d, x, y, 1)
    for (x, y) in [(4, 9),(11, 9),(4, 10),(11, 10),(5, 11),(10, 11)]:
        set_pixel(d, x, y, 2)
    return pal, d


def tile_dune_grass_wind():
    # Dune grass with more diagonal windswept strokes
    pal, d = tile_dune_grass()
    for (x, y) in [(4,3),(5,4),(6,5),(11,6),(12,7),(13,8)]:
        set_pixel(d, x, y, 2)
    return pal, d


def tile_fallen_log():
    # A horizontal fallen spruce log with moss patches on top
    pal = ['#3a2418', '#5a3a20', '#8a5a30', '#2a3a1a', '#4a5a2a', '#1a1208']
    d = blank()
    fill(d, 5)                      # background deep shadow
    for y in range(4, 12):
        for x in range(W):
            set_pixel(d, x, y, 0)
    hbands_indices = [(4, 1), (5, 2), (6, 1), (7, 0), (8, 0), (9, 1), (10, 2), (11, 1)]
    for (y, c) in hbands_indices:
        for x in range(W):
            set_pixel(d, x, y, c)
    # moss patches on top
    for (x, y) in [(2, 3), (3, 3), (7, 3), (8, 3), (9, 3), (13, 3), (14, 3)]:
        set_pixel(d, x, y, 3)
    for (x, y) in [(2, 3), (8, 3), (13, 3)]:
        set_pixel(d, x, y, 4)
    return pal, d


def tile_disturbed_earth():
    # Freshly-turned soil · dark umber with a rectangular outline
    pal = ['#3a2a18', '#5a4028', '#241812', '#8a6848', '#141008']
    d = blank()
    fill(d, 0)
    # Outer rectangle border (freshly-dug edge)
    for x in range(W):
        set_pixel(d, x, 1, 2)
        set_pixel(d, x, 14, 2)
    for y in range(1, 15):
        set_pixel(d, 1, y, 2)
        set_pixel(d, 14, y, 2)
    # Clod texture inside
    for (x, y) in [(3, 4), (5, 5), (8, 3), (10, 6), (12, 4),
                    (4, 8), (7, 9), (11, 8), (9, 11), (5, 12), (10, 12)]:
        set_pixel(d, x, y, 1)
    for (x, y) in [(5, 5), (10, 6), (7, 9), (5, 12)]:
        set_pixel(d, x, y, 3)
    # A few dark divots
    for (x, y) in [(6, 7), (12, 10), (4, 11)]:
        set_pixel(d, x, y, 4)
    return pal, d


def tile_tent_peg():
    # An iron tent peg driven into duff · small vertical spike, ring on top
    pal = ['#2a3a1a', '#5a5040', '#8a7048', '#c8a848', '#1a2210']
    d = blank()
    # duff floor background
    fill(d, 0)
    # scattered darker specks
    for (x, y) in [(2, 3), (5, 8), (11, 5), (13, 13), (3, 14)]:
        set_pixel(d, x, y, 4)
    # peg shaft (vertical) at x=7-8
    for y in range(5, 13):
        set_pixel(d, 7, y, 1)
        set_pixel(d, 8, y, 2)
    # peg head/ring at the top
    for (x, y) in [(6, 4), (7, 4), (8, 4), (9, 4), (6, 3), (9, 3)]:
        set_pixel(d, x, y, 1)
    set_pixel(d, 7, 3, 3)
    set_pixel(d, 8, 3, 3)
    # rust glint
    set_pixel(d, 8, 6, 3)
    return pal, d


def tile_cairn():
    # Small stack of nine dark beach-stones · pyramid shape
    pal = ['#2a3a1a', '#3a3a38', '#5a5a58', '#8a8a88', '#141a10', '#c8c8c6']
    d = blank()
    fill(d, 0)
    # bottom row · 4 stones
    for i in range(4):
        x0 = 2 + i * 3
        for (dx, dy) in [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]:
            set_pixel(d, x0 + dx, 12 + dy, 1)
        set_pixel(d, x0, 12, 4)
        set_pixel(d, x0 + 2, 12, 2)
    # middle row · 3 stones
    for i in range(3):
        x0 = 3 + i * 3
        for (dx, dy) in [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]:
            set_pixel(d, x0 + dx, 9 + dy, 2)
    # top row · 2 stones
    for i in range(2):
        x0 = 5 + i * 3
        for (dx, dy) in [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]:
            set_pixel(d, x0 + dx, 6 + dy, 3)
    # cap stone
    for (dx, dy) in [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]:
        set_pixel(d, 6 + dx, 3 + dy, 5)
    return pal, d


def tile_hollow_log():
    # Fallen log with a black hole visible in the end · a crawl-through
    pal, d = tile_fallen_log()
    # Add a dark ellipse at the center-right suggesting a hollow
    for (x, y) in [(11, 6), (12, 6), (13, 6),
                    (10, 7), (11, 7), (12, 7), (13, 7),
                    (10, 8), (11, 8), (12, 8), (13, 8),
                    (11, 9), (12, 9), (13, 9)]:
        set_pixel(d, x, y, 5)     # deep shadow
    # rim highlight
    for (x, y) in [(10, 6), (13, 6), (10, 9), (13, 9)]:
        set_pixel(d, x, y, 0)
    return pal, d


def tile_hollow_tree():
    # Standing spruce trunk with a small hollow at chest height
    pal = ['#141a10', '#2a1e12', '#4a3418', '#6a4820', '#0a0a08', '#8a6840']
    d = blank()
    # background · forest shadow
    fill(d, 0)
    # trunk
    for x in range(3, 13):
        for y in range(H):
            set_pixel(d, x, y, 1)
    # bark grain (verticals)
    for x in [4, 7, 10]:
        for y in range(H):
            set_pixel(d, x, y, 2)
    # highlight side
    for y in range(H):
        set_pixel(d, 11, y, 3)
    # hollow · black oval at mid-height
    for (x, y) in [(6, 7), (7, 7), (8, 7), (9, 7),
                    (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8),
                    (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
                    (6, 10), (7, 10), (8, 10), (9, 10)]:
        set_pixel(d, x, y, 4)
    # A hint of the ziploc bag inside
    set_pixel(d, 7, 9, 5)
    set_pixel(d, 8, 9, 5)
    return pal, d


# ── Cabin dressing (production pass 2 · 2026-08-04) ──────────────
# The four cabins were 18x10 rooms with four props in them. These
# are the tiles that make an interior read as lived in: a footlocker
# at the end of a bunk, a shelf with somebody's things on it, wet
# swimsuits on a line, the cabin's one oil lamp, a screen door.


def tile_footlocker():
    # camp trunk at the foot of a bunk · canvas over wood, brass corners
    pal = ['#6a4e30', '#4a3420', '#2a1c10', '#8a7a52', '#9a8a62']
    d = blank()
    fill(d, 0)
    # floorboard hint above and below
    for x in range(W):
        d[0 * W + x] = 1
        d[15 * W + x] = 1
    # the trunk body
    for y in range(3, 13):
        for x in range(1, 15):
            d[y * W + x] = 1
    # lid line
    for x in range(1, 15):
        d[6 * W + x] = 2
        d[3 * W + x] = 2
        d[12 * W + x] = 2
    # brass corners + latch
    for (cx, cy) in ((1, 3), (14, 3), (1, 12), (14, 12)):
        set_pixel(d, cx, cy, 3)
        set_pixel(d, cx, cy + 1 if cy < 8 else cy - 1, 3)
    for y in range(6, 9):
        set_pixel(d, 7, y, 4)
        set_pixel(d, 8, y, 4)
    return pal, d


def tile_cubby():
    # open shelf unit · three bays, somebody's folded things
    pal = ['#5a4028', '#3a2818', '#241408', '#7a6a4a', '#8a6a58']
    d = blank()
    fill(d, 1)
    # carcass
    for x in range(W):
        for y in (0, 5, 10, 15):
            d[y * W + x] = 2
    for y in range(H):
        d[y * W + 0] = 2
        d[y * W + 15] = 2
    # bay interiors
    for band, col in ((1, 0), (6, 0), (11, 0)):
        for y in range(band, band + 4):
            for x in range(1, 15):
                d[y * W + x] = col
    # folded clothes / a rolled towel per bay
    for (by, c) in ((3, 3), (8, 4), (13, 3)):
        for x in range(2, 8):
            set_pixel(d, x, by, c)
            set_pixel(d, x, by + 1, c)
    for x in range(9, 14):
        set_pixel(d, x, 8, 3)
    return pal, d


def tile_clothesline():
    # wet swimsuits + a towel on a line strung across the cabin
    pal = ['#6a5a3e', '#3a3428', '#c05a5a', '#4a7ab0', '#d8c890']
    d = blank()
    fill(d, 0)
    # the line
    for x in range(W):
        d[3 * W + x] = 1
    # a red suit
    for y in range(4, 11):
        for x in range(2, 6):
            d[y * W + x] = 2
    d[10 * W + 3] = 0
    # a blue one
    for y in range(4, 9):
        for x in range(7, 10):
            d[y * W + x] = 3
    # a towel, hung long
    for y in range(4, 13):
        for x in range(11, 15):
            d[y * W + x] = 4
    return pal, d


def tile_oil_lamp():
    # the cabin's one lamp on a nail · warm, small, off by day
    pal = ['#4a3826', '#2a1c10', '#8a8a94', '#e8c060', '#f8e8a8']
    d = blank()
    fill(d, 0)
    # nail + bracket
    set_pixel(d, 8, 1, 1)
    for x in range(6, 11):
        d[2 * W + x] = 1
    # glass chimney
    for y in range(3, 9):
        for x in range(6, 11):
            d[y * W + x] = 2
    # flame
    for y in range(5, 8):
        for x in range(7, 10):
            d[y * W + x] = 3
    set_pixel(d, 8, 6, 4)
    # brass base
    for x in range(5, 12):
        d[9 * W + x] = 1
        d[10 * W + x] = 1
    return pal, d


def tile_screen_door():
    # the cabin's screen door · mesh, spring, the light behind it
    pal = ['#4a3620', '#2a1c10', '#6a6a5a', '#8a8a72', '#c8b888']
    d = blank()
    fill(d, 0)
    # frame
    for x in range(W):
        d[0 * W + x] = 1
        d[15 * W + x] = 1
    for y in range(H):
        d[y * W + 0] = 1
        d[y * W + 15] = 1
    # the mesh · daylight through it
    for y in range(2, 14):
        for x in range(2, 14):
            d[y * W + x] = 3 if (x + y) % 2 == 0 else 2
    # rail across the middle
    for x in range(1, 15):
        d[7 * W + x] = 1
        d[8 * W + x] = 1
    # the spring, and the handle
    for y in range(2, 6):
        set_pixel(d, 13, y, 4)
    set_pixel(d, 12, 9, 4)
    set_pixel(d, 12, 10, 4)
    return pal, d


# ── Unmapped-kind sweep (production pass 2 · 2026-08-04) ─────────
# An audit found 58 tile kinds in use with no sprite — they rendered
# as flat color rects. Eight of them were EXITS. These cover the
# high-count props and every remaining affordance.


def tile_fence():
    # split-rail fence · the archery range's boundary
    pal = ['#6a7a4a', '#7a6a48', '#5a4a30', '#3a3020']
    d = blank()
    mottle(d, [(0, 0.55), (0, 1.0)], 3)
    # two rails
    for y in (5, 6, 10, 11):
        for x in range(W):
            d[y * W + x] = 1 if y in (5, 10) else 2
    # posts
    for px in (3, 12):
        for y in range(3, 15):
            d[y * W + px] = 2
            d[y * W + px + 1] = 3
    return pal, d


def tile_log_bench():
    # a split log on two rounds · the campfire ring's seating
    pal = ['#5a5038', '#7a6244', '#8a7250', '#3a2e1c', '#4a3c26']
    d = blank()
    fill(d, 0)
    # the log body
    for y in range(4, 11):
        for x in range(W):
            d[y * W + x] = 1
    # flat cut top
    for x in range(W):
        d[4 * W + x] = 2
        d[5 * W + x] = 2
    # bark shadow underside
    for x in range(W):
        d[10 * W + x] = 3
    # grain
    for x in range(0, W, 3):
        d[7 * W + x] = 4
        d[8 * W + ((x + 1) % W)] = 4
    # legs
    for lx in (2, 12):
        for y in range(11, 15):
            d[y * W + lx] = 3
            d[y * W + lx + 1] = 4
    return pal, d


def tile_hay_bale():
    # straw bale backstop
    pal = ['#b09a52', '#c8b268', '#8a7638', '#6a5a28']
    d = blank()
    fill(d, 0)
    for y in range(H):
        for x in range(W):
            if h01(x, y, 4) > 0.72:
                d[y * W + x] = 1
            elif h01(x, y, 9) > 0.86:
                d[y * W + x] = 2
    # binding twine
    for x in range(W):
        d[4 * W + x] = 3
        d[11 * W + x] = 3
    # edges
    for y in range(H):
        d[y * W + 0] = 2
        d[y * W + 15] = 2
    return pal, d


def tile_archery_target():
    # the classic boss · concentric rings on a stand
    pal = ['#d8d0c0', '#c04040', '#4a6ab0', '#e8d060', '#3a3028']
    d = blank()
    fill(d, 4)
    cx, cy = 7.5, 6.5
    for y in range(H):
        for x in range(W):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= 1.6:
                d[y * W + x] = 3
            elif dist <= 3.0:
                d[y * W + x] = 1
            elif dist <= 4.4:
                d[y * W + x] = 0
            elif dist <= 5.6:
                d[y * W + x] = 2
    # legs
    for y in range(12, 16):
        d[y * W + 5] = 4
        d[y * W + 10] = 4
    return pal, d


def tile_canoe():
    # an aluminum canoe upside down on the rack
    pal = ['#7a8a94', '#9aaab4', '#5a6a74', '#3a4a52']
    d = blank()
    fill(d, 3)
    # hull · a long lens shape
    for y in range(5, 11):
        span = 7 - abs(y - 7)
        for x in range(8 - span, 8 + span):
            d[y * W + x] = 0
    # highlight along the keel
    for x in range(3, 13):
        d[6 * W + x] = 1
    # shadowed gunwale
    for x in range(2, 14):
        d[10 * W + x] = 2
    return pal, d


def tile_barrel():
    # a staved barrel, head-on
    pal = ['#6a4a2a', '#8a6238', '#4a3018', '#8a8a94']
    d = blank()
    fill(d, 2)
    for y in range(2, 14):
        for x in range(3, 13):
            d[y * W + x] = 0
    # staves
    for x in range(4, 13, 3):
        for y in range(2, 14):
            d[y * W + x] = 1
    # hoops
    for y in (4, 11):
        for x in range(2, 14):
            d[y * W + x] = 3
    return pal, d


def tile_wall_paper():
    # anything pinned to a wall · map, poster, postcard, note, chart
    pal = ['#3a2e1e', '#d8cfae', '#b0a582', '#8a7a58', '#c04040']
    d = blank()
    fill(d, 0)
    for y in range(2, 14):
        for x in range(2, 14):
            d[y * W + x] = 1
    # a curl of shadow on two edges
    for y in range(2, 14):
        d[y * W + 13] = 2
    for x in range(2, 14):
        d[13 * W + x] = 2
    # writing / ink marks
    for y in (5, 7, 9, 11):
        for x in range(4, 12):
            if (x + y) % 3 != 0:
                d[y * W + x] = 3
    # one red pin
    set_pixel(d, 8, 3, 4)
    return pal, d


def tile_carved_mark():
    # scratched into rock or wood · graffiti, tally, initials
    pal = ['#4a4238', '#5a5248', '#302a22', '#7a7264']
    d = blank()
    mottle(d, [(1, 0.35), (0, 1.0)], 6)
    # tally scratches
    for i, x in enumerate((3, 6, 9)):
        for y in range(4, 12):
            d[y * W + x] = 2
            d[y * W + x + 1] = 3
    # the crossing stroke
    for i in range(9):
        set_pixel(d, 2 + i, 11 - i, 2)
    return pal, d


def tile_console_tv():
    # the slowstick console / the shortwave set · a screen with a glow
    pal = ['#2a2a30', '#4a4a52', '#1a2a24', '#5ac088', '#8a8a94']
    d = blank()
    fill(d, 0)
    # case
    for y in range(2, 13):
        for x in range(1, 15):
            d[y * W + x] = 1
    # screen
    for y in range(4, 10):
        for x in range(3, 11):
            d[y * W + x] = 2
    # a scanline of phosphor
    for x in range(4, 10):
        d[6 * W + x] = 3
        d[7 * W + ((x + 2) % 10 + 3)] = 3
    # knobs
    for y in (5, 8):
        set_pixel(d, 12, y, 4)
        set_pixel(d, 13, y, 4)
    # feet
    for x in (2, 13):
        d[13 * W + x] = 4
    return pal, d


def tile_sail_canvas():
    # ghost-ship sail · rotted canvas, wind-lifted
    pal = ['#2a2a2e', '#9a9280', '#7a7264', '#c8c0aa']
    d = blank()
    fill(d, 0)
    for y in range(H):
        span = min(15, 2 + y)
        for x in range(0, span):
            d[y * W + x] = 1
    # weave shading
    for y in range(H):
        for x in range(W):
            if d[y * W + x] == 1 and (x + y) % 4 == 0:
                d[y * W + x] = 2
    # a lit edge
    for y in range(H):
        span = min(15, 2 + y)
        if span > 0:
            d[y * W + span - 1] = 3
    # tears
    for (tx, ty) in ((4, 9), (5, 10), (6, 11), (9, 3)):
        set_pixel(d, tx, ty, 0)
    return pal, d


def tile_rope_coil():
    # a coil of old rope on the ground
    pal = ['#4a4438', '#a08a58', '#7a6840', '#5a4c30']
    d = blank()
    fill(d, 0)
    cx, cy = 7.5, 8.0
    for y in range(H):
        for x in range(W):
            dist = ((x - cx) ** 2 + ((y - cy) * 1.35) ** 2) ** 0.5
            if 2.0 < dist <= 3.2:
                d[y * W + x] = 1
            elif 4.0 < dist <= 5.2:
                d[y * W + x] = 2
    # frayed tail
    for i in range(5):
        set_pixel(d, 12 + i % 3, 12 + i // 3, 3)
    return pal, d


def tile_item_glint():
    # a small object worth picking up · reads as "something is here"
    pal = ['#5c4432', '#c8b070', '#8a7040', '#f0e0a8']
    d = blank()
    mottle(d, [(0, 1.0)], 5)
    # the object
    for y in range(7, 11):
        for x in range(5, 11):
            d[y * W + x] = 1
    for x in range(5, 11):
        d[10 * W + x] = 2
    # glint
    set_pixel(d, 6, 6, 3)
    set_pixel(d, 7, 5, 3)
    set_pixel(d, 5, 5, 3)
    return pal, d


def tile_cave_mouth():
    # the opening in the rock · dark, and clearly an opening
    pal = ['#4a4438', '#3a352c', '#141210', '#5a5248']
    d = blank()
    mottle(d, [(1, 0.40), (0, 1.0)], 8)
    cx = 7.5
    for y in range(H):
        # arch: widest at the bottom
        half = 2.0 + (y / 15.0) * 5.0
        for x in range(W):
            if abs(x - cx) < half and y >= 2:
                d[y * W + x] = 2
    # lit lip of the arch
    for y in range(2, H):
        half = 2.0 + (y / 15.0) * 5.0
        lx = int(cx - half)
        rx = int(cx + half)
        set_pixel(d, lx, y, 3)
        set_pixel(d, rx, y, 3)
    return pal, d


# ── Zone dressing wave 2 (production pass 3 · 2026-08-04) ────────
# The mess hall's tables AND benches both mapped to wood_floor, so
# the room the player eats in three times a day rendered as an empty
# box. The camp path's four cabins were four identical flat walls.
# These are the pieces that make furniture furniture and a building
# a building.


def tile_table_long():
    # mess-hall table top · seen from above, planked, worn light
    pal = ['#7a5a34', '#8c6a40', '#5a3e22', '#a08050', '#4a3018']
    d = blank()
    fill(d, 0)
    # plank seams down the length
    for y in range(H):
        for x in range(W):
            if (y % 5) == 0:
                d[y * W + x] = 2
            elif (x + y * 3) % 11 == 0:
                d[y * W + x] = 1
    # the worn stripe down the middle where forearms go
    for x in range(W):
        d[7 * W + x] = 3
        d[8 * W + x] = 3
    # edge shadow so it sits above the floor
    for x in range(W):
        d[15 * W + x] = 4
    for y in range(H):
        d[y * W + 15] = 4
    return pal, d


def tile_bench_wood():
    # bench · a narrower plank with legs, floor visible above/below
    pal = ['#5c4432', '#8a6a44', '#6a4e30', '#3a2a18']
    d = blank()
    fill(d, 0)          # floor showing through
    for y in range(4, 12):
        for x in range(W):
            d[y * W + x] = 1
    # plank seam
    for x in range(W):
        d[7 * W + x] = 2
    # front edge shadow
    for x in range(W):
        d[11 * W + x] = 3
    # legs
    for lx in (2, 13):
        for y in range(12, 15):
            d[y * W + lx] = 3
            d[y * W + lx + 1] = 2
    return pal, d


def tile_serving_counter():
    # the mess line · stainless top, a rail, steam
    pal = ['#6a5a4a', '#9aa2a6', '#c0c8cc', '#4a4038', '#7a8a90']
    d = blank()
    fill(d, 0)
    # counter body
    for y in range(5, 15):
        for x in range(W):
            d[y * W + x] = 3
    # the steel top
    for y in range(3, 6):
        for x in range(W):
            d[y * W + x] = 1
    for x in range(W):
        d[3 * W + x] = 2
    # tray rail
    for x in range(W):
        d[9 * W + x] = 4
    # a well of something hot
    for y in range(6, 9):
        for x in range(4, 12):
            d[y * W + x] = 0
    return pal, d


def tile_cabin_roof():
    # shingled roof · the building's mass, read from above
    pal = ['#4a3a2c', '#3a2c20', '#5a4836', '#241a12']
    d = blank()
    fill(d, 0)
    # shingle courses, offset row to row
    for row in range(0, H, 4):
        for x in range(W):
            d[row * W + x] = 3
        off = 0 if (row // 4) % 2 == 0 else 3
        for x in range(off, W, 6):
            for y in range(row, min(row + 4, H)):
                d[y * W + x] = 1
    # sun on the upper courses
    for x in range(W):
        d[1 * W + x] = 2
    return pal, d


def tile_cabin_face():
    # cabin front · planks with a lit window, so a wall reads as a
    # place somebody is
    pal = ['#4a3826', '#3a2a1c', '#5c4a34', '#241814', '#c8a85a', '#8a7a4a']
    d = blank()
    for y in range(H):
        band = (y // 4) % 3
        c = [0, 2, 1][band]
        for x in range(W):
            d[y * W + x] = c
    for y in (3, 7, 11, 15):
        for x in range(W):
            d[y * W + x] = 3
    # the window · frame, glass, muntins
    for y in range(4, 12):
        for x in range(4, 12):
            d[y * W + x] = 3
    for y in range(5, 11):
        for x in range(5, 11):
            d[y * W + x] = 4
    for y in range(5, 11):
        d[y * W + 7] = 5
        d[y * W + 8] = 5
    for x in range(5, 11):
        d[7 * W + x] = 5
    return pal, d


def tile_cabin_sign():
    # the cabin's name board on a post beside the door
    pal = ['#4a3826', '#8a7048', '#d8cfae', '#2a1e14', '#6a5436']
    d = blank()
    fill(d, 0)
    # post
    for y in range(9, 16):
        d[y * W + 7] = 4
        d[y * W + 8] = 4
    # the board
    for y in range(3, 10):
        for x in range(1, 15):
            d[y * W + x] = 1
    for x in range(1, 15):
        d[3 * W + x] = 3
        d[9 * W + x] = 3
    # lettering · unreadable at this size, which is right
    for x in range(3, 13, 2):
        d[5 * W + x] = 2
        d[6 * W + x] = 2
    return pal, d


def tile_woodpile():
    # split rounds stacked against a tree · the fire's supply
    pal = ['#5a4632', '#7a6244', '#3a2c1e', '#c8b58a', '#8a7050']
    d = blank()
    fill(d, 2)
    # log ends, three courses
    for row, ys in enumerate((2, 7, 12)):
        for col in range(4):
            cx = 2 + col * 4 + (2 if row % 2 else 0)
            for y in range(ys, min(ys + 4, H)):
                for x in range(cx - 1, cx + 2):
                    if 0 <= x < W:
                        d[y * W + x] = 0
            # the pale split face
            if 0 <= cx < W and ys + 1 < H:
                d[(ys + 1) * W + cx] = 3
                d[(ys + 2) * W + cx] = 4
    return pal, d


def tile_stump():
    # a cut stump · someone always sits here
    pal = ['#4a5a38', '#6a5236', '#8a7050', '#c0a878', '#3a2c1e']
    d = blank()
    mottle(d, [(0, 1.0)], 3)
    cx, cy = 7.5, 8.0
    for y in range(H):
        for x in range(W):
            dist = ((x - cx) ** 2 + ((y - cy) * 1.15) ** 2) ** 0.5
            if dist <= 6.0:
                d[y * W + x] = 1
            if dist <= 4.6:
                d[y * W + x] = 2
    # rings
    for r in (1.6, 3.0):
        for y in range(H):
            for x in range(W):
                dist = ((x - cx) ** 2 + ((y - cy) * 1.15) ** 2) ** 0.5
                if abs(dist - r) < 0.6:
                    d[y * W + x] = 3
    # bark shadow at the base
    for x in range(3, 13):
        d[14 * W + x] = 4
    return pal, d


TILES = {
    'table_long':       tile_table_long,
    'bench_wood':       tile_bench_wood,
    'serving_counter':  tile_serving_counter,
    'cabin_roof':       tile_cabin_roof,
    'cabin_face':       tile_cabin_face,
    'cabin_sign':       tile_cabin_sign,
    'woodpile':         tile_woodpile,
    'stump':            tile_stump,
    'fence':            tile_fence,
    'log_bench':        tile_log_bench,
    'hay_bale':         tile_hay_bale,
    'archery_target':   tile_archery_target,
    'canoe':            tile_canoe,
    'barrel':           tile_barrel,
    'wall_paper':       tile_wall_paper,
    'carved_mark':      tile_carved_mark,
    'console_tv':       tile_console_tv,
    'sail_canvas':      tile_sail_canvas,
    'rope_coil':        tile_rope_coil,
    'item_glint':       tile_item_glint,
    'cave_mouth':       tile_cave_mouth,
    'footlocker':       tile_footlocker,
    'cubby':            tile_cubby,
    'clothesline':      tile_clothesline,
    'oil_lamp':         tile_oil_lamp,
    'screen_door':      tile_screen_door,
    'grass':            tile_grass,
    'sand':             tile_sand,
    'path':             tile_path,
    'water_deep':       tile_water_deep,
    'water_shallow':    tile_water_shallow,
    'dock':             tile_dock,
    'wood_floor':       tile_wood_floor,
    'rock_wall':        tile_rock_wall,
    'cabin_wall':       tile_cabin_wall,
    'tree_top':         tile_tree_top,
    'brush':            tile_brush,
    'dune_grass':       tile_dune_grass,
    'boulder':          tile_boulder,
    'bunk':             tile_bunk,
    'deck_wood':        tile_deck_wood,
    'fire':             tile_fire,
    'window':           tile_window,
    'sign':             tile_sign,
    'chest':            tile_chest,
    'dock_edge':        tile_dock_edge,
    'seaweed':          tile_seaweed,
    'mattress':         tile_mattress,
    'kitchen_range':    tile_kitchen_range,
    'bulletin_board':   tile_bulletin_board,
    'grass_flower':     tile_grass_flower,
    'grass_thick':      tile_grass_thick,
    'sand_shell':       tile_sand_shell,
    'path_pebble':      tile_path_pebble,
    'brush_berry':      tile_brush_berry,
    'rock_wall_moss':   tile_rock_wall_moss,
    'tree_short':       tile_tree_short,
    'dune_grass_wind':  tile_dune_grass_wind,
    'fallen_log':       tile_fallen_log,
    'disturbed_earth':  tile_disturbed_earth,
    'tent_peg':         tile_tent_peg,
    'cairn':            tile_cairn,
    'hollow_log':       tile_hollow_log,
    'hollow_tree':      tile_hollow_tree,
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
