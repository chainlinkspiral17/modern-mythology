#!/usr/bin/env python3
"""page_split.py — one page of text at a time (2026-09-12).

Deck read: "some sections have too much text on screen at once and it
gets too small and cramped." The dialogue box keeps its full 34 px
body up to 260 visible characters and then auto-fits, stepping the
font down toward HALF SIZE so the whole passage fits (DialogueBox.
_fit_body_size / _fit_size_by_count). 2,219 narrate / say / think
nodes were over that line; the longest is 1,566 characters — a 17 px
wall of type over the picture.

This splits a long node into PAGES at sentence boundaries: greedy
packing of sentences up to TARGET, never past HARD when a sentence can
be broken at an em dash, semicolon or comma near the middle.

  · The leading directives ([mood:] [shot:] [trip:] …) stay on the
    FIRST page — a cut fires once.
  · `voice` stays on the first page (the recording is the passage).
  · `char`, `expr`, `when_flag` / `when_not_flag` and every other field
    are copied to every page, so a gated or spoken node stays gated
    and spoken.
  · Inline [fade …]…[/fade] markup is never split across (2 nodes).
  · Index references — choice `goto`, choice `check.pass` / `.fail`,
    jump `goto` — are re-pointed to the first page of the node they
    named. A save file's node index will land a few lines off inside
    a split chapter, once; that is the whole cost.

RAW-TEXT SPLICE. Scene JSON is never re-serialised (211 of 313 files
do not round-trip byte-for-byte). Each node's exact span is found with
json.JSONDecoder.raw_decode, and only those spans are replaced — with
pages dumped in the node's own key order and the file's own indent.
The result is parsed before it is written.

    python3 godot/tools/audit/page_split.py --dry [scene.json …]
    python3 godot/tools/audit/page_split.py [scene.json …]
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCENES = os.path.join(ROOT, "godot", "resources", "scenes")

TEXT_TYPES = ("narrate", "say", "think")
LIMIT = 260          # DialogueBox keeps the full font up to here
TARGET = 230         # what a page packs to (room for wide glyphs)
HARD = 300           # a single sentence past this is broken inside
DIRECT = re.compile(r"^(\[[a-z]+:[^\]]*\]\s*)+")
# a sentence ends at . ! ? … (optionally followed by a closing quote or
# bracket) before whitespace and an opener
SENT = re.compile(r'(?<=[.!?…])["”’)\]]?\s+(?=[A-Z"“‘(\[0-9])')
BREAK = re.compile(r"\s+—\s+|;\s+|,\s+")
# a sentence with no dash, semicolon or comma near its middle breaks at
# a conjunction ("the cabin and the bakery and the wall and …"), and a
# sentence with none of those at any space — a page turn mid-list
# reads; a 17 px wall of type does not
BREAK2 = re.compile(r"\s+(?:and|but|or|so|then|because|while|which|that)\s+")
BREAK3 = re.compile(r"\s+")


def sentences(body):
    parts = []
    last = 0
    for m in SENT.finditer(body):
        parts.append(body[last:m.end()].rstrip())
        last = m.end()
    tail = body[last:].strip()
    if tail:
        parts.append(tail)
    return [p for p in parts if p]


def break_long(s):
    """A sentence past HARD: break at the em dash / semicolon / comma
    nearest the middle, if both halves are worth a page."""
    if len(s) <= HARD:
        return [s]
    best = None
    for rx in (BREAK, BREAK2, BREAK3):
        for m in rx.finditer(s):
            cut = m.end() if rx is BREAK else m.start()
            if 60 <= cut <= len(s) - 60:
                if best is None or abs(cut - len(s) / 2) < abs(best - len(s) / 2):
                    best = cut
        if best is not None:
            break
    if best is None:
        return [s]
    return break_long(s[:best].rstrip()) + break_long(s[best:].lstrip())


def pages_for(text):
    """None if the node must not be split; else a list of page texts
    (the first carries the directives)."""
    m = DIRECT.match(text)
    pre = m.group(0) if m else ""
    body = text[len(pre):]
    if len(body) <= LIMIT or "[fade" in body:
        return None
    units = []
    for s in sentences(body):
        units.extend(break_long(s))
    pages, cur = [], ""
    for u in units:
        if cur and len(cur) + 1 + len(u) > TARGET:
            pages.append(cur)
            cur = u
        else:
            cur = (cur + " " + u) if cur else u
    if cur:
        pages.append(cur)
    if len(pages) < 2:
        return None
    pages[0] = pre + pages[0]
    return pages


def node_spans(raw):
    """[(start, end)] of every object in the top-level "nodes" array."""
    i = raw.index('"nodes"')
    i = raw.index("[", i) + 1
    dec = json.JSONDecoder()
    spans = []
    while True:
        while i < len(raw) and raw[i] in " \t\r\n,":
            i += 1
        if i >= len(raw) or raw[i] == "]":
            break
        obj, end = dec.raw_decode(raw, i)
        spans.append((i, end))
        i = end
    return spans


def dump_like(node, raw, span):
    """Dump `node` in the style of the original span: same base indent,
    same inner indent, same ascii policy."""
    start = span[0]
    line_start = raw.rfind("\n", 0, start) + 1
    base = raw[line_start:start]
    orig = raw[span[0]:span[1]]
    nl = orig.find("\n")
    inner = ""
    if nl >= 0:
        m = re.match(r"[ \t]*", orig[nl + 1:])
        inner = m.group(0)[len(base):] if m else "  "
    step = len(inner) if inner else 2
    ascii_ = "\\u" in orig
    txt = json.dumps(node, indent=step, ensure_ascii=ascii_)
    lines = txt.split("\n")
    return "\n".join(lines[:1] + [base + l for l in lines[1:]])


def repoint(node, remap):
    """Return a copy with every index reference moved to the first page
    of the node it named, or None when nothing changed."""
    changed = False
    out = json.loads(json.dumps(node))
    if out.get("t") == "jump" and isinstance(out.get("goto"), int):
        nv = remap[out["goto"]]
        changed |= nv != out["goto"]
        out["goto"] = nv
    if out.get("t") == "choice":
        for opt in out.get("opts", out.get("options", [])) or []:
            if isinstance(opt, dict):
                if isinstance(opt.get("goto"), int):
                    nv = remap[opt["goto"]]
                    changed |= nv != opt["goto"]
                    opt["goto"] = nv
                chk = opt.get("check")
                if isinstance(chk, dict):
                    for k in ("pass", "fail"):
                        if isinstance(chk.get(k), int):
                            nv = remap[chk[k]]
                            changed |= nv != chk[k]
                            chk[k] = nv
    return out if changed else None


def split_file(path, dry):
    raw = open(path, encoding="utf-8").read()
    j = json.loads(raw)
    nodes = j.get("nodes", [])
    spans = node_spans(raw)
    assert len(spans) == len(nodes), (path, len(spans), len(nodes))
    plan = {}
    for i, n in enumerate(nodes):
        if n.get("t") in TEXT_TYPES and isinstance(n.get("text"), str):
            pg = pages_for(n["text"])
            if pg:
                plan[i] = pg
    if not plan:
        return 0, 0
    # old index → new index of its first page
    remap, k = {}, 0
    for i in range(len(nodes)):
        remap[i] = k
        k += len(plan.get(i, [None]))
    remap[len(nodes)] = k          # a goto one past the end stays one past the end
    edits = []                     # (span, replacement text)
    for i, n in enumerate(nodes):
        if i in plan:
            pages = []
            for pi, txt in enumerate(plan[i]):
                pn = json.loads(json.dumps(n))
                pn["text"] = txt
                if pi > 0:
                    pn.pop("voice", None)
                pages.append(dump_like(pn, raw, spans[i]))
            base = raw[raw.rfind("\n", 0, spans[i][0]) + 1:spans[i][0]]
            edits.append((spans[i], (",\n" + base).join(pages)))
        else:
            rp = repoint(n, remap)
            if rp is not None:
                edits.append((spans[i], dump_like(rp, raw, spans[i])))
    out = raw
    for (s, e), rep in sorted(edits, key=lambda x: -x[0][0]):
        out = out[:s] + rep + out[e:]
    j2 = json.loads(out)                       # validate BEFORE writing
    assert len(j2["nodes"]) == k, (path, len(j2["nodes"]), k)
    for i, n in enumerate(nodes):              # every old node survives as its first page
        first = j2["nodes"][remap[i]]
        assert first.get("t") == n.get("t"), (path, i)
    if not dry:
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
    return len(plan), k - len(nodes)


def main():
    dry = "--dry" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = only or sorted(glob.glob(os.path.join(SCENES, "**", "*.json"), recursive=True))
    tot_nodes = tot_added = tot_files = 0
    for f in files:
        if os.path.basename(f) == "index.json":
            continue
        n, added = split_file(f, dry)
        if n:
            tot_files += 1
            tot_nodes += n
            tot_added += added
            print("  %-34s %3d node(s) → +%d page(s)" % (os.path.relpath(f, SCENES), n, added))
    print("\npage_split · %d node(s) in %d file(s) → %d extra page(s) %s"
          % (tot_nodes, tot_files, tot_added, "planned" if dry else "written"))


if __name__ == "__main__":
    main()
