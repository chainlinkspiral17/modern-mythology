"""cabin_interior — Tem's off-grid cabin, vol7's home base (29
scenes). Rebuilt 2026-08-03 hero-prop pass from the prose:

"The main room held the wood stove, the small wooden table beside
the kerosene lamp, two armchairs, a daybed where Kai had slept."
Plus: the sleeping loft above the kitchen with its ladder (Marina,
ch15), the thermometer above the door nailed there in 1979, the
writing desk in the east room with the cedar shelf ("the reader was
on the shelf where it had been since '46"), the black rotary phone
on a small table by the kitchen window, the side table by the wood
stove (the stick lives there in ch11), the cedar chest the wool
blankets come out of, the firewood basket, the copper kettle with
the dent, the coffee CONE (not a percolator), and a table that can
seat seven ("The seven stayed at the table").

No electricity: kerosene and candlelight only — the hanging oil
lamp over the table and the hurricane lantern are the practicals.

DETAIL DRAFT 5 (2026-09-17, the visual program's first background
pass — lore/_VISUAL_PROGRAM.md §3, cabin_interior is the game's
most-seen room at 31 placements): the primitive upgrade. The stove
is one turned potbelly on cast legs with an elbowed pipe into a wall
thimble; the kettle, oil lamp, hurricane lantern, basin, pitcher,
firewood basket, side-table pedestal and mason jars are lathe
profiles; the east bed and the desk come from the furniture kit
(turned legs, aprons, a made bed); the armchairs are chamfered
upholstery with rolled arms on turned feet; the cedar chest has its
straps and hasp; the vigil chair is a kit chair. Kerosene
INFRASTRUCTURE (D3 for a room with no wires): the fuel can and funnel
by the door, the match tin, the lamp's tin shade, the stovepipe
thimble. The .tscn loses the two fluorescent practicals a template
gave a cabin with no electricity and gains the lamp, lantern and
stove-door glow.

DRAFT 6 targets: the loft (deck, rail, mattress are still boxes —
turned balusters, a rope-lashed ladder); the kitchen counter's face
(a plank door, a drawer, the coffee cone as a lathe); the daybed's
blanket draped over the edge (a rot_box fold); the crow's window sill
and the Sitka trunks as lathes with bark taper; the table's SEVEN
chairs told apart (one with a cushion, one mended); Deck: the
contact sheet's establish + `insert bowls` under candlelight_low.

THE OUTSIDE + TEM'S PORCH · draft 1 (2026-10-08): twelve vol 7 porch
scenes were shot on the Millers' Texas back porch. The cabin grew a
building's outside (gable roof, foundation, siding, the stovepipe up
past the eave, the yard and the clearing's Sitkas) and the porch on its
south wall (deck, step, four posts, shed roof, rails with the coffee,
the cedar hand, the smokers' tin and the crow on them; the bench, a
chair, boots, firewood, the rain barrel, the chopping block). The
`cabin_porch` preset (Background3D) shoots it from the turnaround; its
markers are suffixed __cabin_porch. SAME DAY (the user: "The cabin
looks too small on the outside"): the roof went to a loft's pitch (ridge
~6.4 m) and the cabin grew OLAF'S SHOP, a west wing under its own lower
gable (build_shop_wing_2026_10); the truck parks in front of it.
PORCH DRAFT 2 targets: the shop's door (on its west gable) and a path
to it; the outside
is lit by the interior's rig (dim under morning_bright) — a per-preset
exterior light; the gravel road out of the clearing to the SW (cabin_
road's track); the crowns are single lathes (tiers with droop, a second
tone); the window's "square of yellow on the porch boards" at night (a
spot through the south window); moss on the roof and the step's edge;
the siding as boards with a shadow line rather than seams on a slab.

Coordinate frame: Blender Z-up, y=0 south wall with the door, +Y
into the cabin, x=±3.0, back wall y=6.0, ceiling 3.4 (raised for
the loft). glTF export remaps to Godot (x, z, -y).
"""
import os, sys
import math as _m
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_chair, make_table, make_bed
from _props import palette as P
from _props.geometry import (make_taper_cyl, clear_scene, make_box, make_cyl, make_lathe,
                             make_chamfer_box, make_tube, make_rot_box, make_prism, make_heightfield, make_blob, export_glb)
from _props.structure import make_floor, make_wall, make_ceiling, make_window
from _props.food_service import make_coffee_pots  # noqa: F401 (unused, kept for parity)

ROOM_W = 6.0; ROOM_D = 6.0; CEIL = 3.4
PAL_WALL = {"wall": (0.62, 0.46, 0.32, 1.0), "baseboard": (0.32, 0.22, 0.14, 1.0)}
COL_FLOOR = (0.42, 0.30, 0.20, 1.0); COL_SEAM = (0.22, 0.14, 0.10, 1.0)
COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_WOOD_DK = (0.34, 0.24, 0.15, 1.0)
COL_IRON = (0.14, 0.14, 0.16, 1.0)
COL_IRON_WM = (0.20, 0.19, 0.20, 1.0)
COL_COPPER = (0.72, 0.42, 0.22, 1.0)
COL_GLASS = (0.42, 0.52, 0.55, 0.6)
COL_WOOL = (0.42, 0.46, 0.55, 1.0)
GRAVEL = (0.35, 0.33, 0.27, 1.0)   # a tone off the yard's dirt, not a pale slab (2026-10-08: it read as a raised block)
YARD_Z = -0.40   # the ground round the cabin: the floor stands on a 0.40 m foundation (2026-10-08)


def _sitka(prefix, x, y, r, h, trunk, crown):
    """A Sitka spruce on the yard: a tapered trunk under a tiered,
    drooping crown that starts a quarter of the way up."""
    make_taper_cyl(f"{prefix}_Trunk", (x, y, YARD_Z + h / 2.0), r, r * 0.35, h, trunk, segments=8)
    # (draft 5, 2026-10-08) four drooping TIERS in two greens, each skirt
    # flaring out under the one above — one cone lit khaki in the sun
    R, H = min(2.0, r * 6.5), h * 0.80
    z0 = YARD_Z + h * 0.25
    dark = (crown[0] * 0.70, crown[1] * 0.74, crown[2] * 0.72, 1.0)
    for ti, (zb, zt, rb) in enumerate(((0.00, 0.40, 1.00), (0.22, 0.62, 0.80), (0.44, 0.82, 0.58), (0.64, 1.00, 0.36))):
        rr, t = R * rb, (zt - zb) * H
        # a SKIRT: the underside rises from the drooping rim to the trunk
        # (the first try flared from a ring and read as stacked bells)
        make_lathe(f"{prefix}_Crown_T{ti}", (x, y, z0 + zb * H),
                   [(0.0, 0.16 * t), (rr, 0.0), (rr * 0.88, 0.08 * t), (rr * 0.40, 0.70 * t), (0.0, t)],
                   crown if ti % 2 == 0 else dark, segments=10)


from _props.structure import make_wall_with_openings   # (2026-10-07)

from _props.structure import make_frame_ring   # (2026-10-07: the frame boards → rings)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    # (2026-10-07, window_backing_audit) the loop unrolled: Wall_E is cut
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1, openings=[(1.450, 1.750, 1.060, 0.820), (4.200, 1.600, 1.240, 0.940)])
    # the N wall built round a REAL opening for the kitchen window
    # (2026-09-23: the wall was solid, so the crow "seen through the
    # glass" on the outside sill was never in any frame)
    kw_x0, kw_x1, kw_z0, kw_z1 = -2.10, -1.10, 1.005, 1.955
    wn_x0, wn_x1 = -(ROOM_W + 0.2) / 2.0, (ROOM_W + 0.4) / 2.0   # west end flush with Wall_W's outer face: Olaf's shop abuts it (2026-10-08)
    wcol = PAL_WALL["wall"]
    make_box("Wall_N", ((kw_x1 + wn_x1) / 2.0, ROOM_D, CEIL / 2.0), (wn_x1 - kw_x1, 0.20, CEIL), wcol)
    make_box("Wall_N_W", ((wn_x0 + kw_x0) / 2.0, ROOM_D, CEIL / 2.0), (kw_x0 - wn_x0, 0.20, CEIL), wcol)
    make_box("Wall_N_Sill", ((kw_x0 + kw_x1) / 2.0, ROOM_D, kw_z0 / 2.0), (kw_x1 - kw_x0, 0.20, kw_z0), wcol)
    make_box("Wall_N_Head", ((kw_x0 + kw_x1) / 2.0, ROOM_D, (kw_z1 + CEIL) / 2.0), (kw_x1 - kw_x0, 0.20, CEIL - kw_z1), wcol)
    make_box("Wall_N_Base", (0.0, ROOM_D - 0.106, 0.08), (ROOM_W + 0.4, 0.012, 0.16), PAL_WALL["baseboard"])
    # the outside sill the crow stands on
    make_box("Kitchen_Window_OutSill", ((kw_x0 + kw_x1) / 2.0, ROOM_D + 0.275, 1.04), (1.10, 0.35, 0.04), wcol)
    make_wall_with_openings("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1, openings=[(-2.000, 1.450, 1.100, 1.000)])   # cut 2026-10-07 (window_backing_audit): the window was a pane on a solid wall
    make_wall_with_openings("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1, openings=[(2.000, 1.450, 0.950, 0.950)])   # cut 2026-10-07 (window_backing_audit): the window was a pane on a solid wall
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.45), (2.0, 0.20, 0.90), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 with_grid=False, with_stains=False,
                 palette={"tile": (0.48, 0.36, 0.26, 1.0)})
    # The thermometer above the door, nailed there in 1979
    make_box("Thermometer_Back", (0.0, 0.12, 2.60), (0.10, 0.03, 0.26), (0.82, 0.78, 0.68, 1.0))
    make_box("Thermometer_Tube", (0.0, 0.13, 2.60), (0.02, 0.02, 0.20), (0.72, 0.24, 0.20, 1.0))
    # The front door itself
    make_box("Front_Door", (0.0, 0.06, 1.05), (0.95, 0.05, 2.10), COL_WOOD_DK)
    # the door's head, up to the wall above it (2026-10-08: a 0.40 m slot
    # over the door showed the thermometer from the porch)
    make_box("Wall_S_DoorHead", (0.0, 0.0, 2.30), (0.951, 0.20, 0.40), PAL_WALL["wall"])
    make_cyl("Door_Latch", (0.36, 0.10, 1.02), 0.025, 0.04, COL_IRON, axis='Y', segments=8)
    # its OUTSIDE (2026-10-08, the porch): a board-and-batten door — four
    # boards with their seams, the Z-brace, two strap hinges and the
    # thumb-latch's handle. A flat dark slab under the porch sun was one
    # field the paint pass blotched into a disc.
    dy = 0.035 - 0.004
    for bi, bx in enumerate((-0.2375, 0.0, 0.2375)):
        make_box(f"Front_Door_Out_Seam_{bi}", (bx, dy, 1.05), (0.012, 0.008, 2.06), (0.22, 0.15, 0.10, 1.0))
    for ri, rz in enumerate((0.28, 1.82)):
        make_box(f"Front_Door_Out_Batten_{ri}", (0.0, dy - 0.012, rz), (0.86, 0.024, 0.14), (0.40, 0.29, 0.19, 1.0))
    make_prism("Front_Door_Out_Brace", (0.0, dy - 0.012, 0.0),
               [(-0.40, 0.36), (-0.27, 0.36), (0.40, 1.74), (0.27, 1.74)], 0.024, (0.40, 0.29, 0.19, 1.0), axis="Y")
    for hi, hz in enumerate((0.28, 1.82)):
        make_box(f"Front_Door_Out_Hinge_{hi}", (-0.25, dy - 0.027, hz), (0.42, 0.006, 0.05), COL_IRON)
    make_tube("Front_Door_Out_Handle", [(0.36, dy, 1.10), (0.36, dy - 0.06, 1.07), (0.36, dy - 0.06, 0.95), (0.36, dy, 0.92)],
              0.012, COL_IRON, segments=5)
    # Bedroom partition: the east room (Tem/Lena's) behind x=+1.0
    make_wall("East_Part", (1.0, 1.3, 0), length=2.6, height=CEIL, axis='Y', palette=PAL_WALL)
    make_box("East_Part_Header", (1.0, 2.85, CEIL-0.35), (0.16, 0.55, 0.70), PAL_WALL["wall"])


