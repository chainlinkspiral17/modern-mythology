"""VOL 5 · VIII Strength — the New Orleans bar. "The Ouroboros in
the Ashtray" (vol5_ch8_strength.json). Douglas Forte's Saturday-
night dive somewhere off the Marigny: the muted game on the bar TV,
three buzzing beer neons, his corner booth, the tired bartender's
long bar with the brass rail. Late-90s operator-noir warmth — the
grime is part of the offer (L40).

ADJUDICATION — NOT the same building as new_orleans_room. The coda
walks "the eight blocks back to the room above the laundromat"
(vol5_ch8_strength.json L280), so the two locales are separate
sites. Palettes are independent but city-consistent (the small
NOLA_* register below is repeated by intent, not a shared-venue
KEEP-IN-SYNC contract).

Canon dressed into this room (line numbers = vol5_ch8_strength.json):
  · The bar TV, muted football, "ghosts in pads" (L40); the next
    game with the Saints behind by ten (L352, L356). High on the
    N wall over the backbar's east end, screen facing the room.
  · "the buzzing neon of three different beer signs, two of which
    had been advertising brands the bar no longer carried" (L40):
    a red ring over the corner booth — the neon the ouroboros
    tattoo "caught ... and sent it back, dim and red" (L68) — plus
    a dusty amber board over the mirror and a dusty green board on
    the E wall (the two defunct brands, still lit, still buzzing).
  · His corner booth (L44), cheap vinyl that sighs (L252), sticky
    tabletop (L52 — darker sheen patch under the props).
  · HERO — the ashtray (chapter subtitle, L27; "stale smoke", L44):
    a ring of ash curled back on itself in the bowl, the butt's
    ember tip meeting its own tail. Grace, not force.
  · What he leaves on the table (L252): two empty bottles, the
    grimed glass with its condensation paths (L40), and a folded
    twenty under the saltshaker.
  · The bartender's side (L84): register — cash bar (L128, L252) —
    and "the same rag" on "the same bar" (L352).
  · The long back mirror — "reflections distorted by cheap bar
    glass" (L144). Opaque pale slab; vertex colors can't do glass.
  · The jukebox is KEPT from the scaffold (the .tscn's
    Fill_JukeboxGlow light is named for it) but dark and silent —
    "The silence in the bar felt louder now" (L204).
  · House clock frozen 11:47 — the hour of Refrain 2, before the
    walk home ("too many midnights", L84).
Canon-negatives: NO ceiling fans (never staged), NO fluorescent
troughs (the light here is neon + pendants + TV — scaffold's
corporate fixtures removed), no band gear, no pool table. The
woman in white / lion-tamer exists only on the card (L32) and the
open question of whether she and the Star woman are the same
figure is NOT resolved in geometry — no figure, no white dress,
no lemniscate prop.

Playbook compliance: windows are REAL openings with frame +
mullions + open louver shutters, no glass slabs; scaffold's
make_counter bug fixed (it ran the 7 m bar along Y through the N
wall of a 6 m room); bottles/mirror/jukebox glass all opaque tints.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.store_fixtures import make_register
from _props.decor import make_wall_clock
from _props.safety import make_smoke_detector, make_ceiling_speaker

# Shell footprint — KEPT from the scaffold; the Background3D preset
# ("new_orleans_bar", camera at the S door looking N) and the .tscn
# lights are tuned to it.
ROOM_W = 9.0; ROOM_D = 6.0; CEIL = 3.20

# ── NOLA city register ────────────────────────────────────────────
# City-consistent hues, repeated by intent in build_new_orleans_bar
# .py and build_new_orleans_room.py. NOT a shared-venue block: the
# bar and the room are eight blocks apart (vol5_ch8 L280).
NOLA_BRASS      = (0.80, 0.60, 0.28, 1.0)   # rails, knobs, finials
NOLA_CYPRESS    = (0.38, 0.26, 0.16, 1.0)   # old-growth trim wood
NOLA_CYPRESS_DK = (0.22, 0.14, 0.09, 1.0)
NOLA_IRON       = (0.17, 0.16, 0.15, 1.0)   # wrought / cast iron
NOLA_LINEN      = (0.84, 0.80, 0.72, 1.0)   # bar rag / bed linen
# ── end city register ─────────────────────────────────────────────

# Bar-local palette — smoke-cured plaster, worn plank, oxblood vinyl.
PAL = {"wall": (0.34, 0.24, 0.18, 1.0), "baseboard": (0.16, 0.11, 0.09, 1.0)}
COL_FLOOR = (0.30, 0.21, 0.15, 1.0); COL_SEAM = (0.17, 0.11, 0.08, 1.0)
COL_SCUFF = (0.23, 0.15, 0.10, 1.0)
COL_BAR_TOP = (0.20, 0.13, 0.09, 1.0)
COL_VINYL_OX = (0.44, 0.18, 0.15, 1.0)      # cheap booth vinyl (L252)
COL_TABLE = (0.37, 0.25, 0.15, 1.0)
COL_STICKY = (0.29, 0.19, 0.11, 1.0)        # the sticky sheen (L52)
COL_MIRROR = (0.62, 0.68, 0.72, 1.0)        # opaque "cheap bar glass"
COL_NEON_RED = (0.88, 0.24, 0.18, 1.0)      # the booth ring (L68)
COL_NEON_AMBER = (0.92, 0.62, 0.24, 1.0)
COL_NEON_GREEN = (0.36, 0.64, 0.42, 1.0)
COL_BOARD = (0.12, 0.10, 0.09, 1.0)         # the live sign's board
COL_BOARD_DUST = (0.19, 0.16, 0.13, 1.0)    # the two defunct brands
COL_BOTTLE_AMBER = (0.66, 0.38, 0.16, 1.0)
COL_BOTTLE_GREEN = (0.30, 0.40, 0.22, 1.0)
COL_BOTTLE_BROWN = (0.30, 0.18, 0.10, 1.0)
COL_BOTTLE_CLEAR = (0.62, 0.68, 0.64, 1.0)  # opaque glass-gray
COL_TV_FIELD = (0.22, 0.38, 0.24, 1.0)
COL_TV_GOLD = (0.80, 0.64, 0.28, 1.0)       # Saints old gold (L356)
COL_TV_DARK = (0.10, 0.10, 0.10, 1.0)
COL_ASH = (0.55, 0.53, 0.50, 1.0)
COL_ASHTRAY = (0.58, 0.42, 0.24, 1.0)       # amber glass, opaque
COL_ASHTRAY_BOWL = (0.26, 0.19, 0.12, 1.0)
COL_CIG_PAPER = (0.88, 0.86, 0.80, 1.0)
COL_EMBER = (0.82, 0.36, 0.16, 1.0)
COL_TWENTY = (0.52, 0.58, 0.46, 1.0)        # the folded twenty (L252)

BAR_CX = 0.9                                 # bar run center (E of center
                                             # so the NW corner keeps the booth)
BAR_TOP_Z = 1.16                             # working surface height


def _s_window_wall(tag, seg_cx):
    """One south-wall segment with a REAL window opening (playbook:
    no glass — piers + sill + header + frame + cross mullion), plus
    open louvered shutters flat against the street face. Segment
    spans seg_cx ± 1.40; opening is 1.50 w × 1.30 h, sill at 1.10."""
    sgn = 1 if seg_cx > 0 else -1
    # Piers / sill band / header band (wall plane y = 0 ± 0.10).
    make_box(f"WallS_{tag}_PierIn", (seg_cx - sgn * 1.075, 0.0, CEIL / 2.0),
             (0.65, 0.20, CEIL), PAL["wall"])
    make_box(f"WallS_{tag}_PierOut", (seg_cx + sgn * 1.075, 0.0, CEIL / 2.0),
             (0.65, 0.20, CEIL), PAL["wall"])
    make_box(f"WallS_{tag}_Below", (seg_cx, 0.0, 0.55), (1.50, 0.20, 1.10),
             PAL["wall"])
    make_box(f"WallS_{tag}_Above", (seg_cx, 0.0, 2.80), (1.50, 0.20, 0.80),
             PAL["wall"])
    make_box(f"WallS_{tag}_Base", (seg_cx, 0.16, 0.08), (2.80, 0.06, 0.16),
             PAL["baseboard"])
    # Frame + cross mullion — NO glass (see-through to the night).
    make_box(f"Win_{tag}_Head", (seg_cx, 0.0, 2.44), (1.60, 0.26, 0.08),
             NOLA_CYPRESS)
    for jsgn in (-1, +1):
        make_box(f"Win_{tag}_Jamb_{jsgn:+d}",
                 (seg_cx + jsgn * 0.77, 0.0, 1.75), (0.08, 0.26, 1.46),
                 NOLA_CYPRESS)
    make_box(f"Win_{tag}_Sill", (seg_cx, 0.16, 1.075), (1.66, 0.14, 0.05),
             NOLA_CYPRESS)
    make_box(f"Win_{tag}_MullV", (seg_cx, 0.0, 1.75), (0.05, 0.08, 1.30),
             NOLA_CYPRESS_DK)
    make_box(f"Win_{tag}_MullH", (seg_cx, 0.0, 1.75), (1.50, 0.08, 0.05),
             NOLA_CYPRESS_DK)
    # Open louver shutters folded back over the piers (street side).
    for ssgn, snm in ((-1, "L"), (+1, "R")):
        scx = seg_cx + ssgn * 1.08
        make_box(f"Shutter_{tag}_{snm}_Panel", (scx, -0.16, 1.75),
                 (0.62, 0.05, 1.40), NOLA_CYPRESS_DK)
        for li in range(6):
            make_box(f"Shutter_{tag}_{snm}_Louver_{li}",
                     (scx, -0.19, 1.30 + li * 0.18),
                     (0.52, 0.02, 0.05), NOLA_CYPRESS)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=PAL, baseboard_face_sign=-1)
    # S wall: door gap x ∈ [-1.8, +1.8] (camera doorway — he walks
    # out into the humid night through it, L260), framed posts +
    # lintel + open mullioned transom, one real window per side.
    for psgn in (-1, +1):
        make_box(f"Door_Post_{psgn:+d}", (psgn * 1.85, 0.0, CEIL / 2.0),
                 (0.10, 0.24, CEIL), NOLA_CYPRESS_DK)
    make_box("Door_Lintel", (0.0, 0.0, 2.60), (3.70, 0.22, 0.10), NOLA_CYPRESS_DK)
    make_box("Door_TransomTop", (0.0, 0.0, 3.125), (3.70, 0.20, 0.15), PAL["wall"])
    for mi, mx in enumerate([-1.35, -0.45, 0.45, 1.35]):
        make_box(f"Door_TransomMull_{mi}", (mx, 0.0, 2.86),
                 (0.05, 0.10, 0.42), NOLA_CYPRESS_DK)
    _s_window_wall("W", -3.30)
    _s_window_wall("E", +3.30)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4,
                 palette={"tile": (0.24, 0.17, 0.12, 1.0),
                          "grid": (0.14, 0.10, 0.08, 1.0)},
                 with_stains=False)
    # Smoke-cured water stains hung BELOW the tile plane so they read.
    for si, (sx, sy) in enumerate([(-2.6, 2.0), (3.1, 4.5)]):
        make_box(f"Ceil_Stain_{si}", (sx, sy, CEIL - 0.006),
                 (0.75, 0.70, 0.004), (0.33, 0.26, 0.18, 1.0))
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": NOLA_CYPRESS})
    # The grime is part of the offer (L40) — wear paths: door, bar
    # rail, and the walk to the corner booth.
    make_box("Floor_Scuff_Door", (0.0, 0.55, 0.007), (1.60, 0.90, 0.002), COL_SCUFF)
    make_box("Floor_Scuff_Bar", (BAR_CX, 3.42, 0.007), (5.00, 0.55, 0.002), COL_SCUFF)
    make_box("Floor_Scuff_Booth", (-3.5, 2.9, 0.007), (0.80, 3.20, 0.002), COL_SCUFF)


def build_corner_booth():
    """Douglas's corner booth, NW corner (L44). Benches perpendicular
    to the W wall, open at the east end toward the room (playbook
    booth rule); cheap oxblood vinyl (L252); sticky tabletop (L52).
    Later taken by the two younger men who won't tip (L352) — same
    geometry, the room doesn't change for them."""
    bx = -3.50                               # bench/table center x
    for cy, bnm, back_y in ((5.62, "N", 5.84), (4.44, "S", 4.22)):
        make_box(f"Booth_{bnm}_Base", (bx, cy, 0.20), (1.70, 0.45, 0.40),
                 NOLA_CYPRESS_DK)
        make_box(f"Booth_{bnm}_Seat", (bx, cy, 0.45), (1.70, 0.47, 0.10),
                 COL_VINYL_OX)
        make_box(f"Booth_{bnm}_Back", (bx, back_y, 0.85), (1.70, 0.12, 0.75),
                 COL_VINYL_OX)
        make_box(f"Booth_{bnm}_BackCap", (bx, back_y, 1.25), (1.70, 0.14, 0.05),
                 NOLA_CYPRESS_DK)
    # An hour of body heat pressed into the S seat (L252) — worn patch.
    make_box("Booth_S_SeatWear", (-3.30, 4.44, 0.505), (0.48, 0.40, 0.004),
             (0.36, 0.14, 0.12, 1.0))
    # Table on an iron pedestal, W end near the wall.
    make_box("Booth_Table_Top", (-3.55, 5.03, 0.745), (1.45, 0.70, 0.05),
             COL_TABLE)
    make_cyl("Booth_Table_Pedestal", (-3.55, 5.03, 0.36), 0.06, 0.68,
             NOLA_IRON)
    make_cyl("Booth_Table_Foot", (-3.55, 5.03, 0.02), 0.22, 0.04, NOLA_IRON,
             segments=10)
    # Sticky sheen under everything (L52).
    make_box("Booth_Table_Sticky", (-3.45, 5.03, 0.771), (0.52, 0.38, 0.002),
             COL_STICKY)
    # HERO — the ouroboros in the ashtray (L27, L44): amber-glass
    # ashtray, a ring of ash curled back on itself, the butt's ember
    # tip meeting the ring where head eats tail.
    ax_, ay_ = -3.35, 5.00
    make_cyl("Ashtray_Body", (ax_, ay_, 0.786), 0.055, 0.032, COL_ASHTRAY,
             segments=12)
    make_cyl("Ashtray_Bowl", (ax_, ay_, 0.806), 0.042, 0.008, COL_ASHTRAY_BOWL,
             segments=12)
    make_cyl("Ashtray_AshRing", (ax_, ay_, 0.812), 0.030, 0.006, COL_ASH,
             segments=12)
    make_cyl("Ashtray_AshRing_Hole", (ax_, ay_, 0.8125), 0.017, 0.007,
             COL_ASHTRAY_BOWL, segments=10)
    make_cyl("Ashtray_Butt", (ax_ + 0.010, ay_, 0.818), 0.006, 0.050,
             COL_CIG_PAPER, axis='X', segments=6)
    make_cyl("Ashtray_Ember", (ax_ + 0.038, ay_, 0.818), 0.0065, 0.010,
             COL_EMBER, axis='X', segments=6)
    # The folded twenty under the saltshaker (L252).
    make_box("Twenty_Folded", (-3.05, 4.88, 0.7735), (0.075, 0.040, 0.005),
             COL_TWENTY)
    make_box("Twenty_FoldRidge", (-3.05, 4.88, 0.777), (0.075, 0.020, 0.004),
             COL_TWENTY)
    make_cyl("SaltShaker_Glass", (-3.05, 4.88, 0.820), 0.021, 0.085,
             (0.80, 0.82, 0.78, 1.0), segments=10)
    make_cyl("SaltShaker_Cap", (-3.05, 4.88, 0.871), 0.022, 0.018,
             P.METAL_STEEL, segments=10)
    # The empty bottles he leaves (L252) + the grimed glass whose
    # condensation traced clean paths (L40) — darker grime band low.
    for bi, (bbx, bby) in enumerate([(-3.80, 5.14), (-3.68, 4.80)]):
        make_cyl(f"BoothBottle_{bi}_Body", (bbx, bby, 0.865), 0.031, 0.19,
                 COL_BOTTLE_BROWN, segments=8)
        make_cyl(f"BoothBottle_{bi}_Neck", (bbx, bby, 1.010), 0.012, 0.10,
                 COL_BOTTLE_BROWN, segments=6)
    make_cyl("BoothGlass_Body", (-3.15, 5.18, 0.8375), 0.038, 0.135,
             COL_BOTTLE_CLEAR, segments=10)
    make_cyl("BoothGlass_GrimeBand", (-3.15, 5.18, 0.795), 0.0385, 0.045,
             (0.52, 0.56, 0.52, 1.0), segments=10)


