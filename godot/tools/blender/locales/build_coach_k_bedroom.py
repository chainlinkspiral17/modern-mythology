"""Coach K's master bedroom — vol6 placement script.

Canon (vol6 ch19 "The Chains", final beat): "In a different bedroom
in a different house in a different cul-de-sac, Coach K is in his bed
beside Eileen. Eileen is asleep. Coach K is not. Coach K is lying on
his back looking at the ceiling," running the depth chart the way he
has every Friday night before a game for twenty years.

A grown couple's room — deliberately DIFFERENT from every teen room:
queen bed centered on the NORTH wall, matched nightstands, a ceiling
fan (he is looking up at it), a dresser with twenty years of small
domestic sediment, reading glasses and a folded newspaper on his
side. Dark; the only lights are the clock digits and the moon seam
at the curtains.

Coordinate frame: Blender Z-up. y=0 south wall (door), +Y north,
walls x=±ROOM_W/2. glTF export remaps to Godot (x, z, -y).
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 4.4      # x ∈ [-2.2, 2.2]
ROOM_D = 4.6      # y ∈ [0, 4.6]
CEIL = 2.6

COL_WALL = (0.44, 0.40, 0.34, 1.0)      # warm taupe
COL_BASE = (0.30, 0.27, 0.22, 1.0)
COL_FLOOR = (0.30, 0.26, 0.22, 1.0)     # carpet
COL_SEAM = (0.26, 0.22, 0.19, 1.0)
COL_FRAME = (0.26, 0.18, 0.12, 1.0)     # dark cherry furniture
COL_FRAME_DK = (0.18, 0.12, 0.08, 1.0)
COL_SHEET = (0.68, 0.66, 0.62, 1.0)
COL_QUILT = (0.34, 0.30, 0.24, 1.0)     # tan quilt
COL_PILLOW = (0.78, 0.76, 0.72, 1.0)
COL_SLEEPER = (0.42, 0.38, 0.34, 1.0)   # Eileen under the quilt
COL_CURTAIN = (0.36, 0.32, 0.26, 1.0)
COL_MOON = (0.62, 0.68, 0.80, 1.0)      # the seam of night at the gap
COL_CLOCK = (0.90, 0.24, 0.16, 1.0)
COL_PAPER = (0.78, 0.76, 0.68, 1.0)
COL_FAN = (0.55, 0.50, 0.42, 1.0)


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
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # THE CEILING FAN — what he is looking at. Center of the room.
    make_cyl("Fan_Mount", (0.0, 2.3, CEIL - 0.06), 0.05, 0.10, COL_FRAME_DK, segments=8)
    make_cyl("Fan_Motor", (0.0, 2.3, CEIL - 0.18), 0.12, 0.14, COL_FAN, segments=10)
    for bi in range(4):
        ang = bi * 1.5708
        bx, by = 0.42 * math.cos(ang), 0.42 * math.sin(ang)
        make_box(f"Fan_Blade_{bi}", (bx, 2.3 + by, CEIL - 0.24),
                 (0.55 if bi % 2 == 0 else 0.16, 0.16 if bi % 2 == 0 else 0.55, 0.02),
                 COL_FAN)
    # Curtained window WEST — closed but for a seam of night
    make_box("Curtain_L", (-ROOM_W / 2.0 + 0.08, 2.3, 1.5), (0.06, 0.70, 1.6), COL_CURTAIN)
    make_box("Curtain_R", (-ROOM_W / 2.0 + 0.08, 3.15, 1.5), (0.06, 0.60, 1.6), COL_CURTAIN)
    make_box("Curtain_Seam", (-ROOM_W / 2.0 + 0.06, 2.78, 1.5), (0.02, 0.06, 1.5), COL_MOON)
    make_cyl("Curtain_Rod", (-ROOM_W / 2.0 + 0.10, 2.72, 2.36), 0.02, 1.6, COL_FRAME_DK,
             segments=6, axis='Y')


def build_bed():
    """Queen centered on the NORTH wall — two sleepers' sides, only
    one asleep."""
    by = ROOM_D - 1.15
    make_box("Bed_Frame", (0.0, by, 0.26), (1.7, 2.1, 0.24), COL_FRAME)
    make_box("Bed_Head", (0.0, ROOM_D - 0.08, 0.68), (1.7, 0.10, 0.95), COL_FRAME_DK)
    make_box("Bed_Foot", (0.0, by - 1.02, 0.42), (1.7, 0.06, 0.35), COL_FRAME_DK)
    make_box("Bed_Mattress", (0.0, by, 0.48), (1.62, 2.0, 0.18), COL_SHEET)
    make_box("Bed_Quilt", (0.0, by - 0.25, 0.585), (1.64, 1.5, 0.06), COL_QUILT)
    # Eileen — asleep, her side (west), a long low mound under the quilt
    make_box("Sleeper_Eileen", (-0.45, by - 0.1, 0.64), (0.5, 1.5, 0.12), COL_SLEEPER)
    make_box("Pillow_Eileen", (-0.45, ROOM_D - 0.35, 0.60), (0.55, 0.4, 0.10), COL_PILLOW)
    # Coach K's side: pillow dented, quilt folded back (he is on his
    # back on TOP of the covers, abstracted as a flatter mound)
    make_box("Sleeper_CoachK", (0.45, by - 0.15, 0.62), (0.5, 1.7, 0.08), COL_QUILT)
    make_box("Pillow_CoachK", (0.45, ROOM_D - 0.35, 0.60), (0.55, 0.4, 0.08), COL_PILLOW)


def build_nightstands():
    by = ROOM_D - 0.45
    for sgn, side in ((-1, "W"), (1, "E")):
        nx = sgn * 1.25
        make_box(f"Nightstand_{side}", (nx, by, 0.30), (0.45, 0.42, 0.55), COL_FRAME)
        make_box(f"Nightstand_{side}_Drawer", (nx, by - 0.23, 0.38), (0.36, 0.02, 0.14), COL_FRAME_DK)
    # Her side: a book, her glasses case
    make_box("Book_Eileen", (-1.25, by - 0.05, 0.61), (0.16, 0.22, 0.04), (0.40, 0.24, 0.22, 1.0))
    # His side: THE CLOCK (glowing digits — Friday night is long),
    # reading glasses, folded newspaper sports section
    make_box("Clock_Body", (1.25, by - 0.02, 0.63), (0.22, 0.11, 0.10), (0.10, 0.10, 0.11, 1.0))
    make_box("Clock_Digits", (1.25, by - 0.08, 0.63), (0.15, 0.005, 0.05), COL_CLOCK)
    make_box("Glasses", (1.15, by + 0.12, 0.585), (0.14, 0.06, 0.015), COL_FRAME_DK)
    make_box("Newspaper", (1.38, by + 0.08, 0.59), (0.18, 0.26, 0.02), COL_PAPER)


def build_dresser():
    """Dresser on the EAST wall + twenty years of sediment: framed
    photos, a dish of keys and whistles, folded laundry."""
    dx = ROOM_W / 2.0 - 0.30
    dy = 1.4
    make_box("Dresser", (dx, dy, 0.52), (0.55, 1.5, 1.0), COL_FRAME)
    for r in range(3):
        make_box(f"Dresser_Drawer_{r}", (dx - 0.28, dy, 0.28 + r * 0.28),
                 (0.02, 1.35, 0.20), COL_FRAME_DK)
        for kx in (dy - 0.35, dy + 0.35):
            make_cyl(f"Dresser_Knob_{r}_{kx:.1f}", (dx - 0.30, kx, 0.28 + r * 0.28),
                     0.02, 0.03, COL_BASE, segments=6, axis='X')
    # Framed photos, staggered
    for pi, (py, ph) in enumerate(((dy - 0.5, 0.22), (dy - 0.1, 0.28), (dy + 0.45, 0.20))):
        make_box(f"Photo_{pi}", (dx + 0.05, py, 1.02 + ph / 2.0 + 0.02),
                 (0.02, 0.16, ph), COL_FRAME_DK)
        make_box(f"Photo_{pi}_Img", (dx + 0.03, py, 1.02 + ph / 2.0 + 0.02),
                 (0.015, 0.12, ph - 0.05), (0.55, 0.52, 0.46, 1.0))
    # The dish: keys + the whistle he has carried for twenty years
    make_cyl("Dish", (dx - 0.05, dy + 0.15, 1.05), 0.09, 0.04, (0.55, 0.55, 0.58, 1.0),
             segments=10)
    make_cyl("Whistle", (dx - 0.05, dy + 0.15, 1.08), 0.025, 0.05, (0.72, 0.60, 0.24, 1.0),
             segments=6, axis='Y')
    # Folded laundry stack
    for li in range(3):
        make_box(f"Laundry_{li}", (dx - 0.02, dy - 0.55, 1.06 + li * 0.06),
                 (0.30, 0.26, 0.055), (0.5 + 0.08 * li, 0.5, 0.46, 1.0))


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_nightstands()
    build_dresser()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/coach_k_bedroom.glb"))
    print(f"\n[build_coach_k_bedroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
