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
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl,
                             make_taper_cyl, export_glb)

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
    make_box("Main_Door", (-4.0, 8.44, 1.55), (1.3, 0.10, 2.30), COL_MAROON_DK)
    make_box("Main_Door_Glass", (-4.0, 8.40, 1.75), (0.9, 0.06, 1.4), COL_WIN_WARM)
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
    """The gate — now a modest ENTRANCE ARCH (user: "a little bit
    more grand, not much more"): two posts, a painted crossboard,
    pennants. The carved 'Twisted Beauty and a Beast' sign keeps its
    post beside it. Plus the ticket kiosk with the striped roof, a
    plank boardwalk to the porch, and string lights."""
    # Arch
    for gx in (-2.2, 0.4):
        make_box(f"Arch_Post_{gx:+.1f}", (gx, 2.0, 1.7), (0.24, 0.24, 3.4), COL_SIGN_WOOD)
    make_box("Arch_Board", (-0.9, 2.0, 3.55), (3.2, 0.20, 0.75), COL_MAROON)
    make_box("Arch_Board_Trim", (-0.9, 1.94, 3.55), (3.3, 0.06, 0.85), COL_CREAM)
    make_box("Arch_Text", (-0.9, 1.88, 3.55), (2.6, 0.05, 0.34), COL_CREAM)
    for i in range(5):
        make_box(f"Arch_Pennant_{i}", (-2.0 + i * 0.55, 1.96, 4.12 - 0.06 * (i % 2)),
                 (0.20, 0.04, 0.28), COL_BUNTING if i % 2 == 0 else COL_BUNTING_B)
    # The carved sign on its own post, beside the arch
    make_box("Gate_Post", (1.6, 2.0, 1.4), (0.22, 0.22, 2.8), COL_SIGN_WOOD)
    make_box("Gate_Sign", (1.6, 1.88, 2.35), (1.5, 0.08, 0.85), COL_SIGN_WOOD)
    make_box("Gate_Sign_Figure", (1.45, 1.82, 2.42), (0.28, 0.05, 0.55), (0.62, 0.50, 0.38, 1.0))
    make_box("Gate_Sign_Script", (1.75, 1.82, 2.10), (0.9, 0.05, 0.14), COL_CREAM)
    # Ticket kiosk — round body, candy-striped conical roof
    kx, ky = 4.9, 1.9
    make_cyl("Kiosk_Body", (kx, ky, 1.05), 0.75, 2.1, COL_CREAM, segments=10)
    make_box("Kiosk_Window", (kx - 0.05, ky - 0.72, 1.35), (0.9, 0.06, 0.6), COL_WIN_DARK)
    make_box("Kiosk_Counter", (kx - 0.05, ky - 0.80, 1.02), (1.0, 0.14, 0.06), COL_SIGN_WOOD)
    make_taper_cyl("Kiosk_Roof", (kx, ky, 2.55), 1.05, 0.06, 0.9, COL_MAROON, segments=10)
    make_taper_cyl("Kiosk_Roof_Stripe", (kx, ky, 2.42), 1.09, 0.55, 0.28, COL_CREAM, segments=10)
    make_cyl("Kiosk_Finial", (kx, ky, 3.12), 0.05, 0.28, COL_CREAM, segments=6)
    # Boardwalk: gate to porch
    for i in range(7):
        make_box(f"Boardwalk_{i}", (-1.6, 2.6 + i * 0.68, 0.06), (1.7, 0.55, 0.05), COL_SIGN_WOOD)
    # ── BUNTING, attached this time: a catenary LINE from the main
    # roof corner down to a flagpole on shack 0, flags hanging from
    # it. (They used to float mid-air with no rope and no second
    # anchor — "a clothesline hovering in air.")
    make_cyl("Bunting_Pole", (2.2, 9.8, 3.4), 0.05, 1.9, COL_SIGN_WOOD, segments=6)
    ax, az = -1.0, 6.05     # main roof corner anchor
    bx2, bz = 2.2, 4.30     # flagpole top
    segs = 8
    for i in range(segs):
        t0 = i / segs
        t1 = (i + 1) / segs
        sag0 = 0.55 * 4.0 * t0 * (1.0 - t0)
        sag1 = 0.55 * 4.0 * t1 * (1.0 - t1)
        x0, z0 = ax + (bx2 - ax) * t0, az + (bz - az) * t0 - sag0
        x1, z1 = ax + (bx2 - ax) * t1, az + (bz - az) * t1 - sag1
        mx, mz = (x0 + x1) / 2.0, (z0 + z1) / 2.0
        seg_len = ((x1 - x0) ** 2 + (z1 - z0) ** 2) ** 0.5
        make_box(f"Bunting_Line_{i}", (mx, 9.7, mz), (seg_len, 0.025, 0.025), COL_SIGN_WOOD)
        if i < segs - 1:
            col = COL_BUNTING if i % 2 == 0 else COL_BUNTING_B
            make_box(f"Bunting_{i}", (x1, 9.7, z1 - 0.20), (0.30, 0.04, 0.35), col)
    # String lights along the porch eave — warm evening bulbs
    for i in range(9):
        lx = -6.7 + i * 0.68
        make_cyl(f"StringBulb_{i}", (lx, 7.28, 2.62 - 0.10 * (1.0 - abs(i - 4) / 4.0)),
                 0.045, 0.09, COL_WIN_WARM, segments=6)
    make_box("StringWire", (-4.0, 7.28, 2.70), (5.6, 0.02, 0.02), (0.20, 0.18, 0.16, 1.0))