def build_bar():
    """The long bar, E of center so the booth keeps its corner.
    Scaffold bug fixed: make_counter ran its 7 m length along Y —
    through the N wall of a 6 m room. Hand-built E-W run instead.
    The tired bartender's station (L84): register (cash, L128),
    the same rag (L352), two taps for what the bar still carries."""
    make_box("Bar_Body", (BAR_CX, 4.30, 0.55), (5.20, 0.65, 1.10), NOLA_CYPRESS)
    make_box("Bar_Top", (BAR_CX, 4.30, 1.13), (5.50, 0.90, 0.06), COL_BAR_TOP)
    make_box("Bar_Kick", (BAR_CX, 3.965, 0.10), (5.20, 0.03, 0.20),
             NOLA_CYPRESS_DK)
    # Victorian batten strips on the front panel.
    for vi, vx in enumerate([-1.6, -0.6, 0.4, 1.4, 2.4, 3.4]):
        make_box(f"Bar_Batten_{vi}", (vx, 3.96, 0.62), (0.05, 0.03, 0.85),
                 NOLA_CYPRESS_DK)
    # Bullnose front edge (cuts the boxy AABB silhouette).
    for s in range(8):
        sx = (BAR_CX - 2.75) + (s + 0.5) * (5.50 / 8.0)
        make_cyl(f"Bar_Bullnose_{s}", (sx, 3.85, 1.145), 0.025, 5.50 / 8.0,
                 COL_BAR_TOP, axis='X', segments=8)
    # Brass foot rail + brackets (the register of the place).
    make_cyl("Bar_FootRail", (BAR_CX, 3.72, 0.22), 0.028, 5.00, NOLA_BRASS,
             axis='X', segments=10)
    for bi, bx in enumerate([-1.3, 0.9, 3.1]):
        make_box(f"Bar_RailBracket_{bi}", (bx, 3.83, 0.14), (0.04, 0.14, 0.16),
                 NOLA_BRASS)
    # Five stools, brass pillars, oxblood seats.
    for si, sx in enumerate([-1.0, 0.0, 1.0, 2.0, 3.0]):
        make_cyl(f"Stool_{si}_Base", (sx, 3.30, 0.015), 0.18, 0.03, NOLA_IRON,
                 segments=10)
        make_cyl(f"Stool_{si}_Pillar", (sx, 3.30, 0.40), 0.035, 0.74,
                 NOLA_BRASS)
        make_cyl(f"Stool_{si}_FootRing", (sx, 3.30, 0.24), 0.12, 0.02,
                 NOLA_BRASS, segments=10)
        make_cyl(f"Stool_{si}_Seat", (sx, 3.30, 0.80), 0.17, 0.06,
                 COL_VINYL_OX, segments=12)
    # Register at the E end (cash bar — L128, L252) + the rag (L352).
    make_register("Register", (2.90, 4.30, BAR_TOP_Z))
    make_box("Bar_Rag", (2.20, 4.35, BAR_TOP_Z + 0.008), (0.20, 0.14, 0.015),
             NOLA_LINEN)
    # Two taps — flat domestic (L40) is all Douglas orders anyway.
    for ti, tx in enumerate([0.20, 0.50]):
        make_cyl(f"Tap_{ti}_Stem", (tx, 4.32, BAR_TOP_Z + 0.14), 0.020, 0.28,
                 P.METAL_STEEL)
        make_box(f"Tap_{ti}_Handle", (tx, 4.32, BAR_TOP_Z + 0.34),
                 (0.05, 0.05, 0.14), [NOLA_CYPRESS_DK, COL_VINYL_OX][ti])


