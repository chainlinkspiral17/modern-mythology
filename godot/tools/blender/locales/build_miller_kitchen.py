"""Miller Kitchen — 1428 Meadowlark Circle, Harmony Creek, TX —
vol6 hero locale (11 VN bg refs, all vol6; heaviest users:
vol6_ch17_table "The Four-Thirty Table" and vol6_ch11_kitchen "The
Kitchen at Four Thirty").

Bianca Miller's kitchen in a NexCorp-built HCE tract house — the
four-thirty room. Canon baked in:

  · vol6_ch11_kitchen:86 — "The kitchen window faces the front yard
    and the cul-de-sac." Stage-north here = the front of the house:
    the window over the sink looks across the cul-de-sac at DON
    GELLER'S PORCH LIGHT (:118, vol6_ch17_table:38) — modeled, warm,
    dead ahead of the camera. Sheer curtain on the window
    (vol6_ch5_miller_drive:75).
  · vol6_ch11_kitchen:78 — "the small under-cabinet light over the
    sink, which gives the kitchen the soft contained light it does
    in this hour": warm under-cabinet strips flank the sink (real
    Light3D stays scene-side).
  · vol6_ch11_kitchen:106 — the table's seat geography, kept
    exactly: rectangular table, Bianca's chair on the LONG side,
    Mike's chair on the SHORT SIDE NEAR THE WINDOW (north), "Sammy
    at the head" (south).
  · vol6_ch17_table:192 — "The Cuisinart is still on, running its
    own pot on the counter"; :156 — the two jars of Peggy's peach
    preserves "on the counter next to the coffee pot"; :1472 — the
    foil-wrapped loaf (the cinnamon coffee cake); :84 — Eileen's
    small stainless insulated press pot on the table; :532 — the
    small white bakery bag (three kolaches, the place on Alamosa).
  · vol6_ch6_miller_kitchen:106 — "the phone in the kitchen rings.
    It is the landline. The landline never rings." — beige wall
    phone with the coiled cord, east wall.
  · vol6_ch6_miller_kitchen:32 — the Friday cast-iron: the skillet
    lives on the range. Sink / dishwasher / drying rack per
    vol6_ch11_kitchen:646-662, vol6_ch17_porch:130. Pantry
    (vol6_ch11_kitchen:260). Microwave (vol6_ch5_miller_drive:83).
  · Wall clock frozen at 4:30 — the four-thirty hour
    (vol6_ch17_table:1441). The New Auburn Sentinel folded on the
    table (vol6_ch17_porch delivery canon).
  · Sam (17, the Kwik Stop register, 8-to-4): her backpack waits by
    the hunter-green back door with the license-plate notebook —
    "spiral-bound, college-ruled, 9x6, blue cover" — in the front
    pocket (lore/planned_community/sam_miller.md:181), the travel
    mug she fills on the way out (vol6_ch17_table:1230) at her
    place, her Kwik Stop shift schedule magneted to the fridge.
  · Exterior (through the window): the sprinkler-kept front lawn
    (back yard browns; the front is on the cycle —
    vol6_ch11_eileen:512), the cracked sprinkler head
    (vol6_ch0_prelude:99), Sam's silver Corolla in the driveway
    (vol6_ch4_kitchen:26), and the HCE standards from
    _HCE_LAYOUT_INVENTORY: foundation shrubs in mulch rings, the
    front walk, one specimen tree — the same tract model repeating
    around the cul-de-sac.

HCE register: standardized bones (builder eggshell walls, golden-oak
cabinets, almond laminate + appliances, vinyl floor, the 1991
wallpaper border) with the Millers' life layered on: the preserves,
the pickle-jar fridge, the notebook in the backpack.

Shell footprint kept from the scaffold (7 x 6, CEIL 2.6, gap
x -1..+1 in the south wall = the hall doorway the Background3D
camera preset (0, 2.30, +0.5 / yaw 180 / fov 60) shoots through).
Window is a REAL OPENING with frame + sash rails, no glass
(playbook no-transparency rule).
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
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.6

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

# Kitchen-only palette
COL_VINYL       = (0.82, 0.77, 0.66, 1.0)     # sheet-vinyl floor
COL_VINYL_SEAM  = (0.63, 0.56, 0.44, 1.0)
COL_BORDER      = (0.44, 0.54, 0.56, 1.0)     # 1991 wallpaper border
COL_SHEER       = (0.95, 0.93, 0.86, 1.0)     # the sheer curtain
COL_GLOW_WARM   = (0.99, 0.90, 0.66, 1.0)     # under-cabinet light
COL_NIGHT       = (0.09, 0.11, 0.15, 1.0)     # pre-dawn through the back door
COL_STEEL_DK    = (0.44, 0.46, 0.48, 1.0)

PAL_WALL = {"wall": MILLER_INT_WALL, "baseboard": MILLER_BASEBOARD}

GRADE_Z = -0.40           # front-yard grade outside the window
WIN_W = 1.70              # window opening x -0.85..+0.85
WIN_SILL = 0.95
WIN_HEAD = 2.15


# ═════════════════════════════════════════════════════════════════
# SHELL — vinyl floor, eggshell walls, flat drywall ceiling (no
# drop-tile grid — this is a house, not the Kwik Stop), the 1991
# wallpaper border, the hall doorway casing in the scaffold gap.
# North wall carries the front window opening.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_VINYL, "seam": COL_VINYL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall — window opening x -0.85..+0.85, sill 0.95, head 2.15
    make_wall("Wall_N_W", (-(WIN_W / 2.0 + (ROOM_W / 2.0 - WIN_W / 2.0) / 2.0 + 0.1),
              ROOM_D, 0), length=ROOM_W / 2.0 - WIN_W / 2.0 + 0.2, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+(WIN_W / 2.0 + (ROOM_W / 2.0 - WIN_W / 2.0) / 2.0 + 0.1),
              ROOM_D, 0), length=ROOM_W / 2.0 - WIN_W / 2.0 + 0.2, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_SillFill", (0.0, ROOM_D, WIN_SILL / 2.0), (WIN_W, 0.20, WIN_SILL),
             MILLER_INT_WALL)
    make_box("Wall_N_HeadFill", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.20, CEIL - WIN_HEAD), MILLER_INT_WALL)
    # South wall — scaffold hall gap x -1..+1 kept (camera doorway)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             MILLER_INT_WALL)
    # Hall doorway casing — open to the front of the house / stairs
    for sgn in (-1, +1):
        make_box(f"HallDoor_Jamb_{sgn:+d}", (sgn * 1.03, 0.0, 1.00), (0.10, 0.26, 2.00),
                 MILLER_TRIM)
    make_box("HallDoor_Head", (0.0, 0.0, 2.05), (2.26, 0.26, 0.10), MILLER_TRIM)
    # Flat drywall ceiling — no grid, no water stains
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": (0.93, 0.91, 0.85, 1.0)},
                 with_grid=False, with_stains=False)
    # The 1991 wallpaper border (E / W / S walls; the N wall carries
    # the window + clock instead)
    make_box("Border_W", (-ROOM_W / 2.0 + 0.112, ROOM_D / 2.0, 2.40),
             (0.012, ROOM_D + 0.2, 0.16), COL_BORDER)
    make_box("Border_E", (+ROOM_W / 2.0 - 0.112, ROOM_D / 2.0, 2.40),
             (0.012, ROOM_D + 0.2, 0.16), COL_BORDER)
    make_box("Border_S", (0.0, 0.112, 2.40), (ROOM_W + 0.2, 0.012, 0.16), COL_BORDER)


# ═════════════════════════════════════════════════════════════════
# WINDOW — the front window over the sink: REAL OPENING, white
# double-hung sash frame (meeting rail + upper muntins), sheer
# curtain side panels + valance on a rod
# (vol6_ch5_miller_drive:75). Bianca stands here at 4:30 watching
# the cul-de-sac.
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D           # wall centerline 6.0; interior face 5.9
    # Sash frame inside the opening
    make_box("Win_FrameT", (0.0, wy, WIN_HEAD - 0.03), (WIN_W, 0.14, 0.06), MILLER_TRIM)
    make_box("Win_FrameB", (0.0, wy, WIN_SILL + 0.03), (WIN_W, 0.14, 0.06), MILLER_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Jamb_{sgn:+d}", (sgn * (WIN_W / 2.0 - 0.03), wy, 1.55),
                 (0.06, 0.14, 1.20), MILLER_TRIM)
    make_box("Win_MeetingRail", (0.0, wy, 1.56), (WIN_W - 0.08, 0.10, 0.06), MILLER_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Muntin_{sgn:+d}", (sgn * 0.28, wy - 0.02, 1.86),
                 (0.035, 0.06, 0.56), MILLER_TRIM)
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
    # Sheer curtain — rod, side panels, valance
    make_cyl("Curtain_Rod", (0.0, wy - 0.16, 2.30), 0.013, 2.10, (0.70, 0.57, 0.30, 1.0),
             axis='X', segments=8)
    for sgn in (-1, +1):
        make_cyl(f"Curtain_Finial_{sgn:+d}", (sgn * 1.06, wy - 0.16, 2.30), 0.028, 0.05,
                 (0.70, 0.57, 0.30, 1.0), axis='X', segments=8)
        make_box(f"Curtain_Panel_{sgn:+d}", (sgn * 0.82, wy - 0.155, 1.62),
                 (0.30, 0.030, 1.30), COL_SHEER)
        make_box(f"Curtain_PanelFold_{sgn:+d}", (sgn * 0.74, wy - 0.175, 1.58),
                 (0.10, 0.018, 1.20), (0.90, 0.88, 0.80, 1.0))
    make_box("Curtain_Valance", (0.0, wy - 0.155, 2.16), (1.92, 0.030, 0.22), COL_SHEER)
    # The clock above the window — frozen at 4:30, the four-thirty
    # hour (vol6_ch17_table).
    make_wall_clock("Clock", (0.0, wy - 0.14, 2.37), frozen_hour=4, frozen_min=30)


# ═════════════════════════════════════════════════════════════════
# COUNTER RUN — golden-oak base + upper cabinets along the north
# wall, almond laminate. Sink under the window; dishwasher beside
# it; slide-in range with the CAST-IRON SKILLET; hood; microwave;
# the Cuisinart with the peach preserves next to it; the
# foil-wrapped coffee cake; drying rack. Warm under-cabinet strips
# flank the window (the 4:30 light source — vol6_ch11_kitchen:78).
# ═════════════════════════════════════════════════════════════════
def build_counter_run():
    wallf = ROOM_D - 0.10                     # interior wall face y 5.9
    # Base cabinets: x -3.4..+1.95, depth 0.58 (front face y ~5.41)
    make_box("Base_Body", (-0.725, 5.70, 0.445), (5.35, 0.58, 0.79), MILLER_OAK)
    make_box("Base_Kick", (-0.725, 5.44, 0.05), (5.25, 0.03, 0.10), MILLER_OAK_DK)
    make_box("Counter_Top", (-0.725, 5.69, 0.89), (5.42, 0.66, 0.04), MILLER_LAMINATE)
    make_box("Counter_Edge", (-0.725, 5.375, 0.89), (5.42, 0.03, 0.04), MILLER_OAK_DK)
    make_box("Backsplash", (-0.725, 5.885, 1.00), (5.35, 0.03, 0.18), MILLER_LAMINATE)
    # Cabinet door + drawer fronts (skip the appliance bays)
    doors = [(-3.15, 0.46), (-0.72, 0.50), (-0.24, 0.42), (0.24, 0.42),
             (0.74, 0.44), (1.22, 0.44), (1.70, 0.42)]
    for di, (dx, dw) in enumerate(doors):
        make_box(f"Base_Door_{di}", (dx, 5.415, 0.40), (dw - 0.04, 0.02, 0.54),
                 MILLER_OAK)
        make_cyl(f"Base_Knob_{di}", (dx + dw / 2.0 - 0.06, 5.40, 0.62), 0.014, 0.03,
                 (0.70, 0.57, 0.30, 1.0), axis='Y')
        if abs(dx) > 0.5:     # drawers everywhere except the sink front
            make_box(f"Base_Drawer_{di}", (dx, 5.415, 0.775), (dw - 0.04, 0.02, 0.14),
                     MILLER_OAK)
            make_cyl(f"Base_DrawerKnob_{di}", (dx, 5.40, 0.775), 0.014, 0.03,
                     (0.70, 0.57, 0.30, 1.0), axis='Y')
    # Upper cabinets flanking the window (+ short cab over the hood)
    uppers = [("W0", -3.12, 0.56, 1.90, 0.76), ("Hood", -2.45, 0.76, 2.14, 0.28),
              ("W1", -1.50, 1.10, 1.90, 0.76), ("E0", 1.45, 1.00, 1.90, 0.76)]
    for nm, ux, uw, uz, uh in uppers:
        make_box(f"Upper_{nm}", (ux, 5.835, uz), (uw, 0.33, uh), MILLER_OAK)
        make_box(f"Upper_{nm}_Seam", (ux, 5.665, uz), (0.012, 0.012, uh - 0.06),
                 MILLER_OAK_DK)
        make_cyl(f"Upper_{nm}_Knob", (ux - 0.06, 5.66, uz - uh / 2.0 + 0.10),
                 0.013, 0.03, (0.70, 0.57, 0.30, 1.0), axis='Y')
    # THE under-cabinet light strips (vol6_ch11_kitchen:78) — warm
    # baked glow; the scene's real Light3D matches from the .tscn.
    make_box("UnderCabLight_W", (-1.50, 5.70, 1.505), (1.02, 0.05, 0.028), COL_GLOW_WARM)
    make_box("UnderCabLight_E", (1.45, 5.70, 1.505), (0.92, 0.05, 0.028), COL_GLOW_WARM)
    # Sink under the window + faucet + dish soap
    make_box("Sink_Rim", (0.0, 5.70, 0.925), (0.82, 0.52, 0.02), P.METAL_STEEL)
    make_box("Sink_Basin", (0.0, 5.70, 0.83), (0.70, 0.42, 0.17), P.METAL_STEEL,
             open_faces={'+Z'})
    make_box("Sink_BasinFloor", (0.0, 5.70, 0.752), (0.66, 0.38, 0.012), COL_STEEL_DK)
    make_cyl("Faucet_Base", (0.0, 5.92, 0.955), 0.030, 0.04, P.METAL_STEEL)
    make_cyl("Faucet_Riser", (0.0, 5.92, 1.06), 0.016, 0.20, P.METAL_STEEL)
    make_cyl("Faucet_Spout", (0.0, 5.82, 1.15), 0.014, 0.22, P.METAL_STEEL, axis='Y')
    make_box("Faucet_Handle", (0.10, 5.92, 1.17), (0.08, 0.02, 0.02), P.METAL_STEEL)
    make_cyl("DishSoap", (0.36, 5.90, 0.985), 0.022, 0.13, (0.72, 0.60, 0.30, 1.0))
    # Drying rack east of the sink — the washed plate + a mug
    make_box("DryRack_Tray", (0.85, 5.72, 0.925), (0.32, 0.40, 0.015), MILLER_TRIM)
    for wi in range(4):
        make_box(f"DryRack_Wire_{wi}", (0.73 + wi * 0.08, 5.72, 0.985),
                 (0.010, 0.36, 0.09), P.METAL_STEEL)
    make_cyl("DryRack_Plate", (0.85, 5.72, 1.03), 0.10, 0.014, COL_CERAMIC, axis='Y',
             segments=12)
    make_cyl("DryRack_Mug", (0.85, 5.56, 0.975), 0.036, 0.09, COL_CERAMIC, segments=10)
    # Dishwasher west of the sink
    make_box("DW_Front", (-1.35, 5.42, 0.45), (0.60, 0.025, 0.74), MILLER_APPLIANCE)
    make_box("DW_Handle", (-1.35, 5.40, 0.80), (0.55, 0.03, 0.04), P.METAL_STEEL)
    make_box("DW_Controls", (-1.35, 5.405, 0.72), (0.50, 0.012, 0.05), COL_STEEL_DK)
    # Slide-in range + the cast-iron skillet (Friday roasts,
    # vol6_ch6_miller_kitchen:32) + hood
    make_box("Range_Body", (-2.45, 5.67, 0.45), (0.76, 0.64, 0.90), MILLER_APPLIANCE)
    make_box("Range_Cooktop", (-2.45, 5.67, 0.915), (0.76, 0.64, 0.02), P.METAL_BLACK)
    for bi, (bx, by) in enumerate([(-0.19, -0.16), (0.19, -0.16), (-0.19, 0.16),
                                   (0.19, 0.16)]):
        make_cyl(f"Range_Burner_{bi}", (-2.45 + bx, 5.67 + by, 0.930), 0.085, 0.010,
                 (0.12, 0.11, 0.10, 1.0), segments=10)
    make_box("Range_Backguard", (-2.45, 5.955, 0.98), (0.76, 0.05, 0.12), MILLER_APPLIANCE)
    for ki in range(4):
        make_cyl(f"Range_Knob_{ki}", (-2.69 + ki * 0.16, 5.925, 0.99), 0.018, 0.025,
                 P.METAL_BLACK, axis='Y')
    make_box("Range_OvenDoor", (-2.45, 5.345, 0.46), (0.70, 0.02, 0.52), MILLER_APPLIANCE)
    make_box("Range_OvenWindow", (-2.45, 5.335, 0.50), (0.42, 0.012, 0.22), P.METAL_BLACK)
    make_box("Range_OvenHandle", (-2.45, 5.33, 0.76), (0.72, 0.03, 0.03), P.METAL_STEEL)
    make_cyl("Skillet_Pan", (-2.64, 5.51, 0.965), 0.14, 0.055, (0.13, 0.13, 0.14, 1.0),
             segments=12)
    make_box("Skillet_Handle", (-2.64, 5.30, 0.97), (0.035, 0.20, 0.028),
             (0.13, 0.13, 0.14, 1.0))
    make_box("Hood_Body", (-2.45, 5.77, 1.96), (0.76, 0.44, 0.14), MILLER_APPLIANCE)
    make_box("Hood_Lip", (-2.45, 5.56, 1.90), (0.76, 0.03, 0.05), P.METAL_STEEL)
    # Counter props east of the sink: THE CUISINART + the two jars
    # of Peggy's peach preserves next to the pot (vol6_ch17_table)
    make_box("Cuisinart_Body", (1.30, 5.80, 1.08), (0.24, 0.26, 0.34), MILLER_TRIM)
    make_box("Cuisinart_Basket", (1.30, 5.74, 1.28), (0.22, 0.30, 0.07), MILLER_TRIM)
    make_cyl("Cuisinart_Carafe", (1.30, 5.68, 0.99), 0.068, 0.155, (0.74, 0.78, 0.76, 1.0),
             segments=12)
    make_cyl("Cuisinart_Coffee", (1.30, 5.68, 0.955), 0.058, 0.075, COL_COFFEE,
             segments=12)
    make_box("Cuisinart_Switch", (1.30, 5.665, 1.13), (0.05, 0.012, 0.03),
             (0.86, 0.42, 0.32, 1.0))
    for ji, (jx, jy) in enumerate([(1.60, 5.76), (1.70, 5.62)]):
        make_cyl(f"Preserves_{ji}_Jar", (jx, jy, 0.962), 0.042, 0.10,
                 (0.85, 0.55, 0.30, 1.0), segments=10)
        make_cyl(f"Preserves_{ji}_Lid", (jx, jy, 1.018), 0.045, 0.018,
                 (0.70, 0.57, 0.30, 1.0), segments=10)
    # The foil-wrapped loaf — the cinnamon coffee cake (ch17:1472)
    make_box("FoilLoaf", (-0.65, 5.76, 0.955), (0.28, 0.14, 0.09), (0.80, 0.81, 0.84, 1.0))
    make_box("FoilLoaf_Seam", (-0.65, 5.76, 1.002), (0.24, 0.02, 0.008), COL_STEEL_DK)
    # Microwave in the west corner (vol6_ch5_miller_drive:83)
    make_box("Microwave_Body", (-3.02, 5.72, 1.065), (0.52, 0.38, 0.30), MILLER_APPLIANCE)
    make_box("Microwave_Window", (-3.10, 5.525, 1.065), (0.30, 0.012, 0.22), P.METAL_BLACK)
    make_box("Microwave_Handle", (-2.80, 5.525, 1.065), (0.03, 0.015, 0.24), COL_STEEL_DK)
    # Paper towels under the west uppers; salt + pepper by the range
    make_cyl("PaperTowel_Roll", (-1.50, 5.76, 1.40), 0.055, 0.26, MILLER_TRIM, axis='X',
             segments=10)
    make_cyl("Salt", (-1.95, 5.84, 0.965), 0.020, 0.11, COL_CERAMIC, segments=8)
    make_cyl("Pepper", (-1.87, 5.80, 0.965), 0.020, 0.11, (0.36, 0.30, 0.26, 1.0),
             segments=8)


# ═════════════════════════════════════════════════════════════════
# FRIDGE — almond top-freezer against the north wall east of the
# counter. On the door: the HCE newsletter, Sam's Kwik Stop shift
# schedule, one of her grade-school drawings still magneted up.
# (The pickle jar there since 2022 is inside — vol6_ch6:98.)
# ═════════════════════════════════════════════════════════════════
def build_fridge():
    fx, fy = 2.55, 5.55
    make_box("Fridge_Body", (fx, fy, 0.86), (0.82, 0.72, 1.72), MILLER_APPLIANCE)
    make_box("Fridge_DoorSeam", (fx, fy - 0.365, 1.28), (0.80, 0.015, 0.03), COL_STEEL_DK)
    make_box("Fridge_HandleTop", (fx - 0.35, fy - 0.375, 1.46), (0.035, 0.035, 0.26),
             COL_STEEL_DK)
    make_box("Fridge_HandleBot", (fx - 0.35, fy - 0.375, 0.86), (0.035, 0.035, 0.50),
             COL_STEEL_DK)
    make_box("Fridge_Grille", (fx, fy - 0.365, 0.06), (0.78, 0.02, 0.10), COL_STEEL_DK)
    # The HCE newsletter — canon navy + cream (P.BRAND_NAVY_HCE)
    make_box("Fridge_HCENews", (fx + 0.17, fy - 0.373, 1.58), (0.16, 0.012, 0.22),
             P.BRAND_NAVY_HCE)
    make_box("Fridge_HCENews_Head", (fx + 0.17, fy - 0.380, 1.66), (0.14, 0.006, 0.045),
             P.BRAND_NAVY_TXT)
    # Sam's Kwik Stop shift schedule (8-to-4, the register)
    make_box("Fridge_Shifts", (fx - 0.17, fy - 0.373, 1.55), (0.13, 0.012, 0.17), P.PAPER)
    make_box("Fridge_Shifts_Stripe", (fx - 0.17, fy - 0.380, 1.615), (0.11, 0.006, 0.03),
             P.BRAND_RED_KWIK)
    # The old crayon drawing (Sam, age six, still up)
    make_box("Fridge_Drawing", (fx + 0.02, fy - 0.373, 1.22), (0.15, 0.012, 0.12),
             P.PAPER_AGED)
    for mi, (mx, mz, tint) in enumerate([(-0.04, -0.02, (0.86, 0.42, 0.32, 1.0)),
                                         (0.02, 0.01, (0.34, 0.42, 0.54, 1.0)),
                                         (0.05, -0.03, (0.56, 0.58, 0.42, 1.0))]):
        make_box(f"Fridge_Crayon_{mi}", (fx + 0.02 + mx, fy - 0.379, 1.22 + mz),
                 (0.035, 0.004, 0.018), tint)
    # Assorted magnets
    for mi, (mx, mz) in enumerate([(-0.28, 1.70), (0.30, 1.40), (-0.05, 1.66),
                                   (0.24, 1.10), (-0.25, 0.98)]):
        make_box(f"Fridge_Magnet_{mi}", (fx + mx, fy - 0.376, mz), (0.035, 0.008, 0.045),
                 P.SNACK_TINTS[mi % len(P.SNACK_TINTS)])


# ═════════════════════════════════════════════════════════════════
# TABLE — the seat geography from vol6_ch11_kitchen:106, kept
# exactly: rectangular oak table, long axis N-S. Mike's chair on
# the SHORT SIDE NEAR THE WINDOW (north — empty since Alabama;
# Eileen sits in it when she visits), Sam at the head (south),
# Bianca on the long side. Dressed for the four-thirty table:
# bakery bag, mugs, Eileen's stainless press pot, the Sentinel,
# Sam's travel mug at her place.
# ═════════════════════════════════════════════════════════════════
def build_table_zone():
    tx, ty = 0.35, 2.85
    make_box("Table_Top", (tx, ty, 0.745), (0.95, 1.55, 0.045), MILLER_OAK)
    make_box("Table_Apron", (tx, ty, 0.685), (0.82, 1.42, 0.07), MILLER_OAK)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Table_Leg_{li}", (tx + sx * 0.40, ty + sy * 0.68, 0.34),
                 (0.055, 0.055, 0.68), MILLER_OAK_DK)
    _miller_chair("Chair_Mike", tx, ty + 0.93, 'S')      # short side, near the window
    _miller_chair("Chair_Sam", tx, ty - 0.93, 'N')       # the head
    _miller_chair("Chair_Bianca", tx - 0.77, ty, 'E')    # the long side
    _miller_chair("Chair_Guest", tx + 0.77, ty, 'W')     # Eileen / Anita
    top = 0.7675
    # The small white bakery bag (three kolaches, ch17_table:532)
    make_box("BakeryBag", (tx, ty + 0.28, top + 0.075), (0.20, 0.13, 0.15),
             (0.94, 0.92, 0.87, 1.0))
    make_box("BakeryBag_Fold", (tx, ty + 0.28, top + 0.16), (0.21, 0.14, 0.020),
             (0.84, 0.81, 0.75, 1.0))
    # Eileen's small stainless insulated press pot (ch17_table:84)
    make_cyl("PressPot_Body", (tx - 0.28, ty + 0.10, top + 0.085), 0.055, 0.17,
             P.METAL_STEEL, segments=12)
    make_cyl("PressPot_Knob", (tx - 0.28, ty + 0.10, top + 0.185), 0.014, 0.025,
             P.METAL_BLACK)
    make_box("PressPot_Handle", (tx - 0.21, ty + 0.10, top + 0.09), (0.02, 0.016, 0.12),
             P.METAL_BLACK)
    # Coffee mugs at Bianca's and Mike's places
    for nm, (mx, my) in (("Bianca", (tx - 0.30, ty - 0.18)), ("Mike", (tx + 0.02, ty + 0.55))):
        make_cyl(f"Mug_{nm}", (mx, my, top + 0.047), 0.038, 0.095, COL_CERAMIC,
                 segments=10)
        make_cyl(f"Mug_{nm}_Coffee", (mx, my, top + 0.092), 0.030, 0.006, COL_COFFEE,
                 segments=10)
        make_box(f"Mug_{nm}_Handle", (mx + 0.048, my, top + 0.05), (0.016, 0.014, 0.05),
                 COL_CERAMIC)
    # A plate with the cheese danish (vol6_ch11_eileen:312)
    make_cyl("Plate_Danish", (tx + 0.30, ty + 0.16, top + 0.006), 0.085, 0.012,
             COL_CERAMIC, segments=12)
    make_cyl("Danish", (tx + 0.30, ty + 0.16, top + 0.030), 0.046, 0.032,
             (0.82, 0.64, 0.38, 1.0), segments=10)
    make_cyl("Danish_Center", (tx + 0.30, ty + 0.16, top + 0.050), 0.024, 0.008,
             (0.90, 0.82, 0.62, 1.0), segments=8)
    # The New Auburn Sentinel, folded (delivered ~6:15)
    make_box("Sentinel", (tx + 0.02, ty - 0.48, top + 0.008), (0.30, 0.21, 0.016),
             P.NEWSPRINT)
    make_box("Sentinel_Masthead", (tx + 0.02, ty - 0.40, top + 0.018), (0.26, 0.05, 0.004),
             (0.30, 0.28, 0.26, 1.0))
    # Sam's travel mug, filled on the way out (ch17_table:1230)
    make_cyl("TravelMug", (tx - 0.26, ty - 0.55, top + 0.08), 0.040, 0.16, COL_STEEL_DK,
             segments=10)
    make_cyl("TravelMug_Lid", (tx - 0.26, ty - 0.55, top + 0.17), 0.042, 0.02,
             P.METAL_BLACK, segments=10)
    # Sugar bowl + the half-and-half kept for Anita (ch17_table:422)
    make_cyl("SugarBowl", (tx + 0.30, ty - 0.12, top + 0.030), 0.038, 0.06, COL_CERAMIC,
             segments=10)
    make_cyl("SugarBowl_Lid", (tx + 0.30, ty - 0.12, top + 0.068), 0.030, 0.014,
             COL_CERAMIC, segments=10)
    make_box("HalfAndHalf", (tx + 0.42, ty - 0.02, top + 0.045), (0.05, 0.05, 0.09),
             MILLER_TRIM)
    # Napkin holder
    make_box("Napkins_Base", (tx + 0.38, ty + 0.38, top + 0.008), (0.13, 0.09, 0.016),
             MILLER_OAK_DK)
    make_box("Napkins_Stack", (tx + 0.38, ty + 0.38, top + 0.05), (0.11, 0.07, 0.07),
             P.PAPER)


# ═════════════════════════════════════════════════════════════════
# EAST WALL — the hunter-green back door to the porch (same door
# the porch file shows from outside — same MILLER_DOOR_GREEN),
# pre-dawn dark in its panes; Sam's backpack beneath it with the
# blue license-plate notebook in the front pocket
# (sam_miller.md:181). The pantry door. The LANDLINE that never
# rings (vol6_ch6_miller_kitchen:106).
# ═════════════════════════════════════════════════════════════════
def build_east_wall():
    wf = ROOM_W / 2.0 - 0.10          # interior face x 3.4
    # Back door (closed) — hunter green, half-glazed
    make_box("BackDoor_Leaf", (wf - 0.035, 2.0, 1.05), (0.05, 0.92, 2.10),
             MILLER_DOOR_GREEN)
    make_box("BackDoor_Night", (wf - 0.065, 2.0, 1.60), (0.012, 0.62, 0.76), COL_NIGHT)
    make_box("BackDoor_MullV", (wf - 0.072, 2.0, 1.60), (0.012, 0.05, 0.76), MILLER_TRIM)
    make_box("BackDoor_MullH", (wf - 0.072, 2.0, 1.60), (0.012, 0.62, 0.05), MILLER_TRIM)
    for pi, py in enumerate((-0.21, +0.21)):
        make_box(f"BackDoor_Panel_{pi}", (wf - 0.065, 2.0 + py, 0.52),
                 (0.012, 0.30, 0.62), (0.22, 0.31, 0.26, 1.0))
    make_cyl("BackDoor_Knob", (wf - 0.075, 1.66, 1.02), 0.030, 0.035,
             (0.70, 0.57, 0.30, 1.0), axis='X')
    make_box("BackDoor_Deadbolt", (wf - 0.068, 1.66, 1.16), (0.014, 0.045, 0.07),
             (0.70, 0.57, 0.30, 1.0))
    for sgn in (-1, +1):
        make_box(f"BackDoor_Casing_{sgn:+d}", (wf - 0.02, 2.0 + sgn * 0.52, 1.08),
                 (0.06, 0.10, 2.16), MILLER_TRIM)
    make_box("BackDoor_CasingHead", (wf - 0.02, 2.0, 2.20), (0.06, 1.14, 0.10),
             MILLER_TRIM)
    make_box("BackDoor_Mat", (wf - 0.42, 2.0, 0.008), (0.58, 0.92, 0.014),
             (0.55, 0.44, 0.30, 1.0))
    # Sam's backpack + THE NOTEBOOK (spiral-bound, 9x6, blue cover)
    make_box("Backpack_Body", (wf - 0.20, 1.22, 0.22), (0.22, 0.34, 0.44),
             (0.36, 0.42, 0.55, 1.0))
    make_box("Backpack_Flap", (wf - 0.315, 1.22, 0.33), (0.035, 0.30, 0.20),
             (0.30, 0.36, 0.48, 1.0))
    make_box("Backpack_Strap", (wf - 0.10, 1.22, 0.30), (0.03, 0.26, 0.05),
             (0.24, 0.28, 0.38, 1.0))
    make_box("Backpack_Pocket", (wf - 0.325, 1.22, 0.14), (0.045, 0.26, 0.24),
             (0.30, 0.36, 0.48, 1.0))
    make_box("PlateNotebook", (wf - 0.355, 1.22, 0.26), (0.022, 0.155, 0.21),
             (0.22, 0.34, 0.62, 1.0))
    make_box("PlateNotebook_Spiral", (wf - 0.355, 1.30, 0.26), (0.024, 0.014, 0.20),
             P.METAL_STEEL)
    # Pantry door (closed, white six-panel)
    make_box("Pantry_Leaf", (wf - 0.035, 4.15, 1.03), (0.05, 0.90, 2.06), MILLER_TRIM)
    for ci, py in enumerate((-0.21, +0.21)):
        for ri, pz in enumerate((0.48, 1.06, 1.62)):
            make_box(f"Pantry_Panel_{ci}_{ri}", (wf - 0.065, 4.15 + py, pz),
                     (0.012, 0.30, 0.44), (0.85, 0.82, 0.74, 1.0))
    make_cyl("Pantry_Knob", (wf - 0.075, 3.78, 1.00), 0.028, 0.035,
             (0.70, 0.57, 0.30, 1.0), axis='X')
    for sgn in (-1, +1):
        make_box(f"Pantry_Casing_{sgn:+d}", (wf - 0.02, 4.15 + sgn * 0.51, 1.06),
                 (0.06, 0.10, 2.12), MILLER_TRIM)
    make_box("Pantry_CasingHead", (wf - 0.02, 4.15, 2.16), (0.06, 1.12, 0.10),
             MILLER_TRIM)
    # The landline — beige wall phone, coiled cord
    make_box("Phone_Body", (wf - 0.035, 3.12, 1.42), (0.05, 0.11, 0.22),
             (0.82, 0.76, 0.64, 1.0))
    make_box("Phone_Handset", (wf - 0.075, 3.12, 1.47), (0.04, 0.085, 0.24),
             (0.78, 0.72, 0.60, 1.0))
    for ci in range(4):
        make_box(f"Phone_Cord_{ci}", (wf - 0.045, 3.17 + (0.02 if ci % 2 else -0.01),
                 1.28 - ci * 0.10), (0.014, 0.014, 0.09), (0.72, 0.66, 0.54, 1.0))


# ═════════════════════════════════════════════════════════════════
# WEST WALL + CEILING — calendar on the west wall; flat-dome
# ceiling fixture (house fixture, not commercial fluorescents),
# HVAC register, smoke detector.
# ═════════════════════════════════════════════════════════════════
def build_west_wall_and_ceiling():
    make_calendar("Calendar", (-ROOM_W / 2.0 + 0.11, 3.9, 1.55))
    # August: a small red X-marks strip on the grid (the bills week)
    make_box("Calendar_Mark", (-ROOM_W / 2.0 + 0.118, 3.83, 1.42), (0.002, 0.05, 0.04),
             (0.78, 0.18, 0.16, 1.0))
    # Dome light over the table
    make_cyl("DomeLight_Plate", (0.35, 2.85, CEIL - 0.015), 0.19, 0.025,
             (0.70, 0.57, 0.30, 1.0), segments=12)
    make_cyl("DomeLight_Dome", (0.35, 2.85, CEIL - 0.065), 0.165, 0.075,
             (0.97, 0.93, 0.82, 1.0), segments=12)
    make_cyl("DomeLight_Lower", (0.35, 2.85, CEIL - 0.125), 0.115, 0.05,
             (0.97, 0.93, 0.82, 1.0), segments=12)
    make_cyl("DomeLight_Finial", (0.35, 2.85, CEIL - 0.16), 0.018, 0.03,
             (0.70, 0.57, 0.30, 1.0))
    make_hvac_vent("HVAC", (-2.2, 4.6, CEIL), width=0.60, depth=0.35)
    make_smoke_detector("Smoke", (1.6, 0.9, CEIL))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · THE CUL-DE-SAC (through the front window) — what
# Bianca watches at 4:30: the sprinkler-kept front lawn (with the
# cracked head, vol6_ch0_prelude:99), the front walk + mailbox,
# Sam's silver Corolla in the driveway, the street, and DON
# GELLER'S PORCH LIGHT dead ahead across the cul-de-sac — the one
# warm dot in the dark. HCE standards on the far house: foundation
# shrubs, the same massing repeating.
# ═════════════════════════════════════════════════════════════════
def build_exterior_front():
    wallout = ROOM_D + 0.10
    # Ground: front lawn (sprinklered green) / sidewalk / street /
    # far lawn strip
    make_box("Ext_Lawn", (0.0, 7.95, GRADE_Z - 0.05), (22.0, 3.7, 0.10), COL_LAWN_FRONT)
    make_box("Ext_Sidewalk", (0.0, 9.95, GRADE_Z - 0.02), (22.0, 0.75, 0.10), COL_CONCRETE)
    make_box("Ext_Curb", (0.0, 10.38, GRADE_Z - 0.02), (22.0, 0.16, 0.14), COL_CONCRETE)
    make_box("Ext_Street", (0.0, 12.55, GRADE_Z - 0.07), (22.0, 4.2, 0.10), COL_ASPHALT)
    make_box("Ext_FarLawn", (0.0, 16.9, GRADE_Z - 0.05), (22.0, 4.6, 0.10),
             COL_LAWN_FRONT)
    # The front walk + the mailbox at the curb
    make_box("Ext_Walk", (-1.3, 7.95, GRADE_Z + 0.006), (0.95, 3.7, 0.012), COL_CONCRETE)
    make_cyl("Ext_MailPost", (-1.3, 9.75, GRADE_Z + 0.45), 0.035, 0.90, MILLER_FENCE_SEAM)
    make_box("Ext_Mailbox", (-1.3, 9.75, GRADE_Z + 1.00), (0.18, 0.42, 0.20),
             (0.24, 0.34, 0.30, 1.0))
    # The cracked sprinkler head (vol6_ch0_prelude:99) + two mates
    make_cyl("Ext_SprinklerCracked", (1.35, 7.35, GRADE_Z + 0.035), 0.020, 0.07,
             (0.70, 0.57, 0.30, 1.0), segments=8)
    make_box("Ext_SprinklerPuddle", (1.42, 7.28, GRADE_Z + 0.004), (0.40, 0.30, 0.006),
             (0.34, 0.42, 0.28, 1.0))
    for si, (sx, sy) in enumerate([(-3.4, 7.1), (3.9, 8.6)]):
        make_cyl(f"Ext_Sprinkler_{si}", (sx, sy, GRADE_Z + 0.025), 0.016, 0.05,
                 (0.30, 0.31, 0.32, 1.0), segments=8)
    # The Millers' HCE specimen tree, east of the walk
    make_cyl("Ext_Tree_Trunk", (2.7, 8.7, GRADE_Z + 1.1), 0.12, 2.20, COL_TRUNK)
    for ci, (cr, cz) in enumerate([(1.15, 2.30), (0.85, 3.05), (0.50, 3.65)]):
        make_cyl(f"Ext_Tree_Canopy_{ci}", (2.7, 8.7, GRADE_Z + cz), cr, 0.70,
                 COL_OAK_CANOPY if ci % 2 == 0 else COL_OAK_CANOPY_2, segments=10)
    # The driveway (crosses the sidewalk to its curb cut, per the
    # HCE driveway standard) + Sam's silver Corolla
    # (vol6_ch4_kitchen:26)
    make_box("Ext_Driveway", (-3.2, 8.35, GRADE_Z + 0.006), (2.5, 4.5, 0.012),
             COL_CONCRETE)
    cx, cy = -3.2, 8.3
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
    for sgn in (-1, +1):
        make_box(f"Corolla_Tail_{sgn:+d}", (cx + sgn * 0.62, cy - 2.085, GRADE_Z + 0.62),
                 (0.18, 0.02, 0.08), (0.72, 0.20, 0.16, 1.0))
    make_box("Corolla_Plate", (cx, cy - 2.09, GRADE_Z + 0.48), (0.30, 0.015, 0.10),
             P.PAPER)
    # DON GELLER'S HOUSE — dead ahead across the cul-de-sac, the
    # same tract massing (uniformity), his porch light ON.
    gx, gy = 0.4, 17.8
    make_box("Geller_Body", (gx, gy, GRADE_Z + 1.55), (7.5, 4.5, 3.10),
             (0.72, 0.66, 0.56, 1.0))
    make_box("Geller_Roof0", (gx, gy, GRADE_Z + 3.30), (8.1, 5.1, 0.50), MILLER_ROOF)
    make_box("Geller_Roof1", (gx, gy, GRADE_Z + 3.76), (5.7, 3.5, 0.44), MILLER_ROOF)
    make_box("Geller_Roof2", (gx, gy, GRADE_Z + 4.12), (3.0, 1.8, 0.30), MILLER_ROOF)
    make_box("Geller_Porch", (gx + 0.5, gy - 2.55, GRADE_Z + 0.12), (2.6, 1.2, 0.24),
             COL_CONCRETE)
    for pi, px in enumerate((-0.6, 1.6)):
        make_cyl(f"Geller_PorchPost_{pi}", (gx + px, gy - 3.05, GRADE_Z + 1.15),
                 0.05, 2.05, MILLER_TRIM)
    make_box("Geller_PorchRoof", (gx + 0.5, gy - 2.65, GRADE_Z + 2.24), (2.9, 1.5, 0.14),
             MILLER_ROOF)
    make_box("Geller_Door", (gx + 1.1, gy - 2.28, GRADE_Z + 1.02), (0.90, 0.06, 2.00),
             (0.28, 0.24, 0.22, 1.0))
    # THE PORCH LIGHT (vol6_ch11_kitchen:118 / vol6_ch17_table:38)
    make_box("Geller_LightBracket", (gx + 0.42, gy - 2.26, GRADE_Z + 1.72),
             (0.07, 0.05, 0.12), P.METAL_BLACK)
    make_cyl("Geller_PorchLight", (gx + 0.42, gy - 2.32, GRADE_Z + 1.68), 0.055, 0.12,
             COL_PORCHBULB, segments=10)
    for wi, wx2 in enumerate((-2.2, -0.6)):
        make_box(f"Geller_Window_{wi}", (gx + wx2, gy - 2.28, GRADE_Z + 1.55),
                 (0.90, 0.06, 0.80), (0.10, 0.12, 0.15, 1.0))
    # HCE standard foundation shrubs along Geller's front wall
    for si2 in range(4):
        make_cyl(f"Geller_Shrub_{si2}", (gx - 2.6 + si2 * 1.15, gy - 2.42,
                 GRADE_Z + 0.30), 0.34, 0.55, (0.22, 0.34, 0.20, 1.0), segments=8)
        make_cyl(f"Geller_MulchRing_{si2}", (gx - 2.6 + si2 * 1.15, gy - 2.42,
                 GRADE_Z + 0.012), 0.42, 0.02, (0.30, 0.22, 0.16, 1.0), segments=10)
    # A second dark tract house west across the circle — same bones
    hx, hy = -8.6, 17.4
    make_box("TractW_Body", (hx, hy, GRADE_Z + 1.50), (6.5, 4.8, 3.00),
             (0.62, 0.58, 0.62, 1.0))
    make_box("TractW_Roof0", (hx, hy, GRADE_Z + 3.22), (7.1, 5.4, 0.48), MILLER_ROOF)
    make_box("TractW_Roof1", (hx, hy, GRADE_Z + 3.66), (4.8, 3.6, 0.42), MILLER_ROOF)
    make_box("TractW_Window", (hx + 1.2, hy - 2.42, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             (0.10, 0.12, 0.15, 1.0))
    # Our own siding face wrapping the window opening outside (so
    # the view edges read as house, not void — opening left CLEAR)
    # + shutters
    make_box("Ext_Skin_W", (-2.325, wallout + 0.02, 1.30), (2.95, 0.06, 2.60),
             MILLER_SIDING)
    make_box("Ext_Skin_E", (+2.325, wallout + 0.02, 1.30), (2.95, 0.06, 2.60),
             MILLER_SIDING)
    make_box("Ext_Skin_Sill", (0.0, wallout + 0.02, WIN_SILL / 2.0),
             (1.70, 0.06, WIN_SILL), MILLER_SIDING)
    make_box("Ext_Skin_Head", (0.0, wallout + 0.02, (WIN_HEAD + 2.60) / 2.0),
             (1.70, 0.06, 2.60 - WIN_HEAD), MILLER_SIDING)
    for sgn in (-1, +1):
        make_box(f"Ext_Shutter_{sgn:+d}", (sgn * (WIN_W / 2.0 + 0.28), wallout + 0.06,
                 1.55), (0.34, 0.05, 1.34), MILLER_DOOR_GREEN)
        for li2 in range(4):
            make_box(f"Ext_Shutter_{sgn:+d}_Louver_{li2}", (sgn * (WIN_W / 2.0 + 0.28),
                     wallout + 0.09, 1.10 + li2 * 0.30), (0.30, 0.012, 0.03),
                     (0.20, 0.28, 0.23, 1.0))


def main():
    clear_scene()
    build_shell()
    build_window()
    build_counter_run()
    build_fridge()
    build_table_zone()
    build_east_wall()
    build_west_wall_and_ceiling()
    build_exterior_front()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/miller_kitchen.glb"))
    print(f"\n[build_miller_kitchen] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
