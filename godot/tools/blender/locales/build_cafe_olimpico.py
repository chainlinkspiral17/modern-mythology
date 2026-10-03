"""VOL 5 · Cafe Olimpico — Mile-End Montreal cafe cameo.
Classic Italian espresso bar: counter w/ espresso machine, pastry
case, marble tables, vinyl booth, soccer-pennant decor.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, make_tube, make_chamfer_box
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding, make_wall_with_openings
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.food_service import make_donut_display, make_coffee_pots
from _props.decor import make_wall_clock, make_faded_poster, make_floor_plant
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
    # (2026-10-03: walls CUT round their windows — they were solid behind the panes)
    make_wall_with_openings("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1,
                            openings=[(4.3, 1.65, 1.16, 1.26)])
    make_wall("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S_W", (-3.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(-3.0, 1.60, 1.60, 1.60)])
    make_wall_with_openings("Wall_S_E", (+3.0, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(3.0, 1.60, 1.60, 1.60)])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (4.0, 0.20, 0.60), PAL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10),("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    # (2026-10-03: centred on their wall pieces — at ±2.0, 2.2 wide, half of each hung over the door opening)
    make_window("Window_SW", (-3.0, 0.10, 1.60), width=1.60, height=1.60, room_dir=+1)
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_SE", (+3.0, 0.10, 1.60), width=1.60, height=1.60, room_dir=+1)
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
        make_cyl(f"Table_{ti}_Pedestal", (tx, ty, 0.36), 0.06, 0.72, COL_ESPRESSO_TRIM)   # floor to top (2026-09-23: 2 cm up)
        make_cyl(f"Table_{ti}_Foot", (tx, ty, 0.02), 0.24, 0.04, COL_ESPRESSO_TRIM)
        # 2 chairs per table
        for ci, (cx_off, cy_off) in enumerate([(-0.60, 0), (+0.60, 0)]):
            cx, cy = tx + cx_off, ty + cy_off
            make_cyl(f"Table_{ti}_Chair_{ci}_Seat", (cx, cy, 0.46), 0.20, 0.04, COL_WOOD)
            for lx_ in (-0.14, 0.14):   # bentwood legs (2026-09-23: seats hung 44 cm up on nothing)
                for ly_ in (-0.14, 0.14):
                    make_cyl(f"Table_{ti}_Chair_{ci}_Leg_{lx_:+.2f}_{ly_:+.2f}", (cx + lx_, cy + ly_, 0.22), 0.015, 0.44, COL_WOOD, segments=6)
            make_box(f"Table_{ti}_Chair_{ci}_Back", (cx, cy + (0.18 if cx_off < 0 else -0.18), 0.74), (0.40, 0.04, 0.56), COL_WOOD)
        # Espresso + saucer on each table
        make_cyl(f"Table_{ti}_Saucer", (tx, ty, 0.7625), 0.06, 0.005, P.PAPER)   # on the marble (2026-09-23: 1.8 cm over it)
        make_cyl(f"Table_{ti}_Cup", (tx, ty, 0.795), 0.04, 0.06, P.PAPER)
    # Vinyl booth along east wall
    bx, by = +3.30, 3.0
    make_box("Booth_Seat", (bx, by, 0.40), (0.60, 2.20, 0.10), COL_VINYL_BOOTH)
    make_box("Booth_Base", (bx, by, 0.175), (0.56, 2.16, 0.35), COL_ESPRESSO_TRIM)   # (2026-09-23: seat and back on nothing)
    make_box("Booth_Back", (bx+0.20, by, 0.92), (0.20, 2.20, 1.00), COL_VINYL_BOOTH)
    make_box("Booth_Table", (bx-0.60, by, 0.72), (0.50, 1.40, 0.04), COL_MARBLE)
    make_cyl("Booth_Table_Pedestal", (bx-0.60, by, 0.36), 0.06, 0.72, COL_ESPRESSO_TRIM)
    # The BACK-CORNER table (NW, under its window): water glass, the
    # open notebook, and the croissant in its paper bag.
    ctx, cty = -3.25, 4.25
    make_cyl("CornerTable_Top", (ctx, cty, 0.74), 0.42, 0.04, COL_MARBLE)
    make_cyl("CornerTable_Pedestal", (ctx, cty, 0.36), 0.06, 0.72, COL_ESPRESSO_TRIM)
    make_cyl("CornerTable_Foot", (ctx, cty, 0.02), 0.24, 0.04, COL_ESPRESSO_TRIM)
    for ci2, (cxo, cyo) in enumerate([(0.60, 0.0), (0.0, -0.60)]):
        ccx, ccy = ctx + cxo, cty + cyo
        make_cyl(f"CornerTable_Chair_{ci2}_Seat", (ccx, ccy, 0.46), 0.20, 0.04, COL_WOOD)
        for lx_ in (-0.14, 0.14):   # bentwood legs (2026-09-23: seats hung 44 cm up on nothing)
            for ly_ in (-0.14, 0.14):
                make_cyl(f"CornerTable_Chair_{ci2}_Leg_{lx_:+.2f}_{ly_:+.2f}", (ccx + lx_, ccy + ly_, 0.22), 0.015, 0.44, COL_WOOD, segments=6)
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
    make_wall_clock("Clock", (0.0, 5.900, 2.10), frozen_hour=10, frozen_min=30, facing='-Y')
    make_faded_poster("Poster_W", (-3.8965, 3.0, 1.80), into_room=+1)

def build_ceiling_infra():
    # 2026-08 tail pass: the 3x3 office fluorescent grid was the
    # template leak — the marble-and-pennants idiom takes warm
    # globe pendants over bar and floor.
    for pi2, (px, py) in enumerate([(-2.0, 2.4), (2.0, 2.4), (0.0, 4.6)]):
        make_cyl(f"Globe_{pi2}_Cord", (px, py, CEIL-0.22), 0.008, 0.44, P.METAL_BLACK)
        make_cyl(f"Globe_{pi2}_Sphere", (px, py, CEIL-0.55), 0.14, 0.24, (0.97, 0.90, 0.72, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL))
    make_ceiling_speaker("Speaker", (-1.0, 3.0, CEIL))

def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE HANDS ("She reached across the small metal table and took
    his hand. Briefly. Like a handshake at the end of a
    contract."): residue grammar — a hand-worn patch and a cup
    ring where hands keep landing on Table_0."""
    make_box("Hands_Table_Patch", (-1.85, 0.95, 0.761), (0.14, 0.12, 0.002), (0.62, 0.60, 0.58, 1.0))
    make_cyl("Hands_Cup_Ring", (-2.15, 1.02, 0.7615), 0.045, 0.003, (0.42, 0.34, 0.26, 1.0), segments=10)


