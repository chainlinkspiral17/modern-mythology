"""THE MILLER KITCHEN — one room, two locales (2026-10-07).

`miller_kitchen` (vol 6 ch 0 / 11 / many: Mike at the counter at 6:24,
Eileen's cinnamon rolls, the French toast, the kolaches, the jar, the
white sedan at the curb) and `bianca_kitchen_morning` (ch 22 / 23:
Bianca's 4:11 coffee in the dark, the cordless, the stationery, Sammy's
cereal) are one kitchen on Meadowlark Circle. Both were store-kit
template boxes — a formica shop counter, a box fridge, a window that was
a pane on a solid wall, and no window at all over the sink although the
prose looks through one every morning ("The kitchen window faces the
front yard and the cul-de-sac"). Built BIG now (the user, 2026-10-07:
"Don't be afraid to make spaces and floorplans bigger"): a 9 x 7 m open
kitchen in a 2010s planned-community house, opening onto the family room
and the front hall.

From the prose:
  · "She turns on, instead, the small under-cabinet light over the sink"
    — the valance light over the sink window; the cul-de-sac through it,
    Don Geller's porch light across the way ("At five oh-two the porch
    light at the Gellers' across the way comes on").
  · "Her old chair had been at the long side of the table, with Mike
    across from her and Sammy at the head. Since June she has been
    sitting in Mike's chair, which is on the short side near the window."
  · "the green terrycloth robe is on the hook by the back door" ·
    "Sam's father is in the garage" (the lit garage window through the
    east glass) · "The landline never rings" · "they still get the
    Sentinel" · "a voice calls up the stairs" (the front hall's stair).

THE ROOM (blender, +Y north = the street side, z up):
  · N wall: the shaker run on `_props/kitchen_kit` — the French-door
    fridge, the coffee corner, the range under its hood, the double sink
    under the window with the valance light, the dishwasher, the drawer
    run; uppers either side of the window; subway tile.
  · the island with three stools; the breakfast table east under its
    pendant, four chairs (Sammy's head, Bianca's long side, Mike's short
    end by the east window, the guest).
  · E wall: the window (sheers) onto the drive and the garage; the back
    door, the robe on its hook. W wall: the pantry, the wall phone with
    its coiled cord, the calendar, the message board; the doorway to the
    front hall (the stair, the front door, the coat hooks).
  · S: a wide cased opening onto the family room — the sofa's back to the
    kitchen, the coffee table, the armchair, the TV on its console, the
    bookshelf, the floor lamp, the window onto the backyard.

Draft 2 of both locales. Draft 3 targets: the upstairs landing seen from
the stair's foot; the family room's evening practicals; Sammy's school
things on the island; the sedan's two silhouettes.
"""
import math

from .geometry import make_box, make_cyl, make_chamfer_box, make_taper_cyl, make_lathe, make_rot_box, make_blob, make_tube
from .structure import make_floor, make_ceiling, make_crown_molding, make_wall, make_wall_with_openings, make_window
from .decor import make_wall_clock, make_calendar
from .detail import make_wall_outlet, make_light_switch, make_traffic_wear, make_floor_stain, make_scuff_band, make_cord_run
from . import kitchen_kit as KK

X0, X1, Y0, Y1 = -4.5, 4.5, 0.0, 7.0
XW, XE, YS, YN = -4.4, 4.4, 0.1, 6.9
CEIL = 2.75
FR_Y = -5.0                                   # the family room's south wall line
HALL_X = -6.6                                 # the front hall's west wall line
TOP_Z = 0.98
TX, TY = 2.70, 3.40                           # the breakfast table
IX, IY = -1.20, 4.60                          # the island
SINK_X, RANGE_X, FRIDGE_X = -0.60, -2.30, -3.93
WIN_N = (SINK_X, 1.55, 1.50, 1.05)            # the sink window: x, z, w, h
WIN_E = (3.40, 1.55, 1.60, 1.15)              # the east window: y, z, w, h
DOOR_E_Y = 0.95
DOOR_HALL_Y = 1.60

PAL = {"wall": (0.93, 0.90, 0.82, 1.0), "baseboard": (0.92, 0.91, 0.87, 1.0)}
PAL_FR = {"wall": (0.82, 0.80, 0.72, 1.0), "baseboard": (0.92, 0.91, 0.87, 1.0)}
OAK = (0.62, 0.46, 0.30, 1.0)
OAK_DK = (0.42, 0.30, 0.20, 1.0)
WOOD_FLOOR = (0.66, 0.50, 0.34, 1.0)
TRIM = (0.94, 0.93, 0.89, 1.0)
STEEL = (0.62, 0.63, 0.64, 1.0)
PAPER = (0.93, 0.91, 0.85, 1.0)
FABRIC = (0.46, 0.50, 0.54, 1.0)


