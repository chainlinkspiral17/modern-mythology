"""GRACIELA RAMOS'S KITCHEN — one room, two locales (2026-10-06).

The same kitchen was built twice from the store-kit template: as
`ramos_kitchen_morning` (vol 6 ch 1 · ch 10) and as
`grandmother_kitchen_morning` (ch 16 · ch 18 · ch 22 · ch 23) — two
different rooms for one woman's kitchen, both a counter, a centre table
and a grey box. This is the room, once; each locale is a DRESSING of it
(`variant`), the way a set is re-dressed between scenes.

From the prose:
  · "Graciela Ramos is in the kitchen at the small round table under
    the window" (ch 1) — the table stands UNDER the window, and the
    window looks onto the driveway: "His grandmother is at the kitchen
    window when he pulls into the driveway. She has been at the window
    since six forty-five, the same as every morning since June."
  · "the small radio on the windowsill — the kitchen radio ... just a
    radio — the morning Spanish-language news from San Antonio"; "the
    salt she keeps in the small wooden box on the windowsill".
  · "a rosary she is not, at this moment, using, and a cup of black
    coffee ... and a cordless landline phone, on the table, that is
    face-up ... plugged in and charging" (ch 1).
  · "She stands at the counter with her own coffee" — "a cup of
    espresso" — "The clock above the stove reads four thirty-eight PM."
  · "scrambled with a small amount of chorizo she has crumbled into the
    pan" (ch 10) · "the plate she has been bringing him eggs on since he
    was four. The plate is yellow with a small chip at the rim" (ch 22).
  · "The kitchen smells of onions and the small bay leaf she uses in
    caldo. She is at the stove with her back to him" (ch 18) · "She
    brings the soup" (ch 10) · sopa de pollo.
  · "at the kitchen table with the Sentinel ... the small bowl of fruit"
    · "There is a plate in the microwave" (ch 23).
  · "She comes to the front door before he is at the porch" — the hall
    and the front door; Ashberry Drive is a white-stucco subdivision of
    manicured lawns and palms (ch 1).
  · seventy-one, four hurricanes, two husbands: forty years of a life
    on the walls — the Guadalupe, the school photographs, the hutch.

THE ROOM (blender, +Y north, z up; 5 x 5 m, ceiling 2.6):
  · W wall — THE WINDOW over the small round table, the sill with the
    radio, the salt box, a veladora and an aloe; lace tie-backs and a
    valance; outside, the side driveway, the neighbour's white stucco
    and tile roof, a fan palm.
  · N wall — the counter run: canisters, the molcajete, the limes, the
    double sink under an open shelf of mugs, the dish rack, then the
    white enamel range with the clock above its hood, a sliver of
    counter with the spoon crock, the fridge in the corner papered with
    forty years of photographs. Talavera accent tiles behind it all,
    and on the cabinet tops the olla, the rooster, the baskets.
  · E wall — the back door standing open on its screen door and the
    patio (the lemon tree, the clothesline, the cedar fence), the china
    hutch, the calendar.
  · S wall — the doorway to the hall (the front door, the console and
    its mirror, the foot of the stair), the Guadalupe with its palm
    cross, Diego's school pictures climbing the wall, the crucifix.
  · Saltillo tile floor, a serape runner at the sink, a ceiling fan,
    the pendant over the table.

Draft 2 of both locales. Draft 3 targets: the half-bath door off the
hall; steam over the caldo (a mood, not a mesh); the cordless phone's
green charge light as a practical; the hutch's figurines named.
"""
import math

from . import palette as P
from .geometry import (make_box, make_cyl, make_chamfer_box, make_taper_cyl, make_lathe,
                       make_rot_box, make_blob, make_tube, _finalize_mesh)
from .structure import make_ceiling, make_crown_molding, make_wall, make_wall_with_openings, make_window
from .decor import make_wall_clock
from .detail import make_wall_outlet, make_light_switch
from .vehicles import make_car

W, D, CEIL = 5.0, 5.0, 2.6
XW, XE, YS, YN = -2.4, 2.4, 0.1, 4.9          # the room faces of the walls
HALL_S = -1.5                                  # the hall's far wall face
TX, TY = -1.55, 2.70                           # the small round table, under the window
WIN_Y, WIN_Z, WIN_W, WIN_H = 2.70, 1.45, 1.60, 1.15
DOOR_E_Y = 1.20                                # the back door to the patio
DOOR_S_X = -0.40                               # the doorway to the hall
SX = 0.90                                      # the range

PAL = {"wall": (0.94, 0.84, 0.62, 1.0), "baseboard": (0.46, 0.30, 0.18, 1.0)}
HALL_PAL = {"wall": (0.90, 0.84, 0.70, 1.0), "baseboard": (0.46, 0.30, 0.18, 1.0)}
OAK = (0.58, 0.40, 0.22, 1.0)
OAK_DK = (0.40, 0.27, 0.15, 1.0)
WALNUT = (0.32, 0.20, 0.12, 1.0)
ENAMEL = (0.93, 0.91, 0.86, 1.0)
CREAM = (0.94, 0.90, 0.80, 1.0)
CHROME = (0.74, 0.75, 0.76, 1.0)
IRON = (0.15, 0.15, 0.16, 1.0)
PAPER = (0.93, 0.91, 0.85, 1.0)
TALAVERA_BLUE = (0.16, 0.28, 0.62, 1.0)
TALAVERA_YEL = (0.94, 0.70, 0.18, 1.0)
TALAVERA_GRN = (0.24, 0.50, 0.30, 1.0)
TERRACOTTA = (0.70, 0.38, 0.22, 1.0)
LEAF = (0.30, 0.48, 0.26, 1.0)
STUCCO = (0.93, 0.90, 0.82, 1.0)
ROOF_TILE = (0.66, 0.34, 0.22, 1.0)
GRASS = (0.40, 0.52, 0.26, 1.0)
CONCRETE = (0.72, 0.70, 0.66, 1.0)


def _h(*a):
    """Deterministic 0..1 hash (no random in builders)."""
    v = 0
    for k in a:
        v = (v * 131 + int(k * 97.0) + 7) % 100003
    return (v * 7919 % 1000) / 1000.0


# ── the shell ──────────────────────────────────────────────────────
def build_shell():
    """Walls cut for the window, the back door and the hall doorway;
    the hall a step beyond; one ceiling over both."""
    make_wall_with_openings("Wall_W", (-2.5, 2.5, 0), length=D + 0.4, height=CEIL, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(WIN_Y, WIN_Z, WIN_W, WIN_H)])
    make_wall("Wall_N", (0.0, 5.0, 0), length=W + 0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_E", (2.5, 2.5, 0), length=D + 0.4, height=CEIL, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(DOOR_E_Y, 1.04, 0.90, 2.08)])
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=W + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(DOOR_S_X, 1.05, 1.00, 2.10)])
    # the hall: its far wall with the front door, its two ends
    make_wall_with_openings("Hall_Wall_S", (0.0, HALL_S - 0.1, 0), length=W + 0.4, height=CEIL, axis='X',
                            palette=HALL_PAL, baseboard_face_sign=+1, openings=[(-1.70, 1.04, 0.95, 2.08)])
    for nm, x, sgn in (("Hall_Wall_W", -2.5, +1), ("Hall_Wall_E", 2.5, -1)):
        make_wall(nm, (x, (HALL_S - 0.1) / 2.0, 0), length=-HALL_S - 0.1, height=CEIL, axis='Y',
                  palette=HALL_PAL, baseboard_face_sign=sgn)
    make_ceiling("Ceil", (0.0, (D + HALL_S) / 2.0, CEIL), size_x=W + 0.4, size_y=D - HALL_S + 0.6, with_grid=False,
                 palette={"tile": (0.96, 0.93, 0.86, 1.0)})
    for nm, ax, length, wx, wy in (("Crown_W", 'Y', D, XW + 0.0, 2.5), ("Crown_E", 'Y', D, XE - 0.0, 2.5),
                                   ("Crown_N", 'X', W, 0.0, YN - 0.0), ("Crown_S", 'X', W, 0.0, YS + 0.0)):
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": OAK_DK})


def build_floor():
    """Saltillo tile, each tile its own warm shade, the grout a hair
    below — four meshes of quads, not three hundred boxes."""
    make_box("Floor_Grout_Slab", (0.0, (D + HALL_S) / 2.0, -0.055), (W + 0.4, D - HALL_S + 0.4, 0.10),
             (0.52, 0.44, 0.36, 1.0))
    pitch, tile = 0.33, 0.31
    shades = [(0.72, 0.40, 0.24, 1.0), (0.66, 0.36, 0.21, 1.0), (0.76, 0.46, 0.28, 1.0), (0.62, 0.34, 0.22, 1.0)]
    groups = [([], []) for _ in shades]
    nx = int((XE - XW) / pitch) + 1
    ny = int((YN - HALL_S) / pitch) + 1
    for i in range(nx):
        for j in range(ny):
            x0 = XW + i * pitch + 0.01
            y0 = HALL_S + j * pitch + 0.01
            x1 = min(x0 + tile, XE)
            y1 = min(y0 + tile, YN)
            if x1 - x0 < 0.04 or y1 - y0 < 0.04:
                continue
            k = int(_h(i, j, 3) * len(shades)) % len(shades)
            verts, faces = groups[k]
            b = len(verts)
            verts.extend([(x0, y0, -0.001), (x1, y0, -0.001), (x1, y1, -0.001), (x0, y1, -0.001)])
            faces.append((b, b + 1, b + 2, b + 3))
    for k, (verts, faces) in enumerate(groups):
        if faces:
            _finalize_mesh(f"Floor_Tile_Shade_{k}", verts, faces, shades[k])
    # the threshold strips in the two doorways
    make_box("Floor_Threshold_Hall", (DOOR_S_X, 0.0, 0.004), (1.00, 0.20, 0.008), OAK_DK)


# ── the window and the table under it ──────────────────────────────
def build_window():
    make_window("Kitchen_Window", (XW, WIN_Y, WIN_Z), width=WIN_W, height=WIN_H, axis='Y', room_dir=+1,
                see_through=True, palette={"frame": (0.96, 0.95, 0.92, 1.0)})
    sill_z = WIN_Z - WIN_H / 2.0                # 0.875
    make_box("Window_Sill", (XW + 0.13, WIN_Y, sill_z - 0.015), (0.26, WIN_W + 0.24, 0.03), (0.96, 0.95, 0.92, 1.0))
    make_box("Window_Apron", (XW + 0.012, WIN_Y, sill_z - 0.08), (0.024, WIN_W + 0.16, 0.10), (0.96, 0.95, 0.92, 1.0))
    top = sill_z
    SX_ = XW + 0.17                           # the sill items, clear of the frame (to XW+0.08)
    # THE RADIO — "just a radio": a brown plastic set, its dial and grille to the room
    rx, ry = SX_, WIN_Y - 0.50
    make_chamfer_box("Kitchen_Radio", (rx, ry, top + 0.07), (0.12, 0.26, 0.14), (0.42, 0.28, 0.20, 1.0))
    make_box("Kitchen_Radio_Grille", (rx + 0.061, ry - 0.05, top + 0.07), (0.004, 0.13, 0.10), (0.22, 0.16, 0.12, 1.0))
    make_cyl("Kitchen_Radio_Dial", (rx + 0.064, ry + 0.08, top + 0.085), 0.026, 0.008, (0.88, 0.84, 0.72, 1.0), axis='X', segments=10)
    make_cyl("Kitchen_Radio_Knob", (rx + 0.066, ry + 0.08, top + 0.035), 0.012, 0.012, (0.20, 0.16, 0.12, 1.0), axis='X', segments=6)
    make_rot_box("Kitchen_Radio_Antenna_Rod", (rx - 0.02, ry + 0.10, top + 0.29), (0.006, 0.006, 0.34), CHROME, roll=0.0, pitch=0.35)
    make_cyl("Kitchen_Radio_Cord", (rx - 0.04, ry + 0.02, top + 0.004), 0.004, 0.30, (0.12, 0.12, 0.12, 1.0), axis='Y', segments=4)
    # THE SALT BOX — small, wooden, a hinged lid
    make_box("Salt_Box", (SX_, WIN_Y + 0.28, top + 0.045), (0.10, 0.10, 0.09), (0.60, 0.44, 0.28, 1.0))
    make_box("Salt_Box_Lid", (SX_, WIN_Y + 0.28, top + 0.095), (0.11, 0.11, 0.012), (0.50, 0.36, 0.22, 1.0))
    # a veladora — the tall glass candle with the Virgin on it
    make_cyl("Veladora_Glass", (SX_, WIN_Y - 0.12, top + 0.10), 0.032, 0.20, (0.90, 0.86, 0.76, 1.0), segments=10)
    make_cyl("Veladora_Label", (SX_, WIN_Y - 0.12, top + 0.09), 0.0335, 0.11, (0.26, 0.46, 0.38, 1.0), segments=10)
    make_cyl("Veladora_Label_Figure", (SX_ + 0.034, WIN_Y - 0.12, top + 0.09), 0.012, 0.004, (0.86, 0.36, 0.30, 1.0), axis='X', segments=6)
    # an aloe in a clay pot, a geranium at the far end
    make_taper_cyl("Aloe_Pot", (SX_, WIN_Y + 0.48, top + 0.05), 0.045, 0.06, 0.10, TERRACOTTA, segments=10)
    for k in range(6):
        ang = k * math.pi / 3.0
        make_rot_box(f"Aloe_Leaf_{k}", (SX_ + 0.025 * math.cos(ang), WIN_Y + 0.48 + 0.025 * math.sin(ang), top + 0.17),
                     (0.018, 0.010, 0.15), (0.40, 0.56, 0.36, 1.0), yaw=ang, pitch=0.30)
    make_taper_cyl("Geranium_Pot", (SX_, WIN_Y + 0.68, top + 0.055), 0.05, 0.065, 0.11, TERRACOTTA, segments=10)
    make_blob("Geranium_Leaves", (SX_, WIN_Y + 0.68, top + 0.16), 0.08, LEAF, noise=0.25, seed=5)
    for k, (dy, dz) in enumerate(((-0.03, 0.17), (0.035, 0.165), (0.0, 0.19))):
        make_blob(f"Geranium_Leaves_Bloom_{k}", (SX_, WIN_Y + 0.68 + dy, top + dz), 0.025, (0.88, 0.22, 0.24, 1.0), noise=0.2, seed=k)
    # lace tie-back panels and a valance on a rod
    rod_z = WIN_Z + WIN_H / 2.0 + 0.14
    make_cyl("Curtain_Rod", (XW + 0.10, WIN_Y, rod_z), 0.010, WIN_W + 0.50, (0.70, 0.56, 0.30, 1.0), axis='Y', segments=6)
    for sgn in (-1, 1):
        make_box(f"Curtain_Rod_Bracket_{sgn:+d}", (XW + 0.055, WIN_Y + sgn * (WIN_W / 2.0 + 0.22), rod_z),
                 (0.11, 0.02, 0.03), (0.70, 0.56, 0.30, 1.0))
    make_box("Curtain_Valance", (XW + 0.10, WIN_Y, rod_z - 0.10), (0.035, WIN_W + 0.40, 0.22), (0.96, 0.94, 0.88, 1.0))
    make_box("Curtain_Valance_Trim", (XW + 0.119, WIN_Y, rod_z - 0.205), (0.004, WIN_W + 0.40, 0.025), (0.74, 0.20, 0.18, 1.0))
    for sgn, nm in ((-1, "S"), (1, "N")):
        cy = WIN_Y + sgn * (WIN_W / 2.0 + 0.10)
        make_box(f"Curtain_Panel_{nm}_Upper", (XW + 0.09, cy, rod_z - 0.36), (0.03, 0.26, 0.48), (0.95, 0.93, 0.86, 1.0))
        make_box(f"Curtain_Panel_{nm}_Gather", (XW + 0.09, cy - sgn * 0.02, sill_z + 0.62), (0.04, 0.12, 0.10), (0.93, 0.90, 0.82, 1.0))
        make_box(f"Curtain_Panel_{nm}_Lower", (XW + 0.09, cy, sill_z + 0.27), (0.03, 0.22, 0.52), (0.95, 0.93, 0.86, 1.0))
        make_box(f"Curtain_Panel_{nm}_Tie", (XW + 0.108, cy - sgn * 0.02, sill_z + 0.62), (0.004, 0.13, 0.03), (0.74, 0.20, 0.18, 1.0))


