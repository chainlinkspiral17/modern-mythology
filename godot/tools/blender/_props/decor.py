# _props/decor.py
# ════════════════════════════════════════════════════════════════
# Wall + ceiling + counter ornamentation — the things that fill
# the room but aren't transactional fixtures. Wall clock, faded
# poster, payphone, calendar, hanging air freshener tree, etc.
# Reusable across any indoor locale.
# ════════════════════════════════════════════════════════════════
import math
from . import palette as P
from .geometry import make_box, make_cyl


def make_wall_clock(prefix, anchor, *, frozen_hour=11, frozen_min=47,
                    palette=None, facing='-Y'):
    """Wall-mounted analog clock. anchor=(wall_x, wall_y, center_z) ON the
    wall's ROOM face; the barrel is centred on it (2 cm each way).
    facing = the direction the dial looks, INTO the room: '-Y' (a north
    wall, the old fixed behaviour and the default), '+Y' (south), '-X'
    (east), '+X' (west) — 2026-09-24: about twenty clocks on east/west
    walls faced along their wall with the dial inside it.
    Frozen time defaults to 11:47 (canon vol6 Sam-shift hour);
    pass (frozen_hour, frozen_min) to override for other locales."""
    palette = palette or {}
    face = palette.get("face", (0.94, 0.92, 0.86, 1.0))
    rim = palette.get("rim", (0.42, 0.40, 0.36, 1.0))
    cx, cy, cz = anchor
    f = str(facing).upper()
    along_x = f in ('-X', '+X')
    sgn = -1.0 if f.startswith('-') else 1.0

    def at(lat, depth, dz):
        """lat along the wall, depth toward the room, dz up."""
        if along_x:
            return (cx + sgn * depth, cy + lat, cz + dz)
        return (cx + lat, cy + sgn * depth, cz + dz)

    def sz(lat, depth, tall):
        return (depth, lat, tall) if along_x else (lat, depth, tall)

    ax = 'X' if along_x else 'Y'
    # Layered back to front (2026-09-24: the rim was a SOLID 20 cm disc IN
    # FRONT of the 18 cm face — the face, ticks and hands were all inside
    # it and every kit clock rendered as a blank grey disc): the rim sits
    # BEHIND the face's front and shows only as the ring past r 0.18; the
    # ticks lie on the face; the hands lie on the ticks.
    # 2026-09-27 (the 09-26 sheet, eleven kitchens): the off-white face
    # is the colour of a cream kitchen wall under a warm practical, so
    # the clock read as a RING OF SIX BLACK DOTS on the wall — four ticks
    # and two hands with nothing behind them. The rim is what makes a
    # clock read from across a room: a dark ring 3.5 cm wide (r 0.215
    # behind the face's front), and a hub where the hands meet.
    rim = palette.get("rim", (0.18, 0.16, 0.14, 1.0))
    make_cyl(f"{prefix}_Face", (cx, cy, cz), 0.18, 0.04, face, axis=ax)
    make_cyl(f"{prefix}_Rim", (cx, cy, cz), 0.215, 0.02, rim, axis=ax)
    make_cyl(f"{prefix}_Hub", at(0.0, 0.028, 0.0), 0.012, 0.006, P.METAL_BLACK, axis=ax)
    for ang_i, (mx, mz) in enumerate([(0.0, +0.13), (+0.13, 0.0),
                                       (0.0, -0.13), (-0.13, 0.0)]):
        make_box(f"{prefix}_Tick_{ang_i}", at(mx, 0.0225, mz),
                 sz(0.02, 0.005, 0.02), P.METAL_BLACK)
    # Hands — point to frozen_hour / frozen_min on a 12-hour clock face
    hour_ang = ((frozen_hour % 12) + frozen_min / 60.0) * (math.pi * 2 / 12) - math.pi / 2
    min_ang = (frozen_min / 60.0) * (math.pi * 2) - math.pi / 2
    h_len = 0.10
    m_len = 0.16
    make_box(f"{prefix}_HourHand",
             at(math.cos(hour_ang) * h_len * 0.5, 0.027, math.sin(hour_ang) * h_len * 0.5),
             sz(0.05, 0.004, 0.05), P.METAL_BLACK)
    make_box(f"{prefix}_MinuteHand",
             at(math.cos(min_ang) * m_len * 0.5, 0.027, math.sin(min_ang) * m_len * 0.5),
             sz(0.08, 0.004, 0.05), P.METAL_BLACK)


