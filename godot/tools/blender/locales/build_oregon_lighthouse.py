"""oregon_lighthouse — vol 2's lighthouse on the Pacific, an hour and a
half from Small Wood, December, night (draft 1, 2026-10-18).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Not the bayou lighthouse (vol 5's Louisiana) and not any real named light.
  the trail up from the bed and breakfast, the "coastal geological strata"
  the lighthouse "surrounded by barbed gate, padlocked and rising high"
  "the bricked foundation walkway"
  the tower: "Slim and narrow, damp and noisy", "the stone masonry
   surrounding, the light twinkling up above shot out of floorboard and
   crevasse"                        → the hollow stone column, its wooden
                                      floors with light through the gaps
  the beacon "its glass eye", kept running "with diesel burning generating
   machines"                        → the lantern room, the generator shed
  the surf "pounding" below, the wind whistling in the cracks
Night: the dark takes the structure; the beacon and the light through the
boards are what you see.

Blender: x east, y north, z up; Godot (x, z, -y). The tower stands at the
origin on the headland; the sea is west and below.

DRAFT 2 targets: the bed and breakfast and its botanical garden; the gate
as its own view (a new stem); the family's flashlight beams as spots;
Deck framing.
"""
import os, sys, math
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import (clear_scene, make_box, make_cyl, make_blob, make_rot_box, make_lathe, make_taper_cyl,
                             join_stock, export_glb)

STONE = (0.56, 0.54, 0.50, 1.0); STONE_DARK = (0.40, 0.38, 0.36, 1.0)
BRICK = (0.50, 0.28, 0.22, 1.0)
WOOD = (0.36, 0.28, 0.20, 1.0)
R_IN, R_OUT, TH = 1.9, 2.4, 18.0       # the column's bore, its outside, its height
FLOORS = (6.0, 12.0)


def build_tower():
    # the column: a ring of stone courses round the bore, the doorway S
    n = 20
    for k in range(n):
        a0 = k * 2.0 * math.pi / n
        am = a0 + math.pi / n
        if abs(math.atan2(math.sin(am + math.pi / 2.0), math.cos(am + math.pi / 2.0))) < 0.25:
            # the doorway (S): only the courses above the lintel
            r = (R_IN + R_OUT) / 2.0
            make_rot_box(f"Column_Over_Door_{k}", (r * math.cos(am), r * math.sin(am), (2.2 + TH) / 2.0),
                         (R_OUT - R_IN, 2.0 * r * math.sin(math.pi / n) + 0.02, TH - 2.2), STONE, yaw=am)
            continue
        r = (R_IN + R_OUT) / 2.0
        make_rot_box(f"Column_Wall_{k}", (r * math.cos(am), r * math.sin(am), TH / 2.0),
                     (R_OUT - R_IN, 2.0 * r * math.sin(math.pi / n) + 0.02, TH), (STONE, STONE_DARK)[k % 2], yaw=am)
    make_cyl("Column_Base_Floor", (0.0, 0.0, 0.02), R_IN + 0.05, 0.04, (0.40, 0.38, 0.34, 1.0), segments=24)
    # the wooden floors above, their planks with gaps the light comes through
    for f, z in enumerate(FLOORS):
        for k in range(9):
            x = -R_IN + 0.25 + k * 0.43
            half = math.sqrt(max(0.0, R_IN * R_IN - x * x)) - 0.02
            if half <= 0.1:
                continue
            make_box(f"Floor_{f}_Plank_{k}", (x, 0.0, z), (0.38, 2.0 * half, 0.08), WOOD)
        make_box(f"Floor_{f}_Beam", (0.0, 0.0, z - 0.12), (2.0 * R_IN - 0.04, 0.16, 0.16), WOOD)
        # the light between the boards (bright slivers, lit from above)
        for k in range(8):
            x = -R_IN + 0.465 + k * 0.43
            half = math.sqrt(max(0.0, R_IN * R_IN - x * x)) - 0.02
            if half <= 0.1:
                continue
            make_box(f"Floor_{f}_Gap_Light_{k}", (x, 0.0, z + 0.05), (0.04, 2.0 * half, 0.01), (1.0, 0.94, 0.78, 1.0))
    # a stair against the wall, climbing (an iron ladder to each floor)
    for f, z in enumerate((0.0,) + FLOORS[:1]):
        for k in range(16):
            make_box(f"Ladder_{f}_Rung_{k}", (R_IN - 0.40, -0.6, z + 0.35 + k * 0.36), (0.04, 0.50, 0.03), (0.26, 0.26, 0.28, 1.0))
        for s in (-1, 1):
            make_box(f"Ladder_{f}_Rail_{s:+d}", (R_IN - 0.40, -0.6 + s * 0.25, z + 3.0), (0.04, 0.04, 6.0), (0.26, 0.26, 0.28, 1.0))
    # the top: the gallery, the lantern room's glass, the light
    make_cyl("Gallery_Deck", (0.0, 0.0, TH + 0.10), R_OUT + 0.6, 0.20, STONE_DARK, segments=24)
    for k in range(16):
        a = k * 2.0 * math.pi / 16
        make_cyl(f"Gallery_Rail_Post_{k}", ((R_OUT + 0.5) * math.cos(a), (R_OUT + 0.5) * math.sin(a), TH + 0.70), 0.03, 1.0,
                 (0.16, 0.16, 0.18, 1.0), segments=6)
    make_cyl("Lantern_Glass", (0.0, 0.0, TH + 1.40), 1.5, 2.4, (0.86, 0.84, 0.70, 1.0), segments=16)
    make_cyl("Lantern_Lens", (0.0, 0.0, TH + 1.40), 0.6, 1.2, (1.0, 0.96, 0.80, 1.0), segments=16)
    make_lathe("Lantern_Roof", (0.0, 0.0, TH + 2.60), [(0.0, 1.2), (1.7, 0.0), (1.6, -0.05), (0.0, 1.1)], (0.14, 0.14, 0.16, 1.0), segments=16)


