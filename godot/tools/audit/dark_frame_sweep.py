#!/usr/bin/env python3
"""dark_frame_sweep.py — render every frame a cue actually uses, rank by brightness.

Every gate can read zero while a cue cuts to a frame no one can read: a
fridge on a black couch, a crow under a dark roof, a door 4.9 m from any
lamp, headlights aimed at the sky (pass 306, 2026-11-08 — the sweep's
first run, then session scratch, found ~30 such cues across 322 sets).

For each 3D preset the chapters play (resolved through bg_resolve, as the
engine reads bg_places), this collects the [shot:<type> <id>] frames cued
on it, renders them in ONE TripPaintTest launch (`--markers ... --luma 1`,
the director's own marker resolution), and records the mean and 90th
percentile luminance of the clear top 69% of each frame (the text box
covers the rest). Results are cached per preset in the output directory,
so a run killed part-way resumes where it stopped.

Brightness is NOT a gate. The darkest frames are a reading list: much of
the dark is the text's own ("in the dark", a darkroom's safelight, a
windowless room) and stays. Read each by eye (the PNGs are in the output
directory); fix the rest by re-aiming to where the light is, cutting to
another object the same line names, or lighting from a fixture already in
the set (_VN_DIRECTION_PLAYBOOK, pass 306). Record a frame read and kept in
JUDGED_DARK with the reason.

    GODOT_BIN=... python3 tools/audit/dark_frame_sweep.py [--out DIR] [--top N] [preset ...]
    python3 tools/audit/dark_frame_sweep.py --jobs      # list the work, render nothing

Without GODOT_BIN it lists the jobs and exits 0. A full run is ~1 minute
a preset (322 presets on 2026-11-08): run it in the background.
"""
import collections
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCENES = os.path.join(GODOT, "resources", "scenes")
sys.path.insert(0, HERE)
import bg_resolve  # noqa: E402

CUE = re.compile(r"\[shot:(\w+)\s+(\w+)~?\]")
LUMA = re.compile(r"^LUMA (\S+) ([\d.]+) (\d+)")
DARK_MEAN = 32.0          # below this the frame is on the reading list

# Frames read and kept dark ON PURPOSE: (preset, marker) -> why.
JUDGED_DARK = {
    ("darkroom", "shot_insert_tray"): "the darkroom's red safelight",
    ("darkroom", "shot_insert_photograph"): "the darkroom's red safelight",
    ("nightmare_cell", "shot_insert_chair"): "the text: 'The room has no windows.'",
    ("nightmare_cell", "shot_insert_door"): "the text: 'The room has no windows.'",
    ("nightmare_cell", "shot_insert_doors"): "the text: 'The room has no windows.'",
    ("nightmare_cell", "shot_closeup_person"): "the text: 'The room has no windows.'",
    ("jesse_bedroom", "shot_insert_door"): "the text: 'The light under the door is off', 'in the dark'",
    ("lighthouse_base_up", "shot_insert_padlock"): "the preset is 'looking up in darkness' (pass 305)",
    ("lighthouse_base_up", "shot_insert_column"): "the preset is 'looking up in darkness' (pass 305)",
    ("beach_night", "shot_closeup_person"): "the night sea behind a face",
    ("beach_bonfire", "shot_closeup_person"): "the night sea behind a face",
}


def jobs():
    """preset -> (vol, sorted marker names) for every cue frame on a 3D set."""
    want = collections.defaultdict(set)
    vol_of = {}
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn), encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(j, dict):
                continue
            m = re.search(r"vol(\d+)", fn) or re.search(r"vol(\d+)", dirpath)
            vol = int(m.group(1)) if m else int(j.get("vol", 1) or 1)
            cur = ""
            for n in j.get("nodes", []):
                if n.get("t") == "bg":
                    cur = bg_resolve.preset_of(n.get("src"), j.get("id", fn[:-5])) or ""
                if not cur:
                    continue
                for typ, sid in CUE.findall(n.get("text") or ""):
                    want[cur].add("shot_%s_%s" % (typ, sid))
                    vol_of.setdefault(cur, vol)
    return {p: (vol_of[p], sorted(ms)) for p, ms in want.items()}


