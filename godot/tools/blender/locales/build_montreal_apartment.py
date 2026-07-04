"""VOL 5 · Montreal Apartment — JOHN FRANK's Mile-End flat, hero set
for XIV Temperance ("The Moderate Temperature of Tuesday",
vol5_ch14_temperance.json).

ONE-ROOM-TWO-CHAPTERS ADJUDICATION (checked 2026-07-04): the task
brief called this the shared set of ch14 Temperance AND ch16 Tower.
The scene JSONs say otherwise — grep of godot/resources/scenes/vol5/
shows `3d:montreal_apartment` is bound ONLY by vol5_ch14_temperance
(line 10). vol5_ch16_tower (line 10) binds `3d:elicia_apartment`,
a separate GLB with its own builder (build_elicia_apartment.py) and
.tscn. The two chapters are tonal opposites set in two DIFFERENT
Montreal apartments: John's (this one, calm, "temperance held") and
Elicia Duchane's wrecked command center forty-five minutes away by
metro (ch16 scene line 166). So this GLB bakes the TEMPERANCE state,
fully committed — no render rig, no data slates, no wreckage. The
only Tower echo kept is deliberate canon rhyme, not shared geometry:
both apartments own a narwhal mug (ch14 line 60-64 — John's beloved
only-mug; ch16 line 325 — Elicia's disliked one, which lives in HER
GLB's problem space, not here).

Canon baked in (vol5_ch14_temperance.json, cited by line):

  · line 40: "the dust motes performing their intricate silent
    ballet in the shaft of late-morning Montreal sunlight slicing
    through his apartment window" — tall N window is a REAL opening;
    the motes are modeled as tiny sun-lit specks along the shaft
    (same literal-subtitle treatment as cafe_olimpico's).
  · line 48: "the gurgle of the coffee maker" — a DRIP coffee
    maker mid-brew on the kitchenette counter (gurgle = drip
    machine). The scaffold's French press was non-canon; removed.
  · line 56: "Movie posters (mostly Criterion Collection reprints)
    jostled for wall space with pages torn from obscure literary
    journals. Notebooks ... formed precarious ziggurats on every
    available surface." — three Criterion-minimal posters (flat
    field + white title band + spine chip) + one more on the east
    wall, torn journal pages pinned between them and beside the
    desk, notebook ziggurats on desk / coffee table / counter /
    window ledge / bookshelf top / floor.
  · lines 60-64 + 244: the narwhal mug ("the only mug he drank
    from") on THE COASTER he bought for it, on the desk, holding
    the last of the coffee. Pale-blue decal patch + cream blob +
    horn tick stand in for the cartoon (no textures).
  · line 68: oat milk carton by the coffee maker.
  · line 72: "his desk, a landscape of paper drifts" — desk facing
    the window, paper drift, laptop open on the three-weeks-late
    Algorithmic Comfort Food draft (line 76 / 288).
  · line 80: the alleyway out the window — "overflowing recycling
    bins, a surprisingly persistent patch of moss on the opposite
    brick wall, the occasional stray cat navigating the urban
    topography" — opposite brick wall with moss patch, stray cat
    mid-stealth on the stone ledge, bins overflowing at alley
    grade below (flat is one floor up; camera sees wall + pipe).
  · lines 88 + 204: "the graffiti-scarred drainpipe" the light
    hits in the particular way — zinc drainpipe on the opposite
    wall, three muted spray-tag sleeves.
  · line 92: the small private notebook lives IN the kitchen
    drawer — drawer baked CLOSED; the notebook is deliberately
    not visible anywhere.
  · lines 172 + 300: his phone on the desk, face-up, showing the
    four-word thread (two tiny message bubbles on the lit screen).
  · line 244: recycling bin full ("always full on a Tuesday, the
    city collection coming on Wednesdays").
  · line 280: "He set the pen on top of it" — closed notebook with
    the pen resting on top, beside the mug.
  · line 132: "the hum of the refrigerator" — fridge on the north
    wall, vent slats at the base.

CANON-NEGATIVES (as load-bearing as the props):
  · NO French press (scaffold invention — line 48 says coffee
    maker, and it gurgles).
  · Only ONE mug in the whole flat ("the only mug he drank from",
    line 64) — the dish rack holds plates and a bowl, zero mugs.
  · NO conspiracy maps / red string / corkboard — "He wasn't
    mapping conspiracies anymore" (line 148); walls carry posters
    and journal pages only. The mapping notebook is shut in the
    kitchen drawer (line 92).
  · NO fluorescent tube fixtures (scaffold had two) — a Montreal
    walk-up runs on a ceiling-medallion pendant and window light.
  · NO Tower dressing — render rig, data slates, eviction notice,
    teacup, camera all belong to elicia_apartment (see
    adjudication above).
  · NO snow baked despite the .tscn light named Key_SnowWindow —
    ch14 is "The Moderate Temperature of Tuesday" with a sunlight
    shaft and persistent moss; the cool light still reads as grey-
    stone Montreal without contradicting either.
  · Not raining, no umbrellas/puddles — the shaft is the weather.

DUAL-READING NOTES: none required (ch16 renders elsewhere), but the
room stays scene-light-flexible anyway: the shaft motes are tiny
warm specks that vanish under cool light; nothing bakes a time of
day except the frozen clock — 10:33, ten minutes after Cafe
Olimpico's 10:23, the same-city Tuesday-morning rhyme (John is at
Olimpico most Tuesday mornings, ch16 line 365; Temperance is the
Tuesday he stayed home).

Playbook compliance: window is a REAL OPENING (frame + mullions +
meeting rail, zero glass slabs); shell footprint kept from the
scaffold (6 x 5 m, CEIL 2.80, S door gap x -1..+1 — the .tscn
lights and the Background3D "montreal_apartment" camera preset
(0, 2.30, +0.5 / yaw 180 / fov 60) are tuned to it); cylinders for
everything round at eye level; fully deterministic (no random —
seed arithmetic only); no name-dependencies exist on the old mesh
names (grep: only Background3D preset + .tscn reference the GLB
path, never node names).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.decor import make_wall_clock, make_floor_plant
from _props.safety import make_smoke_detector
from _props.store_fixtures import make_counter, make_counter_bullnose

# ── Shell footprint kept from the scaffold (camera-safe) ─────────
ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.80

# ── Palette — pleasant grey stone city, warm oat-milk interior ───
PAL_WALL  = {"wall": (0.90, 0.86, 0.78, 1.0),      # warm plaster
             "baseboard": (0.40, 0.30, 0.21, 1.0)}
COL_FLOOR = (0.60, 0.45, 0.30, 1.0)                # old maple strip
COL_SEAM  = (0.36, 0.26, 0.17, 1.0)
COL_WOOD      = (0.44, 0.32, 0.20, 1.0)            # walnut trim
COL_WOOD_DARK = (0.27, 0.20, 0.14, 1.0)
COL_WOOD_LT   = (0.64, 0.50, 0.33, 1.0)
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_CREAM     = (0.91, 0.88, 0.81, 1.0)
COL_PLASTER   = (0.90, 0.88, 0.82, 1.0)            # ceiling
COL_CURTAIN   = (0.46, 0.29, 0.26, 1.0)            # heavy madder wool
COL_CURTAIN_DK= (0.36, 0.22, 0.20, 1.0)
COL_RADIATOR  = (0.70, 0.68, 0.62, 1.0)            # many coats of paint
COL_CAST_IRON = (0.14, 0.14, 0.15, 1.0)
COL_SOFA      = (0.40, 0.44, 0.42, 1.0)            # sage wool
COL_PILLOW    = (0.60, 0.34, 0.24, 1.0)
COL_RUG       = (0.52, 0.46, 0.40, 1.0)
COL_RUG_EDGE  = (0.38, 0.32, 0.28, 1.0)
COL_GLASSISH  = (0.73, 0.78, 0.79, 1.0)            # opaque carafe stand-in
COL_COFFEE    = (0.20, 0.12, 0.08, 1.0)
COL_OAT       = (0.86, 0.82, 0.72, 1.0)            # oat milk carton
COL_LAPTOP    = (0.32, 0.33, 0.35, 1.0)
COL_PHONE     = (0.10, 0.10, 0.12, 1.0)
COL_SCREEN    = (0.24, 0.28, 0.36, 1.0)            # lit phone glass
COL_CORK      = (0.60, 0.45, 0.30, 1.0)
COL_LINEN     = (0.89, 0.86, 0.78, 1.0)
COL_SUNGLOW   = (0.99, 0.93, 0.78, 1.0)            # dust motes / bulb
COL_GREYSTONE = (0.62, 0.60, 0.56, 1.0)            # our facade (line 64)
COL_GREYSTONE_DK = (0.50, 0.48, 0.45, 1.0)
COL_BRICK     = (0.50, 0.32, 0.25, 1.0)            # opposite wall (line 80)
COL_MORTAR    = (0.42, 0.28, 0.22, 1.0)
COL_MOSS      = (0.35, 0.45, 0.30, 1.0)
COL_MOSS_DK   = (0.28, 0.38, 0.25, 1.0)
COL_ASPHALT   = (0.17, 0.17, 0.18, 1.0)
COL_PIPE      = (0.44, 0.48, 0.44, 1.0)            # weathered zinc
COL_BIN_GREEN = (0.28, 0.40, 0.28, 1.0)            # Montreal wheelie
COL_BIN_BLUE  = (0.26, 0.36, 0.50, 1.0)            # recycling box
COL_KRAFT     = (0.70, 0.56, 0.38, 1.0)
COL_CAT       = (0.30, 0.30, 0.32, 1.0)
COL_NARWHAL_BLUE = (0.62, 0.72, 0.80, 1.0)         # mug decal field
COL_FRIDGE    = (0.84, 0.83, 0.79, 1.0)            # older enamel white
# Muted spray tints for the drainpipe tags (lines 88/204)
TAG_TINTS = [(0.68, 0.38, 0.46, 1.0), (0.38, 0.52, 0.62, 1.0),
             (0.74, 0.62, 0.34, 1.0)]
# Notebook / book tints (deterministic rotation)
NOTE_TINTS = [(0.24, 0.28, 0.34, 1.0), (0.48, 0.30, 0.24, 1.0),
              (0.30, 0.38, 0.32, 1.0), (0.60, 0.54, 0.40, 1.0),
              (0.20, 0.20, 0.22, 1.0)]
BOOK_TINTS = [(0.48, 0.30, 0.24, 1.0), (0.28, 0.36, 0.42, 1.0),
              (0.62, 0.54, 0.34, 1.0), (0.36, 0.30, 0.38, 1.0),
              (0.70, 0.64, 0.52, 1.0), (0.32, 0.44, 0.38, 1.0)]
# Criterion-minimal poster fields (line 56)
POSTER_FIELDS = [(0.24, 0.38, 0.42, 1.0),          # deep teal
                 (0.66, 0.48, 0.24, 1.0),          # warm ochre
                 (0.34, 0.34, 0.40, 1.0),          # slate
                 (0.52, 0.28, 0.26, 1.0)]          # oxblood

# Window opening in the north wall: x -1.1..+1.1, z 0.85..2.35
WIN_X0, WIN_X1 = -1.1, 1.1
WIN_SILL, WIN_HEAD = 0.85, 2.35
ALLEY_Z = -3.0                      # alley grade (flat is one floor up)
OPP_Y = 8.90                        # opposite brick wall face
DESK_TOP = 0.76

_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}


# ═════════════════════════════════════════════════════════════════
# Local helpers (deterministic — seed arithmetic only)
# ═════════════════════════════════════════════════════════════════
def _ziggurat(prefix, cx, cy, bz, count, start=0):
    """Precarious notebook ziggurat (line 56) — offsets drift with
    index so every stack leans a different way."""
    z = bz
    for i in range(count):
        w = 0.22 - (i % 4) * 0.018
        d = 0.28 - ((i + start) % 3) * 0.022
        t = 0.022 + ((i + start) % 2) * 0.008
        ox = (((i * 17 + start * 7) % 9) / 9.0 - 0.5) * 0.05
        oy = (((i * 29 + start * 11) % 7) / 7.0 - 0.5) * 0.06
        make_box(f"{prefix}_{i}", (cx + ox, cy + oy, z + t / 2.0),
                 (w, d, t), NOTE_TINTS[(i + start) % len(NOTE_TINTS)])
        z += t

def _paper_drift(prefix, cx, cy, bz, count, start=0):
    """Loose sheets — 'a landscape of paper drifts' (line 72)."""
    for i in range(count):
        ox = (((i * 13 + start * 5) % 11) / 11.0 - 0.5) * 0.46
        oy = (((i * 23 + start * 3) % 9) / 9.0 - 0.5) * 0.32
        tint = P.PAPER if (i + start) % 3 else P.PAPER_AGED
        make_box(f"{prefix}_{i}", (cx + ox, cy + oy, bz + 0.002 + i * 0.0025),
                 (0.20, 0.27, 0.003), tint)

def _poster(tag, wall_x, cy, cz, w, h, field, face_sign):
    """Criterion-minimal reprint (line 56): flat field, white title
    band at the foot, small spine chip top corner. Faces ±X."""
    fx = wall_x + face_sign * 0.006
    dx = wall_x + face_sign * 0.012
    make_box(f"{tag}_Field", (fx, cy, cz), (0.012, w, h), field)
    make_box(f"{tag}_Band", (dx, cy, cz - h / 2.0 + 0.075),
             (0.006, w * 0.88, 0.11), COL_CREAM)
    make_box(f"{tag}_Title", (dx + face_sign * 0.002, cy - w * 0.12,
             cz - h / 2.0 + 0.075), (0.004, w * 0.52, 0.035), COL_CAST_IRON)
    make_box(f"{tag}_Chip", (dx, cy + w / 2.0 - 0.075, cz + h / 2.0 - 0.075),
             (0.006, 0.075, 0.075), COL_CREAM)

def _journal_page(tag, cx, cy, cz, axis, w=0.15, h=0.21):
    """Torn journal page pinned to plaster (line 56). axis 'X' for
    E/W walls (thin along X), 'Y' for the north wall."""
    if axis == 'X':
        face_sign = +1 if cx < 0 else -1     # push text into the room
        make_box(f"{tag}_Page", (cx, cy, cz), (0.012, w, h), P.PAPER_AGED)
        make_box(f"{tag}_Text", (cx + face_sign * 0.008, cy, cz),
                 (0.004, w * 0.7, h * 0.62), P.NEWSPRINT)
    else:
        make_box(f"{tag}_Page", (cx, cy, cz), (w, 0.012, h), P.PAPER_AGED)
        make_box(f"{tag}_Text", (cx, cy - 0.008, cz),
                 (w * 0.7, 0.004, h * 0.62), P.NEWSPRINT)

def _chair(prefix, cx, cy, facing, tint):
    """Plain wooden chair; `facing` = direction the sitter faces."""
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
    slat_sz = (0.36, 0.03, 0.09) if dx == 0 else (0.03, 0.36, 0.09)
    for si, sz_z in enumerate((0.72, 0.86)):
        make_box(f"{prefix}_Slat_{si}", (bx, by, sz_z), slat_sz, tint)

def _book_row(prefix, cx, cy0, bz, count, start=0):
    """Standing books on an east-wall shelf (spines face west)."""
    y = cy0
    for b in range(count):
        w = 0.036 + ((b + start) % 3) * 0.008
        h = 0.195 + ((b + start) % 4) * 0.017
        make_box(f"{prefix}_{b}", (cx, y + w / 2.0, bz + h / 2.0),
                 (0.14, w, h), BOOK_TINTS[(b + start) % len(BOOK_TINTS)])
        y += w + 0.004


# ═════════════════════════════════════════════════════════════════
# SHELL — scaffold footprint kept: hardwood floor, plaster walls,
# north window carved as a REAL opening, S door gap x -1..+1,
# plaster ceiling (no tile grid) with a medallion, crown molding.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # E/W walls — full height, full run
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # North wall — window opening x -1.1..+1.1, z 0.85..2.35 (real
    # opening per playbook; the shaft of line 40 comes through here)
    make_wall("Wall_N_W", (-2.15, ROOM_D, 0), length=2.10, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+2.15, ROOM_D, 0), length=2.10, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_Sill", (0.0, ROOM_D, WIN_SILL / 2.0),
             (WIN_X1 - WIN_X0, 0.20, WIN_SILL), PAL_WALL["wall"])
    make_box("Wall_N_SillBase", (0.0, ROOM_D - 0.13, 0.08),
             (WIN_X1 - WIN_X0, 0.06, 0.16), PAL_WALL["baseboard"])
    make_box("Wall_N_Header", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_X1 - WIN_X0, 0.20, CEIL - WIN_HEAD), PAL_WALL["wall"])
    # South wall — scaffold door gap x -1..+1 kept (camera preset)
    make_wall("Wall_S_W", (-2.0, 0.0, 0), length=2.0, height=CEIL, axis='X',
              palette=PAL_WALL)
    make_wall("Wall_S_E", (+2.0, 0.0, 0), length=2.0, height=CEIL, axis='X',
              palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             PAL_WALL["wall"])
    # Entry-gap infill either side of the 0.95 m door leaf
    for nm, fx in [("Wall_S_FillW", -0.775), ("Wall_S_FillE", +0.775)]:
        make_box(nm, (fx, 0.0, 1.10), (0.45, 0.20, 2.20), PAL_WALL["wall"])
    # Plaster ceiling — a Montreal walk-up, NOT a drop-tile grid
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_PLASTER},
                 with_grid=False, with_stains=False)
    # Plaster medallion under the pendant (period register)
    make_cyl("Ceil_Medallion", (0.0, 2.5, CEIL - 0.012), 0.26, 0.024,
             COL_PLASTER, segments=16)
    make_cyl("Ceil_MedallionRing", (0.0, 2.5, CEIL - 0.028), 0.17, 0.016,
             (0.84, 0.82, 0.76, 1.0), segments=16)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD})


# ═════════════════════════════════════════════════════════════════
# ENTRY — closed front door in the S gap (behind the camera), mat.
# Minimal on purpose: John's entry has no canon dressing.
# ═════════════════════════════════════════════════════════════════
def build_entry():
    make_box("Door_Leaf", (0.0, 0.04, 1.06), (0.95, 0.06, 2.12), COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"Door_Panel_{pi}", (0.0, 0.075, 0.64 + pi * 0.88),
                 (0.68, 0.012, 0.64), COL_WOOD)
    make_box("Door_HeadTrim", (0.0, 0.10, 2.17), (1.14, 0.06, 0.10), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"Door_JambTrim_{sgn:+d}", (sgn * 0.53, 0.10, 1.08),
                 (0.08, 0.06, 2.16), COL_WOOD)
    make_cyl("Door_Knob", (0.38, 0.10, 1.00), 0.028, 0.05, COL_BRASS, axis='Y')
    make_door_hinges("Door_Hinge", edge_x=-0.46, edge_y=0.08,
                     edge_z_centers=[0.35, 1.06, 1.85], axis='X')
    make_box("Doormat", (0.0, 0.72, 0.010), (0.90, 0.55, 0.014), P.RUBBER_MAT)


# ═════════════════════════════════════════════════════════════════
# WINDOW — the tall north window (line 40): wood frame + double-hung
# meeting rail + mullions in the real opening, NO glass (playbook).
# Heavy curtains on a rod either side; ledge with a small ziggurat.
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D
    make_box("WinN_Sill", (0.0, wy, WIN_SILL - 0.035), (2.42, 0.22, 0.07), COL_WOOD)
    make_box("WinN_Ledge", (0.0, wy - 0.14, WIN_SILL + 0.005),
             (2.20, 0.14, 0.03), COL_WOOD)
    make_box("WinN_Head", (0.0, wy, WIN_HEAD + 0.035), (2.42, 0.22, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinN_Jamb_{sgn:+d}", (sgn * 1.13, wy, (WIN_SILL + WIN_HEAD) / 2.0),
                 (0.06, 0.22, WIN_HEAD - WIN_SILL), COL_WOOD)
    make_box("WinN_MeetRail", (0.0, wy, 1.62), (2.20, 0.14, 0.06), COL_WOOD)
    make_box("WinN_MullLo", (0.0, wy, 1.22), (0.05, 0.12, 0.74), COL_WOOD)
    make_box("WinN_MullHi", (0.0, wy, 2.00), (0.05, 0.12, 0.70), COL_WOOD)
    make_cyl("WinN_SashLock", (0.0, wy - 0.13, 1.665), 0.020, 0.02, COL_BRASS)
    # Heavy curtains (kept from the scaffold read of the room) —
    # solid wool panels, drawn OPEN so the shaft gets in
    make_cyl("CurtainRod", (0.0, wy - 0.20, 2.52), 0.015, 3.00,
             COL_WOOD_DARK, axis='X')
    for fi, sgn in enumerate((-1, +1)):
        make_cyl(f"CurtainRod_Finial_{fi}", (sgn * 1.52, wy - 0.20, 2.52),
                 0.032, 0.06, COL_WOOD_DARK, axis='X')
        make_box(f"CurtainRod_Bracket_{fi}", (sgn * 1.40, wy - 0.10, 2.50),
                 (0.04, 0.10, 0.05), COL_WOOD_DARK)
    for tag, sgn in (("W", -1), ("E", +1)):
        cxp = sgn * 1.32
        make_box(f"Curtain_{tag}", (cxp, wy - 0.20, 1.43), (0.40, 0.10, 2.15),
                 COL_CURTAIN)
        for fo in range(3):
            make_box(f"Curtain_{tag}_Fold_{fo}", (cxp - 0.13 + fo * 0.13,
                     wy - 0.255, 1.43), (0.035, 0.012, 2.13), COL_CURTAIN_DK)
    # Ziggurat on the window ledge — "every available surface" (56)
    _ziggurat("WinLedgeZig", 0.82, wy - 0.145, WIN_SILL + 0.02, 2, start=3)


# ═════════════════════════════════════════════════════════════════
# RADIATOR — cast iron under the window, many coats of paint.
# Montreal register (the scaffold had this right; refined).
# ═════════════════════════════════════════════════════════════════
def build_radiator():
    ry = ROOM_D - 0.28
    for fi in range(7):
        make_box(f"Radiator_Fin_{fi}", (-0.66 + fi * 0.22, ry, 0.38),
                 (0.055, 0.16, 0.60), COL_RADIATOR)
    make_box("Radiator_TopRail", (0.0, ry, 0.70), (1.52, 0.18, 0.035),
             COL_RADIATOR)
    for li, lx in enumerate((-0.62, +0.62)):
        make_cyl(f"Radiator_Foot_{li}", (lx, ry, 0.04), 0.025, 0.08, COL_CAST_IRON)
    make_cyl("Radiator_Valve", (-0.82, ry, 0.20), 0.035, 0.06, COL_BRASS)
    make_cyl("Radiator_Pipe", (0.82, ry + 0.04, 0.14), 0.020, 0.28, COL_RADIATOR)


# ═════════════════════════════════════════════════════════════════
# ALLEY — what the window frames (lines 80/88/204): our greystone
# facade (flat is one floor up), the opposite BRICK wall with the
# persistent moss patch, the graffiti-scarred drainpipe the light
# hits, the stone ledge with the stray cat mid-stealth, and the
# overflowing recycling bins down at alley grade (Tuesday-full,
# line 244 — collection is Wednesday).
# ═════════════════════════════════════════════════════════════════
def build_alley():
    # Our exterior face — pleasant grey stone (line 64)
    make_box("Ext_Face_Below", (0.0, 5.22, (ALLEY_Z + WIN_SILL) / 2.0 - 0.02),
             (7.0, 0.24, WIN_SILL - ALLEY_Z + 0.06), COL_GREYSTONE)
    make_box("Ext_Face_Above", (0.0, 5.22, 2.90), (7.0, 0.24, 1.10), COL_GREYSTONE)
    make_box("Ext_Face_W", (-2.30, 5.22, (WIN_SILL + WIN_HEAD) / 2.0),
             (2.40, 0.24, WIN_HEAD - WIN_SILL), COL_GREYSTONE)
    make_box("Ext_Face_E", (+2.30, 5.22, (WIN_SILL + WIN_HEAD) / 2.0),
             (2.40, 0.24, WIN_HEAD - WIN_SILL), COL_GREYSTONE)
    for ci, cz in enumerate((-1.9, -0.9, 0.1, 2.55, 3.05)):
        make_box(f"Ext_Course_{ci}", (0.0, 5.345, cz), (7.0, 0.02, 0.03),
                 COL_GREYSTONE_DK)
    make_box("Ext_WinSillStone", (0.0, 5.20, 0.79), (2.50, 0.30, 0.10),
             COL_GREYSTONE_DK)
    make_box("Ext_WinLintel", (0.0, 5.18, 2.42), (2.56, 0.26, 0.14),
             COL_GREYSTONE_DK)
    make_box("Ext_ParapetCap", (0.0, 5.22, 3.50), (7.2, 0.32, 0.10),
             COL_GREYSTONE_DK)
    # Alley ground — dry asphalt (not raining; the shaft is the weather)
    make_box("Alley_Ground", (0.0, 7.10, ALLEY_Z - 0.05), (9.5, 3.6, 0.10),
             COL_ASPHALT)
    # Opposite brick wall (line 80) + mortar courses
    make_box("Opp_Wall", (0.0, 9.05, 0.20), (9.5, 0.30, 6.7), COL_BRICK)
    for mi, mz in enumerate((-2.4, -1.5, -0.6, 0.35, 1.25, 2.15, 3.0)):
        make_box(f"Opp_Course_{mi}", (0.0, OPP_Y - 0.006, mz), (9.5, 0.02, 0.025),
                 COL_MORTAR)
    # THE MOSS — "a surprisingly persistent patch" (lines 80/244/292)
    for pi, (px, pz, pw, ph, tint) in enumerate([
            (-0.95, 0.95, 0.55, 0.40, COL_MOSS),
            (-0.70, 1.20, 0.34, 0.30, COL_MOSS_DK),
            (-1.20, 0.72, 0.30, 0.26, COL_MOSS_DK),
            (-0.85, 0.60, 0.40, 0.20, COL_MOSS),
            (-0.55, 0.88, 0.22, 0.34, COL_MOSS)]):
        make_box(f"Opp_Moss_{pi}", (px, OPP_Y - 0.012 - pi * 0.002, pz),
                 (pw, 0.02, ph), tint)
    # Stone ledge across the opposite wall + THE STRAY CAT (line 80)
    make_box("Opp_Ledge", (0.0, 8.82, 0.72), (9.5, 0.16, 0.08), COL_GREYSTONE_DK)
    make_box("Cat_Body", (1.78, 8.80, 0.845), (0.30, 0.13, 0.14), COL_CAT)
    make_box("Cat_Head", (1.57, 8.80, 0.925), (0.11, 0.10, 0.11), COL_CAT)
    for ei, sgn in enumerate((-1, +1)):
        make_box(f"Cat_Ear_{ei}", (1.55, 8.80 + sgn * 0.028, 0.995),
                 (0.03, 0.025, 0.04), COL_CAT)
    make_cyl("Cat_Tail", (2.00, 8.80, 0.90), 0.014, 0.16, COL_CAT, axis='X')
    for li_c, lx in enumerate((1.66, 1.90)):
        make_cyl(f"Cat_Leg_{li_c}", (lx, 8.80, 0.80), 0.012, 0.08, COL_CAT)
    # A steel back door down at grade (someone else's building)
    make_box("Opp_Door", (2.60, 8.87, ALLEY_Z + 1.05), (0.95, 0.08, 2.10),
             (0.30, 0.32, 0.34, 1.0))
    make_box("Opp_DoorFrame", (2.60, 8.885, ALLEY_Z + 2.13), (1.10, 0.05, 0.08),
             COL_GREYSTONE_DK)
    # THE DRAINPIPE (lines 88/204) — graffiti-scarred, catches the
    # light in the particular way. Zinc run, three tag sleeves.
    make_cyl("Drainpipe", (0.85, 8.85, 0.22), 0.055, 6.45, COL_PIPE)
    for bi, bz in enumerate((-1.6, 0.5, 2.4)):
        make_box(f"Drainpipe_Bracket_{bi}", (0.85, 8.90, bz), (0.06, 0.10, 0.05),
                 COL_CAST_IRON)
    make_cyl("Drainpipe_Elbow", (0.85, 8.72, ALLEY_Z + 0.14), 0.055, 0.28,
             COL_PIPE, axis='Y')
    make_cyl("Drainpipe_Shoe", (0.85, 8.58, ALLEY_Z + 0.08), 0.048, 0.10,
             COL_PIPE, axis='Y')
    for ti in range(3):
        make_cyl(f"Drainpipe_Tag_{ti}", (0.85, 8.85, 0.35 + ti * 0.60),
                 0.058, 0.18, TAG_TINTS[ti])
    make_box("Opp_Graffiti", (1.55, OPP_Y - 0.012, 0.45), (0.55, 0.02, 0.28),
             TAG_TINTS[1])
    make_box("Opp_Graffiti_2", (1.42, OPP_Y - 0.016, 0.52), (0.26, 0.02, 0.12),
             TAG_TINTS[0])
    # Overflowing recycling (lines 80/244) — green wheelie, lid
    # propped by the overflow, blue box of bottles + paper stack
    make_box("Recyc_BinGreen", (-1.60, 6.05, ALLEY_Z + 0.46),
             (0.56, 0.50, 0.92), COL_BIN_GREEN)
    make_box("Recyc_BinLid", (-1.60, 6.13, ALLEY_Z + 1.00),
             (0.60, 0.54, 0.03), (0.22, 0.32, 0.22, 1.0))
    make_box("Recyc_Card_0", (-1.60, 5.98, ALLEY_Z + 1.05), (0.40, 0.30, 0.16),
             COL_KRAFT)
    make_box("Recyc_Card_1", (-1.44, 6.12, ALLEY_Z + 1.16), (0.30, 0.34, 0.08),
             COL_KRAFT)
    make_box("Recyc_Card_Lean", (-1.24, 6.05, ALLEY_Z + 0.55), (0.05, 0.44, 0.80),
             COL_KRAFT)
    make_box("Recyc_BoxBlue", (-0.80, 5.80, ALLEY_Z + 0.16), (0.50, 0.38, 0.32),
             COL_BIN_BLUE, open_faces={'+Z'})
    for bt in range(3):
        make_cyl(f"Recyc_Bottle_{bt}", (-0.94 + bt * 0.14, 5.80, ALLEY_Z + 0.34),
                 0.038, 0.22, COL_GLASSISH)
    make_box("Recyc_PaperStack", (-0.62, 5.78, ALLEY_Z + 0.36), (0.22, 0.26, 0.10),
             P.NEWSPRINT)


# ═════════════════════════════════════════════════════════════════
# THE DESK — the heart of the chapter (lines 72/76/156/264-288).
# Faces the window (he watches the motes and the drainpipe from
# here). Landscape of paper drifts, the laptop with the Algorithmic
# Comfort Food draft, the phone face-up on the four-word thread,
# the closed notebook with the pen set on top (line 280), the
# narwhal mug on its coaster (lines 60-64/244), two ziggurats.
# ═════════════════════════════════════════════════════════════════
def build_desk():
    dx, dy = -1.15, 3.55
    make_box("Desk_Top", (dx, dy, DESK_TOP - 0.018), (1.35, 0.68, 0.035),
             COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Desk_Leg_{li}", (dx + sx * 0.62, dy + sy * 0.28, 0.37),
                 0.024, 0.725, COL_WOOD_DARK)
    for si, sgn in enumerate((-1, +1)):
        make_box(f"Desk_Stretcher_{si}", (dx + sgn * 0.62, dy, 0.16),
                 (0.04, 0.56, 0.04), COL_WOOD_DARK)
    _chair("DeskChair", dx, dy - 0.62, 'N', COL_WOOD_LT)
    # Laptop, open on the three-weeks-late draft (lines 76/288)
    make_box("Laptop_Base", (-1.52, 3.55, 0.769), (0.33, 0.24, 0.018), COL_LAPTOP)
    make_box("Laptop_Keys", (-1.52, 3.53, 0.7795), (0.28, 0.17, 0.002),
             COL_CAST_IRON)
    make_box("Laptop_Screen", (-1.52, 3.685, 0.885), (0.33, 0.018, 0.225),
             COL_LAPTOP)
    make_box("Laptop_ScreenFace", (-1.52, 3.674, 0.885), (0.30, 0.006, 0.195),
             (0.80, 0.82, 0.84, 1.0))
    for tl in range(4):
        make_box(f"Laptop_DraftLine_{tl}", (-1.54, 3.670, 0.945 - tl * 0.038),
                 (0.24 - (tl % 2) * 0.05, 0.004, 0.014), P.NEWSPRINT)
    # The phone, face-up, the four-word thread open (lines 172/300)
    make_box("Phone_Body", (-0.84, 3.68, DESK_TOP + 0.006), (0.074, 0.152, 0.012),
             COL_PHONE)
    make_box("Phone_Screen", (-0.84, 3.68, DESK_TOP + 0.0135), (0.064, 0.138, 0.002),
             COL_SCREEN)
    make_box("Phone_Bubble_In", (-0.85, 3.715, DESK_TOP + 0.0155),
             (0.032, 0.020, 0.001), (0.58, 0.60, 0.64, 1.0))   # did you feel it
    make_box("Phone_Bubble_Out", (-0.825, 3.655, DESK_TOP + 0.0155),
             (0.022, 0.014, 0.001), (0.34, 0.48, 0.64, 1.0))   # yes.
    # Closed notebook, pen set on top of it (lines 264/280)
    make_box("Notebook_Closed", (-0.98, 3.30, DESK_TOP + 0.014),
             (0.20, 0.26, 0.028), NOTE_TINTS[0])
    make_cyl("Notebook_Pen", (-0.98, 3.30, DESK_TOP + 0.034), 0.005, 0.13,
             COL_CAST_IRON, axis='Y')
    # THE NARWHAL MUG on THE COASTER (lines 60-64/244) — last of
    # the coffee still in it; pale-blue decal + cream blob + horn
    make_cyl("Mug_Coaster", (-0.68, 3.42, DESK_TOP + 0.004), 0.052, 0.008,
             COL_CORK, segments=12)
    make_cyl("Mug_Body", (-0.68, 3.42, DESK_TOP + 0.056), 0.040, 0.095, COL_CREAM)
    make_box("Mug_Handle", (-0.63, 3.42, DESK_TOP + 0.058), (0.016, 0.014, 0.05),
             COL_CREAM)
    make_cyl("Mug_Coffee", (-0.68, 3.42, DESK_TOP + 0.104), 0.032, 0.006,
             COL_COFFEE)
    make_box("Mug_DecalField", (-0.68, 3.379, DESK_TOP + 0.058),
             (0.050, 0.006, 0.045), COL_NARWHAL_BLUE)
    make_box("Mug_Narwhal", (-0.683, 3.376, DESK_TOP + 0.054),
             (0.028, 0.004, 0.014), COL_CREAM)
    make_box("Mug_NarwhalHorn", (-0.664, 3.376, DESK_TOP + 0.068),
             (0.006, 0.004, 0.016), (0.88, 0.86, 0.78, 1.0))
    # Paper drift + the two desk ziggurats (lines 56/72)
    _paper_drift("DeskDrift", -1.05, 3.40, DESK_TOP, 7, start=1)
    _ziggurat("DeskZig_A", -1.72, 3.30, DESK_TOP, 5, start=0)
    _ziggurat("DeskZig_B", -0.62, 3.74, DESK_TOP, 6, start=2)
    # Wastebasket + two crumpled abandoned narratives (line 56)
    make_cyl("WasteBin", (-0.50, 3.72, 0.12), 0.10, 0.24, (0.42, 0.40, 0.36, 1.0),
             segments=10)
    make_box("WasteCrumple_0", (-0.36, 3.52, 0.022), (0.05, 0.045, 0.044), P.PAPER)
    make_box("WasteCrumple_1", (-0.60, 3.94, 0.019), (0.04, 0.05, 0.038),
             P.PAPER_AGED)
    # Floor stack east of the chair — more ziggurat spillover
    _ziggurat("DeskFloorZig", -0.42, 3.02, 0.0, 5, start=4)


# ═════════════════════════════════════════════════════════════════
# KITCHENETTE — NE corner along the east wall. The gurgling drip
# coffee maker mid-brew (line 48; the scaffold's French press was
# non-canon), oat milk (line 68), sink + rack (mug-free — the
# narwhal is the only mug, line 64), the CLOSED kitchen drawer
# holding the private notebook (line 92), fridge with its hum
# (line 132), wall cabinet, one more counter ziggurat.
# ═════════════════════════════════════════════════════════════════
def build_kitchenette():
    cx, cy = 2.5, 4.0
    top_z = make_counter("Kitch", (cx, cy, 0.0), length=1.80, depth=0.70,
                         height=0.92, palette={"formica": COL_WOOD_LT,
                         "top": (0.30, 0.22, 0.15, 1.0),
                         "kick": COL_WOOD_DARK})
    make_counter_bullnose("Kitch", (cx - 0.35, cy, top_z), length=1.80,
                          palette={"top": (0.30, 0.22, 0.15, 1.0)})
    ktop = top_z + 0.02
    # Drawer stack (west face) — TOP DRAWER stays CLOSED: the small
    # private notebook with the drainpipe dates lives inside
    # (line 92) and is deliberately not modeled anywhere visible.
    for di in range(2):
        make_box(f"Kitch_Drawer_{di}", (2.145, 3.42, 0.78 - di * 0.20),
                 (0.015, 0.50, 0.17), COL_WOOD)
        make_cyl(f"Kitch_DrawerKnob_{di}", (2.135, 3.42, 0.78 - di * 0.20),
                 0.014, 0.03, COL_BRASS, axis='X')
    for ci_d, cyd in enumerate((3.42, 4.10)):
        make_box(f"Kitch_CabDoor_{ci_d}", (2.145, cyd, 0.36 if ci_d == 0 else 0.47),
                 (0.015, 0.50 if ci_d == 0 else 0.62, 0.50 if ci_d == 0 else 0.72),
                 COL_WOOD)
        make_cyl(f"Kitch_CabKnob_{ci_d}", (2.135, cyd + 0.18, 0.55),
                 0.014, 0.03, COL_BRASS, axis='X')
    # THE COFFEE MAKER — drip machine, gurgling mid-brew (line 48)
    make_box("CoffeeMaker_Body", (2.68, 3.85, ktop + 0.17), (0.20, 0.24, 0.34),
             (0.24, 0.24, 0.26, 1.0))
    make_box("CoffeeMaker_Head", (2.55, 3.85, ktop + 0.30), (0.26, 0.22, 0.08),
             (0.24, 0.24, 0.26, 1.0))
    make_cyl("CoffeeMaker_Hotplate", (2.48, 3.85, ktop + 0.008), 0.085, 0.016,
             COL_CAST_IRON, segments=12)
    make_cyl("CoffeeMaker_Carafe", (2.48, 3.85, ktop + 0.095), 0.075, 0.155,
             COL_GLASSISH, segments=12)
    make_cyl("CoffeeMaker_BrewLevel", (2.48, 3.85, ktop + 0.055), 0.070, 0.07,
             COL_COFFEE, segments=12)
    make_box("CoffeeMaker_CarafeHandle", (2.39, 3.85, ktop + 0.11),
             (0.016, 0.014, 0.09), COL_CAST_IRON)
    make_box("CoffeeMaker_PowerLight", (2.575, 3.72, ktop + 0.07),
             (0.012, 0.008, 0.012), (0.85, 0.36, 0.24, 1.0))
    # Oat milk — "a concession to arteries" (line 68)
    make_box("OatMilk_Carton", (2.32, 4.06, ktop + 0.115), (0.085, 0.085, 0.23),
             COL_OAT)
    make_box("OatMilk_Cap", (2.32, 4.08, ktop + 0.242), (0.03, 0.03, 0.025),
             (0.46, 0.52, 0.44, 1.0))
    make_box("OatMilk_Label", (2.276, 4.06, ktop + 0.11), (0.006, 0.06, 0.10),
             (0.46, 0.52, 0.44, 1.0))
    # Sink + rack: the rack is where the mug dries at chapter's end
    # (line 280) — right now it holds PLATES ONLY (one-mug canon)
    make_box("KSink_Basin", (2.52, 4.55, ktop - 0.055), (0.40, 0.34, 0.10),
             P.METAL_STEEL, open_faces={'+Z'})
    make_box("KSink_BasinFloor", (2.52, 4.55, ktop - 0.096), (0.38, 0.32, 0.008),
             (0.44, 0.46, 0.48, 1.0))
    make_cyl("KSink_FaucetRiser", (2.76, 4.55, ktop + 0.10), 0.013, 0.20,
             P.METAL_STEEL)
    make_cyl("KSink_FaucetSpout", (2.66, 4.55, ktop + 0.19), 0.011, 0.20,
             P.METAL_STEEL, axis='X')
    for hi, hy in enumerate((4.44, 4.66)):
        make_box(f"KSink_Handle_{hi}", (2.76, hy, ktop + 0.015),
                 (0.02, 0.05, 0.02), P.METAL_STEEL)
    make_box("Rack_Tray", (2.50, 3.32, ktop + 0.008), (0.34, 0.28, 0.015),
             P.METAL_STEEL)
    for ri in range(3):
        make_box(f"Rack_Rib_{ri}", (2.40 + ri * 0.10, 3.32, ktop + 0.04),
                 (0.010, 0.26, 0.05), P.METAL_STEEL)
    for pi_r in range(2):
        make_cyl(f"Rack_Plate_{pi_r}", (2.43 + pi_r * 0.10, 3.32, ktop + 0.095),
                 0.082, 0.012, COL_CREAM, axis='X', segments=12)
    make_cyl("Rack_Bowl", (2.62, 3.26, ktop + 0.045), 0.055, 0.05, COL_CREAM)
    # Counter ziggurat — the notebooks reach even here (line 56)
    _ziggurat("KitchZig", 2.60, 3.14, ktop, 3, start=6)
    # Wall cabinet above the counter
    make_box("WallCab_Body", (2.80, 4.15, 1.86), (0.34, 1.05, 0.68), COL_WOOD)
    for wi, wy_c in enumerate((3.90, 4.40)):
        make_box(f"WallCab_Door_{wi}", (2.62, wy_c, 1.86), (0.015, 0.46, 0.62),
                 COL_WOOD_LT)
        make_cyl(f"WallCab_Knob_{wi}", (2.61, wy_c + (0.16 if wi == 0 else -0.16),
                 1.80), 0.013, 0.028, COL_BRASS, axis='X')
    # THE FRIDGE — its hum is part of the ambient texture (line 132)
    make_box("Fridge_Body", (1.55, 4.56, 0.86), (0.62, 0.62, 1.72), COL_FRIDGE)
    make_box("Fridge_DoorSeam", (1.55, 4.242, 1.16), (0.56, 0.012, 0.002),
             (0.62, 0.61, 0.58, 1.0))
    make_box("Fridge_HandleLo", (1.29, 4.23, 0.78), (0.03, 0.025, 0.34),
             P.METAL_STEEL)
    make_box("Fridge_HandleHi", (1.29, 4.23, 1.42), (0.03, 0.025, 0.22),
             P.METAL_STEEL)
    for vi in range(3):
        make_box(f"Fridge_Vent_{vi}", (1.55, 4.243, 0.06 + vi * 0.035),
                 (0.46, 0.006, 0.02), COL_CAST_IRON)


# ═════════════════════════════════════════════════════════════════
# LIVING — sofa against the west wall, coffee table with its own
# ziggurat + an open journal, rug, floor lamp, plant. Quiet
# equilibrium furniture; no TV, no radio (none in canon).
# ═════════════════════════════════════════════════════════════════
def build_living():
    make_box("Sofa_Base", (-2.38, 1.55, 0.24), (0.82, 1.70, 0.28), COL_SOFA)
    for ci_s, cy_s in enumerate((1.17, 1.93)):
        make_box(f"Sofa_Cushion_{ci_s}", (-2.32, cy_s, 0.435), (0.66, 0.72, 0.11),
                 COL_SOFA)
    make_box("Sofa_Back", (-2.72, 1.55, 0.60), (0.16, 1.70, 0.46), COL_SOFA)
    for ai, sgn in enumerate((-1, +1)):
        make_box(f"Sofa_Arm_{ai}", (-2.38, 1.55 + sgn * 0.85, 0.50),
                 (0.80, 0.14, 0.24), COL_SOFA)
    for fi_s, (fx, fy) in enumerate([(-2.70, 0.78), (-2.06, 0.78),
                                     (-2.70, 2.32), (-2.06, 2.32)]):
        make_cyl(f"Sofa_Foot_{fi_s}", (fx, fy, 0.05), 0.022, 0.10, COL_WOOD_DARK)
    make_box("Sofa_Pillow", (-2.50, 2.10, 0.56), (0.32, 0.32, 0.13), COL_PILLOW)
    # Books resting on the sofa arm (surfaces, all of them — line 56)
    for bi_a in range(2):
        make_box(f"SofaArmBook_{bi_a}", (-2.42 + bi_a * 0.02, 0.70,
                 0.63 + bi_a * 0.035), (0.19, 0.14, 0.032),
                 BOOK_TINTS[(bi_a + 2) % len(BOOK_TINTS)])
    # Coffee table + ziggurat + open journal
    make_box("CoffeeTable_Top", (-1.42, 1.55, 0.425), (0.85, 0.50, 0.035),
             COL_WOOD_LT)
    for li_t, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"CoffeeTable_Leg_{li_t}", (-1.42 + sx * 0.37, 1.55 + sy * 0.20,
                 0.205), 0.020, 0.41, COL_WOOD_DARK)
    _ziggurat("TableZig", -1.58, 1.44, 0.443, 4, start=1)
    make_box("Journal_Open_L", (-1.24, 1.68, 0.447), (0.15, 0.21, 0.008),
             P.PAPER_AGED)
    make_box("Journal_Open_R", (-1.09, 1.68, 0.447), (0.15, 0.21, 0.008), P.PAPER)
    make_box("Journal_Open_Spine", (-1.165, 1.68, 0.450), (0.012, 0.21, 0.010),
             NOTE_TINTS[1])
    # Rug + border
    make_box("LivingRug", (-1.85, 1.55, 0.006), (1.90, 1.70, 0.012), COL_RUG)
    make_box("LivingRug_Border", (-1.85, 1.55, 0.013), (1.68, 1.48, 0.002),
             COL_RUG_EDGE)
    # Floor lamp by the sofa's north end
    make_cyl("FloorLamp_Base", (-2.55, 2.72, 0.02), 0.13, 0.04, COL_CAST_IRON,
             segments=12)
    make_cyl("FloorLamp_Pole", (-2.55, 2.72, 0.76), 0.013, 1.44, COL_BRASS)
    make_cyl("FloorLamp_Shade", (-2.55, 2.72, 1.57), 0.13, 0.17, COL_LINEN,
             segments=12)
    make_cyl("FloorLamp_Glow", (-2.55, 2.72, 1.475), 0.055, 0.03, COL_SUNGLOW)
    make_floor_plant("Plant", (-2.50, 0.42, 0.0))
    # Sofa-side floor ziggurat (line 56)
    _ziggurat("LivingFloorZig", -1.88, 2.72, 0.0, 6, start=3)


# ═════════════════════════════════════════════════════════════════
# BOOKSHELF — east wall, overflowing (a writer's wall). Case +
# five shelves of mixed spines, horizontal stacks at row ends,
# ziggurat on top, floor overflow beside it.
# ═════════════════════════════════════════════════════════════════
def build_bookshelf():
    x_mid = 2.70
    for si, sy in enumerate((0.90, 2.50)):
        make_box(f"Shelf_Side_{si}", (x_mid, sy, 0.985), (0.30, 0.04, 1.97),
                 COL_WOOD)
    make_box("Shelf_TopBoard", (x_mid, 1.70, 1.955), (0.30, 1.64, 0.035), COL_WOOD)
    make_box("Shelf_Back", (2.86, 1.70, 0.985), (0.02, 1.64, 1.97), COL_WOOD_DARK)
    for bi, bz in enumerate((0.08, 0.46, 0.84, 1.22, 1.60)):
        make_box(f"Shelf_Board_{bi}", (x_mid, 1.70, bz), (0.28, 1.56, 0.03),
                 COL_WOOD)
        _book_row(f"Shelf_Row_{bi}", x_mid, 0.96 + (bi % 3) * 0.04, bz + 0.015,
                  9 - (bi % 2), start=bi * 3)
        # Horizontal stack jammed at the row's north end
        for hi in range(2 + bi % 2):
            make_box(f"Shelf_HStack_{bi}_{hi}", (x_mid, 2.32, bz + 0.038 + hi * 0.042),
                     (0.15, 0.24, 0.038), BOOK_TINTS[(bi + hi) % len(BOOK_TINTS)])
    _ziggurat("ShelfTopZig", 2.70, 1.30, 1.975, 4, start=5)
    # Floor overflow — flat stack leaning against the case's south side
    for fi in range(4):
        make_box(f"ShelfFloorBook_{fi}", (2.55, 0.62, 0.024 + fi * 0.045),
                 (0.24, 0.18, 0.042), BOOK_TINTS[(fi + 1) % len(BOOK_TINTS)])


# ═════════════════════════════════════════════════════════════════
# WALL DECOR — Criterion posters jostling with torn journal pages
# (line 56); NO maps, NO string (line 148). The clock is frozen at
# 10:33 — ten minutes after Cafe Olimpico's 10:23, the same-city
# Tuesday-morning rhyme.
# ═════════════════════════════════════════════════════════════════
def build_wall_decor():
    wx = -2.89   # west wall interior face
    _poster("Poster_W0", wx, 1.10, 1.95, 0.56, 0.80, POSTER_FIELDS[0], +1)
    make_cyl("Poster_W0_Motif", (wx + 0.014, 1.10, 2.05), 0.13, 0.008,
             (0.86, 0.80, 0.62, 1.0), axis='X', segments=14)
    _poster("Poster_W1", wx, 2.02, 1.78, 0.50, 0.72, POSTER_FIELDS[1], +1)
    make_box("Poster_W1_MotifA", (wx + 0.014, 2.02, 1.88), (0.006, 0.30, 0.10),
             (0.30, 0.28, 0.26, 1.0))
    make_box("Poster_W1_MotifB", (wx + 0.018, 1.95, 1.80), (0.006, 0.10, 0.26),
             (0.88, 0.85, 0.78, 1.0))
    _poster("Poster_W2", wx, 3.20, 1.62, 0.44, 0.62, POSTER_FIELDS[2], +1)
    make_cyl("Poster_W2_Motif", (wx + 0.014, 3.20, 1.70), 0.085, 0.008,
             (0.62, 0.40, 0.34, 1.0), axis='X', segments=12)
    # Journal pages jostling between the posters (line 56)
    for ji, (jy, jz) in enumerate([(1.62, 2.18), (1.55, 1.62), (2.48, 2.10),
                                   (2.62, 1.55), (3.62, 1.85)]):
        _journal_page(f"Journal_W_{ji}", wx, jy, jz, 'X',
                      w=0.14 + (ji % 3) * 0.02, h=0.19 + (ji % 2) * 0.04)
    # East wall — one poster + pages in the gap between shelf and
    # kitchenette
    ex = +2.89
    _poster("Poster_E0", ex, 2.85, 1.85, 0.50, 0.72, POSTER_FIELDS[3], -1)
    make_box("Poster_E0_Motif", (ex - 0.014, 2.85, 1.96), (0.006, 0.24, 0.24),
             (0.86, 0.80, 0.62, 1.0))
    for je, (jy, jz) in enumerate([(2.70, 1.32), (3.02, 1.30), (2.62, 2.30)]):
        _journal_page(f"Journal_E_{je}", ex, jy, jz, 'X',
                      w=0.15 + (je % 2) * 0.02, h=0.20)
    # North wall (west of the window) — pages where he can see them
    # from the desk, and THE CLOCK, frozen 10:33
    ny = ROOM_D - 0.105
    for jn, (jx, jz) in enumerate([(-2.62, 1.90), (-2.30, 1.55), (-1.95, 1.86),
                                   (-1.62, 1.48)]):
        _journal_page(f"Journal_N_{jn}", jx, ny, jz, 'Y',
                      w=0.14 + (jn % 3) * 0.02, h=0.19 + (jn % 2) * 0.05)
    make_wall_clock("Clock", (-2.30, ROOM_D - 0.10, 2.32),
                    frozen_hour=10, frozen_min=33)


# ═════════════════════════════════════════════════════════════════
# DUST MOTES — the intricate silent ballet in the shaft (line 40).
# Tiny sun-warm specks along the diagonal from the window head
# down toward the desk (same treatment as cafe_olimpico's motes).
# ═════════════════════════════════════════════════════════════════
def build_dust_motes():
    for i in range(15):
        t = i / 14.0
        jx = (((i * 37) % 11) / 11.0 - 0.5) * 0.90 - 0.20
        jy = (((i * 53) % 7) / 7.0 - 0.5) * 0.22
        jz = (((i * 71) % 9) / 9.0 - 0.5) * 0.18
        px = jx
        py = 4.55 - 1.55 * t + jy
        pz = 2.10 - 1.18 * t + jz
        s = 0.012 + ((i * 3) % 3) * 0.004
        make_box(f"DustMote_{i}", (px, py, pz), (s, s, s), COL_SUNGLOW)


# ═════════════════════════════════════════════════════════════════
# CEILING — medallion pendant (warm, domestic — the scaffold's
# fluorescent tubes were the wrong fixture vocabulary) + detector.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    make_cyl("Pendant_Canopy", (0.0, 2.5, CEIL - 0.045), 0.05, 0.04, COL_BRASS)
    make_cyl("Pendant_Cord", (0.0, 2.5, CEIL - 0.27), 0.008, 0.42, COL_CAST_IRON)
    make_cyl("Pendant_Shade", (0.0, 2.5, CEIL - 0.55), 0.14, 0.15, COL_LINEN,
             segments=12)
    make_cyl("Pendant_Bulb", (0.0, 2.5, CEIL - 0.645), 0.045, 0.04, COL_SUNGLOW)
    make_smoke_detector("Smoke", (0.9, 1.5, CEIL))


def main():
    clear_scene()
    build_shell()
    build_entry()
    build_window()
    build_radiator()
    build_alley()
    build_desk()
    build_kitchenette()
    build_living()
    build_bookshelf()
    build_wall_decor()
    build_dust_motes()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
          "../../../assets/3d/locales/montreal_apartment.glb"))
    print(f"\n[build_montreal_apartment] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
