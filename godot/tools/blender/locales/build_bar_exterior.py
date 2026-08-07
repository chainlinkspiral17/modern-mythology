"""Bar exterior — vol1 ch3's sidewalk ("what sort of superpower
would you have?"). The talk outside the bar, night.

The interior reuses new_orleans_bar; this is the street. Hero
features: a two-story brick frontage, the recessed bar door with
warm spill, the neon sign over the door, a big front window glowing
from inside, dark upper-story windows, a streetlamp, a parked sedan
at the curb, trash can, and the alley gap at the block's end.

Coordinate frame: Blender Z-up. y=0 is the road's south edge (the
camera stands on the sidewalk, y≈2-4); +Y runs north: road → curb →
sidewalk → building face at y=4.5. glTF export remaps to Godot
(x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  bar_exterior_night — on the sidewalk looking NW at door + neon.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_ASPHALT = (0.14, 0.14, 0.16, 1.0)
COL_CURB = (0.36, 0.36, 0.34, 1.0)
COL_WALK = (0.30, 0.30, 0.29, 1.0)
COL_BRICK = (0.34, 0.22, 0.18, 1.0)
COL_BRICK_DK = (0.26, 0.16, 0.13, 1.0)
COL_LINTEL = (0.44, 0.42, 0.38, 1.0)
COL_DOOR = (0.16, 0.13, 0.11, 1.0)
COL_DOOR_GLOW = (0.98, 0.76, 0.42, 1.0)
COL_WIN_WARM = (0.95, 0.72, 0.40, 1.0)
COL_WIN_DARK = (0.10, 0.11, 0.14, 1.0)
COL_FRAME = (0.18, 0.16, 0.14, 1.0)
COL_NEON = (0.95, 0.35, 0.42, 1.0)       # red-pink tube — blooms
COL_NEON_BOX = (0.20, 0.12, 0.14, 1.0)
COL_POLE = (0.26, 0.26, 0.28, 1.0)
COL_LAMP = (0.98, 0.84, 0.55, 1.0)
COL_CAR = (0.22, 0.26, 0.32, 1.0)
COL_CAR_DK = (0.12, 0.14, 0.17, 1.0)
COL_TIRE = (0.08, 0.08, 0.09, 1.0)
COL_SKY = (0.10, 0.10, 0.16, 1.0)


def build_street():
    make_box("Road", (0.0, 0.5, 0.0), (30.0, 3.0, 0.04), COL_ASPHALT)
    make_box("Curb", (0.0, 2.05, 0.07), (30.0, 0.25, 0.14), COL_CURB)
    make_box("Walk", (0.0, 3.3, 0.05), (30.0, 2.4, 0.10), COL_WALK)
    for i in range(9):
        make_box(f"Walk_Seam_{i}", (-12.0 + i * 3.0, 3.3, 0.105), (0.05, 2.4, 0.01),
                 COL_CURB)


def build_building():
    """Brick frontage, face at y=4.5, two stories."""
    make_box("Facade", (0.0, 5.0, 3.1), (16.0, 1.0, 6.2), COL_BRICK)
    make_box("Facade_Base", (0.0, 4.46, 0.35), (16.0, 0.10, 0.7), COL_BRICK_DK)
    make_box("Cornice", (0.0, 4.55, 6.05), (16.2, 0.35, 0.30), COL_LINTEL)
    make_box("Band_Course", (0.0, 4.44, 3.30), (16.0, 0.08, 0.22), COL_LINTEL)
    # Recessed bar door west of center, warm spill inside the reveal
    make_box("Door_Reveal", (-1.0, 4.30, 1.20), (1.4, 0.35, 2.4), COL_BRICK_DK)
    make_box("Door", (-1.0, 4.42, 1.15), (0.95, 0.06, 2.3), COL_DOOR)
    make_box("Door_Spill", (-1.0, 4.24, 1.15), (1.15, 0.04, 2.25), COL_DOOR_GLOW)
    make_box("Door_Lintel", (-1.0, 4.40, 2.55), (1.6, 0.20, 0.22), COL_LINTEL)
    # Big front window east of the door — warm from inside
    make_box("Win_Frame", (2.4, 4.42, 1.65), (3.2, 0.10, 1.9), COL_FRAME)
    make_box("Win_Warm", (2.4, 4.40, 1.65), (2.9, 0.06, 1.65), COL_WIN_WARM)
    make_box("Win_Sill", (2.4, 4.36, 0.66), (3.4, 0.18, 0.10), COL_LINTEL)
    # Dark upper-story windows
    for i, wx in enumerate((-5.5, -2.5, 0.5, 3.5, 6.5)):
        make_box(f"Up_Win_{i}", (wx, 4.44, 4.55), (1.1, 0.06, 1.5), COL_WIN_DARK)
        make_box(f"Up_Sill_{i}", (wx, 4.40, 3.75), (1.3, 0.14, 0.08), COL_LINTEL)
    # Neighbor frontage beyond the alley gap, west
    make_box("Alley_Gap", (-8.6, 5.2, 2.6), (1.2, 1.4, 5.2), (0.05, 0.05, 0.07, 1.0))
    make_box("Neighbor", (-11.5, 5.0, 2.6), (4.6, 1.0, 5.2), COL_BRICK_DK)


def build_neon():
    """The bar's neon over the door: backing box + two tube runs +
    a hanging bracket."""
    make_box("Neon_Box", (-1.0, 4.30, 3.15), (2.6, 0.22, 0.9), COL_NEON_BOX)
    make_box("Neon_Tube_Top", (-1.0, 4.16, 3.38), (2.1, 0.05, 0.10), COL_NEON)
    make_box("Neon_Tube_Bot", (-1.0, 4.16, 2.95), (1.6, 0.05, 0.08), COL_NEON)
    make_box("Neon_Bracket", (-1.0, 4.42, 3.68), (0.12, 0.30, 0.12), COL_FRAME)


def build_street_furniture():
    # Streetlamp east of the window
    make_cyl("Lamp_Pole", (4.8, 2.6, 2.3), 0.08, 4.6, COL_POLE, segments=8)
    make_box("Lamp_Arm", (4.8, 2.0, 4.55), (0.07, 1.3, 0.07), COL_POLE)
    make_box("Lamp_Head", (4.8, 1.45, 4.48), (0.22, 0.55, 0.12), COL_FRAME)
    make_box("Lamp_Bulb", (4.8, 1.45, 4.41), (0.15, 0.38, 0.03), COL_LAMP)
    # Trash can by the alley
    make_cyl("Trash", (-6.9, 3.6, 0.40), 0.26, 0.80, COL_POLE, segments=10)
    # Parked sedan at the curb, west of the door
    cx, cy = -3.8, 1.15
    make_box("Car_Body", (cx, cy, 0.62), (3.9, 1.6, 0.55), COL_CAR)
    make_box("Car_Cabin", (cx - 0.2, cy, 1.05), (2.1, 1.45, 0.45), COL_CAR)
    make_box("Car_Glass", (cx - 0.2, cy, 1.06), (1.85, 1.30, 0.36), COL_CAR_DK)
    for wx in (cx - 1.25, cx + 1.25):
        for wy in (cy - 0.8, cy + 0.8):
            make_cyl(f"Car_Wheel_{wx:.1f}_{wy:.1f}", (wx, wy, 0.30), 0.30, 0.22,
                     COL_TIRE, segments=10, axis='Y')


def build_backdrop():
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)
    # Far rooflines across the street behind the camera don't render;
    # a low distant block face beyond the building's roof
    make_box("Far_Block", (6.0, 9.0, 7.2), (20.0, 0.06, 2.4), (0.07, 0.07, 0.10, 1.0))


def main():
    clear_scene()
    build_street()
    build_building()
    build_neon()
    build_street_furniture()
    build_backdrop()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/bar_exterior.glb"))
    print(f"\n[build_bar_exterior] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)


if __name__ == "__main__":
    main()


def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 43m. The bar is on a street in a
    town: brick rooflines continuing down the block, a water tower
    silhouette, treeline past the edge of town."""
    from _props.detail import make_far_bands
    make_far_bands("FarBlock", COL_BRICK_DK,
                   [(60.0, 70.0, 7.5, 0.92), (130.0, 110.0, 9.0, 0.74)],
                   profile="roofline")
    make_far_bands("FarEdge", (0.20, 0.26, 0.17),
                   [(260.0, 200.0, 11.0, 0.55), (470.0, 330.0, 14.0, 0.42)],
                   profile="treeline")
    make_cyl("WaterTower_Tank", (95.0, 180.0, 26.0), 7.0, 8.0,
             (0.30, 0.30, 0.32, 1.0), segments=10)
    for li in range(4):
        make_cyl("WaterTower_Leg_%d" % li,
                 (95.0 + (5.0 if li % 2 else -5.0),
                  180.0 + (5.0 if li < 2 else -5.0), 11.0),
                 0.5, 22.0, (0.24, 0.24, 0.26, 1.0), segments=6)