def make_fire_extinguisher(prefix, anchor, *, palette=None):
    """Wall-bracketed red fire extinguisher. anchor=(wall_x, wall_y, base_z)."""
    palette = palette or {}
    red = palette.get("red", (0.74, 0.16, 0.14, 1.0))
    ex, ey, ez = anchor
    make_cyl(f"{prefix}_Body", (ex, ey, ez + 0.86), 0.10, 0.50, red)
    make_cyl(f"{prefix}_Top", (ex, ey, ez + 1.20), 0.08, 0.18,
             P.METAL_BLACK)
    make_box(f"{prefix}_Bracket", (ex - 0.04, ey, ez + 0.86),
             (0.04, 0.18, 0.50), P.METAL_STEEL)
    make_box(f"{prefix}_Sign", (ex - 0.02, ey - 0.40, ez + 1.60),
             (0.005, 0.30, 0.30), red)


def make_payphone(prefix, anchor, *, palette=None):
    """Wall-mounted period payphone. anchor=(wall_x, wall_y, center_z)."""
    palette = palette or {}
    body = palette.get("body", (0.32, 0.30, 0.30, 1.0))
    trim = palette.get("trim", (0.20, 0.18, 0.18, 1.0))
    px, py, pz = anchor
    make_box(f"{prefix}_Box", (px, py, pz), (0.06, 0.34, 0.60), body)
    # the hood on the wall over the box (2026-09-23: it hung 9 cm over
    # the box and 4 cm off the wall)
    make_box(f"{prefix}_Hood", (px - 0.12, py, pz + 0.35),
             (0.30, 0.36, 0.10), trim)
    make_box(f"{prefix}_Handset",
             (px - 0.06, py - 0.20, pz),
             (0.04, 0.04, 0.24), trim)
    make_box(f"{prefix}_CoinSlot",
             (px - 0.04, py + 0.08, pz + 0.16),
             (0.02, 0.10, 0.02), P.METAL_BLACK)
    make_box(f"{prefix}_Keypad",
             (px - 0.04, py, pz - 0.12),
             (0.02, 0.16, 0.20), P.METAL_BLACK)
    for r in range(4):
        for c in range(3):
            make_box(f"{prefix}_Key_{r}_{c}",
                     (px - 0.05,
                      py - 0.06 + c * 0.06,
                      pz - 0.20 + r * 0.045),
                     (0.005, 0.04, 0.034), P.PAPER_AGED)


def make_calendar(prefix, anchor, *, palette=None, axis='Y'):
    """Wall calendar with a faded photograph + month grid.

    axis='Y' (default): on an EAST/WEST wall (thin in X).
    axis='X': on a NORTH/SOUTH wall (thin in Y).
    """
    palette = palette or {}
    paper = palette.get("paper", (0.78, 0.62, 0.46, 1.0))
    cx, cy, cz = anchor
    # the grid prints on the ROOM side (2026-10-08: on every east wall it
    # printed +x, behind the sheet, into the wall)
    if str(axis).upper() == 'X':
        d = -1 if cy > 1.0 else 1
        make_box(f"{prefix}_Body", (cx, cy, cz),
                 (0.40, 0.005, 0.50), paper)
        make_box(f"{prefix}_Grid", (cx, cy + 0.002 * d, cz - 0.15),
                 (0.34, 0.001, 0.20), P.PAPER)
        return
    d = -1 if cx > 0 else 1
    make_box(f"{prefix}_Body", (cx, cy, cz),
             (0.005, 0.40, 0.50), paper)
    make_box(f"{prefix}_Grid", (cx + 0.002 * d, cy, cz - 0.15),
             (0.001, 0.34, 0.20), P.PAPER)


