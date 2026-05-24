#!/usr/bin/env python3
"""
Build ASCII substrate JSON grids for the Modern Mythology engine.

Each substrate composes a sparse, atmospheric grid that sits at the
bottom of GameEngine's layer stack — the "machine substrate" beneath
later mediums. Output schema matches tools/img2ascii.py:

  { width, height, charset, color, cells: [[{c, fg, bg}, ...], ...] }

Add a new substrate by writing a `compose_<name>()` function and
registering it in SUBSTRATES at the bottom.
"""
import json, math, os, random, sys
from pathlib import Path

OUT_ROOT = Path(__file__).resolve().parent.parent / "resources" / "substrates"


# ── Grid helpers ─────────────────────────────────────────────────────────────

class Grid:
    def __init__(self, w: int, h: int, fill: str = " ",
                 fg: str = "#1a1a26", bg: str | None = None):
        self.w = w
        self.h = h
        self.cells = [
            [{"c": fill, "fg": fg, "bg": bg} for _ in range(w)]
            for _ in range(h)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def set(self, x: int, y: int, c: str, fg: str | None = None, bg: str | None = "_keep"):
        if not self.in_bounds(x, y):
            return
        cell = self.cells[y][x]
        cell["c"] = c
        if fg is not None:
            cell["fg"] = fg
        if bg != "_keep":
            cell["bg"] = bg

    def get_bg(self, x: int, y: int) -> str | None:
        return self.cells[y][x]["bg"] if self.in_bounds(x, y) else None

    def stamp(self, x: int, y: int, text: str, fg: str | None = None, bg: str | None = "_keep"):
        """Multi-line stamp; spaces are skipped when bg is preserved."""
        for dy, line in enumerate(text.split("\n")):
            for dx, ch in enumerate(line):
                if ch == " " and bg == "_keep":
                    continue
                self.set(x + dx, y + dy, ch, fg, bg)

    def stamp_replace(self, x: int, y: int, text: str, fg: str | None = None, bg: str | None = "_keep"):
        for dy, line in enumerate(text.split("\n")):
            for dx, ch in enumerate(line):
                self.set(x + dx, y + dy, ch, fg, bg)

    def fill_rect(self, x: int, y: int, w: int, h: int, c: str = " ",
                  fg: str | None = None, bg: str | None = "_keep"):
        for dy in range(h):
            for dx in range(w):
                self.set(x + dx, y + dy, c, fg, bg)

    def box(self, x: int, y: int, w: int, h: int, fg: str | None = None,
            chars: str = "+-+|+-+|"):
        tl, top, tr, right, br, bottom, bl, left = chars
        self.set(x,           y,           tl, fg)
        self.set(x + w - 1,   y,           tr, fg)
        self.set(x,           y + h - 1,   bl, fg)
        self.set(x + w - 1,   y + h - 1,   br, fg)
        for dx in range(1, w - 1):
            self.set(x + dx, y,           top,    fg)
            self.set(x + dx, y + h - 1,   bottom, fg)
        for dy in range(1, h - 1):
            self.set(x,         y + dy, left,  fg)
            self.set(x + w - 1, y + dy, right, fg)

    def halo(self, x: int, y: int, w: int, h: int, color: str, radius: int = 1):
        """Set background of empty cells in a radius around a rect."""
        for dy in range(-radius, h + radius):
            for dx in range(-radius, w + radius):
                tx, ty = x + dx, y + dy
                if not self.in_bounds(tx, ty):
                    continue
                if 0 <= dx < w and 0 <= dy < h:
                    continue
                if self.cells[ty][tx]["c"] == " ":
                    self.cells[ty][tx]["bg"] = color

    def to_dict(self, source_name: str = "composed") -> dict:
        return {
            "width": self.w,
            "height": self.h,
            "charset": "ascii",
            "color": "fgbg",
            "source": source_name,
            "cells": self.cells,
        }

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(path.stem)))


# ── Style constants shared across substrates ────────────────────────────────

class Palette:
    """Vol 5 (arcana) palette. Other volumes will extend or override."""
    SKY_BG       = "#070912"
    SKY_FG       = "#222438"
    DAWN_BG      = "#1a131a"
    DAWN_BG_HOT  = "#251a26"
    STAR_BRIGHT  = "#cdd2e6"
    STAR_DIM     = "#5e6378"

    NEON_RED     = "#ff5544"
    NEON_DIM     = "#aa3826"
    NEON_HALO    = "#2a0c06"
    NEON_GHOST   = "#1a0904"

    PILOT_FG     = "#5a4632"
    PILOT_BG     = "#1a1610"
    DECK_FG      = "#3a3024"
    DECK_BG      = "#1f1a14"
    TRIM         = "#7a5a32"

    HULL_LO      = "#0e0a06"
    HULL         = "#1b1610"
    HULL_HI      = "#3a2e22"

    WINDOW_BRIGHT = "#fff2c8"
    WINDOW_WARM   = "#ffbb55"
    WINDOW_FRAME  = "#3a2a18"
    WINDOW_DARK   = "#0c0805"
    WINDOW_DIM    = "#6b5f3a"
    KITCHEN_BG    = "#5a3a18"

    SMOKE        = "#3a3838"
    PADDLE       = "#26201a"
    PADDLE_HI    = "#7a6244"
    PADDLE_HUB   = "#b39060"

    WATER_BG     = "#0a1220"
    WATER_FG     = "#1c2a45"
    WATER_DEEP   = "#060c18"
    WATER_RIPPLE = "#2a3a55"

    REFLECT_BG   = "#1a0a04"
    REFLECT_FG   = "#a04018"
    REFLECT_DIM  = "#5a2410"
    REFLECT_HOT  = "#ff6020"

    ROAD_FG      = "#3a342e"
    ROAD_BG      = "#100c08"
    LAND_FG      = "#2a2520"
    LAND_BG      = "#0e0a06"
    DOCK_FG      = "#5a4422"
    DOCK_BG      = "#1c1408"
    DOCK_PILE    = "#2a1c0c"

    CAPTION      = "#4a4e60"


