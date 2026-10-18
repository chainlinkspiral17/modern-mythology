#!/usr/bin/env python3
"""voice_recover — rebuild the cast's voice IDs from ElevenLabs' own history
(2026-10-18).

Every line the voice studio or elevenlabs_render.py ever generated is in the
ElevenLabs account's history, with the voice it used and the words it spoke.
This reads that history, matches each item's text to the scene line it came
from, resolves the line's speaker exactly as the renderer does
(voice_common.resolve_char), and so learns which voice each character used.

    python3 godot/tools/voice_recover.py            # report only
    python3 godot/tools/voice_recover.py --apply    # also write the IDs

The report is godot/tools/voice_recovery_report.md: per character the
voice used most (with how often, and any other voices it used), and the
voices in the history that matched no line. --apply writes the winners into
godot/tools/voice_map.json and voice_ids_backup.json (gaps only: an ID
already saved is kept).

The API key: ELEVENLABS_API_KEY, else godot/tools/.elevenlabs_key (git
ignores it), else it asks. Stdlib only.
"""
import argparse
import collections
import getpass
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import voice_common as vc  # noqa: E402
import voice_ids  # noqa: E402

HISTORY = "https://api.elevenlabs.io/v1/history"
KEY_FILE = TOOLS / ".elevenlabs_key"
REPORT = TOOLS / "voice_recovery_report.md"


def api_key():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not k and KEY_FILE.exists():
        k = KEY_FILE.read_text(encoding="utf-8").strip()
    if not k:
        k = getpass.getpass("ElevenLabs API key (sk_…, not shown): ").strip()
    if not k:
        sys.exit("No API key.")
    if not k.startswith("sk_"):
        sys.exit("That is not an API key: ElevenLabs' keys start with sk_. The settings page lists key IDs\n"
                 "(labels), not keys; the sk_ value is shown once, when a key is created or rotated.\n"
                 "  ElevenLabs → Developers → API keys → create (or rotate) a key → copy the sk_… value.")
    if not KEY_FILE.exists():
        # keep it for next time (git ignores godot/tools/.*_key)
        KEY_FILE.write_text(k + "\n", encoding="utf-8")
        try:
            KEY_FILE.chmod(0o600)
        except OSError:
            pass
        print(f"(key kept in {KEY_FILE.relative_to(TOOLS.parent.parent)}, which git ignores)")
    return k


def norm(t):
    t = re.sub(r"\[[^\]]*\]", " ", t or "")
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def _get(url, key):
    """GET a JSON page; on an HTTP error, say what ElevenLabs said."""
    req = urllib.request.Request(url, headers={"xi-api-key": key, "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as ex:
        body = ex.read().decode("utf-8", "replace")[:600]
        raise RuntimeError(f"ElevenLabs answered HTTP {ex.code}: {body}") from None


def history(key):
    """Every history item, oldest pages last. (2026-10-18, the Deck: a
    page_size of 1000 came back HTTP 400; pages of 100 are the API's own
    default.)"""
    after = None
    while True:
        q = {"page_size": 100}
        if after:
            q["start_after_history_item_id"] = after
        page = _get(HISTORY + "?" + urllib.parse.urlencode(q), key)
        items = page.get("history") or []
        for it in items:
            yield it
        if not page.get("has_more") or not items:
            return
        after = page.get("last_history_item_id") or items[-1].get("history_item_id")


def line_index():
    """normalised text -> set of voice keys that speak it."""
    vmap = vc.load_voice_map()
    aliases = vc.alias_table(vmap)
    idx = collections.defaultdict(set)
    for path in vc.find_scenes():
        data = vc.load_scene(path) or {}
        sid = data.get("id", path.stem)
        vol = vc.scene_vol_number(data, path)
        for node in data.get("nodes", []):
            kind = node.get("t", "")
            if kind not in vc.VOICE_KINDS:
                continue
            text = (node.get("text") or "").strip()
            if not text:
                continue
            char = "" if kind == "narrate" else (node.get("char") or "").strip()
            key, _ = vc.resolve_char(vmap, char, kind, sid, aliases, vol)
            n = norm(text)
            if len(n) >= 6:
                idx[n].add(key)
    return idx


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the recovered IDs (gaps only)")
    args = ap.parse_args()
    key = api_key()
    try:
        _get(HISTORY + "?page_size=1", key)
    except RuntimeError as ex:
        if KEY_FILE.exists():
            KEY_FILE.unlink()                    # a key that failed is not kept
        sys.exit(f"{ex}\n  If the key is right but history is refused, check that the key's permissions "
                 f"allow reading speech history.")
    idx = line_index()
    per_key = collections.defaultdict(collections.Counter)
    names = {}
    unmatched = collections.Counter()
    n_items = 0
    for it in history(key):
        n_items += 1
        vid = it.get("voice_id")
        if not vid:
            continue
        names[vid] = it.get("voice_name") or names.get(vid, "")
        keys = idx.get(norm(it.get("text", "")))
        if not keys:
            unmatched[vid] += 1
            continue
        for k in keys:
            per_key[k][vid] += 1
    winners = {}
    out = ["# Voice IDs recovered from the ElevenLabs history", "",
           f"{n_items} history items read; {sum(sum(c.values()) for c in per_key.values())} matched a scene line.", "",
           "| character key | voice | uses | other voices it used |", "|---|---|---|---|"]
    for k in sorted(per_key):
        c = per_key[k]
        (vid, uses), *rest = c.most_common()
        winners[k] = vid
        other = ", ".join(f"{names.get(v, '?')} `{v}` ×{u}" for v, u in rest) or ""
        out.append(f"| `{k}` | {names.get(vid, '?')} `{vid}` | {uses} | {other} |")
    if unmatched:
        out += ["", "## Voices in the history that matched no current line", "",
                "(a line since rewritten, a test, or a voice tried and dropped)", ""]
        for vid, u in unmatched.most_common():
            out.append(f"- {names.get(vid, '?')} `{vid}` ×{u}")
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(winners)} characters recovered · report → {REPORT.relative_to(TOOLS.parent.parent)}")
    if args.apply and winners:
        res = voice_ids.save_ids(winners, "voice_recover (ElevenLabs history)", overwrite=False)
        print(f"written {res['set'] + res['added']} · kept {res['kept']} (already saved)")


if __name__ == "__main__":
    main()