def make_faded_poster(prefix, anchor, *, palette=None, axis='Y', into_room=None, kind=None):
    """Sun-faded poster on a wall. anchor=(wall_x, wall_y, center_z).

    axis='Y' (default): hangs on an EAST/WEST wall — thin in X, spans Y.
    axis='X': hangs on a NORTH/SOUTH wall — thin in Y, spans X.
    into_room (2026-09-24): +1 / -1, the direction along the wall's
    normal the ROOM lies; the print goes on that side.

    2026-10-08: every poster in 38 rooms was the SAME tan sheet with a
    dark block and a dark bar — on the contact sheet, three empty frames
    on every bedroom's west wall. A poster reads by its DESIGN: `kind`
    picks one (band / movie / comic / sports), and when not given the
    prefix's hash does, so a wall of three posters is three posters.
    The colours are sun-faded; a white margin frames the print."""
    palette = palette or {}
    cx, cy, cz = anchor
    along_x = str(axis).upper() == 'X'
    if into_room is None:
        into_room = (-1 if cy >= 0 else 1) if along_x else (-1 if cx >= 0 else 1)
    d = into_room
    kinds = ("band", "movie", "comic", "sports")
    seed = sum(ord(ch) * (i + 1) for i, ch in enumerate(prefix))
    if kind is None:
        kind = kinds[seed % len(kinds)]
    k = seed // len(kinds)                 # varies the colours WITHIN a kind (2026-10-08:
                                           # three show bills on one wall were one bill)
    fields = ((0.22, 0.20, 0.28, 1.0), (0.46, 0.18, 0.18, 1.0), (0.16, 0.30, 0.32, 1.0), (0.30, 0.26, 0.18, 1.0), (0.84, 0.80, 0.70, 1.0))
    brights = ((0.86, 0.46, 0.30, 1.0), (0.84, 0.72, 0.36, 1.0), (0.42, 0.62, 0.62, 1.0), (0.76, 0.40, 0.56, 1.0), (0.52, 0.70, 0.40, 1.0))

    def bright(i):
        return brights[(k + i) % len(brights)]

    def box(name, u, v, w, h, col, layer=1):
        off = 0.0035 * d * layer
        if along_x:
            make_box(f"{prefix}_{name}", (cx + u, cy + off, cz + v), (w, 0.002 if layer else 0.005, h), col)
        else:
            make_box(f"{prefix}_{name}", (cx + off, cy + u, cz + v), (0.002 if layer else 0.005, w, h), col)

    def disc(name, u, v, r, col, layer=1):
        off = 0.0035 * d * layer
        if along_x:
            make_cyl(f"{prefix}_{name}", (cx + u, cy + off, cz + v), r, 0.002, col, axis='Y', segments=14)
        else:
            make_cyl(f"{prefix}_{name}", (cx + off, cy + u, cz + v), r, 0.002, col, axis='X', segments=14)

    paper = palette.get("body", (0.90, 0.87, 0.80, 1.0))
    ink = palette.get("ink", (0.26, 0.22, 0.22, 1.0))
    box("Body", 0.0, 0.0, 0.60, 0.80, paper, layer=0)
    if kind == "band":
        box("Field", 0.0, 0.02, 0.54, 0.70, fields[k % 4])
        for bi in range(3):
            w = (0.46, 0.38, 0.30, 0.46)[(k + bi) % 4]
            box(f"Figure_{bi}", 0.0, 0.10 - bi * 0.09, w, 0.06, bright(bi), layer=2)
        box("Title", 0.0, 0.27, 0.46, 0.09, (0.94, 0.90, 0.80, 1.0), layer=2)
        for li in range(3):
            box(f"Dates_{li}", 0.0, -0.20 - li * 0.045, 0.30 - li * 0.06, 0.018, (0.90, 0.86, 0.78, 1.0), layer=2)
    elif kind == "movie":
        box("Field", 0.0, 0.02, 0.54, 0.70, ((0.30, 0.36, 0.48, 1.0), (0.48, 0.30, 0.26, 1.0), (0.24, 0.38, 0.30, 1.0))[k % 3])
        disc("Figure_Head", 0.0, 0.14, 0.075, (0.12, 0.12, 0.16, 1.0), layer=2)
        box("Figure_Shoulders", 0.0, -0.02, 0.30, 0.16, (0.12, 0.12, 0.16, 1.0), layer=2)
        box("Glow", 0.0, 0.22, 0.54, 0.04, bright(0), layer=2)
        box("Title", 0.0, -0.20, 0.46, 0.08, (0.92, 0.80, 0.42, 1.0), layer=2)
        box("Credits", 0.0, -0.29, 0.40, 0.03, (0.80, 0.80, 0.80, 1.0), layer=2)
    elif kind == "comic":
        box("Title", 0.0, 0.30, 0.54, 0.12, bright(3))
        cols = tuple(bright(i) for i in range(4))
        for pi_, (u, v) in enumerate(((-0.135, 0.10), (0.135, 0.10), (-0.135, -0.18), (0.135, -0.18))):
            box(f"Figure_{pi_}", u, v, 0.25, 0.26, cols[pi_])
        box("Logo", 0.0, 0.30, 0.30, 0.05, (0.96, 0.94, 0.88, 1.0), layer=2)
    else:   # sports
        box("Field", 0.0, 0.02, 0.54, 0.70, ((0.28, 0.46, 0.34, 1.0), (0.20, 0.28, 0.46, 1.0), (0.46, 0.22, 0.20, 1.0))[k % 3])
        disc("Figure_Ball", 0.10, 0.10, 0.12, (0.90, 0.56, 0.24, 1.0), layer=2)
        box("Figure_Stripe", -0.10, -0.06, 0.08, 0.40, (0.94, 0.92, 0.86, 1.0), layer=2)
        box("Title", 0.0, -0.27, 0.46, 0.08, ink if ink != (0.26, 0.22, 0.22, 1.0) else (0.94, 0.92, 0.86, 1.0), layer=2)


