"""Ben Kowalski's bedroom — vol6 placement script.

Canon (vol6 ch23 "Sleep" + ch19 "The Chains"): after dinner Ben goes
upstairs, packs his backpack for the morning, sets the alarm, gets in
bed at nine forty-eight. Mister, the half-Kowalski cat, comes through
the door "cracked the small specific way Ben has been cracking it for
a month" and curls up at his feet. The room is dark. Ch19 adds the
shower/lamp-off/alarm-for-ten ritual before a game.

A tidy athlete's room, NOT a slob room: made bed, packed backpack by
the door, football gear in the corner, the depth chart taped over the
desk. Bed-variation rules: headboard EAST wall, twin-XL with a low
footlocker at the foot — a footprint no other bedroom uses.

Hero props: the bed with Mister curled at its foot, the CRACKED door
(ajar at the canon angle), the desk with lamp + alarm clock reading
9:48, the backpack, the gear corner (helmet, shoulder pads, cleats).

Coordinate frame: Blender Z-up. y=0 south wall (door), +Y north,
walls x=±ROOM_W/2. glTF export remaps to Godot (x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling

ROOM_W = 3.6      # x ∈ [-1.8, 1.8]
ROOM_D = 4.0      # y ∈ [0, 4.0]
CEIL = 2.5

COL_WALL = (0.36, 0.40, 0.46, 1.0)      # slate blue-grey
COL_BASE = (0.24, 0.26, 0.30, 1.0)
COL_FLOOR = (0.35, 0.26, 0.17, 1.0)     # oak boards
COL_SEAM = (0.26, 0.19, 0.12, 1.0)
COL_FRAME = (0.30, 0.22, 0.14, 1.0)     # bed/desk wood
COL_FRAME_DK = (0.22, 0.16, 0.10, 1.0)
COL_SHEET = (0.72, 0.74, 0.78, 1.0)
COL_BLANKET = (0.20, 0.28, 0.42, 1.0)   # navy blanket
COL_PILLOW = (0.80, 0.80, 0.82, 1.0)
COL_CAT = (0.28, 0.26, 0.24, 1.0)       # Mister, a dark tabby shape
COL_DOOR = (0.60, 0.56, 0.50, 1.0)
COL_PACK = (0.24, 0.34, 0.28, 1.0)      # green backpack
COL_HELMET = (0.70, 0.68, 0.64, 1.0)
COL_JERSEY = (0.55, 0.14, 0.14, 1.0)    # school colors, wine red
COL_PAPER = (0.82, 0.80, 0.72, 1.0)
COL_LAMP = (1.00, 0.85, 0.58, 1.0)
COL_CLOCK = (0.90, 0.24, 0.16, 1.0)     # red LED digits
COL_RUG = (0.30, 0.32, 0.30, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    pal = {"wall": COL_WALL, "baseboard": COL_BASE}
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=pal, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=pal, baseboard_face_sign=-1)
    # South wall split around the door opening (west of center)
    make_wall("Wall_S_E", (0.85, 0.0, 0), length=ROOM_W - 1.5, height=CEIL,
              axis='X', palette=pal)
    make_box("Wall_S_W", (-1.55, 0.0, CEIL / 2.0), (0.5, 0.20, CEIL), COL_WALL)
    make_box("Wall_S_Above", (-0.85, 0.0, CEIL - 0.20), (0.95, 0.20, 0.40), COL_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=False, with_stains=False)
    # The CRACKED door — ajar ~25 degrees into the room (canon: the
    # small specific way, for Mister)
    make_box("Door", (-0.72, 0.30, 1.02), (0.14, 0.85, 2.04), COL_DOOR)
    make_cyl("Door_Knob", (-0.62, 0.62, 0.98), 0.035, 0.05, COL_FRAME_DK,
             segments=8, axis='X')
    make_box("Door_Jamb", (-1.28, 0.0, 1.02), (0.08, 0.22, 2.04), COL_FRAME_DK)
    # Oval rug mid-floor
    make_cyl("Rug", (0.1, 2.0, 0.008), 0.85, 0.012, COL_RUG, segments=16)


def build_bed():
    """Twin-XL, headboard EAST wall (unique footprint), footlocker at
    the foot, Mister curled at the foot of the blanket."""
    bx = ROOM_W / 2.0 - 1.05     # bed runs E→W, head at east wall
    by = 2.9
    make_box("Bed_Frame", (bx, by, 0.24), (2.0, 1.05, 0.22), COL_FRAME)
    make_box("Bed_Head", (ROOM_W / 2.0 - 0.06, by, 0.55), (0.08, 1.05, 0.75), COL_FRAME_DK)
    make_box("Bed_Mattress", (bx, by, 0.42), (1.95, 1.0, 0.16), COL_SHEET)
    make_box("Bed_Blanket", (bx - 0.25, by, 0.51), (1.4, 1.02, 0.06), COL_BLANKET)
    make_box("Bed_Pillow", (ROOM_W / 2.0 - 0.35, by, 0.54), (0.45, 0.6, 0.10), COL_PILLOW)
    # Mister, curled at the foot — a low mound with a tail sweep
    make_cyl("Cat_Mister", (bx - 0.75, by + 0.15, 0.57), 0.16, 0.10, COL_CAT, segments=10)
    make_box("Cat_Tail", (bx - 0.60, by + 0.28, 0.545), (0.22, 0.05, 0.03), COL_CAT)
    # Footlocker at the foot of the bed
    make_box("Footlocker", (bx - 1.25, by, 0.20), (0.35, 0.9, 0.38), COL_FRAME_DK)
    make_box("Footlocker_Lid", (bx - 1.25, by, 0.40), (0.36, 0.92, 0.03), COL_FRAME)


def build_desk():
    """Desk on the WEST wall: lamp, the 9:48 alarm clock, homework
    stack, the depth chart taped above."""
    dx = -ROOM_W / 2.0 + 0.32
    dy = 1.4
    make_box("Desk_Top", (dx, dy, 0.74), (0.6, 1.2, 0.05), COL_FRAME)
    for sy in (dy - 0.52, dy + 0.52):
        make_box(f"Desk_Leg_{sy:.1f}", (dx, sy, 0.37), (0.55, 0.05, 0.74), COL_FRAME_DK)
    # Lamp (the one he turns off)
    make_cyl("Desk_Lamp_Post", (dx - 0.12, dy + 0.42, 0.90), 0.015, 0.30, COL_FRAME_DK, segments=6)
    make_cyl("Desk_Lamp_Shade", (dx - 0.12, dy + 0.42, 1.06), 0.10, 0.10, COL_BLANKET, segments=10)
    make_cyl("Desk_Lamp_Bulb", (dx - 0.12, dy + 0.42, 1.01), 0.05, 0.03, COL_LAMP, segments=8)
    # Alarm clock — red LED block
    make_box("Clock", (dx - 0.05, dy - 0.35, 0.81), (0.20, 0.10, 0.09), (0.10, 0.10, 0.11, 1.0))
    make_box("Clock_Digits", (dx - 0.05, dy - 0.405, 0.81), (0.14, 0.005, 0.045), COL_CLOCK)
    # Homework stack + a pencil
    make_box("Papers", (dx + 0.05, dy + 0.05, 0.775), (0.30, 0.24, 0.03), COL_PAPER)
    make_cyl("Pencil", (dx + 0.12, dy - 0.12, 0.775), 0.008, 0.18, (0.75, 0.55, 0.20, 1.0),
             segments=6, axis='Y')
    # Chair
    make_box("Chair_Seat", (dx + 0.55, dy, 0.46), (0.40, 0.40, 0.05), COL_FRAME)
    make_box("Chair_Back", (dx + 0.74, dy, 0.78), (0.05, 0.40, 0.60), COL_FRAME)
    for cx, cy in ((dx + 0.38, dy - 0.16), (dx + 0.38, dy + 0.16),
                   (dx + 0.72, dy - 0.16), (dx + 0.72, dy + 0.16)):
        make_box(f"Chair_Leg_{cx:.2f}_{cy:.2f}", (cx, cy, 0.22), (0.04, 0.04, 0.44), COL_FRAME_DK)
    # THE DEPTH CHART taped to the wall above the desk (ch19 canon)
    make_box("DepthChart", (-ROOM_W / 2.0 + 0.03, dy, 1.55), (0.01, 0.5, 0.65), COL_PAPER)
    for r in range(6):
        make_box(f"DepthChart_Row_{r}", (-ROOM_W / 2.0 + 0.036, dy, 1.78 - r * 0.09),
                 (0.005, 0.42, 0.025), (0.35, 0.35, 0.38, 1.0))
    for tc in ((dy - 0.22, 1.86), (dy + 0.22, 1.24)):
        make_box(f"DepthChart_Tape_{tc[1]:.2f}", (-ROOM_W / 2.0 + 0.035, tc[0], tc[1]),
                 (0.006, 0.08, 0.04), (0.85, 0.82, 0.70, 0.8))


def build_gear_and_pack():
    """The packed backpack by the door; football gear in the NW
    corner; jersey hung on the wall."""
    # Backpack — packed, leaning by the door (ready for morning)
    make_box("Backpack", (-1.15, 0.55, 0.26), (0.34, 0.22, 0.5), COL_PACK)
    make_box("Backpack_Pocket", (-1.15, 0.42, 0.18), (0.26, 0.06, 0.24), (0.18, 0.26, 0.21, 1.0))
    make_box("Backpack_Strap", (-1.02, 0.55, 0.30), (0.04, 0.18, 0.42), (0.14, 0.20, 0.16, 1.0))
    # Gear corner NW: helmet on a crate, shoulder pads, cleats
    make_box("Gear_Crate", (-1.45, 3.6, 0.18), (0.45, 0.45, 0.36), COL_FRAME_DK)
    make_cyl("Helmet", (-1.45, 3.6, 0.48), 0.15, 0.24, COL_HELMET, segments=12)
    make_box("Helmet_Mask", (-1.45, 3.38, 0.42), (0.22, 0.05, 0.12), COL_FRAME_DK)
    make_box("ShoulderPads", (-0.95, 3.75, 0.12), (0.55, 0.35, 0.22), COL_HELMET)
    for k in range(2):
        make_box(f"Cleat_{k}", (-1.3 + k * 0.24, 3.15, 0.06), (0.12, 0.30, 0.10),
                 (0.15, 0.15, 0.16, 1.0))
    # Jersey on a hanger, north wall
    make_box("Jersey", (0.45, ROOM_D - 0.05, 1.55), (0.55, 0.04, 0.6), COL_JERSEY)
    make_box("Jersey_Num", (0.45, ROOM_D - 0.075, 1.55), (0.22, 0.01, 0.3), COL_PILLOW)
    make_cyl("Jersey_Rod", (0.45, ROOM_D - 0.06, 1.92), 0.015, 0.7, COL_FRAME_DK,
             segments=6, axis='X')
    # Window on the north wall (dark outside — the room is dark)
    make_box("Window_Frame", (0.45, ROOM_D - 0.02, 1.9), (1.0, 0.06, 0.06), COL_FRAME_DK)


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk()
    build_gear_and_pack()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/ben_bedroom.glb"))
    print(f"\n[build_ben_bedroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
