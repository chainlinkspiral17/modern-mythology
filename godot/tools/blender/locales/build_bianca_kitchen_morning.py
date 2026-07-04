"""Bianca's Kitchen (morning) — THE MILLER KITCHEN, 1428 Meadowlark
Circle, Harmony Creek — vol6 hero locale, MORNING preset (5 VN bg
refs: vol6_ch22_bianca x3 "Saturday — 04:11 — Bianca's Kitchen" /
the 9:17 Carlos call / the 10:14 kouglof doorbell, vol6_ch22_sunday
"1:15 AM" town montage, vol6_ch23_sunday "apply early" + the letter
back to Mike).

CANON ADJUDICATION made by this pass (the wave-8 binding-verification
rule — greped the bindings first):

  1. bianca_kitchen_morning vs miller_kitchen — SAME ROOM, SAME
     HOUSE. Two presets, one kitchen (the ramos_kitchen_morning /
     grandmother_kitchen_morning precedent). Evidence from the
     binding scenes: "The cul-de-sac through the kitchen window is
     dark" (ch22_bianca:48 — the front window on the cul-de-sac,
     vol6_ch11_kitchen:86 canon), Don Geller's porch light dead
     ahead (ch22:88-92 — the 5:02 light, "as long as Bianca has
     lived in this house, which is nineteen years"), the green
     terrycloth robe "on the hook by the back door" (ch22:44), the
     kitchen table / Sammy in her Kwik Stop polo / Mike in Alabama
     (ch22:104, ch23:694-928). miller_kitchen is the 4:30-AM
     four-thirty-table preset; THIS file is the same room in
     daylight (the .tscn mood strata lead with 'morning_bright' /
     'dawn_warm'). Same shell, same fixed geometry, morning-state
     dressing only.
  2. "At the Marin house on Elm, Bianca is on the back porch"
     (ch22_sunday:48) is read as scene-text drift, NOT a different
     house: the same paragraph carries the Miller-canon facts (the
     green terrycloth robe Mike gave her in 2019, the cul-de-sac,
     Don Geller's light as one of the standard four). Documented,
     not resolved here.
  3. Composite morning state: the preset serves 01:15 / 04:11 /
     ~10:14 Saturday and ~17:00 Sunday. Geometry-side state is
     keyed to the marquee on-camera beat — the 10:14 Saturday
     doorbell (Eileen, the kouglof) — because 3 of 5 bg refs are
     ch22_bianca and its only camera-forward kitchen action is the
     doorbell crossing. Pre-dawn hours are lighting-side (.tscn).

SHARED-PALETTE SYNC NOTE: the MILLER HOUSE block below is
byte-identical (md5 323b0fde62d28a0e225f3885acdd2afc) with
build_miller_kitchen.py and build_miller_back_porch.py — THREE files
now hold it. The in-block comment still names only the original two
siblings because editing them is out of this pass's scope; when any
copy is retuned, sync ALL THREE.

Fixed geometry kept byte-for-byte in intent from
build_miller_kitchen.py (the night sibling): 7 x 6 shell, CEIL 2.6,
south hall gap x -1..+1 (the Background3D camera preset
(0, 2.30, +0.5) / yaw 180 / fov 60 shoots through it), the front
window as a REAL OPENING over the sink (no glass — playbook
no-transparency rule), the golden-oak counter run, the table's seat
geography kept exactly (vol6_ch11_kitchen:106 — Mike's chair on the
short side near the window, Sammy at the head, Bianca on the long
side), the hunter-green back door + pantry + landline on the east
wall, Geller's house dead ahead across the cul-de-sac.

MORNING-STATE dressing (only where the binding scenes demand):

  · Clock hands frozen at 10:14 — "At ten-fourteen the doorbell
    rings" (ch22_bianca:662). Same wall position as the night
    preset (a clock doesn't move between presets; only the hands
    are state). A TOASTER added on the counter east of the sink
    beneath it — "The kitchen clock, on the wall above the toaster,
    ticks" (ch22:84); the night file has no toaster and hangs the
    clock over the window, so the toaster sits on the nearest
    counter run under that wall.
  · The kettle on the burner + the coffee grinder on the counter —
    "She puts the kettle on the burner. She measures the beans. The
    grinder makes the noise it makes." (ch22:44). Cast-iron skillet
    stays on the range (fixed, vol6_ch6_miller_kitchen:32).
  · The Cuisinart running — "She puts on a third pot" (ch22:724).
    Under-cabinet strips modeled but OFF (daylight; they are the
    4:30 light source, vol6_ch11_kitchen:78, not the 10:14 one).
  · The kouglof on the counter + the Magnolia bakery paper bag —
    "Will you take a kouglof" / "Bianca puts the kouglof on the
    counter" (ch22:697, :720). Replaces the night preset's
    foil-wrapped coffee cake (a ch17 Friday-table item).
  · The envelope to Mike on the corner of the counter — "She puts
    the envelope on the corner of the kitchen counter where she
    will see it tomorrow morning" (ch23_sunday:948).
  · Table: Bianca's mug on the long side, Eileen's mug at the
    window-side place ("The two of them sit at the kitchen table",
    ch22:728 — Eileen takes Mike's chair when she visits, per the
    night file's canon), Sammy's half-finished cereal bowl + spoon
    at the head (ch23:694), Bianca's stationery + pen (ch23:892),
    the Saturday Express-News folded (the Beecher kid's 5:45 route,
    ch22:92). The four-thirty-table spread (kolaches, press pot,
    danish, travel mug) is FRIDAY dressing — removed; "Friday is
    the table. Saturday is hers." (ch22:60).
  · Robe hook by the back door carries CARMEN'S COTTON WEEKDAY
    ROBE: the hook is canonically the green terrycloth's home
    (ch22:44) but Bianca is WEARING the green one in every bg beat
    of this preset (ch22:72, ch22_sunday:48), so the cotton one
    (ch22:72 — "the cotton one her sister Carmen sent her") hangs
    in its place.
  · Sam's backpack + license-plate notebook + travel mug REMOVED —
    Sammy is at the Kwik Stop until four ("The Corolla is gone.
    The driveway is empty." ch22:104); Sunday she is upstairs
    bag-packing for the first day (ch23:888).
  · Exterior: driveway EMPTY (no Corolla — ch22:104), Don Geller's
    porch light OFF ("Don's light long off" ch22:196; "Don's porch
    is, by nine twenty-two, in full sun" ch22:618) — fixture kept,
    bulb unlit. Tract-house windows read daylit glass, the back
    door's panes read full-sun sky instead of COL_NIGHT.

CANON-NEGATIVES (deliberately NOT here):
  · NO radio — the father's restored radio is on a FedEx truck
    until Wednesday (ch22:141, ch23:920). Do not bake one in.
  · NO cordless handset in the kitchen — it lives on the back-porch
    patio table all chapter (ch22:104, ch22_sunday:48). The beige
    wall landline stays (fixed, vol6_ch6_miller_kitchen:106).
  · NO green terrycloth robe on the hook (she is wearing it), no
    four-thirty-table spread, no Corolla, no lit porch light, no
    kolache bag, no Henderson/Caldwell ceremony props (the cake and
    sticker books are in the CALDWELL yard, ch23:234+).
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

# Kitchen-only palette (morning preset)
COL_VINYL       = (0.82, 0.77, 0.66, 1.0)     # sheet-vinyl floor
COL_VINYL_SEAM  = (0.63, 0.56, 0.44, 1.0)
COL_BORDER      = (0.44, 0.54, 0.56, 1.0)     # 1991 wallpaper border
COL_SHEER       = (0.95, 0.93, 0.86, 1.0)     # the sheer curtain
COL_DAY_SKY     = (0.74, 0.81, 0.88, 1.0)     # full sun through the back-door panes
COL_DAY_WINDOW  = (0.50, 0.58, 0.64, 1.0)     # daylit glass, far tract houses
COL_UNDERCAB_OFF = (0.88, 0.87, 0.82, 1.0)    # strips OFF in daylight
COL_BULB_OFF    = (0.80, 0.78, 0.70, 1.0)     # Geller's light, long off
COL_STEEL_DK    = (0.44, 0.46, 0.48, 1.0)
COL_KRAFT       = (0.76, 0.64, 0.46, 1.0)     # Magnolia bakery paper bag
COL_KOUGLOF     = (0.72, 0.50, 0.26, 1.0)     # the kouglof crust
COL_KOUGLOF_SUGAR = (0.94, 0.92, 0.86, 1.0)   # powdered-sugar dusting
COL_MILK        = (0.93, 0.92, 0.88, 1.0)     # Sammy's cereal milk
COL_COTTON_ROBE = (0.90, 0.87, 0.80, 1.0)     # Carmen's weekday robe
COL_COTTON_BELT = (0.80, 0.76, 0.68, 1.0)

PAL_WALL = {"wall": MILLER_INT_WALL, "baseboard": MILLER_BASEBOARD}

GRADE_Z = -0.40           # front-yard grade outside the window
WIN_W = 1.70              # window opening x -0.85..+0.85
WIN_SILL = 0.95
WIN_HEAD = 2.15


# ═════════════════════════════════════════════════════════════════
# SHELL — identical to the night preset (build_miller_kitchen.py):
# vinyl floor, eggshell walls, flat drywall ceiling, the 1991
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
# WINDOW — the front window over the sink (fixed geometry, identical
# to the night preset): REAL OPENING, white double-hung sash frame,
# sheer curtain side panels + valance (vol6_ch5_miller_drive:75).
# "The cul-de-sac through the kitchen window is dark" at 04:11
# (ch22:48) and in full sun by 9:22 — the glassless opening serves
# both; the light is scene-side. Clock hands frozen at 10:14, the
# doorbell minute (ch22:662).
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
    # The kitchen clock — same wall spot as the night preset; hands
    # are the state: FROZEN AT 10:14, the doorbell minute
    # (ch22_bianca:662). "The kitchen clock, on the wall above the
    # toaster, ticks" (ch22:84) — the toaster sits on the counter
    # run beneath this wall (build_counter_run).
    make_wall_clock("Clock", (0.0, wy - 0.14, 2.37), frozen_hour=10, frozen_min=14)


# ═════════════════════════════════════════════════════════════════
# COUNTER RUN — fixed golden-oak base + uppers, almond laminate,
# sink under the window, dishwasher, range + cast-iron skillet,
# hood, microwave (all identical to the night preset). Morning
# state: under-cab strips OFF, the KETTLE on the burner + the
# GRINDER on the counter (ch22:44), the TOASTER under the clock
# (ch22:84), the Cuisinart running its third pot (ch22:724), the
# KOUGLOF + Magnolia bakery bag where Friday's foil loaf sat
# (ch22:697/:720), the envelope to Mike on the counter corner
# (ch23:948). Peggy's peach preserves stay — the 6:40 toast jam
# (ch22:104 "one piece of toast with peach jam").
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
    # Under-cabinet strips — fixture kept, OFF in daylight (they are
    # the 4:30 light, vol6_ch11_kitchen:78; it is 10:14).
    make_box("UnderCabLight_W", (-1.50, 5.70, 1.505), (1.02, 0.05, 0.028),
             COL_UNDERCAB_OFF)
    make_box("UnderCabLight_E", (1.45, 5.70, 1.505), (0.92, 0.05, 0.028),
             COL_UNDERCAB_OFF)
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
    # THE TOASTER east of the sink, under the clock's wall (ch22:84)
    make_box("Toaster_Body", (0.55, 5.78, 1.005), (0.24, 0.17, 0.19),
             (0.82, 0.81, 0.78, 1.0))
    for si, sy in enumerate((-0.035, +0.035)):
        make_box(f"Toaster_Slot_{si}", (0.55, 5.78 + sy, 1.102), (0.17, 0.030, 0.012),
                 P.METAL_BLACK)
    make_box("Toaster_Lever", (0.55, 5.685, 1.045), (0.035, 0.020, 0.045), COL_STEEL_DK)
    # Drying rack east of the sink — the washed plate + a mug
    make_box("DryRack_Tray", (0.85, 5.72, 0.925), (0.32, 0.40, 0.015), MILLER_TRIM)
    for wi in range(4):
        make_box(f"DryRack_Wire_{wi}", (0.73 + wi * 0.08, 5.72, 0.985),
                 (0.010, 0.36, 0.09), P.METAL_STEEL)
    make_cyl("DryRack_Plate", (0.85, 5.72, 1.03), 0.10, 0.014, COL_CERAMIC, axis='Y',
             segments=12)
    make_cyl("DryRack_Mug", (0.85, 5.56, 0.975), 0.036, 0.09, COL_CERAMIC, segments=10)
    # Dishwasher west of the sink (Sammy's Sunday bowl goes in it,
    # ch23:956)
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
    # THE KETTLE on the front-right burner (ch22:44)
    make_cyl("Kettle_Body", (-2.26, 5.51, 1.010), 0.095, 0.15, P.METAL_STEEL,
             segments=12)
    make_cyl("Kettle_Lid", (-2.26, 5.51, 1.095), 0.050, 0.020, P.METAL_STEEL,
             segments=10)
    make_cyl("Kettle_Knob", (-2.26, 5.51, 1.115), 0.012, 0.020, P.METAL_BLACK)
    make_cyl("Kettle_Spout", (-2.155, 5.51, 1.050), 0.016, 0.09, P.METAL_STEEL,
             axis='X', segments=8)
    for pi, px in enumerate((-0.055, +0.055)):
        make_cyl(f"Kettle_HandlePost_{pi}", (-2.26 + px, 5.51, 1.130), 0.008, 0.06,
                 P.METAL_BLACK, segments=8)
    make_box("Kettle_HandleTop", (-2.26, 5.51, 1.165), (0.13, 0.020, 0.018),
             P.METAL_BLACK)
    make_box("Hood_Body", (-2.45, 5.77, 1.96), (0.76, 0.44, 0.14), MILLER_APPLIANCE)
    make_box("Hood_Lip", (-2.45, 5.56, 1.90), (0.76, 0.03, 0.05), P.METAL_STEEL)
    # THE CUISINART, running the third pot (ch22:724) + the two jars
    # of Peggy's peach preserves (fixed residents; the 6:40 toast
    # jam, ch22:104) + THE GRINDER (ch22:44)
    make_box("Cuisinart_Body", (1.30, 5.80, 1.08), (0.24, 0.26, 0.34), MILLER_TRIM)
    make_box("Cuisinart_Basket", (1.30, 5.74, 1.28), (0.22, 0.30, 0.07), MILLER_TRIM)
    make_cyl("Cuisinart_Carafe", (1.30, 5.68, 0.99), 0.068, 0.155, (0.74, 0.78, 0.76, 1.0),
             segments=12)
    make_cyl("Cuisinart_Coffee", (1.30, 5.68, 0.955), 0.058, 0.075, COL_COFFEE,
             segments=12)
    make_box("Cuisinart_Switch", (1.30, 5.665, 1.13), (0.05, 0.012, 0.03),
             (0.86, 0.42, 0.32, 1.0))
    make_cyl("Grinder_Base", (1.08, 5.83, 0.965), 0.042, 0.11, MILLER_TRIM, segments=10)
    make_cyl("Grinder_Cap", (1.08, 5.83, 1.045), 0.038, 0.050, (0.75, 0.78, 0.80, 1.0),
             segments=10)
    make_box("Grinder_Button", (1.08, 5.785, 0.995), (0.020, 0.012, 0.020), COL_STEEL_DK)
    for ji, (jx, jy) in enumerate([(1.60, 5.76), (1.70, 5.62)]):
        make_cyl(f"Preserves_{ji}_Jar", (jx, jy, 0.962), 0.042, 0.10,
                 (0.85, 0.55, 0.30, 1.0), segments=10)
        make_cyl(f"Preserves_{ji}_Lid", (jx, jy, 1.018), 0.045, 0.018,
                 (0.70, 0.57, 0.30, 1.0), segments=10)
    # THE KOUGLOF on a plate + the Magnolia bakery paper bag
    # (ch22:697 "Will you take a kouglof" / :720) — replaces the
    # night preset's Friday foil loaf.
    make_cyl("Kouglof_Plate", (-0.60, 5.74, 0.916), 0.110, 0.012, COL_CERAMIC,
             segments=12)
    make_cyl("Kouglof_Body", (-0.60, 5.74, 0.960), 0.085, 0.075, COL_KOUGLOF,
             segments=12)
    make_cyl("Kouglof_Sugar", (-0.60, 5.74, 1.000), 0.078, 0.008, COL_KOUGLOF_SUGAR,
             segments=12)
    make_cyl("Kouglof_Center", (-0.60, 5.74, 1.000), 0.024, 0.014, MILLER_OAK_DK,
             segments=8)
    make_box("BakeryBag", (-0.95, 5.76, 1.005), (0.20, 0.15, 0.19), COL_KRAFT)
    make_box("BakeryBag_Fold", (-0.95, 5.76, 1.108), (0.21, 0.16, 0.018),
             (0.66, 0.54, 0.38, 1.0))
    # The envelope to Mike on the corner of the counter (ch23:948)
    make_box("Envelope_Mike", (1.80, 5.47, 0.913), (0.16, 0.11, 0.005), P.PAPER)
    make_box("Envelope_Mike_Address", (1.80, 5.47, 0.917), (0.08, 0.045, 0.002),
             COL_STEEL_DK)
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
# FRIDGE — almond top-freezer, identical to the night preset. Sam's
# Kwik Stop shift schedule stays magneted (she is AT the register
# right now, 8-to-4 — ch22:104); the HCE newsletter and the crayon
# drawing stay. "The refrigerator hum cycles up at four thirty-six"
# (ch22:84) — same box, different hour.
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
# TABLE — seat geography from vol6_ch11_kitchen:106, kept exactly
# (fixed): rectangular oak table, long axis N-S, Mike's chair on the
# SHORT SIDE NEAR THE WINDOW (empty since Alabama — Eileen takes it
# when she visits), Sam at the head (south), Bianca on the long
# side. MORNING dressing: Bianca's mug + Eileen's mug ("The two of
# them sit at the kitchen table", ch22:728), Sammy's half-finished
# cereal bowl at the head (ch23:694), Bianca's stationery + pen for
# the letter back to Mike (ch23:892), the Saturday Express-News
# (the Beecher kid's 5:45 route, ch22:92). NO four-thirty spread —
# "Friday is the table. Saturday is hers." (ch22:60).
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
    _miller_chair("Chair_Guest", tx + 0.77, ty, 'W')     # the fourth chair
    top = 0.7675
    # Coffee mugs: Bianca's place + Eileen's (in Mike's chair,
    # ch22:728)
    for nm, (mx, my) in (("Bianca", (tx - 0.30, ty - 0.18)),
                         ("Eileen", (tx + 0.02, ty + 0.55))):
        make_cyl(f"Mug_{nm}", (mx, my, top + 0.047), 0.038, 0.095, COL_CERAMIC,
                 segments=10)
        make_cyl(f"Mug_{nm}_Coffee", (mx, my, top + 0.092), 0.030, 0.006, COL_COFFEE,
                 segments=10)
        make_box(f"Mug_{nm}_Handle", (mx + 0.048, my, top + 0.05), (0.016, 0.014, 0.05),
                 COL_CERAMIC)
    # Sammy's half-finished cereal bowl + spoon at the head
    # (ch23:694 — "Bianca had made Sammy promise to actually eat")
    make_cyl("CerealBowl", (tx + 0.02, ty - 0.55, top + 0.033), 0.070, 0.065,
             COL_CERAMIC, segments=12)
    make_cyl("CerealBowl_Milk", (tx + 0.02, ty - 0.55, top + 0.058), 0.056, 0.006,
             COL_MILK, segments=12)
    make_box("CerealSpoon", (tx + 0.17, ty - 0.52, top + 0.006), (0.025, 0.13, 0.008),
             P.METAL_STEEL)
    # The stationery she has not used since 2018 + the pen
    # (ch23:892 — the letter back to Mike is written HERE)
    make_box("Stationery", (tx - 0.26, ty + 0.12, top + 0.004), (0.155, 0.215, 0.006),
             P.PAPER)
    make_cyl("Pen", (tx - 0.10, ty + 0.06, top + 0.008), 0.005, 0.13, P.METAL_BLACK,
             axis='Y', segments=8)
    # The Saturday Express-News, folded (ch22:92)
    make_box("ExpressNews", (tx + 0.28, ty - 0.28, top + 0.008), (0.30, 0.21, 0.016),
             P.NEWSPRINT)
    make_box("ExpressNews_Masthead", (tx + 0.28, ty - 0.20, top + 0.018),
             (0.26, 0.05, 0.004), (0.30, 0.28, 0.26, 1.0))
    # Household constants: sugar bowl + napkin holder
    make_cyl("SugarBowl", (tx + 0.30, ty - 0.12, top + 0.030), 0.038, 0.06, COL_CERAMIC,
             segments=10)
    make_cyl("SugarBowl_Lid", (tx + 0.30, ty - 0.12, top + 0.068), 0.030, 0.014,
             COL_CERAMIC, segments=10)
    make_box("Napkins_Base", (tx + 0.38, ty + 0.38, top + 0.008), (0.13, 0.09, 0.016),
             MILLER_OAK_DK)
    make_box("Napkins_Stack", (tx + 0.38, ty + 0.38, top + 0.05), (0.11, 0.07, 0.07),
             P.PAPER)


# ═════════════════════════════════════════════════════════════════
# EAST WALL — the hunter-green back door (fixed; same
# MILLER_DOOR_GREEN the porch file shows from outside), panes in
# FULL SUN (morning state), the pantry, the landline that never
# rings (vol6_ch6_miller_kitchen:106). Morning state: THE HOOK BY
# THE BACK DOOR (ch22:44) carrying Carmen's cotton weekday robe —
# the green terrycloth is ON BIANCA in every bg beat of this preset
# (ch22:72, ch22_sunday:48). Sam's backpack + notebook + travel mug
# are GONE — she is at the Kwik Stop until four (ch22:104).
# ═════════════════════════════════════════════════════════════════
def build_east_wall():
    wf = ROOM_W / 2.0 - 0.10          # interior face x 3.4
    # Back door (closed) — hunter green, half-glazed, daylight panes
    make_box("BackDoor_Leaf", (wf - 0.035, 2.0, 1.05), (0.05, 0.92, 2.10),
             MILLER_DOOR_GREEN)
    make_box("BackDoor_Day", (wf - 0.065, 2.0, 1.60), (0.012, 0.62, 0.76), COL_DAY_SKY)
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
    # THE HOOK BY THE BACK DOOR (ch22:44) + Carmen's cotton robe
    # (ch22:72 — the weekday one; the green terrycloth is on Bianca)
    make_box("RobeHook_Plate", (wf - 0.030, 2.80, 1.80), (0.020, 0.05, 0.07),
             (0.70, 0.57, 0.30, 1.0))
    make_cyl("RobeHook_Peg", (wf - 0.055, 2.80, 1.78), 0.011, 0.05,
             (0.70, 0.57, 0.30, 1.0), axis='X', segments=8)
    make_box("Robe_Shoulders", (wf - 0.10, 2.80, 1.72), (0.08, 0.36, 0.10),
             COL_COTTON_ROBE)
    make_box("Robe_Body", (wf - 0.10, 2.80, 1.36), (0.07, 0.32, 0.82), COL_COTTON_ROBE)
    make_box("Robe_Belt", (wf - 0.10, 2.80, 1.30), (0.075, 0.34, 0.05), COL_COTTON_BELT)
    make_box("Robe_BeltTail", (wf - 0.105, 2.72, 1.10), (0.065, 0.06, 0.36),
             COL_COTTON_BELT)
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
    # The landline — beige wall phone, coiled cord. The CORDLESS is
    # canonically NOT in this room (it is on the patio table,
    # ch22:104 / ch22_sunday:48).
    make_box("Phone_Body", (wf - 0.035, 3.12, 1.42), (0.05, 0.11, 0.22),
             (0.82, 0.76, 0.64, 1.0))
    make_box("Phone_Handset", (wf - 0.075, 3.12, 1.47), (0.04, 0.085, 0.24),
             (0.78, 0.72, 0.60, 1.0))
    for ci in range(4):
        make_box(f"Phone_Cord_{ci}", (wf - 0.045, 3.17 + (0.02 if ci % 2 else -0.01),
                 1.28 - ci * 0.10), (0.014, 0.014, 0.09), (0.72, 0.66, 0.54, 1.0))


# ═════════════════════════════════════════════════════════════════
# WEST WALL + CEILING — identical to the night preset: the kitchen
# calendar Bianca counted backward on (ch22:36), dome light, HVAC
# register, smoke detector.
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
# EXTERIOR · THE CUL-DE-SAC (through the front window) — same
# fixed yard as the night preset: sprinkler-kept front lawn with the
# cracked head (vol6_ch0_prelude:99), front walk + mailbox, the HCE
# specimen tree, Geller's tract house dead ahead. MORNING STATE:
# the driveway is EMPTY ("The Corolla is gone. The driveway is
# empty." ch22:104 — Sammy at the Kwik Stop until four) and Don's
# porch light is OFF ("Don's light long off" ch22:196; "Don's porch
# is, by nine twenty-two, in full sun" ch22:618) — fixture kept,
# bulb unlit, windows daylit.
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
    # The driveway — EMPTY (ch22:104; the Corolla is at the Kwik
    # Stop with Sammy). Curb cut + apron kept per the HCE standard.
    make_box("Ext_Driveway", (-3.2, 8.35, GRADE_Z + 0.006), (2.5, 4.5, 0.012),
             COL_CONCRETE)
    # A faint oil spot where the Corolla parks — the car's absence,
    # made visible.
    make_cyl("Ext_OilSpot", (-3.2, 8.0, GRADE_Z + 0.010), 0.22, 0.004,
             (0.52, 0.51, 0.47, 1.0), segments=10)
    # DON GELLER'S HOUSE — dead ahead across the cul-de-sac, the
    # same tract massing (uniformity). Porch light fixture kept,
    # UNLIT (ch22:196), windows daylit.
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
    # The porch light, long off (ch22:196) — same bracket, dark bulb
    make_box("Geller_LightBracket", (gx + 0.42, gy - 2.26, GRADE_Z + 1.72),
             (0.07, 0.05, 0.12), P.METAL_BLACK)
    make_cyl("Geller_PorchLight", (gx + 0.42, gy - 2.32, GRADE_Z + 1.68), 0.055, 0.12,
             COL_BULB_OFF, segments=10)
    for wi, wx2 in enumerate((-2.2, -0.6)):
        make_box(f"Geller_Window_{wi}", (gx + wx2, gy - 2.28, GRADE_Z + 1.55),
                 (0.90, 0.06, 0.80), COL_DAY_WINDOW)
    # HCE standard foundation shrubs along Geller's front wall
    for si2 in range(4):
        make_cyl(f"Geller_Shrub_{si2}", (gx - 2.6 + si2 * 1.15, gy - 2.42,
                 GRADE_Z + 0.30), 0.34, 0.55, (0.22, 0.34, 0.20, 1.0), segments=8)
        make_cyl(f"Geller_MulchRing_{si2}", (gx - 2.6 + si2 * 1.15, gy - 2.42,
                 GRADE_Z + 0.012), 0.42, 0.02, (0.30, 0.22, 0.16, 1.0), segments=10)
    # A second tract house west across the circle — same bones
    hx, hy = -8.6, 17.4
    make_box("TractW_Body", (hx, hy, GRADE_Z + 1.50), (6.5, 4.8, 3.00),
             (0.62, 0.58, 0.62, 1.0))
    make_box("TractW_Roof0", (hx, hy, GRADE_Z + 3.22), (7.1, 5.4, 0.48), MILLER_ROOF)
    make_box("TractW_Roof1", (hx, hy, GRADE_Z + 3.66), (4.8, 3.6, 0.42), MILLER_ROOF)
    make_box("TractW_Window", (hx + 1.2, hy - 2.42, GRADE_Z + 1.55), (0.90, 0.06, 0.80),
             COL_DAY_WINDOW)
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
        "../../../assets/3d/locales/bianca_kitchen_morning.glb"))
    print(f"\n[build_bianca_kitchen_morning] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
