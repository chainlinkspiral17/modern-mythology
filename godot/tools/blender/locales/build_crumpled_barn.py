"""The crumpled barn — vol2 ch1's history montage. A gray barn that
lost its back half years ago: the gable end still stands, the roof
lies where it fell.

Hero features: the standing weathered gable wall with its dark
doorway and hay-door, the collapsed roof planes lying low behind it
on a rubble bed, exposed frame posts still upright inside the
footprint, scattered siding boards, a remnant fence line, a rusted
water trough, tall weeds working through everything, and a flat
overcast sky.

Coordinate frame: Blender Z-up. y=0 is the field's south edge (the
camera side); +Y runs north to the gable face at y≈8. glTF export
remaps to Godot (x, z, -y).

Vantages wired in Background3D.CAMERA_PRESETS:
  crumpled_barn_ext — in the field looking N at the standing gable
  with the fallen roof behind.
  crumpled_barn_int — inside the standing half: the marionette
  cabinet (Jiggles the Juggler, head resting on his shoulder,
  glass fourth wall broken) facing the carved wooden sign of the
  mermaid — "Come Visit Today. A Twisted Beauty and a Beast. Only
  at The Cliffside Circus Attraction." The hero props of the whole
  Delores thread.

DRAFT 3 (2026-10-23, the sw162 sheet): the barn stood as a grey stepped
slab in an empty field and the interior was one grey wash. Now: "I
thought it part of the hill" — a hill rises behind the footprint and the
hedge sits on it; "Foliage consuming much of the exterior" — bramble
mounds climb the gable, bury the fallen planes and crowd the doorway;
"The sunlight poking through, bleached" — a shadowed sun through a
remnant of rafters and shingle strips over the surviving bay, striping
the cabinet and the sign; debris in the bay's corners ("remnants in
corners, hidden in shadow"); the interior camera closer to the pair.
DRAFT 4 (2026-10-30): build_bay_2026_10 — the bay as a room (side-wall
remnants, the gable's framing from inside, the boarded door, the cabinet's
marquee, curtains, buttons and levers, the sign half hanging with its relief
in front of the board). Draft 5 targets: the hay door's swung leaf, the
bramble as a vine kit with leaves (and coming in through the wall gaps), a
crow on the peak, the field's ruts to the gate gap, Jiggles' face and
juggling pins, the gable's outer board lap as real courses.
DRAFT 6 (2026-11-02, survey 5): the bramble as bramble — every mound a dark
core with its leaf clusters packed over the dome (_bramble), ivy up the
gable's boards from the two climbing mounds (_ivy), the hedge leafed the
same way (from the field they all read as grey boulders). All `_Stock_`,
joined. Draft 7 targets: the hay door's swung leaf; a crow on the peak; the
field's ruts to the gate gap; Jiggles' face and juggling pins; the gable's
outer board lap as real courses; the hill brought down to the collapse so
the barn sits INTO it ("I thought it part of the hill").
(Old draft 4 targets: the gable's board lap as real courses (make_lap_siding
in grey), the hay door's swung leaf, the cabinet's levers and buttons as
a row of brass, the bramble as a vine kit with leaves, a crow on the
peak, the field's ruts to the gate gap.)
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_rot_box, make_heightfield, make_prism, make_tube,
                             join_stock, export_glb)
import math
import random

COL_FIELD = (0.54, 0.50, 0.32, 1.0)      # dry pasture (2026-09-30: was 0.42 grey-olive — the barn, field and sky were one value)
COL_DIRT = (0.40, 0.34, 0.26, 1.0)
COL_BARN = (0.42, 0.40, 0.38, 1.0)       # weathered gray board
COL_BARN_DK = (0.32, 0.30, 0.29, 1.0)
COL_DOOR = (0.14, 0.13, 0.12, 1.0)
COL_ROOF = (0.36, 0.33, 0.30, 1.0)       # fallen shingle planes
COL_ROOF_DK = (0.28, 0.26, 0.24, 1.0)
COL_FRAME = (0.30, 0.25, 0.19, 1.0)      # old fir posts
COL_RUBBLE = (0.38, 0.35, 0.31, 1.0)
COL_WEED = (0.34, 0.38, 0.22, 1.0)
COL_WEED_DRY = (0.48, 0.44, 0.28, 1.0)
COL_FENCE = (0.34, 0.28, 0.20, 1.0)
COL_TROUGH = (0.36, 0.30, 0.26, 1.0)     # rust
COL_TREE = (0.20, 0.26, 0.18, 1.0)
COL_SKY = (0.62, 0.63, 0.64, 1.0)        # flat overcast


def build_field():
    make_box("Field", (0.0, 6.0, 0.0), (34.0, 18.0, 0.05), COL_FIELD)   # to y 15, the hill's foot (draft 7; was to y 21)
    make_box("Yard_Dirt", (0.0, 8.5, 0.01), (10.0, 6.0, 0.05), COL_DIRT)


def build_gable():
    """The standing end wall, face at y=8: wide base narrowing in
    three steps to the peak, doorway and hay door punched dark."""
    # (2026-10-30, draft 5: a GABLE — the pitched pentagon of a barn's end,
    # not three stepped slabs that read as a robot's head from the field)
    make_prism("Gable_Base", (-0.5, 8.4, 0.0), [(-3.2, 0.0), (3.2, 0.0), (3.2, 3.2), (0.0, 5.5), (-3.2, 3.2)], 0.35, COL_BARN, axis="Y")
    # battens up into the triangle, each stopping under the rake
    for i in range(13):
        x = -3.45 + i * 0.5
        u = abs(x + 0.5)
        top = 3.2 + (3.2 - u) * (2.3 / 3.2) - 0.06 if u < 3.2 else 3.14
        if -2.05 < x < -0.35 and True:
            make_box(f"Gable_Batten_Up_{i}", (x, 8.215, (2.6 + top) / 2.0), (0.06, 0.02, top - 2.6), COL_BARN_DK)
            continue                                    # over the doorway only
        make_box(f"Gable_Batten_{i}", (x, 8.215, top / 2.0), (0.06, 0.02, top - 0.02), COL_BARN_DK)
    # the rake boards along the two roof edges, and a scrap of shingle at the peak
    for sgn, tag in ((-1, "W"), (1, "E")):
        make_rot_box(f"Gable_Rake_{tag}", (-0.5 + sgn * 1.6, 8.20, 3.2 + 1.15 + 0.06), (3.95, 0.05, 0.14), (0.36, 0.34, 0.32, 1.0),
                     pitch=sgn * 0.623)
    make_rot_box("Gable_Shingle_Scrap", (-0.30, 8.55, 5.2), (0.5, 0.5, 0.05), COL_ROOF_DK, pitch=-0.62, roll=-0.2)
    # (the old board seams are the battens above now, carried up under the rakes)
    # The doorway (door long gone) + hay door above
    make_box("Doorway", (-1.2, 8.30, 1.25), (1.7, 0.45, 2.5), COL_DOOR)
    make_box("Hay_Door", (-0.5, 8.28, 4.05), (1.0, 0.40, 1.0), COL_DOOR)
    # (draft 7) the hay door's leaf: hung on its W strap hinges, swung out
    # and round 100 degrees, hanging open over the field
    import math as _m
    a = -_m.radians(100.0)
    hgx, hgy = -1.0, 8.17
    make_rot_box("Hay_Door_Leaf", (hgx + 0.5 * _m.cos(a), hgy + 0.5 * _m.sin(a), 4.05), (1.0, 0.05, 1.0), COL_BARN_DK, yaw=a)
    for k, hz in enumerate((3.75, 4.35)):
        make_box(f"Hay_Door_Hinge_{k}", (hgx, 8.20, hz), (0.10, 0.06, 0.05), (0.22, 0.20, 0.18, 1.0))
    # One leaning siding board by the doorway
    make_box("Lean_Board", (0.4, 8.05, 1.15), (0.28, 0.10, 2.3), COL_BARN_DK)


def build_collapse():
    """The fallen roof: two big shingle planes lying low on rubble at
    slightly different heights, plus surviving frame posts."""
    # The planes slid off the BACK half as they fell — the front bay
    # behind the gable survives as a sheltered pocket (the interior
    # vantage stands there)
    make_box("Roof_Plane_W", (-2.6, 12.4, 0.75), (4.4, 4.2, 0.30), COL_ROOF)
    make_box("Roof_Plane_E", (1.9, 12.8, 1.15), (4.0, 3.8, 0.30), COL_ROOF_DK)
    # (2026-09-23: Post_3 ran straight up through this plane; it is a
    # stub now, the post the plane came down on)
    make_box("Roof_Ridge_Piece", (-0.3, 13.6, 1.55), (3.2, 0.7, 0.35), COL_ROOF_DK)
    # Rubble bed under and around the planes
    rubble = [(-3.8, 9.6, 0.5), (-1.0, 10.2, 0.6),   # (Rubble_1 up to the W plane's underside, not 10 cm into it) (2.8, 9.8, 0.45), (0.6, 12.8, 0.55),
              (-4.4, 11.8, 0.4), (4.0, 11.6, 0.6), (2.0, 13.4, 0.35)]
    for i, (rx, ry, rh) in enumerate(rubble):
        make_box(f"Rubble_{i}", (rx, ry, rh / 2.0), (1.3 + 0.3 * (i % 3), 1.0, rh),
                 COL_RUBBLE)
    # Frame posts still standing inside the footprint, varied heights
    posts = [(-2.8, 10.4, 3.4), (1.6, 10.8, 2.6), (-0.4, 12.2, 3.0), (3.0, 12.6, 1.0)]
    for i, (px, py, ph) in enumerate(posts):
        make_box(f"Post_{i}", (px, py, ph / 2.0), (0.24, 0.24, ph), COL_FRAME)
    # on the ground, from the rubble's end (2026-09-23: 3.8 m of it ran
    # through Rubble_1 at knee height)
    make_box("Beam_Fallen", (-1.0, 11.95, 0.11), (0.22, 2.5, 0.22), COL_FRAME)
    # Scattered siding boards in the yard
    # (2026-10-23: three of the four were under the bramble; they lie out in the yard now)
    boards = [(-3.5, 4.6, 0.0), (-1.2, 6.2, 0.4), (-8.4, 5.2, -0.2), (7.6, 6.0, 0.3)]
    for i, (bx, by, rot_hint) in enumerate(boards):
        make_box(f"Board_{i}", (bx, by, 0.06), (1.9 + 0.4 * (i % 2), 0.26, 0.06),
                 COL_BARN_DK)


def build_yard():
    # Remnant fence line, posts missing rails in places
    for i in range(7):
        fx = -9.0 + i * 3.0
        if i == 3:
            continue  # the gap where the gate was
        make_box(f"Fence_Post_{i}", (fx, 3.4, 0.5), (0.14, 0.14, 1.0), COL_FENCE)
    make_cyl("Fence_Rail_W", (-6.0, 3.4, 0.78), 0.05, 5.8, COL_FENCE, segments=6, axis='X')
    make_cyl("Fence_Rail_E", (6.0, 3.4, 0.72), 0.05, 5.6, COL_FENCE, segments=6, axis='X')
    # Rusted water trough
    make_box("Trough", (4.6, 5.4, 0.30), (1.6, 0.7, 0.60), COL_TROUGH,
             open_faces={"+Z"})
    # Weeds: clumps through the yard, taller at the walls
    clumps = [(-4.8, 5.0), (-2.0, 4.4), (3.6, 4.2),
              (-5.6, 9.0), (5.0, 8.8), (0.0, 3.2), (-7.5, 6.0)]   # (three clumps under the bramble now, 2026-10-23)
    for ci, (cx, cy) in enumerate(clumps):
        for b in range(4):
            bx = cx + 0.14 * ((b * 5 + ci * 3) % 5 - 2)
            h = 0.4 + 0.16 * ((b + ci) % 3) + (0.3 if cy > 7.0 else 0.0)
            col = COL_WEED if (b + ci) % 2 == 0 else COL_WEED_DRY
            make_box(f"Weed_{ci}_{b}", (bx, cy + 0.08 * (b % 2), h / 2.0),
                     (0.05, 0.05, h), col)


def build_interior():
    """Inside the standing half, y ∈ [8.6, 13]: the cabinet with the
    broken marionette, and the carved sign half-hanging opposite."""
    # A patch of old plank floor under the props (the surviving bay)
    make_box("Int_Floor", (-0.6, 9.6, 0.03), (5.0, 1.8, 0.06), (0.34, 0.28, 0.22, 1.0))
    # The cabinet — against the gable's inner face beside the sign,
    # glass fourth wall facing north into the bay
    cbx, cby = -1.8, 8.95
    # a hollow case — base, back, sides, head (2026-09-23: Cab_Body was
    # one solid block and Jiggles hung inside the wood)
    cab = (0.30, 0.22, 0.16, 1.0)
    make_box("Cab_Body", (cbx, cby, 0.36), (0.7, 0.9, 0.72), cab)
    make_box("Cab_Back", (cbx, cby - 0.43, 1.31), (0.7, 0.04, 1.18), cab)
    for sgn, tag in ((-1, "W"), (1, "E")):
        make_box(f"Cab_Side_{tag}", (cbx + sgn * 0.33, cby + 0.02, 1.31), (0.04, 0.86, 1.18), cab)
    make_box("Cab_Head", (cbx, cby + 0.02, 1.85), (0.62, 0.86, 0.10), cab)
    make_box("Cab_Stage", (cbx + 0.1, cby, 0.75), (0.45, 0.7, 0.06), (0.44, 0.34, 0.22, 1.0))
    # Glass fourth wall (north face), broken: partial pane + shard
    # the pane is BROKEN: what is left is a jagged strip along the head
    # (2026-09-24: the "partial pane" was 0.55 x 0.75 m over the whole
    # opening — no alpha in this pipeline, so it hid Jiggles entirely)
    make_box("Cab_Glass", (cbx - 0.035, cby + 0.42, 1.5875), (0.55, 0.02, 0.175),
             (0.55, 0.62, 0.66, 0.35))
    # (2026-10-30: the shard stood across Jiggles in both inserts; it is a
    # stub in the W corner now, and the rest of the pane lies on the boards)
    make_box("Cab_Glass_Shard", (cbx - 0.255, cby + 0.42, 0.86), (0.10, 0.02, 0.14),
             (0.55, 0.62, 0.66, 0.5))
    for i, (gx, gy_, w, d) in enumerate(((-0.15, 0.62, 0.16, 0.10), (0.12, 0.75, 0.10, 0.07),
                                         (0.30, 0.58, 0.07, 0.12), (-0.32, 0.90, 0.06, 0.05))):
        make_box(f"Cab_Glass_Floor_{i}", (cbx + gx, cby + gy_, 0.065), (w, d, 0.006), (0.66, 0.72, 0.74, 1.0))
    # Jiggles the Juggler — sagging at the hip, head against shoulder
    make_box("Jiggles_Torso", (cbx + 0.08, cby, 1.10), (0.14, 0.18, 0.30),
             (0.56, 0.44, 0.30, 1.0))
    # slumped onto the stage, torso to boards (2026-09-23: hung 5 cm over it)
    make_box("Jiggles_Hip_Sag", (cbx + 0.06, cby + 0.06, 0.865), (0.13, 0.16, 0.17),
             (0.48, 0.36, 0.26, 1.0))
    make_cyl("Jiggles_Head", (cbx + 0.14, cby - 0.09, 1.30), 0.07, 0.12,
             (0.78, 0.68, 0.55, 1.0), segments=8)
    make_box("Jiggles_Arm_L", (cbx + 0.04, cby - 0.115, 1.02), (0.05, 0.05, 0.26),   # at the shoulder
             (0.56, 0.44, 0.30, 1.0))
    make_box("Jiggles_Arm_R", (cbx + 0.04, cby + 0.115, 1.12), (0.05, 0.05, 0.22),
             (0.56, 0.44, 0.30, 1.0))
    # His name in red paint on the cabinet base (north face)
    # (2026-10-30: a cream board with the name's strokes in red, not one red bar)
    make_box("Jiggles_Name", (cbx, cby + 0.46, 0.62), (0.56, 0.02, 0.10),
             (0.70, 0.62, 0.46, 1.0))
    for i in range(14):
        if i == 7:
            continue                              # the space between the words
        make_box(f"Jiggles_Name_Letter_{i}", (cbx - 0.24 + 0.037 * i, cby + 0.4725, 0.62 + 0.006 * (i % 2)),
                 (0.022, 0.006, 0.055 - 0.01 * (i % 3 == 2)), (0.62, 0.14, 0.10, 1.0))
    # Marionette strings up into the case head
    # from the case head down to head, shoulders, hip
    for i, (sy, sb) in enumerate(((cby - 0.1, 1.36), (cby, 1.25), (cby + 0.1, 0.95))):
        make_box(f"Jiggles_String_{i}", (cbx + 0.08, sy, (1.80 + sb) / 2.0), (0.008, 0.008, 1.80 - sb),
                 (0.62, 0.60, 0.55, 1.0))
    # (the carved sign is build_bay_2026_10's now: 2026-10-30, the relief
    # stood 5-10 cm BEHIND its panels, inside the gable, and the camera saw
    # two blank boards)
    # (2026-09-24: the "shaft of daylight" box is gone — vertex alpha does
    # not render as translucent, so it was a solid pale slab standing
    # between the interior camera and the cabinet and the sign. The light
    # through the roof is the scene's Interior_Shaft OmniLight.)


COL_BOARD_IN = (0.36, 0.33, 0.30, 1.0)     # the boards' inner faces, out of the weather
COL_BATTEN = (0.27, 0.25, 0.23, 1.0)
COL_GAP_DAY = (0.86, 0.83, 0.72, 1.0)      # daylight in a crack
COL_BRASS = (0.70, 0.56, 0.26, 1.0)


def build_bay_2026_10():
    """DRAFT 4 (2026-10-30): the surviving bay as a ROOM. From inside, the
    camera saw the gable's back as a blank stepped slab with open sky either
    side, two plain boards for the sign, and a little dark case.

    - the side walls' remnants: board walls running N from the gable's ends,
      each board broken off lower than the last, a few missing (sky and
      sun through the gaps), the ones under the fallen planes snapped short
    - the gable's inner face framed the way a barn is: corner posts, a
      middle post, a girt the sign hangs from, battens between
    - the doorway from inside, boarded, daylight in the cracks
    - Jiggles' cabinet: the marquee board, faded red curtains either side of
      the little stage, the brass "buttons and levers that ... still worked"
    - the sign HALF hanging: one chain holds the W corner, the E chain hangs
      broken and the board has swung down; the mermaid carved IN FRONT of the
      board this time: rock, figure, hair "falling down below her waist",
      the "long bluefish tail that hugged the rock", the surf behind, the
      line of old script
    """
    gy = 8.575                       # the gable's inner face
    # -- side walls, W (x -3.55) and E (x 2.62) --
    for side, x in (("W", -3.55), ("E", 2.62)):
        for k in range(12):
            y = 8.70 + 0.24 * k
            if (k + (0 if side == "W" else 1)) % 5 == 3:
                continue                                   # a board gone
            h = 3.05 - 0.17 * k - 0.22 * ((k * 7 + (3 if side == "E" else 0)) % 3)
            z0 = 0.0
            if side == "W" and y > 11.0:
                continue                                   # Rubble_2's heap took this board down
            if side == "W" and 9.05 < y < 10.15:
                z0 = 0.5                                   # standing on Rubble_0
            if side == "W" and y > 10.2:
                h = min(h, 0.52)                           # under Roof_Plane_W
            if side == "E" and y > 10.8:
                h = min(h, 0.95)                           # under Roof_Plane_E
            if h - z0 < 0.3:
                continue
            make_box(f"Bay_Wall_{side}_{k}", (x, y, (z0 + h) / 2.0), (0.05, 0.20, h - z0),
                     (COL_BOARD_IN, COL_BARN_DK)[k % 2])
        # a girt along the inner side at hip height, where the boards still reach
        gx = x + (0.06 if side == "W" else -0.06)
        make_box(f"Bay_Girt_{side}", (gx, 9.30, 1.20), (0.07, 1.40, 0.14), COL_FRAME)
    # -- the gable's inner face: posts, girts, battens --
    for i, px in enumerate((-3.40, -0.15, 2.48)):
        make_box(f"Bay_Post_{i}", (px, gy + 0.11, 1.60), (0.20, 0.22, 3.2), COL_FRAME)
    for i, (x0, x1) in enumerate(((-3.30, -0.25), (-0.05, 2.38))):
        make_box(f"Bay_Girt_S_{i}", ((x0 + x1) / 2.0, gy + 0.04, 2.40), (x1 - x0, 0.08, 0.14), COL_FRAME)
    for i in range(13):
        bx = -3.10 + i * 0.45
        if -2.25 < bx < -0.20 or abs(bx - (-0.15)) < 0.2:
            continue                                       # the cabinet, the door, the post
        make_box(f"Bay_Batten_{i}", (bx, gy + 0.0075, 1.60), (0.07, 0.015, 3.15), COL_BATTEN)
    # -- the doorway, boarded from inside (what the cabinet leaves showing) --
    for i, dx in enumerate((-1.30, -0.95, -0.60)):
        make_box(f"Bay_Door_Plank_{i}", (dx, gy + 0.02, 1.25), (0.32, 0.03, 2.48), COL_BOARD_IN)
    for i, dx in enumerate((-1.125, -0.775)):
        make_box(f"Bay_Door_Crack_{i}", (dx, gy + 0.004, 1.25), (0.03, 0.006, 2.40), COL_GAP_DAY)
    make_box("Bay_Door_Header", (-1.2, gy + 0.05, 2.53), (1.80, 0.08, 0.10), COL_FRAME)
    make_rot_box("Bay_Boarded_Brace", (-0.95, gy + 0.05, 1.25), (0.10, 0.03, 2.2), COL_FRAME, pitch=-0.42)
    # -- Jiggles' cabinet (Cab_* in build_interior: x -2.15..-1.45, front y 9.40) --
    cbx, cfy = -1.8, 9.40
    make_box("Cab_Marquee", (cbx, cfy - 0.02, 2.02), (0.70, 0.04, 0.24), (0.66, 0.56, 0.38, 1.0))
    make_box("Cab_Marquee_Stripe", (cbx, cfy + 0.005, 2.02), (0.62, 0.012, 0.05), (0.58, 0.16, 0.12, 1.0))
    for sgn, tag in ((-1, "W"), (1, "E")):
        make_box(f"Cab_Curtain_{tag}", (cbx + sgn * 0.255, cfy - 0.06, 1.30), (0.06, 0.05, 1.00),
                 (0.44, 0.13, 0.12, 1.0))
    make_box("Cab_Valance", (cbx, cfy - 0.06, 1.74), (0.56, 0.05, 0.10), (0.44, 0.13, 0.12, 1.0))
    for i in range(3):
        make_cyl(f"Cab_Button_{i}", (cbx - 0.20 + 0.10 * i, cfy + 0.015, 0.46), 0.025, 0.03, COL_BRASS,
                 segments=10, axis='Y')
    for i, lx in enumerate((0.12, 0.22)):
        make_rot_box(f"Cab_Lever_{i}", (cbx + lx, cfy + 0.05, 0.42), (0.02, 0.02, 0.17), COL_BRASS,
                     roll=0.35 + 0.25 * i)
        make_cyl(f"Cab_Lever_Knob_{i}", (cbx + lx, cfy + 0.08, 0.50 - 0.02 * i), 0.022, 0.04,
                 (0.18, 0.14, 0.10, 1.0), segments=8, axis='Y')
    make_box("Cab_Coin_Plate", (cbx, cfy + 0.008, 0.30), (0.12, 0.016, 0.08), COL_BRASS)
    # -- the sign, half hanging --
    import math
    scx, scz, th = 1.05, 1.50, 0.30           # centre on the face; swung down at the E end
    sy = gy + 0.10                            # 4 cm off the battens

    def at(u, v):
        return (scx + u * math.cos(th) + v * math.sin(th), scz - u * math.sin(th) + v * math.cos(th))

    def relief(name, u, v, w, h, col, dz=0.0):
        x, z = at(u, v)
        make_rot_box(name, (x, sy + 0.035 + dz, z), (w, 0.02, h), col, pitch=th)

    make_rot_box("Sign_Board", (scx, sy, scz), (1.30, 0.05, 0.85), (0.46, 0.34, 0.20, 1.0), pitch=th)
    for nm, u, v, w, h in (("Top", 0, 0.40, 1.30, 0.05), ("Bot", 0, -0.40, 1.30, 0.05),
                           ("W", -0.625, 0, 0.05, 0.75), ("E", 0.625, 0, 0.05, 0.75)):
        relief(f"Sign_Rim_{nm}", u, v, w, h, (0.36, 0.26, 0.16, 1.0))
    relief("Sign_Surf", -0.20, 0.20, 0.70, 0.16, (0.70, 0.72, 0.66, 1.0))
    relief("Sign_Sea", 0.0, 0.02, 1.15, 0.18, (0.30, 0.40, 0.46, 1.0))
    relief("Sign_Rock", -0.06, -0.12, 0.40, 0.20, (0.40, 0.33, 0.26, 1.0), dz=0.005)
    relief("Sign_Figure", -0.10, 0.10, 0.12, 0.24, (0.72, 0.58, 0.44, 1.0), dz=0.01)
    relief("Sign_Head", -0.10, 0.27, 0.09, 0.09, (0.72, 0.58, 0.44, 1.0), dz=0.01)
    relief("Sign_Hair", -0.05, 0.10, 0.06, 0.38, (0.20, 0.14, 0.10, 1.0), dz=0.015)
    relief("Sign_Tail", 0.12, -0.08, 0.30, 0.07, (0.26, 0.44, 0.52, 1.0), dz=0.01)
    relief("Sign_Tail_Fin", 0.30, -0.02, 0.08, 0.13, (0.26, 0.44, 0.52, 1.0), dz=0.01)
    relief("Sign_Script", 0.0, -0.30, 1.05, 0.10, (0.60, 0.50, 0.36, 1.0))
    for i in range(9):
        relief(f"Sign_Letter_{i}", -0.44 + 0.11 * i, -0.30, 0.06, 0.045, (0.30, 0.22, 0.14, 1.0), dz=0.005)
    # the W chain still holds; the E chain broke and hangs from the girt
    wx, wz = at(-0.65, 0.425)
    make_box("Sign_Chain_W", (wx, sy, (wz + 2.33) / 2.0), (0.015, 0.015, 2.33 - wz), (0.30, 0.28, 0.26, 1.0))
    make_box("Sign_Chain_E", (at(0.65, 0.425)[0], gy + 0.06, 2.19), (0.015, 0.015, 0.28), (0.30, 0.28, 0.26, 1.0))


COL_BRAMBLE = (0.22, 0.30, 0.16, 1.0)
COL_BRAMBLE_LT = (0.30, 0.38, 0.20, 1.0)
COL_HILL = (0.36, 0.42, 0.24, 1.0)


COL_BRAMBLE_DK = (0.14, 0.20, 0.11, 1.0)
COL_BRAMBLE_YL = (0.38, 0.44, 0.22, 1.0)      # the new growth at the tips
COL_CANE = (0.38, 0.22, 0.20, 1.0)            # blackberry cane, red-brown


def _bramble(name, center, r, col, seed, squash, canes=(), light=None, tip=None, dark=None):
    """(2026-11-02, draft 6) A bramble mound as a bramble: a dark core with
    the leaf clusters packed over its dome (inside the old blob's bounds,
    so nothing it cleared it now touches) and arching canes thrown out
    along `canes` (headings in radians, only where the ground is open).
    The old single faceted blob read from the field as a grey boulder.
    Every part is `<name>_Stock_*`: join_stock makes the mound one mesh."""
    cx, cy, cz = center
    rng = random.Random(seed)
    hz = r * squash
    light, tip, dark = light or COL_BRAMBLE_LT, tip or COL_BRAMBLE_YL, dark or COL_BRAMBLE_DK
    # the core sits on the mound's own floor (inset 20 %, it hung off the ground)
    make_blob(f"{name}_Stock_Core", (cx, cy, cz - hz * 0.20), r * 0.80, dark, noise=0.22, seed=seed, squash=squash)
    n = int(10 + 26 * r)
    for k in range(n):
        th = rng.uniform(0.0, 2.0 * math.pi)
        ph = rng.uniform(-0.15, 1.35)
        rr = rng.uniform(0.16, 0.30) * min(1.0, 0.45 + r * 0.5)
        reach = max(0.0, r - rr)
        x = cx + reach * math.cos(ph) * math.cos(th)
        y = cy + reach * math.cos(ph) * math.sin(th)
        z = max(cz + (hz - rr * 0.8) * math.sin(ph), rr * 0.75)
        c = (col, light, tip if ph > 0.9 else col)[k % 3]
        make_blob(f"{name}_Stock_Leaf_{k}", (x, y, z), rr, c, noise=0.35, seed=seed * 7 + k, squash=0.8, rings=4, segments=7)
    for k, a in enumerate(canes):
        ca, sa = math.cos(a), math.sin(a)
        top = cz + hz * 0.80              # out of the mound's flank, not over its crown
        out = r * 1.35
        path = [(cx + ca * r * 0.4, cy + sa * r * 0.4, cz + hz * 0.4),
                (cx + ca * r * 0.95, cy + sa * r * 0.95, top),
                (cx + ca * r * 1.2, cy + sa * r * 1.2, top * 0.6),
                (cx + ca * out, cy + sa * out, 0.03)]
        make_tube(f"{name}_Stock_Cane_{k}", path, 0.014, COL_CANE, segments=5)
        make_blob(f"{name}_Stock_Cane_Tip_{k}", (cx + ca * r * 1.0, cy + sa * r * 1.0, top - 0.02), 0.11, tip,
                  noise=0.3, seed=seed + 90 + k, squash=0.8, rings=4, segments=6)


def _ivy(name, stem, seed, n):
    """Ivy up the gable's face: a stem from the bramble at the foot up the
    boards, its leaves packed along it (flat to the wall, in contact with
    the battens at y 8.205). One `_Stock_` mesh."""
    rng = random.Random(seed)
    make_tube(f"{name}_Stock_Stem", stem, 0.022, COL_CANE, segments=5)
    for k in range(n):
        t = rng.uniform(0.0, 1.0)
        seg = min(int(t * (len(stem) - 1)), len(stem) - 2)
        f = t * (len(stem) - 1) - seg
        a, b = stem[seg], stem[seg + 1]
        x = a[0] + (b[0] - a[0]) * f + rng.uniform(-0.16, 0.16)
        z = a[2] + (b[2] - a[2]) * f + rng.uniform(-0.12, 0.12)
        c = (COL_BRAMBLE, COL_BRAMBLE_LT, COL_BRAMBLE_DK)[k % 3]
        make_rot_box(f"{name}_Stock_Leaf_{k}", (x, 8.19, z), (0.14, 0.03, 0.12), c, yaw=rng.uniform(-0.25, 0.25),
                     pitch=rng.uniform(-0.6, 0.6))


def build_foliage():
    """"Foliage consuming much of the exterior — more negative space
    than positive": bramble mounds against the gable face, over the
    fallen roof planes, in the doorway's jambs and along the fence."""
    # against the gable's outer face (y < 8.2), seated on the field
    # (each mound's y + r stays under 8.2 — the gable's face; the two past the
    # gable's ends sit clear of the rubble and the weed clumps)
    # (the arching canes went: from the field they read as lollipops on sticks)
    mounds = ((-0.6, 7.5, 0.5, 15, ()), (-5.8, 7.4, 0.9, 16, ()), (5.4, 7.6, 0.9, 17, ()))
    for i, (x, y, r, sd, canes) in enumerate(mounds):
        _bramble(f"Bramble_{i}", (x, y, r * 0.7 - 0.03), r, (COL_BRAMBLE, COL_BRAMBLE_LT)[i % 2], 40 + sd, 0.7, canes)
    # climbing the gable: two tall mounds, seated, reaching the hay door
    for i, (x, r, sd, canes) in enumerate(((-3.1, 1.5, 21, ()), (2.1, 1.5, 22, ()))):
        _bramble(f"Bramble_Climb_{i}", (x, 8.2 - r - 0.05, r - 0.03), r, COL_BRAMBLE, 40 + sd, 1.0, canes)
    # over the fallen planes: the collapse is going back to the hill
    for i, (x, y, z, r, sd) in enumerate(((-3.6, 12.0, 0.9, 1.3, 31), (-3.2, 14.2, 0.9, 0.8, 32), (2.8, 13.6, 1.3, 1.2, 33),
                                          (2.4, 11.9, 1.3, 0.7, 34), (5.2, 9.9, 0.0, 0.9, 35))):
        _bramble(f"Bramble_Roof_{i}", (x, y, z + r * 0.55), r, (COL_BRAMBLE_LT, COL_BRAMBLE)[i % 2], 40 + sd, 0.55)
    # the fence line is going under too (low, under the rails)
    for i, x in enumerate((-7.6, -4.4, 4.6, 7.4)):
        _bramble(f"Bramble_Fence_{i}", (x, 3.5, 0.23), 0.5, COL_BRAMBLE_LT, 60 + i, 0.5)
    # (draft 6) the ivy up the boards from the two climbing mounds: the
    # west one to under the rake, the east one across toward the hay door
    _ivy("Ivy_W", [(-2.95, 8.19, 2.55), (-2.75, 8.19, 3.10), (-2.55, 8.19, 3.55), (-2.20, 8.19, 3.85)], 81, 46)
    _ivy("Ivy_E", [(1.95, 8.19, 2.55), (1.70, 8.19, 3.10), (1.25, 8.19, 3.55), (0.55, 8.19, 3.90), (0.25, 8.19, 4.35)], 82, 58)


