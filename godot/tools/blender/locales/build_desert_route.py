"""desert_route — vol 3's Utah run, "v. emulsion" (draft 1, 2026-10-27).

The Deck: "vol 1-4 is still super broken and rough … it's all illogical
nonsense." Kathy's drive through "blasted Utah desert red" played on vol 6's
2026 Texas Gulf highway, vol 6's corporate NexCorp station and a Louisiana
motel. It gets its own road, in the early 2000s (Andy, 2026-10-27: "vol 3 is
all over the map, but early 2000s") — books on tape, a Galaga machine still in
the corner, the baby blue Plymouth Voyager already ten years old:

  emulsion: "Kathy drove that baby blue Plymouth voyager minivan with fake
   wood strip down the side through blasted Utah desert red, summer heat
   ashimmer undulating black tarmac horizon"; long haul truckers
                                                   → utah_highway_day
  "She stopped in towns along the way, empty places just off the main drag";
   "Inside the one room store a desktop fan oscillated"; the mud man at "an
   outdoor ice cooler"; "a quick game of Galaga"; "selling dead lizards horny
   toads"; "Kathy pump gas"                         → desert_gas_station
  red dust: "it all turns into this great red smear"; "pulls off to the side
   of the road, the undercar bumping against upturned root clumps"; "Two
   semis meet and collide … their hinged cargo whiteouts both lanes"; "a long
   burning mass of wreckage"; "A family station wagon"
                                                   → dust_storm_highway
  "She pulled into a motel some twenty miles down"; "Inside an elderly woman
   watching the television"                         → desert_motel_dusk
  "The kids all found the pool … ran along the concrete shorelines"; "Red
   silt settles on the skin of the water"           → motel_pool_dusk
  "Kathy had sat on the single bed in the empty room, the television on";
   "She went into the bathroom and locked the door" → motel_room_dusk

PROPOSED (the text names none of it): the town, the station's pumps and pole
sign, the motel's L-plan, its sign and its colours, the mesas.

Blender: x east, y north, z up; Godot (x, z, -y). Three areas 400 m apart:
the highway on x 0 (running north-south), the gas station at x +400 on its
main drag, the motel at x -400.

DRAFT 2 targets: heat shimmer and the dust as particles; the mud man's
"fine pink powder"; the elderly woman's office interior; the wreck's fire
as flicker; the curios as a hero prop; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_taper_cyl, make_rot_box, make_blob,
                             make_tube, join_stock, export_glb)
from _props.trees import make_shrub
from _props.vehicles import make_car
from _props.furniture import make_bed, make_lamp, make_chair
try:
    import bpy
except ImportError:
    bpy = None

DAY, STORM = "__utah_highway_day", "__dust_storm_highway"

SAND = (0.66, 0.40, 0.26, 1.0)
SAND2 = (0.58, 0.34, 0.22, 1.0)
ROCK = (0.56, 0.28, 0.18, 1.0)
ASPHALT = (0.12, 0.12, 0.13, 1.0)
LINE_Y = (0.86, 0.72, 0.22, 1.0)
LINE_W = (0.86, 0.86, 0.82, 1.0)
SAGE = (0.46, 0.50, 0.40, 1.0)
CINDER = (0.80, 0.76, 0.68, 1.0)
WOOD = (0.40, 0.30, 0.22, 1.0)
VOYAGER = (0.58, 0.72, 0.86, 1.0)         # baby blue
WOODGRAIN = (0.46, 0.30, 0.18, 1.0)
GLASS = (0.20, 0.24, 0.28, 1.0)


def _rng(seed):
    s = [seed & 0x7fffffff or 1]
    def r():
        s[0] = (s[0] * 1103515245 + 12345) & 0x7fffffff
        return s[0] / 0x7fffffff
    return r


def voyager(prefix, x, y, along="Y"):
    """The baby blue Plymouth Voyager with the fake wood strip."""
    make_car(prefix, x, y, 4.9, VOYAGER, hatch=True, along=along)
    for sx in (-1, 1):
        if along == "Y":
            make_box(f"{prefix}_Wood_{sx:+d}", (x + sx * 0.90, y, 0.62), (0.02, 3.9, 0.20), WOODGRAIN)
        else:
            make_box(f"{prefix}_Wood_{sx:+d}", (x, y + sx * 0.90, 0.62), (3.9, 0.02, 0.20), WOODGRAIN)


def semi(prefix, x, y, yaw=0.0, trailer_yaw=None, cab_col=(0.62, 0.14, 0.12, 1.0), trailer_col=(0.86, 0.86, 0.84, 1.0)):
    """A tractor-trailer: cab, sleeper, hood, the trailer on its own angle
    (a jackknife), wheels. `yaw` is the cab's heading (0 = north, +y)."""
    ty = yaw if trailer_yaw is None else trailer_yaw
    c, s = math.cos(yaw), math.sin(yaw)
    def at(u, v):                       # u along the heading, v to the left
        return (x - s * u - c * v, y + c * u - s * v)
    hx, hy = at(1.6, 0.0)
    make_rot_box(f"{prefix}_Hood", (hx, hy, 1.15), (1.6, 2.4, 1.2), cab_col, yaw=yaw + math.pi / 2)
    cx_, cy_ = at(0.0, 0.0)
    make_rot_box(f"{prefix}_Cab", (cx_, cy_, 1.85), (2.0, 2.5, 2.4), cab_col, yaw=yaw + math.pi / 2)
    make_rot_box(f"{prefix}_Windshield", (at(1.01, 0.0)[0], at(1.01, 0.0)[1], 2.35), (0.04, 2.1, 0.8), GLASS, yaw=yaw + math.pi / 2)
    for k, u in enumerate((1.6, -0.6, -1.6)):
        for v in (-1.1, 1.1):
            wx, wy = at(u, v)
            make_cyl(f"{prefix}_Wheel_{k}_{v:+.0f}", (wx, wy, 0.52), 0.52, 0.32, (0.10, 0.10, 0.10, 1.0), axis='X', segments=10)
    # the trailer hinged at the fifth wheel (u = -1.2)
    px, py = at(-1.2, 0.0)
    tc, ts = math.cos(ty), math.sin(ty)
    tx, tyy = px + ts * 6.8, py - tc * 6.8
    make_rot_box(f"{prefix}_Trailer", (tx, tyy, 2.35), (2.6, 13.6, 2.9), trailer_col, yaw=ty)
    for k in range(2):
        for v in (-1.1, 1.1):
            u = -11.0 - k * 1.3
            wx, wy = px + ts * (-u - 1.2) * -1.0 - tc * v, py - tc * (-u - 1.2) * -1.0 - ts * v
            make_cyl(f"{prefix}_TWheel_{k}_{v:+.0f}", (px + ts * (11.8 + k * 1.3) - tc * v, py - tc * (11.8 + k * 1.3) - ts * v, 0.52),
                     0.52, 0.32, (0.10, 0.10, 0.10, 1.0), axis='X', segments=10)


