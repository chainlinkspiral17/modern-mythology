"""board_lords_interior — vol5-7 hobby / board-game shop "Board Lords".

Was thin (two double-sided gondolas + a demo table + a dice case +
a register + wall posters, ~31 calls). Enriched to a real game shop:
tall WALL SHELVES of spine-out boxed games on the W/E/N walls, a
NEW RELEASES face-out endcap by the door, a glass sales COUNTER with
register + a divided dice bin + a card spinner, a demo play table
(kept, board mid-game), a front WINDOW, a hanging shop BANNER, a
floor plant, and decor (clock, calendar, posters, crown molding).

Room: door/S wall at blender y=0, extends +Y; interior lands at
godot -Z. Props kept inside the 9.0 x 7.0 footprint.
"""
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
from _props.signage import make_hanging_banner
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture


def make_game_shelf(prefix, anchor, *, axis, run_len, face_sign,
                    levels=4, level_h=0.56, base_z=0.10, col_frame=None):
    """Tall wall shelf unit packed with spine-out boxed games.
    anchor=(wall_x, wall_y, _). axis='Y' (wall runs N-S) or 'X' (E-W).
    face_sign points INTO the room (+/-1 on the perpendicular axis)."""
    col_frame = col_frame or (0.24, 0.18, 0.28, 1.0)
    wx, wy, _ = anchor
    depth = 0.34
    top_z = base_z + levels * level_h
    if axis == 'Y':
        cx = wx + face_sign * depth / 2.0
        # back panel + two end uprights
        make_box(f"{prefix}_Back", (wx + face_sign * 0.02, wy, top_z / 2.0 + base_z / 2.0),
                 (0.04, run_len, top_z), col_frame)
        for eo in (-run_len / 2.0, run_len / 2.0):
            make_box(f"{prefix}_Up_{eo:.1f}", (cx, wy + eo, top_z / 2.0 + base_z / 2.0),
                     (depth, 0.06, top_z), col_frame)
        for lv in range(levels):
            shz = base_z + 0.22 + lv * level_h
            make_box(f"{prefix}_Shelf_{lv}", (cx, wy, shz), (depth, run_len, 0.04), P.METAL_STEEL)
            n = int(run_len / 0.075)
            for bi in range(n):
                by = wy - run_len / 2.0 + (bi + 0.5) * (run_len / n)
                tint = P.SNACK_TINTS[(lv * 2 + bi) % len(P.SNACK_TINTS)]
                bh = [0.30, 0.36, 0.42, 0.28][(lv + bi) % 4]
                make_box(f"{prefix}_Game_{lv}_{bi}", (cx, by, shz + bh / 2.0 + 0.02),
                         (depth * 0.85, run_len / n * 0.8, bh), tint)
    else:
        cy = wy + face_sign * depth / 2.0
        make_box(f"{prefix}_Back", (wx, wy + face_sign * 0.02, top_z / 2.0 + base_z / 2.0),
                 (run_len, 0.04, top_z), col_frame)
        for eo in (-run_len / 2.0, run_len / 2.0):
            make_box(f"{prefix}_Up_{eo:.1f}", (wx + eo, cy, top_z / 2.0 + base_z / 2.0),
                     (0.06, depth, top_z), col_frame)
        for lv in range(levels):
            shz = base_z + 0.22 + lv * level_h
            make_box(f"{prefix}_Shelf_{lv}", (wx, cy, shz), (run_len, depth, 0.04), P.METAL_STEEL)
            n = int(run_len / 0.075)
            for bi in range(n):
                bx = wx - run_len / 2.0 + (bi + 0.5) * (run_len / n)
                tint = P.SNACK_TINTS[(lv * 2 + bi) % len(P.SNACK_TINTS)]
                bh = [0.30, 0.36, 0.42, 0.28][(lv + bi) % 4]
                make_box(f"{prefix}_Game_{lv}_{bi}", (bx, cy, shz + bh / 2.0 + 0.02),
                         (run_len / n * 0.8, depth * 0.85, bh), tint)

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
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_wall_shelves():
    # Tall walls of spine-out boxed games — the identity of a game shop.
    make_game_shelf("ShelfW", (-ROOM_W/2.0+0.06, ROOM_D/2.0+0.3, 0.0),
                    axis='Y', run_len=5.6, face_sign=+1, levels=4)
    make_game_shelf("ShelfE", (+ROOM_W/2.0-0.06, ROOM_D/2.0-0.3, 0.0),
                    axis='Y', run_len=5.6, face_sign=-1, levels=4)
    make_game_shelf("ShelfN", (-1.4, ROOM_D-0.06, 0.0),
                    axis='X', run_len=4.0, face_sign=-1, levels=4)