def build_roof_remnant():
    """What is left of the roof over the surviving bay (y 8.6..12):
    four rafters off the gable's top and three strips of shingle still
    on them, gaps between — the sun comes through the gaps."""
    # (within the peak's width, x -1.7..0.7, so from the field they are
    # behind the gable top and not a slab hung in the sky)
    # a ridge beam against the peak's back face (y 8.55); the rafters hang
    # off it (their high end at y 8.70, z 5.08) and slope down to the fallen
    # half (roll about X: a negative roll drops the +y end)
    make_box("Ridge_Beam", (-0.6, 8.63, 5.12), (2.0, 0.16, 0.16), COL_FRAME)
    for i, x in enumerate((-1.5, -0.7, 0.1)):
        make_rot_box(f"Rafter_{i}", (x, 10.34, 4.35), (0.12, 3.6, 0.16), COL_FRAME, roll=-0.42)


def build_debris():
    """"remnants in corners, hidden in shadow": the bay's floor dirt,
    a broken crate, a coil of rope, bottles, a bucket on its side."""
    make_box("Crate_Broken", (2.1, 10.9, 0.26), (0.5, 0.5, 0.44), (0.40, 0.32, 0.22, 1.0))
    make_rot_box("Crate_Lid", (2.5, 11.3, 0.06), (0.5, 0.5, 0.03), (0.40, 0.32, 0.22, 1.0), yaw=0.5)
    make_cyl("Rope_Coil", (-2.7, 10.9, 0.05), 0.22, 0.10, (0.50, 0.42, 0.30, 1.0), segments=12)
    for i, (x, y) in enumerate(((-2.3, 11.6), (-2.1, 11.5), (2.3, 9.4))):
        make_cyl(f"Bottle_{i}", (x, y, 0.13), 0.035, 0.26, (0.28, 0.36, 0.30, 1.0), segments=8)
    make_cyl("Bucket_Side", (-2.4, 9.3, 0.20), 0.14, 0.30, (0.34, 0.32, 0.30, 1.0), segments=10, axis='Y')   # on the plank patch


