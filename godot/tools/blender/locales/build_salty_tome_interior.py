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
from _props.detail import (make_traffic_wear, make_floor_stain, make_scuff_band,
                           make_wall_tint_band, make_threshold, make_wall_outlet,
                           make_light_switch, make_cord_run)

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
    # N wall split for the doorway into the back annex (x 2.4..3.4).
    make_wall("Wall_N_W", (-0.9, ROOM_D, 0), length=6.6, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (3.8, ROOM_D, 0), length=0.8, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveDoor", (2.9, ROOM_D, CEIL-0.30), (1.0, 0.20, 0.60), PAL_WALL["wall"])
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


def build_back_annex_2026_08():
    """2026-08-03 tail pass — the back of the store the vol7 scenes
    live in: the KITCHENETTE (Petra's kettle, the clay mug from
    Margit's, four mugs, the table by the kitchenette window, the
    radiator, the cat asleep on its chair), Petra's BACK OFFICE
    behind its closed door (desk + phone + couch + coat hook), the
    BACK DOOR Lena unlocks from the alley — and the alley itself:
    dumpster, and the MURAL WALL with the painted face (ch14)."""
    AN_Y0, AN_Y1 = ROOM_D, 9.0
    # Annex floor + side walls + far (alley-side) wall with window
    # + back door.
    make_floor("Annex_Floor", (0.0, (AN_Y0+AN_Y1)/2.0, 0.0), size_x=ROOM_W+0.4, size_y=AN_Y1-AN_Y0,
               palette={"vinyl": (0.56, 0.46, 0.34, 1.0), "seam": COL_SEAM})
    for nm, x, bb in [("Annex_Wall_W", -ROOM_W/2.0, +1), ("Annex_Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, (AN_Y0+AN_Y1)/2.0, 0), length=AN_Y1-AN_Y0, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # Alley-side wall: back door at x=-3.3, kitchenette window at x=-1.6.
    make_wall("Annex_Wall_N_Wd", (-2.45, AN_Y1, 0), length=0.7, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Annex_Wall_N_Mid", (0.35, AN_Y1, 0), length=2.5, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Annex_Wall_N_E", (2.9, AN_Y1, 0), length=2.6, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Annex_AboveBackDoor", (-3.3, AN_Y1, CEIL-0.30), (1.0, 0.20, 0.60), PAL_WALL["wall"])
    make_window("Kitchenette_Window", (-1.6, AN_Y1-0.10, 1.55), width=1.10, height=1.15)
    make_box("Annex_AboveKWin", (-1.6, AN_Y1, CEIL-0.25), (1.2, 0.20, 0.50), PAL_WALL["wall"])
    make_ceiling("Annex_Ceil", (0.0, (AN_Y0+AN_Y1)/2.0, CEIL), size_x=ROOM_W+0.4, size_y=AN_Y1-AN_Y0)
    # The BACK DOOR (Lena's morning key) — mostly closed leaf.
    make_box("Back_Door", (-3.3, AN_Y1-0.06, 1.05), (0.95, 0.06, 2.10), (0.36, 0.28, 0.20, 1.0))
    make_cyl("Back_Door_Knob", (-3.0, AN_Y1-0.12, 1.02), 0.03, 0.04, COL_BRASS, segments=8)
    # Office partition at x=0.9: Petra behind the closed door.
    make_wall("Office_Part", (0.9, (AN_Y0+AN_Y1)/2.0, 0), length=AN_Y1-AN_Y0, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Office_Door", (0.84, AN_Y0+0.85, 1.05), (0.06, 0.90, 2.10), (0.42, 0.32, 0.22, 1.0))
    make_cyl("Office_Door_Knob", (0.78, AN_Y0+0.55, 1.02), 0.03, 0.04, COL_BRASS, segments=8)
    make_box("Office_Coat_Hook", (0.96, AN_Y0+1.9, 1.70), (0.05, 0.04, 0.05), COL_BRASS)
    make_box("Office_Coat", (1.00, AN_Y0+1.9, 1.25), (0.06, 0.38, 0.90), (0.30, 0.32, 0.38, 1.0))
    # Office: desk + phone + the couch.
    make_box("Office_Desk_Top", (2.7, 8.35, 0.74), (1.60, 0.70, 0.04), COL_WOOD)
    for oi, oxo in enumerate([-0.72, 0.72]):
        make_box(f"Office_Desk_Side_{oi}", (2.7+oxo, 8.35, 0.37), (0.06, 0.66, 0.72), COL_WOOD)
    make_box("Office_Phone_Base", (2.35, 8.30, 0.78), (0.20, 0.14, 0.07), COL_BLACK)
    make_box("Office_Phone_Handset", (2.35, 8.30, 0.85), (0.22, 0.06, 0.04), COL_BLACK)
    for pi2 in range(3):
        make_box(f"Office_Papers_{pi2}", (3.0-pi2*0.05, 8.32, 0.765+pi2*0.008), (0.22, 0.28, 0.008),
                 (0.90, 0.88, 0.82, 1.0))
    make_box("Office_Couch_Base", (2.9, 6.85, 0.26), (1.70, 0.70, 0.34), (0.40, 0.30, 0.26, 1.0))
    make_box("Office_Couch_Back", (2.9, 7.16, 0.60), (1.70, 0.16, 0.55), (0.40, 0.30, 0.26, 1.0))
    for ci2, cxo in enumerate([-0.55, 0.0, 0.55]):
        make_box(f"Office_Couch_Cushion_{ci2}", (2.9+cxo, 6.80, 0.45), (0.52, 0.60, 0.10),
                 (0.46, 0.35, 0.30, 1.0))
    # KITCHENETTE along the annex W + N walls.
    make_box("Kitch_Counter", (-3.55, 7.4, 0.45), (0.60, 1.8, 0.90), COL_WOOD)
    make_box("Kitch_Counter_Top", (-3.55, 7.4, 0.92), (0.66, 1.9, 0.05), (0.72, 0.68, 0.60, 1.0))
    make_box("Kitch_Sink", (-3.55, 7.0, 0.93), (0.40, 0.34, 0.03), (0.60, 0.62, 0.64, 1.0))
    make_cyl("Kitch_Faucet", (-3.72, 7.0, 1.05), 0.015, 0.20, (0.62, 0.64, 0.66, 1.0), segments=6)
    # Petra's KETTLE on a two-ring hob.
    make_box("Kitch_Hob", (-3.55, 7.85, 0.95), (0.44, 0.36, 0.04), COL_BLACK)
    make_cyl("Kettle_Body", (-3.55, 7.85, 1.06), 0.11, 0.16, (0.74, 0.76, 0.78, 1.0), segments=12)
    make_cyl("Kettle_Lid", (-3.55, 7.85, 1.16), 0.05, 0.04, (0.66, 0.68, 0.70, 1.0), segments=10)
    make_box("Kettle_Handle", (-3.55, 7.85, 1.22), (0.16, 0.03, 0.03), COL_BLACK)
    # Four mugs set out + the small clay mug from Margit's (2009).
    for mi in range(4):
        make_cyl(f"Mug_{mi}", (-3.40+0.14*(mi%2), 6.55+0.16*(mi//2), 0.99), 0.04, 0.09,
                 [(0.80, 0.78, 0.72, 1.0), (0.46, 0.56, 0.58, 1.0),
                  (0.62, 0.48, 0.36, 1.0), (0.70, 0.70, 0.66, 1.0)][mi], segments=8)
    make_cyl("Clay_Mug_Margits", (-3.62, 6.70, 1.00), 0.045, 0.10, (0.58, 0.38, 0.26, 1.0), segments=8)
    # The table by the kitchenette window + three chairs (Lena and
    # Cale sit, Kai stands by the door).
    make_box("Kitch_Table_Top", (-1.6, 8.1, 0.74), (0.95, 0.85, 0.04), COL_WOOD)
    for li3, (lxo, lyo) in enumerate([(-0.40, -0.35), (0.40, -0.35), (-0.40, 0.35), (0.40, 0.35)]):
        make_box(f"Kitch_Table_Leg_{li3}", (-1.6+lxo, 8.1+lyo, 0.36), (0.05, 0.05, 0.72), COL_WOOD_DK)
    for ci3, (cxo, cyo, bxo) in enumerate([(-0.75, 0.0, -0.20), (0.75, 0.0, 0.20), (0.0, -0.75, 0.0)]):
        make_box(f"Kitch_Chair_{ci3}_Seat", (-1.6+cxo, 8.1+cyo, 0.45), (0.42, 0.42, 0.05), COL_WOOD)
        if ci3 < 2:
            make_box(f"Kitch_Chair_{ci3}_Back", (-1.6+cxo+bxo, 8.1+cyo, 0.75), (0.05, 0.42, 0.55), COL_WOOD)
        else:
            make_box(f"Kitch_Chair_{ci3}_Back", (-1.6+cxo, 8.1+cyo-0.20, 0.75), (0.42, 0.05, 0.55), COL_WOOD)
    # Radiator under the kitchenette window.
    for ri2 in range(6):
        make_box(f"Radiator_Fin_{ri2}", (-2.05+ri2*0.18, AN_Y1-0.22, 0.42), (0.10, 0.16, 0.60),
                 (0.72, 0.70, 0.66, 1.0))
    make_box("Radiator_Top", (-1.6, AN_Y1-0.22, 0.74), (1.10, 0.18, 0.04), (0.66, 0.64, 0.60, 1.0))
    # The CAT — Petra's old cat, asleep in a loaf on its own chair.
    make_box("Cat_Chair_Seat", (-0.5, 6.7, 0.42), (0.44, 0.44, 0.05), COL_WOOD)
    make_box("Cat_Chair_Back", (-0.28, 6.7, 0.72), (0.05, 0.44, 0.52), COL_WOOD)
    make_box("Cat_Cushion", (-0.5, 6.7, 0.47), (0.38, 0.38, 0.06), (0.52, 0.30, 0.26, 1.0))
    make_box("Cat_Loaf_Body", (-0.5, 6.7, 0.56), (0.30, 0.20, 0.13), (0.28, 0.26, 0.24, 1.0))
    make_box("Cat_Loaf_Head", (-0.36, 6.74, 0.60), (0.11, 0.11, 0.09), (0.30, 0.28, 0.26, 1.0))
    for ei2, eyo in enumerate([-0.035, 0.035]):
        make_box(f"Cat_Ear_{ei2}", (-0.33, 6.74+eyo, 0.66), (0.03, 0.025, 0.03), (0.26, 0.24, 0.22, 1.0))


def build_alley_2026_08():
    """The alley behind the store: asphalt, the dumpster Petra reads
    beside, and the MURAL WALL with the three-foot painted face
    (vol7_ch14_figure)."""
    AL_Y0, AL_Y1 = 9.0, 12.0
    make_box("Alley_Asphalt", (0.0, (AL_Y0+AL_Y1)/2.0, -0.02), (ROOM_W+3.0, AL_Y1-AL_Y0, 0.04),
             (0.30, 0.30, 0.32, 1.0))
    # The mural wall — the facing building's brick flank.
    make_box("Mural_Wall", (0.0, AL_Y1, 1.60), (ROOM_W+3.0, 0.24, 3.60), (0.46, 0.30, 0.24, 1.0))
    # The FACE: ~0.9m across at head height, hair falling to waist
    # height (stacked paint planes proud of the brick).
    fx = -0.8
    for zi2, (r, col) in enumerate([(0.18, (0.78, 0.62, 0.50, 1.0)), (0.32, (0.80, 0.64, 0.52, 1.0)),
                                    (0.42, (0.82, 0.66, 0.54, 1.0)), (0.45, (0.82, 0.66, 0.54, 1.0)),
                                    (0.42, (0.80, 0.64, 0.52, 1.0)), (0.30, (0.78, 0.62, 0.50, 1.0))]):
        make_box(f"Face_Band_{zi2}", (fx, AL_Y1-0.13, 2.30-zi2*0.18), (r*2.0, 0.02, 0.18), col)
    for ei3, exo in enumerate([-0.18, 0.18]):
        make_box(f"Face_Eye_{ei3}", (fx+exo, AL_Y1-0.145, 2.12), (0.10, 0.015, 0.05),
                 (0.20, 0.22, 0.26, 1.0))
    make_box("Face_Mouth", (fx, AL_Y1-0.145, 1.72), (0.16, 0.015, 0.035), (0.52, 0.30, 0.28, 1.0))
    # Hair: dark sheets from crown to waist height either side.
    for hi, (hxo, hw, hz, hh) in enumerate([(-0.55, 0.35, 1.65, 1.70), (0.55, 0.35, 1.65, 1.70),
                                            (0.0, 1.15, 2.48, 0.30)]):
        make_box(f"Face_Hair_{hi}", (fx+hxo, AL_Y1-0.14, hz), (hw, 0.02, hh), (0.16, 0.14, 0.16, 1.0))
    # The dumpster ("by my reading at the dumpster").
    make_box("Dumpster_Body", (2.4, 10.2, 0.65), (1.90, 1.00, 1.10), (0.20, 0.34, 0.28, 1.0))
    make_box("Dumpster_Lid", (2.4, 10.45, 1.24), (1.92, 0.55, 0.06), (0.16, 0.28, 0.23, 1.0))
    make_box("Dumpster_Lid_Open", (2.4, 9.85, 1.45), (1.92, 0.06, 0.55), (0.16, 0.28, 0.23, 1.0))
    for wi2, wxo in enumerate([-0.75, 0.75]):
        make_cyl(f"Dumpster_Wheel_{wi2}", (2.4+wxo, 10.2, 0.08), 0.07, 0.05, COL_BLACK,
                 axis='X', segments=8)
    # A milk crate reading-perch and a downspout for texture.
    make_box("Alley_Crate", (1.1, 10.6, 0.16), (0.35, 0.35, 0.32), (0.55, 0.45, 0.30, 1.0))
    make_cyl("Downspout", (-3.9, 9.15, 1.40), 0.05, 2.80, (0.44, 0.44, 0.46, 1.0), segments=8)


def build_detail_pass_2026_08():
    """D2 surface breakup + a first D3 taste (set-detail playbook).
    Forty-one years of Petra: the shop's wear is deep and settled —
    the aisle path is nearly a groove, the kitchenette has poured
    ten thousand kettles, the alley is honest about the dumpster.
    D4 (use states) next."""
    wear = (0.46, 0.35, 0.24, 1.0)
    # The aisle groove: door -> counter -> the N doorway -> annex.
    make_traffic_wear("Wear_Aisle", [(0.0, 0.6), (0.0, 2.6), (2.0, 2.6)],
                      width=0.75, tint=wear)
    make_traffic_wear("Wear_ToBack", [(2.9, 3.4), (2.9, 6.6)],
                      width=0.65, tint=wear)
    # Kitchenette path: back door -> kettle -> the window table; and
    # the cat chair's patch (he is walked around, never moved).
    make_traffic_wear("Wear_Kitch", [(-3.3, 8.4), (-3.3, 7.4), (-1.9, 7.4)],
                      width=0.6, tint=(0.50, 0.41, 0.30, 1.0))
    make_floor_stain("Stain_Kettle", (-3.5, 7.85, ), radius=0.22,
                     tint=(0.48, 0.39, 0.28, 1.0))
    make_floor_stain("Stain_CatChair", (-0.5, 6.7), radius=0.40,
                     tint=(0.50, 0.42, 0.32, 1.0))
    # Reading-nook rug shadow (the rug has not moved since 2015).
    make_floor_stain("Stain_NookEdge", (-2.6, 1.3), radius=0.30, tint=wear)
    # Kick scuffs: sales counter + the back door's boot line.
    make_scuff_band("Scuff_Counter", (ROOM_W/2.0-1.4, 2.24), length=2.5, axis='X',
                    band_z=0.11, tint=(0.28, 0.20, 0.13, 1.0))
    make_scuff_band("Scuff_BackDoor", (-3.3, 8.90), length=0.9, axis='X',
                    band_z=0.09, tint=(0.26, 0.20, 0.14, 1.0))
    # Ceiling gather over the tall shelf walls.
    make_wall_tint_band("Band_W", (-ROOM_W/2.0+0.105, 3.0, 0.0), length=5.4,
                        axis='Y', band_z=CEIL-0.16, tint=(0.72, 0.64, 0.50, 1.0))
    make_wall_tint_band("Band_E", (ROOM_W/2.0-0.105, 3.0, 0.0), length=5.4,
                        axis='Y', band_z=CEIL-0.16, tint=(0.72, 0.64, 0.50, 1.0))
    # Thresholds at every door the scenes use.
    make_threshold("Threshold_Front", (0.0, 0.10), width=1.9, axis='X',
                   tint=(0.46, 0.32, 0.20, 1.0))
    make_threshold("Threshold_Annex", (2.9, ROOM_D), width=1.0, axis='X',
                   tint=(0.46, 0.32, 0.20, 1.0))
    make_threshold("Threshold_Back", (-3.3, 9.0), width=0.95, axis='X',
                   tint=(0.46, 0.32, 0.20, 1.0))
    # First infrastructure: switch by the door, the kitchenette
    # outlet the kettle cord actually reaches.
    make_light_switch("Switch_Front", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_Kitch", (-4.0, 7.6), axis='Y', face_sign=1, aged=True)
    make_cord_run("Cord_Kettle", (-3.55, 7.85, 0.98), (-3.89, 7.6, 0.30))
    # ── Alley truth ──
    make_floor_stain("Alley_Dumpster_Juice", (2.4, 9.65), radius=0.5,
                     tint=(0.22, 0.22, 0.22, 1.0))
    make_floor_stain("Alley_Puddle", (-1.2, 10.6), radius=0.45,
                     tint=(0.26, 0.27, 0.30, 1.0))
    # Downspout streak on the store's back wall + grime base band
    # along the mural wall.
    make_box("Alley_Downspout_Streak", (-3.9, 9.06, 1.30), (0.22, 0.02, 2.5),
             (0.36, 0.36, 0.36, 1.0))
    make_box("Alley_MuralWall_Grime", (0.0, 11.86, 0.25), (10.8, 0.02, 0.5),
             (0.34, 0.24, 0.20, 1.0))


def build_use_states_2026_08():
    """D3 remainder + D4 use states (set-detail playbook). The store
    mid-morning: Petra ON the phone behind her door, the four mugs
    actually poured, the hold shelf doing its slow work. Also lands
    the three commercial-report props draft 1 missed: the SLOW
    TERMINAL, the HOLD SHELF, the open LEDGER. D5/D6 next."""
    # ── Counter: the ledger open beside the register, the slow
    # terminal (a CRT that takes its time), the hold shelf below
    # with three tagged books waiting for their people ──
    cx, cy = ROOM_W/2.0 - 1.4, 2.6
    make_box("Ledger_Open_L", (cx - 0.75, cy - 0.15, 0.965), (0.18, 0.26, 0.015), (0.90, 0.88, 0.80, 1.0))
    make_box("Ledger_Open_R", (cx - 0.56, cy - 0.15, 0.965), (0.18, 0.26, 0.015), (0.90, 0.88, 0.80, 1.0))
    make_box("Ledger_Spine", (cx - 0.655, cy - 0.15, 0.972), (0.02, 0.26, 0.012), (0.36, 0.24, 0.16, 1.0))
    make_box("SlowTerminal_Body", (cx + 0.85, cy + 0.35, 1.13), (0.40, 0.36, 0.34), (0.78, 0.75, 0.68, 1.0))
    make_box("SlowTerminal_Screen", (cx + 0.85, cy + 0.16, 1.15), (0.30, 0.02, 0.22), (0.16, 0.24, 0.18, 1.0))
    make_box("SlowTerminal_Cursor", (cx + 0.76, cy + 0.148, 1.10), (0.03, 0.005, 0.02), (0.55, 0.85, 0.55, 1.0))
    make_box("SlowTerminal_Keyboard", (cx + 0.85, cy - 0.12, 0.975), (0.36, 0.14, 0.025), (0.70, 0.67, 0.60, 1.0))
    for hi in range(3):
        make_box(f"Hold_Book_{hi}", (cx - 0.9 + hi * 0.35, cy + 0.42, 0.62),
                 (0.24, 0.17, 0.05), BOOK_SPINES[(hi * 2) % len(BOOK_SPINES)])
        make_box(f"Hold_Slip_{hi}", (cx - 0.9 + hi * 0.35, cy + 0.34, 0.655),
                 (0.06, 0.14, 0.005), (0.94, 0.92, 0.84, 1.0))
    make_box("Hold_Shelf", (cx - 0.55, cy + 0.42, 0.59), (1.35, 0.25, 0.03), COL_WOOD_DK)
    # ── Petra's office mid-call: handset OFF the cradle, coiled
    # cord to her ear-height, papers pushed to one side ──
    make_box("Office_Handset_InUse", (2.35, 8.05, 1.35), (0.06, 0.20, 0.05), COL_BLACK)
    for ci in range(4):
        make_cyl(f"Office_PhoneCoil_{ci}", (2.35, 8.12 + ci * 0.05, 0.95 + ci * 0.10),
                 0.025, 0.03, COL_BLACK, segments=6)
    make_box("Office_Papers_Pushed", (3.25, 8.45, 0.775), (0.30, 0.24, 0.03), (0.88, 0.86, 0.80, 1.0))
    # ── The four mugs POURED (dark coffee discs) + the kettle just
    # set down off-center on the hob ──
    for mi in range(4):
        mx = -3.40 + 0.14 * (mi % 2)
        my = 6.55 + 0.16 * (mi // 2)
        make_cyl(f"Mug_{mi}_Coffee", (mx, my, 1.075), 0.033, 0.008, (0.24, 0.16, 0.10, 1.0), segments=8)
    make_cyl("Clay_Mug_Coffee", (-3.62, 6.70, 1.085), 0.038, 0.008, (0.26, 0.17, 0.11, 1.0), segments=8)
    # ── The reading nook mid-read: the side-table book now OPEN on
    # the chair arm, cushion dented (darker patch) ──
    make_box("Nook_Book_Open_L", (-2.62, 1.62, 0.665), (0.11, 0.16, 0.01), (0.90, 0.88, 0.80, 1.0))
    make_box("Nook_Book_Open_R", (-2.50, 1.62, 0.665), (0.11, 0.16, 0.01), (0.90, 0.88, 0.80, 1.0))
    make_box("Nook_Cushion_Dent", (-2.9, 1.3, 0.555), (0.36, 0.34, 0.015), (0.40, 0.24, 0.17, 1.0))
    # ── The alley crate as a reading perch: Petra's glasses folded
    # on it + the folded newspaper ("by my reading at the dumpster") ──
    make_box("Alley_Glasses_Bridge", (1.1, 10.55, 0.335), (0.09, 0.012, 0.008), (0.24, 0.22, 0.20, 1.0))
    for gi, gxo in enumerate([-0.05, 0.05]):
        make_cyl(f"Alley_Glasses_Lens_{gi}", (1.1 + gxo, 10.55, 0.333), 0.022, 0.005,
                 (0.70, 0.76, 0.78, 0.6), segments=8)
    make_box("Alley_Newspaper", (1.1, 10.72, 0.335), (0.22, 0.16, 0.012), (0.84, 0.82, 0.76, 1.0))
    make_box("Alley_Newspaper_Fold", (1.1, 10.72, 0.345), (0.22, 0.015, 0.008), (0.70, 0.68, 0.62, 1.0))


def build_beyond_glass_2026_08():
    """D5 · Hemlock Street through the front glass (set-detail
    playbook): sidewalk with joints, a parked car at the curb, the
    facing building with one lit window, a mailbox, a street tree.
    The alley (N) was dressed in the annex pass; this closes the
    last raw edge. D6 coverage rides in the tscn markers."""
    make_box("Hemlock_Sidewalk", (0.0, -1.6, -0.02), (14.0, 2.6, 0.04), (0.56, 0.55, 0.52, 1.0))
    for ji, jx in enumerate([-4.5, -1.5, 1.5, 4.5]):
        make_box(f"Hemlock_Joint_{ji}", (jx, -1.6, 0.005), (0.04, 2.6, 0.01), (0.44, 0.43, 0.40, 1.0))
    make_box("Hemlock_Asphalt", (0.0, -4.8, -0.02), (14.0, 3.8, 0.04), (0.27, 0.27, 0.29, 1.0))
    make_box("Hemlock_Centerline", (0.0, -4.8, 0.005), (12.5, 0.10, 0.01), (0.85, 0.76, 0.30, 1.0))
    # The parked car framed by the front window (x=-2.5 glass).
    make_box("Hemlock_Car_Body", (-2.7, -2.6, 0.55), (4.2, 1.75, 0.55), (0.30, 0.34, 0.30, 1.0))
    make_box("Hemlock_Car_Cabin", (-3.0, -2.6, 1.02), (2.2, 1.6, 0.45), (0.30, 0.34, 0.30, 1.0))
    # Mailbox on the sidewalk + street tree between sightlines.
    make_box("Hemlock_Mailbox_Body", (2.6, -1.0, 1.05), (0.5, 0.4, 0.5), (0.22, 0.30, 0.46, 1.0))
    make_box("Hemlock_Mailbox_Leg", (2.6, -1.0, 0.4), (0.08, 0.08, 0.8), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Hemlock_Tree_Trunk", (4.3, -1.4, 1.2), 0.12, 2.4, (0.30, 0.24, 0.18, 1.0), segments=8)
    make_box("Hemlock_Tree_Crown", (4.3, -1.4, 3.2), (1.8, 1.6, 1.8), (0.16, 0.24, 0.15, 1.0))
    # The facing building: facade band, one lit window (the town is
    # awake), a dark doorway.
    make_box("Hemlock_Across_Facade", (0.0, -7.6, 2.0), (13.0, 0.6, 4.0), (0.42, 0.36, 0.30, 1.0))
    make_box("Hemlock_Across_Win_Dark", (-3.0, -7.25, 1.6), (1.6, 0.06, 1.3), (0.14, 0.15, 0.18, 1.0))
    make_box("Hemlock_Across_Win_Lit", (1.8, -7.25, 1.6), (1.6, 0.06, 1.3), (0.88, 0.78, 0.52, 1.0))
    make_box("Hemlock_Across_Door", (-0.6, -7.25, 1.15), (0.95, 0.06, 2.3), (0.24, 0.20, 0.18, 1.0))


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
    build_back_annex_2026_08()
    build_alley_2026_08()
    build_detail_pass_2026_08()
    build_use_states_2026_08()
    build_beyond_glass_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/salty_tome_interior.glb"))
    print(f"\n[build_salty_tome_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