def build_kitchen():
    """W-wall kitchenette: counter (pulled off the N wall — the old
    anchor buried its own jars inside the wall), pot rack, coffee
    CONE + carafe, mason jars, the rotary phone by the kitchen
    window."""
    # Counter, y 3.4..5.8 along the W wall
    make_box("Counter_Body", (-1.90, 4.60, 0.46), (0.70, 2.40, 0.92), (0.78, 0.66, 0.42, 1.0))
    make_box("Counter_Top", (-1.90, 4.60, 0.945), (0.74, 2.46, 0.05), (0.32, 0.22, 0.14, 1.0))
    # Pour-over cone + carafe ("She had made coffee in the cabin's
    # cone… the run of the water through the grounds")
    make_cyl("Counter_Carafe", (-1.85, 4.10, 1.06), 0.075, 0.18, COL_GLASS, segments=10)
    make_cyl("Counter_Cone", (-1.85, 4.10, 1.20), 0.07, 0.09, (0.86, 0.82, 0.74, 1.0), segments=8)
    # Mason jars, capped inside the room now
    # Mason jars: the shoulder, the threaded neck, the ring lid — and
    # what is in them, at four different levels (draft 5: lathes)
    for i, (fill, fcol) in enumerate(((0.16, (0.62, 0.48, 0.26, 1.0)), (0.09, (0.86, 0.80, 0.62, 1.0)),
                                      (0.13, (0.40, 0.28, 0.18, 1.0)), (0.05, (0.90, 0.88, 0.80, 1.0)))):
        jy = 4.95 + i * 0.22
        make_lathe(f"Counter_Jar_{i}", (-1.80, jy, 0.97),
                   [(0.05, 0.0), (0.055, 0.01), (0.055, 0.16), (0.045, 0.19), (0.042, 0.215)],
                   (0.80, 0.82, 0.72, 0.85), segments=10)
        make_cyl(f"Counter_Jar_{i}_Contents", (-1.80, jy, 0.975 + fill / 2.0), 0.049, fill, fcol, segments=10)
        make_lathe(f"Counter_Jar_{i}_Lid", (-1.80, jy, 1.185),
                   [(0.045, 0.0), (0.056, 0.005), (0.056, 0.03), (0.0, 0.03)], COL_IRON, segments=10)
    # Hanging pot rack over the counter
    make_box("PotRack_Bar", (-1.7, 4.6, 2.0), (0.04, 1.4, 0.04), COL_IRON)
    for si, sy in enumerate((4.0, 5.2)):   # (2026-09-22: straps to the ceiling — the bar hung on nothing)
        make_box(f"PotRack_Strap_{si}", (-1.7, sy, (2.02 + CEIL) / 2.0), (0.03, 0.03, CEIL - 2.02), COL_IRON)
    for i, (py, r, h, col) in enumerate([(4.2, 0.11, 0.14, COL_IRON), (4.6, 0.13, 0.16, (0.55, 0.35, 0.18, 1.0)),
                                         (5.0, 0.10, 0.12, COL_IRON)]):
        make_cyl(f"PotRack_Hook_{i}", (-1.7, py, 1.9), 0.006, 0.16, COL_IRON_WM, segments=4)
        make_cyl(f"PotRack_Pot_{i}", (-1.7, py, 1.82 - h / 2.0 + 0.01), r, h, col, segments=10)   # hangs from its hook
    # The kitchen window (N wall over the counter's end)…
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    # see_through (2026-09-24): the crow on the OUTSIDE sill is the reason
    # this window exists, and the glass + warm pane render opaque — the
    # crow insert was filming a grey pane
    make_window("Kitchen_Window", (-1.6, ROOM_D - 0.10, 1.48), width=1.00, height=0.95,
                see_through=True)
    # …and the black rotary phone on a small table beside it
    make_box("Phone_Table", (-2.60, 5.35, 0.30), (0.45, 0.45, 0.60), COL_WOOD)
    make_box("Phone_Body", (-2.60, 5.35, 0.66), (0.24, 0.20, 0.10), (0.10, 0.10, 0.11, 1.0))
    make_cyl("Phone_Dial", (-2.60, 5.28, 0.72), 0.07, 0.02, (0.80, 0.78, 0.72, 1.0), axis='Y', segments=10)
    make_box("Phone_Handset", (-2.60, 5.42, 0.735), (0.22, 0.07, 0.05), (0.10, 0.10, 0.11, 1.0))   # in the cradle (2026-09-23: 1.5 cm over it)


def build_loft():
    """The sleeping loft above the kitchen + its ladder ("Marina
    woke at four-twenty in the loft above the kitchen. She came down
    the loft ladder.")"""
    make_box("Loft_Deck", (-1.6, 4.8, 2.10), (2.6, 2.4, 0.10), COL_WOOD)
    make_box("Loft_Beam", (-1.6, 3.62, 2.02), (2.6, 0.12, 0.16), COL_WOOD_DK)
    make_box("Loft_Mattress", (-1.9, 5.0, 2.24), (1.30, 1.90, 0.18), (0.88, 0.84, 0.76, 1.0))
    make_box("Loft_Blanket", (-1.9, 4.7, 2.34), (1.26, 1.10, 0.06), COL_WOOL)
    make_box("Loft_Rail", (-1.0, 3.66, 2.45), (1.6, 0.05, 0.06), COL_WOOD_DK)
    for bi, bx in enumerate((-1.6, -1.0, -0.4)):
        make_box(f"Loft_Rail_Bal_{bi}", (bx, 3.66, 2.30), (0.04, 0.04, 0.36), COL_WOOD_DK)
    # Ladder — against the loft's FRONT edge (the beam at y 3.62), rails
    # reaching the deck (2026-09-07 Deck: it stood UNDER the deck at
    # y 3.95, climbing into the loft's underside — "turned 90 degrees")
    # west end of the loft edge — clear of the table's chair ring (r 1.22) and the daybed
    # (2026-09-23: at y 3.50 the ladder stood 13 cm inside the kitchen
    # counter, which runs under the loft's open end. It stands in front
    # of the counter now and hooks over the loft beam.)
    for rx in (-2.30, -2.00):
        make_box(f"Ladder_Rail_{rx:.2f}", (rx, 3.30, 1.10), (0.05, 0.05, 2.20), COL_WOOD)
        make_box(f"Ladder_Hook_{rx:.2f}", (rx, 3.44, 2.125), (0.05, 0.24, 0.05), COL_WOOD_DK)
    for s in range(6):
        make_box(f"Ladder_Rung_{s}", (-2.15, 3.30, 0.30 + s * 0.36), (0.34, 0.04, 0.04), COL_WOOD_DK)


def build_stove_corner():
    """Potbelly stove NE + copper kettle + firewood basket + the
    side table where the stick and the reader sit + two armchairs
    pulled to the stove ("Cale and Per in the chairs by the
    stove")."""
    sx, sy = 2.3, 5.4
    # DETAIL DRAFT 5 (2026-09-17): the potbelly is ONE turned profile
    # — ash lip, the belly's swell, the waist, the cooking plate — on
    # four cast legs; the pipe rises, elbows, and enters the north
    # wall through its thimble. Three stacked cylinders read as a
    # water heater.
    for li, (lx, ly) in enumerate(((sx - 0.24, sy - 0.24), (sx + 0.24, sy - 0.24),
                                   (sx - 0.24, sy + 0.24), (sx + 0.24, sy + 0.24))):
        make_lathe(f"Stove_Leg_{li}", (lx, ly, 0.0),
                   [(0.05, 0.0), (0.035, 0.02), (0.03, 0.14), (0.045, 0.19), (0.045, 0.22)],
                   COL_IRON, segments=8)
    make_lathe("Stove_Body", (sx, sy, 0.20),
               [(0.30, 0.0), (0.34, 0.04), (0.36, 0.20), (0.35, 0.42), (0.31, 0.58),
                (0.27, 0.68), (0.26, 0.74), (0.30, 0.78), (0.32, 0.86), (0.31, 0.90),
                (0.24, 0.905), (0.0, 0.905)],
               COL_IRON, segments=16)
    make_lathe("Stove_Plate_Ring", (sx, sy, 1.10), [(0.16, 0.0), (0.17, 0.012), (0.10, 0.012), (0.0, 0.012)],
               COL_IRON_WM, segments=14)
    make_box("Stove_Door", (sx - 0.34, sy, 0.5), (0.04, 0.26, 0.30), COL_IRON_WM)
    make_box("Stove_Door_Hinge", (sx - 0.355, sy - 0.15, 0.5), (0.015, 0.02, 0.26), COL_IRON)
    make_cyl("Stove_Door_Latch", (sx - 0.365, sy + 0.11, 0.50), 0.012, 0.05, COL_IRON, axis='X', segments=6)
    make_box("Stove_EmberGlow", (sx - 0.355, sy, 0.5), (0.02, 0.16, 0.18), (0.95, 0.45, 0.15, 1.0))
    make_cyl("Stove_Pipe", (sx, sy, 1.62), 0.09, 1.02, COL_IRON_WM, segments=10)
    make_tube("Stove_Pipe_Elbow", [(sx, sy, 2.10), (sx, sy, 2.36), (sx, sy + 0.08, 2.44),
                                   (sx, sy + 0.18, 2.48), (sx, ROOM_D - 0.10, 2.48)],
              0.09, COL_IRON_WM, segments=10)
    make_cyl("Stove_Pipe_Thimble", (sx, ROOM_D - 0.10, 2.48), 0.15, 0.03, COL_IRON, axis='Y', segments=12)
    # THE COPPER KETTLE with the small dent in its side — a turned
    # body with a shoulder, the lid's knob, a spout that rises, a
    # bail handle over the top.
    kx, ky, kz = sx - 0.20, sy + 0.05, 1.12
    make_lathe("Copper_Kettle", (kx, ky, kz),
               [(0.07, 0.0), (0.11, 0.02), (0.12, 0.08), (0.10, 0.14), (0.06, 0.165),
                (0.065, 0.18), (0.02, 0.195), (0.02, 0.215), (0.0, 0.215)],
               COL_COPPER, segments=12)
    make_box("Copper_Kettle_Dent", (kx + 0.11, ky, kz + 0.07), (0.03, 0.06, 0.06), (0.58, 0.32, 0.18, 1.0))
    make_tube("Copper_Kettle_Spout", [(kx - 0.10, ky, kz + 0.06), (kx - 0.15, ky, kz + 0.10), (kx - 0.18, ky, kz + 0.15)],
              0.014, COL_COPPER, segments=6)
    make_tube("Copper_Kettle_Bail", [(kx - 0.08, ky, kz + 0.16), (kx - 0.07, ky, kz + 0.25), (kx, ky, kz + 0.29),
                              (kx + 0.07, ky, kz + 0.25), (kx + 0.08, ky, kz + 0.16)],
              0.008, COL_IRON, segments=5)
    # Firewood: the stack and the cedar BASKET beside the stove
    for r in range(3):
        for c in range(4):
            fy = 4.4 + c * 0.16
            fz = 0.12 + r * 0.16 + (0.0 if c % 2 == 0 else 0.02)
            make_cyl(f"Firewood_{r}_{c}", (2.7, fy, fz), 0.075, 0.5,
                     COL_WOOD if (r + c) % 2 else COL_WOOD_DK, segments=6, axis='X')
    # The firewood basket: a splayed weave, a rolled rim, the cedar
    # kindling standing in it (draft 5: a lathe, not two tins)
    make_lathe("Wood_Basket", (1.68, 5.70, 0.0),
               [(0.20, 0.0), (0.22, 0.02), (0.29, 0.36), (0.31, 0.40), (0.29, 0.42), (0.27, 0.40), (0.0, 0.40)],
               (0.56, 0.42, 0.26, 1.0), segments=12)
    for ki, (kdx, kdy) in enumerate(((-0.08, 0.02), (0.05, -0.07), (0.02, 0.09), (0.10, 0.04))):
        make_rot_box(f"Wood_Basket_Kindling_{ki}", (1.68 + kdx, 5.70 + kdy, 0.42),
                     (0.035, 0.035, 0.46), COL_WOOD_DK if ki % 2 else COL_WOOD,
                     yaw=0.4 * ki, pitch=0.12 + 0.05 * ki)
    # The side table by the wood stove ("She put the stick down on
    # the side table by the wood stove") — a turned pedestal on a foot
    make_chamfer_box("Stove_SideTable_Top", (1.60, 4.95, 0.54), (0.42, 0.42, 0.04), COL_WOOD, chamfer=0.01)
    make_lathe("Stove_SideTable_Post", (1.60, 4.95, 0.0),
               [(0.15, 0.0), (0.13, 0.03), (0.06, 0.05), (0.045, 0.16), (0.06, 0.24), (0.04, 0.34), (0.05, 0.48), (0.07, 0.52)],
               COL_WOOD, segments=10)
    # A tin of matches on the side table, by the stick's spot
    make_box("MatchTin", (1.72, 5.06, 0.57), (0.06, 0.04, 0.02), (0.62, 0.58, 0.44, 1.0))
    # The two armchairs, at the stove where the prose puts them —
    # upholstered: a chamfered cushion on a plinth, rolled arms, the
    # back's crest a soft edge, four turned feet under it all.
    upholstery = (0.44, 0.36, 0.28, 1.0)
    upholstery_dk = (0.40, 0.32, 0.25, 1.0)
    for ci, (cx, cy, tag) in enumerate(((1.35, 4.35, "A"), (0.85, 5.35, "B"))):
        for fi, (fx, fy) in enumerate(((cx - 0.28, cy - 0.28), (cx + 0.28, cy - 0.28),
                                       (cx - 0.28, cy + 0.28), (cx + 0.28, cy + 0.28))):
            make_lathe(f"Armchair_{tag}_Foot_{fi}", (fx, fy, 0.0),
                       [(0.03, 0.0), (0.035, 0.03), (0.025, 0.06), (0.03, 0.10)], COL_WOOD_DK, segments=8)
        make_chamfer_box(f"Armchair_{tag}_Base", (cx, cy, 0.27), (0.66, 0.66, 0.34), upholstery, chamfer=0.03)
        make_chamfer_box(f"Armchair_{tag}_Cushion", (cx - 0.04, cy, 0.475), (0.50, 0.44, 0.07), upholstery, chamfer=0.025)
        make_chamfer_box(f"Armchair_{tag}_Back", (cx + 0.28, cy, 0.66), (0.14, 0.66, 0.60), upholstery_dk, chamfer=0.04)
        for ay in (cy - 0.31, cy + 0.31):
            make_chamfer_box(f"Armchair_{tag}_Arm_{ay:.2f}", (cx, ay, 0.50), (0.62, 0.12, 0.30), upholstery_dk, chamfer=0.03)
            make_cyl(f"Armchair_{tag}_ArmRoll_{ay:.2f}", (cx - 0.05, ay, 0.66), 0.062, 0.52, upholstery_dk, axis='X', segments=10)
    # The wool blanket draped over armchair A
    make_chamfer_box("Armchair_Blanket", (1.35, 4.05, 0.62), (0.60, 0.10, 0.30), COL_WOOL, chamfer=0.02)
    # Cedar chest (the wool blankets live in it): chamfered box, a
    # lid with a lip, two iron straps over the top, the hasp at the front
    make_chamfer_box("Cedar_Chest", (2.55, 3.55, 0.26), (0.60, 1.05, 0.52), (0.56, 0.40, 0.24, 1.0), chamfer=0.012)
    make_chamfer_box("Cedar_Chest_Lid", (2.55, 3.55, 0.545), (0.64, 1.09, 0.05), (0.50, 0.36, 0.22, 1.0), chamfer=0.012)
    for si, syy in enumerate((3.20, 3.90)):
        make_box(f"Cedar_Chest_Strap_{si}", (2.55, syy, 0.572), (0.66, 0.04, 0.006), COL_IRON)
        make_box(f"Cedar_Chest_StrapDown_{si}", (2.24, syy, 0.40), (0.006, 0.04, 0.30), COL_IRON)
    make_box("Cedar_Chest_Hasp", (2.235, 3.55, 0.50), (0.008, 0.06, 0.09), COL_IRON)


