"""VOL 5 · Houston Design Studio — Emperor cameo.
Open-plan creative studio: drafting tables, brick wall, exposed
duct, large monitors, plotter, mood board.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_window, make_crown_molding
from _props.decor import make_faded_poster, make_floor_plant
from _props.safety import make_fluorescent_tube_fixture, make_hvac_vent, make_smoke_detector

PAL_WALL = {"wall": (0.86, 0.78, 0.70, 1.0), "baseboard": (0.42, 0.32, 0.22, 1.0)}
COL_BRICK = (0.62, 0.42, 0.34, 1.0); COL_BRICK_SEAM = (0.32, 0.22, 0.18, 1.0)
COL_FLOOR = (0.42, 0.36, 0.30, 1.0); COL_FLOOR_SEAM = (0.22, 0.18, 0.16, 1.0)
COL_DESK_WOOD = (0.62, 0.46, 0.30, 1.0); COL_MONITOR = (0.06, 0.08, 0.10, 1.0)
COL_DUCT = (0.62, 0.62, 0.60, 1.0); COL_TRIM = (0.32, 0.28, 0.24, 1.0)
ROOM_W = 10.0; ROOM_D = 7.0; CEIL = 3.20

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4, palette={"vinyl": COL_FLOOR, "seam": COL_FLOOR_SEAM})
    # West wall is brick
    make_wall("Wall_W", (-ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette={"wall": COL_BRICK, "baseboard": COL_BRICK_SEAM}, baseboard_face_sign=+1)
    # Brick course lines
    for r in range(int(CEIL*4)):
        make_box(f"Wall_W_Brick_{r}", (-ROOM_W/2.0+0.04, ROOM_D/2.0, r*0.25+0.12), (0.005, ROOM_D, 0.012), COL_BRICK_SEAM)
    make_wall("Wall_E", (+ROOM_W/2.0, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    # Exposed ductwork running E-W
    make_cyl("Duct", (0.0, ROOM_D/2.0, CEIL-0.25), 0.20, ROOM_W, COL_DUCT, axis='X', segments=10)
    # North window — mullioned (make_window was imported/unused)
    make_window("Window_N", (0.0, ROOM_D, 2.10), width=5.0, height=1.60,
                palette={"glass": (0.78, 0.84, 0.86, 0.50), "frame": P.METAL_BLACK})

def build_drafting_row():
    # 3 drafting tables in a row, tilted tops
    for di, dx in enumerate([-2.8, 0.0, +2.8]):
        dy = 3.5
        make_box(f"Drafting_{di}_Top", (dx, dy, 0.90), (1.20, 0.80, 0.04), COL_DESK_WOOD)
        # Tilted-up rear edge
        make_box(f"Drafting_{di}_TopBack", (dx, dy+0.30, 1.06), (1.20, 0.04, 0.20), COL_DESK_WOOD)
        for li, (lx, ly) in enumerate([(dx-0.54,dy-0.34),(dx+0.54,dy-0.34),(dx-0.54,dy+0.34),(dx+0.54,dy+0.34)]):
            make_box(f"Drafting_{di}_Leg_{li}", (lx, ly, 0.45), (0.04, 0.04, 0.90), COL_TRIM)
        # Paper / blueprint on top
        make_box(f"Drafting_{di}_Paper", (dx, dy+0.10, 0.93), (1.00, 0.60, 0.005), P.PAPER)
        # Anglepoise lamp
        make_cyl(f"Drafting_{di}_LampBase", (dx-0.45, dy+0.30, 0.94), 0.05, 0.02, P.METAL_BLACK)
        make_cyl(f"Drafting_{di}_LampArm1", (dx-0.45, dy+0.30, 1.10), 0.012, 0.34, P.METAL_BLACK)
        make_cyl(f"Drafting_{di}_LampHead", (dx-0.35, dy+0.30, 1.30), 0.08, 0.10, P.METAL_BLACK)

def build_workstations():
    # Two tall workstation desks south side
    for wi, wx in enumerate([-3.0, +3.0]):
        wy = 1.5
        make_box(f"Work_{wi}_Desk", (wx, wy, 0.72), (1.40, 0.70, 0.04), COL_DESK_WOOD)
        for li, (lx, ly) in enumerate([(wx-0.64,wy-0.30),(wx+0.64,wy-0.30),(wx-0.64,wy+0.30),(wx+0.64,wy+0.30)]):
            make_box(f"Work_{wi}_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_TRIM)
        # Dual monitors
        make_box(f"Work_{wi}_Mon1", (wx-0.30, wy+0.20, 1.08), (0.50, 0.04, 0.36), COL_MONITOR)
        make_box(f"Work_{wi}_Mon2", (wx+0.30, wy+0.20, 1.08), (0.50, 0.04, 0.36), COL_MONITOR)
        # Keyboard + mouse
        make_box(f"Work_{wi}_KB", (wx, wy-0.10, 0.76), (0.45, 0.15, 0.02), (0.32, 0.30, 0.32, 1.0))

def build_plotter_and_mood_board():
    # Plotter on east wall
    px, py = +4.40, 5.0
    make_box("Plotter_Body", (px, py, 0.50), (0.50, 1.40, 1.00), (0.92, 0.92, 0.88, 1.0))
    make_box("Plotter_Slot", (px-0.26, py, 0.85), (0.04, 1.20, 0.04), P.METAL_BLACK)
    make_box("Plotter_PaperOut", (px-0.30, py, 0.85), (0.05, 1.10, 0.005), P.PAPER)
    # Large mood board on east wall
    make_box("MoodBoard", (+4.96, 5.0, 1.80), (0.04, 2.20, 1.40), (0.18, 0.16, 0.18, 1.0))
    # Pinned items in cycling colors
    for pi in range(8):
        col = P.SNACK_TINTS[pi % len(P.SNACK_TINTS)]
        make_box(f"MoodPin_{pi}",
                 (+4.94, 5.0 + (pi%4 - 1.5)*0.50, 1.50 + (pi//4)*0.50),
                 (0.005, 0.34, 0.26), col)

def _task_chair(name, cx, cy, seat_col=(0.20, 0.22, 0.26, 1.0)):
    make_box(f"{name}_Seat", (cx, cy, 0.50), (0.44, 0.44, 0.06), seat_col)
    make_box(f"{name}_Back", (cx, cy+0.20, 0.86), (0.44, 0.05, 0.60), seat_col)
    make_cyl(f"{name}_Post", (cx, cy, 0.26), 0.03, 0.48, P.METAL_BLACK, segments=6, axis='Z')
    import math
    for s in range(5):
        a = math.radians(72*s)
        make_box(f"{name}_Foot_{s}", (cx+0.24*math.cos(a), cy+0.24*math.sin(a), 0.05),
                 (0.08, 0.08, 0.06), P.METAL_BLACK)
        make_cyl(f"{name}_Caster_{s}", (cx+0.26*math.cos(a), cy+0.26*math.sin(a), 0.03),
                 0.03, 0.04, P.METAL_BLACK, segments=6, axis='X')

def build_task_chairs():
    # Chairs at the three drafting tables (dy=3.5) and two workstations (wy=1.5)
    for di, dx in enumerate([-2.8, 0.0, +2.8]):
        _task_chair(f"DraftChair_{di}", dx, 3.5-0.78, seat_col=(0.36, 0.20, 0.18, 1.0))
    for wi, wx in enumerate([-3.0, +3.0]):
        _task_chair(f"WorkChair_{wi}", wx, 1.5-0.78)

def build_materials_shelf():
    # Materials / samples shelf against the S wall (creative clutter)
    sx, sy = +2.6, 0.30
    make_box("MatShelf_Body", (sx, sy, 0.90), (2.20, 0.40, 1.80), COL_TRIM)
    make_box("MatShelf_Back", (sx, sy+0.18, 0.90), (2.16, 0.04, 1.76), (0.28, 0.24, 0.20, 1.0))
    for si, sz in enumerate([0.36, 0.84, 1.32, 1.72]):
        make_box(f"MatShelf_Shelf_{si}", (sx, sy, sz), (2.16, 0.36, 0.03), (0.30, 0.26, 0.22, 1.0))
    # Colour-blocked sample bins / material swatches on the shelves
    for bi in range(12):
        col = P.SNACK_TINTS[bi % len(P.SNACK_TINTS)]
        bx = sx - 0.90 + (bi % 4)*0.60
        bz = 0.44 + (bi // 4)*0.48
        make_box(f"MatSample_{bi}", (bx, sy-0.06, bz), (0.42, 0.24, 0.22), col)
    # A stack of rolled plans leaning in the corner
    for ri in range(3):
        make_cyl(f"PlanRoll_{ri}", (sx+1.05+ri*0.05, sy+0.05, 0.70), 0.05, 1.30,
                 (0.86, 0.82, 0.72, 1.0), segments=8, axis='Z')

def build_decor():
    make_faded_poster("Poster_E1", (+4.95, 1.5, 1.80))
    make_faded_poster("Poster_W1", (-4.95, 4.5, 2.20), palette={"body": (0.62, 0.46, 0.32, 1.0)})
    make_floor_plant("Plant_NE", (+4.0, 6.5, 0.0))

def build_ceiling_infra():
    for j, ypos in enumerate([2.0, 5.0]):
        for i in range(-1, 2):
            make_fluorescent_tube_fixture(f"Fluor_{j}_{i}", (i*3.0, ypos, CEIL), length=1.80, width=0.40)
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_hvac_vent("HVAC", (-2.0, 6.0, CEIL), width=1.00, depth=0.50)

def main():
    clear_scene(); build_shell(); build_drafting_row(); build_workstations(); build_task_chairs(); build_materials_shelf(); build_plotter_and_mood_board(); build_decor(); build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../assets/3d/locales/houston_design_studio.glb"))
    print(f"\n[build_houston_design_studio] exporting to {out}")
    export_glb(out)

if __name__ == "__main__": main()
