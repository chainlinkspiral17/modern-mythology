"""hospital_room — Room 318, New Auburn General — vol6 hero locale
(2 VN bg refs, both 3d:hospital_room):
  · vol6_ch7_hospital     "The Week"   — Saturday 23:48
  · vol6_ch8_hospital_318 "Room 318"   — Sunday 10:47  (the staged one)

WHO / WHEN THIS ROOM HOLDS: Linda Caldwell — Maya's grandmother, 71,
post-operative after a broken hip, sitting up in the bed on the
regular floor the morning after surgery. Sunday, 10:47 AM. Her hip
is in a brace and a cast; she has an IV in her right hand — "the hand
she would, normally, use for the Morse key" (ch8:42). Track:
vol6_pre_dawn_blue. Register: a real med-surg room the morning after —
RESTRAINT is the register. Institutional geometry, the few named
personal facts, and — loudest of all — the things nobody has brought
yet.

DO NOT CONFLATE with build_hospice_room.py (vol5 palliative, end-of-
life: photo frame, plant, poster, vitals monitor, crown molding — a
softened comfort register) or build_asylum_ward_c.py. Room 318 is
acute post-op, occupied since the night, institutionally bare. The
opposite of the hospice on purpose (see canon-negatives).

CANON ADJUDICATIONS made by this pass (documented, not resolved
elsewhere):

  1. TWO CHAPTERS, ONE ASSET. ch7 (Sat 23:48) is a WAITING-ROOM beat
     — "Maya is in the waiting room... a paper cup of coffee from the
     vending machine" (ch7:38-42); the surgery is still happening.
     ch8 (Sun 10:47) is the PATIENT ROOM, Room 318, and is the fully-
     inspectable minute (bed, IV, brace, visitor's chair, window,
     door). The GLB is authored as the patient room; ch7 borrows the
     same institutional backdrop for its waiting-room dialogue, which
     its sprites carry. The wave-8 rule says the binding is ground
     truth — both bind 3d:hospital_room, and ch8 is the one that
     stages the geometry, so ch8 wins the build. The vending-machine
     coffee is a WAITING-ROOM prop and a canon-negative here (wrong
     register — see the store-fixture strip).
  2. BAKED MINUTE — Sunday 10:47 AM (ch8:26 interlude). The wall
     clock holds 10:47 (the room keeps its minute, the diego-bedroom
     discipline). Morning light comes from the EAST window. ch7's
     23:48 is the waiting room, a different space, not this one.
  3. THE IV IS ON THE RIGHT (ch8:42 — the Morse hand). Baked from the
     supine geometry: head at the NORTH wall, feet south; a person on
     their back, head-north, has the right hand falling to the EAST,
     so the IV POLE stands east of the head and the line runs to that
     hand. The FREE hand is therefore the LEFT (west) — the hand that
     "strokes Maya's hair... ignoring the IV" (ch8:76) and that Maya
     "takes... in both of hers" (ch8:72). So the VISITOR'S CHAIR sits
     on the WEST (free-hand) side of the bed, where a person sits to
     hold that hand. The Morse itself is NOT literalized in the room
     (no key, no radio — those are home, three blocks away, dark; see
     negatives). The room supplies only the IV that stands in the
     way of the key. That is the whole Morse-hand treatment: one
     tether, on the right, and restraint everywhere else.
  4. CAMERA / DOOR. "The door closes" (ch8:180) is a narrative beat.
     The Background3D preset (0, 2.30, +0.5 / yaw 180 / fov 60) shoots
     NORTH through the south door gap, so the leaf is baked OPEN,
     parked flat against Wall_S_E (hinged at the east jamb) — the
     exact diego-bedroom solution. A closed leaf would fill the frame
     with the back of a door. Shell footprint kept from the scaffold
     (5.0 x 5.0, CEIL 2.8, south door gap x -1..+1) — the preset is
     tuned to it.

Canon baked in (cite):
  · ch8:38 — LINDA SITTING UP: adjustable bed with the head section
    raised (Fowler's), pillow high. The hip brace/cast (ch8:42) rides
    on the sprite, not the room.
  · ch8:42 / vol6_pre_dawn_blue — THE IV: chrome pole on a five-star
    caster base, saline bag on the hook, drip chamber, a small pump
    on the pole, the line running down and toward the right hand at
    the pillow. The hero prop (adjudication 3).
  · ch8:136 — THE VISITOR'S CHAIR "which is too large for her"
    [Gracie]: one vinyl-and-wood recliner-style armchair, west of the
    bed (the free-hand side). One lightweight stacking side chair
    waits against the wall for the second visitor (Maya sits, then
    Gracie; ch8:68/136).
  · ch8:521 — THE WINDOW Anita "stands by": east wall, a real opening
    with venetian blinds (slats open on the Sunday morning). East
    light across the bed at 10:47.
  · ch8:180 / :184 — THE DOOR that closes, and the PRIVATE room
    ("Linda and Maya are alone"): one bed, one door, a ceiling cubicle
    curtain track with the curtain pushed open (family all present).
  · med-surg SIGNATURE (any post-op room — the vocabulary that makes
    this read "hospital," not "bedroom"): the HEADWALL console behind
    the bed (O2 + vacuum outlets, nurse-call panel, a swing-arm
    over-bed exam light); the cantilever OVERBED TABLE with an issue
    water pitcher + lidded cup and straw; the bedside CABINET; the
    drop-tile ceiling with grid + recessed troffers; sheet-vinyl
    floor with a coved base; a wall bumper rail; a BLANK patient
    whiteboard (Label3D owns any legible text — playbook rule); wall-
    mounted alcohol-gel dispenser, a yellow SHARPS container, a glove
    box by the door.

Canon-NEGATIVES honored (what Room 318 pointedly LACKS — the morning-
after absences are the loudest props, and the register's whole point):
  · NO FLOWERS, NO GET-WELL CARDS, NO BALLOONS, NO PHOTOS, NO PLANT.
    She was moved from recovery in the night (ch8:42) and it is Sunday
    morning; nobody has been home for her things, and Maya is a
    sixteen-year-old ward with no resources and no car. The room holds
    a beloved grandmother and contains nothing of her yet. This is the
    deliberate inverse of the vol5 hospice's photo-frame + plant +
    faded poster — same prop library, opposite register.
  · NO SHORTWAVE / MORSE KEY / RECEIVER. The radio is at home, three
    blocks away, "dark, untouched, for the first night in five days"
    (ch7:461). The single object that defines Linda is absent from the
    room; the Morse lives in her right hand and the prose, not here.
  · NO VENDING MACHINE / COFFEE / MICROWAVE / SNACK FIXTURES. That is
    the ch7 WAITING-ROOM register (ch7:42). The scaffold's store-
    fixture imports (counter / register / snack aisle / coffee pots /
    endcap / microwave) were codegen vocabulary — removed, the
    Cosmic-Comics lesson.
  · NO VITALS MONITOR / TELEMETRY / GREEN WAVEFORM. She was moved off
    recovery to the regular floor, stable — a straightforward hip,
    three weeks of rehab then home (ch8:205). The IV is the ONLY
    tether. (The hospice's cardiac monitor belongs to a different
    acuity; not here.)
  · NO SECOND BED / ROOMMATE — a private room (ch8:184).
  · NO CROWN MOLDING, NO DECOR POSTERS — an acute institutional wall/
    ceiling junction, not domestic softening.

NAME-DEPENDENCY FLAG (required check): the BINDINGS (ch7/ch8) are the
ground truth and name the grandmother LINDA CALDWELL / "Mrs. Caldwell"
(ch7:276), married to THOMAS (ch8:215), at NEW AUBURN GENERAL (ch7:27,
ch8:27), ROOM 318 (ch8 title/interlude) — all internally consistent.
The vol6 wiki extension-cast table instead calls Maya's grandmother
"Connie Daigle" and Maya "Daigle" (_VOL6_WIKI.md:46,54). Per the wave-
8 binding-verification rule the scene JSONs win; CALDWELL is authored,
"Connie Daigle" noted as unresolved drift. No geometry carries a
legible name (Label3D rule), so the flag is documentation only. Minor
sprite-db drift also seen, out of geometry scope: ch7 routes Anita
Kowalski's line through char-id "sam_mom" while ch8 uses "anita" — the
room is Linda's either way.

Shell footprint kept from the scaffold (5.0 x 5.0, CEIL 2.8, south
door gap x -1..+1 — camera preset). The EAST wall is split around a
REAL window opening (frame + blinds, no glass — playbook no-
transparency rule). Scaffold's store-fixture imports are gone.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.decor import make_wall_clock
from _props.safety import (make_smoke_detector, make_sprinkler, make_hvac_vent,
                           make_fluorescent_tube_fixture)

# ── Shell (footprint kept from the scaffold — camera-safe) ───────
ROOM_W = 5.0; ROOM_D = 5.0; CEIL = 2.8

# ── Institutional palette — warm greige walls, pale sheet-vinyl
#    floor, one clinical seafoam accent (the curtain / the chair
#    vinyl); linens white; equipment beige + stainless. The only
#    saturated colors in the room are clinical (the accent, the
#    yellow sharps box). The absence of a personal palette IS the
#    emotional content of the morning-after room. ────────────────
COL_WALL       = (0.80, 0.79, 0.75, 1.0)   # soft warm greige
COL_COVE       = (0.66, 0.66, 0.64, 1.0)   # vinyl coved base
COL_FLOOR      = (0.80, 0.77, 0.71, 1.0)   # pale warm sheet vinyl
COL_FLOOR_SEAM = (0.68, 0.65, 0.60, 1.0)
COL_CEIL_TILE  = (0.93, 0.92, 0.88, 1.0)
COL_CEIL_GRID  = (0.72, 0.70, 0.66, 1.0)
COL_LINEN      = (0.95, 0.94, 0.90, 1.0)   # sheets
COL_PILLOW     = (0.96, 0.95, 0.92, 1.0)
COL_MATTRESS   = (0.90, 0.90, 0.87, 1.0)
COL_BLANKET    = (0.82, 0.84, 0.82, 1.0)   # thin cellular thermal blanket
COL_TEAL       = (0.42, 0.56, 0.55, 1.0)   # the clinical seafoam accent
COL_TEAL_DK    = (0.30, 0.42, 0.42, 1.0)
COL_FRAME      = (0.82, 0.82, 0.79, 1.0)   # painted bed frame / boards
COL_STEEL      = P.METAL_STEEL             # chrome rails, pole, arms
COL_BEIGE      = (0.86, 0.85, 0.80, 1.0)   # medical equipment beige
COL_BEIGE_DK   = (0.70, 0.69, 0.64, 1.0)
COL_IV_FLUID   = (0.90, 0.92, 0.90, 1.0)   # saline — pale, near-clear
COL_CHAR       = (0.20, 0.20, 0.22, 1.0)   # small tech / cords
COL_WOOD_ARM   = (0.52, 0.40, 0.28, 1.0)   # visitor-chair wood arms
COL_SHARPS     = (0.82, 0.62, 0.18, 1.0)   # the universal yellow sharps bin
COL_WHITE      = (0.94, 0.94, 0.92, 1.0)   # whiteboard / gel dispenser
COL_PLASTIC    = (0.88, 0.88, 0.86, 1.0)   # pitcher / cup

PAL_WALL = {"wall": COL_WALL, "baseboard": COL_COVE}

# East window — the one Anita stands by (ch8:521); morning east light
EWIN_CY   = 2.50               # opening y 1.85..3.15
EWIN_W    = 1.30
EWIN_SILL = 0.95
EWIN_HEAD = 2.10

# Bed — long axis N-S, head at the north wall, foot toward the camera
BED_CX = -0.45                 # slightly frame-left (Linda is "left")
BED_W  = 0.95                  # x -0.925..+0.025
BED_Y0, BED_Y1 = 2.55, 4.55    # foot .. head
IVX, IVY = 0.32, 4.35          # the pole — EAST of the head (the right hand)


# ═════════════════════════════════════════════════════════════════
# SHELL — pale sheet-vinyl floor with a coved base, warm greige
# walls, drop-tile ceiling. West/North solid; EAST split around a
# real window opening; South keeps the scaffold's door gap (x -1..+1)
# for the camera.
# ═════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0), size_x=ROOM_W + 0.4,
               size_y=ROOM_D + 0.4, palette={"vinyl": COL_FLOOR, "seam": COL_FLOOR_SEAM})
    # West wall — solid
    make_wall("Wall_W", (-ROOM_W / 2.0, ROOM_D / 2.0, 0), length=ROOM_D + 0.4,
              height=CEIL, axis='Y', palette=PAL_WALL, baseboard_face_sign=+1)
    # North wall — solid (the headwall mounts on its interior face)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    # East wall — split around the window opening (y 1.85..3.15)
    e_s_len = (EWIN_CY - EWIN_W / 2.0) - (-0.2) + 0.0          # 2.05
    e_s_cy  = (-0.2 + (EWIN_CY - EWIN_W / 2.0)) / 2.0          # 0.825
    e_n_len = (ROOM_D + 0.2) - (EWIN_CY + EWIN_W / 2.0)        # 2.05
    e_n_cy  = ((EWIN_CY + EWIN_W / 2.0) + (ROOM_D + 0.2)) / 2.0  # 4.175
    make_wall("Wall_E_S", (+ROOM_W / 2.0, e_s_cy, 0), length=e_s_len, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_E_N", (+ROOM_W / 2.0, e_n_cy, 0), length=e_n_len, height=CEIL,
              axis='Y', palette=PAL_WALL, baseboard_face_sign=-1)
    make_box("Wall_E_SillFill", (+ROOM_W / 2.0, EWIN_CY, EWIN_SILL / 2.0),
             (0.20, EWIN_W, EWIN_SILL), COL_WALL)
    make_box("Wall_E_HeadFill", (+ROOM_W / 2.0, EWIN_CY, (EWIN_HEAD + CEIL) / 2.0),
             (0.20, EWIN_W, CEIL - EWIN_HEAD), COL_WALL)
    # South wall — scaffold door gap x -1..+1 kept (camera preset)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0), length=ROOM_W / 2.0 - 1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60), COL_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL), size_x=ROOM_W + 0.4,
                 size_y=ROOM_D + 0.4, palette={"tile": COL_CEIL_TILE, "grid": COL_CEIL_GRID},
                 with_grid=True, with_stains=False)


# ═════════════════════════════════════════════════════════════════
# THE BED — adjustable med-surg bed, head raised (Linda sitting up,
# ch8:38). Painted frame on a hi-lo base with casters; the deck; the
# mattress with a stepped raised back at the head; pillow high; a
# thin cellular blanket over the legs with the accent stripe; half
# side rails up (post-op); the call/control pendant clipped to the
# near rail.
# ═════════════════════════════════════════════════════════════════
def build_bed():
    bx = BED_CX
    by = (BED_Y0 + BED_Y1) / 2.0
    # Hi-lo base + casters
    make_box("Bed_Base", (bx, by, 0.16), (0.62, 1.70, 0.14), COL_BEIGE_DK)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Bed_Caster_{li}", (bx + sx * 0.30, by + sy * 0.82, 0.07),
                 0.055, 0.05, COL_CHAR, axis='X')
    # Deck + mattress (foot/leg half flat)
    make_box("Bed_Deck", (bx, by, 0.56), (BED_W + 0.04, 2.02, 0.10), COL_FRAME)
    make_box("Bed_Mattress_Legs", (bx, 3.20, 0.70), (BED_W - 0.04, 1.25, 0.16), COL_MATTRESS)
    # Raised back — two stepped tiers rising toward the head (Fowler's)
    make_box("Bed_Back_Lower", (bx, 3.98, 0.86), (BED_W - 0.04, 0.90, 0.18), COL_MATTRESS)
    make_box("Bed_Back_Upper", (bx, 4.34, 1.02), (BED_W - 0.04, 0.52, 0.18), COL_MATTRESS)
    make_box("Bed_Pillow", (bx, 4.34, 1.16), (0.78, 0.44, 0.12), COL_PILLOW)
    make_box("Bed_Pillow2", (bx + 0.06, 4.30, 1.05), (0.70, 0.40, 0.10), COL_LINEN)
    # Blanket over the legs + stripe + side/foot drapes
    make_box("Bed_Blanket", (bx, 3.14, 0.80), (BED_W, 1.25, 0.05), COL_BLANKET)
    make_box("Bed_Blanket_Stripe", (bx, 3.72, 0.83), (BED_W, 0.06, 0.006), COL_TEAL)
    make_box("Bed_Blanket_DrapeW", (bx - BED_W / 2.0, 3.14, 0.68), (0.02, 1.25, 0.22), COL_BLANKET)
    make_box("Bed_Blanket_DrapeE", (bx + BED_W / 2.0, 3.14, 0.68), (0.02, 1.25, 0.22), COL_BLANKET)
    make_box("Bed_Blanket_DrapeFoot", (bx, BED_Y0 + 0.02, 0.68), (BED_W, 0.02, 0.22), COL_BLANKET)
    make_box("Bed_SheetFold", (bx, 3.64, 0.83), (BED_W, 0.16, 0.012), COL_LINEN)
    # Foot + head boards (painted)
    make_box("Bed_FootBoard", (bx, BED_Y0, 0.78), (BED_W + 0.10, 0.06, 0.52), COL_FRAME)
    make_box("Bed_FootBoard_Cap", (bx, BED_Y0, 1.045), (BED_W + 0.12, 0.08, 0.05), COL_BEIGE_DK)
    make_box("Bed_HeadBoard", (bx, BED_Y1, 0.85), (BED_W + 0.10, 0.06, 0.62), COL_FRAME)
    # Half side rails up at the head half (post-op), chrome
    for sgn, nm in ((-1, "W"), (+1, "E")):
        rx = bx + sgn * (BED_W / 2.0 + 0.02)
        make_box(f"Bed_Rail_{nm}", (rx, 4.05, 1.02), (0.035, 0.92, 0.06), COL_STEEL)
        make_box(f"Bed_Rail_{nm}_Low", (rx, 4.05, 0.80), (0.035, 0.92, 0.05), COL_STEEL)
        for vi in range(3):
            make_cyl(f"Bed_RailPost_{nm}_{vi}", (rx, 3.66 + vi * 0.39, 0.91),
                     0.012, 0.28, COL_STEEL)
    # Control pendant on the near (west) rail
    make_box("Bed_Pendant", (bx - BED_W / 2.0 - 0.06, 3.70, 0.86), (0.05, 0.10, 0.16), COL_BEIGE)
    make_cyl("Bed_PendantCord", (bx - BED_W / 2.0 - 0.02, 3.80, 0.98), 0.006, 0.28,
             COL_CHAR, axis='Y', segments=6)


# ═════════════════════════════════════════════════════════════════
# THE HEADWALL — north wall behind the bed head, facing the camera:
# the console that reads "hospital" more than anything else. A
# horizontal raceway, a medical-gas outlet block (O2 green + vacuum
# white), the nurse-call panel with its call button on a cord, and a
# swing-arm over-bed exam light reaching over the pillow.
# ═════════════════════════════════════════════════════════════════
def build_headwall():
    wy = ROOM_D - 0.10          # interior face of the north wall (~4.90)
    cx = BED_CX
    make_box("Headwall_Raceway", (cx, wy - 0.03, 1.35), (1.50, 0.05, 0.34), COL_BEIGE)
    make_box("Headwall_RacewayTrim", (cx, wy - 0.055, 1.52), (1.52, 0.02, 0.02), COL_BEIGE_DK)
    # Medical-gas outlet block (O2 + vacuum + air)
    make_box("Headwall_GasBlock", (cx - 0.42, wy - 0.06, 1.35), (0.26, 0.03, 0.16), COL_WHITE)
    make_cyl("Headwall_O2", (cx - 0.50, wy - 0.075, 1.35), 0.022, 0.02, (0.30, 0.60, 0.36, 1.0), axis='Y')
    make_cyl("Headwall_Vac", (cx - 0.42, wy - 0.075, 1.35), 0.022, 0.02, COL_WHITE, axis='Y')
    make_cyl("Headwall_Air", (cx - 0.34, wy - 0.075, 1.35), 0.022, 0.02, (0.62, 0.70, 0.80, 1.0), axis='Y')
    # Nurse-call panel + call button on a cord to the near rail
    make_box("Headwall_CallPanel", (cx + 0.42, wy - 0.06, 1.36), (0.18, 0.03, 0.18), COL_BEIGE)
    make_box("Headwall_CallBtn", (cx + 0.42, wy - 0.078, 1.40), (0.05, 0.012, 0.05), (0.80, 0.28, 0.24, 1.0))
    make_box("Headwall_CallPendant", (cx + 0.10, wy - 0.09, 1.02), (0.06, 0.03, 0.11), COL_BEIGE)
    # Swing-arm over-bed exam light, reaching over the pillow
    make_box("Headwall_LightMount", (cx + 0.20, wy - 0.06, 1.62), (0.10, 0.05, 0.10), COL_BEIGE_DK)
    make_cyl("Headwall_LightArm", (cx + 0.10, 4.62, 1.66), 0.018, 0.44, COL_STEEL, axis='Y', segments=8)
    make_cyl("Headwall_LightHead", (cx, 4.42, 1.62), 0.075, 0.07, COL_BEIGE, axis='Z', segments=12)
    make_cyl("Headwall_LightLens", (cx, 4.42, 1.585), 0.058, 0.012, (0.98, 0.96, 0.86, 1.0), axis='Z', segments=12)


# ═════════════════════════════════════════════════════════════════
# THE IV — the hero prop (adjudication 3). Chrome pole on a five-star
# caster base, EAST of the head (the right hand). Saline bag on the
# hook, drip chamber, a small infusion pump on the pole, the line
# dropping and draping toward the pillow / the right hand. The Morse
# key is not here; the thing standing in its way is.
# ═════════════════════════════════════════════════════════════════
def build_iv():
    make_cyl("IV_Pole", (IVX, IVY, 1.02), 0.014, 1.96, COL_STEEL, axis='Z', segments=8)
    make_cyl("IV_Hub", (IVX, IVY, 0.06), 0.05, 0.05, COL_STEEL, axis='Z', segments=10)
    import math
    for li in range(5):
        ang = li * (2.0 * math.pi / 5.0)
        ex, ey = math.cos(ang) * 0.22, math.sin(ang) * 0.22
        make_box(f"IV_Leg_{li}", (IVX + ex / 2.0, IVY + ey / 2.0, 0.05),
                 (0.03 + abs(ex) * 0.4, 0.03 + abs(ey) * 0.4, 0.03), COL_STEEL)
        make_cyl(f"IV_Caster_{li}", (IVX + ex, IVY + ey, 0.03), 0.03, 0.03, COL_CHAR, axis='X')
    make_cyl("IV_Hook", (IVX, IVY, 1.98), 0.010, 0.06, COL_STEEL, axis='Z', segments=6)
    make_box("IV_Bag", (IVX - 0.09, IVY, 1.74), (0.05, 0.15, 0.28), COL_IV_FLUID)
    make_box("IV_Bag_Label", (IVX - 0.116, IVY, 1.74), (0.002, 0.10, 0.10), COL_WHITE)
    make_cyl("IV_DripChamber", (IVX - 0.09, IVY, 1.56), 0.014, 0.09, COL_IV_FLUID, axis='Z', segments=8)
    make_box("IV_Pump", (IVX + 0.05, IVY, 1.24), (0.13, 0.11, 0.18), COL_BEIGE)
    make_box("IV_Pump_Screen", (IVX + 0.05, IVY - 0.056, 1.27), (0.08, 0.006, 0.05), (0.20, 0.34, 0.30, 1.0))
    # Line: drop from the chamber, then drape toward the pillow / right hand
    make_cyl("IV_Line_Drop", (IVX - 0.09, IVY, 1.16), 0.005, 0.70, COL_IV_FLUID, axis='Z', segments=6)
    make_box("IV_Line_Drape", (IVX - 0.16, 4.36, 0.82), (0.20, 0.008, 0.008), COL_IV_FLUID)


# ═════════════════════════════════════════════════════════════════
# OVERBED TABLE — cantilever wheeled table swung across the legs.
# On it: an issue water pitcher, a lidded cup with a bent straw. Not
# a photo, not a card — hospital issue, the one humane object, and a
# canon-negative against everything nobody has brought (see header).
# ═════════════════════════════════════════════════════════════════
def build_overbed_table():
    tbx, tby = 0.42, 3.20       # base/column on the east side
    make_box("Table_Base", (tbx, tby, 0.05), (0.28, 0.60, 0.06), COL_BEIGE_DK)
    for li, sy in enumerate((-1, +1)):
        make_cyl(f"Table_Caster_{li}", (tbx, tby + sy * 0.24, 0.03), 0.03, 0.20, COL_CHAR, axis='Y')
    make_cyl("Table_Column", (tbx, tby, 0.52), 0.028, 0.90, COL_STEEL, axis='Z', segments=8)
    make_box("Table_Top", (-0.18, tby, 0.985), (0.72, 0.46, 0.03), COL_BEIGE)
    make_box("Table_Top_Trim", (-0.18, tby, 0.968), (0.74, 0.48, 0.006), COL_BEIGE_DK)
    make_cyl("Table_Pitcher", (-0.34, tby - 0.06, 1.06), 0.055, 0.13, COL_PLASTIC, axis='Z', segments=10)
    make_cyl("Table_Pitcher_Lid", (-0.34, tby - 0.06, 1.135), 0.058, 0.02, COL_BEIGE, axis='Z', segments=10)
    make_cyl("Table_Cup", (-0.06, tby + 0.08, 1.04), 0.038, 0.09, COL_PLASTIC, axis='Z', segments=8)
    make_cyl("Table_Cup_Lid", (-0.06, tby + 0.08, 1.09), 0.040, 0.012, COL_TEAL, axis='Z', segments=8)
    make_cyl("Table_Straw", (-0.05, tby + 0.08, 1.14), 0.005, 0.10, COL_TEAL_DK, axis='Z', segments=6)


# ═════════════════════════════════════════════════════════════════
# BEDSIDE CABINET — the med-surg nightstand, east of the bed. Body,
# a drawer, a lower cupboard, laminate top, casters; a plastic
# tumbler on top. Nothing personal on it — see negatives.
# ═════════════════════════════════════════════════════════════════
def build_bedside_cabinet():
    cx, cy = 0.66, 4.05
    make_box("Cab_Body", (cx, cy, 0.40), (0.42, 0.44, 0.72), COL_BEIGE)
    make_box("Cab_Top", (cx, cy, 0.775), (0.46, 0.48, 0.03), COL_BEIGE_DK)
    make_box("Cab_Drawer", (cx - 0.215, cy, 0.60), (0.02, 0.38, 0.16), COL_BEIGE_DK)
    make_cyl("Cab_Drawer_Pull", (cx - 0.23, cy, 0.60), 0.012, 0.10, COL_STEEL, axis='Y', segments=6)
    make_box("Cab_Door", (cx - 0.215, cy, 0.34), (0.02, 0.38, 0.36), COL_BEIGE_DK)
    make_cyl("Cab_Door_Pull", (cx - 0.23, cy + 0.13, 0.34), 0.012, 0.08, COL_STEEL, axis='Z', segments=6)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_cyl(f"Cab_Caster_{li}", (cx + sx * 0.17, cy + sy * 0.18, 0.03), 0.028, 0.03, COL_CHAR, axis='X')
    make_cyl("Cab_Tumbler", (cx + 0.06, cy, 0.83), 0.036, 0.09, COL_PLASTIC, axis='Z', segments=8)


# ═════════════════════════════════════════════════════════════════
# VISITOR SEATING — the WEST (free-hand) side of the bed, where a
# visitor sits to hold the free hand (ch8:72). One vinyl-and-wood
# recliner-style ARMCHAIR "too large for" Gracie (ch8:136), facing
# the bed; one lightweight stacking side chair waiting against the
# south wall for the second visitor.
# ═════════════════════════════════════════════════════════════════
def build_visitor_seating():
    ax, ay = -1.58, 3.70        # the armchair, facing east (toward the bed)
    make_box("Armchair_Seat", (ax, ay, 0.46), (0.54, 0.56, 0.12), COL_TEAL)
    make_box("Armchair_SeatCushion", (ax, ay, 0.55), (0.48, 0.50, 0.08), COL_TEAL_DK)
    make_box("Armchair_Back", (ax - 0.24, ay, 0.80), (0.10, 0.56, 0.58), COL_TEAL)
    make_box("Armchair_BackCushion", (ax - 0.19, ay, 0.78), (0.04, 0.48, 0.48), COL_TEAL_DK)
    for sgn, nm in ((-1, "S"), (+1, "N")):
        make_box(f"Armchair_Arm_{nm}", (ax + 0.02, ay + sgn * 0.30, 0.66), (0.44, 0.08, 0.10), COL_WOOD_ARM)
        make_box(f"Armchair_ArmPost_{nm}", (ax + 0.20, ay + sgn * 0.30, 0.55), (0.06, 0.06, 0.22), COL_WOOD_ARM)
    for li, (sx, sy) in enumerate([(-1, -1), (+1, -1), (-1, +1), (+1, +1)]):
        make_box(f"Armchair_Leg_{li}", (ax + sx * 0.22, ay + sy * 0.24, 0.20), (0.05, 0.05, 0.40), COL_WOOD_ARM)
    # Stacking side chair against the south wall, waiting
    sx0, sy0 = 1.65, 1.15
    make_box("SideChair_Seat", (sx0, sy0, 0.45), (0.42, 0.42, 0.04), COL_BEIGE)
    make_box("SideChair_Back", (sx0, sy0 + 0.19, 0.66), (0.42, 0.04, 0.42), COL_BEIGE)
    make_box("SideChair_BackPad", (sx0, sy0 + 0.17, 0.66), (0.34, 0.02, 0.34), COL_TEAL)
    make_box("SideChair_SeatPad", (sx0, sy0, 0.475), (0.34, 0.34, 0.02), COL_TEAL)
    for li, (lx, ly) in enumerate([(-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)]):
        make_cyl(f"SideChair_Leg_{li}", (sx0 + lx, sy0 + ly, 0.225), 0.016, 0.45, COL_STEEL)


# ═════════════════════════════════════════════════════════════════
# EAST WINDOW — the one Anita stands by (ch8:521). Real opening (no
# glass — playbook rule), painted frame, stool + apron, and venetian
# blinds with the slats open on the Sunday morning; a pull cord and a
# bottom rail. Morning east light falls across the bed at 10:47.
# ═════════════════════════════════════════════════════════════════
def build_window_east():
    wx = ROOM_W / 2.0
    w_mid = (EWIN_SILL + EWIN_HEAD) / 2.0
    make_box("EWin_FrameT", (wx, EWIN_CY, EWIN_HEAD - 0.03), (0.14, EWIN_W, 0.06), COL_WHITE)
    make_box("EWin_FrameB", (wx, EWIN_CY, EWIN_SILL + 0.03), (0.14, EWIN_W, 0.06), COL_WHITE)
    for sgn in (-1, +1):
        make_box(f"EWin_Jamb_{sgn:+d}", (wx, EWIN_CY + sgn * (EWIN_W / 2.0 - 0.03), w_mid),
                 (0.14, 0.06, EWIN_HEAD - EWIN_SILL), COL_WHITE)
    for sgn in (-1, +1):
        make_box(f"EWin_Casing_{sgn:+d}", (wx - 0.105, EWIN_CY + sgn * (EWIN_W / 2.0 + 0.09), w_mid),
                 (0.05, 0.10, EWIN_HEAD - EWIN_SILL + 0.30), COL_WHITE)
    make_box("EWin_CasingHead", (wx - 0.105, EWIN_CY, EWIN_HEAD + 0.08), (0.05, EWIN_W + 0.28, 0.10), COL_WHITE)
    make_box("EWin_Stool", (wx - 0.135, EWIN_CY, EWIN_SILL + 0.02), (0.16, EWIN_W + 0.30, 0.04), COL_WHITE)
    make_box("EWin_Apron", (wx - 0.105, EWIN_CY, EWIN_SILL - 0.05), (0.05, EWIN_W + 0.16, 0.09), COL_WHITE)
    # Venetian blinds — head rail, open slats, bottom rail, pull cord
    make_box("EWin_BlindHead", (wx - 0.15, EWIN_CY, EWIN_HEAD - 0.02), (0.06, EWIN_W - 0.02, 0.05), COL_BEIGE)
    n_slat = 11
    z0, z1 = EWIN_SILL + 0.06, EWIN_HEAD - 0.10
    for si in range(n_slat):
        sz = z0 + (z1 - z0) * si / (n_slat - 1)
        make_box(f"EWin_Slat_{si}", (wx - 0.15, EWIN_CY, sz), (0.03, EWIN_W - 0.04, 0.012), COL_BEIGE)
    make_box("EWin_BlindBottom", (wx - 0.15, EWIN_CY, EWIN_SILL + 0.05), (0.05, EWIN_W - 0.02, 0.03), COL_BEIGE_DK)
    make_cyl("EWin_BlindCord", (wx - 0.14, EWIN_CY + EWIN_W / 2.0 - 0.10, w_mid), 0.004,
             EWIN_HEAD - EWIN_SILL, COL_LINEN, axis='Z', segments=4)


# ═════════════════════════════════════════════════════════════════
# THE DOOR — south wall gap. Baked OPEN, parked flat against Wall_S_E
# (hinged at the east jamb) so the camera shoots north through the
# gap (adjudication 4). Wide med-surg leaf with a vision-panel
# opening (framed void, no glass), a push plate and kick plate, a
# lever handle. Painted casing on the gap jambs.
# ═════════════════════════════════════════════════════════════════
def build_door_south():
    # Casing on the door gap (x -1..+1 at y 0)
    for sgn in (-1, +1):
        make_box(f"Door_Casing_{sgn:+d}", (sgn * 1.03, 0.0, 1.10), (0.10, 0.24, 2.20), COL_WHITE)
    make_box("Door_CasingHead", (0.0, 0.0, 2.24), (2.26, 0.24, 0.10), COL_WHITE)
    # The leaf, parked open flat against Wall_S_E (hinged x=+1.0),
    # lying along y ~0.15, leaf x 1.02..2.12 (1.10 m; clear of camera at x 0)
    lx = 1.57
    make_box("Door_Leaf", (lx, 0.155, 1.06), (1.10, 0.045, 2.12), COL_WHITE)
    make_box("Door_Leaf_Edge", (lx, 0.132, 1.06), (1.10, 0.006, 2.12), COL_BEIGE_DK)
    # Vision-panel opening (framed void near the top)
    for sgn in (-1, +1):
        make_box(f"Door_Vision_JambV_{sgn:+d}", (lx + sgn * 0.15, 0.155, 1.62), (0.03, 0.05, 0.44), COL_BEIGE_DK)
    for sgn in (-1, +1):
        make_box(f"Door_Vision_JambH_{sgn:+d}", (lx, 0.155, 1.62 + sgn * 0.22), (0.33, 0.05, 0.03), COL_BEIGE_DK)
    # Push plate + kick plate + lever handle
    make_box("Door_PushPlate", (lx + 0.42, 0.135, 1.12), (0.14, 0.006, 0.40), COL_STEEL)
    make_box("Door_KickPlate", (lx, 0.135, 0.14), (1.06, 0.006, 0.22), COL_STEEL)
    make_box("Door_Lever", (lx + 0.46, 0.10, 1.02), (0.12, 0.06, 0.03), COL_STEEL)
    for hi, hz in enumerate((0.40, 1.06, 1.72)):
        make_box(f"Door_Hinge_{hi}", (1.02, 0.13, hz), (0.015, 0.05, 0.10), COL_STEEL)


# ═════════════════════════════════════════════════════════════════
# PRIVACY CURTAIN — the ceiling cubicle track (the med-surg private-
# room signature) running E-W between the bed and the door, curtain
# pushed OPEN and gathered at the east end (the family is all present,
# ch8:521; nothing to screen this morning). The mesh-top band above
# the fabric is the standard cubicle drape.
# ═════════════════════════════════════════════════════════════════
def build_privacy_curtain():
    ty, tz = 2.35, CEIL - 0.06
    make_box("Curtain_Track", (-0.25, ty, tz), (4.30, 0.05, 0.04), COL_BEIGE_DK)
    for ci, cx in enumerate((-2.20, -0.90, 0.40, 1.60)):
        make_cyl(f"Curtain_Carrier_{ci}", (cx, ty, tz - 0.05), 0.012, 0.04, COL_STEEL, axis='Z', segments=6)
    # Gathered open bundle at the east end
    for fi, fx in enumerate((1.44, 1.58, 1.72)):
        make_box(f"Curtain_Fold_{fi}", (fx, ty, 1.94), (0.10, 0.09, 1.16), COL_TEAL)
    make_box("Curtain_MeshBand", (1.58, ty, 2.58), (0.42, 0.06, 0.14), COL_TEAL_DK)


# ═════════════════════════════════════════════════════════════════
# WALL FIXTURES — the clinical wall vocabulary. A BLANK patient
# whiteboard + marker tray (Label3D owns any text) and the wall clock
# holding 10:47 (the baked minute) on the north wall, camera-facing;
# an alcohol-gel dispenser, a yellow sharps container, and a glove
# box by the door on the east wall; a wall bumper rail. No flowers,
# no cards, no photos anywhere (see negatives).
# ═════════════════════════════════════════════════════════════════
def build_wall_fixtures():
    wy = ROOM_D - 0.10
    # Patient whiteboard (blank) + marker tray, north wall
    make_box("Whiteboard", (1.45, wy - 0.02, 1.58), (1.05, 0.03, 0.74), COL_WHITE)
    make_box("Whiteboard_Frame", (1.45, wy - 0.035, 1.58), (1.11, 0.02, 0.80), COL_BEIGE_DK)
    make_box("Whiteboard_Tray", (1.45, wy - 0.075, 1.20), (0.60, 0.05, 0.03), COL_BEIGE_DK)
    make_box("Whiteboard_Marker", (1.30, wy - 0.085, 1.225), (0.10, 0.014, 0.014), COL_TEAL_DK)
    # Wall clock holding 10:47 (the baked minute), north wall
    make_wall_clock("Clock", (-1.85, wy + 0.02, 2.28), frozen_hour=10, frozen_min=47,
                    palette={"face": (0.95, 0.94, 0.90, 1.0), "rim": COL_BEIGE_DK})
    # Alcohol-gel dispenser, sharps container, glove box — east wall by the door
    ex = ROOM_W / 2.0 - 0.10
    make_box("Gel_Dispenser", (ex, 0.85, 1.42), (0.03, 0.12, 0.24), COL_WHITE)
    make_box("Gel_Nozzle", (ex - 0.03, 0.85, 1.31), (0.03, 0.05, 0.04), COL_BEIGE_DK)
    make_box("Gel_DripTray", (ex - 0.04, 0.85, 1.27), (0.04, 0.12, 0.012), COL_BEIGE_DK)
    make_box("Sharps_Bin", (ex, 1.28, 1.36), (0.05, 0.22, 0.28), COL_SHARPS)
    make_box("Sharps_Lid", (ex - 0.02, 1.28, 1.51), (0.05, 0.22, 0.05), (0.62, 0.46, 0.14, 1.0))
    make_box("Sharps_Bracket", (ex + 0.02, 1.28, 1.36), (0.02, 0.24, 0.30), COL_BEIGE_DK)
    make_box("GloveBox", (ex, 1.70, 1.46), (0.04, 0.14, 0.09), COL_WHITE)
    make_box("GloveBox_Holder", (ex + 0.01, 1.70, 1.44), (0.03, 0.16, 0.13), COL_BEIGE_DK)
    # Wall bumper rail — north + east walls (institutional)
    make_box("BumperRail_N", (0.0, wy - 0.04, 0.90), (ROOM_W - 0.2, 0.04, 0.09), COL_BEIGE_DK)
    make_box("BumperRail_E", (ex - 0.02, 1.30, 0.90), (0.04, ROOM_D - 0.4, 0.09), COL_BEIGE_DK)


# ═════════════════════════════════════════════════════════════════
# CEILING INFRA — drop-tile grid (built in the shell); two recessed
# fluorescent troffers over the bed axis, a smoke detector, a
# sprinkler head (hospitals are fully sprinklered), an HVAC supply
# grille.
# ═════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    for j, ypos in enumerate((2.0, 3.7)):
        make_fluorescent_tube_fixture(f"Troffer_{j}", (BED_CX, ypos, CEIL),
                                      length=1.20, width=0.30,
                                      palette={"diffuser": (1.0, 0.98, 0.94, 1.0)})
    make_smoke_detector("Smoke", (0.9, 2.4, CEIL))
    make_sprinkler("Sprinkler", (-1.2, 1.6, CEIL))
    make_hvac_vent("HVAC", (1.3, 3.9, CEIL), width=0.80, depth=0.50)


def main():
    clear_scene()
    build_shell()
    build_bed()
    build_headwall()
    build_iv()
    build_overbed_table()
    build_bedside_cabinet()
    build_visitor_seating()
    build_window_east()
    build_door_south()
    build_privacy_curtain()
    build_wall_fixtures()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/hospital_room.glb"))
    print(f"\n[build_hospital_room] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
