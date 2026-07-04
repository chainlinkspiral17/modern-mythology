"""VOL 5 · XV The Devil — "Gumbo Limbo" (vol5_ch15_devil.json).
Jimmy Daigle's rented crash-pad apartment, a second-floor French-
Quarter / Marigny walk-up, pre-dawn on a Tuesday — "six twenty-three
AM" (L463), "the thick pre-dawn New Orleans air" (L46), "on a Tuesday
morning" (L567). Jimmy is alone; every other character is a phone
(Q. Paul L266/L308, Antonio L381/L404). "Home sweet temporary hell"
(L46) — a monument to neglect (L58), "a dumpster fire of a life ...
just how he liked it these days" (L58). The morning the operator
learns he is the operated.

ADJUDICATION — same MAN, different PLACE. This Jimmy Daigle IS the
canonical Devil who runs the Gulf-coast bar (Ember & Ash / "Daigle's"
/ Gumbo Limbo) built on Antonio's no-interest loan and who keeps
Antonio's drink on the board for the empty middle stool
(_DAMBROSIO_FAMILY.md L143-147; cosmic_comics.md L82 names him the
Devil). But this apartment is NOT that bar — it is his temporary
rented crash pad, a separate site. The bar's rituals (Antonio's
drink, the vacant stool, the loan history) belong to
build_new_orleans_bar.py's venue AND are POST-Tower grief management:
Antonio is still ALIVE here, phoning Jimmy in this very chapter
(L381, L404-425). So NO Antonio-memorial / empty-stool / bar-drink
prop is staged here — it would be both a wrong-venue import and a
timeline error. The chapter's only bourbon is the warm half-empty
bottle Jimmy drinks alone (L78, L365, L511).

The NOLA_* register below reuses the bar's / room's / office's
constant lines BYTE-IDENTICAL (md5 5b77cdba36eb0b736a10347fcb41bf8a),
repeated by intent as a city-consistency block — NOT a shared-venue
KEEP-IN-SYNC contract. Four separate NOLA sites, one palette register.

Canon dressed in (line numbers = vol5_ch15_devil.json):
  · HERO — the ceiling fan that "wobbled like a dying pelican above
    Jimmy Daigle's head" (L42), stirring the stale air (L46). Built
    frozen mid-wobble: the hub canted off its mount, the four blades
    warped to different heights, the street-facing blade drooping
    lowest (the pelican's dying wing), the pull-chain hanging plumb
    to betray the tilt. The .tscn's Fill_CeilingFan light is named
    for it.
  · The rented sofa he crashed on (L46), springs that groaned (L54):
    a sagging thrift couch, the west cushion crushed where he slept,
    a grimy blanket half kicked to the floor. NOT the scaffold's
    four-poster — he crashed on a SOFA (canon-negative below).
  · The kitchenette, "a monument to neglect" (L58): the sink "full
    of cloudy glasses" (L58), the ashtray "overflowing like a tiny
    toxic volcano" (L58), the "half-empty bottle of something brown
    warming on the counter" left uncapped (L78, L511) with the glass
    he poured a finger into (L365), and the "greasy microwave door"
    he catches the Devil in (L82, L254, L365-369) — its door faced
    into the room so the reflection reads. Formica countertop the
    phone rattled against (L182).
  · Two phones: the buzzing one, screen lit "Q. PAUL" (L266), on the
    formica; and "the second one, the one he kept in a drawer for
    calls he did not, ever, want associated with the first" (L463) —
    in a cracked-open drawer.
  · The street window he "wandered over to" (L190) and looked "Below"
    from (L194): a tall shuttered French window on the far wall, a
    REAL opening (playbook — no glass), folded louver shutters, a
    wrought-iron gallery balcony outside (second floor), and the
    "yellowed lace curtain that disintegrated slightly at his touch"
    (L190) pushed to one side, its hem tattered.
  · His jeans "the same jeans he had been wearing yesterday" with a
    smear on the left thigh (L511) and his boots (L511) crumpled on
    the floor by the sofa — he is in a stained undershirt (L463) at
    scene time and pulls them on at the door.
  · A cheap wall clock frozen at 6:23 — the hour he stood in the
    kitchenette (L463).
Canon-negatives (removed from the scaffold / withheld by canon):
  · NO four-poster canopy bed — he crashed on the rented SOFA (L46).
  · NO elegant armoire — a crash pad; his wardrobe is jeans on the
    floor (L511). Replaced by the neglected galley kitchenette.
  · NO curated faded poster (make_faded_poster) and NO houseplant
    (make_floor_plant) — a "monument to neglect" (L58) is not
    decorated; both scaffold imports dropped.
  · NO Antonio drink / empty stool / bar-loan token (see ADJUDICATION
    — wrong venue AND wrong point in time).
  · NO TV — Jimmy's mirror this morning is the microwave door
    (L82, L254), not a screen.
The loose-chains-that-never-slip register (L38: "the chains are loose.
They could slip free. They do not slip free."; L170, L174, L345,
L571) is staged as MOOD, not a literal prop: the fan wobbles but
never falls, the smoke detector is dead but still screwed to the
ceiling, the uncapped bottle stays uncapped, the door has a knob his
hand can reach — the room could be left and is not. No physical
chains (those live on the card and in the narration, L38).
"""
import os, sys
import math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock
from _props.safety import make_smoke_detector