def _chair(prefix, cx, cy, face):
    """A spindle-back kitchen chair facing `face` ('+X','-X','+Y','-Y'),
    a tie-on cushion on the seat."""
    f = face.upper()
    bx = {"+X": -1, "-X": 1}.get(f, 0)
    by = {"+Y": -1, "-Y": 1}.get(f, 0)
    make_box(f"{prefix}_Seat", (cx, cy, 0.44), (0.42, 0.42, 0.04), OAK)
    make_box(f"{prefix}_Cushion", (cx, cy, 0.475), (0.38, 0.38, 0.03), (0.72, 0.18, 0.16, 1.0))
    for li, (lx, ly) in enumerate(((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18))):
        make_taper_cyl(f"{prefix}_Leg_{li}", (cx + lx, cy + ly, 0.21), 0.020, 0.016, 0.42, OAK, segments=6)
    for k in range(2):
        z = 0.12 + k * 0.0
        if bx:
            make_cyl(f"{prefix}_Stretcher_{k}", (cx, cy + (k * 2 - 1) * 0.18, 0.14), 0.010, 0.34, OAK_DK, axis='X', segments=5)
        else:
            make_cyl(f"{prefix}_Stretcher_{k}", (cx + (k * 2 - 1) * 0.18, cy, 0.14), 0.010, 0.34, OAK_DK, axis='Y', segments=5)
    # the back: two posts, a top rail, four spindles
    if bx:
        px = cx + bx * 0.19
        for k, s in enumerate((-0.18, 0.18)):
            make_cyl(f"{prefix}_Back_Post_{k}", (px, cy + s, 0.74), 0.018, 0.56, OAK, segments=6)
        make_box(f"{prefix}_Back_Rail", (px, cy, 1.00), (0.04, 0.42, 0.07), OAK)
        for k in range(4):
            make_cyl(f"{prefix}_Back_Spindle_{k}", (px, cy - 0.105 + k * 0.07, 0.73), 0.008, 0.50, OAK, segments=5)
    else:
        py = cy + by * 0.19
        for k, s in enumerate((-0.18, 0.18)):
            make_cyl(f"{prefix}_Back_Post_{k}", (cx + s, py, 0.74), 0.018, 0.56, OAK, segments=6)
        make_box(f"{prefix}_Back_Rail", (cx, py, 1.00), (0.42, 0.04, 0.07), OAK)
        for k in range(4):
            make_cyl(f"{prefix}_Back_Spindle_{k}", (cx - 0.105 + k * 0.07, py, 0.73), 0.008, 0.50, OAK, segments=5)


def build_table():
    """The small round table under the window — an oilcloth with lemons
    and cherries on it — and three chairs: his (east, facing the
    window), hers (north), the guest's (south)."""
    make_lathe("Table_Pedestal", (TX, TY, 0.0), [(0.22, 0.0), (0.22, 0.04), (0.08, 0.10), (0.05, 0.30),
                                                (0.07, 0.42), (0.045, 0.62), (0.10, 0.70), (0.0, 0.70)], OAK_DK, segments=12)
    make_cyl("Table_Top", (TX, TY, 0.7225), 0.48, 0.035, OAK, segments=24)
    make_cyl("Table_Oilcloth_Drop", (TX, TY, 0.69), 0.505, 0.10, (0.96, 0.94, 0.86, 1.0), segments=24)
    make_cyl("Table_Oilcloth", (TX, TY, 0.7425), 0.505, 0.005, (0.96, 0.94, 0.86, 1.0), segments=24)
    prints = (((0.94, 0.80, 0.22, 1.0), 0.018), ((0.78, 0.14, 0.16, 1.0), 0.010), ((0.30, 0.56, 0.30, 1.0), 0.012))
    k = 0
    for i in range(-4, 5):
        for j in range(-4, 5):
            px, py = i * 0.10 + (0.05 if j % 2 else 0.0), j * 0.10
            if px * px + py * py > 0.44 * 0.44:
                continue
            col, r = prints[(i + j * 2) % 3]
            make_cyl(f"Table_Oilcloth_Print_{k}", (TX + px, TY + py, 0.7455), r, 0.0012, col, segments=6)
            k += 1
    for sgn, nm in ((1, "Hem_E"), (-1, "Hem_W")):
        make_box(f"Table_Oilcloth_{nm}", (TX + sgn * 0.507, TY, 0.66), (0.004, 0.30, 0.03), (0.78, 0.14, 0.16, 1.0))
    _chair("Chair_Diego", TX + 0.76, TY, "-X")
    _chair("Chair_Graciela", TX, TY + 0.76, "-Y")
    _chair("Chair_Guest", TX, TY - 0.76, "+Y")
    # the things that live on the table
    top = 0.745
    make_box("Napkin_Holder_Base", (TX - 0.16, TY + 0.10, top + 0.006), (0.14, 0.06, 0.012), (0.80, 0.70, 0.40, 1.0))
    for sgn in (-1, 1):
        make_box(f"Napkin_Holder_Side_{sgn:+d}", (TX - 0.16, TY + 0.10 + sgn * 0.028, top + 0.05), (0.14, 0.006, 0.09), (0.80, 0.70, 0.40, 1.0))
    make_box("Napkin_Holder_Napkins", (TX - 0.16, TY + 0.10, top + 0.045), (0.12, 0.045, 0.075), (0.98, 0.96, 0.90, 1.0))
    make_cyl("Salt_Shaker", (TX - 0.03, TY + 0.14, top + 0.04), 0.018, 0.08, (0.94, 0.94, 0.92, 1.0), segments=8)
    make_cyl("Salt_Shaker_Cap", (TX - 0.03, TY + 0.14, top + 0.085), 0.019, 0.012, CHROME, segments=8)
    make_cyl("Pepper_Shaker", (TX + 0.02, TY + 0.14, top + 0.04), 0.018, 0.08, (0.30, 0.24, 0.20, 1.0), segments=8)
    make_cyl("Pepper_Shaker_Cap", (TX + 0.02, TY + 0.14, top + 0.085), 0.019, 0.012, CHROME, segments=8)
    make_cyl("Hot_Sauce_Bottle", (TX + 0.07, TY + 0.15, top + 0.06), 0.022, 0.12, (0.78, 0.30, 0.12, 1.0), segments=8)
    make_cyl("Hot_Sauce_Bottle_Cap", (TX + 0.07, TY + 0.15, top + 0.13), 0.012, 0.02, (0.92, 0.88, 0.80, 1.0), segments=6)
    make_cyl("Hot_Sauce_Bottle_Label", (TX + 0.07, TY + 0.15, top + 0.05), 0.0235, 0.05, (0.94, 0.78, 0.30, 1.0), segments=8)


# ── the counter run, the range, the fridge ─────────────────────────
CAB_Y0, CAB_Y1 = 4.28, YN                      # base cabinets, front to back
TOP_Z = 0.92


def _base_cabinets(prefix, x0, x1, doors):
    """A base-cabinet run x0..x1 with a toe kick, door and drawer fronts."""
    w = x1 - x0
    cx = (x0 + x1) / 2.0
    make_box(f"{prefix}_Kick", (cx, (CAB_Y0 + 0.05 + CAB_Y1) / 2.0, 0.05), (w, CAB_Y1 - CAB_Y0 - 0.05, 0.10), WALNUT)
    make_box(f"{prefix}_Body", (cx, (CAB_Y0 + CAB_Y1) / 2.0, 0.49), (w, CAB_Y1 - CAB_Y0, 0.78), OAK_DK)
    dw = w / doors
    for k in range(doors):
        dx = x0 + dw * (k + 0.5)
        make_box(f"{prefix}_Door_{k}", (dx, CAB_Y0 - 0.008, 0.40), (dw - 0.025, 0.016, 0.52), OAK)
        make_box(f"{prefix}_Door_{k}_Panel", (dx, CAB_Y0 - 0.018, 0.40), (dw - 0.13, 0.006, 0.38), (0.62, 0.44, 0.25, 1.0))
        make_box(f"{prefix}_Drawer_{k}", (dx, CAB_Y0 - 0.008, 0.77), (dw - 0.025, 0.016, 0.14), OAK)
        make_cyl(f"{prefix}_Drawer_{k}_Pull", (dx, CAB_Y0 - 0.022, 0.77), 0.012, 0.012, (0.70, 0.56, 0.30, 1.0), axis='Y', segments=6)
        kx = dx + (dw / 2.0 - 0.06) * (1 if k % 2 else -1)
        make_cyl(f"{prefix}_Door_{k}_Knob", (kx, CAB_Y0 - 0.022, 0.56), 0.012, 0.012, (0.70, 0.56, 0.30, 1.0), axis='Y', segments=6)
    make_box(f"{prefix}_Top", (cx, (CAB_Y0 - 0.04 + CAB_Y1) / 2.0, TOP_Z - 0.02), (w, CAB_Y1 - CAB_Y0 + 0.04, 0.04),
             (0.86, 0.80, 0.68, 1.0))
    make_box(f"{prefix}_Top_Edge", (cx, CAB_Y0 - 0.035, TOP_Z - 0.02), (w, 0.012, 0.042), (0.48, 0.34, 0.20, 1.0))


def _upper_cabinets(prefix, x0, x1, doors, z0=1.46, z1=2.24):
    w = x1 - x0
    cx = (x0 + x1) / 2.0
    y0 = YN - 0.34
    make_box(f"{prefix}_Body", (cx, (y0 + YN) / 2.0, (z0 + z1) / 2.0), (w, YN - y0, z1 - z0), OAK_DK)
    dw = w / doors
    for k in range(doors):
        dx = x0 + dw * (k + 0.5)
        make_box(f"{prefix}_Door_{k}", (dx, y0 - 0.008, (z0 + z1) / 2.0), (dw - 0.025, 0.016, z1 - z0 - 0.04), OAK)
        make_box(f"{prefix}_Door_{k}_Panel", (dx, y0 - 0.018, (z0 + z1) / 2.0), (dw - 0.13, 0.006, z1 - z0 - 0.20), (0.62, 0.44, 0.25, 1.0))
        kx = dx + (dw / 2.0 - 0.06) * (1 if k % 2 else -1)
        make_cyl(f"{prefix}_Door_{k}_Knob", (kx, y0 - 0.022, z0 + 0.10), 0.012, 0.012, (0.70, 0.56, 0.30, 1.0), axis='Y', segments=6)


