"""VOL 5 · XI Justice §II — "Scales Already Shattered"
(vol5_ch11_justice.json L303-L515). ANNA LOGUE's design studio —
"her meticulously greige Houston high-rise office, three floors
down from a law firm" (L324): the SAME tower as Erica Campbell's
firm (build_houston_office.py), three floors lower. The scaffold's
docstring said "Emperor cameo ... drafting tables, brick wall,
exposed duct, plotter" — loft-warehouse vocabulary that belongs to
the PAINTER's converted warehouse in the Heights (ch10 L130), not
to Anna's corporate high-rise floor. Rebuilt canon-first.

OWNERSHIP ADJUDICATION — Anna Logue's workplace at her design firm
("her firm", L466), where she kerns the D'AMBROSIO'S: EMBER & ASH
campaign for Alberto (L312, L344). One building, two tenants: the
older man in the lobby "had come for somebody else, three floors
up" (L494-L502) — Mr. D. Dean's 9:15 with Erica. The HOUSTON TOWER
constants block below is therefore byte-identical with
build_houston_office.py (playbook: shared-venue blocks stay in
md5 sync).

ERA ADJUDICATION — contemporary (~2026): Illustrator layers
(L406), a .psd saved to a private cloud (L462-L466), airdrop
(L466), gifs from Ben (L386). Flat panels, no CRTs, no drafting
boards — Anna's craft is entirely on screen.

Canon dressed in (line numbers = vol5_ch11_justice.json):
  · The S doorway = the open camera doorway (Background3D preset
    "houston_design_studio": origin z=+0.5, yaw 180, fov 62 —
    the exemplar build_new_orleans_office.py arrangement).
  · The N curtain wall — same tower vocabulary as Erica's floor,
    at this room's 3.20 ceiling. NO glass slabs (playbook). The
    .tscn Key_NorthWindow light reads through it.
  · Outside, from ~nine floors up: the plaza she crosses at the
    chapter's end (L482, L494) with its planters and the street
    beyond, and neighbor towers that now rise well PAST us —
    three floors down from Erica reads as more tower above.
  · Anna's workstation, centre-north: THREE monitors "curated,
    naturally, for optimal color fidelity" (L312) —
      LEFT: the pitch deck mock-up, Slide 7 title band + body
      bars ("But what is truly real...", L336);
      CENTER: the D'Ambrosio logo stripped "to its wireframe"
      (L406) — thin light strokes on dark, carrying the small
      inscribed coordinates of the sinkhole hotspot
      (_SINKHOLE_NEXUS.md L187-188: "Anna's wireframe carries
      small inscribed coordinates that pinpoint the sinkhole's
      location");
      RIGHT (the THIRD monitor, L312): D'AMBROSIO'S: EMBER &
      ASH in bold amber on charcoal — the lockup that "felt
      less like branding and more like an accusation."
  · Her cold brew — cashew milk, locally roasted (L332) — a
    two-tone opaque glass (tan pour below, pale empty glass
    above; no alpha).
  · Her phone, face-up on the desk — it buzzes twice: Ben
    (L356), then Alberto rung through (L470-L478).
  · The anglepoise task lamp on the desk — kept because the
    .tscn fill light is NAMED Fill_Anglepoise.
  · TWO air purifiers — canon is plural: "the quiet hum of
    expensive air purifiers" (L324); "The office air hummed,
    sterile and controlled" (L414). White towers, vent rings.
  · The W feature wall: warm walnut slats + low white credenza
    with a squared book stack and one leaning framed print. The
    .tscn back light is NAMED Back_BrickGlow — brick itself is
    canon-negative here (see below), so the warm glow lands on
    wood instead of being orphaned.
  · Clean lines, negative space (L324): one colleague
    workstation (dark monitor, chair squared — Saturday, she is
    alone), one aligned swatch board, one shelf run of uniform
    spines. The floor stays mostly empty on purpose.
Canon-negatives (verified against the full scene):
  · NO brick wall, NO exposed duct — that register belongs to
    the painter's Heights warehouse (ch10 L130). Anna's floor is
    "meticulously greige" high-rise (L324).
  · NO drafting tables, NO plotter — her workflow is Illustrator
    (L406) and a saved .psd (L462); nothing analog is staged.
  · NO rainbow mood-board (scaffold's SNACK_TINTS pin wall
    dropped) — her register is greige + one amber accent.
  · NO Corporate Idols piece on display: D'AMB-IDOL-01.psd went
    to the private cloud "her firm did not know existed"
    (L462-L466). Rendering it on a wall would break the secret.
  · NO croissant / pastry / flat whites — those are at the
    coffee shop with Ben (L482).
  · NO Mr. D. Dean — he is in the lobby, and he did not come
    for her (L494-L498).
  · NO ceiling stains, NO wall clock (unstaged; the chapter
    keeps its own time: 10 AM at L458).

Name dependencies checked: Background3D.gd references only scene +
GLB paths; the .tscn LiminalProximityController location_json is
empty; no script reads mesh names from this GLB. The .tscn light
NAMES are honored by geometry: Key_NorthWindow -> the N curtain
wall opening, Fill_Anglepoise -> the desk task lamp,
Back_BrickGlow -> the warm walnut slat wall (brick canon-negative,
documented above).

Playbook compliance: shell footprint KEPT from the scaffold
(10 x 7 x 3.20). Windows are mullion-and-frame openings — zero
glass slabs, zero alpha. Cylinders for everything round at eye
level (purifiers, lamp, cold brew, chair column). Deterministic —
no RNG anywhere.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.safety import make_smoke_detector, make_hvac_vent

# Shell footprint — KEPT from the scaffold; Background3D preset
# ("houston_design_studio": origin (0, 2.30, +0.5), yaw 180,
# fov 62) and the .tscn lights are tuned to it.
ROOM_W = 10.0; ROOM_D = 7.0; CEIL = 3.20

# ── HOUSTON TOWER — KEEP IN SYNC ─────────────────────────────────
# One building, two tenants: Anna's studio is "three floors down
# from a law firm" in the same high-rise (vol5_ch11_justice.json
# L324, L502). This block is byte-identical in
# build_houston_office.py and build_houston_design_studio.py —
# verify with md5 before editing either copy.
HOUSTON_MULLION    = (0.62, 0.64, 0.66, 1.0)   # anodized curtain wall
HOUSTON_MULLION_DK = (0.36, 0.38, 0.40, 1.0)   # spandrel / channels
HOUSTON_CHROME     = (0.74, 0.76, 0.78, 1.0)   # interior chrome accents
HOUSTON_TOWER_A    = (0.42, 0.48, 0.54, 1.0)   # nearest glass tower
HOUSTON_TOWER_B    = (0.54, 0.58, 0.62, 1.0)   # mid-distance tower
HOUSTON_TOWER_C    = (0.66, 0.68, 0.70, 1.0)   # haze-distance slab
HOUSTON_TOWER_LIT  = (0.96, 0.84, 0.52, 1.0)   # one lit office window
HOUSTON_ASPHALT    = (0.30, 0.29, 0.28, 1.0)   # freeway / plaza deck
HOUSTON_LANE       = (0.72, 0.70, 0.62, 1.0)   # lane striping
HOUSTON_HAWK       = (0.16, 0.14, 0.12, 1.0)   # the bird on the thermal
CURTAIN_PITCH      = 1.30                       # mullion spacing (m)
# ── end HOUSTON TOWER block ──────────────────────────────────────

# Studio-local palette — meticulously greige (L324), one amber
# accent (the EMBER & ASH lockup, L312).
PAL_WALL = {"wall": (0.80, 0.77, 0.72, 1.0),
            "baseboard": (0.44, 0.42, 0.38, 1.0)}
COL_CARPET      = (0.66, 0.63, 0.58, 1.0)   # pale greige carpet tile
COL_CARPET_SEAM = (0.60, 0.57, 0.52, 1.0)   # low-contrast seams
COL_CEIL        = (0.90, 0.89, 0.86, 1.0)   # smooth gypsum, no grid
COL_DESK_WHITE  = (0.90, 0.89, 0.86, 1.0)   # her worktop
COL_DESK_LEG    = (0.82, 0.81, 0.78, 1.0)
COL_WALNUT      = (0.38, 0.26, 0.16, 1.0)   # W slat wall
COL_WALNUT_DK   = (0.26, 0.17, 0.10, 1.0)
COL_MONITOR     = (0.08, 0.09, 0.10, 1.0)   # bezels
COL_SCREEN_DARK = (0.13, 0.13, 0.15, 1.0)   # wireframe canvas
COL_SCREEN_OFF  = (0.10, 0.10, 0.11, 1.0)   # colleague's dark monitor
COL_WIREFRAME   = (0.72, 0.74, 0.76, 1.0)   # stripped-logo strokes (L406)
COL_DECK_BG     = (0.88, 0.87, 0.84, 1.0)   # pitch deck slide (L336)
COL_DECK_TEXT   = (0.46, 0.45, 0.44, 1.0)
COL_EMBER_BG    = (0.14, 0.12, 0.11, 1.0)   # third-monitor charcoal
COL_EMBER_AMBER = (0.88, 0.58, 0.22, 1.0)   # EMBER & ASH bold (L312)
COL_CHAIR       = (0.20, 0.20, 0.22, 1.0)
COL_PHONE       = (0.12, 0.12, 0.13, 1.0)
COL_PHONE_SCRN  = (0.24, 0.26, 0.30, 1.0)
COL_BREW        = (0.58, 0.44, 0.30, 1.0)   # cold brew + cashew (L332)
COL_BREW_GLASS  = (0.80, 0.82, 0.80, 1.0)   # empty glass above the pour
COL_PURIFIER    = (0.92, 0.92, 0.90, 1.0)   # the expensive hum (L324)
COL_PURIFIER_V  = (0.40, 0.41, 0.42, 1.0)
COL_BOOK_TINTS  = [(0.56, 0.54, 0.50, 1.0), (0.42, 0.42, 0.44, 1.0),
                   (0.68, 0.64, 0.56, 1.0), (0.34, 0.34, 0.36, 1.0)]
COL_SWATCHES    = [(0.82, 0.80, 0.76, 1.0), (0.70, 0.68, 0.64, 1.0),
                   (0.56, 0.54, 0.51, 1.0), (0.42, 0.41, 0.39, 1.0),
                   (0.30, 0.29, 0.28, 1.0), (0.88, 0.58, 0.22, 1.0)]

DESK_CX, DESK_CY = 0.60, 4.40   # Anna's workstation
DESK_TOP_Z = 0.74


def build_shell():
    """Carpet + S/E/W walls + smooth ceiling. N is the curtain
    wall. S has the open camera doorway."""
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_CARPET, "seam": COL_CARPET_SEAM})
    # S wall — doorway gap x in [-1.0, +1.0]; the camera sits in it.
    make_wall("Wall_S_W", (-3.10, 0.0, 0), length=4.2, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+3.10, 0.0, 0), length=4.2, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=+1)
    for psgn in (-1, +1):
        make_box(f"Door_S_Post_{psgn:+d}", (psgn * 1.05, 0.0, 1.10),
                 (0.10, 0.22, 2.20), HOUSTON_MULLION_DK)
    make_box("Door_S_Lintel", (0.0, 0.0, 2.24), (2.30, 0.20, 0.08),
             HOUSTON_MULLION_DK)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.74), (2.10, 0.20, 0.92),
             PAL_WALL["wall"])
    # E wall solid; W wall carries the walnut slats (build_west_wall).
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    # Smooth gypsum ceiling — no drop grid, no stains. Meticulous.
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_CEIL},
                 with_grid=False, with_stains=False)


def build_curtain_wall():
    """N curtain wall — same tower vocabulary as Erica's floor
    (HOUSTON TOWER block), at this room's 3.20 ceiling. NO glass.
    The .tscn Key_NorthWindow light reads through it."""
    wy = ROOM_D
    make_box("Curtain_Sill", (0.0, wy, 0.06), (ROOM_W + 0.4, 0.24, 0.12),
             HOUSTON_MULLION_DK)
    make_box("Curtain_Header", (0.0, wy, CEIL - 0.06),
             (ROOM_W + 0.4, 0.24, 0.12), HOUSTON_MULLION_DK)
    make_box("Curtain_Rail", (0.0, wy, 2.42), (ROOM_W + 0.4, 0.14, 0.06),
             HOUSTON_MULLION)
    n_mull = int(round((ROOM_W + 0.4) / CURTAIN_PITCH))     # 8 bays
    for mi in range(n_mull + 1):
        mx = -(ROOM_W + 0.4) / 2.0 + mi * (ROOM_W + 0.4) / n_mull
        make_box(f"Curtain_Mull_{mi}", (mx, wy, CEIL / 2.0),
                 (0.07, 0.18, CEIL), HOUSTON_MULLION)


def build_houston_outside():
    """The view from ~nine floors — three below Erica (L324). The
    neighbor towers rise well past us; the plaza she crosses at
    the chapter's end (L482, L494) sits far below with its
    planters and the street beyond."""
    # Near tower — from this floor it keeps going up.
    make_box("Tower_A", (-6.0, 19.0, -6.0), (6.0, 6.0, 54.0),
             HOUSTON_TOWER_A)
    for si in range(4):
        make_box(f"Tower_A_Strip_{si}", (-8.4 + si * 1.6, 15.95, -6.0),
                 (0.18, 0.14, 54.0), HOUSTON_MULLION_DK)
    make_box("Tower_B", (5.5, 27.0, -9.0), (6.5, 6.0, 50.0),
             HOUSTON_TOWER_B)
    make_box("Tower_C", (6.0, 41.0, -4.0), (16.0, 6.0, 62.0),
             HOUSTON_TOWER_C)
    # The plaza, ~nine floors down (L494) — deck, planters, street.
    make_box("Plaza_Deck", (0.0, 13.5, -27.0), (30.0, 7.0, 0.30),
             HOUSTON_ASPHALT)
    for pi in range(3):
        px = -7.0 + pi * 7.0
        make_box(f"Plaza_Planter_{pi}", (px, 12.5, -26.62),
                 (1.4, 1.4, 0.45), HOUSTON_MULLION_DK)
        make_box(f"Plaza_Planter_{pi}_Green", (px, 12.5, -26.28),
                 (1.1, 1.1, 0.25), (0.36, 0.44, 0.30, 1.0))
    make_box("Street_Deck", (0.0, 19.5, -27.4), (34.0, 4.0, 0.20),
             HOUSTON_ASPHALT)
    make_box("Street_Stripe", (0.0, 19.5, -27.28), (26.0, 0.10, 0.02),
             HOUSTON_LANE)


def build_workstation():
    """Anna's desk (L312-L344): three color-curated monitors —
    pitch deck / stripped wireframe / the EMBER & ASH lockup —
    keyboard, mouse, her phone, the cold brew, the anglepoise."""
    tz = DESK_TOP_Z
    make_box("Desk_Top", (DESK_CX, DESK_CY, tz - 0.02),
             (2.30, 0.85, 0.04), COL_DESK_WHITE)
    for lsgn in (-1, +1):
        make_box(f"Desk_Panel_{lsgn:+d}", (DESK_CX + lsgn * 1.08, DESK_CY,
                 0.36), (0.045, 0.75, 0.72), COL_DESK_LEG)
    make_box("Desk_CableTray", (DESK_CX, DESK_CY + 0.36, 0.58),
             (1.80, 0.08, 0.06), COL_DESK_LEG)
    # LEFT — the pitch deck mock-up, Slide 7 (L332-L336).
    make_box("Mon_Deck_Panel", (-0.28, DESK_CY + 0.18, 1.10),
             (0.58, 0.030, 0.36), COL_MONITOR)
    make_box("Mon_Deck_Screen", (-0.28, DESK_CY + 0.163, 1.10),
             (0.52, 0.002, 0.31), COL_DECK_BG)
    make_box("Mon_Deck_TitleBar", (-0.28, DESK_CY + 0.161, 1.21),
             (0.40, 0.001, 0.05), COL_DECK_TEXT)
    for li in range(3):
        make_box(f"Mon_Deck_Line_{li}", (-0.30, DESK_CY + 0.161,
                 1.12 - li * 0.045), (0.34, 0.001, 0.014), COL_DECK_TEXT)
    make_box("Mon_Deck_Stand", (-0.28, DESK_CY + 0.20, 0.84),
             (0.05, 0.05, 0.16), COL_DESK_LEG)
    # CENTER — the logo stripped to wireframe (L406), carrying the
    # inscribed sinkhole coordinates (_SINKHOLE_NEXUS.md L187-188).
    make_box("Mon_Wire_Panel", (0.60, DESK_CY + 0.18, 1.12),
             (0.62, 0.030, 0.38), COL_MONITOR)
    make_box("Mon_Wire_Screen", (0.60, DESK_CY + 0.163, 1.12),
             (0.56, 0.002, 0.33), COL_SCREEN_DARK)
    make_box("Mon_Wire_StrokeH1", (0.60, DESK_CY + 0.161, 1.20),
             (0.34, 0.001, 0.008), COL_WIREFRAME)
    make_box("Mon_Wire_StrokeH2", (0.60, DESK_CY + 0.161, 1.06),
             (0.28, 0.001, 0.008), COL_WIREFRAME)
    for vi, vx in enumerate([0.46, 0.60, 0.74]):
        make_box(f"Mon_Wire_StrokeV_{vi}", (vx, DESK_CY + 0.161, 1.13),
                 (0.008, 0.001, 0.13), COL_WIREFRAME)
    # The small inscribed coordinates, lower-left of the canvas.
    make_box("Mon_Wire_Coords", (0.42, DESK_CY + 0.161, 0.985),
             (0.14, 0.001, 0.010), COL_WIREFRAME)
    make_box("Mon_Wire_Stand", (0.60, DESK_CY + 0.20, 0.84),
             (0.05, 0.05, 0.18), COL_DESK_LEG)
    # RIGHT — the THIRD monitor (L312): D'AMBROSIO'S: EMBER & ASH,
    # bold amber on charcoal. Branding as accusation.
    make_box("Mon_Ember_Panel", (1.48, DESK_CY + 0.18, 1.10),
             (0.58, 0.030, 0.36), COL_MONITOR)
    make_box("Mon_Ember_Screen", (1.48, DESK_CY + 0.163, 1.10),
             (0.52, 0.002, 0.31), COL_EMBER_BG)
    make_box("Mon_Ember_Lockup", (1.48, DESK_CY + 0.161, 1.13),
             (0.42, 0.001, 0.055), COL_EMBER_AMBER)
    make_box("Mon_Ember_Subline", (1.48, DESK_CY + 0.161, 1.06),
             (0.28, 0.001, 0.018), COL_EMBER_AMBER)
    make_box("Mon_Ember_Flame", (1.30, DESK_CY + 0.161, 1.205),
             (0.030, 0.001, 0.045), COL_EMBER_AMBER)
    make_box("Mon_Ember_Stand", (1.48, DESK_CY + 0.20, 0.84),
             (0.05, 0.05, 0.16), COL_DESK_LEG)
    # Keyboard + mouse, squared to the center monitor.
    make_box("Keyboard", (0.60, DESK_CY - 0.12, tz + 0.011),
             (0.42, 0.14, 0.022), COL_CHAIR)
    make_box("Mouse", (0.94, DESK_CY - 0.12, tz + 0.014),
             (0.058, 0.10, 0.028), COL_CHAIR)
    # Her phone, face-up — Ben's gifs, then Alberto rung through
    # (L356, L470-L478).
    make_box("Phone", (1.24, DESK_CY - 0.24, tz + 0.007),
             (0.072, 0.150, 0.014), COL_PHONE)
    make_box("Phone_Screen", (1.24, DESK_CY - 0.24, tz + 0.0145),
             (0.062, 0.130, 0.001), COL_PHONE_SCRN)
    # The cold brew (L332) — opaque two-tone pour, no alpha.
    make_cyl("ColdBrew_Pour", (-0.10, DESK_CY - 0.24, tz + 0.05),
             0.034, 0.10, COL_BREW, segments=10)
    make_cyl("ColdBrew_Glass", (-0.10, DESK_CY - 0.24, tz + 0.125),
             0.034, 0.05, COL_BREW_GLASS, segments=10)
    # The anglepoise — the .tscn fill light is NAMED for it.
    ax = -0.88
    make_cyl("Anglepoise_Base", (ax, DESK_CY + 0.20, tz + 0.015),
             0.062, 0.03, COL_CHAIR, segments=10)
    make_cyl("Anglepoise_ArmLo", (ax, DESK_CY + 0.20, tz + 0.20),
             0.011, 0.34, COL_CHAIR, segments=8)
    make_cyl("Anglepoise_ArmHi", (ax + 0.16, DESK_CY + 0.20, tz + 0.37),
             0.010, 0.32, COL_CHAIR, axis='X', segments=8)
    make_cyl("Anglepoise_Head", (ax + 0.34, DESK_CY + 0.20, tz + 0.345),
             0.052, 0.09, COL_CHAIR, segments=10)
    # Her chair — minimal, squared.
    cy = DESK_CY - 0.75
    make_box("Chair_Seat", (DESK_CX, cy, 0.48), (0.48, 0.45, 0.06),
             COL_CHAIR)
    make_box("Chair_Back", (DESK_CX, cy + 0.235, 0.94), (0.46, 0.05, 0.66),
             COL_CHAIR)
    make_cyl("Chair_Column", (DESK_CX, cy, 0.26), 0.030, 0.36,
             HOUSTON_CHROME, segments=8)
    make_cyl("Chair_Base", (DESK_CX, cy, 0.03), 0.25, 0.045,
             HOUSTON_CHROME, segments=10)


def build_colleague_desk():
    """One colleague workstation, E side — monitor DARK, chair
    squared under: it is Saturday and the firm's floor is hers
    alone (L308, L466)."""
    wx, wy = 3.60, 2.20
    make_box("Coll_Desk_Top", (wx, wy, 0.72), (1.40, 0.70, 0.035),
             COL_DESK_WHITE)
    for lsgn in (-1, +1):
        make_box(f"Coll_Desk_Panel_{lsgn:+d}", (wx + lsgn * 0.64, wy, 0.35),
                 (0.04, 0.62, 0.70), COL_DESK_LEG)
    make_box("Coll_Monitor", (wx, wy + 0.16, 1.04), (0.52, 0.028, 0.32),
             COL_MONITOR)
    make_box("Coll_Monitor_Screen", (wx, wy + 0.144, 1.04),
             (0.46, 0.002, 0.27), COL_SCREEN_OFF)
    make_box("Coll_Monitor_Stand", (wx, wy + 0.18, 0.80),
             (0.05, 0.05, 0.13), COL_DESK_LEG)
    make_box("Coll_Chair_Seat", (wx, wy - 0.42, 0.47), (0.44, 0.42, 0.055),
             COL_CHAIR)
    make_box("Coll_Chair_Back", (wx, wy - 0.62, 0.90), (0.42, 0.05, 0.58),
             COL_CHAIR)
    make_cyl("Coll_Chair_Column", (wx, wy - 0.42, 0.26), 0.028, 0.35,
             HOUSTON_CHROME, segments=8)
    make_cyl("Coll_Chair_Base", (wx, wy - 0.42, 0.03), 0.23, 0.04,
             HOUSTON_CHROME, segments=10)


def build_west_wall():
    """The warm wall: walnut slats (the .tscn Back_BrickGlow's
    landing surface — brick is canon-negative, L324) + low white
    credenza with a squared book stack and one leaning print."""
    wx = -ROOM_W / 2.0 + 0.13
    for si in range(16):
        sy = 0.55 + si * 0.40
        make_box(f"Slat_{si}", (wx, sy, CEIL / 2.0),
                 (0.045, 0.085, CEIL - 0.10), COL_WALNUT)
    make_box("Slat_Backer", (wx - 0.035, ROOM_D / 2.0, CEIL / 2.0),
             (0.02, ROOM_D - 0.6, CEIL - 0.10), COL_WALNUT_DK)
    # Credenza — clean white, chrome feet.
    cx2 = -4.45
    make_box("Credenza_Body", (cx2, 3.50, 0.42), (0.45, 2.00, 0.56),
             COL_DESK_WHITE)
    make_box("Credenza_Reveal", (cx2 - 0.226, 3.50, 0.42),
             (0.002, 1.90, 0.015), COL_DESK_LEG)
    for fi, fy in enumerate([2.65, 4.35]):
        make_cyl(f"Credenza_Foot_{fi}", (cx2, fy, 0.07), 0.018, 0.14,
                 HOUSTON_CHROME, segments=8)
    # Squared book stack — four muted spines, flush.
    for bi in range(4):
        make_box(f"Credenza_Book_{bi}", (cx2, 3.10, 0.725 + bi * 0.032),
                 (0.24 - bi * 0.01, 0.32 - bi * 0.02, 0.030),
                 COL_BOOK_TINTS[bi])
    # One framed print, leaning against the slats: white frame,
    # greige field, single amber stroke. Minimal, not Idols.
    make_box("Print_Frame", (cx2 + 0.05, 4.20, 1.08), (0.030, 0.62, 0.80),
             COL_DESK_WHITE)
    make_box("Print_Field", (cx2 + 0.067, 4.20, 1.08), (0.002, 0.54, 0.72),
             (0.74, 0.72, 0.68, 1.0))
    make_box("Print_Stroke", (cx2 + 0.069, 4.20, 1.02), (0.001, 0.38, 0.05),
             COL_EMBER_AMBER)


def build_east_wall():
    """E wall: one shelf run of uniform spines + the aligned
    swatch board — a 3x2 greige scale with one amber square.
    Clean lines, negative space (L324)."""
    ex = ROOM_W / 2.0 - 0.14
    make_box("Shelf_E", (ex - 0.10, 4.90, 1.45), (0.26, 1.80, 0.032),
             COL_DESK_WHITE)
    for bri, bry in enumerate([4.20, 5.60]):
        make_box(f"Shelf_E_Bracket_{bri}", (ex - 0.03, bry, 1.37),
                 (0.03, 0.03, 0.13), HOUSTON_MULLION_DK)
    for bi in range(9):
        by = 4.18 + bi * 0.165
        make_box(f"Shelf_E_Book_{bi}", (ex - 0.11, by, 1.61),
                 (0.20, 0.052, 0.29), COL_BOOK_TINTS[bi % 4])
    # Swatch board — aluminum frame, six aligned squares.
    make_box("Swatch_Frame", (ex - 0.005, 2.30, 1.70), (0.020, 1.30, 0.90),
             HOUSTON_MULLION)
    make_box("Swatch_Field", (ex - 0.018, 2.30, 1.70), (0.006, 1.22, 0.82),
             COL_DESK_WHITE)
    for si2 in range(6):
        row = si2 // 3
        col_i = si2 % 3
        make_box(f"Swatch_{si2}",
                 (ex - 0.024, 1.92 + col_i * 0.38, 1.88 - row * 0.36),
                 (0.002, 0.30, 0.28), COL_SWATCHES[si2])


def build_air_purifiers():
    """TWO of them — canon is plural (L324); their hum is the
    room's soundtrack (L414). White towers, dark vent rings,
    one status LED each."""
    for pi, (px, py) in enumerate([(2.30, 5.95), (-3.30, 1.05)]):
        make_cyl(f"Purifier_{pi}_Body", (px, py, 0.33), 0.155, 0.66,
                 COL_PURIFIER, segments=12)
        make_cyl(f"Purifier_{pi}_Vent", (px, py, 0.52), 0.157, 0.10,
                 COL_PURIFIER_V, segments=12)
        make_cyl(f"Purifier_{pi}_Top", (px, py, 0.675), 0.145, 0.03,
                 COL_PURIFIER_V, segments=12)
        make_box(f"Purifier_{pi}_LED", (px, py - 0.152, 0.62),
                 (0.014, 0.006, 0.014), (0.55, 0.80, 0.62, 1.0))


def build_ceiling_infra():
    """Two slim linear pendants (expensive-minimal register — no
    fluorescent troffers here), HVAC ('The office air hummed,
    sterile and controlled', L414), smoke detector."""
    for pi, py in enumerate([3.10, 5.30]):
        for di, dx in enumerate([-0.70, 1.90]):
            make_cyl(f"Pendant_{pi}_Drop_{di}", (dx, py, CEIL - 0.20),
                     0.006, 0.40, COL_CHAIR, segments=6)
        make_box(f"Pendant_{pi}_Bar", (0.60, py, CEIL - 0.42),
                 (3.00, 0.07, 0.045), COL_CHAIR)
        make_box(f"Pendant_{pi}_Diffuser", (0.60, py, CEIL - 0.445),
                 (2.90, 0.045, 0.008), (0.96, 0.94, 0.88, 1.0))
    make_hvac_vent("HVAC_A", (-2.4, 5.9, CEIL), width=1.00, depth=0.50)
    make_hvac_vent("HVAC_B", (3.2, 4.0, CEIL), width=0.80, depth=0.45)
    make_smoke_detector("Smoke", (0.0, 1.8, CEIL))


def main():
    clear_scene()
    build_shell()
    build_curtain_wall()
    build_houston_outside()
    build_workstation()
    build_colleague_desk()
    build_west_wall()
    build_east_wall()
    build_air_purifiers()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/houston_design_studio.glb"))
    print(f"\n[build_houston_design_studio] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
