"""dean_offices — the rooms of Dickens Dean's business, vols 1 and 4
(draft 1, 2026-10-17).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Four places, five stems, one GLB; they are different buildings and share
nothing but the man.

THE OFFICE (origin) — vol 1, day. Not Dean's: "This is your new office. The
cover you'll use is game design." A modest modern building "tucked into the
quiet part of a neighborhood": the street door Dean unlocks, glass beside it,
a desk for each of the three, the goggles on them, the business card on
Jacob's ("Oneironautics"), the coffee Dean holds.
THE TUTORIAL (x 30..44) — "These office spaces were carved out of
imagination": a lobby a little too smooth to be real, "Hazy", Olivia's
console, the television they watch. Nobody walks in; they appear.
THE CLUB OFFICE (x 60..68) — vol 1, night: Dean's back office in Club #,
off the empty floor where Joan's cage is. The three t-shirts laid out, each
a different hero design; the four listening devices; the small needle
devices; the body of young Aria at rest under a sheet (where she lies is
not stated: on the couch, covered, with restraint); the door out to the
club, its neon spilling in.
THE MONITOR ROOM (x 100..107) — vol 4: Dean's bedroom office in the glass
house on the Pacific. "stands alone in the center of computer monitors":
a ring of screens round an open centre, the nearest showing a text game
and its cursor, the desk where the clunky goggles live, the doorway (the
girl is the sprite's, never the set's), the glass with the dark ocean.
THE TOWER CORRIDOR (x 140..146) — vol 4: his office building at night, the
city through the glass, and the door at the end ("These are the things you
probably shouldn't see") shut, its light under it. Nothing behind it.

Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 (2026-10-22, pass 142 — the contact sheet read it as a hall with
three desks in it): THE OFFICE dressed as what the cover says it is, a small
game studio. Daylight on three sides (two W windows with blinds onto the
side yard and the neighbour, a clerestory band over the desks, the street
glass made glass, alpha 0.25); the chairs turned to face their desks (draft
1 sat all three backs to the work); a pedestal, a lamp, a mug and a pinboard
of sketches at each desk; a playtest table mid-room (prototype board, card
decks, dice, index cards, a laptop) with seven chairs; the whiteboard
between the W windows; a lounge on the E side (sofa, armchair, low table,
rug, print, plant); the coffee counter moved up the E wall under two
cabinets; a shelf of boxed games by the back door; a coat stand by the
street door; troffers as a 3 x 3 grid.
DRAFT 3 targets: a lounge preset (no camera sees the sofa); the back room
behind the N door; cords from the desks to the outlets; the lobby's haze
as a real fog pass, not ambient; the club office as a room of
build_club_sharp.py so the door shows the real floor and Joan's cage; the
glass house as one set with vol4_glass_tower (the monitors there are the
same); the tower's city as a proper skyline (Shanghai is the sequence's,
not the text's); Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_tube,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_window, make_blinds
from _props.furniture import make_chair, make_lamp, make_table, make_sofa
from _props.objects import make_mug
from _props.decor import make_faded_poster, make_floor_plant
from _props.views import make_view
from _props.detail import make_wall_outlet, make_light_switch

WHITE = (0.90, 0.90, 0.88, 1.0); OFFWHITE = (0.84, 0.84, 0.80, 1.0)
DESK = (0.70, 0.62, 0.50, 1.0); DESK_LEG = (0.30, 0.30, 0.32, 1.0)
FLAT = (0.10, 0.10, 0.11, 1.0)
GLASS = (0.56, 0.66, 0.72, 0.25)
CLUB_WALL = (0.30, 0.24, 0.32, 1.0); NEON_PINK = (0.98, 0.30, 0.66, 1.0); NEON_CYAN = (0.30, 0.90, 0.98, 1.0)
WOOD = (0.52, 0.38, 0.26, 1.0); WOOD_DARK = (0.34, 0.24, 0.16, 1.0)


def goggles(prefix, x, y, z, yaw=0.0):
    """The goggles: two round lenses on a bridge, the strap trailing."""
    c, s = math.cos(yaw), math.sin(yaw)
    for e in (-1, 1):
        make_cyl(f"{prefix}_Lens_{e:+d}", (x + e * 0.045 * c, y + e * 0.045 * s, z + 0.025), 0.035, 0.05, (0.14, 0.14, 0.16, 1.0), segments=12)
        make_cyl(f"{prefix}_Glass_{e:+d}", (x + e * 0.045 * c, y + e * 0.045 * s, z + 0.052), 0.028, 0.004, (0.40, 0.70, 0.66, 1.0), segments=12)
    make_rot_box(f"{prefix}_Bridge", (x, y, z + 0.03), (0.04, 0.02, 0.012), (0.20, 0.20, 0.22, 1.0), yaw=yaw)
    make_rot_box(f"{prefix}_Strap", (x - 0.06 * s, y + 0.06 * c, z + 0.004), (0.22, 0.03, 0.008), (0.10, 0.10, 0.10, 1.0), yaw=yaw + 0.3)


def flat_monitor(prefix, x, y, z, face="-Y", w=0.50, glow=(0.30, 0.40, 0.56, 1.0)):
    sgn = -1.0 if face in ("-Y", "-X") else 1.0
    along_x = face in ("-Y", "+Y")
    h = w * 0.62
    if along_x:
        make_box(f"{prefix}_Body", (x, y, z + 0.12 + h / 2.0), (w, 0.04, h), FLAT)
        make_box(f"{prefix}_Screen", (x, y + sgn * 0.022, z + 0.12 + h / 2.0), (w - 0.04, 0.004, h - 0.04), glow)
        make_box(f"{prefix}_Neck", (x, y - sgn * 0.03, z + 0.07), (0.05, 0.03, 0.14), FLAT)
        make_box(f"{prefix}_Foot", (x, y - sgn * 0.03, z + 0.006), (0.22, 0.16, 0.012), FLAT)
    else:
        make_box(f"{prefix}_Body", (x, y, z + 0.12 + h / 2.0), (0.04, w, h), FLAT)
        make_box(f"{prefix}_Screen", (x + sgn * 0.022, y, z + 0.12 + h / 2.0), (0.004, w - 0.04, h - 0.04), glow)
        make_box(f"{prefix}_Neck", (x - sgn * 0.03, y, z + 0.07), (0.03, 0.05, 0.14), FLAT)
        make_box(f"{prefix}_Foot", (x - sgn * 0.03, y, z + 0.006), (0.16, 0.22, 0.012), FLAT)


def desk(prefix, x, y, w=1.40, d=0.72, col=DESK):
    make_box(f"{prefix}_Top", (x, y, 0.735), (w, d, 0.03), col)
    for sx in (-1, 1):
        make_box(f"{prefix}_Leg_{sx:+d}", (x + sx * (w / 2.0 - 0.03), y, 0.36), (0.04, d - 0.06, 0.72), DESK_LEG)


# ── THE OFFICE ────────────────────────────────────────────────────────
OX0, OX1, OD, OH = -7.0, 7.0, 9.0, 3.0
DOOR_X = -4.5
OFF_DESK_X = (-3.5, 0.0, 3.5)
OFF_WIN_W = (2.3, 6.7)


def build_office():
    make_floor("Off_Floor", (0.0, OD / 2.0, 0.0), size_x=OX1 - OX0 + 0.4, size_y=OD + 0.4,
               palette={"vinyl": (0.62, 0.60, 0.56, 1.0), "seam": (0.54, 0.52, 0.48, 1.0)})
    make_box("Off_Ceil", (0.0, OD / 2.0, OH + 0.04), (OX1 - OX0 + 0.4, OD + 0.4, 0.08), (0.92, 0.92, 0.90, 1.0))
    pal = {"wall": OFFWHITE, "baseboard": (0.40, 0.40, 0.42, 1.0)}
    # draft 2: daylight on three sides — two tall windows in the W wall
    # onto the side yard and the neighbour's house, a clerestory band over
    # the three desks (the back fence and the trees above it)
    make_wall_with_openings("Off_Wall_W", (OX0, OD / 2.0, 0), length=OD + 0.4, height=OH, thickness=0.2, axis='Y', palette=pal,
                            baseboard_face_sign=+1, openings=[(y, 1.50, 1.60, 1.60) for y in OFF_WIN_W])
    for k, y in enumerate(OFF_WIN_W):
        wa = (OX0 + 0.10, y, 1.50)
        make_window(f"Off_Window_W_{k}", wa, width=1.50, height=1.50, axis='Y', room_dir=+1, see_through=True)
        make_blinds(f"Off_Window_W_{k}_Blinds", wa, width=1.50, height=1.50, axis='Y', room_dir=+1,
                    color=(0.88, 0.88, 0.84, 1.0), raised_frac=0.55 if k else 0.30)
    make_view("Off_Yard_W", "W", OX0 - 0.10, OD / 2.0, kind="side", ground_z=0.0, span=OD, seed=5)
    make_wall("Off_Wall_E", (OX1, OD / 2.0, 0), length=OD + 0.4, height=OH, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Off_Wall_N", (0.0, OD, 0), length=OX1 - OX0 + 0.4, height=OH, thickness=0.2, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(6.0, 1.0, 0.90, 2.0)] + [(x, 2.38, 2.50, 0.66) for x in OFF_DESK_X])
    for k, x in enumerate(OFF_DESK_X):
        make_window(f"Off_Clerestory_{k}", (x, OD - 0.10, 2.38), width=2.40, height=0.56, axis='X', room_dir=-1,
                    see_through=True, trim=False, cross_mullion=False)
    make_view("Off_Back_N", "N", OD + 0.10, 0.0, kind="back", ground_z=0.0, span=OX1 - OX0 + 0.4, seed=2)
    make_box("Off_Door_Back", (6.0, OD, 1.0), (0.86, 0.05, 2.0), (0.62, 0.58, 0.52, 1.0))
    # the front: a low wall, glass above it, the street door
    make_wall_with_openings("Off_Wall_S", (0.0, 0.0, 0), length=OX1 - OX0 + 0.4, height=OH, thickness=0.2, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(DOOR_X, 1.05, 1.0, 2.1), (1.5, 1.55, 8.0, 1.9)])
    make_box("Off_Front_Glass", (1.5, 0.0, 1.55), (8.0, 0.02, 1.9), GLASS)
    for k in range(5):
        make_box(f"Off_Front_Mullion_{k}", (-2.5 + k * 2.0, 0.0, 1.55), (0.05, 0.08, 1.9), (0.30, 0.30, 0.32, 1.0))
    make_box("Off_Door", (DOOR_X, 0.0, 1.05), (0.96, 0.05, 2.08), (0.30, 0.30, 0.32, 1.0))
    make_box("Off_Door_Glass", (DOOR_X, 0.0, 1.25), (0.70, 0.06, 1.40), GLASS)
    make_box("Off_Door_Lock", (DOOR_X + 0.38, -0.04, 1.0), (0.04, 0.03, 0.08), (0.74, 0.70, 0.56, 1.0))
    make_box("Off_Door_Lock_In", (DOOR_X + 0.38, 0.04, 1.0), (0.04, 0.03, 0.08), (0.74, 0.70, 0.56, 1.0))
    # the ceiling: a grid of lay-in troffers, not three panels
    for j, y in enumerate((2.2, 4.5, 6.8)):
        for k, x in enumerate((-4.0, 0.0, 4.0)):
            make_box(f"Off_Ceil_Panel_{j}{k}", (x, y, OH - 0.012), (0.62, 1.22, 0.024), (0.70, 0.70, 0.70, 1.0))
            make_box(f"Off_Ceil_Panel_{j}{k}_Lens", (x, y, OH - 0.026), (0.56, 1.16, 0.006), (0.99, 0.99, 0.95, 1.0))
    # the three desks side by side along the back wall under the clerestory;
    # a chair, a monitor and a pair of goggles at each; the business card on
    # Jacob's (the centre). Draft 2: the chairs face the desks (draft 1 sat
    # them back to the work), a drawer pedestal, a desk lamp and a pinboard
    # of game sketches over each — the cover is game design
    dy = OD - 0.10 - 0.36
    sketch = ((0.86, 0.80, 0.56, 1.0), (0.70, 0.84, 0.92, 1.0), (0.96, 0.96, 0.92, 1.0), (0.92, 0.70, 0.66, 1.0), (0.76, 0.88, 0.70, 1.0))
    for k, (nm, x) in enumerate(zip(("Faust", "Jacob", "Wagner"), OFF_DESK_X)):
        desk(f"Desk_{nm}", x, dy)
        flat_monitor(f"Desk_{nm}_Monitor", x + 0.25, dy + 0.18, 0.75, face="-Y", w=0.48)
        make_box(f"Desk_{nm}_Keyboard", (x + 0.20, dy - 0.14, 0.759), (0.44, 0.15, 0.018), (0.20, 0.20, 0.22, 1.0))
        make_box(f"Desk_{nm}_Mouse", (x + 0.52, dy - 0.12, 0.759), (0.06, 0.10, 0.02), (0.22, 0.22, 0.24, 1.0))
        goggles(f"Goggles_{nm}", x - 0.40, dy - 0.08, 0.75, yaw=0.2 * (k - 1))
        make_chair(f"Desk_{nm}_Chair", x + 0.05 * (k - 1), dy - 0.64, yaw=0.12 * (1 - k), wood=(0.24, 0.24, 0.26, 1.0),
                   seat_col=(0.18, 0.18, 0.20, 1.0))
        make_box(f"Desk_{nm}_Pedestal", (x + 0.42, dy + 0.02, 0.31), (0.40, 0.56, 0.62), (0.56, 0.56, 0.56, 1.0))
        for d in range(3):
            make_box(f"Desk_{nm}_Pedestal_Pull_{d}", (x + 0.42, dy - 0.265, 0.56 - d * 0.20), (0.14, 0.012, 0.016), (0.30, 0.30, 0.32, 1.0))
        make_lamp(f"Desk_{nm}_Lamp", x - 0.58, dy + 0.22, base_z=0.75, h=0.40, shade_col=(0.22, 0.22, 0.24, 1.0), body_col=(0.30, 0.30, 0.32, 1.0))
        make_box(f"Desk_{nm}_Pinboard", (x - 0.15, OD - 0.115, 1.50), (1.10, 0.02, 0.62), (0.62, 0.50, 0.36, 1.0))
        make_box(f"Desk_{nm}_Pinboard_Frame", (x - 0.15, OD - 0.108, 1.50), (1.14, 0.012, 0.66), (0.40, 0.40, 0.42, 1.0))
        for c in range(5):
            u = -0.38 + c * 0.19 + 0.02 * ((c * 7 + k) % 3 - 1)
            v = 0.12 if c % 2 else -0.10
            make_box(f"Desk_{nm}_Sketch_{c}", (x - 0.15 + u, OD - 0.127, 1.50 + v), (0.15, 0.004, 0.20 - 0.04 * (c % 2)), sketch[(c + k) % 5])
        make_mug(f"Desk_{nm}_Mug", x - 0.15, dy + 0.12, 0.75, ((0.84, 0.24, 0.20, 1.0), (0.92, 0.92, 0.90, 1.0), (0.24, 0.36, 0.60, 1.0))[k])
    make_box("Business_Card", (-0.30, dy - 0.26, 0.751), (0.09, 0.05, 0.002), (0.97, 0.97, 0.95, 1.0))
    make_box("Business_Card_Line", (-0.30, dy - 0.26, 0.7522), (0.06, 0.008, 0.0005), (0.16, 0.18, 0.30, 1.0))
    # the playtest table mid-room: the cover's work laid out — a prototype
    # board, card decks, dice, a laptop, index cards; six chairs and two ends
    tx, ty = -1.8, 4.5
    make_table("Play_Table", tx, ty, w=2.40, d=1.10, wood=(0.30, 0.30, 0.32, 1.0), top_col=(0.86, 0.84, 0.78, 1.0))
    for i, x in enumerate((tx - 0.80, tx, tx + 0.80)):
        make_chair(f"Play_Chair_S{i}", x, ty - 0.86, yaw=0.0, wood=(0.24, 0.24, 0.26, 1.0), seat_col=(0.30, 0.44, 0.56, 1.0))
        make_chair(f"Play_Chair_N{i}", x + 0.06 * (i - 1), ty + 0.88, yaw=math.pi + 0.08 * (i - 1), wood=(0.24, 0.24, 0.26, 1.0),
                   seat_col=(0.30, 0.44, 0.56, 1.0))
    make_chair("Play_Chair_W", tx - 1.56, ty, yaw=-math.pi / 2.0, wood=(0.24, 0.24, 0.26, 1.0), seat_col=(0.30, 0.44, 0.56, 1.0))
    make_box("Play_Board", (tx - 0.10, ty + 0.05, 0.7575), (0.56, 0.56, 0.008), (0.20, 0.36, 0.30, 1.0))
    for i in range(4):
        for j in range(4):
            if (i + j) % 2:
                make_box(f"Play_Board_Tile_{i}{j}", (tx - 0.31 + i * 0.14, ty - 0.16 + j * 0.14, 0.7625), (0.12, 0.12, 0.002),
                         (0.86, 0.76, 0.46, 1.0))
    for i, (px, py, col) in enumerate(((tx - 0.20, ty + 0.14, (0.84, 0.24, 0.20, 1.0)), (tx + 0.04, ty - 0.06, (0.24, 0.40, 0.70, 1.0)),
                                       (tx - 0.02, ty + 0.20, (0.92, 0.80, 0.24, 1.0)))):
        make_cyl(f"Play_Piece_{i}", (px, py, 0.785), 0.022, 0.044, col, segments=8)
    for i, (px, py) in enumerate(((tx + 0.52, ty + 0.20), (tx + 0.62, ty - 0.18), (tx - 0.70, ty - 0.10))):
        for h in range(3):
            make_box(f"Play_Deck_{i}_{h}", (px + 0.003 * h, py, 0.757 + h * 0.008), (0.09, 0.13, 0.008),
                     ((0.80, 0.30, 0.26, 1.0), (0.30, 0.40, 0.66, 1.0), (0.94, 0.92, 0.86, 1.0))[i])
    for i, (px, py) in enumerate(((tx + 0.30, ty - 0.30), (tx + 0.36, ty - 0.24))):
        make_box(f"Play_Die_{i}", (px, py, 0.7655), (0.022, 0.022, 0.022), (0.96, 0.96, 0.94, 1.0))
    for i in range(6):
        make_rot_box(f"Play_Index_Card_{i}", (tx - 0.95 + 0.11 * (i % 3), ty + 0.30 - 0.14 * (i // 3), 0.7545),
                     (0.13, 0.08, 0.002), (0.97, 0.96, 0.90, 1.0), yaw=0.18 * (i - 2.5))
    make_rot_box("Play_Laptop_Base", (tx + 0.80, ty - 0.10, 0.763), (0.34, 0.24, 0.016), (0.62, 0.62, 0.64, 1.0), yaw=-0.25)
    make_rot_box("Play_Laptop_Lid", (tx + 0.80 + 0.03, ty - 0.10 + 0.115, 0.88), (0.34, 0.012, 0.23), (0.62, 0.62, 0.64, 1.0),
                 yaw=-0.25, roll=-0.22)
    make_mug("Play_Mug", tx + 0.25, ty + 0.36, 0.75, (0.92, 0.92, 0.90, 1.0))
    # the whiteboard between the W windows: a level drawn out in boxes and arrows
    make_box("Whiteboard", (OX0 + 0.12, OD / 2.0, 1.55), (0.02, 2.00, 1.10), (0.96, 0.96, 0.95, 1.0))
    make_box("Whiteboard_Frame", (OX0 + 0.11, OD / 2.0, 1.55), (0.02, 2.06, 1.16), (0.66, 0.66, 0.68, 1.0))
    make_box("Whiteboard_Tray", (OX0 + 0.16, OD / 2.0, 0.98), (0.06, 1.60, 0.02), (0.66, 0.66, 0.68, 1.0))
    for i, (v, z, sv, sz, col) in enumerate(((-0.62, 1.80, 0.42, 0.26, (0.20, 0.30, 0.60, 1.0)), (-0.05, 1.72, 0.36, 0.30, (0.20, 0.30, 0.60, 1.0)),
                                             (0.55, 1.84, 0.44, 0.20, (0.70, 0.20, 0.20, 1.0)), (-0.30, 1.30, 0.70, 0.010, (0.20, 0.20, 0.22, 1.0)),
                                             (0.40, 1.34, 0.50, 0.010, (0.20, 0.20, 0.22, 1.0)), (0.10, 1.22, 0.012, 0.36, (0.20, 0.50, 0.30, 1.0)))):
        make_box(f"Whiteboard_Mark_{i}", (OX0 + 0.132, OD / 2.0 + v, z), (0.002, sv, sz), col)
    for i, v in enumerate((-0.30, -0.20, 0.10)):
        make_box(f"Whiteboard_Marker_{i}", (OX0 + 0.16, OD / 2.0 + v, 1.0), (0.02, 0.11, 0.02), ((0.20, 0.30, 0.60, 1.0), (0.70, 0.20, 0.20, 1.0), (0.10, 0.10, 0.10, 1.0))[i])
    # the lounge by the front glass on the E side: a sofa against the wall,
    # a low table, a rug, an armchair turned toward them, a print above
    make_box("Lounge_Rug", (5.05, 2.35, 0.006), (3.10, 2.70, 0.012), (0.42, 0.46, 0.52, 1.0))
    make_sofa("Lounge_Sofa", OX1 - 0.10 - 0.46, 2.35, back="+X", w=2.10, d=0.88, seats=3, color=(0.30, 0.34, 0.40, 1.0),
              cushion_col=(0.34, 0.38, 0.44, 1.0), leg_col=(0.20, 0.20, 0.22, 1.0), arm="track",
              pillows=((0.86, 0.66, 0.30, 1.0), (0.84, 0.82, 0.76, 1.0)), z0=0.012)
    make_table("Lounge_Table", 5.05, 2.35, w=0.62, d=1.10, h=0.40, wood=(0.24, 0.24, 0.26, 1.0), top_col=(0.62, 0.48, 0.34, 1.0), z0=0.012)
    for h in range(3):
        make_box(f"Lounge_Magazine_{h}", (5.0 + 0.01 * h, 2.10, 0.415 + h * 0.006), (0.21, 0.28, 0.006),
                 ((0.80, 0.30, 0.26, 1.0), (0.24, 0.40, 0.66, 1.0), (0.94, 0.86, 0.40, 1.0))[h])
    make_sofa("Lounge_Armchair", 4.05, 1.25, back="-X", w=0.92, d=0.84, seats=1, color=(0.66, 0.46, 0.30, 1.0),
              leg_col=(0.20, 0.20, 0.22, 1.0), arm="track", z0=0.012)
    make_faded_poster("Lounge_Print", (OX1 - 0.10, 2.35, 1.70), axis='Y', into_room=-1, kind="movie")
    make_floor_plant("Lounge_Plant", (OX1 - 0.45, 4.40, 0.0), kind="monstera")
    # the coffee: a counter on the E wall with the machine and the cups
    cy = 6.0
    make_box("Coffee_Counter", (OX1 - 0.10 - 0.30, cy, 0.45), (0.60, 1.60, 0.90), (0.56, 0.56, 0.56, 1.0))
    make_box("Coffee_Counter_Top", (OX1 - 0.10 - 0.31, cy, 0.915), (0.62, 1.64, 0.03), (0.30, 0.30, 0.32, 1.0))
    make_box("Coffee_Machine", (OX1 - 0.10 - 0.25, cy - 0.3, 1.10), (0.30, 0.26, 0.34), (0.14, 0.14, 0.16, 1.0))
    make_cyl("Coffee_Pot", (OX1 - 0.10 - 0.36, cy - 0.3, 0.99), 0.07, 0.12, (0.30, 0.20, 0.14, 1.0), segments=12)
    for k in range(3):
        make_cyl(f"Coffee_Mug_{k}", (OX1 - 0.10 - 0.30, cy + 0.2 + k * 0.12, 0.98), 0.04, 0.10, (0.92, 0.92, 0.90, 1.0), segments=10)
    for k in range(2):
        make_box(f"Coffee_Cabinet_{k}", (OX1 - 0.10 - 0.17, cy - 0.4 + k * 0.8, 1.95), (0.34, 0.78, 0.70), (0.84, 0.84, 0.82, 1.0))
    # the game shelf by the back door: boxed games, rulebooks, a few binders
    sx, sy = OX1 - 0.10 - 0.18, 7.80
    make_box("Game_Shelf_Back", (OX1 - 0.115, sy, 0.95), (0.03, 1.20, 1.90), (0.80, 0.78, 0.72, 1.0))
    for s in (-1, 1):
        make_box(f"Game_Shelf_Side_{s:+d}", (sx, sy + s * 0.59, 0.95), (0.36, 0.02, 1.90), (0.80, 0.78, 0.72, 1.0))
    box_cols = ((0.80, 0.30, 0.26, 1.0), (0.24, 0.40, 0.66, 1.0), (0.94, 0.80, 0.30, 1.0), (0.30, 0.56, 0.36, 1.0), (0.46, 0.30, 0.56, 1.0),
                (0.90, 0.56, 0.24, 1.0), (0.20, 0.20, 0.22, 1.0))
    for r, z in enumerate((0.04, 0.50, 0.96, 1.42, 1.88)):
        make_box(f"Game_Shelf_Board_{r}", (sx, sy, z), (0.34, 1.16, 0.02), (0.80, 0.78, 0.72, 1.0))
        if r == 4:
            continue
        v = sy - 0.54
        i = 0
        while True:
            t = (0.06, 0.09, 0.05, 0.12, 0.07)[(i + r) % 5]
            h = (0.30, 0.36, 0.26, 0.40, 0.28)[(i * 3 + r) % 5]
            if v + t > sy + 0.54:
                break
            if r == 1 and i in (3, 4):            # a few boxes lying flat
                make_box(f"Game_Box_{r}_{i}", (sx, v + 0.16, z + 0.01 + 0.03 + 0.06 * (i - 3)), (0.30, 0.30, 0.06), box_cols[(i + r) % 7])
                v += 0.34
                i += 2
                continue
            make_box(f"Game_Box_{r}_{i}", (sx + 0.01, v + t / 2.0, z + 0.01 + h / 2.0), (0.30, t, h), box_cols[(i * 2 + r) % 7])
            v += t + 0.005
            i += 1
    # the door corner: a coat stand and a plant; a plant in the NW corner
    make_cyl("Coat_Stand_Pole", (OX0 + 0.45, 0.50, 0.90), 0.02, 1.80, (0.24, 0.24, 0.26, 1.0), segments=8)
    make_cyl("Coat_Stand_Foot", (OX0 + 0.45, 0.50, 0.02), 0.20, 0.04, (0.24, 0.24, 0.26, 1.0), segments=12)
    for k in range(4):
        a = k * math.pi / 2.0 + 0.4
        make_rot_box(f"Coat_Stand_Hook_{k}", (OX0 + 0.45 + 0.08 * math.cos(a), 0.50 + 0.08 * math.sin(a), 1.72), (0.16, 0.015, 0.015),
                     (0.24, 0.24, 0.26, 1.0), yaw=a, roll=0.5)
    make_rot_box("Coat_Stand_Jacket", (OX0 + 0.52, 0.47, 1.36), (0.26, 0.14, 0.62), (0.44, 0.30, 0.20, 1.0), yaw=0.3)
    make_floor_plant("Off_Plant_NW", (OX0 + 0.45, OD - 0.50, 0.0), kind="ficus")
    make_light_switch("Off_Switch", (DOOR_X + 0.75, 0.0), axis='X', face_sign=1)
    make_wall_outlet("Off_Outlet_Desks", (0.0, OD), axis='X', face_sign=-1)
    make_wall_outlet("Off_Outlet_Lounge", (OX1, 3.70), axis='Y', face_sign=-1)
    # the quiet street outside
    make_view("Off_Street_S", "S", -0.10, 0.0, kind="front", ground_z=0.0, seed=7)


# ── THE TUTORIAL (the imagined lobby) ─────────────────────────────────
LX0, LX1, LD, LH = 30.0, 44.0, 10.0, 4.2


def build_lobby():
    cx = (LX0 + LX1) / 2.0
    make_box("Lob_Floor", (cx, LD / 2.0, -0.01), (LX1 - LX0, LD, 0.02), (0.90, 0.90, 0.88, 1.0))
    make_box("Lob_Ceil", (cx, LD / 2.0, LH + 0.04), (LX1 - LX0, LD, 0.08), (0.96, 0.96, 0.94, 1.0))
    for nm, (x, y, sx, sy) in {"W": (LX0 - 0.1, LD / 2.0, 0.2, LD), "E": (LX1 + 0.1, LD / 2.0, 0.2, LD),
                               "N": (cx, LD + 0.1, LX1 - LX0, 0.2)}.items():
        make_box(f"Lob_Wall_{nm}", (x, y, LH / 2.0), (sx, sy, LH), WHITE)
    make_box("Lob_Wall_S_L", (LX0 + 2.5, -0.1, LH / 2.0), (5.0, 0.2, LH), WHITE)
    make_box("Lob_Wall_S_R", (LX1 - 3.5, -0.1, LH / 2.0), (7.0, 0.2, LH), WHITE)
    # the glass entry doors between them (x 35..37), shut: nobody walks in
    for k in range(2):
        make_box(f"Lob_Entry_Glass_{k}", (LX0 + 5.5 + k * 1.0, -0.1, 1.2), (0.96, 0.03, 2.4), (0.80, 0.86, 0.90, 1.0))
    make_box("Lob_Entry_Transom", (LX0 + 6.0, -0.1, 3.3), (2.0, 0.2, 1.8), WHITE)
    make_box("Lob_Entry_Mullion", (LX0 + 6.0, -0.1, 1.2), (0.04, 0.05, 2.4), (0.70, 0.72, 0.74, 1.0))
    # Olivia's console: a long curved-front reception desk, its monitor
    ox, oy = cx + 1.0, LD - 2.6
    for k in range(5):
        a = (k - 2) * 0.22
        make_rot_box(f"Console_Front_{k}", (ox + math.sin(a) * 1.6, oy - math.cos(a) * 0.30 - 0.30 + abs(k - 2) * 0.08, 0.55),
                     (0.72, 0.10, 1.10), (0.94, 0.94, 0.92, 1.0), yaw=a)
    make_box("Console_Top", (ox, oy - 0.10, 1.12), (3.4, 0.70, 0.04), (0.86, 0.86, 0.84, 1.0))
    make_box("Console_Desk", (ox, oy + 0.20, 0.735), (3.0, 0.60, 0.03), (0.86, 0.86, 0.84, 1.0))
    make_box("Console_Body", (ox, oy + 0.20, 0.36), (2.9, 0.50, 0.72), (0.92, 0.92, 0.90, 1.0))
    flat_monitor("Console_Monitor", ox - 0.3, oy + 0.30, 0.75, face="+Y", w=0.50)
    make_box("Console_Keyboard", (ox - 0.3, oy + 0.55, 0.759), (0.44, 0.15, 0.018), (0.86, 0.86, 0.86, 1.0))
    make_chair("Console_Chair", ox - 0.3, oy + 1.10, yaw=0.0, wood=(0.80, 0.80, 0.80, 1.0), seat_col=(0.70, 0.72, 0.76, 1.0))
    # the television on the W wall and the seating group facing it
    tx, ty = LX0 + 0.04, 4.6
    make_box("Lob_TV", (tx, ty, 1.75), (0.08, 1.90, 1.10), FLAT)
    make_box("Lob_TV_Screen", (tx + 0.042, ty, 1.75), (0.004, 1.80, 1.00), (0.52, 0.62, 0.70, 1.0))
    make_box("Lob_Sofa_Base", (LX0 + 4.2, ty, 0.22), (0.90, 2.40, 0.44), (0.80, 0.80, 0.82, 1.0))
    make_box("Lob_Sofa_Back", (LX0 + 4.55, ty, 0.70), (0.20, 2.40, 0.56), (0.80, 0.80, 0.82, 1.0))
    for s in (-1, 1):
        make_box(f"Lob_Sofa_Arm_{s:+d}", (LX0 + 4.2, ty + s * 1.11, 0.55), (0.90, 0.18, 0.24), (0.80, 0.80, 0.82, 1.0))
        make_chair(f"Lob_Chair_{s:+d}", LX0 + 3.0, ty + s * 2.0, yaw=math.pi / 2.0 + s * 0.4, wood=(0.80, 0.80, 0.80, 1.0),
                   seat_col=(0.76, 0.76, 0.80, 1.0))
    make_box("Lob_Table", (LX0 + 2.8, ty, 0.20), (0.70, 1.20, 0.40), (0.86, 0.86, 0.84, 1.0))
    for k in range(4):
        make_box(f"Lob_Light_{k}", (LX0 + 2.5 + k * 3.0, LD / 2.0, LH - 0.01), (2.0, 0.40, 0.02), (1.0, 1.0, 0.98, 1.0))


# ── THE CLUB OFFICE ──────────────────────────────────────────────────
CX0, CX1, CD, CH = 60.0, 68.0, 6.0, 3.0
CLUB_DOOR_X = 62.0


def build_club_office():
    cx = (CX0 + CX1) / 2.0
    make_floor("Club_Off_Floor", (cx, CD / 2.0, 0.0), size_x=CX1 - CX0 + 0.4, size_y=CD + 0.4,
               palette={"vinyl": (0.22, 0.18, 0.20, 1.0), "seam": (0.18, 0.14, 0.16, 1.0)})
    make_box("Club_Off_Ceil", (cx, CD / 2.0, CH + 0.04), (CX1 - CX0 + 0.4, CD + 0.4, 0.08), (0.12, 0.10, 0.14, 1.0))
    pal = {"wall": CLUB_WALL, "baseboard": (0.06, 0.06, 0.08, 1.0)}
    make_wall("Club_Off_Wall_W", (CX0, CD / 2.0, 0), length=CD + 0.4, height=CH, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("Club_Off_Wall_E", (CX1, CD / 2.0, 0), length=CD + 0.4, height=CH, thickness=0.2, axis='Y', palette=pal, baseboard_face_sign=-1)
    make_wall("Club_Off_Wall_N", (cx, CD, 0), length=CX1 - CX0 + 0.4, height=CH, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall_with_openings("Club_Off_Wall_S", (cx, 0.0, 0), length=CX1 - CX0 + 0.4, height=CH, thickness=0.2, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(CLUB_DOOR_X, 1.05, 1.0, 2.1)])
    # the door stands open into the office; the club beyond it: its dark
    # floor, the # in pink neon on the far wall, the bars of the cage
    make_box("Club_Off_Door", (CLUB_DOOR_X - 0.48, 0.10 + 0.48, 1.05), (0.04, 0.96, 2.08), (0.10, 0.10, 0.12, 1.0))
    make_box("Club_Beyond_Floor", (CLUB_DOOR_X, -4.0, 0.0), (10.0, 8.0, 0.02), (0.08, 0.08, 0.10, 1.0))
    make_box("Club_Beyond_Wall", (CLUB_DOOR_X, -8.1, 2.5), (10.0, 0.2, 5.0), (0.10, 0.08, 0.12, 1.0))
    for i, dx in enumerate((-0.35, 0.35)):
        make_rot_box(f"Club_Beyond_Hash_V_{i}", (CLUB_DOOR_X + 0.6 + dx, -7.97, 2.6), (0.10, 0.04, 1.6), NEON_PINK, pitch=0.18)
    for i, dz in enumerate((-0.32, 0.32)):
        make_box(f"Club_Beyond_Hash_H_{i}", (CLUB_DOOR_X + 0.6, -7.97, 2.6 + dz), (1.4, 0.04, 0.10), NEON_PINK)
    make_box("Club_Beyond_Cage_Base", (CLUB_DOOR_X - 1.4, -4.6, 0.05), (1.6, 1.6, 0.10), (0.30, 0.30, 0.32, 1.0))
    make_box("Club_Beyond_Cage_Top", (CLUB_DOOR_X - 1.4, -4.6, 2.35), (1.6, 1.6, 0.06), (0.30, 0.30, 0.32, 1.0))
    for k in range(8):
        a = k * math.pi / 4.0
        make_cyl(f"Club_Beyond_Cage_Bar_{k}", (CLUB_DOOR_X - 1.4 + 0.76 * math.cos(a), -4.6 + 0.76 * math.sin(a), 1.21), 0.015, 2.22,
                 (0.56, 0.56, 0.58, 1.0), segments=6)
    # the table in the middle: the three shirts laid out, the four
    # listening devices, the needle devices on a tray
    tx, ty = cx, 3.0
    make_box("Brief_Table_Top", (tx, ty, 0.745), (2.40, 1.00, 0.05), (0.20, 0.18, 0.20, 1.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_box(f"Brief_Table_Leg_{sx:+d}_{sy:+d}", (tx + sx * 1.10, ty + sy * 0.42, 0.36), (0.05, 0.05, 0.72), (0.40, 0.40, 0.42, 1.0))
    shirts = [((0.16, 0.16, 0.18, 1.0), (0.86, 0.40, 0.20, 1.0)), ((0.84, 0.84, 0.82, 1.0), (0.24, 0.40, 0.78, 1.0)),
              ((0.40, 0.12, 0.16, 1.0), (0.90, 0.84, 0.36, 1.0))]
    for k, (body, art) in enumerate(shirts):
        x = tx - 0.75 + k * 0.75
        make_box(f"Shirt_{k}_Body", (x, ty - 0.05, 0.775), (0.42, 0.56, 0.01), body)
        for s in (-1, 1):
            make_rot_box(f"Shirt_{k}_Sleeve_{s:+d}", (x + s * 0.27, ty + 0.12, 0.775), (0.16, 0.20, 0.01), body, yaw=s * 0.5)
        make_box(f"Shirt_{k}_Art", (x, ty - 0.02, 0.7805), (0.24, 0.26, 0.001), art)
        make_box(f"Shirt_{k}_Art_Mark", (x + (k - 1) * 0.04, ty + 0.0, 0.781), (0.10 + k * 0.03, 0.08, 0.001),
                 (art[0] * 0.5, art[1] * 0.5, art[2] * 0.5, 1.0))
    for k in range(4):
        x = tx - 0.90 + k * 0.60
        make_chamfer_box(f"Listener_{k}", (x, ty + 0.36, 0.785), (0.07, 0.11, 0.03), (0.08, 0.08, 0.09, 1.0), chamfer=0.008)
        make_tube(f"Listener_{k}_Earpiece", [(x, ty + 0.30, 0.78), (x + 0.05, ty + 0.26, 0.775), (x + 0.08, ty + 0.30, 0.775)],
                  0.004, (0.20, 0.20, 0.22, 1.0))
    # (2026-10-29) a pendant over the briefing table — the room had no light
    # but Dean's desk lamp, and rendered black (club_office.tscn now hangs
    # practicals on this, the lamp, and the neon through the door)
    make_cyl("Club_Off_Pendant_Cord", (tx, ty, CH - 0.35), 0.006, 0.70, (0.08, 0.08, 0.08, 1.0), segments=6)
    make_cyl("Club_Off_Pendant_Shade", (tx, ty, CH - 0.78), 0.22, 0.16, (0.12, 0.10, 0.12, 1.0), segments=14)
    make_cyl("Club_Off_Pendant_Bulb", (tx, ty, CH - 0.87), 0.05, 0.04, (1.0, 0.92, 0.74, 1.0), segments=10)
    make_box("Needle_Tray", (tx + 0.95, ty - 0.30, 0.775), (0.30, 0.20, 0.01), (0.80, 0.82, 0.84, 1.0))
    for k in range(3):
        make_cyl(f"Needle_{k}", (tx + 0.88 + k * 0.07, ty - 0.30, 0.79), 0.008, 0.10, (0.86, 0.88, 0.92, 1.0), axis='Y', segments=8)
    # Dean's desk on the N wall, his lamp and chair; a chair at the table (Faust's)
    desk("Dean_Club_Desk", cx + 1.6, CD - 0.10 - 0.40, w=1.6, d=0.80, col=(0.16, 0.12, 0.12, 1.0))
    make_lamp("Lamp_Desk_Club", cx + 2.2, CD - 0.10 - 0.36, base_z=0.75, h=0.42)
    make_chair("Dean_Club_Chair", cx + 1.5, CD - 1.10, yaw=0.0, wood=(0.10, 0.10, 0.10, 1.0), seat_col=(0.30, 0.10, 0.14, 1.0))
    make_chair("Faust_Chair", tx - 0.70, ty - 1.00, yaw=math.pi + 0.3, wood=(0.10, 0.10, 0.10, 1.0), seat_col=(0.30, 0.10, 0.14, 1.0))
    # the couch on the E wall, and young Aria on it at rest under a sheet
    kx, ky = CX1 - 0.10 - 0.45, 2.6
    make_box("Club_Couch_Base", (kx, ky, 0.22), (0.90, 2.20, 0.44), (0.44, 0.14, 0.20, 1.0))
    make_box("Club_Couch_Back", (kx + 0.36, ky, 0.70), (0.18, 2.20, 0.56), (0.44, 0.14, 0.20, 1.0))
    for s in (-1, 1):
        make_box(f"Club_Couch_Arm_{s:+d}", (kx, ky + s * 1.02, 0.56), (0.90, 0.16, 0.24), (0.44, 0.14, 0.20, 1.0))
    make_chamfer_box("Aria_Sheet", (kx - 0.05, ky - 0.05, 0.53), (0.56, 1.66, 0.18), (0.92, 0.92, 0.90, 1.0), chamfer=0.06)
    make_blob("Aria_Sheet_Head", (kx - 0.05, ky + 0.82, 0.58), 0.13, (0.92, 0.92, 0.90, 1.0), noise=0.04, seed=3, squash=0.8)
    make_box("Aria_Sheet_Fall", (kx - 0.38, ky - 0.05, 0.38), (0.02, 1.60, 0.34), (0.90, 0.90, 0.88, 1.0))


# ── THE MONITOR ROOM (the glass house) ────────────────────────────────
MX0, MX1, MD, MH = 100.0, 107.0, 6.4, 3.2
RING_C = (104.0, 3.2)


def build_monitor_room():
    cx = (MX0 + MX1) / 2.0
    make_floor("Mon_Floor", (cx, MD / 2.0, 0.0), size_x=MX1 - MX0 + 0.4, size_y=MD + 0.4,
               palette={"vinyl": (0.52, 0.38, 0.26, 1.0), "seam": (0.44, 0.32, 0.22, 1.0)}, style="plank")
    make_box("Mon_Ceil", (cx, MD / 2.0, MH + 0.04), (MX1 - MX0 + 0.4, MD + 0.4, 0.08), (0.80, 0.76, 0.70, 1.0))
    pal = {"wall": (0.76, 0.70, 0.62, 1.0), "baseboard": WOOD_DARK}
    make_wall("Mon_Wall_N", (cx, MD, 0), length=MX1 - MX0 + 0.4, height=MH, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=-1)
    make_wall("Mon_Wall_S", (cx, 0.0, 0), length=MX1 - MX0 + 0.4, height=MH, thickness=0.2, axis='X', palette=pal, baseboard_face_sign=+1)
    make_wall_with_openings("Mon_Wall_E", (MX1, MD / 2.0, 0), length=MD + 0.4, height=MH, thickness=0.2, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(RING_C[1], 1.0, 0.90, 2.0)])
    make_box("Mon_Hall_Dark", (MX1 + 1.2, RING_C[1], 1.0), (0.1, 1.6, 2.0), (0.06, 0.05, 0.05, 1.0))
    # the W wall is glass on the Pacific: mullions, the black water, a far line of sky
    make_box("Mon_Glass", (MX0, MD / 2.0, MH / 2.0), (0.03, MD, MH), (0.12, 0.16, 0.22, 1.0))
    for k in range(5):
        make_box(f"Mon_Glass_Mullion_{k}", (MX0 + 0.02, 0.2 + k * 1.5, MH / 2.0), (0.06, 0.06, MH), (0.20, 0.18, 0.16, 1.0))
    # (kept between the club office, x < 68, and the glass)
    make_box("Ocean", (86.0, MD / 2.0, -6.0), (28.0, 60.0, 0.1), (0.03, 0.05, 0.08, 1.0))
    make_box("Ocean_Horizon", (72.0, MD / 2.0, 4.0), (0.2, 60.0, 20.0), (0.06, 0.08, 0.14, 1.0))
    # the ring of monitors on desk segments round an open centre, open to the door
    rx, ry = RING_C
    R = 1.35
    n = 9
    for k in range(n):
        a = math.pi * (0.20 + 1.60 * k / (n - 1))      # from NE round by W to SE; the E is open
        a = a + math.pi / 2.0
        x, y = rx + R * math.cos(a), ry + R * math.sin(a)
        yaw = a + math.pi / 2.0
        make_rot_box(f"Ring_Desk_{k}", (x + 0.12 * math.cos(a), y + 0.12 * math.sin(a), 0.735), (0.66, 0.52, 0.03), WOOD, yaw=yaw)
        make_rot_box(f"Ring_Desk_{k}_Panel", (x + 0.36 * math.cos(a), y + 0.36 * math.sin(a), 0.36), (0.62, 0.04, 0.72), WOOD_DARK, yaw=yaw)
        for t, z in enumerate((0.75, 1.20)):
            if t == 1 and k % 2:
                continue
            mx, my = x + 0.20 * math.cos(a), y + 0.20 * math.sin(a)
            make_rot_box(f"Ring_Mon_{k}_{t}_Body", (mx, my, z + 0.24), (0.52, 0.04, 0.32), FLAT, yaw=yaw)
            glow = (0.20, 0.60, 0.30, 1.0) if (k == 4 and t == 0) else ((0.30, 0.42, 0.62, 1.0), (0.46, 0.36, 0.60, 1.0), (0.26, 0.50, 0.56, 1.0))[(k + t) % 3]
            make_rot_box(f"Ring_Mon_{k}_{t}_Screen", (mx - 0.022 * math.cos(a), my - 0.022 * math.sin(a), z + 0.24), (0.48, 0.004, 0.28),
                         glow, yaw=yaw)
            if t == 0:
                make_rot_box(f"Ring_Mon_{k}_{t}_Stand", (mx + 0.02 * math.cos(a), my + 0.02 * math.sin(a), z + 0.04), (0.06, 0.04, 0.08), FLAT, yaw=yaw)
            else:
                make_rot_box(f"Ring_Mon_{k}_{t}_Arm", (mx + 0.04 * math.cos(a), my + 0.04 * math.sin(a), z - 0.13), (0.05, 0.05, 0.48), FLAT, yaw=yaw)
    # the nearest monitor (k 4, due W): the text game, its lines and cursor
    a = math.pi * (0.20 + 1.60 * 4 / (n - 1)) + math.pi / 2.0
    mx, my = rx + (R + 0.20) * math.cos(a) - 0.026 * math.cos(a), ry + (R + 0.20) * math.sin(a) - 0.026 * math.sin(a)
    for j in range(5):
        make_rot_box(f"Text_Game_Line_{j}", (mx, my, 1.08 - j * 0.045), (0.30 - (j % 2) * 0.10, 0.002, 0.012), (0.70, 1.0, 0.70, 1.0),
                     yaw=a + math.pi / 2.0)
    make_rot_box("Text_Game_Cursor", (mx, my + 0.0, 0.85), (0.02, 0.002, 0.024), (0.86, 1.0, 0.86, 1.0), yaw=a + math.pi / 2.0)
    # the desk with the drawer where the goggles live (the S segment's drawer front)
    make_box("Goggle_Desk", (MX1 - 1.2, 0.10 + 0.40, 0.735), (1.20, 0.70, 0.03), WOOD)
    make_box("Goggle_Desk_Body", (MX1 - 1.2, 0.10 + 0.40, 0.36), (1.16, 0.66, 0.72), WOOD_DARK)
    make_box("Goggle_Desk_Drawer", (MX1 - 1.2, 0.10 + 0.736, 0.58), (0.50, 0.012, 0.14), WOOD)
    make_box("Goggle_Desk_Drawer_Pull", (MX1 - 1.2, 0.10 + 0.746, 0.58), (0.12, 0.012, 0.02), (0.70, 0.62, 0.40, 1.0))
    # his art and music: an easel by the glass, a keyboard on a stand, a tablet
    make_rot_box("Easel_Leg_L", (MX0 + 0.8, MD - 1.0, 0.85), (0.04, 0.04, 1.72), WOOD, roll=0.12)
    make_rot_box("Easel_Leg_R", (MX0 + 1.3, MD - 1.0, 0.85), (0.04, 0.04, 1.72), WOOD, roll=0.12)
    make_box("Easel_Canvas", (MX0 + 1.05, MD - 1.08, 1.25), (0.70, 0.03, 0.60), (0.86, 0.60, 0.40, 1.0))
    make_box("Easel_Ledge", (MX0 + 1.05, MD - 1.10, 0.92), (0.80, 0.08, 0.03), WOOD)
    make_box("Synth_Stand", (MX1 - 1.0, MD - 0.50, 0.40), (1.10, 0.06, 0.80), (0.20, 0.20, 0.22, 1.0))
    make_box("Synth", (MX1 - 1.0, MD - 0.50, 0.84), (1.20, 0.34, 0.08), (0.14, 0.14, 0.16, 1.0))
    make_box("Synth_Keys", (MX1 - 1.0, MD - 0.62, 0.884), (1.04, 0.10, 0.008), (0.94, 0.94, 0.92, 1.0))
    make_box("Rug_Mon", (rx, ry, 0.006), (2.4, 2.4, 0.012), (0.40, 0.30, 0.34, 1.0))


# ── THE TOWER CORRIDOR ────────────────────────────────────────────────
TX0, TX1, TL, TH = 140.0, 146.0, 30.0, 3.4


def build_tower():
    cx = (TX0 + TX1) / 2.0
    make_box("Tow_Floor", (cx, TL / 2.0, -0.01), (TX1 - TX0, TL, 0.02), (0.34, 0.34, 0.36, 1.0))
    make_box("Tow_Floor_Runner", (cx - 0.6, TL / 2.0, 0.003), (1.6, TL - 1.0, 0.006), (0.28, 0.26, 0.30, 1.0))
    make_box("Tow_Ceil", (cx, TL / 2.0, TH + 0.04), (TX1 - TX0, TL, 0.08), (0.30, 0.30, 0.32, 1.0))
    make_box("Tow_Wall_W", (TX0 - 0.1, TL / 2.0, TH / 2.0), (0.2, TL, TH), (0.62, 0.62, 0.64, 1.0))
    make_box("Tow_End_S", (cx, -0.1, TH / 2.0), (TX1 - TX0, 0.2, TH), (0.36, 0.36, 0.38, 1.0))
    make_box("Tow_End_N", (cx, TL + 0.1, TH / 2.0), (TX1 - TX0, 0.2, TH), (0.34, 0.34, 0.36, 1.0))
    # the door at the end, shut; the light under it
    make_box("Tow_Door", (cx - 0.6, TL - 0.02, 1.1), (1.0, 0.05, 2.2), (0.16, 0.14, 0.14, 1.0))
    make_box("Tow_Door_Frame", (cx - 0.6, TL - 0.01, 1.14), (1.14, 0.02, 2.30), (0.50, 0.50, 0.52, 1.0))
    make_box("Tow_Door_Handle", (cx - 0.2, TL - 0.06, 1.05), (0.03, 0.04, 0.24), (0.76, 0.74, 0.70, 1.0))
    make_box("Tow_Door_Gap", (cx - 0.6, TL - 0.03, 0.006), (0.98, 0.012, 0.012), (1.0, 0.96, 0.86, 1.0))
    # offices along the W wall: doors shut
    for k in range(4):
        make_box(f"Tow_Office_Door_{k}", (TX0 + 0.02, 4.0 + k * 6.0, 1.1), (0.04, 1.0, 2.2), (0.26, 0.24, 0.24, 1.0))
    # (round 3) "These are the things you probably shouldn't see": each office
    # door's wired-glass sidelight lit from inside, the blue of screens left
    # on, one door ajar on a room of them (the tscn's Office_Screens_*)
    for k in range(4):
        dy = 4.0 + k * 6.0
        make_box(f"Tow_Office_Sidelight_Frame_{k}", (TX0 + 0.03, dy + 0.80, 1.25), (0.05, 0.40, 1.90), (0.30, 0.30, 0.32, 1.0))
        make_box(f"Tow_Office_Sidelight_Glow_{k}", (TX0 + 0.06, dy + 0.80, 1.25), (0.01, 0.30, 1.78), (0.40, 0.58, 0.86, 1.0))
        for g in range(5):
            make_box(f"Tow_Office_Sidelight_Wire_{k}_{g}", (TX0 + 0.067, dy + 0.80, 0.50 + g * 0.36), (0.003, 0.30, 0.006), (0.20, 0.22, 0.26, 1.0))
    for k in range(10):
        make_cyl(f"Tow_Downlight_{k}", (cx - 0.6, 1.5 + k * 3.0, TH - 0.01), 0.08, 0.02, (0.96, 0.96, 0.94, 1.0), segments=10)
    # the E side: floor-to-ceiling glass, the city at night below and beyond
    # (no pane: our materials are opaque, so the glass is its frame — a sill,
    # a head and the mullions — and the city shows through)
    make_box("Tow_Glass_Sill", (TX1, TL / 2.0, 0.05), (0.12, TL, 0.10), (0.24, 0.24, 0.26, 1.0))
    make_box("Tow_Glass_Head", (TX1, TL / 2.0, TH - 0.05), (0.12, TL, 0.10), (0.24, 0.24, 0.26, 1.0))
    for k in range(11):
        make_box(f"Tow_Glass_Mullion_{k}", (TX1, k * 3.0, TH / 2.0), (0.05, 0.08, TH - 0.20), (0.24, 0.24, 0.26, 1.0))
    make_box("City_Ground", (TX1 + 120.0, TL / 2.0, -80.0), (220.0, 300.0, 0.2), (0.04, 0.04, 0.06, 1.0))
    for k in range(22):
        bx = TX1 + 30.0 + (k * 37 % 9) * 14.0
        by = -60.0 + k * 7.5
        h = 60.0 + (k * 53 % 7) * 22.0
        w = 10.0 + (k % 3) * 4.0
        make_box(f"City_Stock_Tower_{k}", (bx, by, -80.0 + h / 2.0), (w, w, h), (0.08, 0.08, 0.12, 1.0))
        for j in range(int(h / 9.0)):
            for i in range(3):
                if (k + j * 3 + i) % 4 == 0:
                    continue
                make_box(f"City_Stock_Win_{k}_{j}_{i}", (bx - w / 2.0 - 0.05, by - w / 3.0 + i * w / 3.0, -80.0 + 4.0 + j * 9.0),
                         (0.1, w / 4.5, 2.4), ((0.98, 0.84, 0.50, 1.0), (0.80, 0.90, 1.0, 1.0))[(k + j) % 2])


def main():
    clear_scene()
    build_office()
    build_lobby()
    build_club_office()
    build_monitor_room()
    build_tower()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/dean_offices.glb"))
    print(f"\n[build_dean_offices] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
