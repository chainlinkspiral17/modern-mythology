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

DRAFT 2 (2026-10-30, the diamond and the sky): the Little League field
is built at its real size (60 ft bases, a 200 ft fence) with its home plate
by the water, the backstop, both dugouts and bleachers, the chalk, the
mound, six light towers burning and a dark scoreboard. The shores run
300 m back. The turn's stars are point-sized, 340 of them. The text gives
that night no moon, so there is none.

DRAFT 3 targets: the diamond's light pooling on the grass (SpotLights from
the six banks, not four omnis); a cap of moths in the light; the river's
reflections as the streetlights' long smears;
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
    make_cyl(f"{name}_H", (x, y, z + 1.36 * h + 0.12), 0.11, 0.24,  # on the torso, not 2 cm over it
             (0.80, 0.64, 0.52, 1.0), segments=8)


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
    make_box("River_Water_Bright", (RX, 150.0, 0.005), (30.0, 110.0, 0.01), RIVER_BRIGHT)
    # the shores come in only where the things go by (y -60..280)
    # (2026-10-30) 300 m deep, not 60: the ball field runs to x +105 and the
    # back edge stood in frame as a step on the horizon
    for sg, bx in ((1, RX + 20.0), (-1, RX - 22.0)):
        make_box(f"Shore_{'E' if sg > 0 else 'W'}", (bx + sg * 150.0, 110.0, 0.2), (300.0, 340.0, 0.6), (0.16, 0.18, 0.14, 1.0))
    # the streetlights whose reflections turned into the water, along the east bank
    for k in range(12):
        py = -50.0 + k * 28.0
        make_cyl(f"RiverLamp_Stock_{k}", (RX + 21.5, py, 3.6), 0.07, 7.0, (0.24, 0.24, 0.26, 1.0), segments=6)
        make_box(f"RiverLamp_Stock_{k}_Head", (RX + 20.7, py, 7.05), (1.6, 0.30, 0.16), (1.0, 0.86, 0.56, 1.0))
    # "A strip mall."
    # on the bank (its top is at 0.5), 2026-10-30
    make_box("StripMall", (RX + 36.0, 25.0, 2.9), (14.0, 46.0, 4.8), (0.66, 0.60, 0.52, 1.0))
    make_box("StripMall_Canopy", (RX + 28.0, 25.0, 4.1), (2.4, 46.0, 0.24), (0.30, 0.28, 0.30, 1.0))
    for k in range(5):
        make_box(f"StripMall_Window_{k}", (RX + 28.98, 7.0 + k * 9.0, 1.9), (0.04, 6.4, 2.2), (0.96, 0.86, 0.60, 1.0))
        make_box(f"StripMall_Sign_{k}", (RX + 28.98, 7.0 + k * 9.0, 3.6), (0.04, 5.0, 0.6), ((0.86, 0.30, 0.30, 1.0), (0.30, 0.60, 0.86, 1.0), (0.90, 0.80, 0.30, 1.0), (0.40, 0.80, 0.50, 1.0), (0.80, 0.50, 0.80, 1.0))[k])
    # the figure on the bank, hailing a cab
    _figure("Hitchhiker", RX + 20.8, 52.0, 0.5, (0.36, 0.36, 0.40, 1.0))
    make_rot_box("Hitchhiker_Arm", (RX + 20.6, 52.0, 2.1), (0.10, 0.10, 0.70), (0.36, 0.36, 0.40, 1.0), pitch=-0.5)
    # "A Little League diamond with the lights still on." (draft 2, 2026-10-30:
    # it was a 46 m grass square with a fence arc 25 m out). Now a Little
    # League field at its real size, 60 ft bases and a 200 ft fence, built
    # BIG. Home plate is by the water so the river sees it past the backstop.
    # The foul lines run east (first base) and north (third base) so the
    # dugouts, bleachers and side fences sit square. Six light towers burn
    # over an empty field.
    build_diamond(RX)
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
    make_box("Drugstore_Sign", (RX, sy - 5.03, 4.0), (10.0, 0.06, 0.9), (0.86, 0.16, 0.18, 1.0))
    make_box("Drugstore_Roof", (RX, sy + 1.0, 4.7), (20.6, 12.6, 0.2), (0.30, 0.30, 0.32, 1.0))
    # "It's also a gas station: pumps outside on the water, a methane torch
    # burning on a pole, a bucket of filthy window-wash fluid by the door."
    make_box("Drugstore_Apron", (RX, sy - 10.0, 0.45), (16.0, 6.0, 0.3), (0.50, 0.46, 0.40, 1.0))
    for k, px in enumerate((RX - 4.0, RX + 4.0)):
        make_box(f"Drugstore_Pump_{k}", (px, sy - 10.0, 1.3), (0.7, 0.5, 1.4), (0.86, 0.86, 0.84, 1.0))
        make_box(f"Drugstore_Pump_{k}_Face", (px, sy - 10.26, 1.5), (0.5, 0.02, 0.4), (0.30, 0.60, 0.40, 1.0))
    # the pole stands on the apron's corner (it stood in the river off it, 2026-10-30)
    make_cyl("Methane_Torch_Pole", (RX + 7.6, sy - 12.4, 4.3), 0.10, 7.4, (0.30, 0.30, 0.32, 1.0), segments=6)
    make_taper_cyl("Methane_Torch_Flame", (RX + 7.6, sy - 12.4, 8.6), 0.30, 0.02, 1.2, (1.0, 0.62, 0.20, 1.0), segments=7)
    make_cyl("Washfluid_Bucket", (RX - 2.2, sy - 5.6, 0.78), 0.18, 0.36, (0.22, 0.34, 0.30, 1.0), segments=10)
    # Judgement Day riding low, a boat now — and again, on the turn, heading south
    for tag, jy, heading in (("Jd", 0.0, "N"), ("JdTurn", -310.0, "S")):
        make_car(f"{tag}_Judgement_Day", RX, jy, 4.70, MAROON, along="Y" if heading == "N" else "-Y", z0=-0.42)
        make_box(f"{tag}_Judgement_Day_Primer", (RX - 0.885, jy + 0.6, 0.20), (0.006, 0.80, 0.30), (0.56, 0.56, 0.54, 1.0))
        make_box(f"{tag}_Wake", (RX, jy + (-4.5 if heading == "N" else 4.5), 0.01), (2.4, 4.0, 0.01), (0.26, 0.34, 0.40, 1.0))
    # far south, the bank coming back: Club #, a door with the lights low
    make_box("FarBank_S", (RX, -660.0, 0.2), (700.0, 30.0, 0.6), (0.12, 0.13, 0.12, 1.0))
    make_box("Club_Building", (RX, -652.0, 4.0), (14.0, 10.0, 7.0), (0.14, 0.13, 0.16, 1.0))
    make_box("Club_Doorway_Glow", (RX, -646.96, 1.7), (1.2, 0.04, 2.2), (1.0, 0.82, 0.56, 1.0))
    # (2026-10-30, the turn's draft 2: the frame was a car on a flat purple
    # plain) "Out in the middle of the river it's very quiet. There's no shore
    # on either side." / "Then it's just a bright smudge, then a star." /
    # "The river starts to move. There's current now" / "Up ahead ... Club #,
    # with no line and no sign, just a door." — stars over the open water,
    # the current drawn in streaks past the boat, the door's light laid down
    # the water all the way to the boat so the far door reads
    import random as _r
    rnd = _r.Random(15)
    # (2026-10-30, draft 3) the stars were 4-9 m cubes at 600 m, each as wide
    # as the moon. Now there are 240, most 2-3 px (a pixel here is ~0.9 m at
    # 600 m; at 1-2 px the ink outline eats the star and leaves a dark
    # speck), a few brighter and a few tinted. The text gives that night no moon.
    for k in range(240):
        az = rnd.uniform(-math.pi * 0.95, math.pi * 0.95) - math.pi / 2.0      # around the south
        el = math.asin(rnd.uniform(math.sin(0.06), math.sin(1.35)))
        R = 600.0
        x = RX + R * math.cos(el) * math.cos(az)
        y = -300.0 + R * math.cos(el) * math.sin(az)
        z = R * math.sin(el)
        s = rnd.choice((2.2, 2.2, 2.2, 2.6, 2.6, 3.0, 3.0, 3.6, 4.4))
        tint = rnd.choice(((1.0, 1.0, 1.0, 1.0),) * 6 + ((0.80, 0.86, 1.0, 1.0), (1.0, 0.90, 0.76, 1.0)))
        make_box(f"Turn_Sky_Star_Stock_{k}", (x, y, z), (s, s, s), tint)  # Sky_: in the sky by design
    for k in range(28):
        sx = RX + rnd.uniform(-9.0, 9.0)
        sy = -312.0 - rnd.uniform(0.0, 70.0)
        make_box(f"Turn_Current_Stock_{k}", (sx, sy, 0.004), (0.10 + rnd.random() * 0.12, rnd.uniform(1.5, 5.0), 0.004),
                 (0.62, 0.64, 0.92, 1.0))
    make_box("Turn_Door_Reflection", (RX, -488.0, 0.003), (1.6, 312.0, 0.004), (1.0, 0.82, 0.56, 1.0))
    make_box("Turn_Door_Reflection_Near", (RX, -352.0, 0.0035), (0.7, 40.0, 0.004), (1.0, 0.92, 0.74, 1.0))


