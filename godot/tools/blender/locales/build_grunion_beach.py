"""Grunion beach — vol2's night shore, one set, two wired vantages.

Canon (vol2 ch2): "I walked down to the water's edge. It was after
dark, and the moon could not be seen behind the clouds… light was
caught up in water that gleamed off the fresh tide's edge" (the
ghost scene), and the grunion-run interlude — silver fish flickering
on the wet sand at the tide line.

Hero features: dry sand foreground with dune-grass tufts and a
driftwood log, the darker wet-sand band, three pale surf lines, the
near-black sea, a cloud bank with one hidden-moon glow patch, and a
scatter of silver grunion flecks along the tide's edge.

Coordinate frame: Blender Z-up. y=0 is the dune side (camera side);
+Y runs north toward the water: dry sand → wet band (y≈8-10) → surf
→ sea → sky. glTF export remaps to Godot (x, z, -y).

Vantages wired in Background3D.CAMERA_PRESETS:
  beach_night   — standing on the dry sand looking out at the dark
                  water (the ghost scene).
  grunion_beach — low at the tide edge, the silver run at your feet.
"""
import math, os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_rot_box, export_glb

COL_SAND = (0.34, 0.32, 0.28, 1.0)       # night sand (draft 3: a touch up, so the walk down reads)
COL_SAND_WET = (0.20, 0.20, 0.20, 1.0)   # gleaming band, darker
COL_GLEAM = (0.56, 0.60, 0.66, 1.0)      # tide-edge sheen — "water that gleamed off the fresh tide's edge"
COL_SURF = (0.72, 0.76, 0.78, 1.0)       # foam
COL_SEA = (0.07, 0.09, 0.12, 1.0)
COL_SEA_FAR = (0.10, 0.13, 0.17, 1.0)
COL_SKY = (0.13, 0.14, 0.19, 1.0)        # clouded night
COL_CLOUD = (0.18, 0.19, 0.24, 1.0)
COL_MOONGLOW = (0.30, 0.31, 0.36, 1.0)   # the moon behind the clouds
COL_GRASS = (0.16, 0.19, 0.14, 1.0)
COL_DRIFT = (0.44, 0.41, 0.37, 1.0)      # (draft 3) sea-bleached grey, as Pacific drift is
COL_GRUNION = (0.72, 0.76, 0.78, 1.0)    # silver flecks — bloom lifts them


def build_sand():
    make_box("Sand_Dry", (0.0, 4.0, 0.0), (420.0, 8.0, 0.06), COL_SAND)
    make_box("Sand_Wet", (0.0, 9.0, 0.01), (420.0, 2.2, 0.05), COL_SAND_WET)
    # The gleam: a thin lighter band right at the tide's edge
    make_box("Tide_Gleam", (0.0, 10.05, 0.03), (420.0, 0.5, 0.02), COL_GLEAM)
    # Low dune rise at the very south edge
    make_box("Dune", (0.0, -0.8, 0.20), (420.0, 2.0, 0.45), COL_SAND)


def build_sea():
    # (draft 3, 2026-10-30) the surf as BROKEN water: three lines of foam
    # in runs of 2-9 m with gaps, not three unbroken 400 m strips
    import random as _r
    rng = _r.Random(77)
    for li, (ly, lw) in enumerate(((10.6, 0.25), (11.5, 0.20), (12.6, 0.16))):
        x, k = -205.0, 0
        while x < 205.0:
            ln = rng.uniform(2.0, 9.0)
            w = lw * rng.uniform(0.6, 1.4)
            make_box(f"Surf_{li}_{k}", (x + ln / 2.0, ly + rng.uniform(-0.12, 0.12), 0.03 + 0.005 * (li == 0)), (ln, w, 0.02), COL_SURF)
            x += ln + rng.uniform(0.4, 3.5)
            k += 1
    # up to the tide gleam (2026-09-23: a 70 cm strip of nothing between
    # the gleam and the sea, with the first surf line floating over it)
    make_box("Sea_Near", (0.0, 14.15, 0.0), (440.0, 7.7, 0.05), COL_SEA)
    make_box("Sea_Far", (0.0, 21.0, 0.4), (460.0, 6.0, 0.05), COL_SEA_FAR)


def build_sky():
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)
    # (2026-09-30, draft 2: the three cloud "slabs" 24 m out — 22 x 2.6 m
    # cards 6 cm thick — rendered as black bars hung in the sky of both
    # vantages, and the moon glow as a grey card between them. The cloud
    # deck is build_shore_2026_09's now: far, lumpy, fogged.)
    return


