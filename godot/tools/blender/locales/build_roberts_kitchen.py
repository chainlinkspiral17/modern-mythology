"""VOL 5 · Roberts Kitchen — the Lovers chapter / cameos.

PLACEMENT SCRIPT (uses _props/* library).

Canon: the Roberts house kitchen in Texas. Mackenzie's domestic
sphere, where the Anya tape lands on the Roberts' CRT (Elicia at
the Roberts cameo), where the Polaroid arrives (John at the
Roberts), and where Frasier sets the mailbox post (Frasier at
the Roberts).

Footprint:
  Interior X ∈ [-4, +4], Y ∈ [0, +6], ceiling Z=2.60
  Front door south centre
  Counter island in centre, Y=3, with stools
  Sink + stove on north wall (Y=+6)
  Pantry + fridge on east wall (X=+4)
  Window to back yard, east wall — limestone fenced

Run:
    blender --background --python build_roberts_kitchen.py

Output:
    godot/assets/3d/locales/roberts_kitchen.glb
"""
import os, sys
_BLENDER_TOOLS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BLENDER_TOOLS not in sys.path:
    sys.path.insert(0, _BLENDER_TOOLS)

from _props.furniture import make_table, make_chair, make_bench, make_lamp, make_pendant
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, make_chamfer_box, make_dome, make_taper_cyl, make_lathe
from _props.structure import (
    make_floor, make_wall, make_wall_with_openings, make_ceiling, make_window,
    make_crown_molding, make_door_hinges,
)
from _props.store_fixtures import make_counter, make_counter_bullnose
from _props.food_service import make_coffee_pots, make_sugar_creamer_caddy
from _props.decor import (
    make_wall_clock, make_calendar, make_floor_plant, make_faded_poster,
)
from _props.safety import (
    make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture,
    make_ceiling_speaker,
)
from _props.detail import (make_wall_outlet, make_wall_tint_band,
                           make_floor_stain, make_traffic_wear, make_backyard_view,
                           make_threshold, make_light_switch)
from _props.vehicles import make_car
from _props.objects import make_mug, make_bottle, make_jar, make_plate, make_bowl
from _props.cleaning import make_trash_can


# Roberts house palette — warm domestic Texas: cream walls,
# wood-stain trim, brown linoleum, sage curtains.
PAL_DOMESTIC_COUNTER = {
    "formica": (0.78, 0.66, 0.42, 1.0),   # warm laminate
    "top":     (0.42, 0.32, 0.22, 1.0),   # wood-grain top
    "kick":    (0.42, 0.30, 0.18, 1.0),
}
PAL_DOMESTIC_WALL = {
    "wall":      (0.92, 0.86, 0.74, 1.0),
    "baseboard": (0.46, 0.34, 0.22, 1.0),
}
COL_WOOD_TRIM      = (0.46, 0.34, 0.22, 1.0)
COL_LINOLEUM       = (0.74, 0.62, 0.46, 1.0)
COL_LINOLEUM_SEAM  = (0.46, 0.38, 0.28, 1.0)
COL_APPLIANCE      = (0.86, 0.86, 0.82, 1.0)
COL_TILE_BLUE      = (0.48, 0.62, 0.70, 1.0)
COL_CURTAIN_SAGE   = (0.62, 0.72, 0.56, 1.0)
COL_TV_CASE        = (0.32, 0.28, 0.24, 1.0)
COL_TV_SCREEN      = (0.06, 0.10, 0.14, 1.0)

ROOM_W = 8.0
ROOM_D = 6.0
CEIL_Z = 2.60


from _props.structure import make_frame_ring   # (2026-10-07: the frame boards → rings)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_LINOLEUM, "seam": COL_LINOLEUM_SEAM})
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=+1)
    # (2026-10-03: every wall with a window is CUT round it — they were solid
    # behind their panes, so the yard, the street and the porch were never
    # seen through them)
    make_wall_with_openings("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=-1,
              openings=[(3.5, 1.55, 1.80, 1.20)])
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0),
              length=ROOM_W + 0.4, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=-1,
              openings=[(-2.0, 1.98, 1.30, 0.84)])
    make_wall_with_openings("Wall_S_W", (-2.55, 0.0, 0),   # to the header's edge (2026-09-22: 40 cm short)
              length=2.90, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=+1,
              openings=[(-2.8, 1.58, 1.40, 1.00)])
    make_wall_with_openings("Wall_S_E", (+2.55, 0.0, 0),
              length=2.90, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=+1,
              openings=[(2.0, 1.40, 1.40, 1.20)])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (2.20, 0.20, 0.60), PAL_DOMESTIC_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL_Z),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, with_grid=False)
    for nm, ax, length in [
            ("Crown_W", 'Y', ROOM_D),
            ("Crown_E", 'Y', ROOM_D),
            ("Crown_N", 'X', ROOM_W),
            ("Crown_S", 'X', ROOM_W)]:
        if nm == "Crown_W":
            wx, wy = -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0
        elif nm == "Crown_E":
            wx, wy = +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0
        elif nm == "Crown_N":
            wx, wy = 0.0, ROOM_D - 0.10
        else:
            wx, wy = 0.0, +0.10
        make_crown_molding(nm, wall_x=wx, wall_y=wy,
                           length=length, axis=ax, ceil_z=CEIL_Z,
                           palette={"wood": COL_WOOD_TRIM})
    # Front window — east of door
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_SE", (+2.00, 0.10, 1.40),
                width=1.40, height=1.20, room_dir=+1)
    # Back-yard window (east wall, faces sage curtains)
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    make_frame_ring("Window_E_Frame", (ROOM_W / 2.0 - 0.12, 3.5, 1.55),
             (0.04, 1.80, 1.20), P.METAL_STEEL)
    make_box("Window_E_Glass", (ROOM_W / 2.0 - 0.1425, 3.5, 1.55),
             (0.005, 1.70, 1.10), P.GLASS)
    make_box("Window_E_Curtain", (ROOM_W / 2.0 - 0.16, 3.5, 1.55),
             (0.01, 1.80, 1.20), COL_CURTAIN_SAGE)


def build_kitchen_island():
    top_z = make_counter("Island", (0.0, 3.0, 0.0),
                         length=2.80, depth=1.20, height=0.92,
                         palette=PAL_DOMESTIC_COUNTER)
    make_counter_bullnose("Island", (-0.60, 3.0, top_z),
                          length=2.80, palette=PAL_DOMESTIC_COUNTER)
    # Two stools on south side of island
    for si, sx in enumerate([-0.80, +0.80]):
        make_cyl(f"Stool_{si}_Seat", (sx, 1.80, 0.74),
                 0.18, 0.04, COL_WOOD_TRIM)
        make_cyl(f"Stool_{si}_Post", (sx, 1.80, 0.355),   # floor to seat (2026-09-22: 2 cm up)
                 0.025, 0.71, P.METAL_BLACK)
    # Coffee pots on the island
    make_coffee_pots("Coffee", (0.20, 3.10, top_z), pots=2)
    # Sugar caddy
    make_sugar_creamer_caddy("Caddy", (-0.40, 3.10, top_z))


