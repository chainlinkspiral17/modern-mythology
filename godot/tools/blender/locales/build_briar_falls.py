"""Briar Falls — vol2's state-park rest stop, one outdoor set with
FIVE wired vantages (the whole bf_* scene cluster plays here).

Canon (vol2): a mountain rest stop — parking lot, a CCC-era stone
rest-stop building, a trailhead climbing into pines, an overlook
rail above the valley, picnic tables on the grass. The falls
themselves read as a white thread on the far ridge.

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
    # Parking lot, x ∈ [-8, 4], y ∈ [0, 6]
    make_box("Lot", (-2.0, 3.0, 0.02), (12.0, 6.0, 0.05), COL_ASPHALT)
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
    """CCC-style stone rest stop: front face at y=8, x ∈ [-5, -0.5],
    stepped-slab roof reading as pitched at distance."""
    make_box("Bldg_Body", (-2.75, 9.5, 1.5), (4.5, 3.0, 3.0), COL_STONE)
    make_box("Bldg_Base", (-2.75, 9.5, 0.3), (4.7, 3.2, 0.6), COL_STONE_DK)
    # Stepped timber roof
    make_box("Roof_0", (-2.75, 9.5, 3.15), (5.1, 3.6, 0.30), COL_ROOF)
    make_box("Roof_1", (-2.75, 9.5, 3.45), (4.0, 2.8, 0.30), COL_ROOF)
    make_box("Roof_2", (-2.75, 9.5, 3.75), (2.8, 2.0, 0.30), COL_ROOF)
    # Door + flanking windows on the south face
    make_box("Bldg_Door", (-2.75, 7.96, 1.15), (0.95, 0.10, 2.20), COL_DOOR)
    make_box("Bldg_Lintel", (-2.75, 7.94, 2.35), (1.3, 0.10, 0.22), COL_TIMBER)
    for i, wx in enumerate((-4.2, -1.3)):
        make_box(f"Bldg_Win_{i}", (wx, 7.96, 1.55), (0.85, 0.08, 0.95), COL_WIN)
        make_box(f"Bldg_WinFrame_{i}", (wx, 7.98, 1.55), (1.0, 0.06, 1.10), COL_TIMBER)
    # Info board beside the walk: two posts + cream map panel
    for px in (-1.3, -0.3):
        make_box(f"Info_Post_{px:.1f}", (px, 6.8, 0.85), (0.10, 0.10, 1.7), COL_TIMBER)
    make_box("Info_Panel", (-0.8, 6.82, 1.35), (1.3, 0.07, 0.85), COL_SIGN)
    make_box("Info_Roof", (-0.8, 6.8, 1.85), (1.5, 0.30, 0.08), COL_ROOF)


def build_trailhead():
    """Two posts + crossbeam sign at the path mouth."""
    for px in (5.9, 7.1):
        make_box(f"Trail_Post_{px:.1f}", (px, 8.6, 1.15), (0.14, 0.14, 2.3), COL_TIMBER)
    make_box("Trail_Beam", (6.5, 8.6, 2.38), (1.7, 0.12, 0.16), COL_TIMBER)
    make_box("Trail_Sign", (6.5, 8.62, 2.12), (1.1, 0.06, 0.30), COL_SIGN)


def build_overlook():
    """Raised deck at the NE corner with rail on three sides; the
    valley ridges + falls thread render beyond it."""
    make_box("Deck", (9.25, 14.5, 0.30), (3.5, 2.0, 0.12), COL_DECK)
    make_box("Deck_Skirt", (9.25, 14.5, 0.15), (3.3, 1.8, 0.30), COL_STONE_DK)
    # Rail posts + two rails: north edge and both returns
    for px in (7.6, 8.7, 9.8, 10.9):
        make_box(f"Rail_Post_N_{px:.1f}", (px, 15.42, 0.85), (0.10, 0.10, 1.0), COL_RAIL)
    make_box("Rail_N_Top", (9.25, 15.42, 1.32), (3.5, 0.09, 0.09), COL_RAIL)
    make_box("Rail_N_Mid", (9.25, 15.42, 0.90), (3.5, 0.07, 0.07), COL_RAIL)
    for side_x in (7.55, 10.95):
        make_box(f"Rail_Ret_{side_x:.1f}_Top", (side_x, 14.9, 1.32), (0.09, 1.1, 0.09), COL_RAIL)
        make_box(f"Rail_Ret_{side_x:.1f}_Post", (side_x, 14.35, 0.85), (0.10, 0.10, 1.0), COL_RAIL)


def build_picnic():
    """Two timber tables with bench boards, west grass."""
    for ti, (tx, ty) in enumerate(((-7.5, 10.0), (-4.5, 12.5))):
        make_box(f"Table_{ti}_Top", (tx, ty, 0.74), (1.9, 0.9, 0.07), COL_TABLE)
        for by in (ty - 0.75, ty + 0.75):
            make_box(f"Table_{ti}_Bench_{by:.1f}", (tx, by, 0.45), (1.9, 0.30, 0.06), COL_TABLE)
        for lx in (tx - 0.75, tx + 0.75):
            make_box(f"Table_{ti}_Leg_{lx:.1f}", (lx, ty, 0.37), (0.10, 1.9, 0.74), COL_TIMBER)


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
    """Ridge planes beyond the overlook; the falls as a white thread
    on the far ridge. Tops kept low so the rail sees over them."""
    make_box("Ridge_Mid", (6.0, 21.0, 2.2), (40.0, 0.06, 4.4), COL_RIDGE_MID)
    make_box("Ridge_Far", (0.0, 25.0, 3.2), (52.0, 0.06, 6.4), COL_RIDGE_FAR)
    make_box("Falls_Thread", (11.5, 24.9, 3.4), (0.5, 0.05, 4.2), COL_FALLS)
    make_box("Falls_Pool_Mist", (11.5, 24.85, 1.2), (1.6, 0.05, 0.7), COL_FALLS)
    make_box("Sky", (0.0, 30.0, 9.0), (70.0, 0.06, 18.0), COL_SKY)


def main():
    clear_scene()
    build_ground()
    build_building()
    build_trailhead()
    build_overlook()
    build_picnic()
    build_pines()
    build_valley()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/briar_falls.glb"))
    print(f"\n[build_briar_falls] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
