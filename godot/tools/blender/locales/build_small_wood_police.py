"""small_wood_police — the interview room at the Small Wood police station
(draft 1, 2026-10-29).

Vol 2 ch9 ("Truck"), "In town": Julie, after the truck, across a table from a
detective. It was played on the County Line gas station (a reuse: "a police
interview room"). The text:
  "My name is James, he said to me, when we were sitting and everything was
   ready. You can just address me as James."
  "he poured coffee for himself and the other men in the room. He pulled his
   pin from the clip on his notebook and tapped the butt, clicking it ready."
  "I put my head on my arms covering up my eyes."
  "Look Julie, we found the truck, he said. There was blood everywhere."
So: a table they sit at, a coffee pot he pours from, a notebook with a pen on
its clip, and OTHER MEN in the room (standing — the chairs are James's and
Julie's). Small Wood in the late 1990s: a coastal Oregon town's station, not
a city precinct.

  interview room   x 0..4.6, y 0..4.0, ceiling 2.7 — painted block, a drop
                   ceiling with two fluorescent troffers, the steel table, the
                   coffee cart, the observation mirror on the west wall, the
                   door with its wire-glass light onto the squad room.
  squad room       x 4.6..15, y -3..8 — desks with beige CRTs and desk
                   phones, filing cabinets, the corkboard, the front windows
                   onto a wet street; seen through the door and as the far
                   field of the establish.

PROPOSED (not in the text): the mirror, the squad room's fittings, the
street outside. Nothing here is a fact about the station beyond the room.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the observation room behind the mirror; rain on the front
windows; Deck framing of the two closeups across the table.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window, make_blinds
from _props.furniture import make_chair, make_table
from _props.figures import make_standing_figure
from _props.safety import make_fluorescent_tube_fixture

BLOCK = {"wall": (0.74, 0.78, 0.70, 1.0), "baseboard": (0.30, 0.30, 0.28, 1.0)}   # painted block, institutional green
SQUAD = {"wall": (0.80, 0.78, 0.70, 1.0), "baseboard": (0.36, 0.30, 0.24, 1.0)}
STEEL = (0.56, 0.58, 0.60, 1.0)
H = 2.7


def build_interview():
    x0, x1, y0, y1 = 0.0, 4.6, 0.0, 4.0
    make_floor("Interview_Floor", ((x0 + x1) / 2, (y0 + y1) / 2, 0.0), size_x=x1 - x0, size_y=y1 - y0,
               palette={"vinyl": (0.56, 0.58, 0.52, 1.0), "seam": (0.48, 0.50, 0.46, 1.0)})
    # the drop ceiling: grid tiles and two troffers
    make_box("Interview_Ceiling", ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.02), (x1 - x0 + 0.3, y1 - y0 + 0.3, 0.04), (0.88, 0.88, 0.84, 1.0))
    for k in range(1, 4):
        make_box(f"Interview_Ceiling_Grid_X_{k}", (x0 + k * (x1 - x0) / 4, (y0 + y1) / 2, H - 0.004), (0.02, y1 - y0, 0.01), (0.70, 0.70, 0.66, 1.0))
    for k in range(1, 4):
        make_box(f"Interview_Ceiling_Grid_Y_{k}", ((x0 + x1) / 2, y0 + k * (y1 - y0) / 4, H - 0.004), (x1 - x0, 0.02, 0.01), (0.70, 0.70, 0.66, 1.0))
    for k, fy in enumerate((1.4, 2.8)):
        make_fluorescent_tube_fixture(f"Interview_Troffer_{k}", (2.3, fy, H), length=1.2, width=0.6)
    # walls: the observation mirror in the west wall, the door in the east
    make_wall_with_openings("Interview_Wall_W", (x0, (y0 + y1) / 2, 0.0), length=y1 - y0 + 0.16, height=H, thickness=0.16, axis='Y',
                            palette=BLOCK, baseboard_face_sign=+1, openings=[(2.0, 1.45, 1.8, 0.9)])
    make_box("Observation_Mirror", (x0 + 0.03, 2.0, 1.45), (0.02, 1.8, 0.9), (0.20, 0.22, 0.24, 1.0))
    make_box("Observation_Mirror_Frame_T", (x0 + 0.05, 2.0, 1.92), (0.04, 1.9, 0.05), STEEL)
    make_box("Observation_Mirror_Frame_B", (x0 + 0.05, 2.0, 0.98), (0.04, 1.9, 0.05), STEEL)
    make_box("Observation_Room_Dark", (x0 - 1.4, 2.0, 1.3), (2.6, 3.6, 2.6), (0.05, 0.05, 0.06, 1.0))
    make_wall("Interview_Wall_N", ((x0 + x1) / 2, y1, 0.0), length=x1 - x0 + 0.16, height=H, thickness=0.16, axis='X', palette=BLOCK, baseboard_face_sign=-1)
    make_wall("Interview_Wall_S", ((x0 + x1) / 2, y0, 0.0), length=x1 - x0 + 0.16, height=H, thickness=0.16, axis='X', palette=BLOCK, baseboard_face_sign=+1)
    make_wall_with_openings("Interview_Wall_E", (x1, (y0 + y1) / 2, 0.0), length=y1 - y0 + 0.16, height=H, thickness=0.16, axis='Y',
                            palette=BLOCK, baseboard_face_sign=-1, openings=[(3.1, 1.02, 0.92, 2.04)])
    # the door, standing open into the room a hand's width, its wire-glass light
    make_box("Interview_Door", (x1 - 0.06, 3.1, 1.02), (0.05, 0.88, 2.04), (0.46, 0.40, 0.32, 1.0))
    make_box("Interview_Door_Light", (x1 - 0.09, 3.1, 1.48), (0.01, 0.30, 0.44), (0.62, 0.70, 0.72, 1.0))
    for k in range(4):
        make_box(f"Interview_Door_Wire_{k}", (x1 - 0.095, 2.98 + k * 0.08, 1.48), (0.004, 0.006, 0.44), (0.30, 0.30, 0.30, 1.0))
    make_box("Interview_Door_Lever", (x1 - 0.11, 2.75, 1.0), (0.04, 0.14, 0.03), STEEL)
    make_box("Interview_Wall_Clock_Face", (x1 - 0.09, 1.0, 2.15), (0.02, 0.30, 0.30), (0.94, 0.94, 0.90, 1.0))
    make_box("Interview_Wall_Clock_Hands", (x1 - 0.105, 1.0, 2.17), (0.004, 0.02, 0.12), (0.10, 0.10, 0.10, 1.0))
    make_box("Interview_Thermostat", (x1 - 0.09, 1.6, 1.45), (0.03, 0.10, 0.14), (0.86, 0.84, 0.78, 1.0))
    # the steel table, bolted, and the two chairs across it: Julie's (west,
    # her back to the mirror) and James's (east, his back to the door)
    tx, ty = 2.2, 2.0
    make_box("Interview_Table_Top", (tx, ty, 0.74), (1.5, 0.9, 0.04), STEEL)
    for sx in (-0.68, 0.68):
        for sy in (-0.38, 0.38):
            make_box(f"Interview_Table_Leg_{sx:+.2f}_{sy:+.2f}", (tx + sx, ty + sy, 0.36), (0.05, 0.05, 0.72), (0.40, 0.42, 0.44, 1.0))
    make_box("Interview_Table_Ring", (tx - 0.68, ty, 0.62), (0.06, 0.12, 0.06), STEEL)   # the bolted ring
    make_chair("Julie_Chair", tx - 0.95, ty, yaw=-math.pi / 2, wood=(0.36, 0.38, 0.40, 1.0), seat_col=(0.28, 0.30, 0.34, 1.0))
    make_chair("James_Chair", tx + 0.95, ty, yaw=math.pi / 2, wood=(0.36, 0.38, 0.40, 1.0), seat_col=(0.28, 0.30, 0.34, 1.0))
    # on the table: James's notebook with the pen on its clip, the folder,
    # the styrofoam cups he poured, the coffee pot set down at his end
    # (it stood mid-table, square in both closeups)
    top = 0.76
    make_box("Interview_Notebook", (tx + 0.42, ty - 0.10, top + 0.006), (0.16, 0.24, 0.012), (0.92, 0.90, 0.80, 1.0))
    make_box("Interview_Notebook_Coil", (tx + 0.42, ty + 0.02, top + 0.016), (0.16, 0.012, 0.012), (0.70, 0.70, 0.72, 1.0))
    make_cyl("Interview_Notebook_Pen", (tx + 0.50, ty - 0.10, top + 0.020), 0.005, 0.14, (0.10, 0.12, 0.30, 1.0), axis='Y', segments=6)
    make_box("Interview_Case_Folder", (tx + 0.20, ty + 0.26, top + 0.006), (0.24, 0.32, 0.01), (0.86, 0.76, 0.52, 1.0))
    for k, (cx, cy) in enumerate(((tx + 0.40, ty + 0.30), (tx - 0.40, ty - 0.20), (tx + 0.05, ty - 0.32))):
        make_lathe(f"Interview_Coffee_Cup_{k}", (cx, cy, top), [(0.0, 0.0), (0.032, 0.0), (0.040, 0.10), (0.0, 0.10)], (0.96, 0.96, 0.94, 1.0), segments=10)
        make_cyl(f"Interview_Coffee_Cup_{k}_Coffee", (cx, cy, top + 0.092), 0.036, 0.004, (0.24, 0.14, 0.08, 1.0), segments=10)
    make_lathe("Interview_Coffee_Pot", (tx + 0.62, ty + 0.30, top), [(0.0, 0.0), (0.075, 0.0), (0.085, 0.08), (0.06, 0.16), (0.05, 0.19), (0.0, 0.19)],
               (0.28, 0.18, 0.12, 0.85), segments=12)
    make_box("Interview_Coffee_Pot_Handle", (tx + 0.62, ty + 0.40, top + 0.10), (0.03, 0.04, 0.10), (0.10, 0.10, 0.10, 1.0))
    # the coffee cart in the NE corner: the machine the pot came from
    make_box("Coffee_Cart", (3.9, 3.55, 0.40), (0.70, 0.45, 0.80), (0.40, 0.42, 0.44, 1.0))
    make_box("Coffee_Maker", (3.8, 3.6, 0.96), (0.24, 0.26, 0.32), (0.86, 0.84, 0.78, 1.0))
    make_box("Coffee_Maker_Plate", (3.8, 3.48, 0.81), (0.16, 0.16, 0.01), (0.12, 0.12, 0.12, 1.0))
    make_box("Coffee_Cup_Stack", (4.1, 3.6, 0.88), (0.08, 0.08, 0.16), (0.96, 0.96, 0.94, 1.0))
    # the other men in the room — standing; they are scale, never faces
    make_standing_figure("Officer_By_Mirror", 0.55, 0.75, heading=math.pi * 0.25, h=1.80,
                         coat=(0.20, 0.24, 0.34, 1.0), pants=(0.18, 0.20, 0.26, 1.0), arms="folded")
    make_standing_figure("Officer_By_Cart", 3.05, 3.62, heading=math.pi * 1.05, h=1.76,
                         coat=(0.46, 0.40, 0.32, 1.0), pants=(0.26, 0.24, 0.22, 1.0), arms="down")


def build_squad_room():
    x0, x1, y0, y1 = 4.6, 15.0, -3.0, 8.0
    make_floor("Squad_Floor", ((x0 + x1) / 2, (y0 + y1) / 2, 0.0), size_x=x1 - x0, size_y=y1 - y0,
               palette={"vinyl": (0.60, 0.58, 0.52, 1.0), "seam": (0.52, 0.50, 0.46, 1.0)})
    make_box("Squad_Ceiling", ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.02), (x1 - x0, y1 - y0, 0.04), (0.88, 0.88, 0.84, 1.0))
    for i in range(3):
        for j in range(3):
            make_fluorescent_tube_fixture(f"Squad_Troffer_{i}_{j}", (6.8 + i * 3.2, -1.0 + j * 3.6, H), length=1.2, width=0.6)
    make_wall("Squad_Wall_N", ((x0 + x1) / 2, y1, 0.0), length=x1 - x0, height=H, thickness=0.16, axis='X', palette=SQUAD, baseboard_face_sign=-1)
    make_wall("Squad_Wall_S", ((x0 + x1) / 2, y0, 0.0), length=x1 - x0, height=H, thickness=0.16, axis='X', palette=SQUAD, baseboard_face_sign=+1)
    make_wall_with_openings("Squad_Wall_E", (x1, (y0 + y1) / 2, 0.0), length=y1 - y0, height=H, thickness=0.16, axis='Y',
                            palette=SQUAD, baseboard_face_sign=-1, openings=[(0.0, 1.5, 1.8, 1.3), (4.0, 1.5, 1.8, 1.3)])
    for k, wy in enumerate((0.0, 4.0)):
        make_window(f"Squad_Window_{k}", (x1 - 0.08, wy, 1.5), width=1.8, height=1.3, axis='Y', room_dir=-1)
        make_blinds(f"Squad_Blinds_{k}", (x1 - 0.08, wy, 1.5), width=1.8, height=1.3, axis='Y', room_dir=-1)
    # the interview wall's squad-room face shares Interview_Wall_E
    # desks: beige CRTs, desk phones, in-trays, a chair at each
    for k, (dx, dy) in enumerate(((7.0, 5.6), (10.2, 5.6), (7.0, 1.4), (10.2, 1.4), (12.8, -1.6))):
        make_table(f"Squad_Desk_{k}", dx, dy, w=1.5, d=0.75, h=0.76, wood=(0.50, 0.44, 0.36, 1.0))
        make_box(f"Squad_Desk_{k}_CRT", (dx - 0.35, dy + 0.12, 0.96), (0.40, 0.38, 0.36), (0.80, 0.78, 0.70, 1.0))
        make_box(f"Squad_Desk_{k}_CRT_Screen", (dx - 0.35, dy - 0.075, 0.98), (0.30, 0.01, 0.22), (0.16, 0.22, 0.20, 1.0))
        make_box(f"Squad_Desk_{k}_Phone", (dx + 0.40, dy, 0.80), (0.20, 0.22, 0.08), (0.22, 0.22, 0.22, 1.0))
        make_box(f"Squad_Desk_{k}_Tray", (dx + 0.10, dy + 0.18, 0.80), (0.28, 0.34, 0.08), (0.30, 0.30, 0.30, 1.0))
        make_chair(f"Squad_Desk_{k}_Chair", dx, dy - 0.75, yaw=0.0, seat_col=(0.20, 0.22, 0.30, 1.0))
    for k in range(4):
        make_box(f"Squad_File_Cabinet_{k}", (5.2 + k * 0.52, 7.65, 0.66), (0.48, 0.60, 1.32), (0.62, 0.62, 0.58, 1.0))
    make_box("Squad_Corkboard", (9.5, y1 - 0.10, 1.55), (2.4, 0.03, 1.1), (0.66, 0.50, 0.32, 1.0))
    for k in range(9):
        make_box(f"Squad_Corkboard_Sheet_{k}", (8.6 + (k % 5) * 0.42, y1 - 0.12, 1.25 + (k // 5) * 0.45), (0.22, 0.004, 0.28), (0.94, 0.92, 0.86, 1.0))
    make_box("Squad_Flag_Pole", (14.2, 7.4, 1.1), (0.04, 0.04, 2.2), (0.70, 0.62, 0.30, 1.0))
    make_box("Squad_Flag", (14.2, 7.15, 1.85), (0.02, 0.50, 0.32), (0.70, 0.20, 0.20, 1.0))
    # out the front windows: a wet main street, a storefront across it
    make_box("Street_Out", (21.0, 2.0, -0.05), (10.0, 40.0, 0.04), (0.20, 0.22, 0.24, 1.0))
    make_box("Street_Out_Sidewalk", (16.2, 2.0, 0.02), (1.6, 40.0, 0.08), (0.46, 0.46, 0.44, 1.0))
    make_box("Street_Out_Storefronts", (27.5, 2.0, 3.0), (3.0, 40.0, 6.0), (0.56, 0.50, 0.44, 1.0))
    for k in range(6):
        make_box(f"Street_Out_Storefront_Window_{k}", (25.98, -8.0 + k * 4.0, 1.4), (0.02, 2.2, 1.6), (0.30, 0.34, 0.36, 1.0))
    make_box("Street_Out_Car", (19.4, 3.4, 0.62), (1.8, 4.4, 1.2), (0.30, 0.34, 0.40, 1.0))


def main():
    clear_scene()
    build_interview()
    build_squad_room()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_police.glb"))
    print(f"\n[build_small_wood_police] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
