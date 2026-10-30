"""nick_house — vol 3's "uncle nick": Nick's grandmother's house, its garage
and Nick's room (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Halloween night, and "Years later":
  "His grandma's house was unlit from the outside." No decorations since
   Mark left; the mini-bike "sat outside the house"; the neighbour's fence
   the boys shot holes in                → the front (nick_house_front)
  "The garage was Mark's workshop": "Thick old grease and oil stains had
   permanently bonded assembly books and wood chippings to the counter";
   a box of costumes; a broken lightning ball (Nick's hat goes on it)
  the same garage years on: "Nick had built a printing press in his
   grandmother's garage", "the silk-screen printer", comic books and
   T-shirts, the ink brush, the family albums
                                         → one garage, dressed per view
                                           (`__nick_garage_halloween` /
                                           `__nick_print_shop`)
  Nick's room, "empty without his brother Neal": "The walls were lined with
   designs", posters hanging from the ceiling, comics on the floor, the
   child-sized drafting table with the costume sketch, liquid latex and
   make-up tubes, the closet being packed; grandma "asleep on the recliner",
   "the television mute but alive with a shopping channel"
No year is given (lore/_MASTER_TIMELINE.md has none for vol 3's chapters).

Blender: x east, y north, z up; Godot (x, z, -y). The house faces south onto
the street; the garage is its west wing.

DRAFT 2 targets: the living room seen through Nick's door (the TV's glow
as a light); the kitchen of the grilled cheese; Mark's empty room; the
street's other houses dressed for Halloween; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe, make_gable,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_lamp, make_sofa
from _props.trees import make_broadleaf

H, T = 2.6, 0.20
WALL = (0.80, 0.76, 0.66, 1.0); BASE = (0.42, 0.36, 0.28, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
GARAGE_PAL = {"wall": (0.66, 0.64, 0.58, 1.0), "baseboard": (0.40, 0.38, 0.34, 1.0)}
SIDING = (0.62, 0.60, 0.52, 1.0); SIDING_LAP = (0.54, 0.52, 0.45, 1.0); ROOF = (0.30, 0.28, 0.28, 1.0)
CARPET = (0.48, 0.42, 0.34, 1.0); CARPET_SEAM = (0.42, 0.36, 0.30, 1.0)
CONCRETE = (0.56, 0.55, 0.52, 1.0); LAWN = (0.30, 0.38, 0.24, 1.0)
DOOR = (0.70, 0.62, 0.50, 1.0)
HALLOW, PRINT = "__nick_garage_halloween", "__nick_print_shop"
PAPER = [(0.94, 0.92, 0.86, 1.0), (0.90, 0.88, 0.80, 1.0), (0.96, 0.95, 0.90, 1.0), (0.86, 0.84, 0.76, 1.0)]
COMIC = [(0.80, 0.30, 0.24, 1.0), (0.26, 0.40, 0.70, 1.0), (0.92, 0.84, 0.40, 1.0), (0.30, 0.60, 0.40, 1.0)]
# the front's openings (x centre, z centre, w, h): door, two windows, the garage door
FRONT_OPEN = [(-1.0, 1.0, 0.92, 2.0), (-5.6, 1.45, 1.6, 1.2), (4.6, 1.45, 1.4, 1.2), (-10.15, 1.05, 4.6, 2.1)]


def siding(x0, x1, y, openings):
    """Lap siding as strips that stop at every opening."""
    n, k = 13, 0
    for i in range(n):
        z0 = i * H / n
        z1 = z0 + H / n
        cuts = sorted((cx - w / 2.0, cx + w / 2.0) for cx, cz, w, h in openings
                      if cz - h / 2.0 < z1 - 1e-3 and cz + h / 2.0 > z0 + 1e-3)
        xs, a = [], x0
        for ca, cb in cuts:
            if ca > a:
                xs.append((a, ca))
            a = max(a, cb)
        if a < x1:
            xs.append((a, x1))
        for a, b in xs:
            if b - a < 0.02:
                continue
            make_box(f"Siding_Stock_{k}", ((a + b) / 2.0, y, (z0 + z1) / 2.0), (b - a, 0.03, z1 - z0 - 0.006),
                     (SIDING, SIDING_LAP)[i % 2])
            k += 1


def build_shell():
    """The one-storey house x -7..7, y 0..10; the garage x -13.2..-7, y 0..7."""
    make_floor("House_Floor", (0.0, 5.0, 0.0), size_x=14.0, size_y=10.0, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_box("House_Ceil", (0.0, 5.0, H + 0.04), (14.4, 10.4, 0.08), (0.88, 0.86, 0.80, 1.0))
    make_wall_with_openings("House_Wall_S", (0.0, 0.0, 0), length=14.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=FRONT_OPEN[:3])
    make_wall("House_Wall_N", (0.0, 10.0, 0), length=14.4, height=H, thickness=T, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("House_Wall_E", (7.0, 5.0, 0), length=10.0, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("House_Wall_W", (-7.0, 5.0, 0), length=10.0, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(6.0, 1.0, 0.86, 2.0)])
    # the front door, the dark windows (night: no lamp lit behind them)
    make_box("Front_Door", (-1.0, 0.0, 1.0), (0.90, 0.04, 2.0), (0.40, 0.30, 0.24, 1.0))
    for k, (x, w) in enumerate(((-5.6, 1.6), (4.6, 1.4))):
        make_box(f"Front_Window_Pane_{k}", (x, 0.0, 1.45), (w, 0.02, 1.2), (0.08, 0.09, 0.11, 1.0))
        make_box(f"Front_Window_Mullion_{k}", (x, 0.0, 1.45), (0.04, 0.06, 1.2), (0.86, 0.84, 0.78, 1.0))
    # the hall x 0..1.4; the bathroom x 1.4..7, y 0..4.6; Nick's room x 1.4..7, y 4.6..10
    make_wall_with_openings("Wall_Hall_E", (1.4, 5.0, 0), length=9.8, height=H, thickness=0.12, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(2.2, 1.0, 0.82, 2.0), (6.2, 1.0, 0.82, 2.0)])
    make_wall("Wall_Hall_W", (0.0, 7.6, 0), length=4.6, height=H, thickness=0.12, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_Nick_S", (4.23, 4.6, 0), length=5.54, height=H, thickness=0.12, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_box("Bath_Door_Shut", (1.4, 2.2, 1.0), (0.04, 0.80, 2.0), DOOR)
    make_box("Nick_Door_Open", (1.46 + 0.40, 6.2 - 0.43, 1.0), (0.80, 0.04, 2.0), DOOR)
    # the living room (x -7..0, y 0..6): the recliner, the TV on mute
    rc = (0.44, 0.32, 0.26, 1.0)
    make_box("Recliner_Base", (-3.4, 3.4, 0.24), (0.86, 0.90, 0.48), rc)
    make_rot_box("Recliner_Back", (-3.4, 3.86, 0.80), (0.86, 0.16, 0.66), rc, roll=-0.35)
    make_box("Recliner_Footrest", (-3.4, 2.70, 0.34), (0.70, 0.50, 0.10), rc)
    make_box("Recliner_Footrest_Arm", (-3.4, 2.90, 0.33), (0.10, 0.10, 0.12), (0.20, 0.20, 0.20, 1.0))
    make_box("Grandma_Afghan", (-3.4, 3.2, 0.50), (0.84, 0.70, 0.04), (0.60, 0.40, 0.46, 1.0))
    make_box("TV_Stand", (-3.4, 0.36, 0.30), (1.10, 0.48, 0.60), (0.34, 0.26, 0.18, 1.0))
    make_chamfer_box("TV_Set", (-3.4, 0.36, 0.86), (0.70, 0.46, 0.52), (0.18, 0.16, 0.14, 1.0), chamfer=0.04)
    make_box("TV_Screen_Glow", (-3.4, 0.592, 0.88), (0.54, 0.006, 0.40), (0.50, 0.56, 0.72, 1.0))
    make_box("Kitchen_Counter", (-6.6, 7.6, 0.45), (0.60, 2.4, 0.90), (0.66, 0.60, 0.48, 1.0))
    make_box("Kitchen_Counter_Top", (-6.59, 7.6, 0.92), (0.62, 2.4, 0.04), (0.80, 0.78, 0.70, 1.0))
    make_box("Kitchen_Stove", (-6.58, 9.3, 0.45), (0.62, 0.70, 0.90), (0.86, 0.84, 0.80, 1.0))
    # the roof over house and garage
    make_gable("House_Roof", (-3.0, 5.0, H + 0.08 + 1.10), (20.6, 10.8, 2.20), ROOF, ridge_axis='X')
    # the garage (x -13.2..-7.1, y 0..7), its door down for the night
    make_box("Garage_Floor", (-10.15, 3.5, 0.01), (6.1, 7.0, 0.02), CONCRETE)
    make_box("Garage_Ceil", (-10.15, 3.5, H + 0.04), (6.1, 7.0, 0.08), (0.62, 0.60, 0.56, 1.0))
    make_wall("Garage_Wall_N", (-10.15, 7.0, 0), length=6.1, height=H, thickness=T, axis='X', palette=GARAGE_PAL, baseboard_face_sign=-1)
    make_wall("Garage_Wall_W", (-13.2, 3.5, 0), length=7.2, height=H, thickness=T, axis='Y', palette=GARAGE_PAL, baseboard_face_sign=+1)
    make_wall_with_openings("Garage_Wall_S", (-10.15, 0.0, 0), length=6.1, height=H, thickness=T, axis='X', palette=GARAGE_PAL,
                            baseboard_face_sign=+1, openings=[FRONT_OPEN[3]])
    make_box("Garage_Door_Down", (-10.15, 0.0, 1.05), (4.6, 0.04, 2.1), (0.84, 0.82, 0.76, 1.0))
    for k in range(3):
        make_box(f"Garage_Door_Seam_{k}", (-10.15, -0.025, 0.52 + k * 0.52), (4.5, 0.01, 0.03), (0.66, 0.64, 0.58, 1.0))
    make_box("Garage_Bulb_Cord", (-10.15, 3.5, H - 0.10), (0.012, 0.012, 0.20), (0.12, 0.12, 0.12, 1.0))
    make_blob("Garage_Bulb_Glow", (-10.15, 3.5, H - 0.25), 0.05, (0.98, 0.94, 0.80, 1.0), noise=0.0, seed=1)
    make_box("Garage_Door_To_House", (-7.0, 6.0, 1.0), (0.04, 0.84, 2.0), DOOR)
    # the front's lap siding, stopping at every opening
    siding(-13.3, 7.1, -0.115, FRONT_OPEN)
    make_box("Porch_Light_Bracket_Off", (-0.3, -0.15, 1.9), (0.14, 0.04, 0.20), (0.30, 0.30, 0.28, 1.0))


def build_garage_dressing():
    # the workbench on the N wall (both years): the old counter, its stains
    bx, by = -10.15, 7.0 - 0.10 - 0.36
    wood = (0.42, 0.34, 0.24, 1.0)
    make_box("Workbench_Top", (bx, by, 0.92), (3.6, 0.72, 0.06), wood)
    make_box("Workbench_Shelf", (bx, by, 0.30), (3.44, 0.66, 0.04), wood)
    for s in (-1, 1):
        make_box(f"Workbench_Leg_{s:+d}", (bx + s * 1.76, by, 0.445), (0.08, 0.66, 0.89), (0.36, 0.28, 0.20, 1.0))
    for k in range(6):
        make_box(f"Workbench_Stain_{k}", (bx - 1.4 + k * 0.55, by + (k % 2) * 0.12, 0.951), (0.30 + (k % 3) * 0.1, 0.20, 0.002),
                 (0.16, 0.14, 0.12, 1.0))
    make_box("Pegboard_Mounted", (bx, 7.0 - 0.11, 1.70), (3.4, 0.02, 1.10), (0.62, 0.52, 0.36, 1.0))
    for k in range(7):
        make_box(f"Pegboard_Hang_Tool_{k}", (bx - 1.4 + k * 0.46, 7.0 - 0.135, 1.70 + (k % 2) * 0.2), (0.05, 0.03, 0.30 + (k % 3) * 0.08),
                 (0.30, 0.30, 0.32, 1.0))
    # Halloween: Mark's workshop half cleaned: the assembly books bonded to
    # the counter, the chips, the box of costumes, the broken lightning ball
    for k in range(4):
        make_rot_box(f"Assembly_Book_{k}" + HALLOW, (bx - 1.2 + k * 0.30, by - 0.05, 0.960), (0.24, 0.30, 0.012),
                     (0.80, 0.76, 0.62, 1.0), yaw=(k % 3 - 1) * 0.3)
    for k in range(10):
        make_rot_box(f"Wood_Chip_{k}" + HALLOW, (bx - 0.2 + (k % 5) * 0.16, by + 0.14 - (k // 5) * 0.22, 0.957), (0.05, 0.02, 0.006),
                     (0.80, 0.66, 0.44, 1.0), yaw=k)
    make_box("Costume_Box" + HALLOW, (bx + 2.3, by - 0.9, 0.25), (0.70, 0.50, 0.50), (0.62, 0.48, 0.32, 1.0))
    make_box("Costume_Cape" + HALLOW, (bx + 2.3, by - 0.9, 0.52), (0.60, 0.40, 0.04), (0.16, 0.12, 0.14, 1.0))
    make_cyl("Lightning_Ball_Base" + HALLOW, (bx + 1.0, by, 1.00), 0.08, 0.10, (0.14, 0.14, 0.16, 1.0), segments=12)
    make_blob("Lightning_Ball_Globe" + HALLOW, (bx + 1.0, by, 1.17), 0.12, (0.60, 0.56, 0.70, 1.0), noise=0.0, seed=2, squash=1.0)
    make_lathe("Lightning_Ball_Hat" + HALLOW, (bx + 1.0, by, 1.285),
               [(0.0, 0.0), (0.16, 0.0), (0.16, 0.02), (0.08, 0.03), (0.08, 0.14), (0.0, 0.14)], (0.12, 0.12, 0.12, 1.0), segments=14)
    make_chamfer_box("Spare_Parts_Crate" + HALLOW, (-12.5, 2.0, 0.21), (0.60, 1.00, 0.40), (0.50, 0.30, 0.20, 1.0), chamfer=0.05)
    # years later: the press Nick built, the T-shirts on a line, the comic
    # pages, the ink brush, the family albums
    px, py = -10.6, 3.6
    make_box("Press_Table" + PRINT, (px, py, 0.45), (1.40, 1.00, 0.90), (0.36, 0.30, 0.24, 1.0))
    make_box("Press_Platen" + PRINT, (px, py, 0.93), (0.60, 0.80, 0.06), (0.20, 0.20, 0.22, 1.0))
    make_box("Press_Hinge_Bar" + PRINT, (px - 0.62, py, 0.93), (0.06, 0.90, 0.06), (0.30, 0.30, 0.32, 1.0))
    make_rot_box("Press_Screen_Frame" + PRINT, (px - 0.40, py, 1.12), (0.04, 0.80, 0.50), (0.50, 0.40, 0.28, 1.0), pitch=0.5)
    make_box("Press_Squeegee" + PRINT, (px + 0.45, py - 0.30, 0.93), (0.06, 0.40, 0.06), (0.20, 0.20, 0.20, 1.0))
    make_box("Shirt_Line_Hang" + PRINT, (-10.15, 5.6, 2.20), (5.9, 0.012, 0.012), (0.80, 0.80, 0.78, 1.0))
    for s in (-1, 1):
        make_box(f"Shirt_Line_Hook_Mounted_{s:+d}" + PRINT, (-10.15 + s * 2.98, 5.6, 2.20), (0.04, 0.04, 0.06), (0.30, 0.30, 0.32, 1.0))
    for k in range(6):
        make_box(f"Shirt_Hang_{k}" + PRINT, (-12.4 + k * 0.9, 5.6, 1.86), (0.60, 0.02, 0.66), ((0.92, 0.92, 0.90, 1.0), (0.16, 0.16, 0.18, 1.0))[k % 2])
    for k in range(5):
        make_box(f"Comic_Page_{k}" + PRINT, (bx - 1.4 + k * 0.42, by - 0.05, 0.952), (0.30, 0.42, 0.004), (0.96, 0.96, 0.94, 1.0))
    make_rot_box("Ink_Brush" + PRINT, (bx + 0.7, by - 0.22, 0.962), (0.20, 0.012, 0.012), (0.20, 0.16, 0.12, 1.0), yaw=0.4)
    make_box("Ink_Pot" + PRINT, (bx + 0.9, by - 0.08, 0.99), (0.08, 0.08, 0.08), (0.06, 0.06, 0.06, 1.0))
    for k in range(3):
        make_box(f"Family_Album_{k}" + PRINT, (bx + 1.4, by - 0.10, 0.97 + k * 0.04), (0.34, 0.28, 0.04),
                 ((0.40, 0.24, 0.20, 1.0), (0.24, 0.30, 0.40, 1.0), (0.50, 0.44, 0.30, 1.0))[k])
    for k in range(4):
        make_box(f"Comics_Stack_{k}" + PRINT, (-12.6, 5.2 + k * 0.45, 0.20), (0.40, 0.30, 0.40), (0.86, 0.82, 0.72, 1.0))
    # a shop stool (built here, not with make_chair, so every part ends in
    # the preset suffix Background3D reads)
    stw = (0.40, 0.30, 0.22, 1.0)
    make_cyl("Print_Stool_Seat" + PRINT, (-9.4, 4.4, 0.64), 0.17, 0.04, stw, segments=12)
    for k in range(4):
        a = k * math.pi / 2.0 + math.pi / 4.0
        make_box(f"Print_Stool_Leg_{k}" + PRINT, (-9.4 + 0.11 * math.cos(a), 4.4 + 0.11 * math.sin(a), 0.31), (0.03, 0.03, 0.62), stw)
    # the shelving on the W wall (both years): cans, jars, boxes
    for lvl in range(3):
        make_box(f"Garage_Shelf_{lvl}", (-13.1 + 0.25, 3.0, 0.40 + lvl * 0.60), (0.50, 3.2, 0.03), (0.50, 0.42, 0.30, 1.0))
    for s_ in (-1, 1):
        make_box(f"Garage_Shelf_Upright_{s_:+d}", (-13.1 + 0.25, 3.0 + s_ * 1.58, 0.92), (0.50, 0.04, 1.84), (0.46, 0.38, 0.28, 1.0))
    for k in range(12):
        lvl, i = k // 4, k % 4
        z = 0.415 + lvl * 0.60
        if k % 3 == 0:
            make_cyl(f"Shelf_Can_{k}", (-12.85, 1.9 + i * 0.7, z + 0.09), 0.08, 0.18, ((0.70, 0.62, 0.40, 1.0), (0.40, 0.46, 0.50, 1.0))[lvl % 2], segments=10)
        else:
            make_box(f"Shelf_Box_{k}", (-12.85, 1.9 + i * 0.7, z + 0.12), (0.36, 0.40, 0.24), (0.62, 0.50, 0.34, 1.0))


def build_garage_2026_10():
    """DRAFT 3 of the garage (2026-10-30): "The garage was Mark's workshop
    until Nick cleaned it up for his own purposes. Thick old grease and oil
    stains ..." The frame was an empty concrete room with a bench at the end.
    Both years: the oil stains on the slab; a bench vise and a drill press on
    the counter; a lumber rack on the E wall; a shop vac in the corner; a
    hand saw and a hammer on the pegboard. Halloween only: a pair of
    sawhorses with a board across, the costume box spilling (a rubber mask,
    a witch's hat, a tail of fabric).
    Draft 4 targets: a car's worth of oil drip under where the car stood,
    extension cords, Mark's coffee cans of screws, the lightning ball's
    cracked glass."""
    bx, by = -10.15, 7.0 - 0.10 - 0.36
    # (stains, not holes: a shade under the slab, two tones, smaller)
    for k, (x, y, r) in enumerate(((-10.4, 1.8, 0.46), (-9.7, 2.5, 0.28), (-10.9, 2.9, 0.34), (-9.2, 1.3, 0.20))):
        make_cyl(f"Garage_Oil_Stain_{k}", (x, y, 0.0205 + 0.0006 * k), r, 0.001, ((0.40, 0.38, 0.35, 1.0), (0.44, 0.42, 0.39, 1.0))[k % 2], segments=18)
    # the vise on the bench's W end, the drill press on its E end
    STEEL = (0.30, 0.34, 0.36, 1.0)
    make_box("Bench_Vise_Body", (bx - 1.66, by - 0.22, 1.03), (0.16, 0.22, 0.14), STEEL)
    make_box("Bench_Vise_Jaw", (bx - 1.66, by - 0.38 - 0.005, 1.05), (0.16, 0.10, 0.12), STEEL)
    make_cyl("Bench_Vise_Bar", (bx - 1.66, by - 0.44, 1.00), 0.012, 0.24, (0.70, 0.70, 0.72, 1.0), axis='X', segments=6)
    dpx, dpy = bx + 1.45, by + 0.10
    make_box("Drill_Press_Base", (dpx, dpy, 0.975), (0.26, 0.36, 0.05), STEEL)
    make_cyl("Drill_Press_Column", (dpx, dpy + 0.12, 1.30), 0.03, 0.62, (0.70, 0.70, 0.72, 1.0), segments=8)
    make_box("Drill_Press_Head", (dpx, dpy + 0.02, 1.58), (0.20, 0.34, 0.20), STEEL)
    make_cyl("Drill_Press_Chuck", (dpx, dpy - 0.08, 1.42), 0.025, 0.12, (0.70, 0.70, 0.72, 1.0), segments=8)
    make_box("Drill_Press_Table", (dpx, dpy - 0.01, 1.18), (0.20, 0.20, 0.02), STEEL)
    # the lumber rack on the E wall
    ex = -7.0 - T / 2.0
    for i, y in enumerate((1.2, 2.5, 3.8)):
        for j, z in enumerate((1.50, 2.00)):
            make_box(f"Lumber_Bracket_{i}_{j}", (ex - 0.20, y, z), (0.40, 0.04, 0.04), (0.30, 0.30, 0.32, 1.0))
    for k in range(5):
        z = 1.50 + 0.035 + 0.5 * (k // 3) + 0.0
        make_box(f"Lumber_Board_{k}", (ex - 0.08 - (k % 3) * 0.10, 2.5, z + (0.0 if k < 3 else 0.0)), (0.09, 3.2 - 0.3 * (k % 2), 0.03),
                 (0.74, 0.60, 0.42, 1.0))
    make_cyl("Shop_Vac", (-12.70, 0.75, 0.25), 0.22, 0.50, (0.86, 0.66, 0.20, 1.0), segments=14)
    make_cyl("Shop_Vac_Lid", (-12.70, 0.75, 0.53), 0.20, 0.06, (0.16, 0.16, 0.18, 1.0), segments=14)
    # a saw and a hammer on the pegboard
    pz = 7.0 - 0.135
    make_box("Pegboard_Saw_Blade", (bx - 0.9, pz, 1.30), (0.50, 0.01, 0.12), (0.72, 0.72, 0.74, 1.0))
    make_box("Pegboard_Saw_Handle", (bx - 0.60, pz, 1.30), (0.12, 0.03, 0.14), (0.50, 0.30, 0.18, 1.0))
    make_box("Pegboard_Hammer_Handle", (bx + 0.62, pz, 1.30), (0.03, 0.03, 0.30), (0.60, 0.46, 0.30, 1.0))
    make_box("Pegboard_Hammer_Head", (bx + 0.62, pz, 1.46), (0.14, 0.04, 0.04), STEEL)
    # Halloween: sawhorses and a board; the costume box spilling
    for i, y in enumerate((2.6, 3.9)):
        make_box(f"Sawhorse_Beam_{i}" + HALLOW, (-8.3, y, 0.68), (0.80, 0.08, 0.08), (0.70, 0.56, 0.38, 1.0))
        for sx in (-1, 1):
            for sy in (-1, 1):
                make_rot_box(f"Sawhorse_Leg_{i}_{sx:+d}_{sy:+d}" + HALLOW, (-8.3 + sx * 0.32, y + sy * 0.10, 0.33), (0.05, 0.04, 0.70),
                             (0.70, 0.56, 0.38, 1.0), roll=sy * 0.25)
    make_box("Sawhorse_Board" + HALLOW, (-8.3, 3.25, 0.735), (0.30, 1.80, 0.03), (0.78, 0.66, 0.48, 1.0))
    cbx, cby = bx + 2.3, by - 0.9
    make_blob("Costume_Mask" + HALLOW, (cbx - 0.48, cby - 0.20, 0.09), 0.10, (0.50, 0.66, 0.34, 1.0), noise=0.3, seed=11, squash=0.6)
    make_lathe("Costume_Witch_Hat" + HALLOW, (cbx + 0.22, cby + 0.05, 0.54), [(0.0, 0.0), (0.18, 0.0), (0.18, 0.01), (0.07, 0.02), (0.0, 0.30)],
               (0.12, 0.10, 0.14, 1.0), segments=12)
    make_rot_box("Costume_Fabric_Tail" + HALLOW, (cbx - 0.45, cby + 0.05, 0.25), (0.06, 0.30, 0.46), (0.60, 0.16, 0.30, 1.0), pitch=0.35)


def build_grandma_living_2026_10():
    """DRAFT 3 of the living room (2026-10-30): "Nick's grandma was asleep
    on the recliner, the television mute but alive with a shopping channel."
    The frame was a recliner and a set in a bare carpeted box. Now a grandma's
    room: the sofa against the W wall with the family's photographs over it,
    a curio cabinet of figurines, a side table at the recliner (the lamp
    off, her glasses, a water glass, the TV Guide), an oval rug, the front
    window's sheers drawn, a wall clock; on the screen the shopping channel's
    velvet, its piece of jewelry and the price banner.
    Draft 4 targets: doilies on the sofa's arms, a candy dish, the kitchen
    beyond lit by the range hood, the hall's photographs."""
    make_sofa("Grandma_Sofa", -6.40, 3.0, back="-X", w=2.0, d=0.86, seats=3, color=(0.56, 0.48, 0.40, 1.0),
              cushion_col=(0.62, 0.54, 0.44, 1.0), arm="roll", leg_col=(0.30, 0.22, 0.16, 1.0), pillows=((0.70, 0.56, 0.60, 1.0),))
    wx = -7.0 + T / 2.0 + 0.012
    for k, (y, z, w, h) in enumerate(((2.35, 1.55, 0.30, 0.38), (2.95, 1.65, 0.44, 0.34), (3.55, 1.50, 0.28, 0.36), (3.0, 2.05, 0.22, 0.26))):
        make_box(f"Grandma_Photo_{k}_Frame", (wx, y, z), (0.024, w, h), (0.60, 0.48, 0.30, 1.0))
        make_box(f"Grandma_Photo_{k}", (wx + 0.013, y, z), (0.004, w - 0.06, h - 0.06), ((0.70, 0.62, 0.52, 1.0), (0.56, 0.58, 0.60, 1.0))[k % 2])
    # the curio cabinet, figurines behind its glass
    cx, cy = -6.68, 5.05
    make_box("Curio_Body", (cx, cy, 0.90), (0.40, 0.90, 1.80), (0.38, 0.26, 0.18, 1.0))
    make_box("Curio_Glass", (cx + 0.205, cy, 1.05), (0.01, 0.78, 1.36), (0.74, 0.80, 0.84, 0.30))
    for lvl in range(3):
        make_box(f"Curio_Shelf_{lvl}", (cx + 0.02, cy, 0.62 + lvl * 0.42), (0.34, 0.80, 0.015), (0.80, 0.80, 0.82, 1.0))
        for i in range(3):
            make_lathe(f"Curio_Figurine_{lvl}_{i}", (cx + 0.04, cy - 0.25 + i * 0.25, 0.63 + lvl * 0.42),
                       [(0.0, 0.0), (0.035, 0.0), (0.03, 0.06), (0.02, 0.10), (0.025, 0.12), (0.0, 0.15)],
                       ((0.92, 0.90, 0.86, 1.0), (0.60, 0.70, 0.86, 1.0), (0.86, 0.66, 0.70, 1.0))[(lvl + i) % 3], segments=10)
    # the side table at the recliner: the lamp (off), her glasses, water, the TV Guide
    sx, sy = -2.55, 3.5
    make_cyl("Grandma_Side_Table", (sx, sy, 0.30), 0.24, 0.60, (0.38, 0.26, 0.18, 1.0), segments=14)
    make_lamp("Grandma_Lamp", sx + 0.06, sy + 0.08, base_z=0.60, h=0.50, shade_col=(0.90, 0.86, 0.74, 1.0))
    make_cyl("Grandma_Water_Glass", (sx - 0.12, sy - 0.08, 0.65), 0.035, 0.10, (0.80, 0.86, 0.88, 1.0), segments=10)
    make_box("Grandma_TV_Guide", (sx + 0.06, sy - 0.12, 0.606), (0.14, 0.20, 0.012), (0.86, 0.80, 0.30, 1.0))
    make_box("Grandma_Glasses", (sx + 0.06, sy - 0.12, 0.616), (0.12, 0.05, 0.008), (0.60, 0.50, 0.30, 1.0))
    make_box("Grandma_Rug", (-3.4, 2.4, 0.006), (2.2, 3.0, 0.012), (0.56, 0.40, 0.34, 1.0))
    make_box("Grandma_Rug_Border", (-3.4, 2.4, 0.0125), (1.9, 2.7, 0.001), (0.66, 0.54, 0.42, 1.0))
    # the front window's sheers, drawn; a clock on the S wall
    for s in (-1, 1):
        make_box(f"Grandma_Sheer_{s:+d}", (-5.6 + s * 0.42, T / 2.0 + 0.015 + (0.02 if s > 0 else 0.0), 1.45), (0.86, 0.02, 1.40), (0.84, 0.80, 0.72, 1.0))
    make_box("Grandma_Sheer_Rod", (-5.6, T / 2.0 + 0.012, 2.18), (1.90, 0.02, 0.02), (0.60, 0.50, 0.30, 1.0))
    make_cyl("Grandma_Wall_Clock", (-2.3, T / 2.0 + 0.02, 1.95), 0.16, 0.03, (0.60, 0.48, 0.30, 1.0), axis='Y', segments=18)
    make_cyl("Grandma_Wall_Clock_Face", (-2.3, T / 2.0 + 0.036, 1.95), 0.13, 0.004, (0.92, 0.90, 0.84, 1.0), axis='Y', segments=18)
    # the shopping channel on the muted set
    make_box("TV_Shop_Velvet", (-3.42, 0.596, 0.92), (0.30, 0.002, 0.22), (0.16, 0.18, 0.40, 1.0))
    make_cyl("TV_Shop_Ring", (-3.42, 0.598, 0.92), 0.04, 0.002, (0.96, 0.82, 0.36, 1.0), axis='Y', segments=14)
    make_box("TV_Shop_Banner", (-3.4, 0.596, 0.72), (0.54, 0.002, 0.07), (0.86, 0.20, 0.24, 1.0))
    make_box("TV_Shop_Price", (-3.25, 0.598, 0.72), (0.18, 0.002, 0.035), (0.98, 0.90, 0.40, 1.0))


def build_nick_room():
    """x 1.46..6.9, y 4.66..9.9: designs on every wall, posters hung from
    the ceiling, comics on the floor, the drafting table, the closet."""
    x0, x1, y0, y1 = 1.46, 6.9, 4.66, 9.9
    closet = (3.4, 4.9)                 # the closet on the N wall, open
    make_box("Closet_Recess_Dark", ((closet[0] + closet[1]) / 2.0, y1 - 0.01, 1.0), (closet[1] - closet[0], 0.02, 2.0), (0.12, 0.10, 0.08, 1.0))
    for s in closet:
        make_box(f"Closet_Jamb_{s:.1f}", (s, y1 - 0.02, 1.02), (0.06, 0.04, 2.04), DOOR)
    make_box("Closet_Head", ((closet[0] + closet[1]) / 2.0, y1 - 0.02, 2.06), (closet[1] - closet[0] + 0.06, 0.04, 0.06), DOOR)
    # the drawings, sheet over sheet, corners curling (a small tilt each)
    k = 0
    for i in range(11):
        x = x0 + 0.30 + i * 0.47
        if closet[0] - 0.25 < x < closet[1] + 0.25:
            continue
        for j in range(4):
            make_rot_box(f"Drawing_Stock_{k}", (x, y1 - 0.003, 0.70 + j * 0.44), (0.36, 0.004, 0.42), PAPER[(i + j) % 4],
                         roll=0.0, yaw=0.0, pitch=((i + j) % 3 - 1) * 0.05)
            k += 1
    for i in range(10):
        y = y0 + 0.30 + i * 0.50
        for j in range(4):
            if 7.5 < y < 9.3 and j < 2:
                continue                # behind the supply shelf
            make_rot_box(f"Drawing_Stock_{k}", (x1 - 0.003, y, 0.70 + j * 0.44), (0.004, 0.36, 0.42), PAPER[(i + j + 1) % 4],
                         roll=((i + j) % 3 - 1) * 0.05)
            k += 1
    for i in range(8):
        make_box(f"Drawing_Stock_{k}", (x0 + 1.2 + i * 0.55, y0 + 0.003, 1.1 + (i % 2) * 0.46), (0.36, 0.004, 0.42), PAPER[i % 4])
        k += 1
    for j in range(3):                  # the hall wall, N of the door
        for i in range(4):
            make_box(f"Drawing_Stock_{k}", (x0 + 0.003, 7.0 + i * 0.5, 0.9 + j * 0.46), (0.004, 0.36, 0.42), PAPER[(i + j) % 4])
            k += 1
    # posters hung from the ceiling on cords
    for i in range(5):
        px, py = x0 + 1.0 + i * 0.95, 7.0 + (i % 2) * 0.9
        make_box(f"Poster_Hang_{i}", (px, py, H - 0.52), (0.60, 0.01, 0.80), ((0.70, 0.26, 0.20, 1.0), (0.20, 0.30, 0.50, 1.0), (0.86, 0.70, 0.30, 1.0))[i % 3])
        make_box(f"Poster_Hang_{i}_Cord", (px, py, H - 0.06), (0.008, 0.008, 0.12), (0.20, 0.20, 0.20, 1.0))
    # the bed by the hall wall; the comics tiling the rest of the floor
    make_bed("Nick_Bed", x0 + 0.06 + 0.98, 8.85, head="-X", w=0.95, d=1.95, made=False, blanket_col=(0.26, 0.30, 0.40, 1.0))
    for i in range(9):
        for j in range(5):
            cx, cy = x0 + 0.45 + i * 0.58, y0 + 0.45 + j * 0.85
            if i == 0 and j <= 1:
                continue                # the door's swing
            if cx < 3.7 and cy > 7.9:
                continue                # the bed
            if cx > 5.6 and cy < 6.9:
                continue                # the drafting table and its stool
            make_rot_box(f"Comic_Floor_Stock_{i}_{j}", (cx, cy, 0.006), (0.22, 0.32, 0.006), COMIC[(i + j) % 4],
                         yaw=((i * 3 + j) % 5 - 2) * 0.3)
    # the child-sized drafting table by the E wall, the costume sketch
    tx, ty = x1 - 0.40, 6.0
    make_rot_box("Drafting_Board", (tx, ty, 0.74), (0.60, 0.80, 0.03), (0.86, 0.82, 0.70, 1.0), pitch=-0.35)
    make_rot_box("Drafting_Sketch", (tx - 0.006, ty, 0.756), (0.40, 0.56, 0.004), (0.96, 0.96, 0.92, 1.0), pitch=-0.35)
    for s in (-1, 1):
        make_box(f"Drafting_Leg_{s:+d}", (tx, ty + s * 0.36, 0.32), (0.46, 0.04, 0.64), (0.40, 0.30, 0.22, 1.0))
    make_chair("Drafting_Stool", tx - 0.62, ty, yaw=-math.pi / 2.0, wood=(0.40, 0.30, 0.22, 1.0), seat_h=0.40, w=0.32)
    # the supply shelf: liquid latex, make-up tubes, the models and sculptures
    sx, sy = x1 - 0.22, 8.4
    make_box("Supply_Shelf", (sx, sy, 0.60), (0.40, 1.40, 1.20), (0.40, 0.30, 0.22, 1.0))
    make_cyl("Latex_Jar", (sx, sy - 0.50, 1.27), 0.06, 0.14, (0.86, 0.80, 0.70, 1.0), segments=10)
    for k in range(5):
        make_rot_box(f"Makeup_Tube_{k}", (sx - 0.05, sy - 0.30 + k * 0.08, 1.215), (0.12, 0.03, 0.03),
                     ((0.80, 0.30, 0.30, 1.0), (0.86, 0.76, 0.62, 1.0))[k % 2], yaw=0.3)
    for k in range(3):
        make_blob(f"Sculpture_{k}", (sx, sy + 0.20 + k * 0.20, 1.28), 0.08, (0.60, 0.56, 0.50, 1.0), noise=0.3, seed=k, squash=1.0)
    # the closet half packed: boxes in front of it
    for k in range(3):
        make_box(f"Packing_Box_{k}", (closet[0] + 0.3 + k * 0.48, y1 - 0.45, 0.20), (0.44, 0.40, 0.40), (0.62, 0.48, 0.32, 1.0))
    make_box("Packing_Box_Top", (closet[0] + 0.54, y1 - 0.45, 0.60), (0.44, 0.40, 0.40), (0.58, 0.44, 0.30, 1.0))
    make_lamp("Lamp_Nick", x1 - 0.30, y1 - 0.30, base_z=0.0, h=1.40)


def build_street():
    # the lawns round the house, the drive, the walk, the street
    make_box("Front_Lawn_Ground", (0.0, -4.06, -0.01), (80.0, 7.88, 0.02), LAWN)
    make_box("Side_Lawn_Ground_W", (-26.6, 19.94, -0.01), (26.8, 40.12, 0.02), LAWN)
    make_box("Side_Lawn_Ground_E", (23.55, 19.94, -0.01), (32.9, 40.12, 0.02), LAWN)
    make_box("Back_Lawn_Ground", (-3.1, 25.05, -0.01), (20.4, 29.9, 0.02), LAWN)
    make_box("Back_Lawn_Ground_Garage", (-10.15, 8.6, -0.01), (6.3, 3.0, 0.02), LAWN)
    make_box("Driveway", (-10.15, -3.06, 0.005), (4.6, 5.88, 0.01), CONCRETE)
    make_box("Front_Walk", (-1.0, -3.06, 0.005), (1.0, 5.88, 0.01), CONCRETE)
    make_box("Sidewalk", (0.0, -6.8, 0.06), (80.0, 1.6, 0.12), CONCRETE)
    make_box("Street_Asphalt", (0.0, -11.0, -0.01), (80.0, 7.0, 0.02), (0.20, 0.20, 0.22, 1.0))
    make_box("Curb", (0.0, -7.62, 0.06), (80.0, 0.04, 0.12), (0.62, 0.60, 0.56, 1.0))
    # the rusting mini-bike outside
    mx, my = -7.3, -2.2
    for s in (-1, 1):
        make_cyl(f"Minibike_Wheel_{s:+d}", (mx, my + s * 0.45, 0.20), 0.20, 0.10, (0.12, 0.12, 0.12, 1.0), axis='X', segments=12)
    make_box("Minibike_Frame", (mx, my, 0.40), (0.14, 0.90, 0.10), (0.50, 0.26, 0.16, 1.0))
    make_box("Minibike_Seat", (mx, my - 0.10, 0.49), (0.20, 0.40, 0.08), (0.20, 0.16, 0.14, 1.0))
    make_box("Minibike_Stem", (mx, my + 0.45, 0.55), (0.04, 0.04, 0.34), (0.40, 0.30, 0.24, 1.0))
    make_box("Minibike_Bars", (mx, my + 0.45, 0.73), (0.50, 0.04, 0.04), (0.40, 0.30, 0.24, 1.0))
    make_box("Minibike_Engine", (mx, my + 0.05, 0.26), (0.22, 0.30, 0.18), (0.36, 0.30, 0.26, 1.0))
    # the neighbour's fence on the E side, holes shot through it
    make_box("Neighbor_Fence", (8.5, -3.2, 0.9), (0.06, 7.6, 1.8), (0.56, 0.44, 0.30, 1.0))
    for k in range(5):
        make_cyl(f"Fence_Hole_{k}", (8.466, -5.0 + k * 0.7, 0.9 + (k % 2) * 0.3), 0.03, 0.01, (0.06, 0.06, 0.06, 1.0), axis='X', segments=8)
    # the neighbours' houses, their windows lit, a pumpkin on each step
    for k, x in enumerate((-26.0, 18.0)):
        make_box(f"Neighbor_House_{k}", (x, 4.0, 1.5), (12.0, 9.0, 3.0), ((0.70, 0.66, 0.58, 1.0), (0.60, 0.62, 0.66, 1.0))[k])
        make_box(f"Neighbor_Roof_{k}", (x, 4.0, 3.3), (12.6, 9.6, 0.60), ROOF)
        make_box(f"Neighbor_Window_Glow_{k}", (x + 2.0, -0.52, 1.4), (1.4, 0.04, 1.0), (1.0, 0.80, 0.50, 1.0))
        make_blob(f"Pumpkin_{k}", (x - 1.0, -0.9, 0.144), 0.18, (0.90, 0.46, 0.10, 1.0), noise=0.1, seed=k, squash=0.8)
    for k in range(3):
        make_broadleaf(f"Street_Tree_{k}", (-20.0, 12.0, 26.0)[k], -5.4, 6.0, (0.24, 0.30, 0.20, 1.0), (0.34, 0.26, 0.20, 1.0))
    make_cyl("Streetlamp_Post", (4.0, -6.6, 2.72), 0.08, 5.2, (0.30, 0.30, 0.32, 1.0), segments=8)
    make_box("Streetlamp_Head", (4.0, -7.2, 5.3), (0.30, 1.2, 0.14), (0.30, 0.30, 0.32, 1.0))
    # behind the house: the next street's roofs and trees, dark
    make_box("Far_Houses_Band", (0.0, 40.0, 2.5), (120.0, 0.2, 5.0), (0.10, 0.10, 0.12, 1.0))
    for k in range(6):
        make_box(f"Far_Window_Glow_{k}", (-40.0 + k * 16.0, 39.88, 1.6 + (k % 2) * 1.2), (1.2, 0.04, 0.8), (0.86, 0.66, 0.40, 1.0))


def main():
    clear_scene()
    build_shell()
    build_garage_dressing()
    build_garage_2026_10()
    build_grandma_living_2026_10()
    build_nick_room()
    build_street()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/nick_house.glb"))
    print(f"\n[build_nick_house] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
