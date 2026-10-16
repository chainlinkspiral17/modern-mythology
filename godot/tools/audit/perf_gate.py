#!/usr/bin/env python3
"""perf_gate.py — a room's draw calls may not quietly grow (2026-10-16).

The user: "do a quick assessment how well game is handling graphical load …
how much it can be optimized/expanded with new content", then "Go ahead".
Perf draft 2 merged the locales' still parts (scripts/StaticMerge.gd) and
took the worst rooms from 4,998–14,316 draw calls down to a few hundred.
This keeps them there: it runs tools/PerfProbe.gd on the given rooms and
fails when a room's worst view draws more than

    max(BUDGET, baseline × 1.15)

where the baseline is perf_baseline.json beside this file. A room with no
baseline is held to BUDGET alone.

    python3 godot/tools/audit/perf_gate.py ROOM [ROOM …]
    python3 godot/tools/audit/perf_gate.py --changed BASE   # rooms whose
        builder / scene / GLB changed against BASE (run_changed_audits.sh)
    python3 godot/tools/audit/perf_gate.py --update ROOM …  # record them

Needs Godot (GODOT_BIN, or godot4 / godot on PATH) and, without a display,
xvfb-run. Without Godot it says so and passes: counts are exact on any GPU,
so the next session with Godot catches what this one could not.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GODOT_DIR = HERE.parent.parent
REPO = GODOT_DIR.parent
BASELINE = HERE / "perf_baseline.json"
BUDGET = 2000
SLACK = 1.15


def godot_bin():
    env = os.environ.get("GODOT_BIN", "").strip()
    if env and (shutil.which(env) or os.access(env, os.X_OK)):
        return [env]
    for c in ("godot4", "godot", "godot4.6"):
        if shutil.which(c):
            return [shutil.which(c)]
    return None


def changed_rooms(base):
    out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=REPO,
                         capture_output=True, text=True).stdout.split()
    out += subprocess.run(["git", "diff", "--name-only"], cwd=REPO, capture_output=True, text=True).stdout.split()
    scenes = {p.stem: p for p in (GODOT_DIR / "scenes" / "locales").glob("*.tscn")}
    glb_of = {}
    for stem, p in scenes.items():
        for g in re.findall(r'assets/3d/locales/([a-z0-9_]+)\.glb', p.read_text(errors="replace")):
            glb_of.setdefault(g, set()).add(stem)
    rooms = set()
    for f in out:
        m = re.search(r"scenes/locales/([a-z0-9_]+)\.tscn$", f)
        if m and m.group(1) in scenes:
            rooms.add(m.group(1))
        m = re.search(r"(?:blender/locales/build_|assets/3d/locales/)([a-z0-9_]+?)(?:_\d{4}_\d{2})?\.(?:py|glb)$", f)
        if m:
            rooms |= glb_of.get(m.group(1), set())
    return sorted(rooms)


def probe(rooms):
    gd = godot_bin()
    if not gd:
        return None
    cmd = gd + ["--path", str(GODOT_DIR), "--rendering-driver", "opengl3", "--resolution", "1280x720",
                "--script", "res://tools/PerfProbe.gd", "--"] + rooms
    if not os.environ.get("DISPLAY") and shutil.which("xvfb-run"):
        cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x720x24"] + cmd
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300 + 120 * len(rooms))
    got = {}
    for ln in (r.stdout or "").splitlines():
        if ln.startswith("PROBE "):
            name, js = ln[6:].split(" ", 1)
            got[name] = json.loads(js)
    return got


def main():
    args = sys.argv[1:]
    update = "--update" in args
    args = [a for a in args if a != "--update"]
    if args[:1] == ["--changed"]:
        rooms = changed_rooms(args[1] if len(args) > 1 else "origin/claude/3d-locales-clean")
    else:
        rooms = args
    if not rooms:
        print("perf_gate · no rooms to measure")
        return 0
    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    got = probe(rooms)
    if got is None:
        print(f"perf_gate · no Godot here (set GODOT_BIN) — {len(rooms)} room(s) NOT measured: {', '.join(rooms)}")
        return 0
    fails = 0
    for room in rooms:
        g = got.get(room)
        if g is None:
            print(f"   ??  {room}: the probe did not report (scene failed to load?)")
            fails += 1
            continue
        draw = int(g.get("draw", 0))
        was = int((base.get(room) or {}).get("draw", 0))
        cap = max(BUDGET, int(was * SLACK))
        ok = draw <= cap
        fails += 0 if ok else 1
        print(f"   {'ok' if ok else 'OVER'}  {room}: {draw} draw calls (baseline {was or '—'}, cap {cap})")
        if update:
            base[room] = {"draw": draw, "prims": g.get("prims"), "objects": g.get("objects")}
    if update:
        BASELINE.write_text(json.dumps(dict(sorted(base.items())), indent=1) + "\n")
        print(f"perf_gate · baseline updated for {len(rooms)} room(s)")
    print(f"perf_gate · {fails} room(s) over their draw-call cap")
    return 1 if fails and not update else 0


if __name__ == "__main__":
    sys.exit(main())
