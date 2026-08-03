"""pit_stop_office — the Pit Stop DINER's back office (vol6).

2026-08-03 tail pass: this is a diner office, not a garage office —
tyre stack swapped for dry-goods cases, and the vol6_ch3 hero props
added: the yellow legal pad + pen Ben writes his list on, and the
desk's drawer pedestal whose BOTTOM drawer (ajar, folded apron
visible) is where the list goes.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture

ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6
PAL_WALL = {"wall":(0.78,0.70,0.58,1.0),"baseboard":(0.42,0.32,0.22,1.0)}
COL_FLOOR = (0.62,0.52,0.42,1.0); COL_SEAM = (0.32,0.22,0.14,1.0); COL_WOOD = (0.42,0.30,0.20,1.0)
COL_ACCENT = (0.78,0.42,0.22,1.0)

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)

def build_desk():
    dx, dy = 0.0, ROOM_D-1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.80, 0.80, 0.04), COL_WOOD)
    # Legs / modesty panels
    for i, lx in enumerate([-0.82, 0.82]):
        make_box(f"Desk_Side_{i}", (dx+lx, dy, 0.37), (0.06, 0.76, 0.72), COL_WOOD)
    # CRT monitor on a base + keyboard + scattered work-order papers + mug
    make_box("Monitor_Body", (dx, dy+0.20, 1.02), (0.46, 0.36, 0.36), (0.30, 0.30, 0.28, 1.0))
    make_box("Monitor_Screen", (dx, dy+0.02, 1.02), (0.40, 0.02, 0.28), (0.08, 0.14, 0.12, 1.0))
    make_box("Keyboard", (dx, dy-0.16, 0.77), (0.44, 0.16, 0.03), (0.32, 0.32, 0.30, 1.0))
    for pi in range(3):
        make_box(f"Paper_{pi}", (dx-0.6+pi*0.14, dy+0.05, 0.77), (0.18, 0.24, 0.01), (0.86, 0.84, 0.78, 1.0))
    make_cyl("Mug", (dx+0.62, dy-0.05, 0.82), 0.04, 0.09, COL_ACCENT, segments=10)
    # Ben's yellow legal pad + pen (vol6_ch3 — the list).
    make_box("Legal_Pad", (dx+0.34, dy-0.10, 0.765), (0.22, 0.30, 0.012), (0.94, 0.88, 0.42, 1.0))
    make_box("Legal_Pad_Lines", (dx+0.34, dy-0.10, 0.772), (0.18, 0.24, 0.004), (0.88, 0.82, 0.38, 1.0))
    make_cyl("Pen", (dx+0.52, dy-0.22, 0.775), 0.008, 0.14, (0.14, 0.16, 0.30, 1.0), segments=6)
    # Drawer pedestal under the desk's right side — the bottom
    # drawer sits ajar, the folded apron's white edge showing (the
    # list lives beneath it).
    make_box("Desk_Pedestal", (dx+0.55, dy+0.05, 0.36), (0.44, 0.62, 0.70), COL_WOOD)
    for di in range(3):
        make_box(f"Desk_Drawer_{di}", (dx+0.55, dy-0.27, 0.16+di*0.22), (0.40, 0.02, 0.18), (0.48, 0.36, 0.24, 1.0))
        make_box(f"Desk_Drawer_Pull_{di}", (dx+0.55, dy-0.29, 0.16+di*0.22), (0.14, 0.02, 0.03), P.METAL_STEEL)
    make_box("Desk_Drawer_Bottom_Ajar", (dx+0.55, dy-0.33, 0.16), (0.40, 0.10, 0.16), (0.44, 0.32, 0.22, 1.0))
    make_box("Folded_Apron_Edge", (dx+0.55, dy-0.35, 0.235), (0.34, 0.06, 0.025), (0.92, 0.92, 0.90, 1.0))
    # Gooseneck desk lamp
    make_cyl("Lamp_Base", (dx-0.68, dy+0.14, 0.78), 0.07, 0.03, P.METAL_BLACK)
    make_cyl("Lamp_Col", (dx-0.68, dy+0.14, 0.98), 0.02, 0.40, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.58, dy+0.16, 1.16), 0.06, 0.10, COL_ACCENT)
    # Swivel office chair
    make_cyl("Chair_Seat", (dx, dy-0.7, 0.48), 0.24, 0.08, (0.20, 0.20, 0.22, 1.0), segments=14)
    make_box("Chair_Back", (dx, dy-0.92, 0.78), (0.44, 0.06, 0.46), (0.20, 0.20, 0.22, 1.0))
    make_cyl("Chair_Post", (dx, dy-0.7, 0.22), 0.03, 0.44, P.METAL_STEEL)
    for wi in range(5):
        import math as _m
        a = wi * (2.0*_m.pi/5.0)
        make_box(f"Chair_Foot_{wi}", (dx+_m.cos(a)*0.24, dy-0.7+_m.sin(a)*0.24, 0.05), (0.08, 0.08, 0.06), P.METAL_BLACK)

def build_filing():
    for ci in range(2):
        cx = -ROOM_W/2.0+0.35+ci*0.55
        make_box(f"Filing_{ci}", (cx, 1.0, 0.65), (0.50, 0.60, 1.30), (0.60, 0.60, 0.56, 1.0))
        # Three drawer faces + pull handles
        for di in range(3):
            make_box(f"Filing_{ci}_Drawer_{di}", (cx, 1.0-0.31, 0.30+di*0.42), (0.46, 0.02, 0.34), (0.52, 0.52, 0.48, 1.0))
            make_box(f"Filing_{ci}_Pull_{di}", (cx, 1.0-0.33, 0.30+di*0.42), (0.16, 0.02, 0.03), P.METAL_STEEL)

def build_office_dressing():
    """Diner back-office flavour: a pegboard of schedules and invoices,
    the wall calendar, a coffee maker, a dry-goods shelf, stacked
    supplier cases, and the spare apron on a door-side hook."""
    # Pegboard with clipped work orders on the west wall
    make_box("Pegboard", (-ROOM_W/2.0+0.06, ROOM_D-1.4, 1.6), (0.04, 1.2, 0.8), (0.62, 0.44, 0.28, 1.0))
    for wi in range(5):
        make_box(f"WorkOrder_{wi}", (-ROOM_W/2.0+0.10, ROOM_D-1.9+wi*0.24, 1.6), (0.02, 0.16, 0.22), (0.90, 0.88, 0.82, 1.0))
    make_calendar("Calendar", (-ROOM_W/2.0+0.06, ROOM_D-0.4, 1.5))
    # Parts shelf on the east wall with boxed parts
    sx = ROOM_W/2.0-0.22
    make_box("PartsShelf", (sx, ROOM_D-1.4, 1.3), (0.30, 1.10, 1.60), COL_WOOD)
    for r in range(3):
        for c in range(4):
            make_box(f"PartBox_{r}_{c}", (sx-0.03, ROOM_D-1.85+c*0.30, 0.75+r*0.42), (0.22, 0.22, 0.24), P.SNACK_TINTS[(r+c) % len(P.SNACK_TINTS)])
    # Coffee maker on top of a filing cabinet
    make_coffee_pots("Coffee", (-ROOM_W/2.0+0.9, 1.0, 1.35), pots=1)
    # Supplier cases stacked in the SE corner (syrup, napkins).
    for ti, (cw, cd, ch) in enumerate([(0.55, 0.42, 0.30), (0.50, 0.38, 0.28), (0.44, 0.34, 0.26)]):
        make_box(f"Supplier_Case_{ti}", (ROOM_W/2.0-0.5, 0.7, 0.15+ti*0.29), (cw, cd, ch), (0.62, 0.50, 0.34, 1.0))
        make_box(f"Supplier_Case_Tape_{ti}", (ROOM_W/2.0-0.5, 0.7, 0.15+ti*0.29+0.005), (cw+0.01, 0.08, ch), (0.74, 0.62, 0.42, 1.0))
    # Spare apron on a hook beside the door.
    make_cyl("Apron_Hook", (1.35, 0.14, 1.65), 0.02, 0.06, P.METAL_STEEL, segments=6)
    make_box("Apron_Hanging", (1.35, 0.17, 1.15), (0.34, 0.03, 0.95), (0.92, 0.92, 0.90, 1.0))
    make_box("Apron_Straps", (1.35, 0.18, 1.62), (0.20, 0.02, 0.10), (0.84, 0.84, 0.82, 1.0))

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def main():
    clear_scene()
    build_shell()
    build_desk()
    build_filing()
    build_office_dressing()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/pit_stop_office.glb"))
    print(f"\n[build_pit_stop_office] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
