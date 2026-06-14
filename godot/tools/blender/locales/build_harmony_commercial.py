"""
build_harmony_commercial.py
══════════════════════════════════════════════════════════════════
HCE-1 · Harmony Creek Estates · West Commercial Strip

The commercial perimeter belt that lines the western arterial of
Harmony Creek Estates (Hwy 9). The community's first contact with
the outside world: gas station forecourt + attached convenience
store + adjacent drive-thru fast-food + a four-bay strip mall, all
fronting a two-lane road with a planted buffer between sidewalk
and parcel.

The user's framing: "The starting point is the gas station and
assorted commercial suburban center assets." This locale takes the
riverfront's already-shipping vocabulary (gas-station pumps + can-
opy, strip-mall plate-glass fronts, telephone poles, sidewalks
with curb cuts, Lobster signage) and lays it out as a coherent
mini-community front rather than a single building.

COORDINATE FRAME · same as build_riverfront.py.  Blender Z-up;
Godot Y-up at runtime; remap (x_b, y_b, z_b) → (x_b, z_b, -y_b).
1 unit = 1 metre everywhere.

LAYOUT (Blender top-down, X horizontal, Y vertical, north = +Y):

  X = -290 (road centerline) ──┐
  X = -284 (road W edge)       │
  X = -281 (sidewalk W edge)   │     road frontage
  X = -279 (sidewalk W → buffer)
  X = -276 (planted buffer)    │
  X = -274 (parcel west edge)──┤
                               │
                       parcels:                Y range
                                               -120 .. -60   drive-thru
                                                -60 ..  +0   gas station + convenience
                                                 +0 .. +60   strip mall
                                                +60 ..+120   future expansion / vacant
  X = -224 (parcel east edge)──┘

Anchored to a coordinate frame that's separate from the riverfront
so the scenes don't share world position. Built at world (0, 0, 0)
neighborhood (HCE bounds are conceptual in Estuary One; the actual
geometry lives wherever the scene loads).
══════════════════════════════════════════════════════════════════
"""
import bpy
import math
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# Reuse the primitive library and export pipeline from the riverfront
# build. Both scripts share these — eventually they should live in a
# _primitives.py module, but for now importing is cheap and avoids a
# refactor that could destabilise the riverfront.
from build_riverfront import (
    make_box, make_cyl, make_prism, make_ramp, make_sphere,
    make_tube_segment,
)

OUTPUT_DIR = "../../../assets/3d/locales"
OUTPUT_NAME = "harmony_commercial.glb"

# ═══════════════════════════════════════════════════════════════
# LAYOUT CONSTANTS · all in metres, Blender Z-up frame
# ═══════════════════════════════════════════════════════════════
# Road (north-south arterial)
ROAD_CX        = -290.0    # centerline X
ROAD_W         =   11.0    # two-lane
ROAD_L         =  280.0    # extent along Y

# Sidewalk + planted buffer (commercial property starts at PARCEL_W_X)
SIDE_W_X       = -281.0    # sidewalk west edge (away from road)
SIDE_E_X       = -279.0    # sidewalk east edge
BUFFER_W       =    3.0    # planted buffer between sidewalk + parcel
PARCEL_W_X     = SIDE_E_X + BUFFER_W   # = -276 — parcels begin here
PARCEL_E_X     = -224.0                # 52 m parcel depth

# Per-parcel Y ranges
DRIVETHRU_Y_LO = -120.0
DRIVETHRU_Y_HI =  -60.0
GAS_Y_LO       =  -60.0
GAS_Y_HI       =   10.0
MALL_Y_LO      =   10.0
MALL_Y_HI      =   80.0

# Elevations
GROUND_Z       = -0.05     # base ground level
ROAD_Z         =  0.04     # 4 cm above grade
SIDEWALK_Z     =  0.10     # raised curb sidewalk
BUFFER_Z       =  0.14     # planted strip slightly raised over sidewalk

# Curb-cut openings (Y positions where the driveways break the curb)
DRIVEWAY_CUTS  = [-90.0, -25.0, 40.0]   # one per parcel

# ── COLOUR PALETTE ─────────────────────────────────────────────
COL_ASPHALT       = (0.22, 0.22, 0.24, 1.0)
COL_ASPHALT_FRESH = (0.16, 0.16, 0.18, 1.0)   # fresh sealcoat patches
COL_CONCRETE      = (0.72, 0.70, 0.66, 1.0)
COL_CURB          = (0.60, 0.58, 0.52, 1.0)
COL_GRASS         = (0.30, 0.48, 0.20, 1.0)
COL_GRASS_DRY     = (0.55, 0.52, 0.28, 1.0)   # midsummer parch
COL_WHITE_LINE    = (0.92, 0.92, 0.88, 1.0)
COL_YELLOW_LINE   = (0.92, 0.78, 0.20, 1.0)
COL_RED_PAINT     = (0.85, 0.20, 0.18, 1.0)   # curb fire-zone paint

