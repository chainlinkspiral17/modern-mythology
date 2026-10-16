"""gallatin_water_tower — the south end of Gallatin Avenue, Harmony Creek, at
6:19 AM (vol6 ch0 "Prelude", "The Water Tower").

NEW SET (2026-10-10). The segment played on Meadowlark Circle, where the
tower is a landmark off to the south-east. The prose is up close:

  "The Harmony Creek water tower stands at the south end of Gallatin Avenue,
  behind the NexCorp lot, which is currently enclosed in a chain-link fence
  with green privacy screen. The water tower is sixty-two feet tall. It was
  painted in 2019 with the words HARMONY CREEK in blue block letters and a
  small rendering of a creek that does not resemble the actual creek." ·
  "At 6:19, a white NexCorp Residential Solutions van is parked beside the
  fence. The engine is off. No one gets out." · "He ... looks at the green
  privacy screen on the fence, behind which the machines have already begun
  their work for the day."

  · GALLATIN AVENUE running south to its dead end: two lanes, the curbs and
    sidewalks, a few small houses with their lawns, the utility poles, the
    street sign, the dead-end sign.
  · THE NEXCORP LOT across the road's end: chain-link on its posts with the
    green privacy screen, the gate with its padlocked chain and the NexCorp
    construction sign; over the screen the machines — an excavator's arm
    and cab, the spoil mounds, a light tower, the site trailer's roof.
  · THE WATER TOWER behind the lot: 62 ft (18.9 m) to the tank's top; four
    raked legs with their bracing, the ladder, the riser; the tank with
    HARMONY CREEK in blue block letters and the small painted creek.
  · THE VAN beside the fence: white, the NexCorp Residential Solutions band
    and logo on its side.

Coordinate frame: Blender Z-up; Gallatin runs along y, its dead end at the
fence (y = -40); the lot and the tower beyond (y < -40). glTF export remaps
to Godot (x, z, -y).

Draft 2 targets: Henderson's silhouette in the passenger seat; the
machines' work-lights on at 6:19; dew on the screen; a dog walker.
"""
import math
import os
import random
import sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_rot_box, make_blob, export_glb

FENCE_Y = -40.0
COL_ASPHALT = (0.30, 0.30, 0.31, 1.0)
COL_CONCRETE = (0.68, 0.67, 0.64, 1.0)
COL_GRASS = (0.34, 0.44, 0.24, 1.0)
COL_DIRT = (0.56, 0.44, 0.32, 1.0)
COL_SCREEN = (0.16, 0.34, 0.22, 1.0)
COL_STEEL = (0.62, 0.64, 0.66, 1.0)
COL_TANK = (0.86, 0.88, 0.88, 1.0)
COL_BLUE = (0.16, 0.34, 0.66, 1.0)
COL_YELLOW = (0.94, 0.72, 0.14, 1.0)
COL_WHITE = (0.94, 0.94, 0.92, 1.0)
COL_DARK = (0.16, 0.16, 0.18, 1.0)