def build_backbar():
    """Bottle shelves against the N wall + the long mirror — the
    cheap bar glass Joanna flickers in (L144). Mirror is an opaque
    pale slab (no transparency in this pipeline), brass-framed."""
    make_box("Backbar_Ledge", (BAR_CX, 5.70, 1.02), (4.60, 0.30, 0.05),
             NOLA_CYPRESS)
    make_box("Backbar_Mirror", (BAR_CX, 5.875, 1.90), (4.70, 0.02, 1.20),
             COL_MIRROR)
    make_box("Backbar_MirrorFrame_T", (BAR_CX, 5.87, 2.53), (4.78, 0.03, 0.05),
             NOLA_BRASS)
    make_box("Backbar_MirrorFrame_B", (BAR_CX, 5.87, 1.27), (4.78, 0.03, 0.05),
             NOLA_BRASS)
    for fsgn in (-1, +1):
        make_box(f"Backbar_MirrorFrame_{fsgn:+d}",
                 (BAR_CX + fsgn * 2.39, 5.87, 1.90), (0.05, 0.03, 1.26),
                 NOLA_BRASS)
    tints = [COL_BOTTLE_AMBER, COL_BOTTLE_GREEN, COL_BOTTLE_BROWN,
             COL_BOTTLE_CLEAR]
    for shf, sz in enumerate([1.48, 1.86, 2.24]):
        make_box(f"Backbar_Shelf_{shf}", (BAR_CX, 5.72, sz), (4.60, 0.24, 0.03),
                 NOLA_CYPRESS)
        for bi in range(14):
            bx = -1.10 + bi * 0.31
            tint = tints[(shf + bi) % 4]
            make_cyl(f"Bottle_{shf}_{bi}_Body", (bx, 5.72, sz + 0.11),
                     0.034, 0.19, tint, segments=8)
            make_cyl(f"Bottle_{shf}_{bi}_Neck", (bx, 5.72, sz + 0.25),
                     0.013, 0.09, tint, segments=6)


