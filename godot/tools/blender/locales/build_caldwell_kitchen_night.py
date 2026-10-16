"""caldwell_kitchen_night — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_table, make_chair
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.detail import (make_traffic_wear, make_floor_stain,
                           make_wall_tint_band, make_threshold,
                           make_wall_outlet, make_light_switch)

# 2026-09-25: the counter run and the stove stood at ROOM_D-0.45 — 0.55 m off the N wall in every kitchen from this template; ROOM_D-0.45 puts their backs on the wall face
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall":(0.92,0.86,0.74,1.0),"baseboard":(0.42,0.32,0.22,1.0)}
COL_FLOOR = (0.74,0.58,0.38,1.0); COL_SEAM = (0.42,0.30,0.18,1.0); COL_WOOD = (0.46,0.34,0.22,1.0)
COL_ACCENT = (0.62,0.42,0.22,1.0)
# Linda Caldwell's kitchen on the kit (2026-10-08): pale sage cabinets,
# cream laminate with a chrome edge, the pink tile, chrome pulls
from _props import kitchen_kit as K
from _props.geometry import make_lathe, make_tube
Y_BACK = ROOM_D - 0.10
TOP_Z = 0.92
SINK_X, RANGE_X = -1.5, ROOM_W/4.0
SAGE = (0.64, 0.72, 0.60, 1.0); SAGE_DK = (0.52, 0.60, 0.50, 1.0)
CREAM = (0.92, 0.88, 0.78, 1.0); CHROME = (0.80, 0.82, 0.84, 1.0)
PINK = (0.90, 0.74, 0.74, 1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1, openings=[(-1.5, 1.52, 1.20, 1.00)])   # cut 2026-10-07: its window was a pane on a solid wall
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)

def build_counter():
    """The N run on the kitchen kit (2026-10-08: a store counter and a box
    stove). The sink under the window — "Maya, in the kitchen, pouring
    herself a glass of water before bed, pauses at the window" — the
    range, uppers clear of the window and the clock, the pink tile, and
    the sill with the radio on it ("The radio, on the windowsill, stays
    off")."""
    K.base_run("Counter", -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, Y_BACK, top_z=TOP_Z,
               body=SAGE, top=CREAM, edge=CHROME, pull=CHROME, rail=SAGE_DK,
               gaps=[(RANGE_X - 0.38, RANGE_X + 0.38)])
    K.sink("Sink", SINK_X, Y_BACK, TOP_Z)
    K.range_("Stove", RANGE_X, Y_BACK, TOP_Z)
    for nm, a, b in (("Upper_W", -ROOM_W/2.0 + 0.10, SINK_X - 0.75), ("Upper_Mid", 0.40, RANGE_X - 0.42),
                     ("Upper_E", RANGE_X + 0.42, ROOM_W/2.0 - 0.10)):
        K.upper_run(nm, a, b, Y_BACK, z0=1.46, z1=2.20, body=SAGE, pull=CHROME, rail=SAGE_DK)
    K.backsplash("Splash", -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, Y_BACK, TOP_Z, 1.00, tile=PINK,
                 grout=(0.78, 0.62, 0.62, 1.0))
    # the sill, and her radio on it — off
    make_box("Window_Sill", (SINK_X, Y_BACK - 0.07, 1.005), (1.34, 0.14, 0.03), CREAM)
    rx = SINK_X - 0.22   # in the opening, clear of the tied-back curtain (2026-10-08)
    make_box("Sill_Radio", (rx, Y_BACK - 0.08, 1.02 + 0.07), (0.26, 0.11, 0.14), (0.88, 0.82, 0.68, 1.0))
    make_box("Sill_Radio_Grille", (rx - 0.05, Y_BACK - 0.1355, 1.02 + 0.07), (0.12, 0.002, 0.10), (0.46, 0.34, 0.24, 1.0))
    make_cyl("Sill_Radio_Dial", (rx + 0.08, Y_BACK - 0.138, 1.02 + 0.07), 0.03, 0.006, (0.94, 0.86, 0.56, 1.0), axis='Y', segments=12)
    make_box("Sill_Radio_Handle", (rx, Y_BACK - 0.08, 1.02 + 0.15), (0.16, 0.02, 0.02), (0.46, 0.34, 0.24, 1.0))
    # the percolator on the back burner
    make_lathe("Percolator", (RANGE_X + 0.19, Y_BACK - 0.33 + 0.16, TOP_Z), [(0.07, 0.0), (0.08, 0.04), (0.06, 0.20), (0.05, 0.24), (0.0, 0.24)],
               CHROME, segments=12)
    make_lathe("Percolator_Knob", (RANGE_X + 0.19, Y_BACK - 0.33 + 0.16, TOP_Z + 0.24), [(0.02, 0.0), (0.02, 0.03), (0.0, 0.04)],
               (0.70, 0.74, 0.78, 1.0), segments=8)
    make_tube("Percolator_Spout", [(RANGE_X + 0.25, Y_BACK - 0.17, TOP_Z + 0.16), (RANGE_X + 0.29, Y_BACK - 0.17, TOP_Z + 0.20)], 0.01, CHROME)

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    # DETAIL DRAFT 3 (2026-09-06): the table and its four chairs through the
    # furniture kit — turned legs, aprons, a stretcher; spindled chair backs
    # turned away from the table. Names keep Table_Top / Chair_N_Seat.
    make_table("Table", tx, ty, w=1.20, d=0.80, h=0.76, wood=COL_WOOD)
    for ci, (cx, cy, yaw) in enumerate([(tx-0.80, ty, -1.5708), (tx+0.80, ty, 1.5708), (tx, ty-0.62, 0.0), (tx, ty+0.62, 3.1416)]):
        make_chair(f"Chair_{ci}", cx, cy, yaw=yaw, wood=COL_WOOD)

def build_fridge():
    fx, fy = +ROOM_W/2.0 - 0.55, 1.0
    make_box("Fridge_Body", (fx, fy, 1.00), (0.70, 0.70, 2.00), (0.82, 0.82, 0.84, 1.0))
    make_box("Fridge_DoorTop", (fx-0.34, fy, 1.50), (0.04, 0.66, 0.80), (0.82, 0.82, 0.84, 1.0))
    make_box("Fridge_DoorBot", (fx-0.34, fy, 0.40), (0.04, 0.66, 1.00), (0.82, 0.82, 0.84, 1.0))
    make_box("Fridge_Handle", (fx-0.38, fy-0.20, 1.30), (0.04, 0.04, 0.50), P.METAL_STEEL)

def build_dressing():
    cw_x = -ROOM_W/4.0; cw_y = ROOM_D-0.45
    make_calendar("Calendar", (-ROOM_W/2.0+0.1025, 2.0, 1.6))
    tx, ty = 0.0, ROOM_D/2.0
    make_box("NapkinHolder", (tx, ty, 0.82), (0.14, 0.06, 0.12), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Salt", (tx+0.16, ty, 0.80), 0.025, 0.10, (0.92, 0.92, 0.90, 1.0), segments=8)
    make_cyl("Pepper", (tx+0.22, ty, 0.80), 0.025, 0.10, (0.28, 0.24, 0.22, 1.0), segments=8)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, 0.7, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.60, 0.40, 0.26, 1.0)})

