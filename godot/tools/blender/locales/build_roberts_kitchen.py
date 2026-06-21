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
    make_wall("Wall_S_W", (-2.75, 0.0, 0),
              length=2.50, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL)
    make_wall("Wall_S_E", (+2.75, 0.0, 0),
              length=2.50, height=CEIL_Z, axis='X',
              palette=PAL_DOMESTIC_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (2.20, 0.20, 0.60), PAL_DOMESTIC_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL_Z),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4)
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
    make_window("Window_SE", (+2.00, 0.0, 1.40),
                width=1.40, height=1.20)
    # Back-yard window (east wall, faces sage curtains)
    make_box("Window_E_Frame", (ROOM_W / 2.0 - 0.04, 3.5, 1.55),
             (0.04, 1.80, 1.20), P.METAL_STEEL)
    make_box("Window_E_Glass", (ROOM_W / 2.0 - 0.06, 3.5, 1.55),
             (0.005, 1.70, 1.10), P.GLASS)
    make_box("Window_E_Curtain", (ROOM_W / 2.0 - 0.10, 3.5, 1.55),
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
        make_cyl(f"Stool_{si}_Post", (sx, 1.80, 0.37),
                 0.025, 0.70, P.METAL_BLACK)
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
    make_cyl("Sink_Faucet", (-2.0, 5.40, 1.00),
             0.015, 0.30, P.METAL_STEEL)
    make_box("Sink_Faucet_Spout", (-2.0, 5.50, 1.14),
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
                 (+2.0 + mx_off, 5.06, 1.60 + my_off),
                 (0.05, 0.005, 0.08), tint)


def build_kitchen_table_chairs():
    # Small breakfast table near east wall
    tx, ty = +2.5, 1.5
    make_box("Table_Top", (tx, ty, 0.72),
             (0.80, 0.80, 0.04), COL_WOOD_TRIM)
    for li, (lx, ly) in enumerate([
            (tx - 0.34, ty - 0.34), (tx + 0.34, ty - 0.34),
            (tx - 0.34, ty + 0.34), (tx + 0.34, ty + 0.34)]):
        make_box(f"Table_Leg_{li}", (lx, ly, 0.36),
                 (0.04, 0.04, 0.72), COL_WOOD_TRIM)
    # Two chairs
    for ci, (cx, cy) in enumerate([
            (tx - 0.50, ty - 0.50), (tx + 0.50, ty + 0.50)]):
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.46),
                 (0.42, 0.42, 0.04), COL_WOOD_TRIM)
        make_box(f"Chair_{ci}_Back", (cx, cy + (0.22 if ci == 0 else -0.22), 0.74),
                 (0.42, 0.04, 0.56), COL_WOOD_TRIM)
        for li in range(4):
            lxc = cx - 0.18 + (li % 2) * 0.36
            lyc = cy - 0.18 + (li // 2) * 0.36
            make_box(f"Chair_{ci}_Leg_{li}", (lxc, lyc, 0.23),
                     (0.03, 0.03, 0.46), COL_WOOD_TRIM)


def build_living_room_tv_corner():
    # CRT TV in the south-east corner — the Anya tape lands here
    # (Elicia at the Roberts cameo). Top of the case at z=0.66.
    tx, ty = +3.20, 0.80
    make_box("TV_Case", (tx, ty, 0.40),
             (0.60, 0.50, 0.50), COL_TV_CASE)
    make_box("TV_Screen", (tx, ty - 0.26, 0.46),
             (0.40, 0.005, 0.30), COL_TV_SCREEN)
    make_box("TV_Stand", (tx, ty, 0.16),
             (0.60, 0.50, 0.04), COL_WOOD_TRIM)
    # VCR underneath
    make_box("VCR", (tx, ty, 0.10),
             (0.50, 0.40, 0.10), P.METAL_BLACK)
    # Cassette half-ejected
    make_box("VCR_Tape", (tx, ty - 0.20, 0.14),
             (0.16, 0.10, 0.02), COL_TV_CASE)


def build_decor():
    make_wall_clock("Clock", (-3.95, 4.0, 2.10),
                    frozen_hour=8, frozen_min=15)
    make_calendar("Calendar", (-3.95, 1.5, 1.60))
    make_faded_poster("Poster", (3.95, 2.5, 1.70))
    make_floor_plant("Plant", (-3.0, 1.0, 0.0),
                     palette={"leaf": COL_CURTAIN_SAGE,
                              "pot": COL_WOOD_TRIM})
    # Door hinges
    make_door_hinges("FrontDoor_Hinge", edge_x=-1.10, edge_y=0.0,
                     edge_z_centers=[0.30, 1.05, 1.80], axis='X')


def build_ceiling_infra():
    for j, ypos in enumerate([2.0, 4.5]):
        make_fluorescent_tube_fixture(
            f"Fluor_{j}", (0.0, ypos, CEIL_Z),
            length=1.60, width=0.40)
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL_Z))
    make_hvac_vent("HVAC", (-1.0, 5.5, CEIL_Z), width=0.80, depth=0.40)
    make_ceiling_speaker("Speaker", (1.5, 4.0, CEIL_Z))


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
    export_glb(out_path)


if __name__ == "__main__":
    main()
