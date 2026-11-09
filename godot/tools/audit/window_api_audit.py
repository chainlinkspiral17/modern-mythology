#!/usr/bin/env python3
"""window_api_audit.py — the window changes through the root Window (2026-11-09).

The user: "Ultrawide setting isn't taking, still." / "In scenes are back to
their old resolution." Settings sized the window with
DisplayServer.window_set_size: the OS window grew, the root Window node never
heard (the DisplayServer records the size it was asked for, so its "window
changed" callback does not fire) and the game drew at its old size inside the
new window. A size, mode or position change of the game's window goes through
the Window node (get_tree().root.size / .mode / .position), whose setters
call the DisplayServer AND resize the viewport.

    python3 tools/audit/window_api_audit.py     # nonzero exit on a direct call
"""
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BAD = re.compile(r"DisplayServer\.window_set_(size|mode|position)\s*\(")


def main():
    bad = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".godot", "addons", "vendor")]
        for f in files:
            if not f.endswith(".gd"):
                continue
            p = os.path.join(base, f)
            for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                code = line.split("#", 1)[0]
                if BAD.search(code):
                    print("DIRECT  %s:%d  %s" % (os.path.relpath(p, ROOT), i, line.strip()[:90]))
                    bad += 1
    print("window_api_audit · %d direct DisplayServer window change(s)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
