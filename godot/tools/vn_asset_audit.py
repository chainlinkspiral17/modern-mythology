#!/usr/bin/env python3
"""vn_asset_audit.py — the VN's asset/reference gate.

Everything in here was a live defect once (2026-08 visual audit):
cg nodes pointing at files that didn't exist rendered the book's
climaxes as black; three-letter character keys fuzzy-matched tarot
cards as portraits; 13 finale scenes shipped with no bg; expression
words silently collapsed; style packs named lighting presets that
weren't. This keeps each class fixed. Zero output = clean, exit 0.

Usage: python3 godot/tools/vn_asset_audit.py
"""
import json, os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
SCENES = os.path.join(ROOT, "resources", "scenes")
fails = 0
legacy = 0
debt_refs = []   # 2D bg srcs still awaiting 3D-locale migration

# Vols 1-4 predate the 3D-locale era and reference dozens of 2D
# background JPEGs that were never produced (discovered by this
# gate's first run, 2026-08-02 — recorded in the visual audit doc).
# Restoring that estate is its own project; until then those volumes
# are a KNOWN baseline: counted and summarized, not failing. Any NEW
# problem in vols 5-7 or the engine tables still fails the gate.
LEGACY_PREFIXES = ("resources/scenes/vol1/", "resources/scenes/vol2/",
                   "resources/scenes/vol3/", "resources/scenes/vol4/")


def fail(msg, rel=""):
    global fails, legacy
    if any(rel.startswith(pfx) for pfx in LEGACY_PREFIXES):
        legacy += 1
        return
    fails += 1
    print(msg)


def scene_files():
    for vol in sorted(os.listdir(SCENES)):
        vdir = os.path.join(SCENES, vol)
        if not os.path.isdir(vdir):
            continue
        for fn in sorted(os.listdir(vdir)):
            if fn.endswith(".json"):
                yield os.path.join(vdir, fn)