def _stamp_subgrid(g: 'Grid', x: int, y: int, sub_path: Path,
                   fg_override: str | None = None, skip_blank: bool = True):
    """Load another grid JSON and stamp its cells into g at (x, y).
    Useful for compositing pre-converted img2ascii outputs into hand-authored
    substrates. fg_override re-colors every non-blank cell."""
    d = json.loads(sub_path.read_text())
    for dy, row in enumerate(d.get("cells", [])):
        for dx, cell in enumerate(row):
            ch = cell.get("c", " ")
            if skip_blank and ch == " " and cell.get("bg") is None:
                continue
            fg = fg_override if fg_override is not None else cell.get("fg")
            bg = cell.get("bg")
            g.set(x + dx, y + dy, ch, fg, bg if bg is not None else "_keep")


# ── Substrates ───────────────────────────────────────────────────────────────

def _glitch_chars():
    """Vocabulary used for the evolving glitch effect."""
    return list("░▒▓█▀▄│┤┴┬├┼━┃┏┓┗┛◇◆◊∙·∘○●⊙⊕⊗⊘∆∇αβγδ∂∫√∞±≠≈⌐¬┐┘└┌")

def _glitch_band(g: 'Grid', x0: int, y0: int, w: int, h: int,
                 severity: float = 0.35, fg: str = "#7a8198", seed: int = 7):
    """Substitute a random subset of cells in a region with glitch chars."""
    r = random.Random(seed)
    vocab = _glitch_chars()
    for dy in range(h):
        for dx in range(w):
            if r.random() < severity:
                x, y = x0 + dx, y0 + dy
                if g.in_bounds(x, y):
                    g.set(x, y, r.choice(vocab), fg, g.get_bg(x, y))

