"""VOL 5 · X The Wheel of Fortune — "Closing Arguments Against
Chaos" (vol5_ch10_wheel.json) + XI Justice §I — "Scales Already
Shattered" (vol5_ch11_justice.json L10-L301). ERICA CAMPBELL's
private partner office at her corporate law firm, downtown Houston
high-rise, twelve stories up (ch10 L90: "the freeway ... twelve
stories below"). The scaffold's docstring said "Emperor chapter /
generic corporate office: cubicle row" — WRONG on both counts:
both chapters that bind 3d:houston_office are the Erica chapters,
and the room is nobody's cubicle farm. "Her office was a temple to
control. Glass walls. Chrome accents. Files indexed with obsessive
precision" (ch10 L78, L82).

OWNERSHIP ADJUDICATION — this is ERICA's office, not Alberto's.
Alberto only ever phones in (ch10 L230 "The caller ID glowed:
ALBERTO D."); his Houston venture (D'Ambrosio's: Houston / Ember &
Ash branding) is Anna's client work three floors DOWN in the same
tower (see build_houston_design_studio.py). Ch11 §I confirms the
same room the next morning: Marcus's two coffees on the desk
(L130, L161), the SECOND monitor with the PetroTex settlement
still open (L228), the framed photo as "the only personal item in
the office" (L228), the door + "Not in this room. The next one"
(L271) — hence the interior glass partition and the anteroom.

ERA ADJUDICATION — contemporary (~2026), NOT late-90s CRTs: the
comb "she had not, in twenty-three years, replaced" dates 2003+23
(ch10 L46); the painter quit JPL in 2017 (L130); the teak desk was
bought in 2014 (L158); digital files are "backed up nightly to two
separate clouds" (L82). Flat panels, cell phone, modern VOIP desk
set.

Canon dressed in (line numbers = the scene JSONs):
  · The S doorway = the office door Marcus knocked on and pushed
    open (ch11 L130) — chrome-framed glass-office door rendered
    OPEN flat against the S wall (frame outline only, no glass);
    the Background3D camera (preset: origin z=+1.0, yaw 180,
    fov 64) sits in the opening, exactly the exemplar
    build_new_orleans_office.py arrangement.
  · The N wall = "the glass wall of her office" (ch10 L74, L82,
    L453, L489; ch11 L280): full-width floor-to-ceiling curtain
    wall — anodized mullions + sill + transom rail, NO glass
    slabs (playbook: windows are real openings). Justifies the
    .tscn Fill_Window light.
  · Houston outside, twelve stories down (ch10 L90): tower faces
    on three depth tiers, a mid-rise rooftop with its mech unit
    BELOW our sightline (sells the height), the freeway ribbon
    doing "its slow desperate ballet" far below with lane stripes
    and sparse cars, the hawk on its thermal (ch10 L90, ch11
    L280), and — on the near tower's face — the single lit office
    window she watched at dusk (ch10 L489).
  · The teak desk (ch10 L158: custom, 2014, "not ... a single
    visible imperfection"): twin 3-drawer pedestals — "the third
    drawer of her desk" holds the eyedrops, charger and her
    mother's 2003 comb (ch10 L46) — chrome pulls, modesty panel.
  · Desk still life: TWO monitors (ch11 L228 — the draft on one,
    Newsom v. PetroTex boilerplate open on the second; the denied
    motion "continued to be denied" on-screen, ch10 L457), the
    desk phone whose caller-ID display glowed ALBERTO D. (ch10
    L230), her cell — the painter saved under J (ch10 L473) —
    face-up beside it, the pen she set down (ch11 L200), a legal
    pad, Marcus's two coffees (ch11 L161), the chrome desk lamp
    whose light "made small reflections in the chrome and the
    glass and the smooth teak" (ch10 L509), and the small framed
    photograph — her mother, sun hat, Galveston 1996 — the ONLY
    personal item (ch11 L228), on the desk corner.
  · Her ergonomic chair WITH armrests — "She gripped the
    armrests" (ch10 L54) — high mesh back, chrome column,
    five-star base. Two chrome visitor chairs squared to the
    desk (Mr. D. Dean comes up at nine-fifteen, ch11 L251).
  · The file wall, E: "Files indexed with obsessive precision,
    paper and digital" (ch10 L82) — lateral file credenza +
    two shelves of uniform, flush-aligned binders. On the
    credenza, the Fortress Menu file rack (_UNLOCK_WEB.md L616:
    slate / red / gold + file 3, Alberto's log, manila), plus
    the sinkhole hotspot: a FIFTH file "no one has indexed:
    'CASE PREDECESSOR' (Settlement Grey)" (_SINKHOLE_NEXUS.md
    L185-187) — the grey folder is the only one without an
    index tab.
  · The interior glass partition, W ("Glass walls", plural, ch10
    L82): chrome posts + channels, no glass, closed chrome-
    framed door — and beyond it Marcus's anteroom ("Stay in the
    office. Not in this room. The next one." ch11 L271): his
    desk, single monitor, chair, printer, and the firm's one
    floor plant (kept OUT of her room — see canon-negatives).
Canon-negatives (verified against both full scenes):
  · NO cubicle row, NO chest-high partitions, NO water cooler —
    scaffold vocabulary from a bullpen; this is a partner's
    glass-walled office ("temple to control", ch10 L78).
  · NO personal items in her room beyond the one photo (ch11
    L228 is explicit: "the only personal item in the office").
    The plant lives in the anteroom.
  · NO wall clock (scaffold's frozen 2:15 removed — neither
    chapter stages one; ch10's dusk and ch11's 8:47 AM would
    contradict any frozen hand anyway).
  · NO wall art / diplomas — the walls hold files and glass.
  · NO ceiling water stains (with_stains=False) — nothing in
    this room is allowed to be imperfect except her.
  · NO security camera dome / Muzak speaker in a partner
    office; scaffold imports dropped.
  · NO CRTs (era adjudication above).
  · Mrs. Romero, Douglas Forte, the recruitment brochure, the
    courthouse steps (ch10 L170-L206) are memory, not set
    dressing — nothing staged.

Name dependencies checked: Background3D.gd only references the
scene + GLB paths; both .tscn LiminalProximityController
location_json fields are empty; no script reads mesh names from
this GLB. NOTE for the caller: TarotGauntletGame.gd L2411 still
maps the gauntlet fallback "ember_ash_office" to houston_office
.tscn even though ember_ash_office.tscn exists — stale mapping,
not touchable from this task.

Playbook compliance: shell footprint KEPT from the scaffold
(10 x 7 x 2.80 — the Background3D preset and .tscn lights are
tuned to it). All "glass" is mullion-and-frame openings — zero
glass slabs, zero alpha. Cylinders/spheres for everything round
at eye level (lamp, cups, chair bases, plant, folder rack posts).
Deterministic — no RNG anywhere. The HOUSTON TOWER block below is
byte-identical with build_houston_design_studio.py (one building,
two tenants — ch11 L324/L502); verify with md5 before editing.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.decor import make_floor_plant
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture, make_sprinkler)

# Shell footprint — KEPT from the scaffold; Background3D preset
# ("houston_office": origin (0, 2.30, +1.0), yaw 180, fov 64) and
# the .tscn lights (Key_Fluor / Fill_Window / Back_Corp) are tuned
# to it.
ROOM_W = 10.0; ROOM_D = 7.0; CEIL = 2.80

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

# Office-local palette — the temple to control (ch10 L78-L82).
# Cool precision inside; the teak is the room's one warm note.
PAL_WALL = {"wall": (0.88, 0.88, 0.86, 1.0),
            "baseboard": (0.30, 0.30, 0.30, 1.0)}
COL_CARPET      = (0.30, 0.29, 0.31, 1.0)   # charcoal carpet tile
COL_CARPET_SEAM = (0.26, 0.25, 0.27, 1.0)   # low-contrast tile seams
COL_TEAK        = (0.50, 0.34, 0.19, 1.0)   # the 2014 desk (ch10 L158)
COL_TEAK_DK     = (0.34, 0.22, 0.12, 1.0)
COL_MESH_CHAIR  = (0.16, 0.16, 0.18, 1.0)   # her ergonomic chair
COL_VISITOR     = (0.24, 0.25, 0.28, 1.0)   # client chair pads
COL_MONITOR     = (0.09, 0.10, 0.12, 1.0)   # flat-panel bezels
COL_SCREEN_DOC  = (0.86, 0.87, 0.84, 1.0)   # open document white
COL_SCREEN_LN   = (0.42, 0.44, 0.46, 1.0)   # document text lines
COL_SCREEN_DENY = (0.20, 0.22, 0.26, 1.0)   # the denied-motion subject bar
COL_PHONE_BODY  = (0.15, 0.15, 0.16, 1.0)
COL_PHONE_LCD   = (0.58, 0.72, 0.62, 1.0)   # ALBERTO D. glow (ch10 L230)
COL_CELL        = (0.12, 0.12, 0.13, 1.0)
COL_CELL_SCREEN = (0.22, 0.24, 0.28, 1.0)
COL_LEGAL_PAD   = (0.92, 0.86, 0.44, 1.0)
COL_INK         = (0.15, 0.13, 0.12, 1.0)
COL_CUP_PAPER   = (0.90, 0.87, 0.80, 1.0)   # Marcus's coffees (ch11 L161)
COL_CUP_LID     = (0.86, 0.85, 0.82, 1.0)
COL_FRAME_DK    = (0.20, 0.18, 0.16, 1.0)   # the photo frame (ch11 L228)
COL_PHOTO_WARM  = (0.84, 0.74, 0.56, 1.0)   # Galveston 1996 sun
COL_CAB_BODY    = (0.44, 0.45, 0.47, 1.0)   # lateral file steel
COL_CAB_FACE    = (0.52, 0.53, 0.55, 1.0)
COL_BINDER_A    = (0.34, 0.38, 0.44, 1.0)   # slate run
COL_BINDER_B    = (0.24, 0.25, 0.28, 1.0)   # charcoal run
COL_FILE_SLATE  = (0.36, 0.40, 0.46, 1.0)   # Fortress Menu files
COL_FILE_RED    = (0.62, 0.20, 0.16, 1.0)   # (_UNLOCK_WEB.md L616)
COL_FILE_GOLD   = (0.78, 0.62, 0.28, 1.0)
COL_FILE_GREY   = (0.55, 0.55, 0.54, 1.0)   # CASE PREDECESSOR, unindexed
COL_TAB_WHITE   = (0.94, 0.94, 0.92, 1.0)
COL_PRINTER     = (0.82, 0.82, 0.80, 1.0)

PART_X = -1.80                # interior glass partition plane
DESK_CX, DESK_CY = 1.10, 4.55  # the teak desk
DESK_TOP_Z = 0.74


def build_shell():
    """Carpet + S/E/W walls + ceiling. N is the curtain wall
    (build_curtain_wall). S has the open camera doorway."""
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
                 (0.10, 0.22, 2.20), HOUSTON_CHROME)
    make_box("Door_S_Lintel", (0.0, 0.0, 2.24), (2.30, 0.20, 0.08),
             HOUSTON_CHROME)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.54), (2.10, 0.20, 0.52),
             PAL_WALL["wall"])
    # The office door Marcus pushed open (ch11 L130) — chrome-framed
    # glass-office leaf, OPEN flat against the interior S face.
    # Frame outline only; the "glass" is the opening.
    dz = 1.02
    make_box("Door_S_Leaf_StileW", (1.09, 0.16, dz), (0.045, 0.045, 2.04),
             HOUSTON_CHROME)
    make_box("Door_S_Leaf_StileE", (1.93, 0.16, dz), (0.045, 0.045, 2.04),
             HOUSTON_CHROME)
    make_box("Door_S_Leaf_RailT", (1.51, 0.16, 1.99), (0.80, 0.045, 0.09),
             HOUSTON_CHROME)
    make_box("Door_S_Leaf_RailB", (1.51, 0.16, 0.06), (0.80, 0.045, 0.12),
             HOUSTON_CHROME)
    make_box("Door_S_Leaf_Pull", (1.22, 0.235, 1.05), (0.025, 0.03, 0.55),
             HOUSTON_CHROME)
    # E / W walls — solid.
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    # Drop-tile ceiling, grid on, stains OFF — the temple to control
    # does not leak (canon-negative).
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, with_grid=True, with_stains=False)


def build_curtain_wall():
    """The glass wall of her office (ch10 L74/L82/L453/L489; ch11
    L280): full-width floor-to-ceiling curtain wall on the N —
    anodized verticals on CURTAIN_PITCH, sill channel, transom
    rail, header. NO glass (playbook: openings + frames/mullions).
    The .tscn Fill_Window light reads through it."""
    wy = ROOM_D
    make_box("Curtain_Sill", (0.0, wy, 0.06), (ROOM_W + 0.4, 0.24, 0.12),
             HOUSTON_MULLION_DK)
    make_box("Curtain_Header", (0.0, wy, CEIL - 0.06),
             (ROOM_W + 0.4, 0.24, 0.12), HOUSTON_MULLION_DK)
    # Transom rail — vision glass below, clerestory band above.
    make_box("Curtain_Rail", (0.0, wy, 2.26), (ROOM_W + 0.4, 0.14, 0.06),
             HOUSTON_MULLION)
    n_mull = int(round((ROOM_W + 0.4) / CURTAIN_PITCH))     # 8 bays
    for mi in range(n_mull + 1):
        mx = -(ROOM_W + 0.4) / 2.0 + mi * (ROOM_W + 0.4) / n_mull
        make_box(f"Curtain_Mull_{mi}", (mx, wy, CEIL / 2.0),
                 (0.07, 0.18, CEIL), HOUSTON_MULLION)


def build_houston_outside():
    """Houston through the glass, twelve stories up (ch10 L90).
    Three tower tiers, a mid-rise rooftop below our sightline, the
    freeway ribbon far below, the hawk (ch10 L90 / ch11 L280), and
    the single lit window at the edge of her sightline (ch10
    L489)."""
    # Near tower — rises past us; face strips give it scale.
    make_box("Tower_A", (-6.0, 19.0, -13.0), (6.0, 6.0, 54.0),
             HOUSTON_TOWER_A)
    for si in range(4):
        make_box(f"Tower_A_Strip_{si}", (-8.4 + si * 1.6, 15.95, -13.0),
                 (0.18, 0.14, 54.0), HOUSTON_MULLION_DK)
    # The one lit office window (ch10 L489), on Tower A's face.
    make_box("Tower_A_LitWindow", (-5.2, 15.92, -3.2), (0.55, 0.10, 0.40),
             HOUSTON_TOWER_LIT)
    # Mid tower and haze slab.
    make_box("Tower_B", (5.5, 27.0, -17.0), (6.5, 6.0, 46.0),
             HOUSTON_TOWER_B)
    make_box("Tower_C", (6.0, 41.0, -11.0), (16.0, 6.0, 58.0),
             HOUSTON_TOWER_C)
    # Mid-rise rooftop BELOW us — we see its roof + mech unit, which
    # is what sells "twelve stories up".
    make_box("Midrise_Roof", (9.0, 14.0, -21.0), (6.0, 5.0, 38.0),
             HOUSTON_TOWER_B)
    make_box("Midrise_Mech", (9.5, 13.5, -1.6), (1.6, 1.2, 0.80),
             HOUSTON_MULLION_DK)
    # The freeway, far below (ch10 L90) — ribbon + stripes + cars
    # doing the slow desperate ballet.
    make_box("Freeway_Deck", (0.0, 12.8, -38.0), (44.0, 3.2, 0.30),
             HOUSTON_ASPHALT)
    for li in range(5):
        make_box(f"Freeway_Stripe_{li}", (-16.0 + li * 8.0, 12.8, -37.83),
                 (2.2, 0.10, 0.02), HOUSTON_LANE)
    for ci, (cx, cy2, cc) in enumerate([
            (-11.0, 12.0, (0.60, 0.60, 0.62, 1.0)),
            (-2.5, 13.6, (0.34, 0.36, 0.40, 1.0)),
            (6.0, 12.2, (0.52, 0.30, 0.24, 1.0)),
            (13.5, 13.4, (0.60, 0.60, 0.62, 1.0))]):
        make_box(f"Freeway_Car_{ci}", (cx, cy2, -37.72), (0.9, 0.42, 0.26),
                 cc)
    # The hawk on its thermal, below the sightline (ch11 L280:
    # "circling on a thermal twelve stories below").
    make_box("Hawk_Wings", (3.6, 13.0, -3.4), (0.55, 0.10, 0.03),
             HOUSTON_HAWK)
    make_box("Hawk_Body", (3.6, 13.0, -3.42), (0.10, 0.26, 0.05),
             HOUSTON_HAWK)


def build_glass_partition():
    """'Glass walls', plural (ch10 L82): the interior partition
    between her office and Marcus's anteroom ('Not in this room.
    The next one.' ch11 L271). Chrome channels + posts, a CLOSED
    chrome-framed door — and no glass anywhere, per playbook."""
    px = PART_X
    make_box("Part_Channel_Top", (px, ROOM_D / 2.0, CEIL - 0.04),
             (0.10, ROOM_D, 0.08), HOUSTON_MULLION_DK)
    # Bottom channel skips the door gap y in [0.75, 1.65].
    make_box("Part_Channel_Bot_S", (px, 0.375, 0.04), (0.10, 0.75, 0.08),
             HOUSTON_MULLION_DK)
    make_box("Part_Channel_Bot_N", (px, 4.325, 0.04), (0.10, 5.35, 0.08),
             HOUSTON_MULLION_DK)
    for pi, py in enumerate([0.75, 1.65, 3.05, 4.45, 5.85]):
        make_box(f"Part_Post_{pi}", (px, py, CEIL / 2.0),
                 (0.06, 0.06, CEIL), HOUSTON_CHROME)
    # Door header channel over the gap; above-door band left open.
    make_box("Part_Door_Header", (px, 1.20, 2.09), (0.08, 0.90, 0.08),
             HOUSTON_CHROME)
    # The closed door leaf — chrome outline, open air where glass
    # would be.
    make_box("Part_Door_StileS", (px, 0.79, 1.025), (0.045, 0.04, 2.05),
             HOUSTON_CHROME)
    make_box("Part_Door_StileN", (px, 1.61, 1.025), (0.045, 0.04, 2.05),
             HOUSTON_CHROME)
    make_box("Part_Door_RailT", (px, 1.20, 1.98), (0.045, 0.78, 0.08),
             HOUSTON_CHROME)
    make_box("Part_Door_RailB", (px, 1.20, 0.06), (0.045, 0.78, 0.12),
             HOUSTON_CHROME)
    make_box("Part_Door_Pull", (px + 0.055, 1.50, 1.05),
             (0.025, 0.03, 0.55), HOUSTON_CHROME)


def build_desk():
    """The teak desk (ch10 L158): custom, 2014, zero visible
    imperfection. Twin pedestals of three drawers each — the third
    drawer is canon (ch10 L46: eyedrops, spare charger, the 2003
    comb). Chrome pulls; modesty panel; faces S toward the door."""
    make_box("Desk_Top", (DESK_CX, DESK_CY, DESK_TOP_Z - 0.0225),
             (2.00, 0.90, 0.045), COL_TEAK)
    for sgn in (-1, +1):
        make_box(f"Desk_Pedestal_{sgn:+d}",
                 (DESK_CX + sgn * 0.75, DESK_CY, 0.359),
                 (0.44, 0.80, 0.718), COL_TEAK_DK)
        for di, dz in enumerate([0.16, 0.38, 0.60]):
            make_box(f"Desk_Drawer_{sgn:+d}_{di}",
                     (DESK_CX + sgn * 0.75, DESK_CY - 0.415, dz),
                     (0.36, 0.02, 0.17), COL_TEAK)
            make_box(f"Desk_Pull_{sgn:+d}_{di}",
                     (DESK_CX + sgn * 0.75, DESK_CY - 0.435, dz + 0.045),
                     (0.14, 0.018, 0.018), HOUSTON_CHROME)
    make_box("Desk_Modesty", (DESK_CX, DESK_CY + 0.38, 0.40),
             (1.04, 0.035, 0.60), COL_TEAK_DK)


def build_desk_props():
    """The working surface, ch10 dusk + ch11 Saturday 8:47 AM: two
    monitors, the desk phone with the ALBERTO D. caller ID, her
    cell, the pen and pad, Marcus's two coffees, the chrome lamp,
    and the one personal item — the Galveston photo."""
    tz = DESK_TOP_Z
    # Monitor 1 (W) — the eleven-page draft / the denied motion
    # email that "continued to be denied" (ch10 L457, ch11 L74).
    make_box("Monitor1_Panel", (0.52, DESK_CY + 0.16, 1.06),
             (0.56, 0.030, 0.34), COL_MONITOR)
    make_box("Monitor1_Screen", (0.52, DESK_CY + 0.143, 1.06),
             (0.50, 0.002, 0.29), COL_SCREEN_DOC)
    make_box("Monitor1_SubjectBar", (0.52, DESK_CY + 0.141, 1.175),
             (0.50, 0.001, 0.045), COL_SCREEN_DENY)
    for li in range(4):
        make_box(f"Monitor1_Line_{li}", (0.50, DESK_CY + 0.141,
                 1.10 - li * 0.045), (0.42, 0.001, 0.014), COL_SCREEN_LN)
    make_box("Monitor1_Stand", (0.52, DESK_CY + 0.18, 0.82),
             (0.06, 0.06, 0.14), HOUSTON_CHROME)
    make_box("Monitor1_Foot", (0.52, DESK_CY + 0.18, tz + 0.008),
             (0.26, 0.18, 0.016), HOUSTON_CHROME)
    # Monitor 2 (E) — Newsom v. PetroTex settlement boilerplate,
    # still open from yesterday (ch11 L228).
    make_box("Monitor2_Panel", (1.66, DESK_CY + 0.16, 1.06),
             (0.56, 0.030, 0.34), COL_MONITOR)
    make_box("Monitor2_Screen", (1.66, DESK_CY + 0.143, 1.06),
             (0.50, 0.002, 0.29), COL_SCREEN_DOC)
    for li in range(6):
        make_box(f"Monitor2_Line_{li}", (1.64, DESK_CY + 0.141,
                 1.165 - li * 0.038), (0.42, 0.001, 0.012), COL_SCREEN_LN)
    make_box("Monitor2_Stand", (1.66, DESK_CY + 0.18, 0.82),
             (0.06, 0.06, 0.14), HOUSTON_CHROME)
    make_box("Monitor2_Foot", (1.66, DESK_CY + 0.18, tz + 0.008),
             (0.26, 0.18, 0.016), HOUSTON_CHROME)
    # Keyboard, squared to the monitors.
    make_box("Keyboard", (1.09, DESK_CY - 0.14, tz + 0.012),
             (0.44, 0.15, 0.024), COL_MESH_CHAIR)
    # The desk phone — caller ID glowing ALBERTO D. (ch10 L230).
    make_box("DeskPhone_Body", (1.98, DESK_CY - 0.05, tz + 0.035),
             (0.22, 0.17, 0.07), COL_PHONE_BODY)
    make_box("DeskPhone_Handset", (1.90, DESK_CY - 0.05, tz + 0.085),
             (0.05, 0.16, 0.030), COL_PHONE_BODY)
    make_box("DeskPhone_LCD", (2.02, DESK_CY - 0.095, tz + 0.073),
             (0.10, 0.001, 0.030), COL_PHONE_LCD)
    # Her cell, face-up — the painter is saved under J (ch10 L473).
    make_box("CellPhone", (1.62, DESK_CY - 0.22, tz + 0.007),
             (0.074, 0.152, 0.014), COL_CELL)
    make_box("CellPhone_Screen", (1.62, DESK_CY - 0.22, tz + 0.0145),
             (0.064, 0.132, 0.001), COL_CELL_SCREEN)
    # Legal pad + the pen she set down (ch11 L200).
    make_box("LegalPad", (0.44, DESK_CY - 0.20, tz + 0.004),
             (0.22, 0.30, 0.008), COL_LEGAL_PAD)
    for li, ly in enumerate([-0.10, -0.14, -0.18]):
        make_box(f"LegalPad_Line_{li}", (0.43, DESK_CY + ly, tz + 0.0085),
                 (0.16, 0.012, 0.001), COL_INK)
    make_cyl("Pen", (0.62, DESK_CY - 0.30, tz + 0.012), 0.005, 0.14,
             COL_INK, axis='Y', segments=6)
    # Marcus's two coffees, lidded (ch11 L130/L161).
    make_cyl("Coffee_Erica", (1.94, DESK_CY + 0.22, tz + 0.065),
             0.038, 0.13, COL_CUP_PAPER, segments=10)
    make_cyl("Coffee_Erica_Lid", (1.94, DESK_CY + 0.22, tz + 0.137),
             0.040, 0.015, COL_CUP_LID, segments=10)
    make_cyl("Coffee_Second", (0.30, DESK_CY + 0.02, tz + 0.065),
             0.038, 0.13, COL_CUP_PAPER, segments=10)
    make_cyl("Coffee_Second_Lid", (0.30, DESK_CY + 0.02, tz + 0.137),
             0.040, 0.015, COL_CUP_LID, segments=10)
    # The chrome desk lamp — "small reflections in the chrome and
    # the glass and the smooth teak" (ch10 L509).
    make_cyl("Lamp_Base", (0.10, DESK_CY + 0.26, tz + 0.015), 0.065, 0.03,
             HOUSTON_CHROME, segments=10)
    make_cyl("Lamp_Stem", (0.10, DESK_CY + 0.26, tz + 0.20), 0.011, 0.34,
             HOUSTON_CHROME, segments=8)
    make_cyl("Lamp_Head", (0.24, DESK_CY + 0.26, tz + 0.38), 0.045, 0.26,
             HOUSTON_CHROME, axis='X', segments=10)
    make_cyl("Lamp_Bulb", (0.24, DESK_CY + 0.26, tz + 0.355), 0.028, 0.18,
             (0.95, 0.88, 0.62, 1.0), axis='X', segments=8)
    # The ONLY personal item (ch11 L228): her mother, sun hat,
    # Galveston 1996 — small frame on the SE desk corner.
    make_box("Photo_Frame", (2.02, DESK_CY - 0.30, tz + 0.075),
             (0.115, 0.016, 0.15), COL_FRAME_DK)
    make_box("Photo_Print", (2.02, DESK_CY - 0.309, tz + 0.075),
             (0.095, 0.002, 0.125), COL_PHOTO_WARM)
    make_box("Photo_SunHat", (2.015, DESK_CY - 0.311, tz + 0.105),
             (0.030, 0.001, 0.016), (0.93, 0.88, 0.72, 1.0))


def build_chairs():
    """Her ergonomic chair — she gripped the ARMRESTS through the
    lurch (ch10 L54) — and two chrome visitor chairs squared to
    the desk (nine-fifteen is coming, ch11 L251)."""
    cx, cy = DESK_CX, DESK_CY + 0.85
    make_box("Chair_E_Seat", (cx, cy, 0.50), (0.52, 0.48, 0.07),
             COL_MESH_CHAIR)
    make_box("Chair_E_Back", (cx, cy + 0.25, 1.00), (0.50, 0.06, 0.78),
             COL_MESH_CHAIR)
    make_box("Chair_E_Headrest", (cx, cy + 0.26, 1.47), (0.34, 0.05, 0.14),
             COL_MESH_CHAIR)
    for asgn in (-1, +1):
        make_box(f"Chair_E_Arm_{asgn:+d}", (cx + asgn * 0.30, cy, 0.685),
                 (0.06, 0.30, 0.035), COL_MESH_CHAIR)
        make_box(f"Chair_E_ArmPost_{asgn:+d}",
                 (cx + asgn * 0.30, cy + 0.10, 0.585),
                 (0.04, 0.04, 0.17), HOUSTON_CHROME)
    make_cyl("Chair_E_Column", (cx, cy, 0.28), 0.032, 0.38,
             HOUSTON_CHROME, segments=8)
    make_cyl("Chair_E_Base", (cx, cy, 0.035), 0.27, 0.05,
             HOUSTON_CHROME, segments=10)
    # Visitor chairs — chrome cantilever frames, squared precisely.
    for vi, vx in enumerate([0.45, 1.75]):
        vy = 3.20
        make_box(f"Visitor_{vi}_Seat", (vx, vy, 0.46), (0.46, 0.44, 0.05),
                 COL_VISITOR)
        make_box(f"Visitor_{vi}_Back", (vx, vy + 0.21, 0.82),
                 (0.46, 0.045, 0.42), COL_VISITOR)
        for lsgn in (-1, +1):
            make_cyl(f"Visitor_{vi}_LegF_{lsgn:+d}",
                     (vx + lsgn * 0.21, vy - 0.20, 0.22), 0.014, 0.44,
                     HOUSTON_CHROME, segments=8)
            make_cyl(f"Visitor_{vi}_LegB_{lsgn:+d}",
                     (vx + lsgn * 0.21, vy + 0.20, 0.22), 0.014, 0.44,
                     HOUSTON_CHROME, segments=8)
            make_cyl(f"Visitor_{vi}_Runner_{lsgn:+d}",
                     (vx + lsgn * 0.21, vy, 0.014), 0.012, 0.46,
                     HOUSTON_CHROME, axis='Y', segments=8)


def build_file_wall():
    """E wall: 'Files indexed with obsessive precision, paper and
    digital' (ch10 L82). Lateral file credenza, two shelves of
    flush-aligned binders, and the Fortress Menu rack — slate /
    red / gold / Alberto's manila log (_UNLOCK_WEB.md L616) plus
    the unindexed fifth: CASE PREDECESSOR, Settlement Grey
    (_SINKHOLE_NEXUS.md L185-187). The grey file is the only one
    with NO index tab."""
    ex = ROOM_W / 2.0 - 0.36
    make_box("Credenza_Body", (ex, 4.00, 0.375), (0.52, 3.60, 0.75),
             COL_CAB_BODY)
    make_box("Credenza_Top", (ex, 4.00, 0.765), (0.56, 3.68, 0.03),
             COL_CAB_FACE)
    for bi in range(2):
        for di in range(2):
            fy = 3.10 + bi * 1.80
            make_box(f"Credenza_Drawer_{bi}_{di}",
                     (ex - 0.27, fy, 0.22 + di * 0.34),
                     (0.02, 1.62, 0.30), COL_CAB_FACE)
            make_box(f"Credenza_Pull_{bi}_{di}",
                     (ex - 0.285, fy, 0.34 + di * 0.34),
                     (0.014, 0.30, 0.020), HOUSTON_CHROME)
    # Binder shelves — uniform runs, all spines flush (obsessive).
    for si, sz in enumerate([1.30, 1.72]):
        make_box(f"Shelf_{si}", (ex + 0.06, 4.00, sz), (0.34, 3.40, 0.035),
                 COL_CAB_FACE)
        make_box(f"Shelf_{si}_Bracket_S", (ex + 0.16, 2.55, sz - 0.09),
                 (0.03, 0.03, 0.14), HOUSTON_MULLION_DK)
        make_box(f"Shelf_{si}_Bracket_N", (ex + 0.16, 5.45, sz - 0.09),
                 (0.03, 0.03, 0.14), HOUSTON_MULLION_DK)
        for bi in range(14):
            by = 2.70 + bi * 0.19
            col = COL_BINDER_A if (bi + si) % 2 == 0 else COL_BINDER_B
            make_box(f"Binder_{si}_{bi}", (ex + 0.05, by, sz + 0.165),
                     (0.24, 0.062, 0.295), col)
            make_box(f"Binder_{si}_{bi}_Label", (ex - 0.075, by, sz + 0.20),
                     (0.002, 0.036, 0.06), COL_TAB_WHITE)
    # The Fortress Menu rack on the credenza top.
    rx, ry = ex - 0.04, 4.92
    make_box("Fortress_Rack_Base", (rx, ry, 0.785), (0.30, 0.42, 0.014),
             HOUSTON_CHROME)
    make_box("Fortress_Rack_End_S", (rx, ry - 0.20, 0.90),
             (0.28, 0.012, 0.22), HOUSTON_CHROME)
    make_box("Fortress_Rack_End_N", (rx, ry + 0.20, 0.90),
             (0.28, 0.012, 0.22), HOUSTON_CHROME)
    fortress = [
        ("Slate", COL_FILE_SLATE, True, 0.055),
        ("Red", COL_FILE_RED, True, 0.115),
        ("Gold", COL_FILE_GOLD, True, 0.175),
        ("AlbertoLog", P.PAPER_AGED, True, 0.055),
        ("SettlementGrey", COL_FILE_GREY, False, 0.0),
    ]
    for fi, (fname, fcol, has_tab, tab_off) in enumerate(fortress):
        fy = ry - 0.14 + fi * 0.07
        make_box(f"Fortress_File_{fname}", (rx, fy, 0.945),
                 (0.24, 0.022, 0.30), fcol)
        if has_tab:
            make_box(f"Fortress_Tab_{fname}",
                     (rx - 0.12 + 0.05 + tab_off, fy, 1.105),
                     (0.055, 0.018, 0.022), COL_TAB_WHITE)


def build_anteroom():
    """Marcus's room — 'Not in this room. The next one.' (ch11
    L271). His desk, one monitor, chair, the printer, and the
    firm's floor plant (personal-item discipline keeps it OUT of
    Erica's side, ch11 L228)."""
    mx = -4.30
    make_box("Marcus_Desk_Top", (mx, 3.60, 0.715), (0.70, 1.50, 0.035),
             COL_CAB_FACE)
    for lsgn in (-1, +1):
        make_box(f"Marcus_Desk_Panel_{lsgn:+d}", (mx, 3.60 + lsgn * 0.71,
                 0.35), (0.64, 0.035, 0.70), COL_CAB_BODY)
    make_box("Marcus_Monitor", (mx - 0.10, 3.60, 1.02),
             (0.030, 0.50, 0.31), COL_MONITOR)
    make_box("Marcus_Monitor_Stand", (mx - 0.10, 3.60, 0.80),
             (0.05, 0.05, 0.13), HOUSTON_CHROME)
    make_box("Marcus_Keyboard", (mx + 0.16, 3.60, 0.745),
             (0.14, 0.40, 0.022), COL_MESH_CHAIR)
    make_box("Marcus_Chair_Seat", (-3.55, 3.60, 0.48),
             (0.46, 0.46, 0.06), COL_VISITOR)
    make_box("Marcus_Chair_Back", (-3.32, 3.60, 0.92),
             (0.05, 0.44, 0.56), COL_VISITOR)
    make_cyl("Marcus_Chair_Column", (-3.55, 3.60, 0.27), 0.028, 0.36,
             HOUSTON_CHROME, segments=8)
    make_cyl("Marcus_Chair_Base", (-3.55, 3.60, 0.03), 0.24, 0.045,
             HOUSTON_CHROME, segments=10)
    # Printer station.
    make_box("Printer_Stand", (-4.40, 5.75, 0.30), (0.60, 0.55, 0.60),
             COL_CAB_BODY)
    make_box("Printer_Body", (-4.40, 5.75, 0.775), (0.50, 0.46, 0.35),
             COL_PRINTER)
    make_box("Printer_Tray", (-4.06, 5.75, 0.70), (0.18, 0.30, 0.02),
             COL_PRINTER)
    make_box("Printer_Paper", (-4.40, 5.75, 0.965), (0.24, 0.32, 0.028),
             P.PAPER)
    # The firm's plant — anteroom side only.
    make_floor_plant("Plant_Anteroom", (-4.30, 0.95, 0.0))


