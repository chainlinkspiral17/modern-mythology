"""Cosmic Comics — back-issue floor — vol6 placement script.

The vol6 showpiece comic shop (heavily used across the volume).
Enriched from a good-but-modest floor (2 comic bins + a spinner + a
register + a slab case + a pegwall + a standee, ~37 calls) to a dense
showpiece: THREE long spine-out comic-bin rows, a SECOND spinner rack,
a north-wall WALL OF BAGGED KEY ISSUES over a shelf of collectible
STATUES, a freestanding glass STATUE TOWER, floor stacks of back-issue
LONGBOXES, an enriched glass sales COUNTER with a grail slab under a
dome, a front WINDOW with a display, a checkerboard TILE floor, a
hanging COSMIC COMICS banner, and more posters. Room: door/S wall at
blender y=0, extends +Y; interior lands at godot -Z. Props kept inside
the 10.0 x 8.0 footprint.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.signage import make_hanging_banner
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

HERO_COLS = [(0.72, 0.24, 0.22, 1.0), (0.26, 0.36, 0.62, 1.0), (0.30, 0.52, 0.34, 1.0),
             (0.62, 0.52, 0.22, 1.0), (0.52, 0.30, 0.52, 1.0), (0.24, 0.48, 0.56, 1.0)]

def make_mini_statue(prefix, anchor, *, h=0.34, body_col=None, accent_col=None):
    """A small collectible hero statue on a base: base disc + legs +
    torso + head + a raised arm + a cape accent. anchor=(cx, cy, base_z)."""
    body_col = body_col or HERO_COLS[0]
    accent_col = accent_col or (0.86, 0.78, 0.30, 1.0)
    cx, cy, bz = anchor
    make_cyl(f"{prefix}_Base", (cx, cy, bz+0.02), 0.09, 0.04, (0.16, 0.14, 0.18, 1.0), segments=10)
    make_box(f"{prefix}_Legs", (cx, cy, bz+0.04+h*0.22), (0.10, 0.08, h*0.44), body_col)
    make_box(f"{prefix}_Torso", (cx, cy, bz+0.04+h*0.62), (0.14, 0.10, h*0.40), accent_col)
    make_cyl(f"{prefix}_Head", (cx, cy, bz+0.04+h*0.92), 0.045, h*0.20, (0.72, 0.56, 0.46, 1.0), segments=8)
    make_box(f"{prefix}_Arm", (cx+0.10, cy, bz+0.04+h*0.78), (0.05, 0.05, h*0.34), body_col)
    make_box(f"{prefix}_Cape", (cx, cy+0.06, bz+0.04+h*0.60), (0.14, 0.03, h*0.50), body_col)

ROOM_W = 10.0; ROOM_D = 8.0; CEIL = 2.8
PAL_WALL = {"wall": (0.42, 0.32, 0.46, 1.0), "baseboard": (0.18, 0.12, 0.20, 1.0)}
COL_FLOOR = (0.32, 0.28, 0.32, 1.0); COL_SEAM = (0.18, 0.16, 0.20, 1.0); COL_WOOD = (0.42, 0.30, 0.52, 1.0)
COL_ACCENT = (0.78, 0.42, 0.86, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_bins():
    # Three long spine-out back-issue bin rows down the floor.
    for ji, ay in enumerate([2.6, 4.0, 5.4]):
        make_box(f"Bin_{ji}_Base", (0.0, ay, 0.30), (5.0, 0.50, 0.60), (0.30, 0.22, 0.14, 1.0))
        make_box(f"Bin_{ji}_Label", (0.0, ay-0.26, 0.50), (4.6, 0.02, 0.12), (0.86, 0.72, 0.32, 1.0))
        for di in range(11):
            make_box(f"Bin_{ji}_Div_{di}", (-2.5+di*0.5, ay, 0.66), (0.02, 0.50, 0.12), P.METAL_STEEL)
        for ci in range(20):
            cx_pos = -2.4 + (ci % 10) * 0.45
            cy_off = -0.20 + (ci // 10) * 0.40
            tint = P.SNACK_TINTS[(ji + ci) % len(P.SNACK_TINTS)]
            make_box(f"Bin_{ji}_Comic_{ci}", (cx_pos, ay + cy_off, 0.70), (0.40, 0.04, 0.20), tint)

def build_second_spinner():
    # A second revolving spinner rack on the west floor.
    rx, ry = -3.6, 4.0
    make_cyl("Spin2_Base", (rx, ry, 0.06), 0.46, 0.12, P.METAL_BLACK, segments=16)
    make_cyl("Spin2_Pole", (rx, ry, 0.98), 0.045, 1.84, P.METAL_STEEL, segments=8)
    for tier, tz in enumerate([0.66, 1.16, 1.66]):
        for pk in range(6):
            ang = pk * (2.0 * math.pi / 6.0) + tier * 0.4
            ox, oy = math.cos(ang) * 0.34, math.sin(ang) * 0.34
            make_box(f"Spin2_Wire_{tier}_{pk}", (rx+ox*0.6, ry+oy*0.6, tz), (0.02, 0.02, 0.30), P.METAL_STEEL)
            tint = P.SNACK_TINTS[(tier + pk + 2) % len(P.SNACK_TINTS)]
            make_box(f"Spin2_Comic_{tier}_{pk}", (rx+ox, ry+oy, tz+0.02), (0.22, 0.03, 0.30), tint)

def build_key_wall():
    # North-wall WALL OF BAGGED KEY ISSUES (cover-out grid) over a
    # header, with a lit shelf of collectible statues below it.
    cx = -2.0
    make_box("KeyWall_Header", (cx, ROOM_D-0.11, 2.45), (3.8, 0.03, 0.28), COL_ACCENT)
    make_box("KeyWall_HeaderTxt", (cx, ROOM_D-0.125, 2.45), (2.8, 0.01, 0.14), P.PAPER)
    for r in range(3):
        for c in range(8):
            kx = cx - 1.75 + c * 0.50
            kz = 1.30 + r * 0.44
            tint = P.SNACK_TINTS[(r * 3 + c) % len(P.SNACK_TINTS)]
            make_box(f"Key_{r}_{c}_Bag", (kx, ROOM_D-0.10, kz), (0.36, 0.02, 0.40), (0.82, 0.86, 0.90, 0.4))
            make_box(f"Key_{r}_{c}_Cover", (kx, ROOM_D-0.115, kz), (0.30, 0.01, 0.34), tint)
    # Statue shelf below the key wall
    make_box("StatShelf", (cx, ROOM_D-0.30, 1.02), (3.6, 0.36, 0.05), COL_WOOD)
    for si in range(6):
        sx = cx - 1.5 + si * 0.6
        make_mini_statue(f"Statue_{si}", (sx, ROOM_D-0.30, 1.045), h=0.36,
                         body_col=HERO_COLS[si % len(HERO_COLS)],
                         accent_col=HERO_COLS[(si+3) % len(HERO_COLS)])

def build_statue_tower():
    # Freestanding glass statue tower near the entrance — three tiers.
    tx, ty = 0.0, 1.3
    make_box("Tower_Base", (tx, ty, 0.30), (0.90, 0.90, 0.60), COL_WOOD)
    make_box("Tower_Glass", (tx, ty, 1.20), (0.86, 0.86, 1.20), (0.70, 0.80, 0.92, 0.30))
    for tier, tz in enumerate([0.66, 1.10, 1.54]):
        make_box(f"Tower_Shelf_{tier}", (tx, ty, tz), (0.84, 0.84, 0.03), (0.72, 0.74, 0.80, 1.0))
        for si in range(2):
            sx = tx - 0.22 + si * 0.44
            make_mini_statue(f"Tower_Statue_{tier}_{si}", (sx, ty, tz+0.02), h=0.34,
                             body_col=HERO_COLS[(tier*2+si) % len(HERO_COLS)],
                             accent_col=HERO_COLS[(tier*2+si+2) % len(HERO_COLS)])

def build_back_issues():
    # Floor stacks of cardboard back-issue longboxes (lidded).
    def longbox_stack(pfx, bx, by, n):
        for li in range(n):
            make_box(f"{pfx}_Box_{li}", (bx, by, 0.14 + li*0.24), (0.42, 0.74, 0.22), (0.72, 0.62, 0.44, 1.0))
            make_box(f"{pfx}_Lid_{li}", (bx, by, 0.25 + li*0.24), (0.44, 0.76, 0.03), (0.60, 0.50, 0.34, 1.0))
    longbox_stack("LB_E0", ROOM_W/2.0-0.5, 5.2, 3)
    longbox_stack("LB_E1", ROOM_W/2.0-0.5, 6.2, 2)
    longbox_stack("LB_SW", -ROOM_W/2.0+0.5, 1.6, 3)

def build_register_counter():
    cx, cy = ROOM_W/4.0, ROOM_D-1.5
    top_z = make_counter("Register", (cx, cy, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": (0.42, 0.30, 0.52, 1.0), "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_counter_bullnose("Register", (cx-0.55, cy, top_z), length=2.40,
                          palette={"top": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (cx+0.30, cy-0.30, top_z))
    # The GRAIL BOOK — a single high-grade slab under a glass dome, lit.
    gx, gy = cx-0.7, cy
    make_box("Grail_Slab", (gx, gy, top_z+0.14), (0.20, 0.30, 0.03), (0.86, 0.42, 0.30, 1.0))
    make_box("Grail_Label", (gx, gy-0.13, top_z+0.20), (0.16, 0.02, 0.06), P.PAPER)
    make_box("Grail_Dome", (gx, gy, top_z+0.16), (0.30, 0.40, 0.30), (0.72, 0.80, 0.92, 0.25))
    make_box("Grail_DomeBase", (gx, gy, top_z+0.02), (0.32, 0.42, 0.04), P.METAL_BLACK)
    # A glass display of graded slabs along the counter face (customer side)
    for si in range(4):
        make_box(f"CounterSlab_{si}", (cx-0.9+si*0.5, cy-0.52, top_z-0.30), (0.18, 0.02, 0.26),
                 HERO_COLS[si % len(HERO_COLS)])

def build_rack():
    # Iconic revolving comic spinner instead of a flat wall slab: a
    # weighted base, a steel pole, and three tiers of radiating wire
    # pockets, each holding a colour-coded comic.
    rx, ry = -ROOM_W/2.0 + 1.1, ROOM_D - 1.3
    make_cyl("Spinner_Base", (rx, ry, 0.06), 0.46, 0.12, P.METAL_BLACK, segments=16)
    make_cyl("Spinner_Pole", (rx, ry, 0.98), 0.045, 1.84, P.METAL_STEEL, segments=8)
    for tier, tz in enumerate([0.66, 1.16, 1.66]):
        for pk in range(6):
            ang = pk * (2.0 * math.pi / 6.0) + tier * 0.4
            ox, oy = math.cos(ang) * 0.34, math.sin(ang) * 0.34
            make_box(f"Spinner_Wire_{tier}_{pk}", (rx+ox*0.6, ry+oy*0.6, tz), (0.02, 0.02, 0.30), P.METAL_STEEL)
            tint = P.SNACK_TINTS[(tier + pk) % len(P.SNACK_TINTS)]
            make_box(f"Spinner_Comic_{tier}_{pk}", (rx+ox, ry+oy, tz+0.02), (0.22, 0.03, 0.30), tint)

def build_posters():
    for pi in range(3):
        py = 1.0 + pi*2.0
        make_faded_poster(f"Poster_W_{pi}", (-ROOM_W/2.0+0.05, py, 1.70), palette={"body": COL_ACCENT})
    # Two more posters flanking the counter on the east wall
    for pi, py in enumerate([4.6, 6.4]):
        make_faded_poster(f"Poster_E_{pi}", (ROOM_W/2.0-0.05, py, 1.80),
                          palette={"body": HERO_COLS[pi % len(HERO_COLS)]})

def build_window():
    # Front display window on the SW south-wall segment.
    make_window("Win_S", (-3.0, 0.10, 1.55), width=2.60, height=1.50)
    # Window display: a low riser with two statues + a hero poster behind
    make_box("WinRiser", (-3.0, 0.35, 0.55), (2.0, 0.50, 0.50), COL_WOOD)
    for si in range(2):
        make_mini_statue(f"WinStatue_{si}", (-3.5+si*1.0, 0.35, 0.80), h=0.42,
                         body_col=HERO_COLS[si], accent_col=HERO_COLS[si+2])
    make_box("WinPoster", (-3.0, 0.16, 1.70), (1.6, 0.01, 0.90), HERO_COLS[1])

def build_floor_tiles():
    # Checkerboard tile overlay — comic-shop floor.
    for i in range(int(ROOM_W)):
        for j in range(int(ROOM_D)):
            if (i + j) % 2 == 0:
                continue
            tx = -ROOM_W/2.0 + 0.5 + i
            ty = 0.5 + j
            make_box(f"Tile_{i}_{j}", (tx, ty, 0.006), (0.98, 0.98, 0.001), (0.22, 0.18, 0.26, 1.0))

def build_banner():
    make_hanging_banner("Banner", (0.0, 3.0, CEIL), width=3.60, height=0.44,
                        bg_color=(0.52, 0.26, 0.62, 1.0))

def build_drop():
    pass  # ceiling already added in build_shell

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Comic-shop flavour: a glass display case of graded slabs beside
    the register, an action-figure pegwall on the east wall, a cardboard
    standee, and a stool behind the counter."""
    # Glass display case beside the register
    dx, dy = ROOM_W/4.0 - 1.7, ROOM_D - 1.5
    make_box("Case_Body", (dx, dy, 0.45), (1.20, 0.60, 0.90), COL_WOOD)
    make_box("Case_Glass", (dx, dy, 1.06), (1.16, 0.56, 0.32), (0.70, 0.80, 0.92, 0.35))
    for gi in range(5):
        make_box(f"Case_Slab_{gi}", (dx-0.48+gi*0.24, dy, 0.96), (0.16, 0.30, 0.02),
                 P.SNACK_TINTS[gi % len(P.SNACK_TINTS)])
    # Action-figure pegwall, east wall (blister cards + figure bodies)
    for r in range(3):
        for c in range(4):
            px = ROOM_W/2.0 - 0.10; py = 2.0 + c * 0.55; pz = 1.2 + r * 0.5
            make_box(f"Peg_{r}_{c}_Card", (px, py, pz), (0.02, 0.22, 0.30), (0.86, 0.78, 0.42, 1.0))
            make_cyl(f"Peg_{r}_{c}_Fig", (px-0.08, py, pz), 0.05, 0.20,
                     P.SNACK_TINTS[(r + c) % len(P.SNACK_TINTS)], axis='X', segments=8)
    # Cardboard standee near the front SE corner
    make_box("Standee_Board", (ROOM_W/2.0 - 1.3, 1.0, 0.98), (0.55, 0.05, 1.92), COL_ACCENT)
    make_box("Standee_Foot", (ROOM_W/2.0 - 1.3, 1.15, 0.03), (0.55, 0.30, 0.03), (0.30, 0.22, 0.14, 1.0))
    # Stool behind the register
    make_cyl("Stool_Seat", (ROOM_W/4.0 - 0.7, ROOM_D - 2.6, 0.56), 0.18, 0.06, P.METAL_BLACK, segments=12)
    make_cyl("Stool_Post", (ROOM_W/4.0 - 0.7, ROOM_D - 2.6, 0.28), 0.03, 0.54, P.METAL_STEEL, segments=8)

def main():
    clear_scene()
    build_shell()
    build_floor_tiles()
    build_window()
    build_bins()
    build_register_counter()
    build_rack()
    build_second_spinner()
    build_key_wall()
    build_statue_tower()
    build_back_issues()
    build_posters()
    build_banner()
    build_drop()
    build_ceiling_infra()
    build_dressing()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cosmic_comics_interior.glb"))
    print(f"\n[build_cosmic_comics_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
