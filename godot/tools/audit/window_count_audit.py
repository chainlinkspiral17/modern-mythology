#!/usr/bin/env python3
"""window_count_audit.py — how many windows each set has (2026-10-20). A report.

The Deck: "interiors need more windows, as do exteriors." / "still in the too
boxy phase". A room with one window (or none) reads as a box; a street whose
facades are blank reads as a set. This counts the window UNITS each builder
makes — one per kit window (make_window's FrameT), one per pane cluster a
builder drew itself (…Window…/…Win_…/…Pane… parts grouped within 0.6 m) —
and ranks the sets by story lines per window, most-played and window-poorest
first. No gate: the list is the drafting program's queue for the window pass.

    python3 godot/tools/audit/window_count_audit.py            # text
    python3 godot/tools/audit/window_count_audit.py --json out.json
"""
import glob
import json
import math
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GODOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BUILDERS = os.path.join(GODOT, "tools", "blender", "locales")

WIN_RE = re.compile(r"(^|_)(window|windows|win|pane|panes|glazing|storefront)(_|$|\d)", re.I)
SKIP_RE = re.compile(r"(curtain|blind|sill|stool|apron|casing|trim|frame_?ring|view_|thru_|sign|screen|tint|band)", re.I)


def lines_by_locale():
    """Story lines played on each locale (any preset of it, 3d: or bg_places)."""
    src = open(os.path.join(GODOT, "scripts", "vn", "Background3D.gd")).read()
    ps = {m.group(1): m.group(2) for m in re.finditer(
        r'^\t"([a-z0-9_]+)": \{\n\t\t"scene": "res://scenes/locales/([a-z0-9_]+)\.tscn"', src, re.M)}
    places_p = os.path.join(GODOT, "resources", "vn", "bg_places.json")
    places = json.load(open(places_p))["places"] if os.path.exists(places_p) else {}
    out = defaultdict(int)
    for f in glob.glob(os.path.join(GODOT, "resources", "scenes", "*", "*.json")):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        sid, cur = d.get("id", ""), None
        for n in d.get("nodes", []):
            if not isinstance(n, dict):
                continue
            if n.get("t") == "bg" and isinstance(n.get("src"), str):
                s = n["src"]
                pre = s[3:] if s.startswith("3d:") else None
                if pre is None:
                    p = places.get(os.path.splitext(os.path.basename(s))[0]) or {}
                    to = str((p.get("by_scene") or {}).get(sid) or p.get("to") or "")
                    pre = to[3:] if to.startswith("3d:") else None
                cur = ps.get(pre) if pre else None
            elif cur and n.get("text"):
                out[cur] += 1
    return out


def count(boxes):
    kit = {n[:-len("_FrameT")] for n, _, _ in boxes if n.endswith("_FrameT")}
    loose = [(n, c) for n, c, _ in boxes
             if WIN_RE.search(n) and not SKIP_RE.search(n) and not any(n.startswith(k) for k in kit)]
    clusters = []
    for n, c in loose:
        for cl in clusters:
            if math.dist(cl, c) < 0.6:
                break
        else:
            clusters.append(c)
    return len(kit), len(clusters)


def main():
    import prop_overlap_audit as P
    P.A.install_stubs()
    lines = lines_by_locale()
    rows = []
    for b in sorted(glob.glob(os.path.join(BUILDERS, "build_*.py"))):
        loc = os.path.basename(b)[6:-3]
        old = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            boxes, _ = P.record_builder(b)
        except Exception:
            boxes = None
        finally:
            sys.stdout = old
        if not boxes:
            continue
        k, c = count(boxes)
        rows.append({"locale": loc, "kit_windows": k, "drawn_windows": c, "windows": k + c,
                     "lines": lines.get(loc, 0)})
    rows.sort(key=lambda r: (-(r["lines"] / max(1, r["windows"])), r["locale"]))
    if "--json" in sys.argv:
        json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    print("%-30s %6s %8s %6s %6s" % ("locale", "lines", "windows", "kit", "drawn"))
    for r in rows:
        if r["lines"] == 0:
            continue
        print("%-30s %6d %8d %6d %6d" % (r["locale"], r["lines"], r["windows"], r["kit_windows"], r["drawn_windows"]))
    played = [r for r in rows if r["lines"] > 0]
    print("window_count_audit · %d played set(s) · %d with 0-1 windows" % (
        len(played), sum(1 for r in played if r["windows"] <= 1)))


if __name__ == "__main__":
    main()