def build_desert():
    """The red desert to the horizon: sand, sage, rocks, the mesas."""
    make_box("Ground_Desert", (0.0, 0.0, -0.06), (2400.0, 2400.0, 0.04), SAND)
    r = _rng(77)
    for k in range(70):
        x0 = (r() - 0.5) * 1400.0
        y0 = (r() - 0.5) * 1400.0
        if abs(x0) < 14.0 or (abs(x0 - 400) < 60 and abs(y0) < 60) or (abs(x0 + 400) < 70 and abs(y0) < 60):
            continue
        make_box(f"Ground_Stock_Patch_{k}", (x0, y0, -0.04), (20.0 + r() * 40.0, 20.0 + r() * 40.0, 0.02), SAND2)
    for k in range(260):
        x0 = (r() - 0.5) * 900.0
        y0 = (r() - 0.5) * 900.0
        if abs(x0) < 9.0 or (abs(x0 - 400) < 40 and abs(y0) < 40) or (abs(x0 + 400) < 50 and abs(y0) < 45):
            continue
        make_shrub(f"Sage_Stock_{k}", x0, y0, h=0.5 + r() * 0.6, r=0.35 + r() * 0.4, col=SAGE)
    for k in range(40):
        x0 = (r() - 0.5) * 700.0
        y0 = (r() - 0.5) * 700.0
        if abs(x0) < 10.0 or (abs(x0 - 400) < 40 and abs(y0) < 40) or (abs(x0 + 400) < 50 and abs(y0) < 45):
            continue
        # (2026-10-30: boulders, not boxes)
        rr_ = 0.5 + r() * 1.3
        make_blob(f"Rock_Stock_{k}", (x0, y0, rr_ * 0.35), rr_, ROCK, noise=0.35, seed=k, squash=0.55 + r() * 0.3)
    # the mesas and buttes on every horizon
    # (round 4) Mesa_1 back off the highway's N end (its talus lay on the road)
    for i, (mx, my, rr, hh) in enumerate(((-520.0, 760.0, 180.0, 110.0), (260.0, 1050.0, 240.0, 150.0), (820.0, 560.0, 150.0, 80.0),
                                          (-950.0, 120.0, 200.0, 130.0), (980.0, -260.0, 180.0, 100.0), (-380.0, -900.0, 220.0, 120.0),
                                          (460.0, -820.0, 120.0, 170.0), (-120.0, 560.0, 60.0, 60.0))):
        make_taper_cyl(f"Mesa_{i}", (mx, my, hh / 2.0 - 2.0), rr, rr * 0.82, hh, ROCK, segments=12)
        make_taper_cyl(f"Mesa_{i}_Talus", (mx, my, hh * 0.18), rr * 1.35, rr * 1.02, hh * 0.36, (0.62, 0.34, 0.22, 1.0), segments=12)


