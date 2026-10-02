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

from _props.furniture import make_table, make_chair
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (
    make_floor, make_wall, make_ceiling, make_window,
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
                           make_threshold)
from _props.vehicles import make_car
from _props.objects import make_mug, make_bottle, make_jar, make_plate
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


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_LINOLEUM, "seam": COL_LINOLEUM_SEAM})
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0),
              length=ROOM_W + 0.4, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.55, 0.0, 0),   # to the header's edge (2026-09-22: 40 cm short)
              length=2.90, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+2.55, 0.0, 0),
              length=2.90, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL, baseboard_face_sign=+1)
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
    make_box("Window_E_Frame", (ROOM_W / 2.0 - 0.12, 3.5, 1.55),
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
    make_box("Sink_Counter", (-2.0, 5.60, 0.90),
             (1.80, 0.70, 0.04), PAL_DOMESTIC_COUNTER["formica"])
    make_box("Sink_Base", (-2.0, 5.60, 0.45),
             (1.80, 0.70, 0.84), PAL_DOMESTIC_COUNTER["kick"])
    make_box("Sink_Bowl", (-2.0, 5.50, 0.86),
             (0.80, 0.50, 0.16), COL_APPLIANCE)
    make_cyl("Sink_Faucet", (-2.0, 5.40, 1.06),
             0.015, 0.28, P.METAL_STEEL)      # rises from the counter top (0.92)
    make_box("Sink_Faucet_Spout", (-2.0, 5.50, 1.18),
             (0.04, 0.20, 0.04), P.METAL_STEEL)
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
    # Small breakfast table near east wall
    tx, ty = +2.5, 1.5
    make_table("Table", tx, ty, w=0.80, d=0.80, h=0.74, wood=COL_WOOD_TRIM)
    # Two chairs (DETAIL DRAFT 4: through the furniture kit)
    for ci, (cx, cy, yaw) in enumerate([(tx - 0.50, ty - 0.50, 3.1416), (tx + 0.50, ty + 0.50, 0.0)]):
        make_chair(f"Chair_{ci}", cx, cy, yaw=yaw, wood=COL_WOOD_TRIM, w=0.42)


def build_living_room_tv_corner():
    # CRT TV in the south-east corner — the Anya tape lands here
    # (Elicia at the Roberts cameo). Top of the case at z=0.66.
    tx, ty = +3.20, 0.80
    make_box("TV_Case", (tx, ty, 0.40),
             (0.60, 0.50, 0.50), COL_TV_CASE)
    make_box("TV_Screen", (tx, ty + 0.26, 0.46),      # faces the room (2026-09-10: it faced the S wall)
             (0.40, 0.005, 0.30), COL_TV_SCREEN)
    make_box("TV_Stand", (tx, ty, 0.12),   # on the VCR, which is on the floor (2026-09-22: 5 cm up)
             (0.60, 0.50, 0.04), COL_WOOD_TRIM)
    # VCR underneath
    make_box("VCR", (tx, ty, 0.05),
             (0.50, 0.40, 0.10), P.METAL_BLACK)
    # Cassette half-ejected
    make_box("VCR_Tape", (tx, ty - 0.20, 0.09),
             (0.16, 0.10, 0.02), COL_TV_CASE)


def build_decor():
    make_wall_clock("Clock", (-3.900, 4.0, 2.10),
                    frozen_hour=8, frozen_min=15, facing='+X')
    make_calendar("Calendar", (-3.95, 1.5, 1.60))
    make_faded_poster("Poster", (3.8965, 2.5, 1.70), into_room=-1)
    make_floor_plant("Plant", (-3.0, 1.0, 0.0),
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
    make_cyl("Sill_Driftwood", (ROOM_W/2.0-0.20, 3.95, 1.00), 0.05, 0.30, (0.62, 0.55, 0.44, 1.0), segments=7, axis='Y')
    # The small table by the door: keys, unopened mail, pinecones,
    # and the Polaroid the scene ends on
    make_box("Hall_Table", (-1.90, 0.55, 0.76), (0.80, 0.40, 0.04), (0.42, 0.30, 0.20, 1.0))
    for lx in (-2.24, -1.56):
        make_box(f"Hall_Table_Leg_{lx:.2f}", (lx, 0.55, 0.38), (0.05, 0.35, 0.74), (0.34, 0.24, 0.15, 1.0))
    make_box("Hall_Keys", (-2.10, 0.48, 0.79), (0.08, 0.05, 0.015), (0.62, 0.64, 0.66, 1.0))
    make_box("Unopened_Mail", (-1.85, 0.60, 0.79), (0.22, 0.14, 0.03), (0.88, 0.86, 0.78, 1.0))
    make_cyl("Pinecone_Bowl", (-1.62, 0.48, 0.80), 0.09, 0.06, (0.52, 0.42, 0.30, 1.0), segments=10)
    make_box("The_Polaroid", (-2.02, 0.62, 0.785), (0.09, 0.11, 0.003), (0.92, 0.90, 0.86, 1.0))
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
    make_traffic_wear("Lane_Entry_Sink", [(0.0, 0.45), (0.0, 1.95), (-2.0, 1.95), (-2.0, 4.9)], width=0.62, tint=worn)
    make_traffic_wear("Lane_Island_Table", [(0.9, 1.95), (2.2, 1.95)], width=0.42, tint=worn)
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
    make_cyl("Sink_Standing_Water", (-2.0, 5.50, 0.945), 0.17, 0.006, (0.52, 0.60, 0.66, 1.0), segments=12)
    make_box("Sink_Drip_Dark", (-2.0, 5.50, 0.948), (0.06, 0.06, 0.003), (0.38, 0.46, 0.52, 1.0))
    # ── dishes drying beside the sink (two of everything), the soap
    make_box("Dish_Rack_Base", (-1.25, 5.62, 0.9275), (0.42, 0.36, 0.015), steel)   # on the counter (0.92)
    for i, px in enumerate((-1.36, -1.26, -1.16)):
        make_cyl(f"Dish_Rack_Plate_{i}", (px, 5.62, 1.052), 0.12, 0.012, cream, segments=12, axis='X')   # standing on the rack
    for i, (gx, gy) in enumerate(((-1.10, 5.50), (-1.40, 5.74))):
        make_cyl(f"Dish_Rack_Glass_{i}", (gx, gy, 0.978), 0.035, 0.09, (0.80, 0.86, 0.88, 1.0), segments=8)
    make_bottle("Dish_Soap", -1.60, 5.78, 0.945, (0.42, 0.66, 0.36, 1.0), h=0.20, r=0.03)
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
    make_box("Newspaper", (2.62, 1.38, 0.745), (0.34, 0.26, 0.01), (0.84, 0.82, 0.76, 1.0))
    make_box("Newspaper_Fold", (2.62, 1.38, 0.752), (0.34, 0.02, 0.012), (0.70, 0.68, 0.62, 1.0))
    make_box("Newspaper_Headline", (2.55, 1.46, 0.752), (0.16, 0.03, 0.004), (0.22, 0.22, 0.24, 1.0))
    make_plate("Toast_Plate", 2.32, 1.66, 0.745, cream, r=0.11)
    make_box("Toast_Crust_0", (2.28, 1.69, 0.76), (0.07, 0.02, 0.012), (0.58, 0.42, 0.22, 1.0))
    make_box("Toast_Crust_1", (2.37, 1.62, 0.76), (0.02, 0.06, 0.012), (0.58, 0.42, 0.22, 1.0))
    make_jar("Jam", 2.68, 1.70, 0.745, (0.52, 0.14, 0.18, 0.95), h=0.10, r=0.04)
    make_cyl("Jam_Lid_Off", (2.80, 1.56, 0.75), 0.042, 0.012, (0.62, 0.58, 0.50, 1.0), segments=10)
    make_box("Butter_Knife", (2.50, 1.78, 0.75), (0.16, 0.018, 0.006), steel)
    # ── Mackenzie's garden came in with her: boots inside the door (a
    #    pair, one tipped), the mud they tracked, gloves and the trowel
    make_box("Boot_L", (-0.62, 0.42, 0.11), (0.11, 0.28, 0.22), (0.26, 0.22, 0.16, 1.0))
    make_box("Boot_R_Tipped", (-0.44, 0.38, 0.07), (0.11, 0.30, 0.14), (0.26, 0.22, 0.16, 1.0))
    make_box("Boot_L_Mud", (-0.62, 0.50, 0.03), (0.12, 0.10, 0.06), (0.34, 0.28, 0.18, 1.0))
    make_floor_stain("Mud_Track_0", (-0.50, 0.70), radius=0.09, tint=(0.52, 0.44, 0.32, 1.0))
    make_floor_stain("Mud_Track_1", (-0.30, 1.00), radius=0.07, tint=(0.52, 0.44, 0.32, 1.0))
    make_box("Garden_Glove_0", (-0.90, 0.36, 0.015), (0.22, 0.11, 0.03), (0.60, 0.52, 0.36, 1.0))
    make_box("Garden_Glove_1", (-0.84, 0.44, 0.04), (0.20, 0.10, 0.03), (0.60, 0.52, 0.36, 1.0))
    make_box("Trowel_Blade", (-1.10, 0.40, 0.012), (0.07, 0.14, 0.012), steel)
    make_cyl("Trowel_Handle", (-1.10, 0.54, 0.02), 0.014, 0.12, (0.52, 0.34, 0.20, 1.0), segments=6, axis='Y')
    # the basil pot on the east sill, between the radio and the driftwood
    bx, by, bz = ROOM_W / 2.0 - 0.20, 3.52, 0.965
    make_cyl("Basil_Pot", (bx, by, bz + 0.07), 0.07, 0.14, (0.72, 0.42, 0.28, 1.0), segments=10)
    make_cyl("Basil_Soil", (bx, by, bz + 0.135), 0.06, 0.01, (0.26, 0.20, 0.14, 1.0), segments=10)
    for i, (lx, ly, lz, lw) in enumerate(((0.0, 0.0, 0.26, 0.10), (-0.05, 0.04, 0.22, 0.08), (0.05, -0.03, 0.23, 0.08), (0.02, 0.05, 0.19, 0.07))):
        make_box(f"Basil_Leaf_{i}", (bx + lx, by + ly, bz + lz), (lw, lw * 0.8, 0.012), (0.34, 0.52, 0.26, 1.0))
    # ── her loom in the west corner: frame, warp, a cloth half woven
    lx0, ly0 = -3.35, 2.45
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
    make_cyl("Laundry_Basket", (-3.35, 3.60, 0.17), 0.26, 0.34, (0.78, 0.74, 0.62, 1.0), segments=10)
    for i in range(3):
        make_box(f"Folded_Towel_{i}", (-3.35, 3.60, 0.37 + i * 0.07), (0.34 - i * 0.02, 0.26, 0.06), [towel, cream, COL_CURTAIN_SAGE][i])
    make_trash_can("Trash", (3.35, 5.25, 0.0), palette={"body": (0.36, 0.38, 0.40, 1.0)}, branded=False)
    make_box("Trash_Crumple_0", (3.05, 4.95, 0.035), (0.08, 0.07, 0.07), (0.88, 0.86, 0.80, 1.0))
    make_box("Trash_Crumple_1", (3.00, 5.08, 0.028), (0.06, 0.06, 0.055), (0.88, 0.86, 0.80, 1.0))
    make_box("Fridge_Grocery_List", (+1.80, 5.072, 1.22), (0.11, 0.004, 0.16), (0.96, 0.95, 0.90, 1.0))
    for i in range(5):
        make_box(f"Fridge_List_Line_{i}", (+1.80, 5.069, 1.27 - i * 0.025), (0.07 - (i % 2) * 0.02, 0.002, 0.004), (0.28, 0.28, 0.32, 1.0))
    make_box("Fridge_Photo", (+2.22, 5.072, 1.26), (0.10, 0.004, 0.08), (0.86, 0.80, 0.70, 1.0))


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
    export_glb(out_path)


if __name__ == "__main__":
    main()
