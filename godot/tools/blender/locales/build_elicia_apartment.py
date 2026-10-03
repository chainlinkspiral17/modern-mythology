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
from _props.furniture import make_table
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, make_rot_box, make_tube
from _props.structure import make_floor, make_wall, make_wall_with_openings, make_ceiling, make_window, make_crown_molding, make_door_hinges
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
    make_wall_with_openings("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=+1,
                            openings=[(3.0, 1.40, 1.60, 1.40)])   # Window_W (2026-10-03: the wall was solid behind the pane)
    make_wall("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1)
    make_wall_with_openings("Wall_S_E", (+2.5, 0.0, 0), length=2.0, height=CEIL, axis='X', palette=PAL, baseboard_face_sign=+1,
                            openings=[(2.0, 1.40, 1.40, 1.20)])   # Window_SE
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (3.0, 0.20, 0.60), PAL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, with_grid=False)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_SE", (+2.0, 0.10, 1.40), width=1.40, height=1.20, room_dir=+1)
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window_W", (-ROOM_W/2.0 + 0.10, 3.0, 1.40), width=1.60, height=1.40, axis='Y', room_dir=+1)
    # the front door: a leaf on its hinges, a sidelight panel to the
    # jamb (2026-09-22: three hinges hung in the 3 m opening with no door)
    make_box("FrontDoor_Jamb_Panel", (-1.30, 0.0, CEIL/2.0 - 0.15), (0.40, 0.20, CEIL - 0.30), PAL["wall"])
    make_box("FrontDoor_Leaf", (-0.65, 0.05, 1.05), (0.90, 0.05, 2.10), COL_WOOD)
    make_door_hinges("FrontDoor_Hinge", edge_x=-1.10, edge_y=0.0, edge_z_centers=[0.30, 1.05, 1.80], axis='X')

def build_living():
    sx, sy = 0.45, 1.50   # east of the front door's swing (2026-09-24, the user: "doorways obstructed")
    make_box("Sofa_Base", (sx, sy, 0.12), (1.90, 0.76, 0.24), (0.28, 0.32, 0.40, 1.0))   # (2026-09-22: the sofa hung at 0.24)
    make_box("Sofa_Seat", (sx, sy, 0.34), (2.0, 0.80, 0.20), COL_COUCH)
    make_box("Sofa_Back", (sx, sy+0.32, 0.74), (2.0, 0.20, 0.60), COL_COUCH)
    for cs in (-1, +1):
        make_box(f"Sofa_Arm_{cs:+d}", (sx + cs*1.04, sy, 0.50), (0.16, 0.80, 0.42), (0.28, 0.32, 0.40, 1.0))
    # Coffee table low
    make_box("CoffeeTable", (sx, sy-0.80, 0.30), (1.20, 0.50, 0.04), COL_WOOD)
    for lx_ in (-1, 1):   # legs (2026-09-22)
        for ly_ in (-1, 1):
            make_box(f"CoffeeTable_Leg_{lx_:+d}_{ly_:+d}", (sx + lx_ * 0.55, sy-0.80 + ly_ * 0.20, 0.14), (0.04, 0.04, 0.28), COL_WOOD)
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
    make_cyl("MicStand_Base", (mx-0.30, my, 0.40), 0.06, 0.04, P.METAL_BLACK)   # on the desk (2026-09-23: 2 cm over it)
    make_cyl("MicStand_Pole", (mx-0.30, my, 0.70), 0.012, 0.56, P.METAL_BLACK)
    make_cyl("Mic_Body", (mx-0.30, my, 1.04), 0.04, 0.20, P.METAL_BLACK)
    make_cyl("Mic_Pop", (mx-0.30, my-0.07, 1.04), 0.07, 0.06, COL_RING_LIGHT, axis='Y')   # against the mic
    # Ring light on a separate pole
    make_cyl("Ring_Pole", (mx+0.40, my, 0.78), 0.012, 0.80, P.METAL_BLACK)   # from the desk (2026-09-23: 4 cm over it)
    make_cyl("Ring_Light_Hoop", (mx+0.40, my-0.025, 1.20), 0.24, 0.015, P.METAL_BLACK, axis='Y', segments=16)   # the hoop the LEDs sit on (2026-09-22)
    for ri in range(8):
        import math
        ang = ri * 0.785
        ox = mx+0.40 + math.cos(ang)*0.22
        oz = 1.20 + math.sin(ang)*0.22
        make_box(f"Ring_Light_{ri}", (ox, my-0.025, oz), (0.04, 0.02, 0.04), COL_RING_LIGHT)
    # Laptop on desk
    make_box("Laptop_Base", (mx+0.20, my, 0.40), (0.34, 0.24, 0.02), P.METAL_BLACK)
    make_box("Laptop_Lid",  (mx+0.20, my+0.10, 0.50), (0.34, 0.02, 0.20), P.METAL_BLACK)