def build_highway():
    """A two-lane blacktop north-south on x 0: two 3.6 m lanes, shoulders,
    the yellow centre dashes, the white edge lines, the telephone poles."""
    make_box("Hwy_Asphalt", (0.0, 0.0, -0.02), (12.0, 1400.0, 0.04), ASPHALT)
    for k in range(175):
        make_box(f"HwyLine_Stock_Dash_{k}", (0.0, -700.0 + k * 8.0, 0.002), (0.12, 3.0, 0.01), LINE_Y)
    for sx in (-1, 1):
        make_box(f"HwyLine_Stock_Edge_{sx:+d}", (sx * 3.6, 0.0, 0.002), (0.12, 1400.0, 0.01), LINE_W)
    for k in range(29):
        py = -700.0 + k * 50.0
        make_taper_cyl(f"Pole_Stock_{k}", (12.0, py, 4.5), 0.14, 0.11, 9.0, WOOD, segments=7)
        make_box(f"Pole_Stock_{k}_Arm", (12.0, py, 8.4), (1.8, 0.10, 0.10), WOOD)
    for k in range(28):
        py = -700.0 + k * 50.0
        make_tube(f"Wire_Stock_{k}", [(12.6, py, 8.5), (12.6, py + 50.0, 8.5)], 0.012, (0.10, 0.10, 0.10, 1.0), segments=4)
    # the shoulder's upturned root clumps (red dust: "the undercar bumping against upturned root clumps")
    r = _rng(9)
    for k in range(30):
        # (2026-10-30: a clump of dirt with its roots in the air, not a dark box)
        cx_, cy_ = 7.0 + r() * 2.0, -60.0 + k * 6.0
        make_blob(f"Root_Stock_{k}", (cx_, cy_, 0.12), 0.30, (0.46, 0.30, 0.20, 1.0), noise=0.4, seed=200 + k, squash=0.6)
        for j in range(3):
            a = r() * 6.28
            make_tube(f"Root_Stock_{k}_Tendril_{j}", [(cx_, cy_, 0.2), (cx_ + 0.25 * math.cos(a), cy_ + 0.25 * math.sin(a), 0.42),
                                                   (cx_ + 0.40 * math.cos(a), cy_ + 0.40 * math.sin(a), 0.50)], 0.02, (0.36, 0.26, 0.18, 1.0), segments=4)


def build_highway_day():
    """emulsion: the Voyager northbound, a semi coming the other way."""
    voyager("VoyagerDay", 1.8, -22.0)
    semi("SemiDay", -1.8, 70.0, yaw=math.pi)


