"""The school newspaper room — vol2 ch2 interlude three (Small Wood High).

DRAFT 2 (2026-10-10) — rebuilt at a classroom's real size. Draft 1 was an
8 x 6 m box with four desks, a pinboard, a chalkboard and a three-pane
window. The prose:

  "I joined the school newspaper on a whim ... an understaffed,
  underfunded academic endeavor ... Katrina was a photographer for the
  paper. Shannon a features writer. And it was Jay Rose who pencilled the
  one and only comic strip — DriftWood — about a teenager named Wood and
  his yearnings to leave the small town forever. Most of my friendships
  in Small Wood were forged out of that classroom and the late nights."
  · "the football season began ... a glorious disaster" · "the pressure
  of a deadline".

A borrowed classroom the paper has colonised, 9.6 x 8.4 m under a 3.0 m
drop ceiling:
  · THE LAYOUT ISLAND: four desks butted together, the paste-up pages and
    the proofs, the waxer, the X-acto and the steel rule, the rubber
    cement, the old typewriter at its corner, Katrina's camera, Shannon's
    notebook; six chairs pulled up.
  · THE W WALL: the counter of beige computers, the laser printer and the
    scanner, their chairs — and over them the cork board of page dummies
    with Jay Rose's DRIFTWOOD strip pinned across its top.
  · THE N WALL: the chalkboard still carrying last period's math, the
    clock, the PA speaker, the flag; the advisor's desk in the NE corner;
    the DARKROOM door beside it with its red light.
  · THE E WALL: three windows over the radiators, blinds half down, the
    light table with Katrina's negatives under them — and outside, the
    lot, and the football field with its light towers and bleachers.
  · THE S WALL: the bound volumes, the file cabinets, the paper cutter on
    its cart, this week's bundles by the door; the door open on the hall
    and its lockers.
  · A row of the classroom's own desks along the S, the day it still is.

Coordinate frame: Blender Z-up. y=0 is the door (S) wall; +Y runs back to
the chalkboard; walls x=+-4.8, back wall y=8.4, the hall to y=-2.8.
glTF export remaps to Godot (x, z, -y).

Draft 3 targets: the late-night version (the troffers off, the advisor's
lamp, the computer screens as the light); the darkroom beyond its door;
the masthead of the paper's name once the prose gives one.
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_rot_box, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling, make_window
from _props.furniture import make_chair
from _props.safety import make_fluorescent_tube_fixture
from _props.decor import make_wall_clock

X0, X1 = -4.8, 4.8
Y0, Y1 = 0.0, 8.4
CEIL = 3.0
HALL_Y0 = -2.8
DOOR_X = 3.4

COL_WALL = (0.80, 0.78, 0.68, 1.0)       # institutional cream
COL_WALL_LOW = (0.46, 0.52, 0.48, 1.0)   # the painted wainscot
COL_BASE = (0.24, 0.24, 0.22, 1.0)
COL_FLOOR = (0.70, 0.66, 0.56, 1.0)      # waxed VCT
COL_SEAM = (0.58, 0.54, 0.46, 1.0)
COL_DESK = (0.66, 0.54, 0.38, 1.0)       # laminate
COL_STEEL = (0.40, 0.42, 0.44, 1.0)
COL_PAPER = (0.92, 0.90, 0.82, 1.0)
COL_PAPER_DK = (0.80, 0.78, 0.68, 1.0)
COL_BEIGE = (0.80, 0.76, 0.64, 1.0)      # the computers
COL_DARK = (0.18, 0.18, 0.20, 1.0)
COL_CORK = (0.62, 0.46, 0.30, 1.0)
COL_FRAME = (0.36, 0.30, 0.22, 1.0)
COL_CHALK = (0.16, 0.24, 0.20, 1.0)
COL_GRASS = (0.30, 0.46, 0.24, 1.0)
COL_ASPHALT = (0.30, 0.30, 0.31, 1.0)


def build_shell():
    make_floor("Floor", (0.0, (Y0 + Y1) / 2.0, 0.0), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (X0, (HALL_Y0 + Y1) / 2.0, 0), length=Y1 - HALL_Y0 + 0.4, height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    # E wall: three windows over the radiators, looking at the lot and the field
    make_wall_with_openings("Wall_E", (X1, (HALL_Y0 + Y1) / 2.0, 0), length=Y1 - HALL_Y0 + 0.4, height=CEIL, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(2.0, 1.80, 1.90, 1.60), (4.2, 1.80, 1.90, 1.60), (6.4, 1.80, 1.90, 1.60)])
    make_wall_with_openings("Wall_N", (0.0, Y1, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(3.95, 1.05, 0.85, 2.10)])
    make_wall_with_openings("Wall_S", (0.0, Y0, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(DOOR_X, 1.05, 0.95, 2.10)])
    make_ceiling("Ceil", (0.0, (Y0 + Y1) / 2.0, CEIL), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
                 with_grid=True, with_stains=True, palette={"tile": (0.86, 0.86, 0.82, 1.0)})
    # the painted wainscot band on the room faces (the classroom's lower wall)
    make_box("Wall_W_Wainscot", (X0 + 0.101, (Y0 + Y1) / 2.0, 0.60), (0.004, Y1 - Y0 - 0.20, 0.80), COL_WALL_LOW)
    make_box("Wall_N_Wainscot_W", ((X0 + 3.95 - 0.425) / 2.0, Y1 - 0.101, 0.60), (3.95 - 0.425 - X0 - 0.10, 0.004, 0.80), COL_WALL_LOW)
    make_box("Wall_S_Wainscot_W", ((X0 + DOOR_X - 0.475) / 2.0, Y0 + 0.101, 0.60), (DOOR_X - 0.475 - X0 - 0.10, 0.004, 0.80), COL_WALL_LOW)
    # the windows, their radiators, their half-lowered blinds
    for k, cy in enumerate((2.0, 4.2, 6.4)):
        make_window(f"Win_E_{k}", (X1 - 0.10, cy, 1.80), width=1.90, height=1.60, axis='Y', room_dir=-1, see_through=True,
                    palette={"frame": (0.70, 0.70, 0.66, 1.0)}, cross_mullion=True)
        make_box(f"Win_E_{k}_Glass", (X1 - 0.02, cy, 1.80), (0.01, 1.90, 1.60), (0.78, 0.84, 0.86, 0.25))
        make_box(f"Win_E_{k}_Sill", (X1 - 0.18, cy, 0.985), (0.16, 2.0, 0.03), (0.70, 0.70, 0.66, 1.0))
        make_box(f"Win_E_{k}_Blind", (X1 - 0.20, cy, 2.36), (0.03, 1.86, 0.48), (0.88, 0.86, 0.78, 1.0))
        make_box(f"Win_E_{k}_Blind_Head", (X1 - 0.20, cy, 2.62), (0.06, 1.90, 0.04), (0.70, 0.70, 0.66, 1.0))
        make_box(f"Win_E_{k}_Blind_Head_Bracket", (X1 - 0.15, cy, 2.62), (0.10, 0.06, 0.04), (0.70, 0.70, 0.66, 1.0))
        make_box(f"Radiator_{k}", (X1 - 0.18, cy, 0.425), (0.16, 1.60, 0.73), (0.74, 0.72, 0.66, 1.0))   # on the floor, against the wall
        for f in range(14):
            make_box(f"Radiator_{k}_Fin_{f}", (X1 - 0.27, cy - 0.74 + f * 0.114, 0.48), (0.02, 0.05, 0.58), (0.68, 0.66, 0.60, 1.0))
    # the door, open into the room against its jamb
    make_box("Door", (DOOR_X + 0.475 + 0.02, Y0 + 0.55, 1.03), (0.04, 0.90, 2.06), (0.58, 0.44, 0.30, 1.0))
    make_box("Door_Window", (DOOR_X + 0.475 + 0.042, Y0 + 0.55, 1.55), (0.004, 0.20, 0.60), (0.62, 0.70, 0.74, 1.0))
    make_cyl("Door_Knob", (DOOR_X + 0.475 + 0.06, Y0 + 0.92, 0.98), 0.025, 0.05, (0.80, 0.78, 0.70, 1.0), segments=8, axis='X')
    make_box("Door_Stop", (DOOR_X + 0.62, Y0 + 1.00, 0.03), (0.06, 0.06, 0.06), COL_DARK)
    # the troffers
    for i, fx in enumerate((-2.6, 0.2, 3.0)):
        for j, fy in enumerate((2.4, 6.0)):
            make_fluorescent_tube_fixture(f"Fluor_{i}_{j}", (fx, fy, CEIL), length=1.20, width=0.60)


def build_hall():
    """The hall past the door: the lockers, the terrazzo, one troffer."""
    make_box("Hall_Floor", (0.0, (HALL_Y0 + Y0) / 2.0, -0.05), (X1 - X0 + 0.2, Y0 - HALL_Y0 + 0.2, 0.10), (0.64, 0.62, 0.58, 1.0))
    make_box("Hall_Ceil", (0.0, (HALL_Y0 + Y0) / 2.0, CEIL + 0.05), (X1 - X0, Y0 - HALL_Y0, 0.10), (0.86, 0.86, 0.82, 1.0))
    make_wall("Hall_Wall_S", (0.0, HALL_Y0, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X',
              palette={"wall": COL_WALL, "baseboard": COL_BASE}, baseboard_face_sign=+1)
    make_fluorescent_tube_fixture("Hall_Fluor", (DOOR_X, -1.4, CEIL), length=1.20, width=0.30)
    # the lockers along the hall's S wall, facing N
    for k in range(16):
        lx = -0.20 + k * 0.34
        if lx > X1 - 0.30:
            break
        col = (0.26, 0.36, 0.56, 1.0) if k % 5 else (0.30, 0.40, 0.60, 1.0)
        make_box(f"Locker_{k}", (lx, HALL_Y0 + 0.10 + 0.24, 0.95), (0.32, 0.48, 1.80), col)
        make_box(f"Locker_{k}_Vent", (lx, HALL_Y0 + 0.10 + 0.481, 1.62), (0.20, 0.004, 0.10), (0.18, 0.24, 0.40, 1.0))
        make_box(f"Locker_{k}_Handle", (lx + 0.11, HALL_Y0 + 0.10 + 0.49, 1.00), (0.03, 0.02, 0.10), (0.70, 0.70, 0.70, 1.0))
    make_box("Locker_Base", (2.4, HALL_Y0 + 0.34, 0.025), (5.6, 0.48, 0.05), COL_DARK)
    make_box("Hall_Poster_Football", (0.5, Y0 - 0.105, 1.55), (0.60, 0.01, 0.80), (0.70, 0.18, 0.16, 1.0))
    make_box("Hall_Poster_Football_Band", (0.5, Y0 - 0.111, 1.70), (0.50, 0.002, 0.16), (0.96, 0.86, 0.30, 1.0))


def build_layout_island():
    """Four desks butted into the paper's layout table, and what is on it."""
    cx, cy = 0.20, 4.60
    for i, (dx, dy) in enumerate(((-0.60, -0.375), (0.60, -0.375), (-0.60, 0.375), (0.60, 0.375))):
        x, y = cx + dx, cy + dy
        make_box(f"Island_Desk_{i}_Top", (x, y, 0.725), (1.20, 0.75, 0.03), COL_DESK)
        for li, (lx, ly) in enumerate(((-0.56, -0.33), (0.56, -0.33), (-0.56, 0.33), (0.56, 0.33))):
            make_box(f"Island_Desk_{i}_Leg_{li}", (x + lx, y + ly, 0.355), (0.04, 0.04, 0.71), COL_STEEL)
    t = 0.74
    rnd = random.Random(22)
    # the paste-up: boards with columns waxed down, proofs fanned around them
    for k, (px, py) in enumerate(((-0.55, -0.35), (-0.10, -0.40), (0.40, -0.30), (0.75, 0.10), (-0.45, 0.25), (0.05, 0.35))):
        x, y = cx + px, cy + py
        make_rot_box(f"Page_{k}", (x, y, t + 0.002), (0.30, 0.42, 0.004), COL_PAPER, yaw=rnd.uniform(-0.12, 0.12))
        for c in range(3):
            make_rot_box(f"Page_{k}_Column_{c}", (x - 0.09 + c * 0.09, y + 0.02, t + 0.0045), (0.07, 0.30, 0.001), (0.62, 0.62, 0.60, 1.0))
        make_rot_box(f"Page_{k}_Head", (x, y + 0.17, t + 0.0045), (0.24, 0.04, 0.001), (0.20, 0.20, 0.22, 1.0))
    make_box("Waxer", (cx + 0.95, cy - 0.45, t + 0.04), (0.10, 0.22, 0.08), (0.84, 0.82, 0.76, 1.0))
    make_box("Steel_Rule", (cx - 0.20, cy - 0.05, t + 0.002), (0.60, 0.035, 0.004), (0.74, 0.76, 0.78, 1.0))
    make_box("Xacto_Knife", (cx + 0.12, cy - 0.10, t + 0.005), (0.15, 0.012, 0.01), (0.86, 0.66, 0.20, 1.0))
    make_cyl("Rubber_Cement", (cx + 0.95, cy + 0.20, t + 0.05), 0.035, 0.10, (0.66, 0.46, 0.20, 1.0), segments=8)
    make_cyl("Rubber_Cement_Cap", (cx + 0.95, cy + 0.20, t + 0.11), 0.03, 0.02, (0.20, 0.20, 0.22, 1.0), segments=8)
    # the typewriter at the island's corner
    tx, ty = cx - 0.95, cy + 0.50
    make_box("Typewriter_Body", (tx, ty, t + 0.07), (0.44, 0.36, 0.14), (0.40, 0.48, 0.52, 1.0))
    make_box("Typewriter_Keys", (tx, ty - 0.14, t + 0.03), (0.36, 0.10, 0.06), COL_DARK)
    make_cyl("Typewriter_Platen", (tx, ty + 0.12, t + 0.16), 0.03, 0.46, COL_DARK, segments=8, axis='X')
    make_box("Typewriter_Sheet", (tx, ty + 0.13, t + 0.27), (0.22, 0.01, 0.20), COL_PAPER)
    # Katrina's camera, Shannon's notebook, a coffee
    make_box("Camera_Body", (cx + 0.55, cy + 0.55, t + 0.05), (0.15, 0.09, 0.10), COL_DARK)
    make_cyl("Camera_Lens", (cx + 0.55, cy + 0.47, t + 0.045), 0.032, 0.07, (0.30, 0.30, 0.32, 1.0), segments=10, axis='Y')
    make_box("Camera_Strap", (cx + 0.80, cy + 0.55, t + 0.003), (0.30, 0.20, 0.006), (0.30, 0.22, 0.16, 1.0))
    make_box("Shannon_Notebook", (cx - 0.25, cy + 0.62, t + 0.006), (0.15, 0.21, 0.012), (0.80, 0.42, 0.52, 1.0))
    make_lathe("Island_Coffee", (cx - 0.65, cy - 0.20, t), [(0.0, 0.0), (0.04, 0.0), (0.045, 0.10), (0.0, 0.10)], (0.86, 0.84, 0.78, 1.0), segments=10)
    # six chairs pulled up
    for k, (sx, sy, yaw) in enumerate(((-0.60, -1.05, 0.0), (0.60, -1.05, 0.0), (-0.60, 1.05, math.pi), (0.60, 1.05, math.pi),
                                       (-1.50, 0.0, -math.pi / 2.0), (1.50, 0.0, math.pi / 2.0))):
        make_chair(f"Island_Chair_{k}", cx + sx, cy + sy, yaw=yaw, wood=(0.30, 0.36, 0.46, 1.0), w=0.42)


