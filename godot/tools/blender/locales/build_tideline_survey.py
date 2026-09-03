"""tideline_survey — the basalt headland inside the stick, two pools.
vol7 ch18 (Tideline Survey), re-homed off cabin_road (2026-09-03).

"Finn was at a tide pool. The tide pool on a basalt headland —
rendered by a designer who had been at the Oregon coast. The pool the
size of a kitchen table. The basalt around it: the wear of a thing wet
at every high tide for millennia. The pool was clear. A sea anemone
open at one corner, a green shore crab in the other corner, two
purple sea stars on the wall, a hermit crab in a turban shell on the
bottom." The notebook in the wax canvas coat, Brandon's careful
handwriting. "The path to the second pool visible in the basalt — a
slight wear in the rock from the boots of people who had walked it.
Worn into the substrate by the players." "The second pool. Bigger
than the first. The size of a dining table. Clear water." The old man
in waders kneeling at its edge (cast). "At the bottom — a thing. The
size of his thumb. Cedar. A figure carved on it." "The fog at the
inland side ... The horizon at sea was the gray-white of a Pacific
horizon in late summer."

The pools are HOLES: the shelf is a 5x5 grid of basalt cells with two
cells left out, each hole floored below and skinned with a thin water
surface, the creatures on the floor under the surface (nothing sits
inside the water box, so nothing clips).

Coordinate frame: Blender Z-up. Headland shelf top at z 1.2, sea at
z 0. First pool centered (-2, -3); second pool (9, 6). Inland (fog)
is north, +y. glTF export remaps to Godot (x, z, -y). Two scenes share
this glb: tideline_survey.tscn (first pool) and
tideline_survey_second.tscn (second pool) — one marker set each, so
[shot:insert tide_pool] frames the right pool from either preset.

DRAFT 1 (2026-09-03): the sea, the shelf, the two pools with their
creatures, the cedar at the bottom of the second, the worn path, the
knee-wear at the second pool's edge, Finn's sitting wear at the first,
the notebook + pencil on the basalt, survey stakes + string, mussel
beds and kelp wrack at the shelf edge, foam lines, boulders, a gull,
the fog bank inland, the far ridge, the gray-white horizon.
Draft 2 targets: the players' boot-wear as a proper polished channel
(a shallow wedge), the second pool's edge where the old man kneels
worn to a different color, the crow (Finn's — he came here without
it), wave motion on the foam lines via mood.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_dome, export_glb
from _props.detail import make_far_bands
from _props.creatures import make_crow

BASALT = (0.20, 0.20, 0.22, 1.0)
BASALT_LT = (0.26, 0.26, 0.27, 1.0)
BASALT_WET = (0.14, 0.15, 0.17, 1.0)
WEAR = (0.31, 0.31, 0.32, 1.0)
SEA = (0.30, 0.38, 0.42, 1.0)
SEA_FOAM = (0.80, 0.84, 0.84, 1.0)
POOL_WATER = (0.40, 0.56, 0.60, 0.45)
POOL_FLOOR = (0.24, 0.28, 0.26, 1.0)
FOG = (0.82, 0.84, 0.85, 0.55)
HORIZON = (0.78, 0.80, 0.80, 1.0)

Z_TOP = 1.2
# grid lines: x cols and y rows; holes at (row 1, col 1) = pool 1 and (row 3, col 3) = pool 2
XS = (-20.0, -3.2, -0.8, 7.6, 10.4, 20.0)
YS = (-15.0, -4.2, -1.8, 4.6, 7.4, 15.0)
HOLES = {(1, 1), (3, 3)}
P1 = (-2.0, -3.0)
P2 = (9.0, 6.0)


def build_sea_and_shelf():
    make_box("Ground_Far", (0.0, 0.0, -0.10), (700.0, 700.0, 0.02), (0.24, 0.30, 0.34, 1.0))
    make_box("Sea", (0.0, 0.0, -0.025), (400.0, 400.0, 0.05), SEA)
    for r in range(5):
        for c in range(5):
            if (r, c) in HOLES:
                continue
            x0, x1 = XS[c], XS[c + 1]
            y0, y1 = YS[r], YS[r + 1]
            make_box(f"Basalt_Cell_{r}_{c}", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, Z_TOP / 2.0),
                     (x1 - x0, y1 - y0, Z_TOP), BASALT if (r + c) % 2 else BASALT_LT)
    # the shelf's seaward faces are wet and darker: skins on the S, E, W faces
    make_box("Shelf_Face_S", (0.0, -15.02, 0.55), (40.0, 0.04, 1.10), BASALT_WET)
    make_box("Shelf_Face_E", (20.02, 0.0, 0.55), (0.04, 30.0, 1.10), BASALT_WET)
    make_box("Shelf_Face_W", (-20.02, 0.0, 0.55), (0.04, 30.0, 1.10), BASALT_WET)
    # foam lines where the swell meets the shelf
    for i, (x, y, w, d) in enumerate(((0.0, -15.6, 36.0, 0.5), (20.6, 0.0, 0.5, 26.0), (-20.6, 0.0, 0.5, 26.0),
                                      (4.0, -16.6, 22.0, 0.3), (-8.0, -17.4, 14.0, 0.25))):
        make_box(f"Foam_Line_{i}", (x, y, 0.012), (w, d, 0.024), SEA_FOAM)
    # boulders, mussel beds and kelp wrack along the seaward edge
    for i, (x, y, r, s) in enumerate(((-16.0, -12.0, 1.1, 3), (-9.0, -13.5, 0.8, 4), (6.0, -13.0, 1.3, 5), (15.0, -11.5, 0.9, 6),
                                      (17.5, 2.0, 1.0, 7), (-17.0, 6.0, 1.2, 8), (12.0, 12.5, 0.9, 9))):
        make_blob(f"Boulder_{i}", (x, y, Z_TOP + r * 1.06), r, BASALT_LT, noise=0.26, seed=s, squash=0.7)
    for i, (x, y) in enumerate(((-13.0, -14.2), (-5.0, -14.4), (2.0, -14.3), (10.0, -14.1), (19.2, -6.0), (19.3, 4.0))):
        make_box(f"Mussel_Bed_{i}", (x, y, Z_TOP + 0.03), (2.6, 0.9, 0.06), (0.10, 0.10, 0.16, 1.0))
    for i, (x, y) in enumerate(((-11.0, -13.2), (1.5, -13.6), (16.5, -10.0))):
        make_box(f"Kelp_Wrack_{i}", (x, y, Z_TOP + 0.03), (1.8, 0.35, 0.06), (0.30, 0.26, 0.14, 1.0))
        make_blob(f"Kelp_Bulb_{i}", (x + 1.05, y, Z_TOP + 0.14), 0.10, (0.36, 0.30, 0.14, 1.0), noise=0.2, seed=20 + i, squash=0.8)
    # cracks in the basalt
    for i, (x, y, w, d) in enumerate(((-6.0, 2.0, 5.0, 0.05), (3.0, -8.0, 0.05, 6.0), (13.0, -2.0, 4.0, 0.05), (-12.0, -6.0, 0.05, 5.0))):
        make_box(f"Basalt_Crack_{i}", (x, y, Z_TOP + 0.001), (w, d, 0.002), BASALT_WET)


def build_pool(prefix, r, c, floor_z, water_z):
    x0, x1 = XS[c], XS[c + 1]
    y0, y1 = YS[r], YS[r + 1]
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    w, d = x1 - x0, y1 - y0
    make_box(f"{prefix}_Floor", (cx, cy, floor_z / 2.0), (w, d, floor_z), POOL_FLOOR)
    make_box(f"{prefix}_Water", (cx, cy, water_z - 0.006), (w, d, 0.012), POOL_WATER)
    for nm, (rx, ry, rw, rd) in (("S", (cx, y0 - 0.15, w + 0.6, 0.3)), ("N", (cx, y1 + 0.15, w + 0.6, 0.3)),
                                 ("W", (x0 - 0.15, cy, 0.3, d)), ("E", (x1 + 0.15, cy, 0.3, d))):
        make_box(f"{prefix}_Rim_Wear_{nm}", (rx, ry, Z_TOP + 0.0015), (rw, rd, 0.003), WEAR)
    return cx, cy, floor_z


def build_first_pool():
    """Kitchen-table size. Anemone at one corner, the green shore crab in
    the other, two purple sea stars on the wall, a hermit crab in a
    turban shell on the bottom. Finn sits here to read the notebook."""
    cx, cy, fz = build_pool("Tide_Pool", 1, 1, 0.75, 1.10)
    make_dome("Anemone", (cx - 0.85, cy - 0.85, fz), 0.12, (0.62, 0.42, 0.50, 1.0), rings=3, segments=10)
    for ti in range(8):
        a = ti * math.pi / 4.0
        make_cyl(f"Anemone_Tentacle_{ti}", (cx - 0.85 + 0.15 * math.cos(a), cy - 0.85 + 0.15 * math.sin(a), fz + 0.03),
                 0.012, 0.06, (0.72, 0.54, 0.58, 1.0), segments=5)
    make_box("Shore_Crab", (cx + 0.8, cy + 0.85, fz + 0.03), (0.14, 0.10, 0.06), (0.30, 0.44, 0.26, 1.0))
    for ci, sgn in enumerate((-1, 1)):
        make_box(f"Shore_Crab_Claw_{ci}", (cx + 0.8 + sgn * 0.10, cy + 0.93, fz + 0.03), (0.05, 0.04, 0.03), (0.30, 0.44, 0.26, 1.0))
    # sea stars on the wall: five-segment discs against the east and north faces
    make_cyl("Sea_Star_0", (XS[2] - 0.006, cy + 0.3, fz + 0.18), 0.09, 0.012, (0.42, 0.20, 0.50, 1.0), axis="X", segments=5)
    make_cyl("Sea_Star_1", (cx - 0.4, YS[2] - 0.006, fz + 0.26), 0.08, 0.012, (0.46, 0.22, 0.54, 1.0), axis="Y", segments=5)
    make_dome("Hermit_Crab_Shell", (cx + 0.15, cy - 0.5, fz), 0.055, (0.62, 0.50, 0.34, 1.0), rings=3, segments=10)
    make_cyl("Hermit_Crab_Shell_Spire", (cx + 0.15, cy - 0.5, fz + 0.065), 0.02, 0.02, (0.54, 0.42, 0.28, 1.0), segments=6)
    make_box("Hermit_Crab_Legs", (cx + 0.15, cy - 0.42, fz + 0.01), (0.08, 0.04, 0.02), (0.60, 0.36, 0.24, 1.0))
    for i in range(4):
        make_blob(f"Pool_Pebble_{i}", (cx - 0.5 + i * 0.35, cy + 0.2 - (i % 2) * 0.5, fz + 0.05), 0.04,
                  (0.34, 0.34, 0.32, 1.0), noise=0.2, seed=30 + i, squash=0.7)
    # Finn's seat on the basalt at the south edge, the notebook and pencil beside it
    make_box("Finn_Sit_Wear", (cx - 0.3, YS[1] - 0.45, Z_TOP + 0.0035), (0.70, 0.50, 0.001), (0.34, 0.34, 0.35, 1.0))
    make_box("Notebook", (cx + 0.75, YS[1] - 0.55, Z_TOP + 0.006), (0.10, 0.14, 0.012), (0.36, 0.26, 0.18, 1.0))
    make_box("Notebook_Page", (cx + 0.75, YS[1] - 0.55, Z_TOP + 0.013), (0.09, 0.13, 0.002), (0.94, 0.92, 0.86, 1.0))
    make_box("Notebook_Handwriting", (cx + 0.75, YS[1] - 0.545, Z_TOP + 0.0145), (0.06, 0.09, 0.001), (0.36, 0.34, 0.40, 1.0))
    make_cyl("Pencil", (cx + 0.90, YS[1] - 0.55, Z_TOP + 0.004), 0.004, 0.16, (0.80, 0.62, 0.24, 1.0), axis="Y", segments=6)


def build_second_pool():
    """Dining-table size. The old man kneels at its west edge (cast).
    At the bottom, the cedar: a hand, open, palm up, holding a bell."""
    cx, cy, fz = build_pool("Second_Pool", 3, 3, 0.65, 1.10)
    make_box("Cedar", (cx + 0.2, cy - 0.3, fz + 0.012), (0.06, 0.03, 0.024), (0.60, 0.42, 0.26, 1.0))
    make_box("Cedar_Hand_Figure", (cx + 0.2, cy - 0.3, fz + 0.0255), (0.04, 0.018, 0.003), (0.72, 0.54, 0.34, 1.0))
    make_cyl("Cedar_Bell", (cx + 0.205, cy - 0.3, fz + 0.029), 0.005, 0.004, (0.80, 0.66, 0.40, 1.0), segments=6)
    for i in range(6):
        make_blob(f"Second_Pool_Pebble_{i}", (cx - 1.0 + i * 0.4, cy + 0.6 - (i % 3) * 0.55, fz + 0.055), 0.045,
                  (0.32, 0.33, 0.31, 1.0), noise=0.2, seed=40 + i, squash=0.7)
    # where the old man has knelt since 2023: two knee hollows worn into the west rim
    for ki, dy in enumerate((-0.18, 0.18)):
        make_box(f"Waders_Knee_Wear_{ki}", (XS[3] - 0.35, cy + dy, Z_TOP + 0.0035), (0.30, 0.22, 0.001), (0.36, 0.36, 0.37, 1.0))
    make_box("Second_Pool_Sit_Wear", (XS[3] - 1.1, cy, Z_TOP + 0.0035), (0.60, 0.80, 0.001), (0.33, 0.33, 0.34, 1.0))


def build_path_and_survey():
    """The players' path from the first pool to the second, worn into
    the basalt; the survey stakes with their string."""
    segs = ((0.6, -3.0, 2.8, 0.45), (2.0, -1.0, 0.45, 4.4), (4.2, 1.2, 4.4, 0.45), (6.4, 3.4, 0.45, 4.4))
    for i, (x, y, w, d) in enumerate(segs):
        make_box(f"Path_Wear_{i}", (x, y, Z_TOP + 0.0055), (w, d, 0.001), WEAR)
    for i in range(5):
        x = -8.0 + i * 3.0
        make_box(f"Survey_Stake_{i}", (x, 9.0, Z_TOP + 0.35), (0.03, 0.03, 0.70), (0.90, 0.52, 0.18, 1.0))
        make_box(f"Survey_Stake_{i}_Flag", (x + 0.045, 9.0, Z_TOP + 0.66), (0.06, 0.01, 0.05), (0.96, 0.40, 0.30, 1.0))
    make_box("Survey_String", (-2.0, 9.0, Z_TOP + 0.703), (12.0, 0.006, 0.006), (0.86, 0.84, 0.76, 1.0))
    make_crow("Gull", -14.5, 3.0, Z_TOP, facing=-1.0, scale=1.1, perched=True)


def build_fog_and_horizon():
    """Fog at the inland side; the gray-white Pacific horizon at sea."""
    for i, (x, y, r, s) in enumerate(((-16.0, 27.0, 6.0, 51), (-6.0, 29.0, 7.0, 52), (5.0, 28.0, 6.5, 53),
                                      (15.0, 30.0, 7.5, 54), (24.0, 27.0, 6.0, 55), (-25.0, 29.0, 6.5, 56))):
        make_blob(f"Fog_Bank_{i}", (x, y, 3.4 + r * 0.35), r, FOG, noise=0.18, seed=s, squash=0.45)
    make_far_bands("FarRidge", (0.30, 0.34, 0.32),
                   [(60.0, 90.0, 9.0, 0.80), (120.0, 150.0, 12.0, 0.62), (240.0, 260.0, 16.0, 0.48)],
                   sides="N", cx=0.0, cy=10.0, profile="ridge")
    for side, (x, y, w, d) in (("S", (0.0, -300.0, 700.0, 30.0)), ("E", (300.0, 0.0, 30.0, 700.0)), ("W", (-300.0, 0.0, 30.0, 700.0))):
        make_box(f"Horizon_Haze_{side}", (x, y, 1.0), (w, d, 2.0), HORIZON)


def main():
    clear_scene()
    build_sea_and_shelf()
    build_first_pool()
    build_second_pool()
    build_path_and_survey()
    build_fog_and_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/tideline_survey.glb"))
    print(f"\n[build_tideline_survey] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
