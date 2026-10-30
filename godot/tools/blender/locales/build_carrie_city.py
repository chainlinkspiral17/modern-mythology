"""carrie_city — vol 4's Sister Carrie pieces: Charlie's flat, the after
party, the sister's house (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
One unnamed city (the adaptation never names it). Undated: the scenes carry
a PDA, a phone in a car, a newspaper, a Wal-Mart vest and a $6.50 wage, so
nothing later than that (no smartphones, no flat screens on walls).
  Charlie's apartment: "Charlie is lying in bed, a book over his chest.";
   "Charlie wakes up in bed and walks through the apartment."; "There's not
   room enough for us both on the couch."; "He puts a blanket on her.";
   "Charlie sits in a chair across from her."; "It is morning now, the
   blanket is still on the couch, but Carrie is gone." He has "art to make".
                                         → x 0..10: the bedroom and the living
                                           room through its door
  the after party, five minutes' walk away: "A woman swings on a tire";
   "Charlie follows it to the bar, where it lands in a shot glass."; "They
   sit together on two stools so close together." The pink and orange
   contrails are an effect, not fixtures.
                                         → x 40..58: one loft room
  the sister's house: "pretty low rent, in bad shape, maybe two bedrooms,
   tight and cramped, the yard in a sorry state"; inside, the couple "go
   about their business"; "throw your own goddamn clothes in the goddamn
   dryer"                                → x 80..92, the yard and the room

Blender: x east, y north, z up; Godot (x, z, -y). Each area keeps its city
or street inside 200 m (the VN camera's far plane).

(2026-10-28) the after party's grungy bathroom off the loft's east wall
(cc_3: "Someone has drawn a face with a sharpie marker") → afterparty_bathroom.

DRAFT 2 targets: the flat's kitchen; Paradise Lost (the club) as its own area; the sister's street with its neighbours;
the two children's room; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe, make_gable,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_table, make_lamp, make_sofa
from _props.decor import make_floor_plant
from _props.objects import make_mug
from _props.figures import make_standing_figure

T = 0.16
FLAT = {"wall": (0.82, 0.80, 0.74, 1.0), "baseboard": (0.40, 0.36, 0.30, 1.0)}
LOFT = {"wall": (0.56, 0.36, 0.30, 1.0), "baseboard": (0.30, 0.26, 0.24, 1.0)}
WORN = {"wall": (0.74, 0.70, 0.58, 1.0), "baseboard": (0.40, 0.34, 0.26, 1.0)}
TRIM = (0.88, 0.86, 0.80, 1.0)
CN, CD = "__charlie_living_night", "__charlie_living_day"


def window_frame(name, axis, along, at, cz, w, h, depth=T):
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


def build_flat():
    """x 0..10, y 0..8: the bedroom x 0..4, the living room x 4..10; the
    street's facades across from the S windows."""
    H = 2.7
    make_floor("Flat_Floor", (5.0, 4.0, 0.0), size_x=10.0, size_y=8.0,
               palette={"vinyl": (0.56, 0.42, 0.28, 1.0), "seam": (0.48, 0.36, 0.24, 1.0)}, style="plank")
    make_box("Flat_Ceil", (5.0, 4.0, H + 0.04), (10.4, 8.4, 0.08), (0.90, 0.90, 0.88, 1.0))
    make_wall_with_openings("Flat_Wall_S", (5.0, 0.0, 0), length=10.0 + T, height=H, thickness=T, axis='X', palette=FLAT,
                            baseboard_face_sign=+1, openings=[(2.0, 1.45, 1.2, 1.4), (6.6, 1.45, 1.4, 1.5), (8.6, 1.45, 1.4, 1.5)])
    make_wall("Flat_Wall_N", (5.0, 8.0, 0), length=10.0 + T, height=H, thickness=T, axis='X', palette=FLAT, baseboard_face_sign=-1)
    make_wall("Flat_Wall_W", (0.0, 4.0, 0), length=8.0 - T, height=H, thickness=T, axis='Y', palette=FLAT, baseboard_face_sign=+1)
    make_wall_with_openings("Flat_Wall_E", (10.0, 4.0, 0), length=8.0 - T, height=H, thickness=T, axis='Y', palette=FLAT,
                            baseboard_face_sign=-1, openings=[(6.6, 1.0, 0.9, 2.0)])
    make_wall_with_openings("Flat_Wall_Bedroom_E", (4.0, 4.0, 0), length=8.0 - T, height=H, thickness=0.12, axis='Y', palette=FLAT,
                            baseboard_face_sign=+1, openings=[(5.6, 1.0, 0.86, 2.0)])
    make_box("Bedroom_Door_Open", (4.0 - 0.06 - 0.42, 5.6 + 0.43, 1.0), (0.80, 0.04, 2.0), (0.70, 0.62, 0.50, 1.0))
    make_box("Flat_Front_Door", (10.0, 6.6, 1.0), (0.04, 0.88, 2.0), (0.46, 0.36, 0.28, 1.0))
    for nm, al, w, h in (("Bed_Window", 2.0, 1.2, 1.4), ("Living_Window_A", 6.6, 1.4, 1.5), ("Living_Window_B", 8.6, 1.4, 1.5)):
        window_frame(nm, 'X', al, 0.0, 1.45, w, h)
    # the bedroom: the bed, the reading lamp, a book, the dresser, clothes
    make_bed("Charlie_Bed", 1.6, 7.92 - 1.0, head="+Y", w=1.4, d=2.0, made=False, blanket_col=(0.40, 0.42, 0.36, 1.0))
    make_box("Nightstand", (0.08 + 0.26, 7.3, 0.30), (0.44, 0.40, 0.60), (0.44, 0.34, 0.24, 1.0))
    make_lamp("Reading_Lamp", 0.34, 7.3, base_z=0.60, h=0.50)
    make_box("Book_On_Nightstand", (0.40, 7.15, 0.62), (0.16, 0.22, 0.04), (0.50, 0.20, 0.18, 1.0))
    make_box("Dresser", (3.92 - 0.06 - 0.25, 2.0, 0.48), (0.50, 1.10, 0.96), (0.44, 0.34, 0.24, 1.0))
    make_box("Dresser_Clothes_Pile", (3.92 - 0.06 - 0.25, 1.8, 1.00), (0.40, 0.40, 0.08), (0.26, 0.30, 0.40, 1.0))
    make_box("Clothes_On_Floor", (2.8, 3.6, 0.03), (0.60, 0.40, 0.06), (0.30, 0.30, 0.34, 1.0))
    make_box("Bedroom_Rug", (1.8, 3.6, 0.004), (1.6, 1.2, 0.008), (0.50, 0.38, 0.30, 1.0))
    # (2026-10-30) the bedroom was the bed in a bare box; his art lived only
    # in the living room. "I have projects I must work on, people to see, art
    # to make"; "Charlie is lying in bed, a book over his chest." Canvases
    # leaning on the W wall (one begun), the bookshelf, a print over the bed,
    # the book open on the blanket, a stack beside the bed.
    for k, (y, w, h, col) in enumerate(((2.4, 0.90, 1.10, (0.92, 0.90, 0.84, 1.0)), (2.5, 0.70, 0.90, (0.86, 0.60, 0.40, 1.0)),
                                        (3.3, 0.60, 0.76, (0.40, 0.52, 0.66, 1.0)))):
        make_rot_box(f"Bedroom_Canvas_{k}", (0.20 + k * 0.05, y, h / 2.0 + 0.02), (0.03, w, h), col, roll=0.10)
    make_rot_box("Bedroom_Canvas_1_Mark", (0.27, 2.45, 0.50), (0.004, 0.40, 0.30), (0.30, 0.20, 0.16, 1.0), roll=0.10)
    make_box("Bedroom_Shelf", (0.20, 4.6, 0.95), (0.32, 0.90, 1.90), (0.40, 0.30, 0.22, 1.0))
    for r in range(4):
        for b in range(7):
            make_box(f"Bedroom_Shelf_Book_{r}_{b}", (0.30, 4.25 + b * 0.10, 0.32 + r * 0.44), (0.18, 0.06, 0.24 + (b % 3) * 0.03),
                     ((0.60, 0.20, 0.18, 1.0), (0.20, 0.30, 0.44, 1.0), (0.84, 0.78, 0.60, 1.0), (0.30, 0.40, 0.26, 1.0))[(r + b) % 4])
    make_box("Bedroom_Print_Frame", (1.6, 7.92 - 0.016, 1.75), (0.80, 0.02, 0.60), (0.18, 0.16, 0.14, 1.0))
    make_box("Bedroom_Print", (1.6, 7.92 - 0.028, 1.75), (0.72, 0.004, 0.52), (0.70, 0.66, 0.50, 1.0))
    make_rot_box("Book_On_Bed", (1.55, 6.3, 0.66), (0.20, 0.26, 0.03), (0.30, 0.36, 0.50, 1.0), yaw=0.3)
    for k in range(5):
        make_box(f"Bed_Side_Book_Stack_{k}", (2.6, 7.0, 0.03 + k * 0.05), (0.20 + (k % 2) * 0.03, 0.26, 0.05),
                 ((0.60, 0.20, 0.18, 1.0), (0.84, 0.78, 0.60, 1.0), (0.20, 0.30, 0.44, 1.0))[k % 3])
    # the living room: the small couch, the chair across, the low table;
    # canvases leaning (he has art to make); the blanket on the couch
    make_sofa("Couch", 6.2, 6.8, back="+Y", w=1.6, d=0.86, seats=2, color=(0.40, 0.44, 0.50, 1.0), arm="track",
              leg_col=(0.30, 0.24, 0.18, 1.0))                                  # pass 160: the kit sofa (it was three slabs)
    make_rot_box("Couch_Blanket" + CN + CD, (6.1, 6.7, 0.455), (1.30, 0.80, 0.04), (0.70, 0.56, 0.36, 1.0), yaw=0.08)
    # pass 160: the living room was a couch and a chair in a bare box — a rug
    # under the table, two of his own prints on the N wall, a plant by the
    # window, a crate of records, a mug on the table
    make_box("Living_Rug", (6.2, 5.9, 0.004), (2.6, 2.2, 0.008), (0.46, 0.40, 0.36, 1.0))
    for k, (x, col) in enumerate(((7.4, (0.80, 0.52, 0.36, 1.0)), (8.6, (0.30, 0.40, 0.56, 1.0)))):
        make_box(f"Living_Print_{k}_Frame", (x, 7.92 - 0.016, 1.65), (0.70, 0.02, 0.90), (0.20, 0.18, 0.16, 1.0))
        make_box(f"Living_Print_{k}", (x, 7.92 - 0.028, 1.65), (0.62, 0.004, 0.82), col)
        make_box(f"Living_Print_{k}_Mark", (x - 0.1, 7.92 - 0.032, 1.55 + k * 0.2), (0.28, 0.002, 0.10), (0.92, 0.90, 0.84, 1.0))
    make_floor_plant("Living_Plant", (9.4, 0.5, 0.0), kind="snake")
    make_box("Record_Crate", (4.4, 0.6, 0.18), (0.40, 0.36, 0.36), (0.50, 0.40, 0.28, 1.0))
    for k in range(9):
        make_box(f"Record_Crate_Sleeve_{k}", (4.4, 0.45 + k * 0.03, 0.36), (0.32, 0.012, 0.32), ((0.86, 0.30, 0.24, 1.0), (0.20, 0.24, 0.30, 1.0), (0.92, 0.88, 0.70, 1.0))[k % 3])
    make_mug("Living_Mug", 6.4, 5.95, 0.40, (0.30, 0.44, 0.56, 1.0))
    make_chair("Living_Chair", 6.2, 4.7, yaw=0.0, wood=(0.40, 0.30, 0.22, 1.0), seat_col=(0.56, 0.40, 0.30, 1.0))
    make_box("Low_Table", (6.2, 5.8, 0.20), (0.90, 0.50, 0.40), (0.44, 0.34, 0.24, 1.0))
    make_box("Newspaper_On_Table", (6.0, 5.8, 0.405), (0.36, 0.28, 0.01), (0.86, 0.84, 0.78, 1.0))
    for k in range(3):
        ch = 0.96 - k * 0.12
        make_rot_box(f"Canvas_Leaning_{k}", (9.92 - 0.02 - ch / 2.0 * math.sin(0.12) - k * 0.05, 2.0 + k * 0.10, ch / 2.0 * math.cos(0.12) + 0.002),
                     (0.03, 0.80 - k * 0.10, ch), ((0.92, 0.90, 0.86, 1.0), (0.80, 0.70, 0.56, 1.0), (0.94, 0.94, 0.92, 1.0))[k], pitch=0.12)
    make_lamp("Living_Floor_Lamp", 9.5, 7.5, base_z=0.0, h=1.50)
    make_box("Living_Shelf", (5.0, 7.92 - 0.20, 0.90), (1.6, 0.30, 1.80), (0.44, 0.34, 0.24, 1.0))
    for k in range(10):
        make_box(f"Living_Shelf_Book_Stock_{k}", (4.4 + k * 0.13, 7.92 - 0.22, 0.30 + (k % 3) * 0.55), (0.04, 0.22, 0.26),
                 ((0.50, 0.20, 0.18, 1.0), (0.20, 0.30, 0.46, 1.0), (0.80, 0.76, 0.66, 1.0))[k % 3])
    # the city across the street (inside 200 m), lit windows per hour
    for k in range(5):
        make_box(f"Across_Facade_{k}", (-6.0 + k * 6.0, -18.0, 7.0), (5.6, 1.0, 14.0 + (k % 3) * 4.0),
                 ((0.46, 0.40, 0.36, 1.0), (0.40, 0.42, 0.44, 1.0))[k % 2])
        for j in range(6):
            make_box(f"Across_Window_Glow_{k}_{j}" + CN, (-7.6 + k * 6.0 + (j % 3) * 1.6, -17.48, 3.0 + (j // 3) * 3.2),
                     (0.9, 0.04, 1.2), ((1.0, 0.82, 0.52, 1.0), (0.12, 0.12, 0.14, 1.0))[(j + k) % 2])
    make_box("Street_Below_Asphalt", (5.0, -10.0, -6.0), (60.0, 14.0, 0.2), (0.24, 0.24, 0.26, 1.0))
    make_box("Sky_Night_S" + CN + "__charlie_bedroom_night", (5.0, -120.0, 40.0), (300.0, 0.2, 140.0), (0.04, 0.05, 0.08, 1.0))
    make_box("Sky_Day_S" + CD + "__charlie_apartment_day", (5.0, -120.0, 40.0), (300.0, 0.2, 140.0), (0.70, 0.76, 0.82, 1.0))


def build_party():
    """x 40..58, y 0..14: one big loft room, the bar on the N wall, the tire
    on its rope from a beam, old sofas, the floor open between."""
    H = 4.2
    x0, x1, y0, y1 = 40.0, 58.0, 0.0, 14.0
    make_floor("Loft_Floor", (49.0, 7.0, 0.0), size_x=18.0, size_y=14.0,
               palette={"vinyl": (0.40, 0.30, 0.22, 1.0), "seam": (0.34, 0.26, 0.18, 1.0)}, style="plank")
    make_box("Loft_Ceil", (49.0, 7.0, H + 0.04), (18.4, 14.4, 0.08), (0.30, 0.28, 0.28, 1.0))
    for k in range(5):
        make_box(f"Loft_Beam_{k}", (41.8 + k * 3.6, 7.0, H - 0.22), (0.30, 14.0, 0.40), (0.36, 0.26, 0.18, 1.0))
    make_wall_with_openings("Loft_Wall_S", (49.0, y0, 0), length=18.0 + T, height=H, thickness=T, axis='X', palette=LOFT,
                            baseboard_face_sign=+1, openings=[(44.0, 2.2, 2.2, 2.4), (50.0, 2.2, 2.2, 2.4), (56.0, 1.1, 1.0, 2.2)])
    make_wall("Loft_Wall_N", (49.0, y1, 0), length=18.0 + T, height=H, thickness=T, axis='X', palette=LOFT, baseboard_face_sign=-1)
    make_wall("Loft_Wall_W", (x0, 7.0, 0), length=14.0 - T, height=H, thickness=T, axis='Y', palette=LOFT, baseboard_face_sign=+1)
    # (2026-10-28) the door to the grungy bathroom at y 11 (build_party_bathroom)
    make_wall_with_openings("Loft_Wall_E", (x1, 7.0, 0), length=14.0 - T, height=H, thickness=T, axis='Y', palette=LOFT,
                            baseboard_face_sign=-1, openings=[(11.0, 1.05, 0.9, 2.1)])
    make_box("Bathroom_Door_Open", (x1 + 0.45, 11.45 + 0.0, 1.05), (0.04, 0.84, 2.06), (0.30, 0.26, 0.24, 1.0))
    for nm, al in (("Loft_Window_A", 44.0), ("Loft_Window_B", 50.0)):
        window_frame(nm, 'X', al, y0, 2.2, 2.2, 2.4)
    make_box("Loft_Door_Shut", (56.0, y0, 1.1), (0.96, 0.05, 2.2), (0.30, 0.26, 0.24, 1.0))
    # the bar along the N wall: counter, back-bar, bottles, the shot glass
    make_box("Bar_Counter", (50.0, y1 - 0.08 - 1.4, 0.55), (8.0, 0.60, 1.10), (0.24, 0.18, 0.14, 1.0))
    make_box("Bar_Counter_Top", (50.0, y1 - 0.08 - 1.4, 1.12), (8.2, 0.70, 0.04), (0.14, 0.12, 0.10, 1.0))
    make_box("Bar_Foot_Rail_Mounted", (50.0, y1 - 0.08 - 1.4 - 0.32, 0.18), (7.8, 0.04, 0.04), (0.70, 0.60, 0.36, 1.0))
    for k in range(4):
        make_cyl(f"Bar_Foot_Rail_Post_{k}", (46.8 + k * 2.1, y1 - 0.08 - 1.4 - 0.32, 0.08), 0.015, 0.16, (0.70, 0.60, 0.36, 1.0), segments=6)
    for lvl in range(3):
        make_box(f"Back_Bar_Shelf_{lvl}", (50.0, y1 - 0.08 - 0.16, 1.30 + lvl * 0.40), (7.6, 0.30, 0.03), (0.24, 0.18, 0.14, 1.0))
        for k in range(24):
            make_lathe(f"Back_Bar_Bottle_{lvl}_{k}", (46.4 + k * 0.31, y1 - 0.08 - 0.16, 1.315 + lvl * 0.40),
                       [(0.0, 0.0), (0.04, 0.0), (0.04, 0.20), (0.014, 0.26), (0.014, 0.32), (0.0, 0.32)],
                       ((0.30, 0.40, 0.30, 1.0), (0.50, 0.30, 0.14, 1.0), (0.80, 0.80, 0.84, 1.0), (0.60, 0.20, 0.30, 1.0))[(k + lvl) % 4],
                       segments=8)
    make_lathe("Shot_Glass_Pink", (49.6, y1 - 0.08 - 1.4 - 0.10, 1.14), [(0.0, 0.0), (0.024, 0.0), (0.03, 0.06), (0.0, 0.06)],
               (0.96, 0.50, 0.66, 1.0), segments=10)
    for k in range(6):
        make_lathe(f"Shot_Glass_{k}", (46.8 + k * 0.9, y1 - 0.08 - 1.4 + 0.12, 1.14), [(0.0, 0.0), (0.024, 0.0), (0.03, 0.06), (0.0, 0.06)],
                   (0.80, 0.84, 0.86, 1.0), segments=10)
    # the stools: two pulled close together, the rest along the bar
    for k, x in enumerate((46.4, 47.6, 49.1, 49.55, 51.2, 52.6)):
        sy = y1 - 0.08 - 1.4 - 0.72
        make_cyl(f"Bar_Stool_Seat_{k}", (x, sy, 0.76), 0.18, 0.06, (0.50, 0.14, 0.14, 1.0), segments=14)
        make_cyl(f"Bar_Stool_Post_{k}", (x, sy, 0.37), 0.03, 0.72, (0.60, 0.60, 0.62, 1.0), segments=8)
        make_cyl(f"Bar_Stool_Foot_{k}", (x, sy, 0.01), 0.20, 0.02, (0.60, 0.60, 0.62, 1.0), segments=12)
    # the tire swing from the middle beam, its rope
    tx, ty = 49.0, 6.0
    beam_z = H - 0.42
    make_box("Tire_Swing_Rope", (tx + 0.0, ty, (beam_z + 1.30) / 2.0), (0.03, 0.03, beam_z - 1.30), (0.70, 0.62, 0.46, 1.0))
    make_lathe("Tire_Swing_Tire", (tx, ty, 0.90), [(0.22, 0.0), (0.40, 0.0), (0.44, 0.10), (0.44, 0.24), (0.40, 0.34), (0.22, 0.34),
                                                    (0.20, 0.17)], (0.10, 0.10, 0.10, 1.0), segments=18, loop=True)
    for s in (-1, 1):
        make_rot_box(f"Tire_Swing_Strap_{s:+d}", (tx + s * 0.16, ty, 1.12), (0.02, 0.02, 0.40), (0.70, 0.62, 0.46, 1.0), pitch=s * 0.35)
    make_box("Tire_Swing_Strap_Knot", (tx, ty, 1.30), (0.46, 0.04, 0.05), (0.70, 0.62, 0.46, 1.0))
    # old sofas round the edges, a low table of bottles and ashtrays
    for k, (x, y, yaw) in enumerate(((41.0, 6.0, -math.pi / 2.0), (57.0, 7.0, math.pi / 2.0))):
        make_box(f"Loft_Sofa_{k}_Base", (x, y, 0.22), (0.90, 2.2, 0.44), (0.30, 0.24, 0.40, 1.0))
        make_box(f"Loft_Sofa_{k}_Back", (x + (-0.37 if k == 0 else 0.37), y, 0.66), (0.16, 2.2, 0.46), (0.30, 0.24, 0.40, 1.0))
    make_box("Loft_Low_Table", (42.6, 6.0, 0.20), (0.70, 1.20, 0.40), (0.30, 0.24, 0.20, 1.0))
    make_cyl("Ashtray", (42.6, 5.7, 0.415), 0.08, 0.03, (0.50, 0.50, 0.52, 1.0), segments=12)
    for k in range(3):
        make_lathe(f"Party_Bottle_{k}", (42.5 + k * 0.1, 6.2 + k * 0.12, 0.40), [(0.0, 0.0), (0.035, 0.0), (0.035, 0.18), (0.012, 0.24),
                                                                         (0.0, 0.24)], (0.30, 0.40, 0.24, 1.0), segments=8)
    make_box("Speaker_Stack", (57.2, 12.2, 0.60), (0.60, 0.60, 1.20), (0.10, 0.10, 0.10, 1.0))
    make_box("Party_Lamp_Pink_Glow", (41.0, 12.6, 1.6), (0.30, 0.30, 0.40), (0.96, 0.50, 0.66, 1.0))
    make_box("Party_Lamp_Stand", (41.0, 12.6, 0.70), (0.06, 0.06, 1.40), (0.20, 0.20, 0.20, 1.0))
    # (2026-10-30) the loft had no light and no party. Bare bulbs on the
    # beams, the back bar's strip; the CONTRAILS ("A woman swings on a tire,
    # her dress leaving contrails of pink and orange light. One contrail
    # bounces all over the room. Charlie follows it to the bar, where it
    # lands in a shot glass") drawn as ribbons of light, the one that lands
    # arcing to the pink shot glass; the party round the room.
    for k, (bx, by) in enumerate(((45.4, 4.0), (49.0, 9.5), (52.6, 4.0))):
        make_cyl(f"Loft_Bulb_{k}_Cord", (bx, by, H - 0.90), 0.006, 0.80, (0.10, 0.10, 0.10, 1.0), segments=6)
        make_cyl(f"Loft_Bulb_{k}", (bx, by, H - 1.34), 0.06, 0.10, (1.0, 0.86, 0.60, 1.0), segments=10)
    make_box("Back_Bar_Light_Strip", (50.0, y1 - 0.10, 2.70), (7.6, 0.04, 0.05), (1.0, 0.60, 0.40, 1.0))
    def ribbon(name, pts, col, w=0.05):
        for j in range(len(pts) - 1):
            (ax, ay, az), (bx2, by2, bz) = pts[j], pts[j + 1]
            dx, dy, dz = bx2 - ax, by2 - ay, bz - az
            L = math.sqrt(dx * dx + dy * dy + dz * dz)
            make_rot_box(f"{name}_{j}", ((ax + bx2) / 2, (ay + by2) / 2, (az + bz) / 2), (L, w, w), col,
                         yaw=math.atan2(dy, dx), pitch=-math.atan2(dz, math.hypot(dx, dy)))
    PINK, ORANGE = (1.0, 0.46, 0.70, 1.0), (1.0, 0.62, 0.24, 1.0)
    sgx, sgy = 49.6, y1 - 0.08 - 1.4 - 0.10
    ribbon("Contrail_Pink", [(tx, ty, 1.1), (47.6, 7.4, 2.4), (46.6, 9.4, 3.0), (47.8, 11.2, 2.2), (sgx - 0.6, sgy - 0.4, 1.5), (sgx, sgy, 1.2)], PINK)
    ribbon("Contrail_Orange", [(tx, ty, 1.0), (50.6, 5.0, 1.9), (52.8, 4.4, 2.8), (54.6, 5.8, 3.2), (55.2, 8.2, 2.6)], ORANGE)
    ribbon("Contrail_Pink_Bounce", [(tx, ty, 1.2), (48.0, 4.2, 2.6), (45.2, 3.4, 3.4), (43.0, 5.0, 2.8), (42.4, 7.6, 3.4)], PINK, w=0.035)
    # the party: scale and staging (Charlie, Carrie are the VN's)
    for nm, x, y, hd, h, coat, dress, arms in (
            ("Party_Guest_0", 46.2, 10.8, math.pi * 1.0, 1.74, (0.20, 0.22, 0.28, 1.0), None, "front"),
            ("Party_Guest_1", 47.0, 11.0, math.pi * 1.05, 1.66, (0.70, 0.30, 0.44, 1.0), (0.70, 0.30, 0.44, 1.0), "front"),
            ("Party_Guest_2", 53.4, 10.6, math.pi * 0.9, 1.80, (0.40, 0.36, 0.30, 1.0), None, "folded"),
            ("Party_Guest_3", 55.6, 4.4, math.pi * 1.6, 1.70, (0.24, 0.40, 0.44, 1.0), (0.24, 0.40, 0.44, 1.0), "down"),
            ("Party_Guest_4", 51.8, 3.0, math.pi * 0.1, 1.78, (0.60, 0.56, 0.48, 1.0), None, "front"),
            ("Party_Guest_5", 43.4, 8.8, math.pi * 0.6, 1.68, (0.86, 0.62, 0.30, 1.0), (0.86, 0.62, 0.30, 1.0), "down")):
        make_standing_figure(nm, x, y, heading=hd, h=h, coat=coat, dress=dress, arms=arms)
    # outside the tall windows: the city at night
    for k in range(4):
        make_box(f"Loft_Across_Facade_{k}", (42.0 + k * 6.0, -16.0, 9.0), (5.6, 1.0, 18.0), (0.20, 0.20, 0.24, 1.0))
        for j in range(4):
            make_box(f"Loft_Across_Window_Glow_{k}_{j}", (40.6 + k * 6.0 + (j % 2) * 2.4, -15.48, 4.0 + (j // 2) * 3.4), (1.0, 0.04, 1.4),
                     ((1.0, 0.80, 0.50, 1.0), (0.14, 0.14, 0.16, 1.0))[(j + k) % 2])


def build_party_bathroom():
    """(2026-10-28, cc_3 "A Grungy Bathroom") off the loft's east wall:
    x 58..61.2, y 9..13. "Charlie leans up against the wall, looks at
    himself in the mirror. Someone has drawn a face with a sharpie marker.
    His reflection framed most peculiar." An after party's bathroom:
    graffiti over cracked tile, a bare bulb, a tub of ice and cans, a torn
    shower curtain, a towel on the floor."""
    bx0, bx1, by0, by1, bh = 58.0, 61.2, 9.0, 13.0, 2.6
    TILE = (0.70, 0.74, 0.68, 1.0)
    GRUNGE = {"wall": TILE, "baseboard": (0.36, 0.36, 0.32, 1.0)}
    make_floor("Bath_Floor", ((bx0 + bx1) / 2, (by0 + by1) / 2, 0.0), size_x=bx1 - bx0, size_y=by1 - by0,
               palette={"vinyl": (0.52, 0.50, 0.44, 1.0), "seam": (0.30, 0.28, 0.24, 1.0)})
    make_box("Bath_Ceil", ((bx0 + bx1) / 2, (by0 + by1) / 2, bh + 0.04), (bx1 - bx0 + 0.2, by1 - by0 + 0.2, 0.08), (0.62, 0.60, 0.54, 1.0))
    make_wall("Bath_Wall_E", (bx1, (by0 + by1) / 2, 0), length=by1 - by0, height=bh, thickness=T, axis='Y', palette=GRUNGE, baseboard_face_sign=-1)
    make_wall("Bath_Wall_N", ((bx0 + bx1) / 2, by1, 0), length=bx1 - bx0 + T, height=bh, thickness=T, axis='X', palette=GRUNGE, baseboard_face_sign=-1)
    make_wall("Bath_Wall_S", ((bx0 + bx1) / 2, by0, 0), length=bx1 - bx0 + T, height=bh, thickness=T, axis='X', palette=GRUNGE, baseboard_face_sign=+1)
    for k in range(9):
        make_box(f"Bath_Tile_Line_{k}", (bx1 - T / 2 - 0.006, (by0 + by1) / 2, 0.15 + k * 0.15), (0.004, by1 - by0, 0.008), (0.48, 0.50, 0.46, 1.0))
    # the sink and the mirror with the sharpie face
    sy = 11.8
    make_box("Bath_Sink_Basin", (bx1 - 0.32, sy, 0.84), (0.46, 0.56, 0.16), (0.90, 0.90, 0.86, 1.0))
    make_box("Bath_Sink_Pedestal", (bx1 - 0.30, sy, 0.40), (0.18, 0.20, 0.76), (0.88, 0.88, 0.84, 1.0))
    make_cyl("Bath_Sink_Faucet", (bx1 - 0.12, sy, 0.98), 0.02, 0.14, (0.66, 0.66, 0.68, 1.0), segments=8)
    make_box("Mirror_Glass", (bx1 - T / 2 - 0.01, sy, 1.55), (0.02, 0.62, 0.80), (0.70, 0.76, 0.78, 1.0))
    make_box("Mirror_Frame", (bx1 - T / 2 - 0.005, sy, 1.55), (0.015, 0.70, 0.88), (0.30, 0.28, 0.26, 1.0))
    # the sharpie face on the glass: two eyes, a nose, a mouth, a head outline
    INK = (0.06, 0.06, 0.08, 1.0)
    gx = bx1 - T / 2 - 0.022
    for s in (-1, 1):
        make_box(f"Mirror_Sharpie_Eye_{s:+d}", (gx, sy + s * 0.09, 1.66), (0.003, 0.05, 0.03), INK)
    make_box("Mirror_Sharpie_Nose", (gx, sy, 1.58), (0.003, 0.012, 0.07), INK)
    make_box("Mirror_Sharpie_Mouth", (gx, sy, 1.47), (0.003, 0.16, 0.012), INK)
    for k in range(10):
        a = k * math.tau / 10.0
        make_box(f"Mirror_Sharpie_Head_{k}", (gx, sy + math.cos(a) * 0.20, 1.56 + math.sin(a) * 0.26), (0.003, 0.05, 0.012), INK)
    # graffiti and stickers over the tile, the bare bulb
    r_cols = ((0.86, 0.20, 0.30, 1.0), (0.20, 0.30, 0.80, 1.0), (0.10, 0.10, 0.10, 1.0), (0.96, 0.80, 0.20, 1.0))
    for k in range(14):
        wy = by0 + 0.3 + (k * 0.73) % (by1 - by0 - 0.6)
        wz = 0.9 + (k * 0.37) % 1.4
        make_box(f"Bath_Graffiti_{k}", (bx1 - T / 2 - 0.004, wy, wz), (0.003, 0.18 + (k % 3) * 0.08, 0.05 + (k % 2) * 0.06), r_cols[k % 4])
    for k in range(8):
        make_box(f"Bath_Sticker_{k}", (bx0 + 0.4 + k * 0.33, by0 + T / 2 + 0.004, 1.2 + (k % 3) * 0.3), (0.10, 0.003, 0.08), r_cols[(k + 1) % 4])
    make_cyl("Bath_Bulb", ((bx0 + bx1) / 2, (by0 + by1) / 2, bh - 0.12), 0.05, 0.10, (1.0, 0.94, 0.78, 1.0), segments=10)
    make_cyl("Bath_Bulb_Socket", ((bx0 + bx1) / 2, (by0 + by1) / 2, bh - 0.03), 0.04, 0.06, (0.20, 0.20, 0.20, 1.0), segments=8)
    # the toilet, the roll, the plunger
    make_box("Bath_Toilet_Bowl", (bx1 - 0.40, 9.6, 0.22), (0.56, 0.38, 0.44), (0.90, 0.90, 0.86, 1.0))
    make_box("Bath_Toilet_Tank", (bx1 - 0.16, 9.6, 0.62), (0.18, 0.46, 0.40), (0.90, 0.90, 0.86, 1.0))
    make_box("Bath_Toilet_Lid_Up", (bx1 - 0.26, 9.6, 0.70), (0.04, 0.36, 0.42), (0.86, 0.86, 0.82, 1.0))
    make_cyl("Bath_TP_Roll", (bx1 - 0.10, 10.15, 0.70), 0.05, 0.10, (0.94, 0.94, 0.90, 1.0), segments=10, axis='Y')
    make_cyl("Bath_Plunger_Handle", (bx1 - 0.14, 10.4, 0.30), 0.012, 0.56, (0.50, 0.32, 0.18, 1.0), segments=6)
    make_cyl("Bath_Plunger_Cup", (bx1 - 0.14, 10.4, 0.04), 0.07, 0.08, (0.66, 0.14, 0.14, 1.0), segments=10)
    # the tub along the north wall: ice, cans, the torn curtain
    tx0, tx1 = bx0 + 0.25, bx1 - 0.15
    make_box("Bath_Tub", ((tx0 + tx1) / 2, by1 - 0.40, 0.26), (tx1 - tx0, 0.72, 0.52), (0.88, 0.88, 0.84, 1.0))
    make_box("Bath_Tub_Ice", ((tx0 + tx1) / 2, by1 - 0.40, 0.46), (tx1 - tx0 - 0.12, 0.60, 0.04), (0.84, 0.90, 0.94, 1.0))
    for k in range(12):
        make_cyl(f"Bath_Tub_Can_{k}", (tx0 + 0.20 + k * 0.22, by1 - 0.40 + ((k % 3) - 1) * 0.16, 0.52), 0.033, 0.12,
                 ((0.80, 0.10, 0.14, 1.0), (0.80, 0.80, 0.84, 1.0), (0.14, 0.30, 0.66, 1.0))[k % 3], segments=8)
    make_box("Bath_Curtain_Rod", ((tx0 + tx1) / 2, by1 - 0.78, 2.05), (tx1 - tx0, 0.02, 0.02), (0.66, 0.66, 0.68, 1.0))
    make_box("Bath_Curtain_Torn", (tx0 + 0.45, by1 - 0.78, 1.45), (0.80, 0.01, 1.20), (0.46, 0.66, 0.70, 1.0))
    # a towel on the floor, red cups, a bottle on the cistern
    make_box("Bath_Towel_Floor", (bx0 + 0.9, 10.2, 0.02), (0.70, 0.46, 0.04), (0.70, 0.52, 0.30, 1.0))
    for k in range(3):
        make_cyl(f"Bath_Red_Cup_{k}", (bx0 + 0.4 + k * 0.5, 9.4 + (k % 2) * 0.3, 0.06), 0.045, 0.12, (0.80, 0.12, 0.14, 1.0), segments=8)
    make_lathe("Bath_Bottle_On_Tank", (bx1 - 0.16, 9.45, 0.82), [(0.0, 0.0), (0.035, 0.0), (0.035, 0.18), (0.012, 0.24), (0.0, 0.24)],
               (0.30, 0.40, 0.24, 1.0), segments=8)


def build_sister_house():
    """x 80..92, y 0..8: a small worn house set back from the street, its
    yard; inside, the cramped main room and the laundry through a door."""
    H = 2.4
    hx0, hx1, hy0, hy1 = 82.0, 92.0, 2.0, 9.0
    make_floor("Sister_Floor", ((hx0 + hx1) / 2.0, (hy0 + hy1) / 2.0, 0.30), size_x=hx1 - hx0, size_y=hy1 - hy0,
               palette={"vinyl": (0.56, 0.50, 0.40, 1.0), "seam": (0.48, 0.42, 0.34, 1.0)})
    make_box("Sister_Crawlspace_Skirt", ((hx0 + hx1) / 2.0, (hy0 + hy1) / 2.0, 0.14), (hx1 - hx0, hy1 - hy0, 0.28), (0.40, 0.38, 0.34, 1.0))
    z0 = 0.30
    make_box("Sister_Ceil", ((hx0 + hx1) / 2.0, (hy0 + hy1) / 2.0, z0 + H + 0.04), (hx1 - hx0 + 0.4, hy1 - hy0 + 0.4, 0.08), (0.84, 0.82, 0.76, 1.0))
    # the walls (boxes, so they stand on the raised floor)
    def wbox(name, cx, cy, sx, sy, z_lo=z0, z_hi=z0 + H, col=(0.74, 0.70, 0.58, 1.0)):
        make_box(name, (cx, cy, (z_lo + z_hi) / 2.0), (sx, sy, z_hi - z_lo), col)
    ext = (0.70, 0.66, 0.56, 1.0)
    # S wall: the door at x 85 and a window at x 89
    wbox("Sister_Wall_S_A", 83.25, hy0, 2.5 + T, T, col=ext)
    wbox("Sister_Wall_S_B", 87.0, hy0, 3.1, T, col=ext)
    wbox("Sister_Wall_S_C", 91.2, hy0, 1.6 + T, T, col=ext)
    wbox("Sister_Wall_S_Door_Head", 85.0, hy0, 1.0, T, z_lo=z0 + 2.05, col=ext)
    wbox("Sister_Wall_S_Win_Below", 89.6, hy0, 1.2, T, z_hi=z0 + 0.9, col=ext)
    wbox("Sister_Wall_S_Win_Above", 89.6, hy0, 1.2, T, z_lo=z0 + 2.0, col=ext)
    wbox("Sister_Wall_N", (hx0 + hx1) / 2.0, hy1, hx1 - hx0 + T, T, col=ext)
    wbox("Sister_Wall_W", hx0, (hy0 + hy1) / 2.0, T, hy1 - hy0 - T, col=ext)
    wbox("Sister_Wall_E", hx1, (hy0 + hy1) / 2.0, T, hy1 - hy0 - T, col=ext)
    # the partition to the laundry/kitchen (x 88..92, y 5.5..9), its door
    wbox("Sister_Partition_W_A", 88.0, 6.1, 0.10, 1.2)
    wbox("Sister_Partition_W_B", 88.0, 8.35, 0.10, 1.3)
    wbox("Sister_Partition_W_Head", 88.0, 7.25, 0.10, 0.9, z_lo=z0 + 2.0)
    wbox("Sister_Partition_S", 90.0, 5.5, 4.0, 0.10)
    window_frame("Sister_Window", 'X', 89.6, hy0, z0 + 1.45, 1.2, 1.1, depth=T)
    make_box("Sister_Front_Door_Open", (85.0 - 0.46, hy0 + 0.10 + 0.42, z0 + 1.0), (0.04, 0.84, 2.0), (0.56, 0.46, 0.36, 1.0))
    make_gable("Sister_Roof", ((hx0 + hx1) / 2.0, (hy0 + hy1) / 2.0, z0 + H + 0.08 + 0.9), (hx1 - hx0 + 0.8, hy1 - hy0 + 0.8, 1.8),
               (0.30, 0.28, 0.26, 1.0), ridge_axis='X')
    make_box("Sister_Gutter_Sag", (87.0, hy0 - 0.42, z0 + H + 0.06), (10.4, 0.10, 0.08), (0.50, 0.50, 0.48, 1.0))
    # the front step, the worn walk, the patchy yard, the chain-link front
    make_box("Sister_Step", (85.0, hy0 - 0.45, 0.14), (1.2, 0.70, 0.28), (0.56, 0.54, 0.50, 1.0))
    make_box("Sister_Walk", (85.0, -3.0, 0.004), (1.0, 9.4, 0.008), (0.56, 0.54, 0.50, 1.0))
    make_box("Sister_Yard_Ground", (86.0, -1.0, -0.06), (40.0, 22.0, 0.12), (0.46, 0.44, 0.30, 1.0))
    for k in range(9):
        make_box(f"Yard_Bare_Patch_{k}", (81.0 + k * 1.3, -2.0 + (k % 3) * 1.4, 0.003), (0.9 + (k % 2) * 0.5, 0.7, 0.006),
                 (0.50, 0.42, 0.32, 1.0))
    make_box("Yard_Toy_Trike_Body", (88.6, -0.6, 0.22), (0.50, 0.20, 0.10), (0.80, 0.20, 0.18, 1.0))
    for s in (-1, 1):
        make_cyl(f"Yard_Toy_Trike_Wheel_{s:+d}", (88.6 + s * 0.22, -0.6, 0.11), 0.11, 0.04, (0.12, 0.12, 0.12, 1.0), axis='Y', segments=10)
    make_box("Yard_Old_Tire", (82.6, -0.8, 0.10), (0.60, 0.60, 0.20), (0.10, 0.10, 0.10, 1.0))
    for k in range(10):
        if k == 4:
            continue                # the gate's gap
        make_box(f"Front_Fence_Post_{k}", (80.6 + k * 1.1, -7.0, 0.50), (0.05, 0.05, 1.0), (0.56, 0.56, 0.58, 1.0))
    for zz in (0.95,):
        make_box(f"Front_Fence_Top_Rail_W", (82.25, -7.0, zz), (3.3, 0.03, 0.03), (0.56, 0.56, 0.58, 1.0))
        make_box(f"Front_Fence_Top_Rail_E", (88.85, -7.0, zz), (5.5, 0.03, 0.03), (0.56, 0.56, 0.58, 1.0))
    make_box("Street_Asphalt", (86.0, -12.0, -0.02), (60.0, 7.0, 0.04), (0.30, 0.30, 0.32, 1.0))
    # the neighbours either side, the same kind of house
    for k, x in enumerate((72.0, 100.0)):
        make_box(f"Neighbor_House_{k}", (x, 5.0, 1.4), (8.0, 7.0, 2.8), ((0.66, 0.70, 0.66, 1.0), (0.74, 0.66, 0.56, 1.0))[k])
        make_gable(f"Neighbor_Roof_{k}", (x, 5.0, 2.8 + 0.9), (8.6, 7.6, 1.8), (0.30, 0.28, 0.26, 1.0), ridge_axis='X')
    # inside: the cramped main room (couch, TV on a stand, toys, a laundry
    # basket), the dryer through the laundry door
    make_sofa("Sister_Couch", 84.0, 7.8, back="+Y", w=2.0, d=0.86, seats=2, color=(0.52, 0.40, 0.32, 1.0),
              cushion_col=(0.58, 0.46, 0.36, 1.0), arm="roll", leg_col=(0.30, 0.24, 0.18, 1.0), z0=z0,
              throw=(0.40, 0.46, 0.60, 1.0))                                    # pass 160: the kit sofa, a throw over its arm
    # pass 160: a lamp on a crate, curtains at the window, a frame on the wall,
    # a pile of folded laundry on the couch's arm end, the TV's remote
    make_box("Sister_Lamp_Crate", (82.4, 7.6, z0 + 0.22), (0.40, 0.40, 0.44), (0.50, 0.40, 0.28, 1.0))
    make_lamp("Sister_Lamp", 82.4, 7.6, base_z=z0 + 0.44, h=0.50)
    for e in (-1, 1):
        make_box(f"Sister_Curtain_{e:+d}", (89.6 + e * 0.68, hy0 + 0.16, z0 + 1.45), (0.24, 0.06, 1.30), (0.62, 0.52, 0.42, 1.0))
    make_cyl("Sister_Curtain_Rod", (89.6, hy0 + 0.16, z0 + 2.10), 0.015, 1.70, (0.30, 0.26, 0.20, 1.0), axis='X', segments=6)
    for e in (-1, 1):                          # the rod's brackets to the wall
        make_box(f"Sister_Curtain_Bracket_{e:+d}", (89.6 + e * 0.82, hy0 + 0.12, z0 + 2.10), (0.03, 0.10, 0.03), (0.30, 0.26, 0.20, 1.0))
    # (pass 167: both sat inside the wall's thickness — on its room face now)
    make_box("Sister_Frame", (85.6, hy1 - T / 2.0 - 0.026, z0 + 1.60), (0.44, 0.02, 0.34), (0.24, 0.20, 0.16, 1.0))
    make_box("Sister_Frame_Photo", (85.6, hy1 - T / 2.0 - 0.038, z0 + 1.60), (0.36, 0.004, 0.26), (0.72, 0.66, 0.56, 1.0))
    make_box("Sister_Laundry_Fold", (84.9, 7.8, z0 + 0.52), (0.30, 0.26, 0.14), (0.86, 0.84, 0.80, 1.0))
    make_box("Sister_Remote", (83.6, 5.6, z0 + 0.012), (0.05, 0.16, 0.02), (0.14, 0.14, 0.16, 1.0))
    make_box("Sister_TV_Stand", (82.5, 4.4, z0 + 0.30), (0.50, 0.90, 0.60), (0.40, 0.32, 0.24, 1.0))
    make_chamfer_box("Sister_TV", (82.5, 4.4, z0 + 0.82), (0.42, 0.50, 0.44), (0.16, 0.16, 0.16, 1.0), chamfer=0.03)
    make_box("Laundry_Basket", (86.6, 6.6, z0 + 0.18), (0.56, 0.40, 0.36), (0.86, 0.86, 0.84, 1.0))
    make_box("Laundry_Basket_Clothes", (86.6, 6.6, z0 + 0.40), (0.50, 0.34, 0.10), (0.40, 0.46, 0.60, 1.0))
    for k in range(5):
        make_box(f"Floor_Toy_{k}", (84.4 + k * 0.4, 5.2 + (k % 2) * 0.5, z0 + 0.06), (0.14, 0.14, 0.12),
                 ((0.90, 0.30, 0.20, 1.0), (0.30, 0.50, 0.90, 1.0), (0.96, 0.84, 0.30, 1.0))[k % 3])
    make_box("Sister_Rug_Worn", (84.6, 5.6, z0 + 0.004), (2.2, 1.6, 0.008), (0.50, 0.40, 0.34, 1.0))
    make_box("Dryer", (91.5, 8.4, z0 + 0.44), (0.66, 0.66, 0.88), (0.90, 0.90, 0.88, 1.0))
    make_box("Washer", (90.8, 8.4, z0 + 0.44), (0.66, 0.66, 0.88), (0.90, 0.90, 0.88, 1.0))
    make_box("Kitchen_Counter_Sister", (90.0, 5.6 + 0.32, z0 + 0.45), (2.8, 0.60, 0.90), (0.66, 0.60, 0.48, 1.0))
    make_box("Kitchen_Counter_Sister_Top", (90.0, 5.6 + 0.32, z0 + 0.92), (2.84, 0.62, 0.04), (0.82, 0.78, 0.70, 1.0))
    make_box("Dish_Pile", (89.4, 5.92, z0 + 1.00), (0.40, 0.30, 0.12), (0.86, 0.86, 0.84, 1.0))


def build_sister_2026_10():
    """DRAFT 3 of the sister's house (2026-10-30). Inside was a beige box with
    a couch and five toy cubes; the yard was a lawn. The text: "pretty low
    rent, in bad shape, maybe two bedrooms, tight and cramped, the yard in a
    sorry state"; two small kids; the fight over the socks and the dryer.
    INSIDE: cheap wood-grain paneling on the W and N walls; a water stain on
    the ceiling; a fist-sized hole in the partition; a playpen, a high chair,
    a box fan; clothes on the floor and the couch, a lone sock; the dryer
    piled with a load nobody folded; beer cans and an ashtray on the TV
    stand, a baby bottle; a box of diapers by the couch.
    YARD: weeds high along the house and the fence; trash bags by the side;
    a cracked kiddie pool; the screen door hanging off its top hinge.
    Draft 4 targets: the two bedrooms' doors, a kitchen table, the kids'
    drawings taped up, the TV on; outside the neighbours' fences, a car."""
    z0, H = 0.30, 2.4
    hx0, hx1, hy0, hy1 = 82.0, 92.0, 2.0, 9.0
    PANEL = (0.46, 0.32, 0.20, 1.0); GROOVE = (0.34, 0.22, 0.14, 1.0)
    wx = hx0 + T / 2.0 + 0.008
    make_box("Sister_Panel_W", (wx, (hy0 + hy1) / 2.0, z0 + H / 2.0), (0.012, hy1 - hy0 - T - 0.02, H - 0.02), PANEL)
    for k in range(int((hy1 - hy0 - T) / 0.40)):
        make_box(f"Sister_Panel_Stock_W_{k}", (wx + 0.007, hy0 + T / 2.0 + 0.2 + k * 0.40, z0 + H / 2.0), (0.003, 0.012, H - 0.04), GROOVE)
    ny = hy1 - T / 2.0 - 0.008
    make_box("Sister_Panel_N", ((hx0 + 88.0) / 2.0 + 0.02, ny, z0 + H / 2.0), (88.0 - hx0 - T - 0.10, 0.012, H - 0.02), PANEL)
    for k in range(int((88.0 - hx0 - T) / 0.40)):
        x = hx0 + T / 2.0 + 0.2 + k * 0.40
        if abs(x - 85.6) < 0.26:
            continue                               # the frame hangs there
        make_box(f"Sister_Panel_Stock_N_{k}", (x, ny - 0.007, z0 + H / 2.0), (0.012, 0.003, H - 0.04), GROOVE)
    # the stain on the ceiling, the hole in the partition
    # (a flat ring-marked stain on the plaster, not a lump: three discs, darker at the tide line)
    for k, (dx, dy, r, col) in enumerate(((0.0, 0.0, 0.58, (0.66, 0.58, 0.44, 1.0)), (0.08, -0.05, 0.44, (0.74, 0.68, 0.56, 1.0)),
                                          (0.30, 0.32, 0.26, (0.68, 0.60, 0.46, 1.0)))):
        make_cyl(f"Sister_Ceiling_Stain_{k}", (85.8 + dx, 5.2 + dy, z0 + H - 0.003 - 0.002 * k), r, 0.002, col, segments=20)
    make_blob("Sister_Wall_Hole", (87.94, 6.3, z0 + 1.15), 0.09, (0.16, 0.14, 0.12, 1.0), noise=0.45, seed=8, squash=0.15)
    # the playpen, the high chair, the box fan
    px, py = 86.7, 3.4
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_box(f"Playpen_Post_{sx:+d}_{sy:+d}", (px + sx * 0.48, py + sy * 0.48, z0 + 0.36), (0.04, 0.04, 0.72), (0.86, 0.86, 0.84, 1.0))
    for nm, (cx, cy, sx_, sy_) in {"S": (px, py - 0.48, 0.92, 0.01), "N": (px, py + 0.48, 0.92, 0.01),
                                   "W": (px - 0.48, py, 0.01, 0.92), "E": (px + 0.48, py, 0.01, 0.92)}.items():
        make_box(f"Playpen_Mesh_{nm}", (cx, cy, z0 + 0.40), (sx_, sy_, 0.60), (0.70, 0.74, 0.80, 0.35))
        make_box(f"Playpen_Rail_{nm}", (cx, cy, z0 + 0.71), (max(sx_, 0.03), max(sy_, 0.03), 0.03), (0.30, 0.46, 0.70, 1.0))
    make_box("Playpen_Pad", (px, py, z0 + 0.06), (0.92, 0.92, 0.04), (0.40, 0.56, 0.76, 1.0))
    make_blob("Playpen_Bear", (px + 0.2, py + 0.1, z0 + 0.14), 0.09, (0.62, 0.46, 0.30, 1.0), noise=0.15, seed=9, squash=1.0)
    hcx, hcy = 87.45, 5.05
    for sx in (-1, 1):
        for sy in (-1, 1):
            make_rot_box(f"High_Chair_Leg_{sx:+d}_{sy:+d}", (hcx + sx * 0.18, hcy + sy * 0.18, z0 + 0.38), (0.03, 0.03, 0.78),
                         (0.86, 0.84, 0.80, 1.0), roll=-sy * 0.12, pitch=sx * 0.12)
    make_box("High_Chair_Seat", (hcx, hcy, z0 + 0.78), (0.34, 0.34, 0.05), (0.86, 0.84, 0.80, 1.0))
    make_box("High_Chair_Back", (hcx, hcy + 0.16, z0 + 1.02), (0.32, 0.04, 0.44), (0.86, 0.84, 0.80, 1.0))
    make_box("High_Chair_Tray", (hcx, hcy - 0.26, z0 + 0.98), (0.44, 0.24, 0.03), (0.96, 0.80, 0.30, 1.0))
    make_box("Box_Fan", (82.45, 3.0, z0 + 0.28), (0.14, 0.52, 0.52), (0.84, 0.84, 0.82, 1.0))
    make_cyl("Box_Fan_Grille", (82.53, 3.0, z0 + 0.28), 0.22, 0.01, (0.40, 0.40, 0.42, 1.0), axis='X', segments=14)
    # clothes on the floor and on the couch, the lone sock
    for k, (x, y, r, col) in enumerate(((83.2, 6.6, 0.22, (0.30, 0.34, 0.50, 1.0)), (85.6, 7.3, 0.18, (0.80, 0.76, 0.70, 1.0)),
                                        (83.6, 7.75, 0.20, (0.60, 0.20, 0.20, 1.0)), (87.2, 7.9, 0.24, (0.40, 0.46, 0.36, 1.0)))):
        z = z0 + 0.47 if k == 2 else z0
        make_blob(f"Sister_Clothes_{k}", (x, y, z + r * 0.27), r, col, noise=0.35, seed=20 + k, squash=0.3)
    make_rot_box("Sister_Lone_Sock", (86.2, 4.6, z0 + 0.012), (0.08, 0.24, 0.02), (0.92, 0.92, 0.90, 1.0), yaw=0.7)
    # the dryer piled with the load nobody folded
    make_blob("Dryer_Pile", (91.5, 8.28, z0 + 0.88 + 0.10), 0.30, (0.70, 0.70, 0.74, 1.0), noise=0.3, seed=30, squash=0.4)
    make_blob("Dryer_Pile_2", (91.35, 8.3, z0 + 0.88 + 0.22), 0.20, (0.40, 0.46, 0.60, 1.0), noise=0.3, seed=31, squash=0.5)
    # the machines' faces (2026-10-30: two blank white boxes in the dryer insert):
    # the dryer's round door, the washer's lid seam, the backsplash and its knobs
    for nm, x in (("Dryer", 91.5), ("Washer", 90.8)):
        make_box(f"{nm}_Backsplash", (x, 8.4 + 0.27, z0 + 0.88 + 0.09), (0.66, 0.10, 0.18), (0.86, 0.86, 0.84, 1.0))
        for k in range(2):
            make_cyl(f"{nm}_Knob_{k}", (x - 0.18 + 0.36 * k, 8.4 + 0.215, z0 + 0.97), 0.025, 0.02, (0.30, 0.30, 0.32, 1.0), axis='Y', segments=10)
    make_cyl("Dryer_Door", (91.5, 8.4 - 0.335, z0 + 0.48), 0.21, 0.012, (0.70, 0.72, 0.72, 1.0), axis='Y', segments=20)
    make_cyl("Dryer_Door_Glass", (91.5, 8.4 - 0.343, z0 + 0.48), 0.15, 0.006, (0.30, 0.32, 0.34, 1.0), axis='Y', segments=20)
    make_box("Washer_Lid_Seam", (90.8, 8.32, z0 + 0.881), (0.56, 0.44, 0.002), (0.66, 0.66, 0.64, 1.0))
    # beer cans and an ashtray on the TV stand, a baby bottle; diapers
    for k in range(3):
        make_cyl(f"Sister_Beer_Can_{k}", (82.40 + 0.08 * k, 4.72 + 0.03 * k, z0 + 0.66), 0.033, 0.12, (0.80, 0.80, 0.84, 1.0), segments=10)
    make_cyl("Sister_Ashtray", (82.55, 3.98, z0 + 0.61), 0.07, 0.02, (0.40, 0.40, 0.42, 1.0), segments=12)
    make_cyl("Sister_Baby_Bottle", (82.40, 4.05, z0 + 0.67), 0.03, 0.14, (0.92, 0.92, 0.94, 1.0), segments=10)
    make_box("Sister_Diaper_Box", (85.4, 8.4, z0 + 0.20), (0.50, 0.30, 0.40), (0.40, 0.66, 0.90, 1.0))
    # -- the yard in its sorry state --
    for k in range(16):
        x = 82.2 + k * 0.62
        if 84.3 < x < 85.7:
            continue                               # the step and the walk
        h = 0.35 + 0.15 * ((k * 7) % 3)
        make_blob(f"Yard_Weed_Stock_{k}", (x, hy0 - 0.95 - 0.12 * (k % 2), h * 0.45), h * 0.55, (0.40, 0.44, 0.24, 1.0),
                  noise=0.4, seed=40 + k, squash=0.9)
    for k in range(10):
        x = 80.8 + k * 1.1
        if 84.5 < x < 85.6:
            continue
        make_blob(f"Yard_Fence_Weed_Stock_{k}", (x + 0.3, -6.75, 0.25), 0.30, (0.42, 0.44, 0.26, 1.0), noise=0.4, seed=60 + k, squash=0.8)
    for k, (x, y, r) in enumerate(((92.9, 3.4, 0.36), (93.1, 4.2, 0.32), (92.8, 4.9, 0.28))):
        make_blob(f"Yard_Trash_Bag_{k}", (x, y, r * 0.8), r, (0.10, 0.10, 0.12, 1.0), noise=0.25, seed=70 + k, squash=0.85)
    make_cyl("Yard_Kiddie_Pool", (90.4, -2.4, 0.10), 0.75, 0.20, (0.30, 0.60, 0.86, 1.0), segments=18)
    make_cyl("Yard_Kiddie_Pool_Water", (90.4, -2.4, 0.15), 0.70, 0.02, (0.44, 0.50, 0.40, 1.0), segments=18)
    make_rot_box("Screen_Door_Hanging", (84.42, hy0 - 0.30, z0 + 1.05), (0.84, 0.04, 2.0), (0.40, 0.42, 0.40, 0.55),
                 yaw=0.35, pitch=0.10)


def main():
    clear_scene()
    build_flat()
    build_party()
    build_party_bathroom()
    build_sister_house()
    build_sister_2026_10()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/carrie_city.glb"))
    print(f"\n[build_carrie_city] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
