"""VII · CHARIOT — Ember + Ash office. A second-floor business
office above a service garage in Lacombe. Antonio's place.

Three of four Chariot scenarios run here:
  hot_office             · 11:14 AM Tuesday · window AC half-capacity
  option_four            · 4:18 PM late day · silt at 5, Paul has
                           called 11 times, the older man on the
                           corner
  two_horses_one_wreck   · 1:47 PM lunch · the older man appears at
                           turn 2, the Corner Across threshold

Per the setup scene_descriptions, the office holds:
  · A window AC unit running at half capacity (south wall)
  · A bottle of bourbon on the desk (always)
  · The cypress beam (structural cypress crossing the ceiling —
    "the cypress beam is the cypress beam")
  · A back stair (Jimmy comes up it; the actual stair runs down
    to the crew + radio audible from below)
  · Antonio's desk (with rotary phone, voicemail machine showing
    a 2-digit counter, the bourbon, an ashtray, the rolodex)
  · A second window — the CORNER ACROSS — facing the street corner
    where the older man in the charcoal suit appears
  · A wall photograph of an early ember-and-ash crew (the
    historical anchor)
  · A radio downstairs (the crew's radio — only visible as a hint
    through the back stair opening)

COORDINATE FRAME (Blender → Godot):
    +X east   → +X
    +Y north  → -Z
    +Z up     → +Y
1 unit = 1 m. Footprint 6m × 5m, second floor (FLOOR_Z = 3.20).

Run:
    blender --background --python build_ember_ash_office.py
    (or ./run_cathedral.sh build_ember_ash_office.py)

Output: godot/assets/3d/locales/ember_ash_office.glb
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling, make_crown_molding, make_window
from _props.decor import make_wall_clock, make_faded_poster
from _props.safety import make_smoke_detector

# ── Palette ─────────────────────────────────────────────────────
PAL = {"wall": (0.82, 0.74, 0.58, 1.0), "baseboard": (0.36, 0.26, 0.16, 1.0)}
COL_FLOOR_OAK   = (0.46, 0.32, 0.20, 1.0)
COL_FLOOR_SEAM  = (0.32, 0.20, 0.10, 1.0)
COL_CYPRESS     = (0.74, 0.60, 0.42, 1.0)   # the cypress beam
COL_CYPRESS_DK  = (0.52, 0.40, 0.26, 1.0)
COL_DESK_TOP    = (0.30, 0.22, 0.14, 1.0)
COL_DESK_LEG    = (0.20, 0.14, 0.08, 1.0)
COL_LEATHER_OX  = (0.42, 0.22, 0.16, 1.0)
COL_PHONE       = (0.18, 0.16, 0.14, 1.0)
COL_PHONE_DIAL  = (0.30, 0.26, 0.20, 1.0)
COL_BOURBON_BTL = (0.32, 0.20, 0.12, 0.85)  # brown glass
COL_BOURBON_LIQ = (0.56, 0.32, 0.16, 1.0)
COL_VOICEMAIL   = (0.20, 0.18, 0.16, 1.0)
COL_VM_LED      = (0.96, 0.40, 0.18, 1.0)   # red LED
COL_VM_DIGIT    = (0.18, 0.96, 0.40, 1.0)   # mint LCD
COL_ASHTRAY     = (0.34, 0.30, 0.24, 1.0)
COL_PAPER       = (0.92, 0.88, 0.78, 1.0)
COL_ROLODEX     = (0.16, 0.14, 0.12, 1.0)
COL_AC_BODY     = (0.86, 0.84, 0.78, 1.0)
COL_AC_GRILLE   = (0.62, 0.62, 0.60, 1.0)
COL_BRASS       = (0.78, 0.62, 0.30, 1.0)
COL_RADIO_BODY  = (0.40, 0.30, 0.22, 1.0)

ROOM_W = 6.0; ROOM_D = 5.0; CEIL = 2.80


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": COL_FLOOR_OAK, "seam": COL_FLOOR_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=-1)
    # South wall split for the AC window opening
    make_wall("Wall_S_W", (-2.0, 0.0, 0), length=2.0, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_wall("Wall_S_E", (+2.0, 0.0, 0), length=2.0, height=CEIL, axis='X',
              palette=PAL, baseboard_face_sign=+1)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4)
    # Crown molding on three walls (the south wall has the AC interrupting it)
    for nm, ax, length, wx, wy in [("Crown_W", 'Y', ROOM_D, -ROOM_W/2.0+0.10, ROOM_D/2.0),
                                    ("Crown_E", 'Y', ROOM_D, +ROOM_W/2.0-0.10, ROOM_D/2.0),
                                    ("Crown_N", 'X', ROOM_W, 0.0, ROOM_D-0.10)]:
        make_crown_molding(nm, wall_x=wx, wall_y=wy, length=length, axis=ax,
                           ceil_z=CEIL, palette={"wood": COL_CYPRESS_DK})


def build_the_cypress_beam():
    """The cypress beam crossing the ceiling — the canonical
    "cypress beam is the cypress beam" anchor."""
    # Single beam running E-W across the center of the ceiling.
    make_box("CypressBeam", (0.0, 2.6, CEIL - 0.18),
             (ROOM_W + 0.20, 0.26, 0.30), COL_CYPRESS)
    # Beam-end caps in slightly-darker cypress
    for sgn in (-1, +1):
        make_box("CypressBeam_Cap_%+d" % sgn,
                 (sgn * (ROOM_W / 2.0 + 0.08), 2.6, CEIL - 0.18),
                 (0.04, 0.30, 0.34), COL_CYPRESS_DK)
    # Two iron straps wrapping the beam
    for x_off in (-1.5, +1.5):
        make_box("CypressBeam_Strap_%.1f" % x_off,
                 (x_off, 2.6, CEIL - 0.18),
                 (0.04, 0.30, 0.34), (0.18, 0.16, 0.14, 1.0))


def build_window_ac():
    """The window AC unit on the south wall, half-capacity.
    Per setup_hot_office: "The window AC unit is doing the
    half-capacity thing." Bulky beige body sitting in the
    south wall opening between the two south wall segments."""
    ac_cx = 0.0
    ac_cy = 0.0
    ac_top_z = 1.30
    ac_w, ac_d, ac_h = 0.80, 0.50, 0.50
    # Body sits with a small portion outside the wall (south face)
    make_box("WindowAC_Body", (ac_cx, ac_cy, ac_top_z),
             (ac_w, ac_d, ac_h), COL_AC_BODY)
    # Front grille (north face, into the room)
    make_box("WindowAC_Grille", (ac_cx, ac_cy + ac_d/2.0 + 0.005, ac_top_z),
             (ac_w - 0.06, 0.01, ac_h - 0.06), COL_AC_GRILLE)
    # 6 horizontal louvers on the grille
    for li in range(6):
        make_box("WindowAC_Louver_%d" % li,
                 (ac_cx, ac_cy + ac_d/2.0 + 0.012, ac_top_z + 0.18 - li * 0.07),
                 (ac_w - 0.08, 0.003, 0.015),
                 (0.42, 0.40, 0.36, 1.0))
    # Two front control knobs
    for kx in (-0.16, +0.16):
        make_cyl("WindowAC_Knob_%.2f" % kx,
                 (ac_cx + kx, ac_cy + ac_d/2.0 + 0.012, ac_top_z + 0.04),
                 0.018, 0.025, COL_BRASS, segments=8, axis='Y')
    # The "half-capacity" tell — a piece of cardboard wedged in
    # the side gap. Reads as "the wall's air-leak shim."
    make_box("WindowAC_CardboardShim",
             (ac_cx + ac_w/2.0 + 0.02, ac_cy, ac_top_z),
             (0.04, ac_d - 0.04, ac_h - 0.10),
             (0.72, 0.58, 0.36, 1.0))   # cardboard tan
    # Window frame around the AC opening
    # Top lintel
    make_box("WindowAC_Lintel", (ac_cx, ac_cy + 0.04, ac_top_z + ac_h/2.0 + 0.06),
             (ac_w + 0.30, 0.20, 0.08), (0.34, 0.26, 0.18, 1.0))
    # Sill below
    make_box("WindowAC_Sill", (ac_cx, ac_cy + 0.04, ac_top_z - ac_h/2.0 - 0.04),
             (ac_w + 0.30, 0.20, 0.05), (0.34, 0.26, 0.18, 1.0))


def build_corner_across_window():
    """The second window — the CORNER ACROSS — east wall, looking
    onto the street corner where the older man in the charcoal
    suit appears (per setup_two_horses_one_wreck: "the older man
    in the charcoal suit appears on the corner at turn 2. ... The
    Corner Across threshold becomes visible when the man arrives.")
    """
    # Window on the east wall, mid-height
    make_window("CornerAcross", (ROOM_W/2.0 - 0.01, 2.4, 1.40),
                width=1.20, height=1.20, axis='Y')
    # Frame trim (warmer wood)
    make_box("CornerAcross_FrameTop", (ROOM_W/2.0 - 0.01, 2.4, 2.06),
             (0.04, 1.30, 0.08), (0.34, 0.26, 0.18, 1.0))
    make_box("CornerAcross_FrameBot", (ROOM_W/2.0 - 0.01, 2.4, 0.78),
             (0.04, 1.30, 0.08), (0.34, 0.26, 0.18, 1.0))
    # A small brass radiator under the window (the cool-side option
    # — radiator on east wall, AC on south wall)
    make_box("Radiator_Body", (ROOM_W/2.0 - 0.16, 2.4, 0.40),
             (0.18, 0.90, 0.80), (0.78, 0.62, 0.30, 1.0))
    # 6 radiator fins
    for fi in range(6):
        make_box("Radiator_Fin_%d" % fi,
                 (ROOM_W/2.0 - 0.16, 2.05 + fi * 0.14, 0.40),
                 (0.20, 0.02, 0.80), (0.62, 0.50, 0.24, 1.0))


def build_desk_and_props():
    """Antonio's desk · roughly center-north, facing south so he
    looks out the south wall AC. Holds the bourbon, rotary phone,
    voicemail machine, ashtray, rolodex, the day's papers.
    """
    desk_cx, desk_cy = -0.50, 3.20
    desk_top_z = 0.74
    desk_w, desk_d = 1.80, 0.90
    # Top
    make_box("Desk_Top", (desk_cx, desk_cy, desk_top_z),
             (desk_w, desk_d, 0.04), COL_DESK_TOP)
    # Two pedestals (drawers, left + right)
    for sgn in (-1, +1):
        make_box("Desk_Pedestal_%+d" % sgn,
                 (desk_cx + sgn * (desk_w/2.0 - 0.20), desk_cy, desk_top_z / 2.0),
                 (0.40, desk_d - 0.06, desk_top_z), COL_DESK_LEG)
        # Drawer pulls
        for di in range(3):
            make_box("Desk_Drawer_%+d_%d" % (sgn, di),
                     (desk_cx + sgn * (desk_w/2.0 - 0.20),
                      desk_cy - desk_d/2.0 + 0.02,
                      0.12 + di * 0.22),
                     (0.34, 0.005, 0.02),
                     COL_BRASS)
    # Modesty panel (back face, south side)
    make_box("Desk_Modesty",
             (desk_cx, desk_cy + desk_d/2.0 - 0.02, desk_top_z / 2.0),
             (desk_w - 0.06, 0.04, desk_top_z),
             COL_DESK_LEG)

    # ── The bottle of bourbon on the desk ──
    # setup_hot_office: "The bottle of bourbon is on the desk."
    bot_x = desk_cx + 0.30
    bot_y = desk_cy + 0.10
    # Bottle body (brown glass)
    make_cyl("Bourbon_Bottle_Body", (bot_x, bot_y, desk_top_z + 0.13),
             0.045, 0.22, COL_BOURBON_BTL, segments=10, axis='Z')
    # Liquid level (slightly less than full · 60%)
    make_cyl("Bourbon_Bottle_Liquid", (bot_x, bot_y, desk_top_z + 0.09),
             0.040, 0.13, COL_BOURBON_LIQ, segments=10, axis='Z')
    # Neck
    make_cyl("Bourbon_Bottle_Neck", (bot_x, bot_y, desk_top_z + 0.30),
             0.018, 0.10, COL_BOURBON_BTL, segments=8, axis='Z')
    # Label (cream paper around the body)
    make_cyl("Bourbon_Bottle_Label", (bot_x, bot_y, desk_top_z + 0.10),
             0.046, 0.08, COL_PAPER, segments=10, axis='Z')
    # Cap
    make_cyl("Bourbon_Bottle_Cap", (bot_x, bot_y, desk_top_z + 0.38),
             0.022, 0.04, (0.42, 0.32, 0.18, 1.0), segments=8, axis='Z')
    # A short glass next to the bottle
    make_cyl("Bourbon_Glass_Body", (bot_x + 0.14, bot_y, desk_top_z + 0.06),
             0.030, 0.10, (0.86, 0.86, 0.88, 0.55), segments=8, axis='Z')
    make_cyl("Bourbon_Glass_Liquid", (bot_x + 0.14, bot_y, desk_top_z + 0.04),
             0.026, 0.04, COL_BOURBON_LIQ, segments=8, axis='Z')

    # ── Rotary phone (Q. Paul has called eleven times) ──
    ph_x, ph_y = desk_cx - 0.55, desk_cy - 0.10
    # Body (low rectangular base)
    make_box("Phone_Body", (ph_x, ph_y, desk_top_z + 0.04),
             (0.24, 0.22, 0.08), COL_PHONE)
    # Cradle for handset
    make_box("Phone_Cradle", (ph_x, ph_y + 0.04, desk_top_z + 0.10),
             (0.20, 0.10, 0.04), (0.22, 0.18, 0.16, 1.0))
    # Handset resting on cradle
    make_box("Phone_Handset", (ph_x, ph_y + 0.04, desk_top_z + 0.14),
             (0.22, 0.06, 0.04), COL_PHONE)
    # Rotary dial wheel (a low cylinder with a center spindle)
    make_cyl("Phone_RotaryWheel", (ph_x, ph_y - 0.06, desk_top_z + 0.085),
             0.075, 0.005, COL_PHONE_DIAL, segments=12, axis='Z')
    # Finger holes — 10 small darker boxes ringing the wheel
    for h in range(10):
        a = math.radians(36 * h - 90)
        hx = ph_x + 0.055 * math.cos(a)
        hy = ph_y - 0.06 + 0.055 * math.sin(a)
        make_cyl("Phone_FingerHole_%d" % h, (hx, hy, desk_top_z + 0.089),
                 0.008, 0.002, (0.16, 0.14, 0.12, 1.0), segments=4, axis='Z')
    # Center spindle
    make_cyl("Phone_Spindle", (ph_x, ph_y - 0.06, desk_top_z + 0.091),
             0.014, 0.003, COL_BRASS, segments=6, axis='Z')
    # Coiled handset cord (a few segments)
    for s in range(5):
        make_cyl("Phone_Cord_%d" % s,
                 (ph_x - 0.10, ph_y + 0.06 + s * 0.018, desk_top_z + 0.03 + s * 0.008),
                 0.010, 0.020, COL_PHONE, segments=4, axis='Z')

    # ── Voicemail machine with 2-digit counter ──
    # Setup_option_four says "eleven voicemails today, fourteen
    # yesterday" — the counter on the machine reads 11.
    vm_x, vm_y = desk_cx - 0.30, desk_cy - 0.18
    make_box("Voicemail_Body", (vm_x, vm_y, desk_top_z + 0.04),
             (0.22, 0.14, 0.08), COL_VOICEMAIL)
    # Red blinking LED (canon: "messages waiting")
    make_box("Voicemail_LED", (vm_x + 0.08, vm_y + 0.06, desk_top_z + 0.085),
             (0.012, 0.001, 0.012), COL_VM_LED)
    # Two-digit LCD counter on the front face — reads as "11"
    make_box("Voicemail_LCD_Bg", (vm_x - 0.04, vm_y - 0.071, desk_top_z + 0.060),
             (0.06, 0.001, 0.026), (0.20, 0.22, 0.20, 1.0))
    # Two darker segments forming a "11" (two vertical lines)
    for ci in (-0.015, +0.012):
        make_box("Voicemail_LCD_Digit_%.3f" % ci,
                 (vm_x - 0.04 + ci, vm_y - 0.072, desk_top_z + 0.060),
                 (0.005, 0.001, 0.020), COL_VM_DIGIT)
    # Cassette slot on top
    make_box("Voicemail_CassetteSlot", (vm_x, vm_y, desk_top_z + 0.082),
             (0.16, 0.10, 0.002), (0.10, 0.10, 0.10, 1.0))

    # ── Ashtray ──
    make_cyl("Ashtray_Body", (desk_cx + 0.65, desk_cy + 0.20, desk_top_z + 0.018),
             0.08, 0.035, COL_ASHTRAY, segments=12, axis='Z')
    make_cyl("Ashtray_Inside", (desk_cx + 0.65, desk_cy + 0.20, desk_top_z + 0.035),
             0.065, 0.005, (0.20, 0.18, 0.16, 1.0), segments=12, axis='Z')
    # A spent cigarette stubbed on the rim
    make_cyl("Ashtray_Butt", (desk_cx + 0.71, desk_cy + 0.22, desk_top_z + 0.036),
             0.005, 0.04, (0.92, 0.88, 0.74, 1.0), segments=4, axis='X')
    # Tiny ash trail
    make_cyl("Ashtray_Filter", (desk_cx + 0.69, desk_cy + 0.22, desk_top_z + 0.036),
             0.005, 0.012, (0.62, 0.50, 0.30, 1.0), segments=4, axis='X')

    # ── Rolodex ──
    rd_x, rd_y = desk_cx + 0.10, desk_cy + 0.22
    # Base
    make_box("Rolodex_Base", (rd_x, rd_y, desk_top_z + 0.022),
             (0.20, 0.12, 0.04), COL_ROLODEX)
    # Drum (cylinder, axis E-W)
    make_cyl("Rolodex_Drum", (rd_x, rd_y, desk_top_z + 0.080),
             0.060, 0.18, (0.92, 0.88, 0.78, 1.0), segments=10, axis='X')
    # Two side wheels
    for sgn in (-1, +1):
        make_cyl("Rolodex_Wheel_%+d" % sgn, (rd_x + sgn * 0.10, rd_y, desk_top_z + 0.080),
                 0.066, 0.010, COL_ROLODEX, segments=10, axis='X')
    # Top card visible (a cream rectangle on top of the drum)
    make_box("Rolodex_TopCard", (rd_x, rd_y, desk_top_z + 0.144),
             (0.16, 0.10, 0.0005), COL_PAPER)

    # ── Stack of papers (voicemail call logs etc.) ──
    for s in range(3):
        make_box("Desk_PaperStack_%d" % s,
                 (desk_cx + 0.50, desk_cy - 0.18, desk_top_z + 0.005 + s * 0.004),
                 (0.20, 0.28, 0.004),
                 (0.94, 0.90 - s * 0.02, 0.82 - s * 0.02, 1.0))


def build_office_chair():
    # Antonio's chair — facing south so he can see the AC + the
    # corner-across window in his peripheral vision.
    cx, cy = -0.50, 3.95   # north of the desk
    # Seat
    make_box("OfficeChair_Seat", (cx, cy, 0.48), (0.50, 0.50, 0.08), COL_LEATHER_OX)
    # Back
    make_box("OfficeChair_Back", (cx, cy + 0.22, 0.86), (0.50, 0.06, 0.60), COL_LEATHER_OX)
    # Central post
    make_cyl("OfficeChair_Post", (cx, cy, 0.24), 0.030, 0.44, COL_DESK_LEG, segments=6, axis='Z')
    # 5-star base
    for s in range(5):
        a = math.radians(72 * s)
        fx = cx + 0.24 * math.cos(a)
        fy = cy + 0.24 * math.sin(a)
        make_box("OfficeChair_Foot_%d" % s, (fx, fy, 0.04),
                 (0.08, 0.08, 0.06), COL_DESK_LEG)


def build_back_stair_opening():
    """A square opening in the floor at the SW corner with a railing
    and the top of a staircase visible — Jimmy comes up this stair.
    The audible radio downstairs is implied by the opening.
    """
    op_cx, op_cy = -2.4, 1.0
    op_w, op_d = 0.90, 1.20
    # The opening — drawn as a darker floor patch (the stair down)
    make_box("BackStair_Opening", (op_cx, op_cy, -0.020),
             (op_w, op_d, 0.020),
             (0.10, 0.08, 0.06, 1.0))
    # Top step (visible as a slightly recessed darker step at the
    # opening's south edge)
    make_box("BackStair_TopStep", (op_cx, op_cy - op_d/2.0 + 0.10, -0.018),
             (op_w - 0.06, 0.20, 0.04),
             (0.34, 0.26, 0.18, 1.0))
    # Railing around three sides (open south so Jimmy can step up)
    rail_top_z = 0.96
    rail_thick = 0.04
    for nm, cx, cy, w, d in [
        ("BackStair_Rail_N", op_cx, op_cy + op_d/2.0 + 0.02, op_w + 0.10, rail_thick),
        ("BackStair_Rail_W", op_cx - op_w/2.0 - 0.02, op_cy + 0.06, rail_thick, op_d + 0.10),
        ("BackStair_Rail_E", op_cx + op_w/2.0 + 0.02, op_cy + 0.06, rail_thick, op_d + 0.10),
    ]:
        # Top rail
        make_box(nm + "_Top", (cx, cy, rail_top_z), (w, d, 0.04), COL_BRASS)
        # 4 vertical balusters under each rail
        for bi in range(4):
            if "_N" in nm:
                bx = op_cx - op_w/2.0 + bi * (op_w / 3.0)
                by = op_cy + op_d/2.0 + 0.02
            else:
                bx = cx
                by = op_cy - op_d/2.0 + bi * (op_d / 3.0)
            make_box(nm + "_Bal_%d" % bi, (bx, by, rail_top_z / 2.0),
                     (rail_thick, rail_thick, rail_top_z), COL_DESK_LEG)

    # A small radio at the floor level visible through the stair
    # opening · the crew's radio on a milk crate downstairs
    make_box("BackStair_Radio", (op_cx, op_cy, -0.18),
             (0.16, 0.12, 0.10), COL_RADIO_BODY)
    # The milk crate it sits on (visible silhouette)
    make_box("BackStair_MilkCrate", (op_cx, op_cy, -0.30),
             (0.30, 0.30, 0.22),
             (0.62, 0.20, 0.22, 1.0))   # dairy-red plastic


def build_wall_photo_and_clock():
    # Wall photograph of an early ember-and-ash crew on the north
    # wall (above the desk, behind Antonio's chair)
    make_box("CrewPhoto_Frame", (-0.50, ROOM_D - 0.05, 1.94),
             (0.72, 0.04, 0.50), COL_DESK_LEG)
    make_box("CrewPhoto_Mat", (-0.50, ROOM_D - 0.06, 1.94),
             (0.66, 0.005, 0.44), COL_PAPER)
    # 5 darker rectangles · stylized crew members in the photo
    for ci in range(5):
        cx_off = -0.30 + ci * 0.15
        make_box("CrewPhoto_Person_%d" % ci,
                 (-0.50 + cx_off, ROOM_D - 0.063, 1.94),
                 (0.06, 0.001, 0.16),
                 (0.38, 0.30, 0.22, 1.0))
    # Brass plaque under the photo
    make_box("CrewPhoto_Plaque", (-0.50, ROOM_D - 0.06, 1.66),
             (0.36, 0.003, 0.04), COL_BRASS)

    # Wall clock — stopped at the canonical morning hour
    make_wall_clock("OfficeClock", (-ROOM_W/2.0 + 0.05, 3.0, 2.10),
                    frozen_hour=11, frozen_min=14)


def build_ceiling_infra():
    make_smoke_detector("Smoke", (0.0, 1.5, CEIL))
    # Pendant light over the desk
    make_cyl("Pendant_Cord", (-0.50, 3.20, CEIL - 0.40),
             0.012, 0.80, (0.18, 0.16, 0.14, 1.0), segments=4, axis='Z')
    make_cyl("Pendant_Shade", (-0.50, 3.20, CEIL - 0.96),
             0.20, 0.10, (0.86, 0.78, 0.62, 1.0), segments=12, axis='Z')


def main():
    clear_scene()
    build_shell()
    build_the_cypress_beam()
    build_window_ac()
    build_corner_across_window()
    build_desk_and_props()
    build_office_chair()
    build_back_stair_opening()
    build_wall_photo_and_clock()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "../../../assets/3d/locales/ember_ash_office.glb"))
    print(f"\n[build_ember_ash_office] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
