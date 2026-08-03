"""RELOCATED (canon): Simons, Gulf Coast parish walk-up — not San Francisco.
VOL 5 · Natalie's Apartment — Empress chapter (vol5_ch3).

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
    make_box("Kitchen_Counter_N", (-1.50, 5.050, 0.46),
             (2.40, 0.70, 0.92), PAL_APT_COUNTER["formica"])
    make_box("Kitchen_Counter_N_Top", (-1.50, 5.050, top_z),
             (2.50, 0.80, 0.06), PAL_APT_COUNTER["top"])
    # Stove
    make_box("Stove_Body", (-0.50, 5.050, 0.46),
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
    make_box("Fridge_Body", (0.80, 5.050, 1.00),
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
    # Candle-and-lamp apartment: no tubes; the under-cabinet strip,
    # the scarf lamp and the blinds' moonlight carry the room
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL_Z))
    make_hvac_vent("HVAC", (-1.0, 5.0, CEIL_Z), width=0.60, depth=0.30)


def build_hero_props():
    """2026-08-03 tail pass: THE DUAL 1219 record player, the
    windowsill (the Hanged Man lives on it), the kettle, the rug +
    the low reading table + fanned cards, the under-cabinet light
    (the apartment's you're-welcome lamp), the futon quilt, the
    step-stool, the scarf lamp, the blinds."""
    # The Dual turntable on its stand, west corner
    make_box("Turntable_Stand", (-3.00, 1.90, 0.30), (0.50, 0.42, 0.60), (0.36, 0.26, 0.17, 1.0))
    make_box("Turntable_Plinth", (-3.00, 1.90, 0.66), (0.42, 0.36, 0.10), (0.30, 0.22, 0.14, 1.0))
    make_cyl("Turntable_Platter", (-3.03, 1.90, 0.73), 0.15, 0.02, (0.12, 0.12, 0.13, 1.0), segments=14)
    make_box("Turntable_Tonearm", (-2.86, 1.98, 0.745), (0.02, 0.20, 0.015), (0.60, 0.62, 0.63, 1.0))
    # The windowsill + the Hanged Man face-up on it
    make_box("W_Sill", (-3.32, 2.5, 0.55), (0.16, 1.90, 0.05), (0.42, 0.30, 0.20, 1.0))
    make_box("HangedMan_Card", (-3.32, 2.20, 0.585), (0.10, 0.07, 0.002), (0.86, 0.82, 0.70, 1.0))
    make_box("HangedMan_Figure", (-3.32, 2.20, 0.587), (0.03, 0.045, 0.002), (0.30, 0.34, 0.52, 1.0))
    # The kettle on the front burner
    make_cyl("Kettle", (-0.68, 4.95, 1.07), 0.09, 0.18, (0.62, 0.64, 0.65, 1.0), segments=10)
    # The worn rug + the low reading table (daytime footstool) +
    # fanned cards
    make_box("Reading_Rug", (-0.60, 1.90, 0.012), (2.20, 1.80, 0.02), (0.46, 0.34, 0.30, 1.0))
    make_box("Rug_Worn_Patch", (-1.40, 1.90, 0.024), (0.55, 0.45, 0.006), (0.54, 0.42, 0.36, 1.0))
    make_box("Low_Table", (-0.60, 1.90, 0.22), (0.55, 0.55, 0.10), (0.42, 0.30, 0.20, 1.0))
    for ci in range(5):
        make_box(f"Fanned_Card_{ci}", (-0.75 + ci * 0.09, 1.72 + 0.02 * (ci % 2), 0.276),
                 (0.07, 0.11, 0.002), (0.86, 0.82, 0.70, 1.0))
    # Upper cabinets + THE under-cabinet light
    make_box("Upper_Cabs", (-1.50, 5.18, 1.85), (2.40, 0.34, 0.70), (0.42, 0.32, 0.24, 1.0))
    make_box("UnderCab_Light", (-1.50, 5.04, 1.49), (2.30, 0.06, 0.03), (0.98, 0.90, 0.70, 1.0))
    # Futon-ify: the twilight quilt over the sofa/futon
    make_box("Twilight_Quilt", (2.10, 2.4, 0.62), (1.30, 0.85, 0.08), (0.34, 0.30, 0.50, 1.0))
    # Step-stool by the bookshelf, the scarf lamp, the blinds
    make_box("Step_Stool", (2.55, 4.55, 0.16), (0.36, 0.30, 0.32), (0.46, 0.34, 0.22, 1.0))
    make_cyl("Scarf_Lamp_Base", (1.15, 0.55, 0.62), 0.06, 0.03, (0.30, 0.22, 0.14, 1.0), segments=8)
    make_cyl("Scarf_Lamp_Shade", (1.15, 0.55, 0.92), 0.12, 0.18, (0.62, 0.34, 0.44, 0.9), segments=10)
    make_box("Draped_Scarf", (1.20, 0.50, 1.02), (0.20, 0.16, 0.05), (0.56, 0.28, 0.40, 1.0))
    for bi in range(8):
        make_box(f"Blind_Slat_{bi}", (-3.30, 2.5, 0.80 + bi * 0.14), (0.02, 1.80, 0.03), (0.72, 0.70, 0.64, 1.0))


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
    build_hero_props()
    export_glb(out_path)


if __name__ == "__main__":
    main()
