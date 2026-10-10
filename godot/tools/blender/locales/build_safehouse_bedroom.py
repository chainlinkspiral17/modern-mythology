"""safehouse_bedroom — the back bedroom of the safehouse (vol6 ch6, 7, 9).

DRAFT 3 (2026-10-10) — the wrong REGISTER. Drafts 1-2 dressed a spy's
hideout: a corkboard "conspiracy" wall with red string, a CRT, a boarded
window, a pizza box. The chapters describe a quiet sickroom in an old
country house: "The safehouse is a small frame house on a county road
thirty-two miles southeast of the FM-3411 exit, on a property owned, on
paper, by a woman named Linda Caldwell ... Diego is in the back bedroom.
A doctor ... is at his bedside. She has set the IV." "Diego's
grandmother is in the front room, on the phone ... Hal is in the
kitchen, making sandwiches ... Claire is on the back porch." (ch6) —
"Diego's grandmother — Graciela Ramos ... Outside, on the porch ... is on
the phone." (ch7) — "She sets the slushie on the bedside table. She sits
in the chair beside the bed ... Dr. Patel comes in once and out once.
Diego's grandmother is on the back porch. Doyle is in the kitchen making
coffee." (ch9)

Plan (5.2 x 4.8 m, ceiling 2.7, an old frame house's back bedroom):
the bed head to the W wall with a patchwork quilt, the IV pole and its
bag at the head, the line down to the bed; the bedside table on the
room side (the lamp, the slushie with its taped lid and red spoon, the
water glass, his phone, Sam's spiral notebook, the pill bottles); the
chair beside the bed; the dresser on the E wall with a doily, Linda
Caldwell's old photographs and Dr. Patel's supplies (gauze, the saline
bags, gloves); a rag rug; the ceiling fan with its light; painted walls
and a picture rail; the N window onto the BACK PORCH (Graciela's chair,
her phone calls) and the yard, the clothesline, the post oaks, the field;
the door to the hall, its bulb, the kitchen's light at the hall's end.

Draft 4 targets: the front room and the kitchen (Hal's sandwiches,
Doyle's coffee) as their own presets; night on the porch (ch6 is
candlelight_low) with the porch bulb as a practical; Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_tube, make_lathe, make_chamfer_box, make_rot_box, make_blob, export_glb
from _props.structure import make_floor, make_wall, make_wall_with_openings
from _props.furniture import make_bed, make_chair, make_lamp
from _props.detail import make_wall_outlet, make_light_switch, make_traffic_wear, make_far_bands
from _props.trees import make_broadleaf

ROOM_W = 5.2; ROOM_D = 4.8; CEIL = 2.7
XW, XE, YS, YN = -ROOM_W / 2.0, ROOM_W / 2.0, 0.0, ROOM_D
FW, FE, FS, FN = XW + 0.10, XE - 0.10, YS + 0.10, YN - 0.10     # wall faces
DOOR_X, DOOR_W, DOOR_H = -1.55, 0.90, 2.05
WIN_X, WIN_W, WIN_Z, WIN_H = 0.65, 1.20, 1.45, 1.25
WIN_E_Y = 3.10
HALL_Y0 = -1.35
GROUND_Z = -0.60                     # the house stands on piers
PAL = {"wall": (0.78, 0.82, 0.72, 1.0), "baseboard": (0.86, 0.84, 0.78, 1.0)}
WOOD = (0.46, 0.32, 0.20, 1.0); WOOD_DK = (0.34, 0.23, 0.14, 1.0)
WHITE = (0.94, 0.93, 0.89, 1.0); STEEL = (0.72, 0.74, 0.76, 1.0)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": (0.56, 0.42, 0.28, 1.0), "seam": (0.36, 0.26, 0.16, 1.0)})
    make_wall("Wall_W", (XW, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_E", (XE, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y', palette=PAL,
                            baseboard_face_sign=-1, openings=[(WIN_E_Y, 1.45, 0.80, 1.10)])
    make_wall_with_openings("Wall_N", (0.0, YN, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=-1, openings=[(WIN_X, WIN_Z, WIN_W, WIN_H)])
    make_wall_with_openings("Wall_S", (0.0, YS, 0), length=ROOM_W + 0.4, height=CEIL, axis='X', palette=PAL,
                            baseboard_face_sign=+1, openings=[(DOOR_X, DOOR_H / 2.0, DOOR_W, DOOR_H)])
    make_box("Ceil", (0.0, ROOM_D / 2.0, CEIL + 0.05), (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), (0.92, 0.91, 0.86, 1.0))
    # the picture rail round the room
    for tag, c, s in (("N", (0.0, FN - 0.015, 2.20), (ROOM_W - 0.2, 0.03, 0.04)), ("S", (0.0, FS + 0.015, 2.20), (ROOM_W - 0.2, 0.03, 0.04)),
                      ("W", (FW + 0.015, ROOM_D / 2.0, 2.20), (0.03, ROOM_D - 0.26, 0.04)), ("E", (FE - 0.015, ROOM_D / 2.0, 2.20), (0.03, ROOM_D - 0.26, 0.04))):
        make_box(f"Picture_Rail_{tag}", c, s, WHITE)
    # window frames, sashes, sills; the door casing; the door leaf open into the room
    wx0, wx1, wz0, wz1 = WIN_X - WIN_W / 2.0, WIN_X + WIN_W / 2.0, WIN_Z - WIN_H / 2.0, WIN_Z + WIN_H / 2.0
    for nm, c, s in (("Window_N_Frame_L", (wx0 + 0.03, FN, WIN_Z), (0.06, 0.08, WIN_H)), ("Window_N_Frame_R", (wx1 - 0.03, FN, WIN_Z), (0.06, 0.08, WIN_H)),
                     ("Window_N_Frame_T", (WIN_X, FN, wz1 - 0.03), (WIN_W, 0.08, 0.06)), ("Window_N_Meeting_Rail", (WIN_X, FN, WIN_Z), (WIN_W - 0.12, 0.05, 0.05))):
        make_box(nm, c, s, WHITE)
    make_box("Window_N_Sill", (WIN_X, FN - 0.07, wz0 - 0.02), (WIN_W + 0.12, 0.16, 0.04), WHITE)
    make_box("Window_N_Glass", (WIN_X, YN, WIN_Z), (WIN_W, 0.01, WIN_H), (0.74, 0.80, 0.84, 0.18))
    for i, cx in enumerate((wx0 - 0.10, wx1 + 0.10)):
        make_box(f"Curtain_N_{i}", (cx, FN - 0.05, 1.50), (0.30, 0.04, 1.60), (0.92, 0.88, 0.76, 1.0))
    make_cyl("Curtain_Rod_N", (WIN_X, FN - 0.05, 2.33), 0.012, WIN_W + 0.80, STEEL, axis='X', segments=6)
    for i, cx in enumerate((WIN_X - WIN_W / 2.0 - 0.36, WIN_X + WIN_W / 2.0 + 0.36)):
        make_box(f"Curtain_Rod_Bracket_{i}", (cx, FN - 0.03, 2.33), (0.02, 0.06, 0.03), STEEL)
    make_box("Window_E_Sill", (FE - 0.07, WIN_E_Y, 0.88), (0.16, 0.92, 0.04), WHITE)
    make_box("Window_E_Glass", (XE, WIN_E_Y, 1.45), (0.01, 0.80, 1.10), (0.74, 0.80, 0.84, 0.18))
    make_box("Window_E_Meeting_Rail", (XE, WIN_E_Y, 1.45), (0.05, 0.80, 0.05), WHITE)
    for i, (x0, x1) in enumerate(((DOOR_X - DOOR_W / 2.0 - 0.05, DOOR_X - DOOR_W / 2.0), (DOOR_X + DOOR_W / 2.0, DOOR_X + DOOR_W / 2.0 + 0.05))):
        make_box(f"Door_Casing_{i}", ((x0 + x1) / 2.0, FS + 0.01, DOOR_H / 2.0), (0.05, 0.02, DOOR_H), WHITE)
    make_box("Door_Casing_Head", (DOOR_X, FS + 0.01, DOOR_H + 0.03), (DOOR_W + 0.10, 0.02, 0.06), WHITE)
    hx = DOOR_X + DOOR_W / 2.0
    ang = math.radians(80.0)
    make_rot_box("Door_Leaf", (hx - math.cos(ang) * 0.42, FS + math.sin(ang) * 0.42 + 0.02, 1.01), (0.84, 0.04, 2.00), WHITE, yaw=-ang)
    make_cyl("Door_Knob", (hx - math.cos(ang) * 0.76 + 0.03, FS + math.sin(ang) * 0.76, 0.95), 0.025, 0.05, (0.72, 0.62, 0.36, 1.0), axis='X', segments=8)


def build_bed():
    bx, by = FW + 1.02, 2.55
    make_bed("Bed", bx, by, head="-X", w=1.40, d=2.00, style="frame", frame_col=WOOD_DK,
             blanket_col=(0.62, 0.44, 0.42, 1.0), pillows=2, made=False, headboard=True)
    # where her hand holds his on the quilt (ch9 "She takes his hand. He sleeps, holding her hand.")
    make_box("Hands_Sheet_Crease", (bx - 0.22, by - 0.45, 0.551), (0.16, 0.12, 0.002), (0.84, 0.82, 0.78, 1.0))
    # the IV pole at the head on the window side, its bag, the line down to his arm
    px, py = FW + 0.42, by + 0.98
    make_cyl("IV_Pole_Base", (px, py, 0.02), 0.26, 0.04, STEEL, segments=5)
    make_cyl("IV_Pole", (px, py, 0.98), 0.014, 1.88, STEEL, segments=8)
    make_tube("IV_Pole_Hooks", [(px - 0.10, py, 1.90), (px, py, 1.93), (px + 0.10, py, 1.90)], 0.006, STEEL, segments=4)
    make_box("IV_Bag", (px + 0.06, py, 1.74), (0.10, 0.03, 0.24), (0.88, 0.92, 0.94, 0.65))
    make_box("IV_Bag_Label", (px + 0.06, py - 0.016, 1.76), (0.06, 0.002, 0.06), WHITE)
    make_tube("IV_Line", [(px + 0.06, py, 1.61), (px + 0.20, py - 0.20, 1.20), (px + 0.45, py - 0.55, 0.80), (bx - 0.40, by + 0.35, 0.69)], 0.004,
              (0.86, 0.90, 0.92, 0.7), segments=4)
    make_cyl("IV_Drip_Chamber", (px + 0.06, py, 1.58), 0.012, 0.05, (0.86, 0.90, 0.92, 0.7), segments=6)


def build_bedside():
    """The bedside table on the room side of the head, the chair beside
    the bed facing it — Sam's chair."""
    tx, ty = FW + 0.30, 1.48
    make_box("Bedside_Table_Top", (tx, ty, 0.62), (0.46, 0.42, 0.03), WOOD)
    make_box("Bedside_Table_Body", (tx, ty, 0.36), (0.42, 0.38, 0.50), WOOD_DK)
    make_box("Bedside_Table_Drawer", (tx + 0.212, ty, 0.50), (0.006, 0.32, 0.14), WOOD)
    make_cyl("Bedside_Table_Drawer_Knob", (tx + 0.222, ty, 0.50), 0.012, 0.02, (0.72, 0.62, 0.36, 1.0), axis='X', segments=6)
    for i, (lx, ly) in enumerate(((-0.18, -0.16), (0.18, -0.16), (-0.18, 0.16), (0.18, 0.16))):
        make_box(f"Bedside_Table_Leg_{i}", (tx + lx, ty + ly, 0.055), (0.04, 0.04, 0.11), WOOD_DK)
    top = 0.635
    make_lamp("Bedside_Lamp", tx - 0.10, ty + 0.10, base_z=top, h=0.46, shade_col=(0.94, 0.88, 0.72, 1.0), body_col=(0.64, 0.56, 0.44, 1.0))
    # the slushie: blue raspberry, the lid taped, the red spoon through the cross-cut
    make_lathe("Slushie_Cup", (tx + 0.12, ty - 0.10, top), [(0.0, 0.0), (0.035, 0.0), (0.045, 0.15), (0.0, 0.15)], WHITE, segments=12)
    make_cyl("Slushie_Fill", (tx + 0.12, ty - 0.10, top + 0.152), 0.044, 0.004, (0.24, 0.46, 0.86, 1.0), segments=12)
    make_cyl("Slushie_Lid", (tx + 0.12, ty - 0.10, top + 0.158), 0.047, 0.008, (0.88, 0.90, 0.92, 0.8), segments=12)
    make_box("Slushie_Tape", (tx + 0.12, ty - 0.10, top + 0.1625), (0.10, 0.02, 0.001), (0.92, 0.90, 0.80, 1.0))
    make_rot_box("Slushie_Spoon", (tx + 0.12, ty - 0.10, top + 0.21), (0.012, 0.004, 0.12), (0.86, 0.18, 0.16, 1.0), roll=0.15)
    make_lathe("Water_Glass", (tx - 0.06, ty - 0.12, top), [(0.0, 0.0), (0.03, 0.0), (0.034, 0.11), (0.0, 0.11)], (0.80, 0.86, 0.90, 0.5), segments=10)
    make_box("Diego_Phone", (tx + 0.04, ty + 0.12, top + 0.005), (0.07, 0.14, 0.01), (0.10, 0.10, 0.12, 1.0))
    make_box("Sam_Notebook", (tx - 0.02, ty - 0.02, top + 0.006), (0.15, 0.20, 0.012), (0.30, 0.46, 0.70, 1.0))
    make_box("Sam_Notebook_Wire", (tx - 0.095, ty - 0.02, top + 0.007), (0.01, 0.20, 0.014), STEEL)
    for i, (dx, dy) in enumerate(((0.16, 0.12), (0.19, 0.06))):
        make_lathe(f"Pill_Bottle_{i}", (tx + dx, ty + dy, top), [(0.0, 0.0), (0.018, 0.0), (0.018, 0.06), (0.0, 0.06)], (0.86, 0.52, 0.22, 0.85), segments=8)
    # the chair beside the bed, facing it
    make_chair("Bedside_Chair", FW + 1.30, 1.18, yaw=0.0, wood=WOOD, seat_col=(0.56, 0.40, 0.30, 1.0), w=0.44)


