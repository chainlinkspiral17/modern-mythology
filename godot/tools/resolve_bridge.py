#!/usr/bin/env python3
"""Wire RunwayML output (or any local clips) into DaVinci Resolve.

The bridge speaks to a running Resolve via its scripting API, ingests
clips into a project organized by volume, sets metadata, and lays out
a timeline in manifest order. It stops short of rendering — render in
the app, because that's a Studio feature and you haven't committed
yet.

The HTML companion (resolve_studio.html) composes actions; this
script executes them. They communicate via the action JSON format
documented in resolve_actions.example.json.

A typical end-to-end flow:

  # ─ open Resolve.  it has to be running for the API to attach ─
  /opt/resolve/bin/resolve &

  # ─ build an action list in the studio HTML, export it ─
  # ─ then run it:
  python3 godot/tools/resolve_bridge.py resolve_actions.json

  # ─ or skip the HTML and bind a Runway manifest directly ─
  python3 godot/tools/resolve_bridge.py \\
      --from-runway-manifest godot/assets/video/generated/manifest.json \\
      --volume vol5 \\
      --timeline 'Runway batch 2025-06-05'

Requirements:
  - DaVinci Resolve (Studio or Free) running, at default /opt/resolve
    install or with RESOLVE_SCRIPT_API + RESOLVE_SCRIPT_LIB +
    PYTHONPATH set to the Developer/Scripting paths
  - Python 3.9+
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Volume → project naming ────────────────────────────────────────────────

VOLUME_PROJECTS = {
    "vol5": "MM_vol5_major_arcana",
    "vol6": "MM_vol6_planned_community",
    "vol7": "MM_vol7_milk_and_honey",
    "whispers": "MM_vol5_major_arcana",      # whispers material lives in vol5
    "pomegranate": "MM_vol5_major_arcana",   # pomegranate material lives in vol5
    "marketing": "MM_marketing",
    "scratch": "MM_scratch",
    "untagged": "MM_scratch",
}

# Default Linux Resolve install — the script auto-bootstraps these env
# vars if they aren't already set, so you don't need a shell profile entry.
LINUX_DEFAULTS = {
    "RESOLVE_SCRIPT_API": "/opt/resolve/Developer/Scripting",
    "RESOLVE_SCRIPT_LIB": "/opt/resolve/libs/Fusion/fusionscript.so",
}

REPO = Path(__file__).resolve().parent.parent
DEFAULT_RUNWAY_MANIFEST = REPO / "assets" / "video" / "generated" / "manifest.json"


# ── Resolve connection ─────────────────────────────────────────────────────

def bootstrap_env():
    """Set RESOLVE_SCRIPT_API, RESOLVE_SCRIPT_LIB, and extend PYTHONPATH so
    `import DaVinciResolveScript` works on a vanilla shell. No-op if the
    user has already set the vars."""
    for key, default in LINUX_DEFAULTS.items():
        if not os.environ.get(key):
            if Path(default).exists():
                os.environ[key] = default
            else:
                sys.exit(
                    f"{key} is not set and the default ({default}) does not exist.\n"
                    "Set the env vars manually or install Resolve at /opt/resolve.\n"
                    "  export RESOLVE_SCRIPT_API=/path/to/Developer/Scripting\n"
                    "  export RESOLVE_SCRIPT_LIB=/path/to/Fusion/fusionscript.so"
                )

    modules_dir = Path(os.environ["RESOLVE_SCRIPT_API"]) / "Modules"
    if str(modules_dir) not in sys.path:
        sys.path.insert(0, str(modules_dir))


def connect_resolve():
    """Return the live Resolve scripting handle. Errors with guidance if
    Resolve isn't running."""
    bootstrap_env()
    try:
        import DaVinciResolveScript as dvr  # type: ignore
    except ImportError as e:
        sys.exit(
            f"could not import DaVinciResolveScript: {e}\n"
            "  Modules dir: " + str(Path(os.environ['RESOLVE_SCRIPT_API']) / 'Modules') + "\n"
            "  Confirm RESOLVE_SCRIPT_API points at .../Developer/Scripting/"
        )
    resolve = dvr.scriptapp("Resolve")
    if resolve is None:
        sys.exit(
            "Resolve is not running, or its scripting server is disabled.\n"
            "  - Start Resolve.\n"
            "  - In Preferences → System → General, enable\n"
            "    'External scripting using: Local'."
        )
    return resolve


# ── Project + bin helpers ──────────────────────────────────────────────────

def ensure_project(resolve, project_name):
    """Switch to project_name, creating it if missing. Returns the project."""
    pm = resolve.GetProjectManager()
    current = pm.GetCurrentProject()
    if current and current.GetName() == project_name:
        return current
    # Try to load
    if pm.LoadProject(project_name):
        return pm.GetCurrentProject()
    # Create
    project = pm.CreateProject(project_name)
    if not project:
        sys.exit(f"could not create or load project {project_name!r}")
    return project