# Building palette
COL_STUCCO_TAN    = (0.78, 0.72, 0.58, 1.0)
COL_STUCCO_PEACH  = (0.86, 0.74, 0.58, 1.0)
COL_BRICK_RED     = (0.55, 0.30, 0.22, 1.0)
COL_TRIM_WHITE    = (0.88, 0.86, 0.80, 1.0)
COL_TRIM_BROWN    = (0.32, 0.22, 0.16, 1.0)
COL_ROOF_DARK     = (0.18, 0.20, 0.22, 1.0)
COL_ROOF_TAR      = (0.10, 0.10, 0.12, 1.0)

# Glass + lighting
COL_GLASS_DARK    = (0.20, 0.28, 0.34, 1.0)
COL_GLASS_LIT     = (0.95, 0.92, 0.68, 1.0)
COL_FLUOR_TUBE    = (0.92, 0.96, 0.92, 1.0)   # near-white fluorescent
COL_NEON_RED      = (0.98, 0.20, 0.20, 1.0)
COL_NEON_GREEN    = (0.20, 0.95, 0.40, 1.0)

# Pumps + canopy
COL_PUMP_BODY     = (0.92, 0.88, 0.82, 1.0)
COL_PUMP_TRIM     = (0.85, 0.22, 0.20, 1.0)
COL_CANOPY_DECK   = (0.78, 0.74, 0.68, 1.0)
COL_CANOPY_COLUMN = (0.72, 0.68, 0.62, 1.0)

# Signage panels (Lobster cursive will sit on these via LocaleSetup)
COL_SIGN_PANEL    = (0.10, 0.08, 0.08, 1.0)
COL_SIGN_FRAME    = (0.32, 0.26, 0.20, 1.0)

# Pole / metal
COL_POLE_METAL    = (0.30, 0.30, 0.32, 1.0)
COL_POLE_WOOD     = (0.32, 0.24, 0.18, 1.0)


# ═══════════════════════════════════════════════════════════════
# GROUND + ROAD + SIDEWALK + BUFFER
# ═══════════════════════════════════════════════════════════════
def build_ground_plates():
    """Composite ground: large grass plate underneath, then asphalt
    parcels and the road on top."""
    # Big grass plate covering the whole locale
    make_box("Ground_Grass",
             (-250.0, 0.0, GROUND_Z - 0.10),
             (200.0, ROAD_L + 20.0, 0.20),
             COL_GRASS_DRY)
    # Service apron behind each parcel — a single wide asphalt slab
    # the parcels' rear-of-house spans
    make_box("Service_Apron",
             ((PARCEL_W_X + PARCEL_E_X) / 2.0, 0.0, ROAD_Z),
             (PARCEL_E_X - PARCEL_W_X, ROAD_L - 40.0, 0.04),
             COL_ASPHALT)


