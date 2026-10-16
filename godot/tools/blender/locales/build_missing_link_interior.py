"""missing_link_interior — vol1 interlude locale + vol7's Saturday diner.
THE MISSING LINK: a roadside bus-depot diner (the Shillelagh stops here
once a day), and a BIGFOOT diner (the user, 2026-10-09: "Missing Link
diner is bigfoot themed" — the creature "halfway between a man and an
ape" painted under the name on the enamel sign is a Sasquatch).

Canon (vol1_missing_link / vol1_link_*): "a counter with five stools,
four booths against the front windows, a jukebox in the corner blinking
through its red eye. The fluorescents hum." The stool "spins a
half-turn ... pointed exactly at the swinging door to the kitchen."
"The booth in the corner has a wall of framed photographs above it.
None of them are labeled ... All of them are square." The menu is
laminated and typed. vol7_ch16: "The booths along the front window were
full. The back booth was occupied ... He sat at the counter on the
third stool."

DRAFT 4 (2026-10-09, the overnight run; CLAUDE.md "build big"). Draft
3's targets led with "reconcile this plan with build_missing_link_
exterior (the exterior's door is at the diner's EAST end, this room's is
centred, and the exterior body is 8 m to this room's 7 m)". Both are one
building now: 10 x 7 m inside (exterior x -6.5..3.5, front at y 8, the
kitchen behind), the door at the EAST end of the front, and
    interior (x, y) = exterior (x + 1.5, y - 8.0)
so every pump, the awning, the pole sign and the carved Sasquatch by the
door stand where the lot camera sees them.
  - four booths under four front windows (the exterior's four windows
    are these four), benches facing across tables toward the glass;
  - THE CORNER BOOTH: the back booth in the NW corner against the W
    wall, the wall of square photographs above it, the polaroid taped
    among them;
  - the counter with five stools; the third stool points at the
    kitchen door in the N wall; the back-bar either side of the door
    (coffee, mugs, the register / the pie case, the shake mixer);
  - the jukebox on the E wall by the door, blinking;
  - BIGFOOT: a shaggy life-size Sasquatch on the W wall with a
    SASQUATCH CROSSING sign over it, plaster footprint casts in a
    shadow box, the silhouette over the kitchen door, the menu board's
    logo, a "research fund" tip jar; knotty-pine wainscot (Pacific
    northwest roadside), checker tile down the aisle;
  - outside the glass: the apron, the pumps, the depot awning and its
    bench east of the door, the pole sign, the road, the treeline.

Coordinate frame: Blender Z-up. y=0 is the front (south) wall's centre
line; +Y runs back to the kitchen wall (y=7). glTF export remaps to
Godot (x, z, -y).

Draft 5 targets: the kitchen behind the door as a glimpse (the porthole
lit, a cook's shape); rain on the glass (alpha streak cards); the
photographs as their seven subjects; the young man at the bench outside
the E windows at night; Deck framing of the door preset and the corner
booth.
"""
import math
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe, make_tube, export_glb
from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_light_switch, make_wall_outlet
from _props.structure import make_floor, make_wall, make_ceiling, make_case_shell, make_wall_with_openings
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.creatures import make_bigfoot
from _props.vehicles import make_car

ROOM_W = 10.0; ROOM_D = 7.0; CEIL = 2.8
XW, XE, YS, YN = -ROOM_W / 2.0 + 0.10, ROOM_W / 2.0 - 0.10, 0.10, ROOM_D - 0.10
EXT_DX, EXT_DY = 1.5, -8.0          # interior = exterior + this
PAL_WALL = {"wall": (0.80, 0.74, 0.58, 1.0), "baseboard": (0.34, 0.28, 0.22, 1.0)}
COL_FLOOR = (0.72, 0.68, 0.60, 1.0); COL_SEAM = (0.34, 0.30, 0.26, 1.0)
COL_TILE_CHECK = (0.20, 0.18, 0.16, 1.0)
COL_LAMINATE = (0.86, 0.82, 0.70, 1.0); COL_STEEL = (0.70, 0.72, 0.74, 1.0)
COL_CHROME = (0.78, 0.80, 0.84, 1.0); COL_VINYL_RED = (0.72, 0.22, 0.20, 1.0)
COL_VINYL_DK = (0.42, 0.14, 0.14, 1.0); COL_WOOD = (0.46, 0.32, 0.22, 1.0)
COL_PINE = (0.70, 0.52, 0.32, 1.0); COL_PINE_KNOT = (0.46, 0.30, 0.18, 1.0)
COL_GLASS = (0.78, 0.84, 0.86, 0.45); COL_MUG = (0.90, 0.88, 0.82, 1.0)
COL_COFFEE = (0.20, 0.12, 0.08, 1.0); COL_PIE = (0.86, 0.62, 0.34, 1.0)
COL_JUKE = (0.42, 0.24, 0.18, 1.0); COL_JUKE_GLOW = (0.96, 0.72, 0.34, 1.0)
COL_RED_EYE = (0.94, 0.20, 0.16, 1.0); COL_BLACK = (0.14, 0.12, 0.12, 1.0)
COL_ASPHALT = (0.16, 0.16, 0.18, 1.0); COL_PUMP = (0.74, 0.20, 0.18, 1.0)
COL_SIGN_YEL = (0.92, 0.78, 0.20, 1.0); COL_PLASTER = (0.88, 0.86, 0.80, 1.0)