def build_counter_run():
    _base_cabinets("Counter_W", XW, 0.50, 5)
    # THE BACKSPLASH — cream tile with Talavera accents, counter to cabinets
    make_box("Backsplash_Tile", ((XW + 1.62) / 2.0, YN - 0.006, (TOP_Z + 1.46) / 2.0), (1.62 - XW, 0.012, 1.46 - TOP_Z),
             (0.94, 0.92, 0.84, 1.0))
    k = 0
    x = XW + 0.10
    while x < 1.58:
        for r, z in enumerate((TOP_Z + 0.13, TOP_Z + 0.37)):
            col = (TALAVERA_BLUE, TALAVERA_YEL, TALAVERA_GRN)[(k + r) % 3]
            make_rot_box(f"Backsplash_Accent_{k}_{r}", (x, YN - 0.0135, z), (0.075, 0.003, 0.075), col, pitch=0.0, roll=0.0, yaw=0.0)
            make_box(f"Backsplash_Accent_{k}_{r}_Dot", (x, YN - 0.0155, z), (0.026, 0.0015, 0.026), CREAM)
        k += 1
        x += 0.20
    make_wall_outlet("Backsplash_Outlet_W", (-2.05, 5.0), axis='X', face_sign=-1, z=1.08)
    make_wall_outlet("Backsplash_Outlet_E", (0.25, 5.0), axis='X', face_sign=-1, z=1.08)
    # upper cabinets either side of the open shelf over the sink, and their tops
    _upper_cabinets("Upper_W", XW, -1.45, 2)
    _upper_cabinets("Upper_E", -0.55, 0.50, 2)
    _upper_cabinets("Upper_Fridge", 1.66, XE, 2, z0=1.98, z1=2.36)
    # on the cabinet tops: the olla, the rooster, the baskets
    make_lathe("Cab_Top_Olla", (-2.05, YN - 0.17, 2.24), [(0.07, 0.0), (0.13, 0.08), (0.12, 0.18), (0.07, 0.24),
                                                         (0.08, 0.27), (0.0, 0.27)], TERRACOTTA, segments=12)
    make_box("Cab_Top_Olla_Band", (-2.05, YN - 0.30, 2.33), (0.18, 0.004, 0.02), (0.92, 0.88, 0.76, 1.0))
    make_lathe("Cab_Top_Basket", (-1.70, YN - 0.17, 2.24), [(0.10, 0.0), (0.13, 0.12), (0.0, 0.12)], (0.70, 0.56, 0.34, 1.0), segments=10)
    make_box("Cab_Top_Rooster_Body", (-0.20, YN - 0.17, 2.33), (0.16, 0.08, 0.14), (0.86, 0.80, 0.70, 1.0))
    make_box("Cab_Top_Rooster_Neck", (-0.13, YN - 0.17, 2.43), (0.05, 0.05, 0.10), (0.86, 0.80, 0.70, 1.0))
    make_box("Cab_Top_Rooster_Comb", (-0.12, YN - 0.17, 2.495), (0.05, 0.02, 0.03), (0.80, 0.16, 0.14, 1.0))
    make_rot_box("Cab_Top_Rooster_Tail", (-0.29, YN - 0.17, 2.40), (0.06, 0.06, 0.16), (0.18, 0.34, 0.30, 1.0), pitch=-0.4)
    make_box("Cab_Top_Rooster_Base", (-0.20, YN - 0.17, 2.255), (0.20, 0.10, 0.03), (0.86, 0.80, 0.70, 1.0))
    make_lathe("Cab_Top_Basket_E", (0.25, YN - 0.17, 2.24), [(0.09, 0.0), (0.11, 0.10), (0.0, 0.10)], (0.62, 0.48, 0.30, 1.0), segments=10)

    # THE SINK — a stainless double basin, the faucet, the dish rack
    sx = -1.00
    make_box("Sink_Rim", (sx, 4.60, TOP_Z + 0.004), (0.82, 0.50, 0.008), CHROME)
    for sgn, nm in ((-1, "L"), (1, "R")):
        make_box(f"Sink_Basin_{nm}", (sx + sgn * 0.20, 4.58, TOP_Z + 0.009), (0.36, 0.40, 0.003), (0.42, 0.44, 0.46, 1.0))
        make_cyl(f"Sink_Basin_{nm}_Drain", (sx + sgn * 0.20, 4.58, TOP_Z + 0.0115), 0.03, 0.002, (0.20, 0.20, 0.22, 1.0), segments=8)
    make_cyl("Sink_Faucet_Base", (sx, 4.84, TOP_Z + 0.03), 0.03, 0.05, CHROME, segments=8)
    make_tube("Sink_Faucet_Spout", [(sx, 4.84, TOP_Z + 0.05), (sx, 4.84, TOP_Z + 0.30), (sx, 4.76, TOP_Z + 0.36),
                                    (sx, 4.66, TOP_Z + 0.30)], 0.012, CHROME)
    for sgn in (-1, 1):
        make_box(f"Sink_Faucet_Handle_{sgn:+d}", (sx + sgn * 0.058, 4.84, TOP_Z + 0.04), (0.06, 0.018, 0.018), CHROME)
    make_box("Dish_Soap_Bottle", (sx + 0.32, 4.82, TOP_Z + 0.09), (0.05, 0.035, 0.18), (0.30, 0.62, 0.36, 1.0))
    make_box("Sink_Sponge", (sx - 0.30, 4.82, TOP_Z + 0.015), (0.09, 0.06, 0.03), (0.94, 0.80, 0.22, 1.0))
    # the serape runner on the floor in front of the sink
    for k, col in enumerate(((0.72, 0.18, 0.18, 1.0), (0.94, 0.70, 0.20, 1.0), (0.20, 0.46, 0.44, 1.0),
                             (0.92, 0.88, 0.80, 1.0), (0.62, 0.16, 0.36, 1.0), (0.20, 0.46, 0.44, 1.0),
                             (0.94, 0.70, 0.20, 1.0), (0.72, 0.18, 0.18, 1.0))):
        make_box(f"Rug_Runner_Stripe_{k}", (sx - 0.53 + k * 0.15 + 0.075, 3.85, 0.004), (0.15, 0.62, 0.006), col)
    # the dish rack beside it
    rx = -0.30
    make_box("Dish_Rack_Tray", (rx, 4.62, TOP_Z + 0.006), (0.42, 0.34, 0.012), (0.90, 0.90, 0.88, 1.0))
    for sgn in (-1, 1):
        make_box(f"Dish_Rack_Wire_{sgn:+d}", (rx, 4.62 + sgn * 0.16, TOP_Z + 0.07), (0.40, 0.008, 0.12), (0.84, 0.84, 0.84, 1.0))
    for k in range(4):
        make_cyl(f"Dish_Rack_Plate_{k}", (rx - 0.15 + k * 0.05, 4.62, TOP_Z + 0.125), 0.11, 0.012,
                 ((0.94, 0.92, 0.86, 1.0), (0.30, 0.46, 0.62, 1.0))[k % 2], axis='X', segments=12)
    for k in range(2):
        make_taper_cyl(f"Dish_Rack_Cup_{k}", (rx + 0.10 + k * 0.08, 4.66, TOP_Z + 0.055), 0.04, 0.032, 0.09,
                       (0.86, 0.36, 0.22, 1.0) if k else (0.24, 0.42, 0.60, 1.0), segments=8)
    # the open shelf over the sink: spice jars, mugs on hooks, a pothos trailing
    make_box("Shelf_Over_Sink", (sx, YN - 0.11, 1.66), (0.90, 0.22, 0.03), OAK)
    for sgn in (-1, 1):
        make_box(f"Shelf_Over_Sink_Bracket_{sgn:+d}", (sx + sgn * 0.40, YN - 0.08, 1.60), (0.03, 0.16, 0.10), OAK_DK)
    for k in range(6):
        make_cyl(f"Spice_Jar_{k}", (sx - 0.36 + k * 0.10, YN - 0.12, 1.71), 0.026, 0.08,
                 ((0.62, 0.22, 0.14, 1.0), (0.82, 0.62, 0.20, 1.0), (0.40, 0.48, 0.24, 1.0))[k % 3], segments=8)
        make_cyl(f"Spice_Jar_{k}_Lid", (sx - 0.36 + k * 0.10, YN - 0.12, 1.755), 0.027, 0.012, (0.30, 0.30, 0.30, 1.0), segments=8)
    for k in range(4):
        hx = sx - 0.27 + k * 0.18
        make_cyl(f"Mug_Hook_{k}", (hx, YN - 0.17, 1.632), 0.004, 0.03, (0.70, 0.56, 0.30, 1.0), segments=4)
        make_cyl(f"Hanging_Mug_{k}", (hx, YN - 0.17, 1.57), 0.038, 0.09,
                 ((0.86, 0.80, 0.30, 1.0), (0.26, 0.40, 0.62, 1.0), (0.82, 0.34, 0.24, 1.0), (0.94, 0.92, 0.88, 1.0))[k],
                 segments=8)
    make_taper_cyl("Pothos_Pot", (sx + 0.30, YN - 0.12, 1.73), 0.05, 0.06, 0.10, TERRACOTTA, segments=8)
    make_blob("Pothos_Leaves", (sx + 0.30, YN - 0.12, 1.80), 0.08, LEAF, noise=0.3, seed=11)
    for k in range(3):
        make_box(f"Pothos_Hanging_Trail_{k}", (sx + 0.30 + k * 0.03, YN - 0.20, 1.52 - k * 0.04), (0.03, 0.03, 0.26 - k * 0.04), LEAF)

    # the counter west of the sink: canisters, the molcajete, the limes, the board
    for k, (nm, col, h) in enumerate((("Harina", (0.86, 0.20, 0.18, 1.0), 0.24), ("Azucar", (0.86, 0.20, 0.18, 1.0), 0.20),
                                      ("Cafe", (0.86, 0.20, 0.18, 1.0), 0.16))):
        cx = XW + 0.13 + k * 0.17
        make_cyl(f"Canister_{nm}", (cx, 4.72, TOP_Z + h / 2.0), 0.07, h, col, segments=10)
        make_cyl(f"Canister_{nm}_Lid", (cx, 4.72, TOP_Z + h + 0.01), 0.072, 0.02, (0.92, 0.90, 0.86, 1.0), segments=10)
        make_cyl(f"Canister_{nm}_Label", (cx, 4.72, TOP_Z + h * 0.55), 0.0715, 0.05, (0.96, 0.94, 0.88, 1.0), segments=10)
    make_lathe("Molcajete_Bowl", (-1.70, 4.56, TOP_Z + 0.05), [(0.0, 0.0), (0.09, 0.0), (0.11, 0.06), (0.10, 0.08), (0.0, 0.04)],
               (0.26, 0.25, 0.24, 1.0), segments=12)
    for k in range(3):
        ang = k * 2.094
        make_box(f"Molcajete_Foot_{k}", (-1.70 + 0.06 * math.cos(ang), 4.56 + 0.06 * math.sin(ang), TOP_Z + 0.025),
                 (0.04, 0.04, 0.05), (0.24, 0.23, 0.22, 1.0))
    make_cyl("Molcajete_Tejolote", (-1.66, 4.54, TOP_Z + 0.15), 0.022, 0.08, (0.30, 0.29, 0.28, 1.0), segments=6)
    make_taper_cyl("Lime_Bowl", (-1.55, 4.79, TOP_Z + 0.03), 0.05, 0.09, 0.06, (0.94, 0.90, 0.80, 1.0), segments=10)
    for k, (lx, ly) in enumerate(((-0.03, 0.0), (0.03, 0.02), (0.0, -0.03), (0.01, 0.03))):
        make_blob(f"Lime_{k}", (-1.55 + lx, 4.79 + ly, TOP_Z + 0.075), 0.026, (0.46, 0.66, 0.22, 1.0), noise=0.1, seed=k)
    make_box("Tortilla_Warmer_Base", (-2.00, 4.42, TOP_Z + 0.025), (0.22, 0.22, 0.05), (0.90, 0.86, 0.74, 1.0))
    make_lathe("Tortilla_Warmer", (-2.00, 4.42, TOP_Z + 0.05), [(0.10, 0.0), (0.10, 0.03), (0.06, 0.06), (0.0, 0.065)],
               (0.78, 0.30, 0.18, 1.0), segments=12)
    make_box("Paper_Towel_Holder_Bar", (-1.70, YN - 0.36, 1.40), (0.30, 0.02, 0.02), CHROME)
    for sgn in (-1, 1):
        make_box(f"Paper_Towel_Holder_Bracket_{sgn:+d}", (-1.70 + sgn * 0.14, YN - 0.36, 1.43), (0.012, 0.03, 0.06), CHROME)
    make_cyl("Paper_Towel_Roll", (-1.70, YN - 0.42, 1.36), 0.06, 0.26, (0.98, 0.98, 0.96, 1.0), axis='X', segments=10)


