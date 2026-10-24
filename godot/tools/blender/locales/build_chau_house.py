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

PASS 146 (2026-10-23) — the user: "Chau house has tall ceilings and wide
tall windows, it's a luxury home." H 2.9 -> 3.9; every outside window
widened and taken down to a 0.45 m sill (the living room's front one 4.4 m
wide, 2.8 m tall); the front door 2.5 m under a glass transom; Steven's
blinds the kit's; crown molding round the great room, a pendant in the
entry.

Blender: x east, y north, z up; Godot (x, z, -y).

Vol 4's "the wasted sentiment" is Steven's room too (the user, 2026-10-18:
"Steven Chau lives at the Chau house, yes"): the armchair he fell asleep
twisted in, `chau_steven_room`.

PASS 164 (2026-10-24) — THE LUXURY FINISH. The pass-146 shell rendered as
a bare box: a 22 x 14 great room with one couch, a 1 m seam grid that read
as tile, flat walls, a flat ceiling. Now: wide-plank white oak (seams at
0.16 m with staggered ends) under the great room, hall and bedrooms;
coffered beams and recessed cans over the living room; a stone fireplace
with a mantel and chimney breast on the living room's W wall; a six-chair
dining table under a chandelier at the tall front window; drapes on the
living room's N windows and the front one; large canvases on the N and E
walls; an entry mirror over a console; Steven's armchair as a real chair,
a bookcase of games, a rug and a poster; a soaking tub and a tile wainscot
in the bath. "Six month old eight hundred thousand dollar home."

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
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window, make_blinds, make_crown_molding, make_curtains
from _props.views import make_view
from _props.furniture import make_bed, make_chair, make_lamp, make_sofa, make_pendant, make_table
from _props.detail import make_wall_outlet, make_light_switch

X0, X1, D, H, T = -10.0, 12.0, 14.0, 3.9, 0.20   # pass 146 (the user: "tall ceilings and wide tall windows, it's a luxury home"): was 2.9
WALL = (0.90, 0.88, 0.84, 1.0); BASE = (0.70, 0.68, 0.64, 1.0)
PAL = {"wall": WALL, "baseboard": BASE}
OAK_FLOOR = (0.64, 0.55, 0.43, 1.0); OAK_SEAM = (0.52, 0.44, 0.34, 1.0)   # pass 164: white oak, cooler than the orange it rendered
STONE = (0.58, 0.56, 0.52, 1.0); STONE_LT = (0.68, 0.66, 0.62, 1.0)
DRAPE = (0.46, 0.50, 0.56, 1.0)
PAINT = (0.92, 0.91, 0.88, 1.0)
TILE = (0.86, 0.84, 0.80, 1.0); TILE_SEAM = (0.74, 0.72, 0.68, 1.0)
DOOR = (0.92, 0.90, 0.86, 1.0)
LEATHER = (0.36, 0.24, 0.18, 1.0); SOFA = (0.80, 0.78, 0.72, 1.0)
FLAT = (0.08, 0.08, 0.09, 1.0)
DAYGLASS = (0.80, 0.86, 0.90, 0.25)
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
    """A day window in an outside wall (pass 145, 2026-10-23): the kit
    window's frame, sill and casing with a tinted pane (LocaleGlass makes
    it glass) and the yard behind it. Draft 1's pane was an opaque white
    sheet ("our panes are opaque" — true before 2026-10-02), so the new
    house's windows were eight lit panels with nothing outside them."""
    face = line + sign * T / 2.0
    if along == 'X':
        a = (c, face, z)
        make_box(name + "_Pane", (c, line, z), (w, 0.02, h), DAYGLASS)
    else:
        a = (face, c, z)
        make_box(name + "_Pane", (line, c, z), (0.02, w, h), DAYGLASS)
    make_window(name, a, width=w - 0.10, height=h - 0.08, axis=along, room_dir=sign, see_through=True)


