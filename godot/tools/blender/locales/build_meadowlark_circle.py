"""meadowlark_circle — Harmony Creek Estates, Texas. vol6's bookends,
re-homed off louisiana_road (2026-09-01).

The prelude (vol6_ch0): "The sprinkler systems on Meadowlark Circle
come on at 6:12 ... lot by lot, traveling east down the block. Number
1402 goes first. Then 1408. Then 1414. Then 1420. Then 1428, which is
the Miller house, where the head on the left corner of the yard has a
hairline crack in the housing and throws water in a thin, surgical
arc that hits the sidewalk at a forty-degree angle and has, over the
past two summers, etched a faint grey stripe into the concrete." The
water tower "at the south end of Gallatin Avenue, behind the NexCorp
lot ... enclosed in a chain-link fence with green privacy screen ...
sixty-two feet tall ... HARMONY CREEK in blue block letters" with the
white NexCorp Residential Solutions van parked beside the fence.
The closing night (ch23): "The cul-de-sacs of the town ... hold. The
Geller porch light at the end of the Caldwell cul-de-sac is on. Don's
silhouette, at eleven-thirty, is at the window." The Monday-night coda
(ch2): "The streetlamps buzz at their subaudible frequency. A black
cat crosses Prairie View. In a white sedan parked at the curb, two
people ... take their shifts on a vigil."

Every "different cul-de-sac" of ch23 renders as this one — the town
is one shape repeated, which is the point of the chapter.

Coordinate frame: Blender Z-up. The street runs east-west along y=0
from the entry at x=-30 to the bulb at x=+22 (r 9). Lots 1402..1428
line the north side west to east; three more face them on the south.
The water tower stands off to the south-east. glTF export remaps to
Godot (x, z, -y).

DRAFT 1 (2026-09-01): five north lots + three south, the Miller
cracked head and its etched stripe, sequential sprinkler fans, HOA
mailboxes, streetlamps, the end house with Don's lit window, the
white sedan at the curb, the black cat, the water tower + NexCorp
fence + van, far bands. Draft 2: garage-door variety, the Salinas
driveway car, the creek behind the Albertsons as a far band, rain
puddles for the storm chapter.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, export_glb
from _props.detail import make_far_bands

ASPHALT = (0.30, 0.30, 0.32, 1.0)
CONCRETE = (0.62, 0.61, 0.58, 1.0)
LAWN = (0.34, 0.46, 0.26, 1.0)
LAWN_DRY = (0.48, 0.48, 0.30, 1.0)
HOUSE_COLS = [(0.86, 0.82, 0.72, 1.0), (0.74, 0.70, 0.62, 1.0), (0.82, 0.78, 0.70, 1.0),
              (0.68, 0.64, 0.58, 1.0), (0.80, 0.76, 0.66, 1.0), (0.78, 0.72, 0.62, 1.0),
              (0.72, 0.68, 0.60, 1.0), (0.84, 0.80, 0.70, 1.0)]
ROOF = (0.36, 0.30, 0.26, 1.0)
TRIM = (0.92, 0.90, 0.86, 1.0)
GLASS = (0.55, 0.62, 0.70, 0.55)
GLASS_LIT = (0.98, 0.86, 0.58, 0.9)
BULB_LIGHT = (1.0, 0.86, 0.58, 1.0)

BULB_X, BULB_R = 22.0, 9.0


def build_street():
    make_box("Ground_Far", (0.0, 0.0, -0.05), (700.0, 700.0, 0.02), (0.30, 0.34, 0.22, 1.0))
    make_box("Meadowlark_Asphalt", (-4.0, 0.0, -0.03), (56.0, 7.0, 0.06), ASPHALT)
    make_cyl("Meadowlark_Bulb", (BULB_X, 0.0, -0.03), BULB_R, 0.06, ASPHALT, segments=24)
    for sgn, nm in ((1, "N"), (-1, "S")):
        make_box(f"Sidewalk_{nm}", (-4.0, sgn * 4.25, 0.02), (56.0, 1.50, 0.10), CONCRETE)
        make_box(f"Curb_{nm}", (-4.0, sgn * 3.6, 0.03), (56.0, 0.20, 0.12), (0.56, 0.56, 0.54, 1.0))
    make_cyl("Bulb_Sidewalk", (BULB_X, 0.0, 0.02), BULB_R + 1.5, 0.10, CONCRETE, segments=24)
    make_cyl("Bulb_Asphalt_Top", (BULB_X, 0.0, -0.02), BULB_R, 0.08, ASPHALT, segments=24)
    # center-line dashes
    for i in range(10):
        make_box(f"Center_Dash_{i}", (-30.0 + i * 5.5, 0.0, 0.001), (2.0, 0.12, 0.01), (0.80, 0.78, 0.60, 1.0))
    # streetlamps that buzz at their subaudible frequency
    for li, lx in enumerate((-22.0, -4.0, 14.0)):
        make_cyl(f"Streetlamp_{li}_Pole", (lx, -4.9, 3.0), 0.08, 6.0, (0.30, 0.30, 0.32, 1.0), segments=8)
        make_box(f"Streetlamp_{li}_Arm", (lx, -4.3, 5.9), (0.08, 1.2, 0.08), (0.30, 0.30, 0.32, 1.0))
        make_box(f"Streetlamp_{li}_Head", (lx, -3.7, 5.8), (0.36, 0.5, 0.16), (0.96, 0.92, 0.78, 1.0))
    # the black cat crossing Prairie View
    make_blob("Black_Cat_Body", (5.0, -1.4, 0.17), 0.20, (0.06, 0.06, 0.07, 1.0), noise=0.18, seed=7, squash=0.7)
    make_cyl("Black_Cat_Tail", (5.34, -1.4, 0.24), 0.02, 0.34, (0.06, 0.06, 0.07, 1.0), axis="X", segments=6)


def build_house(tag, hx, hy, facing, col, lit_window=False, porch_on=False, garage=True, lot_num=None):
    """A 1987-vintage single-story ranch: slab, body, hipped roof, a door
    with a step, two windows, a porch light, a garage door, a driveway
    to the curb, an HOA mailbox at the curb. `facing` is +1 for a house
    that faces south (north lots) and -1 for one that faces north."""
    f = facing
    front_y = hy - f * 4.0
    make_box(f"{tag}_Slab", (hx, hy, 0.06), (10.4, 8.4, 0.12), CONCRETE)
    make_box(f"{tag}_Body", (hx, hy, 1.50), (10.0, 8.0, 2.80), col)
    make_box(f"{tag}_Roof_Low", (hx, hy, 3.05), (10.8, 8.8, 0.30), ROOF)
    make_box(f"{tag}_Roof_Mid", (hx, hy, 3.45), (8.6, 6.4, 0.50), ROOF)
    make_box(f"{tag}_Roof_Cap", (hx, hy, 3.90), (6.0, 3.6, 0.40), ROOF)
    # front door + step + porch light beside it
    make_box(f"{tag}_Door", (hx - 2.0, front_y - f * 0.03, 1.05), (0.95, 0.06, 2.10), (0.42, 0.30, 0.22, 1.0))
    make_box(f"{tag}_Step", (hx - 2.0, front_y - f * 0.55, 0.16), (1.40, 1.00, 0.32), CONCRETE)
    make_box(f"{tag}_Porch_Fixture", (hx - 1.25, front_y - f * 0.09, 2.25), (0.14, 0.12, 0.22),
             BULB_LIGHT if porch_on else (0.86, 0.84, 0.78, 1.0))
    # two windows; one may be lit
    for wi, wx in enumerate((hx + 0.6, hx + 3.6)):
        make_box(f"{tag}_Win_{wi}_Frame", (wx, front_y - f * 0.02, 1.55), (1.60, 0.04, 1.30), TRIM)
        make_box(f"{tag}_Win_{wi}_Glass", (wx, front_y - f * 0.045, 1.55), (1.44, 0.01, 1.14),
                 GLASS_LIT if (lit_window and wi == 1) else GLASS)
    if garage:
        make_box(f"{tag}_Garage_Door", (hx - 4.4, front_y - f * 0.03, 1.15), (2.60, 0.06, 2.20), (0.88, 0.86, 0.82, 1.0))
        for gi in range(3):
            make_box(f"{tag}_Garage_Panel_{gi}", (hx - 4.4, front_y - f * 0.065, 0.55 + gi * 0.62), (2.40, 0.01, 0.10), (0.78, 0.76, 0.72, 1.0))
        drive_len = abs(front_y - f * 4.0) - 0.4
        make_box(f"{tag}_Driveway", (hx - 4.4, (front_y + f * 0.0 - f * (drive_len / 2.0 + 0.2)), 0.015), (3.20, drive_len, 0.03), CONCRETE)
    # lawn + the HOA mailbox at the curb
    make_box(f"{tag}_Lawn", (hx + 1.5, (front_y - f * 4.6 + front_y) / 2.0, 0.006), (8.5, abs(front_y - (front_y - f * 4.6)), 0.012), LAWN)
    make_cyl(f"{tag}_Mailbox_Post", (hx + 5.2, f * 5.1, 0.55), 0.05, 1.10, (0.30, 0.30, 0.32, 1.0), segments=6)
    make_box(f"{tag}_Mailbox", (hx + 5.2, f * 5.1, 1.20), (0.22, 0.48, 0.24), (0.22, 0.26, 0.34, 1.0))
    if lot_num is not None:
        make_box(f"{tag}_Lot_Number", (hx + 5.2, f * (5.1 - 0.25), 1.20), (0.18, 0.004, 0.10), (0.92, 0.90, 0.86, 1.0))


def build_lots():
    # north side: 1402 .. 1428 west to east; Miller is 1428, nearest the bulb
    north = [("Lot1402", -24.0), ("Lot1408", -13.0), ("Lot1414", -2.0), ("Lot1420", 9.0), ("Miller", 20.0)]
    for i, (tag, hx) in enumerate(north):
        build_house(tag, hx, 12.5, +1, HOUSE_COLS[i], lit_window=(tag == "Miller"), porch_on=False, lot_num=1402 + i * 6)
    south = [("Caldwell", -18.0), ("Salinas", -6.0), ("Kowalski", 6.0)]
    for i, (tag, hx) in enumerate(south):
        build_house(tag, hx, -12.5, -1, HOUSE_COLS[5 + i], lit_window=(tag == "Salinas"), porch_on=False, lot_num=None)
    # the car Sammy will drive to school, in the Salinas driveway
    make_box("Salinas_Car_Body", (-10.4, -6.6, 0.62), (1.75, 4.2, 0.62), (0.52, 0.56, 0.60, 1.0))
    make_box("Salinas_Car_Cabin", (-10.4, -6.6, 1.20), (1.65, 2.3, 0.50), (0.44, 0.48, 0.52, 1.0))
    for wi, (wx, wy) in enumerate(((-11.275, -8.0), (-9.525, -8.0), (-11.275, -5.2), (-9.525, -5.2))):
        make_cyl(f"Salinas_Car_Wheel_{wi}", (wx, wy, 0.32), 0.32, 0.25, (0.14, 0.14, 0.15, 1.0), axis="X", segments=10)
    # the Geller house at the end of the cul-de-sac: porch light ON, Don at the window
    build_house("Geller", 31.5, 0.0, +1, HOUSE_COLS[3], lit_window=True, porch_on=True, garage=False)
    make_box("Don_Silhouette", (35.1, -4.6, 1.45), (0.40, 0.30, 0.90), (0.10, 0.10, 0.12, 1.0))
    make_cyl("Don_Silhouette_Head", (35.1, -4.6, 2.05), 0.11, 0.18, (0.10, 0.10, 0.12, 1.0), segments=8)
    make_cyl("Don_Water_Glass", (34.6, -4.75, 1.32), 0.035, 0.09, (0.80, 0.86, 0.90, 0.7), segments=8)


def build_sprinklers():
    """6:12. Lot by lot, traveling east. Each fan: a wet sheet on the
    lawn and a translucent arc standing over it. The Miller head on
    the left corner is cracked: a thin surgical arc that reaches the
    sidewalk, and the grey stripe it has etched there."""
    for i, hx in enumerate((-24.0, -13.0, -2.0, 9.0)):
        make_cyl(f"Sprinkler_Head_{i}", (hx - 3.0, 6.0, 0.03), 0.03, 0.06, (0.24, 0.26, 0.24, 1.0), segments=6)
        make_box(f"Sprinkler_Wet_{i}", (hx - 1.5, 7.2, 0.013), (3.2, 2.2, 0.006), (0.28, 0.40, 0.24, 1.0))
        make_box(f"Sprinkler_Arc_{i}", (hx - 1.5, 6.4, 0.42), (2.8, 0.03, 0.70), (0.82, 0.88, 0.94, 0.35))
    # the Miller head, left corner, cracked housing
    mx = 20.0 - 3.6
    make_cyl("Miller_Cracked_Head", (mx, 5.6, 0.03), 0.03, 0.06, (0.24, 0.26, 0.24, 1.0), segments=6)
    make_box("Miller_Head_Crack", (mx + 0.02, 5.6, 0.06), (0.012, 0.012, 0.02), (0.10, 0.10, 0.10, 1.0))
    make_box("Miller_Thin_Arc", (mx - 0.35, 4.85, 0.55), (0.90, 0.02, 1.00), (0.86, 0.92, 0.98, 0.45))
    make_box("Miller_Arc_Splash", (mx - 0.9, 4.25, 0.075), (0.60, 0.30, 0.004), (0.50, 0.52, 0.56, 1.0))
    make_box("Sidewalk_Etch_Stripe", (mx - 0.9, 4.25, 0.0715), (0.55, 0.10, 0.003), (0.46, 0.46, 0.44, 1.0))


def build_vigil():
    """The white sedan at the curb in the bulb — the reporter and the
    sunburned man, cold coffee from the same thermos."""
    sx, sy = 18.5, -4.6
    make_box("White_Sedan_Body", (sx, sy, 0.62), (4.20, 1.70, 0.60), (0.90, 0.90, 0.88, 1.0))
    make_box("White_Sedan_Cabin", (sx - 0.3, sy, 1.13), (2.20, 1.50, 0.42), (0.82, 0.83, 0.82, 1.0))
    make_box("White_Sedan_Windows", (sx - 0.3, sy + 0.765, 1.15), (1.80, 0.03, 0.30), (0.26, 0.30, 0.36, 1.0))
    for wi, (wx, wy) in enumerate(((sx - 1.4, sy - 0.975), (sx + 1.4, sy - 0.975), (sx - 1.4, sy + 0.975), (sx + 1.4, sy + 0.975))):
        make_cyl(f"White_Sedan_Wheel_{wi}", (wx, wy, 0.33), 0.33, 0.25, (0.14, 0.14, 0.15, 1.0), axis="Y", segments=10)
    make_cyl("Vigil_Thermos", (sx + 0.4, sy + 0.9, 1.0), 0.04, 0.22, (0.32, 0.34, 0.36, 1.0), segments=8)


def build_water_tower():
    """Sixty-two feet, HARMONY CREEK in blue block letters, the NexCorp
    lot's chain-link with green privacy screen at its base and the
    white Residential Solutions van parked beside the fence."""
    tx, ty = 46.0, -38.0
    make_box("Tower_Lot_Pad", (tx, ty, -0.02), (30.0, 26.0, 0.04), (0.40, 0.40, 0.41, 1.0))
    for li in range(4):
        a = li * math.pi / 2.0 + math.pi / 4.0
        make_cyl(f"Water_Tower_Leg_{li}", (tx + 3.2 * math.cos(a), ty + 3.2 * math.sin(a), 6.5), 0.22, 13.0, (0.72, 0.74, 0.76, 1.0), segments=8)
    make_cyl("Water_Tower_Riser", (tx, ty, 6.5), 0.55, 13.0, (0.72, 0.74, 0.76, 1.0), segments=10)
    make_cyl("Water_Tower_Tank", (tx, ty, 16.0), 5.0, 6.0, (0.86, 0.87, 0.86, 1.0), segments=20)
    make_cyl("Water_Tower_Cap", (tx, ty, 19.5), 5.2, 1.0, (0.78, 0.80, 0.80, 1.0), segments=20)
    make_cyl("Water_Tower_Band", (tx, ty, 16.0), 5.03, 1.2, (0.22, 0.38, 0.62, 1.0), segments=20)
    # the NexCorp lot fence with green privacy screen, the van beside it
    for fi, (fx, fy, fw, fd) in enumerate(((tx - 8.0, ty + 9.0, 16.0, 0.10), (tx - 16.0, ty + 1.0, 0.10, 16.0))):
        make_box(f"NexCorp_Fence_{fi}", (fx, fy, 1.1), (fw, fd, 2.2), (0.20, 0.34, 0.24, 1.0))
        make_box(f"NexCorp_Fence_Rail_{fi}", (fx, fy, 2.22), (fw + 0.1, fd + 0.06, 0.06), (0.62, 0.64, 0.66, 1.0))
    make_box("NexCorp_Van_Body", (tx - 12.5, ty + 12.0, 1.05), (2.10, 5.20, 1.60), (0.92, 0.92, 0.90, 1.0))
    make_box("NexCorp_Van_Windows", (tx - 12.5, ty + 12.5, 1.55), (2.14, 1.20, 0.50), (0.28, 0.32, 0.38, 1.0))
    make_box("NexCorp_Van_Stripe", (tx - 11.43, ty + 12.0, 0.85), (0.03, 4.40, 0.22), (0.20, 0.45, 0.48, 1.0))
    for wi, (wx, wy) in enumerate(((tx - 13.675, ty + 10.2), (tx - 11.325, ty + 10.2), (tx - 13.675, ty + 13.8), (tx - 11.325, ty + 13.8))):
        make_cyl(f"NexCorp_Van_Wheel_{wi}", (wx, wy, 0.36), 0.36, 0.25, (0.14, 0.14, 0.15, 1.0), axis="X", segments=10)


def build_horizon():
    make_far_bands("FarTrees", (0.20, 0.26, 0.16),
                   [(90.0, 120.0, 6.0, 0.90), (170.0, 180.0, 8.0, 0.72),
                    (300.0, 280.0, 10.0, 0.55), (500.0, 420.0, 12.0, 0.42)],
                   cx=0.0, cy=0.0, profile="roofline")


def make_car(prefix, cx, cy, length, col, pickup=False, light_bar=False):
    """A car parked along the street (length along x). Body block,
    cabin block, side/front glass plates OUTSIDE the cabin, wheels
    outside the body — nothing intersects."""
    hw = 0.90
    make_box(f"{prefix}_Body", (cx, cy, 0.62), (length, 2 * hw, 0.60), col)
    if pickup:
        make_box(f"{prefix}_Cab", (cx + 0.55, cy, 1.27), (2.0, 2 * hw, 0.70), col)
        make_box(f"{prefix}_Windshield", (cx + 1.56, cy, 1.30), (0.02, 1.60, 0.50), (0.26, 0.30, 0.36, 1.0))
        for sgn, nm in ((1, "N"), (-1, "S")):
            make_box(f"{prefix}_Side_Glass_{nm}", (cx + 0.55, cy + sgn * 0.91, 1.30), (1.70, 0.02, 0.50), (0.26, 0.30, 0.36, 1.0))
            make_box(f"{prefix}_Bed_Side_{nm}", (cx - 1.35, cy + sgn * (hw - 0.02), 1.12), (1.8, 0.04, 0.40), col)
        make_box(f"{prefix}_Tailgate", (cx - length / 2.0 + 0.03, cy, 1.12), (0.06, 2 * hw - 0.10, 0.40), col)
    else:
        make_box(f"{prefix}_Cabin", (cx - 0.20, cy, 1.13), (2.20, 2 * hw - 0.30, 0.42), col)
        make_box(f"{prefix}_Windshield", (cx + 0.91, cy, 1.15), (0.02, 1.40, 0.30), (0.26, 0.30, 0.36, 1.0))
        make_box(f"{prefix}_Rear_Glass", (cx - 1.31, cy, 1.15), (0.02, 1.40, 0.30), (0.26, 0.30, 0.36, 1.0))
        for sgn, nm in ((1, "N"), (-1, "S")):
            make_box(f"{prefix}_Side_Glass_{nm}", (cx - 0.20, cy + sgn * 0.76, 1.15), (1.90, 0.02, 0.30), (0.26, 0.30, 0.36, 1.0))
    if light_bar:
        make_box(f"{prefix}_Light_Bar", (cx - 0.20, cy, 1.40), (0.30, 1.10, 0.12), (0.16, 0.16, 0.18, 1.0))
        make_box(f"{prefix}_Light_Bar_Red", (cx - 0.20, cy + 0.30, 1.40), (0.32, 0.30, 0.13), (0.70, 0.12, 0.10, 1.0))
        make_box(f"{prefix}_Light_Bar_Blue", (cx - 0.20, cy - 0.30, 1.40), (0.32, 0.30, 0.13), (0.14, 0.24, 0.72, 1.0))
    for wi, (wx, wy) in enumerate(((cx - length * 0.32, cy - 1.03), (cx + length * 0.32, cy - 1.03),
                                   (cx - length * 0.32, cy + 1.03), (cx + length * 0.32, cy + 1.03))):
        make_cyl(f"{prefix}_Wheel_{wi}", (wx, wy, 0.33), 0.33, 0.25, (0.14, 0.14, 0.15, 1.0), axis="Y", segments=10)


def build_henderson_2026_09():
    """TWO HOUSES DOWN (vol6 ch5_garage 14+, ch5_miller_drive; re-homed
    off henderson_porch_front 2026-09-03). The Henderson house is lot
    1414. "Ben arrives first. He is in his truck. He parks at the curb.
    He does not pull into the driveway ... Sam arrives second. She is
    in the Corolla. She parks behind Ben's truck. Maya arrives third.
    She is on her bike ... She chains the bike to the light post at
    the end of the driveway." Then Miller: "He stops. He puts the
    patrol vehicle in park. He does not get out." — and from the
    garage, "its single open vent at the top of the door," the
    distorted Telecaster.
    """
    make_car("Ben_Truck", -2.6, 2.4, 5.6, (0.22, 0.34, 0.24, 1.0), pickup=True)
    make_car("Corolla", -11.5, 2.4, 4.3, (0.72, 0.70, 0.64, 1.0))
    make_car("Patrol_Vehicle", -1.0, -1.8, 4.9, (0.92, 0.92, 0.90, 1.0), light_bar=True)
    make_box("Patrol_Door_Stripe", (-1.0, -2.705, 0.62), (2.4, 0.01, 0.30), (0.16, 0.22, 0.40, 1.0))
    # the light post at the end of the Henderson driveway, on the sidewalk edge
    make_cyl("Henderson_Light_Post", (-8.6, 5.3, 1.64), 0.06, 3.14, (0.30, 0.30, 0.32, 1.0), segments=8)
    make_box("Henderson_Light_Post_Head", (-8.6, 5.3, 3.31), (0.30, 0.30, 0.20), (0.96, 0.92, 0.78, 1.0))
    # Maya's bike, chained to the post, wet
    for wi, wy in enumerate((5.0, 6.05)):
        make_cyl(f"Maya_Bike_Wheel_{wi}", (-9.0, wy, 0.40), 0.33, 0.04, (0.14, 0.14, 0.15, 1.0), axis="X", segments=12)
    make_box("Maya_Bike_Frame_Top", (-9.0, 5.52, 0.86), (0.03, 0.62, 0.03), (0.62, 0.22, 0.24, 1.0))
    make_box("Maya_Bike_Frame_Down", (-9.0, 5.52, 0.62), (0.03, 0.46, 0.03), (0.62, 0.22, 0.24, 1.0))
    make_box("Maya_Bike_Seat", (-9.0, 5.25, 0.94), (0.10, 0.20, 0.05), (0.14, 0.14, 0.15, 1.0))
    make_box("Maya_Bike_Bars", (-9.0, 5.90, 0.98), (0.44, 0.03, 0.03), (0.30, 0.30, 0.32, 1.0))
    make_box("Bike_Chain", (-8.80, 5.30, 0.75), (0.34, 0.02, 0.02), (0.36, 0.36, 0.38, 1.0))
    # the garage door's single open vent at the top, the Telecaster light in it
    make_box("Henderson_Garage_Vent", (-6.4, 8.42, 2.12), (0.60, 0.01, 0.10), (0.98, 0.86, 0.58, 1.0))
    make_box("Henderson_Vent_Slats", (-6.4, 8.412, 2.12), (0.56, 0.002, 0.08), (0.72, 0.62, 0.42, 1.0))
    # rain has mostly stopped: a puddle at the foot of the drive, the wet sheen on the truck's hood
    make_box("Driveway_Puddle", (-6.0, 4.6, 0.0705), (1.6, 0.9, 0.001), (0.34, 0.36, 0.40, 1.0))
    make_box("Truck_Hood_Sheen", (-0.5, 2.4, 0.9205), (1.6, 1.2, 0.001), (0.30, 0.42, 0.34, 1.0))


def main():
    clear_scene()
    build_street()
    build_lots()
    build_sprinklers()
    build_vigil()
    build_water_tower()
    build_henderson_2026_09()
    build_horizon()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/meadowlark_circle.glb"))
    print(f"\n[build_meadowlark_circle] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
