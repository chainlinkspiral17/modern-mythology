"""The Cliffside Circus — vol2's 1902 sideshow, home of Delores
Wiebe, the Siren of Seagash. Replaces the carnival_lot set-reuse:
canon is specific and nothing like a midwest lot.

Canon (vol2 ch2): "The Cliffside Circus looked more like a bordello
or gaming parlor than an actual circus. The main building was true
enough built up along the edge of a cliff — overlooking jagged rock
outcroppings, beaten raw by the harsh surf beneath. Smaller
satellite structures…" Delores's attraction: "a small semi-aquatic
stage with an unnatural island" — the pool with the rail the
rowdies climb over, watched by David with his bottle.

Hero features: the ornate two-story bordello-front main building at
the cliff's edge (maroon clapboard, cream trim, porch, tall
windows), two satellite shacks, the mermaid enclosure — oval pool,
fake rock island with a bent palm, the low rail around it — the
carved-sign gate post at the entrance, bunting between the roofs,
the cliff edge with jagged black outcroppings and surf lines below,
and a cold sea horizon.

Coordinate frame: Blender Z-up. y=0 is the landward entrance (the
camera side); +Y runs north: yard → buildings/pool → cliff edge
(y≈12) → rocks + surf below → sea. glTF export remaps to Godot
(x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  cliffside_circus — inside the gate looking N: main building
  left, mermaid pool + rail right, sea beyond the edge.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_GRASS = (0.40, 0.44, 0.30, 1.0)      # salt-wind headland grass
COL_DIRT = (0.46, 0.40, 0.32, 1.0)
COL_MAROON = (0.42, 0.20, 0.20, 1.0)     # bordello clapboard
COL_MAROON_DK = (0.32, 0.15, 0.15, 1.0)
COL_CREAM = (0.82, 0.76, 0.62, 1.0)      # trim
COL_ROOF = (0.26, 0.24, 0.22, 1.0)
COL_WIN_WARM = (0.90, 0.70, 0.40, 1.0)
COL_WIN_DARK = (0.16, 0.16, 0.20, 1.0)
COL_SHACK = (0.44, 0.38, 0.30, 1.0)
COL_SHACK_ROOF = (0.32, 0.28, 0.24, 1.0)
COL_POOL = (0.24, 0.38, 0.40, 1.0)
COL_POOL_EDGE = (0.58, 0.54, 0.46, 1.0)
COL_ISLAND = (0.46, 0.40, 0.34, 1.0)
COL_PALM = (0.28, 0.40, 0.24, 1.0)
COL_RAIL = (0.36, 0.28, 0.20, 1.0)
COL_SIGN_WOOD = (0.44, 0.32, 0.20, 1.0)
COL_BUNTING = (0.58, 0.26, 0.24, 1.0)
COL_BUNTING_B = (0.66, 0.60, 0.44, 1.0)
COL_CLIFF = (0.30, 0.28, 0.26, 1.0)
COL_ROCK_JAG = (0.16, 0.16, 0.17, 1.0)   # the black outcroppings
COL_SURF = (0.74, 0.78, 0.78, 1.0)
COL_SEA = (0.22, 0.30, 0.34, 1.0)
COL_SEA_FAR = (0.30, 0.38, 0.42, 1.0)
COL_SKY = (0.62, 0.66, 0.68, 1.0)        # cold coastal overcast


def build_ground():
    make_box("Headland", (0.0, 6.0, 0.0), (30.0, 12.0, 0.06), COL_GRASS)
    make_box("Yard", (0.0, 5.5, 0.02), (14.0, 8.0, 0.05), COL_DIRT)


def build_main_building():
    """Two-story bordello front along the cliff, x ∈ [-7, -1],
    face at y=8.5."""
    make_box("Main_Body", (-4.0, 10.0, 3.0), (6.0, 3.0, 6.0), COL_MAROON)
    make_box("Main_Roof", (-4.0, 10.0, 6.25), (6.6, 3.6, 0.5), COL_ROOF)
    make_box("Main_Cornice", (-4.0, 8.42, 5.85), (6.2, 0.14, 0.35), COL_CREAM)
    make_box("Main_Beltline", (-4.0, 8.42, 3.05), (6.2, 0.10, 0.25), COL_CREAM)
    # Porch across the front: deck, posts, shallow roof
    make_box("Porch_Deck", (-4.0, 7.9, 0.35), (6.0, 1.4, 0.14), COL_SIGN_WOOD)
    for px in (-6.6, -5.2, -3.8, -2.4, -1.4):
        make_cyl(f"Porch_Post_{px:.1f}", (px, 7.35, 1.55), 0.07, 2.4, COL_CREAM, segments=8)
        make_box(f"Porch_Bal_{px:.1f}", (px, 7.35, 0.75), (0.05, 0.05, 0.66), COL_CREAM)
    make_box("Porch_Rail", (-4.0, 7.35, 1.10), (5.6, 0.07, 0.08), COL_CREAM)
    make_box("Porch_Roof", (-4.0, 7.8, 2.85), (6.4, 1.8, 0.20), COL_ROOF)
    # Double door + tall warm ground windows
    make_box("Main_Door", (-4.0, 8.44, 1.35), (1.3, 0.10, 2.30), COL_MAROON_DK)
    make_box("Main_Door_Glass", (-4.0, 8.40, 1.55), (0.9, 0.06, 1.4), COL_WIN_WARM)
    for i, wx in enumerate((-6.2, -1.8)):
        make_box(f"Main_GWin_{i}", (wx, 8.44, 1.65), (0.95, 0.08, 1.9), COL_WIN_WARM)
        make_box(f"Main_GWin_Frame_{i}", (wx, 8.46, 1.65), (1.1, 0.06, 2.05), COL_CREAM)
    # Upper-story windows, mixed lit/dark
    for i, wx in enumerate((-6.3, -4.8, -3.3, -1.8)):
        col = COL_WIN_WARM if i % 2 == 0 else COL_WIN_DARK
        make_box(f"Main_UWin_{i}", (wx, 8.44, 4.45), (0.80, 0.08, 1.35), col)
        make_box(f"Main_UWin_Frame_{i}", (wx, 8.46, 4.45), (0.94, 0.06, 1.5), COL_CREAM)
    # The house sign over the porch — long cream board
    make_box("Main_Sign", (-4.0, 8.30, 3.45), (3.4, 0.08, 0.55), COL_CREAM)
    make_box("Main_Sign_Text", (-4.0, 8.26, 3.45), (2.8, 0.05, 0.24), COL_MAROON_DK)


def build_satellites():
    """Two smaller shacks east of the main building."""
    for i, (sx, sy, w, d, h) in enumerate(((2.2, 9.8, 2.6, 2.2, 2.4),
                                            (5.6, 9.0, 2.0, 1.8, 2.1))):
        make_box(f"Shack_{i}_Body", (sx, sy, h / 2.0), (w, d, h), COL_SHACK)
        make_box(f"Shack_{i}_Roof", (sx, sy, h + 0.18), (w + 0.5, d + 0.5, 0.36), COL_SHACK_ROOF)
        make_box(f"Shack_{i}_Door", (sx - w * 0.2, sy - d / 2.0 + 0.02, 0.95),
                 (0.7, 0.06, 1.9), COL_MAROON_DK)


def build_mermaid_pool():
    """Delores's enclosure: the oval pool, the unnatural island with
    its bent palm, the low rail the rowdies climb."""
    px, py = 3.0, 5.6
    # Pool: stone edge ring + water
    make_box("Pool_Water", (px, py, 0.05), (4.6, 3.2, 0.08), COL_POOL)
    edge = [(-2.5, 0.0, 0.35, 3.6), (2.5, 0.0, 0.35, 3.6), (0.0, -1.75, 5.2, 0.35),
            (0.0, 1.75, 5.2, 0.35)]
    for i, (dx, dy, w, d) in enumerate(edge):
        make_box(f"Pool_Edge_{i}", (px + dx, py + dy, 0.14), (w, d, 0.24), COL_POOL_EDGE)
    # The unnatural island — stacked fake rock + one bent palm
    make_box("Island_Base", (px + 0.6, py + 0.2, 0.28), (1.4, 1.0, 0.45), COL_ISLAND)
    make_box("Island_Top", (px + 0.5, py + 0.2, 0.60), (0.9, 0.7, 0.30), (0.52, 0.46, 0.38, 1.0))
    make_cyl("Palm_Trunk", (px + 0.8, py + 0.4, 1.15), 0.06, 0.9, COL_SIGN_WOOD, segments=6)
    make_box("Palm_Head", (px + 0.9, py + 0.4, 1.68), (0.9, 0.7, 0.18), COL_PALM)
    make_box("Palm_Frond_S", (px + 0.9, py - 0.05, 1.58), (0.5, 0.35, 0.10), COL_PALM)
    # The rail around the enclosure, one bay wide of the pool
    for rx, ry in ((px - 3.0, py - 2.3), (px + 3.0, py - 2.3), (px - 3.0, py + 2.3),
                   (px + 3.0, py + 2.3), (px, py - 2.3), (px, py + 2.3),
                   (px - 3.0, py), (px + 3.0, py)):
        make_box(f"Rail_Post_{rx:.1f}_{ry:.1f}", (rx, ry, 0.45), (0.09, 0.09, 0.90), COL_RAIL)
    make_box("Rail_S", (px, py - 2.3, 0.86), (6.1, 0.07, 0.07), COL_RAIL)
    make_box("Rail_N", (px, py + 2.3, 0.86), (6.1, 0.07, 0.07), COL_RAIL)
    make_box("Rail_W", (px - 3.0, py, 0.86), (0.07, 4.7, 0.07), COL_RAIL)
    make_box("Rail_E", (px + 3.0, py, 0.86), (0.07, 4.7, 0.07), COL_RAIL)


def build_entrance():
    """The gate post with the carved sign — the same 'Twisted Beauty
    and a Beast' board the barn preserves, new here."""
    make_box("Gate_Post", (-1.0, 2.0, 1.4), (0.22, 0.22, 2.8), COL_SIGN_WOOD)
    make_box("Gate_Sign", (-1.0, 1.88, 2.35), (1.5, 0.08, 0.85), COL_SIGN_WOOD)
    make_box("Gate_Sign_Figure", (-1.15, 1.82, 2.42), (0.28, 0.05, 0.55), (0.62, 0.50, 0.38, 1.0))
    make_box("Gate_Sign_Script", (-0.85, 1.82, 2.10), (0.9, 0.05, 0.14), COL_CREAM)
    # Bunting: sagging flag runs between main roof and shack 0
    for i in range(7):
        bx = -1.6 + i * 0.55
        sag = 0.18 * (1.0 - abs(i - 3) / 3.0)
        col = COL_BUNTING if i % 2 == 0 else COL_BUNTING_B
        make_box(f"Bunting_{i}", (bx, 9.6, 5.6 - sag), (0.30, 0.04, 0.35), col)


