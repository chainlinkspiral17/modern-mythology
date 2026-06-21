"""Second batch: VII Chariot / VIII Strength / IX Hermit /
XI Justice / XII Hanged Man.

Mirror of the first-batch driver — same canonical 8-element
locale .tscn stack via write_locale_tscn.
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
    # ── VII CHARIOT — Old Lacombe Service Garage ─────────────────
    {
        "name": "lacombe_service_garage",
        "uid": "uid://lacombe_service_garage_locale",
        "root_node": "LacombeServiceGarage",
        "glb": "res://assets/3d/locales/lacombe_service_garage.glb",
        # Bright fluorescent garage — neutral concrete + warm pole-sign neon.
        "env": {"bg": (0.10, 0.10, 0.10, 1.0), "amb": (0.42, 0.40, 0.36, 1.0),
                "amb_e": 0.40, "fog": (0.36, 0.34, 0.30, 1.0),
                "fog_e": 0.10, "fog_d": 0.010,
                "bright": 1.04, "cont": 1.04, "sat": 0.94,
                "glow_i": 0.72, "glow_b": 0.10},
        "shader": {"warm": (0.96, 0.74, 0.32, 1.0),
                   "bg":   (0.10, 0.10, 0.10, 1.0),
                   "neon_edge": (0.96, 0.62, 0.20, 1.0),
                   "neon_lo":   (0.42, 0.32, 0.18, 1.0),
                   "neon_hi":   (0.10, 0.10, 0.10, 1.0),
                   "lim_tint":  (0.96, 0.84, 0.62, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D",
             t_keylight(0.0, 4.5, 7.0, pitch_deg=-60.0),
             "Color(0.96, 0.94, 0.86, 1)", 0.85),
            ("BayWorkLight", "OmniLight3D", t(0.0, 4.50, 2.20),
             "Color(0.96, 0.92, 0.74, 1)", 1.40),
            ("PoleSignNeon", "OmniLight3D", t(0.0, -4.00, 5.80),
             "Color(0.96, 0.34, 0.20, 1)", 0.55),
        ],
        "mood_strata": ["work_lights", "highway_noon", "engine_warm", "out_of_gas"],
    },

    # ── VIII STRENGTH — Abandoned Carnival Lot ───────────────────
    {
        "name": "carnival_lot",
        "uid": "uid://carnival_lot_locale",
        "root_node": "CarnivalLot",
        "glb": "res://assets/3d/locales/carnival_lot.glb",
        # Sun-bleached outdoor — washed warm with cool sky.
        "env": {"bg": (0.74, 0.78, 0.78, 1.0), "amb": (0.62, 0.58, 0.48, 1.0),
                "amb_e": 0.62, "fog": (0.78, 0.74, 0.62, 1.0),
                "fog_e": 0.14, "fog_d": 0.006,
                "bright": 1.06, "cont": 0.96, "sat": 0.82,
                "glow_i": 0.65, "glow_b": 0.08},
        "shader": {"warm": (0.96, 0.74, 0.42, 1.0),
                   "bg":   (0.78, 0.78, 0.72, 1.0),
                   "neon_edge": (0.74, 0.42, 0.28, 1.0),
                   "neon_lo":   (0.62, 0.42, 0.30, 1.0),
                   "neon_hi":   (0.86, 0.82, 0.74, 1.0),
                   "lim_tint":  (0.96, 0.86, 0.62, 1.0)},
        "lights": [
            ("Sun", "DirectionalLight3D",
             t_keylight(0.0, 0.0, 10.0, pitch_deg=-50.0, yaw_deg=30.0),
             "Color(0.98, 0.92, 0.78, 1)", 1.30),
            ("CarouselBounceWarm", "OmniLight3D", t(6.0, 0.0, 3.50),
             "Color(0.96, 0.78, 0.42, 1)", 0.55),
            ("TentBounceWarm", "OmniLight3D", t(-6.0, 0.0, 3.50),
             "Color(0.96, 0.62, 0.42, 1)", 0.50),
        ],
        "mood_strata": ["late_afternoon", "dust_devils", "sunbleached", "abandoned"],
    },

    # ── IX HERMIT — Bayou Lighthouse ─────────────────────────────
    {
        "name": "bayou_lighthouse",
        "uid": "uid://bayou_lighthouse_locale",
        "root_node": "BayouLighthouse",
        "glb": "res://assets/3d/locales/bayou_lighthouse.glb",
        # Whitewashed brick interior + oil-lamp warmth + bayou cool
        # through the window.
        "env": {"bg": (0.18, 0.18, 0.18, 1.0), "amb": (0.42, 0.38, 0.34, 1.0),
                "amb_e": 0.30, "fog": (0.32, 0.34, 0.36, 1.0),
                "fog_e": 0.10, "fog_d": 0.012,
                "bright": 0.98, "cont": 1.06, "sat": 0.88,
                "glow_i": 0.85, "glow_b": 0.14},
        "shader": {"warm": (0.96, 0.62, 0.28, 1.0),
                   "bg":   (0.18, 0.18, 0.18, 1.0),
                   "neon_edge": (0.96, 0.62, 0.28, 1.0),
                   "neon_lo":   (0.42, 0.30, 0.20, 1.0),
                   "neon_hi":   (0.18, 0.18, 0.18, 1.0),
                   "lim_tint":  (0.96, 0.84, 0.62, 1.0)},
        "lights": [
            ("Moonlight", "DirectionalLight3D",
             t_keylight(0.0, 4.0, 8.0, pitch_deg=-40.0),
             "Color(0.74, 0.78, 0.86, 1)", 0.42),
            ("OilLampWarm", "OmniLight3D", t(2.20, -0.20, 1.04),
             "Color(0.96, 0.62, 0.28, 1)", 1.10),
            ("LensTopGlow", "OmniLight3D", t(0.0, 0.80, 6.20),
             "Color(0.96, 0.86, 0.62, 1)", 0.65),
        ],
        "mood_strata": ["lamp_low", "moonlit", "watch_kept", "alone_at_post"],
    },

    # ── XI JUSTICE — Courthouse Chamber ──────────────────────────
    {
        "name": "courthouse_chamber",
        "uid": "uid://courthouse_chamber_locale",
        "root_node": "CourthouseChamber",
        "glb": "res://assets/3d/locales/courthouse_chamber.glb",
        # Wood-paneled wood-warm, fluorescent overhead — sober + balanced.
        "env": {"bg": (0.10, 0.08, 0.08, 1.0), "amb": (0.42, 0.36, 0.28, 1.0),
                "amb_e": 0.38, "fog": (0.32, 0.28, 0.22, 1.0),
                "fog_e": 0.10, "fog_d": 0.008,
                "bright": 1.02, "cont": 1.06, "sat": 0.92,
                "glow_i": 0.78, "glow_b": 0.10},
        "shader": {"warm": (0.96, 0.74, 0.42, 1.0),
                   "bg":   (0.10, 0.08, 0.08, 1.0),
                   "neon_edge": (0.96, 0.62, 0.28, 1.0),
                   "neon_lo":   (0.42, 0.30, 0.18, 1.0),
                   "neon_hi":   (0.10, 0.08, 0.08, 1.0),
                   "lim_tint":  (0.96, 0.84, 0.62, 1.0)},
        "lights": [
            ("KeyLight", "DirectionalLight3D",
             t_keylight(0.0, 8.0, 8.0, pitch_deg=-65.0),
             "Color(0.96, 0.92, 0.86, 1)", 0.85),
            ("BenchKey", "OmniLight3D", t(0.0, 9.80, 3.40),
             "Color(0.96, 0.86, 0.62, 1)", 1.10),
            ("AudienceFill", "OmniLight3D", t(0.0, 2.50, 3.40),
             "Color(0.92, 0.86, 0.74, 1)", 0.65),
        ],
        "mood_strata": ["motion_to_dismiss", "in_session", "recess", "verdict"],
    },

    # ── XII HANGED MAN — Simon's Apartment ───────────────────────
    {
        "name": "simon_apartment",
        "uid": "uid://simon_apartment_locale",
        "root_node": "SimonApartment",
        "glb": "res://assets/3d/locales/simon_apartment.glb",
        # Single-bulb walk-up, fluorescent kitchen, fire-escape blue
        # through front window. Stripped, suspended, not quite empty.
        "env": {"bg": (0.10, 0.10, 0.12, 1.0), "amb": (0.36, 0.34, 0.32, 1.0),
                "amb_e": 0.32, "fog": (0.32, 0.34, 0.38, 1.0),
                "fog_e": 0.10, "fog_d": 0.012,
                "bright": 0.98, "cont": 1.08, "sat": 0.90,
                "glow_i": 0.85, "glow_b": 0.14},
        "shader": {"warm": (0.96, 0.62, 0.28, 1.0),
                   "bg":   (0.10, 0.10, 0.12, 1.0),
                   "neon_edge": (0.62, 0.74, 0.86, 1.0),
                   "neon_lo":   (0.32, 0.34, 0.38, 1.0),
                   "neon_hi":   (0.10, 0.10, 0.12, 1.0),
                   "lim_tint":  (0.96, 0.74, 0.42, 1.0)},
        "lights": [
            ("WindowBlueKey", "DirectionalLight3D",
             t_keylight(0.0, -2.0, 4.0, pitch_deg=-35.0, yaw_deg=170.0),
             "Color(0.62, 0.74, 0.92, 1)", 0.42),
            ("BareBulb", "OmniLight3D", t(0.0, 3.50, 2.20),
             "Color(0.96, 0.86, 0.62, 1)", 0.85),
            ("KitchenFluor", "OmniLight3D", t(-2.0, 2.40, 2.50),
             "Color(0.96, 0.94, 0.86, 1)", 0.55),
        ],
        "mood_strata": ["empty_chair", "tv_snow", "fire_escape_blue", "after_simon"],
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