def build_bar_tv():
    """The bar TV, muted (L40): green field, neon-ghost players, a
    black-and-gold score bug — the Saints behind, again (L356).
    Wall-mounted high on the N wall east of the mirror's midline."""
    make_box("TV_MountPlate", (2.4, 5.88, 2.96), (0.16, 0.04, 0.14), NOLA_IRON)
    make_box("TV_MountArm", (2.4, 5.82, 2.92), (0.06, 0.14, 0.05), NOLA_IRON)
    make_box("TV_Bezel", (2.4, 5.72, 2.78), (0.85, 0.09, 0.52), COL_TV_DARK)
    make_box("TV_Screen", (2.4, 5.665, 2.77), (0.74, 0.015, 0.40), COL_TV_FIELD)
    # Ghosts in pads chasing an electronic pigskin (L40).
    ghosts = [(-0.26, +0.06, COL_CIG_PAPER), (-0.14, -0.04, COL_TV_GOLD),
              (-0.02, +0.08, COL_CIG_PAPER), (+0.10, -0.02, COL_TV_DARK),
              (+0.20, +0.05, COL_TV_GOLD), (+0.28, -0.06, COL_CIG_PAPER)]
    for gi, (gx, gz, gc) in enumerate(ghosts):
        make_box(f"TV_Ghost_{gi}", (2.4 + gx, 5.652, 2.77 + gz),
                 (0.030, 0.006, 0.045), gc)
    # Score bug, bottom of frame — behind by ten (L356).
    make_box("TV_ScoreBug", (2.35, 5.652, 2.595), (0.60, 0.006, 0.05),
             COL_TV_DARK)
    make_box("TV_ScoreBug_Home", (2.12, 5.649, 2.595), (0.08, 0.005, 0.035),
             COL_TV_GOLD)
    make_box("TV_ScoreBug_Away", (2.58, 5.649, 2.595), (0.08, 0.005, 0.035),
             COL_CIG_PAPER)


