#!/usr/bin/env python3
"""audio_reference_audit.py — audio paths named by code and data
(2026-09-11).

`music_coverage_audit.py` checks the CATALOG. This checks everything
else: every `assets/audio/...` string literal in a .gd, .json, .tscn or
.tres, and every SFXBank preset a script asks for by name. Both fail
the same way — a load that returns null, a fallback that advances, and
a game that just sounds slightly emptier than it should.

What the first run found (15 paths, none of them ever on disk):

  · TWELVE `gauntlet_*.ogg` fallbacks in TarotGauntletGame's `_SFX`.
    Harmless in the end — every key had been rerouted to an SFXBank
    preset in an earlier pass — but the table stayed behind pointing
    at twelve files nobody made, which is indistinguishable from a
    live bug until you read the routing. Deleted.
  · The Fool's diner has two jukebox 45s as USABLE ITEMS
    (`play_jukebox_track` in resources/games/fool/items.json). Both
    played nothing: NOON ROOM ROOM and WHERE THE BAR USED TO BE were
    a flavor paragraph and a filename. Authored.
  · The Music Player's TAPE REEL skin unlocks on having HEARD
    `vol5_elicia_theme_solo` — a file that had never existed, so the
    skin was unreachable by construction. Authored.

Gate at zero. A path may be excused only by adding it to ALLOW below
with the reason it is deliberately absent.

    python3 godot/tools/audit/audio_reference_audit.py
    python3 godot/tools/audit/audio_reference_audit.py --all
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")

ROOTS = ("scripts", "scenes", "autoload", "resources", "tools")
EXTS = (".gd", ".json", ".tscn", ".tres")
PATH_RX = re.compile(
    r'(?:res://)?(assets/audio/[A-Za-z0-9_./-]+\.(?:wav|ogg|mp3))')

# The catalog is allowed to register a track ahead of its audio: those
# entries are what music_coverage_audit measures, and AudioMgr's
# rotation already skips file-less srcs. Everything else must resolve.
SKIP_FILES = ("music_catalog.json",)

ALLOW = {
    # path: why it is deliberately absent
}


def files():
    for r in ROOTS:
        for f in glob.glob(os.path.join(GODOT, r, "**", "*"), recursive=True):
            if f.endswith(EXTS) and os.path.basename(f) not in SKIP_FILES:
                yield f


def sfx_presets():
    """Preset names SFXBank actually defines."""
    cand = glob.glob(os.path.join(GODOT, "**", "SFXBank.gd"), recursive=True)
    if not cand:
        return None
    src = open(cand[0], encoding="utf-8").read()
    return set(re.findall(r'"([a-z0-9_]+)"\s*:', src))


SCEN_RX = re.compile(r'_BGM_BY_SCENARIO\s*:?=\s*\{(.*?)\n\}', re.S)
GAUNTLET = os.path.join(GODOT, "scenes", "games", "TarotGauntletGame.gd")
GAMES = os.path.join(GODOT, "resources", "games")


def scenario_bed_keys():
    """The "<arcana>:<difficulty>" keys _BGM_BY_SCENARIO routes."""
    src = open(GAUNTLET, encoding="utf-8").read()
    m = SCEN_RX.search(src)
    return set(re.findall(r'"([a-z_]+:[a-z]+)"\s*:', m.group(1))) if m else set()


def scenario_combos():
    """The "<arcana>:<difficulty>" pairs setup_*.json actually defines."""
    import json
    out = set()
    for f in glob.glob(os.path.join(GAMES, "*", "setup_*.json")):
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        arc = os.path.basename(os.path.dirname(f))
        d = str(j.get("difficulty", ""))
        if d:
            out.add(arc + ":" + d)
    return out


BANK_RX = re.compile(r'_SFX_BANK_KEYS\s*:?=\s*\{(.*?)\n\}', re.S)


def bank_key_tables():
    """{file: [preset names a *_BANK_KEYS table routes to]}."""
    out = {}
    for f in files():
        if not f.endswith(".gd"):
            continue
        src = open(f, encoding="utf-8", errors="ignore").read()
        m = BANK_RX.search(src)
        if m:
            out[f] = re.findall(r':\s*"([a-z0-9_]+)"', m.group(1))
    return out


def main():
    show_all = "--all" in sys.argv
    seen, bad = 0, 0
    for f in files():
        try:
            src = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in PATH_RX.finditer(src):
            p = m.group(1)
            seen += 1
            if os.path.exists(os.path.join(GODOT, p)):
                continue
            if p in ALLOW:
                if show_all:
                    print("ok(allow) %-52s %s" % (p, ALLOW[p]))
                continue
            bad += 1
            print("NOFILE  %-54s %s"
                  % (p, os.path.relpath(f, GODOT)))

    presets = sfx_presets()
    routed = 0
    if presets is not None:
        for f, keys in sorted(bank_key_tables().items()):
            for k in keys:
                routed += 1
                if k in presets:
                    continue
                bad += 1
                print("NOPRESET %-53s %s"
                      % (k, os.path.relpath(f, GODOT)))

    # A scenario bed keyed to an arcana×difficulty no scenario defines
    # plays for nobody. (The reverse — a combo with no bed — is the
    # normal state: seventeen arcana still share the location drones.)
    combos = scenario_combos()
    keys = scenario_bed_keys()
    for k in sorted(keys - combos):
        bad += 1
        print("NOSCENARIO %-51s no setup_*.json has that "
              "arcana × difficulty" % k)
    if show_all:
        for k in sorted(combos - keys):
            print("info    %-54s no scenario bed (uses the location drone)"
                  % k)

    print("\naudio_reference_audit · %d path(s) · %d bank route(s) · "
          "%d scenario bed(s) · %d problem(s)"
          % (seen, routed, len(keys), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
