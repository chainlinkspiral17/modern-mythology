"""VOL 5 · Natalie's Apartment — Empress chapter (vol5_ch3).

PLACEMENT SCRIPT (uses _props/* library).

Canon: Natalie's small one-bedroom in San Francisco. Empress beat:
where John and Natalie made the choice. Used in 3 vol5 scenes
across chapters 3 + Empress cameos.

Footprint:
  Interior X ∈ [-3.5, +3.5], Y ∈ [0, +5.5], ceiling Z=2.60
  Front door south centre
  Living-area south half (sofa, coffee table, bookshelf)
  Kitchenette north-west (counter, sink, fridge)
  Bed nook north-east, low partition wall
  Tall window west wall — afternoon sun

Run:
    blender --background --python build_natalie_apartment.py

Output:
    godot/assets/3d/locales/natalie_apartment.glb
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
from _props.food_service import make_coffee_pots
from _props.decor import (
    make_wall_clock, make_floor_plant, make_faded_poster,
)
from _props.safety import (
    make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture,
)


# Natalie's apartment palette — soft cream walls, warm wood floor,
# muted rose accents (her signature color), dusty teal couch.
PAL_APT_WALL = {
    "wall":      (0.92, 0.88, 0.82, 1.0),    # warm cream
    "baseboard": (0.62, 0.46, 0.30, 1.0),
}
PAL_APT_COUNTER = {
    "formica": (0.86, 0.78, 0.62, 1.0),       # honey laminate
    "top":     (0.32, 0.22, 0.16, 1.0),       # dark walnut
    "kick":    (0.32, 0.22, 0.16, 1.0),
}
COL_FLOOR_OAK     = (0.74, 0.58, 0.38, 1.0)
COL_FLOOR_OAK_SM  = (0.42, 0.30, 0.18, 1.0)
COL_COUCH_TEAL    = (0.42, 0.56, 0.58, 1.0)
COL_COUCH_TRIM    = (0.28, 0.38, 0.42, 1.0)
COL_ACCENT_ROSE   = (0.86, 0.62, 0.62, 1.0)
COL_WOOD_TRIM     = (0.46, 0.34, 0.22, 1.0)
COL_BED_LINEN     = (0.92, 0.86, 0.78, 1.0)
COL_BED_FRAME     = (0.36, 0.28, 0.20, 1.0)
COL_BOOK_SPINES   = [
    (0.62, 0.32, 0.30, 1.0),
    (0.42, 0.52, 0.62, 1.0),
    (0.56, 0.48, 0.32, 1.0),
    (0.32, 0.42, 0.32, 1.0),
    (0.74, 0.58, 0.30, 1.0),
    (0.42, 0.32, 0.42, 1.0),
]

ROOM_W = 7.0
ROOM_D = 5.5
CEIL_Z = 2.60


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR_OAK, "seam": COL_FLOOR_OAK_SM})
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_APT_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0),
              length=ROOM_D + 0.4, height=CEIL_Z, axis='Y',
              palette=PAL_APT_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0),
              length=ROOM_W + 0.4, height=CEIL_Z, axis='X',
              palette=PAL_APT_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.50, 0.0, 0),
              length=2.00, height=CEIL_Z, axis='X',
              palette=PAL_APT_WALL)
    make_wall("Wall_S_E", (+2.50, 0.0, 0),
              length=2.00, height=CEIL_Z, axis='X',
              palette=PAL_APT_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL_Z - 0.30),
             (3.00, 0.20, 0.60), PAL_APT_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL_Z),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy,
                           length=length, axis=ax, ceil_z=CEIL_Z,
                           palette={"wood": COL_WOOD_TRIM})
    # Tall west window (afternoon sun)
    make_box("Window_W_Frame", (-ROOM_W / 2.0 + 0.04, 2.5, 1.45),
             (0.04, 1.80, 1.80), P.METAL_STEEL)
    make_box("Window_W_Glass", (-ROOM_W / 2.0 + 0.06, 2.5, 1.45),
             (0.005, 1.70, 1.70), P.GLASS_WARM)
    # South window beside door
    make_window("Window_SE", (+2.00, 0.0, 1.40),
                width=1.40, height=1.20)
    # Door hinges
    make_door_hinges("FrontDoor_Hinge", edge_x=-1.10, edge_y=0.0,
                     edge_z_centers=[0.30, 1.05, 1.80], axis='X')


def build_living_room():
    # Sofa — south-centre, faces west to window
    sx, sy = -0.30, 1.20
    make_box("Sofa_Seat", (sx, sy, 0.34),
             (1.80, 0.80, 0.20), COL_COUCH_TEAL)
    make_box("Sofa_Back", (sx, sy + 0.32, 0.74),
             (1.80, 0.20, 0.60), COL_COUCH_TEAL)
    for cs in (-1, +1):
        make_box(f"Sofa_Arm_{cs:+d}",
                 (sx + cs * 0.94, sy, 0.50),
                 (0.16, 0.80, 0.42), COL_COUCH_TRIM)
    # Throw pillows (rose accent)
    for pi, px in enumerate([-0.50, +0.30, +0.70]):
        make_box(f"Sofa_Pillow_{pi}",
                 (sx + px, sy + 0.10, 0.62),
                 (0.30, 0.20, 0.18), COL_ACCENT_ROSE)
    # Coffee table
    make_box("CoffeeTable_Top", (sx, sy - 0.80, 0.36),
             (1.20, 0.60, 0.04), COL_WOOD_TRIM)
    for li, (lx, ly) in enumerate([
            (sx - 0.54, sy - 1.04), (sx + 0.54, sy - 1.04),
            (sx - 0.54, sy - 0.56), (sx + 0.54, sy - 0.56)]):
        make_box(f"CoffeeTable_Leg_{li}", (lx, ly, 0.18),
                 (0.04, 0.04, 0.36), COL_WOOD_TRIM)
    # Mug + book on coffee table
    make_cyl("Mug", (sx - 0.30, sy - 0.80, 0.42),
             0.05, 0.10, COL_ACCENT_ROSE)
    make_box("Book", (sx + 0.30, sy - 0.80, 0.40),
             (0.20, 0.28, 0.04), COL_BOOK_SPINES[0])
    # Bookshelf along east wall
    sx2 = +2.90
    make_box("Bookshelf_Side_L", (sx2 - 0.36, 1.5, 1.00),
             (0.04, 0.36, 2.00), COL_BED_FRAME)
    make_box("Bookshelf_Side_R", (sx2 + 0.36, 1.5, 1.00),
             (0.04, 0.36, 2.00), COL_BED_FRAME)
    for shf in range(5):
        sz = 0.20 + shf * 0.42
        make_box(f"Bookshelf_Shelf_{shf}", (sx2, 1.5, sz),
                 (0.76, 0.36, 0.02), COL_BED_FRAME)
        for bi in range(6):
            bx = sx2 - 0.30 + bi * 0.12
            spine = COL_BOOK_SPINES[(shf * 2 + bi) % len(COL_BOOK_SPINES)]
            make_box(f"Bookshelf_Book_{shf}_{bi}",
                     (bx, 1.5, sz + 0.16),
                     (0.10, 0.28, 0.30), spine)


def build_kitchenette():
    # Small kitchenette north-west — L-shaped counter
    top_z = make_counter("Kitchen_W", (-3.0, 4.20, 0.0),
                         length=1.80, depth=0.70, height=0.92,
                         palette=PAL_APT_COUNTER)
    # Sink
    make_box("Kitchen_Sink", (-3.0, 4.20, 0.86),
             (0.50, 0.40, 0.12), P.METAL_STEEL)
    make_cyl("Kitchen_Faucet", (-3.0, 4.10, top_z + 0.02),
             0.015, 0.30, P.METAL_STEEL)
    # Counter run east — under fridge
    make_box("Kitchen_Counter_N", (-1.50, 5.20, 0.46),
             (2.40, 0.70, 0.92), PAL_APT_COUNTER["formica"])
    make_box("Kitchen_Counter_N_Top", (-1.50, 5.20, top_z),
             (2.50, 0.80, 0.06), PAL_APT_COUNTER["top"])
    # Stove
    make_box("Stove_Body", (-0.50, 5.20, 0.46),
             (0.70, 0.70, 0.92), (0.86, 0.84, 0.80, 1.0))
    make_box("Stove_Top", (-0.50, 5.20, 0.94),
             (0.70, 0.70, 0.04), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([
            (-0.70, 5.10), (-0.30, 5.10), (-0.70, 5.30), (-0.30, 5.30)]):
        make_cyl(f"Stove_Burner_{bi}", (bx, by, 0.96),
                 0.08, 0.02, P.METAL_STEEL)
    # Coffee pots on the counter
    make_coffee_pots("Coffee", (-2.0, 5.20, top_z), pots=1)
    # Fridge — east end of counter run
    make_box("Fridge_Body", (0.80, 5.20, 1.00),
             (0.70, 0.70, 2.00), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_Handle", (0.46, 4.85, 1.40),
             (0.03, 0.04, 0.10), P.METAL_STEEL)


def build_bed_nook():
    # Bed in north-east corner with low partition
    bx, by = +2.20, 4.50
    # Low partition (visual separator)
    make_box("Partition", (+0.80, 4.20, 0.60),
             (0.04, 0.80, 1.20), COL_WOOD_TRIM)
    # Mattress
    make_box("Bed_Mattress", (bx, by, 0.40),
             (1.40, 1.80, 0.20), COL_BED_LINEN)
    # Frame
    make_box("Bed_Frame", (bx, by, 0.18),
             (1.50, 1.90, 0.16), COL_BED_FRAME)
    # Pillow
    make_box("Bed_Pillow", (bx, by + 0.70, 0.56),
             (1.20, 0.40, 0.12), P.PAPER)
    # Throw blanket (rose, folded across foot)
    make_box("Bed_Throw", (bx, by - 0.50, 0.54),
             (1.20, 0.60, 0.06), COL_ACCENT_ROSE)
    # Nightstand
    make_box("Nightstand", (bx + 0.90, by + 0.20, 0.36),
             (0.40, 0.36, 0.72), COL_WOOD_TRIM)
    # Lamp on nightstand
    make_cyl("Nightstand_Lamp_Base", (bx + 0.90, by + 0.20, 0.74),
             0.05, 0.10, P.METAL_BLACK)
    make_cyl("Nightstand_Lamp_Shade", (bx + 0.90, by + 0.20, 0.94),
             0.10, 0.18, COL_BED_LINEN)


def build_decor():
    make_wall_clock("Clock", (-3.45, 2.5, 2.10),
                    frozen_hour=4, frozen_min=22)
    make_faded_poster("Poster_W", (-3.45, 1.0, 1.40))
    make_faded_poster("Poster_E", (+3.45, 4.5, 1.50),
                      palette={"body": COL_ACCENT_ROSE})
    make_floor_plant("Plant", (-2.5, 1.50, 0.0),
                     palette={"leaf": (0.42, 0.56, 0.42, 1.0)})


def build_ceiling_infra():
    for j, ypos in enumerate([1.6, 3.6]):
        make_fluorescent_tube_fixture(
            f"Fluor_{j}", (0.0, ypos, CEIL_Z),
            length=1.20, width=0.32)
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL_Z))
    make_hvac_vent("HVAC", (-1.0, 5.0, CEIL_Z), width=0.60, depth=0.30)


def main():
    clear_scene()
    build_shell()
    build_living_room()
    build_kitchenette()
    build_bed_nook()
    build_decor()
    build_ceiling_infra()
    out_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/natalie_apartment.glb"))
    print(f"\n[build_natalie_apartment] exporting to {out_path}")
    export_glb(out_path)


if __name__ == "__main__":
    main()