def build_road_and_sidewalk():
    """Hwy 9 frontage — two-lane road + raised sidewalk + planted
    buffer + curb cuts at every driveway."""
    # Asphalt
    make_box("Hwy9_Asphalt",
             (ROAD_CX, 0.0, ROAD_Z),
             (ROAD_W, ROAD_L, 0.04),
             COL_ASPHALT)
    # Edge stripes (white)
    for side_sign in (-1, +1):
        make_box(f"Hwy9_Edge_{('W' if side_sign < 0 else 'E')}",
                 (ROAD_CX + side_sign * (ROAD_W/2 - 0.30), 0.0, ROAD_Z + 0.04),
                 (0.18, ROAD_L, 0.005),
                 COL_WHITE_LINE)
    # Double-yellow center
    make_box("Hwy9_Center_W", (ROAD_CX - 0.10, 0.0, ROAD_Z + 0.04),
             (0.10, ROAD_L - 4.0, 0.005), COL_YELLOW_LINE)
    make_box("Hwy9_Center_E", (ROAD_CX + 0.10, 0.0, ROAD_Z + 0.04),
             (0.10, ROAD_L - 4.0, 0.005), COL_YELLOW_LINE)
    # Dashed lane divider on each side
    for di in range(56):
        dy = -130.0 + di * 4.5
        make_box(f"Hwy9_DashS_{di}", (ROAD_CX - 3.0, dy, ROAD_Z + 0.04),
                 (0.14, 2.0, 0.005), COL_WHITE_LINE)
        make_box(f"Hwy9_DashN_{di}", (ROAD_CX + 3.0, dy, ROAD_Z + 0.04),
                 (0.14, 2.0, 0.005), COL_WHITE_LINE)

    # ── Raised sidewalk on the EAST side (commercial side) only.
    # Driveway gaps at each curb-cut position (DRIVEWAY_CUTS).
    cut_half = 4.0
    sidewalk_cx = (SIDE_W_X + SIDE_E_X) / 2.0
    sidewalk_w = SIDE_E_X - SIDE_W_X
    # Build sidewalk in segments around the driveway cuts.
    cuts_sorted = sorted(DRIVEWAY_CUTS)
    edges = [-ROAD_L/2 + 5.0]
    for cy in cuts_sorted:
        edges.append(cy - cut_half)
        edges.append(cy + cut_half)
    edges.append(ROAD_L/2 - 5.0)
    for si in range(0, len(edges), 2):
        y_lo = edges[si]
        y_hi = edges[si + 1]
        if y_hi <= y_lo + 0.5:
            continue
        seg_cy = (y_lo + y_hi) / 2.0
        seg_l = y_hi - y_lo
        make_box(f"Sidewalk_{si}",
                 (sidewalk_cx, seg_cy, SIDEWALK_Z / 2),
                 (sidewalk_w, seg_l, SIDEWALK_Z),
                 COL_CONCRETE)
        # seam lines every 3m
        n_seams = max(1, int(seg_l / 3.0))
        for sj in range(n_seams):
            sy = y_lo + (sj + 1) * seg_l / (n_seams + 1)
            make_box(f"Sidewalk_{si}_seam_{sj}",
                     (sidewalk_cx, sy, SIDEWALK_Z + 0.005),
                     (sidewalk_w - 0.10, 0.04, 0.005),
                     COL_CURB)

    # Curb ramps at each driveway cut (north + south sides)
    for cy in DRIVEWAY_CUTS:
        for ramp_sign, lbl in ((-1, "S"), (+1, "N")):
            ramp_far = cy + ramp_sign * cut_half
            ramp_near = cy + ramp_sign * (cut_half - 1.6)
            ramp_cy = (ramp_far + ramp_near) / 2.0
            ramp_len = abs(ramp_far - ramp_near)
            make_prism(f"CurbRamp_{int(cy)}_{lbl}",
                       (sidewalk_cx, ramp_cy, 0.04),
                       (sidewalk_w, ramp_len, SIDEWALK_Z - 0.04),
                       COL_CURB, pitch_axis='X')

    # ── Planted buffer strip between sidewalk and parcels.
    # Earth base + grass cap. Same cuts as sidewalk so curb cuts
    # extend through the buffer.
    buffer_cx = (SIDE_E_X + PARCEL_W_X) / 2.0
    for si in range(0, len(edges), 2):
        y_lo = edges[si]
        y_hi = edges[si + 1]
        if y_hi <= y_lo + 0.5:
            continue
        seg_cy = (y_lo + y_hi) / 2.0
        seg_l = y_hi - y_lo
        make_box(f"Buffer_{si}",
                 (buffer_cx, seg_cy, BUFFER_Z / 2),
                 (BUFFER_W, seg_l, BUFFER_Z),
                 (0.32, 0.26, 0.18, 1.0))   # earth tone
        make_box(f"Buffer_{si}_grass",
                 (buffer_cx, seg_cy, BUFFER_Z + 0.01),
                 (BUFFER_W - 0.10, seg_l, 0.02),
                 COL_GRASS)

    # Buffer planting — a tree every ~15 m along the buffer, skip
    # near the curb cuts.
    for ty in range(-130, 131, 16):
        if any(abs(ty - cy) < 6.0 for cy in DRIVEWAY_CUTS):
            continue
        trunk_h = 4.5
        make_cyl(f"Buffer_Tree_Trunk_{ty}",
                 (buffer_cx, float(ty), trunk_h / 2 + BUFFER_Z),
                 0.18, trunk_h, COL_POLE_WOOD, segments=6)
        make_sphere(f"Buffer_Tree_Canopy_{ty}",
                    (buffer_cx, float(ty), trunk_h + 0.9 + BUFFER_Z),
                    1.3, COL_GRASS)


