"""pit_stop_interior — the Pit Stop DINER (vol6), front + kitchen.

2026-08-03 tail-wave RE-THEME. The old build here was a convenience
store — aisles, coolers, a lottery rack — but every vol6 scene set
in this locale is a DINER: Ben works the grill line (ch2, ch6), the
pass-through with a sightline to the grill (ch4), the back corner
booth "three from the kitchen, with a window" (ch7), the milk crate
by the walk-in that Jesse sits on (ch4), waitress service (ch7),
the back office door (ch4). Rebuilt to match the prose:

- Front of house: booth row along the W window wall with the BACK
  CORNER booth at SW (window + sightline to the pass-through),
  lunch counter + stools, two square 4-tops, register, pie case,
  waitress station.
- Partition at y=6.0 with the PASS-THROUGH (sill + ticket rail +
  service bell), the swing door, and a menu board above.
- Kitchen: flat-top grill + vent hood on the N wall, fryer, prep
  line, the WALK-IN cooler at the W end with the milk crate beside
  its door, the OFFICE door in the E wall, and the N kitchen
  window Ben catalogues parking-lot cars through.

Room: door/S wall at blender y=0, extends +Y; interior lands at
godot -Z. Footprint 11.0 x 9.0, ceiling 3.0.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import (make_counter, make_counter_bullnose, make_register,
                                   make_credit_card_terminal)
from _props.food_service import (make_coffee_pots, make_donut_display,
                                 make_paper_cup_stack, make_sugar_creamer_caddy)
from _props.cleaning import make_trash_can
from _props.decor import make_wall_clock, make_faded_poster, make_calendar
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture)
from _props.detail import (make_traffic_wear, make_floor_stain, make_scuff_band,
                           make_wall_tint_band, make_threshold, make_wall_outlet,
                           make_light_switch, make_cord_run, make_thermostat,
                           make_corner_guard)

ROOM_W = 11.0; ROOM_D = 9.0; CEIL = 3.0
PART_Y = 6.0          # FOH/kitchen partition
PAL_WALL = {"wall": (0.90, 0.87, 0.80, 1.0), "baseboard": (0.40, 0.34, 0.30, 1.0)}
COL_FLOOR = (0.80, 0.78, 0.72, 1.0); COL_SEAM = (0.44, 0.42, 0.38, 1.0)
COL_WOOD = (0.52, 0.40, 0.28, 1.0)
COL_BOOTH = (0.62, 0.26, 0.22, 1.0)       # oxblood vinyl
COL_TABLETOP = (0.82, 0.78, 0.68, 1.0)    # worn formica
COL_STEEL = (0.68, 0.70, 0.72, 1.0)
COL_STEEL_DK = (0.46, 0.48, 0.50, 1.0)
COL_GLASS = (0.62, 0.72, 0.76, 0.6)


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    # South wall with a centred entry-door gap.
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
                           ceil_z=CEIL, palette={"wood": COL_WOOD})


def build_windows():
    # Storefront glass either side of the door (S wall, Y-thin).
    for tag, wx in [("SW", -3.4), ("SE", 3.4)]:
        make_window(f"Win_{tag}", (wx, 0.10, 1.60), width=2.40, height=1.50)
    # W wall windows beside the booth row — the lot is out the W
    # glass (hand-built X-thin panes; make_window is Y-axis only).
    for tag, wy in [("W_Front", 1.55), ("W_Mid", 3.55)]:
        wx = -ROOM_W/2.0 + 0.10
        make_box(f"Win_{tag}_Frame", (wx, wy, 1.60), (0.06, 1.70, 1.55), COL_WOOD)
        make_box(f"Win_{tag}_Glass", (wx+0.01, wy, 1.60), (0.03, 1.54, 1.40), COL_GLASS)
        make_box(f"Win_{tag}_Mullion", (wx+0.02, wy, 1.60), (0.03, 0.05, 1.40), COL_WOOD)
    # Kitchen window on the N wall — Ben catalogues the parking-lot
    # cars through this from the grill (vol6_ch2).
    make_window("Win_Kitchen", (-3.2, ROOM_D-0.10, 1.65), width=1.40, height=1.10)


def _booth(tag, by, corner=False):
    """One W-wall booth: two facing vinyl benches + formica table."""
    bx = -ROOM_W/2.0 + 0.55
    for si, (yo, back_yo) in enumerate([(-0.52, -0.72), (0.52, 0.72)]):
        make_box(f"Booth_{tag}_Seat_{si}", (bx, by+yo, 0.44), (1.10, 0.42, 0.10), COL_BOOTH)
        make_box(f"Booth_{tag}_Back_{si}", (bx, by+back_yo, 0.80), (1.10, 0.10, 0.85), COL_BOOTH)
        make_box(f"Booth_{tag}_Base_{si}", (bx, by+yo, 0.20), (1.05, 0.40, 0.38), (0.30, 0.16, 0.14, 1.0))
    make_box(f"Booth_{tag}_Table", (bx+0.10, by, 0.74), (1.30, 0.70, 0.05), COL_TABLETOP)
    make_box(f"Booth_{tag}_TableEdge", (bx+0.10, by, 0.71), (1.32, 0.72, 0.02), (0.50, 0.48, 0.44, 1.0))
    make_cyl(f"Booth_{tag}_Ped", (bx+0.10, by, 0.36), 0.06, 0.70, COL_STEEL_DK, segments=8)
    # Table dress: napkin dispenser + ketchup.
    make_box(f"Booth_{tag}_Napkins", (bx-0.25, by+0.18, 0.82), (0.14, 0.06, 0.12), COL_STEEL)
    make_cyl(f"Booth_{tag}_Ketchup", (bx-0.22, by-0.18, 0.84), 0.035, 0.16, (0.72, 0.14, 0.10, 1.0), segments=8)
    if corner:
        # The back corner booth (vol6_ch7): a water glass + the
        # check folder Lydia leaves without being asked.
        make_cyl(f"Booth_{tag}_WaterGlass", (bx+0.35, by+0.20, 0.82), 0.04, 0.13, (0.80, 0.86, 0.88, 0.7), segments=8)
        make_box(f"Booth_{tag}_CheckFolder", (bx+0.30, by-0.22, 0.775), (0.16, 0.22, 0.015), (0.16, 0.16, 0.18, 1.0))


def build_booths():
    # Booth row down the W wall. The SW one is THE back corner booth
    # — "the corner one, three from the kitchen, with a window"
    # (vol6_ch7); its bench sightline runs N to the pass-through
    # (how Jim Wagner could see the grill in vol6_ch4).
    _booth("N", 4.90)
    _booth("Mid", 3.55)
    _booth("S", 2.20)
    _booth("Back_Corner", 0.85, corner=True)


def build_counter():
    # Lunch counter parallel to the partition, register at the E end.
    ccy = 4.55
    # make_counter's `depth` is X and `length` is Y. This counter's
    # stools, register, pie case and cup stack all spread along X,
    # so it was authored 90 DEGREES ROTATED: a 6m counter running
    # north-south through the pass-through partition and the prep
    # table, with the dining chairs inside its flank. Same bug as
    # the New Orleans bar (2026-08-12).
    top_z = make_counter("Lunch", (1.4, ccy, 0.0), length=0.75, depth=6.0, height=0.95,
                         palette={"formica": (0.74, 0.68, 0.58, 1.0),
                                  "top": COL_TABLETOP,
                                  "kick": (0.30, 0.26, 0.24, 1.0)})
    make_counter_bullnose("Lunch", (1.4, ccy-0.40, top_z), length=6.0,
                          palette={"top": COL_TABLETOP}, axis='X')
    # Stools bolted along the customer side.
    for si in range(6):
        sx = -1.0 + si * 0.96
        make_cyl(f"Stool_{si}_Post", (sx, ccy-0.95, 0.28), 0.05, 0.56, COL_STEEL_DK, segments=8)
        make_cyl(f"Stool_{si}_Seat", (sx, ccy-0.95, 0.60), 0.19, 0.07, COL_BOOTH, segments=10)
    make_register("RegisterMachine", (4.0, ccy+0.05, top_z))
    make_credit_card_terminal("CardTerm", (3.4, ccy-0.25, top_z))
    make_donut_display("PieCase", (-0.9, ccy+0.05, top_z))
    make_paper_cup_stack("CupStack", (0.2, ccy+0.10, top_z), count=12)
    make_sugar_creamer_caddy("Caddy", (1.4, ccy-0.15, top_z))
    # Coffee station on the back line between counter and partition.
    bz = make_counter("BackLine", (0.6, PART_Y-0.45, 0.0), length=0.60, depth=3.2, height=0.90,
                      palette={"formica": COL_STEEL_DK, "top": COL_STEEL,
                               "kick": (0.26, 0.26, 0.28, 1.0)})
    make_coffee_pots("CoffeePots", (0.0, PART_Y-0.45, bz), pots=2)


def build_tables():
    # Two square freestanding 4-tops mid-floor (square, not pedestal
    # rounds — seating is staged here in ch7's lunch crowd).
    for tag, tx, ty in [("A", 1.6, 1.6), ("B", 3.6, 2.9)]:
        make_box(f"Table_{tag}_Top", (tx, ty, 0.74), (0.90, 0.90, 0.05), COL_TABLETOP)
        for li, (lxo, lyo) in enumerate([(-0.38, -0.38), (0.38, -0.38), (-0.38, 0.38), (0.38, 0.38)]):
            make_box(f"Table_{tag}_Leg_{li}", (tx+lxo, ty+lyo, 0.36), (0.06, 0.06, 0.72), COL_WOOD)
        for ci, (cxo, cyo) in enumerate([(0.0, -0.75), (0.0, 0.75)]):
            make_box(f"Chair_{tag}_{ci}_Seat", (tx+cxo, ty+cyo, 0.45), (0.42, 0.42, 0.05), COL_WOOD)
            make_box(f"Chair_{tag}_{ci}_Back", (tx+cxo, ty+cyo+(0.20 if cyo > 0 else -0.20), 0.72),
                     (0.42, 0.05, 0.50), COL_WOOD)


def build_partition():
    # FOH/kitchen partition: pass-through + swing door + menu board.
    # Pass-through opening spans x -0.6..+2.0, sill 1.05, head 1.95.
    make_wall("Part_W", (-3.05, PART_Y, 0), length=4.9, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Part_UnderPass", (0.7, PART_Y, 0.525), (2.6, 0.20, 1.05), PAL_WALL["wall"])
    make_box("Part_AbovePass", (0.7, PART_Y, (1.95+CEIL)/2.0), (2.6, 0.20, CEIL-1.95), PAL_WALL["wall"])
    make_wall("Part_Mid", (2.45, PART_Y, 0), length=0.9, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Part_E", (4.75, PART_Y, 0), length=1.5, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Part_AboveSwing", (3.65, PART_Y, CEIL-0.45), (1.3, 0.20, 0.90), PAL_WALL["wall"])
    # Pass-through dress: stainless sill shelf, ticket rail, and THE
    # BELL (vol6 kitchen rhythm — order up).
    make_box("Pass_Sill", (0.7, PART_Y, 1.08), (2.7, 0.44, 0.05), COL_STEEL)
    make_box("Pass_TicketRail", (0.7, PART_Y-0.08, 1.92), (2.4, 0.03, 0.05), COL_STEEL_DK)
    for ti, tx in enumerate([-0.2, 0.5, 1.2]):
        make_box(f"Pass_Ticket_{ti}", (tx, PART_Y-0.10, 1.80), (0.12, 0.005, 0.16), (0.94, 0.92, 0.84, 1.0))
    make_cyl("Service_Bell_Base", (1.75, PART_Y-0.16, 1.115), 0.05, 0.02, COL_STEEL_DK, segments=10)
    make_cyl("Service_Bell_Dome", (1.75, PART_Y-0.16, 1.15), 0.045, 0.05, (0.85, 0.80, 0.55, 1.0), segments=10)
    # Swing door, slightly ajar, at x=3.65.
    make_box("Swing_Door", (3.65, PART_Y+0.06, 1.05), (1.05, 0.05, 2.10), (0.58, 0.56, 0.52, 1.0))
    make_box("Swing_Door_Porthole", (3.65, PART_Y+0.03, 1.55), (0.30, 0.03, 0.40), COL_GLASS)
    make_box("Swing_Door_Kick", (3.65, PART_Y+0.09, 0.35), (1.00, 0.02, 0.50), COL_STEEL)
    # Menu board over the pass-through, FOH side.
    make_box("MenuBoard", (0.7, PART_Y-0.12, 2.45), (2.8, 0.04, 0.60), (0.14, 0.14, 0.14, 1.0))
    for mi in range(4):
        make_box(f"MenuBoard_Line_{mi}", (0.7-1.0+mi*0.7, PART_Y-0.145, 2.45),
                 (0.55, 0.005, 0.42), (0.86, 0.84, 0.76, 1.0))


def build_kitchen():
    ky0 = PART_Y + 0.20
    # The GRILL — the flat-top line Ben works, on the N wall, with a
    # stainless vent hood over it.
    make_box("Grill_Body", (-1.0, ROOM_D-0.55, 0.475), (2.00, 0.85, 0.95), COL_STEEL_DK)
    make_box("Grill_FlatTop", (-1.0, ROOM_D-0.55, 0.97), (1.90, 0.75, 0.05), (0.22, 0.22, 0.24, 1.0))
    make_box("Grill_Backsplash", (-1.0, ROOM_D-0.16, 1.30), (2.00, 0.06, 0.60), COL_STEEL)
    make_box("Vent_Hood", (-1.0, ROOM_D-0.60, 2.35), (2.20, 1.00, 0.55), COL_STEEL)
    make_box("Vent_Duct", (-1.0, ROOM_D-0.45, 2.80), (0.60, 0.60, 0.40), COL_STEEL_DK)
    # Fryer beside the grill.
    make_box("Fryer_Body", (0.6, ROOM_D-0.50, 0.45), (0.70, 0.75, 0.90), COL_STEEL)
    make_box("Fryer_Baskets", (0.6, ROOM_D-0.50, 0.98), (0.55, 0.50, 0.10), (0.30, 0.30, 0.32, 1.0))
    # Stainless prep line down the middle of the kitchen.
    make_box("Prep_Table", (0.6, ky0+1.0, 0.45), (2.6, 0.75, 0.90), COL_STEEL)
    make_box("Prep_Top", (0.6, ky0+1.0, 0.925), (2.7, 0.85, 0.05), COL_STEEL)
    make_box("Prep_Undershelf", (0.6, ky0+1.0, 0.25), (2.5, 0.70, 0.04), COL_STEEL_DK)
    # WALK-IN cooler filling the kitchen's W end; heavy latched door
    # facing east, and THE MILK CRATE Jesse sits on beside it.
    make_box("WalkIn_Body", (-4.55, 7.45, 1.30), (1.70, 2.50, 2.60), (0.60, 0.62, 0.64, 1.0))
    make_box("WalkIn_Door", (-3.68, 7.05, 1.05), (0.06, 0.90, 2.10), COL_STEEL)
    make_box("WalkIn_Latch", (-3.64, 7.35, 1.05), (0.05, 0.12, 0.10), (0.30, 0.30, 0.32, 1.0))
    make_box("WalkIn_Hinge_T", (-3.66, 6.68, 1.75), (0.04, 0.06, 0.14), COL_STEEL_DK)
    make_box("WalkIn_Hinge_B", (-3.66, 6.68, 0.45), (0.04, 0.06, 0.14), COL_STEEL_DK)
    make_box("Milk_Crate", (-3.35, 6.45, 0.17), (0.35, 0.35, 0.33), (0.72, 0.28, 0.20, 1.0))
    make_box("Milk_Crate_Rim", (-3.35, 6.45, 0.335), (0.37, 0.37, 0.03), (0.62, 0.22, 0.16, 1.0))
    # The BACK OFFICE door in the E wall (vol6_ch4: Ben at the back
    # office door as Jesse comes through the kitchen).
    make_box("Office_Door", (ROOM_W/2.0-0.12, 7.4, 1.05), (0.06, 0.95, 2.10), (0.48, 0.38, 0.28, 1.0))
    make_box("Office_Door_Frame", (ROOM_W/2.0-0.10, 7.4, 2.16), (0.08, 1.10, 0.10), COL_WOOD)
    make_cyl("Office_Door_Knob", (ROOM_W/2.0-0.16, 7.05, 1.05), 0.035, 0.04, (0.72, 0.66, 0.40, 1.0), segments=8)
    # Dry-storage shelf on the E kitchen wall + a mop by the corner.
    for zi in range(3):
        make_box(f"DryShelf_{zi}", (ROOM_W/2.0-0.30, 8.5, 0.60+zi*0.55), (0.50, 0.90, 0.04), COL_STEEL_DK)
        for ci in range(3):
            make_cyl(f"DryCan_{zi}_{ci}", (ROOM_W/2.0-0.30, 8.20+ci*0.30, 0.60+zi*0.55+0.11),
                     0.08, 0.20, P.SNACK_TINTS[(zi+ci) % len(P.SNACK_TINTS)], segments=8)


def build_decor():
    make_wall_clock("Clock", (-2.0, PART_Y-0.12, CEIL-0.55), frozen_hour=9, frozen_min=18)
    make_calendar("Calendar_Kitchen", (2.4, ROOM_D-0.13, 1.70))
    make_faded_poster("Poster_E", (ROOM_W/2.0-0.05, 2.6, 1.60))
    make_trash_can("Trash", (4.9, 0.9, 0.0), branded=False,
                   palette={"body": (0.30, 0.30, 0.32, 1.0)})
    make_box("FloorMat", (0.0, 0.7, 0.02), (1.60, 1.00, 0.02), P.RUBBER_MAT)
    # Waitress station against the E wall — coffee refills, pads.
    wz = make_counter("WaitStation", (ROOM_W/2.0-0.45, 3.4, 0.0), length=1.10, depth=0.55, height=0.90,
                      palette={"formica": COL_WOOD, "top": COL_TABLETOP,
                               "kick": (0.30, 0.26, 0.24, 1.0)})
    make_box("WaitStation_Pads", (ROOM_W/2.0-0.45, 3.2, wz+0.02), (0.18, 0.13, 0.03), (0.94, 0.92, 0.84, 1.0))
    make_paper_cup_stack("WaitStation_Cups", (ROOM_W/2.0-0.45, 3.7, wz), count=8)


def build_ceiling_infra():
    # Kitchen keeps commercial fluorescents; FOH gets warm pendants
    # over the booth row and the counter (it's a diner, not a store).
    for j, ypos in enumerate([6.9, 8.3]):
        make_fluorescent_tube_fixture(f"Fluor_K{j}", (0.0, ypos, CEIL), length=1.60, width=0.36)
    for pi, (px, py) in enumerate([(-4.4, 1.5), (-4.4, 3.6), (0.4, 3.9), (2.4, 3.9), (2.6, 1.7)]):
        make_cyl(f"Pendant_{pi}_Cord", (px, py, CEIL-0.15), 0.015, 0.30, (0.20, 0.20, 0.20, 1.0), segments=6)
        make_cyl(f"Pendant_{pi}_Shade", (px, py, CEIL-0.38), 0.16, 0.16, (0.30, 0.42, 0.30, 1.0), segments=10)
        make_cyl(f"Pendant_{pi}_Bulb", (px, py, CEIL-0.44), 0.05, 0.06, (0.98, 0.92, 0.72, 1.0), segments=8)
    make_smoke_detector("Smoke", (-1.5, 4.5, CEIL))
    make_hvac_vent("HVAC", (3.5, 1.0, CEIL), width=0.80, depth=0.40)


def build_detail_pass_2026_08():
    """D2 surface breakup + D3 infrastructure (set-detail playbook).
    The diner's wear is 30 years of boots: traffic ribbon from the
    door past the counter to the pass-through, kick scuffs, grease
    shadow at the grill, plugged-in everything. D4 (use states) and
    D5 (through-the-windows) are the next passes."""
    wear = (0.70, 0.68, 0.62, 1.0)         # floor darkened ~12%
    scuff = (0.20, 0.17, 0.16, 1.0)
    # D2 · the path feet actually take: door -> counter front ->
    # swing door (L-shaped axis-aligned runs).
    make_traffic_wear("Wear_Main", [(0.0, 0.6), (0.0, 3.6), (3.2, 3.6)],
                      width=0.9, tint=wear)
    make_traffic_wear("Wear_Booths", [(0.0, 1.2), (-3.4, 1.2)],
                      width=0.7, tint=wear)
    make_traffic_wear("Wear_Kitchen", [(3.65, 6.4), (-1.0, 6.4), (-1.0, 8.0)],
                      width=0.8, tint=(0.66, 0.64, 0.58, 1.0))
    # Stains: grill grease shadow, fryer drips, counter coffee ring.
    make_floor_stain("Stain_Grill", (-1.0, 7.9), radius=0.65,
                     tint=(0.55, 0.52, 0.46, 1.0))
    make_floor_stain("Stain_Fryer", (0.6, 7.8), radius=0.35,
                     tint=(0.50, 0.47, 0.42, 1.0))
    make_floor_stain("Stain_Counter", (1.2, 3.75), radius=0.28, tint=wear)
    # Kick scuffs: counter customer face + swing door + booth bases.
    make_scuff_band("Scuff_Counter", (1.4, 4.11), length=5.6, axis='X',
                    band_z=0.12, tint=scuff)
    make_scuff_band("Scuff_SwingDoor", (3.65, PART_Y+0.13), length=1.0,
                    axis='X', band_z=0.10, tint=scuff)
    # Ceiling-shadow gather at the top of the big walls (proud 5mm).
    make_wall_tint_band("Band_N", (0.0, ROOM_D-0.105, 0.0), length=ROOM_W-0.4,
                        axis='X', band_z=CEIL-0.18, tint=(0.82, 0.79, 0.72, 1.0))
    make_wall_tint_band("Band_W", (-ROOM_W/2.0+0.105, ROOM_D/2.0, 0.0),
                        length=ROOM_D-0.4, axis='Y', band_z=CEIL-0.18,
                        tint=(0.82, 0.79, 0.72, 1.0))
    make_threshold("Threshold_Front", (0.0, 0.10), width=1.9, axis='X')
    # D3 · the room is plugged in.
    make_light_switch("Switch_Front", (1.15, 0.0), axis='X', face_sign=1, aged=True)
    make_wall_outlet("Outlet_Booths", (-ROOM_W/2.0, 2.9), axis='Y', face_sign=1, aged=True)
    make_wall_outlet("Outlet_BackLine", (0.6, PART_Y), axis='X', face_sign=-1, aged=True)
    make_wall_outlet("Outlet_Kitchen", (ROOM_W/2.0, 8.3), axis='Y', face_sign=-1, aged=True)
    make_thermostat("Thermostat", (2.2, PART_Y), axis='X', face_sign=-1)
    # Cords: register + coffee station reach real outlets.
    make_cord_run("Cord_Register", (4.0, 4.85, 0.90), (5.39, 8.3, 0.30))
    make_cord_run("Cord_Coffee", (0.0, PART_Y-0.45, 0.85), (0.6, PART_Y-0.11, 0.30))
    make_corner_guard("CornerGuard_Swing", (2.9, PART_Y-0.12))


def build_use_states_2026_08():
    """D4 · mid-task, not showroom (set-detail playbook). The diner
    is CAUGHT WORKING: the wipe-rag still on the counter, an order
    up on the grill, one table half-bussed, the trash telling the
    truth. D6 (coverage + light) is the next pass."""
    # Counter mid-wipe: the rag where Brenda left it + a customer's
    # half-finished coffee two stools down from the register.
    make_box("Counter_Rag", (0.2, 4.42, 1.005), (0.24, 0.18, 0.02), (0.72, 0.74, 0.70, 1.0))
    make_cyl("Counter_Coffee", (2.4, 4.40, 1.05), 0.04, 0.09, (0.92, 0.90, 0.86, 1.0), segments=8)
    make_cyl("Counter_Coffee_Ring", (2.55, 4.36, 1.001), 0.05, 0.003, (0.66, 0.60, 0.52, 1.0), segments=8)
    # The grill mid-order: two patties, the spatula resting on the
    # flat-top edge, a side towel over the hood bar.
    for pi, pxo in enumerate([-0.25, 0.05]):
        make_cyl(f"Grill_Patty_{pi}", (-1.0+pxo, 8.4, 1.01), 0.07, 0.02, (0.36, 0.22, 0.14, 1.0), segments=10)
    make_box("Grill_Spatula_Blade", (-0.35, 8.35, 1.005), (0.09, 0.11, 0.008), P.METAL_STEEL)
    make_box("Grill_Spatula_Handle", (-0.35, 8.15, 1.02), (0.03, 0.22, 0.02), (0.20, 0.20, 0.22, 1.0))
    make_box("Hood_Towel", (-0.2, 8.35, 2.10), (0.30, 0.06, 0.28), (0.80, 0.80, 0.76, 1.0))
    # Ticket on the pass-through rail mid-order (one more than the
    # static three — this one's crooked).
    make_box("Pass_Ticket_Live", (1.05, PART_Y-0.11, 1.78), (0.13, 0.005, 0.15), (0.96, 0.94, 0.86, 1.0))
    # Table A half-bussed: two plates stacked, crumpled napkin, one
    # chair shoved out of true.
    make_cyl("TableA_Plate_Stack", (1.45, 1.55, 0.79), 0.11, 0.035, (0.90, 0.88, 0.84, 1.0), segments=10)
    make_box("TableA_Napkin_Crumple", (1.85, 1.70, 0.78), (0.07, 0.06, 0.045), (0.86, 0.86, 0.82, 1.0))
    make_box("TableA_Chair_Shoved_Seat", (1.6, 0.62, 0.45), (0.42, 0.42, 0.05), COL_WOOD)
    make_box("TableA_Chair_Shoved_Back", (1.6, 0.44, 0.72), (0.42, 0.05, 0.50), COL_WOOD)
    # Pie case truth: one slice already out, on a plate beside it.
    make_cyl("Pie_Slice_Plate", (-0.35, 4.65, 1.005), 0.09, 0.015, (0.90, 0.88, 0.84, 1.0), segments=10)
    make_box("Pie_Slice", (-0.35, 4.65, 1.035), (0.09, 0.06, 0.045), (0.78, 0.56, 0.30, 1.0))
    # The trash tells the truth: two crumples NEAR the can.
    for ci, (cxo, cyo) in enumerate([(-0.35, 0.15), (0.28, -0.22)]):
        make_box(f"Trash_Crumple_{ci}", (4.9+cxo, 0.9+cyo, 0.035), (0.07, 0.06, 0.06), (0.88, 0.87, 0.82, 1.0))
    # Second milk crate stacked askew by the walk-in (Jesse's seat
    # has a spare — crates accumulate).
    make_box("Milk_Crate_2", (-3.30, 6.42, 0.50), (0.35, 0.35, 0.33), (0.24, 0.36, 0.62, 1.0))
    # Swing-door wedge kicked half under the door.
    make_box("Swing_Door_Wedge", (3.35, PART_Y-0.18, 0.03), (0.10, 0.14, 0.06), (0.52, 0.40, 0.28, 1.0))


def build_beyond_glass_2026_08():
    """D5 · something through every window. W + N glass show the
    PARKING LOT — including the Louisiana pickup that sits in the
    Pit Stop lot with a driver who never enters (Ben's list, item
    2, vol6_ch3). S glass shows the road + the strip across it.
    Cheap silhouette band geometry; fog and glass do the rest."""
    # ── The lot, west of the building (out the booth windows) ──
    make_box("Lot_Asphalt_W", (-9.5, 4.5, -0.02), (7.6, 11.0, 0.04), (0.30, 0.30, 0.32, 1.0))
    for si, sy in enumerate([2.0, 4.4, 6.8]):
        make_box(f"Lot_Stripe_W_{si}", (-7.2, sy, 0.005), (0.10, 1.8, 0.01), (0.86, 0.84, 0.78, 1.0))
    # Two parked cars + THE LOUISIANA PICKUP (nose-in, engine cold,
    # driver never enters) framed by the W_Mid booth window.
    for tag, cy2, col in [("A", 1.9, (0.32, 0.34, 0.40, 1.0)), ("B", 6.6, (0.62, 0.60, 0.56, 1.0))]:
        make_box(f"Lot_Car_{tag}_Body", (-7.6, cy2, 0.55), (4.2, 1.75, 0.55), col)
        make_box(f"Lot_Car_{tag}_Cabin", (-7.9, cy2, 1.02), (2.2, 1.6, 0.45), col)
    make_box("Lot_LA_Pickup_Body", (-8.1, 4.35, 0.62), (4.8, 1.85, 0.70), (0.30, 0.24, 0.20, 1.0))
    make_box("Lot_LA_Pickup_Cab", (-9.1, 4.35, 1.25), (1.8, 1.75, 0.55), (0.30, 0.24, 0.20, 1.0))
    make_box("Lot_LA_Pickup_Bed_Rim", (-6.9, 4.35, 1.02), (2.3, 1.85, 0.08), (0.24, 0.19, 0.16, 1.0))
    # Lot light pole + far treeline wall (edge-of-set).
    make_cyl("Lot_Pole", (-11.5, 4.5, 3.0), 0.09, 6.0, (0.40, 0.40, 0.42, 1.0), segments=8)
    make_box("Lot_Pole_Head", (-11.2, 4.5, 6.0), (0.7, 0.25, 0.18), (0.30, 0.30, 0.32, 1.0))
    make_box("Lot_Treeline_W", (-13.6, 4.5, 2.2), (0.4, 12.0, 4.4), (0.13, 0.18, 0.13, 1.0))
    # ── North strip (out the kitchen window): the lot corner Ben
    # catalogues + the same treeline running behind ──
    make_box("Lot_Asphalt_N", (-2.0, 11.0, -0.02), (8.0, 3.6, 0.04), (0.30, 0.30, 0.32, 1.0))
    make_box("Lot_Treeline_N", (-2.0, 13.2, 2.2), (10.0, 0.4, 4.4), (0.13, 0.18, 0.13, 1.0))
    # ── South: the state-highway strip + the building across it ──
    make_box("Road_S", (0.0, -3.2, -0.02), (16.0, 3.0, 0.04), (0.26, 0.26, 0.28, 1.0))
    make_box("Road_S_Centerline", (0.0, -3.2, 0.005), (14.0, 0.10, 0.01), (0.85, 0.76, 0.30, 1.0))
    make_box("Strip_Across", (1.5, -6.4, 1.7), (10.0, 0.8, 3.4), (0.42, 0.38, 0.34, 1.0))
    make_box("Strip_Across_Sign", (-2.0, -5.9, 3.0), (1.6, 0.12, 0.7), (0.66, 0.58, 0.42, 1.0))


def main():
    clear_scene()
    build_shell()
    build_windows()
    build_booths()
    build_counter()
    build_tables()
    build_partition()
    build_kitchen()
    build_decor()
    build_ceiling_infra()
    build_detail_pass_2026_08()
    build_use_states_2026_08()
    build_beyond_glass_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pit_stop_interior.glb"))
    print(f"\n[build_pit_stop_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