def build_dust_storm():
    """red dust: the Voyager pulled onto the shoulder; ahead, two semis met
    across the lanes, their trailers jackknifed across both, the wreckage
    burning; the family station wagon."""
    voyager("VoyagerStorm", 6.4, -20.0)
    semi("WreckSemiA", -1.5, 62.0, yaw=math.pi + 0.35, trailer_yaw=math.pi + 1.35, cab_col=(0.18, 0.26, 0.48, 1.0))
    semi("WreckSemiB", 2.0, 74.0, yaw=-0.30, trailer_yaw=0.95, cab_col=(0.60, 0.12, 0.10, 1.0))
    make_car("WreckWagon", -3.0, 52.0, 5.0, (0.46, 0.36, 0.22, 1.0), hatch=True, along="X")
    r = _rng(31)
    for k in range(14):
        # (round 4) on the road, not sunk 15 cm through it, and clear of the
        # semis' wheels
        dx_, dy_, sx_, sy_, sz_, yw_ = -6.0 + r() * 12.0, 48.0 + r() * 34.0, 0.4 + r() * 1.4, 0.3 + r(), 0.2 + r() * 0.5, r() * 3.0
        if min(math.hypot(dx_ + 1.5, dy_ - 62.0), math.hypot(dx_ - 2.0, dy_ - 74.0)) < 4.5:
            continue
        make_rot_box(f"WreckDebris_{k}", (dx_, dy_, sz_ / 2.0 + 0.002), (sx_, sy_, sz_), (0.24, 0.22, 0.22, 1.0), yaw=yw_)
    for k in range(6):
        make_taper_cyl(f"WreckFire_Glow_{k}", (-4.0 + k * 1.8, 60.0 + (k % 3) * 5.0, 0.9), 1.0, 0.1, 1.8 + r() * 1.4, (1.0, 0.56, 0.18, 1.0), segments=7)
        make_taper_cyl(f"WreckSmoke_{k}", (-4.0 + k * 1.8, 61.0 + (k % 3) * 5.0, 7.0), 1.6, 3.4, 9.0, (0.10, 0.08, 0.08, 1.0), segments=8)


