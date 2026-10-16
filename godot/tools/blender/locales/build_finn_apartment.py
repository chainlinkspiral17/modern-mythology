"""finn_apartment — Finn's one-bedroom (vol 7) over the kayak shop: "The
apartment was at the corner of Hemlock and the alley that ran behind the
bakery." Kitchen south, bedroom north beyond the partition.

DRAFT 4 (2026-10-09, the overnight run; CLAUDE.md "build big"). Draft 3
was 5.0 x 5.4: the kitchen was a counter, the bedroom partition stood
across a third of the preset, and the things the prose does in the
kitchen had no home ("He banked the space heater in the corner. He put
the kettle on. He stood at the kitchen window looking down at the
alley."; "the fridge Finn must have"). Rebuilt at 8.4 x 7.6 under 2.7:
  - KITCHEN (S): the run on the W wall — fridge, stove with the kettle,
    sink under THE KITCHEN WINDOW that looks down into the alley at the
    bakery's back wall, its door and its back-kitchen light (the same
    light Marina stands under in vol7 ch15); upper cupboards. The
    kitchen table with the cloth, the charred-wood pieces, the hexagon
    and the stick in its sleeve, three chairs. The space heater in the
    corner (lit), the nine-month duffel in the other, Finn's desk with
    the lamp, phone, notebook and the carved cedar, a low bookcase, the
    entry door from the stairs in the E wall, the S window toward the
    street and the sea with the crow's marks on its sill.
  - BEDROOM (N, through a real doorway): the raised platform bed on
    turned posts with slatted crates under it, the side table with the
    reader and the headset, THE CHAIR BESIDE THE BED with the crow on
    its back ("The crow was on the back of the chair beside the bed"),
    the dresser with its change bowl and keys, the N window over the
    neighbour's roof, a rug, the ceiling light.
Coordinate frame: Blender Z-up. y=0 is the S wall (Hemlock side); +Y
runs north; the W wall is over the alley. glTF export remaps to Godot
(x, z, -y).

Draft 5 targets: a bathroom door off the bedroom; the kitchen's dish
rack and a towel on the oven bar; the crates' contents; rain on the
alley (puddles under the bakery light); Deck framing of the preset from
the entry door and the bedroom from its doorway.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_blob, make_cyl, make_lathe, make_tube, make_prism, export_glb
from _props.furniture import make_chair, make_lamp
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_wall_with_openings
from _props.decor import make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector
from _props.creatures import make_crow
from _props.detail import (make_traffic_wear, make_floor_stain, make_threshold,
                           make_wall_outlet, make_light_switch)

ROOM_W = 8.4; ROOM_D = 7.6; CEIL = 2.7   # draft 4 (2026-10-09): was 5.0 x 5.4 x 2.6
XW, XE, YS, YN = -ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 - 0.10, 0.10, ROOM_D - 0.10
PART_Y = 3.90                      # kitchen / bedroom partition (centre line)
PDOOR = (1.6, 1.05, 0.90, 2.10)    # the doorway in it — "the crow flew low through the doorway"
WIN_W = (2.20, 1.55, 1.10, 1.00)   # the kitchen window over the sink, W wall (y, z, w, h)
WIN_S = (1.80, 1.55, 0.90, 0.95)   # the S window, toward the street and the sea (x, z, w, h)
WIN_N = (0.0, 1.55, 1.30, 1.10)    # the bedroom's N window
EDOOR = (2.40, 1.05, 0.92, 2.10)   # the entry door from the stairs, E wall (y, ...)
PAL_WALL = {"wall": (0.78, 0.78, 0.72, 1.0), "baseboard": (0.62, 0.46, 0.30, 1.0)}   # coastal grey-green (the warm cream read pink under the lamps)
COL_FLOOR = (0.66, 0.50, 0.32, 1.0); COL_SEAM = (0.42, 0.30, 0.18, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_ACCENT = (0.80, 0.56, 0.54, 1.0)
COL_CAB = (0.56, 0.60, 0.52, 1.0)      # painted cupboards
COL_TOP = (0.34, 0.28, 0.22, 1.0)
COL_ENAMEL = (0.88, 0.88, 0.84, 1.0)
COL_STEEL = (0.62, 0.64, 0.65, 1.0)
BED_X, BED_Y = -3.0, 5.65
DESK_X, DESK_Y = -2.0, 0.42


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    make_wall_with_openings("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                            palette=PAL_WALL, baseboard_face_sign=+1, openings=[WIN_W])
    make_wall_with_openings("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                            palette=PAL_WALL, baseboard_face_sign=-1, openings=[EDOOR])
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=-1, openings=[WIN_N])
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=+1, openings=[WIN_S])
    make_wall_with_openings("Bedroom_Wall", (0.0, PART_Y, 0), length=ROOM_W - 0.2, height=CEIL, thickness=0.12, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=+1, openings=[PDOOR])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4, with_grid=False,
                 palette={"tile": (0.92, 0.88, 0.80, 1.0)})
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, XW, ROOM_D / 2.0), ("Crown_E", 'Y', ROOM_D, XE, ROOM_D / 2.0),
                                    ("Crown_N", 'X', ROOM_W, 0.0, YN), ("Crown_S", 'X', ROOM_W, 0.0, YS)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    # the doorway's casing on both faces
    p0, p1 = PDOOR[0] - PDOOR[2] / 2.0, PDOOR[0] + PDOOR[2] / 2.0
    for face, yy in (("S", PART_Y - 0.07), ("N", PART_Y + 0.07)):
        for nm, x in (("A", p0 - 0.035), ("B", p1 + 0.035)):
            make_box(f"Bedroom_Door_Casing_{face}_{nm}", (x, yy, 1.08), (0.07, 0.02, 2.16), COL_WOOD)
        make_box(f"Bedroom_Door_Casing_{face}_Head", (PDOOR[0], yy, 2.135), (PDOOR[2] + 0.14, 0.02, 0.07), COL_WOOD)
    # the entry door, closed, its chain hanging loose ("Finn's door was unlocked")
    ey = EDOOR[0]
    make_box("Entry_Door_Leaf", (ROOM_W / 2.0, ey, 1.045), (0.045, 0.90, 2.09), (0.42, 0.30, 0.20, 1.0))
    make_cyl("Entry_Door_Knob", (XE + 0.05, ey - 0.36, 1.0), 0.03, 0.06, (0.70, 0.62, 0.36, 1.0), segments=8, axis='X')
    make_tube("Entry_Door_Chain", [(XE + 0.072, ey - 0.30, 1.40), (XE + 0.068, ey - 0.26, 1.30), (XE + 0.072, ey - 0.22, 1.36)], 0.006, COL_STEEL, segments=4)
    for nm, y in (("A", ey - 0.495), ("B", ey + 0.495)):
        make_box(f"Entry_Door_Casing_{nm}", (XE - 0.01, y, 1.08), (0.02, 0.07, 2.16), COL_WOOD)
    make_box("Entry_Door_Casing_Head", (XE - 0.01, ey, 2.135), (0.02, 1.06, 0.07), COL_WOOD)
    make_threshold("Threshold_Entry", (XE - 0.30, ey), width=0.9, axis='Y')
    make_light_switch("Switch_Entry", (ROOM_W / 2.0, ey - 0.70), axis='Y', face_sign=-1, aged=True)


def _window(prefix, center, w, h, along):
    """Frame ring + mullion + glass in a cut wall; `along` 'X' or 'Y'."""
    cx, cy, cz = center
    def B(nm, du, dz, su, sz):
        if along == 'X':
            make_box(f"{prefix}_{nm}", (cx + du, cy, cz + dz), (su, 0.10, sz), (0.40, 0.32, 0.24, 1.0))
        else:
            make_box(f"{prefix}_{nm}", (cx, cy + du, cz + dz), (0.10, su, sz), (0.40, 0.32, 0.24, 1.0))
    B("Frame_Head", 0.0, h / 2.0 - 0.035, w, 0.07)
    B("Frame_Sill", 0.0, -h / 2.0 + 0.035, w, 0.07)
    B("Frame_JambA", -w / 2.0 + 0.035, 0.0, 0.07, h - 0.14)
    B("Frame_JambB", w / 2.0 - 0.035, 0.0, 0.07, h - 0.14)
    B("Frame_Mullion", 0.0, 0.0, 0.04, h - 0.14)
    if along == 'X':
        make_box(f"{prefix}_Glass", (cx, cy, cz), (w - 0.14, 0.01, h - 0.14), (0.45, 0.52, 0.60, 0.5))
    else:
        make_box(f"{prefix}_Glass", (cx, cy, cz), (0.01, w - 0.14, h - 0.14), (0.45, 0.52, 0.60, 0.5))


def build_windows():
    _window("Kitchen_Window", (-ROOM_W / 2.0, WIN_W[0], WIN_W[1]), WIN_W[2], WIN_W[3], 'Y')
    _window("S_Window", (WIN_S[0], 0.0, WIN_S[1]), WIN_S[2], WIN_S[3], 'X')
    _window("N_Window", (WIN_N[0], ROOM_D, WIN_N[1]), WIN_N[2], WIN_N[3], 'X')
    # the S window's interior sill, the crow's marks on it
    make_box("S_Window_Sill", (WIN_S[0], YS + 0.10, WIN_S[1] - WIN_S[3] / 2.0 - 0.015), (WIN_S[2] + 0.14, 0.22, 0.03), (0.80, 0.78, 0.72, 1.0))
    for mi in range(5):
        make_box(f"Sill_Mark_{mi}", (WIN_S[0] - 0.20 + mi * 0.09, YS + 0.08 + (mi % 2) * 0.05, WIN_S[1] - WIN_S[3] / 2.0 + 0.001), (0.03, 0.02, 0.002), (0.90, 0.90, 0.86, 1.0))
    make_box("N_Window_Sill", (WIN_N[0], YN - 0.08, WIN_N[1] - WIN_N[3] / 2.0 - 0.015), (WIN_N[2] + 0.14, 0.18, 0.03), (0.80, 0.78, 0.72, 1.0))
    # curtain on the kitchen window, pushed to one side
    make_cyl("Kitchen_Window_Rod", (XW + 0.07, WIN_W[0], WIN_W[1] + WIN_W[3] / 2.0 + 0.10), 0.012, WIN_W[2] + 0.40, COL_STEEL, segments=6, axis='Y')
    make_box("Kitchen_Window_Curtain", (XW + 0.07, WIN_W[0] + WIN_W[2] / 2.0 + 0.05, WIN_W[1] + 0.08), (0.05, 0.26, 1.10), (0.86, 0.80, 0.66, 1.0))
    for nm, y in (("A", WIN_W[0] - WIN_W[2] / 2.0 - 0.17), ("B", WIN_W[0] + WIN_W[2] / 2.0 + 0.17)):
        make_box(f"Kitchen_Window_Rod_Bracket_{nm}", (XW + 0.035, y, WIN_W[1] + WIN_W[3] / 2.0 + 0.10), (0.07, 0.02, 0.02), COL_STEEL)


def build_kitchen_run():
    """The W wall: fridge, stove, the sink under the alley window, the
    upper cupboards either side of it."""
    fx = XW + 0.33
    make_chamfer_box("Fridge", (fx, 0.52, 0.85), (0.66, 0.70, 1.70), COL_ENAMEL)
    make_box("Fridge_Seam", (fx + 0.332, 0.52, 1.24), (0.004, 0.66, 0.012), (0.62, 0.62, 0.60, 1.0))
    make_box("Fridge_Handle", (fx + 0.35, 0.80, 0.95), (0.03, 0.03, 0.42), COL_STEEL)
    make_box("Fridge_Photo", (fx + 0.334, 0.40, 1.45), (0.004, 0.10, 0.14), (0.52, 0.58, 0.62, 1.0))
    cy0, cy1 = 0.92, 3.20
    ccy, cl = (cy0 + cy1) / 2.0, cy1 - cy0
    make_box("Counter", (XW + 0.31, ccy, 0.44), (0.62, cl, 0.88), COL_CAB)
    make_box("Counter_Top", (XW + 0.32, ccy, 0.905), (0.66, cl + 0.04, 0.05), COL_TOP)
    for i in range(4):
        y = cy0 + cl * (i + 0.5) / 4.0
        make_box(f"Counter_Door_{i}", (XW + 0.625, y, 0.46), (0.01, cl / 4.0 - 0.04, 0.70), (0.62, 0.66, 0.58, 1.0))
        make_box(f"Counter_Pull_{i}", (XW + 0.635, y + cl / 8.0 - 0.06, 0.74), (0.012, 0.02, 0.10), P.METAL_BLACK)
    # two-burner stove top and the kettle on it
    sy = 1.30
    make_box("Stove", (XW + 0.32, sy, 0.94), (0.50, 0.56, 0.02), (0.18, 0.18, 0.18, 1.0))
    for bi, oy in enumerate((-0.13, 0.13)):
        make_cyl(f"Stove_Burner_{bi}", (XW + 0.32, sy + oy, 0.955), 0.09, 0.01, (0.30, 0.22, 0.18, 1.0), segments=12)
    kz = 0.96
    make_lathe("Kettle", (XW + 0.32, sy - 0.13, kz), [(0.0, 0.0), (0.085, 0.0), (0.095, 0.05), (0.09, 0.13), (0.06, 0.16), (0.035, 0.165), (0.035, 0.18), (0.0, 0.18)], COL_STEEL, segments=12)
    make_tube("Kettle_Spout", [(XW + 0.40, sy - 0.13, kz + 0.085), (XW + 0.47, sy - 0.13, kz + 0.155), (XW + 0.50, sy - 0.13, kz + 0.195)], 0.012, COL_STEEL, segments=6)
    make_tube("Kettle_Bail", [(XW + 0.32, sy - 0.19, kz + 0.165), (XW + 0.32, sy - 0.17, kz + 0.255), (XW + 0.32, sy - 0.09, kz + 0.255), (XW + 0.32, sy - 0.07, kz + 0.165)], 0.008, (0.18, 0.17, 0.16, 1.0), segments=5)
    # the sink under the window, the pour-over cone and a mug beside it
    make_box("Sink", (XW + 0.33, WIN_W[0], 0.934), (0.42, 0.50, 0.012), COL_STEEL)
    make_box("Sink_Bowl", (XW + 0.33, WIN_W[0], 0.938), (0.34, 0.42, 0.004), (0.40, 0.42, 0.44, 1.0))
    make_cyl("Sink_Faucet", (XW + 0.07, WIN_W[0], 1.0), 0.016, 0.16, COL_STEEL, segments=6)
    make_box("Sink_Spout", (XW + 0.14, WIN_W[0], 1.07), (0.14, 0.022, 0.022), COL_STEEL)
    make_lathe("Pour_Cone", (XW + 0.32, 2.88, 0.93), [(0.03, 0.0), (0.03, 0.02), (0.045, 0.03), (0.075, 0.10), (0.065, 0.10), (0.04, 0.035), (0.0, 0.035)], (0.86, 0.82, 0.74, 1.0), segments=10)
    make_lathe("Pour_Mug", (XW + 0.50, 2.88, 0.93), [(0.0, 0.0), (0.04, 0.0), (0.042, 0.09), (0.0, 0.09)], (0.30, 0.34, 0.40, 1.0), segments=10)
    # upper cupboards (closed) left of the window
    make_box("Upper_Cupboard", (XW + 0.17, 1.18, 1.85), (0.34, 0.52, 0.70), COL_CAB)
    make_box("Upper_Cupboard_Door", (XW + 0.345, 1.18, 1.85), (0.01, 0.48, 0.64), (0.62, 0.66, 0.58, 1.0))
    make_wall_outlet("Outlet_Counter", (-ROOM_W / 2.0, 1.75), axis='Y', face_sign=1, z=1.12, aged=True)
    make_tube("Kettle_Cord", [(XW + 0.40, 1.20, 0.96), (XW + 0.03, 1.75, 1.12)], 0.006, (0.16, 0.16, 0.18, 1.0), segments=4)
    make_box("Kitchen_Mat", (XW + 0.98, 2.0, 0.006), (0.60, 1.30, 0.008), (0.52, 0.44, 0.34, 1.0))


def build_kitchen_table():
    """The table the charred wood is laid out on (ch9: "Finn was at the
    kitchen table"); three chairs; the hexagon, the stick in its sleeve."""
    wood = (0.44, 0.32, 0.20, 1.0)
    tx, ty, T = 0.30, 1.95, 0.765
    make_chamfer_box("Kitchen_Table", (tx, ty, 0.74), (1.20, 0.84, 0.05), wood)
    for lx, ly in ((-0.53, -0.35), (0.53, -0.35), (-0.53, 0.35), (0.53, 0.35)):
        make_box(f"KT_Leg_{lx:+.2f}_{ly:+.2f}", (tx + lx, ty + ly, 0.37), (0.05, 0.05, 0.72), wood)
    make_chair("KT_Chair_S", tx, ty - 0.72, yaw=0.0, wood=wood, w=0.40)
    make_chair("KT_Chair_N", tx, ty + 0.72, yaw=math.pi, wood=wood, w=0.40)
    make_chair("KT_Chair_E", tx + 0.92, ty, yaw=math.pi / 2.0, wood=wood, w=0.40)
    # the cloth, the five pieces of charred wood laid out in a shape that is not random
    make_chamfer_box("Folded_Cloth", (tx + 0.10, ty, T + 0.004), (0.46, 0.36, 0.008), (0.82, 0.78, 0.68, 1.0))
    for wi, (ox, oy, rz) in enumerate(((-0.08, -0.06, 0.0), (0.04, -0.07, 0.0), (0.12, 0.02, 0.0), (0.02, 0.07, 0.0), (-0.10, 0.05, 0.0))):
        make_box(f"Charred_Wood_{wi}", (tx + 0.10 + ox, ty + oy, T + 0.020), (0.09, 0.06, 0.025), (0.10, 0.09, 0.08, 1.0))
    # THE HEXAGON on its own cloth at the west end
    cedar, cedar_dk = (0.55, 0.38, 0.26, 1.0), (0.44, 0.30, 0.20, 1.0)
    hx, hy = tx - 0.36, ty
    make_box("Hexagon_Cloth", (hx, hy, T + 0.002), (0.30, 0.28, 0.004), (0.78, 0.74, 0.64, 1.0))
    for hi in range(6):
        ang = math.pi / 3.0 * hi + math.pi / 6.0
        make_box(f"Hexagon_Ring_{hi}", (hx + 0.095 * math.cos(ang), hy + 0.095 * math.sin(ang), T + 0.013), (0.065, 0.065, 0.018), cedar)
    make_cyl("Hexagon_Center_Face", (hx, hy, T + 0.012), 0.040, 0.016, cedar_dk, segments=12)
    make_cyl("Hexagon_Face_Inlay", (hx, hy, T + 0.0215), 0.022, 0.003, (0.62, 0.46, 0.32, 1.0), segments=10)
    make_box("Hexagon_Aria_Piece", (hx + 0.115, hy - 0.11, T + 0.014), (0.060, 0.045, 0.020), cedar)
    # THE STICK in its waxed-paper sleeve, east end
    make_box("Stick_Sleeve", (tx + 0.44, ty + 0.18, T + 0.010), (0.26, 0.09, 0.020), (0.88, 0.84, 0.72, 1.0))
    make_box("Stick_Label", (tx + 0.44, ty + 0.18, T + 0.021), (0.10, 0.05, 0.002), (0.96, 0.95, 0.92, 1.0))
    # "You eat?" — the plate Kai put in front of him (ch9), and the paper bag (ch18)
    make_cyl("Food_Plate", (tx + 0.25, ty - 0.25, T + 0.006), 0.12, 0.012, (0.92, 0.90, 0.86, 1.0), segments=14)
    make_box("Food_Sandwich", (tx + 0.25, ty - 0.25, T + 0.032), (0.12, 0.09, 0.04), (0.82, 0.66, 0.40, 1.0))
    make_box("Paper_Bag", (tx + 0.50, ty + 0.30, T + 0.11), (0.16, 0.10, 0.22), (0.68, 0.54, 0.36, 1.0))
    make_lathe("Table_Mug", (tx + 0.42, ty - 0.20, T), [(0.0, 0.0), (0.042, 0.0), (0.044, 0.09), (0.0, 0.09)], (0.86, 0.84, 0.78, 1.0), segments=10)


def build_living():
    """Finn's desk on the S wall, the low bookcase, the space heater in
    one corner and the nine-month duffel in the other."""
    wood = COL_WOOD
    make_box("Desk_Top", (DESK_X, DESK_Y, 0.74), (1.10, 0.60, 0.04), wood)
    for li, (ox, oy) in enumerate(((-0.49, -0.24), (0.49, -0.24), (-0.49, 0.24), (0.49, 0.24))):
        make_lathe(f"Desk_Leg_{li}", (DESK_X + ox, DESK_Y + oy, 0.0), [(0.022, 0.0), (0.026, 0.03), (0.018, 0.08), (0.02, 0.45), (0.028, 0.52), (0.02, 0.60), (0.024, 0.72)], wood, segments=8)
    make_box("Desk_Apron", (DESK_X, DESK_Y, 0.70), (1.02, 0.52, 0.04), (0.40, 0.29, 0.18, 1.0))
    make_lamp("Lamp", DESK_X - 0.38, DESK_Y + 0.12, base_z=0.76, h=0.55, shade_col=COL_ACCENT, body_col=P.METAL_BLACK)
    make_chair("Desk_Chair", DESK_X, DESK_Y + 0.62, yaw=math.pi, wood=wood, seat_col=COL_ACCENT, w=0.42)
    make_box("Finns_Phone", (DESK_X + 0.20, DESK_Y - 0.10, 0.7655), (0.070, 0.140, 0.011), (0.13, 0.13, 0.15, 1.0))
    make_box("Finns_Notebook", (DESK_X - 0.02, DESK_Y + 0.02, 0.766), (0.150, 0.200, 0.012), (0.36, 0.30, 0.24, 1.0))
    make_box("Finns_Notebook_Wire", (DESK_X - 0.101, DESK_Y + 0.02, 0.767), (0.010, 0.200, 0.014), (0.55, 0.56, 0.58, 1.0))
    make_box("Carved_Cedar", (DESK_X + 0.38, DESK_Y + 0.10, 0.785), (0.030, 0.020, 0.050), (0.52, 0.34, 0.22, 1.0))
    for bi in range(3):
        make_box(f"Desk_Book_{bi}", (DESK_X - 0.12 + bi * 0.08, DESK_Y - 0.20, 0.86), (0.06, 0.18, 0.20), P.SNACK_TINTS[bi % len(P.SNACK_TINTS)])
    make_wall_outlet("Outlet_Desk", (DESK_X - 0.60, 0.0), axis='X', face_sign=1, z=0.30, aged=True)
    # the low bookcase under nothing, beside the S window
    bx = 0.25
    make_box("Bookcase_Back", (bx, YS + 0.01, 0.45), (1.20, 0.02, 0.90), wood)
    for nm, ox in (("A", -0.59), ("B", 0.59)):
        make_box(f"Bookcase_Side_{nm}", (bx + ox, YS + 0.16, 0.45), (0.02, 0.30, 0.90), wood)
    for si, z in enumerate((0.04, 0.46, 0.89)):
        make_box(f"Bookcase_Shelf_{si}", (bx, YS + 0.16, z), (1.16, 0.30, 0.025), wood)
    for si, z in enumerate((0.04, 0.46)):
        for k in range(9):
            if k == 6:
                continue
            h = 0.22 + 0.03 * (k % 3)
            make_box(f"Bookcase_Book_{si}_{k}", (bx - 0.52 + k * 0.12, YS + 0.20, z + 0.0125 + h / 2.0), (0.05 + 0.01 * (k % 2), 0.20, h), P.SNACK_TINTS[(k + si) % len(P.SNACK_TINTS)])
    # "He banked the space heater in the corner"
    hx, hy = XE - 0.24, PART_Y - 0.36
    make_chamfer_box("Space_Heater", (hx, hy, 0.32), (0.22, 0.46, 0.60), (0.44, 0.40, 0.36, 1.0))
    for gi in range(6):
        make_box(f"Space_Heater_Grille_{gi}", (hx - 0.112, hy, 0.16 + gi * 0.06), (0.004, 0.40, 0.012), (0.20, 0.18, 0.16, 1.0))
    make_box("Space_Heater_Glow", (hx - 0.113, hy, 0.30), (0.002, 0.36, 0.26), (1.0, 0.46, 0.18, 1.0))
    make_box("Space_Heater_Dial", (hx, hy + 0.10, 0.625), (0.06, 0.06, 0.02), (0.14, 0.14, 0.14, 1.0))
    make_wall_outlet("Outlet_Heater", (ROOM_W / 2.0, hy - 0.40), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_tube("Space_Heater_Cord", [(hx + 0.08, hy - 0.20, 0.10), (XE - 0.03, hy - 0.40, 0.30)], 0.006, (0.16, 0.16, 0.18, 1.0), segments=4)
    # the duffel, SE corner, nine months — soft canvas, and its patch on the wall
    make_blob("Duffel", (XE - 0.40, 0.42, 0.17), 0.30, (0.34, 0.36, 0.30, 1.0), noise=0.14, seed=7, squash=0.55)
    make_box("Duffel_Strap", (XE - 0.40, 0.42, 0.34), (0.50, 0.06, 0.03), (0.24, 0.25, 0.22, 1.0))
    make_box("Duffel_Zip", (XE - 0.40, 0.36, 0.335), (0.44, 0.012, 0.006), (0.72, 0.70, 0.62, 1.0))
    make_box("Duffel_Patch", (XE - 0.004, 0.42, 0.26), (0.004, 0.50, 0.22), (0.80, 0.70, 0.60, 1.0))
    # a coat on a hook by the door, his boots under it
    make_box("Coat_Hook", (XE - 0.03, ey_hook(), 1.70), (0.05, 0.02, 0.02), COL_STEEL)
    make_box("Coat_Canvas", (XE - 0.07, ey_hook(), 1.28), (0.08, 0.46, 0.84), (0.46, 0.40, 0.28, 1.0))
    for k, oy in enumerate((-0.08, 0.08)):
        make_box(f"Boot_{k}", (XE - 0.20, ey_hook() + oy, 0.08), (0.28, 0.11, 0.16), (0.22, 0.18, 0.14, 1.0))


def ey_hook():
    return EDOOR[0] + 0.70


def build_bedroom():
    # the raised platform bed on turned posts, head at the W wall, crates under it
    bx, by, bw, bd = BED_X, BED_Y, 2.06, 1.44
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_lathe(f"Bed_Post_{sx}_{sy}", (bx + sx * (bw / 2.0 - 0.05), by + sy * (bd / 2.0 - 0.05), 0.0),
                       [(0.04, 0.0), (0.045, 0.03), (0.032, 0.08), (0.036, 0.40), (0.045, 0.49), (0.045, 0.56), (0.03, 0.60), (0.035, 0.66), (0.0, 0.70)],
                       COL_WOOD, segments=8)
    make_tube("Bed_Foot_Rail", [(bx + bw / 2.0 - 0.05, by - bd / 2.0 + 0.05, 0.63), (bx + bw / 2.0 - 0.05, by + bd / 2.0 - 0.05, 0.63)], 0.016, COL_WOOD, segments=6)
    make_box("Bed_Deck", (bx, by, 0.52), (bw, bd, 0.06), COL_WOOD)
    make_chamfer_box("Bed_Mattress", (bx, by, 0.63), (bw - 0.10, bd - 0.10, 0.16), (0.92, 0.86, 0.78, 1.0))
    make_chamfer_box("Bed_Blanket", (bx + 0.22, by, 0.77), (bw - 0.56, bd - 0.20, 0.12), (0.44, 0.40, 0.34, 1.0))   # the wool blanket
    make_chamfer_box("Bed_Pillow", (bx - bw / 2.0 + 0.30, by, 0.77), (0.32, bd - 0.30, 0.12), P.PAPER)
    for ci, ox in enumerate((-0.62, 0.0, 0.62)):
        c0 = (bx + ox, by)
        for k, (dx, sxx) in enumerate(((-0.19, 0.02), (0.19, 0.02))):
            make_box(f"Bed_Crate_{ci}_Side_{k}", (c0[0] + dx, c0[1], 0.14), (sxx, 0.90, 0.28), (0.40, 0.30, 0.20, 1.0))
        for k, dz in enumerate((0.04, 0.14, 0.24)):
            make_box(f"Bed_Crate_{ci}_Slat_{k}", (c0[0], c0[1] - 0.44, dz), (0.36, 0.02, 0.05), (0.40, 0.30, 0.20, 1.0))
        make_box(f"Bed_Crate_{ci}_Bottom", (c0[0], c0[1], 0.01), (0.36, 0.88, 0.02), (0.34, 0.24, 0.16, 1.0))
    # the side table at the head (the reader and its headset, "beeping the end-of-stick beep")
    nx, ny = XW + 0.25, by + bd / 2.0 + 0.30
    make_chamfer_box("Nightstand", (nx, ny, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Reader", (nx + 0.06, ny - 0.08, 0.571), (0.100, 0.150, 0.020), (0.22, 0.22, 0.25, 1.0))
    make_box("Reader_Screen", (nx + 0.06, ny - 0.08, 0.5825), (0.080, 0.110, 0.002), (0.30, 0.38, 0.46, 1.0))
    for ci2, cy2 in enumerate((ny + 0.05, ny + 0.12)):
        make_cyl(f"Headset_Cup_{ci2}", (nx - 0.10, cy2, 0.575), 0.030, 0.030, (0.18, 0.18, 0.20, 1.0), segments=8)
    make_box("Headset_Band", (nx - 0.10, ny + 0.085, 0.596), (0.012, 0.10, 0.012), (0.24, 0.24, 0.26, 1.0))
    make_box("Bedside_Clock", (nx + 0.08, ny + 0.10, 0.61), (0.15, 0.08, 0.10), P.METAL_BLACK)
    # THE CHAIR BESIDE THE BED, the crow on its back
    pcx, pcy = bx + bw / 2.0 + 0.55, by + 0.10
    make_chair("Perch_Chair", pcx, pcy, yaw=math.pi / 2.0, wood=(0.36, 0.26, 0.17, 1.0), w=0.42)
    make_cyl("Perch_Chair_Rail", (pcx + 0.17, pcy, 0.93), 0.022, 0.42, (0.30, 0.22, 0.14, 1.0), segments=6, axis='Y')
    make_crow("Crow", pcx + 0.17, pcy, 0.952, facing=1.0)
    make_box("Wool_Socks", (bx + bw / 2.0 + 0.25, by - 0.55, 0.012), (0.20, 0.14, 0.02), (0.62, 0.58, 0.50, 1.0))
    make_cyl("Rug", (bx + bw / 2.0 + 0.35, by - 0.30, 0.010), 0.62, 0.006, COL_ACCENT, segments=20)
    # the dresser on the E wall: the change bowl and the truck keys
    dy = 5.6
    make_chamfer_box("Dresser", (XE - 0.24, dy, 0.48), (0.46, 1.10, 0.96), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (XE - 0.475, dy, 0.24 + di * 0.27), (0.01, 0.98, 0.22), (0.34, 0.24, 0.16, 1.0))
        for pi_, py_ in enumerate((dy - 0.28, dy + 0.28)):
            make_cyl(f"Dresser_Pull_{di}_{pi_}", (XE - 0.485, py_, 0.26 + di * 0.27), 0.012, 0.01, P.METAL_BLACK, axis='X', segments=6)
    make_lathe("Dresser_Change_Bowl", (XE - 0.24, dy - 0.25, 0.96), [(0.0, 0.0), (0.05, 0.0), (0.09, 0.04), (0.08, 0.045), (0.0, 0.01)], (0.40, 0.46, 0.50, 1.0), segments=12)
    make_box("Dresser_Keys", (XE - 0.20, dy + 0.15, 0.965), (0.08, 0.04, 0.01), COL_STEEL)
    # the clothes rail on the N wall W of the window: shirts, the thermal, a jacket
    rx0, rx1 = -2.9, -1.3
    for k, x in enumerate((rx0, rx1)):
        make_box(f"Clothes_Rail_Post_{k}", (x, YN - 0.30, 0.80), (0.04, 0.04, 1.60), P.METAL_BLACK)
        make_box(f"Clothes_Rail_Foot_{k}", (x, YN - 0.30, 0.02), (0.06, 0.46, 0.04), P.METAL_BLACK)
    make_cyl("Clothes_Rail_Bar", ((rx0 + rx1) / 2.0, YN - 0.30, 1.58), 0.014, rx1 - rx0, P.METAL_BLACK, segments=6, axis='X')
    for k, (ox, col, ln) in enumerate(((0.20, (0.36, 0.40, 0.46, 1.0), 0.80), (0.45, (0.70, 0.66, 0.58, 1.0), 0.75), (0.70, (0.30, 0.34, 0.30, 1.0), 0.95),
                                         (0.95, (0.56, 0.30, 0.26, 1.0), 0.78), (1.20, (0.22, 0.24, 0.30, 1.0), 0.90))):
        make_box(f"Clothes_Hanger_{k}", (rx0 + ox, YN - 0.30, 1.555), (0.02, 0.36, 0.03), (0.40, 0.30, 0.20, 1.0))
        make_box(f"Clothes_Garment_{k}", (rx0 + ox, YN - 0.30, 1.54 - ln / 2.0), (0.06, 0.44, ln), col)
    # the bench at the bed's foot, the folded clothes and the jeans on it
    fbx = BED_X + 2.06 / 2.0 + 0.30
    make_box("Foot_Bench_Seat", (fbx, BED_Y - 0.62, 0.43), (0.40, 0.70, 0.04), COL_WOOD)
    for k, oy in enumerate((-0.30, 0.30)):
        make_box(f"Foot_Bench_Leg_{k}", (fbx, BED_Y - 0.62 + oy, 0.205), (0.36, 0.04, 0.41), COL_WOOD)
    make_box("Folded_Thermal", (fbx, BED_Y - 0.75, 0.475), (0.30, 0.26, 0.05), (0.62, 0.60, 0.56, 1.0))
    make_box("Folded_Jeans", (fbx, BED_Y - 0.48, 0.47), (0.30, 0.22, 0.04), (0.26, 0.32, 0.46, 1.0))
    # a stack of books on the floor by the head of the bed
    for k in range(4):
        make_box(f"Floor_Books_{k}", (BED_X - 0.6 + 0.02 * (k % 2), BED_Y - 1.00, 0.03 + k * 0.05), (0.22, 0.16, 0.05), P.SNACK_TINTS[(k + 2) % len(P.SNACK_TINTS)])
    make_floor_plant("Plant", (XE - 0.40, YN - 0.40, 0.0), palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.44, 0.34, 0.24, 1.0)})
    make_faded_poster("Poster_W", (XW + 0.0035, BED_Y, 1.75), into_room=+1)
    make_wall_outlet("Outlet_Bed", (-ROOM_W / 2.0, BED_Y + 1.25), axis='Y', face_sign=1, aged=True)
    make_light_switch("Switch_Bedroom", (PDOOR[0] + PDOOR[2] / 2.0 + 0.20, PART_Y - 0.055), axis='X', face_sign=1, aged=True)


def build_ceiling():
    for nm, (x, y) in (("Kitchen_Light", (0.30, 1.95)), ("Bedroom_Light", (-1.0, 5.7))):
        make_lathe(nm, (x, y, CEIL), [(0.0, -0.14), (0.09, -0.13), (0.14, -0.08), (0.16, -0.02), (0.16, 0.0), (0.0, 0.0)], (0.94, 0.88, 0.70, 1.0), segments=12)
        make_cyl(f"{nm}_Ring", (x, y, CEIL - 0.01), 0.17, 0.02, (0.62, 0.52, 0.30, 1.0), segments=12)
    make_smoke_detector("Smoke", (1.5, 2.6, CEIL))


def build_wear():
    floor_dk = (COL_FLOOR[0] * 0.84, COL_FLOOR[1] * 0.84, COL_FLOOR[2] * 0.84, 1.0)
    make_traffic_wear("Wear_Entry", [(XE - 0.4, EDOOR[0]), (1.6, EDOOR[0]), (1.6, PART_Y + 0.8), (BED_X + 1.4, PART_Y + 1.3)], width=0.60, tint=floor_dk)
    make_traffic_wear("Wear_Kitchen", [(1.0, 2.6), (XW + 1.0, 2.6), (XW + 1.0, 1.0)], width=0.55, tint=floor_dk)
    for ci, (cx, cy) in enumerate(((0.30, 1.23), (0.30, 2.67), (DESK_X, DESK_Y + 0.62))):
        make_floor_stain(f"Wear_Seat_{ci}", (cx, cy), radius=0.25, tint=floor_dk, segments=10)
    make_box("Wear_Drip", (XW + 0.627, WIN_W[0], 0.60), (0.004, 0.30, 0.20), (0.44, 0.38, 0.30, 1.0))


def build_outside():
    """What the three windows see. W: two floors down, the alley behind
    the bakery — its back wall across the alley, the back door, the
    back-kitchen light over it. S: Hemlock, the roofline, the sea band.
    N: the neighbour's roof and the treeline."""
    gz = -3.0
    make_box("Out_Alley", (XW - 3.2, ROOM_D / 2.0, gz), (6.0, 30.0, 0.05), (0.26, 0.26, 0.28, 1.0))
    bwx = XW - 6.4
    make_box("Out_Bakery_Wall", (bwx, ROOM_D / 2.0, gz + 3.4), (0.30, 30.0, 6.8), (0.56, 0.44, 0.34, 1.0))
    make_box("Out_Bakery_Door", (bwx + 0.16, 2.6, gz + 1.05), (0.04, 0.92, 2.10), (0.36, 0.28, 0.20, 1.0))
    make_cyl("Out_Bakery_Light_Shade", (bwx + 0.22, 2.6, gz + 2.42), 0.10, 0.12, (0.30, 0.32, 0.30, 1.0), axis='X', segments=10)
    make_cyl("Out_Bakery_Light_Bulb", (bwx + 0.29, 2.6, gz + 2.42), 0.035, 0.05, (1.0, 0.85, 0.55, 1.0), axis='X', segments=8)
    for wi, wy in enumerate((0.4, 5.0)):
        make_box(f"Out_Bakery_Window_{wi}", (bwx + 0.16, wy, gz + 4.5), (0.04, 1.2, 1.0), (0.30, 0.34, 0.40, 1.0))
    make_box("Out_Alley_Bin", (bwx + 0.9, 4.6, gz + 0.55), (1.1, 0.8, 1.1), (0.26, 0.36, 0.30, 1.0))
    make_box("Out_Alley_Puddle", (XW - 3.0, 2.4, gz + 0.03), (1.6, 0.9, 0.01), (0.36, 0.38, 0.44, 1.0))
    make_box("Out_S_Ground", (0.0, -4.0, -3.03), (16.0, 7.0, 0.05), (0.34, 0.34, 0.36, 1.0))
    make_box("Out_S_Roofline", (0.0, -7.5, -1.0), (18.0, 0.4, 4.4), (0.44, 0.40, 0.36, 1.0))
    make_box("Out_S_Sea", (0.0, -14.0, 1.4), (40.0, 0.3, 0.9), (0.42, 0.52, 0.60, 1.0))
    make_box("Out_N_Ground", (0.0, ROOM_D + 4.0, -3.03), (16.0, 7.0, 0.05), (0.30, 0.36, 0.26, 1.0))
    make_box("Out_N_House", (1.5, ROOM_D + 4.5, -0.6), (7.0, 3.2, 4.8), (0.62, 0.58, 0.52, 1.0))
    make_prism("Out_N_Roof", (1.5, ROOM_D + 4.5, 1.8), [(-3.8, 0.0), (3.8, 0.0), (0.0, 1.6)], 3.4, (0.32, 0.26, 0.22, 1.0), axis="Y")
    make_box("Out_N_Treeline", (0.0, ROOM_D + 10.0, 1.5), (24.0, 0.4, 6.0), (0.13, 0.22, 0.17, 1.0))


def main():
    clear_scene()
    build_shell()
    build_windows()
    build_kitchen_run()
    build_kitchen_table()
    build_living()
    build_bedroom()
    build_ceiling()
    build_wear()
    build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/finn_apartment.glb"))
    print(f"\n[build_finn_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
