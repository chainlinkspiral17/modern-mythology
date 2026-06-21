"""VOL 5 · Elicia's Apartment — Lovers cameos / Pomegranate Hour
host. PLACEMENT SCRIPT (uses _props library).

Canon: Elicia's tidy one-bedroom. Recording setup, vinyl
collection, plants. Cool blue + warm tungsten lamp duotone.

Footprint:
  Interior X ∈ [-3.5, +3.5], Y ∈ [0, +5.5], ceiling Z=2.60
  Door south. Studio nook NE (mic + ring light). Plant wall S.
  Sofa centre, vinyl shelf east.

Output: godot/assets/3d/locales/elicia_apartment.glb
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding, make_door_hinges
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

PAL = {"wall": (0.88, 0.86, 0.84, 1.0), "baseboard": (0.32, 0.28, 0.30, 1.0)}
COL_FLOOR = (0.62, 0.52, 0.46, 1.0); COL_SEAM = (0.32, 0.28, 0.26, 1.0)
COL_COUCH = (0.42, 0.46, 0.54, 1.0); COL_VINYL = (0.18, 0.16, 0.18, 1.0)
COL_RING_LIGHT = (1.0, 0.88, 0.62, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
ROOM_W = 7.0; ROOM_D = 5.5; CEIL = 2.60

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (3.0, 0.20, 0.60), PAL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    make_window("Window_SE", (+2.0, 0.0, 1.40), width=1.40, height=1.20)
    make_window("Window_W", (-ROOM_W/2.0+0.02, 3.0, 1.40), width=1.60, height=1.40)
    make_door_hinges("FrontDoor_Hinge", edge_x=-1.10, edge_y=0.0, edge_z_centers=[0.30, 1.05, 1.80], axis='X')

def build_living():
    sx, sy = 0.0, 1.50
    make_box("Sofa_Seat", (sx, sy, 0.34), (2.0, 0.80, 0.20), COL_COUCH)
    make_box("Sofa_Back", (sx, sy+0.32, 0.74), (2.0, 0.20, 0.60), COL_COUCH)
    for cs in (-1, +1):
        make_box(f"Sofa_Arm_{cs:+d}", (sx + cs*1.04, sy, 0.50), (0.16, 0.80, 0.42), (0.28, 0.32, 0.40, 1.0))
    # Coffee table low
    make_box("CoffeeTable", (sx, sy-0.80, 0.30), (1.20, 0.50, 0.04), COL_WOOD)
    # Vinyl shelf east wall
    for shf in range(4):
        make_box(f"VinylShelf_{shf}", (+3.20, 3.0, 0.40+shf*0.36), (0.40, 1.20, 0.02), COL_WOOD)
        for vi in range(6):
            make_box(f"VinylRecord_{shf}_{vi}",
                     (+3.20, 2.50+vi*0.16, 0.52+shf*0.36),
                     (0.32, 0.04, 0.30),
                     [(0.62, 0.32, 0.30, 1.0), (0.42, 0.52, 0.62, 1.0), COL_VINYL, (0.74, 0.58, 0.30, 1.0)][(shf+vi)%4])

def build_studio_nook():
    # Mic on stand + ring light + small recording desk NE corner
    mx, my = +2.8, 4.5
    make_box("Desk", (mx, my, 0.36), (1.20, 0.60, 0.04), COL_WOOD)
    for li in range(4):
        lx = mx + (-0.54, +0.54, -0.54, +0.54)[li]
        ly = my + (-0.24, -0.24, +0.24, +0.24)[li]
        make_box(f"Desk_Leg_{li}", (lx, ly, 0.18), (0.04, 0.04, 0.36), COL_WOOD)
    # Mic stand
    make_cyl("MicStand_Base", (mx-0.30, my, 0.42), 0.06, 0.04, P.METAL_BLACK)
    make_cyl("MicStand_Pole", (mx-0.30, my, 0.70), 0.012, 0.56, P.METAL_BLACK)
    make_cyl("Mic_Body", (mx-0.30, my, 1.04), 0.04, 0.20, P.METAL_BLACK)
    make_cyl("Mic_Pop", (mx-0.30, my-0.10, 1.04), 0.07, 0.06, COL_RING_LIGHT, axis='Y')
    # Ring light on a separate pole
    make_cyl("Ring_Pole", (mx+0.40, my, 0.80), 0.012, 0.76, P.METAL_BLACK)
    for ri in range(8):
        import math
        ang = ri * 0.785
        ox = mx+0.40 + math.cos(ang)*0.22
        oz = 1.20 + math.sin(ang)*0.22
        make_box(f"Ring_Light_{ri}", (ox, my-0.04, oz), (0.04, 0.02, 0.04), COL_RING_LIGHT)
    # Laptop on desk
    make_box("Laptop_Base", (mx+0.20, my, 0.40), (0.34, 0.24, 0.02), P.METAL_BLACK)
    make_box("Laptop_Lid",  (mx+0.20, my+0.10, 0.50), (0.34, 0.02, 0.20), P.METAL_BLACK)

def build_decor():
    make_wall_clock("Clock", (-3.45, 3.0, 2.10), frozen_hour=11, frozen_min=15)
    make_faded_poster("Poster_N", (0.0, ROOM_D-0.02, 1.70), palette={"body": (0.62, 0.42, 0.52, 1.0)})
    make_floor_plant("Plant_S1", (-3.0, 0.80, 0.0))
    make_floor_plant("Plant_S2", (+3.0, 0.80, 0.0), palette={"leaf": (0.62, 0.74, 0.56, 1.0)})

def build_ceiling_infra():
    for j, ypos in enumerate([1.5, 3.5]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, 3.0, CEIL))
    make_hvac_vent("HVAC", (-1.0, 5.0, CEIL), width=0.60, depth=0.30)

def main():
    clear_scene(); build_shell(); build_living(); build_studio_nook(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/elicia_apartment.glb"))
    print(f"\n[build_elicia_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