# ═══════════════════════════════════════════════════════════════
# GAS STATION + CANOPY + PUMPS + CONVENIENCE STORE
# ═══════════════════════════════════════════════════════════════
def build_gas_station():
    """Forecourt with 4 pumps under a flat canopy, the convenience
    store wedged on the east (rear-of-parcel) side. Sign monument
    on the corner facing the road."""
    parcel_cx = (PARCEL_W_X + PARCEL_E_X) / 2.0
    parcel_cy = (GAS_Y_LO + GAS_Y_HI) / 2.0
    parcel_w = PARCEL_E_X - PARCEL_W_X
    parcel_l = GAS_Y_HI - GAS_Y_LO

    # ── Asphalt forecourt (full parcel)
    make_box("Gas_Forecourt", (parcel_cx, parcel_cy, ROAD_Z),
             (parcel_w, parcel_l, 0.04), COL_ASPHALT)
    # Fresher asphalt patches near the pumps
    for px_off in (-6, +6):
        make_box(f"Gas_Sealcoat_{px_off}",
                 (parcel_cx + px_off - 8, parcel_cy, ROAD_Z + 0.005),
                 (8.0, 4.0, 0.005), COL_ASPHALT_FRESH)

    # ── Pump islands — 2 islands, 2 pumps each, set close to the
    # road so the canopy roofline reads from the parcel front.
    island_x = PARCEL_W_X + 14.0
    for ii, island_y_off in enumerate((-6.0, +6.0)):
        iy = parcel_cy + island_y_off
        # Island base (raised concrete)
        make_box(f"Pump_Island_{ii}_base",
                 (island_x, iy, ROAD_Z + 0.10),
                 (1.4, 4.6, 0.20),
                 COL_CONCRETE)
        # Two pumps per island, one facing each direction along Y
        for pi, py_off in enumerate((-1.4, 1.4)):
            py = iy + py_off
            base_z = ROAD_Z + 0.22
            # Pump body
            make_box(f"Pump_{ii}_{pi}_body",
                     (island_x, py, base_z + 0.65),
                     (0.62, 0.95, 1.30),
                     COL_PUMP_BODY)
            # Trim band
            make_box(f"Pump_{ii}_{pi}_band",
                     (island_x, py, base_z + 1.15),
                     (0.64, 0.97, 0.10),
                     COL_PUMP_TRIM)
            # Display screen
            make_box(f"Pump_{ii}_{pi}_screen",
                     (island_x + 0.32, py, base_z + 1.05),
                     (0.02, 0.55, 0.30),
                     COL_GLASS_LIT)
            # Hose nozzle holster (small box on one side)
            for hi, hy_off in enumerate((-0.30, 0.30)):
                make_box(f"Pump_{ii}_{pi}_hose_{hi}",
                         (island_x - 0.30, py + hy_off, base_z + 0.50),
                         (0.04, 0.16, 0.50),
                         (0.18, 0.18, 0.18, 1.0))
            # Top cap with brand colour
            make_box(f"Pump_{ii}_{pi}_top",
                     (island_x, py, base_z + 1.32),
                     (0.65, 0.95, 0.06),
                     COL_PUMP_TRIM)

    # ── Canopy — flat roof on 4 columns over the pump islands
    canopy_y_extent = 16.0
    canopy_x_extent = 14.0
    canopy_z = ROAD_Z + 4.6
    canopy_cx = island_x
    canopy_cy = parcel_cy
    # Roof deck
    make_box("Gas_Canopy_Deck",
             (canopy_cx, canopy_cy, canopy_z),
             (canopy_x_extent, canopy_y_extent, 0.30),
             COL_CANOPY_DECK)
    # Sky-facing edge fascia
    for ex_sign in (-1, +1):
        make_box(f"Gas_Canopy_Fascia_x{ex_sign}",
                 (canopy_cx + ex_sign * canopy_x_extent/2, canopy_cy, canopy_z - 0.20),
                 (0.18, canopy_y_extent, 0.50),
                 COL_PUMP_TRIM)
    for ey_sign in (-1, +1):
        make_box(f"Gas_Canopy_Fascia_y{ey_sign}",
                 (canopy_cx, canopy_cy + ey_sign * canopy_y_extent/2, canopy_z - 0.20),
                 (canopy_x_extent, 0.18, 0.50),
                 COL_PUMP_TRIM)
    # Columns
    col_h = canopy_z - 0.35 - ROAD_Z
    col_z = ROAD_Z + col_h / 2
    for ci, (cx_o, cy_o) in enumerate([
        (-canopy_x_extent/2 + 0.6, -canopy_y_extent/2 + 0.6),
        (+canopy_x_extent/2 - 0.6, -canopy_y_extent/2 + 0.6),
        (-canopy_x_extent/2 + 0.6, +canopy_y_extent/2 - 0.6),
        (+canopy_x_extent/2 - 0.6, +canopy_y_extent/2 - 0.6),
    ]):
        make_box(f"Gas_Canopy_Col_{ci}",
                 (canopy_cx + cx_o, canopy_cy + cy_o, col_z),
                 (0.50, 0.50, col_h),
                 COL_CANOPY_COLUMN)
    # Underside lights (4 fluorescent tubes lighting the pumps)
    for li, (lx_o, ly_o) in enumerate([
        (-4.0, -4.0), (4.0, -4.0), (-4.0, 4.0), (4.0, 4.0),
    ]):
        make_box(f"Gas_Canopy_Tube_{li}",
                 (canopy_cx + lx_o, canopy_cy + ly_o, canopy_z - 0.40),
                 (2.0, 0.20, 0.04),
                 COL_FLUOR_TUBE)

    # ── Convenience store building (east side of parcel, behind pumps)
    store_w = 22.0
    store_l = 14.0
    store_h = 4.2
    store_cx = PARCEL_E_X - store_w/2 - 2.0
    store_cy = parcel_cy
    store_cz = ROAD_Z + store_h/2
    make_box("Store_Walls", (store_cx, store_cy, store_cz),
             (store_w, store_l, store_h), COL_STUCCO_TAN)
    # Roof — slightly proud parapet
    make_box("Store_Parapet", (store_cx, store_cy, store_cz + store_h/2 + 0.20),
             (store_w + 0.20, store_l + 0.20, 0.40), COL_ROOF_TAR)
    # Plate-glass storefront (the parcel-road-facing side, low Y not
    # used — the front faces -X toward the pumps)
    glass_z = ROAD_Z + 1.8
    make_box("Store_Glass",
             (store_cx - store_w/2 - 0.02, store_cy, glass_z),
             (0.06, store_l - 4.0, 2.4),
             COL_GLASS_LIT)
    # Mullions (vertical) splitting the glass into 4 panels
    for mi, my_off in enumerate((-3.0, -1.0, 1.0, 3.0)):
        make_box(f"Store_Mullion_{mi}",
                 (store_cx - store_w/2 - 0.04, store_cy + my_off, glass_z),
                 (0.10, 0.10, 2.5), COL_TRIM_BROWN)
    # Entry door (single flush)
    make_box("Store_Door",
             (store_cx - store_w/2 - 0.04, store_cy + 4.0, glass_z - 0.20),
             (0.08, 1.20, 2.20), COL_TRIM_BROWN)
    # "OPEN 24" stenciled box above the door (Label3D will spell
    # the text via LocaleSetup if we add a Sign_Panel here later)
    make_box("Store_OpenSign_Panel",
             (store_cx - store_w/2 - 0.05, store_cy + 4.0, ROAD_Z + 3.5),
             (0.06, 1.8, 0.55), COL_NEON_RED)
    # Brand awning above the storefront
    make_box("Store_Awning",
             (store_cx - store_w/2 - 0.35, store_cy, ROAD_Z + 3.0),
             (0.65, store_l - 0.6, 0.30), COL_PUMP_TRIM)
    # ICE machine + propane cage on the wall
    make_box("Store_IceMachine",
             (store_cx - store_w/2 + 0.50, store_cy - store_l/2 + 1.0, ROAD_Z + 0.85),
             (0.80, 1.20, 1.70), COL_TRIM_WHITE)
    make_box("Store_PropaneCage",
             (store_cx - store_w/2 + 0.50, store_cy + store_l/2 - 1.0, ROAD_Z + 0.65),
             (0.80, 1.40, 1.30), (0.50, 0.32, 0.18, 1.0))

    # ── Pole monument sign (Lobster cursive via LocaleSetup)
    sign_x = PARCEL_W_X + 3.0
    sign_y = GAS_Y_LO + 3.0
    make_cyl("Gas_Sign_Pole", (sign_x, sign_y, 3.8),
             0.16, 7.6, COL_POLE_METAL, segments=8)
    sign_w = 4.6
    sign_h = 2.4
    sign_z = 6.4
    # Two-sided panel (north + south, like riverfront)
    make_box("Sign_Panel_N", (sign_x, sign_y + 0.08, sign_z),
             (sign_w, 0.05, sign_h), COL_SIGN_PANEL)
    make_box("Sign_Panel_S", (sign_x, sign_y - 0.08, sign_z),
             (sign_w, 0.05, sign_h), COL_SIGN_PANEL)
    # Frames
    for face_y, lbl in ((0.10, "N"), (-0.10, "S")):
        make_box(f"Sign_Frame_{lbl}_top", (sign_x, sign_y + face_y, sign_z + sign_h/2 + 0.05),
                 (sign_w + 0.20, 0.06, 0.10), COL_SIGN_FRAME)
        make_box(f"Sign_Frame_{lbl}_low", (sign_x, sign_y + face_y, sign_z - sign_h/2 - 0.05),
                 (sign_w + 0.20, 0.06, 0.10), COL_SIGN_FRAME)
    # Price-board panel under the cursive
    make_box("Gas_PriceBoard", (sign_x, sign_y, sign_z - sign_h/2 - 0.50),
             (sign_w * 0.75, 0.06, 0.70), COL_GLASS_LIT)


