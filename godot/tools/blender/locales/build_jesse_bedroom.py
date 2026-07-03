"""Jesse's Bedroom — upstairs at the Henderson house on Magnolia,
Harmony Creek / New Auburn, TX — vol6 hero locale (5 VN bg refs:
vol6_ch3_jesse_bedroom, vol6_ch6_jesse_bedroom "Blowback",
vol6_ch20_bridge "Substation Nine", vol6_ch20_prints close,
vol6_ch23_sleep).

Jesse Henderson (20, Telecaster, frontman of SUBURBAN BLIGHT, the
Pit Stop, the Civic) — the SECOND room of the Henderson house after
build_henderson_kitchen.py. Same house, same shared-palette block
(byte-identical, verify with md5). Canon baked in:

  · THE FOUR-TWELVE MOMENT (vol6_ch20_bridge:32 — "this afternoon
    at four-twelve PM in his bedroom with the unplugged Telecaster
    in his lap"; music_catalog vol6_fourth_chord: "a suspended
    fourth chord found at four-twelve in Jesse's bedroom, the
    kitchen light still on at ten thirty-eight"). The kitchen froze
    its wall clock at 10:38; THIS room's alarm clock holds 4:12 —
    the two rooms tied by their clocks, per the kitchen docstring's
    adjudication.
  · vol6_ch3 / ch20_bridge — THE TELECASTER: butterscotch, the 1994
    Whitfield pair (music_strata.md — Sammy Whitfield's; Sam Miller
    owns the twin). On its A-stand (ch6: "He gets the Telecaster
    from its stand") — same geometry vocabulary and butterscotch
    tint as build_foxhole_stage.py, where the SAME guitar stands on
    stage on gig night. Its CASE on the carpet (ch3: "He puts the
    Telecaster back in its case").
  · vol6_ch6 — THE PRACTICE AMP ("He plugs into the amp. He turns
    the amp on, just to the practice setting"). Small combo against
    the east wall — the amp that rides in the Civic's trunk to the
    Foxhole (build_foxhole_stage). Cable coiled on top, UNPLUGGED:
    ch3 and the four-twelve tableau both play the Tele unplugged.
  · vol6_ch3 — he sits ON THE FLOOR, back against the bed, guitar
    in his lap: a worn carpet patch along the bed's east side. His
    bedroom door is CLOSED (ch3: "He looks up at his bedroom door.
    It is closed.") — closed leaf + infills per the Sam/Maya
    bedroom pattern.
  · vol6_ch6 — the phone FACE-DOWN on the bed ("He puts the phone
    face-down on the bed"); he lies on top of the made bed staring
    at the ceiling — flat drywall, spread pulled square then
    lain-on.
  · vol6_ch20_prints — THE SMALL SPIRAL NOTEBOOK with the bridge
    lyric "on Jesse's nightstand, in his own handwriting" — its
    canon resting place; the nightstand LAMP he turns off; the
    cicadas through the window.
  · vol6_ch23_sleep — THE SECOND NOTEBOOK, "the one he uses for
    general song-writing, the one he has been using since 2023,"
    open on the desk with a single underlined line (the next song —
    his mother and the piano). Desk + a Henderson walnut ladder-back
    chair (the shared _henderson_chair — one house, one chair
    catalog, one carried upstairs).
  · Kitchen key-rack canon (build_henderson_kitchen build_east_wall:
    "the Civic's is out with Jesse most nights") — the Civic keys
    live on JESSE'S DRESSER, with his wallet and two guitar picks
    (one on band-orange stock — Em's sticker-run color).
  · EXTERIOR (second floor, window over the BACK YARD — the kitchen
    window owns the front drive; one house, one garden, per the
    kitchen docstring's sync note): THE GARDEN SHED and THE
    TERRA-COTTA POT BEHIND IT (vol6_ch20_prints — Jim's contact
    print of "the pot behind the garden shed... the pot is the
    whole picture"). The pot is placed north of the shed, OCCLUDED
    from this window by the shed's own roofline — present,
    occluded, never announced (the print is the only way anyone
    sees it; that is the point of the print). Eileen-and-Jim's
    garden rows beside it (the "garden series" Jim prints), the
    live oak the cicadas are loud in (ch20_prints / ch23), the
    weathered privacy fence, the back patio + door below, and the
    rear neighbor's tract massing beyond — dark panes, ONE faintly
    lit (the same night register as the kitchen's street view).

Canon-NEGATIVES honored (what Jesse's room does NOT have):
  · NO band gear beyond his own — practice is in the GARAGE
    (suburban_blight.md; vol6_ch20_bridge: Carl's snare, Nate's
    bass, Em's mic all arrive AT THE GARAGE). No drums, no bass,
    no mic stand, no keys.
  · NO Suburban Blight stickers — the mid-August sticker locations
    are enumerated (suburban_blight.md) and Jesse's room is not
    one of them; the bedroom-window-frame sticker is SAM'S window.
  · NO Foxhole flyer — the flyer is magneted to the KITCHEN fridge
    (build_henderson_kitchen, ch20_prints/ch22); not duplicated.
  · NO Graflex cameras — the study's (glitch_report.md:303), and
    the stickered one is Mr. Henderson's, not Jesse's.
  · NO posters / store wall art — the scaffold's three faded
    posters were codegen vocabulary; no bedroom scene hangs
    anything on Jesse's walls.
  · NO laptop / corkboard / zine gear / license-plate notebook —
    Jesse's channel is his phone (ch3/ch6 text threads); the
    corkboard is Sam's, the studio is Maya's.
  · NO piano — the piano goes in the DINING ROOM (ch23_sleep);
    here it exists only as the underlined line in the notebook.
  · NO commercial fluorescents / drop grid / crown molding — the
    scaffold's tubes and crown were store/codegen vocabulary; a
    1998 house room gets one flush-mount dome (the light he turns
    out, ch23) + the nightstand lamp (ch20_prints).

Shell footprint kept from the scaffold (4 x 4.5 m, CEIL 2.6, door
gap in the south wall x -1..+1 — the Background3D camera preset
(0, 2.30, +0.5 / yaw 180 / fov 60) is tuned to it; closed leaf +
infills). Window is a REAL OPENING with frame + sash + muntins, no
glass (playbook no-transparency rule).

HENDERSON HOUSE shared block below is byte-identical with
build_henderson_kitchen.py (⚠ KEEP IN SYNC — verify with md5).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_wall, make_ceiling, make_door_hinges
from _props.safety import make_smoke_detector, make_hvac_vent

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 4.0; ROOM_D = 4.5; CEIL = 2.6

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

# ── Jesse's-room-only palette ────────────────────────────────────
COL_SPREAD      = (0.36, 0.40, 0.48, 1.0)   # slate blue-grey spread
COL_SPREAD_SH   = (0.30, 0.34, 0.41, 1.0)   # the lain-on shading (ch6)
COL_LINEN       = (0.90, 0.88, 0.82, 1.0)
COL_MATTRESS    = (0.94, 0.92, 0.87, 1.0)
COL_CHARCOAL    = (0.16, 0.15, 0.16, 1.0)   # phone / clock body
COL_LED_RED     = (0.86, 0.16, 0.12, 1.0)   # alarm-clock segments
COL_TELE_BUTTER = (0.85, 0.62, 0.30, 1.0)   # butterscotch — matches
                                            # build_foxhole_stage's Tele
COL_TELE_GUARD  = (0.90, 0.86, 0.74, 1.0)   # cream pickguard
COL_AMP_GRILLE  = (0.24, 0.22, 0.20, 1.0)
COL_STEEL_DK    = (0.44, 0.46, 0.48, 1.0)
COL_WALLET      = (0.34, 0.24, 0.16, 1.0)
COL_BLIND       = (0.90, 0.88, 0.82, 1.0)   # rolled vinyl blind
COL_DOOR_PANEL  = (0.86, 0.85, 0.80, 1.0)   # inset-panel shading
COL_FENCE       = (0.58, 0.50, 0.38, 1.0)   # weathered pine privacy
COL_FENCE_SEAM  = (0.42, 0.35, 0.26, 1.0)
COL_SHED_SIDE   = (0.55, 0.52, 0.44, 1.0)   # sun-greyed shed board
COL_SHED_SIDE_SH = (0.44, 0.41, 0.34, 1.0)
COL_TERRACOTTA  = (0.72, 0.40, 0.26, 1.0)   # THE pot (ch20_prints)
COL_TERRACOTTA_DK = (0.58, 0.31, 0.20, 1.0)
COL_SOIL        = (0.30, 0.24, 0.18, 1.0)   # the garden rows
COL_GARDEN_ROW  = (0.30, 0.42, 0.22, 1.0)
COL_OAK_CANOPY  = (0.27, 0.38, 0.22, 1.0)   # the cicada oak
COL_OAK_CANOPY_2 = (0.23, 0.33, 0.19, 1.0)

PAL_WALL = {"wall": HENDERSON_INT_WALL, "baseboard": HENDERSON_BASEBOARD}

# Window opening in the north wall (real opening, no glass)
WIN_W = 1.30                  # opening x -0.65..+0.65
WIN_SILL = 0.95
WIN_HEAD = 2.15
GRADE_Z = -3.20               # back-yard grade (second-floor room)


# ═════════════════════════════════════════════════════════════════
# SHELL — wall-to-wall carpet (the shared block's upstairs COL_
# CARPET), Eileen's butter-yellow walls (one house, one paint job),
# flat white drywall ceiling (house — no drop grid, no stains, no
# crown). South door gap kept with infills for the closed leaf.
# Worn carpet: the floor spot where he sits with his back against
# the bed (ch3) + the door-traffic patch.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_box("Floor_Carpet", (0.0, ROOM_D / 2.0, -0.05),
             (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), COL_CARPET)
    make_box("Floor_Worn_BedSit", (-0.58, 3.10, 0.0008), (0.52, 0.95, 0.0016),
             COL_CARPET_SH)             # ch3 — back against the bed, guitar in lap
    make_box("Floor_Worn_Door", (0.0, 0.55, 0.0008), (0.85, 0.70, 0.0016),
             COL_CARPET_SH)
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall — REAL window opening x -0.65..+0.65
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20     # 1.55
    seg_cx = WIN_W / 2.0 + seg_len / 2.0              # 1.425
    make_wall("Wall_N_W", (-seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_SillFill", (0.0, ROOM_D, WIN_SILL / 2.0), (WIN_W, 0.20, WIN_SILL),
             HENDERSON_INT_WALL)
    make_box("Wall_N_HeadFill", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.20, CEIL - WIN_HEAD), HENDERSON_INT_WALL)
    # South wall — scaffold door gap x -1..+1 kept (camera preset)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             HENDERSON_INT_WALL)
    # Gap infill either side of the 0.90 m door leaf
    for nm, fx in [("Wall_S_FillW", -0.725), ("Wall_S_FillE", +0.725)]:
        make_box(nm, (fx, 0.0, 1.15), (0.55, 0.20, 2.30), HENDERSON_INT_WALL)
    # Flat white drywall ceiling — the one he stares at (ch6)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_CEIL_WHITE},
                 with_grid=False, with_stains=False)


# ═════════════════════════════════════════════════════════════════
# DOOR — CLOSED white six-panel leaf in the south gap (ch3: "He
# looks up at his bedroom door. It is closed."). Behind it: the
# hall, the stairs, the dishwasher one floor down, the darkroom two
# floors below (ch3) — all offstage.
# ═════════════════════════════════════════════════════════════════
def build_door():
    make_box("Door_Leaf", (0.0, 0.03, 1.03), (0.90, 0.05, 2.06), HENDERSON_TRIM)
    for ci, px in enumerate((-0.21, +0.21)):
        for ri, pz in enumerate((0.48, 1.06, 1.62)):
            make_box(f"Door_Panel_{ci}_{ri}", (px, 0.062, pz), (0.30, 0.012, 0.44),
                     COL_DOOR_PANEL)
    make_cyl("Door_Knob", (0.35, 0.075, 0.98), 0.028, 0.045, COL_BRASS, axis='Y')
    make_door_hinges("Door_Hinge", edge_x=-0.43, edge_y=0.06,
                     edge_z_centers=[0.35, 1.03, 1.75], axis='X')
    for sgn in (-1, +1):
        make_box(f"Door_Casing_{sgn:+d}", (sgn * 0.50, 0.11, 1.06), (0.09, 0.05, 2.12),
                 HENDERSON_TRIM)
    make_box("Door_CasingHead", (0.0, 0.11, 2.16), (1.09, 0.05, 0.10), HENDERSON_TRIM)


# ═════════════════════════════════════════════════════════════════
# WINDOW — north wall over the back yard: REAL OPENING, painted
# double-hung frame, meeting rail + upper muntins, casing, stool,
# apron — the same joinery as the kitchen's front window, one floor
# up (one house, one window catalog). A rolled vinyl blind at the
# head, no curtains — the cicadas come through loud (ch20_prints /
# ch23: "The cicadas, through the window, are loud").
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D
    make_box("Win_FrameT", (0.0, wy, WIN_HEAD - 0.03), (WIN_W, 0.14, 0.06),
             HENDERSON_TRIM)
    make_box("Win_FrameB", (0.0, wy, WIN_SILL + 0.03), (WIN_W, 0.14, 0.06),
             HENDERSON_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Jamb_{sgn:+d}", (sgn * (WIN_W / 2.0 - 0.03), wy, 1.55),
                 (0.06, 0.14, 1.20), HENDERSON_TRIM)
    make_box("Win_MeetingRail", (0.0, wy, 1.56), (WIN_W - 0.08, 0.10, 0.06),
             HENDERSON_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Muntin_{sgn:+d}", (sgn * 0.22, wy - 0.02, 1.86),
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
    # Rolled blind — up (the room listens to the yard at night)
    make_cyl("Blind_Roll", (0.0, wy - 0.115, WIN_HEAD - 0.10), 0.032, WIN_W - 0.10,
             COL_BLIND, axis='X', segments=10)
    make_cyl("Blind_Cord", (0.56, wy - 0.115, WIN_HEAD - 0.32), 0.003, 0.38,
             (0.80, 0.78, 0.72, 1.0), segments=6)


# ═════════════════════════════════════════════════════════════════
# BED ZONE — walnut frame on the west wall, head at the window end
# (the cicada end). Made, spread pulled square, then lain-on all
# volume long (ch6: "Jesse is on his bed. He has been on his bed
# since eleven"). The phone FACE-DOWN on the spread (ch6). Along
# the east rail: the floor spot he sits at with the Telecaster in
# his lap (ch3, ch20_bridge) — the worn patch is in build_shell.
# ═════════════════════════════════════════════════════════════════
def build_bed_zone():
    bx = -1.38                     # frame x -1.90..-0.86
    y0, y1 = 2.35, 4.30            # foot..head (head at window end)
    by = (y0 + y1) / 2.0
    make_box("Bed_Rail", (bx, by, 0.32), (1.04, 1.95, 0.12), HENDERSON_WALNUT)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Bed_Leg_{li}", (bx + sx * 0.47, by + sy * 0.92, 0.15), 0.030, 0.30,
                 HENDERSON_WALNUT_DK)
    make_box("Bed_Headboard", (bx, y1 - 0.02, 0.62), (1.04, 0.06, 0.70),
             HENDERSON_WALNUT)
    make_box("Bed_HeadboardCap", (bx, y1 - 0.02, 0.99), (1.08, 0.09, 0.05),
             HENDERSON_WALNUT_DK)
    make_box("Bed_BoxSpring", (bx, by, 0.425), (1.00, 1.89, 0.13), COL_LINEN)
    make_box("Bed_Mattress", (bx, by, 0.56), (1.00, 1.89, 0.14), COL_MATTRESS)
    # Spread — slate, pulled square, drapes east + south, lain-on
    make_box("Bedspread_Top", (bx, by - 0.09, 0.655), (1.02, 1.71, 0.05), COL_SPREAD)
    make_box("Bedspread_DrapeE", (bx + 0.515, by - 0.09, 0.50), (0.025, 1.71, 0.28),
             COL_SPREAD)
    make_box("Bedspread_DrapeS", (bx, y0 + 0.03, 0.50), (1.02, 0.025, 0.28), COL_SPREAD)
    make_box("Bedspread_LainOn", (bx + 0.06, 3.35, 0.681), (0.62, 1.10, 0.006),
             COL_SPREAD_SH)                    # ch6 — on the bed since eleven
    make_box("Bed_Pillow", (bx, y1 - 0.24, 0.72), (0.84, 0.34, 0.11), COL_LINEN)
    # THE PHONE — face-down on the bed (ch6). Face-down: shell up,
    # no screen modeled.
    make_box("Phone_Slab", (bx + 0.22, 3.02, 0.688), (0.072, 0.148, 0.012),
             COL_CHARCOAL)


# ═════════════════════════════════════════════════════════════════
# NIGHTSTAND — east of the bed head, under the window's west edge.
# On top: the lamp he turns off (ch20_prints), THE SMALL SPIRAL
# NOTEBOOK with the bridge lyric ("on Jesse's nightstand, in his
# own handwriting... waiting for tomorrow" — ch20_prints), a pen,
# and THE ALARM CLOCK HOLDING 4:12 — the found-chord minute
# (music_catalog vol6_fourth_chord; the kitchen's wall clock holds
# the other half of the pair at 10:38).
# ═════════════════════════════════════════════════════════════════
def build_nightstand():
    nx, ny = -0.52, 4.14
    make_box("Nightstand_Body", (nx, ny, 0.26), (0.40, 0.38, 0.52), HENDERSON_WALNUT)
    make_box("Nightstand_Top", (nx, ny, 0.535), (0.44, 0.42, 0.03),
             HENDERSON_WALNUT_DK)
    make_box("Nightstand_Drawer", (nx, ny - 0.195, 0.40), (0.32, 0.015, 0.14),
             HENDERSON_WALNUT_DK)
    make_cyl("Nightstand_Knob", (nx, ny - 0.21, 0.40), 0.013, 0.03, COL_BRASS, axis='Y')
    # The lamp (ch20_prints: "He turns off the lamp." — glow disc is
    # for the scene's practical; mood is scene-side)
    make_cyl("BedLamp_Base", (nx - 0.10, ny + 0.08, 0.565), 0.062, 0.025,
             HENDERSON_WALNUT_DK)
    make_cyl("BedLamp_Stem", (nx - 0.10, ny + 0.08, 0.70), 0.012, 0.26, COL_BRASS)
    make_cyl("BedLamp_Shade", (nx - 0.10, ny + 0.08, 0.885), 0.090, 0.13, COL_LINEN,
             segments=12)
    make_cyl("BedLamp_Glow", (nx - 0.10, ny + 0.08, 0.815), 0.038, 0.02, COL_LAMP_GLOW)
    # THE ALARM CLOCK — 4:12 (the suspended fourth chord's minute).
    # Charcoal body, red LED segments: 4 : 1 2.
    make_box("AlarmClock_Body", (nx + 0.12, ny + 0.10, 0.588), (0.155, 0.085, 0.075),
             COL_CHARCOAL)
    make_box("AlarmClock_Face", (nx + 0.12, ny + 0.055, 0.592), (0.125, 0.006, 0.048),
             (0.08, 0.08, 0.09, 1.0))
    make_box("AlarmClock_Digit_H", (nx + 0.078, ny + 0.050, 0.592),
             (0.022, 0.004, 0.034), COL_LED_RED)         # 4
    make_box("AlarmClock_Colon", (nx + 0.104, ny + 0.050, 0.592),
             (0.006, 0.004, 0.022), COL_LED_RED)         # :
    make_box("AlarmClock_Digit_M1", (nx + 0.126, ny + 0.050, 0.592),
             (0.010, 0.004, 0.034), COL_LED_RED)         # 1
    make_box("AlarmClock_Digit_M2", (nx + 0.152, ny + 0.050, 0.592),
             (0.022, 0.004, 0.034), COL_LED_RED)         # 2
    # THE SPIRAL NOTEBOOK — small, cheap, the bridge page up
    # (ch20_bridge: carried in his back pocket since Wednesday;
    # ch20_prints: it ends the day here)
    make_box("SpiralNotebook", (nx + 0.05, ny - 0.09, 0.556), (0.082, 0.112, 0.012),
             P.PAPER)
    for wi in range(4):
        make_cyl(f"SpiralNotebook_Wire_{wi}", (nx + 0.022 + wi * 0.019, ny - 0.032,
                 0.560), 0.005, 0.012, P.METAL_STEEL, axis='Y', segments=6)
    for li in range(4):
        make_box(f"SpiralNotebook_Line_{li}", (nx + 0.05, ny - 0.075 - li * 0.018,
                 0.5635), (0.058, 0.004, 0.001), COL_INK)   # the eight lines, folded small
    make_cyl("Nightstand_Pen", (nx - 0.10, ny - 0.11, 0.552), 0.0045, 0.125, COL_INK,
             axis='X', segments=6)


# ═════════════════════════════════════════════════════════════════
# GUITAR RIG — east wall. THE TELECASTER on its A-stand (ch6 — the
# butterscotch 1994 Whitfield twin, music_strata.md; same geometry
# vocabulary as build_foxhole_stage, where this guitar stands on
# gig night). THE PRACTICE AMP (ch6: "just to the practice
# setting") with the cable COILED on top — the Tele is unplugged in
# the four-twelve tableau (ch3 / ch20_bridge). THE CASE flat on the
# carpet by the bed foot (ch3: "He puts the Telecaster back in its
# case").
# ═════════════════════════════════════════════════════════════════
def build_guitar_rig():
    # The amp — small combo, front (grille) facing west into the room
    ax, ay = 1.58, 1.50
    make_box("Amp_Body", (ax, ay, 0.21), (0.48, 0.34, 0.42), P.METAL_BLACK)
    make_box("Amp_Grille", (ax - 0.245, ay, 0.17), (0.012, 0.40, 0.26), COL_AMP_GRILLE)
    make_box("Amp_Panel", (ax - 0.245, ay, 0.36), (0.012, 0.40, 0.06), COL_STEEL_DK)
    for ki in range(3):
        make_cyl(f"Amp_Knob_{ki}", (ax - 0.255, ay - 0.10 + ki * 0.10, 0.36),
                 0.014, 0.02, P.METAL_BLACK, axis='X', segments=8)
    make_box("Amp_Handle", (ax, ay, 0.435), (0.16, 0.05, 0.03), COL_CHARCOAL)
    # The cable, coiled on the amp top — UNPLUGGED (ch3/ch20_bridge)
    make_cyl("Amp_CableCoil", (ax + 0.10, ay + 0.02, 0.435), 0.075, 0.030,
             COL_CHARCOAL, segments=12)
    make_cyl("Amp_CableCoilTop", (ax + 0.10, ay + 0.02, 0.457), 0.052, 0.018,
             (0.11, 0.10, 0.11, 1.0), segments=10)
    # THE TELECASTER on its A-stand — body faces west into the room
    tx, ty = 1.52, 2.35
    make_box("Tele_Body", (tx, ty, 0.46), (0.06, 0.30, 0.40), COL_TELE_BUTTER)
    make_box("Tele_Pickguard", (tx - 0.035, ty - 0.05, 0.44), (0.005, 0.13, 0.20),
             COL_TELE_GUARD)
    make_box("Tele_Neck", (tx, ty, 0.92), (0.04, 0.05, 0.52), HENDERSON_WALNUT)
    make_box("Tele_Head", (tx, ty, 1.24), (0.03, 0.08, 0.13), HENDERSON_WALNUT)
    for si, sy in enumerate([ty - 0.10, ty + 0.10]):
        make_cyl(f"Tele_StandLeg_{si}", (tx + 0.07, sy, 0.17), 0.010, 0.34,
                 P.METAL_BLACK, segments=6)
    # THE CASE — closed, flat on the carpet near the bed foot (ch3)
    cx, cy = -0.55, 1.30
    make_box("Case_Shell", (cx, cy, 0.065), (0.42, 1.20, 0.13), P.METAL_BLACK)
    make_box("Case_LidSeam", (cx, cy, 0.075), (0.425, 1.205, 0.008), COL_CHARCOAL)
    for li2, ly in enumerate((cy - 0.42, cy, cy + 0.42)):
        make_box(f"Case_Latch_{li2}", (cx - 0.215, ly, 0.075), (0.015, 0.05, 0.04),
                 P.METAL_STEEL)
    make_box("Case_Handle", (cx - 0.235, cy, 0.10), (0.02, 0.16, 0.03), COL_CHARCOAL)


# ═════════════════════════════════════════════════════════════════
# DESK ZONE — east wall, north end (the window light). THE 2023
# SONGWRITING NOTEBOOK open on it (ch23_sleep: "a different
# notebook open beside it — the one he uses for general
# song-writing, the one he has been using since 2023"), with the
# single underlined line (the next song: his mother and the piano).
# The chair is a Henderson walnut ladder-back — the shared
# _henderson_chair the kitchen table seats, one carried upstairs.
# ═════════════════════════════════════════════════════════════════
def build_desk_zone():
    dx = 1.60
    y0, y1 = 2.98, 4.13
    dy = (y0 + y1) / 2.0
    make_box("Desk_Top", (dx, dy, 0.735), (0.58, 1.15, 0.035), HENDERSON_WALNUT)
    make_box("Desk_Apron", (dx, dy, 0.685), (0.48, 1.03, 0.06), HENDERSON_WALNUT)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Desk_Leg_{li}", (dx + sx * 0.25, dy + sy * 0.52, 0.345),
                 (0.045, 0.045, 0.69), HENDERSON_WALNUT_DK)
    _henderson_chair("DeskChair", 1.10, dy, 'E')   # the borrowed kitchen chair
    # THE 2023 NOTEBOOK — open, two pages. Left page: three summers
    # of lines. Right page: ONE line, underlined (ch23).
    make_box("Notebook23_PageL", (dx - 0.09, dy + 0.05, 0.754), (0.150, 0.210, 0.006),
             P.PAPER_AGED)
    make_box("Notebook23_PageR", (dx + 0.075, dy + 0.05, 0.754), (0.150, 0.210, 0.006),
             P.PAPER)
    make_box("Notebook23_Gutter", (dx - 0.008, dy + 0.05, 0.7565),
             (0.014, 0.210, 0.003), COL_CHARCOAL)
    for ai in range(5):
        make_box(f"Notebook23_LineL_{ai}", (dx - 0.09, dy + 0.13 - ai * 0.032, 0.758),
                 (0.105, 0.006, 0.001), COL_INK)
    make_box("Notebook23_TheLine", (dx + 0.075, dy + 0.10, 0.758), (0.105, 0.007, 0.001),
             COL_INK)                              # the mother-and-piano line
    make_box("Notebook23_Underline", (dx + 0.075, dy + 0.085, 0.758),
             (0.105, 0.004, 0.001), COL_INK)       # "He underlines it."
    make_cyl("Desk_Pencil", (dx + 0.02, dy - 0.16, 0.756), 0.0042, 0.13,
             (0.82, 0.62, 0.22, 1.0), axis='Y', segments=6)


# ═════════════════════════════════════════════════════════════════
# DRESSER — west wall, south of the bed. Walnut three-drawer. On
# top: THE CIVIC KEYS (the kitchen key rack's third hook is empty —
# "the Civic's is out with Jesse most nights",
# build_henderson_kitchen), his wallet, and two guitar picks — one
# on the band's orange sticker stock (Em's Kinko's runs,
# suburban_blight.md).
# ═════════════════════════════════════════════════════════════════
def build_dresser():
    fx, fy = -1.63, 1.20
    make_box("Dresser_Body", (fx, fy, 0.525), (0.50, 0.90, 1.05), HENDERSON_WALNUT)
    make_box("Dresser_Top", (fx + 0.01, fy, 1.065), (0.54, 0.94, 0.03),
             HENDERSON_WALNUT_DK)
    make_box("Dresser_Kick", (fx + 0.02, fy, 0.04), (0.48, 0.86, 0.08),
             HENDERSON_WALNUT_DK)
    for ri, rz in enumerate((0.30, 0.60, 0.90)):
        make_box(f"Dresser_Drawer_{ri}", (fx + 0.26, fy, rz), (0.02, 0.80, 0.22),
                 HENDERSON_WALNUT)
        for ki, sgn in enumerate((-1, +1)):
            make_cyl(f"Dresser_Knob_{ri}_{ki}", (fx + 0.275, fy + sgn * 0.22, rz),
                     0.013, 0.03, COL_BRASS, axis='X')
    # The Civic keys — ring + two keys
    make_cyl("Civic_KeyRing", (fx + 0.10, fy - 0.24, 1.084), 0.020, 0.006, COL_BRASS,
             axis='Z', segments=10)
    make_box("Civic_Key_0", (fx + 0.13, fy - 0.26, 1.084), (0.045, 0.014, 0.005),
             P.METAL_STEEL)
    make_box("Civic_Key_1", (fx + 0.125, fy - 0.215, 1.084), (0.040, 0.013, 0.005),
             COL_STEEL_DK)
    # Wallet + the two picks
    make_box("Wallet", (fx - 0.06, fy + 0.20, 1.092), (0.105, 0.085, 0.024), COL_WALLET)
    make_box("Pick_Orange", (fx + 0.04, fy + 0.05, 1.082), (0.022, 0.020, 0.003),
             COL_BLIGHT_ORANGE)
    make_box("Pick_Cream", (fx + 0.09, fy + 0.08, 1.082), (0.022, 0.020, 0.003),
             COL_TELE_GUARD)


# ═════════════════════════════════════════════════════════════════
# CEILING — one flush-mount dome (the light he turns out,
# ch23_sleep: "He turns out the light."), smoke detector, HVAC
# register. House hardware only — the scaffold's two commercial
# fluorescent tubes were store vocabulary and are gone.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_fixtures():
    lx, ly = 0.0, 2.30
    make_cyl("CeilLight_Plate", (lx, ly, CEIL - 0.012), 0.105, 0.024, HENDERSON_TRIM,
             segments=12)
    make_cyl("CeilLight_DomeUp", (lx, ly, CEIL - 0.055), 0.115, 0.065,
             (0.95, 0.93, 0.86, 1.0), segments=12)
    make_cyl("CeilLight_DomeTip", (lx, ly, CEIL - 0.105), 0.075, 0.038,
             (0.95, 0.93, 0.86, 1.0), segments=12)
    make_cyl("CeilLight_Glow", (lx, ly, CEIL - 0.128), 0.042, 0.012, COL_LAMP_GLOW,
             segments=10)                 # scene Light3D matches from the .tscn
    make_smoke_detector("Smoke", (-0.9, 1.1, CEIL))
    make_hvac_vent("HVAC", (0.9, 0.7, CEIL), width=0.50, depth=0.30)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · THE BACK YARD (through the window) — the other half of
# the Henderson garden, synced with build_henderson_kitchen (its
# window owns the front drive; this one owns the yard Jim
# photographs). THE GARDEN SHED with THE TERRA-COTTA POT BEHIND IT
# (ch20_prints — "the pot behind the garden shed... the pot is the
# whole picture"): the pot sits north of the shed where this window
# CANNOT see it past the shed's roofline — present, occluded, never
# announced; Jim's print is the only witness. The garden rows (the
# "garden series"), the live oak the cicadas are loud in
# (ch20_prints / ch23), the privacy fence, the patio + back door
# below, and the rear neighbors' tract bones — dark, one pane
# faintly lit (the same night register as the kitchen's view).
# ═════════════════════════════════════════════════════════════════
def build_exterior_back():
    wallout = ROOM_D + 0.10
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20
    seg_cx = WIN_W / 2.0 + seg_len / 2.0
    # Facade skins — full height (second floor: grade to eave), sage
    skin_h = CEIL - GRADE_Z                          # 5.8
    make_box("Ext_Skin_W", (-seg_cx, wallout + 0.02, (CEIL + GRADE_Z) / 2.0),
             (seg_len, 0.06, skin_h), HENDERSON_SIDING)
    make_box("Ext_Skin_E", (+seg_cx, wallout + 0.02, (CEIL + GRADE_Z) / 2.0),
             (seg_len, 0.06, skin_h), HENDERSON_SIDING)
    make_box("Ext_Skin_Sill", (0.0, wallout + 0.02, (WIN_SILL + GRADE_Z) / 2.0),
             (WIN_W, 0.06, WIN_SILL - GRADE_Z), HENDERSON_SIDING)
    make_box("Ext_Skin_Head", (0.0, wallout + 0.02, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.06, CEIL - WIN_HEAD), HENDERSON_SIDING)
    for si, sz in enumerate((-2.4, -1.2, 0.55, 2.35)):
        make_box(f"Ext_SidingSeam_{si}", (0.0, wallout + 0.052, sz),
                 (ROOM_W + 0.4, 0.006, 0.02), HENDERSON_SIDING_SH)
    make_box("Ext_WinTrimHead", (0.0, wallout + 0.06, WIN_HEAD + 0.06),
             (WIN_W + 0.24, 0.05, 0.10), HENDERSON_TRIM)
    make_box("Ext_WinTrimSill", (0.0, wallout + 0.06, WIN_SILL - 0.05),
             (WIN_W + 0.24, 0.05, 0.09), HENDERSON_TRIM)
    # First floor below: the back door + stoop + a dark utility pane
    make_box("Ext_BackDoor", (-0.9, wallout + 0.06, GRADE_Z + 1.02),
             (0.90, 0.05, 2.00), HENDERSON_TRIM)
    make_box("Ext_BackDoor_Pane", (-0.9, wallout + 0.08, GRADE_Z + 1.55),
             (0.40, 0.02, 0.50), COL_NIGHT_PANE)
    make_cyl("Ext_BackDoor_Knob", (-0.58, wallout + 0.09, GRADE_Z + 0.98),
             0.022, 0.04, COL_BRASS, axis='Y')
    make_box("Ext_Stoop", (-0.9, 5.05, GRADE_Z + 0.08), (1.30, 0.90, 0.16),
             COL_CONCRETE)
    make_box("Ext_UtilityWin", (1.1, wallout + 0.06, GRADE_Z + 1.60), (0.80, 0.05, 0.70),
             COL_NIGHT_PANE)
    make_box("Ext_UtilityWin_TrimT", (1.1, wallout + 0.07, GRADE_Z + 1.99),
             (0.94, 0.05, 0.08), HENDERSON_TRIM)
    make_box("Ext_UtilityWin_TrimB", (1.1, wallout + 0.07, GRADE_Z + 1.21),
             (0.94, 0.05, 0.08), HENDERSON_TRIM)
    make_cyl("Ext_PorchLight", (-1.5, wallout + 0.09, GRADE_Z + 1.90), 0.050, 0.11,
             COL_PORCHBULB, segments=10)   # the back-door bulb, warm
    # Patio + the yard
    make_box("Ext_Patio", (0.2, 5.85, GRADE_Z + 0.006), (3.40, 2.10, 0.012),
             COL_CONCRETE)
    make_box("Ext_Lawn", (0.0, 9.6, GRADE_Z - 0.05), (16.4, 7.6, 0.10), COL_LAWN_AUG)
    make_box("Ext_LawnBrown_0", (-1.6, 8.2, GRADE_Z + 0.002), (1.5, 1.0, 0.004),
             COL_LAWN_BROWN)               # August does what August does
    make_box("Ext_LawnBrown_1", (2.3, 7.4, GRADE_Z + 0.002), (1.1, 0.8, 0.004),
             COL_LAWN_BROWN)
    # THE GARDEN SHED — back east corner, greyed board, white trim,
    # shingle slab roof (one house: same trim + roof vocabulary)
    shx, shy = 2.7, 10.9
    make_box("Shed_Body", (shx, shy, GRADE_Z + 1.02), (2.00, 1.60, 2.04), COL_SHED_SIDE)
    for bi, bz in enumerate((0.45, 1.05, 1.65)):
        make_box(f"Shed_BoardSeam_{bi}", (shx, shy - 0.81, GRADE_Z + bz),
                 (1.96, 0.006, 0.02), COL_SHED_SIDE_SH)
    make_box("Shed_Door", (shx - 0.35, shy - 0.815, GRADE_Z + 0.85),
             (0.62, 0.03, 1.70), HENDERSON_TRIM)
    make_box("Shed_Door_Z", (shx - 0.35, shy - 0.835, GRADE_Z + 0.85),
             (0.06, 0.012, 1.60), COL_SHED_SIDE_SH)
    make_cyl("Shed_Hasp", (shx - 0.09, shy - 0.84, GRADE_Z + 0.90), 0.016, 0.02,
             P.METAL_STEEL, axis='Y', segments=8)
    make_box("Shed_Roof", (shx, shy, GRADE_Z + 2.14), (2.30, 1.90, 0.16),
             HENDERSON_ROOF)
    make_box("Shed_RoofRidge", (shx, shy, GRADE_Z + 2.26), (2.30, 0.60, 0.10),
             HENDERSON_ROOF)
    for ci2, csx in enumerate((-0.98, +0.98)):
        make_box(f"Shed_CornerTrim_{ci2}", (shx + csx, shy - 0.79, GRADE_Z + 1.02),
                 (0.06, 0.05, 2.00), HENDERSON_TRIM)
    # THE TERRA-COTTA POT — BEHIND the shed (north side). From this
    # window the shed's roofline occludes it; only Jim's contact
    # print sees it ("the pot is the whole picture", ch20_prints).
    make_cyl("TerraCotta_Pot", (2.85, 12.05, GRADE_Z + 0.15), 0.165, 0.30,
             COL_TERRACOTTA, segments=12)
    make_cyl("TerraCotta_Rim", (2.85, 12.05, GRADE_Z + 0.315), 0.180, 0.045,
             COL_TERRACOTTA, segments=12)
    make_cyl("TerraCotta_Soil", (2.85, 12.05, GRADE_Z + 0.345), 0.145, 0.015,
             COL_TERRACOTTA_DK, segments=10)
    # The garden — the rows Jim prints (the "garden series")
    make_box("Garden_Soil", (-0.4, 11.6, GRADE_Z + 0.015), (3.00, 1.60, 0.05), COL_SOIL)
    for ri2, ry in enumerate((11.15, 11.60, 12.05)):
        make_cyl(f"Garden_Row_{ri2}", (-0.4, ry, GRADE_Z + 0.10), 0.10, 2.70,
                 COL_GARDEN_ROW, axis='X', segments=8)
    for st, (stx, sty) in enumerate([(-1.35, 11.15), (0.45, 11.60)]):
        make_cyl(f"Garden_Stake_{st}", (stx, sty, GRADE_Z + 0.45), 0.015, 0.90,
                 COL_TRUNK, segments=6)
    # THE LIVE OAK — west corner, the cicada tree (ch20_prints/ch23)
    make_cyl("Oak_Trunk", (-3.4, 10.6, GRADE_Z + 1.35), 0.16, 2.70, COL_TRUNK)
    for ci3, (cr, cz) in enumerate([(1.70, 2.60), (1.30, 3.50), (0.75, 4.25)]):
        make_cyl(f"Oak_Canopy_{ci3}", (-3.4, 10.6, GRADE_Z + cz), cr, 0.85,
                 COL_OAK_CANOPY if ci3 % 2 == 0 else COL_OAK_CANOPY_2, segments=10)
    # Privacy fence — back run + side runs, weathered pine
    make_box("Fence_Back", (0.0, 13.4, GRADE_Z + 0.92), (16.4, 0.06, 1.84), COL_FENCE)
    make_box("Fence_Back_Rail", (0.0, 13.36, GRADE_Z + 1.62), (16.4, 0.05, 0.09),
             COL_FENCE_SEAM)
    for pi, px in enumerate((-6.9, -4.6, -2.3, 0.0, 2.3, 4.6, 6.9)):
        make_box(f"Fence_Post_{pi}", (px, 13.36, GRADE_Z + 0.95), (0.09, 0.09, 1.90),
                 COL_FENCE_SEAM)
    for sgn, snm in ((-1, "W"), (+1, "E")):
        make_box(f"Fence_Side_{snm}", (sgn * 8.2, 9.0, GRADE_Z + 0.92),
                 (0.06, 8.80, 1.84), COL_FENCE)
        make_box(f"Fence_Side_{snm}_Rail", (sgn * 8.16, 9.0, GRADE_Z + 1.62),
                 (0.05, 8.80, 0.09), COL_FENCE_SEAM)
    # Beyond the fence: the rear neighbors' tract bones — dark at
    # this hour, one pane faintly lit (the kitchen view's register)
    gx, gy = 1.8, 17.6
    make_box("Rear_Body_A", (gx, gy, GRADE_Z + 1.55), (7.40, 4.60, 3.10),
             (0.66, 0.62, 0.55, 1.0))
    make_box("Rear_Roof_A", (gx, gy, GRADE_Z + 3.32), (8.00, 5.20, 0.50),
             HENDERSON_ROOF)
    make_box("Rear_Window_A0", (gx - 1.9, gy - 2.33, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_NIGHT_PANE)
    make_box("Rear_Window_A1", (gx + 1.5, gy - 2.33, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_WINDOW_LIT)               # somebody else still up
    make_box("Rear_Body_B", (-6.9, 17.2, GRADE_Z + 1.50), (6.20, 4.80, 3.00),
             (0.60, 0.58, 0.54, 1.0))
    make_box("Rear_Roof_B", (-6.9, 17.2, GRADE_Z + 3.24), (6.80, 5.40, 0.48),
             HENDERSON_ROOF)
    make_box("Rear_Window_B0", (-6.0, 14.75, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_NIGHT_PANE)


def main():
    clear_scene()
    build_shell()
    build_door()
    build_window()
    build_bed_zone()
    build_nightstand()
    build_guitar_rig()
    build_desk_zone()
    build_dresser()
    build_ceiling_fixtures()
    build_exterior_back()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/jesse_bedroom.glb"))
    print(f"\n[build_jesse_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
