"""estuary_7_template — the planner's-view of Estuary 7 as a tabletop
diorama in a dark room. vol7's epilogue (The Gallery, The Submission),
re-homed off cabin_road (2026-09-03).

"Estuary 7 opened at the planner's-view the way it had always opened.
The coastal template from above. The river coming down from the
cedars to the east. The bar of sand at the mouth. The flats north of
the river. The bluff south of it. The forested ridge behind the
bluff. The drone-palette docked at the right of the view. The
labor-crew palette docked below the drones. The construction
primitives docked below the labor crews. The clock at the upper-right
showing zero." Then the gallery renders the saved builds over it —
Dean's tower on the bluff and Smolvud below it; Olaf's cabin as a
hub with four substrate-lines to Marit's house, Eddvard's mill,
Lindholm's office in Eugene (off the south-east frame), Olaus's cove
south of Bandon (off the south frame); Eddvard's mill; Marit's grove;
Aud's diner; Brandon's pools. And in The Submission, Tem places one
drone at the cabin.

We can't render a substrate. We can build the substrate's picture of
the coast as an object: a museum diorama, twelve meters of coast on
a plinth, the palettes as docked slabs at its right edge, the clock
as a panel. The gallery's layers are all present at once — the tower,
the town, the cabin and its lines, the mill, the grove, the diner,
the pools, the drone — because by the end of the epilogue they are.

Coordinate frame: Blender Z-up. The plinth is 14 x 9.6 at the origin,
top at z 0.30; the land plate (x -3.2..6) and the sea (x -6..-3.2)
sit on it to z 0.36. North is +y. glTF export remaps to Godot
(x, z, -y). The camera preset hangs high over the south-west corner.

DRAFT 1 (2026-09-03): plinth + title strip; sea, land, the river in
four reaches, the sand bar, the flats, the bluff with Dean's seven-
floor tower + roof garden, Smolvud's blocks with Marit's house, the
road with Aud's diner, the cabin with the drone hovering on its beam,
the four substrate-lines as circuit traces, the mill with its water
wheel on the bend, the grove, the basalt headland with the pools, the
ridge; the three palettes and the two clocks; a void floor.
DRAFT 2 (2026-09-03): the gallery's layers as four glass sheets over
the table with name tabs, labels on the off-frame glyphs, the cursor
at the template center. Draft 3 targets: a tight preset on the cabin
hub, wake lines on the sea, the drone-palette's greyed-out state as
a second variant.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_gable, export_glb

PLINTH = (0.12, 0.11, 0.11, 1.0)
PLINTH_EDGE = (0.20, 0.18, 0.17, 1.0)
BRASS = (0.72, 0.60, 0.32, 1.0)
LAND = (0.36, 0.42, 0.28, 1.0)
LAND_DK = (0.28, 0.34, 0.22, 1.0)
SEA = (0.16, 0.30, 0.42, 1.0)
SEA_LT = (0.26, 0.42, 0.52, 1.0)
RIVER = (0.22, 0.38, 0.46, 1.0)
SAND = (0.78, 0.72, 0.54, 1.0)
FLATS = (0.62, 0.60, 0.46, 1.0)
BLUFF = (0.44, 0.40, 0.32, 1.0)
BASALT = (0.22, 0.22, 0.24, 1.0)
CEDAR = (0.18, 0.30, 0.20, 1.0)
CEDAR_LT = (0.26, 0.38, 0.24, 1.0)
GLASS = (0.62, 0.74, 0.80, 1.0)
GLASS_DK = (0.46, 0.58, 0.64, 1.0)
ROOF = (0.40, 0.32, 0.26, 1.0)
WALL = (0.70, 0.64, 0.54, 1.0)
ROAD = (0.30, 0.30, 0.32, 1.0)
TRACE = (0.62, 0.86, 0.96, 1.0)
PALETTE = (0.10, 0.12, 0.16, 1.0)
PALETTE_GLYPH = (0.62, 0.86, 0.96, 1.0)
PALETTE_GREY = (0.30, 0.32, 0.36, 1.0)
DRONE = (0.86, 0.90, 0.94, 1.0)

Z_TOP = 0.36      # land / sea surface
Z_DECAL = 0.362   # thin surface markings
Z_TRACE = 0.3675  # substrate-lines float above the decals


def build_plinth():
    make_box("Void_Floor", (0.0, 0.0, -2.0), (700.0, 700.0, 0.02), (0.03, 0.03, 0.035, 1.0))
    make_box("Plinth", (0.0, 0.0, 0.15), (14.0, 9.6, 0.30), PLINTH)
    make_box("Plinth_Edge_S", (0.0, -4.78, 0.305), (14.0, 0.04, 0.01), PLINTH_EDGE)
    make_box("Plinth_Edge_N", (0.0, 4.78, 0.305), (14.0, 0.04, 0.01), PLINTH_EDGE)
    make_box("Plinth_Edge_W", (-6.98, 0.0, 0.305), (0.04, 9.52, 0.01), PLINTH_EDGE)
    make_box("Plinth_Edge_E", (6.98, 0.0, 0.305), (0.04, 9.52, 0.01), PLINTH_EDGE)
    # title strip on the south face: ESTUARY 7 · I. ROCHA · 2046
    make_box("Title_Plate", (0.0, -4.81, 0.16), (1.60, 0.02, 0.16), BRASS)
    for i, w in enumerate((0.36, 0.08, 0.22, 0.30, 0.10, 0.26)):
        x = -0.66 + sum((0.36, 0.08, 0.22, 0.30, 0.10, 0.26)[:i]) + i * 0.05 + w / 2.0
        make_box(f"Title_Word_{i}", (x, -4.822, 0.16), (w, 0.002, 0.05), (0.18, 0.15, 0.10, 1.0))
    # the four legs of the table, so it reads as furniture in a room
    for li, (lx, ly) in enumerate(((-6.4, -4.2), (6.4, -4.2), (-6.4, 4.2), (6.4, 4.2))):
        make_box(f"Table_Leg_{li}", (lx, ly, -0.85), (0.16, 0.16, 1.70), PLINTH_EDGE)


def build_coast():
    # sea west, land east; the surfaces are level so the camera reads a map
    make_box("Template_Sea", (-4.6, 0.0, 0.33), (2.8, 9.0, 0.06), SEA)
    make_box("Template_Land", (1.4, 0.0, 0.33), (9.2, 9.0, 0.06), LAND)
    # swell lines on the sea
    for i in range(6):
        make_box(f"Sea_Swell_{i}", (-4.6 + (i % 2) * 0.3, -3.6 + i * 1.4, Z_DECAL), (1.6, 0.03, 0.004), SEA_LT)
    # the river in four reaches, cedars to mouth, each reach a step north of the last
    reaches = ((4.60, 0.80, 2.78, 0.30), (1.80, 0.50, 2.78, 0.32), (-0.70, 0.20, 2.18, 0.34), (-2.50, 0.00, 1.38, 0.36))
    for i, (x, y, w, d) in enumerate(reaches):
        make_box(f"River_Reach_{i}", (x, y, Z_DECAL), (w, d, 0.004), RIVER)
    make_box("River_Mouth", (-3.35, -0.05, Z_DECAL), (0.30, 0.50, 0.004), RIVER)
    # the bar of sand at the mouth, the flats north of the river
    make_box("Sand_Bar", (-3.55, -0.55, Z_DECAL + 0.004), (0.50, 1.00, 0.008), SAND)
    make_box("Sand_Bar_Tip", (-3.75, 0.20, Z_DECAL + 0.004), (0.30, 0.24, 0.008), SAND)
    make_box("Flats", (-0.60, 2.00, Z_DECAL + 0.003), (4.20, 2.40, 0.006), FLATS)
    for i in range(5):
        make_box(f"Flats_Channel_{i}", (-2.4 + i * 0.9, 2.0 + (i % 2) * 0.5, Z_DECAL + 0.0065), (0.03, 1.4, 0.002), RIVER)
    # the cedars the river comes down from: a stand along the east edge
    for i, (x, y, r, s) in enumerate(((5.4, 1.6, 0.30, 1), (5.7, 2.4, 0.26, 2), (5.2, 3.2, 0.32, 3), (5.8, 3.9, 0.24, 4),
                                      (5.5, -0.2, 0.28, 5), (5.8, -1.0, 0.26, 6), (5.3, -1.9, 0.30, 7), (5.7, -2.7, 0.24, 8))):
        make_cyl(f"Cedar_{i}_Trunk", (x, y, Z_TOP + 0.08), 0.02, 0.16, (0.30, 0.24, 0.18, 1.0), segments=6)
        make_blob(f"Cedar_{i}_Crown", (x, y, Z_TOP + 0.16 + r * 0.9), r, CEDAR if i % 2 else CEDAR_LT, noise=0.22, seed=s, squash=0.9)


def build_bluff_and_tower():
    """The bluff south of the river; Dean's tower at old-Yachats on its
    south-west: "seventy feet on a side ... seven floor-levels.
    Smart-glass and cedar, seven floors, an indoor garden at the
    seventh-floor roof level, a portal-room marked on the fourth
    floor." The ridge behind."""
    make_box("Bluff", (-1.5, -1.6, 0.535), (3.0, 1.6, 0.35), BLUFF)
    make_box("Bluff_Top_Grass", (-1.5, -1.6, 0.713), (2.9, 1.5, 0.006), LAND_DK)
    make_box("Bluff_Face_Band", (-1.5, -0.81, 0.62), (3.0, 0.02, 0.10), (0.36, 0.32, 0.26, 1.0))
    tx, ty = -2.3, -1.7
    for fl in range(7):
        z = 0.716 + 0.15 * fl + 0.075
        col = GLASS if fl % 2 == 0 else GLASS_DK
        if fl == 3:
            col = (0.70, 0.62, 0.48, 1.0)   # the portal-room floor marked in cedar
        make_box(f"Tower_Floor_{fl}", (tx, ty, z), (0.42, 0.42, 0.15), col)
    make_box("Tower_Garden", (tx, ty, 0.716 + 1.05 + 0.03), (0.34, 0.34, 0.06), CEDAR_LT)
    make_box("Tower_Garden_Rail", (tx, ty, 0.716 + 1.05 + 0.065), (0.42, 0.42, 0.01), (0.60, 0.62, 0.64, 1.0))
    # ridge behind the bluff: a long gable with a darker crown line
    make_gable("Ridge", (1.4, -3.9, 0.66), (9.2, 1.2, 0.6), CEDAR, ridge_axis="X")


