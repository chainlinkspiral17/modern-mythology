"""Skatepark — vol1 ch2's afternoon ("fun just to imagine how the
world could be"). Municipal concrete park, day.

Hero features: the big concrete slab with two half-buried pipe
humps, a grind ledge pair, a flat rail on posts, a three-stair set
with handrail, chain-link fence along the back, a bench, tagged
utility box, and trees over the fence line.

Coordinate frame: Blender Z-up. y=0 is the entry side (camera);
+Y runs north across the slab to the fence. glTF export remaps to
Godot (x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  skatepark_day — at the slab's south edge looking N across the
  features.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_SLAB = (0.56, 0.56, 0.54, 1.0)
COL_SLAB_DK = (0.46, 0.46, 0.45, 1.0)
COL_LEDGE = (0.50, 0.50, 0.48, 1.0)
COL_COPING = (0.66, 0.62, 0.52, 1.0)     # steel coping edge
COL_RAIL = (0.40, 0.42, 0.46, 1.0)
COL_GRASS = (0.42, 0.50, 0.30, 1.0)
COL_FENCE = (0.48, 0.50, 0.52, 1.0)
COL_TRUNK = (0.32, 0.24, 0.16, 1.0)
COL_LEAF = (0.30, 0.44, 0.24, 1.0)
COL_LEAF_LT = (0.38, 0.52, 0.28, 1.0)
COL_BENCH = (0.44, 0.32, 0.22, 1.0)
COL_TAG_A = (0.62, 0.30, 0.44, 1.0)      # spray tags on the utility box
COL_TAG_B = (0.30, 0.44, 0.60, 1.0)
COL_BOX = (0.42, 0.46, 0.42, 1.0)
COL_SKY = (0.68, 0.76, 0.82, 1.0)


def build_ground():
    make_box("Grass_Base", (0.0, 7.0, 0.0), (30.0, 20.0, 0.05), COL_GRASS)
    make_box("Slab", (-1.0, 6.0, 0.02), (16.0, 12.0, 0.06), COL_SLAB)
    # Expansion seams
    for i in range(4):
        make_box(f"Seam_X_{i}", (-7.0 + i * 4.0, 6.0, 0.055), (0.06, 12.0, 0.01), COL_SLAB_DK)
    make_box("Seam_Y", (-1.0, 6.0, 0.055), (16.0, 0.06, 0.01), COL_SLAB_DK)


def build_features():
    # THE POOL (canon: "waiting to push off into the pool") — an
    # in-ground bowl suggested without booleans: darker basin patch,
    # steel coping ring, a visible far inner wall band, deck lip.
    px, py = 0.5, 7.2
    make_box("Pool_Basin", (px, py, 0.028), (5.6, 4.0, 0.02), (0.40, 0.41, 0.41, 1.0))
    make_box("Pool_Deep", (px + 0.6, py + 0.4, 0.034), (3.0, 2.2, 0.015), (0.34, 0.35, 0.36, 1.0))
    # Coping ring: short segments tracing the rounded-rect rim
    rim = [(-2.8, 0.0, 0.14, 3.6), (2.8, 0.0, 0.14, 3.6), (0.0, -2.0, 5.2, 0.14),
           (0.0, 2.0, 5.2, 0.14), (-2.55, -1.75, 0.6, 0.6), (2.55, -1.75, 0.6, 0.6),
           (-2.55, 1.75, 0.6, 0.6), (2.55, 1.75, 0.6, 0.6)]
    for i, (dx, dy, w, d) in enumerate(rim):
        make_box(f"Pool_Coping_{i}", (px + dx, py + dy, 0.065), (w, d, 0.05), COL_COPING)
    # Far inner wall band (visible over the rim from the S camera)
    make_box("Pool_Wall_N", (px, py + 1.85, 0.0), (5.2, 0.10, 0.10), COL_SLAB_DK)
    # One half-buried pipe hump keeps the flow line west
    make_cyl("Hump_W", (-4.5, 5.0, -0.25), 1.15, 5.0, COL_SLAB_DK, segments=18, axis='X')
    # Grind ledge pair
    make_box("Ledge_Lo", (1.5, 4.0, 0.20), (2.6, 0.65, 0.40), COL_LEDGE)
    make_box("Ledge_Lo_Coping", (1.5, 4.0, 0.415), (2.6, 0.65, 0.035), COL_COPING)
    make_box("Ledge_Hi", (4.2, 4.4, 0.30), (2.0, 0.65, 0.60), COL_LEDGE)
    make_box("Ledge_Hi_Coping", (4.2, 4.4, 0.615), (2.0, 0.65, 0.035), COL_COPING)
    # Flat rail on posts
    for py in (2.6, 4.4):
        make_box(f"Rail_Post_{py:.1f}", (-2.0, py, 0.22), (0.07, 0.07, 0.44), COL_RAIL)
    make_cyl("Rail", (-2.0, 3.5, 0.46), 0.045, 2.2, COL_RAIL, segments=8, axis='Y')
    # Three-stair set into a lower pad, with handrail
    for s in range(3):
        make_box(f"Stair_{s}", (-6.5, 8.6 + s * 0.35, 0.30 - s * 0.10),
                 (2.4, 0.35, 0.60 - s * 0.20), COL_LEDGE)
    make_box("Stair_Pad", (-6.5, 10.4, 0.02), (2.8, 1.6, 0.06), COL_SLAB_DK)
    make_box("HandRail_Post_S", (-5.5, 8.5, 0.45), (0.06, 0.06, 0.9), COL_RAIL)
    make_box("HandRail_Post_N", (-5.5, 10.3, 0.25), (0.06, 0.06, 0.5), COL_RAIL)
    make_cyl("HandRail", (-5.5, 9.4, 0.72), 0.04, 2.0, COL_RAIL, segments=8, axis='Y')


def build_perimeter():
    # Chain-link fence: posts + top rail + a faint mesh plane
    for i in range(9):
        fx = -12.0 + i * 3.0
        make_cyl(f"Fence_Post_{i}", (fx, 12.5, 0.9), 0.05, 1.8, COL_FENCE, segments=6)
    make_cyl("Fence_TopRail", (0.0, 12.5, 1.78), 0.035, 24.5, COL_FENCE, segments=6, axis='X')
    make_box("Fence_Mesh", (0.0, 12.5, 0.9), (24.5, 0.02, 1.7), (0.55, 0.57, 0.58, 0.35))
    # Bench + tagged utility box near the entry
    make_box("Bench_Seat", (5.5, 1.5, 0.42), (1.8, 0.45, 0.06), COL_BENCH)
    for bx in (4.8, 6.2):
        make_box(f"Bench_Leg_{bx:.1f}", (bx, 1.5, 0.20), (0.08, 0.4, 0.40), COL_RAIL)
    make_box("Utility_Box", (-8.6, 2.0, 0.55), (0.8, 0.6, 1.10), COL_BOX)
    make_box("Tag_A", (-8.6, 1.68, 0.62), (0.5, 0.02, 0.28), COL_TAG_A)
    make_box("Tag_B", (-8.45, 1.68, 0.92), (0.34, 0.02, 0.18), COL_TAG_B)


def build_backdrop():
    # Trees over the fence line
    spots = [(-10.0, 14.5), (-5.0, 15.5), (0.5, 14.8), (6.0, 15.2), (10.5, 14.3)]
    for i, (px, py) in enumerate(spots):
        h = 4.2 + 1.0 * ((i * 3) % 3)
        make_cyl(f"Tree_{i}_Trunk", (px, py, h * 0.22), 0.18, h * 0.44, COL_TRUNK, segments=6)
        col = COL_LEAF if i % 2 == 0 else COL_LEAF_LT
        make_box(f"Tree_{i}_Crown", (px, py, h * 0.68), (2.6, 2.4, h * 0.55), col)
    make_box("Sky", (0.0, 22.0, 7.0), (50.0, 0.06, 14.0), COL_SKY)


def main():
    clear_scene()
    build_ground()
    build_features()
    build_perimeter()
    build_backdrop()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/skatepark.glb"))
    print(f"\n[build_skatepark] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
