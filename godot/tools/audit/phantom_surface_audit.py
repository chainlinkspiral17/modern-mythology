#!/usr/bin/env python3
"""phantom_surface_audit.py — detail passes that name a surface the
builder never put there (2026-09-10).

Fourteen locales carried the same bug: a later "detail pass" hard-
coded a desk / counter / bar / bench origin and a top height from a
comment ("approx at (0, -1), top 1.05") while the builder's own
object stood somewhere else. Thin, mounted and legged props on the
phantom surface pass every geometry gate, so this audit reads the
SOURCE: every `<name>_x = <n>` / `<name>_y = <n>` / `<name>_z = <n>`
(or `<name>_top_z`) triple inside a builder is a claim that a
surface exists at (x, y) with its top near z. The claim is checked
against the recorded boxes: some box whose footprint contains
(x, y) must top out within TOL of z.

    python3 godot/tools/audit/phantom_surface_audit.py            # all
    python3 godot/tools/audit/phantom_surface_audit.py <locale>…  # some

Informational. A hit is a line to READ, not a count to drive down —
a few claims are legitimately a floor (z 0.0) or a hanging thing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prop_overlap_audit as P
import vantage_obstruction_audit as VO

TOL = 0.08
ASSIGN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*?)_(x|y|z|top_z|cx|cy)\s*=\s*([+-]?\s*(?:ROOM_[DW]\s*[-+/*]\s*)?[0-9.]+(?:\s*[-+*/]\s*[0-9.]+)?)\s*(#.*)?$")
SURFACE_STEM = re.compile(r"(desk|counter|bar|table|bench|shelf|sill|top|ledge|stand|dresser|nightstand|vanity|dash|console|altar|pulpit|lectern|pew|seat|cart|tray|island|workbench|surface|plinth|pedestal|mantel|hearth|stove|dryer|washer|fridge|freezer|cooler|crate|box|bed|bunk|cot|pallet|step|stair|porch|deck)", re.I)


def eval_num(expr, room_w, room_d):
    e = expr.replace("ROOM_W", str(room_w)).replace("ROOM_D", str(room_d))
    try:
        return float(eval(e, {"__builtins__": {}}, {}))
    except Exception:
        return None


def room_consts(src):
    w = d = None
    m = re.search(r"\bROOM_W\s*=\s*([0-9.]+)", src)
    if m:
        w = float(m.group(1))
    m = re.search(r"\bROOM_D\s*=\s*([0-9.]+)", src)
    if m:
        d = float(m.group(1))
    return w or 0.0, d or 0.0


XY_ASSIGN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*?)_(x|y|cx|cy)\s*=\s*([+-]?\s*(?:ROOM_[DW]\s*[-+/*]\s*)?[0-9.]+(?:\s*[-+*/]\s*[0-9.]+)?)\s*(#.*)?$")
XY_TUPLE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*?)_?x\s*,\s*([A-Za-z_][A-Za-z0-9_]*?)_?y\s*=\s*([^,#]+),\s*([^#]+?)\s*(#.*)?$")
Z_ASSIGN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*?)_(z|top_z)\s*=\s*([+-]?\s*(?:ROOM_[DW]\s*[-+/*]\s*)?[0-9.]+(?:\s*[-+*/]\s*[0-9.]+)?)\s*(#.*)?$")
WINDOW = 6          # lines: an x/y pair and a z within this many lines are one claim


def claims_in(path):
    """Every (x, y, z) a detail pass hard-codes: an `<a>_x = n` /
    `<a>_y = n` pair (or `ax, ay = n, n`) with a `<b>_z = n` or
    `<b>_top_z = n` within WINDOW lines — the stems need not match
    (rc_x / rc_y / counter_z was the courthouse's shape)."""
    src = open(path).read()
    rw, rd = room_consts(src)
    lines = src.splitlines()
    xs, ys, zs = {}, {}, []           # stem → (value, line)
    pairs = []                        # (x, y, line)
    for ln, line in enumerate(lines, 1):
        m = XY_ASSIGN.match(line)
        if m:
            stem, axis, expr = m.group(1), m.group(2), m.group(3)
            v = eval_num(expr, rw, rd)
            if v is None:
                continue
            axis = {"cx": "x", "cy": "y"}.get(axis, axis)
            (xs if axis == "x" else ys)[stem] = (v, ln)
            other = ys if axis == "x" else xs
            if stem in other and abs(other[stem][1] - ln) <= 2:
                x = xs[stem][0] if stem in xs else None
                y = ys[stem][0] if stem in ys else None
                pairs.append((stem, x, y, ln))
            continue
        m = XY_TUPLE.match(line)
        if m:
            vx = eval_num(m.group(3).strip(), rw, rd)
            vy = eval_num(m.group(4).strip(), rw, rd)
            if vx is not None and vy is not None:
                pairs.append((m.group(1), vx, vy, ln))
            continue
        m = Z_ASSIGN.match(line)
        if m:
            v = eval_num(m.group(3), rw, rd)
            if v is not None:
                zs.append((m.group(1), v, ln))
    out = []
    seen = set()
    for stem, x, y, ln in pairs:
        for zstem, z, zln in zs:
            if abs(zln - ln) <= WINDOW and z >= 0.25:
                key = (round(x, 2), round(y, 2), round(z, 2))
                if key in seen:
                    continue
                seen.add(key)
                out.append(("%s/%s" % (stem, zstem), x, y, z, ln))
    return out


def check(locale, boxes, claims):
    hits = []
    for stem, x, y, z, ln in claims:
        best = None
        for n, c, h in boxes:
            if VO.IGNORE.search(n):
                continue
            if c[0] - h[0] - 0.05 <= x <= c[0] + h[0] + 0.05 and c[1] - h[1] - 0.05 <= y <= c[1] + h[1] + 0.05:
                top = c[2] + h[2]
                d = abs(top - z)
                if best is None or d < best[0]:
                    best = (d, n, top)
        if best is None:
            hits.append((stem, x, y, z, ln, "NOTHING under (%.1f, %.1f)" % (x, y)))
        elif best[0] > TOL:
            hits.append((stem, x, y, z, ln, "nearest top %s at %.2f (claim %.2f)" % (best[1], best[2], z)))
    return hits


def main():
    P.A.install_stubs()
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = sorted(os.path.basename(p)[6:-3] for p in os.listdir(P.A.LOCALES) if p.startswith("build_") and p.endswith(".py"))
    total = 0
    for locale in names:
        if only and locale not in only:
            continue
        path = os.path.join(P.A.LOCALES, "build_%s.py" % locale)
        claims = claims_in(path)
        if not claims:
            continue
        boxes = VO.boxes_for(locale)
        if not boxes:
            continue
        hits = check(locale, boxes, claims)
        if not hits:
            continue
        print("== %s · %d surface claim(s), %d unbacked" % (locale, len(claims), len(hits)))
        for stem, x, y, z, ln, why in hits:
            print("   L%-5d %-22s (%.1f, %.1f, %.2f)  %s" % (ln, stem, x, y, z, why))
        total += len(hits)
    print("\nphantom_surface_audit · %d unbacked surface claim(s)" % total)


if __name__ == "__main__":
    main()