# Shell footprint — KEPT from the scaffold; the Background3D preset
# ("new_orleans_apartment", camera at the S doorway looking N, fov 62)
# and the .tscn lights (Key_ShutterSun, Fill_CeilingFan, Back_
# BalconyCool) are tuned to it. Camera frames the far (N) street
# window, the wobbling fan overhead, the sofa mid-ground, and the
# neglected kitchenette on the east.
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 3.40

# ── NOLA city register ────────────────────────────────────────────
# City-consistent hues, repeated by intent in build_new_orleans_bar
# .py, build_new_orleans_room.py, build_new_orleans_office.py, and
# this file. NOT a shared-venue block: the bar, the laundromat room,
# the Ember & Ash office, and Daigle's crash pad are four separate
# sites in the same city. Constant lines byte-identical with all
# three siblings (md5 5b77cdba36eb0b736a10347fcb41bf8a).
NOLA_BRASS      = (0.80, 0.60, 0.28, 1.0)   # rails, knobs, finials
NOLA_CYPRESS    = (0.38, 0.26, 0.16, 1.0)   # old-growth trim wood
NOLA_CYPRESS_DK = (0.22, 0.14, 0.09, 1.0)
NOLA_IRON       = (0.17, 0.16, 0.15, 1.0)   # wrought / cast iron
NOLA_LINEN      = (0.84, 0.80, 0.72, 1.0)   # bar rag / bed linen
# ── end city register ─────────────────────────────────────────────

