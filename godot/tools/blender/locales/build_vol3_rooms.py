"""vol3_rooms — the single rooms of vol 3 that had only stand-ins (draft 1,
2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Each area stands far from the others (the VN camera sees 200 m).
  arcadeum (1991): "She kept the game in the back of her closet for a long
   time"; "WHAT LIES BEYOND in a regal cloudy blue script"; "an old, brand
   new never been opened game"            → june_closet (x 0)
  non stop flights / janessa / christine: Andy in Oregon, "sobbing mom on
   the phone", "a ticket already on hand", "emailing back and forth to Dad";
   that evening, "the live-in girlfriend" ("the little rented duplex college
   town shack", vol 2)                     → oregon_home_day, oregon_home_night
                                            (x 300)
  the coast / names in neon: "a photographer friend's home-studio
   overlooking the coast"; "We set-up in the bathroom."; "Lighting kits
   were unfurled and cameras set-up on tripods."; "the girl shivering in the
   stranger's bathtub"; "The bubbles ... mostly dispersed into a thin film"
                                          → coast_studio, coast_bathroom (x 600)
  names in neon: "several of the empty demo units, fully furnished and
   glossy like a magazine spread"; "trendy and urban hip"; Vancouver,
   Washington, autumn 2001                 → condo_demo_unit (x 900)
  tunnels (2003, Pasadena): "Dinner that night is Korean Barbecue."; "The
   restaurant looks like something out of a movie."; "the table is full of
   good uncooked food and kimchees of variety"; "the communal center over a
   hotpot"; "in tiny booth"                 → korean_bbq_table (x 1200)
  acceptable losses: "a pizza parlor tucked in the corner" of a strip mall
   on "a hot wet summer night", "a party room reserved for a baseball team in
   the back", "a projection screen", "steaming windows", "rain on the pane",
   "the film of water over asphalt"         → pizza_party_window (x 1500)
  passengers: "industrial downtown", "Green and pink light cut across body
   mist, artificial smoke, thick fog"; "those four walls"
                                          → warehouse_floor (x 1800)
  the catwalk (pulp) / yellow card: "a tube of glass slung out over
   nothing, a bridge from one tower to the next"; "red lights going one
   way, white lights coming"; "a vent breathes steam"; "Towers of lit
   windows"                                → catwalk_rail_night, catwalk_walk
                                            (x 2100; the tube at z 0, the city
                                            below it at z -40)
Blender: x east, y north, z up; Godot (x, z, -y).

DRAFT 2 targets: the slide/projected images as real pictures; June's
whole room; the condo's lobby (the cafe across from the gallery); the
hospital's other rooms moving in from vol 6's sets; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_chamfer_box, make_rot_box, make_blob, make_lathe, make_gable,
                             join_stock, export_glb)
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_table, make_lamp
from _props.vehicles import make_car

T = 0.16
TRIM = (0.88, 0.86, 0.80, 1.0)


def frame(name, axis, along, at, cz, w, h, depth=T, col=TRIM):
    for s in (-1, 1):
        if axis == 'X':
            make_box(f"{name}_Frame_Jamb_{s:+d}", (along + s * (w / 2.0 - 0.03), at, cz), (0.06, depth + 0.02, h), col)
        else:
            make_box(f"{name}_Frame_Jamb_{s:+d}", (at, along + s * (w / 2.0 - 0.03), cz), (depth + 0.02, 0.06, h), col)
    for zz in (cz - h / 2.0 + 0.03, cz + h / 2.0 - 0.03):
        if axis == 'X':
            make_box(f"{name}_Frame_Rail_{zz:.2f}", (along, at, zz), (w - 0.12, depth + 0.02, 0.06), col)
        else:
            make_box(f"{name}_Frame_Rail_{zz:.2f}", (at, along, zz), (depth + 0.02, w - 0.12, 0.06), col)


def room(prefix, x0, y0, w, d, H, pal, floor_cols, doors=None, wins=None, skip=()):
    """A plain room x0..x0+w, y0..y0+d: walls with openings per side
    ('S','N','W','E': [(along, cz, w, h)])."""
    doors = doors or {}
    wins = wins or {}
    make_floor(f"{prefix}_Floor", (x0 + w / 2.0, y0 + d / 2.0, 0.0), size_x=w, size_y=d,
               palette={"vinyl": floor_cols[0], "seam": floor_cols[1]})
    make_box(f"{prefix}_Ceil", (x0 + w / 2.0, y0 + d / 2.0, H + 0.04), (w + 0.3, d + 0.3, 0.08), (0.90, 0.90, 0.88, 1.0))
    for side, (anchor, length, axis, sign) in {"S": ((x0 + w / 2.0, y0, 0), w + T, 'X', +1), "N": ((x0 + w / 2.0, y0 + d, 0), w + T, 'X', -1),
                                               "W": ((x0, y0 + d / 2.0, 0), d - T, 'Y', +1), "E": ((x0 + w, y0 + d / 2.0, 0), d - T, 'Y', -1)}.items():
        if side in skip:
            continue                        # a wall another room already built
        ops = list(doors.get(side, [])) + list(wins.get(side, []))
        if ops:
            make_wall_with_openings(f"{prefix}_Wall_{side}", anchor, length=length, height=H, thickness=T, axis=axis, palette=pal,
                                    baseboard_face_sign=sign, openings=ops)
        else:
            make_wall(f"{prefix}_Wall_{side}", anchor, length=length, height=H, thickness=T, axis=axis, palette=pal, baseboard_face_sign=sign)
        for k, (al, cz, ww, hh) in enumerate(wins.get(side, [])):
            at = {"S": y0, "N": y0 + d, "W": x0, "E": x0 + w}[side]
            frame(f"{prefix}_Win_{side}{k}", 'X' if side in "SN" else 'Y', al, at, cz, ww, hh)


# ── A. June's room, 1991 (x 0..4, y 0..4) ────────────────────────────────
def build_june():
    pal = {"wall": (0.82, 0.76, 0.78, 1.0), "baseboard": (0.40, 0.34, 0.32, 1.0)}
    room("June", 0.0, 0.0, 4.0, 4.2, 2.5, pal, ((0.56, 0.50, 0.50, 1.0), (0.48, 0.42, 0.42, 1.0)),
         doors={"S": [(0.6, 1.0, 0.80, 2.0)], "N": [(2.6, 1.05, 1.6, 2.1)]}, wins={"W": [(2.4, 1.45, 1.1, 1.2)]})
    make_box("June_Window_Sky_Night", (-0.45, 2.4, 1.45), (0.04, 1.6, 1.6), (0.10, 0.12, 0.18, 1.0))
    # the closet behind its opening (x 1.8..3.4, y 4.2..5.0), doors slid open
    make_box("June_Closet_Floor", (2.6, 4.6, 0.004), (1.6, 0.8, 0.008), (0.50, 0.44, 0.42, 1.0))
    make_box("June_Closet_Back", (2.6, 5.08, 1.25), (1.9, 0.16, 2.5), (0.80, 0.74, 0.76, 1.0))
    for s in (-1, 1):
        make_box(f"June_Closet_Side_{s:+d}", (2.6 + s * 0.88, 4.64, 1.25), (0.16, 0.88, 2.5), (0.80, 0.74, 0.76, 1.0))
    make_box("June_Closet_Ceil", (2.6, 4.64, 2.54), (1.9, 0.88, 0.08), (0.90, 0.90, 0.88, 1.0))
    make_box("June_Closet_Sliding_Panel", (2.0, 4.26, 1.05), (0.80, 0.04, 2.1), (0.86, 0.84, 0.80, 1.0))
    make_box("June_Closet_Rod", (2.6, 4.66, 1.85), (1.6, 0.03, 0.03), (0.70, 0.70, 0.72, 1.0))
    for k in range(8):
        make_box(f"June_Closet_Clothes_Hang_{k}", (1.95 + k * 0.18, 4.66, 1.44), (0.05, 0.46, 0.80),
                 ((0.30, 0.40, 0.70, 1.0), (0.80, 0.40, 0.50, 1.0), (0.20, 0.20, 0.24, 1.0), (0.86, 0.84, 0.70, 1.0))[k % 4])
    make_box("June_Closet_Shelf", (2.6, 4.66, 2.10), (1.6, 0.70, 0.03), (0.86, 0.84, 0.80, 1.0))
    for k in range(3):
        make_box(f"June_Closet_Shelf_Box_{k}", (2.1 + k * 0.5, 4.70, 2.26), (0.40, 0.40, 0.28), (0.66, 0.54, 0.38, 1.0))
    # the sealed box at the back, the blue script on its face
    make_box("What_Lies_Beyond_Box", (2.9, 4.82, 0.158), (0.36, 0.08, 0.30), (0.20, 0.22, 0.36, 1.0))
    make_box("What_Lies_Beyond_Script", (2.9, 4.775, 0.20), (0.26, 0.004, 0.08), (0.56, 0.74, 0.96, 1.0))
    make_box("What_Lies_Beyond_Shrink_Wrap_Sheen", (2.9, 4.778, 0.08), (0.30, 0.002, 0.04), (0.80, 0.86, 0.90, 1.0))
    for k in range(3):
        make_box(f"June_Closet_Shoe_{k}", (2.1 + k * 0.28, 4.5, 0.05), (0.12, 0.26, 0.10), (0.30, 0.24, 0.20, 1.0))
    # the room: the bed, the desk with a cassette player and a lamp, a poster
    make_bed("June_Bed", 4.0 - 0.08 - 0.50, 1.6, head="+X", w=0.95, d=1.95, made=False, blanket_col=(0.60, 0.40, 0.56, 1.0))
    make_table("June_Desk", 0.08 + 0.35, 1.2, w=0.70, d=1.1, h=0.74, wood=(0.56, 0.46, 0.36, 1.0))
    make_lamp("June_Desk_Lamp", 0.30, 1.6, base_z=0.74, h=0.46)
    make_box("June_Cassette_Player", (0.45, 0.9, 0.80), (0.30, 0.18, 0.10), (0.20, 0.20, 0.22, 1.0))
    make_box("June_Poster_Mounted", (2.2, 0.08 + 0.004, 1.6), (0.60, 0.006, 0.80), (0.30, 0.50, 0.70, 1.0))


# ── B. the Oregon home (x 300..308, y 0..6) ─────────────────────────────
def build_oregon():
    x0 = 300.0
    pal = {"wall": (0.80, 0.78, 0.70, 1.0), "baseboard": (0.40, 0.34, 0.28, 1.0)}
    room("Oregon", x0, 0.0, 8.0, 6.0, 2.4, pal, ((0.46, 0.40, 0.34, 1.0), (0.40, 0.34, 0.28, 1.0)),
         doors={"S": [(x0 + 1.0, 1.0, 0.86, 2.0)]}, wins={"N": [(x0 + 2.4, 1.45, 1.4, 1.1), (x0 + 6.4, 1.45, 1.2, 1.1)]})
    make_box("Oregon_Front_Door", (x0 + 1.0, 0.0, 1.0), (0.84, 0.04, 2.0), (0.50, 0.40, 0.30, 1.0))
    # the partition: the main room x 300..304.6, the bedroom x 304.6..308
    make_wall_with_openings("Oregon_Partition", (x0 + 4.6, 3.0, 0), length=6.0 - T, height=2.4, thickness=0.10, axis='Y', palette=pal,
                            baseboard_face_sign=-1, openings=[(1.2, 1.0, 0.80, 2.0)])
    # the bedroom door swung back flat to the partition (out of both views)
    make_box("Oregon_Bedroom_Door_Open", (x0 + 4.6 + 0.07, 1.2 + 0.41 + 0.40, 1.0), (0.04, 0.80, 2.0), (0.66, 0.58, 0.46, 1.0))
    for k, x in enumerate((x0 + 2.4, x0 + 6.4)):
        make_box(f"Oregon_Window_Sky_Day_{k}__oregon_home_day", (x, 6.5, 1.45), (1.8, 0.04, 1.6), (0.70, 0.76, 0.80, 1.0))
        make_box(f"Oregon_Window_Sky_Night_{k}__oregon_home_night", (x, 6.5, 1.45), (1.8, 0.04, 1.6), (0.06, 0.07, 0.10, 1.0))
    # the main room: the wall phone, the table with the papers and the
    # ticket, the computer, a thrift couch, two people's things
    make_box("Wall_Phone_Mounted", (x0 + 0.08 + 0.04, 3.4, 1.40), (0.08, 0.20, 0.24), (0.86, 0.84, 0.78, 1.0))
    make_box("Wall_Phone_Cord_Hang", (x0 + 0.08 + 0.10, 3.4, 1.05), (0.02, 0.02, 0.50), (0.86, 0.84, 0.78, 1.0))
    make_table("Oregon_Table", x0 + 2.0, 2.2, w=1.2, d=0.8, h=0.74, wood=(0.50, 0.40, 0.30, 1.0))
    for k, (dx, yaw) in enumerate(((-0.75, -math.pi / 2.0), (0.75, math.pi / 2.0))):
        make_chair(f"Oregon_Chair_{k}", x0 + 2.0 + dx, 2.2, yaw=yaw, wood=(0.50, 0.40, 0.30, 1.0))
    make_box("Oregon_Papers_Pile", (x0 + 1.8, 2.1, 0.76), (0.30, 0.24, 0.04), (0.92, 0.92, 0.88, 1.0))
    make_box("Oregon_Plane_Ticket", (x0 + 2.2, 2.3, 0.743), (0.20, 0.08, 0.004), (0.86, 0.80, 0.70, 1.0))
    make_box("Oregon_Computer_Desk", (x0 + 0.08 + 0.35, 5.0, 0.37), (0.70, 1.2, 0.74), (0.40, 0.34, 0.28, 1.0))
    make_chamfer_box("Oregon_CRT", (x0 + 0.08 + 0.35, 5.0, 0.95), (0.42, 0.42, 0.40), (0.82, 0.80, 0.74, 1.0), chamfer=0.03)
    make_box("Oregon_CRT_Screen", (x0 + 0.08 + 0.35 + 0.212, 5.0, 0.96), (0.004, 0.32, 0.26), (0.30, 0.40, 0.56, 1.0))
    make_box("Oregon_Couch_Base", (x0 + 2.4, 5.5, 0.22), (2.0, 0.84, 0.44), (0.46, 0.34, 0.30, 1.0))
    make_box("Oregon_Couch_Back", (x0 + 2.4, 5.86, 0.64), (2.0, 0.16, 0.42), (0.46, 0.34, 0.30, 1.0))
    make_box("Oregon_Two_Coats_Hook_Hang", (x0 + 1.9, 0.11, 1.40), (0.60, 0.06, 0.70), (0.30, 0.30, 0.40, 1.0))
    # the bedroom: the bed, the lamp, her bag half-packed for a trip she
    # won't take, two people's clothes
    make_bed("Oregon_Bed", x0 + 8.0 - 0.08 - 0.75, 3.4, head="+X", w=1.4, d=2.0, made=False, blanket_col=(0.44, 0.30, 0.34, 1.0))
    make_box("Oregon_Nightstand", (x0 + 8.0 - 0.08 - 0.22, 5.2, 0.30), (0.40, 0.40, 0.60), (0.44, 0.34, 0.26, 1.0))
    make_lamp("Oregon_Bed_Lamp", x0 + 8.0 - 0.08 - 0.22, 5.2, base_z=0.60, h=0.50)
    make_chamfer_box("Oregon_Duffel_Half_Packed", (x0 + 6.6, 0.6, 0.18), (0.70, 0.36, 0.34), (0.30, 0.34, 0.26, 1.0), chamfer=0.10)
    make_box("Oregon_Duffel_Clothes_Spill", (x0 + 6.6, 0.6, 0.37), (0.50, 0.26, 0.06), (0.60, 0.50, 0.66, 1.0))
    make_box("Oregon_Clothes_Floor", (x0 + 5.4, 4.6, 0.03), (0.60, 0.40, 0.06), (0.30, 0.30, 0.36, 1.0))
    make_box("Oregon_Dresser", (x0 + 4.6 + 0.05 + 0.25, 4.8, 0.48), (0.50, 1.00, 0.96), (0.50, 0.40, 0.30, 1.0))


# ── C. the coast home-studio and its bathroom (x 600..612, y 0..8) ──────
def build_coast_studio():
    x0 = 600.0
    pal = {"wall": (0.90, 0.90, 0.88, 1.0), "baseboard": (0.60, 0.58, 0.54, 1.0)}
    room("Studio", x0, 0.0, 9.0, 8.0, 3.4, pal, ((0.62, 0.52, 0.40, 1.0), (0.56, 0.46, 0.34, 1.0)),
         doors={"E": [(5.6, 1.0, 0.86, 2.0)]}, wins={"W": [(1.6, 1.7, 2.2, 2.4), (4.0, 1.7, 2.2, 2.4), (6.4, 1.7, 2.2, 2.4)]})
    # the bathroom E of the studio (x 609..613, y 3.5..8)
    pal_b = {"wall": (0.86, 0.90, 0.92, 1.0), "baseboard": (0.70, 0.72, 0.74, 1.0)}
    room("Bath", x0 + 9.0, 3.5, 4.0, 4.5, 2.6, pal_b, ((0.80, 0.82, 0.82, 1.0), (0.72, 0.74, 0.74, 1.0)), skip=("W",))
    make_box("Bath_Door_Open", (x0 + 9.0 + 0.06 + 0.40, 5.6 - 0.43, 1.0), (0.80, 0.04, 2.0), (0.86, 0.84, 0.80, 1.0))
    # the coast out the W windows: the bluff, the sea, the sky (inside 200 m)
    make_box("Coast_Bluff_Ground", (x0 - 20.0, 4.0, -0.10), (40.0, 80.0, 0.20), (0.36, 0.40, 0.28, 1.0))
    make_rot_box("Coast_Bluff_Face", (x0 - 42.0, 4.0, -8.0), (6.0, 80.0, 18.0), (0.36, 0.32, 0.28, 1.0), pitch=0.35)
    make_box("Coast_Sea_Water", (x0 - 110.0, 4.0, -14.0), (130.0, 300.0, 0.04), (0.34, 0.46, 0.52, 1.0))
    make_box("Coast_Sky_W", (x0 - 180.0, 4.0, 40.0), (0.2, 400.0, 140.0), (0.74, 0.82, 0.90, 1.0))
    for k in range(5):
        make_blob(f"Coast_Shrub_Plant_{k}", (x0 - 6.0 - (k % 3) * 4.0, -8.0 + k * 5.0, 0.3), 0.9, (0.28, 0.36, 0.22, 1.0), noise=0.4, seed=k)
    # the studio: the seamless backdrop on its stands, his own lights, the
    # crew's cases open, a light stand on its way to the bathroom
    make_box("Backdrop_Roll_Bar", (x0 + 4.5, 7.6, 2.8), (3.0, 0.06, 0.06), (0.30, 0.30, 0.32, 1.0))
    for s in (-1, 1):
        make_box(f"Backdrop_Stand_{s:+d}", (x0 + 4.5 + s * 1.5, 7.6, 1.42), (0.04, 0.04, 2.84), (0.30, 0.30, 0.32, 1.0))
    make_box("Backdrop_Paper_Hang", (x0 + 4.5, 7.58, 1.42), (2.8, 0.01, 2.76), (0.84, 0.82, 0.78, 1.0))
    make_box("Backdrop_Paper_Sweep", (x0 + 4.5, 6.9, 0.006), (2.8, 1.4, 0.008), (0.84, 0.82, 0.78, 1.0))
    for k, (x, y) in enumerate(((x0 + 2.6, 5.6), (x0 + 6.6, 5.8))):
        make_cyl(f"Studio_Light_{k}_Pole", (x, y, 0.95), 0.02, 1.9, (0.20, 0.20, 0.22, 1.0), segments=6)
        make_cyl(f"Studio_Light_{k}_Base", (x, y, 0.02), 0.30, 0.04, (0.20, 0.20, 0.22, 1.0), segments=10)
        make_chamfer_box(f"Studio_Light_{k}_Softbox", (x, y, 2.05), (0.60, 0.30, 0.60), (0.92, 0.92, 0.90, 1.0), chamfer=0.04)
    for k in range(3):
        make_box(f"Crew_Case_Open_{k}", (x0 + 6.6 + k * 0.6, 1.4, 0.12), (0.50, 0.36, 0.24), (0.14, 0.14, 0.16, 1.0))
        make_box(f"Crew_Case_Lid_{k}", (x0 + 6.6 + k * 0.6, 1.60, 0.36), (0.50, 0.04, 0.30), (0.14, 0.14, 0.16, 1.0))
    make_rot_box("Light_Stand_Carried", (x0 + 6.3, 3.0, 0.80), (0.04, 0.04, 1.70), (0.20, 0.20, 0.22, 1.0), pitch=0.35)
    make_cyl("Light_Stand_Carried_Base", (x0 + 6.0, 3.0, 0.02), 0.20, 0.04, (0.20, 0.20, 0.22, 1.0), segments=8)
    make_box("Studio_Low_Table", (x0 + 3.4, 2.6, 0.20), (1.2, 0.60, 0.40), (0.30, 0.26, 0.22, 1.0))
    make_box("Studio_Sofa_Base", (x0 + 3.4, 1.0, 0.22), (2.2, 0.86, 0.44), (0.70, 0.66, 0.60, 1.0))
    make_box("Studio_Sofa_Back", (x0 + 3.4, 0.62, 0.64), (2.2, 0.16, 0.42), (0.70, 0.66, 0.60, 1.0))
    for k in range(3):
        make_box(f"Studio_Print_Mounted_{k}", (x0 + 8.92 - 0.004, 1.4 + k * 1.1, 1.6), (0.006, 0.80, 0.60), ((0.20, 0.20, 0.22, 1.0), (0.86, 0.84, 0.80, 1.0))[k % 2])
    # the bathroom: the tub with its thin film of bubbles, the crew's kit
    bx0, by0 = x0 + 9.0, 3.5
    make_box("Bath_Tub_Body", (bx0 + 2.0, by0 + 4.5 - 0.08 - 0.40, 0.28), (1.7, 0.80, 0.56), (0.96, 0.96, 0.94, 1.0))
    make_box("Bath_Tub_Water", (bx0 + 2.0, by0 + 4.5 - 0.08 - 0.40, 0.50), (1.5, 0.62, 0.01), (0.66, 0.80, 0.86, 1.0))
    for k in range(9):
        make_blob(f"Bath_Bubble_Film_Foam_{k}", (bx0 + 1.4 + (k % 5) * 0.28, by0 + 3.85 + (k // 5) * 0.22, 0.51), 0.05, (0.94, 0.96, 0.98, 1.0),
                  noise=0.2, seed=k, squash=0.3)
    make_box("Bath_Sink_Vanity", (bx0 + 4.0 - 0.08 - 0.28, by0 + 1.2, 0.42), (0.56, 1.0, 0.84), (0.60, 0.50, 0.40, 1.0))
    make_box("Bath_Mirror_Mounted", (bx0 + 4.0 - 0.08 - 0.012, by0 + 1.2, 1.55), (0.02, 0.90, 0.80), (0.70, 0.76, 0.80, 1.0))
    make_box("Bath_Towel_Bar_Mounted", (bx0 + 0.08 + 0.06, by0 + 2.0, 1.20), (0.04, 0.70, 0.03), (0.70, 0.70, 0.72, 1.0))
    make_box("Bath_Towel_Hang", (bx0 + 0.08 + 0.09, by0 + 2.0, 0.92), (0.02, 0.50, 0.56), (0.86, 0.80, 0.70, 1.0))
    for k, (x, y) in enumerate(((bx0 + 0.9, by0 + 2.4), (bx0 + 3.2, by0 + 2.2))):
        make_cyl(f"Kit_Light_{k}_Pole", (x, y, 0.85), 0.02, 1.7, (0.20, 0.20, 0.22, 1.0), segments=6)
        make_cyl(f"Kit_Light_{k}_Base", (x, y, 0.02), 0.26, 0.04, (0.20, 0.20, 0.22, 1.0), segments=8)
        make_chamfer_box(f"Kit_Light_{k}_Head_Glow", (x, y, 1.80), (0.24, 0.24, 0.20), (0.96, 0.94, 0.86, 1.0), chamfer=0.03)
    tx, ty = bx0 + 1.8, by0 + 0.9
    for k in range(3):
        a = k * 2.0 * math.pi / 3.0
        make_rot_box(f"Tripod_Leg_{k}", (tx + 0.18 * math.cos(a), ty + 0.18 * math.sin(a), 0.62), (0.02, 0.02, 1.26), (0.14, 0.14, 0.16, 1.0),
                     roll=0.15 * math.sin(a), pitch=-0.15 * math.cos(a))
    make_cyl("Tripod_Collar", (tx, ty, 1.22), 0.10, 0.06, (0.14, 0.14, 0.16, 1.0), segments=10)
    make_box("Tripod_Head", (tx, ty, 1.28), (0.10, 0.10, 0.06), (0.14, 0.14, 0.16, 1.0))
    make_chamfer_box("Tape_Camera", (tx, ty + 0.05, 1.38), (0.14, 0.32, 0.16), (0.16, 0.16, 0.18, 1.0), chamfer=0.02)


# ── D. the condo demo unit, autumn 2001 (x 900..910, y 0..8) ────────────
def build_condo():
    x0 = 900.0
    pal = {"wall": (0.94, 0.94, 0.92, 1.0), "baseboard": (0.86, 0.86, 0.84, 1.0)}
    room("Condo", x0, 0.0, 10.0, 8.0, 2.9, pal, ((0.56, 0.42, 0.28, 1.0), (0.50, 0.38, 0.26, 1.0)),
         doors={"S": [(x0 + 1.0, 1.05, 0.96, 2.1)]}, wins={"N": [(x0 + 2.5, 1.45, 2.4, 2.5), (x0 + 5.0, 1.45, 2.4, 2.5), (x0 + 7.5, 1.45, 2.4, 2.5)]})
    # the staged room: the sectional, the low table with its styled pieces,
    # the rug, the art, the island in white gloss, the dining set
    make_box("Condo_Sectional_Base", (x0 + 3.0, 5.0, 0.22), (3.0, 0.90, 0.44), (0.40, 0.40, 0.42, 1.0))
    make_box("Condo_Sectional_Back", (x0 + 3.0, 4.6, 0.62), (3.0, 0.16, 0.40), (0.40, 0.40, 0.42, 1.0))
    make_box("Condo_Sectional_Chaise", (x0 + 1.95, 5.9, 0.22), (0.90, 1.0, 0.44), (0.40, 0.40, 0.42, 1.0))
    make_box("Condo_Coffee_Table", (x0 + 3.2, 6.3, 0.20), (1.4, 0.70, 0.40), (0.86, 0.84, 0.80, 1.0))
    make_cyl("Condo_Styled_Vase", (x0 + 2.8, 6.3, 0.52), 0.07, 0.24, (0.16, 0.16, 0.18, 1.0), segments=12)
    make_box("Condo_Styled_Books", (x0 + 3.5, 6.3, 0.43), (0.30, 0.22, 0.06), (0.86, 0.30, 0.24, 1.0))
    make_box("Condo_Rug", (x0 + 3.2, 5.8, 0.004), (3.6, 2.6, 0.008), (0.80, 0.78, 0.72, 1.0))
    for k in range(2):
        make_box(f"Condo_Art_Mounted_{k}", (x0 + 0.08 + 0.004, 2.4 + k * 2.6, 1.6), (0.006, 1.6, 1.0), ((0.86, 0.40, 0.20, 1.0), (0.20, 0.40, 0.60, 1.0))[k])
    make_box("Condo_Island", (x0 + 7.6, 3.0, 0.46), (2.4, 0.90, 0.92), (0.96, 0.96, 0.94, 1.0))
    make_box("Condo_Island_Top", (x0 + 7.6, 3.0, 0.94), (2.5, 1.0, 0.04), (0.30, 0.30, 0.32, 1.0))
    for k in range(3):
        make_cyl(f"Condo_Bar_Stool_Seat_{k}", (x0 + 6.8 + k * 0.8, 2.3, 0.70), 0.18, 0.05, (0.20, 0.20, 0.22, 1.0), segments=12)
        make_cyl(f"Condo_Bar_Stool_Post_{k}", (x0 + 6.8 + k * 0.8, 2.3, 0.34), 0.03, 0.68, (0.80, 0.80, 0.82, 1.0), segments=8)
        make_cyl(f"Condo_Bar_Stool_Foot_{k}", (x0 + 6.8 + k * 0.8, 2.3, 0.01), 0.20, 0.02, (0.80, 0.80, 0.82, 1.0), segments=12)
        make_cyl(f"Condo_Pendant_Glow_{k}", (x0 + 6.8 + k * 0.8, 3.0, 2.30), 0.12, 0.20, (0.98, 0.92, 0.80, 1.0), segments=12)
        make_box(f"Condo_Pendant_Cord_{k}", (x0 + 6.8 + k * 0.8, 3.0, 2.65), (0.01, 0.01, 0.50), (0.20, 0.20, 0.20, 1.0))
    make_box("Condo_Kitchen_Run", (x0 + 7.6, 0.08 + 0.32, 0.46), (3.0, 0.64, 0.92), (0.96, 0.96, 0.94, 1.0))
    # the film crew's light stand at the edge: it is their set
    make_cyl("Crew_Light_Pole", (x0 + 9.2, 6.8, 1.0), 0.02, 2.0, (0.20, 0.20, 0.22, 1.0), segments=6)
    make_cyl("Crew_Light_Base", (x0 + 9.2, 6.8, 0.02), 0.30, 0.04, (0.20, 0.20, 0.22, 1.0), segments=10)
    make_chamfer_box("Crew_Light_Head_Glow", (x0 + 9.2, 6.8, 2.10), (0.30, 0.30, 0.30), (0.96, 0.94, 0.86, 1.0), chamfer=0.04)
    # the city beyond the glass (a river town, low; inside 200 m)
    for k in range(10):
        make_box(f"Condo_City_Block_{k}", (x0 - 40.0 + k * 14.0, 60.0 + (k % 3) * 20.0, -14.0 + (6 + (k % 4) * 4) / 2.0),
                 (10.0, 10.0, 6 + (k % 4) * 4), ((0.62, 0.60, 0.58, 1.0), (0.52, 0.54, 0.56, 1.0))[k % 2])
    make_box("Condo_City_Ground", (x0 + 5.0, 70.0, -14.1), (200.0, 120.0, 0.2), (0.40, 0.42, 0.40, 1.0))
    make_box("Condo_River_Water", (x0 + 5.0, 140.0, -14.0), (200.0, 30.0, 0.04), (0.44, 0.54, 0.60, 1.0))
    make_box("Condo_Sky_N", (x0 + 5.0, 170.0, 40.0), (300.0, 0.2, 140.0), (0.76, 0.82, 0.88, 1.0))
    make_box("Condo_Tower_Below", (x0 + 5.0, 4.0, -7.1), (12.0, 10.0, 14.0), (0.72, 0.72, 0.74, 1.0))


# ── E. the Korean barbecue, Pasadena 2003 (x 1200..1214, y 0..10) ──────
def build_bbq():
    x0 = 1200.0
    pal = {"wall": (0.40, 0.30, 0.24, 1.0), "baseboard": (0.24, 0.18, 0.14, 1.0)}
    room("BBQ", x0, 0.0, 14.0, 10.0, 3.2, pal, ((0.30, 0.22, 0.16, 1.0), (0.26, 0.18, 0.12, 1.0)),
         wins={"S": [(x0 + 4.0, 1.5, 2.6, 1.8), (x0 + 10.0, 1.5, 2.6, 1.8)]})
    for k in range(20):
        make_box(f"BBQ_Wall_Slat_Stock_{k}", (x0 + 0.5 + k * 0.7, 10.0 - 0.08 - 0.02, 1.6), (0.10, 0.04, 3.0), (0.56, 0.40, 0.26, 1.0))
    make_box("BBQ_Window_Sky_Night", (x0 + 7.0, -0.6, 1.5), (12.0, 0.04, 2.4), (0.04, 0.05, 0.08, 1.0))
    # the booths: a run along the N wall, each table with its grill at the
    # centre, a hood and its pipe above; the group's booth set with dishes
    for b in range(4):
        cx = x0 + 2.0 + b * 3.2
        cy = 10.0 - 0.08 - 1.0
        make_box(f"Booth_{b}_Table", (cx, cy, 0.72), (1.4, 0.90, 0.06), (0.22, 0.16, 0.12, 1.0))
        make_box(f"Booth_{b}_Table_Base", (cx, cy, 0.35), (0.20, 0.20, 0.70), (0.14, 0.12, 0.10, 1.0))
        for s in (-1, 1):
            make_box(f"Booth_{b}_Bench_{s:+d}", (cx + s * 1.0, cy, 0.24), (0.50, 0.90, 0.48), (0.50, 0.14, 0.12, 1.0))
            make_box(f"Booth_{b}_Bench_Back_{s:+d}", (cx + s * 1.22, cy, 0.76), (0.10, 0.90, 0.60), (0.50, 0.14, 0.12, 1.0))
        make_cyl(f"Booth_{b}_Grill", (cx, cy, 0.77), 0.22, 0.04, (0.30, 0.30, 0.32, 1.0), segments=16)
        make_cyl(f"Booth_{b}_Hood", (cx, cy, 1.90), 0.26, 0.24, (0.66, 0.66, 0.68, 1.0), segments=14)
        make_cyl(f"Booth_{b}_Hood_Pipe", (cx, cy, 2.61), 0.08, 1.18, (0.66, 0.66, 0.68, 1.0), segments=10)
    gx, gy = x0 + 2.0, 10.0 - 0.08 - 1.0
    for k in range(12):
        a = k * 2.0 * math.pi / 12.0
        make_cyl(f"Banchan_Bowl_{k}", (gx + 0.48 * math.cos(a) * 1.2, gy + 0.30 * math.sin(a), 0.77), 0.05, 0.04,
                 ((0.86, 0.30, 0.20, 1.0), (0.40, 0.56, 0.24, 1.0), (0.92, 0.86, 0.60, 1.0))[k % 3], segments=10)
    for k in range(3):
        make_box(f"Raw_Meat_Plate_{k}", (gx - 0.36 + k * 0.36, gy - 0.30, 0.765), (0.24, 0.16, 0.03), (0.86, 0.46, 0.44, 1.0))
    make_box("Empty_Plates_Stack", (gx + 0.56, gy + 0.32, 0.79), (0.22, 0.22, 0.08), (0.94, 0.94, 0.92, 1.0))
    for k in range(4):
        make_blob(f"Grill_Steam_Cloud_{k}", (gx + 0.02 * k, gy, 0.98 + k * 0.20), 0.10 + k * 0.03, (0.86, 0.86, 0.86, 1.0), noise=0.3, seed=k)
    # other tables in the room's middle, other diners' places set
    for k in range(3):
        make_table(f"BBQ_Floor_Table_{k}", x0 + 3.5 + k * 3.6, 4.0, w=1.2, d=0.9, h=0.74, wood=(0.22, 0.16, 0.12, 1.0))
        make_cyl(f"BBQ_Floor_Table_{k}_Grill", (x0 + 3.5 + k * 3.6, 4.0, 0.765), 0.20, 0.03, (0.30, 0.30, 0.32, 1.0), segments=14)
        for s in (-1, 1):
            make_chair(f"BBQ_Floor_Chair_{k}_{s:+d}", x0 + 3.5 + k * 3.6 + s * 0.85, 4.0, yaw=-s * math.pi / 2.0, wood=(0.22, 0.16, 0.12, 1.0))
    for k in range(5):
        make_cyl(f"BBQ_Pendant_Glow_{k}", (x0 + 2.0 + k * 2.6, 5.6, 2.50), 0.16, 0.24, (0.98, 0.80, 0.52, 1.0), segments=12)
        make_box(f"BBQ_Pendant_Cord_{k}", (x0 + 2.0 + k * 2.6, 5.6, 2.92), (0.01, 0.01, 0.56), (0.20, 0.20, 0.20, 1.0))


# ── F. the pizza parlor's party room, rain (x 1500..1512, y 0..8) ───────
def build_pizza():
    x0 = 1500.0
    pal = {"wall": (0.80, 0.70, 0.54, 1.0), "baseboard": (0.40, 0.30, 0.22, 1.0)}
    room("Pizza", x0, 0.0, 12.0, 8.0, 2.8, pal, ((0.60, 0.20, 0.18, 1.0), (0.88, 0.86, 0.80, 1.0)),
         doors={"E": [(4.0, 1.0, 1.0, 2.1)]}, wins={"S": [(x0 + 2.0, 1.4, 1.8, 1.3), (x0 + 5.0, 1.4, 1.8, 1.3)]})
    # the steamed panes (opaque: our materials have no alpha), the rain on
    # them, the wet lot and a car beyond
    for k, x in enumerate((x0 + 2.0, x0 + 5.0)):
        make_box(f"Pizza_Window_Steam_Pane_{k}", (x, 0.0, 1.4), (1.68, 0.02, 0.50), (0.72, 0.74, 0.74, 1.0))
        for j in range(6):
            make_box(f"Pizza_Rain_Water_Streak_{k}_{j}", (x - 0.7 + j * 0.28, -0.03, 1.2 + (j % 2) * 0.1), (0.008, 0.008, 0.70), (0.80, 0.84, 0.88, 1.0))
    make_box("Lot_Wet_Asphalt", (x0 + 6.0, -10.0, -0.02), (40.0, 20.0, 0.04), (0.16, 0.16, 0.18, 1.0))
    for k in range(5):
        make_box(f"Lot_Puddle_Water_{k}", (x0 + 1.0 + k * 2.4, -4.0 - (k % 2) * 2.0, 0.003), (1.6, 0.9, 0.006), (0.30, 0.32, 0.36, 1.0))
    make_car("Lot_Car", x0 + 3.4, -5.0, 4.6, (0.30, 0.30, 0.34, 1.0), along="Y")
    make_box("Strip_Mall_Facade_Next", (x0 + 18.0, 0.0, 2.4), (12.0, 0.30, 4.8), (0.66, 0.60, 0.50, 1.0))
    make_box("Strip_Mall_Sign_Glow", (x0 + 18.0, -0.2, 3.6), (8.0, 0.06, 0.8), (0.96, 0.80, 0.40, 1.0))
    make_box("Lot_Light_Pole", (x0 + 9.0, -12.0, 3.5), (0.12, 0.12, 7.0), (0.36, 0.36, 0.38, 1.0))
    make_box("Lot_Light_Head_Glow", (x0 + 9.0, -11.6, 7.0), (0.40, 0.80, 0.14), (1.0, 0.76, 0.44, 1.0))
    make_box("Pizza_Sky_S", (x0 + 6.0, -80.0, 30.0), (200.0, 0.2, 80.0), (0.06, 0.06, 0.08, 1.0))
    # the party room: long tables end to end, the plates piled, cups; the
    # projector on its cart, the screen at the N end with the pitcher
    for r, y in enumerate((2.4, 5.2)):
        for k in range(3):
            make_table(f"Party_Table_{r}_{k}", x0 + 2.4 + k * 2.6, y, w=2.4, d=0.9, h=0.74, wood=(0.66, 0.56, 0.44, 1.0))
            for s in (-1, 1):
                for c in (-1, 1):
                    make_chair(f"Party_Chair_{r}_{k}_{s:+d}{c:+d}", x0 + 2.4 + k * 2.6 + c * 0.6, y + s * 0.75,
                               yaw=(0.0 if s < 0 else math.pi), wood=(0.30, 0.24, 0.20, 1.0))
    for k in range(4):
        make_box(f"Plate_Pile_{k}", (x0 + 1.8 + k * 2.2, 2.4 + (k % 2) * 2.8, 0.78), (0.26, 0.26, 0.08), (0.94, 0.94, 0.92, 1.0))
        make_cyl(f"Party_Cup_{k}", (x0 + 2.2 + k * 2.2, 2.2 + (k % 2) * 2.8, 0.80), 0.04, 0.12, (0.86, 0.20, 0.20, 1.0), segments=8)
    make_box("Pizza_Box_Open", (x0 + 4.9, 5.2, 0.76), (0.40, 0.40, 0.03), (0.86, 0.80, 0.66, 1.0))
    make_box("Projection_Screen_Hang", (x0 + 6.0, 8.0 - 0.08 - 0.04, 1.6), (3.0, 0.02, 1.9), (0.94, 0.94, 0.92, 1.0))
    make_box("Projection_Screen_Case_Mounted", (x0 + 6.0, 8.0 - 0.08 - 0.06, 2.62), (3.2, 0.10, 0.12), (0.30, 0.30, 0.32, 1.0))
    make_box("Screen_Image_Field", (x0 + 6.0, 8.0 - 0.08 - 0.055, 1.30), (2.8, 0.004, 1.00), (0.48, 0.60, 0.40, 1.0))
    make_box("Screen_Image_Stands", (x0 + 6.0, 8.0 - 0.08 - 0.055, 2.10), (2.8, 0.004, 0.60), (0.60, 0.56, 0.54, 1.0))
    make_box("Screen_Image_Pitcher", (x0 + 5.8, 8.0 - 0.08 - 0.058, 1.50), (0.16, 0.004, 0.50), (0.90, 0.88, 0.84, 1.0))
    make_box("Projector_Cart", (x0 + 6.0, 3.8, 0.45), (0.60, 0.50, 0.90), (0.30, 0.30, 0.32, 1.0))
    make_chamfer_box("Projector_Body", (x0 + 6.0, 3.8, 0.98), (0.34, 0.30, 0.16), (0.60, 0.60, 0.58, 1.0), chamfer=0.03)


# ── G. the club, industrial downtown (x 1800..1830, y 0..24) ────────────
def build_warehouse():
    x0 = 1800.0
    H = 8.0
    conc = (0.36, 0.36, 0.38, 1.0)
    make_box("Warehouse_Floor_Slab", (x0 + 15.0, 12.0, -0.10), (30.0, 24.0, 0.20), (0.14, 0.14, 0.16, 1.0))
    make_box("Warehouse_Roof_Slab", (x0 + 15.0, 12.0, H + 0.15), (30.4, 24.4, 0.30), (0.10, 0.10, 0.12, 1.0))
    for nm, c, sz in (("Warehouse_Wall_S", (x0 + 15.0, 0.0, H / 2.0), (30.4, 0.30, H)), ("Warehouse_Wall_N", (x0 + 15.0, 24.0, H / 2.0), (30.4, 0.30, H)),
                      ("Warehouse_Wall_W", (x0, 12.0, H / 2.0), (0.30, 24.0, H)), ("Warehouse_Wall_E", (x0 + 30.0, 12.0, H / 2.0), (0.30, 24.0, H))):
        make_box(nm, c, sz, conc)
    for k in range(6):
        make_box(f"Warehouse_Truss_{k}", (x0 + 2.5 + k * 5.0, 12.0, H - 0.4), (0.30, 24.0, 0.50), (0.22, 0.22, 0.24, 1.0))
        make_box(f"Warehouse_Column_{k}", (x0 + 2.5 + k * 5.0, 0.4, (H - 0.65) / 2.0), (0.40, 0.40, H - 0.65), (0.22, 0.22, 0.24, 1.0))
    # (2026-10-30, draft 2: the "haze banks" were opaque grey blobs, one of
    # them around the camera, and the floor was empty — the frame was a
    # black void with a green smear. The fog is the environment's now; the
    # light is drawn as beams; the floor is full.)
    for k in range(8):
        make_cyl(f"Beam_Lamp_Can_{k}", (x0 + 4.0 + k * 3.2, 23.4, 6.0), 0.18, 0.40, (0.10, 0.10, 0.10, 1.0), axis='Y', segments=10)
    make_box("Beam_Lamp_Bar", (x0 + 15.2, 23.55, 6.25), (24.0, 0.10, 0.10), (0.16, 0.16, 0.18, 1.0))
    make_box("DJ_Riser", (x0 + 15.0, 22.6, 0.40), (6.0, 2.4, 0.80), (0.10, 0.10, 0.12, 1.0))
    make_box("DJ_Table", (x0 + 15.0, 22.4, 1.25), (2.4, 0.80, 0.90), (0.08, 0.08, 0.10, 1.0))
    for s in (-1, 1):
        make_box(f"Speaker_Stack_{s:+d}", (x0 + 15.0 + s * 4.6, 22.6, 1.4), (1.2, 1.0, 2.8), (0.06, 0.06, 0.08, 1.0))
        for j in range(2):
            make_cyl(f"Speaker_Cone_{s:+d}_{j}", (x0 + 15.0 + s * 4.6, 22.09, 0.75 + j * 1.25), 0.38, 0.02,
                     (0.14, 0.14, 0.16, 1.0), axis='Y', segments=16)
    build_warehouse_2026_10(x0, H)


def _beam(name, apex, length, angle, roll, col):
    """A light beam as a translucent cone (LocaleGlass draws vertex alpha):
    apex at the lamp, opening `angle` (half, radians), tilted from straight
    down by `roll` about X (negative swings it toward -y, the camera)."""
    from _props.geometry import _gen_lathe, _rot3, _finalize_mesh, _fix_winding
    r = length * math.tan(angle)
    prof = [(r, -length), (r * 0.5, -length * 0.5), (0.12, 0.0)]
    verts, faces = _gen_lathe(apex, prof, 16, False)
    verts = _rot3(verts, apex, 0.0, 0.0, roll)
    return _finalize_mesh(name, verts, _fix_winding(verts, faces, apex), col)


def build_warehouse_2026_10(x0, H):
    """passengers (vol 3 ch8), DRAFT 2: "Green and pink light cut across body
    mist, artificial smoke"; "Young people flinging all up against each
    other"; "into those four walls, even more into the floor".
    - the four beams drawn: translucent green and pink cones from the cans
      on the N wall's bar, down across the floor toward the camera
    - the crowd: thirty-odd dancers packed on the floor, arms up, the DJ on
      the riser behind his table
    - the four walls as an industrial downtown shell: brick courses on the N
      and S walls, the clerestory windows (sodium glow outside), the steel
      doors and the red EXIT over one, a bar along the W wall with its lit
      back shelf, ducts along the trusses
    Draft 3 targets: the fog as volumetric fog in this preset only (if the
    Deck can carry it), the dancers' clothes under the beams' colours, the
    bar's people, the coats piled on the riser's edge."""
    from _props.figures import make_standing_figure
    import random
    rnd = random.Random(1801)
    # the beams: the four spots in the tscn (x 1804, 1810.4, 1816.8, 1823.2,
    # 6 m up at y 23.4, aimed 37 deg below level toward -y), narrower than
    # the spot so the cone's skin stays inside the light
    for k, (bx, col) in enumerate(((4.0, (0.40, 1.0, 0.50, 0.10)), (10.4, (1.0, 0.40, 0.80, 0.10)),
                                    (16.8, (0.40, 1.0, 0.50, 0.10)), (23.2, (1.0, 0.40, 0.80, 0.10)))):
        _beam(f"Beam_Cone_{k}", (x0 + bx, 23.2, 5.85), 9.6, math.radians(13.0), -0.927, col)
    # the crowd: a jittered grid on y 11..19, facing the riser (heading ~0)
    tops = ((0.10, 0.10, 0.12, 1.0), (0.16, 0.12, 0.20, 1.0), (0.52, 0.52, 0.56, 1.0), (0.12, 0.16, 0.20, 1.0),
            (0.50, 0.12, 0.16, 1.0), (0.20, 0.20, 0.22, 1.0), (0.70, 0.60, 0.20, 1.0))
    hairs = ((0.10, 0.08, 0.06, 1.0), (0.30, 0.20, 0.12, 1.0), (0.62, 0.50, 0.30, 1.0), (0.06, 0.06, 0.06, 1.0))
    n = 0
    for j in range(6):
        for i in range(10):
            if rnd.random() < 0.28:
                continue
            fx = x0 + 6.0 + i * 1.9 + rnd.uniform(-0.35, 0.35) + (0.9 if j % 2 else 0.0)
            fy = 11.0 + j * 1.55 + rnd.uniform(-0.3, 0.3)
            if fx > x0 + 25.0:
                continue
            arms = ("up", "up_r", "down", "up", "front", "up_r")[rnd.randrange(6)]
            dress = (0.12, 0.10, 0.14, 1.0) if rnd.random() < 0.3 else None
            make_standing_figure(f"Dancer_{n}", fx, fy, heading=rnd.uniform(-0.6, 0.6) + (math.pi if rnd.random() < 0.2 else 0.0),
                                 h=rnd.uniform(1.62, 1.86), coat=tops[rnd.randrange(len(tops))],
                                 pants=(0.12, 0.12, 0.16, 1.0), hair=hairs[rnd.randrange(len(hairs))],
                                 dress=dress, arms=arms)
            n += 1
    # the DJ's gooseneck lamp on the table (the tscn's DJ_Lamp practical)
    make_cyl("DJ_Lamp_Base", (x0 + 16.0, 22.2, 1.71), 0.07, 0.02, (0.12, 0.12, 0.12, 1.0), segments=10)
    make_rot_box("DJ_Lamp_Neck", (x0 + 16.0, 22.12, 1.86), (0.015, 0.015, 0.30), (0.12, 0.12, 0.12, 1.0), roll=0.5)
    make_cyl("DJ_Lamp_Head", (x0 + 16.0, 22.02, 2.0), 0.04, 0.07, (1.0, 0.86, 0.60, 1.0), segments=10)
    make_standing_figure("DJ", x0 + 15.0, 23.15, heading=math.pi, h=1.78, coat=(0.08, 0.08, 0.10, 1.0), arms="front", z0=0.80)
    # brick courses on the N and S walls (their inner faces at y 23.85 / 0.15)
    brick = (0.46, 0.30, 0.24, 1.0)
    for wy, nm in ((23.84, "N"), (0.16, "S")):
        make_box(f"Brick_Face_{nm}", (x0 + 15.0, wy, H / 2.0), (29.6, 0.01, H), brick)
        for c in range(26):
            make_box(f"Brick_Course_{nm}_{c}", (x0 + 15.0, wy + (-0.006 if nm == "N" else 0.006), 0.15 + c * 0.30),
                     (29.6, 0.004, 0.02), (0.18, 0.12, 0.10, 1.0))
    # clerestory windows high on the E and W walls: sodium light outside
    for wx, nm in ((x0 + 0.16, "W"), (x0 + 29.84, "E")):
        for k in range(5):
            make_box(f"Clerestory_{nm}_{k}", (wx, 3.0 + k * 4.4, 6.4), (0.02, 2.6, 1.0), (0.62, 0.42, 0.20, 1.0))
            for m in range(3):
                make_box(f"Clerestory_Mull_{nm}_{k}_{m}", (wx + (0.01 if nm == "W" else -0.01), 3.0 + k * 4.4 + (m - 1) * 0.87, 6.4),
                         (0.02, 0.05, 1.0), (0.12, 0.12, 0.14, 1.0))
    # the steel doors in the S wall, the red EXIT over the W one
    for k, dx in enumerate((4.0, 26.0)):
        make_box(f"Steel_Door_{k}", (x0 + dx, 0.18, 1.05), (1.8, 0.04, 2.1), (0.26, 0.28, 0.30, 1.0))
        make_box(f"Steel_Door_Bar_{k}", (x0 + dx, 0.22, 1.0), (1.4, 0.04, 0.06), (0.50, 0.50, 0.52, 1.0))
    make_box("Exit_Sign", (x0 + 4.0, 0.22, 2.45), (0.50, 0.08, 0.20), (0.95, 0.12, 0.10, 1.0))
    # the bar along the W wall: counter, lit back shelf, bottles
    make_box("Bar_Counter", (x0 + 2.6, 12.0, 0.55), (0.80, 9.0, 1.10), (0.12, 0.10, 0.10, 1.0))
    make_box("Bar_Top", (x0 + 2.6, 12.0, 1.13), (0.90, 9.1, 0.05), (0.30, 0.24, 0.20, 1.0))
    make_box("Bar_Back_Shelf_Glow", (x0 + 0.20, 12.0, 1.9), (0.04, 8.0, 0.9), (0.95, 0.66, 0.30, 1.0))
    for sh in range(2):
        make_box(f"Bar_Shelf_{sh}", (x0 + 0.35, 12.0, 1.55 + sh * 0.5), (0.26, 8.0, 0.03), (0.20, 0.18, 0.16, 1.0))
        for b in range(22):
            make_cyl(f"Bar_Bottle_{sh}_{b}", (x0 + 0.36, 8.3 + b * 0.35, 1.68 + sh * 0.5), 0.035, 0.24,
                     ((0.30, 0.50, 0.30, 1.0), (0.60, 0.40, 0.20, 1.0), (0.80, 0.80, 0.84, 1.0))[(b + sh) % 3], segments=8)
    # ducts along the trusses
    for k in range(2):
        make_cyl(f"Duct_{k}", (x0 + 9.0 + k * 12.0, 12.0, H - 1.2), 0.40, 23.4, (0.40, 0.40, 0.42, 1.0), axis='Y', segments=14)


# ── H. the catwalk between the towers, the lit city below (x 2100..) ────
def build_catwalk():
    x0, y0 = 2100.0, 0.0
    L = 40.0                                   # the tube runs N 40 m, tower to tower
    W, H = 3.0, 2.8
    make_box("Catwalk_Floor", (x0, y0 + L / 2.0, -0.10), (W, L, 0.20), (0.56, 0.58, 0.60, 1.0))
    make_box("Catwalk_Ceil", (x0, y0 + L / 2.0, H + 0.05), (W, L, 0.10), (0.80, 0.82, 0.84, 1.0))
    for k in range(int(L / 2.5) + 1):
        y = y0 + k * 2.5
        for s in (-1, 1):
            make_box(f"Catwalk_Rib_{k}_{s:+d}", (x0 + s * (W / 2.0), y, H / 2.0), (0.08, 0.10, H), (0.70, 0.72, 0.74, 1.0))
        make_box(f"Catwalk_Rib_Top_{k}", (x0, y, H - 0.02), (W, 0.10, 0.06), (0.70, 0.72, 0.74, 1.0))
    for s in (-1, 1):
        make_box(f"Catwalk_Rail_Mounted_{s:+d}", (x0 + s * (W / 2.0 - 0.10), y0 + L / 2.0, 1.0), (0.05, L, 0.05), (0.80, 0.80, 0.82, 1.0))
        make_box(f"Catwalk_Kick_Plate_{s:+d}", (x0 + s * (W / 2.0 - 0.02), y0 + L / 2.0, 0.15), (0.04, L, 0.30), (0.62, 0.64, 0.66, 1.0))
    for k in range(8):
        make_box(f"Catwalk_Ceiling_Light_Glow_{k}", (x0, y0 + 2.5 + k * 5.0, H - 0.02), (0.30, 1.2, 0.04), (0.92, 0.96, 0.98, 1.0))
    # the towers at either end, their doors
    for nm, y, dy in (("Tower_S", y0 - 10.0, 1), ("Tower_N", y0 + L + 10.0, -1)):
        make_box(f"Catwalk_{nm}", (x0, y, -20.0 + 15.0), (24.0, 20.0, 70.0), (0.62, 0.64, 0.66, 1.0))
        make_box(f"Catwalk_{nm}_Door", (x0, y + dy * 10.02, 1.05), (1.6, 0.04, 2.1), (0.70, 0.74, 0.76, 1.0))
        for j in range(10):
            make_box(f"Catwalk_{nm}_Window_Glow_Stock_{j}", (x0 - 9.0 + (j % 5) * 4.5, y + dy * 10.03, -16.0 + (j // 5) * 8.0),
                     (2.0, 0.04, 1.6), (0.96, 0.90, 0.70, 1.0))
    # the city below and all round: towers of lit windows, the road of red
    # and white lights, a near roof with its steam vent, a helicopter
    cz = -40.0
    make_box("Catwalk_City_Ground", (x0, y0 + L / 2.0, cz - 0.1), (380.0, 380.0, 0.2), (0.06, 0.06, 0.08, 1.0))
    k = 0
    for ring in range(3):
        r = 50.0 + ring * 40.0
        n = 10 + ring * 4
        for i in range(n):
            a = (i + 0.5 * (ring % 2)) * 2.0 * math.pi / n
            bx, by = x0 + r * math.cos(a), y0 + L / 2.0 + r * math.sin(a)
            h = 20.0 + ((i * 7 + ring * 3) % 5) * 10.0
            make_box(f"Catwalk_City_Tower_Stock_{k}", (bx, by, cz + h / 2.0), (12.0, 12.0, h), (0.14, 0.15, 0.18, 1.0))
            for j in range(5):
                make_box(f"Catwalk_City_Window_Glow_Stock_{k}_{j}", (bx - 6.02 * math.cos(a), by - 6.02 * math.sin(a), cz + h * (0.15 + j * 0.16)),
                         (abs(math.sin(a)) * 10.0 + 0.1, abs(math.cos(a)) * 10.0 + 0.1, 1.8),
                         ((1.0, 0.86, 0.60, 1.0), (0.84, 0.92, 1.0, 1.0))[(k + j) % 2])
            k += 1
    for k in range(30):
        make_box(f"Road_Tail_Light_Stock_{k}", (x0 + 28.0, y0 - 100.0 + k * 8.0, cz + 0.2), (0.6, 1.6, 0.2), (0.96, 0.20, 0.16, 1.0))
        make_box(f"Road_Head_Light_Stock_{k}", (x0 + 32.0, y0 - 96.0 + k * 8.0, cz + 0.2), (0.6, 1.6, 0.2), (0.98, 0.96, 0.90, 1.0))
    make_box("Road_Asphalt", (x0 + 30.0, y0 + L / 2.0, cz + 0.02), (10.0, 300.0, 0.04), (0.10, 0.10, 0.12, 1.0))
    # (2026-10-30) "lamps up on poles, thousands and thousands of them laid
    # out over the land like a quilt": 40 lamps on a 30 m grid read as a
    # dozen dots; now a 12 m grid out past the towers, both sides
    k = 0
    for i in range(16):
        for j in range(12):
            lx, ly = x0 + 36.0 + i * 12.0 + (j % 2) * 6.0, y0 - 60.0 + j * 14.0
            make_box(f"Streetlamp_Quilt_Glow_Stock_{k}", (lx, ly, cz + 0.4), (0.8, 0.8, 0.4), (1.0, 0.80, 0.46, 1.0))
            k += 1
    # the near roof is BELOW the catwalk ("On a near roof a vent breathes
    # steam up into the dark") — it stood 14 m above it and filled the view
    make_box("Near_Roof", (x0 + 16.0, y0 + 24.0, -24.0), (16.0, 14.0, 32.0), (0.40, 0.40, 0.42, 1.0))
    make_box("Near_Roof_Vent", (x0 + 14.0, y0 + 24.0, -7.4), (1.2, 1.2, 1.2), (0.50, 0.50, 0.52, 1.0))
    for k in range(4):
        make_blob(f"Vent_Steam_Cloud_{k}", (x0 + 14.0 + k * 0.3, y0 + 24.0, -6.2 + k * 0.9), 0.6 + k * 0.3, (0.80, 0.80, 0.82, 1.0), noise=0.3, seed=k)
    make_chamfer_box("Helicopter_Sky_Body", (x0 + 40.0, y0 + 50.0, 22.0), (2.0, 5.0, 1.8), (0.20, 0.22, 0.26, 1.0), chamfer=0.4)
    make_blob("Helicopter_Light_Red_Glow", (x0 + 40.0, y0 + 47.4, 22.4), 0.25, (1.0, 0.20, 0.16, 1.0), noise=0.0, seed=1)
    make_blob("Helicopter_Light_White_Glow", (x0 + 40.0, y0 + 52.6, 22.4), 0.25, (1.0, 1.0, 1.0, 1.0), noise=0.0, seed=2)
    make_box("Catwalk_Sky_Night", (x0, y0 + 190.0, 20.0), (400.0, 0.2, 160.0), (0.04, 0.04, 0.08, 1.0))


def main():
    clear_scene()
    build_june()
    build_oregon()
    build_coast_studio()
    build_condo()
    build_bbq()
    build_pizza()
    build_warehouse()
    build_catwalk()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/vol3_rooms.glb"))
    print(f"\n[build_vol3_rooms] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
