#!/usr/bin/env python3
"""gdinfer_check.py — catch the GDScript errors gdparse cannot see.

`gdparse` checks GRAMMAR. Godot ALSO runs type inference and rejects
`:=` whenever the right-hand side has no static type — a class of
error that is syntactically perfect and therefore invisible to the
linter. It has broken a shipped build:

    var x := {"a": 1}[k]     # inline literal, indexed  <- 2026-07-28
    var x := d.get("k", 0)   # Dictionary.get() returns Variant
    var x := node.call("f")  # call() returns Variant
    var x := n.get_meta("m") # get_meta() returns Variant

Deliberately NOT flagged (Godot infers these fine): an explicit cast
(`... as Array`), a typed declaration (`var x: String = ...`), and
indexing a container whose element type the file declares —
`Array[T]`, any `Packed*Array`, or a `String`.

The tool must report ZERO on a codebase that loads, or it becomes
noise and the next real break slips through with it.

Usage:  python3 godot/tools/gdinfer_check.py [path ...]
Exit 1 if anything is flagged. Run it beside gdparse, always.
"""
import os, re, sys

PATTERNS = [
    (re.compile(r':=\s*[\{\[].*[\}\]]\s*\['),
     "inline dict/array literal indexed on the spot"),
    (re.compile(r':=\s*[A-Za-z_][\w.]*\.get\s*\((?!.*\bas\b)'),
     "Dictionary/Object .get() returns Variant"),
    (re.compile(r':=\s*[A-Za-z_][\w.]*\.call\s*\((?!.*\bas\b)'),
     ".call() returns Variant"),
    (re.compile(r':=\s*[A-Za-z_][\w.]*\.get_meta\s*\((?!.*\bas\b)'),
     "get_meta() returns Variant"),
    (re.compile(r':=\s*JSON\.parse_string\s*\('),
     "JSON.parse_string() returns Variant"),
]

# a declaration that gives the name a known element type
_TYPED_DECL = r'\bvar\s+{0}\s*:\s*(Array\[|Packed\w*Array|String\b)'
# an inferred assignment from something with a known element type
_TYPED_FROM = (r'\bvar\s+{0}\s*:=\s*.*(\.split\(|PackedStringArray|'
               r'PackedInt|PackedFloat|PackedVector)')


def _declared_typed(lines, name):
    esc = re.escape(name)
    dec = re.compile(_TYPED_DECL.format(esc))
    frm = re.compile(_TYPED_FROM.format(esc))
    # `var shown := _f(...)` is typed when _f declares `-> String` /
    # `-> Array[T]` / `-> Packed*Array`, so chase the callee too.
    call = re.compile(r'\bvar\s+%s\s*:=\s*(?:self\.)?(\w+)\s*\(' % esc)
    for ln in lines:
        if dec.search(ln) or frm.search(ln):
            return True
        m = call.search(ln)
        if m:
            sig = re.compile(r'\bfunc\s+%s\s*\(.*\)\s*->\s*'
                             r'(String|Array\[|Packed\w*Array)'
                             % re.escape(m.group(1)))
            for other in lines:
                if sig.search(other):
                    return True
    return False


def scan(path):
    hits = []
    try:
        lines = open(path, encoding="utf-8").read().split("\n")
    except Exception:
        return hits
    for i, raw in enumerate(lines, 1):
        line = raw.split("#")[0]
        if ":=" not in line:
            continue
        flagged = False
        for rx, why in PATTERNS:
            if rx.search(line):
                hits.append((path, i, why, raw.strip()[:96]))
                flagged = True
                break
        if flagged:
            continue
        # bare container index — safe only when the element type is known
        m = re.search(r':=\s*([A-Za-z_]\w*)\s*\[', line)
        if m and not _declared_typed(lines, m.group(1)):
            hits.append((path, i, "index of an untyped container",
                         raw.strip()[:96]))
    return hits


def main():
    roots = sys.argv[1:] or ["godot"]
    files = []
    for root in roots:
        if os.path.isfile(root):
            files.append(root)
            continue
        for dp, _, fns in os.walk(root):
            if "/.godot" in dp:
                continue
            files += [os.path.join(dp, f) for f in fns if f.endswith(".gd")]
    hits = []
    for f in sorted(files):
        hits += scan(f)
    for path, ln, why, src in hits:
        print("%s:%d  %s\n    %s" % (path, ln, why, src))
    print("\n%d file(s) scanned · %d suspect inference site(s)"
          % (len(files), len(hits)))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