def build_decor():
    # clear of the window (2026-09-24: once the clock faced the room it overlapped it)
    make_wall_clock("Clock", (-3.400, 3.0, 2.37), frozen_hour=4, frozen_min=22, facing='+X')
    make_faded_poster("Poster_N", (0.0, ROOM_D-0.02 - 0.0835, 1.70), axis='X',
                      palette={"body": (0.62, 0.42, 0.52, 1.0)}, into_room=-1)
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
    # on the window's bottom rail, lens to the room (2026-09-24: the lens
    # pointed into the wall — the window it filmed through had been built
    # inside that wall; it faces the room she films herself in)
    make_box("Camera_Body", (2.0, 0.19, 0.90), (0.16, 0.10, 0.10), (0.14, 0.14, 0.16, 1.0))
    make_cyl("Camera_Lens", (2.0, 0.265, 0.90), 0.035, 0.05, (0.10, 0.10, 0.12, 1.0), axis='Y', segments=8)
    make_box("Camera_RedLight", (2.06, 0.20, 0.9575), (0.015, 0.015, 0.015), (0.96, 0.16, 0.14, 1.0))
    # The award + the eviction envelope on the coffee table
    # with the coffee table, 0.45 east (2026-09-24)
    make_box("Glass_Award", (0.15, 0.70, 0.42), (0.10, 0.06, 0.20), (0.66, 0.78, 0.84, 0.7))
    make_box("Award_Base", (0.15, 0.70, 0.335), (0.14, 0.10, 0.03), (0.20, 0.20, 0.22, 1.0))
    make_box("Eviction_Envelope", (0.70, 0.70, 0.33), (0.22, 0.11, 0.006), (0.94, 0.93, 0.90, 1.0))
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
    make_light_switch("Switch_Entry", (1.65, 0.0), axis='X', face_sign=1, aged=True)   # on the wall east of the opening (2026-09-22: it hung in the doorway)
    make_wall_outlet("Outlet_W", (-ROOM_W / 2.0, ROOM_D * 0.35), axis='Y',
                     face_sign=1, aged=True)
    make_wall_outlet("Outlet_E", (ROOM_W / 2.0, ROOM_D * 0.70), axis='Y',
                     face_sign=-1, aged=True)


