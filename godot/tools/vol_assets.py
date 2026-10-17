#!/usr/bin/env python3
"""vol_assets.py — what a set of volumes asks for, and what covers it (2026-10-17).

The user: "we'll need all the heroes and hero props and assets for vol 1-4
accounted for as well." Reads every scene of the given volumes and lists:

  · SPEAKERS — each `char` on a say / think / show node, resolved the way
    CharLayer resolves it (the static maps, then the roster's keys, then a
    look for that volume, then <key>.glb), each one: a roster entry that may
    play in that volume (Hero Studio can generate it) and whether its GLB is
    installed;
  · CG — every `cg` picture: on disk, or a roster `scene2d` entry to paint it;
  · BACKGROUNDS — every `bg` stem: on disk, a 3D preset in bg_places.json, or
    a roster `scene2d` entry;
  · BGM — every music cue: on disk or not.

    python3 godot/tools/vol_assets.py                      # vols 1-4, this branch
    python3 godot/tools/vol_assets.py --scenes DIR --vols 1,2,3,4
    python3 godot/tools/vol_assets.py --json out.json      # the full table

DIR is a scenes folder (…/resources/scenes) — e.g. one extracted from
claude/vol1-4-source-text with `git archive`, while those volumes live on
that branch. Nothing is written except --json.
"""
import argparse
import collections
import glob
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
GODOT = TOOLS.parent
ROSTER = TOOLS / "meshy_roster.json"
CHARLAYER = GODOT / "scenes" / "game" / "CharLayer.gd"
BG_PLACES = GODOT / "resources" / "vn" / "bg_places.json"
HEROES = GODOT / "assets" / "3d" / "characters" / "heroes"
# Speakers who get no model, by the text (2026-10-17 ruling): a voice through
# an earbud or a phone, a group line, an unseen speaker. Keyed (char id, vol).
VOICE_ONLY = {
    ("man", 1): "Dickens Dean before he gives his name (vol1_ch4_dream_bar shows dickens_dean)",
    ("jacob's_son", 1): "a voice in Jacob's earbud",
    ("wagner's_partner", 1): "a recorded sample in Wagner's earbud",
    ("habes", 1): "a text-message voice Faust hears",
    ("wood", 1): "the painting's frame speaking",
    ("voice_over", 1): "voice-over",
    ("a_player", 1): "one line over a cut to The Players",
    ("faust,_jacob,_wagner", 1): "the three together (each has a model)",
    ("passing_stranger", 2): "one line in passing",
    ("sentries", 3): "the starship's voice",
    ("the_girl", 4): "Dean's daughter, unseen by the text ('We don't see her yet')",
}
DEMONS = GODOT / "assets" / "3d" / "characters" / "demons"


def ref_files(ref):
    """Paths (relative to godot/) that exist in git ref `ref` under assets/ —
    the vols 1-4 branch carries some pictures this branch does not."""
    if not ref:
        return set()
    import subprocess
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "godot/assets"], cwd=GODOT.parent,
                         capture_output=True, text=True).stdout.split()
    return {p[len("godot/"):] for p in out}


def char_key(name):
    return (name or "").strip().lower().replace(" ", "_")


def static_map(const):
    """A `const NAME := { "key": "file.glb", … }` block from CharLayer.gd."""
    src = CHARLAYER.read_text()
    m = re.search(const + r"\s*:?=\s*\{(.*?)\n\}", src, re.S)
    return dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+\.glb)"', m.group(1))) if m else {}


def load_scenes(root, vols):
    out = []
    for v in vols:
        for f in sorted(glob.glob(f"{root}/vol{v}/*.json")):
            try:
                d = json.loads(Path(f).read_text())
            except ValueError:
                continue
            out.append((v, d.get("id") or Path(f).stem, d))
    return out