def build_west_wall():
    """The computer counter, and the cork board of dummies with DRIFTWOOD over it."""
    cy0, cy1 = 1.80, 6.80
    ccy = (cy0 + cy1) / 2.0
    face = X0 + 0.10
    make_box("Computer_Counter_Top", (face + 0.35, ccy, 0.745), (0.70, cy1 - cy0, 0.03), COL_DESK)
    for k, ly in enumerate((cy0 + 0.05, ccy, cy1 - 0.05)):
        make_box(f"Computer_Counter_Panel_{k}", (face + 0.35, ly, 0.365), (0.66, 0.04, 0.73), COL_STEEL)
    t = 0.76
    for k, my in enumerate((2.60, 4.30, 6.00)):
        make_box(f"Computer_{k}_Tower", (face + 0.32, my + 0.45, 0.20), (0.40, 0.18, 0.40), COL_BEIGE)   # on the floor under the counter
        make_box(f"Computer_{k}_Monitor", (face + 0.30, my, t + 0.22), (0.38, 0.40, 0.36), COL_BEIGE)
        make_box(f"Computer_{k}_Monitor_Screen", (face + 0.492, my, t + 0.24), (0.004, 0.30, 0.24), (0.30, 0.42, 0.52, 1.0))
        make_box(f"Computer_{k}_Keyboard", (face + 0.58, my, t + 0.015), (0.16, 0.44, 0.03), COL_BEIGE)
        make_box(f"Computer_{k}_Mouse", (face + 0.58, my - 0.32, t + 0.015), (0.10, 0.06, 0.03), COL_BEIGE)
        make_chair(f"Computer_{k}_Chair", face + 1.20, my, yaw=-math.pi / 2.0, wood=(0.30, 0.36, 0.46, 1.0), w=0.42)
    # the laser printer and the scanner at the counter's ends
    make_box("Laser_Printer", (face + 0.32, cy0 + 0.30, t + 0.14), (0.42, 0.44, 0.28), COL_BEIGE)
    make_box("Laser_Printer_Tray", (face + 0.58, cy0 + 0.30, t + 0.20), (0.12, 0.30, 0.01), COL_DARK)
    make_box("Scanner", (face + 0.32, cy1 - 0.32, t + 0.05), (0.36, 0.48, 0.10), COL_BEIGE)
    # the cork board of page dummies, and Jay Rose's comic strip across its top
    bz = 1.85
    make_box("Board_Frame", (face + 0.02, ccy, bz), (0.04, 4.40, 1.30), COL_FRAME)
    make_box("Board_Cork", (face + 0.045, ccy, bz), (0.01, 4.24, 1.14), COL_CORK)
    rnd = random.Random(5)
    for k in range(10):
        py = cy0 + 0.40 + (k % 5) * 0.84
        pz = bz + (0.20 if k < 5 else -0.32)
        make_box(f"Pinned_Dummy_{k}", (face + 0.054, py, pz), (0.008, 0.30, 0.40), COL_PAPER if k % 3 else COL_PAPER_DK)
        make_box(f"Pinned_Dummy_{k}_Head", (face + 0.0585, py, pz + 0.15), (0.001, 0.24, 0.04), COL_DARK)
        make_box(f"Pinned_Dummy_{k}_Photo", (face + 0.0585, py - 0.05, pz + 0.02), (0.001, 0.14, 0.12), (0.46, 0.46, 0.44, 1.0))
    # DRIFTWOOD: four panels pencilled by Jay Rose, a teenager named Wood
    make_box("DriftWood_Strip", (face + 0.054, ccy, bz + 0.475), (0.008, 1.40, 0.20), COL_PAPER)
    for p in range(4):
        make_box(f"DriftWood_Panel_{p}", (face + 0.0585, ccy - 0.51 + p * 0.34, bz + 0.475), (0.001, 0.30, 0.16), (0.98, 0.97, 0.92, 1.0))
        make_box(f"DriftWood_Panel_{p}_Figure", (face + 0.0595, ccy - 0.54 + p * 0.34, bz + 0.46), (0.001, 0.04, 0.10), (0.16, 0.16, 0.18, 1.0))
        make_box(f"DriftWood_Panel_{p}_Horizon", (face + 0.0595, ccy - 0.51 + p * 0.34, bz + 0.44), (0.001, 0.28, 0.006), (0.30, 0.30, 0.32, 1.0))
    make_box("DriftWood_Title", (face + 0.0585, ccy - 0.80, bz + 0.475), (0.001, 0.16, 0.12), (0.20, 0.30, 0.46, 1.0))


