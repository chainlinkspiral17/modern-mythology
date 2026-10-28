"""One-shot: the locale tscn for portland_downtown (draft 1, 2026-10-28).

Same contract as make_honolulu_highrise_tscn_2026_10_28.py. A Friday early
evening in downtown Portland: a low warm sun down the street from the west,
the blue sky fill, the globe street lamps coming on; the vacant gallery's
few fluorescent tubes that came on "non-sequentially". Lights named
`<name>__<preset>` play only in that preset. Run with plain python3.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))
I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
# travels EAST, 12 deg down: the sun going down in the west
B_SUN_FROM_W = "Transform3D(0, 0.208, -0.978, 0, 0.978, 0.208, 1, 0, 0, {}, {}, {})"
ST, GL = "__portland_street_friday", "__vacant_gallery_lobby"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


lights = [
    ("Sun" + ST, "DirectionalLight3D", B_SUN_FROM_W.format(-60, 20, -7), c(1.0, 0.78, 0.52), 1.0),
    ("SkyFill" + ST, "DirectionalLight3D", B_FILL.format(0, 20, -10), c(0.62, 0.70, 0.90), 0.45),
]
for k in range(6):
    lights.append(("Street_Lamp_%d%s" % (k, ST), "OmniLight3D", I.format(-40.0 + k * 16.0, 4.9, -2.4), c(1.0, 0.86, 0.62), 0.9, {"omni_range": 9.0}))
for k in range(4):
    lights.append(("Plaza_Lamp_%d%s" % (k, ST), "OmniLight3D", I.format(44.0 + k * 6.0, 4.4, -12.0), c(1.0, 0.86, 0.62), 0.8, {"omni_range": 8.0}))
for nm, x in (("Bookstore_Glow", -17.0), ("Record_Store_Glow", 3.0), ("Coffee_Glow", 14.0)):
    lights.append((nm + ST, "OmniLight3D", I.format(x, 2.0, -15.0), c(1.0, 0.84, 0.58), 0.8, {"omni_range": 7.0}))
# the gallery's lit tubes (blender (x0 + 2.5 + j*3, 1.8 + k*3.2) -> godot (x, z, -y))
for (k, j) in ((0, 1), (1, 3), (2, 0), (2, 2)):
    lights.append(("Gallery_Tube_Light_%d_%d%s" % (k, j, GL), "OmniLight3D", I.format(100.0 + 2.5 + j * 3.0, 2.9, -(1.8 + k * 3.2)),
                   c(0.90, 0.98, 1.0), 0.8, {"omni_range": 5.0}))
lights.append(("Gallery_Street_Spill" + GL, "OmniLight3D", I.format(104.0, 2.0, 1.5), c(1.0, 0.82, 0.56), 0.5, {"omni_range": 5.0}))

CFG = {
    # VOL 3's DOWNTOWN PORTLAND (build_portland_downtown.py): ch 4
    # invitation only — the Friday street, the pigeon plaza, the vacant gallery.
    "out_path": os.path.join(ROOT, "portland_downtown.tscn"),
    "uid": "uid://portland_downtown_v1",
    "root_node": "PortlandDowntown",
    "glb": "res://assets/3d/locales/portland_downtown.glb",
    "env": {"bg": (0.52, 0.60, 0.78, 1), "amb": (0.70, 0.70, 0.76, 1),
            "amb_e": 0.62, "fog": (0.72, 0.66, 0.66, 1), "fog_e": 0.35,
            "fog_d": 0.004, "sat": 0.98, "glow_i": 0.8, "glow_b": 0.14},
    "shader": {"warm": (0.98, 0.86, 0.70, 1), "bg": (0.08, 0.08, 0.08, 1),
               "neon_edge": (0.80, 0.70, 0.56, 1), "neon_lo": (0.28, 0.24, 0.22, 1),
               "neon_hi": (0.08, 0.08, 0.08, 1), "lim_tint": (0.72, 0.66, 0.58, 1)},
    "lights": lights,
    "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
}

MARKERS = [
    ("shot_insert_pigeons", (46.5, 2.6, 0.5), (-0.3063, -0.6055), 52.0,
     "\"a pigeon occupied park plaza\"; \"The whole flock lifts an inch off the stones and settles again where it was.\""),
    ("shot_insert_records", (3.0, 1.6, -9.0), (0.0, 0.0), 40.0,
     "\"window drop shopping independent record stores\""),
    ("shot_insert_trashcan__vacant_gallery_lobby", (102.4, 1.5, -5.9), (0.0, 0.0), 38.0,
     "\"a table with refreshments set up along one wall, a trashcan filled with ice and cans of beer\""),
]


def main():
    path = write_locale_tscn(CFG)
    blk = []
    for nm, pos, rot, fov, why in MARKERS:
        blk += ["", "; " + why,
                '[node name="%s" type="Marker3D" parent="." groups=["vn_shot"]]' % nm,
                "position = Vector3(%.3f, %.3f, %.3f)" % pos,
                "rotation = Vector3(%.4f, %.4f, 0.0)" % rot,
                "metadata/fov = %.1f" % fov]
    with open(path, "a") as f:
        f.write("\n".join(blk) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