def build_neon_signs():
    """Three beer neons, two for brands the bar no longer carries
    (L40). All three lit, all three buzzing. The RED one hangs over
    the booth — the light the ouroboros tattoo returns (L68)."""
    # 1 · The live brand: red neon RING on the W wall over the booth
    #     (a circle — the sign the tattoo answers).
    make_box("Neon_Red_Board", (-4.375, 5.0, 2.15), (0.05, 0.85, 0.62),
             COL_BOARD)
    make_cyl("Neon_Red_Ring", (-4.34, 5.0, 2.20), 0.21, 0.03, COL_NEON_RED,
             axis='X', segments=16)
    make_cyl("Neon_Red_Ring_Hole", (-4.335, 5.0, 2.20), 0.15, 0.035,
             COL_BOARD, axis='X', segments=16)
    make_box("Neon_Red_Underline", (-4.335, 5.0, 1.86), (0.03, 0.55, 0.035),
             COL_NEON_RED)
    # 2 · Defunct brand, amber, dustier board — over the mirror.
    make_box("Neon_Amber_Board", (0.2, 5.86, 2.76), (0.85, 0.05, 0.36),
             COL_BOARD_DUST)
    make_box("Neon_Amber_Tube", (0.2, 5.825, 2.82), (0.65, 0.03, 0.05),
             COL_NEON_AMBER)
    make_box("Neon_Amber_Tube2", (0.2, 5.825, 2.70), (0.40, 0.03, 0.04),
             COL_NEON_AMBER)
    # 3 · Defunct brand, green, dusty board — E wall.
    make_box("Neon_Green_Board", (4.375, 3.2, 2.30), (0.05, 0.80, 0.42),
             COL_BOARD_DUST)
    make_box("Neon_Green_Tube", (4.34, 3.2, 2.34), (0.03, 0.60, 0.04),
             COL_NEON_GREEN)
    for vi, vy in enumerate([2.95, 3.45]):
        make_box(f"Neon_Green_Vert_{vi}", (4.34, vy, 2.22),
                 (0.03, 0.04, 0.18), COL_NEON_GREEN)


