"""copy_shop — vol 2's copy shop in Small Wood on the graveyard shift, and
vol 4's office after hours (draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Two places in one GLB that never share a frame.

THE COPY SHOP (origin) — "a small ugly copy shop" that "used to be an office
supply store", the narrator alone on "the first graveyard shift".
  "every third long florescent bulb gasps as the end nears"
                                       → Fluor_* rows, every third tube dim
  "The walls are greenish black in places"                 → Grime_*
  the back room "full of boxes" of unsold merchandise, where he reads on
   his breaks                          → the back room through the N doorway
  "the wastebasket of the copy shop, the stapled copy page"
                                       → Wastebasket, Stapled_Copy
  the customers' leftovers, the day crew's unfinished jobs → Job_* on the
                                         work counter, Leftover_*
  the melds' copier at 4 a.m.: the lid, the glass "scratched" (a white line
   down the copies), the scan light "a dirty pink" under the lid, the tray,
   the pages "warm"                    → Copier_Hero_*; its pink bar shows
                                         only in the copier view
  The text gives no windows: the shopfront's glass is blinded at night.
THE OFFICE (x 34..52) — vol 4's "paper cuts": "the office", "after hours";
  his desk and its drawer, the rolodex, the notepad, "a copying machine"
  that enlarges to 400%, the cleaning crews in white (their cart), floors
  "above and below", and "How bright it is in the center, at the nexus"
  — the corner where two walls meet, lit.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the back room as its own view (he reads there on breaks);
the copier's warm pages as a stack in the tray (now one sheet); the office's
floors above and below as sound only — but a stairwell door; what the copy
shop sells off its old shelves; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_taper_cyl,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_chair
from _props.safety import make_fluorescent_tube_fixture
from _props.detail import make_wall_outlet

X0, X1, D, H, T = -6.0, 6.0, 9.0, 3.0, 0.20
WALL = (0.70, 0.72, 0.62, 1.0); BASE = (0.36, 0.36, 0.34, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
GRIME = (0.20, 0.26, 0.20, 1.0)
VINYL = (0.56, 0.54, 0.48, 1.0); VINYL_SEAM = (0.46, 0.44, 0.40, 1.0)
COPIER = (0.82, 0.80, 0.74, 1.0); COPIER_DARK = (0.30, 0.30, 0.32, 1.0)
PAPER = (0.95, 0.95, 0.92, 1.0)
CARDBOARD = (0.62, 0.48, 0.32, 1.0)


def copier(prefix, x, y, face="+Y", hero=False):
    """A floor copier: cabinet, the body with its glass and lid, the panel,
    the output tray on its side. face = the side the operator stands on."""
    yaw = {"+Y": 0.0, "-Y": math.pi, "+X": -math.pi / 2.0, "-X": math.pi / 2.0}[face]
    c, s = math.cos(yaw), math.sin(yaw)

    def at(u, v):       # u across the machine, v toward the operator
        return (x + u * c - v * s, y + u * s + v * c)
    make_rot_box(f"{prefix}_Cabinet", (*at(0.0, 0.0), 0.40), (1.10, 0.70, 0.80), COPIER, yaw=yaw)
    make_rot_box(f"{prefix}_Body", (*at(0.0, 0.0), 0.98), (1.10, 0.70, 0.36), COPIER, yaw=yaw)
    make_rot_box(f"{prefix}_Glass", (*at(-0.08, -0.02), 1.165), (0.70, 0.50, 0.01), (0.30, 0.40, 0.44, 1.0), yaw=yaw)
    make_rot_box(f"{prefix}_Panel", (*at(0.38, 0.30), 1.18), (0.26, 0.10, 0.04), COPIER_DARK, yaw=yaw)
    make_rot_box(f"{prefix}_Tray", (*at(0.66, 0.0), 0.92), (0.24, 0.40, 0.02), COPIER_DARK, yaw=yaw)
    make_rot_box(f"{prefix}_Tray_Arm", (*at(0.56, 0.0), 0.89), (0.04, 0.36, 0.06), COPIER_DARK, yaw=yaw)
    for k in range(3):
        make_rot_box(f"{prefix}_Drawer_{k}", (*at(0.0, 0.352), 0.16 + k * 0.24), (0.96, 0.004, 0.18), (0.74, 0.72, 0.66, 1.0), yaw=yaw)
    if hero:
        # the lid half open, the scratch on the glass, the pink scan bar
        # bleeding from under it (copier view only), the warm page in the tray
        make_rot_box(f"{prefix}_Lid", (*at(-0.08, -0.30), 1.40), (0.74, 0.04, 0.48), (0.86, 0.84, 0.78, 1.0), yaw=yaw)
        make_rot_box(f"{prefix}_Hinge", (*at(-0.08, -0.29), 1.18), (0.70, 0.04, 0.03), COPIER_DARK, yaw=yaw)
        make_rot_box(f"{prefix}_Scratch", (*at(0.05, -0.02), 1.171), (0.004, 0.46, 0.002), (0.92, 0.94, 0.94, 1.0), yaw=yaw)
        make_rot_box(f"{prefix}_Scan_Bar__copy_shop_copier", (*at(-0.30, -0.02), 1.172), (0.03, 0.48, 0.004), (0.98, 0.50, 0.66, 1.0),
                     yaw=yaw)
        make_rot_box(f"{prefix}_Page_Warm", (*at(0.66, 0.0), 0.935), (0.22, 0.30, 0.004), PAPER, yaw=yaw)
    else:
        make_rot_box(f"{prefix}_Lid", (*at(-0.08, -0.02), 1.19), (0.74, 0.54, 0.04), (0.86, 0.84, 0.78, 1.0), yaw=yaw)


def build_shop():
    cx, cy = (X0 + X1) / 2.0, D / 2.0
    make_floor("Shop_Floor", (cx, cy, 0.0), size_x=X1 - X0 + 0.4, size_y=D + 0.4, palette={"vinyl": VINYL, "seam": VINYL_SEAM})
    make_box("Shop_Ceil", (cx, cy, H + 0.04), (X1 - X0 + 0.4, D + 0.4, 0.08), (0.80, 0.80, 0.76, 1.0))
    make_wall("Shop_Wall_W", (X0, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Shop_Wall_E", (X1, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Shop_Wall_N", (cx, D, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(3.6, 1.0, 1.0, 2.0)])
    # the old store's front: glass to the street, its blinds down at night, the door
    make_wall_with_openings("Shop_Wall_S", (cx, 0.0, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-3.0, 1.45, 4.6, 2.3), (2.2, 1.05, 1.0, 2.1)])
    make_box("Shop_Front_Glass", (-3.0, 0.0, 1.45), (4.6, 0.02, 2.3), (0.06, 0.07, 0.09, 1.0))
    for k in range(24):
        make_box(f"Shop_Front_Blind_{k}", (-3.0, 0.13, 2.55 - k * 0.092), (4.6, 0.006, 0.07), (0.66, 0.64, 0.56, 1.0))
    make_box("Shop_Front_Blind_Head", (-3.0, 0.115, 2.62), (4.7, 0.03, 0.06), (0.60, 0.58, 0.52, 1.0))
    for s in (-1, 1):
        make_box(f"Shop_Front_Blind_Cord_{s:+d}", (-3.0 + s * 1.6, 0.13, 1.50), (0.006, 0.006, 2.24), (0.66, 0.64, 0.56, 1.0))
    make_box("Shop_Door", (2.2, 0.0, 1.05), (0.98, 0.05, 2.08), (0.30, 0.30, 0.32, 1.0))
    make_box("Shop_Door_Glass", (2.2, 0.0, 1.35), (0.60, 0.06, 1.10), (0.06, 0.07, 0.09, 1.0))
    # the walls greenish black in places
    for k, (wall, a, z, w, h) in enumerate((("W", 2.0, 0.6, 1.4, 0.9), ("W", 6.5, 1.8, 1.0, 1.2), ("E", 4.0, 0.4, 2.0, 0.6),
                                             ("N", -4.0, 2.2, 1.6, 0.6), ("E", 7.6, 1.6, 0.8, 1.4))):
        if wall == "W":
            make_box(f"Grime_{k}", (X0 + 0.104, a, z), (0.004, w, h), GRIME)
        elif wall == "E":
            make_box(f"Grime_{k}", (X1 - 0.104, a, z), (0.004, w, h), GRIME)
        else:
            make_box(f"Grime_{k}", (a, D - 0.104, z), (w, 0.004, h), GRIME)
    # the tubes: two rows of three; every third gasping (its tube dull)
    for r, y in enumerate((3.0, 6.2)):
        for k, x in enumerate((-3.6, 0.0, 3.6)):
            dying = (r * 3 + k) % 3 == 2
            make_fluorescent_tube_fixture(f"Fluor_Shop_{r}_{k}", (x, y, H), length=1.20, width=0.30,
                                          palette={"tube": (0.42, 0.44, 0.40, 1.0)} if dying else None)
    # the counter across the front for the customers, the work counter down the W wall
    make_box("Front_Counter", (0.0, 1.9, 0.52), (3.2, 0.60, 1.04), (0.50, 0.46, 0.40, 1.0))
    make_box("Front_Counter_Top", (0.0, 1.9, 1.055), (3.3, 0.66, 0.03), (0.74, 0.72, 0.66, 1.0))
    make_box("Register", (-0.8, 1.95, 1.15), (0.36, 0.34, 0.16), (0.24, 0.24, 0.26, 1.0))
    for k in range(3):
        make_box(f"Leftover_Original_{k}", (0.4 + k * 0.34, 1.9, 1.072 + k * 0.004), (0.22, 0.28, 0.004),
                 ((0.86, 0.80, 0.70, 1.0), PAPER, (0.70, 0.62, 0.50, 1.0))[k])
    make_box("Leftover_Photo", (1.30, 1.75, 1.074), (0.10, 0.15, 0.004), (0.50, 0.44, 0.40, 1.0))
    wx = X0 + 0.10 + 0.40
    make_box("Work_Counter", (wx, 4.6, 0.46), (0.80, 4.0, 0.92), (0.50, 0.46, 0.40, 1.0))
    make_box("Work_Counter_Top", (wx, 4.6, 0.935), (0.84, 4.1, 0.03), (0.74, 0.72, 0.66, 1.0))
    for k in range(5):
        h = 0.06 + (k % 3) * 0.05
        make_box(f"Job_Stack_{k}", (wx + 0.06, 3.0 + k * 0.72, 0.95 + h / 2.0), (0.24, 0.32, h), PAPER)
        make_box(f"Job_Ticket_{k}", (wx + 0.06, 3.0 + k * 0.72, 0.952 + h), (0.10, 0.14, 0.003), (0.96, 0.84, 0.50, 1.0))
    make_box("Paper_Cutter", (wx - 0.05, 6.2, 0.97), (0.46, 0.40, 0.04), (0.40, 0.40, 0.40, 1.0))
    make_rot_box("Paper_Cutter_Arm", (wx - 0.05, 6.2, 1.005), (0.46, 0.03, 0.03), (0.60, 0.60, 0.62, 1.0), roll=0.0, yaw=0.3)
    make_box("Stapler", (wx + 0.20, 5.5, 0.975), (0.06, 0.20, 0.05), (0.20, 0.20, 0.22, 1.0))
    # paper reams on a steel shelf (what was the store's), the copiers
    for sh in range(4):
        make_box(f"Ream_Shelf_{sh}", (X1 - 0.10 - 0.25, 5.0, 0.30 + sh * 0.50), (0.46, 2.40, 0.03), (0.56, 0.58, 0.60, 1.0))
        for k in range(8):
            make_box(f"Ream_Stock_{sh}_{k}", (X1 - 0.10 - 0.25, 4.0 + k * 0.29, 0.30 + sh * 0.50 + 0.07), (0.28, 0.22, 0.11),
                     ((0.96, 0.96, 0.94, 1.0), (0.90, 0.86, 0.96, 1.0), (0.96, 0.90, 0.70, 1.0))[(sh + k) % 3])
    for s in (-1, 1):
        make_box(f"Ream_Shelf_Post_{s:+d}", (X1 - 0.10 - 0.25, 5.0 + s * 1.18, 1.0), (0.04, 0.04, 2.0), (0.56, 0.58, 0.60, 1.0))
    copier("Copier_Hero", 0.0, 5.2, face="-Y", hero=True)
    copier("Copier_B", -2.6, 7.6, face="-Y")
    copier("Copier_C", 2.4, 7.6, face="-Y")
    # the wastebasket by the work counter, the stapled copy in it
    bx, by = X0 + 1.15, 2.6
    make_taper_cyl("Wastebasket", (bx, by, 0.20), 0.15, 0.19, 0.40, (0.30, 0.32, 0.30, 1.0), segments=14)
    # the stapled copy standing up out of it, its staple at the top corner
    make_rot_box("Stapled_Copy", (bx + 0.02, by, 0.45), (0.20, 0.01, 0.27), PAPER, yaw=0.3, roll=0.25)
    make_box("Stapled_Copy_Staple", (bx - 0.05, by - 0.02, 0.575), (0.02, 0.004, 0.004), (0.70, 0.70, 0.72, 1.0))
    for k in range(3):
        make_rot_box(f"Wastebasket_Paper_{k}", (bx + 0.03 * k - 0.03, by - 0.04, 0.30 + k * 0.015), (0.12, 0.10, 0.06), PAPER, yaw=k)
    make_chair("Shop_Stool", wx + 0.70, 4.0, yaw=-math.pi / 2.0, wood=(0.30, 0.30, 0.32, 1.0), seat_h=0.62, w=0.36)
    make_wall_outlet("Outlet_Copiers", (0.0, D), axis='X', face_sign=-1)
    # the back room through the N doorway: boxes of the store's unsold
    # merchandise, a clear spot by them, a lamp-less bulb
    make_box("Back_Floor", (3.6, D + 2.0, 0.0), (4.6, 4.0, 0.02), (0.46, 0.44, 0.40, 1.0))
    make_box("Back_Ceil", (3.6, D + 2.0, H + 0.04), (4.6, 4.0, 0.08), (0.62, 0.62, 0.58, 1.0))
    for nm, (x, y, sx, sy) in {"W": (1.2, D + 2.0, 0.2, 4.0), "E": (6.0, D + 2.0, 0.2, 4.0), "N": (3.6, D + 4.1, 5.0, 0.2)}.items():
        make_box(f"Back_Wall_{nm}", (x, y, H / 2.0), (sx, sy, H), WALL)
    for k in range(14):
        col, row = k % 5, k // 5
        h = 0.40
        make_box(f"Back_Box_{k}", (1.8 + col * 0.82, D + 3.6 - (row % 2) * 0.1, h / 2.0 + row * h), (0.70, 0.60, h - 0.01),
                 (CARDBOARD[0] - (k % 3) * 0.04, CARDBOARD[1] - (k % 3) * 0.03, CARDBOARD[2], 1.0))
    make_box("Back_Box_Seat", (4.6, D + 1.2, 0.20), (0.60, 0.50, 0.40), CARDBOARD)
    make_box("Back_Paperback", (4.6, D + 1.2, 0.41), (0.12, 0.18, 0.02), (0.60, 0.22, 0.18, 1.0))
    make_cyl("Back_Bulb", (3.6, D + 2.0, H - 0.05), 0.04, 0.10, (0.96, 0.92, 0.80, 1.0), segments=10)


# ── THE OFFICE ────────────────────────────────────────────────────────
OX0, OX1, OD, OH = 34.0, 52.0, 14.0, 2.8


def build_office():
    cx, cy = (OX0 + OX1) / 2.0, OD / 2.0
    make_floor("Off_Floor", (cx, cy, 0.0), size_x=OX1 - OX0 + 0.4, size_y=OD + 0.4,
               palette={"vinyl": (0.42, 0.44, 0.48, 1.0), "seam": (0.38, 0.40, 0.44, 1.0)})
    make_box("Off_Ceil", (cx, cy, OH + 0.04), (OX1 - OX0 + 0.4, OD + 0.4, 0.08), (0.88, 0.88, 0.86, 1.0))
    opal = {"wall": (0.84, 0.84, 0.80, 1.0), "baseboard": (0.40, 0.40, 0.42, 1.0)}
    make_wall_with_openings("Off_Wall_W", (OX0, cy, 0), length=OD + 0.4, height=OH, thickness=T, axis='Y', palette=opal,
                            baseboard_face_sign=+1, openings=[(3.5, 1.5, 3.0, 1.6), (9.5, 1.5, 3.0, 1.6)])
    for k, y in enumerate((3.5, 9.5)):
        make_box(f"Off_Window_{k}", (OX0, y, 1.5), (0.02, 3.0, 1.6), (0.06, 0.07, 0.10, 1.0))
    make_wall("Off_Wall_E", (OX1, cy, 0), length=OD + 0.4, height=OH, thickness=T, axis='Y', palette=opal, baseboard_face_sign=-1)
    make_wall("Off_Wall_N", (cx, OD, 0), length=OX1 - OX0 + 0.4, height=OH, thickness=T, axis='X', palette=opal, baseboard_face_sign=-1)
    make_wall_with_openings("Off_Wall_S", (cx, 0.0, 0), length=OX1 - OX0 + 0.4, height=OH, thickness=T, axis='X', palette=opal,
                            baseboard_face_sign=+1, openings=[(49.5, 1.0, 0.96, 2.0)])
    make_box("Off_Stair_Door", (49.5, 0.0, 1.0), (0.94, 0.05, 2.0), (0.50, 0.52, 0.56, 1.0))
    for i in range(3):
        for j in range(3):
            make_box(f"Off_Ceil_Panel_{i}_{j}", (37.0 + i * 6.0, 2.5 + j * 4.5, OH - 0.01), (1.2, 0.6, 0.02), (0.98, 0.98, 0.94, 1.0))
    # desks in two rows against the S and N walls, his at the W end of the N
    # row (his chair looks along the row to the bright corner); the drawer,
    # the rolodex, the lunch notepad, the expense report
    for r, (y, back) in enumerate(((0.10 + 0.38, -1), (OD - 0.10 - 0.38, 1))):
        for k in range(4):
            x = 37.0 + k * 3.4
            make_box(f"Off_Desk_{r}_{k}_Top", (x, y, 0.735), (1.50, 0.76, 0.03), (0.62, 0.56, 0.48, 1.0))
            make_box(f"Off_Desk_{r}_{k}_Pedestal", (x + 0.52, y, 0.36), (0.42, 0.70, 0.72), (0.50, 0.50, 0.52, 1.0))
            make_box(f"Off_Desk_{r}_{k}_Leg", (x - 0.70, y, 0.36), (0.04, 0.70, 0.72), (0.50, 0.50, 0.52, 1.0))
            make_box(f"Off_Desk_{r}_{k}_Monitor", (x - 0.10, y + back * 0.20, 0.96), (0.40, 0.36, 0.40), (0.80, 0.78, 0.72, 1.0))
            make_chair(f"Off_Desk_{r}_{k}_Chair", x, y - back * 0.70, yaw=(0.0 if back > 0 else math.pi), wood=(0.24, 0.24, 0.26, 1.0),
                       seat_col=(0.24, 0.26, 0.36, 1.0))
    hx, hy = 37.0, OD - 0.10 - 0.38
    make_box("His_Drawer", (hx + 0.52, hy - 0.352, 0.58), (0.38, 0.012, 0.16), (0.56, 0.56, 0.58, 1.0))
    make_cyl("Rolodex", (hx + 0.45, hy + 0.05, 0.81), 0.08, 0.14, (0.20, 0.20, 0.22, 1.0), axis='X', segments=12)
    make_box("Rolodex_Base", (hx + 0.45, hy + 0.05, 0.76), (0.18, 0.14, 0.02), (0.20, 0.20, 0.22, 1.0))
    make_box("Lunch_Notepad", (hx - 0.40, hy - 0.15, 0.754), (0.14, 0.20, 0.008), (0.96, 0.92, 0.62, 1.0))
    make_box("Expense_Report", (hx - 0.10, hy - 0.20, 0.752), (0.22, 0.28, 0.004), PAPER)
    make_box("Form_Letter_Stack", (hx + 0.15, hy - 0.10, 0.76), (0.22, 0.28, 0.02), PAPER)
    # the copying machine against the E wall, its enlargements in the tray
    copier("Off_Copier", OX1 - 0.10 - 0.35, 9.0, face="-X")
    make_box("Off_Copier_Enlargements", (OX1 - 0.10 - 0.35, 9.0 - 0.66, 0.945), (0.30, 0.22, 0.03), PAPER)
    # the cleaning crew's cart and a vacuum, far off
    make_box("Cleaning_Cart", (49.0, 6.2, 0.45), (0.60, 1.10, 0.90), (0.84, 0.84, 0.86, 1.0))
    make_cyl("Cleaning_Bin", (49.0, 5.8, 1.05), 0.18, 0.30, (0.30, 0.30, 0.34, 1.0), segments=12)
    make_box("Vacuum", (48.0, 7.2, 0.40), (0.30, 0.34, 0.80), (0.86, 0.84, 0.80, 1.0))
    # the bright corner where the walls meet (NE) is a light, not a prop


def main():
    clear_scene()
    build_shop()
    build_office()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/copy_shop.glb"))
    print(f"\n[build_copy_shop] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
