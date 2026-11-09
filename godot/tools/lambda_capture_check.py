#!/usr/bin/env python3
"""lambda_capture_check.py — a lambda cannot write a captured local (2026-11-09).

GDScript lambdas capture local variables BY VALUE. `var pending := x` then
`func(v): pending = v` in one lambda and `use(pending)` in another: the second
never sees the write. SettingsOverlay's SCREEN SIZE did exactly this — APPLY
always applied the size saved before the page opened ("everytime I hit apply
in the options menu, the window resizes down to 720").

Flags, per function: a local `var NAME` (a value type by its initialiser or
annotation, or untyped) that a lambda body ASSIGNS (`NAME = …`, `NAME += …`).
Containers mutated in place (`arr.append`, `d[k] = v`) are fine and not
flagged. A one-element Array / Dictionary is the way to share a value.

    python3 godot/tools/lambda_capture_check.py [files…]   # nonzero exit on a hit
"""
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
VAR = re.compile(r"^(\t+)var\s+([A-Za-z_]\w*)")
ASSIGN = re.compile(r"^\t+([A-Za-z_]\w*)\s*(?:[-+*/%]|\|\||&&)?=(?!=)")
LAMBDA = re.compile(r"\bfunc\s*\([^)]*\)\s*(?:->\s*[\w\[\], ]+\s*)?:\s*(.*)$")
INLINE = re.compile(r"^\s*([A-Za-z_]\w*)\s*(?:[-+*/%])?=(?!=)")


def indent(line):
    return len(line) - len(line.lstrip("\t"))


def check(path):
    hits = []
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    func_locals = {}        # name -> indent it was declared at
    lam = []                # stack of (indent of the line holding the lambda, names declared inside)
    for i, raw in enumerate(lines, 1):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        ind = indent(line)
        if ind == 0:
            if line.startswith(("func ", "static func ")):
                func_locals, lam = {}, []
            continue
        while lam and ind <= lam[-1][0]:
            lam.pop()
        m = VAR.match(line)
        if m:
            (lam[-1][1] if lam else func_locals)[m.group(2)] = ind
            if lam:
                lam[-1][1][m.group(2)] = ind
        a = ASSIGN.match(line)
        if a and lam and not m:
            name = a.group(1)
            inner = set()
            for _, names in lam:
                inner |= set(names)
            if name in func_locals and name not in inner:
                hits.append((i, name, raw.strip()))
        lm = LAMBDA.search(line)
        if lm and not line.lstrip().startswith(("func ", "static func ")):
            body = lm.group(1).strip()
            if body:                      # one-line lambda: func(v): x = v
                b = INLINE.match(body)
                if b and b.group(1) in func_locals:
                    hits.append((i, b.group(1), raw.strip()))
            else:
                lam.append((ind, {}))
    return hits


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not files:
        for base, dirs, fs in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".godot", "addons", "vendor")]
            files += [os.path.join(base, f) for f in fs if f.endswith(".gd")]
    bad = 0
    for p in sorted(files):
        for i, name, text in check(p):
            print("CAPTURE  %s:%d  `%s` is a captured local — the write stays in the lambda · %s" % (
                os.path.relpath(p, ROOT), i, name, text[:70]))
            bad += 1
    print("lambda_capture_check · %d file(s) · %d write(s) to a captured local" % (len(files), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
