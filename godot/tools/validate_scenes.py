#!/usr/bin/env python3
"""
validate_scenes.py — Static integrity checker for Modern Mythology scene data.

Walks every scene under resources/scenes/vol*/ and the index.json registry and
verifies the data contract the Godot engine (GameEngine.gd / SceneDataDB.gd)
relies on at runtime, so broken content fails CI instead of failing in front of
a player.

Checks (ERROR = fails the build, WARNING = reported but non-fatal):

  ERROR
    * file does not parse as JSON
    * scene "id" field is missing or != filename stem
    * a "jump"/"choice" target scene does not exist on disk
    * an index.json entry has no corresponding file on disk
    * an unknown node "t" type is used
    * a node is missing a field the engine requires
    * a choice option is malformed (no text, or >1 of scene/goto/check)

  WARNING
    * a scene file on disk is not listed in index.json (drift). Files matching
      a name in scene_allowlist.txt (e.g. intentional *_stub placeholders and
      unwired drafts) are reported as "known-unindexed" and do not warn.

Usage:
    cd godot
    python3 tools/validate_scenes.py
    python3 tools/validate_scenes.py --scenes resources/scenes
    python3 tools/validate_scenes.py --quiet      # summary + problems only

Exit code: 0 if no ERRORs, 1 otherwise. WARNINGs never change the exit code.
Requires only the Python 3 standard library.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── Node contract ───────────────────────────────────────────────────────────
# Mirrors the dispatch table in scenes/game/GameEngine.gd::_dispatch().
# Each known node type maps to the fields the handler reads as required.
# Optional fields are documented in comments but not enforced.

REQUIRED_FIELDS: dict[str, list[str]] = {
    "narrate":    ["text"],            # optional: voice
    "say":        ["text"],            # speaker checked separately; optional: expr, voice, name
    "think":      ["text"],            # char optional (null/absent => protagonist); optional: voice
    "show":       ["char"],            # optional: expr, pos
    "hide":       [],                  # optional: pos
    "bg":         ["src"],             # src may be null (clears background)
    "substrate":  ["src"],
    "bgm":        ["src"],
    "sfx":        ["src"],
    "flag":       ["key"],             # optional: val
    "jump":       [],                  # scene optional (absent => end of scene)
    "end":        [],
    "interlude":  ["text"],            # optional: sub, duration
    "cg":         ["src"],             # optional: caption
    "choice":     ["opts"],            # optional: prompt
    "videoscene": [],                  # engine currently no-ops this
    "gallery":    [],                  # engine no-ops this
}
KNOWN_TYPES = set(REQUIRED_FIELDS)

# Fields whose presence is required but whose value is allowed to be null.
NULLABLE_FIELDS = {("bg", "src")}

VOL_ID_RE = re.compile(r"^vol(\d+)")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_allowlist(path: Path) -> set[str]:
    """Scene ids that are intentionally absent from index.json (stubs, drafts)."""
    if not path.exists():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def collect_scenes(scenes_dir: Path, rep: Report) -> dict[str, dict]:
    """Parse every vol*/*.json scene file. Records parse / id errors."""
    scenes: dict[str, dict] = {}
    for path in sorted(scenes_dir.glob("vol*/*.json")):
        sid = path.stem
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            rep.error(f"{path}: JSON parse error: {e}")
            continue
        if not isinstance(data, dict):
            rep.error(f"{path}: top-level value is not an object")
            continue
        declared = data.get("id")
        if declared != sid:
            rep.error(f"{path}: 'id' is {declared!r}, expected {sid!r} (must match filename)")
        scenes[sid] = data
    return scenes


def validate_nodes(sid: str, data: dict, all_ids: set[str], rep: Report) -> None:
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        rep.error(f"{sid}: 'nodes' is not an array")
        return
    for i, node in enumerate(nodes):
        where = f"{sid} node[{i}]"
        if not isinstance(node, dict):
            rep.error(f"{where}: not an object")
            continue
        t = node.get("t")
        if t not in KNOWN_TYPES:
            rep.error(f"{where}: unknown node type {t!r}")
            continue

        for field in REQUIRED_FIELDS[t]:
            if field not in node:
                rep.error(f"{where} ({t}): missing required field '{field}'")
            elif node[field] is None and (t, field) not in NULLABLE_FIELDS:
                rep.error(f"{where} ({t}): field '{field}' is null")

        if t in ("say", "think"):
            _validate_speaker(where, t, node, rep)
        elif t == "jump":
            tgt = node.get("scene")
            if tgt and tgt not in all_ids:
                rep.error(f"{where} (jump): target scene {tgt!r} does not exist")
        elif t == "choice":
            _validate_choice(where, node, all_ids, rep)