WIN_XS = (-3.9, -2.0, -0.1, 1.8)          # the four booths, the four windows
WIN_Z, WIN_W, WIN_H = 1.575, 1.40, 1.25   # sill 0.95, head 2.20
DOOR = (3.9, 1.075, 0.96, 2.15)           # front door, the diner's east end
KDOOR = (0.6, 1.025, 0.96, 2.05)          # the kitchen door, behind the third stool
COUNTER_X, COUNTER_Y = 0.6, 4.95
STOOL_XS = (-1.3, -0.35, 0.6, 1.55, 2.5)


def _ext(x, y):
    return x + EXT_DX, y + EXT_DY


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # checker tile down the aisle between the booths and the stools
    for j in range(5):
        for i in range(23):
            if (i + j) % 2 == 0:
                make_box(f"CheckTile_{i}_{j}", (-4.4 + i * 0.4, 1.80 + j * 0.4, 0.011), (0.4, 0.4, 0.002), COL_TILE_CHECK)
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=-1, openings=[KDOOR])
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W + 0.4, height=CEIL, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=+1,
                            openings=[(x, WIN_Z, WIN_W, WIN_H) for x in WIN_XS] + [DOOR])
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
                 with_grid=False, with_stains=True, palette={"tile": (0.86, 0.84, 0.76, 1.0)})
    # knotty-pine wainscot (W, E, the front under the windows) + a chrome rail
    for nm, c, sz in (("W", (XW + 0.01, ROOM_D / 2.0, 0.50), (0.02, ROOM_D - 0.2, 1.0)),
                      ("E", (XE - 0.01, ROOM_D / 2.0, 0.50), (0.02, ROOM_D - 0.2, 1.0)),
                      ("S", ((XW + DOOR[0] - DOOR[2] / 2.0) / 2.0, YS + 0.01, 0.47), (DOOR[0] - DOOR[2] / 2.0 - XW, 0.02, 0.94))):
        make_box(f"Wainscot_{nm}", c, sz, COL_PINE)
    for nm, c, sz in (("W", (XW + 0.025, ROOM_D / 2.0, 1.01), (0.03, ROOM_D - 0.2, 0.025)),
                      ("E", (XE - 0.025, ROOM_D / 2.0, 1.01), (0.03, ROOM_D - 0.2, 0.025))):
        make_box(f"Wainscot_Rail_{nm}", c, sz, COL_CHROME)
    k = 0
    for wx_, along in ((XW + 0.021, 'Y'), (XE - 0.021, 'Y')):
        for i in range(10):
            yy = 0.5 + i * 0.66 + (0.17 if k % 2 else 0.0)
            make_box(f"Wainscot_Knot_{k}_{i}", (wx_, yy, 0.25 + 0.5 * ((i * 7 + k) % 3) / 2.0), (0.002, 0.05, 0.03), COL_PINE_KNOT)
        k += 1
    # the front door: glazed, closed, the bell over it (canon: the bell
    # "is unsubtle about your leaving")
    dx = DOOR[0]
    for nm, ox in (("L", -0.44), ("R", 0.44)):
        make_box(f"FrontDoor_Stile_{nm}", (dx + ox, 0.0, 1.07), (0.06, 0.05, 2.14), COL_CHROME)
    make_box("FrontDoor_Rail_T", (dx, 0.0, 2.11), (0.82, 0.05, 0.06), COL_CHROME)
    make_box("FrontDoor_Rail_B", (dx, 0.0, 0.14), (0.82, 0.05, 0.24), COL_CHROME)
    make_box("FrontDoor_Glass", (dx, 0.0, 1.17), (0.82, 0.02, 1.70), COL_GLASS)
    make_box("FrontDoor_PushBar", (dx, 0.035, 1.05), (0.88, 0.02, 0.05), COL_CHROME)
    make_box("FrontDoor_Bell_Bracket", (dx + 0.30, YS + 0.04, 2.30), (0.03, 0.08, 0.03), COL_CHROME)
    make_cyl("FrontDoor_Bell", (dx + 0.30, YS + 0.08, 2.255), 0.04, 0.06, (0.72, 0.58, 0.28, 1.0), segments=8)
    make_box("EntryMat", (dx, 0.70, 0.013), (1.2, 0.9, 0.006), (0.24, 0.22, 0.20, 1.0))


def _booth_pair(tag, bx):
    """A front booth under its window: two benches facing E-W across a
    table that meets the glass."""
    for sgn, side in ((-1, "W"), (1, "E")):
        sx = bx + sgn * 0.60
        make_chamfer_box(f"Booth_{tag}_Seat_{side}", (sx, 0.82, 0.44), (0.42, 1.30, 0.10), COL_VINYL_RED, chamfer=0.03)
        make_box(f"Booth_{tag}_Plinth_{side}", (sx + sgn * 0.02, 0.82, 0.195), (0.38, 1.24, 0.39), COL_VINYL_DK)
        make_chamfer_box(f"Booth_{tag}_Back_{side}", (bx + sgn * 0.86, 0.82, 0.83), (0.10, 1.30, 0.70), COL_VINYL_DK, chamfer=0.03)
        make_tube(f"Booth_{tag}_Rail_{side}", [(bx + sgn * 0.86, 0.17, 1.19), (bx + sgn * 0.86, 1.47, 1.19)], 0.018, COL_CHROME, segments=6)
    make_lathe(f"Booth_{tag}_Table_Post", (bx, 0.75, 0.011), [(0.16, 0.0), (0.16, 0.015), (0.05, 0.03), (0.03, 0.05), (0.03, 0.705)], COL_CHROME, segments=10)
    make_box(f"Booth_{tag}_Table", (bx, 0.72, 0.74), (0.72, 0.95, 0.05), COL_LAMINATE)
    make_tube(f"Booth_{tag}_Table_Band", [(bx - 0.365, 0.245, 0.74), (bx + 0.365, 0.245, 0.74), (bx + 0.365, 1.195, 0.74), (bx - 0.365, 1.195, 0.74), (bx - 0.365, 0.245, 0.74)], 0.012, COL_CHROME, segments=6)
    make_box(f"Booth_{tag}_Napkin", (bx, 0.36, 0.805), (0.10, 0.07, 0.08), COL_CHROME)
    make_cyl(f"Booth_{tag}_Ketchup", (bx + 0.12, 0.36, 0.83), 0.025, 0.13, COL_VINYL_RED, segments=8)
    make_cyl(f"Booth_{tag}_Sugar", (bx - 0.12, 0.36, 0.82), 0.035, 0.11, COL_GLASS, segments=8)
    make_cyl(f"Booth_{tag}_Mug", (bx - 0.15, 0.92, 0.81), 0.04, 0.09, COL_MUG, segments=8)


