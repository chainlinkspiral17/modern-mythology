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
import os, sys, math
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
POST_XS = (-2.90, -1.725, -0.55, 0.55, 1.725, 2.90)   # the south posts: corners, mid, the door
PAL_WALL = {"wall":(0.62,0.46,0.32,1.0),"baseboard":(0.32,0.22,0.14,1.0)}
COL_FLOOR = (0.42,0.30,0.20,1.0); COL_SEAM = (0.22,0.14,0.10,1.0); COL_WOOD = (0.42,0.30,0.18,1.0)
COL_ACCENT = (0.96,0.62,0.32,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # A PORCH, NOT A ROOM (2026-10-08): it was walled on three sides to the
    # ceiling — on the contact sheet an orange box with a fan in it, the
    # railing standing inside its south wall. Now the house wall (N) and
    # the roof on posts and header beams, open west, east and south, the
    # night past the railings.
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for pi_, px in enumerate(POST_XS):
        make_box(f"Porch_Post_{pi_}", (px, 0.10, (CEIL - 0.20) / 2.0), (0.12, 0.12, CEIL - 0.20), COL_WOOD)
    for e in (-1, 1):
        make_box(f"Porch_Post_N_{e:+d}", (e * (ROOM_W/2.0 - 0.10), ROOM_D - 0.16, (CEIL - 0.20) / 2.0), (0.12, 0.12, CEIL - 0.20), COL_WOOD)
        make_box(f"Porch_Beam_{'W' if e < 0 else 'E'}", (e * (ROOM_W/2.0 - 0.10), (0.04 + ROOM_D - 0.10) / 2.0, CEIL - 0.10),
                 (0.14, ROOM_D - 0.14, 0.20), COL_WOOD)
    make_box("Porch_Beam_S", (0.0, 0.10, CEIL - 0.10), (ROOM_W - 0.06, 0.14, 0.20), COL_WOOD)
    make_box("Porch_Fascia", (0.0, -0.02, CEIL + 0.02), (ROOM_W + 0.40, 0.04, 0.26), (0.90, 0.88, 0.82, 1.0))

BAL = [(0.022, 0.0), (0.022, 0.10), (0.032, 0.16), (0.02, 0.24), (0.026, 0.42), (0.02, 0.60), (0.03, 0.70), (0.022, 0.78), (0.022, 0.86)]


def _rail_run(tag, a, b, fixed, axis):
    """A railing between two posts: top and bottom rails, turned balusters."""
    L, mid = b - a, (a + b) / 2.0
    if axis == 'X':
        make_chamfer_box(f"{tag}_Top", (mid, fixed, 1.00), (L, 0.08, 0.05), COL_WOOD, chamfer=0.01)
        make_box(f"{tag}_Bottom", (mid, fixed, 0.10), (L, 0.05, 0.04), COL_WOOD)
    else:
        make_chamfer_box(f"{tag}_Top", (fixed, mid, 1.00), (0.08, L, 0.05), COL_WOOD, chamfer=0.01)
        make_box(f"{tag}_Bottom", (fixed, mid, 0.10), (0.05, L, 0.04), COL_WOOD)
    n = max(1, int(L / 0.30))
    for vi in range(n):
        t = a + (vi + 0.5) * L / n
        make_lathe(f"{tag}_Bal_{vi}", (t, fixed, 0.12) if axis == 'X' else (fixed, t, 0.12), BAL, COL_WOOD, segments=8)


def build_railing():
    # the south run split at the screen door, post to post; the open
    # west and east sides railed post to house
    xs = POST_XS
    for k in range(len(xs) - 1):
        a, b = xs[k] + 0.06, xs[k + 1] - 0.06
        if a < 0.0 < b:          # the door's opening
            continue
        _rail_run(f"Rail_S_{k}", a, b, 0.10, 'X')
    for e in (-1, 1):
        _rail_run(f"Rail_{'W' if e < 0 else 'E'}", 0.16, ROOM_D - 0.22, e * (ROOM_W/2.0 - 0.10), 'Y')

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

WICKER = (0.76, 0.62, 0.42, 1.0); WICKER_DK = (0.58, 0.46, 0.30, 1.0)


def _wicker_chair(prefix, wx, wy):
    """Linda's wicker chair (ch12/ch19: "Linda in the wicker"), facing the
    railing (-Y): a woven skirt, a floral cushion, arms, the fan back."""
    make_chamfer_box(f"{prefix}_Skirt", (wx, wy, 0.20), (0.66, 0.60, 0.40), WICKER, chamfer=0.04)
    for k in range(4):
        make_box(f"{prefix}_Weave_{k}", (wx, wy - 0.3005, 0.06 + k * 0.09), (0.60, 0.002, 0.012), WICKER_DK)
    make_chamfer_box(f"{prefix}_Seat", (wx, wy - 0.03, 0.44), (0.54, 0.50, 0.08), (0.80, 0.56, 0.52, 1.0), chamfer=0.03)
    make_box(f"{prefix}_Back", (wx, wy + 0.25, 0.61), (0.66, 0.10, 0.42), WICKER)
    make_cyl(f"{prefix}_Back_Fan", (wx, wy + 0.25, 0.98), 0.38, 0.08, WICKER, axis='Y', segments=20)
    for k, r in enumerate((0.30, 0.20)):
        make_cyl(f"{prefix}_Back_Fan_Ring_{k}", (wx, wy + 0.209 - k * 0.002, 0.98), r, 0.002, WICKER_DK, axis='Y', segments=18)
    for e in (-1, 1):
        make_box(f"{prefix}_Arm_{e:+d}", (wx + e * 0.30, wy - 0.02, 0.64), (0.08, 0.54, 0.06), WICKER)
        make_box(f"{prefix}_Arm_{e:+d}_Post", (wx + e * 0.30, wy - 0.25, 0.505), (0.06, 0.06, 0.21), WICKER_DK)


def build_chairs():
    """The porch's three chairs (ch19: "Linda in the wicker, Maya in the
    second porch chair, two iced teas on the small table, the third pulled
    out and waiting") — it had two rockers (2026-10-08)."""
    from _props.furniture import make_chair
    _wicker_chair("Wicker_Chair", -1.40, ROOM_D/2.0)
    make_chair("Porch_Chair_Maya", 1.10, ROOM_D/2.0, yaw=3.1416, wood=(0.90, 0.90, 0.86, 1.0))
    make_chair("Porch_Chair_Third", -0.40, ROOM_D/2.0 + 0.58, yaw=3.40, wood=(0.90, 0.90, 0.86, 1.0))   # pulled out at the table, clear of the front door's swing

def build_door():
    # the frame as a ring between the door posts, the screen see-through
    from _props.structure import make_frame_ring
    make_frame_ring("ScreenDoor_Frame", (0.0, 0.10, 1.05), (0.98, 0.06, 2.10), COL_WOOD, bar=0.10)
    make_box("ScreenDoor_Screen", (0.0, 0.10, 1.05), (0.78, 0.01, 1.90), (0.28, 0.30, 0.26, 0.35))
    make_box("ScreenDoor_KickRail", (0.0, 0.09, 0.40), (0.78, 0.03, 0.08), COL_WOOD)

def build_porchlamp():
    LX = -1.725   # on the mid post (2026-10-08: it hung on the south wall that came out)
    # Wall-mounted carriage lamp: bracket, glass housing, warm bulb.
    make_box("PorchLamp_Bracket", (LX, 0.21, CEIL-0.66), (0.05, 0.20, 0.05), P.METAL_BLACK)
    make_tube("PorchLamp_Housing", [(LX-0.09, 0.30-0.09, CEIL-0.82), (LX-0.09, 0.30-0.09, CEIL-0.50)], 0.006, P.METAL_BLACK, segments=4)
    for ci2, (ux, uy) in enumerate(((1, -1), (-1, 1), (1, 1))):
        make_tube(f"PorchLamp_Housing_{ci2}", [(LX+ux*0.09, 0.30+uy*0.09, CEIL-0.82), (LX+ux*0.09, 0.30+uy*0.09, CEIL-0.50)], 0.006, P.METAL_BLACK, segments=4)
    make_lathe("PorchLamp_Cap", (LX, 0.30, CEIL-0.50), [(0.12, 0.0), (0.06, 0.06), (0.02, 0.10), (0.0, 0.10)], P.METAL_BLACK, segments=8)
    make_lathe("PorchLamp_Foot", (LX, 0.30, CEIL-0.84), [(0.0, 0.0), (0.10, 0.0), (0.10, 0.02), (0.0, 0.02)], P.METAL_BLACK, segments=8)
    make_box("PorchLamp_Glass", (LX, 0.30, CEIL-0.66), (0.14, 0.14, 0.30), P.GLASS_WARM)
    make_lathe("PorchLamp_Bulb", (LX, 0.30, CEIL-0.76), [(0.0, 0.0), (0.025, 0.01), (0.03, 0.05), (0.018, 0.09), (0.0, 0.10)], COL_ACCENT, segments=8)

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
    # the small light blanket, folded over the wicker's west arm
    make_box("Blanket_Fold", (-1.70, ROOM_D/2.0 - 0.02, 0.69), (0.16, 0.40, 0.04), (0.52, 0.36, 0.30, 1.0))
    make_box("Blanket_Drop", (-1.79, ROOM_D/2.0 - 0.02, 0.46), (0.02, 0.38, 0.44), (0.49, 0.34, 0.28, 1.0))
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
    make_cyl("Wear_CupRing_B", (0.14, cy + 0.14, 0.5421), 0.04, 0.003, (0.42, 0.30, 0.18, 1.0), segments=10)
    make_scuff_band("Wear_Scuff_Threshold", (0.0, 0.29), 0.80, axis='X', height=0.03, band_z=0.02, tint=(0.26, 0.19, 0.13, 1.0))
    make_box("Wear_Rail_Hands", (-0.9, 0.10, 1.027), (0.60, 0.06, 0.004), (0.52, 0.40, 0.28, 1.0))
    make_light_switch("Switch_1", (0.75, ROOM_D), axis='X', face_sign=-1, z=1.20, aged=True)
    # (2026-10-08) up the corner post's north face, along the south beam to the lamp
    make_tube("Conduit_1", [(-ROOM_W/2.0 + 0.10, 0.17, 0.30), (-ROOM_W/2.0 + 0.10, 0.17, CEIL - 0.24), (-1.725, 0.17, CEIL - 0.24)], 0.01, (0.36, 0.36, 0.38, 1.0), segments=5)
    make_cyl("Hose_Bib", (2.60, ROOM_D - 0.10, 0.45), 0.02, 0.12, (0.62, 0.60, 0.56, 1.0), axis='Y', segments=6)
    # D5
    for hi in range(9):
        hx = -5.6 + hi * 1.4
        from _props.geometry import make_blob
        make_blob(f"Hedge_{hi}", (hx, -1.0, 0.45), 0.7, (0.24, 0.36, 0.20, 1.0), noise=0.18, seed=40 + hi, squash=0.7)
    make_lathe("Street_Lamp_Post", (7.5, -4.4, -0.03), [(0.14, 0.0), (0.09, 0.10), (0.06, 5.6), (0.07, 5.8), (0.0, 5.8)], (0.24, 0.24, 0.26, 1.0), segments=8)
    make_lathe("Street_Lamp_Head", (7.5, -4.4, 5.72), [(0.0, 0.0), (0.12, 0.05), (0.16, 0.18), (0.0, 0.22)], (0.98, 0.84, 0.50, 1.0), segments=10)
    make_far_bands("Far", (0.42, 0.38, 0.36, 1.0), [(11.0, 12.0, 4.5, 0.85), (18.0, 16.0, 6.0, 0.7)], sides="S", cy=0.0, profile="roofline")



def build_lived_in_2026_10():
    """THE PORCH, LIVED IN (2026-10-08; the user: "Too bare and empty, the
    Caldwell"): the house's front door in the house wall (Maya "stands in
    the doorway watching her grandmother breathe" — the wall had no door),
    the house number and the mailbox by it, geraniums in clay pots on the
    railing, a wind chime under the beam."""
    from _props.geometry import make_blob
    NF = ROOM_D - 0.10
    door_col = (0.30, 0.42, 0.40, 1.0); trim = (0.92, 0.90, 0.84, 1.0)
    for nm, c, sz in (("Head", (0.0, NF - 0.03, 2.13), (1.08, 0.06, 0.10)),
                      ("JambW", (-0.50, NF - 0.03, 1.04), (0.08, 0.06, 2.08)),
                      ("JambE", (0.50, NF - 0.03, 1.04), (0.08, 0.06, 2.08))):
        make_box(f"House_Door_Frame_{nm}", c, sz, trim)
    make_box("House_Door", (0.0, NF - 0.02, 1.03), (0.90, 0.04, 2.04), door_col)
    for k, (pz, ph) in enumerate(((0.45, 0.60), (1.20, 0.60))):
        for e in (-1, 1):
            make_box(f"House_Door_Panel_{k}_{e:+d}", (e * 0.20, NF - 0.042, pz), (0.30, 0.004, ph), (0.26, 0.36, 0.34, 1.0))
    make_box("House_Door_Lite", (0.0, NF - 0.042, 1.78), (0.60, 0.004, 0.30), (0.42, 0.34, 0.22, 1.0))
    make_cyl("House_Door_Knob", (0.36, NF - 0.07, 1.00), 0.03, 0.06, (0.70, 0.58, 0.30, 1.0), axis='Y', segments=8)
    make_box("House_Number", (-0.85, NF - 0.01, 1.75), (0.30, 0.02, 0.12), (0.70, 0.58, 0.30, 1.0))
    make_box("House_Mailbox", (-0.85, NF - 0.05, 1.35), (0.30, 0.10, 0.22), (0.20, 0.20, 0.22, 1.0))
    make_box("House_Mailbox_Lid", (-0.85, NF - 0.06, 1.47), (0.32, 0.12, 0.02), (0.20, 0.20, 0.22, 1.0))
    # geraniums on the west railing
    for gi, gx in enumerate((-2.55, -2.12)):
        make_lathe(f"Geranium_Pot_{gi}", (gx, 0.10, 1.025), [(0.05, 0.0), (0.07, 0.12), (0.075, 0.13), (0.0, 0.13)], (0.70, 0.40, 0.28, 1.0), segments=10)
        make_blob(f"Geranium_{gi}", (gx, 0.10, 1.22), 0.10, (0.28, 0.46, 0.26, 1.0), noise=0.30, seed=80 + gi, squash=0.7)
        make_blob(f"Geranium_{gi}_Bloom", (gx + 0.03, 0.08, 1.29), 0.05, (0.86, 0.22, 0.24, 1.0), noise=0.25, seed=90 + gi, squash=0.8)
    # the wind chime under the south beam, east of the door
    cx_, cy_ = 2.30, 0.12
    make_cyl("Wind_Chime_String", (cx_, cy_, 2.525), 0.003, 0.15, (0.20, 0.20, 0.20, 1.0), segments=4)
    make_cyl("Wind_Chime_Ring", (cx_, cy_, 2.445), 0.06, 0.01, (0.46, 0.34, 0.24, 1.0), segments=12)
    for t in range(5):
        a = t * 1.2566
        ln = 0.22 + 0.05 * t
        make_cyl(f"Wind_Chime_Tube_{t}", (cx_ + 0.045 * math.cos(a), cy_ + 0.045 * math.sin(a), 2.445 - ln / 2.0), 0.008, ln,
                 (0.78, 0.80, 0.82, 1.0), segments=6)


def build_yard_party_2026_10():
    """THE CALDWELL FRONT YARD, SUNDAY AFTERNOON (2026-10-10; vol6 ch23 "Sunday",
    the sweep: the sticker-book ceremony played on the porch at night).
    "the Caldwell front yard at three forty-five PM has been arranged for the
    small specific event Anita has been organizing for two weeks. The folding
    table from the Kowalski garage is set up under the pecan tree. On the table
    is the cake — a sheet cake from the bakery on Magnolia, with white frosting
    and the words GRACIE — STICKER QUEEN in pink piping. Beside the cake, on a
    small folded cloth, sits Gracie's completed activity book ... Linda is in
    the wicker chair from the Caldwell porch, which Maya has wheeled out to the
    yard. Anita is at the table ... pouring lemonade into paper cups." ·
    "Eileen has the cinnamon coffee cake in the small white box".
    The yard opens east of the porch: the lawn, the pecan, the folding table
    and what is on it, Linda's wicker chair on the grass, folding chairs, the
    house's body behind the porch (the day shows it), the side fence and the
    neighbour's roof past it. Preset `caldwell_yard_afternoon` (day lights
    and markers suffixed)."""
    from _props.geometry import make_blob
    grass = (0.30, 0.44, 0.22, 1.0)
    make_box("Side_Yard_Lawn", (11.0, 1.0, -0.03), (10.0, 10.0, 0.05), grass)
    # the house behind the porch, which the day finally shows
    make_box("House_Body_Facade", (0.0, ROOM_D + 4.1, 2.6), (11.0, 8.0, 5.2), (0.82, 0.78, 0.68, 1.0))
    make_rot_box("House_Roof_S", (0.0, ROOM_D + 2.3, 5.75), (11.6, 4.6, 0.16), (0.36, 0.30, 0.28, 1.0), roll=0.42)
    make_rot_box("House_Roof_N", (0.0, ROOM_D + 5.9, 5.75), (11.6, 4.6, 0.16), (0.36, 0.30, 0.28, 1.0), roll=-0.42)
    for k, wy in enumerate((ROOM_D + 1.6, ROOM_D + 5.0)):
        make_box(f"House_Body_Window_E_{k}", (5.505, wy, 1.6), (0.01, 1.0, 1.2), (0.40, 0.46, 0.50, 1.0))
        make_box(f"House_Body_Window_E_{k}_Frame", (5.51, wy, 1.6), (0.01, 1.12, 1.32), (0.92, 0.90, 0.84, 1.0))
    # the pecan tree
    px, py = 11.2, 1.8
    make_lathe("Pecan_Trunk", (px, py, -0.03), [(0.42, 0.0), (0.34, 0.6), (0.30, 3.2), (0.0, 3.25)], (0.36, 0.28, 0.22, 1.0), segments=12)
    for k, (bx, by, bz, r) in enumerate(((0.0, 0.0, 5.0, 3.2), (-2.4, 0.6, 4.4, 2.4), (2.2, -0.8, 4.6, 2.4), (0.6, 2.2, 4.8, 2.2), (-0.8, -2.0, 4.2, 2.0))):
        make_blob(f"Pecan_Crown_{k}", (px + bx, py + by, bz), r, (0.26, 0.40, 0.20, 1.0), noise=0.22, seed=300 + k, squash=0.62)
    for k, (dx, dy, a) in enumerate(((1.0, 0.4, 0.5), (-1.1, 0.2, -0.6), (0.2, -1.1, 0.2))):
        make_rot_box(f"Pecan_Limb_{k}", (px + dx * 0.9, py + dy * 0.9, 3.6), (0.20, 0.20, 2.2), (0.36, 0.28, 0.22, 1.0), pitch=a, roll=0.3 * dy)
    # the folding table under it, and what is on it
    tx, ty, th = 10.4, 0.6, 0.74
    make_box("Folding_Table_Top", (tx, ty, th - 0.02), (1.83, 0.76, 0.04), (0.92, 0.92, 0.90, 1.0))
    for e in (-1, 1):
        make_rot_box(f"Folding_Table_Leg_{e:+d}", (tx + e * 0.80, ty, (th - 0.04) / 2.0), (0.04, 0.66, 0.70), (0.40, 0.40, 0.42, 1.0))
    t = th
    make_box("Cake_Board", (tx - 0.20, ty, t + 0.005), (0.52, 0.38, 0.01), (0.94, 0.92, 0.86, 1.0))
    make_box("Cake", (tx - 0.20, ty, t + 0.06), (0.46, 0.32, 0.10), (0.98, 0.97, 0.94, 1.0))
    make_box("Cake_Piping_Gracie", (tx - 0.26, ty + 0.03, t + 0.111), (0.26, 0.05, 0.003), (0.94, 0.56, 0.70, 1.0))
    make_box("Cake_Piping_Sticker_Queen", (tx - 0.20, ty - 0.06, t + 0.111), (0.36, 0.04, 0.003), (0.94, 0.56, 0.70, 1.0))
    make_box("Cake_Border", (tx - 0.20, ty - 0.165, t + 0.10), (0.46, 0.012, 0.02), (0.94, 0.56, 0.70, 1.0))
    make_box("Sticker_Book_Cloth", (tx + 0.30, ty + 0.05, t + 0.004), (0.34, 0.28, 0.008), (0.86, 0.78, 0.94, 1.0))
    make_box("Sticker_Book", (tx + 0.30, ty + 0.05, t + 0.016), (0.22, 0.28, 0.016), (0.96, 0.62, 0.16, 1.0))
    make_box("Sticker_Book_Stars", (tx + 0.30, ty + 0.05, t + 0.0245), (0.14, 0.18, 0.001), (0.30, 0.56, 0.86, 1.0))
    make_lathe("Lemonade_Pitcher", (tx + 0.66, ty + 0.12, t), [(0.0, 0.0), (0.07, 0.0), (0.075, 0.18), (0.055, 0.24), (0.0, 0.24)], (0.96, 0.92, 0.56, 1.0), segments=12)
    for k in range(6):
        make_cyl(f"Paper_Cup_{k}", (tx + 0.52 + (k % 3) * 0.09, ty - 0.18 + (k // 3) * 0.09, t + 0.05), 0.035, 0.10, (0.96, 0.96, 0.94, 1.0), segments=8)
    make_box("Paper_Plates", (tx - 0.70, ty + 0.15, t + 0.012), (0.24, 0.24, 0.024), (0.96, 0.96, 0.94, 1.0))
    make_box("Cake_Knife", (tx - 0.62, ty - 0.18, t + 0.003), (0.24, 0.025, 0.004), (0.74, 0.76, 0.78, 1.0))
    make_box("Photo_Phone", (tx - 0.75, ty - 0.22, t + 0.005), (0.07, 0.14, 0.01), (0.13, 0.13, 0.15, 1.0))   # Anita's, for the picture
    # Linda's wicker chair, wheeled out onto the grass from the porch
    _wicker_chair("Lawn_Wicker", 8.70, 0.20)
    # folding chairs for the guests
    for k, (cx, cy) in enumerate(((12.3, -0.2), (12.5, 1.1), (9.4, -1.0))):
        fx, fy = tx - cx, ty - cy                     # each faces the table
        fl = math.hypot(fx, fy); fx, fy = fx / fl, fy / fl
        yaw = math.atan2(fy, fx) - math.pi / 2.0      # local +y toward the table
        make_rot_box(f"Lawn_Folding_Chair_{k}_Seat", (cx, cy, 0.45), (0.42, 0.42, 0.04), (0.40, 0.40, 0.42, 1.0), yaw=yaw)
        make_rot_box(f"Lawn_Folding_Chair_{k}_Back", (cx - 0.20 * fx, cy - 0.20 * fy, 0.72), (0.42, 0.04, 0.50), (0.40, 0.40, 0.42, 1.0), yaw=yaw)
        make_rot_box(f"Lawn_Folding_Chair_{k}_Legs", (cx, cy, 0.215), (0.40, 0.40, 0.43), (0.30, 0.30, 0.32, 1.0), yaw=yaw)
    # Eileen's cinnamon coffee cake in its small white box, set down on a chair
    make_box("Coffee_Cake_Box", (9.43, -0.95, 0.47 + 0.05), (0.20, 0.20, 0.10), (0.97, 0.97, 0.95, 1.0))   # toward the seat's front
    # the side fence and the neighbour's roof past it
    make_box("Side_Fence_Boards", (16.1, 1.0, 0.90), (0.05, 10.0, 1.80), (0.56, 0.44, 0.32, 1.0))
    for k in range(6):
        make_box(f"Side_Fence_Post_{k}", (16.0, -4.0 + k * 2.0, 0.95), (0.10, 0.10, 1.90), (0.46, 0.36, 0.26, 1.0))
    make_box("Neighbour_House_Facade", (21.0, 2.0, 2.4), (8.0, 9.0, 4.8), (0.70, 0.74, 0.76, 1.0))
    hd = 9.0 / 4.0 + 0.25
    rz = 4.8 + hd * math.sin(0.42) + 0.08 - 0.02          # the eaves on the wall top
    make_rot_box("Neighbour_Roof_N", (21.0, 2.0 + 9.0 / 4.0, rz), (8.6, 2.0 * hd, 0.16), (0.34, 0.32, 0.30, 1.0), roll=-0.42)
    make_rot_box("Neighbour_Roof_S", (21.0, 2.0 - 9.0 / 4.0, rz), (8.6, 2.0 * hd, 0.16), (0.34, 0.32, 0.30, 1.0), roll=0.42)
    # the rest of the neighbourhood the day shows: the lawns running back, the
    # street on east, two more houses, the trees (no world edge past the fence)
    make_box("Back_Lawns", (17.0, 23.0, -0.035), (46.0, 34.0, 0.04), grass)
    make_box("Back_Lawns_W", (-10.0, 26.0, -0.035), (8.0, 28.0, 0.04), grass)
    make_box("Neighbour_Lawn_E", (28.0, 1.0, -0.035), (24.0, 10.0, 0.04), grass)
    make_box("Street_Strip_E", (23.0, -6.0, -0.03), (34.0, 4.0, 0.05), (0.26, 0.26, 0.28, 1.0))
    for k, (hx, hy, hw, hdp, hh, col) in enumerate(((12.0, 21.0, 9.0, 8.0, 4.4, (0.78, 0.70, 0.58, 1.0)),
                                                   (-6.0, 24.0, 10.0, 8.0, 4.8, (0.66, 0.72, 0.68, 1.0)),
                                                   (28.0, 19.0, 9.0, 9.0, 4.2, (0.84, 0.82, 0.76, 1.0)))):
        make_box(f"Street_House_{k}_Facade", (hx, hy, hh / 2.0), (hw, hdp, hh), col)
        rh = hdp / 4.0 + 0.25
        rzz = hh + rh * math.sin(0.42) + 0.08 - 0.02
        make_rot_box(f"Street_House_{k}_Roof_N", (hx, hy + hdp / 4.0, rzz), (hw + 0.6, 2.0 * rh, 0.16), (0.32, 0.30, 0.30, 1.0), roll=-0.42)
        make_rot_box(f"Street_House_{k}_Roof_S", (hx, hy - hdp / 4.0, rzz), (hw + 0.6, 2.0 * rh, 0.16), (0.32, 0.30, 0.30, 1.0), roll=0.42)
    for k, (gx, gy) in enumerate(((4.0, 17.0), (20.0, 12.0), (32.0, 8.0), (6.0, 30.0))):
        make_cyl(f"Street_Tree_{k}_Trunk", (gx, gy, 1.6), 0.24, 3.2, (0.36, 0.28, 0.22, 1.0), segments=8)
        make_blob(f"Street_Tree_{k}_Crown", (gx, gy, 4.6), 2.6, (0.26, 0.40, 0.22, 1.0), noise=0.22, seed=330 + k, squash=0.7)

def main():
    clear_scene()
    build_shell()
    build_railing()
    build_chairs()
    build_lived_in_2026_10()
    build_yard_party_2026_10()
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
