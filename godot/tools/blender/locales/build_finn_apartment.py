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

DRAFT 5 (pass 331, 2026-11-10) — read by render on eighteen real lines.
  - THE CROW IS IN TWO ROOMS. "The crow was on the back of the chair
    across from him" (ch5, ch9: the kitchen), "on the back of the chair
    beside the bed" (ch12, ch18). Only the bedroom crow was built, so
    every kitchen crow line cut to the bed. `Kitchen_Crow` perches on the
    N kitchen chair; the day view strips the bedroom bird, the night view
    the kitchen one, the dusk view (ch9, ch18_stick) keeps both — no lens
    there sees the two at once.
  - THE RADIO ("He could hear the radio going faintly through the door",
    ch5) was lost in draft 4's rebuild: a taped portable on a small
    console on the partition wall, in the frame of the set's most-used
    closeup, which looked at a bare wall.
  - THE CLOSET ("He went to the closet. His own wax canvas coat was on
    the hook", ch18): east of the bedroom doorway, one leaf open on the
    coat. The cap on its peg by the entry.
  - SOUTH OF THE S WINDOW: "South was the direction of Cape Perpetua ...
    the tower on the bluff above old-Yachats. The face was looking out at
    the town" (ch12) — it saw a flat roofline and a band of sea (the sea
    is west). Town roofs stepping down, the bluff, the tower, the cape.
  (The text has ONE kitchen window, facing south over the alley; the set
  has the sink window over the alley on the W wall and a S window to the
  town, each with its own picture in the roster since pass 203. Left.)

Draft 6 targets: a pre-dawn twin of the night view so ch12_morning's
five kitchen crow lines find the crow in the kitchen; a bathroom door
off the bedroom; the kitchen's dish rack and a towel on the oven bar;
the crates' contents; rain on the alley; the notebook to palm size.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_blob, make_cyl, make_lathe, make_tube, make_prism, make_rot_box, export_glb
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
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM}, style="plank")
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
    # THE CROW ON THE CHAIR ACROSS FROM HIM (draft 5): the kitchen bird, on
    # the N chair's back, looking at the wood
    make_cyl("KT_Chair_N_Perch_Rail", (tx, ty + 0.72 + 0.17, 0.93), 0.022, 0.40, (0.36, 0.26, 0.17, 1.0), segments=6, axis='X')
    make_crow("Kitchen_Crow", tx, ty + 0.72 + 0.17, 0.952, facing=1.0)
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


