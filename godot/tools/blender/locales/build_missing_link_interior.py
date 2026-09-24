"""missing_link_interior — vol1 interlude locale. THE MISSING LINK:
a roadside bus-depot diner (the Shillelagh stops here once a day).
A single rectangle of warm yellow light on a wet asphalt apron. Per
canon: a counter with five stools, four booths against the front
windows, a jukebox in the corner blinking through its red eye,
humming fluorescents, coffee on the burner, a swinging door to the
back kitchen. Two gas pumps outside, one retired in place.

Rebuilt 2026-07-13 from the bare auto-generated template (which
shipped only a register counter + a vending box) into a full diner.

DRAFT 3 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass, 8
placements — vol 1's first room). The stools as profiles (flared base,
foot ring, rolled seat); the booths with chamfered vinyl, a top rail,
a flanged table post and a chrome edge band; the cake dome a bell;
feet and side trims on the jukebox; the kitchen door's push plate and
hinge strip. OUTSIDE the front windows: the pumps moved WEST of the
door to where the exterior builder has them (the east one stood in
front of the entrance), the island, a hose, the depot bench under a
real awning east of the door, the road and its dashes past the apron,
the pole sign, the cobra lamppost, the treeline. First WEAR: the
entry path over the checker tiles, the counter's kick scuff and elbow
strip, the booths' sit shine, the lean patch at the jukebox. D3: the
switch bank by the kitchen door, the jukebox's outlet and cord, the
coffee station's.
Draft 4 targets: reconcile this plan with build_missing_link_exterior
(the exterior's door is at the diner's EAST end, this room's is
centred, and the exterior body is 8 m to this room's 7 m); the swing
door's kick; napkin dispensers as the chrome kind; the pie case lit;
Deck: the preset from the SW corner + establish_b.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_cyl, make_lathe, make_tube, export_glb
from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band, make_light_switch, make_wall_outlet
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_case_shell
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.6
PAL_WALL = {"wall": (0.80, 0.74, 0.58, 1.0), "baseboard": (0.34, 0.28, 0.22, 1.0)}
COL_FLOOR = (0.72, 0.68, 0.60, 1.0); COL_SEAM = (0.34, 0.30, 0.26, 1.0)
COL_TILE_CHECK = (0.30, 0.26, 0.22, 1.0)
COL_LAMINATE = (0.86, 0.82, 0.70, 1.0); COL_STEEL = (0.70, 0.72, 0.74, 1.0)
COL_CHROME = (0.78, 0.80, 0.84, 1.0); COL_VINYL_RED = (0.72, 0.22, 0.20, 1.0)
COL_VINYL_DK = (0.42, 0.14, 0.14, 1.0); COL_WOOD = (0.46, 0.32, 0.22, 1.0)
COL_GLASS = (0.78, 0.84, 0.86, 0.45); COL_MUG = (0.90, 0.88, 0.82, 1.0)
COL_COFFEE = (0.20, 0.12, 0.08, 1.0); COL_PIE = (0.86, 0.62, 0.34, 1.0)
COL_JUKE = (0.42, 0.24, 0.18, 1.0); COL_JUKE_GLOW = (0.96, 0.72, 0.34, 1.0)
COL_RED_EYE = (0.94, 0.20, 0.16, 1.0); COL_BLACK = (0.14, 0.12, 0.12, 1.0)
COL_ASPHALT = (0.16, 0.16, 0.18, 1.0); COL_PUMP = (0.74, 0.20, 0.18, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # Checkerboard accent tiles down the center aisle
    for j in range(6):
        for i in range(3):
            if (i + j) % 2 == 0:
                make_box(f"CheckTile_{i}_{j}", (-1.0 + i * 1.0, 1.0 + j * 0.8, 0.011),
                         (0.9, 0.7, 0.002), COL_TILE_CHECK)
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # N wall (kitchen wall) split for the swinging pass-through door
    make_wall("Wall_N_W", (-2.0, ROOM_D, 0), length=3.0, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+2.0, ROOM_D, 0), length=3.0, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveDoor", (0.0, ROOM_D, CEIL-0.30), (1.2, 0.20, 0.60), PAL_WALL["wall"])
    # S front wall — two solid segments flanking the entrance
    make_wall("Wall_S_W", (-2.25, 0.0, 0), length=2.5, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+2.25, 0.0, 0), length=2.5, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
                                    ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_STEEL})


def build_counter_and_stools():
    cy = 4.30
    make_chamfer_box("Counter_Body", (0.0, cy, 0.53), (5.40, 0.62, 1.02), COL_LAMINATE)
    make_box("Counter_Front", (0.0, cy - 0.32, 0.53), (5.40, 0.02, 1.00), COL_STEEL)
    make_chamfer_box("Counter_Top", (0.0, cy, 1.07), (5.60, 0.76, 0.05), COL_LAMINATE)
    # Chrome edge band + kick
    make_cyl("Counter_EdgeBand", (0.0, cy - 0.39, 1.05), 0.03, 5.40, COL_CHROME, axis='X', segments=8)
    make_box("Counter_Kick", (0.0, cy - 0.32, 0.10), (5.40, 0.04, 0.18), COL_BLACK)
    # Five chrome swivel stools facing N
    for si, sx in enumerate([-2.0, -1.0, 0.0, +1.0, +2.0]):
        sy = cy - 0.85
        # (draft 3: profiles — a flared base, a foot ring, a rolled seat)
        make_lathe(f"Stool_{si}_Base", (sx, sy, 0.0), [(0.19, 0.0), (0.19, 0.02), (0.12, 0.04), (0.05, 0.05), (0.035, 0.06)], COL_CHROME, segments=12)
        make_cyl(f"Stool_{si}_Post", (sx, sy, 0.39), 0.035, 0.66, COL_CHROME)
        make_lathe(f"Stool_{si}_FootRing", (sx, sy, 0.22), [(0.13, 0.0), (0.15, 0.012), (0.13, 0.024)], COL_CHROME, segments=12, loop=True)
        make_lathe(f"Stool_{si}_Seat", (sx, sy, 0.725), [(0.0, 0.0), (0.16, 0.0), (0.18, 0.02), (0.18, 0.05), (0.16, 0.07), (0.0, 0.075)], COL_VINYL_RED, segments=12)
    # Counter dressing: 2 chipped white mugs, 3 condiment sets
    for mi, mx in enumerate([-1.6, +0.4]):
        make_cyl(f"CounterMug_{mi}", (mx, cy - 0.10, 1.14), 0.045, 0.10, COL_MUG, segments=10)
        make_cyl(f"CounterMug_{mi}_Coffee", (mx, cy - 0.10, 1.17), 0.038, 0.02, COL_COFFEE, segments=10)
    for ci, cx in enumerate([-2.2, 0.0, +2.2]):
        make_box(f"Napkin_{ci}", (cx, cy + 0.05, 1.14), (0.10, 0.08, 0.10), COL_CHROME)
        make_cyl(f"Salt_{ci}", (cx + 0.14, cy + 0.05, 1.14), 0.02, 0.09, COL_GLASS, segments=8)
        make_cyl(f"Pepper_{ci}", (cx + 0.20, cy + 0.05, 1.14), 0.02, 0.09, COL_BLACK, segments=8)
        make_cyl(f"Ketchup_{ci}", (cx - 0.14, cy + 0.05, 1.16), 0.025, 0.13, COL_VINYL_RED, segments=8)
    # Cake dome + pie on the counter
    make_cyl("CakePlate", (+1.6, cy - 0.02, 1.11), 0.22, 0.03, COL_CHROME, segments=16)
    make_cyl("CakePie", (+1.6, cy - 0.02, 1.16), 0.20, 0.08, COL_PIE, segments=16)
    # the dome LIFTED and set down beside the stand (2026-09-24: over the
    # pie it rendered as an opaque grey bell — no alpha in this pipeline)
    make_lathe("CakeDome", (+2.1, cy - 0.02, 1.095), [(0.23, 0.0), (0.23, 0.14), (0.19, 0.19), (0.08, 0.22), (0.03, 0.22), (0.03, 0.25), (0.0, 0.25)], COL_GLASS, segments=16)


def build_backbar_kitchen():
    by = ROOM_D - 0.45
    make_chamfer_box("BackCounter_Body", (0.0, by, 0.45), (5.60, 0.46, 0.90), COL_STEEL)
    make_chamfer_box("BackCounter_Top", (0.0, by, 0.92), (5.60, 0.50, 0.05), COL_STEEL)
    # Coffee station (drip pots on burners)
    make_coffee_pots("CoffeeStation", (-2.2, by - 0.02, 0.95), pots=2,
                     palette={"glass": COL_GLASS})
    # Pie / dessert display case
    px = +1.5
    # (2026-09-24: a solid body with its shelves and pies inside it,
    # behind a glass slab that renders opaque; 20 cm pies on 16 cm
    # centres overlapped. An open shell; 15 cm pies; glints.)
    make_case_shell("PieCase_Body", (px, by, 1.20), (0.60, 0.44, 0.56), COL_STEEL, open_face='-Y')
    for gi, (gx, gw) in enumerate(((-0.20, 0.02), (-0.13, 0.01))):
        make_box(f"PieCase_Glint_{gi}", (px + gx, by - 0.21, 1.20), (gw, 0.004, 0.52), (0.86, 0.90, 0.92, 1.0))
    for ti, tz in enumerate([1.06, 1.30]):
        make_box(f"PieCase_Shelf_{ti}", (px, by + 0.005, tz), (0.56, 0.39, 0.02), COL_CHROME)
        for wi in range(3):
            make_cyl(f"PieCase_Pie_{ti}_{wi}", (px - 0.17 + wi * 0.17, by, tz + 0.035),
                     0.075, 0.05, [COL_PIE, (0.72, 0.34, 0.28, 1.0), (0.86, 0.78, 0.52, 1.0)][wi],
                     segments=12)
    # Milkshake multi-spindle mixer
    mx = +2.5
    make_chamfer_box("Shake_Body", (mx, by, 1.14), (0.24, 0.28, 0.44), (0.40, 0.60, 0.52, 1.0))
    for mi in range(3):
        make_cyl(f"Shake_Spindle_{mi}", (mx - 0.08 + mi * 0.08, by - 0.06, 1.02), 0.015, 0.20,
                 COL_CHROME, segments=6)
        make_cyl(f"Shake_Cup_{mi}", (mx - 0.08 + mi * 0.08, by - 0.06, 0.98), 0.045, 0.14,
                 COL_CHROME, segments=8)
    # Mug shelf on the N wall + a menu board above the pass
    make_box("MugShelf", (-1.4, ROOM_D - 0.16, 1.55), (2.0, 0.22, 0.03), COL_STEEL)
    for ui in range(8):
        make_cyl(f"ShelfMug_{ui}", (-2.2 + ui * 0.24, ROOM_D - 0.16, 1.62), 0.045, 0.10,
                 COL_MUG, segments=8)
    make_box("MenuBoard_BG", (0.0, ROOM_D - 0.12, 2.05), (3.2, 0.03, 0.60), COL_BLACK)
    for li in range(4):
        make_box(f"MenuBoard_Row_{li}", (-0.4, ROOM_D - 0.14, 2.22 - li * 0.14),
                 (2.2, 0.005, 0.05), (0.90, 0.86, 0.72, 1.0))
    # Ticket rail at the pass
    # (2026-09-23: the rail hung on air 15 cm off the wall; it runs along the
    # menu board's bottom edge now, tickets clipped under it)
    make_box("TicketRail", (0.0, ROOM_D - 0.145, 1.74), (2.0, 0.02, 0.02), COL_CHROME)
    for ti in range(3):
        make_box(f"Ticket_{ti}", (-0.6 + ti * 0.6, ROOM_D - 0.1575, 1.66),
                 (0.10, 0.005, 0.14), (0.94, 0.90, 0.62, 1.0))
    # Swinging kitchen door with a round porthole
    make_box("KitchenDoor", (0.0, ROOM_D - 0.02, 1.05), (0.94, 0.06, 2.05), COL_LAMINATE)
    make_cyl("KitchenDoor_Porthole", (0.0, ROOM_D - 0.05, 1.55), 0.15, 0.04, COL_GLASS, axis='Y', segments=12)
    make_cyl("KitchenDoor_PortRim", (0.0, ROOM_D - 0.04, 1.55), 0.17, 0.02, COL_CHROME, axis='Y', segments=12)
    make_box("KitchenDoor_PushPlate", (0.30, ROOM_D - 0.053, 1.05), (0.16, 0.004, 0.30), COL_CHROME)
    make_box("KitchenDoor_HingeStrip", (-0.46, ROOM_D - 0.02, 1.05), (0.02, 0.07, 2.00), COL_STEEL)


def build_window_booths():
    # Four window booths, benches running N-S facing each other across
    # a table; the front window is at the S (y~0) end of each booth.
    for bi, bx in enumerate([-2.5, -1.4, +1.4, +2.5]):
        for sgn, tag in [(-1, "W"), (+1, "E")]:
            benchx = bx + sgn * 0.36
            make_chamfer_box(f"Booth_{bi}_Seat_{tag}", (benchx, 0.95, 0.44),
                             (0.30, 1.10, 0.10), COL_VINYL_RED, chamfer=0.03)
            # the bench's plinth (2026-09-23: every seat cushion hung at
            # 0.39 with nothing under it)
            make_box(f"Booth_{bi}_Plinth_{tag}", (benchx + sgn * 0.02, 0.95, 0.195),
                     (0.26, 1.04, 0.39), COL_VINYL_DK)
            make_chamfer_box(f"Booth_{bi}_Back_{tag}", (bx + sgn * 0.52, 0.95, 0.83),
                             (0.10, 1.10, 0.66), COL_VINYL_DK, chamfer=0.03)
            make_tube(f"Booth_{bi}_Rail_{tag}", [(bx + sgn * 0.52, 0.40, 1.17), (bx + sgn * 0.52, 1.50, 1.17)], 0.018, COL_CHROME, segments=6)
        # (draft 3: a flanged post, a chrome edge band round the top)
        make_lathe(f"Booth_{bi}_Table_Post", (bx, 0.95, 0.011), [(0.16, 0.0), (0.16, 0.015), (0.05, 0.03), (0.03, 0.05), (0.03, 0.705)], COL_CHROME, segments=10)
        make_box(f"Booth_{bi}_Table", (bx, 0.95, 0.74), (0.48, 0.62, 0.05), COL_LAMINATE)
        make_tube(f"Booth_{bi}_Table_Band", [(bx - 0.245, 0.64, 0.74), (bx + 0.245, 0.64, 0.74), (bx + 0.245, 1.26, 0.74), (bx - 0.245, 1.26, 0.74), (bx - 0.245, 0.64, 0.74)], 0.012, COL_CHROME, segments=6)
        # a napkin box + a mug on each table
        make_box(f"Booth_{bi}_Napkin", (bx, 1.10, 0.80), (0.08, 0.06, 0.08), COL_CHROME)
        make_cyl(f"Booth_{bi}_Mug", (bx - 0.10, 0.85, 0.80), 0.04, 0.09, COL_MUG, segments=8)
    # Two front windows on the S wall segments
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_W", (-2.25, 0.10, 1.55), width=2.0, height=1.30, room_dir=+1)
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_E", (+2.25, 0.10, 1.55), width=2.0, height=1.30, room_dir=+1)


def build_jukebox():
    jx, jy = +ROOM_W/2.0 - 0.35, 2.90
    make_chamfer_box("Juke_Body", (jx, jy, 0.66), (0.44, 0.72, 1.30), COL_JUKE)
    make_cyl("Juke_Dome", (jx, jy, 1.38), 0.34, 0.44, COL_JUKE, axis='X', segments=12)
    # Glowing selection panel facing W (into the room)
    make_box("Juke_Panel", (jx - 0.23, jy, 1.05), (0.03, 0.56, 0.42), COL_JUKE_GLOW)
    make_box("Juke_PanelGrid", (jx - 0.245, jy, 1.05), (0.005, 0.50, 0.36), (0.30, 0.20, 0.12, 1.0))
    # Chrome arch tubes on the dome (color bands)
    for ci, col in enumerate([(0.94, 0.42, 0.34, 1.0), COL_JUKE_GLOW, (0.42, 0.62, 0.86, 1.0)]):
        make_cyl(f"Juke_ArchTube_{ci}", (jx - 0.10 + ci * 0.10, jy, 1.38), 0.35, 0.02,
                 col, axis='X', segments=12)
    # Speaker grilles
    for si, sz in enumerate([0.55, 0.80]):
        make_cyl(f"Juke_Speaker_{si}", (jx - 0.22, jy, sz), 0.10, 0.02, COL_BLACK, axis='X', segments=10)
    # The blinking red eye + coin slot
    make_cyl("Juke_RedEye", (jx - 0.245, jy + 0.24, 1.30), 0.03, 0.02, COL_RED_EYE, axis='X', segments=8)
    make_box("Juke_CoinSlot", (jx - 0.245, jy - 0.20, 1.28), (0.005, 0.04, 0.08), COL_CHROME)
    # (draft 3: feet, chrome side trims)
    for fi, (fx, fy) in enumerate(((jx - 0.17, jy - 0.30), (jx + 0.17, jy - 0.30), (jx - 0.17, jy + 0.30), (jx + 0.17, jy + 0.30))):
        make_cyl(f"Juke_Foot_{fi}", (fx, fy, 0.005), 0.03, 0.01, COL_BLACK, segments=6)
    for ti, ty in enumerate((jy - 0.37, jy + 0.37)):
        make_box(f"Juke_Trim_{ti}", (jx - 0.12, ty, 0.72), (0.20, 0.012, 1.10), COL_CHROME)


def build_ceiling_infra():
    for j, ypos in enumerate([1.6, 3.2, 4.8]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.60, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("Vent", (-1.8, 2.4, CEIL), width=1.00, depth=0.50, slats=5)


def build_decor():
    make_wall_clock("Clock", (3.400, 4.6, 2.20), frozen_hour=3, frozen_min=40, facing='-X')
    make_calendar("Calendar", (-ROOM_W/2.0+0.05, 2.4, 2.10))
    make_faded_poster("Poster", (-ROOM_W/2.0+0.05 + 0.0535, 4.6, 1.60), into_room=+1)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.40, 5.4, 0.0),
                     palette={"leaf": (0.36, 0.46, 0.32, 1.0)})
    # The hand-lettered "THE MISSING LINK" ape-man panel by the door (W of it)
    px = -1.30
    make_box("LinkSign_Frame", (px, 0.06, 2.05), (1.00, 0.04, 0.44), COL_WOOD)
    make_box("LinkSign_Enamel", (px, 0.04, 2.05), (0.92, 0.02, 0.36), (0.90, 0.86, 0.70, 1.0))
    make_box("LinkSign_Title", (px, 0.02, 2.18), (0.72, 0.005, 0.06), COL_BLACK)
    # The ape-man silhouette painted beneath the name
    make_box("LinkSign_Figure_Body", (px, 0.02, 1.98), (0.10, 0.005, 0.14), COL_BLACK)
    make_cyl("LinkSign_Figure_Head", (px, 0.02, 2.08), 0.05, 0.005, COL_BLACK, axis='Y', segments=8)
    # Entry mat
    make_box("EntryMat", (0.0, 0.70, 0.011), (1.4, 0.7, 0.006), (0.24, 0.22, 0.20, 1.0))


def build_exterior():
    # Wet asphalt apron + two gas pumps + a depot bench, visible through
    # the front windows (Blender -Y = south = outside the S wall).
    make_box("Apron", (0.0, -3.0, -0.02), (20.0, 6.0, 0.04), COL_ASPHALT)
    # (draft 3: the pumps WEST of the door where build_missing_link_
    # exterior puts them — the east pump stood in front of the entrance)
    make_box("Pump_Island", (-5.6, -2.6, 0.08), (2.6, 1.0, 0.16), (0.28, 0.28, 0.30, 1.0))
    for pi, px in enumerate((-4.9, -6.3)):
        py = -2.6
        retired = (pi == 1)
        col = (0.42, 0.40, 0.40, 1.0) if retired else COL_PUMP
        make_chamfer_box(f"Pump_{pi}_Body", (px, py, 0.81), (0.50, 0.40, 1.30), col, chamfer=0.02)
        make_box(f"Pump_{pi}_Display", (px, py - 0.21, 1.15), (0.36, 0.02, 0.26),
                 (0.20, 0.24, 0.20, 1.0) if retired else (0.86, 0.92, 0.78, 1.0))
        make_box(f"Pump_{pi}_Topper", (px, py, 1.56), (0.56, 0.30, 0.20), (0.90, 0.88, 0.80, 1.0))
        if not retired:
            make_tube(f"Pump_{pi}_Hose", [(px + 0.26, py, 1.30), (px + 0.42, py, 0.95), (px + 0.28, py, 0.62)], 0.02, COL_BLACK, segments=6)
            make_box(f"Pump_{pi}_Nozzle", (px + 0.28, py, 0.55), (0.06, 0.10, 0.14), COL_STEEL)
    # Depot bench under its awning, east of the door beyond Window_E
    make_chamfer_box("DepotBench_Seat", (5.0, -1.2, 0.42), (1.20, 0.36, 0.06), COL_WOOD)
    make_chamfer_box("DepotBench_Back", (5.0, -1.02, 0.66), (1.20, 0.06, 0.42), COL_WOOD)
    for lx in (-0.5, +0.5):
        make_box(f"DepotBench_Leg_{lx:+.0f}", (5.0 + lx, -1.2, 0.20), (0.06, 0.30, 0.40), COL_BLACK)
    for ax in (4.0, 6.0):
        make_cyl(f"Awning_Post_{ax:.0f}", (ax, -1.9, 1.25), 0.05, 2.5, COL_STEEL, segments=6)
    make_box("Awning_Roof", (5.0, -1.1, 2.55), (2.6, 1.9, 0.08), (0.36, 0.38, 0.36, 1.0))
    # The road past the apron, the pole sign west, the cobra lamppost
    # east, the treeline
    make_box("Road_S", (0.0, -7.7, -0.02), (24.0, 3.4, 0.04), (0.14, 0.14, 0.16, 1.0))
    for di in range(8):
        make_box(f"Road_Dash_{di}", (-10.5 + di * 3.0, -7.7, 0.005), (1.3, 0.12, 0.01), (0.72, 0.68, 0.52, 1.0))
    make_lathe("PoleSign_Pole", (-8.9, -1.5, 0.0), [(0.20, 0.0), (0.20, 0.05), (0.11, 0.10), (0.11, 4.2), (0.0, 4.2)], (0.30, 0.30, 0.32, 1.0), segments=8)
    make_box("PoleSign_Face", (-8.9, -1.5, 4.7), (2.6, 0.22, 1.1), (0.88, 0.84, 0.72, 1.0))
    make_box("PoleSign_Border", (-8.9, -1.5, 4.7), (2.75, 0.08, 1.25), (0.62, 0.20, 0.16, 1.0))
    make_lathe("Lamppost_Pole", (5.8, -4.0, 0.0), [(0.16, 0.0), (0.16, 0.05), (0.09, 0.10), (0.07, 5.0), (0.0, 5.0)], (0.30, 0.30, 0.32, 1.0), segments=8)
    make_tube("Lamppost_Arm", [(5.8, -4.0, 4.9), (5.8, -4.6, 5.0), (5.8, -5.3, 4.95)], 0.04, (0.30, 0.30, 0.32, 1.0), segments=6)
    make_box("Lamppost_Head", (5.8, -5.5, 4.88), (0.24, 0.62, 0.14), (0.44, 0.46, 0.50, 1.0))
    make_box("Treeline_S", (0.0, -12.0, 2.6), (30.0, 0.6, 5.2), (0.10, 0.14, 0.10, 1.0))


def build_draft3_2026_09():
    """DRAFT 3 (2026-09-19) · wear and infrastructure. No part name
    carries a cue word (pie · juke · food)."""
    floor_dk = (COL_FLOOR[0] * 0.84, COL_FLOOR[1] * 0.84, COL_FLOOR[2] * 0.84, 1.0)
    cord = (0.16, 0.16, 0.18, 1.0)
    # the entry line rides ON the checker tiles (z 0.012), not under them
    make_traffic_wear("Wear_Path_Entry", [(0.0, 1.1), (0.0, 3.0)], width=0.70, floor_z=0.008, tint=floor_dk)
    make_scuff_band("Wear_Kick", (0.0, 4.30 - 0.32 - 0.007), 3.6, axis='X', height=0.10, band_z=0.30, tint=(0.36, 0.32, 0.28, 1.0))
    make_box("Wear_Elbow", (0.0, 3.95, 1.0965), (5.0, 0.06, 0.003), (0.70, 0.64, 0.50, 1.0))
    for bi, bx in enumerate([-2.5, -1.4, +1.4, +2.5]):
        for sgn, tag in [(-1, "W"), (+1, "E")]:
            make_box(f"Wear_Sit_{bi}_{tag}", (bx + sgn * 0.36, 0.85, 0.4915), (0.22, 0.50, 0.003), (0.80, 0.30, 0.26, 1.0))
    make_floor_stain("Wear_Lean", (2.55, 2.9), radius=0.30, tint=floor_dk, segments=10)
    # D3
    make_light_switch("Switch_1", (0.90, ROOM_D), axis='X', face_sign=-1, z=1.20, aged=True)
    make_light_switch("Switch_2", (1.02, ROOM_D), axis='X', face_sign=-1, z=1.20, aged=True)
    make_wall_outlet("Outlet_E_1", (ROOM_W / 2.0, 3.7), axis='Y', face_sign=-1, z=0.30, aged=True)
    make_tube("Cord_1", [(3.30, 3.27, 0.20), (ROOM_W / 2.0 - 0.13, 3.68, 0.30)], 0.008, cord, segments=5)
    make_wall_outlet("Outlet_N_1", (-2.2, ROOM_D), axis='X', face_sign=-1, z=1.10, aged=True)
    make_tube("Cord_2", [(-2.0, 5.66, 0.98), (-2.2, ROOM_D - 0.13, 1.10)], 0.008, cord, segments=5)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE FOOD ("The food came. ... Finn ate. He ate slowly and then
    he ate faster"): the plate at the fourth stool — hash, two
    eggs, toast."""
    make_cyl("Food_Plate", (1.0, 4.15, 1.096), 0.13, 0.012, (0.92, 0.90, 0.86, 1.0), segments=14)
    make_cyl("Food_Hash", (0.95, 4.12, 1.114), 0.060, 0.024, (0.66, 0.50, 0.30, 1.0), segments=10)
    for ei, (ex, ey) in enumerate(((1.06, 4.10), (1.07, 4.19))):
        make_cyl(f"Food_Egg_{ei}", (ex, ey, 1.108), 0.028, 0.012, (0.96, 0.94, 0.90, 1.0), segments=8)
        make_cyl(f"Food_Yolk_{ei}", (ex, ey, 1.117), 0.012, 0.006, (0.94, 0.72, 0.20, 1.0), segments=8)
    make_box("Food_Toast", (0.93, 4.22, 1.106), (0.07, 0.045, 0.008), (0.80, 0.62, 0.36, 1.0))


def main():
    clear_scene()
    build_shell()
    build_counter_and_stools()
    build_backbar_kitchen()
    build_window_booths()
    build_jukebox()
    build_ceiling_infra()
    build_decor()
    build_exterior()
    build_hero_props_2026_09()
    build_draft3_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/missing_link_interior.glb"))
    print(f"\n[build_missing_link_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
