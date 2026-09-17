#!/usr/bin/env python3
"""consequence_map.py — the VN's game layer, drawn (design pillar, 2026-09-17).

The visual novel's own game layer — choices, flags, skill checks — had
never been looked at as a system. Drawing it found the defect that
VnSweep's "dead checks" only hinted at: NOTHING RAISES A SKILL. The
five skills start at zero, load from the save, show on the HUD and
are read by every `check` — and no node has ever incremented one. So
every "[LOGIC] …" / "[EMPATHY] …" option the player has ever picked
took the fail branch, silently, since the first build.

This script draws the map, per volume, in scene-index order:
  · every `choice` (its scene, the line before it, each option and
    where it goes, what flag it sets, what skill it trains, what
    check it makes);
  · every flag: where it is set, where it is read, and the LOOSE
    ones — set and never read, a choice the game never remembers;
  · every check: its skill and difficulty against the most that
    skill can have been EARNED before that scene (`skill` on an
    option = +1, or `amount`), so a check that cannot pass is named.

    python3 godot/tools/audit/consequence_map.py           # writes lore/_VN_CONSEQUENCE_MAP.md
    python3 godot/tools/audit/consequence_map.py --print   # to stdout instead

`vn_skill_audit.py` gates the same data at zero; this file is the
design document the gate protects.
"""
import glob
import json
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
SCENES = os.path.join(GODOT, "resources", "scenes")
INDEX = os.path.join(SCENES, "index.json")
OUT = os.path.join(ROOT, "lore", "_VN_CONSEQUENCE_MAP.md")

SKILLS = ["empathy", "logic", "composure", "rhetoric", "signal"]
TEXT_TYPES = ("narrate", "say", "think")
DIRECTIVE_RX = re.compile(r"^(\[[a-z]+:[^\]]*\])+")


def reading_order():
    """vol -> [scene_id …] in index.json order, then any indexed-out
    scene files after them (alphabetical) so nothing is missed."""
    idx = json.load(open(INDEX, encoding="utf-8"))
    order = OrderedDict()
    for vol in sorted(idx, key=lambda v: int(v)):
        ids = list(idx[vol]) if isinstance(idx[vol], list) else list(idx[vol].keys())
        seen = set(ids)
        extra = sorted(os.path.basename(f)[:-5]
                       for f in glob.glob(os.path.join(SCENES, "vol%s" % vol, "*.json"))
                       if os.path.basename(f)[:-5] not in seen)
        order[int(vol)] = ids + extra
    return order


def load_scene(vol, sid):
    p = os.path.join(SCENES, "vol%d" % vol, sid + ".json")
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def line_before(nodes, i):
    for j in range(i - 1, -1, -1):
        if nodes[j].get("t") in TEXT_TYPES:
            t = DIRECTIVE_RX.sub("", str(nodes[j].get("text", "")))
            return t.strip().replace("\n", " ")
    return ""


def load_volumes():
    """Returns {vol: {"scenes": [...], "choices": [...], "flags_set": {...},
    "flags_read": {...}, "checks": [...], "earn": Counter}} with every
    event in reading order."""
    out = {}
    for vol, ids in reading_order().items():
        v = {"scenes": [], "choices": [], "flags_set": defaultdict(list),
             "flags_read": defaultdict(list), "checks": [], "earn_by_scene": []}
        earned = Counter()
        for sid in ids:
            d = load_scene(vol, sid)
            if d is None:
                continue
            nodes = d.get("nodes", [])
            v["scenes"].append(sid)
            before = Counter(earned)   # what the reader can have BEFORE this scene
            for i, n in enumerate(nodes):
                t = n.get("t")
                for k in ("when_flag", "when_not_flag", "only_if_flag", "hide_if_flag"):
                    if k in n:
                        v["flags_read"][str(n[k])].append((sid, i, k))
                if t == "flag":
                    v["flags_set"][str(n.get("key"))].append((sid, i, "flag"))
                if t == "check":
                    v["checks"].append({"scene": sid, "node": i, "skill": n.get("skill"),
                                        "diff": int(n.get("diff", 0)), "pass": n.get("pass"),
                                        "fail": n.get("fail"), "earnable": before.get(n.get("skill"), 0),
                                        "option": ""})
                if t != "choice":
                    continue
                ch = {"scene": sid, "node": i, "prompt": str(n.get("prompt", "")),
                      "before": line_before(nodes, i), "style": n.get("style", ""),
                      "hotspot": n.get("hotspot", ""), "opts": []}
                for o in n.get("opts", []):
                    opt = {"text": str(o.get("text", "")), "goto": o.get("goto"),
                           "scene_to": o.get("scene"), "flag": o.get("flag"), "val": o.get("val", True),
                           "skill": o.get("skill"), "amount": int(o.get("amount", 1)),
                           "check": o.get("check"), "hide_if": o.get("hide_if_flag"),
                           "only_if": o.get("only_if_flag")}
                    if opt["flag"]:
                        v["flags_set"][str(opt["flag"])].append((sid, i, "opt"))
                    for k in ("hide_if", "only_if"):
                        if opt[k]:
                            v["flags_read"][str(opt[k])].append((sid, i, k))
                    if opt["skill"]:
                        # one choice can only be taken once per read; the
                        # most it can earn is the largest amount among its
                        # options for that skill — counted after the scene.
                        pass
                    if opt["check"]:
                        c = dict(opt["check"])
                        v["checks"].append({"scene": sid, "node": i, "skill": c.get("skill"),
                                            "diff": int(c.get("diff", 0)), "pass": c.get("pass"),
                                            "fail": c.get("fail"),
                                            "earnable": before.get(c.get("skill"), 0),
                                            "option": opt["text"]})
                    ch["opts"].append(opt)
                v["choices"].append(ch)
                # After this choice: the reader can have taken ONE option, so a
                # skill's ceiling rises by the best single option for it here.
                best = Counter()
                for opt in ch["opts"]:
                    if opt["skill"]:
                        best[opt["skill"]] = max(best[opt["skill"]], opt["amount"])
                for sk, amt in best.items():
                    earned[sk] += amt
            v["earn_by_scene"].append((sid, dict(earned)))
        v["earn_total"] = dict(earned)
        out[vol] = v
    return out


