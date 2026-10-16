"""Graciela's kitchen, the rosary afternoon — vol 6 ch 1 · ch 10.

DRAFT 2 (2026-10-06): this locale and `grandmother_kitchen_morning` were two template
builds of ONE canonical room — Graciela Ramos's kitchen on Ashberry Drive
— a store-kit counter, a centre table and a grey box each. Both now
build the room from `_props/ramos_kitchen.py` (read its docstring for
the prose anchors and the layout) and differ only in the DRESSING:
the rosary she is not using, the black coffee she is not
drinking, the cordless phone face-up and charging, the soup at his place,
the worn patches where the hands land; the skillet of eggs and chorizo,
the soup pot and the moka on the range; the empty drive with its oil
stain (the truck is the bait); the clock above the stove at 4:38.

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
    build_kitchen("rosary")
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/ramos_kitchen_morning.glb"))
    print(f"\n[build_ramos_kitchen_morning] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