def build_town_and_road():
    """Smolvud below the bluff: Hemlock and Main, the bakery, ChillWave,
    the Salty Tome, the Daily Grind, the co-op, the laundromat, the
    apartments on Cedar Place. Marit's house on Pine and Cedar. The
    road east with the Missing Link at the roadside."""
    blocks = (("Smolvud_Block_Bakery", -1.50, -0.55, 0.20, 0.16, 0.08), ("Smolvud_Block_ChillWave", -1.18, -0.55, 0.18, 0.16, 0.07),
              ("Smolvud_Block_SaltyTome", -1.50, -0.28, 0.20, 0.14, 0.06), ("Smolvud_Block_DailyGrind", -1.18, -0.28, 0.18, 0.14, 0.07),
              ("Smolvud_Block_Coop", -0.42, -0.55, 0.22, 0.16, 0.09), ("Smolvud_Block_Laundromat", -0.10, -0.55, 0.18, 0.16, 0.06),
              ("Smolvud_Block_CedarPlace", -0.42, -0.28, 0.22, 0.14, 0.10), ("Smolvud_Block_Church", -0.10, -0.28, 0.18, 0.14, 0.12))
    for name, x, y, w, d, h in blocks:
        make_box(name, (x, y, Z_TOP + h / 2.0), (w, d, h), WALL)
        make_box(name + "_Roof", (x, y, Z_TOP + h + 0.01), (w + 0.02, d + 0.02, 0.02), ROOF)
    make_box("Main_Street", (-0.80, -0.415, Z_DECAL), (1.70, 0.05, 0.004), ROAD)
    make_box("Hemlock_Street", (-0.80, -0.30, Z_DECAL), (0.05, 0.60, 0.004), ROAD)
    # Marit's house on the corner of Pine and Cedar (the first of Olaf's four points)
    make_box("Marit_House", (-0.80, -0.62, Z_TOP + 0.05), (0.14, 0.14, 0.10), (0.78, 0.70, 0.58, 1.0))
    make_gable("Marit_House_Roof", (-0.80, -0.62, Z_TOP + 0.10 + 0.03), (0.16, 0.16, 0.06), ROOF, ridge_axis="X")
    # the road east out of town, the diner at the roadside
    make_box("Coast_Road", (2.55, -0.35, Z_DECAL), (4.90, 0.06, 0.004), ROAD)
    make_box("Diner", (1.60, -0.56, Z_TOP + 0.04), (0.30, 0.16, 0.08), (0.84, 0.80, 0.70, 1.0))
    make_box("Diner_Roof", (1.60, -0.56, Z_TOP + 0.09), (0.32, 0.18, 0.02), (0.60, 0.22, 0.20, 1.0))
    make_box("Diner_Sign_Post", (1.40, -0.44, Z_TOP + 0.08), (0.01, 0.01, 0.16), (0.40, 0.40, 0.42, 1.0))
    make_box("Diner_Sign", (1.40, -0.44, Z_TOP + 0.185), (0.08, 0.01, 0.05), (0.92, 0.80, 0.40, 1.0))
    make_box("Diner_Lot", (1.60, -0.42, Z_DECAL + 0.0001), (0.40, 0.08, 0.002), (0.42, 0.42, 0.44, 1.0))


