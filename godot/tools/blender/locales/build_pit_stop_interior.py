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
godot -Z. Footprint 11.0 x 11.0, ceiling 3.0.

KITCHEN DRAFT 2 (2026-10-09, the overnight run; CLAUDE.md "build big"):
the kitchen was a 3 m galley behind the partition — grill, fryer, one
prep table, washed out under a white key, and the grill insert framed
the backsplash. The building now runs 2 m further north (kitchen
y 6.1..10.9) and the kitchen is a working line:
  - the COOK LINE on the N wall under one long hood (range, flat-top on
    a chef base, two-well fryer, lowboy), hood lights, a ticket rail on
    the hood lip, the anti-fatigue mat;
  - Ben's WINDOW to the line's left, a hand sink under it — he glances
    left from the flat-top to catalogue the back lot (the dumpster
    enclosure out there: "Dumpster at two-fifteen");
  - a plating ISLAND mid-kitchen (Ben's phone face-up on it), the pass
    counter + heat lamp on the kitchen side of the pass-through;
  - dry storage + a speed rack by the walk-in; the DISH PIT on the E
    wall past the office door; paper-goods shelving on the N wall;
  - quarry-tile floor, sage FRP to 2 m, so the kitchen stops reading
    as one white field.
Draft 3 targets: steam and smoke over the flat-top (a particle pass),
grease on the hood filters, the back door to the dumpster, Deck
framing of the line from the swing door.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_table, make_chair
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_tube, export_glb
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings
from _props.store_fixtures import (make_counter, make_counter_bullnose, make_register,
                                   make_credit_card_terminal)
from _props.food_service import (make_coffee_pots, make_donut_display,
                                 make_paper_cup_stack, make_sugar_creamer_caddy)
from _props.cleaning import make_trash_can
from _props.decor import make_wall_clock, make_faded_poster, make_calendar, make_fire_extinguisher
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture)
from _props.detail import (make_traffic_wear, make_floor_stain, make_scuff_band,
                           make_wall_tint_band, make_threshold, make_wall_outlet,
                           make_light_switch, make_cord_run, make_thermostat,
                           make_corner_guard)