def find_or_create_bin(media_pool, path_parts):
    """Walk path_parts under the root folder, creating subfolders as needed.
    path_parts: list of bin names from root downward, e.g. ['Runway', 'vol5']."""
    folder = media_pool.GetRootFolder()
    for name in path_parts:
        children = folder.GetSubFolderList() or []
        match = next((c for c in children if c.GetName() == name), None)
        if match is None:
            match = media_pool.AddSubFolder(folder, name)
            if match is None:
                sys.exit(f"could not create bin {'/'.join(path_parts)}")
        folder = match
    return folder


def select_bin(media_pool, bin_path):
    """Set the current Media Pool folder to bin_path (string with '/'). Creates
    intermediate folders if missing. Returns the folder."""
    parts = [p for p in bin_path.split("/") if p]
    folder = find_or_create_bin(media_pool, parts)
    media_pool.SetCurrentFolder(folder)
    return folder


def find_clip_by_filename(folder, filename):
    """Walk the bin tree under folder. Return first clip with matching file name."""
    target = Path(filename).name
    stack = [folder]
    while stack:
        f = stack.pop()
        for clip in f.GetClipList() or []:
            cp = clip.GetClipProperty("File Path") or ""
            if Path(cp).name == target:
                return clip
            if clip.GetName() == target:
                return clip
        for sub in f.GetSubFolderList() or []:
            stack.append(sub)
    return None


# ── Runway manifest ingest ─────────────────────────────────────────────────

def load_runway_manifest(path):
    path = Path(path)
    if not path.exists():
        sys.exit(f"manifest not found: {path}")
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit("manifest must be a JSON array of entries")
    return data, path


def runway_entries_to_import(manifest, only_status=("SUCCEEDED",)):
    """Yield (entry, absolute_path) tuples for entries whose output file
    exists on disk and whose status matches."""
    for entry in manifest:
        if entry.get("status") not in only_status:
            continue
        rel = entry.get("output_path")
        if not rel:
            continue
        # output_path is relative to REPO.parent (i.e. the workspace root)
        abs_path = (REPO.parent / rel).resolve()
        if not abs_path.exists():
            continue
        yield entry, abs_path


# ── Actions ────────────────────────────────────────────────────────────────

def act_ensure_project(resolve, args):
    project_name = args["project"]
    project = ensure_project(resolve, project_name)
    return {
        "project": project.GetName(),
        "timelines": project.GetTimelineCount(),
    }


def act_import_files(resolve, args):
    """args: { project, bin, files: [paths], metadata: { description, keywords } }"""
    project = ensure_project(resolve, args["project"])
    media_pool = project.GetMediaPool()
    folder = select_bin(media_pool, args.get("bin", "Imports"))

    file_paths = [str(Path(p).resolve()) for p in args["files"]]
    file_paths = [p for p in file_paths if Path(p).exists()]
    if not file_paths:
        return {"imported": 0, "skipped": len(args["files"]), "warning": "no files exist"}

    items = media_pool.ImportMedia(file_paths) or []
    metadata = args.get("metadata") or {}
    for it in items:
        if metadata.get("description"):
            it.SetClipProperty("Description", metadata["description"])
        if metadata.get("keywords"):
            it.SetClipProperty("Keywords", ",".join(metadata["keywords"]))
    return {"imported": len(items), "bin": args.get("bin", "Imports")}


def act_import_from_runway_manifest(resolve, args):
    """args: { project, manifest, bin_prefix, status_filter }"""
    project = ensure_project(resolve, args["project"])
    media_pool = project.GetMediaPool()
    manifest, manifest_path = load_runway_manifest(args["manifest"])
    bin_prefix = args.get("bin_prefix", "Runway")
    status_filter = tuple(args.get("status_filter") or ["SUCCEEDED"])

    grouped = {}  # tag -> list[(entry, abs_path)]
    for entry, abs_path in runway_entries_to_import(manifest, only_status=status_filter):
        grouped.setdefault(entry.get("tag", "untagged"), []).append((entry, abs_path))

    total_imported = 0
    imported_by_bin = {}
    for tag, items in sorted(grouped.items()):
        bin_path = f"{bin_prefix}/{tag}"
        folder = select_bin(media_pool, bin_path)
        file_paths = [str(p) for _, p in items]
        pool_items = media_pool.ImportMedia(file_paths) or []
        # Attach metadata per clip
        for clip, (entry, _) in zip(pool_items, items):
            if entry.get("prompt_text"):
                clip.SetClipProperty("Description", entry["prompt_text"])
            kw = []
            if entry.get("model"): kw.append(entry["model"])
            if entry.get("seed") is not None: kw.append(f"seed-{entry['seed']}")
            kw.append(f"tag-{entry.get('tag','untagged')}")
            kw.append("runway")
            clip.SetClipProperty("Keywords", ",".join(kw))
        total_imported += len(pool_items)
        imported_by_bin[bin_path] = len(pool_items)

    return {
        "manifest": str(manifest_path.relative_to(REPO.parent)),
        "imported": total_imported,
        "by_bin": imported_by_bin,
    }