# Apartment-local palette — jaundiced plaster, sticky plank, the
# "bruised purples and sickly greens" leached to grime (L46).
PAL = {"wall": (0.72, 0.64, 0.44, 1.0), "baseboard": (0.30, 0.22, 0.15, 1.0)}
COL_FLOOR = (0.34, 0.24, 0.16, 1.0); COL_SEAM = (0.20, 0.13, 0.09, 1.0)
COL_SCUFF = (0.27, 0.19, 0.12, 1.0)
COL_STICKY = (0.30, 0.23, 0.14, 1.0)        # the sticky sheen (L54)
COL_PLASTER_CEIL = (0.70, 0.62, 0.46, 1.0)
COL_STAIN = (0.56, 0.48, 0.34, 1.0)         # humidity bloom
COL_BRICK = (0.50, 0.32, 0.26, 1.0)         # exposed brick where
COL_BRICK_SEAM = (0.30, 0.20, 0.17, 1.0)    # plaster fell (neglect)
COL_SOFA = (0.36, 0.34, 0.26, 1.0)          # tired olive-brown thrift
COL_SOFA_DK = (0.26, 0.24, 0.18, 1.0)
COL_SOFA_CUSHION = (0.40, 0.37, 0.29, 1.0)
COL_BLANKET = (0.34, 0.30, 0.34, 1.0)       # grimy bruise-purple throw
COL_PILLOW = (0.60, 0.55, 0.46, 1.0)
COL_FORMICA = (0.64, 0.56, 0.40, 1.0)       # grimed formica (L182)
COL_FORMICA_GRIME = (0.44, 0.38, 0.27, 1.0)
COL_CAB = (0.52, 0.44, 0.32, 1.0)           # cheap cabinet ply
COL_CAB_DK = (0.34, 0.28, 0.20, 1.0)
COL_MICRO = (0.15, 0.14, 0.13, 1.0)         # microwave body
COL_MICRO_DOOR = (0.09, 0.09, 0.11, 1.0)    # the greasy door (L82)
COL_MICRO_GREASE = (0.13, 0.13, 0.14, 1.0)  # film across the glass
COL_STEEL = P.METAL_STEEL
COL_GLASS_CLOUDY = (0.58, 0.62, 0.58, 1.0)  # dishwater glass, opaque
COL_BOTTLE = (0.30, 0.18, 0.10, 1.0)        # brown-glass fifth
COL_BOURBON = (0.44, 0.25, 0.11, 1.0)       # the warm liquid (L78)
COL_ASH = (0.55, 0.53, 0.50, 1.0)
COL_ASHTRAY = (0.50, 0.36, 0.22, 1.0)       # amber glass, opaque
COL_BUTT = (0.86, 0.83, 0.75, 1.0)
COL_FILTER = (0.74, 0.58, 0.34, 1.0)
COL_LACE = (0.80, 0.76, 0.56, 1.0)          # yellowed lace (L190)
COL_PHONE = (0.10, 0.10, 0.12, 1.0)
COL_PHONE_LIT = (0.72, 0.74, 0.64, 1.0)     # the "Q. PAUL" screen (L266)
COL_DENIM = (0.34, 0.36, 0.42, 1.0)         # the same jeans (L511)
COL_DENIM_SMEAR = (0.24, 0.22, 0.20, 1.0)   # the smear he won't check
COL_BOOT = (0.24, 0.18, 0.13, 1.0)
COL_FAN_BLADE = NOLA_CYPRESS_DK
COL_FAN_HOUSING = (0.20, 0.18, 0.16, 1.0)
COL_FAN_GLOBE = (0.72, 0.66, 0.48, 1.0)     # grimed light globe
COL_CARDBOARD = (0.56, 0.46, 0.32, 1.0)     # takeout box (L58 clutter)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # W wall (left of frame) — plaster with a fallen-away patch of
    # exposed brick (neglect). E wall carries the kitchenette.
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=-1)
    # N (far) wall carries the street window as a REAL opening (piers
    # + sill band + header around a 1.70 w × 1.80 h hole, z 0.90..2.70;
    # a tall French window). Wall plane y = ROOM_D ± 0.10.
    for psgn, pcx, pw in [(-1, -2.30, 2.80), (+1, +2.30, 2.80)]:
        make_box(f"Wall_N_Pier_{psgn:+d}", (pcx, ROOM_D, CEIL / 2.0),
                 (pw, 0.20, CEIL), PAL["wall"])
    make_box("Wall_N_BelowSill", (0.0, ROOM_D, 0.45), (1.70, 0.20, 0.90),
             PAL["wall"])
    make_box("Wall_N_Header", (0.0, ROOM_D, 3.05), (1.70, 0.20, 0.70),
             PAL["wall"])
    make_box("Wall_N_Base", (0.0, ROOM_D - 0.06, 0.08), (ROOM_W + 0.4, 0.06, 0.16),
             PAL["baseboard"])
    # S wall (camera side): door opening x ∈ [-0.70, +0.70] (the
    # Background3D camera sits in it), framed posts + lintel + header.
    make_wall("Wall_S_W", (-2.20, 0.0, 0), length=3.00, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+2.20, 0.0, 0), length=3.00, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.72), (1.60, 0.20, 1.36),
             PAL["wall"])
    make_box("Door_Lintel", (0.0, 0.0, 2.06), (1.72, 0.24, 0.12), NOLA_CYPRESS_DK)
    for psgn in (-1, +1):
        make_box(f"Door_Post_{psgn:+d}", (psgn * 0.80, 0.0, 1.00),
                 (0.12, 0.24, 2.00), NOLA_CYPRESS_DK)
    # Plaster ceiling — no drop-tile grid in a Quarter walk-up.
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_PLASTER_CEIL},
                 with_grid=False, with_stains=False)
    for si, (sx, sy) in enumerate([(-2.4, 1.4), (2.6, 4.8)]):
        make_box(f"Ceil_Stain_{si}", (sx, sy, CEIL - 0.006), (0.80, 0.75, 0.004),
                 COL_STAIN)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": NOLA_CYPRESS})
    # Exposed brick where the plaster has fallen off the W wall.
    make_box("WallW_BrickPatch", (-ROOM_W / 2.0 + 0.105, 2.5, 1.80),
             (0.02, 2.20, 1.40), COL_BRICK)
    for r in range(6):
        make_box(f"WallW_BrickSeam_{r}", (-ROOM_W / 2.0 + 0.095, 2.5, 1.14 + r * 0.24),
                 (0.006, 2.20, 0.014), COL_BRICK_SEAM)
    for c in range(4):
        make_box(f"WallW_BrickSeamV_{c}", (-ROOM_W / 2.0 + 0.095, 1.6 + c * 0.60, 1.80),
                 (0.006, 0.014, 1.40), COL_BRICK_SEAM)
    # Crumbled plaster lip around the patch (irregular fragments).
    for fi, (fy, fz, fh) in enumerate([(1.36, 1.9, 1.10), (3.64, 2.2, 0.90)]):
        make_box(f"WallW_PlasterLip_{fi}", (-ROOM_W / 2.0 + 0.108, fy, fz),
                 (0.03, 0.10, fh), PAL["wall"])
    # Humidity bloom, E wall above the counter run — worn, not derelict.
    make_box("WallE_Stain", (ROOM_W / 2.0 - 0.105, 4.4, 2.55),
             (0.015, 0.60, 0.45), COL_STAIN)
    # The floor felt sticky; everything felt sticky (L54). Sheen +
    # wear paths door→kitchenette and door→sofa.
    make_box("Floor_Sticky_Kitch", (2.7, 3.4, 0.007), (0.90, 2.60, 0.002), COL_STICKY)
    make_box("Floor_Scuff_Sofa", (-0.4, 1.4, 0.007), (0.70, 2.20, 0.002), COL_SCUFF)
    make_box("Floor_Scuff_Kitch", (1.6, 1.6, 0.007), (2.20, 0.55, 0.002), COL_SCUFF)


