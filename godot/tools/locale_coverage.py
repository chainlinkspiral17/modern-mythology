#!/usr/bin/env python3
"""
locale_coverage.py — which locale GLBs are missing, and which matter.

Locale GLBs are LOCAL build artifacts (built on the Deck via
godot/tools/blender/run_cathedral.sh; never committed). When one is
missing, Godot logs a load error at boot and the scene falls back to
the flat bg. This report cross-references:

  1. every camera preset in Background3D.gd (`requires_glb`),
  2. how many story lines actually USE each preset (`3d:<preset>`
     directives across all scene JSONs, counted per volume),
  3. what's actually on disk in assets/3d/locales/,
  4. which build_*.py produces each missing GLB,

and prints a build-priority list: run the top commands, unlock the
most scenes. Run it ON THE DECK (where the GLBs live):

    python3 godot/tools/locale_coverage.py
    python3 godot/tools/locale_coverage.py --all      # include built ones
"""
import json, os, re, sys, glob, collections

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BG3D = os.path.join(ROOT, "scripts", "vn", "Background3D.gd")
SCENES = os.path.join(ROOT, "resources", "scenes")
LOCALES = os.path.join(ROOT, "assets", "3d", "locales")
BUILDERS = os.path.join(ROOT, "tools", "blender")


def presets_from_bg3d():
    """preset_id -> glb res path (only presets that require a GLB)."""
    src = open(BG3D, encoding="utf-8").read()
    out = {}
    # entries look like: "diner_interior": { ... "requires_glb": "res://assets/3d/locales/diner.glb" ... }
    for m in re.finditer(r'"(\w+)"\s*:\s*\{(.*?)\}', src, re.S):
        pid, body = m.group(1), m.group(2)
        g = re.search(r'"requires_glb"\s*:\s*"([^"]+)"', body)
        if g:
            out[pid] = g.group(1)
    return out


def usage_counts():
    """preset_id -> {vol: count} from 3d:<preset> bg directives."""
    counts = collections.defaultdict(collections.Counter)
    for path in glob.glob(os.path.join(SCENES, "vol*", "*.json")):
        vol = os.path.basename(os.path.dirname(path))
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        for n in d.get("nodes", []):
            src = str(n.get("src", ""))
            if src.startswith("3d:"):
                counts[src[3:].strip()][vol] += 1
    return counts


def builder_for(glb_res):
    base = os.path.splitext(os.path.basename(glb_res))[0]
    for cand in (f"build_{base}.py",):
        hits = glob.glob(os.path.join(BUILDERS, "**", cand), recursive=True)
        if hits:
            return os.path.basename(hits[0])
    # fuzzy: any build script whose name contains the base (or vice versa)
    for p in glob.glob(os.path.join(BUILDERS, "**", "build_*.py"), recursive=True):
        name = os.path.basename(p)[6:-3]
        if name in base or base in name:
            return os.path.basename(p)
    return "?"


def main():
    show_all = "--all" in sys.argv
    presets = presets_from_bg3d()
    usage = usage_counts()

    rows = []
    for pid, glb_res in presets.items():
        rel = glb_res.replace("res://", "")
        on_disk = os.path.exists(os.path.join(ROOT, rel))
        n = sum(usage.get(pid, {}).values())
        vols = "+".join(sorted(usage.get(pid, {}).keys())) or "-"
        rows.append((n, pid, os.path.basename(rel), on_disk, vols))

    rows.sort(key=lambda r: (-r[0], r[1]))
    missing = [r for r in rows if not r[3]]
    built = [r for r in rows if r[3]]

    print("LOCALE COVERAGE · %d presets require a GLB · %d built · %d missing"
          % (len(rows), len(built), len(missing)))
    print()
    if missing:
        print("MISSING (build-priority order · scenes = story lines that need it):")
        print("  %-6s %-28s %-30s %-10s %s" % ("scenes", "preset", "glb", "vols", "build with"))
        for n, pid, glb, _, vols in missing:
            b = builder_for("res://x/" + glb)
            print("  %-6d %-28s %-30s %-10s ./run_cathedral.sh %s" % (n, pid, glb, vols, b))
        top = [r for r in missing if r[0] > 0][:8]
        if top:
            print()
            print("Suggested next Deck session (copy-paste, from godot/tools/blender):")
            seen = set()
            for n, pid, glb, _, vols in top:
                b = builder_for("res://x/" + glb)
                if b != "?" and b not in seen:
                    seen.add(b)
                    print("  ./run_cathedral.sh %s" % b)
    else:
        print("All required GLBs are on disk. Clean boot expected.")
    if show_all and built:
        print()
        print("BUILT:")
        for n, pid, glb, _, vols in built:
            print("  %-6d %-28s %-30s %s" % (n, pid, glb, vols))
    # unused-but-required presets are still listed (0 scenes) — they
    # matter for the gauntlet/menus which don't use 3d: directives.
    return 0


if __name__ == "__main__":
    sys.exit(main())
