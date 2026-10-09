"""Centro Grocery — break room — vol6 placement script.

DRAFT 3 (2026-10-09, the overnight run; CLAUDE.md "build big"). The night
crew's break room (vol6 ch18/ch22): "The team is in the break room.
Marisol is at the table with her thermos. Russell is at the table with
the morning Express-News. Doug is at the chair with Karamazov on his
lap"; "Doug is in his standard break-room position — the chair against
the back wall, thermos at his feet"; "The radio above the microwave";
"BT is at the doorway ... The team listens to BT's footsteps cross the
break-room corridor, hit the dock, push the dock door open". The room
was 5.6 x 4.6 with TWO tables built on top of each other (the round
pedestal table the hero pass had meant to replace, and the card table
that replaced it) and the dock door in the break room's own wall. Now
7.2 x 5.6: one folding crew table for six with mismatched chairs,
DOUG'S CHAIR against the back (N) wall, lockers and the time clock, the
doorway standing open on the corridor with the dock door at its far
end, the radio keyed to the microwave.
Draft 4 targets: the crew's things on the lockers (names on tape); the
corridor's dock door lit by the dock's sodium lamp through its wire
glass; Deck framing.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.furniture import make_chair
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, make_lathe, make_tube, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_case_shell
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 7.2; ROOM_D = 5.6; CEIL = 2.6   # draft 3 (2026-10-09): was 5.6 x 4.6   # 2026-09-25: 5.0 × 4.0 read cramped on the sheet (the user: "rooms too cramped")
PAL_WALL = {"wall": (0.74, 0.74, 0.70, 1.0), "baseboard": (0.32, 0.30, 0.28, 1.0)}
COL_FLOOR = (0.62, 0.58, 0.52, 1.0); COL_SEAM = (0.32, 0.30, 0.28, 1.0); COL_WOOD = (0.42, 0.32, 0.22, 1.0)
COL_ACCENT = (0.86, 0.62, 0.28, 1.0)
DOORWAY = (0.6, 1.05, 0.96, 2.10)       # to the corridor (and the dock beyond it)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    from _props.structure import make_wall_with_openings
    make_wall_with_openings("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL,
                            baseboard_face_sign=+1, openings=[DOORWAY])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_table_OLD_round():
    """(draft 3: retired — the hero pass built a card table over it)"""
    tx, ty = 0.0, ROOM_D/2.0
    make_cyl("Table_Top", (tx, ty, 0.74), 0.40, 0.04, COL_WOOD)
    make_lathe("Table_Pedestal", (tx, ty, 0.0), [(0.22, 0.0), (0.20, 0.03), (0.07, 0.06), (0.05, 0.40), (0.06, 0.62), (0.10, 0.70), (0.12, 0.72)], P.METAL_BLACK, segments=12)
    import math
    for ci in range(4):
        ang = ci * 1.57
        cx, cy = tx + math.cos(ang)*0.85, ty + math.sin(ang)*0.85
        make_chair(f"Chair_{ci}", cx, cy, yaw=ang + 1.5708, wood=P.METAL_BLACK, seat_col=COL_WOOD, w=0.38)

def build_vending():
    vx, vy = +ROOM_W/2.0-0.30, ROOM_D-1.0
    # an open shell with a shelf under each row, glints for the glass
    # (2026-09-24: a solid body with the snacks inside it, behind a glass
    # slab that renders opaque — no alpha in this pipeline)
    make_case_shell("Vending_Body", (vx, vy, 1.00), (0.50, 0.70, 2.00), COL_ACCENT, open_face='-X')
    for gi, (gy, gw) in enumerate(((-0.20, 0.02), (-0.13, 0.01))):
        make_box(f"Vending_Glint_{gi}", (vx-0.248, vy+gy, 1.00), (0.004, gw, 1.96), (0.86, 0.90, 0.92, 1.0))
    for r in range(4):
        make_box(f"Vending_Shelf_{r}", (vx-0.0075, vy, 0.60+r*0.30), (0.475, 0.66, 0.02), P.METAL_STEEL)
        for c in range(5):
            make_box(f"Vending_Snack_{r}_{c}", (vx-0.22, vy-0.28+c*0.14, 0.70+r*0.30), (0.04, 0.10, 0.18), P.SNACK_TINTS[(r+c)%len(P.SNACK_TINTS)])

def build_kitchenette():
    """Galley counter along the W wall: sink + faucet, a compound
    microwave, a drip coffee station, and upper cabinets."""
    # (2026-09-23: the run stood 8 cm inside the W wall with every door,
    # pull and the fridge's doors on the wall side; it stands on the
    # wall face now and faces the room, +X)
    cx = -ROOM_W/2.0 + 0.36
    cy0 = ROOM_D/2.0
    # Counter carcass + top
    make_box("Counter_Body", (cx, cy0, 0.45), (0.52, 2.60, 0.90), COL_WOOD)
    make_box("Counter_Top", (cx + 0.02, cy0, 0.92), (0.56, 2.64, 0.05), P.METAL_STEEL)
    make_box("Counter_Kick", (cx, cy0, 0.05), (0.44, 2.56, 0.10), (0.20, 0.16, 0.12, 1.0))
    # Cabinet doors under the counter
    for di, dy in enumerate([cy0-0.85, cy0-0.28, cy0+0.30, cy0+0.88]):
        make_box(f"Counter_Door_{di}", (cx+0.27, dy, 0.46), (0.02, 0.50, 0.72), (0.36, 0.28, 0.18, 1.0))
        make_box(f"Counter_Pull_{di}", (cx+0.29, dy+0.20, 0.46), (0.02, 0.03, 0.12), P.METAL_BLACK)
    # Sink basin (recessed dark box + rim) at the S third
    sy = cy0 - 0.80
    make_box("Sink_Rim", (cx, sy, 0.93), (0.42, 0.44, 0.03), P.METAL_STEEL)
    make_box("Sink_Basin", (cx, sy, 0.86), (0.34, 0.36, 0.14), (0.30, 0.32, 0.34, 1.0))
    # Faucet (riser + gooseneck spout)
    make_cyl("Faucet_Riser", (cx+0.10, sy+0.16, 1.02), 0.02, 0.18, P.METAL_STEEL, segments=8, axis='Z')
    # out of the riser's top over the basin (2026-09-23: 8 cm clear of the riser)
    make_cyl("Faucet_Spout", (cx+0.01, sy+0.16, 1.12), 0.018, 0.20, P.METAL_STEEL, segments=8, axis='X')
    make_box("Faucet_Handle", (cx+0.14, sy+0.16, 1.04), (0.04, 0.10, 0.03), P.METAL_STEEL)
    # Compound microwave at the N third of the counter
    my = cy0 + 0.85
    make_box("Microwave_Body", (cx, my, 1.10), (0.48, 0.44, 0.30), (0.30, 0.30, 0.32, 1.0))
    # door, window, panel and handle on the room face (2026-09-23: on the
    # S side, facing down the counter)
    make_box("Microwave_Door", (cx+0.25, my-0.06, 1.10), (0.02, 0.30, 0.26), (0.18, 0.18, 0.20, 1.0))
    make_box("Microwave_Window", (cx+0.265, my-0.08, 1.10), (0.01, 0.20, 0.18), (0.10, 0.14, 0.12, 0.7))
    make_box("Microwave_Panel", (cx+0.25, my+0.16, 1.10), (0.02, 0.10, 0.24), (0.14, 0.14, 0.16, 1.0))
    make_box("Microwave_Handle", (cx+0.27, my+0.10, 1.10), (0.02, 0.02, 0.22), P.METAL_STEEL)
    # Drip coffee station (make_coffee_pots was imported/unused)
    make_coffee_pots("Coffee", (cx, cy0+0.10, 0.94), pots=2)
    # Upper cabinets above the counter
    make_box("UpperCab_Body", (cx-0.04, cy0, 1.95), (0.44, 2.40, 0.60), (0.36, 0.28, 0.18, 1.0))   # on the wall
    for ui, uy in enumerate([cy0-0.60, cy0+0.60]):
        make_box(f"UpperCab_Door_{ui}", (cx+0.19, uy, 1.95), (0.02, 1.10, 0.56), (0.42, 0.32, 0.20, 1.0))
        make_box(f"UpperCab_Pull_{ui}", (cx+0.21, uy+0.45, 1.80), (0.02, 0.03, 0.12), P.METAL_BLACK)

def build_fridge():
    # Fridge in the NW corner
    # (2026-09-23: 16 cm into the N wall and 4 into the W, doors against
    # the W wall; in the corner now, between the counter's end and the
    # N wall, doors to the room)
    fx, fy = -ROOM_W/2.0 + 0.46, ROOM_D - 0.38
    make_box("Fridge_Body", (fx, fy, 0.95), (0.72, 0.56, 1.90), (0.82, 0.82, 0.80, 1.0))
    make_box("Fridge_DoorUpper", (fx+0.375, fy, 1.35), (0.03, 0.52, 1.02), (0.86, 0.86, 0.84, 1.0))
    make_box("Fridge_DoorLower", (fx+0.375, fy, 0.55), (0.03, 0.52, 0.66), (0.86, 0.86, 0.84, 1.0))
    make_box("Fridge_HandleU", (fx+0.405, fy+0.20, 1.35), (0.03, 0.04, 0.40), P.METAL_STEEL)
    make_box("Fridge_HandleL", (fx+0.405, fy+0.20, 0.55), (0.03, 0.04, 0.30), P.METAL_STEEL)
    make_box("Fridge_Kick", (fx, fy, 0.05), (0.68, 0.52, 0.10), (0.30, 0.30, 0.30, 1.0))
    # Magnets / a note on the door
    make_box("Fridge_Note", (fx+0.3925, fy-0.10, 1.45), (0.005, 0.16, 0.20), P.PAPER)

def build_board():
    # on the wall face (2026-09-23: board and notices inside the N wall)
    make_box("BulletinBoard", (0.0, ROOM_D-0.12, 1.50), (1.60, 0.04, 0.90), (0.62, 0.42, 0.28, 1.0))
    for pi in range(8):
        px = -0.60 + (pi%4)*0.40; pz = 1.20 + (pi//4)*0.50
        make_box(f"Notice_{pi}", (px, ROOM_D-0.1425, pz), (0.20, 0.005, 0.16), P.PAPER)

def build_break_decor():
    # Wall clock on the N wall beside the bulletin board
    make_wall_clock("Clock", (1.70, ROOM_D - 0.100, 2.10), frozen_hour=12, frozen_min=30, facing='-Y')   # on the N wall's face wherever it is (2026-09-25: literal 3.9 floated when the room grew)
    # Wall calendar on the E wall (make_calendar was imported/unused)
    make_calendar("Calendar", (ROOM_W/2.0-0.1025, 1.20, 1.60))
    # Corner floor plant (make_floor_plant was imported/unused)
    make_floor_plant("Plant", (ROOM_W/2.0-0.55, 0.60, 0.0))
    # Swing-lid trash bin by the counter
    tx, ty = -ROOM_W/2.0+1.25, 0.45   # east of the dishwasher (2026-09-25: at +0.95 the widened room put it inside the dishwasher)
    make_cyl("Trash_Body", (tx, ty, 0.34), 0.20, 0.68, (0.34, 0.36, 0.34, 1.0), segments=12, axis='Z')
    make_cyl("Trash_Rim", (tx, ty, 0.68), 0.21, 0.03, (0.24, 0.26, 0.24, 1.0), segments=12, axis='Z')
    make_box("Trash_SwingLid", (tx, ty, 0.71), (0.30, 0.30, 0.04), (0.28, 0.30, 0.28, 1.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_hero_props():
    """2026-08-03 hero-prop pass: DOUG'S CHAIR against the wall
    (thermos at its feet) — the most-staged object here — the
    Tejano radio above the microwave, Jessa's small dishwasher, the
    jacket hooks, the dock door leaf. Plus the table squared into
    the card table canon names."""
    wood = (0.46, 0.36, 0.26, 1.0)
    # Doug's chair "against the back wall", facing the table, thermos at its feet
    make_chair("Dougs_Chair", DOUG_X, ROOM_D - 0.42, yaw=3.1416, wood=wood, seat_col=(0.40, 0.36, 0.30, 1.0), w=0.42)
    make_cyl("Dougs_Thermos", (DOUG_X - 0.32, ROOM_D - 0.40, 0.13), 0.05, 0.26, (0.30, 0.42, 0.30, 1.0), segments=10)
    # Radio above the microwave (the Tejano station since 2019) — on a
    # bracket shelf over it (draft 3: keyed to the microwave)
    rcx, rmy = -ROOM_W/2.0 + 0.36, ROOM_D/2.0 + 0.85
    make_box("Break_Radio_Shelf", (rcx - 0.10, rmy, 1.42), (0.30, 0.40, 0.025), (0.36, 0.28, 0.18, 1.0))
    make_box("Break_Radio_Shelf_Bracket", (-ROOM_W/2.0 + 0.11, rmy, 1.36), (0.02, 0.06, 0.10), P.METAL_BLACK)
    make_box("Break_Radio", (rcx - 0.10, rmy, 1.50), (0.13, 0.24, 0.13), (0.36, 0.30, 0.26, 1.0))
    make_cyl("Break_Radio_Dial", (rcx - 0.03, rmy + 0.06, 1.50), 0.028, 0.02, (0.86, 0.82, 0.72, 1.0), axis='X', segments=8)
    make_tube("Break_Radio_Antenna", [(rcx - 0.12, rmy - 0.10, 1.565), (rcx - 0.12, rmy - 0.42, 1.62)], 0.004, (0.70, 0.70, 0.68, 1.0), segments=4)
    # Jessa's small dishwasher, under-counter
    # at the counter's S end, against the walls (2026-09-23: half inside
    # the counter carcass and 8 cm into the W wall)
    make_box("Small_Dishwasher", (-ROOM_W/2.0+0.66, 0.39, 0.44), (0.52, 0.58, 0.85), (0.78, 0.76, 0.72, 1.0))
    make_box("Dishwasher_Handle", (-ROOM_W/2.0+0.935, 0.39, 0.78), (0.03, 0.42, 0.04), (0.55, 0.57, 0.58, 1.0))
    # Jacket hooks by the doorway (E of it)
    for hi, hx in enumerate((1.55, 1.80, 2.05)):
        make_cyl(f"Jacket_Hook_{hi}", (hx, 0.10, 1.70), 0.015, 0.06, (0.20, 0.19, 0.20, 1.0), axis='Y', segments=6)
    make_box("Hung_Jacket", (1.80, 0.16, 1.34), (0.18, 0.10, 0.68), (0.30, 0.34, 0.40, 1.0))


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Three distinct cues; Dougs_Chair and his floor thermos exist.
    Built:

    - THE KARAMAZOV ("Doug closes the Karamazov. He sets it on the
      floor beside his chair."): the brick of a paperback on the
      floor by the chair's east side, spine band showing.
    - THE HORCHATA ("Diego sets the medium horchata on the table
      in front of Doug"): cream cup + lid + straw at the table's
      Doug-facing edge.
    - DOUG'S COFFEE ("He drinks the last of it. He puts the cup
      down."): the cup on the table — the marker sits close so it
      wins the coffee cue over the kitchenette pots.
    """
    kx_ = DOUG_X + 0.35
    make_box("Karamazov_Paperback", (kx_, ROOM_D - 0.45, 0.020), (0.190, 0.130, 0.040),
             (0.36, 0.28, 0.22, 1.0))
    make_box("Paperback_Spine_Band", (kx_, ROOM_D - 0.512, 0.020), (0.190, 0.006, 0.034),
             (0.74, 0.62, 0.30, 1.0))
    T = TABLE_Z
    make_cyl("Horchata_Cup", (TABLE_X + 0.55, TABLE_Y + 0.22, T + 0.065), 0.042, 0.130,
             (0.90, 0.86, 0.76, 0.95), segments=10)
    make_cyl("Horchata_Lid", (TABLE_X + 0.55, TABLE_Y + 0.22, T + 0.14), 0.044, 0.020,
             (0.86, 0.84, 0.80, 1.0), segments=10)
    make_cyl("Horchata_Straw", (TABLE_X + 0.56, TABLE_Y + 0.21, T + 0.20), 0.005, 0.100,
             (0.86, 0.36, 0.30, 1.0), segments=6)
    make_cyl("Dougs_Coffee_Cup", (TABLE_X + 0.70, TABLE_Y + 0.26, T + 0.04), 0.040, 0.080,
             (0.82, 0.80, 0.76, 1.0), segments=10)