def render(vols):
    L = []
    L.append("# THE VN CONSEQUENCE MAP — generated, do not edit\n")
    L.append("`python3 godot/tools/audit/consequence_map.py` draws this from the scene\n"
             "JSON in `index.json` reading order. It is the design pillar's first\n"
             "document (lore/_VISUAL_PROGRAM.md §6): what the reader can choose, what\n"
             "the game remembers, and which skill checks can actually pass.\n")
    L.append("Skill rule: an option with `\"skill\": \"<name>\"` trains that skill by\n"
             "one (or `\"amount\"`) when taken. A check passes when the skill is at or\n"
             "above `diff`. **Earnable** is the most the reader can have before the\n"
             "check's scene, taking the best option at every earlier choice.\n")
    tot_choices = sum(len(v["choices"]) for v in vols.values())
    tot_checks = sum(len(v["checks"]) for v in vols.values())
    dead = [c for v in vols.values() for c in v["checks"] if c["earnable"] < c["diff"]]
    loose = sum(1 for v in vols.values() for f in v["flags_set"] if f not in v["flags_read"])
    L.append("| | |\n|---|---|\n| choices | %d |\n| skill checks | %d |\n| checks that cannot pass | %d |\n"
             "| flags set | %d |\n| flags set and never read | %d |\n"
             % (tot_choices, tot_checks, len(dead),
                sum(len(v["flags_set"]) for v in vols.values()), loose))
    for vol, v in vols.items():
        if not v["choices"] and not v["checks"]:
            continue
        L.append("\n## Volume %d — %d scenes · %d choices · %d checks\n" % (vol, len(v["scenes"]), len(v["choices"]), len(v["checks"])))
        et = v["earn_total"]
        L.append("Skills earnable across the volume: " + (", ".join("%s %d" % (k, et[k]) for k in SKILLS if et.get(k)) or "none") + "\n")
        L.append("\n### Choices\n")
        for ch in v["choices"]:
            head = ch["prompt"] or ch["before"]
            style = " · verb coin on **%s**" % ch["hotspot"] if ch["style"] == "verb_coin" else ""
            L.append("**%s** #%d%s\n> %s\n" % (ch["scene"], ch["node"], style, head[:160]))
            for o in ch["opts"]:
                to = ("→ scene `%s`" % o["scene_to"]) if o["scene_to"] else ("→ #%s" % o["goto"] if o["goto"] is not None else "→ next")
                bits = []
                if o["check"]:
                    c = o["check"]
                    bits.append("CHECK %s ≥ %s (pass #%s / fail #%s)" % (c.get("skill"), c.get("diff"), c.get("pass"), c.get("fail")))
                if o["skill"]:
                    bits.append("trains **%s**%s" % (o["skill"], "" if o["amount"] == 1 else " +%d" % o["amount"]))
                if o["flag"]:
                    bits.append("sets `%s`%s" % (o["flag"], "" if o["val"] is True else " = %s" % o["val"]))
                if o["hide_if"]:
                    bits.append("hidden once `%s`" % o["hide_if"])
                if o["only_if"]:
                    bits.append("only if `%s`" % o["only_if"])
                L.append("- %s %s%s" % (o["text"][:90].replace("|", "¦"), to, (" — " + "; ".join(bits)) if bits else ""))
            L.append("")
        if v["checks"]:
            L.append("### Checks\n")
            L.append("| scene | skill | diff | earnable before | pass ≠ fail | verdict |\n|---|---|---|---|---|---|")
            for c in v["checks"]:
                ok = c["earnable"] >= c["diff"] and c["diff"] > 0
                verdict = "passable" if ok else ("CANNOT PASS" if c["diff"] > 0 else "always passes")
                L.append("| %s #%d | %s | %d | %d | %s | %s |" % (
                    c["scene"], c["node"], c["skill"], c["diff"], c["earnable"],
                    "yes" if c["pass"] != c["fail"] else "no — decorative", verdict))
            L.append("")
        L.append("### Flags\n")
        L.append("| flag | set at | read at |\n|---|---|---|")
        for f in sorted(set(v["flags_set"]) | set(v["flags_read"])):
            s = ", ".join("%s#%d" % (a, b) for a, b, _ in v["flags_set"].get(f, [])) or "—"
            r = ", ".join("%s#%d (%s)" % (a, b, k) for a, b, k in v["flags_read"].get(f, [])) or "**never — loose**"
            L.append("| `%s` | %s | %s |" % (f, s, r))
        L.append("")
    return "\n".join(L) + "\n"


def main():
    vols = load_volumes()
    text = render(vols)
    if "--print" in sys.argv:
        print(text)
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    dead = [c for v in vols.values() for c in v["checks"] if c["earnable"] < c["diff"]]
    print("consequence_map · %d choice(s) · %d check(s) · %d cannot pass · wrote %s"
          % (sum(len(v["choices"]) for v in vols.values()),
             sum(len(v["checks"]) for v in vols.values()), len(dead), os.path.relpath(OUT, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