# ── the shell: kitchen, family room, front hall ────────────────────
def build_shell():
    make_floor("Floor", ((HALL_X + X1) / 2.0, (FR_Y + Y1) / 2.0, 0.0), size_x=X1 - HALL_X + 0.4, size_y=Y1 - FR_Y + 0.4,
               palette={"vinyl": WOOD_FLOOR, "seam": (0.48, 0.36, 0.24, 1.0)})
    # kitchen
    make_wall_with_openings("Wall_N", (0.0, Y1, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(WIN_N[0], WIN_N[1], WIN_N[2], WIN_N[3])])
    make_wall_with_openings("Wall_E", (X1, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(WIN_E[0], WIN_E[1], WIN_E[2], WIN_E[3]), (DOOR_E_Y, 1.04, 0.90, 2.08)])
    make_wall_with_openings("Wall_W", (X0, (Y0 + Y1) / 2.0, 0), length=Y1 - Y0 + 0.4, height=CEIL, axis='Y', palette=PAL,
                            baseboard_face_sign=+1, openings=[(DOOR_HALL_Y, 1.05, 0.90, 2.10)])
    make_wall_with_openings("Wall_S", (0.0, Y0, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(0.50, 1.15, 5.00, 2.30)])
    # family room
    make_wall_with_openings("FR_Wall_S", (0.0, FR_Y, 0), length=X1 - X0 + 0.4, height=CEIL, axis='X', palette=PAL_FR,
                            baseboard_face_sign=+1, openings=[(-2.40, 1.55, 1.80, 1.30)])
    make_wall("FR_Wall_E", (X1, FR_Y / 2.0, 0), length=-FR_Y, height=CEIL, axis='Y', palette=PAL_FR, baseboard_face_sign=-1)
    make_wall("FR_Wall_W", (X0, FR_Y / 2.0, 0), length=-FR_Y, height=CEIL, axis='Y', palette=PAL_FR, baseboard_face_sign=+1)
    # the front hall, west of the kitchen: the stair, the front door at its north end
    make_wall("Hall_Wall_W", (HALL_X, (FR_Y + Y1) / 2.0, 0), length=Y1 - FR_Y + 0.4, height=CEIL, axis='Y', palette=PAL_FR,
              baseboard_face_sign=+1)
    make_wall_with_openings("Hall_Wall_N", ((HALL_X + X0) / 2.0, Y1, 0), length=X0 - HALL_X, height=CEIL, axis='X',
                            palette=PAL_FR, baseboard_face_sign=-1, openings=[(-5.55, 1.04, 0.95, 2.08)])
    make_wall("Hall_Wall_S", ((HALL_X + X0) / 2.0, FR_Y, 0), length=X0 - HALL_X, height=CEIL, axis='X', palette=PAL_FR,
              baseboard_face_sign=+1)
    make_ceiling("Ceil", ((HALL_X + X1) / 2.0, (FR_Y + Y1) / 2.0, CEIL), size_x=X1 - HALL_X + 0.4, size_y=Y1 - FR_Y + 0.4,
                 with_grid=False, palette={"tile": (0.96, 0.95, 0.92, 1.0)})
    for nm, ax, length, wx, wy in (("Crown_N", 'X', X1 - X0, 0.0, YN), ("Crown_E", 'Y', Y1 - Y0, XE, 3.5)):
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": TRIM})
    # trim: the cased opening to the family room, the hall doorway, the back door
    for sgn in (-1, 1):
        make_box(f"FR_Opening_Casing_{'W' if sgn < 0 else 'E'}", (0.50 + sgn * 2.54, YS + 0.01, 1.15), (0.08, 0.02, 2.30), TRIM)
    make_box("FR_Opening_Casing_Head", (0.50, YS + 0.01, 2.34), (5.16, 0.02, 0.10), TRIM)
    for sgn in (-1, 1):
        make_box(f"Hall_Doorway_Casing_{'S' if sgn < 0 else 'N'}", (XW + 0.01, DOOR_HALL_Y + sgn * 0.49, 1.06), (0.02, 0.08, 2.12), TRIM)
        make_box(f"Back_Door_Casing_{'S' if sgn < 0 else 'N'}", (XE - 0.01, DOOR_E_Y + sgn * 0.49, 1.06), (0.02, 0.08, 2.12), TRIM)
    make_box("Hall_Doorway_Casing_Head", (XW + 0.01, DOOR_HALL_Y, 2.15), (0.02, 1.06, 0.10), TRIM)
    make_box("Back_Door_Casing_Head", (XE - 0.01, DOOR_E_Y, 2.13), (0.02, 1.06, 0.10), TRIM)
    make_box("Back_Door", (X1, DOOR_E_Y, 1.04), (0.05, 0.86, 2.06), (0.92, 0.91, 0.87, 1.0))
    make_box("Back_Door_Window", (X1 - 0.027, DOOR_E_Y, 1.55), (0.004, 0.50, 0.70), (0.62, 0.70, 0.74, 1.0))
    make_cyl("Back_Door_Knob", (X1 - 0.045, DOOR_E_Y - 0.33, 1.00), 0.028, 0.04, (0.70, 0.66, 0.58, 1.0), axis='X', segments=8)
    # THE GREEN TERRYCLOTH ROBE on its hook by the back door
    make_cyl("Robe_Hook", (XE - 0.03, DOOR_E_Y + 0.80, 1.62), 0.015, 0.06, (0.30, 0.28, 0.26, 1.0), axis='X', segments=6)
    make_box("Green_Robe", (XE - 0.09, DOOR_E_Y + 0.80, 1.18), (0.10, 0.34, 0.86), (0.30, 0.52, 0.36, 1.0))
    make_box("Green_Robe_Collar", (XE - 0.10, DOOR_E_Y + 0.80, 1.585), (0.12, 0.22, 0.06), (0.26, 0.46, 0.32, 1.0))
    make_box("Green_Robe_Belt", (XE - 0.145, DOOR_E_Y + 0.80, 1.05), (0.012, 0.30, 0.05), (0.26, 0.46, 0.32, 1.0))
    make_light_switch("Switch_Hall", (X0, DOOR_HALL_Y + 0.62), axis='Y', face_sign=1, z=1.20)
    make_light_switch("Switch_Back", (X1, DOOR_E_Y - 0.62), axis='Y', face_sign=-1, z=1.20)
    make_light_switch("Switch_FR", (-2.20, Y0), axis='X', face_sign=1, z=1.20)


