"""One-shot driver: emits location JSONs for the 16 new gauntlet
locales. Pulls the SPACE_MAP from the hosts driver and translates
to the engine's locations/*.json shape (spaces array + adjacency
graph + start space + threshold flags).

Result: every new gauntlet host now has all four data inputs
loadable at start_scenario():
  · setup_<scenario>.json   (scenarios driver)
  · gravity_deck.json etc.  (scenarios driver)
  · hands/<hand>.json       (placeholder fallback in engine)
  · locations/<loc>.json    (THIS driver)
"""
import os, sys, json, importlib.util

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(_HERE, "../../../.."))
LOCATIONS = os.path.join(REPO, "godot/resources/games/locations")


def _load_hosts_config():
    spec = importlib.util.spec_from_file_location(
        "arcana_hosts_cfg",
        os.path.join(_HERE, "make_arcana_hosts_2026_06_21.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.HOSTS


def emit_location(host):
    # Last 3 spaces in the host's space_map are designated thresholds;
    # everything else is a named station. The default_space gets
    # is_start = True.
    space_ids = [s[0] for s in host["space_map"]]
    threshold_ids = space_ids[-3:]
    spaces = []
    for i, (sid, bx, by, _yaw) in enumerate(host["space_map"]):
        kind = "threshold" if sid in threshold_ids else "named"
        # Convert blender (x, y) to a 2D top-down board layout in pixels
        # for the engine's drag/map view. Scale up so the spaces sit
        # reasonably apart (1 blender unit ≈ 80px).
        pos_x = int(600 + bx * 80)
        pos_y = int(400 - by * 80)  # flip Y so north reads upward in the map
        space = {
            "id": sid,
            "label": sid.upper().replace("_", " "),
            "kind": kind,
            "pos_xy": [pos_x, pos_y],
        }
        if sid == host["default_space"]:
            space["is_start"] = True
        if kind == "threshold":
            space["always_visible"] = True
        spaces.append(space)

    # Adjacency: each space connects to its 3 nearest neighbours by
    # Blender distance. Small bidirectional graph — guarantees
    # connectivity without hand-tuning per room.
    def dist(a, b):
        return ((a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5

    adjacency = {}
    sm = host["space_map"]
    for i, src in enumerate(sm):
        others = sorted(
            ((j, dist(src, sm[j])) for j in range(len(sm)) if j != i),
            key=lambda t: t[1])
        neighbors = [sm[j][0] for j, _ in others[:3]]
        adjacency[src[0]] = neighbors
    # Ensure symmetry: if A→B is in adjacency[A], B→A must be in adjacency[B].
    for a, nbrs in list(adjacency.items()):
        for b in nbrs:
            if a not in adjacency[b]:
                adjacency[b].append(a)

    return {
        "id": host["locale_id"],
        "title": host["locale_id"].replace("_", " ").title(),
        "subtitle": host["scenario_label"],
        "bg_codex_card": f"assets/gallery/{host['arcana_key']}.png",
        "notes": (f"SCAFFOLD location for {host['arcana_label']}. "
                  "Spaces + adjacency derived from the host's "
                  "SPACE_MAP. Per-locale tuning (drift attractors, "
                  "space_effects, search_pile assignments) is TODO."),
        "spaces": spaces,
        "adjacency": adjacency,
        "drift_attractors": {
            "notes": "Synthesised — pick deliberately when authoring.",
            "primary": host["default_space"],
            "secondary": (space_ids[1] if len(space_ids) > 1
                          else host["default_space"]),
            "tertiary": (space_ids[2] if len(space_ids) > 2
                          else host["default_space"]),
        },
    }


def main():
    hosts = _load_hosts_config()
    n = 0
    for h in hosts:
        out = os.path.join(LOCATIONS, h["locale_id"] + ".json")
        if os.path.exists(out):
            # Don't trample anything authored. (None should exist yet
            # for the new locales, but be defensive.)
            print(f"  ⚠ {h['locale_id']}.json exists — skipping")
            continue
        with open(out, "w") as f:
            json.dump(emit_location(h), f, indent=2)
        print(f"  ✓ {out}")
        n += 1
    print(f"\nwrote {n} location JSONs")


if __name__ == "__main__":
    main()