def build_booths():
    for bi, bx in enumerate(WIN_XS):
        _booth_pair(str(bi), bx)
        # the window over each booth — frame ring + mullion (the wall is cut)
        for nm, c, sz in (("Head", (bx, 0.0, WIN_Z + WIN_H / 2.0 - 0.03), (WIN_W, 0.10, 0.06)),
                          ("Sill", (bx, 0.0, WIN_Z - WIN_H / 2.0 + 0.03), (WIN_W, 0.10, 0.06)),
                          ("JambW", (bx - WIN_W / 2.0 + 0.03, 0.0, WIN_Z), (0.06, 0.10, WIN_H - 0.12)),
                          ("JambE", (bx + WIN_W / 2.0 - 0.03, 0.0, WIN_Z), (0.06, 0.10, WIN_H - 0.12))):
            make_box(f"Window_{bi}_Frame_{nm}", c, sz, COL_CHROME)
        make_box(f"Window_{bi}_Glass", (bx, 0.0, WIN_Z), (WIN_W - 0.12, 0.02, WIN_H - 0.12), COL_GLASS)
        make_box(f"Window_{bi}_Mullion", (bx, 0.0, WIN_Z), (0.04, 0.05, WIN_H - 0.12), COL_CHROME)
        make_box(f"Window_{bi}_Sill_In", (bx, YS + 0.05, WIN_Z - WIN_H / 2.0 - 0.01), (WIN_W + 0.10, 0.12, 0.03), COL_LAMINATE)


def build_corner_booth():
    """THE CORNER BOOTH (vol1_link_booth; vol7's back booth): NW, against
    the W wall, benches facing N-S; the wall of square photographs over
    the table, the polaroid taped among them."""
    bx, by = -4.25, 5.95
    for sgn, side in ((-1, "S"), (1, "N")):
        sy = by + sgn * 0.60
        make_chamfer_box(f"BackBooth_Seat_{side}", (bx + 0.05, sy, 0.44), (1.30, 0.42, 0.10), COL_VINYL_RED, chamfer=0.03)
        make_box(f"BackBooth_Plinth_{side}", (bx + 0.05, sy + sgn * 0.02, 0.195), (1.24, 0.38, 0.39), COL_VINYL_DK)
        make_chamfer_box(f"BackBooth_Back_{side}", (bx + 0.05, by + sgn * 0.86, 0.83), (1.30, 0.10, 0.70), COL_VINYL_DK, chamfer=0.03)
    make_box("BackBooth_Table", (bx - 0.05, by, 0.74), (1.20, 0.72, 0.05), COL_LAMINATE)
    make_lathe("BackBooth_Table_Post", (bx, by, 0.011), [(0.16, 0.0), (0.16, 0.015), (0.05, 0.03), (0.03, 0.05), (0.03, 0.705)], COL_CHROME, segments=10)
    make_box("BackBooth_Napkin", (XW + 0.12, by, 0.805), (0.07, 0.10, 0.08), COL_CHROME)
    for mi, my in enumerate((by - 0.18, by + 0.20)):
        make_cyl(f"BackBooth_Mug_{mi}", (bx + 0.25, my, 0.81), 0.04, 0.09, COL_MUG, segments=8)
    # the photographs: square, unlabelled, none recent
    frames = ((5.30, 1.95, 0.30), (5.72, 2.02, 0.26), (6.12, 1.92, 0.34), (6.55, 2.00, 0.28),
              (5.40, 1.50, 0.32), (5.88, 1.55, 0.28), (6.40, 1.52, 0.30))
    for fi, (fy, fz, fs) in enumerate(frames):
        make_box(f"Photo_{fi}_Frame", (XW + 0.015, fy, fz), (0.03, fs, fs), COL_BLACK)
        make_box(f"Photo_{fi}_Print", (XW + 0.032, fy, fz), (0.004, fs - 0.06, fs - 0.06), ((0.52, 0.48, 0.42, 1.0), (0.40, 0.42, 0.40, 1.0), (0.58, 0.52, 0.44, 1.0))[fi % 3])
    # the polaroid, unframed, taped (the yellowed tape)
    make_box("Photo_Polaroid", (XW + 0.004, 6.10, 1.30), (0.004, 0.09, 0.11), (0.92, 0.90, 0.84, 1.0))
    make_box("Photo_Polaroid_Image", (XW + 0.007, 6.10, 1.31), (0.002, 0.075, 0.075), (0.30, 0.32, 0.34, 1.0))
    make_box("Photo_Polaroid_Tape", (XW + 0.008, 6.10, 1.36), (0.002, 0.05, 0.015), (0.86, 0.76, 0.46, 1.0))


