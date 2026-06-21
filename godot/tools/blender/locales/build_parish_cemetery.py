"""XX · JUDGEMENT — Graustark Parish Cemetery (above-ground). A
tomb city of 40-60 raised concrete vaults arranged on a grid of
narrow walkways, single large central mausoleum, all WHITE-bleached
limestone. Open sky, a few wrought-iron lampposts, low-cropped
grass between the rows. The dust-notes ensemble beat — everyone
stays.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_GRASS = (0.42, 0.46, 0.32, 1.0); COL_GRASS_PATH = (0.62, 0.56, 0.42, 1.0)
COL_VAULT_WHITE = (0.92, 0.88, 0.82, 1.0); COL_VAULT_SHADOW = (0.62, 0.56, 0.50, 1.0)
COL_MAUSOLEUM = (0.86, 0.82, 0.74, 1.0); COL_MAUSOLEUM_DOOR = (0.32, 0.30, 0.28, 1.0)
COL_BRASS = (0.74, 0.56, 0.28, 1.0); COL_IRON = (0.18, 0.18, 0.18, 1.0)
COL_LAMP_GLOW = (0.96, 0.86, 0.42, 1.0); COL_GATE = (0.22, 0.20, 0.20, 1.0)
COL_SKY = (0.78, 0.82, 0.84, 1.0); COL_OAK_TRUNK = (0.42, 0.30, 0.22, 1.0)
COL_OAK_FOLIAGE = (0.42, 0.52, 0.32, 1.0); COL_MOSS = (0.42, 0.50, 0.34, 1.0)

LOT_W = 24.0; LOT_D = 18.0


def build_ground():
    # Grass field
    make_box("Ground_Grass", (0.0, 0.0, 0.0), (LOT_W + 4.0, LOT_D + 4.0, 0.04), COL_GRASS)
    # Sky dome
    for sx, sy in [(0.0, LOT_D), (0.0, -LOT_D), (LOT_W, 0.0), (-LOT_W, 0.0)]:
        if sy != 0:
            make_box(f"Sky_NS_{sy:+.0f}", (sx, sy + (LOT_D if sy>0 else -LOT_D)*0.6, 8.0),
                     (60.0, 0.04, 16.0), COL_SKY)
        else:
            make_box(f"Sky_EW_{sx:+.0f}", (sx + (LOT_W if sx>0 else -LOT_W)*0.6, sy, 8.0),
                     (0.04, 60.0, 16.0), COL_SKY)


def build_paths():
    # Central N-S spine + three E-W cross paths
    make_box("Path_Spine", (0.0, 0.0, 0.02), (1.40, LOT_D, 0.04), COL_GRASS_PATH)
    for cy in [-5.0, 0.0, +5.0]:
        if cy == 0.0:  # already covered by spine center
            continue
        make_box(f"Path_X_{cy:+.0f}", (0.0, cy, 0.02), (LOT_W - 2.0, 1.20, 0.04), COL_GRASS_PATH)
    # Central plaza around the mausoleum
    make_cyl("Plaza", (0.0, 0.0, 0.025), 2.40, 0.005, COL_GRASS_PATH, segments=20)


def build_vaults():
    # Grid of vaults around the central mausoleum. Avoid the central plaza.
    rows_x = [-9.0, -7.0, -5.0, +5.0, +7.0, +9.0]
    rows_y = [-7.5, -5.5, -3.5, -1.5, +1.5, +3.5, +5.5, +7.5]
    vi = 0
    for vx in rows_x:
        for vy in rows_y:
            # Vary vault size slightly so they don't all look identical
            sz_x = 1.60 if (vi % 3) == 0 else 1.20
            sz_y = 0.80
            sz_z = 1.40 if (vi % 4) == 1 else 1.20
            vc = COL_VAULT_WHITE if (vi % 5) != 0 else COL_VAULT_SHADOW
            make_box(f"Vault_{vi}_Base", (vx, vy, sz_z/2.0 + 0.10),
                     (sz_x, sz_y, sz_z), vc)
            # Cap on top
            make_box(f"Vault_{vi}_Cap", (vx, vy, sz_z + 0.16),
                     (sz_x + 0.10, sz_y + 0.10, 0.12), COL_VAULT_SHADOW)
            # Cross on top for ~ 1 in 6
            if vi % 6 == 0:
                make_box(f"Vault_{vi}_Cross_V", (vx, vy, sz_z + 0.50),
                         (0.06, 0.06, 0.40), COL_BRASS)
                make_box(f"Vault_{vi}_Cross_H", (vx, vy, sz_z + 0.56),
                         (0.30, 0.06, 0.06), COL_BRASS)
            # Plaque on the S face
            make_box(f"Vault_{vi}_Plaque", (vx, vy - sz_y/2.0 - 0.01, sz_z*0.6 + 0.10),
                     (sz_x*0.7, 0.005, 0.30), (0.32, 0.30, 0.28, 1.0))
            vi += 1


def build_central_mausoleum():
    # Slightly larger and taller — 2.40m wide, 4.0m deep, 3.20m tall
    mx, my = 0.0, 0.0
    make_box("Mauso_Base", (mx, my, 0.10), (3.20, 4.80, 0.20), COL_MAUSOLEUM)
    make_box("Mauso_Body", (mx, my, 1.80), (2.80, 4.40, 3.20), COL_MAUSOLEUM)
    make_box("Mauso_Cornice", (mx, my, 3.50), (3.20, 4.80, 0.20), COL_VAULT_SHADOW)
    # Two columns flanking the door (S face)
    for sgn in (-1, +1):
        make_cyl(f"Mauso_Col_{sgn:+d}", (mx + sgn*0.90, my - 2.10, 1.60),
                 0.20, 3.20, COL_MAUSOLEUM, segments=12)
    # Door (closed, bronze)
    make_box("Mauso_Door", (mx, my - 2.21, 1.40), (1.20, 0.04, 2.40), COL_MAUSOLEUM_DOOR)
    # Door handle ring
    make_cyl("Mauso_Handle", (mx, my - 2.23, 1.40), 0.10, 0.04, COL_BRASS, axis='Y', segments=10)
    # Lintel inscription plaque
    make_box("Mauso_Inscription", (mx, my - 2.23, 2.80), (1.40, 0.02, 0.30), COL_BRASS)
    # Stepped roof — small pediment + pyramid spire
    make_box("Mauso_Pediment", (mx, my, 3.80), (3.00, 4.60, 0.30), COL_VAULT_SHADOW)
    make_box("Mauso_Cap", (mx, my, 4.30), (1.80, 1.80, 0.40), COL_MAUSOLEUM)
    make_box("Mauso_Spire", (mx, my, 4.80), (0.40, 0.40, 0.80), COL_VAULT_SHADOW)
    # Cross atop
    make_box("Mauso_Cross_V", (mx, my, 5.40), (0.06, 0.06, 0.40), COL_BRASS)
    make_box("Mauso_Cross_H", (mx, my, 5.50), (0.30, 0.06, 0.06), COL_BRASS)


def build_iron_lampposts():
    # 6 wrought-iron lampposts along the spine
    for li, ly in enumerate([-8.0, -5.0, -2.0, +2.0, +5.0, +8.0]):
        lx = +1.20 if li % 2 == 0 else -1.20
        make_cyl(f"Lamp_Post_{li}", (lx, ly, 1.50), 0.06, 3.00, COL_IRON, segments=8)
        make_box(f"Lamp_Top_Bracket_{li}", (lx, ly, 3.10), (0.40, 0.10, 0.10), COL_IRON)
        # Lantern (small box + glow)
        make_box(f"Lamp_Lantern_{li}", (lx + 0.16, ly, 2.90), (0.20, 0.20, 0.30), COL_IRON)
        make_box(f"Lamp_Glow_{li}", (lx + 0.16, ly, 2.90),
                 (0.16, 0.16, 0.26), COL_LAMP_GLOW)


def build_perimeter_iron_fence_and_gate():
    # Iron fence S edge with central gate
    fence_y = -LOT_D/2.0
    for bi in range(40):
        bx = -LOT_W/2.0 + 0.4 + bi * 0.60
        if abs(bx) < 1.40:
            continue  # gate opening
        make_cyl(f"Fence_Baluster_{bi}", (bx, fence_y, 1.00), 0.025, 2.00,
                 COL_IRON, segments=6)
    # Top rail
    make_box("Fence_TopRail_W", (-(LOT_W/4.0 + 0.8), fence_y, 2.00),
             (LOT_W/2.0 - 1.6, 0.06, 0.06), COL_IRON)
    make_box("Fence_TopRail_E", (+(LOT_W/4.0 + 0.8), fence_y, 2.00),
             (LOT_W/2.0 - 1.6, 0.06, 0.06), COL_IRON)
    # Bottom rail
    make_box("Fence_BotRail_W", (-(LOT_W/4.0 + 0.8), fence_y, 0.10),
             (LOT_W/2.0 - 1.6, 0.06, 0.06), COL_IRON)
    make_box("Fence_BotRail_E", (+(LOT_W/4.0 + 0.8), fence_y, 0.10),
             (LOT_W/2.0 - 1.6, 0.06, 0.06), COL_IRON)
    # Gate piers
    for sgn in (-1, +1):
        make_box(f"GatePier_{sgn:+d}", (sgn*1.50, fence_y, 1.50),
                 (0.40, 0.40, 3.00), COL_MAUSOLEUM)
        # Ball atop pier
        make_cyl(f"GatePier_Ball_{sgn:+d}", (sgn*1.50, fence_y, 3.20),
                 0.20, 0.20, COL_VAULT_SHADOW, segments=10)
    # Gate leaves (half-open)
    make_box("Gate_Leaf_W", (-1.00, fence_y - 0.40, 1.00),
             (0.04, 0.80, 2.00), COL_GATE)
    make_box("Gate_Leaf_E", (+1.00, fence_y - 0.40, 1.00),
             (0.04, 0.80, 2.00), COL_GATE)


def build_oaks_and_moss():
    # 3 oaks scattered through the rows
    for oi, (ox, oy) in enumerate([(-8.5, -8.0), (+8.5, +6.0), (-3.0, +8.0)]):
        make_cyl(f"Oak_{oi}_Trunk", (ox, oy, 2.50), 0.40, 5.00, COL_OAK_TRUNK, segments=10)
        for fi, (fdx, fdy, fdz) in enumerate([(0.0, 0.0, 5.50), (0.6, 0.3, 5.80),
                                                (-0.4, -0.5, 5.60)]):
            make_cyl(f"Oak_{oi}_Foliage_{fi}", (ox+fdx, oy+fdy, fdz),
                     1.40, 1.20, COL_OAK_FOLIAGE, segments=10)
    # Moss patches on a few vault caps
    for mi, (mx, my) in enumerate([(-5.0, +1.5), (+7.0, -3.5), (-7.0, +5.5)]):
        make_box(f"Moss_{mi}", (mx, my, 1.36), (1.10, 0.70, 0.04), COL_MOSS)


def main():
    clear_scene()
    build_ground()
    build_paths()
    build_vaults()
    build_central_mausoleum()
    build_iron_lampposts()
    build_perimeter_iron_fence_and_gate()
    build_oaks_and_moss()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/parish_cemetery.glb"))
    print(f"\n[build_parish_cemetery] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