# ═══════════════════════════════════════════════════════════════
# DRIVE-THRU FAST FOOD
# ═══════════════════════════════════════════════════════════════
def build_drive_thru():
    """Single-building drive-thru fast food with a drive-around lane
    and a small dining patio on the front."""
    parcel_cx = (PARCEL_W_X + PARCEL_E_X) / 2.0
    parcel_cy = (DRIVETHRU_Y_LO + DRIVETHRU_Y_HI) / 2.0
    parcel_w = PARCEL_E_X - PARCEL_W_X
    parcel_l = DRIVETHRU_Y_HI - DRIVETHRU_Y_LO

    # Asphalt lot
    make_box("DT_Lot", (parcel_cx, parcel_cy, ROAD_Z),
             (parcel_w, parcel_l, 0.04), COL_ASPHALT)

    # ── Main building (east-rear of parcel)
    bldg_w = 14.0
    bldg_l = 16.0
    bldg_h = 3.8
    bldg_cx = PARCEL_E_X - bldg_w/2 - 4.0
    bldg_cy = parcel_cy
    bldg_cz = ROAD_Z + bldg_h/2
    make_box("DT_Walls", (bldg_cx, bldg_cy, bldg_cz),
             (bldg_w, bldg_l, bldg_h), COL_BRICK_RED)
    # Roof (slight overhang)
    make_box("DT_Roof", (bldg_cx, bldg_cy, bldg_cz + bldg_h/2 + 0.15),
             (bldg_w + 0.60, bldg_l + 0.60, 0.30), COL_ROOF_DARK)
    # Mansard-y trim strip below roof
    make_box("DT_RoofTrim", (bldg_cx, bldg_cy, bldg_cz + bldg_h/2 - 0.20),
             (bldg_w + 0.30, bldg_l + 0.30, 0.40), COL_TRIM_WHITE)
    # Storefront windows (large)
    for wi, wy_off in enumerate((-4.0, -1.2, 1.6, 4.4)):
        make_box(f"DT_Window_{wi}",
                 (bldg_cx - bldg_w/2 - 0.02, bldg_cy + wy_off, bldg_cz + 0.30),
                 (0.06, 2.2, 1.8),
                 COL_GLASS_LIT)
    # Entry door
    make_box("DT_Door",
             (bldg_cx - bldg_w/2 - 0.04, bldg_cy - bldg_l/2 + 2.4, bldg_cz - 0.80),
             (0.10, 1.20, 2.20), COL_TRIM_BROWN)
    # Drive-thru window (side facing the drive lane)
    make_box("DT_OrderWindow",
             (bldg_cx + bldg_w/2 + 0.02, bldg_cy - 3.0, bldg_cz + 0.30),
             (0.08, 1.20, 1.20), COL_GLASS_LIT)
    make_box("DT_PickupWindow",
             (bldg_cx + bldg_w/2 + 0.02, bldg_cy + 2.0, bldg_cz + 0.30),
             (0.08, 1.20, 1.20), COL_GLASS_LIT)
    # Menu board on a post in the drive lane
    menu_x = PARCEL_E_X - 3.0
    menu_y = bldg_cy - 8.0
    make_cyl("DT_MenuPost", (menu_x, menu_y, 1.3), 0.10, 2.6,
             COL_POLE_METAL, segments=6)
    make_box("DT_MenuPanel", (menu_x, menu_y, 2.4),
             (0.06, 1.8, 1.6), COL_GLASS_LIT)
    # Roof sign (brand box on top of the building, edges)
    make_box("DT_BrandBox", (bldg_cx, bldg_cy, bldg_cz + bldg_h/2 + 1.40),
             (bldg_w - 4.0, 4.0, 1.40), COL_NEON_RED)

    # ── Drive lane stripe — a thin painted lane the cars follow
    # from the entry curb-cut, around the building, to the exit
    for li, (lx, ly_a, ly_b) in enumerate([
        (PARCEL_W_X + 6.0, parcel_cy - parcel_l/2 + 5.0, parcel_cy - 8.0),
        (PARCEL_W_X + 6.0, parcel_cy - 8.0, parcel_cy + 6.0),
    ]):
        make_box(f"DT_Lane_{li}_a",
                 (lx, (ly_a + ly_b)/2, ROAD_Z + 0.045),
                 (0.18, abs(ly_b - ly_a), 0.005), COL_YELLOW_LINE)

    # Patio — small set of tables at the parcel front
    patio_cx = PARCEL_W_X + 6.0
    patio_cy = parcel_cy + 4.0
    make_box("DT_Patio", (patio_cx, patio_cy, ROAD_Z + 0.07),
             (5.0, 4.0, 0.04), COL_CONCRETE)
    for ti, (tx_off, ty_off) in enumerate([(-1.4, -1.0), (1.4, -1.0), (-1.4, 1.0), (1.4, 1.0)]):
        make_cyl(f"DT_TableLeg_{ti}",
                 (patio_cx + tx_off, patio_cy + ty_off, ROAD_Z + 0.40),
                 0.06, 0.74, COL_POLE_METAL, segments=4)
        make_cyl(f"DT_TableTop_{ti}",
                 (patio_cx + tx_off, patio_cy + ty_off, ROAD_Z + 0.78),
                 0.55, 0.06, COL_TRIM_WHITE, segments=8)