def build_grounds():
    # the headland, the brick walkway to the door, the barbed gate, the trail
    make_cyl("Headland_Ground", (0.0, 0.0, -0.20), 26.0, 0.40, (0.30, 0.34, 0.24, 1.0), segments=24)
    make_box("Headland_Cliff", (-24.0, 0.0, -12.0), (8.0, 70.0, 24.0), (0.32, 0.30, 0.28, 1.0))
    for k in range(6):
        make_box(f"Cliff_Strata_{k}", (-20.05, 0.0, -2.0 - k * 3.4), (0.10, 70.0, 0.40), ((0.48, 0.42, 0.34, 1.0), (0.36, 0.32, 0.28, 1.0))[k % 2])
    make_box("Walkway_Bricks", (0.0, -R_OUT - 3.0, 0.04), (1.6, 6.0, 0.08), BRICK)
    for k in range(10):
        make_box(f"Walkway_Seam_{k}", (0.0, -R_OUT - 0.4 - k * 0.6, 0.082), (1.6, 0.02, 0.004), (0.36, 0.20, 0.16, 1.0))
    gy = -R_OUT - 6.2
    POST = (0.30, 0.30, 0.32, 1.0)
    MESH = (0.46, 0.48, 0.50, 0.30)       # chain-link: a see-through skin, not a wall (2026-10-23)
    WIRE = (0.50, 0.50, 0.52, 1.0)
    for s in (-1, 1):
        make_cyl(f"Gate_Post_{s:+d}", (s * 1.1, gy, 1.40), 0.06, 2.80, POST, segments=8)
        # "barbed gate, padlocked and rising high": line posts every 2.4 m, a
        # top rail, the mesh between, three barbed strands over the rail
        make_box(f"Fence_Mesh_{s:+d}", (s * 7.1, gy, 1.19), (12.0, 0.02, 2.36), MESH)
        make_box(f"Fence_Rail_Top_{s:+d}", (s * 7.1, gy, 2.39), (12.0, 0.04, 0.04), POST)
        for k in range(5):
            make_cyl(f"Fence_Post_{s:+d}_{k}", (s * (3.5 + k * 2.4), gy, 1.20), 0.04, 2.40, POST, segments=8)
        for k in range(3):
            make_box(f"Fence_Barbed_{s:+d}_{k}", (s * 7.1, gy, 2.50 + k * 0.14), (12.0, 0.02, 0.02), WIRE)
    make_rot_box("Gate_Leaf_Open", (1.1 + 0.05, gy - 1.0, 1.2), (0.04, 2.0, 2.2), MESH, yaw=0.0)
    for nm, z in (("Top", 2.32), ("Bot", 0.08)):
        make_box(f"Gate_Leaf_Rail_{nm}", (1.15, gy - 1.0, z), (0.04, 2.0, 0.04), POST)
    make_box("Gate_Padlock", (1.15, gy - 1.95, 1.1), (0.06, 0.04, 0.08), (0.70, 0.62, 0.36, 1.0))
    make_box("Trail", (0.0, gy - 12.0, 0.01), (1.4, 24.0, 0.02), (0.44, 0.38, 0.30, 1.0))
    for k in range(12):
        make_blob(f"Trail_Brush_{k}", ((-1.8 if k % 2 else 1.8) + (k % 3) * 0.3, gy - 2.0 - k * 2.0, 0.3), 0.6,
                  (0.24, 0.30, 0.20, 1.0), noise=0.35, seed=k)
    # the generator shed by the tower
    make_box("Generator_Shed", (5.0, 2.0, 1.2), (3.0, 2.4, 2.4), (0.44, 0.42, 0.40, 1.0))
    make_box("Generator_Shed_Door", (3.48, 2.0, 1.0), (0.04, 0.9, 2.0), (0.30, 0.30, 0.32, 1.0))
    make_cyl("Generator_Exhaust", (5.6, 2.6, 2.8), 0.08, 1.2, (0.30, 0.30, 0.32, 1.0), segments=8)
    # the sea below, west, and the night
    make_box("Night_Sea_Water", (-90.0, 0.0, -18.0), (140.0, 200.0, 0.04), (0.04, 0.06, 0.08, 1.0))
    for k in range(8):
        make_blob(f"Surf_Rock_{k}", (-29.0 - (k % 3) * 2.0, -24.0 + k * 6.0, -17.0), 1.6, (0.20, 0.20, 0.20, 1.0), noise=0.4, seed=30 + k)
    make_box("Night_Sky", (-130.0, 0.0, 20.0), (0.2, 300.0, 90.0), (0.02, 0.03, 0.06, 1.0))


