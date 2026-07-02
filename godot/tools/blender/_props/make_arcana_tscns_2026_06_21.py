"""One-shot driver: writes the .tscn files for the 2026-06-21
Major-Arcana batch (Lovers / Wheel / Temperance / Devil / Moon).

Each .tscn includes the canonical 8 elements per
_VOL5_LOCALES_MANIFEST: WorldEnvironment + three-light foundation
+ GLB + PostProcess (9-shader stack + MoodCycler) +
LiminalProximity + PDPRiffmaster + HUD + DebugMenu.

Run from anywhere — paths are resolved relative to the repo root.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path: sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))  # parent for `from _props ...`

from _props.make_locale_tscn import write_locale_tscn

REPO = os.path.normpath(os.path.join(_HERE, "../../../.."))
SCENES = os.path.join(REPO, "godot/scenes/locales")


def t(x, y, z, rx=0.0, ry=0.0, rz=0.0):
    """Build a Transform3D string. Identity rotation only here — the
    locales' lights point straight down (DirectionalLight3D natively
    -Z) which is fine for a top-down key light when set on a Node3D
    with rotation_x = -1.4. For simplicity we keep most lights
    omni/practical so rotation is irrelevant."""
    return f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})"


def t_keylight(x, y, z, pitch_deg=-55.0, yaw_deg=20.0):
    """Directional key light — pitched down + slightly yawed.
    Returns a basis from XYZ Euler rotation."""
    import math
    p = math.radians(pitch_deg); ya = math.radians(yaw_deg)
    cx, sx = math.cos(p), math.sin(p)
    cy, sy = math.cos(ya), math.sin(ya)
    # Basis = Ry * Rx (Godot uses column-major Transform3D)
    # We'll just hand-write a workable basis.
    bx = (cy, 0, -sy)
    by = (sx*sy, cx, sx*cy)
    bz = (cx*sy, -sx, cx*cy)
    return ("Transform3D("
            f"{bx[0]}, {by[0]}, {bz[0]}, "
            f"{bx[1]}, {by[1]}, {bz[1]}, "
            f"{bx[2]}, {by[2]}, {bz[2]}, "
            f"{x}, {y}, {z})")


# ── Per-locale configs ───────────────────────────────────────────

CONFIGS = [
    {
        "name": "roadside_chapel",
        "uid": "uid://roadside_chapel_locale",
        "root_node": "RoadsideChapel",
        "glb": "res://assets/3d/locales/roadside_chapel.glb",
        # Stone-cool walls, votive-warm pools — leans amber + dust.
        "env": {"bg": (0.10, 0.09, 0.08, 1.0), "amb": (0.62, 0.54, 0.42, 1.0),
                "amb_e": 0.28, "fog": (0.42, 0.36, 0.26, 1.0),
                "fog_e": 0.10, "fog_d": 0.012,
                "bright": 1.0, "cont": 1.04, "sat": 0.88,
                "glow_i": 0.85, "glow_b": 0.16},
        "shader": {"warm": (0.96, 0.62, 0.28, 1.0),
                   "bg":   (0.12, 0.08, 0.06, 1.0),
                   "neon_edge": (0.96, 0.62, 0.28, 1.0),
                   "neon_lo":   (0.42, 0.20, 0.12, 1.0),
                   "neon_hi":   (0.10, 0.06, 0.04, 1.0),
                   "lim_tint":  (0.96, 0.84, 0.62, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D", t_keylight(0.0, 3.5, 6.0, pitch_deg=-60.0),
             "Color(0.94, 0.86, 0.72, 1)", 0.85),
            ("VotiveLight", "OmniLight3D", t(0.0, 5.80, 1.40, 1.0),
             "Color(0.96, 0.62, 0.28, 1)", 1.40),
            ("FillBack", "OmniLight3D", t(0.0, 1.20, 1.80, 1.0),
             "Color(0.62, 0.58, 0.74, 1)", 0.55),
        ],
        "mood_strata": ["votive_dusk", "candlelit", "stonecool_dawn", "sanctuary"],
    },

    {
        "name": "le_roulant_casino",
        "uid": "uid://le_roulant_casino_locale",
        "root_node": "LeRoulantCasino",
        "glb": "res://assets/3d/locales/le_roulant_casino.glb",
        # Maroon + brass — saturated, slightly smokey via fog.
        "env": {"bg": (0.08, 0.06, 0.06, 1.0), "amb": (0.42, 0.24, 0.18, 1.0),
                "amb_e": 0.32, "fog": (0.32, 0.22, 0.18, 1.0),
                "fog_e": 0.14, "fog_d": 0.020,
                "bright": 1.04, "cont": 1.08, "sat": 1.02,
                "glow_i": 1.00, "glow_b": 0.18},
        "shader": {"warm": (0.96, 0.32, 0.42, 1.0),
                   "bg":   (0.10, 0.06, 0.08, 1.0),
                   "neon_edge": (0.96, 0.32, 0.42, 1.0),
                   "neon_lo":   (0.62, 0.18, 0.20, 1.0),
                   "neon_hi":   (0.10, 0.06, 0.08, 1.0),
                   "lim_tint":  (0.96, 0.62, 0.42, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D", t_keylight(0.0, 4.5, 6.0, pitch_deg=-65.0),
             "Color(0.96, 0.86, 0.62, 1)", 0.78),
            ("WheelHotspot", "OmniLight3D", t(0.0, 4.50, 1.80, 1.0),
             "Color(0.96, 0.42, 0.42, 1)", 1.30),
            ("FillBack", "OmniLight3D", t(0.0, 8.00, 2.00, 1.0),
             "Color(0.74, 0.56, 0.28, 1)", 0.65),
        ],
        "mood_strata": ["midnight_glitter", "smokey_room", "neon_pulse", "bust"],
    },

    {
        "name": "mixing_glass",
        "uid": "uid://mixing_glass_locale",
        "root_node": "MixingGlass",
        "glb": "res://assets/3d/locales/mixing_glass.glb",
        # Dark cocktail — copper sconces, amber bottles, no daylight.
        "env": {"bg": (0.06, 0.05, 0.06, 1.0), "amb": (0.22, 0.14, 0.10, 1.0),
                "amb_e": 0.22, "fog": (0.28, 0.18, 0.14, 1.0),
                "fog_e": 0.08, "fog_d": 0.014,
                "bright": 0.96, "cont": 1.10, "sat": 0.94,
                "glow_i": 0.92, "glow_b": 0.14},
        "shader": {"warm": (0.96, 0.62, 0.28, 1.0),
                   "bg":   (0.06, 0.05, 0.06, 1.0),
                   "neon_edge": (0.96, 0.32, 0.42, 1.0),
                   "neon_lo":   (0.42, 0.20, 0.18, 1.0),
                   "neon_hi":   (0.06, 0.05, 0.06, 1.0),
                   "lim_tint":  (0.96, 0.62, 0.42, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D", t_keylight(0.0, 6.0, 5.0, pitch_deg=-50.0),
             "Color(0.92, 0.74, 0.52, 1)", 0.42),
            ("BarPendantHot", "OmniLight3D", t(0.0, 6.20, 1.90, 1.0),
             "Color(0.96, 0.74, 0.42, 1)", 1.10),
            ("BoothCandleFill", "OmniLight3D", t(-1.60, 3.50, 1.20, 1.0),
             "Color(0.96, 0.52, 0.32, 1)", 0.60),
        ],
        "mood_strata": ["amber_pour", "low_jazz", "midnight_observation", "stripped"],
    },

    {
        "name": "daigles_roadhouse",
        "uid": "uid://daigles_roadhouse_locale",
        "root_node": "DaiglesRoadhouse",
        "glb": "res://assets/3d/locales/daigles_roadhouse.glb",
        # Honky-tonk fluorescents + neon — sickly but bright.
        "env": {"bg": (0.10, 0.08, 0.06, 1.0), "amb": (0.42, 0.36, 0.24, 1.0),
                "amb_e": 0.40, "fog": (0.36, 0.30, 0.22, 1.0),
                "fog_e": 0.10, "fog_d": 0.014,
                "bright": 1.02, "cont": 1.06, "sat": 1.00,
                "glow_i": 0.78, "glow_b": 0.12},
        "shader": {"warm": (0.96, 0.62, 0.28, 1.0),
                   "bg":   (0.10, 0.08, 0.06, 1.0),
                   "neon_edge": (0.96, 0.34, 0.20, 1.0),
                   "neon_lo":   (0.42, 0.20, 0.16, 1.0),
                   "neon_hi":   (0.10, 0.08, 0.06, 1.0),
                   "lim_tint":  (0.96, 0.74, 0.42, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D", t_keylight(0.0, 3.5, 5.0, pitch_deg=-55.0),
             "Color(0.96, 0.86, 0.62, 1)", 0.75),
            ("SchlitzNeon", "OmniLight3D", t(0.0, 7.00, 2.20, 1.0),
             "Color(0.96, 0.34, 0.20, 1)", 1.10),
            ("PoolLight", "OmniLight3D", t(1.50, 3.20, 1.80, 1.0),
             "Color(0.96, 0.86, 0.62, 1)", 0.85),
        ],
        "mood_strata": ["humid_midnight", "neon_sweat", "honky_tonk", "last_call"],
    },

    {
        "name": "static_drive_in",
        "uid": "uid://static_drive_in_locale",
        "root_node": "StaticDriveIn",
        "glb": "res://assets/3d/locales/static_drive_in.glb",
        # Moonlit night exterior visible — sky/cool with concession-
        # warmth inside. Fluorescents fill, blue moon outside.
        "env": {"bg": (0.08, 0.10, 0.16, 1.0), "amb": (0.32, 0.36, 0.46, 1.0),
                "amb_e": 0.30, "fog": (0.30, 0.36, 0.46, 1.0),
                "fog_e": 0.14, "fog_d": 0.010,
                "bright": 0.98, "cont": 1.08, "sat": 0.92,
                "glow_i": 0.96, "glow_b": 0.18},
        "shader": {"warm": (0.96, 0.62, 0.28, 1.0),
                   "bg":   (0.10, 0.12, 0.22, 1.0),
                   "neon_edge": (0.62, 0.78, 0.96, 1.0),
                   "neon_lo":   (0.20, 0.28, 0.42, 1.0),
                   "neon_hi":   (0.10, 0.12, 0.22, 1.0),
                   "lim_tint":  (0.62, 0.74, 0.96, 1.0)},
        "lights": [
            ("MoonKey", "DirectionalLight3D", t_keylight(0.0, 8.0, 8.0, pitch_deg=-45.0),
             "Color(0.62, 0.74, 0.96, 1)", 0.55),
            ("SnackbarPracticalWarm", "OmniLight3D", t(0.0, 2.50, 2.30, 1.0),
             "Color(0.96, 0.86, 0.62, 1)", 1.10),
            ("MarqueePulse", "OmniLight3D", t(0.0, 1.20, 2.50, 1.0),
             "Color(0.96, 0.32, 0.42, 1)", 0.65),
        ],
        "mood_strata": ["moonlit_static", "marquee_flicker", "show_starting", "after_credits"],
    },
]


def main():
    written = []
    for cfg in CONFIGS:
        out = os.path.join(SCENES, cfg["name"] + ".tscn")
        cfg["out_path"] = out
        write_locale_tscn(cfg)
        written.append(out)
        print(f"  ✓ {out}")
    print(f"\nwrote {len(written)} locale .tscn files")


if __name__ == "__main__":
    main()
