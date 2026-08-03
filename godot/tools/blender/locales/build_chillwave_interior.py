"""chillwave_interior — ChillWave, Cale's slowstick shop (vol7).

2026-08-03 tail-wave RE-THEME. The old build was a synthwave
COCKTAIL LOUNGE — bar, DJ decks, neon mural. Every vol7_ch6 scene
set here is a small secondhand SLOWSTICK SHOP: "Cale was not at the
counter. The lights were on. The bell rang as she came in" · "The
back was where the inventory lived. Cedar shelves alphabetized by
designer, a wooden crate by the door" · "He was at the workbench"
· "The wooden box held three sticks. The third was Estuary 7."

Rebuilt to the prose:
- FRONT: entry door with the BELL above it, storefront glass, the
  counter (service bell + Cale's face-down paperback + register),
  cedar display shelving with sticks facing out.
- BACK (through the partition doorway): cedar inventory shelves in
  alphabetized rows, the WOODEN CRATE by the doorway, Cale's
  WORKBENCH (soldering iron, LED strip, bench transformer, parts
  trays, task lamp) with his chair, the second chair, and the
  three-slot WOODEN STICK BOX with the Estuary 7 label.

Per the aesthetic bible: warm cedar modernity, no neon cosplay.
Room: door/S wall at blender y=0, extends +Y; 7.0 x 8.0, ceil 2.8.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_register
from _props.decor import make_wall_clock, make_floor_plant
from _props.safety import make_smoke_detector, make_hvac_vent
from _props.detail import (make_traffic_wear, make_floor_stain, make_scuff_band,
                           make_wall_tint_band, make_threshold, make_wall_outlet,
                           make_light_switch, make_cord_run, make_thermostat)

ROOM_W = 7.0; ROOM_D = 8.0; CEIL = 2.8
PART_Y = 4.6          # front-shop / back-room partition
PAL_WALL = {"wall": (0.82, 0.74, 0.62, 1.0), "baseboard": (0.40, 0.30, 0.20, 1.0)}
COL_FLOOR = (0.52, 0.40, 0.28, 1.0); COL_SEAM = (0.36, 0.27, 0.18, 1.0)
COL_CEDAR = (0.66, 0.46, 0.30, 1.0)
COL_CEDAR_DK = (0.50, 0.34, 0.22, 1.0)
COL_STEEL = (0.62, 0.64, 0.66, 1.0)
COL_GLASS = (0.66, 0.74, 0.76, 0.6)
COL_BRASS = (0.82, 0.72, 0.42, 1.0)
# Muted stick-case tints (per-studio cases, not candy plastic).
STICK_TINTS = [(0.48, 0.52, 0.44, 1.0), (0.56, 0.44, 0.38, 1.0),
               (0.40, 0.46, 0.54, 1.0), (0.60, 0.56, 0.42, 1.0),
               (0.44, 0.40, 0.48, 1.0)]


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,
              axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,
              axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_CEDAR_DK})
    # Partition between front shop and the back room, doorway at E.
    make_wall("Part_W", (-1.05, PART_Y, 0), length=4.9, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Part_E", (2.95, PART_Y, 0), length=1.1, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Part_AboveDoorway", (1.9, PART_Y, CEIL-0.35), (1.0, 0.20, 0.70), PAL_WALL["wall"])
    make_box("Part_Doorframe_W", (1.38, PART_Y, 1.05), (0.08, 0.24, 2.10), COL_CEDAR_DK)
    make_box("Part_Doorframe_E", (2.42, PART_Y, 1.05), (0.08, 0.24, 2.10), COL_CEDAR_DK)


def build_storefront():
    # Glass either side of the door + THE BELL over the entry (it
    # rings when she comes in — the shop's opening image).
    for tag, wx in [("SW", -2.25), ("SE", 2.25)]:
        make_window(f"Win_{tag}", (wx, 0.10, 1.60), width=1.80, height=1.45)
    make_box("DoorBell_Arm", (0.55, 0.16, 2.28), (0.03, 0.14, 0.03), COL_STEEL)
    make_cyl("DoorBell", (0.55, 0.26, 2.22), 0.05, 0.07, COL_BRASS, segments=10)
    # A low window-display plinth in the SW glass: two sticks on
    # stands catching the street.
    make_box("Display_Plinth", (-2.25, 0.55, 0.25), (1.40, 0.50, 0.50), COL_CEDAR)
    for di, dx in enumerate([-2.55, -1.95]):
        make_box(f"Display_Stick_{di}", (dx, 0.55, 0.58), (0.09, 0.16, 0.16),
                 STICK_TINTS[di % len(STICK_TINTS)])


def build_counter_front():
    # Cale's counter, angled to see the door: register, the SERVICE
    # BELL, and his face-down paperback.
    ccy = 3.1
    top_z = make_counter("Shop", (-1.1, ccy, 0.0), length=2.60, depth=0.70, height=0.95,
                         palette={"formica": COL_CEDAR, "top": COL_CEDAR_DK,
                                  "kick": (0.30, 0.22, 0.16, 1.0)})
    make_register("RegisterMachine", (-1.9, ccy+0.05, top_z))
    make_cyl("Counter_Bell_Base", (-0.5, ccy-0.10, top_z+0.015), 0.05, 0.02, COL_STEEL, segments=10)
    make_cyl("Counter_Bell_Dome", (-0.5, ccy-0.10, top_z+0.05), 0.045, 0.05, COL_BRASS, segments=10)
    # The paperback, face-down, spine cracked, mid-read.
    make_box("Paperback", (-1.2, ccy-0.15, top_z+0.012), (0.13, 0.19, 0.022), (0.72, 0.62, 0.44, 1.0))
    make_box("Paperback_Pages", (-1.2, ccy-0.15, top_z+0.030), (0.12, 0.18, 0.012), (0.90, 0.87, 0.78, 1.0))
    # Front display shelving: cedar wall units W + E with sticks
    # facing out (retail face of the alphabetized system).
    for tag, sx in [("W", -ROOM_W/2.0+0.24), ("E", ROOM_W/2.0-0.24)]:
        for zi in range(3):
            sz = 0.70 + zi * 0.55
            make_box(f"FrontShelf_{tag}_{zi}", (sx, 2.4, sz), (0.36, 2.6, 0.04), COL_CEDAR)
            for ci in range(5):
                make_box(f"FrontStick_{tag}_{zi}_{ci}", (sx, 1.4+ci*0.5, sz+0.10),
                         (0.16, 0.10, 0.16), STICK_TINTS[(zi+ci) % len(STICK_TINTS)])
        make_box(f"FrontShelf_{tag}_Frame", (sx, 2.4, 1.15), (0.30, 2.7, 2.30), COL_CEDAR_DK)


def build_back_inventory():
    # "The back was where the inventory lived." Cedar shelf rows on
    # the N + W walls, alphabetized by designer — small brass letter
    # tabs step along the shelf edges.
    for zi in range(4):
        sz = 0.55 + zi * 0.52
        make_box(f"InvShelf_N_{zi}", (-0.6, ROOM_D-0.30, sz), (5.4, 0.36, 0.04), COL_CEDAR)
        for ci in range(9):
            make_box(f"InvStick_N_{zi}_{ci}", (-2.8+ci*0.55, ROOM_D-0.30, sz+0.10),
                     (0.10, 0.16, 0.16), STICK_TINTS[(zi+ci) % len(STICK_TINTS)])
        make_box(f"InvTab_N_{zi}", (-2.95+zi*1.5, ROOM_D-0.46, sz+0.02), (0.08, 0.02, 0.06), COL_BRASS)
    make_box("InvShelf_N_Frame", (-0.6, ROOM_D-0.28, 1.35), (5.6, 0.30, 2.70), COL_CEDAR_DK)
    for zi in range(4):
        sz = 0.55 + zi * 0.52
        make_box(f"InvShelf_W_{zi}", (-ROOM_W/2.0+0.24, 6.2, sz), (0.36, 2.6, 0.04), COL_CEDAR)
        for ci in range(5):
            make_box(f"InvStick_W_{zi}_{ci}", (-ROOM_W/2.0+0.24, 5.2+ci*0.5, sz+0.10),
                     (0.16, 0.10, 0.16), STICK_TINTS[(zi+ci+2) % len(STICK_TINTS)])
    make_box("InvShelf_W_Frame", (-ROOM_W/2.0+0.20, 6.2, 1.35), (0.30, 2.7, 2.70), COL_CEDAR_DK)
    # The WOODEN CRATE by the back-room doorway (trade-ins waiting
    # to be shelved).
    make_box("Crate", (2.6, PART_Y+0.55, 0.22), (0.55, 0.55, 0.42), (0.58, 0.44, 0.28, 1.0))
    make_box("Crate_Slat_A", (2.6, PART_Y+0.55, 0.44), (0.57, 0.57, 0.03), COL_CEDAR_DK)
    for si in range(3):
        make_box(f"Crate_InStick_{si}", (2.45+si*0.15, PART_Y+0.55, 0.50),
                 (0.10, 0.16, 0.14), STICK_TINTS[si])
    # The three-slot WOODEN BOX — Estuary 7 in the third slot, its
    # label a pale panel on the box face (vol7_ch6_the_stick).
    make_box("StickBox", (-2.4, 5.2, 0.86), (0.80, 0.30, 0.22), COL_CEDAR)
    make_box("StickBox_Table", (-2.4, 5.2, 0.38), (0.90, 0.44, 0.75), COL_CEDAR_DK)
    for si in range(3):
        make_box(f"StickBox_Slot_{si}", (-2.64+si*0.24, 5.14, 0.90),
                 (0.16, 0.16, 0.16), STICK_TINTS[(si*2) % len(STICK_TINTS)])
    make_box("StickBox_E7_Label", (-2.16, 5.04, 0.83), (0.14, 0.005, 0.05), (0.90, 0.88, 0.80, 1.0))


def build_workbench():
    # Cale's WORKBENCH on the back room's E wall: soldering iron in
    # its stand, the LED strip he's wiring, a bench transformer,
    # parts trays, task lamp — and "the small thing he had been
    # working on" open mid-repair.
    bx = ROOM_W/2.0 - 0.55
    make_box("Bench_Top", (bx, 6.4, 0.90), (0.90, 2.40, 0.06), COL_CEDAR_DK)
    for li, lyo in enumerate([-1.05, 1.05]):
        make_box(f"Bench_Leg_{li}", (bx, 6.4+lyo, 0.44), (0.80, 0.10, 0.86), COL_CEDAR)
    make_box("Bench_Backboard", (ROOM_W/2.0-0.12, 6.4, 1.55), (0.05, 2.40, 1.20), COL_CEDAR)
    # Soldering iron in its coil stand + sponge tin.
    make_cyl("Solder_Stand", (bx-0.15, 5.7, 0.96), 0.05, 0.10, COL_STEEL, segments=8)
    make_cyl("Solder_Iron", (bx-0.05, 5.78, 1.00), 0.015, 0.22, (0.24, 0.24, 0.26, 1.0),
             axis='X', segments=6)
    make_box("Solder_Sponge", (bx-0.30, 5.7, 0.945), (0.10, 0.08, 0.025), (0.80, 0.74, 0.30, 1.0))
    # Bench transformer (the heavy hum in the corner of the scene).
    make_box("Transformer", (bx+0.10, 7.3, 1.04), (0.30, 0.34, 0.28), (0.36, 0.38, 0.40, 1.0))
    make_cyl("Transformer_Dial", (bx-0.06, 7.3, 1.12), 0.05, 0.03, (0.20, 0.20, 0.22, 1.0),
             axis='X', segments=10)
    # The LED strip he's wiring, uncoiled across the bench.
    make_box("LED_Strip", (bx-0.05, 6.5, 0.945), (0.45, 0.04, 0.012), (0.90, 0.92, 0.86, 1.0))
    make_box("LED_Strip_Coil", (bx+0.20, 6.15, 0.95), (0.16, 0.16, 0.04), (0.82, 0.84, 0.80, 1.0))
    # The small thing mid-repair: an opened stick, shell + board.
    make_box("Repair_Shell", (bx-0.18, 6.85, 0.945), (0.16, 0.12, 0.03), STICK_TINTS[2])
    make_box("Repair_Board", (bx-0.02, 6.85, 0.94), (0.12, 0.09, 0.015), (0.24, 0.42, 0.28, 1.0))
    # Parts trays on the backboard + task lamp clamped at the N end.
    for ti in range(3):
        make_box(f"Parts_Tray_{ti}", (ROOM_W/2.0-0.28, 5.9+ti*0.5, 1.30), (0.22, 0.34, 0.10),
                 (0.70, 0.70, 0.66, 1.0))
    make_cyl("TaskLamp_Clamp", (bx+0.30, 7.5, 0.96), 0.04, 0.08, (0.22, 0.22, 0.24, 1.0), segments=8)
    make_cyl("TaskLamp_Arm", (bx+0.22, 7.45, 1.25), 0.015, 0.55, (0.22, 0.22, 0.24, 1.0))
    make_cyl("TaskLamp_Head", (bx+0.05, 7.35, 1.50), 0.08, 0.12, (0.96, 0.90, 0.72, 1.0), segments=10)
    # Cale's chair at the bench + THE second chair (he stayed in
    # the chair while she stood at the stick box).
    for ci, (cx, cy, ang_tag) in enumerate([(bx-0.85, 6.4, "Bench"), (0.6, 6.6, "Second")]):
        make_box(f"Chair_{ang_tag}_Seat", (cx, cy, 0.45), (0.44, 0.44, 0.05), COL_CEDAR)
        make_box(f"Chair_{ang_tag}_Back", (cx+(0.20 if ci == 0 else -0.20), cy, 0.75),
                 (0.05, 0.44, 0.55), COL_CEDAR)
        for li2, (lxo, lyo) in enumerate([(-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)]):
            make_box(f"Chair_{ang_tag}_Leg_{li2}", (cx+lxo, cy+lyo, 0.22), (0.05, 0.05, 0.44), COL_CEDAR_DK)


def build_ceiling_infra():
    # Domestic warm dome fixtures — no fluorescents in Cale's shop.
    for di, (dx, dy) in enumerate([(0.0, 2.2), (0.0, 6.2)]):
        make_cyl(f"Dome_{di}_Base", (dx, dy, CEIL-0.02), 0.16, 0.03, COL_STEEL, segments=12)
        make_cyl(f"Dome_{di}_Glass", (dx, dy, CEIL-0.10), 0.13, 0.13, (0.96, 0.90, 0.76, 1.0), segments=12)
    make_smoke_detector("Smoke", (-1.5, ROOM_D/2.0, CEIL))
    make_hvac_vent("Vent", (1.5, 1.2, CEIL), width=0.80, depth=0.40)


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 2.4, 2.25), frozen_hour=8, frozen_min=52,
                    palette={"face": (0.88, 0.84, 0.74, 1.0), "rim": COL_CEDAR_DK})
    make_floor_plant("Plant", (2.9, 0.7, 0.0),
                     palette={"leaf": (0.34, 0.48, 0.34, 1.0), "pot": (0.46, 0.36, 0.28, 1.0)})
    # Woven runner between door and counter.
    make_box("Runner", (0.0, 1.6, 0.015), (1.00, 2.20, 0.015), (0.54, 0.42, 0.32, 1.0))


def build_detail_pass_2026_08():
    """D2 surface breakup + D3 infrastructure (set-detail playbook).
    Cale's shop is TIDY-WORN: the wear is soft and local (the path
    he walks forty times a day, the burn ring where the iron lives),
    not grime. D4 (use states) and D5 (through-the-glass) next."""
    wear = (0.46, 0.35, 0.24, 1.0)          # floor darkened ~12%
    # The path: door -> counter -> partition doorway -> workbench.
    make_traffic_wear("Wear_Main", [(0.0, 0.6), (0.0, 2.6), (-1.1, 2.6)],
                      width=0.7, tint=wear)
    make_traffic_wear("Wear_Back", [(1.9, 3.2), (1.9, 5.4), (2.6, 5.4), (2.6, 6.4)],
                      width=0.65, tint=wear)
    # The workbench's life: solder-burn ring + a pale ring where
    # the transformer sat for years before its last move.
    make_floor_stain("Stain_Bench", (2.55, 6.1), radius=0.30,
                     tint=(0.40, 0.30, 0.21, 1.0))
    make_floor_stain("Stain_Bench_Ring", (2.55, 6.1), radius=0.18,
                     tint=(0.55, 0.43, 0.31, 1.0))
    # Soft kick scuff on the counter's customer face only.
    make_scuff_band("Scuff_Counter", (-1.1, 2.73), length=2.4, axis='X',
                    band_z=0.10, tint=(0.42, 0.30, 0.20, 1.0))
    # Ceiling gather on the two long walls.
    make_wall_tint_band("Band_W", (-ROOM_W/2.0+0.105, ROOM_D/2.0, 0.0),
                        length=ROOM_D-0.4, axis='Y', band_z=CEIL-0.16,
                        tint=(0.74, 0.66, 0.54, 1.0))
    make_wall_tint_band("Band_E", (ROOM_W/2.0-0.105, ROOM_D/2.0, 0.0),
                        length=ROOM_D-0.4, axis='Y', band_z=CEIL-0.16,
                        tint=(0.74, 0.66, 0.54, 1.0))
    make_threshold("Threshold_Front", (0.0, 0.10), width=1.9, axis='X',
                   tint=(0.50, 0.34, 0.20, 1.0))
    make_threshold("Threshold_Back", (1.9, PART_Y), width=1.0, axis='X',
                   tint=(0.50, 0.34, 0.20, 1.0))
    # D3 · plugged in.
    make_light_switch("Switch_Front", (1.15, 0.0), axis='X', face_sign=1)
    make_wall_outlet("Outlet_Counter", (-ROOM_W/2.0, 3.0), axis='Y', face_sign=1)
    make_wall_outlet("Outlet_Bench", (ROOM_W/2.0, 6.9), axis='Y', face_sign=-1)
    make_thermostat("Thermostat", (-1.05, PART_Y), axis='X', face_sign=-1)
    # Cords: register, the task lamp, and the transformer all reach
    # the bench outlet — the honest tangle of a one-man repair shop.
    make_cord_run("Cord_Register", (-1.9, 3.35, 0.90), (-3.39, 3.0, 0.30))
    make_cord_run("Cord_TaskLamp", (3.0, 7.5, 0.95), (3.39, 6.9, 0.30))
    make_cord_run("Cord_Transformer", (3.05, 7.3, 0.92), (3.39, 6.9, 0.30))


def build_use_states_2026_08():
    """D4 · mid-task (set-detail playbook). Cale's shop caught in
    the middle of an ordinary hour: shelving half-done, the repair
    open under good light, tea going cold. Tidy-worn — the mess is
    PRECISE."""
    # Shelving in progress: two sticks out of the crate, on the
    # floor beside it, one atop the other slightly off-square.
    make_box("Shelving_Stick_A", (2.15, PART_Y+0.85, 0.08), (0.10, 0.16, 0.15), STICK_TINTS[3])
    make_box("Shelving_Stick_B", (2.20, PART_Y+0.90, 0.235), (0.10, 0.16, 0.15), STICK_TINTS[1])
    # One inventory stick half-pulled, proud of its row (the shelf
    # gap Cale is walking back and forth to).
    make_box("InvStick_HalfOut", (-1.15, ROOM_D-0.44, 1.11), (0.10, 0.16, 0.16), STICK_TINTS[0])
    # The bench mid-repair: tweezers, three screws in a saucer, the
    # magnifier loupe set down lens-up.
    make_box("Bench_Tweezers", (2.90, 6.62, 0.95), (0.015, 0.11, 0.01), P.METAL_STEEL)
    make_cyl("Bench_Screw_Saucer", (3.05, 6.72, 0.955), 0.04, 0.012, (0.88, 0.86, 0.80, 1.0), segments=8)
    for si, (sxo, syo) in enumerate([(-0.012, 0.008), (0.010, -0.006), (0.002, 0.014)]):
        make_cyl(f"Bench_Screw_{si}", (3.05+sxo, 6.72+syo, 0.968), 0.004, 0.008,
                 (0.55, 0.55, 0.58, 1.0), segments=6)
    make_cyl("Bench_Loupe", (2.72, 6.55, 0.955), 0.035, 0.025, (0.24, 0.24, 0.26, 1.0), segments=10)
    # Tea going cold at the bench's far corner — ring already dry
    # beside it (yesterday's cup sat there too).
    make_cyl("Bench_Tea", (3.15, 7.05, 0.98), 0.04, 0.09, (0.62, 0.58, 0.50, 1.0), segments=8)
    make_cyl("Bench_Tea_Ring", (3.08, 6.95, 0.933), 0.045, 0.003, (0.44, 0.30, 0.20, 1.0), segments=8)
    # Reading glasses folded on the counter beside the paperback.
    make_box("Counter_Glasses_Bridge", (-0.95, 2.90, 0.965), (0.10, 0.015, 0.01), (0.24, 0.22, 0.20, 1.0))
    for gi, gxo in enumerate([-0.055, 0.055]):
        make_cyl(f"Counter_Glasses_Lens_{gi}", (-0.95+gxo, 2.90, 0.962), 0.025, 0.006,
                 (0.70, 0.76, 0.78, 0.6), segments=8)
    # One brass letter tab crooked — the alphabet is human.
    make_box("InvTab_Crooked", (0.65, ROOM_D-0.455, 1.64), (0.08, 0.02, 0.06), COL_BRASS)


def build_beyond_glass_2026_08():
    """D5 · through the storefront: the street ChillWave lives on —
    sidewalk, parked car, the shop across the way with one lit
    window (somebody else keeps late hours too). Edge-of-set bands;
    fog does the fade."""
    make_box("Street_Sidewalk", (0.0, -1.6, -0.02), (14.0, 2.6, 0.04), (0.56, 0.55, 0.52, 1.0))
    for ji, jx in enumerate([-4.5, -1.5, 1.5, 4.5]):
        make_box(f"Street_Sidewalk_Joint_{ji}", (jx, -1.6, 0.005), (0.04, 2.6, 0.01),
                 (0.44, 0.43, 0.40, 1.0))
    make_box("Street_Asphalt", (0.0, -4.6, -0.02), (14.0, 3.4, 0.04), (0.27, 0.27, 0.29, 1.0))
    # The parked car at the curb, framed by the SE glass.
    make_box("Street_Car_Body", (2.6, -2.5, 0.55), (4.2, 1.75, 0.55), (0.36, 0.30, 0.26, 1.0))
    make_box("Street_Car_Cabin", (2.3, -2.5, 1.02), (2.2, 1.6, 0.45), (0.36, 0.30, 0.26, 1.0))
    # The shopfront across the street: facade band + one lit window.
    make_box("Across_Facade", (0.0, -7.2, 2.0), (13.0, 0.6, 4.0), (0.38, 0.34, 0.30, 1.0))
    make_box("Across_Window_Dark", (-2.6, -6.85, 1.6), (1.6, 0.06, 1.3), (0.14, 0.15, 0.18, 1.0))
    make_box("Across_Window_Lit", (2.2, -6.85, 1.6), (1.6, 0.06, 1.3), (0.88, 0.78, 0.52, 1.0))
    make_box("Across_Door", (0.0, -6.85, 1.15), (0.95, 0.06, 2.3), (0.22, 0.20, 0.18, 1.0))
    # A street tree between the windows' sightlines.
    make_cyl("Street_Tree_Trunk", (-3.4, -2.2, 1.2), 0.12, 2.4, (0.30, 0.24, 0.18, 1.0), segments=8)
    make_box("Street_Tree_Crown", (-3.4, -2.2, 3.2), (1.8, 1.6, 1.8), (0.16, 0.24, 0.15, 1.0))


def main():
    clear_scene()
    build_shell()
    build_storefront()
    build_counter_front()
    build_back_inventory()
    build_workbench()
    build_ceiling_infra()
    build_decor()
    build_detail_pass_2026_08()
    build_use_states_2026_08()
    build_beyond_glass_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/chillwave_interior.glb"))
    print(f"\n[build_chillwave_interior] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
