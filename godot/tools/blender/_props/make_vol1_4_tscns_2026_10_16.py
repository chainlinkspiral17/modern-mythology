"""One-shot: locale tscns for the vols 1-4 sets (2026-10-16, draft 1).

The user: "Let's move back to background and model work for all the new vol
1-4 stuff." Writes godot/scenes/locales/<set>.tscn via write_locale_tscn
(full 8-element parity). Light positions come from the matching
build_<set>.py geometry (blender (x,y,z) -> godot (x,z,-y)). Run with plain
python3 from the repo root; add each new vol 1-4 set's config here.
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
# a key that travels SOUTH (godot +z, in from a north window) and 45 deg DOWN.
# (B_KEY above, copied from the 2026-08-03 generator, aims 45 deg UP by
# light_direction_audit's row-major reading — the audit caught it here.)
B_KEY_FROM_N = "Transform3D(-1, 0, 0, 0, 0.707, 0.707, 0, 0.707, -0.707, {}, {}, {})"
# a sun that travels NORTH (godot -z, in through south windows) and 45 deg DOWN
B_SUN_FROM_S = "Transform3D(1, 0, 0, 0, 0.707, 0.707, 0, -0.707, 0.707, {}, {}, {})"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


CONFIGS = [
    {
        # VOL 4's SCRAPBOOK DESK at night (build_writers_desk.py): the
        # green desk lamp is the room; the street's sodium comes through
        # the N window onto the corkboard; a low cool key so the room's
        # far side does not drop to black. Dawn is a preset env override
        # plus its own window light (Dawn_Window__writers_desk_dawn).
        "out_path": os.path.join(ROOT, "writers_desk.tscn"),
        "uid": "uid://writers_desk_v4",
        "root_node": "WritersDesk",
        "glb": "res://assets/3d/locales/writers_desk.glb",
        "env": {"bg": (0.05, 0.05, 0.07, 1), "amb": (0.42, 0.44, 0.54, 1),
                "amb_e": 0.45, "fog": (0.20, 0.20, 0.26, 1), "fog_e": 0.3,
                "fog_d": 0.004, "sat": 0.92, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.94, 0.84, 0.62, 1), "bg": (0.08, 0.08, 0.10, 1),
                   "neon_edge": (0.72, 0.62, 0.40, 1), "neon_lo": (0.30, 0.24, 0.16, 1),
                   "neon_hi": (0.08, 0.08, 0.10, 1), "lim_tint": (0.70, 0.56, 0.40, 1)},
        "lights": [
            ("Key_Window", "DirectionalLight3D", B_KEY_FROM_N.format(0, 5, -7), c(0.56, 0.62, 0.82), 0.30),
            ("Fill_Room", "DirectionalLight3D", B_FILL.format(0, 3, 0), c(0.70, 0.62, 0.52), 0.16),
            ("Back", "DirectionalLight3D", B_BACK.format(-2, 3, 2), c(0.40, 0.42, 0.56), 0.12),
            # the desk lamp's bulb (blender (-0.98, 5.31, 1.035))
            ("Practical_DeskLamp", "OmniLight3D", I.format(-0.98, 1.03, -5.31), c(1.0, 0.86, 0.58), 1.6,
             {"omni_range": 3.2}),
            # the streetlight beyond the N window (blender (1.25, 6.4, 2.6))
            # night presets only (the dawn has no sodium): one copy per preset, `__<preset>`
            ("Street_Sodium__writers_desk", "OmniLight3D", I.format(1.25, 2.6, -6.6), c(1.0, 0.66, 0.30), 1.6,
             {"omni_range": 5.5}),
            ("Street_Sodium__writers_desk_board", "OmniLight3D", I.format(1.25, 2.6, -6.6), c(1.0, 0.66, 0.30), 1.6,
             {"omni_range": 5.5}),
            ("Street_Sodium__writers_desk_room", "OmniLight3D", I.format(1.25, 2.6, -6.6), c(1.0, 0.66, 0.30), 1.6,
             {"omni_range": 5.5}),
            # dawn only: the window's grey-blue morning (Background3D drops
            # `__<preset>` lights for every other preset)
            ("Dawn_Window__writers_desk_dawn", "OmniLight3D", I.format(1.25, 1.7, -5.0),
             c(0.86, 0.88, 0.98), 3.0, {"omni_range": 7.0}),
            ("Dawn_Sky__writers_desk_dawn", "DirectionalLight3D", B_KEY_FROM_N.format(0, 5, -7), c(0.78, 0.80, 0.92), 0.55),
        ],
        "mood_strata": ["raw", "noir", "lithograph", "macro_haze",
                        "silent_film_18", "candlelight", "memory_warm"],
    },
    {
        # THE SCHOOL (build_small_wood_high.py): a school day — the sun in
        # through the south rooms' windows, fluorescents everywhere else, the
        # gym's high-bays. Blender (x, y, z) -> godot (x, z, -y).
        "out_path": os.path.join(ROOT, "small_wood_high.tscn"),
        "uid": "uid://small_wood_high_v24",
        "root_node": "SmallWoodHigh",
        "glb": "res://assets/3d/locales/small_wood_high.glb",
        "env": {"bg": (0.62, 0.70, 0.80, 1), "amb": (0.70, 0.70, 0.68, 1),
                "amb_e": 0.75, "fog": (0.62, 0.66, 0.70, 1), "fog_e": 0.25,
                "fog_d": 0.002, "sat": 0.92, "glow_i": 0.55, "glow_b": 0.10},
        "shader": {"warm": (0.92, 0.90, 0.80, 1), "bg": (0.22, 0.24, 0.26, 1),
                   "neon_edge": (0.70, 0.74, 0.70, 1), "neon_lo": (0.30, 0.32, 0.30, 1),
                   "neon_hi": (0.12, 0.14, 0.16, 1), "lim_tint": (0.62, 0.66, 0.60, 1)},
        "lights": [
            ("Sun_Key", "DirectionalLight3D", B_SUN_FROM_S.format(0, 12, 12), c(1.0, 0.95, 0.84), 0.85),
            ("Fill_Sky", "DirectionalLight3D", B_FILL.format(0, 8, 0), c(0.70, 0.76, 0.86), 0.25),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 8, -8), c(0.74, 0.78, 0.86), 0.18),
            # the hall's tubes (blender y 1.6, z 3.0)
            ("Hall_Tubes_W", "OmniLight3D", I.format(-16, 2.7, -1.6), c(0.94, 0.96, 1.0), 1.2, {"omni_range": 9.0}),
            ("Hall_Tubes_C", "OmniLight3D", I.format(0, 2.7, -1.6), c(0.94, 0.96, 1.0), 1.2, {"omni_range": 9.0}),
            ("Hall_Tubes_E", "OmniLight3D", I.format(16, 2.7, -1.6), c(0.94, 0.96, 1.0), 1.2, {"omni_range": 9.0}),
            # the gym's high-bays (blender court centre (-9, 12.2), z 6.6)
            ("Gym_HighBay_W", "OmniLight3D", I.format(-17, 6.4, -12.2), c(1.0, 0.96, 0.86), 2.2, {"omni_range": 13.0}),
            ("Gym_HighBay_C", "OmniLight3D", I.format(-8, 6.4, -12.2), c(1.0, 0.96, 0.86), 2.2, {"omni_range": 13.0}),
            ("Gym_HighBay_E", "OmniLight3D", I.format(0, 6.4, -12.2), c(1.0, 0.96, 0.86), 2.0, {"omni_range": 12.0}),
            ("Lock_Tubes", "OmniLight3D", I.format(9, 2.7, -7.2), c(0.92, 0.96, 1.0), 1.1, {"omni_range": 7.0}),
            # one per south room (blender y -4.5)
            ("Class_Tubes", "OmniLight3D", I.format(-9, 2.7, 4.5), c(0.94, 0.96, 1.0), 1.1, {"omni_range": 7.5}),
            ("Art_Tubes", "OmniLight3D", I.format(1, 2.7, 4.5), c(0.96, 0.96, 0.98), 1.1, {"omni_range": 7.5}),
            ("Lab_Tubes", "OmniLight3D", I.format(11, 2.7, 4.5), c(0.90, 0.94, 1.0), 1.0, {"omni_range": 7.5}),
        ],
        "mood_strata": ["raw", "morning_bright", "lithograph", "noir",
                        "silent_film_24", "memory_warm"],
    },
]


def main():
    for cfg in CONFIGS:
        path = write_locale_tscn(cfg)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
