"""Maya Daigle's bedroom — upstairs at her grandmother's house,
lot 7 Phase I, Harmony Creek Estates — vol6 hero locale (9 VN
scene refs: vol6_ch0_prelude, ch1/ch2/ch6 maya_bedroom, ch4
maya_floor, ch5_radio close, ch14_live_oak, ch21_porch close,
ch23_sleep).

An original-1991 HCE house (the scene JSONs name the grandmother
Ms. LINDA CALDWELL / "the Caldwell cul-de-sac"; the older
maya_daigle.md lore doc says Connie Daigle — the JSONs are treated
as current). Maya is sixteen: zine cartoonist (NEWS FROM HARMONY
CREEK, "by M.D."), the room is a working studio disguised as a
bedroom. Canon baked in:

  · vol6_ch1/ch2/ch6/ch14 — THE THINKPAD, open on the desk (the
    F.T. chat window is the volume's mainline). Screen faces the
    desk chair; a pale chat rectangle is lit on the lid.
  · vol6_ch0_prelude — the spiral notebook she writes in
    cross-legged on the bed at 6:16; ch2 "she does not, tonight,
    write in the notebook. She lies down. She turns off the
    lamp." — notebook + pen + lamp on the nightstand.
  · vol6_ch14 — "her phone on the nightstand".
  · vol6_ch6 / ch21 — "the pale yellow ceiling" (flat drywall,
    house fixture — NOT commercial fluorescents; the scaffold's
    tube fixtures were Kwik Stop vocabulary and are gone).
  · vol6_ch4_maya_floor — "the original 1991 pine, worn to a soft
    honey color"; "counting boards from the window. Three in. The
    third board looks no different from the others." The boards
    run E-W and are counted south from the window wall. The third
    board is baked as its own mesh (Floor_Board3_FromWindow) in
    the SAME color — it must look no different — with its two end
    joints, and the rug lies over it ("The rug has been pulled
    back" — so the rug's resting state covers it). The envelope
    ("for whoever is ready") is inside the cavity: NOT modeled.
  · vol6_ch23_sleep — "The fan is on" (box fan by the window);
    "the cicadas are loud" (window); the school-supplies box from
    the New Auburn Walmart (binder / pens / index cards / the new
    notebook saved for the first day) staged by the desk.
  · vol6_ch1 — she lies down ON TOP of the bedspread: the bed is
    made, spread pulled square, pillow at the window end.
  · maya_daigle.md §I — zine production is FINELINER PEN + GREY
    MARKER, quarter-letter (3.5 × 4.25 in) pages; issue #23
    ("F.T.") pencils are complete and laid out on the desk with a
    pencil. Photocopying happens at the Cosmic Comics machine on
    Sunday mornings — NO copier, NO printer, NO typewriter here.
  · maya_daigle.md §II — GENERAL STORE: 187 pages of 8.5 × 11
    printer paper "stored in a single hardback portfolio she
    keeps under her bed" — the portfolio is under the bed, its
    east edge just proud of the rail. The paper supply (the ream
    Rick over-orders for her) sits on the bookcase.
  · maya_daigle.md §III — the A5 black sketchbook ("NOT FOR
    PUBLICATION · NOT YET · M.D.") closed on the desk, white
    label strip on the cover.
  · maya_daigle.md §V — THE CLOSET BOX (12 × 8 × 6 in, her
    father's last in-person gift; the mixtape, the printed F.T.
    chat logs, the Polaroid, the four ANYA tapes are all INSIDE
    it and are not modeled loose). Treatment matches Philip's box
    in the Cosmic back office: PRESENT, OCCLUDED, NEVER
    ANNOUNCED — it sits on the closet floor in the south bay,
    behind the closed bypass door panel, next to an ordinary
    shoebox. Nothing points at it.
  · Her working method ("text, comix, and small map fragments")
    dresses the wall: corkboard over the desk with pinned
    quarter-letter sheets + a small hand-drawn map fragment; two
    of her own ink drawings taped over the bed.
  · Exterior (second floor — ch4 "Maya goes downstairs", ch5 "the
    upstairs window is lit"): the porch roof directly below the
    window (ch14/ch21 porch canon), the cul-de-sac below, the
    cedar across the cul-de-sac (ch14 "the cicadas, in the cedar
    across the cul-de-sac"), and the Geller porch light at the
    end of the Caldwell cul-de-sac, on (ch23).

Canon-NEGATIVES honored (what this room does NOT have):
  · No radio, no shortwave, no boombox — the 1776 kHz radio is in
    the GRANDMOTHER'S room (ch2/ch5); the dual-cassette boombox is
    hers too (maya_daigle.md §IV).
  · No photocopier / printer / typewriter (Cosmic Comics Sundays).
  · No "THE FUND" jar (it lives at the Cosmic Comics back counter).
  · No cat bed — the half-Kowalski cat is at the Kowalskis'
    (ch23: "Maya is alone in her room").
  · No band/movie posters — the only wall art is her own work.
  · No commercial fluorescents, no crown molding (1991 tract).

Shell footprint kept from the scaffold (4 × 5 m, CEIL 2.6, door
gap in the south wall x −1..+1 — the Background3D camera preset
(0, 2.30, +0.5 / yaw 180 / fov 60) is tuned to it; closed door
leaf + infills per the Lena-apartment pattern, ch2 "She closes
her door."). Window is a REAL OPENING with frame + sash + muntins,
no glass (playbook no-transparency rule).

NOTE: build_caldwell_kitchen_night / _porch_night /
_radio_room_night are still raw scaffolds. When they get their
hero passes, graduate the CALDWELL_* constants below into a
shared KEEP-IN-SYNC block (Miller-house pattern).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_wall, make_door_hinges
from _props.safety import make_smoke_detector, make_hvac_vent

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 4.0; ROOM_D = 5.0; CEIL = 2.6

# ── CALDWELL HOUSE constants (graduate to a shared block when the
#    sibling caldwell_* rooms get their hero passes) ──────────────
CALDWELL_INT_WALL  = (0.90, 0.86, 0.75, 1.0)   # 1991 builder warm white
CALDWELL_BASEBOARD = (0.46, 0.35, 0.24, 1.0)
CALDWELL_TRIM      = (0.93, 0.91, 0.85, 1.0)   # painted door/window trim
CALDWELL_CEIL_YEL  = (0.93, 0.89, 0.70, 1.0)   # THE pale yellow ceiling
CALDWELL_PINE      = (0.72, 0.56, 0.36, 1.0)   # original pine, worn honey
CALDWELL_PINE_SEAM = (0.50, 0.37, 0.23, 1.0)
CALDWELL_SIDING    = (0.84, 0.80, 0.70, 1.0)   # exterior lap siding
CALDWELL_ROOF      = (0.33, 0.27, 0.23, 1.0)   # shingle (porch roof below)

# ── Maya's room palette (muted, purple-accented — her dyed tips) ─
COL_WOOD      = (0.50, 0.37, 0.24, 1.0)   # furniture pine/oak
COL_WOOD_DK   = (0.31, 0.23, 0.16, 1.0)
COL_PLUM      = (0.44, 0.36, 0.50, 1.0)   # the accent: bedspread/curtains
COL_PLUM_DK   = (0.32, 0.26, 0.38, 1.0)
COL_QUILT_BND = (0.60, 0.55, 0.46, 1.0)   # bedspread band
COL_LINEN     = (0.90, 0.88, 0.82, 1.0)
COL_CHARCOAL  = (0.16, 0.15, 0.16, 1.0)   # ThinkPad / portfolio
COL_SCREEN    = (0.10, 0.12, 0.16, 1.0)   # lid glass, dark
COL_CHATGLOW  = (0.84, 0.87, 0.84, 1.0)   # the lit chat window
COL_CORK      = (0.62, 0.47, 0.31, 1.0)
COL_INK       = (0.24, 0.22, 0.22, 1.0)   # fineliner ink
COL_PENCIL    = (0.58, 0.57, 0.55, 1.0)   # pencil-line grey
COL_MARKER_GY = (0.55, 0.55, 0.53, 1.0)   # her grey markers
COL_CARDBOARD = (0.66, 0.52, 0.34, 1.0)
COL_BRASS     = (0.70, 0.57, 0.30, 1.0)
COL_LAMP_GLOW = (0.98, 0.88, 0.62, 1.0)
COL_FAN_BODY  = (0.80, 0.79, 0.75, 1.0)
COL_NIGHT_LAWN = (0.22, 0.28, 0.18, 1.0)  # cul-de-sac below, dusk
COL_ASPHALT   = (0.16, 0.16, 0.17, 1.0)
COL_CONCRETE  = (0.50, 0.49, 0.45, 1.0)
COL_CEDAR     = (0.20, 0.30, 0.20, 1.0)   # the cedar across the cul-de-sac
COL_CEDAR_DK  = (0.15, 0.24, 0.16, 1.0)
COL_PORCHBULB = (1.00, 0.88, 0.60, 1.0)   # the Geller porch light, on
BOOK_TINTS = [(0.48, 0.30, 0.24, 1.0), (0.28, 0.36, 0.42, 1.0),
              (0.62, 0.54, 0.34, 1.0), (0.36, 0.30, 0.38, 1.0),
              (0.70, 0.64, 0.52, 1.0), (0.44, 0.36, 0.50, 1.0)]
GARMENT_TINTS = [(0.16, 0.15, 0.16, 1.0),   # the black hoodie
                 (0.48, 0.24, 0.20, 1.0),   # flannel
                 (0.30, 0.36, 0.46, 1.0),   # denim jacket
                 (0.55, 0.55, 0.53, 1.0)]   # grey tee

PAL_WALL = {"wall": CALDWELL_INT_WALL, "baseboard": CALDWELL_BASEBOARD}

# Window opening in the north wall (real opening, no glass)
WIN_W = 1.30                # opening x −0.65..+0.65
WIN_SILL = 0.95
WIN_HEAD = 2.15
WALL_N_FACE = ROOM_D - 0.10   # interior face y 4.9
GRADE_Z = -3.20               # cul-de-sac grade (second-floor room)
BOARD_W = 0.24                # pine board width — boards run E-W,
                              # counted SOUTH from the window (ch4)


# ═════════════════════════════════════════════════════════════════
# SHELL — original-1991 pine plank floor (boards run E-W; the
# THIRD BOARD FROM THE WINDOW is its own mesh, same color — "looks
# no different from the others", vol6_ch4), warm-white walls, the
# PALE YELLOW flat drywall ceiling (vol6_ch6/ch21), south door gap
# kept with a closed white four-panel door (ch2 "She closes her
# door"), no crown molding (1991 tract house).
# ═════════════════════════════════════════════════════════════════
def build_shell():
    # Floor slab + E-W board seams every 0.24 m from the window wall
    make_box("Floor_Slab", (0.0, ROOM_D / 2.0, -0.05), (ROOM_W + 0.4, ROOM_D + 0.4, 0.10),
             CALDWELL_PINE)
    for k in range(1, 21):
        sy = WALL_N_FACE - BOARD_W * k
        make_box(f"Floor_Seam_{k}", (0.0, sy, 0.001), (ROOM_W + 0.4, 0.018, 0.002),
                 CALDWELL_PINE_SEAM)
    # Scattered board end-joints (deterministic — no RNG)
    for ji, (jx, jy) in enumerate([(-1.2, 3.82), (0.9, 2.14), (-0.3, 1.42),
                                   (1.4, 4.54), (-1.6, 0.82), (0.4, 3.10)]):
        make_box(f"Floor_Joint_{ji}", (jx, jy, 0.001), (0.018, BOARD_W - 0.02, 0.002),
                 CALDWELL_PINE_SEAM)
    # THE THIRD BOARD FROM THE WINDOW (vol6_ch4) — board 3 spans
    # y 4.18..4.42. Its own mesh + its two end joints, floor color:
    # it must look no different. The cavity + envelope are beneath
    # it and are not modeled. The rug (build_rug) rests over it.
    make_box("Floor_Board3_FromWindow", (0.05, WALL_N_FACE - BOARD_W * 2.5, 0.0008),
             (1.20, BOARD_W - 0.02, 0.0016), CALDWELL_PINE)
    for ei, ex in enumerate((-0.55, 0.65)):
        make_box(f"Floor_Board3_Joint_{ei}", (ex, WALL_N_FACE - BOARD_W * 2.5, 0.001),
                 (0.018, BOARD_W - 0.02, 0.002), CALDWELL_PINE_SEAM)
    # Walls — west / east full runs
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall — REAL window opening x −0.65..+0.65
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20     # 1.55
    seg_cx = WIN_W / 2.0 + seg_len / 2.0              # 1.425
    make_wall("Wall_N_W", (-seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_SillFill", (0.0, ROOM_D, WIN_SILL / 2.0), (WIN_W, 0.20, WIN_SILL),
             CALDWELL_INT_WALL)
    make_box("Wall_N_HeadFill", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.20, CEIL - WIN_HEAD), CALDWELL_INT_WALL)
    # South wall — scaffold door gap x −1..+1 kept (camera preset)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             CALDWELL_INT_WALL)
    # Gap infill either side of the 0.90 m door leaf
    for nm, fx in [("Wall_S_FillW", -0.725), ("Wall_S_FillE", +0.725)]:
        make_box(nm, (fx, 0.0, 1.15), (0.55, 0.20, 2.30), CALDWELL_INT_WALL)
    # THE PALE YELLOW CEILING (vol6_ch6: "The pale yellow ceiling.")
    make_box("Ceil_Plane", (0.0, ROOM_D / 2.0, CEIL + 0.05),
             (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), CALDWELL_CEIL_YEL)


# ═════════════════════════════════════════════════════════════════
# DOOR — closed white four-panel leaf in the south gap (ch2 "She
# closes her door."), casing, brass knob, hinges. Her school
# backpack leans on the wall east of it (ch23 — packed for the
# first morning).
# ═════════════════════════════════════════════════════════════════
def build_door():
    make_box("Door_Leaf", (0.0, 0.03, 1.03), (0.90, 0.05, 2.06), CALDWELL_TRIM)
    for ci, px in enumerate((-0.20, +0.20)):
        for ri, (pz, ph) in enumerate([(0.60, 0.75), (1.52, 0.85)]):
            make_box(f"Door_Panel_{ci}_{ri}", (px, 0.062, pz), (0.30, 0.012, ph),
                     (0.86, 0.84, 0.78, 1.0))
    make_cyl("Door_Knob", (0.35, 0.075, 0.98), 0.028, 0.045, COL_BRASS, axis='Y')
    make_door_hinges("Door_Hinge", edge_x=-0.43, edge_y=0.06,
                     edge_z_centers=[0.35, 1.03, 1.75], axis='X')
    for sgn in (-1, +1):
        make_box(f"Door_Casing_{sgn:+d}", (sgn * 0.50, 0.11, 1.06), (0.09, 0.05, 2.12),
                 CALDWELL_TRIM)
    make_box("Door_CasingHead", (0.0, 0.11, 2.16), (1.09, 0.05, 0.10), CALDWELL_TRIM)
    # Backpack against the wall east of the door (ch23 — she lays
    # the supplies out "in the order she will pack them")
    make_box("Backpack_Body", (0.78, 0.28, 0.24), (0.28, 0.18, 0.48), COL_PLUM_DK)
    make_box("Backpack_Pocket", (0.78, 0.40, 0.16), (0.22, 0.06, 0.24), COL_PLUM)
    make_box("Backpack_Strap", (0.66, 0.30, 0.30), (0.04, 0.14, 0.34),
             (0.24, 0.20, 0.28, 1.0))


# ═════════════════════════════════════════════════════════════════
# WINDOW — the north-wall window (cicadas, ch23; the upstairs
# window lit, ch5). REAL OPENING: painted double-hung frame,
# meeting rail + upper muntins, casing, stool, apron; plum cotton
# curtain panels on a rod.
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D
    make_box("Win_FrameT", (0.0, wy, WIN_HEAD - 0.03), (WIN_W, 0.14, 0.06), CALDWELL_TRIM)
    make_box("Win_FrameB", (0.0, wy, WIN_SILL + 0.03), (WIN_W, 0.14, 0.06), CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Jamb_{sgn:+d}", (sgn * (WIN_W / 2.0 - 0.03), wy, 1.55),
                 (0.06, 0.14, 1.20), CALDWELL_TRIM)
    make_box("Win_MeetingRail", (0.0, wy, 1.56), (WIN_W - 0.08, 0.10, 0.06), CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Muntin_{sgn:+d}", (sgn * 0.22, wy - 0.02, 1.86),
                 (0.035, 0.06, 0.54), CALDWELL_TRIM)
    # Interior casing + stool + apron
    for sgn in (-1, +1):
        make_box(f"Win_Casing_{sgn:+d}", (sgn * (WIN_W / 2.0 + 0.09), wy - 0.105, 1.55),
                 (0.10, 0.05, 1.40), CALDWELL_TRIM)
    make_box("Win_CasingHead", (0.0, wy - 0.105, WIN_HEAD + 0.08), (WIN_W + 0.28, 0.05, 0.10),
             CALDWELL_TRIM)
    make_box("Win_Stool", (0.0, wy - 0.135, WIN_SILL + 0.02), (WIN_W + 0.30, 0.16, 0.04),
             CALDWELL_TRIM)
    make_box("Win_Apron", (0.0, wy - 0.105, WIN_SILL - 0.05), (WIN_W + 0.16, 0.05, 0.09),
             CALDWELL_TRIM)
    # Curtains — rod, finials, two plum panels (tied back look)
    make_cyl("Curtain_Rod", (0.0, wy - 0.16, 2.28), 0.012, 1.70, COL_BRASS, axis='X')
    for sgn in (-1, +1):
        make_cyl(f"Curtain_Finial_{sgn:+d}", (sgn * 0.86, wy - 0.16, 2.28), 0.026, 0.05,
                 COL_BRASS, axis='X')
        make_box(f"Curtain_Panel_{sgn:+d}", (sgn * 0.70, wy - 0.155, 1.62),
                 (0.26, 0.030, 1.32), COL_PLUM)
        make_box(f"Curtain_Fold_{sgn:+d}", (sgn * 0.62, wy - 0.175, 1.58),
                 (0.09, 0.018, 1.22), COL_PLUM_DK)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR — second-floor view (ch4 "Maya goes downstairs"; ch5
# "the upstairs window is lit"): siding skins wrap the opening, the
# PORCH ROOF directly below (the grandmother's porch, ch14/ch21),
# the cul-de-sac at grade, the CEDAR across the cul-de-sac with the
# cicadas in it (ch14), and the GELLER PORCH LIGHT at the end of
# the Caldwell cul-de-sac, on (ch23) — the one warm dot out there.
# ═════════════════════════════════════════════════════════════════
def build_exterior():
    wallout = ROOM_D + 0.10
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20
    seg_cx = WIN_W / 2.0 + seg_len / 2.0
    make_box("Ext_Skin_W", (-seg_cx, wallout + 0.02, 1.30), (seg_len, 0.06, 2.60),
             CALDWELL_SIDING)
    make_box("Ext_Skin_E", (+seg_cx, wallout + 0.02, 1.30), (seg_len, 0.06, 2.60),
             CALDWELL_SIDING)
    make_box("Ext_Skin_Sill", (0.0, wallout + 0.02, WIN_SILL / 2.0),
             (WIN_W, 0.06, WIN_SILL), CALDWELL_SIDING)
    make_box("Ext_Skin_Head", (0.0, wallout + 0.02, (WIN_HEAD + 2.60) / 2.0),
             (WIN_W, 0.06, 2.60 - WIN_HEAD), CALDWELL_SIDING)
    for si, sz in enumerate((0.55, 1.85, 2.35)):
        make_box(f"Ext_SidingSeam_{si}", (0.0, wallout + 0.052, sz),
                 (ROOM_W + 0.4, 0.006, 0.02), (0.70, 0.66, 0.56, 1.0))
    # The porch roof below the window (grandmother's porch, ch21)
    make_box("PorchRoof_Deck", (0.0, 6.05, -0.62), (4.6, 2.10, 0.10), CALDWELL_ROOF)
    make_box("PorchRoof_Ridge", (0.0, 5.25, -0.50), (4.6, 0.30, 0.08), CALDWELL_ROOF)
    make_box("PorchRoof_Fascia", (0.0, 7.08, -0.68), (4.6, 0.06, 0.16), CALDWELL_TRIM)
    for gi, gx in enumerate((-2.1, 2.1)):
        make_box(f"PorchRoof_EndCap_{gi}", (gx, 6.05, -0.64), (0.08, 2.10, 0.14),
                 CALDWELL_TRIM)
    # The cul-de-sac at grade: lawn / walk / street / far lawn
    make_box("Ext_Lawn", (0.0, 8.6, GRADE_Z - 0.05), (18.0, 3.4, 0.10), COL_NIGHT_LAWN)
    make_box("Ext_Walk", (-1.6, 8.6, GRADE_Z + 0.005), (0.9, 3.4, 0.012), COL_CONCRETE)
    make_box("Ext_Sidewalk", (0.0, 10.5, GRADE_Z - 0.02), (18.0, 0.8, 0.10), COL_CONCRETE)
    make_box("Ext_Street", (0.0, 12.6, GRADE_Z - 0.07), (18.0, 3.4, 0.10), COL_ASPHALT)
    make_box("Ext_FarLawn", (0.0, 15.6, GRADE_Z - 0.05), (18.0, 2.6, 0.10), COL_NIGHT_LAWN)
    # THE CEDAR across the cul-de-sac (ch14 — the cicadas live here)
    make_cyl("Cedar_Trunk", (-4.5, 14.2, GRADE_Z + 0.9), 0.14, 1.80, COL_WOOD_DK)
    for ti, (tr, tz, tc) in enumerate([(1.40, GRADE_Z + 2.25, COL_CEDAR_DK),
                                       (1.05, GRADE_Z + 3.15, COL_CEDAR),
                                       (0.72, GRADE_Z + 3.95, COL_CEDAR_DK),
                                       (0.42, GRADE_Z + 4.65, COL_CEDAR)]):
        make_cyl(f"Cedar_Tier_{ti}", (-4.5, 14.2, tz), tr, 0.85, tc, segments=10)
    # THE GELLER HOUSE at the end of the cul-de-sac — dark massing,
    # porch light ON (ch23: Don at the window, eleven-thirty)
    gx, gy = 5.2, 15.8
    make_box("Geller_Body", (gx, gy, GRADE_Z + 1.5), (6.5, 4.2, 3.0),
             (0.55, 0.51, 0.45, 1.0))
    make_box("Geller_Roof0", (gx, gy, GRADE_Z + 3.24), (7.1, 4.8, 0.48), CALDWELL_ROOF)
    make_box("Geller_Roof1", (gx, gy, GRADE_Z + 3.68), (4.8, 3.2, 0.40), CALDWELL_ROOF)
    for wi, wx in enumerate((-1.9, 0.0)):
        make_box(f"Geller_Window_{wi}", (gx + wx, gy - 2.13, GRADE_Z + 1.6),
                 (0.85, 0.06, 0.75), (0.09, 0.11, 0.14, 1.0))
    # Don's window — the one faint lit pane (ch23, the water glass)
    make_box("Geller_WindowLit", (gx + 1.9, gy - 2.13, GRADE_Z + 1.6),
             (0.85, 0.06, 0.75), (0.42, 0.38, 0.28, 1.0))
    make_box("Geller_Door", (gx - 0.9, gy - 2.12, GRADE_Z + 1.0), (0.85, 0.06, 2.0),
             (0.22, 0.20, 0.19, 1.0))
    make_box("Geller_LightBracket", (gx - 1.45, gy - 2.10, GRADE_Z + 1.70),
             (0.06, 0.05, 0.10), P.METAL_BLACK)
    make_cyl("Geller_PorchLight", (gx - 1.45, gy - 2.16, GRADE_Z + 1.66), 0.055, 0.12,
             COL_PORCHBULB, segments=10)
    # A second dark tract massing west — the street repeating
    make_box("TractW_Body", (-8.0, 15.4, GRADE_Z + 1.4), (5.8, 4.4, 2.8),
             (0.48, 0.46, 0.44, 1.0))
    make_box("TractW_Roof", (-8.0, 15.4, GRADE_Z + 3.02), (6.4, 5.0, 0.44), CALDWELL_ROOF)


# ═════════════════════════════════════════════════════════════════
# BED ZONE — twin bed on the west wall, head at the window end,
# MADE (she lies on top of the bedspread, ch1/ch6): spread pulled
# square with side drapes + a band, pillow. Under it, the hardback
# GENERAL STORE portfolio (maya_daigle.md §II), east edge just
# proud. Nightstand: lamp (ch2), phone (ch14), the spiral
# notebook + pen (ch0/ch2). Two of her own ink drawings taped on
# the wall above.
# ═════════════════════════════════════════════════════════════════
def build_bed_zone():
    bx = -1.425                    # bed center x (frame -1.92..-0.93)
    y0, y1 = 2.55, 4.45            # foot..head
    by = (y0 + y1) / 2.0
    # Frame + legs + headboard
    make_box("Bed_Rail", (bx, by, 0.32), (1.02, 1.92, 0.12), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Bed_Leg_{li}", (bx + sx * 0.46, by + sy * 0.90, 0.15), 0.030, 0.30,
                 COL_WOOD_DK)
    make_box("Bed_Headboard", (bx, y1 - 0.02, 0.62), (1.02, 0.06, 0.70), COL_WOOD)
    make_box("Bed_HeadboardCap", (bx, y1 - 0.02, 0.99), (1.06, 0.09, 0.05), COL_WOOD_DK)
    make_box("Bed_Mattress", (bx, by, 0.46), (0.98, 1.86, 0.16), COL_LINEN)
    # THE BEDSPREAD — made, pulled square (ch1: "She lies down on
    # top of the bedspread"), plum with a woven band near the foot
    make_box("Bedspread_Top", (bx, by - 0.09, 0.565), (1.00, 1.68, 0.055), COL_PLUM)
    make_box("Bedspread_DrapeE", (bx + 0.505, by - 0.09, 0.40), (0.025, 1.68, 0.30),
             COL_PLUM)
    make_box("Bedspread_DrapeS", (bx, y0 + 0.03, 0.40), (1.00, 0.025, 0.30), COL_PLUM)
    make_box("Bedspread_Band", (bx, 2.95, 0.596), (1.005, 0.20, 0.006), COL_QUILT_BND)
    make_box("Bed_Pillow", (bx, y1 - 0.24, 0.62), (0.82, 0.34, 0.11), COL_LINEN)
    # THE PORTFOLIO under the bed — GENERAL STORE, 187 pages of
    # 8.5x11 (maya_daigle.md §II: "a single hardback portfolio she
    # keeps under her bed"). East edge peeks past the rail.
    make_box("Portfolio_Body", (-1.05, 3.10, 0.045), (0.32, 0.44, 0.07), COL_CHARCOAL)
    make_box("Portfolio_PagesEdge", (-0.888, 3.10, 0.045), (0.006, 0.42, 0.05), P.PAPER)
    make_box("Portfolio_Strap", (-1.05, 3.10, 0.083), (0.30, 0.05, 0.006),
             (0.30, 0.28, 0.30, 1.0))
    # Nightstand between bed head and the north wall
    nx, ny = -1.62, 4.68
    make_box("Nightstand_Body", (nx, ny, 0.26), (0.42, 0.40, 0.52), COL_WOOD)
    make_box("Nightstand_Top", (nx, ny, 0.535), (0.46, 0.44, 0.03), COL_WOOD_DK)
    make_box("Nightstand_Drawer", (nx, ny - 0.205, 0.40), (0.34, 0.015, 0.14), COL_WOOD_DK)
    make_cyl("Nightstand_Knob", (nx, ny - 0.22, 0.40), 0.013, 0.03, COL_BRASS, axis='Y')
    # THE LAMP (ch2: "She turns off the lamp.")
    make_cyl("Lamp_Base", (nx - 0.08, ny + 0.08, 0.565), 0.065, 0.025, COL_WOOD_DK)
    make_cyl("Lamp_Stem", (nx - 0.08, ny + 0.08, 0.70), 0.012, 0.26, COL_BRASS)
    make_cyl("Lamp_Shade", (nx - 0.08, ny + 0.08, 0.885), 0.095, 0.13, COL_LINEN,
             segments=12)
    make_cyl("Lamp_Glow", (nx - 0.08, ny + 0.08, 0.815), 0.040, 0.02, COL_LAMP_GLOW)
    # THE PHONE on the nightstand (ch14)
    make_box("Phone_Slab", (nx + 0.12, ny - 0.06, 0.556), (0.072, 0.148, 0.010),
             (0.10, 0.10, 0.12, 1.0))
    # THE SPIRAL NOTEBOOK + pen (ch0: cross-legged at 6:16; ch2:
    # "She does not, tonight, write in the notebook.")
    make_box("SpiralNotebook", (nx - 0.05, ny - 0.10, 0.560), (0.15, 0.21, 0.018),
             (0.34, 0.42, 0.38, 1.0))
    make_box("SpiralNotebook_Coil", (nx - 0.125, ny - 0.10, 0.563), (0.016, 0.20, 0.020),
             P.METAL_STEEL)
    make_cyl("Notebook_Pen", (nx + 0.10, ny + 0.11, 0.556), 0.005, 0.13, COL_INK, axis='Y')
    # Her own ink drawings taped above the bed (only her work hangs
    # here — no store-bought posters)
    for di, (dy, dz, dw, dh) in enumerate([(3.05, 1.52, 0.24, 0.30),
                                           (3.42, 1.60, 0.21, 0.26)]):
        make_box(f"WallDrawing_{di}", (-1.975, dy, dz), (0.006, dw, dh), P.PAPER)
        make_box(f"WallDrawing_{di}_Ink", (-1.972, dy, dz + 0.02),
                 (0.002, dw * 0.62, dh * 0.55), COL_INK)
        make_box(f"WallDrawing_{di}_Tape", (-1.974, dy, dz + dh / 2.0 - 0.008),
                 (0.004, 0.05, 0.022), (0.88, 0.86, 0.78, 1.0))


# ═════════════════════════════════════════════════════════════════
# DESK ZONE — the zine studio on the east wall. THE THINKPAD open
# (ch1/ch2/ch6/ch14) with the chat window lit; the desk lamp (the
# .tscn key light is literally named Key_DeskLamp); fineliner jar +
# grey markers (maya_daigle.md §I — pen and marker, NOT a
# typewriter; the photocopier is at Cosmic Comics); issue #23's
# pencilled quarter-letter flats laid out with the pencil; the A5
# black sketchbook, closed (§III); the school-supplies box staged
# beside the desk (ch23).
# ═════════════════════════════════════════════════════════════════
def build_desk_zone():
    dx = 1.62                        # desk center x (1.34..1.90)
    y0, y1 = 1.55, 2.85
    dy = (y0 + y1) / 2.0
    make_box("Desk_Top", (dx, dy, 0.735), (0.56, 1.30, 0.035), COL_WOOD)
    make_box("Desk_Apron", (dx, dy, 0.685), (0.46, 1.18, 0.06), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Desk_Leg_{li}", (dx + sx * 0.24, dy + sy * 0.60, 0.345),
                 (0.045, 0.045, 0.69), COL_WOOD_DK)
    # THE THINKPAD — open, screen facing the chair (west); the pale
    # chat rectangle is the F.T. window (ch1: "The ThinkPad wakes
    # when she opens it.")
    make_box("ThinkPad_Base", (1.60, 2.58, 0.762), (0.235, 0.31, 0.018), COL_CHARCOAL)
    make_box("ThinkPad_Keys", (1.585, 2.58, 0.7725), (0.17, 0.27, 0.003),
             (0.11, 0.11, 0.12, 1.0))
    make_box("ThinkPad_TrackPoint", (1.585, 2.58, 0.775), (0.010, 0.010, 0.003),
             (0.76, 0.22, 0.18, 1.0))
    make_box("ThinkPad_Lid", (1.725, 2.58, 0.870), (0.014, 0.31, 0.21), COL_CHARCOAL)
    make_box("ThinkPad_Screen", (1.716, 2.58, 0.872), (0.003, 0.27, 0.17), COL_SCREEN)
    make_box("ThinkPad_ChatWindow", (1.713, 2.60, 0.878), (0.002, 0.17, 0.11),
             COL_CHATGLOW)
    # Desk lamp, south end (matches the .tscn Key_DeskLamp)
    make_cyl("DeskLamp_Base", (1.78, 1.70, 0.765), 0.065, 0.022, P.METAL_BLACK)
    make_cyl("DeskLamp_Stem", (1.78, 1.70, 0.92), 0.011, 0.29, P.METAL_BLACK)
    make_cyl("DeskLamp_Arm", (1.66, 1.70, 1.065), 0.010, 0.24, P.METAL_BLACK, axis='X')
    make_cyl("DeskLamp_Shade", (1.55, 1.70, 1.045), 0.055, 0.09, COL_PLUM_DK, axis='X')
    make_cyl("DeskLamp_Glow", (1.505, 1.70, 1.045), 0.038, 0.012, COL_LAMP_GLOW, axis='X')
    # Fineliner jar + grey-marker jar (§I: fineliner pen and grey
    # marker — the whole toolchain)
    make_cyl("PenJar", (1.80, 1.94, 0.795), 0.035, 0.085, (0.72, 0.78, 0.78, 1.0))
    for pi, (px, py) in enumerate([(-0.012, -0.010), (0.012, -0.004),
                                   (-0.004, 0.012), (0.010, 0.010)]):
        make_cyl(f"Fineliner_{pi}", (1.80 + px, 1.94 + py, 0.885), 0.0042, 0.11, COL_INK)
    make_cyl("MarkerJar", (1.80, 2.08, 0.790), 0.035, 0.075, (0.72, 0.78, 0.78, 1.0))
    for mi, (mx, my) in enumerate([(-0.012, 0.0), (0.010, -0.010), (0.008, 0.012)]):
        make_cyl(f"GreyMarker_{mi}", (1.80 + mx, 2.08 + my, 0.875), 0.0085, 0.10,
                 COL_MARKER_GY)
    # ISSUE #23 "F.T." — pencils complete (§I), quarter-letter
    # flats (3.5 x 4.25 in) in a 2x2 layout, pencil beside. Dated
    # in pencil: "to publish — when I have permission."
    for zi, (zx, zy) in enumerate([(-0.056, -0.066), (0.056, -0.066),
                                   (-0.056, 0.066), (0.056, 0.066)]):
        make_box(f"Zine23_Flat_{zi}", (1.50 + zx, 2.16 + zy, 0.754),
                 (0.089, 0.108, 0.0015), P.PAPER)
    for gi, (gx, gy) in enumerate([(-0.056, -0.066), (0.056, 0.066)]):
        make_box(f"Zine23_Pencils_{gi}", (1.50 + gx, 2.16 + gy, 0.7552),
                 (0.062, 0.078, 0.0008), COL_PENCIL)
    make_box("Zine23_MarkerTest", (1.50, 2.16, 0.7548), (0.030, 0.150, 0.0008),
             COL_MARKER_GY)
    make_cyl("Zine23_Pencil", (1.38, 2.02, 0.756), 0.0042, 0.125,
             (0.82, 0.64, 0.28, 1.0), axis='Y')
    # THE SKETCHBOOK — A5, black, closed, white label strip ("NOT
    # FOR PUBLICATION · NOT YET · M.D.", §III)
    make_box("Sketchbook", (1.48, 1.80, 0.753), (0.150, 0.210, 0.024), COL_CHARCOAL)
    make_box("Sketchbook_Label", (1.48, 1.80, 0.7665), (0.085, 0.048, 0.0015), P.PAPER)
    # Desk chair — she faces east at the wall
    make_box("Chair_Seat", (1.06, 2.20, 0.44), (0.40, 0.40, 0.04), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Chair_Leg_{li}", (1.06 + sx * 0.16, 2.20 + sy * 0.16, 0.22),
                 0.018, 0.44, COL_WOOD_DK)
    for pi, sgn in enumerate((-1, +1)):
        make_cyl(f"Chair_Post_{pi}", (0.88, 2.20 + sgn * 0.16, 0.67), 0.016, 0.46,
                 COL_WOOD)
    for si, sz in enumerate((0.72, 0.86)):
        make_box(f"Chair_Slat_{si}", (0.88, 2.20, sz), (0.03, 0.36, 0.085), COL_WOOD)
    # THE SCHOOL-SUPPLIES BOX (ch23 — the Walmart run: the binder,
    # the pack of pens, the index cards, the new notebook saved for
    # the first day), staged on the floor between desk and bookcase
    make_box("SupplyBox_Body", (1.58, 3.14, 0.095), (0.34, 0.26, 0.19), COL_CARDBOARD,
             open_faces={'+Z'})
    make_box("SupplyBox_Floor", (1.58, 3.14, 0.02), (0.32, 0.24, 0.01),
             (0.52, 0.40, 0.26, 1.0))
    make_box("SupplyBox_Binder", (1.53, 3.14, 0.115), (0.06, 0.23, 0.17),
             (0.30, 0.36, 0.46, 1.0))
    make_box("SupplyBox_Notebook", (1.61, 3.14, 0.105), (0.02, 0.21, 0.15), COL_PLUM)
    make_box("SupplyBox_IndexCards", (1.68, 3.10, 0.075), (0.08, 0.13, 0.032), P.PAPER)
    make_box("SupplyBox_PenPack", (1.68, 3.22, 0.068), (0.055, 0.10, 0.018),
             (0.72, 0.78, 0.78, 1.0))


# ═════════════════════════════════════════════════════════════════
# CORKBOARD — over the desk: her documented working method is
# "text, comix, and small map fragments" (§I). Pinned quarter
# sheets, one hand-drawn map fragment, pins. This is the only wall
# system in the room besides her taped drawings.
# ═════════════════════════════════════════════════════════════════
def build_corkboard():
    wx = ROOM_W / 2.0 - 0.10          # interior face x 1.9
    make_box("Cork_Board", (wx - 0.012, 2.20, 1.62), (0.024, 1.05, 0.72), COL_CORK)
    make_box("Cork_FrameT", (wx - 0.018, 2.20, 1.995), (0.036, 1.11, 0.045), COL_WOOD)
    make_box("Cork_FrameB", (wx - 0.018, 2.20, 1.245), (0.036, 1.11, 0.045), COL_WOOD)
    for sgn in (-1, +1):
        make_box(f"Cork_FrameSide_{sgn:+d}", (wx - 0.018, 2.20 + sgn * 0.5525, 1.62),
                 (0.036, 0.045, 0.795), COL_WOOD)
    # Pinned quarter-letter sheets (deterministic scatter)
    sheets = [(1.85, 1.82, P.PAPER), (2.42, 1.46, P.PAPER_AGED), (2.55, 1.80, P.PAPER),
              (2.02, 1.42, P.PAPER), (1.90, 1.44, P.NEWSPRINT)]
    for si, (sy, sz, tint) in enumerate(sheets):
        make_box(f"Cork_Sheet_{si}", (wx - 0.028, sy, sz), (0.006, 0.089, 0.108), tint)
        make_box(f"Cork_Sheet_{si}_Ink", (wx - 0.032, sy, sz + 0.012),
                 (0.002, 0.062, 0.058), COL_INK)
        make_cyl(f"Cork_Pin_{si}", (wx - 0.034, sy, sz + 0.048), 0.007, 0.012,
                 (0.76, 0.22, 0.18, 1.0) if si % 2 == 0 else (0.28, 0.36, 0.42, 1.0),
                 axis='X')
    # The map fragment — a small hand-drawn piece of Harmony Creek
    make_box("Cork_MapFrag", (wx - 0.028, 2.22, 1.66), (0.006, 0.165, 0.135),
             P.PAPER_AGED)
    make_box("Cork_MapFrag_RoadA", (wx - 0.032, 2.22, 1.66), (0.002, 0.130, 0.010),
             COL_INK)
    make_box("Cork_MapFrag_RoadB", (wx - 0.032, 2.25, 1.665), (0.002, 0.010, 0.095),
             COL_INK)
    make_box("Cork_MapFrag_Lot", (wx - 0.032, 2.185, 1.695), (0.002, 0.028, 0.022),
             COL_PLUM_DK)
    make_cyl("Cork_MapFrag_Pin", (wx - 0.034, 2.22, 1.718), 0.007, 0.012,
             (0.76, 0.22, 0.18, 1.0), axis='X')


# ═════════════════════════════════════════════════════════════════
# BOOKCASE — NE corner: her comics + books, the file stack of
# NEWS FROM HARMONY CREEK back issues (23 issues and counting,
# §I), and the ream of 8.5x11 printer paper — the one Rick quietly
# over-orders for her every quarter (§II).
# ═════════════════════════════════════════════════════════════════
def build_bookcase():
    cx, cy = 1.70, 4.30              # against east wall (x 1.55..1.85)
    for si, sgn in enumerate((-1, +1)):
        make_box(f"Bookcase_Side_{si}", (cx, cy + sgn * 0.375, 0.585),
                 (0.30, 0.03, 1.17), COL_WOOD)
    for shi, sz in enumerate((0.02, 0.40, 0.78, 1.16)):
        make_box(f"Bookcase_Shelf_{shi}", (cx, cy, sz), (0.30, 0.72, 0.025), COL_WOOD)
    # Shelf 1 (z 0.41..0.78): book row, mixed spines
    for bi in range(6):
        bh = 0.24 - (bi % 3) * 0.025
        make_box(f"Bookcase_Book_{bi}", (cx, cy - 0.30 + bi * 0.085, 0.415 + bh / 2.0),
                 (0.20, 0.055, bh), BOOK_TINTS[bi % len(BOOK_TINTS)])
    # Shelf 2 (z 0.79..1.16): the comics stack + the zine file stack
    for ci in range(5):
        make_box(f"Bookcase_Comic_{ci}", (cx + (ci % 2) * 0.012, cy - 0.18,
                 0.80 + ci * 0.014), (0.175, 0.26, 0.012),
                 P.SNACK_TINTS[(ci * 2) % len(P.SNACK_TINTS)])
    # NEWS FROM HARMONY CREEK back issues — quarter-letter, her
    # file copies (§I: twenty-three issues across two years)
    for ni in range(8):
        make_box(f"Bookcase_ZineStack_{ni}", (cx + (ni % 2) * 0.008,
                 cy + 0.20 + (ni % 3) * 0.006, 0.795 + ni * 0.005),
                 (0.089, 0.108, 0.004), P.PAPER if ni % 2 == 0 else P.PAPER_AGED)
    # Top: the ream of printer paper (§II — Rick's quiet extra ream)
    make_box("PaperReam", (cx, cy - 0.16, 1.20), (0.22, 0.28, 0.05), P.PAPER)
    make_box("PaperReam_Wrap", (cx, cy - 0.16, 1.20), (0.225, 0.16, 0.052),
             (0.62, 0.68, 0.70, 1.0))
    # Two standing books on top, leaning stack look
    for ti in range(2):
        make_box(f"Bookcase_TopBook_{ti}", (cx, cy + 0.18 + ti * 0.06, 1.285),
                 (0.18, 0.05, 0.22), BOOK_TINTS[(ti + 3) % len(BOOK_TINTS)])


# ═════════════════════════════════════════════════════════════════
# CLOSET — west wall, south bay: bypass sliding doors, both panels
# slid SOUTH so the north half stands open (clothes, sneakers).
# On the floor of the CLOSED south half: THE WOODEN BOX
# (maya_daigle.md §V — 12 x 8 x 6 in, her father's last in-person
# gift; the mixtape, the printed F.T. chat logs, the Polaroid and
# the four ANYA tapes are inside). Present, occluded behind the
# closed panel, never announced — plain wood, no label, an
# ordinary shoebox beside it. (Same treatment as Philip's box in
# the Cosmic back office.)
# ═════════════════════════════════════════════════════════════════
def build_closet():
    wx = -ROOM_W / 2.0 + 0.10        # interior wall face x -1.9
    # Bay: x -1.9..-1.30, y 0.66..2.34
    for pi, py in enumerate((0.68, 2.32)):
        make_box(f"Closet_EndWall_{pi}", (wx + 0.30, py, 1.30), (0.60, 0.04, 2.60),
                 CALDWELL_INT_WALL)
    make_box("Closet_Header", (-1.33, 1.50, 2.30), (0.06, 1.68, 0.60), CALDWELL_INT_WALL)
    make_box("Closet_Track", (-1.345, 1.50, 1.985), (0.045, 1.60, 0.03), P.METAL_STEEL)
    make_box("Closet_FloorStrip", (wx + 0.30, 1.50, 0.004), (0.58, 1.64, 0.008),
             CALDWELL_PINE)
    # Bypass panels — BOTH stacked over the south half (opening
    # shows the north half; the south floor is hidden)
    make_box("Closet_PanelOuter", (-1.335, 1.10, 1.00), (0.028, 0.80, 1.94),
             CALDWELL_TRIM)
    make_box("Closet_PanelInner", (-1.368, 1.14, 1.00), (0.028, 0.80, 1.94),
             (0.88, 0.86, 0.80, 1.0))
    make_cyl("Closet_FingerCup", (-1.318, 1.44, 1.00), 0.022, 0.008,
             (0.62, 0.60, 0.56, 1.0), axis='X')
    # Rod + hangers + clothes in the open north half
    make_cyl("Closet_Rod", (-1.62, 1.50, 1.78), 0.015, 1.56, P.METAL_STEEL, axis='Y')
    for gi, gy in enumerate((1.62, 1.80, 1.98, 2.16)):
        glen = (0.62, 0.80, 0.68, 0.52)[gi]
        make_cyl(f"Closet_Hanger_{gi}", (-1.62, gy, 1.795), 0.008, 0.05, P.METAL_STEEL)
        make_box(f"Closet_Garment_{gi}", (-1.62, gy, 1.74 - glen / 2.0),
                 (0.11, 0.15, glen), GARMENT_TINTS[gi % len(GARMENT_TINTS)])
    make_box("Closet_FlannelStripe", (-1.62, 1.80, 1.46), (0.115, 0.152, 0.03),
             (0.24, 0.18, 0.16, 1.0))
    # Sneakers on the open-half floor
    for shi, sy in enumerate((1.70, 1.86)):
        make_box(f"Closet_Sneaker_{shi}", (-1.66, sy, 0.055), (0.24, 0.10, 0.09),
                 (0.82, 0.80, 0.76, 1.0))
        make_box(f"Closet_SneakerSole_{shi}", (-1.66, sy, 0.016), (0.25, 0.11, 0.03),
                 (0.94, 0.93, 0.90, 1.0))
    # ── THE BOX (§V) — south half, BEHIND the closed panels ──────
    make_box("ClosetBox_Body", (-1.68, 0.94, 0.078), (0.30, 0.20, 0.148), COL_WOOD)
    make_box("ClosetBox_LidSeam", (-1.68, 0.94, 0.118), (0.304, 0.204, 0.006),
             COL_WOOD_DK)
    # An ordinary shoebox beside it — nothing points at the box
    make_box("Closet_Shoebox", (-1.66, 1.24, 0.062), (0.20, 0.32, 0.124), COL_CARDBOARD)
    make_box("Closet_ShoeboxLid", (-1.66, 1.24, 0.128), (0.21, 0.33, 0.012),
             (0.58, 0.45, 0.29, 1.0))


# ═════════════════════════════════════════════════════════════════
# FLOOR CENTER — the rug over the third board (ch4: "The rug has
# been pulled back" — its resting state covers the board), and the
# box fan by the window (ch23: "The fan is on.").
# ═════════════════════════════════════════════════════════════════
def build_rug_and_fan():
    # Braided oval rug, three flattened rings — covers board 3
    for ri, (rr, rz, tint) in enumerate([(0.78, 0.004, COL_PLUM_DK),
                                         (0.56, 0.007, (0.55, 0.48, 0.40, 1.0)),
                                         (0.34, 0.010, (0.40, 0.44, 0.48, 1.0))]):
        make_cyl(f"Rug_Ring_{ri}", (0.15, 3.95, rz), rr, 0.008, tint, segments=16)
    # Box fan on the floor by the window, facing the bed (ch23)
    fx, fy = 0.85, 4.55
    make_box("Fan_Body", (fx, fy, 0.33), (0.50, 0.14, 0.50), COL_FAN_BODY)
    make_cyl("Fan_Blades", (fx, fy - 0.045, 0.33), 0.20, 0.03, (0.30, 0.30, 0.32, 1.0),
             axis='Y', segments=12)
    make_cyl("Fan_Hub", (fx, fy - 0.075, 0.33), 0.05, 0.02, COL_FAN_BODY, axis='Y')
    for si in range(5):
        make_box(f"Fan_Grille_{si}", (fx - 0.20 + si * 0.10, fy - 0.078, 0.33),
                 (0.022, 0.008, 0.44), (0.62, 0.61, 0.58, 1.0))
    for fi, sgn in enumerate((-1, +1)):
        make_box(f"Fan_Foot_{fi}", (fx + sgn * 0.20, fy, 0.03), (0.06, 0.18, 0.06),
                 COL_FAN_BODY)
    make_box("Fan_Cord", (fx + 0.28, fy + 0.28, 0.012), (0.34, 0.014, 0.010),
             (0.30, 0.28, 0.26, 1.0))


# ═════════════════════════════════════════════════════════════════
# CEILING FIXTURES — house dome light (NOT the scaffold's
# commercial fluorescents), smoke detector, HVAC register. The
# ceiling itself is the pale yellow plane in build_shell.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_fixtures():
    make_cyl("DomeLight_Plate", (0.0, 2.50, CEIL - 0.015), 0.17, 0.025, COL_BRASS,
             segments=12)
    make_cyl("DomeLight_Dome", (0.0, 2.50, CEIL - 0.065), 0.145, 0.075,
             (0.97, 0.93, 0.82, 1.0), segments=12)
    make_cyl("DomeLight_Finial", (0.0, 2.50, CEIL - 0.115), 0.018, 0.03, COL_BRASS)
    make_smoke_detector("Smoke", (-0.9, 1.2, CEIL))
    make_hvac_vent("HVAC", (0.9, 0.8, CEIL), width=0.50, depth=0.30)


def main():
    clear_scene()
    build_shell()
    build_door()
    build_window()
    build_exterior()
    build_bed_zone()
    build_desk_zone()
    build_corkboard()
    build_bookcase()
    build_closet()
    build_rug_and_fan()
    build_ceiling_fixtures()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/maya_bedroom.glb"))
    print(f"\n[build_maya_bedroom] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