# ── the north run on the kitchen kit ───────────────────────────────
def build_north_run():
    KK.fridge("Fridge", FRIDGE_X, YN, width=0.86, height=1.78)
    for k, (dx, z, w, h, col) in enumerate(((-0.12, 1.42, 0.10, 0.14, (0.42, 0.50, 0.66, 1.0)), (0.10, 1.48, 0.09, 0.09, (0.86, 0.74, 0.62, 1.0)),
                                            (0.00, 1.20, 0.20, 0.27, (0.98, 0.96, 0.90, 1.0)), (-0.14, 0.95, 0.16, 0.22, (0.92, 0.90, 0.86, 1.0)))):
        make_box(f"Fridge_Magnet_Paper_{k}", (FRIDGE_X + dx, YN - 0.74 - 0.042, z), (w, 0.003, h), col)
    KK.upper_run("Upper_Fridge", FRIDGE_X - 0.43, FRIDGE_X + 0.43, YN, z0=1.86, z1=2.36)
    gaps = [(RANGE_X - 0.38, RANGE_X + 0.38), (0.20, 0.80)]
    KK.base_run("Counter_N", -3.48, 1.90, YN, depth=0.62, top_z=TOP_Z, gaps=gaps)
    make_box("Counter_N_DW_Top", (0.50, YN - 0.31 - 0.0125, TOP_Z - 0.02), (0.60, 0.645, 0.04), KK.QUARTZ)
    KK.dishwasher("Dishwasher", 0.50, YN - 0.62, TOP_Z, width=0.60)
    KK.range_("Range", RANGE_X, YN, TOP_Z, width=0.76)
    KK.sink("Sink", SINK_X, YN, TOP_Z)
    # backsplash: full height either side, to the sill under the window
    sill = WIN_N[1] - WIN_N[3] / 2.0
    wx0, wx1 = WIN_N[0] - WIN_N[2] / 2.0, WIN_N[0] + WIN_N[2] / 2.0
    KK.backsplash("Backsplash_W", -3.48, wx0, YN, TOP_Z, 1.46)
    KK.backsplash("Backsplash_Sink", wx0, wx1, YN, TOP_Z, sill)
    KK.backsplash("Backsplash_E", wx1, 1.90, YN, TOP_Z, 1.46)
    # uppers either side of the window, the hood over the range
    KK.upper_run("Upper_W", -3.48, RANGE_X - 0.40, YN)
    KK.upper_run("Upper_Mid", RANGE_X + 0.40, wx0 - 0.08, YN)
    KK.upper_run("Upper_E", wx1 + 0.08, 1.90, YN)
    make_box("Range_Hood", (RANGE_X, YN - 0.24, 1.68), (0.78, 0.48, 0.16), KK.STAINLESS)
    make_box("Range_Hood_Chimney", (RANGE_X, YN - 0.14, (1.76 + CEIL) / 2.0), (0.36, 0.28, CEIL - 1.76), KK.STAINLESS)
    make_box("Range_Hood_Lamp_Lens", (RANGE_X + 0.20, YN - 0.30, 1.598), (0.12, 0.08, 0.004), (0.98, 0.92, 0.72, 1.0))
    # the sink window: frame, sill, the valance with THE LIGHT OVER THE SINK
    make_window("Sink_Window", (WIN_N[0], YN, WIN_N[1]), width=WIN_N[2], height=WIN_N[3], see_through=True,
                palette={"frame": TRIM})
    make_box("Sink_Window_Sill", (WIN_N[0], YN - 0.08, sill - 0.015), (WIN_N[2] + 0.20, 0.16, 0.03), TRIM)
    make_box("Sink_Valance", (WIN_N[0], YN - 0.15, 2.20), (WIN_N[2] + 0.24, 0.30, 0.18), KK.WHITE_SHAKER)
    make_box("UnderCab_Light", (WIN_N[0], YN - 0.20, 2.104), (WIN_N[2], 0.05, 0.012), (0.98, 0.92, 0.74, 1.0))
    for k, (dx, col) in enumerate(((-0.45, (0.40, 0.56, 0.36, 1.0)), (0.40, (0.86, 0.30, 0.24, 1.0)))):
        make_taper_cyl(f"Sink_Window_Sill_Pot_{k}", (WIN_N[0] + dx, YN - 0.08, sill + 0.05), 0.045, 0.06, 0.10, (0.70, 0.40, 0.26, 1.0), segments=8)
        make_blob(f"Sink_Window_Sill_Pot_{k}_Leaves", (WIN_N[0] + dx, YN - 0.08, sill + 0.15), 0.07, col, noise=0.25, seed=k)
    # the coffee corner and the counter's working things
    make_box("Coffee_Maker_Base", (-3.15, YN - 0.24, TOP_Z + 0.02), (0.24, 0.26, 0.04), (0.14, 0.14, 0.15, 1.0))
    make_box("Coffee_Maker_Body", (-3.15, YN - 0.12, TOP_Z + 0.20), (0.24, 0.12, 0.40), (0.14, 0.14, 0.15, 1.0))
    make_lathe("Coffee_Maker_Carafe", (-3.15, YN - 0.26, TOP_Z + 0.04), [(0.07, 0.0), (0.08, 0.06), (0.07, 0.14), (0.04, 0.17), (0.0, 0.17)],
               (0.30, 0.22, 0.16, 1.0), segments=10)
    make_box("Coffee_Canister", (-2.90, YN - 0.15, TOP_Z + 0.10), (0.12, 0.12, 0.20), (0.86, 0.84, 0.80, 1.0))
    make_box("Microwave", (1.35, YN - 0.24, TOP_Z + 0.16), (0.52, 0.38, 0.32), KK.STAINLESS)
    make_box("Microwave_Door", (1.29, YN - 0.435, TOP_Z + 0.16), (0.38, 0.01, 0.26), (0.12, 0.12, 0.14, 1.0))
    make_box("Paper_Towel_Base", (0.05, YN - 0.20, TOP_Z + 0.006), (0.14, 0.14, 0.012), STEEL)
    make_cyl("Paper_Towel_Roll", (0.05, YN - 0.20, TOP_Z + 0.14), 0.06, 0.26, (0.96, 0.94, 0.90, 1.0), segments=10)
    make_box("Dish_Soap", (SINK_X + 0.36, YN - 0.08, TOP_Z + 0.09), (0.05, 0.035, 0.18), (0.30, 0.62, 0.40, 1.0))
    make_box("Fruit_Bowl_Counter_Base", (1.00, YN - 0.30, TOP_Z + 0.005), (0.01, 0.01, 0.01), (0.90, 0.88, 0.84, 1.0))
    make_taper_cyl("Fruit_Bowl_Counter", (0.95, YN - 0.30, TOP_Z + 0.04), 0.07, 0.14, 0.08, (0.88, 0.86, 0.80, 1.0), segments=12)
    for k, (fx, fy, col) in enumerate(((-0.04, 0.0, (0.94, 0.70, 0.20, 1.0)), (0.05, 0.03, (0.80, 0.20, 0.18, 1.0)), (0.0, -0.05, (0.56, 0.70, 0.26, 1.0)))):
        make_blob(f"Fruit_Counter_{k}", (0.95 + fx, YN - 0.30 + fy, TOP_Z + 0.10), 0.04, col, noise=0.1, seed=k + 30)
    make_wall_outlet("Outlet_Counter_W", (-2.85, Y1), axis='X', face_sign=-1, z=1.12)
    make_wall_outlet("Outlet_Counter_E", (1.55, Y1), axis='X', face_sign=-1, z=1.12)


# ── the island, the table, the chairs ─────────────────────────────
def build_island_and_table():
    w, d = 2.60, 1.00
    make_box("Island_Kick", (IX, IY + 0.05, 0.05), (w - 0.10, d - 0.10, 0.10), (0.20, 0.20, 0.20, 1.0))
    make_box("Island_Carcass", (IX, IY + 0.12, 0.52), (w, d - 0.24, 0.84), (0.30, 0.38, 0.46, 1.0))
    for k in range(4):
        dx = IX - w / 2.0 + w / 8.0 + k * w / 4.0
        make_box(f"Island_Door_{k}", (dx, IY + 0.12 + (d - 0.24) / 2.0 + 0.009, 0.42), (w / 4.0 - 0.012, 0.018, 0.58), (0.30, 0.38, 0.46, 1.0))
        make_box(f"Island_Door_{k}_Pull", (dx + 0.12 * (1 if k % 2 else -1), IY + 0.12 + (d - 0.24) / 2.0 + 0.026, 0.58),
                 (0.012, 0.016, 0.12), KK.NICKEL)
    make_box("Island_Top", (IX, IY, 0.96), (w + 0.06, d + 0.06, 0.04), KK.QUARTZ)
    for k in range(3):
        sx = IX - 0.80 + k * 0.80
        sy = IY - d / 2.0 - 0.30
        make_cyl(f"Island_Stool_{k}_Seat", (sx, sy, 0.66), 0.19, 0.05, OAK, segments=12)
        for e, (lx, ly) in enumerate(((-0.13, -0.13), (0.13, -0.13), (-0.13, 0.13), (0.13, 0.13))):
            make_rot_box(f"Island_Stool_{k}_Leg_{e}", (sx + lx, sy + ly, 0.32), (0.03, 0.03, 0.64), OAK_DK, roll=lx * 0.3, pitch=-ly * 0.3)
        make_box(f"Island_Stool_{k}_Ring", (sx, sy, 0.24), (0.30, 0.30, 0.02), OAK_DK)
        make_box(f"Island_Stool_{k}_Back", (sx, sy - 0.17, 0.88), (0.34, 0.04, 0.40), OAK)
    # the breakfast table: rectangular, the seating motif is its long and short sides
    make_box("Table_Top", (TX, TY, 0.745), (1.60, 0.95, 0.05), OAK)
    make_box("Table_Apron", (TX, TY, 0.67), (1.48, 0.83, 0.10), OAK_DK)
    for li, (lx, ly) in enumerate(((-0.70, -0.38), (0.70, -0.38), (-0.70, 0.38), (0.70, 0.38))):
        make_taper_cyl(f"Table_Leg_{li}", (TX + lx, TY + ly, 0.31), 0.03, 0.025, 0.62, OAK_DK, segments=8)
    chairs = (("Chair_Head_Sammy", TX - 1.12, TY, "-X"), ("Chair_Long_Bianca", TX, TY - 0.90, "-Y"),
              ("Chair_Short_Mike", TX + 1.12, TY, "+X"), ("Chair_Long_Guest", TX, TY + 0.90, "+Y"))
    for nm, cx, cy, back in chairs:
        make_box(f"{nm}_Seat", (cx, cy, 0.45), (0.44, 0.44, 0.04), OAK)
        for li, (lx, ly) in enumerate(((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18))):
            make_taper_cyl(f"{nm}_Leg_{li}", (cx + lx, cy + ly, 0.215), 0.02, 0.016, 0.43, OAK_DK, segments=6)
        bx = {"-X": -0.20, "+X": 0.20}.get(back, 0.0)
        by = {"-Y": -0.20, "+Y": 0.20}.get(back, 0.0)
        sz = (0.04, 0.42, 0.56) if bx else (0.42, 0.04, 0.56)
        make_box(f"{nm}_Back", (cx + bx, cy + by, 0.75), sz, OAK)
        make_box(f"{nm}_Cushion", (cx, cy, 0.48), (0.38, 0.38, 0.03), (0.70, 0.66, 0.56, 1.0))
    make_box("Table_Runner", (TX, TY, 0.7715), (1.20, 0.28, 0.003), (0.62, 0.30, 0.24, 1.0))
    make_taper_cyl("Table_Napkin_Holder", (TX - 0.45, TY + 0.10, 0.80), 0.05, 0.05, 0.05, OAK_DK, segments=6)