def build_north_appliances():
    # Sink + stove + fridge along north wall (Y=+6)
    # Sink
    # (2026-10-03: the bowl was a white BLOCK standing on the counter; a
    # sink is a basin cut INTO it — the top is four strips round a hole,
    # the basin a steel floor and four walls 18 cm down, the base
    # cabinet stops under the basin's floor)
    fm = PAL_DOMESTIC_COUNTER["formica"]
    for nm, cx, cy, w, d in (("Sink_Counter_W", -2.65, 5.60, 0.50, 0.70), ("Sink_Counter_E", -1.35, 5.60, 0.50, 0.70),
                             ("Sink_Counter_S", -2.0, 5.275, 0.80, 0.05), ("Sink_Counter_N", -2.0, 5.875, 0.80, 0.15)):
        make_box(nm, (cx, cy, 0.90), (w, d, 0.04), fm)
    make_box("Sink_Base", (-2.0, 5.60, 0.35),
             (1.80, 0.70, 0.70), PAL_DOMESTIC_COUNTER["kick"])
    for nm, cx, cy, w, d in (("Sink_Base_Band_W", -2.65, 5.60, 0.50, 0.70), ("Sink_Base_Band_E", -1.35, 5.60, 0.50, 0.70),
                             ("Sink_Base_Band_S", -2.0, 5.275, 0.80, 0.05), ("Sink_Base_Band_N", -2.0, 5.875, 0.80, 0.15)):
        make_box(nm, (cx, cy, 0.79), (w, d, 0.18), PAL_DOMESTIC_COUNTER["kick"])
    steel_sink = (0.78, 0.80, 0.80, 1.0)
    make_box("Sink_Basin_Floor", (-2.0, 5.55, 0.715), (0.80, 0.50, 0.03), steel_sink)
    make_box("Sink_Basin_Wall_W", (-2.39, 5.55, 0.815), (0.02, 0.50, 0.17), steel_sink)
    make_box("Sink_Basin_Wall_E", (-1.61, 5.55, 0.815), (0.02, 0.50, 0.17), steel_sink)
    make_box("Sink_Basin_Wall_S", (-2.0, 5.31, 0.815), (0.80, 0.02, 0.17), steel_sink)
    make_box("Sink_Basin_Wall_N", (-2.0, 5.79, 0.815), (0.80, 0.02, 0.17), steel_sink)
    for nm, cx, cy, w, d in (("Sink_Rim_W", -2.41, 5.55, 0.04, 0.54), ("Sink_Rim_E", -1.59, 5.55, 0.04, 0.54),
                             ("Sink_Rim_S", -2.0, 5.29, 0.84, 0.04), ("Sink_Rim_N", -2.0, 5.81, 0.84, 0.04)):
        make_box(nm, (cx, cy, 0.925), (w, d, 0.01), steel_sink)
    make_cyl("Sink_Drain", (-2.0, 5.55, 0.733), 0.03, 0.006, (0.40, 0.42, 0.44, 1.0), segments=10)
    # (2026-10-03: the faucet stood on the bowl's ROOM side and the spout
    # pointed at the wall — "sink on backwards"; it rises behind the
    # bowl, at the backsplash, and reaches over it)
    make_cyl("Sink_Faucet", (-2.0, 5.82, 1.06),
             0.015, 0.28, P.METAL_STEEL)      # rises from the counter top (0.92)
    make_box("Sink_Faucet_Spout", (-2.0, 5.70, 1.18),
             (0.04, 0.24, 0.04), P.METAL_STEEL)
    make_cyl("Sink_Faucet_Handle", (-2.065, 5.82, 1.00), 0.012, 0.12, P.METAL_STEEL, segments=6, axis='X')   # into the pipe
    # Stove
    make_box("Stove_Body", (0.0, 5.60, 0.45),
             (0.80, 0.70, 0.90), COL_APPLIANCE)
    make_box("Stove_Top", (0.0, 5.60, 0.92),
             (0.80, 0.70, 0.04), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([
            (-0.20, 5.50), (+0.20, 5.50),
            (-0.20, 5.70), (+0.20, 5.70)]):
        make_cyl(f"Stove_Burner_{bi}", (bx, by, 0.94),
                 0.10, 0.02, P.METAL_STEEL)
    make_box("Stove_BackPanel", (0.0, 5.92, 1.20),
             (0.80, 0.04, 0.40), COL_APPLIANCE)
    for ki in range(4):
        make_cyl(f"Stove_Knob_{ki}", (-0.30 + ki * 0.20, 5.92, 1.20),
                 0.025, 0.04, P.METAL_BLACK, axis='Y')
    # Fridge (east end of north wall)
    make_box("Fridge_Body", (+2.0, 5.50, 1.00),
             (0.80, 0.80, 2.00), COL_APPLIANCE)
    make_box("Fridge_Door_Top", (+2.0, 5.10, 1.50),
             (0.78, 0.04, 0.80), COL_APPLIANCE)
    make_box("Fridge_Door_Bot", (+2.0, 5.10, 0.40),
             (0.78, 0.04, 1.00), COL_APPLIANCE)
    make_box("Fridge_Handle_Top", (+1.92, 5.06, 1.80),
             (0.03, 0.04, 0.10), P.METAL_STEEL)
    make_box("Fridge_Handle_Bot", (+1.92, 5.06, 0.80),
             (0.03, 0.04, 0.10), P.METAL_STEEL)
    # Magnets on fridge — colorful tile pattern
    for mi in range(8):
        mx_off = -0.30 + (mi % 4) * 0.20
        my_off = 0.0 if mi < 4 else -0.10
        tint = P.SNACK_TINTS[mi % len(P.SNACK_TINTS)]
        make_box(f"Fridge_Magnet_{mi}",
                 (+2.0 + mx_off, 5.075, 1.60 + my_off),   # on the door face
                 (0.05, 0.005, 0.08), tint)


def build_kitchen_table_chairs():
    # The DINING table (2026-10-03: the breakfast table was an 80 cm
    # square with two chairs in a corner; the house has a dining room
    # now — see build_house_rooms_2026_10). Four chairs that do not
    # match: secondhand, two of them a different wood.
    tx, ty = +2.55, 1.95
    make_table("Table", tx, ty, w=1.30, d=0.85, h=0.74, wood=COL_WOOD_TRIM)
    other = (0.34, 0.26, 0.18, 1.0)
    for ci, (cx, cy, yaw, wd) in enumerate([(tx - 0.33, ty - 0.62, 3.1416, COL_WOOD_TRIM), (tx + 0.33, ty - 0.62, 3.1416, other),
                                            (tx - 0.33, ty + 0.62, 0.0, other), (tx + 0.33, ty + 0.62, 0.0, COL_WOOD_TRIM)]):
        make_chair(f"Chair_{ci}", cx, cy, yaw=yaw, wood=wd, w=0.42)


def build_living_room_tv_corner():
    # CRT TV in the south-east corner — the Anya tape lands here
    # (Elicia at the Roberts cameo). Top of the case at z=0.66.
    # (2026-10-03: in the LIVING ROOM now, on a low cabinet against its
    # east wall, the screen facing west into the room — it stood in the
    # kitchen's south-east corner)
    tx, ty = -1.62, 2.65
    make_box("TV_Cabinet", (tx, ty, 0.25), (0.46, 0.70, 0.50), (0.38, 0.28, 0.18, 1.0))
    make_box("TV_Cabinet_Door", (tx - 0.235, ty, 0.25), (0.02, 0.62, 0.42), (0.46, 0.34, 0.22, 1.0))
    make_box("TV_Case", (tx, ty, 0.75),
             (0.50, 0.60, 0.50), COL_TV_CASE)
    make_box("TV_Screen", (tx - 0.26, ty, 0.81),      # faces WEST, into the living room
             (0.005, 0.40, 0.30), COL_TV_SCREEN)
    # VCR on top of the set, the cassette half-ejected toward the room
    make_box("VCR", (tx, ty, 1.05),
             (0.40, 0.50, 0.10), P.METAL_BLACK)
    make_box("VCR_Tape", (tx - 0.20, ty, 1.09),
             (0.10, 0.16, 0.02), COL_TV_CASE)


def build_decor():
    make_wall_clock("Clock", (-3.900, 4.0, 2.10),
                    frozen_hour=8, frozen_min=15, facing='+X')
    make_calendar("Calendar", (-3.8975, 4.9, 1.60))   # (2026-10-03: the west wall's south half is the living room)
    make_faded_poster("Poster", (3.8965, 2.9, 1.70), into_room=-1)
    make_floor_plant("Plant", (-3.55, 5.35, 0.0),
                     palette={"leaf": COL_CURTAIN_SAGE,
                              "pot": COL_WOOD_TRIM})
    # Door hinges
    make_door_hinges("FrontDoor_Hinge", edge_x=+1.10, edge_y=0.0,   # the leaf hangs on the east jamb (2026-10-02)
                     edge_z_centers=[0.30, 1.05, 1.80], axis='X')


def build_ceiling_infra():
    # Domestic light, not shop tubes (hero-prop pass)
    make_cyl("Ceiling_Dome", (0.0, 2.2, CEIL_Z-0.10), 0.15, 0.14, (0.94, 0.88, 0.70, 1.0), segments=12)
    make_smoke_detector("Smoke", (0.9, 2.2, CEIL_Z))


def build_hero_props():
    """2026-08-03 tail pass: THE WRENCH, the World's Okayest Weaver
    mug, the windowsill radio + driftwood, the front-hall table
    (keys / mail / pinecone bowl / the Polaroid), the dishtowel."""
    make_box("Wrench", (-2.0, 5.25, 0.945), (0.05, 0.26, 0.03), (0.42, 0.44, 0.46, 1.0))
    make_cyl("Mug_Weaver", (-1.30, 5.35, 0.98), 0.045, 0.10, (0.72, 0.62, 0.44, 1.0), segments=10)
    make_box("Mug_Weaver_Band", (-1.285, 5.35, 1.00), (0.02, 0.06, 0.03), (0.30, 0.30, 0.34, 1.0))
    # Sill under the E window: radio + Philip's driftwood
    make_box("E_Sill", (ROOM_W/2.0-0.18, 3.5, 0.94), (0.16, 1.90, 0.05), (0.46, 0.34, 0.22, 1.0))   # on the E wall (2026-09-22: 6 cm off it)
    make_box("Sill_Radio", (ROOM_W/2.0-0.20, 3.10, 1.05), (0.14, 0.24, 0.16), (0.36, 0.32, 0.28, 1.0))
    # (2026-10-03: a face — the grille, the dial window, two knobs, the aerial)
    make_box("Sill_Radio_Grille", (ROOM_W/2.0-0.272, 3.14, 1.05), (0.004, 0.12, 0.12), (0.62, 0.56, 0.44, 1.0))
    make_box("Sill_Radio_Dial", (ROOM_W/2.0-0.272, 3.01, 1.08), (0.004, 0.08, 0.04), (0.92, 0.84, 0.60, 1.0))
    for i, oy in enumerate((2.99, 3.04)):
        make_cyl(f"Sill_Radio_Knob_{i}", (ROOM_W/2.0-0.275, oy, 1.00), 0.012, 0.012, (0.16, 0.16, 0.18, 1.0), segments=8, axis='X')
    make_cyl("Sill_Radio_Aerial", (ROOM_W/2.0-0.16, 3.20, 1.30), 0.003, 0.34, P.METAL_STEEL, segments=5)
    make_cyl("Sill_Driftwood", (ROOM_W/2.0-0.20, 3.95, 1.00), 0.05, 0.30, (0.62, 0.55, 0.44, 1.0), segments=7, axis='Y')
    # The small table by the door: keys, unopened mail, pinecones,
    # and the Polaroid the scene ends on
    # (2026-10-03: along the FOYER's west wall — "the small table by the
    # door"; it stood where the living room's sofa is now)
    make_box("Hall_Table", (-1.02, 1.00, 0.76), (0.40, 0.80, 0.04), (0.42, 0.30, 0.20, 1.0))
    for ly in (0.66, 1.34):
        make_box(f"Hall_Table_Leg_{ly:.2f}", (-1.02, ly, 0.38), (0.35, 0.05, 0.74), (0.34, 0.24, 0.15, 1.0))
    make_box("Hall_Keys", (-1.08, 0.72, 0.79), (0.05, 0.08, 0.015), (0.62, 0.64, 0.66, 1.0))
    make_box("Unopened_Mail", (-1.00, 1.05, 0.79), (0.14, 0.22, 0.03), (0.88, 0.86, 0.78, 1.0))
    make_cyl("Pinecone_Bowl", (-1.04, 1.28, 0.80), 0.09, 0.06, (0.52, 0.42, 0.30, 1.0), segments=10)
    for i, (px, py) in enumerate(((-1.06, 1.26), (-1.00, 1.31), (-1.08, 1.32))):
        make_cyl(f"Pinecone_{i}", (px, py, 0.85), 0.022, 0.04, (0.40, 0.30, 0.20, 1.0), segments=6)
    make_box("The_Polaroid", (-0.92, 0.86, 0.785), (0.11, 0.09, 0.003), (0.92, 0.90, 0.86, 1.0))
    # The dishtowel, clean an hour ago
    make_box("Dishtowel", (0.0, 5.235, 0.68), (0.30, 0.04, 0.28), (0.78, 0.74, 0.66, 1.0))   # over the oven door (2026-09-22: 3 cm off it)



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (adaptive template pass per
    lore/_SET_DETAIL_PLAYBOOK.md). Per-locale wear personality is
    the next pass."""
    pw = PAL_DOMESTIC_WALL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL_Z - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL_Z - 0.16, tint=band)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def build_kitchen_bones_2026_10():
    """The kitchen's BONES (2026-10-02). With the proof-of-life props in,
    the room still read as a cream box with an island in it: the north
    wall had a sink, a stove and a fridge standing apart on bare wall —
    no counters between them, no upper cabinets, no backsplash, no
    window over the sink. A kitchen is its runs. Here: base counters
    filling the gaps (cabinet fronts, knobs), a tiled backsplash the
    length of the run, upper cabinets, a hood over the stove, a window
    over the sink with the back yard beyond it (the bird in the prose
    is outside THIS window), and the counter's clutter — canisters, the
    kettle, the spoon crock, the paper towels."""
    fm = PAL_DOMESTIC_COUNTER["formica"]
    kick = PAL_DOMESTIC_COUNTER["kick"]
    top = PAL_DOMESTIC_COUNTER["top"]
    cab = (0.56, 0.42, 0.28, 1.0)          # oak cabinet fronts
    tile = (0.88, 0.86, 0.78, 1.0)
    grout = (0.74, 0.70, 0.62, 1.0)
    wall_y = ROOM_D - 0.10                   # the north wall's ROOM FACE: make_wall builds 20 cm thick
                                             # on the line, so anything at ROOM_D sits inside the wall
                                             # (the first build's backsplash and window did)
    # ── base counters in the gaps: sink (-2.9..-1.1) → stove (-0.4..0.4) → fridge (1.6)
    for nm, x0, x1 in (("CounterRun_W", -1.10, -0.40), ("CounterRun_E", 0.40, 1.60)):
        cx, w = (x0 + x1) / 2.0, x1 - x0
        make_box(f"{nm}_Base", (cx, wall_y - 0.36, 0.44), (w, 0.68, 0.88), kick)
        make_box(f"{nm}_Top", (cx, wall_y - 0.36, 0.90), (w, 0.70, 0.04), fm)
        # a drawer front over a cabinet door front, each with a knob
        make_box(f"{nm}_Drawer", (cx, wall_y - 0.705, 0.76), (w - 0.06, 0.02, 0.16), cab)
        make_box(f"{nm}_Door", (cx, wall_y - 0.705, 0.37), (w - 0.06, 0.02, 0.58), cab)
        make_cyl(f"{nm}_DrawerKnob", (cx, wall_y - 0.725, 0.76), 0.014, 0.02, P.METAL_STEEL, segments=6, axis='Y')
        make_cyl(f"{nm}_DoorKnob", (cx + w * 0.3, wall_y - 0.725, 0.52), 0.014, 0.02, P.METAL_STEEL, segments=6, axis='Y')
    # the sink base gets its cabinet doors too (the open one is in the life pass)
    make_box("Sink_Door_W", (-2.55, 5.24, 0.37), (0.60, 0.02, 0.58), cab)              # on the sink base's front (5.25)
    make_cyl("Sink_Door_W_Knob", (-2.35, 5.22, 0.52), 0.014, 0.02, P.METAL_STEEL, segments=6, axis='Y')
    # ── backsplash: tile the run, sink to fridge, counter top to the uppers
    make_box("Backsplash", (-0.65, wall_y - 0.025, 1.22), (4.50, 0.03, 0.56), tile)
    for r in range(3):
        make_box(f"Backsplash_GroutH_{r}", (-0.65, wall_y - 0.042, 1.00 + r * 0.15), (4.50, 0.004, 0.008), grout)
    for c in range(15):
        make_box(f"Backsplash_GroutV_{c}", (-2.80 + c * 0.30, wall_y - 0.042, 1.22), (0.008, 0.004, 0.56), grout)
    # ── upper cabinets (z 1.50..2.25, 0.34 deep) over the two runs and east
    #    of the window; the hood over the stove; the window over the sink
    for nm, x0, x1 in (("Upper_W", -1.25, -0.40), ("Upper_E", 0.40, 1.60)):
        cx, w = (x0 + x1) / 2.0, x1 - x0
        make_box(f"{nm}_Box", (cx, wall_y - 0.17, 1.875), (w, 0.34, 0.75), kick)
        n = 2 if w > 0.9 else 1
        for i in range(n):
            dx = (i - (n - 1) / 2.0) * (w / n)
            make_box(f"{nm}_Door_{i}", (cx + dx, wall_y - 0.345, 1.875), (w / n - 0.04, 0.02, 0.71), cab)
            make_cyl(f"{nm}_Knob_{i}", (cx + dx + (0.12 if i == 0 else -0.12) * (1 if n > 1 else 0) + (0.0 if n > 1 else w * 0.3), wall_y - 0.365, 1.60), 0.014, 0.02, P.METAL_STEEL, segments=6, axis='Y')
    # the hood hangs at the uppers' bottom line (1.50) so the cabinets
    # flank it; a shallower body and a wider chimney, flush to the wall —
    # from the door the deep body read as set off from its vent (the
    # Deck, 2026-10-02: "hood looks misaligned on vent")
    make_box("Hood_Body", (0.0, wall_y - 0.24, 1.58), (0.84, 0.46, 0.16), COL_APPLIANCE)
    make_box("Hood_Chimney", (0.0, wall_y - 0.16, 2.12), (0.52, 0.30, 0.92), COL_APPLIANCE)
    make_box("Hood_Light", (0.0, wall_y - 0.40, 1.495), (0.30, 0.10, 0.01), (0.98, 0.94, 0.80, 1.0))
    # the window sits ABOVE the tile band (its lower panes were in it:
    # "rack or window overlapping tile"): sill on the tile's top edge (1.50)
    make_window("Window_Sink", (-2.0, wall_y, 1.98), width=1.30, height=0.84, room_dir=-1, see_through=True)
    make_box("Window_Sink_Sill", (-2.0, wall_y - 0.06, 1.52), (1.44, 0.14, 0.04), COL_WOOD_TRIM)
    make_backyard_view("Yard_N", ROOM_D + 0.12, span=4.5, tree=(-3.2, 3.2), fence_dist=4.6)
    # ── the counter's clutter
    for i, (cx, h, col) in enumerate(((-0.95, 0.22, (0.86, 0.82, 0.72, 1.0)), (-0.78, 0.18, (0.86, 0.82, 0.72, 1.0)), (-0.62, 0.14, (0.86, 0.82, 0.72, 1.0)))):
        make_cyl(f"Canister_{i}", (cx, wall_y - 0.50, 0.92 + h / 2.0), 0.06, h, col, segments=10)
        make_cyl(f"Canister_{i}_Lid", (cx, wall_y - 0.50, 0.92 + h + 0.01), 0.062, 0.02, COL_WOOD_TRIM, segments=10)
    make_cyl("Spoon_Crock", (0.62, wall_y - 0.50, 1.00), 0.055, 0.16, (0.52, 0.40, 0.30, 1.0), segments=10)
    for i, (dx, dy, h) in enumerate(((-0.02, 0.0, 0.26), (0.02, 0.03, 0.24), (0.0, -0.03, 0.28))):
        make_box(f"Spoon_{i}", (0.62 + dx, wall_y - 0.50 + dy, 1.08 + h / 2.0), (0.012, 0.012, h), COL_WOOD_TRIM)
    make_cyl("Paper_Towels", (1.25, wall_y - 0.50, 1.04), 0.055, 0.24, (0.94, 0.93, 0.90, 1.0), segments=10)
    make_cyl("Paper_Towels_Core", (1.25, wall_y - 0.50, 1.17), 0.02, 0.03, (0.62, 0.52, 0.40, 1.0), segments=8)
    make_cyl("Kettle", (-0.20, wall_y - 0.50, 1.01), 0.10, 0.14, P.METAL_STEEL, segments=10)   # on the back-left burner
    make_box("Kettle_Handle", (-0.20, wall_y - 0.50, 1.095), (0.03, 0.14, 0.03), (0.12, 0.12, 0.12, 1.0))   # on the kettle's lid (1.08)
    make_cyl("Kettle_Spout", (-0.08, wall_y - 0.44, 1.06), 0.014, 0.10, P.METAL_STEEL, segments=6, axis='X')


def build_front_door_porch_2026_10():
    """D5 — the set never ends at the walls (2026-10-02). The front
    doorway was a 2.2 m hole onto the void: `shot_insert_door` looked at
    nothing, and the chapter's own geography is OUT there — "the morning
    light through the screen door making a soft grid on the worn pine
    floor", the boy on the porch, "the gravel drive", "a station wagon
    idling at the curb". So: the solid door standing open into the
    hall, a SCREEN door closed across the opening (a lattice of fine
    bars — it casts the grid), the threshold, a porch deck under an
    eave on two posts, three steps, the gravel drive, the wagon at the
    curb, and trees past it."""
    wood = COL_WOOD_TRIM
    deck = (0.50, 0.40, 0.28, 1.0)
    bar = (0.26, 0.24, 0.22, 1.0)
    # (no solid leaf: a 2.2 m opening leaves no honest place for an open
    # door inside — the hall table and the boots on the west, the front
    # window on the east — and the doorway gate wants a door's swing
    # clear. The hinges on the east jamb say where it went; the SCREEN
    # door is what the prose sees.)
    make_threshold("FrontDoor_Threshold", (0.0, 0.0), width=2.20, axis='X')
    # the screen door: frame, mid rail, a lattice of fine bars, the pull
    sy = -0.03
    make_box("ScreenDoor_Jamb_W", (-1.07, sy, 1.0), (0.06, 0.04, 2.0), wood)
    make_box("ScreenDoor_Jamb_E", (+1.07, sy, 1.0), (0.06, 0.04, 2.0), wood)
    make_box("ScreenDoor_Rail_Top", (0.0, sy, 1.97), (2.20, 0.04, 0.06), wood)
    make_box("ScreenDoor_Rail_Bot", (0.0, sy, 0.10), (2.20, 0.04, 0.20), wood)
    make_box("ScreenDoor_Rail_Mid", (0.0, sy, 0.95), (2.20, 0.04, 0.05), wood)
    for i in range(1, 14):
        make_box(f"ScreenDoor_BarV_{i}", (-1.10 + i * (2.20 / 14.0), sy, 1.07), (0.008, 0.008, 1.74), bar)
    for j in range(1, 9):
        make_box(f"ScreenDoor_BarH_{j}", (0.0, sy, 0.20 + j * (1.74 / 9.0)), (2.08, 0.008, 0.008), bar)
    make_box("ScreenDoor_Pull", (0.85, sy - 0.05, 1.0), (0.04, 0.06, 0.18), P.METAL_STEEL)
    # the porch: deck, two posts, the eave, three steps
    make_box("Porch_Deck", (0.0, -1.35, -0.03), (5.0, 2.60, 0.06), deck)
    for i in range(12):
        make_box(f"Porch_Board_Gap_{i}", (0.0, -0.20 - i * 0.22, 0.002), (5.0, 0.012, 0.004), (0.34, 0.27, 0.19, 1.0))
    for px in (-2.2, 2.2):
        make_box(f"Porch_Post_{px:+.1f}", (px, -2.5, 1.25), (0.14, 0.14, 2.50), (0.90, 0.88, 0.82, 1.0))
    make_box("Porch_Eave", (0.0, -1.35, 2.56), (5.4, 2.90, 0.12), (0.40, 0.30, 0.22, 1.0))
    make_box("Porch_Fascia", (0.0, -2.78, 2.42), (5.4, 0.06, 0.28), (0.90, 0.88, 0.82, 1.0))
    for i in range(3):
        make_box(f"Porch_Step_{i}", (0.0, -2.85 - i * 0.30, -0.08 - i * 0.16), (1.60, 0.32, 0.10), deck)
    # the gravel drive and the curb, the wagon idling, trees past it
    make_box("Gravel_Drive", (0.6, -6.0, -0.56), (9.0, 6.0, 0.04), (0.62, 0.58, 0.50, 1.0))
    make_box("Ground_Lawn_S", (-4.5, -6.0, -0.57), (6.0, 6.0, 0.03), (0.42, 0.50, 0.30, 1.0))
    make_box("Curb", (0.0, -9.1, -0.52), (18.0, 0.20, 0.12), (0.66, 0.64, 0.60, 1.0))
    make_box("Ground_Street", (0.0, -12.0, -0.60), (24.0, 5.6, 0.03), (0.30, 0.30, 0.31, 1.0))
    # "idling at the curb": on the street, past the curb (its far wheels
    # hung over the curb line at -8.3 — the grammar gate's OUTSIDE)
    make_car("StationWagon", 1.6, -10.3, 4.9, (0.46, 0.34, 0.20, 1.0), hatch=True, along="X", z0=-0.585)
    from _props.trees import make_broadleaf
    make_broadleaf("Tree_SW", -5.5, -7.5, 6.5, (0.34, 0.46, 0.24, 1.0), (0.36, 0.28, 0.20, 1.0))
    make_broadleaf("Tree_SE", 6.5, -5.0, 5.5, (0.38, 0.48, 0.26, 1.0), (0.36, 0.28, 0.20, 1.0))


def build_proof_of_life_2026_10():
    """D4 USE STATES — the Roberts house LIVED IN (2026-10-02, the
    Deck: "the lovers domicile needs to feel domestic and lived in,
    proof of life, not a sterile empty thing"). Everything here is in
    the chapter's prose or follows from it, and the wear personality is
    the Lovers' — IN PAIRS (lore/_SET_DETAIL_PLAYBOOK, 2026-08-19):
      · Philip is mid-repair at the dripping faucet: the cabinet under
        the sink open, his toolbox open on the floor, a bucket, a rag,
        water standing in the bowl
      · dishes drying — two plates, two glasses, two mugs (the chipped
        Weaver mug and his)
      · the neighbours' casserole dish, foil-wrapped, returned Friday
      · breakfast interrupted: the paper folded open, a plate with
        toast crusts, the jam with its lid off, a knife
      · Mackenzie's garden: muddy boots at the door (a pair), gloves
        and a trowel, the basil pot on the windowsill
      · her loom in the west corner with a cloth half woven
      · the laundry basket with the towels folded, the trash with the
        crumple beside it, the grocery list on the fridge
      · the floor: the lane door → island → sink worn darker, and TWO
        mug rings side by side on the island where they sit together
    """
    wood = COL_WOOD_TRIM
    steel = P.METAL_STEEL
    lino = COL_LINOLEUM
    worn = (lino[0] * 0.86, lino[1] * 0.86, lino[2] * 0.84, 1.0)
    cream = (0.92, 0.90, 0.84, 1.0)
    towel = (0.72, 0.68, 0.58, 1.0)
    # ── the floor remembers them: door → island's west end → sink; a
    #    narrower lane island → the table; the mat at the sink
    make_traffic_wear("Lane_Entry_Sink", [(0.0, 0.45), (0.0, 2.1), (-1.0, 2.6), (-1.0, 4.4), (-2.0, 4.9)], width=0.62, tint=worn)
    make_traffic_wear("Lane_Island_Table", [(0.9, 2.3), (1.8, 2.3)], width=0.42, tint=worn)
    make_box("Sink_Mat", (-2.0, 4.70, 0.012), (0.90, 0.55, 0.02), (0.46, 0.40, 0.34, 1.0))
    # ── Philip, under the sink: the cabinet door swung open (a panel
    #    standing out from the base at the hinge), the toolbox open, a
    #    bucket, the rag, water standing in the bowl
    make_box("Sink_Cabinet_Door_Open", (-1.65, 5.03, 0.42), (0.04, 0.46, 0.76), PAL_DOMESTIC_COUNTER["kick"])
    make_box("Sink_Cabinet_Dark", (-2.15, 5.28, 0.40), (0.78, 0.04, 0.70), (0.12, 0.10, 0.08, 1.0))
    make_box("Toolbox_Body", (-2.55, 4.45, 0.09), (0.40, 0.20, 0.18), (0.70, 0.18, 0.14, 1.0))
    make_box("Toolbox_Lid_Open", (-2.55, 4.34, 0.27), (0.40, 0.03, 0.20), (0.62, 0.16, 0.12, 1.0))   # hinged on the box's front edge
    make_box("Toolbox_Tray", (-2.55, 4.45, 0.19), (0.36, 0.16, 0.02), (0.30, 0.30, 0.32, 1.0))
    make_box("Toolbox_Pliers", (-2.60, 4.46, 0.21), (0.18, 0.03, 0.02), steel)
    make_cyl("Bucket", (-1.35, 4.60, 0.14), 0.15, 0.28, (0.80, 0.80, 0.78, 1.0), segments=10)
    make_cyl("Bucket_Water", (-1.35, 4.60, 0.26), 0.13, 0.01, (0.46, 0.56, 0.62, 1.0), segments=10)
    make_box("Sink_Rag", (-1.25, 5.26, 0.90), (0.26, 0.10, 0.05), (0.62, 0.58, 0.50, 1.0))   # over the counter's edge
    make_cyl("Sink_Standing_Water", (-2.0, 5.55, 0.733), 0.17, 0.006, (0.52, 0.60, 0.66, 1.0), segments=12)   # in the basin (2026-10-03)
    make_box("Sink_Drip_Dark", (-2.0, 5.55, 0.737), (0.06, 0.06, 0.003), (0.38, 0.46, 0.52, 1.0))
    # ── dishes drying beside the sink (two of everything), the soap
    make_box("Dish_Rack_Base", (-1.25, 5.62, 0.9275), (0.42, 0.36, 0.015), steel)   # on the counter (0.92)
    for i, px in enumerate((-1.36, -1.26, -1.16)):
        make_cyl(f"Dish_Rack_Plate_{i}", (px, 5.62, 1.052), 0.12, 0.012, cream, segments=12, axis='X')   # standing on the rack
    for i, (gx, gy) in enumerate(((-1.10, 5.50), (-1.40, 5.74))):
        make_cyl(f"Dish_Rack_Glass_{i}", (gx, gy, 0.978), 0.035, 0.09, (0.80, 0.86, 0.88, 1.0), segments=8)
    make_bottle("Dish_Soap", -1.48, 5.86, 0.92, (0.42, 0.66, 0.36, 1.0), h=0.20, r=0.03)   # on the counter east of the basin (2026-10-03: it stood over the hole)
    make_mug("Mug_Philip", -1.18, 5.30, 0.945, (0.30, 0.34, 0.42, 1.0), handle_side=-1)   # his, beside hers
    # ── the casserole, foil-wrapped, returned Friday — on the island
    isl = 0.98                                     # the island's top (make_counter: base + height + 0.06)
    # (the island runs NORTH-SOUTH: x -0.6..0.6, y 1.6..4.4 — the first
    # placement at x 0.95 stood a foot past its east edge)
    make_box("Casserole_Dish", (0.22, 3.95, isl + 0.035), (0.34, 0.24, 0.07), (0.86, 0.84, 0.78, 1.0))
    make_box("Casserole_Foil", (0.22, 3.95, isl + 0.08), (0.36, 0.26, 0.02), (0.78, 0.80, 0.82, 1.0))
    make_box("Casserole_Foil_Dimple_0", (0.17, 3.92, isl + 0.094), (0.08, 0.06, 0.008), (0.70, 0.72, 0.74, 1.0))
    make_box("Casserole_Foil_Dimple_1", (0.29, 3.99, isl + 0.094), (0.07, 0.05, 0.008), (0.70, 0.72, 0.74, 1.0))
    # ── TWO mug rings on the island where they sit, close together
    for i, (rx, ry) in enumerate(((-0.34, 2.06), (-0.22, 2.12))):   # the island's south-west corner, by the stools
        make_floor_stain(f"Island_Ring_{i}", (rx, ry), radius=0.045, floor_z=0.98, tint=(0.56, 0.44, 0.28, 1.0))
        make_floor_stain(f"Island_Ring_{i}_Hole", (rx, ry), radius=0.034, floor_z=0.982, tint=PAL_DOMESTIC_COUNTER["top"])
    # ── breakfast, interrupted (the table at +2.5, 1.5, top 0.74)
    make_box("Newspaper", (2.67, 1.83, 0.745), (0.34, 0.26, 0.01), (0.84, 0.82, 0.76, 1.0))
    make_box("Newspaper_Fold", (2.67, 1.83, 0.752), (0.34, 0.02, 0.012), (0.70, 0.68, 0.62, 1.0))
    make_box("Newspaper_Headline", (2.60, 1.91, 0.752), (0.16, 0.03, 0.004), (0.22, 0.22, 0.24, 1.0))
    make_plate("Toast_Plate", 2.37, 2.11, 0.745, cream, r=0.11)
    make_box("Toast_Crust_0", (2.33, 2.14, 0.76), (0.07, 0.02, 0.012), (0.58, 0.42, 0.22, 1.0))
    make_box("Toast_Crust_1", (2.42, 2.07, 0.76), (0.02, 0.06, 0.012), (0.58, 0.42, 0.22, 1.0))
    make_jar("Jam", 2.73, 2.15, 0.745, (0.52, 0.14, 0.18, 0.95), h=0.10, r=0.04)
    make_cyl("Jam_Lid_Off", (2.85, 2.01, 0.75), 0.042, 0.012, (0.62, 0.58, 0.50, 1.0), segments=10)
    make_box("Butter_Knife", (2.55, 2.23, 0.75), (0.16, 0.018, 0.006), steel)
    # ── Mackenzie's garden came in with her: boots inside the door (a
    #    pair, one tipped), the mud they tracked, gloves and the trowel
    # (2026-10-03: on the foyer's door mat; the gloves and trowel beside)
    make_box("Boot_L", (-0.40, 0.44, 0.13), (0.11, 0.28, 0.22), (0.26, 0.22, 0.16, 1.0))
    make_box("Boot_R_Tipped", (-0.24, 0.40, 0.09), (0.11, 0.30, 0.14), (0.26, 0.22, 0.16, 1.0))
    make_box("Boot_L_Mud", (-0.40, 0.52, 0.05), (0.12, 0.10, 0.06), (0.34, 0.28, 0.18, 1.0))
    make_floor_stain("Mud_Track_0", (-0.20, 1.05), radius=0.09, tint=(0.52, 0.44, 0.32, 1.0))
    make_floor_stain("Mud_Track_1", (-0.05, 1.45), radius=0.07, tint=(0.52, 0.44, 0.32, 1.0))
    make_box("Garden_Glove_0", (0.22, 0.40, 0.035), (0.22, 0.11, 0.03), (0.60, 0.52, 0.36, 1.0))
    make_box("Garden_Glove_1", (0.28, 0.48, 0.065), (0.20, 0.10, 0.03), (0.60, 0.52, 0.36, 1.0))
    make_box("Trowel_Blade", (0.50, 0.44, 0.032), (0.07, 0.14, 0.012), steel)
    make_cyl("Trowel_Handle", (0.50, 0.58, 0.04), 0.014, 0.12, (0.52, 0.34, 0.20, 1.0), segments=6, axis='Y')
    # the basil pot on the east sill, between the radio and the driftwood
    bx, by, bz = ROOM_W / 2.0 - 0.20, 3.52, 0.965
    make_cyl("Basil_Pot", (bx, by, bz + 0.07), 0.07, 0.14, (0.72, 0.42, 0.28, 1.0), segments=10)
    make_cyl("Basil_Soil", (bx, by, bz + 0.135), 0.06, 0.01, (0.26, 0.20, 0.14, 1.0), segments=10)
    for i, (lx, ly, lz, lw) in enumerate(((0.0, 0.0, 0.26, 0.10), (-0.05, 0.04, 0.22, 0.08), (0.05, -0.03, 0.23, 0.08), (0.02, 0.05, 0.19, 0.07))):
        make_box(f"Basil_Leaf_{i}", (bx + lx, by + ly, bz + lz), (lw, lw * 0.8, 0.012), (0.34, 0.52, 0.26, 1.0))
    # ── her loom in the west corner: frame, warp, a cloth half woven
    lx0, ly0 = -3.42, 2.95   # (2026-10-03: the living room's north-west corner)
    for sx in (-0.36, 0.36):
        make_box(f"Loom_Upright_{sx:+.2f}", (lx0 + sx, ly0, 0.62), (0.05, 0.05, 1.24), wood)
    make_box("Loom_Beam_Top", (lx0, ly0, 1.22), (0.78, 0.06, 0.06), wood)
    make_box("Loom_Beam_Breast", (lx0, ly0 - 0.02, 0.36), (0.78, 0.07, 0.06), wood)
    make_box("Loom_Foot", (lx0, ly0 + 0.10, 0.03), (0.80, 0.42, 0.06), wood)
    for i in range(13):
        make_box(f"Loom_Warp_{i}", (lx0 - 0.30 + i * 0.05, ly0 - 0.03, 0.79), (0.006, 0.006, 0.80), (0.86, 0.82, 0.70, 1.0))
    make_box("Loom_Cloth_Woven", (lx0, ly0 - 0.035, 0.57), (0.64, 0.012, 0.36), COL_CURTAIN_SAGE)
    make_box("Loom_Cloth_Stripe", (lx0, ly0 - 0.042, 0.50), (0.64, 0.004, 0.05), (0.62, 0.32, 0.26, 1.0))
    make_box("Loom_Shuttle", (lx0 + 0.12, ly0 - 0.02, 0.405), (0.16, 0.03, 0.03), (0.42, 0.30, 0.20, 1.0))   # resting on the breast beam
    make_cyl("Yarn_Ball_0", (lx0 - 0.42, ly0 + 0.30, 0.10), 0.07, 0.12, (0.62, 0.32, 0.26, 1.0), segments=8)
    make_cyl("Yarn_Ball_1", (lx0 - 0.28, ly0 + 0.36, 0.08), 0.06, 0.10, COL_CURTAIN_SAGE, segments=8)
    # ── the laundry, folded; the trash, and the crumple beside it; the
    #    grocery list on the fridge under a magnet
    make_cyl("Laundry_Basket", (-3.45, 4.35, 0.17), 0.26, 0.34, (0.78, 0.74, 0.62, 1.0), segments=10)
    for i in range(3):
        make_box(f"Folded_Towel_{i}", (-3.45, 4.35, 0.37 + i * 0.07), (0.34 - i * 0.02, 0.26, 0.06), [towel, cream, COL_CURTAIN_SAGE][i])
    make_trash_can("Trash", (3.35, 5.25, 0.0), palette={"body": (0.36, 0.38, 0.40, 1.0)}, branded=False)
    make_box("Trash_Crumple_0", (3.05, 4.95, 0.035), (0.08, 0.07, 0.07), (0.88, 0.86, 0.80, 1.0))
    make_box("Trash_Crumple_1", (3.00, 5.08, 0.028), (0.06, 0.06, 0.055), (0.88, 0.86, 0.80, 1.0))
    make_box("Fridge_Grocery_List", (+1.80, 5.072, 1.22), (0.11, 0.004, 0.16), (0.96, 0.95, 0.90, 1.0))
    for i in range(5):
        make_box(f"Fridge_List_Line_{i}", (+1.80, 5.069, 1.27 - i * 0.025), (0.07 - (i % 2) * 0.02, 0.002, 0.004), (0.28, 0.28, 0.32, 1.0))
    make_box("Fridge_Photo", (+2.22, 5.072, 1.26), (0.10, 0.004, 0.08), (0.86, 0.80, 0.70, 1.0))




# ════════════════════════════════════════════════════════════════
# THE HOUSE (2026-10-03). The Deck: "mackenzie home still looking
# wrong … I want it to feel cozy, brimming with detail. Photos, and
# collections and comfy furniture and book shelves and lived in
# spaces, not antiseptic and sterile" / "a foyer, a living room, a
# dining room/kitchen, I want to have character." One 8×6 box with a
# kitchen run in it was never a house. Now:
#   FOYER   x −1.3..1.3 · y 0..1.9 — walls either side of the front
#           door, a cased opening north into the house; the hall table
#           (keys, mail, pinecones, the Polaroid), the door mat with
#           her boots, a bench with coats on hooks over it, a mirror
#   LIVING  x −4..−1.3 · y 0..3.4 — a window over the sofa, the sofa
#           with its quilt, an armchair, the coffee table with its
#           books, a rug, the bookcase (books, a framed photo, the shell
#           and pinecone collection), the gallery wall, the TV, her
#           loom in the corner, a floor lamp; walls a dusty sage
#   DINING  x 1.3..4 · y 0..4 — the table for four, a pendant over it,
#           the hutch with the plates and the preserves, the sideboard
#           under the front window with the photographs and the
#           garden's flowers, cookbooks on the foyer wall's shelf,
#           beadboard wainscot
#   KITCHEN the north run, unchanged (build_kitchen_bones_2026_10)
# "the small house they had cobbled together out of salvaged lumber
# and secondhand furniture" — nothing matches, everything is kept.
# ════════════════════════════════════════════════════════════════
COL_LIVING_PAINT = (0.66, 0.70, 0.60, 1.0)     # dusty sage
COL_DINING_WAINSCOT = (0.90, 0.88, 0.80, 1.0)  # beadboard, cream
COL_FRAME_DARK = (0.24, 0.18, 0.12, 1.0)
COL_FRAME_GOLD = (0.62, 0.52, 0.30, 1.0)
PHOTO_TINTS = [(0.72, 0.66, 0.54, 1.0), (0.58, 0.62, 0.66, 1.0), (0.70, 0.60, 0.50, 1.0),
               (0.52, 0.60, 0.52, 1.0), (0.76, 0.70, 0.58, 1.0), (0.60, 0.56, 0.60, 1.0)]
BOOK_TINTS = [(0.52, 0.20, 0.16, 1.0), (0.22, 0.30, 0.46, 1.0), (0.34, 0.44, 0.30, 1.0), (0.78, 0.70, 0.52, 1.0),
              (0.26, 0.22, 0.20, 1.0), (0.62, 0.48, 0.26, 1.0), (0.42, 0.26, 0.40, 1.0), (0.86, 0.82, 0.72, 1.0),
              (0.30, 0.46, 0.50, 1.0), (0.66, 0.32, 0.22, 1.0)]


def _facing_offsets(facing):
    """A wall-hung thing: (dx, dy) unit INTO the room and the axis it is wide along."""
    return {"+X": ((1.0, 0.0), 'Y'), "-X": ((-1.0, 0.0), 'Y'), "+Y": ((0.0, 1.0), 'X'), "-Y": ((0.0, -1.0), 'X')}[facing]


def _wall_frame(name, face_xy, z, w, h, facing, pic, frame=COL_FRAME_DARK, depth=0.025, mat=None):
    """A framed picture hung on a wall FACE (face_xy = a point on the
    face), its back on the face, `w` wide, `h` tall, looking `facing`."""
    (nx, ny), along = _facing_offsets(facing)
    fx, fy = face_xy
    cx, cy = fx + nx * depth / 2.0, fy + ny * depth / 2.0
    size = (depth, w, h) if along == 'Y' else (w, depth, h)
    make_box(f"{name}_Frame", (cx, cy, z), size, frame)
    px, py = fx + nx * (depth + 0.002), fy + ny * (depth + 0.002)
    if mat is not None:
        msize = (0.004, w - 0.04, h - 0.04) if along == 'Y' else (w - 0.04, 0.004, h - 0.04)
        make_box(f"{name}_Mat", (px, py, z), msize, mat)
        px, py = px + nx * 0.004, py + ny * 0.004
        w, h = w - 0.12, h - 0.12
    else:
        w, h = w - 0.04, h - 0.04
    psize = (0.004, w, h) if along == 'Y' else (w, 0.004, h)
    make_box(f"{name}_Pic", (px, py, z), psize, pic)


def _book_row(prefix, x0, y0, z0, n, along='X', depth=0.20, seed=0, lean_last=False):
    """`n` books standing on a shelf from (x0, y0) along the axis; each
    its own height, thickness and colour. Returns the run's length."""
    import random
    rnd = random.Random(seed)
    run = 0.0
    for i in range(n):
        t = rnd.choice((0.022, 0.028, 0.034, 0.040, 0.048))
        h = rnd.choice((0.18, 0.20, 0.22, 0.24, 0.27))
        col = BOOK_TINTS[(i * 3 + seed) % len(BOOK_TINTS)]
        if along == 'X':
            make_box(f"{prefix}_{i}", (x0 + run + t / 2.0, y0, z0 + h / 2.0), (t, depth * rnd.uniform(0.75, 1.0), h), col)
        else:
            make_box(f"{prefix}_{i}", (x0, y0 + run + t / 2.0, z0 + h / 2.0), (depth * rnd.uniform(0.75, 1.0), t, h), col)
        run += t + rnd.choice((0.0, 0.0, 0.004))
    return run


def _bookcase(prefix, x, y, w, d, h, shelves, wood, back_x_sign=-1):
    """A bookcase against a wall running N–S (its back toward
    back_x_sign·x): two sides, a top, a back, `shelves` shelf boards.
    Returns the shelf-top z values."""
    make_box(f"{prefix}_Side_S", (x, y - w / 2.0 + 0.01, h / 2.0), (d, 0.02, h), wood)
    make_box(f"{prefix}_Side_N", (x, y + w / 2.0 - 0.01, h / 2.0), (d, 0.02, h), wood)
    make_box(f"{prefix}_Top", (x, y, h - 0.01), (d, w, 0.02), wood)
    make_box(f"{prefix}_Back", (x + back_x_sign * (d / 2.0 - 0.006), y, h / 2.0), (0.012, w, h), (wood[0] * 0.8, wood[1] * 0.8, wood[2] * 0.8, 1.0))
    tops = []
    for i in range(shelves):
        z = 0.06 + i * ((h - 0.10) / shelves)
        make_box(f"{prefix}_Shelf_{i}", (x, y, z), (d - 0.012, w - 0.04, 0.02), wood)
        tops.append(z + 0.01)
    return tops


def build_house_rooms_2026_10():
    wood = COL_WOOD_TRIM
    wall = PAL_DOMESTIC_WALL["wall"]
    wall_pal = PAL_DOMESTIC_WALL
    steel = P.METAL_STEEL
    cream = (0.92, 0.90, 0.84, 1.0)
    quilt = (0.62, 0.36, 0.30, 1.0)
    sofa_col = (0.44, 0.48, 0.42, 1.0)      # a worn green-grey tweed
    chair_col = (0.56, 0.40, 0.30, 1.0)     # the armchair, rust
    rug_col = (0.52, 0.30, 0.26, 1.0)
    rug_edge = (0.72, 0.60, 0.44, 1.0)
    T = 0.12                                # interior walls, half the shell's thickness

    # ── FOYER WALLS and the cased opening into the house ──────────────
    # two walls off the south wall at x ±1.3 up to y 1.9; a header across
    # the opening at y 1.9 with casing on both posts; the living room's
    # east wall carries on from 1.9 to 3.4 (the living room opens NORTH,
    # onto the kitchen's west end, through a 2.5 m cased opening)
    for nm, x0, y0, y1, sign in (("Foyer_Wall_W", -1.30, 0.10, 1.90, +1), ("Foyer_Wall_E", +1.30, 0.10, 1.90, -1),
                                ("Living_Wall_E", -1.30, 1.90, 3.40, -1)):
        make_wall(nm, (x0, (y0 + y1) / 2.0, 0.0), length=y1 - y0, height=CEIL_Z, thickness=T,
                  axis='Y', palette=wall_pal, baseboard_face_sign=sign)
        # the other face's baseboard (make_wall gives one side)
        make_box(f"{nm}_Base2", (x0 - sign * (T / 2.0 + 0.006), (y0 + y1) / 2.0, 0.08), (0.012, y1 - y0, 0.16), wall_pal["baseboard"])
    make_box("Foyer_Header", (0.0, 1.90, 2.38), (2.60 + T, T, 0.44), wall)
    make_box("Foyer_Header_Casing", (0.0, 1.90 - T / 2.0 - 0.01, 2.16), (2.60 + T + 0.16, 0.02, 0.10), wood)
    make_box("Foyer_Header_Casing_N", (0.0, 1.90 + T / 2.0 + 0.01, 2.16), (2.60 + T + 0.16, 0.02, 0.10), wood)
    for sx in (-1.30, 1.30):
        make_box(f"Foyer_Post_Casing_{sx:+.1f}", (sx, 1.90 + T / 2.0 + 0.01, 1.08), (T + 0.16, 0.02, 2.16), wood)   # on the kitchen side of each post
        make_box(f"Foyer_Post_Casing_S_{sx:+.1f}", (sx + (0.0), 1.90 - T / 2.0 - 0.01, 1.08), (T + 0.16, 0.02, 2.16), wood)   # the foyer side
    # the living room's cased opening at y 3.4: header, the post at the east end
    make_box("Living_Header", (-2.60, 3.40, 2.38), (2.60 + T, T, 0.44), wall)
    make_box("Living_Header_Casing_N", (-2.60, 3.40 + T / 2.0 + 0.01, 2.16), (2.60 + T, 0.02, 0.10), wood)
    make_box("Living_Header_Casing_S", (-2.60, 3.40 - T / 2.0 - 0.01, 2.16), (2.60 + T, 0.02, 0.10), wood)
    make_box("Living_Post_Casing_E", (-1.30 + T / 2.0 + 0.01, 3.40, 1.08), (0.02, T + 0.16, 2.16), wood)
    make_box("Living_Post_Casing_W", (-1.30 - T / 2.0 - 0.01, 3.40, 1.08), (0.02, T + 0.16, 2.16), wood)

    # ── FOYER ───────────────────────────────────────────────────────
    make_box("Door_Mat", (0.0, 0.52, 0.01), (1.20, 0.70, 0.02), (0.40, 0.34, 0.26, 1.0))
    make_box("Door_Mat_Border", (0.0, 0.52, 0.021), (1.12, 0.62, 0.002), (0.48, 0.42, 0.32, 1.0))
    # a bench on the east wall with the coats on hooks over it
    make_bench("Foyer_Bench", 1.03, 1.00, length=0.90, yaw=1.5708, wood=wood, h=0.44)
    make_box("Foyer_Bench_Cushion", (1.03, 1.00, 0.47), (0.32, 0.86, 0.05), (0.52, 0.46, 0.40, 1.0))
    make_box("Coat_Rail", (1.215, 1.00, 1.80), (0.03, 0.90, 0.06), wood)
    for i, (hy, col, hang) in enumerate(((0.70, (0.30, 0.34, 0.40, 1.0), 0.78), (1.00, (0.56, 0.44, 0.30, 1.0), 0.70), (1.30, (0.38, 0.42, 0.34, 1.0), 0.60))):
        make_cyl(f"Coat_Hook_{i}", (1.20, hy, 1.80), 0.010, 0.05, steel, segments=6, axis='X')
        make_chamfer_box(f"Coat_{i}", (1.12, hy, 1.78 - hang / 2.0), (0.14, 0.26, hang), col, chamfer=0.03)
        make_chamfer_box(f"Coat_{i}_Collar", (1.11, hy, 1.76), (0.16, 0.28, 0.06), (col[0] * 0.85, col[1] * 0.85, col[2] * 0.85, 1.0), chamfer=0.02)
    make_cyl("Umbrella", (1.14, 1.72, 0.42), 0.025, 0.84, (0.20, 0.22, 0.30, 1.0), segments=8)
    make_cyl("Umbrella_Handle", (1.14, 1.72, 0.86), 0.012, 0.10, wood, segments=6, axis='Y')
    # the mirror over the hall table, a small photo beside the door
    _wall_frame("Foyer_Mirror", (-1.24, 1.00), 1.55, 0.44, 0.60, "+X", (0.78, 0.82, 0.84, 1.0), frame=COL_FRAME_GOLD, depth=0.03)
    _wall_frame("Foyer_Photo", (-1.24, 1.62), 1.45, 0.18, 0.22, "+X", PHOTO_TINTS[0], mat=cream)
    _wall_frame("Foyer_Photo_E", (1.24, 1.68), 1.50, 0.20, 0.16, "-X", PHOTO_TINTS[3], mat=cream)
    make_light_switch("Foyer_Switch", (1.32, 0.0), axis='X', face_sign=+1)   # on the shell's south wall, east of the door
    make_cyl("Foyer_Ceiling_Light", (0.0, 1.0, CEIL_Z - 0.06), 0.12, 0.10, (0.94, 0.88, 0.70, 1.0), segments=12)

    # ── LIVING ROOM ─────────────────────────────────────────────────
    # the paint: dusty sage panels on the room's three solid walls (the
    # window cut out of the south one)
    make_box("Living_Panel_W", (-3.895, 1.75, 1.30), (0.01, 3.30, 2.28), COL_LIVING_PAINT)
    make_box("Living_Panel_E", (-1.30 - T / 2.0 - 0.005, 2.65, 1.30), (0.01, 1.50, 2.28), COL_LIVING_PAINT)
    make_box("Living_Panel_E_F", (-1.30 - T / 2.0 - 0.005, 1.00, 1.30), (0.01, 1.80, 2.28), COL_LIVING_PAINT)
    make_box("Living_Panel_S_W", (-3.75, 0.105, 1.30), (0.30, 0.01, 2.28), COL_LIVING_PAINT)
    make_box("Living_Panel_S_E", (-1.80, 0.105, 1.30), (0.88, 0.01, 2.28), COL_LIVING_PAINT)
    make_box("Living_Panel_S_Over", (-2.80, 0.105, 2.33), (1.60, 0.01, 0.22), COL_LIVING_PAINT)
    make_box("Living_Panel_S_Under", (-2.80, 0.105, 0.60), (1.60, 0.01, 0.88), COL_LIVING_PAINT)
    # the window over the sofa (south wall, built toward the room)
    make_window("Window_Living", (-2.80, 0.10, 1.58), width=1.40, height=1.00, room_dir=+1)
    make_box("Window_Living_Sill", (-2.80, 0.17, 1.06), (1.54, 0.14, 0.04), wood)
    make_box("Window_Living_Curtain_W", (-3.56, 0.16, 1.60), (0.22, 0.03, 1.30), COL_CURTAIN_SAGE)
    make_box("Window_Living_Curtain_E", (-2.04, 0.16, 1.60), (0.22, 0.03, 1.30), COL_CURTAIN_SAGE)
    # the rug
    make_box("Living_Rug", (-2.65, 1.75, 0.006), (2.30, 2.10, 0.012), rug_col)
    make_box("Living_Rug_Border", (-2.65, 1.75, 0.013), (2.10, 1.90, 0.002), rug_edge)
    make_box("Living_Rug_Field", (-2.65, 1.75, 0.0145), (1.90, 1.70, 0.002), rug_col)
    # THE SOFA: a secondhand three-seater against the south wall, its
    # back under the window; two seat cushions, three back cushions, a
    # quilt over one arm, a throw pillow
    sx, sy = -2.75, 0.62
    make_box("Sofa_Base", (sx, sy, 0.20), (1.90, 0.88, 0.40), sofa_col)
    make_box("Sofa_Back", (sx, sy - 0.36, 0.62), (1.90, 0.16, 0.44), sofa_col)
    for i, cx in enumerate((-0.62, 0.0, 0.62)):
        make_chamfer_box(f"Sofa_BackCushion_{i}", (sx + cx, sy - 0.24, 0.62), (0.58, 0.10, 0.40), (sofa_col[0] * 1.08, sofa_col[1] * 1.08, sofa_col[2] * 1.06, 1.0), chamfer=0.03)
    for i, cx in enumerate((-0.46, 0.46)):
        make_chamfer_box(f"Sofa_SeatCushion_{i}", (sx + cx, sy + 0.06, 0.46), (0.86, 0.58, 0.12), (sofa_col[0] * 1.05, sofa_col[1] * 1.05, sofa_col[2] * 1.05, 1.0), chamfer=0.03)
    for i, ax in enumerate((-0.98, 0.98)):
        make_chamfer_box(f"Sofa_Arm_{i}", (sx + ax, sy, 0.44), (0.14, 0.88, 0.48), sofa_col, chamfer=0.03)
    make_chamfer_box("Sofa_Quilt", (sx + 0.98, sy + 0.02, 0.72), (0.26, 0.70, 0.10), quilt, chamfer=0.03)
    make_box("Sofa_Quilt_Drape", (sx + 1.10, sy + 0.02, 0.50), (0.04, 0.60, 0.40), quilt)
    for i in range(4):
        make_box(f"Sofa_Quilt_Stripe_{i}", (sx + 0.98, sy - 0.26 + i * 0.18, 0.775), (0.26, 0.04, 0.002), (0.84, 0.78, 0.62, 1.0))
    make_chamfer_box("Throw_Pillow", (sx - 0.70, sy - 0.08, 0.60), (0.36, 0.14, 0.36), (0.82, 0.70, 0.46, 1.0), chamfer=0.04)
    # THE COFFEE TABLE: books stacked, a mug, a candle, her reading glasses
    make_table("Coffee_Table", -2.65, 1.75, w=0.96, d=0.52, h=0.42, wood=(0.38, 0.28, 0.18, 1.0))
    for i, (bw, bd, bh, col) in enumerate(((0.26, 0.20, 0.03, BOOK_TINTS[1]), (0.24, 0.18, 0.025, BOOK_TINTS[3]), (0.22, 0.17, 0.035, BOOK_TINTS[8]))):
        make_box(f"Coffee_Book_{i}", (-2.84, 1.70, 0.425 + sum((0.03, 0.025, 0.035)[:i]) + bh / 2.0), (bw, bd, bh), col)
    make_mug("Coffee_Table_Mug", -2.44, 1.86, 0.425, (0.30, 0.34, 0.42, 1.0))
    make_cyl("Candle_Jar", (-2.46, 1.62, 0.455), 0.04, 0.06, (0.86, 0.82, 0.70, 1.0), segments=10)
    make_box("Reading_Glasses", (-2.62, 1.92, 0.43), (0.12, 0.04, 0.008), (0.26, 0.22, 0.20, 1.0))
    # THE ARMCHAIR west of the TV, facing it
    ax, ay = -2.62, 2.75   # (its back clipped the loom's upright at -2.75)
    make_box("Armchair_Base", (ax, ay, 0.22), (0.74, 0.76, 0.44), chair_col)
    make_chamfer_box("Armchair_Seat", (ax + 0.04, ay, 0.47), (0.52, 0.58, 0.10), (chair_col[0] * 1.06, chair_col[1] * 1.06, chair_col[2] * 1.06, 1.0), chamfer=0.03)
    make_chamfer_box("Armchair_Back", (ax - 0.30, ay, 0.70), (0.14, 0.76, 0.52), chair_col, chamfer=0.03)
    for i, oy in enumerate((-0.33, 0.33)):
        make_chamfer_box(f"Armchair_Arm_{i}", (ax + 0.02, ay + oy, 0.48), (0.66, 0.10, 0.52), chair_col, chamfer=0.03)
    make_chamfer_box("Armchair_Throw", (ax - 0.30, ay - 0.10, 0.98), (0.20, 0.44, 0.05), COL_CURTAIN_SAGE, chamfer=0.02)
    # THE BOOKCASE on the west wall: five shelves of books, with the
    # collection in among them — a framed photo, the shells, pinecones,
    # a ceramic bowl, a jar of sea glass
    bx, by = -3.75, 1.55
    tops = _bookcase("Bookcase", bx, by, w=1.20, d=0.30, h=2.00, shelves=5, wood=(0.40, 0.30, 0.20, 1.0), back_x_sign=-1)
    y0 = by - 0.56
    for i, zt in enumerate(tops):
        if i == 0:
            run = _book_row(f"Books_{i}", bx, y0, zt, 14, along='Y', depth=0.24, seed=3)
            make_box("Shelf0_Magazines", (bx, y0 + run + 0.22, zt + 0.12), (0.26, 0.40, 0.24), (0.80, 0.78, 0.70, 1.0))
        elif i == 1:
            run = _book_row(f"Books_{i}", bx, y0, zt, 9, along='Y', depth=0.22, seed=7)
            _wall_frame("Shelf_Photo", (bx - 0.12, y0 + run + 0.30), zt + 0.09, 0.22, 0.18, "+X", PHOTO_TINTS[2], mat=cream)   # standing on the shelf
            make_cyl("Shelf_Candle", (bx + 0.04, y0 + run + 0.52, zt + 0.04), 0.03, 0.08, (0.88, 0.82, 0.66, 1.0), segments=8)
        elif i == 2:
            # the collection: shells and the sea glass jar, driftwood
            for k, (oy, r, col) in enumerate(((0.10, 0.045, (0.86, 0.80, 0.70, 1.0)), (0.22, 0.035, (0.78, 0.70, 0.62, 1.0)), (0.32, 0.05, (0.90, 0.86, 0.78, 1.0)))):
                make_dome(f"Shell_{k}", (bx + 0.02, y0 + oy, zt), r, col, rings=3, segments=8)
            make_jar("Sea_Glass_Jar", bx + 0.02, y0 + 0.50, zt, (0.62, 0.80, 0.76, 0.6), h=0.14, r=0.05)
            make_cyl("Shelf_Driftwood", (bx + 0.0, y0 + 0.80, zt + 0.03), 0.03, 0.34, (0.62, 0.55, 0.44, 1.0), segments=7, axis='Y')
            run = _book_row(f"Books_{i}", bx, y0 + 0.98, zt, 4, along='Y', depth=0.20, seed=11)
        elif i == 3:
            run = _book_row(f"Books_{i}", bx, y0, zt, 12, along='Y', depth=0.22, seed=5)
            make_bowl("Shelf_Bowl", bx + 0.02, y0 + run + 0.16, zt, (0.46, 0.56, 0.52, 1.0), r=0.09, h=0.06)
        else:
            run = _book_row(f"Books_{i}", bx, y0 + 0.14, zt, 10, along='Y', depth=0.20, seed=9)
            for k in range(3):
                make_cyl(f"Shelf_Pinecone_{k}", (bx + 0.02, y0 + 0.02 + k * 0.045, zt + 0.025), 0.02, 0.05, (0.40, 0.30, 0.20, 1.0), segments=6)
    # THE GALLERY WALL on the living room's east wall over the TV, and
    # two frames flanking the window over the sofa
    gx = -1.30 - T / 2.0 - 0.01
    for i, (gy, gz, w, h, mat) in enumerate(((2.30, 1.75, 0.30, 0.36, cream), (2.66, 1.62, 0.22, 0.28, None), (2.66, 1.96, 0.22, 0.18, cream),
                                             (2.98, 1.80, 0.26, 0.32, None), (3.22, 1.56, 0.14, 0.18, None))):
        _wall_frame(f"Gallery_{i}", (gx, gy), gz, w, h, "-X", PHOTO_TINTS[i % len(PHOTO_TINTS)], frame=(COL_FRAME_DARK if i % 2 == 0 else COL_FRAME_GOLD), mat=mat)
    _wall_frame("Sofa_Frame_W", (-3.68, 0.115), 1.60, 0.30, 0.40, "+Y", PHOTO_TINTS[4], mat=cream)
    _wall_frame("Sofa_Frame_E", (-1.86, 0.115), 1.60, 0.34, 0.26, "+Y", PHOTO_TINTS[1])
    # the floor lamp in the south-east corner, beside the sofa
    lx, ly = -1.62, 0.50
    make_cyl("Floor_Lamp_Base", (lx, ly, 0.015), 0.14, 0.03, P.METAL_BLACK, segments=12)
    make_cyl("Floor_Lamp_Pole", (lx, ly, 0.78), 0.012, 1.50, (0.56, 0.48, 0.30, 1.0), segments=8)
    make_taper_cyl("Floor_Lamp_Shade", (lx, ly, 1.68), 0.20, 0.13, 0.26, (0.92, 0.86, 0.68, 1.0), segments=12)
    make_lathe("Floor_Lamp_Bulb", (lx, ly, 1.62), [(0.0, 0.0), (0.025, 0.01), (0.03, 0.04), (0.0, 0.07)], (0.98, 0.94, 0.80, 1.0), segments=8)
    # a side table by the armchair with the radio's cousin: a lamp and a photo
    make_table("Side_Table", -2.05, 3.17, w=0.40, d=0.40, h=0.56, wood=(0.38, 0.28, 0.18, 1.0))
    make_lamp("Side_Lamp", -2.05, 3.17, base_z=0.565, h=0.42)
    _wall_frame("Side_Photo", (-1.93, 3.33), 0.66, 0.12, 0.14, "-X", PHOTO_TINTS[5], frame=COL_FRAME_GOLD)

    # ── DINING ROOM ─────────────────────────────────────────────────
    # beadboard wainscot with a chair rail on its three walls
    ex = ROOM_W / 2.0 - 0.105
    make_box("Dining_Wainscot_E", (ex, 2.20, 0.56), (0.01, 4.00, 0.80), COL_DINING_WAINSCOT)
    make_box("Dining_Rail_E", (ex - 0.015, 2.20, 0.97), (0.04, 4.00, 0.03), wood)
    make_box("Dining_Wainscot_S", (2.75, 0.105, 0.56), (2.30, 0.01, 0.80), COL_DINING_WAINSCOT)
    make_box("Dining_Rail_S", (2.75, 0.125, 0.97), (2.30, 0.04, 0.03), wood)
    fx = 1.30 + T / 2.0 + 0.005
    make_box("Dining_Wainscot_W", (fx, 1.00, 0.56), (0.01, 1.80, 0.80), COL_DINING_WAINSCOT)
    make_box("Dining_Rail_W", (fx + 0.015, 1.00, 0.97), (0.04, 1.80, 0.03), wood)
    for i in range(1, 46):
        make_box(f"Beadboard_E_{i}", (ex + 0.004, 0.20 + i * 0.087, 0.56), (0.004, 0.006, 0.78), (0.82, 0.80, 0.72, 1.0))
    # the rug under the table, the pendant over it
    make_box("Dining_Rug", (2.55, 1.95, 0.006), (2.30, 1.80, 0.012), (0.36, 0.40, 0.44, 1.0))
    make_box("Dining_Rug_Border", (2.55, 1.95, 0.013), (2.10, 1.60, 0.002), (0.62, 0.58, 0.46, 1.0))
    make_box("Dining_Rug_Field", (2.55, 1.95, 0.0145), (1.90, 1.40, 0.002), (0.36, 0.40, 0.44, 1.0))
    make_pendant("Dining_Pendant", 2.55, 1.95, bulb_z=1.80, ceil_z=CEIL_Z, shade_col=(0.80, 0.60, 0.34, 1.0), shade_r=0.20)
    # THE HUTCH on the east wall: base cabinet, counter, open upper
    # shelves with the plates standing, the preserves, the teapot
    hx, hy = ROOM_W / 2.0 - 0.36, 1.60
    hwood = (0.46, 0.34, 0.22, 1.0)
    make_box("Hutch_Base", (hx, hy, 0.44), (0.50, 1.20, 0.88), hwood)
    for i, oy in enumerate((-0.29, 0.29)):
        make_box(f"Hutch_Door_{i}", (hx - 0.26, hy + oy, 0.42), (0.02, 0.52, 0.70), (0.52, 0.40, 0.26, 1.0))
        make_cyl(f"Hutch_Knob_{i}", (hx - 0.28, hy + oy - 0.18 * (1 if i == 0 else -1), 0.50), 0.012, 0.02, steel, segments=6, axis='X')
    make_box("Hutch_Counter", (hx - 0.02, hy, 0.90), (0.54, 1.26, 0.04), hwood)
    make_box("Hutch_Upper_Back", (hx + 0.22, hy, 1.52), (0.02, 1.20, 1.20), (0.40, 0.30, 0.20, 1.0))
    for i, oy in enumerate((-0.59, 0.59)):
        make_box(f"Hutch_Upper_Side_{i}", (hx + 0.06, hy + oy, 1.52), (0.34, 0.02, 1.20), hwood)
    make_box("Hutch_Upper_Top", (hx + 0.06, hy, 2.11), (0.34, 1.20, 0.02), hwood)
    make_box("Hutch_Cornice", (hx + 0.04, hy, 2.15), (0.40, 1.26, 0.06), hwood)
    for i, z in enumerate((1.26, 1.62)):
        make_box(f"Hutch_Shelf_{i}", (hx + 0.06, hy, z), (0.32, 1.16, 0.02), hwood)
        make_box(f"Hutch_Shelf_{i}_Lip", (hx - 0.08, hy, z + 0.02), (0.01, 1.16, 0.02), hwood)
    # plates standing on the lower shelf, against the back
    for i, oy in enumerate((-0.40, -0.20, 0.0, 0.20, 0.40)):
        make_cyl(f"Hutch_Plate_{i}", (hx + 0.18, hy + oy, 1.27 + 0.11), 0.11, 0.008, [cream, (0.72, 0.78, 0.74, 1.0), cream, (0.84, 0.72, 0.60, 1.0), cream][i], segments=14, axis='X')
    # preserves on the upper shelf: jars of three colours, labelled
    for i, (oy, col, h) in enumerate(((-0.46, (0.52, 0.14, 0.18, 0.95), 0.14), (-0.34, (0.70, 0.40, 0.14, 0.95), 0.14), (-0.22, (0.52, 0.14, 0.18, 0.95), 0.12),
                                      (-0.10, (0.30, 0.46, 0.22, 0.95), 0.14), (0.02, (0.70, 0.40, 0.14, 0.95), 0.12), (0.14, (0.52, 0.14, 0.18, 0.95), 0.14))):
        make_jar(f"Preserve_{i}", hx + 0.06, hy + oy, 1.63, col, h=h, r=0.04)
        make_box(f"Preserve_{i}_Label", (hx - 0.04 + 0.06, hy + oy, 1.63 + h * 0.45), (0.002, 0.05, 0.03), cream)
    make_lathe("Teapot", (hx + 0.06, hy + 0.40, 1.63), [(0.0, 0.0), (0.07, 0.0), (0.09, 0.05), (0.08, 0.10), (0.04, 0.13), (0.045, 0.15), (0.0, 0.15)], (0.42, 0.50, 0.56, 1.0), segments=12)
    make_cyl("Teapot_Spout", (hx + 0.06, hy + 0.50, 1.72), 0.012, 0.08, (0.42, 0.50, 0.56, 1.0), segments=6, axis='Y')
    make_bowl("Hutch_Bowl_Stack", hx + 0.02, hy - 0.42, 0.92, (0.72, 0.78, 0.74, 1.0), r=0.10, h=0.07)
    _wall_frame("Hutch_Photo", (hx - 0.11, hy + 0.36), 0.98, 0.14, 0.12, "-X", PHOTO_TINTS[0], frame=COL_FRAME_GOLD)   # standing on the counter (0.92)
    # THE SIDEBOARD under the front window: the photographs, the garden's
    # flowers in a jar, a bowl of fruit
    sbx, sby = 2.00, 0.38
    make_box("Sideboard_Body", (sbx, sby, 0.36), (1.20, 0.44, 0.72), (0.38, 0.28, 0.18, 1.0))
    make_box("Sideboard_Top", (sbx, sby, 0.73), (1.26, 0.48, 0.03), (0.44, 0.32, 0.20, 1.0))
    for i, ox in enumerate((-0.30, 0.30)):
        make_box(f"Sideboard_Door_{i}", (sbx + ox, sby + 0.225, 0.34), (0.54, 0.02, 0.56), (0.46, 0.34, 0.22, 1.0))
        make_cyl(f"Sideboard_Knob_{i}", (sbx + ox + (0.20 if i == 0 else -0.20), sby + 0.245, 0.40), 0.012, 0.02, steel, segments=6, axis='Y')
    for i, (ox, w, h) in enumerate(((-0.46, 0.14, 0.18), (-0.28, 0.18, 0.14), (0.48, 0.16, 0.20))):
        make_box(f"Sideboard_Frame_{i}", (sbx + ox, sby - 0.06, 0.745 + h / 2.0), (w, 0.02, h), COL_FRAME_DARK if i != 1 else COL_FRAME_GOLD)
        make_box(f"Sideboard_Frame_{i}_Pic", (sbx + ox, sby - 0.072, 0.745 + h / 2.0), (w - 0.03, 0.002, h - 0.03), PHOTO_TINTS[(i + 2) % 6])
        make_box(f"Sideboard_Frame_{i}_Strut", (sbx + ox, sby + 0.02, 0.745 + h / 4.0), (0.02, 0.12, h / 2.0), COL_FRAME_DARK)
    make_jar("Flower_Jar", sbx + 0.08, sby + 0.02, 0.745, (0.72, 0.80, 0.78, 0.6), h=0.16, r=0.05)
    for i, (ox, oy, col) in enumerate(((0.0, 0.0, (0.88, 0.72, 0.30, 1.0)), (0.06, 0.04, (0.84, 0.40, 0.44, 1.0)), (-0.05, 0.03, (0.92, 0.88, 0.70, 1.0)), (0.02, -0.05, (0.84, 0.40, 0.44, 1.0)))):
        make_cyl(f"Flower_Stem_{i}", (sbx + 0.08 + ox * 0.5, sby + 0.02 + oy * 0.5, 0.86), 0.004, 0.22, (0.34, 0.50, 0.26, 1.0), segments=5)
        make_dome(f"Flower_{i}", (sbx + 0.08 + ox, sby + 0.02 + oy, 0.96), 0.03, col, rings=3, segments=8)
    make_bowl("Fruit_Bowl", sbx + 0.26, sby + 0.0, 0.745, (0.46, 0.56, 0.52, 1.0), r=0.11, h=0.06)
    for i, (ox, oy, col) in enumerate(((0.0, 0.0, (0.86, 0.30, 0.20, 1.0)), (0.07, 0.03, (0.90, 0.72, 0.26, 1.0)), (-0.05, 0.05, (0.60, 0.70, 0.30, 1.0)))):
        make_dome(f"Fruit_{i}", (sbx + 0.26 + ox, sby + oy, 0.80), 0.035, col, rings=3, segments=8)
    # cookbooks and photos on the foyer wall's dining face: a shelf unit
    cbx, cby = 1.30 + T / 2.0 + 0.16, 1.00
    tops = _bookcase("Cookbooks", cbx, cby, w=1.00, d=0.30, h=1.30, shelves=3, wood=(0.44, 0.32, 0.20, 1.0), back_x_sign=-1)
    for i, zt in enumerate(tops):
        n = (12, 8, 10)[i]
        run = _book_row(f"Cookbook_{i}", cbx, cby - 0.46, zt, n, along='Y', depth=0.24, seed=13 + i)
        if i == 1:
            make_cyl("Cookbook_Shelf_Jar", (cbx + 0.02, cby - 0.46 + run + 0.12, zt + 0.06), 0.045, 0.12, (0.80, 0.84, 0.82, 0.6), segments=10)
            make_cyl("Cookbook_Shelf_Jar_Lid", (cbx + 0.02, cby - 0.46 + run + 0.12, zt + 0.125), 0.047, 0.01, (0.52, 0.42, 0.30, 1.0), segments=10)
    _wall_frame("Dining_Photo_0", (fx, 0.75), 1.70, 0.30, 0.24, "+X", PHOTO_TINTS[1], mat=cream)
    _wall_frame("Dining_Photo_1", (fx, 1.20), 1.72, 0.24, 0.30, "+X", PHOTO_TINTS[4], frame=COL_FRAME_GOLD)
    _wall_frame("Dining_Photo_2", (fx, 1.55), 1.62, 0.16, 0.20, "+X", PHOTO_TINTS[2])
    # a spice shelf on the backsplash under the east uppers
    make_box("Spice_Shelf", (1.00, ROOM_D - 0.10 - 0.08, 1.32), (0.60, 0.12, 0.02), wood)
    for i in range(6):
        make_cyl(f"Spice_{i}", (0.78 + i * 0.09, ROOM_D - 0.10 - 0.08, 1.33 + 0.05), 0.022, 0.10, [(0.62, 0.40, 0.18, 1.0), (0.46, 0.52, 0.30, 1.0), (0.70, 0.26, 0.18, 1.0), (0.80, 0.70, 0.40, 1.0), (0.40, 0.30, 0.22, 1.0), (0.66, 0.56, 0.26, 1.0)][i], segments=8)


def main():
    clear_scene()
    build_shell()
    build_kitchen_island()
    build_north_appliances()
    build_kitchen_table_chairs()
    build_living_room_tv_corner()
    build_decor()
    build_ceiling_infra()
    out_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/roberts_kitchen.glb"))
    print(f"\n[build_roberts_kitchen] exporting to {out_path}")
    build_hero_props()
    build_detail_pass_2026_08()
    build_kitchen_bones_2026_10()
    build_front_door_porch_2026_10()
    build_proof_of_life_2026_10()
    build_house_rooms_2026_10()
    export_glb(out_path)


if __name__ == "__main__":
    main()
