"""highway_101 — the coast highway north of Yachats, vol7 ch22 (The
Drive). New 2026-09-03.

"The road north of Yachats was a two-lane state highway running close
to the coast. The cedars on the inland side were the cedars Tem had
been at the cabin in for thirty-one years. The ocean on the seaward
side ..." "The turn for the old-Yachats bluff was not signed. The road
had been bypassed thirty years ago. A green metal road-marker reading
Old Yachats Road sat at the turn with a chain across it the way roads
get when they have been county-decommissioned."

The seaward side is WEST: a guardrail on posts, the bluff top falling
away past it to the cliff edge (x -15, 5 m down), the drop to the
water, the swell line at the foot, the Pacific out to a gray horizon.
Inland is a wall of cedars and a rock cut. Ahead, the old-Yachats
headland stands out into the sea (pass 475: a heightfield, cliffs all
round, cedar to the cliff tops); the decommissioned turn with its chain
and marker at y 160, Old Yachats Road climbing the headland from it.

Presets (Background3D):
  highway_101        dusk · the truck's hood height (1.15) on the
                      northbound lane, the ocean left, cedars right,
                      the headland ahead · 62°
  highway_101_turn   dusk · at the chained turn, eye 1.6, NW at the
                      chain and the green marker, the old road
                      climbing into the cedars, the sea left · 52°

Coordinate frame: Blender Z-up. Highway N-S along y at x 0, ±1200.
Sea level z -22. glTF export remaps to Godot (x, z, -y).
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_wedge, make_tube, make_lathe, catenary, export_glb
from _props.detail import make_far_bands
from _props.trees import make_conifer
from _props.vehicles import make_car
from _props.detail import make_guardrail, make_road_bend

ASPHALT = (0.24, 0.24, 0.25, 1.0)
SHOULDER = (0.44, 0.42, 0.36, 1.0)
GRAVEL = (0.56, 0.52, 0.46, 1.0)
ROCK = (0.34, 0.33, 0.32, 1.0)
ROCK_DK = (0.26, 0.26, 0.26, 1.0)
CEDAR = (0.14, 0.26, 0.18, 1.0)
CEDAR_LT = (0.20, 0.32, 0.22, 1.0)
TRUNK = (0.34, 0.24, 0.16, 1.0)
SEA = (0.30, 0.40, 0.44, 1.0)
FOAM = (0.82, 0.86, 0.86, 1.0)
STEEL = (0.62, 0.64, 0.66, 1.0)
SALAL = (0.24, 0.36, 0.22, 1.0)
SEA_Z = -22.0
ROAD_FAR, ROAD_NEAR = 1200.0, -1200.0


def build_road():
    BEND_Y = 250.0
    span = (BEND_Y - ROAD_NEAR)
    mid = (BEND_Y + ROAD_NEAR) / 2.0
    # the land the road sits on: a shelf, rock below it to the sea
    # (pass 475) the land stops at the bluff edge, x -15: it ran 1,140 m west
    # over the sea at z -0.06 and the Pacific never drew — the coast road
    # read as a road across a green plain to the horizon
    make_box("Ground_Far", (627.0, 0.0, -0.06), (1266.0, 2600.0, 0.02), (0.20, 0.28, 0.20, 1.0))
    make_box("Roadbed", (2.0, mid, -0.5), (16.0, span, 0.9), ROCK_DK)
    make_box("Road_Asphalt", (0.0, mid, 0.0), (7.2, span, 0.04), ASPHALT)
    di = 0
    dy = ROAD_NEAR
    while dy < BEND_Y - 1.0:
        make_box(f"Road_CenterLine_{di}", (0.0, dy, 0.022), (0.10, 1.50, 0.005), (0.92, 0.86, 0.50, 1.0))
        dy += 12.0
        di += 1
    for sgn in (-1, +1):
        # 2026-09-27 (the 09-26 sheet, dusk establish): fresh white paint
        # was the brightest thing in the frame — a blazing line up the
        # shoulder while the centre dashes and the rail sat in the dusk.
        # Coast fog lines are worn grey-white; the paint takes the light
        # the way the rail does now.
        make_box(f"Road_EdgeLine_{sgn:+d}", (sgn * 3.4, mid, 0.022), (0.08, span, 0.005), (0.66, 0.66, 0.62, 1.0))
        make_box(f"Road_Shoulder_{sgn:+d}", (sgn * 4.3, mid, 0.01), (1.4, span, 0.02), SHOULDER)
    # the seaward guardrail: W-beam on posts (a gap at the old-Yachats spur, y 155..165)
    make_guardrail("Guardrail_S", -5.4, ROAD_NEAR, 154.75, side=1, steel=STEEL)
    make_guardrail("Guardrail_N", -5.4, 165.25, BEND_Y, side=1, steel=STEEL)
    # the highway bends inland around the headland: 28 degrees east, then the run
    make_road_bend("Road_Bend", 0.0, BEND_Y, 0.0, 28.0, 140.0, 900.0, 7.2, asphalt=ASPHALT, line=(0.92, 0.86, 0.50, 1.0),
                   edge=(0.92, 0.92, 0.88, 1.0), shoulder_w=1.4, shoulder=SHOULDER, seg_len=10.0)
    # the drop to the sea: a long wedge falling west from the shelf
    # (pass 475) south of the headland and north of it; the headland's own
    # cliffs are its terrain (build_headland_2026_11). The bluff's top meets
    # the ground at -0.05 (it stopped 0.9 m short of it).
    # Past the rail the bluff top FALLS AWAY (x -6 at -0.05 to x -15 at -5),
    # then the cliff: from the hood at 1.15 m a level top hid every metre of
    # water up to the headland.
    for nm, y0, y1 in (("", ROAD_NEAR, 122.0), ("_North", 618.0, 1300.0)):
        make_wedge("Bluff_Ground" + nm, (-10.5, (y0 + y1) / 2.0, (-0.05 + BLUFF_TOP_DROP) / 2.0), (9.0, y1 - y0, -0.05 - BLUFF_TOP_DROP),
                   (0.22, 0.30, 0.20, 1.0), high_end="+X")
        make_wedge("Sea_Bluff" + nm, (-27.0, (y0 + y1) / 2.0, (SEA_Z + BLUFF_TOP_DROP) / 2.0), (24.0, y1 - y0, BLUFF_TOP_DROP - SEA_Z), ROCK, high_end="+X")
    # (2026-11-01) out to the horizon: 260 m of sea ended in a haze slab whose
    # top read as a ledge once the far plane let it draw
    make_box("Sea", (-1515.0, 0.0, SEA_Z - 0.05), (3000.0, 4000.0, 0.10), SEA)
    for nm, y0, y1 in (("", -1300.0, 122.0), ("_North", 618.0, 1300.0)):     # (pass 475) round the headland in its own pass
        make_box("Swell_Line" + nm, (-40.6, (y0 + y1) / 2.0, SEA_Z + 0.012), (1.0, y1 - y0, 0.024), FOAM)
        make_box("Swell_Line_2" + nm, (-43.2, (y0 + y1) / 2.0, SEA_Z + 0.006), (0.6, y1 - y0, 0.012), FOAM)
    # sea stacks
    for i, (x, y, r, s) in enumerate(((-58.0, 90.0, 6.0, 1), (-236.0, 300.0, 8.0, 2), (-52.0, -140.0, 5.0, 3), (-74.0, 592.0, 7.0, 4))):
        # seated in the water (they hung 0.4 r above it: 1.6 r up, 1.2 r tall)
        make_blob(f"Sea_Stack_{i}", (x, y, SEA_Z + r * 0.9), r, ROCK, noise=0.30, seed=s, squash=1.2)


def build_inland():
    """Cedars in a wall east of the road, a rock cut where the highway
    was straightened, salal at the foot of the trees."""
    cedars = []
    for i in range(0, 80):
        y = -240.0 + i * 6.0
        h = 18.0 + (i * 5) % 7 * 1.4
        # (pass 475) set back to road clearance: at x 9 a cedar's lowest
        # tier (radius 0.3 h, 5.4-8.5 m) hung over the shoulder, and the
        # drive preset's right third was one black crown. Its edge now stops
        # past the verge (x >= ~5.6), the way a state highway is kept.
        x = 5.6 + h * 0.32 + (i * 7) % 4 * 1.2
        cedars.append((x, y, h))
        if i % 3 == 0:
            cedars.append((x + 8.0 + (i % 5), y + 2.5, h - 3.0))
    for i, (x, y, h) in enumerate(cedars):
        if 15.0 < y < 145.0:
            continue      # the rock cut and the hill it is cut into
        make_conifer(f"Cedar_{i}", x, y, h, CEDAR if i % 2 else CEDAR_LT, TRUNK)
    import random as _random
    rnd_hill = _random.Random(4752)
    make_box("Rock_Cut", (10.5, 80.0, 6.0), (6.0, 80.0, 12.0), ROCK)
    make_box("Rock_Cut_Face_Band", (7.49, 80.0, 3.0), (0.02, 80.0, 1.2), ROCK_DK)
    # (pass 475) the cut's ENDS: the hill it was blasted through rises to it,
    # so the cut grows from nothing over 12 m at each end — its square end
    # faces stood 12 m tall toward the drive preset, flat grey walls
    # (a 24 m taper, ~27 degrees, in forest floor: at 12 m it was a 45-degree
    # plane the dusk lit as one orange triangle) wooded and broken up
    HILL = (0.22, 0.24, 0.17, 1.0)
    make_wedge("Rock_Cut_Hill_S", (10.5, 28.0, 6.0), (6.0, 24.0, 12.0), HILL, high_end='+Y')
    make_wedge("Rock_Cut_Hill_N", (10.5, 132.0, 6.0), (6.0, 24.0, 12.0), HILL, high_end='-Y')
    hill_z = lambda hy: (hy - 16.0) * 0.5 if hy < 80.0 else (144.0 - hy) * 0.5
    for i, (hx, hy, hh) in enumerate(((10.2, 19.5, 13.0), (12.4, 23.0, 15.0), (9.8, 27.0, 12.5), (12.0, 31.0, 14.0),
                                      (10.3, 35.0, 13.5), (12.8, 38.0, 15.5),
                                      (12.6, 122.0, 15.0), (10.1, 125.5, 13.0), (12.2, 129.5, 14.5),
                                      (9.9, 133.0, 12.0), (12.5, 137.0, 15.0), (10.4, 140.5, 13.0))):
        make_conifer(f"Rock_Cut_Hill_Tree_{i}", hx, hy, hh, CEDAR if i % 2 else CEDAR_LT, TRUNK, z0=hill_z(hy) - 0.4)
    for i in range(20):
        hy = rnd_hill.uniform(17.0, 39.0) if i < 10 else rnd_hill.uniform(121.0, 143.0)
        r = rnd_hill.uniform(0.6, 1.2)
        make_blob(f"Rock_Cut_Hill_Salal_{i}", (rnd_hill.uniform(8.6, 13.0), hy, hill_z(hy) + r * 0.2), r,
                  SALAL if i % 3 else (0.20, 0.30, 0.19, 1.0), noise=0.3, seed=2700 + i, rings=3, segments=7, squash=0.5)
    for i in range(10):
        make_blob(f"Rock_Cut_Rubble_{i}", (6.4, 44.0 + i * 8.0, 0.33), 0.5, ROCK_DK, noise=0.3, seed=20 + i, squash=0.7)   # seated by its squashed height (2026-09-24: a blob's half-height is radius x squash)
    for i in range(24):
        y = -230.0 + i * 20.0
        if 40.0 < y < 120.0:
            continue
        make_blob(f"Salal_{i}", (6.6, y, 0.47), 0.9, SALAL, noise=0.26, seed=50 + i, squash=0.55)   # seated by its squashed height (2026-09-24: a blob's half-height is radius x squash)


def build_headland_and_turn():
    """The old-Yachats headland rising ahead to the north-west with the
    bluff on it; the decommissioned turn with its chain and marker."""
    # (pass 475) the headland is terrain now (build_headland_2026_11): the
    # blob hung over a plain. The old road is paved — "paved in the 2010s for
    # the tower's construction trucks" — so the gravel spur is gone too.
    for nm, py in (("S", 157.4), ("N", 162.6)):
        make_lathe(f"Chain_Post_{nm}", (-6.6, py, 0.0), [(0.07, 0.0), (0.06, 0.9), (0.08, 0.94), (0.08, 1.0), (0.0, 1.02)], (0.36, 0.36, 0.38, 1.0), segments=8)
    # "The chain hung loose on one side." (ch22_drive n48) — hooked to the N
    # post, unhooked from the S one: it droops to the asphalt and its last
    # links lie on the road by the bare S post ("The wagon went around the chain")
    CHAIN_C = (0.30, 0.30, 0.32, 1.0)
    make_tube("Chain", catenary((-6.6, 162.6, 0.92), (-6.62, 158.4, 0.035), 0.22, n=12), 0.022, CHAIN_C, segments=6)
    make_tube("Chain_Slack", [(-6.62, 158.4, 0.035), (-6.70, 157.95, 0.034), (-6.92, 157.70, 0.034), (-7.05, 157.82, 0.034)], 0.022, CHAIN_C, segments=6)
    _cz = [p for p in catenary((-6.6, 162.6, 0.92), (-6.62, 158.4, 0.035), 0.22, n=12)]
    _sz = min(_cz, key=lambda q: abs(q[1] - 161.6))[2]
    make_box("Chain_Sign", (-6.6, 161.6, _sz - 0.15), (0.02, 0.40, 0.26), (0.92, 0.88, 0.30, 1.0))
    make_cyl("Chain_Post_S_Eye", (-6.6, 157.48, 0.92), 0.03, 0.012, (0.30, 0.30, 0.32, 1.0), axis='Y', segments=8)
    # (pass 475) THE SIGN ON ITS POST. The user: "The sign is hovering over the
    # pole." The post stopped at 2.00 m and the sign began at 2.05 — and
    # support_audit had let it off because "Road_Marker" read as road. A
    # square galvanized post up the back of the sign to its top edge, the two
    # bolts through the face at top and bottom, a concrete collar at the foot.
    galv = (0.52, 0.54, 0.54, 1.0)
    make_box("Road_Marker_Post", (-5.045, 156.5, 1.175), (0.05, 0.05, 2.35), galv)
    make_cyl("Road_Marker_Post_Footing", (-5.045, 156.5, 0.04), 0.11, 0.08, (0.58, 0.56, 0.52, 1.0), segments=10)
    for bk, bz in enumerate((2.085, 2.315)):
        make_cyl(f"Road_Marker_Bolt_{bk}", (-4.977, 156.5, bz), 0.012, 0.006, galv, axis='X', segments=8)
    make_box("Road_Marker", (-5.0, 156.5, 2.2), (0.04, 0.90, 0.30), (0.16, 0.42, 0.24, 1.0))
    # (pass 473) "A green metal road-marker reading Old Yachats Road" (ch22_drive
    # n48): its words were a white bar. They are a Label3D on the east face in
    # highway_101.tscn (Road_Marker_Words); the sign keeps a white border.
    for bn, (bz, bh, by_, bw) in {"T": (2.34, 0.012, 0.0, 0.86), "B": (2.06, 0.012, 0.0, 0.86),
                                  "S": (2.2, 0.27, -0.425, 0.012), "N": (2.2, 0.27, 0.425, 0.012)}.items():
        make_box(f"Road_Marker_Border_{bn}", (-4.978, 156.5 + by_, bz), (0.004, bw, bh), (0.94, 0.94, 0.90, 1.0))
    # the guardrail has a gap at the spur
    make_box("Guardrail_End_S", (-5.4, 155.0, 0.72), (0.09, 0.5, 0.34), (0.86, 0.72, 0.20, 1.0))
    make_box("Guardrail_End_N", (-5.4, 165.5, 0.72), (0.09, 0.5, 0.34), (0.86, 0.72, 0.20, 1.0))
    # Tem's wagon northbound for the hood preset (pass 476: it was a pickup;
    # "the wagon went around the chain" — her grandfather's small Toyota
    # wagon, brown as it stands at the cabin)
    make_car("Tem_Wagon", 1.8, 8.0, 4.6, (0.48, 0.36, 0.26, 1.0), wagon=True, along="Y", z0=0.02)
    make_cyl("Mile_Marker", (4.6, 120.0, 0.9), 0.04, 1.8, (0.80, 0.84, 0.62, 1.0), segments=6)


def build_horizon():
    make_far_bands("FarRidge", (0.16, 0.24, 0.18),
                   [(200.0, 300.0, 40.0, 0.85), (420.0, 480.0, 55.0, 0.65)],
                   sides="E", cx=60.0, cy=0.0, profile="ridge")


def build_dusk_dressing_2026_09():
    """Draft 2 (2026-09-25) — the first sheet with this road on it read
    as a road at dusk and nothing else: a flat grey sky, black cedars,
    an unlit rail. What dusk on 101 has that the frame lacked:
      · REFLECTORS — an amber lens on every guardrail post's road face,
        the one thing on a coast rail that reads at dusk;
      · A CAR AHEAD — a sedan northbound 190 m up the lane, its
        taillights toward the truck (the kit puts red lenses on the tail);
      · THE LAST LIGHT — a warm band 600 m out over the sea haze, the
        sun gone but not its colour.
    NEXT (draft 3): the truck's dashboard glow on the hood preset; wet
    asphalt after the ch22 rain (a darker lane with a sheen band); the
    green Old Yachats marker lit by the headlights at the turn preset."""
    y = ROAD_NEAR + 0.4
    i = 0
    while y < 154.55:
        if y > -40.0:
            make_box("Guardrail_Reflector_%d" % i, (-5.35, y, 0.71), (0.02, 0.06, 0.06), (0.98, 0.84, 0.30, 1.0))
        y += 3.8
        i += 1
    make_car("Far_Sedan_Northbound", 1.8, 198.0, 4.6, (0.30, 0.32, 0.36, 1.0), along="Y", z0=0.02)
    make_box("Far_Dusk_Glow", (-600.0, 0.0, SEA_Z + 30.0), (40.0, 2600.0, 28.0), (0.96, 0.66, 0.38, 1.0))


# ── (pass 475) THE HEADLAND: geography ─────────────────────────────────
# "Old-Yachats was the bluff three miles north of present-day Yachats, on a
# small unincorporated headland that had been bypassed when the coastal
# highway had been straightened in the 2020s." (ch22_drive n13) The straight
# highway runs past the headland's base; the headland stands out WEST of the
# turn into the sea, its coast below. COAST walks the shore from the bluff
# edge south of the turn (x -15), west round the headland and back to x -15
# north of it — land on its right hand. East of x -15 is Ground_Far.
COAST = [(-15.0, 120.0), (-15.0, 150.0), (-22.0, 157.0), (-32.0, 168.0), (-46.0, 184.0), (-66.0, 194.0),
         (-90.0, 198.0), (-112.0, 204.0), (-130.0, 216.0), (-144.0, 236.0), (-152.0, 262.0), (-156.0, 292.0),
         (-155.0, 326.0), (-148.0, 362.0), (-136.0, 396.0), (-118.0, 428.0), (-96.0, 456.0), (-72.0, 478.0),
         (-48.0, 494.0), (-30.0, 512.0), (-18.0, 536.0), (-15.0, 560.0), (-15.0, 620.0)]
# "Tem turned off 101 onto the road. The wagon went around the chain. The road
# climbed. Old Yachats Road wound up the bluff for three-quarters of a mile."
# Its first 150 m, from the shoulder's edge NW up the headland's flank.
OLD_ROAD = [(-5.0, 160.0), (-10.0, 160.4), (-14.5, 162.2), (-18.0, 166.8), (-20.6, 173.6), (-22.8, 181.6),
            (-25.4, 190.4), (-29.0, 199.6), (-33.8, 208.6), (-39.6, 217.6), (-46.2, 226.8), (-52.6, 236.4),
            (-58.4, 246.6), (-63.2, 257.6), (-67.0, 269.4), (-70.0, 282.0)]
OLD_ROAD_FLAT, OLD_ROAD_GRADE = 12.0, 0.09


def _smooth(e0, e1, v):
    t = max(0.0, min(1.0, (v - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


def _seg_near(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0.0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    qx, qy = ax + dx * t, ay + dy * t
    return math.hypot(px - qx, py - qy), t


def _coast_dist(x, y):
    return min(_seg_near(x, y, a[0], a[1], b[0], b[1])[0] for a, b in zip(COAST, COAST[1:]))


def _on_land(x, y):
    """West of x -15: inside the headland (COAST closed along x = -15)."""
    poly = COAST + [(-15.0, COAST[0][1])]
    inside = False
    for (ax, ay), (bx, by) in zip(poly, poly[1:]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            inside = not inside
    return inside


def _old_road_s():
    out, acc = [0.0], 0.0
    for a, b in zip(OLD_ROAD, OLD_ROAD[1:]):
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        out.append(acc)
    return out


_OR_S = _old_road_s()


def _old_road_z(s):
    return 0.012 + max(0.0, s - OLD_ROAD_FLAT) * OLD_ROAD_GRADE


def _old_road_near(x, y):
    best = (1e9, 0.0)
    for i, (a, b) in enumerate(zip(OLD_ROAD, OLD_ROAD[1:])):
        d, t = _seg_near(x, y, a[0], a[1], b[0], b[1])
        if d < best[0]:
            best = (d, _OR_S[i] + t * (_OR_S[i + 1] - _OR_S[i]))
    return best


BLUFF_TOP_DROP = -5.0      # the bluff top falls from the rail's footing (x -6) to -5 m at its edge (x -15)


def _strip_edge(y):
    """The bluff top's height at x -15: -5 m where the sea is straight west,
    level with the highway where the headland's base meets it."""
    b = _smooth(140.0, 165.0, y) * (1.0 - _smooth(545.0, 570.0, y))
    return BLUFF_TOP_DROP + (-0.05 - BLUFF_TOP_DROP) * b