def build_street():
    make_box("Ground_Lawns", (0.0, -30.0, -0.06), (200.0, 160.0, 0.04), COL_GRASS)
    make_box("Gallatin_Road", (0.0, -10.0, -0.025), (8.0, 60.0, 0.05), COL_ASPHALT)
    make_box("Gallatin_Road_Centerline", (0.0, -10.0, 0.004), (0.12, 60.0, 0.01), (0.92, 0.80, 0.20, 1.0))
    for s in (-1, 1):
        make_box(f"Gallatin_Curb_{s:+d}", (s * 4.08, -10.0, 0.06), (0.16, 60.0, 0.15), COL_CONCRETE)
        make_box(f"Gallatin_Sidewalk_{s:+d}", (s * 5.6, -10.0, 0.06), (1.6, 60.0, 0.12), COL_CONCRETE)
    # the small houses along Gallatin and their lawns
    rnd = random.Random(19)
    for k, (hx, hy) in enumerate(((-14.0, 12.0), (-14.0, -4.0), (-14.0, -20.0), (14.0, 8.0), (14.0, -8.0), (14.0, -24.0))):
        w, d, h = 9.0, 8.0, rnd.uniform(3.2, 4.0)
        col = ((0.80, 0.74, 0.62, 1.0), (0.66, 0.72, 0.70, 1.0), (0.84, 0.82, 0.76, 1.0))[k % 3]
        make_box(f"House_{k}_Facade", (hx, hy, h / 2.0), (w, d, h), col)
        hd = w / 4.0 + 0.25
        rz = h + hd * math.sin(0.40) + 0.08 - 0.02
        for e in (-1, 1):   # a gable along y, the eaves on the long walls
            make_rot_box(f"House_{k}_Roof_{'E' if e > 0 else 'W'}", (hx + e * w / 4.0, hy, rz), (2.0 * hd, d + 0.6, 0.16), (0.34, 0.32, 0.30, 1.0), pitch=-e * 0.40)
        make_box(f"House_{k}_Door", (hx - (w / 2.0 + 0.01) * (1 if hx > 0 else -1), hy, 1.02), (0.02, 0.90, 2.04), (0.36, 0.26, 0.22, 1.0))
        side = 1.0 if hx > 0 else -1.0
        make_box(f"House_{k}_Driveway", (side * 7.95, hy + 2.5, -0.035), (3.1, 3.0, 0.03), COL_CONCRETE)   # sidewalk to the house front
    for k, (tx, ty) in enumerate(((-9.5, 4.0), (9.5, 0.0), (-9.5, -14.0), (9.5, -18.0), (-20.0, -32.0))):
        make_cyl(f"Street_Tree_{k}_Trunk", (tx, ty, 1.8), 0.22, 3.6, (0.36, 0.28, 0.22, 1.0), segments=8)
        make_blob(f"Street_Tree_{k}_Crown", (tx, ty, 5.0), 2.6, (0.26, 0.40, 0.22, 1.0), noise=0.22, seed=50 + k, squash=0.7)
    # the utility poles down the W side, the street sign, the dead-end sign
    for k in range(4):
        py = 14.0 - k * 16.0
        make_cyl(f"Utility_Pole_{k}", (-6.8, py, 4.5), 0.14, 9.0, (0.40, 0.32, 0.24, 1.0), segments=6)
        make_box(f"Utility_Pole_{k}_Crossarm", (-6.8, py, 8.6), (1.6, 0.12, 0.12), (0.40, 0.32, 0.24, 1.0))
    make_cyl("Street_Sign_Post", (5.2, 2.0, 1.4), 0.03, 2.8, COL_STEEL, segments=6)
    make_box("Street_Sign_Gallatin", (5.2, 2.0, 2.70), (0.04, 0.80, 0.18), (0.12, 0.42, 0.24, 1.0))
    make_cyl("Dead_End_Sign_Post", (4.6, -34.0, 1.2), 0.03, 2.4, COL_STEEL, segments=6)
    make_rot_box("Dead_End_Sign", (4.6, -34.03, 2.25), (0.60, 0.02, 0.60), COL_YELLOW, yaw=0.0, roll=0.0)
    make_box("Dead_End_Sign_Text", (4.6, -34.042, 2.25), (0.40, 0.002, 0.10), COL_DARK)
    make_box("Road_End_Barrier", (0.0, FENCE_Y + 2.2, 0.55), (8.0, 0.20, 0.30), (0.94, 0.94, 0.92, 1.0))
    for e in (-1, 1):
        make_box(f"Road_End_Barrier_Post_{e:+d}", (e * 3.6, FENCE_Y + 2.2, 0.35), (0.12, 0.12, 0.70), (0.50, 0.50, 0.50, 1.0))


