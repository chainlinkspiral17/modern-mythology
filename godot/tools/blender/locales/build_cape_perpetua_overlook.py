"""cape_perpetua_overlook — vol7's central beat, re-homed off cabin_road
(2026-09-01). vol7_ch12_morning: Kai drives the coast highway to the
Cape Perpetua lot ("Two other vehicles — a foundation maintenance
truck with a Vestergaard plaque on its tailgate, and an older Subaru"),
takes "the third branch — the spur trail that went south along the
bluff to the unmarked overlook. The crow flew ahead of him along the
trail. The salal had been pruned back from the trail edges; the cuts
were fresh." "The overlook was an earthen platform at the edge of the
bluff, about ten feet across, with a wooden rail along the seaward
edge. The platform had a bench at its inner edge, set against the
salal. The bench was wet." "The fog was in the trees below the
platform." He lays the hexagon on the platform's earthen floor between
his boots and the rail; the crow lands on the rail beside him.

Coordinate frame: Blender Z-up. The lot is south (y<0), the spur
trail runs north along the bluff to the platform at (-4, 12); the sea
is west (x<-6), the fog and the trees below the bluff west of that.
glTF export remaps to Godot (x, z, -y).

DRAFT 1 (2026-09-01): the platform, rail, bench, salal, trail, lot,
two vehicles, bluff, fog band, sea + horizon. Draft 2 targets: Deck
framing of the fog (a mood, not a mesh, may serve better), the trail's
three branches (only the spur exists), rain on the bench.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, export_glb
from _props.creatures import make_crow
from _props.detail import make_far_bands

EARTH = (0.30, 0.24, 0.18, 1.0)
EARTH_WET = (0.24, 0.19, 0.14, 1.0)
SALAL = (0.18, 0.30, 0.18, 1.0)
SALAL_DK = (0.13, 0.22, 0.14, 1.0)
WOOD_WET = (0.34, 0.28, 0.20, 1.0)
GRAVEL = (0.50, 0.48, 0.44, 1.0)
CEDAR = (0.55, 0.38, 0.26, 1.0)
CEDAR_DK = (0.44, 0.30, 0.20, 1.0)


def build_ground():
    make_box("Headland_Ground", (0.0, 4.0, -0.03), (30.0, 34.0, 0.06), (0.22, 0.26, 0.18, 1.0))
    # the bluff drops away west of x = -5.6
    make_box("Bluff_Face", (-6.1, 12.0, -3.95), (1.0, 12.0, 8.0), (0.36, 0.32, 0.28, 1.0))
    make_box("Bluff_Lip", (-5.55, 12.0, -0.10), (0.3, 12.0, 0.25), EARTH_WET)
    # trees below the platform, in the fog
    for ti, (tx, ty, th) in enumerate(((-8.5, 9.0, 7.0), (-10.2, 12.5, 8.0), (-8.8, 15.5, 6.5), (-11.5, 7.5, 7.5))):
        make_cyl(f"Below_Sitka_{ti}", (tx, ty, -6.0 + th / 2.0), 0.30, th, (0.30, 0.24, 0.20, 1.0), segments=7)
        make_blob(f"Below_Sitka_Crown_{ti}", (tx, ty, -6.0 + th + 0.8), 1.6, (0.14, 0.22, 0.16, 1.0), noise=0.22, seed=31 + ti, squash=0.8)
    make_box("Fog_Bank", (-12.0, 12.0, -0.8), (16.0, 14.0, 3.6), (0.82, 0.84, 0.86, 0.55))
    # the sea and its horizon
    make_box("Sea_Plane", (-110.0, 12.0, -6.0), (200.0, 260.0, 0.06), (0.30, 0.38, 0.42, 1.0))
    make_box("Ground_Far", (0.0, 12.0, -0.05), (600.0, 600.0, 0.02), (0.20, 0.24, 0.17, 1.0))
    make_far_bands("FarTrees", (0.13, 0.20, 0.11),
                   [(60.0, 90.0, 8.0, 0.90), (120.0, 150.0, 11.0, 0.70),
                    (220.0, 240.0, 14.0, 0.52), (400.0, 380.0, 17.0, 0.40)],
                   sides="NSE", cy=12.0, profile="treeline")


def build_lot():
    make_box("Lot_Gravel", (0.0, -6.0, -0.01), (12.0, 8.0, 0.04), GRAVEL)
    # the foundation maintenance truck, Vestergaard plaque on the tailgate
    make_box("Foundation_Truck_Body", (-2.6, -6.0, 0.62), (1.9, 4.6, 0.65), (0.88, 0.88, 0.86, 1.0))
    make_box("Foundation_Truck_Cab", (-2.6, -4.9, 1.22), (1.75, 1.6, 0.55), (0.82, 0.82, 0.80, 1.0))
    make_box("Foundation_Truck_Tailgate", (-2.6, -8.33, 0.83), (1.80, 0.06, 0.55), (0.86, 0.86, 0.84, 1.0))
    make_box("Vestergaard_Plaque", (-2.6, -8.367, 0.83), (0.42, 0.008, 0.16), (0.62, 0.52, 0.30, 1.0))
    for wi, (wx, wy) in enumerate(((-3.575, -7.4), (-1.625, -7.4), (-3.575, -4.6), (-1.625, -4.6))):
        make_cyl(f"Foundation_Truck_Wheel_{wi}", (wx, wy, 0.33), 0.33, 0.25, (0.14, 0.14, 0.15, 1.0), axis="X", segments=10)
    # the older Subaru he did not recognize
    make_box("Old_Subaru_Body", (2.6, -6.0, 0.62), (1.8, 4.4, 0.62), (0.48, 0.50, 0.46, 1.0))
    make_box("Old_Subaru_Cabin", (2.6, -5.9, 1.20), (1.7, 2.6, 0.50), (0.42, 0.44, 0.40, 1.0))
    for wi, (wx, wy) in enumerate(((1.675, -7.3), (3.525, -7.3), (1.675, -4.7), (3.525, -4.7))):
        make_cyl(f"Old_Subaru_Wheel_{wi}", (wx, wy, 0.32), 0.32, 0.25, (0.14, 0.14, 0.15, 1.0), axis="X", segments=10)
    # the trailhead post with its three-branch board
    make_box("Trailhead_Post", (0.0, -1.6, 0.6), (0.12, 0.12, 1.2), WOOD_WET)
    make_box("Trailhead_Board", (0.0, -1.53, 1.0), (0.50, 0.03, 0.30), (0.42, 0.34, 0.24, 1.0))


def build_trail():
    """The spur trail: packed earth in three legs from the trailhead
    north-west to the platform, salal mounds along both edges — the
    cuts fresh where the foundation's drones pruned them back."""
    legs = [((0.0, -1.2), (-1.0, 3.5)), ((-1.0, 3.5), (-2.6, 8.0)), ((-2.6, 8.0), (-3.6, 10.8))]
    for li, ((x0, y0), (x1, y1)) in enumerate(legs):
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        make_box(f"Spur_Trail_{li}", (cx, cy, 0.005), (1.2, abs(y1 - y0) + 0.6, 0.02), EARTH)
    for si, (sx, sy, sr) in enumerate((
            (1.2, 0.5, 0.7), (-1.6, 1.0, 0.6), (1.4, 3.2, 0.8), (-2.6, 3.8, 0.6),
            (0.2, 6.0, 0.7), (-4.0, 6.5, 0.7), (-0.4, 8.6, 0.8), (-4.8, 9.0, 0.6),
            (-1.3, 10.8, 0.7), (-0.4, 12.6, 0.9), (-1.6, 15.0, 0.8), (-4.4, 15.8, 0.7))):
        make_blob(f"Salal_{si}", (sx, sy, sr * 0.45), sr, SALAL if si % 2 else SALAL_DK,
                  noise=0.26, seed=101 + si, squash=0.55)
    # fresh cuts: pale stubs at the trail edge
    for ci, (cx, cy) in enumerate(((0.75, 1.2), (-0.3, 4.6), (-1.9, 7.2), (-3.2, 9.6))):
        make_cyl(f"Salal_Cut_{ci}", (cx, cy, 0.09), 0.02, 0.18, (0.74, 0.70, 0.52, 1.0), segments=6)


