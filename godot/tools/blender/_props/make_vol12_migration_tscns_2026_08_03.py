"""One-shot: locale tscns for the vols 1-2 background 3D migration.

Writes godot/scenes/locales/{missing_link_exterior,briar_falls,
faust_apartment}.tscn via write_locale_tscn (full 8-element parity).
Light positions are derived from the matching build_*.py geometry
(blender (x,y,z) -> godot (x,z,-y)); verify on the Deck once the
GLBs are built. Run with plain python3 from the repo root.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))

I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
# Donor directional bases (see safehouse_bedroom / louisiana_road tscns)
B_KEY = "Transform3D(1, 0, 0, 0, 0.707, -0.707, 0, 0.707, 0.707, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
B_BACK = "Transform3D(0.707, -0.5, 0.5, 0, 0.707, 0.707, -0.707, -0.5, 0.5, {}, {}, {})"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


CONFIGS = [
    {
        # Dusk roadside: warm low key from the west, cool sky fill,
        # practicals on every fixture the build places (window band,
        # door, pole sign, cobra-head, shelter).
        "out_path": os.path.join(ROOT, "missing_link_exterior.tscn"),
        "uid": "uid://missing_link_ext",
        "root_node": "MissingLinkExterior",
        "glb": "res://assets/3d/locales/missing_link_exterior.glb",
        "env": {"bg": (0.30, 0.26, 0.38, 1), "amb": (0.44, 0.42, 0.52, 1),
                "amb_e": 0.5, "fog": (0.22, 0.18, 0.30, 1), "fog_e": 0.4,
                "fog_d": 0.008, "sat": 0.94, "glow_i": 0.8, "glow_b": 0.16},
        "shader": {"warm": (0.96, 0.86, 0.62, 1), "bg": (0.18, 0.16, 0.24, 1),
                   "neon_edge": (0.96, 0.62, 0.20, 1), "neon_lo": (0.42, 0.32, 0.16, 1),
                   "neon_hi": (0.16, 0.16, 0.24, 1), "lim_tint": (0.7, 0.6, 0.44, 1)},
        "lights": [
            ("Dusk_Key", "DirectionalLight3D", B_FILL.format(-4, 8, 0), c(0.98, 0.66, 0.38), 1.0),
            ("Fill_Sky", "DirectionalLight3D", B_KEY.format(0, 6, 0), c(0.52, 0.58, 0.78), 0.35),
            ("Back_Rim", "DirectionalLight3D", B_BACK.format(0, 5, 4), c(0.58, 0.66, 0.88), 0.28),
            # Diner window band (blender front y=8 -> godot z=-8)
            ("Diner_WinGlow_W", "OmniLight3D", I.format(-2.6, 1.7, -7.7), c(1.0, 0.80, 0.48), 1.6, {"omni_range": 5.0}),
            ("Diner_WinGlow_E", "OmniLight3D", I.format(0.4, 1.7, -7.7), c(1.0, 0.80, 0.48), 1.6, {"omni_range": 5.0}),
            ("Diner_DoorGlow", "OmniLight3D", I.format(2.4, 1.6, -7.6), c(1.0, 0.82, 0.50), 1.0, {"omni_range": 3.5}),
            ("Sign_Glow", "OmniLight3D", I.format(-6.5, 4.7, -6.5), c(0.98, 0.72, 0.50), 1.2, {"omni_range": 4.0}),
            # Cobra head at blender (8.2, 2.45, 4.8)
            ("Lamp_Sodium", "OmniLight3D", I.format(8.2, 4.8, -2.45), c(1.0, 0.62, 0.26), 3.0, {"omni_range": 10.0}),
            ("Shelter_Spill", "OmniLight3D", I.format(6.5, 2.2, -4.9), c(0.90, 0.90, 0.85), 0.7, {"omni_range": 3.0}),
        ],
        "mood_strata": ["raw", "noir", "sodium_streetlamp", "lithograph",
                        "silent_film_24", "dawn_warm", "memory_warm"],
    },
    {
        # Mountain day: bright warm sun, blue sky fill, ridge rim.
        # Day exterior — single doorway practical only.
        "out_path": os.path.join(ROOT, "briar_falls.tscn"),
        "uid": "uid://briar_falls_park",
        "root_node": "BriarFalls",
        "glb": "res://assets/3d/locales/briar_falls.glb",
        "env": {"bg": (0.66, 0.76, 0.84, 1), "amb": (0.60, 0.64, 0.62, 1),
                "amb_e": 0.8, "fog": (0.60, 0.68, 0.72, 1), "fog_e": 0.3,
                "fog_d": 0.004, "bright": 1.02, "sat": 1.0,
                "glow_i": 0.6, "glow_b": 0.10},
        "shader": {"warm": (0.90, 0.88, 0.78, 1), "bg": (0.24, 0.30, 0.28, 1),
                   "neon_edge": (0.72, 0.80, 0.62, 1), "neon_lo": (0.30, 0.38, 0.28, 1),
                   "neon_hi": (0.16, 0.22, 0.20, 1), "lim_tint": (0.60, 0.70, 0.55, 1)},
        "lights": [
            ("Sun_Key", "DirectionalLight3D", B_FILL.format(0, 10, 0), c(1.0, 0.96, 0.86), 1.35),
            ("Fill_Sky", "DirectionalLight3D", B_KEY.format(0, 8, 0), c(0.62, 0.72, 0.84), 0.5),
            ("Back_Ridge", "DirectionalLight3D", B_BACK.format(0, 6, 6), c(0.72, 0.78, 0.88), 0.3),
            # Lamp over the rest-stop door (blender front y=8)
            ("Doorway_Lamp", "OmniLight3D", I.format(-2.75, 2.35, -7.7), c(1.0, 0.85, 0.60), 0.6, {"omni_range": 2.5}),
        ],
        "mood_strata": ["raw", "morning_bright", "linework", "lithograph",
                        "silent_film_24", "memory_warm"],
    },
    {
        # Night-warm studio (the 4am scenes are the default; day
        # scenes grade up via moods). Practicals: nightstand lamp,
        # bare ceiling bulb, cool window spill.
        "out_path": os.path.join(ROOT, "faust_apartment.tscn"),
        "uid": "uid://faust_apartment",
        "root_node": "FaustApartment",
        "glb": "res://assets/3d/locales/faust_apartment.glb",
        "env": {"bg": (0.08, 0.06, 0.04, 1), "amb": (0.66, 0.56, 0.40, 1),
                "amb_e": 0.6, "fog": (0.38, 0.30, 0.22, 1), "fog_e": 0.4,
                "fog_d": 0.005, "sat": 0.92, "glow_i": 0.65, "glow_b": 0.10},
        "shader": {"warm": (0.92, 0.82, 0.60, 1), "bg": (0.10, 0.09, 0.07, 1),
                   "neon_edge": (0.72, 0.70, 0.60, 1), "neon_lo": (0.32, 0.28, 0.20, 1),
                   "neon_hi": (0.08, 0.08, 0.09, 1), "lim_tint": (0.70, 0.60, 0.44, 1)},
        "lights": [
            ("Key_Window", "DirectionalLight3D", B_KEY.format(0, 6, 0), c(0.66, 0.72, 0.92), 0.45),
            ("Fill_Warm", "DirectionalLight3D", B_FILL.format(0, 3, -2), c(0.96, 0.78, 0.42), 0.22),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 3), c(0.42, 0.32, 0.22), 0.15),
            # Nightstand lamp (blender (-0.85, 4.65, ~1.0))
            ("Practical_NightLamp", "OmniLight3D", I.format(-0.85, 1.05, -4.65), c(0.98, 0.84, 0.50), 1.0, {"omni_range": 2.2}),
            ("Practical_Bulb", "OmniLight3D", I.format(0, 2.3, -2.5), c(1.0, 0.86, 0.52), 1.2, {"omni_range": 4.5}),
            ("Moon_Spill", "OmniLight3D", I.format(2.5, 1.7, -2.4), c(0.60, 0.70, 0.95), 0.5, {"omni_range": 3.0}),
        ],
        "mood_strata": ["raw", "noir", "lithograph", "macro_haze",
                        "silent_film_18", "candlelight", "memory_warm"],
    },
]


def main():
    for cfg in CONFIGS:
        path = write_locale_tscn(cfg)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
