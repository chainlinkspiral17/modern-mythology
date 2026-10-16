"""hospital_room — vol5-7 locale (auto-generated placement script)."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.views import make_view
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window, make_wall_with_openings
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture
from _props.detail import (make_traffic_wear, make_floor_stain,
                           make_wall_tint_band, make_threshold,
                           make_wall_outlet, make_light_switch)

ROOM_W = 5.0; ROOM_D = 5.0; CEIL = 2.8
PAL_WALL = {"wall":(0.74,0.74,0.70,1.0),"baseboard":(0.32,0.30,0.28,1.0)}
COL_FLOOR = (0.62,0.58,0.52,1.0); COL_SEAM = (0.32,0.30,0.28,1.0); COL_WOOD = (0.42,0.32,0.22,1.0)
COL_ACCENT = (0.86,0.62,0.28,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall_with_openings("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1, openings=[(1.3, 1.55, 1.60, 1.50)])   # cut 2026-10-07: its window was a pane on a solid wall
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

BED_X = -0.2; BED_Y = 3.75     # head to the N wall (2026-09-10: 1.4 m off it)

def build_bed():
    from _props.furniture import make_bed
    bx, by = BED_X, BED_Y
    frame=(0.62,0.60,0.58,1.0); mattress=(0.90,0.90,0.86,1.0); board=(0.82,0.82,0.80,1.0)
    # the shared hospital bed: steel posts on casters, deck, thin
    # mattress, side rails, one pillow (2026-09-07)
    make_bed("Bed", bx, by, head="+Y", w=0.98, d=2.00, style="hospital",
             frame_col=frame, mattress_col=mattress, blanket_col=(0.52, 0.70, 0.72, 1.0),
             pillow_col=(0.96, 0.96, 0.92, 1.0))
    make_box("Bed_Headboard", (bx, by+0.98, 0.62), (1.00, 0.06, 0.60), board)   # on the head posts (2026-10-08: it leaned on the waiting chairs, which have moved next door)
    make_box("Bed_Footboard", (bx, by-0.95, 0.52), (1.00, 0.06, 0.40), board)   # on the foot posts (2026-09-23: 7 cm off them)

def build_monitor():
    mx, my = 1.1, 3.5
    make_cyl("Vitals_Base", (mx, my, 0.03), 0.22, 0.05, P.METAL_BLACK, segments=12)
    make_cyl("Vitals_Pole", (mx, my, 0.75), 0.025, 1.44, P.METAL_STEEL)
    make_box("Vitals_Monitor", (mx, my, 1.42), (0.34, 0.28, 0.30), (0.16,0.16,0.18,1.0))
    make_box("Vitals_Screen", (mx-0.18, my, 1.42), (0.02, 0.22, 0.24), (0.06,0.10,0.14,1.0))
    make_box("Vitals_Wave", (mx-0.19, my-0.02, 1.48), (0.005, 0.16, 0.03), (0.32,0.92,0.42,1.0))
    make_box("Vitals_Num1", (mx-0.19, my+0.05, 1.36), (0.005, 0.05, 0.04), (0.32,0.86,0.92,1.0))
    make_box("Vitals_Num2", (mx-0.19, my-0.05, 1.36), (0.005, 0.05, 0.04), (0.96,0.72,0.32,1.0))

def build_iv():
    ix, iy = -1.4, 3.4
    make_cyl("IV_Hub", (ix, iy, 0.05), 0.06, 0.06, P.METAL_STEEL)
    for k,(dx,dy) in enumerate([(0.20,0.0),(0.06,0.19),(-0.16,0.12),(-0.16,-0.12),(0.06,-0.19)]):
        make_box(f"IV_Foot_{k}", (ix+dx*0.6, iy+dy*0.6, 0.02), (0.14,0.04,0.03), P.METAL_STEEL)
    make_cyl("IV_Pole", (ix, iy, 1.05), 0.02, 2.00, P.METAL_STEEL)
    make_box("IV_Hook", (ix, iy-0.08, 1.98), (0.03,0.16,0.03), P.METAL_STEEL)
    make_box("IV_Bag", (ix, iy-0.12, 1.835), (0.10, 0.16, 0.26), (0.86,0.90,0.86,1.0))   # from the hook (2026-09-23: 11.5 cm under it)
    make_cyl("IV_Chamber", (ix, iy-0.12, 1.655), 0.02, 0.10, (0.78,0.86,0.90,1.0))
    make_box("IV_Line", (ix+0.02, iy-0.30, 1.10), (0.008, 0.60, 0.008), (0.84,0.84,0.82,1.0))

def build_curtain():
    rail_z = CEIL-0.20
    make_cyl("Curtain_Rail", (0.0, 1.9, rail_z), 0.02, ROOM_W-0.6, P.METAL_STEEL, axis='X')
    for bi, bx in enumerate((-2.0, 2.0)):
        make_cyl(f"Curtain_Bracket_{bi}", (bx, 1.9, (rail_z + CEIL) / 2.0), 0.015, CEIL - rail_z, P.METAL_STEEL)   # rail UP to the ceiling (2026-09-23: they hung below the rail)
    make_box("Curtain_Fabric", (1.2, 1.9, rail_z-0.85), (2.0, 0.03, 1.60), (0.60,0.74,0.70,1.0))
    for i in range(6):
        make_box(f"Curtain_Pleat_{i}", (0.3+i*0.34, 1.88, rail_z-0.85), (0.02, 0.02, 1.58), (0.50,0.64,0.60,1.0))

def build_chair():
    cx, cy = -1.7, 1.6
    seat=(0.42,0.52,0.56,1.0)
    make_box("Chair_Seat", (cx, cy, 0.45), (0.44,0.44,0.06), seat)
    make_box("Chair_Back", (cx-0.19, cy, 0.70), (0.05,0.44,0.46), seat)
    for k,(ox,oy) in enumerate([(-0.18,-0.18),(0.18,-0.18),(-0.18,0.18),(0.18,0.18)]):
        make_box(f"Chair_Leg_{k}", (cx+ox, cy+oy, 0.22), (0.05,0.05,0.42), P.METAL_STEEL)
    for ai, oy in enumerate((-0.22,0.22)):
        make_box(f"Chair_Arm_{ai}", (cx, cy+oy, 0.62), (0.42,0.05,0.05), seat)

def build_tray_table():
    tx, ty = 0.7, 2.0
    make_box("Tray_Top", (tx + 0.03, ty, 0.88), (0.60, 0.42, 0.04), (0.86,0.84,0.80,1.0))   # over its post (2026-09-23: 2 cm off it)
    make_box("Tray_Post", (tx+0.34, ty, 0.45), (0.04,0.04,0.86), P.METAL_STEEL)
    make_box("Tray_Foot", (tx+0.34, ty, 0.03), (0.10,0.44,0.05), P.METAL_STEEL)
    make_cyl("Tray_Cup", (tx-0.10, ty, 0.94), 0.05, 0.10, (0.92,0.90,0.86,1.0))

def build_window():
    # anchored on the wall's room face, built toward the room (2026-09-23: the glass was inside the wall)
    make_window("Window", (1.3, ROOM_D - 0.10, 1.55), width=1.6, height=1.5, see_through=True)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

WX0, WX1, WY1 = -10.6, -2.7, 5.0       # the waiting room: W wall, the shared E edge, N wall (centre lines)


def _beam_seats(tag, x0, y, n, face, col_seat=(0.36, 0.46, 0.56, 1.0), col_back=(0.32, 0.42, 0.52, 1.0)):
    """A row of linked waiting-room chairs on a steel beam: seats, backs,
    arms between them, the beam on two legs. face=-1 faces -Y, +1 faces +Y."""
    pitch = 0.56
    steel = (0.55, 0.57, 0.58, 1.0)
    for ci in range(n):
        cx = x0 + ci * pitch
        make_box(f"{tag}_{ci}_Seat", (cx, y, 0.44), (0.50, 0.46, 0.05), col_seat)
        make_box(f"{tag}_{ci}_Back", (cx, y - face * 0.21, 0.72), (0.50, 0.05, 0.50), col_back)
    for ai in range(n + 1):
        make_box(f"{tag}_Arm_{ai}", (x0 - pitch / 2.0 + ai * pitch, y, 0.62), (0.04, 0.40, 0.04), steel)
        make_box(f"{tag}_Arm_{ai}_Post", (x0 - pitch / 2.0 + ai * pitch, y + face * 0.12, 0.53), (0.03, 0.03, 0.16), steel)
    L = n * pitch
    make_box(f"{tag}_Beam", (x0 + (n - 1) * pitch / 2.0, y, 0.385), (L, 0.08, 0.06), steel)
    for e in (-1, 1):
        lx = x0 + (n - 1) * pitch / 2.0 + e * (L / 2.0 - 0.25)
        make_box(f"{tag}_Leg_{e:+d}", (lx, y, 0.18), (0.06, 0.06, 0.36), steel)
        make_box(f"{tag}_Foot_{e:+d}", (lx, y, 0.01), (0.08, 0.44, 0.02), steel)


def build_waiting_room():
    """THE WAITING ROOM (2026-10-08). Ch7: "Maya is in the waiting room
    when Ben arrives ... She is in a chair against the back wall ... a paper
    cup of coffee from the vending machine that she has not drunk." Ch8 is
    Room 318: the bed, the IV, "the visitor's chair, which is too large for
    her". They were one 5 x 5 box — the waiting room's chairs and vending
    machine against the patient's wall. The waiting room is its own room
    now, next door to the west, 7.9 x 5 m under fluorescent troffers: beam
    seating along the back wall and back to back down the middle, the drink
    and snack machines on the east wall, a water cooler, a TV high on the
    west wall, a magazine table, a window three storeys up, the double doors
    to the corridor."""
    pal = {"wall": (0.80, 0.80, 0.74, 1.0), "baseboard": (0.30, 0.30, 0.30, 1.0)}
    make_floor("Wait_Floor", ((WX0 + WX1) / 2.0, WY1 / 2.0, 0.0), size_x=WX1 - WX0, size_y=WY1 + 0.4,
               palette={"vinyl": (0.66, 0.64, 0.58, 1.0), "seam": (0.40, 0.40, 0.38, 1.0)})
    make_wall_with_openings("Wait_Wall_W", (WX0, WY1 / 2.0, 0), length=WY1 + 0.4, height=CEIL, axis='Y', palette=pal,
                            baseboard_face_sign=+1, openings=[(2.5, 1.55, 1.80, 1.40)])
    make_wall("Wait_Wall_N", ((WX0 + WX1) / 2.0 - 0.1, WY1, 0), length=WX1 - WX0 - 0.2, height=CEIL, axis='X', palette=pal, baseboard_face_sign=-1)
    for nm, a, b in (("Wait_Wall_S_W", WX0 - 0.1, -6.2), ("Wait_Wall_S_E", -4.4, WX1)):
        make_wall(nm, ((a + b) / 2.0, 0.0, 0), length=b - a, height=CEIL, axis='X', palette=pal, baseboard_face_sign=+1)
    make_box("Wait_Wall_S_AboveDoor", (-5.3, 0.0, CEIL - 0.30), (1.8, 0.20, 0.60), pal["wall"])
    make_ceiling("Wait_Ceil", ((WX0 + WX1) / 2.0, WY1 / 2.0, CEIL), size_x=WX1 - WX0, size_y=WY1 + 0.4)
    # the double doors to the corridor, closed, a wired-glass light in each
    for e in (-1, 1):
        dx = -5.3 + e * 0.45
        make_box(f"Wait_Door_{e:+d}", (dx, 0.06, 1.05), (0.88, 0.05, 2.10), (0.62, 0.66, 0.70, 1.0))
        make_box(f"Wait_Door_{e:+d}_Light", (dx, 0.09, 1.55), (0.22, 0.01, 0.40), (0.30, 0.34, 0.40, 1.0))
        make_box(f"Wait_Door_{e:+d}_Plate", (dx - e * 0.30, 0.09, 1.05), (0.10, 0.01, 0.30), (0.80, 0.80, 0.78, 1.0))
    make_box("Wait_Sign_Waiting", (-5.3, 0.105, 2.42), (0.90, 0.01, 0.18), (0.24, 0.40, 0.60, 1.0))
    # the back wall's row (Maya's chair) and the middle back-to-back rows
    _beam_seats("Wait_Row_Back", -9.6, WY1 - 0.45, 7, face=-1)
    # the middle rows BACK TO BACK (2026-10-08: they were built FACING, seat
    # fronts 14 cm apart — the user: "Chairs facing each other with no room
    # between seems a big problem"); the north row faces the back wall's row
    # across 1.29 m, the south row faces the doors
    _beam_seats("Wait_Row_Mid_N", -8.9, 2.80, 5, face=+1)
    _beam_seats("Wait_Row_Mid_S", -8.9, 2.30, 5, face=-1)
    # her coffee on the seat beside hers, not drunk
    make_cyl("Paper_Coffee_Cup", (-9.6 + 3 * 0.56, WY1 - 0.45, 0.515), 0.035, 0.10, (0.88, 0.86, 0.80, 1.0), segments=8)
    make_cyl("Paper_Coffee_Cup_Lid", (-9.6 + 3 * 0.56, WY1 - 0.45, 0.57), 0.037, 0.01, (0.20, 0.20, 0.22, 1.0), segments=8)
    # the machines on the east wall, faced west
    ex = WX1 - 0.10
    for mi, (my, body, face) in enumerate(((3.70, (0.62, 0.20, 0.18, 1.0), (0.80, 0.84, 0.88, 1.0)),
                                            (2.70, (0.20, 0.22, 0.26, 1.0), (0.36, 0.46, 0.56, 1.0)))):
        nm = ("Vending_Machine", "Vending_Snack")[mi]
        make_box(nm, (ex - 0.40, my, 0.93), (0.78, 0.86, 1.86), body)
        make_box(f"{nm}_Face", (ex - 0.795, my - 0.08, 1.10), (0.01, 0.58, 1.20), face)
        make_box(f"{nm}_Slot", (ex - 0.795, my + 0.30, 0.25), (0.01, 0.20, 0.12), (0.10, 0.10, 0.12, 1.0))
        if mi == 1:
            for r in range(5):
                for c in range(4):
                    make_box(f"Vending_Snack_Item_{r}_{c}", (ex - 0.803, my - 0.28 + c * 0.14, 0.62 + r * 0.22), (0.004, 0.10, 0.14),
                             P.SNACK_TINTS[(r * 4 + c) % len(P.SNACK_TINTS)])
    make_box("Water_Cooler_Body", (ex - 0.18, 1.55, 0.50), (0.32, 0.32, 1.00), (0.90, 0.90, 0.88, 1.0))
    make_cyl("Water_Cooler_Jug", (ex - 0.18, 1.55, 1.18), 0.13, 0.36, (0.60, 0.74, 0.86, 0.6), segments=12)
    # the TV high on the west wall, on its bracket, the late news
    make_box("Wait_TV_Bracket", (WX0 + 0.20, 2.5, 2.25), (0.20, 0.10, 0.10), (0.20, 0.20, 0.22, 1.0))
    make_box("Wait_TV", (WX0 + 0.34, 3.8, 2.10), (0.08, 0.90, 0.54), (0.10, 0.10, 0.12, 1.0))
    make_box("Wait_TV_Bracket_Arm", (WX0 + 0.20, 3.8, 2.10), (0.20, 0.10, 0.10), (0.20, 0.20, 0.22, 1.0))
    make_box("Wait_TV_Screen", (WX0 + 0.381, 3.8, 2.10), (0.002, 0.82, 0.46), (0.34, 0.42, 0.52, 1.0))
    # a magazine table between the rows and the window, a plant
    make_box("Wait_Table", (-9.9, 1.10, 0.25), (0.60, 0.60, 0.50), (0.46, 0.36, 0.26, 1.0))
    for mi in range(3):
        make_box(f"Wait_Magazine_{mi}", (-9.95 + mi * 0.06, 1.05 + mi * 0.05, 0.505 + mi * 0.006), (0.21, 0.28, 0.006),
                 P.SNACK_TINTS[(mi * 3) % len(P.SNACK_TINTS)])
    make_floor_plant("Wait_Plant", (WX0 + 0.45, WY1 - 0.50, 0.0), kind="ficus")
    make_window("Wait_Window", (WX0 + 0.10, 2.5, 1.55), width=1.80, height=1.40, axis='Y', room_dir=+1, see_through=True)
    for j in range(4):
        make_fluorescent_tube_fixture(f"Wait_Fluor_{j}", (-9.0 + (j % 2) * 3.4, 1.4 + (j // 2) * 2.3, CEIL), length=1.40, width=0.34)
    make_wall_clock("Wait_Clock", (-6.2, WY1 - 0.10, 2.20), frozen_hour=12, frozen_min=14, facing='-Y')

def build_detail_pass_2026_08():
    """D2 surface breakup + first D3 (generic template pass per
    lore/_SET_DETAIL_PLAYBOOK.md): the entry walk-line, a work-zone
    stain, ceiling gather on the long walls, a threshold, and the
    switch/outlet pair every room earns. Per-locale wear
    PERSONALITY (whose feet, whose spills) is the next pass."""
    wear = (COL_FLOOR[0] * 0.88, COL_FLOOR[1] * 0.88, COL_FLOOR[2] * 0.88, 1.0)
    stain = (COL_FLOOR[0] * 0.82, COL_FLOOR[1] * 0.82, COL_FLOOR[2] * 0.82, 1.0)
    pw = PAL_WALL["wall"]
    band = (pw[0] * 0.90, pw[1] * 0.90, pw[2] * 0.88, 1.0)
    make_traffic_wear("Wear_Entry", [(0.0, 0.6), (0.0, ROOM_D * 0.55)],
                      width=0.75, tint=wear)
    make_floor_stain("Stain_WorkZone", (ROOM_W * 0.22, ROOM_D * 0.62),
                     radius=0.24, tint=stain)
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


def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    THE HANDS ("she takes Linda's free hand in both of hers and
    holds it"): residue grammar — two creases in the bed blanket
    at the free-hand side."""
    # on the blanket (2026-09-23: 80 cm off the bed's foot, in the air)
    make_box("Hands_Blanket_Crease_A", (0.10, 3.20, 0.706), (0.14, 0.05, 0.012), (0.52, 0.58, 0.62, 1.0))
    make_box("Hands_Blanket_Crease_B", (0.13, 3.08, 0.705), (0.05, 0.12, 0.010), (0.50, 0.56, 0.60, 1.0))