def build_shell():
    cx, cy = (X0 + X1) / 2.0, D / 2.0
    # (pass 164: the kit floor's 1 m seam grid read as tile — a plain slab, the
    # planks laid over it by build_luxury_finish)
    make_box("Chau_Floor_Slab", (cx, cy, -0.05), (X1 - X0 + 0.4, D + 0.4, 0.10), OAK_FLOOR)
    make_box("Chau_Ceil", (cx, cy, H + 0.04), (X1 - X0 + 0.4, D + 0.4, 0.08), (0.94, 0.94, 0.92, 1.0))
    # outside walls: the front door on the S, windows round
    make_wall_with_openings("Chau_Wall_S", (cx, 0.0, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(-2.0, 1.50, 1.1, 3.0), (-7.0, 1.95, 2.6, 2.3), (2.4, 1.85, 4.4, 2.8)])
    make_box("Front_Door", (-2.0, 0.0, 1.25), (1.08, 0.06, 2.48), (0.40, 0.30, 0.22, 1.0))
    make_box("Front_Door_Lite", (-2.0, 0.0, 2.77), (1.10, 0.03, 0.46), DAYGLASS)   # the transom over the tall door
    make_box("Front_Door_Lite_Bar", (-2.0, 0.0, 2.52), (1.10, 0.20, 0.04), (0.30, 0.30, 0.32, 1.0))
    window("Win_Kitchen_S", 'X', 0.0, -7.0, z=1.95, w=2.6, h=2.3, sign=1)
    window("Win_Living_S", 'X', 0.0, 2.4, z=1.85, w=4.4, h=2.8, sign=1)
    make_wall_with_openings("Chau_Wall_N", (cx, D, 0), length=X1 - X0 + 0.4, height=H, thickness=T, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(-2.3, 1.85, 2.6, 2.8), (4.5, 1.85, 2.2, 2.8)])
    window("Win_Living_N1", 'X', D, -2.3, z=1.85, w=2.6, h=2.8, sign=-1)
    window("Win_Living_N2", 'X', D, 4.5, z=1.85, w=2.2, h=2.8, sign=-1)
    make_wall_with_openings("Chau_Wall_W", (X0, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(8.6, 1.75, 2.0, 2.4)])
    window("Win_Game_W", 'Y', X0, 8.6, z=1.75, w=2.0, h=2.4, sign=1)
    # what the windows see: the street out front, the back yard, the side
    # yards and the neighbours close (a new development, lots shoulder to
    # shoulder)
    make_view("Chau_View_S", "S", -T / 2.0, cx, kind="front", ground_z=0.0, span=X1 - X0 + 2.0, seed=3)
    make_view("Chau_View_N", "N", D + T / 2.0, cx, kind="back", ground_z=0.0, span=X1 - X0 + 0.4, seed=4)
    make_view("Chau_View_E", "E", X1 + T / 2.0, cy, kind="side", ground_z=0.0, span=D + 0.4, seed=5)
    make_view("Chau_View_W", "W", X0 - T / 2.0, cy, kind="side", ground_z=0.0, span=D + 0.4, seed=6)
    make_wall_with_openings("Chau_Wall_E", (X1, cy, 0), length=D + 0.4, height=H, thickness=T, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(6.0, 1.70, 2.2, 2.4), (11.4, 1.70, 2.2, 2.4)])
    window("Win_Steven_E", 'Y', X1, 6.0, z=1.70, w=2.2, h=2.4, sign=-1)
    window("Win_Mom_E", 'Y', X1, 11.4, z=1.70, w=2.2, h=2.4, sign=-1)
    # Steven's blinds ("Light comes in through window blinds"), drawn most of
    # the way down the tall window
    make_blinds("Blind_Steven", (X1 - T / 2.0, 6.0, 1.70), width=2.10, height=2.32, axis='Y', room_dir=-1,
                color=(0.94, 0.94, 0.92, 1.0), raised_frac=0.15)
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