def build_diamond(RX):
    """The Little League field on the east bank (draft 2, 2026-10-30)."""
    DIRT = (0.58, 0.40, 0.27, 1.0)
    INGRASS = (0.31, 0.50, 0.26, 1.0)
    CHALK = (0.94, 0.94, 0.90, 1.0)
    FENCE = (0.14, 0.26, 0.20, 1.0)       # green windscreen on the chain link
    CAP = (0.96, 0.82, 0.16, 1.0)         # the yellow fence cap and foul poles
    GALV = (0.56, 0.58, 0.60, 1.0)
    BLOCK = (0.70, 0.68, 0.62, 1.0)
    ROOF = (0.20, 0.34, 0.26, 1.0)
    LAMP = (1.0, 0.98, 0.90, 1.0)
    HX, HY, Z0 = RX + 41.0, 66.0, 0.54
    BASE = 18.29                          # 60 ft
    FR = 61.0                             # 200 ft to the fence

    def fp(u, v):
        return (HX + u, HY + v)

    def lbox(name, side, t0, t1, o0, o1, z0, z1, col):
        """A box in a foul line's frame: t along the line from home, o out
        into foul territory. side +1 is first base (east, out is south),
        -1 is third base (north, out is west)."""
        tc, oc = (t0 + t1) / 2.0, (o0 + o1) / 2.0
        if side > 0:
            c, sz = fp(tc, -oc), (t1 - t0, o1 - o0, z1 - z0)
        else:
            c, sz = fp(-oc, tc), (o1 - o0, t1 - t0, z1 - z0)
        make_box(name, (c[0], c[1], (z0 + z1) / 2.0), sz, col)

    # the outfield grass, on the bank (its top at 0.5); clear of the strip mall
    make_box("Diamond_Grass", (RX + 64.5, 91.0, 0.52), (81.0, 82.0, 0.04), (0.28, 0.46, 0.24, 1.0))
    # the skinned infield: a 50 ft dirt circle round the mound, the infield
    # grass inside the base paths, the dirt circle at home
    mx, my = fp(BASE * 0.5418, BASE * 0.5418)            # the rubber at 46 ft
    make_cyl("Diamond_Infield", (mx, my, 0.545), 15.24, 0.02, DIRT, segments=40)
    make_box("Diamond_InfieldGrass", (*fp(9.6, 9.6), 0.556), (14.6, 14.6, 0.02), INGRASS)
    make_cyl("Diamond_HomeCircle", (*fp(0.0, 0.0), 0.548), 3.2, 0.02, DIRT, segments=24)
    make_cyl("Diamond_Mound", (mx, my, 0.60), 1.6, 0.14, DIRT, segments=20)
    make_rot_box("Diamond_Rubber", (mx, my, 0.675), (0.61, 0.15, 0.02), CHALK, yaw=-math.pi / 4.0)
    make_rot_box("Diamond_HomePlate", (*fp(0.0, 0.0), 0.562), (0.43, 0.43, 0.012), CHALK, yaw=math.pi / 4.0)
    for k, (bu, bv) in enumerate(((BASE - 0.19, 0.19), (BASE, BASE), (0.19, BASE - 0.19))):
        make_box(f"Diamond_Base_{k + 1}", (*fp(bu, bv), 0.585), (0.38, 0.38, 0.06), CHALK)
    # the foul lines, home to the poles, and the batter's boxes
    make_box("Diamond_Chalk_Stock_1B", (*fp(FR / 2.0 + 0.3, 0.0), 0.562), (FR - 0.6, 0.08, 0.012), CHALK)
    make_box("Diamond_Chalk_Stock_3B", (*fp(0.0, FR / 2.0 + 0.3), 0.562), (0.08, FR - 0.6, 0.012), CHALK)
    # each box 3 x 6 ft, its long sides along the home-second line (a), one
    # either side of the plate across it (p)
    au, av, pu, pv = 0.7071, 0.7071, 0.7071, -0.7071
    for sd in (-1, 1):
        cu, cv = sd * 0.92 * pu, sd * 0.92 * pv
        edges = ((cu + 0.455 * pu, cv + 0.455 * pv, 1.83, -math.pi / 4.0),
                 (cu - 0.455 * pu, cv - 0.455 * pv, 1.83, -math.pi / 4.0),
                 (cu + 0.915 * au, cv + 0.915 * av, 0.91, math.pi / 4.0),
                 (cu - 0.915 * au, cv - 0.915 * av, 0.91, math.pi / 4.0))
        for k, (ou, ov, L, yw) in enumerate(edges):
            make_rot_box(f"Diamond_Chalk_Stock_Box_{sd:+d}_{k}", (*fp(ou, ov), 0.562), (0.06, L, 0.012), CHALK, yaw=yw)
    # the outfield fence: chain link in a green windscreen, the yellow cap,
    # an arc 200 ft from home that runs past the poles to meet the side fences
    th0, th1 = math.radians(-8.5), math.radians(98.5)
    n = 45
    seg = FR * (th1 - th0) / n
    for k in range(n):
        th = th0 + (k + 0.5) * (th1 - th0) / n
        c = fp(FR * math.cos(th), FR * math.sin(th))
        make_rot_box(f"Diamond_Fence_Stock_{k}", (c[0], c[1], Z0 + 0.915), (0.05, seg + 0.06, 1.83), FENCE, yaw=th)
        make_rot_box(f"Diamond_FenceCap_Stock_{k}", (c[0], c[1], Z0 + 1.86), (0.09, seg + 0.06, 0.06), CAP, yaw=th)
    for k, th in enumerate((0.0, math.pi / 2.0)):
        make_cyl(f"Diamond_FoulPole_{k}", (*fp((FR + 0.13) * math.cos(th), (FR + 0.13) * math.sin(th)), Z0 + 6.0),
                 0.10, 12.0, CAP, segments=8)
    # the backstop: a 6 m chain-link screen behind home, its wings running
    # out along both lines. Posts, rails, and the wire drawn as a 0.5 m grid
    # you can see the infield through.
    A, B = fp(-9.0, -2.0), fp(-2.0, -9.0)
    L = math.hypot(B[0] - A[0], B[1] - A[1])
    for k in range(int(L / 0.5) + 1):
        f = k / int(L / 0.5)
        make_box(f"Diamond_Backstop_Stock_V_{k}", (A[0] + (B[0] - A[0]) * f, A[1] + (B[1] - A[1]) * f, Z0 + 3.0),
                 (0.04, 0.04, 6.0), GALV)
    for k in range(13):
        make_rot_box(f"Diamond_Backstop_Stock_H_{k}", ((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0, Z0 + 0.25 + k * 0.48),
                     (0.04, L, 0.04), GALV, yaw=math.pi / 4.0)
    for k, (px, py) in enumerate((A, B)):
        make_cyl(f"Diamond_Backstop_Post_{k}", (px, py, Z0 + 3.05), 0.06, 6.1, GALV, segments=8)
    for side in (1, -1):
        # the wing: from the screen's corner out to t = 8 along the line, 3.6 m
        for k in range(21):
            t = -2.0 + k * 0.5
            lbox(f"Diamond_Backstop_Stock_W{side:+d}_V_{k}", side, t - 0.02, t + 0.02, 8.98, 9.02, Z0, Z0 + 3.6, GALV)
        for k in range(8):
            lbox(f"Diamond_Backstop_Stock_W{side:+d}_H_{k}", side, -2.0, 8.0, 8.98, 9.02, Z0 + 0.25 + k * 0.48, Z0 + 0.29 + k * 0.48, GALV)
        lbox(f"Diamond_Backstop_Stock_W{side:+d}_Rail", side, -2.0, 8.0, 8.96, 9.04, Z0 + 3.56, Z0 + 3.64, GALV)
        # the dugout: block back and ends, a green roof, a bench, a cooler
        D = f"Diamond_Dugout_{'1B' if side > 0 else '3B'}"
        lbox(f"{D}_Floor", side, 9.0, 19.0, 9.0, 11.4, Z0, Z0 + 0.05, (0.56, 0.55, 0.52, 1.0))
        lbox(f"{D}_Back", side, 9.0, 19.0, 11.2, 11.4, Z0, Z0 + 2.3, BLOCK)
        lbox(f"{D}_End_0", side, 9.0, 9.2, 9.0, 11.2, Z0, Z0 + 2.3, BLOCK)
        lbox(f"{D}_End_1", side, 18.8, 19.0, 9.0, 11.2, Z0, Z0 + 2.3, BLOCK)
        lbox(f"{D}_Roof", side, 8.9, 19.1, 8.8, 11.5, Z0 + 2.3, Z0 + 2.42, ROOF)
        lbox(f"{D}_Front_Fence", side, 9.2, 18.8, 9.0, 9.04, Z0 + 0.05, Z0 + 1.05, FENCE)
        lbox(f"{D}_Bench", side, 9.6, 18.4, 10.8, 11.2, Z0 + 0.05, Z0 + 0.48, (0.52, 0.40, 0.26, 1.0))
        cu, cv = (17.9, -10.2) if side > 0 else (-10.2, 17.9)
        make_cyl(f"{D}_Cooler", (*fp(cu, cv), Z0 + 0.27), 0.18, 0.44, (0.92, 0.46, 0.14, 1.0), segments=12)
        # the bleachers behind it: three aluminium steps
        for i in range(3):
            lbox(f"Diamond_Bleacher_{'1B' if side > 0 else '3B'}_Step_{i}", side, 9.0, 19.0,
                 11.6 + i * 0.8, 12.4 + i * 0.8, Z0, Z0 + 0.42 * (i + 1), GALV)
            lbox(f"Diamond_Bleacher_{'1B' if side > 0 else '3B'}_Plank_{i}", side, 9.0, 19.0,
                 11.65 + i * 0.8, 11.95 + i * 0.8, Z0 + 0.42 * (i + 1), Z0 + 0.42 * (i + 1) + 0.04, (0.80, 0.82, 0.84, 1.0))
        # the side fence on from the gate to the outfield arc
        lbox(f"Diamond_SideFence_{'1B' if side > 0 else '3B'}", side, 20.5, 60.4, 9.0, 9.05, Z0, Z0 + 1.22, FENCE)
    # six light towers, every one still burning, their banks turned to the field
    cx, cy = fp(28.0, 28.0)
    for k, (u, v) in enumerate(((4.0, -13.0), (-13.0, 4.0), (38.0, -12.0), (-12.0, 38.0),
                                (67.0 * math.cos(math.radians(25)), 67.0 * math.sin(math.radians(25))),
                                (67.0 * math.cos(math.radians(65)), 67.0 * math.sin(math.radians(65))))):
        px, py = fp(u, v)
        make_cyl(f"Diamond_Pole_{k}", (px, py, Z0 + 9.0), 0.22, 18.0, (0.36, 0.36, 0.38, 1.0), segments=8)
        yw = math.atan2(cy - py, cx - px) + math.pi / 2.0
        make_rot_box(f"Diamond_Lamps_{k}_Frame", (px, py, Z0 + 18.6), (2.8, 0.30, 1.5), (0.92, 0.88, 0.76, 1.0), yaw=yw)  # its housing glows from behind too
        dx, dy = (cx - px), (cy - py)
        d = math.hypot(dx, dy)
        make_rot_box(f"Diamond_Lamps_{k}", (px + dx / d * 0.20, py + dy / d * 0.20, Z0 + 18.6), (2.6, 0.12, 1.3), LAMP, yaw=yw)
    # the scoreboard over left-centre, dark but for its lamps
    sc = fp(66.0 * 0.7071, 66.0 * 0.7071)
    make_rot_box("Diamond_Scoreboard", (sc[0], sc[1], Z0 + 4.3), (6.0, 0.25, 2.6), (0.10, 0.20, 0.14, 1.0), yaw=-math.pi / 4.0 + math.pi)
    for sg in (-1, 1):
        make_cyl(f"Diamond_Scoreboard_Post_{sg:+d}", (sc[0] + sg * 2.6 * 0.7071 + 0.245 * 0.7071, sc[1] - sg * 2.6 * 0.7071 + 0.245 * 0.7071, Z0 + 2.8),
                 0.12, 5.6, GALV, segments=8)
    for k in range(6):
        f = -2.2 + k * 0.88
        make_rot_box(f"Diamond_Scoreboard_Lamp_Stock_{k}", (sc[0] + f * 0.7071 - 0.135 * 0.7071, sc[1] - f * 0.7071 - 0.135 * 0.7071, Z0 + 3.6),
                     (0.36, 0.02, 0.36), (1.0, 0.70, 0.30, 1.0) if k % 2 == 0 else (0.30, 0.20, 0.10, 1.0), yaw=-math.pi / 4.0)
    make_rot_box("Diamond_Scoreboard_Band", (sc[0] - 0.135 * 0.7071, sc[1] - 0.135 * 0.7071, Z0 + 5.15), (5.2, 0.02, 0.30), CHALK, yaw=-math.pi / 4.0)


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
