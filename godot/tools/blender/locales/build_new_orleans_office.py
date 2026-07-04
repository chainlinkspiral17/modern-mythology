"""VOL 5 · VII The Chariot — "Two Horses, One Wreck"
(vol5_ch7_chariot.json). Antonio D'Ambrosio's hot office above what
will, eventually, be Ember & Ash. August in New Orleans; the window
AC unit Jimmy installed losing at half capacity (L58); the carpet
showing the pacing route of a man with two speeds, gone and about
to be gone (L42, L134). Music register vol5_two_speeds
(music_catalog.json L1366): "The window unit losing, the voicemail
light blinking. Gone, and about to be gone." Antonio dies in the
scaffolding fall three chapters of story-time later
(_DAMBROSIO_FAMILY.md L76-78); Daigle keeps his drink on the menu
(L142-147). This is a room a dead man will leave.

ADJUDICATION — SAME diegetic room as the TAROT GAUNTLET locale
build_ember_ash_office.py (do NOT modify that file). The music
entry names this locale "Antonio's hot office above Ember & Ash"
and the gauntlet's scenarios (hot_office / option_four /
two_horses_one_wreck) are game-ified beats of this very chapter.
Two renders, one room. Where they agree we keep vocabulary
agreement: window AC unit in a window opening, desk with bourbon +
voicemail counter reading 11, a back stair Jimmy uses, a second
window onto the corner across the street. Where the CHAPTER prose
contradicts the gauntlet render, the chapter wins here:
  1. The phone is Antonio's CELL, face-down on the desk — "The
     screen said Q. PAUL" (L74), "He put the phone face-down on
     the desk" (L102), "He thumbed Jimmy" (L249) — not the
     gauntlet's rotary.
  2. The cypress beam is DOWNSTAIRS, being hung by the crew "for
     two days" and not going up straight (L122, L126) — it does
     NOT cross this office's ceiling.
  3. The floor is CARPET — "The carpet under the route showed the
     path" (L134) — not oak plank.
  4. The corner-view window is "the small leaded window" (L229).
The gauntlet docstring's "service garage in Lacombe" also differs
from the chapter's Marigny warehouse (L114, L229); chapter wins.

Canon dressed in (line numbers = vol5_ch7_chariot.json):
  · The S doorway = the door at the top of the rusted iron stair
    Antonio climbs (L50), the door the older man watches from the
    corner (L237). Left open — the Background3D camera sits in it.
  · The window AC unit, W wall — installed by Jimmy, half
    capacity, faint smell of melting plastic (L58; scorch streak
    on the grille), plywood shims in the side gaps (Jimmy's
    install), condensation stain below. It cycles 40 seconds and
    loses (L378), and by scene's end grinds and gives up (L468).
    Chapter never fixes its wall; the gauntlet used S, but the S
    wall here holds the camera doorway, so the unit goes W where
    the fixed VN camera can actually see it losing.
  · The small LEADED window (L229), E wall — a REAL opening
    (playbook: no glass), cypress frame, iron came lattice of
    small panes. Justifies the .tscn Fill_EastWindow light.
    Outside it, the streetlight the older man leaned against
    (L233) — unlit, it is 1:47 in the afternoon — with the street
    DOWN there: this is a second floor.
  · The back-stair door, N wall — Jimmy comes up the back way
    (L288), in through it with two coffees (L300), and leaves
    through it; "The office door clicked shut" (L553). Rendered
    CLOSED, with an open mullioned transom above it that lets the
    .tscn Back_HallSpill light through.
  · The desk (L62): the rolled architectural plans he dropped on
    it (L62, L472, banded), the half-empty bourbon (L62 — lower
    body dark "liquid behind glass", upper body paler "empty"),
    the chipped glass he poured one finger into (L292 — nick on
    the rim, residue in the bottom), the cell phone FACE-DOWN
    (L102, L472) full of unread Q. PAUL voicemails (L98),
    the answering machine with the red light and the counter at
    11 — the silt index (L98; "the voicemail light blinking",
    music_catalog.json L1366; counter value in agreement with the
    gauntlet render) — the two coffees Jimmy set down (L300),
    his own drained in three long swallows, lid off (L509), and
    the hire list, incomplete (L142): a legal pad with three
    lines and a lot of blank.
  · The banker's lamp, green glass — kept from the scaffold
    because the .tscn key light is NAMED Key_BankerGreen; shade
    rebuilt as a half-cylinder per the eye-level rule.
  · The file cabinet (L62 — he picked the bourbon up OFF it):
    NW corner, with the bottle's ring stain on top.
  · Forward-motion clutter of a man who never stops moving: the
    crate of spare plan rolls beside the cabinet (L62/L472
    vocabulary), the box of prospectus / publicity materials
    (L110), the August wall calendar with days struck off — four
    months behind schedule (L58, L142) — and the buildout
    blueprint pinned to the N wall behind the desk (L142, L221).
  · The pacing path worn into the carpet (L134): the eight-stride
    E-W route, the turnaround at the leaded window (L229), the
    shuffle patch behind the desk, the entry wear at the S door.
  · Clock frozen at 1:47 — the crew's thirty-minute lunch (L122,
    back at L468); the gauntlet runs two_horses_one_wreck, this
    chapter's subtitle, at 1:47 PM lunch. Same hour, both renders.
Canon-negatives (verified against the full scene):
  · NO BBS terminal / computer. Antonio is sysop of
    ember.ash.rest.bbs (_DAMBROSIO_FAMILY.md L76-77) but no
    machine is staged anywhere in vol5_ch7_chariot.json — the BBS
    diagnostic surface lives in ChariotVisualizer.gd, not in this
    room's geometry.
  · NO cypress beam in the office ceiling (L122 — it is
    downstairs, being hung, for two days).
  · NO rotary desk phone (the phone is the cell, L74/L102).
  · NO ashtray — nobody smokes in this office; the smoker is the
    older man outside on the corner (L233). Gauntlet-only prop.
  · NO figure of the older man — seen only through the window,
    and gone by L577.
  · The crew's radio (salsa, L468, L553) is downstairs behind the
    closed back-stair door — not modeled.
  · Scaffold's law-office dressing removed wholesale: bookcase,
    diplomas, wainscoting, floor plant, corded desk phone,
    inkwell — none staged; this is a jobsite office over an
    unfinished restaurant (L597).

Name dependencies checked: no script reads mesh names from this
GLB (LiminalProximityController.location_json is empty; MoodCycler
/ PDPRiffmaster are shader/music-only; Background3D.gd L195-202
references only the scene + GLB paths). The .tscn light NAMES are
honored by geometry: Key_BankerGreen -> the banker's lamp,
Fill_EastWindow -> the E leaded window opening, Back_HallSpill ->
the open transom over the N back-stair door.

Playbook compliance: shell footprint KEPT from the scaffold
(7 x 6 x 3.20 — the Background3D camera at the S door looking N
and the .tscn lights are tuned to it; the chapter's "twelve feet
by ten" (L134) cramp is carried by clutter + the pacing path
instead). All windows are REAL openings with frames/mullions, no
glass slabs, no alpha anywhere (the gauntlet bottle's 0.85-alpha
brown glass is NOT repeated — bourbon here is opaque two-tone).
Cylinders/spheres at eye level (lamp shades, bottle, cups, plan
rolls, pendant); boxes only for walls, casework, and appliances.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import (make_floor, make_wall, make_ceiling,
                              make_crown_molding, make_door_hinges)
from _props.decor import make_wall_clock, make_calendar
from _props.safety import make_smoke_detector

# Shell footprint — KEPT from the scaffold; the Background3D preset
# ("new_orleans_office", camera at the S door looking N, fov 60)
# and the .tscn lights are tuned to it.
ROOM_W = 7.0; ROOM_D = 6.0; CEIL = 3.20

# ── NOLA city register ────────────────────────────────────────────
# City-consistent hues, repeated by intent in build_new_orleans_bar
# .py, build_new_orleans_room.py, and this file. NOT a shared-venue
# block: the bar, the laundromat room, and the Ember & Ash office
# are separate sites in the same city. Constant lines byte-identical
# with both siblings.
NOLA_BRASS      = (0.80, 0.60, 0.28, 1.0)   # rails, knobs, finials
NOLA_CYPRESS    = (0.38, 0.26, 0.16, 1.0)   # old-growth trim wood
NOLA_CYPRESS_DK = (0.22, 0.14, 0.09, 1.0)
NOLA_IRON       = (0.17, 0.16, 0.15, 1.0)   # wrought / cast iron
NOLA_LINEN      = (0.84, 0.80, 0.72, 1.0)   # bar rag / bed linen
# ── end city register ─────────────────────────────────────────────

# Office-local palette — sweated plaster, jobsite carpet, salvage
# wood. August heat lives in the warm midtones.
PAL = {"wall": (0.76, 0.66, 0.50, 1.0), "baseboard": (0.30, 0.20, 0.13, 1.0)}
COL_CARPET       = (0.42, 0.33, 0.24, 1.0)  # tired jobsite carpet (L134)
COL_CARPET_SEAM  = (0.38, 0.30, 0.22, 1.0)  # low-contrast carpet-tile seams
COL_CARPET_PATH  = (0.31, 0.24, 0.17, 1.0)  # the pacing route (L134)
COL_CARPET_DAMP  = (0.33, 0.27, 0.20, 1.0)  # AC condensation (L58)
COL_PLASTER_CEIL = (0.84, 0.78, 0.66, 1.0)
COL_STAIN        = (0.64, 0.54, 0.40, 1.0)  # humidity blooms
COL_DESK         = (0.40, 0.28, 0.17, 1.0)  # salvage-wood desk
COL_DESK_DK      = (0.24, 0.16, 0.10, 1.0)
COL_LEATHER      = (0.36, 0.20, 0.14, 1.0)  # Antonio's chair
COL_LAMP_GREEN   = (0.16, 0.42, 0.22, 1.0)  # banker's-lamp glass
COL_BULB_WARM    = (0.95, 0.82, 0.46, 1.0)
COL_BOURBON_FULL = (0.42, 0.22, 0.10, 1.0)  # liquid behind brown glass
COL_BOURBON_AIR  = (0.56, 0.37, 0.19, 1.0)  # the half that is gone (L62)
COL_PHONE        = (0.13, 0.13, 0.14, 1.0)  # the cell, face-down (L102)
COL_VM_BODY      = (0.22, 0.20, 0.18, 1.0)
COL_VM_LED       = (0.96, 0.28, 0.16, 1.0)  # the voicemail light (music L1366)
COL_VM_LCD       = (0.20, 0.24, 0.20, 1.0)
COL_VM_DIGIT     = (0.30, 0.92, 0.44, 1.0)  # the silt counter (L98)
COL_CUP_PAPER    = (0.90, 0.87, 0.80, 1.0)  # Jimmy's coffee run (L300)
COL_CUP_LID      = (0.28, 0.24, 0.20, 1.0)
COL_LEGAL_PAD    = (0.92, 0.86, 0.44, 1.0)  # the hire list (L142)
COL_INK          = (0.15, 0.13, 0.12, 1.0)
COL_AC_BODY      = (0.85, 0.83, 0.76, 1.0)
COL_AC_GRILLE    = (0.60, 0.60, 0.57, 1.0)
COL_AC_LOUVER    = (0.44, 0.44, 0.40, 1.0)
COL_AC_SCORCH    = (0.42, 0.30, 0.19, 1.0)  # melting plastic (L58)
COL_PLY_SHIM     = (0.70, 0.56, 0.36, 1.0)  # Jimmy's install (L58)
COL_CARDBOARD    = (0.66, 0.52, 0.32, 1.0)
COL_BLUEPRINT    = (0.36, 0.46, 0.58, 1.0)  # the buildout drawing (L142)
COL_BLUEPRINT_LN = (0.86, 0.90, 0.94, 1.0)
COL_CAL_RED      = (0.72, 0.20, 0.16, 1.0)  # struck-off August days

DESK_CX, DESK_CY = -0.40, 4.20               # desk center
DESK_TOP_Z = 0.785                           # working surface top
BACK_DOOR_CX = 2.30                          # N-wall back-stair door


def build_shell():
    """Carpet floor + four walls. S: open camera doorway (the door
    at the top of the rusted iron stair, L50/L237). N: back-stair
    door zone (built in build_back_stair_door). E/W: hand-built
    piers around the two real window openings."""
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_CARPET, "seam": COL_CARPET_SEAM})
    # The pacing path (L134): eight strides E-W, the turnaround at
    # the leaded window (L229), the shuffle behind the desk, the
    # entry wear at the S door.
    make_box("Path_EW", (0.0, 2.55, 0.007), (5.40, 0.55, 0.002),
             COL_CARPET_PATH)
    make_box("Path_WindowTurn", (3.00, 2.45, 0.007), (0.80, 0.50, 0.002),
             COL_CARPET_PATH)
    make_box("Path_DeskShuffle", (DESK_CX, 5.05, 0.007), (1.20, 0.50, 0.002),
             COL_CARPET_PATH)
    make_box("Path_DoorWear", (0.0, 0.55, 0.007), (1.40, 0.80, 0.002),
             COL_CARPET_PATH)

    # S wall — door gap x in [-1.0, +1.0] (camera doorway), framed
    # posts + lintel + open mullioned transom, like the iron-stair
    # landing door it is (L50).
    make_wall("Wall_S_W", (-2.35, 0.0, 0), length=2.7, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+2.35, 0.0, 0), length=2.7, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    for psgn in (-1, +1):
        make_box(f"Door_S_Post_{psgn:+d}", (psgn * 1.05, 0.0, 1.10),
                 (0.10, 0.24, 2.20), NOLA_CYPRESS_DK)
    make_box("Door_S_Lintel", (0.0, 0.0, 2.25), (2.30, 0.22, 0.10),
             NOLA_CYPRESS_DK)
    for mi, mx in enumerate([-0.65, 0.0, 0.65]):
        make_box(f"Door_S_TransomMull_{mi}", (mx, 0.0, 2.55),
                 (0.05, 0.10, 0.50), NOLA_CYPRESS_DK)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, 3.00), (2.00, 0.20, 0.40),
             PAL["wall"])

    # N wall — back-stair door gap x in [1.85, 2.75] (Jimmy's door,
    # L288/L300/L553); slab + transom in build_back_stair_door.
    make_wall("Wall_N_W", (-0.925, ROOM_D, 0), length=5.55, height=CEIL,
              axis='X', palette=PAL, baseboard_face_sign=-1)
    make_wall("Wall_N_E", (+3.225, ROOM_D, 0), length=0.95, height=CEIL,
              axis='X', palette=PAL, baseboard_face_sign=-1)
    make_box("Wall_N_AboveDoor", (BACK_DOOR_CX, ROOM_D, 2.875),
             (0.90, 0.20, 0.65), PAL["wall"])

    # E wall — piers around the leaded-window opening
    # y in [1.7, 3.1], z in [1.05, 2.35]. Wall plane x = 3.5 ± 0.10.
    make_box("Wall_E_Pier_S", (ROOM_W / 2.0, 0.75, CEIL / 2.0),
             (0.20, 1.90, CEIL), PAL["wall"])
    make_box("Wall_E_Pier_N", (ROOM_W / 2.0, 4.65, CEIL / 2.0),
             (0.20, 3.10, CEIL), PAL["wall"])
    make_box("Wall_E_BelowSill", (ROOM_W / 2.0, 2.4, 0.525),
             (0.20, 1.40, 1.05), PAL["wall"])
    make_box("Wall_E_Header", (ROOM_W / 2.0, 2.4, 2.775),
             (0.20, 1.40, 0.85), PAL["wall"])
    make_box("Wall_E_Base", (ROOM_W / 2.0 - 0.13, ROOM_D / 2.0, 0.08),
             (0.06, ROOM_D + 0.4, 0.16), PAL["baseboard"])

    # W wall — piers around the AC-window opening
    # y in [2.2, 3.4], z in [1.05, 2.25].
    make_box("Wall_W_Pier_S", (-ROOM_W / 2.0, 1.0, CEIL / 2.0),
             (0.20, 2.40, CEIL), PAL["wall"])
    make_box("Wall_W_Pier_N", (-ROOM_W / 2.0, 4.8, CEIL / 2.0),
             (0.20, 2.80, CEIL), PAL["wall"])
    make_box("Wall_W_BelowSill", (-ROOM_W / 2.0, 2.8, 0.525),
             (0.20, 1.20, 1.05), PAL["wall"])
    make_box("Wall_W_Header", (-ROOM_W / 2.0, 2.8, 2.725),
             (0.20, 1.20, 0.95), PAL["wall"])
    make_box("Wall_W_Base", (-ROOM_W / 2.0 + 0.13, ROOM_D / 2.0, 0.08),
             (0.06, ROOM_D + 0.4, 0.16), PAL["baseboard"])

    # Plaster ceiling — a warehouse walk-up, no drop-tile grid.
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_PLASTER_CEIL},
                 with_grid=False, with_stains=False)
    # Humidity: ceiling bloom over the AC side, wall bloom high in
    # the SE corner. August in New Orleans (L58).
    make_box("Ceil_Stain_AC", (-2.6, 2.8, CEIL - 0.006),
             (0.70, 0.60, 0.004), (0.70, 0.62, 0.48, 1.0))
    make_box("Wall_E_Stain", (ROOM_W / 2.0 - 0.105, 0.9, 2.60),
             (0.015, 0.50, 0.45), COL_STAIN)
    for nm, ax, length, wx, wy in [
            ("Crown_W", 'Y', ROOM_D, -ROOM_W / 2.0 + 0.10, ROOM_D / 2.0),
            ("Crown_E", 'Y', ROOM_D, +ROOM_W / 2.0 - 0.10, ROOM_D / 2.0),
            ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D - 0.10),
            ("Crown_S", 'X', ROOM_W, 0.0, +0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": NOLA_CYPRESS})


def build_back_stair_door():
    """The back-stair door, N wall — Jimmy comes up the back way
    (L288), in with two coffees (L300), out again; 'The office door
    clicked shut' (L553). CLOSED slab, brass knob, iron hinges, and
    an OPEN mullioned transom above so the .tscn Back_HallSpill
    light reads as stairwell spill."""
    make_box("Door_N_Post_W", (1.80, ROOM_D, 1.025), (0.10, 0.24, 2.05),
             NOLA_CYPRESS_DK)
    make_box("Door_N_Post_E", (2.80, ROOM_D, 1.025), (0.10, 0.24, 2.05),
             NOLA_CYPRESS_DK)
    make_box("Door_N_Lintel", (BACK_DOOR_CX, ROOM_D, 2.09),
             (1.10, 0.22, 0.09), NOLA_CYPRESS_DK)
    # Open transom 2.135..2.55 — two mullions, NO glass.
    for mi, mx in enumerate([2.08, 2.52]):
        make_box(f"Door_N_TransomMull_{mi}", (mx, ROOM_D, 2.345),
                 (0.05, 0.10, 0.42), NOLA_CYPRESS_DK)
    # The slab, shut (L553).
    make_box("Door_N_Slab", (BACK_DOOR_CX, ROOM_D, 1.025),
             (0.86, 0.06, 2.03), NOLA_CYPRESS)
    make_cyl("Door_N_Knob", (1.95, ROOM_D - 0.055, 0.98), 0.024, 0.05,
             NOLA_BRASS, axis='Y', segments=8)
    make_box("Door_N_LockPlate", (1.95, ROOM_D - 0.033, 0.98),
             (0.06, 0.006, 0.16), NOLA_BRASS)
    make_door_hinges("Door_N_Hinge", edge_x=2.70, edge_y=ROOM_D - 0.04,
                     edge_z_centers=[0.35, 1.05, 1.75], axis='X',
                     palette={"col": NOLA_IRON})


def build_leaded_window():
    """The small leaded window (L229), E wall — a REAL opening,
    cypress frame, iron came lattice of small panes, no glass.
    Where Antonio stands and sees the older man (L233), where Jimmy
    stands at the angle that cannot be seen (L313). Outside: the
    streetlight the man leaned on (L233), unlit at 1:47 PM, its
    pole running DOWN — the street is a story below (L50)."""
    wx = ROOM_W / 2.0
    make_box("Leaded_Head", (wx, 2.4, 2.39), (0.24, 1.52, 0.08),
             NOLA_CYPRESS)
    for jsgn in (-1, +1):
        make_box(f"Leaded_Jamb_{jsgn:+d}", (wx, 2.4 + jsgn * 0.73, 1.70),
                 (0.24, 0.08, 1.42), NOLA_CYPRESS)
    make_box("Leaded_Sill_In", (wx - 0.12, 2.4, 1.015), (0.14, 1.56, 0.05),
             NOLA_CYPRESS)
    make_box("Leaded_Sill_Out", (wx + 0.12, 2.4, 1.01), (0.10, 1.56, 0.05),
             NOLA_CYPRESS)
    # Came lattice — 3 x 3 iron strips = 16 small panes of open air.
    for vi, vy in enumerate([2.05, 2.40, 2.75]):
        make_box(f"Leaded_CameV_{vi}", (wx, vy, 1.70), (0.05, 0.03, 1.30),
                 NOLA_IRON)
    for hi, hz in enumerate([1.375, 1.70, 2.025]):
        make_box(f"Leaded_CameH_{hi}", (wx, 2.4, hz), (0.05, 1.40, 0.03),
                 NOLA_IRON)
    # The streetlight on the corner across (L233) — head near our
    # floor height, pole dropping to the street below.
    make_cyl("Streetlight_Pole", (5.60, 2.50, -1.30), 0.06, 4.60,
             NOLA_IRON, segments=8)
    make_cyl("Streetlight_Arm", (5.35, 2.50, 0.95), 0.035, 0.50,
             NOLA_IRON, axis='X', segments=6)
    make_cyl("Streetlight_Head", (5.10, 2.50, 0.88), 0.10, 0.14,
             (0.13, 0.13, 0.12, 1.0), segments=10)


def build_ac_window():
    """The window AC unit, W wall (L58): installed by Jimmy, runs
    at half capacity with a faint smell of melting plastic and a
    personality. Cycles on for forty seconds and loses (L378);
    grinds and gives up at scene's end (L468). Real opening; the
    lower sash is dropped onto the unit's spine, plywood shims fill
    Jimmy's side gaps, and the condensation has already been at
    the carpet."""
    wx = -ROOM_W / 2.0
    make_box("ACWin_Head", (wx, 2.8, 2.29), (0.24, 1.32, 0.08),
             NOLA_CYPRESS)
    for jsgn in (-1, +1):
        make_box(f"ACWin_Jamb_{jsgn:+d}", (wx, 2.8 + jsgn * 0.63, 1.65),
                 (0.24, 0.08, 1.32), NOLA_CYPRESS)
    make_box("ACWin_Sill_In", (wx + 0.12, 2.8, 1.015), (0.14, 1.36, 0.05),
             NOLA_CYPRESS)
    make_box("ACWin_Sill_Out", (wx - 0.12, 2.8, 1.01), (0.10, 1.36, 0.05),
             NOLA_CYPRESS)
    # The unit — body through the wall, grille into the room.
    make_box("WindowAC_Body", (wx + 0.02, 2.8, 1.33), (0.60, 0.72, 0.52),
             COL_AC_BODY)
    make_box("WindowAC_Grille", (wx + 0.325, 2.8, 1.33),
             (0.012, 0.64, 0.44), COL_AC_GRILLE)
    for li in range(5):
        make_box(f"WindowAC_Louver_{li}", (wx + 0.334, 2.76, 1.16 + li * 0.08),
                 (0.006, 0.48, 0.018), COL_AC_LOUVER)
    for ki, kz in enumerate([1.20, 1.44]):
        make_cyl(f"WindowAC_Knob_{ki}", (wx + 0.34, 3.06, kz), 0.018, 0.03,
                 NOLA_BRASS, axis='X', segments=8)
    # The melting-plastic tell (L58) — scorch browning at the vent top.
    make_box("WindowAC_Scorch", (wx + 0.335, 2.94, 1.52),
             (0.005, 0.14, 0.05), COL_AC_SCORCH)
    # Jimmy's plywood shims in the side gaps (L58: installed by Jimmy).
    make_box("WindowAC_Shim_S", (wx, 2.32, 1.33), (0.16, 0.24, 0.52),
             COL_PLY_SHIM)
    make_box("WindowAC_Shim_N", (wx, 3.28, 1.33), (0.16, 0.24, 0.52),
             COL_PLY_SHIM)
    # Lower sash dropped onto the unit; open upper sash above (no glass).
    make_box("ACWin_SashRail", (wx, 2.8, 1.63), (0.10, 1.24, 0.07),
             NOLA_CYPRESS_DK)
    for ssgn in (-1, +1):
        make_box(f"ACWin_SashStile_{ssgn:+d}", (wx, 2.8 + ssgn * 0.58, 1.95),
                 (0.05, 0.05, 0.58), NOLA_CYPRESS_DK)
    make_box("ACWin_SashMuntin", (wx, 2.8, 1.95), (0.05, 0.04, 0.58),
             NOLA_CYPRESS_DK)
    # Power cord drooping to the outlet — Jimmy did not hide it.
    make_cyl("WindowAC_Cord_Jog", (wx + 0.115, 3.25, 1.07), 0.008, 0.18,
             NOLA_IRON, axis='Y', segments=6)
    make_cyl("WindowAC_Cord_Drop", (wx + 0.115, 3.34, 0.72), 0.008, 0.70,
             NOLA_IRON, segments=6)
    make_box("WindowAC_Outlet", (wx + 0.11, 3.34, 0.33), (0.012, 0.08, 0.12),
             (0.88, 0.84, 0.74, 1.0))
    # Condensation: run down the wall, damp patch in the carpet.
    make_box("WindowAC_DripStain", (wx + 0.105, 2.72, 0.70),
             (0.012, 0.22, 0.66), COL_STAIN)
    make_box("Carpet_Damp_AC", (wx + 0.45, 2.8, 0.008), (0.50, 0.55, 0.002),
             COL_CARPET_DAMP)


def build_desk():
    """Antonio's desk, center-north, facing the room and the S
    doorway. Salvage-wood — a jobsite desk over an unfinished
    restaurant (L597), not the scaffold's law-office oak suite."""
    make_box("Desk_Top", (DESK_CX, DESK_CY, 0.76), (1.90, 0.95, 0.05),
             COL_DESK)
    for sgn in (-1, +1):
        make_box(f"Desk_Pedestal_{sgn:+d}",
                 (DESK_CX + sgn * 0.70, DESK_CY, 0.3675),
                 (0.46, 0.85, 0.735), COL_DESK_DK)
        for di, dz in enumerate([0.18, 0.40, 0.62]):
            make_box(f"Desk_Drawer_{sgn:+d}_{di}",
                     (DESK_CX + sgn * 0.70, DESK_CY + 0.435, dz),
                     (0.38, 0.02, 0.17), COL_DESK)
            make_cyl(f"Desk_Knob_{sgn:+d}_{di}",
                     (DESK_CX + sgn * 0.70, DESK_CY + 0.455, dz),
                     0.014, 0.03, NOLA_BRASS, axis='Y', segments=8)
    make_box("Desk_Modesty", (DESK_CX, DESK_CY - 0.41, 0.42),
             (0.94, 0.04, 0.62), COL_DESK_DK)