def build_great_room_trim():
    """The luxury home's finish (pass 146): crown molding round the great
    room (entry, kitchen, living) at the 3.9 m ceiling, and a pendant over
    the entry."""
    pal = {"wood": (0.96, 0.95, 0.92, 1.0)}
    wx0, wx1 = X0 + T / 2.0, HALL_X0 - 0.07
    make_crown_molding("Crown_S", wall_x=(wx0 + wx1) / 2.0, wall_y=T / 2.0, length=wx1 - wx0, axis='X', ceil_z=H, palette=pal)
    make_crown_molding("Crown_N", wall_x=(-4.0 + 0.07 + wx1) / 2.0, wall_y=D - T / 2.0, length=wx1 - (-4.0 + 0.07), axis='X',
                       ceil_z=H, palette=pal)
    make_crown_molding("Crown_W", wall_x=wx0, wall_y=(T / 2.0 + 6.0 - 0.07) / 2.0, length=6.0 - 0.07 - T / 2.0, axis='Y', ceil_z=H,
                       palette=pal)
    make_crown_molding("Crown_E", wall_x=wx1, wall_y=D / 2.0, length=D - T, axis='Y', ceil_z=H, palette=pal)
    make_pendant("Entry_Pendant", -2.0, 1.6, bulb_z=2.95, ceil_z=H, shade_col=(0.86, 0.84, 0.78, 1.0), shade_r=0.26)


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
    make_sofa("Couch", cx, cy, back="-Y", w=2.40, d=0.92, seats=3, color=SOFA, cushion_col=(0.84, 0.82, 0.76, 1.0),
              leg_col=(0.30, 0.24, 0.18, 1.0), arm="track", pillows=((0.62, 0.30, 0.28, 1.0), (0.86, 0.84, 0.78, 1.0)))
    make_box("Coffee_Table", (cx, 9.0, 0.22), (1.4, 0.7, 0.44), (0.40, 0.30, 0.22, 1.0))
    for k, (x, y) in enumerate(((cx - 2.3, 8.6), (cx + 2.3, 8.6))):
        make_sofa(f"Armchair_{k}", x, y, back=("-X", "+X")[k], w=0.92, d=0.88, seats=1, color=LEATHER, arm="roll",
                  leg_col=(0.24, 0.18, 0.14, 1.0))
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
        make_chamfer_box(f"Towel_Pile_{k}", (10.9 + (k % 2) * 0.14, 1.0 + k * 0.08, 0.04 + k * 0.06), (0.56, 0.40, 0.07),
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
    make_blob("Steven_Clothes", (10.0, 5.9, 0.10), 0.28, (0.36, 0.34, 0.30, 1.0), noise=0.3, seed=3, squash=0.4)
    # vol 4's "the wasted sentiment" (2026-10-18; the user: "Steven Chau lives
    # at the Chau house, yes"): "He was still tired and stiff from falling
    # asleep like he did, twisted in a tight spot" — a small armchair in the
    # SE corner by the blinds, the blanket twisted in it that morning
    ax, ay = X1 - 0.07 - 0.45, 3.6 + 0.07 + 0.45
    # (pass 164: three boxes → the kit's armchair, its back to the E wall)
    make_sofa("Steven_Armchair", ax, ay, back="+X", w=0.88, d=0.86, seats=1, color=(0.30, 0.34, 0.40, 1.0),
              cushion_col=(0.36, 0.40, 0.46, 1.0), leg_col=(0.24, 0.20, 0.16, 1.0), arm="track", seat_h=0.42)
    make_rot_box("Steven_Blanket_Twisted__chau_steven_room", (ax - 0.05, ay, 0.47), (0.56, 0.60, 0.06), (0.60, 0.30, 0.28, 1.0), yaw=0.5)
    make_box("Steven_Controller_On_Arm__chau_steven_room", (ax - 0.05, ay + 0.05, 0.515), (0.14, 0.06, 0.03), (0.14, 0.14, 0.16, 1.0))   # on the blanket (pass 164)
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


def build_luxury_finish():
    """Pass 164: what makes the shell an eight-hundred-thousand-dollar
    house — floors, ceiling, fireplace, dining, drapes, art, the bath's
    tub. Every piece is placed clear of what the text put here."""
    # wide-plank white oak: long seams every 0.16 m (planks run E-W), end
    # seams staggered. Laid where there is no tile or carpet: the entry and
    # hall side (y 0..3.6, x -4..7.6), the middle band (y 3.6..6, x -4..12),
    # the living room, Steven's and Mrs. Chau's rooms (y 6..14, x -4..12).
    bands = ((0.0, 3.6, -4.0, 7.6), (3.6, 6.0, -4.0, 12.0), (6.0, 14.0, -4.0, 12.0))
    k = 0
    for (y0, y1, x0, x1) in bands:
        n = int((y1 - y0) / 0.16)
        for i in range(n):
            y = y0 + 0.08 + i * 0.16
            make_box(f"_Stock_Plank_Seam_{k}", ((x0 + x1) / 2.0, y, 0.0025), (x1 - x0, 0.012, 0.001), OAK_SEAM)
            # two end seams per row, staggered by row
            for j in range(2):
                ex = x0 + 1.1 + ((i * 0.7 + j * 2.9) % (x1 - x0 - 2.2))
                make_box(f"_Stock_Plank_End_{k}_{j}", (ex, y - 0.08, 0.0025), (0.012, 0.15, 0.001), OAK_SEAM)
            k += 1
    # the living room ceiling: three coffered beams E-W, recessed cans between
    for i, y in enumerate((8.0, 10.0, 12.0)):
        make_box(f"Ceiling_Beam_{i}", (1.1, y, H - 0.14), (9.3, 0.24, 0.28), PAINT)   # x -3.55..5.75: short of the chimney breast and the E crown
    for i, (x, y) in enumerate(((-1.5, 9.0), (1.0, 9.0), (3.5, 9.0), (-1.5, 11.0), (1.0, 11.0), (3.5, 11.0), (-2.0, 3.6), (0.0, 4.8))):
        make_cyl(f"Recessed_Can_{i}", (x, y, H - 0.004), 0.07, 0.008, (0.98, 0.96, 0.90, 1.0), segments=12)
    # the fireplace on the living room's W wall (the game-room wall, face x -3.93)
    fx, fy = -3.93, 12.0
    make_box("Fireplace_Surround", (fx + 0.15, fy, 0.70), (0.30, 2.0, 1.40), STONE)
    make_box("Fireplace_Firebox", (fx + 0.305, fy, 0.55), (0.02, 0.90, 0.80), (0.08, 0.07, 0.07, 1.0))
    make_box("Fireplace_Mantel", (fx + 0.18, fy, 1.44), (0.36, 2.2, 0.08), STONE_LT)
    make_box("Fireplace_Breast", (fx + 0.13, fy, (1.48 + H) / 2.0), (0.26, 2.0, H - 1.48), STONE_LT)
    make_box("Fireplace_Hearth", (fx + 0.60, fy, 0.02), (0.60, 2.2, 0.04), STONE)   # x -3.63..-3.03, in front of the surround
    for i, (dy, h, r, col) in enumerate(((-0.6, 0.26, 0.04, (0.30, 0.34, 0.30, 1.0)), (0.0, 0.18, 0.05, (0.86, 0.82, 0.74, 1.0)),
                                         (0.55, 0.32, 0.05, (0.60, 0.36, 0.26, 1.0)))):
        make_cyl(f"Mantel_Object_{i}", (fx + 0.31, fy + dy, 1.48 + h / 2.0), r, h, col, segments=10)   # on the mantel's front half, clear of the breast
    # the dining set at the tall front window: six chairs, a chandelier
    tx, ty = 2.4, 2.6
    make_table("Dining_Table", tx, ty, w=2.2, d=1.0, h=0.76, wood=(0.34, 0.26, 0.20, 1.0))
    for i, x in enumerate((tx - 0.7, tx, tx + 0.7)):
        make_chair(f"Dining_Chair_S_{i}", x, ty - 0.80, yaw=0.0, wood=(0.34, 0.26, 0.20, 1.0), seat_col=(0.72, 0.70, 0.64, 1.0))
        make_chair(f"Dining_Chair_N_{i}", x, ty + 0.80, yaw=math.pi, wood=(0.34, 0.26, 0.20, 1.0), seat_col=(0.72, 0.70, 0.64, 1.0))
    make_pendant("Dining_Chandelier", tx, ty, bulb_z=2.45, ceil_z=H, shade_col=(0.92, 0.90, 0.84, 1.0), shade_r=0.34)
    make_cyl("Dining_Bowl", (tx, ty, 0.78), 0.16, 0.05, (0.92, 0.92, 0.90, 1.0), segments=14)
    # drapes: the living room's two N windows and the big front window
    make_curtains("Drape_N1", (-2.3, D - T / 2.0, 1.85), width=2.6, height=2.8, axis='X', room_dir=-1, color=DRAPE)
    make_curtains("Drape_N2", (4.5, D - T / 2.0, 1.85), width=2.2, height=2.8, axis='X', room_dir=-1, color=DRAPE)
    make_curtains("Drape_Front", (2.4, T / 2.0, 1.85), width=4.4, height=2.8, axis='X', room_dir=+1, color=DRAPE)
    # art: two tall canvases over the surround towers on the N wall, one long
    # one on the E (hall) wall, abstract colour fields in dark frames
    def canvas(prefix, center, size, along, fields):
        cx_, cy_, cz_ = center
        w, h = size
        if along == 'X':
            make_box(f"{prefix}_Frame", (cx_, cy_, cz_), (w + 0.08, 0.04, h + 0.08), (0.14, 0.12, 0.11, 1.0))
            make_box(f"{prefix}_Canvas", (cx_, cy_ - 0.025, cz_), (w, 0.01, h), (0.90, 0.88, 0.84, 1.0))
            for i, (fx_, fz_, fw_, fh_, col) in enumerate(fields):
                make_box(f"{prefix}_Field_{i}", (cx_ + fx_, cy_ - 0.032, cz_ + fz_), (fw_, 0.004, fh_), col)
        else:
            make_box(f"{prefix}_Frame", (cx_, cy_, cz_), (0.04, w + 0.08, h + 0.08), (0.14, 0.12, 0.11, 1.0))
            make_box(f"{prefix}_Canvas", (cx_ - 0.025, cy_, cz_), (0.01, w, h), (0.90, 0.88, 0.84, 1.0))
            for i, (fx_, fz_, fw_, fh_, col) in enumerate(fields):
                make_box(f"{prefix}_Field_{i}", (cx_ - 0.032, cy_ + fx_, cz_ + fz_), (0.004, fw_, fh_), col)
    canvas("Art_N_W", (-0.3, D - T / 2.0 - 0.02, 2.5), (0.8, 1.3), 'X',
           ((0.0, 0.25, 0.7, 0.5, (0.20, 0.28, 0.44, 1.0)), (-0.1, -0.3, 0.5, 0.4, (0.70, 0.42, 0.26, 1.0))))
    canvas("Art_N_E", (2.6, D - T / 2.0 - 0.02, 2.5), (0.9, 1.3), 'X',
           ((0.0, 0.1, 0.7, 0.9, (0.26, 0.30, 0.28, 1.0)), (0.15, -0.4, 0.3, 0.2, (0.86, 0.78, 0.40, 1.0))))
    canvas("Art_E", (HALL_X0 - 0.07 - 0.02, 10.5, 2.1), (2.0, 1.2), 'Y',
           ((0.0, 0.0, 1.8, 0.5, (0.60, 0.62, 0.66, 1.0)), (-0.5, 0.0, 0.5, 1.0, (0.24, 0.20, 0.18, 1.0))))
    # the entry: a mirror over a console between the door and the window
    make_table("Entry_Console", -0.6, T / 2.0 + 0.20, w=1.0, d=0.34, h=0.82, wood=(0.26, 0.20, 0.16, 1.0))
    make_box("Entry_Mirror_Frame", (-0.6, T / 2.0 + 0.02, 1.80), (0.84, 0.04, 1.30), (0.70, 0.62, 0.40, 1.0))
    make_box("Entry_Mirror", (-0.6, T / 2.0 + 0.045, 1.80), (0.74, 0.01, 1.20), (0.72, 0.78, 0.82, 1.0))
    make_lathe("Entry_Vase", (-0.6, T / 2.0 + 0.20, 0.818), [(0.0, 0.0), (0.07, 0.0), (0.09, 0.14), (0.04, 0.26), (0.05, 0.30), (0.0, 0.30)],
               (0.30, 0.34, 0.40, 1.0), segments=12)
    # Steven's room: a rug, a bookcase of games on the N wall, a poster by the door
    make_box("Steven_Rug", (8.8, 6.9, 0.006), (1.4, 1.2, 0.012), (0.34, 0.30, 0.40, 1.0))
    bcx, bcy = 9.2, 9.0 - 0.07 - 0.17
    dark = (0.26, 0.26, 0.28, 1.0)
    make_box("Steven_Bookcase_Back", (bcx, bcy + 0.155, 0.90), (0.90, 0.03, 1.80), dark)
    for sgn, tag in ((-1, "W"), (1, "E")):
        make_box(f"Steven_Bookcase_Side_{tag}", (bcx + sgn * 0.435, bcy, 0.90), (0.03, 0.34, 1.80), dark)
    make_box("Steven_Bookcase_Top", (bcx, bcy, 1.785), (0.90, 0.34, 0.03), dark)
    for i in range(4):
        make_box(f"Steven_Shelf_{i}", (bcx, bcy, 0.40 + i * 0.44), (0.84, 0.31, 0.02), dark)
        for j in range(5):
            make_box(f"_Stock_Game_Box_{i}_{j}", (bcx - 0.34 + j * 0.17, bcy - 0.06, 0.41 + i * 0.44 + 0.10),
                     (0.14, 0.10, 0.20), ((0.20, 0.30, 0.60, 1.0), (0.70, 0.20, 0.20, 1.0), (0.90, 0.86, 0.70, 1.0))[(i + j) % 3])
    make_box("Steven_Poster", (HALL_X1 + 0.07 + 0.012, 8.0, 1.80), (0.02, 0.60, 0.85), (0.16, 0.18, 0.26, 1.0))
    make_box("Steven_Poster_Art", (HALL_X1 + 0.07 + 0.024, 8.0, 1.85), (0.004, 0.44, 0.50), (0.80, 0.50, 0.26, 1.0))
    # the bath: a soaking tub along the S wall, a tile wainscot on the W and S
    tbx, tby = 9.25, 0.58
    make_chamfer_box("Bath_Tub", (tbx, tby, 0.29), (1.70, 0.82, 0.58), (0.96, 0.96, 0.95, 1.0), chamfer=0.06)
    make_box("Bath_Tub_Water", (tbx, tby, 0.57), (1.46, 0.60, 0.02), (0.80, 0.86, 0.88, 1.0))
    make_cyl("Bath_Tub_Faucet", (tbx + 0.70, tby, 0.72), 0.02, 0.28, (0.74, 0.74, 0.76, 1.0), segments=8)
    make_box("Bath_Wainscot_W", (HALL_X1 + 0.07 + 0.015, 1.8, 0.60), (0.02, 3.4, 1.20), (0.78, 0.80, 0.82, 1.0))
    make_box("Bath_Wainscot_S", (9.78, 0.11, 0.60), (4.22, 0.02, 1.20), (0.78, 0.80, 0.82, 1.0))


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
    build_great_room_trim()
    build_living()
    build_hall_rooms()
    build_game_room()
    build_luxury_finish()
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