# ── the west wall and the front hall ──────────────────────────────
def build_west_and_hall():
    # the pantry door, the wall phone, the calendar, the message board
    make_box("Pantry_Door", (XW + 0.025, 4.60, 1.04), (0.05, 0.80, 2.06), KK.WHITE_SHAKER)
    make_cyl("Pantry_Knob", (XW + 0.07, 4.30, 1.00), 0.025, 0.04, KK.NICKEL, axis='X', segments=8)
    for sgn in (-1, 1):
        make_box(f"Pantry_Casing_{sgn:+d}", (XW + 0.01, 4.60 + sgn * 0.44, 1.06), (0.02, 0.08, 2.12), TRIM)
    beige, beige_dk = (0.82, 0.78, 0.68, 1.0), (0.68, 0.63, 0.53, 1.0)
    px, py, pz = XW, 3.40, 1.42
    make_box("Phone_Wall_Base", (px + 0.0275, py, pz), (0.055, 0.095, 0.22), beige)
    make_box("Phone_Wall_Handset", (px + 0.075, py, pz + 0.02), (0.045, 0.062, 0.19), beige_dk)
    make_box("Phone_Wall_Cradle", (px + 0.065, py, pz + 0.115), (0.03, 0.075, 0.02), beige_dk)
    make_box("Phone_Wall_Dial", (px + 0.058, py, pz - 0.055), (0.006, 0.05, 0.06), (0.30, 0.28, 0.26, 1.0))
    for ci, (dy, dz) in enumerate(((0.05, -0.16), (0.11, -0.26), (0.16, -0.18))):
        make_cyl(f"Phone_Wall_Cord_{ci}", (px + 0.06, py + dy, pz + dz), 0.011, 0.14, beige_dk, segments=6)
    make_box("Wear_Phone_HandPatch", (XW + 0.005, py, 1.28), (0.01, 0.16, 0.14), (0.86, 0.83, 0.75, 1.0))
    make_box("PhoneJack_Plate", (XW + 0.006, py, 0.42), (0.012, 0.07, 0.11), (0.82, 0.79, 0.72, 1.0))
    make_calendar("Calendar", (XW + 0.003, 2.55, 1.60))
    make_box("Message_Board", (XW + 0.012, 5.70, 1.50), (0.024, 0.80, 0.60), (0.66, 0.52, 0.36, 1.0))
    for k, (dy, dz, w, h, col) in enumerate(((-0.25, 0.12, 0.18, 0.24, PAPER), (0.02, 0.15, 0.20, 0.14, (0.96, 0.86, 0.50, 1.0)),
                                             (0.24, 0.08, 0.16, 0.22, (0.86, 0.90, 0.96, 1.0)), (-0.10, -0.15, 0.24, 0.16, PAPER),
                                             (0.20, -0.16, 0.14, 0.10, (0.62, 0.74, 0.86, 1.0)))):
        make_box(f"Message_Board_Paper_{k}", (XW + 0.026, 5.70 + dy, 1.50 + dz), (0.004, w, h), col)
    make_box("Key_Hooks", (XW + 0.015, DOOR_HALL_Y + 0.75, 1.45), (0.03, 0.30, 0.06), OAK)
    # THE FRONT HALL: the stair rising south, the front door at the north end, coat hooks
    hx = (HALL_X + X0) / 2.0
    make_box("Hall_Runner", (hx, 2.5, 0.004), (0.90, 6.0, 0.008), (0.40, 0.24, 0.20, 1.0))
    make_box("Front_Door", (-5.55, Y1 - 0.025, 1.04), (0.92, 0.05, 2.06), (0.30, 0.22, 0.18, 1.0))
    for k, (dx, dz) in enumerate(((-0.20, 1.50), (0.20, 1.50), (-0.20, 0.55), (0.20, 0.55))):
        make_box(f"Front_Door_Panel_{k}", (-5.55 + dx, Y1 - 0.054, dz), (0.30, 0.008, 0.70 if dz > 1 else 0.60), (0.24, 0.18, 0.15, 1.0))
    make_cyl("Front_Door_Knob", (-5.55 + 0.36, Y1 - 0.07, 1.00), 0.028, 0.04, (0.80, 0.66, 0.34, 1.0), axis='Y', segments=8)
    make_box("Hall_Coat_Rail", (HALL_X + 0.115, 5.40, 1.65), (0.03, 0.90, 0.08), OAK_DK)
    for k, col in enumerate(((0.30, 0.34, 0.42, 1.0), (0.62, 0.46, 0.30, 1.0), (0.24, 0.24, 0.26, 1.0))):
        make_box(f"Hall_Coat_{k}", (HALL_X + 0.18, 5.10 + k * 0.30, 1.22), (0.12, 0.26, 0.80), col)
    for k in range(9):
        y = 0.80 - k * 0.28
        h = 0.19 * (k + 1)
        make_box(f"Stair_Tread_{k}", (HALL_X + 0.60, y, h / 2.0), (0.96, 0.28, h), OAK)
        make_box(f"Stair_Tread_{k}_Nose", (HALL_X + 0.60, y + 0.13, h - 0.012), (0.98, 0.04, 0.025), OAK_DK)
    make_box("Stair_Newel", (HALL_X + 1.14, 1.00, 0.60), (0.09, 0.09, 1.20), TRIM)
    make_rot_box("Stair_Handrail", (HALL_X + 1.14, -0.30, 1.48), (0.05, 2.70, 0.06), OAK_DK, roll=0.0, pitch=0.0, yaw=0.0)
    for k in range(8):
        y = 0.70 - k * 0.28
        z0 = 0.19 * (k + 1)
        make_box(f"Stair_Baluster_{k}", (HALL_X + 1.14, y, z0 + (1.45 - z0) / 2.0), (0.025, 0.025, 1.45 - z0), TRIM)
    for k in range(3):
        make_box(f"Hall_Photo_{k}_Frame", (HALL_X + 0.112, 2.60 + k * 0.55, 1.55), (0.024, 0.34, 0.42), OAK_DK)
        make_box(f"Hall_Photo_{k}", (HALL_X + 0.126, 2.60 + k * 0.55, 1.55), (0.004, 0.28, 0.34),
                 ((0.58, 0.52, 0.44, 1.0), (0.44, 0.56, 0.66, 1.0), (0.66, 0.60, 0.50, 1.0))[k])


