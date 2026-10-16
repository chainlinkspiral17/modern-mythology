#!/usr/bin/env python3
"""ages_audit.py — the age ledger and the roster agree (2026-10-16).

The user: "characters need new looks and voices as they age." The ledger
(godot/tools/ages.json) gives each recurring character's eras; the roster
(meshy_roster.json) carries the look for each. This fails when:
  · an era's look slug is not in the roster;
  · a look entry is not attached to the ledger's character (its `base`), or
    does not cover the era's volumes (look.vols) — CharLayer would show the
    wrong age;
  · a voice key is not `<base>__<era id>`, or two eras share one;
  · two eras of one character claim the same volume with no scenes to tell
    them apart.

    python3 godot/tools/audit/ages_audit.py
Run by run_changed_audits.sh when ages.json or the roster changes.
"""
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
AGES = TOOLS / "ages.json"
ROSTER = TOOLS / "meshy_roster.json"


def main():
    if not AGES.exists():
        print("ages_audit · no ages.json")
        return 0
    ages = json.loads(AGES.read_text())
    ro = json.loads(ROSTER.read_text())
    by_slug = {e["slug"]: e for e in ro["entries"]}
    bad = []
    keys_seen = {}
    n_eras = 0
    for base, c in (ages.get("characters") or {}).items():
        if base not in by_slug:
            bad.append(f"{base}: not a roster slug")
            continue
        claimed = {}
        for e in c.get("eras") or []:
            n_eras += 1
            eid = e.get("id", "?")
            look = e.get("look")
            if isinstance(look, list):          # several models on stage at once (the author's four facets)
                for s in look:
                    if s not in by_slug:
                        bad.append(f"{base}/{eid}: look {s} is not in the roster")
                look = None
            if look:
                le = by_slug.get(look)
                if le is None:
                    bad.append(f"{base}/{eid}: look {look} is not in the roster")
                elif look != base:
                    if le.get("base") != base:
                        bad.append(f"{base}/{eid}: look {look} has base {le.get('base')!r}, not {base}")
                    lv = set(int(v) for v in ((le.get("look") or {}).get("vols") or []))
                    missing = [v for v in (e.get("vols") or []) if int(v) not in lv]
                    if missing:
                        bad.append(f"{base}/{eid}: look {look} does not cover vol(s) {missing}")
            key = ((e.get("voice") or {}).get("key")) or ""
            if key:
                # voices are named after the voice map's character id (john,
                # elicia), which may differ from the roster slug: any of the
                # character's keys, or the base, may lead the era key
                heads = [base] + [str(k).lower() for k in (c.get("keys") or [])]
                if not any(key.startswith(h + "__") for h in heads):
                    bad.append(f"{base}/{eid}: voice key {key} does not start with one of {heads}")
                # two eras of ONE person may share a voice on purpose; two people may not
                owner = keys_seen.get(key)
                if owner and owner.split("/")[0] != base:
                    bad.append(f"{base}/{eid}: voice key {key} also used by {owner}")
                keys_seen.setdefault(key, f"{base}/{eid}")
            if not e.get("scenes"):
                for v in e.get("vols") or []:
                    if v in claimed:
                        bad.append(f"{base}: vol {v} claimed by eras {claimed[v]} and {eid} with no scenes to tell them apart")
                    claimed[v] = eid
    for b in bad:
        print("   AGE  " + b)
    print(f"ages_audit · {len(ages.get('characters') or {})} character(s) · {n_eras} era(s) · {len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