def build_range_and_fridge(clock_hour, clock_min):
    """The white enamel range (coil burners, back panel, the oven door
    with the towel on its handle), its hood, THE CLOCK above the stove;
    the sliver of counter with the spoon crock; the fridge."""
    x0, x1 = SX - 0.38, SX + 0.38
    make_box("Range_Body", (SX, 4.58, 0.45), (0.76, 0.64, 0.90), ENAMEL)
    make_box("Range_Cooktop", (SX, 4.58, 0.91), (0.76, 0.64, 0.02), (0.88, 0.86, 0.82, 1.0))
    make_box("Range_Backpanel", (SX, YN - 0.05, 1.03), (0.76, 0.10, 0.22), ENAMEL)
    for k in range(4):
        make_cyl(f"Range_Knob_{k}", (SX - 0.27 + k * 0.18, YN - 0.105, 1.03), 0.022, 0.02, (0.24, 0.24, 0.26, 1.0), axis='Y', segments=8)
    make_box("Range_Backpanel_Clock", (SX, YN - 0.101, 1.08), (0.12, 0.004, 0.05), (0.20, 0.30, 0.26, 1.0))
    for bi, (bx, by) in enumerate(((-0.19, -0.18), (0.19, -0.18), (-0.19, 0.08), (0.19, 0.08))):
        make_cyl(f"Range_DripPan_{bi}", (SX + bx, 4.58 + by, 0.922), 0.11, 0.004, CHROME, segments=12)
        make_cyl(f"Range_Burner_{bi}", (SX + bx, 4.58 + by, 0.926), 0.085, 0.006, (0.14, 0.14, 0.15, 1.0), segments=12)
    make_box("Range_Oven_Door", (SX, 4.255, 0.50), (0.72, 0.012, 0.56), ENAMEL)
    make_box("Range_Oven_Window", (SX, 4.247, 0.52), (0.44, 0.004, 0.24), (0.14, 0.13, 0.12, 1.0))
    make_cyl("Range_Oven_Handle", (SX, 4.21, 0.76), 0.012, 0.62, CHROME, axis='X', segments=6)
    for sgn in (-1, 1):
        make_box(f"Range_Oven_Handle_Post_{sgn:+d}", (SX + sgn * 0.29, 4.23, 0.76), (0.02, 0.04, 0.02), CHROME)
    make_box("Range_Drawer", (SX, 4.255, 0.11), (0.72, 0.012, 0.14), ENAMEL)
    # the dish towel over the oven handle: red and white
    make_box("Oven_Towel_Front", (SX - 0.12, 4.20, 0.66), (0.22, 0.006, 0.20), (0.92, 0.90, 0.86, 1.0))
    make_box("Oven_Towel_Front_Stripe", (SX - 0.12, 4.196, 0.62), (0.22, 0.002, 0.03), (0.76, 0.18, 0.16, 1.0))
    make_box("Oven_Towel_Back", (SX - 0.12, 4.225, 0.70), (0.22, 0.006, 0.12), (0.92, 0.90, 0.86, 1.0))
    # the hood and the clock above it
    make_box("Range_Hood", (SX, YN - 0.24, 1.66), (0.80, 0.48, 0.18), (0.88, 0.86, 0.82, 1.0))
    make_box("Range_Hood_Lamp_Lens", (SX + 0.20, YN - 0.30, 1.567), (0.12, 0.08, 0.004), (0.98, 0.92, 0.72, 1.0))
    make_box("Range_Hood_Flue", (SX, YN - 0.12, 1.86), (0.30, 0.22, 0.22), (0.88, 0.86, 0.82, 1.0))
    make_wall_clock("Clock", (SX, YN, 2.24), frozen_hour=clock_hour, frozen_min=clock_min, facing='-Y',
                    palette={"face": (0.98, 0.96, 0.90, 1.0)})
    # the sliver of counter between the range and the fridge
    _base_cabinets("Counter_E", x1 + 0.02, 1.64, 1)
    make_taper_cyl("Utensil_Crock", (1.46, 4.66, TOP_Z + 0.08), 0.06, 0.07, 0.16, (0.30, 0.46, 0.66, 1.0), segments=10)
    for k, (dx, dy, tilt) in enumerate(((-0.02, 0.0, 0.15), (0.02, 0.01, -0.12), (0.0, -0.02, 0.05), (0.01, 0.02, -0.25))):
        make_rot_box(f"Utensil_Spoon_{k}", (1.46 + dx, 4.66 + dy, TOP_Z + 0.25), (0.018, 0.012, 0.30),
                     (0.64, 0.46, 0.28, 1.0), roll=tilt)
    make_box("Recipe_Box", (1.48, 4.82, TOP_Z + 0.06), (0.16, 0.10, 0.12), (0.60, 0.44, 0.28, 1.0))
    # THE FRIDGE — almond, papered in forty years
    fx, fy0, fh = 2.03, 4.16, 1.76
    make_chamfer_box("Fridge_Body", (fx, (fy0 + YN) / 2.0, fh / 2.0), (0.74, YN - fy0, fh), (0.90, 0.88, 0.82, 1.0))
    make_box("Fridge_Seam", (fx, fy0 - 0.003, 1.15), (0.72, 0.006, 0.012), (0.60, 0.58, 0.54, 1.0))
    for nm, z0, z1 in (("Freezer", 1.20, 1.66), ("Fresh", 0.20, 1.06)):
        make_box(f"Fridge_Handle_{nm}", (fx - 0.30, fy0 - 0.015, (z0 + z1) / 2.0), (0.025, 0.03, z1 - z0), (0.70, 0.68, 0.64, 1.0))
    fridge_things = (
        ("Photo_Diego_Grad", -0.10, 1.40, 0.10, 0.14, (0.42, 0.50, 0.66, 1.0)),
        ("Photo_Baby", 0.12, 1.46, 0.09, 0.09, (0.86, 0.74, 0.62, 1.0)),
        ("Drawing_Child", 0.06, 0.80, 0.21, 0.28, (0.98, 0.96, 0.90, 1.0)),
        ("Church_Calendar", -0.12, 0.70, 0.18, 0.26, (0.92, 0.90, 0.86, 1.0)),
        ("Takeout_Menu", 0.18, 1.32, 0.10, 0.20, (0.94, 0.86, 0.50, 1.0)),
        ("Postcard_San_Antonio", -0.20, 1.58, 0.14, 0.09, (0.40, 0.62, 0.78, 1.0)),
        ("Photo_Wedding", 0.20, 0.98, 0.09, 0.12, (0.62, 0.52, 0.40, 1.0)),
        ("Prayer_Card", -0.18, 1.04, 0.06, 0.10, (0.86, 0.80, 0.60, 1.0)),
        ("Photo_Quince", 0.02, 1.22, 0.10, 0.13, (0.86, 0.62, 0.70, 1.0)),
        ("Appointment_Card", -0.06, 0.46, 0.09, 0.05, (0.96, 0.96, 0.94, 1.0)),
    )
    for nm, dx, z, w, h, col in fridge_things:
        make_box(f"Fridge_{nm}", (fx + dx, fy0 - 0.002, z), (w, 0.003, h), col)
        make_cyl(f"Fridge_{nm}_Magnet", (fx + dx, fy0 - 0.006, z + h / 2.0 - 0.015), 0.012, 0.008,
                 ((0.86, 0.20, 0.18, 1.0), (0.22, 0.44, 0.74, 1.0), (0.94, 0.76, 0.22, 1.0))[int(z * 10) % 3], axis='Y', segments=6)
    # the child's drawing: a house, a sun, a stick figure in a cap
    make_box("Fridge_Drawing_Child_House", (fx + 0.06, fy0 - 0.0045, 0.74), (0.10, 0.001, 0.08), (0.84, 0.30, 0.20, 1.0))
    make_box("Fridge_Drawing_Child_Roof", (fx + 0.06, fy0 - 0.0045, 0.80), (0.12, 0.001, 0.03), (0.30, 0.30, 0.70, 1.0))
    make_cyl("Fridge_Drawing_Child_Sun", (fx + 0.14, fy0 - 0.0045, 0.90), 0.025, 0.001, (0.98, 0.80, 0.16, 1.0), axis='Y', segments=8)
    # on the fridge: the bread basket under the cabinet
    make_lathe("Fridge_Top_Bread_Basket", (fx - 0.10, 4.55, fh), [(0.12, 0.0), (0.15, 0.09), (0.0, 0.09)],
               (0.66, 0.50, 0.30, 1.0), segments=10)
    make_blob("Fridge_Top_Pan_Dulce", (fx - 0.10, 4.55, fh + 0.10), 0.06, (0.86, 0.62, 0.40, 1.0), noise=0.1, seed=3)
    make_box("Fridge_Top_Bag", (fx + 0.20, 4.55, fh + 0.07), (0.16, 0.10, 0.14), (0.94, 0.92, 0.86, 1.0))