def build_cabin_and_network():
    """Olaf's cabin as the hub — the bowl-network as architecture. Four
    substrate-lines, laid as circuit traces: west to Marit's house,
    east to Eddvard's mill, south-east off the frame to Eugene, south
    to the ridge toward Bandon. Tem's one drone hovers at the cabin."""
    cx, cy = 2.20, 0.15
    make_box("Cabin", (cx, cy, Z_TOP + 0.06), (0.24, 0.20, 0.12), (0.46, 0.36, 0.26, 1.0))
    make_gable("Cabin_Roof", (cx, cy, Z_TOP + 0.12 + 0.04), (0.28, 0.24, 0.08), ROOF, ridge_axis="X")
    # through the roof (2026-09-23: 4 cm over it)
    make_cyl("Cabin_Chimney", (cx + 0.08, cy, Z_TOP + 0.20), 0.012, 0.08, (0.32, 0.30, 0.28, 1.0), segments=6)
    make_box("Cabin_Clearing", (cx, cy, Z_DECAL + 0.0001), (0.44, 0.40, 0.002), LAND_DK)
    # Marit: west along y=cy to x=-0.80, then south to her house
    make_box("Substrate_Line_Marit", ((cx - 0.12 + -0.80) / 2.0, cy, Z_TRACE), (cx - 0.12 + 0.80, 0.02, 0.003), TRACE)
    make_box("Substrate_Line_Marit_Drop", (-0.80, (cy + -0.55) / 2.0, Z_TRACE), (0.02, cy + 0.55, 0.003), TRACE)
    # Mill: east along y=cy to x=3.60, then north to the mill
    make_box("Substrate_Line_Mill", ((cx + 0.12 + 3.60) / 2.0, cy, Z_TRACE), (3.60 - cx - 0.12, 0.02, 0.003), TRACE)
    make_box("Substrate_Line_Mill_Rise", (3.60, (cy + 0.45) / 2.0, Z_TRACE), (0.02, 0.45 - cy, 0.003), TRACE)
    # Eugene: south along x=2.40 to y=-1.0, then east to the frame edge
    make_box("Substrate_Line_Eugene_Drop", (2.40, (cy - 0.10 + -1.0) / 2.0, Z_TRACE), (0.02, cy - 0.10 + 1.0, 0.003), TRACE)
    make_box("Substrate_Line_Eugene", ((2.40 + 6.0) / 2.0, -1.0, Z_TRACE), (6.0 - 2.40, 0.02, 0.003), TRACE)
    make_box("Foundation_Glyph", (5.94, -1.0, Z_TRACE + 0.02), (0.06, 0.06, 0.04), TRACE)
    # Bandon: south along x=2.00 to the foot of the ridge
    make_box("Substrate_Line_Bandon", (2.00, (cy - 0.10 + -3.28) / 2.0, Z_TRACE), (0.02, cy - 0.10 + 3.28, 0.003), TRACE)
    make_box("Cove_Glyph", (2.00, -3.25, Z_TRACE + 0.02), (0.06, 0.06, 0.04), TRACE)
    # the one drone-unit, rendered in the planner's-view, held at the cabin position
    make_cyl("Drone_Beam", (cx, cy, Z_TOP + 0.20 + 0.0625), 0.006, 0.125, (0.72, 0.92, 1.0, 0.6), segments=6)
    make_box("Drone_Unit_Body", (cx, cy, Z_TOP + 0.325 + 0.015), (0.10, 0.10, 0.03), DRONE)
    for ri, (dx, dy) in enumerate(((-0.08, -0.08), (0.08, -0.08), (-0.08, 0.08), (0.08, 0.08))):
        make_cyl(f"Drone_Unit_Rotor_{ri}", (cx + dx, cy + dy, Z_TOP + 0.325 + 0.025), 0.03, 0.004, (0.70, 0.74, 0.78, 1.0), segments=8)
        make_cyl(f"Drone_Unit_Arm_{ri}", (cx + dx * 0.72, cy + dy * 0.72, Z_TOP + 0.325 + 0.015), 0.006, 0.02,
                 (0.50, 0.54, 0.58, 1.0), axis="Z", segments=6)


