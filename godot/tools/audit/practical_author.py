#!/usr/bin/env python3
"""practical_author.py — every visible fixture is also a light (2026-09-11).

_LIGHTING_PLAYBOOK.md, core rule: "If you can SEE a lamp post / window /
neon sign / lantern in the scene, there must be a Light3D at that
fixture's position emitting the appropriate color." Its 2026-08-19
lesson says the same thing the other way round: practicals ship WITH
the fixture, not after.

A repo count found 205 fixtures across 51 locales that stand in the
room and emit nothing — bulbs in pendants, tubes in fluorescent
frames, porch fixtures on twenty houses, candles on booth tables.
This authors the missing ones from the playbook's own tables:

  · colour by SOURCE (its Kelvin table, verbatim)
  · omni_range ≈ 2 × the fixture's height off the floor, clamped
  · light_energy in the playbook's bands per source
  · shadow_enabled = false (its rule for every locale light)
  · named `<Fixture>_Practical`, so the .tscn stays grep-able to the
    geometry it belongs to

BUDGET. The playbook allows 8–10 practicals per locale, so a room with
twenty dark fixtures does not get twenty lights: the ones NEAREST A
PRESET CAMERA win, because the rule is about what is visible in frame.

    python3 godot/tools/audit/practical_author.py --dry [locale…]
    python3 godot/tools/audit/practical_author.py [locale…]
"""
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO
import preset_vantage_audit as PV

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCENES = os.path.join(ROOT, "godot", "scenes", "locales")

BUDGET = 10                  # practicals authored per locale (playbook: 8–10)
NEAR_LIGHT = 0.9             # m · a fixture this close to a light already has one

FIXTURE = re.compile(r"(lamp|bulb|sconce|pendant|chandelier|lantern|fluor|fixture|candle|worklight|shoplight|ceiling_?dome)", re.I)
# parts of a fixture that are not the emitter
NOT_EMITTER = re.compile(r"(cord|wire|switch|shade|base|post|pole|stand|arm|bracket|plate|glow|halo|zone|outline|^z_|stain|wear|chain|mount|canopy|frame)", re.I)
# a fixture the fiction says is not burning
UNLIT = re.compile(r"(broken|dead|burnt|burned|unlit|dark|off_|_off|cracked|shattered|smashed|empty|spent)", re.I)

# playbook Kelvin table → (colour, energy, range factor × height, min, max)
SOURCES = (
    (re.compile(r"(candle|votive)", re.I),      (1.00, 0.72, 0.42), 0.55, 1.2, 0.8, 2.0),
    (re.compile(r"(fluor|tube|shoplight)", re.I), (0.92, 0.92, 0.85), 1.30, 1.6, 3.0, 6.0),
    (re.compile(r"(sodium|street|dock|parking)", re.I), (1.00, 0.62, 0.26), 3.00, 2.0, 6.0, 16.0),
    (re.compile(r"(porch|halogen|festoon)", re.I), (0.94, 0.84, 0.66), 1.20, 2.0, 2.5, 7.0),
    (re.compile(r"(work|task|desk|drafting)", re.I), (0.95, 0.82, 0.58), 1.10, 1.6, 1.5, 3.5),
)
DEFAULT = ((0.95, 0.78, 0.50), 1.30, 2.0, 2.0, 5.0)     # tungsten interior


def source_for(name, height):
    for rx, col, energy, k, lo, hi in SOURCES:
        if rx.search(name):
            return col, energy, max(lo, min(hi, k * max(height, 0.5)))
    col, energy, k, lo, hi = DEFAULT
    return col, energy, max(lo, min(hi, k * max(height, 0.5)))