# ── the east wall: the back door, the hutch, the calendar ──────────
def build_east_wall():
    dy0, dy1 = DOOR_E_Y - 0.45, DOOR_E_Y + 0.45
    for sgn, nm in ((-1, "S"), (1, "N")):
        make_box(f"Back_Door_Casing_{nm}", (XE - 0.01, DOOR_E_Y + sgn * 0.49, 1.06), (0.02, 0.08, 2.12), (0.96, 0.95, 0.92, 1.0))
    make_box("Back_Door_Casing_Head", (XE - 0.01, DOOR_E_Y, 2.14), (0.02, 1.06, 0.10), (0.96, 0.95, 0.92, 1.0))
    # the door itself stands open against the wall, hinged at its north jamb
    make_box("Back_Door_Open", (XE - 0.035, dy1 + 0.42, 1.04), (0.045, 0.82, 2.04), (0.88, 0.86, 0.80, 1.0))
    make_box("Back_Door_Open_Window", (XE - 0.06, dy1 + 0.42, 1.62), (0.006, 0.50, 0.50), (0.60, 0.70, 0.76, 1.0))
    make_cyl("Back_Door_Open_Knob", (XE - 0.08, dy1 + 0.76, 1.00), 0.028, 0.04, (0.80, 0.66, 0.34, 1.0), axis='X', segments=8)
    # the screen door, closed, out in the frame
    sx = XE + 0.17
    for nm, y, z, sy, sz in (("T", DOOR_E_Y, 2.03, 0.86, 0.06), ("B", DOOR_E_Y, 0.06, 0.86, 0.12),
                             ("Mid", DOOR_E_Y, 0.95, 0.86, 0.08), ("S", dy0 + 0.03, 1.04, 0.06, 2.04),
                             ("N", dy1 - 0.03, 1.04, 0.06, 2.04)):
        make_box(f"Screen_Door_Frame_{nm}", (sx, y, z), (0.04, sy, sz), (0.92, 0.92, 0.90, 1.0))
    make_box("Screen_Door_Mesh_Upper", (sx, DOOR_E_Y, 1.49), (0.004, 0.74, 1.02), (0.36, 0.38, 0.40, 0.35))
    make_box("Screen_Door_Kick", (sx, DOOR_E_Y, 0.50), (0.02, 0.74, 0.82), (0.92, 0.92, 0.90, 1.0))
    make_box("Screen_Door_Kick_Grille", (sx - 0.012, DOOR_E_Y, 0.56), (0.004, 0.40, 0.30), (0.70, 0.70, 0.68, 1.0))
    make_box("Screen_Door_Handle", (sx - 0.03, dy0 + 0.10, 1.00), (0.03, 0.02, 0.14), CHROME)
    make_box("Back_Door_Mat", (XE - 0.30, DOOR_E_Y, 0.006), (0.40, 0.70, 0.012), (0.36, 0.28, 0.20, 1.0))
    make_light_switch("Back_Door_Switch", (2.5, dy0 - 0.12), axis='Y', face_sign=-1, z=1.20)

    # THE CHINA HUTCH
    hx0, hy0, hy1 = XE - 0.46, 2.65, 3.85
    hx = (hx0 + XE) / 2.0
    hy = (hy0 + hy1) / 2.0
    make_box("Hutch_Base", (hx, hy, 0.43), (0.46, hy1 - hy0, 0.86), WALNUT)
    make_box("Hutch_Base_Top", (hx - 0.01, hy, 0.875), (0.50, hy1 - hy0 + 0.04, 0.03), WALNUT)
    for k in range(2):
        dy = hy0 + (hy1 - hy0) * (0.25 + 0.5 * k)
        make_box(f"Hutch_Base_Door_{k}", (hx0 - 0.008, dy, 0.44), (0.016, 0.56, 0.70), (0.40, 0.26, 0.16, 1.0))
        make_cyl(f"Hutch_Base_Door_{k}_Knob", (hx0 - 0.022, dy + (0.22 if k == 0 else -0.22), 0.52), 0.014, 0.014,
                 (0.80, 0.66, 0.34, 1.0), axis='X', segments=6)
    make_box("Hutch_Upper_Back", (XE - 0.02, hy, 1.40), (0.04, hy1 - hy0, 1.02), (0.30, 0.18, 0.11, 1.0))
    for sgn, nm in ((-1, "S"), (1, "N")):
        make_box(f"Hutch_Upper_Side_{nm}", (XE - 0.15, hy + sgn * ((hy1 - hy0) / 2.0 - 0.02), 1.40), (0.30, 0.04, 1.02), WALNUT)
    make_box("Hutch_Upper_Top", (XE - 0.18, hy, 1.93), (0.36, hy1 - hy0 + 0.06, 0.04), WALNUT)
    make_box("Hutch_Crown", (XE - 0.19, hy, 1.97), (0.38, hy1 - hy0 + 0.10, 0.05), (0.36, 0.22, 0.13, 1.0))
    for k, z in enumerate((1.22, 1.56)):
        make_box(f"Hutch_Shelf_{k}", (XE - 0.17, hy, z), (0.28, hy1 - hy0 - 0.08, 0.02), WALNUT)
    for z0 in (0.89, 1.23, 1.57):
        make_box(f"Hutch_Plate_Rail_{int(z0 * 100)}", (XE - 0.105, hy, z0 + 0.04), (0.01, hy1 - hy0 - 0.08, 0.02), WALNUT)
    # the good plates standing, faced to the room; cups in front; a figurine; a photo tucked in
    for row, z0 in enumerate((0.89, 1.23, 1.57)):
        for k in range(4):
            py = hy0 + 0.20 + k * 0.27
            col = ((0.96, 0.94, 0.88, 1.0), TALAVERA_BLUE, (0.96, 0.94, 0.88, 1.0), (0.86, 0.72, 0.36, 1.0))[(k + row) % 4]
            make_cyl(f"Hutch_Plate_{row}_{k}", (XE - 0.08, py, z0 + 0.13), 0.12, 0.012, col, axis='X', segments=14)
            make_cyl(f"Hutch_Plate_{row}_{k}_Center", (XE - 0.0875, py, z0 + 0.13), 0.06, 0.002, CREAM if col != CREAM else TALAVERA_BLUE,
                     axis='X', segments=10)
    for k in range(3):
        make_taper_cyl(f"Hutch_Cup_{k}", (XE - 0.20, hy0 + 0.33 + k * 0.30, 1.23 + 0.035), 0.03, 0.04, 0.07,
                       (0.96, 0.94, 0.88, 1.0), segments=8)
    make_lathe("Hutch_Figurine_Virgin", (XE - 0.20, hy1 - 0.16, 1.57), [(0.03, 0.0), (0.035, 0.05), (0.022, 0.12),
                                                                        (0.016, 0.16), (0.0, 0.18)], (0.30, 0.52, 0.48, 1.0), segments=8)
    make_box("Hutch_Photo_Tucked", (XE - 0.31, hy0 + 0.085, 1.70), (0.004, 0.09, 0.12), (0.70, 0.60, 0.50, 1.0))
    # on the crown: plastic flowers in a vase, a photograph of her husbands' generation
    make_lathe("Hutch_Top_Vase", (XE - 0.20, hy - 0.30, 1.995), [(0.04, 0.0), (0.06, 0.08), (0.035, 0.18), (0.045, 0.22), (0.0, 0.22)],
               (0.30, 0.52, 0.62, 1.0), segments=10)
    for k, (dy, dz, col) in enumerate(((-0.04, 0.30, (0.92, 0.30, 0.40, 1.0)), (0.03, 0.33, (0.96, 0.86, 0.30, 1.0)),
                                       (0.0, 0.36, (0.92, 0.30, 0.40, 1.0)), (0.05, 0.28, (0.96, 0.96, 0.92, 1.0)))):
        make_blob(f"Hutch_Top_Flower_{k}", (XE - 0.20, hy - 0.30 + dy, 1.995 + dz), 0.035, col, noise=0.25, seed=k + 20)
        make_cyl(f"Hutch_Top_Flower_{k}_Stem", (XE - 0.20, hy - 0.30 + dy * 0.6, 1.995 + (0.16 + dz) / 2.0), 0.004,
                 dz - 0.14, (0.30, 0.46, 0.26, 1.0), segments=4)
    make_rot_box("Hutch_Top_Photo_Frame", (XE - 0.20, hy + 0.25, 2.10), (0.02, 0.20, 0.25), (0.70, 0.56, 0.30, 1.0), roll=0.12)
    make_box("Hutch_Top_Photo", (XE - 0.215, hy + 0.25, 2.10), (0.004, 0.15, 0.19), (0.62, 0.54, 0.44, 1.0))
    # three Talavera plates hung over the hutch
    for k in range(3):
        make_cyl(f"Wall_Plate_{k}", (XE - 0.01, hy - 0.40 + k * 0.40, 2.30), 0.11, 0.015,
                 (TALAVERA_BLUE, TALAVERA_YEL, TALAVERA_GRN)[k], axis='X', segments=14)
        make_cyl(f"Wall_Plate_{k}_Center", (XE - 0.0185, hy - 0.40 + k * 0.40, 2.30), 0.06, 0.002, CREAM, axis='X', segments=10)

    # the calendar from the carnicería, between the hutch and the fridge
    cy = 4.00
    make_box("Calendar_Picture", (XE - 0.004, cy, 1.62), (0.006, 0.28, 0.22), (0.30, 0.50, 0.64, 1.0))
    make_box("Calendar_Picture_Sky", (XE - 0.0075, cy, 1.67), (0.002, 0.26, 0.10), (0.94, 0.66, 0.36, 1.0))
    make_box("Calendar_Grid", (XE - 0.004, cy, 1.36), (0.006, 0.28, 0.28), PAPER)
    for r in range(4):
        make_box(f"Calendar_Grid_Line_{r}", (XE - 0.0075, cy, 1.26 + r * 0.06), (0.002, 0.26, 0.004), (0.40, 0.40, 0.42, 1.0))
    make_box("Calendar_Header", (XE - 0.0075, cy, 1.48), (0.002, 0.26, 0.03), (0.76, 0.18, 0.16, 1.0))
    make_cyl("Calendar_Nail", (XE - 0.01, cy, 1.745), 0.004, 0.02, IRON, axis='X', segments=4)


# ── the west wall either side of the window ────────────────────────
def build_west_wall():
    """South of the window, the baker's rack: cookbooks, a basket of
    onions and potatoes, the old Sentinels, a pothos, the good serving
    bowl. North of it, the Sacred Heart over the potholder hook."""
    bx, by = XW + 0.19, 0.95
    for sgn in (-1, 1):
        for d in (-1, 1):
            make_cyl(f"Bakers_Rack_Post_{sgn:+d}_{d:+d}", (bx + d * 0.16, by + sgn * 0.42, 0.85), 0.012, 1.70, IRON, segments=6)
    for k, z in enumerate((0.12, 0.62, 1.08, 1.50)):
        make_box(f"Bakers_Rack_Shelf_{k}", (bx, by, z), (0.36, 0.88, 0.02), (0.20, 0.20, 0.21, 1.0))
    make_box("Bakers_Rack_Finial_Bar", (bx, by, 1.70), (0.34, 0.88, 0.02), IRON)
    # bottom: the basket of onions and potatoes, the stack of old Sentinels
    make_box("Bakers_Rack_Onion_Basket", (bx, by - 0.20, 0.23), (0.30, 0.34, 0.20), (0.66, 0.50, 0.30, 1.0))
    for k, (dx, dy, col) in enumerate(((-0.06, -0.08, (0.80, 0.56, 0.34, 1.0)), (0.05, -0.02, (0.86, 0.62, 0.40, 1.0)),
                                       (-0.02, 0.06, (0.62, 0.46, 0.30, 1.0)), (0.07, 0.09, (0.80, 0.56, 0.34, 1.0)))):
        make_blob(f"Bakers_Rack_Onion_Basket_Onion_{k}", (bx + dx, by - 0.20 + dy, 0.35), 0.045, col, noise=0.12, seed=k + 70)
    for k in range(5):
        make_box(f"Bakers_Rack_Sentinels_{k}", (bx, by + 0.22, 0.135 + 0.012 * k + 0.006), (0.28, 0.34, 0.012),
                 (0.90 - 0.02 * k, 0.88 - 0.02 * k, 0.80 - 0.02 * k, 1.0))
    # middle: the cookbooks, the serving bowl
    for k in range(6):
        h = 0.22 + 0.03 * (k % 3)
        make_box(f"Bakers_Rack_Cookbook_{k}", (bx, by - 0.36 + k * 0.05, 0.63 + h / 2.0), (0.20, 0.045, h),
                 ((0.62, 0.20, 0.18, 1.0), (0.24, 0.40, 0.56, 1.0), (0.86, 0.74, 0.40, 1.0), (0.30, 0.50, 0.32, 1.0))[k % 4])
    make_taper_cyl("Bakers_Rack_Serving_Bowl", (bx, by + 0.22, 0.67), 0.08, 0.15, 0.10, TALAVERA_BLUE, segments=14)
    make_taper_cyl("Bakers_Rack_Serving_Bowl_Rim", (bx, by + 0.22, 0.715), 0.15, 0.152, 0.012, TALAVERA_YEL, segments=14)
    # upper: a pothos trailing, a tin of cookies, the good platter on a stand
    make_taper_cyl("Bakers_Rack_Pothos_Pot", (bx, by - 0.24, 1.15), 0.06, 0.08, 0.12, TERRACOTTA, segments=10)
    make_blob("Bakers_Rack_Pothos_Leaves", (bx, by - 0.24, 1.25), 0.11, LEAF, noise=0.3, seed=71)
    for k in range(3):
        make_box(f"Bakers_Rack_Pothos_Vine_{k}", (bx + 0.10, by - 0.30 + k * 0.06, 0.98 - k * 0.08), (0.03, 0.03, 0.30), LEAF)
    make_cyl("Bakers_Rack_Cookie_Tin", (bx, by + 0.12, 1.13), 0.10, 0.08, (0.22, 0.34, 0.62, 1.0), segments=14)
    make_cyl("Bakers_Rack_Cookie_Tin_Lid", (bx, by + 0.12, 1.175), 0.102, 0.012, (0.86, 0.72, 0.30, 1.0), segments=14)
    make_cyl("Bakers_Rack_Platter", (bx - 0.07, by + 0.10, 1.66), 0.15, 0.012, (0.94, 0.90, 0.80, 1.0), axis='X', segments=14)
    make_cyl("Bakers_Rack_Platter_Center", (bx - 0.063, by + 0.10, 1.66), 0.09, 0.002, TALAVERA_GRN, axis='X', segments=12)
    make_box("Bakers_Rack_Platter_Stand", (bx - 0.05, by + 0.10, 1.53), (0.04, 0.10, 0.04), IRON)
    # north of the window: the Sacred Heart, the potholder hook under it
    hy = 3.95
    make_box("Sacred_Heart_Frame", (XW + 0.012, hy, 1.70), (0.024, 0.36, 0.46), (0.76, 0.58, 0.26, 1.0))
    make_box("Sacred_Heart_Print", (XW + 0.026, hy, 1.70), (0.004, 0.29, 0.39), (0.62, 0.30, 0.24, 1.0))
    make_box("Sacred_Heart_Figure", (XW + 0.0295, hy, 1.66), (0.002, 0.14, 0.28), (0.82, 0.70, 0.58, 1.0))
    make_box("Sacred_Heart_Heart", (XW + 0.031, hy, 1.70), (0.002, 0.04, 0.04), (0.90, 0.20, 0.16, 1.0))
    make_box("Sacred_Heart_Halo", (XW + 0.0305, hy, 1.81), (0.002, 0.10, 0.03), (0.96, 0.80, 0.30, 1.0))
    make_box("Potholder_Hook_Bar", (XW + 0.012, hy, 1.30), (0.024, 0.30, 0.03), OAK_DK)
    for k, col in enumerate(((0.74, 0.20, 0.18, 1.0), (0.94, 0.72, 0.24, 1.0), (0.24, 0.42, 0.62, 1.0))):
        make_cyl(f"Potholder_Hook_Peg_{k}", (XW + 0.04, hy - 0.10 + k * 0.10, 1.30), 0.006, 0.05, OAK_DK, axis='X', segments=4)
        make_box(f"Potholder_Hook_Mitt_{k}", (XW + 0.05, hy - 0.10 + k * 0.10, 1.19), (0.012, 0.09, 0.20), col)