def build_cliff_and_sea():
    """The edge at y=12: cliff band dropping away, jagged black
    outcroppings in the surf, foam lines, cold sea to the horizon."""
    make_box("Cliff_Band", (0.0, 12.4, -1.4), (30.0, 0.8, 3.2), COL_CLIFF)
    # Jagged outcroppings — varied dark verticals poking from the surf
    jags = [(-8.0, 14.0, 1.6), (-3.5, 14.6, 2.2), (0.5, 14.2, 1.2), (4.5, 14.8, 2.6),
            (8.5, 14.3, 1.4), (11.5, 15.0, 1.9), (-11.0, 14.9, 1.1)]
    for i, (jx, jy, jh) in enumerate(jags):
        make_box(f"Jag_{i}", (jx, jy, -2.9 + jh / 2.0), (1.2 + 0.3 * (i % 3), 1.0, jh),
                 COL_ROCK_JAG)
        make_box(f"Jag_{i}_Tip", (jx + 0.2, jy + 0.1, -2.9 + jh + 0.25),
                 (0.5, 0.5, 0.5), COL_ROCK_JAG)
    # Surf beaten raw around the rocks
    make_box("Surf_0", (0.0, 14.5, -2.55), (28.0, 0.5, 0.06), COL_SURF)
    make_box("Surf_1", (-2.0, 15.6, -2.6), (24.0, 0.35, 0.05), COL_SURF)
    make_box("Sea_Near", (0.0, 18.0, -2.8), (40.0, 4.5, 0.06), COL_SEA)
    make_box("Sea_Far", (0.0, 23.0, -1.8), (48.0, 5.0, 0.06), COL_SEA_FAR)
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)


