"""The Bindery — vol6 placement script.

A narrow used-bookshop storefront on Live Oak Street, New Auburn,
four blocks off the interstate exit. Canon (vol6 ch2): the front
window has books "arranged in the lazy attractive chaos of a bookshop
that has stopped trying to sell its books"; the bell over the door is
lower and mellower than Cosmic's; Hal (sixties, white beard, Hawaiian
shirt) reads behind the counter; the Borges section is "third shelf
down, back left, past the Bolaño."

Hero features: the two long walls of tall bookcases with book rows in
a muted spine palette, the counter mid-shop on the east side (register,
book stacks, reading lamp), a low center island of display tables
making a single aisle, the front display window with its stacked
books, three pendant lamps down the aisle, a rolling ladder against
the west shelves, and the Borges corner back-left with a small shelf
sign.

Coordinate frame: Blender Z-up. y=0 is the storefront (south) wall
with window + door; +Y runs back into the shop; walls at x=±ROOM_W/2.
glTF export remaps to Godot (x, z, -y).
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

# ── Narrow-storefront footprint ──
ROOM_W = 4.2      # x ∈ [-2.1, 2.1]
ROOM_D = 9.0      # y ∈ [0, 9.0]  (storefront at y=0)
CEIL = 3.2        # old commercial ceiling, tall

COL_WALL = (0.55, 0.48, 0.38, 1.0)      # aged ochre plaster
COL_BASE = (0.30, 0.24, 0.17, 1.0)
COL_FLOOR = (0.38, 0.27, 0.16, 1.0)     # worn oak boards
COL_SEAM = (0.28, 0.20, 0.12, 1.0)
COL_CEIL = (0.42, 0.38, 0.32, 1.0)      # old tin-look ceiling
COL_CASE = (0.26, 0.18, 0.11, 1.0)      # dark walnut casework
COL_CASE_LT = (0.34, 0.24, 0.15, 1.0)
COL_COUNTER = (0.30, 0.21, 0.13, 1.0)
COL_RUG = (0.36, 0.16, 0.14, 1.0)       # worn red runner
COL_RUG_EDGE = (0.24, 0.11, 0.10, 1.0)
COL_GLASS = (0.55, 0.62, 0.66, 0.35)
COL_FRAME = (0.16, 0.14, 0.12, 1.0)     # storefront framing, near-black
COL_BRASS = (0.66, 0.52, 0.24, 1.0)
COL_LAMP = (1.00, 0.86, 0.55, 1.0)      # warm bulb — blooms via glow
COL_SHADE = (0.28, 0.30, 0.22, 1.0)     # green pendant shade
COL_PAPER = (0.82, 0.78, 0.68, 1.0)
COL_SIGN = (0.86, 0.82, 0.72, 1.0)

# Muted spine palette — cycled deterministically so every shelf reads
# as many books without ever repeating an obvious pattern.
SPINES = [
    (0.48, 0.20, 0.16, 1.0), (0.22, 0.30, 0.24, 1.0), (0.60, 0.52, 0.36, 1.0),
    (0.24, 0.22, 0.34, 1.0), (0.55, 0.38, 0.20, 1.0), (0.30, 0.14, 0.12, 1.0),
    (0.42, 0.44, 0.46, 1.0), (0.18, 0.24, 0.30, 1.0), (0.62, 0.58, 0.50, 1.0),
    (0.36, 0.28, 0.18, 1.0), (0.50, 0.30, 0.30, 1.0), (0.26, 0.34, 0.20, 1.0),
]


def _book_run(prefix, x, y0, y1, z, *, axis='Y', lean_slot=3, seed=0):
    """A run of book spines filling [y0,y1] along Y (or [x0,x1] along X
    when axis='X' — then x is the fixed y). Every `lean_slot`-th slot
    is a gap or a leaning book so rows read hand-shelved."""
    span = (y1 - y0)
    n = max(3, int(span / 0.055))
    w = span / n
    for i in range(n):
        k = (i * 7 + seed * 5) % len(SPINES)
        if (i + seed) % (lean_slot * 4) == lean_slot:
            continue  # a gap — somebody bought one
        h = 0.19 + 0.055 * ((i * 3 + seed) % 4)
        d = 0.14 + 0.02 * ((i + seed) % 3)
        cy = y0 + w * (i + 0.5)
        if axis == 'Y':
            make_box(f"{prefix}_{i}", (x, cy, z + h / 2.0), (d, w * 0.82, h), SPINES[k])
        else:
            make_box(f"{prefix}_{i}", (cy, x, z + h / 2.0), (w * 0.82, d, h), SPINES[k])


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False,
                 palette={"tile": COL_CEIL})
    # Worn red runner down the aisle
    make_box("Rug", (-0.35, 4.4, 0.008), (1.1, 6.4, 0.012), COL_RUG)
    make_box("Rug_Edge_S", (-0.35, 1.25, 0.012), (1.1, 0.10, 0.008), COL_RUG_EDGE)
    make_box("Rug_Edge_N", (-0.35, 7.55, 0.012), (1.1, 0.10, 0.008), COL_RUG_EDGE)


def build_storefront():
    """South wall: big display window (west of center) + glazed door
    (east) + the low mellow bell + window display of stacked books."""
    # Framing posts
    for fx in (-ROOM_W / 2.0, -0.05, 1.05, ROOM_W / 2.0):
        make_box(f"Front_Post_{fx:+.2f}", (fx, 0.0, CEIL / 2.0), (0.14, 0.16, CEIL), COL_FRAME)
    # Header + sill
    make_box("Front_Header", (0.0, 0.0, CEIL - 0.20), (ROOM_W + 0.2, 0.16, 0.40), COL_FRAME)
    make_box("Front_Sill", (-1.08, 0.0, 0.42), (1.95, 0.16, 0.08), COL_FRAME)
    make_box("Front_Knee", (-1.08, 0.0, 0.20), (1.95, 0.14, 0.40), COL_CASE)
    # Display window glass (west bay)
    make_box("Front_Glass", (-1.08, 0.0, 1.70), (1.90, 0.03, 2.15), COL_GLASS)
    # Glazed door (east bay), ajar slightly inward
    make_box("Door", (0.55, 0.10, 1.05), (0.90, 0.05, 2.10), COL_FRAME)
    make_box("Door_Glass", (0.55, 0.10, 1.35), (0.66, 0.02, 1.30), COL_GLASS)
    make_cyl("Door_Knob", (0.90, 0.14, 1.02), 0.035, 0.04, COL_BRASS, segments=8, axis='Y')
    # The bell — small brass dome over the door (lower, mellower)
    make_cyl("Door_Bell", (0.55, 0.16, 2.24), 0.05, 0.06, COL_BRASS, segments=8)
    make_box("Door_Bell_Arm", (0.55, 0.13, 2.30), (0.03, 0.10, 0.02), COL_FRAME)
    # ── Window display: the lazy attractive chaos ──
    make_box("Display_Deck", (-1.08, 0.55, 0.50), (1.85, 0.85, 0.06), COL_CASE_LT)
    stacks = [(-1.70, 0.45, 4), (-1.30, 0.70, 6), (-0.85, 0.40, 3), (-0.50, 0.62, 5)]
    for si, (sx, sy, count) in enumerate(stacks):
        for b in range(count):
            k = (si * 5 + b * 3) % len(SPINES)
            make_box(f"WinStack_{si}_{b}",
                     (sx + 0.012 * ((b * 7) % 3 - 1), 0.30 + sy * 0.5 + 0.0,
                      0.55 + b * 0.045),
                     (0.30 - 0.02 * (b % 2), 0.22, 0.042), SPINES[k])
    # One book standing open on top of the tallest stack
    make_box("WinOpen_L", (-1.36, 0.62, 0.85), (0.14, 0.20, 0.01), COL_PAPER)
    make_box("WinOpen_R", (-1.22, 0.62, 0.85), (0.14, 0.20, 0.01), COL_PAPER)


def build_wall_cases():
    """Tall bookcases the length of both side walls, broken into bays.
    The Borges section is the back-left (NW) bay, marked by its sign."""
    z_shelves = [0.25, 0.72, 1.19, 1.66, 2.13, 2.60]
    for side, wx in (("W", -ROOM_W / 2.0 + 0.24), ("E", ROOM_W / 2.0 - 0.24)):
        y_start = 1.3 if side == "W" else 2.9   # east side leaves room for counter
        bays = int((ROOM_D - 0.4 - y_start) / 1.9)
        for b in range(bays):
            y0 = y_start + b * 1.9
            y1 = min(y0 + 1.8, ROOM_D - 0.3)
            cy = (y0 + y1) / 2.0
            # verticals + back panel
            make_box(f"Case_{side}{b}_Back", (wx + (0.10 if side == "W" else -0.10), cy,
                     1.45), (0.04, y1 - y0, 2.9), COL_CASE)
            for yy in (y0, y1):
                make_box(f"Case_{side}{b}_V_{yy:.1f}", (wx, yy, 1.45),
                         (0.34, 0.05, 2.9), COL_CASE)
            make_box(f"Case_{side}{b}_Top", (wx, cy, 2.92), (0.36, y1 - y0, 0.05), COL_CASE)
            for zi, z in enumerate(z_shelves):
                make_box(f"Case_{side}{b}_S{zi}", (wx, cy, z), (0.32, y1 - y0 - 0.08, 0.035),
                         COL_CASE_LT)
                # books on every shelf except the very top of some bays
                if zi < 5 or (b + zi) % 2 == 0:
                    _book_run(f"Books_{side}{b}_{zi}", wx, y0 + 0.08, y1 - 0.08,
                              z + 0.02, seed=b * 6 + zi + (0 if side == "W" else 3))
    # Borges sign — back-left bay, third shelf down (canon)
    make_box("Borges_Sign", (-ROOM_W / 2.0 + 0.40, ROOM_D - 1.2, 1.98),
             (0.02, 0.34, 0.10), COL_SIGN)
    # North wall case (behind the back of the shop) — solid books
    make_box("Case_N_Back", (0.0, ROOM_D - 0.10, 1.45), (ROOM_W - 0.5, 0.04, 2.9), COL_CASE)
    for zi, z in enumerate([0.25, 0.72, 1.19, 1.66, 2.13, 2.60]):
        make_box(f"Case_N_S{zi}", (0.0, ROOM_D - 0.28, z), (ROOM_W - 0.6, 0.32, 0.035),
                 COL_CASE_LT)
        _book_run(f"Books_N_{zi}", ROOM_D - 0.28, -ROOM_W / 2.0 + 0.4,
                  ROOM_W / 2.0 - 0.4, z + 0.02, axis='X', seed=20 + zi)


def build_counter():
    """Hal's counter on the east side, mid-shop: register, book stacks,
    the reading lamp, his stool behind."""
    cx, cy = 1.35, 1.9
    make_box("Counter_Top", (cx, cy, 0.98), (1.3, 0.7, 0.06), COL_COUNTER)
    make_box("Counter_Front", (cx - 0.62, cy, 0.48), (0.05, 0.7, 0.96), COL_CASE)
    make_box("Counter_Side_S", (cx, cy - 0.33, 0.48), (1.25, 0.05, 0.96), COL_CASE)
    make_box("Counter_Side_N", (cx, cy + 0.33, 0.48), (1.25, 0.05, 0.96), COL_CASE)
    # Register — old mechanical, brass-toned
    make_box("Register", (cx + 0.25, cy - 0.05, 1.16), (0.36, 0.30, 0.28), COL_FRAME)
    make_box("Register_Keys", (cx + 0.18, cy - 0.12, 1.28), (0.20, 0.14, 0.05), COL_BRASS)
    # Stacks of books being priced
    for b in range(5):
        k = (b * 7 + 2) % len(SPINES)
        make_box(f"CounterStack_{b}", (cx - 0.25, cy + 0.18, 1.03 + b * 0.045),
                 (0.26, 0.20, 0.042), SPINES[k])
    # Hal's open hardcover, face-down on the counter
    make_box("Hal_Book", (cx - 0.05, cy - 0.18, 1.02), (0.22, 0.16, 0.03),
             (0.50, 0.30, 0.30, 1.0))
    # Brass reading lamp with a green shade
    make_cyl("CLamp_Post", (cx + 0.48, cy + 0.20, 1.14), 0.015, 0.28, COL_BRASS, segments=6)
    make_box("CLamp_Shade", (cx + 0.42, cy + 0.20, 1.30), (0.24, 0.14, 0.09), COL_SHADE)
    make_box("CLamp_Bulb", (cx + 0.42, cy + 0.20, 1.26), (0.16, 0.08, 0.02), COL_LAMP)
    # Stool behind the counter (east)
    make_cyl("Stool_Seat", (cx + 0.45, cy + 0.62, 0.62), 0.17, 0.05, COL_CASE_LT, segments=10)
    for li in range(3):
        ang = li * 2.09
        make_cyl(f"Stool_Leg_{li}", (cx + 0.45 + 0.11 * math.cos(ang),
                 cy + 0.62 + 0.11 * math.sin(ang), 0.30), 0.015, 0.60, COL_FRAME, segments=5)


def build_center_tables():
    """Two low display tables forming the aisle's east edge, stacked
    with face-up books; plus the rolling ladder and a box of unsorted
    paperbacks on the floor."""
    for ti, ty in enumerate((3.9, 6.1)):
        make_box(f"Table_{ti}_Top", (0.75, ty, 0.72), (0.9, 1.4, 0.05), COL_CASE_LT)
        for lx, ly in ((0.4, ty - 0.6), (1.1, ty - 0.6), (0.4, ty + 0.6), (1.1, ty + 0.6)):
            make_box(f"Table_{ti}_Leg_{lx:.1f}_{ly:.1f}", (lx, ly, 0.36),
                     (0.05, 0.05, 0.72), COL_CASE)
        # face-up books in loose rows
        for r in range(3):
            for c in range(4):
                k = (ti * 11 + r * 5 + c * 3) % len(SPINES)
                make_box(f"Table_{ti}_Bk_{r}_{c}",
                         (0.45 + c * 0.21, ty - 0.5 + r * 0.5 + 0.03 * ((c + r) % 2),
                          0.77 + 0.012 * ((c * 3 + r) % 2)),
                         (0.17, 0.24, 0.025), SPINES[k])
    # Rolling ladder leaning on the west cases
    make_box("Ladder_Rail_L", (-1.72, 5.6, 1.45), (0.05, 0.05, 2.75), COL_CASE)
    make_box("Ladder_Rail_R", (-1.72, 6.0, 1.45), (0.05, 0.05, 2.75), COL_CASE)
    for s in range(7):
        make_box(f"Ladder_Rung_{s}", (-1.72, 5.8, 0.35 + s * 0.38), (0.04, 0.42, 0.04),
                 COL_CASE_LT)
    make_cyl("Ladder_Brass_Rail", (-1.55, 4.9, 2.95), 0.02, 3.4, COL_BRASS,
             segments=6, axis='Y')
    # Box of unsorted paperbacks by the counter
    make_box("SortBox", (0.45, 1.1, 0.16), (0.42, 0.34, 0.30), (0.52, 0.40, 0.26, 1.0),
             open_faces={"+Z"})
    for b in range(6):
        k = (b * 5 + 1) % len(SPINES)
        make_box(f"SortBox_Bk_{b}", (0.34 + 0.07 * (b % 3), 1.05 + 0.05 * (b % 2),
                 0.20 + b * 0.03), (0.18, 0.13, 0.028), SPINES[k])


def build_pendants():
    """Three pendant lamps down the aisle — the practicals the tscn
    Omnis sit on. Warm bulbs under green metal shades."""
    for pi, py in enumerate((2.2, 4.6, 7.0)):
        make_box(f"Pendant_{pi}_Cord", (-0.35, py, CEIL - 0.28), (0.02, 0.02, 0.56), COL_FRAME)
        make_cyl(f"Pendant_{pi}_Shade", (-0.35, py, CEIL - 0.62), 0.17, 0.14, COL_SHADE,
                 segments=12)
        make_cyl(f"Pendant_{pi}_Bulb", (-0.35, py, CEIL - 0.70), 0.055, 0.08, COL_LAMP,
                 segments=8)


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_wall_cases()
    build_counter()
    build_center_tables()
    build_pendants()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/bindery.glb"))
    print(f"\n[build_bindery] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