def build_new_release():
    # NEW RELEASES face-out endcap greeting the door + a placard.
    make_endcap("NewRelease", (2.6, 1.2, 0.0), palette={"header": COL_ACCENT})
    make_box("NewRelease_Placard", (2.6, 0.86, 1.95), (0.90, 0.03, 0.24), (0.96, 0.92, 0.42, 1.0))

def build_window():
    make_window("Win_S", (-2.75, 0.10, 1.55), width=2.60, height=1.50)
    # Two boxed games staged in the display window
    for wi, wx in enumerate([-3.4, -2.1]):
        make_box(f"WinDisplay_{wi}", (wx, 0.30, 0.95), (0.34, 0.34, 0.34),
                 P.SNACK_TINTS[wi % len(P.SNACK_TINTS)])
        make_box(f"WinStand_{wi}", (wx, 0.30, 0.62), (0.30, 0.30, 0.30), (0.30, 0.22, 0.32, 1.0))

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
    cx, cy = ROOM_W/4.0, ROOM_D-1.5
    top_z = make_counter("Register", (cx, cy, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": COL_WOOD, "top": (0.18, 0.12, 0.20, 1.0), "kick": (0.18, 0.12, 0.20, 1.0)})
    make_counter_bullnose("Register", (cx-0.55, cy, top_z), length=2.40,
                          palette={"top": (0.18, 0.12, 0.20, 1.0)})
    make_register("RegisterMachine", (cx+0.30, cy-0.30, top_z))
    # Divided dice bin on the counter — loose polyhedral dice by colour
    make_box("DiceBin_Body", (cx-0.10, cy+0.55, top_z+0.06), (0.60, 0.36, 0.12), (0.30, 0.22, 0.32, 1.0))
    for di in range(3):
        make_box(f"DiceBin_Div_{di}", (cx-0.28+di*0.18, cy+0.55, top_z+0.10), (0.01, 0.34, 0.10), COL_WOOD)
        for kk in range(4):
            make_cyl(f"Dice_{di}_{kk}", (cx-0.34+di*0.18+ (kk%2)*0.10, cy+0.46+(kk//2)*0.16, top_z+0.10),
                     0.02, 0.04, P.SNACK_TINTS[(di+kk) % len(P.SNACK_TINTS)], segments=6)
    # Card / accessories spinner on the counter's south end
    make_cyl("CardSpin_Post", (cx-0.85, cy-0.20, top_z+0.28), 0.02, 0.56, P.METAL_STEEL, segments=8)
    for tier, tz in enumerate([top_z+0.18, top_z+0.40]):
        for pk in range(4):
            import math as _m
            ang = pk*(_m.pi/2.0)+tier*0.5
            ox, oy = _m.cos(ang)*0.14, _m.sin(ang)*0.14
            make_box(f"CardSpin_{tier}_{pk}", (cx-0.85+ox, cy-0.20+oy, tz), (0.10, 0.02, 0.16),
                     P.SNACK_TINTS[(tier+pk) % len(P.SNACK_TINTS)])

def build_decor():
    make_floor_plant("Plant", (-ROOM_W/2.0+0.55, ROOM_D-0.6, 0.0))
    make_wall_clock("Clock", (0.0, ROOM_D-0.11, CEIL-0.55), frozen_hour=4, frozen_min=20)
    make_calendar("Calendar", (ROOM_W/2.0-0.05, 2.4, 1.70))
    make_hanging_banner("Banner", (0.0, 1.4, CEIL), width=3.20, height=0.42,
                        bg_color=(0.42, 0.24, 0.52, 1.0))

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
    build_wall_shelves()
    build_shelves()
    build_new_release()
    build_window()
    build_demo_table()
    build_display()
    build_register_counter()
    build_decor()
    build_posters()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/board_lords_interior.glb"))
    print(f"\n[build_board_lords_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
