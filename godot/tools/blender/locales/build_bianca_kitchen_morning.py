"""Bianca's kitchen at 4:11 — vol 6 ch 22 / 23 (the Miller kitchen, after June).

DRAFT 2 (2026-10-07, BUILD BIG): this locale and `miller_kitchen` were template
builds of ONE room — the Miller kitchen on Meadowlark Circle. Both now build
the room from `_props/miller_kitchen.py` (its docstring carries the prose
anchors and the plan: a 9 x 7 m open kitchen on `_props/kitchen_kit`, the
family room through a wide opening, the front hall and its stair) and differ
only in the DRESSING:
the kettle on the burner and the grinder, her cup at Mike's end, the
cordless, the stationery and its pen and the small drawer, Sammy's cereal at
the head; no sedan; 4:11.
The story props of the earlier Miller passes (the landline and its worn
patch, the French toast, the hands' worn places, the kolaches, the jar, the
photographs, the chair wear including Mike's two ages, the sedan, the lit
garage window) are carried in the module at their new places.
"""
import os, sys
_BT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if _BT not in sys.path:
    sys.path.insert(0, _BT)
from _props.geometry import clear_scene, export_glb
from _props.miller_kitchen import build_kitchen


def main():
    clear_scene()
    build_kitchen("dawn")
    out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "../../../assets/3d/locales/bianca_kitchen_morning.glb"))
    print(f"\n[build_bianca_kitchen_morning] exporting to {out}")
    export_glb(out)


if __name__ == "__main__":
    main()
