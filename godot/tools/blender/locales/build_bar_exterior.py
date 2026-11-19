"""Bar exterior — vol1 ch3's sidewalk ("what sort of superpower
would you have?"). The talk outside the bar, night.

The interior reuses new_orleans_bar; this is the street. Hero
features: a two-story brick frontage, the recessed bar door with
warm spill, the neon sign over the door, a big front window glowing
from inside, dark upper-story windows, a streetlamp, a parked sedan
at the curb, trash can, and the alley gap at the block's end.

Coordinate frame: Blender Z-up. y=0 is the road's south edge (the
camera stands on the sidewalk, y≈2-4); +Y runs north: road → curb →
sidewalk → building face at y=4.5. glTF export remaps to Godot
(x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  bar_exterior_night — from the far parking lane across the street,
  looking N at the whole frontage (draft 2, 2026-11-18).

DRAFT 2 (2026-11-18): the street at real size — two lanes and a parking
lane each side, the block running 60 m both ways, the far side built
(laundromat, record shop, a lot, flats), the door recessed for real.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.vehicles import make_car

COL_ASPHALT = (0.14, 0.14, 0.16, 1.0)
COL_CURB = (0.36, 0.36, 0.34, 1.0)
COL_WALK = (0.30, 0.30, 0.29, 1.0)
COL_BRICK = (0.34, 0.22, 0.18, 1.0)
COL_BRICK_DK = (0.26, 0.16, 0.13, 1.0)
COL_LINTEL = (0.44, 0.42, 0.38, 1.0)
COL_DOOR = (0.16, 0.13, 0.11, 1.0)
COL_DOOR_GLOW = (0.98, 0.76, 0.42, 1.0)
COL_WIN_WARM = (0.95, 0.72, 0.40, 1.0)
COL_WIN_DARK = (0.10, 0.11, 0.14, 1.0)
COL_FRAME = (0.18, 0.16, 0.14, 1.0)
COL_NEON = (0.95, 0.35, 0.42, 1.0)       # red-pink tube — blooms
COL_NEON_BOX = (0.20, 0.12, 0.14, 1.0)
COL_POLE = (0.26, 0.26, 0.28, 1.0)
COL_LAMP = (0.98, 0.84, 0.55, 1.0)
COL_CAR = (0.22, 0.26, 0.32, 1.0)
COL_CAR_DK = (0.12, 0.14, 0.17, 1.0)
COL_TIRE = (0.08, 0.08, 0.09, 1.0)
COL_SKY = (0.10, 0.10, 0.16, 1.0)


def build_street():
    # (2026-11-18, draft 2) a real two-lane street with a parking lane each
    # side, curb to curb 10.9 m, the block running 60 m: it was a 3 m lane
    # with nothing across it, so the reverse close-up looked into the void
    # and the forward one stood a metre off the bricks
    make_box("Road", (0.0, -3.5375, 0.0), (60.0, 10.925, 0.04), COL_ASPHALT)
    make_box("Curb", (0.0, 2.05, 0.07), (60.0, 0.25, 0.14), COL_CURB)
    make_box("Walk", (0.0, 3.3, 0.05), (60.0, 2.4, 0.10), COL_WALK)
    for i in range(19):
        make_box(f"Walk_Seam_{i}", (-27.0 + i * 3.0, 3.3, 0.105), (0.05, 2.4, 0.01),
                 COL_CURB)


def build_building():
    """Brick frontage, face at y=4.5, two stories."""
    make_box("Facade", (0.0, 5.0, 3.1), (16.0, 1.0, 6.2), COL_BRICK)
    make_box("Facade_Base", (0.0, 4.46, 0.35), (16.0, 0.10, 0.7), COL_BRICK_DK)
    make_box("Cornice", (0.0, 4.55, 6.05), (16.2, 0.35, 0.30), COL_LINTEL)
    make_box("Band_Course", (0.0, 4.46, 3.30), (16.0, 0.08, 0.22), COL_LINTEL)   # on the facade (2026-09-23: 2 cm off it)
    # Recessed bar door west of center, warm spill inside the reveal
    # (2026-11-18, draft 2) the reveal was ONE solid block 0.35 m proud of
    # the wall, the door and its glow buried inside it: jambs and a head
    # round an open recess, the door at the back with its lit glass
    for k, jx in enumerate((-1.5875, -0.4125)):
        make_box(f"Door_Reveal_Jamb_{k}", (jx, 4.3125, 1.27), (0.225, 0.375, 2.34), COL_BRICK_DK)
    make_box("Door_Reveal_Head", (-1.0, 4.3125, 2.37), (0.95, 0.375, 0.14), COL_BRICK_DK)
    make_box("Door", (-1.0, 4.47, 1.20), (0.95, 0.06, 2.2), COL_DOOR)
    make_box("Door_Spill", (-1.0, 4.435, 1.55), (0.62, 0.02, 1.10), COL_DOOR_GLOW)
    make_box("Door_Handle", (-0.66, 4.425, 1.10), (0.04, 0.03, 0.30), COL_LINTEL)
    make_box("Door_Kick", (-1.0, 4.435, 0.28), (0.85, 0.02, 0.24), (0.30, 0.28, 0.24, 1.0))
    make_box("Door_Lintel", (-1.0, 4.40, 2.55), (1.6, 0.20, 0.22), COL_LINTEL)
    # Big front window east of the door — warm from inside
    make_box("Win_Frame", (2.4, 4.42, 1.65), (3.2, 0.10, 1.9), COL_FRAME)
    # IN FRONT of the frame (sheet 42: inside the frame box, the frame hid
    # the glow but an L-shaped sliver)
    make_box("Win_Warm", (2.4, 4.35, 1.65), (2.9, 0.03, 1.65), COL_WIN_WARM)
    make_box("Win_Sill", (2.4, 4.36, 0.66), (3.4, 0.18, 0.10), COL_LINTEL)
    # Dark upper-story windows
    for i, wx in enumerate((-5.5, -2.5, 0.5, 3.5, 6.5)):
        # glass and sill on the facade face at y 4.50 (2026-09-23: both
        # stood 3 cm proud of the wall on nothing)
        make_box(f"Up_Win_{i}", (wx, 4.47, 4.55), (1.1, 0.06, 1.5), COL_WIN_DARK)
        make_box(f"Up_Sill_{i}", (wx, 4.43, 3.75), (1.3, 0.14, 0.08), COL_LINTEL)
    # Neighbor frontage beyond the alley gap, west
    # (2026-11-19, draft 3) the alley is a real gap now — build_alley_2026_11();
    # it was a black box flush with the two facades
    make_box("Neighbor", (-11.5, 5.0, 2.6), (4.6, 1.0, 5.2), COL_BRICK_DK)


def build_neon():
    """The bar's neon over the door: backing box + two tube runs +
    a hanging bracket."""
    make_box("Neon_Box", (-1.0, 4.31, 3.15), (2.6, 0.22, 0.9), COL_NEON_BOX)
    make_box("Neon_Tube_Top", (-1.0, 4.175, 3.38), (2.1, 0.05, 0.10), COL_NEON)
    make_box("Neon_Tube_Bot", (-1.0, 4.175, 2.95), (1.6, 0.05, 0.08), COL_NEON)
    # the bracket down onto the box (2026-09-23: 2 cm over it)
    make_box("Neon_Bracket", (-1.0, 4.42, 3.66), (0.12, 0.30, 0.12), COL_FRAME)


def build_street_furniture():
    # Streetlamp east of the window
    make_cyl("Lamp_Pole", (4.8, 2.6, 2.3), 0.08, 4.6, COL_POLE, segments=8)
    make_box("Lamp_Arm", (4.8, 2.0, 4.55), (0.07, 1.3, 0.07), COL_POLE)
    make_box("Lamp_Head", (4.8, 1.45, 4.48), (0.22, 0.55, 0.12), COL_FRAME)
    make_box("Lamp_Bulb", (4.8, 1.45, 4.41), (0.15, 0.38, 0.03), COL_LAMP)
    # Trash can by the alley
    make_cyl("Trash", (-6.9, 3.6, 0.50), 0.26, 0.80, COL_POLE, segments=10)   # on the sidewalk (2026-09-23: sunk 10 cm through it)
    # Parked sedan at the curb, west of the door (2026-11-18, draft 2: the
    # profiled car, 20 cm off the curb face, where three boxes stood)
    make_car("Sedan", -3.8, 0.85, 4.6, COL_CAR, along="X")


def build_backdrop():
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)
    # Far rooflines across the street behind the camera don't render;
    # a low distant block face beyond the building's roof
    # to the ground (2026-09-24: a slab hanging 6 m up — it only read as
    # "a block beyond the roof" from one camera)
    make_box("Far_Block", (6.0, 16.0, 4.2), (20.0, 0.06, 8.4), (0.07, 0.07, 0.10, 1.0))


def main():
    clear_scene()
    build_street()
    build_building()
    build_neon()
    build_street_furniture()
    build_backdrop()
    build_block_2026_11()
    build_far_side_2026_11()
    build_alley_2026_11()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/bar_exterior.glb"))
    print(f"\n[build_bar_exterior] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 43m. The bar is on a street in a
    town: brick rooflines continuing down the block, a water tower
    silhouette, treeline past the edge of town."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    make_box("Ground_Far", (0.0, 0.0, -0.03), (1100.0, 1100.0, 0.02),
             (0.20, 0.19, 0.18, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarBlock", COL_BRICK_DK,
                   [(60.0, 70.0, 7.5, 0.92), (130.0, 110.0, 9.0, 0.74)],
                   profile="roofline")
    make_far_bands("FarEdge", (0.20, 0.26, 0.17),
                   [(260.0, 200.0, 11.0, 0.55), (470.0, 330.0, 14.0, 0.42)],
                   profile="treeline")
    make_cyl("WaterTower_Tank", (95.0, 180.0, 26.0), 7.0, 8.0,
             (0.30, 0.30, 0.32, 1.0), segments=10)
    for li in range(4):
        make_cyl("WaterTower_Leg_%d" % li,
                 (95.0 + (5.0 if li % 2 else -5.0),
                  180.0 + (5.0 if li < 2 else -5.0), 11.0),
                 0.5, 22.0, (0.24, 0.24, 0.26, 1.0), segments=6)



COL_STUCCO = (0.42, 0.40, 0.36, 1.0)
COL_WIN_COOL = (0.72, 0.86, 0.90, 1.0)    # a laundromat's fluorescents
COL_SHUTTER = (0.36, 0.37, 0.39, 1.0)
COL_YELLOW = (0.86, 0.70, 0.22, 1.0)


def _streetlamp(prefix, x, y, toward):
    """The cobra-head lamp: pole at the curb, arm out over the road
    (`toward` -1 reaches south from the near walk, +1 north from the far)."""
    make_cyl(f"{prefix}_Pole", (x, y, 2.3), 0.08, 4.6, COL_POLE, segments=8)
    make_box(f"{prefix}_Arm", (x, y + toward * 0.6, 4.55), (0.07, 1.3, 0.07), COL_POLE)
    make_box(f"{prefix}_Head", (x, y + toward * 1.15, 4.48), (0.22, 0.55, 0.12), COL_FRAME)
    make_box(f"{prefix}_Bulb", (x, y + toward * 1.15, 4.41), (0.15, 0.38, 0.03), COL_LAMP)


def _upper_windows(prefix, x0, x1, face_y, z, lit=(), step=2.6, w=1.0, h=1.4, toward=-1):
    """A row of upper-storey windows on a facade (glass a hair proud of the
    face toward the street), `lit` the indices that are somebody's lamp."""
    n = max(1, int((x1 - x0 - 0.8) // step))
    span = (n - 1) * step
    for i in range(n):
        wx = (x0 + x1) / 2.0 - span / 2.0 + i * step
        col = COL_WIN_WARM if i in lit else COL_WIN_DARK
        make_box(f"{prefix}_{i}", (wx, face_y + toward * 0.03, z), (w, 0.06, h), col)
        make_box(f"{prefix}_{i}_Sill", (wx, face_y + toward * 0.07, z - h / 2.0 - 0.04), (w + 0.2, 0.14, 0.08), COL_LINTEL)


def build_block_2026_11():
    """DRAFT 2 (2026-11-18): the block goes on past the bar both ways —
    the hardware store east, a taller brick block west past the alley —
    with a second streetlamp, parking meters by the sedan and a hydrant.

    Draft 3 targets: the alley as a real gap (walls, a dumpster, the
    side door the smokers use); fire escapes on the west block; awnings;
    wires overhead between the lamps; the bar's own sign lettered (art
    roster) instead of two tube bars."""
    # EAST: the hardware store, closed for the night (x 8..19)
    make_box("East_Store", (13.5, 7.5, 2.4), (11.0, 6.0, 4.8), (0.30, 0.25, 0.21, 1.0))
    make_box("East_Store_Cornice", (13.5, 4.42, 4.65), (11.2, 0.18, 0.25), COL_LINTEL)
    make_box("East_Store_Sign", (13.5, 4.44, 3.55), (6.5, 0.12, 0.70), (0.16, 0.18, 0.20, 1.0))
    for i, wx in enumerate((10.4, 16.6)):
        make_box(f"East_Store_Win_{i}", (wx, 4.47, 1.55), (3.4, 0.06, 1.8), COL_WIN_DARK)
        make_box(f"East_Store_Win_{i}_Sill", (wx, 4.43, 0.60), (3.6, 0.14, 0.10), COL_LINTEL)
    make_box("East_Store_Door", (13.5, 4.47, 1.15), (1.1, 0.06, 2.1), COL_DOOR)
    make_box("East_Store_Door_Lintel", (13.5, 4.44, 2.30), (1.4, 0.12, 0.16), COL_LINTEL)
    # x 19..30: two storeys of somebody's flats over a shut shop
    make_box("East_Flats", (24.5, 7.5, 3.3), (11.0, 6.0, 6.6), (0.34, 0.27, 0.22, 1.0))
    make_box("East_Flats_Cornice", (24.5, 4.40, 6.45), (11.2, 0.22, 0.28), COL_LINTEL)
    _upper_windows("East_Flats_Win", 19.0, 30.0, 4.5, 4.6, lit=(1,))
    make_box("East_Flats_Shop", (24.5, 4.47, 1.5), (7.0, 0.06, 1.9), COL_WIN_DARK)
    # WEST: past the neighbour, a three-storey brick block (x -30..-13.8)
    make_box("West_Block", (-21.9, 7.5, 4.6), (15.8, 6.0, 9.2), (0.31, 0.21, 0.17, 1.0))
    make_box("West_Block_Cornice", (-21.9, 4.40, 9.05), (16.0, 0.22, 0.30), COL_LINTEL)
    _upper_windows("West_Block_Win2", -29.6, -14.2, 4.5, 4.4, lit=(2,))
    _upper_windows("West_Block_Win3", -29.6, -14.2, 4.5, 7.4, lit=(0, 4))
    make_box("West_Block_Shop", (-21.9, 4.47, 1.5), (9.0, 0.06, 1.9), COL_WIN_DARK)
    # the street furniture the near walk was missing
    _streetlamp("Lamp_W", -9.6, 2.6, -1)
    for i, mx in enumerate((-6.4, -1.2)):
        make_cyl(f"Meter_{i}_Post", (mx, 2.45, 0.60), 0.035, 1.0, COL_POLE, segments=8)
        make_box(f"Meter_{i}_Head", (mx, 2.45, 1.24), (0.16, 0.12, 0.28), (0.30, 0.31, 0.33, 1.0))
        make_box(f"Meter_{i}_Glass", (mx, 2.385, 1.28), (0.11, 0.004, 0.09), COL_WIN_DARK)
    make_cyl("Hydrant_Body", (6.6, 2.5, 0.42), 0.11, 0.64, (0.62, 0.16, 0.14, 1.0), segments=10)
    make_cyl("Hydrant_Cap", (6.6, 2.5, 0.78), 0.08, 0.08, (0.62, 0.16, 0.14, 1.0), segments=10)
    make_cyl("Hydrant_Nozzle", (6.6, 2.36, 0.52), 0.045, 0.10, (0.55, 0.14, 0.12, 1.0), segments=8, axis='Y')
    # the street: a double yellow line, a manhole, two storm drains at the curb
    for k, ly in enumerate((-3.45, -3.63)):
        make_box(f"Road_Line_{k}", (0.0, ly, 0.0225), (60.0, 0.10, 0.004), COL_YELLOW)
    make_cyl("Road_Manhole", (5.5, -1.6, 0.0225), 0.33, 0.004, (0.20, 0.20, 0.21, 1.0), segments=14)
    for k, dx in enumerate((-7.6, 9.2)):
        make_box(f"Road_Drain_{k}", (dx, 1.70, 0.0225), (0.90, 0.40, 0.004), (0.08, 0.08, 0.09, 1.0))


def build_alley_2026_11():
    """DRAFT 3 (2026-11-19): the alley between the bar and its west
    neighbour, 1.2 m wide, 8 m deep to a plank fence — the bar's own side
    wall with the side door the smokers use under a caged bulb, two milk
    crates and a coffee-can ashtray by it, a dumpster wedged at the back.
    The two buildings get their depth behind their facades (they were 1 m
    slabs), so the alley has walls.

    Draft 4 targets: a fire escape on the neighbour; wires across; the
    bulb's practical shadow; litter."""
    AX0, AX1, AY0, AY1 = -9.2, -8.0, 4.5, 12.5
    make_box("Bar_Body", (0.0, (5.5 + AY1) / 2.0, 3.1), (16.0, AY1 - 5.5, 6.2), COL_BRICK)
    make_box("Neighbor_Body", (-11.5, (5.5 + AY1) / 2.0, 2.6), (4.6, AY1 - 5.5, 5.2), COL_BRICK_DK)
    make_box("Alley_Ground", ((AX0 + AX1) / 2.0, (AY0 + AY1) / 2.0, 0.03), (AX1 - AX0, AY1 - AY0, 0.06), (0.17, 0.17, 0.18, 1.0))
    make_box("Alley_Fence", ((AX0 + AX1) / 2.0, AY1 - 0.04, 1.0), (AX1 - AX0, 0.06, 2.0), (0.34, 0.27, 0.19, 1.0))
    for k in range(4):
        make_box(f"Alley_Fence_Gap_{k}", (AX0 + 0.15 + k * 0.3, AY1 - 0.075, 1.0), (0.012, 0.01, 2.0), (0.20, 0.16, 0.12, 1.0))
    # the dumpster wedged lengthwise at the back
    make_box("Alley_Dumpster", (-8.6, 11.35, 0.66), (1.0, 1.8, 1.2), (0.18, 0.32, 0.22, 1.0))
    make_box("Alley_Dumpster_Lid", (-8.6, 11.35, 1.29), (1.04, 1.84, 0.06), (0.12, 0.22, 0.15, 1.0))
    # the side door in the bar's west wall, its caged bulb, the smokers' seats
    make_box("Alley_Side_Door", (AX1 - 0.03, 7.5, 1.08), (0.06, 0.92, 2.04), COL_DOOR)
    make_box("Alley_Side_Door_Frame", (AX1 - 0.04, 7.5, 2.14), (0.08, 1.06, 0.08), COL_FRAME)
    make_box("Alley_Side_Door_Plate", (AX1 - 0.065, 7.85, 1.05), (0.01, 0.10, 0.30), COL_LINTEL)
    make_box("Alley_Bulb_Bracket", (AX1 - 0.08, 7.5, 2.42), (0.16, 0.04, 0.04), COL_POLE)
    make_cyl("Alley_Bulb_Cage", (AX1 - 0.17, 7.5, 2.34), 0.06, 0.14, (0.22, 0.22, 0.24, 1.0), segments=8)
    make_cyl("Alley_Bulb", (AX1 - 0.17, 7.5, 2.34), 0.035, 0.08, COL_LAMP, segments=8)
    for k, (cx, cy, cz) in enumerate(((-8.78, 6.85, 0.225), (-8.78, 6.85, 0.555))):
        make_box(f"Alley_Milk_Crate_{k}", (cx, cy, cz), (0.33, 0.33, 0.33), (0.62, 0.14, 0.12, 1.0) if k == 0 else (0.16, 0.28, 0.52, 1.0))
    make_cyl("Alley_Ashtray_Can", (-8.25, 8.2, 0.15), 0.08, 0.18, (0.46, 0.44, 0.40, 1.0), segments=10)


def build_far_side_2026_11():
    """DRAFT 2 (2026-11-18): ACROSS the street — what the reverse close-up
    and anyone leaving the bar look at. Far curb and walk, a laundromat
    still lit at closing time, a record shop with its shutter down, a
    parking lot with one tall light, flats over a garage, two cobra-head
    lamps and two cars at the far curb. Face of the row at y -11.65.

    Draft 3 targets: the laundromat's inside (washers through the glass —
    the pane is opaque); a lettered sign for each shop (art roster); a
    bus-stop bench; litter and a newspaper box on the far walk."""
    # the curb and walk broken at the lot's mouth (x 10.5..15): the curb down
    # to a 2 cm lip, the walk to an apron a car rolls over
    for nm, x0, x1 in (("W", -30.0, 10.5), ("E", 15.0, 30.0)):
        make_box(f"Far_Curb_{nm}", ((x0 + x1) / 2.0, -9.125, 0.07), (x1 - x0, 0.25, 0.14), COL_CURB)
        make_box(f"Far_Walk_{nm}", ((x0 + x1) / 2.0, -10.45, 0.05), (x1 - x0, 2.4, 0.10), COL_WALK)
    make_box("Far_Curb_Cut", (12.75, -9.125, 0.03), (4.5, 0.25, 0.02), COL_CURB)
    make_box("Lot_Apron", (12.75, -10.45, 0.01), (4.5, 2.4, 0.06), (0.24, 0.24, 0.24, 1.0))
    for i in range(19):
        sx = -27.0 + i * 3.0
        if 10.4 < sx < 15.1:
            continue
        make_box(f"Far_Walk_Seam_{i}", (sx, -10.45, 0.105), (0.05, 2.4, 0.01), COL_CURB)
    FY = -11.65
    # the laundromat (x -7..1): one storey, its whole front a lit pane
    make_box("Laundromat", (-3.0, FY - 3.0, 2.3), (8.0, 6.0, 4.6), COL_STUCCO)
    make_box("Laundromat_Pane", (-3.5, FY + 0.03, 1.65), (6.0, 0.06, 2.1), COL_WIN_COOL)
    for k in range(4):
        make_box(f"Laundromat_Mullion_{k}", (-6.5 + k * 2.0, FY + 0.07, 1.65), (0.08, 0.04, 2.1), COL_FRAME)
    make_box("Laundromat_Pane_Head", (-3.5, FY + 0.07, 2.74), (6.1, 0.06, 0.08), COL_FRAME)
    make_box("Laundromat_Pane_Sill", (-3.5, FY + 0.08, 0.56), (6.2, 0.16, 0.10), COL_LINTEL)
    make_box("Laundromat_Door", (0.15, FY + 0.03, 1.15), (0.95, 0.06, 2.1), COL_WIN_COOL)
    make_box("Laundromat_Door_Frame", (0.15, FY + 0.07, 2.24), (1.05, 0.06, 0.08), COL_FRAME)
    make_box("Laundromat_Sign", (-3.0, FY + 0.08, 3.45), (7.0, 0.16, 0.70), (0.14, 0.16, 0.20, 1.0))
    make_box("Laundromat_Sign_Tube", (-3.0, FY + 0.18, 3.45), (5.6, 0.04, 0.10), (0.55, 0.85, 0.95, 1.0))
    # the record shop (x 1..8.5): two storeys, the shutter down
    make_box("Record_Shop", (4.75, FY - 3.0, 3.5), (7.5, 6.0, 7.0), (0.30, 0.20, 0.17, 1.0))
    make_box("Record_Shop_Shutter", (4.75, FY + 0.04, 1.50), (5.2, 0.08, 2.8), COL_SHUTTER)
    for k in range(6):
        make_box(f"Record_Shop_Shutter_Rib_{k}", (4.75, FY + 0.09, 0.35 + k * 0.48), (5.2, 0.03, 0.04), (0.28, 0.29, 0.31, 1.0))
    make_box("Record_Shop_Sign", (4.75, FY + 0.08, 3.40), (6.0, 0.16, 0.60), (0.22, 0.12, 0.12, 1.0))
    make_box("Record_Shop_Cornice", (4.75, FY + 0.12, 6.85), (7.7, 0.24, 0.30), COL_LINTEL)
    _upper_windows("Record_Shop_Win", 1.0, 8.5, FY, 5.0, lit=(), step=2.4, toward=1)
    # the parking lot (x 8.5..17): asphalt back to a block wall, one tall light
    make_box("Lot", (12.75, FY - 9.0, 0.0), (8.5, 18.0, 0.04), (0.17, 0.17, 0.18, 1.0))
    make_box("Lot_Wall_Back", (12.75, FY - 18.1, 1.2), (8.5, 0.2, 2.4), (0.40, 0.39, 0.37, 1.0))
    for k, sx in enumerate((10.0, 12.8, 15.6)):
        make_box(f"Lot_WheelStop_{k}", (sx, FY - 16.6, 0.08), (1.8, 0.2, 0.12), (0.52, 0.51, 0.48, 1.0))
    make_cyl("Lot_Light_Pole", (16.4, FY - 8.0, 4.0), 0.10, 8.0, COL_POLE, segments=8)
    make_box("Lot_Light_Head", (16.0, FY - 8.0, 7.95), (0.9, 0.35, 0.18), COL_FRAME)
    make_box("Lot_Light_Lens", (16.0, FY - 8.0, 7.85), (0.75, 0.28, 0.03), COL_LAMP)
    make_car("Lot_Car", 12.8, FY - 13.9, 4.4, (0.40, 0.36, 0.30, 1.0), along="Y")
    # x 17..30: flats over a two-bay garage
    make_box("Garage_Flats", (23.5, FY - 3.0, 3.4), (13.0, 6.0, 6.8), (0.33, 0.28, 0.23, 1.0))
    for k, gx in enumerate((20.0, 24.0)):
        make_box(f"Garage_Bay_{k}", (gx, FY + 0.04, 1.40), (3.0, 0.08, 2.6), COL_SHUTTER)
    _upper_windows("Garage_Flats_Win", 17.0, 30.0, FY, 4.8, lit=(3,), toward=1)
    # x -30..-7: three storeys of apartments over a shut diner
    make_box("Far_Apts", (-18.5, FY - 3.0, 4.8), (23.0, 6.0, 9.6), (0.32, 0.26, 0.22, 1.0))
    make_box("Far_Apts_Cornice", (-18.5, FY + 0.12, 9.45), (23.2, 0.24, 0.30), COL_LINTEL)
    _upper_windows("Far_Apts_Win2", -30.0, -7.0, FY, 4.6, lit=(1, 5), toward=1)
    _upper_windows("Far_Apts_Win3", -30.0, -7.0, FY, 7.6, lit=(3,), toward=1)
    make_box("Far_Apts_Shop", (-14.0, FY + 0.03, 1.5), (8.0, 0.06, 1.9), COL_WIN_DARK)
    make_box("Far_Apts_Door", (-20.0, FY + 0.03, 1.15), (1.2, 0.06, 2.1), COL_DOOR)
    # two lamps on the far curb, arms north over the road
    _streetlamp("Lamp_FW", -3.0, -9.55, +1)
    _streetlamp("Lamp_FE", 15.0, -9.55, +1)
    # two cars at the far curb
    make_car("Far_Pickup", 5.2, -7.95, 5.2, (0.46, 0.18, 0.14, 1.0), pickup=True, along="X")
    make_car("Far_Hatch", -9.5, -7.95, 4.0, (0.30, 0.34, 0.30, 1.0), hatch=True, along="X")


if __name__ == "__main__":
    main()
