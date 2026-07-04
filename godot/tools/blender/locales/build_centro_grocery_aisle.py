"""
build_centro_grocery_aisle.py · v2 (hero pass)
══════════════════════════════════════════════════════════════════
VOL 6 · Centro Foods — Aisle Seven, mid-shift, 03:14 AM.
Diego's graveyard-stocking floor. One store, two rooms — this file
and build_centro_break_room.py share a byte-identical palette
block (KEEP IN SYNC marker below).

Canon sources (read before dressing):
  · vol6_ch10_night_shift.json — Aisle Seven is canned goods
    (stewed tomatoes, canned vegetables); Russell in dry pasta
    "down the aisle"; BT in cereal; Aisle Nine is paper goods;
    the wrong-packed pallet (cans FOUR high instead of three —
    Carl's stack); the hand truck; the cardboard bale at the end
    of the aisle; the fluorescent over Aisle Seven hums; the
    corporate "ambient music" loop (ceiling speakers); teal-blue
    Centro Foods polos (brand color); 12-aisle chain store.
  · vol6_ch22_inventory.json — canned soup SKU discipline
    ("family size, regular, low sodium — four facings, six
    facings, three deep, two stragglers on top"); the dented can
    of cream of mushroom leaking under the off-brand shelf at
    row 4F; the pallet jack Marisol left at the head of the
    aisle and forgot; chain-issued scanner ("the chain north of
    San Antonio").
  · vol6_ch16_el_rancho / ch16_dawn / ch18_stockroom — receiving
    at the back of the store; cases broken down flat; the store's
    quiet acoustic openness.

Register: REGIONAL CHAIN, NIGHT-WORN. Corporate planogram order
on the shelves (one tint per SKU run, printed price strips,
printed signage, security dome) over a tired physical plant
(scuffed lane, deferred maintenance, the leaking dented can
nobody has had fifteen minutes for). Not Kwik-Stop-personal, not
NexCorp-slick — Gas & Go discipline with Centro fatigue.

Canon-negatives (deliberately NOT built):
  · No windows — Aisle Seven is an interior volume, mid-store.
  · No dairy / glass cooler doors — dairy is a different aisle
    (and glass slabs are banned anyway; see playbook).
  · No crown molding (scaffold had it; a chain grocery has a
    painted brand band at the wall-ceiling line, not wood).
  · No hand-lettered signage on the sales floor — everything out
    here is PRINTED (the one hand-lettered sign in this store is
    Jessa's, on the break-room fridge).

Footprint (unchanged from scaffold / Background3D preset):
  Interior X ∈ [-5, +5], Y ∈ [0, +8], ceiling Z = 3.0
  Door gap at south centre (X ∈ [-1, +1]); camera enters there.
  Two N-S gondola runs at X = ±1.7 → the camera looks straight
  up the centre lane of Aisle Seven; wall shelving E + W.

Run:
    blender --background --python build_centro_grocery_aisle.py
Output:
    godot/assets/3d/locales/centro_grocery_aisle.glb
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props import palette as P
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.safety import (make_smoke_detector, make_hvac_vent,
                           make_fluorescent_tube_fixture,
                           make_ceiling_speaker, make_security_camera,
                           make_sprinkler)

ROOM_W = 10.0; ROOM_D = 8.0; CEIL = 3.0

# ═══ CENTRO FOODS SHARED PALETTE — KEEP IN SYNC ══════════════════
# One store, two rooms: this block is byte-identical in
# build_centro_grocery_aisle.py and build_centro_break_room.py.
# If you edit a constant here, edit BOTH files and verify:
#   awk '/CENTRO_PALETTE_BEGIN/,/CENTRO_PALETTE_END/' <file> | md5sum
# CENTRO_PALETTE_BEGIN
BRAND_TEAL       = (0.16, 0.42, 0.44, 1.0)   # Centro Foods teal — the polo color (vol6 ch10)
BRAND_TEAL_DARK  = (0.10, 0.28, 0.30, 1.0)
BRAND_CREAM      = (0.94, 0.92, 0.84, 1.0)   # sign lettering band
COL_FLOOR_SALES  = (0.80, 0.79, 0.74, 1.0)   # buffed VCT, sales floor
COL_FLOOR_BACK   = (0.62, 0.58, 0.52, 1.0)   # scuffed back-of-house vinyl
COL_FLOOR_SEAM   = (0.55, 0.53, 0.48, 1.0)
COL_FLOOR_SCUFF  = (0.44, 0.42, 0.38, 1.0)
COL_WALL_SALES   = (0.90, 0.89, 0.85, 1.0)
COL_WALL_BACK    = (0.78, 0.76, 0.68, 1.0)
COL_BASEBOARD    = (0.36, 0.35, 0.33, 1.0)
COL_STEEL        = (0.66, 0.68, 0.70, 1.0)
COL_METAL_DARK   = (0.22, 0.22, 0.24, 1.0)
COL_GONDOLA      = (0.88, 0.88, 0.86, 1.0)   # white shelving steel
COL_CARDBOARD    = (0.72, 0.56, 0.38, 1.0)
COL_PALLET_WOOD  = (0.60, 0.48, 0.34, 1.0)
COL_CAN_LID      = (0.78, 0.80, 0.82, 1.0)
# One tint per planogram run — chain shelf discipline (Gas & Go
# lesson: the register lives in the geometry).
CENTRO_CAN_RUNS = [
    (0.72, 0.28, 0.22, 1.0),   # stewed-tomato red (vol6 ch10)
    (0.86, 0.74, 0.44, 1.0),   # corn gold
    (0.44, 0.54, 0.36, 1.0),   # green-bean sage
    (0.92, 0.88, 0.78, 1.0),   # cream-of-mushroom (vol6 ch22, row 4F)
    (0.36, 0.44, 0.56, 1.0),   # house-brand blue
    (0.78, 0.52, 0.28, 1.0),   # chicken-soup amber
]
CENTRO_DRY_RUNS = [
    (0.86, 0.66, 0.34, 1.0),   # honey-oat gold
    (0.94, 0.82, 0.52, 1.0),   # cream wheat
    (0.56, 0.58, 0.42, 1.0),   # sage olive
    (0.62, 0.38, 0.26, 1.0),   # bran rust
    (0.42, 0.52, 0.56, 1.0),   # muted teal (house brand)
]
# CENTRO_PALETTE_END

PAL_WALL = {"wall": COL_WALL_SALES, "baseboard": COL_BASEBOARD}

# Gondola layout — two N-S runs so the entrance camera looks
# straight up the centre lane of Aisle Seven.
GOND_X   = 1.70          # gondola centreline offset from room centre
RUN_L    = 4.8           # gondola run length (Y)
RUN_CY   = 4.0           # run centre Y
SHELF_ZS = [0.30, 0.72, 1.14, 1.56]
GOND_TOP = 1.95


# ════════════════════════════════════════════════════════════════
# SHELL — footprint unchanged; sales-floor finish, teal brand band
# instead of the scaffold's crown molding (canon-negative).
# ════════════════════════════════════════════════════════════════
def build_shell():
    make_floor("Floor", (0.0, ROOM_D / 2.0, 0.0),
               size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4,
               palette={"vinyl": COL_FLOOR_SALES, "seam": COL_FLOOR_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W / 2.0, +1), ("Wall_E", +ROOM_W / 2.0, -1)]:
        make_wall(nm, (x, ROOM_D / 2.0, 0), length=ROOM_D + 0.4, height=CEIL,
                  axis='Y', palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W + 0.4, height=CEIL,
              axis='X', palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W / 4.0 + 0.5), 0.0, 0),
              length=ROOM_W / 2.0 - 1.0, height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL - 0.30), (2.0, 0.20, 0.60),
             COL_WALL_SALES)
    make_ceiling("Ceil", (0.0, ROOM_D / 2.0, CEIL),
                 size_x=ROOM_W + 0.4, size_y=ROOM_D + 0.4)
    # Teal brand band at the wall-ceiling line — the chain's paint
    # scheme (the polo teal, up on the walls).
    # Interior wall faces sit at ±(W/2 - 0.10) and 0.10 / D - 0.10;
    # the band sits 1cm PROUD of the face, never inside the wall.
    band_z = 2.42
    make_box("CentroA_Band_N", (0.0, ROOM_D - 0.115, band_z),
             (ROOM_W - 0.4, 0.02, 0.26), BRAND_TEAL)
    for sgn in (-1, +1):
        make_box(f"CentroA_Band_X{sgn:+d}",
                 (sgn * (ROOM_W / 2.0 - 0.115), ROOM_D / 2.0, band_z),
                 (0.02, ROOM_D - 0.4, 0.26), BRAND_TEAL)
        make_box(f"CentroA_Band_S{sgn:+d}",
                 (sgn * (ROOM_W / 4.0 + 0.5), 0.115, band_z),
                 (ROOM_W / 2.0 - 1.0, 0.02, 0.26), BRAND_TEAL)


# ════════════════════════════════════════════════════════════════
# GONDOLAS — two N-S runs. Lane faces (toward camera lane) carry
# canned goods; the west gondola's outer face is dry pasta
# (Russell, ch10); the east gondola's outer face is cereal (BT).
# ════════════════════════════════════════════════════════════════
def _shelf_pair(tag, gx, face_sign):
    """Shelf planks + printed price strips on one gondola face."""
    for si, shz in enumerate(SHELF_ZS):
        make_box(f"CentroA_Gond{tag}_Shelf_{si}",
                 (gx + face_sign * 0.26, RUN_CY, shz),
                 (0.42, RUN_L, 0.035), COL_GONDOLA)
        make_box(f"CentroA_Gond{tag}_Price_{si}",
                 (gx + face_sign * 0.47, RUN_CY, shz - 0.05),
                 (0.012, RUN_L, 0.04), P.PAPER)


def _can_runs(tag, gx, face_sign, stragglers=False):
    """Planogram runs of cans: cylinder front row + a depth backer
    per SKU. One tint per run (chain discipline). Cans are
    cylinders, never boxes — they sit at eye level (playbook)."""
    can_r, can_h = 0.042, 0.115
    for si, shz in enumerate(SHELF_ZS):
        top = shz + 0.0175
        for k in range(5):
            ry = 2.05 + k * 0.95
            tint = CENTRO_CAN_RUNS[(si * 2 + k) % len(CENTRO_CAN_RUNS)]
            # Depth backer — the "three deep" read behind the front row
            make_box(f"CentroA_Gond{tag}_Backer_{si}_{k}",
                     (gx + face_sign * 0.17, ry, top + 0.15),
                     (0.20, 0.62, 0.30), tint)
            for c in range(4):
                cy = ry - 0.1725 + c * 0.115
                make_cyl(f"CentroA_Gond{tag}_Can_{si}_{k}_{c}",
                         (gx + face_sign * 0.36, cy, top + can_h / 2.0),
                         can_r, can_h, tint)
                make_cyl(f"CentroA_Gond{tag}_CanLid_{si}_{k}_{c}",
                         (gx + face_sign * 0.36, cy, top + can_h + 0.004),
                         can_r + 0.001, 0.008, COL_CAN_LID)
    if stragglers:
        # "regular, six facings, three deep, two stragglers on top"
        # (vol6 ch22) — two loose cans on top of a top-shelf backer.
        s_z = SHELF_ZS[3] + 0.0175 + 0.30
        for si2, sy in enumerate([2.94, 3.08]):
            make_cyl(f"CentroA_Gond{tag}_Straggler_{si2}",
                     (gx + face_sign * 0.17, sy, s_z + can_h / 2.0),
                     can_r, can_h, CENTRO_CAN_RUNS[0])
            make_cyl(f"CentroA_Gond{tag}_StragglerLid_{si2}",
                     (gx + face_sign * 0.17, sy, s_z + can_h + 0.004),
                     can_r + 0.001, 0.008, COL_CAN_LID)


def _box_runs(tag, gx, face_sign, tints, box_w, box_d, box_h):
    """Planogram runs of boxed product (pasta / cereal)."""
    for si, shz in enumerate(SHELF_ZS):
        top = shz + 0.0175
        for k in range(5):
            ry = 2.05 + k * 0.95
            tint = tints[(si + k) % len(tints)]
            for b in range(3):
                by = ry - (box_w + 0.02) + b * (box_w + 0.02)
                make_box(f"CentroA_Gond{tag}_Box_{si}_{k}_{b}",
                         (gx + face_sign * 0.28, by, top + box_h / 2.0),
                         (box_d, box_w, box_h), tint)


def build_gondolas():
    for side, sname in [(-1, "W"), (+1, "E")]:
        gx = side * GOND_X
        make_box(f"CentroA_Gond{sname}_Kick", (gx, RUN_CY, 0.075),
                 (1.00, RUN_L, 0.15), COL_METAL_DARK)
        make_box(f"CentroA_Gond{sname}_Spine", (gx, RUN_CY, 1.05),
                 (0.10, RUN_L, 1.80), COL_GONDOLA)
        make_box(f"CentroA_Gond{sname}_TopCap", (gx, RUN_CY, GOND_TOP + 0.02),
                 (0.60, RUN_L, 0.04), COL_GONDOLA)
        for e_sgn in (-1, +1):
            ey = RUN_CY + e_sgn * (RUN_L / 2.0 + 0.03)
            make_box(f"CentroA_Gond{sname}_End_{e_sgn:+d}", (gx, ey, 0.975),
                     (1.00, 0.06, 1.95), COL_GONDOLA)
            make_box(f"CentroA_Gond{sname}_EndBand_{e_sgn:+d}",
                     (gx, ey + e_sgn * 0.035, 1.70),
                     (0.90, 0.01, 0.22), BRAND_TEAL)
        # Lane face (toward the centre lane, x=0): canned goods on
        # both gondolas. West gondola's lane face is +X, east's -X.
        lane_sign = -side
        _shelf_pair(f"{sname}L", gx, lane_sign)
        _can_runs(f"{sname}L", gx, lane_sign, stragglers=(side > 0))
        # Outer face: pasta on the west run, cereal on the east run
        outer_sign = -lane_sign
        _shelf_pair(f"{sname}O", gx, outer_sign)
        if side < 0:
            _box_runs(f"{sname}O", gx, outer_sign, CENTRO_DRY_RUNS,
                      0.16, 0.30, 0.28)          # dry pasta (Russell)
        else:
            _box_runs(f"{sname}O", gx, outer_sign, CENTRO_DRY_RUNS,
                      0.20, 0.24, 0.34)          # cereal (BT's aisle)
        # Sparse overstock cases on the gondola top — visible from
        # the 2.3m entrance vantage over the 1.95m gondola.
        for oi, oy in enumerate([2.6, 4.9]):
            make_box(f"CentroA_Gond{sname}_Overstock_{oi}",
                     (gx, oy + side * 0.2, GOND_TOP + 0.04 + 0.11),
                     (0.42, 0.32, 0.22), COL_CARDBOARD)


# ════════════════════════════════════════════════════════════════
# WALL SHELVING — west wall reads as paper goods (Aisle Nine nod,
# ch10: Diego and the toilet-paper twelve-packs); east wall is
# bagged dry goods. Standards + brackets + planks.
# ════════════════════════════════════════════════════════════════
def build_wall_shelving():
    shelf_zs = [0.35, 0.80, 1.25, 1.70]
    for side, sname in [(-1, "W"), (+1, "E")]:
        face_x = side * (ROOM_W / 2.0 - 0.10)      # interior wall face
        in_sign = -side
        for si2, sy in enumerate([1.6, 2.8, 4.0, 5.2, 6.4]):
            make_box(f"CentroA_WallStd_{sname}_{si2}",
                     (face_x + in_sign * 0.02, sy, 1.05),
                     (0.04, 0.06, 1.90), COL_STEEL)
        for si, shz in enumerate(shelf_zs):
            make_box(f"CentroA_WallShelf_{sname}_{si}",
                     (face_x + in_sign * 0.22, 4.0, shz),
                     (0.40, 5.2, 0.035), COL_GONDOLA)
            make_box(f"CentroA_WallPrice_{sname}_{si}",
                     (face_x + in_sign * 0.43, 4.0, shz - 0.05),
                     (0.012, 5.2, 0.04), P.PAPER)
            for pi in range(7):
                py = 1.65 + pi * 0.78
                if side < 0:
                    # Paper goods: big pale soft packs + brand band
                    pale = (0.90, 0.90, 0.88, 1.0)
                    make_box(f"CentroA_Paper_{sname}_{si}_{pi}",
                             (face_x + in_sign * 0.23, py, shz + 0.0175 + 0.15),
                             (0.34, 0.55, 0.30), pale)
                    band = CENTRO_DRY_RUNS[(si + pi) % len(CENTRO_DRY_RUNS)]
                    make_box(f"CentroA_PaperBand_{sname}_{si}_{pi}",
                             (face_x + in_sign * 0.41, py, shz + 0.0175 + 0.15),
                             (0.005, 0.40, 0.10), band)
                else:
                    # Bagged dry goods (rice / beans / flour sacks)
                    tint = CENTRO_DRY_RUNS[(si * 2 + pi) % len(CENTRO_DRY_RUNS)]
                    make_box(f"CentroA_Bag_{sname}_{si}_{pi}",
                             (face_x + in_sign * 0.23, py, shz + 0.0175 + 0.13),
                             (0.28, 0.32, 0.26), tint)


# ════════════════════════════════════════════════════════════════
# RECEIVING — double swing doors on the north wall (the aisle
# connects to receiving; the pallets come from there) + the
# cardboard bale cart at the end of the aisle (ch10: Diego
# flat-packs the empty case into it).
# ════════════════════════════════════════════════════════════════
def build_receiving():
    dy = ROOM_D - 0.14
    for sgn, dn in [(-1, "L"), (+1, "R")]:
        dx = sgn * 0.49
        make_box(f"CentroA_RecvDoor_{dn}", (dx, dy, 1.05),
                 (0.94, 0.06, 2.10), (0.55, 0.56, 0.58, 1.0))
        # Dark impact window — opaque is honest: the backroom is dark
        make_box(f"CentroA_RecvView_{dn}", (dx, dy - 0.035, 1.55),
                 (0.22, 0.005, 0.34), (0.10, 0.10, 0.12, 1.0))
        make_box(f"CentroA_RecvKick_{dn}", (dx, dy - 0.035, 0.22),
                 (0.90, 0.005, 0.40), COL_STEEL)
        make_box(f"CentroA_RecvBumper_{dn}", (dx, dy - 0.04, 0.95),
                 (0.90, 0.005, 0.10), (0.14, 0.14, 0.14, 1.0))
    make_box("CentroA_RecvFrame_T", (0.0, dy, 2.16),
             (2.06, 0.08, 0.10), COL_METAL_DARK)
    # Printed RECEIVING sign above (teal panel, cream letter band)
    make_box("CentroA_RecvSign_BG", (0.0, ROOM_D - 0.115, 2.72),
             (1.40, 0.02, 0.30), BRAND_TEAL_DARK)
    make_box("CentroA_RecvSign_Text", (0.0, ROOM_D - 0.13, 2.72),
             (1.10, 0.005, 0.14), BRAND_CREAM)
    # Cardboard bale cart — wire cage + flattened cases (ch10)
    bx, by = 3.40, 7.25
    for ci, (cxo, cyo) in enumerate([(-0.55, -0.38), (+0.55, -0.38),
                                     (-0.55, +0.38), (+0.55, +0.38)]):
        make_box(f"CentroA_BaleCage_Post_{ci}", (bx + cxo, by + cyo, 0.70),
                 (0.05, 0.05, 1.40), COL_STEEL)
    for ri, rz in enumerate([0.25, 0.75, 1.30]):
        make_box(f"CentroA_BaleCage_RailX_{ri}", (bx, by - 0.38, rz),
                 (1.10, 0.02, 0.04), COL_STEEL)
        make_box(f"CentroA_BaleCage_RailX2_{ri}", (bx, by + 0.38, rz),
                 (1.10, 0.02, 0.04), COL_STEEL)
        for sgn in (-1, +1):
            make_box(f"CentroA_BaleCage_RailY_{ri}_{sgn:+d}",
                     (bx + sgn * 0.55, by, rz), (0.02, 0.76, 0.04), COL_STEEL)
    for fi in range(6):
        jx = ((fi * 31) % 5 - 2) * 0.015
        make_box(f"CentroA_BaleFlat_{fi}", (bx + jx, by, 0.10 + fi * 0.055),
                 (0.98, 0.66, 0.045), COL_CARDBOARD)


# ════════════════════════════════════════════════════════════════
# STOCKING ZONE — the shift-in-progress. The pallet packed wrong
# by day side (one column FOUR cases high instead of three —
# Carl's stack, ch10), the hand truck, the open case of stewed
# tomatoes, and the pallet jack Marisol left at the head of the
# aisle three hours ago and forgot (ch22).
# ════════════════════════════════════════════════════════════════
def build_stocking_zone():
    # ── Wood pallet, centre-lane right, mid-aisle ────────────────
    px, py = 0.55, 3.30
    for si, syo in enumerate([-0.50, 0.0, +0.50]):
        make_box(f"CentroA_Pallet_Skid_{si}", (px, py + syo, 0.05),
                 (1.00, 0.09, 0.10), COL_PALLET_WOOD)
    for bi in range(5):
        make_box(f"CentroA_Pallet_Deck_{bi}",
                 (px - 0.40 + bi * 0.20, py, 0.12),
                 (0.14, 1.20, 0.03), COL_PALLET_WOOD)
    # Case columns — three high is right; the corner column is
    # FOUR high (Carl has been stacking like that since June).
    case = (0.42, 0.34, 0.26)
    cols = [(-0.24, -0.36, 3), (-0.24, +0.36, 3), (+0.24, +0.36, 2),
            (+0.24, -0.36, 4)]                    # ← Carl's stack
    for ci, (cxo, cyo, n) in enumerate(cols):
        for zi in range(n):
            make_box(f"CentroA_PalletCase_{ci}_{zi}",
                     (px + cxo, py + cyo, 0.135 + case[2] / 2.0 + zi * case[2]),
                     case, COL_CARDBOARD)
            make_box(f"CentroA_PalletCaseTape_{ci}_{zi}",
                     (px + cxo, py + cyo, 0.135 + case[2] + zi * case[2] - 0.005),
                     (0.42, 0.06, 0.004), (0.60, 0.44, 0.28, 1.0))
    # ── Open case on the floor + loose cans (stewed tomatoes) ────
    ox, oy = -0.45, 2.65
    make_box("CentroA_OpenCase", (ox, oy, 0.07), (0.42, 0.34, 0.14),
             COL_CARDBOARD)
    make_box("CentroA_OpenCase_FlapN", (ox, oy + 0.21, 0.13),
             (0.42, 0.08, 0.01), COL_CARDBOARD)
    make_box("CentroA_OpenCase_FlapS", (ox, oy - 0.21, 0.13),
             (0.42, 0.08, 0.01), COL_CARDBOARD)
    for li, (lxo, lyo) in enumerate([(0.10, 0.04), (0.02, -0.06), (-0.09, 0.05)]):
        make_cyl(f"CentroA_LooseCan_{li}", (ox + lxo, oy + lyo, 0.14 + 0.0575),
                 0.042, 0.115, CENTRO_CAN_RUNS[0])
        make_cyl(f"CentroA_LooseCanLid_{li}", (ox + lxo, oy + lyo, 0.14 + 0.119),
                 0.043, 0.008, COL_CAN_LID)
    # ── Hand truck parked against the east gondola lane face ─────
    hx, hy = 1.02, 4.55
    for sgn in (-1, +1):
        make_box(f"CentroA_HandTruck_Rail_{sgn:+d}", (hx, hy + sgn * 0.18, 0.70),
                 (0.035, 0.035, 1.30), (0.70, 0.28, 0.18, 1.0))
    for ci, cz in enumerate([0.45, 0.85, 1.25]):
        make_box(f"CentroA_HandTruck_Cross_{ci}", (hx, hy, cz),
                 (0.03, 0.36, 0.03), (0.70, 0.28, 0.18, 1.0))
    make_box("CentroA_HandTruck_Toe", (hx - 0.16, hy, 0.045),
             (0.32, 0.36, 0.02), COL_STEEL)
    make_cyl("CentroA_HandTruck_Axle", (hx + 0.04, hy, 0.10),
             0.015, 0.44, COL_METAL_DARK, axis='Y')
    for sgn in (-1, +1):
        make_cyl(f"CentroA_HandTruck_Wheel_{sgn:+d}",
                 (hx + 0.04, hy + sgn * 0.24, 0.10),
                 0.10, 0.05, (0.14, 0.14, 0.14, 1.0), axis='Y', segments=12)
    # ── Pallet jack at the head of the aisle (Marisol's, ch22) ───
    jx, jy = -0.75, 1.30
    for sgn in (-1, +1):
        make_box(f"CentroA_PalletJack_Fork_{sgn:+d}", (jx + sgn * 0.17, jy, 0.09),
                 (0.15, 1.00, 0.05), (0.72, 0.30, 0.20, 1.0))
        make_cyl(f"CentroA_PalletJack_Roller_{sgn:+d}",
                 (jx + sgn * 0.17, jy + 0.40, 0.045),
                 0.035, 0.09, COL_METAL_DARK, axis='Y')
    make_box("CentroA_PalletJack_Yoke", (jx, jy - 0.42, 0.15),
             (0.48, 0.16, 0.18), (0.72, 0.30, 0.20, 1.0))
    make_cyl("CentroA_PalletJack_Hydraulic", (jx, jy - 0.50, 0.32),
             0.06, 0.28, COL_METAL_DARK)
    make_cyl("CentroA_PalletJack_HandlePost", (jx, jy - 0.50, 0.68),
             0.018, 0.48, COL_METAL_DARK)
    make_cyl("CentroA_PalletJack_Grip", (jx, jy - 0.50, 0.93),
             0.022, 0.30, (0.14, 0.14, 0.14, 1.0), axis='X')
    for sgn in (-1, +1):
        make_cyl(f"CentroA_PalletJack_SteerWheel_{sgn:+d}",
                 (jx + sgn * 0.10, jy - 0.50, 0.09),
                 0.08, 0.06, (0.14, 0.14, 0.14, 1.0), axis='Y', segments=12)


# ════════════════════════════════════════════════════════════════
# THE DENTED CAN — cream of mushroom, leaking under the off-brand
# shelf at row 4F, clocked at four AM and not yet dealt with
# (vol6 ch22). On its side under the east gondola's lowest shelf.
# ════════════════════════════════════════════════════════════════
def build_dented_can():
    # x=1.14: half under the bottom shelf's front lip (shelf front
    # at x=1.23) but CLEAR of the gondola kick (x >= 1.20).
    dx, dy = 1.14, 5.05
    make_box("CentroA_DentLeak_Stain", (dx - 0.02, dy, 0.006),
             (0.24, 0.30, 0.002), (0.42, 0.38, 0.24, 1.0))
    make_cyl("CentroA_DentedCan", (dx, dy, 0.045),
             0.042, 0.115, CENTRO_CAN_RUNS[3], axis='Y')
    make_cyl("CentroA_DentedCanLid", (dx, dy - 0.062, 0.045),
             0.043, 0.008, COL_CAN_LID, axis='Y')


# ════════════════════════════════════════════════════════════════
# SIGNAGE — printed only (sales-floor rule): the hanging AISLE 7
# marker over the centre lane and the weekly-ad poster by the
# door. Letters abstracted as bands per pipeline convention.
# ════════════════════════════════════════════════════════════════
def build_signage():
    # Hanging Aisle 7 marker — two cables + teal two-sided panel
    ax, ay = 0.0, 4.1
    for sgn in (-1, +1):
        make_box(f"CentroA_Aisle7Sign_Cable_{sgn:+d}",
                 (ax + sgn * 0.28, ay, CEIL - 0.20),
                 (0.01, 0.01, 0.40), COL_STEEL)
    make_box("CentroA_Aisle7Sign_BG", (ax, ay, CEIL - 0.68),
             (0.80, 0.04, 0.56), BRAND_TEAL)
    for sgn in (-1, +1):
        yo = ay + sgn * 0.023
        make_box(f"CentroA_Aisle7Sign_Digit_{sgn:+d}", (ax, yo, CEIL - 0.58),
                 (0.26, 0.005, 0.30), BRAND_CREAM)
        make_box(f"CentroA_Aisle7Sign_Cat1_{sgn:+d}", (ax, yo, CEIL - 0.82),
                 (0.58, 0.005, 0.05), BRAND_CREAM)
        make_box(f"CentroA_Aisle7Sign_Cat2_{sgn:+d}", (ax, yo, CEIL - 0.90),
                 (0.44, 0.005, 0.04), BRAND_CREAM)
    # Weekly-ad poster on the south-east wall segment, by the door
    make_box("CentroA_WeeklyAd_Body", (3.0, 0.11, 1.60),
             (0.60, 0.005, 0.80), P.PAPER)
    make_box("CentroA_WeeklyAd_Header", (3.0, 0.115, 1.92),
             (0.56, 0.002, 0.12), BRAND_TEAL)
    for ri in range(3):
        make_box(f"CentroA_WeeklyAd_Row_{ri}", (3.0, 0.115, 1.66 - ri * 0.22),
                 (0.50, 0.002, 0.12), P.PAPER_AGED)


# ════════════════════════════════════════════════════════════════
# CEILING INFRA — fluorescent rows over each lane (the one over
# Aisle Seven hums, ch10), the corporate-Muzak ceiling speakers
# (the "ambient music" loop, ch10), HVAC, smoke detector,
# sprinklers, and one chain-issue security dome by the entrance.
# ════════════════════════════════════════════════════════════════
def build_ceiling_infra():
    # Centre-lane fixtures run WITH the aisle (elongated in Y)
    for j, ypos in enumerate([2.0, 4.0, 6.0]):
        make_fluorescent_tube_fixture(f"CentroA_Fluor_C{j}", (0.0, ypos, CEIL),
                                      length=0.42, width=1.50)
    for side, sname in [(-1, "W"), (+1, "E")]:
        for j, ypos in enumerate([2.8, 5.2]):
            make_fluorescent_tube_fixture(f"CentroA_Fluor_{sname}{j}",
                                          (side * 3.3, ypos, CEIL),
                                          length=0.42, width=1.50)
    make_ceiling_speaker("CentroA_Muzak_0", (-2.4, 6.2, CEIL))
    make_ceiling_speaker("CentroA_Muzak_1", (+2.4, 1.8, CEIL))
    make_hvac_vent("CentroA_HVAC_Supply", (-3.0, 7.2, CEIL),
                   width=0.90, depth=0.45)
    make_hvac_vent("CentroA_HVAC_Return", (+3.0, 1.0, CEIL),
                   width=0.90, depth=0.45)
    make_smoke_detector("CentroA_Smoke", (0.0, 6.8, CEIL))
    for si, (sx, sy) in enumerate([(-2.4, 2.6), (+2.4, 2.6),
                                   (-2.4, 5.4), (+2.4, 5.4)]):
        make_sprinkler(f"CentroA_Sprinkler_{si}", (sx, sy, CEIL))
    make_security_camera("CentroA_SecCam", (0.0, 1.3, CEIL))


# ════════════════════════════════════════════════════════════════
# FLOOR DETAILS — scuff traffic down the centre lane; the floor
# is buffed VCT but the graveyard shift walks the same line.
# ════════════════════════════════════════════════════════════════
def build_floor_details():
    for i, (sx, sy) in enumerate([
            (0.10, 1.2), (-0.25, 2.1), (0.30, 3.0), (-0.15, 4.2),
            (0.20, 5.3), (-0.30, 6.3), (2.9, 6.9), (-3.1, 2.4)]):
        make_box(f"CentroA_Scuff_{i}", (sx, sy, 0.008),
                 (0.30, 0.18, 0.001), COL_FLOOR_SCUFF)


def main():
    clear_scene()
    build_shell()
    build_gondolas()
    build_wall_shelving()
    build_receiving()
    build_stocking_zone()
    build_dented_can()
    build_signage()
    build_ceiling_infra()
    build_floor_details()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/centro_grocery_aisle.glb"))
    print(f"\n[build_centro_grocery_aisle] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
