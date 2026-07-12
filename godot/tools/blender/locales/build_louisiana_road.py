"""VOL 5 · Louisiana Road — outdoor cameo. Two-lane blacktop
through swamp/woodland: cypress trees with Spanish moss, road
shoulder, mile markers, distant gas-station sign.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_ASPHALT = (0.16, 0.16, 0.18, 1.0); COL_LANE_LINE = (0.96, 0.92, 0.62, 1.0)
COL_GRASS = (0.42, 0.46, 0.30, 1.0); COL_DIRT_SHOULDER = (0.42, 0.32, 0.22, 1.0)
COL_CYPRESS_TRUNK = (0.32, 0.22, 0.16, 1.0); COL_CYPRESS_FOLIAGE = (0.32, 0.42, 0.30, 1.0)
COL_SPANISH_MOSS = (0.62, 0.58, 0.42, 1.0)
COL_SWAMP_WATER = (0.18, 0.24, 0.18, 0.65); COL_LILY = (0.32, 0.42, 0.30, 1.0)
COL_MILE_MARKER = (0.78, 0.84, 0.62, 1.0); COL_SIGN_RED = (0.74, 0.28, 0.20, 1.0)
COL_SKY = (0.62, 0.74, 0.78, 1.0)


def build_road():
    # Road runs N-S along Y axis. Half-width 2m.
    # Asphalt
    make_box("Asphalt", (0.0, 6.0, 0.0), (4.0, 24.0, 0.04), COL_ASPHALT)
    # Center yellow dashed line
    for di in range(11):
        dy = -5.0 + di*1.40
        make_box(f"CenterLine_{di}", (0.0, dy, 0.022), (0.10, 0.60, 0.005), COL_LANE_LINE)
    # White edge lines
    for sgn in (-1, +1):
        make_box(f"EdgeLine_{sgn:+d}", (sgn*1.85, 6.0, 0.022), (0.06, 24.0, 0.005), (0.92, 0.92, 0.86, 1.0))
    # Dirt shoulders
    for sgn in (-1, +1):
        make_box(f"Shoulder_{sgn:+d}", (sgn*2.50, 6.0, 0.02), (0.80, 24.0, 0.04), COL_DIRT_SHOULDER)


def build_grass_and_swamp():
    # Grass strips west of west shoulder; swamp east of east shoulder
    make_box("Grass_W", (-5.50, 6.0, 0.02), (4.60, 24.0, 0.04), COL_GRASS)
    make_box("Grass_E", (+5.50, 6.0, 0.02), (4.60, 24.0, 0.04), COL_GRASS)
    # Swamp water patches east
    for wi, (wx, wy) in enumerate([(7.5, 2.0), (8.5, 5.0), (7.5, 9.0), (8.0, 13.0)]):
        make_cyl(f"SwampWater_{wi}", (wx, wy, 0.024), 1.20, 0.006, COL_SWAMP_WATER, segments=12)
        # Lily pads
        for li in range(3):
            ang = li * 2.094
            lx = wx + math.cos(ang) * 0.40
            ly = wy + math.sin(ang) * 0.40
            make_cyl(f"Lily_{wi}_{li}", (lx, ly, 0.030), 0.20, 0.005, COL_LILY, segments=8)


def build_cypress_trees():
    # Cypress trees east + west of road, varying distances + heights
    positions = [
        (-8.5, 1.0, 6.5), (-9.0, 4.5, 7.0), (-7.5, 8.0, 5.8),
        (-9.5, 11.5, 6.8), (-8.0, 15.0, 7.2), (-9.0, 18.0, 6.0),
        (+9.0, 2.0, 7.0), (+9.5, 6.0, 6.5), (+9.0, 10.5, 7.5),
        (+9.5, 14.0, 6.0), (+10.5, 17.0, 6.5),
    ]
    for ti, (tx, ty, th) in enumerate(positions):
        # Trunk (buttressed base wider than top)
        make_cyl(f"Cypress_{ti}_TrunkBase", (tx, ty, 0.50), 0.60, 1.00, COL_CYPRESS_TRUNK, segments=10)
        make_cyl(f"Cypress_{ti}_Trunk", (tx, ty, th/2.0 + 1.0), 0.30, th, COL_CYPRESS_TRUNK, segments=10)
        # Foliage clusters (3 stacked)
        for fi in range(3):
            fr = 1.40 - fi*0.30
            fz = th + 1.0 + fi*0.80
            make_cyl(f"Cypress_{ti}_Foliage_{fi}", (tx, ty, fz), fr, 1.20, COL_CYPRESS_FOLIAGE, segments=10)
        # Spanish moss strands hanging
        for mi in range(3):
            mx = tx + (mi - 1) * 0.30
            mz = th + 0.8
            make_box(f"Cypress_{ti}_Moss_{mi}", (mx, ty, mz - 0.80), (0.04, 0.04, 1.20), COL_SPANISH_MOSS)


def build_signs_and_markers():
    # Mile-marker reflectors along edge
    for mi in range(6):
        my = -2.0 + mi*3.5
        make_box(f"Marker_W_{mi}_Post", (-2.80, my, 0.40), (0.04, 0.04, 0.80), COL_MILE_MARKER)
        make_box(f"Marker_W_{mi}_Reflector", (-2.80, my, 0.70), (0.06, 0.04, 0.10), (0.96, 0.62, 0.20, 1.0))
    # Distant gas-station sign (north end of road)
    sx, sy = +2.0, 20.0
    make_cyl("GasSign_Pole", (sx, sy, 2.50), 0.10, 5.00, P.METAL_STEEL)
    make_box("GasSign_BG", (sx, sy, 5.30), (1.20, 0.10, 0.80), COL_SIGN_RED)
    make_box("GasSign_Letters", (sx-0.06, sy, 5.30), (0.005, 1.00, 0.30), P.PAPER)
    # Stop-ahead sign south
    sx2, sy2 = -2.50, -3.5
    make_cyl("StopSign_Pole", (sx2, sy2, 1.20), 0.04, 2.40, P.METAL_STEEL)
    make_box("StopSign_Face", (sx2, sy2, 2.20), (0.50, 0.04, 0.50), COL_SIGN_RED)


def build_sky_backdrop():
    # Large sky-color plane far behind (north) — at distance acts as horizon backdrop
    make_box("SkyBackdrop", (0.0, 24.0, 6.0), (40.0, 0.04, 12.0), COL_SKY)
    # A few cloud puffs
    for ci, (cx, cz) in enumerate([(-8.0, 8.0), (-2.0, 9.5), (5.0, 8.5), (12.0, 9.0)]):
        make_cyl(f"Cloud_{ci}", (cx, 23.9, cz), 1.40, 0.20, (0.92, 0.92, 0.88, 1.0), axis='Y', segments=10)




def build_roadside_detail():
    """Scene-standard deep pass (2026-07-12) for the game's most-seen
    backdrop (67 instances). Adds the iconic two-lane-swamp-highway
    silhouette the flat road was missing: a run of leaning
    utility poles with sagging catenary wires down the east verge, a
    dented guardrail on the swamp side, a stalled sedan on the west
    shoulder (gives the scenes' sedan/truck cuts a real subject),
    cattail reed clumps in the water, a dead cypress snag, a culvert
    pipe under the shoulder, and faded skid marks on the asphalt.
    Road runs N-S along +Y; asphalt half-width 2m; shoulders at
    x=+/-2.2. Uses only make_box/make_cyl (this script's imports)."""
    import math as _m
    pole_wood = (0.34, 0.26, 0.20, 1.0)
    wire_col  = (0.08, 0.08, 0.09, 1.0)
    steel     = (0.52, 0.54, 0.56, 1.0)
    steel_dk  = (0.34, 0.35, 0.37, 1.0)
    # ── Utility poles + sagging wires down the EAST verge (x=+3.4) ──
    pole_x = 3.4
    pole_ys = [-2.0, 4.0, 10.0, 16.0, 22.0]
    top_z = 5.2
    for i, py in enumerate(pole_ys):
        lean = _m.radians(3 + (i % 3))   # each leans a hair differently
        make_cyl(f"Pole_{i}", (pole_x + i * 0.02, py, top_z / 2), 0.09, top_z,
                 pole_wood, segments=6)
        # crossarm near the top
        make_box(f"Pole_{i}_Arm", (pole_x, py, top_z - 0.4),
                 (0.06, 0.9, 0.08), pole_wood)
        for sgn in (-1, +1):
            make_cyl(f"Pole_{i}_Insul_{sgn:+d}", (pole_x, py + sgn * 0.35, top_z - 0.32),
                     0.04, 0.10, (0.30, 0.44, 0.42, 1.0), segments=5)
        # sagging catenary wire to the next pole (three dip segments)
        if i < len(pole_ys) - 1:
            ny = pole_ys[i + 1]
            span = ny - py
            for seg in range(4):
                t0 = seg / 4.0; t1 = (seg + 1) / 4.0
                tm = (t0 + t1) / 2
                sag = 0.55 * _m.sin(_m.pi * tm)   # dip lowest mid-span
                make_cyl(f"Wire_{i}_{seg}", (pole_x, py + span * tm, top_z - 0.30 - sag),
                         0.012, span / 4.0 + 0.05, wire_col, segments=3, axis='Y')
    # ── Guardrail on the SWAMP (west) side, x=-2.5, dented ──
    for i in range(9):
        gy = -3.0 + i * 3.0
        dent = 0.05 if i == 5 else 0.0   # one bashed post
        make_box(f"Guardrail_Beam_{i}", (-2.5 - dent, gy + 1.5, 0.55),
                 (0.04, 3.0, 0.16), steel)
        make_cyl(f"Guardrail_Post_{i}", (-2.5, gy, 0.28), 0.05, 0.56,
                 steel_dk, segments=5)
    # ── Stalled sedan on the WEST shoulder, nosed north ──
    cxp, cyp = -3.1, 8.0
    body = (0.46, 0.16, 0.16, 1.0)
    glass = (0.20, 0.26, 0.30, 1.0)
    make_box("Sedan_LowerBody", (cxp, cyp, 0.44), (1.7, 4.0, 0.5), body)
    make_box("Sedan_Cabin", (cxp, cyp - 0.2, 0.95), (1.55, 2.2, 0.55),
             (0.40, 0.14, 0.14, 1.0))
    make_box("Sedan_Windshield", (cxp, cyp + 0.85, 0.98), (1.4, 0.06, 0.42), glass)
    make_box("Sedan_RearGlass", (cxp, cyp - 1.28, 0.98), (1.4, 0.06, 0.40), glass)
    for sgn in (-1, +1):
        make_box(f"Sedan_SideGlass_{sgn:+d}", (cxp + sgn * 0.76, cyp - 0.2, 0.98),
                 (0.05, 2.0, 0.40), glass)
    for wx in (-0.65, 0.65):
        for wy in (-1.4, 1.4):
            make_cyl(f"Sedan_Wheel_{wx:+.0f}_{wy:+.0f}", (cxp + wx, cyp + wy, 0.30),
                     0.34, 0.30, (0.08, 0.08, 0.09, 1.0), segments=8, axis='X')
    make_box("Sedan_Bumper_F", (cxp, cyp + 2.02, 0.42), (1.6, 0.10, 0.24), steel)
    make_box("Sedan_HoodUp", (cxp, cyp + 1.3, 1.02), (1.4, 1.2, 0.06),
             (0.42, 0.15, 0.15, 1.0))   # hood popped (broken down)
    # ── Cattail reed clumps in the swamp (west of guardrail) ──
    for i, (rx, ry) in enumerate([(-5.5, 2.0), (-6.2, 9.0), (-4.8, 15.0),
                                  (-7.0, 20.0), (-5.0, -4.0)]):
        for b in range(5):
            a = b * 1.3
            bx = rx + _m.cos(a) * 0.18; by = ry + _m.sin(a) * 0.18
            h = 0.9 + 0.25 * (b % 3)
            make_cyl(f"Reed_{i}_{b}", (bx, by, h / 2), 0.015, h,
                     (0.44, 0.48, 0.32, 1.0), segments=3)
            make_cyl(f"Reed_{i}_{b}_Head", (bx, by, h + 0.05), 0.03, 0.12,
                     (0.36, 0.24, 0.14, 1.0), segments=4)
    # ── Dead cypress snag (bare, pale) on the east treeline ──
    sx, sy = 6.5, 13.0
    make_cyl("Snag_Trunk", (sx, sy, 3.0), 0.22, 6.0, (0.58, 0.56, 0.50, 1.0), segments=6)
    for i, (dz, ang, ln) in enumerate([(4.2, 0.4, 1.6), (3.4, 3.5, 1.9), (4.8, 1.9, 1.2)]):
        make_cyl(f"Snag_Limb_{i}",
                 (sx + _m.cos(ang) * ln / 2, sy + _m.sin(ang) * ln / 2, dz),
                 0.06, ln, (0.54, 0.52, 0.46, 1.0), segments=4, axis='X')
    # ── Culvert pipe mouth under the west shoulder ──
    make_cyl("Culvert_Pipe", (-2.9, -1.0, 0.30), 0.30, 0.9,
             (0.30, 0.31, 0.33, 1.0), segments=10, axis='Y')
    make_cyl("Culvert_Bore", (-2.9, -1.35, 0.30), 0.22, 0.2,
             (0.06, 0.07, 0.07, 1.0), segments=10, axis='Y')
    # ── Faded skid marks on the asphalt (two parallel streaks) ──
    for sgn in (-1, +1):
        for k in range(3):
            make_box(f"Skid_{sgn:+d}_{k}", (sgn * 0.5, 5.0 + k * 0.9, 0.021),
                     (0.10, 0.8, 0.002), (0.09, 0.09, 0.10, 1.0))


def main():
    clear_scene()
    build_sky_backdrop()
    build_road()
    build_grass_and_swamp()
    build_cypress_trees()
    build_signs_and_markers()
    build_roadside_detail()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/louisiana_road.glb"))
    print(f"\n[build_louisiana_road] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
