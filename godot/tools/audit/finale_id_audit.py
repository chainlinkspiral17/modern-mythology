#!/usr/bin/env python3
"""finale_id_audit.py — the ending ids the code matches on (2026-09-11).

`TarotGauntletGame.gd` branches on finale ids in three places: the
per-arcana milestone unlocks, the achievement triggers
(`loss_with_finale_id`), and now the ending stings. Every one of those
ids has to exist in `resources/games/<arcana>/finale.json`, and a
`match` arm that names an id nothing produces is silent dead code —
the branch simply never runs.

It had happened. The Priestess block matched six ids
(`the_reel_ran_out`, `the_listener_breaks`, `the_session_ends_empty`,
`they_walked_out_mid_sentence`, `the_cicadas_stopped`,
`session_over_unfinished`) that came from a staging where the board
was a recording booth. The board is Elicia's bungalow now and its four
finales have entirely different ids, so not one
`milestone:priestess_finale:*` could ever unlock. Rewritten by
TRIGGER, which is the part that survives a restaging.

    python3 godot/tools/audit/finale_id_audit.py
    python3 godot/tools/audit/finale_id_audit.py --all

A suite gate at zero.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GODOT = os.path.join(ROOT, "godot")
GAMES = os.path.join(GODOT, "resources", "games")
SCRIPTS = (os.path.join(GODOT, "scenes", "games", "TarotGauntletGame.gd"),)

MATCH_RX = re.compile(r'\n(\t+)match finale_id:\n(.*?)(?=\n\1[a-zA-Z_}]|\n\1\n|\Z)', re.S)
ARC_RX = re.compile(r'_arcana_id == "(\w+)"')
ARM_RX = re.compile(r'"([a-z0-9_]+)"\s*:')
# Ids named outside a `match finale_id:` block — the sting table, the
# achievement JSON — are checked against the union of all arcana.
TABLE_RX = re.compile(r'_FINALE_STING\s*:?=\s*\{(.*?)\n\}', re.S)


def finale_ids():
    """{arcana: {ids}} plus the union under the key ''."""
    out, allids = {}, set()
    for f in sorted(glob.glob(os.path.join(GAMES, "*", "finale.json"))):
        arc = os.path.basename(os.path.dirname(f))
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        ids = {str(x.get("id", "")) for x in j.get("finales", []) if x.get("id")}
        out[arc] = ids
        allids |= ids
    out[""] = allids
    return out


def main():
    show_all = "--all" in sys.argv
    ids = finale_ids()
    bad, checked = 0, 0
    for path in SCRIPTS:
        src = open(path, encoding="utf-8").read()
        rel = os.path.relpath(path, GODOT)
        for m in MATCH_RX.finditer(src):
            # Which arcana does this block belong to? The nearest
            # `_arcana_id == "x"` guard IN THE SAME FUNCTION — scoping
            # to the function matters, or an arcana-agnostic helper
            # like `_loss_cg_path` inherits the guard of whatever
            # function happened to precede it and every id it names
            # reads as dead.
            before = src[:m.start()]
            fn_start = before.rfind("\nfunc ")
            arcs = ARC_RX.findall(before[fn_start:] if fn_start >= 0 else before)
            arc = arcs[-1] if arcs else ""
            pool = ids.get(arc, ids[""])
            for arm in ARM_RX.findall(m.group(2)):
                checked += 1
                if arm in pool:
                    if show_all:
                        print("ok      %-36s %s" % (arm, arc or "(any)"))
                    continue
                bad += 1
                print("DEADARM %-36s %-12s no such finale id · %s"
                      % (arm, arc or "(any)", rel))
        tm = TABLE_RX.search(src)
        if tm:
            for key in re.findall(r'"([a-z0-9_]+)"\s*:', tm.group(1)):
                checked += 1
                if key in ids[""]:
                    continue
                bad += 1
                print("DEADKEY %-36s %-12s no arcana produces it · %s"
                      % (key, "", rel))

    # Achievement triggers name finale ids too.
    for f in sorted(glob.glob(os.path.join(GAMES, "*", "achievements.json"))):
        arc = os.path.basename(os.path.dirname(f))
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for fid in re.findall(r'"finale_id"\s*:\s*"([a-z0-9_]+)"',
                              json.dumps(j)):
            checked += 1
            if fid in ids.get(arc, ids[""]):
                continue
            bad += 1
            print("DEADACH %-36s %-12s no such finale id · %s"
                  % (fid, arc, os.path.relpath(f, GODOT)))

    print("\nfinale_id_audit · %d id reference(s) across %d arcana · "
          "%d dead" % (checked, len(ids) - 1, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
