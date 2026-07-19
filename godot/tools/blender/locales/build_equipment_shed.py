"""Athletics equipment shed — vol6 placement script.

Canon (vol6 ch19 "The Depth Chart"): Coach Dale at the back wall of
the shed, sorting through a small [stack] — the field-side equipment
shed where two decades of practice gear lives. Dusk light through
the open double door.

Hero props: wall shelving with helmets in a row, the blocking sled
frame + pads, two tackle dummies leaning, the field-liner cart with
its chalk hopper, ball bin of footballs, cone stacks, the open
double door with the field's dusk beyond (green strip + goalpost
silhouette), Coach Dale's clipboard wall with the roster sheets.

Coordinate frame: Blender Z-up. y=0 is the OPEN double door (south,
to the field); +Y into the shed. glTF export remaps to Godot
(x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 4.8      # x ∈ [-2.4, 2.4]
ROOM_D = 5.4      # y ∈ [0, 5.4]
CEIL = 2.6

COL_WALL = (0.42, 0.36, 0.28, 1.0)      # bare plywood walls
COL_BASE = (0.30, 0.25, 0.19, 1.0)
COL_FLOOR = (0.40, 0.40, 0.42, 1.0)     # concrete slab
COL_SEAM = (0.32, 0.32, 0.34, 1.0)
COL_SHELF = (0.36, 0.28, 0.18, 1.0)
COL_STEEL = (0.34, 0.35, 0.38, 1.0)
COL_STEEL_DK = (0.18, 0.18, 0.20, 1.0)
COL_HELMET = (0.70, 0.68, 0.64, 1.0)
COL_HELMET_STRIPE = (0.48, 0.14, 0.14, 1.0)
COL_PAD = (0.48, 0.14, 0.14, 1.0)       # wine-red sled/dummy pads
COL_PAD_DK = (0.36, 0.10, 0.10, 1.0)
COL_BALL = (0.45, 0.26, 0.14, 1.0)
COL_CONE = (0.75, 0.38, 0.10, 1.0)
COL_CHALK = (0.85, 0.85, 0.83, 1.0)
COL_LINER = (0.30, 0.38, 0.30, 1.0)
COL_PAPER = (0.82, 0.80, 0.72, 1.0)
COL_DOOR = (0.36, 0.30, 0.22, 1.0)
COL_FIELD = (0.24, 0.34, 0.16, 1.0)     # dusk field beyond the door
COL_GOAL = (0.62, 0.60, 0.30, 1.0)
COL_BULB = (1.00, 0.85, 0.58, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    # Stud lines on the plywood (shed, not drywall)
    for wx, nm in ((-ROOM_W / 2.0 + 0.08, "W"), (ROOM_W / 2.0 - 0.08, "E")):
        for i in range(4):
            make_box(f"Stud_{nm}_{i}", (wx, 0.9 + i * 1.2, CEIL / 2.0),
                     (0.06, 0.10, CEIL - 0.1), COL_BASE)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # South: header + the two door leaves swung OPEN outward
    make_box("Door_Header", (0.0, 0.0, CEIL - 0.18), (ROOM_W + 0.4, 0.2, 0.36), COL_WALL)
    for sgn in (-1, 1):
        make_box(f"Door_Jamb_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.12), 0.0, CEIL / 2.0),
                 (0.24, 0.2, CEIL), COL_WALL)
        # leaves swung out ~120°, standing proud of the front wall
        make_box(f"Door_Leaf_{sgn:+d}", (sgn * (ROOM_W / 2.0 - 0.55), -0.55, 1.1),
                 (0.9, 0.07, 2.2), COL_DOOR)
    # The field beyond: dusk grass apron + a goalpost silhouette
    make_box("Field", (0.0, -3.6, -0.02), (ROOM_W + 8.0, 6.4, 0.04), COL_FIELD)
    make_cyl("Goal_Post", (1.8, -5.4, 1.5), 0.06, 3.0, COL_GOAL, segments=8)
    make_cyl("Goal_Crossbar", (1.8, -5.4, 2.6), 0.05, 2.6, COL_GOAL, segments=8, axis='X')
    for sgn in (-1, 1):
        make_cyl(f"Goal_Upright_{sgn:+d}", (1.8 + sgn * 1.3, -5.4, 3.4), 0.045, 1.7,
                 COL_GOAL, segments=8)
    # Bare bulb over the back wall (Coach Dale's work light)
    make_cyl("Bulb_Base", (0.0, 4.6, CEIL - 0.05), 0.05, 0.05, COL_STEEL_DK, segments=8)
    make_cyl("Bulb", (0.0, 4.6, CEIL - 0.13), 0.045, 0.09, COL_BULB, segments=10)


def build_shelving():
    """Helmet shelf + ball bin along the WEST wall; cones; clipboard
    wall on the back (Coach Dale's sorting spot)."""
    wx = -ROOM_W / 2.0 + 0.30
    for si, sz in enumerate((0.55, 1.15, 1.75)):
        make_box(f"Shelf_{si}", (wx, 2.8, sz), (0.5, 3.4, 0.05), COL_SHELF)
    # Helmets in a row on the top shelf
    for i in range(5):
        hy = 1.35 + i * 0.62
        make_cyl(f"Helmet_{i}", (wx, hy, 1.94), 0.14, 0.22, COL_HELMET, segments=12)
        make_box(f"Helmet_{i}_Stripe", (wx, hy, 2.06), (0.28, 0.04, 0.03), COL_HELMET_STRIPE)
    # Shoulder-pad stacks on the middle shelf
    for i in range(3):
        make_box(f"Pads_{i}", (wx, 1.6 + i * 0.9, 1.28), (0.42, 0.6, 0.20), COL_HELMET)
    # Ball bin on the floor — a crate of footballs
    make_box("Ball_Bin", (wx + 0.15, 0.85, 0.25), (0.6, 0.6, 0.5), COL_STEEL_DK,
             open_faces={"+Z"})
    for i in range(4):
        make_cyl(f"Ball_{i}", (wx + 0.02 + 0.14 * (i % 2), 0.72 + 0.16 * (i // 2), 0.52),
                 0.09, 0.24, COL_BALL, segments=8, axis='Y')
    # Cone stacks by the door
    for ci in range(2):
        for k in range(4):
            make_cyl(f"Cone_{ci}_{k}", (2.0 - ci * 0.5, 0.6, 0.10 + k * 0.09),
                     0.16 - k * 0.012, 0.16, COL_CONE, segments=8)
    # THE CLIPBOARD WALL — back wall, where Coach Dale sorts: roster
    # sheets on nails, one clipboard hanging, a small stack on a stool
    nx = ROOM_D - 0.05
    for pi in range(4):
        make_box(f"Roster_{pi}", (-1.5 + pi * 0.55, nx, 1.65 + 0.05 * (pi % 2)),
                 (0.30, 0.02, 0.40), COL_PAPER)
    make_box("Clipboard", (0.9, nx, 1.6), (0.28, 0.03, 0.38), COL_SHELF)
    make_box("Clipboard_Clip", (0.9, nx - 0.02, 1.76), (0.12, 0.02, 0.05), COL_STEEL)
    make_box("Sort_Stool", (0.0, ROOM_D - 0.55, 0.30), (0.35, 0.35, 0.06), COL_SHELF)
    for sx, sy in ((-0.13, -0.13), (0.13, -0.13), (-0.13, 0.13), (0.13, 0.13)):
        make_box(f"Stool_Leg_{sx:+.2f}_{sy:+.2f}", (sx, ROOM_D - 0.55 + sy, 0.14),
                 (0.04, 0.04, 0.28), COL_BASE)
    make_box("Sort_Stack", (0.0, ROOM_D - 0.55, 0.38), (0.26, 0.20, 0.10), COL_PAPER)


def build_big_gear():
    """The blocking sled + two tackle dummies + the field liner."""
    # Blocking sled — steel skid frame with two upright pads
    sx, sy = 1.5, 3.6
    make_box("Sled_Skid_L", (sx - 0.45, sy, 0.10), (0.10, 1.3, 0.12), COL_STEEL_DK)
    make_box("Sled_Skid_R", (sx + 0.45, sy, 0.10), (0.10, 1.3, 0.12), COL_STEEL_DK)
    make_box("Sled_Cross", (sx, sy, 0.16), (1.0, 0.10, 0.10), COL_STEEL)
    for di, dy in enumerate((-0.35, 0.35)):
        make_box(f"Sled_Arm_{di}", (sx, sy + dy, 0.62), (0.08, 0.08, 1.0), COL_STEEL)
        make_box(f"Sled_Pad_{di}", (sx, sy + dy, 1.15), (0.34, 0.22, 0.6), COL_PAD)
    # Tackle dummies leaning in the NE corner
    for di, (dx, tilt_dy) in enumerate([(2.0, 4.9), (1.6, 5.05)]):
        make_cyl(f"Dummy_{di}", (dx, tilt_dy, 0.75), 0.17, 1.5,
                 COL_PAD if di == 0 else COL_PAD_DK, segments=10)
        make_cyl(f"Dummy_{di}_Cap", (dx, tilt_dy, 1.52), 0.17, 0.05, COL_PAD_DK, segments=10)
    # Field liner cart with chalk hopper
    lx, ly = -1.5, 4.5
    make_box("Liner_Hopper", (lx, ly, 0.45), (0.4, 0.5, 0.4), COL_LINER)
    make_box("Liner_Chalk", (lx, ly, 0.66), (0.32, 0.42, 0.03), COL_CHALK)
    make_box("Liner_Handle", (lx, ly + 0.5, 0.75), (0.05, 0.5, 0.05), COL_STEEL)
    make_box("Liner_Grip", (lx, ly + 0.75, 0.98), (0.30, 0.04, 0.04), COL_STEEL_DK)
    for wy in (-0.2, 0.25):
        make_cyl(f"Liner_Wheel_{wy:+.1f}", (lx, ly + wy, 0.12), 0.12, 0.05,
                 COL_STEEL_DK, segments=12, axis='X')
    # Chalk dust ghost on the slab under the liner
    make_box("Chalk_Dust", (lx, ly - 0.4, 0.005), (0.5, 0.4, 0.006), COL_CHALK)


def main():
    clear_scene()
    build_shell()
    build_shelving()
    build_big_gear()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/equipment_shed.glb"))
    print(f"\n[build_equipment_shed] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