ROOM_W = 11.0; ROOM_D = 11.0; CEIL = 3.0   # kitchen deepened 2.0 m (2026-10-09: it was a 3 m galley)
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
    # (2026-10-07) Wall_W out of the loop: its window is cut
    make_wall_with_openings("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=+1, openings=[(1.55, 1.60, 1.54, 1.40), (3.55, 1.60, 1.54, 1.40)])
    make_wall("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',   # cut 2026-10-07: its window was a pane on a solid wall
              palette=PAL_WALL, baseboard_face_sign=-1, openings=[(-3.2, 1.65, 1.40, 1.10)])
    # South wall with a centred entry-door gap.
    make_wall_with_openings("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,   # cut 2026-10-07: its window was a pane on a solid wall
              axis='X', palette=PAL_WALL, baseboard_face_sign=+1, openings=[(-3.18, 1.60, 1.96, 1.50)])
    make_wall_with_openings("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL,   # cut 2026-10-07: its window was a pane on a solid wall
              axis='X', palette=PAL_WALL, baseboard_face_sign=+1, openings=[(3.18, 1.60, 1.96, 1.50)])
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
    # built toward the room (2026-09-23: into the S wall, invisible);
    # 1.96 wide so the SW frame clears the corner booth's back
    for tag, wx in [("SW", -3.18), ("SE", 3.18)]:
        make_window(f"Win_{tag}", (wx, 0.10, 1.60), width=1.96, height=1.50, room_dir=+1, see_through=True)
    # W wall windows beside the booth row — the lot is out the W
    # glass (hand-built X-thin panes).
    for tag, wy in [("W_Front", 1.55), ("W_Mid", 3.55)]:
        wx = -ROOM_W/2.0 + 0.10
        # (2026-10-07: the "frame" was one solid 1.70 x 1.55 slab — a
        # brown board over the cut; now head, sill and two jambs)
        for fn, fy, fz, fsy, fsz in (("Head", wy, 2.335, 1.70, 0.08), ("Sill", wy, 0.865, 1.70, 0.08),
                                     ("JambS", wy - 0.81, 1.60, 0.08, 1.55), ("JambN", wy + 0.81, 1.60, 0.08, 1.55)):
            make_box(f"Win_{tag}_Frame_{fn}", (wx, fy, fz), (0.06, fsy, fsz), COL_WOOD)
        # (2026-10-07: the wall is cut; the opaque glass box went — the lot is SEEN)
        make_box(f"Win_{tag}_Mullion", (wx+0.02, wy, 1.60), (0.03, 0.05, 1.40), COL_WOOD)
        make_box(f"Win_{tag}_Glint", (wx, wy - 0.40, 1.60), (0.004, 0.03, 1.40), (0.84, 0.88, 0.92, 1.0))   # sill to head
    # Kitchen window on the N wall — Ben catalogues the parking-lot
    # cars through this from the grill (vol6_ch2).
    make_window("Win_Kitchen", (-3.2, ROOM_D-0.10, 1.65), width=1.40, height=1.10, see_through=True)


def _booth(tag, by, corner=False):
    """One W-wall booth: two facing vinyl benches + formica table."""
    bx = -ROOM_W/2.0 + 0.68   # flush with the window frames (2026-09-23: the backs sat 10 cm in the wall, 13 in the frames)
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
        make_table(f"Table_{tag}", tx, ty, w=0.90, d=0.90, h=0.765, wood=COL_WOOD, top_col=COL_TABLETOP)
        for ci, (cxo, cyo) in enumerate([(0.0, -0.75), (0.0, 0.75)]):
            make_chair(f"Chair_{tag}_{ci}", tx+cxo, ty+cyo, yaw=(3.1416 if cyo > 0 else 0.0), wood=COL_WOOD, w=0.42)


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
        make_box(f"Pass_Ticket_{ti}", (tx, PART_Y-0.10, 1.82), (0.12, 0.005, 0.16), (0.94, 0.92, 0.84, 1.0))   # clipped IN the rail (2026-09-23: 1.5 cm under it)
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
    """KITCHEN DRAFT 2 (2026-10-09). Kitchen y 6.1..10.9 (partition N
    face to N wall face), x -5.4..5.4. See the module docstring."""
    KN, KS, XE, XW = ROOM_D - 0.10, PART_Y + 0.10, ROOM_W / 2.0 - 0.10, -ROOM_W / 2.0 + 0.10
    steel, steel_dk = COL_STEEL, COL_STEEL_DK
    knob = (0.14, 0.14, 0.15, 1.0)
    # ── surfaces: quarry tile floor, sage FRP to 2 m ──
    quarry, grout = (0.50, 0.30, 0.22, 1.0), (0.36, 0.24, 0.19, 1.0)
    make_box("Kitchen_Floor_Quarry", (0.0, (KS + KN) / 2.0, 0.004), (XE - XW, KN - KS, 0.008), quarry)
    gx = XW + 0.6
    while gx < XE - 0.1:
        make_box(f"Kitchen_Floor_Grout_X_{gx:+.1f}", (gx, (KS + KN) / 2.0, 0.009), (0.012, KN - KS, 0.002), grout)
        gx += 0.6
    gy = KS + 0.6
    while gy < KN - 0.1:
        make_box(f"Kitchen_Floor_Grout_Y_{gy:.1f}", (0.0, gy, 0.009), (XE - XW, 0.012, 0.002), grout)
        gy += 0.6
    frp, cap = (0.62, 0.68, 0.58, 1.0), (0.48, 0.52, 0.46, 1.0)
    for nm, x0, x1, z1 in (("N_W", XW, -3.9, 2.0), ("N_Sill", -3.9, -2.5, 1.10), ("N_E", -2.5, XE, 2.0)):
        make_box(f"Kitchen_FRP_{nm}", ((x0 + x1) / 2.0, KN - 0.005, z1 / 2.0), (x1 - x0, 0.01, z1), frp)
    make_box("Kitchen_FRP_Cap_N", (0.0, KN - 0.01, 2.01), (XE - XW, 0.02, 0.03), cap)
    make_box("Kitchen_FRP_W", (XW + 0.005, (KS + KN) / 2.0, 1.0), (0.01, KN - KS, 2.0), frp)
    for nm, y0, y1 in (("E_S", KS, 6.85), ("E_N", 7.95, KN)):
        make_box(f"Kitchen_FRP_{nm}", (XE - 0.005, (y0 + y1) / 2.0, 1.0), (0.01, y1 - y0, 2.0), frp)
    for nm, x0, x1, z1 in (("S_W", XW, -0.6, 2.0), ("S_Mid", 2.0, 2.9, 2.0), ("S_E", 4.3, XE, 2.0)):
        make_box(f"Kitchen_FRP_{nm}", ((x0 + x1) / 2.0, KS + 0.005, z1 / 2.0), (x1 - x0, 0.01, z1), frp)

    # ── THE COOK LINE · N wall, under one hood ──
    ly, ld = KN - 0.425, 0.85                       # equipment centre-line, depth
    make_box("Line_Backsplash", (0.25, KN - 0.015, 1.475), (5.5, 0.01, 1.15), steel)
    # six-burner range with its oven
    rx = -1.90
    make_box("Range_Body", (rx, ly, 0.45), (0.90, ld, 0.90), steel)
    make_box("Range_Grate", (rx, ly - 0.03, 0.915), (0.86, 0.76, 0.03), knob)
    for bi in range(6):
        bx_, by_ = rx - 0.27 + (bi % 3) * 0.27, ly - 0.22 + (bi // 3) * 0.36
        make_cyl(f"Range_Burner_{bi}", (bx_, by_, 0.935), 0.09, 0.01, (0.24, 0.22, 0.20, 1.0), segments=10)
    make_cyl("Range_Stockpot", (rx - 0.27, ly + 0.14, 1.09), 0.16, 0.30, steel, segments=14)
    make_cyl("Range_Stockpot_Lid", (rx - 0.27, ly + 0.14, 1.245), 0.165, 0.01, steel_dk, segments=14)
    make_cyl("Range_Saucepan", (rx + 0.27, ly - 0.22, 0.99), 0.10, 0.10, steel_dk, segments=12)
    make_box("Range_Saucepan_Handle", (rx + 0.27, ly - 0.42, 1.02), (0.03, 0.22, 0.02), knob)
    make_box("Range_Oven_Door", (rx, ly - ld / 2.0 - 0.006, 0.42), (0.76, 0.012, 0.50), (0.60, 0.62, 0.64, 1.0))
    make_box("Range_Oven_Handle", (rx, ly - ld / 2.0 - 0.02, 0.62), (0.60, 0.03, 0.025), steel_dk)
    for ki in range(6):
        make_cyl(f"Range_Knob_{ki}", (rx - 0.33 + ki * 0.132, ly - ld / 2.0 - 0.02, 0.80), 0.022, 0.03, knob, segments=8, axis='Y')
    # flat-top griddle on a refrigerated chef base — Ben's station
    gxc = -0.50
    make_box("Grill_ChefBase", (gxc, ly, 0.30), (1.80, ld, 0.60), steel)
    for di, ox in enumerate((-0.45, 0.45)):
        make_box(f"Grill_ChefBase_Drawer_{di}", (gxc + ox, ly - ld / 2.0 - 0.006, 0.30), (0.84, 0.012, 0.50), (0.60, 0.62, 0.64, 1.0))
        make_box(f"Grill_ChefBase_Pull_{di}", (gxc + ox, ly - ld / 2.0 - 0.025, 0.50), (0.50, 0.025, 0.025), steel_dk)
    make_box("Grill_Body", (gxc, ly, 0.78), (1.80, ld, 0.36), steel_dk)
    make_box("Grill_FlatTop", (gxc, ly + 0.025, 0.98), (1.72, 0.70, 0.04), (0.20, 0.20, 0.22, 1.0))
    make_box("Grill_Trough", (gxc, ly - 0.36, 0.97), (1.72, 0.08, 0.04), steel)
    for nm, ox in (("W", -0.89), ("E", 0.89)):
        make_box(f"Grill_Splash_{nm}", (gxc + ox, ly + 0.025, 1.08), (0.02, 0.70, 0.24), steel)
    for ki in range(5):
        make_cyl(f"Grill_Knob_{ki}", (gxc - 0.70 + ki * 0.35, ly - ld / 2.0 - 0.02, 0.86), 0.022, 0.03, knob, segments=8, axis='Y')
    for bi, ox in enumerate((0.25, 0.42)):
        make_cyl(f"Grill_Bun_{bi}", (gxc + ox, ly + 0.15, 1.012), 0.055, 0.025, (0.80, 0.60, 0.34, 1.0), segments=10)
    make_cyl("Grill_Press", (gxc - 0.62, ly + 0.20, 1.02), 0.09, 0.04, knob, segments=10)
    # two-well fryer, baskets on the rail
    fx = 0.85
    make_box("Fryer_Body", (fx, ly, 0.45), (0.80, ld, 0.90), steel)
    for wi, ox in enumerate((-0.20, 0.20)):
        make_box(f"Fryer_Well_{wi}", (fx + ox, ly + 0.02, 0.905), (0.34, 0.55, 0.012), (0.46, 0.34, 0.12, 1.0))
        make_box(f"Fryer_Basket_{wi}", (fx + ox, KN - 0.165, 1.03), (0.30, 0.22, 0.14), (0.30, 0.30, 0.32, 1.0))
    make_box("Fryer_Basket_Rail", (fx, KN - 0.04, 1.10), (0.76, 0.04, 0.03), steel)
    make_box("Fryer_Drain_Door", (fx, ly - ld / 2.0 - 0.006, 0.40), (0.70, 0.012, 0.56), (0.60, 0.62, 0.64, 1.0))
    # lowboy: refrigerated work top with the cut veg and the ticket printer
    lx = 2.10
    make_box("Lowboy_Body", (lx, ly, 0.43), (1.60, ld, 0.86), steel)
    make_box("Lowboy_Top", (lx, ly, 0.875), (1.62, ld + 0.02, 0.03), steel)
    for di, ox in enumerate((-0.40, 0.40)):
        make_box(f"Lowboy_Drawer_{di}", (lx + ox, ly - ld / 2.0 - 0.006, 0.45), (0.74, 0.012, 0.60), (0.60, 0.62, 0.64, 1.0))
        make_box(f"Lowboy_Pull_{di}", (lx + ox, ly - ld / 2.0 - 0.025, 0.70), (0.50, 0.025, 0.025), steel_dk)
    make_box("Lowboy_CuttingBoard", (lx - 0.25, ly - 0.10, 0.90), (0.50, 0.35, 0.02), (0.92, 0.92, 0.88, 1.0))
    make_box("Lowboy_Knife", (lx - 0.20, ly - 0.08, 0.915), (0.26, 0.03, 0.01), steel)
    for pi, (ox, fill) in enumerate(((-0.10, (0.46, 0.66, 0.30, 1.0)), (0.08, (0.80, 0.24, 0.18, 1.0)), (0.26, (0.90, 0.86, 0.74, 1.0)))):
        make_box(f"Lowboy_Bain_{pi}", (lx + ox, KN - 0.18, 0.94), (0.16, 0.26, 0.10), steel)
        make_box(f"Lowboy_Bain_{pi}_Fill", (lx + ox, KN - 0.18, 0.993), (0.14, 0.24, 0.006), fill)
    make_box("Ticket_Printer", (lx + 0.62, KN - 0.20, 0.96), (0.18, 0.20, 0.14), knob)
    make_box("Ticket_Printer_Paper", (lx + 0.62, KN - 0.31, 1.0), (0.08, 0.02, 0.10), (0.94, 0.92, 0.84, 1.0))
    # the hood: canopy, filters, lip, lights, duct to the roof
    make_box("Vent_Hood", (0.25, KN - 0.525, 2.33), (5.6, 1.05, 0.55), steel)
    make_box("Vent_Hood_Filters", (0.25, KN - 0.30, 2.04), (5.4, 0.45, 0.03), (0.36, 0.36, 0.36, 1.0))
    make_box("Vent_Hood_Lip", (0.25, KN - 1.03, 2.00), (5.6, 0.04, 0.12), steel)
    for hi, hx in enumerate((-1.5, 0.3, 2.1)):
        make_box(f"Hood_Light_{hi}", (hx, KN - 0.65, 2.045), (0.30, 0.20, 0.02), (1.0, 0.90, 0.70, 1.0))
    make_box("Vent_Duct", (0.25, KN - 0.45, 2.80), (0.70, 0.60, 0.39), steel_dk)
    # the ticket rail on the hood lip, three tickets riding it
    make_box("Line_TicketRail", (0.0, KN - 1.07, 1.97), (2.4, 0.03, 0.04), steel_dk)
    for ti, tx in enumerate((-0.8, -0.1, 0.5)):
        make_box(f"Line_Ticket_{ti}", (tx, KN - 1.075, 1.875), (0.10, 0.004, 0.16), (0.96, 0.94, 0.86, 1.0))
    make_box("Line_Mat", (0.2, KN - 1.35, 0.018), (4.6, 0.80, 0.016), (0.10, 0.10, 0.11, 1.0))
    # ── Ben's window: a hand sink under it ──
    make_box("Hand_Sink", (-3.2, KN - 0.20, 0.86), (0.45, 0.40, 0.18), steel)
    make_box("Hand_Sink_Bowl", (-3.2, KN - 0.22, 0.952), (0.36, 0.30, 0.006), (0.40, 0.42, 0.44, 1.0))
    make_box("Hand_Sink_Bracket", (-3.2, KN - 0.03, 0.66), (0.30, 0.06, 0.22), steel_dk)
    make_cyl("Hand_Sink_Faucet", (-3.2, KN - 0.04, 1.00), 0.015, 0.10, steel, segments=6)
    make_box("Hand_Sink_Spout", (-3.2, KN - 0.10, 1.045), (0.025, 0.12, 0.02), steel)
    make_box("Hand_Sink_Soap", (-2.92, KN - 0.025, 1.02), (0.08, 0.05, 0.12), (0.90, 0.88, 0.84, 1.0))
    make_box("Hand_Sink_Sign", (-3.62, KN - 0.006, 1.00), (0.18, 0.004, 0.12), (0.92, 0.92, 0.88, 1.0))
    # ── W end: the walk-in (door E, the milk crates beside it) ──
    make_box("WalkIn_Body", (-4.55, 7.45, 1.30), (1.70, 2.50, 2.60), (0.60, 0.62, 0.64, 1.0))
    make_box("WalkIn_Door", (-3.68, 7.05, 1.05), (0.06, 0.90, 2.10), steel)
    make_box("WalkIn_Latch", (-3.64, 7.35, 1.05), (0.05, 0.12, 0.10), (0.30, 0.30, 0.32, 1.0))
    make_box("WalkIn_Hinge_T", (-3.66, 6.68, 1.75), (0.04, 0.06, 0.14), steel_dk)
    make_box("WalkIn_Hinge_B", (-3.66, 6.68, 0.45), (0.04, 0.06, 0.14), steel_dk)
    make_box("WalkIn_Condenser", (-4.55, 7.45, 2.75), (0.80, 0.60, 0.30), steel_dk)
    make_box("WalkIn_Thermo", (-3.69, 7.90, 1.60), (0.02, 0.10, 0.10), (0.92, 0.92, 0.88, 1.0))
    make_box("WalkIn_TempLog", (-3.69, 8.25, 1.45), (0.02, 0.22, 0.30), (0.94, 0.92, 0.84, 1.0))
    make_box("Milk_Crate", (-3.35, 6.275, 0.17), (0.35, 0.35, 0.33), (0.72, 0.28, 0.20, 1.0))   # against the partition's N face at 6.1 (2026-09-25: 18 cm off it)
    make_box("Milk_Crate_Rim", (-3.35, 6.45, 0.335), (0.37, 0.37, 0.03), (0.62, 0.22, 0.16, 1.0))
    # dry storage: wire shelving on the W wall N of the walk-in
    sx0, sy0, sy1 = XW + 0.25, 8.95, 10.75
    for pi, (ox, py) in enumerate(((-0.22, sy0 + 0.02), (0.22, sy0 + 0.02), (-0.22, sy1 - 0.02), (0.22, sy1 - 0.02))):
        make_cyl(f"DryShelf_Post_{pi}", (sx0 + ox, py, 0.90), 0.012, 1.80, steel, segments=6)
    for zi, z in enumerate((0.25, 0.75, 1.25, 1.75)):
        make_box(f"DryShelf_{zi}", (sx0, (sy0 + sy1) / 2.0, z), (0.46, sy1 - sy0, 0.02), steel)
        for ci in range(5):
            cy_ = sy0 + 0.20 + ci * 0.34
            if zi == 0:
                make_box(f"Flour_Sack_{ci}", (sx0, cy_, z + 0.13), (0.36, 0.28, 0.24), (0.86, 0.82, 0.72, 1.0))
            elif zi == 3 and ci % 2:
                make_box(f"DryBox_{zi}_{ci}", (sx0, cy_, z + 0.12), (0.30, 0.26, 0.22), (0.66, 0.52, 0.34, 1.0))
            else:
                for k in range(2):
                    make_cyl(f"DryCan_{zi}_{ci}_{k}", (sx0 - 0.09 + k * 0.18, cy_, z + 0.10), 0.08, 0.18,
                             P.SNACK_TINTS[(zi + ci + k) % len(P.SNACK_TINTS)], segments=8)
    # speed rack of sheet pans in the NW corner, by the window
    rkx, rky = -4.20, KN - 0.34
    for pi, (ox, oy) in enumerate(((-0.25, -0.31), (0.25, -0.31), (-0.25, 0.31), (0.25, 0.31))):
        make_cyl(f"SpeedRack_Post_{pi}", (rkx + ox, rky + oy, 0.87), 0.012, 1.74, steel, segments=6)
    for k in range(9):
        make_box(f"SpeedRack_Pan_{k}", (rkx, rky, 0.30 + k * 0.16), (0.46, 0.64, 0.02), (0.70, 0.66, 0.58, 1.0) if k % 3 else steel)
    # ── mid-kitchen: the plating island ──
    ix, iy = 0.65, 8.30
    make_box("Prep_Top", (ix, iy, 0.925), (2.5, 0.76, 0.05), steel)
    make_box("Prep_Undershelf", (ix, iy, 0.25), (2.36, 0.62, 0.03), steel_dk)
    for li, (ox, oy) in enumerate(((-1.20, -0.33), (1.20, -0.33), (-1.20, 0.33), (1.20, 0.33))):
        make_box(f"Prep_Leg_{li}", (ix + ox, iy + oy, 0.45), (0.04, 0.04, 0.90), steel)
    for si, ox in enumerate((0.85, 1.05)):
        make_cyl(f"Prep_Plates_{si}", (ix + ox, iy + 0.12, 1.00), 0.13, 0.10, (0.92, 0.90, 0.86, 1.0), segments=14)
    for bi, (ox, col) in enumerate(((-0.95, (0.74, 0.14, 0.10, 1.0)), (-0.87, (0.90, 0.72, 0.16, 1.0)), (-0.79, (0.94, 0.92, 0.88, 1.0)))):
        make_cyl(f"Prep_Squeeze_{bi}", (ix + ox, iy + 0.25, 1.04), 0.03, 0.18, col, segments=8)
    make_box("Prep_CuttingBoard", (ix - 0.35, iy - 0.05, 0.96), (0.45, 0.32, 0.02), (0.92, 0.92, 0.88, 1.0))
    make_cyl("Prep_Tomato", (ix - 0.30, iy - 0.02, 0.995), 0.04, 0.05, (0.80, 0.22, 0.16, 1.0), segments=8)
    make_cyl("Prep_Wrap_Roll", (ix + 0.30, iy + 0.25, 0.995), 0.04, 0.46, (0.80, 0.84, 0.86, 1.0), segments=8, axis='X')
    for k in range(3):
        make_box(f"Prep_Undershelf_Box_{k}", (ix - 0.8 + k * 0.6, iy, 0.33), (0.40, 0.50, 0.14), (0.66, 0.54, 0.38, 1.0))
    # ── the pass, kitchen side: plating counter, heat lamp, an order up ──
    make_box("Pass_Counter_K", (0.7, KS + 0.35, 0.44), (2.6, 0.70, 0.88), steel)
    make_box("Pass_Counter_K_Top", (0.7, KS + 0.35, 0.89), (2.62, 0.72, 0.02), steel)
    for pi, px in enumerate((0.15, 0.55)):
        make_cyl(f"Pass_Plate_{pi}", (px, KS + 0.30, 0.906), 0.13, 0.012, (0.94, 0.92, 0.88, 1.0), segments=14)
        make_cyl(f"Pass_Plate_{pi}_Burger", (px - 0.03, KS + 0.30, 0.935), 0.065, 0.045, (0.72, 0.50, 0.28, 1.0), segments=10)
        make_box(f"Pass_Plate_{pi}_Fries", (px + 0.07, KS + 0.33, 0.925), (0.08, 0.10, 0.025), (0.90, 0.74, 0.34, 1.0))
    make_box("Pass_HeatLamp", (0.7, KS + 0.10, 1.90), (2.4, 0.20, 0.09), steel_dk)
    make_box("Pass_HeatLamp_Glow", (0.7, KS + 0.10, 1.852), (2.2, 0.14, 0.006), (1.0, 0.48, 0.22, 1.0))
    for bi, bx_ in enumerate((-0.4, 1.8)):
        make_box(f"Pass_HeatLamp_Bracket_{bi}", (bx_, KS + 0.05, 1.97), (0.03, 0.10, 0.06), steel_dk)
    # ── E side: the BACK OFFICE door (vol6_ch4), the dish pit past it ──
    make_box("Office_Door", (ROOM_W/2.0-0.12, 7.4, 1.05), (0.06, 0.95, 2.10), (0.48, 0.38, 0.28, 1.0))
    make_box("Office_Door_Frame", (ROOM_W/2.0-0.10, 7.4, 2.16), (0.08, 1.10, 0.10), COL_WOOD)
    make_cyl("Office_Door_Knob", (ROOM_W/2.0-0.16, 7.05, 1.05), 0.035, 0.04, (0.72, 0.66, 0.40, 1.0), segments=8)
    dy0, dy1 = 8.30, 10.50
    dyc = (dy0 + dy1) / 2.0
    make_box("Dish_Sink_Body", (XE - 0.35, dyc, 0.42), (0.70, dy1 - dy0, 0.84), steel)
    make_box("Dish_Sink_Top", (XE - 0.36, dyc, 0.855), (0.72, dy1 - dy0 + 0.04, 0.03), steel)
    for bi, by_ in enumerate((9.05, 9.55, 10.05)):
        make_box(f"Dish_Sink_Basin_{bi}", (XE - 0.36, by_, 0.873), (0.50, 0.44, 0.006), (0.40, 0.46, 0.50, 1.0))
        make_cyl(f"Dish_Sink_Faucet_{bi}", (XE - 0.03, by_, 1.05), 0.015, 0.36, steel, segments=6)
        make_box(f"Dish_Sink_Spout_{bi}", (XE - 0.14, by_, 1.22), (0.22, 0.025, 0.025), steel)
    make_box("Dish_Backsplash", (XE - 0.015, dyc, 1.085), (0.01, dy1 - dy0 + 0.04, 0.43), steel)
    make_cyl("Dish_Sprayer_Riser", (XE - 0.08, 10.30, 1.32), 0.015, 0.92, steel, segments=6)
    make_tube("Dish_Sprayer_Hose", [(XE - 0.08, 10.30, 1.78), (XE - 0.30, 10.30, 1.70), (XE - 0.36, 10.30, 1.20)], 0.012, knob, segments=5)
    make_box("Dish_Shelf", (XE - 0.20, dyc, 1.75), (0.40, 2.0, 0.03), steel)
    for bi, by_ in enumerate((dyc - 0.70, dyc + 0.70)):
        make_box(f"Dish_Shelf_Bracket_{bi}", (XE - 0.12, by_, 1.66), (0.24, 0.03, 0.15), steel_dk)
    for ri, by_ in enumerate((8.80, 9.40, 10.00)):
        make_box(f"Dish_Rack_{ri}", (XE - 0.20, by_, 1.815), (0.38, 0.50, 0.10), (0.30, 0.40, 0.56, 1.0))
    make_box("Bus_Tub", (XE - 0.36, 8.55, 0.93), (0.40, 0.30, 0.12), (0.44, 0.44, 0.46, 1.0))
    make_box("Bus_Tub_Dishes", (XE - 0.36, 8.55, 1.0), (0.32, 0.22, 0.02), (0.90, 0.88, 0.84, 1.0))
    make_box("Floor_Drain", (XE - 0.95, dyc, 0.011), (0.25, 0.25, 0.004), (0.20, 0.20, 0.20, 1.0))
    make_trash_can("Trash_K", (3.15, 8.60, 0.0), branded=False, palette={"body": (0.30, 0.34, 0.30, 1.0)})
    # paper goods shelving on the N wall's E end; the K-class extinguisher
    px0, px1 = 3.25, 4.65
    for pi, (ox, oy) in enumerate(((px0 + 0.02, -0.20), (px1 - 0.02, -0.20), (px0 + 0.02, 0.20), (px1 - 0.02, 0.20))):
        make_cyl(f"Paper_Shelf_Post_{pi}", (ox, KN - 0.225 + oy, 0.90), 0.012, 1.80, steel, segments=6)
    for zi, z in enumerate((0.30, 0.85, 1.40)):
        make_box(f"Paper_Shelf_{zi}", ((px0 + px1) / 2.0, KN - 0.225, z), (px1 - px0, 0.44, 0.02), steel)
        for ci in range(3):
            make_box(f"Paper_Goods_{zi}_{ci}", (px0 + 0.25 + ci * 0.45, KN - 0.225, z + 0.13),
                     (0.36, 0.34, 0.24), ((0.86, 0.84, 0.78, 1.0), (0.62, 0.48, 0.32, 1.0), (0.80, 0.80, 0.82, 1.0))[(zi + ci) % 3])
    make_fire_extinguisher("Extinguisher_K", (2.45, KS + 0.11, 0.30), palette={"red": (0.70, 0.72, 0.74, 1.0)})


def build_decor():
    make_wall_clock("Clock", (-2.0, 5.900, CEIL-0.55), frozen_hour=9, frozen_min=18, facing='-Y')
    make_calendar("Calendar_Kitchen", (ROOM_W/2.0-0.11, 8.10, 1.50), axis='Y')   # E wall by the office door (2026-10-09: the hood took the N wall)
    make_faded_poster("Poster_E", (ROOM_W/2.0-0.05 - 0.0535, 2.6, 1.60), into_room=-1)
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
    for j, (fx_, fy_) in enumerate([(-2.6, 7.4), (1.8, 7.4), (-2.6, 9.1), (4.2, 9.4)]):
        make_fluorescent_tube_fixture(f"Fluor_K{j}", (fx_, fy_, CEIL), length=1.60, width=0.36)
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
    make_traffic_wear("Wear_Kitchen", [(3.65, 7.0), (3.65, 7.45), (-1.6, 7.45), (-1.6, 9.0)],
                      width=0.8, floor_z=0.010, tint=(0.44, 0.27, 0.20, 1.0))
    # Stains: grill grease shadow, fryer drips, counter coffee ring.
    make_floor_stain("Stain_Grill", (-0.5, 9.75), radius=0.55, floor_z=0.021,
                     tint=(0.20, 0.18, 0.16, 1.0))
    make_floor_stain("Stain_Fryer", (0.85, 9.80), radius=0.30, floor_z=0.021,
                     tint=(0.24, 0.20, 0.14, 1.0))
    make_floor_stain("Stain_Counter", (1.2, 3.75), radius=0.28, tint=wear)
    # Kick scuffs: counter customer face + swing door + booth bases.
    make_scuff_band("Scuff_Counter", (1.4, 4.169), length=5.6, axis='X',   # on the front, from the floor (2026-09-23: 6 cm off it, 4 cm up)
                    band_z=0.08, tint=scuff)
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
    make_wall_outlet("Outlet_Kitchen", (ROOM_W/2.0, 8.12), axis='Y', face_sign=-1, aged=True, z=1.10)
    make_thermostat("Thermostat", (2.2, PART_Y), axis='X', face_sign=-1)
    # Cords: register + coffee station reach real outlets.
    make_cord_run("Cord_Register", (4.0, 4.85, 0.90), (4.55, 5.45, 0.12))
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
    make_cyl("Counter_Coffee_Ring", (2.55, 4.36, 1.0121), 0.05, 0.003, (0.66, 0.60, 0.52, 1.0), segments=8)
    # The grill mid-order: two patties, the spatula resting on the
    # flat-top edge, a side towel over the hood bar.
    for pi, pxo in enumerate([-0.25, 0.05]):
        make_cyl(f"Grill_Patty_{pi}", (-0.6+pxo, 10.45, 1.01), 0.07, 0.02, (0.36, 0.22, 0.14, 1.0), segments=10)
    make_box("Grill_Spatula_Blade", (0.0, 10.30, 1.005), (0.09, 0.11, 0.008), P.METAL_STEEL)
    make_box("Grill_Spatula_Handle", (0.0, 10.15, 1.008), (0.03, 0.22, 0.02), (0.20, 0.20, 0.22, 1.0))   # into the blade, over the trough
    make_box("Hood_Towel", (2.4, 9.835, 1.86), (0.30, 0.03, 0.26), (0.80, 0.80, 0.76, 1.0))   # over the hood's front lip
    # Ticket on the pass-through rail mid-order (one more than the
    # static three — this one's crooked).
    make_box("Pass_Ticket_Live", (1.05, PART_Y-0.10, 1.82), (0.13, 0.005, 0.15), (0.96, 0.94, 0.86, 1.0))   # in the rail
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
    make_box("Milk_Crate_2", (-3.30, 6.245, 0.50), (0.35, 0.35, 0.33), (0.24, 0.36, 0.62, 1.0))   # stacked on the first, which moved (2026-09-25)
    # Swing-door wedge kicked half under the door.
    make_box("Swing_Door_Wedge", (3.35, PART_Y-0.18, 0.03), (0.10, 0.14, 0.06), (0.52, 0.40, 0.28, 1.0))


def build_beyond_glass_2026_08():
    """D5 · something through every window. W + N glass show the
    PARKING LOT — including the Louisiana pickup that sits in the
    Pit Stop lot with a driver who never enters (Ben's list, item
    2, vol6_ch3). S glass shows the road + the strip across it.
    Cheap silhouette band geometry; fog and glass do the rest."""
    # ── The lot, west of the building (out the booth windows) ──
    make_box("Lot_Asphalt_W", (-9.5, 8.05, -0.02), (7.6, 18.1, 0.04), (0.30, 0.30, 0.32, 1.0))
    for si, sy in enumerate([2.0, 4.4, 6.8]):
        make_box(f"Lot_Stripe_W_{si}", (-7.2, sy, 0.005), (0.10, 1.8, 0.01), (0.86, 0.84, 0.78, 1.0))
    # Two parked cars + THE LOUISIANA PICKUP (nose-in, engine cold,
    # driver never enters) framed by the W_Mid booth window.
    for tag, cy2, col in [("A", 1.9, (0.32, 0.34, 0.40, 1.0)), ("B", 6.6, (0.62, 0.60, 0.56, 1.0))]:
        make_box(f"Lot_Car_{tag}_Body", (-7.72, cy2, 0.55), (4.2, 1.75, 0.55), col)   # clear of the wall (2026-09-23: 10 cm into it)
        make_box(f"Lot_Car_{tag}_Cabin", (-8.02, cy2, 1.02), (2.2, 1.6, 0.45), col)
        for wx_ in (-9.22, -6.22):   # wheels (2026-09-23: the wall had been holding the cars up)
            for wy_ in (-0.70, 0.70):
                make_cyl(f"Lot_Car_{tag}_Wheel_{wx_:.1f}_{wy_:+.1f}", (wx_, cy2 + wy_, 0.30), 0.30, 0.24, (0.10, 0.10, 0.11, 1.0), axis='Y', segments=10)
    # "a black pickup with Louisiana plates" (vol6_ch2) — it was brown
    make_box("Lot_LA_Pickup_Body", (-8.1, 4.35, 0.62), (4.8, 1.85, 0.70), (0.10, 0.10, 0.11, 1.0))
    make_box("Lot_LA_Pickup_Cab", (-9.1, 4.35, 1.25), (1.8, 1.75, 0.55), (0.10, 0.10, 0.11, 1.0))
    make_box("Lot_LA_Pickup_Bed_Rim", (-6.9, 4.35, 1.02), (2.3, 1.85, 0.08), (0.07, 0.07, 0.08, 1.0))
    for wx_ in (-9.8, -6.4):   # the pickup had no wheels — it hung 27 cm over the lot (2026-09-23)
        for wy_ in (3.55, 5.15):
            make_cyl(f"Lot_LA_Pickup_Wheel_{wx_:.1f}_{wy_:.2f}", (wx_, wy_, 0.32), 0.32, 0.26, (0.10, 0.10, 0.11, 1.0), axis='Y', segments=10)
    # Lot light pole + far treeline wall (edge-of-set).
    make_cyl("Lot_Pole", (-11.5, 4.5, 3.0), 0.09, 6.0, (0.40, 0.40, 0.42, 1.0), segments=8)
    make_box("Lot_Pole_Head", (-11.2, 4.5, 6.0), (0.7, 0.25, 0.18), (0.30, 0.30, 0.32, 1.0))
    # (2026-10-07: the windows are cut — a 4.4 m slab at 8 m filled them;
    # a field past the lot and a low treeline far enough back for sky)
    make_box("Lot_Field_W", (-23.95, 10.5, -0.03), (21.1, 52.0, 0.04), (0.36, 0.40, 0.26, 1.0))
    make_box("Lot_Treeline_W", (-34.6, 10.5, 1.0), (0.6, 52.0, 2.0), (0.22, 0.28, 0.19, 1.0))
    # ── North strip (out the kitchen window): the lot corner Ben
    # catalogues + the same treeline running behind ──
    # (2026-10-09: the building runs 2 m further N; the back lot with it)
    make_box("Lot_Asphalt_N", (0.65, ROOM_D + 3.1, -0.02), (12.7, 6.0, 0.04), (0.30, 0.30, 0.32, 1.0))
    make_box("Lot_Field_N", (-0.15, ROOM_D + 15.1, -0.03), (26.5, 18.0, 0.04), (0.36, 0.40, 0.26, 1.0))
    make_box("Lot_Treeline_N", (-2.0, ROOM_D + 24.3, 1.0), (30.0, 0.6, 2.0), (0.22, 0.28, 0.19, 1.0))
    # "Dumpster at two-fifteen": the enclosure out back, framed by Ben's window
    dmx, dmy = -1.0, ROOM_D + 3.0
    make_box("Lot_Dumpster_Body", (dmx, dmy, 0.65), (1.9, 1.1, 1.3), (0.22, 0.36, 0.26, 1.0))
    make_box("Lot_Dumpster_Lid", (dmx, dmy, 1.33), (1.95, 1.15, 0.06), (0.12, 0.12, 0.12, 1.0))
    make_box("Lot_Enclosure_N", (dmx, dmy + 0.85, 0.9), (3.0, 0.2, 1.8), (0.60, 0.58, 0.54, 1.0))
    for nm, ox in (("W", -1.40), ("E", 1.40)):
        make_box(f"Lot_Enclosure_{nm}", (dmx + ox, dmy + 0.10, 0.9), (0.2, 1.3, 1.8), (0.60, 0.58, 0.54, 1.0))
    make_box("Lot_Pallet", (dmx + 2.2, dmy + 0.3, 0.07), (1.2, 1.0, 0.14), (0.58, 0.46, 0.30, 1.0))
    # a sedan nose-in to the back wall, the NexCorp van's empty bay beside it
    cx_, cy_ = -6.6, ROOM_D + 3.6
    make_box("Lot_Car_C_Body", (cx_, cy_, 0.55), (1.75, 4.2, 0.55), (0.56, 0.54, 0.50, 1.0))
    make_box("Lot_Car_C_Cabin", (cx_, cy_ + 0.30, 1.02), (1.6, 2.2, 0.45), (0.56, 0.54, 0.50, 1.0))
    for wx_ in (-0.80, 0.80):
        for wy_ in (-1.45, 1.45):
            make_cyl(f"Lot_Car_C_Wheel_{wx_:+.1f}_{wy_:+.1f}", (cx_ + wx_, cy_ + wy_, 0.30), 0.30, 0.24, (0.10, 0.10, 0.11, 1.0), axis='X', segments=10)
    for si, sx_ in enumerate((-7.8, -5.4, 2.2)):
        make_box(f"Lot_Stripe_N_{si}", (sx_, ROOM_D + 3.4, 0.005), (0.10, 4.4, 0.01), (0.86, 0.84, 0.78, 1.0))
    # ── South: the state-highway strip + the building across it ──
    make_box("Road_S", (0.0, -3.2, -0.02), (16.0, 3.0, 0.04), (0.26, 0.26, 0.28, 1.0))
    make_box("Road_S_Centerline", (0.0, -3.2, 0.005), (14.0, 0.10, 0.01), (0.85, 0.76, 0.30, 1.0))
    make_box("Strip_Across", (1.5, -6.4, 1.7), (10.0, 0.8, 3.4), (0.42, 0.38, 0.34, 1.0))
    make_box("Strip_Across_Sign", (-2.0, -5.94, 3.0), (1.6, 0.12, 0.7), (0.66, 0.58, 0.42, 1.0))   # on the facade (2026-09-23: 4 cm off it)


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    The pit_stop_kitchen preset fires five distinct cues; grill and
    the kitchen window existed (markers only). Built here:

    - THE DINER DOOR + BELL ("the bell over the diner door
      chimes"): the centred entry gap had NO DOOR — a glass diner
      door now fills it (stiles, rails, glass, push bar) with the
      brass bell on a bracket at the transom, inside.
    - THE TEN ("Ben ... picks up the ten-dollar bill. On the back
      of it, in pencil: The red light lies. I am sorry. I will
      come back when I can."): flat on the lunch counter where the
      stranger left it, one faint pencil line showing.
    - BEN'S PHONE ("The phone, at 09:18, buzzes."): face-up on the
      prep line.

    Draft note: draft N+1 could swing the door ajar the day the
    pipeline gets rotation, and give the bell its leather strap.
    """
    steel = COL_STEEL
    door_al = (0.55, 0.57, 0.60, 1.0)
    glass = (0.62, 0.72, 0.76, 0.45)
    brass = (0.72, 0.58, 0.28, 1.0)
    # ── THE DINER DOOR · centred gap, south wall ──
    for sgn in (-1, 1):
        make_box(f"Diner_Door_Stile_{'L' if sgn < 0 else 'R'}",
                 (0.42 * sgn, 0.06, 1.02), (0.05, 0.05, 2.04), door_al)
    make_box("Diner_Door_Rail_T", (0.0, 0.06, 2.01), (0.79, 0.05, 0.06), door_al)
    make_box("Diner_Door_Rail_B", (0.0, 0.06, 0.14), (0.79, 0.05, 0.20), door_al)
    make_box("Diner_Door_Glass", (0.0, 0.06, 1.11), (0.79, 0.02, 1.74), glass)
    make_box("Diner_Door_PushBar", (0.0, 0.085, 1.05), (0.70, 0.030, 0.050), steel)
    # The bell over the door, on its bracket at the transom
    make_box("Door_Bell_Bracket", (0.30, 0.14, 2.45), (0.030, 0.080, 0.030), door_al)
    make_cyl("Door_Bell", (0.30, 0.18, 2.41), 0.035, 0.050, brass, segments=8)
    make_cyl("Door_Bell_Clapper", (0.30, 0.18, 2.375), 0.008, 0.020,
             (0.30, 0.26, 0.20, 1.0), segments=6)
    # ── THE TEN · flat on the lunch counter (top 1.005) ──
    make_box("Ten_Dollar_Bill", (1.7, 4.45, 1.0113), (0.156, 0.066, 0.0015),
             (0.66, 0.66, 0.58, 1.0))
    make_box("Bill_Pencil_Line", (1.7, 4.45, 1.0109), (0.100, 0.008, 0.0005),
             (0.38, 0.37, 0.36, 1.0))
    # ── BEN'S PHONE · on the prep line (top 0.95) ──
    make_box("Bens_Phone", (1.15, 8.12, 0.9555), (0.070, 0.140, 0.011),
             (0.13, 0.13, 0.15, 1.0))


def build_prints_2026_09():
    """THE PRINTS ("Jesse opens the paper bag. He takes out three
    eight-by-tens. He hands them to Ben.") — the bag and the three
    prints fanned on the lunch counter west of the card terminal."""
    for pi, (dx, dy) in enumerate(((0.0, 0.0), (0.035, 0.02), (0.07, 0.04))):
        make_box(f"Print_8x10_{pi}", (2.80 + dx, 4.52 + dy, 1.0118 + pi * 0.0015), (0.20, 0.25, 0.0015), (0.30, 0.30, 0.32, 1.0))   # on the lunch table's top (2026-09-25: 5 mm inside it)
    make_box("Prints_Paper_Bag", (2.95, 4.82, 1.115), (0.16, 0.10, 0.22), (0.72, 0.60, 0.42, 1.0))


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
    build_hero_props_2026_09()
    build_prints_2026_09()
    # what is outside the window (2026-10-07, _props/views.py)
    make_view("View_S", "S", 0.0, 0.0, kind="street", ground_z=0.0, seed=12)   # the road past the front lot
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pit_stop_interior.glb"))
    print(f"\n[build_pit_stop_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