def build_mill_and_grove():
    """Eddvard's small mill on the river just upstream of the cabin,
    the water wheel on the bend; Marit's cedar grove east of Smolvud."""
    mx, my = 3.60, 0.52
    make_box("Mill", (mx, my, Z_TOP + 0.05), (0.16, 0.14, 0.10), (0.56, 0.44, 0.32, 1.0))
    make_gable("Mill_Roof", (mx, my, Z_TOP + 0.10 + 0.03), (0.18, 0.16, 0.06), ROOF, ridge_axis="Y")
    make_cyl("Mill_Water_Wheel", (mx + 0.11, my + 0.06, Z_TOP + 0.10), 0.09, 0.02, (0.44, 0.34, 0.24, 1.0), axis="X", segments=12)
    make_cyl("Mill_Wheel_Hub", (mx + 0.11, my + 0.06, Z_TOP + 0.10), 0.02, 0.026, (0.30, 0.24, 0.18, 1.0), axis="X", segments=8)
    make_box("Mill_Race", (mx + 0.11, my + 0.06, Z_DECAL + 0.0001), (0.06, 0.20, 0.002), RIVER)
    # the grove: fifty-one years old and still growing
    for i, (x, y, r, s) in enumerate(((0.45, -0.95, 0.055, 11), (0.65, -0.80, 0.06, 12), (0.85, -0.98, 0.05, 13),
                                      (1.05, -0.82, 0.058, 14), (0.55, -1.15, 0.05, 15), (0.80, -1.18, 0.06, 16),
                                      (1.02, -1.05, 0.048, 17), (0.68, -1.00, 0.04, 18))):
        make_cyl(f"Grove_{i}_Trunk", (x, y, Z_TOP + 0.03), 0.008, 0.06, (0.30, 0.24, 0.18, 1.0), segments=5)
        make_blob(f"Grove_{i}_Crown", (x, y, Z_TOP + 0.06 + r * 0.9), r, CEDAR if i % 2 else CEDAR_LT, noise=0.2, seed=s, squash=0.9)
    make_box("Grove_Floor", (0.75, -1.00, Z_DECAL + 0.0001), (0.80, 0.56, 0.002), LAND_DK)


