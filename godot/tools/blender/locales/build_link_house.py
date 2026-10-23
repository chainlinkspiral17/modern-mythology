"""link_house — vol 3's family house in Texas (draft 2, 2026-10-23).

DRAFT 2 — TWO STOREYS. The user (2026-10-23): "Dickens Dean/Link house is
two storey", upstairs "Three bedrooms and a small restroom/shower". Draft 1's
"single-storey brick ranch" was invented here, not the text's. Now:
  ground  (the user, 2026-10-23: "The downstairs is a mudroom, kitchen
          dining area, bathroom with a large raised sunken tub, living room
          with stairs going up") the living room (two storeys tall, W of
          LIV_X1, under the balcony), the kitchen and dining, the hall;
          behind the hall the bathroom with the big tub sunk in a raised
          tiled deck (W of BATHG_E) and the mudroom with the back door (E)
  stair   (draft 4) along the living room's N wall, climbing W to the
          landing in the NW corner
  upstairs (FL2) the bedroom wing lifted whole by plan.zoned (UP_WING):
          Andy's room, the second bedroom, the shower room (draft 1's tub
          is a shower stall); the parents' room over the kitchen (the third
          bedroom); the hall's balcony over the living room
The exterior walls run CEIL2 tall; stacked windows are one cut with a band
of wall between (_stack). The presets in the wing and their lights went up
2.9 m.
DRAFT 3 (2026-10-23, the user: "There is a large covered carport that
leads to the mudroom and with two connected outdoor rooms for storage, and
a front porch that overlooks a large pasture field leading to the river"):
build_grounds. The house up on its foundation (GZ); the front porch across
the living room and the door, its shed roof, rail and steps; the path to
the pasture gate; the pasture falling 5 m to the river (a heightfield bowl
so the porch sees the water), the far bank's trees; the carport E at the
mudroom's back door (stoop, steps), the two storage rooms at its N end
under the same roof, the pickup, the gravel drive out east; the clothesline
and the oak out back; the gable roof. Presets andy_house_porch /
andy_house_front / andy_house_carport (day).
DRAFT 4 (2026-10-23, the user: "Stairs run along the wall, not extend out
into the room. Bathroom at top near the stairway two rooms on one side a
large master on the other"): the stair hugs the living room's N wall (the
hall wall), its foot by the hall opening (moved E to x -0.95), climbing W
to a landing in the NW corner, the bookcase in the nook under it; the
living room two storeys tall to the master's wall. Upstairs the bathroom
is at the hall's W end, its door at the stair's head; the second bedroom
in the middle; Andy's room E (unchanged); the master over the kitchen. The
bath presets and lights moved with the bathroom (UB_DX).
DRAFT 5 (pass 151): white lap siding over the exterior walls (_clad: the
same openings, lap lines broken at them, a belt board at the upstairs
floor), corner boards; the master furnished (the second nightstand and
lamp, a rug, a cedar chest, an armchair and floor lamp by the window,
curtains); the second bedroom (nightstand, lamp, rug, desk and chair,
curtains); andy_house_stair from the landing.
DRAFT 6 targets: window casings and sills outside; shutters; a porch
light that lights at dusk; (older:) siding and trim on the house's outside faces (they carry
the interior paint); the upstairs windows' shutters; a porch light that
lights at night; a dusk preset from the porch; the storage rooms' insides;
the house from outside (the second storey's roofline);
the parents' room and the second bedroom dressed (doors shut in every
view); the den, laundry and study beyond a minimum; a setup down the stair
from the balcony; the living room's high windows' light at day.

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Vol 3's home scenes (the bg_places group once called andy_family_house) play
in one house (draft 1 called it a single-storey ranch; see draft 2): nine scene uses across the kitchen at
evening, the living room at night, the bathroom by day and before dawn, and
Andy's room by day, by night and by the bedside lamp. Two of the group's old
stems were somebody else's place: the blanket fort is the Chau house
(chau_house) and the Dallas closet is June's (they stay stand-ins).

What the scenes say, and where it is here:
  "Tony is looking at me, across from the table. The magazine sits between
   us."                                  → the dining table, two chairs
                                           facing, Magazine on the table
  "Nick was asleep on the couch when she came to me, the television showing
   a scary movie marathon."              → Sofa facing the TV on Wall_W,
                                           a blanket and a pillow on it;
                                           the TV's glow is the night key
  "My dad puts his ear to the bathroom door."  → the bathroom door on the
                                           hall, half open; tub, toilet,
                                           vanity under one light bar
  "I'm in the bathroom. It's the middle of the night or early in the
   morning."                             → the same room, the vanity light
                                           only (the night preset)
  "I rummage through my bedroom for a book" → Andy's room: the bookcase on
                                           its W wall, the bed, the bedside
                                           lamp, the desk under the N window

Plan (Blender: x east, y north, z up; Godot (x, z, -y)), 13 x 10.5 m,
ceiling 2.6:
  y 0.0..5.5   living room (x -6.5..-0.3) open to the kitchen and dining
               (x -0.3..6.5); front windows and the front door on Wall_S
  y 5.5..6.7   the hall, end to end
  y 6.7..10.5  the second bedroom (x -6.5..-1.2, door shut), the bathroom
               (x -1.2..1.6), Andy's room (x 1.6..6.5)

DRAFT 2 targets: the second bedroom's interior (its door is shut in every
view); the lake house's bathroom for vol3_family_bathroom_night if the
text means a different room ("The lake house · before dawn"); wear and
clutter (school photos down the hall, the fridge door, a laundry basket);
the backyard beyond the N windows as more than make_view's lawn; per-preset
props (the magazine only in the Uncle Nick scenes); Deck-verified framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_chamfer_box, make_lathe, make_tube, export_glb, join_stock
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_wall_with_openings, make_curtains
from _props.furniture import make_bed, make_chair, make_table, make_lamp, make_pendant, make_sofa
from _props.plan import zoned
from _props.decor import make_faded_poster, make_floor_plant
from _props.trees import make_broadleaf
from _props.vehicles import make_car
from _props.detail import make_far_bands
from _props.geometry import make_rot_box, make_heightfield, make_gable
from _props.safety import make_smoke_detector
from _props.detail import (make_traffic_wear, make_threshold, make_wall_outlet, make_light_switch,
                           make_thermostat, make_wall_tint_band)
from _props import kitchen_kit as K

X0, X1 = -6.5, 6.5
Y0, Y1 = 0.0, 10.5
HALL_S, HALL_N = 5.5, 6.7          # the hall's two walls (centre lines)
BATH_W, BATH_E = -1.2, 1.6         # the bathroom's side walls
CEIL = 2.6
T = 0.20                           # wall thickness
# TWO STOREYS (draft 2, 2026-10-23, the user: "Dickens Dean/Link house is two
# storey" — upstairs "three bedrooms and a small restroom/shower")
FL2 = 2.90                         # the upstairs floor
CEIL2 = FL2 + CEIL                 # the upstairs ceiling, and the living room's
LIV_X1 = -0.40                     # the living room rises two storeys W of here (to the master's wall)
PAR_X0 = -0.3                      # the parents' room over the kitchen, E of here
# the stair runs ALONG THE WALL (draft 4, the user: "Stairs run along the wall,
# not extend out into the room"): against the living room's N wall (the hall
# wall), its foot by the hall opening, climbing W to a landing in the NW corner
STAIR_Y0, STAIR_Y1 = HALL_S - T / 2.0 - 1.00, HALL_S - T / 2.0     # its width, off the wall
STAIR_FOOT, RUN, N_RISE = -1.60, 0.27, 16                          # the first riser's x; it climbs W
RISE = FL2 / N_RISE
STAIR_TOP = STAIR_FOOT - (N_RISE - 1) * RUN                        # the last riser's x, the landing W of it
# upstairs on the N side: the bathroom at the stair's head (W), the second
# bedroom, Andy's room (E); the master across the hall over the kitchen
UB_X0, UB_X1 = X0, -3.70
B2_X1 = BATH_E                     # the second bedroom runs from UB_X1 to Andy's W wall
UB_DX = (UB_X0 + UB_X1) / 2.0 - (BATH_W + BATH_E) / 2.0   # the bath's fixtures, moved from draft 2's place
B2_DX = 2.80                        # the second bedroom's furniture, moved E with it
UP_WING = [(X0 - 1.0, 6.55, X1 + 1.0, Y1 + 1.0, 0.0, 0.0, FL2)]   # plan.zoned: the bedroom wing, lifted a storey

PAL_WALL = {"wall": (0.86, 0.80, 0.68, 1.0), "baseboard": (0.92, 0.90, 0.84, 1.0)}   # builder beige, white trim
PAL_BATH = {"wall": (0.80, 0.84, 0.80, 1.0), "baseboard": (0.92, 0.90, 0.84, 1.0)}   # a sage bathroom
CARPET = (0.62, 0.56, 0.46, 1.0); CARPET_SEAM = (0.56, 0.50, 0.41, 1.0)
VINYL = (0.80, 0.76, 0.66, 1.0); VINYL_SEAM = (0.70, 0.66, 0.57, 1.0)
TILE = (0.88, 0.87, 0.82, 1.0); TILE_SEAM = (0.70, 0.69, 0.65, 1.0)
OAK = (0.62, 0.46, 0.28, 1.0); OAK_DARK = (0.42, 0.30, 0.18, 1.0)
DOOR_WHITE = (0.93, 0.92, 0.88, 1.0)
SOFA = (0.46, 0.36, 0.28, 1.0); SOFA_CUSH = (0.52, 0.41, 0.32, 1.0)
ENAMEL = (0.95, 0.95, 0.93, 1.0); CHROME = (0.78, 0.79, 0.80, 1.0)
BLACK = (0.08, 0.08, 0.09, 1.0)
DOOR_H = 2.05
SIDING_HOUSE = (0.90, 0.89, 0.85, 1.0)
BATHG_E = 0.0                      # the downstairs bathroom (W) and the mudroom (E) behind the hall


def _stack(name, line, axis, openings, pal, t=T):
    """Two windows one over the other (the two storeys) are ONE cut in the
    wall with a band of wall between them: make_wall_with_openings cuts
    along the wall only, so stacked openings at the same place are merged
    here and the band between built as wall."""
    out, done = [], set()
    for i, o in enumerate(openings):
        if i in done:
            continue
        mate = next((j for j in range(i + 1, len(openings)) if j not in done
                     and abs(openings[j][0] - o[0]) < 1e-6 and abs(openings[j][2] - o[2]) < 1e-6), None)
        if mate is None:
            out.append(o)
            continue
        done.add(mate)
        lo, hi = sorted((o, openings[mate]), key=lambda q: q[1])
        b0, b1 = lo[1] + lo[3] / 2.0, hi[1] - hi[3] / 2.0
        z0, z1 = lo[1] - lo[3] / 2.0, hi[1] + hi[3] / 2.0
        out.append((o[0], (z0 + z1) / 2.0, o[2], z1 - z0))
        c = (o[0], line) if axis == 'X' else (line, o[0])
        make_box(f"{name}_Band_{i}", (c[0], c[1], (b0 + b1) / 2.0), (o[2], t, b1 - b0) if axis == 'X' else (t, o[2], b1 - b0),
                 pal["wall"])
    return out


def wall_x(name, y, x0, x1, openings=(), face=+1, pal=PAL_WALL, h=CEIL, z0=0.0):
    """A wall along X from x0 to x1 at y; openings as (x_centre, z_centre, w, h)."""
    ln, cx = x1 - x0, (x0 + x1) / 2.0
    openings = _stack(name, y, 'X', list(openings), pal)
    if openings or z0:
        make_wall_with_openings(name, (cx, y, 0), length=ln, height=h, thickness=T, axis='X',
                                palette=pal, baseboard_face_sign=face, openings=list(openings), base_z=z0)
    else:
        make_wall(name, (cx, y, z0), length=ln, height=h, thickness=T, axis='X', palette=pal,
                  baseboard_face_sign=face)


def wall_y(name, x, y0, y1, openings=(), face=+1, pal=PAL_WALL, h=CEIL, z0=0.0):
    ln, cy = y1 - y0, (y0 + y1) / 2.0
    openings = _stack(name, x, 'Y', list(openings), pal)
    if openings or z0:
        make_wall_with_openings(name, (x, cy, 0), length=ln, height=h, thickness=T, axis='Y',
                                palette=pal, baseboard_face_sign=face, openings=list(openings), base_z=z0)
    else:
        make_wall(name, (x, cy, z0), length=ln, height=h, thickness=T, axis='Y', palette=pal,
                  baseboard_face_sign=face)


def door_casing(name, x, y, w, axis='X'):
    """A white casing round a door opening in a wall at (x, y), both faces."""
    h = DOOR_H
    for side in (-1, 1):
        off = side * (T / 2.0 + 0.008)
        if axis == 'X':
            make_box(f"{name}_Head_{side:+d}", (x, y + off, h + 0.04), (w + 0.14, 0.016, 0.08), DOOR_WHITE)
            for s in (-1, 1):
                make_box(f"{name}_Leg_{side:+d}_{s:+d}", (x + s * (w / 2.0 + 0.035), y + off, h / 2.0), (0.07, 0.016, h), DOOR_WHITE)
        else:
            make_box(f"{name}_Head_{side:+d}", (x + off, y, h + 0.04), (0.016, w + 0.14, 0.08), DOOR_WHITE)
            for s in (-1, 1):
                make_box(f"{name}_Leg_{side:+d}_{s:+d}", (x + off, y + s * (w / 2.0 + 0.035), h / 2.0), (0.016, 0.07, h), DOOR_WHITE)


def _clad(name, axis, line, a0, a1, openings, sg):
    """The outside skin of an exterior wall: siding 2 cm thick over its outer
    face with the same openings (stacked ones merged, as the wall is), its
    lap lines broken at the windows and doors, a belt board at the upstairs
    floor."""
    pal = {"wall": SIDING_HOUSE, "baseboard": TRIM}
    ops = _stack(name, line, axis, list(openings), pal, t=0.022)
    anchor = ((a0 + a1) / 2.0, line, 0) if axis == 'X' else (line, (a0 + a1) / 2.0, 0)
    make_wall_with_openings(name, anchor, length=a1 - a0, height=CEIL2, thickness=0.022, axis=axis, palette=pal,
                            baseboard_face_sign=sg, openings=ops)
    lap = (0.74, 0.74, 0.70, 1.0)
    face = line + sg * 0.014
    j = 0
    z = 0.30
    while z < CEIL2 - 0.10:
        if abs(z - (FL2 - 0.05)) < 0.16:      # the belt board's band
            z += 0.22
            continue
        cuts = sorted((o[0] - o[2] / 2.0 - 0.02, o[0] + o[2] / 2.0 + 0.02) for o in openings
                      if o[1] - o[3] / 2.0 - 0.03 < z < o[1] + o[3] / 2.0 + 0.03)
        cur = a0
        for c0, c1 in cuts + [(a1, a1)]:
            if c0 - cur > 0.05:
                m, ln = (cur + c0) / 2.0, c0 - cur
                make_box(f"{name}_Stock_Lap_{j}", (m, face, z) if axis == 'X' else (face, m, z), (ln, 0.006, 0.014) if axis == 'X' else (0.006, ln, 0.014), lap)
                j += 1
            cur = max(cur, c1)
        z += 0.22
    belt = (a1 - a0, 0.03, 0.20) if axis == 'X' else (0.03, a1 - a0, 0.20)
    make_box(f"{name}_Belt", (((a0 + a1) / 2.0, line + sg * 0.026, FL2 - 0.05) if axis == 'X' else (line + sg * 0.026, (a0 + a1) / 2.0, FL2 - 0.05)), belt, TRIM)


def build_shell():
    """The two-storey box and the ground floor. The bedroom wing upstairs is
    build_upper_wing (lifted by plan.zoned); the stair, the balcony and the
    parents' room are build_stair_and_upstairs."""
    # ground floors: carpet in the living room and hall, vinyl in the kitchen; behind
    # the hall the bathroom with the big tub (tile) and the mudroom (vinyl)
    make_floor("Floor_Living", (-3.40, 2.75, 0.0), size_x=6.2, size_y=5.5, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Kitchen", (3.10, 2.75, 0.0), size_x=6.8, size_y=5.5, palette={"vinyl": VINYL, "seam": VINYL_SEAM})
    make_floor("Floor_Hall", (0.0, 6.10, 0.0), size_x=13.4, size_y=1.2, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Bath_G", ((X0 + BATHG_E) / 2.0, 8.60, 0.0), size_x=BATHG_E - X0, size_y=3.8, palette={"vinyl": TILE, "seam": TILE_SEAM})
    make_floor("Floor_Mud", ((BATHG_E + X1) / 2.0, 8.60, 0.0), size_x=X1 - BATHG_E, size_y=3.8, palette={"vinyl": VINYL, "seam": VINYL_SEAM})
    # the ground ceiling is the underside of the upstairs floor, cut where the
    # living room goes up two storeys and where the stair goes through
    ceil = (0.94, 0.93, 0.89, 1.0)
    for nm, (x0, y0, x1, y1) in (("Kitchen", (PAR_X0 - T / 2.0, Y0, X1 + 0.1, 5.40)), ("Back", (X0 - 0.1, 5.40, X1 + 0.1, Y1 + 0.1)),
                                 ("Landing", (X0 + T / 2.0, STAIR_Y0, STAIR_TOP, STAIR_Y1))):
        make_box(f"Slab_{nm}", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, CEIL + 0.095), (x1 - x0, y1 - y0, 0.19), ceil)
    make_ceiling("Ceil", (0.0, (Y0 + Y1) / 2.0, CEIL2), size_x=X1 - X0 + 0.4, size_y=Y1 - Y0 + 0.4,
                 with_grid=False, with_stains=False, palette={"tile": (0.94, 0.93, 0.89, 1.0)})

    # the exterior, two storeys tall: Wall_S has the living window and its
    # high window over it (the living room is two storeys), the front door,
    # the kitchen window and the parents' window over it
    ext_s = [(-4.2, 1.45, 2.0, 1.40), (-4.2, FL2 + 1.20, 2.0, 1.20), (-1.0, DOOR_H / 2.0, 0.95, DOOR_H),
             (4.2, 1.50, 1.60, 1.20), (3.0, FL2 + 1.45, 1.60, 1.30)]
    wall_x("Wall_S", Y0, X0 - 0.1, X1 + 0.1, face=+1, h=CEIL2, openings=ext_s)
    # Wall_N: the tub's window and the bathroom's small one, the mudroom's below; bed 2, the shower room
    # and Andy's room above (their windows are build_upper_wing's)
    ext_n = [(-4.0, 1.45, 1.40, 1.30), (-0.30, 1.85, 0.70, 0.55), (4.0, 1.45, 1.40, 1.30),
             ((UB_X1 + B2_X1) / 2.0, FL2 + 1.45, 1.40, 1.30), ((UB_X0 + UB_X1) / 2.0 - 0.50, FL2 + 1.85, 0.70, 0.55),
             (4.0, FL2 + 1.45, 1.40, 1.30)]
    wall_x("Wall_N", Y1, X0 - 0.1, X1 + 0.1, face=-1, h=CEIL2, openings=ext_n)
    ext_w = [(2.8, FL2 + 1.10, 1.60, 1.20), (8.6, 1.45, 1.40, 1.30)]
    wall_y("Wall_W", X0, Y0, Y1, face=+1, h=CEIL2, openings=ext_w)
    ext_e = [(2.2, 1.45, 1.60, 1.30), (2.2, FL2 + 1.45, 1.60, 1.30), (8.6, DOOR_H / 2.0, 0.95, DOOR_H)]   # the mudroom's back door
    wall_y("Wall_E", X1, Y0, Y1, face=-1, h=CEIL2, openings=ext_e)
    # the outside: white lap siding over the exterior walls (they showed the
    # rooms' paint), corner boards, a belt board between the storeys
    for nm, ax, line, a0, a1, ops, sg in (("S", 'X', Y0 - T / 2.0, X0 - T / 2.0, X1 + T / 2.0, ext_s, -1),
                                          ("N", 'X', Y1 + T / 2.0, X0 - T / 2.0, X1 + T / 2.0, ext_n, +1),
                                          ("W", 'Y', X0 - T / 2.0, Y0 - T / 2.0, Y1 + T / 2.0, ext_w, -1),
                                          ("E", 'Y', X1 + T / 2.0, Y0 - T / 2.0, Y1 + T / 2.0, ext_e, +1)):
        _clad(f"Siding_{nm}", ax, line + sg * 0.011, a0 - 0.022, a1 + 0.022, ops, sg)
    for k, (cx, cy) in enumerate(((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1))):
        make_box(f"Corner_Board_{k}", (cx + (0.06 if cx > 0 else -0.06) * 2.2, cy + (0.06 if cy > 0 else -0.06) * 2.2, CEIL2 / 2.0),
                 (0.12, 0.12, CEIL2), TRIM)
    # the ground hall: the living room's wide cased opening and the kitchen's
    # door on its S wall; the bathroom's door and the mudroom's wide opening on its N wall
    wall_x("Wall_Hall_S", HALL_S, X0, X1, face=-1, openings=[(-0.95, 1.05, 0.95, 2.10), (0.50 + 0.25, DOOR_H / 2.0, 0.80, DOOR_H)])
    wall_x("Wall_Hall_N_G", HALL_N, X0, X1, face=-1, openings=[(-2.4, DOOR_H / 2.0, 0.86, DOOR_H),
                                                                      (2.6, DOOR_H / 2.0, 1.20, DOOR_H)])
    wall_y("Wall_Bath_G_E", BATHG_E, HALL_N, Y1, face=+1, pal=PAL_BATH)
    for nm, x, y, w, ax in (("Case_Front", -1.0, Y0, 0.95, 'X'), ("Case_Living", -0.95, HALL_S, 0.95, 'X'),
                            ("Case_Kitchen", 0.75, HALL_S, 0.80, 'X'), ("Case_Bath_G", -2.4, HALL_N, 0.86, 'X'),
                            ("Case_Mud", 2.6, HALL_N, 1.20, 'X'), ("Case_Back_Door", X1, 8.6, 0.95, 'Y')):
        door_casing(nm, x, y, w, ax)

    # windows: front windows see the street, back windows the yard
    make_window("Win_Living", (-4.2, Y0 + 0.10, 1.45), width=2.0, height=1.40, see_through=True, room_dir=+1)
    make_window("Win_Living_High", (-4.2, Y0 + 0.10, FL2 + 1.20), width=2.0, height=1.20, see_through=True, room_dir=+1)
    make_window("Win_Living_W_High", (X0 + 0.10, 2.8, FL2 + 1.10), width=1.60, height=1.20, axis='Y', see_through=True, room_dir=+1)
    make_window("Win_Kitchen", (4.2, Y0 + 0.10, 1.50), width=1.60, height=1.20, see_through=True, room_dir=+1)
    make_window("Win_Dining", (X1 - 0.10, 2.2, 1.45), width=1.60, height=1.30, axis='Y', see_through=True)
    make_window("Win_Parents_S", (3.0, Y0 + 0.10, FL2 + 1.45), width=1.60, height=1.30, see_through=True, room_dir=+1)
    make_window("Win_Parents_E", (X1 - 0.10, 2.2, FL2 + 1.45), width=1.60, height=1.30, axis='Y', see_through=True)
    frost = {"glass": (0.86, 0.90, 0.90, 0.85), "warm": (0.92, 0.92, 0.88, 0.9)}
    make_window("Win_Tub", (-4.0, Y1 - 0.10, 1.45), width=1.40, height=1.30, palette=frost)
    make_window("Win_Bath_G_W", (X0 + 0.10, 8.6, 1.45), width=1.40, height=1.30, axis='Y', room_dir=+1, palette=frost)
    make_window("Win_Bath_G_Small", (-0.30, Y1 - 0.10, 1.85), width=0.70, height=0.55, cross_mullion=False, palette=frost)
    make_window("Win_Mud", (4.0, Y1 - 0.10, 1.45), width=1.40, height=1.30, see_through=True)
    # blinds half down in the front windows (a Texas house keeps the sun out)
    for nm, x, y, w, z_top, drop, sgn in (("Blind_Living", -4.2, Y0 + 0.17, 2.0, 2.15, 0.55, +1),
                                          ("Blind_Kitchen", 4.2, Y0 + 0.17, 1.6, 2.10, 0.35, +1)):
        make_box(f"{nm}_Rail", (x, y, z_top), (w + 0.06, 0.05, 0.05), DOOR_WHITE)
        for k in range(int(drop / 0.05)):
            make_box(f"{nm}_Slat_{k}", (x, y, z_top - 0.05 - k * 0.05), (w, 0.03, 0.006), (0.94, 0.93, 0.89, 1.0))
    # doors: the front door shut, the downstairs bathroom's shut, the back door
    # out of the mudroom shut with a lite in it
    make_box("Door_Front", (-1.0, Y0 + 0.03, DOOR_H / 2.0), (0.92, 0.045, DOOR_H - 0.02), (0.36, 0.20, 0.14, 1.0))
    make_cyl("Door_Front_Knob", (-0.66, Y0 + 0.0825, 0.98), 0.03, 0.06, (0.70, 0.58, 0.30, 1.0), axis='Y', segments=10)
    make_box("Door_Bath_G", (-2.4, HALL_N - 0.02, DOOR_H / 2.0), (0.84, 0.04, DOOR_H - 0.02), DOOR_WHITE)
    make_cyl("Door_Bath_G_Knob", (-2.08, HALL_N - 0.065, 0.98), 0.028, 0.05, CHROME, axis='Y', segments=10)
    make_box("Door_Back", (X1 - 0.03, 8.6, DOOR_H / 2.0), (0.045, 0.92, DOOR_H - 0.02), (0.36, 0.42, 0.40, 1.0))
    make_box("Door_Back_Lite", (X1 - 0.03, 8.6, 1.50), (0.05, 0.56, 0.60), (0.80, 0.86, 0.90, 0.30))
    make_cyl("Door_Back_Knob", (X1 - 0.085, 8.6 - 0.36, 0.98), 0.03, 0.06, CHROME, axis='X', segments=10)


def build_upper_wing():
    """The bedroom wing upstairs, authored at ground level and lifted FL2 by
    plan.zoned (main). Draft 4 (the user: "Bathroom at top near the
    stairway two rooms on one side a large master on the other"): the
    bathroom at the hall's W end by the stair's head, the second bedroom in
    the middle, Andy's room E; the master is build_stair_and_upstairs'."""
    b2c = (UB_X1 + B2_X1) / 2.0
    ubc = (UB_X0 + UB_X1) / 2.0
    make_floor("Floor_Bath", (ubc, 8.60, 0.0), size_x=UB_X1 - UB_X0, size_y=3.8, palette={"vinyl": TILE, "seam": TILE_SEAM})
    make_floor("Floor_Bed2", (b2c, 8.60, 0.0), size_x=B2_X1 - UB_X1, size_y=3.8, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Bedroom", (4.05, 8.60, 0.0), size_x=4.9, size_y=3.8, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    DB, D2, DA = ubc, b2c - 0.40, 3.20          # the three doors on the hall
    wall_x("Wall_Hall_N", HALL_N, X0, X1, face=-1, openings=[(DB, DOOR_H / 2.0, 0.81, DOOR_H), (D2, DOOR_H / 2.0, 0.86, DOOR_H),
                                                                    (DA, DOOR_H / 2.0, 0.86, DOOR_H)])
    wall_y("Wall_Bath_E", UB_X1, HALL_N, Y1, face=-1, pal=PAL_BATH)
    wall_y("Wall_Bed2_E", B2_X1, HALL_N, Y1, face=-1)
    for nm, x, w in (("Case_Bath", DB, 0.81), ("Case_Bed2", D2, 0.86), ("Case_Bedroom", DA, 0.86)):
        door_casing(nm, x, HALL_N, w, 'X')
    make_window("Win_Bed2", (b2c, Y1 - 0.10, 1.45), width=1.40, height=1.30, see_through=True)
    make_window("Win_Bedroom", (4.0, Y1 - 0.10, 1.45), width=1.40, height=1.30, see_through=True)
    make_window("Win_Bath", (ubc - 0.50, Y1 - 0.10, 1.85), width=0.70, height=0.55, cross_mullion=False,
                palette={"glass": (0.86, 0.90, 0.90, 0.85), "warm": (0.92, 0.92, 0.88, 0.9)})
    nm, x, y, w, z_top, drop = "Blind_Bedroom", 4.0, Y1 - 0.17, 1.4, 2.10, 0.50
    make_box(f"{nm}_Rail", (x, y, z_top), (w + 0.06, 0.05, 0.05), DOOR_WHITE)
    for k in range(int(drop / 0.05)):
        make_box(f"{nm}_Slat_{k}", (x, y, z_top - 0.05 - k * 0.05), (w, 0.03, 0.006), (0.94, 0.93, 0.89, 1.0))
    # doors: the second bedroom's shut, the bathroom's half open (into the
    # room, hinge on its E jamb), Andy's open against its W wall
    make_box("Door_Bed2", (D2, HALL_N + 0.02, DOOR_H / 2.0), (0.84, 0.04, DOOR_H - 0.02), DOOR_WHITE)
    make_cyl("Door_Bed2_Knob", (D2 + 0.32, HALL_N - 0.025, 0.98), 0.028, 0.05, CHROME, axis='Y', segments=10)
    # the bath door swung 95 degrees into the bathroom on its E-jamb hinge,
    # flat to the room's east side, so the doorway (and the camera in it)
    # sees the toilet, the shower and the vanity
    import math
    a = math.radians(95.0)
    hx, hy, dw = DB + 0.405, HALL_N + 0.12, 0.79
    dx, dy = -math.cos(a), math.sin(a)
    make_rot_box("Door_Bath", (hx + dx * dw / 2.0, hy + dy * dw / 2.0, DOOR_H / 2.0),
                 (dw, 0.04, DOOR_H - 0.02), DOOR_WHITE, yaw=math.atan2(dy, dx))
    make_box("Door_Bedroom", (DA - 0.40, HALL_N + 0.10 + 0.43, DOOR_H / 2.0), (0.04, 0.84, DOOR_H - 0.02), DOOR_WHITE)
    # the upstairs hall's photographs on its N wall, the switches, the outlet by Andy's bed
    for k, x in enumerate((-3.10, -2.35, 0.55, 1.30)):
        make_box(f"Hall_Photo_{k}", (x, HALL_N - T / 2.0 - 0.012, 1.55 + (k % 2) * 0.12), (0.30, 0.02, 0.38), (0.24, 0.18, 0.14, 1.0))
        make_box(f"Hall_Photo_{k}_Print", (x, HALL_N - T / 2.0 - 0.024, 1.55 + (k % 2) * 0.12), (0.24, 0.004, 0.30),
                 ((0.70, 0.62, 0.50, 1.0) if k % 2 else (0.56, 0.62, 0.66, 1.0)))
    make_light_switch("Switch_Bath", (DB + 0.60, HALL_N), axis='X', face_sign=-1)
    make_light_switch("Switch_Bedroom", (2.65, HALL_N), axis='X', face_sign=-1)
    make_wall_outlet("Outlet_Bed", (X1, 9.00), axis='Y', face_sign=-1)
    make_threshold("Threshold_Bath", (DB, HALL_N), width=0.8, axis='X')


def build_stair_and_upstairs():
    """The stair along the living room's N wall, its foot by the hall
    opening, climbing W to the landing in the NW corner at the upstairs
    hall's W end (the bathroom's door); the balcony over the living room;
    the master over the kitchen (its door shut)."""
    from _props.geometry import make_tube
    yc, w = (STAIR_Y0 + STAIR_Y1) / 2.0, STAIR_Y1 - STAIR_Y0
    for k in range(N_RISE - 1):
        x1 = STAIR_FOOT - k * RUN          # this tread's E edge (its riser)
        zt = (k + 1) * RISE
        make_box(f"Stair_Stock_Step_{k}", (x1 - RUN / 2.0, yc, zt / 2.0), (RUN, w, zt), (0.50, 0.38, 0.24, 1.0))
        make_box(f"Stair_Stock_Tread_{k}", (x1 - RUN / 2.0 + 0.01, yc, zt + 0.008), (RUN + 0.02, w, 0.016), CARPET)
    # the stringer on the room side, the balustrade over it, a newel at the
    # foot, the handrail on the wall
    by = STAIR_Y0 - 0.03

    def rail_z(x):
        t = min(1.0, max(0.0, (STAIR_FOOT - x) / (STAIR_FOOT - STAIR_TOP)))
        return RISE + 0.90 + t * (FL2 - RISE)
    make_box("Stair_Newel", (STAIR_FOOT + 0.05, by, 0.55), (0.09, 0.09, 1.10), DOOR_WHITE)
    make_tube("Stair_Rail", [(STAIR_FOOT + 0.05, by, 1.08), (STAIR_TOP, by, FL2 + 0.90)], 0.028, OAK_DARK, segments=8)
    make_tube("Stair_Wall_Rail", [(STAIR_FOOT, STAIR_Y1 - 0.06, RISE + 0.86), (STAIR_TOP, STAIR_Y1 - 0.06, FL2 + 0.86)], 0.022, OAK_DARK, segments=8)
    for k in range(N_RISE - 1):
        for m in range(2):
            x = STAIR_FOOT - k * RUN - 0.07 - m * 0.13
            zt = (k + 1) * RISE
            top = rail_z(x)
            make_box(f"Stair_Stock_Bal_{k}_{m}", (x, by, (zt + top) / 2.0), (0.025, 0.025, top - zt), DOOR_WHITE)
    # under the landing, the bookcase in its nook
    # the upstairs: the hall's carpet, the landing, the master's floor
    make_floor("Floor_Up_Hall", (0.0, (5.40 + HALL_N) / 2.0, FL2), size_x=X1 - X0, size_y=HALL_N - 5.40, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Up_Landing", ((X0 + T / 2.0 + STAIR_TOP) / 2.0, yc, FL2), size_x=STAIR_TOP - X0 - T / 2.0, size_y=w,
               palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    make_floor("Floor_Parents", ((PAR_X0 + X1) / 2.0, 5.40 / 2.0, FL2), size_x=X1 - PAR_X0, size_y=5.40, palette={"vinyl": CARPET, "seam": CARPET_SEAM})
    # the balcony's edge over the living room: fascias and the balustrade,
    # from the landing to the master's wall; the landing's own rail
    make_box("Balcony_Fascia", ((STAIR_TOP + LIV_X1) / 2.0, 5.40 - 0.012, CEIL + 0.14), (LIV_X1 - STAIR_TOP, 0.024, 0.40), DOOR_WHITE)
    make_box("Landing_Fascia", ((X0 + T / 2.0 + STAIR_TOP) / 2.0, STAIR_Y0 - 0.012, CEIL + 0.14), (STAIR_TOP - X0 - T / 2.0, 0.024, 0.40), DOOR_WHITE)
    make_box("Stairwell_Fascia_E", (PAR_X0 - T / 2.0 - 0.012, 5.40 / 2.0, CEIL + 0.14), (0.024, 5.40, 0.40), DOOR_WHITE)
    for nm, (ax, ay), (bx, b2) in (("Balcony", (STAIR_TOP + 0.04, 5.40 + 0.05), (LIV_X1 - 0.05, 5.40 + 0.05)),
                                   ("Landing", (X0 + T / 2.0 + 0.05, STAIR_Y0 + 0.05), (STAIR_TOP, STAIR_Y0 + 0.05))):
        L = abs(bx - ax) + abs(b2 - ay)
        n = max(2, int(L / 0.13))
        for k in range(n + 1):
            t = k / n
            px, py = ax + (bx - ax) * t, ay + (b2 - ay) * t
            if k in (0, n):
                make_box(f"{nm}_Post_{k}", (px, py, FL2 + 0.48), (0.08, 0.08, 0.96), DOOR_WHITE)
            else:
                make_box(f"{nm}_Stock_Bal_{k}", (px, py, FL2 + 0.46), (0.025, 0.025, 0.92), DOOR_WHITE)
        along_x = abs(bx - ax) > 0.01
        make_box(f"{nm}_Rail", ((ax + bx) / 2.0, (ay + b2) / 2.0, FL2 + 0.94), ((L + 0.08) if along_x else 0.07, 0.07 if along_x else (L + 0.08), 0.05), OAK_DARK)
    # the master: its W wall over the living room's E edge, its N wall on the
    # upstairs hall with the door, the bed, a dresser, the lamp
    wall_y("Wall_Parents_W", PAR_X0, Y0, 5.50, face=-1, h=CEIL, z0=FL2)
    wall_x("Wall_Parents_N", 5.50, PAR_X0, X1, face=+1, h=CEIL, z0=FL2, openings=[(2.4, DOOR_H / 2.0, 0.86, DOOR_H)])   # z from the wall's base (FL2)
    make_box("Door_Parents", (2.4, 5.50 + 0.02, FL2 + DOOR_H / 2.0), (0.84, 0.04, DOOR_H - 0.02), DOOR_WHITE)
    make_bed("Parents_Bed", PAR_X0 + 0.10 + 1.05, 2.6, head="-X", w=1.60, d=2.05, blanket_col=(0.66, 0.58, 0.50, 1.0), z0=FL2)
    make_box("Parents_Dresser", (X1 - 0.10 - 0.25, 4.30, FL2 + 0.45), (0.50, 1.40, 0.90), OAK)
    make_box("Parents_Nightstand", (PAR_X0 + 0.10 + 0.24, 4.00, FL2 + 0.30), (0.44, 0.44, 0.60), OAK)
    make_lamp("Lamp_Parents", PAR_X0 + 0.10 + 0.24, 4.00, base_z=FL2 + 0.60, h=0.52)
    # draft 5: the large master furnished — the other nightstand and lamp,
    # a rug under the bed, a cedar chest at its foot, an armchair and a
    # floor lamp by the front window, curtains on both windows
    make_box("Parents_Nightstand_S", (PAR_X0 + 0.10 + 0.24, 1.20, FL2 + 0.30), (0.44, 0.44, 0.60), OAK)
    make_lamp("Lamp_Parents_S", PAR_X0 + 0.10 + 0.24, 1.20, base_z=FL2 + 0.60, h=0.52)
    make_box("Parents_Rug", (PAR_X0 + 1.30, 2.6, FL2 + 0.006), (2.60, 2.40, 0.012), (0.56, 0.42, 0.36, 1.0))
    make_box("Parents_Chest", (PAR_X0 + 0.10 + 2.10 + 0.30, 2.6, FL2 + 0.24), (0.46, 1.10, 0.48), (0.52, 0.32, 0.20, 1.0))
    make_sofa("Parents_Armchair", 4.60, 0.95, back="-Y", w=0.92, d=0.86, seats=1, color=(0.62, 0.56, 0.44, 1.0), arm="roll", z0=FL2)
    make_lamp("Lamp_Parents_Floor", 5.40, 0.70, base_z=FL2, h=1.50)
    make_curtains("Parents_Curtains_S", (3.0, Y0 + 0.10, FL2 + 1.45), width=1.60, height=1.30, axis='X', room_dir=+1, color=(0.76, 0.70, 0.60, 1.0))
    make_curtains("Parents_Curtains_E", (X1 - 0.10, 2.2, FL2 + 1.45), width=1.60, height=1.30, axis='Y', room_dir=-1, color=(0.76, 0.70, 0.60, 1.0))
    # the upstairs hall: its light, the smoke detector
    make_cyl("Hall_Up_Light", (0.0, 6.05, CEIL2 - 0.05), 0.16, 0.08, (0.96, 0.94, 0.86, 1.0), segments=12)
    make_smoke_detector("Smoke_Hall_Up", (-1.8, 6.05, CEIL2))


def build_ground_back_rooms():
    """Behind the ground hall (the user, 2026-10-23: "The downstairs is a
    mudroom, kitchen dining area, bathroom with a large raised sunken tub,
    living room with stairs going up"): the bathroom W, its big tub sunk
    into a raised tiled deck under the N window, two steps up to it, the
    vanity, the toilet; the mudroom E, the back door out to the yard, the
    bench and cubbies and hooks, boots, the washer and dryer."""
    xi0, xi1 = X0 + T / 2.0, BATHG_E - T / 2.0
    yi0, yi1 = HALL_N + T / 2.0, Y1 - T / 2.0
    tile, grout = (0.86, 0.82, 0.74, 1.0), (0.72, 0.68, 0.60, 1.0)
    # the raised deck along the N wall, the tub sunk in it
    dx0, dx1, dy0, dh = xi0, xi0 + 3.90, yi1 - 2.10, 0.52
    make_box("Tub_Deck_Front", ((dx0 + dx1) / 2.0, dy0 + 0.05, dh / 2.0), (dx1 - dx0, 0.10, dh), tile)
    make_box("Tub_Deck_End", (dx1 - 0.05, (dy0 + yi1) / 2.0, dh / 2.0), (0.10, yi1 - dy0, dh), tile)
    tx0, tx1, ty0, ty1 = dx0 + 0.95, dx1 - 0.45, dy0 + 0.45, yi1 - 0.35      # the tub's rim, 2.5 x 1.3
    for nm, (a0, a1, b0, b1) in (("W", (dx0, tx0, dy0 + 0.10, yi1)), ("E", (tx1, dx1 - 0.10, dy0 + 0.10, yi1)),
                                 ("S", (tx0, tx1, dy0 + 0.10, ty0)), ("N", (tx0, tx1, ty1, yi1))):
        make_box(f"Tub_Deck_Top_{nm}", ((a0 + a1) / 2.0, (b0 + b1) / 2.0, dh - 0.03), (a1 - a0, b1 - b0, 0.06), tile)
        make_box(f"Tub_Deck_Body_{nm}", ((a0 + a1) / 2.0, (b0 + b1) / 2.0, (dh - 0.06) / 2.0), (a1 - a0, b1 - b0, dh - 0.06), grout)
    # the tub: its basin sunk 0.42 into the deck, a rounded rim, the water
    make_box("Tub_Basin", ((tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0, dh - 0.40), (tx1 - tx0, ty1 - ty0, 0.04), ENAMEL)
    for nm, (cx, cy, sx, sy) in (("S", ((tx0 + tx1) / 2.0, ty0 + 0.02, tx1 - tx0, 0.04)), ("N", ((tx0 + tx1) / 2.0, ty1 - 0.02, tx1 - tx0, 0.04)),
                                 ("W", (tx0 + 0.02, (ty0 + ty1) / 2.0, 0.04, ty1 - ty0)), ("E", (tx1 - 0.02, (ty0 + ty1) / 2.0, 0.04, ty1 - ty0))):
        make_box(f"Tub_Side_{nm}", (cx, cy, dh - 0.20), (sx, sy, 0.40), ENAMEL)
        make_box(f"Tub_Rim_{nm}", (cx, cy, dh + 0.008), (sx + 0.06 * (sx < 0.1), sy + 0.06 * (sy < 0.1), 0.016), ENAMEL)
    make_box("Tub_Water", ((tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0, dh - 0.16), (tx1 - tx0 - 0.08, ty1 - ty0 - 0.08, 0.01), (0.62, 0.78, 0.82, 0.45))
    make_cyl("Tub_Spout", ((tx0 + tx1) / 2.0, ty1 + 0.08, dh + 0.12), 0.025, 0.16, CHROME, axis='Y', segments=8)
    make_cyl("Tub_Spout_Neck", ((tx0 + tx1) / 2.0, ty1 + 0.15, dh + 0.07), 0.022, 0.14, CHROME, segments=8)
    for k, dxk in enumerate((-0.18, 0.18)):
        make_cyl(f"Tub_Tap_{k}", ((tx0 + tx1) / 2.0 + dxk, ty1 + 0.10, dh + 0.04), 0.03, 0.06, CHROME, segments=8)
    # two steps up onto the deck, in front of it
    for k, (h, d) in enumerate(((dh * 2.0 / 3.0, 0.30), (dh / 3.0, 0.60))):
        make_box(f"Tub_Step_{k}", ((tx0 + tx1) / 2.0, dy0 - d / 2.0, h / 2.0), (1.40, d, h), tile)
    # the things on the deck: towels rolled, a candle, a plant in the corner
    for k in range(3):
        make_cyl(f"Tub_Towel_{k}", (dx0 + 0.35, dy0 + 0.50 + k * 0.20, dh + 0.08), 0.08, 0.36, (0.92, 0.90, 0.84, 1.0), axis='X', segments=10)
    make_cyl("Tub_Candle", (tx1 + 0.22, dy0 + 0.40, dh + 0.06), 0.05, 0.12, (0.96, 0.94, 0.86, 1.0), segments=10)
    make_floor_plant("Tub_Plant", (dx1 - 0.30, yi1 - 0.30, dh), kind="fern")
    # the vanity on the E wall (a double sink), its mirror and light; the toilet by the door
    vx = xi1 - 0.29
    make_box("Vanity_G_Cab", (vx, 8.10, 0.40), (0.56, 1.60, 0.80), OAK)
    make_box("Vanity_G_Top", (vx - 0.01, 8.10, 0.82), (0.60, 1.64, 0.04), (0.92, 0.90, 0.86, 1.0))
    for k, y in enumerate((7.72, 8.48)):
        make_box(f"Vanity_G_Basin_{k}", (vx - 0.02, y, 0.835), (0.36, 0.44, 0.012), (0.82, 0.82, 0.80, 1.0))
        make_cyl(f"Vanity_G_Faucet_{k}", (xi1 - 0.07, y, 0.90), 0.02, 0.14, CHROME, segments=8)
    make_box("Vanity_G_Mirror", (xi1 - 0.008, 8.10, 1.45), (0.012, 1.50, 0.86), (0.78, 0.84, 0.86, 1.0))
    make_box("Vanity_G_LightBar", (xi1 - 0.05, 8.10, 1.98), (0.08, 1.20, 0.08), CHROME)
    make_box("Toilet_G_Tank", (xi0 + 0.11, yi0 + 0.55, 0.62), (0.20, 0.44, 0.38), ENAMEL)
    make_lathe("Toilet_G_Bowl", (xi0 + 0.48, yi0 + 0.55, 0.0), [(0.13, 0.0), (0.10, 0.08), (0.12, 0.25), (0.19, 0.40), (0.0, 0.40)],
               ENAMEL, segments=12)
    make_box("Bath_G_Rug", (-2.6, yi0 + 0.95, 0.006), (1.0, 0.60, 0.012), (0.46, 0.58, 0.62, 1.0))
    # the mudroom: the bench and cubbies on its W wall, the hooks over them,
    # boots under; the washer and dryer on the N wall; the mat at the back door
    mx = BATHG_E + T / 2.0
    make_box("Mud_Bench", (mx + 0.22, 8.60, 0.45), (0.44, 2.20, 0.05), OAK)
    make_box("Mud_Bench_Base", (mx + 0.22, 8.60, 0.21), (0.42, 2.16, 0.42), (0.88, 0.86, 0.80, 1.0))
    make_box("Mud_Backboard", (mx + 0.012, 8.60, 1.35), (0.024, 2.20, 0.90), (0.90, 0.88, 0.82, 1.0))
    make_box("Mud_Cubby_Shelf", (mx + 0.17, 8.60, 2.02), (0.34, 2.20, 0.03), (0.90, 0.88, 0.82, 1.0))
    for k in range(5):
        y = 7.70 + k * 0.45
        make_box(f"Mud_Hook_{k}", (mx + 0.07, y, 1.62), (0.10, 0.03, 0.03), (0.30, 0.30, 0.32, 1.0))
        if k in (0, 2, 3):
            make_rot_box(f"Mud_Coat_{k}", (mx + 0.12, y, 1.31), (0.16, 0.36, 0.62), ((0.30, 0.34, 0.44, 1.0), (0.52, 0.30, 0.20, 1.0),
                         (0.26, 0.40, 0.30, 1.0), (0.40, 0.40, 0.42, 1.0), (0.60, 0.50, 0.30, 1.0))[k], yaw=0.0)
    for k in range(4):
        make_box(f"Mud_Boot_{k}", (mx + 0.62, 7.75 + k * 0.30, 0.13), (0.28, 0.11, 0.26), ((0.30, 0.22, 0.14, 1.0), (0.16, 0.16, 0.18, 1.0))[k % 2])
    for k, x in enumerate((2.10, 2.80)):
        make_box(f"Mud_{('Washer', 'Dryer')[k]}", (x, yi1 - 0.34, 0.45), (0.66, 0.64, 0.90), ENAMEL)
        make_cyl(f"Mud_{('Washer', 'Dryer')[k]}_Door", (x, yi1 - 0.665, 0.48), 0.20, 0.02, (0.70, 0.74, 0.76, 1.0), axis='Y', segments=14)
    make_box("Mud_Laundry_Basket", (3.55, yi1 - 0.40, 0.20), (0.50, 0.36, 0.40), (0.80, 0.72, 0.56, 1.0))
    make_box("Mud_Door_Mat", (X1 - 0.10 - 0.45, 8.6, 0.006), (0.60, 0.90, 0.012), (0.36, 0.30, 0.24, 1.0))


def build_living():
    """The living room: the TV on Wall_W, the sofa facing it, Nick's blanket."""
    # the TV stand and a 2000s 32-inch CRT on it, its screen toward the room (+x)
    make_box("TV_Stand", (X0 + 0.34, 2.80, 0.27), (0.48, 1.50, 0.54), OAK_DARK)
    for k, y in enumerate((2.38, 3.22)):
        make_box(f"TV_Stand_Door_{k}", (X0 + 0.585, y, 0.27), (0.012, 0.62, 0.44), OAK)
    make_box("TV_Body", (X0 + 0.40, 2.80, 0.86), (0.56, 0.80, 0.64), (0.14, 0.14, 0.15, 1.0))
    make_box("TV_Bezel", (X0 + 0.685, 2.80, 0.88), (0.02, 0.78, 0.58), (0.10, 0.10, 0.11, 1.0))
    make_box("TV_Screen", (X0 + 0.697, 2.80, 0.90), (0.006, 0.64, 0.48), (0.30, 0.42, 0.58, 1.0))
    make_box("VCR", (X0 + 0.36, 2.18, 0.58), (0.30, 0.24, 0.08), (0.12, 0.12, 0.13, 1.0))       # on the stand beside the set
    for k in range(6):
        make_box(f"Tapes_{k}", (X0 + 0.34, 3.30 + k * 0.03, 0.59), (0.19, 0.025, 0.10), (0.16 + k * 0.05, 0.12, 0.12, 1.0))
    # the sofa, facing west to the TV (its back to the kitchen)
    sx, sy, sl = -3.30, 2.80, 2.20
    make_box("Sofa_Base", (sx, sy, 0.17), (0.92, sl, 0.34), SOFA)         # down to the carpet
    make_box("Sofa_Back", (sx + 0.37, sy, 0.62), (0.20, sl, 0.60), SOFA)
    for s in (-1, 1):
        make_box(f"Sofa_Arm_{s:+d}", (sx, sy + s * (sl / 2.0 - 0.10), 0.44), (0.90, 0.20, 0.42), SOFA)
    for k, cy in enumerate((sy - 0.62, sy, sy + 0.62)):
        make_box(f"Sofa_SeatCush_{k}", (sx - 0.06, cy, 0.41), (0.66, 0.60, 0.14), SOFA_CUSH)
        make_box(f"Sofa_BackCush_{k}", (sx + 0.20, cy, 0.66), (0.20, 0.58, 0.40), SOFA_CUSH)
    # Nick asleep here: a pillow at the south arm and a crocheted afghan half off
    make_chamfer_box("Sofa_Pillow", (sx - 0.08, sy - 0.80, 0.53), (0.42, 0.32, 0.12), (0.92, 0.90, 0.84, 1.0), chamfer=0.04)
    make_box("Sofa_Afghan", (sx - 0.12, sy + 0.10, 0.495), (0.70, 1.40, 0.03), (0.66, 0.30, 0.22, 1.0))
    make_box("Sofa_Afghan_Hang", (sx - 0.465, sy + 0.10, 0.295), (0.03, 1.20, 0.40), (0.66, 0.30, 0.22, 1.0))
    # the coffee table, a rug, the recliner, an end table with the lamp
    make_box("Rug_Living", (-4.70, 2.80, 0.006), (2.40, 2.00, 0.012), (0.48, 0.36, 0.30, 1.0))
    make_table("CoffeeTable", -4.70, 2.80, w=0.60, d=1.10, h=0.42, wood=OAK)
    make_box("CoffeeTable_Remote", (-4.62, 2.60, 0.435), (0.05, 0.18, 0.02), BLACK)
    make_cyl("CoffeeTable_Mug", (-4.80, 3.05, 0.47), 0.04, 0.09, (0.82, 0.78, 0.70, 1.0), segments=10)
    rx, ry = -5.00, 0.95                       # the recliner by the front window, turned to the room (draft 4: the stair took its corner)
    make_box("Recliner_Base", (rx, ry, 0.17), (0.80, 0.80, 0.34), (0.36, 0.30, 0.26, 1.0))
    make_box("Recliner_Back", (rx, ry - 0.33, 0.70), (0.80, 0.22, 0.70), (0.36, 0.30, 0.26, 1.0))
    for s in (-1, 1):
        make_box(f"Recliner_Arm_{s:+d}", (rx + s * 0.36, ry, 0.48), (0.16, 0.80, 0.30), (0.36, 0.30, 0.26, 1.0))
    make_box("Recliner_Cush", (rx, ry + 0.05, 0.42), (0.52, 0.62, 0.10), (0.40, 0.34, 0.30, 1.0))
    make_box("EndTable", (-3.30, 4.13, 0.29), (0.46, 0.46, 0.58), OAK)
    make_lamp("Lamp_Living", -3.30, 4.13, base_z=0.58, h=0.62)
    # the bookcase in the nook under the stair's landing, on the W wall, family photos on top
    bx, byc = X0 + T / 2.0, (STAIR_Y0 + STAIR_Y1) / 2.0
    make_box("Bookcase_Back", (bx + 0.015, byc, 0.95), (0.02, 1.00, 1.90), OAK_DARK)
    for s in (-1, 1):
        make_box(f"Bookcase_Side_{s:+d}", (bx + 0.16, byc + s * 0.49, 0.95), (0.28, 0.02, 1.90), OAK)
    for b in range(5):
        z = 0.05 + b * 0.45
        make_box(f"Bookcase_Board_{b}", (bx + 0.16, byc, z), (0.28, 0.96, 0.02), OAK)
        if b < 4:
            for i in range(10 - b):
                h = 0.20 + ((i * 5 + b) % 4) * 0.03
                make_box(f"Bookcase_Book_{b}_{i}", (bx + 0.14, byc - 0.42 + i * 0.085, z + 0.01 + h / 2.0),
                         (0.20, 0.06, h), ((0.30 + 0.07 * (i % 4)), 0.22 + 0.05 * (b % 3), 0.18, 1.0))
    for k in range(3):
        make_box(f"Bookcase_Frame_{k}", (bx + 0.18, byc - 0.30 + k * 0.30, 1.97), (0.02, 0.18, 0.22), (0.20, 0.16, 0.12, 1.0))
    make_box("Bookcase_Top", (bx + 0.16, byc, 1.905), (0.30, 1.00, 0.02), OAK)
    # the ceiling fan over the sofa
    make_cyl("Fan_Rod", (-3.90, 2.80, (CEIL - 0.30 + CEIL2) / 2.0), 0.015, CEIL2 - CEIL + 0.30, (0.60, 0.50, 0.30, 1.0), segments=6)   # the downrod from the two-storey ceiling
    make_cyl("Fan_Hub", (-3.90, 2.80, CEIL - 0.34), 0.11, 0.12, (0.60, 0.50, 0.30, 1.0), segments=12)
    import math
    from _props.geometry import make_rot_box, make_heightfield, make_gable
    for k in range(5):
        a = k * 2 * math.pi / 5
        make_rot_box(f"Fan_Blade_{k}", (-3.90 + math.cos(a) * 0.42, 2.80 + math.sin(a) * 0.42, CEIL - 0.36),
                     (0.62, 0.14, 0.012), OAK_DARK, yaw=a)
    make_lathe("Fan_Globe", (-3.90, 2.80, CEIL - 0.52), [(0.0, 0.0), (0.09, 0.03), (0.10, 0.08), (0.0, 0.12)],
               (0.96, 0.92, 0.80, 1.0), segments=10)


def build_kitchen():
    """The kitchen along the hall wall; the dining table under the E window."""
    yb = HALL_S - T / 2.0          # the kitchen run's back: the hall wall's south face
    K.base_run("Kit_Base", 1.30, 5.20, yb, gaps=[(2.95, 3.71), (4.35, 4.95)])
    K.range_("Kit_Range", 3.33, yb, 0.98)
    K.dishwasher("Kit_DW", 4.65, yb - 0.62, 0.98)
    make_box("Kit_DW_Toe", (4.65, yb - 0.60, 0.05), (0.58, 0.06, 0.10), (0.20, 0.20, 0.21, 1.0))   # the kick under the panel
    K.sink("Kit_Sink", 2.10, yb, 0.98)
    K.upper_run("Kit_Upper", 1.30, 5.20, yb)
    K.backsplash("Kit_Splash", 1.30, 5.20, yb, 0.98, 1.46)
    K.fridge("Kit_Fridge", 5.75, yb)
    # what sits on the counter: a toaster, a coffee maker, the mail
    make_box("Kit_Toaster", (1.55, yb - 0.28, 1.08), (0.28, 0.18, 0.20), CHROME)
    make_box("Kit_Coffee", (4.95, yb - 0.24, 1.15), (0.22, 0.26, 0.34), BLACK)
    make_box("Kit_Mail", (2.60, yb - 0.40, 0.99), (0.26, 0.20, 0.02), (0.92, 0.90, 0.84, 1.0))
    # the dining table: father and son across it, the magazine between them
    tx, ty = 4.10, 2.20
    make_table("Dining", tx, ty, w=1.50, d=0.90, h=0.75, wood=OAK)
    make_chair("Chair_S", tx, ty - 0.70, yaw=0.0, wood=OAK)            # faces north, to the table
    make_chair("Chair_N", tx, ty + 0.70, yaw=3.14159, wood=OAK)        # faces south
    make_chair("Chair_W", tx - 1.02, ty, yaw=-1.5708, wood=OAK)        # faces east
    make_box("Magazine", (tx + 0.05, ty - 0.02, 0.757), (0.21, 0.28, 0.006), (0.86, 0.30, 0.24, 1.0))
    make_box("Magazine_Cover", (tx + 0.05, ty - 0.02, 0.761), (0.17, 0.12, 0.002), (0.94, 0.86, 0.60, 1.0))
    make_cyl("Dining_Glass", (tx - 0.40, ty - 0.25, 0.81), 0.035, 0.11, (0.70, 0.78, 0.80, 0.5), segments=10)
    make_pendant("Pendant_Dining", tx, ty, CEIL - 0.85, CEIL, shade_col=(0.56, 0.44, 0.30, 1.0))
    # a ceiling fixture over the kitchen
    make_cyl("Kit_Ceiling_Light", (3.40, 3.80, CEIL - 0.05), 0.24, 0.08, (0.96, 0.94, 0.86, 1.0), segments=14)


def _shower(x0, x1, y0, y1):
    """A shower stall in the NW corner (draft 2: upstairs "a small
    restroom/shower" — draft 1 had a built-in tub): the tray, the tiled walls,
    a glass screen on its open sides, the head and the valve."""
    cx, cy, w, d = (x0 + x1) / 2.0, (y0 + y1) / 2.0, x1 - x0, y1 - y0
    make_box("Shower_Tray", (cx, cy, 0.04), (w, d, 0.08), ENAMEL)
    make_box("Shower_Drain", (cx, cy, 0.081), (0.10, 0.10, 0.002), CHROME)
    make_box("Shower_Tile_N", (cx, y1 - 0.004, 1.15), (w, 0.008, 2.10), (0.90, 0.92, 0.90, 1.0))
    make_box("Shower_Tile_W", (x0 + 0.004, cy, 1.15), (0.008, d, 2.10), (0.90, 0.92, 0.90, 1.0))
    glass = (0.80, 0.88, 0.90, 0.30)
    make_box("Shower_Screen_S", (cx, y0 + 0.01, 1.08), (w, 0.012, 1.95), glass)
    make_box("Shower_Screen_E", (x1 - 0.01, cy + 0.20, 1.08), (0.012, d - 0.40, 1.95), glass)
    make_box("Shower_Frame_S", (cx, y0 + 0.01, 2.06), (w, 0.03, 0.03), CHROME)
    make_box("Shower_Frame_Post", (x1 - 0.01, y0 + 0.01, 1.03), (0.03, 0.03, 2.06), CHROME)
    make_cyl("Shower_Arm", (cx, y1 - 0.08, 1.95), 0.012, 0.16, CHROME, axis='Y', segments=6)
    make_cyl("Shower_Head", (cx, y1 - 0.18, 1.92), 0.05, 0.05, CHROME, axis='Y', segments=10)
    make_cyl("Shower_Valve", (cx, y1 - 0.02, 1.10), 0.05, 0.04, CHROME, axis='Y', segments=10)
    make_box("Shower_Mat", (cx + 0.20, y0 - 0.32, 0.006), (0.60, 0.40, 0.012), (0.46, 0.58, 0.62, 1.0))


def build_bath():
    """The shower in the NW corner under the frosted window, the toilet on the W wall, the
    vanity and its light bar on the E wall."""
    xi0, xi1 = UB_X0 + T / 2.0, UB_X1 - T / 2.0     # draft 4: at the stair's head
    yn = Y1 - T / 2.0
    _shower(xi0, xi0 + 0.95, yn - 0.95, yn)
    # the tile wainscot round the other walls
    for nm, x, a in (("Wainscot_W", xi0 + 0.004, 'Y'), ("Wainscot_E", xi1 - 0.004, 'Y')):
        make_box(nm, (x, (HALL_N + yn) / 2.0 - 0.40, 0.60), (0.008, yn - HALL_N - 0.90, 1.20), (0.90, 0.92, 0.90, 1.0))
    # toilet: tank against the W wall, facing east
    ty = 8.30
    make_box("Toilet_Tank", (xi0 + 0.11, ty, 0.62), (0.20, 0.44, 0.38), ENAMEL)
    make_box("Toilet_Tank_Lid", (xi0 + 0.115, ty, 0.825), (0.22, 0.46, 0.03), ENAMEL)
    make_box("Toilet_Flush", (xi0 + 0.22, ty + 0.15, 0.74), (0.01, 0.06, 0.02), CHROME)
    make_lathe("Toilet_Bowl", (xi0 + 0.48, ty, 0.0), [(0.13, 0.0), (0.10, 0.08), (0.12, 0.25), (0.19, 0.40), (0.0, 0.40)], ENAMEL, segments=12)
    make_box("Toilet_Seat", (xi0 + 0.48, ty, 0.415), (0.42, 0.38, 0.03), (0.90, 0.89, 0.86, 1.0))
    make_box("Toilet_Paper", (xi0 + 0.03, ty - 0.42, 0.68), (0.06, 0.12, 0.12), (0.96, 0.96, 0.94, 1.0))
    # vanity on the E wall: cabinet, top, basin, faucet; the mirror and the light bar over it
    vy = 8.35
    make_box("Vanity_Cab", (xi1 - 0.28, vy, 0.40), (0.55, 1.00, 0.80), OAK)
    for k, dy in enumerate((-0.25, 0.25)):
        make_box(f"Vanity_Door_{k}", (xi1 - 0.556, vy + dy, 0.40), (0.012, 0.46, 0.66), (0.66, 0.50, 0.32, 1.0))
    make_box("Vanity_Top", (xi1 - 0.29, vy, 0.82), (0.58, 1.04, 0.04), (0.92, 0.90, 0.86, 1.0))
    make_box("Vanity_Basin", (xi1 - 0.30, vy, 0.835), (0.36, 0.44, 0.012), (0.82, 0.82, 0.80, 1.0))
    make_cyl("Vanity_Faucet", (xi1 - 0.08, vy, 0.90), 0.02, 0.14, CHROME, segments=8)
    make_box("Vanity_Mirror", (xi1 - 0.008, vy, 1.45), (0.012, 0.96, 0.82), (0.78, 0.84, 0.86, 1.0))
    make_box("Vanity_LightBar", (xi1 - 0.05, vy, 1.98), (0.08, 0.80, 0.08), CHROME)
    for k in range(4):
        make_lathe(f"Vanity_Bulb_{k}", (xi1 - 0.11, vy - 0.30 + k * 0.20, 1.93), [(0.0, 0.0), (0.04, 0.02), (0.045, 0.06), (0.0, 0.10)],
                   (0.98, 0.96, 0.86, 1.0), segments=8)
    make_box("Towel_Bar", (xi1 - 0.015, 9.30, 1.15), (0.03, 0.60, 0.02), CHROME)
    make_box("Towel", (xi1 - 0.035, 9.30, 0.92), (0.03, 0.50, 0.46), (0.42, 0.56, 0.62, 1.0))
    make_box("Bath_Mat", (0.10 + UB_DX, 9.20, 0.006), (0.50, 0.80, 0.012), (0.46, 0.58, 0.62, 1.0))
    make_cyl("Bath_Ceiling_Fan", (0.20 + UB_DX, 8.00, CEIL - 0.03), 0.16, 0.05, (0.94, 0.94, 0.92, 1.0), segments=10)


def build_bedroom():
    """Andy's room: the bed's head on Wall_E, the lamp, the desk under the N
    window, the bookcase on the W wall, the closet on the S wall."""
    xi0, xi1 = BATH_E + T / 2.0, X1 - T / 2.0
    yi0, yi1 = HALL_N + T / 2.0, Y1 - T / 2.0
    make_bed("Bed", xi1 - 0.975 - 0.02, 8.30, head="+X", w=1.35, d=1.95, blanket_col=(0.30, 0.36, 0.46, 1.0))
    make_box("Nightstand", (xi1 - 0.24, 9.45, 0.30), (0.44, 0.44, 0.60), OAK)
    make_lamp("Lamp_Bed", xi1 - 0.24, 9.45, base_z=0.60, h=0.52)
    make_box("Nightstand_Book", (xi1 - 0.20, 9.30, 0.615), (0.16, 0.22, 0.03), (0.42, 0.20, 0.16, 1.0))
    make_box("Nightstand_Clock", (xi1 - 0.30, 9.60, 0.645), (0.10, 0.18, 0.09), BLACK)
    make_box("Nightstand_Clock_Face", (xi1 - 0.356, 9.60, 0.65), (0.004, 0.13, 0.04), (0.86, 0.20, 0.14, 1.0))
    # the desk under the window and its lamp
    dx = 4.00
    make_box("Desk_Top", (dx, yi1 - 0.305, 0.74), (1.30, 0.62, 0.03), OAK_DARK)   # back edge against the wall
    for s in (-1, 1):
        make_box(f"Desk_Side_{s:+d}", (dx + s * 0.63, yi1 - 0.32, 0.365), (0.03, 0.60, 0.73), OAK_DARK)
    make_chair("Desk_Chair", dx, yi1 - 0.95, yaw=0.0, wood=OAK_DARK)
    make_lamp("Lamp_Desk", dx + 0.48, yi1 - 0.22, base_z=0.755, h=0.42, shade_col=(0.30, 0.42, 0.34, 1.0))
    make_box("Desk_Papers", (dx - 0.20, yi1 - 0.36, 0.76), (0.30, 0.22, 0.01), (0.96, 0.95, 0.92, 1.0))
    # the bookcase on the W wall, books packed and a few lying flat
    bx = xi0 + 0.15
    for s in range(2):
        by = 8.32 + s * 0.92          # clear of the door's swing (doorway_audit: 0.9 m each side of the leaf)
        make_box(f"Shelf_{s}_Back", (xi0 + 0.01, by, 0.95), (0.02, 0.88, 1.90), OAK_DARK)
        for side in (-1, 1):
            make_box(f"Shelf_{s}_Side_{side:+d}", (bx, by + side * 0.43, 0.95), (0.28, 0.02, 1.90), OAK)
        for b in range(5):
            z = 0.05 + b * 0.45
            make_box(f"Shelf_{s}_Board_{b}", (bx, by, z), (0.28, 0.84, 0.02), OAK)
            if b < 4:
                n = 8 - (b + s) % 3
                for i in range(n):
                    h = 0.19 + ((i * 3 + b + s) % 4) * 0.03
                    make_box(f"Shelf_{s}_Book_{b}_{i}", (bx + 0.02, by - 0.36 + i * 0.09, z + 0.01 + h / 2.0),
                             (0.20, 0.065, h), (0.26 + 0.08 * ((i + s) % 4), 0.20 + 0.06 * (b % 3), 0.20 + 0.05 * (i % 2), 1.0))
        make_box(f"Shelf_{s}_Top", (bx, by, 1.905), (0.28, 0.88, 0.02), OAK)
    make_box("Shelf_Flat_Books", (bx + 0.02, 8.77, 1.94), (0.22, 0.30, 0.06), (0.52, 0.30, 0.20, 1.0))
    # the closet on the S wall: two bifold pairs
    cx = 5.20
    for k in range(4):
        make_box(f"Closet_Leaf_{k}", (cx - 0.66 + k * 0.44, yi0 + 0.025, 1.02), (0.42, 0.03, 2.02), DOOR_WHITE)
    make_box("Closet_Head", (cx, yi0 + 0.03, 2.08), (1.82, 0.04, 0.06), DOOR_WHITE)
    # a dresser in the NW corner (clear of the door's swing), posters over the bed
    make_box("Dresser", (2.45, yi1 - 0.25, 0.45), (0.90, 0.48, 0.90), OAK)
    for k in range(3):
        make_box(f"Dresser_Drawer_{k}", (2.45, yi1 - 0.496, 0.18 + k * 0.27), (0.84, 0.012, 0.22), (0.68, 0.52, 0.32, 1.0))
    make_box("Dresser_Box", (2.25, yi1 - 0.25, 0.95), (0.30, 0.22, 0.10), (0.24, 0.20, 0.18, 1.0))
    make_faded_poster("Poster_Bed", (xi1 - 0.006, 8.30, 1.65), into_room=-1)
    make_box("Rug_Bedroom", (3.90, 8.40, 0.006), (1.60, 1.10, 0.012), (0.30, 0.34, 0.40, 1.0))
    make_cyl("Bedroom_Ceiling_Light", (4.05, 8.60, CEIL - 0.05), 0.20, 0.08, (0.96, 0.94, 0.86, 1.0), segments=12)


def build_bed2():
    """The second bedroom behind its shut door: enough that the window
    from the yard is not a void (its interior is draft 2)."""
    make_bed("Bed2", -3.90 + B2_DX, 9.20, head="+Y", w=1.50, d=2.00, blanket_col=(0.56, 0.48, 0.40, 1.0))
    make_box("Bed2_Dresser", (-6.10 + B2_DX, 8.00, 0.45), (0.48, 1.10, 0.90), OAK)
    # draft 5: a nightstand and lamp, a rug, a desk and chair under the
    # window's E side, curtains
    b2c = (UB_X1 + B2_X1) / 2.0
    make_box("Bed2_Nightstand", (-3.90 + B2_DX + 1.05, Y1 - T / 2.0 - 0.25, 0.30), (0.42, 0.42, 0.60), OAK)
    make_lamp("Lamp_Bed2", -3.90 + B2_DX + 1.05, Y1 - T / 2.0 - 0.25, base_z=0.60, h=0.50)
    make_box("Bed2_Rug", (-3.90 + B2_DX, 7.90, 0.006), (1.80, 1.20, 0.012), (0.44, 0.50, 0.56, 1.0))
    make_box("Bed2_Desk", (B2_X1 - T / 2.0 - 0.32, 8.20, 0.74), (0.60, 1.10, 0.04), OAK_DARK)
    for s in (-1, 1):
        make_box(f"Bed2_Desk_Side_{s:+d}", (B2_X1 - T / 2.0 - 0.32, 8.20 + s * 0.53, 0.36), (0.58, 0.04, 0.72), OAK_DARK)
    make_chair("Bed2_Desk_Chair", B2_X1 - T / 2.0 - 0.95, 8.20, yaw=-math.pi / 2.0, wood=OAK_DARK)
    make_curtains("Bed2_Curtains", (b2c, Y1 - 0.10, 1.45), width=1.40, height=1.30, axis='X', room_dir=-1, color=(0.66, 0.60, 0.70, 1.0))


def build_hall_and_infra():
    make_box("Hall_Runner", (0.0, 6.10, 0.006), (9.00, 0.80, 0.012), (0.40, 0.30, 0.26, 1.0))
    make_cyl("Hall_Light", (0.0, 6.10, CEIL - 0.05), 0.16, 0.08, (0.96, 0.94, 0.86, 1.0), segments=12)
    make_smoke_detector("Smoke_Hall", (-1.8, 6.10, CEIL))
    make_thermostat("Thermostat", (-1.6, HALL_S), axis='X', face_sign=1)
    make_light_switch("Switch_Front", (-0.30, Y0), axis='X', face_sign=1)
    make_wall_outlet("Outlet_TV", (X0, 3.60), axis='Y', face_sign=1)
    make_wall_outlet("Outlet_Kitchen", (1.50, HALL_S), axis='X', face_sign=-1)
    wear = (CARPET[0] * 0.88, CARPET[1] * 0.88, CARPET[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Front_To_Hall", [(-1.0, 0.4), (-1.0, 5.6)], width=0.7, tint=wear)
    make_traffic_wear("Wear_Hall", [(-3.0, 6.1), (3.2, 6.1)], width=0.6, tint=wear)
    pw = PAL_WALL["wall"]
    make_wall_tint_band("Band_Living_W", (X0 + 0.105, 2.75, 0.0), length=5.0, axis='Y', band_z=CEIL2 - 0.16,
                        tint=(pw[0] * 0.92, pw[1] * 0.92, pw[2] * 0.90, 1.0))


# ── THE GROUNDS (draft 3, 2026-10-23) ────────────────────────────────────
# The user: "There is a large covered carport that leads to the mudroom and
# with two connected outdoor rooms for storage, and a front porch that
# overlooks a large pasture field leading to the river." The house sits up
# on its foundation (GZ below the floor); the front porch and its steps
# face S over the yard and the fence to the pasture, the pasture runs down
# to the river, the far bank's trees beyond. The carport is on the E side
# at the mudroom's back door, the two storage rooms at its N end under the
# same roof, the gravel drive out east. Draft 1-2 had make_view's suburban
# street out front and lawns behind.
GZ = -0.45                         # the ground, below the house floor
CP_X0, CP_X1, CP_Y0, CP_Y1 = X1 + 0.10, X1 + 6.80, 3.40, 11.00   # the carport's slab
ST_Y1 = 14.40                      # the storage rooms run N of the carport to here
PORCH_X0, PORCH_X1, PORCH_D = X0 - 0.10, 3.60, 2.80
RIVER_Y0, RIVER_Y1 = -94.0, -70.0
RIVER_DROP = 5.0                   # the pasture falls this far from the yard fence to the river
GRASS = (0.36, 0.46, 0.26, 1.0); PASTURE = (0.56, 0.58, 0.34, 1.0); DIRT = (0.44, 0.36, 0.26, 1.0)
GRAVEL = (0.62, 0.58, 0.52, 1.0); CONCRETE = (0.66, 0.64, 0.60, 1.0); WATER = (0.48, 0.60, 0.68, 1.0)
SIDING = (0.82, 0.78, 0.68, 1.0); ROOF = (0.36, 0.34, 0.32, 1.0); TRIM = (0.92, 0.90, 0.84, 1.0)
PORCH_WOOD = (0.56, 0.44, 0.32, 1.0)


def _fence_x(prefix, y, x0, x1, gap=None, h=1.2, every=3.0):
    """A pasture fence along X: cedar posts, three wires."""
    n = int(round((x1 - x0) / every))
    for k in range(n + 1):
        x = x0 + k * (x1 - x0) / n
        if gap and gap[0] < x < gap[1]:
            continue
        make_box(f"{prefix}_Stock_Post_{k}", (x, y, GZ + h / 2.0 - 0.10), (0.10, 0.10, h + 0.20), (0.46, 0.40, 0.32, 1.0))
    runs = [(x0, x1)] if not gap else [(x0, gap[0]), (gap[1], x1)]
    for r, (a, b) in enumerate(runs):
        for w, z in enumerate((0.45, 0.78, 1.10)):
            make_box(f"{prefix}_Stock_Wire_{r}_{w}", ((a + b) / 2.0, y, GZ + z), (b - a, 0.008, 0.008), (0.40, 0.40, 0.42, 1.0))


def build_grounds():
    # the ground in tiles that do not overlap (coplanar tiles shimmer): the
    # yard round the house, the pasture to the S, the river bank, the water,
    # the far bank
    for nm, (x0, x1, y0, y1, col, top) in {
            "Yard": (-140.0, 140.0, -9.0, 90.0, GRASS, GZ),
            "Bank_Near": (-140.0, 140.0, RIVER_Y1, RIVER_Y1 + 1.0, DIRT, GZ - RIVER_DROP - 0.10),
            "River": (-140.0, 140.0, RIVER_Y0, RIVER_Y1, WATER, GZ - RIVER_DROP - 0.25),
            "Bank_Far": (-140.0, 140.0, RIVER_Y0 - 1.0, RIVER_Y0, DIRT, GZ - RIVER_DROP - 0.10),
            "Far_Bank": (-140.0, 140.0, -170.0, RIVER_Y0 - 1.0, GRASS, GZ - RIVER_DROP)}.items():
        make_box(f"Ground_{nm}", ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top - 0.30), (x1 - x0, y1 - y0, 0.60), col)
    # the pasture falls away from the fence to the river (a flat field hid the
    # water from the porch): a heightfield, RIVER_DROP over its 60 m, with a
    # long low roll in it
    import math
    cell, cols, rows = 4.0, 71, 16
    y_o = RIVER_Y1 + 1.0
    hts = []
    for r in range(rows):
        y = y_o + r * cell
        t = max(0.0, min(1.0, (-9.0 - y) / (-9.0 - y_o)))
        row = []
        for c in range(cols):
            x = -140.0 + c * cell
            row.append(-RIVER_DROP * t ** 0.75 + 0.25 * t * (1.0 - t) * 4.0 * math.sin(x / 17.0) * math.sin(y / 11.0))   # a bowl, so the porch sees down to the water
        hts.append(row)
    make_heightfield("Ground_Pasture", (-140.0, y_o, GZ), cell, hts, PASTURE, skirt=0.6)
    # the foundation under the walls, the house up on it
    for nm, (cx, cy, sx, sy) in {"S": (0.0, Y0, X1 - X0 + 0.44, 0.24), "N": (0.0, Y1, X1 - X0 + 0.44, 0.24),
                                 "W": (X0, (Y0 + Y1) / 2.0, 0.24, Y1 - Y0), "E": (X1, (Y0 + Y1) / 2.0, 0.24, Y1 - Y0)}.items():
        make_box(f"Foundation_{nm}", (cx, cy, GZ / 2.0 - 0.02), (sx, sy, -GZ + 0.04), (0.60, 0.56, 0.50, 1.0))

    # THE FRONT PORCH: the deck at the floor's height, its skirt to the
    # ground, the shed roof on posts, the rail, the steps down to the path
    px, pw = (PORCH_X0 + PORCH_X1) / 2.0, PORCH_X1 - PORCH_X0
    py0 = Y0 - T / 2.0 - PORCH_D
    make_box("Porch_Deck", (px, py0 + PORCH_D / 2.0, -0.04), (pw, PORCH_D, 0.08), PORCH_WOOD)
    for k in range(int(pw / 0.14)):
        make_box(f"Porch_Stock_Seam_{k}", (PORCH_X0 + 0.14 * (k + 1), py0 + PORCH_D / 2.0, 0.0006), (0.006, PORCH_D, 0.001), (0.44, 0.34, 0.24, 1.0))
    make_box("Porch_Skirt_S", (px, py0 + 0.03, (GZ - 0.08) / 2.0), (pw, 0.06, -GZ - 0.08 + 0.02), TRIM)
    for sd, x in (("W", PORCH_X0 + 0.03), ("E", PORCH_X1 - 0.03)):
        make_box(f"Porch_Skirt_{sd}", (x, py0 + PORCH_D / 2.0, (GZ - 0.08) / 2.0), (0.06, PORCH_D, -GZ - 0.08 + 0.02), TRIM)
    rz0, rz1 = 2.86, 2.50                  # the roof: from the wall down to the front beam
    import math
    pitch = math.atan2(rz0 - rz1, PORCH_D + 0.40)
    make_rot_box("Porch_Roof", (px, py0 + PORCH_D / 2.0 - 0.20, (rz0 + rz1) / 2.0 + 0.06), (pw + 0.40, PORCH_D + 0.60, 0.10), ROOF,
                 roll=pitch)              # higher at the wall (roll: about X, z rises with y)
    make_box("Porch_Beam", (px, py0 + 0.12, rz1 - 0.04), (pw, 0.16, 0.20), TRIM)
    make_box("Porch_Ledger", (px, Y0 - T / 2.0 - 0.08, rz0 - 0.06), (pw, 0.10, 0.16), TRIM)
    step_x = -1.0
    posts = [PORCH_X0 + 0.15, -4.4, step_x - 0.70, step_x + 0.70, PORCH_X1 - 0.15]
    for k, x in enumerate(posts):
        make_box(f"Porch_Post_{k}", (x, py0 + 0.12, (rz1 - 0.14) / 2.0), (0.14, 0.14, rz1 - 0.14), TRIM)
    # the rail between the posts, open at the steps
    for k in range(len(posts) - 1):
        a, b = posts[k] + 0.07, posts[k + 1] - 0.07
        if a < step_x < b:
            continue
        for z, nm in ((0.92, "Top"), (0.12, "Bottom")):
            make_box(f"Porch_Stock_Rail_{k}_{nm}", ((a + b) / 2.0, py0 + 0.12, z), (b - a, 0.06, 0.05), TRIM)
        n = int((b - a) / 0.16)
        for m in range(1, n):
            make_box(f"Porch_Stock_Bal_{k}_{m}", (a + m * (b - a) / n, py0 + 0.12, 0.52), (0.035, 0.035, 0.76), TRIM)
    for k in range(3):                     # three steps down to the path
        top = -(k + 1) * (-GZ / 3.0) + 0.0
        make_box(f"Porch_Step_{k}", (step_x, py0 - 0.15 - k * 0.30, (top + GZ) / 2.0), (1.30, 0.30, top - GZ + 0.001), PORCH_WOOD)
    # on the porch: two rockers and a little table looking out at the pasture, the porch light
    for k, x in enumerate((-5.4, -3.4)):
        make_chair(f"Porch_Rocker_{k}", x, py0 + 0.95, yaw=math.pi + 0.15 * (1 - 2 * k), wood=(0.40, 0.30, 0.22, 1.0))
        for s in (-1, 1):
            make_rot_box(f"Porch_Rocker_{k}_Runner_{s:+d}", (x + s * 0.18, py0 + 0.95, 0.015), (0.04, 0.62, 0.03), (0.40, 0.30, 0.22, 1.0),
                         yaw=0.15 * (1 - 2 * k))
    make_table("Porch_Table", -4.4, py0 + 1.05, w=0.50, d=0.50, h=0.50, wood=(0.40, 0.30, 0.22, 1.0))
    make_cyl("Porch_Tea_Glass", (-4.35, py0 + 1.00, 0.555), 0.035, 0.11, (0.70, 0.56, 0.32, 0.6), segments=10)
    make_box("Porch_Light", (-1.65, Y0 - T / 2.0 - 0.09, 2.00), (0.14, 0.12, 0.24), (0.98, 0.90, 0.66, 1.0))
    # the path from the steps to the pasture gate; the yard's fence along the pasture
    make_box("Path_Front", (step_x, (py0 - 1.0 - 9.0) / 2.0, GZ + 0.012), (1.10, (py0 - 1.0) - (-9.0), 0.024), GRAVEL)
    _fence_x("Pasture_Fence", -9.0, -60.0, 60.0, gap=(step_x - 1.8, step_x + 1.8))
    for s in (-1, 1):
        make_box(f"Pasture_Gate_Post_{s:+d}", (step_x + s * 1.8, -9.0, GZ + 0.70), (0.16, 0.16, 1.60), (0.46, 0.40, 0.32, 1.0))
    gx0, ga = step_x - 1.72, 0.5                 # the gate, swung half open: rails and stiles
    gc, gs = math.cos(ga), math.sin(ga)
    for k, z in enumerate((0.25, 0.65, 1.05)):
        make_rot_box(f"Pasture_Gate_Rail_{k}", (gx0 + 0.85 * gc, -9.0 - 0.85 * gs, GZ + z), (1.70, 0.05, 0.08), (0.66, 0.64, 0.60, 1.0), yaw=-ga)
    for k, u in enumerate((0.04, 1.66)):
        make_rot_box(f"Pasture_Gate_Stile_{k}", (gx0 + u * gc, -9.0 - u * gs, GZ + 0.65), (0.06, 0.05, 0.90), (0.66, 0.64, 0.60, 1.0), yaw=-ga)

    # THE CARPORT: a slab at the mudroom's back door, a low roof from the
    # house wall to a row of posts, the two storage rooms at its N end
    make_box("Carport_Slab", ((CP_X0 + CP_X1) / 2.0, (CP_Y0 + ST_Y1) / 2.0, GZ - 0.03 + 0.04), (CP_X1 - CP_X0, ST_Y1 - CP_Y0, 0.10), CONCRETE)
    croof = 2.70
    make_box("Carport_Roof", ((CP_X0 + 0.10 + CP_X1 + 0.40) / 2.0, (CP_Y0 + ST_Y1) / 2.0, croof + 0.06), (CP_X1 + 0.30 - CP_X0, ST_Y1 - CP_Y0 + 0.6, 0.12), ROOF)
    make_box("Carport_Fascia_E", (CP_X1 + 0.25, (CP_Y0 + ST_Y1) / 2.0, croof - 0.05), (0.06, ST_Y1 - CP_Y0 + 0.6, 0.24), TRIM)
    make_box("Carport_Fascia_S", ((CP_X0 + 0.04 + CP_X1 + 0.40) / 2.0, CP_Y0 - 0.30, croof - 0.05), (CP_X1 + 0.36 - CP_X0, 0.06, 0.24), TRIM)
    make_box("Carport_Ledger", (CP_X0 + 0.08, (CP_Y0 + ST_Y1) / 2.0, croof - 0.10), (0.10, ST_Y1 - CP_Y0, 0.20), TRIM)
    make_box("Carport_Beam", (CP_X1 - 0.10, (CP_Y0 + ST_Y1) / 2.0, croof - 0.12), (0.18, ST_Y1 - CP_Y0, 0.24), TRIM)
    for k, y in enumerate((CP_Y0 + 0.10, CP_Y0 + 2.6, CP_Y0 + 5.1, CP_Y1)):
        make_box(f"Carport_Post_{k}", (CP_X1 - 0.10, y, (GZ + 0.07 + croof - 0.24) / 2.0), (0.16, 0.16, croof - 0.24 - GZ - 0.07), TRIM)
    # the stoop and two steps down from the back door
    make_box("Back_Stoop", (CP_X0 + 0.45, 8.6, (GZ + 0.07) / 2.0 - 0.0), (0.90, 1.30, -GZ - 0.07), CONCRETE)
    make_box("Back_Step", (CP_X0 + 1.05, 8.6, (GZ + 0.07 + GZ / 2.0) / 2.0), (0.30, 1.10, GZ / 2.0 - GZ - 0.07), CONCRETE)
    # the two storage rooms, side by side under the roof, their doors to the carport
    smid = (CP_X0 + CP_X1) / 2.0
    for k, (x0, x1) in enumerate(((CP_X0, smid), (smid, CP_X1 - 0.20))):
        cx = (x0 + x1) / 2.0
        z0 = GZ + 0.07
        h = croof - 0.24 - z0
        make_box(f"Storage_{k}_Wall_N", (cx, ST_Y1 - 0.06, z0 + h / 2.0), (x1 - x0, 0.12, h), SIDING)
        for sd, x in (("W", x0 + 0.06), ("E", x1 - 0.06)):
            if k == 0 and sd == "W":
                continue                     # the first leans on the house's wall
            make_box(f"Storage_{k}_Wall_{sd}", (x, (CP_Y1 + ST_Y1) / 2.0, z0 + h / 2.0), (0.12, ST_Y1 - CP_Y1, h), SIDING)
        dw = 0.90
        for sd, (a, b) in (("L", (x0, cx - dw / 2.0)), ("R", (cx + dw / 2.0, x1))):
            make_box(f"Storage_{k}_Front_{sd}", ((a + b) / 2.0, CP_Y1 + 0.06, z0 + h / 2.0), (b - a, 0.12, h), SIDING)
        make_box(f"Storage_{k}_Front_Head", (cx, CP_Y1 + 0.06, z0 + 2.05 + (h - 2.05) / 2.0), (dw, 0.12, h - 2.05), SIDING)
        make_box(f"Storage_{k}_Door", (cx, CP_Y1 + 0.03, z0 + 1.02), (dw - 0.04, 0.05, 2.03), ((0.40, 0.46, 0.44, 1.0), (0.56, 0.36, 0.26, 1.0))[k])
        make_cyl(f"Storage_{k}_Knob", (cx + dw / 2.0 - 0.12, CP_Y1 - 0.01, z0 + 0.98), 0.028, 0.05, CHROME, axis='Y', segments=8)
    # what lives under it: the pickup, a deep freezer by the back door, a bicycle, cans
    make_car("Carport_Truck", (CP_X0 + CP_X1) / 2.0 + 0.6, 6.4, 5.2, (0.56, 0.20, 0.16, 1.0), pickup=True, along="Y", z0=GZ + 0.07)
    make_box("Carport_Freezer", (CP_X0 + 0.40, 10.30, GZ + 0.07 + 0.45), (0.70, 1.10, 0.90), ENAMEL)
    for k in range(3):
        make_cyl(f"Carport_Can_{k}", (CP_X1 - 0.60 - k * 0.32, CP_Y1 - 0.40, GZ + 0.07 + 0.18), 0.12, 0.36,
                 ((0.70, 0.18, 0.14, 1.0), (0.30, 0.42, 0.30, 1.0), (0.24, 0.24, 0.26, 1.0))[k], segments=10)
    # the gravel drive out east from the carport
    make_box("Drive_Gravel", ((CP_X1 + 70.0) / 2.0, (CP_Y0 + CP_Y1) / 2.0, GZ + 0.015), (70.0 - CP_X1, 4.6, 0.03), GRAVEL)
    # the back yard: a clothesline, the old oak
    for s, x in enumerate((-4.5, 1.5)):
        make_box(f"Clothesline_Post_{s}", (x, Y1 + 6.0, GZ + 1.0), (0.08, 0.08, 2.0), (0.62, 0.62, 0.64, 1.0))
        make_box(f"Clothesline_Bar_{s}", (x, Y1 + 6.0, GZ + 1.95), (0.08, 1.00, 0.05), (0.62, 0.62, 0.64, 1.0))
    for w in (-0.4, 0.0, 0.4):
        make_box(f"Clothesline_Line_{w:+.1f}", (-1.5, Y1 + 6.0 + w, GZ + 1.96), (6.0, 0.006, 0.006), (0.86, 0.86, 0.84, 1.0))
    # trees: the oak out back, a pair over the drive, pecans along the pasture
    # fence, the woods on the river's far bank (lowered to the ground)
    with zoned([(-999.0, -999.0, 999.0, 999.0, 0.0, 0.0, GZ)]):
        make_broadleaf("Oak_Back", 6.0, Y1 + 11.0, 9.0, (0.30, 0.42, 0.22, 1.0), (0.36, 0.28, 0.20, 1.0))
        make_broadleaf("Tree_Drive_0", 22.0, 14.0, 8.0, (0.32, 0.44, 0.24, 1.0), (0.36, 0.28, 0.20, 1.0))
        make_broadleaf("Tree_Drive_1", 34.0, -1.0, 7.0, (0.30, 0.42, 0.22, 1.0), (0.36, 0.28, 0.20, 1.0))
        make_broadleaf("Tree_Yard_W", -12.0, 3.0, 8.5, (0.32, 0.44, 0.24, 1.0), (0.36, 0.28, 0.20, 1.0))
        for k, x in enumerate((-46.0, -27.0, 24.0, 41.0)):
            make_broadleaf(f"Pecan_{k}", x, -10.5, 10.0 + (k % 2) * 2.0, (0.34, 0.44, 0.24, 1.0), (0.38, 0.30, 0.22, 1.0))
        make_far_bands("Woods_N", (0.30, 0.40, 0.26, 1.0), [(70.0, 120.0, 12.0, 0.90)], sides="N", cx=0.0, cy=5.0)
        make_far_bands("Woods_EW", (0.30, 0.40, 0.26, 1.0), [(100.0, 76.0, 13.0, 0.88)], sides="EW", cx=0.0, cy=30.0)   # N of the pasture fence (the pasture falls away S of it)
    with zoned([(-999.0, -999.0, 999.0, 999.0, 0.0, 0.0, GZ - RIVER_DROP)]):      # the far bank, down by the river
        for k in range(12):
            x = -110.0 + k * 20.0 + (k % 3) * 4.0
            make_broadleaf(f"River_Tree_{k}", x, RIVER_Y0 - 4.0 - (k % 2) * 3.0, 12.0 + (k % 4) * 1.5,
                           (0.26, 0.38, 0.22, 1.0), (0.34, 0.28, 0.22, 1.0))
        make_far_bands("Woods", (0.30, 0.40, 0.26, 1.0), [(110.0, 160.0, 14.0, 0.92), (150.0, 200.0, 20.0, 0.80)], sides="S", cx=0.0, cy=0.0)
    # the house's roof: a gable over the two storeys, the ridge E-W, eaves out
    make_gable("House_Roof", (0.0, (Y0 + Y1) / 2.0, CEIL2 + 0.10 + 1.10), (X1 - X0 + 0.80, Y1 - Y0 + 0.90, 2.20), ROOF, ridge_axis='X')
    for nm, y in (("S", Y0 - 0.45), ("N", Y1 + 0.45)):
        make_box(f"House_Fascia_{nm}", (0.0, y, CEIL2 + 0.06), (X1 - X0 + 0.80, 0.05, 0.20), TRIM)


def main():
    clear_scene()
    build_shell()
    build_living()
    build_kitchen()
    build_ground_back_rooms()
    build_stair_and_upstairs()
    with zoned(UP_WING):               # the bedroom wing, up a storey
        build_upper_wing()
        build_bath()
        build_bedroom()
        build_bed2()
    build_hall_and_infra()
    build_grounds()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/link_house.glb"))
    print(f"\n[build_link_house] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
