#!/usr/bin/env python3
"""Shot-cue coverage audit — are the scripts' inserts landing on
anything?

Born 2026-08-12 from the user's note that the vol7 cabin chapters
were "mostly just solid color scenes." The cause was not lazy
direction — those chapters are richly directed — but that a cue
with no matching Marker3D falls back to a BLIND ZOOM: VnDirector
punches the fov to 35 (insert) or 45 (closeup) on the SAME preset
vantage, so the frame fills with whatever flat surface happened to
be in the middle of the wide. Twenty-one [shot:insert bowls] cues
in vol 7 pointed at a table that had no bowls modeled on it.

This audit reads every scene JSON, tracks which 3D background is
in effect at each node, collects the [shot:<type> <id>] cues that
fire against it, and checks the locale's .tscn for the marker
`shot_<type>_<id>` that VnDirector would look for. Missing markers
are reported per locale, ranked by how many cues land blind.

CHARACTER closeups are excluded: `[shot:closeup tem]` is meant to
be answered by the 3D cast (Background3D.CAST_ENABLED), and while
that is off a lens-only punch-in is the intended fallback. What
this hunts is OBJECT cues — inserts, and closeups of things —
which are supposed to frame a specific prop.

Usage:
    python3 godot/tools/audit/shot_marker_audit.py          # summary
    python3 godot/tools/audit/shot_marker_audit.py --all    # every gap
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SCENES = os.path.join(ROOT, "resources", "scenes")
LOCALES_TSCN = os.path.join(ROOT, "scenes", "locales")
BG3D = os.path.join(ROOT, "scripts", "vn", "Background3D.gd")

CUE = re.compile(r"\[shot:([a-z]+)(?:\s+([a-z0-9_]+))?~?\]")

# Cast-answered cues: character closeups. Everything else is an
# object cue and wants a marker.
CAST_TYPES = {"closeup"}
# Known character ids — a closeup of one of these is cast work, not
# a prop frame. Harvested from the say/char fields at runtime.
NEVER_MARKER = {"establish", "wide", "reset"}


def preset_to_scene():
    """preset_id -> the EXACT res:// scene path the preset declares.

    Resolving by basename instead bit once (2026-08-12): the repo
    carries both scenes/cathedral.tscn (the real set, with markers)
    and an orphan scenes/locales/cathedral.tscn (a legacy shell with
    none). A basename search hit the orphan and reported the model
    chapter as having zero coverage. Trust the preset's own path.
    """
    src = open(BG3D).read()
    out = {}
    for m in re.finditer(r'"(\w+)":\s*\{(.*?)\n\t\},', src, re.S):
        pid, body = m.group(1), m.group(2)
        sm = re.search(r'"scene":\s*"res://([\w/]+\.tscn)"', body)
        if sm:
            out[pid] = sm.group(1)
    return out


def markers_in(res_rel_path):
    path = os.path.join(ROOT, res_rel_path)
    if not os.path.exists(path):
        return None
    src = open(path).read()
    return set(re.findall(r'\[node name="(shot_[\w]+)"', src))


# ── Does the cued OBJECT even exist? ───────────────────────────
# The bowls lesson (2026-08-12): [shot:insert bowls] fired 21x in
# vol 7 at Olaf's two carved bowls — the volume's central image —
# which had never been modeled. A missing MARKER is a framing bug;
# a missing OBJECT is an art bug, and no marker audit can see it.
# So for each blind cue we also ask whether the locale's BUILDER
# emits anything whose name resembles the cue id.
BUILDERS = os.path.join(ROOT, "tools", "blender", "locales")
BUILDERS_ALT = os.path.join(ROOT, "tools", "blender")
# Cue ids that name a person, a view, or an abstraction — never a
# prop the builder could carry.
NOT_PROPS = {
    "face", "faces", "hands", "hand", "figure", "eyes", "eye",
    "mouth", "feet", "shoulder", "silhouette", "reflection",
    "sky", "light", "dark", "nothing", "everything", "both",
}
# Cue id -> extra word stems to accept in geometry names.
SYNONYMS = {
    "bowls": ["bowl"], "phone": ["phone", "handset", "landline"],
    "charred_wood": ["char", "burn", "ember", "ash"],
    "coffee": ["coffee", "pot", "mug", "carafe", "percolator"],
    "truck": ["truck", "pickup", "van"],
    "crow": ["crow", "bird", "corvid"],
    "notebook": ["notebook", "note", "journal", "ledger"],
    "window": ["window", "win_", "sash", "pane"],
    "tide_pool": ["tide", "pool", "anemone"],
    "cedar": ["cedar"], "stick": ["stick", "cart", "sleeve"],
    "hexagon": ["hex"], "patch": ["patch", "salal", "moss"],
    "canvas": ["canvas", "easel", "painting"],
    "model_city": ["diorama", "model", "city"],
    "french_toast": ["toast", "skillet", "plate"],
    "package": ["package", "parcel", "box"],
    "laptop": ["laptop", "monitor", "screen"],
    "photograph": ["photo", "frame", "polaroid"],
    "mural": ["nebula", "mural"],
    "unit": ["unit"],
    "marquee": ["marquee"],
    "pot_roast": ["potroast"],
    "eviction_notice": ["evictionnotice", "evictionghost"],
    "sink_light": ["undercab", "sink"],
    "till": ["register"],
    "speak_spell": ["speakspell"],
    "speak_and_spell": ["speakspell"],
    "landline": ["landline", "phone"],
    "iced_tea": ["icedtea"],
    "cigarette": ["cig", "ashtray"],
    "steamship": ["minstral", "steamship", "hull"],
    "folding_chair": ["eileen_chair", "foldingchair"],
    "drum_kit": ["drumkit", "kick", "snare", "hihat"],
    "floorboards": ["floorboard", "board", "cavity"],
    "tv": ["bar_tv", "television", "tv_screen"],
    "telecaster": ["tele", "guitar"],
    "doorknob": ["doorknob", "latch", "knob"],
    "card": ["callingcard", "card"],
    "doohickey": ["doohickey", "onyx"],
}


def builder_names(locale_basename):
    for cand in (os.path.join(BUILDERS, "build_%s.py" % locale_basename),
                 os.path.join(BUILDERS_ALT, "build_%s.py" % locale_basename)):
        if os.path.exists(cand):
            src = open(cand).read()
            return set(x.lower() for x in re.findall(
                r'(?:make_\w+|_mb|_mc)\(\s*f?"([^"]+)"', src))
    return None


def object_exists(locale_basename, cue_id):
    names = builder_names(locale_basename)
    if names is None:
        return None
    stems = SYNONYMS.get(cue_id, []) + [cue_id, cue_id.rstrip("s")]
    blob = " ".join(names)
    for s in stems:
        if len(s) >= 3 and s.replace("_", "") in blob.replace("_", ""):
            return True
    return False


def main():
    show_all = "--all" in sys.argv
    props_mode = "--props" in sys.argv
    p2s = preset_to_scene()
    chars = set()
    # First pass: learn the character ids so closeups of PEOPLE are
    # not reported as missing props.
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn)))
            except Exception:
                continue
            for n in j.get("nodes", []):
                c = n.get("char")
                if isinstance(c, str) and c:
                    chars.add(c.lower())

    gaps = collections.defaultdict(collections.Counter)
    seen_cues = collections.Counter()
    no_marker_support = collections.Counter()
    for dirpath, _dirs, files in os.walk(SCENES):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            try:
                j = json.load(open(os.path.join(dirpath, fn)))
            except Exception:
                continue
            cur = ""
            for n in j.get("nodes", []):
                if n.get("t") == "bg":
                    src = str(n.get("src") or "")
                    cur = src[3:] if src.startswith("3d:") else ""
                if not cur:
                    continue
                for typ, sid in CUE.findall(json.dumps(n)):
                    if typ in NEVER_MARKER or not sid:
                        continue
                    if typ in CAST_TYPES and sid in chars:
                        continue
                    # A closeup id that is one word of a canon char
                    # id is still a cast cue — "closeup miller" for
                    # chief_miller / mrs_miller. 16 phantom-blind
                    # cues read this way before the alias check.
                    if typ in CAST_TYPES and any(
                            sid == part for c in chars
                            for part in c.split("_")):
                        continue
                    seen_cues[(cur, typ, sid)] += 1

    for (preset, typ, sid), n in seen_cues.items():
        tscn = p2s.get(preset)
        if tscn is None:
            no_marker_support[preset] += n
            continue
        have = markers_in(tscn)
        if have is None:
            no_marker_support[preset] += n
            continue
        if ("shot_%s_%s" % (typ, sid)) not in have:
            gaps[preset][(typ, sid)] += n

    total_blind = sum(sum(c.values()) for c in gaps.values())
    print("shot_marker_audit · %d object cues across %d 3D presets"
          % (sum(seen_cues.values()), len({k[0] for k in seen_cues})))
    if no_marker_support:
        print("   (%d cues on presets with no resolvable .tscn — skipped)"
              % sum(no_marker_support.values()))
    ranked = sorted(gaps.items(), key=lambda kv: -sum(kv[1].values()))
    for preset, counter in ranked if show_all else ranked[:14]:
        print("== %-28s %d blind cue(s), %d distinct"
              % (preset, sum(counter.values()), len(counter)))
        for (typ, sid), n in counter.most_common(None if show_all else 6):
            print("     %2dx  shot_%s_%s" % (n, typ, sid))
    if not show_all and len(ranked) > 14:
        print("   … %d more presets (--all)" % (len(ranked) - 14))
    print("\n%d blind object cue(s) across %d preset(s)"
          % (total_blind, len(gaps)))

    if props_mode:
        # The bowls hunt: cued, unmarked, AND absent from the builder.
        print("\n── cued but apparently NOT MODELED "
              "(art gaps, ranked) ──")
        missing = collections.Counter()
        where = {}
        for preset, counter in gaps.items():
            tscn = p2s.get(preset, "")
            base = os.path.basename(tscn).replace(".tscn", "")
            for (typ, sid), n in counter.items():
                if sid in NOT_PROPS:
                    continue
                ex = object_exists(base, sid)
                if ex is False:
                    missing[(base, sid)] += n
                    where.setdefault((base, sid), set()).add(preset)
        for (base, sid), n in missing.most_common(30):
            print("   %2dx  %-26s %s" % (n, base, sid))
        print("\n%d cue(s) name an object no builder emits, "
              "across %d locale/object pair(s)"
              % (sum(missing.values()), len(missing)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
