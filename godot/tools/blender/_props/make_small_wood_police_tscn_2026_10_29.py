"""One-shot: the locale tscn for small_wood_police (draft 1, 2026-10-29).

Same contract as make_vol4_apartments_tscn_2026_10_28.py. The interview room
under its two fluorescent troffers (cool, flat, the light the text never has
to name); the squad room's troffers beyond the door; grey daylight through
the front windows.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))
I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


lights = [
    ("Interview_Troffer_0_Light", "OmniLight3D", I.format(2.3, 2.55, -1.4), c(0.92, 0.96, 1.0), 1.1, {"omni_range": 4.2}),
    ("Interview_Troffer_1_Light", "OmniLight3D", I.format(2.3, 2.55, -2.8), c(0.92, 0.96, 1.0), 1.1, {"omni_range": 4.2}),
]
for i in range(3):
    for j in range(3):
        lights.append(("Squad_Troffer_%d_%d_Light" % (i, j), "OmniLight3D", I.format(6.8 + i * 3.2, 2.55, -(-1.0 + j * 3.6)),
                       c(0.92, 0.96, 1.0), 0.6, {"omni_range": 4.6}))
lights.append(("Squad_Window_Day", "OmniLight3D", I.format(14.2, 1.6, -2.0), c(0.80, 0.86, 0.94), 1.0, {"omni_range": 8.0}))

CFG = {
    "out_path": os.path.join(ROOT, "small_wood_police.tscn"),
    "uid": "uid://small_wood_police_v1",
    "root_node": "SmallWoodPolice",
    "glb": "res://assets/3d/locales/small_wood_police.glb",
    "env": {"bg": (0.40, 0.44, 0.48, 1), "amb": (0.62, 0.66, 0.64, 1),
            "amb_e": 0.45, "fog": (0.40, 0.42, 0.44, 1), "fog_e": 0.3,
            "fog_d": 0.003, "sat": 0.88, "glow_i": 0.5, "glow_b": 0.06},
    "shader": {"warm": (0.86, 0.90, 0.86, 1), "bg": (0.08, 0.08, 0.08, 1),
               "neon_edge": (0.70, 0.74, 0.70, 1), "neon_lo": (0.26, 0.28, 0.26, 1),
               "neon_hi": (0.08, 0.08, 0.08, 1), "lim_tint": (0.66, 0.70, 0.66, 1)},
    "lights": lights,
    "mood_strata": ["raw", "noir", "lithograph", "high_contrast_bw", "silent_film_18"],
}

MARKERS = [
    ("shot_insert_notebook", (3.10, 1.35, -1.55), (-0.7730, 0.9410), 38.0,
     "\"He pulled his pin from the clip on his notebook and tapped the butt, clicking it ready.\""),
    ("shot_insert_coffee", (2.20, 1.40, -1.55), (-0.5144, -0.6908), 40.0,
     "\"he poured coffee for himself and the other men in the room\""),
    ("shot_closeup_julie", (3.20, 1.25, -2.00), (-0.1020, 1.5708), 45.0,
     "closeup: Julie's chair from James's side, the observation mirror behind her"),
    ("shot_closeup_james", (1.20, 1.25, -2.00), (-0.1020, -1.5708), 45.0,
     "closeup: James's chair from Julie's side, the door and its wire glass behind him"),
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
