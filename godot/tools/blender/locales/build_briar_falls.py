"""Briar Falls — vol2's state-park rest stop, one outdoor set with
FIVE wired vantages (the whole bf_* scene cluster plays here).

Canon (vol2 bf_* cluster, all measured from the prose): moss-eaten
asphalt; a low brick building painted brown twice, TWO marked doors
with a vending machine between them, a pay phone with the receiver
dangling by its cord, a brochure rack in the alcove; a bench beside
the building (the mother smokes on it); the wooden TRAILHEAD BOX
with hinged lid and pencil-on-a-string (the dog stares at it); a
post-and-beam picnic SHELTER with corrugated roof and three tables
(two bolted, the third loose and off-square); the blue Chrysler
minivan with faux wood trim; and Briar Falls dropping "in two
stages, then a third you cannot see" just past the railing, mist
coming up the column, a red ribbon + 707 key tied to the rail.

Coordinate frame: Blender Z-up. y=0 is the lot's south edge (the
arrival side); +Y runs north: lot → building/trailhead → picnic
grass → overlook → valley ridges. glTF export remaps to Godot
(x, z, -y).

Vantages wired in Background3D.CAMERA_PRESETS:
  briar_falls_rest_stop — mid-lot, the whole stop in one wide.
  briar_falls_building  — three-quarter on the stone building.
  briar_falls_trail     — at the trailhead posts, path climbing away.
  briar_falls_overlook  — at the rail, valley + falls beyond.
  briar_falls_picnic    — among the tables on the west grass.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb, _finalize_mesh

# ── Palette (mountain day) ──
COL_GRASS = (0.42, 0.52, 0.30, 1.0)
COL_ASPHALT = (0.22, 0.22, 0.24, 1.0)
COL_STRIPE = (0.80, 0.78, 0.70, 1.0)
COL_CURB = (0.60, 0.58, 0.52, 1.0)
COL_STONE = (0.55, 0.52, 0.46, 1.0)
COL_STONE_DK = (0.44, 0.42, 0.37, 1.0)
COL_BRICK_BROWN = (0.40, 0.30, 0.24, 1.0)   # brick painted brown, twice
COL_MOSS = (0.34, 0.42, 0.28, 1.0)
COL_VENDING = (0.62, 0.28, 0.24, 1.0)
COL_VENDING_FACE = (0.30, 0.34, 0.44, 1.0)
COL_PHONE = (0.24, 0.30, 0.40, 1.0)
COL_VAN_BLUE = (0.28, 0.38, 0.52, 1.0)
COL_VAN_WOOD = (0.46, 0.34, 0.22, 1.0)      # the faux wood trim
COL_VAN_GLASS = (0.16, 0.20, 0.26, 1.0)
COL_TIRE = (0.10, 0.10, 0.11, 1.0)
COL_RIBBON = (0.62, 0.22, 0.20, 1.0)        # faded red ribbon
COL_KEY = (0.72, 0.66, 0.42, 1.0)           # the 707 key
COL_BASALT = (0.28, 0.28, 0.30, 1.0)
COL_WATER_SHELF = (0.55, 0.64, 0.66, 1.0)   # first stage, spread thin
COL_MIST = (0.80, 0.84, 0.84, 0.45)
COL_TIMBER = (0.38, 0.28, 0.18, 1.0)
COL_ROOF = (0.30, 0.24, 0.18, 1.0)
COL_DOOR = (0.22, 0.17, 0.12, 1.0)
COL_WIN = (0.55, 0.62, 0.66, 1.0)
COL_SIGN = (0.82, 0.78, 0.64, 1.0)
COL_PATH = (0.52, 0.44, 0.32, 1.0)
COL_DECK = (0.48, 0.36, 0.24, 1.0)
COL_RAIL = (0.42, 0.32, 0.20, 1.0)
COL_TABLE = (0.50, 0.38, 0.25, 1.0)
COL_TRUNK = (0.30, 0.22, 0.15, 1.0)
COL_PINE = (0.16, 0.30, 0.20, 1.0)
COL_PINE_LT = (0.20, 0.36, 0.22, 1.0)
COL_RIDGE_MID = (0.34, 0.46, 0.42, 1.0)
COL_RIDGE_FAR = (0.44, 0.54, 0.58, 1.0)
COL_FALLS = (0.86, 0.88, 0.88, 1.0)
COL_SKY = (0.66, 0.76, 0.84, 1.0)


def build_ground():
    make_box("Grass_Base", (1.0, 6.4, 0.0), (28.0, 18.8, 0.05), COL_GRASS)   # to the bluff edge, y 15.8 (2026-10-30)
    # Parking lot, x ∈ [-8, 4], y ∈ [0, 6] — "grey-going-on-green
    # where the moss has the upper hand"
    make_box("Lot", (-2.0, 3.0, 0.02), (12.0, 6.0, 0.05), COL_ASPHALT)
    mosses = [(-6.8, 1.2, 1.6, 0.9), (-4.0, 4.6, 2.1, 1.2), (-0.5, 2.0, 1.4, 0.8),
              (2.6, 4.9, 1.8, 1.0), (-2.4, 0.6, 1.2, 0.7)]
    for i, (mx, my, mw, md) in enumerate(mosses):
        make_box(f"Lot_Moss_{i}", (mx, my, 0.055), (mw, md, 0.008), COL_MOSS)
    for i in range(5):
        make_box(f"Stripe_{i}", (-7.0 + i * 2.4, 5.1, 0.055), (0.10, 1.8, 0.012), COL_STRIPE)
    make_box("Curb_N", (-2.0, 6.05, 0.08), (12.0, 0.22, 0.16), COL_CURB)
    # Dirt path: trailhead climbing NE in three bends
    make_box("Path_0", (6.5, 9.8, 0.03), (1.1, 2.6, 0.05), COL_PATH)
    make_box("Path_1", (7.3, 12.2, 0.03), (1.0, 2.4, 0.05), COL_PATH)
    make_box("Path_2", (8.3, 14.6, 0.03), (0.9, 2.4, 0.05), COL_PATH)
    # Walk from lot to the building door
    make_box("Walk", (-2.75, 7.0, 0.03), (1.4, 2.0, 0.05), COL_CURB)


def build_building():
    """Canon: "brick painted brown, then painted brown again. Two
    doors. One stick figure with a triangle skirt; one without.
    Between them, a vending machine." Plus the pay phone (receiver
    dangling by the cord), the brochure-rack alcove, and the bench
    the mother smokes on. Front face at y=8, x ∈ [-5, -0.5]."""
    make_box("Bldg_Body", (-2.75, 9.5, 1.5), (4.5, 3.0, 3.0), COL_BRICK_BROWN)
    make_box("Bldg_Base", (-2.75, 9.5, 0.3), (4.7, 3.2, 0.6), COL_STONE_DK)
    # Flat municipal roof with a shallow cap
    make_box("Roof_0", (-2.75, 9.5, 3.12), (5.1, 3.6, 0.24), COL_ROOF)
    make_box("Roof_1", (-2.75, 9.5, 3.32), (4.7, 3.2, 0.16), COL_ROOF)
    # TWO doors on the south face, restroom plaques above each
    for i, dx in enumerate((-4.1, -1.4)):
        make_box(f"Bldg_Door_{i}", (dx, 7.96, 1.10), (0.90, 0.10, 2.20), COL_DOOR)
        # on the wall face at y 8.00 (2026-09-23: 3 cm off it)
        make_box(f"Bldg_Plaque_{i}", (dx, 7.97, 2.42), (0.30, 0.06, 0.34), COL_SIGN)
        # the stick figure: head + body bar; skirt triangle-read wedge on door 0
        make_cyl(f"Fig_{i}_Head", (dx, 7.93, 2.52), 0.035, 0.02, COL_DOOR, segments=8, axis='Y')
        make_box(f"Fig_{i}_Body", (dx, 7.93, 2.38), (0.03, 0.02, 0.14), COL_DOOR)
        if i == 0:
            make_box(f"Fig_{i}_Skirt", (dx, 7.93, 2.36), (0.10, 0.02, 0.05), COL_DOOR)
    # Vending machine between the doors, glowing selection column
    # Stands AGAINST the south face (base front y=7.9), not in it.
    make_box("Vending", (-2.75, 7.60, 0.95), (0.85, 0.55, 1.90), COL_VENDING)
    make_box("Vending_Face", (-2.90, 7.80, 1.15), (0.40, 0.05, 1.30), COL_VENDING_FACE)
    make_box("Vending_Slot", (-2.45, 7.80, 0.55), (0.22, 0.04, 0.14), COL_DOOR)
    # Pay phone bracketed to the wall, receiver dangling by the cord
    make_box("Phone_Shell", (-0.75, 7.94, 1.55), (0.40, 0.14, 0.55), COL_PHONE)
    make_box("Phone_Body", (-0.75, 7.88, 1.55), (0.26, 0.06, 0.38), COL_STONE_DK)
    make_box("Phone_Cord", (-0.66, 7.86, 1.12), (0.02, 0.02, 0.50), COL_DOOR)
    make_box("Phone_Receiver", (-0.66, 7.84, 0.84), (0.07, 0.06, 0.22), COL_DOOR)
    # Brochure-rack alcove at the building's east end
    make_box("Alcove_Wall", (-0.31, 8.6, 1.5), (0.10, 1.2, 3.0), COL_BRICK_BROWN)
    make_box("Rack_Frame", (-0.46, 8.55, 1.30), (0.06, 0.9, 1.20), COL_TIMBER)
    for r in range(3):
        for cslot in range(3):
            make_box(f"Brochure_{r}_{cslot}", (-0.42, 8.25 + cslot * 0.30, 1.72 - r * 0.42),
                     (0.03, 0.22, 0.30),
                     COL_SIGN if (r + cslot) % 2 == 0 else (0.55, 0.62, 0.48, 1.0))
    # The bench beside the building (the mother's)
    # at the building's west corner, west of door 0's swing (x -4.50)
    # — 2026-09-25: it stood across the door
    make_box("Bldg_Bench_Seat", (-5.35, 7.35, 0.44), (1.5, 0.42, 0.06), COL_TIMBER)
    make_box("Bldg_Bench_Back", (-5.35, 7.55, 0.66), (1.5, 0.06, 0.40), COL_TIMBER)   # on the seat
    for lx in (-5.95, -4.75):
        make_box(f"Bldg_Bench_Leg_{lx:.1f}", (lx, 7.38, 0.21), (0.08, 0.36, 0.42), COL_STONE_DK)
    # Info board beside the walk: two posts + cream map panel
    for px in (-1.3, -0.3):
        make_box(f"Info_Post_{px:.1f}", (px, 6.8, 0.85), (0.10, 0.10, 1.7), COL_TIMBER)
    make_box("Info_Panel", (-0.8, 6.82, 1.35), (1.3, 0.07, 0.85), COL_SIGN)
    make_box("Info_Roof", (-0.8, 6.8, 1.85), (1.5, 0.30, 0.08), COL_ROOF)


def build_trailhead():
    """Two posts + crossbeam sign at the path mouth, and THE BOX —
    "the wooden box at the trailhead… lid hinged from the back, a
    pencil on a string" — the thing the dog will not stop watching."""
    for px in (5.9, 7.1):
        make_box(f"Trail_Post_{px:.1f}", (px, 8.6, 1.15), (0.14, 0.14, 2.3), COL_TIMBER)
    make_box("Trail_Beam", (6.5, 8.6, 2.38), (1.7, 0.12, 0.16), COL_TIMBER)
    make_box("Trail_Sign", (6.5, 8.62, 2.12), (1.1, 0.06, 0.30), COL_SIGN)
    # The sign-in box on its own post, west of the posts
    make_box("Box_Post", (5.2, 8.2, 0.55), (0.13, 0.13, 1.10), COL_TIMBER)
    make_box("Box_Body", (5.2, 8.2, 1.22), (0.55, 0.40, 0.26), COL_TIMBER)
    # Lid hinged from the back, propped a crack open
    make_box("Box_Lid", (5.2, 8.14, 1.375), (0.58, 0.44, 0.05), COL_ROOF)   # on the box (2026-09-23: 1.5 cm over it)
    # The pencil on its string
    make_box("Box_String", (4.95, 8.02, 1.10), (0.015, 0.015, 0.28), COL_DOOR)
    make_box("Box_Pencil", (4.95, 8.00, 0.94), (0.03, 0.03, 0.12), (0.72, 0.58, 0.24, 1.0))