def build_foreground():
    # Driftwood log, half-buried
    make_cyl("Driftwood", (-3.5, 4.8, 0.16), 0.22, 3.2, COL_DRIFT, segments=8, axis='X')
    make_cyl("Driftwood_Stub", (-1.8, 4.6, 0.30), 0.10, 0.5, COL_DRIFT, segments=6)
    # Dune-grass tufts: thin dark blades in clumps
    clumps = [(-6.5, 0.8), (-4.0, 1.6), (-0.5, 0.6), (2.5, 1.4), (5.5, 0.9), (8.0, 1.8)]
    for ci, (cx, cy) in enumerate(clumps):
        for b in range(5):
            bx = cx + 0.10 * ((b * 7 + ci * 3) % 5 - 2)
            h = 0.35 + 0.10 * ((b + ci) % 3)
            make_box(f"Grass_{ci}_{b}", (bx, cy + 0.06 * (b % 3), h / 2.0),
                     (0.03, 0.03, h), COL_GRASS)


def build_grunion():
    """The run: silver flecks scattered along the wet band. Sparse
    enough to read as fish, not noise."""
    for i in range(26):
        gx = -14.0 + (i * 41) % 28 + 0.35 * ((i * 7) % 3)
        gy = 9.3 + 0.011 * ((i * 13) % 100)
        # on the gleam, or on the sea past it (2026-09-23: 2 cm over the sea)
        make_box(f"Grunion_{i}", (gx, gy, 0.055 if gy <= 10.3 else 0.035),
                 (0.16, 0.045, 0.02), COL_GRUNION)


def build_bonfires_2026_10():
    """(2026-10-29) THE BONFIRE — vol 2, ch10 and ch12x, played on this beach
    with no fire in it. ch10: "Frank and I built a bonfire on the beach and
    spent the night out there, drunk beyond good measure… Frank tossed his
    empty bottle in the fire and watched it smoke up from the inside"; they
    had bought "saltwater taffy and beer". ch12x: "a white-capped moonlit
    beach, dotted with campfires and larger bonfires… From the top of the
    dune the fires run on down the beach as far as anybody can see, one and
    then another, like porch lights along a county road"; "Two women are
    sitting on a patchwork quilt by the fire."
    Every part is Bonfire_*: the ghost scene's two views (beach_night,
    grunion_beach) strip them; beach_bonfire shows them."""
    fx, fy = -1.0, 5.0
    ember = (1.0, 0.46, 0.14, 1.0)
    flame = (1.0, 0.78, 0.30, 1.0)
    char = (0.12, 0.10, 0.09, 1.0)
    make_cyl("Bonfire_Ring", (fx, fy, 0.05), 0.75, 0.06, char, segments=16)
    for k in range(7):                                  # the stacked driftwood, leaning in
        a = k * (2 * math.pi / 7)
        make_rot_box(f"Bonfire_Log_{k}", (fx + 0.28 * math.cos(a), fy + 0.28 * math.sin(a), 0.40),   # (feet on the sand, not 7 cm under it)
                     (0.10, 0.10, 0.78), COL_DRIFT, yaw=a, pitch=0.55)
    make_blob("Bonfire_Flame_Glow_Core", (fx, fy, 0.42), 0.30, ember, noise=0.25, seed=4, squash=1.6)
    make_blob("Bonfire_Flame_Glow_Top", (fx, fy, 0.82), 0.18, flame, noise=0.3, seed=9, squash=1.9)
    make_blob("Bonfire_Embers_Glow", (fx, fy, 0.10), 0.42, (0.70, 0.22, 0.08, 1.0), noise=0.18, seed=2, squash=0.25)
    # the logs they sat on, the bottles, the taffy, the quilt
    make_rot_box("Bonfire_Seat_Log_0", (fx - 0.2, fy - 1.7, 0.18), (2.2, 0.34, 0.34), COL_DRIFT, yaw=0.12)   # (off the old driftwood, 2026-10-30)
    make_rot_box("Bonfire_Seat_Log_1", (fx + 1.5, fy - 0.9, 0.16), (1.8, 0.30, 0.30), COL_DRIFT, yaw=-0.5)
    bottle = (0.30, 0.20, 0.08, 1.0)
    for k, (bx, by, lying) in enumerate(((fx - 1.2, fy - 1.1, False), (fx - 1.0, fy - 1.25, True), (fx + 1.1, fy - 1.4, False),
                                         (fx + 0.9, fy - 1.6, True), (fx + 0.3, fy + 0.2, True))):
        if lying:
            make_cyl(f"Bonfire_Bottle_{k}", (bx, by, 0.065), 0.032, 0.22, bottle, axis='X', segments=8)
        else:
            make_cyl(f"Bonfire_Bottle_{k}", (bx, by, 0.15), 0.032, 0.22, bottle, segments=8)
            make_cyl(f"Bonfire_Bottle_{k}_Neck", (bx, by, 0.30), 0.012, 0.08, bottle, segments=6)
    make_box("Bonfire_Taffy_Box", (fx - 1.7, fy - 1.0, 0.07), (0.22, 0.14, 0.08), (0.92, 0.70, 0.76, 1.0))
    make_box("Bonfire_Cooler", (fx - 2.4, fy + 0.6, 0.22), (0.56, 0.36, 0.40), (0.24, 0.42, 0.66, 1.0))
    make_box("Bonfire_Cooler_Lid", (fx - 2.4, fy + 0.6, 0.43), (0.58, 0.38, 0.04), (0.92, 0.92, 0.88, 1.0))
    quilt = ((0.70, 0.30, 0.28, 1.0), (0.86, 0.74, 0.40, 1.0), (0.30, 0.44, 0.60, 1.0), (0.40, 0.56, 0.34, 1.0))
    for i in range(4):
        for j in range(3):
            make_box(f"Bonfire_Quilt_{i}{j}", (fx - 0.9 + i * 0.45, fy + 1.6 + j * 0.45, 0.035), (0.44, 0.44, 0.01), quilt[(i + j) % 4])
    # down the beach, both ways: campfires and bonfires along the dry sand
    for side in (-1, 1):
        for k, d in enumerate((14.0, 26.0, 41.0, 60.0, 84.0, 114.0, 150.0, 195.0)):
            x = fx + side * d
            y = 6.4 + ((k * 7 + (side > 0)) % 3) * 0.5
            s = 0.6 if k % 3 else 1.0
            make_blob(f"Bonfire_Far_{'E' if side > 0 else 'W'}_{k}_Glow", (x, y, 0.30 * s), 0.34 * s, ember, noise=0.3, seed=k, squash=1.5)
            make_blob(f"Bonfire_Far_{'E' if side > 0 else 'W'}_{k}_Glow_Top", (x, y, 0.62 * s), 0.18 * s, flame, noise=0.3, seed=k + 3, squash=1.8)


