"""Kowalski Kitchen — vol6 placement script.

DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3, 7 placements): a
gooseneck faucet with its handle, burners, knobs and an oven bar on the
stove, the pendant as canopy + cord + shade + bulb, the fridge's handle
as a pull with a photo under a magnet, salt and pepper as shakers; the
kitchen's first WEAR (paths, the chairs' patches, the counter's edge,
the drip line, the fridge's hand patch, Daisy's spot and her hair on
the couch); D3 (two switches, outlets, cords from the TV, the coffee
maker and the fridge); D5 (the backyard through the sink window, the
neighbour's yard and mower through the east one). The .tscn's overhead
practical becomes the pendant's bulb and the under-cabinet light
Anita sits by gets its own.

DRAFT 5 (2026-10-09, the overnight run; CLAUDE.md "build big"). A 6 x 5
box held the kitchen run, the table, the fridge, the couch, the TV and a
stair: the couch stood a chair-width from the table and the TV hung on
the kitchen's E wall. The Kowalskis' kitchen opens onto a FAMILY ROOM
(vol6 ch13/19: "Bill is at the kitchen table with the Sentinel"; "sat
with the dog, watched five minutes of the noon news"; "He goes in
through the garage"; his mother asleep "by the angle of the bedroom
door from the hallway"). 10.0 x 6.4 now:
  - the KITCHEN, E half: the run on the N wall (the kit, laid out on
    the new wall with the sink under the back-yard window and the hot
    sauce cabinet left of the stove), the table under its pendant, the
    fridge and the E window (moved rigidly, plan.shifted);
  - the FAMILY ROOM, W half: the couch along the W wall with Daisy on
    it, the TV on a low stand facing it with the noon news on, a coffee
    table, a floor lamp, the calendar;
  - the S wall: the garage door (Ben's way in) and the hall opening, the
    hall beyond with the bedroom door shut (night-shift sleep).
The stair mouth is gone: nothing in the prose climbs a stair here.
Draft 6 targets (were draft 5's): the upper cabinet doors with pulls and one ajar; the
dish rack's dishes; the stair treads with risers and a runner; the TV
on a stand with its cord; the couch's throw; Deck: the ch19 establish
under the under-cabinet light alone.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_table, make_chair
from _props import palette as P
from _props.geometry import make_blob   # module-level: plan.shifted moves it (2026-10-09)
from _props.geometry import (clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe,
                             make_tube, make_rot_box, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

# 2026-09-25: the counter run and the stove stood at ROOM_D-0.45 — 0.55 m off the N wall in every kitchen from this template; ROOM_D-0.45 puts their backs on the wall face
ROOM_W = 10.0; ROOM_D = 6.4; CEIL = 2.6   # draft 5 (2026-10-09): was 6.0 x 5.0
PAL_WALL = {"wall": (0.92, 0.86, 0.74, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.74, 0.58, 0.38, 1.0); COL_SEAM = (0.42, 0.30, 0.18, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_ACCENT = (0.62, 0.42, 0.22, 1.0)
# the kitchen on the kit (2026-10-07): the Kowalskis' honey maple and
# butcher-block laminate; the counter stays at the 0.92 every dressing
# prop already stands on
from _props import kitchen_kit as K
Y_BACK = ROOM_D - 0.10
TOP_Z = 0.92
# the kitchen run spans the E 5.8 m of the N wall (draft 5)
KX0, KX1 = -0.90, ROOM_W/2.0 - 0.10
SINK_X, RANGE_X = 0.50, 3.50
HOT_X0 = RANGE_X - 0.42 - 0.46        # the hot sauce cabinet's left edge
MAPLE = (0.58, 0.44, 0.28, 1.0); MAPLE_DK = (0.46, 0.34, 0.22, 1.0)
BLOCK = (0.66, 0.50, 0.32, 1.0); BLOCK_EDGE = (0.50, 0.36, 0.22, 1.0)
PEWTER = (0.48, 0.48, 0.46, 1.0); BISCUIT = (0.90, 0.84, 0.72, 1.0)

from _props.structure import make_frame_ring   # (2026-10-07: the frame boards → rings)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1,
                            openings=[(3.0 + SH_TF[1], 1.550, 1.500, 1.100)])
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=-1, openings=[(SINK_X, 1.52, 1.50, 1.00), (-3.0, 1.52, 1.60, 1.10)])
    # the S wall: the hall opening W, the garage door E
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1,
                            openings=[HALL_OPEN, GARAGE_DOOR])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_counter():
    """The N run on the kitchen kit (2026-10-07). It was a store counter
    (make_counter) with a chamfered box for a stove, and the upper
    cabinets ran ACROSS the sink window — the back yard Gracie's dad
    yells about the weeds in was half behind a cabinet. Now: base
    cabinets wall to wall, the sink under the window, the range where
    Bill cooks the eggs, uppers either side of the window — "hot sauce
    is in the cabinet to the left of the stove" — and the under-cabinet
    light Anita sits by under the run left of the stove."""
    K.base_run("Counter", KX0, KX1, Y_BACK, top_z=TOP_Z,
               body=MAPLE, top=BLOCK, edge=BLOCK_EDGE, pull=PEWTER, rail=MAPLE_DK,
               gaps=[(RANGE_X - 0.38, RANGE_X + 0.38)])
    K.sink("Sink", SINK_X, Y_BACK, TOP_Z)
    K.range_("Stove", RANGE_X, Y_BACK, TOP_Z)
    for nm, a, b in (("Upper_W", KX0, SINK_X - 0.86),
                     ("Upper_Mid", SINK_X + 0.86, HOT_X0),
                     ("Upper_E", RANGE_X + 0.42, KX1)):
        K.upper_run(nm, a, b, Y_BACK, z0=1.46, z1=2.20, body=MAPLE, pull=PEWTER, rail=MAPLE_DK)
    # THE HOT SAUCE CABINET (draft 5's "one upper door ajar"): the last
    # upper left of the stove, open — "Hot sauce is in the cabinet to the
    # left of the stove if you want it" (ch8) — a shell, its shelf, the
    # bottle and its neighbours, the door swung 70 degrees
    from _props.structure import make_case_shell
    from _props.geometry import make_rot_box
    hx0, hx1 = HOT_X0, RANGE_X - 0.42
    hxc, hw = (hx0 + hx1) / 2.0, hx1 - hx0
    make_case_shell("HotSauce_Cab", (hxc, Y_BACK - 0.17, 1.83), (hw, 0.34, 0.74), MAPLE, open_face='-Y')
    make_box("HotSauce_Cab_Shelf", (hxc, Y_BACK - 0.17, 1.83), (hw - 0.04, 0.30, 0.018), MAPLE_DK)
    make_box("HotSauce_Cab_Crown", (hxc, Y_BACK - 0.33, 2.23), (hw + 0.02, 0.05, 0.06), MAPLE)
    for bi, (bx, col, ht) in enumerate(((-0.11, (0.78, 0.14, 0.10, 1.0), 0.16), (0.0, (0.86, 0.66, 0.20, 1.0), 0.22),
                                         (0.11, (0.30, 0.22, 0.16, 1.0), 0.19))):
        nm = "HotSauce_Bottle" if bi == 0 else f"HotSauce_Cab_Jar_{bi}"
        make_cyl(nm, (hxc + bx, Y_BACK - 0.20, 1.839 + ht / 2.0), 0.028, ht, col, segments=8)
        make_cyl(f"{nm}_Cap", (hxc + bx, Y_BACK - 0.20, 1.839 + ht + 0.012), 0.016 if bi == 0 else 0.03, 0.024,
                 (0.94, 0.92, 0.86, 1.0) if bi == 0 else (0.20, 0.20, 0.22, 1.0), segments=8)
    for bi, bx in enumerate((-0.10, 0.06)):
        make_cyl(f"HotSauce_Cab_Can_{bi}", (hxc + bx, Y_BACK - 0.18, 1.48 + 0.06), 0.035, 0.12, (0.62, 0.20, 0.16, 1.0), segments=8)
    # the door, hinged on the cabinet's LEFT edge, swung 70 degrees out
    import math
    sw = math.radians(70.0)                  # the swing, out into the room
    dw = hw - 0.012
    make_rot_box("HotSauce_Cab_Door", (hx0 + math.cos(sw) * dw / 2.0, Y_BACK - 0.34 - math.sin(sw) * dw / 2.0, 1.83),
                 (dw, 0.018, 0.72), MAPLE, yaw=-sw)
    for nm, a, b in (("Splash_W", KX0, SINK_X - 0.86), ("Splash_E", SINK_X + 0.86, KX1)):
        K.backsplash(nm, a, b, Y_BACK, TOP_Z, 1.44, tile=BISCUIT, grout=(0.76, 0.70, 0.58, 1.0))

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    # DETAIL DRAFT 3 (2026-09-06): the table and its four chairs through the
    # furniture kit — turned legs, aprons, a stretcher; spindled chair backs
    # turned away from the table. Names keep Table_Top / Chair_N_Seat.
    make_table("Table", tx, ty, w=1.20, d=0.80, h=0.76, wood=COL_WOOD)
    for ci, (cx, cy, yaw) in enumerate([(tx-0.80, ty, -1.5708), (tx+0.80, ty, 1.5708), (tx, ty-0.62, 0.0), (tx, ty+0.62, 3.1416)]):
        make_chair(f"Chair_{ci}", cx, cy, yaw=yaw, wood=COL_WOOD)

def build_clock():
    make_wall_clock("Clock", (2.0, ROOM_D - 0.10, CEIL-0.22), frozen_hour=8, frozen_min=15, facing='-Y')

def build_window():
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    make_frame_ring("Window_E_Frame", (ROOM_W/2.0-0.12, ROOM_D/2.0+0.5, 1.55), (0.04, 1.60, 1.20), P.METAL_STEEL)
    make_box("Window_E_Glass", (ROOM_W/2.0-0.1425, ROOM_D/2.0+0.5, 1.55), (0.005, 1.50, 1.10), (0.78, 0.84, 0.86, 0.55))

def build_ceiling_infra():
    # Family kitchen: flush dome + over-table pendant, no shop tubes
    make_lathe("Table_Pendant_Canopy", (0.0, ROOM_D/2.0, CEIL-0.03), [(0.06, 0.0), (0.06, 0.02), (0.02, 0.03), (0.0, 0.03)], P.METAL_BLACK, segments=8)
    make_tube("Table_Pendant_Cord", [(0.0, ROOM_D/2.0, CEIL-0.03), (0.0, ROOM_D/2.0, CEIL-0.30)], 0.005, P.METAL_BLACK, segments=4)
    make_lathe("Table_Pendant_Shade", (0.0, ROOM_D/2.0, CEIL-0.46), [(0.17, 0.0), (0.16, 0.02), (0.06, 0.14), (0.025, 0.16), (0.0, 0.16)], (0.62, 0.46, 0.28, 1.0), segments=12)
    make_lathe("Table_Pendant_Bulb", (0.0, ROOM_D/2.0, CEIL-0.48), [(0.0, 0.0), (0.03, 0.01), (0.032, 0.04), (0.02, 0.06), (0.0, 0.07)], (0.98, 0.94, 0.80, 1.0), segments=8)
    make_smoke_detector("Smoke", (0.9, ROOM_D/2.0, CEIL))


def build_fridge():
    fx, fy = +ROOM_W/2.0 - 0.55, 1.0
    make_chamfer_box("Fridge_Body", (fx, fy, 1.00), (0.70, 0.70, 2.00), (0.82, 0.82, 0.84, 1.0))
    make_chamfer_box("Fridge_DoorTop", (fx-0.34, fy, 1.50), (0.04, 0.66, 0.80), (0.82, 0.82, 0.84, 1.0))
    make_chamfer_box("Fridge_DoorBot", (fx-0.34, fy, 0.40), (0.04, 0.66, 1.00), (0.82, 0.82, 0.84, 1.0))
    make_tube("Fridge_Handle", [(fx-0.36, fy-0.20, 1.05), (fx-0.40, fy-0.20, 1.05), (fx-0.40, fy-0.20, 1.55), (fx-0.36, fy-0.20, 1.55)], 0.012, P.METAL_STEEL, segments=6)
    make_box("Fridge_Photo", (fx-0.362, fy+0.05, 1.42), (0.003, 0.10, 0.075), (0.72, 0.66, 0.58, 1.0))
    make_cyl("Fridge_Magnet", (fx-0.365, fy+0.05, 1.465), 0.012, 0.004, (0.62, 0.20, 0.18, 1.0), axis='X', segments=8)

def build_counter_dressing():
    """The coffee maker left of the sink, the dish rack right of it."""
    cw_x = SINK_X; cw_y = ROOM_D-0.45
    make_coffee_pots("Coffee", (cw_x-1.0, cw_y+0.50, 0.94), pots=1)   # the kit puts a lone pot 0.5 in front of its anchor (2026-09-25)
    make_box("DishRack_Base", (cw_x+0.9, cw_y, TOP_Z+0.015), (0.34, 0.30, 0.03), P.METAL_STEEL)
    for ti in range(5):
        make_box(f"DishRack_Tine_{ti}", (cw_x+0.74+ti*0.06, cw_y, TOP_Z+0.11), (0.01, 0.24, 0.16), P.METAL_STEEL)


def build_calendar():
    make_calendar("Calendar", (-ROOM_W/2.0+0.1025, 2.0, 1.6))


def build_table_dressing():
    # Table centrepiece: napkin holder + salt & pepper
    tx, ty = 0.0, ROOM_D/2.0
    make_box("NapkinHolder", (tx, ty, 0.82), (0.14, 0.06, 0.12), (0.86, 0.84, 0.80, 1.0))
    for nm, sx_, col in (("Salt", tx+0.16, (0.92, 0.92, 0.90, 1.0)), ("Pepper", tx+0.22, (0.28, 0.24, 0.22, 1.0))):
        make_lathe(nm, (sx_, ty, 0.76), [(0.02, 0.0), (0.025, 0.01), (0.025, 0.07), (0.018, 0.09), (0.02, 0.10), (0.0, 0.105)], col, segments=8)


def build_plant():
    # Floor plant in the SW corner (make_floor_plant was unused)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, 0.7, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.60, 0.40, 0.26, 1.0)})

def build_hero_props():
    """2026-08-03 hero-prop pass: upper cabinets (hot sauce to the
    left of the stove), the under-cabinet light Anita sits by, the
    couch + noon-news TV, the stair mouth, the window over the
    sink (Gracie's dad yells about weeds through it)."""
    wood = (0.52, 0.40, 0.26, 1.0)
    # Upper cabinets over the counter + the box left of the stove
    # on the wall face (2026-09-23: 9.5 cm into the N wall)
    # (2026-10-07: the uppers are the kit's, in build_counter — the hot
    # sauce is behind Upper_Mid's last door, left of the stove)
    # The under-cabinet light — the only light in the ch19 beat — under
    # Upper_Mid's front edge
    make_box("UnderCab_Light", ((SINK_X + 0.86 + RANGE_X - 0.42) / 2.0, Y_BACK - 0.26, 1.44),
             (RANGE_X - 0.42 - SINK_X - 0.86 - 0.10, 0.05, 0.04), (0.98, 0.90, 0.70, 1.0))   # under Upper_Mid AND the hot sauce cabinet
    # The window over the sink onto the backyard
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Sink_Window", (SINK_X, ROOM_D - 0.10, 1.52), width=1.50, height=1.00, see_through=True)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Three distinct cues, all at the table (top 0.76):

    - ANITA'S PHONE ("Anita slides her phone across the table"):
      face-up mid-slide, off-square.
    - THE CROSSWORD ("He looks down at the crossword"): the folded
      page with its grid inlay, pencil beside.
    - THE EGGS ("Two eggs over-easy, two pieces of toast, a strip
      of bacon. He sets it in front of Maya without comment."):
      the plate as served.
    """
    make_box("Anitas_Phone", (0.30, 2.30, 0.7715), (0.070, 0.140, 0.011),
             (0.13, 0.13, 0.15, 1.0))
    make_box("Crossword_Page", (-0.30, 2.60, 0.761), (0.200, 0.280, 0.002),
             (0.90, 0.88, 0.83, 1.0))
    make_box("Crossword_Grid", (-0.30, 2.54, 0.7625), (0.100, 0.100, 0.001),
             (0.30, 0.30, 0.33, 1.0))
    make_cyl("Crossword_Pencil", (-0.13, 2.70, 0.766), 0.005, 0.130,
             (0.86, 0.72, 0.28, 1.0), axis='Y', segments=6)
    make_cyl("Breakfast_Plate", (0.28, 2.66, 0.771), 0.120, 0.012,
             (0.92, 0.90, 0.86, 1.0), segments=14)
    for ei, (ex2, ey2) in enumerate(((0.235, 2.63), (0.30, 2.70))):
        make_cyl(f"Egg_White_{ei}", (ex2, ey2, 0.783), 0.028, 0.012,
                 (0.96, 0.94, 0.90, 1.0), segments=10)
        make_cyl(f"Egg_Yolk_{ei}", (ex2, ey2, 0.792), 0.012, 0.006,
                 (0.94, 0.72, 0.20, 1.0), segments=8)
    for ti2, (tx3, ty3) in enumerate(((0.35, 2.585), (0.375, 2.66))):
        make_box(f"Toast_{ti2}", (tx3, ty3, 0.781), (0.055, 0.040, 0.008),
                 (0.80, 0.62, 0.36, 1.0))
    make_box("Bacon_Strip", (0.21, 2.72, 0.7795), (0.020, 0.090, 0.005),
             (0.62, 0.30, 0.22, 1.0))


def build_draft4_2026_09():
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; 7 placements) — WEAR,
    D3, D5. Draft 5 split it by AREA (below) so each piece moves with its
    furniture; the paths are re-walked on the new plan here."""
    from _props.detail import make_traffic_wear
    floor_dk = (0.69, 0.54, 0.35, 1.0)    # (draft 5: at 0.58 the paths read as dark rugs)
    make_traffic_wear("Wear_Path_Garage", [(GARAGE_DOOR[0], 0.5), (GARAGE_DOOR[0], 1.6), (2.6, 2.6)], width=0.5, tint=floor_dk)
    make_traffic_wear("Wear_Path_Counter", [(2.0, 4.4), (1.2, 5.0), (0.6, 5.5)], width=0.42, tint=floor_dk)
    make_traffic_wear("Wear_Path_Hall", [(HALL_OPEN[0], 0.5), (-1.6, 2.0), (-3.4, 3.0)], width=0.45, tint=floor_dk)


def build_wear_table():
    from _props.detail import make_floor_stain
    tx, ty = 0.0, ROOM_D/2.0
    for ci, (cx, cy) in enumerate([(tx-0.80, ty), (tx+0.80, ty), (tx, ty-0.62), (tx, ty+0.62)]):
        make_floor_stain(f"Wear_Patch_Seat_{ci}", (cx, cy), radius=0.26, tint=(0.66, 0.52, 0.34, 1.0), segments=10)


def build_wear_counter():
    from _props.detail import make_scuff_band, make_light_switch, make_wall_outlet, make_cord_run, make_backyard_view
    make_box("Wear_Elbow_Strip", (SINK_X, Y_BACK-0.62+0.02, TOP_Z+0.002), (2.2, 0.06, 0.004), (0.50, 0.36, 0.22, 1.0))
    make_scuff_band("Wear_Drip", (SINK_X, Y_BACK-0.62-0.024), 0.6, axis='X', height=0.12, band_z=0.60, tint=(0.62, 0.52, 0.34, 1.0))
    make_light_switch("Switch_2", (SINK_X + 1.30, ROOM_D), axis='X', face_sign=-1, z=1.35, aged=True)
    make_wall_outlet("Outlet_N_1", (SINK_X - 1.05, ROOM_D), axis='X', face_sign=-1, z=1.10, aged=True)
    make_cord_run("Cord_2", (SINK_X - 0.95, ROOM_D-0.45+0.10, 0.96), (SINK_X - 1.05, ROOM_D - 0.12, 1.10), sag=0.03)
    make_backyard_view("Yard", ROOM_D, span=12.0, tree=(2.4, 3.2))


def build_wear_fridge():
    from _props.detail import make_wall_outlet, make_cord_run
    make_box("Wear_Hand_Patch", (ROOM_W/2.0-0.55-0.362, 1.0-0.10, 1.30), (0.003, 0.14, 0.20), (0.74, 0.74, 0.76, 1.0))
    make_wall_outlet("Outlet_E_2", (ROOM_W/2.0, 0.55), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_3", (ROOM_W/2.0-0.22, 0.75, 0.10), (ROOM_W/2.0 - 0.13, 0.55, 0.30), sag=0.0)


def build_eyard():
    make_box("EYard_Lawn", (ROOM_W/2.0 + 3.0, 3.0, -0.03), (6.0, 8.0, 0.05), (0.40, 0.48, 0.28, 1.0))
    make_lathe("EYard_Tree", (ROOM_W/2.0 + 3.5, 3.4, 0.0), [(0.16, 0.0), (0.12, 1.2), (0.09, 2.6), (0.0, 2.6)], (0.38, 0.30, 0.22, 1.0), segments=8)
    make_blob("EYard_Canopy", (ROOM_W/2.0 + 3.5, 3.4, 3.6), 1.5, (0.30, 0.42, 0.24, 1.0), noise=0.22, seed=23, squash=0.8)
    make_chamfer_box("EYard_Mower", (ROOM_W/2.0 + 1.6, 2.2, 0.165), (0.55, 0.85, 0.34), (0.66, 0.20, 0.16, 1.0), chamfer=0.02)   # on the lawn (2026-09-23: 2 cm over it)
    make_tube("EYard_Mower_Handle", [(ROOM_W/2.0 + 1.6 - 0.2, 2.2 - 0.4, 0.33), (ROOM_W/2.0 + 1.6 - 0.2, 2.2 - 1.1, 0.93), (ROOM_W/2.0 + 1.6 + 0.2, 2.2 - 1.1, 0.93), (ROOM_W/2.0 + 1.6 + 0.2, 2.2 - 0.4, 0.33)], 0.012, (0.30, 0.30, 0.32, 1.0), segments=5)


def build_family_room():
    """DRAFT 5: the family room's own things, on the new plan (no shift):
    the TV facing the couch with the noon news on, its stand and cord,
    the coffee table, a floor lamp, DAISY on the couch, a ceiling light;
    the S wall's garage door and the hall beyond the opening with the
    bedroom door shut."""
    from _props.detail import make_wall_outlet, make_light_switch
    from _props.creatures import make_dog
    wood = (0.52, 0.40, 0.26, 1.0)
    # the couch facing S (draft 5: the room turned so the TV can stand on a
    # wall — it was a stand in the middle of the floor)
    cx_, cy_ = -3.0, 4.33
    make_chamfer_box("Couch_Base", (cx_, cy_, 0.19), (2.00, 0.85, 0.38), (0.44, 0.38, 0.30, 1.0))
    make_chamfer_box("Couch_Back", (cx_, cy_ + 0.37, 0.62), (2.00, 0.18, 0.58), (0.40, 0.34, 0.27, 1.0))
    for nm, ox in (("W", -1.06), ("E", 1.06)):
        make_chamfer_box(f"Couch_Arm_{nm}", (cx_ + ox, cy_, 0.30), (0.14, 0.85, 0.60), (0.40, 0.34, 0.27, 1.0))
    for k, ox in enumerate((-0.50, 0.50)):
        make_chamfer_box(f"Couch_Cushion_{k}", (cx_ + ox, cy_ - 0.07, 0.46), (0.96, 0.70, 0.14), (0.48, 0.42, 0.34, 1.0))
    make_box("Couch_Throw", (cx_ + 0.80, cy_ + 0.30, 0.93), (0.40, 0.22, 0.04), (0.62, 0.30, 0.26, 1.0))
    # Daisy's spot on the W cushion, her hair on it, DAISY on it, head up at the door
    make_chamfer_box("Wear_Daisy_Spot", (cx_ - 0.50, cy_ - 0.07, 0.535), (0.55, 0.50, 0.02), (0.42, 0.36, 0.30, 1.0), chamfer=0.008)
    for hi in range(6):
        make_rot_box(f"Wear_Hair_{hi}", (cx_ - 0.58 + 0.08 * (hi % 3), cy_ - 0.20 + 0.10 * (hi // 3), 0.548), (0.03, 0.004, 0.002), (0.80, 0.72, 0.56, 1.0), yaw=0.6 * hi)
    make_dog("Daisy", cx_ - 0.50, cy_ - 0.24, 0.545, heading='-Y', pose='lying', scale=0.85)
    # the TV on its stand against the S wall, the noon news on
    tvx, tvy = -3.0, 0.31
    make_box("TV_Stand", (tvx, tvy, 0.25), (1.30, 0.42, 0.50), MAPLE_DK)
    make_box("TV_Stand_Box", (tvx - 0.30, tvy + 0.215, 0.18), (0.50, 0.01, 0.20), (0.20, 0.20, 0.22, 1.0))
    make_box("TV_Foot", (tvx, tvy, 0.515), (0.40, 0.22, 0.03), (0.10, 0.10, 0.12, 1.0))
    make_box("TV", (tvx, tvy, 0.86), (1.10, 0.07, 0.66), (0.10, 0.10, 0.12, 1.0))
    make_box("TV_Screen", (tvx, tvy + 0.036, 0.86), (1.02, 0.004, 0.58), (0.36, 0.46, 0.56, 1.0))
    make_box("TV_Screen_Anchor_Desk", (tvx - 0.20, tvy + 0.039, 0.74), (0.40, 0.002, 0.14), (0.20, 0.30, 0.52, 1.0))
    make_box("TV_Screen_Ticker", (tvx, tvy + 0.039, 0.62), (1.00, 0.002, 0.05), (0.80, 0.16, 0.14, 1.0))
    make_wall_outlet("Outlet_TV", (tvx + 0.75, 0.0), axis='X', face_sign=1, z=0.30, aged=True)
    # the coffee table between them
    make_box("Coffee_Table", (-3.0, 2.55, 0.40), (1.10, 0.60, 0.04), wood)
    for li, (ox, oy) in enumerate(((-0.50, -0.26), (0.50, -0.26), (-0.50, 0.26), (0.50, 0.26))):
        make_box(f"Coffee_Table_Leg_{li}", (-3.0 + ox, 2.55 + oy, 0.19), (0.04, 0.04, 0.38), wood)
    make_box("Coffee_Table_Remote", (-2.85, 2.50, 0.43), (0.16, 0.05, 0.02), (0.14, 0.14, 0.16, 1.0))
    make_box("Coffee_Table_Mags", (-3.25, 2.58, 0.428), (0.28, 0.22, 0.016), (0.80, 0.68, 0.52, 1.0))
    # a floor lamp at the couch's N end
    make_lathe("FloorLamp_Base", (-4.45, 4.45, 0.0), [(0.0, 0.0), (0.14, 0.0), (0.13, 0.03), (0.02, 0.05), (0.0, 0.05)], (0.24, 0.22, 0.20, 1.0), segments=12)
    make_cyl("FloorLamp_Pole", (-4.45, 4.45, 0.76), 0.012, 1.42, (0.30, 0.28, 0.24, 1.0), segments=6)
    make_lathe("FloorLamp_Shade", (-4.45, 4.45, 1.38), [(0.20, 0.0), (0.14, 0.26), (0.0, 0.26)], (0.86, 0.80, 0.66, 1.0), segments=14)
    make_cyl("FloorLamp_Bulb", (-4.45, 4.45, 1.44), 0.03, 0.06, (0.98, 0.94, 0.80, 1.0), segments=8)
    # the family room's ceiling light
    make_cyl("Family_Ceiling_Light", (-3.0, 3.0, CEIL - 0.05), 0.18, 0.08, (0.96, 0.90, 0.72, 1.0), segments=14)
    # the garage door (closed, a deadbolt) and its switch
    gx = GARAGE_DOOR[0]
    make_box("Garage_Door_Leaf", (gx, 0.0, 1.035), (0.86, 0.045, 2.07), (0.88, 0.86, 0.80, 1.0))
    make_cyl("Garage_Door_Knob", (gx - 0.34, 0.05, 1.0), 0.03, 0.05, (0.62, 0.58, 0.48, 1.0), segments=10, axis='Y')
    make_box("Garage_Door_Deadbolt", (gx - 0.34, 0.035, 1.28), (0.06, 0.025, 0.06), (0.62, 0.58, 0.48, 1.0))
    for nm, x in (("A", gx - GARAGE_DOOR[2] / 2.0 - 0.035), ("B", gx + GARAGE_DOOR[2] / 2.0 + 0.035)):
        make_box(f"Garage_Door_Casing_{nm}", (x, 0.11, 1.07), (0.07, 0.02, 2.14), (0.86, 0.84, 0.78, 1.0))
    make_box("Garage_Door_Casing_Head", (gx, 0.11, 2.115), (GARAGE_DOOR[2] + 0.14, 0.02, 0.07), (0.86, 0.84, 0.78, 1.0))
    make_light_switch("Switch_1", (gx - 0.70, 0.0), axis='X', face_sign=1, z=1.20, aged=True)
    make_box("Key_Hooks", (gx + 0.70, 0.11, 1.45), (0.30, 0.02, 0.08), wood)
    make_box("Key_Hooks_Keys", (gx + 0.66, 0.13, 1.38), (0.04, 0.02, 0.07), (0.70, 0.70, 0.66, 1.0))
    # the hall beyond the opening: its floor, walls, the bedroom door SHUT
    hx = HALL_OPEN[0]
    make_box("Hall_Floor", (hx, -0.75, -0.01), (2.4, 1.3, 0.02), COL_FLOOR)
    make_wall("Hall_Wall_S", (hx, -1.50, 0), length=2.6, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    for nm, x, bb in (("Hall_Wall_W", hx - 1.20, +1), ("Hall_Wall_E", hx + 1.20, -1)):
        make_wall(nm, (x, -0.75, 0), length=1.3, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_box("Hall_Ceil", (hx, -0.75, CEIL + 0.01), (2.4, 1.3, 0.02), (0.92, 0.90, 0.86, 1.0))
    make_box("Bedroom_Door_Leaf", (hx + 0.20, -1.38, 1.035), (0.84, 0.04, 2.07), (0.86, 0.84, 0.78, 1.0))
    make_cyl("Bedroom_Door_Knob", (hx + 0.52, -1.34, 1.0), 0.028, 0.05, (0.62, 0.58, 0.48, 1.0), segments=8, axis='Y')
    make_box("Hall_Photo", (hx - 0.70, -1.385, 1.55), (0.36, 0.02, 0.28), (0.20, 0.16, 0.12, 1.0))
    make_box("Hall_Photo_Image", (hx - 0.70, -1.373, 1.55), (0.30, 0.004, 0.22), (0.62, 0.56, 0.46, 1.0))


def build_family_fill():
    """DRAFT 5 · THE FILL: the doubled room read as bare floor. Bill's
    recliner facing the TV, the area rug under the coffee table, a
    bookcase on the W wall, family photos, Daisy's bowls by the counter
    end, the boots and Bill's work jacket by the garage door."""
    wood = (0.52, 0.40, 0.26, 1.0)
    # the area rug (a border round a field)
    make_box("Family_Rug_Border", (-3.0, 2.95, 0.006), (2.90, 2.40, 0.006), (0.40, 0.26, 0.20, 1.0))
    make_box("Family_Rug_Field", (-3.0, 2.95, 0.010), (2.60, 2.10, 0.004), (0.62, 0.46, 0.34, 1.0))
    # Bill's recliner, facing S at the TV
    rx, ry = -4.40, 2.55
    rc = (0.36, 0.30, 0.24, 1.0)
    make_chamfer_box("Recliner_Base", (rx, ry, 0.22), (0.86, 0.86, 0.44), rc)
    make_chamfer_box("Recliner_Back", (rx, ry + 0.36, 0.72), (0.86, 0.16, 0.66), rc)
    for nm, ox in (("W", -0.37), ("E", 0.37)):
        make_chamfer_box(f"Recliner_Arm_{nm}", (rx + ox, ry - 0.02, 0.56), (0.13, 0.80, 0.26), rc)
    make_chamfer_box("Recliner_Cushion", (rx, ry - 0.06, 0.49), (0.60, 0.66, 0.10), (0.42, 0.36, 0.28, 1.0))
    make_box("Recliner_Lever", (rx + 0.445, ry - 0.10, 0.40), (0.02, 0.04, 0.10), (0.20, 0.20, 0.20, 1.0))
    make_box("Recliner_Sentinel", (rx + 0.36, ry + 0.05, 0.705), (0.20, 0.30, 0.02), (0.86, 0.84, 0.78, 1.0))
    # the W-wall bookcase N of the floor lamp
    bx0, by0, by1 = -ROOM_W/2.0 + 0.10, 4.75, 5.75
    make_box("Family_Case_Back", (bx0 + 0.01, (by0 + by1) / 2.0, 0.90), (0.02, by1 - by0, 1.80), wood)
    for nm, y in (("S", by0 + 0.01), ("N", by1 - 0.01)):
        make_box(f"Family_Case_Side_{nm}", (bx0 + 0.18, y, 0.90), (0.34, 0.02, 1.80), wood)
    for si, z in enumerate((0.05, 0.50, 0.95, 1.40, 1.79)):
        make_box(f"Family_Case_Shelf_{si}", (bx0 + 0.18, (by0 + by1) / 2.0, z), (0.34, by1 - by0 - 0.04, 0.025), wood)
    for si, z in enumerate((0.0625, 0.5125, 0.9625, 1.4125)):
        y = by0 + 0.04
        k = 0
        while y < by1 - 0.06:
            t = 0.035 + 0.01 * ((k + si) % 3)
            if si == 3 and k == 4:
                make_box("Family_Case_Trophy", (bx0 + 0.20, y + 0.08, z + 0.12), (0.10, 0.10, 0.24), (0.80, 0.66, 0.30, 1.0))
                y += 0.20
            else:
                h = 0.20 + 0.03 * ((k * 3 + si) % 4)
                make_box(f"Family_Case_Book_{si}_{k}", (bx0 + 0.22, y + t / 2.0, z + h / 2.0), (0.22, t, h), P.SNACK_TINTS[(k + si * 2) % len(P.SNACK_TINTS)])
                y += t + 0.004
            k += 1
    # family photos on the N wall either side of the family-room window
    for k, (x, w, h) in enumerate(((-4.35, 0.40, 0.50), (-1.85, 0.50, 0.40), (-1.30, 0.30, 0.36))):
        make_box(f"Family_Photo_{k}_Frame", (x, ROOM_D - 0.115, 1.62), (w, 0.03, h), (0.30, 0.22, 0.16, 1.0))
        make_box(f"Family_Photo_{k}_Image", (x, ROOM_D - 0.132, 1.62), (w - 0.08, 0.004, h - 0.08), ((0.60, 0.56, 0.48, 1.0), (0.44, 0.52, 0.40, 1.0), (0.66, 0.60, 0.52, 1.0))[k])
    # Daisy's bowls by the counter's W end
    for k, (ox, col) in enumerate(((0.0, (0.66, 0.70, 0.74, 1.0)), (0.26, (0.62, 0.22, 0.18, 1.0)))):
        make_lathe(f"Daisy_Bowl_{k}", (-1.35 + ox, 5.85, 0.0), [(0.0, 0.0), (0.11, 0.0), (0.12, 0.07), (0.10, 0.07), (0.0, 0.02)], col, segments=12)
    make_box("Daisy_Bowl_Mat", (-1.22, 5.85, 0.004), (0.56, 0.32, 0.008), (0.30, 0.34, 0.40, 1.0))
    # the garage door's corner: boots on a tray, Bill's work jacket on a hook
    gx = GARAGE_DOOR[0]
    make_box("Boot_Tray", (gx + 0.80, 0.34, 0.012), (0.60, 0.40, 0.024), (0.16, 0.16, 0.18, 1.0))
    for k, (ox, oy) in enumerate(((-0.14, -0.05), (0.0, -0.05), (0.14, 0.06))):
        make_box(f"Boot_{k}", (gx + 0.80 + ox, 0.34 + oy, 0.105), (0.11, 0.27, 0.16), (0.30, 0.24, 0.18, 1.0))
    make_box("Jacket_Hook", (gx + 0.62, 0.13, 1.70), (0.03, 0.05, 0.03), (0.60, 0.58, 0.52, 1.0))
    make_box("Work_Jacket", (gx + 0.62, 0.17, 1.28), (0.48, 0.06, 0.82), (0.34, 0.38, 0.28, 1.0))


# ── DRAFT 5 · THE BIGGER ROOM (2026-10-09, lore/_SET_DETAIL_PLAYBOOK.md) ──
from _props.plan import shifted
_OLD = dict(ROOM_W=6.0, ROOM_D=5.0)
SH_TF = (2.0, 0.8)      # the table + pendant + table props, the fridge, the E window, the E yard
SH_W = (-2.0, 1.0)      # the couch + Daisy's spot, the plant, the calendar
HALL_OPEN = (-0.40, 1.05, 1.00, 2.10)
GARAGE_DOOR = (3.70, 1.04, 0.86, 2.08)


def _in(sh):
    return shifted(globals(), sh[0], sh[1], extra=("make_wall_clock", "make_floor_plant", "make_calendar", "make_coffee_pots"), **_OLD)


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_counter_dressing()
    build_clock()
    build_wear_counter()
    with _in(SH_TF):
        build_table(); build_table_dressing(); build_fridge(); build_window(); build_ceiling_infra()
        build_hero_props_2026_09(); build_wear_table(); build_wear_fridge(); build_eyard()
    with _in(SH_W):
        build_plant(); build_calendar()
    build_hero_props()
    build_family_room()
    build_family_fill()
    build_draft4_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/kowalski_kitchen.glb"))
    print(f"\n[build_kowalski_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
