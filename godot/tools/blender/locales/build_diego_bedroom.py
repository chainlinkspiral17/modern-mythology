"""Diego's Bedroom — vol6 — Diego Ramos (the missing kid; lives and
breathes soccer). GREEN/WHITE/RED palette (Mexico colors) and a
soccer-everything prop set: a ball, cleats, jerseys + a scarf pinned to
the wall, a shelf of trophies + medals, a Mexico/club flag, a striker
poster, a desk with homework, and a duffel bag — so it reads
unmistakably as Diego's, not a reskin of Jesse's."""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.store_fixtures import make_counter, make_counter_bullnose, make_register
from _props.shelving import make_snack_aisle, make_endcap
from _props.food_service import make_coffee_pots, make_donut_display
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster, make_calendar
from _props.safety import make_smoke_detector, make_hvac_vent, make_fluorescent_tube_fixture, make_ceiling_speaker

ROOM_W = 4.0; ROOM_D = 4.5; CEIL = 2.6
# Crisp white walls — the room is a shrine to the pitch. Green + red accents.
PAL_WALL = {"wall": (0.90, 0.91, 0.87, 1.0), "baseboard": (0.24, 0.52, 0.32, 1.0)}
COL_FLOOR = (0.58, 0.50, 0.40, 1.0); COL_SEAM = (0.32, 0.24, 0.16, 1.0); COL_WOOD = (0.46, 0.34, 0.22, 1.0)
COL_ACCENT = (0.20, 0.56, 0.34, 1.0)     # pitch green
COL_RED = (0.78, 0.20, 0.20, 1.0)        # Mexico red
COL_WHITE = (0.92, 0.92, 0.90, 1.0)
COL_GOLD = (0.86, 0.72, 0.28, 1.0)       # trophies / medals

def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), PAL_WALL["wall"])
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax, ceil_z=CEIL, palette={"wood": COL_WOOD})

def build_bed():
    # Re-arranged (2026-07-15): bed shoved into the NW corner, headboard
    # against the N wall, long axis E–W (rotated 90° off the shared
    # side-wall twin) — reads distinct from Maya's under-window bed and
    # the apartment beds. Keeps the kit-color dressing.
    bx, by = -0.85, ROOM_D - 0.98
    make_box("Bed_Frame", (bx, by, 0.20), (1.80, 1.12, 0.20), (0.42, 0.30, 0.20, 1.0))
    make_box("Bed_Mattress", (bx, by, 0.40), (1.70, 1.02, 0.16), (0.92, 0.86, 0.78, 1.0))
    make_box("Bed_Headboard", (bx, by+0.60, 0.62), (1.80, 0.08, 0.60), (0.40, 0.28, 0.18, 1.0))
    make_box("Bed_Pillow", (bx, by+0.38, 0.50), (1.60, 0.32, 0.10), P.PAPER)
    # Green comforter with a white center stripe (kit colors)
    make_box("Bed_Comforter", (bx, by-0.06, 0.50), (1.74, 0.86, 0.10), COL_ACCENT)
    make_box("Bed_Stripe", (bx, by-0.06, 0.52), (0.30, 0.86, 0.11), COL_WHITE)
    make_box("Bed_Throw", (bx, by-0.34, 0.50), (1.70, 0.34, 0.06), COL_RED)

def build_desk_lamp():
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Desk_Top", (dx, dy, 0.74), (1.00, 0.60, 0.04), COL_WOOD)
    for li in range(4):
        lx, ly = dx+(-0.44,+0.44,-0.44,+0.44)[li], dy+(-0.24,-0.24,+0.24,+0.24)[li]
        make_box(f"Desk_Leg_{li}", (lx, ly, 0.36), (0.04, 0.04, 0.72), COL_WOOD)
    make_box("Lamp_Base", (dx-0.30, dy+0.20, 0.78), (0.10, 0.10, 0.04), P.METAL_BLACK)
    make_cyl("Lamp_Arm", (dx-0.30, dy+0.20, 0.96), 0.012, 0.30, P.METAL_BLACK)
    make_cyl("Lamp_Head", (dx-0.20, dy+0.20, 1.16), 0.06, 0.08, COL_RED)
    # Homework: an open notebook + textbook + a pen
    make_box("Notebook", (dx+0.12, dy-0.02, 0.765), (0.30, 0.40, 0.01), P.PAPER)
    make_box("Textbook", (dx+0.30, dy+0.16, 0.79), (0.24, 0.30, 0.05), COL_ACCENT)
    make_cyl("Pen", (dx+0.02, dy-0.08, 0.762), 0.008, 0.16, COL_RED, axis='Y', segments=6)

def build_posters():
    # A poster of a favorite striker (west wall)
    for pi in range(2):
        px = -ROOM_W/2.0+0.05
        py = 1.0 + pi*1.6
        make_faded_poster(f"Poster_Striker_{pi}", (px, py, 1.55))

def build_win():
    make_window("Window_N", (0.0, ROOM_D-0.02, 1.50), width=1.20, height=1.00)

def build_ceiling_infra():
    for j in range(2):
        ypos = ROOM_D * (0.30 + j * 0.40)
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL), length=1.40, width=0.34)
    make_smoke_detector("Smoke", (0.0, ROOM_D/2.0, CEIL))
    make_hvac_vent("HVAC", (-ROOM_W/4.0, ROOM_D-0.5, CEIL), width=0.80, depth=0.40)