# ── the family room through the opening ───────────────────────────
def build_family_room():
    make_box("FR_Rug", (0.6, -2.6, 0.004), (3.80, 2.80, 0.008), (0.54, 0.46, 0.40, 1.0))
    make_box("FR_Rug_Border", (0.6, -2.6, 0.0085), (3.50, 2.50, 0.001), (0.42, 0.32, 0.28, 1.0))
    # the sofa, its back to the kitchen, facing the TV
    sx, sy = 0.6, -1.40
    make_box("FR_Sofa_Base", (sx, sy, 0.22), (2.20, 0.90, 0.30), FABRIC)
    make_box("FR_Sofa_Back", (sx, sy + 0.36, 0.62), (2.20, 0.20, 0.55), FABRIC)
    for e in (-1, 1):
        make_box(f"FR_Sofa_Arm_{e:+d}", (sx + e * 1.02, sy, 0.50), (0.16, 0.90, 0.30), FABRIC)
    for k in range(3):
        make_box(f"FR_Sofa_Cushion_{k}", (sx - 0.62 + k * 0.62, sy - 0.08, 0.43), (0.60, 0.70, 0.12), (0.50, 0.54, 0.58, 1.0))
    make_rot_box("FR_Sofa_Throw", (sx + 0.70, sy + 0.20, 0.72), (0.50, 0.30, 0.08), (0.70, 0.40, 0.30, 1.0), yaw=0.3)
    for e in (-1, 1):
        make_box(f"FR_Sofa_Foot_{e:+d}", (sx + e * 0.95, sy, 0.035), (0.06, 0.70, 0.07), OAK_DK)
    make_box("FR_Coffee_Table", (sx, -2.70, 0.40), (1.20, 0.60, 0.05), OAK)
    for li, (lx, ly) in enumerate(((-0.54, -0.24), (0.54, -0.24), (-0.54, 0.24), (0.54, 0.24))):
        make_box(f"FR_Coffee_Table_Leg_{li}", (sx + lx, -2.70 + ly, 0.19), (0.05, 0.05, 0.38), OAK_DK)
    make_box("FR_Coffee_Table_Magazines", (sx - 0.30, -2.75, 0.4335), (0.28, 0.22, 0.017), (0.70, 0.30, 0.26, 1.0))
    make_box("FR_Coffee_Table_Remote", (sx + 0.25, -2.62, 0.4325), (0.05, 0.18, 0.015), (0.14, 0.14, 0.15, 1.0))
    # the TV on its console on the south wall
    make_box("FR_TV_Console", (sx, FR_Y + 0.33, 0.30), (1.80, 0.45, 0.60), OAK_DK)
    make_box("FR_TV", (sx, FR_Y + 0.13, 1.30), (1.40, 0.06, 0.80), (0.08, 0.08, 0.09, 1.0))
    make_box("FR_TV_Screen", (sx, FR_Y + 0.162, 1.30), (1.34, 0.004, 0.74), (0.16, 0.20, 0.26, 1.0))
    # the armchair, the floor lamp, the bookshelf
    make_box("FR_Armchair_Base", (3.30, -2.70, 0.22), (0.86, 0.86, 0.44), (0.56, 0.42, 0.32, 1.0))
    make_box("FR_Armchair_Back", (3.66, -2.70, 0.66), (0.16, 0.86, 0.60), (0.56, 0.42, 0.32, 1.0))
    for e in (-1, 1):
        make_box(f"FR_Armchair_Arm_{e:+d}", (3.30, -2.70 + e * 0.37, 0.52), (0.86, 0.14, 0.26), (0.56, 0.42, 0.32, 1.0))
    make_lathe("FR_Floor_Lamp", (2.70, -0.70, 0.0), [(0.14, 0.0), (0.14, 0.03), (0.015, 0.05), (0.015, 1.50), (0.0, 1.50)], STEEL, segments=8)
    make_taper_cyl("FR_Floor_Lamp_Shade", (2.70, -0.70, 1.58), 0.20, 0.14, 0.26, (0.94, 0.88, 0.72, 1.0), segments=12)
    make_box("FR_Bookshelf", (XE - 0.17, -3.40, 0.95), (0.34, 1.10, 1.90), OAK)
    for sh in range(4):
        make_box(f"FR_Bookshelf_Shelf_{sh}", (XE - 0.17, -3.40, 0.30 + sh * 0.45), (0.30, 1.04, 0.02), OAK_DK)
        for k in range(9):
            make_box(f"FR_Bookshelf_Book_{sh}_{k}", (XE - 0.20, -3.85 + k * 0.11, 0.30 + sh * 0.45 + 0.13), (0.20, 0.08, 0.24),
                     ((0.62, 0.20, 0.18, 1.0), (0.24, 0.40, 0.56, 1.0), (0.86, 0.74, 0.40, 1.0), (0.30, 0.50, 0.32, 1.0))[(k + sh) % 4])
    # the backyard window: frame and the yard beyond it
    make_window("FR_Window", (-2.40, FR_Y, 1.55), width=1.80, height=1.30, room_dir=+1, see_through=True, palette={"frame": TRIM})
    make_box("FR_Window_Sill", (-2.40, FR_Y + 0.18, 0.885), (2.00, 0.16, 0.03), TRIM)
    for e in (-1, 1):
        make_box(f"FR_Window_Curtain_{e:+d}", (-2.40 + e * 1.10, FR_Y + 0.15, 1.45), (0.26, 0.04, 1.90), (0.70, 0.62, 0.50, 1.0))
    make_cyl("FR_Window_Curtain_Rod", (-2.40, FR_Y + 0.15, 2.42), 0.012, 2.70, OAK_DK, axis='X', segments=6)
    for e in (-1, 1):
        make_box(f"FR_Window_Curtain_Rod_Bracket_{e:+d}", (-2.40 + e * 1.30, FR_Y + 0.075, 2.42), (0.03, 0.15, 0.03), OAK_DK)
    for k in range(4):
        make_box(f"FR_Photo_{k}_Frame", (-0.40 + k * 0.48, FR_Y + 0.112, 2.05), (0.34, 0.024, 0.26), OAK_DK)
        make_box(f"FR_Photo_{k}", (-0.40 + k * 0.48, FR_Y + 0.126, 2.05), (0.28, 0.004, 0.20),
                 ((0.58, 0.52, 0.44, 1.0), (0.44, 0.56, 0.66, 1.0), (0.66, 0.60, 0.50, 1.0), (0.52, 0.62, 0.48, 1.0))[k])


# ── the ceiling: pendants over the table and the island, cans ──────
def build_ceiling():
    make_cyl("Table_Pendant_Cord", (TX, TY, (CEIL + 1.82) / 2.0), 0.006, CEIL - 1.82, (0.14, 0.14, 0.15, 1.0), segments=4)
    make_lathe("Table_Pendant_Shade", (TX, TY, 1.52), [(0.26, 0.0), (0.24, 0.05), (0.12, 0.26), (0.03, 0.30), (0.0, 0.30)],
               (0.20, 0.30, 0.26, 1.0), segments=14)
    make_cyl("Table_Pendant_Bulb", (TX, TY, 1.57), 0.05, 0.07, (1.0, 0.94, 0.78, 1.0), segments=8)
    for k, dx in enumerate((-0.70, 0.70)):
        make_cyl(f"Island_Pendant_{k}_Cord", (IX + dx, IY, (CEIL + 1.92) / 2.0), 0.006, CEIL - 1.92, (0.14, 0.14, 0.15, 1.0), segments=4)
        make_lathe(f"Island_Pendant_{k}_Shade", (IX + dx, IY, 1.70), [(0.14, 0.0), (0.15, 0.10), (0.08, 0.20), (0.0, 0.22)],
                   (0.92, 0.90, 0.84, 1.0), segments=12)
    for k, (cx, cy) in enumerate(((-3.0, 2.0), (0.4, 2.2), (-1.0, 6.0), (2.7, 5.8), (0.5, -2.6), (-5.55, 3.0))):
        make_cyl(f"Recessed_Can_{k}", (cx, cy, CEIL - 0.012), 0.09, 0.024, (0.96, 0.95, 0.90, 1.0), segments=10)
    make_box("Smoke_Detector", (0.0, 3.0, CEIL - 0.02), (0.12, 0.12, 0.04), (0.94, 0.94, 0.92, 1.0))
    make_box("HVAC_Register", (-2.0, 3.0, CEIL - 0.006), (0.40, 0.25, 0.012), (0.90, 0.90, 0.88, 1.0))