def build_street_window():
    """The tall shuttered French window on the N wall Jimmy wanders
    to (L190) and looks Below from (L194). REAL opening (playbook —
    no glass): cypress frame + cross mullion, folded louver shutters,
    a wrought-iron gallery balcony outside (second floor), and the
    yellowed lace curtain pushed to one side, hem gone to lace-dust
    at a touch (L190)."""
    wy = ROOM_D
    # Frame around the opening (x ∈ [-0.85,+0.85], z 0.90..2.70).
    make_box("Win_Head", (0.0, wy, 2.74), (1.86, 0.26, 0.08), NOLA_CYPRESS)
    for jsgn in (-1, +1):
        make_box(f"Win_Jamb_{jsgn:+d}", (jsgn * 0.855, wy, 1.80),
                 (0.09, 0.26, 1.80), NOLA_CYPRESS)
    make_box("Win_Sill_In", (0.0, wy - 0.14, 0.88), (1.86, 0.16, 0.06), NOLA_CYPRESS)
    make_box("Win_Sill_Out", (0.0, wy + 0.13, 0.87), (1.86, 0.10, 0.05), NOLA_CYPRESS)
    # Cross mullion (two lights over two) — no glass behind it.
    make_box("Win_MullV", (0.0, wy, 1.80), (0.05, 0.10, 1.72), NOLA_CYPRESS_DK)
    make_box("Win_MullH", (0.0, wy, 1.80), (1.62, 0.10, 0.05), NOLA_CYPRESS_DK)
    # Folded louver shutters against the piers (street side, +Y).
    for ssgn, snm in ((-1, "L"), (+1, "R")):
        scx = ssgn * 1.05
        make_box(f"Shutter_{snm}_Panel", (scx, wy + 0.15, 1.80),
                 (0.34, 0.05, 1.72), NOLA_CYPRESS_DK)
        for li in range(8):
            make_box(f"Shutter_{snm}_Louver_{li}", (scx, wy + 0.185, 1.06 + li * 0.20),
                     (0.28, 0.02, 0.05), NOLA_CYPRESS)
    # Wrought-iron gallery balcony outside the sill — the street is
    # DOWN there (L194); this is a second floor.
    make_cyl("Gallery_TopRail", (0.0, wy + 0.42, 1.40), 0.020, 1.80,
             NOLA_IRON, axis='X', segments=8)
    make_cyl("Gallery_MidRail", (0.0, wy + 0.42, 1.02), 0.014, 1.80,
             NOLA_IRON, axis='X', segments=6)
    for pi, px in enumerate([-0.78, -0.52, -0.26, 0.0, 0.26, 0.52, 0.78]):
        make_cyl(f"Gallery_Picket_{pi}", (px, wy + 0.42, 1.14), 0.010, 0.62,
                 NOLA_IRON, segments=6)
    # A couple of cast scroll curls (French Quarter iron).
    for csgn in (-1, +1):
        make_cyl(f"Gallery_Scroll_{csgn:+d}", (csgn * 0.65, wy + 0.42, 1.32),
                 0.07, 0.03, NOLA_IRON, axis='Y', segments=10)
    # Yellowed lace curtain, pushed to the west side, bunched, hem
    # tattered (L190). Opaque — the pipeline can't do sheer.
    make_box("Lace_Bunched", (-0.55, wy - 0.16, 1.80), (0.34, 0.05, 1.66), COL_LACE)
    make_box("Lace_Gather", (-0.42, wy - 0.14, 1.80), (0.14, 0.06, 1.66), COL_LACE)
    for ti, tx in enumerate([-0.66, -0.48, -0.34]):
        make_box(f"Lace_Tatter_{ti}", (tx, wy - 0.16, 1.02 - ti * 0.03),
                 (0.05, 0.04, 0.10), COL_LACE)