def build_lot():
    """The NexCorp lot: chain-link with the green privacy screen, the gate, the
    machines over the screen."""
    x0, x1 = -32.0, 32.0
    y1 = FENCE_Y - 52.0
    make_box("Lot_Ground_Dirt", (0.0, (FENCE_Y + y1) / 2.0, -0.04), (x1 - x0, FENCE_Y - y1, 0.04), COL_DIRT)
    # the fence: posts, top rail, the screen on the street side, a gate in the middle
    n = int((x1 - x0) / 2.5)
    for k in range(n + 1):
        px = x0 + k * (x1 - x0) / n
        if -2.6 < px < 2.6:
            continue
        make_cyl(f"Fence_Post_{k}", (px, FENCE_Y, 1.0), 0.04, 2.0, COL_STEEL, segments=6)
    for nm, a, b in (("W", x0, -2.6), ("E", 2.6, x1)):
        make_box(f"Fence_Rail_{nm}", ((a + b) / 2.0, FENCE_Y, 1.98), (b - a, 0.05, 0.05), COL_STEEL)
        make_box(f"Fence_Screen_{nm}", ((a + b) / 2.0, FENCE_Y + 0.05, 0.95), (b - a, 0.02, 1.80), COL_SCREEN)
    for e in (-1, 1):
        make_cyl(f"Fence_Gate_Post_{e:+d}", (e * 2.6, FENCE_Y, 1.05), 0.06, 2.1, COL_STEEL, segments=8)
        make_box(f"Fence_Gate_{e:+d}", (e * 1.30, FENCE_Y + 0.02, 1.0), (2.50, 0.04, 1.90), COL_SCREEN)
    make_box("Fence_Gate_Chain", (0.0, FENCE_Y + 0.06, 1.05), (0.30, 0.03, 0.12), COL_STEEL)
    make_box("Fence_Gate_Padlock", (0.0, FENCE_Y + 0.08, 0.98), (0.06, 0.03, 0.08), (0.70, 0.60, 0.30, 1.0))
    make_box("Fence_Sign_NexCorp", (-6.0, FENCE_Y + 0.07, 1.20), (2.40, 0.02, 1.00), COL_WHITE)
    make_box("Fence_Sign_NexCorp_Band", (-6.0, FENCE_Y + 0.082, 1.45), (2.20, 0.004, 0.24), (0.18, 0.32, 0.50, 1.0))
    make_box("Fence_Sign_NexCorp_Text", (-6.0, FENCE_Y + 0.082, 1.05), (1.80, 0.004, 0.40), (0.30, 0.30, 0.32, 1.0))
    for nm, a, b in (("Side_W", FENCE_Y, y1), ("Side_E", FENCE_Y, y1)):
        sx = x0 if nm.endswith("W") else x1
        make_box(f"Fence_Screen_{nm}", (sx, (a + b) / 2.0, 0.95), (0.02, a - b, 1.80), COL_SCREEN)
    # over the screen: the spoil mounds, the excavator, the light tower, the trailer
    for k, (mx, my, r) in enumerate(((-12.0, -64.0, 5.0), (-26.0, -74.0, 6.5), (18.0, -62.0, 4.5))):
        make_blob(f"Spoil_Hump_{k}", (mx, my, 0.4), r, COL_DIRT, noise=0.18, seed=70 + k, squash=0.45)   # spoil heaps: dirt set into the ground
    ex, ey = 8.0, -48.0
    make_box("Excavator_Tracks", (ex, ey, 0.45), (3.2, 4.4, 0.90), COL_DARK)
    make_box("Excavator_Cab", (ex - 0.4, ey, 1.85), (2.6, 2.8, 1.90), COL_YELLOW)
    make_box("Excavator_Cab_Glass", (ex - 1.71, ey + 0.4, 2.20), (0.02, 1.2, 1.00), (0.30, 0.36, 0.40, 1.0))
    make_rot_box("Excavator_Boom_Beam", (ex + 2.6, ey - 2.2, 4.3), (0.50, 0.50, 4.6), COL_YELLOW, pitch=0.70, roll=0.35)
    make_rot_box("Excavator_Stick_Beam", (ex + 4.3, ey - 3.6, 2.2), (0.40, 0.40, 3.4), COL_YELLOW, pitch=-0.30, roll=0.20)
    make_box("Excavator_Bucket", (ex + 4.75, ey - 3.95, 0.35), (1.0, 0.8, 0.7), COL_DARK)   # down in the ground, digging
    make_box("Site_Trailer", (-20.0, -50.0, 1.40), (10.0, 3.2, 2.80), COL_WHITE)
    make_box("Site_Trailer_Skirt", (-20.0, -50.0, 0.10), (10.0, 3.2, 0.20), COL_DARK)
    make_cyl("Site_Lights_Mast", (2.0, -47.0, 4.5), 0.10, 9.0, COL_STEEL, segments=6)
    make_box("Site_Lights_Head", (2.0, -47.0, 9.1), (1.8, 0.30, 0.60), COL_DARK)
    make_box("Site_Lights_Base", (2.0, -47.0, 0.55), (1.4, 2.4, 1.10), COL_YELLOW)