def build_north_wall():
    face = Y1 - 0.10
    make_box("Chalk_Frame", (-1.20, face - 0.03, 1.55), (4.60, 0.06, 1.30), COL_FRAME)
    make_box("Chalk_Board", (-1.20, face - 0.065, 1.55), (4.40, 0.01, 1.14), COL_CHALK)
    make_box("Chalk_Rail", (-1.20, face - 0.10, 0.88), (4.40, 0.14, 0.04), COL_FRAME)
    for k, (cx, cz, cw) in enumerate(((-2.6, 1.90, 1.10), (-2.4, 1.70, 0.80), (-2.5, 1.50, 0.95), (-0.6, 1.92, 1.30), (-0.3, 1.66, 0.70), (0.2, 1.40, 0.40))):
        make_box(f"Chalk_Line_{k}", (cx, face - 0.0705, cz), (cw, 0.002, 0.04), (0.82, 0.84, 0.80, 1.0))
    for k in range(3):
        make_box(f"Chalk_Stick_{k}", (-2.4 + k * 0.12, face - 0.10, 0.905), (0.07, 0.012, 0.012), (0.94, 0.94, 0.90, 1.0))
    make_box("Chalk_Eraser", (-1.6, face - 0.10, 0.92), (0.14, 0.05, 0.04), (0.30, 0.26, 0.22, 1.0))
    make_wall_clock("Clock", (1.70, face, 2.50), frozen_hour=4, frozen_min=40, facing='-Y')
    make_box("PA_Speaker", (-3.90, face - 0.03, 2.60), (0.36, 0.06, 0.36), (0.60, 0.58, 0.52, 1.0))
    make_box("PA_Speaker_Grille", (-3.90, face - 0.062, 2.60), (0.28, 0.004, 0.28), (0.40, 0.38, 0.34, 1.0))
    # the DARKROOM door, closed, its sign and the red light over it
    make_box("Darkroom_Door", (3.95, Y1, 1.04), (0.82, 0.05, 2.08), (0.20, 0.20, 0.22, 1.0))
    make_box("Darkroom_Door_Knob", (3.65, Y1 - 0.05, 1.00), (0.05, 0.05, 0.05), (0.80, 0.78, 0.70, 1.0))
    make_box("Darkroom_Sign", (3.95, Y1 - 0.03, 1.62), (0.40, 0.01, 0.12), (0.92, 0.90, 0.84, 1.0))
    make_cyl("Darkroom_Lamp_Dome", (3.95, face - 0.06, 2.28), 0.07, 0.12, (0.86, 0.12, 0.10, 1.0), segments=10, axis='Y')
    # the advisor's desk in the NE corner: the phone, the proofs, the lamp, the mug
    dx, dy = 2.30, Y1 - 0.10 - 0.38          # against the N wall
    make_box("Advisor_Desk_Top", (dx, dy, 0.745), (1.50, 0.76, 0.03), (0.42, 0.34, 0.26, 1.0))
    make_box("Advisor_Desk_Pedestal", (dx + 0.52, dy, 0.365), (0.42, 0.70, 0.73), (0.40, 0.42, 0.44, 1.0))
    for i, ly in enumerate((-0.33, 0.33)):
        make_box(f"Advisor_Desk_Leg_{i}", (dx - 0.71, dy + ly, 0.365), (0.04, 0.04, 0.73), (0.40, 0.42, 0.44, 1.0))
    t = 0.76
    make_box("Advisor_Phone", (dx - 0.50, dy + 0.18, t + 0.05), (0.22, 0.20, 0.10), COL_BEIGE)
    make_box("Advisor_Proofs", (dx, dy - 0.05, t + 0.02), (0.30, 0.40, 0.04), COL_PAPER)
    make_lathe("Advisor_Mug", (dx + 0.30, dy - 0.20, t), [(0.0, 0.0), (0.04, 0.0), (0.042, 0.10), (0.0, 0.10)], (0.62, 0.18, 0.16, 1.0), segments=10)
    make_cyl("Advisor_Lamp_Base", (dx + 0.55, dy + 0.22, t + 0.01), 0.07, 0.02, COL_DARK, segments=10)
    make_cyl("Advisor_Lamp_Post", (dx + 0.55, dy + 0.22, t + 0.21), 0.012, 0.40, COL_DARK, segments=6)
    make_lathe("Advisor_Lamp_Shade", (dx + 0.55, dy + 0.12, t + 0.36), [(0.0, 0.10), (0.03, 0.10), (0.09, 0.0), (0.0, 0.0)], (0.20, 0.36, 0.30, 1.0), segments=12)
    make_chair("Advisor_Chair", dx, dy - 0.70, yaw=0.0, wood=(0.30, 0.30, 0.32, 1.0), w=0.46)