def act_timeline_from_manifest(resolve, args):
    """args: { project, manifest, name, framerate, status_filter, order, tag_filter }
    order: 'manifest' (default) or 'submitted_at'.
    tag_filter: optional list of tags to include; default is all."""
    project = ensure_project(resolve, args["project"])
    media_pool = project.GetMediaPool()
    manifest, _ = load_runway_manifest(args["manifest"])
    name = args.get("name") or default_timeline_name()
    framerate = args.get("framerate", 24)
    status_filter = tuple(args.get("status_filter") or ["SUCCEEDED"])
    order = args.get("order", "manifest")
    tag_filter = args.get("tag_filter")

    project.SetSetting("timelineFrameRate", str(framerate))

    entries = [
        e for e, _ in runway_entries_to_import(manifest, only_status=status_filter)
        if not tag_filter or e.get("tag") in tag_filter
    ]
    if order == "submitted_at":
        entries.sort(key=lambda e: e.get("submitted_at", ""))

    if not entries:
        return {"created": False, "reason": "no entries matched"}

    # Find the imported clips. If they aren't in the project yet, import them
    # first into the per-tag bins.
    root = media_pool.GetRootFolder()
    runway_folder = next(
        (f for f in root.GetSubFolderList() or [] if f.GetName() == "Runway"),
        None,
    )
    if runway_folder is None:
        # Auto-import what we need
        act_import_from_runway_manifest(resolve, {
            "project": args["project"],
            "manifest": args["manifest"],
            "status_filter": status_filter,
        })
        runway_folder = next(
            (f for f in media_pool.GetRootFolder().GetSubFolderList() or [] if f.GetName() == "Runway"),
            None,
        )

    clips_to_place = []
    for entry in entries:
        fname = Path(entry["output_path"]).name
        clip = find_clip_by_filename(media_pool.GetRootFolder(), fname)
        if clip is None:
            continue
        clips_to_place.append(clip)

    if not clips_to_place:
        return {"created": False, "reason": "no clips matched in project"}

    timeline = media_pool.CreateEmptyTimeline(name)
    if timeline is None:
        return {"created": False, "reason": f"could not create timeline {name!r}"}
    media_pool.AppendToTimeline(clips_to_place)
    return {"created": True, "timeline": name, "clips": len(clips_to_place)}


def act_set_metadata(resolve, args):
    """args: { project, clip, description?, keywords?, notes? }"""
    project = ensure_project(resolve, args["project"])
    media_pool = project.GetMediaPool()
    clip = find_clip_by_filename(media_pool.GetRootFolder(), args["clip"])
    if clip is None:
        return {"updated": False, "reason": f"clip not found: {args['clip']}"}
    if "description" in args:
        clip.SetClipProperty("Description", args["description"])
    if "keywords" in args:
        kw = args["keywords"]
        clip.SetClipProperty("Keywords", ",".join(kw) if isinstance(kw, list) else str(kw))
    if "notes" in args:
        # Resolve uses 'Comments' as the free-text field
        clip.SetClipProperty("Comments", args["notes"])
    return {"updated": True, "clip": args["clip"]}


