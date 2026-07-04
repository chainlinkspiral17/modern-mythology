"""Henderson Kitchen — the Henderson house on Magnolia, Harmony
Creek / New Auburn, TX — vol6 hero locale (6 VN bg refs:
vol6_ch3_jesse_bedroom close, vol6_ch7_henderson_kitchen "Pot
Roast", vol6_ch20_prints "The Prints", vol6_ch22_foxhole close,
vol6_ch23_sleep x2 — Sunday dinner + the 23:18 lights-out beat).

Eileen and Jim Henderson's kitchen — the room this family keeps
coming back to. Canon baked in:

  · vol6_ch7 — the table set for FOUR with "a fourth, at the head
    of the table": rectangular walnut table, Jim's chair at the
    head, Jesse "sitting next to his father, on his right", Ben
    across the corner, Eileen opposite. The seat geography is kept:
    head chair WEST, Jesse on the south long side at his father's
    right hand, Eileen north, Ben at the east end.
  · vol6_ch20_prints — Jim at the kitchen table at 22:38 with "a
    small set of black-and-white photographs — the contact prints",
    including THE print of the terra-cotta pot behind the garden
    shed ("the pot is the whole picture"). Contact prints spread at
    the head place; the same shed + pot are modeled for real in
    build_jesse_bedroom's back-yard view — one house, one garden.
  · vol6_ch20_prints / vol6_ch22_foxhole — "the kitchen light is
    on" at ten thirty-eight and again at twelve thirty-one; the
    music-catalog desc for the fourth chord ties the two rooms by
    their clocks ("found at four-twelve in Jesse's bedroom, the
    kitchen light still on at ten thirty-eight"). Wall clock frozen
    at 10:38 (the bedroom's alarm clock holds 4:12).
  · vol6_ch22_foxhole — the folded Substation Nine lyric sheet
    from the band's printed flyer, on the table where Jim reads it
    at 12:31 before pocketing it. The flyer itself is magneted to
    the fridge (Eileen "had brought [it] home... from the band's
    printed flyer earlier this week").
  · vol6_ch20_prints — "the pot's fresh": decaf drip machine on
    the counter (Eileen switched in July; Jim "by attrition"). Two
    mugs at the table — Jim's and the one Jesse pours at 22:40.
  · vol6_ch6_jesse_bedroom — the pitcher of iced tea, "the small
    steady thing she does": glass pitcher on the counter.
  · vol6_ch3 — Eileen at the SINK drying her hands; "the faint
    sound of his mother running the dishwasher": sink under the
    window, dishwasher beside it.
  · vol6_ch7 — "The pot roast has been in the oven since
    two-thirty... stays in the oven on warm": a real range with a
    real oven door. (The horseradish dish since 1999 comes out
    with the roast and stays in the cabinet here.)
  · vol6_ch7 — the basement door + stairs are HEARD from this
    room, not seen ("At seven oh-eight the basement door opens.
    Footsteps on the stairs... Mr. Henderson comes through the
    doorway"): rendered as the dark cased hall opening in the EAST
    wall — past the laundry room, past the half-bath, down to the
    darkroom two floors below. The doorway Jesse stands in is the
    south camera gap.
  · vol6_ch20_prints / ch22 exterior — "His mother's car is in the
    driveway. His father's truck is also in the driveway. The
    kitchen light is on": the window faces the front — Jim's
    pickup + Eileen's sedan side by side on the double drive, the
    front walk Jesse comes up at 12:31, and a SOUTHERN MAGNOLIA in
    the front yard (the house is "on Magnolia",
    vol6_ch22_sunday:36) with the last late-August blooms.
  · vol6_ch23_sleep — Eileen's Sunday pot roast + "ice cream for
    after" (freezer top door), and the PIANO decision: the piano
    goes in the DINING ROOM ("We don't dine in the dining room. We
    dine here."). Canon-negative: no piano, no small lamp table in
    the kitchen — and "we dine here" is why the table is the
    room's center of mass.

Canon-NEGATIVES honored (what this kitchen does NOT have):
  · NO piano (dining room's, Wednesday's) — vol6_ch23_sleep.
  · NO Graflex cameras / donation boxes — Mr. Henderson's vintage
    Graflexes live in the STUDY (glitch_report.md:303), and the
    Henderson Donation boxes have been at Cosmic Comics since 2017.
  · NO basement door leaf in this room — it is heard offstage
    (ch7); only the dark hall opening east.
  · NO commercial fluorescents / drop grid / ceiling speaker — the
    scaffold's tubes were store vocabulary; a house gets one warm
    schoolhouse fixture (THE kitchen light of 10:38).
  · NO landline wall phone (that is the Millers' signature beat)
    and NO wallpaper border (Miller 1991); this is a 1998 build —
    the down payment was the arrangement (vol6_ch7).

Household register vs the other HCE kitchens: the Hendersons are
sage siding, white-painted cabinet fronts, dusty-blue laminate and
dark walnut furniture — NOT the Millers' cream/golden-oak/almond,
NOT the Caldwells' pine and pale-yellow ceiling. Jim's photography
is the house's quiet layer: contact prints on the table, one
framed garden print on the west wall.

Shell footprint kept from the scaffold (6.5 x 5.5, CEIL 2.6, south
gap x -1..+1 = the kitchen doorway the Background3D camera preset
(0, 2.30, +0.5 / yaw 180 / fov 60) shoots through). Window is a
REAL OPENING with frame + sash rails, no glass (playbook
no-transparency rule).

HENDERSON HOUSE shared block below is byte-identical with
build_jesse_bedroom.py (⚠ KEEP IN SYNC — verify with md5).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.decor import make_wall_clock, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 6.5; ROOM_D = 5.5; CEIL = 2.6

# ═════════════════════════════════════════════════════════════════
# HENDERSON HOUSE — SHARED PALETTE + VOCABULARY (⚠ KEEP IN SYNC)
# This block is declared IDENTICALLY in build_henderson_kitchen.py
# and build_jesse_bedroom.py — two rooms of the Henderson house on
# Magnolia (vol6_ch22_sunday:36). ONE house: if you retune a value
# here, retune the sibling file to match (verify with md5). A 1998
# build (the down payment was the arrangement — vol6_ch7): sage
# lap siding, white trim, white-painted cabinets, dark walnut
# furniture. Deliberately NOT the Millers' cream/golden-oak and
# NOT the Caldwells' pine/pale-yellow — a distinct household.
# ═════════════════════════════════════════════════════════════════
HENDERSON_SIDING    = (0.64, 0.68, 0.58, 1.0)   # sage-green lap siding
HENDERSON_SIDING_SH = (0.50, 0.54, 0.45, 1.0)   # siding shadow seams
HENDERSON_TRIM      = (0.93, 0.92, 0.87, 1.0)   # painted-white trim/casing
HENDERSON_ROOF      = (0.36, 0.33, 0.30, 1.0)   # weathered grey shingle
HENDERSON_INT_WALL  = (0.92, 0.88, 0.70, 1.0)   # Eileen's butter-yellow
HENDERSON_BASEBOARD = (0.44, 0.34, 0.24, 1.0)
HENDERSON_WALNUT    = (0.40, 0.28, 0.19, 1.0)   # the dark walnut furniture
HENDERSON_WALNUT_DK = (0.27, 0.18, 0.12, 1.0)
HENDERSON_CAB_WHITE = (0.90, 0.89, 0.84, 1.0)   # white-painted cabinet fronts
HENDERSON_LAMINATE  = (0.52, 0.60, 0.62, 1.0)   # dusty-blue counter laminate
HENDERSON_APPLIANCE = (0.92, 0.92, 0.90, 1.0)   # white appliances
COL_CARPET      = (0.55, 0.52, 0.45, 1.0)   # upstairs wall-to-wall
COL_CARPET_SH   = (0.46, 0.43, 0.37, 1.0)
COL_CEIL_WHITE  = (0.93, 0.91, 0.86, 1.0)   # flat drywall
COL_CERAMIC     = (0.92, 0.90, 0.84, 1.0)   # plates / mugs
COL_COFFEE      = (0.30, 0.20, 0.12, 1.0)   # decaf reads the same
COL_TEA         = (0.68, 0.44, 0.20, 1.0)   # Eileen's iced-tea amber
COL_BRASS       = (0.70, 0.57, 0.30, 1.0)
COL_LAMP_GLOW   = (0.98, 0.88, 0.62, 1.0)
COL_INK         = (0.22, 0.21, 0.21, 1.0)
COL_PHOTO_GREY  = (0.58, 0.58, 0.56, 1.0)   # Jim's b/w print mid-tone
COL_PHOTO_DK    = (0.24, 0.24, 0.24, 1.0)   # Jim's b/w print shadow
COL_BLIGHT_ORANGE = (0.88, 0.52, 0.16, 1.0) # the band's orange sticker stock
COL_NIGHT_PANE  = (0.10, 0.12, 0.15, 1.0)   # unlit panes at night
COL_WINDOW_LIT  = (0.52, 0.46, 0.30, 1.0)   # one faintly lit pane
COL_PORCHBULB   = (1.00, 0.88, 0.60, 1.0)
COL_CONCRETE    = (0.64, 0.62, 0.56, 1.0)
COL_ASPHALT     = (0.22, 0.22, 0.23, 1.0)
COL_LAWN_AUG    = (0.40, 0.44, 0.24, 1.0)   # mid-August Bermuda
COL_LAWN_BROWN  = (0.58, 0.51, 0.30, 1.0)   # the browning patches
COL_TRUNK       = (0.36, 0.28, 0.20, 1.0)
COL_MAGNOLIA_LEAF   = (0.20, 0.30, 0.18, 1.0)  # glossy southern magnolia
COL_MAGNOLIA_LEAF_2 = (0.16, 0.25, 0.15, 1.0)
COL_MAGNOLIA_BLOOM  = (0.94, 0.92, 0.82, 1.0)  # late creamy blooms

_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _henderson_chair(prefix, cx, cy, facing):
    """The Hendersons' walnut ladder-back kitchen chair — four at
    the table, the fourth at the head (vol6_ch7). Three rungs, not
    the Millers' two-slat oak. Declared identically in both
    Henderson files; keep the geometry in sync."""
    dx, dy = _DIRS[facing]
    make_box(f"{prefix}_Seat", (cx, cy, 0.45), (0.42, 0.42, 0.045), HENDERSON_WALNUT)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.17, cy + sy * 0.17, 0.225),
                 0.019, 0.45, HENDERSON_WALNUT_DK)
    bx, by = cx - dx * 0.20, cy - dy * 0.20
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.17 if dx == 0 else 0.0)
        py = by + (sgn * 0.17 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_Post_{pi}", (px, py, 0.72), 0.017, 0.54, HENDERSON_WALNUT)
    slat = (0.38, 0.030, 0.055) if dx == 0 else (0.030, 0.38, 0.055)
    for si, sz in enumerate((0.66, 0.80, 0.94)):
        make_box(f"{prefix}_Rung_{si}", (bx, by, sz), slat, HENDERSON_WALNUT)
# ═════════ end shared block ══════════════════════════════════════

# ── Kitchen-only palette ─────────────────────────────────────────
COL_VINYL        = (0.77, 0.76, 0.68, 1.0)   # grey-green sheet vinyl
COL_VINYL_SEAM   = (0.56, 0.55, 0.47, 1.0)
COL_LAMINATE_EDGE = (0.40, 0.47, 0.49, 1.0)  # self-edge band, darker blue
COL_GLASS_GREY   = (0.80, 0.84, 0.82, 1.0)   # pitcher / carafe glass
COL_HALL_DARK    = (0.07, 0.07, 0.08, 1.0)   # the unlit hall east
COL_STEEL_DK     = (0.44, 0.46, 0.48, 1.0)
COL_TRUCK        = (0.32, 0.40, 0.46, 1.0)   # Jim's faded steel-blue pickup
COL_TRUCK_DK     = (0.22, 0.28, 0.33, 1.0)
COL_SEDAN_MAROON = (0.42, 0.18, 0.18, 1.0)   # Eileen's sedan

PAL_WALL = {"wall": HENDERSON_INT_WALL, "baseboard": HENDERSON_BASEBOARD}

GRADE_Z = -0.40           # front-yard grade outside the window
WIN_W = 1.60              # window opening x -0.80..+0.80
WIN_SILL = 0.95
WIN_HEAD = 2.15


# ═════════════════════════════════════════════════════════════════
# SHELL — grey-green vinyl floor, butter-yellow walls, flat drywall
# ceiling (house, not store: no drop grid, no stains, no border).
# North wall carries the front window over the sink; south wall
# keeps the scaffold camera gap (the kitchen doorway Jesse stands
# in at 12:31, ch22) with painted casing.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_VINYL, "seam": COL_VINYL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall — window opening x -0.80..+0.80, sill 0.95, head 2.15
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20     # 2.65
    seg_cx = WIN_W / 2.0 + seg_len / 2.0              # 2.125
    make_wall("Wall_N_W", (-seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_SillFill", (0.0, ROOM_D, WIN_SILL / 2.0), (WIN_W, 0.20, WIN_SILL),
             HENDERSON_INT_WALL)
    make_box("Wall_N_HeadFill", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.20, CEIL - WIN_HEAD), HENDERSON_INT_WALL)
    # South wall — scaffold gap x -1..+1 kept (camera doorway)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             HENDERSON_INT_WALL)
    # The kitchen doorway casing — Jesse stands here (ch20/ch22)
    for sgn in (-1, +1):
        make_box(f"KitchenDoor_Jamb_{sgn:+d}", (sgn * 1.03, 0.0, 1.00),
                 (0.10, 0.26, 2.00), HENDERSON_TRIM)
    make_box("KitchenDoor_Head", (0.0, 0.0, 2.05), (2.26, 0.26, 0.10), HENDERSON_TRIM)
    # Flat drywall ceiling — house, not store
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_CEIL_WHITE},
                 with_grid=False, with_stains=False)


# ═════════════════════════════════════════════════════════════════
# WINDOW — over the sink, facing the front drive (ch20/ch22: the
# kitchen light visible from the driveway means the window faces
# it back). REAL OPENING, white double-hung sash, meeting rail +
# muntins, casing/stool/apron. Short café curtains on the lower
# sash only — Eileen's kitchen, not the Millers' sheers. THE CLOCK
# above the window, frozen at 10:38 — "the kitchen light still on
# at ten thirty-eight" (music_catalog: the fourth-chord desc).
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D               # wall centerline 5.5; interior face 5.4
    make_box("Win_FrameT", (0.0, wy, WIN_HEAD - 0.03), (WIN_W, 0.14, 0.06), HENDERSON_TRIM)
    make_box("Win_FrameB", (0.0, wy, WIN_SILL + 0.03), (WIN_W, 0.14, 0.06), HENDERSON_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Jamb_{sgn:+d}", (sgn * (WIN_W / 2.0 - 0.03), wy, 1.55),
                 (0.06, 0.14, 1.20), HENDERSON_TRIM)
    make_box("Win_MeetingRail", (0.0, wy, 1.56), (WIN_W - 0.08, 0.10, 0.06), HENDERSON_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Muntin_{sgn:+d}", (sgn * 0.26, wy - 0.02, 1.86),
                 (0.035, 0.06, 0.54), HENDERSON_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Casing_{sgn:+d}", (sgn * (WIN_W / 2.0 + 0.09), wy - 0.105, 1.55),
                 (0.10, 0.05, 1.40), HENDERSON_TRIM)
    make_box("Win_CasingHead", (0.0, wy - 0.105, WIN_HEAD + 0.08),
             (WIN_W + 0.28, 0.05, 0.10), HENDERSON_TRIM)
    make_box("Win_Stool", (0.0, wy - 0.135, WIN_SILL + 0.02), (WIN_W + 0.30, 0.16, 0.04),
             HENDERSON_TRIM)
    make_box("Win_Apron", (0.0, wy - 0.105, WIN_SILL - 0.05), (WIN_W + 0.16, 0.05, 0.09),
             HENDERSON_TRIM)
    # Café curtains — tension rod at the meeting rail, two short
    # gingham-ish panels over the lower sash, parted at the middle
    make_cyl("Cafe_Rod", (0.0, wy - 0.10, 1.60), 0.010, 1.52, COL_BRASS, axis='X')
    for sgn in (-1, +1):
        make_box(f"Cafe_Panel_{sgn:+d}", (sgn * 0.52, wy - 0.095, 1.29),
                 (0.44, 0.025, 0.58), (0.90, 0.84, 0.66, 1.0))
        make_box(f"Cafe_Fold_{sgn:+d}", (sgn * 0.40, wy - 0.112, 1.27),
                 (0.10, 0.016, 0.52), (0.82, 0.75, 0.56, 1.0))
    # THE CLOCK — 10:38 (ch20_prints: the arrival minute)
    make_wall_clock("Clock", (0.0, wy - 0.14, 2.37), frozen_hour=10, frozen_min=38)


# ═════════════════════════════════════════════════════════════════
# COUNTER RUN — white-painted cabinet fronts under a dusty-blue
# laminate top along the north wall. Sink under the window (ch3:
# Eileen drying her hands); DISHWASHER west of it (ch3: heard
# through the floor); the range whose oven held the pot roast from
# two-thirty (ch7); microwave (ch22: he heats up the leftover
# enchiladas); the DECAF drip machine, pot fresh at 22:40 (ch20);
# Eileen's iced-tea pitcher (ch6). Uppers flank the window.
# ═════════════════════════════════════════════════════════════════
def build_counter_run():
    # Base cabinets: x -3.05..+1.55, depth 0.58 (front face y ~4.82)
    make_box("Base_Body", (-0.75, 5.11, 0.445), (4.60, 0.58, 0.79), HENDERSON_CAB_WHITE)
    make_box("Base_Kick", (-0.75, 4.85, 0.05), (4.50, 0.03, 0.10), HENDERSON_WALNUT_DK)
    make_box("Counter_Top", (-0.75, 5.10, 0.89), (4.68, 0.66, 0.04), HENDERSON_LAMINATE)
    make_box("Counter_Edge", (-0.75, 4.785, 0.89), (4.68, 0.03, 0.04), COL_LAMINATE_EDGE)
    make_box("Backsplash", (-0.75, 5.375, 1.00), (4.60, 0.03, 0.18), HENDERSON_LAMINATE)
    # Cabinet door + drawer fronts (skip the appliance bays: range
    # x -2.43..-1.67, dishwasher x -1.15..-0.55)
    doors = [(-2.90, 0.44), (-1.41, 0.44), (0.0, 0.50), (0.57, 0.50), (1.15, 0.55)]
    for di, (dx, dw) in enumerate(doors):
        make_box(f"Base_Door_{di}", (dx, 4.825, 0.40), (dw - 0.04, 0.02, 0.54),
                 HENDERSON_CAB_WHITE)
        make_cyl(f"Base_Knob_{di}", (dx + dw / 2.0 - 0.06, 4.81, 0.62), 0.014, 0.03,
                 COL_BRASS, axis='Y')
        if abs(dx) > 0.3:     # drawers everywhere except the sink front
            make_box(f"Base_Drawer_{di}", (dx, 4.825, 0.775), (dw - 0.04, 0.02, 0.14),
                     HENDERSON_CAB_WHITE)
            make_cyl(f"Base_DrawerKnob_{di}", (dx, 4.81, 0.775), 0.014, 0.03,
                     COL_BRASS, axis='Y')
    # Upper cabinets flanking the window + short cab over the hood
    uppers = [("W0", -2.90, 0.62, 1.90, 0.76), ("Hood", -2.05, 0.76, 2.14, 0.28),
              ("W1", -1.30, 0.86, 1.90, 0.76), ("E0", 1.20, 0.68, 1.90, 0.76)]
    for nm, ux, uw, uz, uh in uppers:
        make_box(f"Upper_{nm}", (ux, 5.235, uz), (uw, 0.33, uh), HENDERSON_CAB_WHITE)
        make_box(f"Upper_{nm}_Seam", (ux, 5.065, uz), (0.012, 0.012, uh - 0.06),
                 (0.74, 0.73, 0.68, 1.0))
        make_cyl(f"Upper_{nm}_Knob", (ux - 0.06, 5.06, uz - uh / 2.0 + 0.10),
                 0.013, 0.03, COL_BRASS, axis='Y')
    # Sink under the window + faucet + dish soap + Eileen's towel
    make_box("Sink_Rim", (0.0, 5.10, 0.925), (0.82, 0.52, 0.02), P.METAL_STEEL)
    make_box("Sink_Basin", (0.0, 5.10, 0.83), (0.70, 0.42, 0.17), P.METAL_STEEL,
             open_faces={'+Z'})
    make_box("Sink_BasinFloor", (0.0, 5.10, 0.752), (0.66, 0.38, 0.012), COL_STEEL_DK)
    make_cyl("Faucet_Base", (0.0, 5.32, 0.955), 0.030, 0.04, P.METAL_STEEL)
    make_cyl("Faucet_Riser", (0.0, 5.32, 1.06), 0.016, 0.20, P.METAL_STEEL)
    make_cyl("Faucet_Spout", (0.0, 5.22, 1.15), 0.014, 0.22, P.METAL_STEEL, axis='Y')
    make_box("Faucet_Handle", (0.10, 5.32, 1.17), (0.08, 0.02, 0.02), P.METAL_STEEL)
    make_cyl("DishSoap", (0.36, 5.30, 0.985), 0.022, 0.13, (0.60, 0.70, 0.42, 1.0))
    # The dish towel over the sink edge (ch3 — she was drying her
    # hands with it)
    make_box("DishTowel", (-0.52, 4.80, 0.845), (0.20, 0.05, 0.13),
             (0.86, 0.80, 0.62, 1.0))
    # Dishwasher west of the sink (ch3 — running, heard upstairs)
    make_box("DW_Front", (-0.85, 4.83, 0.45), (0.60, 0.025, 0.74), HENDERSON_APPLIANCE)
    make_box("DW_Handle", (-0.85, 4.81, 0.80), (0.55, 0.03, 0.04), P.METAL_STEEL)
    make_box("DW_Controls", (-0.85, 4.815, 0.72), (0.50, 0.012, 0.05), COL_STEEL_DK)
    # Range — THE oven (pot roast in since two-thirty, ch7) + hood
    make_box("Range_Body", (-2.05, 5.08, 0.45), (0.76, 0.64, 0.90), HENDERSON_APPLIANCE)
    make_box("Range_Cooktop", (-2.05, 5.08, 0.915), (0.76, 0.64, 0.02), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([(-0.19, -0.16), (0.19, -0.16), (-0.19, 0.16),
                                   (0.19, 0.16)]):
        make_cyl(f"Range_Burner_{bi}", (-2.05 + bx, 5.08 + by, 0.930), 0.085, 0.010,
                 (0.12, 0.11, 0.10, 1.0), segments=10)
    make_box("Range_Backguard", (-2.05, 5.365, 0.98), (0.76, 0.05, 0.12),
             HENDERSON_APPLIANCE)
    for ki in range(4):
        make_cyl(f"Range_Knob_{ki}", (-2.29 + ki * 0.16, 5.335, 0.99), 0.018, 0.025,
                 P.METAL_BLACK, axis='Y')
    make_box("Range_OvenDoor", (-2.05, 4.755, 0.46), (0.70, 0.02, 0.52),
             HENDERSON_APPLIANCE)
    make_box("Range_OvenWindow", (-2.05, 4.745, 0.50), (0.42, 0.012, 0.22), P.METAL_BLACK)
    make_box("Range_OvenHandle", (-2.05, 4.74, 0.76), (0.72, 0.03, 0.03), P.METAL_STEEL)
    make_box("Hood_Body", (-2.05, 5.18, 1.96), (0.76, 0.44, 0.14), HENDERSON_APPLIANCE)
    make_box("Hood_Lip", (-2.05, 4.97, 1.90), (0.76, 0.03, 0.05), P.METAL_STEEL)
    # Microwave in the west corner (ch22: "He heats them up")
    make_box("Microwave_Body", (-2.85, 5.13, 1.065), (0.50, 0.38, 0.30),
             HENDERSON_APPLIANCE)
    make_box("Microwave_Window", (-2.93, 4.935, 1.065), (0.28, 0.012, 0.22), P.METAL_BLACK)
    make_box("Microwave_Handle", (-2.64, 4.935, 1.065), (0.03, 0.015, 0.24), COL_STEEL_DK)
    # THE DECAF DRIP MACHINE — "It's decaf... The pot's fresh"
    # (ch20_prints, 22:40). Black machine, glass carafe, coffee in.
    make_box("Decaf_Body", (0.55, 5.22, 1.06), (0.22, 0.24, 0.30), P.METAL_BLACK)
    make_box("Decaf_Hood", (0.55, 5.14, 1.19), (0.22, 0.30, 0.05), P.METAL_BLACK)
    make_cyl("Decaf_Carafe", (0.55, 5.10, 0.985), 0.062, 0.145, COL_GLASS_GREY,
             segments=12)
    make_cyl("Decaf_Coffee", (0.55, 5.10, 0.955), 0.052, 0.070, COL_COFFEE, segments=12)
    make_box("Decaf_Switch", (0.55, 5.095, 1.10), (0.05, 0.012, 0.03),
             (0.86, 0.42, 0.32, 1.0))
    # EILEEN'S ICED-TEA PITCHER (ch6 — "the small steady thing she
    # does when she does not, otherwise, know what to do")
    make_cyl("TeaPitcher_Glass", (1.15, 5.15, 0.99), 0.058, 0.19, COL_GLASS_GREY,
             segments=12)
    make_cyl("TeaPitcher_Tea", (1.15, 5.15, 0.955), 0.048, 0.11, COL_TEA, segments=12)
    make_box("TeaPitcher_Handle", (1.23, 5.15, 1.00), (0.020, 0.016, 0.13),
             COL_GLASS_GREY)
    make_cyl("TeaGlass", (1.36, 5.05, 0.945), 0.032, 0.10, COL_GLASS_GREY, segments=10)
    # Salt + pepper by the range
    make_cyl("Salt", (-1.55, 5.25, 0.965), 0.020, 0.11, COL_CERAMIC, segments=8)
    make_cyl("Pepper", (-1.47, 5.21, 0.965), 0.020, 0.11, (0.36, 0.30, 0.26, 1.0),
             segments=8)


# ═════════════════════════════════════════════════════════════════
# FRIDGE — white top-freezer east of the counter ("ice cream for
# after" lives up top, ch23_sleep; Thursday's enchiladas below,
# ch22 — both inside, unmodeled). On the door: THE FOXHOLE FLYER
# for SAT 8/22 (Eileen brought it home, ch20_prints — the lyric
# sheet printed on it is the one on the table), a small b/w
# contact print of Jim's, and magnets.
# ═════════════════════════════════════════════════════════════════
def build_fridge():
    fx, fy = 2.55, 5.05
    make_box("Fridge_Body", (fx, fy, 0.86), (0.82, 0.72, 1.72), HENDERSON_APPLIANCE)
    make_box("Fridge_DoorSeam", (fx, fy - 0.365, 1.28), (0.80, 0.015, 0.03), COL_STEEL_DK)
    make_box("Fridge_HandleTop", (fx - 0.35, fy - 0.375, 1.46), (0.035, 0.035, 0.26),
             COL_STEEL_DK)
    make_box("Fridge_HandleBot", (fx - 0.35, fy - 0.375, 0.86), (0.035, 0.035, 0.50),
             COL_STEEL_DK)
    make_box("Fridge_Grille", (fx, fy - 0.365, 0.06), (0.78, 0.02, 0.10), COL_STEEL_DK)
    # THE FOXHOLE FLYER — SAT 8/22 · SUBURBAN BLIGHT (photocopy:
    # white stock, Jesse's block-letter band bar, the tentacled-
    # monster scrawl under it)
    make_box("Fridge_Flyer", (fx + 0.16, fy - 0.373, 1.52), (0.15, 0.012, 0.21), P.PAPER)
    make_box("Fridge_Flyer_Band", (fx + 0.16, fy - 0.380, 1.595), (0.13, 0.006, 0.035),
             COL_INK)
    make_box("Fridge_Flyer_Monster", (fx + 0.16, fy - 0.380, 1.50), (0.10, 0.006, 0.11),
             COL_INK)
    make_box("Fridge_Flyer_DateLine", (fx + 0.16, fy - 0.380, 1.435),
             (0.11, 0.006, 0.016), COL_INK)
    # One of Jim's contact prints, magneted up (the garden series)
    make_box("Fridge_Print", (fx - 0.18, fy - 0.373, 1.50), (0.11, 0.012, 0.09),
             COL_PHOTO_GREY)
    make_box("Fridge_Print_Image", (fx - 0.18, fy - 0.380, 1.50), (0.09, 0.006, 0.07),
             COL_PHOTO_DK)
    # Assorted magnets (one is band-orange — Em's sticker stock)
    for mi, (mx, mz, tint) in enumerate([(-0.28, 1.66, COL_BLIGHT_ORANGE),
                                         (0.30, 1.38, (0.34, 0.42, 0.54, 1.0)),
                                         (-0.04, 1.64, (0.86, 0.42, 0.32, 1.0)),
                                         (0.24, 1.08, (0.56, 0.58, 0.42, 1.0)),
                                         (-0.25, 0.98, (0.70, 0.57, 0.30, 1.0))]):
        make_box(f"Fridge_Magnet_{mi}", (fx + mx, fy - 0.376, mz), (0.035, 0.008, 0.045),
                 tint)


# ═════════════════════════════════════════════════════════════════
# TABLE — "We don't dine in the dining room. We dine here."
# (ch23_sleep). Rectangular walnut table, long axis E-W, the seat
# geography of ch7 kept: JIM AT THE HEAD (west), JESSE on the
# south long side at his father's right hand, EILEEN north, BEN's
# seat at the east end. Dressed for the 22:38 tableau
# (ch20_prints): the contact prints between them — THE print of
# the pot behind the shed among them — two mugs of decaf, and the
# folded Substation Nine lyric sheet (ch22) waiting at Jim's place.
# ═════════════════════════════════════════════════════════════════
def build_table_zone():
    tx, ty = 0.15, 2.55
    make_box("Table_Top", (tx, ty, 0.745), (1.55, 0.95, 0.045), HENDERSON_WALNUT)
    make_box("Table_Apron", (tx, ty, 0.685), (1.42, 0.82, 0.07), HENDERSON_WALNUT)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Table_Leg_{li}", (tx + sx * 0.68, ty + sy * 0.38, 0.34),
                 (0.055, 0.055, 0.68), HENDERSON_WALNUT_DK)
    _henderson_chair("Chair_Jim", tx - 1.02, ty, 'E')       # THE HEAD (ch7)
    _henderson_chair("Chair_Jesse", tx - 0.30, ty - 0.72, 'N')  # dad's right hand
    _henderson_chair("Chair_Eileen", tx + 0.10, ty + 0.72, 'S')
    _henderson_chair("Chair_Ben", tx + 1.02, ty, 'W')       # the east end
    top = 0.7675
    # THE CONTACT PRINTS (ch20_prints) — small b/w rectangles
    # spread at the head place; the largest one turned toward
    # Jesse's seat is the pot-behind-the-shed print.
    prints = [(-0.62, 0.10, 0.090, 0.110), (-0.48, -0.06, 0.085, 0.105),
              (-0.66, -0.14, 0.080, 0.100), (-0.36, 0.16, 0.085, 0.105)]
    for pi, (px, py, pw, pd) in enumerate(prints):
        make_box(f"Print_{pi}", (tx + px, ty + py, top + 0.002), (pw, pd, 0.003),
                 COL_PHOTO_GREY)
        make_box(f"Print_{pi}_Image", (tx + px, ty + py, top + 0.0045),
                 (pw - 0.018, pd - 0.018, 0.002), COL_PHOTO_DK)
    # The pot print — nearest Jesse's seat ("the pot is the whole
    # picture"): a pale pot shape in the dark field
    make_box("Print_Pot", (tx - 0.44, ty - 0.26, top + 0.002), (0.100, 0.120, 0.003),
             COL_PHOTO_GREY)
    make_box("Print_Pot_Image", (tx - 0.44, ty - 0.26, top + 0.0045),
             (0.082, 0.102, 0.002), COL_PHOTO_DK)
    make_box("Print_Pot_Shape", (tx - 0.45, ty - 0.27, top + 0.006),
             (0.022, 0.028, 0.002), COL_PHOTO_GREY)
    # THE FOLDED LYRIC SHEET — Substation Nine, off the printed
    # flyer (ch22: Jim reads it at 12:31, then pockets it)
    make_box("LyricSheet", (tx - 0.78, ty + 0.28, top + 0.004), (0.150, 0.105, 0.006),
             P.PAPER)
    make_box("LyricSheet_Crease", (tx - 0.78, ty + 0.28, top + 0.008),
             (0.150, 0.008, 0.003), (0.82, 0.79, 0.72, 1.0))
    for ai in range(3):
        make_box(f"LyricSheet_Line_{ai}", (tx - 0.78, ty + 0.30 - ai * 0.022,
                 top + 0.008), (0.11, 0.006, 0.002), COL_INK)
    # Two mugs of decaf — Jim's at the head, Jesse's across the
    # corner (ch20: "Jesse, at the counter, pours himself a cup")
    for nm, (mx, my) in (("Jim", (tx - 0.60, ty + 0.26)),
                         ("Jesse", (tx - 0.26, ty - 0.30))):
        make_cyl(f"Mug_{nm}", (mx, my, top + 0.047), 0.038, 0.095, COL_CERAMIC,
                 segments=10)
        make_cyl(f"Mug_{nm}_Coffee", (mx, my, top + 0.092), 0.030, 0.006, COL_COFFEE,
                 segments=10)
        make_box(f"Mug_{nm}_Handle", (mx + 0.048, my, top + 0.05), (0.016, 0.014, 0.05),
                 COL_CERAMIC)
    # Napkin holder — walnut, Eileen keeps it filled
    make_box("Napkins_Base", (tx + 0.52, ty + 0.24, top + 0.008), (0.13, 0.09, 0.016),
             HENDERSON_WALNUT_DK)
    make_box("Napkins_Stack", (tx + 0.52, ty + 0.24, top + 0.05), (0.11, 0.07, 0.07),
             P.PAPER)


# ═════════════════════════════════════════════════════════════════
# EAST WALL — the dark cased opening to the back hall: past the
# laundry room, past the half-bath, down the basement stairs (ch7
# — the route the pot-roast smell travels and the stairs the
# footsteps climb at seven oh-eight). The doorway is dark; the
# basement door itself is offstage beyond it. Key hooks by the
# casing (truck + sedan + Civic keys — three drivers).
# ═════════════════════════════════════════════════════════════════
def build_east_wall():
    wf = ROOM_W / 2.0 - 0.10          # interior face x 3.15
    # Dark hall opening — flush dark panel + painted casing
    make_box("Hall_Dark", (wf + 0.005, 3.70, 1.03), (0.012, 0.90, 2.06), COL_HALL_DARK)
    for sgn in (-1, +1):
        make_box(f"Hall_Casing_{sgn:+d}", (wf - 0.02, 3.70 + sgn * 0.51, 1.06),
                 (0.06, 0.10, 2.12), HENDERSON_TRIM)
    make_box("Hall_CasingHead", (wf - 0.02, 3.70, 2.16), (0.06, 1.12, 0.10),
             HENDERSON_TRIM)
    # Key hooks — a small walnut plate, three brass hooks, two key
    # sets hanging (the Civic's is out with Jesse most nights)
    make_box("KeyRack_Plate", (wf - 0.02, 2.55, 1.45), (0.03, 0.30, 0.12),
             HENDERSON_WALNUT)
    for hi, hy in enumerate((2.46, 2.55, 2.64)):
        make_cyl(f"KeyRack_Hook_{hi}", (wf - 0.05, hy, 1.41), 0.007, 0.05, COL_BRASS,
                 axis='X')
    for ki, ky in enumerate((2.46, 2.64)):
        make_box(f"KeyRack_Keys_{ki}", (wf - 0.06, ky, 1.35), (0.015, 0.030, 0.07),
                 P.METAL_STEEL)


# ═════════════════════════════════════════════════════════════════
# WEST WALL — Jim's framed garden print (b/w, walnut frame — the
# photography the house lives with) and Eileen's calendar. NO
# piano here: the piano is Wednesday's, and it goes in the dining
# room (ch23_sleep).
# ═════════════════════════════════════════════════════════════════
def build_west_wall():
    wf = -ROOM_W / 2.0 + 0.10         # interior face x -3.15
    # Framed b/w print — the back-garden series
    make_box("GardenPrint_Frame", (wf + 0.015, 2.45, 1.62), (0.03, 0.46, 0.36),
             HENDERSON_WALNUT_DK)
    make_box("GardenPrint_Mat", (wf + 0.032, 2.45, 1.62), (0.005, 0.40, 0.30),
             COL_CERAMIC)
    make_box("GardenPrint_Image", (wf + 0.036, 2.45, 1.62), (0.004, 0.30, 0.22),
             COL_PHOTO_DK)
    make_box("GardenPrint_Tone", (wf + 0.040, 2.42, 1.58), (0.003, 0.10, 0.08),
             COL_PHOTO_GREY)
    make_calendar("Calendar", (wf + 0.01, 3.95, 1.55))
    # August — Wednesday circled (the piano store, ch23_sleep)
    make_box("Calendar_Mark", (wf + 0.018, 3.90, 1.44), (0.002, 0.045, 0.038),
             (0.78, 0.18, 0.16, 1.0))


# ═════════════════════════════════════════════════════════════════
# CEILING — THE KITCHEN LIGHT (the one still on at 10:38 and at
# 12:31 — the beacon Jesse steers home by). One warm schoolhouse
# globe over the table; house hardware only (no fluorescents, no
# speaker — the scaffold's store vocabulary is gone). Smoke
# detector + HVAC register.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_fixtures():
    lx, ly = 0.15, 2.55               # centered on the table
    make_cyl("KitchenLight_Plate", (lx, ly, CEIL - 0.015), 0.10, 0.025, COL_BRASS,
             segments=12)
    make_cyl("KitchenLight_Stem", (lx, ly, CEIL - 0.09), 0.016, 0.13, COL_BRASS)
    make_cyl("KitchenLight_GlobeTop", (lx, ly, CEIL - 0.20), 0.13, 0.10,
             (0.97, 0.93, 0.82, 1.0), segments=12)
    make_cyl("KitchenLight_GlobeBot", (lx, ly, CEIL - 0.28), 0.095, 0.07,
             (0.97, 0.93, 0.82, 1.0), segments=12)
    make_cyl("KitchenLight_Glow", (lx, ly, CEIL - 0.325), 0.055, 0.02, COL_LAMP_GLOW,
             segments=10)                 # scene Light3D matches from the .tscn
    make_smoke_detector("Smoke", (1.8, 1.0, CEIL))
    make_hvac_vent("HVAC", (-2.2, 4.4, CEIL), width=0.60, depth=0.35)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · THE FRONT DRIVE (through the window) — what the house
# shows Jesse at 22:38 and 12:31 (ch20/ch22): his mother's sedan
# AND his father's truck side by side on the double drive, the
# front walk he comes up, the mailbox, the street — and the
# SOUTHERN MAGNOLIA the street is named for (vol6_ch22_sunday:36),
# still holding a few late blooms in August. Across the street:
# the same tract bones, dark at this hour, one pane lit (another
# cul-de-sac's version of the Hendersons' own kitchen light).
# ═════════════════════════════════════════════════════════════════
def build_exterior_front():
    wallout = ROOM_D + 0.10
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20
    seg_cx = WIN_W / 2.0 + seg_len / 2.0
    # Facade skins wrapping the window opening (sage lap siding)
    make_box("Ext_Skin_W", (-seg_cx, wallout + 0.02, 1.30), (seg_len, 0.06, 2.60),
             HENDERSON_SIDING)
    make_box("Ext_Skin_E", (+seg_cx, wallout + 0.02, 1.30), (seg_len, 0.06, 2.60),
             HENDERSON_SIDING)
    make_box("Ext_Skin_Sill", (0.0, wallout + 0.02, WIN_SILL / 2.0),
             (WIN_W, 0.06, WIN_SILL), HENDERSON_SIDING)
    make_box("Ext_Skin_Head", (0.0, wallout + 0.02, (WIN_HEAD + 2.60) / 2.0),
             (WIN_W, 0.06, 2.60 - WIN_HEAD), HENDERSON_SIDING)
    for si, sz in enumerate((0.35, 0.75, 2.35)):
        make_box(f"Ext_SidingSeam_{si}", (0.0, wallout + 0.052, sz),
                 (ROOM_W + 0.4, 0.006, 0.02), HENDERSON_SIDING_SH)
    make_box("Ext_WinTrimHead", (0.0, wallout + 0.06, WIN_HEAD + 0.06),
             (WIN_W + 0.24, 0.05, 0.10), HENDERSON_TRIM)
    make_box("Ext_WinTrimSill", (0.0, wallout + 0.06, WIN_SILL - 0.05),
             (WIN_W + 0.24, 0.05, 0.09), HENDERSON_TRIM)
    # Ground strata: lawn / sidewalk / curb / street / far lawn
    make_box("Ext_Lawn", (0.0, 7.45, GRADE_Z - 0.05), (20.0, 3.7, 0.10), COL_LAWN_AUG)
    make_box("Ext_LawnBrown", (-2.2, 6.6, GRADE_Z + 0.002), (1.6, 1.1, 0.004),
             COL_LAWN_BROWN)               # August does what August does
    make_box("Ext_Sidewalk", (0.0, 9.45, GRADE_Z - 0.02), (20.0, 0.75, 0.10),
             COL_CONCRETE)
    make_box("Ext_Curb", (0.0, 9.88, GRADE_Z - 0.02), (20.0, 0.16, 0.14), COL_CONCRETE)
    make_box("Ext_Street", (0.0, 12.05, GRADE_Z - 0.07), (20.0, 4.2, 0.10), COL_ASPHALT)
    make_box("Ext_FarLawn", (0.0, 16.4, GRADE_Z - 0.05), (20.0, 4.5, 0.10), COL_LAWN_AUG)
    # The front walk (ch22: "He goes up the walk") + mailbox
    make_box("Ext_Walk", (-1.5, 7.45, GRADE_Z + 0.006), (0.95, 3.7, 0.012), COL_CONCRETE)
    make_cyl("Ext_MailPost", (-1.5, 9.25, GRADE_Z + 0.45), 0.035, 0.90,
             HENDERSON_WALNUT_DK)
    make_box("Ext_Mailbox", (-1.5, 9.25, GRADE_Z + 1.00), (0.18, 0.42, 0.20),
             (0.30, 0.34, 0.30, 1.0))
    # THE DOUBLE DRIVEWAY east of the walk — both vehicles home
    # (ch20_prints:36): Eileen's maroon sedan west bay, Jim's
    # steel-blue pickup east bay, both nosed in toward the house.
    make_box("Ext_Driveway", (2.95, 7.85, GRADE_Z + 0.006), (4.5, 4.5, 0.012),
             COL_CONCRETE)
    # Eileen's sedan
    sx0, sy0 = 1.85, 7.8
    for wi, (wx, wy2) in enumerate([(-0.68, -1.30), (0.68, -1.30), (-0.68, 1.30),
                                    (0.68, 1.30)]):
        make_cyl(f"Sedan_Wheel_{wi}", (sx0 + wx, sy0 + wy2, GRADE_Z + 0.28), 0.26, 0.18,
                 (0.13, 0.13, 0.14, 1.0), axis='X', segments=10)
    make_box("Sedan_Body", (sx0, sy0, GRADE_Z + 0.52), (1.60, 4.10, 0.44),
             COL_SEDAN_MAROON)
    make_box("Sedan_Cabin", (sx0, sy0 + 0.10, GRADE_Z + 0.93), (1.45, 2.00, 0.38),
             COL_NIGHT_PANE)
    make_box("Sedan_Roof", (sx0, sy0 + 0.10, GRADE_Z + 1.135), (1.50, 2.05, 0.05),
             COL_SEDAN_MAROON)
    make_box("Sedan_PlateRear", (sx0, sy0 + 2.06, GRADE_Z + 0.48), (0.30, 0.015, 0.10),
             P.PAPER)
    # Jim's pickup — the truck that drives back from the Foxhole
    # after the third song (ch20_prints)
    tx0, ty0 = 4.05, 7.9
    for wi, (wx, wy2) in enumerate([(-0.74, -1.55), (0.74, -1.55), (-0.74, 1.55),
                                    (0.74, 1.55)]):
        make_cyl(f"Truck_Wheel_{wi}", (tx0 + wx, ty0 + wy2, GRADE_Z + 0.32), 0.30, 0.20,
                 (0.13, 0.13, 0.14, 1.0), axis='X', segments=10)
    make_box("Truck_Body", (tx0, ty0, GRADE_Z + 0.62), (1.72, 4.90, 0.48), COL_TRUCK)
    make_box("Truck_Cab", (tx0, ty0 - 1.15, GRADE_Z + 1.10), (1.58, 1.60, 0.50),
             COL_TRUCK)
    make_box("Truck_CabGlass", (tx0, ty0 - 1.15, GRADE_Z + 1.12), (1.46, 1.48, 0.34),
             COL_NIGHT_PANE)
    make_box("Truck_CabRoof", (tx0, ty0 - 1.15, GRADE_Z + 1.38), (1.60, 1.64, 0.06),
             COL_TRUCK)
    # Open bed: floor + three walls + tailgate (north/rear end)
    make_box("Truck_BedFloor", (tx0, ty0 + 1.05, GRADE_Z + 0.88), (1.56, 2.30, 0.04),
             COL_TRUCK_DK)
    for sgn in (-1, +1):
        make_box(f"Truck_BedWall_{sgn:+d}", (tx0 + sgn * 0.80, ty0 + 1.05,
                 GRADE_Z + 1.06), (0.06, 2.30, 0.32), COL_TRUCK)
    make_box("Truck_Tailgate", (tx0, ty0 + 2.23, GRADE_Z + 1.06), (1.56, 0.06, 0.32),
             COL_TRUCK)
    make_box("Truck_PlateRear", (tx0, ty0 + 2.27, GRADE_Z + 0.70), (0.30, 0.015, 0.10),
             P.PAPER)
    # THE MAGNOLIA — front lawn, west of the walk. Glossy dark
    # canopy, a few late creamy blooms (the street's namesake).
    make_cyl("Magnolia_Trunk", (-3.2, 8.1, GRADE_Z + 1.2), 0.14, 2.40, COL_TRUNK)
    for ci, (cr, cz) in enumerate([(1.55, 2.30), (1.20, 3.15), (0.70, 3.85)]):
        make_cyl(f"Magnolia_Canopy_{ci}", (-3.2, 8.1, GRADE_Z + cz), cr, 0.80,
                 COL_MAGNOLIA_LEAF if ci % 2 == 0 else COL_MAGNOLIA_LEAF_2, segments=10)
    for bi, (bx, by, bz) in enumerate([(-2.1, 7.6, 2.65), (-3.9, 8.5, 3.30),
                                       (-2.7, 8.9, 3.85)]):
        make_cyl(f"Magnolia_Bloom_{bi}", (bx, by, GRADE_Z + bz), 0.09, 0.08,
                 COL_MAGNOLIA_BLOOM, segments=8)
    # Across the street: tract massings, dark, one pane lit
    gx, gy = 1.2, 17.0
    make_box("Far_Body_A", (gx, gy, GRADE_Z + 1.55), (7.2, 4.5, 3.10),
             (0.68, 0.64, 0.56, 1.0))
    make_box("Far_Roof_A", (gx, gy, GRADE_Z + 3.32), (7.8, 5.1, 0.50), HENDERSON_ROOF)
    make_box("Far_Window_A0", (gx - 1.8, gy - 2.28, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_NIGHT_PANE)
    make_box("Far_Window_A1", (gx + 1.4, gy - 2.28, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_WINDOW_LIT)               # somebody else still up
    make_box("Far_Body_B", (-7.6, 16.6, GRADE_Z + 1.50), (6.4, 4.8, 3.00),
             (0.60, 0.58, 0.54, 1.0))
    make_box("Far_Roof_B", (-7.6, 16.6, GRADE_Z + 3.24), (7.0, 5.4, 0.48), HENDERSON_ROOF)
    make_box("Far_Window_B0", (-6.6, 14.2, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_NIGHT_PANE)
    make_cyl("Far_PorchLight_A", (gx - 2.9, gy - 2.32, GRADE_Z + 1.68), 0.055, 0.12,
             COL_PORCHBULB, segments=10)


def main():
    clear_scene()
    build_shell()
    build_window()
    build_counter_run()
    build_fridge()
    build_table_zone()
    build_east_wall()
    build_west_wall()
    build_ceiling_fixtures()
    build_exterior_front()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/henderson_kitchen.glb"))
    print(f"\n[build_henderson_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
