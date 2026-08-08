"""board_lords_interior — Kai's SKATEBOARD shop on Main (vol7).

REBUILT 2026-08-03 hero-prop pass: the previous build was a
board-GAME store (gondolas of boxed games, dice case, demo table) —
a wrong-shop read of the name. All five vol7 scenes are a skate
shop: "He cleaned the glass on the deck wall" · "Kai took the board
to the back bench, turned on the work lamp" · "Woke the lathe" ·
"the small drawer under the register where he kept the pieces of
paper" · "The three kids sat on the small bench against the front
window that Kai kept for parents waiting on repairs" · "pulled the
kettle out from under the counter… put it on the small electric
burner" · Devon's old desk in the back office with two boxes of
bearings.

Frame: Blender Z-up, y=0 south storefront wall (Main — the
laundromat's sanderling mural across the street), +Y to the back
wall at y=7, x=±4.5, ceiling 2.8. glTF export remaps to Godot
(x, z, -y).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_chamfer_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window
from _props.store_fixtures import make_counter, make_register
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 9.0; ROOM_D = 7.0; CEIL = 2.8
PAL_WALL = {"wall": (0.50, 0.46, 0.42, 1.0), "baseboard": (0.24, 0.20, 0.16, 1.0)}
COL_FLOOR = (0.44, 0.34, 0.24, 1.0); COL_SEAM = (0.28, 0.20, 0.14, 1.0)
COL_WOOD = (0.42, 0.30, 0.18, 1.0)
COL_STEEL = (0.58, 0.60, 0.62, 1.0)
COL_GLASS = (0.55, 0.62, 0.66, 0.35)
# Deck graphics — a mixed wall of boards
DECK_TINTS = [(0.72, 0.26, 0.22, 1.0), (0.26, 0.44, 0.62, 1.0), (0.86, 0.72, 0.26, 1.0),
              (0.30, 0.52, 0.36, 1.0), (0.56, 0.34, 0.60, 1.0), (0.88, 0.86, 0.80, 1.0),
              (0.20, 0.22, 0.26, 1.0), (0.80, 0.48, 0.24, 1.0)]


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    # Back wall with a gap for the alley door (x ~ +3.4)
    make_wall("Wall_N_W", (-1.0, ROOM_D, 0), length=7.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_E", (4.15, ROOM_D, CEIL/2.0), (0.9, 0.20, CEIL), PAL_WALL["wall"])
    make_box("Wall_N_AboveAlley", (3.15, ROOM_D, CEIL-0.30), (1.1, 0.20, 0.60), PAL_WALL["wall"])
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    # Alley door leaf ("He pulled the truck out of the alley")
    make_box("Alley_Door", (3.15, ROOM_D-0.04, 1.03), (0.90, 0.05, 2.05), (0.34, 0.30, 0.28, 1.0))
    # Front door: bell + reversible OPEN/CLOSED + the taped note
    make_box("Front_Door", (0.0, 0.04, 1.02), (1.90, 0.04, 2.04), (0.30, 0.28, 0.26, 1.0))
    make_box("Front_Door_Glass", (0.0, 0.03, 1.20), (1.50, 0.02, 1.55), COL_GLASS)
    make_cyl("Door_Bell", (0.0, 0.16, 2.05), 0.04, 0.06, (0.74, 0.58, 0.28, 1.0), segments=8)
    make_box("Open_Sign", (0.35, 0.06, 1.55), (0.24, 0.01, 0.16), (0.86, 0.82, 0.72, 1.0))
    make_box("Taped_Note", (0.35, 0.06, 1.74), (0.14, 0.008, 0.10), (0.94, 0.92, 0.84, 1.0))


def build_deck_wall():
    """The glass-fronted DECK WALL along the west side — the thing
    Kai cleans the glass on."""
    make_box("DeckWall_Back", (-4.44, 3.8, 1.30), (0.06, 4.4, 2.30), (0.30, 0.26, 0.22, 1.0))
    for r in range(2):
        for c in range(7):
            dy = 1.85 + c * 0.62
            dz = 0.85 + r * 1.05
            tint = DECK_TINTS[(r * 7 + c) % len(DECK_TINTS)]
            make_box(f"Deck_{r}_{c}", (-4.36, dy, dz), (0.05, 0.22, 0.82), tint)
            make_box(f"Deck_{r}_{c}_Stripe", (-4.33, dy, dz + 0.15), (0.04, 0.18, 0.10),
                     DECK_TINTS[(r * 7 + c + 3) % len(DECK_TINTS)])
    # The glass front Kai cleans
    make_box("DeckWall_Glass", (-4.10, 3.8, 1.30), (0.02, 4.3, 2.20), COL_GLASS)
    make_box("DeckWall_Glass_Frame_T", (-4.10, 3.8, 2.42), (0.05, 4.4, 0.06), COL_STEEL)
    make_box("DeckWall_Glass_Frame_B", (-4.10, 3.8, 0.18), (0.05, 4.4, 0.06), COL_STEEL)


def build_counter():
    """Sales counter, the stool behind it, the small drawer under
    the register, the kettle + electric burner underneath."""
    top_z = make_counter("Register", (2.25, 5.5, 0.0), length=2.40, depth=1.00, height=0.95,
                         palette={"formica": (0.52, 0.42, 0.30, 1.0),
                                  "top": (0.30, 0.22, 0.14, 1.0), "kick": (0.24, 0.18, 0.12, 1.0)})
    make_register("Register", (2.6, 5.4, top_z))
    # The small drawer under the register (the pieces of paper live here)
    make_box("Register_Drawer", (1.75, 5.02, 0.72), (0.40, 0.02, 0.14), (0.34, 0.24, 0.16, 1.0))
    make_box("Register_Drawer_Pull", (1.75, 5.00, 0.72), (0.10, 0.015, 0.03), COL_STEEL)
    # The stool behind the counter
    make_cyl("Counter_Stool", (2.25, 6.15, 0.34), 0.17, 0.05, COL_WOOD, segments=10)
    for li in range(3):
        import math as _m
        ang = li * 2.09
        make_cyl(f"Counter_Stool_Leg_{li}", (2.25 + 0.12 * _m.cos(ang), 6.15 + 0.12 * _m.sin(ang), 0.16),
                 0.015, 0.32, COL_STEEL, segments=5)
    # Kettle on its small electric burner, under-counter shelf
    make_box("Under_Shelf", (1.55, 5.9, 0.28), (0.60, 0.60, 0.03), COL_WOOD)
    make_box("Electric_Burner", (1.55, 5.9, 0.325), (0.26, 0.26, 0.06), (0.22, 0.22, 0.24, 1.0))
    make_cyl("Kettle", (1.55, 5.9, 0.44), 0.09, 0.20, COL_STEEL, segments=10)


def build_repair_back():
    """The back of the shop: repair bench + work lamp + the lathe,
    each with its own light — 'turned on the back light over the
    repair bench.'"""
    make_chamfer_box("Repair_Bench", (0.0, 6.2, 0.45), (2.20, 0.70, 0.90), COL_WOOD)
    make_chamfer_box("Repair_Bench_Top", (0.0, 6.2, 0.92), (2.26, 0.76, 0.05), (0.32, 0.24, 0.16, 1.0))
    # A board mid-repair on the bench, trucks off
    make_box("Repair_Board", (0.15, 6.15, 0.98), (0.80, 0.22, 0.03), DECK_TINTS[1])
    make_box("Repair_Truck_Loose", (-0.45, 6.3, 0.96), (0.16, 0.10, 0.06), COL_STEEL)
    # The clamp work lamp
    make_box("Work_Lamp_Arm", (0.0, 6.35, 1.35), (0.04, 0.04, 0.75), (0.20, 0.19, 0.20, 1.0))
    make_cyl("Work_Lamp_Head", (0.0, 6.25, 1.60), 0.09, 0.14, (0.96, 0.86, 0.55, 1.0), segments=10)
    # The single small tube over the bench (its own light)
    make_fluorescent_tube_fixture("Bench_Light", (0.0, 6.2, CEIL), length=1.00, width=0.20)
    # The lathe, west of the bench against the N wall
    make_chamfer_box("Lathe_Bed", (-2.6, 6.35, 1.00), (1.40, 0.40, 0.25), COL_STEEL)
    for lx in (-3.15, -2.05):
        make_box(f"Lathe_Leg_{lx:.2f}", (lx, 6.35, 0.45), (0.14, 0.34, 0.90), (0.30, 0.32, 0.34, 1.0))
    make_cyl("Lathe_Head", (-3.05, 6.35, 1.20), 0.14, 0.24, (0.30, 0.32, 0.34, 1.0), axis='X', segments=10)
    make_cyl("Lathe_Stock", (-2.5, 6.35, 1.18), 0.05, 0.70, COL_WOOD, axis='X', segments=8)