def build_table():
    """The table seats SEVEN ("The seven stayed at the table") — a
    wide round top, seven simple chairs with backs and legs, the
    hurricane lantern on it, the braided rug beneath."""
    tx, ty = 0.0, 2.9
    make_cyl("Table_Top", (tx, ty, 0.76), 0.85, 0.05, COL_WOOD, segments=18)
    # DETAIL DRAFT 4 (2026-09-06): a turned pedestal on its foot, seven kit chairs
    make_lathe("Table_Pedestal", (tx, ty, 0.10), [(0.16, 0.0), (0.10, 0.06), (0.08, 0.20), (0.11, 0.36), (0.07, 0.50), (0.09, 0.62), (0.13, 0.635)], COL_WOOD, segments=12)
    make_lathe("Table_Foot", (tx, ty, 0.0), [(0.42, 0.0), (0.40, 0.06), (0.22, 0.09), (0.16, 0.10)], COL_WOOD_DK, segments=14)
    # seven chairs, the ring open toward the east partition (nobody sits
    # with their back in the wall)
    for ci, ang in enumerate((0.30, 1.05, 1.80, 2.55, 3.30, 4.05, 4.80)):
        cx, cy = tx + _m.cos(ang) * 1.22, ty + _m.sin(ang) * 1.22
        make_chair(f"Chair_{ci}", cx, cy, yaw=ang + 1.5708, wood=COL_WOOD, w=0.40)
    # ── OLAF'S TWO BOWLS · the hero prop of vol 7 ──────────────
    # (2026-08-12) The volume's central image — cued 21 times as
    # [shot:insert bowls] / [shot:insert bowl] across 46 chapters —
    # and it had never been modeled: every one of those inserts
    # zoomed into an empty table. "The two bowls had been carved by
    # one hand… the grain on the cedar was the same grain on both.
    # The depth of the spiral on the outside was the same depth.
    # The flame-mark pressed into the base with a heated iron was
    # on both — Olaf's mark for the family." Marit's bowl and the
    # substrate's bowl, side by side under the lamp.
    cedar_lt = (0.72, 0.52, 0.32, 1.0)   # planed cedar heartwood
    cedar_md = (0.62, 0.43, 0.26, 1.0)   # the turned outside
    cedar_dk = (0.44, 0.29, 0.18, 1.0)   # shadowed inside
    char = (0.20, 0.13, 0.09, 1.0)       # the heated-iron flame-mark
    top_z = 0.785
    for bi, bx_off in enumerate((-0.22, +0.22)):
        bx, by = tx + bx_off, ty - 0.06
        pfx = "Bowl_%s" % ("Marit" if bi == 0 else "Substrate")
        # Foot ring — a turned bowl sits on a small ring, not flat
        make_cyl(f"{pfx}_Foot", (bx, by, top_z + 0.012),
                 0.052, 0.024, cedar_dk, segments=14)
        # The flame-mark, pressed into the base beside the foot
        make_cyl(f"{pfx}_FlameMark", (bx, by, top_z + 0.003),
                 0.026, 0.004, char, segments=8)
        # Body: flares from foot to rim (the bowl silhouette)
        make_taper_cyl(f"{pfx}_Body", (bx, by, top_z + 0.072),
                       0.058, 0.115, 0.096, cedar_md, segments=16)
        # THE SPIRAL, cut into the outside — three shallow relief
        # bands at rising radius read as one turned spiral at
        # insert distance ("the depth of the spiral was the same").
        for si, (sz, sr) in enumerate(((0.040, 0.079), (0.072, 0.098),
                                       (0.104, 0.114))):
            make_cyl(f"{pfx}_Spiral_{si}", (bx, by, top_z + sz),
                     sr, 0.007, cedar_dk, segments=16)
        # Rim lip as a RING on the body's top, the hollow a darker disc
        # inside it (2026-09-25: the rim was a solid disc and the hollow
        # sat under it, inside the body — the bowls read as flat-topped
        # cylinders and the water lay buried)
        make_lathe(f"{pfx}_Rim", (bx, by, top_z + 0.120),
                   [(0.104, 0.0), (0.122, 0.0), (0.122, 0.020), (0.104, 0.020), (0.104, 0.0)],
                   cedar_lt, segments=16)
        make_cyl(f"{pfx}_Hollow", (bx, by, top_z + 0.121),
                 0.104, 0.002, cedar_dk, segments=16)
    # One bowl holds a little water from the wash; the other is dry —
    # the difference the chapter turns on, stated in one highlight.
    make_cyl("Bowl_Substrate_Water", (tx + 0.22, ty - 0.06, top_z + 0.124),
             0.094, 0.004, (0.58, 0.62, 0.60, 0.85), segments=14)

    # Braided oval rug under the table
    for i, (rr, col) in enumerate([(1.6, (0.46, 0.30, 0.24, 1.0)),
                                   (1.2, (0.54, 0.40, 0.28, 1.0)),
                                   (0.8, (0.40, 0.28, 0.22, 1.0))]):
        make_cyl(f"Rug_Ring_{i}", (tx, ty, 0.008 + i * 0.002), rr, 0.006, col, segments=16)
    # Hurricane lantern on the table — the font, the globe's swell,
    # the vented cap, the wire bail (draft 5: turned, not stacked)
    make_lathe("Lantern_Base", (0.35, 2.6, 0.785),
               [(0.055, 0.0), (0.06, 0.01), (0.05, 0.03), (0.055, 0.07), (0.035, 0.085), (0.03, 0.09)],
               COL_IRON, segments=10)
    make_lathe("Lantern_Glass", (0.35, 2.6, 0.875),
               [(0.03, 0.0), (0.045, 0.02), (0.052, 0.07), (0.045, 0.12), (0.03, 0.145)],
               (0.96, 0.86, 0.55, 0.8), segments=10)
    make_cyl("Lantern_Flame", (0.35, 2.6, 0.94), 0.010, 0.05, (1.0, 0.7, 0.2, 1.0), segments=5)
    make_lathe("Lantern_Cap", (0.35, 2.6, 1.02),
               [(0.03, 0.0), (0.05, 0.015), (0.045, 0.035), (0.025, 0.05), (0.02, 0.06), (0.0, 0.06)],
               COL_IRON, segments=10)
    make_tube("Lantern_Bail", [(0.30, 2.6, 1.03), (0.29, 2.6, 1.10), (0.35, 2.6, 1.14), (0.41, 2.6, 1.10), (0.40, 2.6, 1.03)],
              0.005, COL_IRON, segments=5)


def build_daybed():
    """The daybed against the W wall where Kai slept."""
    # draft 5: the frame stands on four turned feet, the mattress and
    # blanket have soft edges, the bolster is the roll it is
    for fi, (fx, fy) in enumerate(((-2.84, 0.96), (-2.00, 0.96), (-2.84, 2.84), (-2.00, 2.84))):
        make_lathe(f"Daybed_Foot_{fi}", (fx, fy, 0.0),
                   [(0.03, 0.0), (0.04, 0.02), (0.03, 0.05), (0.035, 0.08)], COL_WOOD_DK, segments=8)
    make_chamfer_box("Daybed_Frame", (-2.42, 1.9, 0.21), (0.92, 2.00, 0.26), COL_WOOD_DK, chamfer=0.012)
    make_chamfer_box("Daybed_Mattress", (-2.42, 1.9, 0.44), (0.86, 1.92, 0.16), (0.90, 0.86, 0.78, 1.0), chamfer=0.03)
    make_cyl("Daybed_Bolster", (-2.78, 1.9, 0.62), 0.11, 1.85, COL_WOOL, axis='Y', segments=10)
    make_chamfer_box("Daybed_Blanket", (-2.28, 1.5, 0.545), (0.84, 0.95, 0.06), (0.56, 0.40, 0.30, 1.0), chamfer=0.015)   # clear of the bolster (2026-09-07)
    # Chair by the SOUTH window, main room ("The chair by the south
    # window" / "Finn on the floor by the south window")
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("South_Window_W", (-2.0, 0.10, 1.45), width=1.10, height=1.00, room_dir=+1)
    make_chair("SWChair", -1.70, 0.95, yaw=3.1416, wood=COL_WOOD, w=0.44)