def build_counter_and_stools():
    cx, cy = COUNTER_X, COUNTER_Y
    make_chamfer_box("Counter_Body", (cx, cy, 0.53), (4.80, 0.62, 1.02), COL_LAMINATE)
    make_box("Counter_Front", (cx, cy - 0.32, 0.53), (4.80, 0.02, 1.00), COL_STEEL)
    make_chamfer_box("Counter_Top", (cx, cy, 1.07), (5.00, 0.76, 0.05), COL_LAMINATE)
    make_cyl("Counter_EdgeBand", (cx, cy - 0.39, 1.05), 0.03, 4.80, COL_CHROME, axis='X', segments=8)
    make_box("Counter_Kick", (cx, cy - 0.32, 0.10), (4.80, 0.04, 0.18), COL_BLACK)
    for si, sx in enumerate(STOOL_XS):
        sy = cy - 0.85
        make_lathe(f"Stool_{si}_Base", (sx, sy, 0.0), [(0.19, 0.0), (0.19, 0.02), (0.12, 0.04), (0.05, 0.05), (0.035, 0.06)], COL_CHROME, segments=12)
        make_cyl(f"Stool_{si}_Post", (sx, sy, 0.39), 0.035, 0.66, COL_CHROME)
        make_lathe(f"Stool_{si}_FootRing", (sx, sy, 0.22), [(0.13, 0.0), (0.15, 0.012), (0.13, 0.024)], COL_CHROME, segments=12, loop=True)
        make_lathe(f"Stool_{si}_Seat", (sx, sy, 0.725), [(0.0, 0.0), (0.16, 0.0), (0.18, 0.02), (0.18, 0.05), (0.16, 0.07), (0.0, 0.075)], COL_VINYL_RED, segments=12)
    top = 1.095
    # the third stool's mug, and the second one "a foot to your left. Empty."
    for mi, (mx, full) in enumerate(((STOOL_XS[2], True), (STOOL_XS[2] - 0.30, False))):
        make_cyl(f"CounterMug_{mi}", (mx, cy - 0.12, top + 0.05), 0.045, 0.10, COL_MUG, segments=10)
        if full:
            make_cyl(f"CounterMug_{mi}_Coffee", (mx, cy - 0.12, top + 0.085), 0.038, 0.02, COL_COFFEE, segments=10)
    # the laminated menu, typed, standing in its chrome holder at the third stool
    make_box("Laminated_Menu", (STOOL_XS[2] + 0.22, cy + 0.02, top + 0.002), (0.24, 0.34, 0.004), (0.92, 0.90, 0.80, 1.0))
    make_box("Laminated_Menu_Header", (STOOL_XS[2] + 0.22, cy + 0.15, top + 0.0045), (0.18, 0.04, 0.001), COL_BLACK)
    for ci, cxx in enumerate((-1.6, 0.1, 1.9)):
        make_box(f"Napkin_{ci}", (cxx, cy + 0.05, top + 0.05), (0.10, 0.08, 0.10), COL_CHROME)
        make_cyl(f"Salt_{ci}", (cxx + 0.14, cy + 0.05, top + 0.045), 0.02, 0.09, COL_GLASS, segments=8)
        make_cyl(f"Pepper_{ci}", (cxx + 0.20, cy + 0.05, top + 0.045), 0.02, 0.09, COL_BLACK, segments=8)
        make_cyl(f"Ketchup_{ci}", (cxx - 0.14, cy + 0.05, top + 0.065), 0.025, 0.13, COL_VINYL_RED, segments=8)
    # cake stand + the lifted dome, the BIGFOOT RESEARCH FUND tip jar
    make_cyl("CakePlate", (2.7, cy - 0.02, top + 0.015), 0.22, 0.03, COL_CHROME, segments=16)
    make_cyl("CakePie", (2.7, cy - 0.02, top + 0.07), 0.20, 0.08, COL_PIE, segments=16)
    make_lathe("CakeDome", (2.75, cy + 0.25, top), [(0.20, 0.0), (0.20, 0.12), (0.16, 0.17), (0.07, 0.19), (0.03, 0.19), (0.03, 0.22), (0.0, 0.22)], COL_GLASS, segments=16)
    make_cyl("TipJar", (-1.95, cy - 0.10, top + 0.08), 0.06, 0.16, COL_GLASS, segments=10)
    make_box("TipJar_Label", (-1.95, cy - 0.162, top + 0.08), (0.08, 0.004, 0.06), (0.86, 0.80, 0.52, 1.0))
    make_box("TipJar_Label_Foot", (-1.95, cy - 0.165, top + 0.08), (0.02, 0.002, 0.035), COL_BLACK)