def compose_diner_predawn() -> Grid:
    """D'Ambrosio's — riverboat-diner, docked at the riverbank. Pre-dawn
    Graustark gloom. A wooden ramp descends from the road on land (upper
    left) down to the dock, where the boat is tied with mooring lines.
    The river slides past, indifferent. The kitchen window glows.

    Opening substrate for vol5_ch0_booth6 (A Fool Between Acts)."""
    p = Palette
    W, H = 120, 36
    g = Grid(W, H, fill=" ", fg=p.SKY_FG, bg=p.SKY_BG)

    # ── Sky: stars (denser left), dawn warmth upper-right
    random.seed(11)
    for _ in range(80):
        x = random.randint(0, W - 1)
        y = random.randint(0, 8)
        if x > W * 0.6 and random.random() < 0.6:
            continue
        ch = random.choice([".", ".", ".", "'", "`"])
        col = random.choice([p.STAR_BRIGHT, p.STAR_DIM, p.STAR_DIM, "#7a8198"])
        g.set(x, y, ch, col)
    for x, y in [(33, 2), (76, 4), (12, 5), (95, 3)]:
        g.set(x, y, "*", p.STAR_BRIGHT)

    # Dawn glow on right side: warmer cell backgrounds in a triangle
    for y in range(0, 12):
        for x in range(int(W * 0.55), W):
            t = ((x - W * 0.55) / (W - W * 0.55)) * ((12 - y) / 12.0)
            if t > 0.55:
                g.cells[y][x]["bg"] = p.DAWN_BG_HOT
            elif t > 0.30:
                g.cells[y][x]["bg"] = p.DAWN_BG
            elif t > 0.12:
                g.cells[y][x]["bg"] = "#0e0c14"

    # Far bank silhouette (Louisiana side) — a low dim line just above the
    # horizon, only in the right portion of the frame where no boat sits.
    for x in range(int(W * 0.05), W):
        if x % 2 == 0:
            g.set(x, 13, ".", "#1a1820", g.get_bg(x, 13))

    # Horizon line (sky meets distant water)
    for x in range(W):
        g.set(x, 14, "_", "#2c2440", g.get_bg(x, 14))

    # ── LAND (left): road shoulder and approach
    # Upper-left wedge of land; road runs along its top edge.
    LAND_TOP = 12   # land starts being visible
    LAND_BASE = 24  # land base near the dock
    land_edge_x = [
        # (y, x_right_edge_of_land)
        (12, 4), (13, 6), (14, 9), (15, 12), (16, 15),
        (17, 18), (18, 20), (19, 22), (20, 24), (21, 26),
        (22, 28),
    ]
    # Fill land
    for y, xr in land_edge_x:
        for x in range(0, xr):
            g.set(x, y, " ", p.LAND_FG, p.LAND_BG)
    # Land base extends down to bottom of the dock area
    for y in range(22, 25):
        for x in range(0, 32 - (y - 22)):
            g.set(x, y, " ", p.LAND_FG, p.LAND_BG)
    # Land surface texture
    for y, xr in land_edge_x:
        if y % 2 == 0:
            for x in range(0, xr, 4):
                g.set(x, y, ".", "#3a342a", p.LAND_BG)

    # Road on top of the land (a flat strip near the top of the wedge)
    for x in range(0, 16):
        g.set(x, 11, "=", p.ROAD_FG, p.ROAD_BG)
        g.set(x, 12, " ", p.ROAD_FG, p.ROAD_BG)
    # Dashed center line on the road
    for x in range(1, 16, 3):
        g.set(x, 11, "-", "#6a5a32", p.ROAD_BG)

    # ── RAMP: wooden plank ramp descending from road (~col 15, row 12)
    # down to dock surface (~col 30, row 22). Diagonal of slope ~0.7.
    ramp_points = []
    for step in range(16):
        x = 15 + step
        y = 12 + int(round(step * 0.65))
        ramp_points.append((x, y))
    # Underside / shadow under ramp
    for (x, y) in ramp_points:
        for fy in range(y + 1, 24):
            if g.in_bounds(x, fy) and x > 12:
                g.set(x, fy, " ", "#1c1612", "#080604")
    # Ramp surface (top edge)
    for (x, y) in ramp_points:
        g.set(x, y, "/", p.DOCK_FG, g.get_bg(x, y))
        g.set(x, y - 1, "·", "#5a4632", g.get_bg(x, y - 1))

    # ── DOCK: horizontal wooden platform at the bottom of the ramp
    DOCK_Y = 22
    DOCK_X1, DOCK_X2 = 30, 40
    for x in range(DOCK_X1, DOCK_X2):
        g.set(x, DOCK_Y,     "=", p.DOCK_FG, p.DOCK_BG)
        g.set(x, DOCK_Y + 1, "=", "#3a2c14", p.DOCK_BG)
    # Plank seams
    for x in range(DOCK_X1, DOCK_X2, 2):
        g.set(x, DOCK_Y, "|", p.DOCK_PILE, p.DOCK_BG)
    # Dock pilings sticking down into water
    for px_ in (DOCK_X1 + 1, DOCK_X1 + 5, DOCK_X2 - 2):
        for y in range(DOCK_Y + 2, 26):
            g.set(px_, y, "|", p.DOCK_PILE, g.get_bg(px_, y))

    # ── BOAT: docked riverboat-diner, rows ~10–22, cols ~40–103
    deck_left, deck_right = 40, 103
    deck_top, deck_bottom = 14, 22
    # Hull interior
    for y in range(deck_top, deck_bottom):
        for x in range(deck_left, deck_right):
            g.set(x, y, " ", p.DECK_FG, p.DECK_BG)
    # Top trim (deck rail)
    for x in range(deck_left + 1, deck_right - 1):
        g.set(x, deck_top, "=", p.TRIM, p.HULL)
    g.set(deck_left,      deck_top, "/", p.TRIM, p.HULL)
    g.set(deck_right - 1, deck_top, "\\", p.TRIM, p.HULL)

    # OPEN 24 HRS sub-sign — small, under the main sign on the pilothouse face
    # (drawn later, inside the pilothouse block)

    # Windows along the deck (avoid the paddlewheel zone on the far right)
    win_xs = list(range(deck_left + 18, deck_right - 12, 9))
    for i, wx in enumerate(win_xs):
        g.box(wx, deck_top + 2, 7, 4, p.WINDOW_FRAME, chars="+-+|+-+|")
        for dy in range(1, 3):
            for dx in range(1, 6):
                g.set(wx + dx, deck_top + 2 + dy, "·", "#2a2010", p.WINDOW_DARK)
        if i == 2:  # kitchen window — warm glow
            for dy in range(1, 3):
                for dx in range(1, 6):
                    g.set(wx + dx, deck_top + 2 + dy, "~", p.WINDOW_WARM, p.KITCHEN_BG)
            g.stamp(wx + 1, deck_top + 3, "3:47", "#1a0a04", p.WINDOW_WARM)
        elif i in (0, 4):
            for dy in range(1, 3):
                for dx in range(1, 6):
                    g.set(wx + dx, deck_top + 2 + dy, ".", p.WINDOW_DIM, "#1a1408")

    # Door (between OPEN sign area and first window)
    door_x = deck_left + 10
    g.box(door_x, deck_top + 1, 4, 5, p.WINDOW_FRAME, chars="+-+|+-+|")
    for dy in range(2, 5):
        for dx in range(1, 3):
            g.set(door_x + dx, deck_top + 1 + dy, " ", p.DECK_FG, "#1a1206")
    g.set(door_x + 2, deck_top + 4, ".", "#5a4422", "#1a1206")  # doorknob

    # ── Pilothouse + sign on top of the boat
    px, py, pw, ph = 50, 11, 36, 5
    # Roof
    for x in range(px - 1, px + pw + 1):
        g.set(x, py, "_", p.PILOT_FG, g.get_bg(x, py))
    # Walls
    g.set(px - 1, py + 1, "(", p.PILOT_FG, p.PILOT_BG)
    g.set(px + pw, py + 1, ")", p.PILOT_FG, p.PILOT_BG)
    for y in range(py + 1, py + ph):
        for x in range(px, px + pw):
            g.set(x, y, " ", p.DECK_FG, p.PILOT_BG)
    # Bottom edge meets deck
    for x in range(px, px + pw):
        g.set(x, py + ph - 1, "=", p.TRIM, p.PILOT_BG)
    # The neon sign D'AMBROSIO'S
    sign = "D'AMBROSIO'S"
    sx = px + (pw - len(sign)) // 2
    sy = py + 2
    # Halo on adjacent cells
    for i in range(-2, len(sign) + 2):
        for dy in (-1, 1):
            tx, ty = sx + i, sy + dy
            if g.in_bounds(tx, ty) and g.cells[ty][tx]["c"] in (" ", "=", "_", "(", ")"):
                g.cells[ty][tx]["bg"] = p.NEON_HALO
    # The letters
    for i, ch in enumerate(sign):
        g.set(sx + i, sy, ch, p.NEON_RED, p.NEON_HALO)
    # Sub-sign just below: "open 24 hrs"
    sub = "open 24 hrs"
    sbx = px + (pw - len(sub)) // 2
    for i, ch in enumerate(sub):
        g.set(sbx + i, sy + 1, ch, p.NEON_DIM, p.PILOT_BG)

    # ── Smokestack: rises from pilothouse
    smk_x = px + 4
    for y in range(5, py):
        g.set(smk_x, y, "|", p.PILOT_FG, p.SKY_BG)
        g.set(smk_x + 1, y, "|", p.PILOT_FG, p.SKY_BG)
    # Stack cap
    g.set(smk_x - 1, 4, "/", p.PILOT_FG, p.SKY_BG)
    g.set(smk_x,     4, "=", p.PILOT_FG, p.SKY_BG)
    g.set(smk_x + 1, 4, "=", p.PILOT_FG, p.SKY_BG)
    g.set(smk_x + 2, 4, "\\", p.PILOT_FG, p.SKY_BG)
    # Smoke wisps drifting upper-right toward the dawn
    for dx, dy in [(1, 2), (2, 1), (3, 3), (-1, 1), (4, 0), (-2, 2)]:
        x = smk_x + dx
        y = max(0, 3 - dy if dy > 0 else 3)
        if dy > 0:
            y = 3 - dy if 3 - dy >= 0 else random.randint(0, 2)
        if g.in_bounds(x, y):
            g.set(x, y, ".", p.SMOKE, g.get_bg(x, y))

    # ── Paddlewheel: stern, just off the right edge of the boat
    cx, cy, radius = 107, 18, 4
    # Wheel housing rectangle (subtle frame)
    for y in range(cy - radius - 1, cy + radius + 2):
        for x in range(cx - radius - 1, cx + radius + 2):
            if g.in_bounds(x, y):
                g.set(x, y, " ", p.PADDLE, p.PADDLE)
    # Wheel rim (vertically squished for cell aspect)
    for ang_i in range(20):
        a = ang_i / 20.0 * 2 * math.pi
        rx = int(round(cx + math.cos(a) * radius))
        ry = int(round(cy + math.sin(a) * radius * 0.55))
        if g.in_bounds(rx, ry):
            g.set(rx, ry, "O", p.PADDLE_HI, p.PADDLE)
    # Spokes
    for d in range(-radius, radius + 1):
        g.set(cx + d, cy, "=", p.PADDLE_HI, p.PADDLE)
    for d in range(-2, 3):
        g.set(cx, cy + d, "|", p.PADDLE_HI, p.PADDLE)
    g.set(cx, cy, "@", p.PADDLE_HUB, p.PADDLE)
    # Connecting arm from paddlewheel to boat stern
    for x in range(deck_right - 1, cx - radius):
        if g.in_bounds(x, cy):
            g.set(x, cy, "-", p.PADDLE_HI, g.get_bg(x, cy))

    # ── Hull bottom curves
    for x in range(deck_left, deck_right):
        g.set(x, 22, "=", p.HULL_HI, p.HULL)
    for x in range(deck_left + 1, deck_right - 1):
        g.set(x, 23, "_", p.HULL_HI, p.HULL)
    g.set(deck_left,      22, "(", p.HULL_HI, g.get_bg(deck_left, 22))
    g.set(deck_left - 1,  23, "\\", p.HULL_HI, g.get_bg(deck_left - 1, 23))
    g.set(deck_right - 1, 22, ")", p.HULL_HI, g.get_bg(deck_right - 1, 22))
    g.set(deck_right,     23, "/", p.HULL_HI, g.get_bg(deck_right, 23))

    # Waterline shimmer just under hull
    for x in range(deck_left - 1, deck_right + 1):
        if g.in_bounds(x, 24):
            g.set(x, 24, "_", p.WATER_RIPPLE, p.WATER_DEEP)

    # ── Mooring lines: from dock pilings up to the boat hull
    moor_targets = [(DOCK_X1 + 1, 22, deck_left + 1, 22),
                    (DOCK_X2 - 2, 22, deck_left + 4, 22)]
    for sx_, sy_, tx_, ty_ in moor_targets:
        steps = max(abs(tx_ - sx_), 1)
        for i in range(steps):
            t = i / steps
            x = int(round(sx_ + (tx_ - sx_) * t))
            y = int(round(sy_ + (ty_ - sy_) * t)) - 1
            if g.in_bounds(x, y):
                g.set(x, y, "~", "#5a4632", g.get_bg(x, y))

    # ── River: rows 25–32, surrounding boat and beyond
    for y in range(25, 33):
        for x in range(W):
            if g.cells[y][x]["bg"] not in (p.LAND_BG, p.DOCK_BG):
                ch = "~"
                fg = p.WATER_FG
                bg = p.WATER_BG
                if y >= 28:
                    ch = "-" if (x + y) % 3 == 0 else "~"
                    fg = "#16223a"
                if y >= 30:
                    fg = "#0e1828"
                    bg = p.WATER_DEEP
                g.set(x, y, ch, fg, bg)

    # Neon reflection on water below the sign
    ref_cx = sx + len(sign) // 2
    for x in range(max(0, ref_cx - 14), min(W, ref_cx + 14)):
        t = 1 - abs(x - ref_cx) / 14.0
        if t > 0.7 and g.in_bounds(x, 25):
            g.cells[25][x]["fg"] = p.REFLECT_FG
            g.cells[25][x]["bg"] = p.REFLECT_BG
        elif t > 0.4 and g.in_bounds(x, 25):
            g.cells[25][x]["fg"] = p.REFLECT_DIM
            g.cells[25][x]["bg"] = "#100604"
        if t > 0.5 and g.in_bounds(x, 26):
            g.cells[26][x]["fg"] = p.REFLECT_DIM
    for dx, dy in [(-9, 1), (-5, 0), (-2, 2), (0, 0), (3, 1), (6, 0), (9, 1)]:
        rx, ry = ref_cx + dx, 25 + dy
        if g.in_bounds(rx, ry):
            g.set(rx, ry, "*", p.REFLECT_HOT, g.get_bg(rx, ry))

    # ── Caption
    cap = "river  slow  indifferent"
    cap_x = (W - len(cap)) // 2
    g.stamp(cap_x, 35, cap, p.CAPTION, "#050810")

    return g