def render(godot_bin, preset, vol, markers, outdir):
    d = os.path.join(outdir, preset)
    os.makedirs(d, exist_ok=True)
    cmd = [godot_bin, "--path", GODOT, "--rendering-driver", "opengl3",
           "res://tools/TripPaintTest.tscn", "--", "--energy", "0.0", "--vol", str(vol),
           "--preset", preset, "--markers", ",".join(markers), "--outdir", d, "--luma", "1"]
    if not os.environ.get("DISPLAY") and subprocess.run(["which", "xvfb-run"],
                                                        capture_output=True).returncode == 0:
        cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x720x24"] + cmd
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=600).stdout
    except subprocess.TimeoutExpired:
        return None
    res = {}
    for line in out.splitlines():
        m = LUMA.match(line)
        if m:
            res[m.group(1)] = [float(m.group(2)), int(m.group(3))]
    json.dump(res, open(os.path.join(d, "luma.json"), "w"), indent=1)
    return res


def main():
    argv = sys.argv[1:]
    outdir = "/tmp/dark_frame_sweep"
    top = 40
    if "--out" in argv:
        i = argv.index("--out"); outdir = argv[i + 1]; del argv[i:i + 2]
    if "--top" in argv:
        i = argv.index("--top"); top = int(argv[i + 1]); del argv[i:i + 2]
    only_jobs = "--jobs" in argv
    argv = [a for a in argv if not a.startswith("--")]
    work = jobs()
    if argv:
        work = {p: v for p, v in work.items() if p in argv}
    nframes = sum(len(v[1]) for v in work.values())
    godot_bin = os.environ.get("GODOT_BIN", "")
    if only_jobs or not godot_bin:
        for p in sorted(work):
            print("%-34s vol %d  %s" % (p, work[p][0], ",".join(work[p][1])))
        print("\ndark_frame_sweep · %d preset(s) · %d cue frame(s)%s"
              % (len(work), nframes, "" if godot_bin else " · no GODOT_BIN: nothing rendered"))
        return 0
    rows = []
    for k, p in enumerate(sorted(work)):
        vol, markers = work[p]
        cache = os.path.join(outdir, p, "luma.json")
        res = json.load(open(cache)) if os.path.exists(cache) else None
        if res is None:
            print("[%d/%d] %s" % (k + 1, len(work), p), flush=True)
            res = render(godot_bin, p, vol, markers, outdir) or {}
        for mk in markers:
            if mk in res:
                rows.append((res[mk][0], res[mk][1], p, mk))
            else:
                rows.append((-1.0, -1, p, mk))      # not rendered: a missing marker
    rows.sort()
    missing = [r for r in rows if r[0] < 0]
    dark = [r for r in rows if 0 <= r[0] < DARK_MEAN and (r[2], r[3]) not in JUDGED_DARK]
    judged = sum(1 for r in rows if (r[2], r[3]) in JUDGED_DARK)
    for mean, p90, p, mk in dark[:top]:
        print("  %5.1f  p90 %3d  %-30s %s" % (mean, p90, p, mk))
    for _m, _p, p, mk in missing:
        why = ("a cast closeup with no frame of its own: the director substitutes the room's pair"
               if mk.startswith("shot_closeup_") else "no frame rendered: the marker does not resolve")
        print("  MISSING  %-30s %s (%s)" % (p, mk, why))
    print("\ndark_frame_sweep · %d frame(s) read in %d preset(s) · %d below mean %.0f "
          "to read by eye · %d judged dark on purpose · %d missing · PNGs in %s"
          % (len(rows) - len(missing), len(work), len(dark), DARK_MEAN, judged, len(missing), outdir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