TABLE_X, TABLE_Y, TABLE_Z = 0.20, 2.70, 0.74
DOUG_X = 2.20


def build_crew_table():
    """One folding crew table for six (Marisol, Russell, Diego, the rest),
    the chairs mismatched: kit chairs and two plastic stackers."""
    import math
    tx, ty, tz = TABLE_X, TABLE_Y, TABLE_Z
    make_box("Crew_Table_Top", (tx, ty, tz - 0.0175), (1.83, 0.76, 0.035), (0.86, 0.84, 0.78, 1.0))
    make_box("Crew_Table_Edge", (tx, ty, tz - 0.045), (1.85, 0.78, 0.02), (0.30, 0.30, 0.32, 1.0))
    for li, (ox, oy) in enumerate(((-0.82, -0.32), (0.82, -0.32), (-0.82, 0.32), (0.82, 0.32))):
        make_box(f"Crew_Table_Leg_{li}", (tx + ox, ty + oy, (tz - 0.055) / 2.0), (0.03, 0.03, tz - 0.055), (0.40, 0.42, 0.44, 1.0))
    for si, ox in enumerate((-0.82, 0.82)):
        make_box(f"Crew_Table_Stretcher_{si}", (tx + ox, ty, 0.12), (0.025, 0.60, 0.025), (0.40, 0.42, 0.44, 1.0))
    seats = [(-0.55, -0.70, 0.0, "kit"), (0.15, -0.70, 0.0, "plastic"), (0.70, -0.70, 0.0, "kit"),
             (-0.55, 0.70, math.pi, "plastic"), (0.15, 0.70, math.pi, "kit"), (-1.30, 0.0, -math.pi / 2.0, "kit")]
    for ci, (ox, oy, yaw, kind) in enumerate(seats):
        if kind == "kit":
            make_chair(f"Crew_Chair_{ci}", tx + ox, ty + oy, yaw=yaw, wood=P.METAL_BLACK, seat_col=COL_WOOD, w=0.40)
        else:
            col = (0.24, 0.40, 0.52, 1.0) if ci % 2 else (0.70, 0.66, 0.58, 1.0)
            cx, cy = tx + ox, ty + oy
            s = 1 if yaw == 0.0 else -1
            make_box(f"Crew_Stacker_{ci}_Seat", (cx, cy, 0.45), (0.42, 0.40, 0.03), col)
            make_box(f"Crew_Stacker_{ci}_Back", (cx, cy - s * 0.19, 0.72), (0.40, 0.03, 0.34), col)
            for li, (lx, ly) in enumerate(((-0.18, -0.17), (0.18, -0.17), (-0.18, 0.17), (0.18, 0.17))):
                make_box(f"Crew_Stacker_{ci}_Leg_{li}", (cx + lx, cy + ly, 0.2175), (0.022, 0.022, 0.435), (0.66, 0.66, 0.64, 1.0))
            make_box(f"Crew_Stacker_{ci}_BackPost", (cx, cy - s * 0.19, 0.5075), (0.04, 0.03, 0.085), col)
    # the table's night: Marisol's thermos, Russell's Express-News, a napkin box
    make_cyl("Marisol_Thermos", (tx - 0.55, ty - 0.20, tz + 0.13), 0.045, 0.26, (0.62, 0.20, 0.24, 1.0), segments=10)
    make_box("Express_News", (tx + 0.15, ty + 0.18, tz + 0.006), (0.36, 0.28, 0.012), (0.86, 0.84, 0.78, 1.0))
    make_box("Express_News_Masthead", (tx + 0.15, ty + 0.30, tz + 0.0125), (0.30, 0.03, 0.001), (0.16, 0.16, 0.18, 1.0))
    make_box("Napkin_Box", (tx - 0.10, ty, tz + 0.05), (0.14, 0.12, 0.10), (0.86, 0.86, 0.82, 1.0))