# ── Registry ─────────────────────────────────────────────────────────────────

def compose_tarot_fool() -> Grid:
    """Major Arcana 0 — The Fool. Gallery card + music visualizer substrate.
    A composite dashboard: the card centered in a SCUMM-machine HUD with
    cite-boxes, equations, mountain silhouettes, hex dumps, VU meters.
    Glitch state is part of the tarot sequence aesthetic; severity ramps
    per card and re-renders evolve."""
    p = Palette
    W, H = 200, 80

    BG = "#050810"
    PANEL_BG = "#0a0e1a"
    FRAME = "#7a8198"
    FRAME_DIM = "#3a4258"
    TEXT = "#cdd2e6"
    TEXT_DIM = "#7a8198"
    ACCENT = "#9bc3ff"
    WARM = "#ffd17a"
    CARD_BG = "#06080e"
    CARD_FRAME = "#cdd2e6"
    FIG_FG = "#e6eaf2"
    FIG_HI = "#ffffff"
    SUN = "#ffd17a"
    GLITCH_FG = "#5a6378"
    VU_LO = "#3a5a4a"
    VU_MID = "#8aaa6a"
    VU_HI = "#ffc060"
    VU_PEAK = "#ff6040"

    g = Grid(W, H, fill=" ", fg=TEXT_DIM, bg=BG)

    # ── Panel helper
    def panel(x, y, w, h, title=""):
        # Light frame
        g.box(x, y, w, h, FRAME, chars="┌─┐│┘─└│")
        # Interior fill (dim panel bg)
        for dy in range(1, h - 1):
            for dx in range(1, w - 1):
                g.set(x + dx, y + dy, " ", TEXT, PANEL_BG)
        if title:
            g.stamp(x + 2, y, "[cite: %s]" % title, TEXT, BG)

    def stamp_lines(x, y, lines, fg=TEXT, bg=PANEL_BG, max_w=999):
        for i, line in enumerate(lines):
            line = line[:max_w]
            g.stamp(x, y + i, line, fg, bg)

    # ── LEFT COLUMN: stacked cite-boxes + audio meters
    panel(0, 0, 30, 14, "THE FOOL")
    stamp_lines(2, 2, [
        "[cite: PIGBOY]",
        "[cite: P1GBOY]",
        "[cite: PEORDY]",
        "[cite: PEGRDY]",
        "[cite: ABETT]",
        "",
        "[cite: THE FOOL walks",
        " off a cliff at a cliff",
        " beginning of every",
        " retelling, ... and",
        " then has a series of",
        " things happen to",
    ], fg=TEXT_DIM)

    # Audio level meters block
    panel(0, 15, 30, 10, "")
    for i, lbl in enumerate(["mf", "ml", "ms"]):
        y = 18 + i * 2
        g.stamp(2, y, lbl + ":", TEXT_DIM, PANEL_BG)
        for x in range(6, 24):
            level = int(((x - 6) / 18.0) * 14)
            ch = "▮" if x - 6 < (10 + i * 2) else "·"
            col = WARM if x - 6 < 4 else (TEXT_DIM if x - 6 < (10 + i * 2) else FRAME_DIM)
            g.set(x, y, ch, col, PANEL_BG)
        g.set(24, y, "|", FRAME, PANEL_BG)

    panel(0, 26, 30, 22, "PIGBOY")
    stamp_lines(2, 28, [
        "[cite: P2GROY]",
        "[cite: P1GBOYI]",
        "[cite: S6T]",
        "[cite: THESABBY]",
        "[cite: THR8BOY]",
        "",
        "[cite: PPIGBOY",
        " [cite: THE PODY]",
        "",
        "[cite: FoOL]",
        "[cite: s numbered 0 and",
        " walks off a cliff at",
        " beginning of every",
        " retelling, and after",
        " happen line.",
        "",
        "[cite: The twatis and it",
        " is the a-azd sosser and",
        " srate to processing",
        " this retelling.",
    ], fg=TEXT_DIM)

    panel(0, 49, 30, 10, "PIGBOY")
    stamp_lines(2, 51, [
        "[cite: He is numbered 0",
        " and walks off at the",
        " beginning of every",
        " retelling, and then has",
        " a series x of tlings",
        " the tooe pootling and",
        " then nour corepuling",
        " retelling.",
    ], fg=TEXT_DIM)

    # ── PCB / circuit pattern strip (cols 32-78, rows 0-40)
    for y in range(0, 38):
        for x in range(32, 78):
            r = random.Random(x * 73 + y * 31)
            if r.random() < 0.18:
                ch = r.choice(["|", "-", "+", ".", "."])
                col = FRAME_DIM if r.random() < 0.7 else FRAME
                g.set(x, y, ch, col, BG)
    # A few "trace" horizontal lines
    for y_line in (5, 12, 19, 26, 33):
        for x in range(33, 77):
            cur = g.cells[y_line][x]["c"]
            if cur == " " and random.Random(x + y_line).random() < 0.55:
                g.set(x, y_line, "-", FRAME_DIM, BG)
        g.set(33, y_line, "+", FRAME, BG)
        g.set(76, y_line, "+", FRAME, BG)
    # Small label
    g.stamp(48, 5, "[cite: çdat6]", FRAME_DIM, BG)

    # Mountain silhouette below PCB strip (rows 38-58, cols 32-78)
    mountain_profile = [3, 4, 5, 6, 8, 10, 9, 7, 5, 7, 9, 11, 12, 10, 8, 6,
                        5, 7, 9, 11, 13, 11, 9, 7, 5, 4, 6, 8, 10, 12, 10, 8,
                        6, 4, 6, 8, 10, 8, 6, 4, 6, 8, 9, 7, 5]
    base_y = 58
    for i in range(len(mountain_profile)):
        x = 32 + i
        if x >= 78:
            break
        h_m = mountain_profile[i]
        top_y = base_y - h_m
        for y in range(top_y, base_y):
            ch = "/" if y == top_y else " "
            g.set(x, y, ch, TEXT_DIM, BG)
        g.set(x, base_y, "_", FRAME, BG)
    g.stamp(33, 60, "[cite: 0]", TEXT_DIM, BG)

    # Inner hex-dump style strip at base
    hex_chars = "0123456789ABCDEF"
    r = random.Random(13)
    for y in range(61, 78):
        for x in range(32, 78):
            if r.random() < 0.42:
                g.set(x, y, r.choice(hex_chars + ".:o "), TEXT_DIM, BG)

    # ── CENTER: The Fool card (cols 80-132, rows 4-66 = 52w x 62h)
    cx, cy, cw, ch_ = 80, 4, 52, 62

    # Card frame
    g.box(cx, cy, cw, ch_, CARD_FRAME, chars="┌─┐│┘─└│")
    for dy in range(1, ch_ - 1):
        for dx in range(1, cw - 1):
            g.set(cx + dx, cy + dy, " ", FIG_FG, CARD_BG)

    # Sun + rays in upper-right inside card (drawn first so figure can override)
    sun_x, sun_y = cx + cw - 9, cy + 3
    g.set(sun_x, sun_y, "*", SUN, CARD_BG)
    g.set(sun_x + 1, sun_y, "O", SUN, CARD_BG)
    g.set(sun_x + 2, sun_y, "*", SUN, CARD_BG)
    g.set(sun_x + 1, sun_y - 1, "|", SUN, CARD_BG)
    g.set(sun_x + 1, sun_y + 1, "|", SUN, CARD_BG)
    g.set(sun_x - 1, sun_y - 1, "\\", SUN, CARD_BG)
    g.set(sun_x + 3, sun_y - 1, "/", SUN, CARD_BG)
    g.set(sun_x - 1, sun_y + 1, "/", SUN, CARD_BG)
    g.set(sun_x + 3, sun_y + 1, "\\", SUN, CARD_BG)
    g.set(sun_x - 2, sun_y, "-", SUN, CARD_BG)
    g.set(sun_x + 4, sun_y, "-", SUN, CARD_BG)

    # Figure — converted from assets/gallery/fool.png via img2ascii
    # (blocks-mono variant, 46 wide), stamped into the card interior.
    fig_piece = OUT_ROOT / "_pieces" / "fool_figure.json"
    if fig_piece.exists():
        # Center the 46-wide piece inside the 52-wide card
        fig_x = cx + (cw - 46) // 2
        fig_y = cy + 1
        _stamp_subgrid(g, fig_x, fig_y, fig_piece, fg_override=FIG_FG)
    else:
        # Fallback: stick figure (kept for reference / if piece is missing)
        figure = [
            "    ___    ",
            "   /   \\   ",
            "  | . . |  ",
            "   \\_v_/   ",
            "   _/|\\__  ",
            "  /  |  \\  ",
            " /   |   \\ ",
            "|    |    |",
        ]
        fig_x = cx + (cw - 11) // 2
        fig_y = cy + 12
        for i, line in enumerate(figure):
            g.stamp(fig_x, fig_y + i, line, FIG_FG, CARD_BG)

    # "0" label at top center (drawn AFTER figure so it sits on top)
    g.set(cx + cw // 2, cy + 1, "0", CARD_FRAME, CARD_BG)

    # "FOOL" label at bottom of card (drawn after figure)
    g.stamp(cx + (cw - 4) // 2, cy + ch_ - 2, "FOOL", CARD_FRAME, CARD_BG)

    # ── RIGHT OF CARD: equations + Cathedral of Rust mountains
    # Equations
    eq_lines = [
        "[teat tnare]",
        "                  1     P     1",
        "         f(e) = ---- + (---  - ---)²",
        "                 30     E²    32",
        "",
        "       d = (vo Rot)",
        "                            avoxed",
        "[cite: section]",
        "                 P (P - 0.27)",
        "       E = h * ---------------",
        "                    23",
        "[ae : Equation]                         _",
        "                              F(st = (b * 0.10)",
        "                                    ----------",
        "                                       H * n¸",
    ]
    for i, line in enumerate(eq_lines):
        g.stamp(135, 2 + i, line, TEXT_DIM, BG)

    # Cathedral of Rust mountain range
    g.stamp(140, 20, "[cite: Cathedral of Rust]", TEXT_DIM, BG)
    cor_profile = [3, 5, 6, 8, 10, 11, 9, 7, 6, 8, 10, 12, 11, 9, 7, 5,
                   3, 4, 6, 8, 10, 12, 10, 8, 6, 4, 5, 7, 9, 7, 5]
    for i, h_m in enumerate(cor_profile):
        x = 135 + i
        if x >= 170:
            break
        top_y = 32 - h_m
        for y in range(top_y, 32):
            ch = "/\\"[y % 2] if y == top_y else " "
            g.set(x, y, ch, TEXT_DIM, BG)
        g.set(x, 32, "_", FRAME_DIM, BG)
    g.stamp(140, 35, "[cite: Cathedral of Rust]", TEXT_DIM, BG)
    for i, h_m in enumerate(cor_profile):
        x = 135 + i
        if x >= 170:
            break
        top_y = 47 - h_m
        for y in range(top_y, 47):
            ch = "/\\"[y % 2] if y == top_y else " "
            g.set(x, y, ch, FRAME_DIM, BG)
        g.set(x, 47, "_", FRAME_DIM, BG)

    # Garbled pixel-cluster panel (rows 50-65, cols 135-168)
    for y in range(50, 64):
        for x in range(135, 168):
            r2 = random.Random(x * 91 + y * 17)
            if r2.random() < 0.5:
                ch = r2.choice(["▓", "▒", "░", "█", "·"])
                col = r2.choice([FRAME_DIM, TEXT_DIM, FRAME])
                g.set(x, y, ch, col, BG)

    # ── RIGHT COLUMN: VU meters + player controls + cite boxes
    panel(170, 0, 30, 14, "THE FOOL")
    # mini-bar visualizer placeholder text
    for y in range(2, 12):
        seed = y * 7 + 3
        rr = random.Random(seed)
        bar_w = rr.randint(3, 22)
        g.stamp(172, y, "│", FRAME, PANEL_BG)
        for x in range(173, 173 + 22):
            if x - 173 < bar_w:
                col = VU_LO if x - 173 < 8 else (VU_MID if x - 173 < 14 else (VU_HI if x - 173 < 18 else VU_PEAK))
                g.set(x, y, "█", col, PANEL_BG)
            else:
                g.set(x, y, "·", FRAME_DIM, PANEL_BG)

    panel(170, 15, 30, 14, "PIGBOY")
    # Music chart placeholder — sparkline + bars
    chart = [3, 5, 4, 7, 9, 12, 10, 8, 6, 9, 11, 14, 12, 10, 8, 6, 9, 7, 5, 3,
             4, 6, 8]
    base = 26
    for i, v in enumerate(chart):
        x = 172 + i
        if x >= 198:
            break
        for y in range(base - v, base):
            g.set(x, y, "█", VU_MID if y > base - v // 2 else VU_HI, PANEL_BG)

    # Player controls row
    g.stamp(172, 30, "[▶][⏸][⏭] [▮ ▮▮▮▮▮]", TEXT_DIM, BG)

    # Equalizer/mode strip
    for y in range(33, 47):
        seed = y * 13
        rr = random.Random(seed)
        for col_i, col_x in enumerate(range(172, 196, 4)):
            v = rr.randint(0, 8)
            col = [VU_LO, VU_LO, VU_MID, VU_MID, VU_MID, VU_HI, VU_HI, VU_PEAK, VU_PEAK][min(v, 8)]
            g.set(col_x, y, "█" if v > 4 else ("▮" if v > 2 else "·"), col, BG)

    panel(170, 48, 30, 11, "PIGBOY")
    stamp_lines(172, 50, [
        "[cite: ACT I, PART 1:",
        " THE ACCIDENT]",
        "",
        "[cite: THE FOOL walks",
        " off a cliff at",
        " the beginning of every",
        " retelling",
        " to string....",
    ], fg=TEXT_DIM)

    panel(170, 60, 30, 9, "A.5%T OF FAITH")
    stamp_lines(172, 62, [
        "[cite: THE FOOL walks",
        " off a cliff at the",
        " beginning of every",
        " retelling,",
        " and then has a series",
        " of things happen to",
        " him...",
    ], fg=TEXT_DIM)

    # ── BOTTOM STRIP: hex dump + citations
    # Hex dump under center-right (cols 80-170, rows 67-77)
    hex_dump_lines = [
        "weSores",
        "satioo:",
        "atei:",
        "[ite",
        "8.5.E.[",
        "ttechnical etengeting:Lthe.Tooel.I..ite",
        "[OOBETS.OSST05PFEKO3IELOCO0S91153 '5 'FOO[",
        "'APOQTFAKE(0SBEC]I3ZIIEIGROASL02) '5 8stee",
    ]
    for i, line in enumerate(hex_dump_lines):
        g.stamp(82, 67 + i, line, GLITCH_FG, BG)

    # SINKHOLE / LEAP OF FAITH cites
    g.stamp(105, 67, "[cite: THE SINKHOLE OPENED UP THREE YEARS AGO]", TEXT_DIM, BG)
    g.stamp(105, 70, "[cite: LEAP OF FAITH]", ACCENT, BG)
    g.stamp(105, 72, "[cite: Retelling the story, steps off a cliff at the", TEXT_DIM, BG)
    g.stamp(105, 73, " beginning of every retelling, and then has a", TEXT_DIM, BG)

    # ASCII.THE FOOL stamp lower left
    g.stamp(34, 49, "[cite: A.S.C.I.I. THE FOOL]", ACCENT, BG)

    # Bottom right corner Modern Mythology tag
    g.stamp(155, 78, "[cite: Modern Mythology: Major Arcana]", FRAME, BG)
    g.set(196, 78, "◆", ACCENT, BG)

    # ── GLITCH BAND (evolving — re-seed per render)
    # A wide horizontal band of light corruption across the upper-middle
    _glitch_band(g, 0, 38, W, 2, severity=0.18, fg=GLITCH_FG, seed=random.randint(0, 9999))
    # Vertical strip near the figure
    _glitch_band(g, 60, 10, 6, 45, severity=0.10, fg=GLITCH_FG, seed=random.randint(0, 9999))

    return g


SUBSTRATES = {
    # Per-scene auto-loads: filename must match the scene's id.
    "scene/vol5_ch0_booth6": compose_diner_predawn,

    # Named assets, referenced explicitly with {"t": "substrate", "src": "..."}.
    "vol5/diner_predawn":    compose_diner_predawn,

    # Gallery items (unlockable). Same JSON shape; loaded by gallery/player.
    "gallery/tarot_fool":    compose_tarot_fool,
}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    written = []
    for name, fn in SUBSTRATES.items():
        if only and only != name:
            continue
        g = fn()
        out = OUT_ROOT / f"{name}.json"
        g.save(out)
        written.append(out)
    for p in written:
        print(p)
    if not written:
        print("nothing written", file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()