def build_dresser_and_room():
    dx = FE - 0.26
    dy = 1.30
    make_box("Dresser_Body", (dx, dy, 0.45), (0.48, 1.10, 0.90), WOOD)
    make_box("Dresser_Top", (dx - 0.01, dy, 0.915), (0.52, 1.14, 0.03), WOOD_DK)
    for r in range(3):
        for c in range(2):
            make_box(f"Dresser_Drawer_{r}_{c}", (dx - 0.243, dy - 0.27 + c * 0.54, 0.20 + r * 0.26), (0.006, 0.50, 0.22), WOOD_DK)
            make_cyl(f"Dresser_Knob_{r}_{c}", (dx - 0.252, dy - 0.27 + c * 0.54, 0.20 + r * 0.26), 0.015, 0.02, (0.72, 0.62, 0.36, 1.0), axis='X', segments=6)
    make_box("Dresser_Mirror", (FE - 0.03, dy, 1.45), (0.02, 0.70, 0.80), (0.70, 0.74, 0.76, 0.85))
    make_box("Dresser_Mirror_Frame", (FE - 0.015, dy, 1.45), (0.01, 0.80, 0.90), WOOD_DK)
    top = 0.93
    make_box("Dresser_Doily", (dx - 0.02, dy + 0.20, top + 0.001), (0.34, 0.46, 0.002), WHITE)
    # Linda Caldwell's old photographs, standing in frames
    for i, (py, h, col) in enumerate(((dy + 0.32, 0.22, (0.60, 0.54, 0.44, 1.0)), (dy + 0.10, 0.16, (0.52, 0.48, 0.42, 1.0)))):
        make_rot_box(f"Old_Photo_{i}", (dx - 0.02, py, top + h / 2.0), (0.03, 0.14, h), WOOD_DK, yaw=0.2, pitch=0.0)
        make_rot_box(f"Old_Photo_{i}_Print", (dx - 0.037, py, top + h / 2.0), (0.002, 0.10, h - 0.05), col, yaw=0.2)
    # Dr. Patel's supplies: the gauze, two saline bags, the gloves box, tape
    make_box("Med_Tray", (dx - 0.02, dy - 0.28, top + 0.01), (0.34, 0.44, 0.02), STEEL)
    make_box("Gauze_Box", (dx - 0.06, dy - 0.40, top + 0.06), (0.12, 0.14, 0.08), WHITE)
    for i in range(2):
        make_box(f"Saline_Bag_{i}", (dx + 0.04, dy - 0.18 + i * 0.05, top + 0.035 + i * 0.03), (0.16, 0.10, 0.03), (0.86, 0.92, 0.94, 0.7))
    make_box("Gloves_Box", (dx + 0.10, dy + 0.42, top + 0.05), (0.12, 0.24, 0.10), (0.30, 0.52, 0.72, 1.0))
    make_cyl("Med_Tape", (dx + 0.08, dy - 0.48, top + 0.035), 0.03, 0.025, WHITE, segments=10)
    # the rag rug, the ceiling fan, the switch and outlets
    make_box("Rag_Rug", (-0.30, 1.40, 0.005), (1.60, 1.10, 0.01), (0.50, 0.46, 0.56, 1.0))
    for i in range(4):
        make_box(f"Rag_Rug_Band_{i}", (-0.30, 1.00 + i * 0.26, 0.011), (1.56, 0.05, 0.002), [(0.70, 0.40, 0.36, 1.0), (0.40, 0.56, 0.62, 1.0)][i % 2])
    fx, fy = -0.20, 2.40
    make_cyl("Fan_Downrod", (fx, fy, CEIL - 0.15), 0.015, 0.30, WHITE, segments=6)
    make_cyl("Fan_Motor", (fx, fy, CEIL - 0.36), 0.11, 0.12, WHITE, segments=12)
    for bi, (ddx, ddy, sw, sd) in enumerate(((0.38, 0, 0.56, 0.13), (-0.38, 0, 0.56, 0.13), (0, 0.38, 0.13, 0.56), (0, -0.38, 0.13, 0.56))):
        make_box(f"Fan_Blade_{bi}", (fx + ddx, fy + ddy, CEIL - 0.39), (sw, sd, 0.015), WOOD)
    make_lathe("Fan_Globe", (fx, fy, CEIL - 0.52), [(0.0, 0.0), (0.07, 0.02), (0.08, 0.08), (0.04, 0.10), (0.0, 0.10)], (0.96, 0.92, 0.80, 1.0), segments=10)
    make_light_switch("Switch_Door", (DOOR_X + DOOR_W / 2.0 + 0.25, YS), axis='X', face_sign=1)
    make_wall_outlet("Outlet_W", (XW, 0.90), axis='Y', face_sign=1)
    make_wall_outlet("Outlet_E", (XE, 2.40), axis='Y', face_sign=-1)
    make_traffic_wear("Wear_Door_Bed", [(DOOR_X, 0.30), (-1.4, 0.95)], width=0.6)


