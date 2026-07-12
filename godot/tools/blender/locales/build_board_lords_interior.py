"""board_lords_interior — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 9.0; ROOM_D = 7.0; CEIL = 2.8
PAL_WALL = {"wall":(0.42,0.32,0.46,1.0),"baseboard":(0.18,0.12,0.20,1.0)}
COL_FLOOR = (0.32,0.28,0.32,1.0); COL_SEAM = (0.18,0.16,0.20,1.0); COL_WOOD = (0.42,0.30,0.52,1.0)
COL_ACCENT = (0.78,0.42,0.86,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_shelves():
    # Double-sided gondolas stocked with board-game boxes shelved
    # spine-out (colourful) — was two empty flat base boxes.
    for ji in range(2):
        ay = ROOM_D * (0.35 + ji * 0.30)
        make_box(f"Gondola_{ji}_Base", (0.0, ay, 0.30), (5.0, 0.60, 0.60), (0.28, 0.20, 0.32, 1.0))
        make_box(f"Gondola_{ji}_Spine", (0.0, ay, 1.30), (5.0, 0.12, 1.40), (0.24, 0.18, 0.28, 1.0))
        for side in (-1, 1):
            for sh, sz in enumerate([0.78, 1.30, 1.82]):
                for bi in range(9):
                    bx = -2.2 + bi*0.5
                    tint = P.SNACK_TINTS[(ji + side + sh + bi) % len(P.SNACK_TINTS)]
                    make_box(f"Game_{ji}_{'L' if side < 0 else 'R'}_{sh}_{bi}",
                             (bx, ay+side*0.30, sz), (0.44, 0.06, 0.34), tint)

def build_register_counter():
    top_z = make_counter("Register", (ROOM_W/4.0, ROOM_D-1.5, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (ROOM_W/4.0, ROOM_D-1.5-0.30, top_z))

def build_posters():
    for pi in range(3):
        px = -ROOM_W/2.0+0.05; py = 1.0 + pi*1.5
        make_faded_poster(f"Poster_W_{pi}", (px, py, 1.50))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_demo_table():
    # Open-play demo table on the west side: a game board mid-play,
    # tokens, and two chairs — the heart of a board-game shop.
    tx, ty = -ROOM_W/4.0, ROOM_D/2.0
    make_box("DemoTable_Top", (tx, ty, 0.74), (1.40, 1.00, 0.06), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.6, -0.4), (0.6, -0.4), (-0.6, 0.4), (0.6, 0.4)]):
        make_box(f"DemoLeg_{i}", (tx+lx, ty+ly, 0.36), (0.06, 0.06, 0.72), COL_WOOD)
    make_box("Board", (tx, ty, 0.79), (0.72, 0.72, 0.02), (0.86, 0.82, 0.70, 1.0))
    for gi in range(6):
        make_cyl(f"Piece_{gi}", (tx-0.3+gi*0.12, ty-0.2, 0.84), 0.04, 0.06, P.SNACK_TINTS[gi % len(P.SNACK_TINTS)], segments=8)
    for ci, cy in enumerate([ty-0.9, ty+0.9]):
        make_box(f"DemoChair_{ci}_Seat", (tx, cy, 0.46), (0.42, 0.42, 0.05), COL_WOOD)
        make_box(f"DemoChair_{ci}_Back", (tx, cy + (0.18 if cy > ty else -0.18), 0.72), (0.42, 0.04, 0.44), COL_WOOD)

def build_display():
    # Glass case of dice + minis beside the register
    dx, dy = ROOM_W/4.0 - 1.9, ROOM_D-1.5
    make_box("Case_Body", (dx, dy, 0.45), (1.20, 0.60, 0.90), COL_WOOD)
    make_box("Case_Glass", (dx, dy, 1.06), (1.16, 0.56, 0.32), (0.72, 0.80, 0.92, 0.35))
    for gi in range(6):
        make_cyl(f"Dice_{gi}", (dx-0.5+gi*0.20, dy, 0.95), 0.04, 0.08, P.SNACK_TINTS[gi % len(P.SNACK_TINTS)], segments=6)

def main():
    clear_scene()
    build_shell()
    build_shelves()
    build_demo_table()
    build_display()
    build_register_counter()
    build_posters()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/board_lords_interior.glb"))
    print(f"\n[build_board_lords_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
