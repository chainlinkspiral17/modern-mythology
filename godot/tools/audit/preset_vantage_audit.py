#!/usr/bin/env python3
"""Preset-vantage audit — does every Background3D camera preset
actually LOOK AT its locale's geometry?

Born 2026-08-11: the graustark_ruins preset stood at the riverfront
origin looking west while the ruin quarter — the staging for FOUR
chapters — was 350m south. Every chapter rendered flat brown dirt,
and the stale-GLB failure masked the camera failure (fixing one
without the other left the scene brown). This audit ends the class:
a vantage that sees (almost) nothing is a failure.

Method: record each builder's geometry through the overlap-audit
recorder, convert the godot-frame preset (origin + YXZ euler) to
the blender frame, and count recorded boxes inside a 60-degree
forward cone out to 150m.

Threshold: a preset seeing < MIN_CONE objects fails, UNLESS its
locale records fewer than 2*MIN_CONE boxes total (sparse hand-
rolled sets like the graustark district record only their prop
layer — the graustark_wreck vantage legitimately sees 6 of 114
because the wreck IS six recorded parts; sparse scenes are judged
by seeing ANYTHING at all).

Usage:
    python3 godot/tools/audit/preset_vantage_audit.py
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prop_overlap_audit as P

GD = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "scripts", "vn", "Background3D.gd"))

MIN_CONE = 5
CONE_COS = 0.5      # 60-degree half-angle
MAX_DIST = 150.0

_num = r"([-+0-9.eE_a-z()\s]+?)"
BLOCK = re.compile(r'"(\w+)":\s*\{(.*?)\n\t\},', re.S)
ORIGIN = re.compile(r'"camera_origin":\s*Vector3\(%s,%s,%s\)' %
                    (_num, _num, _num))
ROT = re.compile(r'"camera_rotation":\s*Vector3\(%s,%s,%s\)' %
                 (_num, _num, _num))
GLB = re.compile(
    r'"requires_glb":\s*"res://assets/3d/(?:locales/)?(?:\w+/)?(\w+)\.glb"')


def _ev(expr):
    expr = expr.strip()
    m = re.match(r"deg_to_rad\(([-+0-9.]+)\)", expr)
    if m:
        return math.radians(float(m.group(1)))
    return float(expr)


def main():
    src = open(GD).read()
    P.A.install_stubs()
    cache = {}
    bad = []
    n_checked = 0
    for m in BLOCK.finditer(src):
        pid, body = m.group(1), m.group(2)
        om, rm, gm = ORIGIN.search(body), ROT.search(body), GLB.search(body)
        if not (om and rm and gm):
            continue
        locale = gm.group(1)
        builder = os.path.join(P.A.LOCALES, "build_%s.py" % locale)
        if not os.path.exists(builder):
            continue
        if locale not in cache:
            boxes, _err = P.record_builder(builder)
            cache[locale] = boxes or []
        boxes = cache[locale]
        gx, gy, gz = (_ev(om.group(i)) for i in (1, 2, 3))
        pitch, yaw = _ev(rm.group(1)), _ev(rm.group(2))
        cam = (gx, -gz, gy)                      # godot -> blender
        fg = (-math.sin(yaw) * math.cos(pitch), math.sin(pitch),
              -math.cos(yaw) * math.cos(pitch))
        fwd = (fg[0], -fg[2], fg[1])
        cone = 0
        for _name, c, _h in boxes:
            v = (c[0] - cam[0], c[1] - cam[1], c[2] - cam[2])
            d = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
            if d < 0.5 or d > MAX_DIST:
                continue
            if (v[0] * fwd[0] + v[1] * fwd[1] + v[2] * fwd[2]) / d > CONE_COS:
                cone += 1
        n_checked += 1
        floor = 1 if len(boxes) < 2 * MIN_CONE else MIN_CONE
        if cone < floor:
            bad.append((pid, locale, cone, len(boxes)))
    print("preset_vantage_audit · %d presets checked" % n_checked)
    if bad:
        for pid, locale, cone, total in bad:
            print("BLIND VANTAGE  %-30s %-24s sees %d of %d recorded"
                  % (pid, locale, cone, total))
        return 1
    print("0 blind: every preset sees its locale")
    return 0


if __name__ == "__main__":
    sys.exit(main())
