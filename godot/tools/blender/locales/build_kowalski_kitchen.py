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

DRAFT 5 targets: the upper cabinet doors with pulls and one ajar; the
dish rack's dishes; the stair treads with risers and a runner; the TV
on a stand with its cord; the couch's throw; Deck: the ch19 establish
under the under-cabinet light alone.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_table, make_chair
from _props import palette as P
from _props.geometry import (clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe,
                             make_tube, make_rot_box, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

# 2026-09-25: the counter run and the stove stood at ROOM_D-0.45 — 0.55 m off the N wall in every kitchen from this template; ROOM_D-0.45 puts their backs on the wall face
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.92, 0.86, 0.74, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.74, 0.58, 0.38, 1.0); COL_SEAM = (0.42, 0.30, 0.18, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_ACCENT = (0.62, 0.42, 0.22, 1.0)
# the kitchen on the kit (2026-10-07): the Kowalskis' honey maple and
# butcher-block laminate; the counter stays at the 0.92 every dressing
# prop already stands on
from _props import kitchen_kit as K
Y_BACK = ROOM_D - 0.10
TOP_Z = 0.92
SINK_X, RANGE_X = -ROOM_W/4.0, ROOM_W/4.0
HOT_X0 = RANGE_X - 0.42 - 0.46        # the hot sauce cabinet's left edge
MAPLE = (0.58, 0.44, 0.28, 1.0); MAPLE_DK = (0.46, 0.34, 0.22, 1.0)
BLOCK = (0.66, 0.50, 0.32, 1.0); BLOCK_EDGE = (0.50, 0.36, 0.22, 1.0)
PEWTER = (0.48, 0.48, 0.46, 1.0); BISCUIT = (0.90, 0.84, 0.72, 1.0)

from _props.structure import make_frame_ring   # (2026-10-07: the frame boards → rings)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # (2026-10-07, window_backing_audit) the loop unrolled: Wall_E is cut
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1, openings=[(3.000, 1.550, 1.500, 1.100)])
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1, openings=[(-1.5, 1.52, 1.50, 1.00)])   # cut 2026-10-07: the window was a pane on a solid wall
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
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
    K.base_run("Counter", -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, Y_BACK, top_z=TOP_Z,
               body=MAPLE, top=BLOCK, edge=BLOCK_EDGE, pull=PEWTER, rail=MAPLE_DK,
               gaps=[(RANGE_X - 0.38, RANGE_X + 0.38)])
    K.sink("Sink", SINK_X, Y_BACK, TOP_Z)
    K.range_("Stove", RANGE_X, Y_BACK, TOP_Z)
    for nm, a, b in (("Upper_W", -ROOM_W/2.0 + 0.10, SINK_X - 0.86),
                     ("Upper_Mid", SINK_X + 0.86, HOT_X0),
                     ("Upper_E", RANGE_X + 0.42, ROOM_W/2.0 - 0.10)):
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
    for nm, a, b in (("Splash_W", -ROOM_W/2.0 + 0.10, SINK_X - 0.86), ("Splash_E", SINK_X + 0.86, ROOM_W/2.0 - 0.10)):
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
    make_wall_clock("Clock", (0.0, 4.900, CEIL-0.50), frozen_hour=8, frozen_min=15, facing='-Y')

def build_window():
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    make_frame_ring("Window_E_Frame", (ROOM_W/2.0-0.12, ROOM_D/2.0+0.5, 1.55), (0.04, 1.60, 1.20), P.METAL_STEEL)
    make_box("Window_E_Glass", (ROOM_W/2.0-0.1425, ROOM_D/2.0+0.5, 1.55), (0.005, 1.50, 1.10), (0.78, 0.84, 0.86, 0.55))

def build_ceiling_infra():
    # Family kitchen: flush dome + over-table pendant, no shop tubes
    make_cyl("Ceiling_Dome", (0.0, 1.6, CEIL-0.10), 0.16, 0.16, (0.96, 0.90, 0.72, 1.0), segments=12)
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