def build_room_318_lived_in_2026_10():
    """ROOM 318, A WEEK IN (2026-10-08; "too bare and empty"). Ch8: Linda
    with the IV in her Morse-key hand, Maya at the bed, Gracie on "the
    visitor's chair, which is too large for her", Anita "by the window".
    The headwall behind the bed (gas outlets, the call box, the light over
    it), the nurse's whiteboard, a TV on its arm, a clock, the sink and the
    sanitizer by the door, get-well cards and flowers on the sill, the
    pitcher and the cup with a straw on the tray, the call button clipped
    to the rail, a pillow on the visitor's chair."""
    from _props.geometry import make_lathe, make_blob, make_tube, make_chamfer_box
    WF, EF, NF, SF = -ROOM_W/2.0 + 0.10, ROOM_W/2.0 - 0.10, ROOM_D - 0.10, 0.10
    white = (0.94, 0.94, 0.92, 1.0); grey = (0.66, 0.68, 0.70, 1.0); steel = (0.62, 0.64, 0.66, 1.0)
    # the headwall over the bed
    make_box("Headwall", (BED_X, NF - 0.03, 1.35), (1.50, 0.06, 0.50), (0.80, 0.82, 0.80, 1.0))
    for k, col in enumerate(((0.30, 0.56, 0.32, 1.0), (0.94, 0.94, 0.92, 1.0), (0.80, 0.70, 0.20, 1.0))):
        make_cyl(f"Headwall_Outlet_{k}", (BED_X - 0.50 + k * 0.18, NF - 0.065, 1.42), 0.03, 0.01, col, axis='Y', segments=10)
    make_box("Headwall_CallBox", (BED_X + 0.45, NF - 0.07, 1.35), (0.18, 0.02, 0.22), grey)
    make_box("Overbed_Light", (BED_X, NF - 0.06, 1.85), (1.10, 0.12, 0.10), white)
    # the whiteboard on the W wall
    make_box("Nurse_Whiteboard", (WF + 0.01, 3.20, 1.50), (0.02, 0.90, 0.60), white)
    make_box("Nurse_Whiteboard_Frame", (WF + 0.005, 3.20, 1.50), (0.01, 0.94, 0.64), grey)
    for li in range(4):
        make_box(f"Nurse_Whiteboard_Line_{li}", (WF + 0.021, 3.05 + (li % 2) * 0.10, 1.68 - li * 0.11), (0.002, 0.45 - (li % 3) * 0.08, 0.02),
                 ((0.20, 0.30, 0.70, 1.0), (0.70, 0.20, 0.20, 1.0))[li % 2])
    # the TV on its arm, high on the E wall, toward the bed
    make_box("TV_Arm_Plate", (EF - 0.01, 3.40, 2.05), (0.02, 0.16, 0.20), (0.24, 0.24, 0.26, 1.0))
    make_box("TV_Arm", (EF - 0.20, 3.40, 2.05), (0.36, 0.05, 0.05), (0.24, 0.24, 0.26, 1.0))
    make_box("TV", (EF - 0.40, 3.40, 2.05), (0.05, 0.70, 0.42), (0.10, 0.10, 0.12, 1.0))
    make_box("TV_Screen", (EF - 0.426, 3.40, 2.05), (0.002, 0.64, 0.36), (0.24, 0.30, 0.38, 1.0))
    make_wall_clock("Clock", (EF, 1.30, 2.10), frozen_hour=10, frozen_min=40, facing='-X')
    # the sink by the door, its towels; the sanitizer
    make_box("Sink_Cabinet", (WF + 0.28, 0.75, 0.42), (0.56, 0.60, 0.84), (0.82, 0.80, 0.74, 1.0))
    make_box("Sink_Top", (WF + 0.28, 0.75, 0.855), (0.58, 0.62, 0.03), white)
    make_box("Sink_Basin", (WF + 0.30, 0.75, 0.871), (0.40, 0.40, 0.002), grey)
    make_tube("Sink_Faucet", [(WF + 0.05, 0.75, 0.87), (WF + 0.06, 0.75, 1.10), (WF + 0.20, 0.75, 1.12), (WF + 0.24, 0.75, 1.06)], 0.012, steel)
    make_box("Paper_Towels", (WF + 0.07, 0.75, 1.45), (0.14, 0.30, 0.34), white)
    make_box("Sanitizer", (-1.10, SF + 0.05, 1.30), (0.12, 0.10, 0.22), white)
    make_box("Sanitizer_Pump", (-1.10, SF + 0.11, 1.20), (0.04, 0.02, 0.03), grey)
    # the sill: get-well cards and flowers — the window Anita stands at
    make_box("Window_Sill", (1.30, NF - 0.08, 0.76), (1.84, 0.16, 0.03), white)
    cols = ((0.86, 0.52, 0.56, 1.0), (0.96, 0.86, 0.40, 1.0), (0.52, 0.70, 0.86, 1.0), (0.64, 0.80, 0.56, 1.0))
    for ci in range(4):
        make_box(f"GetWell_Card_{ci}", (0.62 + ci * 0.20, NF - 0.10, 0.775 + 0.07), (0.12, 0.01, 0.14), cols[ci])
    make_lathe("Flowers_Vase", (1.75, NF - 0.08, 0.775), [(0.05, 0.0), (0.06, 0.08), (0.04, 0.18), (0.05, 0.22), (0.0, 0.22)], (0.70, 0.84, 0.86, 1.0), segments=12)
    make_blob("Flowers_Greens", (1.75, NF - 0.08, 1.06), 0.12, (0.30, 0.50, 0.28, 1.0), noise=0.3, seed=21, squash=0.8)
    for fi, (dx, dz, col) in enumerate(((-0.05, 1.12, (0.94, 0.80, 0.30, 1.0)), (0.06, 1.10, (0.90, 0.46, 0.56, 1.0)), (0.0, 1.17, (0.96, 0.96, 0.94, 1.0)))):
        make_blob(f"Flowers_Bloom_{fi}", (1.75 + dx, NF - 0.08, dz), 0.045, col, noise=0.2, seed=30 + fi, squash=0.8)
    # the tray: pitcher, the cup with a straw, tissues
    make_lathe("Tray_Pitcher", (0.52, 2.10, 0.90), [(0.05, 0.0), (0.06, 0.16), (0.05, 0.20), (0.0, 0.20)], (0.86, 0.80, 0.70, 1.0), segments=10)
    make_cyl("Tray_Straw_Cup", (0.82, 1.90, 0.95), 0.035, 0.10, white, segments=10)
    make_cyl("Tray_Straw_Cup_Straw", (0.84, 1.90, 1.04), 0.004, 0.12, (0.86, 0.30, 0.40, 1.0), segments=4)
    make_box("Tray_Tissues", (0.92, 2.10, 0.94), (0.18, 0.12, 0.08), (0.60, 0.74, 0.84, 1.0))
    # the call button clipped to the bed's rail; a pillow on the visitor's chair
    make_box("Call_Button", (0.32, 3.30, 0.62), (0.03, 0.08, 0.04), grey)
    make_tube("Call_Button_Cord", [(0.32, 3.34, 0.60), (0.40, 3.70, 0.45), (0.45, 4.40, 0.80), (BED_X + 0.45, NF - 0.08, 1.30)], 0.004, grey)
    make_chamfer_box("Visitor_Pillow", (-1.70, 1.66, 0.52), (0.36, 0.24, 0.12), (0.82, 0.86, 0.88, 1.0), chamfer=0.03)

def main():
    clear_scene()
    build_shell()
    build_bed()
    build_monitor()
    build_iv()
    build_curtain()
    build_chair()
    build_tray_table()
    build_window()
    build_ceiling_infra()
    build_waiting_room()
    build_detail_pass_2026_08()
    build_hero_props_2026_09()
    build_room_318_lived_in_2026_10()
    # what is outside the window (2026-10-07, _props/views.py)
    make_view("View_N", "N", ROOM_D, 1.3, kind="street", ground_z=-9.0, seed=2)
    make_view("Wait_View_W", "W", WX0, 2.5, kind="street", ground_z=-9.0, span=8.0, seed=30)   # the waiting room's window, three storeys up
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/hospital_room.glb"))
    print(f"\n[build_hospital_room] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
