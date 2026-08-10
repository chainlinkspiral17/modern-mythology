"""Sapo Falls — vol2 ch2 interlude one. Canon places the dream in
VENEZUELA: "the Canaima region — naturally rich in elevated tepuis,
dense with dark green vegetation and flowing with towering
waterfalls." So this is Salto El Sapo country, not a temperate
gorge: a flat-topped tepui on the skyline, vegetation dense and
dark, the fall tall.

Hero features: the white fall column dropping from the rim notch,
the churned pool with its foam ring, stepped rock walls flanking
the gorge under heavy green growth, mist slabs at the base, wet
boulders in the foreground, the TEPUI — sheer-sided, flat-topped —
standing on the skyline, and the bright sky notch above.

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
from _props.geometry import (clear_scene, make_box, make_cyl,
                             make_blob, make_taper_cyl, export_glb)

COL_ROCK = (0.42, 0.42, 0.40, 1.0)
COL_ROCK_DK = (0.32, 0.32, 0.31, 1.0)
COL_ROCK_WET = (0.26, 0.27, 0.27, 1.0)
COL_FALL = (0.88, 0.90, 0.90, 1.0)
COL_FALL_CORE = (0.94, 0.96, 0.96, 1.0)
COL_POOL = (0.20, 0.30, 0.30, 1.0)
COL_POOL_DK = (0.14, 0.22, 0.23, 1.0)
COL_FOAM = (0.78, 0.82, 0.80, 1.0)
COL_MIST = (0.72, 0.76, 0.76, 0.45)
COL_GREEN = (0.18, 0.32, 0.18, 1.0)      # dense Canaima green, dark
COL_GREEN_LT = (0.26, 0.42, 0.22, 1.0)
COL_MOSS = (0.24, 0.36, 0.20, 1.0)
COL_TEPUI = (0.46, 0.42, 0.44, 1.0)      # sheer sandstone flank
COL_TEPUI_TOP = (0.30, 0.38, 0.28, 1.0)  # the green table top
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
    """The column, rebuilt (user: "the waterfalls are primitive").
    Real falls WIDEN and BREAK as they drop: five stacked veil
    segments, each wider and slightly forward of the one above, a
    bright core riding inside each, vertical streamers striating
    the face, taper-round side threads, and a bulged lip where the
    water leaves the rim."""
    # Veil segments, lip to plunge — (z_bottom, z_top, width, y)
    segs = [(8.5, 9.5, 2.3, 13.50), (6.5, 8.7, 2.6, 13.46),
            (4.3, 6.7, 3.0, 13.40), (2.1, 4.5, 3.5, 13.30),
            (0.15, 2.3, 4.1, 13.16)]
    for i, (z0, z1, w, y) in enumerate(segs):
        zc, h = (z0 + z1) / 2.0, z1 - z0
        make_box(f"Fall_Veil_{i}", (0.0, y, zc), (w, 0.30, h), COL_FALL)
        make_box(f"Fall_Core_{i}", (0.15 * (1 if i % 2 else -1), y - 0.06, zc),
                 (w * 0.45, 0.20, h * 0.92), COL_FALL_CORE)
    # Vertical streamers striating the veil faces
    for i, (sx, s0, s1) in enumerate(((-1.6, 0.3, 8.8), (-0.9, 0.2, 9.2),
                                      (-0.2, 0.3, 9.4), (0.5, 0.2, 9.0),
                                      (1.1, 0.3, 8.6), (1.7, 0.2, 7.8))):
        zc, h = (s0 + s1) / 2.0, s1 - s0
        col = COL_FALL_CORE if i % 2 == 0 else COL_FALL
        make_box(f"Fall_Streamer_{i}", (sx, 13.06, zc), (0.16, 0.08, h), col)
    # The lip: a bulge of water leaving the rim notch
    make_blob("Fall_Lip", (0.0, 13.55, 9.5), 1.05, COL_FALL,
              noise=0.10, seed=3, squash=0.45)
    # Side threads — thin round columns, broken heights
    make_taper_cyl("Thread_W", (-2.1, 13.35, 4.2), 0.16, 0.10, 5.6, COL_FALL, segments=6)
    make_taper_cyl("Thread_E", (1.9, 13.35, 3.4), 0.13, 0.08, 4.2, COL_FALL, segments=6)
    # Wet streaks on the face flanking the column
    for sx in (-2.6, 2.6):
        make_box(f"Face_Wet_{sx:+.0f}", (sx, 13.38, 4.6), (0.9, 0.06, 8.2),
                 (0.22, 0.23, 0.24, 1.0))


def build_pool():
    make_box("Pool", (0.0, 9.5, 0.02), (9.5, 8.0, 0.06), COL_POOL)
    make_box("Pool_Deep", (0.0, 12.0, 0.03), (6.0, 3.0, 0.05), COL_POOL_DK)
    # Foam ring at the plunge + drift lines
    make_box("Foam_Ring", (0.0, 12.6, 0.07), (3.6, 1.0, 0.03), COL_FOAM)
    make_box("Foam_Drift_0", (-1.6, 10.8, 0.065), (2.2, 0.18, 0.02), COL_FOAM)
    make_box("Foam_Drift_1", (1.4, 9.8, 0.06), (1.7, 0.14, 0.02), COL_FOAM)
    # The plunge: churned foam MOUNDS (soft blobs), not slabs
    make_blob("Foam_Mound", (0.0, 12.6, 0.35), 1.7, COL_FOAM,
              noise=0.18, seed=11, squash=0.38)
    make_blob("Foam_Mound_W", (-1.9, 12.2, 0.2), 0.9, COL_FOAM,
              noise=0.2, seed=12, squash=0.4)
    make_blob("Foam_Mound_E", (1.8, 12.35, 0.22), 1.0, COL_FOAM,
              noise=0.2, seed=13, squash=0.4)
    # Mist: translucent blobs climbing the column base + a low bank
    make_blob("Mist_Lo", (0.0, 12.5, 1.5), 2.2, COL_MIST,
              noise=0.22, seed=21, squash=0.6)
    make_blob("Mist_Hi", (0.4, 12.9, 3.4), 1.5, COL_MIST,
              noise=0.24, seed=22, squash=0.7)
    make_blob("Mist_Bank", (0.0, 11.2, 0.8), 3.0, COL_MIST,
              noise=0.2, seed=23, squash=0.3)


def build_foreground():
    """Wet boulders + the viewing rocks the camera stands on."""
    rocks = [(-2.8, 4.6, 0.55, 1.4), (-0.6, 3.6, 0.40, 1.1), (1.8, 4.9, 0.65, 1.6),
             (3.4, 3.4, 0.35, 0.9), (-4.2, 3.0, 0.45, 1.2), (0.9, 5.8, 0.30, 0.8)]
    for i, (rx, ry, rz, rs) in enumerate(rocks):
        make_box(f"Boulder_{i}", (rx, ry, rz / 2.0 + 0.02), (rs, rs * 0.8, rz),
                 COL_ROCK_WET if i % 2 == 0 else COL_ROCK_DK)
    make_box("Shore", (0.0, 2.2, 0.05), (12.0, 3.4, 0.14), COL_ROCK)
    # Green growth — dense, everywhere the rock lets it hold: rims,
    # ledges, shore, and hanging masses down the gorge walls
    fringe = [(-5.2, 2.5, 0.9), (5.0, 2.8, 0.8), (-4.4, 12.6, 10.1),
              (4.2, 12.6, 10.1), (-6.2, 7.0, 4.3), (6.4, 8.0, 5.4),
              (-5.6, 5.0, 2.2), (5.8, 5.6, 2.6), (-7.0, 10.0, 6.8),
              (7.2, 10.5, 7.4), (-4.8, 8.5, 5.6), (5.2, 11.5, 8.6),
              (-2.6, 13.4, 9.8), (2.4, 13.4, 9.8)]
    for i, (gx, gy, gz) in enumerate(fringe):
        col = COL_GREEN if i % 2 == 0 else COL_GREEN_LT
        make_box(f"Green_{i}", (gx, gy, gz), (2.0, 1.5, 1.2), col)


def build_sky():
    # The tepui on the skyline: sheer flanks, dead-flat green top —
    # the shape that says Canaima and nowhere else
    make_box("Tepui_Flank", (-9.0, 17.2, 8.5), (9.0, 0.8, 7.0), COL_TEPUI)
    make_box("Tepui_Band", (-9.0, 17.1, 6.2), (9.4, 0.7, 1.0), (0.38, 0.34, 0.36, 1.0))
    make_box("Tepui_Top", (-9.0, 17.2, 12.15), (9.6, 1.0, 0.5), COL_TEPUI_TOP)
    # A second, farther table to the east, hazier
    make_box("Tepui_Far", (11.0, 17.6, 7.0), (7.0, 0.6, 5.2), (0.54, 0.52, 0.56, 1.0))
    make_box("Tepui_Far_Top", (11.0, 17.6, 9.75), (7.4, 0.8, 0.4), (0.42, 0.48, 0.42, 1.0))
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)


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
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 25m. The gorge keeps rising —
    rock shoulders stepping back, jungle canopy over them."""
    from _props.detail import make_far_bands
    make_far_bands("FarRidge", COL_ROCK_DK,
                   [(55.0, 60.0, 10.0, 0.88), (115.0, 100.0, 14.0, 0.72),
                    (230.0, 170.0, 18.0, 0.56), (420.0, 280.0, 24.0, 0.42)],
                   profile="ridge")
    make_far_bands("FarCanopy", (0.16, 0.26, 0.16),
                   [(80.0, 80.0, 6.0, 0.85), (170.0, 140.0, 8.0, 0.66),
                    (330.0, 240.0, 10.0, 0.50)], profile="treeline")


if __name__ == "__main__":
    main()