# ═══════════════════════════════════════════════════════════════
# STRIP MALL — 4-bay frontage
# ═══════════════════════════════════════════════════════════════
def build_strip_mall():
    """Single long building, four storefront bays, each with its own
    glass + sign panel. Continuous flat roof."""
    parcel_cx = (PARCEL_W_X + PARCEL_E_X) / 2.0
    parcel_cy = (MALL_Y_LO + MALL_Y_HI) / 2.0
    parcel_w = PARCEL_E_X - PARCEL_W_X
    parcel_l = MALL_Y_HI - MALL_Y_LO

    # Lot
    make_box("Mall_Lot", (parcel_cx, parcel_cy, ROAD_Z),
             (parcel_w, parcel_l, 0.04), COL_ASPHALT)

    # Building (east half of parcel)
    bldg_w = 14.0
    bldg_l = parcel_l - 8.0
    bldg_h = 4.4
    bldg_cx = PARCEL_E_X - bldg_w/2 - 2.0
    bldg_cy = parcel_cy
    bldg_cz = ROAD_Z + bldg_h/2
    make_box("Mall_Walls", (bldg_cx, bldg_cy, bldg_cz),
             (bldg_w, bldg_l, bldg_h), COL_STUCCO_PEACH)
    make_box("Mall_Parapet",
             (bldg_cx, bldg_cy, bldg_cz + bldg_h/2 + 0.20),
             (bldg_w + 0.20, bldg_l + 0.20, 0.40), COL_ROOF_TAR)
    # Top trim band
    make_box("Mall_TopBand", (bldg_cx, bldg_cy, bldg_cz + bldg_h/2 - 0.20),
             (bldg_w + 0.10, bldg_l + 0.10, 0.40), COL_TRIM_WHITE)

    # Four bays — divide bldg_l into 4 storefronts
    n_bays = 4
    bay_l = bldg_l / n_bays
    bay_glass_z = ROAD_Z + 1.8
    bay_sign_z = ROAD_Z + 3.6
    bay_names = ["Laundr", "Tax_Hut", "Yang_Wok", "Phone_Repair"]
    for bi in range(n_bays):
        by = bldg_cy - bldg_l/2 + bay_l/2 + bi * bay_l
        # Plate glass storefront
        make_box(f"Mall_Bay_{bi}_glass",
                 (bldg_cx - bldg_w/2 - 0.02, by, bay_glass_z),
                 (0.06, bay_l - 1.0, 2.4),
                 COL_GLASS_LIT if bi % 2 == 0 else COL_GLASS_DARK)
        # Divider wall between bays (mullion column)
        if bi < n_bays - 1:
            make_box(f"Mall_Bay_div_{bi}",
                     (bldg_cx - bldg_w/2 - 0.04, by + bay_l/2, bldg_cz),
                     (0.18, 0.50, bldg_h),
                     COL_TRIM_BROWN)
        # Door (centered in each bay)
        make_box(f"Mall_Bay_{bi}_door",
                 (bldg_cx - bldg_w/2 - 0.05, by, bay_glass_z - 0.20),
                 (0.08, 1.10, 2.20), COL_TRIM_BROWN)
        # Bay sign panel above the bay — Label3D will read the bay name
        make_box(f"Mall_Bay_{bi}_sign_panel",
                 (bldg_cx - bldg_w/2 - 0.06, by, bay_sign_z),
                 (0.08, bay_l - 1.4, 0.85),
                 COL_SIGN_PANEL)
        # Awning over each bay
        make_box(f"Mall_Bay_{bi}_awning",
                 (bldg_cx - bldg_w/2 - 0.40, by, ROAD_Z + 2.95),
                 (0.65, bay_l - 1.4, 0.20),
                 COL_PUMP_TRIM if bi % 2 == 0 else (0.30, 0.42, 0.58, 1.0))

    # Sidewalk along the storefront
    make_box("Mall_Walk",
             (bldg_cx - bldg_w/2 - 1.5, bldg_cy, ROAD_Z + 0.07),
             (3.0, bldg_l + 0.20, 0.04),
             COL_CONCRETE)
    # Dumpster behind the building
    dump_x = bldg_cx + bldg_w/2 + 1.4
    dump_y = bldg_cy - bldg_l/2 + 3.0
    make_box("Mall_Dumpster", (dump_x, dump_y, ROAD_Z + 0.60),
             (1.6, 2.4, 1.10), (0.18, 0.28, 0.30, 1.0))
    make_prism("Mall_Dumpster_Lid", (dump_x, dump_y, ROAD_Z + 1.15),
               (1.6, 2.4, 0.20), (0.14, 0.20, 0.22, 1.0), pitch_axis='Y')

    # Lamp posts in the parking lot (2 sodium-style)
    for li, lx_o in enumerate((-12.0, +4.0)):
        lx = bldg_cx + lx_o
        ly = parcel_cy - parcel_l/2 + 6.0
        make_cyl(f"Mall_Lamp_{li}_pole", (lx, ly, 3.6),
                 0.10, 7.0, COL_POLE_METAL, segments=8)
        make_box(f"Mall_Lamp_{li}_arm", (lx + 0.5, ly, 7.0),
                 (0.8, 0.08, 0.08), COL_POLE_METAL)
        make_prism(f"Mall_Lamp_{li}_head", (lx + 0.9, ly, 6.85),
                   (0.5, 0.8, 0.22), (0.92, 0.62, 0.30, 1.0), pitch_axis='X')
        make_box(f"Mall_Lamp_{li}_lens", (lx + 0.9, ly, 6.78),
                 (0.42, 0.62, 0.04), (1.0, 0.72, 0.30, 1.0))


