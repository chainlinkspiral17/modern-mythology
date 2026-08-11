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

Coordinate frame: Blender Z-up, y=0 south wall with the door, +Y
into the cabin, x=±3.0, back wall y=6.0, ceiling 3.4 (raised for
the loft). glTF export remaps to Godot (x, z, -y).
"""
import os, sys
import math as _m
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
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


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.45), (2.0, 0.20, 0.90), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 with_grid=False, with_stains=False,
                 palette={"tile": (0.48, 0.36, 0.26, 1.0)})
    # The thermometer above the door, nailed there in 1979
    make_box("Thermometer_Back", (0.0, 0.12, 2.60), (0.10, 0.03, 0.26), (0.82, 0.78, 0.68, 1.0))
    make_box("Thermometer_Tube", (0.0, 0.13, 2.60), (0.02, 0.02, 0.20), (0.72, 0.24, 0.20, 1.0))
    # The front door itself
    make_box("Front_Door", (0.0, 0.06, 1.05), (0.95, 0.05, 2.10), COL_WOOD_DK)
    make_cyl("Door_Latch", (0.36, 0.10, 1.02), 0.025, 0.04, COL_IRON, axis='Y', segments=8)
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
    for i in range(4):
        make_cyl(f"Counter_Jar_{i}", (-1.80, 4.95 + i * 0.22, 1.08), 0.055, 0.22,
                 (0.80, 0.82, 0.72, 0.85), segments=8)
        make_cyl(f"Counter_Jar_{i}_Lid", (-1.80, 4.95 + i * 0.22, 1.20), 0.056, 0.03, COL_IRON, segments=8)
    # Hanging pot rack over the counter
    make_box("PotRack_Bar", (-1.7, 4.6, 2.0), (0.04, 1.4, 0.04), COL_IRON)
    for i, (py, r, h, col) in enumerate([(4.2, 0.11, 0.14, COL_IRON), (4.6, 0.13, 0.16, (0.55, 0.35, 0.18, 1.0)),
                                         (5.0, 0.10, 0.12, COL_IRON)]):
        make_cyl(f"PotRack_Hook_{i}", (-1.7, py, 1.9), 0.006, 0.16, COL_IRON_WM, segments=4)
        make_cyl(f"PotRack_Pot_{i}", (-1.7, py, 1.72), r, h, col, segments=10)
    # The kitchen window (N wall over the counter's end)…
    make_window("Kitchen_Window", (-1.6, ROOM_D-0.04, 0), width=1.00, height=0.95)
    # …and the black rotary phone on a small table beside it
    make_box("Phone_Table", (-2.60, 5.35, 0.30), (0.45, 0.45, 0.60), COL_WOOD)
    make_box("Phone_Body", (-2.60, 5.35, 0.66), (0.24, 0.20, 0.10), (0.10, 0.10, 0.11, 1.0))
    make_cyl("Phone_Dial", (-2.60, 5.28, 0.72), 0.07, 0.02, (0.80, 0.78, 0.72, 1.0), axis='Y', segments=10)
    make_box("Phone_Handset", (-2.60, 5.42, 0.75), (0.22, 0.07, 0.05), (0.10, 0.10, 0.11, 1.0))


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
    # Ladder
    for rx in (-0.35, -0.05):
        make_box(f"Ladder_Rail_{rx:.2f}", (rx, 3.95, 1.10), (0.05, 0.05, 2.20), COL_WOOD)
    for s in range(6):
        make_box(f"Ladder_Rung_{s}", (-0.20, 3.95, 0.30 + s * 0.36), (0.34, 0.04, 0.04), COL_WOOD_DK)


def build_stove_corner():
    """Potbelly stove NE + copper kettle + firewood basket + the
    side table where the stick and the reader sit + two armchairs
    pulled to the stove ("Cale and Per in the chairs by the
    stove")."""
    sx, sy = 2.3, 5.4
    make_cyl("Stove_Belly", (sx, sy, 0.55), 0.35, 0.7, COL_IRON, segments=12)
    make_cyl("Stove_Waist", (sx, sy, 0.95), 0.28, 0.16, COL_IRON_WM, segments=12)
    make_cyl("Stove_Top", (sx, sy, 1.08), 0.32, 0.08, COL_IRON, segments=12)
    make_box("Stove_Door", (sx - 0.34, sy, 0.5), (0.04, 0.26, 0.30), COL_IRON_WM)
    make_box("Stove_EmberGlow", (sx - 0.355, sy, 0.5), (0.02, 0.16, 0.18), (0.95, 0.45, 0.15, 1.0))
    make_box("Stove_Legs_hint", (sx, sy, 0.12), (0.5, 0.5, 0.12), COL_IRON)
    make_cyl("Stove_Pipe", (sx, sy, 2.2), 0.09, 2.2, COL_IRON_WM, segments=8)
    # THE COPPER KETTLE with the small dent in its side
    make_cyl("Copper_Kettle", (sx - 0.20, sy + 0.05, 1.20), 0.11, 0.16, COL_COPPER, segments=10)
    make_box("Kettle_Dent", (sx + 0.10, sy, 1.18), (0.03, 0.06, 0.06), (0.58, 0.32, 0.18, 1.0))
    make_box("Kettle_Spout", (sx - 0.34, sy + 0.05, 1.22), (0.08, 0.03, 0.03), COL_COPPER)
    # Firewood: the stack and the cedar BASKET beside the stove
    for r in range(3):
        for c in range(4):
            fy = 4.4 + c * 0.16
            fz = 0.12 + r * 0.16 + (0.0 if c % 2 == 0 else 0.02)
            make_cyl(f"Firewood_{r}_{c}", (2.7, fy, fz), 0.075, 0.5,
                     COL_WOOD if (r + c) % 2 else COL_WOOD_DK, segments=6, axis='X')
    make_cyl("Wood_Basket", (1.68, 5.95, 0.20), 0.28, 0.40, (0.56, 0.42, 0.26, 1.0), segments=10)
    make_cyl("Wood_Basket_Cedar", (1.68, 5.95, 0.36), 0.20, 0.14, COL_WOOD_DK, segments=8)
    # The side table by the wood stove ("She put the stick down on
    # the side table by the wood stove")
    make_box("Stove_SideTable_Top", (1.60, 4.95, 0.54), (0.42, 0.42, 0.05), COL_WOOD)
    make_cyl("Stove_SideTable_Post", (1.60, 4.95, 0.27), 0.05, 0.52, COL_WOOD, segments=8)
    # The two armchairs, at the stove where the prose puts them
    for ci, (cx, cy, tag) in enumerate(((1.35, 4.35, "A"), (0.85, 5.35, "B"))):
        make_box(f"Armchair_{tag}_Base", (cx, cy, 0.26), (0.66, 0.66, 0.40), (0.44, 0.36, 0.28, 1.0))
        make_box(f"Armchair_{tag}_Back", (cx + 0.28, cy, 0.66), (0.14, 0.66, 0.60), (0.40, 0.32, 0.25, 1.0))
        for ay in (cy - 0.31, cy + 0.31):
            make_box(f"Armchair_{tag}_Arm_{ay:.2f}", (cx, ay, 0.50), (0.62, 0.12, 0.36), (0.40, 0.32, 0.25, 1.0))
    # The wool blanket draped over armchair A
    make_box("Armchair_Blanket", (1.35, 4.05, 0.62), (0.60, 0.10, 0.30), COL_WOOL)
    # Cedar chest (the wool blankets live in it)
    make_box("Cedar_Chest", (2.55, 3.55, 0.26), (0.60, 1.05, 0.52), (0.56, 0.40, 0.24, 1.0))
    make_box("Cedar_Chest_Lid", (2.55, 3.55, 0.545), (0.64, 1.09, 0.05), (0.50, 0.36, 0.22, 1.0))


def build_table():
    """The table seats SEVEN ("The seven stayed at the table") — a
    wide round top, seven simple chairs with backs and legs, the
    hurricane lantern on it, the braided rug beneath."""
    tx, ty = 0.0, 2.9
    make_cyl("Table_Top", (tx, ty, 0.76), 0.85, 0.05, COL_WOOD, segments=18)
    make_cyl("Table_Pedestal", (tx, ty, 0.38), 0.09, 0.72, COL_WOOD, segments=10)
    make_cyl("Table_Foot", (tx, ty, 0.05), 0.40, 0.05, COL_WOOD_DK, segments=12)
    for ci in range(7):
        ang = ci * (2.0 * _m.pi / 7.0) + 0.45
        cx, cy = tx + _m.cos(ang) * 1.30, ty + _m.sin(ang) * 1.30
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.45), (0.40, 0.40, 0.05), COL_WOOD)
        bx, by = tx + _m.cos(ang) * 1.48, ty + _m.sin(ang) * 1.48
        make_box(f"Chair_{ci}_Back", (bx, by, 0.75), (0.40, 0.06, 0.55), COL_WOOD)
        for li, (lx, ly) in enumerate(((-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15))):
            make_box(f"Chair_{ci}_Leg_{li}", (cx + lx, cy + ly, 0.22), (0.045, 0.045, 0.44), COL_WOOD)
    # Braided oval rug under the table
    for i, (rr, col) in enumerate([(1.6, (0.46, 0.30, 0.24, 1.0)),
                                   (1.2, (0.54, 0.40, 0.28, 1.0)),
                                   (0.8, (0.40, 0.28, 0.22, 1.0))]):
        make_cyl(f"Rug_Ring_{i}", (tx, ty, 0.008 + i * 0.002), rr, 0.006, col, segments=16)
    # Hurricane lantern on the table
    make_cyl("Lantern_Base", (0.35, 2.6, 0.86), 0.05, 0.05, COL_IRON, segments=8)
    make_cyl("Lantern_Glass", (0.35, 2.6, 0.96), 0.04, 0.13, (0.96, 0.86, 0.55, 0.8), segments=8)
    make_cyl("Lantern_Flame", (0.35, 2.6, 0.99), 0.012, 0.05, (1.0, 0.7, 0.2, 1.0), segments=5)
    make_cyl("Lantern_Cap", (0.35, 2.6, 1.05), 0.045, 0.04, COL_IRON, segments=8)