def build_dressing():
    """Soccer-everything dressing: a ball + cleats on the floor, a dresser,
    jerseys + a scarf pinned to the north wall, a shelf of trophies +
    medals, a Mexico/club flag on the west wall, a duffel bag, and a desk
    chair. make_floor_plant is imported/wired as a corner sprout."""
    bx, by = -0.85, ROOM_D - 0.98
    make_box("Nightstand", (bx+1.2, by, 0.28), (0.40, 0.40, 0.56), COL_WOOD)
    make_box("Clock", (bx+1.2, by, 0.62), (0.15, 0.10, 0.10), P.METAL_BLACK)
    # Dresser against the east wall
    make_box("Dresser", (ROOM_W/2.0-0.30, ROOM_D-1.3, 0.45), (0.44, 1.0, 0.90), COL_WOOD)
    for di in range(3):
        make_box(f"Dresser_Drawer_{di}", (ROOM_W/2.0-0.52, ROOM_D-1.3, 0.24+di*0.24), (0.02, 0.86, 0.16), (0.34, 0.24, 0.16, 1.0))
    # Trophy + medal shelf ON TOP of the dresser
    tx = ROOM_W/2.0 - 0.30
    make_box("TrophyShelf", (tx, ROOM_D-1.3, 0.95), (0.44, 1.0, 0.04), COL_WOOD)
    for ti in range(3):
        ty = ROOM_D-1.7 + ti*0.4
        make_cyl(f"Trophy_Cup_{ti}", (tx, ty, 1.12), 0.06, 0.16, COL_GOLD, segments=10)
        make_cyl(f"Trophy_Base_{ti}", (tx, ty, 1.00), 0.05, 0.08, (0.36, 0.24, 0.16, 1.0), segments=8)
    # Hanging medals (ribbon + disc) on the shelf edge
    for mi in range(3):
        my = ROOM_D-1.5 + mi*0.28
        make_box(f"Medal_Ribbon_{mi}", (tx-0.22, my, 1.02), (0.02, 0.05, 0.20), COL_RED)
        make_cyl(f"Medal_Disc_{mi}", (tx-0.22, my, 0.90), 0.05, 0.02, COL_GOLD, axis='X', segments=10)
    # Soccer ball + cleats on the floor
    make_cyl("SoccerBall", (0.4, 1.0, 0.14), 0.14, 0.28, COL_WHITE, segments=12)
    for ci, cx in enumerate([-0.2, 0.06]):
        make_box(f"Cleat_{ci}", (cx, 0.5, 0.06), (0.12, 0.30, 0.12), COL_ACCENT)
        make_box(f"CleatSole_{ci}", (cx, 0.5, 0.01), (0.13, 0.31, 0.03), P.METAL_BLACK)
    # Jerseys + scarf pinned to the north wall
    for ji, (jy, jc) in enumerate([(-0.7, COL_ACCENT), (0.7, COL_WHITE)]):
        make_box(f"Jersey_{ji}", (jy, ROOM_D-0.06, 1.7), (0.60, 0.03, 0.80), jc)
        make_box(f"Jersey_{ji}_Number", (jy, ROOM_D-0.09, 1.7), (0.20, 0.01, 0.30), COL_RED)
    make_box("Scarf", (0.0, ROOM_D-0.06, 2.25), (1.40, 0.03, 0.18), COL_RED)
    # Mexico / club flag on the west wall — green/white/red bands side by side
    fx = -ROOM_W/2.0 + 0.06
    for bi, bc in enumerate([COL_ACCENT, COL_WHITE, COL_RED]):
        make_box(f"Flag_Band_{bi}", (fx, 3.0+bi*0.32, 1.7), (0.02, 0.30, 0.90), bc)
    # Duffel bag by the door
    make_cyl("Duffel", (0.9, 0.5, 0.22), 0.24, 0.72, COL_ACCENT, axis='Y', segments=10)
    make_box("Duffel_Handle", (0.9, 0.5, 0.40), (0.30, 0.04, 0.06), P.METAL_BLACK)
    # Desk chair
    dx, dy = +ROOM_W/4.0, 1.5
    make_box("Chair_Seat", (dx, dy-0.55, 0.46), (0.42, 0.42, 0.05), COL_WOOD)
    make_box("Chair_Back", (dx, dy-0.74, 0.74), (0.42, 0.05, 0.46), COL_ACCENT)
    for i, (lx, ly) in enumerate([(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]):
        make_box(f"Chair_Leg_{i}", (dx+lx, dy-0.55+ly, 0.23), (0.05, 0.05, 0.44), P.METAL_BLACK)
    # Corner sprout (wires the imported helper)
    make_floor_plant("Plant", (-ROOM_W/2.0+0.5, ROOM_D-0.6, 0.0), palette={"leaf": (0.30, 0.54, 0.34, 1.0), "pot": (0.78, 0.24, 0.22, 1.0)})

def main():
    clear_scene()
    build_shell()
    build_bed()
    build_desk_lamp()
    build_dressing()
    build_posters()
    build_win()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/diego_bedroom.glb"))
    print(f"\n[build_diego_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
