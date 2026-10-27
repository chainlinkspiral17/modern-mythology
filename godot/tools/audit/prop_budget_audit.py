#!/usr/bin/env python3
"""prop_budget_audit — what the hero props cost each set (2026-10-27).

The user: "accounting for both storage space and memory cost. Perhaps props
should be lighter load than the character models." The roster's `budgets`
give every prop a class by its `tier`; this gate holds the sets to them.

For every scene that places HeroProps (`glb_path = "res://assets/3d/props/…"`):
  NO_ENTRY   a placed model with no prop entry in meshy_roster.json (nothing
             would ever generate it, and nothing budgets it)
  UNDER_TIER a prop placed bigger than its tier carries: over 0.6 m needs
             medium, over 2.5 m large (a small prop's 4k triangles and one
             1024 px map, stretched over a car)
  OVER_SET   a set whose prop models together would take more video memory
             than SET_CAP (two characters' worth). Each model counts once
             however often the set places it: Godot shares the mesh and maps.
             Counted per PRESET (2026-10-27, draft 2): a HeroProp named
             `HP_<Name>__<preset>…` loads only in those presets, an untagged
             one in all; the set's figure is its heaviest preset (the Kwik
             Stop never holds the hood-up car and the plain one at once).

Estimates come from meshy_pipeline.budget_estimate (the same numbers Hero
Studio shows). Nonzero exit on any finding.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(GODOT, "tools"))
import meshy_pipeline as M  # noqa: E402

TIER_FOR_SIZE = ((0.6, "small"), (2.5, "medium"), (1e9, "large"))
TIER_RANK = {"small": 0, "medium": 1, "large": 2}
SET_CAP = 2 * M.budget_estimate("hero")["vram"]
NODE = re.compile(r'\[node name="([^"]+)"[^\n]*\n(?:(?!\[)[^\n]*\n)*?glb_path = "res://assets/3d/props/([^"]+)"\n'
                  r'(?:(?!\[)[^\n]*\n)*?size_m = ([0-9.]+)')


def need_tier(size):
    return next(t for lim, t in TIER_FOR_SIZE if size <= lim)


def main():
    roster = M.load_roster()
    props = {e["file"]: e for e in roster["entries"] if e["kind"] == "prop"}
    findings, sets = [], []
    for root, _dirs, files in os.walk(os.path.join(GODOT, "scenes")):
        for f in sorted(files):
            if not f.endswith(".tscn"):
                continue
            path = os.path.join(root, f)
            text = open(path, encoding="utf-8", errors="ignore").read()
            placed = NODE.findall(text)
            if not placed:
                continue
            rel = os.path.relpath(path, GODOT)
            models = set()
            for node, glb, size in placed:
                e = props.get(glb)
                if e is None:
                    findings.append(("NO_ENTRY", rel, f"{node}: {glb} has no prop entry in meshy_roster.json"))
                    continue
                tier = e.get("tier") or "medium"
                want = need_tier(float(size))
                if TIER_RANK[tier] < TIER_RANK[want]:
                    findings.append(("UNDER_TIER", rel, f"{node}: {e['slug']} placed at {float(size):.2f} m, "
                                                        f"tier {tier} (needs {want})"))
                models.add(glb)
            total, _n = M.set_prop_vram(text, props)
            sets.append((total, rel, len(models), len(placed)))
            if total > SET_CAP:
                findings.append(("OVER_SET", rel, f"{len(models)} prop model(s) ~{total / 1e6:.1f} MB video memory "
                                                  f"(cap {SET_CAP / 1e6:.1f} MB, two characters)"))
    for cls, rel, msg in findings:
        print(f"   {cls:10} {rel}  {msg}")
    worst = max(sets) if sets else (0, "-", 0, 0)
    print(f"prop_budget_audit · {len(sets)} set(s) place props · {sum(s[3] for s in sets)} placement(s) · "
          f"heaviest {worst[1].split('/')[-1]} ~{worst[0] / 1e6:.1f} MB (cap {SET_CAP / 1e6:.1f}) · "
          f"{len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
