"""VOL 5 · Antonio's office above Ember & Ash — the Marigny, New Orleans.

"He thought about it now, climbing the rusted iron stair to the cramped
office above what would, eventually, be Ember & Ash." "The office was
twelve feet by ten. He could pace it in eight strides. ... The carpet
under the route showed the path." "the window air-conditioning unit
Jimmy had installed" "dropped the rolled architectural plans, picked up
the half-empty bottle of bourbon from the file cabinet" "He put the
phone face-down on the desk." "The warehouse below the office: exposed
brick scarred with generations of graffiti prayers and curses. Towering
ceilings lost in shadow. The floor littered with salvaged materials" —
"a section of reclaimed cypress beam ... not going up straight." "He
stood at the small leaded window of the office and looked out at the
neighborhood ... ancient oaks dripping Spanish moss ... Wrought iron
balconies rusting into lacework." "Across the street, an older man ...
was leaning against a streetlight, smoking. He wore a charcoal suit."
"the dark sedan he had parked carefully in the shadow of the dumpster."
(ch 7 the Chariot; ch 5 §III; ch 20's montage.)

DRAFT 4 · THE REBUILD AT CANON SCALE (2026-10-05). Drafts 1-3 built a
7 x 6 m period law office — four times the canon's twelve by ten, a
genre too grand (banker's furniture, a drafting table, a rotary phone
for a man whose phone says Q. PAUL on its screen), with the street
outside at the office's own floor level for a room the prose climbs a
stair to. Now:
  · the room is 12 x 10 ft (3.66 x 3.05 m) under a 2.75 m plaster
    ceiling: the front door (west) to the iron stair, the back door
    (east) to the back stair Jimmy comes up, the street (south) with
    Jimmy's AC in one sash and the small leaded window beside it, and an
    interior LOOKOUT (north) over the warehouse floor;
  · his desk under the lookout facing the street, his chair behind it;
    on the desk the smartphone face-down, the bourbon and the chipped
    glass, the rolled plans (paper ends), Jimmy's two coffees, the
    banker's lamp, a laptop; the visitor's chair; the file cabinet with
    the hard hat on it; the permits board and the sample boards; the
    worn runner in front of the windows; the ceiling fan; the box fan
    and the AC's drip pan;
  · a storey down: the street, the far sidewalk, the Creole cottages
    with their iron galleries, two live oaks with moss, the streetlight
    and the man in the charcoal suit beside it, the dark sedan by the
    dumpster;
  · a storey down to the north: the warehouse — brick walls with
    graffiti, roof trusses lost in shadow, the cypress beam hanging
    crooked on two chain hoists over two ladders, salvaged doors and
    planks, a clawfoot tub, the crew's radio on a sawhorse, a work light.
Draft 5 targets (the lunch litter went in 2026-10-05): the radio's practical; the
iron stair outside the front door; the man's cigarette ember.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path:
    sys.path.insert(0, _BT)
from _props import palette as P
from _props.objects import make_bottle
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube,
                             make_rot_box, make_blob, make_taper_cyl, export_glb)
from _props.structure import make_floor, make_ceiling, make_crown_molding, make_wall_with_openings
from _props.decor import make_wall_clock
from _props.detail import make_floor_stain, make_wall_outlet

PAL = {"wall": (0.62, 0.52, 0.40, 1.0), "baseboard": (0.26, 0.18, 0.12, 1.0)}
COL_FLOOR = (0.44, 0.31, 0.20, 1.0); COL_SEAM = (0.24, 0.17, 0.12, 1.0)
COL_OAK = (0.46, 0.32, 0.20, 1.0); COL_OAK_DARK = (0.24, 0.16, 0.11, 1.0); COL_BRASS = (0.86, 0.62, 0.28, 1.0)
COL_LEATHER = (0.30, 0.20, 0.14, 1.0); COL_BANKER_GREEN = (0.20, 0.46, 0.22, 1.0)
WOOD = (0.36, 0.26, 0.16, 1.0)
PAPER = (0.90, 0.88, 0.82, 1.0)
INK = (0.24, 0.24, 0.28, 1.0)
BRICK = (0.50, 0.32, 0.26, 1.0)
BRICK_DK = (0.40, 0.26, 0.21, 1.0)
IRON = (0.14, 0.14, 0.15, 1.0)

W, D, CEIL = 3.66, 3.05, 2.75          # twelve feet by ten, a 9 ft ceiling
X0, X1 = -W / 2.0, W / 2.0
Z_ST = -3.6                            # the street and the warehouse floor, a storey down
AC_X, LEAD_X, LOOK_X = -0.90, 0.85, -0.35
DOOR_W_Y, DOOR_E_Y = 0.75, 2.35


# ── the room ───────────────────────────────────────────────────────
def build_shell():
    make_floor("Floor", (0.0, D / 2.0, 0.0), size_x=W + 0.4, size_y=D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=W + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=+1,
                            openings=[(AC_X, 1.30, 0.78, 0.98), (LEAD_X, 1.45, 0.62, 0.76)])
    make_wall_with_openings("Wall_N", (0.0, D, 0), length=W + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(LOOK_X, 1.45, 1.40, 0.90)])
    make_wall_with_openings("Wall_W", (X0, D / 2.0, 0), length=D + 0.4, height=CEIL, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(DOOR_W_Y, 1.04, 0.86, 2.08)])
    make_wall_with_openings("Wall_E", (X1, D / 2.0, 0), length=D + 0.4, height=CEIL, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(DOOR_E_Y, 1.04, 0.80, 2.08)])
    make_ceiling("Ceil", (0.0, D / 2.0, CEIL), size_x=W + 0.4, size_y=D + 0.4, with_grid=False,
                 palette={"tile": (0.80, 0.76, 0.66, 1.0)})
    for nm, ax, length, wx, wy in (("Crown_W", 'Y', D, X0 + 0.10, D / 2.0), ("Crown_E", 'Y', D, X1 - 0.10, D / 2.0),
                                   ("Crown_N", 'X', W, 0.0, D - 0.10), ("Crown_S", 'X', W, 0.0, 0.10)):
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_OAK_DARK})


def build_openings():
    """The doors, Jimmy's AC in its sash, the small leaded window, the
    lookout over the warehouse."""
    # the front door (to the iron stair) and the back door (to the back stair), closed
    make_box("Front_Door", (X0, DOOR_W_Y, 1.04), (0.05, 0.84, 2.06), WOOD)
    make_cyl("Front_Door_Knob", (X0 + 0.045, DOOR_W_Y + 0.32, 1.00), 0.028, 0.04, COL_BRASS, axis='X', segments=8)
    make_box("Back_Door", (X1, DOOR_E_Y, 1.04), (0.05, 0.78, 2.06), WOOD)
    make_cyl("Back_Door_Knob", (X1 - 0.045, DOOR_E_Y - 0.30, 1.00), 0.028, 0.04, COL_BRASS, axis='X', segments=8)
    for nm, x, y, w in (("Front_Door_Casing", X0 + 0.11, DOOR_W_Y, 0.86), ("Back_Door_Casing", X1 - 0.11, DOOR_E_Y, 0.80)):
        for sgn in (-1, 1):
            make_box(f"{nm}_{'L' if sgn < 0 else 'R'}", (x, y + sgn * (w / 2.0 + 0.04), 1.06), (0.02, 0.08, 2.12), COL_OAK_DARK)
        make_box(f"{nm}_Head", (x, y, 2.15), (0.02, w + 0.16, 0.10), COL_OAK_DARK)
    # Jimmy's AC on the sash's sill, the sash pane above it
    sill = 1.30 - 0.49
    make_box("AC_Unit", (AC_X, 0.05, sill + 0.20), (0.66, 0.50, 0.40), (0.78, 0.76, 0.70, 1.0))
    make_box("AC_Unit_Grille", (AC_X, 0.305, sill + 0.20), (0.56, 0.01, 0.30), (0.60, 0.58, 0.54, 1.0))
    make_box("AC_Unit_Panel", (AC_X + 0.24, 0.306, sill + 0.30), (0.10, 0.01, 0.12), (0.30, 0.30, 0.32, 1.0))
    make_box("AC_Sash_Pane", (AC_X, 0.0, (sill + 0.40 + 1.79) / 2.0), (0.70, 0.008, 1.79 - sill - 0.40),
             (0.70, 0.78, 0.80, 0.25))
    for sgn in (-1, 1):
        make_box(f"AC_Sash_Accordion_{sgn:+d}", (AC_X + sgn * 0.36, 0.05, sill + 0.20), (0.05, 0.40, 0.36), (0.20, 0.20, 0.20, 1.0))
    make_box("AC_Drip_Pan", (AC_X, 0.36, 0.015), (0.40, 0.26, 0.03), (0.60, 0.60, 0.58, 1.0))
    make_box("AC_Drip_Water", (AC_X, 0.36, 0.032), (0.30, 0.18, 0.004), (0.46, 0.52, 0.56, 1.0))
    # the small leaded window: frame, pane, cames
    lz, lw, lh = 1.45, 0.62, 0.76
    for nm, fx, fz, sx, sz in (("T", LEAD_X, lz + lh / 2.0 - 0.03, lw, 0.06), ("B", LEAD_X, lz - lh / 2.0 + 0.03, lw, 0.06),
                               ("L", LEAD_X - lw / 2.0 + 0.03, lz, 0.06, lh - 0.12), ("R", LEAD_X + lw / 2.0 - 0.03, lz, 0.06, lh - 0.12)):
        make_box(f"Leaded_Window_Frame_{nm}", (fx, 0.0, fz), (sx, 0.20, sz), WOOD)
    make_box("Leaded_Window_Pane", (LEAD_X, 0.0, lz), (lw - 0.12, 0.008, lh - 0.12), (0.60, 0.66, 0.62, 0.22))
    for k in (-1, 0, 1):
        make_box(f"Leaded_Window_Came_V_{k:+d}", (LEAD_X + k * 0.125, 0.006, lz), (0.012, 0.006, lh - 0.12), (0.20, 0.20, 0.20, 1.0))
    for k in (-1, 0, 1):
        make_box(f"Leaded_Window_Came_H_{k:+d}", (LEAD_X, 0.006, lz + k * 0.16), (lw - 0.12, 0.006, 0.012), (0.20, 0.20, 0.20, 1.0))
    # the lookout over the warehouse (an interior window, glazed)
    oz, ow, oh = 1.45, 1.40, 0.90
    for nm, fx, fz, sx, sz in (("T", LOOK_X, oz + oh / 2.0 - 0.03, ow, 0.06), ("B", LOOK_X, oz - oh / 2.0 + 0.03, ow, 0.06),
                               ("L", LOOK_X - ow / 2.0 + 0.03, oz, 0.06, oh - 0.12), ("R", LOOK_X + ow / 2.0 - 0.03, oz, 0.06, oh - 0.12),
                               ("M", LOOK_X, oz, 0.04, oh - 0.12)):
        make_box(f"Lookout_Frame_{nm}", (fx, D, fz), (sx, 0.20, sz), WOOD)
    make_box("Lookout_Pane", (LOOK_X, D, oz), (ow - 0.12, 0.008, oh - 0.12), (0.72, 0.78, 0.78, 0.18))


def build_desk_and_chairs():
    """His desk under the lookout, facing the street; the sitter north
    of it. The visitor's chair south of it."""
    dx, dy = 0.05, 2.05
    make_box("Desk_Top", (dx, dy, 0.76), (1.40, 0.70, 0.05), COL_OAK)
    make_box("Desk_Front", (dx, dy - 0.33, 0.40), (1.40, 0.04, 0.70), COL_OAK_DARK)    # modesty panel, visitor's side
    for sgn in (-1, 1):
        make_box(f"Desk_Side_{sgn:+d}", (dx + sgn * 0.65, dy, 0.37), (0.10, 0.70, 0.74), COL_OAK_DARK)
        for di in range(3):
            make_box(f"Desk_Drawer_{sgn:+d}_{di}", (dx + sgn * 0.65, dy + 0.37, 0.60 - di * 0.21), (0.10, 0.04, 0.16), COL_OAK)
            make_cyl(f"Desk_Drawer_Knob_{sgn:+d}_{di}", (dx + sgn * 0.65, dy + 0.405, 0.60 - di * 0.21), 0.02, 0.03, COL_BRASS,
                     axis='Y', segments=8)
    top = 0.785
    # his chair, facing the street
    cx, cy = dx, 2.62
    make_chamfer_box("Desk_Chair_Seat", (cx, cy, 0.50), (0.60, 0.48, 0.10), COL_LEATHER, chamfer=0.03)
    make_chamfer_box("Antonio_Chair_Back", (cx, cy + 0.21, 1.02), (0.60, 0.06, 1.02), COL_LEATHER, chamfer=0.02)
    for ai, ax in enumerate((-0.32, 0.32)):
        make_tube(f"Desk_Chair_Arm_{ai}", [(cx + ax, cy + 0.19, 0.55), (cx + ax, cy + 0.19, 0.73), (cx + ax, cy - 0.16, 0.73)],
                  0.018, COL_OAK_DARK, segments=6)
    make_lathe("Desk_Chair_Pillar", (cx, cy, 0.06), [(0.045, 0.0), (0.045, 0.32), (0.06, 0.36), (0.06, 0.39), (0.0, 0.39)],
               P.METAL_BLACK, segments=8)
    for si in range(5):
        a = si * 2.0 * math.pi / 5.0 + 0.3
        make_rot_box(f"Desk_Chair_Star_{si}", (cx + 0.14 * math.cos(a), cy + 0.14 * math.sin(a), 0.055), (0.28, 0.04, 0.035),
                     P.METAL_BLACK, yaw=a)
        make_cyl(f"Desk_Chair_Caster_{si}", (cx + 0.27 * math.cos(a), cy + 0.27 * math.sin(a), 0.025), 0.025, 0.04,
                 P.METAL_BLACK, axis='Y', segments=6)
    # the visitor's chair, facing the desk
    vx, vy = -0.40, 1.40
    for lx in (-0.18, 0.18):
        for ly in (-0.18, 0.18):
            make_box(f"Visitor_Chair_Leg_{lx:+.2f}_{ly:+.2f}", (vx + lx, vy + ly, 0.225), (0.04, 0.04, 0.45), WOOD)
    make_box("Visitor_Chair_Seat", (vx, vy, 0.47), (0.42, 0.42, 0.04), WOOD)
    make_box("Visitor_Chair_Back", (vx, vy - 0.19, 0.80), (0.42, 0.04, 0.62), WOOD)
    # ── on the desk ──
    lx_, ly_ = dx - 0.50, dy + 0.18
    make_lathe("Lamp_Base", (lx_, ly_, top), [(0.0, 0.0), (0.09, 0.0), (0.08, 0.02), (0.04, 0.03), (0.012, 0.035), (0.012, 0.22), (0.0, 0.22)],
               COL_BRASS, segments=10)
    make_tube("Lamp_Arm", [(lx_, ly_, top + 0.21), (lx_, ly_ - 0.06, top + 0.27)], 0.008, COL_BRASS, segments=5)
    make_cyl("Lamp_Shade", (lx_, ly_ - 0.06, top + 0.27), 0.075, 0.34, COL_BANKER_GREEN, axis='X', segments=10)
    # the smartphone, face-down ("The screen said Q. PAUL")
    make_box("Cell_Phone", (dx + 0.30, dy - 0.10, top + 0.0045), (0.075, 0.155, 0.009), (0.12, 0.12, 0.14, 1.0))
    make_box("Cell_Phone_Camera", (dx + 0.28, dy - 0.04, top + 0.0105), (0.025, 0.025, 0.003), (0.30, 0.30, 0.32, 1.0))
    # the bourbon and the chipped glass
    make_lathe("Bourbon_Bottle", (dx - 0.25, dy + 0.15, top), [(0.0, 0.0), (0.045, 0.0), (0.05, 0.03), (0.05, 0.17), (0.03, 0.22), (0.016, 0.24), (0.016, 0.28), (0.0, 0.28)],
               (0.48, 0.30, 0.12, 0.9), segments=8)
    make_cyl("Chipped_Glass", (dx - 0.10, dy + 0.07, top + 0.045), 0.04, 0.09, (0.72, 0.74, 0.70, 0.6), segments=8)
    # the rolled plans, with their paper ends
    for ri, (rx, ry) in enumerate(((dx - 0.20, dy - 0.15), (dx - 0.14, dy - 0.25))):
        make_cyl(f"Plans_Roll_{ri}", (rx, ry, top + 0.045), 0.045, 0.72, (0.70, 0.76, 0.86, 1.0), segments=10, axis='X')
        for sgn in (-1, 1):
            make_cyl(f"Plans_Roll_{ri}_End_{sgn:+d}", (rx + sgn * 0.362, ry, top + 0.045), 0.040, 0.004, PAPER, segments=10, axis='X')
    # Jimmy's two coffees, a laptop, a tape measure
    for i, (cx_, cy_) in enumerate(((dx + 0.52, dy - 0.20), (dx + 0.62, dy - 0.10))):
        make_cyl(f"Jimmy_Coffee_{i}", (cx_, cy_, top + 0.06), 0.04, 0.12, (0.92, 0.90, 0.86, 1.0), segments=10)
        make_cyl(f"Jimmy_Coffee_{i}_Lid", (cx_, cy_, top + 0.125), 0.042, 0.01, (0.20, 0.20, 0.22, 1.0), segments=10)
    make_box("Laptop", (dx + 0.32, dy + 0.20, top + 0.011), (0.34, 0.24, 0.022), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Tape_Measure", (dx + 0.58, dy + 0.18, top + 0.035), 0.035, 0.07, (0.90, 0.72, 0.20, 1.0), segments=10)


def build_room_things():
    """The file cabinet (the bourbon lives in it; the hard hat on top),
    the permits board and the sample boards, the fixture boxes, the worn
    runner, the box fan, the clock, the calendar, the ceiling fan."""
    fx, fy = X1 - 0.33, 0.62
    make_box("File_Cabinet", (fx, fy, 0.66), (0.46, 0.62, 1.32), (0.48, 0.48, 0.46, 1.0))
    for di in range(4):
        make_box(f"File_Cabinet_Drawer_{di}", (fx - 0.235, fy, 1.15 - di * 0.31), (0.01, 0.56, 0.27), (0.54, 0.54, 0.52, 1.0))
        make_box(f"File_Cabinet_Handle_{di}", (fx - 0.245, fy, 1.20 - di * 0.31), (0.012, 0.14, 0.02), (0.70, 0.70, 0.68, 1.0))
    make_lathe("Hard_Hat", (fx, fy, 1.32), [(0.0, 0.0), (0.14, 0.0), (0.135, 0.04), (0.12, 0.08), (0.09, 0.12), (0.05, 0.145), (0.0, 0.15)],
               (0.92, 0.72, 0.18, 1.0), segments=12)
    # the permits board on the west wall, north of the front door
    wx = X0 + 0.10
    make_box("Permit_Board", (wx + 0.014, 2.25, 1.65), (0.028, 1.00, 0.78), (0.62, 0.48, 0.30, 1.0))
    import random
    rnd = random.Random(31)
    for i in range(8):
        py = 1.82 + rnd.uniform(0.0, 0.86)
        pz = 1.34 + rnd.uniform(0.0, 0.58)
        w_, h_ = rnd.choice(((0.14, 0.20), (0.20, 0.14), (0.11, 0.16)))
        make_box(f"Permit_{i}", (wx + 0.0295, py, pz), (0.003, w_, h_), rnd.choice((PAPER, (0.96, 0.92, 0.70, 1.0), (0.84, 0.90, 0.96, 1.0))))
        make_cyl(f"Permit_{i}_Pin", (wx + 0.034, py, pz + h_ / 2.0 - 0.012), 0.006, 0.006, (0.80, 0.20, 0.18, 1.0), segments=6, axis='X')
    for i, (y, kind) in enumerate(((2.58, 0), (2.64, 1), (2.70, 2))):
        make_box(f"Sample_Board_{i}", (wx + 0.012 + i * 0.022, y, 0.42), (0.02, 0.46, 0.80), (0.86, 0.84, 0.78, 1.0))
    for k in range(6):
        make_box(f"Sample_{k}", (wx + 0.067, 2.70 - 0.15 + (k % 3) * 0.15, 0.26 + (k // 3) * 0.30), (0.012, 0.12, 0.20),
                 ((0.52, 0.30, 0.22, 1.0), (0.42, 0.30, 0.20, 1.0), (0.72, 0.74, 0.70, 1.0))[k % 3])
    make_box("Fixture_Box_A", (X0 + 0.45, D - 0.35, 0.22), (0.46, 0.38, 0.44), (0.60, 0.48, 0.32, 1.0))
    make_box("Fixture_Box_B", (X0 + 0.45, D - 0.35, 0.61), (0.40, 0.34, 0.34), (0.58, 0.46, 0.30, 1.0))
    make_box("Fixture_Box_Label", (X0 + 0.45, D - 0.541, 0.26), (0.22, 0.004, 0.10), PAPER)
    # the pacing runner in front of the windows, worn where he paces
    make_box("Pacing_Carpet", (-0.10, 0.82, 0.006), (2.60, 0.55, 0.012), (0.40, 0.22, 0.20, 1.0))
    make_box("Pacing_Path", (-0.10, 0.82, 0.0135), (2.20, 0.20, 0.003), (0.32, 0.18, 0.16, 1.0))
    # August: the box fan by the leaded window
    make_box("Box_Fan", (LEAD_X, 0.40, 0.27), (0.52, 0.14, 0.52), (0.80, 0.78, 0.72, 1.0))
    make_cyl("Box_Fan_Grille", (LEAD_X, 0.475, 0.29), 0.21, 0.01, (0.30, 0.30, 0.32, 1.0), segments=16, axis='Y')
    make_box("Box_Fan_Foot", (LEAD_X, 0.40, 0.005), (0.56, 0.20, 0.01), (0.30, 0.30, 0.32, 1.0))
    # the clock on the pier between the windows, the calendar by the back door
    make_wall_clock("Clock", (0.0, 0.10, 2.20), frozen_hour=1, frozen_min=12, facing='+Y')
    # (the calendar helper prints on +x; this wall faces -x into the room)
    make_box("Site_Calendar_Body", (X1 - 0.1025, 1.45, 1.55), (0.005, 0.40, 0.50), (0.78, 0.62, 0.46, 1.0))
    make_box("Site_Calendar_Grid", (X1 - 0.1055, 1.45, 1.40), (0.001, 0.34, 0.20), PAPER)
    make_box("Site_Calendar_Photo", (X1 - 0.1055, 1.45, 1.66), (0.001, 0.34, 0.20), (0.40, 0.52, 0.56, 1.0))
    # the ceiling fan, its light
    fz = CEIL - 0.04
    make_cyl("Ceiling_Fan_Mount", (0.0, 1.45, fz - 0.02), 0.06, 0.04, (0.30, 0.24, 0.18, 1.0), segments=10)
    make_cyl("Ceiling_Fan_Rod", (0.0, 1.45, fz - 0.16), 0.012, 0.24, (0.30, 0.24, 0.18, 1.0), segments=6)
    make_cyl("Ceiling_Fan_Motor", (0.0, 1.45, fz - 0.33), 0.11, 0.10, (0.30, 0.24, 0.18, 1.0), segments=12)
    for k in range(4):
        a = k * math.pi / 2.0 + 0.3
        make_rot_box(f"Ceiling_Fan_Blade_{k}", (0.40 * math.cos(a), 1.45 + 0.40 * math.sin(a), fz - 0.33),
                     (0.58, 0.13, 0.012), (0.42, 0.30, 0.20, 1.0), yaw=a)
    make_blob("Ceiling_Fan_Globe", (0.0, 1.45, fz - 0.45), 0.08, (0.96, 0.92, 0.80, 1.0), noise=0.0, seed=1, squash=0.9)
    # cords: the lamp to the north wall, the AC to the south
    make_wall_outlet("Outlet_N", (-0.95, D), axis='X', face_sign=-1, z=0.30, aged=True)
    make_tube("Cord_Lamp", [(-0.45, 2.39, 0.78), (-0.95, D - 0.13, 0.30)], 0.007, (0.16, 0.16, 0.18, 1.0), segments=5)
    make_wall_outlet("Outlet_S", (-1.45, 0.0), axis='X', face_sign=1, z=0.30, aged=True)
    make_tube("Cord_AC", [(AC_X - 0.20, 0.31, sill_of_ac()), (-1.45, 0.13, 0.30)], 0.008, (0.16, 0.16, 0.18, 1.0), segments=5)
    make_floor_stain("AC_Drip_Ring", (AC_X, 0.62), radius=0.10, tint=(0.36, 0.26, 0.18, 1.0))


def sill_of_ac():
    return 1.30 - 0.49 + 0.10


# ── a storey down: the street, the Marigny ─────────────────────────
def build_street():
    z = Z_ST
    # the building's own face below and beside the office
    make_box("Out_Facade_Below", (0.0, 0.0, z / 2.0), (14.0, 0.2, -z), BRICK)
    for sgn in (-1, 1):
        make_box(f"Out_Facade_Upper_{'W' if sgn < 0 else 'E'}", (sgn * (X1 + 0.1 + 2.5), 0.0, 2.8), (5.0, 0.2, 5.6), BRICK)
    make_box("Out_Facade_Above", (0.0, 0.0, (CEIL + 5.6) / 2.0), (W + 0.4, 0.2, 5.6 - CEIL), BRICK)
    # sidewalks, curbs, the street
    make_box("Ground_Sidewalk_N", (0.0, -1.05, z - 0.03), (30.0, 1.9, 0.06), (0.58, 0.56, 0.52, 1.0))
    make_box("Ground_Street", (0.0, -5.5, z - 0.08), (30.0, 7.0, 0.06), (0.26, 0.26, 0.28, 1.0))
    make_box("Ground_Sidewalk_S", (0.0, -10.0, z - 0.03), (30.0, 2.0, 0.06), (0.58, 0.56, 0.52, 1.0))
    # the Creole cottages across, their iron galleries rusting into lacework
    for ci, (cx, col) in enumerate(((-9.0, (0.70, 0.56, 0.44, 1.0)), (-3.0, (0.56, 0.62, 0.58, 1.0)),
                                    (3.0, (0.82, 0.74, 0.56, 1.0)), (9.0, (0.62, 0.46, 0.44, 1.0)))):
        make_box(f"Out_Cottage_{ci}", (cx, -11.6, z + 3.5), (5.8, 0.4, 7.0), col)
        for di, dx in enumerate((-1.6, 0.0, 1.6)):
            make_box(f"Out_Cottage_{ci}_Shutter_{di}", (cx + dx, -11.39, z + 1.4), (0.9, 0.02, 2.2), (0.18, 0.30, 0.24, 1.0))
            make_box(f"Out_Cottage_{ci}_Shutter_Up_{di}", (cx + dx, -11.39, z + 4.7), (0.8, 0.02, 1.8), (0.18, 0.30, 0.24, 1.0))
        make_box(f"Out_Cottage_{ci}_Gallery", (cx, -10.85, z + 3.45), (5.8, 1.1, 0.12), IRON)
        make_box(f"Out_Cottage_{ci}_Gallery_Rail", (cx, -10.32, z + 4.48), (5.8, 0.04, 0.05), IRON)
        for pi in range(9):
            make_box(f"Out_Cottage_{ci}_Gallery_Bal_{pi}", (cx - 2.8 + pi * 0.7, -10.32, z + 3.98), (0.025, 0.025, 0.95), IRON)
        for sgn in (-1, 1):
            make_cyl(f"Out_Cottage_{ci}_Post_{sgn:+d}", (cx + sgn * 2.75, -10.36, z + 1.70), 0.05, 3.40, IRON, segments=8)
    # the oaks, dripping moss
    for oi, (ox, oy, h) in enumerate(((-6.4, -9.6, 7.5), (5.6, -9.8, 7.0))):
        make_taper_cyl(f"Out_Oak_{oi}_Trunk", (ox, oy, z + h * 0.3), 0.50, 0.32, h * 0.6, (0.34, 0.26, 0.18, 1.0), segments=9)
        for k, (dx, dy, dz, r) in enumerate(((0.0, 0.0, 0.72, 3.2), (-2.4, 1.6, 0.62, 2.4), (2.2, 1.8, 0.66, 2.6), (0.6, 3.0, 0.70, 2.2))):
            make_blob(f"Out_Oak_{oi}_Canopy_{k}", (ox + dx, oy + dy, z + h * dz + 1.6), r, (0.28, 0.40, 0.22, 1.0),
                      noise=0.25, seed=oi * 7 + k, squash=0.7)
        for mi, (mx, my, ml) in enumerate(((-1.6, 1.2, 1.6), (1.2, 2.2, 1.3), (-0.4, 3.4, 1.8), (2.0, 0.4, 1.2))):
            make_box(f"Out_Oak_{oi}_Moss_{mi}", (ox + mx, oy + my, z + h * 0.6 + 1.0), (0.12, 0.08, ml), (0.56, 0.62, 0.50, 1.0))
    # the streetlight on the far corner, and the man in the charcoal suit beside it
    sx, sy = 2.40, -9.30
    make_cyl("Out_Streetlight_Pole", (sx, sy, z + 2.5), 0.07, 5.0, (0.20, 0.22, 0.22, 1.0), segments=8)
    make_cyl("Out_Streetlight_Arm", (sx, sy + 0.55, z + 4.95), 0.03, 1.1, (0.20, 0.22, 0.22, 1.0), segments=6, axis='Y')
    make_box("Out_Streetlight_Head", (sx, sy + 1.10, z + 4.90), (0.30, 0.46, 0.14), (0.92, 0.88, 0.70, 1.0))
    from human_sculpt import human_figure
    human_figure("Out_Charcoal_Suit_Man", base_x=sx - 0.30, base_y=sy + 0.10, base_z=z, scale=1.0, facing='+Y',
                 body_type='male_tall', skin_color=(0.72, 0.58, 0.48, 1.0), hair_color=(0.66, 0.64, 0.62, 1.0),
                 jacket_color=(0.22, 0.22, 0.24, 1.0), pants_color=(0.22, 0.22, 0.24, 1.0), shoe_color=(0.08, 0.08, 0.08, 1.0))
    # the dark sedan, parked carefully in the shadow of the dumpster
    cx, cy = -3.40, -8.10
    make_box("Out_Sedan_Body", (cx, cy, z + 0.62), (4.7, 1.82, 0.66), (0.10, 0.11, 0.13, 1.0))
    make_box("Out_Sedan_Glass", (cx + 0.2, cy, z + 1.18), (2.4, 1.62, 0.46), (0.08, 0.10, 0.12, 0.7))
    make_box("Out_Sedan_Roof", (cx + 0.2, cy, z + 1.43), (2.4, 1.62, 0.05), (0.10, 0.11, 0.13, 1.0))
    for wx_ in (cx - 1.5, cx + 1.5):
        for sgn in (-1, 1):
            make_cyl(f"Out_Sedan_Wheel_{wx_:.1f}_{sgn:+d}", (wx_, cy + sgn * 0.82, z + 0.33), 0.33, 0.20,
                     (0.06, 0.06, 0.06, 1.0), axis='Y', segments=14)
    make_box("Out_Dumpster", (-6.6, -9.75, z + 0.65), (1.9, 1.1, 1.3), (0.20, 0.34, 0.26, 1.0))
    make_box("Out_Dumpster_Lid", (-6.6, -9.75, z + 1.33), (1.95, 1.15, 0.06), (0.16, 0.26, 0.20, 1.0))


# ── a storey down to the north: the warehouse that will be Ember & Ash ──
def build_warehouse():
    z = Z_ST
    y0, y1, x0, x1, top = D + 0.15, 16.0, -7.0, 7.0, 5.6
    make_box("WH_Ground_Floor", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z - 0.03), (x1 - x0, y1 - y0, 0.06), (0.46, 0.44, 0.40, 1.0))
    # brick, with graffiti prayers and curses
    make_box("WH_Wall_W", (x0 - 0.1, (y0 + y1) / 2.0, (z + top) / 2.0), (0.2, y1 - y0, top - z), BRICK)
    make_box("WH_Wall_E", (x1 + 0.1, (y0 + y1) / 2.0, (z + top) / 2.0), (0.2, y1 - y0, top - z), BRICK)
    make_box("WH_Wall_N", ((x0 + x1) / 2.0, y1 + 0.1, (z + top) / 2.0), (x1 - x0 + 0.4, 0.2, top - z), BRICK_DK)
    # the south wall of the floor: below the office, and beside and above it
    make_box("WH_Wall_S_Below", (0.0, y0 + 0.1, z / 2.0), (x1 - x0, 0.2, -z), BRICK_DK)
    for sgn in (-1, 1):
        make_box(f"WH_Wall_S_{'W' if sgn < 0 else 'E'}", (sgn * (X1 + 0.15 + (x1 - X1 - 0.15) / 2.0), y0 + 0.1, top / 2.0),
                 (x1 - X1 - 0.15, 0.2, top), BRICK_DK)
    make_box("WH_Wall_S_Above", (0.0, y0 + 0.1, (CEIL + top) / 2.0), (W + 0.3, 0.2, top - CEIL), BRICK_DK)
    for gi, (gx, gy, gz, gw, gh, col) in enumerate(((x0 + 0.005, 7.5, z + 1.8, 2.6, 1.2, (0.62, 0.22, 0.30, 1.0)),
                                                    (x0 + 0.005, 12.0, z + 1.3, 1.8, 0.9, (0.22, 0.42, 0.62, 1.0)),
                                                    (x1 - 0.005, 9.5, z + 2.0, 3.0, 1.0, (0.86, 0.72, 0.24, 1.0)),
                                                    (x1 - 0.005, 13.6, z + 1.1, 1.4, 0.7, (0.92, 0.92, 0.88, 1.0)))):
        make_box(f"WH_Graffiti_{gi}", (gx, gy, gz), (0.01, gw, gh), col)
    make_box("WH_Roof", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top + 0.1), (x1 - x0 + 0.4, y1 - y0 + 0.4, 0.2), (0.16, 0.14, 0.13, 1.0))
    for ti, ty in enumerate((5.5, 8.5, 11.5, 14.5)):
        make_box(f"WH_Truss_{ti}_Chord", (0.0, ty, top - 0.65), (x1 - x0, 0.18, 0.22), (0.22, 0.20, 0.18, 1.0))
        for k in range(5):
            make_box(f"WH_Truss_{ti}_Post_{k}", (-5.6 + k * 2.8, ty, top - 0.27), (0.14, 0.14, 0.55), (0.22, 0.20, 0.18, 1.0))
    # THE CYPRESS BEAM, hanging crooked on two chain hoists over two ladders
    bx, by, bz, bl = 0.4, 8.5, z + 3.40, 6.0      # just over the ladders' tops, under the office floor's level
    make_rot_box("Cypress_Beam", (bx, by, bz), (bl, 0.30, 0.32), (0.56, 0.40, 0.26, 1.0), pitch=0.035)
    for k, sgn in enumerate((-1, 1)):
        ex = bx + sgn * (bl / 2.0 - 0.6)
        ez = bz - sgn * 0.035 * (bl / 2.0 - 0.6)
        make_tube(f"Cypress_Beam_Chain_{k}", [(ex, by, ez + 0.16), (ex, by, top - 0.76)], 0.02, (0.30, 0.30, 0.30, 1.0), segments=5)
        make_box(f"Cypress_Beam_Hoist_{k}", (ex, by, ez + 0.95), (0.20, 0.16, 0.26), (0.70, 0.56, 0.12, 1.0))
        lx = ex + sgn * 0.3
        for side in (-1, 1):
            make_rot_box(f"Ladder_{k}_Rail_{side:+d}", (lx, by + side * 0.32, z + 1.55), (0.06, 0.06, 3.15),
                         (0.70, 0.62, 0.40, 1.0), roll=-side * 0.13)
    # salvage: old doors against the west wall, planks, a clawfoot tub, crates
    for di in range(4):
        make_rot_box(f"Salvage_Door_{di}", (x0 + 0.20 + di * 0.07, 5.2 + di * 0.08, z + 1.02), (0.04, 0.84, 2.04),
                     ((0.42, 0.30, 0.22, 1.0), (0.36, 0.44, 0.40, 1.0), (0.56, 0.46, 0.34, 1.0), (0.30, 0.24, 0.20, 1.0))[di],
                     pitch=-0.08)
    for pi in range(5):
        make_box(f"Salvage_Planks_{pi}", (-3.4, 11.0 + (pi % 2) * 0.05, z + 0.06 + pi * 0.12), (3.2, 0.9, 0.11),
                 (0.46 + 0.03 * pi, 0.34, 0.24, 1.0))
    make_blob("Salvage_Tub_Body", (4.4, 12.4, z + 0.38), 0.55, (0.90, 0.88, 0.84, 1.0), noise=0.02, seed=3, squash=0.62)
    for fi, (fx, fy) in enumerate(((3.95, 12.05), (4.85, 12.05), (3.95, 12.75), (4.85, 12.75))):
        make_cyl(f"Salvage_Tub_Foot_{fi}", (fx, fy, z + 0.05), 0.05, 0.10, COL_BRASS, segments=8)
    for ci, (cx, cy) in enumerate(((5.2, 6.2), (5.9, 6.5), (5.5, 6.9))):
        make_box(f"Salvage_Crate_{ci}", (cx, cy, z + 0.26 + (0.52 if ci == 2 else 0.0)), (0.62, 0.52, 0.52), (0.62, 0.50, 0.34, 1.0))
    # the crew's radio on a sawhorse (they're out on their thirty-minute lunch)
    for k, sx in enumerate((1.9, 3.1)):
        make_box(f"Sawhorse_{k}_Top", (sx, 6.3, z + 0.78), (0.10, 0.90, 0.08), (0.62, 0.50, 0.34, 1.0))
        for side in (-1, 1):
            make_rot_box(f"Sawhorse_{k}_Leg_{side:+d}", (sx + side * 0.12, 6.3, z + 0.37), (0.05, 0.80, 0.76),
                         (0.62, 0.50, 0.34, 1.0), roll=0.0, pitch=side * 0.30)
    make_box("Sawhorse_Plank", (2.5, 6.3, z + 0.845), (1.6, 0.30, 0.05), (0.66, 0.54, 0.38, 1.0))
    make_box("Crew_Radio", (2.2, 6.3, z + 0.955), (0.36, 0.14, 0.17), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Crew_Radio_Antenna", (2.33, 6.3, z + 1.24), 0.004, 0.40, (0.70, 0.70, 0.72, 1.0), segments=4)
    make_box("Crew_Lunch_Cooler", (2.9, 6.3, z + 0.98), (0.40, 0.28, 0.22), (0.74, 0.20, 0.18, 1.0))
    # the crew is "outside, on their thirty-minute lunch": what they left
    make_box("Crew_Lunch_Bag", (2.35, 6.92, z + 0.13), (0.18, 0.12, 0.26), (0.66, 0.52, 0.34, 1.0))
    for ci, (cx, cy) in enumerate(((2.70, 6.95), (2.84, 7.05))):
        make_cyl(f"Crew_Lunch_Can_{ci}", (cx, cy, z + 0.06), 0.033, 0.12, ((0.70, 0.16, 0.14, 1.0), (0.82, 0.82, 0.80, 1.0))[ci], segments=10)
    make_blob("Crew_Lunch_Foil", (3.05, 6.85, z + 0.04), 0.06, (0.82, 0.82, 0.84, 1.0), noise=0.35, seed=5, squash=0.6)
    # a work light on its tripod
    make_cyl("Work_Light_Pole", (2.8, 8.5, z + 0.95), 0.02, 1.9, (0.20, 0.20, 0.20, 1.0), segments=6)
    for k in range(3):
        a = k * 2.094
        make_rot_box(f"Work_Light_Leg_{k}", (2.8 + 0.22 * math.cos(a), 8.5 + 0.22 * math.sin(a), z + 0.25), (0.03, 0.03, 0.55),
                     (0.20, 0.20, 0.20, 1.0), yaw=a, pitch=0.6)
    make_box("Work_Light_Head", (2.8, 8.42, z + 1.95), (0.30, 0.12, 0.24), (0.96, 0.86, 0.30, 1.0))


def main():
    clear_scene()
    build_shell()
    build_openings()
    build_desk_and_chairs()
    build_room_things()
    build_street()
    build_warehouse()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/new_orleans_office.glb"))
    print(f"\n[build_new_orleans_office] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