def build_overlook():
    """Canon: "the railing is bolted into a slab of basalt at the
    edge of the lot, where the asphalt stops with no fanfare and the
    bluff begins. Briar Falls drop in two stages, then a third you
    cannot see." Plus the red ribbon + 707 key tied to the rail, and
    the long grey feather on the wet shelf below."""
    # Basalt slab at the bluff edge
    make_box("Basalt_Slab", (9.25, 14.6, 0.14), (4.2, 2.4, 0.28), COL_BASALT)
    # Rail posts + two rails: north edge and both returns
    for px in (7.6, 8.7, 9.8, 10.9):
        # bolted into the slab (2026-09-23: every post stood 7 cm over it)
        make_box(f"Rail_Post_N_{px:.1f}", (px, 15.42, 0.815), (0.10, 0.10, 1.07), COL_RAIL)
    make_box("Rail_N_Top", (9.25, 15.42, 1.32), (3.5, 0.09, 0.09), COL_RAIL)
    make_box("Rail_N_Mid", (9.25, 15.42, 0.90), (3.5, 0.07, 0.07), COL_RAIL)
    for side_x in (7.55, 10.95):
        make_box(f"Rail_Ret_{side_x:.1f}_Top", (side_x, 14.9, 1.32), (0.09, 1.1, 0.09), COL_RAIL)
        make_box(f"Rail_Ret_{side_x:.1f}_Post", (side_x, 14.35, 0.815), (0.10, 0.10, 1.07), COL_RAIL)
    # The ribbon + 707 key, tied at the top rail east of center
    # the key hangs to the mid rail and rests on it (2026-09-23: it hung
    # 3.5 cm over it on a ribbon the support gate reads as cloth)
    make_box("Ribbon", (10.2, 15.40, 1.16), (0.05, 0.03, 0.25), COL_RIBBON)
    make_box("Key_707", (10.2, 15.40, 0.985), (0.045, 0.02, 0.10), COL_KEY)
    # (2026-10-30, draft 2: the falls, the mist and the gorge are
    # build_gorge_2026_10's. They were boxes on FLAT ground — the shelf a
    # slab 0.9 m above the lot, the mist two translucent boxes that read as
    # a glass case standing past the rail, the column sunk into a field.)