def build_lockers_clock():
    """The crew's lockers on the E wall S of the vending machine; the
    time clock and its card rack W of the doorway."""
    lx, ly0 = ROOM_W/2.0 - 0.10 - 0.25, 1.15
    for k in range(6):
        y = ly0 + 0.08 + k * 0.38
        make_box(f"Locker_{k}", (lx, y + 0.19, 0.95), (0.50, 0.36, 1.90), (0.42, 0.48, 0.52, 1.0))
        make_box(f"Locker_{k}_Vents", (lx - 0.252, y + 0.19, 1.62), (0.004, 0.24, 0.16), (0.30, 0.34, 0.38, 1.0))
        make_box(f"Locker_{k}_Handle", (lx - 0.256, y + 0.33, 1.05), (0.012, 0.03, 0.10), (0.70, 0.70, 0.68, 1.0))
        make_box(f"Locker_{k}_Name_Tape", (lx - 0.253, y + 0.19, 1.78), (0.003, 0.18, 0.04), (0.92, 0.90, 0.80, 1.0))
    tcx = DOORWAY[0] - DOORWAY[2] / 2.0 - 0.55
    make_box("Time_Clock", (tcx, 0.18, 1.35), (0.26, 0.16, 0.32), (0.80, 0.78, 0.72, 1.0))
    make_box("Time_Clock_Face", (tcx, 0.262, 1.42), (0.18, 0.004, 0.10), (0.20, 0.28, 0.22, 1.0))
    make_box("Time_Card_Rack", (tcx - 0.45, 0.12, 1.35), (0.40, 0.04, 0.60), (0.56, 0.58, 0.60, 1.0))
    for k in range(6):
        make_box(f"Time_Card_{k}", (tcx - 0.60 + (k % 3) * 0.15, 0.15, 1.20 + (k // 3) * 0.28), (0.08, 0.004, 0.20), (0.92, 0.90, 0.80, 1.0))


def build_corridor():
    """Through the doorway: the break-room corridor and, at its E end,
    the dock door (steel, push bar, the EXIT sign) — "BT's footsteps
    cross the break-room corridor, hit the dock, push the dock door
    open"."""
    cy0, cy1 = -1.70, -0.10
    make_box("Corridor_Floor", (1.4, (cy0 + cy1) / 2.0, -0.01), (6.0, cy1 - cy0, 0.02), (0.56, 0.54, 0.50, 1.0))
    make_box("Corridor_Ceil", (1.4, (cy0 + cy1) / 2.0, CEIL + 0.01), (6.0, cy1 - cy0, 0.02), (0.84, 0.84, 0.80, 1.0))
    make_wall("Corridor_Wall_S", (1.4, cy0 - 0.10, 0), length=6.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Corridor_Wall_W", (-1.70, (cy0 + cy1) / 2.0, 0), length=cy1 - cy0, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    ex = 4.50
    from _props.structure import make_wall_with_openings
    make_wall_with_openings("Corridor_Wall_E", (ex, (cy0 + cy1) / 2.0, 0), length=cy1 - cy0, height=CEIL, axis='Y', palette=PAL_WALL,
                            baseboard_face_sign=-1, openings=[((cy0 + cy1) / 2.0, 1.05, 0.96, 2.10)])
    make_box("Dock_Door", (ex, (cy0 + cy1) / 2.0, 1.035), (0.05, 0.94, 2.07), (0.55, 0.57, 0.58, 1.0))
    make_box("Dock_Door_PushBar", (ex - 0.045, (cy0 + cy1) / 2.0, 1.05), (0.03, 0.70, 0.06), (0.40, 0.42, 0.44, 1.0))
    make_box("Dock_Door_WireGlass", (ex - 0.03, (cy0 + cy1) / 2.0, 1.55), (0.006, 0.26, 0.36), (0.44, 0.48, 0.50, 1.0))
    make_box("Dock_Door_Exit_Sign", (ex - 0.12, (cy0 + cy1) / 2.0, 2.30), (0.10, 0.36, 0.14), (0.86, 0.22, 0.18, 1.0))
    make_box("Corridor_Light", (1.4, (cy0 + cy1) / 2.0, CEIL - 0.03), (1.20, 0.24, 0.05), (0.96, 0.96, 0.90, 1.0))
    make_box("Corridor_Mop_Bucket", (-1.30, cy0 + 0.30, 0.20), (0.36, 0.30, 0.40), (0.86, 0.72, 0.20, 1.0))


def build_door_infill_dock_door_2026_09():
    """Dock_Door was narrower than its wall opening (the user, 2026-09-24:
    "doorways ... misaligned"): close the gap to the door and its frame."""
    make_wall("Wall_Fill_Dock_Door_W", (-0.725, 0.000, 0), length=0.550, height=2.000, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_Fill_Dock_Door_E", (0.725, 0.000, 0), length=0.550, height=2.000, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)

def main():
    clear_scene()
    build_shell()
    build_crew_table()
    build_lockers_clock()
    build_corridor()
    build_vending()
    build_kitchenette()
    build_fridge()
    build_board()
    build_break_decor()
    build_ceiling_infra()
    build_hero_props()
    build_hero_props_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_break_room.glb"))
    print(f"\n[build_centro_break_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
