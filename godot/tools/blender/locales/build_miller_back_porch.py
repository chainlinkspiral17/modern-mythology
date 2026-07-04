"""Miller Back Porch — 1428 Meadowlark Circle, Harmony Creek, TX —
vol6 hero locale (16 VN bg refs; the Miller-house canon lives in
vol6_ch17_porch, vol6_ch11_kitchen §674-869, vol6_ch11_eileen).

The small SCREENED-IN back porch off the kitchen, mid-August Texas,
in a NexCorp-built HCE tract house. Canon baked in:

  · vol6_ch11_kitchen:678 — "The back porch is small. It is screened
    in. It has, against the back wall, a wicker chair that had been
    her mother's and that had come down to Texas in the move from
    Lubbock in 1989." THE hero prop. The light "catches the small
    motes of dust in the screen" (:686).
  · vol6_ch11_eileen:46 — "She puts the coffee cup down on the
    wicker chair's arm." The arm gets a flat board wide enough to
    hold the cup, and the cup sits on it.
  · vol6_ch17_porch:38-94 — Bianca eats coffee cake off a small
    plate in the early-morning shaded window; :106 the mockingbird
    in the NEIGHBOR'S OAK, cicadas warming up.
  · vol6_ch11_kitchen:686/:750 — "The crepe myrtle in the corner is
    in late bloom", cicadas in it; "The grass is browning in
    patches."
  · vol6_ch15_home:80/:200 — the wicker chair and an iced tea;
    evening: "Bianca, on the porch, is reading" (the paperback on
    the side table).
  · vol6_ch11_kitchen:764 — Sam "knocks on the door frame": real
    door casing on the kitchen doorway. vol6_ch17_table:396/:1362 —
    Anita comes and goes through this porch: a screen door in the
    north wall with steps down to the yard.
  · Music manifest: vol6_porch_light_watch — "Porch Lights ·
    Mid-August" — the sconce beside the kitchen door.

Deliberately ABSENT (canon-negative): no ceiling fan (canon puts a
fan only in Sam's bedroom, vol6_ch15_home:192), no drainage canal,
no second wicker chair — company gets one of the oak kitchen-set
chairs carried out (the same _miller_chair the kitchen file builds
four of).

HCE register: the bones are the standard tract model — cream lap
siding, builder-white trim, the SAME house massing repeating past
the fence line (Phase I uniformity, _HCE_LAYOUT_INVENTORY /
_VOL6_WIKI "the lawn is the lawn") — with the Millers' life layered
on top (the Lubbock chair, the iced tea, the browning August grass
the sprinklers don't reach back here).

Shell footprint kept from the scaffold (6 x 4, CEIL 2.8, gap
x -1..+1 in the south wall = the kitchen doorway the Background3D
camera preset (0, 2.30, +0.5 / yaw 180 / fov 62) shoots through).
"South" is stage-south: the house wall. Screens follow the playbook
no-transparency rule the same way windows do — frames, kneewalls
and rails only, openings empty.
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

LAWN_Z = -0.45          # back yard grade (deck top = 0.0)


# ═════════════════════════════════════════════════════════════════
# DECK — pressure-treated boards running E-W, rim + skirt down to
# the August lawn. Small porch, small deck: the scaffold footprint.
# ═════════════════════════════════════════════════════════════════
def build_deck():
    make_box("Deck_Slab", (0.0, 2.0, -0.04), (6.4, 4.4, 0.08), MILLER_DECK)
    for bi in range(13):
        make_box(f"Deck_BoardSeam_{bi}", (0.0, 0.30 + bi * 0.30, 0.002),
                 (6.3, 0.014, 0.004), MILLER_DECK_SEAM)
    # Rim + skirt boards (deck sits ~0.45 m above grade)
    make_box("Deck_Rim_N", (0.0, 4.17, -0.26), (6.4, 0.06, 0.38), MILLER_DECK_SEAM)
    for sgn in (-1, +1):
        make_box(f"Deck_Rim_{'E' if sgn > 0 else 'W'}",
                 (sgn * 3.17, 2.0, -0.26), (0.06, 4.4, 0.38), MILLER_DECK_SEAM)


# ═════════════════════════════════════════════════════════════════
# HOUSE WALL (stage-south) — the back of the tract house: cream lap
# siding + builder-white trim, kitchen doorway in the scaffold gap
# x -1..+1 (the door frame Sam knocks on, vol6_ch11_kitchen:764),
# the wooden screen door propped open flat against the west siding,
# the porch-light sconce (vol6 music: "Porch Lights · Mid-August"),
# and the siding WINGS beyond the porch so the view left and right
# is house, not void.
# ═════════════════════════════════════════════════════════════════
def build_house_wall():
    # Wall segments (scaffold positions kept)
    make_box("House_Wall_W", (-2.0, 0.0, 1.40), (2.0, 0.20, 2.80), MILLER_SIDING)
    make_box("House_Wall_E", (+2.0, 0.0, 1.40), (2.0, 0.20, 2.80), MILLER_SIDING)
    make_box("House_Wall_AboveDoor", (0.0, 0.0, 2.55), (2.0, 0.20, 0.50), MILLER_SIDING)
    # Lap-siding shadow seams on the porch-facing (+Y) face
    for zi in range(10):
        sz = 0.26 + zi * 0.28
        for seg, segx in (("W", -2.0), ("E", +2.0)):
            make_box(f"Siding_{seg}_{zi}", (segx, 0.105, sz), (1.96, 0.012, 0.028),
                     MILLER_SIDING_SH)
    for zi, sz in enumerate((2.42, 2.66)):
        make_box(f"Siding_AD_{zi}", (0.0, 0.105, sz), (1.96, 0.012, 0.028),
                 MILLER_SIDING_SH)
    # Corner trim where the porch frame meets the house
    for sgn in (-1, +1):
        make_box(f"House_CornerTrim_{sgn:+d}", (sgn * 2.98, 0.12, 1.40),
                 (0.10, 0.06, 2.80), MILLER_TRIM)
    # Kitchen doorway — jambs + head casing (the frame Sam knocks on)
    for sgn in (-1, +1):
        make_box(f"KitchenDoor_Jamb_{sgn:+d}", (sgn * 1.03, 0.0, 1.13),
                 (0.10, 0.26, 2.26), MILLER_TRIM)
    make_box("KitchenDoor_Head", (0.0, 0.0, 2.30), (2.26, 0.26, 0.10), MILLER_TRIM)
    make_box("KitchenDoor_Threshold", (0.0, 0.0, 0.02), (2.00, 0.26, 0.04), MILLER_OAK_DK)
    # The wooden screen door — propped OPEN flat against the west
    # siding (opens outward; the gap itself stays clear: the camera
    # shoots through it, and the kitchen's own hunter-green door
    # swings inward out of frame). Charcoal frame, empty panels.
    for sgn, sx in ((-1, -1.88), (+1, -1.12)):
        make_box(f"ScreenDoor_Stile_{sgn:+d}", (sx, 0.16, 1.07),
                 (0.05, 0.04, 2.10), MILLER_SCREEN_FR)
    for ri, rz in enumerate((2.10, 1.10, 0.06)):
        make_box(f"ScreenDoor_Rail_{ri}", (-1.5, 0.16, rz), (0.81, 0.04, 0.05),
                 MILLER_SCREEN_FR)
    make_box("ScreenDoor_Kick", (-1.5, 0.155, 0.31), (0.78, 0.02, 0.44),
             MILLER_SCREEN_FR)
    make_box("ScreenDoor_Handle", (-1.16, 0.20, 1.05), (0.03, 0.03, 0.14),
             P.METAL_BLACK)
    make_door_hinges("ScreenDoor_Hinge", edge_x=-1.06, edge_y=0.13,
                     edge_z_centers=[0.35, 1.07, 1.80], axis='X')
    # Porch-light sconce east of the door (Porch Lights · Mid-August)
    make_box("Sconce_Backplate", (1.38, 0.125, 2.00), (0.11, 0.03, 0.18), P.METAL_BLACK)
    make_box("Sconce_Arm", (1.38, 0.18, 2.06), (0.04, 0.10, 0.03), P.METAL_BLACK)
    make_cyl("Sconce_Bulb", (1.38, 0.24, 1.99), 0.042, 0.10, COL_PORCHBULB, segments=10)
    make_cyl("Sconce_Cap", (1.38, 0.24, 2.055), 0.055, 0.03, P.METAL_BLACK, segments=10)
    # Doormat inside the doorway
    make_box("Doormat", (0.0, 0.62, 0.008), (1.05, 0.60, 0.014), (0.55, 0.44, 0.30, 1.0))
    # House wings beyond the porch (same siding plane) + eaves
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"House_Wing_{seg}", (sgn * 4.6, -0.05, 1.55), (3.2, 0.20, 3.20),
                 MILLER_SIDING)
        for zi in range(5):
            make_box(f"Wing_{seg}_Seam_{zi}", (sgn * 4.6, 0.055, 0.40 + zi * 0.56),
                     (3.16, 0.012, 0.028), MILLER_SIDING_SH)
        make_box(f"Wing_{seg}_Eave", (sgn * 4.6, 0.05, 3.22), (3.3, 0.60, 0.16),
                 MILLER_ROOF)
        make_box(f"Wing_{seg}_Fascia", (sgn * 4.6, 0.32, 3.12), (3.3, 0.06, 0.12),
                 MILLER_TRIM)
    # Hose bib low on the west wing + the coiled garden hose
    make_cyl("HoseBib_Pipe", (-3.6, 0.11, 0.32), 0.018, 0.14, P.METAL_STEEL, axis='Y')
    make_box("HoseBib_Handle", (-3.6, 0.20, 0.36), (0.06, 0.02, 0.02), (0.70, 0.57, 0.30, 1.0))
    for hi in range(2):
        make_cyl(f"HoseCoil_{hi}", (-3.35, 0.55, LAWN_Z + 0.03 + hi * 0.045),
                 0.17 - hi * 0.02, 0.045, (0.24, 0.36, 0.24, 1.0), segments=12)


# ═════════════════════════════════════════════════════════════════
# SCREEN ENCLOSURE — kneewall + charcoal frame grid on N/E/W, the
# screen door to the yard steps in the north-east bay (Anita's way
# in and out, vol6_ch17_table). Openings are EMPTY per the playbook
# no-transparency rule — the "screen" the dust motes hang in is
# frame and light, not a mesh.
# ═════════════════════════════════════════════════════════════════
def build_screen_enclosure():
    # Corner + line posts (structural, builder-white)
    posts = [(-2.97, 3.97), (2.97, 3.97), (-2.97, 0.28), (2.97, 0.28),
             (0.0, 3.97), (-2.97, 2.10), (2.97, 2.10)]
    for pi, (px, py) in enumerate(posts):
        make_box(f"Porch_Post_{pi}", (px, py, 1.40), (0.09, 0.09, 2.80), MILLER_TRIM)
    # Kneewalls + cap rails. North: broken for the screen-door bay
    # x 1.55..2.45.
    make_box("Kneewall_N_W", (-0.725, 3.97, 0.325), (4.55, 0.06, 0.65), MILLER_TRIM)
    make_box("Kneewall_N_E", (2.725, 3.97, 0.325), (0.55, 0.06, 0.65), MILLER_TRIM)
    make_box("KneeCap_N_W", (-0.725, 3.97, 0.675), (4.55, 0.12, 0.05), MILLER_DECK)
    make_box("KneeCap_N_E", (2.725, 3.97, 0.675), (0.55, 0.12, 0.05), MILLER_DECK)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Kneewall_{seg}", (sgn * 2.97, 2.10, 0.325), (0.06, 3.70, 0.65),
                 MILLER_TRIM)
        make_box(f"KneeCap_{seg}", (sgn * 2.97, 2.10, 0.675), (0.12, 3.70, 0.05),
                 MILLER_DECK)
    # Screen-frame verticals (charcoal, thin) dividing the bays
    for vi, vx in enumerate((-2.0, -1.0, 1.0)):
        make_box(f"ScreenMull_N_{vi}", (vx, 3.97, 1.725), (0.045, 0.05, 2.10),
                 MILLER_SCREEN_FR)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        for vi, vy in enumerate((1.35, 2.85)):
            make_box(f"ScreenMull_{seg}_{vi}", (sgn * 2.97, vy, 1.725),
                     (0.05, 0.045, 2.10), MILLER_SCREEN_FR)
    # Horizontal mid-rails at eye height
    make_box("ScreenRail_N_W", (-0.725, 3.97, 1.55), (4.55, 0.045, 0.04), MILLER_SCREEN_FR)
    make_box("ScreenRail_N_E", (2.725, 3.97, 1.55), (0.55, 0.045, 0.04), MILLER_SCREEN_FR)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"ScreenRail_{seg}", (sgn * 2.97, 2.10, 1.55), (0.045, 3.70, 0.04),
                 MILLER_SCREEN_FR)
    # Top header beams under the roof
    make_box("Header_N", (0.0, 3.97, 2.72), (6.10, 0.10, 0.16), MILLER_TRIM)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Header_{seg}", (sgn * 2.97, 2.10, 2.72), (0.10, 3.85, 0.16),
                 MILLER_TRIM)
    # The yard screen door (closed) in the NE bay + steps down
    for sgn, sx in ((-1, 1.585), (+1, 2.415)):
        make_box(f"YardDoor_Stile_{sgn:+d}", (sx, 3.97, 1.075), (0.05, 0.045, 2.15),
                 MILLER_SCREEN_FR)
    for ri, rz in enumerate((2.12, 1.08, 0.06)):
        make_box(f"YardDoor_Rail_{ri}", (2.0, 3.97, rz), (0.78, 0.045, 0.05),
                 MILLER_SCREEN_FR)
    make_box("YardDoor_Kick", (2.0, 3.965, 0.32), (0.76, 0.02, 0.46), MILLER_SCREEN_FR)
    make_box("YardDoor_Handle", (2.36, 3.90, 1.06), (0.03, 0.03, 0.14), P.METAL_BLACK)
    make_box("YardStep_0", (2.0, 4.36, -0.14), (1.10, 0.34, 0.09), MILLER_DECK)
    make_box("YardStep_1", (2.0, 4.70, -0.30), (1.10, 0.34, 0.09), MILLER_DECK)


# ═════════════════════════════════════════════════════════════════
# ROOF — beadboard porch ceiling, shingle slab, white fascia, one
# downspout. Flat underside at CEIL (camera-safe).
# ═════════════════════════════════════════════════════════════════
def build_roof():
    make_box("Porch_Ceiling", (0.0, 2.0, CEIL + 0.05), (6.6, 4.6, 0.10),
             (0.90, 0.88, 0.80, 1.0))
    for bi in range(6):
        make_box(f"Ceiling_Bead_{bi}", (0.0, 0.55 + bi * 0.58, CEIL - 0.006),
                 (6.5, 0.010, 0.006), (0.76, 0.74, 0.66, 1.0))
    make_box("Porch_RoofSlab", (0.0, 2.10, CEIL + 0.19), (6.9, 4.7, 0.12), MILLER_ROOF)
    make_box("Fascia_N", (0.0, 4.42, CEIL + 0.10), (6.9, 0.06, 0.16), MILLER_TRIM)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_box(f"Fascia_{seg}", (sgn * 3.42, 2.10, CEIL + 0.10), (0.06, 4.7, 0.16),
                 MILLER_TRIM)
    make_cyl("Downspout", (3.30, 4.30, 1.15), 0.040, 3.30, MILLER_TRIM)


# ═════════════════════════════════════════════════════════════════
# THE WICKER CHAIR — Bianca's mother's, Lubbock 1989, three houses
# since (vol6_ch11_kitchen:678). Against the back (house) wall,
# facing the yard. Flat arm boards — the coffee cup goes down on
# the arm (vol6_ch11_eileen:46). Round geometry at eye level per
# the playbook: cylinder legs/arms, rounded crest.
# ═════════════════════════════════════════════════════════════════
def build_wicker_chair():
    cx, cy = 1.70, 0.62
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Wicker_Leg_{li}", (cx + sx * 0.30, cy + sy * 0.24, 0.20),
                 0.026, 0.40, MILLER_WICKER_DK)
    make_box("Wicker_Seat", (cx, cy, 0.42), (0.62, 0.56, 0.075), MILLER_WICKER)
    # Woven-skirt weave lines under the seat lip
    for wi in range(3):
        make_box(f"Wicker_SkirtWeave_{wi}", (cx, cy - 0.285, 0.315 + wi * 0.035),
                 (0.60, 0.008, 0.014), MILLER_WICKER_DK)
    make_box("Wicker_Cushion", (cx, cy + 0.02, 0.475), (0.56, 0.50, 0.055),
             (0.62, 0.58, 0.46, 1.0))
    # Arms: cylinder rails + FLAT top boards (the cup lands here)
    for sgn, seg in ((-1, "W"), (+1, "E")):
        make_cyl(f"Wicker_ArmRail_{seg}", (cx + sgn * 0.34, cy + 0.02, 0.63),
                 0.038, 0.54, MILLER_WICKER, axis='Y', segments=10)
        make_box(f"Wicker_ArmBoard_{seg}", (cx + sgn * 0.34, cy + 0.02, 0.665),
                 (0.11, 0.50, 0.020), MILLER_WICKER)
        make_cyl(f"Wicker_ArmPost_{seg}", (cx + sgn * 0.34, cy - 0.20, 0.53),
                 0.022, 0.20, MILLER_WICKER_DK)
    # Back: woven panel rising to a rounded crest
    make_box("Wicker_Back", (cx, cy + 0.295, 1.00), (0.62, 0.06, 0.90), MILLER_WICKER)
    for wi in range(5):
        make_box(f"Wicker_BackWeave_{wi}", (cx, cy + 0.26, 0.66 + wi * 0.16),
                 (0.58, 0.008, 0.020), MILLER_WICKER_DK)
    make_cyl("Wicker_Crest", (cx, cy + 0.295, 1.45), 0.10, 0.62, MILLER_WICKER,
             axis='X', segments=12)
    # The coffee cup, down on the west arm (vol6_ch11_eileen:46)
    make_cyl("Wicker_Cup", (cx - 0.34, cy - 0.04, 0.72), 0.036, 0.09, COL_CERAMIC,
             segments=10)
    make_cyl("Wicker_Cup_Coffee", (cx - 0.34, cy - 0.04, 0.762), 0.028, 0.006,
             COL_COFFEE, segments=10)
    make_box("Wicker_Cup_Handle", (cx - 0.295, cy - 0.04, 0.72), (0.016, 0.014, 0.05),
             COL_CERAMIC)


# ═════════════════════════════════════════════════════════════════
# SEATING + SIDE TABLE — the company chair is one of the oak
# dinette chairs from the kitchen (shared _miller_chair — same set,
# same file-to-file geometry). Wicker side table: the small plate
# with the coffee-cake slice (vol6_ch17_porch:38), the iced tea
# (vol6_ch15_home:80), the paperback (vol6_ch15_home:200).
# ═════════════════════════════════════════════════════════════════
def build_seating():
    _miller_chair("PorchChair", -1.45, 1.85, 'S')
    # Side table between the chairs (clear of the doormat)
    tx, ty = 0.60, 0.90
    make_cyl("SideTable_Top", (tx, ty, 0.50), 0.23, 0.035, MILLER_WICKER, segments=12)
    make_cyl("SideTable_Ring", (tx, ty, 0.465), 0.20, 0.03, MILLER_WICKER_DK, segments=12)
    for li in range(3):
        lx, ly = [(-0.13, -0.09), (0.13, -0.09), (0.0, 0.15)][li]
        make_cyl(f"SideTable_Leg_{li}", (tx + lx, ty + ly, 0.235), 0.016, 0.47,
                 MILLER_WICKER_DK)
    # The small plate + coffee-cake slice
    make_cyl("Plate", (tx - 0.08, ty + 0.05, 0.524), 0.085, 0.012, COL_CERAMIC,
             segments=12)
    make_box("CoffeeCake", (tx - 0.08, ty + 0.05, 0.548), (0.09, 0.06, 0.035),
             (0.78, 0.60, 0.36, 1.0))
    make_box("CoffeeCake_Crumb", (tx - 0.08, ty + 0.05, 0.568), (0.085, 0.055, 0.006),
             (0.62, 0.44, 0.24, 1.0))
    # The iced tea, sweating in the August air
    make_cyl("IcedTea_Glass", (tx + 0.12, ty - 0.02, 0.583), 0.033, 0.125,
             (0.74, 0.78, 0.76, 1.0), segments=10)
    make_cyl("IcedTea_Fill", (tx + 0.12, ty - 0.02, 0.588), 0.028, 0.10, COL_TEA,
             segments=10)
    # Bianca's paperback
    make_box("Paperback", (tx + 0.02, ty - 0.14, 0.535), (0.125, 0.175, 0.028),
             (0.42, 0.46, 0.52, 1.0))
    make_box("Paperback_Pages", (tx + 0.078, ty - 0.14, 0.535), (0.012, 0.165, 0.022),
             P.PAPER)
    # A potted plant in the NW corner keeps the porch lived-in
    make_floor_plant("PorchPlant", (-2.45, 3.35, 0.0))


# ═════════════════════════════════════════════════════════════════
# YARD — mid-August Texas: Bermuda browning in patches (the back
# yard doesn't get the sprinklers), the crepe myrtle in the corner
# in late bloom, the neighbor's oak (the mockingbird's), the fence
# lines, and the SAME tract-house massing repeating beyond them —
# HCE Phase I uniformity, the planned under the personal. AC
# condenser on its pad against the west wing.
# ═════════════════════════════════════════════════════════════════
def build_yard():
    make_box("Lawn", (0.0, 11.0, LAWN_Z - 0.05), (26.0, 19.0, 0.10), COL_LAWN_AUG)
    patches = [(-1.8, 5.6, 1.3, 0.9), (1.2, 7.4, 1.0, 0.7), (3.0, 5.2, 0.8, 0.6),
               (-3.6, 8.8, 1.5, 1.0), (0.2, 10.6, 1.1, 0.8), (-5.4, 6.0, 0.9, 0.7)]
    for pi, (px, py, pw, pl) in enumerate(patches):
        make_box(f"Lawn_Patch_{pi}", (px, py, LAWN_Z + 0.004), (pw, pl, 0.006),
                 COL_LAWN_BROWN)
    # THE CREPE MYRTLE in the corner, late bloom, cicadas in it
    # (vol6_ch11_kitchen:686). Multi-trunk + round canopy + blooms.
    mx, my = 3.7, 6.4
    for ti, (tx, ty) in enumerate([(-0.12, -0.06), (0.12, -0.02), (0.0, 0.13)]):
        make_cyl(f"Crepe_Trunk_{ti}", (mx + tx, my + ty, 0.55), 0.045, 2.00,
                 COL_TRUNK)
    for ci, (cr, cz, tint) in enumerate([(0.85, 1.80, COL_CREPE_LEAF),
                                         (0.68, 2.30, COL_CREPE_LEAF),
                                         (0.42, 2.72, COL_CREPE_LEAF)]):
        make_cyl(f"Crepe_Canopy_{ci}", (mx, my, cz), cr, 0.52, tint, segments=10)
    blooms = [(0.0, 0.0, 3.05), (-0.45, 0.25, 2.62), (0.48, -0.15, 2.60),
              (0.20, 0.42, 2.88), (-0.30, -0.40, 2.85)]
    for bi, (bx, by, bz) in enumerate(blooms):
        make_cyl(f"Crepe_Bloom_{bi}", (mx + bx, my + by, bz), 0.16, 0.20,
                 COL_CREPE_BLOOM, segments=8)
    # THE NEIGHBOR'S OAK (the mockingbird, vol6_ch17_porch:106) —
    # big rounded canopy west of the yard.
    ox, oy = -5.2, 9.6
    make_cyl("Oak_Trunk", (ox, oy, 0.85), 0.24, 2.60, COL_TRUNK, segments=10)
    for ci, (cr, cz, ch, tint) in enumerate([(2.6, 2.70, 0.95, COL_OAK_CANOPY),
                                             (2.1, 3.55, 0.90, COL_OAK_CANOPY_2),
                                             (1.3, 4.30, 0.80, COL_OAK_CANOPY)]):
        make_cyl(f"Oak_Canopy_{ci}", (ox, oy, cz), cr, ch, tint, segments=10)
    # Fence lines — weathered pine privacy fence: the east run
    # (Eileen's side) + the rear run. Long boards + seams, not 60
    # pickets.
    make_box("Fence_E", (5.3, 7.9, LAWN_Z + 0.90), (0.05, 11.0, 1.80), MILLER_FENCE)
    for si in range(8):
        make_box(f"Fence_E_Seam_{si}", (5.27, 3.1 + si * 1.35, LAWN_Z + 0.90),
                 (0.008, 0.020, 1.76), MILLER_FENCE_SEAM)
    make_box("Fence_E_Cap", (5.3, 7.9, LAWN_Z + 1.83), (0.11, 11.0, 0.05), MILLER_FENCE_SEAM)
    for pi in range(4):
        make_box(f"Fence_E_Post_{pi}", (5.3, 3.4 + pi * 3.0, LAWN_Z + 0.92),
                 (0.11, 0.11, 1.88), MILLER_FENCE_SEAM)
    make_box("Fence_R", (-1.3, 13.4, LAWN_Z + 0.90), (13.2, 0.05, 1.80), MILLER_FENCE)
    for si in range(9):
        make_box(f"Fence_R_Seam_{si}", (-6.6 + si * 1.35, 13.37, LAWN_Z + 0.90),
                 (0.020, 0.008, 1.76), MILLER_FENCE_SEAM)
    make_box("Fence_R_Cap", (-1.3, 13.4, LAWN_Z + 1.83), (13.2, 0.11, 0.05),
             MILLER_FENCE_SEAM)
    for pi in range(5):
        make_box(f"Fence_R_Post_{pi}", (-6.9 + pi * 2.8, 13.4, LAWN_Z + 0.92),
                 (0.11, 0.11, 1.88), MILLER_FENCE_SEAM)
    # The tract repeating beyond the fences — the SAME house massing
    # in the seeded palette variants (HCE uniformity register).
    for hi, (hx, hy, body) in enumerate([
            (8.6, 10.8, (0.72, 0.66, 0.56, 1.0)),      # tan (BODY_B)
            (-2.4, 17.0, (0.62, 0.58, 0.62, 1.0)),     # grey-blue (BODY_C)
            (7.2, 17.6, (0.78, 0.62, 0.52, 1.0))]):    # peach (BODY_D)
        make_box(f"TractHouse_{hi}_Body", (hx, hy, 1.05), (6.0, 5.0, 3.00), body)
        make_box(f"TractHouse_{hi}_Roof0", (hx, hy, 2.80), (6.6, 5.6, 0.50), MILLER_ROOF)
        make_box(f"TractHouse_{hi}_Roof1", (hx, hy, 3.28), (4.4, 3.7, 0.46), MILLER_ROOF)
        make_box(f"TractHouse_{hi}_Roof2", (hx, hy, 3.68), (2.2, 1.8, 0.34), MILLER_ROOF)
    make_box("TractHouse_0_Window", (5.58, 10.3, 1.45), (0.06, 0.90, 0.70),
             (0.14, 0.15, 0.18, 1.0))
    make_box("TractHouse_1_Window", (-2.4, 14.46, 1.45), (0.90, 0.06, 0.70),
             (0.14, 0.15, 0.18, 1.0))
    # AC condenser on its concrete pad against the west wing
    make_box("AC_Pad", (-4.1, 0.85, LAWN_Z + 0.03), (0.95, 0.95, 0.06), COL_CONCRETE)
    make_box("AC_Unit", (-4.1, 0.85, LAWN_Z + 0.39), (0.74, 0.74, 0.66),
             (0.72, 0.73, 0.70, 1.0))
    make_cyl("AC_FanGrille", (-4.1, 0.85, LAWN_Z + 0.735), 0.28, 0.025,
             (0.30, 0.31, 0.32, 1.0), segments=12)
    for vi in range(3):
        make_box(f"AC_Vent_{vi}", (-4.1, 0.47, LAWN_Z + 0.22 + vi * 0.16),
                 (0.66, 0.012, 0.05), (0.58, 0.59, 0.57, 1.0))
    make_cyl("AC_Lineset", (-3.85, 0.42, LAWN_Z + 0.62), 0.020, 0.75, P.METAL_STEEL,
             axis='Y')


def main():
    clear_scene()
    build_deck()
    build_house_wall()
    build_screen_enclosure()
    build_roof()
    build_wicker_chair()
    build_seating()
    build_yard()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_back_porch.glb"))
    print(f"\n[build_miller_back_porch] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
