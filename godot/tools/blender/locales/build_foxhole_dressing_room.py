"""foxhole_dressing_room — THE FOXHOLE, the dressing room. Vol 6.

Same venue as build_foxhole_bar.py / build_foxhole_stage.py (The
Foxhole, Live Oak Street strip mall, New Auburn TX). Canon is exact
and modest — vol6_ch22_foxhole.json: "The dressing room is, by
Foxhole standard, a storage closet with two folding chairs and a
clothing rack and a sign on the door that says DRESSING ROOM in
marker. The fluorescent overhead has a slow buzz."

Canon dressed into this room:
  · TWO folding chairs (Em's and Nate's) — no more. Carl sits on
    the floor against the wall; that floor stays clear.
  · The clothing rack Jesse stands at with one hand on the metal,
    and Em grips post-set (vol6_ch22).
  · The door with DRESSING ROOM in marker — leaf swung open flat
    against the south wall so the sign reads from inside.
  · ONE fluorescent overhead with a slow buzz (one dying end).
  · Water bottles — Jesse drinks half a bottle in two pulls
    backstage after the set (vol6_ch22).
  · Wall clock frozen at 8:58 — Ricky's knock: "Five." (vol6_ch22).
  · Storage-closet truth: venue shelf with boxes, flyer stock
    (the mustard half-letter prints, vol6_ch14), a road case, a
    mop and bucket. NOT a vanity mirror — this is a closet.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb
from _props.structure import make_floor, make_wall, make_ceiling
from _props.decor import make_wall_clock
from _props.safety import make_smoke_detector, make_fluorescent_tube_fixture

# Shell footprint — KEPT from the scaffold; the Background3D camera
# preset ("foxhole_dressing_room") and .tscn lights are tuned to it.
ROOM_W = 4.0; ROOM_D = 4.0; CEIL = 2.6

# ══ FOXHOLE SHARED PALETTE ═══════════════════════════════════════
# KEEP IN SYNC — declared identically in build_foxhole_bar.py /
# build_foxhole_stage.py / build_foxhole_dressing_room.py.
# One venue, three rooms: black-painted everything, beer-worn brown
# floor, silver duct tape, mustard flyer stock, fox-red accent, and
# Ramón's blue→purple→magenta LED cycle (vol6_ch20_bridge.json).
FOX_WALL        = (0.25, 0.21, 0.18, 1.0)   # scuffed charcoal-brown paint
FOX_BASEBOARD   = (0.13, 0.11, 0.09, 1.0)
FOX_FLOOR       = (0.27, 0.20, 0.14, 1.0)   # beer-worn brown plank
FOX_FLOOR_SEAM  = (0.15, 0.11, 0.08, 1.0)
FOX_FLOOR_SCUFF = (0.20, 0.15, 0.11, 1.0)
FOX_CEIL_TILE   = (0.20, 0.18, 0.16, 1.0)   # black-painted drop tile
FOX_CEIL_GRID   = (0.14, 0.13, 0.12, 1.0)
FOX_CEIL_STAIN  = (0.30, 0.26, 0.20, 1.0)
FOX_BLACK       = (0.10, 0.09, 0.09, 1.0)   # amps / PA / truss matte
FOX_STAGE_DECK  = (0.16, 0.13, 0.10, 1.0)   # scuffed black stage ply
FOX_STEEL       = (0.58, 0.60, 0.62, 1.0)
FOX_CHROME      = (0.78, 0.80, 0.82, 1.0)
FOX_WOOD        = (0.38, 0.27, 0.17, 1.0)   # bar top / table wood
FOX_TAPE_DUCT   = (0.56, 0.58, 0.61, 1.0)   # silver duct/gaff tape
FOX_TAPE_MASK   = (0.85, 0.79, 0.62, 1.0)   # Ricky's masking tape
FOX_FLYER       = (0.80, 0.66, 0.30, 1.0)   # faded mustard flyer stock
FOX_INK         = (0.16, 0.14, 0.12, 1.0)   # photocopy black
FOX_RED         = (0.70, 0.20, 0.16, 1.0)   # venue accent fox-red
FOX_CREAM       = (0.90, 0.86, 0.74, 1.0)
FOX_AMBER       = (0.92, 0.60, 0.24, 1.0)   # beer-sign warm
FOX_TOPO_GREEN  = (0.36, 0.55, 0.42, 1.0)   # Topo Chico glass
FOX_LED_BLUE    = (0.24, 0.34, 0.84, 1.0)   # Ramón's cue: deep blue…
FOX_LED_PURPLE  = (0.46, 0.24, 0.76, 1.0)   # …into deep purple…
FOX_LED_MAGENTA = (0.78, 0.26, 0.60, 1.0)   # …into a small magenta
FOX_STICKERS    = [(0.72, 0.28, 0.20, 1.0), (0.30, 0.46, 0.60, 1.0),
                   (0.86, 0.72, 0.30, 1.0), (0.42, 0.56, 0.36, 1.0),
                   (0.88, 0.86, 0.80, 1.0), (0.50, 0.30, 0.56, 1.0)]
PAL_WALL = {"wall": FOX_WALL, "baseboard": FOX_BASEBOARD}
PAL_CEIL = {"tile": FOX_CEIL_TILE, "grid": FOX_CEIL_GRID}
# ══ end shared palette ═══════════════════════════════════════════

GRAY_CHAIR = (0.60, 0.60, 0.62, 1.0)   # borrowed folding chairs
KRAFT = (0.62, 0.48, 0.30, 1.0)        # cardboard


# ── Shared venue micro-props (same helpers as build_foxhole_bar) ──
def _flyer(nm, pos, *, axis='X', face=-1, fresh=False, extra_line=False):
    """Photocopied Foxhole flyer — canon vol6_ch14_substation_nine:
    black ink on faded mustard, hand-drawn 2019 block lettering."""
    stock = FOX_CREAM if fresh else FOX_FLYER
    x, y, z = pos
    w, h = 0.28, 0.42
    if axis == 'X':
        make_box(f"{nm}_Paper", (x, y + face * 0.012, z), (w, 0.006, h), stock)
        make_box(f"{nm}_Head", (x, y + face * 0.017, z + 0.13),
                 (w * 0.80, 0.002, 0.09), FOX_INK)
        make_box(f"{nm}_Body", (x, y + face * 0.017, z - 0.06),
                 (w * 0.70, 0.002, 0.16), FOX_INK)
        if extra_line:
            make_box(f"{nm}_Bill", (x, y + face * 0.017, z - 0.17),
                     (w * 0.60, 0.002, 0.03), FOX_INK)
    else:
        make_box(f"{nm}_Paper", (x + face * 0.012, y, z), (0.006, w, h), stock)
        make_box(f"{nm}_Head", (x + face * 0.017, y, z + 0.13),
                 (0.002, w * 0.80, 0.09), FOX_INK)
        make_box(f"{nm}_Body", (x + face * 0.017, y, z - 0.06),
                 (0.002, w * 0.70, 0.16), FOX_INK)
        if extra_line:
            make_box(f"{nm}_Bill", (x + face * 0.017, y, z - 0.17),
                     (0.002, w * 0.60, 0.03), FOX_INK)


def _sticker(nm, pos, i, *, axis='X', face=-1):
    """One gig sticker on a vertical surface — deterministic tint."""
    x, y, z = pos
    col = FOX_STICKERS[i % len(FOX_STICKERS)]
    w = 0.10 + (i % 3) * 0.03
    h = 0.06 + ((i + 1) % 3) * 0.02
    if axis == 'X':
        make_box(f"{nm}_Sticker_{i}", (x, y + face * 0.006, z), (w, 0.003, h), col)
    else:
        make_box(f"{nm}_Sticker_{i}", (x + face * 0.006, y, z), (0.003, w, h), col)
# ── end shared micro-props ────────────────────────────────────────


def build_shell():
    make_floor("Floor", (0.0, ROOM_D/2.0, 0.0), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
               palette={"vinyl": FOX_FLOOR, "seam": FOX_FLOOR_SEAM})
    for nm, x, bb in [("Wall_W", -ROOM_W/2.0, +1), ("Wall_E", +ROOM_W/2.0, -1)]:
        make_wall(nm, (x, ROOM_D/2.0, 0), length=ROOM_D+0.4, height=CEIL, axis='Y',
                  palette=PAL_WALL, baseboard_face_sign=bb)
    make_wall("Wall_N", (0.0, ROOM_D, 0), length=ROOM_W+0.4, height=CEIL, axis='X',
              palette=PAL_WALL, baseboard_face_sign=-1)
    make_wall("Wall_S_W", (-(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_wall("Wall_S_E", (+(ROOM_W/4.0+0.5), 0.0, 0), length=ROOM_W/2.0-1.0,
              height=CEIL, axis='X', palette=PAL_WALL)
    make_box("Wall_S_AboveDoor", (0.0, 0.0, CEIL-0.30), (2.0, 0.20, 0.60), FOX_WALL)
    make_ceiling("Ceil", (0.0, ROOM_D/2.0, CEIL), size_x=ROOM_W+0.4, size_y=ROOM_D+0.4,
                 palette=PAL_CEIL, with_stains=False)
    # One stain, right where the ceiling meets the fluorescent.
    make_box("Ceil_Stain", (0.7, 2.5, CEIL - 0.006), (0.55, 0.55, 0.004),
             FOX_CEIL_STAIN)
    make_box("Floor_Scuff_Door", (0.0, 0.5, 0.007), (1.4, 0.7, 0.002),
             FOX_FLOOR_SCUFF)


def build_door_sign():
    """The door, swung open flat against the south wall's east leaf,
    with DRESSING ROOM in marker on a taped-up sheet (vol6_ch22)."""
    make_box("Door_Slab", (1.48, 0.16, 1.00), (0.95, 0.06, 2.00),
             (0.20, 0.16, 0.13, 1.0))
    for hi, hz in enumerate([0.35, 1.00, 1.65]):
        make_cyl(f"Door_Hinge_{hi}", (1.01, 0.13, hz), 0.018, 0.08, FOX_STEEL,
                 segments=6)
    make_cyl("Door_Knob", (1.86, 0.22, 1.00), 0.024, 0.05, FOX_STEEL, axis='Y',
             segments=8)
    # The marker sign, read from inside the room now the door is open.
    make_box("DoorSign_Paper", (1.48, 0.193, 1.45), (0.20, 0.004, 0.14), FOX_CREAM)
    make_box("DoorSign_Marker_A", (1.48, 0.196, 1.48), (0.16, 0.002, 0.03), FOX_INK)
    make_box("DoorSign_Marker_B", (1.48, 0.196, 1.42), (0.10, 0.002, 0.03), FOX_INK)
    make_box("DoorSign_Tape", (1.48, 0.196, 1.53), (0.06, 0.002, 0.025),
             FOX_TAPE_MASK)


def build_folding_chairs():
    """Exactly two — Em stretches her neck on one, Nate's on his
    phone on the other. Gray metal, borrowed-forever."""
    for ci, (cx, cy) in enumerate([(0.75, 2.30), (-0.95, 2.75)]):
        make_box(f"Chair_{ci}_Seat", (cx, cy, 0.45), (0.38, 0.38, 0.03), GRAY_CHAIR)
        make_box(f"Chair_{ci}_Back", (cx, cy + 0.17, 0.72), (0.38, 0.04, 0.34),
                 GRAY_CHAIR)
        for li, (lx, ly) in enumerate([(-0.16, -0.16), (0.16, -0.16),
                                        (-0.16, 0.16), (0.16, 0.16)]):
            make_cyl(f"Chair_{ci}_Leg_{li}", (cx + lx, cy + ly, 0.22), 0.010, 0.44,
                     (0.42, 0.42, 0.44, 1.0), segments=4)
    # Water bottles — one by each chair (vol6_ch22 backstage beat).
    make_cyl("Water_0", (0.45, 2.15, 0.10), 0.032, 0.20, (0.90, 0.92, 0.92, 1.0),
             segments=8)
    make_cyl("Water_1_HalfDrunk", (-0.65, 2.60, 0.065), 0.032, 0.13,
             (0.90, 0.92, 0.92, 1.0), segments=8)


def build_clothing_rack():
    """The rack. Jesse stands at it with one hand on the metal; Em
    puts her hand on it post-set and breathes (vol6_ch22)."""
    rack_y = 3.45
    for ui, ux in enumerate([-0.85, 0.85]):
        make_cyl(f"Rack_Upright_{ui}", (ux, rack_y, 0.90), 0.020, 1.64, FOX_CHROME)
        make_box(f"Rack_Foot_{ui}", (ux, rack_y, 0.035), (0.10, 0.50, 0.05),
                 FOX_STEEL)
        for wi, wy in enumerate([rack_y - 0.20, rack_y + 0.20]):
            make_cyl(f"Rack_Caster_{ui}_{wi}", (ux, wy, 0.03), 0.03, 0.04,
                     FOX_BLACK, axis='X', segments=8)
    make_cyl("Rack_TopBar", (0.0, rack_y, 1.72), 0.020, 1.90, FOX_CHROME, axis='X')
    # Two empty wire hangers + three hung garments.
    for hi, hx in enumerate([-0.62, 0.55]):
        make_box(f"Rack_Hanger_{hi}", (hx, rack_y, 1.64), (0.36, 0.015, 0.02),
                 FOX_STEEL)
    for gi, (gx, gw, gh, gcol) in enumerate([
            (-0.30, 0.40, 0.62, (0.14, 0.13, 0.14, 1.0)),   # black tee
            (0.05, 0.42, 0.68, FOX_RED),                     # flannel
            (0.32, 0.34, 0.55, (0.30, 0.34, 0.44, 1.0))]):   # denim
        make_box(f"Rack_Garment_{gi}", (gx, rack_y, 1.70 - gh / 2.0 - 0.04),
                 (gw, 0.06, gh), gcol)


def build_storage():
    """Storage-closet truth: venue shelf, boxes, flyer stock, spare
    cable, a road case, mop + bucket."""
    # Steel shelf unit against the E wall.
    for pi, (px, py) in enumerate([(1.55, 1.00), (1.85, 1.00), (1.55, 2.20),
                                    (1.85, 2.20)]):
        make_cyl(f"Shelf_Post_{pi}", (px, py, 0.75), 0.015, 1.50, FOX_STEEL,
                 segments=6)
    for si, sz in enumerate([0.35, 0.85, 1.35]):
        make_box(f"Shelf_Plate_{si}", (1.70, 1.60, sz), (0.36, 1.30, 0.03),
                 FOX_STEEL)
    # Bottom: two kraft boxes.
    make_box("Box_Kraft_0", (1.70, 1.25, 0.51), (0.30, 0.34, 0.28), KRAFT)
    make_box("Box_Kraft_1", (1.70, 1.85, 0.49), (0.30, 0.40, 0.24), KRAFT)
    make_box("Box_Kraft_1_TapeSeam", (1.70, 1.85, 0.615), (0.31, 0.06, 0.006),
             FOX_TAPE_DUCT)
    # Middle: shrink-wrapped water case (the set-break bottles).
    make_box("WaterCase_Tray", (1.70, 1.30, 0.88), (0.30, 0.22, 0.03), KRAFT)
    for wi in range(6):
        wx = 1.62 + (wi % 2) * 0.16
        wy = 1.22 + (wi // 2) * 0.08
        make_cyl(f"WaterCase_Bottle_{wi}", (wx, wy, 0.985), 0.030, 0.17,
                 (0.90, 0.92, 0.92, 1.0), segments=8)
    # Middle: flyer stock — a ream of the mustard prints (vol6_ch14).
    make_box("FlyerStack_Ream", (1.70, 1.95, 0.90), (0.24, 0.32, 0.07), FOX_FLYER)
    make_box("FlyerStack_TopSheet", (1.70, 1.95, 0.938), (0.22, 0.30, 0.002),
             FOX_CREAM)
    # Top: coiled spare mic cable + gaff rolls.
    make_cyl("CableCoil", (1.70, 1.30, 1.39), 0.11, 0.05, FOX_BLACK, segments=10)
    for gi in range(2):
        make_cyl(f"GaffRoll_{gi}", (1.66 + gi * 0.10, 1.95, 1.39), 0.055, 0.045,
                 FOX_TAPE_DUCT, segments=10)
    # Road case parked SW, sticker-crusted, duct-taped corner.
    make_box("RoadCase_Body", (-1.45, 1.00, 0.375), (0.65, 0.50, 0.75), FOX_BLACK)
    for ei, ex in enumerate([-1.76, -1.14]):
        make_box(f"RoadCase_Edge_{ei}", (ex, 1.00, 0.375), (0.03, 0.52, 0.77),
                 FOX_STEEL)
    make_box("RoadCase_Latch", (-1.45, 0.74, 0.42), (0.10, 0.02, 0.14), FOX_STEEL)
    make_box("RoadCase_DuctTape", (-1.45, 0.74, 0.62), (0.16, 0.012, 0.10),
             FOX_TAPE_DUCT)
    for i in range(3):
        _sticker("RoadCase", (-1.62 + i * 0.18, 0.745, 0.22 + (i % 2) * 0.12), i,
                 axis='X', face=-1)
    # Mop + yellow bucket, NE corner.
    make_cyl("Bucket", (1.55, 3.45, 0.125), 0.14, 0.25, (0.82, 0.70, 0.20, 1.0),
             segments=10)
    make_cyl("Mop_Pole", (1.72, 3.60, 0.70), 0.012, 1.30, FOX_WOOD, segments=6)
    make_box("Mop_Head", (1.72, 3.60, 0.08), (0.14, 0.14, 0.16),
             (0.72, 0.68, 0.60, 1.0))


def build_wall_dressing():
    """The clock stopped at Ricky's knock, one old flyer, marker
    tags from seven years of bands, sticker crust."""
    # 8:58 — "At eight fifty-eight Ricky knocks on the door. He
    # says: Five." (vol6_ch22_foxhole.json)
    make_wall_clock("Clock", (0.0, ROOM_D - 0.12, 2.20), frozen_hour=8,
                    frozen_min=58)
    _flyer("Flyer_W", (-(ROOM_W/2.0 - 0.10), 1.60, 1.50), axis='Y', face=+1)
    # Marker tags on the west wall — bands sign the closet, not the
    # greenroom they don't have.
    for ti in range(4):
        make_box(f"MarkerTag_{ti}",
                 (-(ROOM_W/2.0 - 0.105), 2.10 + ti * 0.35, 1.30 + (ti % 2) * 0.28),
                 (0.004, 0.26, 0.05), FOX_INK)
    make_box("MarkerTag_Red", (-(ROOM_W/2.0 - 0.105), 2.65, 1.72),
             (0.004, 0.20, 0.05), FOX_RED)
    for i in range(4):
        _sticker("WallW", (-(ROOM_W/2.0 - 0.10), 0.85 + i * 0.22,
                           1.05 + (i % 2) * 0.14), i + 1, axis='Y', face=+1)


def build_ceiling_infra():
    """ONE fluorescent overhead — 'a slow buzz' (vol6_ch22). The
    dying end of the tube reads darker."""
    make_fluorescent_tube_fixture("Fluor", (0.0, 2.0, CEIL), length=1.20, width=0.30)
    make_box("Fluor_DyingEnd", (-0.42, 2.0, CEIL - 0.145), (0.22, 0.13, 0.015),
             (0.55, 0.52, 0.46, 1.0))
    make_smoke_detector("Smoke", (0.9, 1.2, CEIL))


def main():
    clear_scene()
    build_shell()
    build_door_sign()
    build_folding_chairs()
    build_clothing_rack()
    build_storage()
    build_wall_dressing()
    build_ceiling_infra()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/foxhole_dressing_room.glb"))
    print(f"\n[build_foxhole_dressing_room] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
