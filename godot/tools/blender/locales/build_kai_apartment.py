"""Kai's apartment — vol7 hero locale (Smolvud, OR).

A second-storey walk-up on the south side of town, four blocks
from Board Lords (vol7_ch16_aud: "He walked the four blocks
home", past the alley behind The Salty Tome), reached by BACK
STAIRS off a small rear lot (vol7_ch18_stick: "He pulled into
the small lot behind his apartment ... carried the crow up the
back stairs"). South is the town's direction here per
vol7_ch12_kai: "South was the direction of Cape Perpetua, the
Starfish Nebula, Kai's apartment, Tem's apartment".

BINDING GROUND TRUTH (playbook wave-8 rule — grep before
planning): `3d:kai_apartment` is bound by THREE scenes, and two
of them stage FINN, not Kai:
  · vol7_ch16_aud (tail) — KAI's Saturday evening: the shower,
    "the rest of Hans's bread from the loaf ... in a paper bag",
    the dark-green long-sleeve thermal his grandmother gave him
    "at the bottom of his drawer", the kitchen table + the glass
    of water, and "The clock on the kitchen wall said seven
    oh-eight" — the clock is BAKED AT 7:08 (grease-clock rule).
  · vol7_ch18_home — Finn waking from Tideline Survey: the bed +
    wool blanket, the reader on the side table, the chair beside
    the bed the crow watches from, the kitchen phone he calls
    Tem on (set down, walked away from, picked back up — a
    corded wall phone), the closet with the wax canvas coat on
    its hook, the handkerchiefs in the dresser.
  · vol7_ch18_stick (tail) — Finn at the kitchen table with
    Brandon's stick: coffee at nine, two slices of Hans's bread,
    the compact reader "he had bought from Cale in '49", the cap
    from the side-table drawer, the wool blanket, the chair
    beside the bed.
The catalog says Kai; the ch18 bindings render Finn's morning
here. This build therefore keeps the dressing to the shared
coastal-walk-up register BOTH stagings need (kitchen table, Hans
bread, cone + kettle coffee, wall phone, bed + wool blanket +
side-table reader + bedside chair, dresser, closet coat) and
signs the room as KAI's with owner traces no prose contradicts.

KAI OWNER TRACES (canon-first):
  · Skater since age fourteen (lore/_VOL7_WIKI.md §cast) — his
    daily deck stood by the door, trucks to the wall; his first
    deck hung on the west wall like the relic it is; spare
    wheels, wax puck and a skate tool on a small shelf. The
    repair habit comes home only this far — a tool roll, not a
    bench (the lathe, the maple, the clamps and the glue syringe
    all live at the shop, vol7_ch9_tuesday).
  · The shop keys on their own hook by the door (he locked the
    front door early, flipped OPEN to CLOSED — vol7_ch16_aud).
  · The chipped Tidewater mug lives at Board Lords
    (vol7_ch9_tuesday); its SIBLING sits on Kai's table —
    same glaze constant, repeated by intent (wave-8 city-
    register pattern).
  · Board Lords teal shows up only in small goods (beanie, deck
    art, skate tool) — brand panels and inventory stay at the
    shop.

CANON-NEGATIVES (deliberate absences):
  · NO crow, NO stick, NO waxed-paper sleeve, NO Brandon
    notebook baked — they move through the ch18 scenes (bag →
    table → reader; chair-back → table → shoulder). The reader
    cap lives IN the side-table drawer (ch18_stick), so only the
    drawer is baked.
  · NO Kestrel Mountain bowl — it rides in Kai's shirt pocket
    (vol7_ch16_aud); baking it would contradict every exit.
  · NO dark-green thermal in view — Kai puts it ON at 7:08 and
    wears it out; its drawer (dresser, bottom) is baked ajar.
  · NO taped-together radio, NO bottle-cap saucer — those are
    Finn's-apartment signatures (static_truths.md); duplicating
    them here would conflate the two sets.
  · NO deck wall / register / bearings boxes / zine rack — shop
    vocabulary stays at the shop (vol7_ch12_kai puts the
    cardboard bearings boxes in the BACK OFFICE, not here).
  · NO fluorescents (scaffold had two) — a home, not retail;
    warm pendant + flush domes instead (Finn-pass lesson).
  · NO TV / stereo — the town register's rooms are quiet; the
    sound here is the town at four-forty and rain.

Shell footprint kept from the scaffold (4.5 × 5.0 m, CEIL 2.6,
door gap in the south wall x −1..+1) — the .tscn lights and the
Background3D camera preset (0, 2.30, +0.5 / yaw 180 / fov 60,
same preset family as finn_apartment / lena_apartment) are tuned
to it. Windows are REAL OPENINGS with fir frames + mullions, NO
glass (playbook no-transparency rule). Bedroom is a small annex
north of the main room, door parked open (finn/lena annex
grammar — same-town walk-ups rhyme, documented as intent). The
kitchen window looks down at the back lot (Kai's car —
cannery.md Act III travel: "or in Kai's car" — the back stairs,
the fence); the west window looks at the street and the facade
across it.

Text panels baked as named vertex-color meshes for scene-side
Label3D: FirstDeck_ArtPanel, Poster_Contest_Panel,
Poster_Gig_Panel, Reader_Screen.

KEEP IN SYNC (byte-identical constants, repeated by intent):
  · COL_BL_TEAL / COL_TIDEWATER / COL_DECK_WOOD / COL_GRIP ↔
    build_board_lords_interior.py (the shop's register).
  · COL_RAINCOAT ↔ build_lena_apartment.py ("wax canvas — town
    uniform").
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_crown_molding, make_door_hinges
from _props.decor import make_wall_clock
from _props.safety import make_smoke_detector

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 4.5; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.80, 0.82, 0.76, 1.0),   # cool sage plaster
            "baseboard": (0.34, 0.26, 0.18, 1.0)}
COL_FLOOR = (0.60, 0.46, 0.30, 1.0)            # fir boards
COL_SEAM  = (0.36, 0.26, 0.17, 1.0)

# ── Kai palette (skater's spare warmth, PNW coastal) ─────────────
COL_WOOD      = (0.44, 0.32, 0.20, 1.0)
COL_WOOD_DARK = (0.26, 0.19, 0.13, 1.0)
COL_WOOD_LT   = (0.60, 0.47, 0.30, 1.0)
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_CREAM     = (0.90, 0.87, 0.80, 1.0)
COL_LINEN     = (0.88, 0.85, 0.78, 1.0)
COL_ENAMEL    = (0.84, 0.85, 0.83, 1.0)
COL_CAST_IRON = (0.13, 0.13, 0.14, 1.0)
COL_GLASSISH  = (0.72, 0.78, 0.78, 1.0)   # opaque stand-in (water glass)
# KEEP IN SYNC with build_board_lords_interior.py ─ shop register
COL_BL_TEAL   = (0.30, 0.52, 0.46, 1.0)   # shop brand
COL_TIDEWATER = (0.62, 0.72, 0.76, 1.0)   # the Tidewater glaze
COL_DECK_WOOD = (0.72, 0.58, 0.40, 1.0)   # natural maple deck
COL_GRIP      = (0.14, 0.13, 0.14, 1.0)
# KEEP IN SYNC with build_lena_apartment.py ─ town uniform
COL_RAINCOAT  = (0.38, 0.36, 0.26, 1.0)   # wax canvas coat
COL_RUST      = (0.78, 0.42, 0.22, 1.0)   # deck-tint rust (accent)
COL_FLANNEL   = (0.50, 0.28, 0.22, 1.0)
COL_DENIM     = (0.30, 0.36, 0.46, 1.0)
COL_BEANIE    = COL_BL_TEAL               # shop-teal wool beanie
COL_GUM_SOLE  = (0.62, 0.48, 0.32, 1.0)   # skate-shoe sole
COL_SHOE_UP   = (0.24, 0.23, 0.24, 1.0)
COL_BOOT      = (0.24, 0.22, 0.20, 1.0)
COL_BLANKET   = (0.26, 0.27, 0.28, 1.0)   # charcoal wool blanket
COL_BLANKBAND = COL_BL_TEAL               # its teal band
COL_QUILT     = (0.42, 0.46, 0.42, 1.0)   # spare blanket, closet shelf
COL_READER    = (0.16, 0.16, 0.18, 1.0)   # compact SCUMM reader
COL_READLIGHT = (0.86, 0.70, 0.44, 1.0)
COL_KRAFT     = (0.74, 0.56, 0.34, 1.0)   # Hans's paper bag
COL_BREAD     = (0.76, 0.58, 0.36, 1.0)   # the loaf's crust
COL_BREAD_CUT = (0.90, 0.84, 0.68, 1.0)
COL_MUG_CHAR  = (0.28, 0.27, 0.26, 1.0)
COL_HANKIE    = (0.92, 0.91, 0.87, 1.0)
COL_SIDING    = (0.47, 0.49, 0.45, 1.0)   # weathered cedar lap siding
COL_SIDING_DK = (0.34, 0.36, 0.33, 1.0)
COL_TRIM_EXT  = (0.30, 0.32, 0.30, 1.0)
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.15, 0.15, 0.16, 1.0)
COL_GRAVEL    = (0.48, 0.45, 0.40, 1.0)
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_FENCE     = (0.42, 0.36, 0.28, 1.0)
COL_CAR       = (0.55, 0.34, 0.20, 1.0)   # Kai's faded-rust hatchback
COL_CAR_DK    = (0.38, 0.24, 0.15, 1.0)
COL_GLASS_DK  = (0.10, 0.11, 0.13, 1.0)   # dark opaque "glass" panels
COL_WARM_WIN  = (0.86, 0.70, 0.44, 1.0)   # lit windows across the way
COL_CEIL      = (0.82, 0.79, 0.72, 1.0)   # painted plank ceiling
COL_BATTEN    = (0.52, 0.42, 0.30, 1.0)
COL_GLOW_WARM = (0.98, 0.88, 0.62, 1.0)
COL_PHONE     = (0.86, 0.84, 0.78, 1.0)   # almond corded wall phone

COUNTER_TOP = 0.92
STREET_Z = -3.30                    # street / lot grade (rooms above)
# Bedroom annex north of the main room (doorway x −1.75..−0.85)
ANX_X0, ANX_X1 = -2.15, -0.55       # interior extents
ANX_Y0, ANX_Y1 = ROOM_D + 0.10, ROOM_D + 2.10
ANX_CEIL = 2.45


# ═════════════════════════════════════════════════════════════════
# Local helpers (deterministic; helpers don't auto-port — playbook)
# ═════════════════════════════════════════════════════════════════
_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _chair(prefix, cx, cy, facing, tint):
    """Spindle-back kitchen chair; `facing` = way the sitter faces.
    The top slat is a crow-perch height (~0.86) — ch18_home."""
    dx, dy = _DIRS[facing]
    make_box(f"{prefix}_Seat", (cx, cy, 0.45), (0.40, 0.40, 0.04), tint)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"{prefix}_Leg_{li}", (cx + sx * 0.16, cy + sy * 0.16, 0.225),
                 0.018, 0.45, COL_WOOD_DARK)
    bx, by = cx - dx * 0.19, cy - dy * 0.19
    for pi, sgn in enumerate((-1, +1)):
        px = bx + (sgn * 0.16 if dx == 0 else 0.0)
        py = by + (sgn * 0.16 if dy == 0 else 0.0)
        make_cyl(f"{prefix}_BackPost_{pi}", (px, py, 0.675), 0.016, 0.45, tint)
    slat_sz = (0.36, 0.03, 0.08) if dx == 0 else (0.03, 0.36, 0.08)
    for si, sz_z in enumerate((0.70, 0.86)):
        make_box(f"{prefix}_Slat_{si}", (bx, by, sz_z), slat_sz, tint)


def _mug(prefix, cx, cy, bz, tint):
    make_cyl(f"{prefix}_Body", (cx, cy, bz + 0.048), 0.038, 0.095, tint)
    make_box(f"{prefix}_Handle", (cx + 0.048, cy, bz + 0.050),
             (0.016, 0.014, 0.05), tint)


def _flush_dome(prefix, cx, cy, ceil_z):
    make_cyl(f"{prefix}_Base", (cx, cy, ceil_z - 0.015), 0.09, 0.03, COL_BRASS,
             segments=12)
    make_cyl(f"{prefix}_Dome", (cx, cy, ceil_z - 0.055), 0.075, 0.05,
             (0.96, 0.92, 0.80, 1.0), segments=12)


def _skate_shoe(prefix, cx, cy, heel_facing_sign):
    """Low skate shoe on the floor, toe toward -Y when sign=+1."""
    make_box(f"{prefix}_Sole", (cx, cy, 0.016), (0.10, 0.27, 0.032), COL_GUM_SOLE)
    make_box(f"{prefix}_Upper", (cx, cy + heel_facing_sign * 0.02, 0.062),
             (0.092, 0.21, 0.06), COL_SHOE_UP)
    make_box(f"{prefix}_Toe", (cx, cy - heel_facing_sign * 0.095, 0.048),
             (0.092, 0.07, 0.035), COL_GUM_SOLE)


# ═════════════════════════════════════════════════════════════════
# SHELL — scaffold footprint. South wall keeps the scaffold door
# gap (x −1..+1, entry at the top of the back stairs); west wall
# gets the street-window opening; north wall gets the bedroom
# doorway + the kitchen window over the counter (the back lot
# below). Painted plank ceiling + battens (top floor).
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # South wall — scaffold door gap kept; infill either side of
    # the 0.95 m door leaf
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             PAL_WALL["wall"])
    for nm, fx in [("Wall_S_FillW", -0.775), ("Wall_S_FillE", +0.775)]:
        make_box(nm, (fx, 0.0, 1.15), (0.45, 0.20, 2.30), PAL_WALL["wall"])
    # East wall — full height; bathroom door + kitchen wall phone
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # West wall — street-window opening y 2.6..3.8, z 0.95..2.25
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 1.20, 0), length=2.80, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 4.50, 0), length=1.40, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_Sill", (-ROOM_W / 2.0, 3.2, 0.475), (0.20, 1.20, 0.95),
             PAL_WALL["wall"])
    make_box("Wall_W_Header", (-ROOM_W / 2.0, 3.2, 2.425), (0.20, 1.20, 0.35),
             PAL_WALL["wall"])
    # North wall — bedroom doorway x −1.75..−0.85; kitchen window
    # x 0.55..1.65 (z 1.0..2.2, over the counter, back lot below)
    make_wall("Wall_N_W", (-2.10, ROOM_D, 0), length=0.70, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_M", (-0.15, ROOM_D, 0), length=1.40, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (2.05, ROOM_D, 0), length=0.80, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveBedDoor", (-1.30, ROOM_D, 2.35), (0.90, 0.20, 0.50),
             PAL_WALL["wall"])
    make_box("Wall_N_WinSill", (1.10, ROOM_D, 0.50), (1.10, 0.20, 1.00),
             PAL_WALL["wall"])
    make_box("Wall_N_WinHeader", (1.10, ROOM_D, 2.40), (1.10, 0.20, 0.40),
             PAL_WALL["wall"])
    # Painted plank ceiling + battens (top floor of the building)
    make_box("Ceil_Plane", (0.0, ROOM_D / 2.0, CEIL + 0.05),
             (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), COL_CEIL)
    for bi, bx in enumerate((-1.8, -0.9, 0.0, 0.9, 1.8)):
        make_box(f"Ceil_Batten_{bi}", (bx, ROOM_D / 2.0, CEIL - 0.008),
                 (0.05, ROOM_D + 0.4, 0.016), COL_BATTEN)
    # Crown molding
    make_crown_molding("Crown_W", wall_x=-ROOM_W / 2.0 + 0.10, wall_y=ROOM_D / 2.0,
                       length=ROOM_D, axis='Y', ceil_z=CEIL,
                       palette={"wood": COL_WOOD})
    make_crown_molding("Crown_E", wall_x=+ROOM_W / 2.0 - 0.10, wall_y=ROOM_D / 2.0,
                       length=ROOM_D, axis='Y', ceil_z=CEIL,
                       palette={"wood": COL_WOOD})
    make_crown_molding("Crown_N", wall_x=0.0, wall_y=ROOM_D - 0.10,
                       length=ROOM_W - 0.2, axis='X', ceil_z=CEIL,
                       palette={"wood": COL_WOOD})
    make_crown_molding("Crown_S", wall_x=0.0, wall_y=0.10,
                       length=ROOM_W - 0.2, axis='X', ceil_z=CEIL,
                       palette={"wood": COL_WOOD})


# ═════════════════════════════════════════════════════════════════
# WINDOWS — real openings, fir frames + mullions, NO glass
# (playbook no-transparency rule). West = street window; north =
# the kitchen window over the counter, back lot below.
# ═════════════════════════════════════════════════════════════════
def build_windows():
    # West street window: opening y 2.6..3.8, z 0.95..2.25
    wx = -ROOM_W / 2.0
    make_box("WinW_Sill", (wx, 3.2, 0.915), (0.22, 1.32, 0.07), COL_WOOD)
    make_box("WinW_Ledge", (wx + 0.14, 3.2, 0.955), (0.14, 1.20, 0.03), COL_WOOD)
    make_box("WinW_Head", (wx, 3.2, 2.285), (0.22, 1.32, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinW_Jamb_{sgn:+d}", (wx, 3.2 + sgn * 0.63, 1.60),
                 (0.22, 0.06, 1.44), COL_WOOD)
    make_box("WinW_MeetRail", (wx, 3.2, 1.60), (0.14, 1.20, 0.06), COL_WOOD)
    make_box("WinW_MullLo", (wx, 3.2, 1.275), (0.12, 0.05, 0.59), COL_WOOD)
    make_box("WinW_MullHi", (wx, 3.2, 1.93), (0.12, 0.05, 0.59), COL_WOOD)
    make_cyl("WinW_SashLock", (wx + 0.12, 3.2, 1.645), 0.020, 0.02, COL_BRASS)
    # North kitchen window: opening x 0.55..1.65, z 1.0..2.2
    wy = ROOM_D
    make_box("WinN_Sill", (1.10, wy, 0.965), (1.22, 0.22, 0.07), COL_WOOD)
    make_box("WinN_Ledge", (1.10, wy - 0.14, 1.005), (1.10, 0.14, 0.03), COL_WOOD)
    make_box("WinN_Head", (1.10, wy, 2.235), (1.22, 0.22, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinN_Jamb_{sgn:+d}", (1.10 + sgn * 0.58, wy, 1.60),
                 (0.06, 0.22, 1.34), COL_WOOD)
    make_box("WinN_MeetRail", (1.10, wy, 1.62), (1.10, 0.14, 0.06), COL_WOOD)
    make_box("WinN_MullLo", (1.10, wy, 1.30), (0.05, 0.12, 0.58), COL_WOOD)
    make_box("WinN_MullHi", (1.10, wy, 1.94), (0.05, 0.12, 0.58), COL_WOOD)


# ═════════════════════════════════════════════════════════════════
# ENTRY — the door at the top of the back stairs (ch18_stick). The
# shop keys on their own hook (he locked the front door early,
# ch16_aud). Hooks east of the door: flannel jacket + the teal
# beanie; one peg left empty (the coat he's wearing is with him).
# The DAILY DECK stood by the wall west of the door, trucks in;
# skate shoes + rain boots on the drip tray.
# ═════════════════════════════════════════════════════════════════
def build_entry():
    make_box("Door_Leaf", (0.0, 0.04, 1.03), (0.95, 0.06, 2.06), COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"Door_Panel_{pi}", (0.0, 0.075, 0.62 + pi * 0.85),
                 (0.68, 0.012, 0.62), COL_WOOD)
    make_box("Door_HeadTrim", (0.0, 0.10, 2.12), (1.14, 0.06, 0.10), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"Door_JambTrim_{sgn:+d}", (sgn * 0.53, 0.10, 1.05),
                 (0.08, 0.06, 2.10), COL_WOOD)
    make_cyl("Door_Knob", (0.38, 0.10, 0.98), 0.028, 0.05, COL_BRASS, axis='Y')
    make_box("Door_Deadbolt", (0.38, 0.10, 1.14), (0.05, 0.05, 0.07), COL_BRASS)
    make_door_hinges("Door_Hinge", edge_x=-0.46, edge_y=0.08,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    make_box("Doormat", (0.0, 0.72, 0.010), (0.90, 0.55, 0.014), P.RUBBER_MAT)
    # Coat hooks east of the door — flannel, beanie, one empty peg
    make_box("Hooks_Rail", (1.55, 0.13, 1.62), (0.80, 0.03, 0.09), COL_WOOD)
    for hi, hx in enumerate((1.27, 1.57, 1.87)):
        make_cyl(f"Hooks_Peg_{hi}", (hx, 0.185, 1.60), 0.013, 0.09,
                 COL_BRASS, axis='Y')
    make_box("Flannel_Body", (1.27, 0.235, 1.27), (0.34, 0.08, 0.68), COL_FLANNEL)
    make_box("Flannel_Collar", (1.27, 0.245, 1.645), (0.22, 0.09, 0.10),
             COL_FLANNEL)
    make_box("Flannel_Stripe", (1.27, 0.278, 1.05), (0.32, 0.012, 0.05), COL_CREAM)
    make_box("Beanie_Crown", (1.57, 0.225, 1.56), (0.15, 0.09, 0.10), COL_BEANIE)
    make_box("Beanie_Fold", (1.57, 0.235, 1.505), (0.16, 0.10, 0.035), COL_BEANIE)
    # The shop keys — their own small hook west of the door
    make_cyl("Keys_Hook", (-0.75, 0.165, 1.38), 0.010, 0.07, COL_BRASS, axis='Y')
    make_cyl("Keys_ShopRing", (-0.75, 0.205, 1.33), 0.032, 0.008,
             P.METAL_STEEL, axis='Y', segments=12)
    for ki, kx in enumerate((-0.77, -0.73)):
        make_box(f"Keys_Key_{ki}", (kx, 0.205, 1.275), (0.016, 0.006, 0.075),
                 COL_BRASS if ki == 0 else P.METAL_STEEL)
    # THE DAILY DECK — stood on its tail west of the door, trucks
    # toward the wall (skater since fourteen, _VOL7_WIKI)
    make_box("DailyDeck_Board", (-1.45, 0.175, 0.41), (0.215, 0.030, 0.80),
             COL_DECK_WOOD)
    make_box("DailyDeck_Grip", (-1.45, 0.192, 0.41), (0.20, 0.004, 0.76), COL_GRIP)
    for ti, tz in enumerate((0.20, 0.62)):
        make_box(f"DailyDeck_Truck_{ti}", (-1.45, 0.145, tz), (0.16, 0.035, 0.06),
                 P.METAL_STEEL)
        for wi, sgn in enumerate((-1, +1)):
            make_cyl(f"DailyDeck_Wheel_{ti}_{wi}", (-1.45 + sgn * 0.085, 0.125, tz),
                     0.028, 0.030, COL_CREAM, axis='Y', segments=12)
    # Drip tray east of the door — skate shoes + rain boots
    make_box("ShoeTray", (1.62, 0.46, 0.012), (0.62, 0.40, 0.018), P.RUBBER_MAT)
    _skate_shoe("Shoe_L", 1.44, 0.46, +1)
    _skate_shoe("Shoe_R", 1.57, 0.44, +1)
    for bi, bx in enumerate((1.74, 1.88)):
        make_cyl(f"Boot_{bi}_Shaft", (bx, 0.50, 0.17), 0.048, 0.26, COL_BOOT,
                 segments=12)
        make_box(f"Boot_{bi}_Foot", (bx, 0.40, 0.045), (0.10, 0.24, 0.09), COL_BOOT)


# ═════════════════════════════════════════════════════════════════
# KITCHEN — NE corner. Counter + sink under the back-lot window,
# small enamel range + kettle, compact fridge, open shelf (mugs +
# plates), THE CONE (coffee at nine, ch18_stick), HANS'S BREAD in
# its paper bag with the loaf end on the board (ch16_aud +
# ch18_stick both eat it), THE WALL CLOCK AT 7:08 (ch16_aud), and
# the corded WALL PHONE Finn calls Tem on (ch18_home — set down,
# walked away, picked back up: it stays on the wall).
# ═════════════════════════════════════════════════════════════════
def build_kitchen():
    wy = ROOM_D
    # Counter x 0.30..1.60 under the window
    make_box("Counter_Body", (0.95, wy - 0.38, 0.44), (1.30, 0.56, 0.88), COL_WOOD)
    make_box("Counter_Top", (0.95, wy - 0.40, COUNTER_TOP - 0.025),
             (1.38, 0.62, 0.05), COL_WOOD_LT)
    make_box("Counter_Kick", (0.95, wy - 0.67, 0.09), (1.30, 0.02, 0.18),
             COL_WOOD_DARK)
    for ci, cx in enumerate((0.62, 1.28)):
        make_box(f"Counter_CabDoor_{ci}", (cx, wy - 0.675, 0.50),
                 (0.50, 0.015, 0.66), COL_WOOD_LT)
        make_cyl(f"Counter_CabKnob_{ci}", (cx + (0.18 if ci == 0 else -0.18),
                 wy - 0.69, 0.58), 0.014, 0.03, COL_BRASS, axis='Y')
    # Compact sink under the window + faucet
    make_box("Sink_Basin", (1.10, wy - 0.38, 0.885), (0.42, 0.34, 0.08),
             P.METAL_STEEL, open_faces={'+Z'})
    make_box("Sink_BasinFloor", (1.10, wy - 0.38, 0.850), (0.40, 0.32, 0.01),
             (0.42, 0.44, 0.46, 1.0))
    make_cyl("Sink_FaucetRiser", (1.10, wy - 0.22, 1.02), 0.014, 0.20, P.METAL_STEEL)
    make_cyl("Sink_FaucetSpout", (1.10, wy - 0.30, 1.11), 0.012, 0.16,
             P.METAL_STEEL, axis='Y')
    # THE CONE + a mug at the counter's west end ("He made coffee
    # at nine", ch18_stick)
    _mug("ConeMug", 0.46, wy - 0.36, COUNTER_TOP, COL_MUG_CHAR)
    make_cyl("ConeFilter_Upper", (0.46, wy - 0.36, 1.075), 0.058, 0.06, COL_CREAM)
    make_cyl("ConeFilter_Lower", (0.46, wy - 0.36, 1.030), 0.034, 0.03, COL_CREAM)
    make_box("CoffeeBag", (0.30, wy - 0.24, 1.010), (0.11, 0.08, 0.18),
             (0.34, 0.22, 0.14, 1.0))
    # HANS'S BREAD — the paper bag standing open, the loaf end on
    # the board with the knife (ch16_aud: "the rest of Hans's
    # bread from the loaf ... in a paper bag"; ch18_stick: "two
    # slices of Hans's bread he had taken home last night")
    make_box("HansBag_Body", (0.74, wy - 0.30, 1.025), (0.14, 0.11, 0.21),
             COL_KRAFT)
    make_box("HansBag_FoldTop", (0.74, wy - 0.30, 1.145), (0.15, 0.12, 0.030),
             (0.66, 0.48, 0.28, 1.0))
    make_box("BreadBoard", (1.38, wy - 0.32, 0.938), (0.32, 0.24, 0.016),
             COL_WOOD_LT)
    make_cyl("BreadLoaf_End", (1.34, wy - 0.32, 0.995), 0.052, 0.15, COL_BREAD,
             axis='X', segments=12)
    make_cyl("BreadLoaf_CutFace", (1.415, wy - 0.32, 0.995), 0.048, 0.006,
             COL_BREAD_CUT, axis='X', segments=12)
    make_box("BreadKnife_Blade", (1.44, wy - 0.44, 0.950), (0.020, 0.15, 0.006),
             P.METAL_STEEL)
    make_box("BreadKnife_Handle", (1.44, wy - 0.545, 0.952), (0.024, 0.06, 0.014),
             COL_WOOD_DARK)
    for cr, (ox, oy) in enumerate([(-0.10, 0.07), (0.06, 0.10)]):
        make_box(f"BreadCrumb_{cr}", (1.38 + ox, wy - 0.32 + oy, 0.950),
                 (0.014, 0.010, 0.005), COL_BREAD_CUT)
    # Open shelf west of the window — mugs + plates + a tin
    make_box("KitchenShelf", (0.26, wy - 0.16, 1.58), (0.52, 0.26, 0.03), COL_WOOD)
    for ki, sgn in enumerate((-1, +1)):
        make_box(f"KitchenShelf_Bracket_{ki}", (0.26 + sgn * 0.20, wy - 0.06, 1.50),
                 (0.03, 0.09, 0.13), P.METAL_BLACK)
    _mug("ShelfMug_0", 0.12, wy - 0.16, 1.595, COL_RUST)
    _mug("ShelfMug_1", 0.30, wy - 0.16, 1.595, COL_CREAM)
    for pi in range(2):
        make_cyl(f"ShelfPlate_{pi}", (0.44, wy - 0.16, 1.615 + pi * 0.018),
                 0.075, 0.014, COL_CREAM, segments=12)
    make_cyl("ShelfTin", (0.26, wy - 0.16, 1.70), 0.040, 0.10, P.METAL_STEEL)
    # Small enamel range in the NE corner + the kettle
    make_box("Range_Body", (1.88, wy - 0.38, 0.45), (0.50, 0.56, 0.90), COL_ENAMEL)
    make_box("Range_OvenDoor", (1.88, wy - 0.665, 0.42), (0.42, 0.015, 0.48),
             COL_ENAMEL)
    make_cyl("Range_OvenHandle", (1.88, wy - 0.685, 0.68), 0.013, 0.36,
             P.METAL_STEEL, axis='X')
    make_box("Range_Cooktop", (1.88, wy - 0.38, 0.915), (0.50, 0.56, 0.03),
             COL_ENAMEL)
    for ki in range(2):
        make_cyl(f"Range_Knob_{ki}", (1.78 + ki * 0.20, wy - 0.665, 0.85),
                 0.018, 0.025, COL_CAST_IRON, axis='Y')
    for bi, by in enumerate((wy - 0.50, wy - 0.26)):
        make_cyl(f"Range_Burner_{bi}", (1.88, by, 0.935), 0.068, 0.012,
                 COL_CAST_IRON, segments=12)
    make_cyl("Kettle_Body", (1.88, wy - 0.50, 1.010), 0.082, 0.14, P.METAL_STEEL,
             segments=12)
    make_cyl("Kettle_Lid", (1.88, wy - 0.50, 1.09), 0.052, 0.02, P.METAL_STEEL)
    make_cyl("Kettle_Knob", (1.88, wy - 0.50, 1.11), 0.013, 0.02, COL_WOOD_DARK)
    make_box("Kettle_Spout", (1.88, wy - 0.59, 1.00), (0.018, 0.07, 0.018),
             P.METAL_STEEL)
    make_box("Kettle_Handle", (1.88, wy - 0.50, 1.105), (0.02, 0.03, 0.08),
             COL_CAST_IRON)
    # Compact fridge against the east wall south of the range
    make_box("Fridge_Body", (1.87, 3.55, 0.625), (0.56, 0.52, 1.25), COL_ENAMEL)
    make_box("Fridge_DoorSeam", (1.87, 3.288, 0.625), (0.50, 0.008, 1.17),
             (0.62, 0.63, 0.61, 1.0))
    make_cyl("Fridge_Handle", (1.66, 3.28, 0.80), 0.012, 0.34, P.METAL_STEEL)
    make_box("Fridge_Vent", (1.87, 3.30, 0.035), (0.46, 0.015, 0.05),
             P.METAL_BLACK)
    # THE WALL CLOCK — baked at SEVEN OH-EIGHT (ch16_aud: "The
    # clock on the kitchen wall said seven oh-eight. He had to
    # leave in forty minutes.")
    make_wall_clock("KitchenClock", (-0.15, wy - 0.12, 2.02),
                    frozen_hour=7, frozen_min=8,
                    palette={"face": COL_CREAM, "rim": COL_WOOD_DARK})
    # THE WALL PHONE — corded, on the east wall by the kitchen
    # (ch18_home: "He went to the kitchen. He called the cabin's
    # landline ... He set the phone down ... went back to the
    # phone. He picked it up.")
    px = ROOM_W / 2.0 - 0.10
    make_box("Phone_Body", (px - 0.035, 3.95, 1.42), (0.07, 0.17, 0.26), COL_PHONE)
    make_box("Phone_Keypad", (px - 0.075, 3.95, 1.38), (0.012, 0.10, 0.13),
             (0.70, 0.68, 0.62, 1.0))
    make_box("Phone_Handset", (px - 0.095, 3.95, 1.535), (0.055, 0.155, 0.055),
             COL_PHONE)
    make_box("Phone_Cradle", (px - 0.075, 3.95, 1.505), (0.02, 0.06, 0.02),
             COL_PHONE)
    for si, sz in enumerate((1.30, 1.22, 1.14)):
        make_cyl(f"Phone_CordLoop_{si}", (px - 0.05, 3.87, sz), 0.020, 0.012,
                 COL_PHONE, axis='X', segments=8)


# ═════════════════════════════════════════════════════════════════
# THE TABLE — the kitchen table of all three bindings: Kai's glass
# of water at seven oh-eight (ch16_aud); Brandon's stick opened
# on it, the crow standing on the sleeve (ch18_stick — the stick,
# sleeve and crow move, so only the table is baked). The Tidewater
# SIBLING mug sits here (the chipped one lives at Board Lords,
# ch9_tuesday — same glaze, repeated by intent).
# ═════════════════════════════════════════════════════════════════
def build_table():
    tx, ty = 0.40, 2.70
    make_box("Table_Top", (tx, ty, 0.735), (0.95, 0.70, 0.04), COL_WOOD)
    make_box("Table_Apron", (tx, ty, 0.685), (0.80, 0.55, 0.06), COL_WOOD_DARK)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Table_Leg_{li}", (tx + sx * 0.40, ty + sy * 0.28, 0.345),
                 (0.05, 0.05, 0.69), COL_WOOD_DARK)
    _chair("TableChair_S", tx, ty - 0.62, 'N', COL_WOOD_LT)   # the sitter's
    _chair("TableChair_N", tx, ty + 0.62, 'S', COL_WOOD_DARK) # across (perch)
    # The glass of water (ch16_aud) + the Tidewater sibling mug
    make_cyl("WaterGlass", (0.20, 2.56, 0.80), 0.028, 0.09, COL_GLASSISH)
    _mug("TidewaterMug_Home", 0.62, 2.84, 0.755, COL_TIDEWATER)
    # Braided rug under the table — three flattened rings
    for ri, (rr, rt) in enumerate([(0.80, (0.34, 0.36, 0.34, 1.0)),
                                   (0.56, COL_BL_TEAL),
                                   (0.32, (0.62, 0.52, 0.38, 1.0))]):
        make_cyl(f"TableRug_Ring_{ri}", (0.40, 2.70, 0.006 + ri * 0.003),
                 rr, 0.008, rt, segments=16)


# ═════════════════════════════════════════════════════════════════
# SKATE WALL (west) — the owner traces. THE FIRST DECK from '34-
# era hung on pegs like the relic it is (skater since fourteen,
# _VOL7_WIKI §cast); two flyers; the small shelf with wax puck,
# spare wheels, skate tool and the canvas tool roll. The repair
# HABIT comes home; the repair BENCH stays at the shop
# (vol7_ch9_tuesday: lathe, maple, clamps, glue syringe).
# ═════════════════════════════════════════════════════════════════
def build_skate_wall():
    wx = -ROOM_W / 2.0 + 0.10        # interior face of the west wall
    # The first deck — hung horizontal on two wooden pegs
    for pi, py in enumerate((2.05, 2.65)):
        make_cyl(f"FirstDeck_Peg_{pi}", (wx + 0.045, py, 1.80), 0.014, 0.09,
                 COL_WOOD_DARK, axis='X')
    make_box("FirstDeck_Board", (wx + 0.10, 2.35, 1.90), (0.030, 0.80, 0.215),
             COL_DECK_WOOD)
    # Underside art faces the room — teal field, cream stripe
    make_box("FirstDeck_ArtPanel", (wx + 0.117, 2.35, 1.90), (0.005, 0.72, 0.19),
             COL_BL_TEAL)
    make_box("FirstDeck_ArtStripe", (wx + 0.121, 2.35, 1.90), (0.004, 0.72, 0.045),
             COL_CREAM)
    for ti, sgn in enumerate((-1, +1)):
        make_box(f"FirstDeck_Truck_{ti}", (wx + 0.145, 2.35 + sgn * 0.24, 1.90),
                 (0.035, 0.06, 0.15), P.METAL_STEEL)
        for wi, wsgn in enumerate((-1, +1)):
            make_cyl(f"FirstDeck_Wheel_{ti}_{wi}",
                     (wx + 0.165, 2.35 + sgn * 0.24, 1.90 + wsgn * 0.082),
                     0.026, 0.028, (0.78, 0.72, 0.52, 1.0), axis='Z', segments=12)
    # Two flyers — a contest flyer and a gig flyer (Label3D
    # targets; lettering is scene-side per the playbook)
    make_box("Poster_Contest_Panel", (wx + 0.005, 1.25, 1.62), (0.008, 0.46, 0.62),
             P.PAPER_AGED)
    make_box("Poster_Contest_Figure", (wx + 0.010, 1.25, 1.74), (0.006, 0.30, 0.30),
             COL_BL_TEAL)
    make_box("Poster_Contest_Band", (wx + 0.010, 1.25, 1.44), (0.006, 0.38, 0.08),
             COL_RUST)
    make_box("Poster_Gig_Panel", (wx + 0.005, 3.95, 1.72), (0.008, 0.36, 0.48),
             COL_CREAM)
    make_box("Poster_Gig_Figure", (wx + 0.010, 3.95, 1.80), (0.006, 0.24, 0.24),
             COL_CAST_IRON)
    # Small skate shelf — wax puck, spare wheels, skate tool, roll
    make_box("SkateShelf", (wx + 0.16, 0.95, 1.12), (0.26, 0.60, 0.03), COL_WOOD)
    for ki, sgn in enumerate((-1, +1)):
        make_box(f"SkateShelf_Bracket_{ki}", (wx + 0.06, 0.95 + sgn * 0.24, 1.04),
                 (0.09, 0.03, 0.13), P.METAL_BLACK)
    make_box("Skate_WaxPuck", (wx + 0.12, 0.74, 1.155), (0.07, 0.07, 0.04),
             (0.92, 0.88, 0.76, 1.0))
    for si in range(2):
        make_cyl(f"Skate_SpareWheels_{si}", (wx + 0.16, 0.90 + si * 0.09, 1.164),
                 0.028, 0.056, COL_CREAM, segments=12)
    make_box("Skate_Tool_T", (wx + 0.14, 1.10, 1.145), (0.10, 0.025, 0.022),
             COL_BL_TEAL)
    make_box("Skate_Tool_Stem", (wx + 0.14, 1.135, 1.145), (0.022, 0.05, 0.022),
             COL_BL_TEAL)
    make_cyl("Skate_ToolRoll", (wx + 0.16, 1.19, 1.165), 0.032, 0.20,
             (0.40, 0.44, 0.32, 1.0), axis='Y', segments=12)


# ═════════════════════════════════════════════════════════════════
# BATHROOM DOOR (east wall) — "He went to the apartment. He
# showered." (ch16_aud). The bathroom itself is beyond the wall;
# the door reads the plumbing into the plan.
# ═════════════════════════════════════════════════════════════════
def build_bathroom_door():
    fx = ROOM_W / 2.0 - 0.10          # interior face of the east wall
    make_box("BathDoor_Leaf", (fx - 0.035, 1.10, 1.02), (0.06, 0.90, 2.04),
             COL_WOOD_DARK)
    make_box("BathDoor_Panel", (fx - 0.070, 1.10, 1.12), (0.012, 0.64, 1.30),
             COL_WOOD)
    make_cyl("BathDoor_Knob", (fx - 0.10, 0.78, 0.98), 0.026, 0.05, COL_BRASS,
             axis='X')
    for sgn in (-1, +1):
        make_box(f"BathDoor_JambTrim_{sgn:+d}", (fx - 0.04, 1.10 + sgn * 0.50, 1.05),
                 (0.06, 0.07, 2.10), COL_WOOD)
    make_box("BathDoor_HeadTrim", (fx - 0.04, 1.10, 2.13), (0.06, 1.07, 0.09),
             COL_WOOD)
    make_box("BathDoor_Threshold", (fx - 0.06, 1.10, 0.012), (0.10, 0.94, 0.02),
             COL_WOOD_LT)


# ═════════════════════════════════════════════════════════════════
# CLOSET — a doorless nook in the NW corner of the main room, west
# of the bedroom doorway. THE WAX CANVAS COAT on its hook
# (ch18_home: "He went to the closet. His own wax canvas coat was
# on the hook."; town-uniform register per lena/finn). A spare
# blanket on the shelf above. One hook empty.
# ═════════════════════════════════════════════════════════════════
def build_closet():
    wy = ROOM_D
    for si, sx in enumerate((-2.22, -1.78)):
        make_box(f"Closet_Side_{si}", (sx, wy - 0.29, 1.15), (0.06, 0.42, 2.30),
                 PAL_WALL["wall"])
    make_box("Closet_Header", (-2.00, wy - 0.29, 2.175), (0.50, 0.42, 0.25),
             PAL_WALL["wall"])
    make_box("Closet_HeadTrim", (-2.00, wy - 0.50, 2.06), (0.52, 0.04, 0.09),
             COL_WOOD)
    make_cyl("Closet_Rail", (-2.00, wy - 0.28, 1.80), 0.014, 0.38, COL_WOOD_DARK,
             axis='X')
    # The wax canvas coat on its hook (a hanger loop on the rail)
    make_box("Closet_CoatHanger", (-2.06, wy - 0.28, 1.735), (0.26, 0.03, 0.02),
             COL_WOOD_DARK)
    make_box("Closet_Coat_Body", (-2.06, wy - 0.28, 1.32), (0.34, 0.10, 0.80),
             COL_RAINCOAT)
    make_box("Closet_Coat_Collar", (-2.06, wy - 0.28, 1.755), (0.22, 0.11, 0.09),
             COL_RAINCOAT)
    make_box("Closet_Coat_StormFlap", (-2.06, wy - 0.335, 1.34), (0.05, 0.012, 0.70),
             (0.32, 0.30, 0.22, 1.0))
    # One empty hook east of the coat
    make_cyl("Closet_EmptyHook", (-1.86, wy - 0.10, 1.76), 0.011, 0.08, COL_BRASS,
             axis='Y')
    # Shelf above the rail — the spare blanket, folded
    make_box("Closet_Shelf", (-2.00, wy - 0.28, 2.02), (0.38, 0.40, 0.025), COL_WOOD)
    make_box("Closet_SpareBlanket", (-2.00, wy - 0.28, 2.085), (0.32, 0.34, 0.10),
             COL_QUILT)
    make_box("Closet_SpareBlanket_Band", (-2.00, wy - 0.46, 2.085),
             (0.32, 0.02, 0.10), COL_RUST)


# ═════════════════════════════════════════════════════════════════
# BEDROOM ANNEX — through the open door in the north wall. The bed
# Finn wakes on under THE WOOL BLANKET (ch18_home), THE COMPACT
# READER on the side table (bought from Cale in '49, used twice —
# ch18_stick) with the cap in the side-table DRAWER (baked
# closed), THE CHAIR BESIDE THE BED (the crow's perch — no crow
# baked, it moves per scene), the dresser with the handkerchiefs
# on top and the BOTTOM DRAWER AJAR — the drawer the dark-green
# thermal lived at the bottom of until 7:08 (ch16_aud).
# ═════════════════════════════════════════════════════════════════
def build_bedroom():
    make_box("Anx_Floor", ((ANX_X0 + ANX_X1) / 2.0, (ANX_Y0 + ANX_Y1) / 2.0, -0.05),
             (ANX_X1 - ANX_X0 + 0.4, ANX_Y1 - ANX_Y0 + 0.3, 0.10), COL_FLOOR)
    make_wall("Anx_Wall_W", (ANX_X0 - 0.10, (ANX_Y0 + ANX_Y1) / 2.0, 0),
              length=ANX_Y1 - ANX_Y0 + 0.4, height=ANX_CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Anx_Wall_E", (ANX_X1 + 0.10, (ANX_Y0 + ANX_Y1) / 2.0, 0),
              length=ANX_Y1 - ANX_Y0 + 0.4, height=ANX_CEIL, axis='Y',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Anx_Wall_N", ((ANX_X0 + ANX_X1) / 2.0, ANX_Y1 + 0.10, 0),
              length=ANX_X1 - ANX_X0 + 0.4, height=ANX_CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Anx_Ceil", ((ANX_X0 + ANX_X1) / 2.0, (ANX_Y0 + ANX_Y1) / 2.0,
             ANX_CEIL + 0.05), (ANX_X1 - ANX_X0 + 0.4, ANX_Y1 - ANX_Y0 + 0.3, 0.10),
             COL_CEIL)
    # Bedroom door — open, parked against the north wall east of
    # the doorway
    make_box("BedDoor_Leaf", (-0.39, ROOM_D - 0.135, 1.02), (0.92, 0.05, 2.04),
             COL_WOOD_DARK)
    make_cyl("BedDoor_Knob", (-0.02, ROOM_D - 0.17, 0.98), 0.026, 0.04, COL_BRASS,
             axis='Y')
    make_door_hinges("BedDoor_Hinge", edge_x=-0.85, edge_y=ROOM_D - 0.12,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    for ti, sgn in enumerate((-1, +1)):
        make_box(f"BedDoor_JambTrim_{ti}", (-1.30 + sgn * 0.51, ROOM_D - 0.13, 1.03),
                 (0.07, 0.05, 2.06), COL_WOOD)
    make_box("BedDoor_HeadTrim", (-1.30, ROOM_D - 0.13, 2.09), (1.10, 0.05, 0.08),
             COL_WOOD)
    # The bed — a low platform against the annex west wall, head
    # north; the charcoal wool blanket with the teal band
    make_box("Bed_Frame", (-1.63, 6.17, 0.15), (1.05, 1.75, 0.12), COL_WOOD_DARK)
    make_box("Bed_Mattress", (-1.63, 6.17, 0.29), (0.98, 1.67, 0.14), COL_LINEN)
    make_box("Bed_Blanket", (-1.63, 5.98, 0.375), (1.00, 1.20, 0.045), COL_BLANKET)
    make_box("Bed_Blanket_Band", (-1.63, 5.60, 0.377), (1.005, 0.12, 0.047),
             COL_BLANKBAND)
    make_box("Bed_Pillow", (-1.63, 6.80, 0.39), (0.50, 0.28, 0.10), COL_LINEN)
    # Side table at the bed's head — THE READER on top (dark
    # plastic, stick slot, status light; Reader_Screen is a
    # Label3D target), the cap in the drawer (drawer baked closed)
    make_box("SideTable_Top", (-0.83, 6.82, 0.55), (0.36, 0.36, 0.03), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"SideTable_Leg_{li}", (-0.83 + sx * 0.15, 6.82 + sy * 0.15, 0.27),
                 (0.035, 0.035, 0.54), COL_WOOD_DARK)
    make_box("SideTable_DrawerFront", (-0.995, 6.82, 0.47), (0.015, 0.28, 0.10),
             COL_WOOD_LT)
    make_cyl("SideTable_DrawerKnob", (-1.008, 6.82, 0.47), 0.012, 0.022, COL_BRASS,
             axis='X')
    make_box("Reader_Body", (-0.83, 6.82, 0.590), (0.17, 0.13, 0.05), COL_READER)
    make_box("Reader_StickSlot", (-0.83, 6.755, 0.598), (0.09, 0.012, 0.018),
             (0.08, 0.08, 0.10, 1.0))
    make_box("Reader_Screen", (-0.83, 6.82, 0.617), (0.11, 0.08, 0.006),
             (0.20, 0.24, 0.26, 1.0))
    make_cyl("Reader_StatusLight", (-0.905, 6.765, 0.617), 0.008, 0.006,
             COL_READLIGHT)
    # THE CHAIR BESIDE THE BED — the crow's perch (ch18_home /
    # ch18_stick); top slat at perch height
    _chair("BedsideChair", -0.86, 6.12, 'W', COL_WOOD_LT)
    # Dresser against the annex east wall — handkerchiefs + folded
    # flannel + jeans on top; BOTTOM DRAWER AJAR (the thermal's
    # drawer, emptied at 7:08)
    make_box("Dresser_Body", (-0.82, 5.42, 0.40), (0.44, 0.62, 0.80), COL_WOOD)
    for di in range(2):
        make_box(f"Dresser_Drawer_{di}", (-0.598, 5.42, 0.64 - di * 0.22),
                 (0.015, 0.50, 0.18), COL_WOOD_LT)
        make_cyl(f"Dresser_Knob_{di}", (-0.585, 5.42, 0.64 - di * 0.22),
                 0.013, 0.025, COL_BRASS, axis='X')
    make_box("Dresser_BottomDrawer_Ajar", (-0.545, 5.42, 0.20),
             (0.12, 0.50, 0.18), COL_WOOD_LT)
    make_box("Dresser_BottomDrawer_Gap", (-0.603, 5.42, 0.20),
             (0.012, 0.46, 0.14), (0.10, 0.08, 0.06, 1.0))
    make_cyl("Dresser_BottomKnob", (-0.480, 5.42, 0.20), 0.013, 0.025, COL_BRASS,
             axis='X')
    make_box("Folded_Flannel", (-0.82, 5.30, 0.83), (0.28, 0.22, 0.05), COL_FLANNEL)
    make_box("Folded_Jeans", (-0.82, 5.56, 0.835), (0.30, 0.24, 0.06), COL_DENIM)
    make_box("Hankie_Stack", (-0.82, 5.42, 0.878), (0.14, 0.14, 0.028), COL_HANKIE)
    # Rug beside the bed + the bedroom's ceiling light (ch18_home:
    # "He held it up to the bedroom's ceiling light")
    make_box("Anx_BedRug", (-1.08, 6.15, 0.006), (0.50, 0.90, 0.012),
             (0.36, 0.40, 0.38, 1.0))
    _flush_dome("Anx_CeilLight", -1.35, 6.15, ANX_CEIL)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — warm pendant over the table, flush dome over the
# kitchen, smoke detector. NO fluorescents (scaffold had two — a
# home, not retail; Finn-pass lesson).
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    make_cyl("Pendant_Canopy", (0.40, 2.70, CEIL - 0.02), 0.05, 0.04, P.METAL_BLACK)
    make_cyl("Pendant_Cord", (0.40, 2.70, CEIL - 0.275), 0.008, 0.55, P.METAL_BLACK)
    make_cyl("Pendant_Shade", (0.40, 2.70, CEIL - 0.615), 0.13, 0.13, COL_RUST,
             segments=12)
    make_cyl("Pendant_Bulb", (0.40, 2.70, CEIL - 0.685), 0.045, 0.035,
             COL_GLOW_WARM)
    _flush_dome("Kitchen_CeilLight", 0.95, 4.35, CEIL)
    make_smoke_detector("Smoke", (-0.7, 2.3, CEIL))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · BACK LOT (north) — "the small lot behind his
# apartment" + "the back stairs" (ch18_stick). Kai's car parked in
# it (cannery.md: Act III travel "or in Kai's car"), the board
# fence, a lot lamp, the neighbor's building beyond. Annex hull-
# wrapped in lap siding per the playbook annex rule.
# ═════════════════════════════════════════════════════════════════
def build_exterior_backlot():
    make_box("Lot_Ground", (0.5, 8.35, STREET_Z - 0.05), (11.0, 3.7, 0.10),
             COL_GRAVEL)
    make_box("Lot_AsphaltPatch", (1.6, 8.0, STREET_Z + 0.002), (3.4, 2.4, 0.004),
             COL_ASPHALT)
    make_box("Lot_Puddle_0", (-0.9, 8.6, STREET_Z + 0.006), (1.10, 0.55, 0.004),
             COL_PUDDLE)
    make_box("Lot_Puddle_1", (3.4, 8.9, STREET_Z + 0.006), (0.70, 0.40, 0.004),
             COL_PUDDLE)
    # Building's north face east of the annex (holds the kitchen
    # window), lap siding + course lines
    make_box("Bldg_LotFace", (1.03, 5.13, -1.62), (2.85, 0.15, 3.36), COL_SIDING)
    for ci in range(3):
        make_box(f"Bldg_LotFace_Course_{ci}", (1.03, 5.21, -0.55 - ci * 0.95),
                 (2.85, 0.02, 0.045), COL_SIDING_DK)
    # Annex hull skin (playbook: every annex gets wrapped) + fill
    make_box("Anx_Skin_W", (-2.45, 6.15, ANX_CEIL / 2.0),
             (0.10, 2.40, ANX_CEIL + 0.2), COL_SIDING)
    make_box("Anx_Skin_N", ((ANX_X0 + ANX_X1) / 2.0, 7.30, ANX_CEIL / 2.0),
             (ANX_X1 - ANX_X0 + 0.7, 0.10, ANX_CEIL + 0.2), COL_SIDING)
    make_box("Anx_Skin_E", (-0.25, 6.15, ANX_CEIL / 2.0),
             (0.10, 2.40, ANX_CEIL + 0.2), COL_SIDING)
    make_box("Anx_Skin_Roof", ((ANX_X0 + ANX_X1) / 2.0, 6.15, ANX_CEIL + 0.22),
             (ANX_X1 - ANX_X0 + 0.9, 2.60, 0.12), COL_TRIM_EXT)
    make_box("Anx_Skin_Under", ((ANX_X0 + ANX_X1) / 2.0, 6.15, -1.62),
             (ANX_X1 - ANX_X0 + 0.6, 2.40, 3.36), COL_SIDING)
    # THE BACK STAIRS — upper landing at the building's NE corner,
    # treads stepping down eastward (solid risers, no floating
    # planks); the run below the sill line is implied
    make_box("BackStairs_Landing", (2.80, 5.75, -0.10), (0.95, 1.05, 0.10),
             COL_FENCE)
    make_box("BackStairs_LandingSkirt", (2.80, 5.75, -0.75), (0.85, 0.95, 1.20),
             COL_SIDING_DK)
    for pi, (px, py) in enumerate([(2.42, 6.22), (3.18, 6.22), (3.18, 5.30)]):
        make_cyl(f"BackStairs_Post_{pi}", (px, py, 0.42), 0.035, 1.00, COL_FENCE)
    make_box("BackStairs_Rail_N", (2.80, 6.22, 0.88), (0.80, 0.05, 0.06), COL_FENCE)
    make_box("BackStairs_Rail_E", (3.18, 5.76, 0.88), (0.05, 0.96, 0.06), COL_FENCE)
    for ti in range(7):
        tx = 3.42 + ti * 0.26
        tz = -0.32 - ti * 0.20
        make_box(f"BackStairs_Tread_{ti}", (tx, 5.75, tz), (0.26, 0.95, 0.045),
                 COL_FENCE)
        make_box(f"BackStairs_Riser_{ti}", (tx, 5.75, tz - 0.12),
                 (0.26, 0.95, 0.20), COL_SIDING_DK)
    # Downspout at the corner between window and stairs
    make_cyl("Downspout_Pipe", (2.38, 5.28, -1.65), 0.045, 3.30, COL_CAST_IRON,
             segments=12)
    make_cyl("Downspout_Shoe", (2.38, 5.42, -3.22), 0.045, 0.28, COL_CAST_IRON,
             axis='Y', segments=12)
    # ── KAI'S CAR in the lot (cannery.md) — faded-rust hatchback ─
    cx, cy = 0.4, 8.05
    make_box("KaiCar_BodyBase", (cx, cy, -2.72), (1.62, 3.55, 0.50), COL_CAR)
    make_box("KaiCar_Cabin", (cx, cy - 0.25, -2.20), (1.50, 1.95, 0.58), COL_CAR)
    make_box("KaiCar_Hood", (cx, cy + 1.35, -2.38), (1.52, 0.85, 0.26), COL_CAR)
    make_box("KaiCar_Hatch", (cx, cy - 1.55, -2.32), (1.50, 0.45, 0.42), COL_CAR_DK)
    make_box("KaiCar_Windshield", (cx, cy + 0.75, -2.10), (1.30, 0.05, 0.38),
             COL_GLASS_DK)
    make_box("KaiCar_RearGlass", (cx, cy - 1.24, -2.12), (1.26, 0.05, 0.32),
             COL_GLASS_DK)
    for wi, sgn in enumerate((-1, +1)):
        make_box(f"KaiCar_SideGlass_{wi}", (cx + sgn * 0.73, cy - 0.25, -2.11),
                 (0.05, 1.40, 0.32), COL_GLASS_DK)
    make_box("KaiCar_Grille", (cx, cy + 1.80, -2.62), (1.24, 0.04, 0.22), COL_CAR_DK)
    for hi, sgn in enumerate((-1, +1)):
        make_cyl(f"KaiCar_Headlight_{hi}", (cx + sgn * 0.55, cy + 1.81, -2.54),
                 0.062, 0.03, COL_CREAM, axis='Y', segments=12)
    for wi, (wx_off, wy_off) in enumerate([(-0.78, -1.15), (0.78, -1.15),
                                           (-0.78, 1.15), (0.78, 1.15)]):
        make_cyl(f"KaiCar_Wheel_{wi}", (cx + wx_off, cy + wy_off, -2.99),
                 0.31, 0.24, COL_CAST_IRON, axis='X', segments=12)
        make_cyl(f"KaiCar_Hub_{wi}", (cx + wx_off * 1.16, cy + wy_off, -2.99),
                 0.09, 0.03, P.METAL_STEEL, axis='X', segments=12)
    make_box("KaiCar_Bumper_R", (cx, cy - 1.82, -2.82), (1.56, 0.08, 0.14),
             P.METAL_STEEL)
    # Lot lamp on a wooden pole at the lot's west edge
    make_cyl("LotLamp_Pole", (-2.60, 8.90, STREET_Z + 2.1), 0.055, 4.20, COL_FENCE,
             segments=12)
    make_box("LotLamp_Head", (-2.60, 8.90, 0.86), (0.30, 0.30, 0.10), P.METAL_BLACK)
    make_cyl("LotLamp_Glow", (-2.60, 8.90, 0.78), 0.070, 0.05, COL_GLOW_WARM,
             segments=12)
    # Board fence along the lot's north edge + posts
    for bi in range(3):
        make_box(f"LotFence_Board_{bi}", (0.5, 9.95, -2.35 + bi * 0.42),
                 (10.6, 0.05, 0.34), COL_FENCE)
    for pi2, px2 in enumerate((-4.2, -1.9, 0.4, 2.7, 5.0)):
        make_cyl(f"LotFence_Post_{pi2}", (px2, 9.98, -2.10), 0.055, 2.40,
                 COL_SIDING_DK, segments=8)
    # The neighbor's building beyond the fence — one window lit
    make_box("Neighbor_Facade", (0.8, 10.9, -0.4), (9.5, 0.20, 6.0),
             (0.22, 0.22, 0.21, 1.0))
    make_box("Neighbor_LitWindow", (-0.9, 10.78, -0.6), (0.60, 0.03, 0.85),
             COL_WARM_WIN)
    make_box("Neighbor_DarkWindow", (2.3, 10.78, -0.5), (0.60, 0.03, 0.85),
             (0.10, 0.10, 0.12, 1.0))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · STREET (west) — the town side, four blocks from the
# shop (ch16_aud). Sidewalk, street, the building's own siding
# face with cornice + ground-floor service door, streetlamp, the
# facade across the street with a few lit windows (evening at
# seven / Sunday morning both read).
# ═════════════════════════════════════════════════════════════════
def build_exterior_street():
    make_box("Street_Sidewalk", (-3.15, 2.5, STREET_Z + 0.03), (1.50, 11.0, 0.08),
             COL_CONCRETE)
    for si in range(5):
        make_box(f"Street_SidewalkSeam_{si}", (-3.15, -1.9 + si * 2.2,
                 STREET_Z + 0.072), (1.50, 0.02, 0.002), (0.40, 0.39, 0.37, 1.0))
    make_box("Street_Curb", (-3.98, 2.5, STREET_Z + 0.04), (0.16, 11.0, 0.12),
             (0.46, 0.45, 0.43, 1.0))
    make_box("Street_Asphalt", (-6.6, 2.5, STREET_Z - 0.05), (5.1, 11.0, 0.10),
             COL_ASPHALT)
    make_box("Street_CenterLine", (-6.6, 2.5, STREET_Z + 0.002), (0.10, 9.0, 0.002),
             (0.70, 0.66, 0.50, 1.0))
    make_box("Street_Puddle_0", (-5.5, 4.2, STREET_Z + 0.004), (1.10, 0.55, 0.004),
             COL_PUDDLE)
    make_box("Street_Puddle_1", (-3.3, 1.0, STREET_Z + 0.077), (0.70, 0.45, 0.004),
             COL_PUDDLE)
    # The building's own west face — lap siding, cornice, a plain
    # ground floor with the service door (nobody's storefront;
    # the kayak shop is Finn's building, not this one)
    make_box("Bldg_StreetFace", (-2.42, 2.5, -1.62), (0.15, 5.9, 3.36), COL_SIDING)
    for ci in range(3):
        make_box(f"Bldg_StreetFace_Course_{ci}", (-2.505, 2.5, -0.55 - ci * 0.95),
                 (0.02, 5.9, 0.045), COL_SIDING_DK)
    make_box("Bldg_Cornice", (-2.52, 2.5, -0.14), (0.30, 5.9, 0.18), COL_TRIM_EXT)
    make_box("Bldg_ServiceDoor", (-2.51, 2.05, -2.32), (0.06, 0.90, 1.96),
             COL_WOOD_DARK)
    make_cyl("Bldg_ServiceDoor_Knob", (-2.555, 1.72, -2.36), 0.024, 0.04, COL_BRASS,
             axis='X')
    make_box("Bldg_ServiceDoor_Stoop", (-2.72, 2.05, STREET_Z + 0.09),
             (0.50, 1.10, 0.10), COL_CONCRETE)
    make_box("Bldg_MeterBox", (-2.53, 3.55, -1.95), (0.10, 0.28, 0.40),
             (0.60, 0.60, 0.58, 1.0))
    # Streetlamp on the buffer strip (playbook: edge of road)
    make_cyl("Streetlamp_Pole", (-4.15, 4.40, STREET_Z + 2.25), 0.045, 4.50,
             P.METAL_BLACK, segments=12)
    make_cyl("Streetlamp_Arm", (-3.95, 4.40, 1.06), 0.022, 0.40, P.METAL_BLACK,
             axis='X')
    make_cyl("Streetlamp_Head", (-3.75, 4.40, 1.00), 0.09, 0.14, P.METAL_BLACK,
             segments=12)
    make_cyl("Streetlamp_Glow", (-3.75, 4.40, 0.91), 0.065, 0.05, COL_GLOW_WARM,
             segments=12)
    # The facade across the street — Saturday evening / Sunday
    # morning both read: two windows warm, three dark
    make_box("Opposite_Facade", (-9.4, 2.5, 0.2), (0.20, 11.0, 7.4),
             (0.20, 0.19, 0.20, 1.0))
    for wi, (wyy, wz) in enumerate([(1.0, 0.6), (4.8, 1.6)]):
        make_box(f"Opposite_LitWindow_{wi}", (-9.28, wyy, wz), (0.02, 0.60, 0.90),
                 COL_WARM_WIN)
    for wi, (wyy, wz) in enumerate([(2.6, 0.5), (3.8, -0.9), (0.6, -1.1)]):
        make_box(f"Opposite_DarkWindow_{wi}", (-9.28, wyy, wz), (0.02, 0.60, 0.90),
                 (0.10, 0.10, 0.12, 1.0))


def main():
    clear_scene()
    build_shell()
    build_windows()
    build_entry()
    build_kitchen()
    build_table()
    build_skate_wall()
    build_bathroom_door()
    build_closet()
    build_bedroom()
    build_ceiling_infra()
    build_exterior_backlot()
    build_exterior_street()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/kai_apartment.glb"))
    print(f"\n[build_kai_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
