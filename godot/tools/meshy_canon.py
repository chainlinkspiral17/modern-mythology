#!/usr/bin/env python3
"""Pull each roster entry's physical description out of the story text.

For every entry in tools/meshy_roster.json this scans the scene scripts
(resources/scenes/vol*/*.json narrate/say/think text), the gauntlet data
(resources/games/**/*.json) and the lore (lore/**/*.md) for sentences
that (a) mention the entry by name/key/alias and (b) carry appearance
vocabulary (hair, wears, jacket, brass, chipped …). The best hits are
printed as candidates, and with --write stored in the roster as
`canon: [{src, text}]` — the quotes the image prompt is built from.

It is a keyword heuristic, so it over-collects: read the candidates and
keep the ones that really describe the look (the roster's shipped
`canon` lists were curated by hand from this plus a read of the
scenes). Hand-curated quotes are never touched unless --overwrite.

Usage:
  python3 godot/tools/meshy_canon.py sam_miller scumm_machine   # preview candidates
  python3 godot/tools/meshy_canon.py --write                    # fill EMPTY canon lists
  python3 godot/tools/meshy_canon.py --write --overwrite finn   # rebuild one entry
  python3 godot/tools/meshy_canon.py --report                   # who still has nothing
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROSTER_PATH = REPO / "tools" / "meshy_roster.json"
LORE = REPO.parent / "lore"

APPEARANCE = re.compile(
    r"\b(hair|locs|dreadlocks|braid|ponytail|bald|beard|stubble|moustache|mustache|"
    r"eyes?|face|jaw|cheek|skin|freckl\w*|tattoo|scar|glasses|"
    r"tall|short|thin|lean|wiry|slight|heavy|broad|stocky|barrel|gaunt|"
    r"wears?|wearing|wore|dressed|jacket|coat|parka|bomber|hoodie|sweater|cardigan|"
    r"shirt|tee|t-shirt|polo|blouse|dress|skirt|jeans|denim|trousers|pants|shorts|"
    r"boots?|sneakers|shoes|clogs|sandals|heels|cap|hat|beanie|apron|vest|tie|"
    r"suit|uniform|scrubs|lanyard|badge|"
    r"brass|chrome|steel|iron|cedar|wood(en)?|leather|plastic|glass|paper|cardboard|"
    r"canvas|wool|cotton|enamel|ceramic|rust\w*|chipped|cracked|faded|worn|"
    r"painted|paint|label|handle|lid|carved|stain\w*|inch|foot|feet|cm|metre|meter)\b",
    re.I,
)
STOP_ALIASES = {"man", "woman", "boy", "kid", "old", "the", "a"}
# build docs / plans / manifests describe scenes and tooling, not people
SKIP_LORE = re.compile(r"PLAYBOOK|_PLAN|_SPEC|MANIFEST|LOCALES|SCOPE|INVENTORY|PERFORMANCE|TOPOGRAPHY|OUTLINE|PITCHES|README|COMPASS|UNLOCK", re.I)


def sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?…])\s+(?=[A-Z\"“'(])", text)
    return [p.strip() for p in parts if len(p.strip()) > 20]


def gather_sources():
    """Yield (short_src, text) blocks."""
    for f in sorted(glob.glob(str(REPO / "resources" / "scenes" / "vol*" / "*.json"))):
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        short = "/".join(Path(f).parts[-2:])
        for n in d.get("nodes", []):
            if isinstance(n, dict) and n.get("t") in ("narrate", "say", "think") and n.get("text"):
                yield short, n["text"], n.get("char", "")
    for f in sorted(glob.glob(str(REPO / "resources" / "games" / "**" / "*.json"), recursive=True)):
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        short = "games/" + "/".join(Path(f).parts[-2:])
        stack = [d]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
            elif isinstance(x, str) and len(x) > 40:
                yield short, x, ""
    for f in sorted(glob.glob(str(LORE / "**" / "*.md"), recursive=True)):
        short = "lore/" + str(Path(f).relative_to(LORE))
        if SKIP_LORE.search(Path(f).name):
            continue
        try:
            txt = Path(f).read_text(errors="replace")
        except OSError:
            continue
        for para in re.split(r"\n\s*\n", txt):
            if para.count("|") >= 4:          # markdown tables: never prose
                continue
            para = re.sub(r"^[#>\-*\s]+", "", para, flags=re.M)
            if len(para) > 40:
                yield short, para, ""


def aliases_for(entry):
    names = set()
    full = entry["name"]
    names.add(full)
    # "Sam Miller" → "Sam Miller", "Sam"; "Mr. Dickens Dean" → "Dickens Dean", "Dean"
    words = [w for w in re.findall(r"[A-Z][\w'’]+", full) if w.lower() not in ("mr", "mrs", "ms", "the", "a")]
    if words:
        names.add(words[0])
        if len(words) > 1:
            names.add(" ".join(words))
            names.add(words[-1])
    for k in entry.get("keys", []):
        k2 = k.replace("_", " ").strip()
        if len(k2) > 2 and k2 not in STOP_ALIASES:
            names.add(k2)
    for a in entry.get("aliases", []):
        names.add(a)
    if entry["kind"] == "prop":
        # "Sam's License Plate Notebook" → "License Plate Notebook" (never the
        # bare last word: "notebook"/"machine" match everything)
        names = set()
        base = re.sub(r"^(the|a|an)\s+", "", full, flags=re.I)
        names.add(base)
        names.add(re.sub(r"^[\w'’.]+s\s+", "", base))   # drop leading possessive
        names.update(entry.get("aliases", []))
    # too-generic single words hurt more than they help
    return {n for n in names if len(n) > 2 and n.lower() not in ("man", "woman", "stranger", "figure", "car", "van", "pen", "glass")}


def score(sentence, alias_re):
    hits = len(APPEARANCE.findall(sentence))
    if not hits:
        return 0
    s = hits * 2 + (3 if alias_re.search(sentence) else 0)
    if len(sentence) > 400:
        s -= 2
    return s


def extract(entry, blocks, max_quotes=8):
    aliases = aliases_for(entry)
    alias_re = re.compile(r"\b(" + "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True)) + r")\b(?![’']s\b)", re.I)
    found = {}
    for src, text, speaker in blocks:
        sents = sentences(text)
        for i, sent in enumerate(sents):
            # the sentence must name the subject (characters: or follow one
            # that does — "Sam came in. She wore…")
            window = sent if entry["kind"] == "prop" else " ".join(sents[max(0, i - 1):i + 1])
            if not alias_re.search(window):
                continue
            sc = score(sent, alias_re)
            if sc < 3:
                continue
            key = re.sub(r"\W+", "", sent.lower())[:120]
            if key in found and found[key][0] >= sc:
                continue
            found[key] = (sc, src, sent)
    ranked = sorted(found.values(), key=lambda t: -t[0])[:max_quotes]
    return [{"src": src, "text": sent} for _, src, sent in ranked]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="limit to these slugs (default: all)")
    ap.add_argument("--write", action="store_true", help="store candidates in the roster (default: preview only)")
    ap.add_argument("--overwrite", action="store_true", help="with --write: replace existing canon lists too")
    ap.add_argument("--report", action="store_true", help="list entries with no canon quotes")
    ap.add_argument("--max", type=int, default=8)
    args = ap.parse_args()

    roster = json.loads(ROSTER_PATH.read_text())
    entries = roster["entries"]
    if args.report:
        empty = [e["slug"] for e in entries if not e.get("canon")]
        print(f"{len(entries) - len(empty)} entries have canon quotes; {len(empty)} have none:")
        for s in empty:
            print("  ", s)
        return
    blocks = list(gather_sources())
    print(f"scanning {len(blocks)} text blocks", file=sys.stderr)
    changed = 0
    for e in entries:
        if args.slugs and e["slug"] not in args.slugs:
            continue
        if e.get("canon") and not args.overwrite:
            continue
        quotes = extract(e, blocks, args.max)
        if not args.write:
            print(f"\n== {e['slug']} ({len(quotes)})")
            for q in quotes:
                print(f"  [{q['src']}] {q['text'][:200]}")
            continue
        e["canon"] = quotes
        changed += 1
    if args.write:
        ROSTER_PATH.write_text(json.dumps(roster, indent=2, ensure_ascii=False) + "\n")
        print(f"updated canon for {changed} entries → {ROSTER_PATH.name}", file=sys.stderr)


if __name__ == "__main__":
    main()
