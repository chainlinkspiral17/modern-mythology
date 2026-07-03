"""Caldwell Radio Room (night) — the GRANDMOTHER'S BEDROOM, upstairs
at lot 7 Phase I, the Caldwell cul-de-sac, Harmony Creek Estates —
vol6 hero locale (2 VN bg refs, both vol6_ch5_radio "1776 kHz").

This room is the reason Maya's bedroom has no radio (its
canon-negative list points HERE): the 1776 kHz shortwave lives in
the grandmother's room, across the hall from Maya's
(vol6_ch2_maya_bedroom:18 — "She crosses the hall"). It is NOT a
ham shack — it is a seventy-one-year-old widow's bedroom with a
radio in the window, which is the entire point. Canon baked in:

  · vol6_ch5_radio:113 — "She is, at eleven PM on a Thursday in
    late May, at her shortwave radio. She is not, tonight,
    listening. She is, tonight, transmitting." THE RADIO is the
    hero prop.
  · vol6_ch12_porch:454 — "The radio, on the windowsill, stays
    off." The set sits ON THE WINDOWSILL — the window stool is cut
    deep to carry it. Its dial lamp is baked lit (this GLB's own
    scene, ch5, has it transmitting at 11 PM; ch12's off-state is
    the scene's Light3D to kill).
  · vol6_ch2_maya_bedroom:36 — "Because your grandfather put it
    there, Maya. In 1989. When he got out." A 1989-vintage set:
    steel-and-bakelite case, round tuning dial, band scale, three
    knobs. Thomas the photographer installed it; a LONGWIRE
    antenna runs from the chassis up the window jamb and out the
    head corner.
  · vol6_ch5_radio:117 — "in Morse code she has not used since
    1989, in the cadence her husband Thomas had taught her" /
    :180 — "Her grandmother keys the Morse: Maya says hi." THE
    STRAIGHT KEY on the little desk under the sill, cabled to the
    set, a chair squared to it. The transmission: "Thomas is gone.
    Maya is here. I remember."
  · vol6_ch5_radio:165 — "Maya crosses to the radio. She sits on
    the edge of the bed." The bed stands close enough to the radio
    corner that its edge is a second seat — head on the north
    wall, east of the window.
  · vol6_ch12_porch:406 / ch21:368 — "turns back the covers on her
    grandmother's bed so that when her grandmother comes inside ...
    the bed will be ready": the quilt is baked with its head
    corner TURNED BACK.
  · vol6_ch5_radio:190 — "her grandmother — who has not slept a
    full night since 1989 — begins to nod, and Maya helps her into
    bed": the nightstand lamp is on (warm practical; scene-side
    Light3D matches), the water glass beside it.
  · vol6_ch2_maya_bedroom:41 — Thomas was "a photographer. In
    Graustark. In the seventies." One small framed photograph on
    the dresser (inferred dressing from the ch2 story — flagged,
    not literal scene text).
  · Exterior (upstairs, front): ch5:113 — "the upstairs window is
    lit" is street-visible, so this window faces the cul-de-sac.
    Same night view build_maya_bedroom.py bakes one room over: the
    porch roof below, the cedar across the cul-de-sac (ch14), the
    Geller porch light on (ch21:208), and — over the far
    rooflines, at the end of Gallatin — THE WATER TOWER that
    rebroadcasts her Morse into the grid (vol6_ch1:44, ch5:125).

Canon-NEGATIVES honored (what this room does NOT have):
  · ONE radio. No boombox (the old dual-cassette unit's resting
    place is unspecified, maya_daigle.md §IV), no kitchen radio
    (that windowsill radio is the RAMOS house — vol6_ch10_home:38
    firewalls it from "the upstairs shortwave at Linda Caldwell's").
  · No ham-shack clutter: no QSL cards, no rack gear, no second
    receiver. Thomas put one radio in one window in 1989.
  · No cane or walker (the hip HEALED in June — ch21:320).
  · No TV, no telephone (her phone traffic is 1776 kHz).
  · No commercial fluorescents, no crown molding (1991 tract) —
    the scaffold's tube fixtures are gone; house dome fixture only.
  · Maya's zine #15 claims the grandmother "does not own a
    shortwave radio" — written BEFORE the ch2 reveal; the JSONs
    override (and in-fiction, Maya simply hadn't been told yet).

NAME-DEPENDENCY FLAG (same drift build_maya_bedroom.py flags): the
scene JSONs name the grandmother Ms. LINDA CALDWELL on "the
Caldwell cul-de-sac" (vol6_ch5_radio:121 files her under
GRANDMOTHER, CALDWELL, LINDA); the older lore docs
(lore/planned_community/maya_daigle.md, lore/_VOL6_WIKI.md elders'
list) say CONNIE DAIGLE. The JSONs are treated as current.
Secondary drift, noted: vol6_ch2_maya_bedroom:42 says "the
shortwave DOWNSTAIRS," but ch5 ("She goes upstairs. She knocks"),
ch10:38 ("the upstairs shortwave") and ch12:402-406 all put this
room upstairs — upstairs wins on weight.

Shell footprint kept from the scaffold (4.5 x 5, CEIL 2.6, gap
x -1..+1 in the south wall = the hall doorway the Background3D
camera preset (0, 2.30, +0.5 / yaw 180 / fov 60) shoots through).
The door leaf is modeled OPEN against the south wall (ch5: "Come
in, honey"; ch12: "her grandmother's bedroom door, which is open")
so the camera gap stays clear. Window is a REAL OPENING with frame
+ sash + muntins, no glass (playbook no-transparency rule).
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_wall, make_door_hinges
from _props.safety import make_smoke_detector, make_hvac_vent

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 4.5; ROOM_D = 5.0; CEIL = 2.6

# ═════════════════════════════════════════════════════════════════
# CALDWELL HOUSE — SHARED PALETTE + NIGHT VOCABULARY (⚠ KEEP IN SYNC)
# This block is declared IDENTICALLY in build_caldwell_porch_night.py,
# build_caldwell_kitchen_night.py and build_caldwell_radio_room_night.py
# — three rooms of ONE house (lot 7 Phase I, the Caldwell cul-de-sac).
# md5 the block between these ═ markers when touching any sibling.
# The CALDWELL_* constants also exist as locals in build_maya_bedroom.py
# (Maya's room is upstairs in this house); its docstring asks for them
# to be graduated into a shared block — the values here MATCH that file.
# FOLLOW-UP: next time build_maya_bedroom.py is touched, replace its
# local CALDWELL_* declarations with this block verbatim.
# ═════════════════════════════════════════════════════════════════
CALDWELL_INT_WALL  = (0.90, 0.86, 0.75, 1.0)   # 1991 builder warm white
CALDWELL_BASEBOARD = (0.46, 0.35, 0.24, 1.0)
CALDWELL_TRIM      = (0.93, 0.91, 0.85, 1.0)   # painted door/window trim
CALDWELL_CEIL_YEL  = (0.93, 0.89, 0.70, 1.0)   # THE pale yellow ceiling
CALDWELL_PINE      = (0.72, 0.56, 0.36, 1.0)   # original pine, worn honey
CALDWELL_PINE_SEAM = (0.50, 0.37, 0.23, 1.0)
CALDWELL_SIDING    = (0.84, 0.80, 0.70, 1.0)   # exterior lap siding
CALDWELL_ROOF      = (0.33, 0.27, 0.23, 1.0)   # shingle
# Night-exterior + household vocabulary shared by the three _night
# rooms (values match build_maya_bedroom.py's locals — same street,
# same night):
COL_SIDING_SEAM = (0.70, 0.66, 0.56, 1.0)  # lap-siding shadow lines
COL_NIGHT_LAWN  = (0.22, 0.28, 0.18, 1.0)  # lawn at night
COL_ASPHALT     = (0.16, 0.16, 0.17, 1.0)
COL_CONCRETE    = (0.50, 0.49, 0.45, 1.0)
COL_CEDAR       = (0.20, 0.30, 0.20, 1.0)  # the cedar across the cul-de-sac
COL_CEDAR_DK    = (0.15, 0.24, 0.16, 1.0)
COL_PORCHBULB   = (1.00, 0.88, 0.60, 1.0)  # porch-light warm, ON
COL_WINDOW_DARK = (0.09, 0.11, 0.14, 1.0)  # unlit panes at night
COL_WINDOW_LIT  = (0.42, 0.38, 0.28, 1.0)  # a faintly lit pane
COL_GELLER_BODY = (0.55, 0.51, 0.45, 1.0)  # the Geller house massing
COL_WOOD        = (0.50, 0.37, 0.24, 1.0)  # household furniture pine/oak
COL_WOOD_DK     = (0.31, 0.23, 0.16, 1.0)
COL_BRASS       = (0.70, 0.57, 0.30, 1.0)
COL_LAMP_GLOW   = (0.98, 0.88, 0.62, 1.0)  # practicals: warm bulb glow
COL_CERAMIC     = (0.92, 0.90, 0.84, 1.0)  # plates / mugs / pitcher
COL_TEA         = (0.62, 0.40, 0.18, 1.0)  # Linda's iced tea, amber
COL_TOWER       = (0.30, 0.32, 0.36, 1.0)  # the water tower, moonlit
COL_TOWER_DK    = (0.20, 0.22, 0.26, 1.0)
PAL_WALL = {"wall": CALDWELL_INT_WALL, "baseboard": CALDWELL_BASEBOARD}
# ═════════ end shared block ══════════════════════════════════════

# Radio-room-only palette — a widow's bedroom, kept since 1989
COL_QUILT      = (0.60, 0.44, 0.44, 1.0)   # dusty-rose quilt
COL_QUILT_DK   = (0.48, 0.34, 0.36, 1.0)
COL_LINEN      = (0.90, 0.88, 0.82, 1.0)
COL_CURTAIN    = (0.88, 0.84, 0.74, 1.0)   # aged lace panels
COL_RADIO_CASE = (0.20, 0.19, 0.17, 1.0)   # 1989 steel-and-bakelite
COL_RADIO_FACE = (0.35, 0.33, 0.28, 1.0)
COL_DIAL_LIT   = (0.94, 0.80, 0.50, 1.0)   # dial lamp, transmitting
COL_RUG_A      = (0.52, 0.42, 0.40, 1.0)   # braided rug rings
COL_RUG_B      = (0.60, 0.56, 0.46, 1.0)
COL_RUG_C      = (0.40, 0.44, 0.48, 1.0)
COL_SLIPPER    = (0.56, 0.44, 0.42, 1.0)
COL_PHOTO_GREY = (0.55, 0.53, 0.50, 1.0)   # the photograph, b&w

# Window opening in the north wall (real opening, no glass)
WIN_W = 1.30                # opening x -0.65..+0.65
WIN_SILL = 0.95
WIN_HEAD = 2.15
WALL_N_FACE = ROOM_D - 0.10   # interior face y 4.9
GRADE_Z = -3.20               # cul-de-sac grade (second-floor room)
BOARD_W = 0.24                # original pine boards, run E-W (house-wide)


# ═════════════════════════════════════════════════════════════════
# SHELL — the same original-1991 pine plank floor as Maya's room
# across the hall (boards run E-W), warm-white walls, the pale
# yellow ceiling (one builder, one paint job, 1991), the south hall
# gap kept with the door OPEN against the wall.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_box("Floor_Slab", (0.0, ROOM_D / 2.0, -0.05), (ROOM_W + 0.4, ROOM_D + 0.4, 0.10),
             CALDWELL_PINE)
    for k in range(1, 21):
        sy = WALL_N_FACE - BOARD_W * k
        make_box(f"Floor_Seam_{k}", (0.0, sy, 0.001), (ROOM_W + 0.4, 0.018, 0.002),
                 CALDWELL_PINE_SEAM)
    # Scattered board end-joints (deterministic — no RNG)
    for ji, (jx, jy) in enumerate([(-1.4, 3.94), (1.1, 2.26), (-0.4, 1.30),
                                   (1.6, 4.42), (-1.8, 0.94), (0.5, 3.22)]):
        make_box(f"Floor_Joint_{ji}", (jx, jy, 0.001), (0.018, BOARD_W - 0.02, 0.002),
                 CALDWELL_PINE_SEAM)
    # Walls — west / east full runs
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    # North wall — REAL window opening x -0.65..+0.65
    seg_len = (ROOM_W / 2.0 - WIN_W / 2.0) + 0.20     # 1.80
    seg_cx = WIN_W / 2.0 + seg_len / 2.0              # 1.55
    make_wall("Wall_N_W", (-seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+seg_cx, ROOM_D, 0), length=seg_len, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_N_SillFill", (0.0, ROOM_D, WIN_SILL / 2.0), (WIN_W, 0.20, WIN_SILL),
             CALDWELL_INT_WALL)
    make_box("Wall_N_HeadFill", (0.0, ROOM_D, (WIN_HEAD + CEIL) / 2.0),
             (WIN_W, 0.20, CEIL - WIN_HEAD), CALDWELL_INT_WALL)
    # South wall — scaffold hall gap x -1..+1 kept (camera doorway)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL, baseboard_face_sign=+1)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             CALDWELL_INT_WALL)
    # Gap infill either side of the 0.90 m doorway (Lena pattern)
    for nm, fx in [("Wall_S_FillW", -0.725), ("Wall_S_FillE", +0.725)]:
        make_box(nm, (fx, 0.0, 1.15), (0.55, 0.20, 2.30), CALDWELL_INT_WALL)
    # THE PALE YELLOW CEILING — same 1991 paint as Maya's (ch6/ch21)
    make_box("Ceil_Plane", (0.0, ROOM_D / 2.0, CEIL + 0.05),
             (ROOM_W + 0.4, ROOM_D + 0.4, 0.10), CALDWELL_CEIL_YEL)


# ═════════════════════════════════════════════════════════════════
# DOOR — white four-panel leaf hinged at the west jamb, swung OPEN
# flat against the south wall ("Come in, honey", ch5:147; open door
# at ch12:406). Casing, brass knob, hinges. The gap itself stays
# clear for the camera.
# ═════════════════════════════════════════════════════════════════
def build_door():
    # The doorway proper is x -0.45..+0.45 (the gap infills either
    # side of a 0.90 leaf — Maya/Lena pattern). Leaf hinged at the
    # west jamb, swung open flat along the wall: x -1.35..-0.45.
    make_box("Door_Leaf", (-0.90, 0.155, 1.03), (0.90, 0.05, 2.06), CALDWELL_TRIM)
    for ci, px in enumerate((-1.10, -0.70)):
        for ri, (pz, ph) in enumerate([(0.60, 0.75), (1.52, 0.85)]):
            make_box(f"Door_Panel_{ci}_{ri}", (px, 0.187, pz), (0.30, 0.012, ph),
                     (0.86, 0.84, 0.78, 1.0))
    make_cyl("Door_Knob", (-1.27, 0.20, 0.98), 0.028, 0.045, COL_BRASS, axis='Y')
    make_door_hinges("Door_Hinge", edge_x=-0.47, edge_y=0.13,
                     edge_z_centers=[0.35, 1.03, 1.75], axis='X')
    for sgn in (-1, +1):
        make_box(f"Door_Casing_{sgn:+d}", (sgn * 0.51, 0.11, 1.06), (0.09, 0.05, 2.12),
                 CALDWELL_TRIM)
    make_box("Door_CasingHead", (0.0, 0.11, 2.16), (1.11, 0.05, 0.10), CALDWELL_TRIM)


# ═════════════════════════════════════════════════════════════════
# WINDOW — the lit upstairs window (ch5:113). Painted double-hung
# frame, meeting rail + muntins, casing, apron; the STOOL IS CUT
# DEEP — it is the windowsill the radio sits on (ch12:454). Aged
# lace panels pushed to the jambs so the set owns the opening.
# ═════════════════════════════════════════════════════════════════
def build_window():
    wy = ROOM_D
    make_box("Win_FrameT", (0.0, wy, WIN_HEAD - 0.03), (WIN_W, 0.14, 0.06),
             CALDWELL_TRIM)
    make_box("Win_FrameB", (0.0, wy, WIN_SILL + 0.03), (WIN_W, 0.14, 0.06),
             CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Jamb_{sgn:+d}", (sgn * (WIN_W / 2.0 - 0.03), wy, 1.55),
                 (0.06, 0.14, 1.20), CALDWELL_TRIM)
    make_box("Win_MeetingRail", (0.0, wy, 1.56), (WIN_W - 0.08, 0.10, 0.06),
             CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Muntin_{sgn:+d}", (sgn * 0.22, wy - 0.02, 1.86),
                 (0.035, 0.06, 0.54), CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_Casing_{sgn:+d}", (sgn * (WIN_W / 2.0 + 0.09), wy - 0.105, 1.55),
                 (0.10, 0.05, 1.40), CALDWELL_TRIM)
    make_box("Win_CasingHead", (0.0, wy - 0.105, WIN_HEAD + 0.08),
             (WIN_W + 0.28, 0.05, 0.10), CALDWELL_TRIM)
    # THE WINDOWSILL — deep stool board, proud into the room, that
    # carries the radio (ch12:454 "The radio, on the windowsill")
    make_box("Win_Stool", (0.0, wy - 0.24, WIN_SILL + 0.02), (WIN_W + 0.30, 0.38, 0.04),
             CALDWELL_TRIM)
    for sgn in (-1, +1):
        make_box(f"Win_StoolBracket_{sgn:+d}", (sgn * 0.52, wy - 0.38, WIN_SILL - 0.06),
                 (0.05, 0.08, 0.12), CALDWELL_TRIM)
    make_box("Win_Apron", (0.0, wy - 0.105, WIN_SILL - 0.05), (WIN_W + 0.16, 0.05, 0.09),
             CALDWELL_TRIM)
    # Lace panels on a brass rod, pushed to the jambs
    make_cyl("Curtain_Rod", (0.0, wy - 0.16, 2.28), 0.012, 1.70, COL_BRASS, axis='X')
    for sgn in (-1, +1):
        make_cyl(f"Curtain_Finial_{sgn:+d}", (sgn * 0.86, wy - 0.16, 2.28), 0.026, 0.05,
                 COL_BRASS, axis='X')
        make_box(f"Curtain_Panel_{sgn:+d}", (sgn * 0.72, wy - 0.155, 1.66),
                 (0.22, 0.030, 1.24), COL_CURTAIN)
        make_box(f"Curtain_Fold_{sgn:+d}", (sgn * 0.65, wy - 0.175, 1.62),
                 (0.08, 0.018, 1.14), (0.78, 0.74, 0.64, 1.0))


# ═════════════════════════════════════════════════════════════════
# THE RADIO (hero) — the 1989 shortwave Thomas put in the window
# when he got out (ch2:36), transmitting on 1776 kHz (ch5). On the
# windowsill: steel-and-bakelite case, round tuning dial with the
# lamp LIT (this scene is the transmission), band-scale strip,
# three knobs, toggle. THE STRAIGHT KEY on the little desk under
# the sill, cabled to the set (ch5:180 — "keys the Morse: Maya says
# hi"). A straight chair squared to the key. The longwire antenna
# climbs the jamb and leaves through the head corner.
# ═════════════════════════════════════════════════════════════════
def build_radio():
    rz = WIN_SILL + 0.04            # sill top 0.99
    ry = ROOM_D - 0.245             # centered on the deep stool
    # Case + face
    make_box("Radio_Case", (0.0, ry, rz + 0.105), (0.46, 0.26, 0.21), COL_RADIO_CASE)
    make_box("Radio_Face", (0.0, ry - 0.135, rz + 0.105), (0.40, 0.012, 0.17),
             COL_RADIO_FACE)
    make_box("Radio_Foot_W", (-0.18, ry, rz + 0.008), (0.06, 0.24, 0.016),
             P.METAL_BLACK)
    make_box("Radio_Foot_E", (+0.18, ry, rz + 0.008), (0.06, 0.24, 0.016),
             P.METAL_BLACK)
    # THE DIAL — round, lamp lit (transmitting, ch5:113)
    make_cyl("Radio_Dial", (-0.10, ry - 0.145, rz + 0.115), 0.055, 0.012, COL_DIAL_LIT,
             axis='Y', segments=12)
    make_cyl("Radio_DialRim", (-0.10, ry - 0.140, rz + 0.115), 0.062, 0.008,
             P.METAL_BLACK, axis='Y', segments=12)
    make_box("Radio_DialNeedle", (-0.10, ry - 0.152, rz + 0.118), (0.004, 0.004, 0.045),
             (0.20, 0.18, 0.16, 1.0))
    # Band scale strip + station line
    make_box("Radio_BandScale", (0.10, ry - 0.145, rz + 0.155), (0.16, 0.006, 0.030),
             (0.86, 0.80, 0.62, 1.0))
    make_box("Radio_BandMark", (0.085, ry - 0.150, rz + 0.155), (0.004, 0.004, 0.026),
             (0.72, 0.28, 0.20, 1.0))
    # Knobs + toggle
    for ki, kx in enumerate((0.02, 0.10, 0.18)):
        make_cyl(f"Radio_Knob_{ki}", (kx, ry - 0.148, rz + 0.055), 0.016, 0.018,
                 P.METAL_BLACK, axis='Y', segments=10)
    make_box("Radio_Toggle", (-0.10, ry - 0.150, rz + 0.045), (0.012, 0.014, 0.028),
             P.METAL_STEEL)
    # Speaker grille slits on the case top
    for gi in range(4):
        make_box(f"Radio_Grille_{gi}", (-0.14 + gi * 0.09, ry + 0.02, rz + 0.213),
                 (0.05, 0.16, 0.004), (0.14, 0.13, 0.12, 1.0))
    # THE LONGWIRE — chassis, up beside the east jamb, out under the
    # head (staying below the head fill at z 2.15 — the opening is
    # real, the wire must live in it)
    make_cyl("Antenna_Lead", (0.26, ry - 0.02, rz + 0.26), 0.004, 0.14, P.METAL_BLACK)
    make_cyl("Antenna_Cross", (0.42, ry - 0.02, 1.31), 0.004, 0.30, P.METAL_BLACK,
             axis='X')
    make_cyl("Antenna_Jamb", (0.56, ROOM_D - 0.09, 1.70), 0.004, 0.80, P.METAL_BLACK)
    make_cyl("Antenna_Out", (0.56, ROOM_D - 0.02, 2.08), 0.004, 0.16, P.METAL_BLACK,
             axis='Y')
    # Power cord down to the baseboard outlet
    make_cyl("Radio_Cord_Drop", (-0.20, ROOM_D - 0.12, 0.62), 0.005, 0.72,
             (0.30, 0.28, 0.26, 1.0))
    make_box("Outlet_Plate", (-0.20, ROOM_D - 0.105, 0.28), (0.08, 0.012, 0.12),
             CALDWELL_TRIM)
    # ── THE LITTLE DESK under the sill — the key lives here ──────
    dx, dy = 0.0, 4.42
    make_box("Desk_Top", (dx, dy, 0.72), (1.05, 0.48, 0.030), COL_WOOD)
    make_box("Desk_Apron", (dx, dy, 0.665), (0.92, 0.38, 0.06), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Desk_Leg_{li}", (dx + sx * 0.46, dy + sy * 0.18, 0.335),
                 (0.045, 0.045, 0.67), COL_WOOD_DK)
    # THE STRAIGHT KEY (ch5:180) — brass on a bakelite base
    make_box("Key_Base", (0.12, 4.36, 0.745), (0.09, 0.15, 0.020), COL_RADIO_CASE)
    make_box("Key_Lever", (0.12, 4.38, 0.775), (0.014, 0.13, 0.010), COL_BRASS)
    make_cyl("Key_Knob", (0.12, 4.315, 0.785), 0.016, 0.014, (0.16, 0.15, 0.14, 1.0),
             segments=10)
    make_cyl("Key_Pivot", (0.12, 4.42, 0.768), 0.010, 0.028, COL_BRASS, axis='X',
             segments=8)
    for ti, ty2 in enumerate((4.30, 4.44)):
        make_cyl(f"Key_Terminal_{ti}", (0.155, ty2, 0.762), 0.007, 0.014, COL_BRASS,
                 segments=8)
    # Key cable up to the set
    make_box("Key_Cable_Run", (0.19, 4.55, 0.735), (0.010, 0.22, 0.010),
             (0.30, 0.28, 0.26, 1.0))
    make_cyl("Key_Cable_Rise", (0.20, 4.665, 0.86), 0.005, 0.26,
             (0.30, 0.28, 0.26, 1.0))
    # Her log pad + pencil beside the key (register dressing — she
    # tells Thomas the day's news, ch5:161)
    make_box("LogPad", (-0.24, 4.38, 0.738), (0.15, 0.21, 0.012), P.PAPER_AGED)
    make_cyl("LogPencil", (-0.40, 4.42, 0.740), 0.0042, 0.125, (0.82, 0.64, 0.28, 1.0),
             axis='Y')
    # The chair, squared to the key ("at her shortwave radio")
    cx2, cy2 = 0.0, 3.72
    make_box("RadioChair_Seat", (cx2, cy2, 0.45), (0.42, 0.42, 0.045), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"RadioChair_Leg_{li}", (cx2 + sx * 0.17, cy2 + sy * 0.17, 0.225),
                 0.019, 0.45, COL_WOOD_DK)
    for pi, sgn in enumerate((-1, +1)):
        make_cyl(f"RadioChair_Post_{pi}", (cx2 + sgn * 0.17, cy2 - 0.20, 0.70),
                 0.017, 0.50, COL_WOOD)
    for si, sz in enumerate((0.74, 0.90)):
        make_box(f"RadioChair_Slat_{si}", (cx2, cy2 - 0.20, sz), (0.38, 0.032, 0.085),
                 COL_WOOD)
    # Her shawl over the chair back (an old woman at a cold window)
    make_box("Chair_Shawl", (cx2, cy2 - 0.225, 0.97), (0.40, 0.05, 0.20), COL_QUILT_DK)


# ═════════════════════════════════════════════════════════════════
# BED — head on the north wall east of the window, close enough
# that the edge is the second seat at the radio (ch5:165). Made,
# dusty-rose quilt, two pillows — and the covers TURNED BACK at the
# head corner, the way Maya leaves them (ch12:406 / ch21:368).
# ═════════════════════════════════════════════════════════════════
def build_bed():
    bx = 1.50                      # frame x 0.95..2.05
    y0, y1 = 2.90, 4.80            # foot..head
    by = (y0 + y1) / 2.0
    make_box("Bed_Rail", (bx, by, 0.34), (1.10, 1.90, 0.12), COL_WOOD)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Bed_Leg_{li}", (bx + sx * 0.50, by + sy * 0.89, 0.16), 0.032, 0.32,
                 COL_WOOD_DK)
    make_box("Bed_Headboard", (bx, y1 - 0.02, 0.68), (1.10, 0.06, 0.80), COL_WOOD)
    make_box("Bed_HeadboardCap", (bx, y1 - 0.02, 1.10), (1.14, 0.09, 0.05), COL_WOOD_DK)
    make_box("Bed_Footboard", (bx, y0 + 0.02, 0.52), (1.10, 0.05, 0.36), COL_WOOD)
    make_box("Bed_Mattress", (bx, by, 0.50), (1.06, 1.84, 0.18), COL_LINEN)
    # The quilt — made square, side drapes, stitch bands
    make_box("Quilt_Top", (bx, by - 0.10, 0.605), (1.08, 1.64, 0.050), COL_QUILT)
    make_box("Quilt_DrapeW", (bx - 0.545, by - 0.10, 0.44), (0.025, 1.64, 0.32),
             COL_QUILT)
    make_box("Quilt_DrapeE", (bx + 0.545, by - 0.10, 0.44), (0.025, 1.64, 0.32),
             COL_QUILT)
    make_box("Quilt_DrapeS", (bx, y0 + 0.045, 0.44), (1.08, 0.025, 0.32), COL_QUILT)
    for qi, qy in enumerate((3.35, 3.85, 4.35)):
        make_box(f"Quilt_Band_{qi}", (bx, qy, 0.633), (1.085, 0.16, 0.006), COL_QUILT_DK)
    # THE TURNED-BACK CORNER (ch12:406) — the quilt folded down at
    # the west half of the head, sheet showing (clear of the pillow
    # line at y 4.38)
    make_box("Quilt_TurnedBack", (bx - 0.27, 4.16, 0.645), (0.54, 0.42, 0.030),
             COL_LINEN)
    make_box("Quilt_TurnedEdge", (bx - 0.27, 3.93, 0.648), (0.54, 0.05, 0.036),
             COL_QUILT_DK)
    # Pillows
    make_box("Bed_Pillow_W", (bx - 0.26, y1 - 0.26, 0.68), (0.44, 0.32, 0.11), COL_LINEN)
    make_box("Bed_Pillow_E", (bx + 0.26, y1 - 0.26, 0.68), (0.44, 0.32, 0.11), COL_LINEN)
    # House slippers square beside the bed (register dressing)
    for shi, sy2 in enumerate((3.30, 3.48)):
        make_box(f"Slipper_{shi}", (0.82, sy2, 0.045), (0.22, 0.09, 0.07), COL_SLIPPER)


# ═════════════════════════════════════════════════════════════════
# NIGHTSTAND + DRESSER — the nightstand lamp ON (she is awake at
# eleven, ch5:113; Maya helps her into bed at the end, ch5:190),
# her water glass. The dresser on the west wall: doily, the small
# framed photograph (Thomas the photographer, ch2:41 — inferred
# dressing), her hairbrush dish.
# ═════════════════════════════════════════════════════════════════
def build_nightstand_and_dresser():
    # Nightstand east of the bed foot, against the east wall
    nx, ny = 1.90, 2.42
    make_box("Nightstand_Body", (nx, ny, 0.26), (0.42, 0.40, 0.52), COL_WOOD)
    make_box("Nightstand_Top", (nx, ny, 0.535), (0.46, 0.44, 0.03), COL_WOOD_DK)
    make_box("Nightstand_Drawer", (nx - 0.215, ny, 0.40), (0.015, 0.34, 0.14),
             COL_WOOD_DK)
    make_cyl("Nightstand_Knob", (nx - 0.23, ny, 0.40), 0.013, 0.03, COL_BRASS, axis='X')
    # THE LAMP — on (warm practical; the scene's OmniLight3D matches)
    make_cyl("Lamp_Base", (nx + 0.04, ny + 0.06, 0.565), 0.065, 0.025, COL_WOOD_DK)
    make_cyl("Lamp_Stem", (nx + 0.04, ny + 0.06, 0.70), 0.012, 0.26, COL_BRASS)
    make_cyl("Lamp_Shade", (nx + 0.04, ny + 0.06, 0.885), 0.095, 0.13, COL_LINEN,
             segments=12)
    make_cyl("Lamp_Glow", (nx + 0.04, ny + 0.06, 0.815), 0.040, 0.02, COL_LAMP_GLOW)
    # Her water glass on a crocheted coaster
    make_cyl("Night_Coaster", (nx - 0.10, ny - 0.10, 0.556), 0.045, 0.006, COL_QUILT_DK,
             segments=10)
    make_cyl("Night_WaterGlass", (nx - 0.10, ny - 0.10, 0.612), 0.030, 0.105,
             (0.74, 0.78, 0.76, 1.0), segments=10)
    # ── Dresser, west wall ───────────────────────────────────────
    dx, dy = -2.00, 3.30
    make_box("Dresser_Body", (dx, dy, 0.46), (0.50, 1.15, 0.92), COL_WOOD)
    make_box("Dresser_Top", (dx, dy, 0.935), (0.54, 1.19, 0.03), COL_WOOD_DK)
    for di in range(3):
        make_box(f"Dresser_DrawerSeam_{di}", (dx + 0.252, dy, 0.20 + di * 0.27),
                 (0.012, 1.05, 0.015), COL_WOOD_DK)
        for sgn in (-1, +1):
            make_cyl(f"Dresser_Knob_{di}_{sgn:+d}", (dx + 0.26, dy + sgn * 0.28,
                     0.33 + di * 0.27), 0.013, 0.03, COL_BRASS, axis='X')
    make_box("Dresser_Doily", (dx, dy, 0.955), (0.40, 0.62, 0.006), COL_CURTAIN)
    # The photograph — small frame, black-and-white (Thomas,
    # Graustark, the seventies; ch2:41 — inferred, not scene text)
    make_box("Photo_Frame", (dx - 0.02, dy + 0.30, 1.045), (0.030, 0.13, 0.17),
             COL_WOOD_DK)
    make_box("Photo_Print", (dx - 0.005, dy + 0.30, 1.045), (0.024, 0.10, 0.14),
             COL_PHOTO_GREY)
    make_box("Photo_Stand", (dx + 0.05, dy + 0.30, 0.99), (0.06, 0.03, 0.07),
             COL_WOOD_DK)
    # Hairbrush dish
    make_cyl("Dresser_Dish", (dx + 0.02, dy - 0.32, 0.965), 0.075, 0.018, COL_CERAMIC,
             segments=12)
    make_box("Dresser_Brush", (dx + 0.02, dy - 0.32, 0.985), (0.055, 0.16, 0.020),
             COL_WOOD_DK)


# ═════════════════════════════════════════════════════════════════
# RUG + CEILING — braided oval rug between door and radio corner;
# house dome fixture (NOT fluorescents), smoke detector, HVAC.
# ═════════════════════════════════════════════════════════════════
def build_rug_and_ceiling():
    for ri, (rr, rz2, tint) in enumerate([(0.72, 0.004, COL_RUG_A),
                                          (0.52, 0.007, COL_RUG_B),
                                          (0.32, 0.010, COL_RUG_C)]):
        make_cyl(f"Rug_Ring_{ri}", (-0.35, 2.35, rz2), rr, 0.008, tint, segments=16)
    make_cyl("DomeLight_Plate", (0.0, 2.50, CEIL - 0.015), 0.17, 0.025, COL_BRASS,
             segments=12)
    make_cyl("DomeLight_Dome", (0.0, 2.50, CEIL - 0.065), 0.145, 0.075,
             (0.97, 0.93, 0.82, 1.0), segments=12)
    make_cyl("DomeLight_Finial", (0.0, 2.50, CEIL - 0.115), 0.018, 0.03, COL_BRASS)
    make_smoke_detector("Smoke", (-1.0, 1.2, CEIL))
    make_hvac_vent("HVAC", (1.0, 0.8, CEIL), width=0.50, depth=0.30)


# ═════════════════════════════════════════════════════════════════
# EXTERIOR — second floor, front of the house (the lit window is
# street-visible, ch5:113): siding skins wrap the opening, the
# PORCH ROOF below (the porch of build_caldwell_porch_night.py),
# the cul-de-sac at grade, the CEDAR across the cul-de-sac (ch14),
# the GELLER porch light on (ch21:208), a dark tract massing — and
# THE WATER TOWER over the far rooflines at the end of Gallatin
# (vol6_ch1:44), the repeater that carries her Morse to the dogs.
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
                 (ROOM_W + 0.4, 0.006, 0.02), COL_SIDING_SEAM)
    # The porch roof below the window (the front porch's roof —
    # build_caldwell_porch_night.py; same treatment as Maya's file)
    make_box("PorchRoof_Deck", (0.0, 6.05, -0.62), (4.6, 2.10, 0.10), CALDWELL_ROOF)
    make_box("PorchRoof_Ridge", (0.0, 5.25, -0.50), (4.6, 0.30, 0.08), CALDWELL_ROOF)
    make_box("PorchRoof_Fascia", (0.0, 7.08, -0.68), (4.6, 0.06, 0.16), CALDWELL_TRIM)
    for gi, gx2 in enumerate((-2.1, 2.1)):
        make_box(f"PorchRoof_EndCap_{gi}", (gx2, 6.05, -0.64), (0.08, 2.10, 0.14),
                 CALDWELL_TRIM)
    # The cul-de-sac at grade: lawn / walk / street / far lawn
    make_box("Ext_Lawn", (0.0, 8.6, GRADE_Z - 0.05), (18.0, 3.4, 0.10), COL_NIGHT_LAWN)
    make_box("Ext_Walk", (-1.6, 8.6, GRADE_Z + 0.005), (0.9, 3.4, 0.012), COL_CONCRETE)
    make_box("Ext_Sidewalk", (0.0, 10.5, GRADE_Z - 0.02), (18.0, 0.8, 0.10),
             COL_CONCRETE)
    make_box("Ext_Street", (0.0, 12.6, GRADE_Z - 0.07), (18.0, 3.4, 0.10), COL_ASPHALT)
    make_box("Ext_FarLawn", (0.0, 15.6, GRADE_Z - 0.05), (18.0, 2.6, 0.10),
             COL_NIGHT_LAWN)
    # THE CEDAR across the cul-de-sac (ch14 — the cicadas live here)
    make_cyl("Cedar_Trunk", (-4.5, 14.2, GRADE_Z + 0.9), 0.14, 1.80, COL_WOOD_DK)
    for ti, (tr, tz, tc) in enumerate([(1.40, GRADE_Z + 2.25, COL_CEDAR_DK),
                                       (1.05, GRADE_Z + 3.15, COL_CEDAR),
                                       (0.72, GRADE_Z + 3.95, COL_CEDAR_DK),
                                       (0.42, GRADE_Z + 4.65, COL_CEDAR)]):
        make_cyl(f"Cedar_Tier_{ti}", (-4.5, 14.2, tz), tr, 0.85, tc, segments=10)
    # THE GELLER HOUSE at the end of the cul-de-sac — porch light ON
    gx, gy = 5.2, 15.8
    make_box("Geller_Body", (gx, gy, GRADE_Z + 1.5), (6.5, 4.2, 3.0), COL_GELLER_BODY)
    make_box("Geller_Roof0", (gx, gy, GRADE_Z + 3.24), (7.1, 4.8, 0.48), CALDWELL_ROOF)
    make_box("Geller_Roof1", (gx, gy, GRADE_Z + 3.68), (4.8, 3.2, 0.40), CALDWELL_ROOF)
    for wi, wx in enumerate((-1.9, 0.0)):
        make_box(f"Geller_Window_{wi}", (gx + wx, gy - 2.13, GRADE_Z + 1.6),
                 (0.85, 0.06, 0.75), COL_WINDOW_DARK)
    make_box("Geller_WindowLit", (gx + 1.9, gy - 2.13, GRADE_Z + 1.6),
             (0.85, 0.06, 0.75), COL_WINDOW_LIT)
    make_box("Geller_Door", (gx - 0.9, gy - 2.12, GRADE_Z + 1.0), (0.85, 0.06, 2.0),
             (0.22, 0.20, 0.19, 1.0))
    make_box("Geller_LightBracket", (gx - 1.45, gy - 2.10, GRADE_Z + 1.70),
             (0.06, 0.05, 0.10), P.METAL_BLACK)
    make_cyl("Geller_PorchLight", (gx - 1.45, gy - 2.16, GRADE_Z + 1.66), 0.055, 0.12,
             COL_PORCHBULB, segments=10)
    # A dark tract massing west — the street repeating
    make_box("TractW_Body", (-8.0, 15.4, GRADE_Z + 1.4), (5.8, 4.4, 2.8),
             (0.48, 0.46, 0.44, 1.0))
    make_box("TractW_Roof", (-8.0, 15.4, GRADE_Z + 3.02), (6.4, 5.0, 0.44),
             CALDWELL_ROOF)
    # ── THE WATER TOWER, end of Gallatin, over the far roofs ─────
    twx, twy = 2.8, 26.0
    for li, (lx, ly) in enumerate([(-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5),
                                   (1.5, 1.5)]):
        make_cyl(f"Tower_Leg_{li}", (twx + lx, twy + ly, GRADE_Z + 4.0), 0.12, 8.0,
                 COL_TOWER_DK, segments=8)
    make_cyl("Tower_Riser", (twx, twy, GRADE_Z + 5.5), 0.32, 11.0, COL_TOWER_DK,
             segments=10)
    make_cyl("Tower_Catwalk", (twx, twy, GRADE_Z + 8.4), 2.55, 0.08, COL_TOWER_DK,
             segments=12)
    make_cyl("Tower_Tank", (twx, twy, GRADE_Z + 10.1), 2.30, 3.10, COL_TOWER,
             segments=12)
    make_cyl("Tower_Dome", (twx, twy, GRADE_Z + 12.0), 1.72, 0.80, COL_TOWER,
             segments=12)
    make_cyl("Tower_Finial", (twx, twy, GRADE_Z + 12.6), 0.09, 0.50, COL_TOWER_DK)


def main():
    clear_scene()
    build_shell()
    build_door()
    build_window()
    build_radio()
    build_bed()
    build_nightstand_and_dresser()
    build_rug_and_ceiling()
    build_exterior()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/caldwell_radio_room_night.glb"))
    print(f"\n[build_caldwell_radio_room_night] exporting to {out}")
    export_glb(out)

if __name__ == "__main__":
    main()
