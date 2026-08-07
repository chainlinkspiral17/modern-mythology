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
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

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
    make_box("Grass_Base", (1.0, 8.0, 0.0), (28.0, 22.0, 0.05), COL_GRASS)
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
        make_box(f"Bldg_Plaque_{i}", (dx, 7.94, 2.42), (0.30, 0.06, 0.34), COL_SIGN)
        # the stick figure: head + body bar; skirt triangle-read wedge on door 0
        make_cyl(f"Fig_{i}_Head", (dx, 7.90, 2.52), 0.035, 0.02, COL_DOOR, segments=8, axis='Y')
        make_box(f"Fig_{i}_Body", (dx, 7.90, 2.38), (0.03, 0.02, 0.14), COL_DOOR)
        if i == 0:
            make_box(f"Fig_{i}_Skirt", (dx, 7.90, 2.36), (0.10, 0.02, 0.05), COL_DOOR)
    # Vending machine between the doors, glowing selection column
    make_box("Vending", (-2.75, 8.10, 0.95), (0.85, 0.55, 1.90), COL_VENDING)
    make_box("Vending_Face", (-2.90, 7.80, 1.15), (0.40, 0.05, 1.30), COL_VENDING_FACE)
    make_box("Vending_Slot", (-2.45, 7.80, 0.55), (0.22, 0.04, 0.14), COL_DOOR)
    # Pay phone bracketed to the wall, receiver dangling by the cord
    make_box("Phone_Shell", (-0.75, 7.94, 1.55), (0.40, 0.14, 0.55), COL_PHONE)
    make_box("Phone_Body", (-0.75, 7.88, 1.55), (0.26, 0.06, 0.38), COL_STONE_DK)
    make_box("Phone_Cord", (-0.66, 7.86, 1.12), (0.02, 0.02, 0.50), COL_DOOR)
    make_box("Phone_Receiver", (-0.66, 7.84, 0.84), (0.07, 0.06, 0.22), COL_DOOR)
    # Brochure-rack alcove at the building's east end
    make_box("Alcove_Wall", (-0.55, 8.6, 1.5), (0.10, 1.2, 3.0), COL_BRICK_BROWN)
    make_box("Rack_Frame", (-0.68, 8.55, 1.30), (0.06, 0.9, 1.20), COL_TIMBER)
    for r in range(3):
        for cslot in range(3):
            make_box(f"Brochure_{r}_{cslot}", (-0.72, 8.25 + cslot * 0.30, 1.72 - r * 0.42),
                     (0.03, 0.22, 0.30),
                     COL_SIGN if (r + cslot) % 2 == 0 else (0.55, 0.62, 0.48, 1.0))
    # The bench beside the building (the mother's)
    make_box("Bldg_Bench_Seat", (-4.6, 7.35, 0.44), (1.5, 0.42, 0.06), COL_TIMBER)
    make_box("Bldg_Bench_Back", (-4.6, 7.55, 0.75), (1.5, 0.06, 0.40), COL_TIMBER)
    for lx in (-5.2, -4.0):
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
    make_box("Box_Lid", (5.2, 8.14, 1.39), (0.58, 0.44, 0.05), COL_ROOF)
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
        make_box(f"Rail_Post_N_{px:.1f}", (px, 15.42, 0.85), (0.10, 0.10, 1.0), COL_RAIL)
    make_box("Rail_N_Top", (9.25, 15.42, 1.32), (3.5, 0.09, 0.09), COL_RAIL)
    make_box("Rail_N_Mid", (9.25, 15.42, 0.90), (3.5, 0.07, 0.07), COL_RAIL)
    for side_x in (7.55, 10.95):
        make_box(f"Rail_Ret_{side_x:.1f}_Top", (side_x, 14.9, 1.32), (0.09, 1.1, 0.09), COL_RAIL)
        make_box(f"Rail_Ret_{side_x:.1f}_Post", (side_x, 14.35, 0.85), (0.10, 0.10, 1.0), COL_RAIL)
    # The ribbon + 707 key, tied at the top rail east of center
    make_box("Ribbon", (10.2, 15.40, 1.18), (0.05, 0.03, 0.22), COL_RIBBON)
    make_box("Key_707", (10.2, 15.40, 1.02), (0.045, 0.02, 0.10), COL_KEY)
    # THE FALLS, right below the bluff: stage one — the long shallow
    # tilted shelf, water spreading white at the lip
    make_box("Falls_Shelf", (9.5, 16.8, 0.9), (5.5, 2.6, 0.14), COL_WATER_SHELF)
    make_box("Falls_Lip", (9.5, 15.6, 1.05), (5.0, 0.35, 0.10), COL_FALLS)
    # The feather on the wet shelf ("long and grey, with a white tip")
    make_box("Feather", (8.4, 16.3, 1.00), (0.34, 0.06, 0.02), (0.55, 0.55, 0.56, 1.0))
    make_box("Feather_Tip", (8.60, 16.3, 1.005), (0.07, 0.05, 0.02), (0.86, 0.86, 0.86, 1.0))
    # Stage two — the column dropping out of sight below the shelf
    make_box("Falls_Column", (9.5, 18.3, -1.6), (2.6, 0.4, 5.4), COL_FALLS)
    make_box("Falls_Column_Core", (9.5, 18.25, -1.2), (1.4, 0.3, 4.6), (0.94, 0.96, 0.96, 1.0))
    # Mist coming up the column, warmer than the air at the railing
    make_box("Falls_Mist_Lo", (9.5, 17.6, 0.9), (3.6, 1.2, 1.8), COL_MIST)
    make_box("Falls_Mist_Hi", (9.5, 17.2, 2.2), (2.4, 0.9, 1.2), COL_MIST)
    # The gorge walls the third stage vanishes between
    make_box("Gorge_W", (6.0, 18.5, -0.8), (2.0, 3.0, 4.4), COL_BASALT)
    make_box("Gorge_E", (13.0, 18.5, -0.8), (2.0, 3.0, 4.4), COL_BASALT)


