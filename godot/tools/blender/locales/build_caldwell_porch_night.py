"""Caldwell Front Porch (night) — Linda Caldwell's house, lot 7
Phase I, the Caldwell cul-de-sac, Harmony Creek Estates — vol6 hero
locale (4 VN bg refs: vol6_ch12_porch x2 "The Staying",
vol6_ch21_porch "The Porch", vol6_ch23_sunday).

The GRANDMOTHER'S front porch — where Maya Daigle and her
grandmother sit with iced tea at nine PM all through the vol6
summer. This is one house with THREE hero-passed rooms in this
directory (porch / kitchen / radio room) plus Maya's bedroom
upstairs (build_maya_bedroom.py) — see the shared KEEP-IN-SYNC
palette block below. Canon baked in:

  · vol6_ch12_porch:96 — "The porch light is on. Linda is in the
    wicker chair ... with a glass of iced tea on the small table
    beside her and a paperback in her lap." THE WICKER CHAIR is the
    hero prop (movable — ch23 has Maya wheel it out to the yard and
    Ben set it "back where it had been"). White-painted wicker, an
    old woman's chair.
  · vol6_ch12_porch:132 — "Maya sits in the second porch chair."
    The second chair is deliberately NOT wicker (never called
    wicker in any scene) — a painted straight chair beside the
    table.
  · vol6_ch12_porch:318 — "The iced tea in the second glass has, by
    the warmth of the night, condensed about half its outer surface
    into a small ring on the small table." TWO glasses on the small
    table + the condensation ring baked into the tabletop
    (vol6_ch21_porch:42 — "two glasses of iced tea — the one she
    has been drinking, and the one she has poured for Maya in
    advance"). The paperback rests by them (ch12:96 — twelve pages
    an hour).
  · vol6_ch21_porch:46 — "Maya parks the bike. She climbs the porch
    steps." Porch STEPS down to the front walk; Maya's bike on the
    lawn beside the walk.
  · vol6_ch12_porch:366 — "She turns off the porch light." /
    ch12:28 + ch21:42 — resting state is ON: the sconce beside the
    front door glows warm (scene-side Light3D matches).
  · vol6_ch23_sunday:238 — "The folding table from the Kowalski
    garage is set up under the pecan tree." THE PECAN TREE is
    permanent front-yard canon; the folding table + sheet cake are
    one-afternoon event dressing and are NOT baked.
  · vol6_ch21_porch:208 — "Don Geller's porch light, three doors
    down ... is also on." The Geller house closes the cul-de-sac
    view with its one warm dot (matches build_maya_bedroom.py's
    Geller massing — same house from one floor up).
  · vol6_ch14 (via build_maya_bedroom.py) — the cedar across the
    cul-de-sac, where the cicadas live. Same tiered cedar, seen
    from the porch instead of the upstairs window.
  · vol6_ch12/ch21 — "She goes inside. She locks the front door."
    The front-door gap in the house wall is the Background3D camera
    doorway (kept from the scaffold); the wooden screen door is
    propped open flat against the siding (Miller-porch pattern) so
    the gap stays clear.

Canon-NEGATIVES honored (what this porch does NOT have):
  · No second WICKER chair — Linda's wicker + a plain painted
    second chair only. Ch23's third sitter (Ben) is staged by the
    scene, not by a baked third chair.
  · No porch swing, no ceiling fan (never mentioned; the Miller
    lesson: fans only where canon puts them).
  · The small light blanket lives on the back of the couch INSIDE
    (ch12:362) — not draped here.
  · No screens — people climb the steps straight up (ch21:46);
    this is an open post-and-rail porch, unlike the Millers'
    screened back porch.
  · No radio out here — the 1776 kHz shortwave is upstairs on the
    grandmother's windowsill (ch12:454, build_caldwell_radio_room_
    night.py).
  · No folding table / cake / lemonade (ch23 event dressing only).

NAME-DEPENDENCY FLAG (same drift build_maya_bedroom.py flags): the
scene JSONs name the grandmother Ms. LINDA CALDWELL on "the
Caldwell cul-de-sac" (vol6_ch5_radio:121 files her under
GRANDMOTHER, CALDWELL, LINDA); the older lore docs
(lore/planned_community/maya_daigle.md, lore/_VOL6_WIKI.md elders'
list) say CONNIE DAIGLE. The JSONs are treated as current — the
wiki's Connie facts (the 4/4 vacuuming to WUFR's sub-carrier, the
unopened NexCorp envelopes) are read as Linda facts. Also note
grandmother_kitchen_morning is the RAMOS house (Diego's abuela),
firewalled explicitly by vol6_ch10_home:38 — no vocabulary is
borrowed from it.

Shell footprint kept from the scaffold (6 x 4, CEIL 2.8, gap
x -1..+1 in the stage-south house wall = the front doorway the
Background3D camera preset (0, 2.30, +0.5 / yaw 180 / fov 60)
shoots through). Stage-north = the cul-de-sac.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_door_hinges
from _props.decor import make_floor_plant

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 6.0; ROOM_D = 4.0; CEIL = 2.8

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

# Porch-only palette
COL_DECK        = (0.58, 0.55, 0.48, 1.0)   # painted porch deck, worn grey
COL_DECK_SEAM   = (0.40, 0.37, 0.31, 1.0)
COL_WICKER      = (0.88, 0.85, 0.76, 1.0)   # Linda's wicker, painted white
COL_WICKER_DK   = (0.68, 0.64, 0.55, 1.0)
COL_CHAIR_SAGE  = (0.44, 0.50, 0.42, 1.0)   # the second chair, painted
COL_SCREEN_FR   = (0.30, 0.32, 0.34, 1.0)   # screen-door frame charcoal
COL_PECAN       = (0.25, 0.33, 0.21, 1.0)   # the pecan tree at night
COL_PECAN_DK    = (0.20, 0.27, 0.17, 1.0)
COL_TRUNK       = (0.33, 0.26, 0.19, 1.0)
COL_BIKE        = (0.44, 0.22, 0.20, 1.0)   # Maya's bike, burgundy
COL_TIRE        = (0.14, 0.14, 0.15, 1.0)
COL_PAPERBACK   = (0.50, 0.44, 0.40, 1.0)

LAWN_Z = -0.45          # front-yard grade (deck top = 0.0)


# ═════════════════════════════════════════════════════════════════
# DECK — painted board deck (boards run E-W toward the steps), rim
# and skirt down to the night lawn. Scaffold footprint kept.
# ═════════════════════════════════════════════════════════════════
def build_deck():
    make_box("Deck_Slab", (0.0, 2.0, -0.04), (6.4, 4.4, 0.08), COL_DECK)
    for bi in range(13):
        make_box(f"Deck_BoardSeam_{bi}", (0.0, 0.30 + bi * 0.30, 0.002),
                 (6.3, 0.014, 0.004), COL_DECK_SEAM)
    make_box("Deck_Rim_N", (0.0, 4.17, -0.26), (6.4, 0.06, 0.38), COL_DECK_SEAM)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Deck_Rim_{seg}", (sgn * 3.17, 2.0, -0.26), (0.06, 4.4, 0.38),
                 COL_DECK_SEAM)
    # Lattice skirt panels under the rim (tract-porch standard)
    for si, sx in enumerate((-2.2, 0.0, 2.2)):
        make_box(f"Deck_Skirt_{si}", (sx, 4.145, -0.30), (1.9, 0.02, 0.26),
                 COL_WICKER_DK)


# ═════════════════════════════════════════════════════════════════
# HOUSE FACE (stage-south) — the front of the 1991 tract house:
# lap siding + seams, the front-door gap kept clear (camera; "She
# locks the front door", ch12/ch21), casing + threshold, the wooden
# screen door propped open flat against the west siding, the PORCH
# LIGHT sconce east of the door — ON (ch12:96 / ch21:42) — the
# living-room window east of it, dark (everyone's on the porch),
# and siding wings so the frame edges read as house, not void.
# ═════════════════════════════════════════════════════════════════
def build_house_face():
    make_box("House_Wall_W", (-2.0, 0.0, 1.40), (2.0, 0.20, 2.80), CALDWELL_SIDING)
    make_box("House_Wall_E", (+2.0, 0.0, 1.40), (2.0, 0.20, 2.80), CALDWELL_SIDING)
    make_box("House_Wall_AboveDoor", (0.0, 0.0, 2.55), (2.0, 0.20, 0.50),
             CALDWELL_SIDING)
    # Lap-siding shadow seams on the porch-facing (+Y) face
    for zi in range(10):
        sz = 0.26 + zi * 0.26
        for seg, segx in (("W", -2.0), ("E", +2.0)):
            make_box(f"Siding_{seg}_{zi}", (segx, 0.105, sz), (1.96, 0.012, 0.026),
                     COL_SIDING_SEAM)
    for zi, sz in enumerate((2.42, 2.66)):
        make_box(f"Siding_AD_{zi}", (0.0, 0.105, sz), (1.96, 0.012, 0.026),
                 COL_SIDING_SEAM)
    for sgn in (-1, +1):
        make_box(f"House_CornerTrim_{sgn:+d}", (sgn * 2.98, 0.12, 1.40),
                 (0.10, 0.06, 2.80), CALDWELL_TRIM)
    # Front-door casing + threshold (the leaf itself swings inward,
    # out of frame — the gap is the camera doorway)
    for sgn in (-1, +1):
        make_box(f"FrontDoor_Jamb_{sgn:+d}", (sgn * 1.03, 0.0, 1.13),
                 (0.10, 0.26, 2.26), CALDWELL_TRIM)
    make_box("FrontDoor_Head", (0.0, 0.0, 2.30), (2.26, 0.26, 0.10), CALDWELL_TRIM)
    make_box("FrontDoor_Threshold", (0.0, 0.0, 0.02), (2.00, 0.26, 0.04), COL_WOOD_DK)
    make_box("Doormat", (0.0, 0.62, 0.008), (1.05, 0.60, 0.014),
             (0.52, 0.42, 0.30, 1.0))
    # The wooden screen door — propped open flat against the west
    # siding (Miller-porch pattern; keeps the camera gap clear)
    for si, sx in enumerate((-1.88, -1.12)):
        make_box(f"ScreenDoor_Stile_{si}", (sx, 0.16, 1.07), (0.05, 0.04, 2.10),
                 COL_SCREEN_FR)
    for ri, rz in enumerate((2.10, 1.10, 0.06)):
        make_box(f"ScreenDoor_Rail_{ri}", (-1.5, 0.16, rz), (0.81, 0.04, 0.05),
                 COL_SCREEN_FR)
    make_box("ScreenDoor_Kick", (-1.5, 0.155, 0.31), (0.78, 0.02, 0.44), COL_SCREEN_FR)
    make_box("ScreenDoor_Handle", (-1.16, 0.20, 1.05), (0.03, 0.03, 0.14),
             P.METAL_BLACK)
    make_door_hinges("ScreenDoor_Hinge", edge_x=-1.06, edge_y=0.13,
                     edge_z_centers=[0.35, 1.07, 1.80], axis='X')
    # THE PORCH LIGHT — sconce east of the door, ON (ch12/ch21; she
    # turns it off only at the very end of the night). The scene's
    # real OmniLight3D matches this fixture.
    make_box("Sconce_Backplate", (1.38, 0.125, 2.00), (0.11, 0.03, 0.18), P.METAL_BLACK)
    make_box("Sconce_Arm", (1.38, 0.18, 2.06), (0.04, 0.10, 0.03), P.METAL_BLACK)
    make_cyl("Sconce_Bulb", (1.38, 0.24, 1.99), 0.042, 0.10, COL_PORCHBULB, segments=10)
    make_cyl("Sconce_Cap", (1.38, 0.24, 2.055), 0.055, 0.03, P.METAL_BLACK, segments=10)
    # Living-room window on the east segment — trim + DARK panes
    # (real opening not needed: the interior is another room's GLB;
    # the dark inset reads as night glass-less panes)
    make_box("FrontWin_Inset", (2.15, 0.09, 1.55), (0.90, 0.03, 1.00), COL_WINDOW_DARK)
    make_box("FrontWin_FrameT", (2.15, 0.115, 2.08), (1.02, 0.04, 0.06), CALDWELL_TRIM)
    make_box("FrontWin_FrameB", (2.15, 0.115, 1.02), (1.02, 0.04, 0.06), CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"FrontWin_Jamb_{sgn:+d}", (2.15 + sgn * 0.48, 0.115, 1.55),
                 (0.06, 0.04, 1.12), CALDWELL_TRIM)
    make_box("FrontWin_MullH", (2.15, 0.115, 1.55), (0.90, 0.035, 0.05), CALDWELL_TRIM)
    make_box("FrontWin_MullV", (2.15, 0.115, 1.55), (0.05, 0.035, 1.00), CALDWELL_TRIM)
    # House wings beyond the porch + eaves
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"House_Wing_{seg}", (sgn * 4.6, -0.05, 1.55), (3.2, 0.20, 3.20),
                 CALDWELL_SIDING)
        for zi in range(5):
            make_box(f"Wing_{seg}_Seam_{zi}", (sgn * 4.6, 0.055, 0.40 + zi * 0.56),
                     (3.16, 0.012, 0.026), COL_SIDING_SEAM)
        make_box(f"Wing_{seg}_Eave", (sgn * 4.6, 0.05, 3.22), (3.3, 0.60, 0.16),
                 CALDWELL_ROOF)
        make_box(f"Wing_{seg}_Fascia", (sgn * 4.6, 0.32, 3.12), (3.3, 0.06, 0.12),
                 CALDWELL_TRIM)


# ═════════════════════════════════════════════════════════════════
# POSTS + RAILING — open post-and-rail porch (NOT screened — Maya
# climbs the steps straight up, ch21:46). Turned posts as cylinders
# per the playbook (columns are make_cyl, not tall boxes). North
# rail breaks at the steps bay x -0.55..+0.55.
# ═════════════════════════════════════════════════════════════════
def build_posts_and_rail():
    posts = [(-2.90, 3.90), (2.90, 3.90), (-0.75, 3.90), (0.75, 3.90),
             (-2.90, 2.00), (2.90, 2.00), (-2.90, 0.30), (2.90, 0.30)]
    for pi, (px, py) in enumerate(posts):
        make_cyl(f"Porch_Post_{pi}", (px, py, 1.40), 0.055, 2.80, CALDWELL_TRIM,
                 segments=10)
        make_box(f"Porch_PostBase_{pi}", (px, py, 0.10), (0.14, 0.14, 0.20),
                 CALDWELL_TRIM)
    # Top + bottom rails: north spans flank the steps; E/W full runs
    rails = [("N_W", (-1.825, 3.90), (2.15, 0.09)), ("N_E", (1.825, 3.90), (2.15, 0.09)),
             ("W", (-2.90, 2.10), (0.09, 3.60)), ("E", (2.90, 2.10), (0.09, 3.60))]
    for nm, (rx, ry), (lx, ly) in rails:
        make_box(f"Rail_Top_{nm}", (rx, ry, 0.92), (lx, ly, 0.07), CALDWELL_TRIM)
        make_box(f"Rail_Bot_{nm}", (rx, ry, 0.12), (lx, ly, 0.05), CALDWELL_TRIM)
    # Balusters (0.30 spacing, square stock)
    for bi in range(7):
        for seg, sgn in (("W", -1), ("E", +1)):
            bx = sgn * (0.90 + bi * 0.30)
            make_box(f"Baluster_N_{seg}_{bi}", (bx, 3.90, 0.52), (0.032, 0.032, 0.76),
                     CALDWELL_TRIM)
    for bi in range(11):
        by = 0.60 + bi * 0.30
        for seg, sgn in (("W", -1), ("E", +1)):
            make_box(f"Baluster_{seg}_{bi}", (sgn * 2.90, by, 0.52),
                     (0.032, 0.032, 0.76), CALDWELL_TRIM)


# ═════════════════════════════════════════════════════════════════
# ROOF — beadboard porch ceiling + shingle slab + fascia. Flat
# underside at CEIL (camera-safe). No ceiling fan (canon-negative).
# ═════════════════════════════════════════════════════════════════
def build_roof():
    make_box("Porch_Ceiling", (0.0, 2.0, CEIL + 0.05), (6.6, 4.6, 0.10),
             (0.90, 0.88, 0.80, 1.0))
    for bi in range(6):
        make_box(f"Ceiling_Bead_{bi}", (0.0, 0.55 + bi * 0.58, CEIL - 0.006),
                 (6.5, 0.010, 0.006), (0.76, 0.74, 0.66, 1.0))
    make_box("Porch_RoofSlab", (0.0, 2.10, CEIL + 0.19), (6.9, 4.7, 0.12),
             CALDWELL_ROOF)
    make_box("Fascia_N", (0.0, 4.42, CEIL + 0.10), (6.9, 0.06, 0.16), CALDWELL_TRIM)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Fascia_{seg}", (sgn * 3.42, 2.10, CEIL + 0.10), (0.06, 4.7, 0.16),
                 CALDWELL_TRIM)


# ═════════════════════════════════════════════════════════════════
# STEPS — center bay down to the front walk ("She climbs the porch
# steps", ch21:46). Two treads + stringers, straight shot from the
# front door to the cul-de-sac.
# ═════════════════════════════════════════════════════════════════
def build_steps():
    make_box("Step_0", (0.0, 4.38, -0.14), (1.10, 0.34, 0.09), COL_DECK)
    make_box("Step_1", (0.0, 4.72, -0.30), (1.10, 0.34, 0.09), COL_DECK)
    for sgn in (-1, +1):
        make_box(f"Step_Stringer_{sgn:+d}", (sgn * 0.56, 4.55, -0.26),
                 (0.04, 0.70, 0.34), COL_DECK_SEAM)


# ═════════════════════════════════════════════════════════════════
# THE SITTING — Linda's white wicker chair (ch12:96; movable, per
# ch23's yard ceremony), the small table with TWO iced teas + the
# condensation ring (ch12:318, ch21:42) + the paperback (ch12:96),
# and the SECOND porch chair (painted, plain — never called wicker).
# Grouped west of the door, the way the scenes stage it: Linda in
# the wicker, Maya in the second chair, the table between them.
# ═════════════════════════════════════════════════════════════════
def build_sitting():
    # ── THE WICKER CHAIR ─────────────────────────────────────────
    cx, cy = -2.05, 0.75
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Wicker_Leg_{li}", (cx + sx * 0.30, cy + sy * 0.24, 0.20),
                 0.026, 0.40, COL_WICKER_DK)
    make_box("Wicker_Seat", (cx, cy, 0.42), (0.62, 0.56, 0.075), COL_WICKER)
    for wi in range(3):
        make_box(f"Wicker_SkirtWeave_{wi}", (cx, cy - 0.285, 0.315 + wi * 0.035),
                 (0.60, 0.008, 0.014), COL_WICKER_DK)
    make_box("Wicker_Cushion", (cx, cy + 0.02, 0.475), (0.56, 0.50, 0.055),
             (0.58, 0.52, 0.48, 1.0))
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_cyl(f"Wicker_ArmRail_{seg}", (cx + sgn * 0.34, cy + 0.02, 0.63),
                 0.038, 0.54, COL_WICKER, axis='Y', segments=10)
        make_box(f"Wicker_ArmBoard_{seg}", (cx + sgn * 0.34, cy + 0.02, 0.665),
                 (0.11, 0.50, 0.020), COL_WICKER)
        make_cyl(f"Wicker_ArmPost_{seg}", (cx + sgn * 0.34, cy - 0.20, 0.53),
                 0.022, 0.20, COL_WICKER_DK)
    make_box("Wicker_Back", (cx, cy + 0.295, 1.00), (0.62, 0.06, 0.90), COL_WICKER)
    for wi in range(5):
        make_box(f"Wicker_BackWeave_{wi}", (cx, cy + 0.26, 0.66 + wi * 0.16),
                 (0.58, 0.008, 0.020), COL_WICKER_DK)
    make_cyl("Wicker_Crest", (cx, cy + 0.295, 1.45), 0.10, 0.62, COL_WICKER,
             axis='X', segments=12)
    # ── THE SMALL TABLE (ch12:96 "the small table beside her") ───
    tx, ty = -1.18, 0.80
    make_cyl("SideTable_Top", (tx, ty, 0.52), 0.24, 0.035, COL_WICKER, segments=12)
    make_cyl("SideTable_Ring", (tx, ty, 0.485), 0.20, 0.03, COL_WICKER_DK, segments=12)
    for li in range(3):
        lx, ly = [(-0.13, -0.09), (0.13, -0.09), (0.0, 0.15)][li]
        make_cyl(f"SideTable_Leg_{li}", (tx + lx, ty + ly, 0.25), 0.016, 0.50,
                 COL_WICKER_DK)
    # The two iced teas — Linda's and the one poured for Maya in
    # advance (ch21:42)
    for gi, (gx, gy) in enumerate([(tx - 0.09, ty + 0.06), (tx + 0.10, ty - 0.04)]):
        make_cyl(f"IcedTea_{gi}_Glass", (gx, gy, 0.601), 0.033, 0.125,
                 (0.74, 0.78, 0.76, 1.0), segments=10)
        make_cyl(f"IcedTea_{gi}_Fill", (gx, gy, 0.606), 0.028, 0.10, COL_TEA,
                 segments=10)
    # THE CONDENSATION RING on the tabletop (ch12:318) — a faint
    # darker ring where Maya's glass has been sweating
    make_cyl("Table_SweatRing", (tx + 0.10, ty - 0.04, 0.539), 0.040, 0.002,
             COL_WICKER_DK, segments=12)
    # Linda's paperback — twelve pages an hour (ch12:96)
    make_box("Paperback", (tx - 0.02, ty - 0.15, 0.552), (0.125, 0.175, 0.028),
             COL_PAPERBACK)
    make_box("Paperback_Pages", (tx + 0.043, ty - 0.15, 0.552), (0.012, 0.165, 0.022),
             P.PAPER)
    # ── THE SECOND PORCH CHAIR (ch12:132) — painted, plain ───────
    sx2, sy2 = -0.42, 0.85
    make_box("Chair2_Seat", (sx2, sy2, 0.44), (0.42, 0.42, 0.045), COL_CHAIR_SAGE)
    for li, (lx, ly) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Chair2_Leg_{li}", (sx2 + lx * 0.17, sy2 + ly * 0.17, 0.22),
                 0.019, 0.44, (0.34, 0.40, 0.33, 1.0))
    for pi, sgn in enumerate((-1, +1)):
        make_cyl(f"Chair2_Post_{pi}", (sx2 + sgn * 0.17, sy2 - 0.20, 0.69),
                 0.017, 0.50, COL_CHAIR_SAGE)
    for si, sz in enumerate((0.72, 0.88)):
        make_box(f"Chair2_Slat_{si}", (sx2, sy2 - 0.20, sz), (0.38, 0.032, 0.085),
                 COL_CHAIR_SAGE)
    # A potted fern by the west rail — the one flourish the porch
    # allows itself (register dressing)
    make_floor_plant("PorchFern", (-2.55, 3.30, 0.0))


# ═════════════════════════════════════════════════════════════════
# YARD + CUL-DE-SAC (stage-north) — the night view the two of them
# watch: front walk from the steps, MAYA'S BIKE parked on the lawn
# beside it (ch12:100, ch21:46), THE PECAN TREE (ch23:238), the
# sidewalk / curb / street, the CEDAR across the cul-de-sac (the
# cicadas' tree, per build_maya_bedroom.py's ch14 exterior), the
# GELLER HOUSE closing the view with its porch light ON three doors
# down (ch21:208), a dark tract massing west, and one HCE
# streetlight. The cul-de-sac is quiet.
# ═════════════════════════════════════════════════════════════════
def build_yard():
    make_box("Ext_Lawn", (0.0, 7.2, LAWN_Z - 0.05), (20.0, 5.4, 0.10), COL_NIGHT_LAWN)
    make_box("Ext_Walk", (0.0, 7.2, LAWN_Z + 0.006), (0.95, 5.4, 0.012), COL_CONCRETE)
    make_box("Ext_Sidewalk", (0.0, 10.3, LAWN_Z - 0.02), (20.0, 0.80, 0.10),
             COL_CONCRETE)
    make_box("Ext_Curb", (0.0, 10.78, LAWN_Z - 0.02), (20.0, 0.16, 0.14), COL_CONCRETE)
    make_box("Ext_Street", (0.0, 12.9, LAWN_Z - 0.07), (20.0, 4.1, 0.10), COL_ASPHALT)
    make_box("Ext_FarLawn", (0.0, 17.1, LAWN_Z - 0.05), (20.0, 4.3, 0.10),
             COL_NIGHT_LAWN)
    # The mailbox at the walk's end
    make_cyl("Ext_MailPost", (0.78, 10.05, LAWN_Z + 0.45), 0.035, 0.90, COL_WOOD_DK)
    make_box("Ext_Mailbox", (0.78, 10.05, LAWN_Z + 1.00), (0.18, 0.42, 0.20),
             (0.30, 0.32, 0.34, 1.0))
    # ── MAYA'S BIKE on the lawn east of the walk (ch12/ch21) ─────
    bx = 1.35
    for wi, wy in enumerate((5.28, 6.10)):
        make_cyl(f"Bike_Wheel_{wi}", (bx, wy, LAWN_Z + 0.33), 0.32, 0.05, COL_TIRE,
                 axis='X', segments=12)
        make_cyl(f"Bike_Hub_{wi}", (bx, wy, LAWN_Z + 0.33), 0.045, 0.07,
                 (0.60, 0.62, 0.64, 1.0), axis='X', segments=8)
    make_box("Bike_TopTube", (bx, 5.69, LAWN_Z + 0.62), (0.035, 0.62, 0.045), COL_BIKE)
    make_box("Bike_DownTube", (bx, 5.62, LAWN_Z + 0.48), (0.03, 0.50, 0.035), COL_BIKE)
    make_cyl("Bike_SeatPost", (bx, 5.36, LAWN_Z + 0.74), 0.016, 0.22,
             (0.60, 0.62, 0.64, 1.0))
    make_box("Bike_Seat", (bx, 5.36, LAWN_Z + 0.87), (0.09, 0.24, 0.05), COL_TIRE)
    make_cyl("Bike_HeadPost", (bx, 6.02, LAWN_Z + 0.78), 0.016, 0.28,
             (0.60, 0.62, 0.64, 1.0))
    make_cyl("Bike_Handlebar", (bx, 6.02, LAWN_Z + 0.93), 0.016, 0.44,
             (0.60, 0.62, 0.64, 1.0), axis='X', segments=8)
    make_cyl("Bike_Kickstand", (bx - 0.14, 5.62, LAWN_Z + 0.16), 0.010, 0.32,
             (0.44, 0.46, 0.48, 1.0))
    # ── THE PECAN TREE, west front yard (ch23:238) ───────────────
    px, py = -3.6, 6.9
    make_cyl("Pecan_Trunk", (px, py, LAWN_Z + 1.30), 0.16, 2.60, COL_TRUNK, segments=10)
    for ci, (cr, cz, tint) in enumerate([(2.10, LAWN_Z + 3.30, COL_PECAN),
                                         (1.60, LAWN_Z + 4.25, COL_PECAN_DK),
                                         (0.95, LAWN_Z + 5.05, COL_PECAN)]):
        make_cyl(f"Pecan_Canopy_{ci}", (px, py, cz), cr, 0.80, tint, segments=10)
    # ── THE CEDAR across the cul-de-sac (ch14 — the cicadas) ─────
    make_cyl("Cedar_Trunk", (-5.0, 14.8, LAWN_Z + 0.9), 0.14, 1.80, COL_WOOD_DK)
    for ti, (tr, tz, tc) in enumerate([(1.40, LAWN_Z + 2.25, COL_CEDAR_DK),
                                       (1.05, LAWN_Z + 3.15, COL_CEDAR),
                                       (0.72, LAWN_Z + 3.95, COL_CEDAR_DK),
                                       (0.42, LAWN_Z + 4.65, COL_CEDAR)]):
        make_cyl(f"Cedar_Tier_{ti}", (-5.0, 14.8, tz), tr, 0.85, tc, segments=10)
    # ── THE GELLER HOUSE, three doors down (ch21:208) — the one
    # warm dot: porch light ON. Same massing build_maya_bedroom.py
    # models from one floor up.
    gx, gy = 5.4, 16.4
    make_box("Geller_Body", (gx, gy, LAWN_Z + 1.5), (6.5, 4.2, 3.0), COL_GELLER_BODY)
    make_box("Geller_Roof0", (gx, gy, LAWN_Z + 3.24), (7.1, 4.8, 0.48), CALDWELL_ROOF)
    make_box("Geller_Roof1", (gx, gy, LAWN_Z + 3.68), (4.8, 3.2, 0.40), CALDWELL_ROOF)
    for wi, wx in enumerate((-1.9, 0.0)):
        make_box(f"Geller_Window_{wi}", (gx + wx, gy - 2.13, LAWN_Z + 1.6),
                 (0.85, 0.06, 0.75), COL_WINDOW_DARK)
    make_box("Geller_Door", (gx - 0.9, gy - 2.12, LAWN_Z + 1.0), (0.85, 0.06, 2.0),
             (0.22, 0.20, 0.19, 1.0))
    make_box("Geller_LightBracket", (gx - 1.45, gy - 2.10, LAWN_Z + 1.70),
             (0.06, 0.05, 0.10), P.METAL_BLACK)
    make_cyl("Geller_PorchLight", (gx - 1.45, gy - 2.16, LAWN_Z + 1.66), 0.055, 0.12,
             COL_PORCHBULB, segments=10)
    # A dark tract massing west — the street repeating
    make_box("TractW_Body", (-8.6, 16.2, LAWN_Z + 1.4), (5.8, 4.4, 2.8),
             (0.48, 0.46, 0.44, 1.0))
    make_box("TractW_Roof", (-8.6, 16.2, LAWN_Z + 3.02), (6.4, 5.0, 0.44),
             CALDWELL_ROOF)
    make_box("TractW_Window", (-8.6, 13.96, LAWN_Z + 1.5), (0.85, 0.06, 0.70),
             COL_WINDOW_DARK)
    # One HCE streetlight at the curb, east
    make_cyl("Street_Pole", (3.6, 10.5, LAWN_Z + 2.6), 0.05, 5.20, P.METAL_BLACK)
    make_cyl("Street_Arm", (3.28, 10.5, LAWN_Z + 5.10), 0.030, 0.60, P.METAL_BLACK,
             axis='X')
    make_cyl("Street_Lens", (3.0, 10.5, LAWN_Z + 5.02), 0.09, 0.07, COL_PORCHBULB,
             segments=10)


def main():
    clear_scene()
    build_deck()
    build_house_face()
    build_posts_and_rail()
    build_roof()
    build_steps()
    build_sitting()
    build_yard()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_porch_night.glb"))
    print(f"\n[build_caldwell_porch_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
