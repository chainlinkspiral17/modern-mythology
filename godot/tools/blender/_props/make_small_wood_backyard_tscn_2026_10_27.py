"""One-shot: the locale tscn for small_wood_backyard (draft 1, 2026-10-27).

Same contract as make_vol1_4_tscns_2026_10_17.py. The scene's own
environment is the backyard on a bright overcast coast-summer afternoon. Lights named `<name>__<preset>[__<preset>]` play
only in those presets. Then the shot markers are appended. Run with plain
python3 from the repo root.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))
I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
# high noon, a little from the south (travels north and down)
B_NOON = "Transform3D(1, 0, 0, 0, 0.342, 0.940, 0, -0.940, 0.342, {}, {}, {})"
# travels EAST, 12 deg down: the sun going down in the west
B_SUN_FROM_W = "Transform3D(0, 0.208, -0.978, 0, 0.978, 0.208, 1, 0, 0, {}, {}, {})"
T = "__small_wood_backyard_party"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


lights = [
    ("Sun" + T, "DirectionalLight3D", B_NOON.format(0, 30, -10), c(1.0, 0.96, 0.88), 1.2),
    ("SkyFill" + T, "DirectionalLight3D", B_FILL.format(0, 20, -10), c(0.76, 0.82, 0.92), 0.40),
]

CFG = {
    # VOL 2's SMALL WOOD BACKYARD (build_small_wood_backyard.py): her
    # fifteenth birthday, summer, late 1990s.
    "out_path": os.path.join(ROOT, "small_wood_backyard.tscn"),
    "uid": "uid://small_wood_backyard_v1",
    "root_node": "SmallWoodBackyard",
    "glb": "res://assets/3d/locales/small_wood_backyard.glb",
    "env": {"bg": (0.66, 0.74, 0.82, 1), "amb": (0.86, 0.86, 0.82, 1),
            "amb_e": 0.80, "fog": (0.78, 0.82, 0.84, 1), "fog_e": 0.4,
            "fog_d": 0.003, "sat": 0.94, "glow_i": 0.6, "glow_b": 0.12},
    "shader": {"warm": (0.96, 0.88, 0.74, 1), "bg": (0.08, 0.08, 0.08, 1),
               "neon_edge": (0.78, 0.70, 0.56, 1), "neon_lo": (0.28, 0.26, 0.20, 1),
               "neon_hi": (0.08, 0.08, 0.08, 1), "lim_tint": (0.70, 0.66, 0.56, 1)},
    "lights": lights,
    "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
}

MARKERS = [
    ("shot_insert_cake", (-2.6, 1.4, -9.4), (-0.335, 2.62), 40.0,
     "\"played with a mash of cake and cream\""),
    ("shot_insert_hutch", (8.6, 1.3, -15.0), (-0.14, -1.060), 42.0,
     "the rabbit hutches along the fence — she bred rabbits at nine"),
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
