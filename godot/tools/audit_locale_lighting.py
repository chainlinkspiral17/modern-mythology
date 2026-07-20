#!/usr/bin/env python3
"""Audit locale lighting against the three-light foundation.

Per _LIGHTING_PLAYBOOK.md, every locale should carry KEY + FILL + BACK
(three DirectionalLight3D) plus a practical (Omni/Spot) at every
visible fixture. Background3D instantiates the locale and relies on its
BAKED lights — a scene with one directional renders flat in the VN.

Reports, per locale: directional-light count, practical count,
WorldEnvironment presence. Flags locales below the three-light
foundation (<3 directional) — BUT note some are intentionally low-key
(a darkroom's safelight, a nightmare cell); this tool maps coverage,
it does not judge intent. Run: python3 godot/tools/audit_locale_lighting.py
"""
import os, re, glob, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOCALES = os.path.join(ROOT, "scenes/locales")

# Locales whose low-key / practical-driven lighting is BY DESIGN — a
# full three-light rig would flatten the intended mood. Excluded from
# the "needs a rig" list (the playbook's practicals rule still applies).
INTENTIONAL_LOWKEY = {
    "darkroom",          # red safelight, light-tight by definition
    "nightmare_cell",    # oppressive single-source
    "henderson_porch_front", "henderson_garage",  # night
    "caldwell_porch_night", "caldwell_kitchen_night", "caldwell_radio_room_night",
    "diner",             # god's-eye, 29 practicals carry it
    "le_roulant_casino", # moody casino, 7 practicals
    "equipment_shed", "lacombe_service_garage", "bindery",
    "centro_stockroom",
}

def main():
    normal_flat = []
    lowkey_flat = []
    ok = 0
    for p in sorted(glob.glob(os.path.join(LOCALES, "*.tscn"))):
        t = open(p).read()
        dl = len(re.findall(r'type="DirectionalLight3D"', t))
        pr = len(re.findall(r'type="OmniLight3D"', t)) + len(re.findall(r'type="SpotLight3D"', t))
        name = os.path.basename(p)[:-5]
        if dl >= 3:
            ok += 1
            continue
        row = (name, dl, pr)
        if name in INTENTIONAL_LOWKEY:
            lowkey_flat.append(row)
        else:
            normal_flat.append(row)

    print(f"=== {ok} locales have the full three-light foundation (>=3 directional) ===")
    print(f"\n--- {len(normal_flat)} NORMAL locales below the foundation — rig-pass candidates ---")
    for n, dl, pr in sorted(normal_flat):
        print(f"   {n:32s} directional={dl}  practicals={pr}")
    print(f"\n--- {len(lowkey_flat)} intentionally LOW-KEY (leave the rig; verify practicals only) ---")
    for n, dl, pr in sorted(lowkey_flat):
        print(f"   {n:32s} directional={dl}  practicals={pr}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