def build_jukebox():
    """SE-corner jukebox — kept from the scaffold (the .tscn's
    Fill_JukeboxGlow is named for it), but dark and silent tonight:
    'The silence in the bar felt louder now' (L204). Rounded arch
    top per the eye-level cylinder rule; display opaque."""
    jx, jy = 3.85, 1.05
    make_box("Jukebox_Body", (jx, jy, 0.70), (0.78, 0.55, 1.40),
             (0.50, 0.28, 0.13, 1.0))
    make_cyl("Jukebox_Dome", (jx, jy, 1.40), 0.27, 0.78,
             (0.44, 0.24, 0.11, 1.0), axis='X', segments=12)
    make_box("Jukebox_Display", (jx, 0.76, 1.15), (0.60, 0.03, 0.35),
             (0.32, 0.21, 0.13, 1.0))
    # Light columns unlit-warm — the machine is asleep.
    for csgn in (-1, +1):
        make_box(f"Jukebox_LightCol_{csgn:+d}", (jx + csgn * 0.29, 0.765, 0.80),
                 (0.07, 0.03, 0.95), (0.50, 0.34, 0.16, 1.0))
    make_box("Jukebox_Grille", (jx, 0.765, 0.32), (0.50, 0.02, 0.26),
             (0.16, 0.12, 0.10, 1.0))
    make_box("Jukebox_ChromeTrim", (jx, 0.768, 0.50), (0.66, 0.02, 0.03),
             P.METAL_STEEL)
    for ki in range(8):
        make_box(f"Jukebox_Key_{ki}", (jx - 0.245 + ki * 0.07, 0.77, 0.94),
                 (0.05, 0.015, 0.03), COL_CIG_PAPER)