def _headland_h(x, y):
    """The ground's height west of the roadbed (x < -6). The bluff top falls
    away past the rail (so from the road the sea shows over its edge); the
    headland rises from its cliffs to a crest ~28 m up, eased down to the
    bluff top along x -15; the old road is benched into its flank; off the
    land, the cliff falls 24 m into the sea (the Sea_Bluff wedges' profile)."""
    edge = _strip_edge(y)
    if x > -15.0:
        h = -0.05 + (edge + 0.05) * min(1.0, (-6.0 - x) / 9.0)
    else:
        D = _coast_dist(x, y)
        k = _smooth(-15.0, -70.0, x)
        if _on_land(x, y):
            h = edge + (2.0 + 26.0 * _smooth(0.0, 140.0, D) - edge) * k
        else:
            lip = edge + (2.0 - edge) * k
            h = lip - (lip - (SEA_Z - 1.5)) * min(1.0, D / 24.0)
    d, s = _old_road_near(x, y)
    if d < 13.0:
        w = 1.0 if d < 4.0 else 1.0 - _smooth(4.0, 13.0, d)
        h = h * (1.0 - w) + (_old_road_z(s) - 0.03) * w
    return h


def _surf(x, y):
    """The ground under (x, y) anywhere along this stretch."""
    if x >= -6.0:
        return -0.05
    if 120.0 <= y <= 620.0:
        return _headland_h(x, y)
    return -0.05 + (BLUFF_TOP_DROP + 0.05) * min(1.0, (-6.0 - x) / 9.0)


