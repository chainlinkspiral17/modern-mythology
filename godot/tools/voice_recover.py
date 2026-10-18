#!/usr/bin/env python3
"""voice_recover — rebuild the cast's voice IDs from ElevenLabs' own history
(2026-10-18).

Every line the voice studio or elevenlabs_render.py ever generated is in the
ElevenLabs account's history, with the voice it used and the words it spoke.
This reads that history, matches each item's text to the scene line it came
from, resolves the line's speaker exactly as the renderer does
(voice_common.resolve_char), and so learns which voice each character used.

It also reads the workspace's OWN voices (the ones designed, cloned or added
for the cast; 2026-10-18 the Deck: the history matched nothing, but the
workspace holds voices named for the characters, e.g. "Alberto"), and matches
each voice's name to a character key the way the renderer matches a speaker
name (aliases included).

    python3 godot/tools/voice_recover.py            # report only
    python3 godot/tools/voice_recover.py --apply    # also write the IDs
    python3 godot/tools/voice_recover.py --pack     # the RECORDINGS route

--pack (2026-10-18: the history matched nothing, and most of the cast used
library voices, whose names name no one) gathers what a voice match needs
into godot/tools/voice_recovery/: three recorded lines per character from
this machine's game audio (vol 6 first), the workspace's voices with their
preview clips' addresses, and the history's voice ids and texts (never the
key). Pushed, a speaker-embedding match pairs each character's recordings
with the voice that made them.

The report is godot/tools/voice_recovery_report.md: per character the
voice the history used most (with how often, and any other voices it used),
the workspace voices whose name names a character, and every other own
voice with its description, so the rest can be cast by hand in the studio.
--apply writes the history winners and the name matches into
godot/tools/voice_map.json and voice_ids_backup.json (gaps only: an ID
already saved is kept; a history match beats a name match).

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
VOICES = "https://api.elevenlabs.io/v2/voices"
# the categories a workspace makes or adds itself; "premade" voices are
# ElevenLabs' own defaults, named for no one in the cast
OWN = {"generated", "cloned", "professional", "famous", "high_quality"}
KEY_FILE = TOOLS / ".elevenlabs_key"
REPORT = TOOLS / "voice_recovery_report.md"
PACK = TOOLS / "voice_recovery"
GAME = TOOLS.parent


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


def own_voices(key):
    """Every voice in the workspace (v2 pages of 100)."""
    token = None
    while True:
        q = {"page_size": 100, "include_total_count": "false"}
        if token:
            q["next_page_token"] = token
        page = _get(VOICES + "?" + urllib.parse.urlencode(q), key)
        for v in page.get("voices") or []:
            yield v
        token = page.get("next_page_token")
        if not page.get("has_more") or not token:
            return


def name_matches(vmap, name):
    """The character keys a voice's NAME names: the whole name, then the name
    without a trailing take/version word ("Alberto v2", "Faust - take 3"),
    then its first word, each through the same aliases the renderer uses.
    Returns (keys, how)."""
    chars = vmap.get("characters") or {}
    aliases = vc.alias_table(vmap)
    base = re.split(r"\s+[-–—:(]\s*|\s+(?:v|take|draft|alt|test)\s*\d*\b", name or "", 1, flags=re.I)[0]
    for how, cand in (("name", name or ""), ("name", base), ("first word", (base.split() or [""])[0])):
        k = vc.char_key(cand)
        k = aliases.get(k, k)
        if k in chars and not k.startswith("_narrator"):
            return [k], how
    return [], ""


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


def loose(idx, t):
    """A line edited since it was voiced, or voiced in part: the history text
    inside a line, or a line inside it (24+ characters, one speaker only)."""
    if len(t) < 24:
        return None
    hits = set()
    for n, keys in idx.items():
        if len(n) >= 24 and (t in n or n in t):
            hits |= keys
    return hits if len(hits) == 1 else None


def pack(key):
    """Write godot/tools/voice_recovery/ (see --pack in the docstring)."""
    import shutil
    PACK.mkdir(exist_ok=True)
    vmap = vc.load_voice_map()
    aliases = vc.alias_table(vmap)
    cands = collections.defaultdict(list)            # key -> [(prefer, len, path, sid, i)]
    for path in vc.find_scenes():
        data = vc.load_scene(path) or {}
        sid = data.get("id", path.stem)
        vol = vc.scene_vol_number(data, path)
        for i, node in enumerate(data.get("nodes", [])):
            kind, v = node.get("t", ""), node.get("voice") or ""
            if kind not in vc.VOICE_KINDS or not v:
                continue
            f = GAME / v
            if not f.is_file() or f.stat().st_size < 12000:
                continue
            char = "" if kind == "narrate" else (node.get("char") or "").strip()
            k, _ = vc.resolve_char(vmap, char, kind, sid, aliases, vol)
            try:
                prefer = {6: 0, 7: 1, 5: 2}.get(int(vol), 3)
            except (TypeError, ValueError):
                prefer = 3
            cands[k].append((prefer, -len(node.get("text") or ""), f, sid, i))
    samples = PACK / "samples"
    if samples.exists():
        shutil.rmtree(samples)
    n = 0
    index = []
    for k, rows in sorted(cands.items()):
        rows.sort(key=lambda r: (r[0], r[1]))
        seen = set()
        for prefer, _, f, sid, i in rows:
            if sid in seen and len(rows) > 3:
                continue                                  # spread across scenes
            seen.add(sid)
            dst = samples / k / f"{sid}_{i:03d}{f.suffix}"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dst)
            index.append({"key": k, "scene": sid, "node": i, "file": str(dst.relative_to(PACK))})
            n += 1
            if len([x for x in index if x["key"] == k]) >= 3:
                break
    (PACK / "samples.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    print(f"recordings: {n} lines for {len(cands)} characters (of the voiced lines on this machine)")
    hist = []
    try:
        for it in history(key):
            # (2026-10-18) the whole item: most v3 items carry no top-level
            # voice_id or text, so the voice must sit in another field
            hist.append({k: v for k, v in it.items() if k not in ("feedback",)})
    except Exception as ex:  # noqa: BLE001 — the recordings still count
        print(f"history: not read ({ex})")
    (PACK / "history.json").write_text(json.dumps(hist, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"history: {len(hist)} items, {len({h['voice_id'] for h in hist})} voices")
    vs = []
    try:
        for v in own_voices(key):
            vs.append({k: v.get(k) for k in ("voice_id", "name", "category", "description", "labels",
                                              "preview_url")})
    except Exception as ex:  # noqa: BLE001
        print(f"workspace voices: not read ({ex})")
    # every voice's preview clip (some live on a host the cloud cannot reach)
    prev = PACK / "previews"
    prev.mkdir(exist_ok=True)
    got = 0
    for v in vs:
        url, dst = v.get("preview_url") or "", prev / f"{v.get('voice_id')}.mp3"
        if not url or (dst.exists() and dst.stat().st_size > 5000):
            got += dst.exists()
            continue
        try:
            host = urllib.parse.urlparse(url).hostname or ""
            hdr = {"xi-api-key": key} if host.endswith(".elevenlabs.io") else {}    # the key goes to ElevenLabs only
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60) as r:
                dst.write_bytes(r.read())
            got += 1
        except Exception as ex:  # noqa: BLE001
            print(f"  preview not fetched: {v.get('name')} ({ex})")
    print(f"previews: {got} of {len(vs)}")
    (PACK / "workspace_voices.json").write_text(json.dumps(vs, indent=1, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    print(f"workspace voices: {len(vs)}")
    print("Now push it (the command Claude gave you), and Claude matches the voices.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the recovered IDs (gaps only)")
    ap.add_argument("--pack", action="store_true", help="gather recordings + voice lists for a voice match")
    args = ap.parse_args()
    key = api_key()
    try:
        _get(HISTORY + "?page_size=1", key)
    except RuntimeError as ex:
        if KEY_FILE.exists():
            KEY_FILE.unlink()                    # a key that failed is not kept
        if not args.pack:
            sys.exit(f"{ex}\n  If the key is right but history is refused, check that the key's permissions "
                     f"allow reading speech history.")
        print(f"(ElevenLabs refused the key: {ex} — packing the recordings anyway)")
    if args.pack:
        return pack(key)
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
        t = norm(it.get("text", ""))
        keys = idx.get(t) or loose(idx, t)
        if not keys:
            unmatched[vid] += 1
            continue
        for k in keys:
            per_key[k][vid] += 1
    winners = {}
    n_matched = sum(sum(c.values()) for c in per_key.values())
    print(f"history: {n_items} items read, {n_matched} matched a scene line")
    out = ["# Voice IDs recovered from ElevenLabs", "",
           "## From the speech history", "",
           f"{n_items} history items read; {n_matched} matched a scene line.", ""]
    if not n_items:
        out += ["The history is empty for this key's workspace: the lines were never generated here, the "
                "history was cleared, or they were generated with another account.", ""]
    out += ["| character key | voice | uses | other voices it used |", "|---|---|---|---|"]
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
    # the workspace's own voices, matched by name
    vmap = vc.load_voice_map()
    by_name = {}
    rest = []
    try:
        voices = [v for v in own_voices(key) if (v.get("category") or "") in OWN or names.get(v.get("voice_id"))]
    except RuntimeError as ex:
        voices = []
        out += ["", f"(the workspace's voices could not be read: {ex})"]
    for v in sorted(voices, key=lambda v: (v.get("name") or "").lower()):
        vid, nm = v.get("voice_id") or "", (v.get("name") or "").strip()
        keys, how = name_matches(vmap, nm)
        if keys:
            by_name.setdefault(keys[0], []).append((nm, vid, how))
        else:
            rest.append(v)
    print(f"workspace: {len(voices)} own voices, {len(by_name)} named for a character")
    out += ["", "## Workspace voices named for a character", "",
            f"{len(voices)} own voices in the workspace (designed, cloned or added); "
            f"{len(by_name)} characters have one named for them.", "",
            "| character key | voice | matched by |", "|---|---|---|"]
    for k in sorted(by_name):
        for nm, vid, how in by_name[k]:
            out.append(f"| `{k}` | {nm} `{vid}` | {how} |")
        if k not in winners:
            winners[k] = by_name[k][0][1]          # the history wins when both speak
    if rest:
        out += ["", "## Other own voices (cast these by hand in the voice studio)", ""]
        for v in rest:
            desc = re.sub(r"\s+", " ", v.get("description") or "").strip()[:160]
            out.append(f"- **{v.get('name')}** `{v.get('voice_id')}` ({v.get('category')})" + (f": {desc}" if desc else ""))
    REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(winners)} characters recovered · report → {REPORT.relative_to(TOOLS.parent.parent)}")
    if args.apply and winners:
        res = voice_ids.save_ids(winners, "voice_recover (ElevenLabs history)", overwrite=False)
        print(f"written {res['set'] + res['added']} · kept {res['kept']} (already saved)")


if __name__ == "__main__":
    main()