def build_platform():
    """The overlook: an earthen platform about ten feet across at the
    bluff edge, a wooden rail along the seaward edge, the wet bench at
    the inner edge against the salal."""
    px, py = -4.0, 12.0
    make_cyl("Overlook_Platform", (px, py, 0.05), 1.55, 0.10, EARTH_WET, segments=18)
    make_cyl("Overlook_Platform_Edge", (px, py, 0.02), 1.75, 0.04, EARTH, segments=18)
    # rail along the seaward (west) edge
    for pi, ry in enumerate((py - 1.3, py, py + 1.3)):
        make_box(f"Overlook_Rail_Post_{pi}", (-5.35, ry, 0.60), (0.10, 0.10, 1.00), WOOD_WET)
    make_box("Overlook_Rail_Top", (-5.35, py, 1.12), (0.12, 2.80, 0.08), WOOD_WET)
    make_box("Overlook_Rail_Mid", (-5.35, py, 0.72), (0.06, 2.70, 0.06), WOOD_WET)
    # the bench at the inner edge, set against the salal
    make_box("Overlook_Bench_Seat", (-2.85, py, 0.46), (0.40, 1.50, 0.06), WOOD_WET)
    make_box("Overlook_Bench_Back", (-2.66, py, 0.78), (0.06, 1.50, 0.40), WOOD_WET)
    for li, ly in enumerate((py - 0.6, py + 0.6)):
        make_box(f"Overlook_Bench_Leg_{li}", (-2.85, ly, 0.215), (0.34, 0.08, 0.43), WOOD_WET)
    make_box("Bench_Wet_Sheen", (-2.85, py, 0.4915), (0.30, 1.30, 0.003), (0.42, 0.36, 0.28, 1.0))
    # the canvas bag on the bench, the cloth beside it
    make_box("Canvas_Bag", (-2.85, py - 0.45, 0.58), (0.28, 0.20, 0.18), (0.62, 0.58, 0.48, 1.0))
    make_box("Canvas_Bag_Strap", (-2.85, py - 0.45, 0.682), (0.24, 0.05, 0.024), (0.48, 0.44, 0.36, 1.0))
    # THE HEXAGON on the platform's earthen floor between the boots and the rail
    hx, hy = -4.75, py + 0.15
    T = 0.10
    make_box("Hexagon_Cloth", (hx, hy, T + 0.002), (0.40, 0.36, 0.004), (0.78, 0.74, 0.64, 1.0))
    for hi in range(6):
        ang = math.pi / 3.0 * hi + math.pi / 6.0
        make_box(f"Hexagon_Ring_{hi}", (hx + 0.13 * math.cos(ang), hy + 0.13 * math.sin(ang), T + 0.013),
                 (0.085, 0.085, 0.018), CEDAR)
    make_cyl("Hexagon_Center_Face", (hx, hy, T + 0.012), 0.055, 0.016, CEDAR_DK, segments=12)
    make_cyl("Hexagon_Face_Inlay", (hx, hy, T + 0.0215), 0.030, 0.003, (0.62, 0.46, 0.32, 1.0), segments=10)
    make_box("Hexagon_Aria_Piece", (hx + 0.155, hy - 0.145, T + 0.014), (0.070, 0.050, 0.020), CEDAR)
    # the crow, landed on the rail beside him
    make_crow("Crow", -5.35, py - 0.55, 1.16, facing=1.0)
    # boot prints in the wet earth where he stood
    for bi, (bx, by) in enumerate(((-4.45, py + 0.32), (-4.45, py - 0.05))):
        make_box(f"Boot_Print_{bi}", (bx, by, 0.1015), (0.11, 0.30, 0.003), (0.20, 0.16, 0.12, 1.0))


def main():
    clear_scene()
    build_ground()
    build_lot()
    build_trail()
    build_platform()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cape_perpetua_overlook.glb"))
    print(f"\n[build_cape_perpetua_overlook] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
