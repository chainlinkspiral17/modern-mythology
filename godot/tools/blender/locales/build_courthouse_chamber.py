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


def build_justice_dressing():
    """Scene-description specifics from setup_motion_to_dismiss.json:
      · "Department 3" placard on the door
      · The case-caption page on Anna's plaintiff's table:
        AVANT v. TESSIER HOLDINGS
      · Tessier's counsel's bound motion (the motion to dismiss
        for failure to state a claim) on the defense table
      · Two coffee cups · one at each counsel table · neither
        Anna nor opposing counsel has touched theirs
      · An empty jury box (this is a bench matter) made visible
        as bare seats with no notepads on them
      · The judge's gavel resting on the bench (it has not yet
        been used this morning)
    """
    # Approximate plaintiff's table: (-1.6, +2.5); defense: (+1.6, +2.5)
    table_top_z = 0.78

    # ── DEPT 3 placard on the courtroom door (south wall) ──
    placard_x = -3.40
    placard_y = -3.95
    make_box("Dept3_Placard_Backing",
             (placard_x, placard_y, 2.20),
             (0.30, 0.005, 0.20),
             (0.78, 0.62, 0.30, 1.0))   # brass plaque
    make_box("Dept3_Placard_Text",
             (placard_x, placard_y - 0.003, 2.20),
             (0.22, 0.001, 0.10),
             (0.20, 0.16, 0.10, 1.0))

    # ── Avant v. Tessier · case caption on plaintiff's table ──
    pt_x = -1.60
    pt_y = +2.50
    # Caption page (cream paper)
    make_box("AvantCaption_Page",
             (pt_x - 0.20, pt_y, table_top_z + 0.012),
             (0.22, 0.30, 0.002),
             (0.94, 0.90, 0.80, 1.0))
    # Letterhead block (a darker rectangle at the top)
    make_box("AvantCaption_Letterhead",
             (pt_x - 0.20, pt_y + 0.10, table_top_z + 0.0135),
             (0.20, 0.06, 0.0005),
             (0.20, 0.16, 0.12, 1.0))
    # Case caption lines · 5 darker text strips
    for li in range(5):
        make_box("AvantCaption_Line_%d" % li,
                 (pt_x - 0.20, pt_y + 0.02 - li * 0.04, table_top_z + 0.014),
                 (0.18, 0.016, 0.0005),
                 (0.18, 0.16, 0.10, 1.0))
    # Anna's pen alongside
    make_cyl("AnnaPen",
             (pt_x - 0.05, pt_y + 0.16, table_top_z + 0.014),
             0.006, 0.14,
             (0.18, 0.16, 0.14, 1.0),
             segments=4, axis='Y')
    # Anna's coffee (untouched)
    make_cyl("AnnaCoffeeCup_Body",
             (pt_x + 0.18, pt_y, table_top_z + 0.06),
             0.040, 0.10,
             (0.94, 0.90, 0.82, 1.0),
             segments=10, axis='Z')
    # Coffee level inside (almost full)
    make_cyl("AnnaCoffeeCup_Liquid",
             (pt_x + 0.18, pt_y, table_top_z + 0.095),
             0.036, 0.005,
             (0.30, 0.18, 0.10, 1.0),
             segments=10, axis='Z')

    # ── Tessier's bound motion on defense table ──
    dt_x = +1.60
    dt_y = +2.50
    # Bound brief (heavier, oxblood)
    make_box("TessierBrief_Body",
             (dt_x - 0.16, dt_y, table_top_z + 0.020),
             (0.22, 0.30, 0.040),
             (0.42, 0.20, 0.16, 1.0))
    # Title page (cream label)
    make_box("TessierBrief_Title",
             (dt_x - 0.16, dt_y, table_top_z + 0.041),
             (0.18, 0.26, 0.001),
             (0.92, 0.88, 0.78, 1.0))
    # "MOTION TO DISMISS" text line
    make_box("TessierBrief_TitleText",
             (dt_x - 0.16, dt_y + 0.08, table_top_z + 0.0415),
             (0.14, 0.020, 0.0005),
             (0.20, 0.16, 0.10, 1.0))
    # Brass binding clip at the spine
    make_box("TessierBrief_BindingClip",
             (dt_x - 0.16 - 0.115, dt_y, table_top_z + 0.020),
             (0.005, 0.30, 0.040),
             (0.78, 0.62, 0.30, 1.0))
    # Defense counsel's coffee (also untouched, full)
    make_cyl("DefenseCoffeeCup_Body",
             (dt_x + 0.18, dt_y, table_top_z + 0.06),
             0.040, 0.10,
             (0.94, 0.90, 0.82, 1.0),
             segments=10, axis='Z')

    # ── Empty jury box · 12 seats with no notepads ──
    # Jury box approx at (-3.0, +1.0)
    jb_x = -3.0
    jb_y = +1.0
    for ri in range(2):
        for ci in range(6):
            sx = jb_x + ci * 0.30
            sy = jb_y + ri * 0.40
            # Seat (empty)
            make_box("JurySeat_%d_%d" % (ri, ci),
                     (sx, sy, 0.46),
                     (0.26, 0.26, 0.04),
                     (0.42, 0.30, 0.22, 1.0))
            # The seat back stub
            make_box("JurySeatBack_%d_%d" % (ri, ci),
                     (sx, sy + 0.12, 0.78),
                     (0.26, 0.04, 0.50),
                     (0.42, 0.30, 0.22, 1.0))

    # ── Judge's gavel on the bench ──
    # Bench approx at (0, +4.5, dais height 1.06)
    gavel_x = +0.40
    gavel_y = +4.50
    bench_top_z = 1.06
    # Head
    make_cyl("Gavel_Head",
             (gavel_x, gavel_y, bench_top_z + 0.04),
             0.022, 0.08,
             (0.42, 0.28, 0.16, 1.0),
             segments=8, axis='Z')
    # Handle (cylinder running east)
    make_cyl("Gavel_Handle",
             (gavel_x + 0.10, gavel_y, bench_top_z + 0.04),
             0.012, 0.16,
             (0.42, 0.28, 0.16, 1.0),
             segments=6, axis='X')
    # Wooden sound block
    make_box("Gavel_SoundBlock",
             (gavel_x - 0.04, gavel_y, bench_top_z + 0.012),
             (0.10, 0.10, 0.024),
             (0.32, 0.22, 0.14, 1.0))