def build_sofa():
    """The rented sofa he crashed on (L46), springs groaning (L54):
    a sagging thrift couch mid-room facing the street window, the
    west cushion crushed where he slept, the grimy blanket half
    kicked toward the floor. This is his bed — NOT a four-poster
    (canon-negative)."""
    sx, sy = -0.50, 2.60                     # sofa center; faces +Y (N)
    make_box("Sofa_Base", (sx, sy, 0.20), (1.95, 0.92, 0.40), COL_SOFA_DK)
    # Seat cushions — east one intact, west one crushed / sprung.
    make_box("Sofa_Cushion_E", (sx + 0.48, sy + 0.02, 0.47),
             (0.90, 0.80, 0.14), COL_SOFA_CUSHION)
    make_box("Sofa_Cushion_W", (sx - 0.48, sy + 0.02, 0.43),
             (0.90, 0.80, 0.10), COL_SOFA_CUSHION)  # dipped springs
    # Low back on the S side (camera sees over it to the crash).
    make_box("Sofa_Back", (sx, sy - 0.36, 0.68), (1.95, 0.20, 0.62), COL_SOFA)
    make_box("Sofa_BackCushion", (sx, sy - 0.28, 0.62), (1.82, 0.16, 0.42),
             COL_SOFA_CUSHION)
    for asgn, anm in ((-1, "W"), (+1, "E")):
        make_box(f"Sofa_Arm_{anm}", (sx + asgn * 0.95, sy, 0.52),
                 (0.20, 0.92, 0.66), COL_SOFA)
    for li, (lx, ly) in enumerate([(sx - 0.85, sy - 0.38), (sx + 0.85, sy - 0.38),
                                    (sx - 0.85, sy + 0.38), (sx + 0.85, sy + 0.38)]):
        make_cyl(f"Sofa_Foot_{li}", (lx, ly, 0.03), 0.03, 0.06,
                 NOLA_CYPRESS_DK, segments=6)
    # The blanket, half thrown off (L46 crash) — offset mass, a fold
    # ridge, and a corner kicked over the front edge toward the floor.
    make_box("Sofa_Blanket", (sx - 0.30, sy + 0.08, 0.53), (1.10, 0.72, 0.10),
             COL_BLANKET)
    make_box("Sofa_Blanket_Fold", (sx - 0.52, sy + 0.28, 0.57), (0.55, 0.20, 0.10),
             COL_BLANKET)
    make_box("Sofa_Blanket_Kicked", (sx - 0.18, sy + 0.52, 0.34),
             (0.40, 0.16, 0.32), COL_BLANKET)
    # The pillow he crashed on, squashed at the east end.
    make_box("Sofa_Pillow", (sx + 0.58, sy + 0.02, 0.55), (0.34, 0.46, 0.12),
             COL_PILLOW)
    # His jeans + boots on the floor by the west arm (L511) — he's in
    # a stained undershirt at scene time and pulls them on at the door.
    make_box("Jeans_Pile", (sx - 1.35, sy + 0.20, 0.07), (0.44, 0.34, 0.10),
             COL_DENIM)
    make_box("Jeans_Leg", (sx - 1.55, sy - 0.15, 0.05), (0.16, 0.42, 0.07),
             COL_DENIM)
    make_box("Jeans_Smear", (sx - 1.30, sy + 0.16, 0.121), (0.10, 0.12, 0.004),
             COL_DENIM_SMEAR)  # the smear on the left thigh (L511)
    for bsgn, bnm in ((-1, "L"), (+1, "R")):
        bxo = sx - 1.55 + bsgn * 0.14
        make_box(f"Boot_{bnm}_Shaft", (bxo, sy - 0.55, 0.11), (0.11, 0.13, 0.22),
                 COL_BOOT)
        make_box(f"Boot_{bnm}_Toe", (bxo, sy - 0.44, 0.05), (0.11, 0.16, 0.09),
                 COL_BOOT)
    # A grease-stained takeout box on the floor (L58 dumpster fire).
    make_box("Takeout_Box", (sx + 1.05, sy + 0.70, 0.05), (0.34, 0.30, 0.08),
             COL_CARDBOARD)
    make_box("Takeout_Lid", (sx + 1.05, sy + 0.70, 0.095), (0.30, 0.26, 0.01),
             COL_CARDBOARD)