def _hwy_path():
    """The highway's centre line as build_road lays it (straight to y 250,
    then make_road_bend: 28 degrees east over 140 m in 10 m steps, 900 m on)."""
    pts = [(0.0, y) for y in range(-1200, 251, 10)]
    x, y, h = 0.0, 250.0, 0.0
    dh = math.radians(28.0) / 14
    for i in range(14):
        h += dh
        x += math.sin(h) * 10.0
        y += math.cos(h) * 10.0
        pts.append((x, y))
    for i in range(90):
        x += math.sin(h) * 10.0
        y += math.cos(h) * 10.0
        pts.append((x, y))
    return pts


_HWY = _hwy_path()


def _hwy_point(s):
    """(point, west-hand unit normal) at arc length s north of y 0."""
    i = int((s + 1200.0) // 10.0)
    i = max(0, min(len(_HWY) - 2, i))
    (ax, ay), (bx, by) = _HWY[i], _HWY[i + 1]
    t = max(0.0, min(1.0, (s + 1200.0 - i * 10.0) / 10.0))
    L = math.hypot(bx - ax, by - ay) or 1.0
    return (ax + (bx - ax) * t, ay + (by - ay) * t), (-(by - ay) / L, (bx - ax) / L)


def _ribbon(name, pts, width, thick, color):
    """A road laid along a 3D centre line: a closed strip, level across, its
    top on the line. One mesh (no seams between segments on the bends)."""
    from _props.geometry import _finalize_mesh
    hw = width / 2.0
    verts, faces = [], []
    n = len(pts)
    for i, (x, y, z) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        verts += [(x + nx * hw, y + ny * hw, z), (x - nx * hw, y - ny * hw, z),
                  (x - nx * hw, y - ny * hw, z - thick), (x + nx * hw, y + ny * hw, z - thick)]
    for i in range(n - 1):
        a, b = 4 * i, 4 * (i + 1)
        faces += [[a, a + 1, b + 1, b], [a + 3, b + 3, b + 2, a + 2], [a, b, b + 3, a + 3], [a + 1, a + 2, b + 2, b + 1]]
    faces += [[0, 3, 2, 1], [4 * (n - 1), 4 * (n - 1) + 1, 4 * (n - 1) + 2, 4 * (n - 1) + 3]]
    return _finalize_mesh(name, verts, faces, color)


def build_headland_2026_11():
    """THE HEADLAND (pass 475). The user, on the turn: "More detail on the
    backgrounds." The frame had no coast in it: Ground_Far ran a kilometre
    out over the sea, the Pacific never drew, and the headland was a blob
    hanging over a green plain. By the text (ch22_drive n13, n43-52):
      · the straight highway passes the headland's BASE ("bypassed when the
        coastal highway had been straightened"); the headland stands out
        west into the sea, ~30 m up, cliffs all round;
      · OLD YACHATS ROAD climbs it from the chain — "The road climbed" —
        paved ("in the 2010s for the tower's construction trucks"), aged
        ("had not ... been used much"): cracks, grass up the seams, a faded
        centre line, a pothole, gravel at its edges;
      · cedar both sides ("Trees on either side had not been cut back to
        road-clearance in years. The wagon brushed cedar branches on both
        sides"), and the headland under cedar to its cliffs, the cliff tops
        in wind-bent shore pine; the swell's foam line at the cliff foot.
    The tower is not drawn: from the turn it is three-quarters of a mile up
    the road, and "From a distance it nearly disappeared into the bluff."
    NEXT (draft 2): rock faces where the cliffs are sheer (the terrain is one
    green); the road's first bend seen from the drive preset; salal under
    the roadside cedars; the old village's foundations, if the text ever
    places them."""
    import random
    from _props.geometry import make_heightfield, make_rot_box, join_prefix
    rnd = random.Random(4751)
    # ── the ground: one heightfield, x -215..-15, y 120..620, 4 m cells ──
    cell = 4.0
    xs = [-214.0 + c * cell for c in range(53)]          # x -214 .. -6 (the roadbed's edge)
    ys = [120.0 + r * cell for r in range(126)]
    # its base (and the skirt's bottom cap) below the sea: at z 0 the cap
    # was a floor at -0.3 over the whole 200 x 500 m and hid the water
    BASE = SEA_Z - 2.5
    heights = [[_headland_h(x, y) - BASE for x in xs] for y in ys]
    make_heightfield("Headland_Terrain", (-214.0, 120.0, BASE), cell, heights, (0.22, 0.30, 0.20, 1.0), skirt=0.3)
    # the cliffs and the road cut in rock, not grass: faces steeper than ~38
    # degrees take the bluff's grey (one mesh, coloured by its own slope)
    # The slope comes from the height grid itself (face k of the grid is row
    # k // (cols - 1), column k % (cols - 1), as _gen_heightfield lays them),
    # so only loop_indices is read off the mesh.
    rows_, cols_ = len(heights), len(heights[0])
    steep = {}
    for r in range(rows_ - 1):
        for c in range(cols_ - 1):
            h00, h01, h10, h11 = heights[r][c], heights[r][c + 1], heights[r + 1][c], heights[r + 1][c + 1]
            gx = ((h01 + h11) - (h00 + h10)) / (2.0 * cell)
            gy = ((h10 + h11) - (h00 + h01)) / (2.0 * cell)
            if 1.0 / math.sqrt(1.0 + gx * gx + gy * gy) < 0.78 and (h00 + h01 + h10 + h11) / 4.0 > 0.5:
                k = r * (cols_ - 1) + c
                steep[k] = ROCK if (k * 7) % 5 else ROCK_DK
    try:
        import bpy
        ob = bpy.data.objects.get("Headland_Terrain")
        me = ob.data if ob else None
        lay = None
        if me is not None:
            lay = me.vertex_colors.get("Col") if hasattr(me, "vertex_colors") and me.vertex_colors else me.color_attributes.get("Col")
        if lay is not None:
            for k, poly in enumerate(me.polygons):
                col = steep.get(k)
                if col is not None:
                    for li in poly.loop_indices:
                        lay.data[li].color = col
    except ImportError:
        pass
    # ── the foam at the cliff foot, round the headland ──
    for k, (a, b) in enumerate(zip(COAST[2:-2], COAST[3:-1])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L                  # seaward (land is on the right hand)
        for j, (off, w, zz) in enumerate(((24.5, 1.0, 0.012), (27.2, 0.6, 0.006))):
            make_rot_box(f"Headland_Swell_{k}_{j}", ((a[0] + b[0]) / 2.0 + nx * off, (a[1] + b[1]) / 2.0 + ny * off, SEA_Z + zz),
                         (L + 6.0, w, zz * 2.0), FOAM, yaw=math.atan2(dy, dx))
    # ── OLD YACHATS ROAD ──
    pts = []
    for i, (a, b) in enumerate(zip(OLD_ROAD, OLD_ROAD[1:])):
        n = max(1, int(round(math.hypot(b[0] - a[0], b[1] - a[1]) / 2.0)))
        for j in range(n):
            t = j / n
            s_ = _OR_S[i] + t * (_OR_S[i + 1] - _OR_S[i])
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, _old_road_z(s_)))
    pts.append((OLD_ROAD[-1][0], OLD_ROAD[-1][1], _old_road_z(_OR_S[-1])))
    OLD = (0.31, 0.31, 0.30, 1.0)
    _ribbon("Old_Yachats_Road_Asphalt", pts, 4.8, 0.6, OLD)
    _ribbon("Old_Yachats_Road_Gravel", [(x, y, z - 0.012) for x, y, z in pts], 6.2, 0.6, GRAVEL)

    def at(s_, off):
        """(x, y, z, heading, grade) on the old road, `off` m to its left."""
        i = max(0, min(len(OLD_ROAD) - 2, next((k for k in range(len(_OR_S) - 1) if _OR_S[k + 1] >= s_), len(_OR_S) - 2)))
        a, b = OLD_ROAD[i], OLD_ROAD[i + 1]
        t = (s_ - _OR_S[i]) / max(1e-6, _OR_S[i + 1] - _OR_S[i])
        hx, hy = (b[0] - a[0]), (b[1] - a[1])
        L = math.hypot(hx, hy)
        hx, hy = hx / L, hy / L
        x, y = a[0] + (b[0] - a[0]) * t - hy * off, a[1] + (b[1] - a[1]) * t + hx * off
        return x, y, _old_road_z(s_), math.atan2(hy, hx), (OLD_ROAD_GRADE if s_ > OLD_ROAD_FLAT else 0.0)
    # its faded centre line, its cracks (along it, pitched to the grade, and
    # across it, level), its pothole, grass up the seams and along both edges
    k = 0
    s_ = 6.0
    while s_ < _OR_S[-1] - 3.0:
        if (k % 4) != 2:                                   # worn away in places
            x, y, z, hd, g = at(s_, 0.0)
            make_rot_box(f"Old_Yachats_Road_Dash_{k}", (x, y, z + 0.001), (1.6, 0.09, 0.004), (0.62, 0.58, 0.40, 1.0),
                         yaw=hd, pitch=-math.atan(g))
        s_ += 6.5
        k += 1
    for i in range(70):
        s_ = rnd.uniform(3.0, _OR_S[-1] - 2.0)
        along = i % 3 != 0
        x, y, z, hd, g = at(s_, rnd.uniform(-2.0, 2.0))
        ln = rnd.uniform(0.8, 3.0) if along else rnd.uniform(0.6, 2.2)
        make_rot_box(f"Old_Yachats_Road_Crack_{i}", (x, y, z + 0.001), (ln, 0.05, 0.004), (0.18, 0.18, 0.18, 1.0),
                     yaw=hd + (rnd.uniform(-0.25, 0.25) if along else math.pi / 2.0), pitch=(-math.atan(g) if along else 0.0))
    for nm, s_, off, r in (("Old_Yachats_Pothole", 21.0, -0.9, 0.45), ("Old_Yachats_Pothole_2", 63.0, 1.1, 0.32)):
        x, y, z, hd, g = at(s_, off)
        make_cyl(nm, (x, y, z + 0.0015), r, 0.003, (0.16, 0.17, 0.18, 1.0), segments=10)
        make_cyl(nm + "_Water", (x, y, z + 0.0035), r * 0.75, 0.002, (0.36, 0.42, 0.46, 1.0), segments=10)
    grass = ((0.30, 0.40, 0.22, 1.0), (0.38, 0.42, 0.24, 1.0), (0.46, 0.44, 0.28, 1.0))
    for i in range(110):
        s_ = rnd.uniform(4.0, _OR_S[-1] - 1.0)
        seam = i % 4 == 0
        off = rnd.uniform(-1.6, 1.6) if seam else rnd.choice((-1, 1)) * rnd.uniform(2.45, 3.3)
        x, y, z, hd, g = at(s_, off)
        r = rnd.uniform(0.10, 0.20) if seam else rnd.uniform(0.18, 0.42)
        make_blob(f"Old_Yachats_Road_Weed_{i}", (x, y, z + r * 0.25), r, grass[i % 3], noise=0.35, seed=1500 + i, rings=3, segments=6, squash=0.4)
    # ── cedar both sides of the road, and the headland under cedar ──
    trees = []
    s_ = 15.0
    while s_ < _OR_S[-1] + 4.0:
        for side in (-1, 1):
            off = side * rnd.uniform(4.6, 6.6)
            x, y, z, hd, g = at(min(s_, _OR_S[-1]), off)
            if x < -17.0 and _on_land(x, y):
                trees.append((x, y, rnd.uniform(13.0, 21.0)))
        s_ += rnd.uniform(6.0, 8.0)
    for gx in range(-212, -16, 12):
        for gy in range(124, 616, 12):
            x, y = gx + rnd.uniform(-4.0, 4.0), gy + rnd.uniform(-4.0, 4.0)
            if x > -18.0 or not _on_land(x, y) or _coast_dist(x, y) < 8.0:
                continue
            if _old_road_near(x, y)[0] < 6.0 or any(abs(x - t[0]) < 4.0 and abs(y - t[1]) < 4.0 for t in trees[-40:]):
                continue
            trees.append((x, y, rnd.uniform(14.0, 24.0)))
    for i, (x, y, h) in enumerate(trees):
        make_conifer(f"Headland_Tree_{i}", x, y, h, CEDAR if i % 2 else CEDAR_LT, TRUNK, z0=_headland_h(x, y) - 0.5)
    # ── shore pine on the cliff tops, swept inland by the westerlies ──
    PINE, PINE_DK, BARK = (0.18, 0.30, 0.20, 1.0), (0.14, 0.24, 0.17, 1.0), (0.30, 0.22, 0.16, 1.0)
    spots = []
    for a, b in zip(COAST[2:-2], COAST[3:-1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        for t in (0.3, 0.75):
            ix, iy = dy / L, -dx / L                       # inland (right hand)
            off = rnd.uniform(3.0, 5.5)
            spots.append((a[0] + dx * t + ix * off, a[1] + dy * t + iy * off, rnd.uniform(4.0, 7.0)))
    spots += [(-12.5, 104.0, 4.2), (-11.5, 78.0, 3.8), (-13.0, 46.0, 4.6), (-12.0, 12.0, 4.0)]
    for i, (sx, sy, h) in enumerate(spots):
        if sx > -16.0 and sy > 118.0:
            continue
        z0 = _surf(sx, sy) - 0.3
        lean = 0.9
        top = (sx + lean * h * 0.35, sy, z0 + h * 0.92)
        make_tube(f"Shore_Pine_{i}_Trunk", [(sx, sy, z0), (sx + lean * h * 0.12, sy, z0 + h * 0.45), top], 0.09 + h * 0.012, BARK, segments=6)
        for ci, (cdx, cz, cr) in enumerate(((0.55, 0.78, 0.62), (0.35, 0.92, 0.48), (0.80, 0.66, 0.46))):
            make_blob(f"Shore_Pine_{i}_Crown_{ci}", (sx + lean * h * 0.35 * cdx + h * 0.10, sy + rnd.uniform(-0.4, 0.4), z0 + h * cz),
                      h * 0.18 * cr / 0.5, PINE if (i + ci) % 2 else PINE_DK, noise=0.25, seed=2100 + i * 3 + ci, squash=0.55)
    for pfx in ("Headland_Tree", "Headland_Swell", "Shore_Pine", "Old_Yachats_Road_Crack", "Old_Yachats_Road_Weed", "Old_Yachats_Road_Dash"):
        join_prefix(pfx)


def build_detail_2026_11():
    """DETAIL PASS (pass 475 · D2 surface breakup, D3 infrastructure, D5
    depth). The user, on the Old Yachats Road frame: "More detail on the
    backgrounds." The road was one grey ribbon, the verges a clean edge
    against a flat green plane, the turn a gravel pad and nothing past it.
    What a decommissioned turn off 101 on the Oregon coast has:
      · THE ROAD'S HISTORY — patches of newer asphalt, tar-sealed cracks,
        the raised reflectors on the centre line, the wheel paths worn pale;
      · THE VERGE — grass and weeds up to the shoulder's edge, salal and
        fern under the cedars, the land not one flat green;
      · INFRASTRUCTURE — utility poles down the inland side with their wires
        sagging pole to pole, white delineator posts, the green milepost;
      · THE OLD ROAD — past the chain the old asphalt goes on west, cracked,
        grass up its seams and its edges, a faded centre line, a pothole,
        into wind-bent shore pine on the bluff;
      · THE BLUFF TOP — tufts, salal and shore pine between the rail and the
        drop, so the land meets the sea through something.
    Repeated small parts are joined to one mesh per kind (perf_gate).
    NEXT (draft 2 of this pass): wet sheen on the asphalt after the ch22
    rain; a fallen limb across the old road; the turn preset's headlight
    pool on the marker."""
    import random
    from _props.geometry import make_rot_box, join_prefix
    rnd = random.Random(475)
    # ── D2 · the road's history ──
    for i in range(26):
        py = rnd.uniform(-30.0, 240.0)
        px = rnd.choice((-1.8, 1.8)) + rnd.uniform(-0.8, 0.8)
        make_box(f"Road_Patch_{i}", (px, py, 0.0215), (rnd.uniform(1.0, 2.6), rnd.uniform(1.4, 4.5), 0.003),
                 (0.19, 0.19, 0.20, 1.0) if i % 3 else (0.28, 0.28, 0.29, 1.0))
    for i in range(70):
        py = rnd.uniform(-30.0, 245.0)
        px = rnd.uniform(-3.3, 3.3)
        make_rot_box(f"Road_Crack_{i}", (px, py, 0.0222), (0.035, rnd.uniform(0.8, 3.2), 0.0015), (0.11, 0.11, 0.12, 1.0),
                     yaw=rnd.uniform(-0.9, 0.9))
    y = -36.0
    k = 0
    while y < 248.0:
        make_box(f"Road_RPM_{k}", (0.0, y + 6.0, 0.026), (0.10, 0.10, 0.012), (0.96, 0.82, 0.30, 1.0))
        y += 24.0
        k += 1
    for li, wx in enumerate((-2.55, -0.95, 0.95, 2.55)):
        make_box(f"Road_WheelPath_{li}", (wx, (ROAD_NEAR + 250.0) / 2.0, 0.0206), (0.55, 250.0 - ROAD_NEAR, 0.002), (0.29, 0.29, 0.30, 1.0))
    # the land is not one green: patches of drier and wetter grass
    for i in range(40):
        side = rnd.choice((-1, 1))      # (west of the rail the bluff top falls away: east side only)
        gx = rnd.uniform(7.2, 9.0)
        make_box(f"Ground_Patch_{i}", (gx, rnd.uniform(-30.0, 250.0), -0.028 + 0.001 * (i % 5)),
                 (rnd.uniform(1.0, 1.8), rnd.uniform(3.0, 9.0), 0.012),
                 rnd.choice(((0.26, 0.34, 0.20, 1.0), (0.34, 0.36, 0.22, 1.0), (0.22, 0.30, 0.19, 1.0), (0.40, 0.38, 0.26, 1.0))))
    # the verges: the roadbed's dark top showed between the shoulder and the
    # rail (black in every shadow); gravel to the rail, and on the inland
    # side gravel then the forest floor to the cedars
    for sg in (-1, 1):
        make_box(f"Road_Verge_Gravel_{sg:+d}", (sg * 5.6, (ROAD_NEAR + 250.0) / 2.0, -0.035), (1.2, 250.0 - ROAD_NEAR, 0.03), GRAVEL)
    make_box("Road_Verge_Duff_E", (11.1, (ROAD_NEAR + 250.0) / 2.0, -0.04), (9.8, 250.0 - ROAD_NEAR, 0.02), (0.24, 0.24, 0.17, 1.0))
    # ── the verge: grass up to both shoulders' outer edges ──
    grass = ((0.30, 0.40, 0.22, 1.0), (0.38, 0.42, 0.24, 1.0), (0.46, 0.44, 0.28, 1.0))
    gi = 0
    for side, ex in ((-1, -5.05), (1, 5.05)):
        yy = -30.0
        while yy < 250.0:
            if side < 0 and 154.0 < yy < 166.0:
                yy += 2.0
                continue           # the turn's mouth is gravel
            # west of the rail posts (x -5.4) on the seaward side, so no tuft grows through one
            r = rnd.uniform(0.22, 0.45) if side > 0 else rnd.uniform(0.18, 0.30)
            gx_ = ex + side * rnd.uniform(0.05, 0.6) if side > 0 else rnd.uniform(-5.95, -5.85)
            make_blob(f"Verge_Grass_{gi}", (gx_, yy + rnd.uniform(-0.6, 0.6), r * 0.35 - 0.05), r,
                      grass[gi % 3], noise=0.35, seed=900 + gi, rings=3, segments=6, squash=0.45)
            yy += rnd.uniform(1.6, 3.2)
            gi += 1
    for i in range(36):                          # salal and sword fern under the cedars
        make_blob(f"Verge_Salal_{i}", (rnd.uniform(5.8, 8.4), rnd.uniform(-28.0, 250.0), 0.30), rnd.uniform(0.45, 0.8),
                  SALAL if i % 2 else (0.20, 0.32, 0.20, 1.0), noise=0.3, seed=1200 + i, rings=3, segments=7, squash=0.5)
    # ── D3 · infrastructure ──
    # The line runs on the SEAWARD side, 7.4 m off the centre line, on the
    # bluff top between the rail and the drop: on the inland side its wires
    # went through the cedar crowns (prop_overlap: 20 clips). It follows the
    # highway round the bend; north of the bend it is over open ground.
    POLE_C, ARM_C = (0.36, 0.28, 0.20, 1.0), (0.34, 0.26, 0.18, 1.0)
    poles = []
    s_ = -20.0                       # the old road's mouth (y 160) mid-span, not under a pole
    pi_ = 0
    while s_ < 420.0:
        (cx_, cy_), (nx_, ny_) = _hwy_point(s_)
        px_, py_ = cx_ + nx_ * 7.4, cy_ + ny_ * 7.4
        yaw_ = math.atan2(ny_, nx_)
        poles.append((px_, py_, nx_, ny_))
        zb = _surf(px_, py_) - 0.35                  # on the falling bluff top
        make_cyl(f"Utility_Pole_{pi_}", (px_, py_, (10.9 + zb) / 2.0), 0.15, 10.9 - zb, POLE_C, segments=8)
        make_rot_box(f"Utility_Pole_Arm_{pi_}", (px_, py_, 10.4), (2.0, 0.12, 0.12), ARM_C, yaw=yaw_)
        for ii, off in enumerate((-0.85, 0.0, 0.85)):
            make_cyl(f"Utility_Pole_Insulator_{pi_}_{ii}", (px_ + nx_ * off, py_ + ny_ * off, 10.53), 0.035, 0.14, (0.70, 0.76, 0.74, 1.0), segments=6)
        pi_ += 1
        s_ += 40.0
    for k_, (a_, b_) in enumerate(zip(poles, poles[1:])):
        for ii, off in enumerate((-0.85, 0.0, 0.85)):
            make_tube(f"Utility_Wire_{k_}_{ii}", catenary((a_[0] + a_[2] * off, a_[1] + a_[3] * off, 10.6),
                                                          (b_[0] + b_[2] * off, b_[1] + b_[3] * off, 10.6), 0.9, n=8),
                      0.012, (0.10, 0.10, 0.11, 1.0), segments=4)
    dy = -20.0
    di = 0
    while dy < 250.0:
        if not (40.0 < dy < 120.0):
            make_box(f"Delineator_{di}", (5.25, dy, 0.55), (0.08, 0.06, 1.10), (0.92, 0.92, 0.88, 1.0))
            make_box(f"Delineator_Lens_{di}", (5.25, dy - 0.031, 0.98), (0.06, 0.004, 0.10), (0.98, 0.70, 0.22, 1.0))
        dy += 50.0
        di += 1
    # the milepost: a green paddle on its post (it was a bare cylinder)
    make_box("Mile_Marker_Paddle", (4.6, 120.0 - 0.045, 1.55), (0.26, 0.012, 0.56), (0.16, 0.42, 0.24, 1.0))
    make_box("Mile_Marker_Paddle_Border", (4.6, 120.0 - 0.052, 1.55), (0.22, 0.002, 0.52), (0.92, 0.92, 0.88, 1.0))
    make_box("Mile_Marker_Paddle_Field", (4.6, 120.0 - 0.054, 1.55), (0.20, 0.002, 0.50), (0.16, 0.42, 0.24, 1.0))
    # ── the bluff top south of the headland: tufts and salal ──
    for i in range(60):
        bx_ = rnd.uniform(-14.5, -5.9)
        by_ = rnd.uniform(-20.0, 240.0)
        if 154.0 < by_ < 166.0 and bx_ > -14.0:
            continue                                  # the old road's mouth
        if any(math.hypot(bx_ - q[0], by_ - q[1]) < 1.0 for q in poles):
            continue
        r = rnd.uniform(0.25, 0.6)
        make_blob(f"Bluff_Tuft_{i}", (bx_, by_, _surf(bx_, by_) + r * 0.30), r, grass[(i + 1) % 3] if i % 4 else SALAL,
                  noise=0.35, seed=1800 + i, rings=3, segments=6, squash=0.45)
    # ── THE ROCK CUT, where the highway was straightened (it was one grey
    # box the size of a building, the biggest thing in the drive preset):
    # blasted ledges, the drill seams, boulders proud of the face, talus,
    # and the cedars standing on its top edge ──
    ROCK_LT = (0.42, 0.40, 0.36, 1.0)
    proud = []                                     # (y0, y1, z0, z1) of what stands off the face
    for i in range(14):
        ly = rnd.uniform(44.0, 116.0)
        ll = rnd.uniform(6.0, 18.0)
        ll = min(ll, 2.0 * min(ly - 40.5, 119.5 - ly))
        dep = rnd.uniform(0.25, 0.6)
        lz, lh = rnd.uniform(1.2, 11.4), rnd.uniform(0.25, 0.7)
        make_rot_box(f"Rock_Cut_Ledge_{i}", (7.5 - dep / 2.0 + 0.05, ly, lz), (dep, ll, lh),
                     (ROCK, ROCK_DK, ROCK_LT)[i % 3], yaw=rnd.uniform(-0.02, 0.02))
        proud.append((ly - ll / 2.0 - 0.3, ly + ll / 2.0 + 0.3, lz - lh / 2.0 - 0.05, lz + lh / 2.0 + 0.05))
    for i in range(26):
        r = rnd.uniform(0.9, 2.0)
        by_, bz_ = rnd.uniform(42.0, 118.0), rnd.uniform(1.0, 10.5)
        make_blob(f"Rock_Cut_Boulder_{i}", (7.5 + r * 0.25, by_, bz_), r,
                  (ROCK, ROCK_DK, ROCK_LT)[i % 3], noise=0.30, seed=2400 + i, rings=4, segments=7, squash=0.75)
        proud.append((by_ - r * 1.3, by_ + r * 1.3, bz_ - r, bz_ + r))
    for i in range(12):                            # on the tapering faces at each end
        by_ = rnd.uniform(19.0, 39.0) if i < 6 else rnd.uniform(121.0, 141.0)
        top_ = (by_ - 16.0) * 0.5 if by_ < 80.0 else (144.0 - by_) * 0.5
        r = rnd.uniform(0.6, 1.4)
        if top_ < r * 1.5:
            continue
        make_blob(f"Rock_Cut_Boulder_T{i}", (7.5 + r * 0.25, by_, rnd.uniform(r * 0.8, top_ - r * 0.8)), r,
                  (ROCK, ROCK_DK, ROCK_LT)[i % 3], noise=0.30, seed=2450 + i, rings=4, segments=7, squash=0.75)
    # the presplit drill lines down the face, broken where a ledge or a
    # boulder stands off it
    for i in range(22):
        sy_ = 41.5 + i * 3.5 + rnd.uniform(-0.6, 0.6)
        top = rnd.uniform(7.0, 11.5)
        cuts = sorted((z0, z1) for (y0, y1, z0, z1) in proud if y0 <= sy_ <= y1)
        z = 0.3
        j = 0
        for z0, z1 in cuts + [(top, top)]:
            if z0 - z > 0.8:
                make_box(f"Rock_Cut_Seam_{i}_{j}", (7.49, sy_, (z + min(z0, top)) / 2.0), (0.03, 0.05, min(z0, top) - z), (0.18, 0.18, 0.18, 1.0))
                j += 1
            z = max(z, z1)
            if z >= top:
                break
    for i in range(18):
        r = rnd.uniform(0.25, 0.7)
        make_blob(f"Rock_Cut_Talus_{i}", (rnd.uniform(6.4, 7.3), rnd.uniform(41.0, 119.0), r * 0.5 - 0.05), r,
                  (ROCK_DK, ROCK, ROCK_LT)[i % 3], noise=0.35, seed=2500 + i, rings=3, segments=6, squash=0.7)
    for i, ty in enumerate([44.0 + k * 7.3 for k in range(10)]):
        make_conifer(f"Rock_Cut_Tree_{i}", 11.6 + (i % 3) * 0.7, ty, 14.0 + (i * 3) % 5 * 1.3, CEDAR if i % 2 else CEDAR_LT, TRUNK, z0=11.7)
    for i in range(16):
        make_blob(f"Rock_Cut_Salal_{i}", (8.3 + rnd.uniform(0.0, 0.8), 42.0 + i * 4.7, 12.25), rnd.uniform(0.45, 0.8),
                  SALAL if i % 2 else (0.20, 0.32, 0.20, 1.0), noise=0.3, seed=2600 + i, rings=3, segments=7, squash=0.5)
    for pfx in ("Road_Patch", "Road_Crack", "Road_RPM", "Ground_Patch", "Verge_Grass", "Verge_Salal", "Utility_Wire",
                "Utility_Pole", "Delineator", "Bluff_Tuft", "Rock_Cut_Ledge", "Rock_Cut_Seam", "Rock_Cut_Boulder",
                "Rock_Cut_Talus", "Rock_Cut_Tree", "Rock_Cut_Salal", "Rock_Cut_Hill_Tree", "Rock_Cut_Hill_Salal"):
        join_prefix(pfx)


def main():
    clear_scene()
    build_road()
    build_inland()
    build_headland_and_turn()
    build_horizon()
    build_dusk_dressing_2026_09()
    build_headland_2026_11()
    build_detail_2026_11()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/highway_101.glb"))
    print(f"\n[build_highway_101] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
