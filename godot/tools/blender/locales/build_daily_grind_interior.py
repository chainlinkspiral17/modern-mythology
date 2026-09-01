"""daily_grind_interior — the Daily Grind coffee shop (sibling idiom to
cafe_olimpico). Espresso bar + machine, pastry case, chalkboard menu,
café tables with chairs, a couch/armchair nook. Warm pendant lighting
(see .tscn).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window
from _props.store_fixtures import make_register
from _props.food_service import make_coffee_pots, make_donut_display, make_paper_cup_stack, make_sugar_creamer_caddy
from _props.decor import make_floor_plant
from _props.safety import make_smoke_detector

ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 2.8
PAL_WALL = {"wall":(0.72,0.66,0.56,1.0),"baseboard":(0.34,0.28,0.22,1.0)}
COL_FLOOR = (0.54,0.44,0.34,1.0); COL_SEAM = (0.32,0.26,0.20,1.0)
COL_WOOD = (0.42,0.30,0.20,1.0); COL_COUNTER_TOP = (0.22,0.16,0.12,1.0)
COL_STEEL = P.METAL_STEEL; COL_BLACK = P.METAL_BLACK
COL_ESPRESSO = (0.78,0.78,0.74,1.0); COL_ESPRESSO_TRIM = (0.32,0.22,0.14,1.0)
COL_CHALK = (0.14,0.16,0.15,1.0); COL_COUCH = (0.40,0.32,0.26,1.0)
COL_ACCENT = (0.86,0.62,0.28,1.0)

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
    # 2026-08 tail pass: FRONT WINDOWS in both S segments (street
    # light on the tables) + the BELL over the entry door.
    make_window("Win_SW", (-2.25, 0.10, 1.60), width=1.70, height=1.40)
    make_window("Win_SE", (+2.25, 0.10, 1.60), width=1.70, height=1.40)
    make_box("DoorBell_Arm", (0.55, 0.16, 2.28), (0.03, 0.14, 0.03), COL_STEEL)
    make_cyl("DoorBell", (0.55, 0.26, 2.22), 0.05, 0.07, (0.82, 0.72, 0.42, 1.0), segments=10)
    # BACK DOOR in the N wall's E end (to the alley), mostly closed.
    make_box("Back_Door", (2.95, ROOM_D-0.06, 1.05), (0.90, 0.06, 2.10), (0.36, 0.30, 0.24, 1.0))
    make_cyl("Back_Door_Knob", (2.67, ROOM_D-0.12, 1.02), 0.03, 0.04, COL_STEEL, segments=8)

def build_service_counter():
    # Espresso bar running along X in front of the north wall.
    top_z = 1.03
    make_box("Counter_Front", (-0.4, 5.2, 0.47), (5.6, 0.60, 0.94), COL_WOOD)
    make_box("Counter_Top",   (-0.4, 5.14, top_z), (5.8, 0.80, 0.06), COL_COUNTER_TOP)
    make_box("Counter_Kick",  (-0.4, 4.90, 0.10), (5.6, 0.05, 0.20), COL_BLACK)
    # Espresso machine (2-group, chrome).
    ex, ey = -1.9, 5.25
    make_box("Espresso_Body", (ex, ey, top_z+0.28), (1.20, 0.46, 0.54), COL_ESPRESSO)
    make_box("Espresso_TopHat", (ex, ey, top_z+0.60), (1.20, 0.46, 0.10), COL_ESPRESSO_TRIM)
    for gi in range(2):
        gx = ex - 0.26 + gi*0.52
        make_cyl(f"Espresso_Group_{gi}_Head", (gx, ey-0.20, top_z+0.18), 0.06, 0.10, COL_ESPRESSO_TRIM)
        make_cyl(f"Espresso_Group_{gi}_Spout", (gx, ey-0.20, top_z+0.10), 0.02, 0.08, COL_STEEL)
        make_cyl(f"Espresso_Cup_{gi}", (gx, ey-0.20, top_z+0.04), 0.04, 0.06, P.PAPER)
    make_cyl("Espresso_SteamWand", (ex+0.54, ey-0.10, top_z+0.28), 0.012, 0.28, COL_STEEL)
    # 2026-08 tail pass: steaming MILK PITCHERS by the wand + the
    # under-counter milk COOLER + the house MARSHMALLOW SLAB on its
    # cutting board (the hot-chocolate ritual).
    for mi, (mxo, myo) in enumerate([(0.72, -0.15), (0.86, 0.02)]):
        make_cyl(f"Milk_Pitcher_{mi}_Body", (ex+mxo, ey+myo, top_z+0.07), 0.05, 0.14, COL_STEEL, segments=10)
        make_box(f"Milk_Pitcher_{mi}_Handle", (ex+mxo+0.06, ey+myo, top_z+0.08), (0.02, 0.02, 0.10), COL_STEEL)
    make_box("Milk_Cooler", (ex+0.85, ey+0.05, 0.38), (0.55, 0.50, 0.70), (0.66, 0.68, 0.70, 1.0))
    make_box("Milk_Cooler_Door", (ex+0.85, ey-0.21, 0.38), (0.48, 0.02, 0.60), (0.58, 0.60, 0.62, 1.0))
    make_box("Milk_Cooler_Handle", (ex+1.02, ey-0.23, 0.50), (0.03, 0.02, 0.14), COL_BLACK)
    make_box("Marshmallow_Board", (0.9, 5.05, top_z+0.045), (0.40, 0.28, 0.03), (0.52, 0.40, 0.28, 1.0))
    make_box("Marshmallow_Slab", (0.9, 5.05, top_z+0.10), (0.30, 0.20, 0.08), (0.97, 0.95, 0.90, 1.0))
    for si, (sxo, syo) in enumerate([(0.20, 0.06), (0.24, -0.05)]):
        make_box(f"Marshmallow_Cube_{si}", (0.9+sxo, 5.05+syo, top_z+0.075), (0.05, 0.05, 0.05),
                 (0.97, 0.95, 0.90, 1.0))
    make_box("Marshmallow_Knife", (0.9, 4.88, top_z+0.05), (0.22, 0.03, 0.01), COL_STEEL)
    make_paper_cup_stack("CupStack", (ex-0.66, ey+0.02, top_z), count=16)
    # Drip coffee pots (make_coffee_pots — was imported but never used).
    make_coffee_pots("Coffee", (0.5, 5.25, top_z), pots=2)
    # Pastry case at the east end.
    make_donut_display("Pastry", (2.0, 5.28, top_z))
    # Register on the counter top.
    make_register("Register", (2.95, 5.05, top_z))
    # Condiment / sugar caddy at the west end.
    make_sugar_creamer_caddy("Caddy", (-3.0, 4.95, top_z))

def build_chalkboard():
    cx, cz, y = -0.5, 2.05, 5.90
    make_box("Chalk_Frame", (cx, y, cz), (2.40, 0.04, 0.90), COL_WOOD)
    make_box("Chalk_Board", (cx, y-0.02, cz), (2.20, 0.02, 0.74), COL_CHALK)
    # Menu text rows (faint chalk lines).
    chalk_cols = [(0.86,0.84,0.78,1.0),(0.72,0.82,0.72,1.0),(0.86,0.78,0.62,1.0)]
    for r in range(4):
        make_box(f"Chalk_Row_{r}", (cx-0.30, y-0.03, cz+0.24 - r*0.16), (1.10, 0.002, 0.03), chalk_cols[r % 3])
        make_box(f"Chalk_Price_{r}", (cx+0.72, y-0.03, cz+0.24 - r*0.16), (0.26, 0.002, 0.03), (0.86,0.72,0.42,1.0))

def _make_cafe_table(prefix, tx, ty):
    make_cyl(f"{prefix}_Top", (tx, ty, 0.74), 0.38, 0.04, COL_WOOD, segments=16)
    make_cyl(f"{prefix}_Pedestal", (tx, ty, 0.37), 0.05, 0.70, COL_ESPRESSO_TRIM)
    make_cyl(f"{prefix}_Foot", (tx, ty, 0.03), 0.22, 0.04, COL_ESPRESSO_TRIM, segments=12)
    make_cyl(f"{prefix}_Saucer", (tx, ty, 0.77), 0.06, 0.006, P.PAPER)
    make_cyl(f"{prefix}_Cup", (tx, ty, 0.81), 0.04, 0.06, P.PAPER)
    for ci, (ox, oy) in enumerate([(-0.58, 0.0), (0.58, 0.0)]):
        cx, cy = tx + ox, ty + oy
        make_cyl(f"{prefix}_Chair_{ci}_Seat", (cx, cy, 0.46), 0.18, 0.04, COL_WOOD, segments=12)
        make_box(f"{prefix}_Chair_{ci}_Back", (cx + (0.16 if ox < 0 else -0.16), cy, 0.72), (0.04, 0.36, 0.52), COL_WOOD)
        for li, (lx, ly) in enumerate([(-0.13,-0.13),(0.13,-0.13),(-0.13,0.13),(0.13,0.13)]):
            make_cyl(f"{prefix}_Chair_{ci}_Leg_{li}", (cx+lx, cy+ly, 0.23), 0.012, 0.46, COL_BLACK)

def build_tables():
    _make_cafe_table("Table_0", -2.0, 2.3)
    _make_cafe_table("Table_1", 0.4, 1.9)
    # The CORNER FOUR-TOP (SE, by the front window) — square, four
    # chairs; where the group scenes actually sit.
    tx, ty = 2.55, 1.3
    make_box("FourTop_Top", (tx, ty, 0.74), (0.95, 0.95, 0.05), COL_WOOD)
    for li,(lxo,lyo) in enumerate([(-0.40,-0.40),(0.40,-0.40),(-0.40,0.40),(0.40,0.40)]):
        make_box(f"FourTop_Leg_{li}", (tx+lxo, ty+lyo, 0.36), (0.06, 0.06, 0.72), COL_ESPRESSO_TRIM)
    for ci,(cxo,cyo,along_x) in enumerate([(0.0,-0.78,True),(0.0,0.78,True),(-0.78,0.0,False),(0.78,0.0,False)]):
        make_cyl(f"FourTop_Chair_{ci}_Seat", (tx+cxo, ty+cyo, 0.46), 0.18, 0.04, COL_WOOD, segments=12)
        if along_x:
            byo = 0.17 if cyo > 0 else -0.17
            make_box(f"FourTop_Chair_{ci}_Back", (tx+cxo, ty+cyo+byo, 0.72), (0.36, 0.04, 0.52), COL_WOOD)
        else:
            bxo = 0.17 if cxo > 0 else -0.17
            make_box(f"FourTop_Chair_{ci}_Back", (tx+cxo+bxo, ty+cyo, 0.72), (0.04, 0.36, 0.52), COL_WOOD)
    make_cyl("FourTop_Cup", (tx-0.15, ty+0.12, 0.81), 0.04, 0.06, P.PAPER)

def build_lounge():
    # Couch + armchair + low table nook in the SW corner.
    cx = -2.9
    make_box("Couch_Base", (cx, 4.0, 0.24), (0.70, 1.60, 0.22), COL_COUCH)
    make_box("Couch_Back", (cx-0.27, 4.0, 0.56), (0.16, 1.60, 0.52), COL_COUCH)
    for ay in (3.25, 4.75):
        make_box(f"Couch_Arm_{ay:.0f}", (cx, ay, 0.40), (0.66, 0.16, 0.34), COL_COUCH)
    for ci, cy in enumerate([3.62, 4.38]):
        make_box(f"Couch_SeatCush_{ci}", (cx+0.02, cy, 0.40), (0.58, 0.60, 0.14), (0.50,0.40,0.32,1.0))
        make_box(f"Couch_BackCush_{ci}", (cx-0.16, cy, 0.60), (0.18, 0.58, 0.38), (0.50,0.40,0.32,1.0))
    # Low coffee table
    make_box("Lounge_Table_Top", (cx+1.0, 4.0, 0.42), (0.66, 0.90, 0.05), COL_WOOD)
    for li, (lx, ly) in enumerate([(-0.28,-0.38),(0.28,-0.38),(-0.28,0.38),(0.28,0.38)]):
        make_cyl(f"Lounge_Table_Leg_{li}", (cx+1.0+lx, 4.0+ly, 0.20), 0.02, 0.40, COL_BLACK)
    make_box("Lounge_Magazine", (cx+1.0, 4.0, 0.46), (0.24, 0.30, 0.02), (0.72,0.42,0.28,1.0))
    # Armchair facing the couch
    ax = cx + 1.9
    make_box("Armchair_Base", (ax, 4.0, 0.24), (0.62, 0.62, 0.22), COL_COUCH)
    make_box("Armchair_Back", (ax+0.25, 4.0, 0.56), (0.14, 0.62, 0.52), COL_COUCH)
    for ay in (3.70, 4.30):
        make_box(f"Armchair_Arm_{ay:.0f}", (ax, ay, 0.40), (0.58, 0.14, 0.34), COL_COUCH)
    make_box("Armchair_Cush", (ax, 4.0, 0.40), (0.54, 0.54, 0.14), (0.50,0.40,0.32,1.0))

def build_pendants():
    for pi, (px, py) in enumerate([(-1.5, 5.0), (1.0, 5.0), (0.0, 2.3)]):
        make_cyl(f"Pendant_{pi}_Cord", (px, py, CEIL-0.28), 0.006, 0.36, COL_BLACK)
        make_cyl(f"Pendant_{pi}_Shade", (px, py, CEIL-0.58), 0.15, 0.16, (0.86,0.58,0.28,1.0), segments=12)
        make_cyl(f"Pendant_{pi}_Bulb", (px, py, CEIL-0.66), 0.05, 0.06, (0.98,0.88,0.62,1.0))

def build_decor():
    make_floor_plant("Plant_SE", (ROOM_W/2.0-0.55, 0.60, 0.0))

def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))

def build_hero_props_2026_09():
    """HERO PROPS FOR THE BLIND CUES (shot_marker_audit, 2026-09-01).

    Five distinct cues fire on the Daily Grind and none had
    geometry:

    - KAI'S PHONE ("Kai showed her the pictures of the patch on
      his phone" — the corner table): face-up on Table_0 by the
      SW window.
    - THE FREQUENCY BENEATH ("a hand-drawn radio dial in graphite
      on what looked like brown paper"): the John Frank paperback
      flat on Table_1, graphite dial on the cover.
    - WREN'S NOTEBOOK ("the small spiral notebook she carried for
      her schoolwork"): beside the book.
    - THE DUFFEL ("He set the duffel down on the floor beside the
      chair"): canvas duffel on the floor by the four-top's north
      chair.
    - THE TOWER (~ "There is a tower on the hill that has been
      there longer than the town"): a hill band + dark tower
      silhouette past the SW window — distant, unlabeled, the way
      the town treats it.

    Draft note: draft N+1 could give the tower its one lit floor
    after dusk (mood strata) and the duffel a zipper line.
    """
    # ── KAI'S PHONE · corner table (top 0.76) ──
    make_box("Kais_Phone", (-2.20, 2.15, 0.7665), (0.070, 0.140, 0.011),
             (0.13, 0.13, 0.15, 1.0))
    # ── THE FREQUENCY BENEATH · Table_1 ──
    make_box("Frequency_Book", (0.25, 1.80, 0.771), (0.130, 0.200, 0.020),
             (0.62, 0.50, 0.36, 1.0))
    make_cyl("Frequency_Book_Dial", (0.25, 1.80, 0.7825), 0.035, 0.002,
             (0.28, 0.28, 0.30, 1.0), segments=10)
    # ── WREN'S NOTEBOOK · beside it ──
    make_box("Wrens_Notebook", (0.58, 2.00, 0.766), (0.110, 0.150, 0.010),
             (0.30, 0.44, 0.58, 1.0))
    make_box("Wrens_Notebook_Wire", (0.641, 2.00, 0.767), (0.010, 0.150, 0.012),
             (0.55, 0.56, 0.58, 1.0))
    # ── THE DUFFEL · floor beside the four-top's north chair ──
    make_box("Kai_Duffel", (3.10, 2.45, 0.15), (0.55, 0.28, 0.30),
             (0.36, 0.40, 0.34, 1.0))
    make_box("Kai_Duffel_Strap", (3.10, 2.45, 0.312), (0.42, 0.06, 0.024),
             (0.26, 0.28, 0.24, 1.0))
    # ── THE TOWER ON THE HILL · past the SW window ──
    make_box("Hill_Beyond", (-5.0, -18.0, 1.8), (18.0, 10.0, 3.6),
             (0.30, 0.36, 0.28, 1.0))
    make_cyl("Watch_Tower", (-5.5, -20.0, 6.1), 0.9, 5.0,
             (0.26, 0.24, 0.28, 1.0), segments=10)
    make_cyl("Watch_Tower_Cap", (-5.5, -20.0, 8.85), 1.1, 0.5,
             (0.22, 0.20, 0.24, 1.0), segments=10)


def main():
    clear_scene()
    build_shell()
    build_service_counter()
    build_chalkboard()
    build_tables()
    build_lounge()
    build_pendants()
    build_decor()
    build_ceiling_infra()
    build_hero_props_2026_09()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/daily_grind_interior.glb"))
    print(f"\n[build_daily_grind_interior] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