def build_backbar_kitchen():
    by = YN - 0.25
    k0, k1 = KDOOR[0] - KDOOR[2] / 2.0, KDOOR[0] + KDOOR[2] / 2.0
    for nm, x0, x1 in (("W", -2.3, k0 - 0.12), ("E", k1 + 0.12, 3.6)):
        xc, ln = (x0 + x1) / 2.0, x1 - x0
        make_chamfer_box(f"BackCounter_{nm}_Body", (xc, by, 0.45), (ln, 0.46, 0.90), COL_STEEL)
        make_chamfer_box(f"BackCounter_{nm}_Top", (xc, by, 0.92), (ln, 0.50, 0.05), COL_STEEL)
    make_coffee_pots("CoffeeStation", (-1.6, by - 0.02, 0.945), pots=2, palette={"glass": COL_GLASS})
    # the register on the W back-bar
    make_box("Register_Body", (-0.55, by, 1.03), (0.36, 0.34, 0.17), (0.30, 0.30, 0.32, 1.0))
    make_box("Register_Keys", (-0.55, by - 0.10, 1.125), (0.30, 0.12, 0.02), (0.84, 0.82, 0.76, 1.0))
    make_box("Register_Display", (-0.55, by + 0.08, 1.16), (0.18, 0.04, 0.10), (0.20, 0.42, 0.30, 1.0))
    # pie case (open shell, glints, three pies a shelf)
    px = 1.95
    make_case_shell("PieCase_Body", (px, by, 1.22), (0.64, 0.44, 0.56), COL_STEEL, open_face='-Y')
    for gi, (gx, gw) in enumerate(((-0.22, 0.02), (-0.15, 0.01))):
        make_box(f"PieCase_Glint_{gi}", (px + gx, by - 0.21, 1.22), (gw, 0.004, 0.52), (0.86, 0.90, 0.92, 1.0))
    for ti, tz in enumerate((1.08, 1.32)):
        make_box(f"PieCase_Shelf_{ti}", (px, by + 0.005, tz), (0.60, 0.39, 0.02), COL_CHROME)
        for wi in range(3):
            make_cyl(f"PieCase_Pie_{ti}_{wi}", (px - 0.18 + wi * 0.18, by, tz + 0.035), 0.075, 0.05,
                     [COL_PIE, (0.72, 0.34, 0.28, 1.0), (0.86, 0.78, 0.52, 1.0)][wi], segments=12)
    mx = 3.05
    make_chamfer_box("Shake_Body", (mx, by, 1.165), (0.24, 0.28, 0.44), (0.40, 0.60, 0.52, 1.0))
    for mi in range(3):
        make_cyl(f"Shake_Cup_{mi}", (mx - 0.08 + mi * 0.08, by - 0.20, 1.015), 0.045, 0.14, COL_CHROME, segments=8)
        make_cyl(f"Shake_Spindle_{mi}", (mx - 0.08 + mi * 0.08, by - 0.20, 1.15), 0.012, 0.16, COL_CHROME, segments=6)
    make_box("Shake_Arm", (mx, by - 0.17, 1.24), (0.24, 0.10, 0.04), (0.40, 0.60, 0.52, 1.0))
    # mug shelf over the coffee, the menu board over the E back-bar
    make_box("MugShelf", (-1.15, YN - 0.11, 1.55), (2.2, 0.22, 0.03), COL_STEEL)
    for ui in range(9):
        make_cyl(f"ShelfMug_{ui}", (-2.1 + ui * 0.24, YN - 0.11, 1.615), 0.045, 0.10, COL_MUG, segments=8)
    make_box("MenuBoard_BG", (2.4, YN - 0.015, 2.10), (2.2, 0.03, 0.70), COL_BLACK)
    for li in range(4):
        make_box(f"MenuBoard_Row_{li}", (2.65, YN - 0.032, 2.22 - li * 0.14), (1.40, 0.005, 0.05), (0.90, 0.86, 0.72, 1.0))
    # the menu board's logo: a striding Sasquatch in cream on the black
    lx = 1.62
    for nm, c, sz in (("Body", (lx, 2.12), (0.12, 0.22)), ("Head", (lx + 0.02, 2.29), (0.08, 0.08)),
                      ("LegA", (lx - 0.04, 1.92), (0.05, 0.18)), ("LegB", (lx + 0.05, 1.93), (0.05, 0.16)),
                      ("Arm", (lx + 0.08, 2.08), (0.04, 0.20))):
        make_box(f"MenuBoard_Logo_{nm}", (c[0], YN - 0.033, c[1]), (sz[0], 0.005, sz[1]), (0.90, 0.86, 0.72, 1.0))
    make_box("TicketRail", (2.4, YN - 0.035, 1.73), (2.0, 0.02, 0.02), COL_CHROME)
    for ti in range(3):
        make_box(f"Ticket_{ti}", (1.8 + ti * 0.6, YN - 0.048, 1.65), (0.10, 0.005, 0.14), (0.94, 0.90, 0.62, 1.0))
    # the swinging kitchen door: porthole, push plate, hinge strip
    kx = KDOOR[0]
    make_box("KitchenDoor", (kx, ROOM_D, 1.02), (0.94, 0.06, 2.03), COL_LAMINATE)
    make_cyl("KitchenDoor_Porthole", (kx, ROOM_D - 0.035, 1.55), 0.15, 0.01, (0.86, 0.84, 0.70, 1.0), axis='Y', segments=12)
    make_cyl("KitchenDoor_PortRim", (kx, ROOM_D - 0.04, 1.55), 0.17, 0.02, COL_CHROME, axis='Y', segments=12)
    make_box("KitchenDoor_PushPlate", (kx + 0.30, ROOM_D - 0.033, 1.05), (0.16, 0.004, 0.30), COL_CHROME)
    make_box("KitchenDoor_HingeStrip", (kx - 0.46, ROOM_D - 0.035, 1.02), (0.02, 0.01, 2.00), COL_STEEL)
    # BIGFOOT over the kitchen door: the walking silhouette, cut from ply
    sx_ = kx - 0.25
    for nm, c, sz in (("Torso", (sx_, 2.45), (0.22, 0.30)), ("Head", (sx_ + 0.05, 2.66), (0.12, 0.12)),
                      ("LegA", (sx_ - 0.06, 2.22), (0.08, 0.18)), ("LegB", (sx_ + 0.10, 2.23), (0.08, 0.16)),
                      ("ArmA", (sx_ + 0.15, 2.36), (0.06, 0.26)), ("ArmB", (sx_ - 0.14, 2.40), (0.06, 0.22))):
        make_box(f"Bigfoot_Cutout_{nm}", (c[0], YN - 0.01, c[1]), (sz[0], 0.02, sz[1]), (0.24, 0.16, 0.10, 1.0))


