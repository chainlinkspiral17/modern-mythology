"""Missing Link exterior — vol1's roadside bus-depot diner from the
lot, plus THE SHUTTLE BENCH (vol1's highest-traffic background: the
whole link_* question chain is played sitting at this stop).

Companion to build_missing_link_interior.py — same diner, seen from
outside at dusk. Canon: a roadside bus-depot diner; the shuttle
stops at a three-sided shelter on the shoulder east of the building.

Hero features: the stainless-clad diner front with its warm window
band and glazed door, the double-panel MISSING LINK pole sign with
arrow, the bus shelter with slat bench + route board + trash can,
a cobra-head lamppost, telephone poles along the far shoulder, a
parked pickup, and a dark treeline under a dusk sky.

Coordinate frame: Blender Z-up. y=0 is the road's south edge (the
camera side); +Y runs north through road → gravel lot → diner front
(y=8) → treeline. glTF export remaps to Godot (x, z, -y).

Two vantages wired in Background3D.CAMERA_PRESETS:
  missing_link_exterior — in the lot looking NNE at the diner front.
  shuttle_bench         — seated at the shelter looking W down the
                          shoulder: road left, diner + sign center.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

# ── Palette (dusk) ──
COL_ASPHALT = (0.16, 0.16, 0.18, 1.0)
COL_DASH = (0.72, 0.68, 0.52, 1.0)
COL_GRAVEL = (0.42, 0.38, 0.32, 1.0)
COL_GRASS = (0.24, 0.28, 0.18, 1.0)
COL_CLAD = (0.58, 0.60, 0.63, 1.0)       # stainless cladding
COL_CLAD_DK = (0.44, 0.46, 0.50, 1.0)
COL_TRIM = (0.55, 0.18, 0.16, 1.0)       # diner red band
COL_GLOW = (1.00, 0.82, 0.50, 1.0)       # lit windows — blooms via glow
COL_DOOR = (0.30, 0.32, 0.36, 1.0)
COL_SIGN = (0.88, 0.84, 0.72, 1.0)       # cream sign face
COL_SIGN_RED = (0.62, 0.20, 0.16, 1.0)
COL_POLE = (0.30, 0.30, 0.32, 1.0)
COL_SHELTER = (0.36, 0.38, 0.36, 1.0)    # painted municipal green-gray
COL_BENCH = (0.46, 0.34, 0.22, 1.0)      # worn wood slats
COL_WOODPOLE = (0.26, 0.20, 0.15, 1.0)   # creosote telephone poles
COL_TRUCK = (0.34, 0.40, 0.44, 1.0)
COL_TRUCK_DK = (0.20, 0.24, 0.26, 1.0)
COL_TIRE = (0.10, 0.10, 0.11, 1.0)
COL_TREE = (0.10, 0.14, 0.10, 1.0)
COL_TREE_LT = (0.13, 0.18, 0.12, 1.0)
COL_HILL = (0.16, 0.18, 0.22, 1.0)
COL_SKY = (0.30, 0.26, 0.38, 1.0)        # dusk violet


def build_ground():
    # Road: two lanes running E-W, y ∈ [0, 3.4]
    make_box("Road", (0.0, 1.7, 0.0), (34.0, 3.4, 0.04), COL_ASPHALT)
    for i in range(11):
        make_box(f"Dash_{i}", (-15.0 + i * 3.0, 1.7, 0.045), (1.3, 0.12, 0.012), COL_DASH)
    # Gravel shoulder / diner lot north of the road
    make_box("Lot", (0.0, 5.7, 0.0), (34.0, 4.6, 0.05), COL_GRAVEL)
    # Grass fringes: south of road, and between lot and treeline
    make_box("Grass_S", (0.0, -2.0, 0.0), (34.0, 4.0, 0.04), COL_GRASS)
    make_box("Grass_N", (0.0, 14.5, 0.0), (34.0, 5.0, 0.04), COL_GRASS)


def build_diner():
    """The diner box: front face at y=8, x ∈ [-4.5, 3.5], flat roof."""
    # Main volume
    make_box("Diner_Body", (-0.5, 10.5, 1.7), (8.0, 5.0, 3.4), COL_CLAD)
    # Red trim band + parapet cap
    make_box("Diner_Band", (-0.5, 7.98, 2.95), (8.0, 0.10, 0.5), COL_TRIM)
    make_box("Diner_Parapet", (-0.5, 10.5, 3.48), (8.2, 5.2, 0.16), COL_CLAD_DK)
    # Warm window band along the front (proud of the face so it reads)
    for i, wx in enumerate((-3.4, -1.9, -0.4, 1.1)):
        make_box(f"Diner_Win_{i}", (wx, 7.94, 1.65), (1.25, 0.06, 1.15), COL_GLOW)
        make_box(f"Diner_WinFrame_{i}", (wx, 7.96, 1.65), (1.40, 0.05, 1.30), COL_CLAD_DK)
    # Glazed door, east end of the front, with concrete step
    make_box("Diner_Door", (2.4, 7.94, 1.25), (0.92, 0.08, 2.30), COL_DOOR)
    make_box("Diner_DoorGlass", (2.4, 7.90, 1.55), (0.62, 0.05, 1.20), COL_GLOW)
    make_box("Diner_Step", (2.4, 7.65, 0.09), (1.3, 0.7, 0.18), COL_CLAD_DK)
    # Roof clutter: A/C unit + vent
    make_box("Diner_AC", (-2.5, 10.8, 3.85), (1.2, 1.0, 0.6), COL_CLAD_DK)
    make_cyl("Diner_Vent", (1.5, 11.5, 3.85), 0.16, 0.55, COL_POLE, segments=8)


def build_pole_sign():
    """Double-panel MISSING LINK sign on a pole west of the diner,
    an arrow panel angled at the lot."""
    make_cyl("Sign_Pole", (-6.5, 6.5, 2.1), 0.11, 4.2, COL_POLE, segments=8)
    make_box("Sign_Face_N", (-6.5, 6.56, 4.7), (2.6, 0.10, 1.1), COL_SIGN)
    make_box("Sign_Face_S", (-6.5, 6.44, 4.7), (2.6, 0.10, 1.1), COL_SIGN)
    make_box("Sign_Border", (-6.5, 6.5, 4.7), (2.75, 0.08, 1.25), COL_SIGN_RED)
    # Arrow panel under the main faces, pointing at the diner
    make_box("Sign_Arrow", (-5.9, 6.5, 3.85), (1.3, 0.09, 0.4), COL_SIGN_RED)
    make_box("Sign_Arrow_Tip", (-5.15, 6.5, 3.85), (0.28, 0.09, 0.7), COL_SIGN_RED)


def build_shelter():
    """The shuttle shelter: concrete pad, three walls, flat roof,
    slat bench, route board, trash can. Opening faces the road."""
    sx, sy = 6.5, 4.9          # shelter center
    make_box("Shelter_Pad", (sx, sy, 0.05), (3.0, 1.8, 0.10), COL_CLAD_DK)
    # Back wall (north) + side walls
    make_box("Shelter_Back", (sx, sy + 0.85, 1.25), (3.0, 0.10, 2.3), COL_SHELTER)
    make_box("Shelter_Side_W", (sx - 1.45, sy, 1.25), (0.10, 1.8, 2.3), COL_SHELTER)
    make_box("Shelter_Side_E", (sx + 1.45, sy, 1.25), (0.10, 1.8, 2.3), COL_SHELTER)
    make_box("Shelter_Roof", (sx, sy, 2.46), (3.3, 2.1, 0.12), COL_CLAD_DK)
    # Slat bench along the back wall
    for i in range(3):
        make_box(f"Bench_Slat_{i}", (sx, sy + 0.55 - i * 0.13, 0.46), (2.3, 0.11, 0.04), COL_BENCH)
    make_box("Bench_Back", (sx, sy + 0.72, 0.72), (2.3, 0.06, 0.34), COL_BENCH)
    for lx in (sx - 1.0, sx + 1.0):
        make_box(f"Bench_Leg_{lx:.1f}", (lx, sy + 0.45, 0.22), (0.08, 0.34, 0.44), COL_POLE)
    # Route board on its own post, just west of the shelter
    make_cyl("Route_Post", (sx - 2.0, sy - 0.6, 0.85), 0.04, 1.7, COL_POLE, segments=6)
    make_box("Route_Board", (sx - 2.0, sy - 0.55, 1.95), (0.55, 0.06, 0.75), COL_SIGN)
    make_box("Route_Board_Head", (sx - 2.0, sy - 0.53, 2.22), (0.55, 0.05, 0.16), COL_SIGN_RED)
    # Trash can east of the bench
    make_cyl("Trash", (sx + 1.9, sy - 0.3, 0.38), 0.24, 0.76, COL_SHELTER, segments=10)


def build_street_furniture():
    # Cobra-head lamppost between shelter and road
    make_cyl("Lamp_Pole", (8.2, 4.0, 2.5), 0.09, 5.0, COL_POLE, segments=8)
    make_box("Lamp_Arm", (8.2, 3.2, 4.95), (0.08, 1.7, 0.08), COL_POLE)
    make_box("Lamp_Head", (8.2, 2.45, 4.88), (0.24, 0.62, 0.14), COL_CLAD_DK)
    make_box("Lamp_Bulb", (8.2, 2.45, 4.80), (0.16, 0.42, 0.03), COL_GLOW)
    # Telephone poles along the far (south) shoulder
    for i, px in enumerate((-12.0, -2.0, 8.0)):
        make_cyl(f"TPole_{i}", (px, -0.8, 3.0), 0.12, 6.0, COL_WOODPOLE, segments=7)
        make_box(f"TPole_{i}_Arm", (px, -0.8, 5.6), (1.5, 0.09, 0.09), COL_WOODPOLE)
    # Parked pickup in the lot, west of the door
    tx, ty = -8.5, 5.6
    make_box("Truck_Bed", (tx, ty, 0.75), (3.6, 1.6, 0.7), COL_TRUCK)
    make_box("Truck_Cab", (tx + 1.0, ty, 1.35), (1.4, 1.5, 0.6), COL_TRUCK)
    make_box("Truck_Glass", (tx + 1.0, ty, 1.38), (1.15, 1.30, 0.42), COL_TRUCK_DK)
    for wx, wy in ((tx - 1.1, ty - 0.8), (tx + 1.1, ty - 0.8),
                   (tx - 1.1, ty + 0.8), (tx + 1.1, ty + 0.8)):
        make_cyl(f"Truck_Wheel_{wx:.0f}_{wy:.0f}", (wx, wy, 0.34), 0.34, 0.24,
                 COL_TIRE, segments=10, axis='Y')


def build_backdrop():
    # Dark treeline north of the grass
    for i in range(12):
        tx = -15.0 + i * 2.8
        h = 3.6 + 1.3 * ((i * 5) % 3)
        make_box(f"Tree_{i}", (tx, 16.5, h / 2.0), (2.6, 1.8, h),
                 COL_TREE if i % 2 == 0 else COL_TREE_LT)
    # Low hill band + dusk sky
    make_box("Hills", (0.0, 20.0, 3.0), (48.0, 0.06, 6.0), COL_HILL)
    make_box("Sky", (0.0, 24.0, 8.0), (60.0, 0.06, 16.0), COL_SKY)


def main():
    clear_scene()
    build_ground()
    build_diner()
    build_pole_sign()
    build_shelter()
    build_street_furniture()
    build_backdrop()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/missing_link_exterior.glb"))
    print(f"\n[build_missing_link_exterior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
