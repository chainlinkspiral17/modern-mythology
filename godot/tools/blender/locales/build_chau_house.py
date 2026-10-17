"""chau_house — vol 3's "passengers": the Chau house, and Amanda's (draft 1,
2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Two houses in one GLB. They share nothing: Amanda's (x 40..56) is where the
hot tub and the blanket fort are ("Amanda's", Saturday 10 p.m.; the four
fall asleep there straight after), never the Chau house.

THE CHAU HOUSE (origin) — "six month old eight hundred thousand dollar
home", "the new empty beautiful house": big, new, sparsely furnished.
  "Light comes in through window blinds"   → Steven's room's E window
  "He grabs candy from a candy dish" ("Seasonal candy, this looks like
   Valentine's Day, old and left out")      → Candy_Dish on the hall table
  "He is in front of the bathroom door, it is closed."     → Bath_Door
  "there is Aaron hunched by the computer" (Steven's)      → Steven's desk,
                                            its monitor seen from the hall
  "the bass from the surround a rattle"   → the living room's TV and speakers
  "Mrs. Chau puts her purse on a counter and hangs up her jacket"
                                         → the entry counter, Coat_Hooks
  "The mess left in the kitchen"         → Kitchen_Mess_*
  the game room: "the liquor cabinet", "the fancy found cigars", "Playing
   billiards, throwing darts, flipping channels", "a potted fern like
   plant" in a corner                   → Pool_Table, Dartboard, Liquor_*,
                                            Game_TV, Fern
  the bathroom: the shower, "disposable razors found behind the mirror",
   the towels "discarded in a pile", the drain
  the living room: "Mrs. Chau on the couch", "The four men look down on her
   even if they're seated"              → the couch and four other seats
AMANDA'S (x 40..56) — "the two boys at a friend's house, her name Amanda":
  the jetted water at night (the text says nothing of its setting: a plain
  deck, a fence, the dark); and "pushed together couches ... music videos
  playing behind them on a large television. A large floor fan drones and
  kicks a sheet into the air, tented in place by a tall floor lamp."

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: Chris's room and Mrs. Chau's room past their doors, the
garage ("the open garage door"), the sheet's breathing as a per-frame
wobble (it is still), the steam as a fog pass, the kitchen's mess as more
than boxes; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe,
                             make_taper_cyl, join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_lamp
from _props.detail import make_wall_outlet, make_light_switch

X0, X1, D, H, T = -10.0, 12.0, 14.0, 2.9, 0.20
WALL = (0.90, 0.88, 0.84, 1.0); BASE = (0.70, 0.68, 0.64, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
OAK_FLOOR = (0.66, 0.52, 0.36, 1.0); OAK_SEAM = (0.56, 0.44, 0.30, 1.0)
TILE = (0.86, 0.84, 0.80, 1.0); TILE_SEAM = (0.74, 0.72, 0.68, 1.0)
DOOR = (0.92, 0.90, 0.86, 1.0)
LEATHER = (0.36, 0.24, 0.18, 1.0); SOFA = (0.80, 0.78, 0.72, 1.0)
FLAT = (0.08, 0.08, 0.09, 1.0)
DAYGLASS = (0.86, 0.90, 0.94, 1.0)
HALL_X0, HALL_X1 = 6.0, 7.6


def door_leaf(name, x, y, along, w=0.86):
    """A shut interior door in an opening: along 'X' (in an E-W wall) or 'Y'."""
    if along == 'X':
        make_box(name, (x, y, 1.0), (w, 0.05, 2.0), DOOR)
        make_cyl(name + "_Knob", (x + w / 2.0 - 0.08, y - 0.045, 0.98), 0.026, 0.04, (0.70, 0.64, 0.44, 1.0), axis='Y', segments=10)
    else:
        make_box(name, (x, y, 1.0), (0.05, w, 2.0), DOOR)
        make_cyl(name + "_Knob", (x - 0.045, y + w / 2.0 - 0.08, 0.98), 0.026, 0.04, (0.70, 0.64, 0.44, 1.0), axis='X', segments=10)


def window(name, along, line, c, z=1.5, w=1.6, h=1.3, sign=1):
    """A day window: frame, the bright pane (our panes are opaque)."""
    if along == 'X':
        make_box(name + "_Pane", (c, line + sign * 0.02, z), (w, 0.02, h), DAYGLASS)
        make_box(name + "_Sill", (c, line + sign * 0.12, z - h / 2.0 - 0.02), (w + 0.12, 0.16, 0.04), WALL)
    else:
        make_box(name + "_Pane", (line + sign * 0.02, c, z), (0.02, w, h), DAYGLASS)
        make_box(name + "_Sill", (line + sign * 0.12, c, z - h / 2.0 - 0.02), (0.16, w + 0.12, 0.04), WALL)


def build_shell():
    cx, cy = (X0 + X1) / 2.0, D / 2.0
    make_floor("Chau_Floor", (cx, cy, 0.0), size_x=X1 - X0 + 0.4, size_y=D + 0.4, palette={"vinyl": OAK_FLOOR, "seam": OAK_SEAM})
    make_box("Chau_Ceil", (cx, cy, H + 0.04), (X1 - X0 + 0.4, D + 0.4, 0.08), (0.94, 0.94, 0.92, 1.0))
    # outside walls: the front door on the S, windows round
    make_wall_with_openings("Chau_Wall_S", (cx, 0.0, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-2.0, 1.05, 1.0, 2.1), (-7.0, 1.5, 2.0, 1.3), (2.5, 1.5, 2.4, 1.4)])
    make_box("Front_Door", (-2.0, 0.0, 1.05), (0.98, 0.06, 2.08), (0.40, 0.30, 0.22, 1.0))
    window("Win_Kitchen_S", 'X', 0.0, -7.0, w=2.0, sign=1)
    window("Win_Living_S", 'X', 0.0, 2.5, w=2.4, h=1.4, sign=1)
    make_wall_with_openings("Chau_Wall_N", (cx, D, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(-1.5, 1.5, 2.4, 1.4), (4.0, 1.5, 1.6, 1.3)])
    window("Win_Living_N1", 'X', D, -1.5, w=2.4, h=1.4, sign=-1)
    window("Win_Living_N2", 'X', D, 4.0, sign=-1)
    make_wall("Chau_Wall_W", (X0, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall_with_openings("Chau_Wall_E", (X1, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(6.0, 1.5, 1.4, 1.3), (11.2, 1.5, 1.4, 1.3)])
    window("Win_Steven_E", 'Y', X1, 6.0, w=1.4, sign=-1)
    window("Win_Mom_E", 'Y', X1, 11.2, w=1.4, sign=-1)
    # Steven's blinds: the slats over his window
    for k in range(16):
        make_box(f"Blind_Steven_{k}", (X1 - 0.13, 6.0, 2.12 - k * 0.08), (0.006, 1.40, 0.05), (0.94, 0.94, 0.92, 1.0))
    make_box("Blind_Steven_Head", (X1 - 0.125, 6.0, 2.20), (0.05, 1.46, 0.05), (0.94, 0.94, 0.92, 1.0))
    for s in (-1, 1):             # the ladder cords the slats hang on
        make_box(f"Blind_Steven_Cord_{s:+d}", (X1 - 0.13, 6.0 + s * 0.45, 1.53), (0.008, 0.008, 1.30), (0.94, 0.94, 0.92, 1.0))
    # inside walls: the game room (W, its door to the living room), the hall
    # (E) and its rooms off it
    make_wall_with_openings("Wall_Game_E", (-4.0, 10.0, 0), length=8.0, height=H, thickness=0.14, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(9.0, 1.0, 0.90, 2.0)])
    make_wall("Wall_Game_S", (-7.0, 6.0, 0), length=6.0, height=H, thickness=0.14, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_box("Game_Door_Open", (-4.0 + 0.05 + 0.43, 9.0 - 0.45, 1.0), (0.86, 0.05, 2.0), DOOR)
    make_wall_with_openings("Wall_Hall_W", (HALL_X0, 7.0, 0), length=14.0, height=H, thickness=0.14, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(2.8, 1.1, 1.4, 2.2)])
    make_wall_with_openings("Wall_Hall_E", (HALL_X1, 7.0, 0), length=14.0, height=H, thickness=0.14, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(2.2, 1.0, 0.86, 2.0), (6.6, 1.0, 0.86, 2.0), (11.2, 1.0, 0.86, 2.0)])
    make_wall("Wall_Bath_N", ((HALL_X1 + X1) / 2.0, 3.6, 0), length=X1 - HALL_X1, height=H, thickness=0.14, axis='X', palette=PAL,
              baseboard_face_sign=-1)
    make_wall("Wall_Steven_N", ((HALL_X1 + X1) / 2.0, 9.0, 0), length=X1 - HALL_X1, height=H, thickness=0.14, axis='X', palette=PAL,
              baseboard_face_sign=-1)
    make_box("Hall_End_Wall", ((HALL_X0 + HALL_X1) / 2.0, D - 0.07, H / 2.0), (HALL_X1 - HALL_X0, 0.14, H), WALL)
    # the bathroom door shut (locked: the stranger in the shower), Steven's
    # standing open (the monitor's glow), Mrs. Chau's shut
    door_leaf("Bath_Door", HALL_X1, 2.2, 'Y')
    make_box("Steven_Door_Open", (HALL_X1 + 0.05 + 0.43, 6.6 - 0.45, 1.0), (0.86, 0.05, 2.0), DOOR)
    door_leaf("Mom_Door", HALL_X1, 11.2, 'Y')
    make_light_switch("Switch_Front", (-2.8, 0.0), axis='X', face_sign=1)
    make_wall_outlet("Outlet_Living", (2.0, D), axis='X', face_sign=-1)


def build_entry_kitchen():
    # the entry: coat hooks by the door, the jacket, the counter's end
    for k in range(4):
        make_box(f"Coat_Hook_{k}", (-3.2 + k * 0.22, 0.13, 1.70), (0.04, 0.06, 0.06), (0.50, 0.44, 0.30, 1.0))
    make_box("Coat_Hook_Board", (-2.87, 0.11, 1.74), (1.0, 0.02, 0.12), (0.60, 0.50, 0.36, 1.0))
    make_rug = make_box
    make_rug("Entry_Rug", (-2.0, 1.2, 0.006), (1.6, 1.0, 0.012), (0.40, 0.30, 0.30, 1.0))
    # the kitchen: counters on the W wall and the S wall, the island whose
    # end is "a counter" by the entry, the fridge, the mess
    make_box("Kitchen_Floor_Tile", (-7.0, 3.0, 0.008), (6.0, 6.0, 0.016), TILE)
    make_box("Kitchen_Counter_W", (X0 + 0.10 + 0.32, 2.65, 0.45), (0.64, 4.7, 0.90), (0.72, 0.66, 0.56, 1.0))
    make_box("Kitchen_Counter_W_Top", (X0 + 0.10 + 0.33, 2.65, 0.92), (0.66, 4.7, 0.04), (0.30, 0.28, 0.28, 1.0))
    make_box("Kitchen_Fridge", (X0 + 0.10 + 0.40, 5.6, 0.92), (0.78, 0.86, 1.84), (0.80, 0.80, 0.80, 1.0))
    make_box("Kitchen_Island", (-5.0, 3.0, 0.45), (1.0, 2.8, 0.90), (0.72, 0.66, 0.56, 1.0))
    make_box("Kitchen_Island_Top", (-5.0, 3.0, 0.92), (1.1, 2.9, 0.04), (0.30, 0.28, 0.28, 1.0))
    make_box("Purse_Spot", (-4.70, 1.85, 0.97), (0.30, 0.12, 0.06), (0.86, 0.84, 0.80, 1.0))   # a mat on the island's end
    for k in range(3):
        make_box(f"Kitchen_Mess_Box_{k}", (-5.1 + (k % 2) * 0.12, 3.4, 0.96 + k * 0.05), (0.42, 0.42, 0.04), (0.82, 0.74, 0.60, 1.0))
    for k in range(5):
        make_cyl(f"Kitchen_Mess_Bottle_{k}", (-5.3 + k * 0.14, 2.3, 1.06), 0.035, 0.24, ((0.30, 0.20, 0.10, 1.0), (0.20, 0.36, 0.20, 1.0))[k % 2],
                 segments=8)
    for k in range(4):
        make_cyl(f"Kitchen_Mess_Plate_{k}", (X0 + 0.45 + (k % 2) * 0.01, 1.2, 0.946 + k * 0.012), 0.12, 0.012, (0.94, 0.94, 0.92, 1.0), segments=14)
    for k in range(4):
        make_chair(f"Kitchen_Stool_{k}", -4.25, 2.0 + k * 0.65, yaw=-math.pi / 2.0, wood=(0.30, 0.30, 0.32, 1.0),
                   seat_col=(0.30, 0.30, 0.32, 1.0), seat_h=0.66, w=0.36)


def build_living():
    """The main living room: the big TV and its surround, the couch facing
    it, four more seats round."""
    tx, ty = 1.0, D - 0.10
    make_box("Living_TV", (tx, ty - 0.05, 1.45), (1.60, 0.08, 0.92), FLAT)
    make_box("Living_TV_Screen", (tx, ty - 0.092, 1.45), (1.52, 0.004, 0.84), (0.40, 0.46, 0.60, 1.0))
    make_box("Living_TV_Console", (tx, ty - 0.25, 0.30), (2.2, 0.46, 0.60), (0.24, 0.20, 0.18, 1.0))
    for s in (-1, 1):
        make_box(f"Surround_Tower_{s:+d}", (tx + s * 1.5, ty - 0.20, 0.55), (0.24, 0.26, 1.10), FLAT)
    make_box("Surround_Sub", (tx + 2.0, ty - 0.30, 0.25), (0.40, 0.40, 0.50), FLAT)
    make_box("Living_Rug", (tx, 8.6, 0.006), (4.6, 3.4, 0.012), (0.60, 0.56, 0.50, 1.0))
    # the couch (Mrs. Chau's) facing the TV, armchairs and chairs round
    cx, cy = tx, 7.4
    make_box("Couch_Base", (cx, cy, 0.22), (2.40, 0.92, 0.44), SOFA)
    make_box("Couch_Back", (cx, cy - 0.36, 0.68), (2.40, 0.20, 0.56), SOFA)
    for s in (-1, 1):
        make_box(f"Couch_Arm_{s:+d}", (cx + s * 1.11, cy, 0.56), (0.18, 0.92, 0.26), SOFA)
    for k in range(3):
        make_box(f"Couch_Cush_{k}", (cx - 0.70 + k * 0.70, cy + 0.06, 0.49), (0.66, 0.66, 0.12), (0.84, 0.82, 0.76, 1.0))
    make_box("Coffee_Table", (cx, 9.0, 0.22), (1.4, 0.7, 0.44), (0.40, 0.30, 0.22, 1.0))
    for k, (x, y, yaw) in enumerate(((cx - 2.3, 8.6, -math.pi / 2.0 + 0.3), (cx + 2.3, 8.6, math.pi / 2.0 - 0.3))):
        make_box(f"Armchair_{k}_Base", (x, y, 0.22), (0.86, 0.86, 0.44), LEATHER)
        make_rot_box(f"Armchair_{k}_Back", (x + (-0.36 if k == 0 else 0.36), y, 0.66), (0.16, 0.86, 0.50), LEATHER, yaw=0.0)
    for k, x in enumerate((cx - 1.4, cx + 1.4)):
        make_chair(f"Living_Chair_{k}", x, 10.4, yaw=math.pi, wood=(0.40, 0.30, 0.22, 1.0), seat_col=(0.60, 0.54, 0.46, 1.0))
    make_lamp("Lamp_Living", cx + 2.6, 6.6, base_z=0.0, h=1.50)


def build_hall_rooms():
    # the hall table at its S end: the candy dish of Valentine's candy
    hx = HALL_X0 + 0.07 + 0.16
    ty = 1.45
    make_box("Hall_Table", (hx, ty, 0.80), (0.30, 0.90, 0.03), (0.40, 0.30, 0.22, 1.0))
    for s in (-1, 1):
        make_box(f"Hall_Table_Leg_{s:+d}", (hx, ty + s * 0.40, 0.395), (0.26, 0.03, 0.77), (0.40, 0.30, 0.22, 1.0))
    make_lathe("Candy_Dish", (hx, ty, 0.815), [(0.0, 0.0), (0.08, 0.0), (0.11, 0.04), (0.12, 0.05), (0.0, 0.05)],
               (0.80, 0.86, 0.90, 1.0), segments=14)
    for k in range(6):
        make_box(f"Candy_Heart_{k}", (hx - 0.05 + (k % 3) * 0.05, ty - 0.04 + (k // 3) * 0.06, 0.86), (0.035, 0.035, 0.02),
                 ((0.90, 0.30, 0.40, 1.0), (0.96, 0.70, 0.76, 1.0))[k % 2])
    make_box("Hall_Runner", ((HALL_X0 + HALL_X1) / 2.0, 7.0, 0.005), (0.90, 12.0, 0.01), (0.44, 0.32, 0.30, 1.0))
    # the bathroom (x 7.6..12, y 0..3.6): vanity and mirror cabinet on the E
    # wall, its door ajar; the shower in the NE; the towels on the floor
    bx = X1 - 0.10
    make_box("Bath_Floor_Tile", ((HALL_X1 + X1) / 2.0, 1.8, 0.008), (X1 - HALL_X1, 3.6, 0.016), TILE)
    make_box("Bath_Vanity", (bx - 0.28, 1.4, 0.42), (0.56, 1.20, 0.84), (0.86, 0.84, 0.80, 1.0))
    make_box("Bath_Vanity_Top", (bx - 0.29, 1.4, 0.86), (0.58, 1.24, 0.04), (0.80, 0.80, 0.82, 1.0))
    make_cyl("Bath_Sink", (bx - 0.30, 1.4, 0.875), 0.18, 0.02, (0.96, 0.96, 0.96, 1.0), segments=16)
    make_box("Bath_Mirror_Cabinet", (bx - 0.06, 1.4, 1.55), (0.12, 0.80, 0.76), (0.86, 0.86, 0.84, 1.0))
    make_rot_box("Bath_Mirror_Door", (bx - 0.30, 1.4 + 0.40 - 0.03, 1.55), (0.02, 0.06, 0.74), (0.70, 0.76, 0.80, 1.0))
    make_box("Bath_Mirror_Door_Glass", (bx - 0.12 - 0.15, 1.4 + 0.42, 1.55), (0.30, 0.02, 0.72), (0.72, 0.78, 0.82, 1.0))
    for k in range(3):
        make_box(f"Bath_Razor_{k}", (bx - 0.10, 1.25 + k * 0.08, 1.30), (0.06, 0.012, 0.10), (0.30, 0.50, 0.86, 1.0))
    make_box("Bath_Cabinet_Shelf", (bx - 0.07, 1.4, 1.26), (0.10, 0.76, 0.012), (0.86, 0.86, 0.84, 1.0))
    make_box("Bath_Vanity_Light", (bx - 0.05, 1.4, 2.06), (0.10, 0.70, 0.10), (1.0, 0.96, 0.86, 1.0))
    for k in range(4):
        make_cyl(f"Bath_Toiletry_{k}", (bx - 0.45, 0.95 + k * 0.10, 0.94), 0.025, 0.14, ((0.40, 0.70, 0.86, 1.0), (0.90, 0.86, 0.70, 1.0))[k % 2],
                 segments=8)
    make_box("Shower_Base", (X1 - 0.10 - 0.55, 3.6 - 0.07 - 0.55, 0.05), (1.1, 1.1, 0.10), (0.94, 0.94, 0.94, 1.0))
    make_box("Shower_Glass_S", (X1 - 0.10 - 0.55, 3.6 - 0.07 - 1.10, 1.05), (1.1, 0.02, 1.90), (0.80, 0.86, 0.88, 1.0))
    make_box("Shower_Glass_W", (X1 - 0.10 - 1.10, 3.6 - 0.07 - 0.55, 1.05), (0.02, 1.1, 1.90), (0.80, 0.86, 0.88, 1.0))
    make_cyl("Shower_Drain", (X1 - 0.10 - 0.55, 3.6 - 0.07 - 0.55, 0.102), 0.05, 0.004, (0.60, 0.60, 0.62, 1.0), segments=10)
    make_box("Shower_Head_Arm", (X1 - 0.18, 3.6 - 0.07 - 0.55, 1.95), (0.16, 0.025, 0.025), (0.74, 0.74, 0.76, 1.0))
    make_cyl("Shower_Head", (X1 - 0.27, 3.6 - 0.07 - 0.55, 1.93), 0.06, 0.03, (0.74, 0.74, 0.76, 1.0), segments=10)
    for k in range(4):
        make_chamfer_box(f"Towel_Pile_{k}", (9.0 + (k % 2) * 0.14, 0.8 + k * 0.08, 0.04 + k * 0.06), (0.56, 0.40, 0.07),
                         ((0.94, 0.94, 0.92, 1.0), (0.70, 0.80, 0.86, 1.0))[k % 2], chamfer=0.02)
    make_box("Toilet_Bowl", (8.2, 3.6 - 0.07 - 0.36, 0.20), (0.38, 0.50, 0.40), (0.96, 0.96, 0.96, 1.0))
    make_box("Toilet_Tank", (8.2, 3.6 - 0.07 - 0.10, 0.58), (0.44, 0.20, 0.36), (0.96, 0.96, 0.96, 1.0))
    # Steven's room (y 3.6..9): the bed he woke in, the desk and computer near
    # his door (seen from the hall), the blinds on the E window
    make_bed("Steven_Bed", X1 - 0.10 - 1.0, 8.9 - 0.07 - 0.75, head="+X", w=1.40, d=2.0, made=False, blanket_col=(0.30, 0.34, 0.46, 1.0))
    dx, dy = HALL_X1 + 0.07 + 0.36, 4.5
    make_box("Steven_Desk_Top", (dx, dy, 0.74), (0.72, 1.40, 0.03), (0.30, 0.30, 0.32, 1.0))
    for s in (-1, 1):
        make_box(f"Steven_Desk_Leg_{s:+d}", (dx, dy + s * 0.66, 0.36), (0.68, 0.04, 0.72), (0.24, 0.24, 0.26, 1.0))
    make_chamfer_box("Steven_CRT", (dx - 0.08, dy + 0.10, 0.97), (0.40, 0.40, 0.42), (0.80, 0.76, 0.66, 1.0), chamfer=0.03)
    make_box("Steven_CRT_Screen", (dx + 0.125, dy + 0.10, 0.98), (0.004, 0.32, 0.26), (0.40, 0.56, 0.76, 1.0))
    make_box("Steven_Tower", (dx - 0.05, dy + 0.62, 0.98), (0.44, 0.18, 0.44), (0.80, 0.76, 0.66, 1.0))
    make_box("Steven_Keyboard", (dx + 0.22, dy + 0.10, 0.76), (0.16, 0.44, 0.025), (0.80, 0.76, 0.66, 1.0))
    make_chair("Steven_Chair", dx + 0.66, dy + 0.05, yaw=math.pi / 2.0, wood=(0.24, 0.24, 0.26, 1.0))
    make_blob("Steven_Clothes", (X1 - 0.6, 4.1, 0.10), 0.28, (0.36, 0.34, 0.30, 1.0), noise=0.3, seed=3, squash=0.4)
    # Mrs. Chau's room (y 9..14): the bed, the dresser and its mirror
    make_bed("Mom_Bed", X1 - 0.10 - 1.1, 12.4, head="+X", w=1.60, d=2.1, blanket_col=(0.80, 0.74, 0.66, 1.0))
    make_box("Mom_Dresser", (HALL_X1 + 0.07 + 0.26, 12.0, 0.42), (0.50, 1.20, 0.84), (0.52, 0.40, 0.30, 1.0))
    make_box("Mom_Dresser_Mirror", (HALL_X1 + 0.08, 12.0, 1.40), (0.03, 0.80, 0.90), (0.72, 0.78, 0.82, 1.0))


def build_game_room():
    """W of the living room (x -10..-4, y 6..14): the pool table, the
    dartboard, the liquor cabinet, the TV, the fern in its corner, and the
    night's leavings."""
    gx, gy = -7.0, 10.0
    make_box("Game_Carpet", (gx, gy, 0.006), (6.0, 8.0, 0.012), (0.30, 0.20, 0.20, 1.0))
    make_box("Pool_Table_Bed", (gx, gy, 0.76), (1.30, 2.40, 0.10), (0.20, 0.46, 0.30, 1.0))
    for s in (-1, 1):
        make_box(f"Pool_Table_Rail_X_{s:+d}", (gx + s * 0.70, gy, 0.80), (0.12, 2.64, 0.12), (0.34, 0.20, 0.12, 1.0))
        make_box(f"Pool_Table_Rail_Y_{s:+d}", (gx, gy + s * 1.26, 0.80), (1.28, 0.12, 0.12), (0.34, 0.20, 0.12, 1.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_box(f"Pool_Table_Leg_{sx:+d}_{sy:+d}", (gx + sx * 0.55, gy + sy * 1.05, 0.355), (0.14, 0.14, 0.71), (0.30, 0.18, 0.10, 1.0))
    for k in range(5):
        make_blob(f"Pool_Ball_{k}", (gx - 0.3 + k * 0.15, gy + 0.4 - (k % 2) * 0.3, 0.84), 0.028,
                  ((0.96, 0.96, 0.94, 1.0), (0.90, 0.80, 0.20, 1.0), (0.20, 0.30, 0.70, 1.0), (0.80, 0.20, 0.16, 1.0), (0.10, 0.10, 0.10, 1.0))[k],
                  noise=0.0, seed=k)
    make_rot_box("Pool_Cue_Floor", (gx + 1.0, gy - 1.6, 0.02), (0.03, 1.45, 0.03), (0.70, 0.56, 0.36, 1.0), yaw=0.4)
    # the dartboard on the N wall, darts in it and one in the wall
    make_cyl("Dartboard", (gx, D - 0.12, 1.73), 0.23, 0.04, (0.14, 0.12, 0.10, 1.0), axis='Y', segments=20)
    make_cyl("Dartboard_Face", (gx, D - 0.145, 1.73), 0.20, 0.01, (0.86, 0.80, 0.62, 1.0), axis='Y', segments=20)
    make_cyl("Dartboard_Bull", (gx, D - 0.152, 1.73), 0.03, 0.01, (0.80, 0.16, 0.14, 1.0), axis='Y', segments=12)
    for k, (dx, dz) in enumerate(((0.08, 0.05), (-0.12, -0.04), (0.40, 0.30))):
        make_cyl(f"Dart_{k}", (gx + dx, D - 0.14 - (0.04 if k < 2 else 0.0), 1.73 + dz), 0.006, 0.08, (0.20, 0.30, 0.70, 1.0), axis='Y', segments=6)
    # the liquor cabinet on the W wall, open, bottles out on its top
    lx = X0 + 0.10 + 0.25
    make_box("Liquor_Cabinet", (lx, 11.5, 0.70), (0.50, 1.40, 1.40), (0.30, 0.18, 0.12, 1.0))
    make_box("Liquor_Cabinet_Door_Open", (lx + 0.55, 11.5 + 0.715, 0.75), (0.60, 0.03, 1.10), (0.30, 0.18, 0.12, 1.0))
    for k in range(6):
        make_cyl(f"Liquor_Bottle_{k}", (lx, 11.25 + k * 0.17, 1.52), 0.04, 0.24 + (k % 3) * 0.04,
                 ((0.50, 0.30, 0.12, 1.0), (0.80, 0.80, 0.76, 1.0), (0.20, 0.36, 0.20, 1.0))[k % 3], segments=8)
    make_cyl("Bottle_On_Floor", (gx + 1.4, gy + 2.6, 0.04), 0.04, 0.28, (0.50, 0.30, 0.12, 1.0), axis='X', segments=8)
    make_box("Cigar_Box", (lx + 0.10, 10.95, 1.43), (0.24, 0.18, 0.06), (0.60, 0.40, 0.20, 1.0))
    make_cyl("Ashtray", (gx + 0.66, gy - 1.10, 0.875), 0.08, 0.02, (0.70, 0.70, 0.70, 1.0), segments=12)
    for k in range(4):
        make_rot_box(f"Cigar_Butt_{k}", (gx + 0.62 + (k % 2) * 0.05, gy - 1.12 + k * 0.025, 0.895), (0.08, 0.016, 0.016),
                     (0.42, 0.26, 0.14, 1.0), yaw=k * 0.8)
    # the TV on the S wall (the jazz channel left on), a leather chair
    make_box("Game_TV", (gx, 6.0 + 0.07 + 0.05, 1.50), (1.30, 0.08, 0.76), FLAT)
    make_box("Game_TV_Screen", (gx, 6.0 + 0.07 + 0.092, 1.50), (1.22, 0.004, 0.68), (0.30, 0.34, 0.56, 1.0))
    make_box("Game_TV_Console", (gx, 6.0 + 0.07 + 0.25, 0.30), (1.6, 0.44, 0.60), (0.24, 0.20, 0.18, 1.0))
    make_box("Game_Chair_Base", (gx + 2.2, 7.4, 0.22), (0.86, 0.86, 0.44), LEATHER)
    make_box("Game_Chair_Back", (gx + 2.2, 7.4 - 0.36, 0.66), (0.86, 0.16, 0.50), LEATHER)
    # the fern in the SW corner, its pot
    make_taper_cyl("Fern_Pot", (X0 + 0.45, 6.0 + 0.07 + 0.38, 0.22), 0.20, 0.26, 0.44, (0.62, 0.36, 0.24, 1.0), segments=12)
    make_cyl("Fern_Soil", (X0 + 0.45, 6.0 + 0.07 + 0.38, 0.445), 0.24, 0.01, (0.24, 0.18, 0.12, 1.0), segments=12)
    for k in range(9):
        a = k * 0.70
        make_rot_box(f"Fern_Frond_{k}", (X0 + 0.45 + math.cos(a) * 0.22, 6.45 + math.sin(a) * 0.22, 0.72), (0.06, 0.16, 0.60),
                     (0.26, 0.48, 0.22, 1.0), yaw=a, roll=0.5)


# ── AMANDA'S (x 40..56) ───────────────────────────────────────────────
AX0, AX1, AD, AH = 40.0, 47.0, 6.4, 2.6


def build_amanda():
    cx, cy = (AX0 + AX1) / 2.0, AD / 2.0
    make_floor("Am_Floor", (cx, cy, 0.0), size_x=AX1 - AX0 + 0.4, size_y=AD + 0.4,
               palette={"vinyl": (0.52, 0.48, 0.42, 1.0), "seam": (0.46, 0.42, 0.36, 1.0)})
    make_box("Am_Ceil", (cx, cy, AH + 0.04), (AX1 - AX0 + 0.4, AD + 0.4, 0.08), (0.86, 0.84, 0.80, 1.0))
    apal = {"wall": (0.78, 0.74, 0.66, 1.0), "baseboard": (0.50, 0.44, 0.36, 1.0)}
    make_wall("Am_Wall_W", (AX0, cy, 0), length=AD + 0.4, height=AH, thickness=T, axis='Y', palette=apal, baseboard_face_sign=+1)
    make_wall("Am_Wall_N", (cx, AD, 0), length=AX1 - AX0 + 0.4, height=AH, thickness=T, axis='X', palette=apal, baseboard_face_sign=-1)
    make_wall("Am_Wall_S", (cx, 0.0, 0), length=AX1 - AX0 + 0.4, height=AH, thickness=T, axis='X', palette=apal, baseboard_face_sign=+1)
    make_wall_with_openings("Am_Wall_E", (AX1, cy, 0), length=AD + 0.4, height=AH, thickness=T, axis='Y', palette=apal,
                            baseboard_face_sign=-1, openings=[(3.2, 1.05, 1.8, 2.1)])
    # the large television on the W wall, music videos on it
    make_box("Am_TV", (AX0 + 0.15, 3.2, 1.20), (0.50, 1.10, 0.90), FLAT)          # a big rear-projection-deep set
    make_box("Am_TV_Screen", (AX0 + 0.402, 3.2, 1.25), (0.004, 0.96, 0.72), (0.46, 0.40, 0.84, 1.0))
    make_box("Am_TV_Stand", (AX0 + 0.35, 3.2, 0.37), (0.70, 1.30, 0.74), (0.20, 0.18, 0.16, 1.0))
    # the two couches pushed together seat to seat into one bed
    for k, (y, face) in enumerate(((2.35, 1), (4.05, -1))):
        make_box(f"Am_Couch_{k}_Base", (43.6, y, 0.22), (2.20, 0.90, 0.44), (0.40, 0.30, 0.44, 1.0))
        make_box(f"Am_Couch_{k}_Back", (43.6, y - face * 0.36, 0.66), (2.20, 0.18, 0.52), (0.40, 0.30, 0.44, 1.0))
        for s in (-1, 1):
            make_box(f"Am_Couch_{k}_Arm_{s:+d}", (43.6 + s * 1.01, y, 0.56), (0.18, 0.90, 0.24), (0.40, 0.30, 0.44, 1.0))
        make_box(f"Am_Couch_{k}_Cush", (43.6, y + face * 0.06, 0.48), (1.82, 0.70, 0.08), (0.46, 0.36, 0.50, 1.0))
    # towels and blankets on the bed of them
    for k in range(5):
        make_chamfer_box(f"Am_Blanket_{k}", (43.0 + k * 0.32, 3.1 + (k % 2) * 0.26, 0.56), (0.70, 0.90, 0.07),
                         ((0.94, 0.94, 0.92, 1.0), (0.30, 0.44, 0.66, 1.0), (0.86, 0.60, 0.50, 1.0))[k % 3], chamfer=0.02)
    # the tall floor lamp, the sheet tented over it, the floor fan blowing
    lx, ly = 43.6, 3.2
    make_cyl("Am_Floor_Lamp_Base", (lx + 1.6, ly, 0.02), 0.16, 0.04, (0.30, 0.30, 0.30, 1.0), segments=12)
    make_cyl("Am_Floor_Lamp_Pole", (lx + 1.6, ly, 0.92), 0.015, 1.80, (0.40, 0.40, 0.40, 1.0), segments=8)
    make_lathe("Am_Floor_Lamp_Shade", (lx + 1.6, ly, 1.78), [(0.10, 0.0), (0.20, 0.0), (0.12, 0.26), (0.06, 0.26)], (0.92, 0.88, 0.76, 1.0),
               segments=12)
    # the sheet: a ridge from the lamp's top down over the couches, its two
    # sides falling away, billowed on the fan's side
    make_rot_box("Am_Sheet_Ridge", (lx + 0.5, ly, 1.64), (2.30, 0.10, 0.02), (0.90, 0.90, 0.94, 1.0), pitch=-0.38)
    for s in (-1, 1):
        make_rot_box(f"Am_Sheet_Side_{s:+d}", (lx + 0.3, ly + s * 0.55, 1.20), (2.30, 1.30, 0.02), (0.90, 0.90, 0.94, 1.0),
                     roll=s * 0.95, pitch=-0.30)
    make_blob("Am_Sheet_Billow", (lx - 0.6, ly - 1.30, 0.55), 0.30, (0.90, 0.90, 0.94, 1.0), noise=0.1, seed=4, squash=0.4)
    fx, fy = lx - 1.6, 1.0
    make_cyl("Am_Fan_Base", (fx, fy, 0.03), 0.22, 0.06, (0.80, 0.80, 0.80, 1.0), segments=12)
    make_cyl("Am_Fan_Pole", (fx, fy, 0.55), 0.025, 1.00, (0.80, 0.80, 0.80, 1.0), segments=8)
    make_rot_box("Am_Fan_Hub", (fx, fy + 0.10, 1.10), (0.16, 0.20, 0.16), (0.80, 0.80, 0.80, 1.0), yaw=0.6)
    make_rot_box("Am_Fan_Cage", (fx + 0.06, fy + 0.20, 1.10), (0.60, 0.04, 0.60), (0.70, 0.72, 0.74, 1.0), yaw=0.6)
    # the glass door out to the deck, the deck, the jetted water, the fence
    make_box("Am_Deck", (51.5, 3.2, -0.02), (9.0, 10.0, 0.06), (0.46, 0.36, 0.26, 1.0))
    for k in range(20):
        make_box(f"Am_Deck_Seam_{k}", (47.2 + k * 0.45, 3.2, 0.011), (0.012, 10.0, 0.002), (0.34, 0.26, 0.18, 1.0))
    tx, ty = 51.4, 3.6
    make_box("Tub_Shell", (tx, ty, 0.45), (2.3, 2.3, 0.90), (0.40, 0.34, 0.28, 1.0))
    make_box("Tub_Water", (tx, ty, 0.86), (1.96, 1.96, 0.04), (0.30, 0.60, 0.70, 1.0))
    make_box("Tub_Rim", (tx, ty, 0.905), (2.34, 2.34, 0.01), (0.86, 0.84, 0.80, 1.0))
    for k in range(10):
        make_blob(f"Tub_Bubble_{k}", (tx - 0.7 + (k * 37 % 14) / 10.0, ty - 0.7 + (k * 53 % 14) / 10.0, 0.89), 0.05,
                  (0.80, 0.92, 0.96, 1.0), noise=0.1, seed=k, squash=0.5)
    make_cyl("Tub_Bottle", (tx + 1.0, ty - 0.95, 1.02), 0.045, 0.22, (0.40, 0.24, 0.10, 1.0), segments=10)
    for k in range(3):
        make_chamfer_box(f"Tub_Towel_{k}", (tx - 1.5, ty - 0.8 + k * 0.5, 0.04), (0.50, 0.40, 0.06),
                         (0.94, 0.94, 0.92, 1.0), chamfer=0.02)
    for side, (x, y, w, d) in {"E": (56.0, 3.2, 0.10, 10.0), "N": (51.5, 8.2, 9.0, 0.10), "S": (51.5, -1.8, 9.0, 0.10)}.items():
        make_box(f"Am_Fence_{side}", (x, y, 0.9), (w, d, 1.8), (0.26, 0.22, 0.18, 1.0))


def main():
    clear_scene()
    build_shell()
    build_entry_kitchen()
    build_living()
    build_hall_rooms()
    build_game_room()
    build_amanda()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/chau_house.glb"))
    print(f"\n[build_chau_house] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