def main():
    clear_scene()
    build_ground()
    build_main_building()
    build_satellites()
    build_mermaid_pool()
    build_entrance()
    build_cliff_and_sea()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cliffside_circus.glb"))
    print(f"\n[build_cliffside_circus] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 36m. Seaward: the water runs to a
    real horizon with two dim headlands. Landward: coastal scrub
    ridges. The old Sea_Far ended 28m out."""
    make_box("Sea_Mid", (0.0, 60.0, -2.2), (140.0, 34.0, 0.06), COL_SEA)
    make_box("Sea_Horizon", (0.0, 240.0, -1.6), (420.0, 150.0, 0.06),
             (COL_SEA_FAR[0] * 1.15, COL_SEA_FAR[1] * 1.15,
              COL_SEA_FAR[2] * 1.2, 1.0))
    make_box("Headland_W", (-120.0, 150.0, 2.5), (40.0, 18.0, 5.0),
             (0.20, 0.21, 0.22, 1.0))
    make_box("Headland_E", (150.0, 200.0, 3.0), (55.0, 22.0, 6.0),
             (0.17, 0.18, 0.20, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarScrub", COL_GRASS,
                   [(70.0, 80.0, 6.0, 0.80), (150.0, 130.0, 8.0, 0.60),
                    (300.0, 220.0, 11.0, 0.44)], sides="SEW",
                   profile="ridge")


if __name__ == "__main__":
    main()
