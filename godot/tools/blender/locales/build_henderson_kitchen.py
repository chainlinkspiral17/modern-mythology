"""Henderson Kitchen — vol6 placement script.

DRAFT 5 (pass 330, 2026-11-10) — THE HOUSE AROUND THE KITCHEN. The S
wall had a 2 m x 2 m open HOLE in it (x -1..1) straight onto the front
lawn: every establishing shot showed the street through it, "the
basement door opens" framed it, and three stair treads stood under the
front window. The text has a front door AND a kitchen doorway ("He
opens the front door quietly ... Jesse, at the kitchen doorway", ch22),
stairs up ("He goes up the stairs"), and a dining room nobody dines in
("the room where the small table that holds the lamp lives", ch23).
The house front (build_henderson_porch_front) is flat: the door, the
kitchen window east of it. So:

    x -10.05      -5.65     -3.25                    +3.25
      +-------------+---------+------------------------+   y 5.5 (back)
      |             |  stair  |  sink        stove     |
      |   DINING    |  up  ^  |                  fridge|
      |  lamp table |  HALL   |       table      bsmt >|
      |             =         =  <- kitchen doorway    |
      +---window----+--door---+---------window---------+   y 0 (front)

The S wall is closed with a wider front window; the kitchen doorway is
a cased opening in the W wall; the hall has the front door, the stair
up along the shared wall (a real flight into a dark well) and a back
door; the dining room across the hall is carpet, a chandelier with no
table under it, and the small table with the lamp.

DRAFT 6 targets: the hall's D2/D3 (wear at the front door, outlets, a
return-air grille), the stair's upper landing past the well, the dining
room's window dressing seen from the porch build (the two fronts do not
yet agree on window positions), cabinet doors ajar, a second camera
area for the hall ("He goes upstairs" plays on a kitchen wide)."""
import math, os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_table, make_chair
from _props.detail import (make_traffic_wear, make_floor_stain, make_scuff_band, make_wall_tint_band,
                           make_wall_outlet, make_light_switch, make_cord_run, make_thermostat, make_threshold)
from _props import palette as P
from _props.geometry import make_blob, clear_scene, make_box, make_chamfer_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings, make_curtains
from _props.views import make_view
from _props import kitchen_kit as K
from _props.geometry import make_lathe, make_tube
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

