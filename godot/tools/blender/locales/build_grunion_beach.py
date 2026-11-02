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
from _props.geometry import clear_scene, make_box, make_cyl, make_blob, make_rot_box, make_prism, make_chamfer_box, export_glb

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


def _shore(x):
    """The shoreline's wander (m, across the beach) along it: the swash
    reaches further up in some places than others."""
    return 0.35 * math.sin(x / 7.0) + 0.18 * math.sin(x / 2.9 + 1.3)


def _shore_slope(x):
    return 0.35 / 7.0 * math.cos(x / 7.0) + 0.18 / 2.9 * math.cos(x / 2.9 + 1.3)


def build_sand():
    make_box("Sand_Dry", (0.0, 4.0, 0.0), (420.0, 8.0, 0.06), COL_SAND)
    make_box("Sand_Wet", (0.0, 9.0, 0.01), (420.0, 2.2, 0.05), COL_SAND_WET)
    # The gleam: "water that gleamed off the fresh tide's edge". (2026-11-01)
    # One ruled 420 m stripe read, from the low lens looking along the
    # shore, as a lane line on a highway. The strip under it keeps the wet
    # sand's tone (it fills the edge, it does not draw it); the gleam is
    # the swash's lobes on top, wandering with the shoreline.
    make_box("Tide_Gleam", (0.0, 10.05, 0.03), (420.0, 0.5, 0.02), (0.30, 0.31, 0.33, 1.0))
    x, k = -208.0, 0
    while x < 208.0:
        ln = 2.4 + 1.6 * abs(math.sin(x * 0.37))
        xc = x + ln / 2.0
        yaw = math.atan(_shore_slope(xc))
        make_rot_box(f"Tide_Gleam_Lobe_{k}", (xc, 9.95 + 0.35 * _shore(xc), 0.0405), (ln, 0.18 + 0.12 * abs(math.sin(x * 0.9)), 0.004), COL_GLEAM, yaw=yaw)
        x += ln + 0.5 + 0.9 * abs(math.cos(x * 0.53))
        k += 1
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
            # (2026-11-01) along the shore's wander, each run turned to it,
            # so the lines stop converging like a highway's
            xc = x + ln / 2.0
            make_rot_box(f"Surf_{li}_{k}", (xc, ly + (0.5 - 0.05 * li) * _shore(xc) + rng.uniform(-0.08, 0.08), 0.03 + 0.005 * (li == 0)),
                         (ln, w, 0.02), COL_SURF, yaw=math.atan(_shore_slope(xc)) + rng.uniform(-0.05, 0.05))
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
        # (2026-11-01, the user: "Logs look like they are exploding out
        # instead of leaning against each other stacked up") +0.55 tipped
        # each top AWAY from the fire. A teepee now: feet on the ring at
        # 0.6 m, tops meeting over the flame at 0.12 m, 1.15 m of driftwood
        make_rot_box(f"Bonfire_Log_{k}", (fx + 0.36 * math.cos(a), fy + 0.36 * math.sin(a), 0.63),
                     (0.11, 0.11, 1.15), COL_DRIFT, yaw=a, pitch=-0.42)
    # the fire inside the stack, its tip up through the apex
    make_blob("Bonfire_Flame_Glow_Core", (fx, fy, 0.45), 0.24, ember, noise=0.25, seed=4, squash=1.5)
    make_blob("Bonfire_Flame_Glow_Top", (fx, fy, 0.95), 0.15, flame, noise=0.3, seed=9, squash=2.0)
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