def scene_lights(src):
    """Existing Light3D positions, in blender space."""
    out = []
    for m in re.finditer(r'\[node name="([^"]+)" type="(OmniLight3D|SpotLight3D)"[^\]]*\](.*?)(?=\n\[|\Z)', src, re.S):
        body = m.group(3)
        pm = re.search(r"position = Vector3\(([^)]+)\)", body)
        tm = re.search(r"transform = Transform3D\(([^)]+)\)", body)
        if pm:
            p = [float(v) for v in pm.group(1).split(",")]
        elif tm:
            v = [float(x) for x in tm.group(1).split(",")]
            p = v[9:12]
        else:
            continue
        out.append((p[0], -p[2], p[1]))
    return out


def preset_cameras_for(locale):
    """Blender-space camera positions of every preset that shows this locale."""
    src = open(PV.GD).read()
    out = []
    for m in PV.BLOCK.finditer(src):
        body = m.group(2)
        om, gm = PV.ORIGIN.search(body), PV.GLB.search(body)
        if not (om and gm) or gm.group(1) != locale:
            continue
        gx, gy, gz = (PV._ev(om.group(i)) for i in (1, 2, 3))
        out.append((gx, -gz, gy))
    return out


def dark_fixtures(boxes, lights):
    seen, out = set(), []
    for n, c, h in boxes:
        if not FIXTURE.search(n) or NOT_EMITTER.search(n) or UNLIT.search(n):
            continue
        if VO.IGNORE.search(n) or c[2] < 0.3:
            continue
        stem = re.sub(r"_[A-Za-z0-9.+-]+$", "", n)
        if stem in seen:
            continue
        if any((c[0] - l[0]) ** 2 + (c[1] - l[1]) ** 2 + (c[2] - l[2]) ** 2 < NEAR_LIGHT ** 2
               for l in lights):
            continue
        seen.add(stem)
        out.append((n, c, h))
    return out


def main():
    dry = "--dry" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    P.A.install_stubs()
    total = 0
    for tscn in sorted(glob.glob(os.path.join(SCENES, "*.tscn"))):
        locale = os.path.basename(tscn)[:-5]
        if only and locale not in only:
            continue
        src = open(tscn).read()
        gm = re.search(r'path="res://assets/3d/locales/(\w+)\.glb"', src)
        glb = gm.group(1) if gm else locale
        if not os.path.exists(os.path.join(P.A.LOCALES, "build_%s.py" % glb)):
            continue
        boxes = VO.boxes_for(glb)
        if not boxes:
            continue
        lights = scene_lights(src)
        dark = dark_fixtures(boxes, lights)
        if not dark:
            continue
        cams = preset_cameras_for(glb) or [(0.0, 0.0, 1.6)]
        def near_cam(f):
            c = f[1]
            return min(math.dist((c[0], c[1], c[2]), k) for k in cams)
        dark.sort(key=near_cam)
        chosen = dark[:BUDGET]
        print("== %-28s %2d light(s) · %2d dark fixture(s) · authoring %d"
              % (locale, len(lights), len(dark), len(chosen)))
        blk = ["", "; practicals authored by practical_author.py (2026-09-11):",
               "; every visible fixture is also a light (_LIGHTING_PLAYBOOK.md)"]
        for n, c, h in chosen:
            col, energy, rng = source_for(n, c[2])
            gpos = (c[0], c[2], -c[1])          # blender → godot
            print("   %-30s %4.1f m range · energy %.1f · rgb(%.2f, %.2f, %.2f)"
                  % (n, rng, energy, col[0], col[1], col[2]))
            blk.append('[node name="%s_Practical" type="OmniLight3D" parent="."]' % n)
            blk.append("position = Vector3(%.3f, %.3f, %.3f)" % gpos)
            blk.append("light_color = Color(%.3f, %.3f, %.3f, 1)" % col)
            blk.append("light_energy = %.2f" % energy)
            blk.append("shadow_enabled = false")
            blk.append("omni_range = %.2f" % rng)
            blk.append("")
        total += len(chosen)
        if not dry:
            with open(tscn, "a") as f:
                f.write("\n".join(blk))
    print("\n%d practical(s) %s" % (total, "planned" if dry else "authored"))


if __name__ == "__main__":
    main()