def build_east_light_table():
    """Katrina's light table under the S window: the box, the negatives, the loupe."""
    lx, ly = 3.55, 2.00
    make_box("LightTable_Table_Top", (lx, ly, 0.745), (0.80, 1.20, 0.03), COL_DESK)
    for i, (ox, oy) in enumerate(((-0.36, -0.56), (0.36, -0.56), (-0.36, 0.56), (0.36, 0.56))):
        make_box(f"LightTable_Table_Leg_{i}", (lx + ox, ly + oy, 0.365), (0.04, 0.04, 0.73), COL_STEEL)
    make_rot_box("LightTable_Box", (lx, ly, 0.82), (0.50, 0.70, 0.12), (0.30, 0.30, 0.32, 1.0), pitch=0.0, roll=0.0)
    make_box("LightTable_Glow", (lx, ly, 0.882), (0.46, 0.64, 0.004), (0.98, 0.98, 0.94, 1.0))
    for k in range(4):
        make_box(f"LightTable_Negative_{k}", (lx - 0.12 + k * 0.08, ly, 0.886), (0.04, 0.50, 0.002), (0.42, 0.30, 0.18, 1.0))
    make_cyl("LightTable_Loupe", (lx + 0.12, ly - 0.18, 0.91), 0.02, 0.05, COL_DARK, segments=8)
    make_chair("LightTable_Chair", lx - 0.72, ly, yaw=-math.pi / 2.0, wood=(0.30, 0.36, 0.46, 1.0), w=0.42)