def build_hall():
    """Through the door: the hall, its bulb, the kitchen's light at the
    end (Doyle making coffee)."""
    hx0, hx1 = XW, XE
    make_box("Hall_Floor", ((hx0 + hx1) / 2.0, (HALL_Y0 + YS) / 2.0 - 0.05, -0.05), (hx1 - hx0, -HALL_Y0 - 0.10, 0.10), (0.56, 0.42, 0.28, 1.0))
    make_box("Hall_Ceil", ((hx0 + hx1) / 2.0, (HALL_Y0 + YS) / 2.0, CEIL + 0.05), (hx1 - hx0, -HALL_Y0, 0.10), (0.92, 0.91, 0.86, 1.0))
    make_wall("Hall_Wall_S", ((hx0 + hx1) / 2.0, HALL_Y0 - 0.10, 0), length=hx1 - hx0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall("Hall_Wall_E", (hx1 + 0.10, (HALL_Y0 + YS) / 2.0, 0), length=-HALL_Y0, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_box("Hall_Print", (DOOR_X + 0.10, HALL_Y0 + 0.012, 1.55), (0.50, 0.025, 0.40), WOOD_DK)
    make_box("Hall_Print_Field", (DOOR_X + 0.10, HALL_Y0 + 0.027, 1.55), (0.40, 0.006, 0.30), (0.70, 0.66, 0.50, 1.0))
    make_cyl("Hall_Bulb_Base", (DOOR_X, (HALL_Y0 + YS) / 2.0, CEIL - 0.03), 0.07, 0.06, WHITE, segments=10)
    make_lathe("Hall_Bulb", (DOOR_X, (HALL_Y0 + YS) / 2.0, CEIL - 0.14), [(0.0, 0.0), (0.03, 0.01), (0.035, 0.05), (0.02, 0.08), (0.0, 0.08)], (1.0, 0.94, 0.80, 1.0), segments=8)
    # the kitchen through the hall's west end: its doorway lit, the counter's edge
    make_box("Kitchen_Floor", (XW - 1.6, (HALL_Y0 + YS) / 2.0, -0.05), (3.0, -HALL_Y0 + 1.0, 0.10), (0.70, 0.66, 0.56, 1.0))
    make_box("Kitchen_Wall_W", (XW - 3.1, (HALL_Y0 + YS) / 2.0, CEIL / 2.0), (0.20, -HALL_Y0 + 1.0, CEIL), (0.90, 0.86, 0.66, 1.0))
    make_box("Kitchen_Counter", (XW - 2.65, (HALL_Y0 + YS) / 2.0, 0.45), (0.65, 1.20, 0.90), (0.62, 0.50, 0.36, 1.0))
    make_box("Kitchen_Counter_Top", (XW - 2.65, (HALL_Y0 + YS) / 2.0, 0.92), (0.69, 1.24, 0.04), (0.80, 0.78, 0.72, 1.0))
    make_lathe("Kitchen_Coffee_Pot", (XW - 2.60, (HALL_Y0 + YS) / 2.0 + 0.2, 0.94), [(0.0, 0.0), (0.07, 0.0), (0.08, 0.12), (0.05, 0.18), (0.0, 0.18)], (0.30, 0.26, 0.22, 0.8), segments=10)
    make_box("Kitchen_Ceil", (XW - 1.6, (HALL_Y0 + YS) / 2.0, CEIL + 0.05), (3.2, -HALL_Y0 + 1.0, 0.10), (0.92, 0.91, 0.86, 1.0))


def build_outside():
    """The back porch beyond the N window, the yard, the clothesline,
    the post oaks, the field to the treeline; the side yard E."""
    gz = GROUND_Z
    make_box("Ground", (0.0, 20.0, gz - 0.02), (160.0, 160.0, 0.04), (0.44, 0.48, 0.30, 1.0))
    # the porch: deck on its joists, posts, the shed roof, the rail, the chair she phones from
    py0, py1 = YN + 0.10, YN + 2.50
    make_box("Porch_Deck", (0.6, (py0 + py1) / 2.0, -0.05), (6.0, py1 - py0, 0.10), (0.56, 0.48, 0.38, 1.0))
    for i in range(14):
        make_box(f"Porch_Deck_Seam_{i}", (-2.3 + i * 0.44, (py0 + py1) / 2.0, 0.0005), (0.01, py1 - py0, 0.001), (0.40, 0.34, 0.26, 1.0))
    make_box("Porch_Fascia", (0.6, py1 - 0.03, -0.20), (6.0, 0.06, 0.30), (0.56, 0.48, 0.38, 1.0))
    for i, x in enumerate((-2.25, 0.6, 3.45)):
        make_box(f"Porch_Post_{i}", (x, py1 - 0.10, 1.25), (0.11, 0.11, 2.50), WHITE)
        make_box(f"Porch_Pier_{i}", (x, py1 - 0.10, gz / 2.0 - 0.10), (0.22, 0.22, -gz - 0.20 + 0.0), (0.56, 0.54, 0.50, 1.0))
    make_box("Porch_Beam", (0.6, py1 - 0.10, 2.56), (6.0, 0.14, 0.14), WHITE)
    make_rot_box("Porch_Roof", (0.6, (py0 + py1) / 2.0 + 0.10, 2.80), (6.3, py1 - py0 + 0.6, 0.06), (0.46, 0.46, 0.48, 1.0), roll=0.0, pitch=0.0)
    make_box("Porch_Rail", (0.6, py1 - 0.10, 0.90), (5.6, 0.06, 0.06), WHITE)
    for i in range(16):
        make_box(f"Porch_Baluster_{i}", (-2.0 + i * 0.35, py1 - 0.10, 0.47), (0.03, 0.03, 0.82), WHITE)
    make_box("Porch_Step", (2.6, py1 + 0.25, -0.30), (1.1, 0.40, 0.08), (0.56, 0.48, 0.38, 1.0))
    # Graciela's chair: the metal porch glider, a cushion, her mug on the boards
    gx, gy = 1.55, py0 + 1.00
    make_box("Porch_Glider_Seat", (gx, gy, 0.44), (1.10, 0.50, 0.06), (0.36, 0.52, 0.44, 1.0))
    make_box("Porch_Glider_Back", (gx, gy - 0.27, 0.74), (1.10, 0.05, 0.56), (0.36, 0.52, 0.44, 1.0))
    for i, x in enumerate((-0.52, 0.52)):
        make_box(f"Porch_Glider_Frame_{i}", (gx + x, gy, 0.21), (0.05, 0.56, 0.42), (0.30, 0.42, 0.36, 1.0))
    make_box("Porch_Glider_Cushion", (gx, gy, 0.49), (1.00, 0.44, 0.05), (0.86, 0.74, 0.52, 1.0))
    make_lathe("Porch_Mug", (gx + 0.70, gy, 0.0), [(0.0, 0.0), (0.04, 0.0), (0.04, 0.10), (0.0, 0.10)], (0.74, 0.30, 0.24, 1.0), segments=10)
    # the yard: the clothesline, the post oaks, the fence, the field
    for i, (x, y) in enumerate(((-3.0, 12.0), (4.0, 12.0))):
        make_box(f"Clothesline_Post_{i}", (x, y, gz + 1.0), (0.08, 0.08, 2.0), (0.62, 0.62, 0.60, 1.0))
        make_box(f"Clothesline_Bar_{i}", (x, y, gz + 1.95), (0.08, 0.80, 0.06), (0.62, 0.62, 0.60, 1.0))
    for j, dy in enumerate((-0.30, 0.0, 0.30)):
        make_tube(f"Clothesline_Wire_{j}", [(-3.0, 12.0 + dy, gz + 1.92), (0.5, 12.0 + dy, gz + 1.80), (4.0, 12.0 + dy, gz + 1.92)], 0.006, (0.70, 0.70, 0.68, 1.0), segments=4)
    make_box("Clothesline_Sheet", (1.4, 12.0, gz + 1.45), (0.90, 0.02, 0.70), WHITE)
    for i, (x, y, h) in enumerate(((-7.0, 15.0, 7.5), (9.0, 17.0, 8.5), (2.0, 24.0, 7.0), (-12.0, 9.0, 6.5))):
        make_broadleaf(f"Post_Oak_{i}", x, y, h, (0.30, 0.40, 0.22, 1.0), (0.36, 0.30, 0.24, 1.0), crown=0.36)
    for i in range(16):
        make_box(f"Fence_Post_{i}", (-24.0 + i * 3.2, 30.0, gz + 0.60), (0.10, 0.10, 1.20), (0.50, 0.46, 0.40, 1.0))
    for j, z in enumerate((0.45, 0.95)):
        make_box(f"Fence_Wire_{j}", (0.0, 30.0, gz + z), (48.0, 0.01, 0.01), (0.56, 0.56, 0.54, 1.0))
    make_box("Field", (0.0, 52.0, gz - 0.005), (120.0, 40.0, 0.02), (0.62, 0.58, 0.36, 1.0))
    make_far_bands("FarTrees", (0.22, 0.30, 0.18), [(70.0, 90.0, 7.0, 0.85), (140.0, 170.0, 9.0, 0.6)], cx=0.0, cy=10.0, profile="treeline")


def main():
    clear_scene()
    build_shell(); build_bed(); build_bedside(); build_dresser_and_room(); build_hall(); build_outside()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/safehouse_bedroom.glb"))
    print(f"\n[build_safehouse_bedroom] exporting to {out}")
    export_glb(out)


if __name__ == "__main__": main()