def build_headland_and_pools():
    """Brandon's Tideline Survey: the pools on the basalt headland at
    the north-west, where the sea meets the flats."""
    hx, hy = -3.6, 3.5
    make_box("Headland", (hx, hy, Z_TOP + 0.05), (0.80, 0.90, 0.10), BASALT)
    make_box("Headland_Step", (hx - 0.55, hy - 0.10, Z_TOP + 0.02), (0.30, 0.60, 0.04), BASALT)
    make_box("Tide_Pool_0", (hx - 0.10, hy - 0.10, Z_TOP + 0.103), (0.26, 0.20, 0.006), SEA_LT)
    make_box("Tide_Pool_1", (hx + 0.22, hy + 0.22, Z_TOP + 0.103), (0.14, 0.12, 0.006), SEA_LT)
    make_box("Tide_Pool_2", (hx - 0.24, hy + 0.28, Z_TOP + 0.103), (0.10, 0.10, 0.006), SEA_LT)
    for i, (dx, dy) in enumerate(((-0.14, -0.14), (-0.02, -0.06), (0.26, 0.24), (-0.26, 0.30))):
        make_cyl(f"Pool_Anemone_{i}", (hx + dx, hy + dy, Z_TOP + 0.108), 0.012, 0.004, (0.72, 0.36, 0.42, 1.0), segments=6)
    for i in range(4):
        make_box(f"Survey_Stake_{i}", (hx - 0.36 + i * 0.24, hy + 0.42, Z_TOP + 0.13), (0.008, 0.008, 0.06), (0.90, 0.60, 0.20, 1.0))