def build_bandstand():
    """A small open pavilion east of the pool — the third structure
    that makes it a tiny COMPLEX and not two shacks. Weathered, but
    with the striped cone roof of something that once drew crowds."""
    bx, by = 8.6, 5.4
    make_cyl("Band_Deck", (bx, by, 0.18), 2.1, 0.36, COL_SIGN_WOOD, segments=10)
    for i in range(6):
        a = i * (2 * 3.14159 / 6.0)
        px = bx + 1.75 * math.cos(a)
        py = by + 1.75 * math.sin(a)
        make_cyl(f"Band_Post_{i}", (px, py, 1.45), 0.07, 2.2, COL_CREAM, segments=6)
    make_taper_cyl("Band_Roof", (bx, by, 3.0), 2.5, 0.10, 1.1, COL_MAROON, segments=10)
    make_taper_cyl("Band_Roof_Stripe", (bx, by, 2.80), 2.56, 1.5, 0.34, COL_CREAM, segments=10)
    make_cyl("Band_Finial", (bx, by, 3.75), 0.05, 0.35, COL_CREAM, segments=6)
    make_box("Band_Rail_S", (bx, by - 1.85, 0.75), (2.6, 0.06, 0.06), COL_RAIL)


def build_cliff_and_sea():
    """The TALL edge (canon: 'built up along the edge of a cliff —
    overlooking jagged rock outcroppings, beaten raw by the harsh
    surf beneath'). The drop is 14m now — the old band fell 3m,
    which read as a garden wall, not an Oregon sea cliff."""
    make_box("Cliff_Face_Upper", (0.0, 12.5, -3.2), (30.0, 1.0, 6.6), COL_CLIFF)
    make_box("Cliff_Face_Lower", (0.0, 13.3, -10.4), (30.0, 1.8, 7.9),
             (0.24, 0.23, 0.22, 1.0))
    make_box("Cliff_Talus", (0.0, 14.3, -13.6), (30.0, 1.6, 1.6), COL_ROCK_JAG)
    # Jagged black outcroppings rising from the surf, tall enough
    # to matter against a 14m wall
    jags = [(-8.0, 15.4, 4.2), (-3.5, 16.2, 5.8), (0.5, 15.6, 3.2), (4.5, 16.6, 6.6),
            (8.5, 15.8, 3.8), (11.5, 17.0, 5.0), (-11.0, 16.6, 3.0)]
    for i, (jx, jy, jh) in enumerate(jags):
        make_box(f"Jag_{i}", (jx, jy, -14.0 + jh / 2.0), (1.5 + 0.4 * (i % 3), 1.3, jh),
                 COL_ROCK_JAG)
        make_box(f"Jag_{i}_Tip", (jx + 0.25, jy + 0.15, -14.0 + jh + 0.3),
                 (0.6, 0.6, 0.7), COL_ROCK_JAG)
    # Surf beaten raw around the rocks, far below
    make_box("Surf_0", (0.0, 15.8, -13.75), (28.0, 0.7, 0.06), COL_SURF)
    make_box("Surf_1", (-2.0, 17.2, -13.8), (24.0, 0.5, 0.05), COL_SURF)
    make_box("Surf_2", (3.0, 18.6, -13.85), (20.0, 0.4, 0.05), COL_SURF)
    make_box("Sea_Near", (0.0, 21.0, -13.9), (44.0, 6.0, 0.06), COL_SEA)
    make_box("Sea_Far", (0.0, 27.0, -13.5), (52.0, 6.5, 0.06), COL_SEA_FAR)


def main():
    clear_scene()
    build_ground()
    build_main_building()
    build_satellites()
    build_mermaid_pool()
    build_entrance()
    build_bandstand()
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
    make_box("Sea_Mid", (0.0, 62.0, -13.0), (140.0, 64.0, 0.06), COL_SEA)
    make_box("Sea_Horizon", (0.0, 250.0, -11.5), (420.0, 240.0, 0.06),
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
