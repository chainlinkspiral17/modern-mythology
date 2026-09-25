#!/usr/bin/env python3
"""contact_diff — which frames changed between two contact sheets, and how.

The user on the 09-25 sheet: "seeing lots more new issues … hopefully
it's all work in progress and not stuff getting broken." The answer is
a diff, not a guess: per frame, the mean absolute pixel difference on a
160×90 greyscale reduction (film grain and dither wash out below ~6),
the brightness before and after, and NEW / GONE frames. A draft's
report should say which frames it changed and why.

    python3 godot/tools/audit/contact_diff.py <old_sheet_dir> <new_sheet_dir> [--min 6] [--top 60]
The dirs are the `godot/qa/contact` folders extracted from two
`origin/qa/contact` commits (`git archive origin/qa/contact | tar -x -C …`).
Exit 0 always; the report is the product.
"""
import os
import sys

from PIL import Image, ImageChops, ImageStat


def frames(root):
    out = {}
    for loc in sorted(os.listdir(root)):
        d = os.path.join(root, loc)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".jpg"):
                out[(loc, f)] = os.path.join(d, f)
    return out


def main():
    lo = 6.0
    top = 60
    args = []
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--min":
            lo = float(argv[i + 1]); i += 2
        elif argv[i] == "--top":
            top = int(argv[i + 1]); i += 2
        else:
            args.append(argv[i]); i += 1
    if len(args) != 2:
        print(__doc__)
        return 2
    old, new = frames(args[0]), frames(args[1])
    rows = []
    for key, pb in new.items():
        pa = old.get(key)
        if pa is None:
            rows.append((999.0, key, "NEW"))
            continue
        a = Image.open(pa).convert("L").resize((160, 90))
        b = Image.open(pb).convert("L").resize((160, 90))
        d = ImageStat.Stat(ImageChops.difference(a, b)).mean[0]
        if d >= lo:
            rows.append((d, key, "mean %3.0f -> %3.0f" % (ImageStat.Stat(a).mean[0], ImageStat.Stat(b).mean[0])))
    gone = [k for k in old if k not in new]
    rows.sort(reverse=True)
    by_loc = {}
    for d, (loc, f), note in rows:
        by_loc[loc] = by_loc.get(loc, 0) + 1
    for d, (loc, f), note in rows[:top]:
        print("  %5.1f  %-28s %-46s %s" % (d, loc, f, note))
    if len(rows) > top:
        print("  … %d more" % (len(rows) - top))
    for loc, f in gone[:20]:
        print("  GONE   %-28s %s" % (loc, f))
    print("contact_diff · %d frame(s) · %d changed (diff ≥ %.0f) · %d new · %d gone · locales: %s" % (
        len(new), len(rows), lo, sum(1 for r in rows if r[2] == "NEW"), len(gone),
        " ".join("%s:%d" % kv for kv in sorted(by_loc.items(), key=lambda kv: -kv[1])[:12])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
