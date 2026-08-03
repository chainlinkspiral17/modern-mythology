"""Sapo Falls — vol2 ch2 interlude one. A waterfall in a green
gorge, seen from the viewing rocks at the pool's edge.

Hero features: the white fall column dropping from the rim notch,
the churned pool with its foam ring, stepped gray rock walls
flanking the gorge, mist slabs at the base, wet boulders in the
foreground, green growth clinging to the rim and ledges, and the
bright sky notch above.

Coordinate frame: Blender Z-up. y=0 is the viewing side (camera);
+Y runs north up the gorge to the falls face (y≈14). glTF export
remaps to Godot (x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  sapo_falls — on the rocks at the pool's edge, looking up at the
  column.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_ROCK = (0.42, 0.42, 0.40, 1.0)
COL_ROCK_DK = (0.32, 0.32, 0.31, 1.0)
COL_ROCK_WET = (0.26, 0.27, 0.27, 1.0)
COL_FALL = (0.88, 0.90, 0.90, 1.0)
COL_FALL_CORE = (0.94, 0.96, 0.96, 1.0)
COL_POOL = (0.20, 0.30, 0.30, 1.0)
COL_POOL_DK = (0.14, 0.22, 0.23, 1.0)
COL_FOAM = (0.78, 0.82, 0.80, 1.0)
COL_MIST = (0.72, 0.76, 0.76, 0.45)
COL_GREEN = (0.24, 0.38, 0.22, 1.0)
COL_GREEN_LT = (0.32, 0.46, 0.26, 1.0)
COL_MOSS = (0.30, 0.40, 0.24, 1.0)
COL_SKY = (0.72, 0.80, 0.84, 1.0)


def build_gorge():
    """Stepped rock walls flanking the falls; each side rises in
    three setback tiers so the gorge reads carved, not boxed."""
    tiers = [(0.0, 3.2, 4.0), (1.2, 6.0, 3.0), (2.4, 9.0, 2.2)]
    for side, sgn in (("W", -1), ("E", +1)):
        for ti, (setback, height, depth) in enumerate(tiers):
            x = sgn * (5.0 + setback + ti * 0.8)
            make_box(f"Wall_{side}_{ti}", (x, 9.0, height / 2.0),
                     (2.4 + ti * 1.2, 11.0, height),
                     COL_ROCK if ti % 2 == 0 else COL_ROCK_DK)
        # Moss patches on the lower tier
        for mi in range(3):
            make_box(f"Moss_{side}_{mi}", (sgn * (4.6 + 0.5 * mi), 5.5 + mi * 2.6,
                     1.0 + 0.7 * mi), (0.5, 1.2, 0.8), COL_MOSS)
    # The falls face: back wall with the rim notch
    make_box("Face", (0.0, 14.0, 4.5), (9.0, 1.2, 9.0), COL_ROCK_WET)
    make_box("Rim_W", (-3.2, 13.9, 9.4), (2.6, 1.4, 1.0), COL_ROCK)
    make_box("Rim_E", (3.2, 13.9, 9.4), (2.6, 1.4, 1.0), COL_ROCK)


def build_falls():
    """The column: a bright core inside a softer sheet, plus the
    lip where it leaves the rim."""
    make_box("Fall_Sheet", (0.0, 13.35, 5.2), (2.6, 0.30, 8.4), COL_FALL)
    make_box("Fall_Core", (0.0, 13.30, 5.6), (1.4, 0.22, 7.4), COL_FALL_CORE)
    make_box("Fall_Lip", (0.0, 13.6, 9.35), (2.9, 0.8, 0.5), COL_FALL)
    # Broken side threads
    make_box("Thread_W", (-1.9, 13.4, 4.2), (0.30, 0.20, 5.6), COL_FALL)
    make_box("Thread_E", (1.7, 13.4, 3.4), (0.22, 0.20, 4.2), COL_FALL)


def build_pool():
    make_box("Pool", (0.0, 9.5, 0.02), (9.5, 8.0, 0.06), COL_POOL)
    make_box("Pool_Deep", (0.0, 12.0, 0.03), (6.0, 3.0, 0.05), COL_POOL_DK)
    # Foam ring at the plunge + drift lines
    make_box("Foam_Ring", (0.0, 12.6, 0.07), (3.6, 1.0, 0.03), COL_FOAM)
    make_box("Foam_Drift_0", (-1.6, 10.8, 0.065), (2.2, 0.18, 0.02), COL_FOAM)
    make_box("Foam_Drift_1", (1.4, 9.8, 0.06), (1.7, 0.14, 0.02), COL_FOAM)
    # Mist slabs at the base of the column
    make_box("Mist_Lo", (0.0, 12.7, 1.2), (4.4, 1.4, 2.2), COL_MIST)
    make_box("Mist_Hi", (0.0, 13.0, 3.0), (3.0, 1.0, 1.6), COL_MIST)


def build_foreground():
    """Wet boulders + the viewing rocks the camera stands on."""
    rocks = [(-2.8, 4.6, 0.55, 1.4), (-0.6, 3.6, 0.40, 1.1), (1.8, 4.9, 0.65, 1.6),
             (3.4, 3.4, 0.35, 0.9), (-4.2, 3.0, 0.45, 1.2), (0.9, 5.8, 0.30, 0.8)]
    for i, (rx, ry, rz, rs) in enumerate(rocks):
        make_box(f"Boulder_{i}", (rx, ry, rz / 2.0 + 0.02), (rs, rs * 0.8, rz),
                 COL_ROCK_WET if i % 2 == 0 else COL_ROCK_DK)
    make_box("Shore", (0.0, 2.2, 0.05), (12.0, 3.4, 0.14), COL_ROCK)
    # Green growth on the rims and along the shore edges
    fringe = [(-5.2, 2.5, 0.9), (5.0, 2.8, 0.8), (-4.4, 12.6, 10.1),
              (4.2, 12.6, 10.1), (-6.2, 7.0, 4.3), (6.4, 8.0, 5.4)]
    for i, (gx, gy, gz) in enumerate(fringe):
        col = COL_GREEN if i % 2 == 0 else COL_GREEN_LT
        make_box(f"Green_{i}", (gx, gy, gz), (1.8, 1.4, 1.0), col)


def build_sky():
    make_box("Sky", (0.0, 18.0, 8.0), (40.0, 0.06, 16.0), COL_SKY)


def main():
    clear_scene()
    build_gorge()
    build_falls()
    build_pool()
    build_foreground()
    build_sky()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/sapo_falls.glb"))
    print(f"\n[build_sapo_falls] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