def build_daybed():
    """The daybed against the W wall where Kai slept."""
    make_box("Daybed_Frame", (-2.42, 1.9, 0.20), (0.92, 2.00, 0.34), COL_WOOD_DK)
    make_box("Daybed_Mattress", (-2.42, 1.9, 0.44), (0.86, 1.92, 0.16), (0.90, 0.86, 0.78, 1.0))
    make_box("Daybed_Bolster", (-2.78, 1.9, 0.62), (0.18, 1.85, 0.22), COL_WOOL)
    make_box("Daybed_Blanket", (-2.40, 1.5, 0.545), (0.84, 0.95, 0.06), (0.56, 0.40, 0.30, 1.0))
    # Chair by the SOUTH window, main room ("The chair by the south
    # window" / "Finn on the floor by the south window")
    make_window("South_Window_W", (-2.0, 0.04, 0), width=1.10, height=1.00)
    make_box("SWChair_Seat", (-1.70, 0.95, 0.44), (0.44, 0.44, 0.05), COL_WOOD)
    make_box("SWChair_Back", (-1.70, 1.15, 0.72), (0.44, 0.05, 0.52), COL_WOOD)
    for li, (lx, ly) in enumerate(((-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16))):
        make_box(f"SWChair_Leg_{li}", (-1.70 + lx, 0.95 + ly, 0.22), (0.045, 0.045, 0.44), COL_WOOD)


