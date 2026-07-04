"""Sam Miller's bedroom — upstairs at 1428 Meadowlark Circle,
Harmony Creek Estates, TX — vol6 hero locale (9 VN bg refs:
vol6_ch0_prelude x2, ch1_bedroom, ch3_sam_bedroom, ch4_sam_list,
ch4_kitchen close, ch5_meadowlark, ch6_sam_bedroom, ch15_home close).

Sam Miller (18, the Kwik Stop register, 8-to-4) — the THIRD room of
1428 Meadowlark Circle after build_miller_kitchen.py and
build_miller_back_porch.py. Same house, same shared-palette block
(byte-identical, verify with md5). Canon baked in:

  · vol6_ch1_bedroom:28 + ch6_sam_bedroom:146 — "her cornflower
    blue bedroom". The walls are cornflower; the one non-negotiable
    color call in the whole room.
  · THE CEILING FAN — ch0_prelude:22 "The ceiling fan turns";
    ch1:28 "The fan still clicks on the third rotation, then the
    sixth, then the ninth"; ch5_meadowlark:147 she counts the
    clicks; ch15_home:192 "the clicks are, by August, just clicks."
    Modeled with the EAST blade hung 4 mm low — the click has a
    cause. House fixture; the scaffold's two commercial fluorescent
    tubes were Kwik Stop vocabulary and are gone.
  · ch0_prelude:22 — "The light through her curtains shifts from
    black to grey": light cotton panels on a rod, parted.
  · ch2_coda:60 + ch4_sam_list:26 — HER DESK, with the lamp
    ("the lamp on against the grey of the storm"; ch4:92 its
    reflection is "the lamp in her own window" — so the desk sits
    at the north end of the east wall, near the window). Lamp glow
    baked; the scene Light3D matches from the .tscn.
  · ch4_sam_list:84 — the WEDNESDAY LIST notebook ("one of the
    small cheap spiral-bound ones", 99 cents, Kwik Stop): "She
    slides it between the mattress and the box spring." Modeled as
    a thin paper edge just proud of the east bed rail seam —
    present, occluded, never announced.
  · ch6_sam_bedroom:38 — "Sam's phone, on her dresser, buzzes":
    the dresser is real furniture here, phone slab on top.
  · ch4_sam_list:121 — "She goes to the closet": west-wall bypass
    closet, north half open — a spare Kwik Stop pinks-and-blues
    uniform polo on the rod (the uniform per sam_miller.md header).
  · ch3_sam_bedroom:38 ("Sam is in bed. Lamp off.") — bedside lamp
    on the nightstand. ch1:24 / ch2 "She closes her bedroom door" /
    ch5:135 — the door in the south gap is CLOSED (white six-panel,
    matching the kitchen's pantry leaf).
  · sam_miller.md §III — THE CORKBOARD above her bed, four feet by
    three, pinned since she was twelve, FULL. Pinned per the lore
    inventory: the Westport wedding-chapel Polaroid, the Gallatin
    Rock Club ticket stub (Jan 14, $8), the frog-in-sunglasses
    receipt strip, the graduation tassel (gold/white/blue), the
    folded "if you ever want me to stop" square, the 2019 Pensacola
    postcard, the Phase II model-home photo held by the NexCorp
    lapel pin (the pin IS the navy one), and the D'Ambrosio napkin
    with the HALSEY·PRIVATE gate sketch — plus filler layers,
    because the board is full.
  · sam_miller.md §V — THE JUNK DRAWER: the nightstand drawer is
    CLOSED. Diego's drumstick, the sealed "do not open until you
    are nineteen" envelope, the ceramic frog, the NexCorp pencils,
    Skip's loyalty card, Maya's paper crane, the guitar picks, the
    Galveston lottery roll are all INSIDE and not modeled loose
    (same treatment as Maya's closet box / Philip's box).
  · sam_miller.md §I — THE MIXTAPE ("MIX FOR SAMMY · FOR THE 3 PM
    SHIFT") on the nightstand by the lamp: canon gives it no fixed
    resting place, so it sits with her most-reached-for things —
    Diego is missing and this is what she has. Register-roll paper
    insert, one red tick (track 7).
  · One NexCorp Residential Solutions pencil on the desk (§V: her
    father's 2016 box — "she has been using [them] ever since").
  · EXTERIOR (second floor, window over the front yard): the
    cul-de-sac below (ch1:51, ch4:88). The CRACKED SPRINKLER HEAD
    on the corner of the yard and the faint grey stripe it has
    etched into the sidewalk (ch0_prelude:14) — head + puddle sync
    with build_miller_kitchen's front yard; the stripe is new here.
    Sam's silver Corolla in the driveway, the front walk, mailbox,
    specimen tree — all mirrored from the kitchen exterior (y-1,
    kitchen ROOM_D is 6, this room's is 5). The overhead
    STREETLIGHT and the THREE DRIVEWAYS OPPOSITE and the storm
    drain at the bend (ch4_sam_list:88). The NEXCORP-LOGO MAILBOX
    across the street (ch1:51). THE WHITE SEDAN at the curb keeping
    its vigil (ch2_coda:36; ch3 network canon) — NO FRONT PLATE
    (vol6_ch1_stranger:85 "Texas requires a front license plate"),
    rear plate only. Don Geller's tract massing dead ahead with the
    porch light on (shared sightline with the kitchen window).

Canon-NEGATIVES honored (what Sam's room does NOT have):
  · NO license-plate notebook — §IV keeps it in the front pocket of
    her backpack, modeled by the kitchen back door in
    build_miller_kitchen.py. No bedroom scene shows it here.
  · NO zine stockpile — §II keeps the GAS STATION OBSERVATIONS
    copies in the Kwik Stop storeroom under the cleaning supplies.
  · NO laptop / no glowing chat client — Sam's late-night channel
    is her PHONE (ch2_coda:60, ch6:38). The lit chat window on a
    ThinkPad is Maya's room, not Sam's.
  · NO posters / store-bought wall art — the only wall system in
    canon is the corkboard (§III). The scaffold's three faded
    posters were codegen vocabulary and are gone.
  · NO commercial fluorescents, NO drop ceiling (house, not store).
  · NO box fan (Maya's), NO radio, NO cat (the black cat of ch1 is
    transient and unregistered — it does not live here).

NOTE — the ch0_prelude Diego's-bedroom stand-in: the prelude reuses
this bg for one wide narrated shot of 892 Ashberry. Diego's props
(the green duffel, the mirror photo, the periodic table) belong to
his room and are NOT modeled here; the shot reads on the generic
teen-bedroom bones.

Shell footprint kept from the scaffold (4 x 5 m, CEIL 2.6, door gap
in the south wall x -1..+1 — the Background3D camera preset
(0, 2.30, +0.5 / yaw 180 / fov 60) is tuned to it; closed leaf +
infills per the Maya-bedroom pattern). Window is a REAL OPENING with
frame + sash + muntins, no glass (playbook no-transparency rule).

MILLER HOUSE shared block below is byte-identical with
build_miller_kitchen.py / build_miller_back_porch.py (⚠ KEEP IN
SYNC — verify with md5). Their block headers still name only the
two original files; when either sibling gets its next pass, update
all three headers together (this session must not touch them).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_wall, make_ceiling, make_door_hinges
from _props.safety import make_smoke_detector, make_hvac_vent

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6

# ═════════════════════════════════════════════════════════════════
# MILLER HOUSE — SHARED PALETTE + VOCABULARY (⚠ KEEP IN SYNC)
# This block is declared IDENTICALLY in build_miller_back_porch.py
# and build_miller_kitchen.py — the two rooms of 1428 Meadowlark
# Circle. ONE house: if you retune a value here, retune the sibling
# file to match. Exterior body/roof match build_harmony_district's
# COL_HOUSE_BODY_A / COL_HOUSE_ROOF_A so the house reads as the same
# cream tract model it is from the street grid.
# ═════════════════════════════════════════════════════════════════
MILLER_SIDING     = (0.86, 0.82, 0.72, 1.0)   # HCE cream lap siding
MILLER_SIDING_SH  = (0.72, 0.68, 0.58, 1.0)   # siding shadow seams
MILLER_TRIM       = (0.93, 0.91, 0.85, 1.0)   # builder-white trim/fascia
MILLER_ROOF       = (0.32, 0.26, 0.22, 1.0)   # dark shingle
MILLER_DOOR_GREEN = (0.26, 0.36, 0.30, 1.0)   # the back door, hunter green
MILLER_INT_WALL   = (0.91, 0.87, 0.76, 1.0)   # builder eggshell
MILLER_BASEBOARD  = (0.42, 0.32, 0.22, 1.0)
MILLER_OAK        = (0.62, 0.46, 0.28, 1.0)   # golden oak — the dinette set
MILLER_OAK_DK     = (0.38, 0.27, 0.17, 1.0)
MILLER_LAMINATE   = (0.78, 0.72, 0.62, 1.0)   # almond countertop laminate
MILLER_APPLIANCE  = (0.88, 0.87, 0.82, 1.0)   # almond-white appliances
MILLER_WICKER     = (0.76, 0.65, 0.46, 1.0)   # Bianca's mother's chair
MILLER_WICKER_DK  = (0.56, 0.46, 0.31, 1.0)
MILLER_DECK       = (0.55, 0.44, 0.31, 1.0)   # porch deck boards
MILLER_DECK_SEAM  = (0.34, 0.27, 0.19, 1.0)
MILLER_SCREEN_FR  = (0.28, 0.30, 0.32, 1.0)   # screen-frame charcoal
MILLER_FENCE      = (0.60, 0.52, 0.40, 1.0)   # weathered pine privacy fence
MILLER_FENCE_SEAM = (0.42, 0.35, 0.26, 1.0)
COL_LAWN_AUG      = (0.44, 0.46, 0.24, 1.0)   # back-yard Bermuda, mid-August
COL_LAWN_BROWN    = (0.60, 0.53, 0.30, 1.0)   # the browning patches
COL_LAWN_FRONT    = (0.30, 0.48, 0.22, 1.0)   # front lawn — sprinkler-kept
COL_CONCRETE      = (0.66, 0.64, 0.58, 1.0)
COL_ASPHALT       = (0.24, 0.24, 0.25, 1.0)
COL_TRUNK         = (0.36, 0.28, 0.20, 1.0)
COL_OAK_CANOPY    = (0.27, 0.38, 0.22, 1.0)   # the neighbor's oak
COL_OAK_CANOPY_2  = (0.23, 0.33, 0.19, 1.0)
COL_CREPE_LEAF    = (0.32, 0.45, 0.26, 1.0)
COL_CREPE_BLOOM   = (0.82, 0.45, 0.52, 1.0)   # late-bloom watermelon pink
COL_CERAMIC       = (0.92, 0.90, 0.84, 1.0)   # plates / mugs
COL_COFFEE        = (0.30, 0.20, 0.12, 1.0)
COL_TEA           = (0.68, 0.44, 0.20, 1.0)   # iced-tea amber
COL_PORCHBULB     = (1.00, 0.88, 0.60, 1.0)   # warm porch-light glow

_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _miller_chair(prefix, cx, cy, facing):
    """The Millers' oak dinette chair — four at the kitchen table,
    ONE carried out to the porch for company. Declared identically
    in both Miller files; keep the geometry in sync."""
    dx, dy = _DIRS[facing]
    make_box(f"{prefix}_Seat", (cx, cy, 0.45), (0.42, 0.42, 0.045), MILLER_OAK)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.17, cy + sy * 0.17, 0.225),
                 0.019, 0.45, MILLER_OAK_DK)
    bx, by = cx - dx * 0.20, cy - dy * 0.20
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.17 if dx == 0 else 0.0)
        py = by + (sgn * 0.17 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_Post_{pi}", (px, py, 0.70), 0.017, 0.50, MILLER_OAK)
    slat = (0.38, 0.032, 0.085) if dx == 0 else (0.032, 0.38, 0.085)
    for si, sz in enumerate((0.74, 0.90)):
        make_box(f"{prefix}_Slat_{si}", (bx, by, sz), slat, MILLER_OAK)
# ═════════ end shared block ══════════════════════════════════════

# ── Sam's-room-only palette ──────────────────────────────────────
COL_CORNFLOWER  = (0.56, 0.66, 0.84, 1.0)   # THE cornflower blue (ch1/ch6)
COL_CARPET      = (0.63, 0.59, 0.51, 1.0)   # builder beige carpet
COL_CARPET_SH   = (0.54, 0.50, 0.43, 1.0)   # traffic-worn shading
COL_CEIL_WHITE  = (0.93, 0.91, 0.85, 1.0)   # flat drywall
COL_QUILT       = (0.84, 0.79, 0.68, 1.0)   # oatmeal spread
COL_QUILT_BAND  = (0.44, 0.52, 0.70, 1.0)   # denim-blue band
COL_LINEN       = (0.90, 0.88, 0.82, 1.0)
COL_CURTAIN     = (0.93, 0.90, 0.82, 1.0)   # light cotton (ch0 light passes)
COL_CURTAIN_SH  = (0.84, 0.80, 0.71, 1.0)
COL_BRASS       = (0.70, 0.57, 0.30, 1.0)
COL_LAMP_GLOW   = (0.98, 0.88, 0.62, 1.0)
COL_INK         = (0.24, 0.22, 0.22, 1.0)
COL_CORK        = (0.62, 0.47, 0.31, 1.0)
COL_CHARCOAL    = (0.16, 0.15, 0.16, 1.0)   # cassette shell / phone
COL_RED_INK     = (0.78, 0.18, 0.16, 1.0)   # Diego's one red passage
COL_TASSEL_GOLD = (0.80, 0.66, 0.28, 1.0)   # HCHS gold / white / blue
COL_TASSEL_WHT  = (0.92, 0.91, 0.86, 1.0)
COL_TASSEL_BLUE = (0.30, 0.40, 0.62, 1.0)
COL_POLO_PINK   = (0.88, 0.55, 0.62, 1.0)   # Kwik Stop pinks-and-blues
COL_POLO_BLUE   = (0.34, 0.46, 0.72, 1.0)
COL_NIGHT_PANE  = (0.10, 0.12, 0.15, 1.0)   # dark glazing on far houses
COL_SEDAN_WHITE = (0.90, 0.90, 0.88, 1.0)   # the vigil sedan
GARMENT_TINTS = [(0.30, 0.36, 0.46, 1.0),   # denim jacket
                 (0.48, 0.24, 0.20, 1.0),   # flannel
                 (0.55, 0.55, 0.53, 1.0)]   # grey tee

PAL_WALL = {"wall": COL_CORNFLOWER, "baseboard": MILLER_BASEBOARD}

# Window opening in the north wall (real opening, no glass)
WIN_W = 1.30                  # opening x -0.65..+0.65
WIN_SILL = 0.95
WIN_HEAD = 2.15
WALL_N_FACE = ROOM_D - 0.10   # interior face y 4.9
GRADE_Z = -3.20               # front-yard grade (second-floor room)


# ═════════════════════════════════════════════════════════════════
# SHELL — wall-to-wall builder carpet, CORNFLOWER BLUE walls
# (ch1:28 / ch6:146 — the color the prose names twice), flat white
# drywall ceiling (house — no drop grid, no stains), south door gap
# kept with infills for the closed leaf. No crown molding (1991
# HCE tract, same bones as the kitchen).
# ═════════════════════════════════════════════════════════════════
def build_shell():
    # Carpet: one slab + two worn traffic patches (bedside + door)
    make_box("Floor_Carpet", (0.0, ROOM_D / 2.0, -0.05),
             (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), COL_CARPET)
    make_box("Floor_Worn_Bedside", (-0.72, 3.5, 0.0008), (0.55, 1.30, 0.0016),
             COL_CARPET_SH)
    make_box("Floor_Worn_Door", (0.0, 0.55, 0.0008), (0.85, 0.70, 0.0016),
             COL_CARPET_SH)
    # Walls — west / east full runs, cornflower
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
             COL_CORNFLOWER)
    make_box("Wall_N_HeadFill", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.20, CEIL - WIN_HEAD), COL_CORNFLOWER)
    # South wall — scaffold door gap x -1..+1 kept (camera preset)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             COL_CORNFLOWER)
    # Gap infill either side of the 0.90 m door leaf
    for nm, fx in [("Wall_S_FillW", -0.725), ("Wall_S_FillE", +0.725)]:
        make_box(nm, (fx, 0.0, 1.15), (0.55, 0.20, 2.30), COL_CORNFLOWER)
    # Flat white drywall ceiling — the one she stares at (ch3/ch15)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_CEIL_WHITE},
                 with_grid=False, with_stains=False)


# ═════════════════════════════════════════════════════════════════
# DOOR — CLOSED white six-panel leaf in the south gap (ch1 "She
# closes her bedroom door", ch2_coda "Her bedroom door is closed",
# ch5:135 her mother "closes the door behind her"). Six-panel to
# match the kitchen's pantry leaf — one house, one door catalog.
# Beyond it: the hall, the parents' bedroom two walls down (ch3:72).
# ═════════════════════════════════════════════════════════════════
def build_door():
    make_box("Door_Leaf", (0.0, 0.03, 1.03), (0.90, 0.05, 2.06), MILLER_TRIM)
    for ci, px in enumerate((-0.21, +0.21)):
        for ri, pz in enumerate((0.48, 1.06, 1.62)):
            make_box(f"Door_Panel_{ci}_{ri}", (px, 0.062, pz), (0.30, 0.012, 0.44),
                     (0.85, 0.82, 0.74, 1.0))
    make_cyl("Door_Knob", (0.35, 0.075, 0.98), 0.028, 0.045, COL_BRASS, axis='Y')
    make_door_hinges("Door_Hinge", edge_x=-0.43, edge_y=0.06,
                     edge_z_centers=[0.35, 1.03, 1.75], axis='X')
    for sgn in (-1, +1):
        make_box(f"Door_Casing_{sgn:+d}", (sgn * 0.50, 0.11, 1.06), (0.09, 0.05, 2.12),
                 MILLER_TRIM)
    make_box("Door_CasingHead", (0.0, 0.11, 2.16), (1.09, 0.05, 0.10), MILLER_TRIM)


# ═════════════════════════════════════════════════════════════════
# WINDOW — the north window over the front yard: REAL OPENING,
# painted double-hung frame, meeting rail + upper muntins, casing,
# stool, apron — same joinery as the kitchen's front window, one
# floor up. Light cotton curtains, parted (ch0: "The light through
# her curtains shifts from black to grey").
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D
    make_box("Win_FrameT", (0.0, wy, WIN_HEAD - 0.03), (WIN_W, 0.14, 0.06), MILLER_TRIM)
    make_box("Win_FrameB", (0.0, wy, WIN_SILL + 0.03), (WIN_W, 0.14, 0.06), MILLER_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Jamb_{sgn:+d}", (sgn * (WIN_W / 2.0 - 0.03), wy, 1.55),
                 (0.06, 0.14, 1.20), MILLER_TRIM)
    make_box("Win_MeetingRail", (0.0, wy, 1.56), (WIN_W - 0.08, 0.10, 0.06), MILLER_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Muntin_{sgn:+d}", (sgn * 0.22, wy - 0.02, 1.86),
                 (0.035, 0.06, 0.54), MILLER_TRIM)
    # Interior casing + stool + apron
    for sgn in (-1, +1):
        make_box(f"Win_Casing_{sgn:+d}", (sgn * (WIN_W / 2.0 + 0.09), wy - 0.105, 1.55),
                 (0.10, 0.05, 1.40), MILLER_TRIM)
    make_box("Win_CasingHead", (0.0, wy - 0.105, WIN_HEAD + 0.08),
             (WIN_W + 0.28, 0.05, 0.10), MILLER_TRIM)
    make_box("Win_Stool", (0.0, wy - 0.135, WIN_SILL + 0.02), (WIN_W + 0.30, 0.16, 0.04),
             MILLER_TRIM)
    make_box("Win_Apron", (0.0, wy - 0.105, WIN_SILL - 0.05), (WIN_W + 0.16, 0.05, 0.09),
             MILLER_TRIM)
    # Curtains — rod, finials, two parted cotton panels
    make_cyl("Curtain_Rod", (0.0, wy - 0.16, 2.28), 0.012, 1.70, COL_BRASS, axis='X')
    for sgn in (-1, +1):
        make_cyl(f"Curtain_Finial_{sgn:+d}", (sgn * 0.86, wy - 0.16, 2.28), 0.026, 0.05,
                 COL_BRASS, axis='X')
        make_box(f"Curtain_Panel_{sgn:+d}", (sgn * 0.70, wy - 0.155, 1.62),
                 (0.26, 0.030, 1.32), COL_CURTAIN)
        make_box(f"Curtain_Fold_{sgn:+d}", (sgn * 0.62, wy - 0.175, 1.58),
                 (0.09, 0.018, 1.22), COL_CURTAIN_SH)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · THE CUL-DE-SAC FROM UPSTAIRS — what Sam watches
# (ch1:51, ch4:88): the front yard below with the CRACKED SPRINKLER
# HEAD and the grey stripe it has etched into the sidewalk
# (ch0_prelude:14), her silver Corolla in the driveway, the street,
# the overhead streetlight, THREE driveways opposite, the storm
# drain at the bend, the NEXCORP-LOGO MAILBOX across the street
# (ch1:51), THE WHITE SEDAN at the curb on its vigil (ch2_coda:36 —
# no front plate, vol6_ch1_stranger:85), and Don Geller's massing
# dead ahead, porch light on (same sightline the kitchen window
# has, one floor down). Yard features mirror build_miller_kitchen's
# exterior at y-1 (that room is 6 m deep, this one 5) so the two
# views describe ONE front yard.
# ═════════════════════════════════════════════════════════════════
def build_exterior_front():
    wallout = ROOM_D + 0.10
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20
    seg_cx = WIN_W / 2.0 + seg_len / 2.0
    # Facade skins — full height (second floor: grade to eave)
    skin_h = CEIL - GRADE_Z                          # 5.8
    make_box("Ext_Skin_W", (-seg_cx, wallout + 0.02, (CEIL + GRADE_Z) / 2.0),
             (seg_len, 0.06, skin_h), MILLER_SIDING)
    make_box("Ext_Skin_E", (+seg_cx, wallout + 0.02, (CEIL + GRADE_Z) / 2.0),
             (seg_len, 0.06, skin_h), MILLER_SIDING)
    make_box("Ext_Skin_Sill", (0.0, wallout + 0.02, (WIN_SILL + GRADE_Z) / 2.0),
             (WIN_W, 0.06, WIN_SILL - GRADE_Z), MILLER_SIDING)
    make_box("Ext_Skin_Head", (0.0, wallout + 0.02, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.06, CEIL - WIN_HEAD), MILLER_SIDING)
    for si, sz in enumerate((-2.4, -1.2, 0.55, 2.35)):
        make_box(f"Ext_SidingSeam_{si}", (0.0, wallout + 0.052, sz),
                 (ROOM_W + 0.4, 0.006, 0.02), MILLER_SIDING_SH)
    # Her shutters + the first-floor (kitchen) window below-left of
    # hers on the same facade — dark pane, trim, hunter shutters
    for sgn in (-1, +1):
        make_box(f"Ext_Shutter_{sgn:+d}", (sgn * (WIN_W / 2.0 + 0.26), wallout + 0.06,
                 1.55), (0.32, 0.05, 1.34), MILLER_DOOR_GREEN)
        for li in range(4):
            make_box(f"Ext_Shutter_{sgn:+d}_Louver_{li}", (sgn * (WIN_W / 2.0 + 0.26),
                     wallout + 0.09, 1.10 + li * 0.30), (0.28, 0.012, 0.03),
                     (0.20, 0.28, 0.23, 1.0))
    make_box("Ext_KitchenWin_Pane", (0.0, wallout + 0.06, GRADE_Z + 1.55),
             (1.70, 0.05, 1.20), COL_NIGHT_PANE)
    make_box("Ext_KitchenWin_TrimT", (0.0, wallout + 0.07, GRADE_Z + 2.20),
             (1.86, 0.05, 0.08), MILLER_TRIM)
    make_box("Ext_KitchenWin_TrimB", (0.0, wallout + 0.07, GRADE_Z + 0.90),
             (1.86, 0.05, 0.08), MILLER_TRIM)
    for sgn in (-1, +1):
        make_box(f"Ext_KitchenWin_Shutter_{sgn:+d}", (sgn * 1.13, wallout + 0.08,
                 GRADE_Z + 1.55), (0.34, 0.05, 1.34), MILLER_DOOR_GREEN)
    # Ground: front lawn (sprinkler-kept) / sidewalk / curb / street
    # / far lawn — same strata as the kitchen view
    make_box("Ext_Lawn", (0.0, 6.95, GRADE_Z - 0.05), (24.0, 3.7, 0.10), COL_LAWN_FRONT)
    make_box("Ext_Sidewalk", (0.0, 8.95, GRADE_Z - 0.02), (24.0, 0.75, 0.10),
             COL_CONCRETE)
    make_box("Ext_Curb", (0.0, 9.38, GRADE_Z - 0.02), (24.0, 0.16, 0.14), COL_CONCRETE)
    make_box("Ext_Street", (0.0, 11.55, GRADE_Z - 0.07), (24.0, 4.2, 0.10), COL_ASPHALT)
    make_box("Ext_FarLawn", (0.0, 15.9, GRADE_Z - 0.05), (24.0, 4.6, 0.10),
             COL_LAWN_FRONT)
    # The front walk + the Millers' own mailbox at the curb
    make_box("Ext_Walk", (-1.3, 6.95, GRADE_Z + 0.006), (0.95, 3.7, 0.012), COL_CONCRETE)
    make_cyl("Ext_MailPost", (-1.3, 8.75, GRADE_Z + 0.45), 0.035, 0.90, MILLER_FENCE_SEAM)
    make_box("Ext_Mailbox", (-1.3, 8.75, GRADE_Z + 1.00), (0.18, 0.42, 0.20),
             (0.24, 0.34, 0.30, 1.0))
    # THE CRACKED SPRINKLER HEAD (ch0_prelude:14 — "the head on the
    # left corner of the yard... a thin, surgical arc") + its
    # puddle + THE FAINT GREY STRIPE etched into the sidewalk
    # concrete over two summers. Head position syncs with
    # build_miller_kitchen (its 7.35 at y-1).
    make_cyl("Ext_SprinklerCracked", (1.35, 6.35, GRADE_Z + 0.035), 0.020, 0.07,
             COL_BRASS, segments=8)
    make_box("Ext_SprinklerPuddle", (1.42, 6.28, GRADE_Z + 0.004), (0.40, 0.30, 0.006),
             (0.34, 0.42, 0.28, 1.0))
    make_box("Ext_EtchedStripe", (1.88, 8.95, GRADE_Z + 0.036), (0.11, 0.78, 0.004),
             (0.57, 0.56, 0.51, 1.0))
    for si, (sx, sy) in enumerate([(-3.4, 6.1), (3.9, 7.6)]):
        make_cyl(f"Ext_Sprinkler_{si}", (sx, sy, GRADE_Z + 0.025), 0.016, 0.05,
                 (0.30, 0.31, 0.32, 1.0), segments=8)
    # The HCE specimen tree east of the walk (sync w/ kitchen)
    make_cyl("Ext_Tree_Trunk", (2.7, 7.7, GRADE_Z + 1.1), 0.12, 2.20, COL_TRUNK)
    for ci, (cr, cz) in enumerate([(1.15, 2.30), (0.85, 3.05), (0.50, 3.65)]):
        make_cyl(f"Ext_Tree_Canopy_{ci}", (2.7, 7.7, GRADE_Z + cz), cr, 0.70,
                 COL_OAK_CANOPY if ci % 2 == 0 else COL_OAK_CANOPY_2, segments=10)
    # The driveway + SAM'S SILVER COROLLA (vol6_ch4_kitchen:26 —
    # same car, same colors as the kitchen view)
    make_box("Ext_Driveway", (-3.2, 7.35, GRADE_Z + 0.006), (2.5, 4.5, 0.012),
             COL_CONCRETE)
    cx, cy = -3.2, 7.3
    for wi, (wx, wy2) in enumerate([(-0.68, -1.30), (0.68, -1.30), (-0.68, 1.30),
                                    (0.68, 1.30)]):
        make_cyl(f"Corolla_Wheel_{wi}", (cx + wx, cy + wy2, GRADE_Z + 0.28), 0.26, 0.18,
                 (0.13, 0.13, 0.14, 1.0), axis='X', segments=10)
    make_box("Corolla_Body", (cx, cy, GRADE_Z + 0.52), (1.60, 4.15, 0.44),
             (0.74, 0.75, 0.78, 1.0))
    make_box("Corolla_Cabin", (cx, cy - 0.10, GRADE_Z + 0.93), (1.45, 2.05, 0.38),
             (0.16, 0.18, 0.20, 1.0))
    make_box("Corolla_Roof", (cx, cy - 0.10, GRADE_Z + 1.135), (1.50, 2.10, 0.05),
             (0.74, 0.75, 0.78, 1.0))
    make_box("Corolla_Plate", (cx, cy - 2.09, GRADE_Z + 0.48), (0.30, 0.015, 0.10),
             P.PAPER)
    # THE OVERHEAD STREETLIGHT (ch4:88 — the storm sheet catches
    # it). Pole on the buffer strip at the road edge, arm over the
    # street (playbook: never in the road surface).
    make_cyl("Streetlight_Pole", (2.4, 9.42, GRADE_Z + 2.3), 0.055, 4.60,
             (0.35, 0.36, 0.38, 1.0), segments=8)
    make_cyl("Streetlight_Arm", (2.4, 10.15, GRADE_Z + 4.52), 0.032, 1.50,
             (0.35, 0.36, 0.38, 1.0), axis='Y', segments=8)
    make_box("Streetlight_Head", (2.4, 10.95, GRADE_Z + 4.48), (0.16, 0.55, 0.12),
             (0.28, 0.29, 0.30, 1.0))
    make_cyl("Streetlight_Lamp", (2.4, 10.95, GRADE_Z + 4.41), 0.07, 0.03,
             COL_PORCHBULB, segments=10)
    # The storm drain at the bend (ch4:88) — curb inlet, west end
    make_box("StormDrain_Throat", (-6.5, 9.34, GRADE_Z + 0.02), (0.90, 0.10, 0.11),
             (0.10, 0.10, 0.11, 1.0))
    make_box("StormDrain_Lintel", (-6.5, 9.38, GRADE_Z + 0.085), (1.00, 0.18, 0.03),
             (0.52, 0.51, 0.47, 1.0))
    # THE NEXCORP-LOGO MAILBOX across the street (ch1:51)
    make_cyl("NexMail_Post", (-1.2, 13.85, GRADE_Z + 0.45), 0.035, 0.90,
             (0.30, 0.28, 0.26, 1.0))
    make_box("NexMail_Box", (-1.2, 13.85, GRADE_Z + 1.00), (0.18, 0.42, 0.20),
             P.BRAND_NAVY_HCE)
    make_box("NexMail_Logo", (-1.2, 13.63, GRADE_Z + 1.00), (0.10, 0.012, 0.06),
             P.BRAND_NAVY_TXT)
    # THE WHITE SEDAN — parked at the far curb, nose west, on its
    # vigil (ch2_coda:36). NO FRONT PLATE (vol6_ch1_stranger:85);
    # the rear plate is the only one it has. Windshield tinted dark
    # (ch2_kwik_stop:108). The two watchers stay unmodeled — from
    # up here they are silhouettes at most.
    sx0, sy0 = 1.6, 12.85
    for wi, (wx, wy3) in enumerate([(-1.30, -0.72), (-1.30, 0.72), (1.30, -0.72),
                                    (1.30, 0.72)]):
        make_cyl(f"Sedan_Wheel_{wi}", (sx0 + wx, sy0 + wy3, GRADE_Z + 0.28), 0.26, 0.18,
                 (0.13, 0.13, 0.14, 1.0), axis='Y', segments=10)
    make_box("Sedan_Body", (sx0, sy0, GRADE_Z + 0.52), (4.20, 1.60, 0.44),
             COL_SEDAN_WHITE)
    make_box("Sedan_Cabin", (sx0 + 0.10, sy0, GRADE_Z + 0.93), (2.05, 1.45, 0.38),
             (0.14, 0.16, 0.18, 1.0))
    make_box("Sedan_Roof", (sx0 + 0.10, sy0, GRADE_Z + 1.135), (2.10, 1.50, 0.05),
             COL_SEDAN_WHITE)
    make_box("Sedan_PlateRear", (sx0 + 2.11, sy0, GRADE_Z + 0.48), (0.015, 0.30, 0.10),
             P.PAPER)                     # rear only — no front plate
    # DON GELLER'S HOUSE dead ahead — same massing the kitchen sees,
    # porch light on. Plus the flanking tract repeats and the THREE
    # DRIVEWAYS OPPOSITE (ch4:88).
    gx, gy = 0.4, 16.8
    make_box("Geller_Body", (gx, gy, GRADE_Z + 1.55), (7.5, 4.5, 3.10),
             (0.72, 0.66, 0.56, 1.0))
    make_box("Geller_Roof0", (gx, gy, GRADE_Z + 3.30), (8.1, 5.1, 0.50), MILLER_ROOF)
    make_box("Geller_Roof1", (gx, gy, GRADE_Z + 3.76), (5.7, 3.5, 0.44), MILLER_ROOF)
    make_box("Geller_Porch", (gx + 0.5, gy - 2.55, GRADE_Z + 0.12), (2.6, 1.2, 0.24),
             COL_CONCRETE)
    for pi, px in enumerate((-0.6, 1.6)):
        make_cyl(f"Geller_PorchPost_{pi}", (gx + px, gy - 3.05, GRADE_Z + 1.15),
                 0.05, 2.05, MILLER_TRIM)
    make_box("Geller_PorchRoof", (gx + 0.5, gy - 2.65, GRADE_Z + 2.24), (2.9, 1.5, 0.14),
             MILLER_ROOF)
    make_box("Geller_Door", (gx + 1.1, gy - 2.28, GRADE_Z + 1.02), (0.90, 0.06, 2.00),
             (0.28, 0.24, 0.22, 1.0))
    make_box("Geller_LightBracket", (gx + 0.42, gy - 2.26, GRADE_Z + 1.72),
             (0.07, 0.05, 0.12), P.METAL_BLACK)
    make_cyl("Geller_PorchLight", (gx + 0.42, gy - 2.32, GRADE_Z + 1.68), 0.055, 0.12,
             COL_PORCHBULB, segments=10)
    for wi, wx2 in enumerate((-2.2, -0.6)):
        make_box(f"Geller_Window_{wi}", (gx + wx2, gy - 2.28, GRADE_Z + 1.55),
                 (0.90, 0.06, 0.80), COL_NIGHT_PANE)
    for si2 in range(4):
        make_cyl(f"Geller_Shrub_{si2}", (gx - 2.6 + si2 * 1.15, gy - 2.42,
                 GRADE_Z + 0.30), 0.34, 0.55, (0.22, 0.34, 0.20, 1.0), segments=8)
    # Flanking tract repeats — the same bones down the block
    make_box("TractW_Body", (-8.4, 16.4, GRADE_Z + 1.50), (6.5, 4.8, 3.00),
             (0.62, 0.58, 0.62, 1.0))
    make_box("TractW_Roof", (-8.4, 16.4, GRADE_Z + 3.22), (7.1, 5.4, 0.48), MILLER_ROOF)
    make_box("TractW_Window", (-7.2, 14.0, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_NIGHT_PANE)
    make_box("TractE_Body", (9.2, 16.5, GRADE_Z + 1.50), (6.2, 4.6, 2.95),
             (0.66, 0.62, 0.54, 1.0))
    make_box("TractE_Roof", (9.2, 16.5, GRADE_Z + 3.18), (6.8, 5.2, 0.46), MILLER_ROOF)
    make_box("TractE_Window", (8.2, 14.2, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_NIGHT_PANE)
    # The three driveways opposite (ch4:88 — the storm sheet runs
    # "across all three driveways opposite")
    for di, dx in enumerate((-7.4, 3.6, 8.6)):
        make_box(f"Ext_FarDriveway_{di}", (dx, 14.65, GRADE_Z + 0.006),
                 (2.2, 2.10, 0.012), COL_CONCRETE)


# ═════════════════════════════════════════════════════════════════
# BED ZONE — twin bed on the west wall, head at the window end.
# She lies ON it fully dressed all volume long (ch3/ch4k/ch15):
# made, slightly sat-on. Between the mattress and the box spring,
# its east edge just proud of the seam: THE WEDNESDAY LIST notebook
# (ch4_sam_list:84) — present, occluded, never announced.
# ═════════════════════════════════════════════════════════════════
def build_bed_zone():
    bx = -1.42                     # bed center x (frame -1.93..-0.91)
    y0, y1 = 2.55, 4.45            # foot..head (head at window end)
    by = (y0 + y1) / 2.0
    make_box("Bed_Rail", (bx, by, 0.32), (1.02, 1.92, 0.12), MILLER_OAK)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Bed_Leg_{li}", (bx + sx * 0.46, by + sy * 0.90, 0.15), 0.030, 0.30,
                 MILLER_OAK_DK)
    make_box("Bed_Headboard", (bx, y1 - 0.02, 0.62), (1.02, 0.06, 0.70), MILLER_OAK)
    make_box("Bed_HeadboardCap", (bx, y1 - 0.02, 0.99), (1.06, 0.09, 0.05),
             MILLER_OAK_DK)
    # Box spring + mattress — the seam the notebook lives in
    make_box("Bed_BoxSpring", (bx, by, 0.425), (0.98, 1.86, 0.13), COL_LINEN)
    make_box("Bed_Mattress", (bx, by, 0.56), (0.98, 1.86, 0.14),
             (0.94, 0.92, 0.87, 1.0))
    # THE WEDNESDAY LIST (ch4:84 — "She slides it between the
    # mattress and the box spring.") Paper edge 1.5 cm proud of the
    # east rail seam. Small, cheap, 99 cents, Kwik Stop.
    make_box("WednesdayList_Edge", (-0.918, 3.30, 0.49), (0.032, 0.145, 0.012), P.PAPER)
    # Spread — oatmeal, denim-blue band, pulled square then sat on
    # (ch5: her mother was sitting here)
    make_box("Bedspread_Top", (bx, by - 0.09, 0.655), (1.00, 1.68, 0.05), COL_QUILT)
    make_box("Bedspread_DrapeE", (bx + 0.505, by - 0.09, 0.50), (0.025, 1.68, 0.28),
             COL_QUILT)
    make_box("Bedspread_DrapeS", (bx, y0 + 0.03, 0.50), (1.00, 0.025, 0.28), COL_QUILT)
    make_box("Bedspread_Band", (bx, 2.95, 0.681), (1.005, 0.20, 0.006), COL_QUILT_BAND)
    make_box("Bedspread_SatWrinkle", (bx + 0.18, 3.55, 0.682), (0.44, 0.30, 0.006),
             (0.78, 0.73, 0.62, 1.0))
    make_box("Bed_Pillow", (bx, y1 - 0.24, 0.72), (0.82, 0.34, 0.11), COL_LINEN)


# ═════════════════════════════════════════════════════════════════
# THE CORKBOARD (sam_miller.md §III) — above the bed on the west
# wall, four feet by three (1.22 x 0.91), pinned since she was
# twelve, FULL. Filler layers first, then the lore inventory:
# the Westport Polaroid, the Gallatin Rock Club stub, the frog
# receipt, the graduation tassel, the folded square, the Pensacola
# postcard, the model-home photo held by THE NEXCORP LAPEL PIN
# (navy — every other pin is red or steel), the D'Ambrosio napkin.
# ═════════════════════════════════════════════════════════════════
def build_corkboard():
    wx = -ROOM_W / 2.0 + 0.10          # interior wall face x -1.9
    make_box("Cork_Board", (wx - 0.012, 3.50, 1.62), (0.024, 1.22, 0.91), COL_CORK)
    make_box("Cork_FrameT", (wx - 0.018, 3.50, 2.095), (0.036, 1.28, 0.05), MILLER_OAK)
    make_box("Cork_FrameB", (wx - 0.018, 3.50, 1.145), (0.036, 1.28, 0.05), MILLER_OAK)
    for sgn in (-1, +1):
        make_box(f"Cork_FrameSide_{sgn:+d}", (wx - 0.018, 3.50 + sgn * 0.615, 1.62),
                 (0.036, 0.05, 1.00), MILLER_OAK)
    face = wx - 0.028                  # pinned-layer plane
    # Filler layers — six years of accumulation under the hero items
    fills = [(3.02, 1.95, P.PAPER_AGED), (3.30, 2.00, P.PAPER),
             (3.58, 1.96, P.NEWSPRINT), (3.90, 1.92, P.PAPER_AGED),
             (3.16, 1.24, P.PAPER), (3.88, 1.26, P.NEWSPRINT)]
    for fi, (fy, fz, tint) in enumerate(fills):
        make_box(f"Cork_Fill_{fi}", (face + 0.002, fy, fz), (0.006, 0.10, 0.115), tint)
        make_cyl(f"Cork_FillPin_{fi}", (face - 0.004, fy, fz + 0.05), 0.006, 0.010,
                 (0.76, 0.22, 0.18, 1.0) if fi % 2 == 0 else P.METAL_STEEL, axis='X')
    # 1 · the Westport wedding-chapel Polaroid (Sam + Diego, 17/18,
    #     someone else's wedding clothes, both laughing)
    make_box("Cork_Polaroid", (face, 3.16, 1.84), (0.006, 0.088, 0.108), P.PAPER)
    make_box("Cork_Polaroid_Image", (face - 0.003, 3.16, 1.852), (0.002, 0.074, 0.072),
             (0.62, 0.58, 0.50, 1.0))
    make_cyl("Cork_Polaroid_Pin", (face - 0.007, 3.16, 1.90), 0.007, 0.012,
             (0.76, 0.22, 0.18, 1.0), axis='X')
    # 2 · the ticket stub — GALLATIN ROCK CLUB, Lake Charles,
    #     Jan 14, $8 (she went alone; he played it looking at her)
    make_box("Cork_TicketStub", (face, 3.60, 1.88), (0.006, 0.125, 0.055), P.PAPER_AGED)
    make_box("Cork_TicketStub_Stripe", (face - 0.003, 3.655, 1.88),
             (0.002, 0.014, 0.055), COL_RED_INK)
    make_cyl("Cork_TicketStub_Pin", (face - 0.007, 3.55, 1.905), 0.007, 0.012,
             P.METAL_STEEL, axis='X')
    # 3 · the frog-in-sunglasses receipt (Diego, on her first-ever
    #     sale receipt — four panels, "hello, sammy")
    make_box("Cork_FrogReceipt", (face, 3.34, 1.55), (0.006, 0.058, 0.165), P.PAPER)
    for pi2, pz2 in enumerate((1.60, 1.55, 1.50)):
        make_box(f"Cork_FrogPanel_{pi2}", (face - 0.003, 3.34, pz2),
                 (0.002, 0.040, 0.030), COL_INK)
    make_cyl("Cork_FrogReceipt_Pin", (face - 0.007, 3.34, 1.625), 0.007, 0.012,
             (0.76, 0.22, 0.18, 1.0), axis='X')
    # 4 · the graduation tassel — HCHS gold/white/blue, class of
    #     last spring (Jen brought it back to her at the register)
    make_cyl("Cork_Tassel_Pin", (face - 0.007, 3.82, 2.02), 0.007, 0.012,
             P.METAL_STEEL, axis='X')
    make_cyl("Cork_Tassel_Ring", (face - 0.004, 3.82, 1.985), 0.016, 0.008,
             COL_BRASS, axis='X', segments=8)
    for ti, (ty, tint) in enumerate([(-0.016, COL_TASSEL_GOLD),
                                     (0.0, COL_TASSEL_WHT),
                                     (0.016, COL_TASSEL_BLUE)]):
        make_box(f"Cork_Tassel_Strand_{ti}", (face - 0.002, 3.82 + ty, 1.885),
                 (0.008, 0.013, 0.185), tint)
    # 5 · the folded square — Diego's hand: "if you ever want me to
    #     stop, just say." She has never said.
    make_box("Cork_FoldedSquare", (face, 3.97, 1.60), (0.006, 0.068, 0.068), P.PAPER)
    make_box("Cork_FoldedSquare_Crease", (face - 0.003, 3.97, 1.60),
             (0.002, 0.068, 0.006), (0.80, 0.78, 0.72, 1.0))
    make_cyl("Cork_FoldedSquare_Pin", (face - 0.007, 3.97, 1.63), 0.007, 0.012,
             (0.76, 0.22, 0.18, 1.0), axis='X')
    # 6 · the postcard — Pensacola, 2019, her mother's hand ("Be
    #     brave. — Mom."). The handwriting match is the meta-game's
    #     to find, not the mesh's.
    make_box("Cork_Postcard", (face, 3.08, 1.40), (0.006, 0.148, 0.100), P.PAPER_AGED)
    make_box("Cork_Postcard_Stamp", (face - 0.003, 3.145, 1.435),
             (0.002, 0.022, 0.026), (0.66, 0.40, 0.34, 1.0))
    for ai in range(3):
        make_box(f"Cork_Postcard_Line_{ai}", (face - 0.003, 3.045, 1.425 - ai * 0.022),
                 (0.002, 0.058, 0.006), COL_INK)
    make_cyl("Cork_Postcard_Pin", (face - 0.007, 3.08, 1.44), 0.007, 0.012,
             P.METAL_STEEL, axis='X')
    # 7 · the Phase II model-home photo — held by THE NEXCORP LAPEL
    #     PIN (§III: she does not know where she got the pin). The
    #     one navy pin on the board.
    make_box("Cork_ModelHome", (face, 3.52, 1.34), (0.006, 0.120, 0.090), P.PAPER)
    make_box("Cork_ModelHome_House", (face - 0.003, 3.52, 1.325),
             (0.002, 0.076, 0.042), (0.58, 0.54, 0.48, 1.0))
    make_box("Cork_ModelHome_Roof", (face - 0.003, 3.52, 1.358),
             (0.002, 0.056, 0.016), (0.34, 0.28, 0.24, 1.0))
    make_cyl("Cork_NexCorpPin", (face - 0.007, 3.52, 1.375), 0.008, 0.014,
             P.BRAND_NAVY_HCE, axis='X')
    # 8 · the D'Ambrosio napkin — the road, the fence, the gate
    #     marked HALSEY · PRIVATE. Her father's pocket; she took it.
    make_box("Cork_Napkin", (face, 3.78, 1.42), (0.006, 0.110, 0.110), P.PAPER)
    make_box("Cork_Napkin_Road", (face - 0.003, 3.78, 1.395), (0.002, 0.088, 0.008),
             COL_INK)
    make_box("Cork_Napkin_Fence", (face - 0.003, 3.755, 1.435), (0.002, 0.050, 0.006),
             COL_INK)
    make_box("Cork_Napkin_Gate", (face - 0.003, 3.815, 1.435), (0.002, 0.014, 0.022),
             COL_RED_INK)
    make_cyl("Cork_Napkin_Pin", (face - 0.007, 3.78, 1.462), 0.007, 0.012,
             (0.76, 0.22, 0.18, 1.0), axis='X')


# ═════════════════════════════════════════════════════════════════
# NIGHTSTAND — between the bed head and the north wall. THE JUNK
# DRAWER (sam_miller.md §V) is the drawer: CLOSED. The drumstick,
# the sealed nineteen envelope, the ceramic frog, the NexCorp
# pencils, Skip's loyalty card, the paper crane, the guitar picks
# are all inside and stay unmodeled. On top: the bedside lamp
# (ch3:38 "Lamp off") and THE MIXTAPE (§I — "MIX FOR SAMMY · FOR
# THE 3 PM SHIFT", register-roll insert, Diego's block print, one
# red passage). Canon fixes no resting place for the tape; it sits
# where her hand lands in the dark.
# ═════════════════════════════════════════════════════════════════
def build_nightstand():
    nx, ny = -1.62, 4.68
    make_box("Nightstand_Body", (nx, ny, 0.26), (0.42, 0.40, 0.52), MILLER_OAK)
    make_box("Nightstand_Top", (nx, ny, 0.535), (0.46, 0.44, 0.03), MILLER_OAK_DK)
    make_box("Nightstand_Drawer", (nx, ny - 0.205, 0.40), (0.34, 0.015, 0.14),
             MILLER_OAK_DK)                        # THE junk drawer — closed (§V)
    make_cyl("Nightstand_Knob", (nx, ny - 0.22, 0.40), 0.013, 0.03, COL_BRASS, axis='Y')
    # Bedside lamp (ch3: "Lamp off." — the glow disc is for the
    # scene's practical to pick up; mood is scene-side)
    make_cyl("BedLamp_Base", (nx - 0.08, ny + 0.08, 0.565), 0.065, 0.025, MILLER_OAK_DK)
    make_cyl("BedLamp_Stem", (nx - 0.08, ny + 0.08, 0.70), 0.012, 0.26, COL_BRASS)
    make_cyl("BedLamp_Shade", (nx - 0.08, ny + 0.08, 0.885), 0.095, 0.13, COL_LINEN,
             segments=12)
    make_cyl("BedLamp_Glow", (nx - 0.08, ny + 0.08, 0.815), 0.040, 0.02, COL_LAMP_GLOW)
    # THE MIXTAPE — cassette flat by the lamp, insert tucked under
    make_box("Mixtape_Insert", (nx + 0.11, ny - 0.06, 0.553), (0.115, 0.075, 0.004),
             P.PAPER_AGED)
    make_box("Mixtape_Shell", (nx + 0.10, ny - 0.05, 0.562), (0.100, 0.064, 0.013),
             COL_CHARCOAL)
    make_box("Mixtape_Label", (nx + 0.10, ny - 0.05, 0.5695), (0.078, 0.044, 0.002),
             P.PAPER)
    make_box("Mixtape_RedTick", (nx + 0.10, ny - 0.072, 0.5700), (0.030, 0.006, 0.002),
             COL_RED_INK)                          # track 7 — "this one is yours"


# ═════════════════════════════════════════════════════════════════
# DESK ZONE — north end of the east wall, near the window (ch4:92 —
# the desk lamp reads as "the lamp in her own window" from the
# street). Where she writes the lists (ch4) and waits with the
# phone in her lap (ch2_coda). The chair is a Miller oak dinette
# chair — same _miller_chair the kitchen table seats, one carried
# upstairs years ago. On the desk: the lamp (glow ON), a NexCorp
# Residential Solutions pencil (§V — her father's 2016 box), a
# ballpoint, one loose sheet. NO laptop — her channel is the phone.
# ═════════════════════════════════════════════════════════════════
def build_desk_zone():
    dx = 1.62                        # desk center x (1.34..1.90)
    y0, y1 = 2.60, 3.80
    dy = (y0 + y1) / 2.0
    make_box("Desk_Top", (dx, dy, 0.735), (0.56, 1.20, 0.035), MILLER_OAK)
    make_box("Desk_Apron", (dx, dy, 0.685), (0.46, 1.08, 0.06), MILLER_OAK)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Desk_Leg_{li}", (dx + sx * 0.24, dy + sy * 0.55, 0.345),
                 (0.045, 0.045, 0.69), MILLER_OAK_DK)
    _miller_chair("DeskChair", 1.14, dy, 'E')      # the borrowed dinette chair
    # Desk lamp — north end, toward the window (ch4:26/92)
    make_cyl("DeskLamp_Base", (1.76, 3.62, 0.765), 0.065, 0.022, P.METAL_BLACK)
    make_cyl("DeskLamp_Stem", (1.76, 3.62, 0.92), 0.011, 0.29, P.METAL_BLACK)
    make_cyl("DeskLamp_Arm", (1.64, 3.62, 1.065), 0.010, 0.24, P.METAL_BLACK, axis='X')
    make_cyl("DeskLamp_Shade", (1.53, 3.62, 1.045), 0.055, 0.09,
             (0.30, 0.34, 0.44, 1.0), axis='X')
    make_cyl("DeskLamp_Glow", (1.485, 3.62, 1.045), 0.038, 0.012, COL_LAMP_GLOW,
             axis='X')
    # One loose sheet + the NexCorp pencil + a ballpoint
    make_box("Desk_Sheet", (1.55, 3.10, 0.754), (0.155, 0.21, 0.0015), P.PAPER)
    make_cyl("Desk_NexPencil", (1.50, 2.86, 0.756), 0.0042, 0.13,
             (0.24, 0.30, 0.44, 1.0), axis='Y')    # navy — Residential Solutions
    make_cyl("Desk_Pen", (1.72, 2.92, 0.756), 0.0045, 0.125, COL_INK, axis='Y')


# ═════════════════════════════════════════════════════════════════
# DRESSER — east wall, south of the desk (ch6:38 "Sam's phone, on
# her dresser, buzzes"). Oak three-drawer, phone face-up on top
# (sam_miller.md header: "Her phone is on the counter face-up" —
# the habit travels home with her).
# ═════════════════════════════════════════════════════════════════
def build_dresser():
    fx, fy = 1.64, 1.30
    make_box("Dresser_Body", (fx, fy, 0.525), (0.50, 0.90, 1.05), MILLER_OAK)
    make_box("Dresser_Top", (fx - 0.01, fy, 1.065), (0.54, 0.94, 0.03), MILLER_OAK_DK)
    make_box("Dresser_Kick", (fx - 0.02, fy, 0.04), (0.48, 0.86, 0.08), MILLER_OAK_DK)
    for ri, rz in enumerate((0.30, 0.60, 0.90)):
        make_box(f"Dresser_Drawer_{ri}", (fx - 0.26, fy, rz), (0.02, 0.80, 0.22),
                 MILLER_OAK)
        for ki, sgn in enumerate((-1, +1)):
            make_cyl(f"Dresser_Knob_{ri}_{ki}", (fx - 0.275, fy + sgn * 0.22, rz),
                     0.013, 0.03, COL_BRASS, axis='X')
    # THE PHONE — face-up (ch6)
    make_box("Phone_Slab", (fx - 0.06, fy - 0.18, 1.086), (0.072, 0.148, 0.012),
             COL_CHARCOAL)
    make_box("Phone_Screen", (fx - 0.06, fy - 0.18, 1.0935), (0.062, 0.132, 0.002),
             (0.12, 0.13, 0.16, 1.0))


# ═════════════════════════════════════════════════════════════════
# CLOSET — west wall, south bay (ch4:121 "She goes to the closet.
# She gets dressed for work."). Bypass doors, both panels slid
# south, north half open: the spare Kwik Stop pinks-and-blues
# uniform polo on the rod (the uniform per sam_miller.md header),
# flannel, denim, a grey tee, sneakers below.
# ═════════════════════════════════════════════════════════════════
def build_closet():
    wx = -ROOM_W / 2.0 + 0.10        # interior wall face x -1.9
    for pi, py in enumerate((0.68, 2.32)):
        make_box(f"Closet_EndWall_{pi}", (wx + 0.30, py, 1.30), (0.60, 0.04, 2.60),
                 COL_CORNFLOWER)
    make_box("Closet_Header", (-1.33, 1.50, 2.30), (0.06, 1.68, 0.60), COL_CORNFLOWER)
    make_box("Closet_Track", (-1.345, 1.50, 1.985), (0.045, 1.60, 0.03), P.METAL_STEEL)
    make_box("Closet_FloorStrip", (wx + 0.30, 1.50, 0.004), (0.58, 1.64, 0.008),
             COL_CARPET_SH)
    # Bypass panels — stacked over the south half
    make_box("Closet_PanelOuter", (-1.335, 1.10, 1.00), (0.028, 0.80, 1.94),
             MILLER_TRIM)
    make_box("Closet_PanelInner", (-1.368, 1.14, 1.00), (0.028, 0.80, 1.94),
             (0.88, 0.86, 0.80, 1.0))
    make_cyl("Closet_FingerCup", (-1.318, 1.44, 1.00), 0.022, 0.008,
             (0.62, 0.60, 0.56, 1.0), axis='X')
    # Rod + the hanging row — THE UNIFORM POLO first (pink body,
    # blue collar band), then civilian clothes
    make_cyl("Closet_Rod", (-1.62, 1.50, 1.78), 0.015, 1.56, P.METAL_STEEL, axis='Y')
    make_cyl("Closet_Hanger_Polo", (-1.62, 1.62, 1.795), 0.008, 0.05, P.METAL_STEEL)
    make_box("Closet_UniformPolo", (-1.62, 1.62, 1.42), (0.11, 0.15, 0.64),
             COL_POLO_PINK)
    make_box("Closet_UniformPolo_Collar", (-1.62, 1.62, 1.71), (0.112, 0.152, 0.06),
             COL_POLO_BLUE)
    for gi, gy in enumerate((1.80, 1.98, 2.16)):
        glen = (0.80, 0.68, 0.52)[gi]
        make_cyl(f"Closet_Hanger_{gi}", (-1.62, gy, 1.795), 0.008, 0.05, P.METAL_STEEL)
        make_box(f"Closet_Garment_{gi}", (-1.62, gy, 1.74 - glen / 2.0),
                 (0.11, 0.15, glen), GARMENT_TINTS[gi % len(GARMENT_TINTS)])
    for shi, sy in enumerate((1.70, 1.86)):
        make_box(f"Closet_Sneaker_{shi}", (-1.66, sy, 0.055), (0.24, 0.10, 0.09),
                 (0.82, 0.80, 0.76, 1.0))
        make_box(f"Closet_SneakerSole_{shi}", (-1.66, sy, 0.016), (0.25, 0.11, 0.03),
                 (0.94, 0.93, 0.90, 1.0))


# ═════════════════════════════════════════════════════════════════
# CEILING — THE CEILING FAN (ch0/ch1/ch5/ch15 — the fan that
# clicks on the third rotation; the EAST blade hangs 4 mm low, the
# click's cause), frosted light kit, pull chains; smoke detector,
# HVAC register. House hardware only.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_fixtures():
    fx, fy = 0.0, 2.50
    make_cyl("Fan_Canopy", (fx, fy, CEIL - 0.02), 0.075, 0.04, COL_BRASS, segments=10)
    make_cyl("Fan_Downrod", (fx, fy, CEIL - 0.13), 0.012, 0.18, COL_BRASS)
    make_cyl("Fan_Motor", (fx, fy, CEIL - 0.265), 0.105, 0.10, MILLER_OAK_DK,
             segments=12)
    blades = [("N", 0.0, +0.34, 0.16, 0.54, 0.0),
              ("S", 0.0, -0.34, 0.16, 0.54, 0.0),
              ("W", -0.34, 0.0, 0.54, 0.16, 0.0),
              ("E", +0.34, 0.0, 0.54, 0.16, -0.004)]   # the low blade — the click
    for nm, bxo, byo, bsx, bsy, dz in blades:
        make_box(f"Fan_Blade_{nm}", (fx + bxo, fy + byo, CEIL - 0.315 + dz),
                 (bsx, bsy, 0.014), MILLER_OAK)
        make_box(f"Fan_Iron_{nm}", (fx + bxo * 0.38, fy + byo * 0.38,
                 CEIL - 0.298 + dz), (0.10 if bsx > bsy else 0.05,
                 0.05 if bsx > bsy else 0.10, 0.012), COL_BRASS)
    make_cyl("Fan_LightKit", (fx, fy, CEIL - 0.355), 0.075, 0.08,
             (0.94, 0.92, 0.86, 1.0), segments=12)
    for pi, (po, plen) in enumerate([(0.05, 0.16), (-0.05, 0.10)]):
        make_cyl(f"Fan_PullChain_{pi}", (fx + po, fy - 0.06, CEIL - 0.40 - plen / 2.0),
                 0.003, plen, COL_BRASS, segments=6)
    make_smoke_detector("Smoke", (-0.9, 1.2, CEIL))
    make_hvac_vent("HVAC", (0.9, 0.8, CEIL), width=0.50, depth=0.30)


def main():
    clear_scene()
    build_shell()
    build_door()
    build_window()
    build_exterior_front()
    build_bed_zone()
    build_corkboard()
    build_nightstand()
    build_desk_zone()
    build_dresser()
    build_closet()
    build_ceiling_fixtures()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/sam_bedroom.glb"))
    print(f"\n[build_sam_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