def build_clock():
    make_wall_clock("Clock", (0.0, 4.900, CEIL-0.50), frozen_hour=11, frozen_min=5, facing='-Y')

def build_ceiling_infra():
    # Domestic light, not shop tubes (hero-prop pass)
    make_cyl("Ceiling_Dome", (0.0, 2.2, CEIL-0.10), 0.15, 0.14, (0.94, 0.88, 0.70, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, 2.2, CEIL))


def build_hero_props():
    """2026-08-03 tail pass: the night window Maya pauses at (the
    dogs), the water glass, the stair mouth, burners + oven face on
    the blank stove."""
    make_window("Window_N", (-1.5, ROOM_D-0.10, 1.52), width=1.20, height=1.00, see_through=True)
    make_cyl("Water_Glass", (SINK_X + 0.62, Y_BACK - 0.40, TOP_Z + 0.06), 0.035, 0.12, (0.55, 0.62, 0.66, 0.5), segments=8)
    make_box("Stair_Newel", (0.92, 0.15, 0.60), (0.10, 0.10, 1.20), (0.46, 0.34, 0.22, 1.0))
    for s in range(3):
        make_box(f"Stair_Tread_{s}", (1.4, 0.20 + s * 0.28, (0.185 + s * 0.18) / 2.0), (0.80, 0.28, 0.185 + s * 0.18), (0.46, 0.34, 0.22, 1.0))   # solid step (2026-09-08)
    # (2026-10-08: the burners and oven face are the kit range's own)



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (generic template pass per
    lore/_SET_DETAIL_PLAYBOOK.md): the entry walk-line, a work-zone
    stain, ceiling gather on the long walls, a threshold, and the
    switch/outlet pair every room earns. Per-locale wear
    PERSONALITY (whose feet, whose spills) is the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    stain = (COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0)
    pw = PAL_WALL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Entry", [(0.0, 0.6), (0.0, ROOM_D * 0.55)],
                      width=0.75, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62),
                     radius=0.24, tint=stain)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_threshold("Threshold_Entry", (0.0, 0.10), width=1.9, axis='X')
    make_light_switch("Switch_Entry", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)