def build_south_wall():
    face = Y0 + 0.10
    # the bound volumes: a bookcase of back issues and the stylebooks
    bx0, bx1 = -4.40, -2.40
    bcx = (bx0 + bx1) / 2.0
    for e, ex in enumerate((bx0, bx1)):
        make_box(f"Bookcase_Side_{e}", (ex, face + 0.16, 0.95), (0.02, 0.32, 1.90), COL_FRAME)
    make_box("Bookcase_Back", (bcx, face + 0.01, 0.95), (bx1 - bx0, 0.02, 1.90), COL_FRAME)
    make_box("Bookcase_Top", (bcx, face + 0.16, 1.91), (bx1 - bx0 + 0.02, 0.32, 0.02), COL_FRAME)
    rnd = random.Random(31)
    for s in range(4):
        z = 0.06 + s * 0.46
        make_box(f"Bookcase_Shelf_{s}", (bcx, face + 0.16, z), (bx1 - bx0 - 0.02, 0.30, 0.02), COL_FRAME)
        x = bx0 + 0.04
        b = 0
        while x < bx1 - 0.10:
            w = rnd.uniform(0.04, 0.07) if s else 0.09
            h = rnd.uniform(0.26, 0.34)
            col = ((0.20, 0.24, 0.40, 1.0), (0.46, 0.16, 0.14, 1.0), (0.22, 0.36, 0.26, 1.0))[(b + s) % 3] if s else (0.16, 0.16, 0.18, 1.0)
            make_box(f"Bookcase_Volume_{s}_{b}", (x + w / 2.0, face + 0.16, z + 0.01 + h / 2.0), (w, 0.24, h), col)
            x += w + 0.006
            b += 1
    # the file cabinets, the paper cutter on its cart
    for k, fx in enumerate((-2.00, -1.52)):
        make_box(f"File_Cabinet_{k}", (fx, face + 0.33, 0.66), (0.46, 0.64, 1.32), (0.52, 0.54, 0.52, 1.0))
        for d in range(4):
            make_box(f"File_Cabinet_{k}_Drawer_{d}", (fx, face + 0.655, 0.20 + d * 0.31), (0.40, 0.01, 0.26), (0.48, 0.50, 0.48, 1.0))
    make_box("Cutter_Cart_Top", (-0.60, face + 0.40, 0.80), (0.70, 0.60, 0.03), COL_STEEL)
    for i, (ox, oy) in enumerate(((-0.32, -0.27), (0.32, -0.27), (-0.32, 0.27), (0.32, 0.27))):
        make_box(f"Cutter_Cart_Leg_{i}", (-0.60 + ox, face + 0.40 + oy, 0.40), (0.03, 0.03, 0.78), COL_STEEL)
    make_box("Paper_Cutter_Bed", (-0.60, face + 0.40, 0.835), (0.50, 0.45, 0.04), (0.72, 0.62, 0.42, 1.0))
    make_rot_box("Paper_Cutter_Blade", (-0.60, face + 0.18, 0.88), (0.50, 0.03, 0.04), (0.70, 0.72, 0.74, 1.0), pitch=0.0, roll=0.0)
    # this week's bundles by the door, tied with twine
    for k in range(5):
        bx = 1.50 + (k % 3) * 0.40
        bz = 0.10 + (k // 3) * 0.20
        make_box(f"Bundle_{k}", (bx, face + 0.30, bz), (0.36, 0.28, 0.20), COL_PAPER_DK)
        make_box(f"Bundle_{k}_Twine", (bx, face + 0.30, bz + 0.101), (0.01, 0.29, 0.004), (0.66, 0.54, 0.34, 1.0))


def build_student_desks():
    """The classroom's own desks, a row of them along the S, chairs pushed in."""
    for k, dx in enumerate((-3.40, -2.00, -0.60, 0.80)):
        dy = 2.30
        make_box(f"Student_Desk_{k}_Top", (dx, dy, 0.725), (0.62, 0.46, 0.025), COL_DESK)
        make_box(f"Student_Desk_{k}_Book_Box", (dx, dy, 0.64), (0.56, 0.40, 0.14), COL_STEEL)
        for li, (lx, ly) in enumerate(((-0.27, -0.19), (0.27, -0.19), (-0.27, 0.19), (0.27, 0.19))):
            make_box(f"Student_Desk_{k}_Leg_{li}", (dx + lx, dy + ly, 0.285), (0.03, 0.03, 0.57), COL_STEEL)
        make_chair(f"Student_Desk_{k}_Chair", dx, dy - 0.50, yaw=0.0, wood=(0.30, 0.36, 0.46, 1.0), w=0.40)


def build_outside():
    """Past the E windows: the lot, the field, its lights and its bleachers."""
    make_box("Out_Lawn", (40.0, 4.0, -0.04), (70.0, 90.0, 0.06), COL_GRASS)
    make_box("Out_Walk", (X1 + 1.2, 4.0, -0.005), (2.0, 30.0, 0.02), (0.64, 0.62, 0.58, 1.0))
    make_box("Out_Lot", (X1 + 9.0, 4.0, -0.004), (12.0, 30.0, 0.02), COL_ASPHALT)
    for k in range(9):
        make_box(f"Out_Lot_Stall_{k}", (X1 + 9.0, -9.0 + k * 3.0, 0.008), (5.0, 0.10, 0.004), (0.90, 0.90, 0.86, 1.0))
    # the field: the turf, the yard lines, the goalposts, the light towers, the home stands
    fx, fy = 42.0, 4.0
    make_box("Field_Turf", (fx, fy, 0.0), (48.0, 100.0, 0.02), (0.26, 0.48, 0.22, 1.0))
    for k in range(11):
        make_box(f"Field_Yard_Line_{k}", (fx, fy - 45.0 + k * 9.0, 0.012), (48.0, 0.12, 0.004), (0.94, 0.94, 0.90, 1.0))
    for e, gy in enumerate((fy - 52.0, fy + 52.0)):
        make_cyl(f"Field_Goal_{e}_Post", (fx, gy, 1.5), 0.08, 3.0, (0.94, 0.80, 0.20, 1.0), segments=8)
        make_box(f"Field_Goal_{e}_Bar", (fx, gy, 3.0), (5.6, 0.10, 0.10), (0.94, 0.80, 0.20, 1.0))
        for s in (-1, 1):
            make_cyl(f"Field_Goal_{e}_Upright_{s:+d}", (fx + s * 2.8, gy, 6.0), 0.06, 6.0, (0.94, 0.80, 0.20, 1.0), segments=8)
    for k, (lx, ly) in enumerate(((fx - 27.0, fy - 30.0), (fx - 27.0, fy + 30.0), (fx + 27.0, fy - 30.0), (fx + 27.0, fy + 30.0))):
        make_cyl(f"Field_Light_{k}_Pole", (lx, ly, 10.7), 0.30, 21.4, (0.56, 0.56, 0.58, 1.0), segments=8)
        make_box(f"Field_Light_{k}_Bank", (lx, ly, 22.4), (0.60, 3.6, 2.0), (0.40, 0.40, 0.42, 1.0))
    for r in range(8):
        make_box(f"Field_Stands_Step_{r}", (fx + 30.0 + r * 0.8, fy, 0.25 + r * 0.45), (0.8, 40.0, 0.50 + r * 0.9), (0.62, 0.62, 0.64, 1.0))
    make_box("Field_Press_Box", (fx + 36.4, fy, 7.0), (2.4, 8.0, 2.6), (0.70, 0.18, 0.16, 1.0))
    make_box("Field_Scoreboard", (fx, fy + 62.0, 5.0), (8.0, 0.4, 3.6), (0.12, 0.12, 0.14, 1.0))
    make_box("Field_Scoreboard_Post", (fx, fy + 62.0, 1.6), (0.4, 0.4, 3.2), (0.40, 0.40, 0.42, 1.0))
    make_box("Field_Fence", (fx - 25.0, fy, 0.6), (0.04, 100.0, 1.2), (0.56, 0.58, 0.60, 1.0))


def main():
    clear_scene()
    build_shell()
    build_hall()
    build_layout_island()
    build_west_wall()
    build_north_wall()
    build_east_light_table()
    build_south_wall()
    build_student_desks()
    build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/school_newspaper.glb"))
    print(f"\n[build_school_newspaper] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