def build_office():
    """The back office: Devon's old desk, the chair Devon also left,
    two cardboard boxes of bearings on the floor."""
    make_box("Office_Part", (3.55, 6.0, CEIL/2.0), (1.90, 0.10, CEIL), PAL_WALL["wall"])
    make_chamfer_box("Devon_Desk", (3.9, 6.55, 0.37), (1.00, 0.55, 0.74), COL_WOOD)
    make_box("Devon_Chair_Seat", (3.35, 6.35, 0.44), (0.40, 0.40, 0.05), COL_WOOD)
    make_box("Devon_Chair_Back", (3.35, 6.53, 0.72), (0.40, 0.05, 0.50), COL_WOOD)
    for bi, by in enumerate((6.2, 6.5)):
        make_box(f"Bearings_Box_{bi}", (2.95, by, 0.16), (0.34, 0.28, 0.32), (0.60, 0.48, 0.32, 1.0))


def build_retail():
    """Small-parts retail: bearings/trucks/wheels/wax pegwall on the
    E wall, plus the waiting bench under the front window."""
    make_box("Parts_Pegboard", (4.44, 4.0, 1.35), (0.05, 2.00, 0.95), (0.62, 0.56, 0.46, 1.0))
    for r in range(3):
        for c in range(5):
            py = 3.2 + c * 0.40
            pz = 1.05 + r * 0.30
            make_box(f"Part_{r}_{c}", (4.38, py, pz), (0.07, 0.16, 0.14),
                     [(0.72, 0.26, 0.22, 1.0), COL_STEEL, (0.86, 0.72, 0.26, 1.0)][(r + c) % 3])
    # Wheels in a low bin
    make_chamfer_box("Wheel_Bin", (4.15, 2.4, 0.35), (0.55, 0.55, 0.55), COL_WOOD)
    for wi in range(4):
        make_cyl(f"Wheel_{wi}", (4.05 + (wi % 2) * 0.18, 2.3 + (wi // 2) * 0.18, 0.66),
                 0.07, 0.09, (0.92, 0.88, 0.66, 1.0), segments=10)
    # Front window + the parents' bench under it (NO staged board
    # games — the mural across Main does the window's work)
    make_window("Win_S", (-2.75, 0.10, 1.55), width=2.60, height=1.50)
    make_chamfer_box("Wait_Bench", (-2.75, 0.55, 0.42), (1.80, 0.42, 0.06), COL_WOOD)
    for lx in (-3.5, -2.0):
        make_box(f"Wait_Bench_Leg_{lx:.1f}", (lx, 0.55, 0.20), (0.08, 0.36, 0.40), (0.30, 0.22, 0.14, 1.0))


def build_decor():
    make_wall_clock("Clock", (0.0, ROOM_D-0.05, CEIL-0.45), frozen_hour=10, frozen_min=5)
    make_floor_plant("Plant", (-4.0, 0.8, 0.0),
                     palette={"leaf": (0.36, 0.48, 0.30, 1.0), "pot": (0.66, 0.40, 0.26, 1.0)})
    for pi, py in enumerate((1.5, 2.6)):
        make_faded_poster(f"Poster_E_{pi}", (ROOM_W/2.0-0.05, py, 1.55))
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-2.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)
    # Shop lighting: two tubes over the retail floor (a shop earns
    # them; the bench has its own)
    for j, ypos in enumerate((1.8, 4.0)):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)


def main():
    clear_scene()
    build_shell()
    build_deck_wall()
    build_counter()
    build_repair_back()
    build_office()
    build_retail()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/board_lords_interior.glb"))
    print(f"\n[build_board_lords_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