def build_east_room():
    """The east room behind the partition: the bed with its window
    above ("the window above the bed gave her the gray-green of
    cedars"), the writing desk with the cedar shelf ("the reader
    was on the shelf where it had been since '46"), the basin with
    the mirror over it."""
    # Bed along the E wall
    make_box("EBed_Frame", (2.10, 1.75, 0.20), (1.45, 1.90, 0.30), COL_WOOD_DK)
    make_box("EBed_Mattress", (2.10, 1.75, 0.46), (1.38, 1.82, 0.16), (0.90, 0.86, 0.78, 1.0))
    make_box("EBed_Blanket", (2.10, 1.45, 0.565), (1.34, 1.10, 0.07), COL_WOOL)
    make_box("EBed_Pillow", (2.10, 2.50, 0.58), (0.90, 0.38, 0.12), (0.96, 0.92, 0.86, 1.0))
    # The window above the bed (E wall) — cedars beyond
    make_box("EBed_Win_Frame", (2.96, 1.45, 1.75), (0.04, 1.20, 0.95), COL_WOOD_DK)
    make_box("EBed_Win_Glass", (2.98, 1.45, 1.75), (0.02, 1.06, 0.82), COL_GLASS)
    # Writing desk against the S wall + the south window over it
    make_window("South_Window_E", (2.0, 0.04, 0), width=0.95, height=0.95)
    make_box("Desk_Top", (1.75, 0.55, 0.74), (0.95, 0.60, 0.05), COL_WOOD)
    for lx in (1.35, 2.15):
        make_box(f"Desk_Leg_{lx:.2f}", (lx, 0.55, 0.37), (0.06, 0.55, 0.72), COL_WOOD_DK)
    make_box("Desk_Notebook", (1.72, 0.52, 0.775), (0.26, 0.20, 0.015), (0.30, 0.26, 0.22, 1.0))
    # The cedar shelf above the desk — player, books, notebooks
    make_box("Cedar_Shelf", (1.75, 0.16, 1.55), (1.10, 0.24, 0.04), (0.56, 0.40, 0.24, 1.0))
    make_box("Shelf_Player", (1.45, 0.16, 1.63), (0.24, 0.16, 0.10), (0.20, 0.20, 0.22, 1.0))
    for bi in range(4):
        make_box(f"Shelf_Book_{bi}", (1.80 + bi * 0.10, 0.16, 1.66),
                 (0.07, 0.16, 0.20), [(0.48, 0.20, 0.16, 1.0), (0.22, 0.30, 0.24, 1.0),
                                      (0.60, 0.52, 0.36, 1.0), (0.30, 0.26, 0.34, 1.0)][bi])
    # Basin + mirror on the partition side
    make_box("Basin_Stand", (0.55, 0.35, 0.42), (0.44, 0.36, 0.84), COL_WOOD)
    make_cyl("Basin_Bowl", (0.55, 0.35, 0.88), 0.16, 0.08, (0.86, 0.86, 0.84, 1.0), segments=12)
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
    make_box("OilLamp_Chain", (0.0, 2.9, CEIL-0.25), (0.02, 0.02, 0.50), COL_IRON)
    make_cyl("OilLamp_Font", (0.0, 2.9, CEIL-0.62), 0.09, 0.12, (0.66, 0.52, 0.24, 1.0), segments=10)
    make_cyl("OilLamp_Chimney", (0.0, 2.9, CEIL-0.48), 0.05, 0.16, (0.96, 0.86, 0.55, 0.8), segments=8)
    # Curtained E window in the main… now inside the east room wall
    # segment north of the partition (main room's east outlook)
    make_box("Window_E_Frame", (2.96, 4.2, 1.6), (0.04, 1.4, 1.1), COL_WOOD_DK)
    make_box("Window_E_Glass", (2.98, 4.2, 1.6), (0.02, 1.24, 0.94), COL_GLASS)
    for sgn in (-1, +1):
        make_box("Window_E_Curtain_%+d" % sgn, (2.9, 4.2 + sgn * 0.55, 1.6),
                 (0.05, 0.34, 1.14), (0.60, 0.28, 0.24, 1.0))


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
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cabin_interior.glb"))
    print(f"\n[build_cabin_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