def build_jukebox():
    """The Wurlitzer on the E wall by the door, blinking through its red
    eye, facing W into the room."""
    jx, jy = XE - 0.25, 3.0
    make_chamfer_box("Juke_Body", (jx, jy, 0.53), (0.44, 0.72, 1.04), COL_JUKE)   # the dome sits on it
    make_cyl("Juke_Dome", (jx, jy, 1.38), 0.34, 0.44, COL_JUKE, axis='X', segments=12)
    make_box("Juke_Panel", (jx - 0.23, jy, 1.05), (0.03, 0.56, 0.42), COL_JUKE_GLOW)
    make_box("Juke_PanelGrid", (jx - 0.245, jy, 1.05), (0.005, 0.50, 0.36), (0.30, 0.20, 0.12, 1.0))
    for ci, col in enumerate([(0.94, 0.42, 0.34, 1.0), COL_JUKE_GLOW, (0.42, 0.62, 0.86, 1.0)]):
        make_cyl(f"Juke_ArchTube_{ci}", (jx - 0.10 + ci * 0.10, jy, 1.38), 0.35, 0.02, col, axis='X', segments=12)
    for si, sz in enumerate([0.55, 0.80]):
        make_cyl(f"Juke_Speaker_{si}", (jx - 0.22, jy, sz), 0.10, 0.02, COL_BLACK, axis='X', segments=10)
    make_cyl("Juke_RedEye", (jx - 0.245, jy + 0.24, 1.30), 0.03, 0.02, COL_RED_EYE, axis='X', segments=8)
    make_box("Juke_SelectionCard", (jx - 0.248, jy - 0.18, 1.28), (0.004, 0.14, 0.10), (0.92, 0.90, 0.80, 1.0))
    for fi, (fx, fy) in enumerate(((jx - 0.17, jy - 0.30), (jx + 0.17, jy - 0.30), (jx - 0.17, jy + 0.30), (jx + 0.17, jy + 0.30))):
        make_cyl(f"Juke_Foot_{fi}", (fx, fy, 0.005), 0.03, 0.01, COL_BLACK, segments=6)
    for ti, ty in enumerate((jy - 0.37, jy + 0.37)):
        make_box(f"Juke_Trim_{ti}", (jx - 0.12, ty, 0.72), (0.20, 0.012, 1.10), COL_CHROME)


def build_bigfoot():
    """The theme: a life-size Sasquatch on the W wall between the front
    booths and the corner booth, the crossing sign over him, the plaster
    footprint casts in a shadow box beside him."""
    make_bigfoot("Sasquatch", XW + 0.42, 3.30, heading='+X', h=2.05, seed=11)
    # SASQUATCH CROSSING: the yellow diamond road sign, on the W wall
    make_box("Crossing_Sign", (XW + 0.012, 3.30, 2.42), (0.02, 0.42, 0.42), COL_SIGN_YEL)
    make_box("Crossing_Sign_Border", (XW + 0.008, 3.30, 2.42), (0.01, 0.46, 0.46), COL_BLACK)
    make_box("Crossing_Sign_Figure", (XW + 0.024, 3.30, 2.42), (0.004, 0.10, 0.22), COL_BLACK)
    make_box("Crossing_Sign_Figure_Head", (XW + 0.024, 3.32, 2.57), (0.004, 0.07, 0.07), COL_BLACK)
    # the plaster casts: two footprints (and a hand) in a shadow box
    cy_ = 2.35
    make_box("Cast_Box_Back", (XW + 0.01, cy_, 1.55), (0.02, 0.62, 0.52), COL_WOOD)
    for nm, oy, oz, sz in (("T", 0.0, 0.25, (0.08, 0.62, 0.03)), ("B", 0.0, -0.25, (0.08, 0.62, 0.03)),
                           ("S", -0.30, 0.0, (0.08, 0.03, 0.52)), ("N", 0.30, 0.0, (0.08, 0.03, 0.52))):
        make_box(f"Cast_Box_{nm}", (XW + 0.04, cy_ + oy, 1.55 + oz), sz, COL_WOOD)
    for fi, oy in enumerate((-0.13, 0.11)):
        make_box(f"Cast_Footprint_{fi}", (XW + 0.035, cy_ + oy, 1.55 + (0.02 if fi else -0.02)), (0.03, 0.16, 0.38), COL_PLASTER)
        for ti in range(5):
            make_box(f"Cast_Footprint_{fi}_Toe_{ti}", (XW + 0.052, cy_ + oy - 0.06 + ti * 0.03, 1.55 + (0.02 if fi else -0.02) + 0.17), (0.004, 0.022, 0.03), (0.70, 0.66, 0.58, 1.0))
    make_box("Cast_Label", (XW + 0.022, cy_, 1.34), (0.004, 0.24, 0.035), (0.92, 0.90, 0.80, 1.0))


def build_ceiling_infra():
    for j, (fx, fy) in enumerate(((-3.0, 2.2), (0.0, 2.2), (3.0, 2.2), (-3.0, 5.0), (0.6, 5.0), (3.0, 5.0))):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (fx, fy, CEIL), length=1.60, width=0.34)
    make_smoke_detector("Smoke", (-1.5, 3.6, CEIL))
    make_hvac_vent("Vent", (1.6, 3.6, CEIL), width=1.00, depth=0.50, slats=5)


