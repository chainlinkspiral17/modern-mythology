"""XVIII · MOON — The Static Drive-In Snack Bar. Small concession
interior in the middle of the drive-in lot: popcorn machine,
soda fountain, candy case, ticket counter. Through the long window
on the N wall: the blank white drive-in screen looming, speaker
posts in the lot, an empty pickup or two — moonlit. Natalie's
sigils-in-static beat.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_faded_poster, make_floor_plant
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture)
from _props.food_service import make_donut_display
from _props.signage import make_hanging_banner

PAL = {"wall": (0.86, 0.84, 0.78, 1.0), "baseboard": (0.42, 0.38, 0.34, 1.0)}
COL_FLOOR_LINO = (0.78, 0.74, 0.66, 1.0); COL_SEAM = (0.42, 0.40, 0.36, 1.0)
COL_COUNTER = (0.86, 0.84, 0.78, 1.0); COL_COUNTER_TOP = (0.62, 0.18, 0.16, 1.0)
COL_POPCORN_RED = (0.86, 0.22, 0.20, 1.0); COL_POPCORN_YELLOW = (0.96, 0.86, 0.42, 1.0)
COL_GLASS = (0.78, 0.84, 0.86, 0.50); COL_NEON_MARQUEE = (0.96, 0.32, 0.42, 1.0)
COL_SCREEN_WHITE = (0.96, 0.96, 0.94, 1.0); COL_SKY_MOON = (0.10, 0.12, 0.22, 1.0)
COL_MOON_DISC = (0.92, 0.92, 0.84, 1.0); COL_ASPHALT = (0.16, 0.16, 0.18, 1.0)
COL_SODA_FOUNTAIN = (0.62, 0.66, 0.70, 1.0); COL_CANDY = (0.86, 0.74, 0.42, 1.0)

ROOM_W = 7.0; ROOM_D = 5.0; CEIL = 2.90


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_LINO, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    # N wall has a long window (the drive-in view)
    make_wall("Wall_N_W", (-2.80, ROOM_D, 0), length=1.40, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+2.80, ROOM_D, 0), length=1.40, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": (0.42, 0.38, 0.34, 1.0)})


def build_picture_window_and_view():
    # Big horizontal window N — frame + glass.
    make_box("Window_Frame", (0.0, ROOM_D-0.04, 1.70), (4.00, 0.04, 1.40), COL_NEON_MARQUEE)
    make_box("Window_Glass", (0.0, ROOM_D-0.06, 1.70), (3.80, 0.005, 1.30), COL_GLASS)
    # ── Outside view (far back-plane) ────────────────────────────
    # Night sky backdrop
    make_box("Sky_BG", (0.0, ROOM_D + 16.0, 4.0), (40.0, 0.04, 10.0), COL_SKY_MOON)
    # Moon
    make_cyl("Moon", (-2.0, ROOM_D + 15.9, 6.5), 0.70, 0.04, COL_MOON_DISC, axis='Y', segments=20)
    # Massive blank drive-in screen — the iconic empty rectangle
    make_box("Screen_BG", (0.0, ROOM_D + 12.0, 4.5), (10.0, 0.30, 4.50), (0.22, 0.20, 0.22, 1.0))
    make_box("Screen_White", (0.0, ROOM_D + 11.85, 4.5), (9.20, 0.04, 4.20), COL_SCREEN_WHITE)
    # Screen support struts
    for sx in [-4.5, +4.5]:
        make_box(f"Screen_Strut_{sx:+.0f}", (sx, ROOM_D + 12.0, 1.20), (0.20, 0.30, 2.40),
                 (0.18, 0.16, 0.18, 1.0))
    # Asphalt lot
    make_box("Lot_Asphalt", (0.0, ROOM_D + 6.0, 0.02), (12.0, 9.0, 0.04), COL_ASPHALT)
    # Speaker posts — 6 of them in a grid
    for spi, (spx, spy) in enumerate([(-3.0, ROOM_D+2.0), (0.0, ROOM_D+2.0), (+3.0, ROOM_D+2.0),
                                       (-3.0, ROOM_D+5.0), (0.0, ROOM_D+5.0), (+3.0, ROOM_D+5.0)]):
        make_cyl(f"Speaker_Post_{spi}", (spx, spy, 0.70), 0.04, 1.40, P.METAL_BLACK)
        make_box(f"Speaker_Box_{spi}", (spx, spy, 1.50), (0.12, 0.12, 0.20), (0.32, 0.30, 0.30, 1.0))
    # A lone pickup at the front row
    px, py = -1.50, ROOM_D + 3.0
    make_box("Pickup_Body", (px, py, 0.70), (1.60, 0.80, 0.50), (0.42, 0.30, 0.30, 1.0))
    make_box("Pickup_Cab", (px-0.20, py, 1.05), (0.80, 0.80, 0.40), (0.42, 0.30, 0.30, 1.0))
    make_box("Pickup_Bed", (px+0.60, py, 0.94), (0.60, 0.70, 0.30), (0.32, 0.22, 0.20, 1.0))
    for sgn_x in (-1, +1):
        for sgn_y in (-1, +1):
            make_cyl(f"Pickup_Wheel_{sgn_x:+d}_{sgn_y:+d}",
                     (px+sgn_x*0.62, py+sgn_y*0.34, 0.30), 0.18, 0.10, P.METAL_BLACK, axis='X')


def build_concession_counter():
    # L-shaped counter, opening toward S (visitors)
    # E section
    make_box("Counter_E_Top",  (+2.20, 3.20, 0.96), (1.40, 0.50, 0.04), COL_COUNTER_TOP)
    make_box("Counter_E_Body", (+2.20, 3.20, 0.46), (1.40, 0.50, 0.92), COL_COUNTER)
    # W section
    make_box("Counter_W_Top",  (-1.60, 3.20, 0.96), (2.40, 0.50, 0.04), COL_COUNTER_TOP)
    make_box("Counter_W_Body", (-1.60, 3.20, 0.46), (2.40, 0.50, 0.92), COL_COUNTER)
    # Cash register on the W section
    make_box("Register_Body", (-2.20, 3.20, 1.10), (0.40, 0.40, 0.25), (0.32, 0.32, 0.36, 1.0))
    make_box("Register_Screen", (-2.20, 3.10, 1.32), (0.30, 0.005, 0.10), (0.18, 0.42, 0.34, 1.0))
    make_box("Register_Drawer", (-2.20, 3.20, 0.86), (0.40, 0.40, 0.10), (0.32, 0.32, 0.36, 1.0))


def build_popcorn_machine():
    px, py = +1.00, 3.20
    make_box("Popcorn_Base", (px, py, 1.20), (0.50, 0.50, 0.40), COL_POPCORN_RED)
    make_box("Popcorn_Kettle_BG", (px, py, 1.60), (0.50, 0.50, 0.40), COL_POPCORN_RED)
    make_box("Popcorn_Window", (px, py-0.20, 1.60), (0.42, 0.005, 0.36), COL_GLASS)
    # Kettle inside
    make_cyl("Popcorn_Kettle", (px, py, 1.70), 0.10, 0.20, P.METAL_BLACK, segments=10)
    # Striped peaked roof
    make_box("Popcorn_Roof_R", (px, py, 1.94), (0.50, 0.50, 0.08), COL_POPCORN_RED)
    make_box("Popcorn_Roof_Y", (px, py, 2.00), (0.40, 0.50, 0.06), COL_POPCORN_YELLOW)
    # A few popped kernels piled in the window
    for ki in range(8):
        kx = px + (ki % 4) * 0.08 - 0.15
        ky = py - 0.10
        kz = 1.50 + (ki // 4) * 0.05
        make_cyl(f"Popcorn_Kernel_{ki}", (kx, ky, kz), 0.03, 0.04, COL_POPCORN_YELLOW, segments=6)


def build_soda_fountain_and_candy():
    # Soda fountain on the W section of counter
    sx, sy = -0.80, 3.10
    make_box("SodaFountain_Base", (sx, sy, 1.10), (0.80, 0.40, 0.35), COL_SODA_FOUNTAIN)
    # 4 dispenser nozzles
    for ni in range(4):
        nx = sx - 0.30 + ni * 0.20
        make_cyl(f"Soda_Nozzle_{ni}", (nx, sy-0.16, 1.30), 0.04, 0.10, COL_NEON_MARQUEE)
        make_box(f"Soda_Tag_{ni}", (nx, sy-0.20, 1.42), (0.16, 0.005, 0.10),
                 [(0.86, 0.22, 0.20, 1.0), (0.32, 0.20, 0.16, 1.0),
                  (0.96, 0.86, 0.42, 1.0), (0.32, 0.48, 0.34, 1.0)][ni])
    # Ice / cup tower
    make_box("Cup_Tower", (sx+0.34, sy, 1.40), (0.10, 0.30, 0.40), P.PAPER)
    # Candy display case to the right (a 2-tier donut display reskinned)
    make_donut_display("Candy", (+0.20, 3.20, 0.96), tiers=2,
                       palette={"glass": (0.78, 0.84, 0.86, 0.50),
                                "metal": (0.62, 0.66, 0.70, 1.0),
                                "donut": COL_CANDY})


def build_marquee_inside():
    # Hanging "SHOW STARTING" banner from the ceiling, near the S
    # entrance, so guests inside the snack bar can read it.
    make_hanging_banner("Banner_Show", (0.0, 1.2, CEIL), width=2.40, height=0.36,
                         bg_color=COL_NEON_MARQUEE, text_color=P.PAPER)


def build_ceiling_infra():
    for j, (xpos, ypos) in enumerate([(-1.5, 2.0), (+1.5, 2.0), (-1.5, 4.0), (+1.5, 4.0)]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (xpos, ypos, CEIL),
                                       length=1.00, width=0.30,
                                       palette={"diffuser": (1.00, 0.98, 0.92, 1.0)})
    make_smoke_detector("Smoke", (0.0, 2.5, CEIL))
    make_sprinkler("Spr_W", (-2.0, 2.5, CEIL))
    make_sprinkler("Spr_E", (+2.0, 2.5, CEIL))


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 2.5, 2.30), frozen_hour=4, frozen_min=15)
    make_faded_poster("Poster_S", (-ROOM_W/2.0+0.05, 0.8, 1.50))
    make_floor_plant("Plant", (+ROOM_W/2.0-0.50, 0.50, 0.0), palette={"leaf": (0.40, 0.46, 0.30, 1.0)})


def main():
    clear_scene()
    build_shell()
    build_picture_window_and_view()
    build_concession_counter()
    build_popcorn_machine()
    build_soda_fountain_and_candy()
    build_marquee_inside()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/static_drive_in.glb"))
    print(f"\n[build_static_drive_in] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