def main():
    clear_scene()
    build_sand()
    build_sea()
    build_sky()
    build_foreground()
    build_grunion()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/grunion_beach.glb"))
    print(f"\n[build_grunion_beach] exporting to {out}")
    build_horizon_2026_08()
    build_shore_2026_09()
    build_bonfires_2026_10()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT: view stopped at 50m. Night sea to a true horizon
    seaward; dune ridges and a distant point light landward."""
    # GROUND under everything out past the last band (2026-08-09,
    # user: "no ground on any of the roads — a flat expanse of
    # nothing"). Locale-colored so exteriors stop sharing a void.
    # landward only (2026-09-30: under the sea too, it showed as a sand
    # strip past the last sea band on the horizon)
    make_box("Ground_Far", (0.0, -270.0, -0.03), (1080.0, 540.0, 0.02),
             (0.30, 0.28, 0.24, 1.0))
    make_box("Sea_Deep", (0.0, 90.0, 0.3), (600.0, 62.0, 0.05), COL_SEA_FAR)
    make_box("Sea_Mid", (0.0, 167.5, 0.25), (900.0, 93.0, 0.05), COL_SEA_FAR)
    make_box("Sea_Horizon", (0.0, 560.0, 0.2), (1200.0, 700.0, 0.05),
             (COL_SEA_FAR[0] * 1.3, COL_SEA_FAR[1] * 1.3,
              COL_SEA_FAR[2] * 1.25, 1.0))
    from _props.detail import make_far_bands
    make_far_bands("FarDune", (0.24, 0.23, 0.20),
                   [(70.0, 80.0, 5.0, 0.85), (150.0, 130.0, 7.0, 0.65),
                    (300.0, 230.0, 9.0, 0.48)], sides="S",
                   profile="ridge")


def build_shore_2026_09():
    """Draft 2 (2026-09-30) — the 09-26 sheet: both vantages read as a
    dark sea under three black bars. The bars were the cloud cards 24 m
    out; the beach was 36 m wide, so the tide-edge vantage looking
    west along the wet band saw the sand, the gleam and the surf lines
    END, and a dune ridge standing in the western sea. Draft 2:
      · THE BEACH RUNS OUT OF FRAME — sand, wet band, gleam, surf and
        sea are 400+ m long; the far dunes are landward only;
      · A CLOUD DECK — lumpy flattened masses 140-200 m out, 20-40 m
        up, fogged into the sky, with a GAP where the moon is: a pale
        disc behind it and the Hidden_Moon light moved up there to
        catch the edges (the .tscn);
      · THE WALK DOWN — "I walked down to the water's edge": a line of
        footprints from the dune through the dry sand to the wet band,
        the one thing that says someone is here;
      · THE WRACK LINE — a ragged dark line of kelp and drift at the
        high-tide mark, more driftwood at the dune foot (a Pacific
        beach piles its logs there).
    NEXT (draft 3): the surf as broken water (the lines are three flat
    strips); a heightfield dune with the grass on it; wet-sand
    reflection of the moon gap (a pale smear on the wet band under
    it); the grunion run bigger and brighter at the tide-edge vantage
    (the run is the vol2 interlude's whole subject)."""
    # the cloud deck — (x, y, z, radius, squash, seed)
    deck = [(-150.0, 150.0, 30.0, 34.0, 0.26, 11), (-95.0, 175.0, 34.0, 30.0, 0.24, 12),
            (-45.0, 160.0, 27.0, 28.0, 0.28, 13), (-8.0, 190.0, 36.0, 26.0, 0.22, 14),
            (62.0, 165.0, 30.0, 30.0, 0.26, 15), (110.0, 185.0, 36.0, 32.0, 0.22, 16),
            (160.0, 150.0, 28.0, 34.0, 0.26, 17), (20.0, 205.0, 46.0, 24.0, 0.20, 18),
            (-120.0, 215.0, 48.0, 30.0, 0.20, 19)]
    for i, (x, y, z, r, sq, sd) in enumerate(deck):
        make_blob("Cloud_Deck_%d" % i, (x, y, z), r, COL_CLOUD, noise=0.30, seed=sd, rings=5, segments=12, squash=sq)
    # the moon behind the gap between decks 3 and 4 (x 8..36)
    make_blob("Moon_Disc", (26.0, 240.0, 38.0), 5.0, (0.70, 0.72, 0.78, 1.0), noise=0.02, seed=3, rings=6, segments=12, squash=1.0)
    make_blob("Moon_Glow_Halo", (26.0, 242.0, 38.0), 11.0, COL_MOONGLOW, noise=0.10, seed=4, rings=5, segments=12, squash=0.8)
    # (draft 3) the moon gap's smear on the wet band: what light there is,
    # "caught up in water" — pale, broken, under where the moon hides
    for k, (sx, sw) in enumerate(((0.6, 1.4), (1.4, 0.9), (2.0, 0.6), (0.1, 0.5))):
        make_box(f"Moon_Smear_{k}", (sx, 8.95 + 0.20 * k, 0.037), (sw, 0.16, 0.004), (0.50, 0.53, 0.60, 1.0))
    # the walk down: left-right pairs from the dune to the wet band
    FOOT = (0.17, 0.16, 0.14, 1.0)       # (draft 3) each print a shadow in the paler sand
    for k in range(14):
        t = k / 13.0
        fx = -0.9 + 0.55 * t + (0.13 if k % 2 else -0.13)
        fy = 0.4 + t * 7.9
        if (fx + 1.0) ** 2 + (fy - 5.0) ** 2 < 0.9 ** 2:
            continue                     # (the bonfire burns on this stretch of the walk now)
        make_box("Footprint_%d" % k, (fx, fy, 0.031), (0.11, 0.26, 0.004), FOOT)
    # the wrack line at the high-tide mark (y 7.3-7.8), ragged
    WRACK = (0.14, 0.15, 0.11, 1.0)
    for i in range(40):
        wx = -60.0 + i * 3.1 + 0.9 * ((i * 7) % 3)
        wy = 7.4 + 0.18 * ((i * 5) % 4)
        make_box("Wrack_%d" % i, (wx, wy, 0.034), (1.2 + 0.4 * (i % 3), 0.22, 0.012), WRACK)
    # driftwood piled at the dune foot
    # clear of the dune's toe (y 0.2) and the grass clumps (2026-09-30)
    for i, (dx, dy, ln, rad, rot_axis) in enumerate([(-10.0, 0.6, 5.2, 0.28, "X"), (-14.5, 1.0, 3.4, 0.18, "X"),
                                                     (4.5, 0.6, 4.6, 0.24, "X"), (6.8, 0.45, 2.6, 0.16, "X"),
                                                     (12.0, 0.7, 6.0, 0.30, "X"), (-20.0, 0.6, 3.8, 0.22, "X")]):
        make_cyl("Driftwood_Pile_%d" % i, (dx, dy, rad), rad, ln, COL_DRIFT, segments=8, axis=rot_axis)


if __name__ == "__main__":
    main()
