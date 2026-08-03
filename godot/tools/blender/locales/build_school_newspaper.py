"""The school newspaper room — vol2 ch2 interlude three. A borrowed
classroom that the paper has colonized: desks pushed into one big
layout table, the pinboard of pages, a chalkboard still carrying
last period's math.

Hero features: four student desks butted into a layout island piled
with paste-up pages and a typewriter, the W-wall pinboard with
pinned sheets, the N-wall chalkboard + chalk rail, teacher's desk in
the NE corner with a phone, the E-wall window band pouring in
afternoon light, a paper-stacked side counter, and the wall clock.

Coordinate frame: Blender Z-up. y=0 is the door (south) wall; +Y
runs back to the chalkboard; walls at x=±4.0, back wall y=6.0,
ceiling 2.9. glTF export remaps to Godot (x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  school_newspaper — inside the door looking N: layout island
  center, pinboard left, window light right.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 8.0
ROOM_D = 6.0
CEIL = 2.9

COL_WALL = (0.62, 0.60, 0.52, 1.0)      # institutional cream
COL_BASE = (0.36, 0.34, 0.28, 1.0)
COL_FLOOR = (0.52, 0.48, 0.40, 1.0)     # waxed tile
COL_SEAM = (0.40, 0.36, 0.30, 1.0)
COL_CEIL = (0.68, 0.68, 0.64, 1.0)
COL_DESK_TOP = (0.60, 0.50, 0.36, 1.0)  # laminate
COL_DESK_LEG = (0.36, 0.38, 0.40, 1.0)
COL_PAPER = (0.84, 0.82, 0.74, 1.0)
COL_PAPER_DK = (0.74, 0.72, 0.62, 1.0)
COL_TYPE = (0.28, 0.30, 0.30, 1.0)
COL_BOARD_CORK = (0.52, 0.38, 0.26, 1.0)
COL_BOARD_FR = (0.34, 0.26, 0.18, 1.0)
COL_CHALK = (0.16, 0.24, 0.20, 1.0)     # green board
COL_CHALK_TXT = (0.72, 0.74, 0.70, 1.0)
COL_GLASS = (0.72, 0.76, 0.70, 0.5)     # bright afternoon
COL_FRAME = (0.30, 0.30, 0.32, 1.0)
COL_TDESK = (0.38, 0.28, 0.20, 1.0)
COL_CLOCK = (0.84, 0.82, 0.74, 1.0)
COL_FLUOR = (0.94, 0.96, 0.90, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=True, with_stains=False,
                 palette={"tile": COL_CEIL})
    make_box("Door", (2.8, 0.08, 1.10), (0.95, 0.05, 2.20), COL_BOARD_FR)
    for i, fy in enumerate((1.8, 4.2)):
        make_box(f"Fluor_{i}", (0.0, fy, CEIL - 0.03), (3.0, 0.34, 0.05), COL_FLUOR)


def build_layout_island():
    """Four desks butted together mid-room, paste-up spread on top."""
    for i, (dx, dy) in enumerate(((-0.75, 2.4), (0.75, 2.4), (-0.75, 3.4), (0.75, 3.4))):
        make_box(f"Desk_{i}_Top", (dx, dy, 0.72), (1.45, 0.95, 0.05), COL_DESK_TOP)
        for lx in (dx - 0.62, dx + 0.62):
            for ly in (dy - 0.38, dy + 0.38):
                make_box(f"Desk_{i}_Leg_{lx:.2f}_{ly:.2f}", (lx, ly, 0.36),
                         (0.05, 0.05, 0.72), COL_DESK_LEG)
    # Paste-up pages fanned across the island
    pages = [(-1.1, 2.2, 0.0), (-0.45, 2.55, 0.012), (0.2, 2.3, 0.0),
             (0.9, 2.6, 0.012), (-0.8, 3.3, 0.0), (0.1, 3.5, 0.012),
             (0.95, 3.25, 0.0), (-0.15, 2.95, 0.024)]
    for i, (px, py, dz) in enumerate(pages):
        col = COL_PAPER if i % 3 else COL_PAPER_DK
        make_box(f"Page_{i}", (px, py, 0.75 + dz), (0.34, 0.44, 0.008), col)
    # Katrina's camera, strap pooled beside it on the island
    make_box("Camera_Body", (-1.05, 3.45, 0.80), (0.22, 0.14, 0.13), COL_TYPE)
    make_cyl("Camera_Lens", (-1.05, 3.36, 0.80), 0.05, 0.06, COL_DESK_LEG,
             segments=10, axis='Y')
    make_box("Camera_Strap", (-0.80, 3.50, 0.755), (0.30, 0.20, 0.015), (0.30, 0.22, 0.16, 1.0))
    # The typewriter, corner of the island
    make_box("Type_Body", (1.0, 3.55, 0.83), (0.44, 0.36, 0.16), COL_TYPE)
    make_box("Type_Keys", (1.0, 3.42, 0.78), (0.36, 0.14, 0.05), COL_DESK_LEG)
    make_box("Type_Platen", (1.0, 3.68, 0.94), (0.48, 0.07, 0.06), COL_DESK_LEG)
    make_box("Type_Sheet", (1.0, 3.70, 1.06), (0.28, 0.01, 0.20), COL_PAPER)
    # Chairs pulled up (two visible)
    for i, (cx, cy) in enumerate(((-1.5, 2.9), (1.55, 2.6))):
        make_box(f"Chair_{i}_Seat", (cx, cy, 0.44), (0.4, 0.4, 0.05), COL_DESK_TOP)
        make_box(f"Chair_{i}_Back", (cx + (0.18 if cx > 0 else -0.18), cy, 0.75),
                 (0.05, 0.4, 0.55), COL_DESK_TOP)
        for lx in (cx - 0.16, cx + 0.16):
            for ly in (cy - 0.16, cy + 0.16):
                make_box(f"Chair_{i}_Leg_{lx:.2f}_{ly:.2f}", (lx, ly, 0.22),
                         (0.035, 0.035, 0.44), COL_DESK_LEG)


def build_pinboard():
    """W wall: cork board with pinned page mock-ups."""
    make_box("Board_Frame", (-3.94, 3.0, 1.55), (0.06, 3.2, 1.5), COL_BOARD_FR)
    make_box("Board_Cork", (-3.91, 3.0, 1.55), (0.04, 3.0, 1.3), COL_BOARD_CORK)
    pins = [(2.0, 1.85), (2.6, 1.35), (3.2, 1.9), (3.8, 1.5), (2.3, 1.05), (3.5, 1.1)]
    for i, (py, pz) in enumerate(pins):
        col = COL_PAPER if i % 2 else COL_PAPER_DK
        make_box(f"Pinned_{i}", (-3.88, py, pz), (0.02, 0.30, 0.40), col)
    # Jay Rose's comic strip — DRIFTWOOD — a horizontal four-panel
    # strip pinned along the board's top edge
    make_box("DriftWood_Strip", (-3.87, 2.9, 2.10), (0.02, 1.30, 0.28), COL_PAPER)
    for p in range(4):
        make_box(f"DriftWood_Panel_{p}", (-3.86, 2.42 + p * 0.32, 2.10),
                 (0.015, 0.26, 0.22), COL_PAPER_DK)


def build_chalkboard():
    """N wall: green board + rail; a few chalk line strokes remain."""
    make_box("Chalk_Frame", (-0.8, ROOM_D - 0.06, 1.60), (4.4, 0.06, 1.4), COL_BOARD_FR)
    make_box("Chalk_Board", (-0.8, ROOM_D - 0.09, 1.60), (4.2, 0.04, 1.2), COL_CHALK)
    make_box("Chalk_Rail", (-0.8, ROOM_D - 0.16, 0.96), (4.2, 0.14, 0.04), COL_BOARD_FR)
    for i, (cx, cw, cz) in enumerate(((-2.2, 1.1, 1.85), (-1.6, 0.7, 1.60),
                                      (0.2, 1.4, 1.95), (0.6, 0.9, 1.45))):
        make_box(f"Chalk_Line_{i}", (cx, ROOM_D - 0.105, cz), (cw, 0.01, 0.045),
                 COL_CHALK_TXT)


def build_perimeter():
    """E-wall window band, teacher desk NE, paper counter S, clock."""
    make_box("Win_Frame", (3.94, 3.0, 1.75), (0.06, 4.0, 1.5), COL_FRAME)
    for i, wy in enumerate((1.6, 3.0, 4.4)):
        make_box(f"Win_Glass_{i}", (3.90, wy, 1.75), (0.04, 1.25, 1.30), COL_GLASS)
    make_box("Win_Sill", (3.82, 3.0, 0.98), (0.24, 4.3, 0.06), COL_FRAME)
    # Teacher's desk, NE corner
    make_box("TDesk_Top", (2.9, 5.35, 0.74), (1.5, 0.8, 0.06), COL_TDESK)
    make_box("TDesk_Body", (3.25, 5.35, 0.38), (0.7, 0.75, 0.70), COL_TDESK)
    for lx in (2.22, 3.58):
        make_box(f"TDesk_Leg_{lx:.2f}", (lx, 5.35, 0.36), (0.06, 0.7, 0.72), COL_BOARD_FR)
    make_box("TDesk_Phone", (2.6, 5.5, 0.82), (0.26, 0.20, 0.12), COL_TYPE)
    # Side counter of paper stacks along the S wall, west of the door
    make_box("Counter", (-1.8, 0.35, 0.45), (3.4, 0.55, 0.90), COL_DESK_TOP)
    for i in range(5):
        h = 0.10 + 0.05 * (i % 3)
        make_box(f"Stack_{i}", (-3.1 + i * 0.65, 0.35, 0.90 + h / 2.0),
                 (0.42, 0.34, h), COL_PAPER if i % 2 else COL_PAPER_DK)
    # Wall clock over the chalkboard
    make_cyl("Clock", (1.9, ROOM_D - 0.07, 2.45), 0.18, 0.05, COL_CLOCK,
             segments=14, axis='Y')
    make_box("Clock_Hand_H", (1.86, ROOM_D - 0.11, 2.47), (0.09, 0.015, 0.02),
             COL_TYPE)
    make_box("Clock_Hand_M", (1.9, ROOM_D - 0.11, 2.52), (0.02, 0.015, 0.12),
             COL_TYPE)


def main():
    clear_scene()
    build_shell()
    build_layout_island()
    build_pinboard()
    build_chalkboard()
    build_perimeter()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/school_newspaper.glb"))
    print(f"\n[build_school_newspaper] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