class Resolver:
    def __init__(self, roster):
        self.entries = [e for e in roster["entries"] if e["kind"] in ("hero", "demon")]
        self.by_slug = {e["slug"]: e for e in roster["entries"]}
        self.hero_map = static_map("PORTRAIT_3D_KEY_TO_GLB")
        self.demon_map = static_map("PORTRAIT_3D_DEMON_KEY_TO_GLB")
        self.by_file = collections.defaultdict(list)
        self.by_key = collections.defaultdict(list)
        for e in self.entries:
            self.by_file[e.get("file", "")].append(e)
            for k in [e["slug"]] + list(e.get("keys") or []):
                self.by_key[str(k)].append(e)

    @staticmethod
    def _vol_ok(e, vol):
        vs = e.get("vol") or []
        return not vs or vol in [int(x) for x in vs]

    def resolve(self, key, vol, scene_id):
        """(entry or None, how). The first entry CharLayer would try that may
        play here — installed or not, since the question is whether Hero
        Studio has it to make."""
        if key in self.demon_map:
            for e in self.by_file.get(self.demon_map[key], []):
                return e, "demon map"
        # a look of a base key staged in this volume / scene
        for e in self.entries:
            lk = e.get("look") or {}
            if not e.get("base") or vol not in [int(x) for x in lk.get("vols") or []]:
                continue
            if lk.get("scenes") and scene_id not in lk["scenes"]:
                continue
            base = self.by_slug.get(e["base"]) or {}
            if key in (base.get("keys") or []) or key in (e.get("keys") or []):
                return e, "look"
        if key in self.hero_map:
            for e in self.by_file.get(self.hero_map[key], []):
                if self._vol_ok(e, vol):
                    return e, "static map"
        for e in self.by_key.get(key, []):
            if self._vol_ok(e, vol) and not e.get("base"):
                return e, "roster key"
        for e in self.by_key.get(key, []):
            if self._vol_ok(e, vol):
                return e, "roster key (look)"
        for e in self.by_file.get(key + ".glb", []):
            if self._vol_ok(e, vol):
                return e, "file name"
        return None, ""

    @staticmethod
    def installed(e):
        f = e.get("file") or ""
        root = DEMONS if e["kind"] == "demon" else HEROES
        return bool(f) and (root / f).exists()

    def elsewhere(self, key):
        """Roster entries with this key that the volume filter turned away."""
        return sorted({e["slug"] for e in self.by_key.get(key, [])})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenes", default=str(GODOT / "resources" / "scenes"))
    ap.add_argument("--vols", default="1,2,3,4")
    ap.add_argument("--json", help="write the full table here")
    ap.add_argument("--assets-ref", default="origin/claude/vol1-4-source-text",
                    help="a git ref whose assets count as present ('' for none)")
    a = ap.parse_args()
    vols = [int(v) for v in a.vols.split(",") if v.strip()]
    roster = json.loads(ROSTER.read_text())
    res = Resolver(roster)
    scenes = load_scenes(a.scenes, vols)
    if not scenes:
        print(f"vol_assets · no scenes for vols {vols} under {a.scenes}")
        return 1
    scene2d = {}
    for e in roster["entries"]:
        if e["kind"] == "scene2d":
            for s in [e["slug"]] + list(e.get("stems") or []):
                scene2d[s] = e
    places = json.loads(BG_PLACES.read_text()).get("places", {}) if BG_PLACES.exists() else {}
    elsewhere = ref_files(a.assets_ref)

    speakers = collections.defaultdict(lambda: {"lines": 0, "shows": 0, "scenes": set(), "vols": set(), "label": ""})
    cgs = collections.defaultdict(lambda: {"scenes": set(), "caption": ""})
    bgs = collections.defaultdict(set)
    bgm = collections.defaultdict(set)
    for vol, sid, d in scenes:
        for n in d.get("nodes") or []:
            t = n.get("t")
            if t in ("say", "think", "show") and n.get("char"):
                k = char_key(n["char"])
                s = speakers[(k, vol)]
                s["lines" if t != "show" else "shows"] += 1
                s["scenes"].add(sid)
                s["label"] = s["label"] or n["char"]
            elif t == "cg" and n.get("src"):
                c = cgs[Path(n["src"]).stem]
                c["scenes"].add(sid)
                c["caption"] = c["caption"] or n.get("caption", "")
                c["src"] = n["src"]
            elif t == "bg" and n.get("src"):
                src = n["src"]
                bgs[src if src.startswith("3d:") else Path(src).stem].add(sid)
            elif t == "bgm" and n.get("src"):
                bgm[n["src"]].add(sid)

    table = {"speakers": [], "cg": [], "bg": [], "bgm": []}
    print(f"vol_assets · vols {vols} · {len(scenes)} scenes · from {a.scenes}\n")
    print("SPEAKERS (char id · vol · lines/shows → roster entry · GLB)")
    miss = 0
    for (k, vol), s in sorted(speakers.items(), key=lambda kv: (kv[0][1], -kv[1]["lines"], kv[0][0])):
        scene0 = sorted(s["scenes"])[0]
        e, how = res.resolve(k, vol, scene0)
        row = {"key": k, "vol": vol, "label": s["label"], "lines": s["lines"], "shows": s["shows"],
               "scenes": sorted(s["scenes"]), "entry": e["slug"] if e else None, "how": how,
               "installed": bool(e and res.installed(e)), "elsewhere": [] if e else res.elsewhere(k)}
        table["speakers"].append(row)
        voice = VOICE_ONLY.get((k, vol))
        row["voice_only"] = voice
        if not e and not voice:
            miss += 1
        mark = "voice" if voice and not e else "MISS" if not e else ("glb " if row["installed"] else "make")
        extra = f"  (other vols: {', '.join(row['elsewhere'])})" if row["elsewhere"] else ""
        extra = f"  ({voice})" if voice and not e else extra
        print(f"  {mark} {k:28s} v{vol} {s['lines']:4d}/{s['shows']:<3d} → {row['entry'] or '—'}{extra}")
    n_sp = len(speakers)
    n_glb = sum(r["installed"] for r in table["speakers"])
    n_voice = sum(1 for r in table["speakers"] if r["voice_only"] and not r["entry"])
    print(f"  {n_sp} speaker(s): {n_glb} with a model installed, {n_sp - n_glb - miss - n_voice} in the roster to make, "
          f"{n_voice} voice only, {miss} with no entry\n")

    print("CG (picture · scenes → on disk / scene2d entry)")
    cg_open = 0
    for stem, c in sorted(cgs.items()):
        on_disk = (GODOT / c["src"]).exists() or c["src"] in elsewhere
        e = scene2d.get(stem)
        state = "disk" if on_disk else ("make" if e else "MISS")
        cg_open += state == "MISS"
        table["cg"].append({"stem": stem, "src": c["src"], "caption": c["caption"], "scenes": sorted(c["scenes"]),
                            "on_disk": on_disk, "entry": e["slug"] if e else None})
        print(f"  {state} {stem:40s} {len(c['scenes'])}  {c['caption'][:50]}")
    print(f"  {len(cgs)} CG picture(s), {cg_open} with neither a file nor an entry\n")

    print("BACKGROUNDS (stem → on disk / 3D preset / scene2d entry)")
    fits = collections.Counter()
    bg_open = 0
    for stem, sids in sorted(bgs.items()):
        if stem.startswith("3d:"):          # the scene names a 3D set itself (the merged vols 1-2)
            fits["3d"] += 1
            table["bg"].append({"stem": stem, "scenes": sorted(sids), "on_disk": False, "to": stem,
                                "fit": "exact", "entry": None})
            continue
        on_disk = any((GODOT / "assets" / "backgrounds" / f"{stem}.{x}").exists()
                      or f"assets/backgrounds/{stem}.{x}" in elsewhere for x in ("jpg", "png", "webp"))
        p = places.get(stem) or {}
        e = scene2d.get(stem)
        state = "disk" if on_disk else ("3d" if p.get("to") else ("make" if e else
                ("build" if p.get("build") else "MISS")))
        fits[state] += 1
        bg_open += state == "MISS"
        table["bg"].append({"stem": stem, "scenes": sorted(sids), "on_disk": on_disk, "to": p.get("to"),
                            "fit": p.get("fit"), "entry": e["slug"] if e else None})
        if state in ("MISS", "build"):
            print(f"  {state:5s} {stem:40s} {len(sids)}  fit={p.get('fit')}  build={p.get('build')}")
    print(f"  {len(bgs)} stem(s): " + ", ".join(f"{k} {v}" for k, v in sorted(fits.items())) + "\n")

    print("BGM (cue → on disk)")
    bgm_open = 0
    for src, sids in sorted(bgm.items()):
        # any extension counts: AudioMgr falls back across .ogg / .wav / .mp3
        alts = [src] + [str(Path(src).with_suffix(x)) for x in (".ogg", ".wav", ".mp3")]
        ok = any((GODOT / a).exists() or a in elsewhere for a in alts)
        bgm_open += not ok
        table["bgm"].append({"src": src, "scenes": sorted(sids), "on_disk": ok})
        if not ok:
            print(f"  MISS {src}  ({len(sids)} scene(s))")
    print(f"  {len(bgm)} cue(s), {bgm_open} not on disk\n")

    if a.json:
        Path(a.json).write_text(json.dumps(table, indent=1) + "\n")
    print(f"vol_assets · speakers {miss} unmatched · cg {cg_open} · bg {bg_open} · bgm {bgm_open} open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