# ── through the windows ────────────────────────────────────────────
def build_outside(sedan):
    """North (the street side, through the sink window): the front lawn,
    the walk, the curb, the street, the Gellers' house across the
    cul-de-sac with its porch light; the white sedan at the curb when
    the vigil is on. East (through the east window and the back door):
    the drive and the garage, its one window lit. South (through the
    family room window): the backyard, the fence, a crape myrtle."""
    grass = (0.38, 0.50, 0.28, 1.0)
    make_box("Thru_N_Lawn", (0.0, 11.0, -0.04), (30.0, 7.8, 0.05), grass)
    make_box("Thru_N_Sidewalk", (0.0, 15.3, -0.02), (30.0, 1.2, 0.05), (0.62, 0.60, 0.56, 1.0))
    make_box("Thru_N_Curb", (0.0, 16.0, -0.02), (30.0, 0.15, 0.10), (0.56, 0.54, 0.50, 1.0))
    make_box("Thru_N_Street", (0.0, 20.0, -0.04), (30.0, 7.8, 0.05), (0.32, 0.32, 0.33, 1.0))
    make_box("Thru_N_Lawn_Far", (0.0, 27.0, -0.04), (30.0, 6.2, 0.05), grass)
    for k, (hx, col) in enumerate(((-9.0, (0.86, 0.80, 0.70, 1.0)), (1.0, (0.80, 0.82, 0.78, 1.0)), (11.0, (0.88, 0.78, 0.66, 1.0)))):
        make_box(f"Thru_N_House_{k}", (hx, 33.0, 1.8), (8.0, 6.0, 3.6), col)
        make_box(f"Thru_N_House_{k}_Roof", (hx, 33.0, 4.0), (8.6, 6.6, 0.8), (0.36, 0.32, 0.28, 1.0))
        make_box(f"Thru_N_House_{k}_Door", (hx + 1.2, 29.98, 1.05), (0.95, 0.04, 2.10), (0.42, 0.30, 0.22, 1.0))
        make_box(f"Thru_N_House_{k}_Window", (hx - 2.0, 29.98, 1.60), (1.60, 0.04, 1.10), (0.30, 0.34, 0.38, 1.0))
    # DON GELLER'S PORCH LIGHT, by his door across the way (the middle house)
    make_box("Don_Porch_Bracket", (2.75, 29.97, 2.22), (0.06, 0.04, 0.06), (0.20, 0.20, 0.22, 1.0))
    make_cyl("Don_Porch_Light", (2.75, 29.93, 2.10), 0.06, 0.12, (0.98, 0.86, 0.56, 1.0), segments=8)
    for k, sx in enumerate((-2.6, 0.4, 3.4)):
        make_cyl(f"Thru_N_Sprinkler_{k}", (sx, 9.0, 0.03), 0.03, 0.07, (0.30, 0.32, 0.30, 1.0), segments=6)
    make_cyl("Thru_N_Mailbox_Post", (3.4, 15.75, 0.55), 0.05, 1.10, (0.30, 0.30, 0.32, 1.0), segments=6)
    make_box("Thru_N_Mailbox", (3.4, 15.75, 1.18), (0.22, 0.48, 0.24), (0.20, 0.20, 0.22, 1.0))
    if sedan:
        white = (0.90, 0.90, 0.88, 1.0)
        make_box("White_Sedan_Body", (-1.6, 17.0, 0.62), (4.20, 1.70, 0.60), white)
        make_box("White_Sedan_Cabin", (-1.9, 17.0, 1.13), (2.20, 1.50, 0.42), (0.82, 0.83, 0.82, 1.0))
        make_box("White_Sedan_Glass", (-1.9, 16.24, 1.13), (2.00, 0.02, 0.32), (0.22, 0.26, 0.30, 1.0))
        for wi, (wx2, wy2) in enumerate(((-3.0, 16.12), (-0.2, 16.12), (-3.0, 17.88), (-0.2, 17.88))):
            make_cyl(f"White_Sedan_Wheel_{wi}", (wx2, wy2, 0.33), 0.33, 0.25, (0.14, 0.14, 0.15, 1.0), axis='Y', segments=10)
    # east: the drive, the garage with its one lit window
    make_box("Thru_E_Driveway", (7.0, 3.5, -0.03), (4.6, 12.0, 0.05), (0.56, 0.55, 0.52, 1.0))
    make_box("Thru_E_Lawn", (12.0, 3.0, -0.04), (6.0, 20.0, 0.05), grass)
    make_box("Thru_E_Garage_Wall", (9.6, 3.5, 1.5), (0.25, 7.0, 3.0), (0.86, 0.84, 0.78, 1.0))
    make_box("Thru_E_Garage_Roofline", (9.6, 3.5, 3.2), (0.6, 7.4, 0.4), (0.40, 0.38, 0.35, 1.0))
    make_box("Thru_E_Garage_Window", (9.46, 3.4, 1.6), (0.03, 0.9, 0.7), (0.95, 0.85, 0.55, 1.0))
    make_box("Thru_E_Garage_Mullion", (9.45, 3.4, 1.6), (0.02, 0.06, 0.72), (0.30, 0.30, 0.34, 1.0))
    make_box("Thru_E_Step", (X1 + 0.35, DOOR_E_Y, -0.02), (0.50, 1.00, 0.06), (0.62, 0.60, 0.56, 1.0))
    # south: the backyard past the family room window
    make_box("Thru_S_Lawn", (0.0, FR_Y - 6.0, -0.04), (22.0, 11.8, 0.05), grass)
    make_box("Thru_S_Fence", (0.0, FR_Y - 9.0, 0.90), (22.0, 0.05, 1.80), (0.62, 0.52, 0.40, 1.0))
    make_taper_cyl("Thru_S_Myrtle_Trunk", (-3.0, FR_Y - 5.0, 1.1), 0.10, 0.06, 2.2, (0.56, 0.44, 0.38, 1.0), segments=8)
    make_blob("Thru_S_Myrtle_Canopy", (-3.0, FR_Y - 5.0, 2.8), 1.4, (0.72, 0.40, 0.52, 1.0), noise=0.25, seed=7, squash=0.8)
    make_box("Thru_S_Patio", (0.5, FR_Y - 1.4, -0.02), (4.0, 2.6, 0.06), (0.62, 0.60, 0.56, 1.0))