def build_east_room():
    """The east room behind the partition: the bed with its window
    above ("the window above the bed gave her the gray-green of
    cedars"), the writing desk with the cedar shelf ("the reader
    was on the shelf where it had been since '46"), the basin with
    the mirror over it."""
    # Bed along the E wall — the furniture kit's frame bed (draft 5):
    # legs, rails, a deck, the mattress, a made bed with its blanket
    # turned down and the pillows at the head (+Y, where they were)
    make_bed("EBed", 2.10, 1.75, head="+Y", w=1.45, d=1.90, style="frame",
             frame_col=COL_WOOD_DK, mattress_col=(0.90, 0.86, 0.78, 1.0),
             blanket_col=COL_WOOL, pillow_col=(0.96, 0.92, 0.86, 1.0), pillows=2,
             made=True, headboard=False)   # no headboard: shot_insert_chest looks past the bed's head at the chest
    # The window above the bed (E wall) — cedars beyond
    # on the wall's room face, glass in front of the frame (2026-09-24: frame and glass
    # were offset from the wall's CENTRE line — inside the wall, never visible)
    make_frame_ring("EBed_Win_Frame", (2.88, 1.45, 1.75), (0.04, 1.20, 0.95), COL_WOOD_DK)
    # "the window above the bed gave her the gray-green of cedars" (ch1):
    # the glass was a dark solid pane with nothing behind it (sheet 42) —
    # it is the cedars' grey-green now, with a cross of glazing bars
    make_box("EBed_Win_Glass", (2.85, 1.45, 1.75), (0.02, 1.06, 0.82), (0.50, 0.58, 0.52, 1.0))
    make_box("EBed_Win_Muntin_V", (2.835, 1.45, 1.75), (0.01, 0.04, 0.82), COL_WOOD_DK)
    make_box("EBed_Win_Muntin_H", (2.835, 1.45, 1.75), (0.01, 1.06, 0.04), COL_WOOD_DK)
    # Writing desk against the S wall + the south window over it —
    # the kit table: turned legs, an apron, a stretcher (draft 5)
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("South_Window_E", (2.0, 0.10, 1.45), width=0.95, height=0.95, room_dir=+1)
    make_table("Desk", 1.75, 0.55, w=0.95, d=0.60, h=0.75, wood=COL_WOOD, top_col=COL_WOOD)
    make_box("Desk_Notebook", (1.72, 0.52, 0.7575), (0.26, 0.20, 0.015), (0.30, 0.26, 0.22, 1.0))
    make_cyl("Desk_Pen", (1.90, 0.44, 0.754), 0.004, 0.14, (0.16, 0.16, 0.18, 1.0), axis='X', segments=5)
    # The cedar shelf above the desk — player, books, notebooks
    make_box("Cedar_Shelf", (1.75, 0.16, 1.55), (1.10, 0.24, 0.04), (0.56, 0.40, 0.24, 1.0))
    make_box("Shelf_Player", (1.45, 0.16, 1.63), (0.24, 0.16, 0.10), (0.20, 0.20, 0.22, 1.0))
    for bi in range(4):
        make_box(f"Shelf_Book_{bi}", (1.80 + bi * 0.10, 0.16, 1.66),
                 (0.07, 0.16, 0.20), [(0.48, 0.20, 0.16, 1.0), (0.22, 0.30, 0.24, 1.0),
                                      (0.60, 0.52, 0.36, 1.0), (0.30, 0.26, 0.34, 1.0)][bi])
    # Basin + mirror on the partition side — the enamel bowl is a
    # bowl (draft 5), with the pitcher beside it
    # east of the front door's swing (2026-09-24, the user: "doorways obstructed")
    make_chamfer_box("Basin_Stand", (0.75, 0.35, 0.42), (0.44, 0.36, 0.84), COL_WOOD, chamfer=0.01)
    make_lathe("Basin_Bowl", (0.75, 0.35, 0.84),
               [(0.08, 0.0), (0.13, 0.02), (0.165, 0.07), (0.175, 0.09), (0.16, 0.09), (0.0, 0.085)],
               (0.86, 0.86, 0.84, 1.0), segments=14)
    make_lathe("Basin_Pitcher", (0.62, 0.24, 0.84),
               [(0.045, 0.0), (0.06, 0.03), (0.065, 0.12), (0.045, 0.19), (0.05, 0.22), (0.0, 0.22)],
               (0.86, 0.86, 0.84, 1.0), segments=10)
    make_box("Basin_Mirror", (1.06, 2.35, 1.50), (0.03, 0.36, 0.50), (0.68, 0.74, 0.78, 1.0))


def build_wall_dressing():
    """North-wall art + antlers — now actually ON the wall (the old
    coords floated them 0.18 m outside the building)."""
    make_box("NorthWall_Frame", (-0.6, ROOM_D-0.12, 1.9), (0.5, 0.03, 0.4), COL_WOOD_DK)
    make_box("NorthWall_Frame_Art", (-0.6, ROOM_D-0.13, 1.9), (0.42, 0.02, 0.32), (0.46, 0.52, 0.44, 1.0))
    for sgn in (-1, +1):
        make_cyl("Antler_%+d" % sgn, (0.8 + sgn * 0.18, ROOM_D-0.12, 2.1), 0.02, 0.4,
                 (0.78, 0.74, 0.62, 1.0), segments=5)
        make_cyl("Antler_%+d_Tine" % sgn, (0.8 + sgn * 0.30, ROOM_D-0.12, 2.25), 0.015, 0.2,
                 (0.78, 0.74, 0.62, 1.0), segments=4)
    # The hanging oil lamp over the table — the cabin's practical
    # (no fluorescents in an off-grid kerosene cabin)
    # (draft 5: the font is a brass lathe with a burner collar, the
    # chimney flares, a tin reflector-shade hangs over it, three chains)
    for ci, ang in enumerate((0.0, 2.094, 4.189)):
        # from the ceiling itself (2026-09-23: 1.4 cm under it — the whole lamp hung on nothing)
        make_tube(f"OilLamp_Chain_{ci}", [(0.0, 2.9, CEIL - 0.01), (0.11 * _m.cos(ang), 2.9 + 0.11 * _m.sin(ang), CEIL - 0.50)],
                  0.006, COL_IRON, segments=4)
    make_lathe("OilLamp_Shade", (0.0, 2.9, CEIL - 0.56),
               [(0.0, 0.06), (0.06, 0.06), (0.16, 0.0), (0.17, 0.0), (0.07, 0.065), (0.0, 0.065)],
               (0.72, 0.68, 0.60, 1.0), segments=12)
    make_lathe("OilLamp_Font", (0.0, 2.9, CEIL - 0.72),
               [(0.04, 0.0), (0.09, 0.02), (0.10, 0.07), (0.08, 0.11), (0.05, 0.125), (0.05, 0.14), (0.035, 0.15)],
               (0.66, 0.52, 0.24, 1.0), segments=12)
    make_lathe("OilLamp_Chimney", (0.0, 2.9, CEIL - 0.57),
               [(0.035, 0.0), (0.05, 0.03), (0.045, 0.10), (0.03, 0.17), (0.028, 0.19)],
               (0.96, 0.86, 0.55, 0.8), segments=10)
    make_cyl("OilLamp_Flame", (0.0, 2.9, CEIL - 0.54), 0.010, 0.04, (1.0, 0.72, 0.24, 1.0), segments=5)
    # Curtained E window in the main… now inside the east room wall
    # segment north of the partition (main room's east outlook)
    make_frame_ring("Window_E_Frame", (2.88, 4.2, 1.6), (0.04, 1.4, 1.1), COL_WOOD_DK, bar=0.08)
    make_box("Window_E_Glass", (2.85, 4.2, 1.6), (0.02, 1.24, 0.94), COL_GLASS)
    for sgn in (-1, +1):
        make_box("Window_E_Curtain_%+d" % sgn, (2.815, 4.2 + sgn * 0.55, 1.6),
                 (0.05, 0.34, 1.14), (0.60, 0.28, 0.24, 1.0))


def build_crow_2026_08():
    """THE CROW at the cabin's kitchen window (north wall), seen
    through the glass from inside — the vol 7 motif made physical.
    Kitchen_Window sits at (-1.6, ROOM_D-0.04); the bird stands on
    the outside sill, which is where it always is.
    """
    from _props.creatures import make_crow
    make_crow("Crow", -1.6, ROOM_D + 0.30, 1.06, facing=1.0)


def build_wear_personality_2026_08():
    """WHOSE FEET, WHOSE SPILLS (wear-personality pass, 2026-08-19).

    The cabin's wear is TWO AGES deep and the difference is the
    story. Olaf lived here from '79 until he died: his wear is
    DECADES — the Sunday carving spot, the kettle ring, the path
    his feet cut. Tem's vigil is WEEKS — a faint new patch beside
    the daybed. New wear is narrower and shallower-toned than old
    wear; the floor remembers them differently.
    """
    from _props.detail import make_traffic_wear, make_floor_stain, make_scuff_band
    floor_dk = (0.36, 0.25, 0.16, 1.0)     # old traffic (12% dark)
    floor_pale = (0.50, 0.38, 0.27, 1.0)   # decades of chair scrape
    floor_new = (0.39, 0.275, 0.185, 1.0)  # weeks-old wear · faint
    ash = (0.30, 0.28, 0.26, 1.0)
    scorch = (0.20, 0.15, 0.11, 1.0)
    shaving = (0.60, 0.48, 0.30, 1.0)
    handworn = (0.62, 0.48, 0.30, 1.0)

    # ── OLAF'S DECADES ─────────────────────────────────────────
    # The path: door → table → kitchen → stove. Forty-five years
    # of the same three destinations.
    make_traffic_wear("Wear_Olaf_Path",
                      [(0.0, 0.6), (0.0, 2.0), (-0.6, 3.4), (-1.3, 4.6)],
                      width=0.55, tint=floor_dk)
    make_traffic_wear("Wear_Olaf_Path_Stove",
                      [(0.4, 3.3), (1.5, 4.6), (2.0, 5.0)],
                      width=0.5, tint=floor_dk)
    # THE SUNDAY SPOT · Olaf carved "a little of it every Sunday
    # afternoon" for decades, in the chair nearest the east light
    # at the table. The floor there is scraped PALE (chair legs),
    # with a shaving-dust crescent no broom ever fully got.
    make_floor_stain("Wear_SundaySpot_Scrape", (0.85, 2.55), radius=0.34,
                     tint=floor_pale, segments=10)
    make_floor_stain("Wear_SundaySpot_Shavings", (1.05, 2.35), radius=0.16,
                     tint=shaving, segments=8)
    # The table edge at that seat, worn lighter by forearms; a
    # knife-nick strip just inside the rim.
    make_box("Wear_Table_Forearm", (0.62, 2.62, 0.788), (0.34, 0.10, 0.006), handworn)
    make_box("Wear_Table_Nicks", (0.55, 2.70, 0.787), (0.22, 0.05, 0.004),
             (0.30, 0.21, 0.14, 1.0))
    # THE KETTLE RING · "He put the kettle on" — the same spot on
    # the stove top since '79. A darker ring, then the iron's own
    # color inside it (ring stains: two calls).
    make_cyl("Wear_KettleRing", (2.18, 5.32, 1.125), 0.115, 0.004, scorch, segments=10)
    make_cyl("Wear_KettleRing_In", (2.18, 5.32, 1.126), 0.085, 0.004,
             (0.24, 0.23, 0.22, 1.0), segments=10)
    # Ash fan on the floor in front of the stove door, and the
    # scorch where the flame-mark iron was always set down.
    make_floor_stain("Wear_AshFan", (1.75, 5.15), radius=0.30, tint=ash, segments=9)
    make_floor_stain("Wear_IronScorch", (1.95, 4.78), radius=0.07, tint=scorch, segments=6)
    # The marking iron itself, hanging by the stove — Olaf's mark
    # for the family, within reach of the fire that heats it.
    make_box("MarkIron_Hook", (2.72, ROOM_D - 0.13, 1.45), (0.04, 0.06, 0.06), COL_IRON)   # on the N wall face
    make_box("MarkIron_Shaft", (2.72, ROOM_D - 0.15, 1.18), (0.025, 0.025, 0.50), COL_IRON)
    make_box("MarkIron_Head", (2.72, ROOM_D - 0.15, 0.90), (0.06, 0.03, 0.06), COL_IRON_WM)
    # Door wear: the latch-hand patch and boot scuff at the base.
    make_box("Wear_Door_Hand", (0.30, 0.078, 1.04), (0.16, 0.008, 0.20), handworn)
    make_scuff_band("Wear_Door_Boot", (0.0, 0.085), 0.80, axis='X',
                    height=0.12, band_z=0.08, tint=(0.28, 0.20, 0.14, 1.0))
    # Ladder rungs worn pale at the grab line (the loft, decades).
    for s in (2, 3, 4):
        make_box("Wear_Rung_%d" % s, (-2.15, 3.2775, 0.305 + s * 0.36),
                 (0.20, 0.045, 0.012), handworn)
    # The reader's shelf shadow: "on the shelf where it had been
    # since '46" — the shelf around it darkened, the rectangle
    # under it the shelf's young color.
    make_box("Wear_Shelf_Dust", (1.75, 0.16, 1.572), (1.06, 0.22, 0.004),
             (0.48, 0.34, 0.20, 1.0))
    make_box("Wear_Shelf_ReaderShadow", (1.55, 0.16, 1.574), (0.26, 0.18, 0.004),
             (0.58, 0.42, 0.26, 1.0))
    # Counter drip-line below the kettle's pour path.
    # on the counter's face (2026-09-23: 2.4 cm in front of it)
    make_scuff_band("Wear_Counter_Drip", (-1.544, 4.60), 0.9, axis='Y',
                    height=0.10, band_z=0.55, tint=(0.26, 0.18, 0.11, 1.0))

    # ── TEM'S WEEKS ────────────────────────────────────────────
    # The chair beside the daybed and the short path to it — worn
    # FAINT and NARROW. Six weeks against forty-five years.
    # the kit chair (draft 5): back west, he faces the room (2026-09-07)
    make_chair("Vigil_Chair", -1.70, 1.9, yaw=-1.5708, wood=COL_WOOD, w=0.42)
    make_traffic_wear("Wear_Tem_Path",
                      [(0.0, 1.0), (-1.0, 1.5), (-1.55, 1.9)],
                      width=0.30, tint=floor_new)
    make_floor_stain("Wear_Tem_ChairSpot", (-1.70, 1.95), radius=0.20,
                     tint=floor_new, segments=8)
    # Her mug's ring on the daybed-side floor, one ring only —
    # weeks make one ring; decades make the kettle's.
    make_cyl("Wear_Tem_MugRing", (-2.02, 1.55, 0.008), 0.045, 0.003,
             (0.32, 0.22, 0.14, 1.0), segments=8)


