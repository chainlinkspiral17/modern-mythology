"""small_wood_cemetery — vol2's graveside, Small Wood, Oregon (2026-10-10).

"Later, at the gravesite, the minister says something about roots and
returns. He doesn't know your aunt at all and it shows. Jo stands beside
you. Not touching. Not quite." (vol2_graveyard)

vol2's funeral played on `parish_cemetery`: Graustark's above-ground tomb
city of white limestone vaults, a Louisiana burial form, for an in-ground
funeral on the Oregon coast. That set stays the Tarot Gauntlet's
Judgement board; this is the Small Wood one: a hillside lawn cemetery
ringed by Douglas firs and red cedars, granite uprights in rows and flat
bronze markers between them, the older stones mossed, a family obelisk;
the aunt's open grave under the funeral home's canopy — the green
carpet, the lowering device with the casket on its straps, the dirt
mound under its tarp, two short rows of folding chairs, the flower
sprays on their stands, the minister's lectern; the gravel lane
winding through, the hearse on it; the coastal hills going grey in the
morning mist.

Coordinates: Blender Z-up, the grave at the origin, its head to the N;
the lane comes in from the SE. glTF export -> Godot (x, z, -y).

Draft 2 targets: the mourners as figures with a pose; the hillside's
fall (the lawn is flat); the ocean as a far band past the firs.
"""
import os, sys, math, random
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, make_blob, export_glb
from _props.trees import make_conifer, make_shrub
from _props.detail import make_far_bands, make_traffic_wear
from _props.vehicles import make_car

LAWN = (0.36, 0.46, 0.28, 1.0); LAWN_DK = (0.30, 0.40, 0.24, 1.0)
GRAVEL = (0.56, 0.54, 0.50, 1.0)
GRANITE = (0.52, 0.52, 0.54, 1.0); GRANITE_DK = (0.36, 0.36, 0.38, 1.0)
MOSS = (0.40, 0.48, 0.28, 1.0); BRONZE = (0.48, 0.38, 0.22, 1.0)
FIR = (0.16, 0.26, 0.18, 1.0); CEDAR = (0.20, 0.30, 0.20, 1.0); TRUNK = (0.32, 0.24, 0.18, 1.0)
TENT = (0.24, 0.30, 0.26, 1.0); STEEL = (0.70, 0.72, 0.74, 1.0)
CASKET = (0.42, 0.28, 0.20, 1.0); TURF = (0.24, 0.52, 0.28, 1.0)


def build_ground():
    make_box("Ground", (0.0, 0.0, -0.03), (240.0, 240.0, 0.06), LAWN)
    rnd = random.Random(5)
    for i in range(18):
        make_box(f"Lawn_Patch_{i}", (rnd.uniform(-30, 30), rnd.uniform(-24, 30), 0.001), (rnd.uniform(3, 7), rnd.uniform(3, 7), 0.002), LAWN_DK)
    # the gravel lane: in from the SE, round the section's south edge, out W
    make_traffic_wear("Lane", [(26.0, -22.0), (14.0, -10.5), (2.0, -8.5), (-12.0, -9.5), (-28.0, -6.0)], width=3.2, tint=GRAVEL)


