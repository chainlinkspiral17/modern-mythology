"""One-shot: the locale tscn for vol4_apartments (draft 1, 2026-10-28).

Same contract as make_honolulu_highrise_tscn_2026_10_28.py. influx: an hour
before sunrise — the bedside lamp, the coffee maker's red light, the lot's
sodium lamps through the blinds. Chess's hallway: morning — the sconces,
the elevator's ceiling light, daylight from the window at the far end.
Lights named `<name>__<preset>` play only in that preset.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))
I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
IN, CH = "__vol4_apartment_dawn", "__chess_hallway"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


lights = [
    ("Influx_Lamp_Light" + IN, "OmniLight3D", I.format(0.25, 1.15, -5.55), c(1.0, 0.78, 0.52), 1.0, {"omni_range": 4.5}),
    ("Influx_Kitchen_Light" + IN, "OmniLight3D", I.format(4.6, 2.2, -0.9), c(0.96, 0.92, 0.84), 0.45, {"omni_range": 3.5}),
    ("Influx_Coffee_Glow" + IN, "OmniLight3D", I.format(3.9, 1.05, -0.5), c(1.0, 0.30, 0.16), 0.25, {"omni_range": 1.2}),
    ("Influx_Lot_Spill" + IN, "OmniLight3D", I.format(2.2, 1.6, -7.0), c(1.0, 0.68, 0.36), 0.7, {"omni_range": 5.0}),
]
for k in range(3):
    lights.append(("Complex_Lamp_%d%s" % (k, IN), "OmniLight3D", I.format(-6.0 + k * 9.0, 3.8, -16.0), c(1.0, 0.66, 0.32), 1.2, {"omni_range": 12.0}))
lights.append(("Elevator_Light" + CH, "OmniLight3D", I.format(41.6, 2.2, -1.0), c(1.0, 0.94, 0.82), 0.8, {"omni_range": 3.0}))
for k in range(7):
    lights.append(("Hall_Sconce_Light_%d%s" % (k, CH), "OmniLight3D", I.format(41.6, 1.95, -(3.0 + k * 4.0)), c(1.0, 0.84, 0.60), 0.55, {"omni_range": 3.4}))
lights.append(("Hall_Window_Day" + CH, "OmniLight3D", I.format(41.6, 1.6, -28.8), c(0.84, 0.90, 1.0), 1.2, {"omni_range": 8.0}))

CFG = {
    "out_path": os.path.join(ROOT, "vol4_apartments.tscn"),
    "uid": "uid://vol4_apartments_v1",
    "root_node": "Vol4Apartments",
    "glb": "res://assets/3d/locales/vol4_apartments.glb",
    "env": {"bg": (0.10, 0.12, 0.20, 1), "amb": (0.56, 0.56, 0.62, 1),
            "amb_e": 0.45, "fog": (0.16, 0.16, 0.22, 1), "fog_e": 0.3,
            "fog_d": 0.004, "sat": 0.92, "glow_i": 0.7, "glow_b": 0.12},
    "shader": {"warm": (0.96, 0.86, 0.70, 1), "bg": (0.08, 0.08, 0.08, 1),
               "neon_edge": (0.78, 0.70, 0.56, 1), "neon_lo": (0.28, 0.26, 0.22, 1),
               "neon_hi": (0.08, 0.08, 0.08, 1), "lim_tint": (0.70, 0.66, 0.56, 1)},
    "lights": lights,
    "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
}

MARKERS = [
    ("shot_insert_coffee__vol4_apartment_dawn", (4.6, 1.5, -1.5), (0.0, 0.0), 38.0,
     "\"He fills the morning emptiness with hot coffee diluted to last through the weekend.\""),
    ("shot_insert_trough__chess_hallway", (41.9, 1.3, -10.6), (0.0, 0.0), 40.0,
     "\"an elderly man was walking their way with a garden trough in his hand\""),
    ("shot_insert_elevator__chess_hallway", (41.15, 1.5, -0.75), (-0.2289, -1.0778), 40.0,
     "\"The elevator hums and settles, slow as an old man.\""),
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
