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
from _props.detail import (make_floor_stain, make_light_switch, make_threshold, make_traffic_wear, make_wall_outlet, make_wall_tint_band)

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
    make_window("Window_W", (-ROOM_W/2.0+0.02, 3.0, 1.40), width=1.60, height=1.40, axis='Y')
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
    make_wall_clock("Clock", (-3.45, 3.0, 2.10), frozen_hour=4, frozen_min=22)
    make_faded_poster("Poster_N", (0.0, ROOM_D-0.02, 1.70), axis='X',
                      palette={"body": (0.62, 0.42, 0.52, 1.0)})
    make_floor_plant("Plant_S1", (-3.0, 0.80, 0.0))
    make_floor_plant("Plant_S2", (+3.0, 0.80, 0.0), palette={"leaf": (0.62, 0.74, 0.56, 1.0)})

def build_ceiling_infra():
    # The docstring wanted "warm tungsten lamp duotone" — here is
    # the lamp; the tubes are gone
    make_cyl("Tungsten_Lamp_Base", (-1.2, 1.0, 0.02), 0.12, 0.03, (0.24, 0.20, 0.17, 1.0), segments=10)
    make_cyl("Tungsten_Lamp_Post", (-1.2, 1.0, 0.72), 0.02, 1.40, (0.24, 0.20, 0.17, 1.0), segments=6)
    make_cyl("Tungsten_Lamp_Shade", (-1.2, 1.0, 1.52), 0.16, 0.22, (0.86, 0.68, 0.42, 1.0), segments=10)
    make_smoke_detector("Smoke", (0.9, 2.75, CEIL))


def build_hero_props():
    """2026-08-03 tail pass: the kitchen counter with her mother's
    dust-filled teacup + the green sponge by the sink, the camera
    with its red record light on the windowsill, the heavy glass
    award, the eviction envelope, and the wreckage (data slates,
    script-page drifts, cable ivy)."""
    make_box("Kitchen_Counter", (2.2, 5.20, 0.46), (1.6, 0.60, 0.92), (0.50, 0.46, 0.40, 1.0))
    make_box("Kitchen_Counter_Top", (2.2, 5.20, 0.94), (1.66, 0.66, 0.05), (0.62, 0.60, 0.56, 1.0))
    make_box("Kitchen_Sink", (2.6, 5.20, 0.95), (0.42, 0.40, 0.05), (0.42, 0.44, 0.45, 1.0))
    make_box("Green_Sponge", (2.36, 5.05, 0.985), (0.09, 0.06, 0.03), (0.34, 0.62, 0.36, 1.0))
    make_cyl("Mothers_Teacup", (1.90, 5.20, 1.00), 0.045, 0.07, (0.90, 0.88, 0.82, 1.0), segments=10)
    make_cyl("Teacup_Saucer", (1.90, 5.20, 0.965), 0.075, 0.012, (0.90, 0.88, 0.82, 1.0), segments=10)
    # The camera on the windowsill, red light on
    make_box("Camera_Body", (2.0, 0.14, 1.05), (0.16, 0.10, 0.10), (0.14, 0.14, 0.16, 1.0))
    make_cyl("Camera_Lens", (2.0, 0.06, 1.05), 0.035, 0.05, (0.10, 0.10, 0.12, 1.0), axis='Y', segments=8)
    make_box("Camera_RedLight", (2.06, 0.10, 1.11), (0.015, 0.015, 0.015), (0.96, 0.16, 0.14, 1.0))
    # The award + the eviction envelope on the coffee table
    make_box("Glass_Award", (-0.30, 0.70, 0.42), (0.10, 0.06, 0.20), (0.66, 0.78, 0.84, 0.7))
    make_box("Award_Base", (-0.30, 0.70, 0.335), (0.14, 0.10, 0.03), (0.20, 0.20, 0.22, 1.0))
    make_box("Eviction_Envelope", (0.25, 0.70, 0.33), (0.22, 0.11, 0.006), (0.94, 0.93, 0.90, 1.0))
    # The wreckage
    for i, (sx, sy) in enumerate(((-2.4, 2.2), (-1.2, 3.6), (0.8, 2.8), (2.4, 1.6))):
        make_box(f"Data_Slate_{i}", (sx, sy, 0.02), (0.42, 0.28, 0.03), (0.18, 0.20, 0.24, 1.0))
    for i, (px, py) in enumerate(((-2.0, 1.4), (-0.4, 2.6), (1.4, 3.6), (0.2, 4.2), (2.6, 2.4))):
        make_box(f"Script_Drift_{i}", (px, py, 0.012), (0.55, 0.45, 0.02), (0.88, 0.86, 0.80, 1.0))
    for i, (cx, cy, cl) in enumerate(((-1.5, 2.9, 1.4), (0.9, 1.9, 1.1), (1.9, 4.1, 1.6))):
        make_cyl(f"Cable_Ivy_{i}", (cx, cy, 0.03), 0.018, cl, (0.30, 0.32, 0.34, 1.0), segments=6, axis='X' if i % 2 else 'Y')



