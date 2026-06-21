"""Third batch — finishes the Major Arcana sweep:
XIII Death / XVI Tower / XVII Star / XIX Sun / XX Judgement /
XXI World.

Same canonical 8-element locale .tscn stack via write_locale_tscn.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path: sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from _props.make_locale_tscn import write_locale_tscn

REPO = os.path.normpath(os.path.join(_HERE, "../../../.."))
SCENES = os.path.join(REPO, "godot/scenes/locales")


def t(x, y, z, *_):
    return f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})"


def t_keylight(x, y, z, pitch_deg=-55.0, yaw_deg=20.0):
    import math
    p = math.radians(pitch_deg); ya = math.radians(yaw_deg)
    cx, sx = math.cos(p), math.sin(p)
    cy, sy = math.cos(ya), math.sin(ya)
    bx = (cy, 0, -sy)
    by = (sx*sy, cx, sx*cy)
    bz = (cx*sy, -sx, cx*cy)
    return ("Transform3D("
            f"{bx[0]}, {by[0]}, {bz[0]}, "
            f"{bx[1]}, {by[1]}, {bz[1]}, "
            f"{bx[2]}, {by[2]}, {bz[2]}, "
            f"{x}, {y}, {z})")


CONFIGS = [
    # ── XIII DEATH — Asylum Ward C ───────────────────────────────
    {
        "name": "asylum_ward_c",
        "uid": "uid://asylum_ward_c_locale",
        "root_node": "AsylumWardC",
        "glb": "res://assets/3d/locales/asylum_ward_c.glb",
        # Faded-green-tile corridor under sickly fluorescents.
        "env": {"bg": (0.08, 0.10, 0.08, 1.0), "amb": (0.42, 0.52, 0.46, 1.0),
                "amb_e": 0.34, "fog": (0.30, 0.42, 0.34, 1.0),
                "fog_e": 0.12, "fog_d": 0.018,
                "bright": 0.96, "cont": 1.10, "sat": 0.84,
                "glow_i": 0.85, "glow_b": 0.16},
        "shader": {"warm": (0.86, 0.96, 0.86, 1.0),
                   "bg":   (0.08, 0.10, 0.08, 1.0),
                   "neon_edge": (0.62, 0.86, 0.62, 1.0),
                   "neon_lo":   (0.32, 0.46, 0.32, 1.0),
                   "neon_hi":   (0.08, 0.10, 0.08, 1.0),
                   "lim_tint":  (0.96, 0.86, 0.62, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D",
             t_keylight(0.0, 7.0, 6.0, pitch_deg=-65.0),
             "Color(0.86, 0.92, 0.84, 1)", 0.62),
            ("CorridorFluor", "OmniLight3D", t(0.0, 7.00, 3.20),
             "Color(0.86, 0.96, 0.86, 1)", 0.95),
            ("CupolaBlue", "OmniLight3D", t(0.0, 13.20, 4.40),
             "Color(0.62, 0.78, 0.92, 1)", 0.55),
        ],
        "mood_strata": ["fluorescent_dim", "walpurgisnacht", "ward_silence", "ward_c"],
    },

    # ── XVI TOWER — WGUR Transmitter Shack ───────────────────────
    {
        "name": "wgur_transmitter_shack",
        "uid": "uid://wgur_transmitter_shack_locale",
        "root_node": "WgurTransmitterShack",
        "glb": "res://assets/3d/locales/wgur_transmitter_shack.glb",
        # VU-glow amber inside, red obstruction pulses outside.
        "env": {"bg": (0.04, 0.04, 0.08, 1.0), "amb": (0.32, 0.30, 0.34, 1.0),
                "amb_e": 0.28, "fog": (0.22, 0.20, 0.26, 1.0),
                "fog_e": 0.12, "fog_d": 0.014,
                "bright": 0.96, "cont": 1.10, "sat": 0.94,
                "glow_i": 0.92, "glow_b": 0.16},
        "shader": {"warm": (0.96, 0.86, 0.42, 1.0),
                   "bg":   (0.04, 0.04, 0.08, 1.0),
                   "neon_edge": (0.96, 0.32, 0.20, 1.0),
                   "neon_lo":   (0.32, 0.20, 0.18, 1.0),
                   "neon_hi":   (0.04, 0.04, 0.08, 1.0),
                   "lim_tint":  (0.96, 0.74, 0.42, 1.0)},
        "lights": [
            ("WindowMoonKey", "DirectionalLight3D",
             t_keylight(0.0, 4.0, 5.0, pitch_deg=-40.0),
             "Color(0.62, 0.74, 0.92, 1)", 0.42),
            ("VUMeterAmber", "OmniLight3D", t(-2.0, 2.50, 1.50),
             "Color(0.96, 0.86, 0.42, 1)", 1.00),
            ("ObstructionPulseRed", "OmniLight3D", t(2.0, 14.0, 9.0),
             "Color(0.96, 0.18, 0.18, 1)", 0.85),
        ],
        "mood_strata": ["carrier_steady", "obstruction_pulse", "dead_air", "broadcast_on"],
    },

    # ── XVII STAR — Christian Ice Co. ────────────────────────────
    {
        "name": "christian_ice_co",
        "uid": "uid://christian_ice_co_locale",
        "root_node": "ChristianIceCo",
        "glb": "res://assets/3d/locales/christian_ice_co.glb",
        # Cool blue-white interior, fluorescents tinted cyan.
        "env": {"bg": (0.86, 0.94, 0.96, 1.0), "amb": (0.62, 0.78, 0.82, 1.0),
                "amb_e": 0.48, "fog": (0.78, 0.88, 0.92, 1.0),
                "fog_e": 0.14, "fog_d": 0.008,
                "bright": 1.04, "cont": 1.02, "sat": 0.88,
                "glow_i": 0.92, "glow_b": 0.16},
        "shader": {"warm": (0.78, 0.92, 0.96, 1.0),
                   "bg":   (0.86, 0.94, 0.96, 1.0),
                   "neon_edge": (0.62, 0.84, 0.96, 1.0),
                   "neon_lo":   (0.42, 0.62, 0.78, 1.0),
                   "neon_hi":   (0.92, 0.96, 0.98, 1.0),
                   "lim_tint":  (0.62, 0.86, 0.96, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D",
             t_keylight(0.0, 5.5, 7.0, pitch_deg=-60.0),
             "Color(0.92, 0.96, 0.98, 1)", 0.92),
            ("IceLetterGlow", "OmniLight3D", t(0.0, -1.40, 4.50),
             "Color(0.78, 0.92, 0.96, 1)", 1.10),
            ("FreezerCool", "OmniLight3D", t(0.0, 3.80, 1.40),
             "Color(0.62, 0.86, 0.96, 1)", 0.65),
        ],
        "mood_strata": ["bright_cold", "evening_glow", "shut_down", "glass_skin"],
    },

    # ── XIX SUN — Solenade Memorial Garden ───────────────────────
    {
        "name": "solenade_garden",
        "uid": "uid://solenade_garden_locale",
        "root_node": "SolenadeGarden",
        "glb": "res://assets/3d/locales/solenade_garden.glb",
        # Open warm noon, lush green, slight sky glow.
        "env": {"bg": (0.62, 0.78, 0.86, 1.0), "amb": (0.74, 0.78, 0.62, 1.0),
                "amb_e": 0.70, "fog": (0.78, 0.84, 0.74, 1.0),
                "fog_e": 0.10, "fog_d": 0.004,
                "bright": 1.08, "cont": 1.00, "sat": 0.96,
                "glow_i": 0.85, "glow_b": 0.12},
        "shader": {"warm": (0.96, 0.86, 0.42, 1.0),
                   "bg":   (0.62, 0.78, 0.86, 1.0),
                   "neon_edge": (0.96, 0.74, 0.32, 1.0),
                   "neon_lo":   (0.62, 0.74, 0.42, 1.0),
                   "neon_hi":   (0.86, 0.92, 0.84, 1.0),
                   "lim_tint":  (0.96, 0.86, 0.62, 1.0)},
        "lights": [
            ("Sun", "DirectionalLight3D",
             t_keylight(0.0, 0.0, 14.0, pitch_deg=-70.0, yaw_deg=30.0),
             "Color(0.98, 0.94, 0.82, 1)", 1.50),
            ("BounceWarm", "OmniLight3D", t(0.0, 0.0, 1.20),
             "Color(0.96, 0.84, 0.62, 1)", 0.55),
            ("LeafFill", "OmniLight3D", t(0.0, 0.0, 5.20),
             "Color(0.74, 0.86, 0.62, 1)", 0.40),
        ],
        "mood_strata": ["high_noon", "dust_motes", "shaded_afternoon", "long_light"],
    },

    # ── XX JUDGEMENT — Parish Cemetery ───────────────────────────
    {
        "name": "parish_cemetery",
        "uid": "uid://parish_cemetery_locale",
        "root_node": "ParishCemetery",
        "glb": "res://assets/3d/locales/parish_cemetery.glb",
        # Bleached white tomb city, overcast sky, brass lamp warmth.
        "env": {"bg": (0.74, 0.78, 0.80, 1.0), "amb": (0.62, 0.62, 0.58, 1.0),
                "amb_e": 0.48, "fog": (0.74, 0.74, 0.70, 1.0),
                "fog_e": 0.16, "fog_d": 0.006,
                "bright": 0.98, "cont": 1.06, "sat": 0.82,
                "glow_i": 0.78, "glow_b": 0.12},
        "shader": {"warm": (0.96, 0.86, 0.62, 1.0),
                   "bg":   (0.74, 0.78, 0.80, 1.0),
                   "neon_edge": (0.86, 0.74, 0.42, 1.0),
                   "neon_lo":   (0.62, 0.58, 0.50, 1.0),
                   "neon_hi":   (0.86, 0.86, 0.80, 1.0),
                   "lim_tint":  (0.96, 0.84, 0.62, 1.0)},
        "lights": [
            ("OvercastKey", "DirectionalLight3D",
             t_keylight(0.0, 0.0, 12.0, pitch_deg=-65.0),
             "Color(0.92, 0.92, 0.88, 1)", 0.85),
            ("LampGlow_Center", "OmniLight3D", t(0.0, 0.0, 3.00),
             "Color(0.96, 0.86, 0.42, 1)", 0.65),
            ("MausoleumBounce", "OmniLight3D", t(0.0, 0.0, 1.20),
             "Color(0.86, 0.84, 0.78, 1)", 0.40),
        ],
        "mood_strata": ["all_souls", "lamp_lit_dusk", "white_noon", "everyone_stays"],
    },

    # ── XXI WORLD — Frog Knows Best ──────────────────────────────
    {
        "name": "frog_knows_best",
        "uid": "uid://frog_knows_best_locale",
        "root_node": "FrogKnowsBest",
        "glb": "res://assets/3d/locales/frog_knows_best.glb",
        # Wood shop interior, tank-aqua key + porch-green fill.
        "env": {"bg": (0.18, 0.20, 0.18, 1.0), "amb": (0.52, 0.56, 0.42, 1.0),
                "amb_e": 0.40, "fog": (0.42, 0.50, 0.38, 1.0),
                "fog_e": 0.14, "fog_d": 0.012,
                "bright": 1.02, "cont": 1.04, "sat": 0.96,
                "glow_i": 0.88, "glow_b": 0.14},
        "shader": {"warm": (0.96, 0.74, 0.32, 1.0),
                   "bg":   (0.18, 0.20, 0.18, 1.0),
                   "neon_edge": (0.32, 0.86, 0.62, 1.0),
                   "neon_lo":   (0.32, 0.46, 0.30, 1.0),
                   "neon_hi":   (0.18, 0.20, 0.18, 1.0),
                   "lim_tint":  (0.62, 0.96, 0.74, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D",
             t_keylight(0.0, 3.0, 5.0, pitch_deg=-55.0),
             "Color(0.96, 0.92, 0.78, 1)", 0.85),
            ("TankAqua", "OmniLight3D", t(0.0, 6.20, 1.40),
             "Color(0.42, 0.86, 0.96, 1)", 1.00),
            ("PorchGreen", "OmniLight3D", t(0.0, -1.40, 2.20),
             "Color(0.62, 0.86, 0.62, 1)", 0.55),
        ],
        "mood_strata": ["bayou_humid", "tank_aqua", "porch_screen", "loop_completed"],
    },
]


def main():
    for cfg in CONFIGS:
        out = os.path.join(SCENES, cfg["name"] + ".tscn")
        cfg["out_path"] = out
        write_locale_tscn(cfg)
        print(f"  ✓ {out}")
    print(f"\nwrote {len(CONFIGS)} locale .tscn files")


if __name__ == "__main__":
    main()