def build_pendants_2026_09():
    """Two pendants the scene has lit since 08-02 with nothing hanging
    there (orphan_practical_audit, 2026-09-18): one over the bar's
    middle, one over the seating — bulbs where the practicals are,
    canopies on the ceiling."""
    from _props.furniture import make_pendant
    make_pendant("BarPendant", 0.0, 4.80, 2.60, 3.10, shade_col=(0.18, 0.18, 0.20, 1.0), shade_r=0.17)
    make_pendant("SeatingPendant", 0.0, 1.80, 2.60, 3.10, shade_col=(0.18, 0.18, 0.20, 1.0), shade_r=0.20)


def build_front_and_street_2026_10():
    """THE FRONT AND THE STREET (2026-10-03). The door insert saw "81 %
    sky": the cafe's front was a 4 m hole with nothing beyond it, and
    once the walls were cut round the windows the lens looked straight
    out. A cafe front is a glass door pair in a glazed wall, and a
    Mile End street beyond it: the sidewalk, the curb, the street, the
    facade opposite with its windows, a lamp post, a parked car, a
    street tree."""
    frame = (0.18, 0.18, 0.20, 1.0)
    glass = (0.78, 0.84, 0.86, 0.25)
    # the glazed front: two door leaves in the middle, a fixed light each side
    for nm, x0, x1, door in (("Front_Light_W", -2.0, -1.0, False), ("Front_Door_L", -1.0, 0.0, True), ("Front_Door_R", 0.0, 1.0, True), ("Front_Light_E", 1.0, 2.0, False)):
        cx, w = (x0 + x1) / 2.0, x1 - x0
        make_box(f"{nm}_Glass", (cx, 0.0, 1.20), (w - 0.10, 0.02, 2.30), glass)
        make_box(f"{nm}_Stile_W", (x0 + 0.03, 0.0, 1.20), (0.06, 0.06, 2.40), frame)
        make_box(f"{nm}_Stile_E", (x1 - 0.03, 0.0, 1.20), (0.06, 0.06, 2.40), frame)
        make_box(f"{nm}_Rail_T", (cx, 0.0, 2.37), (w, 0.06, 0.06), frame)
        make_box(f"{nm}_Rail_B", (cx, 0.0, 0.08), (w, 0.06, 0.16), frame)
        if door:
            make_box(f"{nm}_Rail_M", (cx, 0.0, 0.95), (w, 0.06, 0.06), frame)
            make_box(f"{nm}_Pull", (cx + (0.30 if 'L' in nm else -0.30), -0.06, 1.05), (0.03, 0.04, 0.30), P.METAL_STEEL)
            make_box(f"{nm}_Pull_In", (cx + (0.30 if 'L' in nm else -0.30), 0.06, 1.05), (0.03, 0.04, 0.30), P.METAL_STEEL)
    make_box("Front_Sign_Band", (0.0, -0.11, 2.70), (4.0, 0.02, 0.50), (0.16, 0.30, 0.28, 1.0))
    make_box("Front_Sign_Text", (0.0, -0.125, 2.70), (1.80, 0.01, 0.22), (0.92, 0.88, 0.70, 1.0))
    # the street
    make_box("Ground_Sidewalk", (0.0, -2.2, -0.03), (24.0, 4.4, 0.06), (0.60, 0.58, 0.54, 1.0))
    for i in range(1, 12):
        make_box(f"Sidewalk_Joint_{i}", (-12.0 + i * 2.0, -2.2, 0.001), (0.012, 4.4, 0.004), (0.46, 0.44, 0.40, 1.0))
    make_box("Curb", (0.0, -4.45, -0.06), (24.0, 0.14, 0.14), (0.68, 0.66, 0.62, 1.0))
    make_box("Ground_Street", (0.0, -10.0, -0.14), (24.0, 11.0, 0.06), (0.30, 0.30, 0.31, 1.0))
    make_box("Street_Centreline", (0.0, -10.0, -0.108), (24.0, 0.10, 0.004), (0.86, 0.78, 0.40, 1.0))
    make_box("Out_Facade", (0.0, -16.0, 5.0), (26.0, 0.6, 10.0), (0.62, 0.46, 0.34, 1.0))
    for r in range(3):
        for c in range(9):
            make_box(f"Out_Facade_Win_{r}_{c}", (-10.0 + c * 2.5, -15.69, 2.2 + r * 2.9), (1.1, 0.02, 1.6), (0.26, 0.30, 0.36, 1.0))
    make_box("Out_Facade_Shopfront", (0.0, -15.6, 1.4), (26.0, 0.2, 2.8), (0.30, 0.26, 0.24, 1.0))
    # a lamp post, a parked car, a street tree
    make_cyl("Lamp_Post", (-3.2, -4.1, 2.0), 0.06, 4.0, (0.20, 0.22, 0.24, 1.0), segments=8)
    make_cyl("Lamp_Post_Arm", (-3.2, -4.5, 3.9), 0.03, 0.8, (0.20, 0.22, 0.24, 1.0), segments=6, axis='Y')
    make_box("Lamp_Post_Head", (-3.2, -4.9, 3.85), (0.30, 0.50, 0.14), (0.92, 0.88, 0.70, 1.0))
    from _props.vehicles import make_car
    make_car("Parked_Car", 3.0, -6.2, 4.4, (0.30, 0.34, 0.46, 1.0), along="X", z0=-0.11)
    from _props.trees import make_broadleaf
    make_broadleaf("Street_Tree", 5.5, -2.6, 6.0, (0.36, 0.48, 0.26, 1.0), (0.36, 0.28, 0.20, 1.0))
    make_box("Tree_Grate", (5.5, -2.6, 0.001), (1.2, 1.2, 0.004), (0.26, 0.26, 0.28, 1.0))


