"""pasadena_1945 — vol 3's 1945: the Pasadena street, the park, a Hollywood
street, the clinic (draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
1945 comes from the text ("Pasadena · 1945"; "Pasadena, the box said,
1945"). Plain period-safe dressing only: no brands, no real titles or
names, no war posters (the month is not given).

THE STREET (origin, running north) — ch10: people reading in public with
"coffee resting" on their papers, slow cars, "The buses are fantastic",
"The same movie plays all over town", "Heavy citrus aromas in the air".
meld_seam_2_3's game picture of it: "A street in the rain. Streetcar wire.
A movie marquee. Orange trees." — the same street; the rain is that view's
(`__street_rain` props: the wet road, the streaks, the low cloud).
THE PARK (x 60..100) — "chess boards in the shade", gravel, pigeons, the
old men; the open ground for a football with college kids; kites.
HOLLYWOOD (x 140..) — a busier, different street: "They shoot on the
streets" — a film camera on its tripod, a lamp, the rope.
THE CLINIC (x 200..) — ch9: "Here's the clinic son, the nice woman is handing
you a glass of water"; "the nurse puts a blood pressure cuff on Andy's arm".
A small room, not a ward.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the streetcar itself, the crowd as hats and coats on benches, the marquee's
lettering (no real title), the park's paths, the clinic's corridor; Deck
framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_tube,
                             make_taper_cyl, join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.trees import make_broadleaf
from _props.furniture import make_chair

try:
    import bpy
except ImportError:
    bpy = None

ASPHALT = (0.30, 0.30, 0.30, 1.0); CONCRETE = (0.72, 0.70, 0.64, 1.0); CURB = (0.62, 0.60, 0.56, 1.0)
RAIL = (0.50, 0.48, 0.46, 1.0)
FACADES = [(0.78, 0.66, 0.52, 1.0), (0.66, 0.40, 0.32, 1.0), (0.86, 0.82, 0.70, 1.0), (0.70, 0.72, 0.62, 1.0),
           (0.58, 0.46, 0.38, 1.0), (0.84, 0.76, 0.58, 1.0)]
CAR_COLS = [(0.10, 0.10, 0.12, 1.0), (0.34, 0.12, 0.12, 1.0), (0.20, 0.30, 0.22, 1.0), (0.20, 0.24, 0.36, 1.0),
            (0.58, 0.54, 0.46, 1.0)]
ORANGE = (0.96, 0.56, 0.12, 1.0); LEAF = (0.22, 0.40, 0.20, 1.0); TRUNK = (0.36, 0.28, 0.20, 1.0)
RAIN = "__street_rain"


def join_named(prefix, out_name):
    if bpy is None:
        return
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(prefix)]
    if len(objs) < 2:
        return
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = out_name
    bpy.ops.object.select_all(action='DESELECT')


def storefront_block(prefix, x_face, y0, y1, side, storeys=2, seed=0, tall=False, skip=None):
    """A row of shopfronts along a street. side = +1 (the buildings lie to
    +x of x_face) or -1. Each building: its mass, the shop glass, the
    upper windows, a cornice, a striped awning on some."""
    y = y0
    k = 0
    while y < y1 - 2.0:
        w = 6.0 + ((k * 7 + seed) % 4) * 2.0
        w = min(w, y1 - y)
        if skip and y < skip[1] and y + w > skip[0]:     # another building stands here
            y = max(y + w, skip[1])
            k += 1
            continue
        h = (3.6 * storeys + ((k + seed) % 3) * 1.2) * (1.4 if tall else 1.0)
        col = FACADES[(k + seed) % len(FACADES)]
        d = 12.0
        cx = x_face + side * d / 2.0
        p = f"{prefix}_Stock_{k}"
        make_box(p + "_Mass", (cx, y + w / 2.0, h / 2.0), (d, w - 0.1, h), col)
        make_box(p + "_Cornice", (x_face + side * 0.15, y + w / 2.0, h - 0.2), (0.30, w - 0.1, 0.30),
                 (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8, 1.0))
        make_box(p + "_Shopglass", (x_face - side * 0.01, y + w / 2.0, 1.5), (0.02, w - 1.4, 2.2), (0.30, 0.36, 0.40, 1.0))
        make_box(p + "_Door", (x_face - side * 0.012, y + 0.9, 1.1), (0.02, 0.9, 2.2), (0.30, 0.22, 0.16, 1.0))
        make_box(p + "_Sign", (x_face - side * 0.02, y + w / 2.0, 3.0), (0.04, w - 1.6, 0.5), (0.90, 0.86, 0.74, 1.0))
        for f in range(1, storeys + (1 if tall else 0)):
            for j in range(int((w - 1.0) / 1.8)):
                make_box(p + f"_Win_{f}_{j}", (x_face - side * 0.01, y + 1.2 + j * 1.8, 3.6 * f + 1.6), (0.02, 1.0, 1.4),
                         (0.24, 0.28, 0.32, 1.0))
        if k % 2 == 0:
            make_rot_box(p + "_Awning", (x_face - side * 0.7, y + w / 2.0, 2.75), (1.4, w - 1.4, 0.06),
                         ((0.70, 0.22, 0.20, 1.0), (0.22, 0.40, 0.30, 1.0), (0.84, 0.80, 0.60, 1.0))[(k + seed) % 3],
                         roll=0.0, pitch=side * 0.30)
        y += w
        k += 1


def car_1940s(prefix, x, y, col, heading=1):
    """A 1940s sedan along Y (heading +1 = nose north): the long hood and
    the tall rounded cab, separate fenders over the wheels, running boards,
    whitewalls, chrome bumpers and grille, the headlamps on the fenders."""
    h = heading
    trim = (min(1.0, col[0] * 0.6 + 0.05), min(1.0, col[1] * 0.6 + 0.05), min(1.0, col[2] * 0.6 + 0.05), 1.0)
    chrome = (0.84, 0.84, 0.82, 1.0)
    make_chamfer_box(f"{prefix}_Body", (x, y, 0.72), (1.70, 4.70, 0.56), col, chamfer=0.12)
    make_chamfer_box(f"{prefix}_Hood", (x, y + h * 1.45, 1.06), (1.12, 1.70, 0.20), col, chamfer=0.08)
    make_chamfer_box(f"{prefix}_Cab", (x, y - h * 0.35, 1.30), (1.56, 2.20, 0.70), col, chamfer=0.26)
    make_box(f"{prefix}_Glass_Side_L", (x - 0.782, y - h * 0.35, 1.38), (0.004, 1.70, 0.36), (0.18, 0.22, 0.26, 1.0))
    make_box(f"{prefix}_Glass_Side_R", (x + 0.782, y - h * 0.35, 1.38), (0.004, 1.70, 0.36), (0.18, 0.22, 0.26, 1.0))
    make_rot_box(f"{prefix}_Windshield", (x, y + h * 0.70, 1.40), (1.30, 0.004, 0.40), (0.18, 0.22, 0.26, 1.0), roll=h * 0.45)
    for e in (-1, 1):
        for s in (-1, 1):
            wy = y + e * 1.45
            make_cyl(f"{prefix}_Wheel_{e:+d}_{s:+d}", (x + s * 0.80, wy, 0.36), 0.36, 0.22, (0.08, 0.08, 0.08, 1.0), axis='X', segments=14)
            make_cyl(f"{prefix}_Whitewall_{e:+d}_{s:+d}", (x + s * 0.915, wy, 0.36), 0.24, 0.01, (0.94, 0.94, 0.92, 1.0), axis='X', segments=14)
            make_chamfer_box(f"{prefix}_Fender_{e:+d}_{s:+d}", (x + s * 0.80, wy, 0.66), (0.34, 1.10, 0.36), col, chamfer=0.12)
        make_box(f"{prefix}_Bumper_{e:+d}", (x, y + e * 2.38, 0.50), (1.80, 0.10, 0.12), chrome)
    for s in (-1, 1):
        make_box(f"{prefix}_Running_Board_{s:+d}", (x + s * 0.90, y, 0.46), (0.18, 1.80, 0.04), trim)
        make_cyl(f"{prefix}_Headlamp_{s:+d}", (x + s * 0.80, y + h * 2.02, 0.92), 0.10, 0.12, chrome, axis='Y', segments=12)
    make_box(f"{prefix}_Grille", (x, y + h * 2.36, 0.78), (0.50, 0.03, 0.42), chrome)


def build_street():
    """Pasadena: a long street north, the streetcar line down its middle under
    its wire, sidewalks and shopfronts, the marquee, the orange trees."""
    L0, L1 = -20.0, 160.0
    cy = (L0 + L1) / 2.0
    make_box("St_Road", (0.0, cy, -0.01), (12.0, L1 - L0, 0.02), ASPHALT)
    for s in (-1, 1):
        make_box(f"St_Curb_{s:+d}", (s * 6.05, cy, 0.06), (0.10, L1 - L0, 0.12), CURB)
        make_box(f"St_Walk_{s:+d}", (s * 8.0, cy, 0.06), (3.9, L1 - L0, 0.12), CONCRETE)
        for k in range(45):
            make_box(f"St_Walk_Seam_{s:+d}_{k}", (s * 8.0, L0 + 2.0 + k * 4.0, 0.121), (3.9, 0.02, 0.002), (0.60, 0.58, 0.54, 1.0))
    for s in (-1, 1):
        make_box(f"Streetcar_Rail_{s:+d}", (s * 0.72, cy, 0.006), (0.08, L1 - L0, 0.012), RAIL)
    # the streetcar wire on its poles (both views: the line is there in 1945)
    for k in range(18):
        y = L0 + 4.0 + k * 10.0
        for s in (-1, 1):
            make_cyl(f"Wire_Pole_{k}_{s:+d}", (s * 6.4, y, 3.8), 0.10, 7.6, (0.30, 0.26, 0.22, 1.0), segments=8)
        make_box(f"Wire_Span_{k}", (0.0, y, 6.6), (12.8, 0.03, 0.03), (0.16, 0.16, 0.16, 1.0))
    make_box("Wire_Trolley", (0.0, cy, 6.3), (0.02, L1 - L0, 0.02), (0.16, 0.16, 0.16, 1.0))
    for k in range(18):
        make_box(f"Wire_Hanger_{k}", (0.0, L0 + 4.0 + k * 10.0, 6.45), (0.02, 0.02, 0.30), (0.16, 0.16, 0.16, 1.0))
    storefront_block("StW", -10.0, L0, L1, -1, seed=1)
    storefront_block("StE", 10.0, L0, L1, +1, seed=4, skip=(40.0, 52.0))
    # the movie house on the E side: its marquee over the walk, the bulbs
    my = 46.0
    make_box("Theatre_Mass", (16.0, my, 6.0), (12.0, 12.0, 12.0), (0.82, 0.74, 0.60, 1.0))
    make_box("Marquee", (8.6, my, 4.0), (2.8, 9.0, 1.1), (0.92, 0.88, 0.80, 1.0))
    make_box("Marquee_Face_N", (8.6, my + 4.52, 4.0), (2.6, 0.04, 0.8), (0.98, 0.96, 0.88, 1.0))
    make_box("Marquee_Face_W", (7.18, my, 4.0), (0.04, 8.6, 0.8), (0.98, 0.96, 0.88, 1.0))
    for k in range(10):
        make_box(f"Marquee_Letter_{k}", (7.15, my - 3.6 + k * 0.8, 4.05), (0.02, 0.5, 0.4), (0.16, 0.16, 0.18, 1.0))
    for k in range(18):
        make_cyl(f"Marquee_Bulb_{k}", (7.19, my - 4.3 + k * 0.5, 4.48), 0.05, 0.02, (1.0, 0.92, 0.66, 1.0), axis='X', segments=8)
    make_box("Theatre_Vertical_Sign", (10.1, my, 8.6), (0.40, 1.2, 5.6), (0.70, 0.18, 0.16, 1.0))
    for k in range(4):
        make_box(f"Marquee_Hanger_{k}", (9.2, my - 3.6 + k * 2.4, 5.2), (1.6, 0.04, 0.04), (0.30, 0.30, 0.32, 1.0))
    # orange trees in the walks, down the block
    for k, (s, y) in enumerate(((-1, 18.0), (1, 26.0), (-1, 34.0), (1, 62.0), (-1, 70.0), (1, 78.0), (-1, 92.0))):
        x = s * 7.2
        make_box(f"Orange_Tree_{k}_Well", (x, y, 0.13), (1.0, 1.0, 0.02), (0.36, 0.28, 0.20, 1.0))
        make_taper_cyl(f"Orange_Tree_{k}_Trunk", (x, y, 0.95), 0.12, 0.08, 1.6, TRUNK, segments=8)
        make_blob(f"Orange_Tree_{k}_Crown", (x, y, 2.4), 1.3, LEAF, noise=0.22, seed=k)
        for j in range(10):
            a = j * 0.63 + k
            make_blob(f"Orange_Tree_{k}_Crown_Fruit_{j}", (x + math.cos(a) * 0.85, y + math.sin(a) * 0.85, 2.2 + (j % 4) * 0.12), 0.08,
                      ORANGE, noise=0.0, seed=j)
    # readers' benches with their papers and coffee, a newsstand
    for k, (s, y) in enumerate(((-1, 10.0), (-1, 22.0), (1, 14.0))):
        x = s * 9.3
        make_box(f"Bench_{k}_Seat", (x, y, 0.46), (0.50, 1.80, 0.06), (0.36, 0.42, 0.30, 1.0))
        make_box(f"Bench_{k}_Back", (x + s * 0.22, y, 0.74), (0.06, 1.80, 0.50), (0.36, 0.42, 0.30, 1.0))
        for e in (-1, 1):
            make_box(f"Bench_{k}_Leg_{e:+d}", (x, y + e * 0.80, 0.29), (0.46, 0.06, 0.34), (0.20, 0.20, 0.22, 1.0))
        make_rot_box(f"Bench_{k}_Paper", (x - s * 0.05, y - 0.4, 0.50), (0.36, 0.48, 0.01), (0.86, 0.84, 0.76, 1.0), yaw=0.2)
        make_cyl(f"Bench_{k}_Coffee", (x - s * 0.05, y - 0.3, 0.55), 0.04, 0.09, (0.94, 0.94, 0.92, 1.0), segments=10)
    make_box("Newsstand", (-7.0, 30.0, 0.80), (1.2, 2.0, 1.36), (0.30, 0.36, 0.26, 1.0))      # at the curb
    make_box("Newsstand_Roof", (-7.0, 30.0, 1.52), (1.4, 2.2, 0.08), (0.24, 0.30, 0.22, 1.0))
    for k in range(6):
        make_box(f"Newsstand_Paper_{k}", (-7.61, 29.2 + k * 0.32, 1.10), (0.02, 0.28, 0.36), (0.86, 0.84, 0.76, 1.0))
    # slow cars at the curbs and in the road; the bus
    for k, (x, y, along) in enumerate(((-4.8, 16.0, "Y"), (-4.8, 30.0, "Y"), (4.8, 24.0, "Y"), (4.8, 52.0, "Y"), (-2.4, 44.0, "Y"),
                                        (2.4, 70.0, "Y"))):
        car_1940s(f"Car_{k}", x, y, CAR_COLS[k % len(CAR_COLS)], heading=(1 if x > 0 else -1))
    bx, by = 2.6, 34.0
    make_chamfer_box("Bus_Body", (bx, by, 1.75), (2.5, 10.0, 2.7), (0.86, 0.72, 0.30, 1.0), chamfer=0.25)
    make_box("Bus_Window_Band", (bx - 1.26, by, 2.2), (0.02, 8.6, 0.8), (0.24, 0.28, 0.32, 1.0))
    make_box("Bus_Window_Band_E", (bx + 1.26, by, 2.2), (0.02, 8.6, 0.8), (0.24, 0.28, 0.32, 1.0))
    make_box("Bus_Windshield", (bx, by + 5.01, 2.2), (2.2, 0.02, 0.8), (0.24, 0.28, 0.32, 1.0))
    for s in (-1, 1):
        for e in (-1, 1):
            make_cyl(f"Bus_Wheel_{s:+d}_{e:+d}", (bx + s * 1.1, by + e * 3.4, 0.48), 0.48, 0.30, (0.10, 0.10, 0.10, 1.0), axis='X', segments=12)
    # the far ends: a cross street and more blocks so no edge shows
    make_box("St_Far_N", (0.0, L1 + 30.0, 8.0), (80.0, 2.0, 16.0), (0.74, 0.70, 0.62, 1.0))
    make_box("St_Far_S", (0.0, L0 - 20.0, 8.0), (80.0, 2.0, 16.0), (0.74, 0.70, 0.62, 1.0))
    make_box("St_Ground", (0.0, cy, -0.05), (120.0, (L1 - L0) + 60.0, 0.04), (0.44, 0.42, 0.36, 1.0))
    # the rain (the meld's game picture only): the wet road, the puddles,
    # the streaks in the air, the low cloud over the street
    make_box("Wet_Road" + RAIN, (0.0, cy, 0.002), (11.9, L1 - L0, 0.006), (0.16, 0.18, 0.20, 1.0))
    for s in (-1, 1):
        make_box(f"Wet_Walk_{s:+d}" + RAIN, (s * 8.0, cy, 0.124), (3.88, L1 - L0, 0.004), (0.46, 0.46, 0.46, 1.0))
    for k in range(10):
        make_cyl(f"Puddle_{k}" + RAIN, ((-3.0 if k % 2 else 3.0) + (k % 3) * 0.8, 8.0 + k * 9.0, 0.006), 0.6 + (k % 3) * 0.3, 0.004,
                 (0.40, 0.46, 0.54, 1.0), segments=14)
    for k in range(160):
        x = -9.0 + (k * 37 % 180) / 10.0
        y = 2.0 + (k * 53 % 400) / 10.0
        z = 0.6 + (k * 29 % 50) / 10.0
        if 1.2 < x < 4.0 and 28.8 < y < 39.2:        # not through the bus
            continue
        make_rot_box(f"RainStreak_{k}" + RAIN, (x, y, z), (0.008, 0.008, 0.42), (0.70, 0.74, 0.80, 1.0), roll=0.12)
    make_box("Low_Cloud" + RAIN, (0.0, cy, 28.0), (140.0, (L1 - L0) + 80.0, 0.5), (0.44, 0.46, 0.50, 1.0))


def build_park():
    """A neighbourhood park: the chess boards in the shade of two big trees,
    gravel under them, pigeons; the open ground past them; kites."""
    px, py = 80.0, 20.0
    make_box("Park_Grass", (px, py, -0.01), (44.0, 44.0, 0.02), (0.40, 0.52, 0.28, 1.0))
    make_box("Park_Gravel", (px - 10.0, py - 8.0, 0.006), (10.0, 8.0, 0.012), (0.70, 0.66, 0.58, 1.0))
    for k, (x, y) in enumerate(((px - 12.0, py - 6.0), (px - 7.0, py - 10.0), (px - 14.0, py - 11.0))):
        make_broadleaf(f"Park_Shade_Tree_{k}", x, y, 9.5, (0.24, 0.38, 0.20, 1.0), TRUNK)
    for k in range(4):
        tx, ty = px - 13.0 + (k % 2) * 3.2, py - 9.6 + (k // 2) * 3.0
        make_cyl(f"Chess_Table_{k}_Post", (tx, ty, 0.36), 0.10, 0.72, CONCRETE, segments=10)
        make_box(f"Chess_Table_{k}_Top", (tx, ty, 0.745), (0.80, 0.80, 0.05), CONCRETE)
        make_box(f"Chess_Table_{k}_Board", (tx, ty, 0.773), (0.42, 0.42, 0.006), (0.20, 0.20, 0.20, 1.0))
        for j in range(6):
            make_cyl(f"Chess_Table_{k}_Piece_{j}", (tx - 0.15 + (j % 3) * 0.12, ty - 0.14 + (j // 3) * 0.28, 0.80), 0.016, 0.05,
                     ((0.94, 0.92, 0.86, 1.0), (0.12, 0.12, 0.12, 1.0))[j // 3], segments=8)
        for s in (-1, 1):
            make_cyl(f"Chess_Table_{k}_Stool_{s:+d}", (tx + s * 0.62, ty, 0.22), 0.16, 0.44, CONCRETE, segments=10)
    for k in range(9):
        x, y = px - 11.0 + (k * 37 % 50) / 10.0, py - 6.5 + (k * 53 % 30) / 10.0
        make_blob(f"Pigeon_{k}", (x, y, 0.075), 0.09, ((0.50, 0.52, 0.58, 1.0), (0.40, 0.40, 0.46, 1.0))[k % 2], noise=0.0, seed=k,
                  squash=0.7)
        make_blob(f"Pigeon_{k}_Head", (x + 0.08, y, 0.145), 0.04, (0.36, 0.40, 0.44, 1.0), noise=0.0, seed=k + 20)
    make_rot_box("Football", (px + 2.0, py - 2.0, 0.085), (0.28, 0.17, 0.17), (0.50, 0.28, 0.16, 1.0), yaw=0.6)
    # kites in a clear sky, their strings falling away
    for k, (x, y, z, col) in enumerate(((px + 4.0, py + 18.0, 22.0, (0.90, 0.24, 0.20, 1.0)), (px + 12.0, py + 14.0, 28.0, (0.24, 0.40, 0.86, 1.0)),
                                         (px - 2.0, py + 16.0, 18.0, (0.96, 0.84, 0.30, 1.0)))):
        make_rot_box(f"Kite_{k}", (x, y, z), (1.1, 0.02, 1.4), col, yaw=0.0, roll=0.0, pitch=0.785)
        make_tube(f"Kite_{k}_Tail", [(x, y, z - 0.9), (x + 0.3, y, z - 2.0), (x - 0.2, y, z - 3.2)], 0.02, col)
        make_tube(f"Kite_{k}_String", [(x, y, z - 0.6), (x - 3.0, y - 8.0, z * 0.45), (x - 5.0, y - 14.0, 0.0)], 0.008,
                  (0.90, 0.90, 0.86, 1.0))
    make_box("Park_Edge_Hedge", (px, py + 22.0, 0.7), (44.0, 1.2, 1.4), (0.24, 0.38, 0.20, 1.0))
    for k in range(5):
        make_box(f"Park_Far_House_{k}", (px - 18.0 + k * 9.0, py + 32.0, 3.5), (7.0, 8.0, 7.0), FACADES[k % len(FACADES)])


def build_hollywood():
    """A busier street, taller fronts, and a location shoot down the block."""
    hx = 160.0
    L0, L1 = -10.0, 120.0
    cy = (L0 + L1) / 2.0
    make_box("Hw_Road", (hx, cy, -0.01), (14.0, L1 - L0, 0.02), ASPHALT)
    for s in (-1, 1):
        make_box(f"Hw_Walk_{s:+d}", (hx + s * 9.0, cy, 0.06), (4.0, L1 - L0, 0.12), CONCRETE)
        make_box(f"Hw_Curb_{s:+d}", (hx + s * 7.05, cy, 0.06), (0.10, L1 - L0, 0.12), CURB)
    storefront_block("HwW", hx - 11.0, L0, L1, -1, storeys=3, seed=2, tall=True)
    storefront_block("HwE", hx + 11.0, L0, L1, +1, storeys=3, seed=5, tall=True)
    for k in range(10):
        car_1940s(f"Hw_Car_{k}", hx + (-5.0 if k % 2 else 5.0) + (k % 3 - 1) * 0.4, 6.0 + k * 9.0, CAR_COLS[(k + 2) % len(CAR_COLS)],
                  heading=(-1 if k % 2 else 1))
    # the shoot on the E walk: the camera on its tripod, a lamp on its stand,
    # a reflector, a canvas chair, the rope and its stands, a cable
    sx, sy = hx + 8.4, 30.0
    for k in range(3):
        a = k * 2.09
        make_rot_box(f"Shoot_Tripod_Leg_{k}", (sx + math.cos(a) * 0.22, sy + math.sin(a) * 0.22, 0.62), (0.03, 0.03, 1.30),
                     (0.36, 0.28, 0.20, 1.0), yaw=a, pitch=0.0, roll=0.18)
    make_box("Shoot_Camera_Body", (sx, sy, 1.42), (0.34, 0.52, 0.40), (0.12, 0.12, 0.14, 1.0))
    make_cyl("Shoot_Camera_Lens", (sx - 0.30, sy, 1.44), 0.07, 0.26, (0.10, 0.10, 0.10, 1.0), axis='X', segments=12)
    for s in (-1, 1):
        make_cyl(f"Shoot_Camera_Reel_{s:+d}", (sx, sy + s * 0.12, 1.78), 0.16, 0.06, (0.16, 0.16, 0.18, 1.0), axis='Y', segments=14)
    make_cyl("Shoot_Lamp_Stand", (sx + 1.2, sy + 3.0, 1.1), 0.03, 2.2, (0.30, 0.30, 0.32, 1.0), segments=8)
    make_cyl("Shoot_Lamp", (sx + 1.1, sy + 3.0, 2.30), 0.24, 0.40, (0.20, 0.20, 0.22, 1.0), axis='X', segments=12)
    make_box("Shoot_Lamp_Base", (sx + 1.2, sy + 3.0, 0.02), (0.60, 0.60, 0.04), (0.30, 0.30, 0.32, 1.0))
    make_box("Shoot_Reflector", (sx + 1.4, sy - 2.4, 1.10), (0.04, 1.2, 1.2), (0.92, 0.90, 0.80, 1.0))
    make_box("Shoot_Reflector_Stand", (sx + 1.4, sy - 2.4, 0.25), (0.40, 0.40, 0.50), (0.30, 0.30, 0.32, 1.0))
    make_chair("Shoot_Chair", sx + 1.6, sy + 1.2, yaw=math.pi / 2.0, wood=(0.62, 0.48, 0.30, 1.0), seat_col=(0.30, 0.26, 0.20, 1.0))
    for k in range(5):
        make_cyl(f"Shoot_Stanchion_{k}", (hx + 7.4, sy - 4.0 + k * 2.0, 0.55), 0.03, 1.0, (0.62, 0.56, 0.36, 1.0), segments=8)
    make_box("Shoot_Rope", (hx + 7.4, sy, 0.98), (0.02, 8.0, 0.02), (0.70, 0.18, 0.16, 1.0))
    make_tube("Shoot_Cable", [(sx + 1.2, sy + 3.0, 0.15), (sx + 0.6, sy + 1.4, 0.02), (sx, sy, 0.02)], 0.02, (0.10, 0.10, 0.10, 1.0))
    make_box("Hw_Far_N", (hx, L1 + 20.0, 10.0), (80.0, 2.0, 20.0), (0.80, 0.76, 0.66, 1.0))
    make_box("Hw_Ground", (hx, cy, -0.05), (120.0, (L1 - L0) + 40.0, 0.04), (0.44, 0.42, 0.36, 1.0))


# ── the clinic ────────────────────────────────────────────────────────
CX0, CX1, CD, CH = 200.0, 205.0, 4.4, 2.8


def build_clinic():
    cx, cy = (CX0 + CX1) / 2.0, CD / 2.0
    make_floor("Cl_Floor", (cx, cy, 0.0), size_x=CX1 - CX0 + 0.4, size_y=CD + 0.4,
               palette={"vinyl": (0.70, 0.72, 0.66, 1.0), "seam": (0.60, 0.62, 0.56, 1.0)})
    make_box("Cl_Ceil", (cx, cy, CH + 0.04), (CX1 - CX0 + 0.4, CD + 0.4, 0.08), (0.92, 0.92, 0.88, 1.0))
    pal = {"wall": (0.82, 0.86, 0.80, 1.0), "baseboard": (0.40, 0.44, 0.40, 1.0)}
    make_wall("Cl_Wall_N", (cx, CD, 0), length=CX1 - CX0 + 0.4, height=CH, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Cl_Wall_E", (CX1, cy, 0), length=CD + 0.4, height=CH, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Cl_Wall_W", (CX0, cy, 0), length=CD + 0.4, height=CH, thickness=0.2, axis='Y', palette=pal,
                            baseboard_face_sign=+1, openings=[(2.2, 1.55, 1.4, 1.2)])
    make_box("Cl_Window", (CX0, 2.2, 1.55), (0.02, 1.4, 1.2), (0.86, 0.90, 0.92, 1.0))
    for k in range(3):
        make_box(f"Cl_Window_Mullion_{k}", (CX0 + 0.02, 1.75 + k * 0.45, 1.55), (0.03, 0.03, 1.2), (0.92, 0.92, 0.88, 1.0))
    make_wall_with_openings("Cl_Wall_S", (cx, 0.0, 0), length=CX1 - CX0 + 0.4, height=CH, thickness=0.2, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(CX0 + 1.2, 1.05, 0.96, 2.1)])
    make_box("Cl_Door_Open", (CX0 + 1.2 - 0.48 + 0.02, 0.10 + 0.46, 1.05), (0.04, 0.92, 2.08), (0.86, 0.84, 0.76, 1.0))
    make_box("Cl_Door_Glass", (CX0 + 1.2 - 0.48 + 0.02, 0.10 + 0.46, 1.50), (0.05, 0.60, 0.70), (0.80, 0.84, 0.82, 1.0))
    make_box("Cl_Corridor_Floor", (CX0 + 1.2, -1.4, 0.0), (3.0, 2.6, 0.02), (0.62, 0.62, 0.56, 1.0))
    make_box("Cl_Corridor_Wall", (CX0 + 1.2, -2.8, CH / 2.0), (3.0, 0.2, CH), (0.76, 0.80, 0.74, 1.0))
    # the exam table against the N wall, its sheet, the step
    ex, ey = cx + 0.3, CD - 0.10 - 0.36
    make_box("Exam_Table_Base", (ex, ey, 0.38), (1.80, 0.62, 0.76), (0.86, 0.86, 0.82, 1.0))
    make_box("Exam_Table_Pad", (ex, ey, 0.82), (1.84, 0.66, 0.12), (0.30, 0.36, 0.34, 1.0))
    make_box("Exam_Table_Sheet", (ex + 0.2, ey, 0.885), (1.30, 0.64, 0.01), (0.96, 0.96, 0.94, 1.0))
    make_box("Exam_Step", (ex - 0.6, ey - 0.50, 0.12), (0.46, 0.34, 0.24), (0.70, 0.70, 0.68, 1.0))
    # the cuff: the sphygmomanometer's gauge on its wall bracket, the cuff hung by it
    make_box("BP_Bracket", (CX1 - 0.12, 2.6, 1.40), (0.04, 0.20, 0.30), (0.70, 0.70, 0.72, 1.0))
    make_cyl("BP_Gauge", (CX1 - 0.165, 2.6, 1.48), 0.09, 0.05, (0.92, 0.92, 0.88, 1.0), axis='X', segments=16)
    make_box("BP_Cuff", (CX1 - 0.16, 2.6, 1.18), (0.04, 0.16, 0.30), (0.20, 0.26, 0.36, 1.0))
    make_blob("BP_Bulb", (CX1 - 0.18, 2.64, 1.00), 0.04, (0.10, 0.10, 0.10, 1.0), noise=0.0, seed=2)
    # the cabinet and sink on the E wall, the glass of water on a tray
    make_box("Cl_Cabinet", (CX1 - 0.10 - 0.28, 1.2, 0.45), (0.56, 1.20, 0.90), (0.92, 0.92, 0.88, 1.0))
    make_box("Cl_Cabinet_Top", (CX1 - 0.10 - 0.29, 1.2, 0.915), (0.58, 1.24, 0.03), (0.80, 0.80, 0.78, 1.0))
    make_cyl("Cl_Sink", (CX1 - 0.10 - 0.30, 1.5, 0.92), 0.16, 0.02, (0.96, 0.96, 0.96, 1.0), segments=14)
    make_box("Cl_Tray", (CX1 - 0.10 - 0.30, 0.9, 0.937), (0.30, 0.22, 0.015), (0.74, 0.74, 0.76, 1.0))
    make_cyl("Glass_Of_Water", (CX1 - 0.10 - 0.30, 0.9, 1.0), 0.035, 0.11, (0.80, 0.88, 0.92, 1.0), segments=12)
    for k in range(3):
        make_cyl(f"Cl_Jar_{k}", (CX1 - 0.10 - 0.24, 1.35 + k * 0.14, 0.99), 0.04, 0.12, (0.86, 0.88, 0.84, 1.0), segments=10)
    make_chair("Cl_Chair", CX0 + 0.6, 3.4, yaw=-math.pi / 2.0, wood=(0.62, 0.62, 0.60, 1.0), seat_col=(0.40, 0.44, 0.40, 1.0))
    make_box("Cl_Ceil_Light", (cx, cy, CH - 0.05), (0.80, 0.30, 0.10), (0.98, 0.98, 0.94, 1.0))


def build_clinic_2026_10():
    """DRAFT 3 of the 1945 clinic (2026-10-30): "Here's the clinic son, the
    nice woman is handing you a glass of water" / "the nurse puts a blood
    pressure cuff on Andy's arm". It read as an empty green room with a table.
    Now a 1945 doctor's room: the white-enamel instrument cabinet with glass
    doors and its instruments; a balance-beam scale; an eye chart; a
    three-panel privacy screen; venetian blinds in the window; a school-house
    clock over the door; a calendar for 1945; an enamel pendant shade; a
    kidney dish and a rolled bandage on the tray.
    Draft 4 targets: the doctor's desk and candlestick telephone in the
    corridor's office, the men's hats on a rack, the anatomy chart."""
    ENAMEL = (0.94, 0.94, 0.90, 1.0); CHROME = (0.76, 0.76, 0.78, 1.0)
    # the instrument cabinet, NW corner on the N wall
    ix, iy = CX0 + 0.10 + 0.32, CD - 0.10 - 0.18
    make_box("Cl_Instrument_Cabinet", (ix, iy, 0.90), (0.60, 0.34, 1.80), ENAMEL)
    make_box("Cl_Instrument_Glass", (ix, iy - 0.172, 1.20), (0.52, 0.006, 1.00), (0.80, 0.86, 0.88, 0.35))
    for lvl in range(3):
        make_box(f"Cl_Instrument_Shelf_{lvl}", (ix, iy, 0.80 + lvl * 0.34), (0.54, 0.28, 0.012), (0.86, 0.88, 0.88, 1.0))
        for k in range(3):
            make_cyl(f"Cl_Instrument_Bottle_{lvl}_{k}", (ix - 0.17 + k * 0.17, iy + 0.02, 0.87 + lvl * 0.34), 0.03, 0.12,
                     ((0.40, 0.26, 0.14, 1.0), (0.86, 0.88, 0.86, 1.0), (0.30, 0.40, 0.56, 1.0))[(lvl + k) % 3], segments=10)
    make_box("Cl_Instrument_Drawer_Seam", (ix, iy - 0.172, 0.55), (0.56, 0.004, 0.008), (0.70, 0.70, 0.68, 1.0))
    make_box("Cl_Instrument_Pull", (ix, iy - 0.18, 0.45), (0.12, 0.02, 0.02), CHROME)
    # the balance-beam scale by the S wall
    scx, scy = CX1 - 1.4, 0.45
    make_box("Cl_Scale_Platform", (scx, scy, 0.05), (0.40, 0.50, 0.10), (0.30, 0.30, 0.32, 1.0))
    make_box("Cl_Scale_Column", (scx, scy - 0.20, 0.80), (0.06, 0.06, 1.40), ENAMEL)
    make_box("Cl_Scale_Beam", (scx, scy - 0.20, 1.45), (0.50, 0.03, 0.05), CHROME)
    make_box("Cl_Scale_Poise", (scx + 0.10, scy - 0.20, 1.45), (0.04, 0.05, 0.07), (0.30, 0.30, 0.32, 1.0))
    # the eye chart on the E wall, the privacy screen
    make_box("Cl_Eye_Chart", (CX1 - 0.11, 2.05, 1.55), (0.01, 0.44, 0.70), (0.96, 0.96, 0.92, 1.0))
    for k in range(6):
        make_box(f"Cl_Eye_Chart_Row_{k}", (CX1 - 0.116, 2.05, 1.80 - k * 0.09), (0.004, 0.30 - k * 0.04, 0.04 - k * 0.005), (0.10, 0.10, 0.10, 1.0))
    for k, (x, y, yaw) in enumerate(((CX1 - 0.95, 3.05, 0.5), (CX1 - 0.72, 3.48, -0.5), (CX1 - 0.49, 3.91, 0.5))):
        make_rot_box(f"Cl_Screen_Panel_{k}", (x, y, 0.92), (0.03, 0.52, 1.60), (0.86, 0.88, 0.84, 1.0), yaw=yaw)
    # blinds in the window, a clock over the door, a calendar
    for k in range(16):
        make_box(f"Cl_Blind_Slat_Stock_{k}", (CX0 + 0.13, 2.2, 1.0 + k * 0.07), (0.01, 1.36, 0.03), (0.92, 0.90, 0.84, 1.0))
    make_box("Cl_Blind_Head", (CX0 + 0.13, 2.2, 2.16), (0.04, 1.40, 0.05), (0.92, 0.90, 0.84, 1.0))
    make_cyl("Cl_Clock", (CX0 + 1.2, 0.12, 2.42), 0.16, 0.04, (0.36, 0.26, 0.18, 1.0), axis='Y', segments=18)
    make_cyl("Cl_Clock_Face", (CX0 + 1.2, 0.142, 2.42), 0.13, 0.004, (0.94, 0.92, 0.84, 1.0), axis='Y', segments=18)
    make_box("Cl_Calendar", (CX0 + 0.11, 3.45, 1.70), (0.01, 0.30, 0.44), (0.92, 0.90, 0.82, 1.0))
    make_box("Cl_Calendar_Picture", (CX0 + 0.116, 3.45, 1.82), (0.004, 0.26, 0.16), (0.56, 0.40, 0.34, 1.0))
    make_box("Cl_Calendar_Year", (CX0 + 0.116, 3.45, 1.70), (0.004, 0.16, 0.03), (0.70, 0.16, 0.14, 1.0))
    # the enamel shade under the ceiling light, the tray's kidney dish and bandage
    cx, cy = (CX0 + CX1) / 2.0, CD / 2.0
    make_lathe("Cl_Pendant_Shade", (cx, cy, CH - 0.50), [(0.03, 0.40), (0.06, 0.38), (0.26, 0.10), (0.28, 0.0)], ENAMEL, segments=16)
    make_box("Cl_Kidney_Dish", (CX1 - 0.10 - 0.28, 1.12, 0.94), (0.14, 0.08, 0.02), CHROME)
    make_cyl("Cl_Bandage_Roll", (CX1 - 0.20, 0.84, 0.96), 0.03, 0.06, (0.96, 0.96, 0.94, 1.0), axis='Y', segments=10)


def main():
    clear_scene()
    build_street()
    build_park()
    build_hollywood()
    build_clinic()
    build_clinic_2026_10()
    try:
        join_stock()
        join_named("RainStreak_", "RainStreak" + RAIN)
        join_named("Puddle_", "Puddle" + RAIN)
    except Exception as _e:
        print("[join] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/pasadena_1945.glb"))
    print(f"\n[build_pasadena_1945] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
