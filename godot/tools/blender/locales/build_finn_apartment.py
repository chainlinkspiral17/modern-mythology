"""Finn's apartment — vol7 hero locale (Smolvud, OR).

One-bedroom OVER THE CLOSED KAYAK SHOP "on the connective stretch
between old-Yachats and old-Waldport" (vol7_ch5_cabin; music
catalog vol7_across_main: "Finn's rooms above the closed kayak
shop"). The shop closed in 2048 when the owner went back to New
Zealand; the foundation owns the building and rents the upstairs
to Finn at the local-token rate (vol7_ch5_cabin). Five vol7 scene
bindings render here: vol7_ch5_cabin, vol7_ch9_evening (opens AND
returns here — 2 bindings), vol7_ch12_morning, vol7_ch12_kai.

Canon sources baked in:
  · vol7_ch5_cabin: "Finn was at the small kitchen table with
    three pieces of charred wood laid out on a folded cloth";
    "the crow was on the back of the chair across from him";
    "He could hear the radio going faintly through the door";
    the door Finn never locked during the day; boots + coat
    pulled on by the door; the wax paper he wraps the wood in.
  · vol7_ch9_evening: the five pieces "laid out in a shape that
    was not random ... a rough irregular hexagon about ten
    inches across"; the wool cap + the coat; the duffel; "They
    went down the stairs together"; the truck "at the curb in
    front of the kayak-shop building".
  · vol7_ch12_morning: the apartment "at the corner of Hemlock
    and the alley that ran behind the bakery"; rain on the ROOF
    (top floor, roof right overhead) + "the dripping in the
    alley"; the crow's chair BESIDE THE BED and its chair by the
    kitchen table; wool socks laid by the bed, the jeans, the
    long-sleeve thermal; the space heater banked IN THE CORNER;
    the kettle; the kitchen window he stands at looking DOWN at
    the alley; THE DUFFEL in the corner, nine months in place,
    with the cloth Tem gave him; the coffee worked at the
    counter with THE CONE AND THE KETTLE at five-oh-three; the
    completed hexagon — six pieces in a ring, the cedar face in
    the center, the A R I A piece beside it; the kitchen light
    he holds the wood up to; Maya's voice through the EMERGENCY
    RADIO + the notebook that entry lives in.
  · vol7_ch12_kai: "the kitchen window faced south ... the face
    was looking out at the town"; the glass of water; the bed he
    lies down on; the chair in the bedroom the crow goes to.
  · lore/_VOL7_WIKI.md: Finn "carries the radio that picks up
    signals not on any allocated band" + "a portable UV light".
  · lore/milk_and_honey/static_truths.md: "The radio Finn
    carries that holds together on electrical tape, and that
    has, since June, been picking up a signal that is not on
    any allocated band" — the radio is a taped-together
    PORTABLE, not a ham shack; also the crow Finn feeds bottle
    caps to (a saucer of caps on the kitchen sill).

THE RADIO TREATMENT: a battery portable on its own small console
against the east wall — bakelite-brown body wrapped in two bands
of electrical tape, one taped corner, whip antenna, cream dial
face (named Radio_DialFace for scene-side Label3D), two knobs,
speaker slats — with the spiral LOG NOTEBOOK + pencil beside it,
the roll of electrical tape, spare batteries, and the portable
UV light. Small, worn, held together: canon's rig, not a shack.

CANON-NEGATIVES (deliberate absences):
  · NO crow baked — it moves scene to scene (chair-back in the
    kitchen, chair in the bedroom, the table, the dashboard);
    any fixed perch would contradict some binding. Its chairs
    are baked instead.
  · NO Finn's phone — it leaves the apartment with him (ch12);
    only the charger cord + outlet by the counter (ch5:
    "Battery's dead. I plugged it in five minutes ago").
  · Kitchen kept SPARE — Finn forgets to eat for a day at this
    table (vol7_ch9_evening); no food spread, one loaf board
    empty, mugs few. Contrast axis vs Lena's kept-warm kitchen.
  · NO fluorescents (scaffold had two) — rooms over a shop, not
    retail; warm pendant + flush domes instead.
  · NO TV / record player / stereo — the rooms' sound is the
    radio and the rain.
  · The wood count varies across bindings (3 → 5 → 8 pieces);
    the COMPLETED hexagon (six ring + cedar face center + the
    ARIA piece beside) is baked — the state of both ch12 scenes
    and the arrangement ch9 is building toward.

Shell footprint kept from the scaffold (4.5 × 5.0 m, CEIL 2.6,
door gap in the south wall x −1..+1) — the .tscn lights and the
Background3D camera preset (0, 2.30, +0.5 / yaw 180 / fov 60,
same preset family as lena_apartment) are tuned to it. Windows
are REAL OPENINGS with frames + mullions, no glass (playbook
no-transparency rule). The bedroom is a small annex north of the
main room with its door OPEN, parked against the north wall (the
crow flies low through the doorway, ch12_morning). Build-north =
canon-south: the kitchen window looks down at the alley behind
the bakery; the west window looks down at the street with the
truck at the curb and the kayak shopfront below.

Text panels baked as named vertex-color meshes for scene-side
Label3D: Radio_DialFace, Radio_LogBook, KayakShop_SignBoard,
Foundation_Plaque, Hexagon_Center_Face.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
import math
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, _finalize_mesh
from _props.structure import make_floor, make_wall, make_crown_molding, make_door_hinges
from _props.safety import make_smoke_detector

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 4.5; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.96, 0.86, 0.78, 1.0),   # warm plaster (scaffold)
            "baseboard": (0.62, 0.46, 0.30, 1.0)}
COL_FLOOR = (0.74, 0.58, 0.38, 1.0)            # fir boards (scaffold)
COL_SEAM  = (0.42, 0.30, 0.18, 1.0)

# ── Finn palette (spare, weathered, single-man PNW) ──────────────
COL_WOOD      = (0.46, 0.34, 0.22, 1.0)   # scaffold trim wood
COL_WOOD_DARK = (0.27, 0.20, 0.14, 1.0)
COL_WOOD_LT   = (0.62, 0.49, 0.32, 1.0)
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_CREAM     = (0.90, 0.87, 0.80, 1.0)
COL_LINEN     = (0.88, 0.85, 0.78, 1.0)
COL_ENAMEL    = (0.84, 0.85, 0.83, 1.0)
COL_CAST_IRON = (0.13, 0.13, 0.14, 1.0)
COL_GLASSISH  = (0.72, 0.78, 0.78, 1.0)   # opaque stand-in (water glass)
COL_COAT      = (0.36, 0.34, 0.26, 1.0)   # Finn's wax-canvas coat
COL_CYCLEJKT  = (0.40, 0.44, 0.32, 1.0)   # canvas cycling jacket
COL_WOOLCAP   = (0.28, 0.27, 0.26, 1.0)
COL_DENIM     = (0.30, 0.36, 0.46, 1.0)
COL_THERMAL   = (0.82, 0.78, 0.68, 1.0)
COL_WOOL_SOCK = (0.52, 0.48, 0.40, 1.0)
COL_BLANKET   = (0.34, 0.42, 0.38, 1.0)   # spruce wool blanket
COL_BLANKBAND = (0.60, 0.32, 0.24, 1.0)
COL_DUFFEL    = (0.38, 0.40, 0.34, 1.0)   # nine-months-in-the-corner olive
COL_CLOTH     = (0.86, 0.82, 0.72, 1.0)   # the cloth Tem gave him
COL_CHAR      = (0.11, 0.10, 0.09, 1.0)   # charred wood
COL_CHAR_LT   = (0.20, 0.18, 0.15, 1.0)
COL_GRAIN_YEL = (0.76, 0.64, 0.28, 1.0)   # "a yellow he had not seen
                                           #  in any of the local woods"
COL_CEDAR     = (0.62, 0.44, 0.28, 1.0)   # Olaf's carved cedar face
COL_CEDAR_LT  = (0.72, 0.55, 0.36, 1.0)
COL_RADIO     = (0.35, 0.26, 0.20, 1.0)   # bakelite brown
COL_ETAPE     = (0.07, 0.07, 0.09, 1.0)   # electrical tape
COL_UV_LENS   = (0.36, 0.22, 0.52, 1.0)
COL_MUG_A     = (0.34, 0.46, 0.44, 1.0)
COL_MUG_B     = (0.70, 0.32, 0.24, 1.0)
COL_HEATER    = (0.76, 0.74, 0.70, 1.0)
COL_HEATGLOW  = (0.94, 0.52, 0.24, 1.0)
COL_BRICK     = (0.44, 0.28, 0.22, 1.0)
COL_BRICK_DK  = (0.32, 0.20, 0.16, 1.0)
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.15, 0.15, 0.16, 1.0)
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_SHOPFACE  = (0.32, 0.42, 0.46, 1.0)   # kayak shop's faded marine paint
COL_SHOPTRIM  = (0.22, 0.29, 0.32, 1.0)
COL_KAYAK     = (0.62, 0.30, 0.24, 1.0)   # sun-faded red hull
COL_KAYAK_DK  = (0.44, 0.22, 0.18, 1.0)
COL_TRUCK     = (0.32, 0.40, 0.34, 1.0)   # Finn's weathered green pickup
COL_TRUCK_DK  = (0.22, 0.28, 0.24, 1.0)
COL_GLASS_DK  = (0.10, 0.11, 0.13, 1.0)   # dark opaque "glass" panels
COL_WARM_WIN  = (0.86, 0.70, 0.44, 1.0)   # lit windows (pre-dawn town)
COL_PAPERED   = (0.80, 0.72, 0.56, 1.0)   # papered-over shop glass
COL_CEIL      = (0.80, 0.75, 0.66, 1.0)   # painted plank ceiling
COL_BATTEN    = (0.58, 0.48, 0.36, 1.0)
COL_GLOW_WARM = (0.98, 0.88, 0.62, 1.0)

COUNTER_TOP = 0.92
STREET_Z = -3.30                    # street / alley grade (rooms above shop)
# Bedroom annex north of the main room (doorway x −1.75..−0.85)
ANX_X0, ANX_X1 = -2.15, -0.55       # interior extents
ANX_Y0, ANX_Y1 = ROOM_D + 0.10, ROOM_D + 2.10
ANX_CEIL = 2.45


# ═════════════════════════════════════════════════════════════════
# Local helpers (deterministic; flat extruded quad for the hexagon
# pieces — angled edges must not be axis-aligned boxes)
# ═════════════════════════════════════════════════════════════════
def _flat_piece(name, corners, z0, thick, color):
    """Extruded flat quad: `corners` = 4 (x, y) CCW viewed from +Z,
    bottom at z0, `thick` tall. Winding mirrors make_box."""
    verts = [(x, y, z0) for x, y in corners] + \
            [(x, y, z0 + thick) for x, y in corners]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (2, 3, 7, 6), (3, 0, 4, 7), (1, 2, 6, 5)]
    return _finalize_mesh(name, verts, list(faces), color)


_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _chair(prefix, cx, cy, facing, tint):
    """Spindle-back kitchen chair; `facing` = way the sitter faces.
    The top slat is the crow's perch height (~0.86)."""
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