def build_desk_props():
    """The day's still life (L62, L472): plans, bourbon, the
    chipped glass, the cell face-down, the answering machine's
    light, two coffees, the incomplete hire list, and the banker's
    lamp the .tscn key light is named for."""
    # Rolled architectural plans (L62, L472) — two banded rolls, W end.
    make_cyl("Plans_Roll_A", (-1.00, 4.02, DESK_TOP_Z + 0.035), 0.035, 0.62,
             P.PAPER, axis='X', segments=8)
    make_cyl("Plans_Roll_A_Band", (-0.80, 4.02, DESK_TOP_Z + 0.035),
             0.037, 0.02, (0.60, 0.32, 0.24, 1.0), axis='X', segments=8)
    make_cyl("Plans_Roll_B", (-0.96, 4.095, DESK_TOP_Z + 0.098), 0.033, 0.58,
             P.PAPER_AGED, axis='X', segments=8)
    make_cyl("Plans_Roll_B_Band", (-0.78, 4.095, DESK_TOP_Z + 0.098),
             0.035, 0.02, (0.60, 0.32, 0.24, 1.0), axis='X', segments=8)
    # The half-empty bourbon (L62), recapped, at his elbow (L292).
    # Opaque two-tone: dark liquid-behind-glass below, paler empty
    # glass above — the half that is gone reads at a glance.
    bx, by = 0.45, 4.35
    make_cyl("Bourbon_Body_Full", (bx, by, DESK_TOP_Z + 0.065), 0.042, 0.13,
             COL_BOURBON_FULL, segments=10)
    make_cyl("Bourbon_Body_Air", (bx, by, DESK_TOP_Z + 0.175), 0.042, 0.09,
             COL_BOURBON_AIR, segments=10)
    make_cyl("Bourbon_Label", (bx, by, DESK_TOP_Z + 0.075), 0.0435, 0.055,
             P.PAPER_AGED, segments=10)
    make_cyl("Bourbon_Shoulder", (bx, by, DESK_TOP_Z + 0.235), 0.030, 0.03,
             COL_BOURBON_AIR, segments=10)
    make_cyl("Bourbon_Neck", (bx, by, DESK_TOP_Z + 0.295), 0.016, 0.09,
             COL_BOURBON_AIR, segments=8)
    make_cyl("Bourbon_Cap", (bx, by, DESK_TOP_Z + 0.355), 0.019, 0.03,
             (0.20, 0.14, 0.10, 1.0), segments=8)
    # The chipped glass (L292) — one finger poured, drunk; residue
    # in the bottom, a pale nick on the rim.
    make_cyl("ChippedGlass_Body", (0.62, 4.18, DESK_TOP_Z + 0.045),
             0.032, 0.09, (0.78, 0.80, 0.76, 1.0), segments=10)
    make_cyl("ChippedGlass_Residue", (0.62, 4.18, DESK_TOP_Z + 0.008),
             0.026, 0.008, COL_BOURBON_FULL, segments=8)
    make_box("ChippedGlass_Nick", (0.651, 4.18, DESK_TOP_Z + 0.085),
             (0.008, 0.010, 0.012), (0.90, 0.92, 0.88, 1.0))
    # The cell, FACE-DOWN (L102, L472) — full of unread Q. PAUL.
    make_box("CellPhone_FaceDown", (-0.15, 4.32, DESK_TOP_Z + 0.007),
             (0.075, 0.150, 0.014), COL_PHONE)
    make_box("CellPhone_CameraDot", (-0.13, 4.375, DESK_TOP_Z + 0.0155),
             (0.018, 0.018, 0.002), (0.06, 0.06, 0.07, 1.0))
    # The answering machine — the red light, the counter at 11: the
    # silt index (L98; music_catalog.json L1366; counter agrees
    # with the gauntlet render). Front faces Antonio's chair (N).
    vx, vy = 0.10, 4.44
    make_box("Voicemail_Body", (vx, vy, DESK_TOP_Z + 0.032),
             (0.24, 0.16, 0.064), COL_VM_BODY)
    make_box("Voicemail_CassetteLid", (vx - 0.02, vy - 0.01,
             DESK_TOP_Z + 0.066), (0.14, 0.10, 0.003),
             (0.16, 0.15, 0.14, 1.0))
    make_box("Voicemail_LED", (vx + 0.085, vy + 0.082, DESK_TOP_Z + 0.050),
             (0.012, 0.002, 0.012), COL_VM_LED)
    make_box("Voicemail_LCD_Bg", (vx - 0.04, vy + 0.082, DESK_TOP_Z + 0.038),
             (0.055, 0.002, 0.024), COL_VM_LCD)
    for ci, cxo in enumerate([-0.015, +0.012]):
        make_box(f"Voicemail_LCD_Digit_{ci}",
                 (vx - 0.04 + cxo, vy + 0.083, DESK_TOP_Z + 0.038),
                 (0.005, 0.002, 0.018), COL_VM_DIGIT)
    # Two coffees (L300). Antonio's, lidded, untouched; Jimmy's,
    # drained in three long swallows, lid off beside it (L509).
    make_cyl("Coffee_Antonio_Cup", (-0.55, 4.45, DESK_TOP_Z + 0.065),
             0.038, 0.13, COL_CUP_PAPER, segments=10)
    make_cyl("Coffee_Antonio_Lid", (-0.55, 4.45, DESK_TOP_Z + 0.137),
             0.040, 0.015, COL_CUP_LID, segments=10)
    make_cyl("Coffee_Jimmy_Cup", (0.28, 3.92, DESK_TOP_Z + 0.065),
             0.038, 0.13, COL_CUP_PAPER, segments=10)
    make_cyl("Coffee_Jimmy_Lid_Off", (0.40, 3.88, DESK_TOP_Z + 0.004),
             0.040, 0.008, COL_CUP_LID, segments=10)
    # The hire list, incomplete (L142) — three lines, then blank.
    make_box("HireList_Pad", (-0.62, 4.05, DESK_TOP_Z + 0.004),
             (0.22, 0.30, 0.008), COL_LEGAL_PAD)
    for hi, hy in enumerate([4.16, 4.12, 4.08]):
        make_box(f"HireList_Line_{hi}", (-0.63, hy, DESK_TOP_Z + 0.0085),
                 (0.16, 0.012, 0.001), COL_INK)
    make_cyl("HireList_Pen", (-0.47, 4.00, DESK_TOP_Z + 0.012), 0.005, 0.13,
             COL_INK, axis='Y', segments=6)
    # Banker's lamp, rear E corner — the .tscn key light is NAMED
    # Key_BankerGreen for this. Half-cylinder green shade per the
    # eye-level rule (scaffold's box shade replaced).
    make_cyl("BankerLamp_Base", (0.90, 4.52, DESK_TOP_Z + 0.015), 0.07, 0.03,
             NOLA_BRASS, segments=10)
    make_cyl("BankerLamp_Stem", (0.90, 4.52, DESK_TOP_Z + 0.12), 0.011, 0.18,
             NOLA_BRASS, segments=6)
    make_cyl("BankerLamp_Shade", (0.90, 4.52, DESK_TOP_Z + 0.235), 0.085,
             0.34, COL_LAMP_GREEN, axis='X', segments=10)
    make_cyl("BankerLamp_Bulb", (0.90, 4.52, DESK_TOP_Z + 0.195), 0.030,
             0.22, COL_BULB_WARM, axis='X', segments=8)