def build_philip_2026_11():
    """(2026-11-02) PHILIP'S NIGHT — vol2 ch6 ("Triptych — Philip") played on
    the ghost scene's empty view. The text: "Most of his friends were
    hippies because like them he liked to surf, smoke and screw"; "One
    summer night baked on the beach Jesus spoke to Philip"; "Philip saw the
    ocean rise up and he scrambled for his surf board. His friends slept
    through the rising surf." 30 m east of the ch10 bonfire: a campfire
    burned down to its embers in a ring of stones, the friends asleep round
    it in their bags, one blanket kicked off and empty (his), the boards
    stood on their tails between the camp and the water. Every part
    ends `__philip_beach`: no other view shows it."""
    T = "__philip_beach"
    fx, fy = 32.0, 4.0
    stone = (0.30, 0.29, 0.27, 1.0)
    char = (0.10, 0.09, 0.08, 1.0)
    for k in range(9):
        a = k * (2 * math.pi / 9) + 0.2
        make_blob(f"Philip_Fire_Stone_{k}{T}", (fx + 0.55 * math.cos(a), fy + 0.55 * math.sin(a), 0.08), 0.12, stone,
                  noise=0.3, seed=300 + k, squash=0.7)
    make_blob(f"Philip_Fire_Embers_Glow{T}", (fx, fy, 0.05), 0.38, (0.78, 0.26, 0.08, 1.0), noise=0.2, seed=310, squash=0.22)
    make_blob(f"Philip_Fire_Coal_Glow{T}", (fx + 0.05, fy - 0.04, 0.10), 0.16, (1.0, 0.50, 0.16, 1.0), noise=0.3, seed=311, squash=0.5)
    # two logs burned through and fallen across each other
    make_rot_box(f"Philip_Fire_Log_0{T}", (fx - 0.05, fy, 0.10), (0.85, 0.12, 0.12), char, yaw=0.5)
    make_rot_box(f"Philip_Fire_Log_1{T}", (fx + 0.05, fy + 0.02, 0.21), (0.75, 0.10, 0.10), char, yaw=-0.7)
    # the friends asleep in their bags, heads to the fire
    bags = (((30.4, 4.9), 0.35, (0.30, 0.34, 0.22, 1.0), (0.46, 0.32, 0.20, 1.0)),
            ((33.7, 5.0), -0.45, (0.50, 0.24, 0.14, 1.0), (0.20, 0.16, 0.12, 1.0)),
            ((33.3, 2.6), 0.75, (0.22, 0.26, 0.40, 1.0), (0.62, 0.52, 0.30, 1.0)),
            ((29.9, 3.2), -0.55, (0.40, 0.30, 0.42, 1.0), (0.28, 0.20, 0.14, 1.0)))
    for k, ((bx, by), yaw, col, hair) in enumerate(bags):
        # the bag's axis points at the fire; the head is at the fire end
        dx, dy = fx - bx, fy - by
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        ang = math.atan2(dy, dx)
        # soft: every edge cut well back, the body a second rounded hump
        make_rot_box(f"Philip_Sleeper_{k}_Bag{T}", (bx - ux * 0.35, by - uy * 0.35, 0.10), (1.85, 0.72, 0.20), col, yaw=ang)
        make_chamfer_box(f"Philip_Sleeper_{k}_Body{T}", (bx - ux * 0.50, by - uy * 0.50, 0.26), (1.20, 0.56, 0.14), col,
                         chamfer=0.07, yaw=ang + 0.04)
        make_blob(f"Philip_Sleeper_{k}_Head{T}", (bx + ux * 0.38, by + uy * 0.38, 0.28), 0.12, hair, noise=0.3, seed=320 + k, squash=0.9)
    # his blanket, kicked off and empty, the hollow where he lay
    make_rot_box(f"Philip_Blanket{T}", (31.4, 5.8, 0.02), (1.7, 1.2, 0.03), (0.62, 0.30, 0.20, 1.0), yaw=0.9)
    make_rot_box(f"Philip_Blanket_Fold{T}", (31.9, 6.2, 0.07), (0.9, 0.35, 0.07), (0.56, 0.26, 0.18, 1.0), yaw=1.2)
    # (draft 2) "Philip saw the ocean rise up": in his view only, the swell
    # stands up in three ridges of dark water, each breaking white along its
    # crest, the farthest the tallest, and the foam of the last one pushed up
    # the wet sand past the tide's edge toward the camp
    import random as _r
    rng = _r.Random(613)
    dark = (0.06, 0.08, 0.11, 1.0)
    for row, (ry, rh, base) in enumerate(((13.0, 0.55, 0.025), (15.8, 0.85, 0.025), (19.0, 1.25, 0.425))):   # on the sea slabs' tops
        x, k = 6.0, 0
        while x < 60.0:
            ln = rng.uniform(4.0, 11.0)
            xc = x + ln / 2.0
            yc = ry + 0.5 * _shore(xc) + rng.uniform(-0.15, 0.15)
            yaw = math.atan(_shore_slope(xc)) + rng.uniform(-0.04, 0.04)
            make_rot_box(f"Philip_Swell_{row}_{k}{T}", (xc, yc, base + rh / 2.0), (ln, 1.1 + 0.3 * row, rh), dark, yaw=yaw)
            make_rot_box(f"Philip_Swell_{row}_{k}_Crest{T}", (xc, yc - 0.12, base + rh + 0.02), (ln * 0.92, 0.42 + 0.1 * row, 0.10),
                         COL_SURF, yaw=yaw)
            x += ln + rng.uniform(0.3, 1.6)
            k += 1
    for k in range(7):
        fxc = 14.0 + k * 6.5 + rng.uniform(-1.0, 1.0)
        make_rot_box(f"Philip_Surge_Foam_{k}{T}", (fxc, 9.2 + 0.5 * _shore(fxc), 0.045), (5.2, 0.9, 0.02), (0.78, 0.80, 0.82, 0.85),
                     yaw=math.atan(_shore_slope(fxc)))
    # the boards stood on their tails in the dry sand, the water beyond
    board = [(-0.20, 0.0), (0.20, 0.0), (0.27, 0.6), (0.27, 1.45), (0.18, 2.0), (0.0, 2.3), (-0.18, 2.0), (-0.27, 1.45), (-0.27, 0.6)]
    for k, (bx, by, col) in enumerate(((35.2, 6.3, (0.62, 0.58, 0.50, 1.0)), (35.9, 6.0, (0.58, 0.50, 0.28, 1.0)),
                                       (36.6, 6.4, (0.26, 0.38, 0.50, 1.0)))):
        make_prism(f"Philip_Board_{k}{T}", (bx, by, 0.03), board, 0.07, col, axis="Y", yaw=0.15 * (k - 1))


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
    build_philip_2026_11()
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
    # the cloud deck (draft 3, 2026-10-30): nine dark blobs read as cut-outs
    # pasted on the sky. "The moon could not be seen behind the clouds": a
    # low continuous layer instead, two overlapping rows a shade under the
    # overcast sky (the low one down to the horizon), and a paler moonlit
    # mass over where the moon is, so the
    # light comes THROUGH cloud and the disc never shows clean.
    import random as _r
    rng = _r.Random(2402)
    n = 0
    for row, (y0, z0, r0, sq, col, step) in enumerate((
            (138.0, 11.0, 34.0, 0.17, (0.22, 0.23, 0.28, 1.0), 26.0),
            (205.0, 30.0, 46.0, 0.14, (0.24, 0.25, 0.30, 1.0), 32.0))):
        x = -290.0
        while x < 290.0:
            make_blob("Cloud_Deck_%d" % n, (x + rng.uniform(-6, 6), y0 + rng.uniform(-14, 14), z0 + rng.uniform(-3, 3)),
                      r0 * rng.uniform(0.85, 1.15), col, noise=0.26, seed=100 + n, rings=5, segments=12, squash=sq)
            x += step
            n += 1
    # (2026-10-31) the low row's underside sat ~5 m up at 138 m out, so a
    # thin strip of clear sky showed between it and the sea: a haze row
    # sitting ON the horizon closes it
    x = -290.0
    while x < 290.0:
        make_blob("Cloud_Deck_%d" % n, (x + rng.uniform(-5, 5), 172.0 + rng.uniform(-8, 8), 5.8),
                  34.0 * rng.uniform(0.9, 1.1), (0.20, 0.21, 0.26, 1.0), noise=0.18, seed=100 + n, rings=5, segments=12, squash=0.12)
        x += 24.0
        n += 1
    for m, (mx, my, mz, mr) in enumerate(((24.0, 190.0, 34.0, 30.0), (30.0, 198.0, 37.0, 22.0))):
        make_blob("Cloud_Moonlit_%d" % m, (mx, my, mz), mr, (0.30, 0.31, 0.37, 1.0), noise=0.22, seed=300 + m,
                  rings=5, segments=12, squash=0.20)
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