HILL_Y0 = 15.0                  # (draft 7) the hill's foot: at the back of the collapse


def hill_h(x, y):
    """The hill's height at (x, y): 0 at its foot (HILL_Y0) rising to a
    rounded crest ~8.5 m up 36 m back; the lumps grow with the rise so the
    foot meets the field with no step."""
    t = max(0.0, (y - HILL_Y0) / 36.0)
    return 8.5 * (t ** 1.3) * (1.0 - 0.25 * (x / 32.0) ** 2)


def build_hill():
    """"I thought it part of the hill": (draft 7, 2026-11-02) the ground
    rises from right behind the collapse (its foot at y 15, where the fallen
    roof's bramble ends), so from the field the barn's broken back runs into
    the slope; the hedge sits on it. Draft 3's hill began 6 m further back
    and read as a separate rise behind a barn in a field."""
    rows = []
    for j in range(10):         # y 15 .. 51 at 4 m
        y = HILL_Y0 + j * 4.0
        row = []
        for i in range(17):     # x -32 .. 32 at 4 m
            x = -32.0 + i * 4.0
            lump = 0.6 * ((i * 7 + j * 3) % 5) / 5.0 * min(1.0, j / 2.0)
            row.append(round(hill_h(x, y) + lump, 2))
        rows.append(row)
    make_heightfield("Hill", (-32.0, HILL_Y0, 0.0), 4.0, rows, COL_HILL, skirt=0.3)


