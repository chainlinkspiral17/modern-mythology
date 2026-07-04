"""Caldwell Kitchen (night) — Linda Caldwell's house, lot 7 Phase I,
the Caldwell cul-de-sac, Harmony Creek Estates — vol6 hero locale
(2 VN bg refs: vol6_ch5_radio "1776 kHz", vol6_ch12_porch "The
Staying").

The GRANDMOTHER'S kitchen at night — the room Maya passes through
on her way to bed: a glass of water, a sandwich at the counter, the
light she turns off last. One house, three hero-passed rooms in
this directory (porch / kitchen / radio room) plus Maya's bedroom
upstairs (build_maya_bedroom.py) — see the shared KEEP-IN-SYNC
palette block below. Canon baked in:

  · vol6_ch5_radio:139 — "Maya, in the kitchen, pouring herself a
    glass of water before bed, pauses at the window. She hears the
    dogs." THE WINDOW over the sink is the hero: a real opening
    (no glass, playbook rule), and through it, beyond the back
    fence, THE WATER TOWER at the end of Gallatin — the repeater
    that picks up her grandmother's 1776 kHz Morse and rebroadcasts
    it into the subdivision grid (vol6_ch1_maya_bedroom:44), the
    reason the dogs bark. The tower hums its subaudible B-flat at
    eleven-seventeen (ch5:125) — the wall clock over the window is
    frozen at 11:17.
  · vol6_ch5_radio:139 / ch21:312 — the glass of water: in the
    drying rack at the sink, where it lives between nights.
  · vol6_ch12_porch:342 — "She makes a sandwich. She eats it at the
    kitchen counter." (ch21:312 — "standing at the counter") — the
    bread board, the loaf, the plate and butter knife on the
    counter's east run.
  · vol6_ch12_porch:438 — Linda remembers "porch, granddaughter at
    the shop, soup in the kitchen": THE SOUP POT sits on the range,
    lid on, done for the night.
  · vol6_ch12/ch21 — the iced tea Linda pours in advance: the
    ceramic pitcher on the counter (the glasses themselves are out
    on the porch — build_caldwell_porch_night.py).
  · vol6_ch12_porch:398 — "She turns off the kitchen light." — one
    house dome fixture over the table (NOT commercial fluorescents;
    the scaffold's tube fixtures were Kwik Stop vocabulary and are
    gone — same lesson as build_maya_bedroom.py).
  · maya_daigle.md §IV (mixtape unlock) — "the audio diorama of
    Maya reading the General Store pages aloud at her grandmother's
    kitchen table at 1:14 AM": THE KITCHEN TABLE, oak, two chairs —
    a household of two.
  · _VOL6_WIKI elders'-network entry (see name flag below) — the
    grandmother "receives NexCorp Residential Solutions envelopes
    from a sender she has never seen": one unopened NexCorp
    envelope on the table.
  · maya_daigle.md issue #22 — "the kettle is on" is the passphrase
    Maya's father chose for this house: the kettle sits on the back
    burner (register-true for the house; the phrase's referent).

Canon-NEGATIVES honored (what this kitchen does NOT have):
  · NO RADIO. The 1776 kHz shortwave is UPSTAIRS on the
    grandmother's windowsill (ch12:454). vol6_ch10_home:38
    explicitly firewalls the OTHER grandmother's windowsill kitchen
    radio ("nothing to do with the upstairs shortwave at Linda
    Caldwell's") — that one is the RAMOS house
    (grandmother_kitchen_morning). No vocabulary borrowed from it.
  · No boombox — the old dual-cassette boombox's resting place is
    unspecified (Maya carried it to this table once, at 1:14 AM,
    §IV); not baked anywhere.
  · No landline wall phone (that's Miller-kitchen canon — not
    imported), no dishwasher drama, no Cuisinart: Linda's kitchen
    is not Bianca's.
  · No vacuum — the 4/4 vacuuming happens in the LIVING ROOM
    (vol6_ch1_maya_bedroom:74).
  · No commercial fluorescents, no drop-tile grid, no crown molding
    (1991 tract house).

NAME-DEPENDENCY FLAG (same drift build_maya_bedroom.py flags): the
scene JSONs name the grandmother Ms. LINDA CALDWELL on "the
Caldwell cul-de-sac" (vol6_ch5_radio:121 files her under
GRANDMOTHER, CALDWELL, LINDA); the older lore docs
(lore/planned_community/maya_daigle.md, lore/_VOL6_WIKI.md elders'
list) say CONNIE DAIGLE. The JSONs are treated as current; the
wiki's Connie facts (WUFR 4/4, the NexCorp envelopes) are read as
Linda facts. Secondary drift, noted: vol6_ch2_maya_bedroom:42 says
"the shortwave DOWNSTAIRS" but ch5 ("She goes upstairs. She
knocks"), ch10:38 ("the upstairs shortwave") and ch12:402-406 (she
climbs the stairs past the bedroom door) all put it upstairs —
upstairs wins on weight.

Shell footprint kept from the scaffold (6 x 5, CEIL 2.6, gap
x -1..+1 in the south wall = the hall doorway the Background3D
camera preset (0, 2.30, +0.5 / yaw 180 / fov 60) shoots through).
Stage-north = the BACK of the house (the porch and cul-de-sac are
at the front — build_caldwell_porch_night.py). Window is a REAL
OPENING with frame + sash + muntins, no glass (playbook
no-transparency rule).
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
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.6

# ═════════════════════════════════════════════════════════════════
# CALDWELL HOUSE — SHARED PALETTE + NIGHT VOCABULARY (⚠ KEEP IN SYNC)
# This block is declared IDENTICALLY in build_caldwell_porch_night.py,
# build_caldwell_kitchen_night.py and build_caldwell_radio_room_night.py
# — three rooms of ONE house (lot 7 Phase I, the Caldwell cul-de-sac).
# md5 the block between these ═ markers when touching any sibling.
# The CALDWELL_* constants also exist as locals in build_maya_bedroom.py
# (Maya's room is upstairs in this house); its docstring asks for them
# to be graduated into a shared block — the values here MATCH that file.
# FOLLOW-UP: next time build_maya_bedroom.py is touched, replace its
# local CALDWELL_* declarations with this block verbatim.
# ═════════════════════════════════════════════════════════════════
CALDWELL_INT_WALL  = (0.90, 0.86, 0.75, 1.0)   # 1991 builder warm white
CALDWELL_BASEBOARD = (0.46, 0.35, 0.24, 1.0)
CALDWELL_TRIM      = (0.93, 0.91, 0.85, 1.0)   # painted door/window trim
CALDWELL_CEIL_YEL  = (0.93, 0.89, 0.70, 1.0)   # THE pale yellow ceiling
CALDWELL_PINE      = (0.72, 0.56, 0.36, 1.0)   # original pine, worn honey
CALDWELL_PINE_SEAM = (0.50, 0.37, 0.23, 1.0)
CALDWELL_SIDING    = (0.84, 0.80, 0.70, 1.0)   # exterior lap siding
CALDWELL_ROOF      = (0.33, 0.27, 0.23, 1.0)   # shingle
# Night-exterior + household vocabulary shared by the three _night
# rooms (values match build_maya_bedroom.py's locals — same street,
# same night):
COL_SIDING_SEAM = (0.70, 0.66, 0.56, 1.0)  # lap-siding shadow lines
COL_NIGHT_LAWN  = (0.22, 0.28, 0.18, 1.0)  # lawn at night
COL_ASPHALT     = (0.16, 0.16, 0.17, 1.0)
COL_CONCRETE    = (0.50, 0.49, 0.45, 1.0)
COL_CEDAR       = (0.20, 0.30, 0.20, 1.0)  # the cedar across the cul-de-sac
COL_CEDAR_DK    = (0.15, 0.24, 0.16, 1.0)
COL_PORCHBULB   = (1.00, 0.88, 0.60, 1.0)  # porch-light warm, ON
COL_WINDOW_DARK = (0.09, 0.11, 0.14, 1.0)  # unlit panes at night
COL_WINDOW_LIT  = (0.42, 0.38, 0.28, 1.0)  # a faintly lit pane
COL_GELLER_BODY = (0.55, 0.51, 0.45, 1.0)  # the Geller house massing
COL_WOOD        = (0.50, 0.37, 0.24, 1.0)  # household furniture pine/oak
COL_WOOD_DK     = (0.31, 0.23, 0.16, 1.0)
COL_BRASS       = (0.70, 0.57, 0.30, 1.0)
COL_LAMP_GLOW   = (0.98, 0.88, 0.62, 1.0)  # practicals: warm bulb glow
COL_CERAMIC     = (0.92, 0.90, 0.84, 1.0)  # plates / mugs / pitcher
COL_TEA         = (0.62, 0.40, 0.18, 1.0)  # Linda's iced tea, amber
COL_TOWER       = (0.30, 0.32, 0.36, 1.0)  # the water tower, moonlit
COL_TOWER_DK    = (0.20, 0.22, 0.26, 1.0)
PAL_WALL = {"wall": CALDWELL_INT_WALL, "baseboard": CALDWELL_BASEBOARD}
# ═════════ end shared block ══════════════════════════════════════

# Kitchen-only palette — Linda's register: 1991 tract bones kept
# original for thirty-five years. Sage laminate, oak cabinets worn
# at the knobs, peach gingham cafe curtains.
COL_VINYL       = (0.80, 0.74, 0.62, 1.0)   # sheet-vinyl floor
COL_VINYL_SEAM  = (0.60, 0.53, 0.42, 1.0)
COL_CABINET     = (0.58, 0.43, 0.27, 1.0)   # original oak fronts
COL_CABINET_DK  = (0.36, 0.26, 0.17, 1.0)
COL_LAMINATE    = (0.62, 0.68, 0.58, 1.0)   # sage-green laminate
COL_APPLIANCE   = (0.89, 0.87, 0.80, 1.0)   # almond, 1991 originals
COL_CURTAIN     = (0.86, 0.64, 0.54, 1.0)   # peach gingham cafe curtain
COL_CURTAIN_DK  = (0.72, 0.52, 0.44, 1.0)
COL_STEEL_DK    = (0.44, 0.46, 0.48, 1.0)
COL_FENCE       = (0.38, 0.33, 0.26, 1.0)   # back fence at night
COL_FENCE_SEAM  = (0.27, 0.23, 0.18, 1.0)
COL_BREAD       = (0.78, 0.62, 0.40, 1.0)
COL_SOUP_POT    = (0.82, 0.80, 0.76, 1.0)   # enamel stock pot

GRADE_Z = -0.40           # back-yard grade outside the window
WIN_W = 1.50              # window opening x -0.75..+0.75
WIN_SILL = 0.95
WIN_HEAD = 2.15


# ═════════════════════════════════════════════════════════════════
# SHELL — vinyl floor, warm-white walls, flat drywall ceiling
# (house, not store: no grid, no stains, no fluorescents), the hall
# doorway casing in the scaffold gap, REAL window opening in the
# north (back) wall.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_VINYL, "seam": COL_VINYL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall — window opening x -0.75..+0.75, sill 0.95, head 2.15
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20     # 2.45
    seg_cx = WIN_W / 2.0 + seg_len / 2.0              # 1.975
    make_wall("Wall_N_W", (-seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_SillFill", (0.0, ROOM_D, WIN_SILL / 2.0), (WIN_W, 0.20, WIN_SILL),
             CALDWELL_INT_WALL)
    make_box("Wall_N_HeadFill", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.20, CEIL - WIN_HEAD), CALDWELL_INT_WALL)
    # South wall — scaffold hall gap x -1..+1 kept (camera doorway)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             CALDWELL_INT_WALL)
    # Hall doorway casing — through to the front door and the stairs
    for sgn in (-1, +1):
        make_box(f"HallDoor_Jamb_{sgn:+d}", (sgn * 1.03, 0.0, 1.00), (0.10, 0.26, 2.00),
                 CALDWELL_TRIM)
    make_box("HallDoor_Head", (0.0, 0.0, 2.05), (2.26, 0.26, 0.10), CALDWELL_TRIM)
    # Flat drywall ceiling — a house ceiling, painted once, in 1991
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": (0.93, 0.91, 0.85, 1.0)},
                 with_grid=False, with_stains=False)


# ═════════════════════════════════════════════════════════════════
# WINDOW — over the sink, the back-yard window Maya pauses at when
# the dogs bark (vol6_ch5_radio:139). Real opening: painted
# double-hung frame, meeting rail + muntins, casing, stool, apron;
# peach gingham CAFE curtains on the lower sash + valance (Linda's
# register). The clock above is frozen at 11:17 — the minute the
# water tower hums (ch5:125).
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D
    make_box("Win_FrameT", (0.0, wy, WIN_HEAD - 0.03), (WIN_W, 0.14, 0.06),
             CALDWELL_TRIM)
    make_box("Win_FrameB", (0.0, wy, WIN_SILL + 0.03), (WIN_W, 0.14, 0.06),
             CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Jamb_{sgn:+d}", (sgn * (WIN_W / 2.0 - 0.03), wy, 1.55),
                 (0.06, 0.14, 1.20), CALDWELL_TRIM)
    make_box("Win_MeetingRail", (0.0, wy, 1.56), (WIN_W - 0.08, 0.10, 0.06),
             CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Muntin_{sgn:+d}", (sgn * 0.25, wy - 0.02, 1.86),
                 (0.035, 0.06, 0.54), CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Casing_{sgn:+d}", (sgn * (WIN_W / 2.0 + 0.09), wy - 0.105, 1.55),
                 (0.10, 0.05, 1.40), CALDWELL_TRIM)
    make_box("Win_CasingHead", (0.0, wy - 0.105, WIN_HEAD + 0.08),
             (WIN_W + 0.28, 0.05, 0.10), CALDWELL_TRIM)
    make_box("Win_Stool", (0.0, wy - 0.135, WIN_SILL + 0.02), (WIN_W + 0.30, 0.16, 0.04),
             CALDWELL_TRIM)
    make_box("Win_Apron", (0.0, wy - 0.105, WIN_SILL - 0.05), (WIN_W + 0.16, 0.05, 0.09),
             CALDWELL_TRIM)
    # Cafe curtains — brass rod at the meeting rail, two gingham
    # panels on the lower sash, valance at the head
    make_cyl("Cafe_Rod", (0.0, wy - 0.16, 1.58), 0.010, 1.62, COL_BRASS, axis='X',
             segments=8)
    for sgn in (-1, +1):
        make_box(f"Cafe_Panel_{sgn:+d}", (sgn * 0.44, wy - 0.155, 1.27),
                 (0.42, 0.028, 0.58), COL_CURTAIN)
        make_box(f"Cafe_Fold_{sgn:+d}", (sgn * 0.36, wy - 0.172, 1.24),
                 (0.12, 0.016, 0.52), COL_CURTAIN_DK)
    make_box("Cafe_Valance", (0.0, wy - 0.155, 2.06), (1.74, 0.028, 0.22), COL_CURTAIN)
    # The clock — frozen at 11:17, the hum minute (vol6_ch5:125)
    make_wall_clock("Clock", (0.0, wy - 0.14, 2.38), frozen_hour=11, frozen_min=17)


# ═════════════════════════════════════════════════════════════════
# COUNTER RUN — original 1991 oak base + upper cabinets along the
# north wall, sage laminate. Sink under the window; the drying rack
# with THE WATER GLASS (ch5:139, ch21:312); range west with THE
# SOUP POT (ch12:438) + THE KETTLE ("the kettle is on" — issue
# #22's passphrase); the bread board with loaf + plate + butter
# knife (the sandwich, ch12:342 / ch21:312); the iced-tea pitcher.
# ═════════════════════════════════════════════════════════════════
def build_counter_run():
    # Base cabinets: x -2.9..+1.3, front face y ~5.41
    make_box("Base_Body", (-0.80, 4.7, 0.445), (4.20, 0.58, 0.79), COL_CABINET)
    make_box("Base_Kick", (-0.80, 4.44, 0.05), (4.10, 0.03, 0.10), COL_CABINET_DK)
    make_box("Counter_Top", (-0.80, 4.69, 0.89), (4.27, 0.66, 0.04), COL_LAMINATE)
    make_box("Counter_Edge", (-0.80, 4.375, 0.89), (4.27, 0.03, 0.04), COL_CABINET_DK)
    make_box("Backsplash", (-0.80, 4.885, 1.00), (4.20, 0.03, 0.18), COL_LAMINATE)
    # Door + drawer fronts (sink bay at x -0.4..+0.4 gets doors only)
    doors = [(-2.65, 0.44), (-1.35, 0.46), (-0.42, 0.40), (0.02, 0.40),
             (0.55, 0.44), (1.05, 0.44)]
    for di, (dx, dw) in enumerate(doors):
        make_box(f"Base_Door_{di}", (dx, 5.415, 0.40), (dw - 0.04, 0.02, 0.54),
                 COL_CABINET)
        make_cyl(f"Base_Knob_{di}", (dx + dw / 2.0 - 0.06, 5.40, 0.62), 0.014, 0.03,
                 COL_BRASS, axis='Y')
        if abs(dx + 0.2) > 0.7:   # drawers everywhere except the sink bay
            make_box(f"Base_Drawer_{di}", (dx, 5.415, 0.775), (dw - 0.04, 0.02, 0.14),
                     COL_CABINET)
            make_cyl(f"Base_DrawerKnob_{di}", (dx, 5.40, 0.775), 0.014, 0.03,
                     COL_BRASS, axis='Y')
    # Upper cabinets flanking the window (clear of the hood bay
    # x -2.43..-1.67 — the Gas & Go interpenetration lesson)
    uppers = [("W0", -2.70, 0.44, 1.90, 0.76), ("W1", -1.28, 0.72, 1.90, 0.76),
              ("E0", 1.20, 0.85, 1.90, 0.76)]
    for nm, ux, uw, uz, uh in uppers:
        make_box(f"Upper_{nm}", (ux, 5.835, uz), (uw, 0.33, uh), COL_CABINET)
        make_box(f"Upper_{nm}_Seam", (ux, 5.665, uz), (0.012, 0.012, uh - 0.06),
                 COL_CABINET_DK)
        make_cyl(f"Upper_{nm}_Knob", (ux - 0.06, 5.66, uz - uh / 2.0 + 0.10),
                 0.013, 0.03, COL_BRASS, axis='Y')
    # Sink under the window + faucet + dish soap
    make_box("Sink_Rim", (0.0, 4.7, 0.925), (0.82, 0.52, 0.02), P.METAL_STEEL)
    make_box("Sink_Basin", (0.0, 4.7, 0.83), (0.70, 0.42, 0.17), P.METAL_STEEL,
             open_faces={'+Z'})
    make_box("Sink_BasinFloor", (0.0, 4.7, 0.752), (0.66, 0.38, 0.012), COL_STEEL_DK)
    make_cyl("Faucet_Base", (0.0, 4.92, 0.955), 0.030, 0.04, P.METAL_STEEL)
    make_cyl("Faucet_Riser", (0.0, 4.92, 1.06), 0.016, 0.20, P.METAL_STEEL)
    make_cyl("Faucet_Spout", (0.0, 4.82, 1.15), 0.014, 0.22, P.METAL_STEEL, axis='Y')
    make_box("Faucet_Handle", (0.10, 4.92, 1.17), (0.08, 0.02, 0.02), P.METAL_STEEL)
    make_cyl("DishSoap", (0.34, 4.9, 0.985), 0.022, 0.13, (0.72, 0.60, 0.30, 1.0))
    # Drying rack east of the sink — THE WATER GLASS lives here
    # between nights (ch5:139: "pouring herself a glass of water
    # before bed"), plus the supper plate
    make_box("DryRack_Tray", (0.85, 4.72, 0.925), (0.32, 0.40, 0.015), CALDWELL_TRIM)
    for wi in range(4):
        make_box(f"DryRack_Wire_{wi}", (0.73 + wi * 0.08, 5.72, 0.985),
                 (0.010, 0.36, 0.09), P.METAL_STEEL)
    make_cyl("DryRack_WaterGlass", (0.80, 4.62, 0.99), 0.033, 0.115,
             (0.74, 0.78, 0.76, 1.0), segments=10)
    make_cyl("DryRack_Plate", (0.90, 4.76, 1.03), 0.10, 0.014, COL_CERAMIC, axis='Y',
             segments=12)
    # Range west — THE SOUP POT front (ch12:438, lid on), THE KETTLE
    # back ("the kettle is on", issue #22), hood above
    make_box("Range_Body", (-2.05, 4.67, 0.45), (0.76, 0.64, 0.90), COL_APPLIANCE)
    make_box("Range_Cooktop", (-2.05, 4.67, 0.915), (0.76, 0.64, 0.02), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([(-0.19, -0.16), (0.19, -0.16), (-0.19, 0.16),
                                   (0.19, 0.16)]):
        make_cyl(f"Range_Burner_{bi}", (-2.05 + bx, 5.67 + by, 0.930), 0.085, 0.010,
                 (0.12, 0.11, 0.10, 1.0), segments=10)
    make_box("Range_Backguard", (-2.05, 4.955, 0.98), (0.76, 0.05, 0.12), COL_APPLIANCE)
    for ki in range(4):
        make_cyl(f"Range_Knob_{ki}", (-2.29 + ki * 0.16, 5.925, 0.99), 0.018, 0.025,
                 P.METAL_BLACK, axis='Y')
    make_box("Range_OvenDoor", (-2.05, 4.345, 0.46), (0.70, 0.02, 0.52), COL_APPLIANCE)
    make_box("Range_OvenWindow", (-2.05, 4.335, 0.50), (0.42, 0.012, 0.22),
             P.METAL_BLACK)
    make_box("Range_OvenHandle", (-2.05, 4.33, 0.76), (0.72, 0.03, 0.03), P.METAL_STEEL)
    make_box("Hood_Body", (-2.05, 4.77, 1.96), (0.76, 0.44, 0.14), COL_APPLIANCE)
    make_box("Hood_Lip", (-2.05, 4.56, 1.90), (0.76, 0.03, 0.05), P.METAL_STEEL)
    # The soup pot — enamel, lid on, done for the night (ch12:438)
    make_cyl("SoupPot_Body", (-2.24, 4.51, 1.015), 0.135, 0.17, COL_SOUP_POT,
             segments=12)
    make_cyl("SoupPot_Lid", (-2.24, 4.51, 1.108), 0.140, 0.018, COL_SOUP_POT,
             segments=12)
    make_cyl("SoupPot_LidKnob", (-2.24, 4.51, 1.132), 0.022, 0.03, P.METAL_BLACK)
    for sgn in (-1, +1):
        make_box(f"SoupPot_Handle_{sgn:+d}", (-2.24 + sgn * 0.15, 5.51, 1.05),
                 (0.03, 0.07, 0.02), P.METAL_BLACK)
    # The kettle on the back burner (issue #22's passphrase)
    make_cyl("Kettle_Body", (-1.86, 4.83, 1.00), 0.105, 0.13, COL_APPLIANCE,
             segments=12)
    make_cyl("Kettle_Lid", (-1.86, 4.83, 1.075), 0.055, 0.025, COL_APPLIANCE,
             segments=10)
    make_cyl("Kettle_Spout", (-1.74, 4.83, 1.02), 0.020, 0.10, COL_APPLIANCE, axis='X',
             segments=8)
    make_box("Kettle_HandleUp", (-1.86, 4.83, 1.13), (0.14, 0.024, 0.02), P.METAL_BLACK)
    # The sandwich counter, east run: bread board, loaf, plate +
    # butter knife (ch12:342 / ch21:312 — she eats standing here)
    make_box("BreadBoard", (1.15, 4.68, 0.918), (0.40, 0.30, 0.016), COL_WOOD)
    make_box("BreadLoaf", (1.06, 4.7, 0.982), (0.16, 0.24, 0.11), COL_BREAD)
    make_box("BreadLoaf_Heel", (1.06, 4.555, 0.965), (0.14, 0.02, 0.08),
             (0.90, 0.82, 0.64, 1.0))
    make_cyl("SandwichPlate", (1.32, 4.62, 0.932), 0.085, 0.012, COL_CERAMIC,
             segments=12)
    make_box("ButterKnife_Blade", (1.32, 4.78, 0.932), (0.022, 0.10, 0.006),
             P.METAL_STEEL)
    make_box("ButterKnife_Handle", (1.32, 4.86, 0.934), (0.018, 0.06, 0.012),
             COL_WOOD_DK)
    # The iced-tea pitcher — the tea Linda pours in advance
    # (ch12/ch21; the glasses are out on the porch)
    make_cyl("TeaPitcher_Body", (-1.35, 4.76, 1.03), 0.075, 0.22, COL_CERAMIC,
             segments=12)
    make_cyl("TeaPitcher_Band", (-1.35, 4.76, 1.10), 0.077, 0.03, COL_TEA, segments=12)
    make_box("TeaPitcher_Handle", (-1.25, 4.76, 1.03), (0.020, 0.016, 0.14),
             COL_CERAMIC)
    # Canisters under the west uppers (flour / sugar / coffee row)
    for ci in range(3):
        make_cyl(f"Canister_{ci}", (-2.75 + ci * 0.17, 5.82, 0.985 + (2 - ci) * 0.01),
                 0.055, 0.15 + (2 - ci) * 0.02, COL_CERAMIC, segments=10)
        make_cyl(f"Canister_{ci}_Lid", (-2.75 + ci * 0.17, 5.82,
                 1.068 + (2 - ci) * 0.02, ), 0.058, 0.014, COL_WOOD, segments=10)


# ═════════════════════════════════════════════════════════════════
# FRIDGE — almond top-freezer, east of the counter run. On the
# door: the HCE newsletter and a small row of magnets. (No shift
# schedules, no crayon drawings — that's the Miller fridge. This
# household's paper goes on the TABLE: the NexCorp envelope.)
# ═════════════════════════════════════════════════════════════════
def build_fridge():
    fx, fy = 2.35, 5.55
    make_box("Fridge_Body", (fx, fy, 0.86), (0.82, 0.72, 1.72), COL_APPLIANCE)
    make_box("Fridge_DoorSeam", (fx, fy - 0.365, 1.28), (0.80, 0.015, 0.03),
             COL_STEEL_DK)
    make_box("Fridge_HandleTop", (fx - 0.35, fy - 0.375, 1.46), (0.035, 0.035, 0.26),
             COL_STEEL_DK)
    make_box("Fridge_HandleBot", (fx - 0.35, fy - 0.375, 0.86), (0.035, 0.035, 0.50),
             COL_STEEL_DK)
    make_box("Fridge_Grille", (fx, fy - 0.365, 0.06), (0.78, 0.02, 0.10), COL_STEEL_DK)
    # The HCE newsletter, magneted up (canon navy + cream)
    make_box("Fridge_HCENews", (fx + 0.15, fy - 0.373, 1.56), (0.16, 0.012, 0.22),
             P.BRAND_NAVY_HCE)
    make_box("Fridge_HCENews_Head", (fx + 0.15, fy - 0.380, 1.64), (0.14, 0.006, 0.045),
             P.BRAND_NAVY_TXT)
    for mi, (mx, mz) in enumerate([(-0.26, 1.68), (0.28, 1.36), (-0.08, 1.14),
                                   (0.20, 0.98)]):
        make_box(f"Fridge_Magnet_{mi}", (fx + mx, fy - 0.376, mz), (0.035, 0.008, 0.045),
                 P.SNACK_TINTS[mi % len(P.SNACK_TINTS)])


# ═════════════════════════════════════════════════════════════════
# TABLE — the kitchen table of a household of two: oak, TWO chairs
# (Linda's and Maya's — maya_daigle.md §IV puts Maya here reading
# General Store aloud at 1:14 AM). On it: the unopened NexCorp
# Residential Solutions envelope (_VOL6_WIKI elders'-network entry),
# salt + pepper, the napkin holder.
# ═════════════════════════════════════════════════════════════════
def build_table_zone():
    tx, ty = 0.55, 2.70
    make_box("Table_Top", (tx, ty, 0.745), (0.90, 1.35, 0.045), COL_WOOD)
    make_box("Table_Apron", (tx, ty, 0.685), (0.78, 1.22, 0.07), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Table_Leg_{li}", (tx + sx * 0.38, ty + sy * 0.58, 0.34),
                 (0.055, 0.055, 0.68), COL_WOOD_DK)
    # Two chairs — Linda west, Maya east (a household of two)
    for nm, cx, dxs in (("Linda", tx - 0.72, +1), ("Maya", tx + 0.72, -1)):
        make_box(f"Chair_{nm}_Seat", (cx, ty, 0.45), (0.42, 0.42, 0.045), COL_WOOD)
        for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
            make_cyl(f"Chair_{nm}_Leg_{li}", (cx + sx * 0.17, ty + sy * 0.17, 0.225),
                     0.019, 0.45, COL_WOOD_DK)
        bx = cx - dxs * 0.20
        for pi, sgn in enumerate((-1, +1)):
            make_cyl(f"Chair_{nm}_Post_{pi}", (bx, ty + sgn * 0.17, 0.70), 0.017, 0.50,
                     COL_WOOD)
        for si, sz in enumerate((0.74, 0.90)):
            make_box(f"Chair_{nm}_Slat_{si}", (bx, ty, sz), (0.032, 0.38, 0.085),
                     COL_WOOD)
    top = 0.7675
    # THE NEXCORP ENVELOPE — unopened, from a sender she has never
    # seen (_VOL6_WIKI elders' network; Linda facts, see name flag)
    make_box("NexEnvelope", (tx - 0.14, ty + 0.34, top + 0.006), (0.24, 0.115, 0.010),
             P.PAPER)
    make_box("NexEnvelope_Logo", (tx - 0.22, ty + 0.375, top + 0.012),
             (0.055, 0.022, 0.004), P.BRAND_AMBER_NEX)
    make_box("NexEnvelope_Window", (tx - 0.10, ty + 0.315, top + 0.012),
             (0.10, 0.032, 0.004), (0.80, 0.82, 0.80, 1.0))
    # Salt + pepper + napkin holder
    make_cyl("Salt", (tx + 0.26, ty - 0.02, top + 0.055), 0.020, 0.11, COL_CERAMIC,
             segments=8)
    make_cyl("Pepper", (tx + 0.34, ty + 0.04, top + 0.055), 0.020, 0.11,
             (0.36, 0.30, 0.26, 1.0), segments=8)
    make_box("Napkins_Base", (tx + 0.28, ty - 0.24, top + 0.008), (0.13, 0.09, 0.016),
             COL_WOOD_DK)
    make_box("Napkins_Stack", (tx + 0.28, ty - 0.24, top + 0.05), (0.11, 0.07, 0.07),
             P.PAPER)


# ═════════════════════════════════════════════════════════════════
# WALLS + CEILING — calendar on the west wall, THE kitchen light
# ("She turns off the kitchen light", ch12:398 / ch21:352): one
# brass-trimmed dome over the table. House fixtures only. Smoke
# detector + HVAC register.
# ═════════════════════════════════════════════════════════════════
def build_walls_and_ceiling():
    make_calendar("Calendar", (-ROOM_W / 2.0 + 0.11, 3.6, 1.55))
    make_cyl("DomeLight_Plate", (0.55, 2.70, CEIL - 0.015), 0.19, 0.025, COL_BRASS,
             segments=12)
    make_cyl("DomeLight_Dome", (0.55, 2.70, CEIL - 0.065), 0.165, 0.075,
             (0.97, 0.93, 0.82, 1.0), segments=12)
    make_cyl("DomeLight_Finial", (0.55, 2.70, CEIL - 0.115), 0.018, 0.03, COL_BRASS)
    make_smoke_detector("Smoke", (-1.6, 1.2, CEIL))
    make_hvac_vent("HVAC", (1.8, 0.9, CEIL), width=0.55, depth=0.32)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · THE BACK YARD (through the window) — night: siding
# skins wrap the opening, the dark lawn, the privacy fence, and
# beyond it THE WATER TOWER at the end of Gallatin
# (vol6_ch1_maya_bedroom:44 — the repeater; vol6_ch5_radio:125 —
# the eleven-seventeen hum the dogs answer). Its legs stand in the
# window's sight line from the preset camera; the full tower reads
# in free-roam.
# ═════════════════════════════════════════════════════════════════
def build_exterior_back():
    wallout = ROOM_D + 0.10
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20
    seg_cx = WIN_W / 2.0 + seg_len / 2.0
    make_box("Ext_Skin_W", (-seg_cx, wallout + 0.02, 1.30), (seg_len, 0.06, 2.60),
             CALDWELL_SIDING)
    make_box("Ext_Skin_E", (+seg_cx, wallout + 0.02, 1.30), (seg_len, 0.06, 2.60),
             CALDWELL_SIDING)
    make_box("Ext_Skin_Sill", (0.0, wallout + 0.02, WIN_SILL / 2.0),
             (WIN_W, 0.06, WIN_SILL), CALDWELL_SIDING)
    make_box("Ext_Skin_Head", (0.0, wallout + 0.02, (WIN_HEAD + 2.60) / 2.0),
             (WIN_W, 0.06, 2.60 - WIN_HEAD), CALDWELL_SIDING)
    for si, sz in enumerate((0.55, 1.85, 2.35)):
        make_box(f"Ext_SidingSeam_{si}", (0.0, wallout + 0.052, sz),
                 (ROOM_W + 0.4, 0.006, 0.02), COL_SIDING_SEAM)
    # The back lawn, dark
    make_box("Ext_Lawn", (0.0, 9.0, GRADE_Z - 0.05), (22.0, 7.6, 0.10), COL_NIGHT_LAWN)
    # The privacy fence line
    make_box("Fence_Run", (0.0, 12.6, GRADE_Z + 0.90), (18.0, 0.05, 1.80), COL_FENCE)
    for si in range(12):
        make_box(f"Fence_Seam_{si}", (-7.4 + si * 1.35, 12.57, GRADE_Z + 0.90),
                 (0.020, 0.008, 1.76), COL_FENCE_SEAM)
    make_box("Fence_Cap", (0.0, 12.6, GRADE_Z + 1.83), (18.0, 0.11, 0.05),
             COL_FENCE_SEAM)
    for pi in range(6):
        make_box(f"Fence_Post_{pi}", (-7.0 + pi * 2.8, 12.6, GRADE_Z + 0.92),
                 (0.11, 0.11, 1.88), COL_FENCE_SEAM)
    # A dark neighbor roofline east beyond the fence
    make_box("Neighbor_Body", (7.6, 16.4, GRADE_Z + 1.4), (5.6, 4.2, 2.8),
             (0.44, 0.42, 0.40, 1.0))
    make_box("Neighbor_Roof", (7.6, 16.4, GRADE_Z + 3.0), (6.2, 4.8, 0.42),
             CALDWELL_ROOF)
    # ── THE WATER TOWER at the end of Gallatin ───────────────────
    twx, twy = 1.2, 27.0
    for li, (lx, ly) in enumerate([(-1.7, -1.7), (1.7, -1.7), (-1.7, 1.7),
                                   (1.7, 1.7)]):
        make_cyl(f"Tower_Leg_{li}", (twx + lx, twy + ly, GRADE_Z + 4.5), 0.13, 9.0,
                 COL_TOWER_DK, segments=8)
    for bi, bz in enumerate((GRADE_Z + 3.0, GRADE_Z + 6.2)):
        make_box(f"Tower_BraceX_{bi}", (twx, twy - 1.7, bz), (3.4, 0.10, 0.10),
                 COL_TOWER_DK)
        make_box(f"Tower_BraceY_{bi}", (twx - 1.7, twy, bz), (0.10, 3.4, 0.10),
                 COL_TOWER_DK)
    make_cyl("Tower_Riser", (twx, twy, GRADE_Z + 6.0), 0.35, 12.0, COL_TOWER_DK,
             segments=10)
    make_cyl("Tower_Catwalk", (twx, twy, GRADE_Z + 9.3), 2.85, 0.08, COL_TOWER_DK,
             segments=12)
    make_cyl("Tower_Tank", (twx, twy, GRADE_Z + 11.2), 2.60, 3.40, COL_TOWER,
             segments=12)
    make_cyl("Tower_Dome", (twx, twy, GRADE_Z + 13.3), 1.95, 0.85, COL_TOWER,
             segments=12)
    make_cyl("Tower_Finial", (twx, twy, GRADE_Z + 13.95), 0.10, 0.55, COL_TOWER_DK)


def main():
    clear_scene()
    build_shell()
    build_window()
    build_counter_run()
    build_fridge()
    build_table_zone()
    build_walls_and_ceiling()
    build_exterior_back()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_kitchen_night.glb"))
    print(f"\n[build_caldwell_kitchen_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
