"""vol4_story_rooms — the single rooms of vol 4's stories and "daddy" (draft
1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Undated (pre-2012; Knot 6 is the author's): nothing later than a CRT, a
PDA, a phone in a car.
  paper cuts: "The parking garage is the color of honeydew."; "The
   fluorescent lighting plays against the concrete hardtop interior."; "the
   far off car descending"; "The headlights catching me"
                                          → garage_level (x 0..40)
  map of the city: "a clothing store", "empty except for naked mannequins and
   sale banners slumped and covered thick with dust"; "He hops up on a
   counter, the glass crunching in the recess"; "the metal spine of the dead
   escalator"; outside, the sun high      → dead_store (x 120..150)
  cracked and broken: "Reflections in the mirror. What she glanced back at,
   not herself, but the world behind her."; "One side in bright, the other
   in black". The text never says bathroom: an ordinary washroom. Our
   materials are opaque, so the mirror is an opening onto a mirrored copy
   of the room behind it.                 → mirror_room (x 260..)
  heavy breathing: Aaron "still played with his toys when he was thirteen";
   "One of those early nintendo systems"; "magazines, strategies and comic
   books"; the waking dream: "soft melodies and blue lighting filled his
   bedroom"                               → aaron_bedroom, aaron_bedroom_blue
  the wasted sentiment: Steven's room is in the Chau house (the user,
   2026-10-18): chau_house's `chau_steven_room`, not here
  daddy: "This is too easy, don't you think, Esther asked him one late
   night."; "Just reading a bit longer, okay?" (a comfortable family house,
   no city named)                          → dean_house_late
   Shanghai: "his one-room apartment"; "She wanders from window to window";
   "The city lights go on below without end, every window someone else's."
                                          → shanghai_window_night (the room at
                                            z 0, the city below at z -60)
Blender: x east, y north, z up; Godot (x, z, -y). The areas stand far
enough apart that no window sees another inside the 200 m far plane.

DRAFT 2 targets: the store's roof and its broken pink sky; the garage's
upper level and the car on the ramp; the mirror room's woman's mark;
Shanghai sharing dean_offices' night city; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_table, make_lamp

T = 0.18
CONC = (0.58, 0.58, 0.56, 1.0); HONEYDEW = (0.72, 0.84, 0.62, 1.0)
TRIM = (0.88, 0.86, 0.80, 1.0)


def frame(name, axis, along, at, cz, w, h, depth=T):
    for s in (-1, 1):
        if axis == 'X':
            make_box(f"{name}_Frame_Jamb_{s:+d}", (along + s * (w / 2.0 - 0.03), at, cz), (0.06, depth + 0.02, h), TRIM)
        else:
            make_box(f"{name}_Frame_Jamb_{s:+d}", (at, along + s * (w / 2.0 - 0.03), cz), (depth + 0.02, 0.06, h), TRIM)
    for zz in (cz - h / 2.0 + 0.03, cz + h / 2.0 - 0.03):
        if axis == 'X':
            make_box(f"{name}_Frame_Rail_{zz:.2f}", (along, at, zz), (w - 0.12, depth + 0.02, 0.06), TRIM)
        else:
            make_box(f"{name}_Frame_Rail_{zz:.2f}", (at, along, zz), (depth + 0.02, w - 0.12, 0.06), TRIM)


def car(prefix, x, y, yaw, col):
    c, s = math.cos(yaw), math.sin(yaw)
    make_chamfer_box(f"{prefix}_Body", (x, y, 0.62), (1.8, 4.4, 0.70), col, chamfer=0.16, yaw=yaw)
    make_chamfer_box(f"{prefix}_Cabin", (x - 0.2 * s, y + 0.2 * c * 0 - 0.2 * c, 1.16), (1.6, 2.2, 0.44), (0.18, 0.20, 0.22, 1.0), chamfer=0.10, yaw=yaw)
    for i in (-1, 1):
        for j in (-1, 1):
            u, v = i * 0.80, j * 1.40
            make_cyl(f"{prefix}_Wheel_{i:+d}{j:+d}", (x + u * c - v * s, y + u * s + v * c, 0.32), 0.32, 0.22, (0.10, 0.10, 0.10, 1.0),
                     axis='X' if abs(c) > 0.5 else 'Y', segments=12)


def build_garage():
    """x 0..40, y 0..24: one level, columns on a 8 m grid, the bays, the
    down-ramp from the level above along the E side."""
    H = 2.5
    make_box("Garage_Floor_Slab", (20.0, 12.0, -0.10), (40.0, 24.0, 0.20), CONC)
    make_box("Garage_Ceil_Slab", (20.0, 12.0, H + 0.15), (40.0, 24.0, 0.30), (0.62, 0.62, 0.60, 1.0))
    for nm, c, sz in (("Garage_Wall_S", (20.0, 0.0, H / 2.0), (40.4, 0.30, H)), ("Garage_Wall_N", (20.0, 24.0, H / 2.0), (40.4, 0.30, H)),
                      ("Garage_Wall_W", (0.0, 12.0, H / 2.0), (0.30, 24.0, H))):
        make_box(nm, c, sz, CONC)
    make_box("Garage_Wall_E_S", (40.0, 5.0, H / 2.0), (0.30, 10.0, H), CONC)
    make_box("Garage_Wall_E_N", (40.0, 21.0, H / 2.0), (0.30, 6.0, H), CONC)
    # the honeydew band round the walls, on every column
    for nm, c, sz in (("Honeydew_Band_S", (20.0, 0.16, 0.90), (40.0, 0.02, 1.0)), ("Honeydew_Band_N", (20.0, 23.84, 0.90), (40.0, 0.02, 1.0)),
                      ("Honeydew_Band_W", (0.16, 12.0, 0.90), (0.02, 23.6, 1.0))):
        make_box(nm, c, sz, HONEYDEW)
    for i in range(1, 5):
        for j in range(1, 3):
            x, y = i * 8.0, j * 8.0
            make_box(f"Garage_Column_{i}_{j}", (x, y, H / 2.0), (0.50, 0.50, H), CONC)
            make_box(f"Garage_Column_Band_{i}_{j}", (x, y, 0.90), (0.54, 0.54, 1.0), HONEYDEW)
    # the fluorescent tubes in rows, the bay stripes, the cars
    for i in range(5):
        for j in range(3):
            make_box(f"Garage_Tube_Glow_{i}_{j}", (4.0 + i * 8.0, 4.0 + j * 8.0, H - 0.04), (1.2, 0.12, 0.06), (0.92, 0.98, 0.92, 1.0))
    for k in range(16):
        make_box(f"Bay_Stripe_Stock_S_{k}", (1.5 + k * 2.5, 2.8, 0.003), (0.10, 5.0, 0.006), (0.90, 0.90, 0.86, 1.0))
        make_box(f"Bay_Stripe_Stock_N_{k}", (1.5 + k * 2.5, 21.2, 0.003), (0.10, 5.0, 0.006), (0.90, 0.90, 0.86, 1.0))
    for k, (x, y, col) in enumerate(((2.75, 3.0, (0.40, 0.42, 0.46, 1.0)), (10.25, 3.0, (0.60, 0.20, 0.18, 1.0)),
                                     (17.75, 21.0, (0.82, 0.82, 0.80, 1.0)), (27.75, 21.0, (0.20, 0.24, 0.30, 1.0)),
                                     (30.25, 3.0, (0.30, 0.30, 0.30, 1.0)))):
        car(f"Parked_Car_{k}", x, y, 0.0, col)
    # the down-ramp from above, in along the E side (x 40..46, y 10..18)
    make_rot_box("Ramp_Down_Slab", (44.0, 14.0, H / 2.0 - 0.1), (6.0, 8.6, 0.30), CONC, roll=math.atan2(H, 8.0))
    make_box("Ramp_Wall_E", (47.0, 14.0, H / 2.0 + 0.6), (0.30, 9.0, H + 1.2), CONC)
    make_box("Ramp_Wall_Honeydew_Band", (46.84, 14.0, 0.90), (0.02, 8.6, 1.0), HONEYDEW)
    make_box("Ramp_Upper_Ceil", (44.0, 14.0, H + 1.3), (6.4, 9.0, 0.30), (0.62, 0.62, 0.60, 1.0))
    make_box("Ramp_Upper_Wall_N", (43.5, 18.4, (H + 1.2) / 2.0), (7.0, 0.30, H + 1.2), CONC)
    make_box("Ramp_Upper_Wall_S", (43.5, 9.6, (H + 1.2) / 2.0), (7.0, 0.30, H + 1.2), CONC)
    make_box("Exit_Sign_Mounted_Glow", (39.8, 9.0, 2.1), (0.06, 0.40, 0.16), (0.30, 0.86, 0.40, 1.0))


def build_store():
    """x 120..150, y 0..24: two floors, the mezzanine at z 4.5 over the back
    half; the escalator up; the counter; mannequins; banners; the street S."""
    H, Z2 = 9.0, 4.5
    x0, x1, y0, y1 = 120.0, 150.0, 0.0, 24.0
    make_box("Store_Floor_Slab", (135.0, 12.0, -0.10), (30.0, 24.0, 0.20), (0.62, 0.60, 0.56, 1.0))
    make_box("Store_Roof_Slab", (135.0, 12.0, H + 0.15), (30.4, 24.4, 0.30), (0.40, 0.40, 0.40, 1.0))
    make_box("Store_Wall_N", (135.0, y1, H / 2.0), (30.4, 0.30, H), (0.70, 0.66, 0.60, 1.0))
    make_box("Store_Wall_W", (x0, 12.0, H / 2.0), (0.30, 24.0, H), (0.70, 0.66, 0.60, 1.0))
    make_box("Store_Wall_E", (x1, 12.0, H / 2.0), (0.30, 24.0, H), (0.70, 0.66, 0.60, 1.0))
    # the S front: three tall windows (frames, the glass long gone), the door
    for k, x in enumerate((122.5, 127.5, 132.5, 137.5, 142.5, 147.5)):
        if k in (1, 4):
            make_box(f"Store_Front_Pier_{k}", (x, y0, H / 2.0), (5.0, 0.30, H), (0.66, 0.62, 0.56, 1.0))
            continue
        make_box(f"Store_Front_Sill_{k}", (x, y0, 0.25), (5.0, 0.30, 0.50), (0.66, 0.62, 0.56, 1.0))
        make_box(f"Store_Front_Head_{k}", (x, y0, (3.6 + H) / 2.0), (5.0, 0.30, H - 3.6), (0.66, 0.62, 0.56, 1.0))
        frame(f"Store_Front_Window_{k}", 'X', x, y0, 2.05, 5.0, 3.1, depth=0.30)
    # the mezzanine (the back half, y 12..24) and its rail
    # cut round the escalator's head (x 133.2..134.8)
    mz = (0.62, 0.60, 0.56, 1.0)
    make_box("Mezzanine_Floor_Slab_W", (126.7, 18.0, Z2 - 0.15), (13.0, 12.0, 0.30), mz)
    make_box("Mezzanine_Floor_Slab_E", (142.3, 18.0, Z2 - 0.15), (15.0, 12.0, 0.30), mz)
    make_box("Mezzanine_Floor_Slab_Head", (134.0, 18.45, Z2 - 0.15), (1.6, 11.1, 0.30), mz)
    make_box("Mezzanine_Rail_W", (126.7, 12.05, Z2 + 0.50), (13.0, 0.06, 0.06), (0.60, 0.60, 0.62, 1.0))
    make_box("Mezzanine_Rail_E", (142.3, 12.05, Z2 + 0.50), (15.0, 0.06, 0.06), (0.60, 0.60, 0.62, 1.0))
    for k in range(15):
        if 132.9 < 121.0 + k * 2.0 < 135.1:
            continue
        make_box(f"Mezzanine_Rail_Post_{k}", (121.0 + k * 2.0, 12.05, Z2 + 0.25), (0.05, 0.05, 0.50), (0.60, 0.60, 0.62, 1.0))
    # the dead escalator up to it (x 133..135, y 4..12)
    run = 8.0
    ang = math.atan2(Z2, run)
    make_rot_box("Escalator_Truss", (134.0, 8.0, Z2 / 2.0 - 0.30), (1.4, run / math.cos(ang) + 0.6, 0.6), (0.40, 0.40, 0.42, 1.0), roll=ang)
    for k in range(20):
        t = (k + 0.5) / 20.0
        make_box(f"Escalator_Step_Stock_{k}", (134.0, 4.0 + t * run, t * Z2 + 0.02), (1.0, run / 20.0, 0.10), (0.30, 0.30, 0.32, 1.0))
    for s in (-1, 1):
        make_rot_box(f"Escalator_Balustrade_{s:+d}", (134.0 + s * 0.62, 8.0, Z2 / 2.0 + 0.55), (0.08, run / math.cos(ang) + 0.6, 0.90),
                     (0.56, 0.58, 0.60, 1.0), roll=ang)
        make_rot_box(f"Escalator_Handrail_{s:+d}", (134.0 + s * 0.62, 8.0, Z2 / 2.0 + 1.02), (0.10, run / math.cos(ang) + 0.6, 0.06),
                     (0.10, 0.10, 0.10, 1.0), roll=ang)
    # the glass counter with its crunching recess, the register gone
    make_box("Counter_Base", (127.0, 7.0, 0.45), (3.2, 0.70, 0.90), (0.44, 0.40, 0.36, 1.0))
    make_box("Counter_Glass_Recess_Dark", (127.0, 7.0, 0.905), (3.0, 0.56, 0.01), (0.20, 0.22, 0.22, 1.0))
    for k in range(9):
        make_rot_box(f"Counter_Broken_Glass_{k}", (125.8 + k * 0.28, 6.9 + (k % 3) * 0.10, 0.915), (0.12, 0.08, 0.008),
                     (0.80, 0.86, 0.86, 1.0), yaw=k * 0.7)
    # the naked mannequins, the slumped dusty sale banners, empty racks
    for k, (x, y, yaw) in enumerate(((124.0, 3.4, 0.3), (130.5, 4.6, -0.6), (139.0, 6.0, 1.2), (144.0, 3.8, 2.0), (141.5, 9.6, 0.0))):
        make_cyl(f"Mannequin_{k}_Stand", (x, y, 0.03), 0.18, 0.06, (0.30, 0.30, 0.30, 1.0), segments=12)
        make_cyl(f"Mannequin_{k}_Pole", (x, y, 0.40), 0.02, 0.70, (0.30, 0.30, 0.30, 1.0), segments=6)
        make_blob(f"Mannequin_{k}_Hips", (x, y, 0.90), 0.18, (0.86, 0.82, 0.76, 1.0), noise=0.0, seed=k, squash=1.2)
        make_blob(f"Mannequin_{k}_Torso", (x, y, 1.30), 0.20, (0.86, 0.82, 0.76, 1.0), noise=0.0, seed=10 + k, squash=1.6)
        make_blob(f"Mannequin_{k}_Head", (x, y, 1.70), 0.10, (0.86, 0.82, 0.76, 1.0), noise=0.0, seed=20 + k, squash=1.2)
        make_box(f"Mannequin_{k}_Neck", (x, y, 1.56), (0.06, 0.06, 0.10), (0.86, 0.82, 0.76, 1.0))
    for k, (x, y) in enumerate(((123.0, 11.8), (131.0, 11.8), (141.0, 11.8), (147.0, 11.8))):
        make_box(f"Sale_Banner_Hang_{k}", (x, 12.1, Z2 - 0.30 - 0.45), (2.6, 0.03, 0.9), ((0.80, 0.30, 0.26, 1.0), (0.86, 0.80, 0.56, 1.0))[k % 2])
        make_rot_box(f"Sale_Banner_Fallen_{k}", (x + 0.6, 9.8 - (k % 2) * 1.2, 0.015), (2.0, 0.6, 0.03), ((0.74, 0.28, 0.24, 1.0), (0.80, 0.74, 0.52, 1.0))[k % 2],
                     yaw=0.3 * (k - 1.5))
    for k in range(3):
        make_box(f"Empty_Rack_Bar_{k}", (137.0 + k * 3.0, 15.0, 1.50), (1.6, 0.03, 0.03), (0.60, 0.60, 0.62, 1.0))
        for s in (-1, 1):
            make_box(f"Empty_Rack_Upright_{k}_{s:+d}", (137.0 + k * 3.0 + s * 0.78, 15.0, 0.75), (0.03, 0.03, 1.50), (0.60, 0.60, 0.62, 1.0))
    for k in range(10):
        make_box(f"Dust_Drift_{k}", (122.0 + k * 2.8, 2.0 + (k % 4) * 2.5, 0.004), (1.6, 1.2, 0.006), (0.70, 0.66, 0.60, 1.0))
    # the street outside, the fast-food place across it, the sun high
    make_box("Street_Asphalt", (135.0, -8.0, -0.02), (80.0, 10.0, 0.04), (0.30, 0.30, 0.32, 1.0))
    make_box("Sidewalk", (135.0, -1.6, 0.06), (80.0, 2.8, 0.12), (0.62, 0.60, 0.56, 1.0))
    make_box("Across_Fast_Food_Facade", (135.0, -16.0, 3.5), (16.0, 1.0, 7.0), (0.86, 0.70, 0.40, 1.0))
    make_box("Across_Fast_Food_Sign_Board", (135.0, -15.4, 6.2), (6.0, 0.20, 1.2), (0.86, 0.26, 0.20, 1.0))
    for k in range(4):
        make_box(f"Across_Building_{k}", (105.0 + k * 20.0 if k < 2 else 155.0 + (k - 2) * 20.0, -18.0, 8.0), (14.0, 2.0, 16.0),
                 ((0.56, 0.52, 0.48, 1.0), (0.48, 0.50, 0.52, 1.0))[k % 2])
    make_box("Sky_Day_S", (135.0, -150.0, 50.0), (400.0, 0.2, 160.0), (0.70, 0.78, 0.86, 1.0))


def build_mirror_room():
    """x 260..263.6, y 0..3: an ordinary washroom; the mirror on the N wall is
    an opening onto the same room mirrored (y 3..6), so it shows the world
    behind her."""
    H = 2.5
    def room(tag, flip):
        sgn = -1.0 if flip else 1.0
        oy = 6.0 if flip else 0.0
        def Y(y):
            return oy + sgn * y
        make_box(f"Mirror_{tag}_Floor", (261.8, Y(1.5), 0.004), (3.6, 3.0, 0.008), (0.80, 0.80, 0.76, 1.0))
        make_box(f"Mirror_{tag}_Ceil", (261.8, Y(1.5), H + 0.04), (3.6, 3.0, 0.08), (0.90, 0.90, 0.88, 1.0))
        make_box(f"Mirror_{tag}_Wall_W", (259.9, Y(1.5), H / 2.0), (0.20, 3.0, H), (0.78, 0.80, 0.78, 1.0))
        make_box(f"Mirror_{tag}_Wall_E", (263.7, Y(1.5), H / 2.0), (0.20, 3.0, H), (0.78, 0.80, 0.78, 1.0))
        make_box(f"Mirror_{tag}_Wall_Far_W", (260.6, Y(-0.1), H / 2.0), (1.6, 0.20, H), (0.78, 0.80, 0.78, 1.0))
        make_box(f"Mirror_{tag}_Wall_Far_E", (263.25, Y(-0.1), H / 2.0), (0.70, 0.20, H), (0.78, 0.80, 0.78, 1.0))
        make_box(f"Mirror_{tag}_Wall_Far_Head", (262.15, Y(-0.1), 2.3), (1.0, 0.20, 0.40), (0.78, 0.80, 0.78, 1.0))
        make_box(f"Mirror_{tag}_Door_Ajar", (261.75, Y(0.30), 1.05), (0.04, 0.78, 2.1), (0.70, 0.62, 0.50, 1.0))
        make_box(f"Mirror_{tag}_Hall_Dark", (262.15, Y(-1.2), 1.1), (2.0, 0.04, 2.2), (0.06, 0.06, 0.08, 1.0))
        make_box(f"Mirror_{tag}_Towel_Hang", (260.08, Y(1.4), 1.1), (0.04, 0.50, 0.60), (0.56, 0.62, 0.70, 1.0))
        make_box(f"Mirror_{tag}_Towel_Bar_Mounted", (260.03, Y(1.4), 1.42), (0.06, 0.60, 0.03), (0.70, 0.70, 0.72, 1.0))
        make_box(f"Mirror_{tag}_Tub_Body", (262.9, Y(0.95), 0.28), (1.5, 1.7, 0.56), (0.94, 0.94, 0.92, 1.0))
        make_box(f"Mirror_{tag}_Picture_Mounted", (263.58, Y(1.5), 1.6), (0.02, 0.40, 0.50), (0.40, 0.30, 0.26, 1.0))
    room("Here", False)
    room("Glass", True)
    # the N wall with the mirror opening, the sink under it
    make_box("Mirror_Wall_N_W", (260.45, 3.0, 1.25), (1.30, 0.06, 2.5), (0.78, 0.80, 0.78, 1.0))
    make_box("Mirror_Wall_N_E", (263.15, 3.0, 1.25), (1.30, 0.06, 2.5), (0.78, 0.80, 0.78, 1.0))
    make_box("Mirror_Wall_N_Below", (261.8, 3.0, 0.55), (1.4, 0.06, 1.10), (0.78, 0.80, 0.78, 1.0))
    make_box("Mirror_Wall_N_Above", (261.8, 3.0, 2.35), (1.4, 0.06, 0.30), (0.78, 0.80, 0.78, 1.0))
    frame("Mirror_Edge", 'X', 261.8, 3.0, 1.65, 1.4, 1.1, depth=0.06)
    make_box("Sink_Vanity", (261.8, 3.0 - 0.03 - 0.25, 0.42), (1.0, 0.50, 0.84), (0.66, 0.58, 0.48, 1.0))
    make_box("Sink_Counter", (261.8, 3.0 - 0.03 - 0.26, 0.86), (1.04, 0.52, 0.04), (0.86, 0.84, 0.80, 1.0))
    make_box("Sink_Basin", (261.8, 2.72, 0.882), (0.40, 0.30, 0.004), (0.96, 0.96, 0.94, 1.0))
    make_box("Mirror_Glass_Sink_Basin", (261.8, 3.28, 0.882), (0.40, 0.30, 0.004), (0.96, 0.96, 0.94, 1.0))
    make_box("Mirror_Glass_Sink_Vanity", (261.8, 3.0 + 0.03 + 0.25, 0.42), (1.0, 0.50, 0.84), (0.66, 0.58, 0.48, 1.0))
    make_box("Mirror_Glass_Sink_Counter", (261.8, 3.0 + 0.03 + 0.26, 0.86), (1.04, 0.52, 0.04), (0.86, 0.84, 0.80, 1.0))
    make_box("Mirror_Side_Lamp_Mounted_Glow", (260.95, 3.0 - 0.06, 1.65), (0.10, 0.06, 0.24), (1.0, 0.92, 0.74, 1.0))


def build_boys_rooms():
    """Aaron's room (x 300..304.4, y 0..3.8). (Steven's is in chau_house.)"""
    H = 2.4
    for tag, x0, w, d in (("Aaron", 300.0, 4.4, 3.8),):
        pal = {"wall": ((0.70, 0.76, 0.82, 1.0) if tag == "Aaron" else (0.80, 0.76, 0.66, 1.0)), "baseboard": (0.40, 0.36, 0.30, 1.0)}
        make_floor(f"{tag}_Floor", (x0 + w / 2.0, d / 2.0, 0.0), size_x=w, size_y=d,
                   palette={"vinyl": (0.46, 0.40, 0.36, 1.0), "seam": (0.40, 0.34, 0.30, 1.0)})
        make_box(f"{tag}_Ceil", (x0 + w / 2.0, d / 2.0, H + 0.04), (w + 0.3, d + 0.3, 0.08), (0.90, 0.90, 0.88, 1.0))
        make_wall_with_openings(f"{tag}_Wall_N", (x0 + w / 2.0, d, 0), length=w + T, height=H, thickness=T, axis='X', palette=pal,
                                baseboard_face_sign=-1, openings=[(x0 + w / 2.0, 1.45, 1.1, 1.1)])
        make_wall_with_openings(f"{tag}_Wall_S", (x0 + w / 2.0, 0.0, 0), length=w + T, height=H, thickness=T, axis='X', palette=pal,
                                baseboard_face_sign=+1, openings=[(x0 + 0.7, 1.0, 0.80, 2.0)])
        make_wall(f"{tag}_Wall_W", (x0, d / 2.0, 0), length=d - T, height=H, thickness=T, axis='Y', palette=pal, baseboard_face_sign=+1)
        make_wall(f"{tag}_Wall_E", (x0 + w, d / 2.0, 0), length=d - T, height=H, thickness=T, axis='Y', palette=pal, baseboard_face_sign=-1)
        frame(f"{tag}_Window", 'X', x0 + w / 2.0, d, 1.45, 1.1, 1.1)
        make_box(f"{tag}_Door_Open", (x0 + 0.7 + 0.40, 0.09 + 0.42, 1.0), (0.04, 0.80, 2.0), (0.70, 0.62, 0.50, 1.0))
        make_box(f"{tag}_Window_Sky", (x0 + w / 2.0, d + 0.40, 1.45), (1.6, 0.04, 1.6),
                 (0.26, 0.26, 0.40, 1.0))   # Aaron's evening (pass 160: dusk, not a black panel)
        make_box(f"{tag}_Window_Neighbor_Roof", (x0 + w / 2.0 + 0.3, d + 0.38, 1.05), (1.0, 0.02, 0.60), (0.16, 0.14, 0.14, 1.0))
        make_box(f"{tag}_Window_Neighbor_Light", (x0 + w / 2.0 + 0.5, d + 0.36, 1.10), (0.22, 0.01, 0.18), (0.96, 0.82, 0.50, 1.0))
        make_box(f"{tag}_Window_Pane", (x0 + w / 2.0, d, 1.45), (1.1, 0.02, 1.1), (0.78, 0.84, 0.88, 0.25))
        make_box(f"{tag}_Curtain_L", (x0 + w / 2.0 - 0.62, d - 0.14, 1.45), (0.22, 0.06, 1.30), (0.56, 0.50, 0.40, 1.0))
        make_box(f"{tag}_Curtain_R", (x0 + w / 2.0 + 0.62, d - 0.14, 1.45), (0.22, 0.06, 1.30), (0.56, 0.50, 0.40, 1.0))
        make_cyl(f"{tag}_Curtain_Rod", (x0 + w / 2.0, d - 0.14, 2.10), 0.015, 1.60, (0.30, 0.26, 0.20, 1.0), axis='X', segments=6)
        for e in (-1, 1):                      # the rod's brackets to the wall
            make_box(f"{tag}_Curtain_Bracket_{e:+d}", (x0 + w / 2.0 + e * 0.76, d - 0.12, 2.10), (0.03, 0.06, 0.03), (0.30, 0.26, 0.20, 1.0))
    # Aaron: the bed, the toys still out, the small grey console, the
    # magazines and comics, a shelf of toys
    ax = 300.0
    make_bed("Aaron_Bed", ax + 4.4 - 0.09 - 0.50, 1.9, head="+Y", w=0.95, d=1.9, made=False, blanket_col=(0.30, 0.40, 0.60, 1.0))
    make_box("Aaron_Toy_Shelf", (ax + 0.09 + 0.18, 2.4, 0.70), (0.36, 1.4, 1.40), (0.60, 0.50, 0.36, 1.0))
    for k in range(8):
        make_box(f"Aaron_Shelf_Toy_{k}", (ax + 0.27, 1.85 + (k % 4) * 0.30, 0.30 + (k // 4) * 0.50), (0.18, 0.16, 0.20),
                 ((0.90, 0.30, 0.20, 1.0), (0.30, 0.50, 0.90, 1.0), (0.96, 0.84, 0.30, 1.0), (0.30, 0.70, 0.40, 1.0))[k % 4])
    for k in range(7):
        make_box(f"Aaron_Floor_Toy_{k}", (ax + 1.4 + (k % 4) * 0.5, 1.2 + (k // 4) * 0.7, 0.06), (0.14 + (k % 2) * 0.08, 0.12, 0.12),
                 ((0.90, 0.30, 0.20, 1.0), (0.30, 0.50, 0.90, 1.0), (0.96, 0.84, 0.30, 1.0))[k % 3])
    make_box("Aaron_TV_Stand", (ax + 1.6, 3.8 - 0.09 - 0.25, 0.25), (0.80, 0.46, 0.50), (0.40, 0.32, 0.24, 1.0))
    make_chamfer_box("Aaron_TV", (ax + 1.6, 3.8 - 0.09 - 0.27, 0.72), (0.44, 0.40, 0.42), (0.18, 0.18, 0.18, 1.0), chamfer=0.03)
    make_box("Aaron_TV_Screen", (ax + 1.6, 3.8 - 0.09 - 0.472, 0.73), (0.32, 0.004, 0.26), (0.20, 0.24, 0.30, 1.0))
    make_box("Aaron_Console_Grey", (ax + 1.6, 3.8 - 0.09 - 0.70, 0.04), (0.26, 0.20, 0.08), (0.66, 0.66, 0.66, 1.0))
    make_box("Aaron_Controller_Cord", (ax + 1.6, 3.8 - 0.09 - 1.00, 0.008), (0.012, 0.40, 0.012), (0.12, 0.12, 0.12, 1.0))
    make_box("Aaron_Controller", (ax + 1.6, 3.8 - 0.09 - 1.24, 0.015), (0.14, 0.06, 0.03), (0.66, 0.66, 0.66, 1.0))
    for k in range(5):
        make_box(f"Aaron_Magazine_{k}", (ax + 2.6, 1.0, 0.008 + k * 0.012), (0.21, 0.28, 0.010),
                 ((0.86, 0.30, 0.24, 1.0), (0.30, 0.40, 0.70, 1.0), (0.92, 0.86, 0.40, 1.0))[k % 3])
    make_box("Aaron_Rug", (ax + 2.0, 1.6, 0.004), (1.8, 1.4, 0.008), (0.40, 0.46, 0.56, 1.0))


def build_dean_house():
    """x 420..428, y 0..7: the reading room, late: the armchair, the lamp,
    the books, the door to the dark hall and the stairs."""
    H = 2.9
    x0, x1, y0, y1 = 420.0, 428.0, 0.0, 7.0
    pal = {"wall": (0.62, 0.54, 0.44, 1.0), "baseboard": (0.34, 0.26, 0.20, 1.0)}
    make_floor("DeanHome_Floor", (424.0, 3.5, 0.0), size_x=8.0, size_y=7.0,
               palette={"vinyl": (0.40, 0.28, 0.20, 1.0), "seam": (0.34, 0.24, 0.16, 1.0)}, style="plank")
    make_box("DeanHome_Ceil", (424.0, 3.5, H + 0.04), (8.4, 7.4, 0.08), (0.86, 0.84, 0.78, 1.0))
    make_wall_with_openings("DeanHome_Wall_S", (424.0, y0, 0), length=8.0 + T, height=H, thickness=T, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(426.6, 1.1, 1.2, 2.2)])
    make_wall_with_openings("DeanHome_Wall_N", (424.0, y1, 0), length=8.0 + T, height=H, thickness=T, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(422.4, 1.5, 1.6, 1.6)])
    make_wall("DeanHome_Wall_W", (x0, 3.5, 0), length=7.0 - T, height=H, thickness=T, axis='Y', palette=pal, baseboard_face_sign=+1)
    make_wall("DeanHome_Wall_E", (x1, 3.5, 0), length=7.0 - T, height=H, thickness=T, axis='Y', palette=pal, baseboard_face_sign=-1)
    frame("DeanHome_Window", 'X', 422.4, y1, 1.5, 1.6, 1.6)
    make_box("DeanHome_Window_Sky_Night", (422.4, y1 + 0.5, 1.5), (2.2, 0.04, 2.0), (0.04, 0.05, 0.08, 1.0))
    # the bookshelves along the W wall, the armchair, the lamp, the book
    for k in range(3):
        make_box(f"DeanHome_Bookcase_{k}", (x0 + 0.09 + 0.18, 1.2 + k * 1.6, 1.10), (0.36, 1.5, 2.20), (0.36, 0.24, 0.16, 1.0))
        for lvl in range(5):
            make_box(f"DeanHome_Books_Stock_{k}_{lvl}", (x0 + 0.09 + 0.20, 1.2 + k * 1.6, 0.30 + lvl * 0.42), (0.26, 1.36, 0.26),
                     ((0.50, 0.20, 0.18, 1.0), (0.20, 0.30, 0.40, 1.0), (0.60, 0.50, 0.30, 1.0))[(k + lvl) % 3])
    make_box("Armchair_Base", (422.4, 3.6, 0.24), (0.90, 0.90, 0.48), (0.46, 0.24, 0.18, 1.0))
    make_box("Armchair_Back", (422.4, 4.0, 0.80), (0.90, 0.18, 0.66), (0.46, 0.24, 0.18, 1.0))
    for s in (-1, 1):
        make_box(f"Armchair_Arm_{s:+d}", (422.4 + s * 0.40, 3.6, 0.60), (0.12, 0.90, 0.24), (0.46, 0.24, 0.18, 1.0))
    make_box("Armchair_Ottoman", (422.4, 2.6, 0.22), (0.60, 0.50, 0.44), (0.46, 0.24, 0.18, 1.0))
    make_box("Side_Table", (423.25, 4.1, 0.30), (0.50, 0.50, 0.60), (0.36, 0.24, 0.16, 1.0))
    make_lamp("Reading_Lamp", 423.25, 4.1, base_z=0.60, h=0.70)
    make_box("Book_Open_On_Arm", (422.0, 3.5, 0.735), (0.24, 0.18, 0.03), (0.92, 0.90, 0.84, 1.0))
    make_box("Whiskey_Glass", (423.10, 3.95, 0.65), (0.07, 0.07, 0.10), (0.70, 0.56, 0.30, 1.0))
    make_box("DeanHome_Rug", (423.4, 3.4, 0.004), (3.0, 2.2, 0.008), (0.50, 0.30, 0.24, 1.0))
    make_box("DeanHome_Sofa_Base", (425.8, 5.8, 0.22), (2.2, 0.86, 0.44), (0.56, 0.50, 0.40, 1.0))
    make_box("DeanHome_Sofa_Back", (425.8, 6.18, 0.64), (2.2, 0.16, 0.42), (0.56, 0.50, 0.40, 1.0))
    make_box("Child_Drawing_On_Table", (425.6, 4.6, 0.405), (0.30, 0.22, 0.004), (0.96, 0.94, 0.88, 1.0))
    make_box("DeanHome_Coffee_Table", (425.6, 4.6, 0.20), (1.2, 0.60, 0.40), (0.36, 0.24, 0.16, 1.0))
    # the dark hall through the door, the stair's first steps
    make_box("DeanHome_Hall_Floor", (426.6, -1.5, -0.02), (3.0, 2.8, 0.04), (0.40, 0.28, 0.20, 1.0))
    for k in range(4):
        make_box(f"DeanHome_Stair_Step_{k}", (427.6, -1.0 - k * 0.28, 0.09 + k * 0.18), (1.0, 0.28, 0.18 * (k + 1)), (0.36, 0.24, 0.16, 1.0))
    make_box("DeanHome_Hall_Wall_Far", (426.6, -2.95, 1.45), (3.2, 0.10, 2.9), (0.40, 0.34, 0.28, 1.0))


def build_shanghai():
    """x 700..708, y 0..6: one room, windows along the N and E walls, high
    over a night city (the towers stand below, z -60..)."""
    H = 2.8
    x0, x1, y0, y1 = 700.0, 708.0, 0.0, 6.0
    pal = {"wall": (0.82, 0.82, 0.80, 1.0), "baseboard": (0.40, 0.40, 0.40, 1.0)}
    make_floor("Shanghai_Floor", (704.0, 3.0, 0.0), size_x=8.0, size_y=6.0,
               palette={"vinyl": (0.52, 0.48, 0.44, 1.0), "seam": (0.46, 0.42, 0.38, 1.0)})
    make_box("Shanghai_Ceil", (704.0, 3.0, H + 0.04), (8.4, 6.4, 0.08), (0.90, 0.90, 0.88, 1.0))
    make_wall_with_openings("Shanghai_Wall_N", (704.0, y1, 0), length=8.0 + T, height=H, thickness=T, axis='X', palette=pal,
                            baseboard_face_sign=-1, openings=[(701.6, 1.45, 1.8, 2.1), (704.0, 1.45, 1.8, 2.1), (706.4, 1.45, 1.8, 2.1)])
    make_wall_with_openings("Shanghai_Wall_E", (x1, 3.0, 0), length=6.0 - T, height=H, thickness=T, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(2.0, 1.45, 1.8, 2.1), (4.4, 1.45, 1.8, 2.1)])
    make_wall_with_openings("Shanghai_Wall_S", (704.0, y0, 0), length=8.0 + T, height=H, thickness=T, axis='X', palette=pal,
                            baseboard_face_sign=+1, openings=[(701.0, 1.0, 0.90, 2.0)])
    make_wall("Shanghai_Wall_W", (x0, 3.0, 0), length=6.0 - T, height=H, thickness=T, axis='Y', palette=pal, baseboard_face_sign=+1)
    for k, x in enumerate((701.6, 704.0, 706.4)):
        frame(f"Shanghai_Win_N_{k}", 'X', x, y1, 1.45, 1.8, 2.1)
    for k, y in enumerate((2.0, 4.4)):
        frame(f"Shanghai_Win_E_{k}", 'Y', y, x1, 1.45, 1.8, 2.1)
    make_box("Shanghai_Door_Shut", (701.0, y0, 1.0), (0.88, 0.04, 2.0), (0.50, 0.44, 0.36, 1.0))
    # spare: a bed, a chair, a lamp, his bag left by the door
    make_bed("Shanghai_Bed", x0 + 0.09 + 1.0, 2.2, head="-X", w=1.4, d=1.95, made=True, blanket_col=(0.80, 0.80, 0.78, 1.0))
    make_chair("Shanghai_Chair", 705.6, 2.0, yaw=math.pi / 4.0, wood=(0.30, 0.30, 0.32, 1.0))
    make_lamp("Shanghai_Floor_Lamp", 707.4, 0.6, base_z=0.0, h=1.40)
    make_box("Aria_Bag", (701.8, 0.6, 0.18), (0.50, 0.30, 0.36), (0.40, 0.20, 0.30, 1.0))
    # the city below: towers in rings out to 180 m, their windows lit; the
    # streets far down; the haze over it all
    make_box("Shanghai_Building_Core", (704.0, 3.0, -30.0), (12.0, 10.0, 59.6), (0.40, 0.40, 0.42, 1.0))
    make_box("City_Ground_Far", (704.0, 3.0, -60.0), (380.0, 380.0, 0.2), (0.08, 0.08, 0.10, 1.0))
    k = 0
    for ring in range(4):
        r = 40.0 + ring * 36.0
        n = 10 + ring * 4
        for i in range(n):
            a = (i + 0.5 * (ring % 2)) * 2.0 * math.pi / n
            bx, by = 704.0 + r * math.cos(a), 3.0 + r * math.sin(a)
            h = 30.0 + ((i * 7 + ring * 3) % 5) * 12.0
            make_box(f"City_Tower_Stock_{k}", (bx, by, -60.0 + h / 2.0), (12.0, 12.0, h), (0.14, 0.15, 0.18, 1.0))
            for j in range(6):
                make_box(f"City_Window_Glow_Stock_{k}_{j}", (bx - 6.02 * math.cos(a), by - 6.02 * math.sin(a), -60.0 + h * (0.15 + j * 0.14)),
                         (abs(math.sin(a)) * 10.0 + 0.1, abs(math.cos(a)) * 10.0 + 0.1, 2.0),
                         ((1.0, 0.82, 0.52, 1.0), (0.80, 0.90, 1.0, 1.0), (1.0, 0.70, 0.40, 1.0))[(k + j) % 3])
            k += 1
    for k in range(6):
        make_box(f"City_Street_Glow_Stock_{k}", (704.0 + (k - 3) * 30.0, 3.0, -59.8), (2.0, 360.0, 0.1), (0.90, 0.70, 0.40, 1.0))
    make_box("Sky_Night_N", (704.0, 190.0, 20.0), (400.0, 0.2, 200.0), (0.06, 0.06, 0.10, 1.0))
    make_box("Sky_Night_E", (894.0, 3.0, 20.0), (0.2, 400.0, 200.0), (0.06, 0.06, 0.10, 1.0))


def main():
    clear_scene()
    build_garage()
    build_store()
    build_mirror_room()
    build_boys_rooms()
    build_dean_house()
    build_shanghai()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/vol4_story_rooms.glb"))
    print(f"\n[build_vol4_story_rooms] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