def build_chairs():
    """Antonio's leather swivel behind the desk; the plain wooden
    chair Jimmy takes — 'Okay. Sit down.' (L305) — south of it."""
    make_box("Chair_A_Seat", (DESK_CX, 5.10, 0.50), (0.55, 0.50, 0.09),
             COL_LEATHER)
    make_box("Chair_A_Back", (DESK_CX, 5.34, 1.02), (0.55, 0.07, 0.85),
             COL_LEATHER)
    make_cyl("Chair_A_Pillar", (DESK_CX, 5.10, 0.28), 0.035, 0.36,
             P.METAL_BLACK, segments=8)
    make_cyl("Chair_A_Base", (DESK_CX, 5.10, 0.03), 0.26, 0.04,
             P.METAL_BLACK, segments=10)
    # The visitor chair, facing the desk.
    make_box("Chair_J_Seat", (0.85, 3.30, 0.455), (0.42, 0.40, 0.045),
             NOLA_CYPRESS)
    for li, (lx, ly) in enumerate([(0.67, 3.13), (1.03, 3.13),
                                    (0.67, 3.47), (1.03, 3.47)]):
        make_cyl(f"Chair_J_Leg_{li}", (lx, ly, 0.2175), 0.018, 0.435,
                 NOLA_CYPRESS_DK, segments=6)
    for bi, bx in enumerate([0.67, 1.03]):
        make_cyl(f"Chair_J_BackPost_{bi}", (bx, 3.14, 0.73), 0.018, 0.50,
                 NOLA_CYPRESS_DK, segments=6)
    for si, sz in enumerate([0.76, 0.91]):
        make_box(f"Chair_J_BackSlat_{si}", (0.85, 3.14, sz),
                 (0.40, 0.03, 0.07), NOLA_CYPRESS)