# ── the dressings ──────────────────────────────────────────────────
def dress_french_toast():
    """ch11 (4:11 AM): the French toast being made on the range's front-left
    burner — shared by the family and the dawn kitchens (2026-10-10: ch11 and
    ch17 moved to the 4 AM kitchen; their props moved with them)."""
    top = 0.77
    # the French toast, mid-making, on the range's front-left burner
    sx, sy = RANGE_X - 0.19, YN - 0.33 - 0.14
    make_cyl("FrenchToast_Skillet", (sx, sy, TOP_Z + 0.019), 0.14, 0.035, (0.16, 0.15, 0.14, 1.0), segments=14)
    make_box("FrenchToast_Skillet_Handle", (sx - 0.22, sy, TOP_Z + 0.028), (0.16, 0.032, 0.022), (0.16, 0.15, 0.14, 1.0))
    for si, (ox, oy) in enumerate(((-0.055, 0.03), (0.055, -0.035))):
        make_box(f"FrenchToast_Slice_{si}", (sx + ox, sy + oy, TOP_Z + 0.050), (0.105, 0.085, 0.028), (0.83, 0.68, 0.44, 1.0))
    make_box("FrenchToast_Challah", (-1.70, YN - 0.36, TOP_Z + 0.055), (0.30, 0.13, 0.11), (0.62, 0.44, 0.24, 1.0))
    make_cyl("FrenchToast_EggBowl", (-1.40, YN - 0.42, TOP_Z + 0.0275), 0.095, 0.055, (0.90, 0.88, 0.84, 1.0), segments=12)
    make_cyl("FrenchToast_Cinnamon", (-1.20, YN - 0.20, TOP_Z + 0.0375), 0.028, 0.075, (0.55, 0.34, 0.18, 1.0), segments=8)


def dress_four_thirty_table():
    """The four-thirty table: the hands' worn patches, Eileen's cinnamon roll,
    the kolaches, the jar — shared by both kitchens."""
    top = 0.77
    # the table: hands' worn patches, the cinnamon roll, the kolaches, the jar, the Sentinel
    make_box("Hands_Worn_Patch_A", (TX, TY - 0.28, top + 0.001), (0.16, 0.12, 0.002), (0.52, 0.40, 0.27, 1.0))
    make_box("Hands_Worn_Patch_B", (TX + 0.60, TY, top + 0.001), (0.12, 0.16, 0.002), (0.52, 0.40, 0.27, 1.0))
    make_cyl("Small_Plate", (TX + 0.35, TY + 0.25, top + 0.006), 0.090, 0.012, PAPER, segments=12)
    make_cyl("Cinnamon_Roll", (TX + 0.35, TY + 0.25, top + 0.0345), 0.055, 0.045, (0.72, 0.50, 0.28, 1.0), segments=10)
    make_cyl("Cinnamon_Roll_Swirl", (TX + 0.35, TY + 0.25, top + 0.059), 0.030, 0.004, (0.90, 0.84, 0.72, 1.0), segments=8)
    make_box("Bakery_Bag", (TX - 0.30, TY + 0.22, top + 0.09), (0.22, 0.14, 0.18), (0.76, 0.62, 0.42, 1.0))
    make_cyl("Kolache_Plate", (TX - 0.05, TY + 0.24, top + 0.006), 0.100, 0.012, PAPER, segments=12)
    for ki, (kx, ky, kc) in enumerate(((-0.045, -0.03, (0.86, 0.62, 0.30, 1.0)), (0.045, -0.03, (0.90, 0.84, 0.66, 1.0)),
                                       (0.0, 0.045, (0.66, 0.44, 0.28, 1.0)))):
        make_cyl(f"Kolache_{ki}", (TX - 0.05 + kx, TY + 0.24 + ky, top + 0.027), 0.045, 0.030, kc, segments=8)
    make_cyl("Mason_Jar", (TX - 0.55, TY - 0.30, top + 0.065), 0.045, 0.130, (0.72, 0.76, 0.70, 0.75), segments=10)
    make_cyl("Mason_Jar_Lid", (TX - 0.55, TY - 0.30, top + 0.1375), 0.047, 0.015, (0.62, 0.52, 0.30, 1.0), segments=10)


def dress_family():
    """miller_kitchen: Mike's coffee and his phone at the counter (ch 0),
    the French toast being made (ch 11), Eileen's cinnamon roll and the
    kolaches and the jar on the table, the Sentinel folded at Mike's end,
    the photographs fanned on the island, the white sedan at the curb."""
    top = 0.77
    dress_french_toast()
    # Mike's coffee and his phone at the counter by the coffee maker
    make_cyl("Mike_Coffee_Mug", (-2.95, YN - 0.42, TOP_Z + 0.048), 0.04, 0.095, (0.30, 0.36, 0.52, 1.0), segments=10)
    make_box("Phone_Cell", (-2.75, YN - 0.46, TOP_Z + 0.006), (0.075, 0.15, 0.012), (0.12, 0.12, 0.14, 1.0))
    dress_four_thirty_table()
    make_box("Sentinel_Folded", (TX + 0.55, TY - 0.15, top + 0.0075), (0.30, 0.20, 0.015), (0.86, 0.84, 0.78, 1.0))
    make_box("Sentinel_Headline", (TX + 0.55, TY - 0.08, top + 0.0155), (0.22, 0.03, 0.002), (0.28, 0.26, 0.24, 1.0))
    # THE PHOTOGRAPHS fanned on the island ("He looks at the photographs")
    for pi, (dx, dy) in enumerate(((0.0, 0.0), (0.04, 0.03), (0.08, 0.05))):
        make_box(f"Photographs_{pi}", (IX + 0.50 + dx, IY - 0.10 + dy, 0.9806 + pi * 0.0012), (0.10, 0.15, 0.001), (0.78, 0.76, 0.70, 1.0))


def dress_dawn():
    """bianca_kitchen_morning: the 4:11 coffee in the dark — the kettle on
    the burner, the grinder, her cup at Mike's end; the cordless on the
    table; the stationery from the small drawer and its pen; Sammy's
    half-finished cereal at the head."""
    top = 0.77
    make_lathe("Kettle", (RANGE_X + 0.19, YN - 0.33 + 0.16, TOP_Z + 0.002), [(0.10, 0.0), (0.11, 0.05), (0.09, 0.17), (0.04, 0.21), (0.0, 0.22)],
               KK.STAINLESS, segments=12)
    make_box("Kettle_Handle", (RANGE_X + 0.19, YN - 0.33 + 0.16, TOP_Z + 0.215), (0.16, 0.02, 0.03), (0.14, 0.14, 0.15, 1.0))
    make_box("Coffee_Grinder", (-2.80, YN - 0.40, TOP_Z + 0.10), (0.12, 0.12, 0.20), (0.20, 0.20, 0.22, 1.0))
    make_cyl("Coffee_Cup_Bianca", (TX + 0.55, TY, top + 0.045), 0.04, 0.09, (0.94, 0.92, 0.88, 1.0), segments=10)
    make_box("Cordless_Handset", (TX + 0.35, TY - 0.25, top + 0.015), (0.05, 0.18, 0.03), (0.18, 0.18, 0.20, 1.0))
    make_box("Cordless_Handset_Screen", (TX + 0.35, TY - 0.20, top + 0.0305), (0.034, 0.05, 0.001), (0.62, 0.74, 0.66, 1.0))
    make_box("Stationery_Sheet", (TX - 0.20, TY - 0.20, top + 0.001), (0.16, 0.21, 0.002), PAPER)
    for k in range(5):
        make_box(f"Stationery_Line_{k}", (TX - 0.20, TY - 0.13 - k * 0.025, top + 0.0025), (0.12, 0.004, 0.001), (0.24, 0.26, 0.40, 1.0))
    make_cyl("Stationery_Pen", (TX - 0.05, TY - 0.20, top + 0.005), 0.005, 0.130, (0.18, 0.18, 0.22, 1.0), axis='Y', segments=6)
    make_box("Stationery_Drawer", (-1.20, YN - 0.62 - 0.07, TOP_Z - 0.135), (0.40, 0.12, 0.10), KK.WHITE_SHAKER)
    make_box("Stationery_Drawer_Box", (-1.20, YN - 0.62 - 0.07, TOP_Z - 0.10), (0.30, 0.10, 0.02), PAPER)
    make_taper_cyl("Cereal_Bowl_Sammy", (TX - 0.55, TY, top + 0.03), 0.04, 0.075, 0.06, (0.86, 0.36, 0.30, 1.0), segments=12)
    make_cyl("Cereal_Bowl_Sammy_Milk", (TX - 0.55, TY, top + 0.055), 0.065, 0.004, (0.96, 0.94, 0.88, 1.0), segments=10)
    make_box("Cereal_Box", (TX - 0.62, TY + 0.30, top + 0.15), (0.20, 0.07, 0.30), (0.86, 0.62, 0.20, 1.0))
    make_box("Cereal_Spoon", (TX - 0.45, TY - 0.05, top + 0.003), (0.02, 0.15, 0.005), STEEL)
    dress_french_toast()
    dress_four_thirty_table()