def build_backdrop():
    # 2026-08-04 · this was a hedgerow and then a 104m-wide "Sky"
    # slab standing 11m past it with NOTHING behind it — the
    # louisiana_road failure exactly: the field stopped at a painted
    # wall. The horizon is the environment's job (fog + sky in the
    # .tscn). Geometry's job is to keep receding until fog eats it.
    # the hedge behind the barn is FOLIAGE (2026-09-30, the 09-26 sheet:
    # six 4.8 x 3.2 m boxes read as grey walls either side of the gable)
    for i in range(6):
        tx = -14.0 + i * 5.5
        for k in range(2):
            r = 1.7 + 0.25 * ((i + k) % 3)
            # seated on the field by its squashed half-height (a blob's
            # half-height is radius x squash), 2 cm in
            # the back row is on the hill now (2026-10-23): ground ~0.5-0.9 m up at y 26
            hy = (18.5, 26.0)[k]
            gz = hill_h(tx - 1.2 + k * 2.4, hy)        # (draft 7) seated on the hill where it stands
            # (draft 6) leafed like the bramble: one faceted blob read as a boulder
            _bramble(f"Hedge_{i}_{k}", (tx - 1.2 + k * 2.4, hy, gz + 0.005 + r * 0.85),
                     r, COL_TREE, 70 + i * 2 + k, 0.85, light=(0.26, 0.33, 0.20, 1.0), tip=(0.32, 0.38, 0.22, 1.0),
                     dark=(0.12, 0.16, 0.10, 1.0))
    # GROUND out past the last windbreak (2026-08-09 ground wave):
    # wheat-stubble section, not a void.
    make_box("Ground_Far", (0.0, 0.0, -0.03), (1680.0, 1680.0, 0.02),
             (0.46, 0.41, 0.26, 1.0))   # wheat stubble (2026-09-30: lifted with the field)
    # Receding hedgerows and windbreaks out across the section, each
    # band dimmer and lower so aerial perspective has steps to grade.
    for i, (by, bw, bh, shade) in enumerate([
            (60.0, 60.0, 5.0, 0.88), (130.0, 110.0, 6.0, 0.74),
            (260.0, 190.0, 7.5, 0.60), (460.0, 300.0, 9.0, 0.48),
            (760.0, 440.0, 11.0, 0.38)]):
        c = (COL_TREE[0] * shade, COL_TREE[1] * shade,
             COL_TREE[2] * shade, 1.0)
        make_box(f"FarWindbreak_{i}", (0.0, by, bh * 0.5),
                 (bw, 5.0, bh), c)
        # a farm building or two out on the section line
        if i in (1, 3):
            make_box(f"FarBarn_{i}", (bw * 0.35, by - 8.0, 3.0),
                     (7.0, 5.0, 6.0), c)


def main():
    clear_scene()
    build_field()
    build_gable()
    build_collapse()
    build_interior()
    build_yard()
    build_foliage()
    build_roof_remnant()
    build_debris()
    build_bay_2026_10()
    build_hill()
    build_backdrop()
    join_stock()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/crumpled_barn.glb"))
    print(f"\n[build_crumpled_barn] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