def make_air_freshener_tree(prefix, anchor, *, count=3, palette=None):
    """Pine-tree air-fresheners hanging on a wire above the register."""
    palette = palette or {}
    colors = palette.get("colors", [
        (0.42, 0.52, 0.36, 1.0),    # pine green
        (0.74, 0.32, 0.20, 1.0),    # cherry rust
        (0.42, 0.52, 0.62, 1.0),    # dusty blue
    ])
    bx, by, base_z = anchor
    make_box(f"{prefix}_Wire", (bx, by, base_z + 0.18),
             (0.005, 0.005, 0.36), P.METAL_BLACK)
    for ti in range(count):
        ty = by + (ti - (count - 1) / 2.0) * 0.06
        col = colors[ti % len(colors)]
        for tier in range(3):
            scale = 0.10 - tier * 0.025
            make_box(f"{prefix}_{ti}_Tier_{tier}",
                     (bx, ty, base_z - 0.04 + tier * 0.04),
                     (0.005, scale, 0.04), col)
        make_box(f"{prefix}_{ti}_Trunk",
                 (bx, ty, base_z - 0.18),
                 (0.005, 0.02, 0.06), (0.42, 0.30, 0.20, 1.0))


def make_floor_plant(prefix, anchor, *, palette=None, kind=None):
    """A potted plant on the floor. anchor=(x, y, floor_z).

    2026-10-08: it was ONE plant in 37 rooms — the same three-ring pot and
    a stack of disc "leaves" floating 10 cm off a pencil stem, in the same
    south-west corner of every template room on the contact sheet. A plant
    reads by its kind: `kind` picks one (snake / fern / ficus / monstera),
    and when not given the prefix's hash does."""
    from .geometry import make_blob, make_tube, make_rot_box, make_lathe
    palette = palette or {}
    px, py, z0 = anchor
    kinds = ("snake", "fern", "ficus", "monstera")
    if kind is None:
        kind = kinds[sum(ord(ch) * (i + 3) for i, ch in enumerate(prefix)) % len(kinds)]
    leaf = palette.get("leaf", {"snake": (0.24, 0.40, 0.24, 1.0), "fern": (0.44, 0.60, 0.30, 1.0),
                                "ficus": (0.26, 0.44, 0.24, 1.0), "monstera": (0.18, 0.40, 0.24, 1.0)}[kind])
    pot = palette.get("pot", ((0.62, 0.40, 0.28, 1.0), (0.86, 0.84, 0.80, 1.0), (0.26, 0.28, 0.30, 1.0),
                              (0.70, 0.52, 0.34, 1.0))[kinds.index(kind)])
    soil = (0.24, 0.17, 0.12, 1.0)
    # the pot: a turned profile, the soil just under its rim
    ph = 0.30 if kind in ("snake", "ficus") else 0.24
    make_lathe(f"{prefix}_Pot", (px, py, z0), [(0.13, 0.0), (0.15, 0.02), (0.18, ph - 0.03), (0.19, ph), (0.0, ph)], pot, segments=14)
    make_cyl(f"{prefix}_Pot_Fill", (px, py, z0 + ph - 0.015), 0.165, 0.02, soil, segments=12)
    top = z0 + ph - 0.005
    if kind == "snake":
        dark = (0.18, 0.30, 0.18, 1.0)
        for b in range(7):
            ang = b * 2.399
            r = 0.04 + 0.03 * (b % 3)
            h = 0.48 + 0.10 * ((b * 5) % 4)
            make_rot_box(f"{prefix}_Leaf_{b}", (px + math.cos(ang) * r, py + math.sin(ang) * r, top + h / 2.0),
                         (0.07, 0.012, h), leaf if b % 2 else dark, yaw=ang, pitch=0.0, roll=0.10 * ((b % 3) - 1))
    elif kind == "fern":
        for b in range(3):
            ang = b * 2.09
            make_blob(f"{prefix}_Leaf_{b}", (px + math.cos(ang) * 0.10, py + math.sin(ang) * 0.10, top + 0.14), 0.24,
                      leaf, noise=0.35, seed=7 + b, squash=0.55)
        make_blob(f"{prefix}_Leaf_Crown", (px, py, top + 0.24), 0.18, leaf, noise=0.30, seed=11, squash=0.6)
    elif kind == "ficus":
        make_tube(f"{prefix}_Trunk", [(px, py, top - 0.01), (px + 0.03, py, top + 0.45), (px - 0.02, py + 0.02, top + 0.85)], 0.025,
                  (0.40, 0.32, 0.24, 1.0), segments=6)
        for b, (dx, dy, dz, r) in enumerate(((0.0, 0.02, 0.92, 0.26), (0.12, -0.06, 0.74, 0.18), (-0.12, 0.08, 0.66, 0.16))):
            make_blob(f"{prefix}_Leaf_{b}", (px + dx, py + dy, top + dz), r, leaf, noise=0.28, seed=17 + b, squash=0.85)
    else:   # monstera: stems from the soil, a broad leaf on each
        for b in range(5):
            ang = b * 1.257 + 0.3
            r = 0.30 + 0.06 * (b % 2)
            lx, ly, lz = px + math.cos(ang) * r, py + math.sin(ang) * r, top + 0.42 + 0.12 * (b % 3)
            make_tube(f"{prefix}_Stem_{b}", [(px + math.cos(ang) * 0.03, py + math.sin(ang) * 0.03, top - 0.01),
                                            (px + math.cos(ang) * r * 0.5, py + math.sin(ang) * r * 0.5, lz - 0.05),
                                            (lx, ly, lz)], 0.008, (0.30, 0.48, 0.28, 1.0), segments=5)
            make_rot_box(f"{prefix}_Leaf_{b}", (lx, ly, lz), (0.24, 0.20, 0.012), leaf, yaw=ang, pitch=0.0, roll=0.0)
