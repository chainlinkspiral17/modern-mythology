"""Grunion beach — vol2's night shore, one set, two wired vantages.

Canon (vol2 ch2): "I walked down to the water's edge. It was after
dark, and the moon could not be seen behind the clouds… light was
caught up in water that gleamed off the fresh tide's edge" (the
ghost scene), and the grunion-run interlude — silver fish flickering
on the wet sand at the tide line.

Hero features: dry sand foreground with dune-grass tufts and a
driftwood log, the darker wet-sand band, three pale surf lines, the
near-black sea, a cloud bank with one hidden-moon glow patch, and a
scatter of silver grunion flecks along the tide's edge.

Coordinate frame: Blender Z-up. y=0 is the dune side (camera side);
+Y runs north toward the water: dry sand → wet band (y≈8-10) → surf
→ sea → sky. glTF export remaps to Godot (x, z, -y).

Vantages wired in Background3D.CAMERA_PRESETS:
  beach_night   — standing on the dry sand looking out at the dark
                  water (the ghost scene).
  grunion_beach — low at the tide edge, the silver run at your feet.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_SAND = (0.30, 0.28, 0.24, 1.0)       # night sand
COL_SAND_WET = (0.20, 0.20, 0.20, 1.0)   # gleaming band, darker
COL_GLEAM = (0.38, 0.40, 0.42, 1.0)      # tide-edge sheen
COL_SURF = (0.55, 0.58, 0.58, 1.0)       # foam lines
COL_SEA = (0.07, 0.09, 0.12, 1.0)
COL_SEA_FAR = (0.10, 0.13, 0.17, 1.0)
COL_SKY = (0.13, 0.14, 0.19, 1.0)        # clouded night
COL_CLOUD = (0.18, 0.19, 0.24, 1.0)
COL_MOONGLOW = (0.30, 0.31, 0.36, 1.0)   # the moon behind the clouds
COL_GRASS = (0.16, 0.19, 0.14, 1.0)
COL_DRIFT = (0.26, 0.22, 0.18, 1.0)
COL_GRUNION = (0.72, 0.76, 0.78, 1.0)    # silver flecks — bloom lifts them


def build_sand():
    make_box("Sand_Dry", (0.0, 4.0, 0.0), (36.0, 8.0, 0.06), COL_SAND)
    make_box("Sand_Wet", (0.0, 9.0, 0.01), (36.0, 2.2, 0.05), COL_SAND_WET)
    # The gleam: a thin lighter band right at the tide's edge
    make_box("Tide_Gleam", (0.0, 10.05, 0.03), (36.0, 0.5, 0.02), COL_GLEAM)
    # Low dune rise at the very south edge
    make_box("Dune", (0.0, -0.8, 0.20), (36.0, 2.0, 0.45), COL_SAND)


def build_sea():
    make_box("Surf_0", (0.0, 10.6, 0.035), (36.0, 0.25, 0.02), COL_SURF)
    make_box("Surf_1", (-2.0, 11.5, 0.03), (30.0, 0.20, 0.02), COL_SURF)
    make_box("Surf_2", (3.0, 12.6, 0.03), (26.0, 0.16, 0.02), COL_SURF)
    make_box("Sea_Near", (0.0, 14.5, 0.0), (44.0, 7.0, 0.05), COL_SEA)
    make_box("Sea_Far", (0.0, 21.0, 0.4), (52.0, 6.0, 0.05), COL_SEA_FAR)


def build_sky():
    make_box("Sky", (0.0, 28.0, 7.0), (60.0, 0.06, 14.0), COL_SKY)
    # Cloud bank slabs, slightly proud of the sky plane
    make_box("Cloud_0", (-8.0, 27.8, 9.5), (22.0, 0.06, 2.6), COL_CLOUD)
    make_box("Cloud_1", (10.0, 27.9, 8.2), (18.0, 0.06, 2.0), COL_CLOUD)
    make_box("Cloud_2", (0.0, 27.85, 11.4), (26.0, 0.06, 1.6), COL_CLOUD)
    # The hidden moon: a soft glow patch behind the cloud seam
    make_box("Moon_Glow", (5.0, 27.95, 10.2), (4.5, 0.04, 2.8), COL_MOONGLOW)


def build_foreground():
    # Driftwood log, half-buried
    make_cyl("Driftwood", (-3.5, 4.8, 0.16), 0.22, 3.2, COL_DRIFT, segments=8, axis='X')
    make_cyl("Driftwood_Stub", (-1.8, 4.6, 0.30), 0.10, 0.5, COL_DRIFT, segments=6)
    # Dune-grass tufts: thin dark blades in clumps
    clumps = [(-6.5, 0.8), (-4.0, 1.6), (-0.5, 0.6), (2.5, 1.4), (5.5, 0.9), (8.0, 1.8)]
    for ci, (cx, cy) in enumerate(clumps):
        for b in range(5):
            bx = cx + 0.10 * ((b * 7 + ci * 3) % 5 - 2)
            h = 0.35 + 0.10 * ((b + ci) % 3)
            make_box(f"Grass_{ci}_{b}", (bx, cy + 0.06 * (b % 3), h / 2.0),
                     (0.03, 0.03, h), COL_GRASS)


def build_grunion():
    """The run: silver flecks scattered along the wet band. Sparse
    enough to read as fish, not noise."""
    for i in range(26):
        gx = -14.0 + (i * 41) % 28 + 0.35 * ((i * 7) % 3)
        gy = 9.3 + 0.011 * ((i * 13) % 100)
        make_box(f"Grunion_{i}", (gx, gy, 0.055),
                 (0.16, 0.045, 0.02), COL_GRUNION)


def main():
    clear_scene()
    build_sand()
    build_sea()
    build_sky()
    build_foreground()
    build_grunion()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/grunion_beach.glb"))
    print(f"\n[build_grunion_beach] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)


if __name__ == "__main__":
    main()


def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 50m. Night sea to a true horizon
    seaward; dune ridges and a distant point light landward."""
    make_box("Sea_Deep", (0.0, 90.0, 0.3), (180.0, 62.0, 0.05), COL_SEA_FAR)
    make_box("Sea_Horizon", (0.0, 300.0, 0.2), (460.0, 150.0, 0.05),
             (COL_SEA_FAR[0] * 1.3, COL_SEA_FAR[1] * 1.3,
              COL_SEA_FAR[2] * 1.25, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarDune", (0.24, 0.23, 0.20),
                   [(70.0, 80.0, 5.0, 0.85), (150.0, 130.0, 7.0, 0.65),
                    (300.0, 230.0, 9.0, 0.48)], sides="SEW",
                   profile="ridge")