def build_decor():
    make_wall_clock("Clock", (XE, 5.6, 2.20), frozen_hour=3, frozen_min=40, facing='-X')
    make_calendar("Calendar", (XE - 0.0025, 4.4, 1.70))
    make_floor_plant("Plant", (XE - 0.35, 1.25, 0.0), palette={"leaf": (0.36, 0.46, 0.32, 1.0)})
    # The hand-lettered enamel panel over the front door (inside): THE
    # MISSING LINK, the Sasquatch painted beneath the name
    px = DOOR[0]
    make_box("LinkSign_Frame", (px, YS + 0.02, 2.47), (1.00, 0.04, 0.44), COL_WOOD)
    make_box("LinkSign_Enamel", (px, YS + 0.045, 2.47), (0.92, 0.01, 0.36), (0.90, 0.86, 0.70, 1.0))
    make_box("LinkSign_Title", (px, YS + 0.052, 2.60), (0.72, 0.004, 0.06), COL_BLACK)
    make_box("LinkSign_Figure_Body", (px, YS + 0.052, 2.43), (0.10, 0.004, 0.14), (0.30, 0.20, 0.14, 1.0))
    make_box("LinkSign_Figure_Arm", (px + 0.07, YS + 0.052, 2.41), (0.03, 0.004, 0.14), (0.30, 0.20, 0.14, 1.0))
    make_cyl("LinkSign_Figure_Head", (px + 0.01, YS + 0.052, 2.535), 0.045, 0.004, (0.30, 0.20, 0.14, 1.0), axis='Y', segments=8)


def build_outside():
    """What the front windows see, placed from build_missing_link_
    exterior's coordinates (interior = exterior + (1.5, -8.0))."""
    make_box("Apron", (0.0, -3.4, -0.02), (26.0, 6.6, 0.04), COL_ASPHALT)
    # the pumps: exterior island (-3.2, 5.4), east pump working, west retired
    ix, iy = _ext(-3.2, 5.4)
    make_box("Pump_Island", (ix, iy, 0.08), (2.6, 1.0, 0.16), (0.28, 0.28, 0.30, 1.0))
    for pi, ex in enumerate((-2.5, -3.9)):
        px, py = _ext(ex, 5.4)
        retired = (pi == 1)
        col = (0.42, 0.40, 0.40, 1.0) if retired else COL_PUMP
        make_chamfer_box(f"Pump_{pi}_Body", (px, py, 0.81), (0.50, 0.40, 1.30), col, chamfer=0.02)
        make_box(f"Pump_{pi}_Display", (px, py + 0.21, 1.15), (0.36, 0.02, 0.26),
                 (0.20, 0.24, 0.20, 1.0) if retired else (0.86, 0.92, 0.78, 1.0))
        make_box(f"Pump_{pi}_Topper", (px, py, 1.56), (0.56, 0.30, 0.20), (0.90, 0.88, 0.80, 1.0))
        if not retired:
            make_tube(f"Pump_{pi}_Hose", [(px + 0.26, py, 1.30), (px + 0.42, py, 0.95), (px + 0.28, py, 0.62)], 0.02, COL_BLACK, segments=6)
            make_box(f"Pump_{pi}_Nozzle", (px + 0.28, py, 0.55), (0.06, 0.10, 0.14), COL_STEEL)
    # the depot awning and its bench, off the diner's SE corner (exterior 5.6, 6.6)
    ax, ay = _ext(5.6, 6.6)
    for i in range(3):
        make_box(f"DepotBench_Slat_{i}", (ax, ay + 0.62 - i * 0.13, 0.46), (2.4, 0.11, 0.04), COL_WOOD)
    make_box("DepotBench_Back", (ax, ay + 0.70, 0.65), (2.4, 0.06, 0.34), COL_WOOD)
    for lx in (-1.0, 1.0):
        make_box(f"DepotBench_Leg_{lx:+.0f}", (ax + lx, ay + 0.52, 0.22), (0.08, 0.34, 0.44), COL_BLACK)
    for px_ in (ax - 1.5, ax + 1.5):
        make_cyl(f"Awning_Post_{px_:.1f}", (px_, ay - 0.85, 1.25), 0.06, 2.5, COL_STEEL, segments=6)
    make_box("Awning_Roof", (ax, ay, 2.55), (3.5, 2.2, 0.10), (0.36, 0.38, 0.36, 1.0))
    make_box("Awning_Back", (ax, ay + 1.0, 1.25), (3.5, 0.10, 2.5), (0.52, 0.54, 0.52, 1.0))
    # the carved cedar Sasquatch greeting by the door (exterior 1.20, 7.35)
    gx, gy = _ext(1.20, 7.35)
    make_bigfoot("Greeter", gx, gy, heading='-Y', h=1.85, carved=True, seed=21)
    # the pole sign west (exterior -6.5, 6.5) with the Sasquatch under the name
    sx, sy = _ext(-6.5, 6.5)
    make_lathe("PoleSign_Pole", (sx, sy, 0.0), [(0.20, 0.0), (0.20, 0.05), (0.11, 0.10), (0.11, 4.2), (0.0, 4.2)], (0.30, 0.30, 0.32, 1.0), segments=8)
    make_box("PoleSign_Face", (sx, sy, 4.7), (2.6, 0.22, 1.1), (0.88, 0.84, 0.72, 1.0))
    make_box("PoleSign_Border", (sx, sy, 4.7), (2.75, 0.08, 1.25), (0.62, 0.20, 0.16, 1.0))
    make_box("PoleSign_Figure", (sx + 0.7, sy + 0.115, 4.62), (0.24, 0.01, 0.50), (0.24, 0.16, 0.10, 1.0))
    # the pickup in the lot (exterior -9.6, 5.6)
    tx, ty = _ext(-9.6, 5.6)
    make_car("Truck", tx, ty, 4.9, (0.36, 0.30, 0.24, 1.0), pickup=True, along="X")
    # the road past the apron, the cobra lamppost, field and treeline
    make_box("Road_S", (0.0, -7.7, -0.02), (40.0, 3.4, 0.04), (0.14, 0.14, 0.16, 1.0))
    for di in range(12):
        make_box(f"Road_Dash_{di}", (-16.5 + di * 3.0, -7.7, 0.005), (1.3, 0.12, 0.01), (0.72, 0.68, 0.52, 1.0))
    lx, ly = _ext(8.2, 4.0)
    make_lathe("Lamppost_Pole", (lx, ly, 0.0), [(0.16, 0.0), (0.16, 0.05), (0.09, 0.10), (0.07, 5.0), (0.0, 5.0)], (0.30, 0.30, 0.32, 1.0), segments=8)
    make_tube("Lamppost_Arm", [(lx, ly, 4.9), (lx, ly - 0.6, 5.0), (lx, ly - 1.3, 4.95)], 0.04, (0.30, 0.30, 0.32, 1.0), segments=6)
    make_box("Lamppost_Head", (lx, ly - 1.5, 4.88), (0.24, 0.62, 0.14), (0.44, 0.46, 0.50, 1.0))
    make_box("Field_S", (0.0, -22.0, -0.03), (70.0, 25.0, 0.04), (0.36, 0.40, 0.26, 1.0))
    make_box("Treeline_S", (0.0, -34.0, 0.8), (70.0, 0.6, 1.6), (0.24, 0.30, 0.20, 1.0))
    for ti in range(15):
        tx_ = -31.5 + ti * 4.5 + (0.8 if ti % 2 else -0.6)
        ch = 1.4 + (ti * 37 % 5) * 0.25
        make_cyl(f"Treeline_Crown_{ti}", (tx_, -34.0, 1.5 + ch / 2.0), 1.8 + (ti % 3) * 0.4, ch, (0.22 + (ti % 3) * 0.03, 0.30, 0.20, 1.0), segments=8)


