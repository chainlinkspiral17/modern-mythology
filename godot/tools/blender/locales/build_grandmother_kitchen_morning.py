"""Abuela's kitchen, the eggs mornings — vol 6 ch 16 · 18 · 22 · 23.

DRAFT 2 (2026-10-06): this locale and `ramos_kitchen_morning` were two template
builds of ONE canonical room — Graciela Ramos's kitchen on Ashberry Drive
— a store-kit counter, a centre table and a grey box each. Both now
build the room from `_props/ramos_kitchen.py` (read its docstring for
the prose anchors and the layout) and differ only in the DRESSING:
the yellow plate with the chip and the eggs at his place, her
Sentinel and her coffee, the small bowl of fruit, the second letter and its
pen, the microwave, the caldo / the comal / the skillet / the moka on the
range, the onion and the bay leaf on the board, his truck in the drive;
the clock above the stove at 8:15.

Draft 3 targets (see the module): the half-bath door off the hall; steam
over the pot (a mood); the cordless phone's charge light as a practical.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path:
    sys.path.insert(0, _BT)
from _props.geometry import clear_scene, export_glb
from _props.ramos_kitchen import build_kitchen


def main():
    clear_scene()
    build_kitchen("eggs")
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/grandmother_kitchen_morning.glb"))
    print(f"\n[build_grandmother_kitchen_morning] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
