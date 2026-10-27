"""One-shot: the locale tscn for desert_route (draft 1, 2026-10-27).

Same contract as make_vol1_4_tscns_2026_10_17.py. The scene's own
environment is the highway at noon; the storm and the motel's dusk lift or
drown it in Background3D. Lights named `<name>__<preset>[__<preset>]` play
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
DAY = "__utah_highway_day__desert_gas_station"
STORM = "__dust_storm_highway"
DUSK = "__desert_motel_dusk__motel_pool_dusk__motel_room_dusk"

# from build_desert_route.py
R4 = -400.0 - 17.0 + 2.125 + 3 * 4.25          # room No. 4's centre x
FY = 14.0                                       # wing A's front y


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


lights = [
    ("Noon" + DAY, "DirectionalLight3D", B_NOON.format(0, 40, 0), c(1.0, 0.95, 0.86), 1.5),
    ("SkyFill" + DAY, "DirectionalLight3D", B_FILL.format(0, 20, 0), c(0.70, 0.78, 0.96), 0.30),
    ("Store_Fluorescent__desert_gas_station", "OmniLight3D", I.format(400.0, 2.8, -12.5), c(0.92, 0.96, 1.0), 1.2, {"omni_range": 7.0}),
    ("StormGlow" + STORM, "DirectionalLight3D", B_NOON.format(0, 40, 0), c(1.0, 0.46, 0.28), 0.45),
    ("StormFill" + STORM, "DirectionalLight3D", B_FILL.format(0, 20, 0), c(0.80, 0.40, 0.30), 0.25),
]
for k in range(6):
    lights.append(("WreckFire_{}".format(k) + STORM, "OmniLight3D",
                   I.format(round(-4.0 + k * 1.8, 2), 1.6, round(-(60.0 + (k % 3) * 5.0), 2)), c(1.0, 0.56, 0.22), 3.0, {"omni_range": 18.0}))
lights += [
    ("Sunset" + DUSK, "DirectionalLight3D", B_SUN_FROM_W.format(-460, 20, 0), c(1.0, 0.70, 0.46), 1.3),
    ("DuskSky" + DUSK, "DirectionalLight3D", B_FILL.format(-400, 20, 0), c(0.62, 0.56, 0.86), 0.35),
    ("Office_Window" + DUSK, "OmniLight3D", I.format(-379.0, 1.5, -2.0), c(1.0, 0.84, 0.56), 1.6, {"omni_range": 8.0}),
    ("Room4_Lamp" + DUSK, "OmniLight3D", I.format(round(R4 - 1.6, 2), 1.25, -(FY + 5.0)), c(1.0, 0.82, 0.54), 1.2, {"omni_range": 5.0}),
    ("Room4_TV" + DUSK, "OmniLight3D", I.format(round(R4 + 1.0, 2), 1.1, -(FY + 2.6)), c(0.56, 0.74, 1.0), 0.8, {"omni_range": 3.5}),
    ("Pool_Underwater" + DUSK, "OmniLight3D", I.format(-402.0, 0.0, -2.0), c(0.40, 0.90, 1.0), 1.2, {"omni_range": 6.0}),
    ("Motel_Sign_Glow" + DUSK, "OmniLight3D", I.format(-374.0, 6.4, 19.0), c(0.50, 0.90, 0.90), 1.2, {"omni_range": 9.0}),
]

CFG = {
    # VOL 3's DESERT ROUTE (build_desert_route.py): Kathy's Utah run —
    # the highway at noon, the station off the main drag, the red storm,
    # the motel at dusk.
    "out_path": os.path.join(ROOT, "desert_route.tscn"),
    "uid": "uid://desert_route_v1",
    "root_node": "DesertRoute",
    "glb": "res://assets/3d/locales/desert_route.glb",
    "env": {"bg": (0.55, 0.68, 0.86, 1), "amb": (0.92, 0.82, 0.70, 1),
            "amb_e": 0.80, "fog": (0.88, 0.74, 0.60, 1), "fog_e": 0.4,
            "fog_d": 0.0006, "sat": 0.96, "glow_i": 0.7, "glow_b": 0.14},
    "shader": {"warm": (0.98, 0.84, 0.64, 1), "bg": (0.10, 0.06, 0.04, 1),
               "neon_edge": (0.96, 0.58, 0.32, 1), "neon_lo": (0.42, 0.22, 0.14, 1),
               "neon_hi": (0.10, 0.06, 0.04, 1), "lim_tint": (0.86, 0.56, 0.38, 1)},
    "lights": lights,
    "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
}

MARKERS = [
    ("shot_insert_ice_chest", (402.0, 1.4, -5.0), (-0.219, -0.476), 40.0,
     "the outdoor ice cooler the mud man washes himself in"),
    ("shot_insert_galaga", (398.5, 1.5, -11.5), (-0.08, 2.054), 40.0,
     "\"a quick game of Galaga\""),
    ("shot_insert_curio", (398.5, 1.5, -12.5), (-0.09, 0.222), 40.0,
     "\"selling dead lizards horny toads\": the curios Kathy keeps the children from"),
    ("shot_insert_wreck", (5.0, 1.6, -35.0), (0.0, 0.149), 45.0,
     "\"a long burning mass of wreckage\": the two semis across both lanes"),
    ("shot_insert_pool", (-398.5, 1.5, 2.6), (-0.31, 0.483), 45.0,
     "\"Red silt settles on the skin of the water\""),
    ("shot_insert_tv", (round(R4 - 0.4, 3), 1.3, -(FY + 1.6)), (-0.09, -1.087), 42.0,
     "the motel television, \"the first thing that came on\""),
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