def build_file_cabinet_corner():
    """NW corner: the file cabinet the bourbon lived on (L62) —
    ring stain on top where the bottle sat — plus the forward-
    motion clutter of a man who never stops moving: the crate of
    spare plan rolls and the box of prospectus / publicity
    materials the LLC's name went onto instead of his (L110)."""
    make_box("FileCab_Body", (-3.02, 5.45, 0.66), (0.55, 0.62, 1.32),
             COL_DESK_DK)
    make_box("FileCab_Top", (-3.02, 5.45, 1.335), (0.58, 0.65, 0.03),
             COL_DESK)
    for di, dz in enumerate([0.28, 0.58, 0.88, 1.18]):
        make_box(f"FileCab_Drawer_{di}", (-2.735, 5.45, dz),
                 (0.02, 0.54, 0.24), COL_DESK)
        make_box(f"FileCab_Handle_{di}", (-2.722, 5.45, dz + 0.06),
                 (0.012, 0.16, 0.02), NOLA_BRASS)
    # The bottle's ring stain (L62: picked up ... FROM the file cabinet).
    make_cyl("FileCab_RingStain", (-2.95, 5.32, 1.352), 0.045, 0.003,
             (0.16, 0.10, 0.07, 1.0), segments=12)
    make_cyl("FileCab_RingStain_In", (-2.95, 5.32, 1.3545), 0.034, 0.003,
             COL_DESK, segments=12)
    # Crate of spare plan rolls (L62/L472 vocabulary).
    make_box("PlanCrate", (-2.95, 4.62, 0.25), (0.45, 0.45, 0.50),
             NOLA_CYPRESS_DK)
    for ri, (rx, ry, rc) in enumerate([(-3.05, 4.57, P.PAPER),
                                        (-2.90, 4.72, P.PAPER_AGED),
                                        (-2.85, 4.54, P.PAPER)]):
        make_cyl(f"PlanCrate_Roll_{ri}", (rx, ry, 0.62), 0.032, 0.72, rc,
                 segments=8)
    # The prospectus box (L110) — open flaps, print stack inside.
    make_box("ProspectusBox", (-2.30, 5.55, 0.14), (0.40, 0.30, 0.28),
             COL_CARDBOARD)
    make_box("ProspectusBox_Flap_N", (-2.30, 5.73, 0.285),
             (0.40, 0.06, 0.010), COL_CARDBOARD)
    make_box("ProspectusBox_Flap_S", (-2.30, 5.37, 0.285),
             (0.40, 0.06, 0.010), COL_CARDBOARD)
    make_box("ProspectusBox_Stack", (-2.30, 5.55, 0.26), (0.32, 0.22, 0.05),
             P.PAPER)
    make_box("ProspectusBox_TitleBand", (-2.30, 5.55, 0.2865),
             (0.20, 0.04, 0.001), COL_INK)


