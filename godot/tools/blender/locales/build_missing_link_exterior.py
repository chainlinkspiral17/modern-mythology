"""Missing Link exterior — vol1's roadside bus-depot diner from the
lot, plus THE SHUTTLE BENCH (vol1's highest-traffic background: the
whole link_* question chain is played sitting at this stop).

Companion to build_missing_link_interior.py — same diner, seen from
outside in the rain. Canon (vol1_missing_link): "a single rectangle
of warm yellow light pinned to a wet asphalt apron. Two gas pumps,
one of them retired in place. A sign hand-lettered on enamel — THE
MISSING LINK. Beside the diner, under a metal awning, is the depot
bench. The schedule is taped to the wall behind cracked plexiglass."

Hero features (all canon): the wet asphalt apron with puddle
gleams, the two gas pumps (the retired one visibly dead — no hose,
duller paint), the enamel pole sign, the metal depot awning against
the diner's east end with slat bench + schedule board under cracked
plexiglass + trash can, the bell over the door, a cobra-head
lamppost, telephone poles, a parked pickup, dark treeline, low sky.

Coordinate frame: Blender Z-up. y=0 is the road's south edge (the
camera side); +Y runs north through road → gravel lot → diner front
(y=8) → treeline. glTF export remaps to Godot (x, z, -y).

Two vantages wired in Background3D.CAMERA_PRESETS:
  missing_link_exterior — in the lot looking NNE at the diner front.
  shuttle_bench         — seated at the shelter looking W down the
                          shoulder: road left, diner + sign center.

DRAFT 2 (2026-09-19, lore/_VISUAL_PROGRAM.md §3 backgrounds pass;
shuttle_bench is vol 1's highest-traffic background, 8 placements +
the exterior's own). The pickup is the kit pickup; the telephone
poles are the kit's (crossarms, insulators) with the wires strung
between them; the treeline is a double row of conifers, not twelve
boxes; the cobra lamppost and the sign pole are profiles with base
flanges; the pumps chamfered with a hanging hose and a nozzle, two
bollards at the island's ends; the awning corrugated, its own tube
fixture under the roof (lit — the spill practical had hung outside
the awning), the trash can with a domed lid; window mullions, a door
pull, a downspout at the diner's west corner. WEAR: two tire tracks
from the road to the pumps, the oil stain at the island, the drip
line under the awning's lip, the worn centre of the door step, the
bench's sit shine, the rust streak at the sign pole's foot.
Draft 3 targets: reconcile with the interior's plan (see that file);
the diner's roofline neon; a second parked car; rain streaks on the
plexiglass; the puddles as sheets with the sky in them (alpha);
Deck: the shuttle_bench preset for the wire read against the sky.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_tube, make_chamfer_box, catenary, export_glb
from _props.vehicles import make_car
from _props.trees import make_conifer
from _props.detail import make_utility_pole, make_wire_run, make_floor_stain

# ── Palette (rain dusk) ──
COL_ASPHALT = (0.16, 0.16, 0.18, 1.0)
COL_APRON = (0.19, 0.19, 0.21, 1.0)      # wet asphalt apron
COL_PUDDLE = (0.34, 0.36, 0.42, 1.0)     # sky caught in standing water
COL_DASH = (0.72, 0.68, 0.52, 1.0)
COL_GRASS = (0.24, 0.28, 0.18, 1.0)
COL_PUMP_DEAD = (0.38, 0.30, 0.28, 1.0)  # the retired pump, faded
COL_PUMP_DEAD_FACE = (0.52, 0.48, 0.42, 1.0)
COL_PLEXI = (0.62, 0.66, 0.68, 0.5)      # cracked plexiglass
COL_CLAD = (0.58, 0.60, 0.63, 1.0)       # stainless cladding
COL_CLAD_DK = (0.44, 0.46, 0.50, 1.0)
COL_TRIM = (0.55, 0.18, 0.16, 1.0)       # diner red band
COL_GLOW = (1.00, 0.82, 0.50, 1.0)       # lit windows — blooms via glow
COL_DOOR = (0.30, 0.32, 0.36, 1.0)
COL_SIGN = (0.88, 0.84, 0.72, 1.0)       # cream sign face
COL_SIGN_RED = (0.62, 0.20, 0.16, 1.0)
COL_POLE = (0.30, 0.30, 0.32, 1.0)
COL_SHELTER = (0.36, 0.38, 0.36, 1.0)    # painted municipal green-gray
COL_BENCH = (0.46, 0.34, 0.22, 1.0)      # worn wood slats
COL_WOODPOLE = (0.26, 0.20, 0.15, 1.0)   # creosote telephone poles
COL_TRUCK = (0.34, 0.40, 0.44, 1.0)
COL_TRUCK_DK = (0.20, 0.24, 0.26, 1.0)
COL_TIRE = (0.10, 0.10, 0.11, 1.0)
COL_TREE = (0.10, 0.14, 0.10, 1.0)
COL_TREE_LT = (0.13, 0.18, 0.12, 1.0)
COL_HILL = (0.16, 0.18, 0.22, 1.0)
COL_SKY = (0.30, 0.26, 0.38, 1.0)        # dusk violet


def build_ground():
    # Road: two lanes running E-W, y ∈ [0, 3.4]
    make_box("Road", (0.0, 1.7, 0.0), (34.0, 3.4, 0.04), COL_ASPHALT)
    for i in range(11):
        make_box(f"Dash_{i}", (-15.0 + i * 3.0, 1.7, 0.026), (1.3, 0.12, 0.012), COL_DASH)   # on the road (2026-09-22)
    # The asphalt apron ("wet asphalt apron" — canon) north of the road
    make_box("Apron", (0.0, 5.7, 0.0), (34.0, 4.6, 0.05), COL_APRON)
    # Rain: puddle gleams scattered on apron + road
    puddles = [(-6.5, 4.8, 1.6, 0.8), (-1.5, 6.4, 2.2, 1.0), (3.8, 5.2, 1.3, 0.7),
               (7.4, 4.4, 1.8, 0.9), (-10.5, 5.9, 1.4, 0.8), (1.2, 2.2, 2.4, 0.7),
               (-4.0, 1.2, 1.7, 0.6)]
    for i, (px, py, pw, pd) in enumerate(puddles):
        make_box(f"Puddle_{i}", (px, py, 0.029), (pw, pd, 0.008), COL_PUDDLE)
    # Grass fringes: south of road, and between apron and treeline
    make_box("Grass_S", (0.0, -2.0, 0.0), (34.0, 4.0, 0.04), COL_GRASS)
    make_box("Grass_N", (0.0, 14.5, 0.0), (34.0, 5.0, 0.04), COL_GRASS)


def build_gas_pumps():
    """Two pumps on a low island, mid-apron west of the door. The
    east one still works; the west one retired in place — duller,
    no hose, a bag-taped nozzle slot."""
    make_box("Pump_Island", (-3.2, 5.4, 0.10), (2.6, 1.0, 0.20), COL_CLAD_DK)
    # Working pump (east)
    make_chamfer_box("Pump_E_Body", (-2.5, 5.4, 0.80), (0.55, 0.45, 1.40), COL_TRIM, chamfer=0.02)
    make_box("Pump_E_Face", (-2.5, 5.16, 1.05), (0.40, 0.04, 0.55), COL_SIGN)
    make_box("Pump_E_Crown", (-2.5, 5.4, 1.58), (0.58, 0.48, 0.16), COL_CLAD_DK)
    # (draft 2: the hose hangs from the crown to the nozzle in its holster)
    make_tube("Pump_E_Hose", [(-2.22, 5.4, 1.42), (-2.05, 5.4, 1.05), (-2.20, 5.4, 0.72)], 0.02, COL_POLE, segments=6)
    make_box("Pump_E_Nozzle", (-2.21, 5.4, 0.64), (0.06, 0.10, 0.14), COL_CLAD)
    for bi_, bx_ in enumerate((-4.7, -1.7)):
        make_lathe(f"Bollard_{bi_}", (bx_, 5.4, 0.025), [(0.07, 0.0), (0.07, 0.85), (0.05, 0.90), (0.0, 0.90)], (0.86, 0.72, 0.18, 1.0), segments=8)
    # Retired pump (west) — faded, capped, hoseless
    make_chamfer_box("Pump_W_Body", (-3.9, 5.4, 0.78), (0.55, 0.45, 1.36), COL_PUMP_DEAD, chamfer=0.02)
    make_box("Pump_W_Face", (-3.9, 5.16, 1.02), (0.40, 0.04, 0.55), COL_PUMP_DEAD_FACE)
    make_box("Pump_W_Crown", (-3.9, 5.4, 1.54), (0.58, 0.48, 0.16), COL_PUMP_DEAD)
    make_box("Pump_W_Cap", (-3.59, 5.4, 0.95), (0.10, 0.20, 0.24), COL_CLAD_DK)


def build_diner():
    """The diner box: front face at y=8, x ∈ [-4.5, 3.5], flat roof."""
    # Main volume
    make_box("Diner_Body", (-0.5, 10.5, 1.7), (8.0, 5.0, 3.4), COL_CLAD)
    # Red trim band + parapet cap
    make_box("Diner_Band", (-0.5, 7.98, 2.95), (8.0, 0.10, 0.5), COL_TRIM)
    make_box("Diner_Parapet", (-0.5, 10.5, 3.48), (8.2, 5.2, 0.16), COL_CLAD_DK)
    # Warm window band along the front (proud of the face so it reads)
    for i, wx in enumerate((-3.4, -1.9, -0.4, 1.1)):
        make_box(f"Diner_Win_{i}", (wx, 7.955, 1.65), (1.25, 0.06, 1.15), COL_GLOW)   # in the front wall's face (8.00; 2026-09-22: 3 cm off it)
        make_box(f"Diner_WinFrame_{i}", (wx, 7.975, 1.65), (1.40, 0.05, 1.30), COL_CLAD_DK)
    # Glazed door, east end of the front, with concrete step
    make_box("Diner_Door", (2.4, 7.94, 1.25), (0.92, 0.08, 2.30), COL_DOOR)
    make_box("Diner_DoorGlass", (2.4, 7.90, 1.55), (0.62, 0.05, 1.20), COL_GLOW)
    make_box("Diner_Step", (2.4, 7.65, 0.09), (1.3, 0.7, 0.18), COL_CLAD_DK)
    # (draft 2: mullions in the windows, a pull on the door, a downspout)
    for i, wx in enumerate((-3.4, -1.9, -0.4, 1.1)):
        make_box(f"Diner_Mullion_{i}", (wx, 7.915, 1.65), (0.04, 0.02, 1.15), COL_CLAD_DK)
    make_tube("Diner_Door_Pull", [(2.75, 7.88, 0.95), (2.75, 7.88, 1.30)], 0.012, COL_CLAD, segments=6)
    make_tube("Diner_Downspout", [(-4.55, 8.06, 3.35), (-4.55, 8.06, 0.30), (-4.55, 7.80, 0.12)], 0.04, COL_CLAD_DK, segments=6)
    # The bell over the door ("unsubtle about your leaving")
    # on the door's top edge. (2026-09-24: this comment once sat mid-call
    # and swallowed the colour — the Blender build died here)
    make_cyl("Door_Bell", (2.4, 7.86, 2.43), 0.05, 0.06, (0.66, 0.52, 0.24, 1.0),
             segments=8)
    # Roof clutter: A/C unit + vent
    make_box("Diner_AC", (-2.5, 10.8, 3.85), (1.2, 1.0, 0.6), COL_CLAD_DK)
    make_cyl("Diner_Vent", (1.5, 11.5, 3.83), 0.16, 0.55, COL_POLE, segments=8)   # on the parapet


def build_pole_sign():
    """Double-panel MISSING LINK sign on a pole west of the diner,
    an arrow panel angled at the lot."""
    make_lathe("Sign_Pole", (-6.5, 6.5, 0.025), [(0.22, 0.0), (0.22, 0.05), (0.12, 0.10), (0.11, 4.15), (0.0, 4.15)], COL_POLE, segments=8)
    make_box("Rust_Streak", (-6.5, 6.15, 0.027), (0.30, 0.55, 0.004), (0.36, 0.22, 0.14, 1.0))
    make_box("Sign_Face_N", (-6.5, 6.56, 4.7), (2.6, 0.10, 1.1), COL_SIGN)
    make_box("Sign_Face_S", (-6.5, 6.44, 4.7), (2.6, 0.10, 1.1), COL_SIGN)
    make_box("Sign_Border", (-6.5, 6.5, 4.7), (2.75, 0.08, 1.25), COL_SIGN_RED)
    # Arrow panel under the main faces, pointing at the diner
    make_box("Sign_Arrow", (-5.9, 6.5, 3.85), (1.3, 0.09, 0.4), COL_SIGN_RED)
    make_box("Sign_Arrow_Tip", (-5.15, 6.5, 3.85), (0.28, 0.09, 0.7), COL_SIGN_RED)


def build_depot_awning():
    """Canon: "Beside the diner, under a metal awning, is the depot
    bench. The schedule is taped to the wall behind cracked
    plexiglass." A corrugated metal awning off the diner's east end,
    back panel carrying the schedule, slat bench beneath, trash can."""
    sx, sy = 5.6, 6.6          # awning center, abutting the diner's SE corner
    # Posts + sloped-read roof (two stacked slabs, lower lip south)
    for px, py in ((sx - 1.5, sy - 0.85), (sx + 1.5, sy - 0.85)):
        make_cyl(f"Awning_Post_{px:.1f}", (px, py, 1.25), 0.06, 2.5, COL_POLE, segments=6)
    make_box("Awning_Roof_Hi", (sx, sy + 0.5, 2.72), (3.5, 1.1, 0.10), COL_CLAD_DK)
    make_box("Awning_Roof_Lo", (sx, sy - 0.5, 2.52), (3.5, 1.2, 0.10), COL_CLAD_DK)
    make_box("Awning_Corrugate", (sx, sy, 2.64), (3.4, 2.0, 0.05), COL_SHELTER)
    for ri in range(9):
        make_box(f"Awning_Ridge_{ri}", (sx - 1.6 + ri * 0.4, sy, 2.675), (0.06, 1.9, 0.02), COL_CLAD_DK)
    # the tube fixture under the roof (its practical is in the tscn)
    make_box("Shelter_Tube_Housing", (sx + 0.9, sy - 0.2, 2.44), (0.90, 0.14, 0.06), COL_CLAD_DK)
    make_cyl("Shelter_Tube", (sx + 0.9, sy - 0.2, 2.40), 0.02, 0.80, COL_GLOW, axis='X', segments=6)
    # Back panel (the "wall" the schedule is taped to)
    make_box("Awning_Back", (sx, sy + 1.0, 1.225), (3.5, 0.10, 2.4), COL_SHELTER)   # on the apron
    # The schedule: paper sheet + cracked plexiglass + a crack line
    make_box("Schedule_Paper", (sx - 0.6, sy + 0.93, 1.55), (0.55, 0.03, 0.75), COL_SIGN)
    make_box("Schedule_Plexi", (sx - 0.6, sy + 0.90, 1.55), (0.62, 0.02, 0.82), COL_PLEXI)
    make_box("Schedule_Crack", (sx - 0.72, sy + 0.885, 1.50), (0.03, 0.015, 0.70), COL_CLAD_DK)
    # Slat bench under the awning
    for i in range(3):
        make_box(f"Bench_Slat_{i}", (sx, sy + 0.62 - i * 0.13, 0.46), (2.4, 0.11, 0.04), COL_BENCH)
    make_box("Bench_Back", (sx, sy + 0.70, 0.65), (2.4, 0.06, 0.34), COL_BENCH)   # on the rear slat (2026-09-22: 10 cm behind it, 7 cm up)
    for lx in (sx - 1.0, sx + 1.0):
        make_box(f"Bench_Leg_{lx:.1f}", (lx, sy + 0.52, 0.22), (0.08, 0.34, 0.44), COL_POLE)
    # Route board on its own post at the awning's road side
    make_cyl("Route_Post", (sx - 2.1, sy - 1.4, 0.85), 0.04, 1.7, COL_POLE, segments=6)
    make_box("Route_Board", (sx - 2.1, sy - 1.35, 1.95), (0.55, 0.06, 0.75), COL_SIGN)
    make_box("Route_Board_Head", (sx - 2.1, sy - 1.33, 2.22), (0.55, 0.05, 0.16), COL_SIGN_RED)
    # Trash can east of the bench
    make_lathe("Trash", (sx + 2.1, sy - 0.6, 0.025), [(0.0, 0.0), (0.22, 0.0), (0.24, 0.70), (0.26, 0.72), (0.26, 0.76), (0.18, 0.84), (0.06, 0.86), (0.0, 0.86)], COL_SHELTER, segments=10)
    make_box("Trash_Slot", (sx + 2.1, sy - 0.86, 0.72), (0.18, 0.02, 0.10), (0.12, 0.12, 0.12, 1.0))


def build_street_furniture():
    # Cobra-head lamppost between shelter and road
    make_lathe("Lamp_Pole", (8.2, 4.0, 0.025), [(0.18, 0.0), (0.18, 0.05), (0.10, 0.10), (0.08, 4.90), (0.0, 4.90)], COL_POLE, segments=8)
    make_tube("Lamp_Arm", [(8.2, 4.0, 4.85), (8.2, 3.4, 4.98), (8.2, 2.7, 4.94)], 0.04, COL_POLE, segments=6)
    make_box("Lamp_Head", (8.2, 2.45, 4.88), (0.24, 0.62, 0.14), COL_CLAD_DK)
    make_box("Lamp_Bulb", (8.2, 2.45, 4.80), (0.16, 0.42, 0.03), COL_GLOW)
    # Telephone poles along the far (south) shoulder
    # (draft 2: the kit's poles, and the wires strung between them)
    poles = [(-12.0, -0.8), (-2.0, -0.8), (8.0, -0.8)]
    for i, (px, py) in enumerate(poles):
        make_utility_pole(f"TPole_{i}", px, py, h=7.0, transformer=(i == 1), wood=COL_WOODPOLE)
    make_wire_run("TLine", poles, h=7.0, sag=0.45)
    # Parked pickup in the lot, west of the door (draft 2: the kit pickup)
    # (the kit pickup is 4.9 m; at -8.5 its nose reached the sign pole)
    make_car("Truck", -9.6, 5.6, 4.9, COL_TRUCK, pickup=True, along="X")


def build_backdrop():
    # Dark treeline north of the grass
    # (draft 2: two rows of conifers, not twelve boxes)
    for i in range(12):
        tx = -15.0 + i * 2.8
        h = 5.2 + 1.6 * ((i * 5) % 3)
        make_conifer(f"Tree_{i}", tx, 16.5 + 0.6 * (i % 2), h, COL_TREE if i % 2 == 0 else COL_TREE_LT, COL_WOODPOLE)
    for i in range(10):
        make_conifer(f"Tree_Back_{i}", -13.6 + i * 3.1, 19.6 + 0.5 * (i % 3), 6.5 + 1.2 * ((i * 7) % 3), COL_TREE, COL_WOODPOLE)
    # Low hill band + dusk sky
    # (occluder slab deleted 2026-08-04 — a paper-thin wall 20m out
    # hiding the real receding bands built behind it)
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)


def build_draft2_2026_09():
    """DRAFT 2 (2026-09-19) · wear on the lot. No part name carries a
    cue word (sign · bench)."""
    track = (0.13, 0.13, 0.15, 1.0)
    # two tire tracks from the road up to the pumps (above the puddles'
    # top, z 0.059, so a puddle and a track never share a volume)
    for ti, tx in enumerate((-4.0, -2.4)):
        make_box(f"Apron_Track_{ti}", (tx, 4.2, 0.064), (0.34, 1.6, 0.008), track)
    make_floor_stain("Oil_Stain", (-3.2, 4.55), radius=0.40, floor_z=0.05, tint=(0.09, 0.09, 0.10, 1.0), segments=10)
    make_box("Awning_Drip", (5.6, 5.92, 0.029), (3.4, 0.06, 0.008), (0.14, 0.14, 0.16, 1.0))
    make_box("Step_Worn", (2.4, 7.65, 0.182), (0.60, 0.50, 0.003), (0.38, 0.40, 0.44, 1.0))
    for i in range(3):
        make_box(f"Seat_Shine_{i}", (4.6 + i * 1.0, 6.98, 0.482), (0.40, 0.30, 0.003), (0.54, 0.42, 0.28, 1.0))


def main():
    clear_scene()
    build_ground()
    build_gas_pumps()
    build_diner()
    build_pole_sign()
    build_depot_awning()
    build_street_furniture()
    build_backdrop()
    build_draft2_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/missing_link_exterior.glb"))
    print(f"\n[build_missing_link_exterior] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 60m. The station sits on a road
    that goes somewhere: receding grass hills carrying the road's
    line of poles away."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    make_box("Ground_Far", (0.0, 0.0, -0.03), (1400.0, 1400.0, 0.02),
             (0.26, 0.24, 0.16, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarHill", COL_GRASS,
                   [(80.0, 90.0, 8.0, 0.85), (170.0, 150.0, 12.0, 0.66),
                    (340.0, 260.0, 17.0, 0.50), (620.0, 440.0, 24.0, 0.38)],
                   profile="ridge")
    for pi in range(8):
        d = 70.0 + pi * 34.0
        make_cyl("FarPole_%d" % pi, (6.0, d, 3.4), 0.10, 6.8,
                 (0.22, 0.20, 0.18, 1.0), segments=6)


if __name__ == "__main__":
    main()
