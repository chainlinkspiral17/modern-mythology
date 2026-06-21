"""XI · JUSTICE — Graustark Parish Courthouse. Small-claims
courtroom interior: judge's bench on a raised dais, witness stand
to the judge's right, jury box of six chairs along the W wall, two
counsel tables, three rows of public pews S. Wood-paneled walls,
single-pane arched window N behind the bench. Erica + Anna's room.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding
from _props.decor import make_wall_clock, make_floor_plant, make_faded_poster
from _props.safety import (make_smoke_detector, make_sprinkler,
                            make_fluorescent_tube_fixture)

PAL = {"wall": (0.62, 0.52, 0.42, 1.0), "baseboard": (0.32, 0.22, 0.16, 1.0)}
COL_FLOOR_PARQUET = (0.62, 0.42, 0.28, 1.0); COL_SEAM = (0.32, 0.22, 0.16, 1.0)
COL_WOOD_DARK = (0.32, 0.22, 0.14, 1.0); COL_WOOD_MID = (0.52, 0.36, 0.24, 1.0)
COL_BENCH_TOP = (0.42, 0.28, 0.18, 1.0); COL_GAVEL = (0.22, 0.14, 0.10, 1.0)
COL_LEATHER = (0.42, 0.20, 0.18, 1.0); COL_BRASS = (0.74, 0.56, 0.28, 1.0)
COL_FLAG_RED = (0.74, 0.22, 0.20, 1.0); COL_FLAG_BLUE = (0.20, 0.30, 0.52, 1.0)
COL_FLAG_WHITE = (0.92, 0.90, 0.84, 1.0); COL_SCALES = (0.62, 0.46, 0.26, 1.0)
COL_WINDOW_GLASS = (0.74, 0.84, 0.86, 0.55)

ROOM_W = 11.0; ROOM_D = 12.0; CEIL = 4.40


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_PARQUET, "seam": COL_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    # S wall — single center door opening
    make_wall("Wall_S_W", (-3.0, 0.0, 0), length=5.0, height=CEIL, axis='X', palette=PAL)
    make_wall("Wall_S_E", (+3.0, 0.0, 0), length=5.0, height=CEIL, axis='X', palette=PAL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    for nm, ax, length, wx, wy in [("Crown_W",'Y',ROOM_D,-ROOM_W/2.0+0.10,ROOM_D/2.0),
                                    ("Crown_E",'Y',ROOM_D,+ROOM_W/2.0-0.10,ROOM_D/2.0),
                                    ("Crown_N",'X',ROOM_W,0.0,ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_WOOD_DARK})
    # Wainscoting band on all walls
    for nm, axis, length, wx, wy, sign in [
        ("Wains_W", 'Y', ROOM_D, -ROOM_W/2.0 + 0.06, ROOM_D/2.0, +1),
        ("Wains_E", 'Y', ROOM_D, +ROOM_W/2.0 - 0.06, ROOM_D/2.0, -1),
        ("Wains_N", 'X', ROOM_W, 0.0, ROOM_D - 0.06, -1)]:
        if axis == 'Y':
            make_box(nm, (wx, wy, 1.10), (0.08, length, 1.20), COL_WOOD_DARK)
        else:
            make_box(nm, (wx, wy, 1.10), (length, 0.08, 1.20), COL_WOOD_DARK)


def build_arched_window_behind_bench():
    # Tall arched window centered on N wall above the judge's bench
    make_box("Window_Frame", (0.0, ROOM_D-0.04, 3.20), (2.40, 0.04, 1.80), COL_BRASS)
    make_box("Window_Glass", (0.0, ROOM_D-0.06, 3.20), (2.20, 0.005, 1.60), COL_WINDOW_GLASS)
    # Arch top — three half-discs
    for i, px in enumerate([-0.60, 0.0, +0.60]):
        make_cyl(f"Window_Arch_{i}", (px, ROOM_D-0.06, 4.10), 0.30, 0.005,
                 COL_WINDOW_GLASS, axis='Y', segments=10)


def build_judge_bench_and_dais():
    # Raised dais (0.30 m high) running across N section
    make_box("Dais", (0.0, ROOM_D-1.80, 0.15), (4.00, 1.40, 0.30), COL_WOOD_DARK)
    # Judge's bench — long lectern with leather top
    by = ROOM_D - 2.20
    make_box("Bench_Front", (0.0, by, 1.20), (3.60, 0.20, 1.80), COL_WOOD_DARK)
    make_box("Bench_Counter_Top", (0.0, by, 1.42), (3.60, 0.50, 0.06), COL_BENCH_TOP)
    # Side wings
    make_box("Bench_Wing_W", (-1.80, by-0.10, 1.20), (0.20, 0.60, 1.80), COL_WOOD_DARK)
    make_box("Bench_Wing_E", (+1.80, by-0.10, 1.20), (0.20, 0.60, 1.80), COL_WOOD_DARK)
    # Judge's high-back chair (S-facing)
    make_box("Judge_Chair_Seat", (0.0, by-0.40, 0.66), (0.60, 0.50, 0.06), COL_LEATHER)
    make_box("Judge_Chair_Back", (0.0, by-0.50, 1.20), (0.60, 0.10, 1.20), COL_LEATHER)
    # Gavel + sound block on the bench top
    make_box("Sound_Block", (-0.40, by+0.20, 1.46), (0.20, 0.16, 0.04), COL_BENCH_TOP)
    make_cyl("Gavel_Handle", (-0.40, by+0.20, 1.52), 0.018, 0.20, COL_GAVEL, axis='X')
    make_cyl("Gavel_Head", (-0.20, by+0.20, 1.52), 0.05, 0.08, COL_GAVEL)
    # Scales of justice
    make_cyl("Scales_Post", (+0.40, by+0.20, 1.62), 0.014, 0.30, COL_SCALES)
    make_box("Scales_Beam", (+0.40, by+0.20, 1.76), (0.30, 0.02, 0.02), COL_SCALES)
    for sgn in (-1, +1):
        make_cyl(f"Scales_Pan_{sgn:+d}", (+0.40 + sgn*0.14, by+0.20, 1.66),
                 0.06, 0.02, COL_SCALES, segments=10)


def build_witness_stand():
    # Small box on the dais to the judge's right (E side)
    wx, wy = +2.40, ROOM_D - 2.40
    make_box("Witness_Stand_Front", (wx, wy, 0.70), (0.60, 0.20, 1.00), COL_WOOD_DARK)
    make_box("Witness_Stand_Top",   (wx, wy, 1.24), (0.70, 0.30, 0.04), COL_BENCH_TOP)
    make_box("Witness_Chair_Seat", (wx, wy-0.30, 0.46), (0.40, 0.40, 0.04), COL_LEATHER)
    make_box("Witness_Chair_Back", (wx, wy-0.46, 0.86), (0.40, 0.06, 0.74), COL_LEATHER)


def build_jury_box():
    # Six chairs in two rows along the W wall (jurors face E)
    for ji in range(6):
        col_ = ji % 3
        row = ji // 3
        jx = -ROOM_W/2.0 + 0.80 + row * 0.70
        jy = ROOM_D/2.0 - 1.20 + (col_ - 1) * 0.70
        make_box(f"Juror_Chair_Seat_{ji}", (jx, jy, 0.46), (0.40, 0.40, 0.04), COL_LEATHER)
        make_box(f"Juror_Chair_Back_{ji}", (jx+0.16, jy, 0.86), (0.04, 0.40, 0.74), COL_LEATHER)
    # Jury box railing
    make_box("Jury_Rail_S", (-ROOM_W/2.0 + 1.50, ROOM_D/2.0 + 1.40, 1.00),
             (2.00, 0.04, 0.80), COL_WOOD_DARK)
    make_box("Jury_Rail_N", (-ROOM_W/2.0 + 1.50, ROOM_D/2.0 - 2.00, 1.00),
             (2.00, 0.04, 0.80), COL_WOOD_DARK)
    make_box("Jury_Rail_E", (-ROOM_W/2.0 + 2.50, ROOM_D/2.0, 1.00),
             (0.04, 3.60, 0.80), COL_WOOD_DARK)


def build_counsel_tables():
    # Two tables facing the bench
    for ti, (tx, label) in enumerate([(-1.50, "Plaintiff"), (+1.50, "Defense")]):
        ty = ROOM_D/2.0 - 0.50
        make_box(f"Table_{ti}_Top",  (tx, ty, 0.74), (1.40, 0.80, 0.04), COL_WOOD_MID)
        make_box(f"Table_{ti}_Body", (tx, ty, 0.40), (1.36, 0.76, 0.68), COL_WOOD_MID)
        # Two chairs per table (S-facing, attorneys)
        for ci, csgn in enumerate([-0.40, +0.40]):
            make_box(f"Table_{ti}_Chair_Seat_{ci}", (tx+csgn, ty-0.60, 0.46),
                     (0.40, 0.40, 0.04), COL_LEATHER)
            make_box(f"Table_{ti}_Chair_Back_{ci}", (tx+csgn, ty-0.80, 0.86),
                     (0.40, 0.04, 0.74), COL_LEATHER)
        # Folder / papers on the table
        make_box(f"Table_{ti}_Folder", (tx-0.30, ty, 0.78), (0.30, 0.20, 0.02),
                 (0.62, 0.42, 0.20, 1.0))


def build_public_pews():
    # Three pews S of the bar separating audience from well
    for pi in range(3):
        py = 1.50 + pi * 1.20
        make_box(f"Pew_{pi}_Seat", (0.0, py, 0.46), (5.20, 0.50, 0.06), COL_WOOD_DARK)
        make_box(f"Pew_{pi}_Back", (0.0, py-0.22, 0.84), (5.20, 0.06, 0.70), COL_WOOD_DARK)
    # The bar (low railing separating well from audience)
    make_box("Bar_Rail", (0.0, 4.20, 1.00), (5.40, 0.04, 0.86), COL_WOOD_DARK)
    make_box("Bar_Cap",  (0.0, 4.20, 1.46), (5.40, 0.08, 0.06), COL_BENCH_TOP)


def build_flag_and_seal():
    # American flag NE corner, state flag NW corner — abstracted
    for ci, (cx, fc1, fc2) in enumerate([(-3.20, COL_FLAG_RED, COL_FLAG_WHITE),
                                          (+3.20, COL_FLAG_BLUE, COL_FLAG_WHITE)]):
        make_cyl(f"Flag_Pole_{ci}", (cx, ROOM_D-0.30, 2.20), 0.04, 4.20, COL_BRASS, segments=8)
        # Flag drape (alternating stripes via two boxes)
        make_box(f"Flag_Drape_R_{ci}", (cx+0.40, ROOM_D-0.30, 3.50), (0.60, 0.04, 0.40), fc1)
        make_box(f"Flag_Drape_W_{ci}", (cx+0.40, ROOM_D-0.30, 3.10), (0.60, 0.04, 0.40), fc2)
    # Court seal mounted high above the bench arched window
    make_box("Seal_Mount", (0.0, ROOM_D-0.04, 4.10), (0.80, 0.04, 0.40), COL_WOOD_DARK)
    make_cyl("Seal", (0.0, ROOM_D-0.06, 4.10), 0.34, 0.04, COL_BRASS, axis='Y', segments=18)


def build_ceiling_infra():
    for j, ypos in enumerate([3.5, 7.0, 10.0]):
        make_fluorescent_tube_fixture(f"Fluor_{j}", (0.0, ypos, CEIL),
                                       length=2.20, width=0.32,
                                       palette={"diffuser": (0.96, 0.94, 0.86, 1.0)})
    make_smoke_detector("Smoke", (0.0, 4.0, CEIL))
    make_sprinkler("Spr_W", (-3.0, 6.0, CEIL))
    make_sprinkler("Spr_E", (+3.0, 6.0, CEIL))


def build_decor():
    make_wall_clock("Clock", (+ROOM_W/2.0-0.05, 6.0, 3.20), frozen_hour=4, frozen_min=15)
    make_floor_plant("Plant_SE", (+ROOM_W/2.0-0.40, 0.40, 0.0),
                     palette={"leaf": (0.40, 0.46, 0.30, 1.0)})
    make_floor_plant("Plant_SW", (-ROOM_W/2.0+0.40, 0.40, 0.0),
                     palette={"leaf": (0.40, 0.46, 0.30, 1.0)})
    make_faded_poster("Notice", (-ROOM_W/2.0+0.05, 1.5, 1.80))


def main():
    clear_scene()
    build_shell()
    build_arched_window_behind_bench()
    build_judge_bench_and_dais()
    build_witness_stand()
    build_jury_box()
    build_counsel_tables()
    build_public_pews()
    build_flag_and_seal()
    build_ceiling_infra()
    build_decor()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/courthouse_chamber.glb"))
    print(f"\n[build_courthouse_chamber] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
