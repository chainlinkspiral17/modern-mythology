"""graustark_post_office — the post office on Elm, Graustark (vol5 ch20, 2026-10-10).

"She was at the post office on Elm. She had, three minutes before, handed
the envelope to the clerk. The clerk had stamped it. The envelope had
gone into the outgoing bin. Joanna had turned to leave. Joanna was, at
the moment the earth began, halfway to the door. The floor tiles of the
post office cracked in a single precise line from the outgoing bin to
Joanna's feet. The line passed between her shoes. The line continued to
the door. The door, on the line's arrival, opened of its own accord."
"Go, Joanna. Go now." — then "the alley beside the post office".

The beat played on the chalk wall in the ruins. This is the post office:
a small-town Louisiana federal lobby, 9 x 7 m under a 4 m ceiling with
two fans; checkerboard tile; the long counter with the clerk's window
behind its bronze grille, the scale and the stamp; the OUTGOING bin
behind the counter at the window's end; the wall of brass PO boxes; the
lobby table with its forms and chained pen; the flag; the clock; tall
windows on Elm; the door, standing open; and THE LINE — the crack
running in one straight course through the tiles from under the bin's
end of the counter to the door.

Coordinates: Blender Z-up, the door on the S wall at y 0. glTF export ->
Godot (x, z, -y).

Draft 2 targets: the alley beside it (the animals waiting); the street
on Elm beginning to lift.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, make_rot_box, export_glb
from _props.structure import make_wall, make_wall_with_openings
from _props.decor import make_wall_clock

W, D, H = 9.0, 7.0, 4.0
XW, XE, YS, YN = -W / 2.0, W / 2.0, 0.0, D
FW, FE, FS, FN = XW + 0.10, XE - 0.10, YS + 0.10, YN - 0.10
DOOR_X, DOOR_W, DOOR_H = 1.8, 1.1, 2.4
PAL = {"wall": (0.84, 0.82, 0.72, 1.0), "baseboard": (0.30, 0.22, 0.16, 1.0)}
WOOD = (0.46, 0.32, 0.20, 1.0); WOOD_DK = (0.32, 0.22, 0.14, 1.0); BRONZE = (0.56, 0.42, 0.24, 1.0)
TILE_A = (0.86, 0.84, 0.78, 1.0); TILE_B = (0.30, 0.30, 0.32, 1.0)
COUNTER_Y = 5.4
BIN_X = -2.9


def build_shell():
    # checkerboard tile, 0.6 m squares, in two tones
    make_box("Floor_Slab", (0.0, D / 2.0, -0.05), (W + 0.4, D + 0.4, 0.10), TILE_A)
    n_x, n_y = int(W / 0.6), int(D / 0.6)
    for i in range(n_x):
        for j in range(n_y):
            if (i + j) % 2:
                make_box(f"Floor_Tile_{i}_{j}", (XW + 0.3 + i * 0.6 + 0.0, 0.3 + j * 0.6, 0.001), (0.58, 0.58, 0.002), TILE_B)
    make_wall("Wall_W", (XW, D / 2.0, 0), length=D + 0.4, height=H, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_E", (XE, D / 2.0, 0), length=D + 0.4, height=H, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, YN, 0), length=W + 0.4, height=H, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_S", (0.0, YS, 0), length=W + 0.4, height=H, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(-2.6, 2.0, 1.4, 2.6), (DOOR_X, DOOR_H / 2.0, DOOR_W, DOOR_H)])
    make_box("Ceil", (0.0, D / 2.0, H + 0.05), (W + 0.4, D + 0.4, 0.10), (0.88, 0.86, 0.80, 1.0))
    make_box("Window_S_Glass", (-2.6, YS, 2.0), (1.4, 0.01, 2.6), (0.72, 0.78, 0.82, 0.3))
    make_box("Window_S_Sill", (-2.6, FS + 0.07, 0.68), (1.5, 0.16, 0.04), WOOD)
    make_box("Window_S_Mullion", (-2.6, YS, 2.0), (0.05, 0.08, 2.6), WOOD_DK)
    # the door standing open (it opened "of its own accord"), its transom
    hx = DOOR_X - DOOR_W / 2.0
    ang = math.radians(75.0)
    make_rot_box("Front_Door", (hx + math.cos(ang) * 0.52, FS + math.sin(ang) * 0.52, 1.17), (1.04, 0.05, 2.32), WOOD_DK, yaw=ang)
    make_rot_box("Front_Door_Glass", (hx + math.cos(ang) * 0.52 - math.sin(ang) * 0.03, FS + math.sin(ang) * 0.52 + math.cos(ang) * 0.03, 1.50),
                 (0.70, 0.01, 1.10), (0.72, 0.78, 0.82, 0.35), yaw=ang)
    make_box("Front_Door_Lettering", (DOOR_X, YS - 0.11, DOOR_H + 0.25), (1.6, 0.01, 0.22), (0.86, 0.72, 0.32, 1.0))
    for i, x in enumerate((-1.8, 1.8)):
        make_cyl(f"Fan_{i}_Rod", (x, 3.4, H - 0.30), 0.015, 0.60, (0.20, 0.20, 0.22, 1.0), segments=6)
        make_cyl(f"Fan_{i}_Motor", (x, 3.4, H - 0.66), 0.12, 0.14, (0.20, 0.20, 0.22, 1.0), segments=10)
        for b, (dx, dy, sw, sd) in enumerate(((0.42, 0, 0.62, 0.14), (-0.42, 0, 0.62, 0.14), (0, 0.42, 0.14, 0.62), (0, -0.42, 0.14, 0.62))):
            make_box(f"Fan_{i}_Blade_{b}", (x + dx, 3.4 + dy, H - 0.70), (sw, sd, 0.015), WOOD)
        make_lathe(f"Fan_{i}_Globe", (x, 3.4, H - 0.86), [(0.0, 0.0), (0.08, 0.02), (0.09, 0.08), (0.05, 0.12), (0.0, 0.12)], (0.96, 0.92, 0.80, 1.0), segments=10)


def build_counter():
    """The long counter, the clerk's window behind its grille, the scale and
    the stamp; the OUTGOING bin behind the counter at its W end."""
    x0, x1 = -4.0, 3.0
    make_box("Counter_Body", ((x0 + x1) / 2.0, COUNTER_Y, 0.55), (x1 - x0, 0.70, 1.10), WOOD)
    make_box("Counter_Top", ((x0 + x1) / 2.0, COUNTER_Y - 0.03, 1.125), (x1 - x0 + 0.06, 0.80, 0.05), (0.62, 0.58, 0.50, 1.0))
    for i in range(6):
        make_box(f"Counter_Panel_{i}", (x0 + 0.58 + i * 1.17, COUNTER_Y - 0.36, 0.55), (0.98, 0.02, 0.80), WOOD_DK)
    # the screen over the counter: three windows with bronze grilles; the clerk's is the open one
    make_box("Counter_Screen", ((x0 + x1) / 2.0, COUNTER_Y + 0.10, 2.10), (x1 - x0, 0.06, 1.90), WOOD_DK)
    for i, wx in enumerate((-2.9, -0.5, 1.9)):
        make_box(f"Clerk_Window_{i}_Opening", (wx, COUNTER_Y + 0.065, 1.55), (0.90, 0.01, 0.70), (0.22, 0.20, 0.18, 1.0))
        for k in range(7):
            make_box(f"Clerk_Window_{i}_Grille_{k}", (wx - 0.39 + k * 0.13, COUNTER_Y + 0.055, 1.55), (0.015, 0.012, 0.70), BRONZE)
        make_box(f"Clerk_Window_{i}_Sign", (wx, COUNTER_Y + 0.06, 2.05), (0.60, 0.01, 0.16), (0.90, 0.86, 0.70, 1.0))
    top = 1.15
    make_box("Postal_Scale", (-2.4, COUNTER_Y - 0.15, top + 0.06), (0.30, 0.26, 0.12), (0.72, 0.72, 0.74, 1.0))
    make_box("Postal_Scale_Pan", (-2.4, COUNTER_Y - 0.15, top + 0.125), (0.26, 0.22, 0.01), (0.80, 0.80, 0.82, 1.0))
    make_box("Date_Stamp_Pad", (-3.25, COUNTER_Y - 0.18, top + 0.01), (0.14, 0.09, 0.02), (0.20, 0.20, 0.30, 1.0))
    make_lathe("Date_Stamp", (-3.15, COUNTER_Y - 0.10, top), [(0.0, 0.0), (0.03, 0.0), (0.03, 0.02), (0.012, 0.04), (0.012, 0.09), (0.025, 0.11), (0.0, 0.12)], WOOD_DK, segments=8)
    # the OUTGOING bin behind the counter at the clerk's elbow, the canvas hamper
    make_box("Outgoing_Bin", (BIN_X, COUNTER_Y + 0.75, 0.40), (0.80, 0.60, 0.80), (0.40, 0.42, 0.36, 1.0))
    make_box("Outgoing_Bin_Label", (BIN_X, COUNTER_Y + 0.445, 0.62), (0.40, 0.01, 0.10), (0.92, 0.90, 0.84, 1.0))
    for k in range(5):
        make_rot_box(f"Outgoing_Letter_{k}", (BIN_X - 0.2 + k * 0.10, COUNTER_Y + 0.75, 0.80), (0.024, 0.16, 0.10), (0.94, 0.92, 0.86, 1.0), yaw=0.1 * k)
    make_box("Mail_Hamper", (BIN_X + 1.2, FN - 0.28, 0.40), (0.70, 0.55, 0.80), (0.52, 0.46, 0.36, 1.0))


def build_lobby():
    """The PO boxes, the lobby table, the flag, the clock, the board."""
    # the wall of brass PO boxes on the E wall
    bx = FE - 0.04
    for r in range(8):
        for c in range(10):
            make_box(f"PO_Box_{r}_{c}", (bx, 1.2 + c * 0.36, 0.55 + r * 0.24), (0.04, 0.33, 0.21), BRONZE)
            make_box(f"PO_Box_{r}_{c}_Window", (bx - 0.022, 1.2 + c * 0.36, 0.58 + r * 0.24), (0.004, 0.18, 0.08), (0.30, 0.30, 0.28, 1.0))
    make_box("PO_Box_Surround", (FE - 0.015, 2.82, 1.46), (0.03, 3.80, 2.10), WOOD_DK)
    # the lobby table with its forms and its pen on a chain
    tx, ty = -0.6, 2.4
    make_box("Lobby_Table_Top", (tx, ty, 1.05), (1.80, 0.60, 0.05), WOOD)
    make_box("Lobby_Table_Base", (tx, ty, 0.52), (1.60, 0.40, 1.02), WOOD_DK)
    for k in range(3):
        make_box(f"Lobby_Form_Slot_{k}", (tx - 0.5 + k * 0.5, ty + 0.22, 1.12), (0.30, 0.10, 0.10), WOOD_DK)
    make_cyl("Lobby_Pen", (tx + 0.3, ty - 0.10, 1.083), 0.005, 0.14, (0.10, 0.10, 0.12, 1.0), axis='X', segments=6)
    make_tube("Lobby_Pen_Chain", [(tx + 0.37, ty - 0.10, 1.083), (tx + 0.50, ty - 0.05, 1.076), (tx + 0.60, ty + 0.10, 1.076)], 0.003, (0.70, 0.70, 0.72, 1.0), segments=4)
    # the flag in its stand by the W wall, the clock over the counter, the wanted board
    make_box("Flag_Base", (FW + 0.40, 4.0, 0.06), (0.36, 0.36, 0.12), WOOD_DK)
    make_cyl("Flag_Pole", (FW + 0.40, 4.0, 1.35), 0.02, 2.50, (0.80, 0.66, 0.30, 1.0), segments=6)
    make_rot_box("Flag_Cloth", (FW + 0.40, 4.38, 2.20), (0.04, 0.70, 0.90), (0.72, 0.20, 0.18, 1.0), pitch=0.0, roll=0.10)
    make_box("Flag_Canton", (FW + 0.38, 4.20, 2.42), (0.004, 0.30, 0.38), (0.20, 0.28, 0.50, 1.0))
    make_wall_clock("Clock", (0.0, FN, 3.20), frozen_hour=10, frozen_min=44, facing='-Y')
    make_box("Wanted_Board", (FW + 0.015, 1.8, 1.60), (0.03, 1.20, 0.90), (0.62, 0.50, 0.34, 1.0))
    for i in range(6):
        make_box(f"Wanted_Poster_{i}", (FW + 0.035, 1.35 + (i % 3) * 0.32, 1.80 - (i // 3) * 0.42), (0.004, 0.24, 0.32), (0.92, 0.90, 0.84, 1.0))


def build_crack():
    """THE LINE: one straight crack through the tiles from under the bin's
    end of the counter to the door — splintered tile chips along it."""
    a = (BIN_X + 0.2, COUNTER_Y - 0.40)
    b = (DOOR_X, FS + 0.25)
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    yaw = math.atan2(dy, dx)
    n = 22
    for k in range(n):
        t = (k + 0.5) / n
        x, y = a[0] + dx * t, a[1] + dy * t
        jog = 0.03 * math.sin(k * 2.1)
        make_rot_box(f"Floor_Crack_{k}", (x - math.sin(yaw) * jog, y + math.cos(yaw) * jog, 0.0035), (L / n + 0.02, 0.025, 0.003), (0.06, 0.06, 0.06, 1.0), yaw=yaw)
    for k in range(9):
        t = (k + 0.5) / 9
        x, y = a[0] + dx * t, a[1] + dy * t
        make_rot_box(f"Floor_Crack_Chip_{k}", (x + 0.05 * math.cos(k * 1.7), y + 0.05 * math.sin(k * 1.7), 0.006), (0.06, 0.04, 0.008), TILE_A, yaw=k * 0.7)


def build_outside():
    make_box("Out_Sidewalk", (0.0, -1.8, -0.03), (20.0, 3.6, 0.06), (0.62, 0.60, 0.56, 1.0))
    make_box("Out_Elm_Street", (0.0, -8.0, -0.10), (30.0, 9.0, 0.06), (0.30, 0.30, 0.32, 1.0))
    make_box("Out_Sidewalk_Far", (0.0, -14.0, -0.03), (30.0, 3.0, 0.06), (0.60, 0.58, 0.54, 1.0))
    for i in range(4):
        make_box(f"Out_Elm_Front_{i}", (-9.0 + i * 6.0, -13.5, 2.8), (5.6, 0.6, 5.6), [(0.70, 0.62, 0.52, 1.0), (0.62, 0.66, 0.60, 1.0)][i % 2])
    from _props.trees import make_broadleaf
    make_broadleaf("Out_Live_Oak", -6.5, -3.4, 7.0, (0.30, 0.40, 0.24, 1.0), (0.32, 0.26, 0.20, 1.0), crown=0.42)


def main():
    clear_scene()
    build_shell(); build_counter(); build_lobby(); build_crack(); build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/graustark_post_office.glb"))
    print(f"\n[build_graustark_post_office] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
