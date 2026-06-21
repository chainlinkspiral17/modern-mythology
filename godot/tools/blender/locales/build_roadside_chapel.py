"""VI · LOVERS — Roadside Chapel. Tiny limestone chapel on a raised
mound in the cane fields. Single altar, two short kneelers, statue
niche on the east wall, arched stained-glass window N, bell pull
in the SW corner. Stone-cool interior, votive-warm pools at the
altar — sanctuary on cursed ground.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import make_smoke_detector, make_sprinkler

PAL = {"wall": (0.84, 0.80, 0.72, 1.0), "baseboard": (0.62, 0.56, 0.46, 1.0)}
COL_FLOOR_STONE = (0.66, 0.60, 0.52, 1.0); COL_SEAM = (0.46, 0.40, 0.34, 1.0)
COL_ALTAR = (0.92, 0.88, 0.78, 1.0); COL_ALTAR_CLOTH = (0.88, 0.72, 0.32, 1.0)
COL_PEW_WOOD = (0.36, 0.24, 0.16, 1.0); COL_STAINED_R = (0.74, 0.22, 0.20, 0.65)
COL_STAINED_B = (0.20, 0.34, 0.62, 0.65); COL_STAINED_G = (0.30, 0.48, 0.34, 0.65)
COL_VOTIVE = (0.96, 0.62, 0.28, 1.0); COL_STATUE = (0.86, 0.84, 0.78, 1.0)
COL_BELL_BRONZE = (0.62, 0.46, 0.26, 1.0)

ROOM_W = 5.0; ROOM_D = 7.0; CEIL = 3.40


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_STONE, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_S", (0.0, 0.0, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_N_W", (-1.40, ROOM_D, 0), length=1.80, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+1.40, ROOM_D, 0), length=1.80, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    # Crown moldings — limestone wash
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_S",'X',ROOM_W,0.0,+0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_BELL_BRONZE})


def build_stained_glass_window():
    # Tall arched window centered on the N wall (above altar). Three vertical panels.
    make_box("Window_Frame", (0.0, ROOM_D-0.04, 2.20), (1.60, 0.04, 1.40), COL_BELL_BRONZE)
    panels = [(-0.50, COL_STAINED_R), (0.0, COL_STAINED_B), (+0.50, COL_STAINED_G)]
    for i, (px, pc) in enumerate(panels):
        make_box(f"Stained_{i}", (px, ROOM_D-0.06, 2.20), (0.42, 0.005, 1.20), pc)
    # Arched top — three small half-discs
    for i, px in enumerate([-0.50, 0.0, +0.50]):
        make_cyl(f"Stained_Arch_{i}", (px, ROOM_D-0.06, 2.96), 0.21, 0.005,
                 (0.96, 0.84, 0.62, 0.65), axis='Y', segments=10)


def build_altar():
    ax, ay = 0.0, ROOM_D - 1.20
    make_box("Altar_Base", (ax, ay, 0.50), (1.30, 0.50, 1.00), COL_ALTAR)
    make_box("Altar_Top",  (ax, ay, 1.04), (1.40, 0.56, 0.04), COL_ALTAR)
    # Altar cloth front
    make_box("Altar_Cloth", (ax, ay-0.30, 0.50), (1.34, 0.005, 1.00), COL_ALTAR_CLOTH)
    # Candle pair + crucifix
    for sgn in (-1, +1):
        make_cyl(f"Altar_Candle_{sgn:+d}", (ax + sgn*0.40, ay, 1.18), 0.04, 0.24, P.PAPER)
        make_cyl(f"Altar_Candle_Flame_{sgn:+d}", (ax + sgn*0.40, ay, 1.34), 0.025, 0.04, COL_VOTIVE)
    make_box("Altar_Crucifix_V", (ax, ay, 1.40), (0.04, 0.04, 0.40), COL_PEW_WOOD)
    make_box("Altar_Crucifix_H", (ax, ay, 1.50), (0.20, 0.04, 0.04), COL_PEW_WOOD)
    # Votive rack to the right of the altar
    vx, vy = +1.40, ay - 0.20
    make_box("Votive_Rack", (vx, vy, 0.42), (0.30, 0.30, 0.10), COL_BELL_BRONZE)
    for i in range(6):
        cx = vx - 0.20 + (i % 3) * 0.20
        cy = vy - 0.10 + (i // 3) * 0.20
        make_cyl(f"Votive_{i}", (cx, cy, 0.50), 0.025, 0.06, COL_VOTIVE)
        make_cyl(f"Votive_Flame_{i}", (cx, cy, 0.58), 0.018, 0.03, COL_VOTIVE)


def build_pews():
    # Two short kneelers in the center, oriented to face the altar.
    for pi, py in enumerate([2.00, 3.80]):
        make_box(f"Pew_{pi}_Seat",   (0.0, py, 0.46), (2.20, 0.40, 0.06), COL_PEW_WOOD)
        make_box(f"Pew_{pi}_Back",   (0.0, py-0.20, 0.80), (2.20, 0.06, 0.68), COL_PEW_WOOD)
        make_box(f"Pew_{pi}_Kneeler", (0.0, py+0.32, 0.12), (2.20, 0.16, 0.06), COL_PEW_WOOD)
        for sgn in (-1, +1):
            make_box(f"Pew_{pi}_End_{sgn:+d}", (sgn*1.12, py, 0.46), (0.04, 0.40, 0.80), COL_PEW_WOOD)


def build_statue_niche():
    # Recessed niche on the E wall with a small Madonna figure.
    nx, ny = ROOM_W/2.0 - 0.14, 3.40
    make_box("Niche_Recess", (nx-0.04, ny, 1.80), (0.20, 0.80, 1.20), (0.78, 0.74, 0.66, 1.0))
    # Statue (stylised: pedestal + body + head)
    make_box("Statue_Pedestal", (nx-0.20, ny, 1.30), (0.16, 0.20, 0.10), COL_STATUE)
    make_cyl("Statue_Body", (nx-0.20, ny, 1.62), 0.10, 0.50, COL_STATUE, segments=10)
    make_cyl("Statue_Head", (nx-0.20, ny, 1.96), 0.07, 0.16, COL_STATUE, segments=10)


def build_bell_pull():
    # Rope dangling from ceiling in SW corner.
    bx, by = -ROOM_W/2.0 + 0.40, 0.60
    make_box("BellPull_Rope", (bx, by, 1.70), (0.04, 0.04, 1.60), COL_BELL_BRONZE)
    make_cyl("BellPull_Knot", (bx, by, 0.94), 0.08, 0.10, COL_BELL_BRONZE)


def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, 3.5, CEIL))
    make_sprinkler("Spr", (0.0, 1.5, CEIL))
    # Hanging brass pendant over the altar
    make_cyl("Pendant_Cord", (0.0, ROOM_D-1.20, CEIL-0.40), 0.012, 0.80, P.METAL_BLACK)
    make_cyl("Pendant_Bowl", (0.0, ROOM_D-1.20, CEIL-0.96), 0.16, 0.08, COL_BELL_BRONZE)


def build_decor():
    make_wall_clock("Clock", (-ROOM_W/2.0+0.05, 5.5, 2.20), frozen_hour=4, frozen_min=15)
    make_floor_plant("Plant_SE", (ROOM_W/2.0-0.60, 0.60, 0.0), palette={"leaf": (0.42, 0.52, 0.36, 1.0)})
    make_faded_poster("Poster", (-ROOM_W/2.0+0.05, 1.8, 1.50))


def main():
    clear_scene()
    build_shell()
    build_stained_glass_window()
    build_altar()
    build_pews()
    build_statue_niche()
    build_bell_pull()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/roadside_chapel.glb"))
    print(f"\n[build_roadside_chapel] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