def build_picnic():
    """Canon: "a six-by-six post-and-beam square with a corrugated
    metal roof and three picnic tables under it. Two tables are
    bolted to the slab. The third is loose, set off-square." """
    # West of the restroom building (body x in [-5.0,-0.5], y in
    # [8.0,11.0]) — at the old cx=-6.0 the slab/posts/loose table
    # overlapped the building's whole west end.
    cx, cy = -8.6, 11.2
    make_box("Shelter_Slab", (cx, cy, 0.06), (6.4, 6.4, 0.12), COL_CURB)
    for px, py in ((cx - 3.0, cy - 3.0), (cx + 3.0, cy - 3.0),
                   (cx - 3.0, cy + 3.0), (cx + 3.0, cy + 3.0)):
        make_box(f"Shelter_Post_{px:.0f}_{py:.0f}", (px, py, 1.35), (0.20, 0.20, 2.7), COL_TIMBER)
    make_box("Shelter_Beam_S", (cx, cy - 3.0, 2.72), (6.4, 0.16, 0.20), COL_TIMBER)
    make_box("Shelter_Beam_N", (cx, cy + 3.0, 2.72), (6.4, 0.16, 0.20), COL_TIMBER)
    make_box("Shelter_Roof", (cx, cy, 2.95), (7.2, 7.2, 0.12), COL_ROOF)
    make_box("Shelter_Roof_Ridge", (cx, cy, 3.10), (5.0, 5.0, 0.12), COL_ROOF)
    # Two bolted tables, square to the slab
    tables = [(cx - 1.5, cy - 1.2, 0.0), (cx + 1.5, cy + 1.2, 0.0)]
    # The third: loose, set off-square (axis-aligned proxy: offset +
    # asymmetric bench placement so it reads shoved)
    tables.append((cx + 1.1, cy - 1.9, 1.0))
    for ti, (tx, ty, off) in enumerate(tables):
        make_box(f"Table_{ti}_Top", (tx, ty, 0.74), (1.9, 0.9, 0.07), COL_TABLE)
        for bs, by in ((0, ty - 0.75), (1, ty + 0.75)):
            bench_x = tx + (0.22 if off and bs == 0 else 0.0)
            make_box(f"Table_{ti}_Bench_{bs}", (bench_x, by, 0.45), (1.9, 0.30, 0.06), COL_TABLE)
        for lx in (tx - 0.75, tx + 0.75):
            make_box(f"Table_{ti}_Leg_{lx:.1f}", (lx, ty, 0.37), (0.10, 1.9, 0.74), COL_TIMBER)
    # The dressing the prose leaves on the tables: the face-down
    # paperback and the snapped sunglasses
    make_box("Paperback", (cx + 1.4, cy + 1.0, 0.79), (0.22, 0.15, 0.03), (0.60, 0.46, 0.26, 1.0))
    make_box("Sunglasses", (cx - 1.2, cy - 1.85, 0.485), (0.16, 0.05, 0.02), COL_DOOR)