# ═══════════════════════════════════════════════════════════════
# PARKING LOT STRIPING + CARS + UTILITY DETAILS
# ═══════════════════════════════════════════════════════════════
def build_parking_lines():
    """Paint a row of parking stalls along each parcel's road-facing
    asphalt. Two stalls per parcel for compactness."""
    for parcel_y, label in [(GAS_Y_LO + 30.0, "Gas"),
                              (MALL_Y_LO + 35.0, "Mall"),
                              (DRIVETHRU_Y_LO + 30.0, "DT")]:
        for si in range(8):
            sx = PARCEL_W_X + 12.0 + si * 2.7
            sy = parcel_y - 5.0
            # Painted slot line
            make_box(f"{label}_Stall_{si}_W",
                     (sx, sy, ROAD_Z + 0.045),
                     (0.10, 5.0, 0.005), COL_WHITE_LINE)
        # End cap line
        make_box(f"{label}_Stall_endcap",
                 (PARCEL_W_X + 12.0 + 8 * 2.7, parcel_y - 5.0, ROAD_Z + 0.045),
                 (0.10, 5.0, 0.005), COL_WHITE_LINE)


def build_utility_details():
    """Telephone poles + fire hydrant + bus bench + small details
    that say 'a human laid this town out'."""
    # Telephone poles every 32m on the WEST side of the road
    for pi, py in enumerate(range(-120, 121, 32)):
        px = ROAD_CX - ROAD_W/2 - 1.6
        make_cyl(f"TelPole_{pi}_shaft", (px, float(py), 5.5), 0.16, 11.0,
                 COL_POLE_WOOD, segments=6)
        make_box(f"TelPole_{pi}_xarm_top",
                 (px, float(py), 9.6), (0.10, 2.4, 0.10), COL_POLE_WOOD)
        make_box(f"TelPole_{pi}_xarm_low",
                 (px, float(py), 8.6), (0.10, 1.6, 0.10), COL_POLE_WOOD)
        # 3 insulators per crossarm
        for ii, iy in enumerate([-1.0, 0.0, 1.0]):
            make_cyl(f"TelPole_{pi}_ins_top_{ii}",
                     (px, float(py) + iy, 9.75), 0.06, 0.18,
                     (0.85, 0.80, 0.72, 1.0), segments=6)
    # Fire hydrant near the road on the buffer side
    for hi, hy in enumerate([-40.0, 70.0]):
        hx = SIDE_E_X + 0.5
        make_cyl(f"FireHydrant_{hi}_base",
                 (hx, hy, BUFFER_Z + 0.35),
                 0.20, 0.70, COL_NEON_RED, segments=8)
        make_sphere(f"FireHydrant_{hi}_cap",
                    (hx, hy, BUFFER_Z + 0.78), 0.22, COL_NEON_RED)
    # Bus bench at the south end of the strip mall
    bx = SIDE_E_X + 1.4
    by = MALL_Y_LO - 4.0
    make_box("BusBench_Seat", (bx, by, BUFFER_Z + 0.45),
             (0.40, 1.8, 0.10), COL_TRIM_BROWN)
    make_box("BusBench_Back", (bx + 0.18, by, BUFFER_Z + 0.85),
             (0.06, 1.8, 0.70), COL_TRIM_BROWN)
    for li, ly_o in enumerate([-0.80, 0.80]):
        make_box(f"BusBench_Leg_{li}", (bx, by + ly_o, BUFFER_Z + 0.22),
                 (0.40, 0.10, 0.45), (0.18, 0.18, 0.18, 1.0))