# ── the south wall and the hall ────────────────────────────────────
def build_south_wall_and_hall():
    # the Guadalupe with its palm cross, west of the doorway
    gx = -1.70
    make_box("Guadalupe_Frame", (gx, YS + 0.012, 1.58), (0.46, 0.024, 0.62), (0.76, 0.58, 0.26, 1.0))
    make_box("Guadalupe_Print", (gx, YS + 0.026, 1.58), (0.38, 0.004, 0.54), (0.20, 0.44, 0.40, 1.0))
    make_box("Guadalupe_Mandorla", (gx, YS + 0.029, 1.56), (0.20, 0.002, 0.44), (0.94, 0.76, 0.30, 1.0))
    make_box("Guadalupe_Figure_Mantle", (gx, YS + 0.031, 1.54), (0.12, 0.002, 0.34), (0.20, 0.44, 0.40, 1.0))
    make_box("Guadalupe_Figure_Robe", (gx, YS + 0.0325, 1.50), (0.05, 0.001, 0.24), (0.84, 0.40, 0.40, 1.0))
    make_box("Guadalupe_Figure_Face", (gx, YS + 0.0325, 1.69), (0.03, 0.001, 0.04), (0.66, 0.50, 0.38, 1.0))
    make_box("Guadalupe_Figure_Moon", (gx, YS + 0.0325, 1.36), (0.10, 0.001, 0.025), (0.20, 0.20, 0.22, 1.0))
    make_box("Guadalupe_Palm_Cross", (gx + 0.21, YS + 0.034, 1.86), (0.012, 0.004, 0.22), (0.80, 0.72, 0.46, 1.0))
    make_box("Guadalupe_Palm_Cross_Arm", (gx + 0.21, YS + 0.034, 1.90), (0.10, 0.004, 0.012), (0.80, 0.72, 0.46, 1.0))
    make_box("Guadalupe_Shelf", (gx, YS + 0.08, 1.18), (0.36, 0.16, 0.025), OAK_DK)
    make_cyl("Guadalupe_Shelf_Veladora", (gx - 0.08, YS + 0.08, 1.2925), 0.030, 0.20, (0.86, 0.26, 0.20, 1.0), segments=10)
    make_cyl("Guadalupe_Shelf_Rosary_Dish", (gx + 0.08, YS + 0.08, 1.2025), 0.05, 0.02, (0.92, 0.88, 0.80, 1.0), segments=10)
    # the broom and the dustpan in the corner
    make_rot_box("Broom_Handle", (XW + 0.12, YS + 0.16, 0.78), (0.024, 0.024, 1.20), (0.70, 0.56, 0.32, 1.0), roll=0.08, pitch=-0.06)
    make_rot_box("Broom_Head", (XW + 0.17, YS + 0.20, 0.13), (0.24, 0.07, 0.24), (0.84, 0.70, 0.36, 1.0), roll=0.08)
    make_box("Dustpan", (XW + 0.40, YS + 0.08, 0.15), (0.26, 0.03, 0.30), (0.26, 0.46, 0.62, 1.0))
    # the crucifix over the doorway
    make_box("Crucifix_Upright", (DOOR_S_X, YS + 0.012, 2.36), (0.04, 0.024, 0.30), WALNUT)
    make_box("Crucifix_Arm", (DOOR_S_X, YS + 0.012, 2.42), (0.20, 0.024, 0.04), WALNUT)
    make_box("Crucifix_Corpus", (DOOR_S_X, YS + 0.028, 2.38), (0.03, 0.008, 0.14), (0.86, 0.80, 0.66, 1.0))
    for sgn, nm in ((-1, "W"), (1, "E")):
        make_box(f"Hall_Doorway_Casing_{nm}", (DOOR_S_X + sgn * 0.54, YS + 0.01, 1.06), (0.08, 0.02, 2.12), (0.96, 0.95, 0.92, 1.0))
    make_box("Hall_Doorway_Casing_Head", (DOOR_S_X, YS + 0.01, 2.14), (1.16, 0.02, 0.10), (0.96, 0.95, 0.92, 1.0))
    make_light_switch("Hall_Doorway_Switch", (DOOR_S_X + 0.68, 0.0), axis='X', face_sign=1, z=1.20)
    # DIEGO'S SCHOOL PICTURES climbing the wall east of the doorway, K to tenth
    for k in range(11):
        px = 0.45 + k * 0.17
        pz = 1.18 + k * 0.05 + (0.08 if k % 2 else 0.0)
        make_box(f"School_Photo_{k}_Frame", (px, YS + 0.01, pz), (0.13, 0.02, 0.17), (0.70, 0.56, 0.30, 1.0) if k % 3 else WALNUT)
        make_box(f"School_Photo_{k}", (px, YS + 0.0205, pz), (0.10, 0.002, 0.13), (0.40 + 0.02 * k, 0.48, 0.66 - 0.02 * k, 1.0))
        make_box(f"School_Photo_{k}_Face", (px, YS + 0.022, pz + 0.01), (0.04, 0.001, 0.05), (0.72, 0.54, 0.40, 1.0))
    # the wedding photograph, sepia, larger, under them
    make_box("Wedding_Photo_Frame", (1.30, YS + 0.012, 0.92), (0.34, 0.024, 0.42), WALNUT)
    make_box("Wedding_Photo", (1.30, YS + 0.0255, 0.92), (0.27, 0.003, 0.35), (0.66, 0.56, 0.42, 1.0))
    make_box("Wedding_Photo_Couple", (1.30, YS + 0.0275, 0.88), (0.12, 0.001, 0.20), (0.36, 0.30, 0.24, 1.0))
    make_box("Wedding_Photo_Veil", (1.27, YS + 0.0285, 0.93), (0.05, 0.001, 0.16), (0.90, 0.86, 0.76, 1.0))
    # the key rack by the doorway, the trash can in the corner by the back door
    make_box("Key_Rack", (0.32, YS + 0.012, 1.42), (0.18, 0.024, 0.06), OAK)
    for k in range(3):
        make_cyl(f"Key_Rack_Hook_{k}", (0.26 + k * 0.06, YS + 0.03, 1.40), 0.004, 0.03, CHROME, axis='Y', segments=4)
        make_box(f"Key_Rack_Keys_{k}", (0.26 + k * 0.06, YS + 0.036, 1.36), (0.02, 0.004, 0.05), (0.80, 0.70, 0.36, 1.0))
    make_taper_cyl("Trash_Can", (2.10, YS + 0.24, 0.32), 0.15, 0.17, 0.64, (0.86, 0.86, 0.84, 1.0), segments=12)
    make_cyl("Trash_Can_Lid", (2.10, YS + 0.24, 0.655), 0.175, 0.03, (0.80, 0.80, 0.78, 1.0), segments=12)

    # THE HALL: the front door, the console with its mirror and its lamp, the runner, the stair's foot
    fx = -1.70
    make_box("Front_Door", (fx, HALL_S - 0.025, 1.04), (0.90, 0.05, 2.06), (0.42, 0.26, 0.16, 1.0))
    for k, (dx, dz) in enumerate(((-0.20, 1.50), (0.20, 1.50), (-0.20, 0.55), (0.20, 0.55))):
        make_box(f"Front_Door_Panel_{k}", (fx + dx, HALL_S + 0.004, dz), (0.30, 0.008, 0.70 if dz > 1 else 0.60),
                 (0.36, 0.22, 0.13, 1.0))
    make_cyl("Front_Door_Knob", (fx + 0.36, HALL_S + 0.02, 1.00), 0.028, 0.04, (0.80, 0.66, 0.34, 1.0), axis='Y', segments=8)
    make_box("Front_Door_Deadbolt", (fx + 0.36, HALL_S + 0.01, 1.18), (0.05, 0.02, 0.07), (0.80, 0.66, 0.34, 1.0))
    make_box("Front_Door_Peephole", (fx, HALL_S + 0.002, 1.55), (0.02, 0.004, 0.02), (0.80, 0.66, 0.34, 1.0))
    make_box("Hall_Runner", (-0.60, HALL_S + 0.70, 0.004), (2.60, 0.70, 0.008), (0.52, 0.20, 0.18, 1.0))
    make_box("Hall_Runner_Border", (-0.60, HALL_S + 0.70, 0.0085), (2.40, 0.54, 0.001), (0.70, 0.52, 0.30, 1.0))
    cx = -0.40
    make_box("Hall_Console_Top", (cx, HALL_S + 0.17, 0.78), (0.90, 0.32, 0.03), WALNUT)
    for sgn in (-1, 1):
        for d in (0.03, 0.29):
            make_box(f"Hall_Console_Leg_{sgn:+d}_{int(d * 100)}", (cx + sgn * 0.42, HALL_S + d + 0.02, 0.385),
                     (0.04, 0.04, 0.77), WALNUT)
    make_box("Hall_Console_Shelf", (cx, HALL_S + 0.17, 0.18), (0.86, 0.28, 0.02), WALNUT)
    make_box("Hall_Console_Mail", (cx - 0.22, HALL_S + 0.18, 0.80), (0.22, 0.12, 0.012), PAPER)
    make_taper_cyl("Hall_Console_Key_Bowl", (cx + 0.05, HALL_S + 0.18, 0.81), 0.05, 0.08, 0.03, TALAVERA_BLUE, segments=10)
    make_lathe("Hall_Lamp_Base", (cx + 0.30, HALL_S + 0.17, 0.795), [(0.07, 0.0), (0.06, 0.04), (0.04, 0.20), (0.015, 0.34), (0.0, 0.34)],
               (0.70, 0.56, 0.30, 1.0), segments=10)
    make_taper_cyl("Hall_Lamp_Shade", (cx + 0.30, HALL_S + 0.17, 1.23), 0.15, 0.10, 0.20, (0.96, 0.88, 0.70, 1.0), segments=12)
    make_box("Hall_Mirror_Frame", (cx, HALL_S + 0.012, 1.45), (0.62, 0.024, 0.80), (0.70, 0.56, 0.30, 1.0))
    make_box("Hall_Mirror_Glass", (cx, HALL_S + 0.026, 1.45), (0.52, 0.004, 0.70), (0.62, 0.66, 0.68, 1.0))
    for k in range(3):
        make_box(f"Hall_Photo_{k}_Frame", (0.75 + k * 0.42, HALL_S + 0.012, 1.55 + 0.06 * k), (0.30, 0.024, 0.38), WALNUT)
        make_box(f"Hall_Photo_{k}", (0.75 + k * 0.42, HALL_S + 0.0255, 1.55 + 0.06 * k), (0.24, 0.003, 0.32),
                 ((0.58, 0.50, 0.40, 1.0), (0.46, 0.56, 0.62, 1.0), (0.70, 0.62, 0.50, 1.0))[k])
    # the foot of the stair, rising east along the hall's far wall
    for k in range(6):
        x = 0.95 + k * 0.26
        h = 0.19 * (k + 1)
        make_box(f"Stair_Tread_{k}", (x, HALL_S + 0.48, h / 2.0), (0.26, 0.92, h), (0.50, 0.34, 0.20, 1.0))
        make_box(f"Stair_Tread_{k}_Nose", (x - 0.12, HALL_S + 0.48, h - 0.012), (0.04, 0.94, 0.025), OAK_DK)
    make_box("Stair_Newel", (0.82, HALL_S + 0.90, 0.55), (0.10, 0.10, 1.10), WALNUT)
    make_rot_box("Stair_Handrail", (1.60, HALL_S + 0.90, 1.50), (1.70, 0.06, 0.06), WALNUT, pitch=-math.atan2(0.19, 0.26))
    for k in range(5):
        x = 1.00 + k * 0.26
        z0 = 0.19 * (k + 1)
        make_box(f"Stair_Baluster_{k}", (x, HALL_S + 0.90, z0 + 0.45), (0.03, 0.03, 0.90 - 0.04 * 0), OAK)


# ── the ceiling: the fan, the pendant over the table ───────────────
def build_ceiling_things():
    fx, fy = 0.50, 2.40
    make_cyl("Ceiling_Fan_Canopy", (fx, fy, CEIL - 0.04), 0.07, 0.08, (0.70, 0.56, 0.30, 1.0), segments=10)
    make_cyl("Ceiling_Fan_Downrod", (fx, fy, CEIL - 0.20), 0.012, 0.26, (0.70, 0.56, 0.30, 1.0), segments=6)
    make_lathe("Ceiling_Fan_Motor", (fx, fy, CEIL - 0.42), [(0.0, 0.0), (0.12, 0.02), (0.13, 0.08), (0.10, 0.12), (0.0, 0.12)],
               (0.70, 0.56, 0.30, 1.0), segments=14)
    for k in range(5):
        ang = k * 2.0 * math.pi / 5.0 + 0.3
        r = 0.42
        make_rot_box(f"Ceiling_Fan_Blade_{k}", (fx + r * math.cos(ang), fy + r * math.sin(ang), CEIL - 0.37),
                     (0.56, 0.13, 0.008), OAK, yaw=ang)
        make_rot_box(f"Ceiling_Fan_Blade_Iron_{k}", (fx + 0.16 * math.cos(ang), fy + 0.16 * math.sin(ang), CEIL - 0.365),
                     (0.12, 0.03, 0.014), (0.70, 0.56, 0.30, 1.0), yaw=ang)
    make_lathe("Ceiling_Fan_Light_Bowl", (fx, fy, CEIL - 0.56), [(0.0, 0.0), (0.08, 0.02), (0.13, 0.10), (0.0, 0.14)],
               (0.98, 0.94, 0.82, 1.0), segments=12)
    for k in range(2):
        make_cyl(f"Ceiling_Fan_Pull_Chain_{k}", (fx + 0.05 - k * 0.10, fy, CEIL - 0.60), 0.003, 0.22, (0.80, 0.66, 0.34, 1.0), segments=4)
    # the pendant over the table: amber glass in a copper cap
    make_cyl("Table_Pendant_Cord", (TX, TY, CEIL - 0.32), 0.006, 0.64, IRON, segments=4)
    make_cyl("Table_Pendant_Canopy", (TX, TY, CEIL - 0.015), 0.05, 0.03, (0.62, 0.40, 0.22, 1.0), segments=8)
    make_lathe("Table_Pendant_Shade", (TX, TY, CEIL - 0.86), [(0.20, 0.0), (0.18, 0.06), (0.10, 0.18), (0.03, 0.22), (0.0, 0.22)],
               (0.86, 0.52, 0.22, 1.0), segments=14)
    make_cyl("Table_Pendant_Bulb", (TX, TY, CEIL - 0.84), 0.04, 0.05, (1.0, 0.94, 0.78, 1.0), segments=8)
    make_box("Smoke_Detector", (1.40, 1.20, CEIL - 0.02), (0.12, 0.12, 0.04), (0.94, 0.94, 0.92, 1.0))
    make_box("Ceiling_Vent", (-0.40, 3.60, CEIL - 0.006), (0.30, 0.20, 0.012), (0.90, 0.90, 0.88, 1.0))
    for k in range(4):
        make_box(f"Ceiling_Vent_Slat_{k}", (-0.40, 3.53 + k * 0.045, CEIL - 0.013), (0.26, 0.01, 0.002), (0.60, 0.60, 0.58, 1.0))
    make_cyl("Hall_Ceiling_Light", (-0.40, HALL_S + 0.70, CEIL - 0.05), 0.16, 0.08, (0.96, 0.92, 0.80, 1.0), segments=12)


