#!/usr/bin/env python3
"""glass_alpha_audit.py — builder parts NAMED as glass but written opaque.

LocaleGlass (scripts/LocaleGlass.gd) makes a surface transparent only when
its vertex alpha is below 0.98. A pane a builder writes at alpha 1.0 is a
painted slab: the monitor room's west wall hid the whole Pacific, and the
Dabney fridges' doors hid their drinks (pass 306, 2026-11-08).

This is a REPORT, not a gate: not every opaque "glass" is a bug. A mirror
is not a pane; a lit display or a dark night window may be meant opaque;
and a pane with nothing modelled behind it would open onto the void if it
were made transparent. Read each candidate by render before changing it.

    python3 tools/audit/glass_alpha_audit.py           # every builder
    python3 tools/audit/glass_alpha_audit.py diner     # builders matching
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.path.normpath(os.path.join(HERE, "..", "blender"))
ALPHA_MAX = 0.98

GLASSY = re.compile(r"(glass|pane|windshield|storefront)", re.I)
# drinkware, mirrors, spectacles and the like: named glass, not a pane
NOT_PANE = re.compile(
    r"(mirror|eyeglass|glasses|spectacle|tumbler|whiskey|wine|beer|shot_glass|"
    r"pint|goblet|jar|bottle|cup|mug|lens|shard|ashtray|frame|mullion|sill|"
    r"rim|lid|panel|palette|crate|recess|basin|vanity|water|dish|broken|glint|"
    r"header|storefronts|propane|rack|rail|post|base|head|decal|bulb|seam|ledge|"
    r"band|chain|top|liquid)", re.I)
CALLS = {"make_box", "make_rot_box", "make_cyl", "make_chamfer_box", "_mb", "_mc"}

# Parts read and judged OPAQUE ON PURPOSE (builder, name as the report
# prints it) -> why. They are counted, not listed. Add a part here only
# after reading it in its builder and, where it is on a cue frame, by render.
JUDGED = {
    ("build_cabin_interior.py", "EBed_Win_Glass"): "painted cedar view; nothing modelled behind",
    ("build_hans_bakery_back_kitchen.py", "FOH_Street_Pane"): "painted street; nothing modelled behind",
    ("build_chillwave_interior.py", "Dome_{}_Glass"): "a lit lamp dome (frosted)",
    ("build_graustark.py", "Minstral_Porthole_{}_Glass"): "a porthole onto an unmodelled hull",
    ("build_diner.py", "Wall_W_mid_glass_{}"): "COL_NIGHT_GLASS: the night window, opaque by design",
    ("build_diner.py", "PhoneBooth_GlassEW_{}"): "faces a solid booth body",
    ("build_diner.py", "PhoneBooth_GlassS"): "faces a solid booth body",
    ("build_diner.py", "WestFormal_Glass_{}"): "drinkware",
    ("build_diner.py", "PrivGlass_{}"): "drinkware",
    ("build_diner.py", "Damb_{}_Glass"): "drinkware",
    ("build_diner.py", "Formal_Glass_{}_{}"): "drinkware",
    ("build_dean_offices.py", "{}_Glass_{}"): "goggle lenses",
    ("build_dean_offices.py", "Lob_Entry_Glass_{}"): "frosted entry doors, shut; nothing modelled outside",
    ("build_foxhole_bar.py", "Entrance_Door_Leaf_{}_Glass"): "painted with the street's sodium light",
    ("build_club_sharp.py", "Arcade_Prize_Counter_Glass"): "a counter top; the prizes stand on it",
    ("build_airport_cabin.py", "Store_Cooler_Glass"): "faces a solid cooler body; no stock modelled (N+1)",
    ("build_copy_shop.py", "Shop_Front_Glass"): "night glass with the blinds down behind it",
    ("build_caltech_dabney.py", "Sp_Window_Glass"): "painted daylight; nothing modelled outside",
    ("build_carrie_city.py", "Dryer_Door_Glass"): "a dryer porthole; nothing inside",
    ("build_editing_suite.py", "Suite_Window_Pane"): "the text: 'the one window and nothing out of it: a pale, featureless pane'",
    ("build_wagner_home.py", "Jacob_Window_Pane_{}"): "on a solid house body",
    ("build_nick_house.py", "Front_Window_Pane_{}"): "dark at night, 'no lamp lit behind them'",
    ("build_small_wood_backyard.py", "House_Window_{}_Glass"): "on the house wall; nothing modelled inside",
    ("build_centro_break_room.py", "Dock_Door_WireGlass"): "wired glass in a door",
    ("build_cathedral_interior.py", "RiverWindow_Glass"): "a dark-blue painted slab; the runtime light brings the river's spill",
    ("build_missing_link_exterior.py", "Diner_DoorGlass"): "COL_GLOW: the lit diner seen from outside",
}


def _const_colors(tree):
    """Module-level NAME = (r, g, b, a) assignments."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Tuple):
            vals = node.value.elts
            if len(vals) == 4 and all(isinstance(v, ast.Constant) for v in vals):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        out[t.id] = tuple(v.value for v in vals)
    return out


def _name_of(arg):
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    if isinstance(arg, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in arg.values)
    return None


def _alpha_of(call, consts):
    """The colour argument's alpha: the last 4-tuple of constants, or a
    module-level colour constant named among the arguments."""
    for arg in reversed(call.args):
        if isinstance(arg, ast.Tuple) and len(arg.elts) == 4 \
                and all(isinstance(v, ast.Constant) for v in arg.elts):
            return float(arg.elts[3].value)
        if isinstance(arg, ast.Name) and arg.id in consts:
            return float(consts[arg.id][3])
    return None


def scan(path):
    src = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    consts = _const_colors(tree)
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        fn = node.func.id if isinstance(node.func, ast.Name) else \
            node.func.attr if isinstance(node.func, ast.Attribute) else ""
        if fn not in CALLS:
            continue
        name = _name_of(node.args[0])
        if not name or not GLASSY.search(name) or NOT_PANE.search(name):
            continue
        a = _alpha_of(node, consts)
        if a is not None and a >= ALPHA_MAX:
            rows.append((node.lineno, name))
    return rows


def main():
    want = sys.argv[1:]
    total = 0
    judged = 0
    for dirpath, _dirs, files in os.walk(BLENDER):
        for fn in sorted(files):
            if not (fn.startswith("build_") and fn.endswith(".py")):
                continue
            if want and not any(w in fn for w in want):
                continue
            rows = scan(os.path.join(dirpath, fn))
            keep = [(ln, nm) for ln, nm in rows if (fn, nm) not in JUDGED]
            judged += len(rows) - len(keep)
            rows = keep
            if not rows:
                continue
            total += len(rows)
            print("== %s" % os.path.relpath(os.path.join(dirpath, fn), BLENDER))
            for ln, name in rows:
                print("   %5d  %s" % (ln, name))
    print("\nglass_alpha_audit · %d part(s) named as glass, written opaque "
          "(alpha >= %.2f), not yet judged — read each by render before changing it"
          " · %d judged opaque on purpose (JUDGED)" % (total, ALPHA_MAX, judged))


if __name__ == "__main__":
    main()
