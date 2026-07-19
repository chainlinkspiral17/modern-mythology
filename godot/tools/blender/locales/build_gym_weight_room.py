"""Harmony Creek HS weight room — vol6 placement script.

Canon (vol6 ch13 "Two-a-Days"): "The weight room is in the basement
of the gym building." August two-a-days — a low basement room, block
walls, fluorescent tubes, decades of iron. This is Ben's second home.

Hero props: the squat rack with a loaded barbell, two flat benches
with bars racked, the dumbbell rack (paired rows), plate trees,
the wall mirror panel, the DEPTH CHART + record board on the wall,
a box fan in the corner (basement in August), chalk bucket, the
stairs down from the door (it is a basement).

Coordinate frame: Blender Z-up. y=0 south wall (stairs/door), +Y
north, walls x=±ROOM_W/2. glTF export remaps to Godot (x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 7.5      # x ∈ [-3.75, 3.75]
ROOM_D = 6.5      # y ∈ [0, 6.5]
CEIL = 2.5        # low basement ceiling

COL_WALL = (0.55, 0.55, 0.50, 1.0)      # painted block
COL_BASE = (0.38, 0.38, 0.34, 1.0)
COL_FLOOR = (0.22, 0.22, 0.24, 1.0)     # black rubber mat
COL_SEAM = (0.16, 0.16, 0.18, 1.0)
COL_RACK = (0.28, 0.30, 0.44, 1.0)      # school-blue steel
COL_IRON = (0.20, 0.20, 0.22, 1.0)
COL_PLATE = (0.14, 0.14, 0.15, 1.0)
COL_PLATE_RIM = (0.45, 0.45, 0.48, 1.0)
COL_BENCH_PAD = (0.48, 0.14, 0.14, 1.0) # wine-red vinyl pads
COL_MIRROR = (0.60, 0.66, 0.70, 1.0)
COL_PAPER = (0.82, 0.80, 0.72, 1.0)
COL_BOARD = (0.16, 0.22, 0.16, 1.0)     # record board green
COL_CHALK = (0.85, 0.85, 0.83, 1.0)
COL_TUBE = (0.92, 0.96, 0.94, 1.0)
COL_FIXTURE = (0.58, 0.58, 0.56, 1.0)
COL_STEP = (0.42, 0.42, 0.40, 1.0)
COL_FAN = (0.30, 0.32, 0.34, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    # South wall split around the stairwell opening (east side)
    make_wall("Wall_S_W", (-1.5, 0.0, 0), length=ROOM_W - 3.0, height=CEIL,
              axis='X', palette=pal)
    make_box("Wall_S_Above", (2.6, 0.0, CEIL - 0.30), (2.3, 0.2, 0.60), COL_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=True)
    # Basement stairs coming down along the east wall from the door
    for s in range(5):
        make_box(f"Stair_{s}", (2.6, 0.25 + s * 0.30, 1.05 - s * 0.21),
                 (1.6, 0.32, 0.10), COL_STEP)
    make_box("Stair_Rail", (1.85, 0.9, 1.15), (0.06, 1.6, 0.06), COL_RACK)
    # Exposed ceiling pipe run (basement)
    make_cyl("Pipe", (-1.2, ROOM_D / 2.0, CEIL - 0.12), 0.07, ROOM_D, COL_FIXTURE,
             segments=8, axis='Y')


def build_squat_rack():
    """Hero: the squat rack against the north wall, bar loaded."""
    rx, ry = -1.8, ROOM_D - 0.7
    for dx in (-0.6, 0.6):
        for dy in (-0.35, 0.35):
            make_box(f"Rack_Post_{dx:+.1f}_{dy:+.1f}", (rx + dx, ry + dy, 1.1),
                     (0.09, 0.09, 2.2), COL_RACK)
    for dx in (-0.6, 0.6):
        make_box(f"Rack_Top_{dx:+.1f}", (rx + dx, ry, 2.2), (0.09, 0.8, 0.08), COL_RACK)
        # J-hooks
        make_box(f"Rack_Hook_{dx:+.1f}", (rx + dx, ry - 0.42, 1.45), (0.10, 0.12, 0.08), COL_IRON)
    # The bar, racked, loaded with plates
    make_cyl("Squat_Bar", (rx, ry - 0.45, 1.52), 0.025, 2.2, COL_IRON, segments=8, axis='X')
    for sgn in (-1, 1):
        for pi, pr in enumerate((0.22, 0.22, 0.16)):
            make_cyl(f"Squat_Plate_{sgn:+d}_{pi}", (rx + sgn * (0.85 + pi * 0.06),
                     ry - 0.45, 1.52), pr, 0.05, COL_PLATE, segments=14, axis='X')
    # Chalk bucket at its foot
    make_cyl("Chalk_Bucket", (rx + 1.0, ry - 0.7, 0.22), 0.16, 0.42, COL_FAN, segments=10)
    make_cyl("Chalk", (rx + 1.0, ry - 0.7, 0.44), 0.13, 0.02, COL_CHALK, segments=10)


def build_benches():
    """Two flat benches mid-floor, bars racked on uprights."""
    for bi, (bx, by) in enumerate([(1.4, 4.6), (1.4, 2.9)]):
        make_box(f"Bench_{bi}_Pad", (bx, by, 0.45), (0.32, 1.25, 0.09), COL_BENCH_PAD)
        make_box(f"Bench_{bi}_Spine", (bx, by, 0.28), (0.14, 1.1, 0.26), COL_IRON)
        for dy in (-0.5, 0.5):
            make_box(f"Bench_{bi}_Foot_{dy:+.1f}", (bx, by + dy, 0.06), (0.5, 0.08, 0.10),
                     COL_IRON)
        # Uprights at the head (north end) + racked bar
        for dx in (-0.42, 0.42):
            make_box(f"Bench_{bi}_Up_{dx:+.1f}", (bx + dx, by + 0.45, 0.62),
                     (0.07, 0.07, 1.15), COL_RACK)
        make_cyl(f"Bench_{bi}_Bar", (bx, by + 0.45, 1.18), 0.022, 1.9, COL_IRON,
                 segments=8, axis='X')
        for sgn in (-1, 1):
            make_cyl(f"Bench_{bi}_Plate_{sgn:+d}", (bx + sgn * 0.75, by + 0.45, 1.18),
                     0.18, 0.05, COL_PLATE, segments=12, axis='X')


def build_dumbbells_and_plates():
    """Dumbbell rack along the WEST wall under the mirror; two plate
    trees; the wall mirror panel."""
    dx = -ROOM_W / 2.0 + 0.45
    # Two-tier rack
    for tier, tz in ((0, 0.35), (1, 0.75)):
        make_box(f"DB_Shelf_{tier}", (dx, 2.4, tz), (0.5, 2.4, 0.06), COL_RACK)
        for i in range(6):
            dy = 1.45 + i * 0.4
            r = 0.055 + 0.012 * ((i + tier * 3) % 4)
            make_cyl(f"DB_{tier}_{i}_L", (dx - 0.12, dy, tz + 0.09), r, 0.07,
                     COL_IRON, segments=10, axis='X')
            make_cyl(f"DB_{tier}_{i}_R", (dx + 0.12, dy, tz + 0.09), r, 0.07,
                     COL_IRON, segments=10, axis='X')
            make_cyl(f"DB_{tier}_{i}_Bar", (dx, dy, tz + 0.09), 0.018, 0.26,
                     COL_PLATE_RIM, segments=6, axis='X')
    # Mirror panel above the rack
    make_box("Mirror", (-ROOM_W / 2.0 + 0.05, 2.4, 1.7), (0.02, 2.6, 1.1), COL_MIRROR)
    make_box("Mirror_Frame_T", (-ROOM_W / 2.0 + 0.06, 2.4, 2.27), (0.03, 2.65, 0.05), COL_IRON)
    make_box("Mirror_Frame_B", (-ROOM_W / 2.0 + 0.06, 2.4, 1.13), (0.03, 2.65, 0.05), COL_IRON)
    # Plate trees
    for ti, (tx, ty) in enumerate([(-3.0, 5.6), (0.2, 5.9)]):
        make_cyl(f"Tree_{ti}_Post", (tx, ty, 0.55), 0.045, 1.1, COL_RACK, segments=8)
        make_box(f"Tree_{ti}_Base", (tx, ty, 0.03), (0.55, 0.55, 0.05), COL_IRON)
        for ai, az in enumerate((0.35, 0.7, 1.0)):
            make_cyl(f"Tree_{ti}_Arm_{ai}", (tx + 0.14, ty, az), 0.025, 0.26,
                     COL_RACK, segments=6, axis='X')
            make_cyl(f"Tree_{ti}_Pl_{ai}", (tx + 0.22, ty, az), 0.16 + 0.04 * (2 - ai),
                     0.05, COL_PLATE, segments=12, axis='X')


def build_wall_dressing():
    """Depth chart + record board on the EAST wall; the box fan; a
    water cooler; motivational sign."""
    ex = ROOM_W / 2.0 - 0.04
    # THE DEPTH CHART (ch13/ch19 object of dread) — big, gridded
    make_box("DepthChart", (ex, 3.4, 1.6), (0.02, 0.9, 1.0), COL_PAPER)
    for r in range(8):
        make_box(f"DepthChart_Row_{r}", (ex - 0.006, 3.4, 1.98 - r * 0.11),
                 (0.005, 0.78, 0.03), (0.35, 0.35, 0.38, 1.0))
    make_box("DepthChart_Head", (ex - 0.006, 3.4, 2.04), (0.006, 0.8, 0.06),
             (0.48, 0.14, 0.14, 1.0))
    # Record board — green with gold lines
    make_box("RecordBoard", (ex, 4.9, 1.6), (0.02, 1.1, 0.9), COL_BOARD)
    for r in range(6):
        make_box(f"Record_Line_{r}", (ex - 0.006, 4.9, 1.9 - r * 0.11),
                 (0.005, 0.95, 0.025), (0.72, 0.60, 0.24, 1.0))
    # Box fan in the SW corner on a milk crate (basement, August)
    make_box("Fan_Crate", (-3.3, 0.6, 0.17), (0.34, 0.34, 0.34), (0.60, 0.28, 0.12, 1.0))
    make_box("BoxFan", (-3.3, 0.6, 0.62), (0.16, 0.55, 0.55), COL_FAN)
    make_cyl("BoxFan_Grille", (-3.21, 0.6, 0.62), 0.24, 0.02, COL_FIXTURE,
             segments=14, axis='X')
    # Water cooler by the stairs
    make_box("Cooler_Body", (1.4, 0.45, 0.55), (0.4, 0.4, 1.1), COL_FIXTURE)
    make_cyl("Cooler_Jug", (1.4, 0.45, 1.28), 0.16, 0.36, (0.45, 0.60, 0.70, 0.7), segments=10)


def build_fluorescents():
    for fx in (-1.8, 1.4):
        for fy in (1.8, 4.4):
            make_box(f"Fix_{fx:+.1f}_{fy:.1f}", (fx, fy, CEIL - 0.08),
                     (0.30, 1.25, 0.06), COL_FIXTURE)
            for dx in (-0.07, 0.07):
                make_cyl(f"Tube_{fx:+.1f}_{fy:.1f}_{dx:+.2f}", (fx + dx, fy, CEIL - 0.13),
                         0.02, 1.2, COL_TUBE, segments=8, axis='Y')


def main():
    clear_scene()
    build_shell()
    build_squat_rack()
    build_benches()
    build_dumbbells_and_plates()
    build_wall_dressing()
    build_fluorescents()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/gym_weight_room.glb"))
    print(f"\n[build_gym_weight_room] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
