"""One-shot: locale tscns for the vols 1-4 sets built 2026-10-17 (draft 1).

The user: "go ahead and start working on backgrounds for vol 1-4 as needed."
Same contract as make_vol1_4_tscns_2026_10_16.py: write_locale_tscn with
full parity; light positions come from the builder's geometry (blender
(x, y, z) -> godot (x, z, -y)); a light named `<name>__<preset>` plays only
in that preset (Background3D drops it everywhere else). Run with plain
python3 from the repo root.
"""
import os, sys
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))

I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
B_BACK = "Transform3D(0.707, -0.5, 0.5, 0, 0.707, 0.707, -0.707, -0.5, 0.5, {}, {}, {})"
# travels SOUTH (godot +z, in from north windows), 45 deg down — checked by light_direction_audit
B_KEY_FROM_N = "Transform3D(-1, 0, 0, 0, 0.707, 0.707, 0, 0.707, -0.707, {}, {}, {})"
# travels NORTH (godot -z, in through south windows), 45 deg down
B_SUN_FROM_S = "Transform3D(1, 0, 0, 0, 0.707, 0.707, 0, -0.707, 0.707, {}, {}, {})"


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


NIGHT_BED = ("andy_house_bedroom_night", "andy_house_bedroom_lamp")

CONFIGS = [
    {
        # VOL 3's LINK HOUSE (build_link_house.py): a ranch house in Texas
        # after dark — every room on its own lamps. The day presets
        # (bathroom, bedroom) add their window light by name and lift the
        # environment in Background3D.
        "out_path": os.path.join(ROOT, "link_house.tscn"),
        "uid": "uid://link_house_v3",
        "root_node": "LinkHouse",
        "glb": "res://assets/3d/locales/link_house.glb",
        "env": {"bg": (0.04, 0.05, 0.08, 1), "amb": (0.40, 0.42, 0.52, 1),
                "amb_e": 0.40, "fog": (0.16, 0.17, 0.22, 1), "fog_e": 0.25,
                "fog_d": 0.003, "sat": 0.94, "glow_i": 0.65, "glow_b": 0.12},
        "shader": {"warm": (0.94, 0.84, 0.64, 1), "bg": (0.08, 0.08, 0.10, 1),
                   "neon_edge": (0.74, 0.64, 0.44, 1), "neon_lo": (0.30, 0.24, 0.18, 1),
                   "neon_hi": (0.08, 0.08, 0.10, 1), "lim_tint": (0.70, 0.58, 0.42, 1)},
        "lights": [
            ("Key_Night", "DirectionalLight3D", B_KEY_FROM_N.format(0, 6, -12), c(0.52, 0.58, 0.80), 0.22),
            ("Fill_Room", "DirectionalLight3D", B_FILL.format(0, 3, -5), c(0.70, 0.62, 0.52), 0.14),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 0), c(0.40, 0.42, 0.56), 0.10),
            # the living room's end-table lamp (blender (-3.30, 4.25, 1.03))
            ("Practical_LivingLamp", "OmniLight3D", I.format(-3.30, 1.03, -4.25), c(1.0, 0.84, 0.58), 1.3,
             {"omni_range": 4.5}),
            # the TV's screen, on in the living-room night (the scary movie marathon)
            ("TV_Glow__andy_house_living", "OmniLight3D", I.format(-5.70, 0.95, -2.80), c(0.56, 0.70, 1.0), 1.6,
             {"omni_range": 4.2}),
            # the pendant over the dining table (blender (4.10, 2.20, 1.75))
            ("Practical_Pendant", "OmniLight3D", I.format(4.10, 1.70, -2.20), c(1.0, 0.82, 0.56), 1.6,
             {"omni_range": 4.5}),
            ("Practical_KitchenCeiling", "OmniLight3D", I.format(3.40, 2.40, -3.80), c(1.0, 0.94, 0.84), 0.9,
             {"omni_range": 5.0}),
            ("Practical_Hall", "OmniLight3D", I.format(0.0, 2.40, -6.10), c(1.0, 0.92, 0.78), 0.7,
             {"omni_range": 4.0}),
            # the vanity's light bar (blender (1.39, 8.35, 1.95))
            ("Practical_Vanity", "OmniLight3D", I.format(1.25, 1.95, -8.35), c(1.0, 0.94, 0.82), 1.4,
             {"omni_range": 3.6}),
            # Andy's room at night: the bedside lamp (blender (6.16, 9.45, 0.97)), the desk lamp
            *[("Lamp_Bed__" + p, "OmniLight3D", I.format(6.10, 1.0, -9.40), c(1.0, 0.82, 0.54), 1.2,
               {"omni_range": 3.8}) for p in NIGHT_BED],
            *[("Lamp_Desk__" + p, "OmniLight3D", I.format(4.48, 1.06, -10.10), c(0.96, 0.92, 0.80), 0.6,
               {"omni_range": 2.6}) for p in NIGHT_BED],
            # the day presets: window light by name
            ("Sky_N__andy_house_bedroom", "DirectionalLight3D", B_KEY_FROM_N.format(4, 4, -12), c(0.90, 0.92, 1.0), 0.75),
            ("Window_N__andy_house_bedroom", "OmniLight3D", I.format(4.0, 1.6, -9.9), c(0.92, 0.94, 1.0), 1.6,
             {"omni_range": 5.5}),
            ("Window_N__andy_house_bath", "OmniLight3D", I.format(-0.30, 1.8, -10.0), c(0.96, 0.96, 0.98), 2.2,
             {"omni_range": 4.5}),
            ("Sun_S__andy_house_kitchen", "DirectionalLight3D", B_SUN_FROM_S.format(2, 6, 6), c(1.0, 0.70, 0.46), 0.35),
        ],
        "mood_strata": ["raw", "memory_warm", "lithograph", "noir",
                        "candlelight", "silent_film_18"],
    },
    {
        # VOL 2's SMALL WOOD RANCH (build_small_wood_ranch.py): the
        # narrator's room at night — the reading lamp and the moon through
        # the plank blinds; the second house (x 30..34) on its kerosene
        # lamp. "The same afternoon" (Dean's rebuilt room) is the day
        # preset: its sky and window light by name.
        "out_path": os.path.join(ROOT, "small_wood_ranch.tscn"),
        "uid": "uid://small_wood_ranch_v2",
        "root_node": "SmallWoodRanch",
        "glb": "res://assets/3d/locales/small_wood_ranch.glb",
        "env": {"bg": (0.03, 0.04, 0.07, 1), "amb": (0.36, 0.40, 0.52, 1),
                "amb_e": 0.38, "fog": (0.14, 0.16, 0.22, 1), "fog_e": 0.3,
                "fog_d": 0.004, "sat": 0.90, "glow_i": 0.7, "glow_b": 0.12},
        "shader": {"warm": (0.92, 0.82, 0.62, 1), "bg": (0.07, 0.08, 0.10, 1),
                   "neon_edge": (0.70, 0.62, 0.44, 1), "neon_lo": (0.28, 0.24, 0.18, 1),
                   "neon_hi": (0.07, 0.08, 0.10, 1), "lim_tint": (0.62, 0.58, 0.48, 1)},
        "lights": [
            ("Key_Moon", "DirectionalLight3D", B_KEY_FROM_N.format(0, 6, -8), c(0.60, 0.68, 0.92), 0.28),
            ("Fill_Room", "DirectionalLight3D", B_FILL.format(0, 3, -2), c(0.62, 0.58, 0.54), 0.12),
            ("Back", "DirectionalLight3D", B_BACK.format(0, 3, 1), c(0.40, 0.44, 0.58), 0.10),
            # the reading lamp on the nightstand (blender (-0.45, 3.92, 0.91)), the night presets
            *[("Lamp_Reading__" + p, "OmniLight3D", I.format(-0.45, 0.92, -3.90), c(1.0, 0.82, 0.54), 1.3,
               {"omni_range": 3.6}) for p in ("ranch_bedroom_night", "ranch_bedroom_lamp")],
            # the moon at the N window
            *[("Moon_Window__" + p, "OmniLight3D", I.format(0.20, 1.5, -3.95), c(0.62, 0.70, 0.96), 0.8,
               {"omni_range": 3.4}) for p in ("ranch_bedroom_night", "ranch_bedroom_lamp")],
            # the afternoon: sky through the N window
            ("Sky_N__ranch_bedroom_day", "DirectionalLight3D", B_KEY_FROM_N.format(0, 6, -8), c(0.92, 0.94, 1.0), 0.7),
            ("Window_N__ranch_bedroom_day", "OmniLight3D", I.format(0.20, 1.5, -3.85), c(0.92, 0.94, 1.0), 1.8,
             {"omni_range": 5.0}),
            # the second house: the kerosene lamp on its crate (blender (31.95, 1.70, 0.55)),
            # the cold through the gone E window
            ("Kerosene_Lamp", "OmniLight3D", I.format(31.95, 0.62, -1.70), c(1.0, 0.70, 0.36), 1.8,
             {"omni_range": 4.6}),
            ("Window_Gone_E", "OmniLight3D", I.format(33.70, 1.40, -1.80), c(0.56, 0.64, 0.90), 0.5,
             {"omni_range": 2.6}),
        ],
        "mood_strata": ["raw", "memory_warm", "noir", "candlelight",
                        "lithograph", "silent_film_18"],
    },
]


def main():
    for cfg in CONFIGS:
        path = write_locale_tscn(cfg)
        print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    main()
