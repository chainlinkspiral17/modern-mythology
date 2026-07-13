"""safehouse_bedroom — vol5-7 hideout bedroom.

Was near-bare (bed + desk-top + a floating monitor + a bare bulb).
Enriched to a lived-in safehouse: a real bed (headboard/pillow/duvet),
a nightstand with a lamp + table clock + mug, a work desk with a CRT +
keyboard + papers + gooseneck lamp and a chair, a dresser, a
footlocker + a canvas duffel at the foot of the bed, a boarded-over
front window beside the door, a corkboard "conspiracy" wall of pinned
notes + a map + red string, a mini-fridge, a floor rug, and lived-in
clutter (stacked books, cans, a pizza box).

Room: door/S wall at blender y=0, extends +Y; interior lands at
godot -Z. Props kept inside the 4.0 x 5.0 footprint.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_fluorescent_tube_fixture

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall":(0.78,0.70,0.58,1.0),"baseboard":(0.42,0.32,0.22,1.0)}
COL_FLOOR = (0.62,0.52,0.42,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.20,1.0)
COL_ACCENT = (0.78,0.42,0.22,1.0)
COL_SHEET = (0.86,0.82,0.74,1.0); COL_DUVET = (0.46,0.36,0.30,1.0)
COL_METAL = P.METAL_STEEL; COL_DARK = (0.24,0.22,0.20,1.0)
COL_CANVAS = (0.44,0.46,0.34,1.0); COL_CORK = (0.72,0.56,0.34,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_door():
    # A door leaf hung in the south opening, ajar, with a knob.
    make_box("Door_Leaf", (-0.55, 0.06, 1.02), (0.90, 0.06, 2.04), COL_WOOD)
    make_box("Door_Panel_U", (-0.55, 0.10, 1.45), (0.62, 0.02, 0.60), (0.36, 0.26, 0.18, 1.0))
    make_box("Door_Panel_L", (-0.55, 0.10, 0.60), (0.62, 0.02, 0.60), (0.36, 0.26, 0.18, 1.0))
    make_cyl("Door_Knob", (-0.12, 0.12, 1.00), 0.04, 0.06, (0.72, 0.62, 0.32, 1.0), axis='Y', segments=8)
    for hi, hz in enumerate([0.30, 1.02, 1.74]):
        make_cyl(f"Door_Hinge_{hi}", (-1.00, 0.05, hz), 0.02, 0.10, P.METAL_BLACK, axis='Z', segments=6)

def build_bed():
    bx, by = -1.05, 2.60
    make_box("Bed_Frame", (bx, by, 0.20), (1.20, 1.90, 0.20), COL_WOOD)
    make_box("Bed_Mattress", (bx, by, 0.40), (1.10, 1.80, 0.16), (0.86, 0.80, 0.72, 1.0))
    make_box("Bed_Headboard", (bx, by+0.98, 0.78), (1.22, 0.10, 0.72), COL_WOOD)
    make_box("Bed_Pillow", (bx, by+0.68, 0.54), (1.02, 0.42, 0.14), COL_SHEET)
    make_box("Bed_Sheet", (bx, by-0.10, 0.50), (1.12, 1.20, 0.06), COL_SHEET)
    make_box("Bed_Duvet", (bx, by-0.35, 0.54), (1.14, 1.10, 0.16), COL_DUVET)
    make_box("Bed_DuvetFold", (bx, by+0.18, 0.60), (1.14, 0.30, 0.10), COL_ACCENT)

def build_nightstand():
    nx, ny = -1.72, 3.95
    make_box("Night_Body", (nx, ny, 0.28), (0.44, 0.42, 0.56), COL_WOOD)
    make_box("Night_Drawer", (nx-0.20, ny, 0.36), (0.03, 0.34, 0.16), (0.34, 0.24, 0.16, 1.0))
    make_cyl("Night_Pull", (nx-0.22, ny, 0.36), 0.02, 0.04, P.METAL_BLACK, axis='X', segments=6)
    top = 0.58
    # Gooseneck-free table lamp: base + column + drum shade
    make_cyl("Lamp_Base", (nx+0.10, ny+0.08, top+0.02), 0.08, 0.04, P.METAL_BLACK, segments=10)
    make_cyl("Lamp_Column", (nx+0.10, ny+0.08, top+0.18), 0.02, 0.30, P.METAL_STEEL, segments=8)
    make_cyl("Lamp_Shade", (nx+0.10, ny+0.08, top+0.36), 0.11, 0.14, (0.94, 0.82, 0.52, 1.0), segments=10)
    # Table clock (a small boxy alarm clock with a red face)
    make_box("Clock_Body", (nx-0.10, ny-0.08, top+0.06), (0.14, 0.10, 0.10), COL_DARK)
    make_box("Clock_Face", (nx-0.10, ny-0.14, top+0.06), (0.10, 0.005, 0.06), (0.86, 0.22, 0.18, 1.0))
    # Mug
    make_cyl("Night_Mug", (nx+0.14, ny-0.12, top+0.05), 0.04, 0.09, (0.42, 0.46, 0.52, 1.0), segments=10)

def build_desk():
    dx, dy = 0.35, 4.55
    make_box("Desk_Top", (dx, dy, 0.74), (1.60, 0.62, 0.05), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.72,-0.24),(0.72,-0.24),(-0.72,0.24),(0.72,0.24)]):
        make_box(f"Desk_Leg_{i}", (dx+lx, dy+ly, 0.37), (0.06, 0.06, 0.74), COL_DARK)
    # Chunky CRT monitor + keyboard + tower
    make_box("CRT_Body", (dx-0.15, dy+0.14, 1.05), (0.52, 0.44, 0.42), (0.34, 0.34, 0.30, 1.0))
    make_box("CRT_Screen", (dx-0.15, dy-0.10, 1.06), (0.40, 0.02, 0.32), (0.16, 0.28, 0.30, 1.0))
    make_box("Keyboard", (dx-0.15, dy-0.18, 0.78), (0.44, 0.16, 0.03), (0.30, 0.30, 0.28, 1.0))
    make_box("PC_Tower", (dx+0.62, dy+0.05, 0.98), (0.20, 0.44, 0.46), COL_DARK)
    make_box("PC_LED", (dx+0.52, dy-0.14, 1.05), (0.01, 0.03, 0.03), (0.32, 0.86, 0.42, 1.0))
    # Scattered work-papers + a stack of folders
    for pi, (px, py) in enumerate([(dx+0.30,dy+0.08),(dx+0.44,dy+0.16)]):
        make_box(f"Desk_Paper_{pi}", (px, py, 0.775), (0.24, 0.30, 0.01), P.PAPER)
    make_box("Desk_Folders", (dx-0.62, dy+0.10, 0.82), (0.24, 0.32, 0.10), (0.72, 0.62, 0.34, 1.0))
    # Gooseneck desk lamp clamped to the back edge
    make_cyl("DeskLamp_Base", (dx+0.55, dy+0.24, 0.79), 0.05, 0.03, P.METAL_BLACK, segments=8)
    make_cyl("DeskLamp_Arm1", (dx+0.55, dy+0.24, 0.95), 0.015, 0.30, P.METAL_STEEL, segments=6)
    make_cyl("DeskLamp_Arm2", (dx+0.40, dy+0.10, 1.12), 0.015, 0.32, P.METAL_STEEL, axis='X', segments=6)
    make_cyl("DeskLamp_Head", (dx+0.24, dy+0.02, 1.10), 0.06, 0.10, COL_DARK, segments=8)

def build_chair():
    cx, cy = 0.35, 3.85
    make_box("Chair_Seat", (cx, cy, 0.46), (0.44, 0.44, 0.05), COL_WOOD)
    make_box("Chair_Back", (cx, cy+0.20, 0.72), (0.44, 0.04, 0.46), COL_WOOD)
    for i, (lx, ly) in enumerate([(-0.18,-0.18),(0.18,-0.18),(-0.18,0.18),(0.18,0.18)]):
        make_box(f"Chair_Leg_{i}", (cx+lx, cy+ly, 0.22), (0.05, 0.05, 0.44), COL_DARK)

def build_dresser():
    dx, dy = 1.66, 2.60
    make_box("Dresser_Body", (dx, dy, 0.46), (0.52, 1.20, 0.92), COL_WOOD)
    for di, dz in enumerate([0.24, 0.54, 0.84]):
        make_box(f"Dresser_Drawer_{di}", (dx-0.24, dy, dz), (0.03, 1.06, 0.24), (0.34, 0.24, 0.16, 1.0))
        for pk in (-0.26, 0.26):
            make_cyl(f"Dresser_Pull_{di}_{'L' if pk<0 else 'R'}", (dx-0.27, dy+pk, dz), 0.02, 0.05, P.METAL_BLACK, axis='X', segments=6)
    # On top: a boxy transistor radio + a stack of clothes
    make_box("Dresser_Radio", (dx-0.05, dy-0.32, 1.00), (0.26, 0.18, 0.16), COL_DARK)
    make_cyl("Dresser_RadioDial", (dx-0.19, dy-0.32, 1.00), 0.03, 0.02, (0.82, 0.72, 0.42, 1.0), axis='X', segments=8)
    make_box("Dresser_Clothes", (dx-0.02, dy+0.34, 1.00), (0.34, 0.34, 0.14), (0.52, 0.42, 0.40, 1.0))

def build_footlocker():
    # Steel footlocker at the foot of the bed + a canvas duffel beside it.
    fx, fy = -1.05, 1.10
    make_box("Locker_Body", (fx, fy, 0.20), (1.00, 0.48, 0.40), COL_DARK)
    make_box("Locker_Lid", (fx, fy, 0.42), (1.02, 0.50, 0.06), (0.30, 0.28, 0.26, 1.0))
    for lk in (-0.36, 0.36):
        make_box(f"Locker_Latch_{'L' if lk<0 else 'R'}", (fx+lk, fy-0.25, 0.34), (0.08, 0.02, 0.08), P.METAL_STEEL)
    make_box("Locker_Hasp", (fx, fy-0.25, 0.40), (0.06, 0.02, 0.10), P.METAL_STEEL)
    # Canvas duffel (horizontal cylinder + end caps + strap)
    duf_x, duf_y = 0.55, 0.95
    make_cyl("Duffel_Body", (duf_x, duf_y, 0.22), 0.22, 0.86, COL_CANVAS, axis='X', segments=10)
    for ec in (-0.44, 0.44):
        make_cyl(f"Duffel_End_{'L' if ec<0 else 'R'}", (duf_x+ec, duf_y, 0.22), 0.20, 0.04, (0.38, 0.40, 0.30, 1.0), axis='X', segments=10)
    make_box("Duffel_Strap", (duf_x, duf_y, 0.44), (0.16, 0.06, 0.03), COL_DARK)
    make_box("Duffel_Zip", (duf_x, duf_y-0.20, 0.28), (0.70, 0.03, 0.02), P.METAL_BLACK)

def build_window():
    # Boarded-over front window on the SE south-wall segment.
    wx = 1.45
    make_window("Win_S", (wx, 0.10, 1.45), width=0.90, height=1.20)
    # Nailed planks across the glass (blocking the view out).
    for bi, bz in enumerate([0.95, 1.30, 1.65]):
        make_box(f"Win_Board_{bi}", (wx, 0.14, bz), (1.02, 0.04, 0.18), COL_WOOD)
    make_box("Win_BoardDiag", (wx, 0.15, 1.30), (1.10, 0.03, 0.12), (0.36, 0.26, 0.18, 1.0))
    # Half-drawn curtain to one side.
    make_box("Win_Curtain", (wx-0.55, 0.16, 1.45), (0.18, 0.05, 1.30), (0.42, 0.30, 0.34, 1.0))
    make_box("Win_Rod", (wx, 0.20, 2.12), (1.10, 0.03, 0.03), P.METAL_BLACK)

def build_corkboard():
    # The "conspiracy" wall over the desk: cork panel, pinned notes,
    # a map, pushpins, and red string linking clues.
    bx, bz = 0.35, 1.95
    make_box("Cork_Panel", (bx, ROOM_D-0.09, bz), (1.60, 0.03, 0.90), COL_CORK)
    make_box("Cork_Frame_T", (bx, ROOM_D-0.10, bz+0.47), (1.66, 0.04, 0.06), COL_DARK)
    make_box("Cork_Frame_B", (bx, ROOM_D-0.10, bz-0.47), (1.66, 0.04, 0.06), COL_DARK)
    # A muted street map pinned centre-left
    make_box("Cork_Map", (bx-0.42, ROOM_D-0.11, bz+0.05), (0.52, 0.005, 0.44), (0.62, 0.66, 0.58, 1.0))
    # Pinned notes / photos across the board
    notes = [(-0.62,0.30,0.16,0.20,P.PAPER),(0.05,0.34,0.20,0.24,P.PAPER_AGED),
             (0.42,0.28,0.18,0.22,(0.86,0.82,0.62,1.0)),(0.60,-0.06,0.16,0.20,P.PAPER),
             (0.20,-0.24,0.18,0.16,P.PAPER_AGED),(-0.10,-0.20,0.16,0.18,P.PAPER),
             (0.44,-0.30,0.14,0.16,(0.82,0.70,0.60,1.0))]
    for ni, (dy, dz, w, h, col) in enumerate(notes):
        make_box(f"Cork_Note_{ni}", (bx+dy, ROOM_D-0.115, bz+dz), (w, 0.004, h), col)
        make_cyl(f"Cork_Pin_{ni}", (bx+dy, ROOM_D-0.14, bz+dz+h*0.4), 0.012, 0.03, (0.86,0.22,0.18,1.0), axis='Y', segments=6)
    # Red string connecting a few nodes (thin boxes)
    for si, (x0, z0, x1, z1) in enumerate([(-0.42,0.10,0.05,0.34),(0.05,0.34,0.60,-0.06),(0.60,-0.06,0.20,-0.24)]):
        mx, mz = (x0+x1)/2.0, (z0+z1)/2.0
        ln = ((x1-x0)**2 + (z1-z0)**2)**0.5
        make_box(f"Cork_String_{si}", (bx+mx, ROOM_D-0.125, bz+mz), (ln, 0.003, 0.008), (0.82,0.20,0.16,1.0))

def build_minifridge():
    fx, fy = 1.58, 0.85
    make_box("Fridge_Body", (fx, fy, 0.42), (0.56, 0.56, 0.84), (0.86, 0.84, 0.80, 1.0))
    make_box("Fridge_Door", (fx-0.29, fy, 0.42), (0.03, 0.52, 0.80), (0.90, 0.88, 0.84, 1.0))
    make_box("Fridge_Handle", (fx-0.31, fy+0.20, 0.52), (0.03, 0.04, 0.28), P.METAL_STEEL)
    # Clutter on top: a couple of cans + a takeout box
    for ci, cy_off in enumerate([-0.12, 0.06]):
        make_cyl(f"Fridge_Can_{ci}", (fx-0.06, fy+cy_off, 0.90), 0.04, 0.13, P.SNACK_TINTS[ci%len(P.SNACK_TINTS)], segments=10)
    make_box("Fridge_Takeout", (fx+0.10, fy+0.06, 0.89), (0.24, 0.24, 0.10), (0.82, 0.78, 0.66, 1.0))

def build_clutter_and_rug():
    # Floor rug centred under the room
    make_box("Rug", (-0.15, 2.6, 0.015), (1.9, 2.6, 0.02), (0.46, 0.30, 0.28, 1.0))
    make_box("Rug_Border", (-0.15, 2.6, 0.018), (1.7, 2.4, 0.008), (0.58, 0.42, 0.36, 1.0))
    # Stack of paperbacks by the bed
    for bi in range(4):
        col = [(0.62,0.32,0.30,1.0),(0.42,0.52,0.62,1.0),(0.56,0.48,0.32,1.0),(0.34,0.44,0.36,1.0)][bi%4]
        make_box(f"FloorBook_{bi}", (-1.55, 1.7, 0.05+bi*0.05), (0.30, 0.22, 0.05), col)
    # Discarded pizza box + a couple of cans on the floor
    make_box("PizzaBox", (0.85, 2.0, 0.05), (0.50, 0.50, 0.08), (0.82, 0.72, 0.52, 1.0))
    for ci, (cx2, cy2) in enumerate([(1.1, 2.5),(0.6, 2.7)]):
        make_cyl(f"FloorCan_{ci}", (cx2, cy2, 0.07), 0.035, 0.13, P.SNACK_TINTS[(ci+2)%len(P.SNACK_TINTS)], segments=8)

def build_wall_decor():
    make_faded_poster("Poster_W", (-ROOM_W/2.0+0.05, 2.6, 1.90))
    make_calendar("Calendar_E", (ROOM_W/2.0-0.05, 3.9, 1.70))
    make_wall_clock("Clock_N", (-1.30, ROOM_D-0.11, 2.05), frozen_hour=2, frozen_min=18)
    make_floor_plant("Plant", (ROOM_W/2.0-0.55, 4.55, 0.0))

def build_bulb():
    make_cyl("Bulb_Cord", (0.0, ROOM_D/2.0, CEIL-0.30), 0.005, 0.60, P.METAL_BLACK)
    make_cyl("Bulb_Glass", (0.0, ROOM_D/2.0, CEIL-0.86), 0.06, 0.14, (0.96, 0.86, 0.46, 1.0))

def build_ceiling_infra():
    make_fluorescent_tube_fixture("Fluor_0", (0.35, ROOM_D-0.6, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_door()
    build_bed()
    build_nightstand()
    build_desk()
    build_chair()
    build_dresser()
    build_footlocker()
    build_window()
    build_corkboard()
    build_minifridge()
    build_clutter_and_rug()
    build_wall_decor()
    build_bulb()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/safehouse_bedroom.glb"))
    print(f"\n[build_safehouse_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
