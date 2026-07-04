"""Pit Stop Diner — dining room + kitchen line — vol6 hero pass.

The Pit Stop is Ben Kowalski's diner (lore/planned_community/
suburban_blight.md L13: "Ben Kowalski (the Pit Stop, observer)") in
the Harmony Creek strip mall, next door to the Coin Wash. Register
per the music catalog (music_catalog.json L1866, "the Pit Stop's
lunch-shuffle grill"): a worn family lunch counter — HOA maintenance
guys, retirees, NexCorp van drivers — the personal-clutter OPPOSITE
of the Gas & Go's corporate planogram. NOT a convenience store: the
scaffold's Kwik Stop vocabulary (two snack aisles, endcap imports)
is removed per the wave-2 "wrong fixture vocabulary" lesson.

Binding scenes (grep "3d:pit_stop_interior" — 5 VN scenes):
  · vol6_ch2_pit_stop_kitchen (Mon 12:22) — Ben on the grill through
    the lunch shuffle; the swinging kitchen door Jesse pushes
    through; "cataloguing the specific cars in the parking lot from
    the kitchen window"; "a black pickup with Louisiana plates ...
    parked at the edge of the Pit Stop lot" (L78) — so the kitchen
    gets a real window onto the west lot, and the pickup is parked
    out there.
  · vol6_ch2_dumpster (Mon 14:17) — the back dumpster with Ben's
    grease patina Jesse hates leaning on, the back screen door that
    "slapped shut behind him" — screen door in the kitchen's north
    wall, dumpster in the north exterior slice beyond it.
  · vol6_ch4_pit_stop — the back booth by the window where Mr.
    Henderson sits 41 minutes; "through the pass-through" Jesse sees
    him; Henderson "was sitting at an angle that could see the
    grill"; the milk crate by the walk-in Jesse sits on; the bell
    over the diner door; the back-office door Ben stands at with a
    sightline to the booth.
  · vol6_ch6_pit_stop (Fri 09:18) — Ben wiping down the line;
    Brenda (morning manager) in the office behind the office door.
  · vol6_ch7_pit_stop (Sat 09:14) — "The back booth at the Pit Stop
    is the corner one, three from the kitchen, with a window that
    looks out on the strip-mall parking lot and the Coin Wash next
    door" (L32); Ben "taps the bell on the pass-through twice";
    Lydia pours coffee; short stack / egg-white scramble.

Adjudications:
  · The corner booth: prose wants "back" + "corner" + window +
    angle-to-the-grill all at once. Booths run down the west wall;
    the Henderson booth is the NORTH one (Booth T3) — the corner
    against the kitchen partition, deepest into the establishing
    frame, window beside it, diagonal sightline through the
    pass-through to the flat-top. "Three from the kitchen" is read
    as the third table of the row (it is the third table counting
    from the entry; the row has exactly three).
  · Coin Wash "next door": the Pit Stop's east wall is the shared
    strip-mall party wall (NO windows east — canon-consistent); the
    Coin Wash storefront the booth window actually SEES sits across
    the west side lot (CoinWash_Facade, porthole washers,
    CoinWash_SignBand for scene-side Label3D).
  · ch0 note: the "ch0 Pit Stop office" beat used to be served by
    the cosmic_comics_back_office GLB (see that file's docstring);
    vol6_ch0_prelude L64 now binds 3d:pit_stop_office directly, so
    this venue owns both of its rooms.

Canon-negatives (as load-bearing as the props):
  · NO Suburban Blight sticker under the counter — Ben puts it
    there "by mid-August" (suburban_blight.md L257), after every
    scene this GLB backs. Leave the counter underside bare.
  · NO stage/band gear — the diner-deck show is August 8, outside.
  · NO jukebox, NO TV — never named at the Pit Stop.
  · East wall windowless (party wall with the Coin Wash).

Scaffold audit (playbook 2026-07-02 — openings/intersections first):
  · Two snack aisles + convenience register in a DINER — removed.
  · Zero window openings anywhere (solid walls) — west booth
    windows, kitchen window and south storefront windows are now
    REAL openings (frame + mullions, NO glass slab, bright day
    boxes / exterior slice beyond) per the no-transparency rule.
  · No kitchen, no booths, no counter stools, no doors — built.

Shell footprint kept from the scaffold (7 x 6 x 2.8) — the .tscn
camera preset (Background3D.gd "pit_stop_interior": south-doorway
establishing shot at 2.30 m, fov 60) is tuned to it; the south
door gap x -1..+1 stays clear for the camera.

Text is scene-side Label3D; this script bakes only named panels:
MenuBoard_Panel_{0..2}, CoinWash_SignBand, Pickup_PlatePanel,
Office_DoorSign, Corkboard notices, Window day boxes.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.store_fixtures import make_register
from _props.signage import make_paper_notices_wall
from _props.decor import make_wall_clock
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture,
                           make_ceiling_speaker)
from _props.cleaning import make_trash_can

# ── Shell (kept from the scaffold — camera + lights tuned to it) ──
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8

# ═════════════════════════════════════════════════════════════════
# PITSTOP_* — Pit Stop Diner venue palette. KEEP IN SYNC: this block
# is byte-identical in build_pit_stop_interior.py and
# build_pit_stop_office.py (one venue, two GLBs — md5-verify after
# any edit, per the Miller-house / Foxhole multi-room rule).
# ═════════════════════════════════════════════════════════════════
PITSTOP_CREAM      = (0.93, 0.88, 0.76, 1.0)   # painted walls
PITSTOP_CREAM_AGED = (0.85, 0.78, 0.64, 1.0)   # grease-adjacent wall tone
PITSTOP_RED        = (0.62, 0.18, 0.16, 1.0)   # booth vinyl / brand oxblood
PITSTOP_RED_WORN   = (0.70, 0.34, 0.26, 1.0)   # sun-worn vinyl / table edging
PITSTOP_FORMICA    = (0.76, 0.66, 0.46, 1.0)   # counter + table tops
PITSTOP_TOP_DARK   = (0.20, 0.15, 0.13, 1.0)   # counter top laminate
PITSTOP_WOOD       = (0.52, 0.36, 0.22, 1.0)   # oak trim / the office desk
PITSTOP_WOOD_DARK  = (0.33, 0.22, 0.14, 1.0)
PITSTOP_STAINLESS  = (0.70, 0.71, 0.72, 1.0)   # kitchen line steel
PITSTOP_STEEL_DK   = (0.44, 0.45, 0.47, 1.0)
PITSTOP_FLOOR      = (0.82, 0.76, 0.62, 1.0)   # tan linoleum
PITSTOP_FLOOR_SEAM = (0.58, 0.51, 0.40, 1.0)
PITSTOP_CHECKER    = (0.48, 0.16, 0.14, 1.0)   # dark-red checker tiles
PITSTOP_MINT       = (0.62, 0.76, 0.68, 1.0)   # 50s mint accent trim
PITSTOP_LEGAL_PAD  = (0.94, 0.86, 0.44, 1.0)   # Ben's legal pad (ch0/ch3)
PITSTOP_APRON      = (0.90, 0.88, 0.82, 1.0)   # bib aprons
PITSTOP_BRASS      = (0.78, 0.62, 0.30, 1.0)   # door bell + pass bell
PITSTOP_DAY_SKY    = (0.98, 0.92, 0.72, 1.0)   # Texas summer daylight outside
PITSTOP_ASPHALT    = (0.30, 0.30, 0.32, 1.0)   # strip-mall lot
PITSTOP_STRIPE     = (0.88, 0.86, 0.78, 1.0)   # lot striping
PITSTOP_PICKUP_BLK = (0.10, 0.10, 0.11, 1.0)   # the Louisiana pickup (ch2/ch3)
PITSTOP_COINWASH   = (0.70, 0.78, 0.82, 1.0)   # Coin Wash facade next door (ch7)
PITSTOP_GREASE     = (0.34, 0.28, 0.20, 1.0)   # grill patina / dumpster grime
# ═══════════════════════ end shared block ════════════════════════

PAL_WALL = {"wall": PITSTOP_CREAM, "baseboard": PITSTOP_WOOD_DARK}

# Locals (this room only)
COL_SIDEWALK  = (0.62, 0.60, 0.56, 1.0)
COL_DUMPSTER  = (0.30, 0.38, 0.30, 1.0)   # the back dumpster (ch2)
COL_CAB_GLASS = (0.25, 0.28, 0.30, 1.0)   # pickup glass band, opaque
COL_GRIDDLE   = (0.16, 0.14, 0.12, 1.0)
COL_PATTY     = (0.35, 0.22, 0.14, 1.0)
COL_PIE       = (0.82, 0.62, 0.34, 1.0)
COL_KETCHUP   = (0.70, 0.16, 0.12, 1.0)
COL_MUSTARD   = (0.86, 0.70, 0.22, 1.0)
COL_CORK      = (0.72, 0.58, 0.38, 1.0)

# Partition between dining room and kitchen (y = 4.7, 0.15 thick)
PART_Y = 4.70; PART_T = 0.15
# Booth row geometry (west wall). Three tables; T3 (north, corner
# against the partition) is the Henderson booth (ch4 / ch7).
BOOTH_TABLE_Y = [0.86, 2.30, 3.74]
BOOTH_WIN_Z0, BOOTH_WIN_Z1 = 1.0, 2.0


# ═════════════════════════════════════════════════════════════════
# SHELL — floor + checker field, four walls with REAL window
# openings (west booth windows, kitchen window, south storefront),
# the kitchen partition, ceiling.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": PITSTOP_FLOOR, "seam": PITSTOP_FLOOR_SEAM})
    # Checkerboard accent tiles across the dining floor (diner read)
    tile = 0.55
    for ix in range(12):
        for iy in range(8):
            if (ix + iy) % 2:
                continue
            tx = -3.3 + tile / 2.0 + ix * tile
            ty = 0.30 + tile / 2.0 + iy * tile
            make_box(f"Checker_{ix}_{iy}", (tx, ty, 0.008),
                     (tile - 0.03, tile - 0.03, 0.004), PITSTOP_CHECKER)
    # High-traffic scuffs — door-to-counter lane + stool line
    for i, (sx, sy) in enumerate([(0.0, 0.9), (-0.3, 1.6), (0.3, 2.3),
                                  (0.6, 2.8), (1.3, 2.8)]):
        make_box(f"Floor_Scuff_{i}", (sx, sy, 0.010),
                 (0.30, 0.20, 0.001), P.FLOOR_SCUFF)

    # ── West wall — sill band / header band / piers around the
    #    three booth-window openings + the kitchen window (ch2:
    #    Ben catalogues the lot "from the kitchen window").
    make_box("Wall_W_Sill", (-3.5, 3.0, 0.5), (0.2, 6.4, 1.0), PITSTOP_CREAM)
    make_box("Wall_W_Header", (-3.5, 3.0, 2.4), (0.2, 6.4, 0.8), PITSTOP_CREAM)
    for i, (yc, ln) in enumerate([(0.08, 0.56), (1.58, 0.44), (3.02, 0.44),
                                  (4.595, 0.71), (5.975, 0.45)]):
        make_box(f"Wall_W_Pier_{i}", (-3.5, yc, 1.5), (0.2, ln, 1.0),
                 PITSTOP_CREAM)
    make_box("Wall_W_Base", (-3.37, 3.0, 0.08), (0.06, 6.4, 0.16),
             PITSTOP_WOOD_DARK)

    # ── East wall — SOLID: shared party wall with the Coin Wash
    #    next door (ch7). No windows here, canon-consistent.
    make_wall("Wall_E", (+3.5, 3.0, 0), length=6.4, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)

    # ── North wall — solid except the back screen-door opening
    #    (x 1.7..2.5) to the dumpster (ch2_dumpster).
    make_box("Wall_N_W", (-1.0, 6.0, CEIL / 2.0), (5.4, 0.2, CEIL),
             PITSTOP_CREAM_AGED)
    make_box("Wall_N_E", (3.1, 6.0, CEIL / 2.0), (1.2, 0.2, CEIL),
             PITSTOP_CREAM_AGED)
    make_box("Wall_N_DoorHead", (2.1, 6.0, 2.45), (0.8, 0.2, 0.7),
             PITSTOP_CREAM_AGED)
    make_box("Wall_N_Base_W", (-1.0, 5.94, 0.08), (5.4, 0.06, 0.16),
             PITSTOP_WOOD_DARK)
    make_box("Wall_N_Base_E", (3.1, 5.94, 0.08), (1.2, 0.06, 0.16),
             PITSTOP_WOOD_DARK)

    # ── South (storefront) wall — door gap x -1..+1 stays CLEAR
    #    (camera shoots through it); window openings either side.
    for nm, cx, w in [("Wall_S_Pier_WW", -3.375, 0.65),
                      ("Wall_S_Pier_WM", -1.225, 0.45),
                      ("Wall_S_Pier_EM", +1.225, 0.45),
                      ("Wall_S_Pier_EE", +3.375, 0.65)]:
        make_box(nm, (cx, 0.0, CEIL / 2.0), (w, 0.2, CEIL), PITSTOP_CREAM)
    for nm, cx in [("Wall_S_Sill_W", -2.25), ("Wall_S_Sill_E", +2.25)]:
        make_box(nm, (cx, 0.0, 0.375), (1.6, 0.2, 0.75), PITSTOP_CREAM)
    make_box("Wall_S_Header", (0.0, 0.0, 2.5), (ROOM_W + 0.4, 0.2, 0.6),
             PITSTOP_CREAM)
    for nm, cx in [("Wall_S_Base_W", -2.25), ("Wall_S_Base_E", +2.25)]:
        make_box(nm, (cx, 0.13, 0.08), (1.6, 0.06, 0.16), PITSTOP_WOOD_DARK)

    # ── Kitchen partition (y = 4.7): pass-through opening
    #    (x -0.9..+1.1, z 1.1..1.7), swinging kitchen door opening
    #    (x 1.6..2.4), back-office door (x 2.6..3.4 — ch4: Ben at
    #    the office door has a clean SW sightline to Booth T3).
    make_box("Part_W", (-2.2, PART_Y, CEIL / 2.0), (2.6, PART_T, CEIL),
             PITSTOP_CREAM_AGED)
    make_box("Part_PassSill", (0.1, PART_Y, 0.55), (2.0, PART_T, 1.1),
             PITSTOP_CREAM_AGED)
    make_box("Part_PassHead", (0.1, PART_Y, 2.25), (2.0, PART_T, 1.1),
             PITSTOP_CREAM_AGED)
    make_box("Part_Pier_M", (1.35, PART_Y, CEIL / 2.0), (0.5, PART_T, CEIL),
             PITSTOP_CREAM_AGED)
    make_box("Part_SwingHead", (2.0, PART_Y, 2.45), (0.8, PART_T, 0.7),
             PITSTOP_CREAM_AGED)
    make_box("Part_Pier_E", (2.5, PART_Y, CEIL / 2.0), (0.2, PART_T, CEIL),
             PITSTOP_CREAM_AGED)
    make_box("Part_OfficeHead", (3.0, PART_Y, 2.45), (0.8, PART_T, 0.7),
             PITSTOP_CREAM_AGED)
    make_box("Part_Pier_EE", (3.45, PART_Y, CEIL / 2.0), (0.1, PART_T, CEIL),
             PITSTOP_CREAM_AGED)
    make_box("Part_Base_S", (-2.2, PART_Y - PART_T / 2.0 - 0.03, 0.08),
             (2.6, 0.06, 0.16), PITSTOP_WOOD_DARK)

    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4)
    # Mint cove trim around the dining room (50s diner register)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', 4.6, -3.4, 2.3),
            ("Crown_E", 'Y', 4.6, +3.4, 2.3),
            ("Crown_S", 'X', ROOM_W, 0.0, 0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length,
                           axis=ax, ceil_z=CEIL, palette={"wood": PITSTOP_MINT})


def _alum_window(tag, *, cx, cy_face, width, z0, z1, axis='X'):
    """Storefront aluminum frame + mullions for a REAL wall opening.
    axis='X': opening in an E-W (south) wall; axis='Y': in a N-S
    (west) wall — cx is then the wall plane, cy_face the run center."""
    zc = (z0 + z1) / 2.0
    h = z1 - z0
    if axis == 'X':
        make_box(f"Window_{tag}_Head", (cx, cy_face, z1 + 0.04),
                 (width + 0.12, 0.22, 0.08), PITSTOP_STEEL_DK)
        make_box(f"Window_{tag}_SillCap", (cx, cy_face, z0 - 0.04),
                 (width + 0.12, 0.26, 0.08), PITSTOP_STEEL_DK)
        for sgn in (-1, +1):
            make_box(f"Window_{tag}_Jamb_{sgn:+d}",
                     (cx + sgn * (width / 2.0 + 0.03), cy_face, zc),
                     (0.08, 0.22, h), PITSTOP_STEEL_DK)
        make_box(f"Window_{tag}_MullH", (cx, cy_face, zc),
                 (width, 0.05, 0.05), PITSTOP_STEEL_DK)
        make_box(f"Window_{tag}_MullV", (cx, cy_face, zc),
                 (0.05, 0.05, h), PITSTOP_STEEL_DK)
    else:
        make_box(f"Window_{tag}_Head", (cx, cy_face, z1 + 0.04),
                 (0.22, width + 0.12, 0.08), PITSTOP_STEEL_DK)
        make_box(f"Window_{tag}_SillCap", (cx, cy_face, z0 - 0.04),
                 (0.26, width + 0.12, 0.08), PITSTOP_STEEL_DK)
        for sgn in (-1, +1):
            make_box(f"Window_{tag}_Jamb_{sgn:+d}",
                     (cx, cy_face + sgn * (width / 2.0 + 0.03), zc),
                     (0.22, 0.08, h), PITSTOP_STEEL_DK)
        make_box(f"Window_{tag}_MullH", (cx, cy_face, zc),
                 (0.05, width, 0.05), PITSTOP_STEEL_DK)
        make_box(f"Window_{tag}_MullV", (cx, cy_face, zc),
                 (0.05, 0.05, h), PITSTOP_STEEL_DK)


# ═════════════════════════════════════════════════════════════════
# STOREFRONT — south door (frame + west leaf, gap stays open for
# the camera), the bell over the diner door (ch4), entry mat,
# window frames + day boxes, trash can.
# ═════════════════════════════════════════════════════════════════
def build_storefront():
    for tag, wx in [("SW", -2.25), ("SE", +2.25)]:
        _alum_window(tag, cx=wx, cy_face=0.0, width=1.6,
                     z0=0.75, z1=2.20, axis='X')
        # Bright Texas-summer day box beyond the opening (all bound
        # scenes are 09:14-15:15 — day, not el Rancho's 4 AM night)
        make_box(f"Window_{tag}_Day", (wx, -0.55, 1.475),
                 (1.9, 0.7, 1.75), PITSTOP_DAY_SKY)
    # Door surround
    for sgn in (-1, +1):
        make_box(f"DoorPost_{sgn:+d}", (sgn * 0.96, 0.0, 1.10),
                 (0.08, 0.24, 2.20), PITSTOP_STEEL_DK)
    make_box("DoorTransom", (0.0, 0.0, 2.16), (2.0, 0.24, 0.09),
             PITSTOP_STEEL_DK)
    # West-half aluminum leaf (east half open — the camera lane)
    make_box("Door_Stile_W", (-0.88, 0.0, 1.08), (0.07, 0.05, 2.10),
             PITSTOP_STEEL_DK)
    make_box("Door_Stile_E", (-0.12, 0.0, 1.08), (0.07, 0.05, 2.10),
             PITSTOP_STEEL_DK)
    make_box("Door_Rail_Top", (-0.50, 0.0, 2.09), (0.83, 0.05, 0.08),
             PITSTOP_STEEL_DK)
    make_box("Door_Rail_Mid", (-0.50, 0.0, 1.02), (0.83, 0.05, 0.08),
             PITSTOP_STEEL_DK)
    make_box("Door_Panel_Lower", (-0.50, 0.0, 0.55), (0.79, 0.035, 0.86),
             PITSTOP_MINT)
    make_box("Door_KickPlate", (-0.50, 0.0, 0.16), (0.83, 0.05, 0.24),
             PITSTOP_STEEL_DK)
    make_cyl("Door_PushBar", (-0.50, 0.07, 1.02), 0.020, 0.62,
             PITSTOP_STEEL_DK, axis='X')
    make_door_hinges("Door_Hinge", edge_x=-0.92, edge_y=0.0,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # The bell over the diner door (ch4: "the bell over the diner
    # door chimes") — brass dome on a curl bracket, inside face
    make_box("DoorBell_Bracket", (0.42, 0.14, 2.06), (0.03, 0.16, 0.03),
             PITSTOP_STEEL_DK)
    make_cyl("DoorBell_Dome", (0.42, 0.20, 1.99), 0.05, 0.08,
             PITSTOP_BRASS)
    make_cyl("DoorBell_Clapper", (0.42, 0.20, 1.93), 0.012, 0.05,
             PITSTOP_STEEL_DK)
    # Entry mat
    make_box("EntryMat_Under", (0.0, 0.80, 0.012), (1.90, 1.05, 0.006),
             (0.14, 0.13, 0.13, 1.0))
    make_box("EntryMat", (0.0, 0.80, 0.018), (1.76, 0.92, 0.008),
             P.RUBBER_MAT)
    make_box("EntryMat_Text", (0.0, 0.80, 0.023), (1.00, 0.18, 0.002),
             (0.42, 0.40, 0.38, 1.0))
    make_trash_can("DoorTrash", (3.05, 0.55, 0.0),
                   palette={"body": PITSTOP_RED_WORN})


# ═════════════════════════════════════════════════════════════════
# BOOTH ROW — west wall. Single bench / three tables / two shared
# double-backs / single bench against the partition. Booth T3
# (north corner) is the Henderson booth (ch4 41 minutes / ch7
# Eileen breakfast). Window openings above each table.
# ═════════════════════════════════════════════════════════════════
def _booth_single_bench(tag, cy, back_sign):
    """Bench with its tall back on the back_sign side (-1 = south)."""
    make_box(f"Booth_{tag}_Base", (-2.95, cy, 0.20), (0.90, 0.42, 0.40),
             PITSTOP_WOOD_DARK)
    make_box(f"Booth_{tag}_Seat", (-2.95, cy + 0.02 * -back_sign, 0.46),
             (0.90, 0.46, 0.10), PITSTOP_RED)
    make_box(f"Booth_{tag}_Back", (-2.95, cy + back_sign * 0.16, 0.82),
             (0.90, 0.10, 0.76), PITSTOP_RED)
    make_box(f"Booth_{tag}_BackCap", (-2.95, cy + back_sign * 0.16, 1.22),
             (0.90, 0.14, 0.04), PITSTOP_WOOD)


def _booth_double_bench(tag, cy):
    make_box(f"Booth_{tag}_Base", (-2.95, cy, 0.20), (0.90, 0.84, 0.40),
             PITSTOP_WOOD_DARK)
    make_box(f"Booth_{tag}_Seat_S", (-2.95, cy - 0.24, 0.46),
             (0.90, 0.40, 0.10), PITSTOP_RED)
    make_box(f"Booth_{tag}_Seat_N", (-2.95, cy + 0.24, 0.46),
             (0.90, 0.40, 0.10), PITSTOP_RED)
    make_box(f"Booth_{tag}_Back", (-2.95, cy, 0.82), (0.90, 0.12, 0.76),
             PITSTOP_RED)
    make_box(f"Booth_{tag}_BackCap", (-2.95, cy, 1.22), (0.90, 0.16, 0.04),
             PITSTOP_WOOD)


def _booth_table(tag, cy):
    make_box(f"Booth_{tag}_Top", (-2.925, cy, 0.74), (0.95, 0.62, 0.05),
             PITSTOP_FORMICA)
    make_box(f"Booth_{tag}_EdgeBand", (-2.4525, cy, 0.74),
             (0.035, 0.62, 0.055), PITSTOP_RED_WORN)
    make_cyl(f"Booth_{tag}_Pedestal", (-2.95, cy, 0.36), 0.05, 0.70,
             PITSTOP_STEEL_DK)
    make_cyl(f"Booth_{tag}_Foot", (-2.95, cy, 0.02), 0.12, 0.03,
             PITSTOP_STEEL_DK)
    make_box(f"Booth_{tag}_WallCleat", (-3.36, cy, 0.70), (0.08, 0.50, 0.04),
             PITSTOP_WOOD)
    # Table set: napkin dispenser + ketchup/mustard pair
    make_box(f"Booth_{tag}_Napkins", (-3.16, cy + 0.14, 0.83),
             (0.14, 0.08, 0.13), PITSTOP_STEEL_DK)
    make_box(f"Booth_{tag}_NapkinPaper", (-3.16, cy + 0.14, 0.90),
             (0.10, 0.05, 0.02), P.PAPER)
    make_cyl(f"Booth_{tag}_Ketchup", (-3.18, cy - 0.10, 0.835), 0.030,
             0.14, COL_KETCHUP)
    make_cyl(f"Booth_{tag}_Mustard", (-3.10, cy - 0.16, 0.825), 0.026,
             0.12, COL_MUSTARD)


def build_booths():
    _booth_single_bench("B0", 0.35, -1)          # entry-end bench
    _booth_table("T1", BOOTH_TABLE_Y[0])
    _booth_double_bench("D1", 1.58)
    _booth_table("T2", BOOTH_TABLE_Y[1])
    _booth_double_bench("D2", 3.02)
    _booth_table("T3", BOOTH_TABLE_Y[2])         # HENDERSON booth (ch4/ch7)
    _booth_single_bench("B3", 4.25, +1)          # back against the partition
    # Window openings above each table + the kitchen window
    for k, cy in enumerate(BOOTH_TABLE_Y):
        _alum_window(f"B{k}", cx=-3.5, cy_face=cy, width=1.0,
                     z0=BOOTH_WIN_Z0, z1=BOOTH_WIN_Z1, axis='Y')
    _alum_window("K", cx=-3.5, cy_face=5.35, width=0.8,
                 z0=BOOTH_WIN_Z0, z1=BOOTH_WIN_Z1, axis='Y')
    # Framed regulars' photos on the piers between windows
    for i, py in enumerate([1.58, 3.02]):
        make_box(f"PierPhoto_{i}_Frame", (-3.385, py, 1.60),
                 (0.02, 0.26, 0.32), PITSTOP_WOOD)
        make_box(f"PierPhoto_{i}_Print", (-3.375, py, 1.60),
                 (0.006, 0.20, 0.26), P.PAPER_AGED)


# ═════════════════════════════════════════════════════════════════
# LUNCH COUNTER — mid-frame hero: formica counter facing the door,
# four vinyl stools, register, cake dome, backbar with the coffee
# Lydia pours (ch7). The counter UNDERSIDE stays bare: the Suburban
# Blight sticker Ben puts there arrives mid-August (canon-negative).
# ═════════════════════════════════════════════════════════════════
def build_counter():
    cx, cy = 0.9, 3.55
    make_box("Counter_Body", (cx, cy, 0.46), (3.2, 0.65, 0.92),
             PITSTOP_FORMICA)
    make_box("Counter_Top", (cx, cy, 0.955), (3.36, 0.80, 0.07),
             PITSTOP_TOP_DARK)
    make_box("Counter_Kick", (cx, cy - 0.335, 0.10), (3.2, 0.02, 0.20),
             PITSTOP_WOOD_DARK)
    make_cyl("Counter_Bullnose", (cx, cy - 0.40, 0.92), 0.030, 3.2,
             PITSTOP_TOP_DARK, axis='X')
    # Stools — red vinyl, chrome posts, foot rings
    for i, sx in enumerate([-0.30, 0.50, 1.30, 2.10]):
        make_cyl(f"Stool_{i}_Seat", (sx, 2.82, 0.68), 0.17, 0.07,
                 PITSTOP_RED, segments=10)
        make_cyl(f"Stool_{i}_Post", (sx, 2.82, 0.34), 0.030, 0.60,
                 PITSTOP_STAINLESS)
        make_cyl(f"Stool_{i}_Base", (sx, 2.82, 0.02), 0.19, 0.04,
                 PITSTOP_STEEL_DK, segments=10)
        make_cyl(f"Stool_{i}_FootRing", (sx, 2.82, 0.25), 0.12, 0.015,
                 PITSTOP_STAINLESS, segments=10)
    # Counter top dressing
    make_register("Register", (2.10, 3.62, 0.99))
    make_cyl("CakeDome_Plate", (-0.35, 3.62, 0.995), 0.18, 0.02,
             PITSTOP_STAINLESS, segments=12)
    make_cyl("CakeDome_Dome", (-0.35, 3.62, 1.10), 0.16, 0.18,
             (0.85, 0.88, 0.86, 1.0), segments=12)
    make_cyl("CakeDome_Knob", (-0.35, 3.62, 1.21), 0.025, 0.04,
             PITSTOP_STAINLESS)
    for i, nx in enumerate([0.20, 1.60]):
        make_box(f"Counter_Napkins_{i}", (nx, 3.50, 1.06),
                 (0.15, 0.09, 0.14), PITSTOP_STEEL_DK)
        make_box(f"Counter_NapkinPaper_{i}", (nx, 3.50, 1.14),
                 (0.11, 0.05, 0.02), P.PAPER)
    make_cyl("Counter_Ketchup", (0.62, 3.48, 1.06), 0.030, 0.14,
             COL_KETCHUP)
    make_cyl("Counter_Mustard", (0.72, 3.42, 1.05), 0.026, 0.12,
             COL_MUSTARD)
    make_box("Counter_SugarRack", (1.05, 3.46, 1.02), (0.16, 0.10, 0.06),
             PITSTOP_STEEL_DK)
    make_box("Counter_SugarPax", (1.05, 3.46, 1.06), (0.12, 0.07, 0.03),
             P.PAPER)
    # The line rag — ch6: "He keeps wiping the line."
    make_box("Counter_LineRag", (1.75, 3.42, 1.00), (0.18, 0.12, 0.02),
             PITSTOP_MINT)
    # Backbar against the partition — coffee station (Lydia's pot),
    # mug pyramid, saucers, pie stand, order spike
    make_box("Backbar_Base", (0.45, 4.42, 0.44), (2.1, 0.45, 0.88),
             PITSTOP_WOOD_DARK)
    make_box("Backbar_Top", (0.45, 4.42, 0.90), (2.2, 0.50, 0.04),
             PITSTOP_STAINLESS)
    make_box("Coffee_Brewer", (-0.32, 4.50, 1.10), (0.36, 0.30, 0.36),
             PITSTOP_STEEL_DK)
    for i, px in enumerate([-0.42, -0.20]):
        make_cyl(f"Coffee_Warmer_{i}", (px, 4.38, 0.925), 0.085, 0.015,
                 P.METAL_BLACK)
        make_cyl(f"Coffee_Pot_{i}", (px, 4.38, 1.01), 0.075, 0.16,
                 (0.24, 0.15, 0.10, 1.0))
        make_box(f"Coffee_PotHandle_{i}", (px + 0.10, 4.38, 1.02),
                 (0.05, 0.03, 0.09), P.METAL_BLACK)
    for i, (mx, my) in enumerate([(0.28, 4.36), (0.37, 4.48), (0.46, 4.38),
                                  (0.33, 4.42), (0.42, 4.46)]):
        make_cyl(f"Backbar_Mug_{i}", (mx, my, 0.965), 0.040,
                 0.085, (0.92, 0.90, 0.84, 1.0), segments=10)
    make_cyl("Backbar_Saucers", (0.70, 4.42, 0.97), 0.070, 0.10,
             (0.92, 0.90, 0.84, 1.0), segments=12)
    make_cyl("PieStand_Pedestal", (1.10, 4.44, 0.965), 0.035, 0.09,
             PITSTOP_STAINLESS)
    make_cyl("PieStand_Plate", (1.10, 4.44, 1.02), 0.15, 0.02,
             PITSTOP_STAINLESS, segments=12)
    make_cyl("PieStand_Pie", (1.10, 4.44, 1.07), 0.12, 0.07, COL_PIE,
             segments=12)
    make_cyl("OrderSpike_Base", (1.42, 4.44, 0.935), 0.045, 0.02,
             PITSTOP_STEEL_DK)
    make_cyl("OrderSpike_Needle", (1.42, 4.44, 1.02), 0.006, 0.15,
             PITSTOP_STAINLESS)
    make_box("OrderSpike_Tickets", (1.42, 4.44, 0.97), (0.09, 0.09, 0.015),
             P.PAPER)


# ═════════════════════════════════════════════════════════════════
# PASS-THROUGH + PARTITION FACE — stainless sill shelf, the tap
# bell (ch7: "taps the bell on the pass-through twice"), order
# wheel, heat lamps, menu board panels (Label3D), the wall clock
# frozen at 12:22 (the lunch shuffle, ch2 / music catalog).
# ═════════════════════════════════════════════════════════════════
def build_pass_through():
    make_box("Pass_SillShelf", (0.1, PART_Y, 1.13), (2.1, 0.50, 0.06),
             PITSTOP_STAINLESS)
    # The bell — dining-side edge of the shelf, where Ben taps it
    make_cyl("PassBell_Dome", (0.85, 4.52, 1.185), 0.045, 0.05,
             PITSTOP_BRASS, segments=10)
    make_cyl("PassBell_Button", (0.85, 4.52, 1.215), 0.010, 0.02,
             PITSTOP_STEEL_DK)
    # Order wheel hanging in the opening
    make_cyl("OrderWheel", (0.45, PART_Y, 1.58), 0.12, 0.04,
             PITSTOP_STEEL_DK, axis='Y', segments=12)
    for i, tx in enumerate([0.34, 0.52]):
        make_box(f"OrderWheel_Ticket_{i}", (tx, PART_Y, 1.46),
                 (0.10, 0.012, 0.14), P.PAPER)
    # Heat lamps under the pass head
    for i, lx in enumerate([-0.35, 0.55]):
        make_box(f"Pass_HeatLamp_{i}", (lx, PART_Y, 1.73),
                 (0.40, 0.20, 0.05), (1.0, 0.78, 0.32, 1.0))
    # Menu boards above the pass — lettering is scene-side Label3D
    for i, mx in enumerate([-0.58, 0.10, 0.78]):
        make_box(f"MenuBoard_Panel_{i}", (mx, PART_Y - PART_T / 2.0 - 0.01,
                 2.25), (0.62, 0.02, 0.46), PITSTOP_TOP_DARK)
        make_box(f"MenuBoard_Trim_{i}", (mx, PART_Y - PART_T / 2.0 - 0.015,
                 2.50), (0.62, 0.02, 0.05), PITSTOP_MINT)
    # Clock on the partition face west of the boards — frozen at
    # 12:22, the ch2 lunch-shuffle minute
    make_wall_clock("DinerClock", (-2.2, PART_Y - PART_T / 2.0, 2.25),
                    frozen_hour=12, frozen_min=22)
    # Swinging kitchen door (ch2: "Jesse pushed through the
    # kitchen's swinging door") — double-action leaf, upper window
    # left EMPTY (see-through to the kitchen), steel kick plate
    make_box("SwingDoor_Stile_W", (1.66, PART_Y, 1.05), (0.06, 0.06, 2.10),
             PITSTOP_WOOD)
    make_box("SwingDoor_Stile_E", (2.34, PART_Y, 1.05), (0.06, 0.06, 2.10),
             PITSTOP_WOOD)
    make_box("SwingDoor_Rail_Top", (2.0, PART_Y, 2.07), (0.74, 0.06, 0.06),
             PITSTOP_WOOD)
    make_box("SwingDoor_Rail_Mid", (2.0, PART_Y, 1.28), (0.74, 0.06, 0.08),
             PITSTOP_WOOD)
    make_box("SwingDoor_Panel", (2.0, PART_Y, 0.72), (0.70, 0.045, 1.04),
             PITSTOP_WOOD)
    make_box("SwingDoor_Kick", (2.0, PART_Y - 0.0225, 0.32),
             (0.70, 0.01, 0.28), PITSTOP_STAINLESS)
    # Back-office door — CLOSED leaf (ch3/ch6: Ben's and Brenda's
    # room lives in the pit_stop_office GLB; here it's the door
    # Ben stands at in ch4)
    make_box("OfficeDoor_Leaf", (3.0, PART_Y, 1.03), (0.78, 0.06, 2.06),
             PITSTOP_WOOD)
    make_cyl("OfficeDoor_Knob", (3.28, PART_Y - 0.035, 1.02), 0.022, 0.05,
             PITSTOP_BRASS, axis='Y')
    make_door_hinges("OfficeDoor_Hinge", edge_x=2.62, edge_y=PART_Y,
                     edge_z_centers=[0.35, 1.05, 1.78], axis='X')
    make_box("Office_DoorSign", (3.0, PART_Y - PART_T / 2.0 - 0.005, 1.72),
             (0.18, 0.01, 0.12), P.PAPER_AGED)


# ═════════════════════════════════════════════════════════════════
# KITCHEN — behind the partition: the flat-top (ch2 burgers +
# spatula), hood, fryer, prep table under the kitchen window,
# walk-in with the milk crate by it (ch4), back screen door to the
# dumpster (ch2_dumpster), grease patina.
# ═════════════════════════════════════════════════════════════════
def build_kitchen():
    # Flat-top grill against the north wall — the hero through the
    # pass-through (and Booth T3's diagonal sightline, ch4)
    make_box("Grill_Body", (0.15, 5.50, 0.475), (1.5, 0.75, 0.95),
             PITSTOP_STAINLESS)
    make_box("Grill_Surface", (0.15, 5.50, 0.965), (1.4, 0.65, 0.02),
             COL_GRIDDLE)
    make_box("Grill_GreaseTrough", (0.15, 5.11, 0.94), (1.4, 0.05, 0.05),
             PITSTOP_STEEL_DK)
    make_box("Grill_Backsplash", (0.15, 5.86, 1.35), (1.5, 0.06, 0.75),
             PITSTOP_STAINLESS)
    # Two patties on (ch2: "He slid the spatula under a burger.")
    make_cyl("Grill_Patty_0", (-0.12, 5.44, 0.985), 0.065, 0.02, COL_PATTY)
    make_cyl("Grill_Patty_1", (0.24, 5.56, 0.985), 0.065, 0.02, COL_PATTY)
    make_box("Grill_Spatula_Blade", (0.52, 5.42, 0.99), (0.10, 0.12, 0.008),
             PITSTOP_STAINLESS)
    make_box("Grill_Spatula_Handle", (0.52, 5.28, 1.00), (0.03, 0.16, 0.02),
             PITSTOP_WOOD_DARK)
    # Hood + duct
    make_box("Grill_Hood", (0.15, 5.55, 2.32), (1.8, 0.95, 0.45),
             PITSTOP_STEEL_DK)
    make_box("Grill_HoodDuct", (0.15, 5.55, 2.66), (0.5, 0.5, 0.24),
             PITSTOP_STEEL_DK)
    # Ticket rail on the hood lip
    make_box("TicketRail", (0.15, 5.06, 1.98), (1.6, 0.03, 0.03),
             PITSTOP_STAINLESS)
    for i, tx in enumerate([-0.30, 0.15, 0.55]):
        make_box(f"TicketRail_Ticket_{i}", (tx, 5.05, 1.90),
                 (0.10, 0.01, 0.14), P.PAPER)
    # Fryer
    make_box("Fryer_Body", (1.15, 5.55, 0.45), (0.55, 0.70, 0.90),
             PITSTOP_STAINLESS)
    for i, fx in enumerate([1.03, 1.28]):
        make_box(f"Fryer_Basket_{i}", (fx, 5.45, 0.95), (0.18, 0.28, 0.10),
                 PITSTOP_STEEL_DK)
        make_cyl(f"Fryer_BasketHandle_{i}", (fx, 5.24, 0.98), 0.012, 0.16,
                 P.METAL_BLACK, axis='Y')
    # Prep table under the kitchen window (ch2: the lot watch)
    make_box("PrepTable_Top", (-2.90, 5.35, 0.87), (0.90, 0.60, 0.04),
             PITSTOP_STAINLESS)
    for i, (lx, ly) in enumerate([(-0.40, -0.25), (+0.40, -0.25),
                                  (-0.40, +0.25), (+0.40, +0.25)]):
        make_cyl(f"PrepTable_Leg_{i}", (-2.90 + lx, 5.35 + ly, 0.435),
                 0.020, 0.83, PITSTOP_STEEL_DK)
    make_box("PrepTable_LowerShelf", (-2.90, 5.35, 0.25), (0.85, 0.55, 0.03),
             PITSTOP_STEEL_DK)
    make_box("PrepTable_Board", (-2.90, 5.30, 0.905), (0.40, 0.30, 0.03),
             PITSTOP_WOOD)
    make_box("PrepTable_BusTub", (-2.90, 5.35, 0.34), (0.50, 0.35, 0.15),
             (0.55, 0.58, 0.60, 1.0))
    # Wall shelf with plate stacks
    make_box("KitchenShelf", (-2.90, 5.78, 1.90), (0.90, 0.32, 0.04),
             PITSTOP_STAINLESS)
    for i, px in enumerate([-3.10, -2.70]):
        make_cyl(f"KitchenShelf_Plates_{i}", (px, 5.78, 1.98), 0.09, 0.12,
                 (0.92, 0.90, 0.84, 1.0), segments=12)
    # Walk-in cooler + the milk crate by it (ch4: "Jesse ... sits
    # down, heavily, on the milk crate by the walk-in")
    make_box("WalkIn_Body", (-1.10, 5.55, 1.18), (1.20, 0.80, 2.36),
             (0.62, 0.64, 0.66, 1.0))
    make_box("WalkIn_Door", (-1.10, 5.12, 1.00), (0.70, 0.06, 1.90),
             PITSTOP_STEEL_DK)
    make_box("WalkIn_Latch", (-0.84, 5.08, 1.02), (0.06, 0.04, 0.16),
             P.METAL_BLACK)
    for i, hz in enumerate([0.45, 1.55]):
        make_box(f"WalkIn_HingeStrap_{i}", (-1.38, 5.10, hz),
                 (0.10, 0.03, 0.08), PITSTOP_STEEL_DK)
    make_box("MilkCrate", (-0.68, 5.02, 0.17), (0.34, 0.34, 0.34),
             (0.70, 0.30, 0.20, 1.0))
    make_box("MilkCrate_Rim", (-0.68, 5.02, 0.335), (0.36, 0.36, 0.02),
             (0.55, 0.22, 0.15, 1.0))
    # Back screen door (ch2_dumpster: "The screen door slapped shut")
    make_box("ScreenDoor_Jamb_W", (1.66, 6.0, 1.05), (0.08, 0.22, 2.10),
             PITSTOP_WOOD)
    make_box("ScreenDoor_Jamb_E", (2.54, 6.0, 1.05), (0.08, 0.22, 2.10),
             PITSTOP_WOOD)
    make_box("ScreenDoor_Head", (2.10, 6.0, 2.13), (0.96, 0.22, 0.07),
             PITSTOP_WOOD)
    make_box("ScreenDoor_Stile_W", (1.74, 5.98, 1.02), (0.05, 0.04, 2.02),
             PITSTOP_WOOD_DARK)
    make_box("ScreenDoor_Stile_E", (2.46, 5.98, 1.02), (0.05, 0.04, 2.02),
             PITSTOP_WOOD_DARK)
    make_box("ScreenDoor_Rail_Mid", (2.10, 5.98, 0.95), (0.70, 0.04, 0.07),
             PITSTOP_WOOD_DARK)
    make_box("ScreenDoor_Mesh_Top", (2.10, 5.98, 1.53), (0.68, 0.015, 1.02),
             (0.24, 0.24, 0.25, 1.0))
    make_box("ScreenDoor_Mesh_Bot", (2.10, 5.98, 0.47), (0.68, 0.015, 0.86),
             (0.24, 0.24, 0.25, 1.0))
    make_box("ScreenDoor_Spring", (1.78, 5.90, 1.30), (0.03, 0.14, 0.03),
             PITSTOP_STEEL_DK)
    # Kitchen floor: rubber mats + the grease patina (ch2: "The
    # grease hissed.")
    make_box("Kitchen_Mat_Grill", (0.15, 5.05, 0.010), (1.6, 0.50, 0.015),
             P.RUBBER_MAT)
    make_box("Kitchen_Mat_Prep", (-2.90, 4.95, 0.010), (0.9, 0.40, 0.015),
             P.RUBBER_MAT)
    make_box("Kitchen_GreasePatina", (0.15, 5.32, 0.020), (1.2, 0.30, 0.002),
             PITSTOP_GREASE)


# ═════════════════════════════════════════════════════════════════
# EAST WALL DRESSING — community corkboard (custom notice set — the
# Kwik Stop tallboy/we-card defaults would be the wrong register),
# faded poster, coat hooks.
# ═════════════════════════════════════════════════════════════════
def build_east_wall():
    make_box("Corkboard_Panel", (3.41, 1.60, 1.70), (0.02, 1.30, 0.90),
             COL_CORK)
    for i, (fy, fz, fl) in enumerate([(0.93, 1.70, 0.9), (2.27, 1.70, 0.9)]):
        make_box(f"Corkboard_FrameV_{i}", (3.40, fy, fz), (0.03, 0.04, fl),
                 PITSTOP_WOOD)
    for i, fz in enumerate([1.23, 2.17]):
        make_box(f"Corkboard_FrameH_{i}", (3.40, 1.60, fz), (0.03, 1.38, 0.04),
                 PITSTOP_WOOD)
    make_paper_notices_wall(
        "Corkboard_Notice", wall_x=3.42, wall_face_sign=-1,
        run_center_y=1.60, base_z=0.0,
        notices=[
            # community board, not convenience-store compliance:
            # church pancake breakfast / HOA newsletter (navy) /
            # youth-league signup / lost cat / plumber's card /
            # week's specials / handwritten shift swap
            (-0.48, 1.86, 0.24, 0.30, P.PAPER),
            (-0.12, 1.90, 0.26, 0.32, P.BRAND_NAVY_HCE),
            (+0.26, 1.86, 0.22, 0.28, P.PAPER),
            (-0.34, 1.48, 0.20, 0.24, P.PAPER_AGED),
            (+0.04, 1.44, 0.16, 0.12, P.PAPER),
            (+0.38, 1.48, 0.22, 0.26, (0.96, 0.96, 0.62, 1.0)),
            (+0.02, 1.70, 0.14, 0.16, P.PAPER_AGED),
        ])
    # Faded poster (hand-built — decor helper faces the wrong way
    # on an east wall)
    make_box("Poster_Body", (3.394, 3.40, 1.72), (0.012, 0.60, 0.80),
             P.PAPER_AGED)
    make_box("Poster_Figure", (3.386, 3.40, 1.88), (0.005, 0.42, 0.34),
             (0.32, 0.24, 0.20, 1.0))
    make_box("Poster_TitleBand", (3.386, 3.40, 1.44), (0.005, 0.46, 0.10),
             PITSTOP_RED_WORN)
    # Coat hooks by the door
    make_box("CoatHook_Rail", (3.385, 0.70, 1.60), (0.03, 0.50, 0.06),
             PITSTOP_WOOD)
    for i, hy in enumerate([0.52, 0.70, 0.88]):
        make_cyl(f"CoatHook_{i}", (3.34, hy, 1.57), 0.012, 0.08,
                 PITSTOP_BRASS, axis='X')


# ═════════════════════════════════════════════════════════════════
# EXTERIOR SLICES — what the real openings look out on.
# West: sidewalk, strip-mall lot, the black Louisiana pickup parked
# at the lot edge (ch2 L78; plate LA 7R3-G92 per ch3 — lettering is
# Label3D on Pickup_PlatePanel), the Coin Wash across the side lot
# (ch7), day-sky backdrop. North: the dumpster (ch2_dumpster).
# ═════════════════════════════════════════════════════════════════
def build_exterior():
    # West slice
    make_box("Sidewalk_W", (-3.85, 3.0, 0.01), (0.5, 6.4, 0.08),
             COL_SIDEWALK)
    make_box("Asphalt_W", (-5.35, 3.0, -0.02), (2.5, 6.4, 0.06),
             PITSTOP_ASPHALT)
    for i, sy in enumerate([1.1, 2.3, 3.5]):
        make_box(f"LotStripe_{i}", (-4.55, sy, 0.013), (0.90, 0.10, 0.002),
                 PITSTOP_STRIPE)
    # The pickup — nose north, parked at the lot edge, driver never
    # coming in (ch2/ch3). Box-slab tiers per the playbook car rule.
    px, py = -5.2, 2.3
    make_box("Pickup_BodyLower", (px, py, 0.75), (1.8, 4.4, 0.50),
             PITSTOP_PICKUP_BLK)
    make_box("Pickup_Cab", (px, py + 0.6, 1.28), (1.70, 1.60, 0.55),
             PITSTOP_PICKUP_BLK)
    make_box("Pickup_CabGlass", (px, py + 0.6, 1.33), (1.74, 1.20, 0.30),
             COL_CAB_GLASS)
    make_box("Pickup_BedFloor", (px, py - 1.0, 1.02), (1.60, 2.20, 0.04),
             (0.06, 0.06, 0.07, 1.0))
    for i, (wx, wy) in enumerate([(-0.80, +1.35), (+0.80, +1.35),
                                  (-0.80, -1.35), (+0.80, -1.35)]):
        make_cyl(f"Pickup_Wheel_{i}", (px + wx, py + wy, 0.34), 0.34, 0.26,
                 (0.08, 0.08, 0.09, 1.0), axis='X', segments=10)
        make_cyl(f"Pickup_Hub_{i}", (px + wx, py + wy, 0.34), 0.10, 0.28,
                 PITSTOP_STEEL_DK, axis='X', segments=8)
    make_box("Pickup_PlatePanel", (px, py - 2.21, 0.75), (0.30, 0.02, 0.15),
             (0.92, 0.92, 0.88, 1.0))
    # Coin Wash across the side lot (the booth window sees it, ch7)
    make_box("CoinWash_Facade", (-6.8, 5.1, 1.5), (0.16, 2.6, 3.0),
             PITSTOP_COINWASH)
    make_box("CoinWash_SignBand", (-6.70, 5.1, 2.60), (0.02, 2.0, 0.42),
             PITSTOP_RED)
    for i, wy in enumerate([4.45, 5.10, 5.75]):
        make_cyl(f"CoinWash_Porthole_{i}", (-6.70, wy, 1.15), 0.20, 0.06,
                 PITSTOP_STEEL_DK, axis='X', segments=12)
        make_cyl(f"CoinWash_PortholeGlass_{i}", (-6.68, wy, 1.15), 0.15,
                 0.05, (0.18, 0.22, 0.26, 1.0), axis='X', segments=12)
    make_box("Day_Backdrop_W", (-7.3, 3.0, 1.8), (0.12, 7.6, 3.6),
             PITSTOP_DAY_SKY)
    # North slice — the dumpster (ch2: Jesse "leans against the
    # dumpster, which he has never leaned against before"; the
    # grease streak is why)
    make_box("Asphalt_N", (1.9, 7.0, -0.02), (4.0, 1.8, 0.06),
             PITSTOP_ASPHALT)
    make_box("Dumpster_Body", (2.7, 6.9, 0.68), (1.7, 0.95, 1.15),
             COL_DUMPSTER)
    for i, lx in enumerate([2.30, 3.10]):
        make_box(f"Dumpster_Lid_{i}", (lx, 6.9, 1.28), (0.76, 0.98, 0.05),
                 (0.22, 0.28, 0.22, 1.0))
    make_box("Dumpster_GreaseStreak", (2.7, 6.41, 0.55), (1.30, 0.012, 0.45),
             PITSTOP_GREASE)
    make_box("Day_Backdrop_N", (1.9, 7.95, 1.7), (4.4, 0.12, 3.4),
             PITSTOP_DAY_SKY)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — fluorescents, mint pendants over the counter,
# smoke detector, HVAC, Muzak speaker.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for j, (fx, fy) in enumerate([(-1.8, 1.6), (1.8, 1.6),
                                  (-1.8, 3.6), (2.6, 3.4)]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (fx, fy, CEIL),
                                      length=1.30, width=0.32)
    for j, (fx, fy) in enumerate([(-2.2, 5.35), (0.9, 5.35)]):
        make_fluorescent_tube_fixture(f"Fluor_K{j}", (fx, fy, CEIL),
                                      length=1.30, width=0.32)
    # Pendants over the counter
    for i, px in enumerate([0.2, 1.6]):
        make_cyl(f"Pendant_{i}_Rod", (px, 3.55, 2.65), 0.015, 0.30,
                 PITSTOP_STEEL_DK)
        make_cyl(f"Pendant_{i}_Shade", (px, 3.55, 2.44), 0.14, 0.12,
                 PITSTOP_MINT, segments=12)
        make_cyl(f"Pendant_{i}_Bulb", (px, 3.55, 2.36), 0.05, 0.05,
                 (1.0, 0.90, 0.66, 1.0), segments=10)
    make_smoke_detector("Smoke", (-0.9, 2.6, CEIL))
    make_hvac_vent("HVAC", (2.6, 2.0, CEIL), width=0.80, depth=0.40)
    make_ceiling_speaker("MuzakSpeaker", (-2.6, 1.2, CEIL))


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_booths()
    build_counter()
    build_pass_through()
    build_kitchen()
    build_east_wall()
    build_exterior()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pit_stop_interior.glb"))
    print(f"\n[build_pit_stop_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