def build_gate_night_2026_10():
    """DRAFT 2 (2026-10-30), the gate view: the tower read as one dark
    pipe, the headland as a flat disc. Now:
    - the stone in COURSES: a darker joint ring every 0.9 m (joined mesh)
    - "the light twinkling up above shot out of floorboard and crevasse":
      slit windows up the S face, warm with the lit floors behind them
    - the door in the doorway, plank and strap, ajar on its keys' night
    - grass and heather in tussocks on the headland, rocks along the fence
    (the beams are SpotLights in the .tscn: the family's flashlights)
    Draft 3 targets: breath vapor in the beams, the bed and breakfast's
    lights down the trail, the gallery rail's ring, the sea's surf line."""
    JOINT = (0.30, 0.29, 0.27, 1.0)
    n = 20
    for c in range(1, 20):
        z = c * 0.9
        for k in range(n):
            am = k * 2.0 * math.pi / n + math.pi / n
            if z < 2.25 and abs(math.atan2(math.sin(am + math.pi / 2.0), math.cos(am + math.pi / 2.0))) < 0.25:
                continue                                   # the doorway
            r = R_OUT + 0.006
            make_rot_box(f"Column_Joint_Stock_{c}_{k}", (r * math.cos(am), r * math.sin(am), z),
                         (0.012, 2.0 * r * math.sin(math.pi / n) + 0.02, 0.05), JOINT, yaw=am)
    for i, z in enumerate((3.4, 7.2, 10.6, 13.4)):
        a = -math.pi / 2.0 + (0.55 if i % 2 else -0.55)
        x, y = (R_OUT + 0.01) * math.cos(a), (R_OUT + 0.01) * math.sin(a)
        make_rot_box(f"Tower_Slit_{i}_Frame", (x, y, z), (0.04, 0.38, 0.86), (0.22, 0.21, 0.20, 1.0), yaw=a)
        x2, y2 = (R_OUT + 0.03) * math.cos(a), (R_OUT + 0.03) * math.sin(a)
        make_rot_box(f"Tower_Slit_{i}_Glow", (x2, y2, z), (0.02, 0.24, 0.70), (1.0, 0.84, 0.56, 1.0), yaw=a)
    # the door, ajar into the bore
    make_rot_box("Tower_Door", (0.32, -R_IN - 0.05, 1.05), (0.95, 0.08, 2.10), (0.30, 0.22, 0.16, 1.0), yaw=0.35)
    for i, z in enumerate((0.4, 1.7)):
        make_rot_box(f"Tower_Door_Strap_{i}", (0.30, -R_IN - 0.10, z), (0.90, 0.02, 0.06), (0.16, 0.16, 0.18, 1.0), yaw=0.35)
    make_box("Tower_Door_Lintel", (0.0, -R_OUT + 0.10, 2.28), (1.30, 0.30, 0.16), STONE_DARK)
    # tussocks of grass and heather on the headland, rocks by the fence
    gy = -R_OUT - 6.2
    for k in range(70):
        x = -14.0 + ((k * 37) % 280) / 10.0
        y = gy + 4.6 - ((k * 53) % 150) / 10.0
        if abs(x) < 1.3 or (abs(x) < 1.0 and y > gy):
            continue                                       # the trail and the walkway
        if abs(y - gy) < 0.35:
            continue                                       # the fence line itself
        r = 0.16 + 0.05 * (k % 4)
        col = ((0.26, 0.32, 0.20, 1.0), (0.34, 0.36, 0.24, 1.0), (0.30, 0.24, 0.28, 1.0))[k % 3]
        make_blob(f"Headland_Tuft_Stock_{k}", (x, y, r * 0.35), r, col, noise=0.4, seed=100 + k, squash=0.7)
    for k in range(8):
        x = (-1 if k % 2 else 1) * (2.0 + k * 1.3)
        make_blob(f"Fence_Rock_{k}", (x, gy - 0.6 - (k % 3) * 0.3, 0.12), 0.30 + 0.06 * (k % 3), (0.34, 0.33, 0.31, 1.0),
                  noise=0.35, seed=140 + k, squash=0.6)


def main():
    clear_scene()
    build_tower()
    build_grounds()
    build_gate_night_2026_10()
    try:
        join_stock()
    except Exception as _e:
        print("[join_stock] skipped:", _e)
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "../../../assets/3d/locales/oregon_lighthouse.glb"))
    print(f"\n[build_oregon_lighthouse] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