def _stack_bottle(prefix, cx, cy, base_z, *, fill=0.42):
    """A brown-glass fifth, half-empty and warming (L78): a darker
    lower body (liquid) and a paler upper body (empty), uncapped
    (L511)."""
    body_h = 0.22
    liq_h = body_h * fill
    make_cyl(f"{prefix}_Empty", (cx, cy, base_z + liq_h + (body_h - liq_h) / 2.0),
             0.045, body_h - liq_h, COL_BOTTLE, segments=10)
    make_cyl(f"{prefix}_Liquid", (cx, cy, base_z + liq_h / 2.0),
             0.045, liq_h, COL_BOURBON, segments=10)
    make_cyl(f"{prefix}_Neck", (cx, cy, base_z + body_h + 0.06),
             0.016, 0.12, COL_BOTTLE, segments=8)   # uncapped (L511)


def build_kitchenette():
    """The kitchenette, "a monument to neglect" (L58), on the E wall.
    The sink of cloudy glasses, the overflowing ashtray, the warm
    uncapped bourbon, and the greasy microwave door Jimmy meets the
    Devil in (L82, L254, L365-369) — its door turned into the room
    so the reflection reads to the camera."""
    ex = ROOM_W / 2.0                        # E wall face at +3.5
    ccx = ex - 0.42                          # counter center x
    # Cabinet carcass + formica top + toe kick + backsplash.
    make_box("Kitch_Cabinet", (ccx, 3.95, 0.44), (0.66, 3.30, 0.88), COL_CAB)
    make_box("Kitch_Counter", (ccx - 0.03, 3.95, 0.90), (0.72, 3.34, 0.05),
             COL_FORMICA)
    make_box("Kitch_Counter_Grime", (ccx - 0.06, 2.9, 0.926), (0.55, 0.80, 0.003),
             COL_FORMICA_GRIME)
    make_box("Kitch_Kick", (ex - 0.30, 3.95, 0.05), (0.40, 3.26, 0.10), COL_CAB_DK)
    make_box("Kitch_Backsplash", (ex - 0.105, 3.95, 1.20), (0.02, 3.34, 0.55),
             COL_FORMICA_GRIME)
    # Cabinet doors + brass pulls.
    for di, dy in enumerate([3.10, 4.10, 4.90]):
        make_box(f"Kitch_Door_{di}", (ex - 0.755, dy, 0.46), (0.02, 0.90, 0.80),
                 COL_CAB_DK)
        make_cyl(f"Kitch_Pull_{di}", (ex - 0.775, dy + 0.36, 0.46), 0.012, 0.05,
                 NOLA_BRASS, axis='X', segments=6)
    # The second phone's drawer, cracked open (L463) — the front
    # pulled proud of the counter face, a dark phone on its floor.
    make_box("Kitch_Drawer_Front", (ex - 0.80, 3.60, 0.74), (0.05, 0.66, 0.16),
             COL_CAB_DK)
    make_cyl("Kitch_Drawer_Pull", (ex - 0.83, 3.60, 0.74), 0.012, 0.05,
             NOLA_BRASS, axis='X', segments=6)
    make_box("Phone2_Body", (ex - 0.66, 3.60, 0.685), (0.05, 0.08, 0.15), COL_PHONE)
    # Upper cabinet, E wall above the counter.
    make_box("Kitch_Upper", (ex - 0.24, 4.55, 2.15), (0.34, 1.30, 0.62), COL_CAB)
    for ui, uy in enumerate([4.20, 4.90]):
        make_box(f"Kitch_UpperDoor_{ui}", (ex - 0.415, uy, 2.15),
                 (0.02, 0.62, 0.58), COL_CAB_DK)
        make_cyl(f"Kitch_UpperPull_{ui}", (ex - 0.435, uy + 0.24, 2.02),
                 0.011, 0.04, NOLA_BRASS, axis='X', segments=6)
    # The sink "full of cloudy glasses" (L58) — steel basin recessed
    # in the counter, dishwater glasses upright and toppled inside.
    make_box("Kitch_Sink_Basin", (ccx, 4.70, 0.86), (0.50, 0.60, 0.12), COL_STEEL,
             open_faces={'+Z'})
    for gi, (gx, gy, up) in enumerate([(-0.10, 4.58, True), (0.08, 4.62, True),
                                        (-0.02, 4.80, True), (0.12, 4.78, False),
                                        (-0.12, 4.86, True)]):
        if up:
            make_cyl(f"Kitch_Glass_{gi}", (ccx + gx, gy, 0.90), 0.036, 0.10,
                     COL_GLASS_CLOUDY, segments=8)
        else:                                # one glass on its side
            make_cyl(f"Kitch_Glass_{gi}", (ccx + gx, gy, 0.875), 0.036, 0.10,
                     COL_GLASS_CLOUDY, axis='X', segments=8)
    # Gooseneck faucet at the back of the sink.
    make_cyl("Kitch_Faucet_Stem", (ex - 0.16, 5.00, 1.02), 0.014, 0.24, COL_STEEL)
    make_cyl("Kitch_Faucet_Neck", (ex - 0.28, 5.00, 1.14), 0.013, 0.26, COL_STEEL,
             axis='X', segments=6)
    make_cyl("Kitch_Faucet_Spout", (ex - 0.40, 5.00, 1.06), 0.012, 0.12, COL_STEEL)
    # Two-burner hotplate at the north end.
    make_box("Kitch_Stove_Top", (ccx, 5.35, 0.94), (0.58, 0.52, 0.04), COL_CAB_DK)
    for bi, (bx, by) in enumerate([(-0.13, 5.25), (0.13, 5.45)]):
        make_cyl(f"Kitch_Burner_{bi}", (ccx + bx, by, 0.965), 0.10, 0.012,
                 (0.14, 0.13, 0.12, 1.0), segments=10)
    # The greasy microwave, its DOOR turned into the room (-X face) so
    # the Devil's reflection reads (L82, L254, L365-369).
    mx, my = ccx - 0.02, 2.98
    make_box("Micro_Body", (mx, my, 1.05), (0.46, 0.42, 0.30), COL_MICRO)
    make_box("Micro_Door", (mx - 0.24, my - 0.06, 1.05), (0.02, 0.30, 0.24),
             COL_MICRO_DOOR)
    make_box("Micro_Grease", (mx - 0.252, my - 0.06, 1.03), (0.006, 0.26, 0.20),
             COL_MICRO_GREASE)   # the greasy film he meets himself in
    make_box("Micro_Panel", (mx - 0.24, my + 0.14, 1.05), (0.02, 0.10, 0.24),
             COL_MICRO)
    # The half-empty bottle warming on the counter + the glass he
    # poured a finger of bourbon into (L78, L365).
    _stack_bottle("Bottle", ccx + 0.04, 2.42, 0.925, fill=0.42)
    make_cyl("Tumbler_Glass", (ccx - 0.16, 2.66, 0.965), 0.036, 0.09,
             COL_GLASS_CLOUDY, segments=8)
    make_cyl("Tumbler_Bourbon", (ccx - 0.16, 2.66, 0.945), 0.032, 0.03,
             COL_BOURBON, segments=8)      # a finger, warming (L365)
    # The ashtray "overflowing like a tiny toxic volcano" (L58) — a
    # mounded amber tray spilling butts onto the formica.
    ax_, ay_ = ccx + 0.10, 3.30
    make_cyl("Ashtray_Body", (ax_, ay_, 0.935), 0.075, 0.03, COL_ASHTRAY,
             segments=12)
    make_cyl("Ashtray_Mound", (ax_, ay_, 0.965), 0.058, 0.05, COL_ASH, segments=12)
    butts = [(0.00, 0.00, 'Z'), (0.03, 0.02, 'Z'), (-0.02, 0.03, 'Z'),
             (0.09, -0.02, 'X'), (-0.10, -0.05, 'X'), (0.05, -0.11, 'Y')]
    for bi, (bx, by, bax) in enumerate(butts):
        make_cyl(f"Ashtray_Butt_{bi}", (ax_ + bx, ay_ + by, 0.985), 0.006, 0.05,
                 COL_BUTT, axis=bax, segments=6)
        make_cyl(f"Ashtray_Filter_{bi}", (ax_ + bx, ay_ + by, 0.985), 0.0062, 0.012,
                 COL_FILTER, axis=bax, segments=6)
    # The buzzing phone on the formica, screen lit "Q. PAUL" (L266).
    make_box("Phone1_Body", (ccx - 0.20, 3.85, 0.928), (0.05, 0.09, 0.16), COL_PHONE)
    make_box("Phone1_Screen", (ccx - 0.226, 3.85, 0.930), (0.004, 0.075, 0.14),
             COL_PHONE_LIT)


