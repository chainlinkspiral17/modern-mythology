#!/usr/bin/env python3
"""no_embed.py — debug runs open in their OWN window (2026-11-09).

The user: "when I run it in debug, it doesn't work" — the screen size. Run
from the editor (F5), Godot 4.4+ plays the game EMBEDDED in its Game tab, and
an embedded game cannot change its window: SCREEN SIZE (ULTRAWIDE,
FULLSCREEN …) does nothing there. This turns the editor's "Embed Game on Next
Play" off for this project, so F5 opens a real window and the saved screen
size applies (Settings → SCREEN SIZE; FULLSCREEN = the screen's own maximum).

It writes the project's editor metadata (godot/.godot/editor/
project_metadata.cfg, local, not in git): [game_view] embed_on_play=false.
CLOSE GODOT FIRST — the editor rewrites that file when it quits.

    python3 godot/tools/no_embed.py          # turn embedding off
    python3 godot/tools/no_embed.py --on     # back to the Game tab
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.normpath(os.path.join(HERE, "..", ".godot", "editor", "project_metadata.cfg"))


def main():
    value = "true" if "--on" in sys.argv else "false"
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    text = open(CFG, encoding="utf-8").read() if os.path.exists(CFG) else ""
    m = re.search(r"^\[game_view\][^\[]*", text, re.M)
    if m:
        block = m.group(0)
        if re.search(r"^embed_on_play=.*$", block, re.M):
            new = re.sub(r"^embed_on_play=.*$", "embed_on_play=" + value, block, flags=re.M)
        else:
            new = block.rstrip("\n") + "\nembed_on_play=" + value + "\n\n"
        text = text[:m.start()] + new + text[m.end():]
    else:
        text = text.rstrip("\n") + ("\n\n" if text.strip() else "") + "[game_view]\n\nembed_on_play=" + value + "\n"
    open(CFG, "w", encoding="utf-8").write(text)
    print("embed_on_play=%s in %s" % (value, CFG))
    print("debug runs (F5) now open in their own window" if value == "false" else "debug runs play in the editor's Game tab again")
    print("(Godot must have been closed while this ran; open it now.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