def build_gas_station():
    """Just off the main drag of a town that isn't one: the one-room store
    (cinderblock, a door, the window), two old pumps on an island, the ice
    chest out front, the pole sign; inside, the counter and the desk fan,
    the Galaga cabinet, the candy and the curios."""
    gx, gy = 400.0, 0.0
    make_box("Drag_Asphalt", (gx, gy - 14.0, -0.02), (300.0, 9.0, 0.04), ASPHALT)
    make_box("Drag_Line", (gx, gy - 14.0, 0.002), (300.0, 0.12, 0.01), LINE_Y)
    make_box("Station_Apron", (gx, gy + 1.0, -0.015), (26.0, 16.0, 0.03), (0.42, 0.40, 0.36, 1.0))
    # the store: 9 x 7, door and window on its south face
    sx0, sy0 = gx - 4.5, gy + 9.0
    make_box("Store_Wall_S_W", (gx - 3.2, sy0, 1.6), (2.6, 0.24, 3.2), CINDER)
    make_box("Store_Wall_S_E", (gx + 3.4, sy0, 1.6), (2.2, 0.24, 3.2), CINDER)
    make_box("Store_Wall_S_Mid", (gx + 0.6, sy0, 2.75), (3.4, 0.24, 0.9), CINDER)
    make_box("Store_Wall_S_Sill", (gx + 1.25, sy0, 0.45), (2.1, 0.24, 0.9), CINDER)
    make_box("Store_Window", (gx + 1.25, sy0, 1.6), (2.1, 0.04, 1.4), (0.36, 0.40, 0.42, 1.0))
    make_box("Store_Door_Frame", (gx - 1.0, sy0 - 0.02, 1.15), (1.1, 0.06, 2.3), (0.70, 0.70, 0.66, 1.0))
    make_box("Store_Door_Glass", (gx - 1.0, sy0 - 0.05, 1.2), (0.9, 0.02, 1.9), (0.30, 0.34, 0.36, 1.0))
    make_box("Store_Wall_N", (gx, sy0 + 7.0, 1.6), (9.0, 0.24, 3.2), CINDER)
    for sxn in (-1, 1):
        make_box(f"Store_Wall_{'E' if sxn > 0 else 'W'}", (gx + sxn * 4.5, sy0 + 3.5, 1.6), (0.24, 7.0, 3.2), CINDER)
    make_box("Store_Roof", (gx, sy0 + 3.5, 3.28), (9.6, 7.6, 0.16), (0.30, 0.28, 0.26, 1.0))
    make_box("Store_Floor", (gx, sy0 + 3.5, 0.01), (8.8, 6.8, 0.02), (0.52, 0.48, 0.42, 1.0))
    make_box("Store_Sign_Band", (gx, sy0 - 0.14, 2.9), (6.0, 0.04, 0.5), (0.86, 0.80, 0.62, 1.0))
    # inside
    make_box("Store_Counter", (gx + 2.6, sy0 + 2.4, 0.5), (2.4, 0.7, 1.0), (0.46, 0.36, 0.26, 1.0))
    make_box("Store_Register", (gx + 2.2, sy0 + 2.4, 1.12), (0.42, 0.36, 0.24), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Store_DeskFan_Head", (gx + 3.3, sy0 + 2.4, 1.22), 0.16, 0.08, (0.80, 0.80, 0.76, 1.0), axis='Y', segments=12)
    make_box("Store_DeskFan_Base", (gx + 3.3, sy0 + 2.5, 1.04), (0.16, 0.16, 0.08), (0.60, 0.60, 0.58, 1.0))
    make_box("Galaga_Cabinet", (gx - 3.6, sy0 + 1.4, 0.88), (0.66, 0.74, 1.76), (0.12, 0.12, 0.14, 1.0))
    make_box("Galaga_Screen", (gx - 3.6, sy0 + 1.02, 1.30), (0.50, 0.02, 0.40), (0.10, 0.16, 0.26, 1.0))
    make_box("Galaga_Marquee", (gx - 3.6, sy0 + 1.02, 1.66), (0.56, 0.02, 0.16), (0.90, 0.40, 0.20, 1.0))
    for k in range(3):
        make_box(f"Candy_Rack_{k}", (gx - 0.6, sy0 + 3.0 + k * 0.01, 0.45 + k * 0.4), (2.0, 0.4, 0.04), (0.70, 0.70, 0.68, 1.0))
    make_box("Curio_Shelf", (gx - 2.2, sy0 + 6.6, 1.2), (2.4, 0.4, 2.0), WOOD)
    r = _rng(5)
    for k in range(12):
        make_box(f"Curio_Stock_{k}", (gx - 3.2 + (k % 6) * 0.38, sy0 + 6.5, 0.6 + (k // 6) * 0.7 + 0.08), (0.24, 0.16, 0.10), (0.56 + r() * 0.2, 0.46, 0.30, 1.0))
    # out front: the ice chest, the pump island, the pole sign
    make_box("Ice_Chest", (gx + 3.6, sy0 - 0.9, 0.62), (1.6, 0.8, 1.24), (0.92, 0.94, 0.96, 1.0))
    make_box("Ice_Chest_Band", (gx + 3.6, sy0 - 1.31, 0.92), (1.5, 0.02, 0.32), (0.22, 0.46, 0.78, 1.0))
    make_box("Island", (gx, gy, 0.08), (6.0, 1.2, 0.16), (0.70, 0.70, 0.66, 1.0))
    for k, px in enumerate((gx - 1.6, gx + 1.6)):
        make_box(f"Pump_{k}", (px, gy, 0.86), (0.7, 0.5, 1.4), (0.80, 0.20, 0.16, 1.0))
        make_box(f"Pump_{k}_Face", (px, gy - 0.26, 1.12), (0.5, 0.02, 0.5), (0.90, 0.88, 0.82, 1.0))
        make_cyl(f"Pump_{k}_Globe", (px, gy, 1.72), 0.22, 0.30, (0.96, 0.92, 0.80, 1.0), segments=12)
        make_tube(f"Pump_{k}_Hose", [(px + 0.36, gy, 1.2), (px + 0.6, gy - 0.2, 0.5), (px + 0.4, gy - 0.3, 0.3)], 0.025, (0.08, 0.08, 0.08, 1.0), segments=5)
    make_box("Station_Sign_Pole", (gx + 10.0, gy - 6.0, 3.5), (0.24, 0.24, 7.0), (0.60, 0.60, 0.58, 1.0))
    make_box("Station_Sign", (gx + 10.0, gy - 6.0, 6.4), (3.0, 0.20, 1.6), (0.92, 0.88, 0.76, 1.0))
    # the town that isn't one: a shuttered café, a house, a dead pickup
    make_box("Town_Cafe", (gx - 20.0, gy + 10.0, 1.6), (10.0, 8.0, 3.2), (0.72, 0.64, 0.52, 1.0))
    make_box("Town_Cafe_Boards", (gx - 20.0, gy + 5.98, 1.4), (4.0, 0.04, 1.2), (0.46, 0.36, 0.26, 1.0))
    make_box("Town_House", (gx + 24.0, gy + 14.0, 1.4), (8.0, 7.0, 2.8), (0.80, 0.74, 0.62, 1.0))
    make_rot_box("Town_House_Roof", (gx + 24.0, gy + 14.0, 3.1), (8.6, 7.6, 0.16), (0.36, 0.30, 0.26, 1.0), roll=0.1)
    make_car("Town_DeadPickup", gx + 18.0, gy + 2.0, 5.2, (0.50, 0.42, 0.34, 1.0), pickup=True, along="X")
    # the Voyager at the pump; the mud man at the ice chest
    voyager("VoyagerGas", gx - 1.6, gy - 2.6, along="X")
    make_box("MudMan_Legs", (gx + 2.7, sy0 - 1.0, 0.42), (0.30, 0.22, 0.84), (0.30, 0.26, 0.22, 1.0))
    make_box("MudMan_Torso", (gx + 2.7, sy0 - 1.0, 1.15), (0.42, 0.26, 0.62), (0.62, 0.42, 0.34, 1.0))
    make_cyl("MudMan_Head", (gx + 2.7, sy0 - 1.0, 1.62), 0.11, 0.24, (0.70, 0.50, 0.42, 1.0), segments=8)


def build_motel():
    """Some twenty miles down: an L of single-storey rooms round a court
    with the pool, the office at the corner where the elderly woman
    watches the television, the pole sign by the road. One room (No. 4)
    is built inside: the single bed, the TV, the lamp, the bathroom door."""
    mx, my = -400.0, 0.0
    make_box("Motel_Road", (mx, my - 26.0, -0.02), (300.0, 9.0, 0.04), ASPHALT)
    make_box("Motel_Lot", (mx, my - 12.0, -0.015), (60.0, 18.0, 0.03), (0.30, 0.30, 0.30, 1.0))
    wall = (0.88, 0.80, 0.66, 1.0)
    trim = (0.30, 0.52, 0.56, 1.0)
    # wing A: eight rooms along x, facing south (front y = my + 14)
    fy = my + 14.0
    make_box("WingA_Back", (mx, fy + 8.0, 1.4), (34.0, 0.24, 2.8), wall)
    make_box("WingA_Roof", (mx, fy + 4.0, 2.92), (35.0, 9.8, 0.2), (0.62, 0.36, 0.24, 1.0))
    make_box("WingA_Walk", (mx, fy - 0.96, 0.06), (34.0, 1.68, 0.12), (0.72, 0.70, 0.66, 1.0))   # (round 4) to the fronts' face
    for k in range(9):
        make_box(f"WingA_Party_{k}", (mx - 17.0 + k * 4.25, fy + 4.0, 1.4), (0.2, 8.0, 2.8), wall)
    for k in range(8):
        rx = mx - 17.0 + 2.125 + k * 4.25
        if k == 3:
            continue                   # No. 4 is built as a room below
        make_box(f"WingA_Front_{k}", (rx, fy, 1.4), (4.25, 0.24, 2.8), wall)
        make_box(f"WingA_Door_{k}", (rx - 1.1, fy - 0.13, 1.05), (0.9, 0.04, 2.1), trim)
        make_box(f"WingA_Window_{k}", (rx + 0.8, fy - 0.13, 1.5), (1.6, 0.04, 1.0), (0.40, 0.42, 0.44, 1.0))
    # room No. 4, open to the camera through its door, lit inside
    r4 = mx - 17.0 + 2.125 + 3 * 4.25
    make_box("Room4_Front_W", (r4 - 1.70, fy, 1.4), (0.65, 0.24, 2.8), wall)   # (round 4) between the party walls
    make_box("Room4_Front_Mid", (r4 + 0.0, fy, 2.45), (2.75, 0.24, 0.7), wall)
    make_box("Room4_Front_E", (r4 + 1.70, fy, 1.4), (0.65, 0.24, 2.8), wall)
    make_box("Room4_Front_Sill", (r4 + 0.8, fy, 0.45), (1.25, 0.24, 0.9), wall)
    make_box("Room4_Window", (r4 + 0.8, fy, 1.5), (1.25, 0.04, 1.0), (0.40, 0.42, 0.44, 1.0))
    make_box("Room4_Floor", (r4, fy + 3.0, 0.02), (4.0, 5.8, 0.02), (0.44, 0.34, 0.30, 1.0))
    make_box("Room4_Ceiling", (r4, fy + 4.0, 2.78), (4.0, 7.8, 0.04), (0.86, 0.84, 0.78, 1.0))
    make_box("Room4_Bath_Wall", (r4, fy + 6.0, 1.4), (4.0, 0.14, 2.8), wall)
    make_box("Room4_Bath_Door", (r4 + 1.2, fy + 5.92, 1.05), (0.8, 0.04, 2.1), (0.70, 0.62, 0.50, 1.0))
    make_bed("Room4_Bed", r4 - 0.6, fy + 4.92, head="+Y", w=1.0, d=2.0)   # (round 4) headboard to the bath wall (face fy + 5.93)
    make_box("Room4_Dresser", (r4 + 1.55, fy + 2.6, 0.42), (0.5, 1.6, 0.84), (0.42, 0.30, 0.22, 1.0))
    make_box("Room4_TV", (r4 + 1.5, fy + 2.6, 1.08), (0.46, 0.52, 0.44), (0.12, 0.12, 0.12, 1.0))
    make_box("Room4_TV_Screen", (r4 + 1.26, fy + 2.6, 1.10), (0.02, 0.40, 0.30), (0.40, 0.62, 0.72, 1.0))
    make_lamp("Room4_Lamp", r4 - 1.6, fy + 5.0, base_z=0.6)
    make_box("Room4_Nightstand", (r4 - 1.6, fy + 5.0, 0.30), (0.42, 0.42, 0.60), (0.42, 0.30, 0.22, 1.0))
    make_box("Room4_Curtain", (r4 + 0.8, fy + 0.18, 1.5), (1.4, 0.04, 1.2), (0.62, 0.38, 0.26, 1.0))
    make_box("Room4_Painting", (r4 - 0.6, fy + 5.9, 1.7), (0.9, 0.02, 0.6), (0.62, 0.42, 0.30, 1.0))
    make_chair("Room4_Chair", r4 + 1.2, fy + 1.0, yaw=math.pi * 0.75)
    # wing B: five rooms along y on the west, facing east; the office at the corner
    wx = mx - 17.0
    make_box("WingB_Back", (wx - 8.0, my, 1.4), (0.24, 26.0, 2.8), wall)
    make_box("WingB_Roof", (wx - 4.0, my, 2.92), (9.8, 26.0, 0.2), (0.62, 0.36, 0.24, 1.0))
    for k in range(5):
        ry = my - 11.0 + k * 4.4
        make_box(f"WingB_Front_{k}", (wx, ry, 1.4), (0.24, 4.4, 2.8), wall)
        make_box(f"WingB_Door_{k}", (wx + 0.13, ry - 1.1, 1.05), (0.04, 0.9, 2.1), trim)
        make_box(f"WingB_Window_{k}", (wx + 0.13, ry + 0.8, 1.5), (0.04, 1.6, 1.0), (0.40, 0.42, 0.44, 1.0))
    # the office: glass front, the counter, the television, the elderly woman
    ox, oy = mx + 21.0, my + 6.0
    make_box("Office", (ox, oy, 1.6), (7.0, 6.0, 3.2), wall)
    make_box("Office_Roof", (ox, oy, 3.3), (7.8, 6.8, 0.2), (0.62, 0.36, 0.24, 1.0))
    make_box("Office_Window", (ox, oy - 3.02, 1.5), (5.0, 0.04, 1.6), (0.92, 0.80, 0.56, 1.0))
    make_box("Office_Door", (ox - 2.8, oy - 3.02, 1.05), (0.9, 0.04, 2.1), trim)
    make_box("Office_Sign", (ox, oy - 3.06, 2.75), (4.0, 0.04, 0.4), trim)
    # the court: the pool and its concrete shorelines, the low fence, chairs
    px, py = mx - 2.0, my + 2.0
    # the concrete shorelines: four strips round the water (a whole slab hid it)
    deck = (0.80, 0.76, 0.70, 1.0)
    for tag, cx_, cy_, w, d in (("S", px, py - 3.75, 16.0, 2.5), ("N", px, py + 3.75, 16.0, 2.5),
                                ("W", px - 6.5, py, 3.0, 5.0), ("E", px + 6.5, py, 3.0, 5.0)):
        make_box(f"Pool_Deck_{tag}", (cx_, cy_, 0.03), (w, d, 0.06), deck)
    make_box("Pool_Water", (px, py, 0.02), (10.0, 5.0, 0.04), (0.18, 0.56, 0.70, 1.0), open_faces={'+Z'})
    make_box("Pool_Water_Surface", (px, py, 0.045), (9.9, 4.9, 0.01), (0.22, 0.60, 0.72, 1.0))
    make_box("Pool_Silt", (px + 1.4, py - 0.6, 0.052), (3.2, 1.6, 0.004), (0.62, 0.32, 0.24, 1.0))
    make_box("Pool_Coping", (px, py, 0.075), (10.4, 5.4, 0.03), (0.92, 0.90, 0.86, 1.0), open_faces={'+Z', '-Z'})
    for k in range(4):
        make_rot_box(f"Pool_Lounger_{k}", (px - 6.0 + k * 2.6, py - 4.2, 0.30), (0.7, 1.9, 0.12), (0.92, 0.92, 0.90, 1.0), yaw=0.0, roll=0.1)
    make_tube("Pool_Ladder", [(px + 4.6, py + 2.3, 0.0), (px + 4.6, py + 2.3, 0.9), (px + 4.6, py + 2.0, 0.9)], 0.025, (0.80, 0.80, 0.80, 1.0), segments=6)
    for k in range(17):
        make_cyl(f"PoolFence_Stock_{k}", (px - 8.0 + k * 1.0, py - 5.2, 0.6), 0.02, 1.2, (0.62, 0.62, 0.64, 1.0), segments=5)
    make_tube("PoolFence_Stock_Top", [(px - 8.0, py - 5.2, 1.2), (px + 8.0, py - 5.2, 1.2)], 0.02, (0.62, 0.62, 0.64, 1.0), segments=5)
    # the pole sign by the road, the cars, the Voyager
    make_box("Motel_Sign_Pole", (mx + 26.0, my - 20.0, 4.0), (0.3, 0.3, 8.0), (0.60, 0.60, 0.58, 1.0))
    make_box("Motel_Sign", (mx + 26.0, my - 20.0, 7.0), (4.4, 0.3, 2.2), trim)
    make_box("Motel_Sign_Vacancy", (mx + 26.0, my - 20.0, 5.4), (2.8, 0.24, 0.6), (0.90, 0.30, 0.24, 1.0))
    voyager("VoyagerMotel", mx + 6.0, my - 6.0, along="Y")
    make_car("MotelCar_0", mx - 8.0, my - 9.0, 4.8, (0.66, 0.62, 0.52, 1.0), along="Y")
    make_car("MotelCar_1", mx + 14.0, my - 8.0, 5.2, (0.36, 0.38, 0.42, 1.0), pickup=True, along="Y")


def _group_tagged(groups):
    """Parent each group's parts under its tagged empty (Blender only): the
    day's traffic and the storm's wreck share the one stretch of road, and
    Background3D strips the group a preset does not own."""
    if bpy is None:
        return
    for empty_name, prefixes in groups:
        empty = bpy.data.objects.new(empty_name, None)
        bpy.context.scene.collection.objects.link(empty)
        for obj in list(bpy.data.objects):
            if obj is not empty and obj.parent is None and obj.name.startswith(prefixes):
                obj.parent = empty


def main():
    clear_scene()
    build_desert()
    build_highway()
    build_highway_day()
    build_dust_storm()
    build_gas_station()
    build_motel()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    _group_tagged((("DayTraffic" + DAY, ("VoyagerDay", "SemiDay")),
                   ("StormWreck" + STORM, ("VoyagerStorm", "WreckSemi", "WreckWagon", "WreckDebris", "WreckFire", "WreckSmoke"))))
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/desert_route.glb"))
    print(f"\n[build_desert_route] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