def build_ceiling_fan():
    """HERO — the fan that "wobbled like a dying pelican above Jimmy
    Daigle's head" (L42), stirring the stale air (L46). Built frozen
    mid-wobble: the hub canted off its mount, the four blades warped
    to four different heights, the street-facing (N) blade drooping
    lowest — the dying wing — and the pull-chain hanging plumb to
    betray the tilt. No rotation helper exists, so the wobble is sold
    by the warped blade disc + the off-axis hub, not a tilt matrix."""
    mcx, mcy = -0.50, 2.60                   # over the sofa (his head)
    # Ceiling canopy (mount).
    make_cyl("Fan_Canopy", (mcx, mcy, CEIL - 0.05), 0.09, 0.10, COL_FAN_HOUSING,
             segments=10)
    # Downrod — hub sits offset from the canopy (the lean); the rod
    # drops to the offset hub, reading off-plumb against the canopy.
    hcx, hcy = mcx + 0.07, mcy + 0.05        # hub laterally offset
    make_cyl("Fan_Downrod", ((mcx + hcx) / 2.0, (mcy + hcy) / 2.0, CEIL - 0.26),
             0.018, 0.34, COL_FAN_HOUSING, segments=8)
    hub_z = CEIL - 0.48
    make_cyl("Fan_Hub", (hcx, hcy, hub_z), 0.16, 0.12, COL_FAN_HOUSING, segments=12)
    # Four blades, axis-aligned arms at N/S/E/W, each warped to a
    # different height — the disc is visibly non-planar (the wobble).
    # N (street-facing) blade droops lowest: the dying pelican wing.
    blade_specs = [
        # dx,   dy,   z_off,  size_x, size_y   (arm points outward)
        (0.00,  0.46, -0.14, 0.13, 0.66),    # N — drooping wing
        (0.00, -0.46, +0.06, 0.13, 0.66),    # S
        (0.46,  0.00, +0.02, 0.66, 0.13),    # E
        (-0.46, 0.00, -0.05, 0.66, 0.13),    # W
    ]
    for bi, (dx, dy, zo, bxw, byw) in enumerate(blade_specs):
        bz = hub_z + zo
        make_box(f"Fan_Blade_{bi}", (hcx + dx, hcy + dy, bz), (bxw, byw, 0.02),
                 COL_FAN_BLADE)
        # Outer paddle drooping a touch lower than its arm.
        pdx = dx * 1.55
        pdy = dy * 1.55
        make_box(f"Fan_Paddle_{bi}", (hcx + pdx, hcy + pdy, bz - 0.03),
                 (bxw * 0.9 if bxw > byw else 0.20,
                  byw * 0.9 if byw > bxw else 0.20, 0.015), COL_FAN_BLADE)
    # Grimed light globe under the hub — the .tscn Fill_CeilingFan is
    # named for the fixture. Opaque; the pipeline can't do glass.
    make_cyl("Fan_GlobeCollar", (hcx, hcy, hub_z - 0.10), 0.06, 0.05,
             COL_FAN_HOUSING, segments=10)
    make_cyl("Fan_Globe", (hcx, hcy, hub_z - 0.18), 0.10, 0.14, COL_FAN_GLOBE,
             segments=12)
    # Pull-chain hangs PLUMB from the hub — its verticality against
    # the canted fan is what sells the wobble.
    make_cyl("Fan_PullChain", (hcx + 0.11, hcy, hub_z - 0.26), 0.004, 0.30,
             P.METAL_STEEL, segments=6)
    make_cyl("Fan_PullBead", (hcx + 0.11, hcy, hub_z - 0.44), 0.012, 0.03,
             NOLA_BRASS, segments=8)