def build_through_windows_2026_08():
    """D5 · the cabin's windows open on the stand. South pair: the
    Sitka band and fern floor the road builder renders at scale,
    here as a near band a few meters out (trunks + dark canopy +
    fern line). North kitchen window: the crow is already on the
    sill; past it, the woodpile lean-to and one pale trunk — and
    the strip of creek the prose keeps hearing.
    """
    trunk = (0.36, 0.28, 0.22, 1.0)
    canopy = (0.11, 0.25, 0.13, 1.0)
    fern = (0.24, 0.36, 0.20, 1.0)
    # SOUTH · the stand past the turnaround (2026-10-08: it stood 5-8 m
    # out, where the turnaround and the porch went; tapered trunks under
    # tiered crowns now, the canopy box gone)
    for ti, (tx3, ty3, tr3, th3) in enumerate((
            (-3.9, -10.5, 0.30, 16.0), (2.2, -12.6, 0.38, 19.0),
            (2.8, -10.8, 0.28, 15.0), (5.6, -12.6, 0.34, 18.0))):
        _sitka("Thru_S_Sitka_%d" % ti, tx3, ty3, tr3, th3, trunk, canopy)
    for fi3, (fx3, fl3, fh3) in enumerate(((-4.6, 3.0, 0.55), (-7.6, 2.6, 0.70), (3.6, 3.0, 0.50), (6.8, 2.6, 0.62))):
        make_chamfer_box("Thru_S_FernLine_%d" % fi3, (fx3, -9.4 - 0.2 * fi3, YARD_Z + fh3 / 2.0),
                         (fl3, 1.3, fh3), fern, chamfer=0.12)
    # NORTH · woodpile lean-to, a pale trunk, the creek strip — on the
    # yard's ground (0.40 below the floor) and the roof on four posts
    make_box("Thru_N_Leanto_Roof", (-2.6, 8.0, 1.30), (2.2, 1.4, 0.10),
             (0.40, 0.32, 0.24, 1.0))
    for pi4, (px4, py4) in enumerate(((-3.65, 7.35), (-1.55, 7.35), (-3.65, 8.65), (-1.55, 8.65))):
        make_box("Thru_N_Leanto_Post_%d" % pi4, (px4, py4, (YARD_Z + 1.25) / 2.0), (0.08, 0.08, 1.25 - YARD_Z),
                 (0.36, 0.28, 0.20, 1.0))
    for pi3, pz3 in enumerate((-0.26, 0.02, 0.30)):
        make_box("Thru_N_Woodrow_%d" % pi3, (-2.6, 8.0, pz3), (2.0, 1.1, 0.28),
                 (0.48, 0.38, 0.26, 1.0))
    make_taper_cyl("Thru_N_PaleTrunk", (0.6, 9.5, YARD_Z + 3.0), 0.30, 0.16, 6.0,
                   (0.55, 0.50, 0.42, 1.0), segments=7)
    make_box("Thru_N_CreekStrip", (0.0, 11.5, YARD_Z + 0.02), (10.0, 1.2, 0.04),
             (0.35, 0.42, 0.44, 0.9))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Fifteen distinct cues fire on Tem's cabin — the vol7 heart —
    and most had nothing to aim at. Existing anchors: the desk
    (+notebook), Shelf_Player, Door_Latch (SYNONYMS doorknob ->
    latch). Built here, each at its prose station:

    TABLE (top 0.785; the two bowls + lantern already hold the
    south-centre):
    - THE HEXAGON laid out north ("six in the ring, the cedar face
      in the center, the AR I A piece beside").
    - THE THREE STICKS in waxed-paper sleeves, west ("one of the
      three sticks in the waxed-paper sleeves ... the middle of
      the three").
    - THE PACKAGE (the charred-wood parcel), south-west.
    - THE CUP (the heavy ceramic cup from the cheese-factory-town
      pottery), north-east.
    - THE DISC-CASE ("The disc-case was on the kitchen table"),
      east.
    - THE EGGS: the skillet with four yolks intact on the folded
      towel Tem uses as a trivet, north-west.
    - THE HAND (residue): a hand-worn patch at the west chair
      place, where her hand went on his.
    - THE FACE: the shallow relief inside Marit's bowl, flush on
      the rim disc ("visible only when Per tilted the bowl into
      the kerosene-lamp light").
    DAYBED:
    - THE CAP (Tem's warm fabric band) folded on the bolster.
    - THE HANDS (residue): two blanket creases where Tem's hand
      came up from under it to the back of Lena's neck.
    OUTSIDE, on a gravel turnaround north of the fern line:
    - THE TRUCK: Finn's grandfather's Toyota, seen from the west
      south window.
    - THE WAGON: the station wagon that came up the road at nine
      fifty-two, seen from the east south window.
    """
    cedar = (0.55, 0.38, 0.26, 1.0)
    cedar_dk = (0.44, 0.30, 0.20, 1.0)
    waxpaper = (0.88, 0.84, 0.72, 1.0)
    T = 0.785   # table top
    # ── THE HEXAGON · table north ──
    hx, hy = 0.0, 3.40
    make_box("Hexagon_Cloth", (hx, hy, T + 0.002), (0.40, 0.36, 0.004), (0.78, 0.74, 0.64, 1.0))
    for hi in range(6):
        ang = _m.pi / 3.0 * hi + _m.pi / 6.0
        make_box(f"Hexagon_Ring_{hi}", (hx + 0.13 * _m.cos(ang), hy + 0.13 * _m.sin(ang), T + 0.013),
                 (0.085, 0.085, 0.018), cedar)
    make_cyl("Hexagon_Center_Face", (hx, hy, T + 0.012), 0.055, 0.016, cedar_dk, segments=12)
    make_cyl("Hexagon_Face_Inlay", (hx, hy, T + 0.0215), 0.030, 0.003, (0.62, 0.46, 0.32, 1.0), segments=10)
    make_box("Hexagon_Aria_Piece", (0.155, 3.255, T + 0.014), (0.070, 0.050, 0.020), cedar)
    # ── THE THREE STICKS · table west ──
    for si2, sy2 in enumerate((2.75, 2.90, 3.05)):
        make_box(f"Stick_Sleeve_{si2}", (-0.50, sy2, T + 0.010), (0.26, 0.09, 0.020), waxpaper)
        make_box(f"Stick_Label_{si2}", (-0.50, sy2, T + 0.021), (0.10, 0.05, 0.002), (0.96, 0.95, 0.92, 1.0))
    # ── THE PACKAGE · table south-west ──
    make_box("Charred_Package", (-0.45, 2.35, T + 0.040), (0.22, 0.16, 0.080), (0.66, 0.56, 0.42, 1.0))
    make_box("Package_Twine", (-0.45, 2.35, T + 0.0815), (0.24, 0.012, 0.003), (0.42, 0.36, 0.26, 1.0))
    # ── THE CUP · table north-east ──
    make_cyl("Ceramic_Cup", (0.58, 3.30, T + 0.050), 0.045, 0.100, (0.52, 0.44, 0.36, 1.0), segments=10)
    make_cyl("Ceramic_Cup_Coffee", (0.58, 3.30, T + 0.1015), 0.036, 0.003, (0.24, 0.16, 0.10, 1.0), segments=10)
    # ── THE DISC-CASE · table east ──
    make_box("Disc_Case", (0.72, 2.90, T + 0.0075), (0.14, 0.125, 0.015), (0.18, 0.18, 0.20, 1.0))
    make_box("Disc_Case_Label", (0.72, 2.90, T + 0.0158), (0.10, 0.06, 0.001), (0.82, 0.80, 0.74, 1.0))
    # ── THE HEADSET · beside the disc-case (vol7 epilogue, The Submission:
    # "Tem took off the headset. She set it on the kitchen table beside
    # the disc-case.") Visor down, strap arms back, the lens plate dark.
    make_box("Headset_Visor", (0.50, 3.05, T + 0.045), (0.18, 0.10, 0.09), (0.16, 0.16, 0.18, 1.0))
    make_box("Headset_Front_Plate", (0.50, 2.999, T + 0.045), (0.16, 0.002, 0.07), (0.08, 0.09, 0.11, 1.0))
    make_box("Headset_Foam", (0.50, 3.1005, T + 0.045), (0.17, 0.001, 0.08), (0.30, 0.28, 0.26, 1.0))
    for sgn, nm in ((1, "R"), (-1, "L")):
        make_box(f"Headset_Strap_{nm}", (0.50 + sgn * 0.0975, 3.17, T + 0.045), (0.015, 0.14, 0.03), (0.20, 0.20, 0.22, 1.0))
    make_box("Headset_Strap_Back", (0.50, 3.2475, T + 0.045), (0.21, 0.015, 0.03), (0.20, 0.20, 0.22, 1.0))
    make_box("Headset_Cable", (0.50, 3.34, T + 0.003), (0.008, 0.17, 0.006), (0.12, 0.12, 0.13, 1.0))
    # ── THE EGGS · skillet on the folded towel, table north-west ──
    make_box("Trivet_Towel", (-0.45, 3.40, T + 0.004), (0.30, 0.30, 0.008), (0.70, 0.62, 0.50, 1.0))
    make_cyl("Egg_Skillet", (-0.45, 3.40, T + 0.0255), 0.140, 0.035, (0.16, 0.16, 0.17, 1.0), segments=12)
    make_box("Egg_Skillet_Handle", (-0.67, 3.40, T + 0.028), (0.16, 0.03, 0.012), (0.14, 0.14, 0.15, 1.0))
    for ei, (ex2, ey2) in enumerate(((-0.50, 3.35), (-0.40, 3.35), (-0.50, 3.45), (-0.40, 3.45))):
        make_cyl(f"Egg_White_{ei}", (ex2, ey2, T + 0.049), 0.030, 0.012, (0.96, 0.94, 0.90, 1.0), segments=8)
        make_cyl(f"Egg_Yolk_{ei}", (ex2, ey2, T + 0.058), 0.013, 0.006, (0.94, 0.72, 0.20, 1.0), segments=8)
    # ── THE HAND · worn patch at the west chair place ──
    make_box("Hand_Table_Patch", (-0.75, 2.90, T + 0.001), (0.12, 0.14, 0.002), (0.50, 0.40, 0.28, 1.0))
    # ── THE FACE · relief inside Marit's bowl, flush on the rim disc ──
    make_cyl("Bowl_Face_Inlay", (-0.22, 2.84, 0.9155), 0.040, 0.003, (0.60, 0.44, 0.30, 1.0), segments=10)
    # ── THE CAP · folded on the daybed bolster (top 0.73) ──
    make_box("Fabric_Cap", (-2.78, 1.55, 0.7425), (0.14, 0.18, 0.025), (0.62, 0.30, 0.28, 1.0))
    # ── THE HANDS · blanket creases (blanket top 0.575) ──
    make_box("Hands_Blanket_Crease_A", (-2.25, 1.35, 0.581), (0.16, 0.05, 0.012), (0.50, 0.36, 0.27, 1.0))
    make_box("Hands_Blanket_Crease_B", (-2.20, 1.22, 0.580), (0.05, 0.13, 0.010), (0.48, 0.34, 0.26, 1.0))
    # ── OUTSIDE · "the small gravel turnaround in front of the cabin's
    # porch" (2026-10-08: it moved south of the new porch, onto the yard's
    # ground 0.40 below the cabin floor; the two vehicles are the kit's
    # cars, parked nose-in to the porch either side of the steps — they
    # were four boxes each, standing where the porch now is)
    from _props.vehicles import make_car
    make_cyl("Gravel_Turnaround", (0.2, -5.9, YARD_Z + 0.006), 3.6, 0.012, GRAVEL, segments=36)   # round, and a tone off the dirt (a pale slab on the 10-08 sheet)
    make_cyl("Gravel_Turnaround_Shop", (-4.4, -6.0, YARD_Z + 0.004), 2.4, 0.008, GRAVEL, segments=28)   # where the truck pulls in, in front of the shop
    # the road out (draft 5): the gravel track leaves the turnaround to the
    # south and goes into the trees through a cut in the bank — the way
    # the wagon came up "at nine fifty-two"; two darker wheel tracks on it
    road = [(-1.3, -8.9), (1.5, -8.9), (-1.0, -18.0), (-4.4, -18.0)]
    _prism_ccw_z("Gravel_Road", road, YARD_Z + 0.004, 0.008, GRAVEL)
    for wi, off in enumerate((0.75, 2.05)):
        trk = [(-1.3 + off - 0.16, -9.0), (-1.3 + off + 0.16, -9.0), (-4.4 + off * 1.2 + 0.16, -17.9), (-4.4 + off * 1.2 - 0.16, -17.9)]
        _prism_ccw_z(f"Gravel_Road_Track_{wi}", trk, YARD_Z + 0.0085, 0.001, (0.29, 0.27, 0.22, 1.0))
    make_car("Finn_Truck", -5.4, -6.2, 4.8, (0.44, 0.48, 0.42, 1.0), pickup=True, along="Y", z0=YARD_Z)
    make_car("Station_Wagon", 3.7, -5.9, 5.0, (0.48, 0.36, 0.26, 1.0), along="Y", z0=YARD_Z)
    # the wagon's roof rack, on the roofline (z0 + 1.46)
    make_box("Station_Wagon_Rack", (3.7, -6.2, YARD_Z + 1.48), (1.20, 1.40, 0.04), (0.30, 0.30, 0.32, 1.0))


def build_kerosene_infra_2026_09():
    """D3 for a room with no wires (draft 5): what an off-grid cabin
    is plugged into. The kerosene can and its funnel inside the door
    on the west side, where a can gets set down; a spare lamp chimney
    on the counter's end; the lamp's wick-trimmer scissors on the
    side table. Positions clear of the door swing (x ±0.5) and the
    daybed (x < -1.96)."""
    tin = (0.56, 0.20, 0.16, 1.0)
    tin_dk = (0.40, 0.14, 0.12, 1.0)
    # The kerosene can: a square-shouldered can with a screw cap and
    # a wire-and-wood handle
    make_chamfer_box("Kerosene_Can", (-1.15, 0.40, 0.14), (0.24, 0.16, 0.28), tin, chamfer=0.015)
    make_lathe("Kerosene_Can_Neck", (-1.22, 0.40, 0.28), [(0.03, 0.0), (0.03, 0.03), (0.035, 0.035), (0.035, 0.05), (0.0, 0.05)], tin_dk, segments=8)
    make_tube("Kerosene_Can_Handle", [(-1.06, 0.34, 0.28), (-1.06, 0.34, 0.36), (-1.06, 0.46, 0.36), (-1.06, 0.46, 0.28)],
              0.006, COL_IRON, segments=5)
    make_cyl("Kerosene_Can_Grip", (-1.06, 0.40, 0.36), 0.012, 0.08, COL_WOOD_DK, axis='Y', segments=6)
    # The funnel, upside down on the can's shoulder
    make_lathe("Kerosene_Funnel", (-1.10, 0.44, 0.28), [(0.012, 0.0), (0.012, 0.03), (0.06, 0.09), (0.062, 0.095), (0.0, 0.095)], (0.70, 0.70, 0.68, 1.0), segments=10)
    # A spare chimney at the counter's south end, in its paper
    make_lathe("Spare_Chimney", (-1.90, 3.55, 0.97), [(0.035, 0.0), (0.05, 0.03), (0.045, 0.10), (0.03, 0.17), (0.028, 0.19)],
               (0.92, 0.90, 0.84, 0.9), segments=10)
    # Wick-trimmer scissors on the stove side table, beside the tin
    make_box("Wick_Scissors_A", (1.52, 4.86, 0.562), (0.12, 0.012, 0.004), COL_IRON)
    make_rot_box("Wick_Scissors_B", (1.52, 4.86, 0.566), (0.12, 0.012, 0.004), COL_IRON, yaw=0.35)



def build_door_infill_front_door_2026_09():
    """Front_Door was narrower than its wall opening (the user, 2026-09-24:
    "doorways ... misaligned"): close the gap to the door and its frame."""
    make_wall("Wall_Fill_Front_Door_W", (-0.738, 0.000, 0), length=0.525, height=2.500, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_Fill_Front_Door_E", (0.738, 0.000, 0), length=0.525, height=2.500, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)

def _prism_ccw_z(name, poly, z, h, col):
    """A flat footprint (any quad on the ground) at centre height z, h thick."""
    _prism_ccw(name, (0.0, 0.0, z), poly, h, col, axis="Z")


def _prism_ccw(name, center, poly, length, col, axis="X"):
    """make_prism wants the polygon counter-clockwise; take it either way."""
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    make_prism(name, center, poly if area > 0 else list(reversed(poly)), length, col, axis=axis)


def build_exterior_2026_10():
    """THE OUTSIDE OF THE CABIN (2026-10-08). Twelve vol 7 chapters are
    set on the cabin's porch and they were shot on the Millers' TEXAS
    back porch — a different house in a different state — because the
    cabin had no outside: a box of walls with a flat lid, on nothing,
    the vehicles parked against the front wall. To build a porch the
    cabin needs the rest of a building first:

    - a gable ROOF on the walls (ridge E-W over the room's middle, the
      eaves overhanging 0.45 m), the gable ends filled;
    - the FOUNDATION: the floor stands 0.40 m over the yard (a cabin
      in a rain forest is never on the dirt), a stone course round it;
    - board SIDING lines on the outside faces, broken at the openings;
    - the STOVEPIPE outside, out of the north wall and up past the eave;
    - the YARD: ground to the forest, Sitkas round the clearing and a
      dark band past them where the set ends.
    """
    ground = (0.31, 0.28, 0.21, 1.0)
    stone = (0.42, 0.41, 0.38, 1.0)
    shake = (0.30, 0.25, 0.21, 1.0)
    seam = (0.40, 0.29, 0.19, 1.0)
    make_box("Yard_Ground", (0.0, -2.0, YARD_Z - 0.02), (32.0, 36.0, 0.04), ground)
    # foundation: a stone course under the walls, floor to ground
    fz, fh = YARD_Z / 2.0, -YARD_Z
    make_box("Foundation_S", (0.0, 0.0, fz), (ROOM_W + 0.2, 0.20, fh), stone)
    make_box("Foundation_N", (0.0, ROOM_D, fz), (ROOM_W + 0.2, 0.20, fh), stone)
    for e, nm in ((-1, "W"), (1, "E")):
        make_box(f"Foundation_{nm}", (e * ROOM_W / 2.0, ROOM_D / 2.0, fz), (0.20, ROOM_D - 0.2, fh), stone)
    # the roof: two slabs from eave to ridge, the gable ends under them
    pitch = 0.95   # (2026-10-08, the user: "the cabin looks too small on the outside") a loft's roof, ridge ~6.4 m — was 0.60, a shed's
    under_s = lambda y: CEIL + pitch * (y + 0.20)              # on the side walls' outer corners (y -0.20 / 6.20)
    ridge_y = ROOM_D / 2.0
    ridge_z = under_s(ridge_y)
    eave = 0.45
    th = 0.18
    # each slab in two: the eave past the wall's outside face, the main
    # plane from that face up (the recorder reads a prism as its bounding
    # box — one piece would read as a roof sunk into every wall top)
    def slab(name, ya, yb, under):
        _prism_ccw(name, (0.0, 0.0, 0.0),
                   [(ya, under(ya)), (yb, under(yb)), (yb, under(yb) + th), (ya, under(ya) + th)], ROOM_W + 1.2, shake)
    under_n = lambda y: ridge_z - pitch * (y - ridge_y)
    slab("Roof_S_Eave", -0.20 - eave, -0.20, under_s)
    slab("Roof_S", -0.20, ridge_y, under_s)
    slab("Roof_N", ridge_y, ROOM_D + 0.20, under_n)
    slab("Roof_N_Eave", ROOM_D + 0.20, ROOM_D + 0.20 + eave, under_n)
    # the frieze boards close the slit between the wall tops and the roof
    for e, nm in ((-1, "S"), (1, "N")):
        make_box(f"Roof_Frieze_{nm}", (0.0, ROOM_D / 2.0 + e * (ROOM_D / 2.0 + 0.103), CEIL - 0.05), (ROOM_W - 0.2, 0.006, 0.10), shake)
    make_box("Roof_Ridge", (0.0, ridge_y, ridge_z + th + 0.03), (ROOM_W + 1.2, 0.26, 0.06), (0.24, 0.20, 0.17, 1.0))
    for e, nm in ((-1, "W"), (1, "E")):
        _prism_ccw(f"Gable_{nm}", (e * ROOM_W / 2.0, 0.0, 0.0),
                   [(-0.20, CEIL), (ROOM_D + 0.20, CEIL), (ridge_y, ridge_z - 0.02)], 0.20, PAL_WALL["wall"])
        # the gable's vent, under the ridge
        make_box(f"Gable_{nm}_Vent", (e * (ROOM_W / 2.0 + 0.105), ridge_y, ridge_z - 0.55), (0.01, 0.40, 0.30), (0.20, 0.15, 0.11, 1.0))
    # siding: the board lines on the outside faces, broken at the openings
    def rows(lo, hi, holes):
        """[lo, hi] minus the hole spans → the board runs."""
        runs, cur = [], lo
        for a, b in sorted(holes):
            if a > cur:
                runs.append((cur, a))
            cur = max(cur, b)
        if cur < hi:
            runs.append((cur, hi))
        return runs
    s_holes = [((-2.55, -1.45), (0.95, 1.95)), ((1.525, 2.475), (0.975, 1.925)), ((-0.50, 0.50), (0.0, 2.10))]
    e_holes = [((0.92, 1.98), (1.34, 2.16)), ((3.58, 4.82), (1.13, 2.07))]
    for k in range(1, 15):
        z = k * 0.225
        if z > CEIL - 0.30:
            break
        for ri, (a, b) in enumerate(rows(-2.9, 2.9, [h[0] for h in s_holes if h[1][0] - 0.01 < z < h[1][1] + 0.01])):
            if b - a > 0.05:
                make_box(f"Siding_S_{k}_{ri}", ((a + b) / 2.0, -0.103, z), (b - a, 0.006, 0.012), seam)
        for ri, (a, b) in enumerate(rows(-0.20, ROOM_D - 0.10, [h[0] for h in e_holes if h[1][0] - 0.01 < z < h[1][1] + 0.01])):
            if b - a > 0.05:
                make_box(f"Siding_E_{k}_{ri}", (ROOM_W / 2.0 + 0.103, (a + b) / 2.0, z), (0.006, b - a, 0.012), seam)
        make_box(f"Siding_W_{k}", (-ROOM_W / 2.0 - 0.103, (ROOM_D - 0.30) / 2.0, z), (0.006, ROOM_D - 0.10, 0.012), seam)
    # the stovepipe outside: out of the thimble, past the eave, up over the roof
    sx, pz = 2.3, 2.48
    py = ROOM_D + 0.20 + eave + 0.20
    make_tube("Stove_Pipe_Out", [(sx, ROOM_D + 0.10, pz), (sx, py - 0.12, pz), (sx, py, pz + 0.12)], 0.09, COL_IRON_WM, segments=10)
    make_cyl("Stove_Pipe_Out_Rise", (sx, py, (pz + 0.12 + ridge_z + 0.9) / 2.0), 0.09, ridge_z + 0.9 - pz - 0.12, COL_IRON_WM, segments=10)
    make_lathe("Stove_Pipe_Out_Cap", (sx, py, ridge_z + 0.9),
               [(0.10, 0.0), (0.10, 0.06), (0.0, 0.06), (0.0, 0.10), (0.20, 0.10), (0.0, 0.20)], COL_IRON, segments=10)
    # the clearing's edge: Sitkas round the cabin, a dark band past them
    trunk = (0.36, 0.28, 0.22, 1.0)
    crown = (0.11, 0.25, 0.13, 1.0)   # greener: under the porch sun the old tone lit tan (2026-10-08)
    for ti, (tx, ty, tr, tht) in enumerate((
            (-9.0, -3.6, 0.32, 17.0), (-10.0, 1.8, 0.36, 19.0), (-9.2, 7.0, 0.30, 16.0),
            (8.4, -0.6, 0.30, 16.0), (7.2, 3.6, 0.38, 20.0), (6.4, 7.4, 0.32, 17.0),
            (3.6, 11.0, 0.34, 18.0), (-5.6, 11.6, 0.30, 16.0))):
        _sitka(f"Yard_Sitka_{ti}", tx, ty, tr, tht, trunk, crown)
    # the clearing's EDGE RISES (2026-10-08, the user: "Why are the vehicles
    # on a big block that sits above the bottom of the cabin"): the yard was
    # one flat plane to the forest band, so its far edge met the dark band
    # at eye level — the whole clearing read as a plinth with the cabin sunk
    # in it. The ground climbs 1.8 m into the trees now, in a ring of berms
    # outside everything that stands in the clearing, and the band stands
    # on the berms' crest.
    import math as _mm
    duff = (0.24, 0.24, 0.17, 1.0)
    rise = 1.8
    def berm(name, x0, y0, cols, rows, t_of):
        cell = 0.9
        hs = []
        for r in range(rows):
            row = []
            for c in range(cols):
                x, y = x0 + c * cell, y0 + r * cell
                t = max(0.0, min(1.0, t_of(x, y)))
                wob = 0.14 * _mm.sin(1.7 * x + 0.9 * y) * _mm.sin(0.8 * x - 1.3 * y) * 4.0 * t * (1.0 - t)
                row.append(rise * (t * t * (3.0 - 2.0 * t)) + wob)
            hs.append(row)
        make_heightfield(name, (x0, y0, YARD_Z), cell, hs, duff, skirt=0.3)
    berm("Forest_Berm_E", 11.5, -18.5, 6, 40, lambda x, y: (x - 11.5) / 3.5)
    berm("Forest_Berm_W", -16.0, -18.5, 6, 40, lambda x, y: (-11.5 - x) / 3.5)
    berm("Forest_Berm_N", -11.7, 12.5, 27, 5, lambda x, y: (y - 12.5) / 2.5)
    # the S berm parts where the road leaves the clearing (draft 5): a cut
    # through the bank, x -4.5 .. 0.9
    berm("Forest_Berm_S", -11.7, -18.5, 9, 6, lambda x, y: (-14.0 - y) / 3.5)
    berm("Forest_Berm_SE", 0.9, -18.5, 13, 6, lambda x, y: (-14.0 - y) / 3.5)
    # the berms' foot: sword fern and salal where the yard meets the slope
    # (draft 4: the clearing's edge was a clean line where dirt met duff)
    from _props.trees import make_fern
    fern_c, salal_c = (0.22, 0.36, 0.22, 1.0), (0.14, 0.24, 0.15, 1.0)
    trunks = [(-9.0, -3.6), (-10.0, 1.8), (-9.2, 7.0), (8.4, -0.6), (7.2, 3.6), (6.4, 7.4), (3.6, 11.0), (-5.6, 11.6)]
    foot = []
    for i in range(16):
        y = -13.0 + i * 1.6
        foot += [("E", 10.95 + 0.25 * ((i * 7) % 3), y), ("W", -10.95 - 0.25 * ((i * 5) % 3), y)]
    for i in range(14):
        x = -10.2 + i * 1.6
        foot += [("N", x, 11.95 + 0.2 * ((i * 3) % 3))]
        if not -3.8 < x < 0.9:      # the road
            foot += [("S", x, -13.45 - 0.2 * ((i * 7) % 3))]
    k = 0
    for side, fx, fy in foot:
        if any((fx - tx) ** 2 + (fy - ty) ** 2 < 1.4 ** 2 for tx, ty in trunks) or (side == "N" and abs(fy - 11.5) < 0.7 and -5.0 < fx < 5.0):
            continue
        if k % 3 == 2:
            make_blob(f"Edge_Salal_{side}_{k}", (fx, fy, YARD_Z + 0.22), 0.42, salal_c, noise=0.25, seed=k, squash=0.6)
        else:
            make_fern(f"Edge_Fern_{side}_{k}", fx, fy, h=0.62 + 0.08 * (k % 3), fronds=6, col=fern_c, z0=YARD_Z)
        k += 1
    band = (0.10, 0.15, 0.11, 1.0)
    bz, bh = YARD_Z + rise, 14.0 - rise
    make_box("Forest_Band_S", (0.0, -18.0, bz + bh / 2.0), (32.0, 1.0, bh), band)
    make_box("Forest_Band_N", (0.0, 15.5, bz + bh / 2.0), (32.0, 1.0, bh), band)
    for e, nm in ((-1, "W"), (1, "E")):
        make_box(f"Forest_Band_{nm}", (e * 15.5, -1.25, bz + bh / 2.0), (1.0, 32.5, bh), band)


def build_shop_wing_2026_10():
    """OLAF'S SHOP · the west wing (2026-10-08, the user: "The cabin looks
    too small on the outside"). A 6 m box under a shallow roof read as a
    garden shed from the turnaround — for a house that seats seven, sleeps
    a loft and keeps an east room. The roof went steep (the loft's), and
    the cabin grew the wing a man who carved "a little of it every Sunday
    afternoon" for forty-five years would have built onto it: his carving
    shop, 4 m by 5.7 m against the west wall (which has no openings, so
    the room inside is untouched), set back 0.5 m from the porch's wall,
    under its own lower gable. Its window shows the bench under it, dark.
    """
    wall_c = PAL_WALL["wall"]
    shake = (0.30, 0.25, 0.21, 1.0)
    seam = (0.40, 0.29, 0.19, 1.0)
    stone = (0.42, 0.41, 0.38, 1.0)
    X0, X1 = -7.1, -3.1        # outer west face … the cabin's west wall face
    YS, YN = 0.40, 6.10        # outer south face … outer north face
    H = 2.70
    make_wall_with_openings("Shop_Wall_S", ((X0 + X1) / 2.0, YS + 0.10, 0), length=X1 - X0, height=H, axis='X',
                            palette=PAL_WALL, baseboard_face_sign=+1, openings=[(-5.000, 1.450, 1.000, 0.900), (-6.300, 1.000, 0.900, 2.000)])
    make_wall("Shop_Wall_N", ((X0 + X1) / 2.0, YN - 0.10, 0), length=X1 - X0, height=H, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Shop_Wall_W", (X0 + 0.10, (YS + YN) / 2.0, 0), length=YN - YS - 0.40, height=H, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Shop_Floor", ((X0 + 0.2 + X1) / 2.0, (YS + YN) / 2.0, -0.02), (X1 - X0 - 0.2, YN - YS - 0.4, 0.04), COL_FLOOR)
    make_box("Foundation_Shop_S", ((X0 + X1) / 2.0, YS + 0.10, YARD_Z / 2.0), (X1 - X0, 0.20, -YARD_Z), stone)
    make_box("Foundation_Shop_N", ((X0 + X1) / 2.0, YN - 0.10, YARD_Z / 2.0), (X1 - X0, 0.20, -YARD_Z), stone)
    make_box("Foundation_Shop_W", (X0 + 0.10, (YS + YN) / 2.0, YARD_Z / 2.0), (0.20, YN - YS - 0.40, -YARD_Z), stone)
    # the roof: its own gable, ridge E-W, lower than the cabin's eaves meet
    pitch, th, eave = 0.95, 0.18, 0.40
    ridge_y = (YS + YN) / 2.0
    under = lambda y: H + pitch * (y - YS) if y <= ridge_y else H + pitch * (YN - y)
    ridge_z = under(ridge_y)
    L = X1 - X0 + 0.40
    for nm, ya, yb in (("Shop_Roof_S_Eave", YS - eave, YS), ("Shop_Roof_S", YS, ridge_y),
                       ("Shop_Roof_N", ridge_y, YN), ("Shop_Roof_N_Eave", YN, YN + eave)):
        za, zb = under(ya) if ya >= YS else H - pitch * (YS - ya), under(yb) if yb <= YN else H - pitch * (yb - YN)
        _prism_ccw(nm, (X1 - L / 2.0, 0.0, 0.0), [(ya, za), (yb, zb), (yb, zb + th), (ya, za + th)], L, shake)
    make_box("Shop_Roof_Ridge", (X1 - L / 2.0, ridge_y, ridge_z + th + 0.03), (L, 0.26, 0.06), (0.24, 0.20, 0.17, 1.0))
    _prism_ccw("Shop_Gable_W", (X0 + 0.10, 0.0, 0.0), [(YS, H), (YN, H), (ridge_y, ridge_z - 0.02)], 0.20, wall_c)
    for e, nm in ((-1, "S"), (1, "N")):
        make_box(f"Shop_Roof_Frieze_{nm}", ((X0 + X1) / 2.0, (YS - 0.003) if e < 0 else (YN + 0.003), H - 0.05), (X1 - X0, 0.006, 0.10), shake)
    # the window and what is under it: the carving bench, a cedar blank, the gouges
    make_window("Shop_Window", (-5.0, YS + 0.20, 1.45), width=1.00, height=0.90, room_dir=+1, see_through=True)
    make_table("Shop_Bench", -5.0, YS + 0.62, w=1.70, d=0.62, h=0.90, wood=COL_WOOD_DK, top_col=COL_WOOD)
    make_chamfer_box("Shop_Bench_Cedar_Blank", (-5.2, YS + 0.60, 0.96), (0.30, 0.14, 0.12), (0.62, 0.43, 0.26, 1.0), chamfer=0.01)
    for gi in range(4):
        make_box(f"Shop_Bench_Gouge_{gi}", (-4.55 + gi * 0.06, YS + 0.66, 0.9075), (0.025, 0.20, 0.015), COL_IRON)
    # the shop's door (draft 5): board-and-batten in the S wall, a stone
    # step down to the yard, and stepping stones round to the porch steps —
    # the way Olaf walked from the bench to the house
    door_c, bat_c = (0.30, 0.21, 0.14, 1.0), (0.38, 0.27, 0.18, 1.0)
    make_box("Shop_Door", (-6.30, YS + 0.13, 1.00), (0.88, 0.05, 2.00), door_c)
    for ri, rz in enumerate((0.30, 1.70)):
        make_box(f"Shop_Door_Batten_{ri}", (-6.30, YS + 0.093, rz), (0.80, 0.024, 0.13), bat_c)
    make_box("Shop_Door_Head", (-6.30, YS + 0.10, 2.025), (0.90, 0.20, 0.05), wall_c)
    make_cyl("Shop_Door_Latch", (-5.98, YS + 0.075, 1.00), 0.02, 0.04, COL_IRON, axis='Y', segments=8)
    make_box("Shop_Door_Step", (-6.30, YS - 0.22, (YARD_Z - 0.20) / 2.0), (1.00, 0.44, -0.20 - YARD_Z), stone)
    for si, (sx2, sy2) in enumerate(((-6.0, -0.55), (-5.4, -1.05), (-4.7, -1.45), (-3.95, -1.80), (-3.2, -2.15),
                                     (-2.45, -2.40), (-1.65, -2.55), (-0.95, -2.55))):
        make_cyl(f"Shop_Path_Stepping_Stone_{si}", (sx2, sy2, YARD_Z + 0.015), 0.21 + 0.03 * (si % 2), 0.03, stone, segments=9)
    # siding on the wing's two outside faces
    for k in range(1, 12):
        z = k * 0.225
        if z > H - 0.20:
            break
        holes = ([(-5.52, -4.48)] if 0.98 < z < 1.92 else []) + ([(-6.77, -5.83)] if z < 2.02 else [])
        cuts, cur = [], X0
        for a2, b2 in sorted(holes):
            cuts.append((cur, a2)); cur = b2
        cuts.append((cur, X1))
        for ri, (a, b) in enumerate(cuts):
            make_box(f"Shop_Siding_S_{k}_{ri}", ((a + b) / 2.0, YS - 0.003, z), (b - a, 0.006, 0.012), seam)
        make_box(f"Shop_Siding_W_{k}", (X0 - 0.003, (YS + YN) / 2.0, z), (0.006, YN - YS, 0.012), seam)


def build_porch_2026_10():
    """TEM'S PORCH (2026-10-08) — "the small porch", from the prose:

    - "He came up the porch steps" · "The figure walked down the porch
      steps": the deck stands 0.40 over the yard, one step between.
    - "She set the coffee on the porch railing" (ch5): her mug on the
      rail cap.
    - "a piece of cedar, the size of his thumb ... on the porch rail"
      (ch13): Eddvard's hand, palm-up, the fingers slightly curled.
    - "the small tin Tem kept on the porch for the people who smoked"
      (ch13): on the rail at the east end, a butt in it.
    - "The crow was on the porch railing" (ch15): on the west rail.
    - "The light from the cabin's south window threw a square of yellow
      onto the porch boards": the deck runs under both south windows.
    - "Per's old Buick at an angle on the porch side" · "the small
      gravel turnaround in front of the cabin's porch".
    Plus what a porch in a wet forest holds: the bench under the west
    window, one chair, boots by the door, the firewood under the east
    window out of the rain, a rain barrel at the corner, the chopping
    block in the yard. No porch lamp — there are no wires up here.

    The deck runs between the side walls' ends (x ±2.90), from the
    south wall's face to y -1.92; the shed roof hangs off a ledger on
    the wall and lands on a beam on four posts.
    """
    deck_col = (0.46, 0.35, 0.24, 1.0)
    deck_seam = (0.28, 0.20, 0.13, 1.0)
    rail_col = (0.40, 0.30, 0.20, 1.0)
    X0, X1 = -2.90, 2.90
    Y0, Y1 = -0.10, -1.92
    make_box("Porch_Deck", (0.0, (Y0 + Y1) / 2.0, -0.02), (X1 - X0, Y0 - Y1, 0.04), deck_col)
    n = int((X1 - X0) / 0.14)
    for i in range(1, n):
        x = X0 + i * (X1 - X0) / n
        make_box(f"Porch_Deck_Seam_{i}", (x, (Y0 + Y1) / 2.0, 0.0015), (0.006, Y0 - Y1 - 0.02, 0.003), deck_seam)
    # the rim and the skirt down to the yard
    make_box("Porch_Skirt_S", (0.0, Y1 + 0.02, (YARD_Z - 0.04) / 2.0), (X1 - X0, 0.04, -0.04 - YARD_Z), COL_WOOD_DK)
    for e, nm in ((-1, "W"), (1, "E")):
        make_box(f"Porch_Skirt_{nm}", (e * (X1 - 0.02), (Y0 + Y1 + 0.04) / 2.0, (YARD_Z - 0.04) / 2.0),
                 (0.04, Y0 - Y1 - 0.04, -0.04 - YARD_Z), COL_WOOD_DK)
    # the step, centred on the door
    make_box("Porch_Step_0", (0.0, Y1 - 0.16, (YARD_Z - 0.20) / 2.0), (1.24, 0.32, -0.20 - YARD_Z), deck_col)
    make_box("Porch_Step_0_Nosing", (0.0, Y1 - 0.315, -0.215), (1.24, 0.03, 0.03), COL_WOOD_DK)
    # posts, the beam on them, the ledger on the wall, the shed roof between
    PY = -1.80
    post_xs = (-2.80, -0.70, 0.70, 2.80)
    beam_top = 2.66
    for pi, px in enumerate(post_xs):
        make_box(f"Porch_Post_{pi}", (px, PY, (beam_top - 0.16) / 2.0), (0.12, 0.12, beam_top - 0.16), rail_col)
    make_box("Porch_Beam", (0.0, PY, beam_top - 0.08), (X1 - X0, 0.14, 0.16), rail_col)
    make_box("Porch_Ledger", (0.0, Y0 - 0.03, 2.86), (X1 - X0, 0.06, 0.14), rail_col)
    r_wall, r_beam = 2.94, beam_top
    slope = (r_wall - r_beam) / (Y0 - 0.06 - PY)
    _prism_ccw("Porch_Roof", (0.0, 0.0, 0.0),
               [(Y0 - 0.06, r_wall), (Y1 - 0.14, r_beam - slope * (PY - Y1 + 0.14)),
                (Y1 - 0.14, r_beam - slope * (PY - Y1 + 0.14) + 0.08), (Y0 - 0.06, r_wall + 0.08)],
               X1 - X0 - 0.02, (0.34, 0.28, 0.23, 1.0))
    make_box("Porch_Roof_Fascia", (0.0, Y1 - 0.15, r_beam - slope * (PY - Y1 + 0.14) - 0.02), (X1 - X0 - 0.02, 0.02, 0.14), rail_col)
    # railings: the south run in two halves (the steps between the middle
    # posts), the west and east runs from the wall to the corner posts.
    # A wide flat cap — the coffee, the tin and the cedar sit on it.
    CAP = 0.94
    def run(tag, a, b, fixed, axis):
        L, mid = b - a, (a + b) / 2.0
        if axis == 'X':
            make_chamfer_box(f"{tag}_Cap", (mid, fixed, CAP - 0.02), (L, 0.12, 0.04), rail_col, chamfer=0.008)
            make_box(f"{tag}_Bottom", (mid, fixed, 0.12), (L, 0.06, 0.05), rail_col)
        else:
            make_chamfer_box(f"{tag}_Cap", (fixed, mid, CAP - 0.02), (0.12, L, 0.04), rail_col, chamfer=0.008)
            make_box(f"{tag}_Bottom", (fixed, mid, 0.12), (0.06, L, 0.05), rail_col)
        k = max(1, int(L / 0.14))
        for i in range(k):
            t = a + (i + 0.5) * L / k
            make_box(f"{tag}_Bal_{i}", (t, fixed, (0.145 + CAP - 0.04) / 2.0) if axis == 'X' else (fixed, t, (0.145 + CAP - 0.04) / 2.0),
                     (0.04, 0.04, CAP - 0.04 - 0.145), rail_col)
    run("Porch_Rail_SW", post_xs[0] + 0.06, post_xs[1] - 0.06, PY, 'X')
    run("Porch_Rail_SE", post_xs[2] + 0.06, post_xs[3] - 0.06, PY, 'X')
    run("Porch_Rail_W", PY + 0.06, Y0 - 0.01, post_xs[0], 'Y')
    run("Porch_Rail_E", PY + 0.06, Y0 - 0.01, post_xs[3], 'Y')
    # ── the rail's three things ──
    cedar = (0.62, 0.43, 0.26, 1.0)
    cedar_wet = (0.48, 0.32, 0.20, 1.0)
    # Eddvard's hand: "a piece of cedar, the size of his thumb, not
    # recently placed by the wet color of it" — palm-up, fingers curled
    hx, hy = -1.30, PY
    make_chamfer_box("Porch_Cedar_Hand", (hx, hy, CAP + 0.0125), (0.075, 0.040, 0.025), cedar_wet, chamfer=0.006)
    make_cyl("Porch_Cedar_Hand_Palm", (hx + 0.008, hy, CAP + 0.0255), 0.014, 0.002, cedar, segments=8)
    for fi in range(4):
        make_box(f"Porch_Cedar_Hand_Finger_{fi}", (hx - 0.024, hy - 0.012 + fi * 0.008, CAP + 0.027), (0.018, 0.005, 0.004), cedar)
    # her coffee, set on the railing when she saw it was Finn's truck
    mx, my = 1.25, PY
    make_lathe("Porch_Coffee_Mug", (mx, my, CAP),
               [(0.038, 0.0), (0.042, 0.006), (0.044, 0.09), (0.046, 0.10), (0.040, 0.10), (0.0, 0.095)],
               (0.82, 0.78, 0.70, 1.0), segments=12)
    make_cyl("Porch_Coffee_Mug_Coffee", (mx, my, CAP + 0.088), 0.038, 0.004, (0.22, 0.14, 0.09, 1.0), segments=12)
    make_tube("Porch_Coffee_Mug_Handle", [(mx + 0.044, my, CAP + 0.075), (mx + 0.070, my, CAP + 0.068),
                                          (mx + 0.072, my, CAP + 0.035), (mx + 0.044, my, CAP + 0.028)],
              0.007, (0.82, 0.78, 0.70, 1.0), segments=5)
    # the smokers' tin, at the east end of the rail, a butt in it
    tx, ty = 2.45, PY
    make_lathe("Porch_Cigarette_Tin", (tx, ty, CAP),
               [(0.045, 0.0), (0.048, 0.004), (0.048, 0.028), (0.044, 0.028), (0.044, 0.006), (0.0, 0.006)],
               (0.56, 0.58, 0.58, 1.0), segments=12)
    make_cyl("Porch_Cigarette_Ash", (tx, ty, CAP + 0.008), 0.040, 0.004, (0.36, 0.35, 0.33, 1.0), segments=10)
    make_cyl("Porch_Cigarette_Butt", (tx + 0.005, ty + 0.01, CAP + 0.016), 0.0045, 0.030, (0.90, 0.86, 0.76, 1.0), axis='X', segments=6)
    make_cyl("Porch_Cigarette_Butt_Filter", (tx - 0.014, ty + 0.01, CAP + 0.016), 0.0046, 0.010, (0.80, 0.56, 0.32, 1.0), axis='X', segments=6)
    # the crow, on the west rail
    from _props.creatures import make_crow
    make_crow("Porch_Crow", post_xs[0], -1.05, CAP, facing=1.0)
    # ── against the wall ──
    # the bench under the west window
    bx = -2.00
    make_chamfer_box("Porch_Bench_Seat", (bx, -0.42, 0.45), (1.40, 0.40, 0.05), rail_col, chamfer=0.01)
    make_box("Porch_Bench_Back", (bx, -0.245, 0.675), (1.40, 0.05, 0.40), rail_col)   # on the seat's back edge
    for li, (lx, ly) in enumerate(((bx - 0.62, -0.60), (bx + 0.62, -0.60), (bx - 0.62, -0.26), (bx + 0.62, -0.26))):
        make_box(f"Porch_Bench_Leg_{li}", (lx, ly, 0.2125), (0.05, 0.05, 0.425), rail_col)
    # a folded wool blanket on the bench's end (the cedar chest's blankets go everywhere)
    make_chamfer_box("Porch_Bench_Blanket", (bx - 0.45, -0.44, 0.50), (0.36, 0.30, 0.05), COL_WOOL, chamfer=0.012)
    # one kit chair east of the door, facing the yard
    make_chair("Porch_Chair", 1.30, -0.70, yaw=3.1416, wood=rail_col, w=0.44)
    # boots by the door, out of the swing
    for bi, bxx in enumerate((-1.12, -0.97)):
        make_chamfer_box(f"Porch_Boot_{bi}_Foot", (bxx, -0.34, 0.04), (0.10, 0.26, 0.08), (0.16, 0.18, 0.15, 1.0), chamfer=0.02)
        make_cyl(f"Porch_Boot_{bi}_Shaft", (bxx, -0.27, 0.23), 0.055, 0.30, (0.16, 0.18, 0.15, 1.0), segments=10)
    make_box("Porch_Doormat", (0.0, -0.40, 0.006), (0.85, 0.50, 0.012), (0.36, 0.30, 0.22, 1.0))
    # the firewood under the east window, out of the rain
    for r in range(3):
        for c in range(3):
            make_cyl(f"Porch_Firewood_{r}_{c}", (2.42, -0.24 - c * 0.155, 0.075 + r * 0.14),
                     0.072, 0.56, COL_WOOD if (r + c) % 2 else COL_WOOD_DK, segments=7, axis='X')
    # ── off the porch ──
    # the rain barrel at the west corner, under the eave's drip line
    make_lathe("Rain_Barrel", (-3.62, -0.62, YARD_Z),
               [(0.27, 0.0), (0.30, 0.04), (0.32, 0.42), (0.30, 0.82), (0.28, 0.86), (0.0, 0.85)],
               (0.30, 0.34, 0.30, 1.0), segments=14)
    make_cyl("Rain_Barrel_Water", (-3.62, -0.62, YARD_Z + 0.845), 0.27, 0.006, (0.20, 0.24, 0.24, 1.0), segments=14)
    for hi, hz in enumerate((0.16, 0.68)):
        make_cyl(f"Rain_Barrel_Hoop_{hi}", (-3.62, -0.62, YARD_Z + hz), 0.315, 0.03, COL_IRON, segments=14)
    # the chopping block in the yard, the axe laid across it
    cbx, cby = 4.6, -1.2
    make_lathe("Chopping_Block", (cbx, cby, YARD_Z),
               [(0.28, 0.0), (0.26, 0.04), (0.25, 0.44), (0.0, 0.44)], (0.50, 0.40, 0.28, 1.0), segments=12)
    make_cyl("Chopping_Block_Rings", (cbx, cby, YARD_Z + 0.441), 0.18, 0.002, (0.62, 0.50, 0.34, 1.0), segments=12)
    make_box("Chopping_Block_Axe_Handle", (cbx + 0.12, cby, YARD_Z + 0.457), (0.62, 0.035, 0.03), (0.66, 0.52, 0.32, 1.0))
    make_box("Chopping_Block_Axe_Head", (cbx - 0.16, cby, YARD_Z + 0.462), (0.06, 0.16, 0.04), COL_IRON)
    for ci, (sx2, sy2, syaw) in enumerate(((4.2, -1.55, 0.3), (4.95, -0.85, 1.4), (4.4, -0.70, 2.2))):
        make_rot_box(f"Chopping_Block_Split_{ci}", (sx2, sy2, YARD_Z + 0.05), (0.36, 0.10, 0.10), COL_WOOD, yaw=syaw)


def main():
    clear_scene()
    build_shell()
    build_kitchen()
    build_loft()
    build_stove_corner()
    build_table()
    build_daybed()
    build_east_room()
    build_wall_dressing()
    build_crow_2026_08()
    build_wear_personality_2026_08()
    build_through_windows_2026_08()
    build_hero_props_2026_09()
    build_kerosene_infra_2026_09()
    build_exterior_2026_10()
    build_shop_wing_2026_10()
    build_porch_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cabin_interior.glb"))
    build_door_infill_front_door_2026_09()
    print(f"\n[build_cabin_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
