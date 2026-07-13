"""salty_tome_interior — vol5-7 locale. THE SALTY TOME, a cramped
second-hand bookshop: floor-to-ceiling shelves packed spine-out, a
double-sided center gondola, a sales counter with an antique register
and stacked books, a reading nook (wing armchair + floor lamp + side
table on a rug), a rolling library ladder, a globe on a stand, a card
catalog, a hanging shop sign, and a front window. Warm tungsten light.

Rebuilt 2026-07-13 from the bare auto-generated template (which
shipped only two floor bins + a register counter + filing cabinets —
a stockroom mislabelled as a bookshop).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_register
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent
from _props.signage import make_hanging_banner

ROOM_W = 8.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall": (0.80, 0.72, 0.58, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.52, 0.40, 0.28, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0)
COL_WOOD = (0.42, 0.30, 0.20, 1.0); COL_WOOD_DK = (0.30, 0.20, 0.12, 1.0)
COL_LEATHER = (0.46, 0.28, 0.20, 1.0); COL_BRASS = (0.78, 0.62, 0.30, 1.0)
COL_GLASS = (0.78, 0.84, 0.86, 0.45); COL_LAMP = (0.98, 0.82, 0.52, 1.0)
COL_TEAL = (0.16, 0.34, 0.34, 1.0); COL_RUG = (0.52, 0.24, 0.20, 1.0)
COL_RUG_BORDER = (0.34, 0.16, 0.14, 1.0); COL_BLACK = (0.14, 0.12, 0.12, 1.0)

BOOK_SPINES = [(0.42, 0.16, 0.14, 1.0), (0.20, 0.30, 0.22, 1.0), (0.16, 0.22, 0.38, 1.0),
               (0.62, 0.50, 0.28, 1.0), (0.58, 0.44, 0.16, 1.0), (0.36, 0.20, 0.28, 1.0),
               (0.28, 0.34, 0.36, 1.0), (0.48, 0.34, 0.18, 1.0)]
BOOK_W = [0.05, 0.07, 0.045, 0.06, 0.055, 0.08, 0.05, 0.065]
BOOK_HF = [0.86, 0.78, 0.92, 0.72, 0.88, 0.80, 0.90, 0.76]


def make_bookshelf(prefix, anchor, *, run_len=4.0, height=2.2, depth=0.32,
                   shelves=5, axis='X', front_sign=-1, wood=COL_WOOD):
    """Wall bookcase packed spine-out. axis='X' runs E-W (books face
    ±Y per front_sign); axis='Y' runs N-S (books face ±X). anchor is
    the unit center at floor level (cx, cy, 0.0)."""
    cx, cy, bz = anchor
    shelf_gap = (height - 0.18) / shelves
    if axis == 'X':
        for sgn in (-1, +1):
            make_box(f"{prefix}_Post_{sgn:+d}", (cx + sgn*run_len/2.0, cy, bz+height/2.0),
                     (0.06, depth, height), wood)
        make_box(f"{prefix}_Top", (cx, cy, bz+height), (run_len, depth, 0.06), wood)
        make_box(f"{prefix}_Back", (cx, cy - front_sign*depth/2.0, bz+height/2.0),
                 (run_len, 0.02, height), wood)
        for sh in range(shelves):
            sz = bz + 0.10 + sh*shelf_gap
            make_box(f"{prefix}_Shelf_{sh}", (cx, cy, sz), (run_len-0.08, depth, 0.03), wood)
            n = int((run_len - 0.16) / 0.072)
            x = cx - run_len/2.0 + 0.10
            for bi in range(n):
                w = BOOK_W[(sh+bi) % len(BOOK_W)]
                if x + w > cx + run_len/2.0 - 0.10:
                    break
                bh = shelf_gap * BOOK_HF[(sh*2+bi) % len(BOOK_HF)]
                col = BOOK_SPINES[(sh*3+bi) % len(BOOK_SPINES)]
                make_box(f"{prefix}_Book_{sh}_{bi}",
                         (x + w/2.0, cy + front_sign*(depth*0.12), sz + 0.03 + bh/2.0),
                         (w, depth*0.72, bh), col)
                x += w + 0.006
    else:  # axis == 'Y'
        for sgn in (-1, +1):
            make_box(f"{prefix}_Post_{sgn:+d}", (cx, cy + sgn*run_len/2.0, bz+height/2.0),
                     (depth, 0.06, height), wood)
        make_box(f"{prefix}_Top", (cx, cy, bz+height), (depth, run_len, 0.06), wood)
        make_box(f"{prefix}_Back", (cx - front_sign*depth/2.0, cy, bz+height/2.0),
                 (0.02, run_len, height), wood)
        for sh in range(shelves):
            sz = bz + 0.10 + sh*shelf_gap
            make_box(f"{prefix}_Shelf_{sh}", (cx, cy, sz), (depth, run_len-0.08, 0.03), wood)
            n = int((run_len - 0.16) / 0.072)
            y = cy - run_len/2.0 + 0.10
            for bi in range(n):
                w = BOOK_W[(sh+bi) % len(BOOK_W)]
                if y + w > cy + run_len/2.0 - 0.10:
                    break
                bh = shelf_gap * BOOK_HF[(sh*2+bi) % len(BOOK_HF)]
                col = BOOK_SPINES[(sh*3+bi) % len(BOOK_SPINES)]
                make_box(f"{prefix}_Book_{sh}_{bi}",
                         (cx + front_sign*(depth*0.12), y + w/2.0, sz + 0.03 + bh/2.0),
                         (depth*0.72, w, bh), col)
                y += w + 0.006


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.5, 0.0, 0), length=3.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+2.5, 0.0, 0), length=3.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
                                    ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
                                    ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD_DK})


def build_bookshelves():
    # N wall (E-W run, books face S)
    make_bookshelf("Shelf_N", (-0.6, ROOM_D-0.22, 0.0), run_len=5.6, height=2.4,
                   axis='X', front_sign=-1)
    # W wall (N-S run, books face E)
    make_bookshelf("Shelf_W", (-ROOM_W/2.0+0.22, 3.4, 0.0), run_len=3.6, height=2.4,
                   axis='Y', front_sign=+1)
    # E wall, north portion (N-S run, books face W) — S portion left for counter
    make_bookshelf("Shelf_E", (+ROOM_W/2.0-0.22, 4.6, 0.0), run_len=2.2, height=2.4,
                   axis='Y', front_sign=-1)
    # Double-sided center gondola (two back-to-back E-W units)
    make_bookshelf("Gondola_S", (-0.4, 2.95, 0.0), run_len=3.4, height=1.7,
                   axis='X', front_sign=-1)
    make_bookshelf("Gondola_N", (-0.4, 3.25, 0.0), run_len=3.4, height=1.7,
                   axis='X', front_sign=+1)


def build_rolling_ladder():
    # Rolling library ladder leaning on the N shelf
    lx, ly = -2.4, ROOM_D - 0.55
    for sgn in (-1, +1):
        make_box(f"Ladder_Rail_{sgn:+d}", (lx + sgn*0.16, ly, 1.25), (0.05, 0.05, 2.50), COL_WOOD_DK)
    for ri in range(6):
        make_cyl(f"Ladder_Rung_{ri}", (lx, ly, 0.30 + ri*0.42), 0.022, 0.32, COL_WOOD_DK, axis='X', segments=6)
    make_box("Ladder_TopHook", (lx, ly + 0.16, 2.45), (0.40, 0.30, 0.05), COL_BRASS)
    for sgn in (-1, +1):
        make_cyl(f"Ladder_Wheel_{sgn:+d}", (lx + sgn*0.16, ly - 0.08, 0.10), 0.06, 0.04,
                 COL_BLACK, axis='X', segments=10)


def build_sales_counter():
    cx, cy = +ROOM_W/2.0 - 1.4, 2.6
    top_z = make_counter("Counter", (cx, cy, 0.0), length=2.60, depth=0.70, height=0.95,
                         palette={"formica": COL_WOOD, "top": COL_WOOD_DK, "kick": COL_WOOD_DK})
    make_register("Register", (cx, cy + 0.70, top_z),
                  palette={"body": COL_BRASS, "keys": COL_WOOD_DK, "screen": (0.30, 0.22, 0.14, 1.0)})
    # Stacked books to be shelved + a service bell + a banker's lamp
    for si in range(4):
        make_box(f"CounterStack_{si}", (cx - 0.05, cy - 0.60, top_z + 0.03 + si*0.055),
                 (0.34, 0.24, 0.05), BOOK_SPINES[si % len(BOOK_SPINES)])
    make_cyl("CounterBell", (cx - 0.10, cy - 1.00, top_z + 0.04), 0.05, 0.05, COL_BRASS, segments=12)
    # Green banker's lamp
    make_cyl("DeskLamp_Base", (cx + 0.05, cy + 1.05, top_z + 0.03), 0.06, 0.04, COL_BRASS, segments=10)
    make_cyl("DeskLamp_Stem", (cx + 0.05, cy + 1.05, top_z + 0.14), 0.012, 0.20, COL_BRASS)
    make_box("DeskLamp_Shade", (cx + 0.05, cy + 1.05, top_z + 0.26), (0.26, 0.12, 0.06), COL_TEAL)
    make_box("DeskLamp_Glow", (cx + 0.05, cy + 1.05, top_z + 0.22), (0.22, 0.10, 0.02), COL_LAMP)


def build_reading_nook():
    nx, ny = -ROOM_W/2.0 + 1.1, 1.3
    # Rug
    make_box("Rug", (nx, ny, 0.006), (2.0, 2.0, 0.006), COL_RUG)
    make_box("Rug_Border", (nx, ny, 0.007), (1.7, 1.7, 0.004), COL_RUG_BORDER)
    # Wing armchair (facing E, into the room)
    ax, ay = nx - 0.1, ny
    make_box("Chair_Seat", (ax, ay, 0.40), (0.62, 0.60, 0.14), COL_LEATHER)
    make_box("Chair_Cushion", (ax, ay, 0.50), (0.54, 0.52, 0.10), COL_LEATHER)
    make_box("Chair_Back", (ax - 0.28, ay, 0.72), (0.12, 0.60, 0.62), COL_LEATHER)
    for sgn in (-1, +1):
        make_box(f"Chair_Arm_{sgn:+d}", (ax - 0.02, ay + sgn*0.32, 0.54), (0.44, 0.12, 0.22), COL_LEATHER)
        make_box(f"Chair_Wing_{sgn:+d}", (ax - 0.24, ay + sgn*0.30, 0.80), (0.14, 0.10, 0.30), COL_LEATHER)
    for lx, ly in [(-0.24, -0.24), (0.24, -0.24), (-0.24, 0.24), (0.24, 0.24)]:
        make_box(f"Chair_Leg_{lx:+.0f}_{ly:+.0f}", (ax + lx, ay + ly, 0.16), (0.06, 0.06, 0.32), COL_WOOD_DK)
    # Floor lamp beside the chair
    fx, fy = nx + 0.7, ny + 0.6
    make_cyl("FloorLamp_Base", (fx, fy, 0.03), 0.16, 0.05, COL_WOOD_DK, segments=12)
    make_cyl("FloorLamp_Pole", (fx, fy, 0.85), 0.02, 1.60, COL_BRASS)
    make_cyl("FloorLamp_Shade", (fx, fy, 1.66), 0.20, 0.24, (0.86, 0.74, 0.52, 1.0), segments=12)
    make_cyl("FloorLamp_Bulb", (fx, fy, 1.60), 0.06, 0.06, COL_LAMP, segments=8)
    # Side table with a book + a teacup
    tx, ty = nx + 0.5, ny - 0.5
    make_cyl("SideTable_Top", (tx, ty, 0.52), 0.26, 0.04, COL_WOOD, segments=14)
    make_cyl("SideTable_Post", (tx, ty, 0.27), 0.03, 0.50, COL_WOOD_DK)
    for sgn in (-1, +1):
        make_box(f"SideTable_Foot_{sgn:+d}", (tx + sgn*0.16, ty, 0.03), (0.30, 0.05, 0.04), COL_WOOD_DK)
    make_box("SideTable_Book", (tx, ty, 0.57), (0.20, 0.15, 0.04), BOOK_SPINES[2])
    make_cyl("SideTable_Cup", (tx + 0.10, ty + 0.08, 0.58), 0.04, 0.06, (0.90, 0.88, 0.82, 1.0), segments=10)


def build_globe_and_catalog():
    # Globe on a wooden tripod stand
    gx, gy = +0.8, 1.2
    for ai in range(3):
        ang = ai * (2.0*math.pi/3.0)
        make_box(f"Globe_Leg_{ai}", (gx + math.cos(ang)*0.16, gy + math.sin(ang)*0.16, 0.35),
                 (0.04, 0.04, 0.70), COL_WOOD_DK)
    make_cyl("Globe_Ring", (gx, gy, 0.86), 0.20, 0.02, COL_BRASS, axis='X', segments=16)
    for zi, r in enumerate([0.09, 0.13, 0.15, 0.15, 0.13, 0.09]):
        make_cyl(f"Globe_Sphere_{zi}", (gx, gy, 0.74 + zi*0.058), r, 0.058,
                 (0.36, 0.48, 0.56, 1.0), segments=14)
    # Card catalog cabinet near the counter
    cx, cy = +2.2, 1.1
    make_box("Catalog_Body", (cx, cy, 0.55), (0.90, 0.50, 1.10), COL_WOOD)
    make_box("Catalog_Top", (cx, cy, 1.12), (0.96, 0.56, 0.04), COL_WOOD_DK)
    for r in range(5):
        for c in range(3):
            dz = 0.20 + r*0.18
            dx = cx - 0.28 + c*0.28
            make_box(f"Catalog_Drawer_{r}_{c}", (dx, cy - 0.24, dz), (0.24, 0.02, 0.14), COL_WOOD_DK)
            make_box(f"Catalog_Label_{r}_{c}", (dx, cy - 0.252, dz + 0.02), (0.12, 0.005, 0.04), P.PAPER)
            make_cyl(f"Catalog_Pull_{r}_{c}", (dx, cy - 0.26, dz - 0.03), 0.012, 0.02, COL_BRASS, axis='Y', segments=6)


def build_ceiling_and_sign():
    for pi, px in enumerate([-2.4, 0.0, +2.4]):
        make_cyl(f"Pendant_Cord_{pi}", (px, 3.0, CEIL-0.30), 0.01, 0.50, COL_BLACK)
        make_cyl(f"Pendant_Shade_{pi}", (px, 3.0, CEIL-0.60), 0.14, 0.14, COL_BRASS, segments=12)
        make_cyl(f"Pendant_Bulb_{pi}", (px, 3.0, CEIL-0.70), 0.05, 0.06, COL_LAMP, segments=8)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("Vent", (+2.0, 4.8, CEIL), width=1.00, depth=0.50, slats=5)
    # Hanging "THE SALTY TOME" shop sign near the entrance
    make_hanging_banner("SaltyTomeSign", (0.0, 1.4, CEIL), width=1.90, height=0.40,
                        bg_color=COL_TEAL, text_color=COL_BRASS)


def build_decor():
    make_wall_clock("Clock", (+ROOM_W/2.0-0.05, 1.2, 2.10), frozen_hour=5, frozen_min=10)
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 5.4, 2.05))
    make_faded_poster("Poster", (+ROOM_W/2.0-0.05, 5.6, 1.70))
    make_floor_plant("Plant", (+ROOM_W/2.0-0.40, 0.55, 0.0),
                     palette={"leaf": (0.36, 0.46, 0.32, 1.0)})
    # Front window on the S-W wall segment
    make_window("Window_Front", (-2.5, 0.0, 1.55), width=2.4, height=1.30)


def main():
    clear_scene()
    build_shell()
    build_bookshelves()
    build_rolling_ladder()
    build_sales_counter()
    build_reading_nook()
    build_globe_and_catalog()
    build_ceiling_and_sign()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/salty_tome_interior.glb"))
    print(f"\n[build_salty_tome_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