def build_minivan():
    """The blue Chrysler minivan with faux wood trim, nosed into a
    stall mid-lot — the family's whole interlude arrives in it."""
    vx, vy = -3.2, 3.6
    make_box("Van_Body", (vx, vy, 0.85), (2.0, 4.4, 1.1), COL_VAN_BLUE)
    make_box("Van_Nose", (vx, vy + 2.35, 0.62), (1.9, 0.6, 0.55), COL_VAN_BLUE)
    # The faux wood trim band down both flanks
    for sx in (vx - 1.01, vx + 1.01):
        make_box(f"Van_Wood_{sx:.1f}", (sx, vy, 0.72), (0.03, 4.2, 0.34), COL_VAN_WOOD)
    make_box("Van_Glass_Band", (vx, vy - 0.2, 1.28), (2.04, 3.2, 0.42), COL_VAN_GLASS)
    make_box("Van_Windshield", (vx, vy + 2.05, 1.22), (1.7, 0.06, 0.5), COL_VAN_GLASS)
    for wx in (vx - 0.95, vx + 0.95):
        for wy in (vy - 1.5, vy + 1.6):
            make_cyl(f"Van_Wheel_{wx:.1f}_{wy:.1f}", (wx, wy, 0.32), 0.32, 0.22,
                     COL_TIRE, segments=10, axis='X')
    # The side door slid open (dark rectangle in the east flank)
    make_box("Van_Door_Open", (vx + 1.02, vy - 0.6, 0.85), (0.02, 1.1, 0.95), COL_VAN_GLASS)


