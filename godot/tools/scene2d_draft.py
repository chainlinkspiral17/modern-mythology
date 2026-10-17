#!/usr/bin/env python3
"""scene2d_draft.py — a Hero Studio entry for every picture the text shows (2026-10-17).

The user: "we'll need all the heroes and hero props and assets for vol 1-4
accounted for as well." A scene's `cg` node and a `bg` that no 3D set plays
(bg_places.json fit "2d") name a picture under assets/ that was never made.
This drafts one `scene2d` roster entry per missing picture, so Hero Studio
can paint and install it:

  · canon = the scene's own words around the picture, verbatim: a CG's
    caption and the narration just before and after it; a background's
    interlude card and the narration after the cut, up to the next one;
  · prompt = the caption / place card, appended as direction;
  · notes say it is a draft: read the quotes before spending credits.

It never overwrites: a stem that already has an entry is skipped, so a hand-
edited entry survives a re-run after the text changes.

    python3 godot/tools/scene2d_draft.py --scenes DIR [--vols 1,2,3,4] [--dry-run]

DIR is a scenes folder (…/resources/scenes); see vol_assets.py.
"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
GODOT = TOOLS.parent
ROSTER = TOOLS / "meshy_roster.json"
BG_PLACES = GODOT / "resources" / "vn" / "bg_places.json"
QUOTES = 4
QUOTE_CHARS = 320
# real people the text fictionalises: their names stay out of image prompts
# (the roster's prompt_name rule — the generator draws the text, not a likeness)
NO_NAMES = re.compile(r"Hubbard|Parsons|Northrup", re.I)


def sentences(text, limit):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    out = ""
    for s in re.split(r"(?<=[.!?])\s+", text):
        if len(out) + len(s) + 1 > limit:
            break
        out = (out + " " + s).strip()
    return out or text[:limit].rsplit(" ", 1)[0] + "…"


def quote_list(nodes, idxs, src):
    out = []
    for i in idxs:
        n = nodes[i]
        t = n.get("text") if n.get("t") == "narrate" else None
        if n.get("t") == "interlude":
            t = " · ".join(x for x in (n.get("text"), n.get("sub")) if x)
        if not t or NO_NAMES.search(t):
            continue
        q = sentences(t, QUOTE_CHARS)
        if q and all(q != o["text"] for o in out):
            out.append({"src": src, "text": q})
        if len(out) >= QUOTES:
            break
    return out


def ref_files(ref):
    """Paths (relative to godot/) that exist in git ref `ref` under assets/ —
    the vols 1-4 branch carries some pictures this branch does not."""
    if not ref:
        return set()
    import subprocess
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "godot/assets"], cwd=GODOT.parent,
                         capture_output=True, text=True).stdout.split()
    return {p[len("godot/"):] for p in out}


def humanize(stem):
    s = re.sub(r"^vol\d+_", "", stem)
    m = re.match(r"scumm_(.+?)(_vga)?$", s)
    if m:              # Dean's dream journal kept as a graphic adventure (vol 2 ch vii)
        return "the dream-journal adventure — " + m.group(1).replace("_", " ")
    return s.replace("_", " ")


def place_name(stem, note):
    """bg_places' note when it names the place; a one- or two-word note
    ("abstract", "an insert", "game screen") only qualifies the stem."""
    note = (note or "").strip()
    if len(note) > 20:
        return note
    return f"{humanize(stem)} ({note})" if note else humanize(stem)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--vols", default="1,2,3,4")
    ap.add_argument("--assets-ref", default="origin/claude/vol1-4-source-text",
                    help="a git ref whose assets count as present ('' for none)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    vols = [int(v) for v in a.vols.split(",") if v.strip()]
    text = ROSTER.read_text()
    roster = json.loads(text)
    have = {e["slug"] for e in roster["entries"]}
    places = json.loads(BG_PLACES.read_text()).get("places", {})
    elsewhere = ref_files(a.assets_ref)
    drafts = {}
    for v in vols:
        for f in sorted(glob.glob(f"{a.scenes}/vol{v}/*.json")):
            d = json.loads(Path(f).read_text())
            sid = d.get("id") or Path(f).stem
            src = f"vol{v}/{Path(f).name}"
            nodes = d.get("nodes") or []
            for i, n in enumerate(nodes):
                if n.get("t") not in ("cg", "bg") or not n.get("src"):
                    continue
                stem = Path(n["src"]).stem
                if n["t"] == "bg":
                    p = places.get(stem) or {}
                    if p.get("fit") != "2d" or p.get("to"):
                        continue
                    if (GODOT / "assets" / "backgrounds" / f"{stem}.jpg").exists() \
                            or f"assets/backgrounds/{stem}.jpg" in elsewhere:
                        continue
                    after = []
                    for j in range(i + 1, min(len(nodes), i + 14)):
                        if nodes[j].get("t") in ("bg", "cg", "jump", "end"):
                            break
                        after.append(j)
                    before = [j for j in range(max(0, i - 2), i) if nodes[j].get("t") == "interlude"]
                    quotes = quote_list(nodes, before + after, src)
                    label = next((" · ".join(x for x in (nodes[j].get("text"), nodes[j].get("sub")) if x)
                                  for j in before + after if nodes[j].get("t") == "interlude"), "")
                    role, file = "bg", f"backgrounds/{stem}.jpg"
                    name = place_name(stem, p.get("note"))
                    direction = f"The place: {label or name}. An establishing view of the place itself."
                else:
                    if (GODOT / n["src"]).exists() or n["src"] in elsewhere:
                        continue
                    idxs = list(range(max(0, i - 3), i)) + list(range(i + 1, min(len(nodes), i + 3)))
                    quotes = quote_list(nodes, idxs, src)
                    cap = (n.get("caption") or "").strip()
                    role, file = "cg", f"cg/{stem}.jpg"
                    name = cap if cap and not NO_NAMES.search(cap) else humanize(stem)
                    direction = f"The moment: {name}." if name else ""
                e = drafts.get(stem)
                if e is None:
                    if stem in have:
                        continue
                    e = drafts[stem] = {
                        "slug": stem, "kind": "scene2d", "name": name[:90], "file": file, "vol": [v],
                        "keys": [stem], "tag": f"vol{v} · {role.upper()} · {name[:80]}",
                        "aspect": "16:9", "pose": None, "role": role, "scenes": [],
                        "prompt": direction, "prompt_mode": "append", "canon": [],
                        "notes": "DRAFT (scene2d_draft.py, 2026-10-17): the quotes are the scene's own words around "
                                 "this picture. Read them before spending credits; trim any that describe a "
                                 "different moment, and add `lettering` when the picture carries words."}
                if sid not in e["scenes"]:
                    e["scenes"].append(sid)
                for q in quotes:
                    if len(e["canon"]) < QUOTES and all(q["text"] != o["text"] for o in e["canon"]):
                        e["canon"].append(q)
    new = list(drafts.values())
    for e in new:
        if not e["canon"]:
            e["notes"] += " NO QUOTES: the text says nothing around it — the prompt is all the generator gets."
    print(f"scene2d_draft · {len(new)} new entr{'y' if len(new) == 1 else 'ies'} "
          f"({sum(e['role'] == 'cg' for e in new)} CG, {sum(e['role'] == 'bg' for e in new)} backgrounds), "
          f"{sum(not e['canon'] for e in new)} without quotes")
    if a.dry_run or not new:
        for e in new[:10]:
            print("  ", e["slug"], "·", e["name"], "·", len(e["canon"]), "quote(s)")
        return 0
    roster["entries"].extend(new)
    ROSTER.write_text(json.dumps(roster, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