def build_wear_and_infra():
    floor_dk = (0.52, 0.38, 0.26, 1.0)
    floor_pale = (0.72, 0.58, 0.42, 1.0)
    make_traffic_wear("Wear_Family_Path", [(0.5, 0.4), (0.3, 2.4), (-0.4, 5.6), (SINK_X, 6.1)], width=0.70, tint=floor_dk)
    make_traffic_wear("Wear_Door_Path", [(XE - 0.3, DOOR_E_Y), (2.6, 2.0), (1.4, 4.8)], width=0.55, tint=floor_dk)
    make_floor_stain("Wear_Sink_Stand", (SINK_X, YN - 0.92), radius=0.24, tint=(0.48, 0.35, 0.24, 1.0), segments=9)
    make_floor_stain("Wear_Coffee_Dust", (-3.0, YN - 0.80), radius=0.10, tint=(0.54, 0.40, 0.28, 1.0), segments=7)
    make_floor_stain("Wear_Chair_Sammy", (TX - 1.40, TY), radius=0.20, tint=floor_dk, segments=8)
    make_floor_stain("Wear_Chair_Bianca", (TX, TY - 1.18), radius=0.20, tint=floor_dk, segments=8)
    make_floor_stain("Wear_Chair_Mike_Years", (TX + 1.40, TY), radius=0.22, tint=floor_pale, segments=8)
    make_floor_stain("Wear_Chair_Mike_June", (TX + 1.33, TY + 0.05), radius=0.11, tint=(0.56, 0.42, 0.30, 1.0), segments=8)
    make_box("Wear_Phone_CordArc", (XW + 0.003, 3.0, 1.02), (0.006, 0.70, 0.06), (0.84, 0.80, 0.72, 1.0))
    make_box("Vent_Register", (3.6, 2.10, 0.045), (0.36, 0.14, 0.09), (0.72, 0.70, 0.66, 1.0))
    for vi in range(5):
        make_box(f"Vent_Register_Slat_{vi}", (3.50 + vi * 0.05, 2.10, 0.095), (0.012, 0.11, 0.008), (0.55, 0.53, 0.50, 1.0))
    make_wall_outlet("Outlet_East", (X1, 2.20), axis='Y', face_sign=-1, z=0.30)
    make_wall_outlet("Outlet_FR", (-1.4, FR_Y), axis='X', face_sign=1, z=0.30)


def build_east_window():
    make_window("East_Window", (XE, WIN_E[0], WIN_E[1]), width=WIN_E[2], height=WIN_E[3], axis='Y', room_dir=-1, see_through=True,
                palette={"frame": TRIM})
    sill = WIN_E[1] - WIN_E[3] / 2.0
    make_box("East_Window_Sill", (XE - 0.08, WIN_E[0], sill - 0.015), (0.16, WIN_E[2] + 0.20, 0.03), TRIM)
    # "watching him through the sheer curtain": one sheer drawn across the
    # window's south half, its mate gathered north
    make_box("East_Window_Sheer_Drawn", (XE - 0.16, WIN_E[0] - WIN_E[2] / 4.0, WIN_E[1] + 0.05), (0.01, WIN_E[2] / 2.0 + 0.04, WIN_E[3] + 0.20),
             (0.94, 0.92, 0.88, 0.35))
    make_box("East_Window_Sheer_Gathered", (XE - 0.16, WIN_E[0] + WIN_E[2] / 2.0 + 0.08, WIN_E[1] + 0.05), (0.04, 0.20, WIN_E[3] + 0.20),
             (0.92, 0.90, 0.86, 1.0))
    make_cyl("East_Window_Sheer_Rod", (XE - 0.16, WIN_E[0], WIN_E[1] + WIN_E[3] / 2.0 + 0.17), 0.010, WIN_E[2] + 0.50, KK.NICKEL, axis='Y', segments=6)
    for e in (-1, 1):
        make_box(f"East_Window_Sheer_Rod_Bracket_{e:+d}", (XE - 0.08, WIN_E[0] + e * (WIN_E[2] / 2.0 + 0.20), WIN_E[1] + WIN_E[3] / 2.0 + 0.17),
                 (0.16, 0.02, 0.03), KK.NICKEL)
    make_box("Nook_TV", (3.30, YN - 0.03, 1.90), (0.80, 0.05, 0.46), (0.10, 0.10, 0.12, 1.0))
    make_box("Nook_TV_Screen", (3.30, YN - 0.057, 1.90), (0.74, 0.004, 0.40), (0.30, 0.36, 0.42, 1.0))
    make_box("Nook_Sideboard", (3.30, YN - 0.24, 0.43), (1.50, 0.46, 0.86), OAK)
    make_box("Nook_Sideboard_Top", (3.30, YN - 0.24, 0.875), (1.54, 0.50, 0.03), OAK_DK)
    make_box("Nook_Sideboard_Mail_Basket", (2.85, YN - 0.24, 0.96), (0.32, 0.22, 0.14), (0.62, 0.48, 0.30, 1.0))
    for k in range(3):
        make_rot_box(f"Nook_Sideboard_Photo_{k}", (3.20 + k * 0.30, YN - 0.12, 1.00), (0.18, 0.03, 0.22), OAK_DK, roll=0.0, pitch=0.12)


def build_kitchen(variant):
    build_shell()
    build_north_run()
    build_island_and_table()
    build_west_and_hall()
    build_family_room()
    build_ceiling()
    build_east_window()
    build_wear_and_infra()
    build_outside(sedan=(variant == "family"))
    if variant == "family":
        make_wall_clock("Clock", (2.30, YN, 1.95), frozen_hour=6, frozen_min=24, facing='-Y')
        dress_family()
    else:
        make_wall_clock("Clock", (2.30, YN, 1.95), frozen_hour=4, frozen_min=11, facing='-Y')
        dress_dawn()