def build_pines():
    """Scattered pines (2026-10-30: real conifers; they were three stacked
    boxes on a stick)."""
    from _props.trees import make_conifer
    # (round 4) three nudged off the shelter's and the building's roofs
    spots = [(-13.6, 6.2), (-12.2, 16.2), (-5.6, 17.0), (0.6, 13.4),
             (1.5, 10.5), (3.5, 13.0), (3.6, 15.2), (11.5, 9.0),
             (12.5, 12.5), (-11.5, 3.0), (13.0, 4.5), (10.5, 6.5),
             (2.0, 15.4), (-3.0, 15.4)]
    for i, (px, py) in enumerate(spots):
        h = 5.0 + 1.2 * ((i * 7) % 4)
        # (round 4) narrower skirts: at 0.24 the lot's pines ran their lowest
        # tier through the shelter's and the building's roofs
        make_conifer(f"Pine_{i}", px, py, h, COL_PINE if i % 2 == 0 else COL_PINE_LT, COL_TRUNK, skirt=0.16)


def build_valley():
    """Ridge planes beyond the bluff. Tops kept low so the rail sees
    over them; the falls themselves live at the overlook now."""
    # (cardboard ridge slab deleted 2026-08-04 — a 0.06m-thick
    # 'mountain' occluding the real banded ridges behind it)
    # (occluder slab deleted 2026-08-04 — a paper-thin wall 20m out
    # hiding the real receding bands built behind it)
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)


def main():
    clear_scene()
    build_ground()
    build_building()
    build_trailhead()
    build_overlook()
    build_picnic()
    build_minivan()
    build_pines()
    build_valley()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/briar_falls.glb"))
    print(f"\n[build_briar_falls] exporting to {out}")
    build_horizon_2026_08()
    build_gorge_2026_10()
    from _props.geometry import join_stock
    join_stock()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 56m. Stone ridges and wooded
    slopes closing the valley the falls cut through."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    # (2026-10-30: in four pieces around the gorge's terrain patch,
    # x -40..60, y 15.8..75.8, which it would otherwise cap)
    gf = (0.24, 0.22, 0.18, 1.0)
    make_box("Ground_Far_S", (0.0, -302.1, -0.03), (1240.0, 635.8, 0.02), gf)
    make_box("Ground_Far_N", (0.0, 347.9, -0.03), (1240.0, 544.2, 0.02), gf)
    make_box("Ground_Far_W", (-330.0, 45.8, -0.03), (580.0, 60.0, 0.02), gf)
    make_box("Ground_Far_E", (340.0, 45.8, -0.03), (560.0, 60.0, 0.02), gf)
    from _props.detail import make_far_bands
    make_far_bands("FarStone", COL_STONE_DK,
                   [(70.0, 80.0, 11.0, 0.86), (150.0, 130.0, 15.0, 0.68)],
                   profile="ridge")
    make_far_bands("FarWood", (0.18, 0.26, 0.15),
                   [(300.0, 230.0, 14.0, 0.52), (540.0, 380.0, 18.0, 0.40)],
                   profile="treeline")


def _terrain_mesh(name, verts_xyz, cells, col):
    # (_finalize_mesh is imported at module level so the audits' recorder
    # can rebind it and see the terrain)
    used = sorted({i for c in cells for i in c})
    remap = {o: n for n, o in enumerate(used)}
    return _finalize_mesh(name, [verts_xyz[i] for i in used], [[remap[i] for i in c] for c in cells], col)