def build_decor():
    # House clock frozen at 11:47 — Refrain 2's hour, shy of another
    # midnight the bartender has already seen too many of (L84).
    make_wall_clock("Clock", (-2.0, 5.88, 2.62), frozen_hour=11, frozen_min=47)
    # Three pendant lamps over the bar — cylinder shades + warm bulb
    # (eye-level rule: no box lampshades). The .tscn key light
    # (Key_PendantAmber) is named for these.
    for pi, px in enumerate([-0.7, 0.9, 2.5]):
        make_cyl(f"Pendant_{pi}_Cord", (px, 4.30, 2.925), 0.006, 0.55,
                 NOLA_IRON, segments=6)
        make_cyl(f"Pendant_{pi}_Shade", (px, 4.30, 2.57), 0.16, 0.18,
                 (0.30, 0.20, 0.12, 1.0), segments=12)
        make_cyl(f"Pendant_{pi}_Bulb", (px, 4.30, 2.44), 0.045, 0.08,
                 (0.95, 0.82, 0.46, 1.0), segments=10)


def build_ceiling_infra():
    # Canon-negative: NO fluorescent troughs (scaffold's removed) —
    # this room is lit by neon, pendants, and the TV. No ceiling
    # fans either; the scene never stages one.
    make_smoke_detector("Smoke", (-2.0, 3.0, CEIL))
    make_ceiling_speaker("Speaker", (2.0, 2.6, CEIL))


def main():
    clear_scene()
    build_shell()
    build_corner_booth()
    build_bar()
    build_backbar()
    build_bar_tv()
    build_neon_signs()
    build_jukebox()
    build_decor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/new_orleans_bar.glb"))
    print(f"\n[build_new_orleans_bar] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