def build_dressing():
    """Counter + table + wall dressing so it reads as a family kitchen."""
    cw_x = -ROOM_W/4.0; cw_y = ROOM_D-0.45
    make_coffee_pots("Coffee", (cw_x-1.0, cw_y+0.50, 0.94), pots=1)   # the kit puts a lone pot 0.5 in front of its anchor (2026-09-25)
    make_box("DishRack_Base", (cw_x+0.9, cw_y, TOP_Z+0.015), (0.34, 0.30, 0.03), P.METAL_STEEL)
    for ti in range(5):
        make_box(f"DishRack_Tine_{ti}", (cw_x+0.74+ti*0.06, cw_y, TOP_Z+0.11), (0.01, 0.24, 0.16), P.METAL_STEEL)
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 2.0, 1.6))
    # Table centrepiece: napkin holder + salt & pepper
    tx, ty = 0.0, ROOM_D/2.0
    make_box("NapkinHolder", (tx, ty, 0.82), (0.14, 0.06, 0.12), (0.86, 0.84, 0.80, 1.0))
    for nm, sx_, col in (("Salt", tx+0.16, (0.92, 0.92, 0.90, 1.0)), ("Pepper", tx+0.22, (0.28, 0.24, 0.22, 1.0))):
        make_lathe(nm, (sx_, ty, 0.76), [(0.02, 0.0), (0.025, 0.01), (0.025, 0.07), (0.018, 0.09), (0.02, 0.10), (0.0, 0.105)], col, segments=8)
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
    make_window("Sink_Window", (-1.5, ROOM_D - 0.10, 1.52), width=1.50, height=1.00, see_through=True)
    # Couch + Daisy's spot + the muted noon news
    make_chamfer_box("Couch_Base", (-2.35, 2.0, 0.19), (0.85, 2.00, 0.38), (0.44, 0.38, 0.30, 1.0))   # on the floor (2026-09-23: 5 cm over it)
    make_chamfer_box("Couch_Back", (-2.72, 2.0, 0.62), (0.18, 2.00, 0.58), (0.40, 0.34, 0.27, 1.0))
    for py in (1.5, 2.5):
        make_chamfer_box(f"Couch_Cushion_{py:.1f}", (-2.28, py, 0.46), (0.70, 0.85, 0.14), (0.48, 0.42, 0.34, 1.0))
    make_chamfer_box("TV", (2.85, 2.0, 1.15), (0.06, 0.85, 0.50), (0.10, 0.10, 0.12, 1.0))
    make_box("TV_Screen", (2.80, 2.0, 1.15), (0.01, 0.75, 0.42), (0.32, 0.38, 0.44, 1.0))
    # Stair mouth at the S gap edge
    make_box("Stair_Newel", (0.92, 0.15, 0.60), (0.10, 0.10, 1.20), wood)
    for s in range(3):
        make_box(f"Stair_Tread_{s}", (1.4, 0.20 + s * 0.28, (0.185 + s * 0.18) / 2.0), (0.80, 0.28, 0.185 + s * 0.18), wood)   # solid step (2026-09-08)


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
    """DRAFT 4 (2026-09-18, lore/_VISUAL_PROGRAM.md §3; 7 placements). A
    family kitchen's WEAR: the path from the stair mouth to the table
    and the counter, the chairs' floor patches, the counter's edge, the
    sink's drip line, the fridge door's hand patch, Daisy's spot on the
    couch. D3: the switch, outlets, cords from the TV, the coffee maker
    and the fridge; the under-cabinet light's own switch. D5: the
    backyard through the sink window (the shared helper) and Gracie's
    dad's yard through the east window.
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_light_switch, make_wall_outlet, make_cord_run, make_backyard_view
    floor_dk = (0.58, 0.46, 0.30, 1.0)
    tx, ty = 0.0, ROOM_D/2.0
    make_traffic_wear("Wear_Path_Entry_A", [(0.0, 0.5), (0.0, 1.5), (0.0, 1.9)], width=0.5, tint=floor_dk)
    make_traffic_wear("Wear_Path_B", [(-0.3, 3.1), (-1.0, 3.5), (-1.5, 3.7)], width=0.42, tint=floor_dk)
    for ci, (cx, cy) in enumerate([(tx-0.80, ty), (tx+0.80, ty), (tx, ty-0.62), (tx, ty+0.62)]):
        make_floor_stain(f"Wear_Patch_Seat_{ci}", (cx, cy), radius=0.26, tint=(0.66, 0.52, 0.34, 1.0), segments=10)
    make_box("Wear_Elbow_Strip", (-ROOM_W/4.0, Y_BACK-0.62+0.02, TOP_Z+0.002), (2.2, 0.06, 0.004), (0.50, 0.36, 0.22, 1.0))
    make_scuff_band("Wear_Drip", (-ROOM_W/4.0, Y_BACK-0.62-0.024), 0.6, axis='X', height=0.12, band_z=0.60, tint=(0.62, 0.52, 0.34, 1.0))
    make_box("Wear_Hand_Patch", (ROOM_W/2.0-0.55-0.362, 1.0-0.10, 1.30), (0.003, 0.14, 0.20), (0.74, 0.74, 0.76, 1.0))
    make_chamfer_box("Wear_Daisy_Spot", (-2.28, 1.5, 0.535), (0.50, 0.55, 0.02), (0.42, 0.36, 0.30, 1.0), chamfer=0.008)
    for hi in range(6):
        make_rot_box(f"Wear_Hair_{hi}", (-2.35 + 0.08 * (hi % 3), 1.35 + 0.10 * (hi // 3), 0.548), (0.03, 0.004, 0.002), (0.80, 0.72, 0.56, 1.0), yaw=0.6 * hi)
    # D3
    make_light_switch("Switch_1", (1.30, 0.0), axis='X', face_sign=1, z=1.20, aged=True)
    make_light_switch("Switch_2", (-0.20, ROOM_D), axis='X', face_sign=-1, z=1.35, aged=True)
    make_wall_outlet("Outlet_E_1", (ROOM_W/2.0, 2.0), axis='Y', face_sign=-1, z=1.00, aged=True)
    make_cord_run("Cord_1", (2.82, 2.2, 0.92), (ROOM_W/2.0 - 0.13, 2.0, 1.00), sag=0.02)
    make_wall_outlet("Outlet_N_1", (-2.55, ROOM_D), axis='X', face_sign=-1, z=1.10, aged=True)
    make_cord_run("Cord_2", (-2.45, ROOM_D-0.45+0.10, 0.96), (-2.55, ROOM_D - 0.12, 1.10), sag=0.03)
    make_wall_outlet("Outlet_E_2", (ROOM_W/2.0, 0.55), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_cord_run("Cord_3", (ROOM_W/2.0-0.22, 0.75, 0.10), (ROOM_W/2.0 - 0.13, 0.55, 0.30), sag=0.0)
    # D5
    make_backyard_view("Yard", ROOM_D, span=7.0, tree=(2.4, 3.2))
    make_box("EYard_Lawn", (ROOM_W/2.0 + 3.0, 3.0, -0.03), (6.0, 8.0, 0.05), (0.40, 0.48, 0.28, 1.0))
    make_lathe("EYard_Tree", (ROOM_W/2.0 + 3.5, 3.4, 0.0), [(0.16, 0.0), (0.12, 1.2), (0.09, 2.6), (0.0, 2.6)], (0.38, 0.30, 0.22, 1.0), segments=8)
    from _props.geometry import make_blob
    make_blob("EYard_Canopy", (ROOM_W/2.0 + 3.5, 3.4, 3.6), 1.5, (0.30, 0.42, 0.24, 1.0), noise=0.22, seed=23, squash=0.8)
    make_chamfer_box("EYard_Mower", (ROOM_W/2.0 + 1.6, 2.2, 0.165), (0.55, 0.85, 0.34), (0.66, 0.20, 0.16, 1.0), chamfer=0.02)   # on the lawn (2026-09-23: 2 cm over it)
    make_tube("EYard_Mower_Handle", [(ROOM_W/2.0 + 1.6 - 0.2, 2.2 - 0.4, 0.33), (ROOM_W/2.0 + 1.6 - 0.2, 2.2 - 1.1, 0.93), (ROOM_W/2.0 + 1.6 + 0.2, 2.2 - 1.1, 0.93), (ROOM_W/2.0 + 1.6 + 0.2, 2.2 - 0.4, 0.33)], 0.012, (0.30, 0.30, 0.32, 1.0), segments=5)


def main():
    clear_scene()
    build_shell()
    build_counter()
    build_table()
    build_fridge()
    build_clock()
    build_window()
    build_ceiling_infra()
    build_dressing()
    build_hero_props()
    build_hero_props_2026_09()
    build_draft4_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/kowalski_kitchen.glb"))
    print(f"\n[build_kowalski_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