def build_ceiling_infra():
    """Recessed troffers (the .tscn key light is NAMED Key_Fluor),
    HVAC, smoke detectors, sprinklers. No camera dome, no Muzak
    speaker — partner-office register."""
    for j, ypos in enumerate([1.9, 4.2, 6.2]):
        for i, xpos in enumerate([0.4, 3.2]):
            make_fluorescent_tube_fixture(f"Troffer_E_{j}_{i}",
                                          (xpos, ypos, CEIL),
                                          length=1.15, width=0.55)
    for j, ypos in enumerate([2.6, 5.2]):
        make_fluorescent_tube_fixture(f"Troffer_W_{j}", (-3.5, ypos, CEIL),
                                      length=1.15, width=0.55)
    make_hvac_vent("HVAC_E", (2.0, 5.6, CEIL), width=1.00, depth=0.50)
    make_hvac_vent("HVAC_W", (-3.5, 1.4, CEIL), width=0.80, depth=0.45)
    make_smoke_detector("Smoke_E", (1.4, 2.6, CEIL))
    make_smoke_detector("Smoke_W", (-3.4, 3.8, CEIL))
    make_sprinkler("Sprinkler_E", (2.8, 1.6, CEIL))
    make_sprinkler("Sprinkler_W", (-2.6, 6.0, CEIL))


def main():
    clear_scene()
    build_shell()
    build_curtain_wall()
    build_houston_outside()
    build_glass_partition()
    build_desk()
    build_desk_props()
    build_chairs()
    build_file_wall()
    build_anteroom()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/houston_office.glb"))
    print(f"\n[build_houston_office] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