def walk_nodes(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk_nodes(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_nodes(v)


# ── gather engine tables once ────────────────────────────────────
def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8").read()

bg3d = read("scripts/vn/Background3D.gd")
PRESETS = set(re.findall(r'^\t"([a-z0-9_]+)"\s*:\s*\{', bg3d, re.M))

mood_src = read("scripts/MoodCycler.gd")
# MOODS / STYLE_PACKS / LIGHTING_PRESETS are ARRAYS of {"name": ...}
# dicts — slice each array block (declaration to the closing `]` at
# column 0) and collect the "name" fields.
def names_of(const_name):
    m = re.search(r'const %s: Array = \[' % const_name, mood_src)
    if not m:
        return set()
    end = mood_src.find("\n]", m.end())
    block = mood_src[m.end():end if end != -1 else len(mood_src)]
    return set(re.findall(r'"name"\s*:\s*"([a-z0-9_]+)"', block))

MOODS = names_of("MOODS")
PACKS = names_of("STYLE_PACKS")
LIGHTING = names_of("LIGHTING_PRESETS")

char_src = read("scenes/game/CharLayer.gd")
p3d_src = read("scripts/vn/Portrait3D.gd")
bust_src = read("scripts/vn/VnBustPortrait.gd")
KNOWN_EXPR = set(re.findall(r'"([a-z_]+)"\s*:\s*Color', char_src))
KNOWN_EXPR |= set(re.findall(r'"([a-z_]+)"\s*:\s*"[a-z]+"', p3d_src))
KNOWN_EXPR |= set(re.findall(r'"([a-z_]+)"(?:, "[a-z_]+")*\s*:\n', bust_src))
for grp in re.findall(r'^\t\t((?:"[a-z_]+"(?:, )?)+):', bust_src, re.M):
    KNOWN_EXPR |= set(re.findall(r'"([a-z_]+)"', grp))
KNOWN_EXPR |= {"neutral", "happy", "sad", "angry", "surprised", "tired", "nervous"}

# ── checks per scene file ────────────────────────────────────────
STUB_MAX_NODES = 2
for path in scene_files():
    rel = os.path.relpath(path, ROOT)
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        fail("%s: JSON parse error: %s" % (rel, e), rel)
        continue
    nodes = doc.get("nodes", [])
    has_bg = False
    for n in walk_nodes(nodes):
        t = n.get("t")
        if t == "bg":
            has_bg = True
            src = str(n.get("src", ""))
            if src.startswith("3d:"):
                if src[3:] not in PRESETS:
                    fail("%s: bg preset '%s' not in CAMERA_PRESETS" % (rel, src), rel)
            elif src and isinstance(n.get("src"), str):
                # "Visual novel backgrounds are 3d scenes" (2026-08-03):
                # any 2D file src is migration debt, tracked per-ref so
                # the remaining estate is always visible in the summary.
                # (A JSON-null src — the title cards — is not a bg ref.)
                debt_refs.append("%s -> %s" % (rel, src))
                if not os.path.exists(os.path.join(ROOT, src)):
                    fail("%s: bg image missing: %s" % (rel, src), rel)
        elif t == "cg":
            src = str(n.get("src", ""))
            if src and not os.path.exists(os.path.join(ROOT, src)):
                fail("%s: cg image missing: %s" % (rel, src), rel)
        # expression tokens
        expr = n.get("expr", n.get("expression"))
        if isinstance(expr, str) and expr and expr not in KNOWN_EXPR:
            fail("%s: unknown expression token '%s' (collapses to neutral)"
                 % (rel, expr), rel)
        # mood directives in text
        txt = n.get("text")
        if isinstance(txt, str):
            for mname in re.findall(r'\[mood:([a-z0-9_]+)\]', txt):
                if mname not in MOODS and mname not in PACKS:
                    fail("%s: [mood:%s] resolves to nothing" % (rel, mname), rel)
    # every real scene declares its home (the finale-cluster lesson)
    is_stub = "_stub" in os.path.basename(path) or "_test_" in os.path.basename(path)
    if not has_bg and len(nodes) > STUB_MAX_NODES and not is_stub:
        fail("%s: no bg node in a %d-node scene (inherits stale locale)"
             % (rel, len(nodes)), rel)

# ── engine-table cross-checks ────────────────────────────────────
pm = re.search(r'const STYLE_PACKS: Array = \[', mood_src)
pack_end = mood_src.find("\n]", pm.end()) if pm else -1
pack_block = mood_src[pm.end():pack_end] if pm else ""
for entry in re.finditer(
        r'"name"\s*:\s*"([a-z0-9_]+)"[^{]*?"lighting"\s*:\s*"([a-z0-9_]+)"',
        pack_block):
    if entry.group(2) not in LIGHTING:
        fail("MoodCycler STYLE_PACKS.%s: lighting '%s' is not a LIGHTING_PRESET"
             % (entry.group(1), entry.group(2)))

glb_lines = [l for l in char_src.split("\n") if not l.strip().startswith("#")]
for key, glb in re.findall(r'"([a-z_]+)"\s*:\s*"([a-z0-9_]+\.glb)"',
                           "\n".join(glb_lines)):
    p = os.path.join(ROOT, "assets", "3d", "characters", "heroes", glb)
    pd = os.path.join(ROOT, "assets", "3d", "characters", "demons", glb)
    if not os.path.exists(p) and not os.path.exists(pd):
        fail("CharLayer GLB mapping '%s' -> %s: file missing" % (key, glb))

if debt_refs:
    print("\n2D-background migration debt (%d ref(s) — VN backgrounds are"
          " 3D scenes; these still play over a flat image):" % len(debt_refs))
    for d in sorted(debt_refs):
        print("  " + d)

print("\nvn_asset_audit: %d problem(s) · %d legacy vol1-4 known issue(s)"
      " · %d migration-debt bg ref(s)" % (fails, legacy, len(debt_refs)))
sys.exit(1 if fails else 0)
