"""cabin_road — the road to Tem's cabin, Oregon coast (vol7's ~20
road scenes, split off louisiana_road 2026-08-03: the prose is "the
switchbacks above the third creek crossing where the asphalt gave
out and the gravel started," Sitka stands, alders, cedars — nothing
a Louisiana swamp road can play).

Hero features: the asphalt-to-gravel transition line, the creek
crossing (culvert pipe under the roadbed, water band, mossed
stones), the switchback bend climbing away right, dense Sitka
spruce + cedar walls with alder lightening the lower story, the
clearing gap ahead where the cabin's smoke would hang, roadside
ferns, a leaning mile marker, coastal mist.

Coordinate frame: Blender Z-up. y=0 south (camera, downhill end);
+Y climbs north: asphalt → transition (y≈6) → gravel → creek
crossing (y≈10) → switchback bend (y≈15, road curves east) →
treewall/clearing gap. Grade suggested by raising the far roadbed.
glTF export remaps to Godot (x, z, -y).

Vantage wired in Background3D.CAMERA_PRESETS:
  cabin_road — on the asphalt looking N up the climb: transition
  line, creek, the bend, the Sitka walls.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path: sys.path.insert(0, _BT)
from _props.geometry import clear_scene, make_box, make_cyl, export_glb

COL_ASPHALT = (0.24, 0.24, 0.25, 1.0)   # wet coastal asphalt
COL_GRAVEL = (0.52, 0.48, 0.42, 1.0)
COL_GRAVEL_DK = (0.44, 0.40, 0.35, 1.0)
COL_SHOULDER = (0.36, 0.34, 0.28, 1.0)
COL_FERN = (0.24, 0.40, 0.24, 1.0)
COL_MOSS = (0.28, 0.42, 0.24, 1.0)
COL_SITKA = (0.12, 0.22, 0.16, 1.0)     # dense dark conifer
COL_SITKA_LT = (0.16, 0.28, 0.19, 1.0)
COL_CEDAR = (0.18, 0.30, 0.18, 1.0)
COL_ALDER = (0.38, 0.48, 0.30, 1.0)     # lighter lower story
COL_TRUNK = (0.30, 0.24, 0.18, 1.0)
COL_ALDER_BARK = (0.62, 0.62, 0.58, 1.0)
COL_CREEK = (0.30, 0.38, 0.40, 1.0)
COL_CREEK_FOAM = (0.72, 0.76, 0.76, 1.0)
COL_CULVERT = (0.46, 0.46, 0.44, 1.0)
COL_MIST = (0.72, 0.76, 0.76, 0.35)
COL_SKY = (0.66, 0.70, 0.70, 1.0)       # coastal gray-bright


def build_road():
    # GROUND (2026-08-09): full forest-floor plane under everything —
    # the road used to float in a void past the tree trunks. Oregon
    # duff: dark red-brown, unlike louisiana's green swamp floor.
    make_box("Forest_Floor", (0.0, 60.0, -0.012), (300.0, 420.0, 0.02),
             (0.16, 0.13, 0.10, 1.0))
    # Asphalt approach runs BEHIND the camera too — the road arrives
    # from somewhere (was a 6m stub starting at the lens).
    make_box("Asphalt", (0.0, -27.0, 0.0), (4.6, 66.0, 0.06), COL_ASPHALT)
    make_box("Asphalt_Patch", (0.6, 4.6, 0.035), (1.2, 0.9, 0.02), (0.20, 0.20, 0.21, 1.0))
    # THE TRANSITION — where the asphalt gives out
    make_box("Transition_Lip", (0.0, 6.05, 0.045), (4.6, 0.25, 0.03), COL_GRAVEL_DK)
    # Gravel climbing away, rising with the grade
    make_box("Gravel_0", (0.0, 8.0, 0.10), (4.4, 4.0, 0.08), COL_GRAVEL)
    make_box("Gravel_1", (0.4, 12.0, 0.30), (4.2, 4.0, 0.08), COL_GRAVEL)
    # The switchback: the bend swings east and up
    make_box("Gravel_Bend", (2.6, 15.5, 0.55), (5.0, 3.4, 0.08), COL_GRAVEL_DK)
    make_box("Gravel_Upper", (5.4, 17.5, 0.95), (4.4, 3.0, 0.08), COL_GRAVEL)
    # Soft shoulders
    for sx in (-2.6, 2.6):
        make_box(f"Shoulder_{sx:+.1f}", (sx, 5.0, 0.02), (0.8, 10.0, 0.05), COL_SHOULDER)


def build_creek():
    """The creek crossing at y≈10: water band under the roadbed,
    culvert mouths both sides, mossed stones."""
    make_box("Creek_W", (-5.5, 10.0, 0.02), (6.5, 1.6, 0.05), COL_CREEK)
    make_box("Creek_E", (5.5, 10.0, 0.02), (6.5, 1.6, 0.05), COL_CREEK)
    make_box("Creek_Foam_W", (-3.1, 10.0, 0.06), (1.2, 0.5, 0.02), COL_CREEK_FOAM)
    make_box("Creek_Foam_E", (2.9, 10.2, 0.06), (1.0, 0.4, 0.02), COL_CREEK_FOAM)
    for sgn in (-1, 1):
        make_cyl(f"Culvert_{sgn:+d}", (sgn * 2.5, 10.0, 0.14), 0.30, 0.6, COL_CULVERT,
                 segments=10, axis='X')
    stones = [(-3.6, 9.4, 0.30), (-4.8, 10.5, 0.42), (3.4, 9.6, 0.34), (4.6, 10.6, 0.28)]
    for i, (px, py, s) in enumerate(stones):
        make_box(f"Creek_Stone_{i}", (px, py, s / 2.0), (s * 1.6, s * 1.2, s), (0.44, 0.44, 0.42, 1.0))
        make_box(f"Creek_Stone_{i}_Moss", (px, py, s + 0.02), (s * 1.2, s * 0.9, 0.05), COL_MOSS)


def _conifer(prefix, px, py, h, col):
    # 2026-08-04: was three stacked CUBES on a pole — a Minecraft
    # tree on the game's Oregon road. Now a real spruce silhouette
    # (tapered trunk + stacked cones) from _props.trees.
    from _props.trees import make_conifer
    make_conifer(prefix, px, py, h, col, COL_TRUNK)


def build_forest():
    """The Sitka stand: tall dark walls both sides, cedar mixed in,
    alder lightening the road edge, ferns at the shoulders."""
    west = [(-4.5, 2.0, 7.5), (-5.5, 5.5, 9.0), (-4.8, 8.0, 8.0), (-5.8, 12.0, 9.5),
            (-4.6, 15.0, 8.5), (-6.5, 18.0, 10.0), (-7.5, 8.5, 9.0), (-8.0, 14.0, 10.0)]
    east = [(4.6, 1.5, 8.0), (5.6, 4.5, 9.5), (4.9, 7.5, 8.5), (6.0, 12.5, 9.0),
            (7.5, 9.0, 10.0), (8.2, 15.5, 9.5), (7.0, 20.0, 10.5), (2.2, 19.5, 9.0)]
    for i, (px, py, h) in enumerate(west):
        _conifer(f"SitkaW_{i}", px, py, h, COL_SITKA if i % 3 else COL_CEDAR)
    for i, (px, py, h) in enumerate(east):
        _conifer(f"SitkaE_{i}", px, py, h, COL_SITKA_LT if i % 3 else COL_SITKA)
    # Alders at the road edge: pale trunks, light crowns
    for i, (px, py) in enumerate([(-3.2, 4.0), (3.3, 6.5), (-3.4, 13.0), (3.0, 12.0)]):
        # 2026-08-04: alder crowns were cylinders (the sitkas got
        # real silhouettes earlier the same day; these were missed in
        # the same file). Broadleaf now — pale trunk kept via look.
        from _props.trees import make_broadleaf
        make_broadleaf(f"Alder_{i}", px, py, 4.4, COL_ALDER,
                       COL_ALDER_BARK, crown=0.30)
    # Ferns along the shoulders
    ferns = [(-2.9, 1.5), (2.9, 3.0), (-3.0, 7.2), (3.1, 8.6), (-3.2, 11.5), (2.8, 14.0)]
    for i, (px, py) in enumerate(ferns):
        for b in range(4):
            make_box(f"Fern_{i}_{b}", (px + 0.10 * ((b * 3) % 3 - 1), py + 0.08 * (b % 2),
                     0.18 + 0.04 * b), (0.34 - 0.06 * b, 0.05, 0.05), COL_FERN)
    # Leaning mile marker at the transition
    make_box("Mile_Marker", (-2.65, 6.0, 0.50), (0.08, 0.08, 1.00), (0.86, 0.86, 0.82, 1.0))
    make_box("Mile_Marker_Band", (-2.65, 6.0, 0.85), (0.09, 0.09, 0.12), (0.26, 0.44, 0.30, 1.0))


def build_atmosphere():
    """Coastal mist hanging in the stand + the clearing gap ahead."""
    make_box("Mist_Low", (0.0, 14.0, 1.6), (12.0, 3.0, 1.6), COL_MIST)
    make_box("Mist_High", (2.0, 18.0, 3.4), (10.0, 2.5, 2.0), COL_MIST)
    # The clearing gap — a lighter break in the treewall where the
    # road disappears toward the cabin
    make_box("Clearing_Glow", (4.5, 21.5, 2.6), (3.4, 0.3, 5.0), (0.78, 0.80, 0.74, 1.0))
    # (Sky wall deleted 2026-08-04 — it stood between the camera
    # and the new far bands, occluding the horizon it faked.
    # The sky is the .tscn environment's job.)


def build_drones_2026_08():
    """ONEIRONAUTICS WORK-DRONES (user 2026-08-12: "the drones in
    land of milk and honey factor in heavily").

    Canon this stages: "The drones came in off the bluff in the last
    hour before dawn" (ch2) and "The salal had been pruned back from
    the trail edges; the cuts were fresh. The foundation's drones
    had been..." (ch12). So the road shows BOTH — the machines
    themselves in the air over the stand, and the evidence of their
    work along the shoulder, which is the part a walker notices.
    """
    from _props.drones import make_drone_flight, make_drone

    # A skein coming in over the stand, off the bluff (west), holding
    # north up the climb. High and small: three amber eyes above the
    # treeline, the way Lena registers them — always somewhere.
    make_drone_flight("Drone_Skein", -6.0, 26.0, 13.5, n=3,
                      spread=11.0, climb=2.2)
    # One working low over the shoulder brush, arm deployed — this is
    # the one the player can actually read as a machine.
    make_drone("Drone_Worker", 5.6, 12.5, 4.2, arm_down=True)

    # THE EVIDENCE: fresh-cut salal stubs where the drones pruned the
    # trail edge back. Pale cut faces against the dark leaf mass —
    # tiny, but it is the detail the prose actually describes.
    for i, (sx, sy) in enumerate(((3.05, 6.0), (3.15, 8.4), (3.0, 10.9),
                                  (-3.05, 7.2), (-3.15, 12.9),
                                  (-3.0, 15.4))):
        make_box(f"SalalCut_{i}_Mass", (sx, sy, 0.34),
                 (0.55, 0.85, 0.68), COL_FERN)
        # the sheared plane, lighter — a fresh cut reads as a highlight
        make_box(f"SalalCut_{i}_Face", (sx, sy, 0.685),
                 (0.52, 0.80, 0.02), (0.52, 0.60, 0.38, 1.0))
        make_box(f"SalalCut_{i}_Trim", (sx + (0.30 if sx > 0 else -0.30),
                                        sy - 0.25, 0.09),
                 (0.34, 0.40, 0.14), (0.34, 0.42, 0.26, 1.0))


def main():
    clear_scene()
    build_road()
    build_creek()
    build_forest()
    build_atmosphere()
    build_drones_2026_08()
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/cabin_road.glb"))
    print(f"\n[build_cabin_road] exporting to {out}")
    build_horizon_2026_08()
    export_glb(out)



def build_horizon_2026_08():
    """STUMP HUNT (locale_geometry_audit): view stopped at 22m. The
    Oregon coast road now runs into receding Sitka ridgelines on
    every side until the marine fog takes them."""
    from _props.detail import make_far_bands
    make_far_bands("FarSitka", COL_SITKA,
                   [(60.0, 70.0, 7.0, 0.90), (130.0, 120.0, 9.0, 0.74),
                    (260.0, 200.0, 12.0, 0.58), (450.0, 320.0, 15.0, 0.44),
                    (760.0, 480.0, 18.0, 0.34)], profile="treeline")


if __name__ == "__main__":
    main()