def build_justice_wave2_props():
    """Named props from setup_chambers_at_nine.json and
    setup_post_decision_review.json.

    chambers_at_nine (8:48 AM · Erica's chambers, off-record):
      · Chambers-corridor placard 'HON. ERICA PELLETIER · CHAMBERS'
      · Erica's judge_desk in the back (through the corridor door)
        with her robe on a hook
      · The bakery bag on the corridor bench with two croissants
      · Marcellette Dupré's clerk_desk to the side of the bench

    post_decision_review (11:18 AM · readiness conference · three
    weeks after the motion denial):
      · Lucien Avant alone in the second_pew (the small suit-shape
        at the back of the room)
      · The supplemental disclosure folder on the plaintiff's table
        (bulging manila with a certified-mail green card stapled)
      · Marcellette at the clerk_desk with the corrected index page
        tabbed ready
      · Walter Reynaud's brown leather briefcase on the defense
        table (his silver-hair-tell)
    """
    table_top_z = 0.78

    # ── chambers_at_nine ────────────────────────────────────────
    # Chambers corridor is off the courtroom's north wall behind the
    # bench. We build a short protruding hallway stub at (0, +5.5)
    # and put the placard and bench visually adjacent.

    # Chambers-corridor placard on the wall between courtroom and chambers
    make_box("Chambers_Placard_Backing",
             (+3.20, +5.50, 2.20),
             (0.005, 0.42, 0.16),
             (0.78, 0.62, 0.30, 1.0))   # brass
    make_box("Chambers_Placard_Text",
             (+3.203, +5.50, 2.20),
             (0.001, 0.36, 0.08),
             (0.20, 0.16, 0.10, 1.0))

    # A small bench in the corridor (where the bakery bag sits)
    corridor_x = +3.40
    corridor_y = +5.10
    make_box("Chambers_CorridorBench_Seat",
             (corridor_x, corridor_y, 0.44),
             (0.28, 0.60, 0.05),
             (0.42, 0.30, 0.22, 1.0))
    make_box("Chambers_CorridorBench_Back",
             (corridor_x + 0.13, corridor_y, 0.78),
             (0.05, 0.60, 0.36),
             (0.42, 0.30, 0.22, 1.0))
    # The Boutte-Street bakery bag on the bench (paper bag)
    make_box("Chambers_BakeryBag_Body",
             (corridor_x - 0.02, corridor_y + 0.10, 0.52),
             (0.18, 0.18, 0.14),
             (0.86, 0.72, 0.42, 1.0))
    # A rolled-top on the bag
    make_box("Chambers_BakeryBag_Rolltop",
             (corridor_x - 0.02, corridor_y + 0.10, 0.61),
             (0.18, 0.18, 0.02),
             (0.72, 0.60, 0.34, 1.0))
    # Two croissants visible at the top of the bag (crescent
    # approximations · two brown ovals)
    for ci, dx in enumerate([-0.04, +0.04]):
        make_cyl("Chambers_Croissant_%d" % ci,
                 (corridor_x + dx, corridor_y + 0.10, 0.66),
                 0.05, 0.04,
                 (0.78, 0.58, 0.28, 1.0), segments=8, axis='Z')

    # Erica's judge_desk in the chambers area behind the corridor
    # (this is inside chambers, adjacent to the corridor bench)
    desk_x = +3.80
    desk_y = +6.00
    # Desk top
    make_box("Erica_JudgeDesk_Top",
             (desk_x, desk_y, table_top_z),
             (0.90, 0.50, 0.04),
             (0.28, 0.18, 0.14, 1.0))
    # Desk drawers (side)
    make_box("Erica_JudgeDesk_Drawers",
             (desk_x + 0.30, desk_y, 0.40),
             (0.30, 0.50, 0.72),
             (0.24, 0.16, 0.12, 1.0))
    # Desk lamp
    make_cyl("Erica_JudgeDesk_LampPost",
             (desk_x - 0.32, desk_y + 0.12, table_top_z + 0.20),
             0.008, 0.36,
             (0.62, 0.62, 0.60, 1.0), segments=6, axis='Z')
    make_cyl("Erica_JudgeDesk_LampShade",
             (desk_x - 0.32, desk_y + 0.12, table_top_z + 0.38),
             0.08, 0.08,
             (0.94, 0.86, 0.62, 1.0), segments=10, axis='Z')
    # Erica's robe on a hook on the chambers wall
    make_box("Erica_Robe_Hanger",
             (+3.90, +6.60, 1.90),
             (0.20, 0.02, 0.03),
             (0.62, 0.62, 0.60, 1.0))
    make_box("Erica_Robe_Body",
             (+3.90, +6.60, 1.30),
             (0.40, 0.06, 0.90),
             (0.14, 0.12, 0.10, 1.0))   # black judicial robe

    # ── Marcellette's clerk desk to the side of the bench ──
    # She's beside the judge's bench · at (-3.20, +4.20)
    md_x = -3.20
    md_y = +4.20
    make_box("Marcellette_ClerkDesk_Top",
             (md_x, md_y, table_top_z),
             (0.70, 0.42, 0.04),
             (0.32, 0.22, 0.16, 1.0))
    make_box("Marcellette_ClerkDesk_Drawers",
             (md_x, md_y - 0.16, 0.40),
             (0.70, 0.10, 0.72),
             (0.28, 0.20, 0.14, 1.0))
    # The court clerk's typewriter (IBM Selectric-ish · gray box)
    make_box("Marcellette_Typewriter_Body",
             (md_x, md_y + 0.02, table_top_z + 0.08),
             (0.34, 0.28, 0.14),
             (0.72, 0.72, 0.70, 1.0))
    make_box("Marcellette_Typewriter_Paper",
             (md_x, md_y + 0.12, table_top_z + 0.16),
             (0.20, 0.001, 0.10),
             (0.94, 0.90, 0.80, 1.0))

    # ── post_decision_review ────────────────────────────────────

    # Lucien Avant alone in the second_pew (the second row from the
    # back). Public pews are behind the counsel-tables area.
    avant_x = 0.0
    avant_y = -1.80   # second pew
    # A single suit-shape approximation on the pew (a small hunched
    # figure). We'll use two boxes: torso + head. Existing pews
    # provide the seat.
    make_box("Avant_Suit_Torso",
             (avant_x, avant_y, 0.98),
             (0.30, 0.20, 0.44),
             (0.24, 0.20, 0.18, 1.0))   # dark suit
    make_cyl("Avant_Suit_Head",
             (avant_x, avant_y, 1.30),
             0.09, 0.14,
             (0.78, 0.62, 0.52, 1.0),   # skin-tone approx
             segments=10, axis='Z')

    # The supplemental disclosure folder on the plaintiff's table
    pt_x = -1.60
    pt_y = +2.50
    make_box("SupplementalDisclosure_Folder",
             (pt_x + 0.24, pt_y - 0.04, table_top_z + 0.020),
             (0.24, 0.32, 0.036),
             (0.72, 0.60, 0.30, 1.0))   # manila
    # A stapled certified-mail green card
    make_box("SupplementalDisclosure_GreenCard",
             (pt_x + 0.30, pt_y + 0.10, table_top_z + 0.041),
             (0.10, 0.14, 0.001),
             (0.24, 0.62, 0.36, 1.0))
    # Small staple mark
    make_box("SupplementalDisclosure_Staple",
             (pt_x + 0.30, pt_y + 0.16, table_top_z + 0.042),
             (0.008, 0.02, 0.0008),
             (0.72, 0.72, 0.72, 1.0))

    # Walter Reynaud's brown leather briefcase on the defense table
    dt_x = +1.60
    dt_y = +2.50
    make_box("Reynaud_Briefcase_Body",
             (dt_x + 0.30, dt_y - 0.06, table_top_z + 0.09),
             (0.30, 0.20, 0.16),
             (0.42, 0.24, 0.14, 1.0))
    # Handle
    make_box("Reynaud_Briefcase_Handle",
             (dt_x + 0.30, dt_y - 0.06, table_top_z + 0.20),
             (0.14, 0.02, 0.03),
             (0.42, 0.24, 0.14, 1.0))
    # Gold catch
    make_box("Reynaud_Briefcase_Catch",
             (dt_x + 0.30, dt_y - 0.16, table_top_z + 0.09),
             (0.04, 0.008, 0.02),
             (0.86, 0.68, 0.32, 1.0))


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
    build_justice_dressing()
    build_justice_wave2_props()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/courthouse_chamber.glb"))
    print(f"\n[build_courthouse_chamber] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
