"""One-shot: the locale tscn for honolulu_highrise (draft 1, 2026-10-28).

Same contract as make_small_wood_backyard_tscn_2026_10_27.py. A bright
Honolulu late morning through the lobby's glass front; the lobby's
downlights; the game store's fluorescent troffers and its back-lit box
sign. Lights named `<name>__<preset>` play only in that preset. Then the
shot markers are appended. Run with plain python3 from the repo root.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))
I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
# late-morning sun from the south-east, travelling north-west and down, through the glass front
B_SUN = "Transform3D(0.707, 0.454, -0.542, 0, 0.766, 0.643, 0.707, -0.454, 0.542, {}, {}, {})"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


lights = [
    ("Sun", "DirectionalLight3D", B_SUN.format(0, 30, 10), c(1.0, 0.96, 0.88), 1.1),
    ("SkyFill", "DirectionalLight3D", B_FILL.format(0, 20, -10), c(0.78, 0.86, 0.96), 0.35),
]
# the lobby's downlights (blender (x, y, z) -> godot (x, z, -y))
for k in range(6):
    bx, by = -5.0 + (k % 3) * 5.0, 4.0 + (k // 3) * 7.0
    lights.append(("Lobby_Downlight_%d" % k, "OmniLight3D", I.format(bx, 5.2, -by), c(1.0, 0.92, 0.80), 0.7, {"omni_range": 7.0}))
# the store's troffers and its sign
for k in range(3):
    for j in range(2):
        bx, by = 10.2 + k * 1.8, 7.0 + j * 2.0
        lights.append(("Store_Troffer_%d_%d" % (k, j), "OmniLight3D", I.format(bx, 2.8, -by), c(0.92, 0.98, 1.0), 0.6, {"omni_range": 3.6}))
lights.append(("Store_Sign_Glow", "OmniLight3D", I.format(8.5, 3.3, -8.0), c(0.92, 0.96, 1.0), 0.8, {"omni_range": 3.0}))

CFG = {
    # VOL 3's HONOLULU HIGH-RISE (build_honolulu_highrise.py): ch 6
    # arcadeum, the lobby and the boutique game store, early 2000s.
    "out_path": os.path.join(ROOT, "honolulu_highrise.tscn"),
    "uid": "uid://honolulu_highrise_v1",
    "root_node": "HonoluluHighrise",
    "glb": "res://assets/3d/locales/honolulu_highrise.glb",
    "env": {"bg": (0.62, 0.78, 0.92, 1), "amb": (0.88, 0.88, 0.86, 1),
            "amb_e": 0.75, "fog": (0.80, 0.86, 0.92, 1), "fog_e": 0.3,
            "fog_d": 0.002, "sat": 1.0, "glow_i": 0.7, "glow_b": 0.14},
    "shader": {"warm": (0.98, 0.92, 0.80, 1), "bg": (0.08, 0.08, 0.08, 1),
               "neon_edge": (0.80, 0.74, 0.60, 1), "neon_lo": (0.28, 0.26, 0.22, 1),
               "neon_hi": (0.08, 0.08, 0.08, 1), "lim_tint": (0.72, 0.68, 0.58, 1)},
    "lights": lights,
    "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
}

# (name, godot position, (pitch, yaw), fov, why) — aimed by marker_reaim.py --tight after writing
MARKERS = [
    ("shot_insert_register", (12.30, 1.55, -5.85), (-0.45, -2.30), 35.0,
     "\"the clear display underneath the register\" — WHAT LIES BEYOND in the case, the imprinter on top"),
    ("shot_insert_window", (10.6, 1.40, -6.20), (-0.20, 1.80), 40.0,
     "\"The newest game in their front window display was Mountaintop's Final Cut\""),
    ("shot_insert_sign", (2.5, 1.60, -7.0), (0.20, -1.57), 40.0,
     "\"a cheap box vinyl back-lit fluorescent number that promised only COMPUTER GAMES\""),
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
