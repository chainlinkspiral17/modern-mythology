"""caldwell_radio_room_night — Linda Caldwell's bedroom, upstairs, and her
shortwave (vol 6 ch5 "1776 kHz").

DRAFT 1 OF THE RIGHT ROOM (2026-10-08). The prose: "At Maya's
grandmother's house, the upstairs window is lit. She is, at eleven PM on
a Thursday in late May, at her shortwave radio ... sending, on 1776 kHz,
a single phrase, over and over, in Morse code she has not used since
1989, in the cadence her husband Thomas had taught her." Maya "sits on
the edge of the bed"; "Maya helps her into bed, and Maya turns off the
radio". The builder had made a broadcast STATION BOOTH — a mixing board,
a boom mic, an equipment rack, an ON AIR sign, two fluorescent tubes —
and the window pass had given it a ground-floor yard. Now her bedroom:
the radio desk on the east wall beside the south window (the coax out
through the sash, the window the street sees lit), the transceiver with
its amber S-meter, the straight key, the headphones, the open log, QSL
cards pinned above, Thomas's photograph; the bed with its foot toward
the desk; a nightstand and its lamp; a dresser with a mirror; the door to
the hall closed; the back yard a storey down.

DRAFT 2 targets: the quilt's pattern; the log's handwriting rows;
Thomas's photo as a portrait; the coax's drip loop at the sash; the
hall light under the door.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_tube, export_glb
from _props.furniture import make_table, make_chair, make_lamp
from _props.views import make_view
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_window, make_wall_with_openings)
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 4.5; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall": (0.78, 0.70, 0.58, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_FLOOR = (0.62, 0.52, 0.42, 1.0); COL_SEAM = (0.32, 0.22, 0.14, 1.0)
COL_WOOD = (0.42, 0.30, 0.20, 1.0); COL_WOOD_DK = (0.30, 0.20, 0.13, 1.0)
COL_CONSOLE = (0.20, 0.20, 0.22, 1.0); COL_PANEL = (0.14, 0.14, 0.16, 1.0)
COL_METAL = (0.46, 0.46, 0.48, 1.0); COL_METAL_DK = (0.28, 0.28, 0.30, 1.0)
COL_VU_AMBER = (0.96, 0.78, 0.34, 1.0); COL_LED_GREEN = (0.34, 0.92, 0.44, 1.0)
COL_LED_RED = (0.96, 0.28, 0.22, 1.0); COL_KNOB = (0.62, 0.60, 0.58, 1.0)
COL_FADER = (0.72, 0.70, 0.68, 1.0); COL_SCREEN = (0.10, 0.14, 0.12, 1.0)
COL_PHOSPHOR = (0.30, 0.90, 0.52, 1.0); COL_ONAIR = (0.96, 0.20, 0.16, 1.0)
COL_BAKELITE = (0.16, 0.14, 0.13, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,   # cut 2026-10-07: its window was a pane on a solid wall
              axis='X', palette=PAL_WALL, baseboard_face_sign=+1, openings=[(1.55, 1.55, 1.00, 0.90)])
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    # the door to the hall, closed; the wall fills the rest of the opening
    for nm, a, b in (("Wall_S_DoorFill_W", -1.0, -0.45), ("Wall_S_DoorFill_E", 0.45, 1.0)):
        make_wall(nm, ((a + b) / 2.0, 0.0, 0), length=b - a, height=2.0, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Hall_Door", (0.0, 0.06, 1.0), (0.90, 0.05, 2.0), COL_WOOD)
    make_cyl("Hall_Door_Knob", (0.32, 0.10, 0.98), 0.03, 0.05, (0.70, 0.58, 0.30, 1.0), axis='Y', segments=8)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
                                    ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
                                    ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD_DK})



RX, RY0, RY1 = ROOM_W/2.0 - 0.10, 0.55, 1.95      # the radio desk: E wall face, its south and north ends
DESK_D, DESK_Z = 0.62, 0.74


def build_radio_desk():
    """The desk on the east wall beside the window, and on it the station
    she has kept since Thomas: the transceiver, its power supply, the
    straight key, the headphones, the log open at tonight."""
    x0 = RX - DESK_D
    dx, dy = (x0 + RX) / 2.0, (RY0 + RY1) / 2.0
    make_table("Radio_Desk", dx, dy, w=DESK_D, d=RY1 - RY0, h=DESK_Z, wood=COL_WOOD)
    top = DESK_Z
    # the transceiver against the wall, its face to the room (-X)
    make_box("Radio_Transceiver", (RX - 0.20, dy + 0.15, top + 0.08), (0.36, 0.42, 0.16), COL_METAL_DK)
    make_box("Radio_Dial", (RX - 0.381, dy + 0.15, top + 0.10), (0.002, 0.36, 0.09), (0.18, 0.18, 0.20, 1.0))
    make_box("Radio_Dial_Meter", (RX - 0.383, dy + 0.27, top + 0.11), (0.002, 0.08, 0.04), COL_VU_AMBER)
    make_box("Radio_Dial_Freq", (RX - 0.383, dy + 0.08, top + 0.11), (0.002, 0.14, 0.03), (0.96, 0.66, 0.30, 1.0))
    for ki, ky in enumerate((-0.02, 0.06, 0.20, 0.28)):
        make_cyl(f"Radio_Knob_{ki}", (RX - 0.39, dy + ky, top + 0.035), 0.016 if ki % 2 else 0.024, 0.02, COL_KNOB, axis='X', segments=10)
    make_box("Radio_PSU", (RX - 0.16, dy - 0.24, top + 0.06), (0.28, 0.20, 0.12), (0.24, 0.24, 0.26, 1.0))
    make_box("Radio_PSU_Meter", (RX - 0.301, dy - 0.24, top + 0.08), (0.002, 0.08, 0.05), (0.90, 0.88, 0.80, 1.0))
    # the straight key: base, lever, the black knob under her fingers
    kx, ky = x0 + 0.22, dy + 0.05
    make_box("Morse_Key_Base", (kx, ky, top + 0.01), (0.16, 0.08, 0.02), COL_BAKELITE)
    make_box("Morse_Key_Lever", (kx - 0.01, ky, top + 0.035), (0.13, 0.012, 0.012), COL_METAL)
    make_cyl("Morse_Key_Knob", (kx - 0.07, ky, top + 0.05), 0.016, 0.012, COL_BAKELITE, segments=10)
    make_tube("Morse_Key_Lead", [(kx + 0.08, ky, top + 0.01), (RX - 0.38, dy - 0.02, top + 0.01)], 0.003, COL_BAKELITE)
    # the headphones, set down on the desk, the band up
    hx, hy = x0 + 0.20, dy + 0.42
    for e in (-1, 1):
        make_cyl(f"Headphones_Cup_{e:+d}", (hx, hy + e * 0.08, top + 0.03), 0.045, 0.05, COL_BAKELITE, axis='Y', segments=10)
    make_tube("Headphones_Band", [(hx, hy - 0.08, top + 0.07), (hx, hy - 0.04, top + 0.15), (hx, hy + 0.04, top + 0.15), (hx, hy + 0.08, top + 0.07)], 0.008, COL_METAL_DK)
    # the log, open at tonight, the pencil
    make_box("Log_Book_L", (x0 + 0.24, dy - 0.32, top + 0.006), (0.20, 0.15, 0.012), (0.94, 0.92, 0.84, 1.0))
    make_box("Log_Book_R", (x0 + 0.24, dy - 0.17, top + 0.006), (0.20, 0.15, 0.012), (0.94, 0.92, 0.84, 1.0))
    for li in range(5):
        make_box(f"Log_Book_Line_{li}", (x0 + 0.17 + li * 0.03, dy - 0.32, top + 0.0125), (0.004, 0.12, 0.001), (0.30, 0.30, 0.42, 1.0))
    make_cyl("Log_Pencil", (x0 + 0.32, dy - 0.25, top + 0.005), 0.004, 0.15, (0.90, 0.72, 0.24, 1.0), axis='Y', segments=6)
    # a cup of tea gone cold, and Thomas
    make_cyl("Tea_Cup", (x0 + 0.12, dy + 0.62, top + 0.04), 0.04, 0.08, (0.92, 0.90, 0.86, 1.0), segments=10)
    make_box("Thomas_Photo", (RX - 0.05, dy + 0.58, top + 0.11), (0.03, 0.14, 0.18), (0.62, 0.50, 0.34, 1.0))
    make_box("Thomas_Photo_Print", (RX - 0.066, dy + 0.58, top + 0.11), (0.002, 0.10, 0.14), (0.42, 0.40, 0.38, 1.0))
    # the desk lamp (the light the window shows the street)
    make_lamp("Desk_Lamp", x0 + 0.48, dy + 0.52, base_z=top, h=0.42, shade_col=(0.86, 0.74, 0.46, 1.0))
    # the coax: off the transceiver's back, along the wall, out the sash
    make_tube("Coax", [(RX - 0.01, dy + 0.15, top + 0.17), (RX - 0.01, dy + 0.15, top + 0.40), (RX - 0.01, RY0 - 0.30, top + 0.40), (1.95, 0.16, 1.15)], 0.008, COL_BAKELITE)
    # her chair at the desk, facing the radio
    make_chair("Radio_Chair", x0 - 0.30, dy, yaw=1.5708, wood=COL_WOOD_DK)
    # QSL cards above the desk on a cork board
    make_box("QSL_Board", (RX - 0.01, dy, 1.62), (0.02, 1.10, 0.60), (0.62, 0.48, 0.32, 1.0))
    cols = ((0.86, 0.32, 0.26, 1.0), (0.30, 0.52, 0.76, 1.0), (0.94, 0.84, 0.40, 1.0), (0.44, 0.66, 0.42, 1.0), (0.94, 0.92, 0.86, 1.0))
    for qi in range(10):
        make_box(f"QSL_Card_{qi}", (RX - 0.021, dy - 0.44 + (qi % 5) * 0.22, 1.76 - (qi // 5) * 0.26), (0.002, 0.14, 0.09), cols[qi % len(cols)])


def build_bedroom():
    """The bed (its foot toward the desk, where Maya sits on its edge), the
    nightstand and its lamp, the dresser and its mirror, a rug."""
    from _props.furniture import make_bed
    make_bed("Bed", 1.35, ROOM_D - 1.10, head="+Y", w=1.40, d=2.00, style="frame", frame_col=COL_WOOD,
             blanket_col=(0.62, 0.44, 0.48, 1.0), pillows=2)
    make_box("Bed_Quilt_Fold", (1.35, ROOM_D - 2.02, 0.60), (1.30, 0.22, 0.05), (0.86, 0.80, 0.66, 1.0))
    make_table("Nightstand", 0.30, ROOM_D - 0.40, w=0.46, d=0.40, h=0.60, wood=COL_WOOD)
    make_lamp("Bedside_Lamp", 0.30, ROOM_D - 0.40, base_z=0.60, h=0.48)
    make_box("Reading_Glasses", (0.20, ROOM_D - 0.52, 0.605), (0.12, 0.04, 0.01), (0.30, 0.24, 0.20, 1.0))
    make_box("Dresser", (-ROOM_W/2.0 + 0.36, 2.60, 0.48), (0.52, 1.30, 0.96), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (-ROOM_W/2.0 + 0.625, 2.60, 0.18 + di * 0.30), (0.01, 1.20, 0.24), COL_WOOD_DK)
        for e in (-1, 1):
            make_box(f"Dresser_Pull_{di}_{e:+d}", (-ROOM_W/2.0 + 0.64, 2.60 + e * 0.32, 0.18 + di * 0.30), (0.02, 0.10, 0.02), (0.70, 0.58, 0.30, 1.0))
    make_box("Dresser_Mirror", (-ROOM_W/2.0 + 0.12, 2.60, 1.45), (0.03, 0.80, 0.90), COL_WOOD_DK)
    make_box("Dresser_Mirror_Glass", (-ROOM_W/2.0 + 0.137, 2.60, 1.45), (0.004, 0.70, 0.80), (0.58, 0.64, 0.68, 1.0))
    for bi, (bx, col) in enumerate(((-0.30, (0.86, 0.72, 0.62, 1.0)), (-0.10, (0.62, 0.70, 0.82, 1.0)))):
        make_cyl(f"Dresser_Bottle_{bi}", (-ROOM_W/2.0 + 0.36, 2.60 + bx, 0.96 + 0.06), 0.03, 0.12, col, segments=8)
    make_box("Rug", (0.10, 2.40, 0.006), (2.0, 1.40, 0.012), (0.54, 0.36, 0.34, 1.0))


def build_window():
    # the south window by the radio — the one the street sees lit
    make_window("WindowS", (+1.55, 0.10, 1.55), width=1.00, height=0.90,
                palette={"frame": COL_WOOD_DK}, room_dir=+1, see_through=True)


def build_ceiling_infra():
    make_cyl("Ceiling_Dome", (0.0, ROOM_D/2.0, CEIL - 0.06), 0.16, 0.10, (0.94, 0.90, 0.78, 1.0), segments=12)
    make_smoke_detector("Smoke", (-0.8, ROOM_D/2.0, CEIL))


def build_decor():
    make_wall_clock("Clock", (2.150, 3.0, 1.90), frozen_hour=11, frozen_min=8, facing='-X')
    make_calendar("Calendar", (-ROOM_W/2.0+0.1025, 4.0, 1.70))
    make_floor_plant("Plant", (-ROOM_W/2.0+0.45, ROOM_D-0.5, 0.0), kind="fern")



def build_lived_in_2026_10():
    """HER ROOM, LIVED IN (2026-10-08). The user: "Too bare and empty, the
    Caldwell." Forty years in one room: the quilt pieced in squares, her
    cane against the nightstand (the hip is healed; she does not yet trust
    it), her slippers, her robe on the back of the door, the family on the
    wall over the bed and in frames on the dresser — Thomas in the middle —
    her reading chair in the corner with an afghan and its lamp table, a
    low bookshelf, curtains at the radio's window, a picture rail."""
    from _props.geometry import make_chamfer_box, make_blob, make_lathe
    WF, EF, NF = -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, ROOM_D - 0.10
    walnut, walnut_dk = COL_WOOD, COL_WOOD_DK
    # ── the quilt: squares pieced across the blanket ──
    qcols = ((0.78, 0.40, 0.42, 1.0), (0.92, 0.86, 0.70, 1.0), (0.46, 0.58, 0.66, 1.0), (0.62, 0.70, 0.48, 1.0), (0.86, 0.66, 0.40, 1.0))
    for i in range(6):
        for j in range(4):
            make_box(f"Quilt_Square_{i}_{j}", (0.81 + i * 0.216, 3.22 + j * 0.22, 0.5905), (0.20, 0.20, 0.001), qcols[(i * 3 + j * 2) % len(qcols)])
    # ── the cane against the nightstand, the slippers ──
    make_tube("Cane", [(0.56, 4.38, 0.02), (0.54, 4.42, 0.84), (0.53, 4.50, 0.90), (0.535, 4.56, 0.86)], 0.012, walnut_dk)
    make_cyl("Cane_Tip", (0.56, 4.38, 0.015), 0.016, 0.03, (0.10, 0.10, 0.10, 1.0), segments=6)
    for e in (-1, 1):
        make_chamfer_box(f"Slipper_{e:+d}", (0.45 + e * 0.07, 3.55, 0.025), (0.10, 0.26, 0.05), (0.62, 0.48, 0.58, 1.0), chamfer=0.02)
    make_cyl("Nightstand_Water", (0.42, 4.70, 0.645), 0.035, 0.09, (0.70, 0.78, 0.82, 0.6), segments=10)
    make_box("Nightstand_Book", (0.18, 4.62, 0.615), (0.16, 0.22, 0.03), (0.30, 0.40, 0.52, 1.0))
    # ── the robe on the back of the hall door ──
    make_cyl("Door_Hook", (-0.25, 0.10, 1.78), 0.008, 0.04, (0.70, 0.58, 0.30, 1.0), axis='Y', segments=6)
    make_chamfer_box("Door_Robe", (-0.25, 0.12, 1.36), (0.42, 0.06, 0.86), (0.36, 0.52, 0.56, 1.0), chamfer=0.02)
    make_box("Door_Robe_Belt", (-0.25, 0.152, 1.24), (0.40, 0.006, 0.04), (0.30, 0.44, 0.48, 1.0))
    # ── the family over the bed; frames on the dresser, Thomas in the middle ──
    for fi, (fx, fz, fw, fh) in enumerate(((0.95, 1.62, 0.30, 0.38), (1.40, 1.72, 0.40, 0.30), (1.85, 1.58, 0.26, 0.34), (1.40, 1.42, 0.22, 0.16))):
        make_box(f"Wall_Photo_{fi}", (fx, NF - 0.015, fz), (fw, 0.03, fh), walnut_dk)
        make_box(f"Wall_Photo_{fi}_Print", (fx, NF - 0.031, fz), (fw - 0.06, 0.002, fh - 0.06),
                 ((0.56, 0.50, 0.44, 1.0), (0.46, 0.44, 0.42, 1.0), (0.60, 0.54, 0.46, 1.0), (0.52, 0.48, 0.44, 1.0))[fi])
    for fi, (fy, fh) in enumerate(((2.68, 0.20), (2.85, 0.26), (3.05, 0.18))):
        make_box(f"Dresser_Frame_{fi}", (-1.80, fy, 0.96 + fh / 2.0), (0.02, 0.14, fh), (0.70, 0.58, 0.30, 1.0) if fi == 1 else walnut_dk)
        make_box(f"Dresser_Frame_{fi}_Stand", (-1.84, fy, 0.96 + fh * 0.25), (0.06, 0.02, fh * 0.5), walnut_dk)
    make_box("Dresser_Runner", (-1.89, 2.60, 0.962), (0.40, 1.10, 0.004), (0.96, 0.95, 0.92, 1.0))
    make_box("Jewelry_Box", (-1.95, 2.10, 1.01), (0.18, 0.14, 0.10), (0.52, 0.28, 0.24, 1.0))
    # ── her reading chair in the south-west corner, the afghan, the lamp table ──
    ax, ay = -1.60, 0.85
    upholstery = (0.58, 0.46, 0.38, 1.0)
    make_chamfer_box("Armchair_Base", (ax, ay, 0.20), (0.76, 0.76, 0.40), upholstery, chamfer=0.04)
    make_chamfer_box("Armchair_Seat", (ax, ay + 0.04, 0.46), (0.56, 0.58, 0.12), (0.64, 0.52, 0.42, 1.0), chamfer=0.04)
    make_chamfer_box("Armchair_Back", (ax, ay - 0.31, 0.78), (0.70, 0.14, 0.64), upholstery, chamfer=0.05)
    for e in (-1, 1):
        make_chamfer_box(f"Armchair_Arm_{e:+d}", (ax + e * 0.32, ay, 0.56), (0.12, 0.76, 0.32), upholstery, chamfer=0.04)
    make_box("Armchair_Afghan", (ax, ay - 0.24, 1.00), (0.66, 0.08, 0.36), (0.72, 0.54, 0.30, 1.0))
    make_box("Armchair_Afghan_Band", (ax, ay - 0.199, 0.98), (0.66, 0.002, 0.05), (0.42, 0.56, 0.48, 1.0))
    make_table("Lamp_Table", -2.00, 1.55, w=0.36, d=0.36, h=0.56, wood=walnut)
    make_lamp("Reading_Lamp", -2.00, 1.55, base_z=0.56, h=0.50, shade_col=(0.92, 0.84, 0.66, 1.0))
    for bi in range(3):
        make_box(f"Lamp_Table_Book_{bi}", (-1.94, 1.48, 0.575 + bi * 0.03), (0.15 - bi * 0.01, 0.20, 0.03), ((0.42, 0.24, 0.20, 1.0), (0.26, 0.36, 0.30, 1.0), (0.80, 0.74, 0.60, 1.0))[bi])
    # ── a low bookshelf on the W wall north of the dresser ──
    bx0, by0, by1 = WF, 3.45, 4.15
    make_box("Bookshelf_Back", (bx0 + 0.01, (by0 + by1) / 2.0, 0.55), (0.02, by1 - by0, 1.10), walnut_dk)
    for e in (-1, 1):
        make_box(f"Bookshelf_Side_{e:+d}", (bx0 + 0.15, (by0 + by1) / 2.0 + e * ((by1 - by0) / 2.0 - 0.01), 0.55), (0.30, 0.02, 1.10), walnut)
    for si, sz in enumerate((0.02, 0.38, 0.74, 1.09)):
        make_box(f"Bookshelf_Shelf_{si}", (bx0 + 0.15, (by0 + by1) / 2.0, sz), (0.30, by1 - by0 - 0.04, 0.02), walnut)
        if si < 3:
            y = by0 + 0.04
            for bi in range(10):
                t = 0.03 + 0.012 * ((bi + si) % 3); h = 0.22 + 0.04 * ((bi * 7 + si) % 3)
                if y + t > by1 - 0.04:
                    break
                make_box(f"Bookshelf_Book_{si}_{bi}", (bx0 + 0.14, y + t / 2.0, sz + 0.01 + h / 2.0), (0.20, t, h),
                         ((0.48, 0.22, 0.20, 1.0), (0.22, 0.32, 0.46, 1.0), (0.72, 0.64, 0.46, 1.0), (0.30, 0.42, 0.30, 1.0))[(bi + si) % 4])
                y += t + 0.003
    # ── curtains at the radio's window, a picture rail round the room ──
    make_cyl("Window_Curtain_Rod", (1.55, 0.23, 2.16), 0.01, 1.40, (0.70, 0.58, 0.30, 1.0), axis='X', segments=6)
    for e, cx in ((-1, 0.88), (1, 2.14 - 0.09)):
        make_box(f"Window_Curtain_{e:+d}", (cx, 0.23, 1.55), (0.16, 0.05, 1.20), (0.82, 0.70, 0.58, 1.0))
    for e in (-1, 1):
        make_box(f"Window_Curtain_Bracket_{e:+d}", (1.55 + e * 0.59, 0.16, 2.16), (0.02, 0.14, 0.02), (0.70, 0.58, 0.30, 1.0))
    for nm, c, sz in (("W", (WF + 0.012, ROOM_D / 2.0, 2.25), (0.024, ROOM_D - 0.2, 0.04)),
                      ("N", (0.0, NF - 0.012, 2.25), (ROOM_W - 0.2, 0.024, 0.04))):
        make_box(f"Picture_Rail_{nm}", c, sz, walnut)

def main():
    clear_scene()
    build_shell()
    build_radio_desk()
    build_bedroom()
    build_window()
    build_ceiling_infra()
    build_decor()
    build_lived_in_2026_10()
    # the back yard a storey down (2026-10-08: her room is UPSTAIRS)
    make_view("View_S", "S", 0.0, 1.55, kind="back", ground_z=-2.9, seed=10)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_radio_room_night.glb"))
    print(f"\n[build_caldwell_radio_room_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