def build_palettes_and_clocks():
    """Docked at the right of the view: drones, labor crews,
    construction primitives; the clock at the upper-right showing
    zero; the second clock at the upper-left that counts up."""
    px = 6.5
    for name, y, glyph in (("Drone_Palette", 2.3, "drone"), ("Crew_Palette", 0.3, "crew"), ("Primitive_Palette", -1.7, "prim")):
        make_box(name, (px, y, 0.31), (0.80, 1.70, 0.02), PALETTE)
        make_box(name + "_Frame", (px, y + 0.86, 0.315), (0.80, 0.02, 0.03), PALETTE_GLYPH)
        for gi in range(4):
            gy = y + 0.62 - gi * 0.42
            if glyph == "drone":
                # (pass 474) "The drone-palette docked at the right of the view"
                # (epilogue_gallery n8): its icons were plain squares. Each a
                # small quadcopter — the body, four arms, four rotor discs.
                gcol = PALETTE_GREY if gi else DRONE
                make_box(f"{name}_Glyph_{gi}", (px, gy, 0.333), (0.06, 0.06, 0.026), gcol)
                make_box(f"{name}_Glyph_{gi}_Arm_X", (px, gy, 0.336), (0.13, 0.012, 0.008), gcol)
                make_box(f"{name}_Glyph_{gi}_Arm_Y", (px, gy, 0.336), (0.012, 0.13, 0.008), gcol)
                for ri, (rdx, rdy) in enumerate(((-0.065, 0.0), (0.065, 0.0), (0.0, -0.065), (0.0, 0.065))):
                    make_cyl(f"{name}_Glyph_{gi}_Rotor_{ri}", (px + rdx, gy + rdy, 0.343), 0.032, 0.006, gcol, segments=10)
            elif glyph == "crew":
                make_cyl(f"{name}_Glyph_{gi}", (px, gy, 0.35), 0.03, 0.06, PALETTE_GREY, segments=8)
                make_cyl(f"{name}_Glyph_{gi}_Head", (px, gy, 0.395), 0.02, 0.03, PALETTE_GREY, segments=8)
            else:
                make_box(f"{name}_Glyph_{gi}", (px, gy, 0.345), (0.10, 0.10, 0.05), PALETTE_GREY)
    make_box("Gallery_Clock", (px, 3.95, 0.31), (0.80, 0.42, 0.02), PALETTE)
    make_box("Gallery_Clock_Face", (px, 3.95, 0.325), (0.60, 0.20, 0.01), (0.04, 0.05, 0.07, 1.0))
    for i, dx in enumerate((-0.20, -0.08, 0.08, 0.20)):
        make_box(f"Gallery_Clock_Digit_{i}", (px + dx, 3.95, 0.3325), (0.06, 0.10, 0.005), PALETTE_GLYPH)
    make_box("Gallery_Clock_Colon", (px, 3.95, 0.3325), (0.012, 0.012, 0.005), PALETTE_GLYPH)
    # the second clock, upper-left, that counted up — off the sea's west edge
    make_box("Gallery_Clock_Left", (-6.5, 3.95, 0.31), (0.80, 0.42, 0.02), PALETTE)
    make_box("Gallery_Clock_Left_Face", (-6.5, 3.95, 0.325), (0.60, 0.20, 0.01), (0.04, 0.05, 0.07, 1.0))
    for i, dx in enumerate((-0.20, -0.08, 0.08, 0.20)):
        make_box(f"Gallery_Clock_Left_Digit_{i}", (-6.5 + dx, 3.95, 0.3325), (0.06, 0.10, 0.005), (0.96, 0.72, 0.36, 1.0))
    # the submission label at the upper-left, below the clock
    make_box("Submission_Label", (-6.5, 3.35, 0.31), (0.80, 0.30, 0.02), PALETTE)
    make_box("Submission_Label_Text", (-6.5, 3.35, 0.325), (0.62, 0.06, 0.01), (0.86, 0.84, 0.78, 1.0))