# ── outside: the side drive (west window), the patio (east door) ───
def _fan_palm(prefix, x, y, h):
    make_taper_cyl(f"{prefix}_Trunk", (x, y, (h - 0.12) / 2.0), 0.24, 0.16, h + 0.12, (0.52, 0.44, 0.36, 1.0), segments=8)
    make_blob(f"{prefix}_Boot", (x, y, h - 0.4), 0.42, (0.46, 0.38, 0.28, 1.0), noise=0.3, seed=int(x * 3))
    for k in range(12):
        ang = k * math.pi / 6.0
        make_rot_box(f"{prefix}_Frond_{k}", (x + 0.9 * math.cos(ang), y + 0.9 * math.sin(ang), h + 0.25 - 0.25 * (k % 3)),
                     (1.60, 0.70, 0.02), (0.30, 0.46, 0.28, 1.0), yaw=ang, roll=0.0, pitch=-0.25 - 0.1 * (k % 3))


def _stucco_house(prefix, x0, x1, y0, y1, h, facing):
    """A neighbour's white stucco house with a clay tile roof and two
    windows on the side `facing` the kitchen ('+X' or '-X')."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    make_box(f"{prefix}_Wall", (cx, cy, (h - 0.12) / 2.0), (x1 - x0, y1 - y0, h + 0.12), STUCCO)
    make_box(f"{prefix}_Roof", (cx, cy, h + 0.45), (x1 - x0 + 0.8, y1 - y0 + 0.8, 0.9), ROOF_TILE)
    make_box(f"{prefix}_Roof_Ridge", (cx, cy, h + 1.05), (x1 - x0 - 1.2, 0.5, 0.3), (0.58, 0.28, 0.18, 1.0))
    face_x = x1 if facing == '+X' else x0
    sgn = 1 if facing == '+X' else -1
    for k, wy in enumerate((y0 + 2.0, y1 - 2.4)):
        make_box(f"{prefix}_Window_{k}", (face_x + sgn * 0.02, wy, 1.6), (0.04, 1.2, 1.1), (0.30, 0.36, 0.40, 1.0))
        make_box(f"{prefix}_Window_{k}_Trim", (face_x + sgn * 0.04, wy, 1.0), (0.04, 1.36, 0.10), (0.86, 0.82, 0.72, 1.0))
    make_box(f"{prefix}_Wainscot", (face_x + sgn * 0.02, cy, 0.25), (0.04, y1 - y0, 0.50), (0.84, 0.78, 0.66, 1.0))


def build_outside(truck):
    """West, through the window: the lawn strip, the side drive (and his
    truck in it, nose to the garage, or only its oil stain), the cedar
    fence, the neighbour's white stucco and tile, a fan palm, the next
    roof. East, through the back door: the patio, the lemon tree, the
    clothesline, the lawn, the fence, the live oak, a roofline."""
    make_box("Ground_West_Yard", (-16.35, 10.0, -0.13), (27.3, 60.0, 0.06), GRASS)
    make_box("Ground_West_Driveway", (-6.6, 2.5, -0.13), (3.4, 30.0, 0.062), CONCRETE)
    for k in range(5):
        make_box(f"Ground_West_Driveway_Joint_{k}", (-6.6, -6.0 + k * 4.5, -0.098), (3.4, 0.03, 0.002), (0.56, 0.54, 0.50, 1.0))
    make_box("Foundation_West_Grade", (-2.65, 2.5, -0.06), (0.10, 6.0, 0.14), (0.62, 0.60, 0.56, 1.0))
    if truck:
        make_car("Truck", -6.6, 5.0, 5.2, (0.34, 0.40, 0.48, 1.0), pickup=True, along="Y", z0=-0.10)
    else:
        make_box("Driveway_Oil_Stain", (-6.6, 5.6, -0.098), (0.9, 1.4, 0.002), (0.46, 0.44, 0.42, 1.0))
    # the fence on the lot line, the neighbour's house beyond it
    for k in range(16):
        y = -10.0 + k * 1.8
        make_box(f"West_Fence_Post_{k}", (-10.2, y, 0.65), (0.10, 0.10, 1.60), (0.56, 0.46, 0.36, 1.0))
    for k in range(2):
        make_box(f"West_Fence_Rail_{k}", (-10.15, 3.5, 0.35 + k * 0.75), (0.05, 27.0, 0.08), (0.56, 0.46, 0.36, 1.0))
    make_box("West_Fence_Boards", (-10.10, 3.5, 0.65), (0.03, 27.0, 1.50), (0.62, 0.50, 0.38, 1.0))
    # (2026-10-06: at 12 m the neighbour filled the window, no sky — 17 m now, past a side yard)
    _stucco_house("Neighbor_W", -27.0, -17.0, -4.0, 9.0, 3.0, '+X')
    _fan_palm("Palm_W", -8.8, 9.5, 7.5)
    _fan_palm("Palm_W2", -9.0, -4.5, 6.2)
    make_blob("Shrub_West_0", (-3.2, 0.6, 0.20), 0.45, (0.30, 0.42, 0.24, 1.0), noise=0.25, seed=31)
    make_blob("Shrub_West_1", (-3.2, 4.6, 0.20), 0.45, (0.30, 0.42, 0.24, 1.0), noise=0.25, seed=32)
    make_box("Neighbor_W2_Roof", (-20.0, 24.0, 4.0), (10.0, 9.0, 1.0), ROOF_TILE)
    make_box("Neighbor_W2_Wall", (-20.0, 24.0, 1.69), (9.0, 8.0, 3.62), STUCCO)
    _fan_palm("Palm_W3", -15.0, 1.0, 8.4)

    # east: the patio a step down, the yard, the fence, the oak
    make_box("Porch_Step", (XE + 0.45, DOOR_E_Y, -0.08), (0.30, 1.20, 0.16), CONCRETE)
    make_box("Patio_Slab", (XE + 2.30, 1.60, -0.23), (3.40, 4.40, 0.14), CONCRETE)
    make_box("Ground_East_Lawn", (XE + 15.2, 10.0, -0.30), (30.0, 60.0, 0.06), GRASS)
    make_lathe("Patio_Lemon_Pot", (XE + 1.30, 3.20, -0.16), [(0.20, 0.0), (0.26, 0.40), (0.0, 0.40)], TERRACOTTA, segments=12)
    make_taper_cyl("Patio_Lemon_Trunk", (XE + 1.30, 3.20, 0.60), 0.04, 0.03, 0.80, (0.42, 0.34, 0.24, 1.0), segments=6)
    make_blob("Patio_Lemon_Canopy", (XE + 1.30, 3.20, 1.30), 0.50, (0.26, 0.44, 0.22, 1.0), noise=0.25, seed=41)
    for k, (dx, dy, dz) in enumerate(((0.3, -0.2, 1.2), (-0.2, 0.3, 1.4), (0.1, 0.35, 1.05), (-0.3, -0.2, 1.3))):
        make_blob(f"Patio_Lemon_Fruit_{k}", (XE + 1.30 + dx, 3.20 + dy, dz), 0.045, (0.96, 0.84, 0.20, 1.0), noise=0.1, seed=k)
    make_box("Patio_Chair_Seat", (XE + 2.40, 0.40, 0.24), (0.48, 0.48, 0.04), (0.94, 0.94, 0.92, 1.0))
    make_box("Patio_Chair_Back", (XE + 2.62, 0.40, 0.52), (0.04, 0.48, 0.52), (0.94, 0.94, 0.92, 1.0))
    for k, (dx, dy) in enumerate(((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2))):
        make_box(f"Patio_Chair_Leg_{k}", (XE + 2.40 + dx, 0.40 + dy, 0.03), (0.03, 0.03, 0.38), (0.94, 0.94, 0.92, 1.0))
    for k, y in enumerate((-1.5, 4.5)):
        make_box(f"Clothesline_Post_{k}", (XE + 5.5, y, 0.85), (0.08, 0.08, 2.30), (0.62, 0.62, 0.60, 1.0))
        make_box(f"Clothesline_Post_{k}_Arm", (XE + 5.5, y, 1.95), (0.90, 0.06, 0.06), (0.62, 0.62, 0.60, 1.0))
    for k in range(3):
        make_cyl(f"Clothesline_Line_{k}", (XE + 5.1 + k * 0.4, 1.5, 1.94), 0.004, 6.0, (0.90, 0.90, 0.88, 1.0), axis='Y', segments=4)
    for k, (y, col) in enumerate(((0.2, (0.94, 0.94, 0.92, 1.0)), (0.9, (0.74, 0.20, 0.18, 1.0)), (2.0, (0.30, 0.46, 0.66, 1.0)))):
        make_box(f"Clothesline_Towel_{k}", (XE + 5.1 + (k % 3) * 0.4, y, 1.64), (0.02, 0.50, 0.60), col)
    make_box("East_Fence_Boards", (XE + 14.0, 2.5, 0.60), (0.04, 30.0, 1.80), (0.62, 0.50, 0.38, 1.0))
    for k in range(17):
        make_box(f"East_Fence_Post_{k}", (XE + 13.95, -12.0 + k * 1.8, 0.62), (0.10, 0.10, 1.86), (0.56, 0.46, 0.36, 1.0))
    make_taper_cyl("Oak_East_Trunk", (XE + 10.0, 6.0, 1.6), 0.36, 0.24, 3.8, (0.36, 0.30, 0.24, 1.0), segments=10)
    for k, (dx, dy, dz, r) in enumerate(((0.0, 0.0, 4.6, 2.6), (1.8, 1.0, 4.0, 1.9), (-1.6, -0.8, 4.2, 2.0), (0.6, -1.8, 4.8, 1.7))):
        make_blob(f"Oak_East_Canopy_{k}", (XE + 10.0 + dx, 6.0 + dy, dz), r, (0.28, 0.40, 0.22, 1.0), noise=0.25, seed=50 + k)
    make_box("Neighbor_E_Wall", (XE + 21.0, 2.0, 1.4), (8.0, 12.0, 3.4), STUCCO)
    make_box("Neighbor_E_Roof", (XE + 21.0, 2.0, 3.6), (9.0, 13.0, 1.0), ROOF_TILE)


# ── each locale's dressing ─────────────────────────────────────────
def dress_morning_eggs():
    """grandmother_kitchen_morning: ch 16 / 18 / 22 / 23 — the yellow
    plate with the chip at his place, his coffee, her Sentinel, the
    small bowl of fruit, the second letter and its pen, the microwave
    (the plate in it), the caldo on the back of the stove, the comal,
    the skillet she makes the eggs in, the moka pot, the onion and the
    bay leaf on the board."""
    top = 0.745
    dx, dy = TX + 0.26, TY                      # his place, east, facing the window
    make_taper_cyl("Yellow_Plate", (dx, dy, top + 0.010), 0.08, 0.12, 0.02, (0.94, 0.80, 0.30, 1.0), segments=16)
    make_box("Yellow_Plate_Chip", (dx + 0.06, dy - 0.095, top + 0.019), (0.022, 0.012, 0.004), (0.96, 0.93, 0.80, 1.0))
    make_blob("Yellow_Plate_Eggs", (dx, dy + 0.01, top + 0.03), 0.06, (0.98, 0.86, 0.42, 1.0), noise=0.2, seed=7)
    make_box("Yellow_Plate_Tortilla", (dx - 0.05, dy - 0.05, top + 0.022), (0.08, 0.06, 0.004), (0.92, 0.84, 0.64, 1.0))
    make_box("Fork_Diego", (dx + 0.15, dy, top + 0.003), (0.02, 0.18, 0.004), CHROME)
    make_cyl("Coffee_Mug_Diego", (dx + 0.06, dy + 0.18, top + 0.048), 0.04, 0.095, (0.26, 0.40, 0.62, 1.0), segments=10)
    make_box("Coffee_Mug_Diego_Handle", (dx + 0.105, dy + 0.18, top + 0.05), (0.016, 0.03, 0.05), (0.26, 0.40, 0.62, 1.0))
    # her place, north: the Sentinel folded to the local page, her coffee
    make_box("Sentinel_Paper", (TX - 0.02, TY + 0.27, top + 0.006), (0.30, 0.20, 0.012), (0.90, 0.88, 0.82, 1.0))
    make_box("Sentinel_Paper_Masthead", (TX - 0.02, TY + 0.34, top + 0.0125), (0.26, 0.04, 0.001), (0.18, 0.18, 0.20, 1.0))
    for k in range(4):
        make_box(f"Sentinel_Paper_Column_{k}", (TX - 0.12 + k * 0.065, TY + 0.24, top + 0.0125), (0.05, 0.12, 0.001),
                 (0.56, 0.56, 0.56, 1.0))
    make_cyl("Coffee_Cup_Graciela", (TX + 0.17, TY + 0.30, top + 0.035), 0.034, 0.07, (0.96, 0.94, 0.90, 1.0), segments=10)
    make_cyl("Coffee_Cup_Graciela_Saucer", (TX + 0.17, TY + 0.30, top + 0.004), 0.065, 0.008, (0.96, 0.94, 0.90, 1.0), segments=12)
    # the small bowl of fruit
    make_taper_cyl("Fruit_Bowl", (TX - 0.12, TY - 0.10, top + 0.03), 0.06, 0.11, 0.06, TALAVERA_BLUE, segments=12)
    for k, (fx, fy, col) in enumerate(((-0.03, 0.0, (0.96, 0.62, 0.18, 1.0)), (0.04, 0.02, (0.80, 0.20, 0.18, 1.0)),
                                       (0.0, -0.05, (0.56, 0.68, 0.24, 1.0)), (0.0, 0.05, (0.98, 0.84, 0.30, 1.0)))):
        make_blob(f"Fruit_{k}", (TX - 0.12 + fx, TY - 0.10 + fy, top + 0.08), 0.036, col, noise=0.1, seed=k + 60)
    # THE SECOND LETTER and its pen, at the south place
    make_box("Second_Letter", (TX + 0.04, TY - 0.30, top + 0.0015), (0.21, 0.28, 0.002), (0.96, 0.95, 0.90, 1.0))
    for k in range(6):
        make_box(f"Second_Letter_Line_{k}", (TX + 0.03, TY - 0.24 - k * 0.025, top + 0.003), (0.15, 0.004, 0.001),
                 (0.24, 0.26, 0.40, 1.0))
    make_box("Second_Letter_Envelope", (TX - 0.17, TY - 0.33, top + 0.003), (0.22, 0.11, 0.004), (0.92, 0.88, 0.78, 1.0))
    make_rot_box("Letter_Pen", (TX + 0.15, TY - 0.30, top + 0.006), (0.010, 0.14, 0.010), (0.16, 0.18, 0.30, 1.0), yaw=0.4)
    # the microwave on the counter (there is a plate in it)
    mx = 0.21
    make_chamfer_box("Microwave", (mx, 4.66, TOP_Z + 0.15), (0.50, 0.36, 0.30), (0.90, 0.89, 0.86, 1.0))
    make_box("Microwave_Door", (mx - 0.06, 4.476, TOP_Z + 0.15), (0.34, 0.012, 0.24), (0.18, 0.18, 0.20, 1.0))
    make_box("Microwave_Panel", (mx + 0.18, 4.476, TOP_Z + 0.15), (0.10, 0.012, 0.24), (0.30, 0.30, 0.32, 1.0))
    make_box("Microwave_Display", (mx + 0.18, 4.468, TOP_Z + 0.24), (0.07, 0.004, 0.025), (0.30, 0.66, 0.40, 1.0))
    # the stove: the caldo, the comal, the skillet, the moka
    make_lathe("Caldo_Pot", (SX - 0.19, 4.66, 0.93), [(0.11, 0.0), (0.12, 0.02), (0.12, 0.20), (0.125, 0.21), (0.0, 0.21)],
               (0.22, 0.34, 0.60, 1.0), segments=14)
    make_cyl("Caldo_Pot_Lid", (SX - 0.19, 4.66, 1.145), 0.12, 0.012, (0.22, 0.34, 0.60, 1.0), segments=14)
    make_cyl("Caldo_Pot_Lid_Knob", (SX - 0.19, 4.66, 1.165), 0.02, 0.025, IRON, segments=6)
    for k in range(5):
        ang = k * 1.256
        make_cyl(f"Caldo_Pot_Speckle_{k}", (SX - 0.19 + 0.122 * math.cos(ang), 4.66 + 0.122 * math.sin(ang), 1.04 + 0.03 * (k % 2)),
                 0.008, 0.002, (0.92, 0.92, 0.90, 1.0), segments=4)
    make_cyl("Comal", (SX + 0.19, 4.40, 0.936), 0.14, 0.008, IRON, segments=14)
    make_cyl("Comal_Tortilla", (SX + 0.19, 4.40, 0.942), 0.09, 0.004, (0.92, 0.84, 0.62, 1.0), segments=12)
    make_cyl("Iron_Skillet", (SX - 0.19, 4.45, 0.9475), 0.13, 0.035, (0.16, 0.16, 0.17, 1.0), segments=12)
    make_box("Iron_Skillet_Handle", (SX - 0.40, 4.45, 0.955), (0.16, 0.03, 0.014), (0.14, 0.14, 0.15, 1.0))
    make_lathe("Moka_Pot", (SX + 0.19, 4.73, 0.93), [(0.05, 0.0), (0.045, 0.08), (0.035, 0.09), (0.05, 0.17), (0.0, 0.19)],
               (0.70, 0.72, 0.74, 1.0), segments=8)
    make_box("Moka_Pot_Handle", (SX + 0.255, 4.73, 1.06), (0.03, 0.015, 0.07), IRON)
    make_box("Cutting_Board", (0.23, 4.36, TOP_Z + 0.01), (0.30, 0.18, 0.02), (0.78, 0.62, 0.40, 1.0))
    make_blob("Cutting_Board_Onion_Half", (0.17, 4.35, TOP_Z + 0.045), 0.04, (0.94, 0.88, 0.78, 1.0), noise=0.05, seed=2)
    make_box("Cutting_Board_Bay_Leaf", (0.31, 4.32, TOP_Z + 0.021), (0.06, 0.02, 0.002), (0.46, 0.52, 0.30, 1.0))
    make_box("Cutting_Board_Knife", (0.26, 4.41, TOP_Z + 0.023), (0.20, 0.022, 0.006), CHROME)


def dress_afternoon_rosary():
    """ramos_kitchen_morning: ch 1 (the afternoon Sam is asked) and
    ch 10 (the chorizo morning, the soup at 4:38). On the table: the
    rosary she is not using, the black coffee she is not drinking, the
    cordless phone face-up, charging; the soup at his place; the worn
    patches where the hands land. On the stove: the skillet with the
    eggs and chorizo, the soup pot, the moka. The truck is gone."""
    top = 0.745
    for k in range(20):
        ang = k * 2.0 * math.pi / 20.0
        make_cyl(f"Rosary_Bead_{k}", (TX - 0.05 + 0.07 * math.cos(ang), TY + 0.24 + 0.05 * math.sin(ang), top + 0.006),
                 0.007, 0.012, (0.30, 0.20, 0.14, 1.0), segments=6)
    make_box("Rosary_Cross", (TX - 0.05, TY + 0.13, top + 0.004), (0.03, 0.05, 0.006), (0.70, 0.56, 0.30, 1.0))
    make_cyl("Coffee_Cup_Black", (TX + 0.14, TY + 0.30, top + 0.035), 0.034, 0.07, (0.96, 0.94, 0.90, 1.0), segments=10)
    make_cyl("Coffee_Cup_Black_Surface", (TX + 0.14, TY + 0.30, top + 0.0705), 0.030, 0.002, (0.12, 0.08, 0.06, 1.0), segments=10)
    make_cyl("Coffee_Cup_Black_Saucer", (TX + 0.14, TY + 0.30, top + 0.004), 0.065, 0.008, (0.96, 0.94, 0.90, 1.0), segments=12)
    make_box("Cordless_Base", (TX - 0.22, TY - 0.16, top + 0.015), (0.10, 0.14, 0.03), (0.22, 0.22, 0.24, 1.0))
    make_box("Cordless_Handset", (TX - 0.22, TY - 0.16, top + 0.045), (0.05, 0.16, 0.03), (0.26, 0.26, 0.28, 1.0))
    make_box("Cordless_Handset_Screen", (TX - 0.22, TY - 0.12, top + 0.0605), (0.03, 0.04, 0.001), (0.62, 0.74, 0.66, 1.0))
    make_box("Cordless_Charge_Light", (TX - 0.22, TY - 0.235, top + 0.022), (0.012, 0.004, 0.008), (0.30, 0.96, 0.40, 1.0))
    make_cyl("Cordless_Cord", (TX - 0.22, TY - 0.38, top + 0.003), 0.003, 0.30, (0.12, 0.12, 0.12, 1.0), axis='Y', segments=4)
    for nm, hx, hy in (("A", TX - 0.02, TY - 0.20), ("B", TX + 0.30, TY + 0.06)):
        make_cyl(f"Hands_Worn_Patch_{nm}", (hx, hy, top + 0.0012), 0.06, 0.0012, (0.90, 0.88, 0.80, 1.0), segments=10)
    # the soup at his place
    dx, dy = TX + 0.26, TY
    make_taper_cyl("Soup_Bowl", (dx, dy, top + 0.03), 0.05, 0.085, 0.06, (0.94, 0.90, 0.82, 1.0), segments=14)
    make_cyl("Soup_Surface", (dx, dy, top + 0.055), 0.075, 0.004, (0.86, 0.62, 0.30, 1.0), segments=12)
    make_blob("Soup_Avocado", (dx + 0.02, dy + 0.01, top + 0.06), 0.025, (0.56, 0.68, 0.30, 1.0), noise=0.1, seed=9)
    make_box("Soup_Lime_Wedge", (dx - 0.03, dy - 0.02, top + 0.06), (0.03, 0.015, 0.012), (0.50, 0.70, 0.26, 1.0))
    make_box("Soup_Spoon", (dx + 0.14, dy - 0.02, top + 0.003), (0.02, 0.17, 0.005), CHROME)
    # the stove
    make_cyl("Iron_Skillet", (SX - 0.19, 4.45, 0.9475), 0.13, 0.035, (0.16, 0.16, 0.17, 1.0), segments=12)
    make_box("Iron_Skillet_Handle", (SX - 0.40, 4.45, 0.955), (0.16, 0.03, 0.014), (0.14, 0.14, 0.15, 1.0))
    make_blob("Iron_Skillet_Scrambled_Eggs", (SX - 0.19, 4.45, 0.97), 0.08, (0.98, 0.84, 0.44, 1.0), noise=0.25, seed=13)
    for k, (cx, cy) in enumerate(((-0.04, 0.03), (0.05, -0.02), (0.01, 0.05))):
        make_blob(f"Iron_Skillet_Chorizo_Crumble_{k}", (SX - 0.19 + cx, 4.45 + cy, 0.99), 0.016, (0.62, 0.22, 0.16, 1.0), noise=0.2, seed=k)
    make_lathe("Soup_Pot", (SX - 0.19, 4.66, 0.93), [(0.11, 0.0), (0.12, 0.02), (0.12, 0.20), (0.125, 0.21), (0.0, 0.21)],
               (0.70, 0.72, 0.74, 1.0), segments=14)
    make_cyl("Soup_Pot_Lid", (SX - 0.19, 4.66, 1.145), 0.12, 0.012, (0.70, 0.72, 0.74, 1.0), segments=14)
    make_lathe("Moka_Pot", (SX + 0.19, 4.73, 0.93), [(0.05, 0.0), (0.045, 0.08), (0.035, 0.09), (0.05, 0.17), (0.0, 0.19)],
               (0.70, 0.72, 0.74, 1.0), segments=8)
    make_box("Moka_Pot_Handle", (SX + 0.255, 4.73, 1.06), (0.03, 0.015, 0.07), IRON)
    make_cyl("Espresso_Cup", (SX + 0.19, 4.40, 0.955), 0.028, 0.05, (0.96, 0.94, 0.90, 1.0), segments=8)
    # on the counter where the microwave is in the other dressing: the coffee things
    make_box("Coffee_Tin", (0.12, 4.72, TOP_Z + 0.08), (0.12, 0.12, 0.16), (0.86, 0.72, 0.20, 1.0))
    make_box("Coffee_Tin_Label", (0.12, 4.659, TOP_Z + 0.08), (0.10, 0.002, 0.08), (0.20, 0.30, 0.52, 1.0))
    make_box("Sugar_Bowl", (0.32, 4.60, TOP_Z + 0.04), (0.09, 0.09, 0.08), (0.96, 0.94, 0.90, 1.0))


def build_kitchen(variant):
    """variant: 'eggs' (grandmother_kitchen_morning) or 'rosary'
    (ramos_kitchen_morning)."""
    build_shell()
    build_floor()
    build_window()
    build_table()
    build_counter_run()
    if variant == "eggs":
        build_range_and_fridge(8, 15)
    else:
        build_range_and_fridge(4, 38)
    build_east_wall()
    build_west_wall()
    build_south_wall_and_hall()
    build_ceiling_things()
    build_outside(truck=(variant == "eggs"))
    if variant == "eggs":
        dress_morning_eggs()
    else:
        dress_afternoon_rosary()