def build_water_tower():
    """62 ft to the top: four raked legs, the bracing, the riser, the ladder, the tank."""
    tx, ty = 4.0, -74.0
    top = 18.9
    tank_h, tank_r = 6.4, 5.2
    leg_top = top - tank_h + 0.20            # into the tank's flare, a joint not a clip
    leg_base = 0.30                          # the legs start on the footings
    for k, a in enumerate((45, 135, 225, 315)):
        ar = math.radians(a)
        fx, fy = tx + 4.6 * math.cos(ar), ty + 4.6 * math.sin(ar)       # the foot
        hx, hy = tx + 3.4 * math.cos(ar), ty + 3.4 * math.sin(ar)       # under the tank
        rise = leg_top - leg_base
        L = math.hypot(math.hypot(fx - hx, fy - hy), rise)
        rake = math.atan2(math.hypot(fx - hx, fy - hy), rise)
        # tilt the leg inward: pitch/roll from the rake toward the tower's axis
        make_rot_box(f"Water_Tower_Leg_{k}", ((fx + hx) / 2.0, (fy + hy) / 2.0, (leg_base + leg_top) / 2.0), (0.36, 0.36, L), COL_STEEL,
                     pitch=-rake * math.cos(ar), roll=rake * math.sin(ar))
        make_box(f"Water_Tower_Footing_{k}", (fx, fy, 0.15), (1.0, 1.0, 0.30), (0.62, 0.62, 0.60, 1.0))
    for k, z in enumerate((4.0, 8.0)):
        rr = 4.6 - (4.6 - 3.4) * z / leg_top
        for e, ax in enumerate(('X', 'Y')):
            size = (2.0 * rr * 0.71 * 2.0, 0.12, 0.12) if ax == 'X' else (0.12, 2.0 * rr * 0.71 * 2.0, 0.12)
            make_box(f"Water_Tower_Brace_{k}_{ax}", (tx, ty, z), size, COL_STEEL)
    make_cyl("Water_Tower_Riser", (tx, ty, leg_top / 2.0), 0.55, leg_top, COL_STEEL, segments=12)
    make_box("Water_Tower_Ladder", (tx + 0.58, ty, leg_top / 2.0 + 0.3), (0.06, 0.50, leg_top - 0.6), COL_DARK)
    zt = top - tank_h
    make_lathe("Water_Tower_Tank", (tx, ty, zt), [(0.0, 0.0), (3.0, 0.2), (tank_r, 1.6), (tank_r, 4.4), (3.6, 5.8), (0.6, tank_h), (0.0, tank_h)],
               COL_TANK, segments=24)
    make_cyl("Water_Tower_Finial", (tx, ty, top + 0.35), 0.18, 0.7, COL_STEEL, segments=8)
    make_cyl("Water_Tower_Catwalk", (tx, ty, zt + 1.55), tank_r + 0.55, 0.10, COL_STEEL, segments=24)
    # HARMONY CREEK in blue block letters, on the street-facing face (toward +y)
    face_y = ty + tank_r + 0.02
    letters = "HARMONY CREEK"
    for i, ch in enumerate(letters):
        if ch == " ":
            continue
        a = (i - (len(letters) - 1) / 2.0) * 0.14         # around the drum
        lx, ly = tx + (tank_r + 0.02) * math.sin(a), ty + (tank_r + 0.02) * math.cos(a)
        make_rot_box(f"Water_Tower_Letter_{i}", (lx, ly, zt + 3.4), (0.50, 0.06, 0.80), COL_BLUE, yaw=-a)
    # the small painted creek under the words: a wave of blue segments
    for i in range(9):
        a = (i - 4) * 0.10
        lx, ly = tx + (tank_r + 0.02) * math.sin(a), ty + (tank_r + 0.02) * math.cos(a)
        make_rot_box(f"Water_Tower_Creek_{i}", (lx, ly, zt + 2.35 + 0.18 * math.sin(i * 1.3)), (0.56, 0.05, 0.12), (0.30, 0.56, 0.84, 1.0), yaw=-a)


def build_van():
    """The white NexCorp Residential Solutions van beside the fence, engine off."""
    vx, vy = -9.5, FENCE_Y + 2.6
    L, W, H = 5.6, 2.0, 2.3
    make_box("Van_Body", (vx, vy, 0.40 + (H - 0.40) / 2.0), (L, W, H - 0.40), COL_WHITE)
    make_box("Van_Hood", (vx + L / 2.0 + 0.40, vy, 0.40 + 0.50), (0.80, W - 0.04, 1.00), COL_WHITE)
    make_rot_box("Van_Windshield", (vx + L / 2.0 + 0.14, vy, 1.62), (0.02, W - 0.16, 0.90), (0.36, 0.42, 0.48, 1.0), pitch=0.42)
    for s in (-1, 1):
        make_box(f"Van_Cab_Window_{s:+d}", (vx + L / 2.0 - 0.45, vy + s * (W / 2.0 + 0.005), 1.70), (0.80, 0.01, 0.62), (0.36, 0.42, 0.48, 1.0))
        make_box(f"Van_Band_{s:+d}", (vx - 0.4, vy + s * (W / 2.0 + 0.006), 1.10), (L - 1.6, 0.01, 0.34), (0.18, 0.32, 0.50, 1.0))
        make_box(f"Van_Logo_{s:+d}", (vx - 0.4, vy + s * (W / 2.0 + 0.008), 1.60), (1.6, 0.006, 0.30), (0.18, 0.32, 0.50, 1.0))
        for e in (-1, 1):
            make_cyl(f"Van_Wheel_{s:+d}_{e:+d}", (vx + e * (L / 2.0 - 0.8) + (0.4 if e > 0 else 0.0), vy + s * (W / 2.0 - 0.12), 0.38), 0.38, 0.24, COL_DARK, segments=14, axis='Y')
    make_box("Van_Bumper_F", (vx + L / 2.0 + 0.82, vy, 0.50), (0.08, W, 0.20), COL_DARK)
    make_box("Van_Bumper_R", (vx - L / 2.0 - 0.04, vy, 0.50), (0.08, W, 0.20), COL_DARK)


def main():
    clear_scene()
    build_street()
    build_lot()
    build_water_tower()
    build_van()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/gallatin_water_tower.glb"))
    print(f"\n[build_gallatin_water_tower] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