def build_radio_2026_11():
    """THE RADIO (ch5: "He could hear the radio going faintly through the
    door"; vol7 ch2: "the shortwave receiver from his grandfather"). A
    battery portable held together with electrical tape on its own small
    console against the partition wall, the log notebook and a pencil
    beside it, the roll of tape, spare batteries. Small, worn: a rig,
    not a shack."""
    wood = (0.40, 0.29, 0.19, 1.0)
    cx, cy, T = -1.35, PART_Y - 0.06 - 0.20, 0.70
    make_chamfer_box("Radio_Console_Top", (cx, cy, T - 0.015), (0.80, 0.36, 0.03), wood)
    for li, (ox, oy) in enumerate(((-0.36, -0.14), (0.36, -0.14), (-0.36, 0.14), (0.36, 0.14))):
        make_box(f"Radio_Console_Leg_{li}", (cx + ox, cy + oy, (T - 0.03) / 2.0), (0.04, 0.04, T - 0.03), wood)
    make_box("Radio_Console_Shelf", (cx, cy, 0.22), (0.72, 0.30, 0.02), wood)
    bake = (0.30, 0.20, 0.14, 1.0); tape = (0.08, 0.08, 0.09, 1.0)
    rx, ry = cx - 0.12, cy + 0.03
    make_chamfer_box("Radio_Body", (rx, ry, T + 0.105), (0.34, 0.13, 0.21), bake)
    make_box("Radio_DialFace", (rx + 0.07, ry - 0.066, T + 0.145), (0.15, 0.004, 0.07), (0.88, 0.84, 0.70, 1.0))
    make_box("Radio_Dial_Needle", (rx + 0.05, ry - 0.069, T + 0.145), (0.004, 0.002, 0.06), (0.70, 0.16, 0.12, 1.0))
    for si in range(5):
        make_box(f"Radio_Speaker_Slat_{si}", (rx - 0.09, ry - 0.066, T + 0.06 + si * 0.025), (0.12, 0.004, 0.010), (0.16, 0.11, 0.08, 1.0))
    for ki, kx in enumerate((0.03, 0.11)):
        make_cyl(f"Radio_Knob_{ki}", (rx + kx, ry - 0.075, T + 0.065), 0.016, 0.02, (0.82, 0.78, 0.66, 1.0), axis='Y', segments=8)
    for ti, tx_ in enumerate((-0.135, 0.02)):
        make_box(f"Radio_Tape_Band_{ti}", (rx + tx_, ry, T + 0.105), (0.03, 0.134, 0.214), tape)
    make_box("Radio_Tape_Corner", (rx + 0.155, ry - 0.05, T + 0.19), (0.034, 0.034, 0.034), tape)
    make_tube("Radio_Antenna", [(rx + 0.14, ry + 0.04, T + 0.20), (rx + 0.20, ry + 0.05, T + 0.48), (rx + 0.25, ry + 0.055, T + 0.72)], 0.004, COL_STEEL, segments=4)
    make_box("Radio_Log_Notebook", (cx + 0.22, cy - 0.04, T + 0.007), (0.13, 0.19, 0.014), (0.26, 0.34, 0.30, 1.0))
    make_box("Radio_Log_Spiral", (cx + 0.152, cy - 0.04, T + 0.008), (0.008, 0.19, 0.016), (0.55, 0.56, 0.58, 1.0))
    make_cyl("Radio_Pencil", (cx + 0.22, cy - 0.04, T + 0.018), 0.004, 0.15, (0.86, 0.66, 0.20, 1.0), axis='Y', segments=6)
    make_lathe("Radio_Tape_Roll", (cx + 0.33, cy + 0.10, T), [(0.022, 0.0), (0.042, 0.0), (0.042, 0.02), (0.022, 0.02)], tape, segments=12)
    for bi in range(2):
        make_cyl(f"Radio_Battery_{bi}", (cx + 0.30 + bi * 0.035, cy - 0.13, T + 0.012), 0.012, 0.05, (0.72, 0.52, 0.18, 1.0), axis='Y', segments=8)
    make_wall_outlet("Outlet_Radio", (cx - 0.55, PART_Y + 0.04), axis='X', face_sign=-1, z=0.30, aged=True)   # the kit assumes a 20 cm wall; the partition is 12
    # the wool cap on its peg by the entry ("He pulled the wool cap over
    # his hair and the coat over the wool cap", ch9)
    py = ey_hook() + 0.36
    make_box("Cap_Peg", (XE - 0.03, py, 1.70), (0.05, 0.02, 0.02), COL_STEEL)
    make_blob("Wool_Cap", (XE - 0.07, py, 1.63), 0.085, (0.30, 0.34, 0.40, 1.0), noise=0.10, seed=4, squash=0.85)


