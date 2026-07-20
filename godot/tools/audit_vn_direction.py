#!/usr/bin/env python3
"""Audit VN scene direction (vol5 / vol6).

Two jobs, mirroring the gauntlet locale director pass:
  1. CORRECTNESS — every `{"t":"bg","src":"3d:<preset>"}` must resolve
     to a real Background3D.CAMERA_PRESETS key, or the scene renders a
     blank/wrong set. Reports broken bg refs.
  2. DIRECTION DENSITY — per scene: node count, distinct 3d backdrops,
     mood cues ([mood:...]), stage/blocking cues ([stage:...]), and
     whether bgm is set. Flags "flat" scenes (a long scene on one
     backdrop with no mood shifts) as candidates for a direction pass.

Run from repo root: python3 godot/tools/audit_vn_direction.py
Exit 1 if any broken bg ref is found.
"""
import json, re, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
SCENES = os.path.join(ROOT, "resources/scenes")
BG3D = os.path.join(ROOT, "scripts/vn/Background3D.gd")

def valid_presets():
    t = open(BG3D).read()
    m = re.search(r"CAMERA_PRESETS\b[^{]*\{", t)
    i = m.end()-1; depth = 0; body = ""
    for j in range(i, len(t)):
        if t[j] == '{': depth += 1
        elif t[j] == '}':
            depth -= 1
            if depth == 0: body = t[i+1:j]; break
    out = set(); d2 = 0
    for ln in body.splitlines():
        km = re.match(r'"([a-z_0-9]+)"\s*:\s*\{', ln.strip())
        if km and d2 == 0: out.add(km.group(1))
        d2 += ln.count('{')-ln.count('}')
    return out

def text_of(n):
    return " ".join(str(n.get(k, "")) for k in ("text", "sub", "src"))

def main():
    presets = valid_presets()
    broken = 0
    flat = []
    scanned = 0
    for vol in ("vol5", "vol6"):
        vdir = os.path.join(SCENES, vol)
        if not os.path.isdir(vdir): continue
        for fn in sorted(os.listdir(vdir)):
            if not fn.endswith(".json"): continue
            try:
                d = json.load(open(os.path.join(vdir, fn)))
            except Exception:
                continue
            nodes = d.get("nodes", [])
            if not isinstance(nodes, list) or not nodes: continue
            scanned += 1
            bgs = []
            mood_cues = 0
            stage_cues = 0
            interludes = 0
            has_bgm = False
            for n in nodes:
                if not isinstance(n, dict): continue
                t = n.get("t", "")
                if t == "interlude":
                    interludes += 1
                if t == "bg":
                    src = str(n.get("src", ""))
                    if src.startswith("3d:"):
                        pid = src[3:]
                        bgs.append(pid)
                        if pid not in presets:
                            broken += 1
                            print(f"  !! {vol}/{fn}: bg 3d:{pid} — NOT a CAMERA_PRESET")
                elif t == "bgm":
                    has_bgm = True
                blob = text_of(n)
                mood_cues += len(re.findall(r"\[mood:", blob))
                stage_cues += len(re.findall(r"\[stage:", blob))
            distinct_bg = len(set(bgs))
            # "flat" = a direction-pass candidate: substantial, one backdrop,
            # <=1 mood cue, AND >=2 interludes (its own structural beats to
            # hang mood shifts on). A long one-room, single-interlude scene is
            # an intentionally STEADY two-hander, not a defect — excluded.
            if len(nodes) >= 40 and distinct_bg <= 1 and mood_cues <= 1 and interludes >= 2:
                flat.append((f"{vol}/{fn}", len(nodes), distinct_bg, mood_cues, stage_cues, interludes, has_bgm))

    print(f"\n=== scanned {scanned} scenes · {broken} broken bg ref(s) ===")
    if flat:
        print(f"\n--- {len(flat)} FLAT scenes (>=40 nodes, <=1 backdrop, <=1 mood, >=2 interludes) — direction-pass candidates ---")
        for f, nc, db, mc, sc, il, bg in sorted(flat, key=lambda r: -r[1]):
            print(f"   {f:42s} nodes={nc:3d}  backdrops={db}  moods={mc}  stages={sc}  interludes={il}  bgm={'y' if bg else 'n'}")
    return 1 if broken else 0

if __name__ == "__main__":
    sys.exit(main())