def build_decor():
    # A cheap wall clock, N wall east pier, frozen at 6:23 — the hour
    # he stood in the kitchenette (L463). Faces -Y into the room.
    make_wall_clock("Clock", (2.0, ROOM_D - 0.10, 2.30), frozen_hour=6,
                    frozen_min=23, palette={"face": (0.80, 0.76, 0.62, 1.0),
                                            "rim": (0.30, 0.26, 0.22, 1.0)})
    # A cheap light switch plate by the door (grimy).
    make_box("SwitchPlate", (0.86, 0.10, 1.20), (0.02, 0.08, 0.13),
             (0.68, 0.62, 0.50, 1.0))


def build_ceiling_infra():
    """Loose-chains register (L38): the smoke detector is dead but
    still screwed to the ceiling — the room could be made safe and is
    not. Battery cover hanging open, off to one side of the fan."""
    make_smoke_detector("Smoke", (2.4, 1.6, CEIL))
    make_box("Smoke_CoverHang", (2.55, 1.6, CEIL - 0.10), (0.08, 0.10, 0.02),
             (0.72, 0.70, 0.64, 1.0))
    make_cyl("Smoke_CoverWire", (2.50, 1.6, CEIL - 0.05), 0.003, 0.10,
             P.METAL_BLACK, segments=6)


def main():
    clear_scene()
    build_shell()
    build_street_window()
    build_sofa()
    build_kitchenette()
    build_ceiling_fan()
    build_decor()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/new_orleans_apartment.glb"))
    print(f"\n[build_new_orleans_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