def build_olimpico_2026_10():
    """CHARACTER PASS (2026-10-03). The chapter: "Café Olimpico on
    Saint-Viateur … the single espresso … the small water glass … the
    small round metal table in the back corner, under the window … A
    shaft of late-morning sunlight fell across the table … the dust
    motes … the bell over the café door … a small table by the front
    window … Marco, the barista … the menu she had already memorized."
    An Italian café in Mile End: the soccer on the TV, tricolour
    bunting, the team photographs, the chalk menu over the bar, cannoli
    and biscotti, sugar and napkins on every table, two more tables,
    the paper rack and the coat stand by the door, a plant, and the
    motes in the back window's light."""
    import random
    rnd = random.Random(19)
    wood = COL_WOOD
    chrome = P.METAL_STEEL
    top = 1.11
    # ── the soccer on the TV, high on the east wall
    ex = ROOM_W / 2.0 - 0.10
    make_box("Cafe_TV", (ex - 0.05, 1.20, 2.35), (0.08, 0.90, 0.54), (0.10, 0.10, 0.12, 1.0))
    make_box("Cafe_TV_Screen", (ex - 0.095, 1.20, 2.35), (0.01, 0.80, 0.45), (0.30, 0.62, 0.34, 1.0))
    make_box("Cafe_TV_Pitch_Line", (ex - 0.10, 1.20, 2.35), (0.004, 0.76, 0.012), (0.90, 0.92, 0.88, 1.0))
    make_box("Cafe_TV_Bracket", (ex - 0.03, 1.20, 2.10), (0.06, 0.20, 0.04), (0.30, 0.30, 0.32, 1.0))
    # ── tricolour bunting along the east wall and over the bar
    make_tube("Bunting_String_E", [(ex - 0.03, 0.4, 2.80), (ex - 0.03, 2.0, 2.66), (ex - 0.03, 3.6, 2.80), (ex - 0.03, 5.2, 2.66)], 0.004, (0.30, 0.28, 0.26, 1.0), segments=4)
    for i in range(16):
        y = 0.55 + i * 0.30
        z = 2.80 - 0.14 * abs(((y - 0.4) % 3.2) / 1.6 - 1.0) * 1.0
        make_box(f"Bunting_E_{i}", (ex - 0.035, y, z - 0.10), (0.01, 0.16, 0.18), [(0.20, 0.56, 0.32, 1.0), (0.94, 0.94, 0.92, 1.0), (0.82, 0.22, 0.22, 1.0)][i % 3])
    # ── the team photographs on the west wall, round the poster
    for i, (y, z, w, h) in enumerate(((1.65, 1.95, 0.30, 0.22), (2.05, 1.60, 0.24, 0.30), (2.35, 2.05, 0.22, 0.18), (3.75, 1.65, 0.28, 0.22), (3.65, 2.10, 0.22, 0.28))):
        make_box(f"Team_Photo_{i}_Frame", (-ROOM_W / 2.0 + 0.115, y, z), (0.025, w, h), (0.20, 0.16, 0.12, 1.0))
        make_box(f"Team_Photo_{i}_Pic", (-ROOM_W / 2.0 + 0.130, y, z), (0.004, w - 0.04, h - 0.04), [(0.58, 0.62, 0.66, 1.0), (0.72, 0.66, 0.54, 1.0), (0.52, 0.60, 0.52, 1.0)][i % 3])
    # ── the chalk menu over the bar, east of the clock
    make_box("Menu_Board_Frame", (2.9, ROOM_D - 0.11, 2.20), (0.96, 0.02, 0.70), wood)
    make_box("Menu_Board", (2.9, ROOM_D - 0.125, 2.20), (0.88, 0.01, 0.62), (0.12, 0.14, 0.12, 1.0))
    for i in range(7):
        make_box(f"Menu_Line_{i}", (2.9 + rnd.uniform(-0.06, 0.06), ROOM_D - 0.132, 2.44 - i * 0.08), (0.40 + rnd.uniform(-0.12, 0.18), 0.002, 0.022), [(0.92, 0.88, 0.70, 1.0), (0.96, 0.60, 0.60, 1.0), (0.70, 0.90, 0.96, 1.0)][i % 3])
        make_box(f"Menu_Price_{i}", (3.24, ROOM_D - 0.132, 2.44 - i * 0.08), (0.08, 0.002, 0.018), (0.92, 0.88, 0.70, 1.0))
    # ── on the bar: cannoli on a tray, the biscotti jar, a tip jar, the sugar station
    make_box("Cannoli_Tray", (1.20, 4.72, top + 0.01), (0.40, 0.26, 0.02), chrome)
    for i in range(5):
        make_cyl(f"Cannolo_{i}", (1.05 + i * 0.075, 4.72 + (i % 2) * 0.06, top + 0.045), 0.022, 0.12, (0.86, 0.72, 0.46, 1.0), segments=8, axis='Y')
        make_cyl(f"Cannolo_{i}_Cream", (1.05 + i * 0.075, 4.72 + (i % 2) * 0.06 + 0.066, top + 0.045), 0.018, 0.008, (0.96, 0.94, 0.88, 1.0), segments=8, axis='Y')
    make_cyl("Biscotto_Jar", (0.80, 4.70, top + 0.11), 0.07, 0.22, (0.80, 0.86, 0.88, 0.5), segments=10)
    for i in range(6):
        make_box(f"Biscotto_{i}", (0.80 + rnd.uniform(-0.03, 0.03), 4.70 + rnd.uniform(-0.03, 0.03), top + 0.06 + i * 0.025), (0.09, 0.025, 0.02), (0.78, 0.60, 0.34, 1.0))
    make_cyl("Biscotto_Lid", (0.80, 4.70, top + 0.225), 0.072, 0.012, chrome, segments=10)
    make_cyl("Cafe_Tip_Jar", (-0.90, 4.68, top + 0.07), 0.05, 0.14, (0.80, 0.86, 0.88, 0.5), segments=10)
    make_box("Cafe_Tip_Bills", (-0.90, 4.68, top + 0.04), (0.06, 0.04, 0.07), (0.56, 0.62, 0.50, 1.0))
    make_box("Sugar_Station", (-1.50, 4.70, top + 0.03), (0.22, 0.14, 0.06), (0.40, 0.30, 0.20, 1.0))
    for i in range(3):
        make_box(f"Sugar_Packets_{i}", (-1.58 + i * 0.08, 4.70, top + 0.085), (0.05, 0.10, 0.05), [(0.94, 0.92, 0.86, 1.0), (0.86, 0.60, 0.34, 1.0), (0.94, 0.92, 0.86, 1.0)][i])
    # ── sugar and napkins on every table
    for i, (tx, ty, tz) in enumerate(((-2.0, 0.95, 0.76), (2.0, 1.80, 0.76), (-3.25, 4.25, 0.76), (0.0, 3.30, 0.76), (-2.30, 3.00, 0.76))):
        make_cyl(f"Table_Sugar_{i}", (tx + 0.26, ty - 0.20, tz + 0.055), 0.025, 0.11, (0.80, 0.86, 0.88, 0.6), segments=8)
        make_cyl(f"Table_Sugar_{i}_Top", (tx + 0.26, ty - 0.20, tz + 0.118), 0.027, 0.016, chrome, segments=8)
        make_box(f"Table_Napkins_{i}", (tx - 0.24, ty - 0.22, tz + 0.05), (0.12, 0.08, 0.10), chrome)
        make_box(f"Table_Napkins_{i}_Paper", (tx - 0.24, ty - 0.265, tz + 0.05), (0.09, 0.004, 0.07), (0.94, 0.94, 0.90, 1.0))
    # ── two more round tables with their chairs
    for ti, (tx, ty) in enumerate(((0.0, 3.30), (-2.30, 3.00))):
        make_cyl(f"More_Table_{ti}_Top", (tx, ty, 0.74), 0.42, 0.04, COL_MARBLE)
        make_cyl(f"More_Table_{ti}_Pedestal", (tx, ty, 0.36), 0.06, 0.72, COL_ESPRESSO_TRIM)
        make_cyl(f"More_Table_{ti}_Foot", (tx, ty, 0.02), 0.24, 0.04, COL_ESPRESSO_TRIM)
        for ci, cx_off in enumerate((-0.60, 0.60)):
            cx, cy = tx + cx_off, ty
            make_cyl(f"More_Table_{ti}_Chair_{ci}_Seat", (cx, cy, 0.46), 0.20, 0.04, COL_WOOD)
            for lx_ in (-0.14, 0.14):
                for ly_ in (-0.14, 0.14):
                    make_cyl(f"More_Table_{ti}_Chair_{ci}_Leg_{lx_:+.2f}_{ly_:+.2f}", (cx + lx_, cy + ly_, 0.22), 0.015, 0.44, COL_WOOD, segments=6)
            make_box(f"More_Table_{ti}_Chair_{ci}_Back", (cx + (-0.18 if cx_off < 0 else 0.18), cy, 0.74), (0.04, 0.40, 0.56), COL_WOOD)
        make_cyl(f"More_Table_{ti}_Saucer", (tx - 0.05, ty + 0.08, 0.7625), 0.06, 0.005, P.PAPER)
        make_cyl(f"More_Table_{ti}_Cup", (tx - 0.05, ty + 0.08, 0.795), 0.04, 0.06, P.PAPER)
    # ── by the door: the paper rack, the coat stand; a plant in the north-east corner
    make_box("Paper_Rack_Frame", (1.60, 0.45, 0.45), (0.40, 0.22, 0.90), (0.30, 0.30, 0.32, 1.0))
    for i in range(3):
        make_box(f"Paper_{i}", (1.60, 0.36 + i * 0.03, 0.30 + i * 0.26), (0.30, 0.02, 0.26), [(0.90, 0.88, 0.82, 1.0), (0.86, 0.84, 0.78, 1.0), (0.92, 0.90, 0.84, 1.0)][i])
        make_box(f"Paper_{i}_Masthead", (1.60, 0.345 + i * 0.03, 0.40 + i * 0.26), (0.24, 0.002, 0.03), (0.20, 0.20, 0.24, 1.0))
    # (east of the door, beside the paper rack — west of it the jacket hung over Table_0)
    make_cyl("Coat_Stand_Base", (1.20, 0.40, 0.02), 0.18, 0.04, (0.20, 0.18, 0.16, 1.0), segments=10)
    make_cyl("Coat_Stand_Pole", (1.20, 0.40, 0.90), 0.02, 1.76, (0.20, 0.18, 0.16, 1.0), segments=8)
    for i in range(4):
        import math
        a = i * 1.5708
        make_cyl(f"Coat_Stand_Hook_{i}", (1.20 + 0.08 * math.cos(a), 0.40 + 0.08 * math.sin(a), 1.72), 0.012, 0.16, (0.20, 0.18, 0.16, 1.0), segments=5, axis='X' if i % 2 == 0 else 'Y')
    # a long coat on the stand, to the base (a short jacket "hung above" the base for the grammar gate)
    make_chamfer_box("Coat_Stand_Coat", (1.20, 0.40, 0.88), (0.22, 0.26, 1.64), (0.26, 0.30, 0.40, 1.0), chamfer=0.03)
    make_chamfer_box("Coat_Stand_Coat_Collar", (1.20, 0.40, 1.72), (0.26, 0.30, 0.08), (0.22, 0.26, 0.36, 1.0), chamfer=0.02)
    make_floor_plant("Cafe_Plant", (3.55, 5.45, 0.0))
    # ── the motes in the back window's shaft of light
    for i in range(9):
        make_cyl(f"Mote_{i}", (-3.1 + rnd.uniform(-0.3, 0.3), 3.9 + rnd.uniform(-0.4, 0.5), 1.0 + rnd.uniform(0.0, 0.9)), 0.006, 0.006, (0.96, 0.92, 0.80, 0.75), segments=6)


def main():
    clear_scene(); build_shell(); build_bar_counter(); build_seating(); build_pennants_and_decor(); build_ceiling_infra()
    build_hero_props_2026_09()
    build_pendants_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/cafe_olimpico.glb"))
    print(f"\n[build_cafe_olimpico] exporting to {out}")
    build_front_and_street_2026_10()
    build_olimpico_2026_10()
    export_glb(out)

if __name__ == "__main__": main()