def build_picnic():
    """Canon: "a six-by-six post-and-beam square with a corrugated
    metal roof and three picnic tables under it. Two tables are
    bolted to the slab. The third is loose, set off-square." """
    cx, cy = -6.0, 11.2
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
    """Scattered pines: trunk + three shrinking canopy tiers."""
    spots = [(-10.5, 7.5), (-9.0, 13.5), (-6.5, 15.5), (-1.0, 12.0),
             (1.5, 10.5), (3.5, 13.0), (5.0, 16.5), (11.5, 9.0),
             (12.5, 12.5), (-11.5, 3.0), (13.0, 4.5), (10.5, 6.5),
             (2.0, 16.0), (-3.0, 15.8)]
    for i, (px, py) in enumerate(spots):
        h = 3.2 + 0.9 * ((i * 7) % 4)
        make_cyl(f"Pine_{i}_Trunk", (px, py, h * 0.18), 0.14, h * 0.36, COL_TRUNK, segments=6)
        col = COL_PINE if i % 2 == 0 else COL_PINE_LT
        make_box(f"Pine_{i}_T0", (px, py, h * 0.42), (1.9, 1.9, h * 0.30), col)
        make_box(f"Pine_{i}_T1", (px, py, h * 0.66), (1.4, 1.4, h * 0.26), col)
        make_box(f"Pine_{i}_T2", (px, py, h * 0.88), (0.8, 0.8, h * 0.22), col)


def build_valley():
    """Ridge planes beyond the bluff. Tops kept low so the rail sees
    over them; the falls themselves live at the overlook now."""
    make_box("Ridge_Mid", (6.0, 21.0, 2.2), (40.0, 0.06, 4.4), COL_RIDGE_MID)
    make_box("Ridge_Far", (0.0, 25.0, 3.2), (52.0, 0.06, 6.4), COL_RIDGE_FAR)
    make_box("Sky", (0.0, 30.0, 9.0), (70.0, 0.06, 18.0), COL_SKY)


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
    export_glb(out)


if __name__ == "__main__":
    main()


def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 56m. Stone ridges and wooded
    slopes closing the valley the falls cut through."""
    from _props.detail import make_far_bands
    make_far_bands("FarStone", COL_STONE_DK,
                   [(70.0, 80.0, 11.0, 0.86), (150.0, 130.0, 15.0, 0.68)],
                   profile="ridge")
    make_far_bands("FarWood", (0.18, 0.26, 0.15),
                   [(300.0, 230.0, 14.0, 0.52), (540.0, 380.0, 18.0, 0.40)],
                   profile="treeline")
