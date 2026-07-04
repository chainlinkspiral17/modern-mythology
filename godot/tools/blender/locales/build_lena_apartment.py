"""Lena Vargas's apartment — vol7 hero locale (Smolvud, OR).

One-bedroom over THE SALTY TOME bookshop (Petra's building, "a
hundred and four years old", vol7_ch10_morning), up a stairwell
from the street. 13 vol7 scene JSONs render here (ch3 ×2, ch6
×2, ch7 ×2, ch8 ×5, ch10, ch12); the mood is
vol7_apartment_rain: "Six o'clock. Four coats on four hooks."
PNW register — warm fir and plaster, rain-lit, kept-not-curated.
Canon sources baked in:

  · vol7_ch3_apartment: kettle on the stove, the cone filter +
    the dark French Soren gave her, the couch with the wool
    blanket Lena keeps folded over the back, the end table
    beside the couch, the chair across, the window over the
    kitchen sink looking at the alley + the STARFISH NEBULA
    mural she painted (and its four patches), the radiator pipe
    in the corner that clicks whether the heat is on or off,
    the thermostat above the bed reading sixty-one.
  · vol7_ch8_six_oclock: "the row of hooks by the door, which
    had, in three years, never had more than one coat on it at
    a time. Four hooks, four coats." — four hooks are baked;
    ONE wax-canvas coat hangs (the apartment's normal state;
    the Estuary 7 stick lives in its inside pocket per
    vol7_ch7_night). Kai took the chair by the window; the
    small wooden side table by the chair; the small portable
    space heater "because the apartment did not warm up
    otherwise"; the front window she looks DOWN from at
    Hemlock when Finn's truck pulls up.
  · vol7_ch8_the_table: the small round oak table from the
    seventies with a wobble in one leg she's been meaning to
    shim (Tem has a shim at the cabin); four chairs "not a
    matched set" — three from Margit's, one from the previous
    tenant; second drawer down holds four bowls + four spoons.
  · vol7_ch10_morning: the steel kettle bought at Margit's for
    nine tokens ("the kettle her grandmother had used in
    Salem"), the hand grinder on the counter, the cast iron on
    the stove, the small fridge (eggs on the second shelf, the
    cheddar), the braided rag rug in front of the sink, the
    small dish drainer, the side table outside the bedroom
    where she keeps the lamp she does not use, the orange of
    the laundromat's safety light in the alley, the three
    ceiling water stains above the closet (the upstairs
    neighbor's 2050 bathtub leak — fixed in '51, never painted
    over: "a lie she did not want to live with").
  · vol7_ch12_lena: boots by the door; the Daily Grind apron
    over the back of the kitchen chair.
  · vol7_ch7_night: the deadbolt she locks for the first time
    in three years; her phone on the side table; the dishes
    rinsed and stacked on the small drainer.
  · lore/_VOL6_VOL7_LOCALES_MANIFEST.md: "The writing desk
    where Static Truths gets laid out" — the zine desk on the
    east wall (paste-up flats, masthead, issue stack with the
    octopus back cover; the actual copier is downstairs in the
    Salty Tome back room per static_truths.md, so no print
    machinery up here).

NO record player, NO radio — canon has neither (Finn owns the
radio; Lena doesn't even own a stick reader). The room's music
is rain. No paintings hang here either — her studio is behind
the Daily Grind; the only "gallery" is the mural OUT the window.

Shell footprint kept from the scaffold (5 × 5 m, door gap in the
south wall x −1..+1) — the .tscn lights and the Background3D
camera preset (0, 2.30, +0.5 / yaw 180 / fov 60, same preset as
daily_grind_interior) are tuned to it. Windows are REAL OPENINGS
with frames + mullions, no glass (playbook no-transparency
rule). The bedroom is a small annex north of the main room with
its door open — canon says bedroom-off-a-hall; the hall is
abstracted to the doorway so the wake-up scenes still read.
Sloped garret ceiling over the east strip (roof pitch of a
building this age), writing desk tucked under it.

Text panels bake as named vertex-color meshes for scene-side
Label3D: Zine_Masthead, Zine_Stack_TopBack, SaltyTome_SignBoard,
Thermostat_Screen.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, _finalize_mesh
from _props.structure import make_floor, make_wall, make_crown_molding, make_door_hinges
from _props.decor import make_floor_plant
from _props.safety import make_smoke_detector

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 5.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.88, 0.83, 0.74, 1.0),   # warm plaster
            "baseboard": (0.44, 0.33, 0.23, 1.0)}
COL_FLOOR = (0.58, 0.44, 0.31, 1.0)            # fir floorboards
COL_SEAM  = (0.35, 0.26, 0.18, 1.0)

# ── Apartment palette (2025 PNW, warm + muted) ───────────────────
COL_WOOD      = (0.48, 0.35, 0.22, 1.0)   # walnut / old oak
COL_WOOD_DARK = (0.28, 0.21, 0.15, 1.0)
COL_WOOD_LT   = (0.66, 0.52, 0.34, 1.0)   # 70s golden oak (the table)
COL_BUTCHER   = (0.72, 0.58, 0.38, 1.0)
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_CREAM     = (0.90, 0.87, 0.80, 1.0)
COL_GLASSISH  = (0.72, 0.78, 0.78, 1.0)   # opaque stand-in for jar glass
COL_ENAMEL    = (0.86, 0.88, 0.86, 1.0)   # old range enamel
COL_CAST_IRON = (0.13, 0.13, 0.14, 1.0)
COL_RAINCOAT  = (0.38, 0.36, 0.26, 1.0)   # wax canvas (town uniform)
COL_UPHOLSTER = (0.42, 0.46, 0.42, 1.0)   # mossy wool couch
COL_ARMCHAIR  = (0.55, 0.32, 0.22, 1.0)   # rust wool chair
COL_WOOL_BASE = (0.78, 0.72, 0.62, 1.0)   # blanket ground
COL_WOOL_BAND = (0.62, 0.30, 0.24, 1.0)   # blanket stripe (madder red)
COL_WOOL_BND2 = (0.30, 0.38, 0.44, 1.0)   # blanket stripe (spruce blue)
COL_LINEN     = (0.90, 0.88, 0.82, 1.0)
COL_PLANT     = (0.36, 0.47, 0.32, 1.0)
COL_POT       = (0.58, 0.38, 0.26, 1.0)
COL_APRON     = (0.30, 0.26, 0.22, 1.0)   # Daily Grind waxed apron
COL_BRICK     = (0.44, 0.28, 0.22, 1.0)   # building fabric, alley face
COL_BRICK_DK  = (0.32, 0.20, 0.16, 1.0)
COL_CONCRETE  = (0.55, 0.54, 0.51, 1.0)
COL_ASPHALT   = (0.15, 0.15, 0.16, 1.0)
COL_PUDDLE    = (0.30, 0.33, 0.36, 1.0)
COL_STAIN     = (0.62, 0.55, 0.42, 1.0)   # ceiling water stains
COL_RADIATOR  = (0.68, 0.66, 0.60, 1.0)   # many-coats-of-paint cast iron
COL_CORK      = (0.60, 0.45, 0.30, 1.0)
COL_MAT_GREEN = (0.32, 0.40, 0.36, 1.0)   # cutting mat
# Starfish Nebula mural (out the kitchen window)
COL_MURAL_GROUND = (0.14, 0.12, 0.26, 1.0)   # deep indigo night
COL_MURAL_OCTO   = (0.82, 0.52, 0.30, 1.0)   # warm octopus
COL_MURAL_STAR   = (0.90, 0.82, 0.52, 1.0)   # starfish kite
COL_MURAL_POOL   = (0.24, 0.48, 0.48, 1.0)   # tide pool teal
COL_MURAL_ARCH   = (0.72, 0.56, 0.38, 1.0)   # sandstone arches
COL_MURAL_TOWER  = (0.56, 0.24, 0.20, 1.0)   # radio-tower lattice
COL_PATCH        = (0.46, 0.46, 0.44, 1.0)   # the gray patches eating it
COL_ORANGE_LAMP  = (0.96, 0.62, 0.26, 1.0)   # laundromat safety light
# Mismatched chair + mug tints (muted)
CHAIR_TINTS = [COL_WOOD_LT, (0.34, 0.48, 0.46, 1.0), COL_WOOD_DARK,
               (0.62, 0.34, 0.22, 1.0)]
MUG_TINTS = [(0.72, 0.30, 0.22, 1.0), (0.34, 0.48, 0.46, 1.0),
             (0.82, 0.64, 0.28, 1.0), (0.38, 0.44, 0.56, 1.0),
             (0.90, 0.87, 0.80, 1.0)]
BOOK_TINTS = [(0.48, 0.30, 0.24, 1.0), (0.28, 0.36, 0.42, 1.0),
              (0.62, 0.54, 0.34, 1.0), (0.36, 0.30, 0.38, 1.0),
              (0.70, 0.64, 0.52, 1.0)]

COUNTER_TOP = 0.93          # kitchen counter surface z
# Sloped garret ceiling over the east strip:
SLOPE_X0, SLOPE_X1 = 1.35, 2.70    # flat 2.60 at x0 → 2.05 at wall
SLOPE_Z0, SLOPE_Z1 = 2.60, 2.05
EAST_WALL_H = 2.05
# Bedroom annex (north of the main room, doorway x −1.9..−1.0)
ANX_X0, ANX_X1 = -2.40, -0.50      # interior extents
ANX_Y0, ANX_Y1 = ROOM_D + 0.10, ROOM_D + 2.30
ANX_CEIL = 2.45
STREET_Z = -3.55                    # Hemlock / alley grade (upstairs flat)


# ═════════════════════════════════════════════════════════════════
# Local helpers (deterministic, axis-aligned; wedge for the slope)
# ═════════════════════════════════════════════════════════════════
def _wedge_slab(name, x0, x1, zb0, zb1, y0, y1, thick, color):
    """Slab whose underside runs from z=zb0 at x=x0 to z=zb1 at
    x=x1 (constant along Y), `thick` measured vertically. Vertex
    layout + winding mirror make_box so faces render correctly."""
    verts = [
        (x0, y0, zb0), (x1, y0, zb1), (x1, y1, zb1), (x0, y1, zb0),
        (x0, y0, zb0 + thick), (x1, y0, zb1 + thick),
        (x1, y1, zb1 + thick), (x0, y1, zb0 + thick),
    ]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (2, 3, 7, 6), (3, 0, 4, 7), (1, 2, 6, 5)]
    return _finalize_mesh(name, verts, list(faces), color)

_DIRS = {'N': (0.0, 1.0), 'S': (0.0, -1.0), 'E': (1.0, 0.0), 'W': (-1.0, 0.0)}

def _chair(prefix, cx, cy, facing, tint):
    """Kitchen chair; `facing` = direction the sitter faces."""
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

def _small_table(prefix, cx, cy, r, tint, top_z=0.55):
    """Little round side / end table."""
    make_cyl(f"{prefix}_Top", (cx, cy, top_z), r, 0.035, tint, segments=12)
    make_cyl(f"{prefix}_Column", (cx, cy, top_z / 2.0), 0.035, top_z - 0.05,
             COL_WOOD_DARK)
    make_cyl(f"{prefix}_Base", (cx, cy, 0.02), r * 0.6, 0.04, COL_WOOD_DARK,
             segments=12)

def _mug(prefix, cx, cy, bz, tint):
    make_cyl(f"{prefix}_Body", (cx, cy, bz + 0.048), 0.038, 0.095, tint)
    make_box(f"{prefix}_Handle", (cx + 0.048, cy, bz + 0.050),
             (0.016, 0.014, 0.05), tint)

def _book_stack(prefix, cx, cy, bz, count, start=0):
    for bi in range(count):
        w = 0.19 - (bi % 3) * 0.015
        d = 0.14 - ((bi + 1) % 2) * 0.012
        make_box(f"{prefix}_{bi}", (cx + (bi % 2) * 0.014, cy - (bi % 3) * 0.01,
                 bz + 0.019 + bi * 0.038), (w, d, 0.036),
                 BOOK_TINTS[(start + bi) % len(BOOK_TINTS)])

def _pendant(prefix, cx, cy, ceil_z, drop, shade_tint):
    """Cylinder-shade pendant — round geometry at eye level."""
    make_cyl(f"{prefix}_Canopy", (cx, cy, ceil_z - 0.02), 0.05, 0.04, P.METAL_BLACK)
    make_cyl(f"{prefix}_Cord", (cx, cy, ceil_z - drop / 2.0), 0.008, drop,
             P.METAL_BLACK)
    make_cyl(f"{prefix}_Shade", (cx, cy, ceil_z - drop - 0.065), 0.13, 0.13,
             shade_tint, segments=12)
    make_cyl(f"{prefix}_Bulb", (cx, cy, ceil_z - drop - 0.135), 0.045, 0.035,
             (0.98, 0.88, 0.62, 1.0))


# ═════════════════════════════════════════════════════════════════
# SHELL — scaffold footprint, fir floor, plaster walls with the
# two window openings + bedroom doorway carved, sloped garret
# ceiling over the east strip (knee wall 2.05), plank ceiling.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # South wall — scaffold door gap x −1..+1 kept (camera preset
    # sits just inside it)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             PAL_WALL["wall"])
    # Entry-gap infill either side of the actual 0.95 m door leaf
    for nm, fx in [("Wall_S_FillW", -0.775), ("Wall_S_FillE", +0.775)]:
        make_box(nm, (fx, 0.0, 1.15), (0.45, 0.20, 2.30), PAL_WALL["wall"])
    # West wall — front window opening y 2.9..4.1, z 0.85..2.25
    # (the window Lena looks DOWN from at Hemlock, vol7_ch8)
    make_wall("Wall_W_S", (-ROOM_W / 2.0, 1.35, 0), length=3.10, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_W_N", (-ROOM_W / 2.0, 4.65, 0), length=1.10, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_W_Sill", (-ROOM_W / 2.0, 3.5, 0.425), (0.20, 1.20, 0.85),
             PAL_WALL["wall"])
    make_box("Wall_W_SillBase", (-ROOM_W / 2.0 + 0.06, 3.5, 0.08), (0.06, 1.20, 0.16),
             PAL_WALL["baseboard"])
    make_box("Wall_W_Header", (-ROOM_W / 2.0, 3.5, 2.425), (0.20, 1.20, 0.35),
             PAL_WALL["wall"])
    # North wall — bedroom doorway x −1.9..−1.0, kitchen window
    # x 0.7..1.8 (z 1.0..2.2, over the sink)
    make_wall("Wall_N_W", (-2.30, ROOM_D, 0), length=0.80, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_M", (-0.15, ROOM_D, 0), length=1.70, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (2.25, ROOM_D, 0), length=0.90, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveBedDoor", (-1.45, ROOM_D, 2.30), (0.90, 0.20, 0.60),
             PAL_WALL["wall"])
    make_box("Wall_N_WinSill", (1.25, ROOM_D, 0.50), (1.10, 0.20, 1.00),
             PAL_WALL["wall"])
    make_box("Wall_N_WinHeader", (1.25, ROOM_D, 2.40), (1.10, 0.20, 0.40),
             PAL_WALL["wall"])
    # East wall — knee wall under the roof slope
    make_wall("Wall_E", (+ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=EAST_WALL_H, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    # Ceiling — painted plank flat portion + sloped garret wedge
    flat_x0, flat_x1 = -2.70, SLOPE_X0
    make_box("Ceil_Flat", ((flat_x0 + flat_x1) / 2.0, ROOM_D / 2.0, CEIL + 0.05),
             (flat_x1 - flat_x0, ROOM_D + 0.4, 0.10), (0.82, 0.78, 0.70, 1.0))
    for bi, bx in enumerate((-2.0, -1.0, 0.0, 1.0)):
        make_box(f"Ceil_Batten_{bi}", (bx, ROOM_D / 2.0, CEIL - 0.008),
                 (0.05, ROOM_D + 0.4, 0.016), (0.60, 0.50, 0.38, 1.0))
    _wedge_slab("Ceil_Slope", SLOPE_X0, SLOPE_X1, SLOPE_Z0, SLOPE_Z1,
                -0.20, ROOM_D + 0.20, 0.10, (0.82, 0.78, 0.70, 1.0))
    for ri, ry in enumerate((0.9, 2.5, 4.1)):
        _wedge_slab(f"Ceil_Rafter_{ri}", SLOPE_X0, SLOPE_X1 - 0.10,
                    SLOPE_Z0 - 0.09, SLOPE_Z1 - 0.09, ry - 0.045, ry + 0.045,
                    0.09, (0.42, 0.31, 0.21, 1.0))
    # Crown molding on the full-height walls only (slope side gets
    # the rafters instead)
    make_crown_molding("Crown_W", wall_x=-ROOM_W / 2.0 + 0.10, wall_y=ROOM_D / 2.0,
                       length=ROOM_D, axis='Y', ceil_z=CEIL,
                       palette={"wood": COL_WOOD})
    make_crown_molding("Crown_N", wall_x=-0.575, wall_y=ROOM_D - 0.10,
                       length=3.85, axis='X', ceil_z=CEIL,
                       palette={"wood": COL_WOOD})
    make_crown_molding("Crown_S", wall_x=-0.575, wall_y=0.10,
                       length=3.85, axis='X', ceil_z=CEIL,
                       palette={"wood": COL_WOOD})


# ═════════════════════════════════════════════════════════════════
# WINDOWS — openings get wood frames + mullions, NO glass (playbook
# rule). West = front window over Hemlock; north = the window over
# the kitchen sink that looks at the Starfish Nebula.
# ═════════════════════════════════════════════════════════════════
def build_windows():
    # West front window: opening y 2.9..4.1, z 0.85..2.25
    wx = -ROOM_W / 2.0
    make_box("WinW_Sill", (wx, 3.5, 0.815), (0.22, 1.32, 0.07), COL_WOOD)
    make_box("WinW_Ledge", (wx + 0.14, 3.5, 0.855), (0.14, 1.20, 0.03), COL_WOOD)
    make_box("WinW_Head", (wx, 3.5, 2.285), (0.22, 1.32, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinW_Jamb_{sgn:+d}", (wx, 3.5 + sgn * 0.63, 1.55),
                 (0.22, 0.06, 1.54), COL_WOOD)
    # Double-hung look: meeting rail + one vertical mullion per sash
    make_box("WinW_MeetRail", (wx, 3.5, 1.57), (0.14, 1.20, 0.06), COL_WOOD)
    make_box("WinW_MullLo", (wx, 3.5, 1.20), (0.12, 0.05, 0.68), COL_WOOD)
    make_box("WinW_MullHi", (wx, 3.5, 1.93), (0.12, 0.05, 0.66), COL_WOOD)
    # Sash lock + a plant on the interior ledge
    make_cyl("WinW_SashLock", (wx + 0.12, 3.5, 1.615), 0.020, 0.02, COL_BRASS)
    make_cyl("WinW_LedgePlant_Pot", (wx + 0.15, 3.05, 0.905), 0.045, 0.07, COL_POT)
    make_cyl("WinW_LedgePlant_Leaf", (wx + 0.15, 3.05, 0.975), 0.038, 0.07, COL_PLANT)
    _book_stack("WinW_LedgeBooks", wx + 0.16, 3.85, 0.87, 2, start=1)
    # North kitchen window: opening x 0.7..1.8, z 1.0..2.2
    wy = ROOM_D
    make_box("WinN_Sill", (1.25, wy, 0.965), (1.22, 0.22, 0.07), COL_WOOD)
    make_box("WinN_Ledge", (1.25, wy - 0.14, 1.005), (1.10, 0.14, 0.03), COL_WOOD)
    make_box("WinN_Head", (1.25, wy, 2.235), (1.22, 0.22, 0.07), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"WinN_Jamb_{sgn:+d}", (1.25 + sgn * 0.58, wy, 1.60),
                 (0.06, 0.22, 1.34), COL_WOOD)
    make_box("WinN_MeetRail", (1.25, wy, 1.62), (1.10, 0.14, 0.06), COL_WOOD)
    make_box("WinN_MullLo", (1.25, wy, 1.30), (0.05, 0.12, 0.58), COL_WOOD)
    make_box("WinN_MullHi", (1.25, wy, 1.94), (0.05, 0.12, 0.58), COL_WOOD)
    # Little jar of pencils on the sink-window ledge (she documents
    # the patches from here)
    make_cyl("WinN_LedgeJar", (0.85, wy - 0.15, 1.06), 0.032, 0.09, COL_GLASSISH)
    for pi in range(3):
        make_cyl(f"WinN_LedgePencil_{pi}", (0.84 + pi * 0.014, wy - 0.16 + (pi % 2) * 0.01,
                 1.14), 0.004, 0.10, (0.82, 0.64, 0.28, 1.0))


# ═════════════════════════════════════════════════════════════════
# ENTRY — the closed front door with the deadbolt (locked for the
# first time in three years, vol7_ch7_night), the FOUR HOOKS with
# one wax-canvas coat (Estuary 7 stick in its inside pocket), the
# boots by the door (vol7_ch12), doormat, drip tray.
# ═════════════════════════════════════════════════════════════════
def build_entry():
    # Door leaf — closed, centered in the gap; stairwell beyond
    make_box("Door_Leaf", (0.0, 0.04, 1.03), (0.95, 0.06, 2.06), COL_WOOD_DARK)
    for pi in range(2):
        make_box(f"Door_Panel_{pi}", (0.0, 0.075, 0.62 + pi * 0.85),
                 (0.68, 0.012, 0.62), COL_WOOD)
    make_box("Door_HeadTrim", (0.0, 0.10, 2.12), (1.14, 0.06, 0.10), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"Door_JambTrim_{sgn:+d}", (sgn * 0.53, 0.10, 1.05),
                 (0.08, 0.06, 2.10), COL_WOOD)
    make_cyl("Door_Knob", (0.38, 0.10, 0.98), 0.028, 0.05, COL_BRASS, axis='Y')
    # THE DEADBOLT — thumb-turn above the knob (vol7_ch7_night)
    make_cyl("Door_DeadboltRose", (0.38, 0.085, 1.16), 0.026, 0.02, COL_BRASS,
             axis='Y')
    make_box("Door_DeadboltTurn", (0.38, 0.105, 1.16), (0.012, 0.03, 0.05), COL_BRASS)
    make_door_hinges("Door_Hinge", edge_x=-0.46, edge_y=0.08,
                     edge_z_centers=[0.35, 1.05, 1.80], axis='X')
    # Doormat just inside
    make_box("Doormat", (0.0, 0.72, 0.010), (0.90, 0.55, 0.014), P.RUBBER_MAT)
    # FOUR COAT HOOKS on the south wall east of the door — "Four
    # hooks, four coats" is the vol7_ch8 evening; the resting state
    # is Lena's single coat (never more than one in three years)
    make_box("CoatHooks_Rail", (1.02, 0.13, 1.62), (0.84, 0.03, 0.09), COL_WOOD)
    for hi, hx in enumerate((0.64, 0.87, 1.10, 1.33)):
        make_cyl(f"CoatHooks_Peg_{hi}", (hx, 0.185, 1.60), 0.013, 0.09,
                 COL_BRASS, axis='Y')
    # Lena's wax-canvas coat on the first peg (Estuary 7 stick is
    # in the inside pocket — not modeled, it's inside the coat)
    make_box("LenaCoat_Body", (0.64, 0.235, 1.21), (0.36, 0.08, 0.80), COL_RAINCOAT)
    make_box("LenaCoat_Hood", (0.64, 0.245, 1.655), (0.24, 0.09, 0.13), COL_RAINCOAT)
    make_box("LenaCoat_Flap", (0.64, 0.278, 1.17), (0.10, 0.012, 0.64),
             (0.32, 0.30, 0.22, 1.0))
    # Boots by the door on a drip tray (vol7_ch12_lena)
    make_box("BootTray", (1.72, 0.40, 0.012), (0.55, 0.38, 0.018), P.RUBBER_MAT)
    for bi, bx in enumerate((1.58, 1.84)):
        make_cyl(f"Boot_{bi}_Shaft", (bx, 0.46, 0.17), 0.052, 0.26,
                 (0.24, 0.22, 0.20, 1.0), segments=12)
        make_box(f"Boot_{bi}_Foot", (bx, 0.35, 0.045), (0.11, 0.26, 0.09),
                 (0.24, 0.22, 0.20, 1.0))
    # The radiator in the SE corner — the pipe "ran whether the
    # heat was on or off" (vol7_ch3_apartment). Cast iron, many
    # coats of paint.
    for fi in range(6):
        make_box(f"Radiator_Fin_{fi}", (2.32, 0.42 + fi * 0.075, 0.36),
                 (0.16, 0.045, 0.56), COL_RADIATOR)
    make_box("Radiator_TopRail", (2.32, 0.60, 0.655), (0.17, 0.44, 0.03), COL_RADIATOR)
    for li, ly in enumerate((0.42, 0.79)):
        make_cyl(f"Radiator_Foot_{li}", (2.32, ly, 0.04), 0.025, 0.08, COL_CAST_IRON)
    make_cyl("Radiator_Pipe", (2.34, 0.86, 1.11), 0.022, 2.22, COL_RADIATOR)
    make_cyl("Radiator_Valve", (2.34, 0.86, 0.26), 0.040, 0.05, COL_BRASS)


# ═════════════════════════════════════════════════════════════════
# KITCHEN — the four-people-cannot-comfortably-stand corner (NE).
# Counter with sink under the window, the old enamel range with
# the Salem steel kettle + cast iron + Wednesday soup pot, the
# under-counter fridge, hand grinder, dish drainer, cone-filter
# shelf above the stove with Soren's dark French, drawer stack
# (second drawer down: four bowls, four spoons), braided rag rug.
# ═════════════════════════════════════════════════════════════════
def build_kitchen():
    wy = ROOM_D
    # Counter run x 0.1..1.7 (range stands x 1.7..2.4)
    make_box("Counter_Body", (0.90, wy - 0.41, 0.44), (1.60, 0.58, 0.88), COL_WOOD)
    make_box("Counter_Top", (0.90, wy - 0.41, COUNTER_TOP - 0.025),
             (1.68, 0.64, 0.05), COL_BUTCHER)
    make_box("Counter_Kick", (0.90, wy - 0.71, 0.09), (1.60, 0.02, 0.18),
             COL_WOOD_DARK)
    # Drawer stack under the counter west end — "the second drawer
    # down" holds the four bowls + four spoons (vol7_ch8_the_table);
    # the little fridge slots below them
    for di in range(2):
        make_box(f"Counter_Drawer_{di}", (0.38, wy - 0.705, 0.78 - di * 0.18),
                 (0.42, 0.015, 0.16), COL_WOOD_LT)
        make_cyl(f"Counter_DrawerKnob_{di}", (0.38, wy - 0.72, 0.78 - di * 0.18),
                 0.014, 0.03, COL_BRASS, axis='Y')
    # Cabinet doors under the sink
    for ci, cx in enumerate((0.95, 1.40)):
        make_box(f"Counter_CabDoor_{ci}", (cx, wy - 0.705, 0.47),
                 (0.40, 0.015, 0.70), COL_WOOD_LT)
        make_cyl(f"Counter_CabKnob_{ci}", (cx + (0.14 if ci == 0 else -0.14),
                 wy - 0.72, 0.55), 0.014, 0.03, COL_BRASS, axis='Y')
    # Sink under the window + gooseneck faucet
    make_box("Sink_Basin", (1.25, wy - 0.42, 0.885), (0.46, 0.38, 0.09),
             P.METAL_STEEL, open_faces={'+Z'})
    make_box("Sink_BasinFloor", (1.25, wy - 0.42, 0.845), (0.44, 0.36, 0.01),
             (0.42, 0.44, 0.46, 1.0))
    make_cyl("Sink_FaucetRiser", (1.25, wy - 0.24, 1.05), 0.014, 0.22, P.METAL_STEEL)
    make_cyl("Sink_FaucetSpout", (1.25, wy - 0.33, 1.15), 0.012, 0.18,
             P.METAL_STEEL, axis='Y')
    for hi, hx in enumerate((1.13, 1.37)):
        make_box(f"Sink_Handle_{hi}", (hx, wy - 0.24, 0.945), (0.05, 0.02, 0.02),
                 P.METAL_STEEL)
    # Small dish drainer west of the sink, against the wall —
    # dishes rinsed + stacked (vol7_ch7_night)
    make_box("Drainer_Tray", (0.50, wy - 0.26, 0.94), (0.38, 0.30, 0.015),
             P.METAL_STEEL)
    for ri in range(4):
        make_box(f"Drainer_Rib_{ri}", (0.37 + ri * 0.085, wy - 0.26, 0.975),
                 (0.010, 0.28, 0.05), P.METAL_STEEL)
    for pi in range(3):
        make_cyl(f"Drainer_Plate_{pi}", (0.40 + pi * 0.085, wy - 0.26, 1.03),
                 0.085, 0.012, COL_CREAM, axis='X', segments=12)
    make_cyl("Drainer_Bowl", (0.63, wy - 0.32, 0.975), 0.058, 0.05, MUG_TINTS[1])
    # Hand grinder on the counter (vol7_ch10_morning)
    make_cyl("Grinder_Body", (0.22, wy - 0.52, 1.015), 0.045, 0.16, COL_WOOD)
    make_cyl("Grinder_Cap", (0.22, wy - 0.52, 1.10), 0.040, 0.02, P.METAL_STEEL)
    make_cyl("Grinder_CrankArm", (0.28, wy - 0.52, 1.115), 0.007, 0.12,
             P.METAL_STEEL, axis='X')
    make_cyl("Grinder_CrankKnob", (0.345, wy - 0.52, 1.135), 0.014, 0.04,
             COL_WOOD_DARK)
    # Cutting board + the bread + cheddar + knife on the counter's
    # front half (Kai cutting bread on the small wooden board,
    # vol7_ch8_six_oclock)
    make_box("CuttingBoard", (0.75, wy - 0.56, 0.945), (0.36, 0.24, 0.018), COL_WOOD_LT)
    make_box("Bread_Loaf", (0.68, wy - 0.54, 0.995), (0.20, 0.11, 0.08),
             (0.76, 0.56, 0.32, 1.0))
    make_box("Cheddar_Block", (0.86, wy - 0.60, 0.975), (0.09, 0.07, 0.045),
             (0.88, 0.68, 0.30, 1.0))
    make_box("BreadKnife_Blade", (0.75, wy - 0.665, 0.958), (0.20, 0.018, 0.006),
             P.METAL_STEEL)
    make_box("BreadKnife_Handle", (0.89, wy - 0.665, 0.961), (0.08, 0.022, 0.02),
             COL_WOOD_DARK)
    # ── The range (old enamel, 60 cm) x 1.7..2.3 ─────────────────
    make_box("Range_Body", (2.00, wy - 0.40, 0.45), (0.60, 0.56, 0.90), COL_ENAMEL)
    make_box("Range_OvenDoor", (2.00, wy - 0.69, 0.42), (0.50, 0.015, 0.50), COL_ENAMEL)
    make_box("Range_OvenWindow", (2.00, wy - 0.70, 0.50), (0.30, 0.008, 0.14),
             COL_CAST_IRON)
    make_cyl("Range_OvenHandle", (2.00, wy - 0.71, 0.70), 0.014, 0.44,
             P.METAL_STEEL, axis='X')
    make_box("Range_Cooktop", (2.00, wy - 0.40, 0.915), (0.60, 0.56, 0.03),
             COL_ENAMEL)
    for ki in range(4):
        make_cyl(f"Range_Knob_{ki}", (1.80 + ki * 0.13, wy - 0.685, 0.86),
                 0.018, 0.025, COL_CAST_IRON, axis='Y')
    burners = [(1.86, wy - 0.52), (2.14, wy - 0.52), (1.86, wy - 0.27), (2.14, wy - 0.27)]
    for bi, (bx, by) in enumerate(burners):
        make_cyl(f"Range_Burner_{bi}", (bx, by, 0.935), 0.070, 0.012, COL_CAST_IRON,
                 segments=12)
    # THE KETTLE — steel, nine tokens at Margit's, "the kettle her
    # grandmother had used in Salem" (vol7_ch10_morning). Front-left.
    make_cyl("Kettle_Body", (1.86, wy - 0.52, 1.015), 0.085, 0.15, P.METAL_STEEL,
             segments=12)
    make_cyl("Kettle_Lid", (1.86, wy - 0.52, 1.10), 0.055, 0.02, P.METAL_STEEL)
    make_cyl("Kettle_Knob", (1.86, wy - 0.52, 1.12), 0.014, 0.02, COL_WOOD_DARK)
    make_box("Kettle_Spout_A", (1.86, wy - 0.615, 1.00), (0.018, 0.08, 0.018),
             P.METAL_STEEL)
    make_box("Kettle_Spout_B", (1.86, wy - 0.66, 1.035), (0.015, 0.04, 0.015),
             P.METAL_STEEL)
    make_box("Kettle_Handle", (1.86, wy - 0.52, 1.115), (0.02, 0.03, 0.085),
             COL_CAST_IRON)
    # The cast iron (back-left) + the Wednesday soup pot (back-right)
    make_cyl("CastIron_Pan", (1.86, wy - 0.27, 0.955), 0.100, 0.035, COL_CAST_IRON,
             segments=12)
    make_cyl("CastIron_Handle", (2.00, wy - 0.27, 0.96), 0.014, 0.14, COL_CAST_IRON,
             axis='X')
    make_cyl("SoupPot_Body", (2.14, wy - 0.27, 1.00), 0.085, 0.13, P.METAL_STEEL,
             segments=12)
    make_cyl("SoupPot_Lid", (2.14, wy - 0.27, 1.075), 0.090, 0.015, P.METAL_STEEL)
    make_cyl("SoupPot_LidKnob", (2.14, wy - 0.27, 1.10), 0.014, 0.025, COL_CAST_IRON)
    # Shelf above the stove — the cone filter comes down from here;
    # the dark French bag beside it (vol7_ch10_morning)
    make_box("StoveShelf", (2.08, wy - 0.16, 1.72), (0.50, 0.26, 0.03), COL_WOOD)
    for ki, sgn in enumerate((-1, +1)):
        make_box(f"StoveShelf_Bracket_{ki}", (2.08 + sgn * 0.20, wy - 0.06, 1.64),
                 (0.03, 0.09, 0.13), P.METAL_BLACK)
    make_cyl("ConeFilter_Upper", (1.94, wy - 0.16, 1.79), 0.060, 0.06, COL_CREAM)
    make_cyl("ConeFilter_Lower", (1.94, wy - 0.16, 1.755), 0.036, 0.025, COL_CREAM)
    make_box("DarkFrench_Bag", (2.13, wy - 0.16, 1.83), (0.12, 0.08, 0.19),
             (0.34, 0.22, 0.14, 1.0))
    make_box("DarkFrench_Label", (2.13, wy - 0.198, 1.82), (0.06, 0.006, 0.07), P.PAPER)
    make_cyl("StoveShelf_Jar", (2.26, wy - 0.16, 1.795), 0.035, 0.11, COL_GLASSISH)
    # Open shelf west of the window — mismatched mugs + the bowls
    make_box("MugShelf", (0.38, wy - 0.16, 1.62), (0.62, 0.26, 0.03), COL_WOOD)
    for ki, sgn in enumerate((-1, +1)):
        make_box(f"MugShelf_Bracket_{ki}", (0.38 + sgn * 0.24, wy - 0.06, 1.54),
                 (0.03, 0.09, 0.13), P.METAL_BLACK)
    for mi in range(3):
        _mug(f"ShelfMug_{mi}", 0.20 + mi * 0.18, wy - 0.16, 1.635, MUG_TINTS[mi])
    for bi in range(3):
        make_cyl(f"ShelfBowl_{bi}", (0.38, wy - 0.16, 1.665 + bi * 0.045),
                 0.075 - bi * 0.004, 0.042, MUG_TINTS[(bi + 2) % len(MUG_TINTS)],
                 segments=12)
    # Under-counter fridge at the counter's west end — eggs on the
    # second shelf, the cheddar (vol7_ch10_morning); door closed
    make_box("Fridge_Door", (0.38, wy - 0.72, 0.27), (0.44, 0.015, 0.42),
             P.METAL_STEEL)
    make_box("Fridge_Vent", (0.38, wy - 0.725, 0.10), (0.36, 0.008, 0.05),
             P.METAL_BLACK)
    make_box("Fridge_Handle", (0.20, wy - 0.735, 0.32), (0.03, 0.015, 0.20),
             P.METAL_BLACK)
    # Braided rag rug in front of the sink (vol7_ch10_morning) —
    # three concentric flattened rings
    for ri, (rr, rt) in enumerate([(0.40, (0.55, 0.42, 0.34, 1.0)),
                                   (0.28, (0.38, 0.44, 0.42, 1.0)),
                                   (0.16, (0.66, 0.52, 0.36, 1.0))]):
        make_cyl(f"RagRug_Ring_{ri}", (1.25, wy - 1.05, 0.006 + ri * 0.003),
                 rr, 0.008, rt, segments=16)


# ═════════════════════════════════════════════════════════════════
# TABLE — the small round oak from the seventies with the wobble
# in one leg (no shim yet; Tem has one at the cabin). Four chairs,
# not a matched set: three from Margit's, one from the previous
# tenant. The Daily Grind apron over the back of the south chair
# (vol7_ch12). Doubles as her writing surface — the letter to
# Jorgen sits out.
# ═════════════════════════════════════════════════════════════════
def build_table():
    tx, ty = 0.75, 3.05
    make_cyl("OakTable_Top", (tx, ty, 0.735), 0.50, 0.045, COL_WOOD_LT, segments=16)
    make_cyl("OakTable_Skirt", (tx, ty, 0.685), 0.44, 0.055, COL_WOOD_LT, segments=16)
    make_cyl("OakTable_Column", (tx, ty, 0.36), 0.055, 0.60, COL_WOOD_LT, segments=12)
    for fi, (fx, fy) in enumerate([(-1, 0), (+1, 0), (0, -1), (0, +1)]):
        make_box(f"OakTable_Foot_{fi}", (tx + fx * 0.22, ty + fy * 0.22, 0.045),
                 (0.30 if fx else 0.09, 0.30 if fy else 0.09, 0.07), COL_WOOD_LT)
    # Four mismatched chairs (vol7_ch8_the_table)
    _chair("TableChair_S", tx, ty - 0.70, 'N', CHAIR_TINTS[0])
    _chair("TableChair_W", tx - 0.70, ty, 'E', CHAIR_TINTS[1])
    _chair("TableChair_N", tx, ty + 0.70, 'S', CHAIR_TINTS[2])
    _chair("TableChair_E", tx + 0.70, ty, 'W', CHAIR_TINTS[3])
    # The Daily Grind apron over the back of the south chair
    make_box("Apron_Drape", (tx, ty - 0.90, 0.72), (0.34, 0.06, 0.34), COL_APRON)
    make_box("Apron_Strap", (tx, ty - 0.925, 0.92), (0.03, 0.015, 0.10), COL_APRON)
    # Writing left out on the table — the letter + pen + a mug
    make_box("Letter_Page", (0.62, 3.18, 0.762), (0.16, 0.22, 0.004), P.PAPER)
    make_box("Letter_Page_Lines", (0.62, 3.18, 0.765), (0.11, 0.15, 0.002),
             P.NEWSPRINT)
    make_cyl("Letter_Pen", (0.80, 3.10, 0.766), 0.005, 0.13, COL_CAST_IRON, axis='Y')
    _mug("TableMug", 0.98, 2.90, 0.758, MUG_TINTS[4])


# ═════════════════════════════════════════════════════════════════
# LIVING — couch against the west wall with THE WOOL BLANKET
# folded over the back, end table beside it, Lena's chair across,
# the small wooden side table by the chair (her phone lives here,
# vol7_ch7_night), Kai's chair by the front window, the space
# heater, a flat-woven rug, floor lamp by the window.
# ═════════════════════════════════════════════════════════════════
def build_living():
    # Couch — long axis N-S against the west wall, facing east
    make_box("Couch_Base", (-1.98, 2.0, 0.24), (0.80, 1.70, 0.28), COL_UPHOLSTER)
    for ci, cy in enumerate((1.62, 2.38)):
        make_box(f"Couch_Cushion_{ci}", (-1.92, cy, 0.435), (0.66, 0.72, 0.11),
                 COL_UPHOLSTER)
    make_box("Couch_Back", (-2.32, 2.0, 0.60), (0.16, 1.70, 0.46), COL_UPHOLSTER)
    for ai, sgn in enumerate((-1, +1)):
        make_box(f"Couch_Arm_{ai}", (-1.98, 2.0 + sgn * 0.85, 0.50),
                 (0.78, 0.14, 0.24), COL_UPHOLSTER)
    for fi, (fx, fy) in enumerate([(-2.30, 1.22), (-1.66, 1.22),
                                   (-2.30, 2.78), (-1.66, 2.78)]):
        make_cyl(f"Couch_Foot_{fi}", (fx, fy, 0.05), 0.022, 0.10, COL_WOOD_DARK)
    # THE WOOL BLANKET folded over the back (vol7_ch3_apartment) —
    # cream ground with madder + spruce bands
    make_box("WoolBlanket_Fold", (-2.30, 1.72, 0.87), (0.20, 0.55, 0.09),
             COL_WOOL_BASE)
    make_box("WoolBlanket_Band_0", (-2.30, 1.53, 0.87), (0.205, 0.09, 0.092),
             COL_WOOL_BAND)
    make_box("WoolBlanket_Band_1", (-2.30, 1.86, 0.87), (0.205, 0.07, 0.092),
             COL_WOOL_BND2)
    # A throw pillow
    make_box("Couch_Pillow", (-2.10, 2.62, 0.56), (0.34, 0.34, 0.13), COL_WOOL_BND2)
    # End table beside the couch (Tem's coffee lands here)
    _small_table("EndTable", -2.10, 0.80, 0.24, COL_WOOD)
    _book_stack("EndTable_Books", -2.12, 0.80, 0.5675, 3, start=0)
    # Lena's chair across from the couch — rust wool armchair
    make_box("Armchair_Base", (-0.62, 2.0, 0.22), (0.62, 0.62, 0.30), COL_ARMCHAIR)
    make_box("Armchair_Cushion", (-0.67, 2.0, 0.42), (0.50, 0.52, 0.12), COL_ARMCHAIR)
    make_box("Armchair_Back", (-0.38, 2.0, 0.62), (0.16, 0.62, 0.60), COL_ARMCHAIR)
    for ai, sgn in enumerate((-1, +1)):
        make_box(f"Armchair_Arm_{ai}", (-0.62, 2.0 + sgn * 0.30, 0.50),
                 (0.58, 0.12, 0.26), COL_ARMCHAIR)
    for fi, (fx, fy) in enumerate([(-0.86, 1.77), (-0.38, 1.77),
                                   (-0.86, 2.23), (-0.38, 2.23)]):
        make_cyl(f"Armchair_Foot_{fi}", (fx, fy, 0.035), 0.022, 0.07, COL_WOOD_DARK)
    # The small wooden side table by the chair + her phone on it
    _small_table("SideTable", -0.60, 1.32, 0.22, COL_WOOD)
    make_box("Phone_Slab", (-0.62, 1.30, 0.575), (0.075, 0.15, 0.010),
             (0.10, 0.10, 0.12, 1.0))
    # Kai's chair by the front window (vol7_ch8_six_oclock)
    _chair("WindowChair", -1.95, 3.62, 'E', CHAIR_TINTS[1])
    # The small portable space heater (vol7_ch8_six_oclock)
    make_box("SpaceHeater_Body", (-1.30, 1.10, 0.20), (0.34, 0.15, 0.36),
             (0.80, 0.78, 0.74, 1.0))
    for vi in range(4):
        make_box(f"SpaceHeater_Vent_{vi}", (-1.30, 1.022, 0.10 + vi * 0.075),
                 (0.26, 0.006, 0.035), P.METAL_BLACK)
    make_box("SpaceHeater_Glow", (-1.30, 1.028, 0.205), (0.26, 0.004, 0.03),
             (0.94, 0.52, 0.24, 1.0))
    for fi, sgn in enumerate((-1, +1)):
        make_box(f"SpaceHeater_Foot_{fi}", (-1.30 + sgn * 0.13, 1.10, 0.012),
                 (0.04, 0.14, 0.024), P.METAL_BLACK)
    # Flat-woven rug between couch and chair
    make_box("LivingRug", (-1.35, 2.05, 0.006), (1.30, 1.80, 0.012),
             (0.52, 0.46, 0.40, 1.0))
    make_box("LivingRug_Border", (-1.35, 2.05, 0.013), (1.10, 1.60, 0.002),
             (0.40, 0.34, 0.30, 1.0))
    make_box("LivingRug_Stripe", (-1.35, 2.05, 0.015), (0.90, 0.28, 0.002),
             COL_WOOL_BAND)
    # Floor lamp by the window end of the couch
    make_cyl("FloorLamp_Base", (-2.25, 3.15, 0.02), 0.13, 0.04, P.METAL_BLACK,
             segments=12)
    make_cyl("FloorLamp_Pole", (-2.25, 3.15, 0.76), 0.013, 1.44, COL_BRASS)
    make_cyl("FloorLamp_Shade", (-2.25, 3.15, 1.56), 0.13, 0.17, COL_LINEN,
             segments=12)
    make_cyl("FloorLamp_Glow", (-2.25, 3.15, 1.47), 0.055, 0.03,
             (0.98, 0.88, 0.62, 1.0))
    # A crate of Salty Tome loans beside the armchair (she lives
    # over a bookshop; Petra is the landlord)
    make_box("BookCrate", (-0.55, 1.02, 0.14), (0.36, 0.28, 0.28), COL_WOOD,
             open_faces={'+Z'})
    for bi in range(5):
        make_box(f"BookCrate_Book_{bi}", (-0.67 + bi * 0.058, 1.02, 0.16),
                 (0.035, 0.22, 0.20 - (bi % 2) * 0.03),
                 BOOK_TINTS[bi % len(BOOK_TINTS)])
    make_floor_plant("FloorPlant_SW", (-2.20, 0.35, 0.0))


# ═════════════════════════════════════════════════════════════════
# BEDROOM ANNEX — through the open door in the north wall. Bed
# with the wool blanket, bedside table (sketchbook on top, pencils
# in the drawer — vol7 interlude ii), the thermostat above the bed
# that read sixty-one, the closet, and the three water stains +
# crack above it (2050 bathtub leak, never painted over). The
# side table with the unused lamp stands just outside the door.
# ═════════════════════════════════════════════════════════════════
def build_bedroom():
    # Annex shell — floor, three walls, ceiling
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
             (0.82, 0.78, 0.70, 1.0))
    # THE WATER STAINS — three, above the closet at the back-right
    # corner of the bedroom; the crack (vol7_ch8_monday /
    # vol7_ch10_morning). Left unpainted on purpose.
    for si, (sx, sy, sr) in enumerate([(-2.05, 6.95, 0.16), (-1.85, 7.10, 0.11),
                                       (-2.20, 7.15, 0.09)]):
        make_cyl(f"Anx_CeilStain_{si}", (sx, sy, ANX_CEIL - 0.006), sr, 0.008,
                 COL_STAIN, segments=12)
    make_box("Anx_CeilCrack", (-2.10, 7.02, ANX_CEIL - 0.010), (0.42, 0.015, 0.006),
             (0.46, 0.40, 0.32, 1.0))
    # Bedroom door — open, parked against the annex east wall
    make_box("BedDoor_Leaf", (ANX_X1 - 0.04, 5.70, 1.02), (0.05, 0.92, 2.04),
             COL_WOOD_DARK)
    make_cyl("BedDoor_Knob", (ANX_X1 - 0.10, 6.08, 0.98), 0.026, 0.04, COL_BRASS,
             axis='X')
    for ti, sgn in enumerate((-1, +1)):
        make_box(f"BedDoor_JambTrim_{ti}", (-1.45 + sgn * 0.51, ROOM_D - 0.13, 1.03),
                 (0.07, 0.05, 2.06), COL_WOOD)
    make_box("BedDoor_HeadTrim", (-1.45, ROOM_D - 0.13, 2.09), (1.10, 0.05, 0.08),
             COL_WOOD)
    # The bed — head against the annex north wall (interior face
    # y 7.30)
    make_box("Bed_Frame", (-1.52, 6.36, 0.18), (1.20, 1.86, 0.16), COL_WOOD_DARK)
    make_box("Bed_Headboard", (-1.52, 7.26, 0.55), (1.24, 0.06, 0.70), COL_WOOD_DARK)
    make_box("Bed_Mattress", (-1.52, 6.36, 0.34), (1.12, 1.78, 0.16), COL_LINEN)
    make_box("Bed_Sheet_Fold", (-1.52, 5.66, 0.425), (1.13, 0.30, 0.025), COL_LINEN)
    # Wool blanket on the bed (Pendleton-ish bands)
    make_box("Bed_Blanket", (-1.52, 6.49, 0.43), (1.14, 1.30, 0.05), COL_WOOL_BASE)
    make_box("Bed_Blanket_Band_0", (-1.52, 6.04, 0.432), (1.145, 0.14, 0.052),
             COL_WOOL_BAND)
    make_box("Bed_Blanket_Band_1", (-1.52, 6.69, 0.432), (1.145, 0.10, 0.052),
             COL_WOOL_BND2)
    for pi, px in enumerate((-1.80, -1.24)):
        make_box(f"Bed_Pillow_{pi}", (px, 6.98, 0.44), (0.48, 0.30, 0.11), COL_LINEN)
    # Bedside table — SKETCHBOOK on top where she left it, alarm
    # clock; the pencils are in the drawer (vol7 interlude ii)
    make_box("Nightstand_Body", (-0.72, 6.95, 0.28), (0.38, 0.38, 0.52), COL_WOOD)
    make_box("Nightstand_Top", (-0.72, 6.95, 0.555), (0.42, 0.42, 0.03), COL_WOOD_LT)
    make_box("Nightstand_Drawer", (-0.72, 6.753, 0.42), (0.30, 0.015, 0.14),
             COL_WOOD_LT)
    make_cyl("Nightstand_Knob", (-0.72, 6.74, 0.42), 0.012, 0.025, COL_BRASS,
             axis='Y')
    make_box("Sketchbook", (-0.72, 6.88, 0.585), (0.22, 0.28, 0.025), COL_WOOD_DARK)
    make_box("Sketchbook_Band", (-0.72, 6.88, 0.599), (0.05, 0.282, 0.012),
             (0.62, 0.30, 0.24, 1.0))
    make_cyl("AlarmClock_Body", (-0.62, 7.05, 0.615), 0.045, 0.035, P.METAL_BLACK,
             axis='Y', segments=12)
    make_cyl("AlarmClock_Face", (-0.62, 7.03, 0.615), 0.036, 0.006, COL_CREAM,
             axis='Y', segments=12)
    # THE THERMOSTAT above the bed — "read sixty-one"
    # (vol7_ch3_apartment). Screen panel named for scene-side text.
    make_box("Thermostat_Body", (-1.52, 7.28, 1.80), (0.16, 0.05, 0.10),
             COL_CREAM)
    make_box("Thermostat_Screen", (-1.52, 7.25, 1.81), (0.08, 0.012, 0.045),
             (0.30, 0.36, 0.30, 1.0))
    # Closet on the annex west wall — sliding leaf, closed
    make_box("Closet_Leaf", (ANX_X0 + 0.055, 6.55, 1.00), (0.05, 1.05, 2.00),
             COL_WOOD_LT)
    make_box("Closet_Trim", (ANX_X0 + 0.08, 6.55, 2.04), (0.06, 1.15, 0.08), COL_WOOD)
    make_cyl("Closet_Pull", (ANX_X0 + 0.10, 6.20, 1.00), 0.016, 0.03, COL_BRASS,
             axis='X')
    # Small rug beside the bed
    make_box("Anx_BedRug", (-1.52, 5.42, 0.006), (0.90, 0.50, 0.012),
             (0.38, 0.44, 0.42, 1.0))
    # Flush ceiling light
    make_cyl("Anx_CeilLight_Base", (-1.45, 6.30, ANX_CEIL - 0.015), 0.09, 0.03,
             COL_BRASS, segments=12)
    make_cyl("Anx_CeilLight_Dome", (-1.45, 6.30, ANX_CEIL - 0.055), 0.075, 0.05,
             (0.96, 0.92, 0.80, 1.0), segments=12)
    # The side table OUTSIDE the bedroom door with the lamp she
    # does not use (vol7_ch10_morning)
    _small_table("HallTable", -0.55, 4.70, 0.20, COL_WOOD_DARK, top_z=0.62)
    make_cyl("UnusedLamp_Base", (-0.55, 4.70, 0.655), 0.07, 0.03, COL_BRASS,
             segments=12)
    make_cyl("UnusedLamp_Stem", (-0.55, 4.70, 0.76), 0.010, 0.18, COL_BRASS)
    make_cyl("UnusedLamp_Shade", (-0.55, 4.70, 0.895), 0.085, 0.11, COL_LINEN,
             segments=12)


# ═════════════════════════════════════════════════════════════════
# ZINE DESK — east wall, tucked under the roof slope. "The writing
# desk where Static Truths gets laid out" (_VOL6_VOL7_LOCALES_
# MANIFEST). Paste-up only — the copier is downstairs in the Salty
# Tome back room (static_truths.md): cutting mat, two half-letter
# flats, glue jar + brush, scissors, pencil cup, the hand-lettered
# masthead strip, the stack of finished issues with the OCTOPUS on
# the top back cover, corkboard of alley/patch photos above.
# ═════════════════════════════════════════════════════════════════
def build_zine_desk():
    wall_face = ROOM_W / 2.0 - 0.10   # 2.40
    dx = 2.12
    make_box("Desk_Top", (dx, 1.55, 0.735), (0.58, 1.20, 0.04), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Desk_Leg_{li}", (dx + sx * 0.25, 1.55 + sy * 0.54, 0.36),
                 (0.05, 0.05, 0.72), COL_WOOD_DARK)
    make_box("Desk_Stretcher", (dx, 1.55, 0.18), (0.52, 1.00, 0.04), COL_WOOD_DARK)
    _chair("DeskChair", dx - 0.62, 1.55, 'E', CHAIR_TINTS[2])
    # Cutting mat + the two page flats (photocopied half-letter,
    # single-fold — static_truths.md)
    make_box("Desk_CuttingMat", (dx, 1.55, 0.758), (0.42, 0.60, 0.006), COL_MAT_GREEN)
    for fi, fy in enumerate((1.38, 1.72)):
        make_box(f"Zine_Flat_{fi}", (dx - 0.02, fy, 0.764), (0.15, 0.21, 0.004),
                 P.PAPER)
        make_box(f"Zine_Flat_{fi}_ColA", (dx - 0.06, fy, 0.767), (0.05, 0.15, 0.002),
                 P.NEWSPRINT)
        make_box(f"Zine_Flat_{fi}_ColB", (dx + 0.02, fy, 0.767), (0.05, 0.15, 0.002),
                 P.NEWSPRINT)
    # Hand-lettered masthead strip (block print) — Label3D target
    make_box("Zine_Masthead", (dx - 0.02, 1.55, 0.767), (0.13, 0.05, 0.004),
             P.METAL_BLACK)
    # Glue jar + brush, scissors, pencil cup
    make_cyl("Desk_GlueJar", (dx + 0.18, 1.30, 0.795), 0.032, 0.07, COL_GLASSISH)
    make_cyl("Desk_GlueBrush", (dx + 0.18, 1.30, 0.865), 0.007, 0.07, COL_WOOD_DARK)
    make_box("Desk_Scissors_BladeA", (dx + 0.16, 1.80, 0.762), (0.03, 0.15, 0.005),
             P.METAL_STEEL)
    make_box("Desk_Scissors_BladeB", (dx + 0.19, 1.80, 0.766), (0.03, 0.15, 0.005),
             P.METAL_STEEL)
    make_cyl("Desk_Scissors_Pivot", (dx + 0.175, 1.80, 0.766), 0.010, 0.012,
             COL_CAST_IRON)
    make_cyl("Desk_PencilCup", (dx + 0.20, 2.02, 0.785), 0.032, 0.09, MUG_TINTS[0])
    for pi in range(4):
        make_cyl(f"Desk_Pencil_{pi}", (dx + 0.19 + (pi % 2) * 0.02,
                 2.01 + (pi % 3) * 0.012, 0.875), 0.004, 0.10,
                 (0.82, 0.64, 0.28, 1.0) if pi % 2 == 0 else COL_CAST_IRON)
    # Finished-issue stack — top copy face-down: the octopus drawn
    # on the back cover (vol7 interlude ii / static_truths.md).
    for zi in range(4):
        make_box(f"Zine_Stack_{zi}", (dx - 0.04 + (zi % 2) * 0.008, 1.06,
                 0.759 + zi * 0.007), (0.15, 0.21, 0.006),
                 P.PAPER if zi % 2 == 0 else P.PAPER_AGED)
    make_box("Zine_Stack_TopBack", (dx - 0.04, 1.06, 0.7905), (0.14, 0.20, 0.002),
             P.PAPER)
    make_cyl("Zine_Octopus_Head", (dx - 0.05, 1.09, 0.7925), 0.030, 0.003,
             (0.20, 0.18, 0.24, 1.0), segments=12)
    for ai in range(4):
        make_box(f"Zine_Octopus_Arm_{ai}", (dx - 0.09 + ai * 0.028, 1.025, 0.7925),
                 (0.008, 0.05 + (ai % 2) * 0.015, 0.002), (0.20, 0.18, 0.24, 1.0))
    # Anglepoise-ish desk lamp (upright + horizontal arm + shade)
    make_cyl("DeskLamp_Base", (dx + 0.16, 2.10, 0.755), 0.055, 0.025, P.METAL_BLACK,
             segments=12)
    make_cyl("DeskLamp_Post", (dx + 0.16, 2.10, 0.95), 0.009, 0.36, P.METAL_BLACK)
    make_cyl("DeskLamp_Arm", (dx + 0.16, 1.95, 1.13), 0.008, 0.32, P.METAL_BLACK,
             axis='Y')
    make_cyl("DeskLamp_Shade", (dx + 0.16, 1.78, 1.075), 0.055, 0.10,
             (0.34, 0.48, 0.46, 1.0), segments=12)
    make_cyl("DeskLamp_Glow", (dx + 0.16, 1.78, 1.02), 0.028, 0.02,
             (0.98, 0.88, 0.62, 1.0))
    # Corkboard above the desk (fits under the 2.05 knee wall) —
    # alley photos + index cards, the patch documentation
    make_box("Corkboard", (wall_face + 0.02, 1.55, 1.52), (0.03, 1.00, 0.62), COL_CORK)
    make_box("Corkboard_FrameT", (wall_face + 0.005, 1.55, 1.845), (0.04, 1.06, 0.05),
             COL_WOOD)
    make_box("Corkboard_FrameB", (wall_face + 0.005, 1.55, 1.195), (0.04, 1.06, 0.05),
             COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"Corkboard_FrameSide_{sgn:+d}",
                 (wall_face + 0.005, 1.55 + sgn * 0.52, 1.52), (0.04, 0.05, 0.70),
                 COL_WOOD)
    photos = [(-0.30, 1.62, 0.16, 0.12, (0.22, 0.20, 0.30, 1.0)),
              (-0.02, 1.66, 0.16, 0.12, (0.30, 0.26, 0.24, 1.0)),
              (+0.26, 1.60, 0.16, 0.12, (0.22, 0.20, 0.30, 1.0)),
              (-0.18, 1.40, 0.14, 0.10, P.PAPER),
              (+0.14, 1.38, 0.14, 0.10, P.PAPER_AGED)]
    for ni, (dy, dz, w, h, tint) in enumerate(photos):
        make_box(f"Corkboard_Pin_{ni}_Sheet", (wall_face - 0.005, 1.55 + dy, dz),
                 (0.012, w, h), tint)
        make_cyl(f"Corkboard_Pin_{ni}_Tack", (wall_face - 0.015, 1.55 + dy,
                 dz + h / 2.0 - 0.015), 0.008, 0.012, COL_WOOL_BAND, axis='X')
    # Wastebasket with crumpled paste-up rejects
    make_cyl("Wastebasket", (2.28, 2.42, 0.14), 0.11, 0.28, P.METAL_BLACK,
             segments=12)
    for wi in range(2):
        make_cyl(f"Wastebasket_Paper_{wi}", (2.26 + wi * 0.05, 2.40 + wi * 0.04,
                 0.30), 0.035, 0.05, P.PAPER, segments=6)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — two warm pendants (table + sink), smoke detector.
# No fluorescents: this is a 104-year-old walk-up, not a store.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    _pendant("Pendant_Table", 0.75, 3.05, CEIL, 0.55, (0.34, 0.48, 0.46, 1.0))
    _pendant("Pendant_Sink", 1.25, 4.55, CEIL, 0.45, COL_CREAM)
    make_smoke_detector("Smoke", (-0.8, 2.5, CEIL))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · ALLEY (north) — what the kitchen window looks at: the
# opposite building's wall with THE STARFISH NEBULA (the mural
# Lena painted in spring '50: the octopus with seven and a half
# arms, the kite of starfish over a tide pool, sandstone arches, a
# radio-tower section) and the FOUR gray patches eating it
# (vol7_ch3_apartment counts four). The orange laundromat safety
# light (vol7_ch10_morning). Alley grade is a storey down.
# ═════════════════════════════════════════════════════════════════
def build_exterior_alley():
    # Alley floor + puddles, one storey below the apartment
    make_box("Alley_Ground", (0.6, 6.9, STREET_Z - 0.05), (11.0, 3.6, 0.10),
             COL_ASPHALT)
    make_box("Alley_Puddle_0", (1.6, 7.6, STREET_Z + 0.004), (1.40, 0.60, 0.004),
             COL_PUDDLE)
    make_box("Alley_Puddle_1", (-1.2, 7.9, STREET_Z + 0.004), (0.80, 0.45, 0.004),
             COL_PUDDLE)
    # Our own building's alley face east of the annex, dropping
    # from the window to grade (so looking down reads as a real
    # wall, not void)
    make_box("Bldg_AlleyFace", (1.85, 5.20, -1.72), (4.0, 0.15, 3.7), COL_BRICK)
    make_box("Bldg_AlleyFace_Course", (1.85, 5.12, -0.15), (4.0, 0.02, 0.10),
             COL_BRICK_DK)
    # Hull skin around the bedroom annex (playbook: every annex
    # gets wrapped) + the void under it down to grade
    make_box("Anx_Skin_W", (-2.65, 6.35, ANX_CEIL / 2.0),
             (0.10, 2.50, ANX_CEIL + 0.2), COL_BRICK)
    make_box("Anx_Skin_N", ((ANX_X0 + ANX_X1) / 2.0, 7.55, ANX_CEIL / 2.0),
             (ANX_X1 - ANX_X0 + 0.7, 0.10, ANX_CEIL + 0.2), COL_BRICK)
    make_box("Anx_Skin_E", (-0.25, 6.35, ANX_CEIL / 2.0),
             (0.10, 2.50, ANX_CEIL + 0.2), COL_BRICK)
    make_box("Anx_Skin_Roof", ((ANX_X0 + ANX_X1) / 2.0, 6.35, ANX_CEIL + 0.22),
             (ANX_X1 - ANX_X0 + 0.9, 2.70, 0.12), COL_BRICK_DK)
    make_box("Anx_Skin_Under", ((ANX_X0 + ANX_X1) / 2.0, 6.35, -1.80),
             (ANX_X1 - ANX_X0 + 0.6, 2.50, 3.5), COL_BRICK)
    # The opposite building — the mural wall
    make_box("Opposite_Wall", (0.6, 8.8, 0.3), (11.0, 0.20, 8.6), COL_BRICK_DK)
    # THE STARFISH NEBULA — indigo ground panel
    make_box("Mural_Ground", (0.75, 8.68, 0.55), (8.5, 0.02, 3.4), COL_MURAL_GROUND)
    # Octopus with seven and a half arms (vol7_ch10_morning)
    make_cyl("Mural_Octo_Head", (-0.6, 8.66, 1.45), 0.58, 0.012, COL_MURAL_OCTO,
             axis='Y', segments=16)
    arm_specs = [(-1.55, 0.55, 0.95), (-1.15, 0.30, 1.20), (-0.75, 0.15, 1.35),
                 (-0.30, 0.10, 1.30), (0.10, 0.20, 1.10), (0.45, 0.40, 0.90),
                 (0.75, 0.65, 0.70)]
    for ai, (ax, az_len, az_top) in enumerate(arm_specs):
        make_box(f"Mural_Octo_Arm_{ai}", (ax, 8.665, az_top - az_len / 2.0),
                 (0.14, 0.012, az_len + 0.45), COL_MURAL_OCTO)
    make_box("Mural_Octo_HalfArm", (1.05, 8.665, 1.05), (0.12, 0.012, 0.40),
             COL_MURAL_OCTO)
    # The kite of starfish over a tide pool
    make_cyl("Mural_TidePool", (2.6, 8.66, 0.05), 0.75, 0.012, COL_MURAL_POOL,
             axis='Y', segments=16)
    star_pts = [(2.1, 0.9), (2.5, 1.35), (2.95, 1.75), (3.3, 2.15), (3.0, 1.15)]
    for si, (sx, sz) in enumerate(star_pts):
        make_box(f"Mural_Star_{si}_A", (sx, 8.665, sz), (0.20, 0.012, 0.06),
                 COL_MURAL_STAR)
        make_box(f"Mural_Star_{si}_B", (sx, 8.665, sz), (0.06, 0.012, 0.20),
                 COL_MURAL_STAR)
    # Sandstone arches (east end)
    for ci, cx in enumerate((3.9, 4.5)):
        for sgn in (-1, +1):
            make_box(f"Mural_Arch_{ci}_Leg_{sgn:+d}", (cx + sgn * 0.18, 8.665, -0.35),
                     (0.10, 0.012, 0.85), COL_MURAL_ARCH)
        make_box(f"Mural_Arch_{ci}_Cap", (cx, 8.665, 0.14), (0.48, 0.012, 0.14),
                 COL_MURAL_ARCH)
    # Radio-tower lattice section (west end)
    for ti, tx in enumerate((-3.35, -3.05)):
        make_box(f"Mural_Tower_Leg_{ti}", (tx, 8.665, 0.95), (0.06, 0.012, 2.4),
                 COL_MURAL_TOWER)
    for bi in range(3):
        make_box(f"Mural_Tower_Brace_{bi}", (-3.2, 8.665, 0.25 + bi * 0.75),
                 (0.36, 0.012, 0.06), COL_MURAL_TOWER)
    # THE FOUR PATCHES — gray primer rectangles eating the mural
    patches = [(-1.15, 1.55, 0.55, 0.70), (0.35, 0.65, 0.45, 0.55),
               (2.45, 1.05, 0.60, 0.50), (-2.55, 0.35, 0.40, 0.60)]
    for pi, (px, pz, pw, ph) in enumerate(patches):
        make_box(f"Mural_Patch_{pi}", (px, 8.655, pz), (pw, 0.012, ph), COL_PATCH)
    # The laundromat's orange safety light (caged, on the opposite
    # wall east of the mural)
    make_box("Laundromat_LampBracket", (4.9, 8.62, 2.30), (0.08, 0.14, 0.08),
             P.METAL_BLACK)
    make_cyl("Laundromat_LampGlobe", (4.9, 8.52, 2.22), 0.075, 0.14,
             COL_ORANGE_LAMP, segments=12)
    for gi in range(3):
        make_box(f"Laundromat_LampCage_{gi}", (4.9, 8.52, 2.30 - gi * 0.08),
                 (0.17, 0.17, 0.012), P.METAL_BLACK, open_faces={'+Z', '-Z'})
    # A dumpster down in the alley
    make_box("Dumpster_Body", (3.4, 7.7, STREET_Z + 0.575), (1.60, 0.95, 1.05),
             (0.24, 0.34, 0.30, 1.0))
    make_box("Dumpster_Lid", (3.4, 7.55, STREET_Z + 1.13), (1.64, 0.70, 0.06),
             (0.18, 0.26, 0.24, 1.0))
    make_box("Dumpster_LidBack", (3.4, 8.02, STREET_Z + 1.21), (1.64, 0.28, 0.06),
             (0.18, 0.26, 0.24, 1.0))


# ═════════════════════════════════════════════════════════════════
# EXTERIOR · HEMLOCK (west) — the street she looks DOWN at from
# the front window (vol7_ch8_six_oclock): sidewalk + wet asphalt a
# storey below, the Salty Tome's hanging sign under her window,
# the streetlamp whose head sits near window height, the dark
# facade across the street with a few lit windows.
# ═════════════════════════════════════════════════════════════════
def build_exterior_street():
    make_box("Hemlock_Sidewalk", (-3.45, 2.5, STREET_Z + 0.03), (1.60, 12.0, 0.08),
             COL_CONCRETE)
    for si in range(5):
        make_box(f"Hemlock_SidewalkSeam_{si}", (-3.45, -2.3 + si * 2.4,
                 STREET_Z + 0.072), (1.60, 0.02, 0.002), (0.40, 0.39, 0.37, 1.0))
    make_box("Hemlock_Curb", (-4.32, 2.5, STREET_Z + 0.04), (0.16, 12.0, 0.12),
             (0.46, 0.45, 0.43, 1.0))
    make_box("Hemlock_Street", (-6.9, 2.5, STREET_Z - 0.05), (5.0, 12.0, 0.10),
             COL_ASPHALT)
    make_box("Hemlock_Puddle_0", (-5.6, 3.6, STREET_Z + 0.004), (1.30, 0.70, 0.004),
             COL_PUDDLE)
    make_box("Hemlock_Puddle_1", (-6.5, 0.8, STREET_Z + 0.004), (0.90, 0.50, 0.004),
             COL_PUDDLE)
    make_box("Hemlock_CenterLine", (-6.9, 2.5, STREET_Z + 0.002), (0.10, 10.0, 0.002),
             (0.70, 0.66, 0.50, 1.0))
    # Our building's street face below the apartment + the shop
    # cornice; THE SALTY TOME's hanging sign under Lena's window
    # (Label3D scene-side on SaltyTome_SignBoard)
    make_box("Bldg_StreetFace", (-2.82, 2.5, -1.72), (0.15, 5.9, 3.7), COL_BRICK)
    make_box("Bldg_Cornice", (-2.92, 2.5, -0.30), (0.30, 5.9, 0.22),
             (0.30, 0.34, 0.32, 1.0))
    make_box("SaltyTome_SignArm", (-3.12, 3.5, -0.55), (0.50, 0.04, 0.04),
             P.METAL_BLACK)
    for hi, hx in enumerate((-3.00, -3.28)):
        make_cyl(f"SaltyTome_SignLink_{hi}", (hx, 3.5, -0.64), 0.008, 0.16,
                 P.METAL_BLACK)
    make_box("SaltyTome_SignBoard", (-3.14, 3.5, -0.92), (0.42, 0.05, 0.40),
             (0.16, 0.24, 0.30, 1.0))
    for ri, sgn in enumerate((-1, +1)):
        make_box(f"SaltyTome_SignRule_{ri}", (-3.14, 3.5 + sgn * 0.026, -0.80),
                 (0.34, 0.006, 0.04), COL_BRASS)
    # Shopfront glow hint at grade (warm rectangles = the bookshop
    # windows below, lit)
    for wi, wyy in enumerate((1.4, 3.1, 4.6)):
        make_box(f"SaltyTome_ShopWindow_{wi}", (-2.895, wyy, -2.35),
                 (0.02, 1.10, 1.60), (0.86, 0.72, 0.46, 1.0))
    # Streetlamp — head near her window height (rain-lit glow)
    make_cyl("Streetlamp_Pole", (-3.95, 4.35, STREET_Z + 2.35), 0.045, 4.70,
             P.METAL_BLACK, segments=12)
    make_cyl("Streetlamp_Arm", (-3.75, 4.35, 1.12), 0.025, 0.45, P.METAL_BLACK,
             axis='X')
    make_cyl("Streetlamp_Head", (-3.55, 4.35, 1.06), 0.09, 0.14, P.METAL_BLACK,
             segments=12)
    make_cyl("Streetlamp_Glow", (-3.55, 4.35, 0.97), 0.065, 0.05,
             (0.98, 0.84, 0.56, 1.0), segments=12)
    # The facade across Hemlock — dark, a few windows lit
    make_box("Opposite_Facade_W", (-9.6, 2.5, 0.3), (0.20, 12.0, 8.6),
             (0.20, 0.19, 0.20, 1.0))
    lit = [(0.6, 0.6), (3.4, 1.9), (5.2, -0.9), (1.8, -1.1)]
    for wi, (wyy, wz) in enumerate(lit):
        make_box(f"Opposite_LitWindow_{wi}", (-9.48, wyy, wz), (0.02, 0.60, 0.90),
                 (0.80, 0.66, 0.40, 1.0))
    for wi, (wyy, wz) in enumerate([(2.6, 0.7), (4.4, -1.0), (0.9, -1.2)]):
        make_box(f"Opposite_DarkWindow_{wi}", (-9.48, wyy, wz), (0.02, 0.60, 0.90),
                 (0.10, 0.10, 0.12, 1.0))


def main():
    clear_scene()
    build_shell()
    build_windows()
    build_entry()
    build_kitchen()
    build_table()
    build_living()
    build_bedroom()
    build_zine_desk()
    build_ceiling_infra()
    build_exterior_alley()
    build_exterior_street()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/lena_apartment.glb"))
    print(f"\n[build_lena_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