# 2026-09-25: the counter run and the stove stood at ROOM_D-0.45 — 0.55 m off the N wall in every kitchen from this template; ROOM_D-0.45 puts their backs on the wall face
ROOM_W = 6.5; ROOM_D = 5.5; CEIL = 2.6
PAL_WALL = {"wall": (0.92, 0.86, 0.74, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.74, 0.58, 0.38, 1.0); COL_SEAM = (0.42, 0.30, 0.18, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_ACCENT = (0.62, 0.42, 0.22, 1.0)
# the kitchen on the kit (2026-10-07): the Hendersons' oak and gold
# formica, not the Millers' white shaker
Y_BACK = ROOM_D - 0.10                 # the N wall's room face
TOP_Z = 0.94
SINK_X, RANGE_X = -ROOM_W/4.0, ROOM_W/4.0
OAK = (0.56, 0.42, 0.28, 1.0); OAK_DK = (0.42, 0.30, 0.20, 1.0)
FORMICA = (0.78, 0.66, 0.42, 1.0); FORMICA_EDGE = (0.62, 0.50, 0.30, 1.0)
BRASS = (0.70, 0.58, 0.30, 1.0); ALMOND = (0.90, 0.86, 0.76, 1.0)
# the house around the kitchen (draft 5)
W_X = -ROOM_W / 2.0                    # the shared kitchen / hall wall
DOOR_Y, DOOR_W, DOOR_H = 1.50, 1.10, 2.10   # the kitchen doorway (W wall)
HALL_X0 = -5.65                        # the hall's W wall line (hall 2.2 m clear)
HALL_CX = (HALL_X0 + W_X) / 2.0
DIN_X0, DIN_Y1 = -10.05, 4.70          # the dining room's W and N wall lines
DIN_DOOR_Y, DIN_DOOR_W = 1.80, 1.60    # hall -> dining cased opening
FWIN_X, FWIN_W, FWIN_H = 1.45, 1.50, 1.15   # the kitchen's front window
ST_X0, ST_X1, ST_Y0 = -4.30, W_X - 0.10, 2.30   # the stair up: its open side, the wall side, its foot
ST_N, ST_RISE, ST_RUN = 13, 2.70 / 13.0, 0.25
PAL_HALL = {"wall": (0.90, 0.85, 0.74, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
PAL_DIN = {"wall": (0.70, 0.75, 0.66, 1.0), "baseboard": (0.90, 0.88, 0.82, 1.0)}
HALL_OAK = (0.60, 0.44, 0.27, 1.0); HALL_SEAM = (0.40, 0.28, 0.17, 1.0)
CARPET = (0.66, 0.60, 0.50, 1.0)
TRIM = (0.48, 0.36, 0.24, 1.0)
CASE = 0.08                            # a casing's bar: the rough opening is this much bigger a side

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # the kitchen doorway (draft 5): a cased opening to the hall
    make_wall_with_openings("Wall_W", (W_X, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=+1, openings=[(DOOR_Y, (DOOR_H + CASE) / 2.0, DOOR_W + 2 * CASE, DOOR_H + CASE)])
    # the basement door's opening (2026-10-07: the wall was solid behind a
    # 2 cm dark card — the ch7 hinge opened onto plaster)
    make_wall_with_openings("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=-1, openings=[(1.6, 1.025, 0.85, 2.05)])
    # the window over the sink (2026-10-07): "He stands at the kitchen
    # sink for a long minute ... Through the open window, the cicadas
    # are loud" (ch14) — the N wall was solid and the sink faced plaster
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1, openings=[(SINK_X, 1.67, 1.50, 1.06)])   # 2026-11-10: 1.50 x 1.06 (was 1.20 x 0.92)
    # the house FRONT (draft 5): one wall, the front window in it. It had
    # a 2 m open hole at x -1..1 onto the lawn with a lintel over it.
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1,
                            openings=[(FWIN_X, 1.50, FWIN_W, FWIN_H)])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_counter():
    """The N run on the kitchen kit (2026-10-07): base cabinets wall to
    wall on the N wall's face, the sink under the window, a gap for the
    range, uppers either side of the window and clear of the clock.
    (It was make_counter — a store counter — and a chamfered box.)"""
    K.base_run("Counter", -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, Y_BACK, top_z=TOP_Z,
               body=OAK, top=FORMICA, edge=FORMICA_EDGE, pull=BRASS, rail=OAK_DK,
               gaps=[(RANGE_X - 0.38, RANGE_X + 0.38)])
    K.sink("Sink", SINK_X, Y_BACK, TOP_Z)
    K.range_("Stove", RANGE_X, Y_BACK, TOP_Z)
    K.dishwasher("Dishwasher", SINK_X + 0.90, Y_BACK - 0.62, TOP_Z)
    for nm, a, b in (("Upper_W", -ROOM_W/2.0 + 0.10, SINK_X - 0.90),      # (2026-11-10: the uppers step back for a wider sink window)
                     ("Upper_Mid", SINK_X + 0.90, -0.30),
                     ("Upper_E", RANGE_X + 0.55, ROOM_W/2.0 - 0.10)):
        K.upper_run(nm, a, b, Y_BACK, z0=1.46, z1=2.20, body=OAK, pull=BRASS, rail=OAK_DK)
    K.backsplash("Splash", -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, Y_BACK, TOP_Z, 1.11, tile=ALMOND,
                 grout=(0.76, 0.72, 0.62, 1.0))
    # WEAR (2026-10-07): the formica worn pale at the sink's edge, the
    # runner in front of it, the floor's path sink - stove - table
    make_box("Wear_Formica_Sink", (SINK_X, Y_BACK - 0.60, TOP_Z + 0.001), (0.90, 0.05, 0.002), (0.88, 0.80, 0.58, 1.0))
    make_box("Sink_Runner", (SINK_X, Y_BACK - 0.98, 0.006), (1.20, 0.60, 0.012), (0.42, 0.26, 0.20, 1.0))
    make_box("Sink_Runner_Band", (SINK_X, Y_BACK - 0.98, 0.0125), (1.10, 0.50, 0.002), (0.62, 0.44, 0.30, 1.0))
    from _props.detail import make_traffic_wear
    make_traffic_wear("Wear_Path_Sink", [(SINK_X, Y_BACK - 1.35), (0.0, Y_BACK - 1.70), (RANGE_X, Y_BACK - 0.95)], width=0.45,
                      tint=(0.68, 0.53, 0.35, 1.0))
    # the open window over the sink: sash up, the screen in
    make_window("Sink_Window", (SINK_X, Y_BACK, 1.67), width=1.50, height=1.06, room_dir=-1,
                see_through=True, palette={"frame": (0.92, 0.90, 0.84, 1.0)})
    make_box("Sink_Window_Sill", (SINK_X, Y_BACK - 0.06, 1.67 - 0.53 - 0.02), (1.64, 0.12, 0.04), (0.92, 0.90, 0.84, 1.0))
    # the kettle his mother uses and his father does not (ch20), on the
    # back left burner
    kx, ky = RANGE_X - 0.19, Y_BACK - 0.33 + 0.16
    make_lathe("Kettle", (kx, ky, TOP_Z), [(0.10, 0.0), (0.11, 0.04), (0.10, 0.12), (0.06, 0.17), (0.02, 0.18), (0.0, 0.18)],
               (0.22, 0.42, 0.40, 1.0), segments=14)
    make_tube("Kettle_Spout", [(kx + 0.09, ky, TOP_Z + 0.06), (kx + 0.15, ky, TOP_Z + 0.12), (kx + 0.18, ky, TOP_Z + 0.15)], 0.014, (0.22, 0.42, 0.40, 1.0))
    make_tube("Kettle_Handle", [(kx - 0.06, ky, TOP_Z + 0.16), (kx - 0.02, ky, TOP_Z + 0.24), (kx + 0.04, ky, TOP_Z + 0.16)], 0.010, (0.16, 0.14, 0.12, 1.0))

def build_table():
    tx, ty = 0.0, ROOM_D/2.0
    # DETAIL DRAFT 4 (2026-09-06): table + chairs through the furniture kit
    make_table("Table", tx, ty, w=1.20, d=0.80, h=0.76, wood=COL_WOOD)
    for ci, (cx, cy, yaw) in enumerate([(tx-0.80, ty, -1.5708), (tx+0.80, ty, 1.5708), (tx, ty-0.62, 0.0), (tx, ty+0.62, 3.1416)]):
        make_chair(f"Chair_{ci}", cx, cy, yaw=yaw, wood=COL_WOOD)

def build_clock():
    make_wall_clock("Clock", (0.0, 5.400, CEIL-0.50), frozen_hour=10, frozen_min=38, facing='-Y')

def build_fridge():
    # north of the basement door, not in front of it (2026-09-07: the
    # fridge stood square in the doorway and no lens could see the door)
    fx, fy = +ROOM_W/2.0 - 0.50, 3.0
    make_chamfer_box("Fridge_Body", (fx, fy, 1.00), (0.70, 0.70, 2.00), (0.86, 0.84, 0.80, 1.0))
    make_chamfer_box("Fridge_DoorTop", (fx-0.34, fy, 1.50), (0.04, 0.66, 0.80), (0.86, 0.84, 0.80, 1.0))
    make_chamfer_box("Fridge_DoorBot", (fx-0.34, fy, 0.40), (0.04, 0.66, 1.00), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_Handle", (fx-0.38, fy-0.20, 1.30), (0.04, 0.04, 0.50), P.METAL_STEEL)
    for mi in range(6):
        make_box(f"Magnet_{mi}", (fx-0.36, fy-0.20+mi*0.10, 1.60), (0.005, 0.06, 0.08), P.SNACK_TINTS[mi%len(P.SNACK_TINTS)])

def build_dressing():
    """Counter + table + wall dressing for a working family kitchen."""
    cw_x = -ROOM_W/4.0; cw_y = ROOM_D-0.45
    make_coffee_pots("Coffee", (cw_x-1.0, cw_y+0.50, TOP_Z), pots=1)   # the kit puts a lone pot 0.5 in front of its anchor (2026-09-25)
    make_box("DishRack_Base", (cw_x+0.9, cw_y, TOP_Z+0.015), (0.34, 0.30, 0.03), P.METAL_STEEL)
    for ti in range(5):
        make_box(f"DishRack_Tine_{ti}", (cw_x+0.74+ti*0.06, cw_y, TOP_Z+0.11), (0.01, 0.24, 0.16), P.METAL_STEEL)
    make_calendar("Calendar", (-ROOM_W/2.0+0.1025, 3.30, 1.6))   # north of the doorway (draft 5)
    tx, ty = 0.0, ROOM_D/2.0
    make_box("NapkinHolder", (tx, ty, 0.82), (0.14, 0.06, 0.12), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Salt", (tx+0.16, ty, 0.80), 0.025, 0.10, (0.92, 0.92, 0.90, 1.0), segments=8)
    make_cyl("Pepper", (tx+0.22, ty, 0.80), 0.025, 0.10, (0.28, 0.24, 0.22, 1.0), segments=8)
    make_floor_plant("Plant", (0.12, 0.52, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.60, 0.40, 0.26, 1.0)})

def build_ceiling_infra():
    # A night kitchen lit warm and low — dome + pendant, no tubes
    make_cyl("Ceiling_Dome", (0.0, 1.6, CEIL-0.10), 0.16, 0.16, (0.96, 0.88, 0.68, 1.0), segments=12)
    make_cyl("Table_Pendant_Cord", (0.0, ROOM_D/2.0, CEIL-0.14), 0.008, 0.28, P.METAL_BLACK)
    make_cyl("Table_Pendant_Shade", (0.0, ROOM_D/2.0, CEIL-0.36), 0.15, 0.15, (0.60, 0.44, 0.28, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, ROOM_D/2.0, CEIL))


def build_hero_props():
    """2026-08-03 hero-prop pass: the front kitchen window (the one
    the porch build lights from outside), THE BASEMENT DOOR (the
    ch7 hinge), the stair mouth, the oven face, the microwave, four
    place settings — the fourth, at the head, unset for eight days
    until tonight — and the coffee mugs."""
    wood = (0.48, 0.36, 0.24, 1.0)
    # Front window, S wall east of the doorway — matches the porch
    # build's lit window at x=+2.55
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Front_Window", (FWIN_X, 0.10, 1.50), width=FWIN_W, height=FWIN_H, room_dir=+1, see_through=True)
    make_box("Front_Window_Sill", (FWIN_X, 0.16, 1.50 - FWIN_H / 2.0 - 0.02), (FWIN_W + 0.14, 0.12, 0.04), (0.92, 0.90, 0.84, 1.0))
    # The basement door, E wall, dark stair void behind
    # the frame as a ring (it was a solid board the size of the door) and
    # the door CRACKED — 25 degrees into the kitchen, hinged at its north
    # jamb — onto a real stair going down
    from _props.structure import make_frame_ring
    from _props.geometry import make_rot_box
    import math
    make_frame_ring("Basement_Doorframe", (ROOM_W/2.0-0.04, 1.6, 1.08), (0.10, 1.00, 2.16), wood, bar=0.075)
    crack = math.radians(25.0)
    hx, hy = ROOM_W/2.0 - 0.07, 1.6 + 0.425
    dcx, dcy = hx - math.sin(crack) * 0.425, hy - math.cos(crack) * 0.425
    make_rot_box("Basement_Door", (dcx, dcy, 1.05), (0.05, 0.85, 2.05),
                 (0.52, 0.40, 0.28, 1.0), yaw=-crack)
    # two sunk panels on its kitchen face (draft 5: one flat slab of the
    # darkest brown in the room read as a black card in every low mood)
    nx_, ny_ = -math.cos(crack), math.sin(crack)
    for pn, pz, ph in (("Upper", 1.50, 0.86), ("Lower", 0.54, 0.76)):
        make_rot_box(f"Basement_Door_Panel_{pn}", (dcx + nx_ * 0.027, dcy + ny_ * 0.027, pz), (0.006, 0.60, ph),
                     (0.43, 0.32, 0.22, 1.0), yaw=-crack)
    make_cyl("Basement_Door_Knob", (hx - math.sin(crack) * 0.80 - 0.04, hy - math.cos(crack) * 0.80, 1.00), 0.03, 0.05,
             (0.70, 0.58, 0.30, 1.0), axis='X', segments=8)
    # THE STAIR DOWN: a landing, nine steps falling east into the dark,
    # the well's walls and ceiling, a dark end wall where the light gives out
    well = (0.30, 0.27, 0.24, 1.0); tread = (0.36, 0.28, 0.20, 1.0)
    wx0, wy0, wy1 = ROOM_W/2.0 + 0.10, 1.12, 2.08
    make_box("Basement_Landing", (wx0 + 0.25, 1.6, -0.03), (0.50, wy1 - wy0, 0.06), tread)
    for i in range(9):
        z = -0.19 * (i + 1)
        make_box(f"Basement_Step_{i}", (wx0 + 0.50 + 0.25 * (i + 0.5), 1.6, z - 0.03), (0.25, wy1 - wy0, 0.06), tread)
        make_box(f"Basement_Riser_{i}", (wx0 + 0.50 + 0.25 * i + 0.005, 1.6, z + 0.095), (0.01, wy1 - wy0, 0.19), well)
    span = 0.50 + 0.25 * 9
    for nm, y in (("S", wy0 - 0.05), ("N", wy1 + 0.05)):
        make_box(f"Basement_Well_{nm}", (wx0 + span / 2.0, y, (CEIL - 1.9) / 2.0), (span, 0.10, CEIL + 1.9), well)
    make_box("Basement_Well_Ceiling", (wx0 + span / 2.0, 1.6, 2.15), (span, wy1 - wy0, 0.10), well)
    make_box("Basement_Well_End", (wx0 + span + 0.05, 1.6, (CEIL - 1.9) / 2.0), (0.10, wy1 - wy0 + 0.20, CEIL + 1.9), (0.06, 0.05, 0.05, 1.0))
    make_box("Basement_Well_Floor", (wx0 + span - 0.20, 1.6, -1.90), (0.50, wy1 - wy0, 0.06), (0.10, 0.09, 0.08, 1.0))
    # the bare bulb on its long cord near the well's foot, lit low — what
    # little light comes up the stairs past the cracked door (ch7: "His
    # eyes adjust to the kitchen light")
    bx_ = wx0 + span - 0.35
    make_cyl("Basement_Bulb_Cord", (bx_, 1.6, (2.10 + 0.36) / 2.0), 0.004, 2.10 - 0.36, (0.10, 0.10, 0.10, 1.0), segments=4)
    make_cyl("Basement_Bulb_Socket", (bx_, 1.6, 0.34), 0.02, 0.05, (0.20, 0.18, 0.16, 1.0), segments=8)
    make_cyl("Basement_Bulb", (bx_, 1.6, 0.28), 0.035, 0.08, (1.0, 0.90, 0.66, 1.0), segments=8)
    make_tube("Basement_Handrail", [(wx0 + 0.45, wy1 - 0.06, 0.88), (wx0 + span - 0.10, wy1 - 0.06, 0.88 - 1.71)], 0.02, wood)
    # (the stair up is the hall's now, draft 5 — three treads stood here
    # under the front window)
    # (the oven face is the kit range's own now, 2026-10-07)
    # Microwave, counter east end
    make_chamfer_box("Microwave", (0.15, Y_BACK-0.30, TOP_Z+0.15), (0.50, 0.38, 0.30), (0.30, 0.30, 0.32, 1.0))
    # ── THE POT ROAST · the chapter's hero object ──────────────
    # (2026-08-12, shot_marker_audit --props) [shot:insert pot_roast]
    # fires 3x in a MODEL CHAPTER — "Eileen has made a pot roast…
    # the pot roast Eileen has been making on Sunday nights since he
    # was three. She has not made it since April." It was never
    # modeled; the insert framed bare table.
    # It sits at the table's head, still in the enameled dutch oven
    # it was cooked in, lid off and leaning against its own base —
    # which is what "she made it tonight" looks like from the door.
    tx0, ty0 = 0.0, ROOM_D/2.0
    enamel = (0.62, 0.16, 0.14, 1.0)      # the old red enamel
    enamel_dk = (0.46, 0.11, 0.10, 1.0)
    cream = (0.90, 0.88, 0.82, 1.0)       # the chipped interior
    roast = (0.42, 0.24, 0.16, 1.0)
    gravy = (0.34, 0.20, 0.12, 1.0)
    carrot = (0.78, 0.42, 0.16, 1.0)
    tater = (0.80, 0.72, 0.52, 1.0)
    # Dutch oven: body, a proud rolled rim, two lug handles
    make_cyl("PotRoast_Pot", (tx0, ty0 + 0.22, 0.855),
             0.155, 0.19, enamel, segments=16)
    make_cyl("PotRoast_Pot_Rim", (tx0, ty0 + 0.22, 0.948),
             0.166, 0.022, enamel_dk, segments=16)
    make_cyl("PotRoast_Pot_Inner", (tx0, ty0 + 0.22, 0.944),
             0.140, 0.010, cream, segments=16)
    for sgn in (-1, 1):
        make_box("PotRoast_Lug_%d" % sgn,
                 (tx0 + sgn * 0.175, ty0 + 0.22, 0.930),
                 (0.055, 0.085, 0.030), enamel_dk)
    # The roast itself, proud of the rim, with vegetables around it
    make_blob("PotRoast_Meat", (tx0, ty0 + 0.22, 0.975), 0.105,
              roast, noise=0.16, seed=5, squash=0.62)
    make_cyl("PotRoast_Gravy", (tx0, ty0 + 0.22, 0.950),
             0.132, 0.012, gravy, segments=14)
    for vi, (vx, vy) in enumerate(((-0.085, 0.055), (0.080, 0.040),
                                   (-0.050, -0.075), (0.065, -0.065))):
        col = carrot if vi % 2 == 0 else tater
        make_blob("PotRoast_Veg_%d" % vi,
                  (tx0 + vx, ty0 + 0.22 + vy, 0.962), 0.036,
                  col, noise=0.20, seed=11 + vi, squash=0.80)
    # The lid, OFF — leaning against the pot, which is the detail
    # that says it was served just now.
    make_cyl("PotRoast_Lid", (tx0 + 0.245, ty0 + 0.30, 0.815),
             0.150, 0.030, enamel, segments=16)
    make_cyl("PotRoast_Lid_Knob", (tx0 + 0.245, ty0 + 0.30, 0.845),
             0.024, 0.030, enamel_dk, segments=8)
    # A trivet under the pot — nobody puts a hot dutch oven on oak
    make_box("PotRoast_Trivet", (tx0, ty0 + 0.22, 0.768),
             (0.36, 0.36, 0.016), (0.36, 0.28, 0.20, 1.0))

    # Four place settings — the head setting is the shot
    tx, ty = 0.0, ROOM_D/2.0
    for si, (dx, dy) in enumerate(((-0.45, 0.0), (0.0, -0.32), (0.0, 0.32), (0.45, 0.0))):
        make_cyl(f"Setting_{si}_Plate", (tx+dx, ty+dy, 0.77), 0.11, 0.012, (0.90, 0.88, 0.84, 1.0), segments=12)
        make_box(f"Setting_{si}_Fork", (tx+dx-0.15, ty+dy, 0.772), (0.02, 0.12, 0.008), (0.60, 0.62, 0.63, 1.0))
    # Coffee mugs by the pot: three poured, one never drunk
    for mi, (mx, my) in enumerate(((-2.98, Y_BACK-0.20), (-2.36, Y_BACK-0.45), (0.35, ty-0.05))):   # on the counter, which is on the wall now (2026-09-25)
        make_cyl(f"Mug_{mi}", (mx, my, TOP_Z+0.045 if mi < 2 else 0.79), 0.04, 0.09,
                 [(0.72, 0.30, 0.22, 1.0), (0.30, 0.40, 0.52, 1.0), (0.86, 0.82, 0.74, 1.0)][mi], segments=10)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Seven distinct cues; pot (the pot roast), coffee (the pots on
    the counter) and door (the basement door) already have
    geometry — markers only. Built, on a table that is already
    set for four:

    - THE CONTACT PRINTS ("a small set of black-and-white
      photographs — the contact prints from this week's
      photography class"): a strip of six frames at the
      north-west corner.
    - THE LYRIC SHEET ("Jim has, on the table in front of him, a
      sheet of paper. Jesse ... recognizes the sheet of paper."):
      at the north-east corner beside the pot-roast lid.
    - THE NOTEBOOK (the bridge lyrics, in Jesse's kid's-hand):
      the small spiral at the south-west corner.
    - THE GUITAR: the Telecaster on its stand by the stairs — he
      carries it down to the kitchen doorway in the bridge
      chapters.
    """
    T = 0.76
    # ── THE CONTACT PRINTS · table NW corner ──
    make_box("Contact_Prints_Sheet", (-0.42, 3.05, T + 0.001), (0.20, 0.13, 0.002),
             (0.90, 0.88, 0.84, 1.0))
    for fi2 in range(6):
        make_box(f"Contact_Print_{fi2}", (-0.49 + (fi2 % 3) * 0.062, 3.02 + (fi2 // 3) * 0.06, T + 0.0025),
                 (0.050, 0.045, 0.001), (0.22, 0.22, 0.24, 1.0))
    # ── THE LYRIC SHEET · table NE corner ──
    make_box("Lyric_Sheet", (0.47, 3.05, T + 0.001), (0.15, 0.20, 0.002),
             (0.94, 0.93, 0.88, 1.0))
    make_box("Lyric_Sheet_Lines", (0.47, 3.08, T + 0.0025), (0.10, 0.10, 0.001),
             (0.40, 0.40, 0.44, 1.0))
    # ── THE NOTEBOOK · table SW corner ──
    make_box("Bridge_Notebook", (-0.45, 2.45, T + 0.006), (0.110, 0.150, 0.012),
             (0.30, 0.44, 0.58, 1.0))
    make_box("Bridge_Notebook_Wire", (-0.511, 2.45, T + 0.007), (0.010, 0.150, 0.014),
             (0.55, 0.56, 0.58, 1.0))
    # ── THE GUITAR · Telecaster on its stand by the stairs ──
    # (draft 5: in the SW corner beside the kitchen doorway, its face to
    # the room — it stood by three stub treads with its face to the wall)
    gx, gy = -2.70, 0.42
    make_box("Guitar_Body", (gx, gy, 0.22), (0.32, 0.06, 0.40), (0.72, 0.60, 0.34, 1.0))   # body on the stand's cradle (2026-09-08)
    make_box("Guitar_Guard", (gx - 0.05, gy + 0.032, 0.20), (0.16, 0.004, 0.22), (0.12, 0.12, 0.12, 1.0))
    make_box("Guitar_Neck", (gx + 0.02, gy, 0.695), (0.05, 0.04, 0.55), (0.62, 0.50, 0.32, 1.0))
    make_box("Guitar_Head", (gx + 0.02, gy, 1.05), (0.07, 0.04, 0.16), (0.72, 0.60, 0.34, 1.0))
    for sgn in (-1, 1):
        make_box(f"Guitar_Stand_Leg_{'W' if sgn < 0 else 'E'}", (gx + sgn * 0.12, gy - 0.10, 0.15),
                 (0.03, 0.03, 0.30), (0.20, 0.20, 0.22, 1.0))
    make_box("Guitar_Stand_Foot", (gx, gy - 0.10, 0.015), (0.30, 0.06, 0.03), (0.20, 0.20, 0.22, 1.0))
    # the cradle the body sits in (2026-09-24: the body stood 2 cm up,
    # 4.5 cm in front of the stand, touching none of it)
    make_box("Guitar_Stand_Cradle", (gx, gy - 0.035, 0.035), (0.30, 0.07, 0.03), (0.20, 0.20, 0.22, 1.0))


def build_detail_2026_10():
    """DETAIL PASSES D2–D4 (pass 77, 2026-10-11 — lore/_SET_DETAIL_PLAYBOOK.md).
    D2: the traffic ribbon front door → table → sink, the stain at the sink's
    foot and the fridge's, the counter's kick scuff, the ceiling-shadow bands.
    D3: outlets over the counter (two), by the fridge and on the west wall,
    the switch by the front door, the thermostat, the fridge's cord. D4: the
    dish towel over the oven handle, a coffee ring on the table, the mail
    stacked off-square on the counter's end, a chair pushed back. The views
    past both windows were D5 already (make_view S/N). Draft N+1: the
    coffee maker's cord (the kit's anchor is a function local); a cabinet
    door ajar once the kitchen kit names its doors; the phone on the wall
    the Hendersons must have."""
    W = ROOM_W / 2.0
    # ── D2 ──
    make_traffic_wear("Wear_Door_Table", [(W_X + 0.25, DOOR_Y), (-1.7, 1.75), (-0.95, 2.35)], width=0.7)
    make_traffic_wear("Wear_Table_Sink", [(-0.5, 3.1), (-1.6, 4.6)], width=0.6)
    make_floor_stain("Stain_Sink", (SINK_X, 4.45), radius=0.17)
    make_floor_stain("Stain_Fridge", (W - 0.95, 3.0), radius=0.14)
    make_scuff_band("Scuff_Counter", (0.0, Y_BACK - 0.60 - 0.005), 5.4, axis='X', height=0.12, band_z=0.07)
    make_wall_tint_band("Tint_N_Top", (0.0, ROOM_D - 0.10), ROOM_W - 0.2, axis='X', height=0.28, band_z=CEIL - 0.16)
    make_wall_tint_band("Tint_W_Top", (-W + 0.10, ROOM_D / 2.0), ROOM_D - 0.2, axis='Y', height=0.28, band_z=CEIL - 0.16)
    # ── D3 ──
    make_wall_outlet("Outlet_Counter_W", (-0.60, ROOM_D), axis='X', face_sign=-1, z=1.10)
    make_wall_outlet("Outlet_Counter_E", (2.40, ROOM_D), axis='X', face_sign=-1, z=1.10)
    make_wall_outlet("Outlet_Fridge", (W, 3.60), axis='Y', face_sign=-1, z=0.30)
    make_wall_outlet("Outlet_W", (-W, 0.45), axis='Y', face_sign=1, z=0.30)
    make_light_switch("Switch_Door", (-W, DOOR_Y + DOOR_W / 2.0 + 0.22), axis='Y', face_sign=1, z=1.20)   # by the kitchen doorway
    make_thermostat("Thermostat", (-W, 2.75), axis='Y', face_sign=1, z=1.45)
    make_cord_run("Cord_Fridge", (W - 0.50 + 0.34, 3.32, 0.22), (W - 0.10, 3.60, 0.30), sag=0.04)
    # ── D4 ──
    make_box("Oven_Towel", (RANGE_X, Y_BACK - 0.60 - 0.012, 0.76), (0.30, 0.02, 0.30), (0.56, 0.62, 0.70, 1.0))
    make_cyl("Table_Coffee_Ring", (0.42, 2.55, 0.761), 0.045, 0.002, (0.48, 0.36, 0.22, 1.0), segments=12)
    for mi, (dx, dy, dz) in enumerate(((0.0, 0.0, 0.0), (0.03, -0.02, 0.004), (-0.02, 0.03, 0.008))):
        make_box(f"Mail_{mi}", (2.55 + dx, Y_BACK - 0.40 + dy, TOP_Z + 0.003 + dz), (0.24, 0.11, 0.004), ((0.92, 0.92, 0.88, 1.0), (0.86, 0.84, 0.78, 1.0), (0.94, 0.90, 0.80, 1.0))[mi])
    make_chair("Chair_Pushed", 1.35, 1.55, yaw=2.35, wood=COL_WOOD)


def _base(name, axis, line, a0, a1, sign, col):
    """A baseboard on a wall face the wall helper did not give one (the
    far side of a shared wall): 1.2 cm proud, like make_wall's."""
    off = sign * (0.10 + 0.006)
    if axis == 'Y':
        make_box(name, (line + off, (a0 + a1) / 2.0, 0.06), (0.012, a1 - a0, 0.12), col)
    else:
        make_box(name, ((a0 + a1) / 2.0, line + off, 0.06), (a1 - a0, 0.012, 0.12), col)


def _cased(prefix, axis, line, centre, width, height, col, depth=0.24, bar=CASE):
    """A cased opening. `width` x `height` is the CLEAR opening; the wall
    is cut `bar` bigger a side and the jambs and head line the cut, 2 cm
    proud of both faces."""
    for nm, c in (("A", centre - width / 2.0 - bar / 2.0), ("B", centre + width / 2.0 + bar / 2.0)):
        if axis == 'Y':
            make_box(f"{prefix}_Jamb_{nm}", (line, c, height / 2.0), (depth, bar, height), col)
        else:
            make_box(f"{prefix}_Jamb_{nm}", (c, line, height / 2.0), (bar, depth, height), col)
    if axis == 'Y':
        make_box(f"{prefix}_Head", (line, centre, height + bar / 2.0), (depth, width + 2 * bar, bar), col)
    else:
        make_box(f"{prefix}_Head", (centre, line, height + bar / 2.0), (width + 2 * bar, depth, bar), col)


def build_hall_2026_11():
    """THE FRONT HALL (draft 5). West of the kitchen, 2.2 m clear, the
    house's depth: the front door in the S wall, the kitchen doorway in
    its E wall, the dining room's opening across from it, the stair up
    along the shared wall ("He goes upstairs to shower. He comes down at
    six-twenty", ch7; "Eileen and Jim climb the stairs together", ch23),
    a back door at its N end."""
    hw = W_X - HALL_X0
    make_floor("Hall_Floor", (HALL_CX - 0.15, ROOM_D / 2.0, 0.0), size_x=hw - 0.10, size_y=ROOM_D + 0.4,
               palette={"vinyl": HALL_OAK, "seam": HALL_SEAM}, style="plank", plank_axis='Y')
    make_wall_with_openings("Hall_Wall_W", (HALL_X0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
              palette=PAL_HALL, baseboard_face_sign=+1, openings=[(DIN_DOOR_Y, (DOOR_H + CASE) / 2.0, DIN_DOOR_W + 2 * CASE, DOOR_H + CASE)])
    fdx = HALL_CX
    make_wall_with_openings("Hall_Wall_S", (HALL_CX, 0.0, 0), length=hw - 0.20, height=CEIL, axis='X',
              palette=PAL_HALL, baseboard_face_sign=+1, openings=[(fdx, (2.08 + 0.06) / 2.0, 0.95 + 0.12, 2.08 + 0.06)])
    bdx = (HALL_X0 + 0.10 + ST_X0) / 2.0
    make_wall_with_openings("Hall_Wall_N", (HALL_CX, ROOM_D, 0), length=hw - 0.20, height=CEIL, axis='X',
              palette=PAL_HALL, baseboard_face_sign=-1, openings=[(bdx, (2.04 + 0.06) / 2.0, 0.80 + 0.12, 2.04 + 0.06)])
    # the hall side of the shared wall, south of the doorway
    _base("Hall_Base_E", 'Y', W_X, 0.10, DOOR_Y - DOOR_W / 2.0 - CASE, -1, PAL_HALL["baseboard"])
    # ceiling, with the stair's well left open
    well_y0 = ST_Y0 + 2 * ST_RUN
    make_ceiling("Hall_Ceil_S", (HALL_CX, (well_y0 - 0.2) / 2.0, CEIL), size_x=hw - 0.20, size_y=well_y0 + 0.2, with_grid=False, with_stains=False)
    make_ceiling("Hall_Ceil_N", ((HALL_X0 + ST_X0 - 0.10) / 2.0, (well_y0 + ROOM_D + 0.2) / 2.0, CEIL),
                 size_x=ST_X0 - 0.10 - HALL_X0, size_y=ROOM_D + 0.2 - well_y0, with_grid=False, with_stains=False)
    # the well above: the upstairs dark at the top of the flight
    dark = (0.34, 0.31, 0.27, 1.0)
    wz = CEIL + 0.10 + 1.30
    make_box("Hall_Well_S", ((ST_X0 - 0.10 + W_X) / 2.0, well_y0 - 0.05, wz), (W_X - ST_X0 + 0.10, 0.10, 2.60), dark)
    make_box("Hall_Well_W", (ST_X0 - 0.15, (well_y0 + ROOM_D) / 2.0, wz), (0.10, ROOM_D - well_y0, 2.60), dark)
    make_box("Hall_Well_E", (W_X, (well_y0 + ROOM_D) / 2.0, wz), (0.20, ROOM_D - well_y0 + 0.2, 2.60), dark)
    make_box("Hall_Well_N", ((ST_X0 - 0.10 + W_X) / 2.0, ROOM_D, wz), (W_X - ST_X0 + 0.30, 0.20, 2.60), dark)
    make_box("Hall_Well_Cap", ((ST_X0 - 0.10 + W_X) / 2.0, (well_y0 + ROOM_D) / 2.0, CEIL + 2.75), (W_X - ST_X0 + 0.30, ROOM_D - well_y0 + 0.3, 0.10), (0.20, 0.18, 0.16, 1.0))
    # THE STAIR UP: thirteen risers, oak treads on painted risers, solid
    # under (the closet's wall), a newel, a rail and a baluster a tread
    sx = (ST_X0 + ST_X1) / 2.0; sw = ST_X1 - ST_X0
    riser = (0.90, 0.87, 0.80, 1.0)
    for i in range(ST_N - 1):
        h = (i + 1) * ST_RISE
        y = ST_Y0 + (i + 0.5) * ST_RUN
        make_box(f"Hall_Stair_Step_{i}", (sx, y, (h - 0.03) / 2.0), (sw, ST_RUN, h - 0.03), riser)
        make_box(f"Hall_Stair_Tread_{i}", (sx, y - 0.012, h - 0.015), (sw, ST_RUN + 0.024, 0.03), HALL_OAK)
        make_box(f"Hall_Stair_Baluster_{i}", (ST_X0 + 0.03, y, h + 0.483), (0.03, 0.03, 0.966), riser)
    top_y = ST_Y0 + (ST_N - 1) * ST_RUN
    make_box("Hall_Stair_Landing", (sx, (top_y + ROOM_D - 0.10) / 2.0, 2.70 / 2.0), (sw, ROOM_D - 0.10 - top_y, 2.70), riser)
    make_box("Hall_Stair_Landing_Top", (sx, (top_y + ROOM_D - 0.10) / 2.0 - 0.012, 2.70 - 0.015), (sw, ROOM_D - 0.10 - top_y + 0.024, 0.03), HALL_OAK)
    make_box("Hall_Stair_Newel", (ST_X0 + 0.03, ST_Y0 - 0.06, 0.58), (0.10, 0.10, 1.16), TRIM)
    make_box("Hall_Stair_Newel_Cap", (ST_X0 + 0.03, ST_Y0 - 0.06, 1.18), (0.13, 0.13, 0.04), TRIM)
    slope = ST_RISE / ST_RUN
    make_tube("Hall_Stair_Rail", [(ST_X0 + 0.03, ST_Y0 - 0.06, 1.02), (ST_X0 + 0.03, top_y, 1.02 + (top_y - ST_Y0 + 0.06) * slope)], 0.025, TRIM)
    # the kitchen doorway's casing and its threshold, vinyl to oak
    _cased("Kitchen_Doorway", 'Y', W_X, DOOR_Y, DOOR_W, DOOR_H, TRIM)
    make_threshold("Kitchen_Doorway_Threshold", (W_X - 0.20, DOOR_Y, 0.0), width=DOOR_W, axis='Y')
    _cased("Dining_Opening", 'Y', HALL_X0, DIN_DOOR_Y, DIN_DOOR_W, DOOR_H, TRIM)
    make_threshold("Dining_Opening_Threshold", (HALL_X0 - 0.10, DIN_DOOR_Y, 0.0), width=DIN_DOOR_W, axis='Y')
    # THE FRONT DOOR ("He opens the front door quietly", ch22): six panels,
    # shut, its knob and deadbolt on the stair side
    door = (0.36, 0.22, 0.16, 1.0); door_dk = (0.28, 0.17, 0.12, 1.0)
    _cased("Front_Entry", 'X', 0.0, fdx, 0.95, 2.08, TRIM, bar=0.06)
    make_box("Front_Door", (fdx, 0.02, 1.04), (0.94, 0.05, 2.07), door)
    for pi, (px, pz, pw, ph) in enumerate(((-0.22, 1.62, 0.30, 0.56), (0.22, 1.62, 0.30, 0.56), (-0.22, 0.98, 0.30, 0.50),
                                           (0.22, 0.98, 0.30, 0.50), (-0.22, 0.38, 0.30, 0.46), (0.22, 0.38, 0.30, 0.46))):
        make_box(f"Front_Door_Panel_{pi}", (fdx + px, 0.048, pz), (pw, 0.008, ph), door_dk)
    make_cyl("Front_Door_Knob", (fdx + 0.38, 0.085, 1.00), 0.032, 0.07, BRASS, axis='Y', segments=10)
    make_cyl("Front_Door_Deadbolt", (fdx + 0.38, 0.060, 1.16), 0.026, 0.03, BRASS, axis='Y', segments=10)
    make_box("Hall_Mat", (fdx, 0.62, 0.006), (0.86, 0.56, 0.012), (0.30, 0.26, 0.22, 1.0))
    # the back door at the hall's N end, shut
    make_box("Hall_Back_Door", (bdx, ROOM_D - 0.02, 1.02), (0.79, 0.05, 2.03), (0.90, 0.87, 0.80, 1.0))
    _cased("Hall_Back_Entry", 'X', ROOM_D, bdx, 0.80, 2.04, TRIM, bar=0.06)
    make_cyl("Hall_Back_Door_Knob", (bdx - 0.30, ROOM_D - 0.08, 1.00), 0.03, 0.06, BRASS, axis='Y', segments=10)
    # hooks by the door: what a family hangs up coming in
    hy = 0.50
    make_box("Hall_Hook_Rail", (HALL_X0 + 0.115, hy, 1.62), (0.03, 0.70, 0.09), TRIM)
    for hi in range(4):
        make_cyl(f"Hall_Hook_{hi}", (HALL_X0 + 0.15, hy - 0.27 + hi * 0.18, 1.60), 0.012, 0.06, BRASS, axis='X', segments=6)
    make_chamfer_box("Hall_Coat_0", (HALL_X0 + 0.20, hy - 0.09, 1.22), (0.12, 0.30, 0.74), (0.26, 0.32, 0.40, 1.0))
    make_chamfer_box("Hall_Coat_1", (HALL_X0 + 0.19, hy + 0.27, 1.28), (0.10, 0.26, 0.62), (0.52, 0.44, 0.30, 1.0))
    make_cyl("Hall_Ceiling_Dome", (HALL_CX, 1.40, CEIL - 0.06), 0.15, 0.12, (0.96, 0.90, 0.72, 1.0), segments=12)
    make_light_switch("Hall_Switch", (fdx + 0.80, 0.0), axis='X', face_sign=1, z=1.20)
    make_traffic_wear("Hall_Wear", [(fdx, 0.5), (HALL_CX, 1.5), (W_X - 0.3, DOOR_Y)], width=0.6, tint=(0.52, 0.38, 0.23, 1.0))


def build_dining_2026_11():
    """THE DINING ROOM (draft 5): "We don't dine in the dining room. We
    dine here. The dining room has been, for fourteen years, the room
    where the small table that holds the lamp lives" (ch23). Carpet, a
    chandelier hung where a table would stand and nothing under it, the
    front window, and the small table with the lamp against the far
    wall — on the line of sight from the kitchen, through the doorway
    and across the hall. (The piano comes later than any scene here.)"""
    cx = (DIN_X0 + HALL_X0) / 2.0; w = HALL_X0 - DIN_X0
    make_box("Dining_Floor_Slab", (cx - 0.05, DIN_Y1 / 2.0, -0.05), (w - 0.10, DIN_Y1 + 0.4, 0.10), CARPET)
    make_wall("Dining_Wall_W", (DIN_X0, DIN_Y1 / 2.0, 0), length=DIN_Y1 + 0.4, height=CEIL, axis='Y', palette=PAL_DIN, baseboard_face_sign=+1)
    make_wall("Dining_Wall_N", (cx, DIN_Y1, 0), length=w - 0.20, height=CEIL, axis='X', palette=PAL_DIN, baseboard_face_sign=-1)
    dwx = cx - 0.10
    make_wall_with_openings("Dining_Wall_S", (cx, 0.0, 0), length=w - 0.20, height=CEIL, axis='X', palette=PAL_DIN, baseboard_face_sign=+1,
                            openings=[(dwx, 1.45, 1.80, 1.30)])
    # the dining room's face of the hall wall: its paint and its baseboard
    for nm, a0, a1 in (("S", 0.10, DIN_DOOR_Y - DIN_DOOR_W / 2.0 - CASE), ("N", DIN_DOOR_Y + DIN_DOOR_W / 2.0 + CASE, DIN_Y1 - 0.10)):
        make_box(f"Dining_Wall_E_Face_{nm}", (HALL_X0 - 0.104, (a0 + a1) / 2.0, CEIL / 2.0), (0.008, a1 - a0, CEIL), PAL_DIN["wall"])
        _base(f"Dining_Base_E_{nm}", 'Y', HALL_X0 - 0.008, a0, a1, -1, PAL_DIN["baseboard"])
    make_box("Dining_Wall_E_Face_Head", (HALL_X0 - 0.104, DIN_DOOR_Y, (DOOR_H + CASE + CEIL) / 2.0), (0.008, DIN_DOOR_W + 2 * CASE, CEIL - DOOR_H - CASE), PAL_DIN["wall"])
    make_ceiling("Dining_Ceil", (cx, DIN_Y1 / 2.0, CEIL), size_x=w + 0.2, size_y=DIN_Y1 + 0.4, with_grid=False, with_stains=False)
    make_window("Dining_Window", (dwx, 0.10, 1.45), width=1.80, height=1.30, room_dir=+1, see_through=True)
    make_curtains("Dining_Curtains", (dwx, 0.10, 1.45), width=1.80, height=1.30, room_dir=+1, color=(0.78, 0.72, 0.60, 1.0))
    for nm, ax, length, wx, wy in (("Dining_Crown_W", 'Y', DIN_Y1 - 0.2, DIN_X0 + 0.10, DIN_Y1 / 2.0),
                                   ("Dining_Crown_N", 'X', w - 0.2, cx, DIN_Y1 - 0.10),
                                   ("Dining_Crown_S", 'X', w - 0.2, cx, 0.10)):
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": (0.90, 0.88, 0.82, 1.0)})
    # THE SMALL TABLE THAT HOLDS THE LAMP
    lx, ly = DIN_X0 + 0.46, 2.35
    make_table("Lamp_Table", lx, ly, w=0.50, d=0.62, h=0.68, wood=(0.38, 0.26, 0.18, 1.0))
    from _props.furniture import make_lamp
    make_lamp("Dining_Lamp", lx, ly, base_z=0.68, h=0.58)
    make_box("Lamp_Table_Doily", (lx, ly, 0.681), (0.30, 0.30, 0.002), (0.92, 0.90, 0.84, 1.0))
    make_cord_run("Dining_Lamp_Cord", (lx - 0.10, ly + 0.10, 0.70), (DIN_X0 + 0.11, ly + 0.55, 0.30), sag=0.20)
    make_wall_outlet("Dining_Outlet_W", (DIN_X0, ly + 0.55), axis='Y', face_sign=1, z=0.30)
    # the chandelier over where a table would stand, and nothing under it
    hx, hy = cx, DIN_Y1 / 2.0
    make_cyl("Dining_Chandelier_Canopy", (hx, hy, CEIL - 0.02), 0.07, 0.04, BRASS, segments=10)
    make_cyl("Dining_Chandelier_Stem", (hx, hy, CEIL - 0.34), 0.012, 0.60, BRASS, segments=6)
    make_lathe("Dining_Chandelier_Body", (hx, hy, CEIL - 0.80), [(0.0, 0.0), (0.05, 0.02), (0.07, 0.08), (0.03, 0.14), (0.02, 0.18), (0.0, 0.18)], BRASS, segments=10)
    for ai in range(5):
        a = ai * 2.0 * math.pi / 5.0
        ex, ey = hx + math.cos(a) * 0.26, hy + math.sin(a) * 0.26
        make_tube(f"Dining_Chandelier_Arm_{ai}", [(hx + math.cos(a) * 0.05, hy + math.sin(a) * 0.05, CEIL - 0.74), (hx + math.cos(a) * 0.17, hy + math.sin(a) * 0.17, CEIL - 0.80), (ex, ey, CEIL - 0.74)], 0.008, BRASS)
        make_cyl(f"Dining_Chandelier_Cup_{ai}", (ex, ey, CEIL - 0.73), 0.022, 0.02, BRASS, segments=8)
        make_cyl(f"Dining_Chandelier_Candle_{ai}", (ex, ey, CEIL - 0.68), 0.010, 0.08, (0.90, 0.88, 0.80, 1.0), segments=6)
    # fourteen years of nobody: the carpet's vacuum lanes, the dents of
    # nothing. One air return low on the N wall.
    for vi in range(5):
        make_box(f"Dining_Carpet_Lane_{vi}", (DIN_X0 + 0.9 + vi * 0.72, DIN_Y1 / 2.0 + 0.2, 0.0006), (0.34, DIN_Y1 - 1.3, 0.0012), (0.69, 0.63, 0.53, 1.0))
    make_box("Dining_Return_Grille", (cx + 1.0, DIN_Y1 - 0.108, 0.28), (0.60, 0.012, 0.30), (0.86, 0.84, 0.78, 1.0))
    for gi in range(6):
        make_box(f"Dining_Return_Slat_{gi}", (cx + 1.0, DIN_Y1 - 0.116, 0.17 + gi * 0.045), (0.54, 0.006, 0.012), (0.66, 0.64, 0.60, 1.0))


def build_front_wall_2026_11():
    """What stands on the kitchen's closed front wall (draft 5): the
    oak sideboard a kitchen this size keeps under its long wall, a fruit
    bowl, the cookbooks — between the doorway corner and the window."""
    sx, sy = -1.15, 0.10 + 0.24
    make_chamfer_box("Sideboard_Body", (sx, sy, 0.47), (1.50, 0.46, 0.78), OAK)
    make_chamfer_box("Sideboard_Top", (sx, sy + 0.01, 0.875), (1.56, 0.50, 0.03), OAK_DK)
    for li, (lx_, ly_) in enumerate(((-0.70, -0.18), (0.70, -0.18), (-0.70, 0.18), (0.70, 0.18))):
        make_box(f"Sideboard_Foot_{li}", (sx + lx_, sy + ly_, 0.04), (0.05, 0.05, 0.08), OAK_DK)
    for di in range(3):
        dx = sx - 0.49 + di * 0.49
        make_box(f"Sideboard_Front_{di}", (dx, sy + 0.234, 0.45), (0.45, 0.008, 0.62), OAK_DK)
        make_cyl(f"Sideboard_Pull_{di}", (dx + (0.17 if di == 0 else -0.17), sy + 0.25, 0.60), 0.012, 0.025, BRASS, axis='Y', segments=6)
    make_lathe("Fruit_Bowl", (sx - 0.35, sy, 0.89), [(0.0, 0.0), (0.07, 0.0), (0.13, 0.05), (0.15, 0.08), (0.13, 0.08), (0.0, 0.066)], (0.86, 0.84, 0.78, 1.0), segments=14)
    for fi, (fx, fy, col) in enumerate(((-0.04, 0.02, (0.80, 0.22, 0.16, 1.0)), (0.05, -0.02, (0.86, 0.66, 0.20, 1.0)), (0.0, 0.06, (0.52, 0.62, 0.24, 1.0)))):
        make_blob(f"Fruit_{fi}", (sx - 0.35 + fx, sy + fy, 0.955), 0.042, col, noise=0.08, seed=30 + fi)
    for bi, (bw, col) in enumerate(((0.035, (0.62, 0.24, 0.20, 1.0)), (0.05, (0.88, 0.84, 0.72, 1.0)), (0.03, (0.26, 0.36, 0.44, 1.0)), (0.045, (0.70, 0.56, 0.30, 1.0)))):
        make_box(f"Cookbook_{bi}", (sx + 0.28 + sum((0.035, 0.05, 0.03, 0.045)[:bi]) + bw / 2.0, sy - 0.04, 0.89 + 0.12), (bw, 0.19, 0.24), col)
    make_box("Cookbook_End", (sx + 0.265, sy - 0.04, 0.89 + 0.075), (0.02, 0.14, 0.15), (0.30, 0.26, 0.22, 1.0))
    make_wall_outlet("Outlet_S", (0.55, 0.0), axis='X', face_sign=1, z=0.30)


def main():
    clear_scene()
    build_shell()
    build_hall_2026_11()
    build_dining_2026_11()
    build_front_wall_2026_11()
    build_counter()
    build_table()
    build_dressing()
    build_detail_2026_10()
    build_hero_props()
    build_clock()
    build_fridge()
    build_ceiling_infra()
    build_hero_props_2026_09()
    # what is outside the window (2026-10-07, _props/views.py)
    make_view("View_S", "S", 0.0, -2.5, kind="front", ground_z=0.0, span=40.0, seed=2)
    # the ground past the far lawns (draft 5): between the houses across the
    # street a low ray met nothing — the wide from the fridge corner opened
    # 8 % void through the front window on a 21:9 screen
    make_box("View_S_Ground_Beyond", (-2.5, -46.0, -0.04), (90.0, 40.4, 0.05), (0.34, 0.42, 0.24, 1.0))   # Magnolia: the front yard, the street, the houses across
    make_view("View_N", "N", ROOM_D, SINK_X, kind="back", ground_z=0.0, seed=13)   # past the sink: the back yard, the shed, the cicadas
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/henderson_kitchen.glb"))
    print(f"\n[build_henderson_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
