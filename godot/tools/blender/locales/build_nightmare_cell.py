"""Diego's nightmare cell — vol6 placement script.

Canon (vol6 ch9 "Diego's Nightmare"): a chapter "not in its
narrator's full possession of itself" — Diego between a concussion
and the long dark. "The room has no windows. The room has one
fluorescent overhead, set behind a wire cage. The cage is, he
thinks, less to protect the bulb than to protect the room from him.
The bulb hums" — the same hum as the Gas & Go stockroom bulb, the
hum that started the red dots.

Deliberately SPARSE and wrong: a too-empty concrete room, one caged
tube, a steel door with no handle on the inside, a cot, a floor
drain dead-center, and a field of small red dots on one wall that
resolves out of the concrete the longer you look. Dream logic: the
proportions are slightly tall, the door slightly too small.

Coordinate frame: Blender Z-up. y=0 south wall (the door), +Y north,
walls x=±ROOM_W/2. glTF export remaps to Godot (x, z, -y).
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 3.4      # x ∈ [-1.7, 1.7]
ROOM_D = 4.2      # y ∈ [0, 4.2]
CEIL = 3.4        # too tall for the footprint — dream proportion

COL_WALL = (0.34, 0.35, 0.33, 1.0)      # raw concrete
COL_WALL_STAIN = (0.28, 0.29, 0.27, 1.0)
COL_BASE = (0.24, 0.25, 0.23, 1.0)
COL_FLOOR = (0.30, 0.30, 0.31, 1.0)
COL_SEAM = (0.22, 0.22, 0.23, 1.0)
COL_STEEL = (0.30, 0.31, 0.34, 1.0)
COL_STEEL_DK = (0.16, 0.16, 0.18, 1.0)
COL_DOOR = (0.36, 0.37, 0.40, 1.0)
COL_TUBE = (0.90, 0.96, 0.88, 1.0)      # the humming bulb — blooms
COL_CAGE = (0.20, 0.20, 0.22, 1.0)
COL_COT_FRAME = (0.26, 0.28, 0.30, 1.0)
COL_COT = (0.42, 0.44, 0.40, 1.0)       # institutional canvas
COL_BLANKET = (0.30, 0.33, 0.30, 1.0)
COL_DRAIN = (0.14, 0.14, 0.15, 1.0)
COL_DOT = (0.62, 0.10, 0.08, 1.0)       # the red dots


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=True)
    # Water stain columns down two walls — the concrete has history
    make_box("Stain_W", (-ROOM_W / 2.0 + 0.09, 1.4, 2.2), (0.02, 0.5, 2.2), COL_WALL_STAIN)
    make_box("Stain_N", (0.8, ROOM_D - 0.09, 1.9), (0.7, 0.02, 2.6), COL_WALL_STAIN)
    # Floor drain, dead-center, with a subtle slab slope ring
    make_cyl("Drain_Ring", (0.0, ROOM_D / 2.0, 0.004), 0.35, 0.006, COL_SEAM, segments=16)
    make_cyl("Drain", (0.0, ROOM_D / 2.0, 0.008), 0.12, 0.012, COL_DRAIN, segments=12)
    for k in range(3):
        make_box(f"Drain_Slot_{k}", (0.0, ROOM_D / 2.0 - 0.06 + k * 0.06, 0.016),
                 (0.16, 0.015, 0.004), COL_STEEL_DK)


def build_door():
    """Steel door in the south wall — slightly too small, NO inside
    handle. A viewing slit, closed."""
    make_box("Door", (0.35, 0.06, 0.92), (0.80, 0.10, 1.84), COL_DOOR)
    make_box("Door_Frame_T", (0.35, 0.06, 1.88), (0.94, 0.12, 0.10), COL_STEEL_DK)
    for sgn in (-1, 1):
        make_box(f"Door_Frame_{sgn:+d}", (0.35 + sgn * 0.44, 0.06, 0.94),
                 (0.08, 0.12, 1.92), COL_STEEL_DK)
    for hz in (0.5, 1.35):
        make_box(f"Door_Hinge_{hz:.1f}", (-0.06, 0.10, hz), (0.05, 0.06, 0.16), COL_STEEL)
    # The slit — a closed steel flap where a handle should be
    make_box("Door_Slit", (0.35, 0.115, 1.35), (0.34, 0.015, 0.09), COL_STEEL_DK)
    make_box("Door_Slit_Frame", (0.35, 0.11, 1.35), (0.40, 0.012, 0.13), COL_STEEL)
    # No handle. A smooth plate where one would be.
    make_box("Door_Plate", (0.62, 0.115, 0.95), (0.12, 0.012, 0.20), COL_DOOR)


def build_light():
    """THE fluorescent — one twin-tube fixture dead-center behind a
    wire cage. The only light. The tscn Omni sits under it."""
    make_box("Fix", (0.0, ROOM_D / 2.0, CEIL - 0.09), (0.30, 1.25, 0.07), COL_STEEL)
    for dx in (-0.07, 0.07):
        make_cyl(f"Tube_{dx:+.2f}", (dx, ROOM_D / 2.0, CEIL - 0.145), 0.022, 1.2,
                 COL_TUBE, segments=8, axis='Y')
    # The wire cage — bar lattice boxing the fixture
    cz = CEIL - 0.24
    for i in range(5):
        cy = ROOM_D / 2.0 - 0.62 + i * 0.31
        make_box(f"Cage_Rib_{i}", (0.0, cy, cz), (0.44, 0.015, 0.015), COL_CAGE)
    for sgn in (-1, 1):
        make_box(f"Cage_Rail_{sgn:+d}", (sgn * 0.21, ROOM_D / 2.0, cz),
                 (0.015, 1.28, 0.015), COL_CAGE)
        for i in range(4):
            cy = ROOM_D / 2.0 - 0.5 + i * 0.33
            make_box(f"Cage_Drop_{sgn:+d}_{i}", (sgn * 0.21, cy, CEIL - 0.165),
                     (0.012, 0.012, 0.13), COL_CAGE)


def build_cot():
    """Institutional cot against the east wall. Blanket folded with
    unnatural neatness — he did not sleep."""
    cx = ROOM_W / 2.0 - 0.48
    cy = 3.0
    make_box("Cot_Frame", (cx, cy, 0.28), (0.75, 1.9, 0.07), COL_COT_FRAME)
    for dy in (-0.85, 0.85):
        for dx in (-0.32, 0.32):
            make_cyl(f"Cot_Leg_{dx:+.1f}_{dy:+.1f}", (cx + dx, cy + dy, 0.14),
                     0.02, 0.28, COL_STEEL_DK, segments=6)
    make_box("Cot_Canvas", (cx, cy, 0.335), (0.72, 1.85, 0.04), COL_COT)
    make_box("Cot_Blanket", (cx, cy - 0.55, 0.37), (0.70, 0.55, 0.05), COL_BLANKET)
    make_box("Cot_Pillow", (cx, cy + 0.78, 0.37), (0.55, 0.30, 0.06), (0.55, 0.56, 0.52, 1.0))


def build_red_dots():
    """The field of red dots on the WEST wall — sparse at the edges,
    denser toward a center the eye keeps returning to. Deterministic
    spiral scatter, no RNG."""
    wx = -ROOM_W / 2.0 + 0.095
    cy, cz = 2.4, 1.5
    for i in range(46):
        a = i * 2.39996            # golden angle — organic scatter
        r = 0.085 * math.sqrt(i)
        dy = cy + r * math.cos(a)
        dz = cz + r * 0.72 * math.sin(a)
        if dz < 0.35 or dz > 2.9 or dy < 0.5 or dy > ROOM_D - 0.4:
            continue
        s = 0.014 + 0.006 * ((i * 7) % 3)
        make_box(f"Dot_{i}", (wx, dy, dz), (0.006, s, s), COL_DOT)


def main():
    clear_scene()
    build_shell()
    build_door()
    build_light()
    build_cot()
    build_red_dots()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/nightmare_cell.glb"))
    print(f"\n[build_nightmare_cell] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