def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (adaptive template pass per
    lore/_SET_DETAIL_PLAYBOOK.md). Per-locale wear personality is
    the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Entry", [(0.0, 0.6), (0.0, ROOM_D * 0.55)],
                      width=0.75, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62), radius=0.24,
                     tint=(COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0))
    pw = PAL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_wall_tint_band("Band_W", (-ROOM_W / 2.0 + 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_wall_tint_band("Band_E", (ROOM_W / 2.0 - 0.105, ROOM_D / 2.0, 0.0),
                        length=ROOM_D - 0.4, axis='Y', band_z=CEIL - 0.16, tint=band)
    make_threshold("Threshold_Entry", (0.0, 0.10), width=1.9, axis='X')
    make_light_switch("Switch_Entry", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def build_use_states_d4():
    """D4 use states: the Tower is the week it all comes down —
    papers fanned by the door, the laptop open, boxes half-packed."""
    # The eviction notice on the desk + papers fanned on the floor
    make_box("Desk_Notice", (2.65, 4.35, 0.395), (0.15, 0.21, 0.004),
             (0.94, 0.92, 0.86, 1.0))
    for i, (px, py, rot_off) in enumerate(((0.35, 0.55, 0.0), (0.55, 0.42, 0.06),
                                           (0.22, 0.38, -0.04))):
        make_box(f"Floor_Paper_{i}", (px + rot_off, py, 0.012 + i * 0.003),
                 (0.15, 0.21, 0.003), (0.90, 0.88, 0.82, 1.0))
    # Laptop OPEN on the desk: base + tilted-back lid (offset fake)
    make_box("Laptop_Base", (2.95, 4.55, 0.395), (0.30, 0.21, 0.015),
             (0.30, 0.31, 0.33, 1.0))
    make_box("Laptop_Lid", (2.95, 4.68, 0.50), (0.30, 0.03, 0.20),
             (0.26, 0.27, 0.29, 1.0))
    make_box("Laptop_Screen", (2.95, 4.665, 0.50), (0.26, 0.005, 0.16),
             (0.18, 0.24, 0.30, 1.0))
    # Half-packed boxes by the door: one closed, one open with flaps
    make_box("Pack_Box_A", (-0.9, 0.5, 0.18), (0.45, 0.35, 0.36),
             (0.52, 0.40, 0.28, 1.0))
    make_box("Pack_Box_B", (-1.45, 0.55, 0.15), (0.42, 0.34, 0.30),
             (0.50, 0.38, 0.26, 1.0))
    for sgn in (-1, 1):
        make_box(f"Pack_Box_B_Flap_{sgn:+d}", (-1.45 + sgn * 0.24, 0.55, 0.34),
                 (0.10, 0.32, 0.02), (0.48, 0.36, 0.25, 1.0))
    # The second teacup — one on the coffee table (marker), one
    # abandoned on the desk corner
    make_cyl("Desk_Teacup", (2.35, 4.62, 0.425), 0.032, 0.055,
             (0.86, 0.84, 0.80, 1.0), segments=8)

def main():
    clear_scene(); build_shell(); build_living(); build_studio_nook(); build_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_use_states_d4()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/elicia_apartment.glb"))
    print(f"\n[build_elicia_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
