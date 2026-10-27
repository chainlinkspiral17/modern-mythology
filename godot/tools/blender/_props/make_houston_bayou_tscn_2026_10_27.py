"""One-shot: the locale tscn for houston_bayou (draft 1, 2026-10-27).

Same contract as make_vol1_4_tscns_2026_10_17.py. The scene's own
environment is the park by day; the dream river's night is set per preset
in Background3D. Lights named `<name>__<preset>[__<preset>]` play
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
PARK = "__houston_park_day"
RIVER = "__jd_river__jd_river_turn"
RX = 3000.0


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


lights = [
    ("Sun" + PARK, "DirectionalLight3D", B_NOON.format(0, 40, 0), c(1.0, 0.95, 0.86), 1.4),
    ("SkyFill" + PARK, "DirectionalLight3D", B_FILL.format(0, 20, 0), c(0.70, 0.80, 0.98), 0.32),
    ("Moon" + RIVER, "DirectionalLight3D", B_NOON.format(RX, 30, 0), c(0.62, 0.60, 0.96), 0.75),
    ("NightFill" + RIVER, "DirectionalLight3D", B_FILL.format(RX, 30, 0), c(0.50, 0.44, 0.80), 0.35),
    ("JD_Headlights__jd_river", "OmniLight3D", I.format(RX, 0.8, -3.0), c(1.0, 0.90, 0.70), 1.0, {"omni_range": 12.0}),
    ("JD_Headlights__jd_river_turn", "OmniLight3D", I.format(RX, 0.8, 313.0), c(1.0, 0.90, 0.70), 1.0, {"omni_range": 12.0}),
    ("StripMall_Glow" + RIVER, "OmniLight3D", I.format(RX + 27.0, 2.4, -25.0), c(1.0, 0.86, 0.60), 2.0, {"omni_range": 26.0}),
    ("Toll_Light" + RIVER, "OmniLight3D", I.format(RX + 9.0, 3.4, -95.0), c(1.0, 0.94, 0.80), 1.4, {"omni_range": 14.0}),
    ("Bright_Water" + RIVER, "OmniLight3D", I.format(RX, 1.2, -150.0), c(0.80, 1.0, 0.96), 2.0, {"omni_range": 40.0}),
    ("Drugstore_Glow" + RIVER, "OmniLight3D", I.format(RX, 3.0, -152.0), c(1.0, 0.98, 0.92), 4.0, {"omni_range": 45.0}),
    ("Methane_Torch" + RIVER, "OmniLight3D", I.format(RX + 9.0, 8.4, -149.0), c(1.0, 0.60, 0.24), 2.0, {"omni_range": 20.0}),
    ("Club_Door" + RIVER, "OmniLight3D", I.format(RX, 1.5, 645.0), c(1.0, 0.80, 0.54), 1.6, {"omni_range": 10.0}),
]
for k in range(12):
    lights.append(("RiverLamp_{}".format(k) + RIVER, "OmniLight3D", I.format(RX + 20.5, 6.6, round(-(-50.0 + k * 28.0), 2)),
                   c(1.0, 0.82, 0.52), 1.5, {"omni_range": 22.0}))
for k, (lx, ly) in enumerate(((RX + 24.0, 55.0), (RX + 24.0, 95.0), (RX + 68.0, 53.0), (RX + 68.0, 97.0))):
    lights.append(("Diamond_Flood_{}".format(k) + RIVER, "OmniLight3D", I.format(lx, 14.0, -ly), c(1.0, 0.98, 0.90), 3.0, {"omni_range": 45.0}))

CFG = {
    # VOL 1's HOUSTON OUTSIDE (build_houston_bayou.py): the jogging park on
    # Buffalo Bayou by day; the dream river at night.
    "out_path": os.path.join(ROOT, "houston_bayou.tscn"),
    "uid": "uid://houston_bayou_v1",
    "root_node": "HoustonBayou",
    "glb": "res://assets/3d/locales/houston_bayou.glb",
    "env": {"bg": (0.58, 0.72, 0.90, 1), "amb": (0.86, 0.86, 0.82, 1),
            "amb_e": 0.75, "fog": (0.80, 0.84, 0.86, 1), "fog_e": 0.4,
            "fog_d": 0.0006, "sat": 0.98, "glow_i": 0.8, "glow_b": 0.14},
    "shader": {"warm": (0.96, 0.86, 0.70, 1), "bg": (0.06, 0.06, 0.10, 1),
               "neon_edge": (0.70, 0.60, 0.96, 1), "neon_lo": (0.24, 0.20, 0.36, 1),
               "neon_hi": (0.06, 0.06, 0.10, 1), "lim_tint": (0.66, 0.60, 0.86, 1)},
    "lights": lights,
    "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
}

MARKERS = [
    ("shot_closeup_person", (-24.0, 1.62, 26.4), (0.0, -1.20), 45.0,
     "the jog: a face against the trail ahead, the bridge and downtown"),
    ("shot_closeup_person_b", (-20.0, 1.62, 25.6), (0.0, 1.75), 45.0,
     "the reverse: a face against the oaks and the trail behind"),
    ("shot_insert_bridge", (40.0, 1.6, 24.0), (0.04, -0.695), 45.0,
     "the white arched footbridge over the bayou, the joggers' turn"),
    ("shot_insert_toll", (RX + 3.0, 1.6, -85.0), (0.02, -0.541), 42.0,
     "\"an old wooden arm painted red and white, a booth with nobody in it\""),
    ("shot_insert_drugstore", (RX - 4.0, 1.6, -142.0), (0.03, -0.207), 45.0,
     "\"a building sits on the water with every light on\""),
    ("shot_insert_diamond", (RX + 21.0, 2.0, -71.0), (0.02, -1.340), 45.0,
     "\"A Little League diamond with the lights still on.\""),
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
