"""VOL 5 · Cafe Olimpico — Mile-End Montreal cafe cameo.
Classic Italian espresso bar: counter w/ espresso machine, pastry
case, marble tables, vinyl booth, soccer-pennant decor.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.food_service import make_donut_display, make_coffee_pots
from _props.decor import make_wall_clock, make_faded_poster
from _props.safety import make_smoke_detector, make_ceiling_speaker, make_fluorescent_tube_fixture

PAL = {"wall": (0.86, 0.78, 0.62, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR_TILE = (0.32, 0.30, 0.30, 1.0); COL_GROUT = (0.18, 0.16, 0.16, 1.0)
COL_MARBLE = (0.86, 0.86, 0.82, 1.0); COL_MARBLE_VEIN = (0.42, 0.40, 0.38, 1.0)
COL_VINYL_BOOTH = (0.62, 0.32, 0.20, 1.0); COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_ESPRESSO = (0.78, 0.78, 0.74, 1.0); COL_ESPRESSO_TRIM = (0.32, 0.22, 0.14, 1.0)
COL_PENNANT_BLUE = (0.18, 0.32, 0.62, 1.0); COL_PENNANT_RED = (0.78, 0.22, 0.20, 1.0)
ROOM_W = 8.0; ROOM_D = 6.0; CEIL = 3.00

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR_TILE, "seam": COL_GROUT})
    for nm, x, ax, bb in [("Wall_W", -ROOM_W/2.0, 'Y', +1), ("Wall_E", +ROOM_W/2.0, 'Y', -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis=ax, palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-3.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+3.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (4.0, 0.20, 0.60), PAL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    make_window("Window_SW", (-2.0, 0.0, 1.60), width=2.20, height=1.60)
    make_window("Window_SE", (+2.0, 0.0, 1.60), width=2.20, height=1.60)
    # 2026-08 tail pass: the BELL over the door + the BACK-CORNER
    # window in the W wall (X-thin, hand-built) the corner table
    # sits under.
    make_box("DoorBell_Arm", (0.55, 0.16, 2.42), (0.03, 0.14, 0.03), P.METAL_STEEL)
    make_cyl("DoorBell", (0.55, 0.26, 2.36), 0.05, 0.07, (0.82, 0.72, 0.42, 1.0), segments=10)
    wx = -ROOM_W/2.0 + 0.10
    make_box("Win_BackCorner_Frame", (wx, 4.3, 1.65), (0.06, 1.30, 1.40), COL_WOOD)
    make_box("Win_BackCorner_Glass", (wx+0.01, 4.3, 1.65), (0.03, 1.16, 1.26), (0.68, 0.76, 0.78, 0.6))
    make_box("Win_BackCorner_Mullion", (wx+0.02, 4.3, 1.65), (0.03, 0.05, 1.26), COL_WOOD)

def build_bar_counter():
    # Long bar counter along north wall
    # make_counter's `depth` is the X extent, `length` the Y —
    # so length>depth built this counter ROTATED 90 DEGREES:
    # a narrow face against the wall and the run jutting into
    # the room. Swapped 2026-08-12 (same bug as the New
    # Orleans bar and the pit stop's lunch counter).
    top_z = make_counter("Bar", (0.0, 5.0, 0.0), length=0.80, depth=5.0, height=1.05, palette={"formica": COL_MARBLE, "top": COL_MARBLE_VEIN, "kick": COL_WOOD})
    make_counter_bullnose("Bar", (0.0, 5.0 - 0.40, top_z), length=5.0, palette={"top": COL_MARBLE_VEIN}, axis='X')
    # Espresso machine — classic 2-group La Marzocco-ish chrome
    ex, ey = 0.0, 5.10
    make_box("Espresso_Body", (ex, ey, top_z+0.30), (1.40, 0.50, 0.60), COL_ESPRESSO)
    make_box("Espresso_TopHat", (ex, ey, top_z+0.66), (1.40, 0.50, 0.10), COL_ESPRESSO_TRIM)
    for gi in range(2):
        gx = ex - 0.30 + gi*0.60
        make_cyl(f"Espresso_Group_{gi}_Head", (gx, ey-0.22, top_z+0.20), 0.06, 0.10, COL_ESPRESSO_TRIM)
        make_cyl(f"Espresso_Group_{gi}_Spout", (gx, ey-0.22, top_z+0.12), 0.02, 0.08, P.METAL_STEEL)
        # Cup waiting under spout
        make_cyl(f"Espresso_Cup_{gi}", (gx, ey-0.22, top_z+0.04), 0.04, 0.06, P.PAPER)
    # Steam wand
    make_cyl("Espresso_SteamWand", (ex+0.60, ey-0.10, top_z+0.30), 0.012, 0.30, P.METAL_STEEL)
    # Pastry case east end of bar
    make_donut_display("Pastry", (+2.20, 5.20, top_z))
    # Coffee pots west end
    make_coffee_pots("Coffee", (-2.20, 5.10, top_z), pots=2)

def build_seating():
    # Marble round tables (2) with bentwood chairs
    # Table_0 moved against the SW front window (2026-08 — the
    # street-watching seat the scenes describe).
    for ti, (tx, ty) in enumerate([(-2.0, 0.95), (+2.0, 1.80)]):
        make_cyl(f"Table_{ti}_Top", (tx, ty, 0.74), 0.42, 0.04, COL_MARBLE)
        make_cyl(f"Table_{ti}_Pedestal", (tx, ty, 0.37), 0.06, 0.70, COL_ESPRESSO_TRIM)
        make_cyl(f"Table_{ti}_Foot", (tx, ty, 0.04), 0.24, 0.04, COL_ESPRESSO_TRIM)
        # 2 chairs per table
        for ci, (cx_off, cy_off) in enumerate([(-0.60, 0), (+0.60, 0)]):
            cx, cy = tx + cx_off, ty + cy_off
            make_cyl(f"Table_{ti}_Chair_{ci}_Seat", (cx, cy, 0.46), 0.20, 0.04, COL_WOOD)
            make_box(f"Table_{ti}_Chair_{ci}_Back", (cx, cy + (0.18 if cx_off < 0 else -0.18), 0.74), (0.40, 0.04, 0.56), COL_WOOD)
        # Espresso + saucer on each table
        make_cyl(f"Table_{ti}_Saucer", (tx, ty, 0.78), 0.06, 0.005, P.PAPER)
        make_cyl(f"Table_{ti}_Cup", (tx, ty, 0.82), 0.04, 0.06, P.PAPER)
    # Vinyl booth along east wall
    bx, by = +3.30, 3.0
    make_box("Booth_Seat", (bx, by, 0.40), (0.60, 2.20, 0.10), COL_VINYL_BOOTH)
    make_box("Booth_Back", (bx+0.20, by, 0.92), (0.20, 2.20, 1.00), COL_VINYL_BOOTH)
    make_box("Booth_Table", (bx-0.60, by, 0.72), (0.50, 1.40, 0.04), COL_MARBLE)
    make_cyl("Booth_Table_Pedestal", (bx-0.60, by, 0.37), 0.06, 0.70, COL_ESPRESSO_TRIM)
    # The BACK-CORNER table (NW, under its window): water glass, the
    # open notebook, and the croissant in its paper bag.
    ctx, cty = -3.25, 4.25
    make_cyl("CornerTable_Top", (ctx, cty, 0.74), 0.42, 0.04, COL_MARBLE)
    make_cyl("CornerTable_Pedestal", (ctx, cty, 0.37), 0.06, 0.70, COL_ESPRESSO_TRIM)
    make_cyl("CornerTable_Foot", (ctx, cty, 0.04), 0.24, 0.04, COL_ESPRESSO_TRIM)
    for ci2, (cxo, cyo) in enumerate([(0.60, 0.0), (0.0, -0.60)]):
        ccx, ccy = ctx + cxo, cty + cyo
        make_cyl(f"CornerTable_Chair_{ci2}_Seat", (ccx, ccy, 0.46), 0.20, 0.04, COL_WOOD)
        if cxo != 0.0:
            make_box(f"CornerTable_Chair_{ci2}_Back", (ccx+0.18, ccy, 0.74), (0.04, 0.40, 0.56), COL_WOOD)
        else:
            make_box(f"CornerTable_Chair_{ci2}_Back", (ccx, ccy-0.18, 0.74), (0.40, 0.04, 0.56), COL_WOOD)
    make_cyl("CornerTable_WaterGlass", (ctx+0.18, cty+0.14, 0.81), 0.035, 0.13, (0.80, 0.86, 0.88, 0.6), segments=8)
    make_box("CornerTable_Notebook", (ctx-0.10, cty-0.05, 0.765), (0.30, 0.21, 0.015), (0.92, 0.90, 0.84, 1.0))
    make_box("CornerTable_Notebook_Spine", (ctx-0.10, cty-0.05, 0.772), (0.015, 0.21, 0.012), (0.30, 0.28, 0.26, 1.0))
    make_cyl("CornerTable_Pen", (ctx+0.08, cty-0.16, 0.775), 0.007, 0.13, (0.16, 0.18, 0.32, 1.0), axis='X', segments=6)
    make_box("CornerTable_CroissantBag", (ctx-0.02, cty+0.20, 0.775), (0.20, 0.13, 0.05), (0.80, 0.68, 0.48, 1.0))
    make_box("CornerTable_Croissant", (ctx-0.02, cty+0.24, 0.795), (0.13, 0.06, 0.04), (0.86, 0.64, 0.34, 1.0))

def build_pennants_and_decor():
    # Soccer pennants hanging on north wall over bar
    pennant_colors = [COL_PENNANT_BLUE, COL_PENNANT_RED, COL_PENNANT_BLUE, COL_PENNANT_RED, COL_PENNANT_BLUE]
    for pi, col in enumerate(pennant_colors):
        px = -2.0 + pi*1.0
        make_box(f"Pennant_{pi}", (px, ROOM_D-0.04, 2.50), (0.40, 0.04, 0.40), col)
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, 2.10), frozen_hour=10, frozen_min=30)
    make_faded_poster("Poster_W", (-3.95, 3.0, 1.80))

def build_ceiling_infra():
    # 2026-08 tail pass: the 3x3 office fluorescent grid was the
    # template leak — the marble-and-pennants idiom takes warm
    # globe pendants over bar and floor.
    for pi2, (px, py) in enumerate([(-2.0, 2.4), (2.0, 2.4), (0.0, 4.6)]):
        make_cyl(f"Globe_{pi2}_Cord", (px, py, CEIL-0.22), 0.008, 0.44, P.METAL_BLACK)
        make_cyl(f"Globe_{pi2}_Sphere", (px, py, CEIL-0.55), 0.14, 0.24, (0.97, 0.90, 0.72, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL))
    make_ceiling_speaker("Speaker", (-1.0, 3.0, CEIL))

def main():
    clear_scene(); build_shell(); build_bar_counter(); build_seating(); build_pennants_and_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/cafe_olimpico.glb"))
    print(f"\n[build_cafe_olimpico] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
