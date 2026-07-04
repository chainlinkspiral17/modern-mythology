"""VOL 5 · VIII Strength § Coda — the room above the laundromat,
Marigny, "eight blocks back" from the bar (vol5_ch8_strength.json
L280). Month-to-month, paid in cash by Jimmy (L280); it smells,
faintly, of dryer sheets (L284). Where Douglas writes the letter
(L288-L324) and looks at his own face in the small mirror above
the dresser (L328). Spare because it IS spare.

ADJUDICATION — NOT the same building as new_orleans_bar; the walk
between them is the § Coda's eight blocks (L280). Palettes are
independent but city-consistent (the small NOLA_* register below
is repeated by intent, not a shared-venue KEEP-IN-SYNC contract).

Canon dressed in (line numbers = vol5_ch8_strength.json):
  · The small desk under the window (L288), with a drawer — the
    paper came out of it — the letter on the desktop (the date
    line, L292; "J —", L304; the body; "— D.", L320) and the pen
    (L288) beside it.
  · The chair at the desk with the jacket hanging on its back —
    where he always hangs it (L324) — the sealed envelope's corner
    just showing at the inside pocket (L324).
  · The dresser with the small mirror above it (L328). Mirror is
    an opaque pale slab — vertex colors can't do glass.
  · The bed — he slept "briefly, badly" (L344): rumpled blanket,
    kicked corner.
  · His father's Korea canvas duffle, "battered enough to look
    intentional" (L104), on the floor at the foot of the bed.
  · Sash window, N wall, looking DOWN at the street (L340) — a
    REAL opening (playbook: no glass), double-hung frame, meeting
    rail + muntin, and a sliver of wrought-iron gallery rail
    outside the sill (second floor, Marigny, L280).
  · Bare bulb on a cord — the .tscn's Key_BareBulb is named for it.
  · Clock frozen at 12:24 — after the bar's 11:47 and the eight
    blocks home; the hour the chain rattles once (L344).
Canon-negatives (all removed from the scaffold — none staged in
the coda): the washbasin, the faded poster, the nightstand and
water glass, the peeling-wallpaper strips, and the scaffold's
"suitcase" (the bag is canonically the canvas duffle, L104).
No radio, no TV — the room's sound is the street (L280).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.decor import make_wall_clock
from _props.safety import make_smoke_detector

# Shell footprint — KEPT from the scaffold; the Background3D preset
# ("new_orleans_room", camera at the S door looking N) and the .tscn
# lights (Key_BareBulb, Fill_SashWindow on the N side) are tuned to it.
ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.80

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

# Room-local palette — aged plaster, worn cypress plank, iron bed.
PAL = {"wall": (0.78, 0.70, 0.56, 1.0), "baseboard": (0.34, 0.23, 0.15, 1.0)}
COL_FLOOR = (0.40, 0.28, 0.17, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0)
COL_SCUFF = (0.33, 0.23, 0.14, 1.0)
COL_PLASTER_CEIL = (0.82, 0.76, 0.64, 1.0)
COL_MATTRESS = (0.80, 0.76, 0.66, 1.0)
COL_PILLOW = (0.88, 0.85, 0.78, 1.0)
COL_BLANKET = (0.38, 0.40, 0.44, 1.0)       # faded gray wool
COL_JACKET = (0.23, 0.21, 0.20, 1.0)        # the jacket on the chair (L324)
COL_DUFFLE = (0.38, 0.36, 0.24, 1.0)        # Korea canvas, olive (L104)
COL_DUFFLE_DK = (0.30, 0.28, 0.19, 1.0)
COL_MIRROR = (0.62, 0.68, 0.72, 1.0)        # opaque "small mirror" (L328)
COL_INK = (0.15, 0.13, 0.12, 1.0)
COL_ENVELOPE = (0.90, 0.86, 0.74, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=PAL, baseboard_face_sign=bb)
    # N wall carries the sash window as a REAL opening (playbook:
    # no glass slab) — piers + sill band + header band around a
    # 1.24 w × 1.40 h hole, z 0.98..2.38. Wall plane y = 5.0 ± 0.10.
    for psgn in (-1, +1):
        make_box(f"Wall_N_Pier_{psgn:+d}", (psgn * 1.41, ROOM_D, CEIL / 2.0),
                 (1.58, 0.20, CEIL), PAL["wall"])
    make_box("Wall_N_BelowSill", (0.0, ROOM_D, 0.49), (1.24, 0.20, 0.98),
             PAL["wall"])
    make_box("Wall_N_Header", (0.0, ROOM_D, 2.59), (1.24, 0.20, 0.42),
             PAL["wall"])
    make_box("Wall_N_Base", (0.0, ROOM_D - 0.06, 0.08), (ROOM_W + 0.4, 0.06, 0.16),
             PAL["baseboard"])
    # S wall: door gap x ∈ [-0.9, +0.9] (camera doorway) + header.
    make_wall("Wall_S_W", (-1.5, 0.0, 0), length=1.2, height=CEIL, axis='X',
              palette=PAL)
    make_wall("Wall_S_E", (+1.5, 0.0, 0), length=1.2, height=CEIL, axis='X',
              palette=PAL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 2.56), (1.80, 0.20, 0.48),
             PAL["wall"])
    make_box("Door_Lintel", (0.0, 0.0, 2.26), (2.00, 0.24, 0.12),
             NOLA_CYPRESS_DK)
    for psgn in (-1, +1):
        make_box(f"Door_Post_{psgn:+d}", (psgn * 0.95, 0.0, 1.10),
                 (0.10, 0.24, 2.20), NOLA_CYPRESS_DK)
    # The door Jimmy has a key to (L324) — swung open flat against
    # the SE wall interior (the doorway itself stays clear for the
    # camera). Hinges on the E post.
    make_box("Door_Slab", (1.40, 0.145, 1.10), (0.86, 0.05, 2.16),
             NOLA_CYPRESS)
    make_cyl("Door_Knob", (1.05, 0.19, 1.02), 0.024, 0.05, NOLA_BRASS,
             axis='Y', segments=8)
    make_box("Door_LockPlate", (1.05, 0.172, 1.02), (0.06, 0.006, 0.16),
             NOLA_BRASS)
    make_door_hinges("Door_Hinge", edge_x=0.97, edge_y=0.145,
                     edge_z_centers=[0.35, 1.10, 1.85], axis='X',
                     palette={"col": NOLA_IRON})
    # Plaster ceiling — no drop-tile grid in a Marigny walk-up.
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_PLASTER_CEIL},
                 with_grid=False, with_stains=False)
    make_box("Ceil_Stain", (-1.0, 1.2, CEIL - 0.006), (0.60, 0.60, 0.004),
             (0.70, 0.64, 0.50, 1.0))
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": NOLA_CYPRESS})
    # Humidity bloom on the E wall — worn, not derelict.
    make_box("Wall_E_Stain", (ROOM_W / 2.0 - 0.105, 3.9, 2.30),
             (0.015, 0.50, 0.40), (0.66, 0.58, 0.44, 1.0))
    # Wear path from the door to the desk.
    make_box("Floor_Scuff_Desk", (0.0, 2.4, 0.007), (0.60, 3.80, 0.002),
             COL_SCUFF)


def build_sash_window():
    """Double-hung sash in the N-wall opening (L340: 'He went to
    the window. He looked down at the street.'). Frame + meeting
    rail + muntin only — the opening stays open. A sliver of
    wrought-iron gallery rail sits outside the sill: second floor."""
    wy = ROOM_D
    # Outer frame.
    make_box("Sash_Head", (0.0, wy, 2.42), (1.44, 0.26, 0.08), NOLA_CYPRESS)
    for jsgn in (-1, +1):
        make_box(f"Sash_Jamb_{jsgn:+d}", (jsgn * 0.66, wy, 1.68),
                 (0.08, 0.26, 1.52), NOLA_CYPRESS)
    make_box("Sash_Sill_In", (0.0, wy - 0.14, 0.965), (1.50, 0.16, 0.05),
             NOLA_CYPRESS)
    make_box("Sash_Sill_Out", (0.0, wy + 0.13, 0.96), (1.50, 0.10, 0.05),
             NOLA_CYPRESS)
    # Lower sash (inner plane) — stiles + bottom rail.
    for ssgn in (-1, +1):
        make_box(f"Sash_Lower_Stile_{ssgn:+d}", (ssgn * 0.60, wy + 0.04, 1.32),
                 (0.05, 0.06, 0.68), NOLA_CYPRESS_DK)
    make_box("Sash_Lower_Bottom", (0.0, wy + 0.04, 1.015), (1.24, 0.06, 0.07),
             NOLA_CYPRESS_DK)
    # Meeting rail where the two sashes pass.
    make_box("Sash_MeetingRail", (0.0, wy + 0.02, 1.68), (1.24, 0.08, 0.06),
             NOLA_CYPRESS_DK)
    # Upper sash (outer plane) — stiles + top rail + one muntin.
    for ssgn in (-1, +1):
        make_box(f"Sash_Upper_Stile_{ssgn:+d}", (ssgn * 0.60, wy - 0.02, 2.015),
                 (0.05, 0.06, 0.61), NOLA_CYPRESS_DK)
    make_box("Sash_Upper_Top", (0.0, wy - 0.02, 2.35), (1.24, 0.06, 0.06),
             NOLA_CYPRESS_DK)
    make_box("Sash_Upper_Muntin", (0.0, wy - 0.02, 2.015), (0.04, 0.05, 0.61),
             NOLA_CYPRESS_DK)
    # Gallery rail outside — the street is DOWN there (L340).
    make_cyl("Gallery_TopRail", (0.0, wy + 0.38, 1.42), 0.018, 1.50,
             NOLA_IRON, axis='X', segments=8)
    for pi, px in enumerate([-0.60, -0.30, 0.0, 0.30, 0.60]):
        make_cyl(f"Gallery_Picket_{pi}", (px, wy + 0.38, 1.13), 0.010, 0.55,
                 NOLA_IRON, segments=6)


def build_desk():
    """The small desk under the window (L288) — drawer the paper
    came from, the letter written and read back twice (L292-L324),
    the pen set down beside it."""
    make_box("Desk_Top", (0.0, 4.55, 0.755), (1.08, 0.52, 0.04), NOLA_CYPRESS)
    for li, (lx, ly) in enumerate([(-0.48, 4.33), (0.48, 4.33),
                                    (-0.48, 4.77), (0.48, 4.77)]):
        make_cyl(f"Desk_Leg_{li}", (lx, ly, 0.3675), 0.022, 0.735,
                 NOLA_CYPRESS_DK, segments=6)
    make_box("Desk_Drawer", (0.0, 4.275, 0.66), (0.44, 0.03, 0.12),
             NOLA_CYPRESS_DK)
    make_cyl("Desk_DrawerKnob", (0.0, 4.253, 0.66), 0.012, 0.03, NOLA_BRASS,
             axis='Y', segments=8)
    # The letter — date at the top of the page the way he was taught
    # in the third grade (L292), "J —" (L304), the body, "— D."
    # (L320). Page top toward the window.
    make_box("Letter_Paper", (-0.10, 4.55, 0.776), (0.21, 0.28, 0.0015),
             P.PAPER)
    make_box("Letter_DateLine", (-0.16, 4.665, 0.7775), (0.07, 0.012, 0.0008),
             COL_INK)
    make_box("Letter_Salutation", (-0.175, 4.625, 0.7775), (0.05, 0.012, 0.0008),
             COL_INK)
    for bi, by in enumerate([4.585, 4.550, 4.515]):
        make_box(f"Letter_BodyLine_{bi}", (-0.105, by, 0.7775),
                 (0.17, 0.012, 0.0008), COL_INK)
    make_box("Letter_SignOff", (-0.16, 4.475, 0.7775), (0.05, 0.012, 0.0008),
             COL_INK)
    make_cyl("Desk_Pen", (0.06, 4.50, 0.782), 0.005, 0.135, COL_INK,
             axis='Y', segments=6)


def build_chair_and_jacket():
    """The chair at the desk; the jacket hanging on its back, where
    he always hangs it (L324); the sealed envelope's corner just
    showing at the inside pocket — where Jimmy will find it, if
    and when (L324)."""
    make_box("Chair_Seat", (0.0, 3.95, 0.475), (0.42, 0.40, 0.045),
             NOLA_CYPRESS)
    for li, (lx, ly) in enumerate([(-0.18, 3.78), (0.18, 3.78),
                                    (-0.18, 4.12), (0.18, 4.12)]):
        make_cyl(f"Chair_Leg_{li}", (lx, ly, 0.2275), 0.018, 0.455,
                 NOLA_CYPRESS_DK, segments=6)
    for bi, bx in enumerate([-0.18, 0.18]):
        make_cyl(f"Chair_BackPost_{bi}", (bx, 3.79, 0.75), 0.018, 0.50,
                 NOLA_CYPRESS_DK, segments=6)
    for si, sz in enumerate([0.78, 0.93]):
        make_box(f"Chair_BackSlat_{si}", (0.0, 3.79, sz), (0.40, 0.03, 0.07),
                 NOLA_CYPRESS)
    # The jacket, draped: shoulders over the top rail, back panel on
    # the S side, front panels hanging toward the seat.
    make_box("Jacket_Shoulders", (0.0, 3.83, 1.00), (0.46, 0.16, 0.07),
             COL_JACKET)
    make_box("Jacket_BackPanel", (0.0, 3.76, 0.77), (0.44, 0.06, 0.40),
             COL_JACKET)
    for fsgn in (-1, +1):
        make_box(f"Jacket_FrontPanel_{fsgn:+d}", (fsgn * 0.13, 3.90, 0.80),
                 (0.20, 0.05, 0.34), COL_JACKET)
    # Envelope corner at the inside pocket (L324).
    make_box("Jacket_EnvelopeCorner", (-0.13, 3.928, 0.90),
             (0.055, 0.012, 0.035), COL_ENVELOPE)


def build_bed():
    """Iron bed along the E wall — slept in 'briefly, badly'
    (L344): thrown blanket, kicked corner, one pillow."""
    bx, by = 1.325, 2.275                    # bed center; head at N end
    # Posts (brass finials — the one warm note the room came with).
    for pi, (px, py, ph) in enumerate([(0.82, 3.23, 1.05), (1.83, 3.23, 1.05),
                                        (0.82, 1.32, 0.80), (1.83, 1.32, 0.80)]):
        make_cyl(f"Bed_Post_{pi}", (px, py, ph / 2.0), 0.022, ph, NOLA_IRON,
                 segments=8)
        make_cyl(f"Bed_Finial_{pi}", (px, py, ph + 0.02), 0.030, 0.04,
                 NOLA_BRASS, segments=8)
    for ri, (ry, rz) in enumerate([(3.23, 0.92), (3.23, 0.68),
                                    (1.32, 0.70), (1.32, 0.52)]):
        make_cyl(f"Bed_Rail_{ri}", (bx, ry, rz), 0.014, 0.97, NOLA_IRON,
                 axis='X', segments=6)
    make_box("Bed_Frame", (bx, by, 0.30), (1.02, 1.86, 0.06), NOLA_IRON)
    make_box("Bed_Mattress", (bx, by, 0.40), (1.02, 1.86, 0.16), COL_MATTRESS)
    make_box("Bed_Sheet", (bx, by, 0.485), (0.98, 1.80, 0.02), NOLA_LINEN)
    make_box("Bed_Pillow", (bx, 3.02, 0.53), (0.80, 0.34, 0.10), COL_PILLOW)
    # The blanket, half thrown off (L344) — offset mass, fold ridge,
    # kicked corner hanging toward the floor side.
    make_box("Bed_Blanket", (1.31, 1.85, 0.505), (1.00, 0.95, 0.05),
             COL_BLANKET)
    make_box("Bed_Blanket_Fold", (1.20, 2.30, 0.535), (0.55, 0.18, 0.05),
             COL_BLANKET)
    make_box("Bed_Blanket_Kicked", (0.86, 1.45, 0.44), (0.24, 0.30, 0.16),
             COL_BLANKET)


def build_dresser_and_mirror():
    """The dresser, W wall, with the small mirror above it — where
    he looks at his own face and the face looks back (L328)."""
    make_box("Dresser_Body", (-1.63, 2.55, 0.51), (0.50, 0.92, 0.98),
             NOLA_CYPRESS)
    make_box("Dresser_Top", (-1.63, 2.55, 1.015), (0.54, 0.96, 0.03),
             NOLA_CYPRESS_DK)
    for di, dz in enumerate([0.30, 0.58, 0.86]):
        make_box(f"Dresser_Drawer_{di}", (-1.37, 2.55, dz), (0.02, 0.82, 0.24),
                 NOLA_CYPRESS_DK)
        for ksgn in (-1, +1):
            make_cyl(f"Dresser_Knob_{di}_{ksgn:+d}",
                     (-1.355, 2.55 + ksgn * 0.25, dz), 0.014, 0.025,
                     NOLA_BRASS, axis='X', segments=8)
    make_box("Mirror_Frame", (-1.885, 2.55, 1.70), (0.03, 0.55, 0.72),
             NOLA_CYPRESS_DK)
    make_box("Mirror_Glass", (-1.865, 2.55, 1.70), (0.02, 0.47, 0.64),
             COL_MIRROR)


def build_duffle():
    """The canvas duffle his father carried back from Korea,
    'battered enough to look intentional' (L104) — at the foot of
    the bed, packed the day he answered the summons."""
    make_cyl("Duffle_Body", (0.75, 0.95, 0.17), 0.155, 0.60, COL_DUFFLE,
             axis='X', segments=10)
    for csgn, cnm in ((-1, "W"), (+1, "E")):
        make_cyl(f"Duffle_Cap_{cnm}", (0.75 + csgn * 0.31, 0.95, 0.17),
                 0.158, 0.03, COL_DUFFLE_DK, axis='X', segments=10)
    make_box("Duffle_Strap", (0.75, 0.95, 0.325), (0.62, 0.04, 0.02),
             (0.28, 0.22, 0.15, 1.0))
    make_box("Duffle_Handle", (0.75, 0.95, 0.345), (0.18, 0.03, 0.045),
             (0.28, 0.22, 0.15, 1.0))
    # The battering — a sun-faded canvas patch and a dark scuff.
    make_box("Duffle_Patch", (0.62, 0.795, 0.20), (0.14, 0.02, 0.08),
             (0.55, 0.52, 0.42, 1.0))
    make_box("Duffle_Scuff", (0.92, 0.80, 0.12), (0.10, 0.015, 0.06),
             (0.26, 0.24, 0.16, 1.0))


def build_ceiling_infra():
    """Bare bulb on a cord — the only fixture; the .tscn's
    Key_BareBulb is named for it. Clock frozen at 12:24 (after the
    bar's 11:47 plus eight blocks; the chain rattles once, L344)."""
    make_cyl("Bulb_Cord", (0.0, 2.5, CEIL - 0.25), 0.005, 0.50, NOLA_IRON,
             segments=6)
    make_cyl("Bulb_Socket", (0.0, 2.5, CEIL - 0.53), 0.024, 0.06,
             (0.62, 0.62, 0.60, 1.0), segments=8)
    make_cyl("Bulb_Glass", (0.0, 2.5, CEIL - 0.61), 0.045, 0.10,
             (0.95, 0.85, 0.50, 1.0), segments=12)
    make_wall_clock("Clock", (-1.41, ROOM_D - 0.12, 2.30), frozen_hour=12,
                    frozen_min=24)
    make_smoke_detector("Smoke", (0.9, 1.4, CEIL))


def main():
    clear_scene()
    build_shell()
    build_sash_window()
    build_desk()
    build_chair_and_jacket()
    build_bed()
    build_dresser_and_mirror()
    build_duffle()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/new_orleans_room.glb"))
    print(f"\n[build_new_orleans_room] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
