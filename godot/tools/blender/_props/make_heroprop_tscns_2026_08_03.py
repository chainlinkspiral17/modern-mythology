"""One-shot: tscns for the vols 5-7 hero-prop pass — cabin_road
(vol7's Oregon road, split off louisiana_road) and nexcorp_gas_go
(the Harmony Creek Gas & Go, whose rich build had no tscn while its
scenes played over the wrong station). Run with plain python3.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))
I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
B_KEY = "Transform3D(1, 0, 0, 0, 0.707, -0.707, 0, 0.707, 0.707, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
B_BACK = "Transform3D(0.707, -0.5, 0.5, 0, 0.707, 0.707, -0.707, -0.5, 0.5, {}, {}, {})"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


CONFIGS = [
    {
        # Gray-bright coastal light in the Sitka stand; no practicals
        # (there is nothing electric on this road).
        "out_path": os.path.join(ROOT, "cabin_road.tscn"),
        "uid": "uid://cabin_road_v7",
        "root_node": "CabinRoad",
        "glb": "res://assets/3d/locales/cabin_road.glb",
        "env": {"bg": (0.66, 0.70, 0.70, 1), "amb": (0.54, 0.58, 0.56, 1),
                "amb_e": 0.75, "fog": (0.62, 0.66, 0.66, 1), "fog_e": 0.55,
                "fog_d": 0.014, "sat": 0.92, "glow_i": 0.55, "glow_b": 0.08},
        "shader": {"warm": (0.84, 0.86, 0.80, 1), "bg": (0.20, 0.24, 0.23, 1),
                   "neon_edge": (0.62, 0.72, 0.62, 1), "neon_lo": (0.22, 0.30, 0.26, 1),
                   "neon_hi": (0.12, 0.16, 0.15, 1), "lim_tint": (0.55, 0.66, 0.58, 1)},
        "lights": [
            ("Overcast_Key", "DirectionalLight3D", B_KEY.format(0, 10, 0), c(0.82, 0.85, 0.83), 0.9),
            ("Fill", "DirectionalLight3D", B_FILL.format(-3, 6, 0), c(0.66, 0.70, 0.66), 0.4),
            ("Back_Clearing", "DirectionalLight3D", B_BACK.format(3, 6, 6), c(0.74, 0.78, 0.70), 0.35),
        ],
        "mood_strata": ["raw", "noir", "linework", "lithograph",
                        "silent_film_18", "memory_warm"],
    },
    {
        # NexCorp navy interior, fluorescent-bright store + canopy
        # glow through the south glass.
        "out_path": os.path.join(ROOT, "nexcorp_gas_go.tscn"),
        "uid": "uid://nexcorp_gas_go",
        "root_node": "NexcorpGasGo",
        "glb": "res://assets/3d/locales/nexcorp_gas_go.glb",
        "env": {"bg": (0.30, 0.34, 0.42, 1), "amb": (0.58, 0.60, 0.64, 1),
                "amb_e": 0.8, "fog": (0.40, 0.44, 0.52, 1), "fog_e": 0.3,
                "fog_d": 0.004, "sat": 0.94, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.86, 0.88, 0.92, 1), "bg": (0.16, 0.20, 0.26, 1),
                   "neon_edge": (0.55, 0.68, 0.88, 1), "neon_lo": (0.20, 0.26, 0.36, 1),
                   "neon_hi": (0.10, 0.13, 0.18, 1), "lim_tint": (0.52, 0.60, 0.74, 1)},
        "lights": [
            ("Key_Overhead", "DirectionalLight3D", B_KEY.format(0, 7, 0), c(0.90, 0.92, 0.95), 1.0),
            ("Fill_Canopy", "DirectionalLight3D", B_FILL.format(0, 4, 2), c(0.72, 0.78, 0.88), 0.4),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 4, 4), c(0.55, 0.60, 0.70), 0.25),
            ("Store_Fluor_S", "OmniLight3D", I.format(0, 2.7, -2.5), c(0.90, 0.93, 0.96), 1.3, {"omni_range": 5.0}),
            ("Store_Fluor_N", "OmniLight3D", I.format(0, 2.7, -6.5), c(0.90, 0.93, 0.96), 1.3, {"omni_range": 5.0}),
            ("Canopy_Spill", "OmniLight3D", I.format(0, 2.2, 2.5), c(0.80, 0.86, 0.95), 1.2, {"omni_range": 6.0}),
        ],
        "mood_strata": ["raw", "noir", "sodium_streetlamp", "lithograph",
                        "silent_film_24", "memory_warm"],
    },
    {
        # The Oneironautics cedar tower: warm cedar interiors, the
        # portal floor's substrate glow, the seventh-floor garden.
        "out_path": os.path.join(ROOT, "cedar_tower.tscn"),
        "uid": "uid://cedar_tower_v7",
        "root_node": "CedarTower",
        "glb": "res://assets/3d/locales/cedar_tower.glb",
        "env": {"bg": (0.20, 0.18, 0.15, 1), "amb": (0.62, 0.52, 0.40, 1),
                "amb_e": 0.65, "fog": (0.36, 0.30, 0.24, 1), "fog_e": 0.35,
                "fog_d": 0.004, "sat": 0.96, "glow_i": 0.75, "glow_b": 0.14},
        "shader": {"warm": (0.92, 0.82, 0.62, 1), "bg": (0.16, 0.13, 0.10, 1),
                   "neon_edge": (0.80, 0.66, 0.44, 1), "neon_lo": (0.34, 0.28, 0.20, 1),
                   "neon_hi": (0.12, 0.10, 0.08, 1), "lim_tint": (0.70, 0.62, 0.46, 1)},
        "lights": [
            ("Key_Warm", "DirectionalLight3D", B_KEY.format(0, 8, 0), c(0.95, 0.86, 0.70), 0.85),
            ("Fill", "DirectionalLight3D", B_FILL.format(-3, 5, 0), c(0.72, 0.64, 0.52), 0.35),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 5, 5), c(0.55, 0.50, 0.44), 0.25),
            # The portrait wash in the lobby
            ("Portrait_Wash", "OmniLight3D", I.format(0, 2.4, -7.4), c(0.98, 0.88, 0.68), 1.0, {"omni_range": 3.5}),
            # Studio rack LEDs' green ambient
            ("Rack_Green", "OmniLight3D", I.format(0, 6.6, -8.4), c(0.40, 0.80, 0.48), 0.7, {"omni_range": 5.0}),
            # Quarters wood-stove ember
            ("Q_Stove_Ember", "OmniLight3D", I.format(5.0, 10.6, -6.6), c(0.96, 0.52, 0.24), 0.8, {"omni_range": 3.5}),
            # The substrate's held light in the portal room
            ("Substrate_Glow", "OmniLight3D", I.format(0, 16.6, -20.4), c(0.60, 0.82, 0.88), 1.6, {"omni_range": 12.0}),
            # The seventh floor's garden glass, from the clearing
            ("Garden_Glass", "OmniLight3D", I.format(45.0, 25.0, -7.6), c(0.55, 0.80, 0.58), 1.2, {"omni_range": 8.0}),
        ],
        "mood_strata": ["raw", "noir", "lithograph", "macro_haze",
                        "liminal_interior", "memory_warm"],
    },
]


def main():
    for cfg in CONFIGS:
        path = write_locale_tscn(cfg)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
