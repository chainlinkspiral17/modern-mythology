"""caldwell_porch_night — vol5-7 locale (auto-generated placement script).

DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3, 7 placements): turned
balusters on a bottom rail, both rockers on curved runners with turned
legs, the carriage lamp as a caged housing with a cap and a bulb, the
side table on turned legs with stretchers, spokes and hubs on Maya's
bike, the slow car from the vehicle kit; the porch's first WEAR (two
paths, runner arcs, cup rings, the mat's scuff, the rail worn where
hands go); D3 (switch, conduit, hose bib); D5 (a hedge, the streetlamp
down the block, the houses across).

DRAFT 5 targets: the screen door as mesh on a frame with a spring; the
logs with bark; the hanging planter's chain; the street lamp's sodium
practical for the nine-fifty-three car; Deck: night establish and
`insert radio`.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe,
                             make_tube, make_rot_box, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 6.0; ROOM_D = 4.0; CEIL = 2.8
PAL_WALL = {"wall":(0.62,0.46,0.32,1.0),"baseboard":(0.32,0.22,0.14,1.0)}
COL_FLOOR = (0.42,0.30,0.20,1.0); COL_SEAM = (0.22,0.14,0.10,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.96,0.62,0.32,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)

def build_railing():
    make_chamfer_box("Rail_Top", (0.0, 0.10, 1.00), (ROOM_W-1.0, 0.08, 0.05), COL_WOOD, chamfer=0.01)
    make_box("Rail_Bottom", (0.0, 0.10, 0.10), (ROOM_W-1.0, 0.05, 0.04), COL_WOOD)
    for vi in range(10):
        vx = -(ROOM_W-1.0)/2.0+vi*0.6
        make_lathe(f"Rail_Bal_{vi}", (vx, 0.10, 0.12), [(0.022, 0.0), (0.022, 0.10), (0.032, 0.16), (0.02, 0.24), (0.026, 0.42), (0.02, 0.60), (0.03, 0.70), (0.022, 0.78), (0.022, 0.86)], COL_WOOD, segments=8)

def _make_rocker(prefix, cx, cy):
    """Compound rocking chair — seat faces south (toward the railing),
    back at +Y with spindles, armrests, four legs, two curved runners."""
    make_chamfer_box(f"{prefix}_Seat", (cx, cy, 0.46), (0.50, 0.46, 0.05), COL_WOOD)
    make_chamfer_box(f"{prefix}_Back", (cx, cy+0.22, 0.76), (0.48, 0.04, 0.56), COL_WOOD)
    for si in range(4):
        sx = cx - 0.18 + si*0.12
        make_box(f"{prefix}_Spindle_{si}", (sx, cy+0.22, 0.74), (0.02, 0.03, 0.50), COL_ACCENT)
    for ai, ax in enumerate((cx-0.26, cx+0.26)):
        make_box(f"{prefix}_Arm_{ai}", (ax, cy-0.02, 0.64), (0.05, 0.44, 0.04), COL_WOOD)
        make_box(f"{prefix}_ArmPost_{ai}", (ax, cy-0.20, 0.55), (0.04, 0.04, 0.18), COL_WOOD)
    for k,(ox,oy) in enumerate([(-0.22,-0.20),(0.22,-0.20),(-0.22,0.20),(0.22,0.20)]):
        make_lathe(f"{prefix}_Leg_{k}", (cx+ox, cy+oy, 0.03), [(0.018, 0.0), (0.024, 0.12), (0.016, 0.28), (0.022, 0.41)], COL_WOOD, segments=6)
    # curved runners (draft 4, 2026-09-18), rails leg to leg
    for ri, rx in enumerate((cx-0.22, cx+0.22)):
        make_tube(f"{prefix}_Runner_{ri}", [(rx, cy-0.42, 0.10), (rx, cy-0.25, 0.035), (rx, cy, 0.02), (rx, cy+0.25, 0.035), (rx, cy+0.42, 0.10)], 0.02, COL_WOOD, segments=6)
    for si, sy in enumerate((cy-0.20, cy+0.20)):
        make_tube(f"{prefix}_Stretcher_{si}", [(cx-0.22, sy, 0.20), (cx+0.22, sy, 0.20)], 0.012, COL_WOOD, segments=5)

def build_chairs():
    for ci, cx in enumerate([-1.5, +1.5]):
        _make_rocker(f"Rocker_{ci}", cx, ROOM_D/2.0)

def build_door():
    make_box("ScreenDoor_Frame", (0.0, 0.0, 1.05), (1.00, 0.04, 2.10), COL_WOOD)
    make_box("ScreenDoor_Screen", (0.0, 0.03, 1.05), (0.80, 0.01, 1.90), (0.28,0.30,0.26,1.0))

def build_porchlamp():
    # Wall-mounted carriage lamp: bracket, glass housing, warm bulb.
    make_box("PorchLamp_Bracket", (-1.5, 0.16, CEIL-0.66), (0.05, 0.20, 0.05), P.METAL_BLACK)
    make_tube("PorchLamp_Housing", [(-1.5-0.09, 0.30-0.09, CEIL-0.82), (-1.5-0.09, 0.30-0.09, CEIL-0.50)], 0.006, P.METAL_BLACK, segments=4)
    for ci2, (ux, uy) in enumerate(((1, -1), (-1, 1), (1, 1))):
        make_tube(f"PorchLamp_Housing_{ci2}", [(-1.5+ux*0.09, 0.30+uy*0.09, CEIL-0.82), (-1.5+ux*0.09, 0.30+uy*0.09, CEIL-0.50)], 0.006, P.METAL_BLACK, segments=4)
    make_lathe("PorchLamp_Cap", (-1.5, 0.30, CEIL-0.50), [(0.12, 0.0), (0.06, 0.06), (0.02, 0.10), (0.0, 0.10)], P.METAL_BLACK, segments=8)
    make_lathe("PorchLamp_Foot", (-1.5, 0.30, CEIL-0.84), [(0.0, 0.0), (0.10, 0.0), (0.10, 0.02), (0.0, 0.02)], P.METAL_BLACK, segments=8)
    make_box("PorchLamp_Glass", (-1.5, 0.30, CEIL-0.66), (0.14, 0.14, 0.30), P.GLASS_WARM)
    make_lathe("PorchLamp_Bulb", (-1.5, 0.30, CEIL-0.76), [(0.0, 0.0), (0.025, 0.01), (0.03, 0.05), (0.018, 0.09), (0.0, 0.10)], COL_ACCENT, segments=8)

def build_dressing():
    # Side table between the rockers, with a mug and a folded paper.
    tx, ty = 0.0, ROOM_D/2.0
    make_chamfer_box("SideTable_Top", (tx, ty, 0.52), (0.44, 0.44, 0.04), COL_WOOD, chamfer=0.01)
    for k,(ox,oy) in enumerate([(-0.18,-0.18),(0.18,-0.18),(-0.18,0.18),(0.18,0.18)]):
        make_lathe(f"SideTable_Leg_{k}", (tx+ox, ty+oy, 0.0), [(0.018, 0.0), (0.024, 0.05), (0.016, 0.12), (0.022, 0.30), (0.026, 0.38), (0.02, 0.50)], COL_WOOD, segments=6)
    for si2, (a, b) in enumerate((((-0.18, -0.18), (0.18, -0.18)), ((-0.18, 0.18), (0.18, 0.18)))):
        make_tube(f"SideTable_Stretcher_{si2}", [(tx+a[0], ty+a[1], 0.16), (tx+b[0], ty+b[1], 0.16)], 0.01, COL_WOOD, segments=5)
    # Canon (vol6 ch21): "two glasses of iced tea — the one she
    # poured for herself and the one she poured for Maya"
    for gi, gx in enumerate((tx-0.10, tx+0.08)):
        make_cyl(f"IcedTea_Glass_{gi}", (gx, ty-0.05, 0.61), 0.04, 0.14,
                 (0.62,0.52,0.34,0.8))
        make_cyl(f"IcedTea_Ice_{gi}", (gx, ty-0.05, 0.66), 0.032, 0.03,
                 (0.86,0.88,0.86,0.9), segments=6)
    make_box("Paper", (tx+0.12, ty+0.12, 0.55), (0.20, 0.14, 0.03), P.NEWSPRINT)
    # Maya's bike, leaned at the porch's east end past the railing
    # Leaned AGAINST the east rail, not through it (the rear
    # wheel at bx+0.50 reached the wall plane).
    bx, by = 2.15, 0.35   # rear wheel and its spokes clear of the east wall (2026-09-18)
    for wx in (bx-0.50, bx+0.50):
        make_cyl(f"MayaBike_Wheel_{wx:.1f}", (wx, by, 0.33), 0.32, 0.04,
                 P.METAL_BLACK, segments=14, axis='Y')
        make_cyl(f"MayaBike_Hub_{wx:.1f}", (wx, by, 0.33), 0.05, 0.06, (0.62, 0.64, 0.66, 1.0), segments=8, axis='Y')
        for sk in range(6):
            ang = sk * 0.5236
            import math as _mm
            make_tube(f"MayaBike_Spoke_{wx:.1f}_{sk}", [(wx - 0.28 * _mm.cos(ang), by, 0.33 - 0.28 * _mm.sin(ang)), (wx + 0.28 * _mm.cos(ang), by, 0.33 + 0.28 * _mm.sin(ang))], 0.003, (0.62, 0.64, 0.66, 1.0), segments=4)
    make_box("MayaBike_TopBar", (bx, by, 0.60), (0.70, 0.03, 0.04), (0.30,0.42,0.55,1.0))
    make_box("MayaBike_DownBar", (bx-0.12, by, 0.47), (0.52, 0.03, 0.04), (0.30,0.42,0.55,1.0))
    make_box("MayaBike_SeatPost", (bx-0.28, by, 0.68), (0.03, 0.03, 0.16), (0.30,0.42,0.55,1.0))   # (2026-09-22: seat, bars and basket hung loose)
    make_box("MayaBike_HeadTube", (bx+0.36, by, 0.70), (0.03, 0.03, 0.20), (0.30,0.42,0.55,1.0))
    make_chamfer_box("MayaBike_Seat", (bx-0.28, by, 0.76), (0.15, 0.06, 0.05), P.METAL_BLACK)
    make_box("MayaBike_Bars", (bx+0.36, by, 0.80), (0.05, 0.28, 0.04), P.METAL_BLACK)
    make_chamfer_box("MayaBike_Basket", (bx+0.47, by, 0.62), (0.20, 0.24, 0.16), (0.46,0.36,0.24,1.0))
    # Doormat at the door.
    make_box("Doormat", (0.0, 0.55, 0.02), (0.90, 0.55, 0.03), P.RUBBER_MAT)
    make_box("Doormat_Trim", (0.0, 0.55, 0.03), (0.78, 0.44, 0.02), (0.36,0.30,0.22,1.0))
    # Cordwood stack in the NW corner (logs along X, pyramid rows).
    lx0, ly0 = -ROOM_W/2.0+0.45, ROOM_D-0.7
    for r, n in enumerate((4,3,2)):
        for c in range(n):
            col = (0.52,0.38,0.26,1.0) if (r+c)%2 else (0.42,0.30,0.20,1.0)
            make_cyl(f"Log_{r}_{c}", (lx0, ly0 - 0.16*(n-1)/2.0 + c*0.16, 0.07+r*0.14),   # on the deck, log on log
                     0.07, 0.52, col, axis='X', segments=8)
    # Potted plant in the NE corner (wire the imported helper).
    make_floor_plant("PorchPlant", (ROOM_W/2.0-0.5, ROOM_D-0.6, 0.0),
                     palette={"leaf":(0.34,0.46,0.30,1.0),"pot":(0.56,0.36,0.24,1.0)})
    # Hanging planter over the railing on the east side.
    hx, hy = 1.5, 0.62
    make_cyl("HangWire", (hx, hy, CEIL-0.36), 0.005, 0.72, P.METAL_BLACK)   # ceiling to pot rim (2026-09-22: 3 cm short)
    make_cyl("HangPot", (hx, hy, CEIL-0.80), 0.14, 0.16, (0.56,0.36,0.24,1.0))
    for i,(dx,dy) in enumerate([(0.14,0.0),(0.07,0.121),(-0.07,0.121),(-0.14,0.0),(-0.07,-0.121),(0.07,-0.121)]):
        make_cyl(f"HangLeaf_{i}", (hx+dx, hy+dy, CEIL-0.95), 0.03, 0.16, (0.36,0.48,0.32,1.0))   # from the pot rim, not through it (2026-09-22)

def build_ceiling_infra():
    # A porch gets a ceiling fan, not office fluorescents (the tube
    # fixtures were interior boilerplate — a wrong-room tell on a
    # Texas porch; the carriage lamp is the practical).
    fx, fy = 0.0, ROOM_D/2.0
    make_cyl("Fan_Downrod", (fx, fy, CEIL-0.12), 0.025, 0.24, P.METAL_BLACK, segments=6)
    make_cyl("Fan_Hub", (fx, fy, CEIL-0.28), 0.10, 0.10, P.METAL_BLACK, segments=10)
    for bi, (dx, dy) in enumerate([(0.55,0.0),(-0.55,0.0),(0.0,0.55),(0.0,-0.55)]):
        make_box(f"Fan_Blade_{bi}", (fx+dx, fy+dy, CEIL-0.30),
                 (0.92 if dy==0.0 else 0.20, 0.20 if dy==0.0 else 0.92, 0.025),   # into the hub (2026-09-22: 9 cm short)
                 (0.40,0.30,0.22,1.0))

def build_porch_props_2026_08():
    """The night-porch cues that had no objects: the radio (a
    porch evening runs on one), the blanket, the cake, the photo.
    All at the side table + rail — a porch gathering's props."""
    tx, ty = 0.0, ROOM_D/2.0
    # Transistor radio on the rail, antenna up at an angle (two
    # segments), dial face lit-warm.
    # ON the rail's top (y 0.06..0.14, z 1.025); 2026-09-22 it hung 11 cm
    # off the rail, 15 cm over nothing
    make_box("Radio_Body", (1.45, 0.145, 1.095), (0.24, 0.09, 0.14), (0.32, 0.26, 0.22, 1.0))
    make_box("Radio_Dial", (1.40, 0.097, 1.105), (0.09, 0.006, 0.07), (0.90, 0.80, 0.55, 1.0))
    make_cyl("Radio_Antenna_A", (1.55, 0.165, 1.255), 0.006, 0.18, (0.62, 0.64, 0.66, 1.0), segments=6)
    make_cyl("Radio_Antenna_B", (1.562, 0.18, 1.395), 0.005, 0.14, (0.62, 0.64, 0.66, 1.0), segments=6)
    # The blanket over a chair back, one corner hanging lower.
    # over Rocker_0's back (cx -1.5, back at cy + 0.22; 2026-09-22 it hung 30 cm in front of it)
    make_box("Blanket_Fold", (-1.35, ROOM_D/2.0 + 0.22, 0.78), (0.55, 0.16, 0.10), (0.52, 0.36, 0.30, 1.0))
    make_box("Blanket_Drop", (-1.35, ROOM_D/2.0 + 0.175, 0.52), (0.50, 0.05, 0.42), (0.49, 0.34, 0.28, 1.0))
    make_box("Blanket_Corner", (-1.15, ROOM_D/2.0 + 0.18, 0.30), (0.16, 0.04, 0.16), (0.46, 0.32, 0.27, 1.0))
    # The cake on its plate at the side table, two slices gone —
    # a porch cake is a cake being eaten.
    make_cyl("Cake_Plate", (tx + 0.10, ty + 0.10, 0.545), 0.13, 0.012, (0.90, 0.88, 0.84, 1.0), segments=12)
    make_cyl("Cake_Body", (tx + 0.10, ty + 0.10, 0.585), 0.095, 0.07, (0.82, 0.72, 0.52, 1.0), segments=12)
    make_box("Cake_CutGap", (tx + 0.175, ty + 0.155, 0.585), (0.075, 0.075, 0.072), (0.70, 0.58, 0.40, 1.0))
    make_cyl("Cake_Frosting", (tx + 0.10, ty + 0.10, 0.625), 0.098, 0.012, (0.92, 0.90, 0.86, 1.0), segments=12)
    # The photo: a small framed print leaning against the tea
    # pitcher's side of the table — brought out to be shown.
    make_box("Photo_Frame", (tx - 0.14, ty + 0.12, 0.60), (0.10, 0.014, 0.13), (0.40, 0.30, 0.22, 1.0))
    make_box("Photo_Print", (tx - 0.14, ty + 0.128, 0.60), (0.084, 0.004, 0.112), (0.78, 0.74, 0.66, 1.0))
    make_box("Photo_Figures", (tx - 0.145, ty + 0.131, 0.585), (0.05, 0.002, 0.05), (0.40, 0.38, 0.34, 1.0))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE CAR ("A car comes down the street at nine fifty-three ...
    going slow"): the porch had no street — a front yard strip, a
    street strip, and the slow car on it, headlights toward the
    house. MAYA'S PHONE (the stoplight buzz, remembered on the
    porch) on the rail top."""
    make_box("Front_Yard", (0.0, -2.2, -0.03), (12.0, 3.6, 0.05), (0.14, 0.20, 0.13, 1.0))
    make_box("Street_Strip", (0.0, -6.0, -0.03), (12.0, 4.0, 0.05), (0.26, 0.26, 0.28, 1.0))
    from _props.vehicles import make_car
    make_car("Slow_Car", 1.5, -6.0, 4.4, (0.24, 0.26, 0.30, 1.0), along="X", z0=-0.005)   # draft 4: the kit car, going slow
    make_box("Mayas_Phone", (1.9, 0.10, 1.0355), (0.14, 0.07, 0.011), (0.13, 0.13, 0.15, 1.0))


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; 7 placements).
    WEAR (the door to the rockers, the runners' arcs, cup rings on the
    side table, the mat's scuff, the rail worn pale where hands go);
    D3 (the porch light's switch by the door, its conduit up the post,
    the hose bib); D5 (a hedge along the yard's edge, the streetlamp
    down the block, the houses across).
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_light_switch, make_far_bands
    floor_dk = (0.36, 0.25, 0.16, 1.0)
    cy = ROOM_D/2.0
    make_traffic_wear("Wear_Path_Entry_A", [(0.0, 0.5), (-0.6, 1.2), (-1.3, 1.6)], width=0.45, tint=floor_dk)
    make_traffic_wear("Wear_Path_Entry_B", [(0.0, 0.5), (0.6, 1.2), (1.3, 1.6)], width=0.45, tint=floor_dk)
    for ci, cx in enumerate([-1.5, 1.5]):
        for ri, rx in enumerate((cx-0.22, cx+0.22)):
            make_box(f"Wear_Arc_{ci}_{ri}", (rx, cy, 0.006), (0.06, 0.95, 0.004), (0.50, 0.38, 0.27, 1.0))
    make_cyl("Wear_CupRing_A", (-0.12, cy - 0.12, 0.542), 0.04, 0.003, (0.42, 0.30, 0.18, 1.0), segments=10)
    make_cyl("Wear_CupRing_B", (0.14, cy + 0.14, 0.542), 0.04, 0.003, (0.42, 0.30, 0.18, 1.0), segments=10)
    make_scuff_band("Wear_Scuff_Threshold", (0.0, 0.29), 0.80, axis='X', height=0.03, band_z=0.02, tint=(0.26, 0.19, 0.13, 1.0))
    make_box("Wear_Rail_Hands", (-0.9, 0.10, 1.027), (0.60, 0.06, 0.004), (0.52, 0.40, 0.28, 1.0))
    make_light_switch("Switch_1", (0.75, ROOM_D), axis='X', face_sign=-1, z=1.20, aged=True)
    make_tube("Conduit_1", [(-ROOM_W/2.0 + 0.10, 0.20, 0.30), (-ROOM_W/2.0 + 0.10, 0.20, CEIL - 0.05), (-1.6, 0.20, CEIL - 0.05)], 0.01, (0.36, 0.36, 0.38, 1.0), segments=5)
    make_cyl("Hose_Bib", (2.60, ROOM_D - 0.10, 0.45), 0.02, 0.12, (0.62, 0.60, 0.56, 1.0), axis='Y', segments=6)
    # D5
    for hi in range(9):
        hx = -5.6 + hi * 1.4
        from _props.geometry import make_blob
        make_blob(f"Hedge_{hi}", (hx, -1.0, 0.45), 0.7, (0.24, 0.36, 0.20, 1.0), noise=0.18, seed=40 + hi, squash=0.7)
    make_lathe("Street_Lamp_Post", (7.5, -4.4, -0.03), [(0.14, 0.0), (0.09, 0.10), (0.06, 5.6), (0.07, 5.8), (0.0, 5.8)], (0.24, 0.24, 0.26, 1.0), segments=8)
    make_lathe("Street_Lamp_Head", (7.5, -4.4, 5.72), [(0.0, 0.0), (0.12, 0.05), (0.16, 0.18), (0.0, 0.22)], (0.98, 0.84, 0.50, 1.0), segments=10)
    make_far_bands("Far", (0.42, 0.38, 0.36, 1.0), [(11.0, 12.0, 4.5, 0.85), (18.0, 16.0, 6.0, 0.7)], sides="S", cy=0.0, profile="roofline")


def main():
    clear_scene()
    build_shell()
    build_railing()
    build_chairs()
    build_door()
    build_porchlamp()
    build_dressing()
    build_ceiling_infra()
    build_porch_props_2026_08()
    build_hero_props_2026_09()
    build_draft4_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_porch_night.glb"))
    print(f"\n[build_caldwell_porch_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