def build_grave():
    """The aunt's grave at the origin, its head to the N."""
    # the green carpet round the opening, the opening, the lowering device, the casket
    make_box("Grave_Carpet", (0.0, 0.0, 0.004), (3.4, 4.4, 0.008), TURF)
    make_box("Grave_Opening", (0.0, 0.0, 0.009), (1.10, 2.50, 0.002), (0.08, 0.07, 0.06, 1.0))
    for i, x in enumerate((-0.68, 0.68)):
        make_box(f"Lowering_Device_Rail_{i}", (x, 0.0, 0.10), (0.10, 2.70, 0.16), STEEL)
    for i, y in enumerate((-1.30, 1.30)):
        make_box(f"Lowering_Device_End_{i}", (0.0, y, 0.10), (1.46, 0.10, 0.16), STEEL)
    for i, y in enumerate((-0.70, 0.0, 0.70)):
        make_box(f"Lowering_Strap_{i}", (0.0, y, 0.19), (1.30, 0.06, 0.02), (0.30, 0.42, 0.30, 1.0))
    make_chamfer_box("Casket", (0.0, 0.0, 0.50), (0.66, 2.10, 0.58), CASKET, chamfer=0.05)
    make_chamfer_box("Casket_Lid", (0.0, 0.0, 0.83), (0.62, 2.04, 0.08), (0.48, 0.32, 0.22, 1.0), chamfer=0.03)
    for i, y in enumerate((-0.70, 0.0, 0.70)):
        for s in (-1, 1):
            make_box(f"Casket_Handle_{i}_{s:+d}", (s * 0.345, y, 0.48), (0.03, 0.30, 0.04), (0.72, 0.62, 0.36, 1.0))
    make_blob("Casket_Spray", (0.0, 0.10, 0.92), 0.30, (0.88, 0.80, 0.84, 1.0), noise=0.3, seed=4, squash=0.45)
    # the dirt mound under its tarp, east of the grave
    make_blob("Dirt_Mound", (3.2, 0.2, 0.47), 1.1, (0.30, 0.26, 0.20, 1.0), noise=0.15, seed=9, squash=0.45)
    make_blob("Dirt_Mound_Tarp", (3.2, 0.2, 0.49), 1.12, (0.26, 0.40, 0.26, 1.0), noise=0.15, seed=9, squash=0.44)
    # the canopy: four poles, the roof, the valance with the funeral home's name
    tx0, tx1, ty0, ty1, th = -2.4, 2.0, -3.8, 2.2, 2.30
    for i, (x, y) in enumerate(((tx0, ty0), (tx1, ty0), (tx0, ty1), (tx1, ty1))):
        make_cyl(f"Tent_Pole_{i}", (x, y, th / 2.0), 0.03, th, STEEL, segments=6)
    make_box("Tent_Roof", ((tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0, th + 0.10), (tx1 - tx0 + 0.20, ty1 - ty0 + 0.20, 0.20), TENT)
    for i, (c, s) in enumerate((((((tx0 + tx1) / 2.0), ty0 - 0.10, th - 0.12), (tx1 - tx0 + 0.20, 0.02, 0.24)),
                                 (((tx0 + tx1) / 2.0, ty1 + 0.10, th - 0.12), (tx1 - tx0 + 0.20, 0.02, 0.24)))):
        make_box(f"Tent_Valance_{i}", c, s, TENT)
    make_box("Tent_Valance_Name", ((tx0 + tx1) / 2.0, ty0 - 0.112, th - 0.12), (1.80, 0.004, 0.08), (0.86, 0.82, 0.70, 1.0))
    # two short rows of folding chairs facing the grave from the south
    for r, y in enumerate((-2.3, -3.1)):
        for c in range(4):
            x = -1.65 + c * 0.62
            make_box(f"Chair_{r}_{c}_Seat", (x, y, 0.45), (0.42, 0.40, 0.03), (0.52, 0.48, 0.42, 1.0))
            make_box(f"Chair_{r}_{c}_Back", (x, y - 0.19, 0.66), (0.42, 0.03, 0.38), (0.52, 0.48, 0.42, 1.0))
            for lx in (-0.18, 0.18):
                for ly in (-0.17, 0.17):
                    make_box(f"Chair_{r}_{c}_Leg_{lx:+.2f}_{ly:+.2f}", (x + lx, y + ly, 0.215), (0.02, 0.02, 0.43), STEEL)
    make_box("Chair_0_1_Program", (-1.03, -2.25, 0.468), (0.14, 0.20, 0.003), (0.94, 0.92, 0.88, 1.0))
    # the flower sprays on their easels flanking the head of the grave
    for i, x in enumerate((-1.5, 1.5)):
        for j, dx in enumerate((-0.25, 0.25)):
            make_rot_box(f"Spray_Easel_{i}_{j}", (x + dx, 1.85, 0.55), (0.03, 0.03, 1.12), (0.36, 0.30, 0.22, 1.0), roll=(0.12 if j else -0.12))
        make_blob(f"Spray_{i}", (x, 1.82, 1.15), 0.42, [(0.92, 0.88, 0.80, 1.0), (0.84, 0.56, 0.60, 1.0)][i], noise=0.35, seed=12 + i, squash=0.75)
    # the minister's lectern at the head
    make_box("Lectern_Post", (0.0, 2.05, 0.55), (0.08, 0.08, 1.10), (0.36, 0.30, 0.22, 1.0))
    make_rot_box("Lectern_Top", (0.0, 1.98, 1.12), (0.46, 0.34, 0.04), (0.42, 0.34, 0.24, 1.0), pitch=0.0, roll=0.0)
    make_box("Lectern_Foot", (0.0, 2.05, 0.02), (0.40, 0.40, 0.04), (0.36, 0.30, 0.22, 1.0))
    make_box("Lectern_Book", (0.0, 1.98, 1.155), (0.22, 0.28, 0.03), (0.16, 0.12, 0.12, 1.0))


def build_stones():
    """Rows of granite uprights with flat bronze markers between them, the
    old ones mossed, a family obelisk."""
    rnd = random.Random(21)
    k = 0
    for row in range(6):
        y = 5.0 + row * 3.2
        for c in range(9):
            x = -14.0 + c * 3.5 + (row % 2) * 1.2 + rnd.uniform(-0.3, 0.3)
            if abs(x) < 3.5 and y < 7.0:
                continue
            kind = rnd.random()
            if kind < 0.55:
                w, h = rnd.uniform(0.6, 1.0), rnd.uniform(0.6, 1.1)
                old = row >= 3 and rnd.random() < 0.6
                make_box(f"Stone_Base_{k}", (x, y, 0.08), (w + 0.16, 0.36, 0.16), GRANITE_DK)
                make_chamfer_box(f"Stone_{k}", (x, y, 0.16 + h / 2.0), (w, 0.16, h), GRANITE if not old else (0.60, 0.60, 0.56, 1.0), chamfer=0.04)
                make_box(f"Stone_{k}_Inscription", (x, y - 0.082, 0.16 + h * 0.62), (w * 0.6, 0.002, h * 0.22), GRANITE_DK)
                if old:
                    make_blob(f"Stone_{k}_Moss", (x, y, 0.16 + h), w * 0.32, MOSS, noise=0.3, seed=k, squash=0.35)
            else:
                make_box(f"Marker_Flat_{k}", (x, y, 0.012), (0.70, 0.40, 0.024), BRONZE)
                make_box(f"Marker_Flat_{k}_Plate", (x, y, 0.026), (0.56, 0.28, 0.004), (0.58, 0.48, 0.30, 1.0))
            k += 1
    # in the near rows south of the grave
    for c, x in enumerate((-9.0, -5.5, 5.5, 9.0, 12.0)):
        make_box(f"Stone_S_Base_{c}", (x, -5.0, 0.08), (0.96, 0.36, 0.16), GRANITE_DK)
        make_chamfer_box(f"Stone_S_{c}", (x, -5.0, 0.56), (0.80, 0.16, 0.80), GRANITE, chamfer=0.04)
    make_box("Obelisk_Base", (-7.5, 9.0, 0.25), (1.2, 1.2, 0.50), GRANITE_DK)
    make_box("Obelisk_Plinth", (-7.5, 9.0, 0.70), (0.80, 0.80, 0.40), GRANITE)
    make_lathe("Obelisk_Shaft", (-7.5, 9.0, 0.90), [(0.30, 0.0), (0.18, 2.6), (0.0, 2.9)], GRANITE, segments=4)


def build_setting():
    """The firs and cedars round the section, the shrubs, the hearse on the
    lane, the hills going grey."""
    rnd = random.Random(33)
    ring = []
    tries = 0
    while len(ring) < 18 and tries < 2000:      # a loose ring, no two crowns within 16 m
        tries += 1
        a = rnd.uniform(0.0, 2.0 * math.pi)
        r = rnd.uniform(30.0, 50.0)
        p = (r * math.cos(a), r * math.sin(a) + 4.0)
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 16.0 ** 2 for q in ring):
            ring.append(p)
    for i, (x, y) in enumerate(ring):
        make_conifer(f"Fir_{i}", x, y, rnd.uniform(14.0, 22.0), FIR if i % 3 else CEDAR, TRUNK)
    for i, (x, y) in enumerate(((-10.0, -2.0), (11.0, 3.0), (-16.0, 14.0), (15.0, 18.0))):
        make_conifer(f"Cedar_Near_{i}", x, y, rnd.uniform(9.0, 13.0), CEDAR, TRUNK)
    for i, (x, y) in enumerate(((-4.5, -6.4), (6.0, -6.2), (-12.5, 4.0))):
        make_shrub(f"Shrub_{i}", x, y, h=0.9, r=0.6, col=(0.24, 0.36, 0.22, 1.0))
    make_car("Hearse", 9.6, -10.0, 5.6, (0.08, 0.08, 0.09, 1.0), along="X", z0=0.0)
    make_far_bands("FarHills", (0.30, 0.36, 0.32), [(70.0, 120.0, 12.0, 0.72), (130.0, 200.0, 20.0, 0.52), (240.0, 320.0, 30.0, 0.40)],
                   cx=0.0, cy=4.0, profile="treeline")


def main():
    clear_scene()
    build_ground(); build_grave(); build_stones(); build_setting()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/small_wood_cemetery.glb"))
    print(f"\n[build_small_wood_cemetery] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
