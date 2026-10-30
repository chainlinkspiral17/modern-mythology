"""One-shot: the locale tscn for small_wood_field (draft 1, 2026-10-27).

Same contract as make_vol1_4_tscns_2026_10_17.py: write_locale_tscn with
full parity; light positions from the builder's geometry (blender (x, y, z)
-> godot (x, z, -y)); a light named `<name>__<preset>` plays only in that
preset. The night is the scene's own environment (the white haze); the dusk
lifts it in Background3D. Then the shot markers are appended. Run with plain
python3 from the repo root.
"""
import os, sys, math
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from _props.make_locale_tscn import write_locale_tscn

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", "scenes", "locales"))
I = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {}, {}, {})"
B_FILL = "Transform3D(-0.707, -0.354, -0.612, 0, 0.866, -0.5, 0.707, -0.354, -0.612, {}, {}, {})"
# travels EAST (godot +x), 12 deg down: the sun going down behind the visitors' side
B_SUN_FROM_W = "Transform3D(0, 0.208, -0.978, 0, 0.978, 0.208, 1, 0, 0, {}, {}, {})"
B_MOON = "Transform3D(-1, 0, 0, 0, 0.707, 0.707, 0, 0.707, -0.707, {}, {}, {})"
NIGHT, DUSK = "__small_wood_field_night", "__small_wood_field_dusk"
MAY = "__small_wood_field_may"     # May's view in the stand, the same dusk light

# from build_small_wood_field.py
YD = 0.9144
SIDE_X, MID_Y, FIELD_LEN = 53.333 * YD / 2.0, 60.0 * YD, 120.0 * YD
# draft 2 (2026-10-27): the track rings the field; everything stands past it
TRACK_OUT = 36.5 + 6 * 1.22
GS_X0 = TRACK_OUT + 2.56
GS_XB = GS_X0 + 0.30 + 0.80 * 14
VIS_D0 = TRACK_OUT + 1.56 - SIDE_X
SOUTH = -24.0


def c(r, g, b):
    return "Color({}, {}, {}, 1)".format(r, g, b)


hx, wx = TRACK_OUT + 1.3, -(SIDE_X + VIS_D0 + 8 * 0.8 + 2.2)
POLES = ((wx, MID_Y - 38.0), (wx, MID_Y), (wx, MID_Y + 38.0), (hx, MID_Y - 38.0), (hx, MID_Y + 38.0), (hx, MID_Y - 52.0))
lights = [("Moon" + NIGHT, "DirectionalLight3D", B_MOON.format(0, 30, -60), c(0.56, 0.62, 0.82), 0.16),
          ("Fill" + NIGHT, "DirectionalLight3D", B_FILL.format(0, 20, -50), c(0.70, 0.72, 0.80), 0.18)]
for pi, (px, py) in enumerate(POLES):
    toward = 1.0 if px < 0 else -1.0
    lights.append(("Flood_{}".format(pi) + NIGHT, "OmniLight3D", I.format(round(px + toward * 1.2, 2), 19.6, round(-py, 2)),
                   c(1.0, 0.97, 0.88), 5.5, {"omni_range": 80.0}))
for i in range(3):
    lights.append(("GS_Underroof_{}".format(i) + NIGHT, "OmniLight3D",
                   I.format(round(GS_X0 + 4.0, 2), 10.3, round(-(MID_Y - 20.0 + i * 20.0), 2)), c(1.0, 0.86, 0.62), 1.6, {"omni_range": 12.0}))
lights += [
    ("PressBox_Glow" + NIGHT, "OmniLight3D", I.format(round(GS_XB - 3.2, 2), 13.4, round(-MID_Y, 2)), c(1.0, 0.86, 0.60), 1.0, {"omni_range": 8.0}),
    ("Concession_Window" + NIGHT, "OmniLight3D", I.format(round(GS_X0 + 2.0, 2), 1.6, 5.5), c(1.0, 0.84, 0.58), 1.4, {"omni_range": 7.0}),
    ("Church_Glow" + NIGHT, "OmniLight3D", I.format(14.0, 3.4, round(98.0 - SOUTH - 24.0, 2)), c(1.0, 0.80, 0.50), 1.2, {"omni_range": 14.0}),
]
for i in range(-3, 4):
    lights.append(("Streetlight_{}".format(i + 3) + NIGHT, "OmniLight3D", I.format(i * 24.0, 6.8, round(46.0 - SOUTH, 2)), c(1.0, 0.74, 0.40), 1.4, {"omni_range": 15.0}))
lights += [
    ("Sun" + DUSK + MAY, "DirectionalLight3D", B_SUN_FROM_W.format(-80, 20, -55), c(1.0, 0.76, 0.50), 1.5),
    ("SkyFill" + DUSK + MAY, "DirectionalLight3D", B_FILL.format(0, 20, -50), c(0.62, 0.70, 0.92), 0.35),
]

CFG = {
    # VOL 2's SMALL WOOD FIELD (build_small_wood_field.py): Friday night
    # under the lights in a white haze; two-a-days at dusk.
    "out_path": os.path.join(ROOT, "small_wood_field.tscn"),
    "uid": "uid://small_wood_field_v1",
    "root_node": "SmallWoodField",
    "glb": "res://assets/3d/locales/small_wood_field.glb",
    "env": {"bg": (0.03, 0.04, 0.07, 1), "amb": (0.44, 0.48, 0.60, 1),
            "amb_e": 0.35, "fog": (0.60, 0.62, 0.66, 1), "fog_e": 0.6,
            "fog_d": 0.0045, "sat": 0.92, "glow_i": 1.0, "glow_b": 0.20},
    "shader": {"warm": (0.94, 0.88, 0.74, 1), "bg": (0.05, 0.06, 0.08, 1),
               "neon_edge": (0.80, 0.82, 0.70, 1), "neon_lo": (0.22, 0.26, 0.22, 1),
               "neon_hi": (0.05, 0.06, 0.08, 1), "lim_tint": (0.66, 0.70, 0.62, 1)},
    "lights": lights,
    "mood_strata": ["raw", "memory_warm", "noir", "lithograph", "candlelight", "silent_film_18"],
}

MARKERS = [
    # (name, godot position, rotation (pitch, yaw, 0), fov, comment)
    ("shot_closeup_person", (27.5, 1.62, -52.0), (0.0, -1.5708), 45.0,
     "the sideline, his helmet off: a face against the track and the lit home stand"),
    ("shot_closeup_person_b", (31.5, 1.62, -50.0), (0.0, 1.5708), 45.0,
     "the reverse: a face against the field, the visitors' side and the lights"),
    ("shot_establish_b", (-51.6, 4.6, -(MID_Y + 16.0)), (-0.04, -1.7244), 55.0,
     "from the top of the visitors' side: the field, the track and the full home stand across it"),
    ("shot_insert_scoreboard", (7.0, 1.7, -(FIELD_LEN + 22.0)), (0.30, 0.4636), 38.0,
     "the scoreboard past the track's north curve (rewind: R.I.P. — the CG has that moment)"),
    ("shot_insert_lamp_0", (-30.0, 1.6, -32.0), (0.5839, 2.146), 45.0,
     "\"The stadium lights hung over the field in a white haze\": a visitors'-side bank over the firs"),
    ("shot_insert_church", (15.0, 1.7, round(69.0, 2)), (0.30, 3.0831), 52.0,
     "from the near curb across the street: the church door, the nave, the belfry (the vigil)"),
    ("shot_insert_concession", (47.5, 1.6, 1.5), (-0.05, 3.1416), 40.0,
     "the concession window on the walk"),
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