def build_wear():
    """Wear and infrastructure. No part name carries a cue word."""
    floor_dk = (COL_FLOOR[0] * 0.84, COL_FLOOR[1] * 0.84, COL_FLOOR[2] * 0.84, 1.0)
    cord = (0.16, 0.16, 0.18, 1.0)
    # in at the door, up past the jukebox, west down the aisle to the stools
    make_traffic_wear("Wear_Path_Entry", [(DOOR[0], 1.2), (DOOR[0], 3.4), (-1.3, 3.4)], width=0.70, floor_z=0.008, tint=floor_dk)
    make_scuff_band("Wear_Kick", (COUNTER_X, COUNTER_Y - 0.32 - 0.007), 3.8, axis='X', height=0.10, band_z=0.30, tint=(0.36, 0.32, 0.28, 1.0))
    make_box("Wear_Elbow", (COUNTER_X, COUNTER_Y - 0.35, 1.0965), (4.4, 0.06, 0.003), (0.70, 0.64, 0.50, 1.0))
    for bi, bx in enumerate(WIN_XS):
        for sgn, tag in ((-1, "W"), (1, "E")):
            make_box(f"Wear_Sit_{bi}_{tag}", (bx + sgn * 0.60, 0.95, 0.4915), (0.30, 0.50, 0.003), (0.80, 0.30, 0.26, 1.0))
    make_floor_stain("Wear_Lean", (XE - 0.75, 3.0), radius=0.30, tint=floor_dk, segments=10)
    make_light_switch("Switch_1", (KDOOR[0] + 0.70, ROOM_D), axis='X', face_sign=-1, z=1.20, aged=True)
    make_light_switch("Switch_2", (KDOOR[0] + 0.82, ROOM_D), axis='X', face_sign=-1, z=1.20, aged=True)
    make_wall_outlet("Outlet_E_1", (ROOM_W / 2.0, 3.6), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_tube("Cord_1", [(XE - 0.40, 3.30, 0.20), (XE - 0.03, 3.58, 0.30)], 0.008, cord, segments=5)
    make_wall_outlet("Outlet_N_1", (-1.6, ROOM_D), axis='X', face_sign=-1, z=1.10, aged=True)
    make_tube("Cord_2", [(-1.45, YN - 0.27, 0.98), (-1.6, YN - 0.03, 1.10)], 0.008, cord, segments=5)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE FOOD ("The food came. ... Finn ate. He ate slowly and then
    he ate faster"): the plate at the fourth stool — hash, two
    eggs, toast."""
    fx, fy, top = STOOL_XS[3], COUNTER_Y - 0.15, 1.096
    make_cyl("Food_Plate", (fx, fy, top), 0.13, 0.012, (0.92, 0.90, 0.86, 1.0), segments=14)
    make_cyl("Food_Hash", (fx - 0.05, fy - 0.03, top + 0.018), 0.060, 0.024, (0.66, 0.50, 0.30, 1.0), segments=10)
    for ei, (ex, ey) in enumerate(((fx + 0.06, fy - 0.05), (fx + 0.07, fy + 0.04))):
        make_cyl(f"Food_Egg_{ei}", (ex, ey, top + 0.012), 0.028, 0.012, (0.96, 0.94, 0.90, 1.0), segments=8)
        make_cyl(f"Food_Yolk_{ei}", (ex, ey, top + 0.021), 0.012, 0.006, (0.94, 0.72, 0.20, 1.0), segments=8)
    make_box("Food_Toast", (fx - 0.07, fy + 0.07, top + 0.010), (0.07, 0.045, 0.008), (0.80, 0.62, 0.36, 1.0))


def main():
    clear_scene()
    build_shell()
    build_booths()
    build_corner_booth()
    build_counter_and_stools()
    build_backbar_kitchen()
    build_jukebox()
    build_bigfoot()
    build_ceiling_infra()
    build_decor()
    build_outside()
    build_hero_props_2026_09()
    build_wear()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/missing_link_interior.glb"))
    print(f"\n[build_missing_link_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
