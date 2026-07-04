"""
build_nexcorp_fueling_station.py
══════════════════════════════════════════════════════════════════
VOL 6 · The NexCorp forecourt — EXTERIOR hero locale (7 VN bg refs
across 6 scene files; grep godot/resources/scenes for
"3d:nexcorp_fueling_station").

ADJUDICATION — one preset, two canon sites (wave-8 rule: the
binding is ground truth):
  · vol6_ch1_gas_and_go / vol6_ch2_gas_go_lot / vol6_ch2_gas_oracles
    — the NexCorp GAS & GO on Gallatin Ave, Harmony Creek Estates
    ("three blocks south on Gallatin, across the intersection with
    Fifth"; Sam watches it from the Kwik Stop lot across the street).
  · vol6_ch6_fueling_station / vol6_ch6_tome / vol6_ch6_boyd (2 bg
    refs) — a DIFFERENT NexCorp fueling station "off FM-3411" at the
    I-10 exit, "ninety-eight miles west" (vol6_ch6_kwik_stop_text:80,
    vol6_ch6_interstate).
  These are NOT the same building — but they bind the same 3D
  preset ON PURPOSE: NexCorp is a franchise, and franchise
  standardization ("Monday arrives ... dressed up as itself,
  indistinguishable") means the corporate forecourt is the same
  forecourt anywhere. So this locale is the BRAND-STANDARD NexCorp
  exterior: everything both sites share, nothing site-exclusive
  that would contradict either reading. It is the exterior sibling
  of build_nexcorp_gas_go.py (the interior GLB); the brand register
  below is copied from that file — KEEP IN SYNC.

Canon baked in (scene json : node):
  · vol6_ch1_gas_and_go:20 — "eight pumps and a car wash in the
    rear — the full automated tunnel kind." → 4 dispensers /
    8 fueling positions under the canopy; automated tunnel at the
    rear-east.
  · vol6_ch1_gas_and_go:28 — "the lot behind the car wash, which is
    technically for employee parking and which is not visible from
    the street or from the counter window." → striped employee lot
    behind the building/car-wash masses, screened by a fence run in
    the one sightline gap.
  · vol6_ch1_gas_and_go:24/28 — Skip behind the counter, the
    counter window. → real storefront OPENINGS (no glass slabs,
    playbook 2026-06-17) with a lit interior liner: counter,
    register, backbar, cooler glow, readable from the lot.
  · vol6_ch2_gas_go_lot:36/46 — Sam watching "from her car in the
    Kwik Stop lot across the street," "through her windshield."
    → the frontage road crosses the FOREGROUND; the camera stands
    on the far verge. Same framing serves ch1's street narration.
  · vol6_ch6_interstate — "the NexCorp station" at the FM-3411
    exit; "the transport van is currently parked at pump six ON THE
    BACK SIDE." → pumps 1-4 on the front island row, 5-8 on the
    back row; pump six is a back-row position.
  · vol6_ch6_fueling_station:32 — Vince smoking "on a no-smoking
    lot." → NO SMOKING placard on every dispenser (white plate,
    red band).
  · vol6_ch6_fueling_station:118 — "a beat-up sedan parked near the
    dumpster." → dumpster enclosure at the lot's rear-west corner
    with an empty striped stall beside it (see canon-negatives).
  · vol6_ch6_tome:38/42 — Claire pays at the counter, watches
    "through the front window," "crosses the lot." → open forecourt
    asphalt between pumps and storefront.
  · vol6_ch6_interstate — "the gravel shoulder of the I-10 service
    road." → gravel shoulders on the frontage road.
  · Brand vocabulary (KEEP IN SYNC with build_nexcorp_gas_go.py):
    corporate navy + amber accent, white letter blocks, navy
    bollards with amber caps (Kwik Stop's are yellow), camera domes
    over every zone, planogram-regular everything.

CANON-NEGATIVES (deliberately NOT built):
  · NO story vehicles. Every canon vehicle at this locale is
    transient WITHIN its own scene: the black Louisiana pickup
    (arrives 15:04, leaves 15:17+), the white NexCorp van (ch1:
    leaves 15:14; ch6: "The van is gone" is the climax line),
    Tomé's silver compact, Claire's white sedan, Vince's beat-up
    sedan ("drives away"). A baked vehicle contradicts the second
    half of every scene it appears in; the empty forecourt — "the
    empty space where the van had been" (vol6_ch6_boyd:66) — is
    the only state all seven bg displays share. (The gas_go GLB
    bakes the pickup+van because it serves ch1's single moment;
    this locale serves seven.)
  · No route markers / street-name signs — they would pin the
    locale to ONE of its two sites. The pylon price sign carries
    only the brand cabinet (Label3D territory if ever needed).
  · No people — VN sprites carry the cast.

Exterior discipline (playbook 2026-06-14): continuous GROUND first,
then circulation (frontage road, aprons, lot, side drive), THEN
features. Infrastructure on the planner's grid: streetlights and
utility poles on the buffer strip, never in the road; the pylon
sign set back on commercial property at the lot's road-facing
corner, panel facing the road. Drainage ditch with tannin water on
the lot side, culverts under both aprons (gulf-coast water table).
Camera preset (Background3D.gd): (0, 2.30, +0.5) / yaw 180 /
fov 60 — content at Blender y >= 0, camera on the far road verge
looking north: road foreground, canopy + pumps mid-frame, the
storefront holding the frame, car wash rear-east, tree line horizon.

Run:
    blender --background --python build_nexcorp_fueling_station.py

Output:
    godot/assets/3d/locales/nexcorp_fueling_station.glb
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, _finalize_mesh

# ── NexCorp brand register — KEEP IN SYNC with build_nexcorp_gas_go.py ──
COL_WALL_NEXCORP    = (0.16, 0.32, 0.56, 1.0)   # NexCorp corporate blue
COL_AMBER_NEX       = (0.84, 0.64, 0.28, 1.0)   # canon NexCorp accent
COL_WHITE_PANEL     = (0.96, 0.96, 0.96, 1.0)
COL_CHROME          = (0.78, 0.80, 0.82, 1.0)
COL_CONCRETE        = (0.62, 0.60, 0.56, 1.0)
COL_ASPHALT         = (0.20, 0.20, 0.22, 1.0)
COL_STRIPE_WHITE    = (0.88, 0.88, 0.86, 1.0)
COL_METAL_STEEL     = (0.66, 0.68, 0.70, 1.0)
COL_METAL_BLACK     = (0.18, 0.16, 0.14, 1.0)
COL_DARK_SCREEN     = (0.10, 0.12, 0.15, 1.0)
COL_SCREEN_BLUE     = (0.42, 0.62, 0.88, 1.0)
COL_CAM_SMOKE       = (0.12, 0.12, 0.14, 1.0)
COL_PLASTIC_GREY    = (0.52, 0.53, 0.55, 1.0)
COL_RED_ACCENT      = (0.86, 0.42, 0.32, 1.0)
COL_COUNTER_LAMINATE= (0.42, 0.40, 0.38, 1.0)
# ── Site palette (Gulf-coast Texas roadside; vertex colors only) ──
COL_GROUND      = (0.42, 0.42, 0.26, 1.0)   # dry roadside scrub
COL_SCRUB       = (0.50, 0.47, 0.28, 1.0)   # scorched patches
COL_GRAVEL      = (0.55, 0.52, 0.46, 1.0)   # the gravel shoulder
COL_ASPH_WEAR   = (0.16, 0.16, 0.18, 1.0)
COL_ASPH_PATCH  = (0.24, 0.24, 0.26, 1.0)
COL_DITCH       = (0.31, 0.30, 0.19, 1.0)   # damp drainage ditch
COL_TANNIN      = (0.29, 0.25, 0.15, 1.0)   # standing tannin water
COL_CURB        = (0.68, 0.66, 0.60, 1.0)
COL_LINE_YEL    = (0.80, 0.66, 0.20, 1.0)   # road centerline
COL_CMU         = (0.80, 0.80, 0.78, 1.0)   # building block, corporate white
COL_CMU_SHADE   = (0.72, 0.72, 0.70, 1.0)
COL_ROOF_METAL  = (0.58, 0.60, 0.62, 1.0)
COL_GALV        = (0.56, 0.58, 0.60, 1.0)
COL_STEEL_DK    = (0.30, 0.31, 0.33, 1.0)
COL_TINT_GLASS  = (0.14, 0.15, 0.17, 1.0)   # dark mouth / opaque panes
COL_FLOOR_TILE  = (0.78, 0.74, 0.70, 1.0)   # interior liner floor
COL_CEIL_TILE   = (0.86, 0.88, 0.86, 1.0)
COL_TUBE_LIT    = (0.96, 0.96, 0.92, 1.0)
COL_TRUNK       = (0.34, 0.26, 0.19, 1.0)
COL_OAK_A       = (0.26, 0.37, 0.21, 1.0)
COL_OAK_B       = (0.22, 0.32, 0.18, 1.0)
COL_PINE        = (0.19, 0.30, 0.19, 1.0)

# ── Layout constants (Blender Z-up, 1 unit = 1 m) ─────────────────
ROAD_Y0, ROAD_Y1 = 1.0, 8.2         # frontage road (Gallatin / FM-3411)
DITCH_Y = 9.8                        # lot-side drainage ditch centerline
CURB_Y  = 10.6                       # commercial curb line
LOT_Y0, LOT_Y1 = 10.8, 39.0
LOT_X0, LOT_X1 = -18.0, 18.0
APRON_W_CX, APRON_E_CX = -11.5, 11.5  # driveway aprons crossing the ditch
CANOPY_CX, CANOPY_CY = 0.0, 19.5
ISL_Y_FRONT, ISL_Y_BACK = 16.2, 22.8  # pumps 1-4 front, 5-8 BACK row
BLD_X0, BLD_X1 = -9.0, 9.0
BLD_Y0, BLD_Y1 = 30.0, 38.0
BLD_H = 3.6                          # wall height (fascia above)
CW_X0, CW_X1 = 11.5, 17.5            # car wash tunnel, rear-east
CW_Y0, CW_Y1 = 29.0, 38.0
EMP_Y0, EMP_Y1 = 40.0, 46.0          # employee lot, hidden behind masses
LOT_TOP, ROAD_TOP, WALK_TOP = 0.04, 0.04, 0.06


# ── Local helper — tube between two points (playbook: diagonals are
#    never stair-stepped boxes). Same construction as the school-
#    field exemplar's make_tube.
def make_tube(name, p0, p1, radius, color, segments=8):
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    if L < 1e-9:
        return None
    wx, wy, wz = dx / L, dy / L, dz / L
    cx_, cy_, cz_ = wy, -wx, 0.0                    # w x Z-hat
    m = math.sqrt(cx_ * cx_ + cy_ * cy_ + cz_ * cz_)
    if m < 1e-6:
        cx_, cy_, cz_ = 0.0, wz, -wy                # w x X-hat
        m = math.sqrt(cx_ * cx_ + cy_ * cy_ + cz_ * cz_)
    e1 = (cx_ / m, cy_ / m, cz_ / m)
    e2 = (wy * e1[2] - wz * e1[1], wz * e1[0] - wx * e1[2],
          wx * e1[1] - wy * e1[0])
    verts = []
    for base in (p0, p1):
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            ca, sa = math.cos(a) * radius, math.sin(a) * radius
            verts.append((base[0] + ca * e1[0] + sa * e2[0],
                          base[1] + ca * e1[1] + sa * e2[1],
                          base[2] + ca * e1[2] + sa * e2[2]))
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, ni + segments, i + segments])
    faces.append(list(reversed(range(segments))))
    faces.append(list(range(segments, segments * 2)))
    return _finalize_mesh(name, verts, faces, color)


# ══════════════════════════════════════════════════════════════════
# GROUND — one continuous plane under the ENTIRE world (playbook
# 2026-06-14: ground first, or the locale is floating islands).
# Top at z = 0; extends south past the camera so no void shows.
# ══════════════════════════════════════════════════════════════════
def build_ground():
    make_box("Ground", (0.0, 32.5, -0.06), (160.0, 125.0, 0.12), COL_GROUND)
    # Scorched scrub patches (deterministic, hand-baked)
    patches = [(-34.0, -6.0, 9.0, 5.0), (28.0, -8.0, 7.0, 4.0),
               (-46.0, 22.0, 10.0, 6.0), (44.0, 18.0, 8.0, 5.0),
               (-30.0, 48.0, 9.0, 6.0), (30.0, 50.0, 7.0, 5.0),
               (-52.0, 60.0, 11.0, 7.0), (8.0, 60.0, 8.0, 5.0),
               (52.0, 44.0, 9.0, 6.0), (-12.0, -10.0, 6.0, 4.0)]
    for i, (px, py, pw, pl) in enumerate(patches):
        make_box(f"Scrub_{i}", (px, py, 0.003), (pw, pl, 0.006), COL_SCRUB)


# ══════════════════════════════════════════════════════════════════
# CIRCULATION — the frontage road across the foreground (ch2: Sam
# watches from across the street; ch6: the I-10 service road),
# gravel shoulders ("the gravel shoulder", vol6_ch6_interstate),
# lot-side drainage ditch with culverts under both aprons, curb,
# the commercial lot, the side drive to the car wash. Roads BEFORE
# features.
# ══════════════════════════════════════════════════════════════════
def build_road():
    rcy = (ROAD_Y0 + ROAD_Y1) / 2.0
    make_box("Road", (0.0, rcy, 0.02), (160.0, ROAD_Y1 - ROAD_Y0, 0.04),
             COL_ASPHALT)
    # Yellow centerline dashes + white edge lines, lifted above
    for i in range(-13, 14):
        make_box(f"Road_Dash_{i + 13}", (i * 6.0, rcy, ROAD_TOP + 0.004),
                 (2.6, 0.12, 0.006), COL_LINE_YEL)
    for tag, ey in (("S", ROAD_Y0 + 0.35), ("N", ROAD_Y1 - 0.35)):
        make_box(f"Road_Edge_{tag}", (0.0, ey, ROAD_TOP + 0.004),
                 (160.0, 0.10, 0.006), COL_STRIPE_WHITE)
    # Wear splotches + one square repave patch (roads are not pristine)
    wear = [(-22.0, rcy - 1.4, 5.0, 2.2), (9.0, rcy + 1.5, 4.0, 2.0),
            (34.0, rcy - 0.8, 6.0, 2.4), (-49.0, rcy + 0.9, 5.0, 2.0)]
    for i, (px, py, pw, pl) in enumerate(wear):
        make_box(f"Road_Wear_{i}", (px, py, ROAD_TOP + 0.002),
                 (pw, pl, 0.004), COL_ASPH_WEAR)
    make_box("Road_Patch", (-4.0, rcy - 1.6, ROAD_TOP + 0.002),
             (3.2, 2.6, 0.005), COL_ASPH_PATCH)
    # Gravel shoulders both sides
    make_box("Shoulder_S", (0.0, ROAD_Y0 - 0.5, 0.008), (160.0, 1.0, 0.016),
             COL_GRAVEL)
    make_box("Shoulder_N", (0.0, ROAD_Y1 + 0.4, 0.008), (160.0, 0.8, 0.016),
             COL_GRAVEL)
    # Lot-side drainage ditch (gulf-coast water table) with standing
    # tannin water, broken by the two driveway aprons
    for i, (dx0, dx1) in enumerate([(-80.0, APRON_W_CX - 3.2),
                                    (APRON_W_CX + 3.2, APRON_E_CX - 3.2),
                                    (APRON_E_CX + 3.2, 80.0)]):
        make_box(f"Ditch_{i}", ((dx0 + dx1) / 2.0, DITCH_Y, 0.004),
                 (dx1 - dx0, 1.2, 0.008), COL_DITCH)
    for i, (px, pw) in enumerate([(-30.0, 6.0), (2.0, 4.0), (30.0, 5.0)]):
        make_box(f"Ditch_Water_{i}", (px, DITCH_Y, 0.009), (pw, 0.8, 0.006),
                 COL_TANNIN)
    # Driveway aprons over galvanized culverts
    for tag, acx in (("W", APRON_W_CX), ("E", APRON_E_CX)):
        make_box(f"Apron_{tag}", (acx, (ROAD_Y1 + LOT_Y0) / 2.0, 0.02),
                 (6.0, LOT_Y0 - ROAD_Y1, 0.04), COL_ASPHALT)
        make_cyl(f"Culvert_{tag}", (acx, DITCH_Y, 0.16), 0.24, 6.6,
                 COL_GALV, segments=10, axis='X')
    # Concrete curb along the commercial frontage between the aprons
    for i, (cx0, cx1) in enumerate([(LOT_X0, APRON_W_CX - 3.0),
                                    (APRON_W_CX + 3.0, APRON_E_CX - 3.0),
                                    (APRON_E_CX + 3.0, LOT_X1)]):
        make_box(f"Curb_{i}", ((cx0 + cx1) / 2.0, CURB_Y, 0.07),
                 (cx1 - cx0, 0.35, 0.14), COL_CURB)
    # Sewer grate at the curb line (playbook: curb-line intervals)
    make_box("Sewer_Frame", (5.5, CURB_Y - 0.45, 0.045), (0.90, 0.55, 0.01),
             COL_STEEL_DK)
    for s in range(4):
        make_box(f"Sewer_Slat_{s}", (5.5, CURB_Y - 0.62 + s * 0.12, 0.052),
                 (0.74, 0.05, 0.006), COL_METAL_BLACK)


def build_lot():
    make_box("Lot", (0.0, (LOT_Y0 + LOT_Y1) / 2.0, 0.02),
             (LOT_X1 - LOT_X0, LOT_Y1 - LOT_Y0, 0.04), COL_ASPHALT)
    # Side drive to the car wash mouth + the turn pad behind
    make_box("Drive_CW", ((CW_X0 + CW_X1) / 2.0, (LOT_Y0 + CW_Y0) / 2.0, 0.02),
             (CW_X1 - CW_X0, CW_Y0 - LOT_Y0, 0.04), COL_ASPHALT)
    make_box("Drive_CW_Exit", ((CW_X0 + CW_X1) / 2.0, (CW_Y1 + EMP_Y1) / 2.0, 0.02),
             (CW_X1 - CW_X0, EMP_Y1 - CW_Y1, 0.04), COL_ASPHALT)
    # Employee lot behind the building / car wash (ch1:28 — "not
    # visible from the street or from the counter window")
    make_box("EmpLot", (9.0, (EMP_Y0 + EMP_Y1) / 2.0, 0.02),
             (16.0, EMP_Y1 - EMP_Y0, 0.04), COL_ASPHALT)
    for i in range(4):
        make_box(f"EmpLot_Stripe_{i}", (3.0 + i * 3.0, EMP_Y0 + 1.6, LOT_TOP + 0.004),
                 (0.08, 3.2, 0.006), COL_STRIPE_WHITE)
    # Oil-stain wear where cars idle at the pumps + general splotches
    stains = [(-3.8, ISL_Y_FRONT - 1.9, 1.6, 1.0), (3.8, ISL_Y_FRONT - 1.9, 1.4, 0.9),
              (-3.8, ISL_Y_BACK + 1.9, 1.5, 1.0), (3.8, ISL_Y_BACK + 1.9, 1.6, 0.9),
              (-10.0, 27.0, 3.0, 2.0), (12.5, 14.5, 2.6, 1.8)]
    for i, (px, py, pw, pl) in enumerate(stains):
        make_box(f"Lot_Stain_{i}", (px, py, LOT_TOP + 0.002), (pw, pl, 0.004),
                 COL_ASPH_WEAR)
    # Customer stalls along the storefront walk + curb stops
    for i in range(5):
        sx = -7.6 + i * 2.9
        make_box(f"Park_Stripe_{i}", (sx, BLD_Y0 - 3.3, LOT_TOP + 0.004),
                 (0.08, 4.6, 0.006), COL_STRIPE_WHITE)
    for i in range(4):
        make_box(f"Curb_Stop_{i}", (-6.15 + i * 2.9, BLD_Y0 - 1.6, 0.06),
                 (1.60, 0.18, 0.12), COL_CONCRETE)
    # Underground-tank fill lids, flush in the lot (product-color
    # coded) + the tank vent-pipe cluster at the west edge
    for i, (lx, lcol) in enumerate([(-5.4, COL_WHITE_PANEL),
                                    (-3.9, COL_AMBER_NEX),
                                    (-2.4, COL_WALL_NEXCORP)]):
        make_cyl(f"Tank_Lid_{i}", (lx, 12.8, LOT_TOP + 0.005), 0.32, 0.01,
                 COL_CONCRETE, segments=12)
        make_cyl(f"Tank_Cap_{i}", (lx, 12.8, LOT_TOP + 0.012), 0.18, 0.012,
                 lcol, segments=12)
    for i in range(3):
        make_cyl(f"Vent_Pipe_{i}", (-17.3, 20.4 + i * 0.9, 1.9), 0.05, 3.8,
                 COL_GALV, segments=8)
        make_cyl(f"Vent_Cap_{i}", (-17.3, 20.4 + i * 0.9, 3.86), 0.09, 0.12,
                 COL_STEEL_DK, segments=8)
    # Directional arrow at the west apron throat
    make_box("Lot_Arrow_Shaft", (APRON_W_CX, 12.6, LOT_TOP + 0.004),
             (0.16, 1.6, 0.006), COL_STRIPE_WHITE)
    make_box("Lot_Arrow_Head", (APRON_W_CX, 13.6, LOT_TOP + 0.004),
             (0.55, 0.30, 0.006), COL_STRIPE_WHITE)


# ══════════════════════════════════════════════════════════════════
# PYLON PRICE SIGN — at the lot's road-facing SW corner, ON
# commercial property, set back from the curb, panel facing the
# road (playbook infrastructure-placement rule). Brand cabinet +
# three dark price rows + amber CAR WASH tier. No text — Label3D
# territory.
# ══════════════════════════════════════════════════════════════════
def build_pylon_sign():
    px, py = -13.5, 12.6
    make_cyl("Pylon_Pole", (px, py, 3.2), 0.16, 6.4, COL_METAL_STEEL,
             segments=10)
    make_box("Pylon_PoleWrap", (px, py, 0.55), (0.60, 0.60, 1.10),
             COL_WALL_NEXCORP)
    # Brand cabinet (navy, white letter band = Label3D anchor face)
    make_box("Pylon_Brand", (px, py, 7.0), (3.00, 0.30, 1.20),
             COL_WALL_NEXCORP)
    make_box("Pylon_Brand_Band", (px, py - 0.165, 7.0), (2.40, 0.03, 0.55),
             COL_WHITE_PANEL)
    make_box("Pylon_Brand_Accent", (px, py, 6.34), (3.00, 0.32, 0.08),
             COL_AMBER_NEX)
    # Price cabinet — three dark rows on white
    make_box("Pylon_Price", (px, py, 5.35), (2.60, 0.24, 1.70),
             COL_WHITE_PANEL)
    for r in range(3):
        make_box(f"Pylon_Price_Row_{r}", (px, py - 0.135, 5.85 - r * 0.50),
                 (2.20, 0.02, 0.36), COL_DARK_SCREEN)
    # CAR WASH tier (amber — matches the interior menu's top tier)
    make_box("Pylon_Carwash", (px, py, 4.28), (2.60, 0.22, 0.36),
             COL_AMBER_NEX)
    make_box("Pylon_Carwash_Band", (px, py - 0.125, 4.28), (2.00, 0.02, 0.20),
             COL_WHITE_PANEL)


# ══════════════════════════════════════════════════════════════════
# CANOPY + PUMPS — the hero mass. 4 dispensers = the canonical
# EIGHT fueling positions (ch1:20). Two island rows: pumps 1-4
# front, 5-8 back — "pump six on the back side"
# (vol6_ch6_interstate). Navy fascia + amber accent + NEXCORP
# letter blocks on the road face, recessed light panels, camera
# domes under the deck (the forecourt watches itself).
# ══════════════════════════════════════════════════════════════════
def build_canopy():
    cx, cy = CANOPY_CX, CANOPY_CY
    make_box("Canopy_Deck", (cx, cy, 5.35), (17.0, 12.0, 0.35),
             COL_ROOF_METAL)
    # Fascia band around all four edges + amber accent line (south)
    make_box("Canopy_Fascia_S", (cx, cy - 6.06, 5.05), (17.4, 0.14, 0.80),
             COL_WALL_NEXCORP)
    make_box("Canopy_Fascia_N", (cx, cy + 6.06, 5.05), (17.4, 0.14, 0.80),
             COL_WALL_NEXCORP)
    for tag, fx in (("W", cx - 8.56), ("E", cx + 8.56)):
        make_box(f"Canopy_Fascia_{tag}", (fx, cy, 5.05), (0.14, 12.25, 0.80),
                 COL_WALL_NEXCORP)
    make_box("Canopy_Accent", (cx, cy - 6.10, 4.68), (17.4, 0.06, 0.08),
             COL_AMBER_NEX)
    # NEXCORP letter blocks, road face (7 blocks, gas_go convention)
    for i in range(7):
        make_box(f"Canopy_Letter_{i}", (cx - 1.44 + i * 0.48, cy - 6.145, 5.05),
                 (0.32, 0.03, 0.40), COL_WHITE_PANEL)
    # Columns at the island ends, steel with navy impact wrap
    for ci, (px, py) in enumerate([(-7.4, ISL_Y_FRONT), (7.4, ISL_Y_FRONT),
                                   (-7.4, ISL_Y_BACK), (7.4, ISL_Y_BACK)]):
        make_cyl(f"Canopy_Col_{ci}", (px, py, 2.60), 0.20, 5.20,
                 COL_METAL_STEEL, segments=10)
        make_box(f"Canopy_ColWrap_{ci}", (px, py, 0.60), (0.56, 0.56, 1.20),
                 COL_WALL_NEXCORP)
        make_box(f"Canopy_ColWrap_Cap_{ci}", (px, py, 1.23), (0.60, 0.60, 0.06),
                 COL_AMBER_NEX)
    # Recessed light panels over each fueling position
    for li, (lx, ly) in enumerate([(-3.8, ISL_Y_FRONT), (3.8, ISL_Y_FRONT),
                                   (-3.8, ISL_Y_BACK), (3.8, ISL_Y_BACK)]):
        make_box(f"Canopy_Light_A_{li}", (lx, ly - 1.5, 5.14),
                 (1.30, 0.70, 0.06), COL_TUBE_LIT)
        make_box(f"Canopy_Light_B_{li}", (lx, ly + 1.5, 5.14),
                 (1.30, 0.70, 0.06), COL_TUBE_LIT)
    # Under-deck camera domes — one per island row
    for di, dy in enumerate([ISL_Y_FRONT, ISL_Y_BACK]):
        make_cyl(f"Canopy_CamRing_{di}", (0.0, dy, 5.15), 0.10, 0.03,
                 COL_WHITE_PANEL, segments=12)
        make_cyl(f"Canopy_CamDome_{di}", (0.0, dy, 5.10), 0.075, 0.09,
                 COL_CAM_SMOKE, segments=12)


def _dispenser(prefix, dx, dy):
    """One two-sided dispenser = two fueling positions. Blue price
    screens both faces, hose holsters both sides, NO SMOKING plate
    (canon: Vince smokes on a no-smoking lot, ch6:32)."""
    make_box(f"{prefix}_Body", (dx, dy, 1.12), (0.66, 0.56, 1.60),
             COL_PLASTIC_GREY)
    make_box(f"{prefix}_Skirt", (dx, dy, 0.26), (0.72, 0.62, 0.52),
             COL_WALL_NEXCORP)
    make_box(f"{prefix}_Crown", (dx, dy, 1.99), (0.74, 0.64, 0.18),
             COL_WALL_NEXCORP)
    make_box(f"{prefix}_Crown_Accent", (dx, dy, 1.905), (0.76, 0.66, 0.04),
             COL_AMBER_NEX)
    # Position number plates on the crown, both faces (Label3D
    # territory for the digits; the plate is the anchor)
    for sgn, tag in ((-1, "S"), (+1, "N")):
        make_box(f"{prefix}_NumPlate_{tag}", (dx, dy + sgn * 0.335, 1.99),
                 (0.22, 0.01, 0.14), COL_WHITE_PANEL)
        make_box(f"{prefix}_Screen_{tag}", (dx, dy + sgn * 0.295, 1.50),
                 (0.44, 0.03, 0.30), COL_SCREEN_BLUE)
        make_box(f"{prefix}_Keypad_{tag}", (dx, dy + sgn * 0.295, 1.16),
                 (0.30, 0.02, 0.18), COL_METAL_BLACK)
        make_box(f"{prefix}_NoSmoke_{tag}", (dx, dy + sgn * 0.29, 0.78),
                 (0.20, 0.012, 0.14), COL_WHITE_PANEL)
        make_box(f"{prefix}_NoSmoke_Band_{tag}", (dx, dy + sgn * 0.297, 0.78),
                 (0.16, 0.012, 0.03), COL_RED_ACCENT)
    for sgn, tag in ((-1, "W"), (+1, "E")):
        make_cyl(f"{prefix}_Holster_{tag}", (dx + sgn * 0.30, dy, 1.30),
                 0.045, 0.55, COL_METAL_BLACK, segments=8)
        make_box(f"{prefix}_Nozzle_{tag}", (dx + sgn * 0.36, dy, 1.02),
                 (0.08, 0.16, 0.14), COL_METAL_BLACK)
        # Hose loop — a sagging tube, never a stair-stepped box
        make_tube(f"{prefix}_Hose_{tag}", (dx + sgn * 0.33, dy + 0.10, 1.55),
                  (dx + sgn * 0.40, dy - 0.14, 0.70), 0.028, COL_METAL_BLACK)


def build_pumps():
    # Islands: concrete rafts, navy bollards with amber caps
    # (Kwik Stop's bollards are yellow; NexCorp paints them navy),
    # squeegee service stations, uniform navy trash cans.
    for ri, iy in enumerate([ISL_Y_FRONT, ISL_Y_BACK]):
        for ii, ix in enumerate([-3.8, 3.8]):
            pref = f"Isl_{ri}_{ii}"
            make_box(f"{pref}_Raft", (ix, iy, 0.09), (4.6, 1.15, 0.18),
                     COL_CONCRETE)
            for bi, bx in enumerate([ix - 2.05, ix + 2.05]):
                make_cyl(f"{pref}_Bollard_{bi}", (bx, iy, 0.52), 0.07, 0.88,
                         COL_WALL_NEXCORP, segments=10)
                make_cyl(f"{pref}_Bollard_Cap_{bi}", (bx, iy, 0.98), 0.075,
                         0.04, COL_AMBER_NEX, segments=10)
            _dispenser(f"Pump_{ri}_{ii}", ix, iy)
        # One squeegee station + one trash can per row, outer islands
        sq_x = -3.8 - 1.35 if ri == 0 else 3.8 + 1.35
        sq_y = iy
        make_cyl(f"Squeegee_Post_{ri}", (sq_x, sq_y, 0.60), 0.03, 1.20,
                 COL_PLASTIC_GREY, segments=8)
        make_box(f"Squeegee_Box_{ri}", (sq_x, sq_y, 1.22), (0.30, 0.22, 0.26),
                 COL_WALL_NEXCORP)
        make_cyl(f"Squeegee_Bucket_{ri}", (sq_x, sq_y, 0.30), 0.13, 0.24,
                 COL_METAL_BLACK, segments=10)
        tr_x = 3.8 + 1.35 if ri == 0 else -3.8 - 1.35
        make_cyl(f"Isl_Trash_{ri}", (tr_x, iy, 0.42), 0.16, 0.80,
                 COL_WALL_NEXCORP, segments=10)
        make_cyl(f"Isl_Trash_Lid_{ri}", (tr_x, iy, 0.84), 0.17, 0.05,
                 COL_METAL_BLACK, segments=10)


# ══════════════════════════════════════════════════════════════════
# THE STATION BUILDING — corporate CMU box, navy fascia + NEXCORP
# letter blocks + amber stripe. Storefront is REAL OPENINGS (no
# glass slabs) with a lit interior liner so "the counter window"
# reads from the lot: floor, counter, register, backbar, cooler
# glow (ch1:24/28 Skip behind the counter; ch6_tome:38 Claire pays
# and watches through the front window).
# ══════════════════════════════════════════════════════════════════
def build_building():
    bcx = (BLD_X0 + BLD_X1) / 2.0
    bcy = (BLD_Y0 + BLD_Y1) / 2.0
    # Slab the building sits on
    make_box("Bld_Slab", (bcx, bcy, 0.05), (18.4, 8.4, 0.10), COL_CONCRETE)
    # Walls: N / E / W solid; S is the storefront
    make_box("Bld_Wall_N", (bcx, BLD_Y1, BLD_H / 2.0 + 0.10),
             (18.0, 0.24, BLD_H), COL_CMU_SHADE)
    for tag, wx in (("W", BLD_X0), ("E", BLD_X1)):
        make_box(f"Bld_Wall_{tag}", (wx, bcy, BLD_H / 2.0 + 0.10),
                 (0.24, 8.0, BLD_H), COL_CMU_SHADE)
    # Storefront south face — piers + sills + headers around REAL
    # openings. Door x [-1.1, 1.1]; windows x [±1.7, ±6.3].
    for tag, px in (("W", -7.65), ("E", 7.65)):
        make_box(f"Bld_Pier_{tag}", (px, BLD_Y0, BLD_H / 2.0 + 0.10),
                 (2.70, 0.24, BLD_H), COL_CMU)
    for sgn, tag in ((-1, "W"), (+1, "E")):
        make_box(f"Bld_Pier_Door_{tag}", (sgn * 1.40, BLD_Y0, BLD_H / 2.0 + 0.10),
                 (0.60, 0.24, BLD_H), COL_CMU)
        make_box(f"Bld_Sill_{tag}", (sgn * 4.0, BLD_Y0, 0.475),
                 (4.60, 0.24, 0.75), COL_CMU)
        make_box(f"Bld_Head_{tag}", (sgn * 4.0, BLD_Y0, 3.325),
                 (4.60, 0.24, 0.55), COL_CMU)
    make_box("Bld_Head_Door", (0.0, BLD_Y0, 3.20), (2.20, 0.24, 0.80),
             COL_CMU)
    # Window frames + mullions (openings stay OPEN — no glass slab)
    for sgn, tag in ((-1, "W"), (+1, "E")):
        wx = sgn * 4.0
        make_box(f"Win_{tag}_Frame_T", (wx, BLD_Y0, 3.02), (4.64, 0.10, 0.08),
                 COL_METAL_STEEL)
        make_box(f"Win_{tag}_SillCap", (wx, BLD_Y0, 0.88), (4.70, 0.18, 0.07),
                 COL_METAL_STEEL)
        for side in (-1, +1):
            make_box(f"Win_{tag}_Side_{'W' if side < 0 else 'E'}",
                     (wx + side * 2.28, BLD_Y0, 1.95), (0.08, 0.10, 2.14),
                     COL_METAL_STEEL)
        for k in (-1, +1):
            make_box(f"Win_{tag}_MullV_{'W' if k < 0 else 'E'}",
                     (wx + k * 0.76, BLD_Y0, 1.95), (0.06, 0.08, 2.10),
                     COL_METAL_STEEL)
        make_box(f"Win_{tag}_MullH", (wx, BLD_Y0, 2.10), (4.56, 0.08, 0.06),
                 COL_METAL_STEEL)
    # Storefront door — aluminum frame, open glazing, push rail
    make_box("Door_Frame_T", (0.0, BLD_Y0, 2.62), (2.30, 0.12, 0.10),
             COL_METAL_STEEL)
    for sgn, tag in ((-1, "W"), (+1, "E")):
        make_box(f"Door_Jamb_{tag}", (sgn * 1.06, BLD_Y0, 1.31),
                 (0.10, 0.12, 2.62), COL_METAL_STEEL)
    make_box("Door_Stile_Mid", (0.0, BLD_Y0, 1.31), (0.14, 0.08, 2.62),
             COL_METAL_STEEL)
    make_box("Door_PushRail", (0.0, BLD_Y0, 1.10), (1.96, 0.07, 0.14),
             COL_METAL_STEEL)
    make_box("Door_Kick", (0.0, BLD_Y0, 0.20), (1.96, 0.07, 0.36),
             COL_METAL_STEEL)
    # Fascia — navy band with white NEXCORP blocks + amber stripe
    make_box("Fascia_S", (bcx, BLD_Y0 - 0.02, BLD_H + 0.50),
             (18.6, 0.30, 0.85), COL_WALL_NEXCORP)
    make_box("Fascia_Accent", (bcx, BLD_Y0 - 0.19, BLD_H + 0.045),
             (18.6, 0.05, 0.07), COL_AMBER_NEX)
    for i in range(7):
        make_box(f"Fascia_Letter_{i}", (bcx - 1.68 + i * 0.56, BLD_Y0 - 0.185,
                 BLD_H + 0.50), (0.38, 0.03, 0.46), COL_WHITE_PANEL)
    for tag, wx in (("W", BLD_X0), ("E", BLD_X1)):
        make_box(f"Fascia_Return_{tag}", (wx, bcy, BLD_H + 0.50),
                 (0.30, 8.4, 0.85), COL_WALL_NEXCORP)
    make_box("Fascia_N", (bcx, BLD_Y1 + 0.02, BLD_H + 0.50),
             (18.6, 0.28, 0.85), COL_CMU_SHADE)
    # Roof + parapet mech (visible over the fascia at this distance)
    make_box("Bld_Roof", (bcx, bcy, BLD_H + 0.12), (18.0, 8.0, 0.10),
             COL_ROOF_METAL)
    make_box("Bld_RTU", (3.5, 34.5, BLD_H + 0.62), (2.4, 1.6, 0.90),
             COL_ROOF_METAL)
    make_box("Bld_RTU_Grille", (3.5, 33.68, BLD_H + 0.62), (1.8, 0.05, 0.55),
             COL_STEEL_DK)
    make_cyl("Bld_VentStack", (-4.5, 36.5, BLD_H + 0.75), 0.10, 1.30,
             COL_GALV, segments=8)
    # Corner camera domes + door camera (six cameras is the brand)
    for ci, (cx_, cy_) in enumerate([(BLD_X0 + 0.4, BLD_Y0 + 0.2),
                                     (BLD_X1 - 0.4, BLD_Y0 + 0.2)]):
        make_box(f"Ext_Cam_Arm_{ci}", (cx_, cy_ - 0.32, BLD_H - 0.15),
                 (0.08, 0.30, 0.08), COL_PLASTIC_GREY)
        make_box(f"Ext_Cam_Body_{ci}", (cx_, cy_ - 0.52, BLD_H - 0.18),
                 (0.12, 0.20, 0.12), COL_PLASTIC_GREY)
        make_cyl(f"Ext_Cam_Lens_{ci}", (cx_, cy_ - 0.63, BLD_H - 0.18),
                 0.04, 0.03, COL_CAM_SMOKE, segments=8, axis='Y')
    make_cyl("Door_CamRing", (0.0, BLD_Y0 - 0.16, 3.10), 0.09, 0.03,
             COL_WHITE_PANEL, segments=12, axis='Y')
    make_cyl("Door_CamDome", (0.0, BLD_Y0 - 0.20, 3.10), 0.065, 0.08,
             COL_CAM_SMOKE, segments=12, axis='Y')
    # Storefront placards (Label3D anchors): hours, no-loiter,
    # CAMERAS IN OPERATION, restroom pictogram on the west pier
    make_box("Hours_Placard", (-1.55, BLD_Y0 - 0.135, 1.55),
             (0.26, 0.012, 0.36), COL_WHITE_PANEL)
    make_box("NoLoiter_Placard", (1.55, BLD_Y0 - 0.135, 1.55),
             (0.26, 0.012, 0.36), COL_WHITE_PANEL)
    make_box("CamNotice_Panel", (-4.0, BLD_Y0 - 0.135, 3.18),
             (0.55, 0.012, 0.26), COL_WHITE_PANEL)
    make_box("CamNotice_Dot", (-4.21, BLD_Y0 - 0.145, 3.18),
             (0.06, 0.012, 0.06), COL_RED_ACCENT)
    make_box("Restroom_Placard", (-7.65, BLD_Y0 - 0.135, 1.70),
             (0.34, 0.012, 0.22), COL_WHITE_PANEL)
    make_box("Restroom_Picto", (-7.65, BLD_Y0 - 0.145, 1.70),
             (0.18, 0.012, 0.12), COL_WALL_NEXCORP)


def build_interior_liner():
    """What reads through the open storefront: the corporate-lit
    sales floor. Kept shallow — floor, ceiling with lit tubes,
    back wall, the counter + register + backbar (Skip's post /
    where Claire pays), a cooler glow band. No figures (sprites)."""
    make_box("Int_Floor", (0.0, 34.0, 0.14), (17.5, 7.6, 0.08),
             COL_FLOOR_TILE)
    make_box("Int_Ceiling", (0.0, 34.0, 3.10), (17.5, 7.6, 0.08),
             COL_CEIL_TILE)
    make_box("Int_Wall_N", (0.0, 37.7, 1.66), (17.5, 0.12, 2.96), COL_CMU)
    for tag, wx in (("W", -8.6), ("E", 8.6)):
        make_box(f"Int_Wall_{tag}", (wx, 34.0, 1.66), (0.12, 7.6, 2.96),
                 COL_CMU)
    for i in range(3):
        make_box(f"Int_Tube_{i}", (-4.5 + i * 4.5, 33.0, 3.04),
                 (1.60, 0.38, 0.06), COL_TUBE_LIT)
    # The counter — east of the door, facing the pumps (forecourt
    # watch, gas_go convention: clerk sees the door AND the pumps)
    make_box("Int_Counter", (3.4, 32.4, 0.68), (3.6, 0.60, 1.00),
             COL_COUNTER_LAMINATE)
    make_box("Int_Counter_Top", (3.4, 32.4, 1.21), (3.7, 0.70, 0.06),
             COL_METAL_BLACK)
    make_box("Int_Register", (2.6, 32.5, 1.42), (0.36, 0.36, 0.32),
             COL_METAL_BLACK)
    make_box("Int_Register_Screen", (2.6, 32.30, 1.52), (0.28, 0.02, 0.14),
             COL_SCREEN_BLUE)
    # Backbar cigarette wall behind the counter — navy planogram
    make_box("Int_Backbar", (3.4, 37.55, 1.85), (3.6, 0.14, 1.90),
             COL_WALL_NEXCORP)
    for sh in range(3):
        make_box(f"Int_Backbar_Shelf_{sh}", (3.4, 37.40, 1.35 + sh * 0.50),
                 (3.30, 0.16, 0.05), COL_METAL_STEEL)
    # Cooler glow band along the west interior — the lit doors read
    # through the west window as depth
    make_box("Int_Cooler_Body", (-8.35, 34.0, 1.30), (0.30, 6.0, 2.40),
             COL_STEEL_DK)
    make_box("Int_Cooler_Glow", (-8.18, 34.0, 1.30), (0.04, 5.6, 2.10),
             COL_TUBE_LIT)
    # One gondola silhouette mid-floor (planogram-regular)
    make_box("Int_Gondola", (-2.5, 34.5, 0.90), (4.0, 0.55, 1.50),
             COL_PLASTIC_GREY)
    make_box("Int_Gondola_Cap", (-2.5, 34.5, 1.70), (4.0, 0.50, 0.10),
             COL_WALL_NEXCORP)


def build_front_walk():
    # Concrete walk strip between the lot and the storefront
    make_box("Walk", (0.0, 29.5, 0.03), (18.4, 1.4, 0.06), COL_CONCRETE)
    for i in range(5):
        make_box(f"Walk_Joint_{i}", (-7.2 + i * 3.6, 29.5, WALK_TOP + 0.002),
                 (0.03, 1.40, 0.004), (0.48, 0.46, 0.42, 1.0))
    for i, bx in enumerate([-1.9, 1.9]):
        make_cyl(f"Walk_Bollard_{i}", (bx, 29.3, 0.45), 0.07, 0.90,
                 COL_WALL_NEXCORP, segments=10)
        make_cyl(f"Walk_Bollard_Cap_{i}", (bx, 29.3, 0.92), 0.075, 0.04,
                 COL_AMBER_NEX, segments=10)
    # Ice merchandiser (west of door) + propane cage (east end) —
    # corporate exterior retail, gas_go vocabulary
    make_box("Ice_Body", (-3.6, 29.55, 0.81), (0.90, 0.75, 1.50),
             COL_WHITE_PANEL)
    make_box("Ice_Band", (-3.6, 29.16, 1.16), (0.90, 0.02, 0.36),
             COL_WALL_NEXCORP)
    make_box("Ice_Lid_Seam", (-3.6, 29.17, 0.68), (0.74, 0.012, 0.03),
             COL_PLASTIC_GREY)
    cgx, cgy = 6.9, 29.55
    for pxi, pxs in enumerate([-0.38, 0.38]):
        for pyi, pys in enumerate([-0.30, 0.30]):
            make_box(f"Propane_Post_{pxi}_{pyi}", (cgx + pxs, cgy + pys, 0.76),
                     (0.05, 0.05, 1.40), COL_METAL_STEEL)
    for ri, rz in enumerate([0.32, 0.80, 1.28]):
        make_box(f"Propane_Rail_F_{ri}", (cgx, cgy - 0.30, rz),
                 (0.80, 0.03, 0.05), COL_METAL_STEEL)
        make_box(f"Propane_Rail_B_{ri}", (cgx, cgy + 0.30, rz),
                 (0.80, 0.03, 0.05), COL_METAL_STEEL)
    make_box("Propane_Roof", (cgx, cgy, 1.50), (0.86, 0.72, 0.05),
             COL_WALL_NEXCORP)
    for t in range(3):
        make_cyl(f"Propane_Tank_{t}", (cgx - 0.24 + t * 0.24, cgy, 0.37),
                 0.10, 0.50, COL_WHITE_PANEL, segments=10)
    # Windshield-fluid pallet stack by the ice box (uniform ranks)
    for jx in range(2):
        for jy in range(2):
            make_box(f"Fluid_Jug_{jx}_{jy}",
                     (-5.0 + jx * 0.26, 29.45 + jy * 0.26, 0.25),
                     (0.22, 0.22, 0.38), (0.34, 0.42, 0.54, 1.0))


# ══════════════════════════════════════════════════════════════════
# CAR WASH — "the full automated tunnel kind" (ch1:20), rear-east.
# Mouth faces south onto the side drive, exit faces north into the
# employee lot; navy roof band, amber mouth frame, white CAR WASH
# sign panel (Label3D anchor). Dark mouths, no transparency.
# ══════════════════════════════════════════════════════════════════
def build_carwash():
    ccx = (CW_X0 + CW_X1) / 2.0
    ccy = (CW_Y0 + CW_Y1) / 2.0
    make_box("CW_Body", (ccx, ccy, 1.95), (CW_X1 - CW_X0, CW_Y1 - CW_Y0, 3.90),
             COL_CONCRETE)
    make_box("CW_RoofBand", (ccx, ccy, 4.08), (CW_X1 - CW_X0 + 0.3,
             CW_Y1 - CW_Y0 + 0.3, 0.40), COL_WALL_NEXCORP)
    make_box("CW_RoofBand_Accent", (ccx, CW_Y0 - 0.17, 3.83),
             (CW_X1 - CW_X0 + 0.3, 0.05, 0.07), COL_AMBER_NEX)
    # Entrance mouth (south) — dark inset + amber frame
    make_box("CW_Mouth_S", (ccx, CW_Y0 - 0.06, 1.55), (3.40, 0.12, 3.10),
             COL_TINT_GLASS)
    make_box("CW_Mouth_Frame_T", (ccx, CW_Y0 - 0.10, 3.22), (3.70, 0.10, 0.22),
             COL_AMBER_NEX)
    for sgn, tag in ((-1, "W"), (+1, "E")):
        make_box(f"CW_Mouth_Frame_{tag}", (ccx + sgn * 1.80, CW_Y0 - 0.10, 1.60),
                 (0.14, 0.10, 3.05), COL_AMBER_NEX)
    # Exit mouth (north, into the employee lot)
    make_box("CW_Mouth_N", (ccx, CW_Y1 + 0.06, 1.55), (3.40, 0.12, 3.10),
             COL_TINT_GLASS)
    # CAR WASH sign panel over the mouth (Label3D anchor)
    make_box("CW_SignPanel", (ccx, CW_Y0 - 0.14, 3.62), (3.60, 0.06, 0.50),
             COL_WALL_NEXCORP)
    make_box("CW_SignText", (ccx, CW_Y0 - 0.18, 3.62), (2.60, 0.02, 0.26),
             COL_WHITE_PANEL)
    # Guidance rails into the mouth + tire guide stripes
    for sgn, tag in ((-1, "W"), (+1, "E")):
        make_box(f"CW_GuideRail_{tag}", (ccx + sgn * 1.05, CW_Y0 - 2.2, 0.14),
                 (0.10, 4.0, 0.16), COL_CAM_SMOKE)
    make_box("CW_GuideStripe", (ccx, CW_Y0 - 4.5, LOT_TOP + 0.004),
             (0.14, 5.0, 0.006), COL_STRIPE_WHITE)
    # Vacuum island on the drive (truck-stop / franchise standard)
    make_box("Vac_Island", (16.0, 13.8, 0.08), (1.6, 1.0, 0.16), COL_CONCRETE)
    make_cyl("Vac_Body", (16.0, 13.8, 0.75), 0.18, 1.20, COL_WALL_NEXCORP,
             segments=10)
    make_cyl("Vac_Dome", (16.0, 13.8, 1.42), 0.16, 0.16, COL_PLASTIC_GREY,
             segments=10)
    make_tube("Vac_Hose", (16.16, 13.8, 1.10), (16.55, 14.15, 0.12), 0.035,
              COL_METAL_BLACK)
    # Air/water tower beside it
    make_cyl("Air_Post", (14.8, 13.4, 0.60), 0.05, 1.20, COL_GALV, segments=8)
    make_box("Air_Head", (14.8, 13.4, 1.32), (0.30, 0.24, 0.28),
             COL_AMBER_NEX)
    make_tube("Air_Hose", (14.9, 13.5, 1.20), (15.3, 13.9, 0.10), 0.025,
              COL_METAL_BLACK)


# ══════════════════════════════════════════════════════════════════
# REAR SCREENING + DUMPSTER — the employee lot must not read from
# the street (ch1:28): the building and tunnel masses hide it; the
# one sightline gap (x 9..11.5) gets a chain-link run with privacy
# slats. Dumpster enclosure at the rear-west corner with an EMPTY
# striped stall beside it (Vince's beat-up sedan was here and
# "drives away" — vol6_ch6_fueling_station:118; see canon-negatives).
# ══════════════════════════════════════════════════════════════════
def build_rear_and_dumpster():
    # Screening fence in the building↔car-wash gap
    for pi in range(3):
        make_cyl(f"Screen_Post_{pi}", (9.1 + pi * 1.2, 38.6, 1.25), 0.045,
                 2.50, COL_GALV, segments=8)
    for rz, tag in ((2.42, "T"), (0.28, "B")):
        make_cyl(f"Screen_Rail_{tag}", (10.3, 38.6, rz), 0.028, 2.60,
                 COL_GALV, segments=8, axis='X')
    make_box("Screen_Slats", (10.3, 38.6, 1.25), (2.40, 0.04, 2.10),
             COL_CMU_SHADE)
    # Dumpster enclosure — two CMU wing walls + the navy dumpster
    make_box("Dump_Wall_W", (-16.6, 35.0, 1.00), (0.20, 3.2, 2.00), COL_CMU_SHADE)
    make_box("Dump_Wall_N", (-15.4, 36.5, 1.00), (2.60, 0.20, 2.00), COL_CMU_SHADE)
    make_box("Dump_Body", (-15.3, 35.0, 0.80), (2.20, 1.60, 1.30),
             COL_WALL_NEXCORP)
    make_box("Dump_Lid_W", (-15.85, 35.0, 1.50), (1.05, 1.64, 0.10),
             COL_METAL_BLACK)
    make_box("Dump_Lid_E", (-14.75, 35.0, 1.54), (1.05, 1.64, 0.10),
             COL_METAL_BLACK)
    for si, sx in enumerate([-16.2, -14.4]):
        make_box(f"Dump_Skid_{si}", (sx, 35.0, 0.10), (0.24, 1.55, 0.20),
                 COL_STEEL_DK)
    # The empty stall near the dumpster (personal-car spot)
    for i in range(2):
        make_box(f"Dump_Stall_Stripe_{i}", (-13.0 + i * 2.8, 34.6,
                 LOT_TOP + 0.004), (0.08, 4.2, 0.006), COL_STRIPE_WHITE)


# ══════════════════════════════════════════════════════════════════
# SITE INFRASTRUCTURE — streetlights + utility poles on the buffer
# strip (NEVER in the road), sagging span cable, the corporate flag.
# ══════════════════════════════════════════════════════════════════
def build_site_infra():
    # Cobra-head streetlights flanking the frontage
    for si, sx in enumerate([-21.0, 21.0]):
        make_cyl(f"Street_Pole_{si}", (sx, 9.4, 3.6), 0.09, 7.2, COL_GALV,
                 segments=10)
        # Arm reaches from the buffer strip out over the shoulder —
        # the pole itself never stands in the road surface
        make_tube(f"Street_Arm_{si}", (sx, 9.4, 7.0), (sx, 7.6, 7.5), 0.045,
                  COL_GALV)
        make_box(f"Street_Head_{si}", (sx, 7.4, 7.5), (0.30, 0.85, 0.22),
                 COL_STEEL_DK)
        make_box(f"Street_Lens_{si}", (sx, 7.4, 7.38), (0.22, 0.60, 0.03),
                 COL_TUBE_LIT)
    # Utility poles + crossarms + sagging span (playbook expected
    # bayou-city vocabulary; chorded tubes, never boxes)
    for pi, px in enumerate([-27.0, 27.0]):
        make_cyl(f"Util_Pole_{pi}", (px, 10.0, 4.5), 0.13, 9.0, COL_TRUNK,
                 segments=10)
        make_box(f"Util_Crossarm_{pi}", (px, 10.0, 8.4), (1.80, 0.10, 0.10),
                 COL_TRUNK)
        for ii in range(3):
            make_cyl(f"Util_Insul_{pi}_{ii}", (px - 0.70 + ii * 0.70, 10.0,
                     8.53), 0.04, 0.10, COL_PLASTIC_GREY, segments=8)
    span = [(-27.0, 8.45), (-13.5, 7.85), (0.0, 7.65), (13.5, 7.85),
            (27.0, 8.45)]
    for si in range(len(span) - 1):
        (x0, z0), (x1, z1) = span[si], span[si + 1]
        make_tube(f"Util_Cable_{si}", (x0, 10.0, z0), (x1, 10.0, z1), 0.02,
                  COL_METAL_BLACK)
    # NexCorp corporate flag at the lot's west entry (brand beat)
    make_cyl("Flag_Pole", (-16.5, 13.8, 3.0), 0.05, 6.0, COL_WHITE_PANEL,
             segments=8)
    make_cyl("Flag_Ball", (-16.5, 13.8, 6.05), 0.08, 0.12, COL_AMBER_NEX,
             segments=8)
    make_box("Flag_Cloth", (-15.85, 13.8, 5.55), (1.25, 0.03, 0.75),
             COL_WALL_NEXCORP)
    make_box("Flag_Cloth_Band", (-15.85, 13.78, 5.55), (0.80, 0.02, 0.28),
             COL_WHITE_PANEL)


# ══════════════════════════════════════════════════════════════════
# BACKDROP — tree line + distant massing hold the horizon (species
# diversity with baked scale variety; canopy lobes are cylinders,
# limbs are tubes — never boxes for organic shapes).
# ══════════════════════════════════════════════════════════════════
def _bg_pine(prefix, x, y, s):
    make_cyl(f"{prefix}_Trunk", (x, y, 2.4 * s), 0.16 * s, 4.8 * s, COL_TRUNK)
    for ti, (tr, tz, th) in enumerate([(1.9, 5.6, 2.2), (1.4, 7.3, 2.0),
                                       (0.8, 8.8, 1.8)]):
        make_cyl(f"{prefix}_Tier_{ti}", (x, y, tz * s), tr * s, th * s,
                 COL_PINE, segments=8)


def _bg_oak(prefix, x, y, s):
    make_cyl(f"{prefix}_Trunk", (x, y, 1.3 * s), 0.24 * s, 2.6 * s, COL_TRUNK)
    for ci, (cdx, cdy, cz, cr, ch, col) in enumerate([
            (0.0, 0.0, 3.4, 2.6, 1.9, COL_OAK_A),
            (-1.1, 0.6, 4.3, 1.9, 1.6, COL_OAK_B),
            (1.2, -0.4, 4.5, 1.7, 1.5, COL_OAK_A)]):
        make_cyl(f"{prefix}_Lobe_{ci}", (x + cdx * s, y + cdy * s, cz * s),
                 cr * s, ch * s, col, segments=8)


def build_backdrop():
    pines = [(-38.0, 56.0, 1.15), (-14.0, 60.0, 0.90), (12.0, 58.0, 1.30),
             (44.0, 54.0, 1.05), (-58.0, 50.0, 1.25)]
    oaks = [(-26.0, 52.0, 1.25), (26.0, 55.0, 1.05), (58.0, 48.0, 0.90),
            (-46.0, 60.0, 1.10)]
    for i, (x, y, s) in enumerate(pines):
        _bg_pine(f"BgPine_{i}", x, y, s)
    for i, (x, y, s) in enumerate(oaks):
        _bg_oak(f"BgOak_{i}", x, y, s)
    # A pair of live oaks on the lot's own verge (species diversity
    # inside the frame, not just at the horizon)
    _bg_oak("VergeOak_0", -24.0, 24.0, 1.35)
    _bg_oak("VergeOak_1", 24.0, 30.0, 1.15)
    # Distant metal massing — reads as ag-warehouse (FM-3411) or
    # back-of-strip commercial (Gallatin); deliberately neutral
    make_box("Far_Shed_A", (40.0, 62.0, 3.0), (16.0, 10.0, 6.0),
             COL_ROOF_METAL)
    make_box("Far_Shed_A_Roof", (40.0, 62.0, 6.3), (16.6, 10.6, 0.6),
             COL_STEEL_DK)
    make_box("Far_Shed_B", (-52.0, 66.0, 2.2), (10.0, 8.0, 4.4),
             COL_CMU_SHADE)


def main():
    clear_scene()
    # Exterior discipline: ground → circulation → THEN features
    # (playbook 2026-06-14).
    build_ground()
    build_road()
    build_lot()
    build_pylon_sign()
    build_canopy()
    build_pumps()
    build_building()
    build_interior_liner()
    build_front_walk()
    build_carwash()
    build_rear_and_dumpster()
    build_site_infra()
    build_backdrop()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/nexcorp_fueling_station.glb"))
    print(f"\n[build_nexcorp_fueling_station] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