def act_sync_metadata_out(resolve, args):
    """Pull markers + ratings + Comments back into the manifest. Updates the
    manifest file on disk. args: { project, manifest, output? }."""
    project = ensure_project(resolve, args["project"])
    media_pool = project.GetMediaPool()
    manifest_path = Path(args["manifest"])
    manifest, _ = load_runway_manifest(manifest_path)

    updated = 0
    for entry in manifest:
        rel = entry.get("output_path")
        if not rel:
            continue
        fname = Path(rel).name
        clip = find_clip_by_filename(media_pool.GetRootFolder(), fname)
        if clip is None:
            continue
        markers = clip.GetMarkers() or {}
        comments = clip.GetClipProperty("Comments") or ""
        flags = clip.GetClipColor() or ""
        # Stash under a 'resolve' subkey so manifest stays clean
        entry["resolve"] = {
            "markers": markers,
            "comments": comments,
            "flag_color": flags,
            "synced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        updated += 1

    out = Path(args.get("output") or manifest_path)
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    return {"synced": updated, "manifest": str(out.relative_to(REPO.parent))}


ACTIONS = {
    "ensure_project": act_ensure_project,
    "import_files": act_import_files,
    "import_from_runway_manifest": act_import_from_runway_manifest,
    "timeline_from_manifest": act_timeline_from_manifest,
    "set_metadata": act_set_metadata,
    "sync_metadata_out": act_sync_metadata_out,
}


# ── Helpers ────────────────────────────────────────────────────────────────

def default_timeline_name():
    today = datetime.now().strftime("%Y-%m-%d")
    return f"Runway batch {today}"


def load_actions(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "actions" in data:
        return data["actions"]
    if isinstance(data, list):
        return data
    sys.exit("action file must be a list or {\"actions\": [...]}")


def execute(resolve, actions, dry_run=False):
    for i, act in enumerate(actions, start=1):
        kind = act.get("action")
        if kind not in ACTIONS:
            print(f"[{i}] unknown action {kind!r}; valid: {sorted(ACTIONS)}", file=sys.stderr)
            continue
        label = f"[{i}/{len(actions)}] {kind}"
        if dry_run:
            print(f"  [DRY] {label}  {summarize(act)}")
            continue
        print(f"  → {label}  {summarize(act)}", flush=True)
        try:
            result = ACTIONS[kind](resolve, act)
            print(f"    ok: {result}", flush=True)
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)


def summarize(act):
    """Tight one-line representation of an action for stdout."""
    kind = act.get("action", "?")
    if kind == "ensure_project":
        return f"project={act.get('project')}"
    if kind == "import_from_runway_manifest":
        return f"manifest={act.get('manifest')} → {act.get('project')}"
    if kind == "timeline_from_manifest":
        return f"timeline={act.get('name') or default_timeline_name()} @ {act.get('framerate', 24)} fps"
    if kind == "import_files":
        files = act.get("files") or []
        return f"{len(files)} file(s) → {act.get('bin','Imports')}"
    if kind == "set_metadata":
        return f"clip={act.get('clip')}"
    if kind == "sync_metadata_out":
        return f"manifest={act.get('manifest')}"
    return ""


# ── Direct manifest shortcut ───────────────────────────────────────────────

def build_actions_from_manifest_args(args):
    """Convenience: --from-runway-manifest builds a sensible action list
    without requiring the user to write JSON."""
    project = VOLUME_PROJECTS.get(args.volume) if args.volume else None
    if project is None and args.volume:
        sys.exit(f"unknown --volume {args.volume!r}; "
                 f"known: {sorted(VOLUME_PROJECTS)}")
    if project is None:
        project = VOLUME_PROJECTS["scratch"]

    actions = [
        {"action": "ensure_project", "project": project},
        {
            "action": "import_from_runway_manifest",
            "project": project,
            "manifest": str(args.from_runway_manifest),
            "bin_prefix": "Runway",
        },
    ]
    if args.timeline is not False:
        timeline_name = args.timeline or default_timeline_name()
        actions.append({
            "action": "timeline_from_manifest",
            "project": project,
            "manifest": str(args.from_runway_manifest),
            "name": timeline_name,
            "framerate": args.framerate,
        })
    return actions


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "actions",
        nargs="?",
        help="Path to the action JSON (from resolve_studio.html). Omit if "
             "you're using --from-runway-manifest.",
    )
    ap.add_argument(
        "--from-runway-manifest",
        type=Path,
        help="Skip the action JSON and import a Runway manifest directly. "
             "Uses --volume to pick the project.",
    )
    ap.add_argument(
        "--volume",
        choices=sorted(VOLUME_PROJECTS),
        default="vol5",
        help="Which volume project to import into. Default: vol5.",
    )
    ap.add_argument(
        "--timeline",
        nargs="?",
        const=None,
        default=False,
        help="Build a timeline as part of the import. Pass a name or leave "
             "blank to auto-name. Omit the flag to skip timeline creation.",
    )
    ap.add_argument(
        "--framerate",
        type=int,
        default=24,
        help="Timeline framerate (default 24).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the action list without connecting to Resolve.",
    )
    args = ap.parse_args()

    if not args.actions and not args.from_runway_manifest:
        ap.error("Provide an action JSON path or use --from-runway-manifest.")

    if args.from_runway_manifest:
        actions = build_actions_from_manifest_args(args)
        if not args.from_runway_manifest.exists():
            sys.exit(f"manifest not found: {args.from_runway_manifest}")
    else:
        actions = load_actions(args.actions)

    print(f"actions: {len(actions)}")
    if args.dry_run:
        for i, act in enumerate(actions, start=1):
            print(f"  [DRY] [{i}] {act.get('action')}  {summarize(act)}")
        return

    resolve = connect_resolve()
    print(f"connected: {resolve.GetProductName()} {resolve.GetVersionString()}")
    execute(resolve, actions, dry_run=False)


if __name__ == "__main__":
    main()
