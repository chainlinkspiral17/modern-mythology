#!/usr/bin/env python3
"""Audit gauntlet per-space FP camera/background wiring.

For every location JSON (resources/games/locations/*.json), every board
space must resolve to a first-person vantage, or the gauntlet falls
back to the top-down map for that space. The FP render has four tiers
(see TarotGauntletGame._render_current_space):
  1. HOST 3D      — the location's *GauntletHost.gd SPACE_MAP
  2. STANDALONE 3D — TarotGauntletGame._STANDALONE_SPACE_VANTAGES +
                     a _LOCATION_SCENE_PATHS entry to load
  3. painted PNG   — assets/gallery/locations/<loc>_fp_<space>.png
  4. top-down map  — the fallback we want to avoid

This tool reports, per location, which board spaces have NO FP source.
Run from the repo root:  python3 godot/tools/audit_gauntlet_locales.py
"""
import json, re, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOC  = os.path.join(ROOT, "resources/games/locations")
SCR  = os.path.join(ROOT, "scripts")
GAME = os.path.join(ROOT, "scenes/games/TarotGauntletGame.gd")
ART  = os.path.join(ROOT, "assets/gallery/locations")

# location id -> host script basename
HOST = {
 "asylum_ward_c":"AsylumWardCGauntletHost","bayou_lighthouse":"LighthouseGauntletHost",
 "carnival_lot":"CarnivalLotGauntletHost","cathedral":"CathedralGauntletHost",
 "christian_ice_co":"ChristianIceGauntletHost","courthouse_chamber":"CourthouseGauntletHost",
 "daigles_roadhouse":"RoadhouseGauntletHost","dambrosios":"DinerGauntletHost",
 "elicia_bungalow":"BungalowGauntletHost","ember_ash_office":"EmberAshOfficeGauntletHost",
 "frog_knows_best":"FrogKnowsBestGauntletHost","lacombe_service_garage":"ServiceGarageGauntletHost",
 "le_roulant_casino":"RoulantCasinoGauntletHost","mixing_glass":"MixingGlassGauntletHost",
 "parish_cemetery":"ParishCemeteryGauntletHost","riverboat_interior":"RiverboatGauntletHost",
 "roadside_chapel":"ChapelGauntletHost","roberts_house":"RobertsHouseGauntletHost",
 "simon_apartment":"SimonApartmentGauntletHost","solenade_garden":"SolenadeGardenGauntletHost",
 "static_drive_in":"DriveInGauntletHost","the_hierophant_circuit":"HierophantCircuitGauntletHost",
 "wgur_transmitter_shack":"WgurShackGauntletHost",
}

def _dict_keys(txt, decl):
    """Top-level string keys of a GDScript dict literal named `decl`."""
    m = re.search(decl + r"\b[^{]*\{", txt)
    if not m: return None
    i = m.end()-1; depth = 0; body = ""
    for j in range(i, len(txt)):
        if txt[j] == '{': depth += 1
        elif txt[j] == '}':
            depth -= 1
            if depth == 0: body = txt[i+1:j]; break
    keys = []; d2 = 0
    for line in body.splitlines():
        km = re.match(r'"([^"]+)"\s*:', line.strip())
        if km and d2 == 0: keys.append(km.group(1))
        d2 += line.count('{')-line.count('}')
    return keys

def host_space_keys(base):
    p = os.path.join(SCR, base+".gd")
    if not os.path.exists(p): return None
    return _dict_keys(open(p).read(), "SPACE_MAP")

def standalone_block(loc_id, game_txt):
    """Keys of _STANDALONE_SPACE_VANTAGES[loc_id], or [] if absent."""
    m = re.search(r"_STANDALONE_SPACE_VANTAGES\s*:=\s*\{", game_txt)
    i = m.end()-1; depth = 0
    for j in range(i, len(game_txt)):
        if game_txt[j]=='{': depth+=1
        elif game_txt[j]=='}':
            depth-=1
            if depth==0: outer = game_txt[i+1:j]; break
    lm = re.search(r'"'+re.escape(loc_id)+r'"\s*:\s*\{', outer)
    if not lm: return []
    i2 = lm.end()-1; d=0
    for j in range(i2, len(outer)):
        if outer[j]=='{': d+=1
        elif outer[j]=='}':
            d-=1
            if d==0: inner = outer[i2+1:j]; break
    return [k.group(1) for k in re.finditer(r'"([^"]+)"\s*:', inner)]

def main():
    game_txt = open(GAME).read()
    scene_paths = _dict_keys(game_txt, "_LOCATION_SCENE_PATHS") or []
    problems = 0
    for lf in sorted(os.listdir(LOC)):
        if not lf.endswith(".json"): continue
        loc = lf[:-5]
        d = json.load(open(os.path.join(LOC, lf)))
        board = [(s.get("id") if isinstance(s, dict) else s) for s in d.get("spaces", [])]
        hk = host_space_keys(HOST.get(loc, "")) or []
        sk = standalone_block(loc, game_txt)
        has_scene = loc in scene_paths
        missing = []
        for sp in board:
            in_host = sp in hk
            in_std  = sp in sk and has_scene
            has_png = os.path.exists(os.path.join(ART, f"{loc}_fp_{sp}.png"))
            if not (in_host or in_std or has_png):
                missing.append(sp)
        if missing:
            problems += 1
            print(f"\n== {loc} :: {len(missing)}/{len(board)} spaces have NO FP source (top-down fallback) ==")
            print(f"   host={len(hk)} keys, standalone={'yes' if sk else 'MISSING'}, scene_path={'yes' if has_scene else 'MISSING'}")
            print(f"   missing: {missing}")
        else:
            print(f"ok {loc} :: all {len(board)} spaces FP-wired")
    print(f"\n=== {problems} location(s) with FP gaps ===")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