def build_closet_2026_11():
    """THE CLOSET (ch18: "He went back to the bedroom ... He went to the
    closet. His own wax canvas coat was on the hook. He patted the right
    outside pocket."). East of the bedroom doorway against the
    partition: a built-in 1.5 m wide, one leaf standing open on the coat
    on its hook, the other shut on the rail."""
    wood = (0.70, 0.70, 0.64, 1.0)       # painted, like the walls
    y0 = PART_Y + 0.06                    # the partition's bedroom face
    x0, x1, dep, H = 2.50, XE, 0.62, 2.10
    make_box("Closet_Side_W", (x0 + 0.02, y0 + dep / 2.0, H / 2.0), (0.04, dep, H), wood)
    make_box("Closet_Top", ((x0 + x1) / 2.0, y0 + dep / 2.0, H + 0.02), (x1 - x0, dep, 0.04), wood)
    make_box("Closet_Fascia", ((x0 + x1) / 2.0, y0 + dep - 0.02, (H + 0.04 + CEIL) / 2.0), (x1 - x0, 0.04, CEIL - H - 0.04), wood)
    make_box("Closet_Mullion", ((x0 + 0.04 + x1) / 2.0, y0 + dep - 0.02, H / 2.0), (0.04, 0.04, H), wood)
    lw = (x1 - x0 - 0.04 - 0.04) / 2.0
    # the E leaf, shut
    make_box("Closet_Wardrobe_Door_E", (x1 - lw / 2.0, y0 + dep - 0.015, H / 2.0), (lw - 0.01, 0.03, H - 0.03), (0.66, 0.66, 0.60, 1.0))
    make_cyl("Closet_Wardrobe_Door_E_Knob", ((x0 + 0.04 + x1) / 2.0 + 0.07, y0 + dep + 0.012, 1.0), 0.016, 0.03, P.METAL_BLACK, axis='Y', segments=8)
    # the W leaf, standing open: hinged at the side panel, swung into the room
    a = math.radians(8.0)
    hx, hy = x0 + 0.05, y0 + dep
    make_rot_box("Closet_Wardrobe_Door_W", (hx - math.sin(a) * lw / 2.0, hy + math.cos(a) * lw / 2.0, H / 2.0), (0.03, lw - 0.01, H - 0.03),
                 (0.66, 0.66, 0.60, 1.0), yaw=a)
    # inside: the shelf, the rail and what hangs on it behind the shut leaf
    make_box("Closet_Shelf", ((x0 + 0.04 + x1) / 2.0, y0 + 0.20, 1.86), (x1 - x0 - 0.04, 0.40, 0.02), wood)
    make_cyl("Closet_Rail", ((x0 + 0.04 + x1) / 2.0, y0 + 0.30, 1.72), 0.013, x1 - x0 - 0.04, COL_STEEL, axis='X', segments=6)
    for gi, (gx, col, ln) in enumerate(((3.50, (0.34, 0.38, 0.44, 1.0), 0.86), (3.68, (0.62, 0.58, 0.50, 1.0), 0.78), (3.86, (0.28, 0.30, 0.26, 1.0), 0.92))):
        make_box(f"Closet_Hanger_{gi}", (gx, y0 + 0.30, 1.70), (0.02, 0.36, 0.03), (0.40, 0.30, 0.20, 1.0))
        make_box(f"Closet_Garment_{gi}", (gx, y0 + 0.30, 1.685 - ln / 2.0), (0.06, 0.42, ln), col)
    for bi in range(2):
        make_box(f"Closet_Shelf_Box_{bi}", (3.05 + bi * 0.50, y0 + 0.20, 1.87 + 0.09), (0.40, 0.30, 0.18), ((0.62, 0.52, 0.38, 1.0), (0.52, 0.46, 0.38, 1.0))[bi])
    # THE HOOK and the wax canvas coat, on the back wall behind the open leaf
    kx = 2.98
    make_box("Closet_Coat_Hook", (kx, y0 + 0.03, 1.66), (0.02, 0.06, 0.02), COL_STEEL)
    # pale waxed khaki: at (0.40, 0.34, 0.22) and again at (0.60, 0.50, 0.31) the
    # coat was a black cut-out in the night view — a third of the wall's light
    # in linear terms, and the night's painted pass crushes that to nothing
    wax = (0.78, 0.68, 0.46, 1.0)
    make_chamfer_box("Closet_Wax_Coat", (kx, y0 + 0.085, 1.17), (0.52, 0.10, 0.96), wax)
    make_box("Closet_Wax_Coat_Collar", (kx, y0 + 0.10, 1.63), (0.24, 0.09, 0.07), (0.50, 0.36, 0.22, 1.0))
    for si, sx in enumerate((-0.30, 0.30)):
        make_chamfer_box(f"Closet_Wax_Coat_Sleeve_{si}", (kx + sx, y0 + 0.085, 1.22), (0.11, 0.09, 0.70), (0.72, 0.62, 0.41, 1.0))
    for pi_, px in enumerate((-0.14, 0.14)):
        make_box(f"Closet_Wax_Coat_Pocket_{pi_}", (kx + px, y0 + 0.138, 0.95), (0.16, 0.008, 0.17), (0.68, 0.58, 0.38, 1.0))
        make_box(f"Closet_Wax_Coat_Flap_{pi_}", (kx + px, y0 + 0.144, 1.02), (0.17, 0.008, 0.05), (0.60, 0.50, 0.32, 1.0))
    # the notebook's corner out of the right outside pocket
    make_box("Closet_Pocket_Notebook", (kx - 0.14, y0 + 0.132, 1.045), (0.08, 0.012, 0.05), (0.26, 0.17, 0.11, 1.0))
    for bi, bx in enumerate((-0.10, 0.08)):
        make_box(f"Closet_Shoe_{bi}", (kx + bx, y0 + 0.22, 0.05), (0.10, 0.27, 0.10), (0.20, 0.17, 0.14, 1.0))


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
    dy = 6.2      # clear of the closet's leaves (draft 5: it stood 0.47 m in front of them at 5.6)
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
    # S: the town (draft 5). "South was the direction of Cape Perpetua ...
    # the tower on the bluff above old-Yachats. The face was looking out at
    # the town." Roofs stepping down from the window, the bluff, the tower
    # with its lit top floor, the cape past it. (It was one flat roofline
    # and a band of sea; the sea is west.)
    make_box("Out_S_Ground", (0.0, -22.0, -3.03), (70.0, 44.0, 0.05), (0.30, 0.32, 0.30, 1.0))
    make_box("Out_S_Street", (0.0, -5.0, -3.0), (70.0, 5.0, 0.03), (0.24, 0.24, 0.26, 1.0))
    roofs = ((0.36, 0.30, 0.26, 1.0), (0.30, 0.32, 0.34, 1.0), (0.40, 0.34, 0.28, 1.0), (0.28, 0.30, 0.28, 1.0))
    sides = ((0.62, 0.58, 0.52, 1.0), (0.54, 0.44, 0.36, 1.0), (0.58, 0.60, 0.56, 1.0), (0.50, 0.50, 0.46, 1.0))
    for hi, (hx_, hy_, hw_, hd_, hh_) in enumerate(((-7.5, -10.5, 6.0, 5.0, 3.4), (-0.6, -10.0, 5.2, 4.6, 2.6), (5.4, -11.0, 6.4, 5.2, 3.8),
                                                  (-11.0, -19.0, 7.0, 5.0, 2.4), (-3.2, -18.5, 6.0, 5.0, 1.8), (3.6, -19.5, 5.6, 4.8, 2.2),
                                                  (10.5, -18.5, 6.5, 5.0, 2.8), (-6.0, -27.0, 8.0, 5.0, 1.2), (4.5, -27.5, 9.0, 5.0, 1.4))):
        make_box(f"Out_S_House_{hi}", (hx_, hy_, -3.0 + hh_ / 2.0), (hw_, hd_, hh_), sides[hi % 4])
        make_prism(f"Out_S_House_{hi}_Roof", (hx_, hy_, -3.0 + hh_), [(-hw_ / 2.0 - 0.2, 0.0), (hw_ / 2.0 + 0.2, 0.0), (0.0, 1.3)], hd_ + 0.3, roofs[hi % 4], axis="Y")
        make_box(f"Out_S_House_{hi}_Window", (hx_ + hw_ * 0.18, hy_ + hd_ / 2.0 + 0.02, -3.0 + hh_ - 0.9), (0.7, 0.04, 0.8), (0.86, 0.72, 0.44, 1.0) if hi % 3 == 0 else (0.22, 0.26, 0.32, 1.0))
    make_box("Out_S_Bluff", (6.0, -46.0, 0.2), (46.0, 10.0, 6.4), (0.16, 0.24, 0.20, 1.0))
    make_box("Out_S_Bluff_Low", (-12.0, -42.0, -1.2), (40.0, 8.0, 3.6), (0.20, 0.28, 0.22, 1.0))
    make_box("Out_S_Tower", (9.0, -44.0, 7.2), (1.6, 1.6, 7.6), (0.50, 0.50, 0.48, 1.0))
    make_box("Out_S_Tower_Top", (9.0, -44.0, 11.3), (1.9, 1.9, 0.9), (0.42, 0.62, 0.48, 1.0))
    make_box("Out_S_Cape", (-22.0, -70.0, 2.5), (60.0, 12.0, 11.0), (0.20, 0.26, 0.28, 1.0))
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
    build_radio_2026_11()
    build_bedroom()
    build_closet_2026_11()
    build_ceiling()
    build_wear()
    build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/finn_apartment.glb"))
    print(f"\n[build_finn_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