def _validate_speaker(where: str, t: str, node: dict, rep: Report) -> None:
    """Speaker-key checks for say/think.

    The engine reads the speaker from "char" (GameEngine._do_say/_do_think).
    A "say" must name a speaker; "think" may omit it (the protagonist's own
    inner voice renders unattributed). A "c" key with no "char" is the known
    typo that silently drops the speaker — always an error.
    """
    if "c" in node and "char" not in node:
        rep.error(f"{where} ({t}): uses key 'c' for the speaker — should be 'char'")
        return
    if t == "say" and not node.get("char"):
        rep.error(f"{where} (say): missing speaker (field 'char')")


def _validate_choice(where: str, node: dict, all_ids: set[str], rep: Report) -> None:
    opts = node.get("opts", [])
    if not isinstance(opts, list) or not opts:
        rep.error(f"{where} (choice): 'opts' must be a non-empty array")
        return
    for j, opt in enumerate(opts):
        ow = f"{where} opt[{j}]"
        if not isinstance(opt, dict):
            rep.error(f"{ow}: not an object")
            continue
        if not opt.get("text"):
            rep.error(f"{ow}: missing 'text'")
        targets = [k for k in ("scene", "goto", "check") if k in opt]
        if len(targets) > 1:
            rep.error(f"{ow}: has multiple targets {targets} (use at most one)")
        if "scene" in opt:
            tgt = opt["scene"]
            if tgt and tgt not in all_ids:
                rep.error(f"{ow}: target scene {tgt!r} does not exist")
        if "check" in opt and not isinstance(opt["check"], dict):
            rep.error(f"{ow}: 'check' must be an object")


def validate_index(index_path: Path, all_ids: set[str], allowlist: set[str],
                   rep: Report) -> None:
    if not index_path.exists():
        rep.error(f"{index_path}: index.json not found")
        return
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        rep.error(f"{index_path}: JSON parse error: {e}")
        return

    indexed: set[str] = set()
    for vol_key, listing in index.items():
        if not isinstance(listing, list):
            rep.error(f"index.json: volume {vol_key!r} is not an array")
            continue
        for sid in listing:
            indexed.add(sid)
            if sid not in all_ids:
                rep.error(f"index.json: vol {vol_key} lists {sid!r} but no file exists")

    drift = sorted(all_ids - indexed - allowlist)
    for sid in drift:
        rep.warn(f"{sid}: file on disk is not in index.json (unreachable via SceneDataDB)")

    known = sorted((all_ids - indexed) & allowlist)
    if known:
        print(f"  note: {len(known)} known-unindexed file(s) "
              f"(stubs/unwired drafts) skipped via allowlist")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Modern Mythology scene data")
    parser.add_argument("--scenes", default=None,
                        help="path to resources/scenes (default: relative to this script)")
    parser.add_argument("--quiet", action="store_true",
                        help="suppress the per-volume summary line")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    scenes_dir = Path(args.scenes).resolve() if args.scenes \
        else (script_dir.parent / "resources" / "scenes")
    if not scenes_dir.is_dir():
        print(f"ERROR: scenes dir not found: {scenes_dir}", file=sys.stderr)
        return 1

    allowlist = load_allowlist(script_dir / "scene_allowlist.txt")
    rep = Report()

    scenes = collect_scenes(scenes_dir, rep)
    all_ids = set(scenes)
    for sid, data in scenes.items():
        validate_nodes(sid, data, all_ids, rep)
    validate_index(scenes_dir / "index.json", all_ids, allowlist, rep)

    if not args.quiet:
        print(f"Validated {len(scenes)} scene file(s) under {scenes_dir}")

    for w in rep.warnings:
        print(f"  WARNING: {w}")
    for e in rep.errors:
        print(f"  ERROR: {e}", file=sys.stderr)

    print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