def build_gorge_2026_10():
    """DRAFT 2 of the overlook (2026-10-30). "The railing is bolted into a
    slab of basalt at the edge of the lot, where the asphalt stops with no
    fanfare and the bluff begins. Briar Falls drop in two stages, then a
    third you cannot see." The land past the rail was flat; now it falls.

    - the bluff: a 5 m rock face below the rail, then the first stage's
      "long shallow" SHELF (y 17.8..30.2), tilted, the creek coming onto it
      from the east in its own cut, "white at the lip"
    - the second stage: the column "concentrates it and ... lets go", 26 m
      down a basalt face into the gorge, narrowing as it falls
    - the gorge running N, then turning W ("where the canyon turns and the
      falls go into the woods proper"), its floor stepping down out of
      sight; conifers on the rims and down in the woods
    - the mist "as a slow soft column" rising straight out of the hidden
      third stage, past the turn
    - the feather on the wet shelf below the rail
    Terrain: one height grid (x -40..60, y 15.8..75.8, 2 m), split by slope
    into rock (basalt) and forest floor. Draft 3 targets: water motion as
    streaks on the column, spray at the plunge, ferns on the ledges, a
    trail down the far rim, the rail's view framed by the pines nearest it.
    """
    import math
    from _props.geometry import make_rot_box, make_blob, make_prism
    from _props.trees import make_conifer
    X0, Y0, CELL, NC, NR = -40.0, 15.8, 2.0, 51, 31

    SH0, SH1, SZ0, SSL = 17.8, 30.2, -5.0, 0.25      # the shelf: y from/to, top z, fall per metre
    LIP = SZ0 - SSL * (SH1 - SH0)                     # -8.1

    def shelf_z(y):
        return SZ0 - SSL * (y - SH0)

    def gorge(x, y):
        """(floor z, half width, centre x) of the gorge at y, or None."""
        if y < 31.0 or y > 62.0:
            return None
        cx = 9.5 - max(0.0, y - 38.0) * 1.1
        hw = min(10.0, 4.5 + (y - 31.0) * 0.3)
        fl = -34.0 - max(0.0, 9.5 - cx) * 0.45
        return fl, hw, cx

    def rim(x, y):
        rise = max(0.0, (y - 34.0) / 41.0) * 8.0
        n = 0.35 * math.sin(x * 0.37 + y * 0.21) * math.cos(y * 0.17 - x * 0.11)
        if y < 21.0 and -2.0 < x < 22.0:
            n *= 0.3
        return rise + n

    def creek_z(x):
        return -4.7 + 0.075 * (x - 12.0)

    H = []
    for r in range(NR):
        y = Y0 + r * CELL
        row = []
        for c in range(NC):
            x = X0 + c * CELL
            if r == 0:
                row.append(0.0)
                continue
            z = rim(x, y)
            # the first stage's shelf in its notch under the bluff
            if y <= SH1 + 0.5:
                d = abs(x - 9.5)
                sz = shelf_z(min(y, SH1))
                if d <= 4.0:
                    z = sz
                elif d <= 7.0:
                    z = sz + (z - sz) * (d - 4.0) / 3.0
            # the creek's cut from the east onto the shelf
            if 18.5 <= y <= 25.5 and x > 12.0:
                cz = creek_z(x)
                dy = abs(y - 21.8)
                if dy <= 1.2:
                    z = min(z, cz)
                elif dy <= 3.2:
                    z = min(z, cz + (rim(x, y) - cz) * (dy - 1.2) / 2.0)
            g = gorge(x, y)
            if g:
                fl, hw, gx = g
                d = abs(x - gx)
                if d <= hw:
                    z = fl
                elif d <= hw + 4.0:
                    z = min(z, fl + (z - fl) * (d - hw) / 4.0)
            row.append(round(z, 3))
        H.append(row)
    verts = [(X0 + c * CELL, Y0 + r * CELL, H[r][c]) for r in range(NR) for c in range(NC)]
    # (round 2, 2026-10-30) the rock read as one flat grey: the faces split
    # into basalt STRATA (bands by height, darker and lighter, the columnar
    # layers of the coast range), MOSS on the wet rock round the falls, and
    # the forest floor in two greens
    strata = ((0.30, 0.29, 0.29, 1.0), (0.40, 0.38, 0.36, 1.0), (0.26, 0.26, 0.27, 1.0), (0.46, 0.43, 0.39, 1.0))
    rock_bands = {i: [] for i in range(len(strata))}
    moss, floor_, floor_dk = [], [], []
    for r in range(NR - 1):
        for c in range(NC - 1):
            a = r * NC + c
            q = [a, a + 1, a + NC + 1, a + NC]
            zs = [verts[i][2] for i in q]
            cxq = sum(verts[i][0] for i in q) / 4.0
            cyq = sum(verts[i][1] for i in q) / 4.0
            if max(zs) - min(zs) > 1.6:
                if (cxq - 9.5) ** 2 + (cyq - 31.0) ** 2 < 9.0 ** 2:
                    moss.append(q)
                else:
                    band = int((sum(zs) / 4.0 + 40.0) / 5.0) % len(strata)
                    rock_bands[band].append(q)
            else:
                (floor_ if (r * 7 + c * 3) % 5 else floor_dk).append(q)
    for i, cells in rock_bands.items():
        if cells:
            # (round 4) named as TERRAIN: the recorder sees a heightfield mesh as
            # its bounding box, and the overlook's camera stood "inside" the
            # rock's box (vantage_obstruction: Gorge_Rock_3 fills 100% at 1 m)
            _terrain_mesh(f"Gorge_Terrain_Rock_{i}", verts, cells, strata[i])
    if moss:
        _terrain_mesh("Gorge_Terrain_Rock_Moss", verts, moss, (0.24, 0.34, 0.22, 1.0))
    _terrain_mesh("Gorge_Ground", verts, floor_, (0.32, 0.38, 0.24, 1.0))
    _terrain_mesh("Gorge_Ground_Dk", verts, floor_dk, (0.26, 0.32, 0.20, 1.0))

    def hz(x, y):
        c = min(NC - 2, max(0, int((x - X0) / CELL)))
        r = min(NR - 2, max(0, int((y - Y0) / CELL)))
        fx, fy = (x - X0) / CELL - c, (y - Y0) / CELL - r
        z00, z10, z01, z11 = H[r][c], H[r][c + 1], H[r + 1][c], H[r + 1][c + 1]
        return (z00 * (1 - fx) + z10 * fx) * (1 - fy) + (z01 * (1 - fx) + z11 * fx) * fy

    # first stage: "the water spreading and slowing along a tilted shelf"
    slope = math.atan(SSL)
    ym = (SH0 + SH1) / 2.0
    L = (SH1 - SH0) / math.cos(slope)
    make_rot_box("Falls_Shelf_Water", (9.5, ym, shelf_z(ym) + 0.07), (7.6, L, 0.04), COL_WATER_SHELF, roll=-slope)
    for i, (sx, w, f) in enumerate(((6.6, 0.22, 0.55), (7.7, 0.40, 0.8), (8.9, 0.30, 0.9), (10.3, 0.50, 0.85),
                                    (11.5, 0.26, 0.6), (12.3, 0.20, 0.45))):
        sl = L * f
        yc = SH1 - sl * math.cos(slope) / 2.0
        make_rot_box(f"Falls_Shelf_Streak_{i}", (sx, yc, shelf_z(yc) + 0.10), (w, sl, 0.02), (0.76, 0.84, 0.86, 1.0), roll=-slope)
    # "white at the lip": a roll of foam along the edge
    for i in range(9):
        make_blob(f"Falls_Lip_Foam_{i}", (6.1 + i * 0.85, SH1 - 0.1, LIP + 0.12), 0.55, COL_FALLS, noise=0.25, seed=540 + i, squash=0.45)
    # the feather on the wet shelf below the rail ("long and grey, with a white tip")
    fz = shelf_z(18.6) + 0.10
    make_rot_box("Feather", (8.3, 18.6, fz), (0.34, 0.06, 0.02), (0.55, 0.55, 0.56, 1.0), roll=-slope)
    make_rot_box("Feather_Tip", (8.5, 18.6, fz + 0.005), (0.07, 0.05, 0.02), (0.86, 0.86, 0.86, 1.0), roll=-slope)
    # the creek in its cut, falling onto the shelf from the east
    for i in range(6):
        x0_, x1_ = 13.0 + i * 8.0, 21.0 + i * 8.0
        z0_, z1_ = creek_z(x0_) + 0.12, creek_z(x1_) + 0.12
        make_rot_box(f"Creek_Water_{i}", ((x0_ + x1_) / 2.0, 21.8, (z0_ + z1_) / 2.0),
                     (math.hypot(8.0, z1_ - z0_), 2.0, 0.04), COL_WATER_SHELF, pitch=-math.atan((z1_ - z0_) / 8.0))
        make_blob(f"Creek_Rock_{i}", (16.0 + i * 8.0, 21.8 + (0.9 if i % 2 else -0.9), creek_z(16.0 + i * 8.0) + 0.05),
                  0.5 + 0.1 * (i % 3), (0.36, 0.36, 0.36, 1.0), noise=0.3, seed=500 + i, squash=0.6)
    make_rot_box("Creek_Spill", (12.4, 21.8, (creek_z(12.6) + shelf_z(21.8)) / 2.0 + 0.1), (1.0, 2.0, 0.04), COL_FALLS,
                 pitch=-math.atan(0.4))
    # second stage: "takes the volume and concentrates it and the water
    # remembers what it is and lets go" — a sheet narrowing as it drops
    bot = -34.0
    hgt = LIP - bot
    make_prism("Falls_Column", (9.5, SH1 + 0.45, (LIP + bot) / 2.0),
               [(-3.6, hgt / 2.0), (-1.1, -hgt / 2.0), (1.1, -hgt / 2.0), (3.6, hgt / 2.0)], 0.7, COL_FALLS, axis="Y")
    make_prism("Falls_Column_Core", (9.5, SH1 + 0.85, (LIP + bot) / 2.0 - 0.2),
               [(-1.8, hgt / 2.0 - 0.4), (-0.6, -hgt / 2.0), (0.6, -hgt / 2.0), (1.8, hgt / 2.0 - 0.4)], 0.3,
               (0.97, 0.98, 0.98, 1.0), axis="Y")
    for k in range(4):
        make_blob(f"Falls_Plunge_Spray_{k}", (9.5 + (k - 1.5) * 1.6, SH1 + 2.0, bot + 1.0 + (k % 2) * 1.2), 2.4,
                  (0.92, 0.93, 0.93, 0.35), noise=0.3, seed=531 + k, squash=0.6)
    for i in range(8):
        y = 34.0 + i * 4.0
        g = gorge(9.5, y)
        if not g:
            continue
        fl, hw, gx = g
        make_box(f"Gorge_Stream_{i}", (gx, y, fl + 0.06), (min(3.0, hw), 4.2, 0.05), COL_WATER_SHELF)
    # the third stage's mist: "a slow soft column, and the column does not
    # move with the wind" — many soft overlapping puffs, straight up
    for k in range(14):
        make_blob(f"Falls_Mist_Column_{k}", (3.0 + 1.1 * math.sin(k * 1.7), 43.0 + 0.9 * math.cos(k * 1.3), -32.0 + k * 3.2),
                  5.6 - 0.10 * k, (0.92, 0.92, 0.90, 0.07), noise=0.35, seed=560 + k, squash=1.1)
    # (round 2) ferns on the shelf's banks and the bluff's ledges, the spray
    # veil drifting off the column's face
    from _props.trees import make_fern
    for i, (fx_, fy_) in enumerate(((5.2, 19.0), (5.6, 22.5), (5.0, 26.0), (13.8, 18.4), (14.2, 25.0), (13.6, 28.5),
                                    (4.0, 17.2), (15.4, 17.0), (6.0, 29.4), (13.0, 29.8))):
        make_fern(f"Ledge_Fern_Stock_{i}", fx_, fy_, h=0.6, fronds=7, z0=hz(fx_, fy_))
    for k in range(5):
        make_blob(f"Falls_Spray_Veil_{k}", (9.5 + (k - 2) * 0.9, SH1 + 1.4 + 0.3 * (k % 2), LIP - 3.0 - k * 4.0), 2.2 + 0.3 * k,
                  (0.92, 0.94, 0.94, 0.16), noise=0.3, seed=590 + k, squash=1.4)
    # conifers on the rims and down in the woods (one joined mesh: _Stock_)
    import random
    rnd = random.Random(1707)
    n = 0
    for _ in range(420):
        x = rnd.uniform(-38.0, 58.0)
        y = rnd.uniform(24.0, 62.0)       # (round 4) S of the far stone band at y 65..75
        z = hz(x, y)
        zs = [hz(x + dx, y + dy) for dx, dy in ((1.5, 0), (-1.5, 0), (0, 1.5), (0, -1.5))]
        if max(zs) - min(zs) > 1.4:
            continue                                # not on the rock faces
        if abs(x - 9.5) < 7.0 and y < 40.0:
            continue                                # keep the column and the pool clear
        if abs(x - 3.0) < 6.0 and y > 38.0 and z < -10.0:
            continue                                # the mist's own hole in the woods
        h = rnd.uniform(9.0, 17.0)
        make_conifer(f"GorgePine_Stock_{n}", x, y, h, COL_PINE if n % 2 else COL_PINE_LT, COL_TRUNK,
                     skirt=0.22, z0=z - 0.05)
        n += 1
        if n >= 140:
            break


if __name__ == "__main__":
    main()
