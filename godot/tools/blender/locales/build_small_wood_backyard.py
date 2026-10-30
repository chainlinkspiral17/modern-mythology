"""small_wood_backyard — vol 2's "mayhune": her fifteenth birthday in the
backyard, Small Wood, Oregon, the late 1990s (draft 1, 2026-10-27).

It played on vol 6's 2026 Texas backyard (Kowalski's). The text:
  "Her family had set-up a large table out in the backyard. It was summer,
   of course."; "The small children played in a sprinkler, on a slip and
   slide. The bright husks of broken water balloons were not well hidden in
   the tall grass."; "He would sit in the grass, let his brothers and
   sisters wrestle him to the wet carpet."; "He drank cherry soda"; "a mash
   of cake and cream"; "The sound of a fog horn off in the distance, birds
   overhead."; she "loved animals and was preoccupied with breeding rabbits"
   (at nine — the hutches are still along the fence).
                                         → small_wood_backyard_party

PROPOSED: the house (a 1970s single-storey with a deck and a slider), the
fence, the colours of everything. Late-90s Oregon coast: grey-bright summer
sky, Douglas fir over the fence, a cedar-board fence silvered by weather.

Blender: x east, y north, z up; Godot (x, z, -y). The house's back wall
on y 0 facing north into the yard (y 0..24, x -12..12), the firs past
the back fence at y 26.

(2026-10-28) her room, upstairs that night (x 40..44.4): the stethoscope
on the quilt, the unwrapped presents, the pillows → mayhune_room_night.

DRAFT 2 targets: the kids in the sprinkler as figures with a pose; the
presents unwrapped on the table; her window above (her room, which the
scene goes up to after); the neighbours' roofs; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_rot_box, make_blob, make_tube, make_lathe,
                             join_stock, export_glb)
from _props.trees import make_conifer, make_shrub
from _props.furniture import make_chair, make_bed, make_lamp
from _props.figures import make_standing_figure
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window

GRASS = (0.34, 0.46, 0.24, 1.0)
GRASS_TALL = (0.42, 0.50, 0.28, 1.0)
WET = (0.24, 0.36, 0.20, 1.0)
SIDING = (0.70, 0.66, 0.54, 1.0)
TRIM = (0.92, 0.90, 0.84, 1.0)
DECK = (0.52, 0.40, 0.28, 1.0)
FENCE = (0.58, 0.56, 0.52, 1.0)
FIR = (0.12, 0.24, 0.16, 1.0)
TRUNK = (0.30, 0.22, 0.16, 1.0)


HUTCH_Y = (15.0, 16.4, 17.8)       # the rabbit hutches on the E fence (15.0 + k * 1.4)

def _rng(seed):
    s = [seed & 0x7fffffff or 1]
    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7fffffff
        return s[0] / 0x7fffffff
    return r


def build_house():
    """The back of a single-storey 1970s house: siding, two windows, the
    sliding glass door onto a low deck, the eave and the roof."""
    make_box("House_Back_Wall", (0.0, -0.1, 1.4), (18.0, 0.2, 2.8), SIDING)
    for k in range(14):
        make_box(f"House_Siding_Line_{k}", (0.0, 0.005, 0.2 + k * 0.2), (18.0, 0.01, 0.02), (0.60, 0.56, 0.46, 1.0))
    for k, wx in enumerate((-6.0, 5.4)):
        make_box(f"House_Window_{k}", (wx, 0.02, 1.6), (1.6, 0.04, 1.1), (0.30, 0.34, 0.36, 1.0))
        make_box(f"House_Window_{k}_Trim", (wx, 0.03, 1.6), (1.8, 0.02, 1.3), TRIM)
        make_box(f"House_Window_{k}_Glass", (wx, 0.05, 1.6), (1.6, 0.01, 1.1), (0.30, 0.34, 0.36, 1.0))
    make_box("Slider_Frame", (0.0, 0.03, 1.05), (2.4, 0.04, 2.1), TRIM)
    make_box("Slider_Glass", (0.0, 0.05, 1.05), (2.2, 0.01, 1.95), (0.32, 0.38, 0.40, 1.0))
    make_box("House_Eave", (0.0, 0.6, 2.9), (18.6, 1.4, 0.16), TRIM)
    make_rot_box("House_Roof", (0.0, -2.6, 3.9), (18.8, 7.0, 0.2), (0.30, 0.28, 0.28, 1.0), roll=-0.32)
    make_box("Deck", (0.0, 1.8, 0.25), (8.0, 3.6, 0.10), DECK)
    for k in range(4):
        make_box(f"Deck_Step_{k}", (0.0, 3.8 + k * 0.0, 0.10), (2.0, 0.5, 0.20), DECK)
    for k in range(9):
        make_box(f"Deck_Board_Seam_{k}", (-4.0 + k * 1.0, 1.8, 0.302), (0.02, 3.6, 0.004), (0.40, 0.30, 0.20, 1.0))
    make_box("Deck_Grill", (3.2, 1.2, 0.75), (0.6, 0.5, 0.8), (0.12, 0.12, 0.12, 1.0))
    make_cyl("Deck_Grill_Lid", (3.2, 1.2, 1.25), 0.32, 0.25, (0.12, 0.12, 0.12, 1.0), segments=12)


def build_yard():
    """The yard: lawn, its long-grass edges, the cedar fence, the hutches,
    the firs beyond."""
    make_box("Lawn", (0.0, 12.0, -0.03), (26.0, 26.0, 0.06), GRASS)
    make_box("Ground_Beyond", (0.0, 20.0, -0.08), (160.0, 120.0, 0.04), (0.28, 0.36, 0.22, 1.0))
    r = _rng(1997)
    for k in range(70):
        side = k % 3
        if side == 0:
            gx, gy = -11.4 + r() * 1.4, 2.0 + r() * 21.4
        elif side == 1:
            gx, gy = 9.9 + r() * 1.4, 2.0 + r() * 21.4
        else:
            gx, gy = -11.0 + r() * 22.0, 22.4 + r() * 0.9   # (clear of the N fence, 2026-10-30)
        rr = 0.3 + r() * 0.25
        if gx > 10.3 and any(abs(gy - hy) < 0.6 + rr + 0.1 for hy in HUTCH_Y):
            continue                     # the rabbit hutches stand there (2026-10-30)
        make_shrub(f"TallGrass_Stock_{k}", gx, gy, h=0.35 + r() * 0.3, r=rr, col=GRASS_TALL, segments=6)
    # the cedar-board fence, silvered
    for name, a, b in (("W", (-12.0, 0.0), (-12.0, 24.0)), ("E", (12.0, 0.0), (12.0, 24.0)), ("N", (-12.0, 24.0), (12.0, 24.0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ax = 'X' if b[1] == a[1] else 'Y'
        cx, cy = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        make_box(f"Fence_{name}", (cx, cy, 0.9), (L if ax == 'X' else 0.05, L if ax == 'Y' else 0.05, 1.8), FENCE)
        n = int(L / 2.4)
        for k in range(n + 1):
            t = k / n
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            make_box(f"Fence_{name}_Post_{k}", (px, py, 0.95), (0.10, 0.10, 1.9), (0.48, 0.46, 0.42, 1.0))
    # the rabbit hutches along the east fence (she bred rabbits at nine)
    for k in range(3):
        hy = 15.0 + k * 1.4
        make_box(f"Hutch_{k}", (11.1, hy, 0.9), (1.0, 1.2, 0.7), (0.56, 0.48, 0.36, 1.0))
        make_box(f"Hutch_{k}_Mesh", (10.59, hy, 0.95), (0.02, 1.0, 0.5), (0.42, 0.42, 0.40, 1.0))
        for s in (-1, 1):
            make_box(f"Hutch_{k}_Leg_{s:+d}", (11.1, hy + s * 0.5, 0.28), (0.08, 0.08, 0.56), (0.40, 0.32, 0.24, 1.0))
    make_blob("Rabbit", (10.9, 16.4, 1.30), 0.14, (0.86, 0.82, 0.76, 1.0), noise=0.1, seed=3, squash=0.8)
    # Douglas fir over the back fence
    for k in range(16):
        make_conifer(f"Fir_Stock_{k}", -30.0 + k * 4.0 + r() * 2.0, 30.0 + r() * 14.0, 18.0 + r() * 14.0, FIR, TRUNK, skirt=0.24)


def build_party():
    """The table, the sprinkler and the slip and slide, the balloon husks."""
    tx, ty = -3.0, 8.0
    make_box("Party_Table_Top", (tx, ty, 0.74), (3.6, 1.0, 0.04), (0.96, 0.94, 0.90, 1.0))
    make_box("Party_Tablecloth", (tx, ty, 0.60), (3.7, 1.1, 0.28), (0.90, 0.56, 0.62, 1.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_box(f"Party_Table_Leg_{sx:+d}{sy:+d}", (tx + sx * 1.6, ty + sy * 0.4, 0.36), (0.05, 0.05, 0.72), (0.70, 0.70, 0.70, 1.0))
    make_cyl("Party_Cake", (tx - 0.4, ty, 0.84), 0.20, 0.16, (0.96, 0.90, 0.86, 1.0), segments=16)
    make_cyl("Party_Cake_Cut", (tx - 0.4, ty - 0.1, 0.92), 0.06, 0.02, (0.56, 0.30, 0.22, 1.0), segments=8)
    for k in range(6):
        make_cyl(f"Party_Plate_{k}", (tx - 1.4 + k * 0.55, ty + (0.32 if k % 2 else -0.32), 0.765), 0.11, 0.01, (0.96, 0.96, 0.94, 1.0), segments=12)
    for k in range(5):
        make_cyl(f"Party_Soda_{k}", (tx - 1.2 + k * 0.6, ty + 0.1, 0.82), 0.033, 0.12, (0.78, 0.10, 0.20, 1.0), segments=8)   # cherry soda
    for k, col in enumerate(((0.30, 0.50, 0.86, 1.0), (0.96, 0.80, 0.24, 1.0), (0.40, 0.76, 0.46, 1.0))):
        make_box(f"Party_Present_{k}", (tx + 0.8 + k * 0.32, ty - 0.1, 0.84), (0.26, 0.24, 0.18), col)
    make_box("Party_Ice_Cream", (tx + 0.2, ty + 0.3, 0.82), (0.18, 0.14, 0.12), (0.92, 0.88, 0.80, 1.0))
    # folding chairs along both long sides, one pushed back where she sat
    for k, (cx_, cy_, yaw) in enumerate(((tx - 1.0, ty - 0.85, 0.0), (tx + 0.4, ty - 0.85, 0.0),
                                          (tx - 1.0, ty + 0.85, math.pi), (tx + 0.4, ty + 1.15, math.pi + 0.2))):
        make_chair(f"Party_Chair_{k}", cx_, cy_, yaw=yaw, wood=(0.86, 0.86, 0.84, 1.0))
    # the slip and slide down the lawn, the sprinkler at its head, wet grass round both
    make_box("SlipSlide", (4.5, 13.0, 0.012), (1.0, 7.0, 0.01), (0.96, 0.84, 0.20, 1.0))
    make_box("SlipSlide_Stripe", (4.5, 13.0, 0.014), (0.16, 7.0, 0.01), (0.20, 0.50, 0.86, 1.0))
    make_box("Wet_Grass", (4.5, 13.0, 0.002), (3.2, 9.0, 0.004), WET)
    make_cyl("Sprinkler_Base", (4.5, 9.0, 0.04), 0.10, 0.06, (0.30, 0.60, 0.30, 1.0), segments=10)
    make_box("Sprinkler_Arm", (4.5, 9.0, 0.10), (0.60, 0.04, 0.03), (0.60, 0.62, 0.64, 1.0))
    make_tube("Garden_Hose", [(4.5, 9.0, 0.03), (6.0, 6.0, 0.03), (7.5, 3.0, 0.03), (8.5, 0.3, 0.3)], 0.02, (0.20, 0.44, 0.22, 1.0), segments=5)
    r = _rng(15)
    for k in range(18):
        bx = -10.6 + r() * 2.2 if k % 2 else 9.0 + r() * 2.0
        by = 3.0 + r() * 19.0
        make_box(f"Balloon_Husk_Stock_{k}", (bx, by, 0.04), (0.10, 0.07, 0.01),
                 ((0.96, 0.30, 0.40, 1.0), (0.30, 0.60, 0.96, 1.0), (0.96, 0.86, 0.24, 1.0), (0.50, 0.86, 0.40, 1.0))[k % 4])
    # (2026-10-30, draft 2's target) the party had nobody at it. Stand-ins
    # (scale and staging, never faces; the girl and the boy are the VN's):
    # "The small children played in a sprinkler, on a slip and slide";
    # "Their parents had been best friends" — three of them at the table.
    for nm, x, y, hd, h, coat in (("Party_Kid_0", 4.9, 9.6, math.pi * 1.2, 1.12, (0.96, 0.40, 0.30, 1.0)),
                                  ("Party_Kid_1", 3.8, 10.5, math.pi * 0.7, 1.24, (0.30, 0.56, 0.86, 1.0)),
                                  ("Party_Kid_2", 3.9, 8.4, math.pi * 1.6, 1.05, (0.96, 0.86, 0.30, 1.0))):
        make_standing_figure(nm, x, y, heading=hd, h=h, coat=coat, pants=(0.30, 0.36, 0.56, 1.0), arms="down")
    make_standing_figure("Party_Parent_0", tx - 2.2, ty - 0.2, heading=math.pi * 0.5, h=1.76, coat=(0.56, 0.62, 0.48, 1.0), arms="folded")
    make_standing_figure("Party_Parent_1", tx + 2.1, ty + 0.4, heading=math.pi * 1.5, h=1.66, coat=(0.84, 0.66, 0.70, 1.0),
                         dress=(0.84, 0.66, 0.70, 1.0), arms="front")
    make_standing_figure("Party_Parent_2", tx + 0.7, ty - 1.6, heading=0.0, h=1.80, coat=(0.40, 0.44, 0.56, 1.0), arms="down")


def build_her_room():
    """(2026-10-28) HER ROOM, upstairs, that night — x 40..44.4, y 0..4,
    its own area (the VN only ever sees it from inside). The text: "she
    went up to her room and sat in silence. She looked over all her
    unwrapped presents"; "He'd given her a stethoscope for her birthday.
    She'd wanted to be a doctor now"; "The day turned to night and she sat
    on her pillows, her legs crossed"; at nine she "wanted to be a vet,
    loved animals and was preoccupied with breeding rabbits"; at thirteen
    she wanted "to go to Nepal and climb the highest mountain". A late-90s
    girl's room: the bed under the window, the presents and their paper,
    the stethoscope on the quilt, the animal posters of the vet she meant
    to be, the mountain she means to climb, the desk lamp on."""
    x0, x1, y0, y1, H = 40.0, 44.4, 0.0, 4.0, 2.45
    PAL = {"wall": (0.86, 0.80, 0.84, 1.0), "baseboard": (0.92, 0.90, 0.86, 1.0)}
    make_floor("Her_Room_Floor", ((x0 + x1) / 2, (y0 + y1) / 2, 0.0), size_x=x1 - x0, size_y=y1 - y0,
               palette={"vinyl": (0.58, 0.52, 0.56, 1.0), "seam": (0.52, 0.46, 0.50, 1.0)}, style="plank")
    make_box("Her_Room_Carpet", ((x0 + x1) / 2, 1.6, 0.006), (2.4, 1.8, 0.01), (0.46, 0.56, 0.62, 1.0))
    make_box("Her_Room_Ceiling", ((x0 + x1) / 2, (y0 + y1) / 2, H + 0.04), (x1 - x0 + 0.3, y1 - y0 + 0.3, 0.08), (0.94, 0.92, 0.90, 1.0))
    make_wall_with_openings("Her_Room_Wall_N", ((x0 + x1) / 2, y1, 0.0), length=x1 - x0 + 0.16, height=H, thickness=0.16,
                            axis='X', palette=PAL, baseboard_face_sign=-1, openings=[(42.8, 1.45, 1.1, 1.0)])
    make_window("Her_Room_Window", (42.8, y1 - 0.08, 1.45), width=1.1, height=1.0, axis='X', room_dir=-1)
    make_wall("Her_Room_Wall_S", ((x0 + x1) / 2, y0, 0.0), length=x1 - x0 + 0.16, height=H, thickness=0.16, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall("Her_Room_Wall_W", (x0, (y0 + y1) / 2, 0.0), length=y1 - y0, height=H, thickness=0.16, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Her_Room_Wall_E", (x1, (y0 + y1) / 2, 0.0), length=y1 - y0, height=H, thickness=0.16, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_box("Her_Room_Door", (x1 - 0.08, 0.8, 1.02), (0.04, 0.84, 2.04), (0.92, 0.90, 0.86, 1.0))
    # the bed under the window, piled pillows she sits on, the quilt
    make_bed("Her_Bed", 42.4, 3.0, head="+Y", w=1.05, d=1.95, style="frame")
    for k in range(3):
        make_box(f"Her_Bed_Pillow_{k}", (42.05 + k * 0.33, 3.70, 0.70 + (k % 2) * 0.04), (0.34, 0.30, 0.14), ((0.96, 0.90, 0.94, 1.0), (0.80, 0.86, 0.96, 1.0))[k % 2])
    make_box("Her_Bed_Quilt", (42.4, 2.70, 0.585), (1.10, 1.30, 0.04), (0.70, 0.40, 0.52, 1.0))
    # the stethoscope on the quilt: its tubing as a loop, the chest piece, the ear tips
    make_lathe("Stethoscope_Tubing", (42.55, 2.55, 0.615), [(0.10, 0.0), (0.12, 0.0), (0.12, 0.012), (0.10, 0.012)], (0.12, 0.12, 0.14, 1.0), segments=16, loop=True)
    make_cyl("Stethoscope_Chest_Piece", (42.72, 2.40, 0.62), 0.035, 0.02, (0.78, 0.78, 0.80, 1.0), segments=12)
    for s_ in (-1, 1):
        make_cyl(f"Stethoscope_Ear_Tip_{s_:+d}", (42.40 + s_ * 0.04, 2.68, 0.62), 0.012, 0.02, (0.20, 0.20, 0.22, 1.0), segments=8)
    # the unwrapped presents and their paper, on the bed's foot and the floor
    for k, (px, py, pz, col) in enumerate(((42.0, 2.15, 0.66, (0.30, 0.50, 0.86, 1.0)), (42.75, 2.05, 0.65, (0.96, 0.80, 0.24, 1.0)),
                                           (41.3, 1.6, 0.12, (0.40, 0.76, 0.46, 1.0)))):
        make_box(f"Present_Open_{k}", (px, py, pz), (0.26, 0.22, 0.16), col)
    for k in range(5):
        make_box(f"Present_Paper_{k}", (41.0 + k * 0.32, 1.2 + (k % 2) * 0.35, 0.012), (0.30, 0.22, 0.008),
                 ((0.90, 0.56, 0.62, 1.0), (0.30, 0.50, 0.86, 1.0), (0.96, 0.86, 0.30, 1.0))[k % 3])
    make_box("Present_Bow", (41.4, 1.35, 0.03), (0.08, 0.08, 0.05), (0.86, 0.20, 0.30, 1.0))
    # the desk, its lamp lit, a boom box, the phone
    make_box("Her_Desk_Top", (40.45, 2.2, 0.74), (0.60, 1.10, 0.04), (0.84, 0.80, 0.72, 1.0))
    for sy_ in (-1, 1):
        make_box(f"Her_Desk_Side_{sy_:+d}", (40.45, 2.2 + sy_ * 0.52, 0.37), (0.56, 0.03, 0.74), (0.84, 0.80, 0.72, 1.0))
    make_lamp("Her_Desk_Lamp", 40.35, 2.55, base_z=0.76, h=0.40, shade_col=(0.96, 0.86, 0.70, 1.0))
    make_box("Boom_Box", (40.45, 1.85, 0.86), (0.40, 0.16, 0.20), (0.24, 0.24, 0.26, 1.0))
    make_box("Her_Phone_Cordless", (40.55, 2.15, 0.78), (0.06, 0.18, 0.04), (0.92, 0.90, 0.86, 1.0))
    make_chair("Her_Desk_Chair", 40.95, 2.2, yaw=math.pi / 2.0, wood=(0.84, 0.80, 0.72, 1.0))
    # the walls: the vet she meant to be, the mountain she means to climb
    make_box("Poster_Rabbits", (40.09, 1.2, 1.60), (0.02, 0.50, 0.66), (0.86, 0.80, 0.70, 1.0))
    make_box("Poster_Horse", (40.09, 3.0, 1.62), (0.02, 0.56, 0.42), (0.62, 0.46, 0.32, 1.0))
    make_box("Poster_Everest", (43.2, 0.09, 1.55), (0.80, 0.02, 0.56), (0.80, 0.86, 0.94, 1.0))
    make_box("Corkboard", (41.4, 0.09, 1.45), (0.70, 0.02, 0.50), (0.70, 0.56, 0.40, 1.0))
    for k in range(5):
        make_box(f"Corkboard_Photo_{k}", (41.15 + (k % 3) * 0.24, 0.075, 1.38 + (k // 3) * 0.18), (0.14, 0.004, 0.10),
                 (0.5 + k * 0.08, 0.6, 0.7 - k * 0.06, 1.0))
    # the china rabbit and a stuffed one, from the rabbit years
    make_blob("Rabbit_Figurine", (40.55, 2.75, 0.82), 0.05, (0.94, 0.92, 0.88, 1.0), noise=0.1, seed=9, squash=0.9)
    make_blob("Stuffed_Rabbit", (42.9, 3.65, 0.78), 0.11, (0.84, 0.78, 0.70, 1.0), noise=0.12, seed=11, squash=0.85)
    make_box("Her_Dresser", (43.95, 2.6, 0.45), (0.46, 1.0, 0.90), (0.88, 0.86, 0.80, 1.0))
    make_box("Her_Dresser_Mirror", (44.27, 2.6, 1.30), (0.02, 0.60, 0.70), (0.66, 0.72, 0.76, 1.0))
    # outside the window: the backyard's firs under the night sky
    for k in range(6):
        make_conifer(f"Her_Room_View_Fir_{k}", 38.0 + k * 2.4, 9.0 + (k % 2) * 3.0, 9.0 + (k % 3) * 3.0, FIR, TRUNK, skirt=0.24)
    make_box("Her_Room_View_Ground", (42.0, 9.0, -2.6), (20.0, 12.0, 0.04), (0.10, 0.14, 0.10, 1.0))


def main():
    clear_scene()
    build_house()
    build_yard()
    build_party()
    build_her_room()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/small_wood_backyard.glb"))
    print(f"\n[build_small_wood_backyard] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