def build_wall_dressing():
    """The buildout blueprint behind the desk (L142, L221), the
    clock frozen at the lunch hour, the August calendar losing
    days to a schedule four months behind (L58, L142)."""
    # Blueprint pinned to the N wall — pale plan lines on blue.
    make_box("Blueprint_Sheet", (DESK_CX, ROOM_D - 0.065, 2.00),
             (0.90, 0.008, 0.60), COL_BLUEPRINT)
    make_box("Blueprint_Border_T", (DESK_CX, ROOM_D - 0.070, 2.24),
             (0.74, 0.002, 0.015), COL_BLUEPRINT_LN)
    make_box("Blueprint_Border_B", (DESK_CX, ROOM_D - 0.070, 1.76),
             (0.74, 0.002, 0.015), COL_BLUEPRINT_LN)
    for psgn in (-1, +1):
        make_box(f"Blueprint_Border_{psgn:+d}",
                 (DESK_CX + psgn * 0.37, ROOM_D - 0.070, 2.00),
                 (0.015, 0.002, 0.44), COL_BLUEPRINT_LN)
    # Plan rooms — the dining floor, the kitchen, the bar run.
    make_box("Blueprint_Room_A", (DESK_CX - 0.16, ROOM_D - 0.071, 2.06),
             (0.22, 0.002, 0.18), COL_BLUEPRINT_LN)
    make_box("Blueprint_Room_A_In", (DESK_CX - 0.16, ROOM_D - 0.072, 2.06),
             (0.19, 0.002, 0.15), COL_BLUEPRINT)
    make_box("Blueprint_Room_B", (DESK_CX + 0.14, ROOM_D - 0.071, 2.10),
             (0.18, 0.002, 0.12), COL_BLUEPRINT_LN)
    make_box("Blueprint_Room_B_In", (DESK_CX + 0.14, ROOM_D - 0.072, 2.10),
             (0.15, 0.002, 0.09), COL_BLUEPRINT)
    make_box("Blueprint_TitleBlock", (DESK_CX + 0.24, ROOM_D - 0.071, 1.84),
             (0.16, 0.002, 0.07), COL_BLUEPRINT_LN)
    for pi, (px, pz) in enumerate([(-0.42, 2.27), (0.44, 2.27),
                                    (-0.42, 1.73), (0.44, 1.73)]):
        make_cyl(f"Blueprint_Pin_{pi}", (DESK_CX + px + 0.40 - 0.40,
                 ROOM_D - 0.06, pz), 0.008, 0.02, NOLA_BRASS, axis='Y',
                 segments=6)
    # Clock frozen at 1:47 — the crew's thirty-minute lunch (L122,
    # back at L468); the gauntlet runs this chapter's scenario,
    # two_horses_one_wreck, at 1:47 PM. Same hour, both renders.
    make_wall_clock("Clock", (1.20, ROOM_D - 0.12, 2.55), frozen_hour=1,
                    frozen_min=47)
    # August calendar, W wall (L58) — days struck off in red; the
    # buildout is four months behind (L142).
    make_calendar("Calendar_Aug", (-3.39, 4.55, 1.90))
    for xi, xy in enumerate([4.42, 4.50, 4.58]):
        make_box(f"Calendar_Strike_{xi}", (-3.386, xy, 1.80),
                 (0.001, 0.03, 0.03), COL_CAL_RED)


def build_ceiling_infra():
    """One warm pendant over the desk; a smoke detector. Nothing
    corporate — no fluorescent troughs in a warehouse walk-up (the
    scaffold's unused import dropped). The heat is the fixture."""
    make_cyl("Pendant_Cord", (DESK_CX, DESK_CY, CEIL - 0.25), 0.006, 0.50,
             NOLA_IRON, segments=6)
    make_cyl("Pendant_Shade", (DESK_CX, DESK_CY, CEIL - 0.58), 0.17, 0.16,
             (0.30, 0.22, 0.14, 1.0), segments=12)
    make_cyl("Pendant_Bulb", (DESK_CX, DESK_CY, CEIL - 0.70), 0.045, 0.08,
             COL_BULB_WARM, segments=10)
    make_smoke_detector("Smoke", (1.4, 2.0, CEIL))


def main():
    clear_scene()
    build_shell()
    build_back_stair_door()
    build_leaded_window()
    build_ac_window()
    build_desk()
    build_desk_props()
    build_chairs()
    build_file_cabinet_corner()
    build_wall_dressing()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/new_orleans_office.glb"))
    print(f"\n[build_new_orleans_office] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
