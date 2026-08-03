"""One-shot: locale tscns for the vols 1-2 migration DEBT wave —
the nine sets that close the 2D-background estate to zero.

Writes godot/scenes/locales/{pharmacy,grunion_beach,bar_exterior,
skatepark,wagner_home,school_newspaper,sapo_falls,little_switzerland,
crumpled_barn}.tscn via write_locale_tscn. Light positions derived
from the matching build_*.py geometry (blender (x,y,z) -> godot
(x,z,-y)); verify on the Deck once the GLBs are built. Run with
plain python3 from the repo root.
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


DAY_TRIO = [
    ("Sun_Key", "DirectionalLight3D", B_FILL.format(0, 10, 0), c(1.0, 0.95, 0.85), 1.3),
    ("Fill_Sky", "DirectionalLight3D", B_KEY.format(0, 8, 0), c(0.62, 0.72, 0.84), 0.5),
    ("Back_Rim", "DirectionalLight3D", B_BACK.format(0, 6, 6), c(0.72, 0.78, 0.88), 0.3),
]

CONFIGS = [
    {
        # Fluorescent retail interior; office lamp is the one warm note.
        "out_path": os.path.join(ROOT, "pharmacy.tscn"),
        "uid": "uid://pharmacy_vol1",
        "root_node": "Pharmacy",
        "glb": "res://assets/3d/locales/pharmacy.glb",
        "env": {"bg": (0.55, 0.56, 0.52, 1), "amb": (0.62, 0.63, 0.60, 1),
                "amb_e": 0.85, "fog": (0.55, 0.56, 0.52, 1), "fog_e": 0.2,
                "fog_d": 0.002, "sat": 0.92, "glow_i": 0.55, "glow_b": 0.08},
        "shader": {"warm": (0.90, 0.90, 0.84, 1), "bg": (0.30, 0.31, 0.29, 1),
                   "neon_edge": (0.70, 0.74, 0.66, 1), "neon_lo": (0.34, 0.36, 0.32, 1),
                   "neon_hi": (0.16, 0.17, 0.16, 1), "lim_tint": (0.70, 0.72, 0.60, 1)},
        "lights": [
            ("Key_Overhead", "DirectionalLight3D", B_KEY.format(0, 6, 0), c(0.92, 0.95, 0.90), 1.0),
            ("Fill_Warm", "DirectionalLight3D", B_FILL.format(-2, 4, 0), c(0.96, 0.88, 0.72), 0.3),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 4, 4), c(0.60, 0.64, 0.68), 0.2),
            # Tube panels at blender y 1.6/3.2/4.8
            ("Fluor_S", "OmniLight3D", I.format(0, 2.55, -1.6), c(0.92, 0.96, 0.92), 1.3, {"omni_range": 4.5}),
            ("Fluor_M", "OmniLight3D", I.format(0, 2.55, -3.2), c(0.92, 0.96, 0.92), 1.3, {"omni_range": 4.5}),
            ("Fluor_N", "OmniLight3D", I.format(0, 2.55, -4.8), c(0.92, 0.96, 0.92), 1.3, {"omni_range": 4.5}),
            ("Office_Lamp", "OmniLight3D", I.format(3.7, 1.15, -5.72), c(0.98, 0.84, 0.55), 0.8, {"omni_range": 2.0}),
        ],
        "mood_strata": ["raw", "noir", "linework", "lithograph",
                        "silent_film_18", "candlelight", "memory_warm"],
    },
    {
        # Clouded-moon night shore; one big soft omni stands in for
        # the hidden moon so the tide gleam reads.
        "out_path": os.path.join(ROOT, "grunion_beach.tscn"),
        "uid": "uid://grunion_beach",
        "root_node": "GrunionBeach",
        "glb": "res://assets/3d/locales/grunion_beach.glb",
        "env": {"bg": (0.10, 0.11, 0.15, 1), "amb": (0.30, 0.34, 0.44, 1),
                "amb_e": 0.5, "fog": (0.12, 0.14, 0.20, 1), "fog_e": 0.5,
                "fog_d": 0.010, "sat": 0.90, "glow_i": 0.9, "glow_b": 0.20},
        "shader": {"warm": (0.72, 0.76, 0.82, 1), "bg": (0.08, 0.09, 0.12, 1),
                   "neon_edge": (0.55, 0.65, 0.80, 1), "neon_lo": (0.16, 0.20, 0.28, 1),
                   "neon_hi": (0.06, 0.07, 0.10, 1), "lim_tint": (0.50, 0.58, 0.70, 1)},
        "lights": [
            ("Moon_Key", "DirectionalLight3D", B_KEY.format(0, 8, 0), c(0.55, 0.62, 0.85), 0.4),
            ("Fill", "DirectionalLight3D", B_FILL.format(-3, 4, 0), c(0.30, 0.34, 0.42), 0.15),
            ("Back_Sea", "DirectionalLight3D", B_BACK.format(0, 5, 6), c(0.45, 0.55, 0.70), 0.3),
            ("Hidden_Moon", "OmniLight3D", I.format(5.0, 10.0, -27.5), c(0.55, 0.58, 0.70), 1.5, {"omni_range": 25.0}),
        ],
        "mood_strata": ["raw", "noir", "ink_blue", "lithograph",
                        "silent_film_18", "memory_warm"],
    },
    {
        # Night street: neon + door spill + window warmth + sodium lamp.
        "out_path": os.path.join(ROOT, "bar_exterior.tscn"),
        "uid": "uid://bar_exterior_v1",
        "root_node": "BarExterior",
        "glb": "res://assets/3d/locales/bar_exterior.glb",
        "env": {"bg": (0.10, 0.10, 0.16, 1), "amb": (0.42, 0.42, 0.55, 1),
                "amb_e": 0.5, "fog": (0.12, 0.12, 0.18, 1), "fog_e": 0.4,
                "fog_d": 0.008, "sat": 0.94, "glow_i": 0.85, "glow_b": 0.18},
        "shader": {"warm": (0.95, 0.85, 0.62, 1), "bg": (0.10, 0.10, 0.15, 1),
                   "neon_edge": (0.95, 0.45, 0.50, 1), "neon_lo": (0.34, 0.20, 0.22, 1),
                   "neon_hi": (0.08, 0.08, 0.12, 1), "lim_tint": (0.70, 0.60, 0.44, 1)},
        "lights": [
            ("Moon_Key", "DirectionalLight3D", B_KEY.format(0, 8, 0), c(0.60, 0.66, 0.90), 0.45),
            ("Fill_WindowWarm", "DirectionalLight3D", B_FILL.format(-2, 4, 0), c(0.95, 0.75, 0.45), 0.25),
            ("Back_Rim", "DirectionalLight3D", B_BACK.format(0, 5, 4), c(0.50, 0.60, 0.85), 0.25),
            ("Neon_Glow", "OmniLight3D", I.format(-1.0, 3.2, -4.1), c(0.95, 0.40, 0.45), 2.2, {"omni_range": 5.0}),
            ("Door_Spill", "OmniLight3D", I.format(-1.0, 1.3, -4.0), c(1.0, 0.78, 0.45), 1.5, {"omni_range": 3.5}),
            ("Window_Warm", "OmniLight3D", I.format(2.4, 1.7, -4.2), c(1.0, 0.76, 0.42), 1.6, {"omni_range": 4.5}),
            # Cobra head at blender (4.8, 1.45, 4.4)
            ("Street_Sodium", "OmniLight3D", I.format(4.8, 4.4, -1.45), c(0.98, 0.84, 0.55), 2.6, {"omni_range": 9.0}),
        ],
        "mood_strata": ["raw", "noir", "sodium_streetlamp", "lithograph",
                        "silent_film_24", "memory_warm"],
    },
    {
        # Day exterior — sun trio only.
        "out_path": os.path.join(ROOT, "skatepark.tscn"),
        "uid": "uid://skatepark_vol1",
        "root_node": "Skatepark",
        "glb": "res://assets/3d/locales/skatepark.glb",
        "env": {"bg": (0.68, 0.76, 0.82, 1), "amb": (0.60, 0.64, 0.62, 1),
                "amb_e": 0.8, "fog": (0.62, 0.68, 0.72, 1), "fog_e": 0.3,
                "fog_d": 0.004, "bright": 1.02, "sat": 1.0,
                "glow_i": 0.55, "glow_b": 0.08},
        "shader": {"warm": (0.88, 0.88, 0.80, 1), "bg": (0.30, 0.32, 0.32, 1),
                   "neon_edge": (0.70, 0.76, 0.66, 1), "neon_lo": (0.32, 0.36, 0.32, 1),
                   "neon_hi": (0.18, 0.20, 0.20, 1), "lim_tint": (0.60, 0.68, 0.58, 1)},
        "lights": list(DAY_TRIO),
        "mood_strata": ["raw", "morning_bright", "linework", "lithograph",
                        "silent_film_24", "memory_warm"],
    },
    {
        # Early-evening family room: lamp + TV glow + ceiling dome.
        "out_path": os.path.join(ROOT, "wagner_home.tscn"),
        "uid": "uid://wagner_home",
        "root_node": "WagnerHome",
        "glb": "res://assets/3d/locales/wagner_home.glb",
        "env": {"bg": (0.09, 0.07, 0.05, 1), "amb": (0.64, 0.55, 0.42, 1),
                "amb_e": 0.62, "fog": (0.38, 0.30, 0.22, 1), "fog_e": 0.4,
                "fog_d": 0.005, "sat": 0.94, "glow_i": 0.6, "glow_b": 0.10},
        "shader": {"warm": (0.94, 0.84, 0.62, 1), "bg": (0.11, 0.09, 0.07, 1),
                   "neon_edge": (0.72, 0.70, 0.60, 1), "neon_lo": (0.32, 0.28, 0.20, 1),
                   "neon_hi": (0.08, 0.08, 0.09, 1), "lim_tint": (0.70, 0.60, 0.44, 1)},
        "lights": [
            ("Key_Window", "DirectionalLight3D", B_KEY.format(0, 6, 0), c(0.70, 0.72, 0.88), 0.4),
            ("Fill_Warm", "DirectionalLight3D", B_FILL.format(0, 3, -2), c(0.96, 0.80, 0.50), 0.25),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 3), c(0.42, 0.34, 0.24), 0.15),
            # Floor lamp (blender (-2.5, 1.15, ~1.5))
            ("Floor_Lamp", "OmniLight3D", I.format(-2.5, 1.5, -1.15), c(0.98, 0.84, 0.50), 1.1, {"omni_range": 3.0}),
            ("TV_Glow", "OmniLight3D", I.format(2.1, 0.9, -2.6), c(0.60, 0.70, 0.80), 0.9, {"omni_range": 2.5}),
            ("Ceiling_Dome", "OmniLight3D", I.format(0, 2.45, -2.5), c(1.0, 0.86, 0.52), 0.9, {"omni_range": 4.0}),
        ],
        "mood_strata": ["raw", "noir", "lithograph", "macro_haze",
                        "silent_film_18", "candlelight", "memory_warm"],
    },
    {
        # Bright afternoon classroom: E-window sun + tube panels.
        "out_path": os.path.join(ROOT, "school_newspaper.tscn"),
        "uid": "uid://school_newspaper",
        "root_node": "SchoolNewspaper",
        "glb": "res://assets/3d/locales/school_newspaper.glb",
        "env": {"bg": (0.60, 0.60, 0.54, 1), "amb": (0.64, 0.63, 0.56, 1),
                "amb_e": 0.85, "fog": (0.60, 0.60, 0.54, 1), "fog_e": 0.2,
                "fog_d": 0.002, "sat": 0.96, "glow_i": 0.55, "glow_b": 0.08},
        "shader": {"warm": (0.92, 0.88, 0.74, 1), "bg": (0.30, 0.30, 0.27, 1),
                   "neon_edge": (0.74, 0.74, 0.62, 1), "neon_lo": (0.36, 0.36, 0.30, 1),
                   "neon_hi": (0.18, 0.18, 0.16, 1), "lim_tint": (0.72, 0.70, 0.55, 1)},
        "lights": [
            ("Key_Window", "DirectionalLight3D", B_FILL.format(3, 5, -3), c(1.0, 0.92, 0.75), 1.0),
            ("Fill", "DirectionalLight3D", B_KEY.format(0, 6, 0), c(0.72, 0.74, 0.72), 0.4),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 4, 4), c(0.60, 0.64, 0.68), 0.25),
            ("Fluor_S", "OmniLight3D", I.format(0, 2.65, -1.8), c(0.92, 0.96, 0.92), 1.2, {"omni_range": 4.5}),
            ("Fluor_N", "OmniLight3D", I.format(0, 2.65, -4.2), c(0.92, 0.96, 0.92), 1.2, {"omni_range": 4.5}),
        ],
        "mood_strata": ["raw", "morning_bright", "linework", "lithograph",
                        "silent_film_18", "memory_warm"],
    },
    {
        # Green gorge day; heavier fog for spray, glow lifts the falls.
        "out_path": os.path.join(ROOT, "sapo_falls.tscn"),
        "uid": "uid://sapo_falls",
        "root_node": "SapoFalls",
        "glb": "res://assets/3d/locales/sapo_falls.glb",
        "env": {"bg": (0.60, 0.70, 0.72, 1), "amb": (0.50, 0.58, 0.54, 1),
                "amb_e": 0.75, "fog": (0.55, 0.62, 0.60, 1), "fog_e": 0.5,
                "fog_d": 0.012, "sat": 0.98, "glow_i": 0.75, "glow_b": 0.15},
        "shader": {"warm": (0.86, 0.90, 0.84, 1), "bg": (0.22, 0.28, 0.28, 1),
                   "neon_edge": (0.66, 0.78, 0.70, 1), "neon_lo": (0.26, 0.34, 0.32, 1),
                   "neon_hi": (0.14, 0.18, 0.18, 1), "lim_tint": (0.55, 0.68, 0.60, 1)},
        "lights": [
            ("Sun_Key", "DirectionalLight3D", B_FILL.format(0, 12, 0), c(0.95, 0.98, 0.92), 1.2),
            ("Fill_Sky", "DirectionalLight3D", B_KEY.format(0, 9, 0), c(0.60, 0.70, 0.74), 0.5),
            ("Back_Gorge", "DirectionalLight3D", B_BACK.format(0, 6, 6), c(0.70, 0.78, 0.80), 0.3),
        ],
        "mood_strata": ["raw", "morning_bright", "linework", "lithograph",
                        "silent_film_24", "memory_warm"],
    },
    {
        # Alpine day; chalet ground-floor windows carry warm practicals.
        "out_path": os.path.join(ROOT, "little_switzerland.tscn"),
        "uid": "uid://little_switzerland",
        "root_node": "LittleSwitzerland",
        "glb": "res://assets/3d/locales/little_switzerland.glb",
        "env": {"bg": (0.64, 0.74, 0.84, 1), "amb": (0.60, 0.64, 0.64, 1),
                "amb_e": 0.8, "fog": (0.60, 0.68, 0.74, 1), "fog_e": 0.3,
                "fog_d": 0.004, "bright": 1.02, "sat": 1.0,
                "glow_i": 0.6, "glow_b": 0.10},
        "shader": {"warm": (0.90, 0.88, 0.80, 1), "bg": (0.26, 0.30, 0.32, 1),
                   "neon_edge": (0.74, 0.78, 0.68, 1), "neon_lo": (0.32, 0.38, 0.36, 1),
                   "neon_hi": (0.18, 0.22, 0.24, 1), "lim_tint": (0.62, 0.70, 0.58, 1)},
        "lights": list(DAY_TRIO) + [
            # Warm ground-floor windows, chalets W + M (front face y=7)
            ("Chalet_W_Warm", "OmniLight3D", I.format(-7.0, 1.3, -6.8), c(0.95, 0.78, 0.48), 0.9, {"omni_range": 3.0}),
            ("Chalet_M_Warm", "OmniLight3D", I.format(-0.5, 1.3, -6.8), c(0.95, 0.78, 0.48), 0.9, {"omni_range": 3.2}),
        ],
        "mood_strata": ["raw", "morning_bright", "linework", "lithograph",
                        "silent_film_24", "memory_warm"],
    },
    {
        # Flat overcast; desaturated, no practicals — the gray day
        # IS the look.
        "out_path": os.path.join(ROOT, "crumpled_barn.tscn"),
        "uid": "uid://crumpled_barn",
        "root_node": "CrumpledBarn",
        "glb": "res://assets/3d/locales/crumpled_barn.glb",
        "env": {"bg": (0.62, 0.63, 0.64, 1), "amb": (0.55, 0.55, 0.56, 1),
                "amb_e": 0.8, "fog": (0.56, 0.57, 0.58, 1), "fog_e": 0.4,
                "fog_d": 0.006, "sat": 0.85, "glow_i": 0.4, "glow_b": 0.06},
        "shader": {"warm": (0.82, 0.82, 0.78, 1), "bg": (0.28, 0.28, 0.28, 1),
                   "neon_edge": (0.66, 0.66, 0.62, 1), "neon_lo": (0.32, 0.32, 0.30, 1),
                   "neon_hi": (0.18, 0.18, 0.18, 1), "lim_tint": (0.64, 0.62, 0.52, 1)},
        "lights": [
            ("Overcast_Key", "DirectionalLight3D", B_KEY.format(0, 8, 0), c(0.85, 0.86, 0.86), 0.9),
            ("Fill", "DirectionalLight3D", B_FILL.format(-3, 5, 0), c(0.70, 0.70, 0.72), 0.4),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 5, 5), c(0.62, 0.64, 0.68), 0.25),
            # Daylight shaft through the broken roof onto the
            # marionette cabinet + carved sign (interior vantage)
            ("Interior_Shaft", "OmniLight3D", I.format(-0.6, 2.4, -9.8), c(0.88, 0.87, 0.80), 1.1, {"omni_range": 4.0}),
        ],
        "mood_strata": ["raw", "noir", "linework", "lithograph",
                        "silent_film_18", "memory_warm"],
    },
    {
        # 1902 coastal sideshow: cold overcast key, warm bordello
        # windows + porch as practicals, surf rim from the sea.
        "out_path": os.path.join(ROOT, "cliffside_circus.tscn"),
        "uid": "uid://cliffside_circus",
        "root_node": "CliffsideCircus",
        "glb": "res://assets/3d/locales/cliffside_circus.glb",
        "env": {"bg": (0.62, 0.66, 0.68, 1), "amb": (0.52, 0.55, 0.56, 1),
                "amb_e": 0.7, "fog": (0.55, 0.58, 0.60, 1), "fog_e": 0.5,
                "fog_d": 0.008, "sat": 0.88, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.88, 0.80, 0.64, 1), "bg": (0.24, 0.26, 0.27, 1),
                   "neon_edge": (0.72, 0.62, 0.55, 1), "neon_lo": (0.30, 0.24, 0.24, 1),
                   "neon_hi": (0.14, 0.16, 0.17, 1), "lim_tint": (0.66, 0.58, 0.48, 1)},
        "lights": [
            ("Overcast_Key", "DirectionalLight3D", B_KEY.format(0, 9, 0), c(0.80, 0.83, 0.85), 0.85),
            ("Fill", "DirectionalLight3D", B_FILL.format(-3, 5, 0), c(0.72, 0.70, 0.68), 0.35),
            ("Back_Sea", "DirectionalLight3D", B_BACK.format(0, 5, 6), c(0.60, 0.68, 0.74), 0.35),
            # Bordello front: door + the two warm ground windows
            ("Porch_Warm", "OmniLight3D", I.format(-4.0, 1.8, -8.1), c(0.95, 0.72, 0.42), 1.4, {"omni_range": 4.5}),
            ("GWin_W", "OmniLight3D", I.format(-6.2, 1.65, -8.2), c(0.95, 0.72, 0.42), 1.0, {"omni_range": 3.0}),
            ("GWin_E", "OmniLight3D", I.format(-1.8, 1.65, -8.2), c(0.95, 0.72, 0.42), 1.0, {"omni_range": 3.0}),
            # Lantern by the mermaid rail (David's watch post)
            ("Rail_Lantern", "OmniLight3D", I.format(6.1, 1.4, -5.6), c(0.98, 0.80, 0.48), 0.8, {"omni_range": 3.0}),
        ],
        "mood_strata": ["raw", "noir", "ink_blue", "lithograph",
                        "silent_film_18", "memory_warm"],
    },
]


def main():
    for cfg in CONFIGS:
        path = write_locale_tscn(cfg)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
