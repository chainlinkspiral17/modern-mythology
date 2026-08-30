#!/usr/bin/env python3
"""VN story audit — every directive in every chapter must RESOLVE.

Born 2026-08-30, the day the VN pillar was declared the focus
("bring it up to top tier professional level"). The first mark of a
professional book is that nothing in it dangles: every background
preset, CG path, jump target, mood, beat, and panel a chapter names
must exist. The engine degrades gracefully (missing bg → warning,
missing panel → silent nothing), which is exactly why these rot
unnoticed — a broken reference LOOKS like a stylistic choice.

Checks across resources/scenes/vol*/*.json:
  1.  JSON parses; scene ids unique.
  2.  bg "3d:<preset>" → preset exists in Background3D.CAMERA_PRESETS.
  3.  bg non-3d src → file exists on disk.
  4.  cg src → file exists.
  5.  substrate src → <root><src>.json or .png exists.
  6.  composition src → compositions/<src>.json exists.
  7.  jump/choice/check scene targets → a scene with that id exists.
  8.  choice goto / check pass+fail indices in node range.
  9.  [mood:x] → a MoodCycler mood name.
 10.  [beat:x] → a VnDirector BEATS key.
 11.  [panel:x] → resources/vn/panels/<x>.json (x=off ok).
 12.  bgm/sfx src → audio file exists.
 13.  unknown node types (vs the engine's dispatch table).
Info-only (reported, never fails):
  - voice files missing (the voice program is aspirational)
  - distinct char names with counts (typo hunting by eye)

Usage:
    python3 godot/tools/audit/vn_story_audit.py            # all vols
    python3 godot/tools/audit/vn_story_audit.py vol5 vol6  # some
    python3 godot/tools/audit/vn_story_audit.py --chars    # char report
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SCENES = os.path.join(GODOT, "resources", "scenes")
PANELS = os.path.join(GODOT, "resources", "vn", "panels")
SUBSTRATES = os.path.join(GODOT, "resources", "substrates")
COMPOSITIONS = os.path.join(SUBSTRATES, "compositions")

NODE_TYPES = {
    "narrate", "say", "think", "choice", "show", "hide", "bg",
    "substrate", "composition", "bgm", "sfx", "flag", "jump", "end",
    "interlude", "cg", "videoscene", "gallery",
}
BEATS = {"still", "hit", "chill", "lift"}
DIRECT_RX = re.compile(r"^\[(\w+):([^\]]*)\]")


def camera_presets():
    src = open(os.path.join(GODOT, "scripts", "vn", "Background3D.gd")).read()
    m = re.search(r"const CAMERA_PRESETS := \{", src)
    depth = 0
    keys = set()
    for line in src[m.start():].splitlines():
        depth += line.count("{") - line.count("}")
        km = re.match(r'\s*"([\w~]+)":\s*\{', line)
        if km and depth >= 1:
            keys.add(km.group(1))
        if depth == 0 and "{" in line is False:
            break
        if depth <= 0 and keys:
            break
    return keys


def mood_names():
    src = open(os.path.join(GODOT, "scripts", "MoodCycler.gd")).read()
    return set(re.findall(r'"name":\s*"(\w+)"', src))


def exists(rel):
    return os.path.exists(os.path.join(GODOT, rel))


def leading_directives(text):
    out = []
    while text.startswith("["):
        m = DIRECT_RX.match(text)
        if not m:
            break
        out.append((m.group(1), m.group(2).strip()))
        text = text[m.end():]
    return out


def main():
    args = [a for a in sys.argv[1:]]
    chars_only = "--chars" in args
    only = [a for a in args if not a.startswith("-")]

    presets = camera_presets()
    moods = mood_names()

    files = []
    for vol in sorted(os.listdir(SCENES)):
        if only and vol not in only:
            continue
        vd = os.path.join(SCENES, vol)
        if not os.path.isdir(vd):
            continue
        for fn in sorted(os.listdir(vd)):
            if fn.endswith(".json"):
                files.append(os.path.join(vd, fn))

    scenes = {}
    problems = []
    voice_missing = 0
    voice_total = 0
    char_uses = {}

    for path in files:
        rel = os.path.relpath(path, GODOT)
        try:
            data = json.load(open(path))
        except Exception as e:
            problems.append((rel, "JSON PARSE: %s" % e))
            continue
        sid = str(data.get("id", ""))
        if sid in scenes:
            problems.append((rel, "duplicate scene id '%s' (also %s)" %
                             (sid, scenes[sid][0])))
        scenes[sid] = (rel, data)

    # id → node count for goto range checks
    for sid, (rel, data) in scenes.items():
        nodes = data.get("nodes", [])
        n_count = len(nodes)
        for i, n in enumerate(nodes):
            t = str(n.get("t", ""))
            where = "%s#%d" % (rel, i)
            if t not in NODE_TYPES:
                problems.append((where, "unknown node type '%s'" % t))
            if t == "bg":
                # Engine's _s() maps null → "" (clear-bg); mirror it.
                src = n.get("src") if isinstance(n.get("src"), str) else ""
                if src.startswith("3d:"):
                    if src[3:] not in presets:
                        problems.append((where, "bg 3d preset '%s' not in "
                                         "CAMERA_PRESETS" % src[3:]))
                elif src and not exists(src):
                    problems.append((where, "bg file missing: %s" % src))
            elif t == "cg":
                src = str(n.get("src", ""))
                if src and not exists(src):
                    problems.append((where, "cg file missing: %s" % src))
            elif t == "substrate":
                src = str(n.get("src", ""))
                if src and not (
                        os.path.exists(os.path.join(SUBSTRATES, src + ".json"))
                        or os.path.exists(os.path.join(SUBSTRATES, src + ".png"))):
                    problems.append((where, "substrate missing: %s" % src))
            elif t == "composition":
                src = str(n.get("src", ""))
                if src and not os.path.exists(
                        os.path.join(COMPOSITIONS, src + ".json")):
                    problems.append((where, "composition missing: %s" % src))
            elif t in ("bgm", "sfx"):
                src = str(n.get("src", ""))
                if src and not exists(src):
                    problems.append((where, "%s file missing: %s" % (t, src)))
            elif t == "jump":
                tgt = str(n.get("scene", ""))
                if tgt and tgt not in scenes:
                    problems.append((where, "jump target '%s' not found" % tgt))
            elif t == "choice":
                for oi, opt in enumerate(n.get("opts", [])):
                    tgt = str(opt.get("scene", ""))
                    if tgt and tgt not in scenes:
                        problems.append((where, "opt %d scene '%s' not found"
                                         % (oi, tgt)))
                    if "goto" in opt and not (0 <= int(opt["goto"]) < n_count):
                        problems.append((where, "opt %d goto %s out of range "
                                         "(%d nodes)" % (oi, opt["goto"], n_count)))
                    chk = opt.get("check")
                    if isinstance(chk, dict):
                        for k in ("pass", "fail"):
                            if k in chk and not (0 <= int(chk[k]) < n_count):
                                problems.append((where, "opt %d check %s=%s "
                                                 "out of range" % (oi, k, chk[k])))
            if t in ("say", "think", "show"):
                cn = str(n.get("char", "")).strip()
                if cn:
                    char_uses[cn] = char_uses.get(cn, 0) + 1
            text = n.get("text", "")
            if isinstance(text, str):
                for kind, arg in leading_directives(text):
                    if kind == "mood" and arg.lower() not in moods:
                        problems.append((where, "[mood:%s] unknown" % arg))
                    elif kind == "beat" and arg.lower() not in BEATS:
                        problems.append((where, "[beat:%s] unknown" % arg))
                    elif kind == "panel" and arg.lower() not in ("off", ""):
                        if not os.path.exists(
                                os.path.join(PANELS, arg.lower() + ".json")):
                            problems.append((where, "[panel:%s] missing" % arg))
            v = n.get("voice", "")
            if isinstance(v, str) and v:
                voice_total += 1
                if not exists(v):
                    voice_missing += 1

    if chars_only:
        for cn, ct in sorted(char_uses.items(), key=lambda x: -x[1]):
            print("%5d  %s" % (ct, cn))
        return

    print("vn_story_audit · %d scene file(s) · %d preset(s) · %d mood(s)"
          % (len(files), len(presets), len(moods)))
    if voice_total:
        print("voice lines: %d referenced · %d missing on disk (info only)"
              % (voice_total, voice_missing))
    if problems:
        for where, msg in problems:
            print("PROBLEM  %-52s %s" % (where, msg))
        print("%d problem(s)" % len(problems))
        sys.exit(1)
    print("0 problems: every directive resolves")


if __name__ == "__main__":
    main()
