"""houston_bayou — vol 1's Houston outside, 2010s, "weird and fantastical"
(draft 1, 2026-10-27).

Andy (2026-10-27): "vol 1 is 2010s Houston but weird and fantastical";
"Houston and New Orleans interiors can be similar" — so Jacob's apartment
keeps its set, but vol 1's park and its river played on vol 5's Graustark
riverfront (a Gulf Coast bayou town) and now have their own:

  ch2 the park: "EXT. THE PARK — DAY"; "Faust is jogging with his friend,
   Jacob"; "Cut back to the jogging." — Houston's jogging park is Buffalo
   Bayou: the trail along the water, the live oaks, the pedestrian bridge,
   downtown standing over the trees              → houston_park_day
  ch10 the river: "The street outside the windshield goes soft and wet.
   Streetlights stretch into long reflections and the reflections turn into
   water. Judgement Day isn't on a road anymore."; "On the shore, things go
   by. A strip mall. A Little League diamond with the lights still on."; "A
   figure on the bank raises a hand like he's hailing a cab."; "A toll gate
   rises out of it, an old wooden arm painted red and white, a booth with
   nobody in it."; "The water goes still and very flat and very bright, a
   fluorescent kind of bright, and up ahead a building sits on the water with
   every light on."                                 → jd_river
  ch15 the turn: "Behind them the drugstore glows and gets smaller"; "Out in
   the middle of the river it's very quiet. There's no shore on either side.";
   "on the bank, there's a building with the lights low: Club #, with no line
   and no sign, just a door."                       → jd_river_turn

Judgement Day is club_street's beat-up maroon sedan with the primer patch,
riding low in the water like a boat. PROPOSED: the park's particular bridge,
the skyline's towers (generic 2010s Houston, no real building copied), every
shore building.

Blender: x east, y north, z up; Godot (x, z, -y). The park at x 0 (the bayou
running east-west on y 0, downtown east), the dream river at x +3000
(running north; its shore things y 0..240, open water south to y -650).

DRAFT 2 targets: the river's reflections as the streetlights' long smears;
the tanooki leaf; the drugstore's interior through its glass; joggers with a
pose; the skyline's lit windows at dusk; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_taper_cyl, make_rot_box,
                             make_tube, join_stock, export_glb)
from _props.trees import make_broadleaf
from _props.vehicles import make_car

GRASS = (0.30, 0.44, 0.22, 1.0)
GRASS2 = (0.26, 0.38, 0.20, 1.0)
BAYOU = (0.22, 0.26, 0.18, 1.0)
CONC = (0.64, 0.62, 0.58, 1.0)
ASPHALT = (0.18, 0.18, 0.20, 1.0)
OAK = (0.20, 0.32, 0.18, 1.0)
BARK = (0.30, 0.24, 0.20, 1.0)
GLASS_T = (0.36, 0.46, 0.56, 1.0)
RIVER = (0.12, 0.20, 0.30, 1.0)
RIVER_BRIGHT = (0.70, 0.86, 0.84, 1.0)
MAROON = (0.40, 0.18, 0.16, 1.0)


def _rng(seed):
    s = [seed & 0x7fffffff or 1]
    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7fffffff
        return s[0] / 0x7fffffff
    return r


def _figure(name, x, y, z, coat, h=1.0):
    make_box(f"{name}_L", (x, y, z + 0.38 * h), (0.28, 0.22, 0.76 * h), (0.18, 0.18, 0.22, 1.0))
    make_box(f"{name}_T", (x, y, z + 1.06 * h), (0.42, 0.26, 0.60 * h), coat)
    make_cyl(f"{name}_H", (x, y, z + 1.50 * h), 0.11, 0.24, (0.80, 0.64, 0.52, 1.0), segments=8)


# ── the park: Buffalo Bayou by day ─────────────────────────────────────
def build_park():
    make_box("Park_Ground", (0.0, 0.0, -0.06), (900.0, 600.0, 0.04), GRASS2)
    # the bayou sunk 3 m between sloping banks
    make_box("Bayou_Water", (0.0, 0.0, -2.9), (900.0, 20.0, 0.1), BAYOU)
    make_box("Bayou_Bed", (0.0, 0.0, -3.4), (900.0, 22.0, 0.6), (0.24, 0.20, 0.14, 1.0))
    run, rise = 12.0, 3.0
    pitch = math.atan2(rise, run)
    for sg in (-1, 1):
        make_rot_box(f"Bayou_Bank_{'S' if sg < 0 else 'N'}", (0.0, sg * (10.0 + run / 2.0), -1.5), (900.0, math.hypot(run, rise) + 0.2, 0.3),
                     GRASS, roll=sg * pitch)
        make_box(f"Bayou_Top_{'S' if sg < 0 else 'N'}", (0.0, sg * 60.0, -0.03), (900.0, 76.0, 0.04), GRASS)
    # the trail on the south bank, the parkway on the north
    make_box("Trail", (0.0, -26.0, 0.01), (900.0, 3.0, 0.04), CONC)
    make_box("Trail_Edge", (0.0, -24.4, 0.02), (900.0, 0.2, 0.06), (0.52, 0.50, 0.46, 1.0))
    make_box("Parkway", (0.0, 44.0, 0.0), (900.0, 14.0, 0.04), ASPHALT)
    make_box("Parkway_Line", (0.0, 44.0, 0.022), (900.0, 0.14, 0.01), (0.86, 0.74, 0.30, 1.0))
    # lamps along the trail
    for k in range(16):
        px = -300.0 + k * 40.0
        make_cyl(f"Trail_Lamp_Stock_{k}", (px, -28.2, 1.9), 0.06, 3.8, (0.20, 0.22, 0.24, 1.0), segments=6)
        make_cyl(f"Trail_Lamp_Stock_{k}_Head", (px, -28.2, 3.9), 0.18, 0.25, (0.92, 0.90, 0.80, 1.0), segments=8)
    # live oaks both banks, crepe myrtles by the trail
    r = _rng(713)
    k = 0
    for sg, y0, y1 in ((-1, -60.0, -30.0), (1, 22.0, 34.0), (1, 54.0, 90.0)):
        for _ in range(26):
            make_broadleaf(f"Oak_Stock_{k}", -300.0 + r() * 600.0, y0 + r() * (y1 - y0), 9.0 + r() * 6.0, OAK, BARK)
            k += 1
    # the pedestrian bridge: a white arched truss across the bayou
    bx = 60.0
    make_box("Bridge_Deck", (bx, 0.0, 0.6), (3.6, 50.0, 0.3), CONC)
    for sx in (-1, 1):
        pts = [(bx + sx * 1.9, -25.0 + i * 2.5, 0.8 + 5.0 * math.sin(math.pi * i / 20.0)) for i in range(21)]
        make_tube(f"Bridge_Arch_{sx:+d}", pts, 0.22, (0.92, 0.92, 0.90, 1.0), segments=8)
        for i in range(1, 20, 2):
            make_tube(f"Bridge_Hanger_{sx:+d}_{i}", [pts[i], (pts[i][0], pts[i][1], 0.8)], 0.04, (0.92, 0.92, 0.90, 1.0), segments=5)
        make_box(f"Bridge_Rail_{sx:+d}", (bx + sx * 1.75, 0.0, 1.8), (0.06, 50.0, 0.06), (0.80, 0.80, 0.78, 1.0))
    # joggers and a cyclist on the trail
    for i, (jx, coat) in enumerate(((-60.0, (0.80, 0.24, 0.24, 1.0)), (-12.0, (0.20, 0.42, 0.70, 1.0)), (34.0, (0.92, 0.90, 0.30, 1.0)),
                                    (90.0, (0.30, 0.30, 0.34, 1.0)))):
        _figure(f"Jogger_{i}", jx, -26.0 + (i % 2) * 0.8, 0.02, coat)


def build_skyline():
    """Downtown 1.2-1.7 km east over the trees: 2010s glass towers, two of
    them with their tops cut on a slant, one with a pyramid crown. Generic —
    no real tower copied."""
    r = _rng(2014)
    for k in range(26):
        tx = 1150.0 + r() * 500.0
        ty = -220.0 + r() * 440.0
        w = 28.0 + r() * 34.0
        h = 70.0 + r() ** 1.6 * 240.0
        col = GLASS_T if k % 3 else (0.50, 0.52, 0.54, 1.0)
        make_box(f"Tower_Stock_{k}", (tx, ty, h / 2.0), (w, w * (0.8 + r() * 0.4), h), col)
        if k % 7 == 0:
            make_taper_cyl(f"Tower_Stock_{k}_Crown", (tx, ty, h + w * 0.3), w * 0.72, 0.5, w * 0.6, (0.46, 0.48, 0.50, 1.0), segments=4)
        elif k % 5 == 0:
            make_rot_box(f"Tower_Stock_{k}_Slant", (tx, ty, h + w * 0.18), (w * 1.02, w * 0.9, w * 0.2), col, roll=0.35)


# ── the dream river at night ──────────────────────────────────────────
def build_river():
    RX = 3000.0
    make_box("River_Water", (RX, -200.0, -0.05), (700.0, 1100.0, 0.1), RIVER)
    # "a fluorescent kind of bright": the flat water at the toll and on to the drugstore
    make_box("River_Bright", (RX, 150.0, 0.005), (30.0, 110.0, 0.01), RIVER_BRIGHT)
    # the shores come in only where the things go by (y -60..280)
    for sg, bx in ((1, RX + 20.0), (-1, RX - 22.0)):
        make_box(f"Shore_{'E' if sg > 0 else 'W'}", (bx + sg * 30.0, 110.0, 0.2), (60.0, 340.0, 0.6), (0.16, 0.18, 0.14, 1.0))
    # the streetlights whose reflections turned into the water, along the east bank
    for k in range(12):
        py = -50.0 + k * 28.0
        make_cyl(f"RiverLamp_Stock_{k}", (RX + 21.5, py, 3.6), 0.07, 7.0, (0.24, 0.24, 0.26, 1.0), segments=6)
        make_box(f"RiverLamp_Stock_{k}_Head", (RX + 20.7, py, 7.05), (1.6, 0.30, 0.16), (1.0, 0.86, 0.56, 1.0))
    # "A strip mall."
    make_box("StripMall", (RX + 36.0, 25.0, 2.4), (14.0, 46.0, 4.8), (0.66, 0.60, 0.52, 1.0))
    make_box("StripMall_Canopy", (RX + 28.0, 25.0, 3.6), (2.4, 46.0, 0.24), (0.30, 0.28, 0.30, 1.0))
    for k in range(5):
        make_box(f"StripMall_Window_{k}", (RX + 28.95, 7.0 + k * 9.0, 1.4), (0.04, 6.4, 2.2), (0.96, 0.86, 0.60, 1.0))
        make_box(f"StripMall_Sign_{k}", (RX + 28.92, 7.0 + k * 9.0, 3.1), (0.04, 5.0, 0.6), ((0.86, 0.30, 0.30, 1.0), (0.30, 0.60, 0.86, 1.0), (0.90, 0.80, 0.30, 1.0), (0.40, 0.80, 0.50, 1.0), (0.80, 0.50, 0.80, 1.0))[k])
    # the figure on the bank, hailing a cab
    _figure("Hitchhiker", RX + 20.8, 52.0, 0.5, (0.36, 0.36, 0.40, 1.0))
    make_rot_box("Hitchhiker_Arm", (RX + 20.6, 52.0, 2.1), (0.10, 0.10, 0.70), (0.36, 0.36, 0.40, 1.0), pitch=-0.5)
    # "A Little League diamond with the lights still on."
    dx, dy = RX + 48.0, 75.0
    make_box("Diamond_Grass", (dx, dy, 0.52), (46.0, 46.0, 0.04), (0.28, 0.46, 0.24, 1.0))
    make_rot_box("Diamond_Infield", (dx - 10.0, dy, 0.545), (17.0, 17.0, 0.02), (0.56, 0.40, 0.28, 1.0), yaw=math.pi / 4)
    make_rot_box("Diamond_InfieldGrass", (dx - 10.0, dy, 0.556), (11.0, 11.0, 0.02), (0.30, 0.50, 0.26, 1.0), yaw=math.pi / 4)
    for k in range(9):
        a = -math.pi / 2 + k * math.pi / 8
        make_box(f"Diamond_Fence_{k}", (dx - 10.0 + 30.0 * math.cos(a) * 0.0 + 26.0 * math.cos(a + math.pi), dy + 26.0 * math.sin(a + math.pi), 1.3),
                 (0.06, 9.0, 1.6), (0.46, 0.48, 0.48, 1.0))
    for k, (lx, ly) in enumerate(((dx - 24.0, dy - 20.0), (dx - 24.0, dy + 20.0), (dx + 20.0, dy - 22.0), (dx + 20.0, dy + 22.0))):
        make_cyl(f"Diamond_Pole_{k}", (lx, ly, 7.5), 0.18, 14.0, (0.36, 0.36, 0.38, 1.0), segments=8)
        make_box(f"Diamond_Lamps_{k}", (lx, ly, 14.6), (1.2, 1.2, 0.8), (1.0, 0.98, 0.90, 1.0))
    # "A toll gate rises out of it, an old wooden arm painted red and white, a booth with nobody in it."
    ty = 95.0
    make_box("Toll_Island", (RX + 9.0, ty, 0.25), (4.0, 6.0, 0.5), CONC)
    make_box("Toll_Booth", (RX + 9.0, ty, 1.7), (2.4, 2.4, 2.4), (0.80, 0.78, 0.72, 1.0))
    make_box("Toll_Booth_Window", (RX + 7.78, ty, 1.9), (0.04, 1.8, 1.0), (0.40, 0.50, 0.54, 1.0))
    make_box("Toll_Booth_Roof", (RX + 9.0, ty, 3.0), (3.0, 3.0, 0.2), (0.70, 0.18, 0.16, 1.0))
    make_box("Toll_Post", (RX + 7.6, ty - 2.0, 0.8), (0.4, 0.4, 1.6), (0.80, 0.78, 0.72, 1.0))
    for k in range(8):
        make_box(f"Toll_Arm_{k}", (RX + 7.0 - k * 1.25, ty - 2.0, 1.45), (1.25, 0.14, 0.14),
                 (0.86, 0.12, 0.10, 1.0) if k % 2 == 0 else (0.94, 0.94, 0.92, 1.0))
    # "a building sits on the water with every light on": the drugstore on its piles
    sy = 160.0
    for i in range(4):
        for j in range(3):
            make_cyl(f"Drug_Pile_{i}_{j}", (RX - 9.0 + i * 6.0, sy - 6.0 + j * 6.0, -0.5), 0.3, 1.8, (0.30, 0.26, 0.22, 1.0), segments=8)
    make_box("Drugstore_Deck", (RX, sy, 0.45), (22.0, 16.0, 0.3), (0.50, 0.46, 0.40, 1.0))
    make_box("Drugstore", (RX, sy + 1.0, 2.6), (20.0, 12.0, 4.0), (0.88, 0.88, 0.86, 1.0))
    for k in range(5):
        make_box(f"Drugstore_Window_{k}", (RX - 8.0 + k * 4.0, sy - 5.02, 2.0), (3.4, 0.04, 2.2), (1.0, 0.98, 0.90, 1.0))
    make_box("Drugstore_Sign", (RX, sy - 5.06, 4.0), (10.0, 0.06, 0.9), (0.86, 0.16, 0.18, 1.0))
    make_box("Drugstore_Roof", (RX, sy + 1.0, 4.7), (20.6, 12.6, 0.2), (0.30, 0.30, 0.32, 1.0))
    # "It's also a gas station: pumps outside on the water, a methane torch
    # burning on a pole, a bucket of filthy window-wash fluid by the door."
    make_box("Drugstore_Apron", (RX, sy - 10.0, 0.45), (16.0, 6.0, 0.3), (0.50, 0.46, 0.40, 1.0))
    for k, px in enumerate((RX - 4.0, RX + 4.0)):
        make_box(f"Drugstore_Pump_{k}", (px, sy - 10.0, 1.3), (0.7, 0.5, 1.4), (0.86, 0.86, 0.84, 1.0))
        make_box(f"Drugstore_Pump_{k}_Face", (px, sy - 10.26, 1.5), (0.5, 0.02, 0.4), (0.30, 0.60, 0.40, 1.0))
    make_cyl("Methane_Torch_Pole", (RX + 9.0, sy - 11.0, 4.0), 0.10, 7.4, (0.30, 0.30, 0.32, 1.0), segments=6)
    make_taper_cyl("Methane_Torch_Flame", (RX + 9.0, sy - 11.0, 8.2), 0.30, 0.02, 1.2, (1.0, 0.62, 0.20, 1.0), segments=7)
    make_cyl("Washfluid_Bucket", (RX - 2.2, sy - 5.6, 0.78), 0.18, 0.36, (0.22, 0.34, 0.30, 1.0), segments=10)
    # Judgement Day riding low, a boat now — and again, on the turn, heading south
    for tag, jy, heading in (("Jd", 0.0, "N"), ("JdTurn", -310.0, "S")):
        make_car(f"{tag}_Judgement_Day", RX, jy, 4.70, MAROON, along="Y" if heading == "N" else "-Y", z0=-0.42)
        make_box(f"{tag}_Judgement_Day_Primer", (RX - 0.885, jy + 0.6, 0.20), (0.006, 0.80, 0.30), (0.56, 0.56, 0.54, 1.0))
        make_box(f"{tag}_Wake", (RX, jy + (-4.5 if heading == "N" else 4.5), 0.01), (2.4, 4.0, 0.01), (0.26, 0.34, 0.40, 1.0))
    # far south, the bank coming back: Club #, a door with the lights low
    make_box("FarBank_S", (RX, -660.0, 0.2), (700.0, 30.0, 0.6), (0.12, 0.13, 0.12, 1.0))
    make_box("Club_Building", (RX, -652.0, 3.5), (14.0, 10.0, 7.0), (0.14, 0.13, 0.16, 1.0))
    make_box("Club_Doorway_Glow", (RX, -646.96, 1.2), (1.2, 0.04, 2.2), (1.0, 0.82, 0.56, 1.0))
    # (2026-10-30, the turn's draft 2: the frame was a car on a flat purple
    # plain) "Out in the middle of the river it's very quiet. There's no shore
    # on either side." / "Then it's just a bright smudge, then a star." /
    # "The river starts to move. There's current now" / "Up ahead ... Club #,
    # with no line and no sign, just a door." — stars over the open water,
    # the current drawn in streaks past the boat, the door's light laid down
    # the water all the way to the boat so the far door reads
    import random as _r
    rnd = _r.Random(15)
    for k in range(90):
        az = rnd.uniform(-math.pi * 0.95, math.pi * 0.95) - math.pi / 2.0      # around the south
        el = rnd.uniform(0.10, 0.95)
        R = 600.0
        x = RX + R * math.cos(el) * math.cos(az)
        y = -300.0 + R * math.cos(el) * math.sin(az)
        z = R * math.sin(el)
        s = rnd.choice((4.0, 5.5, 7.0, 9.0))
        make_box(f"Turn_Star_Stock_{k}", (x, y, z), (s, s, s), (1.0, 1.0, 1.0, 1.0))
    for k in range(28):
        sx = RX + rnd.uniform(-9.0, 9.0)
        sy = -312.0 - rnd.uniform(0.0, 70.0)
        make_box(f"Turn_Current_Stock_{k}", (sx, sy, 0.004), (0.10 + rnd.random() * 0.12, rnd.uniform(1.5, 5.0), 0.004),
                 (0.62, 0.64, 0.92, 1.0))
    make_box("Turn_Door_Reflection", (RX, -488.0, 0.003), (1.6, 312.0, 0.004), (1.0, 0.82, 0.56, 1.0))
    make_box("Turn_Door_Reflection_Near", (RX, -352.0, 0.0035), (0.7, 40.0, 0.004), (1.0, 0.92, 0.74, 1.0))


def main():
    clear_scene()
    build_park()
    build_skyline()
    build_river()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/houston_bayou.glb"))
    print(f"\n[build_houston_bayou] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