# ═════════════════════════════════════════════════════════════════
# SHELL — scaffold footprint. South wall keeps the scaffold door
# gap (x −1..+1); west wall gets the street-window opening; north
# wall gets the bedroom doorway + the kitchen-window opening (the
# window that "faced south" in canon — build-north = canon-south).
# Painted plank ceiling: the roof is right overhead (rain on the
# roof is the room's sound, ch12_morning).
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
    # East wall — full height, the radio console lives against it
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # West wall — street-window opening y 2.7..3.9, z 0.9..2.25
    # (the truck at the curb + the kayak shopfront below)
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 1.25, 0), length=2.90, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 4.65, 0), length=1.50, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_Sill", (-ROOM_W / 2.0, 3.3, 0.45), (0.20, 1.20, 0.90),
             PAL_WALL["wall"])
    make_box("Wall_W_Header", (-ROOM_W / 2.0, 3.3, 2.425), (0.20, 1.20, 0.35),
             PAL_WALL["wall"])
    # North wall — bedroom doorway x −1.75..−0.85; kitchen window
    # x 0.55..1.65 (z 1.0..2.2, over the counter, alley below)
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
    # Painted plank ceiling + battens (roof right above)
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
# WINDOWS — real openings, fir frames + mullions, NO glass. West =
# street window (Hemlock corner / the connective stretch); north =
# the kitchen window Finn stands at looking down at the alley
# (canon-south, faces the town, ch12_kai).
# ═════════════════════════════════════════════════════════════════
def build_windows():
    # West street window: opening y 2.7..3.9, z 0.9..2.25
    wx = -ROOM_W / 2.0
    make_box("WinW_Sill", (wx, 3.3, 0.865), (0.22, 1.32, 0.07), COL_WOOD)
    make_box("WinW_Ledge", (wx + 0.14, 3.3, 0.905), (0.14, 1.20, 0.03), COL_WOOD)
    make_box("WinW_Head", (wx, 3.3, 2.285), (0.22, 1.32, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinW_Jamb_{sgn:+d}", (wx, 3.3 + sgn * 0.63, 1.575),
                 (0.22, 0.06, 1.49), COL_WOOD)
    make_box("WinW_MeetRail", (wx, 3.3, 1.58), (0.14, 1.20, 0.06), COL_WOOD)
    make_box("WinW_MullLo", (wx, 3.3, 1.24), (0.12, 0.05, 0.62), COL_WOOD)
    make_box("WinW_MullHi", (wx, 3.3, 1.92), (0.12, 0.05, 0.62), COL_WOOD)
    make_cyl("WinW_SashLock", (wx + 0.12, 3.3, 1.625), 0.020, 0.02, COL_BRASS)
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
    # Saucer of bottle caps on the kitchen sill — Finn feeds the
    # crow bottle caps (static_truths.md)
    make_cyl("WinN_CapSaucer", (0.78, wy - 0.15, 1.030), 0.048, 0.014,
             COL_CREAM, segments=12)
    for ci, (ox, oy) in enumerate([(-0.02, 0.01), (0.015, -0.015),
                                   (0.02, 0.02), (-0.01, -0.02)]):
        make_cyl(f"WinN_BottleCap_{ci}", (0.78 + ox, wy - 0.15 + oy, 1.041),
                 0.013, 0.006, P.METAL_STEEL if ci % 2 == 0 else COL_MUG_B)


# ═════════════════════════════════════════════════════════════════
# ENTRY — the door Finn never locked during the day (plain knob
# lock, no deadbolt hardware beyond it — Kai locking it in ch5 is
# the change that registers). Hooks west of the door: the coat,
# the canvas cycling jacket (Finn delivers the co-op boxes by
# bike), the wool cap. Boots on a drip tray east of the door.
# Stacked co-op delivery crates in the SE corner.
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
    make_door_hinges("Door_Hinge", edge_x=-0.46, edge_y=0.08,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    make_box("Doormat", (0.0, 0.72, 0.010), (0.90, 0.55, 0.014), P.RUBBER_MAT)
    # Hooks west of the door — coat, cycling jacket, wool cap
    make_box("Hooks_Rail", (-1.60, 0.13, 1.62), (0.80, 0.03, 0.09), COL_WOOD)
    for hi, hx in enumerate((-1.88, -1.58, -1.28)):
        make_cyl(f"Hooks_Peg_{hi}", (hx, 0.185, 1.60), 0.013, 0.09,
                 COL_BRASS, axis='Y')
    make_box("Coat_Body", (-1.88, 0.235, 1.21), (0.36, 0.08, 0.80), COL_COAT)
    make_box("Coat_Collar", (-1.88, 0.245, 1.645), (0.24, 0.09, 0.11), COL_COAT)
    make_box("CycleJacket_Body", (-1.52, 0.235, 1.30), (0.32, 0.07, 0.62),
             COL_CYCLEJKT)
    make_box("CycleJacket_Stripe", (-1.52, 0.278, 1.10), (0.30, 0.012, 0.06),
             COL_CREAM)
    make_box("WoolCap_Crown", (-1.28, 0.225, 1.56), (0.15, 0.09, 0.10), COL_WOOLCAP)
    make_box("WoolCap_Fold", (-1.28, 0.235, 1.505), (0.16, 0.10, 0.035), COL_WOOLCAP)
    # Boots on a drip tray east of the door (ch5: he pulls them on)
    make_box("BootTray", (1.40, 0.42, 0.012), (0.55, 0.38, 0.018), P.RUBBER_MAT)
    for bi, bx in enumerate((1.27, 1.53)):
        make_cyl(f"Boot_{bi}_Shaft", (bx, 0.48, 0.17), 0.052, 0.26,
                 (0.24, 0.22, 0.20, 1.0), segments=12)
        make_box(f"Boot_{bi}_Foot", (bx, 0.37, 0.045), (0.11, 0.26, 0.09),
                 (0.24, 0.22, 0.20, 1.0))
    # Co-op delivery crates, stacked (the boxes Finn cycles around)
    make_box("CoopCrate_0", (1.90, 0.85, 0.14), (0.46, 0.36, 0.28), COL_WOOD,
             open_faces={'+Z'})
    make_box("CoopCrate_1", (1.87, 0.88, 0.42), (0.44, 0.34, 0.26), COL_WOOD_LT,
             open_faces={'+Z'})


# ═════════════════════════════════════════════════════════════════
# KITCHEN — the NE corner, kept SPARE (Finn forgets to eat, ch9).
# Counter under the alley window with the sink + the CONE worked
# at the counter (ch12_morning, coffee at five-oh-three), small
# enamel range with THE KETTLE, wax paper roll (ch5), the space
# heater banked in the corner, THE DUFFEL in its nine-month
# corner, the phone charger cord at the outlet (ch5).
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
    # THE CONE + a mug at the counter's west end — "he stood at the
    # counter and worked the cone and the kettle" (ch12_morning)
    _mug("ConeMug", 0.50, wy - 0.36, COUNTER_TOP, COL_MUG_A)
    make_cyl("ConeFilter_Upper", (0.50, wy - 0.36, 1.075), 0.058, 0.06, COL_CREAM)
    make_cyl("ConeFilter_Lower", (0.50, wy - 0.36, 1.030), 0.034, 0.03, COL_CREAM)
    make_box("CoffeeBag", (0.34, wy - 0.24, 1.010), (0.11, 0.08, 0.18),
             (0.34, 0.22, 0.14, 1.0))
    # Wax paper roll (ch5: he wraps the three pieces in wax paper)
    make_cyl("WaxPaper_Roll", (0.72, wy - 0.22, 0.945), 0.030, 0.24,
             P.PAPER_AGED, axis='X')
    # Empty bread board — the sparse kitchen of a man who forgot
    # to eat since yesterday morning (ch9)
    make_box("BreadBoard_Empty", (1.42, wy - 0.30, 0.938), (0.30, 0.22, 0.016),
             COL_WOOD_LT)
    # Open shelf west of the window — two mugs, two plates, tin
    make_box("KitchenShelf", (0.38, wy - 0.16, 1.58), (0.56, 0.26, 0.03), COL_WOOD)
    for ki, sgn in enumerate((-1, +1)):
        make_box(f"KitchenShelf_Bracket_{ki}", (0.38 + sgn * 0.22, wy - 0.06, 1.50),
                 (0.03, 0.09, 0.13), P.METAL_BLACK)
    _mug("ShelfMug_0", 0.22, wy - 0.16, 1.595, COL_MUG_B)
    _mug("ShelfMug_1", 0.40, wy - 0.16, 1.595, COL_CREAM)
    for pi in range(2):
        make_cyl(f"ShelfPlate_{pi}", (0.56, wy - 0.16, 1.615 + pi * 0.018),
                 0.075, 0.014, COL_CREAM, segments=12)
    make_cyl("ShelfTin", (0.38, wy - 0.16, 1.70), 0.040, 0.10, P.METAL_STEEL)
    # Small enamel range in the NE corner + THE KETTLE
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
    # THE SPACE HEATER banked in the corner (ch12_morning) — against
    # the east wall by the range
    make_box("SpaceHeater_Body", (2.02, 3.85, 0.20), (0.16, 0.34, 0.36), COL_HEATER)
    for vi in range(4):
        make_box(f"SpaceHeater_Vent_{vi}", (1.932, 3.85, 0.10 + vi * 0.075),
                 (0.006, 0.26, 0.035), P.METAL_BLACK)
    make_box("SpaceHeater_Glow", (1.938, 3.85, 0.205), (0.004, 0.26, 0.03),
             COL_HEATGLOW)
    for fi, sgn in enumerate((-1, +1)):
        make_box(f"SpaceHeater_Foot_{fi}", (2.02, 3.85 + sgn * 0.13, 0.012),
                 (0.14, 0.04, 0.024), P.METAL_BLACK)
    # THE DUFFEL in the corner — nine months in place (ch12_morning);
    # NW corner, in the crow's sightline from the table chair
    make_cyl("Duffel_Body", (-1.95, 4.62, 0.17), 0.16, 0.55, COL_DUFFEL, axis='X',
             segments=12)
    make_box("Duffel_Strap", (-1.95, 4.62, 0.325), (0.30, 0.05, 0.025), COL_COAT)
    make_box("Duffel_Zip", (-1.95, 4.57, 0.315), (0.50, 0.012, 0.012), COL_ETAPE)
    make_box("Duffel_ClothPeek", (-1.68, 4.62, 0.22), (0.05, 0.16, 0.10), COL_CLOTH)
    # Phone charger at the wall outlet west of the counter (ch5:
    # "Battery's dead. I plugged it in five minutes ago.") — cord
    # only; the phone leaves with Finn.
    make_box("Outlet_Plate", (0.16, wy - 0.095, 0.32), (0.09, 0.02, 0.13), COL_CREAM)
    make_box("Charger_Brick", (0.16, wy - 0.115, 0.345), (0.045, 0.03, 0.05),
             (0.92, 0.90, 0.88, 1.0))
    make_cyl("Charger_CordDrop", (0.16, wy - 0.13, 0.17), 0.005, 0.30,
             (0.92, 0.90, 0.88, 1.0))
    make_cyl("Charger_CordRun", (0.28, wy - 0.13, 0.025), 0.005, 0.30,
             (0.92, 0.90, 0.88, 1.0), axis='X')


# ═════════════════════════════════════════════════════════════════
# THE TABLE — the small kitchen table the whole volume happens at.
# Two chairs: Finn's (south) and "the chair across from him" the
# crow perches on (north). On the folded cloth Tem gave him: the
# COMPLETED HEXAGON — six charred yellow-grain pieces in a ring,
# Olaf's cedar face in the center — with the A R I A piece beside
# it (ch12_morning), the glass of water (ch12_kai), his mug.
# ═════════════════════════════════════════════════════════════════
def build_table():
    tx, ty = 0.50, 2.80
    make_box("Table_Top", (tx, ty, 0.735), (0.95, 0.70, 0.04), COL_WOOD)
    make_box("Table_Apron", (tx, ty, 0.685), (0.80, 0.55, 0.06), COL_WOOD_DARK)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Table_Leg_{li}", (tx + sx * 0.40, ty + sy * 0.28, 0.345),
                 (0.05, 0.05, 0.69), COL_WOOD_DARK)
    _chair("FinnChair", tx, ty - 0.62, 'N', COL_WOOD_LT)          # Finn's seat
    _chair("CrowChair", tx, ty + 0.62, 'S', COL_WOOD_DARK)        # the crow's perch
    # The folded cloth (Tem gave it to him to keep the pieces in)
    make_box("Hex_Cloth", (0.42, 2.80, 0.759), (0.46, 0.44, 0.008), COL_CLOTH)
    make_box("Hex_Cloth_FoldEdge", (0.42, 2.60, 0.765), (0.46, 0.05, 0.010),
             COL_CLOTH)
    # THE HEXAGON — six ring pieces, irregular, edges that fit but
    # were burned apart ("a rough irregular hexagon about ten
    # inches across", ch9). Angled quads, not axis boxes.
    hx, hy, hz = 0.42, 2.80, 0.767
    r_outs = [0.130, 0.118, 0.126, 0.114, 0.128, 0.120]
    r_in = 0.045
    for i in range(6):
        a0 = math.radians(i * 60.0 + 6.0)
        a1 = math.radians((i + 1) * 60.0 - 6.0)
        ro0 = r_outs[i]
        ro1 = r_outs[(i + 1) % 6] * 0.97
        corners = [
            (hx + r_in * math.cos(a0), hy + r_in * math.sin(a0)),
            (hx + ro0 * math.cos(a0), hy + ro0 * math.sin(a0)),
            (hx + ro1 * math.cos(a1), hy + ro1 * math.sin(a1)),
            (hx + r_in * math.cos(a1), hy + r_in * math.sin(a1)),
        ]
        _flat_piece(f"Hex_Ring_{i}", corners, hz, 0.020,
                    COL_CHAR if i % 2 == 0 else COL_CHAR_LT)
        # Unburnt yellow grain showing on alternate pieces
        if i % 2 == 0:
            gm = 0.62
            g_corners = [(hx + (cx - hx) * gm + 0.004, hy + (cy - hy) * gm)
                         for cx, cy in corners]
            _flat_piece(f"Hex_Grain_{i}", g_corners, hz + 0.020, 0.003,
                        COL_GRAIN_YEL)
    # The center piece — Olaf's cedar, the face of the young woman,
    # eyes closed, hair curling (ch12_morning / ch12_kai)
    make_cyl("Hex_Center_Char", (hx, hy, hz + 0.010), 0.048, 0.020, COL_CHAR,
             segments=6)
    make_cyl("Hex_Center_Cedar", (hx, hy, hz + 0.024), 0.042, 0.010, COL_CEDAR,
             segments=6)
    make_cyl("Hexagon_Center_Face", (hx, hy, hz + 0.031), 0.030, 0.004,
             COL_CEDAR_LT, segments=12)
    for ci, (ox, oy) in enumerate([(-0.020, 0.014), (0.0, 0.024), (0.020, 0.014)]):
        make_box(f"Hex_Face_Curl_{ci}", (hx + ox, hy + oy, hz + 0.0345),
                 (0.010, 0.006, 0.003), COL_CEDAR)
    for ei, sgn in enumerate((-1, +1)):
        make_box(f"Hex_Face_Eye_{ei}", (hx + sgn * 0.010, hy + 0.006, hz + 0.0345),
                 (0.009, 0.003, 0.002), COL_WOOD_DARK)
    # The A R I A piece beside the hexagon (letters scratched into
    # the underside — it lies letters-down)
    make_box("Aria_Piece", (0.63, 2.94, 0.777), (0.10, 0.055, 0.018), COL_CHAR_LT)
    make_box("Aria_Piece_Grain", (0.63, 2.94, 0.7875), (0.07, 0.035, 0.004),
             COL_GRAIN_YEL)
    # The glass of water (ch12_kai) + Finn's mug
    make_cyl("WaterGlass", (0.20, 2.62, 0.80), 0.028, 0.09, COL_GLASSISH)
    _mug("TableMug", 0.76, 2.62, 0.755, COL_MUG_B)
    # Braided rug under the table — three flattened rings
    for ri, (rr, rt) in enumerate([(0.80, (0.50, 0.44, 0.36, 1.0)),
                                   (0.56, (0.36, 0.40, 0.38, 1.0)),
                                   (0.32, (0.58, 0.46, 0.32, 1.0))]):
        make_cyl(f"TableRug_Ring_{ri}", (0.50, 2.80, 0.006 + ri * 0.003),
                 rr, 0.008, rt, segments=16)


# ═════════════════════════════════════════════════════════════════
# THE RADIO — canon hero object. A battery portable that "holds
# together on electrical tape" (static_truths.md), picking up the
# unallocated-band signal since June (_VOL7_WIKI), audible through
# the door (ch5), the emergency radio Maya spoke through, with the
# notebook the entry was logged in (ch12_morning). On its own
# small console against the east wall, with the log notebook,
# pencil, tape roll, spare batteries, and the portable UV light.
# ═════════════════════════════════════════════════════════════════
def build_radio_console():
    cx = 1.93          # console center; east wall interior face 2.15
    make_box("RadioConsole_Top", (cx, 1.60, 0.83), (0.40, 0.85, 0.04), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"RadioConsole_Leg_{li}", (cx + sx * 0.16, 1.60 + sy * 0.37, 0.405),
                 (0.045, 0.045, 0.81), COL_WOOD_DARK)
    make_box("RadioConsole_Shelf", (cx, 1.60, 0.30), (0.36, 0.78, 0.03),
             COL_WOOD_DARK)
    # The radio — bakelite body, dial face west (toward the room)
    make_box("Radio_Body", (1.99, 1.52, 0.935), (0.13, 0.30, 0.17), COL_RADIO)
    make_cyl("Radio_DialFace", (1.922, 1.44, 0.955), 0.045, 0.012, COL_CREAM,
             axis='X', segments=12)
    make_box("Radio_DialNeedle", (1.914, 1.44, 0.955), (0.004, 0.006, 0.055),
             COL_MUG_B)
    for si in range(4):
        make_box(f"Radio_SpeakerSlat_{si}", (1.922, 1.565 + si * 0.022, 0.945),
                 (0.008, 0.010, 0.10), COL_WOOD_DARK)
    for ki in range(2):
        make_cyl(f"Radio_Knob_{ki}", (1.922, 1.42 + ki * 0.05, 0.880),
                 0.013, 0.014, COL_CAST_IRON, axis='X')
    # THE ELECTRICAL TAPE — two wrap bands + a taped corner
    for ti, toff in enumerate((-0.085, 0.065)):
        make_box(f"Radio_TapeBand_{ti}", (1.99, 1.52 + toff, 0.935),
                 (0.136, 0.030, 0.176), COL_ETAPE)
    make_box("Radio_TapeCorner", (1.99, 1.665, 1.012), (0.10, 0.035, 0.020),
             COL_ETAPE)
    # Whip antenna off the back corner
    make_cyl("Radio_AntennaBase", (2.035, 1.64, 1.030), 0.010, 0.02, P.METAL_STEEL)
    make_cyl("Radio_AntennaWhip", (2.035, 1.64, 1.30), 0.004, 0.52, P.METAL_STEEL)
    make_cyl("Radio_AntennaTip", (2.035, 1.64, 1.565), 0.007, 0.012, P.METAL_STEEL)
    # The LOG NOTEBOOK + pencil (the Maya entry lives in it, ch12)
    make_box("Radio_LogBook", (1.96, 1.86, 0.860), (0.15, 0.20, 0.020),
             P.PAPER_AGED)
    make_box("Radio_LogBook_Band", (1.96, 1.86, 0.872), (0.15, 0.035, 0.008),
             COL_ETAPE)
    make_cyl("Radio_LogPencil", (1.90, 1.755, 0.856), 0.004, 0.11,
             (0.82, 0.64, 0.28, 1.0), axis='Y')
    # Roll of electrical tape, spare batteries, the UV light
    make_cyl("TapeRoll_Outer", (1.86, 1.32, 0.862), 0.042, 0.022, COL_ETAPE)
    make_cyl("TapeRoll_Core", (1.86, 1.32, 0.876), 0.016, 0.006, COL_CREAM)
    for bi in range(2):
        make_cyl(f"SpareBattery_{bi}", (2.02, 1.28 + bi * 0.045, 0.863),
                 0.013, 0.05, P.METAL_STEEL, axis='Y')
    make_cyl("UVLight_Body", (1.94, 1.20, 0.868), 0.019, 0.13, COL_CAST_IRON,
             axis='Y')
    make_cyl("UVLight_Lens", (1.94, 1.128, 0.868), 0.021, 0.014, COL_UV_LENS,
             axis='Y')
    # Wall outlet + the radio's cord (it runs on the wall feed at
    # home, batteries on the trail)
    make_box("RadioOutlet_Plate", (2.135, 1.90, 0.30), (0.02, 0.09, 0.13),
             COL_CREAM)
    make_cyl("Radio_CordDrop", (2.10, 1.90, 0.56), 0.005, 0.52, COL_ETAPE)


# ═════════════════════════════════════════════════════════════════
# BEDROOM ANNEX — through the OPEN door in the north wall (the
# crow flies low through the doorway, ch12_morning). The bed Finn
# lies down on at noon (ch12_kai), THE CHAIR BESIDE THE BED the
# crow watches him from, the wool socks laid by the bed, the
# folded jeans + thermal on the dresser.
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
    # Bedroom door — OPEN, swung into the main room, parked against
    # the north wall east of the doorway
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
    # The bed — head against the annex north wall
    make_box("Bed_Frame", (-1.58, 6.20, 0.17), (1.10, 1.76, 0.14), COL_WOOD_DARK)
    make_box("Bed_Headboard", (-1.58, 7.05, 0.52), (1.14, 0.06, 0.64), COL_WOOD_DARK)
    make_box("Bed_Mattress", (-1.58, 6.20, 0.32), (1.02, 1.68, 0.14), COL_LINEN)
    make_box("Bed_Blanket", (-1.58, 6.02, 0.405), (1.04, 1.24, 0.045), COL_BLANKET)
    make_box("Bed_Blanket_Band", (-1.58, 5.62, 0.407), (1.045, 0.12, 0.047),
             COL_BLANKBAND)
    make_box("Bed_Pillow", (-1.58, 6.82, 0.42), (0.52, 0.30, 0.10), COL_LINEN)
    # THE CHAIR BESIDE THE BED — the crow's bedroom perch
    # (ch12_morning / ch12_kai); no crow baked, it moves per scene
    _chair("BedsideChair", -0.82, 6.50, 'W', COL_WOOD_LT)
    # Wool socks laid by the bed (ch12_morning)
    for si in range(2):
        make_cyl(f"WoolSock_{si}", (-1.06 + si * 0.10, 5.68 + si * 0.04, 0.028),
                 0.028, 0.13, COL_WOOL_SOCK, axis='Y')
    # Dresser on the annex east wall — folded jeans + thermal on top
    make_box("Dresser_Body", (-0.80, 5.52, 0.40), (0.44, 0.66, 0.80), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (-0.578, 5.52, 0.64 - di * 0.22),
                 (0.015, 0.54, 0.18), COL_WOOD_LT)
        make_cyl(f"Dresser_Knob_{di}", (-0.565, 5.52, 0.64 - di * 0.22),
                 0.013, 0.025, COL_BRASS, axis='X')
    make_box("Folded_Jeans", (-0.80, 5.40, 0.835), (0.30, 0.24, 0.06), COL_DENIM)
    make_box("Folded_Thermal", (-0.80, 5.66, 0.825), (0.28, 0.22, 0.045),
             COL_THERMAL)
    # Small rug beside the bed + flush ceiling light
    make_box("Anx_BedRug", (-1.30, 5.50, 0.006), (0.80, 0.45, 0.012),
             (0.38, 0.44, 0.42, 1.0))
    _flush_dome("Anx_CeilLight", -1.35, 6.20, ANX_CEIL)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — warm pendant over the table (the kitchen light
# Finn holds the wood up to, ch12_morning), flush dome over the
# counter, smoke detector. NO fluorescents — rooms over a shop.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    make_cyl("Pendant_Canopy", (0.50, 2.85, CEIL - 0.02), 0.05, 0.04, P.METAL_BLACK)
    make_cyl("Pendant_Cord", (0.50, 2.85, CEIL - 0.275), 0.008, 0.55, P.METAL_BLACK)
    make_cyl("Pendant_Shade", (0.50, 2.85, CEIL - 0.615), 0.13, 0.13,
             (0.34, 0.42, 0.38, 1.0), segments=12)
    make_cyl("Pendant_Bulb", (0.50, 2.85, CEIL - 0.685), 0.045, 0.035,
             COL_GLOW_WARM)
    _flush_dome("Kitchen_CeilLight", 0.95, 4.35, CEIL)
    make_smoke_detector("Smoke", (-0.7, 2.3, CEIL))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · STREET (west) — the connective stretch at the Hemlock
# corner, one storey down: THE CLOSED KAYAK SHOP below (papered
# windows, faded sign board, the relic kayak leaning by the door,
# the foundation's plaque), the street door to Finn's stairs,
# FINN'S TRUCK at the curb (ch5 / ch9), streetlamp, wet asphalt,
# the dark facade across the street with a few pre-dawn windows.
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
    make_box("Street_Puddle_0", (-5.7, 4.4, STREET_Z + 0.004), (1.20, 0.60, 0.004),
             COL_PUDDLE)
    make_box("Street_Puddle_1", (-3.3, 0.9, STREET_Z + 0.036 + 0.041),
             (0.70, 0.45, 0.004), COL_PUDDLE)
    # ── The kayak shop's street face below the apartment ─────────
    make_box("Shop_StreetFace", (-2.42, 2.5, -1.62), (0.15, 5.9, 3.36),
             COL_SHOPFACE)
    make_box("Shop_Cornice", (-2.52, 2.5, -0.18), (0.30, 5.9, 0.20), COL_SHOPTRIM)
    make_box("Shop_Bulkhead", (-2.505, 2.75, -3.05), (0.06, 3.4, 0.50), COL_SHOPTRIM)
    # Papered-over display windows either side of the shop door
    for wi, wyy in enumerate((1.75, 3.75)):
        make_box(f"Shop_Window_Frame_{wi}", (-2.50, wyy, -1.95), (0.06, 1.30, 1.66),
                 COL_SHOPTRIM)
        make_box(f"Shop_Window_Paper_{wi}", (-2.515, wyy, -2.10), (0.05, 1.14, 1.20),
                 COL_PAPERED)
        make_box(f"Shop_Window_DarkGap_{wi}", (-2.515, wyy, -1.32), (0.05, 1.14, 0.30),
                 COL_GLASS_DK)
    # The shop door — recessed, dark, a small white CLOSED card
    make_box("Shop_Door", (-2.505, 2.75, -2.30), (0.06, 0.90, 1.98), COL_WOOD_DARK)
    make_box("Shop_Door_ClosedCard", (-2.545, 2.60, -1.90), (0.02, 0.16, 0.11),
             COL_CREAM)
    make_cyl("Shop_Door_Knob", (-2.55, 3.06, -2.35), 0.024, 0.04, COL_BRASS,
             axis='X')
    # THE SIGN BOARD over the storefront — faded; Label3D target
    make_box("KayakShop_SignBoard", (-2.53, 2.75, -0.58), (0.06, 2.20, 0.42),
             (0.84, 0.78, 0.62, 1.0))
    for sgn in (-1, +1):
        make_box(f"KayakShop_SignTrim_{sgn:+d}", (-2.535, 2.75 + sgn * 1.14, -0.58),
                 (0.07, 0.06, 0.46), COL_SHOPTRIM)
    # The relic kayak stood on end beside the shop door
    make_box("Kayak_Hull", (-2.58, 3.42, -2.12), (0.14, 0.50, 2.30), COL_KAYAK)
    make_box("Kayak_Deck", (-2.63, 3.42, -2.12), (0.06, 0.38, 2.24), COL_KAYAK_DK)
    make_box("Kayak_Cockpit", (-2.665, 3.42, -1.70), (0.02, 0.26, 0.58),
             COL_GLASS_DK)
    # The foundation's plaque by the door (the building is theirs,
    # ch5; Vestergaard plaque register, ch12_morning)
    make_box("Foundation_Plaque", (-2.545, 2.28, -1.60), (0.02, 0.24, 0.16),
             COL_BRASS)
    # Finn's street door — the stairs up (ch9: "they went down the
    # stairs together"); south end of the face
    make_box("StairDoor_Leaf", (-2.505, 0.62, -2.32), (0.06, 0.85, 1.96),
             COL_WOOD_DARK)
    make_box("StairDoor_Transom", (-2.505, 0.62, -1.22), (0.06, 0.85, 0.24),
             COL_WARM_WIN)
    make_cyl("StairDoor_Knob", (-2.55, 0.32, -2.36), 0.024, 0.04, COL_BRASS,
             axis='X')
    make_box("StairDoor_Stoop", (-2.72, 0.62, STREET_Z + 0.09), (0.50, 1.10, 0.10),
             COL_CONCRETE)
    # ── FINN'S TRUCK at the curb (ch5 / ch9 / ch12) ──────────────
    tx, tyc = -5.1, 3.35
    make_box("Truck_BodyBase", (tx, tyc, -2.72), (1.72, 4.60, 0.46), COL_TRUCK)
    make_box("Truck_BedWall_W", (tx - 0.83, tyc - 1.15, -2.29), (0.06, 2.20, 0.40),
             COL_TRUCK)
    make_box("Truck_BedWall_E", (tx + 0.83, tyc - 1.15, -2.29), (0.06, 2.20, 0.40),
             COL_TRUCK)
    make_box("Truck_Tailgate", (tx, tyc - 2.25, -2.29), (1.60, 0.06, 0.40),
             COL_TRUCK)
    make_box("Truck_Cab", (tx, tyc + 0.67, -2.18), (1.60, 1.45, 0.62), COL_TRUCK)
    make_box("Truck_Windshield", (tx, tyc + 1.37, -2.05), (1.35, 0.05, 0.40),
             COL_GLASS_DK)
    make_box("Truck_RearWindow", (tx, tyc - 0.03, -2.05), (1.30, 0.05, 0.32),
             COL_GLASS_DK)
    for wi, sgn in enumerate((-1, +1)):
        make_box(f"Truck_SideWindow_{wi}", (tx + sgn * 0.78, tyc + 0.67, -2.06),
                 (0.05, 1.00, 0.34), COL_GLASS_DK)
    make_box("Truck_Hood", (tx, tyc + 1.85, -2.32), (1.62, 0.95, 0.34), COL_TRUCK)
    make_box("Truck_Grille", (tx, tyc + 2.31, -2.62), (1.30, 0.04, 0.25),
             COL_TRUCK_DK)
    for hi, sgn in enumerate((-1, +1)):
        make_cyl(f"Truck_Headlight_{hi}", (tx + sgn * 0.60, tyc + 2.32, -2.55),
                 0.070, 0.03, COL_CREAM, axis='Y', segments=12)
    for wi, (wx_off, wy_off) in enumerate([(-0.80, -1.60), (0.80, -1.60),
                                           (-0.80, 1.40), (0.80, 1.40)]):
        make_cyl(f"Truck_Wheel_{wi}", (tx + wx_off, tyc + wy_off, -2.97),
                 0.33, 0.26, COL_CAST_IRON, axis='X', segments=12)
        make_cyl(f"Truck_Hub_{wi}", (tx + wx_off * 1.17, tyc + wy_off, -2.97),
                 0.10, 0.03, P.METAL_STEEL, axis='X', segments=12)
    make_box("Truck_Bumper_R", (tx, tyc - 2.32, -2.80), (1.66, 0.08, 0.14),
             P.METAL_STEEL)
    # Streetlamp on the buffer strip (playbook: edge of road)
    make_cyl("Streetlamp_Pole", (-4.15, 4.55, STREET_Z + 2.25), 0.045, 4.50,
             P.METAL_BLACK, segments=12)
    make_cyl("Streetlamp_Arm", (-3.95, 4.55, 1.06), 0.022, 0.40, P.METAL_BLACK,
             axis='X')
    make_cyl("Streetlamp_Head", (-3.75, 4.55, 1.00), 0.09, 0.14, P.METAL_BLACK,
             segments=12)
    make_cyl("Streetlamp_Glow", (-3.75, 4.55, 0.91), 0.065, 0.05, COL_GLOW_WARM,
             segments=12)
    # The facade across the street — dark, a few windows lit before
    # dawn (the town at four-forty-two, ch12_morning)
    make_box("Opposite_Facade", (-9.4, 2.5, 0.2), (0.20, 11.0, 7.4),
             (0.20, 0.19, 0.20, 1.0))
    for wi, (wyy, wz) in enumerate([(0.8, 0.5), (3.6, 1.7), (5.4, -0.8)]):
        make_box(f"Opposite_LitWindow_{wi}", (-9.28, wyy, wz), (0.02, 0.60, 0.90),
                 COL_WARM_WIN)
    for wi, (wyy, wz) in enumerate([(2.2, 0.6), (4.6, -0.9), (1.1, -1.1)]):
        make_box(f"Opposite_DarkWindow_{wi}", (-9.28, wyy, wz), (0.02, 0.60, 0.90),
                 (0.10, 0.10, 0.12, 1.0))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · ALLEY (north) — "the alley that ran behind the
# bakery" (ch12_morning): the bakery's back wall opposite with its
# door, caged lamp and lit pre-dawn windows (bakers up at four),
# bread crates, the downspout whose dripping is the alley's other
# sound, puddles, dumpster. Annex hull-wrapped per playbook.
# ═════════════════════════════════════════════════════════════════
def build_exterior_alley():
    make_box("Alley_Ground", (0.5, 8.15, STREET_Z - 0.05), (10.0, 3.3, 0.10),
             COL_ASPHALT)
    make_box("Alley_Puddle_0", (1.4, 8.0, STREET_Z + 0.004), (1.30, 0.55, 0.004),
             COL_PUDDLE)
    make_box("Alley_Puddle_1", (-1.1, 8.5, STREET_Z + 0.004), (0.80, 0.45, 0.004),
             COL_PUDDLE)
    # Our building's alley face east of the annex, window to grade
    make_box("Bldg_AlleyFace", (1.03, 5.13, -1.62), (2.85, 0.15, 3.36), COL_BRICK)
    make_box("Bldg_AlleyFace_Course", (1.03, 5.21, -0.15), (2.85, 0.02, 0.10),
             COL_BRICK_DK)
    # The downspout — the dripping in the alley (ch12_morning)
    make_cyl("Downspout_Pipe", (2.30, 5.28, -1.65), 0.045, 3.30, COL_CAST_IRON,
             segments=12)
    make_cyl("Downspout_Shoe", (2.30, 5.42, -3.22), 0.045, 0.28, COL_CAST_IRON,
             axis='Y', segments=12)
    make_cyl("Downspout_DripPuddle", (2.30, 5.72, STREET_Z + 0.005), 0.28, 0.006,
             COL_PUDDLE, segments=12)
    # Annex hull skin (playbook: every annex gets wrapped) + fill
    # to grade
    make_box("Anx_Skin_W", (-2.45, 6.15, ANX_CEIL / 2.0),
             (0.10, 2.40, ANX_CEIL + 0.2), COL_BRICK)
    make_box("Anx_Skin_N", ((ANX_X0 + ANX_X1) / 2.0, 7.30, ANX_CEIL / 2.0),
             (ANX_X1 - ANX_X0 + 0.7, 0.10, ANX_CEIL + 0.2), COL_BRICK)
    make_box("Anx_Skin_E", (-0.25, 6.15, ANX_CEIL / 2.0),
             (0.10, 2.40, ANX_CEIL + 0.2), COL_BRICK)
    make_box("Anx_Skin_Roof", ((ANX_X0 + ANX_X1) / 2.0, 6.15, ANX_CEIL + 0.22),
             (ANX_X1 - ANX_X0 + 0.9, 2.60, 0.12), COL_BRICK_DK)
    make_box("Anx_Skin_Under", ((ANX_X0 + ANX_X1) / 2.0, 6.15, -1.62),
             (ANX_X1 - ANX_X0 + 0.6, 2.40, 3.36), COL_BRICK)
    # The bakery's back wall opposite
    make_box("Bakery_BackWall", (0.4, 8.95, 0.0), (10.5, 0.20, 6.80), COL_BRICK_DK)
    make_box("Bakery_BackDoor", (-0.6, 8.83, -2.30), (0.95, 0.05, 2.00),
             P.METAL_STEEL)
    make_box("Bakery_DoorStep", (-0.6, 8.60, STREET_Z + 0.10), (1.20, 0.50, 0.14),
             COL_CONCRETE)
    # Caged lamp over the bakery door — warm, lit (bakers pre-dawn)
    make_box("Bakery_LampBracket", (-0.6, 8.80, -1.10), (0.08, 0.14, 0.08),
             P.METAL_BLACK)
    make_cyl("Bakery_LampGlobe", (-0.6, 8.70, -1.20), 0.070, 0.13, COL_GLOW_WARM,
             segments=12)
    for gi in range(3):
        make_box(f"Bakery_LampCage_{gi}", (-0.6, 8.70, -1.12 - gi * 0.08),
                 (0.16, 0.16, 0.012), P.METAL_BLACK, open_faces={'+Z', '-Z'})
    # High back windows, lit warm — the bakery awake at four-forty-
    # two (ch12_morning)
    for wi, wxx in enumerate((0.9, 2.1, 3.3)):
        make_box(f"Bakery_LitWindow_{wi}", (wxx, 8.83, -0.85), (0.85, 0.03, 0.55),
                 COL_WARM_WIN)
        make_box(f"Bakery_WindowSill_{wi}", (wxx, 8.81, -1.16), (0.95, 0.06, 0.06),
                 COL_CONCRETE)
    # Bread crates by the bakery door
    make_box("BreadCrate_0", (0.35, 8.62, STREET_Z + 0.16), (0.50, 0.36, 0.30),
             COL_WOOD, open_faces={'+Z'})
    make_box("BreadCrate_1", (0.38, 8.60, STREET_Z + 0.46), (0.48, 0.34, 0.28),
             COL_WOOD_LT, open_faces={'+Z'})
    make_box("BreadCrate_2", (0.95, 8.64, STREET_Z + 0.15), (0.48, 0.34, 0.28),
             COL_WOOD, open_faces={'+Z'})
    # Dumpster further down
    make_box("Dumpster_Body", (3.3, 8.45, STREET_Z + 0.575), (1.50, 0.90, 1.05),
             (0.24, 0.34, 0.30, 1.0))
    make_box("Dumpster_Lid", (3.3, 8.31, STREET_Z + 1.13), (1.54, 0.66, 0.06),
             (0.18, 0.26, 0.24, 1.0))
    make_box("Dumpster_LidBack", (3.3, 8.74, STREET_Z + 1.21), (1.54, 0.26, 0.06),
             (0.18, 0.26, 0.24, 1.0))


def main():
    clear_scene()
    build_shell()
    build_windows()
    build_entry()
    build_kitchen()
    build_table()
    build_radio_console()
    build_bedroom()
    build_ceiling_infra()
    build_exterior_street()
    build_exterior_alley()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/finn_apartment.glb"))
    print(f"\n[build_finn_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