def build_gallery_2026_09():
    """DRAFT 2 (2026-09-03): the gallery's layers. "The build faded to
    dimness — still visible, tower and town held as the gallery's
    first layer — and the next build began to render over it." Four
    glass sheets hover over the table, one per submission in the
    order the substrate walked them (Dean 2013, Egilsson 1971,
    Halvorsen 1968, the rest), each with a name tab at its south-west
    corner. Labels beside the two off-frame glyphs. The cursor
    blinking at the center of the template, where The Submission
    starts."""
    sheet = (0.62, 0.78, 0.92, 0.10)
    for li, (z, shade) in enumerate(((1.90, 0.10), (2.15, 0.08), (2.40, 0.06), (2.65, 0.05))):
        make_box(f"Gallery_Layer_{li}", (1.4, 0.0, z), (9.2, 9.0, 0.004), (sheet[0], sheet[1], sheet[2], shade))
        make_box(f"Gallery_Layer_{li}_Edge", (1.4, -4.51, z), (9.2, 0.02, 0.012), (0.62, 0.86, 0.96, 0.6))
        make_box(f"Gallery_Layer_{li}_Tab", (-2.9, -4.62, z), (0.70, 0.20, 0.010), PALETTE)
        make_box(f"Gallery_Layer_{li}_Tab_Text", (-2.9, -4.62, z + 0.0075), (0.56, 0.06, 0.004), PALETTE_GLYPH if li == 0 else PALETTE_GREY)
    # the vitrine's four brass standards the sheets hang on (2026-09-23:
    # four glass sheets hovered 1.5-2.3 m over the table on nothing)
    for sx_, sy_ in ((-3.21, -4.49), (6.01, -4.49), (-3.21, 4.51), (6.01, 4.51)):
        make_box(f"Gallery_Standard_{sx_:+.0f}_{sy_:+.0f}", (sx_, sy_, 0.30 + (2.66 - 0.30) / 2.0), (0.05, 0.05, 2.66 - 0.30), BRASS)
    # the off-frame glyphs get their labels
    make_box("Foundation_Label", (5.94, -1.16, Z_TRACE + 0.001), (0.30, 0.08, 0.004), PALETTE)
    make_box("Foundation_Label_Text", (5.94, -1.16, Z_TRACE + 0.0045), (0.24, 0.03, 0.002), PALETTE_GLYPH)
    make_box("Cove_Label", (2.25, -3.25, Z_TRACE + 0.001), (0.30, 0.08, 0.004), PALETTE)
    make_box("Cove_Label_Text", (2.25, -3.25, Z_TRACE + 0.0045), (0.24, 0.03, 0.002), PALETTE_GLYPH)
    # the cursor at the center of the template, waiting for her to place something
    make_cyl("Cursor_Ring", (0.0, -0.06, Z_TRACE + 0.001), 0.06, 0.002, PALETTE_GLYPH, segments=16)
    make_cyl("Cursor_Ring_Inner", (0.0, -0.06, Z_TRACE + 0.0025), 0.045, 0.001, LAND, segments=16)
    make_box("Cursor_Cross_H", (0.0, -0.06, Z_TRACE + 0.0035), (0.05, 0.004, 0.001), PALETTE_GLYPH)
    make_box("Cursor_Cross_V", (0.0, -0.06, Z_TRACE + 0.0035), (0.004, 0.05, 0.001), PALETTE_GLYPH)


# (pass 471) make_gable's centre is the prism's MID-height: the house, cabin
# and mill roofs were centred on their walls' tops, so the walls' top edges
# came out through both slopes. Each roof is now raised by its half-height.


def build_cove_2026_11():
    """(pass 471) OLAUS'S COVE, rendered: "Olaus's submission rendered. A
    boat, a dock, a salt-shed at a small cove south of Bandon. The smallest
    of the builds." (epilogue_gallery). The cove was a 6 cm glyph cube and its
    label — the close-up showed a blue box. The submission now renders beside
    its glyph, smaller than the mill: a crescent of beach round a round of
    sea, a plank dock on four posts, a sailboat at the dock (the mast and sail
    are what make a stranger say "boat" at this scale), the salt-shed on the
    beach under its gable."""
    cx, cy = 2.75, -2.97
    make_cyl("Cove_Beach", (cx, cy + 0.03, Z_DECAL + 0.0015), 0.21, 0.003, SAND, segments=20)
    make_cyl("Cove_Water", (cx, cy - 0.02, Z_DECAL + 0.0035), 0.15, 0.003, SEA, segments=20)
    make_box("Cove_Water_Swell", (cx, cy - 0.08, Z_DECAL + 0.0055), (0.16, 0.006, 0.001), SEA_LT)
    # the dock: from the beach's north edge out over the water
    dx_, dy0, dy1 = cx + 0.04, cy + 0.15, cy - 0.04
    make_box("Cove_Dock", (dx_, (dy0 + dy1) / 2.0, Z_TOP + 0.016), (0.03, dy0 - dy1, 0.006), (0.52, 0.40, 0.28, 1.0))
    for pi_, py_ in enumerate((dy0 - 0.01, (dy0 + dy1) / 2.0 + 0.02, (dy0 + dy1) / 2.0 - 0.03, dy1 + 0.01)):
        for sx_ in (-0.014, 0.014):
            make_cyl(f"Cove_Dock_Post_{pi_}_{'W' if sx_ < 0 else 'E'}", (dx_ + sx_, py_, Z_TOP + 0.0095),
                     0.0028, 0.013, (0.34, 0.26, 0.18, 1.0), segments=6)
    # the boat tied at the dock's end, on the water
    bx_, by_ = dx_ + 0.045, cy - 0.02
    make_box("Cove_Boat_Hull", (bx_, by_, Z_DECAL + 0.0105), (0.026, 0.066, 0.012), (0.90, 0.88, 0.82, 1.0))
    make_box("Cove_Boat_Stripe", (bx_, by_, Z_DECAL + 0.0150), (0.027, 0.067, 0.003), (0.66, 0.22, 0.18, 1.0))
    make_box("Cove_Boat_Bow", (bx_, by_ + 0.038, Z_DECAL + 0.0115), (0.016, 0.012, 0.012), (0.90, 0.88, 0.82, 1.0))
    make_box("Cove_Boat_Well", (bx_, by_ - 0.004, Z_DECAL + 0.0167), (0.018, 0.040, 0.001), (0.40, 0.30, 0.22, 1.0))
    make_cyl("Cove_Boat_Mast", (bx_, by_ + 0.010, Z_DECAL + 0.0165 + 0.030), 0.0018, 0.060, (0.46, 0.36, 0.26, 1.0), segments=6)
    make_box("Cove_Boat_Sail", (bx_ + 0.0015, by_ - 0.006, Z_DECAL + 0.0165 + 0.030), (0.0015, 0.030, 0.048), (0.96, 0.94, 0.88, 1.0))
    make_box("Cove_Boat_Line", (bx_ - 0.024, by_ + 0.020, Z_TOP + 0.017), (0.024, 0.0015, 0.0015), (0.80, 0.74, 0.58, 1.0))
    # the salt-shed on the beach, west of the dock
    sx0, sy0 = cx - 0.09, cy + 0.12
    make_box("Cove_Salt_Shed", (sx0, sy0, Z_TOP + 0.0045 + 0.022), (0.075, 0.055, 0.044), (0.82, 0.80, 0.74, 1.0))
    make_gable("Cove_Salt_Shed_Roof", (sx0, sy0, Z_TOP + 0.0045 + 0.044 + 0.016), (0.085, 0.065, 0.032), ROOF, ridge_axis="X")
    make_box("Cove_Salt_Shed_Door", (sx0 + 0.010, sy0 - 0.0280, Z_TOP + 0.0045 + 0.016), (0.018, 0.002, 0.030), (0.36, 0.28, 0.20, 1.0))