# ═══════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════
def export_glb():
    out_dir = os.path.normpath(os.path.join(_SCRIPT_DIR, OUTPUT_DIR))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    print(f"\n[build_harmony_commercial] exporting to {out_path}")
    print(f"[build_harmony_commercial] scene objects: {len(bpy.context.scene.objects)}")
    bpy.ops.object.select_all(action='SELECT')
    base = {
        'filepath': out_path, 'export_format': 'GLB',
        'use_selection': False, 'export_apply': True,
        'export_lights': False, 'export_cameras': False,
    }
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    legacy = {}
    if 'export_colors' in rna.properties: legacy['export_colors'] = True
    if 'export_normals' in rna.properties: legacy['export_normals'] = True
    try:
        bpy.ops.export_scene.gltf(**base, **legacy)
    except Exception as e:
        print(f"[build_harmony_commercial] ✗ EXPORT FAILED: {e}")
        import traceback; traceback.print_exc()
        raise
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"[build_harmony_commercial] ✓ wrote {out_path} ({size} bytes)")


def main():
    print("[build_harmony_commercial] HCE-1 West Commercial Strip")
    # Clear default scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    build_ground_plates()
    build_road_and_sidewalk()
    build_gas_station()
    build_drive_thru()
    build_strip_mall()
    build_parking_lines()
    build_utility_details()
    export_glb()


if __name__ == "__main__":
    main()