def build_lived_in_2026_10():
    """LINDA'S KITCHEN, LIVED IN (2026-10-08). The user: "Too bare and
    empty, the Caldwell." She has kept this kitchen since 1979: the china
    hutch, the wall phone with its coiled cord, the canisters and the
    bread box, the spice shelf, the soup on the stove ("porch, granddaughter
    at the shop, soup in the kitchen"), a dish towel on the oven handle,
    café curtains and violets on the sill by the radio, a gingham cloth and
    a fruit bowl on the table, cookbooks and photographs on the east wall,
    the fridge door's magnets, a chair rail, a braided rug at the sink."""
    from _props.geometry import make_blob, make_chamfer_box
    WF, EF = -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10        # the W / E wall faces
    walnut, walnut_dk = (0.46, 0.32, 0.20, 1.0), (0.34, 0.22, 0.14, 1.0)
    china = (0.94, 0.94, 0.90, 1.0); blue = (0.36, 0.48, 0.70, 1.0)
    # ── the china hutch on the W wall ──
    hy0, hy1 = 2.70, 3.90; hc = (hy0 + hy1) / 2.0; hw = hy1 - hy0
    make_box("Hutch_Base", (WF + 0.23, hc, 0.45), (0.46, hw, 0.90), walnut)
    for di, dy in enumerate((-0.30, 0.30)):
        make_box(f"Hutch_Base_Door_{di}", (WF + 0.465, hc + dy, 0.42), (0.01, 0.56, 0.66), walnut_dk)
        make_cyl(f"Hutch_Base_Knob_{di}", (WF + 0.48, hc + dy * 0.2, 0.55), 0.015, 0.02, (0.70, 0.58, 0.30, 1.0), axis='X', segments=8)
    make_box("Hutch_Top", (WF + 0.25, hc, 0.915), (0.50, hw + 0.04, 0.03), walnut)
    make_box("Hutch_Back", (WF + 0.01, hc, 1.47), (0.02, hw, 1.08), walnut_dk)
    for e in (-1, 1):
        make_box(f"Hutch_Side_{e:+d}", (WF + 0.16, hc + e * (hw / 2.0 - 0.015), 1.47), (0.30, 0.03, 1.08), walnut)
    make_box("Hutch_Crown", (WF + 0.17, hc, 2.04), (0.34, hw + 0.06, 0.06), walnut)
    for si, sz in enumerate((1.28, 1.64)):
        make_box(f"Hutch_Shelf_{si}", (WF + 0.16, hc, sz), (0.28, hw - 0.06, 0.02), walnut)
        for pi in range(4):   # plates on edge in the plate groove
            make_cyl(f"Hutch_Plate_{si}_{pi}", (WF + 0.08, hy0 + 0.20 + pi * 0.27, sz + 0.12), 0.11, 0.015, china if pi % 2 else blue, axis='X', segments=16)
        for ci in range(3):   # cups in front
            make_cyl(f"Hutch_Cup_{si}_{ci}", (WF + 0.22, hy0 + 0.32 + ci * 0.30, sz + 0.05), 0.035, 0.07, china, segments=10)
    make_box("Hutch_Base_Doily", (WF + 0.25, hc, 0.932), (0.30, 0.50, 0.004), (0.96, 0.95, 0.92, 1.0))
    make_lathe("Hutch_Vase", (WF + 0.25, hc, 0.934), [(0.04, 0.0), (0.06, 0.06), (0.03, 0.16), (0.04, 0.20), (0.0, 0.20)], blue, segments=12)
    # ── the wall phone by the door, its coiled cord ──
    make_box("Wall_Phone", (WF + 0.04, 1.15, 1.45), (0.08, 0.12, 0.22), (0.86, 0.80, 0.66, 1.0))
    make_box("Wall_Phone_Handset", (WF + 0.10, 1.15, 1.47), (0.05, 0.06, 0.22), (0.86, 0.80, 0.66, 1.0))
    make_tube("Wall_Phone_Cord", [(WF + 0.10, 1.15, 1.36), (WF + 0.12, 1.12, 1.20), (WF + 0.10, 1.18, 1.05), (WF + 0.12, 1.12, 0.92),
                                  (WF + 0.08, 1.15, 0.86)], 0.008, (0.86, 0.80, 0.66, 1.0))
    make_box("Wall_Phone_Notepad", (WF + 0.01, 1.42, 1.30), (0.01, 0.12, 0.16), (0.96, 0.92, 0.70, 1.0))
    # ── the chair rail and the painted lower wall, W and E ──
    lower = (0.80, 0.84, 0.74, 1.0)
    for nm, x, y0, y1, sgn in (("W", WF, 0.25, hy0 - 0.02, 1), ("E", EF, 1.45, 4.20, -1)):
        make_box(f"ChairRail_{nm}", (x + sgn * 0.012, (y0 + y1) / 2.0, 0.90), (0.024, y1 - y0, 0.05), walnut)
        make_box(f"LowerWall_{nm}", (x + sgn * 0.002, (y0 + y1) / 2.0, 0.52), (0.004, y1 - y0, 0.71), lower)
    # ── the E wall: the cookbook shelf, two photographs ──
    make_box("Cookbook_Shelf", (EF - 0.11, 2.50, 1.48), (0.22, 1.00, 0.025), walnut)
    for bi in range(2):
        make_box(f"Cookbook_Shelf_Bracket_{bi}", (EF - 0.06, 2.10 + bi * 0.80, 1.40), (0.12, 0.02, 0.14), walnut_dk)
    cols = ((0.62, 0.20, 0.18, 1.0), (0.24, 0.36, 0.52, 1.0), (0.86, 0.76, 0.46, 1.0), (0.28, 0.44, 0.30, 1.0), (0.80, 0.46, 0.26, 1.0))
    y = 2.05
    for bi in range(9):
        t = 0.03 + 0.012 * (bi % 3); h = 0.20 + 0.03 * ((bi * 5) % 3)
        make_box(f"Cookbook_{bi}", (EF - 0.11, y + t / 2.0, 1.4925 + h / 2.0), (0.17, t, h), cols[bi % len(cols)])
        y += t + 0.004
    make_box("Recipe_Box", (EF - 0.11, 2.85, 1.5525), (0.14, 0.20, 0.11), (0.78, 0.30, 0.24, 1.0))
    for pi, (py, pz, pw, ph) in enumerate(((3.40, 1.70, 0.30, 0.36), (3.85, 1.62, 0.24, 0.30))):
        make_box(f"Photo_Frame_{pi}", (EF - 0.015, py, pz), (0.03, pw, ph), walnut_dk)
        make_box(f"Photo_Print_{pi}", (EF - 0.031, py, pz), (0.002, pw - 0.06, ph - 0.06), ((0.56, 0.50, 0.42, 1.0), (0.48, 0.46, 0.44, 1.0))[pi])
    # ── the counter: canisters, the bread box, the pill box, the spice shelf ──
    can = (0.92, 0.86, 0.66, 1.0)
    for ci, r in enumerate((0.085, 0.075, 0.065, 0.055)):
        cx = -2.72 + ci * 0.17
        make_lathe(f"Canister_{ci}", (cx, Y_BACK - 0.18, TOP_Z), [(r, 0.0), (r, 0.22 - ci * 0.03), (0.0, 0.22 - ci * 0.03)], can, segments=12)
        make_cyl(f"Canister_{ci}_Lid", (cx, Y_BACK - 0.18, TOP_Z + 0.22 - ci * 0.03 + 0.01), r + 0.004, 0.02, (0.42, 0.62, 0.48, 1.0), segments=12)
    make_chamfer_box("Bread_Box", (0.10, Y_BACK - 0.20, TOP_Z + 0.11), (0.40, 0.26, 0.22), (0.86, 0.84, 0.80, 1.0), chamfer=0.03)
    make_box("Bread_Box_Lid_Line", (0.10, Y_BACK - 0.331, TOP_Z + 0.15), (0.38, 0.002, 0.02), (0.42, 0.62, 0.48, 1.0))
    make_box("Pill_Box", (-0.55, Y_BACK - 0.45, TOP_Z + 0.012), (0.20, 0.06, 0.024), (0.60, 0.70, 0.84, 1.0))
    make_box("Magnifier_Handle", (-0.30, Y_BACK - 0.42, TOP_Z + 0.008), (0.10, 0.02, 0.016), (0.20, 0.20, 0.22, 1.0))
    make_cyl("Magnifier_Lens", (-0.22, Y_BACK - 0.42, TOP_Z + 0.006), 0.04, 0.012, (0.70, 0.78, 0.82, 1.0), segments=12)
    make_box("Spice_Shelf", (0.72, Y_BACK - 0.05, 1.20), (0.60, 0.10, 0.02), walnut)
    for si in range(6):
        make_cyl(f"Spice_Jar_{si}", (0.47 + si * 0.10, Y_BACK - 0.05, 1.255), 0.025, 0.09, (0.80, 0.56, 0.30, 1.0) if si % 2 else (0.56, 0.30, 0.20, 1.0), segments=8)
    # ── the soup on the front burner, the towel on the oven handle ──
    sx, sy = RANGE_X - 0.19, Y_BACK - 0.33 - 0.14
    make_cyl("Soup_Pot", (sx, sy, TOP_Z + 0.09), 0.13, 0.18, (0.78, 0.80, 0.82, 1.0), segments=14)
    make_cyl("Soup_Pot_Lid", (sx, sy, TOP_Z + 0.19), 0.135, 0.015, (0.70, 0.72, 0.74, 1.0), segments=14)
    make_cyl("Soup_Pot_Knob", (sx, sy, TOP_Z + 0.21), 0.02, 0.025, (0.16, 0.16, 0.18, 1.0), segments=8)
    for e in (-1, 1):
        make_box(f"Soup_Pot_Handle_{e:+d}", (sx + e * 0.15, sy, TOP_Z + 0.15), (0.04, 0.03, 0.02), (0.16, 0.16, 0.18, 1.0))
    make_box("Dish_Towel", (RANGE_X + 0.15, Y_BACK - 0.66 - 0.075, 0.66), (0.22, 0.01, 0.34), (0.94, 0.90, 0.80, 1.0))
    make_box("Dish_Towel_Stripe", (RANGE_X + 0.15, Y_BACK - 0.66 - 0.081, 0.58), (0.22, 0.002, 0.03), (0.72, 0.24, 0.20, 1.0))
    # ── the window: café curtains, the valance, violets by the radio ──
    gingham = (0.96, 0.86, 0.46, 1.0)
    make_cyl("Curtain_Rod", (SINK_X, Y_BACK - 0.16, 1.56), 0.008, 1.40, (0.80, 0.82, 0.84, 1.0), axis='X', segments=6)
    for e in (-1, 1):   # tied back to the sides, so the radio and the violets show
        make_box(f"Cafe_Curtain_{e:+d}", (SINK_X + e * 0.57, Y_BACK - 0.16, 1.30), (0.22, 0.04, 0.50), gingham)
        make_box(f"Cafe_Curtain_Tie_{e:+d}", (SINK_X + e * 0.57, Y_BACK - 0.16, 1.22), (0.23, 0.05, 0.03), (0.72, 0.24, 0.20, 1.0))
        make_box(f"Curtain_Rod_Bracket_{e:+d}", (SINK_X + e * 0.70, Y_BACK - 0.08, 1.56), (0.02, 0.17, 0.02), (0.80, 0.82, 0.84, 1.0))
    make_box("Valance", (SINK_X, Y_BACK - 0.06, 2.00), (1.40, 0.12, 0.16), gingham)
    for vi, vx in enumerate((SINK_X + 0.12, SINK_X + 0.32)):
        make_lathe(f"Violet_Pot_{vi}", (vx, Y_BACK - 0.07, 1.02), [(0.04, 0.0), (0.05, 0.08), (0.0, 0.08)], (0.74, 0.44, 0.32, 1.0), segments=10)
        make_blob(f"Violet_{vi}", (vx, Y_BACK - 0.07, 1.14), 0.07, (0.30, 0.48, 0.28, 1.0), noise=0.30, seed=50 + vi, squash=0.6)
        make_blob(f"Violet_{vi}_Bloom", (vx, Y_BACK - 0.07, 1.17), 0.035, (0.56, 0.36, 0.70, 1.0), noise=0.20, seed=60 + vi, squash=0.7)
    # ── the table: a gingham cloth, a fruit bowl ──
    cloth = (0.84, 0.70, 0.62, 1.0)
    make_box("Table_Cloth", (0.0, ROOM_D/2.0, 0.765), (1.30, 0.90, 0.006), cloth)
    for k in range(5):   # the check
        make_box(f"Table_Cloth_Check_X{k}", (-0.52 + k * 0.26, ROOM_D/2.0, 0.7685), (0.08, 0.90, 0.001), (0.74, 0.30, 0.26, 1.0))
    for e in (-1, 1):
        make_box(f"Table_Cloth_Drop_X{e:+d}", (e * 0.65, ROOM_D/2.0, 0.66), (0.006, 0.90, 0.21), cloth)
        make_box(f"Table_Cloth_Drop_Y{e:+d}", (0.0, ROOM_D/2.0 + e * 0.45, 0.66), (1.30, 0.006, 0.21), cloth)
    make_lathe("Fruit_Bowl", (-0.30, ROOM_D/2.0 + 0.05, 0.768), [(0.06, 0.0), (0.12, 0.05), (0.13, 0.07), (0.0, 0.07)], blue, segments=14)
    for fi, (fx, fy, col) in enumerate(((-0.33, 2.53, (0.80, 0.24, 0.18, 1.0)), (-0.26, 2.58, (0.94, 0.76, 0.26, 1.0)), (-0.29, 2.50, (0.86, 0.50, 0.20, 1.0)))):
        make_blob(f"Fruit_{fi}", (fx, fy, 0.86), 0.04, col, noise=0.10, seed=70 + fi, squash=0.95)
    # ── the fridge door: magnets, two photographs, a note ──
    fx = ROOM_W/2.0 - 0.55 - 0.35 - 0.002
    for mi, (my, mz, col) in enumerate(((0.80, 1.55, (0.62, 0.48, 0.40, 1.0)), (1.05, 1.42, (0.50, 0.56, 0.62, 1.0)), (0.92, 1.20, (0.96, 0.94, 0.86, 1.0)))):
        make_box(f"Fridge_Photo_{mi}", (fx, my, mz), (0.003, 0.10, 0.13), col)
        make_cyl(f"Fridge_Magnet_{mi}", (fx - 0.004, my, mz + 0.06), 0.012, 0.006, ((0.80, 0.24, 0.18, 1.0), (0.30, 0.50, 0.30, 1.0), (0.94, 0.80, 0.26, 1.0))[mi], axis='X', segments=8)
    # ── the braided rug at the sink ──
    make_cyl("Braided_Rug", (SINK_X, Y_BACK - 1.00, 0.005), 0.42, 0.01, (0.62, 0.40, 0.30, 1.0), segments=20)
    make_cyl("Braided_Rug_Ring", (SINK_X, Y_BACK - 1.00, 0.0105), 0.30, 0.002, (0.46, 0.54, 0.40, 1.0), segments=20)

def main():
    clear_scene()
    build_shell()
    build_counter()
    build_table()
    build_fridge()
    build_dressing()
    build_clock()
    build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_lived_in_2026_10()
    # what is outside the window (2026-10-07, _props/views.py)
    make_view("View_N", "N", ROOM_D, -1.5, kind="back", ground_z=0.0, seed=9)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_kitchen_night.glb"))
    print(f"\n[build_caldwell_kitchen_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