def build_foundation_2026_11():
    """(pass 474) "The foundation building in Eugene rendered. A four-story
    office building on the corner of 11th and Olive. Brick, with cedar trim."
    (epilogue_gallery n71). It was the glyph cube on the east edge and its
    label; the build renders beside its glyph, the way the cove does: four
    brick storeys, a cedar band at each floor line, the windows in rows,
    the corner entrance, the two streets meeting at its corner."""
    fx, fy = 5.60, -1.30
    brick, cedar = (0.56, 0.28, 0.22, 1.0), (0.70, 0.50, 0.30, 1.0)
    make_box("Foundation_Street_11th", (fx, fy - 0.15, Z_DECAL + 0.0006), (0.50, 0.06, 0.002), ROAD)
    make_box("Foundation_Street_Olive", (fx - 0.17, fy + 0.05, Z_DECAL + 0.0007), (0.06, 0.46, 0.002), ROAD)
    make_box("Foundation_Building", (fx + 0.03, fy + 0.04, Z_TOP + 0.10), (0.20, 0.16, 0.20), brick)
    make_box("Foundation_Roof_Cap", (fx + 0.03, fy + 0.04, Z_TOP + 0.2035), (0.21, 0.17, 0.007), cedar)
    for fl in range(1, 4):
        make_box(f"Foundation_Cedar_Band_{fl}", (fx + 0.03, fy + 0.04, Z_TOP + 0.05 * fl), (0.204, 0.164, 0.006), cedar)
    for fl in range(4):
        for wi in range(4):
            make_box(f"Foundation_Window_S_{fl}_{wi}", (fx - 0.045 + wi * 0.05, fy + 0.04 - 0.081, Z_TOP + 0.025 + 0.05 * fl), (0.026, 0.003, 0.024), (0.16, 0.20, 0.26, 1.0))
            if wi < 3:
                make_box(f"Foundation_Window_W_{fl}_{wi}", (fx + 0.03 - 0.101, fy + 0.04 - 0.045 + wi * 0.045, Z_TOP + 0.025 + 0.05 * fl), (0.003, 0.024, 0.024), (0.16, 0.20, 0.26, 1.0))
    make_box("Foundation_Entrance", (fx - 0.06, fy + 0.04 - 0.0815, Z_TOP + 0.016), (0.03, 0.004, 0.032), (0.30, 0.22, 0.16, 1.0))


def main():
    clear_scene()
    build_plinth()
    build_coast()
    build_bluff_and_tower()
    build_town_and_road()
    build_cabin_and_network()
    build_mill_and_grove()
    build_headland_and_pools()
    build_palettes_and_clocks()
    build_gallery_2026_09()
    build_cove_2026_11()
    build_foundation_2026_11()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/estuary_7_template.glb"))
    print(f"\n[build_estuary_7_template] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