def build_use_states_d4():
    """D4 use states: the Tower is the week it all comes down —
    papers fanned by the door, the laptop open, boxes half-packed."""
    # The eviction notice on the desk + papers fanned on the floor
    make_box("Desk_Notice", (2.65, 4.35, 0.382), (0.15, 0.21, 0.004),   # on the desk (2026-09-23: 1.3 cm over it)
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
    # beside the door, west of its swing (2026-09-24: box A stood in it)
    make_box("Pack_Box_A", (-1.40, 0.5, 0.18), (0.45, 0.35, 0.36),
             (0.52, 0.40, 0.28, 1.0))
    make_box("Pack_Box_B", (-1.87, 0.55, 0.15), (0.42, 0.34, 0.30),
             (0.50, 0.38, 0.26, 1.0))
    for sgn in (-1, 1):
        make_box(f"Pack_Box_B_Flap_{sgn:+d}", (-1.87 + sgn * 0.24, 0.55, 0.31),   # on the box's rim
                 (0.10, 0.32, 0.02), (0.48, 0.36, 0.25, 1.0))
    # The second teacup — one on the coffee table (marker), one
    # abandoned on the desk corner
    make_cyl("Desk_Teacup", (2.35, 4.62, 0.4075), 0.032, 0.055,
             (0.86, 0.84, 0.80, 1.0), segments=8)

def build_eviction_notice_2026_08():
    """THE EVICTION NOTICE (shot_marker_audit --props, 2026-08-12).
    [shot:insert eviction_notice] fires in vol5 ch16 and the object
    did not exist: "The landlord had left it taped to the door in
    the small Quebecois white envelope landlords used here, with the
    tape applied in the exact location that had previously held the
    lease renewal."

    So it is ON THE DOOR, not on a table — and the detail that
    carries the chapter is the SECOND piece of tape: the pale
    rectangle where the last notice hung, still there under the new
    one. The envelope hangs slightly askew, because tape does.
    """
    # Front door is the south wall's opening; leaf face at y≈0.06,
    # hinge edge x=-1.10, so the latch half is around x=-0.35.
    dx, dz = -0.42, 1.44
    env = (0.94, 0.93, 0.90, 1.0)
    env_shadow = (0.82, 0.81, 0.78, 1.0)
    tape = (0.88, 0.86, 0.80, 0.55)
    ghost = (0.86, 0.85, 0.83, 1.0)     # the old adhesive rectangle
    ink = (0.30, 0.28, 0.26, 1.0)
    stamp = (0.42, 0.20, 0.18, 1.0)
    # The GHOST of the lease renewal — same spot, sun-bleached edge
    make_box("EvictionGhost_Patch", (dx, 0.0766, dz + 0.015),
             (0.175, 0.002, 0.115), ghost)
    # The envelope, hung a few degrees off true (staggered boxes)
    make_box("EvictionNotice_Envelope", (dx, 0.075, dz),
             (0.165, 0.004, 0.105), env)
    make_box("EvictionNotice_Flap", (dx, 0.077, dz + 0.028),
             (0.165, 0.003, 0.048), env_shadow)
    make_box("EvictionNotice_Window", (dx - 0.028, 0.078, dz - 0.018),
             (0.075, 0.002, 0.030), (0.86, 0.88, 0.90, 1.0))
    # The address showing through the window + the landlord's stamp
    for li, lz in enumerate((-0.012, -0.024)):
        make_box("EvictionNotice_Line_%d" % li,
                 (dx - 0.030, 0.0795, dz + lz),
                 (0.058, 0.001, 0.005), ink)
    make_box("EvictionNotice_Stamp", (dx + 0.052, 0.0795, dz + 0.026),
             (0.030, 0.001, 0.022), stamp)
    # Two strips of tape — the new one, and the older strip beside
    # it that never came off.
    make_box("EvictionNotice_Tape_New", (dx, 0.079, dz + 0.062),
             (0.052, 0.002, 0.030), tape)
    make_box("EvictionNotice_Tape_Old", (dx + 0.058, 0.074, dz + 0.070),
             (0.044, 0.002, 0.026), tape)



def build_door_infill_frontdoor_leaf_2026_09():
    """FrontDoor_Leaf was narrower than its wall opening (the user, 2026-09-24:
    "doorways ... misaligned"): close the gap to the door and its frame."""
    make_wall("Wall_Fill_FrontDoor_Leaf_E", (0.650, 0.000, 0), length=1.700, height=2.000, axis='X', palette=PAL, baseboard_face_sign=+1)

def build_wrecked_command_center_2026_10():
    """CHARACTER PASS (2026-10-03). The chapter: "once Elicia Duchane's
    sleek command center, now resembled the ruins of some forgotten
    exposition … Data slates lay like fallen monoliths on the floor
    amidst drifts of rejected script pages. Cables snaked across
    surfaces like dormant metallic ivy." What a command center leaves
    when it falls: the long work table under the west window with two
    dead monitors, the keyboard, the drive stacks, a dead plant; the
    story-map whiteboard on the north wall under its post-its, the
    corkboard of the photographs she stopped taking; her prints,
    unhung, leaning on the wall; the low case of binders and film cans;
    a tripod standing for the camera; many more pages, slates and
    cables; and Montreal's dusk through the west window — tower blocks
    with their lights, the harbour's red and gold afar."""
    import random
    rnd = random.Random(16)
    wood = COL_WOOD
    paper = (0.88, 0.86, 0.80, 1.0)
    dark = (0.18, 0.20, 0.24, 1.0)
    # ── the work table under the west window, the dead monitors
    make_table("Work_Table", -2.90, 3.00, w=0.60, d=1.90, h=0.75, wood=(0.30, 0.30, 0.32, 1.0))
    for i, (ty, tilt) in enumerate(((2.45, 0.0), (3.35, 0.0))):
        make_box(f"Dead_Monitor_{i}_Foot", (-2.98, ty, 0.765), (0.18, 0.14, 0.02), (0.14, 0.14, 0.16, 1.0))
        make_box(f"Dead_Monitor_{i}_Neck", (-2.98, ty, 0.84), (0.04, 0.03, 0.14), (0.14, 0.14, 0.16, 1.0))
        make_box(f"Dead_Monitor_{i}", (-2.98, ty, 1.05), (0.03, 0.56, 0.34), (0.14, 0.14, 0.16, 1.0))
        make_box(f"Dead_Monitor_{i}_Screen", (-2.963, ty, 1.05), (0.004, 0.50, 0.28), (0.10, 0.11, 0.13, 1.0))
    make_box("Keyboard", (-2.76, 2.90, 0.765), (0.14, 0.42, 0.02), (0.22, 0.22, 0.24, 1.0))
    for k in range(4):
        make_box(f"Drive_Stack_{k}", (-2.80, 3.78, 0.75 + k * 0.03 + 0.015), (0.18, 0.12, 0.03), [(0.20, 0.20, 0.22, 1.0), (0.32, 0.32, 0.34, 1.0)][k % 2])
    make_cyl("Dead_Plant_Pot", (-2.80, 2.18, 0.80), 0.06, 0.10, (0.52, 0.42, 0.34, 1.0), segments=8)
    for k in range(3):
        make_rot_box(f"Dead_Plant_Stalk_{k}", (-2.80 + 0.03 * (k - 1), 2.18 + 0.02 * k, 0.94), (0.008, 0.008, 0.18), (0.42, 0.36, 0.22, 1.0), pitch=0.6 * (k - 1), roll=0.3)
    # ── cables: the ivy, across the table and down to the floor
    make_tube("Cable_Ivy_Table_0", [(-2.98, 2.45, 0.78), (-2.80, 2.70, 0.77), (-2.62, 2.60, 0.77), (-2.60, 2.60, 0.02), (-2.20, 2.30, 0.02)], 0.008, (0.30, 0.32, 0.34, 1.0), segments=5)
    # (two tubes: the overlap audit boxes a whole polyline, and one tube from
    # the table top to the floor "hits" the stretcher under the table)
    make_tube("Cable_Ivy_Table_1", [(-2.98, 3.35, 0.78), (-2.70, 3.55, 0.77), (-2.60, 3.80, 0.77)], 0.008, (0.26, 0.28, 0.30, 1.0), segments=5)
    make_tube("Cable_Ivy_Drop_1", [(-2.60, 3.80, 0.77), (-2.48, 3.85, 0.60), (-2.46, 3.86, 0.02), (-2.00, 4.30, 0.02), (-1.40, 4.10, 0.02)], 0.008, (0.26, 0.28, 0.30, 1.0), segments=5)
    make_tube("Cable_Ivy_Floor_3", [(0.60, 3.20, 0.02), (1.20, 3.60, 0.02), (1.90, 3.30, 0.02), (2.40, 3.80, 0.02)], 0.009, (0.30, 0.32, 0.34, 1.0), segments=5)
    make_tube("Cable_Ivy_Floor_4", [(-0.80, 1.30, 0.02), (-1.40, 1.80, 0.02), (-1.60, 2.40, 0.02)], 0.009, (0.26, 0.28, 0.30, 1.0), segments=5)
    # ── the story map: a whiteboard on the north wall under post-its;
    #    the corkboard of her photographs beside it
    wy = ROOM_D - 0.10
    make_box("Whiteboard_Frame", (-1.80, wy - 0.012, 1.62), (1.64, 0.024, 1.04), (0.60, 0.62, 0.64, 1.0))
    make_box("Whiteboard", (-1.80, wy - 0.026, 1.62), (1.56, 0.004, 0.96), (0.94, 0.95, 0.94, 1.0))
    for i in range(14):
        px = -2.50 + rnd.uniform(0.0, 1.40)
        pz = 1.22 + rnd.uniform(0.0, 0.80)
        make_box(f"PostIt_{i}", (px, wy - 0.030, pz), (0.07, 0.003, 0.07), rnd.choice(((0.96, 0.90, 0.40, 1.0), (0.98, 0.70, 0.40, 1.0), (0.60, 0.86, 0.96, 1.0), (0.80, 0.94, 0.60, 1.0))))
    for i in range(6):
        make_box(f"Whiteboard_Line_{i}", (-1.80 + rnd.uniform(-0.6, 0.6), wy - 0.029, 1.62 + rnd.uniform(-0.4, 0.4)), (rnd.uniform(0.2, 0.6), 0.002, 0.008), rnd.choice(((0.20, 0.30, 0.60, 1.0), (0.70, 0.20, 0.20, 1.0), (0.20, 0.20, 0.22, 1.0))))
    make_box("Corkboard", (-3.00, wy - 0.014, 1.62), (0.70, 0.028, 0.56), (0.62, 0.48, 0.30, 1.0))
    for i in range(7):
        px = -3.30 + rnd.uniform(0.0, 0.60)
        pz = 1.40 + rnd.uniform(0.0, 0.42)
        make_box(f"Pinned_Photo_{i}", (px, wy - 0.031, pz), (0.10, 0.003, 0.08), rnd.choice(((0.58, 0.62, 0.66, 1.0), (0.72, 0.66, 0.54, 1.0), (0.52, 0.60, 0.52, 1.0), (0.76, 0.70, 0.58, 1.0))))
    # ── her prints, unhung, leaning on the west wall south of the window
    for i, (y, h, w, tint) in enumerate(((1.30, 0.60, 0.80, (0.52, 0.56, 0.60, 1.0)), (1.36, 0.50, 0.70, (0.70, 0.62, 0.50, 1.0)), (1.42, 0.44, 0.60, (0.46, 0.54, 0.50, 1.0)))):
        make_rot_box(f"Print_{i}_Frame", (-3.27 + i * 0.045, y, h / 2.0 + 0.01), (0.03, w, h), (0.22, 0.20, 0.18, 1.0), roll=0.0, pitch=0.0)
        make_rot_box(f"Print_{i}_Pic", (-3.253 + i * 0.045, y, h / 2.0 + 0.01), (0.004, w - 0.06, h - 0.06), tint)
    # ── the low case of binders and film cans under the north poster
    make_box("Low_Case_Top", (0.0, 5.20, 0.90), (1.60, 0.32, 0.02), wood)
    make_box("Low_Case_Bot", (0.0, 5.20, 0.01), (1.60, 0.32, 0.02), wood)
    for sx in (-0.79, 0.79):
        make_box(f"Low_Case_Side_{sx:+.2f}", (sx, 5.20, 0.455), (0.02, 0.32, 0.91), wood)
    make_box("Low_Case_Shelf", (0.0, 5.20, 0.46), (1.56, 0.30, 0.02), wood)
    run = -0.76
    for i in range(12):
        t = rnd.choice((0.05, 0.06, 0.07))
        make_box(f"Binder_{i}", (run + t / 2.0, 5.20, 0.47 + 0.15), (t, 0.26, 0.30), rnd.choice(((0.20, 0.22, 0.26, 1.0), (0.86, 0.84, 0.78, 1.0), (0.40, 0.20, 0.18, 1.0), (0.24, 0.34, 0.46, 1.0))))
        run += t + 0.004
    for i in range(5):
        make_cyl(f"Film_Can_{i}", (-0.60 + i * 0.09, 5.22, 0.02 + 0.014 * i + 0.0125), 0.11, 0.025, [(0.60, 0.60, 0.62, 1.0), (0.46, 0.46, 0.48, 1.0)][i % 2], segments=12)
    for i in range(3):
        make_box(f"Drive_Case_{i}", (0.40 + i * 0.16, 5.20, 0.09), (0.12, 0.24, 0.14), (0.26, 0.26, 0.28, 1.0))
    # ── a tripod standing for the camera, facing the sofa
    tx, ty = 0.45, 2.75
    import math
    for i in range(3):
        a = i * 2.094 + 0.5
        make_rot_box(f"Tripod_Leg_{i}", (tx + math.cos(a) * 0.18, ty + math.sin(a) * 0.18, 0.62), (0.02, 0.02, 1.30), (0.16, 0.16, 0.18, 1.0), pitch=0.26 * math.sin(a), roll=-0.26 * math.cos(a))
    make_cyl("Tripod_Collar", (tx, ty, 1.21), 0.05, 0.10, (0.16, 0.16, 0.18, 1.0), segments=8)   # where the legs meet
    make_cyl("Tripod_Head", (tx, ty, 1.29), 0.04, 0.06, (0.16, 0.16, 0.18, 1.0), segments=8)
    make_box("Tripod_Plate", (tx, ty, 1.33), (0.08, 0.06, 0.02), (0.22, 0.22, 0.24, 1.0))
    # ── more of the ruin: pages, slates, a slate against the sofa
    for i in range(10):
        px, py = rnd.uniform(-2.2, 2.2), rnd.uniform(2.0, 4.6)
        if abs(px - 0.45) < 0.5 and abs(py - 2.75) < 0.5:
            continue
        make_rot_box(f"Script_Page_{i}", (px, py, 0.006 + 0.002 * (i % 3)), (0.21, 0.28, 0.003), paper, yaw=rnd.uniform(-0.8, 0.8))
    for i, (sx, sy) in enumerate(((-1.9, 4.3), (1.6, 2.4), (-0.6, 3.9))):
        make_rot_box(f"Slate_More_{i}", (sx, sy, 0.018), (0.42, 0.28, 0.03), dark, yaw=rnd.uniform(-0.6, 0.6))
    make_rot_box("Slate_Leaning", (1.72, 1.75, 0.20), (0.42, 0.03, 0.28), dark, pitch=-0.35)   # against the sofa's east arm
    # ── Montreal's dusk through the west window: tower blocks, their
    #    windows lit; the harbour's lights far off
    for i, (bx, by, bw, bd, bh) in enumerate(((-9.5, 1.0, 3.0, 3.0, 11.0), (-11.0, 5.5, 2.6, 2.6, 15.0), (-8.6, 7.6, 2.2, 2.2, 8.0), (-13.0, -1.5, 3.4, 3.4, 13.0))):
        make_box(f"Tower_{i}", (bx, by, bh / 2.0 - 4.0), (bw, bd, bh), (0.22, 0.22, 0.28, 1.0))
        for r in range(int(bh / 0.9)):
            for c in range(3):
                if rnd.random() < 0.55:
                    make_box(f"Tower_{i}_Win_{r}_{c}", (bx + bw / 2.0 + 0.01, by - bd / 3.0 + c * bd / 3.0, -3.6 + r * 0.9), (0.02, 0.36, 0.40), rnd.choice(((0.98, 0.84, 0.46, 1.0), (0.96, 0.92, 0.70, 1.0), (0.80, 0.86, 0.96, 1.0))))
    for i in range(9):
        make_box(f"Harbour_Light_{i}", (-24.0, -6.0 + i * 1.6, -1.6 + rnd.uniform(0.0, 0.8)), (0.3, 0.4, 0.4), rnd.choice(((0.96, 0.22, 0.18, 1.0), (0.98, 0.78, 0.30, 1.0))))
    make_box("Harbour_Water", (-24.0, 2.0, -3.0), (16.0, 30.0, 0.1), (0.10, 0.12, 0.18, 1.0))


def main():
    clear_scene(); build_shell(); build_living(); build_studio_nook(); build_decor(); build_ceiling_infra()
    build_hero_props()
    build_detail_pass_2026_08()
    build_use_states_d4()
    build_eviction_notice_2026_08()
    build_wrecked_command_center_2026_10()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/elicia_apartment.glb"))
    build_door_infill_frontdoor_leaf_2026_09()
    print(f"\n[build_elicia_apartment] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
