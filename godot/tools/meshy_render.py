#!/usr/bin/env python3
"""Generate low-poly 3D models from images via the Meshy Image-to-3D API and
drop the raw GLBs into the project's 3D staging area.

This is the RUNNER (network + download). It is deliberately dumb about the
game's conventions: it fetches raw GLBs into assets/3d/meshy/<tag>/<slug>.glb.
The pipeline-integration half — axis/scale normalization, a flat vertex-color
material for the untextured T2 output, optional decimate, re-export into the
real assets/3d/<category> dir — is a Blender pass:
    godot/tools/blender/build_meshy_import.py
run on the Deck via run_cathedral.sh, like every other build_*.py. Keeping the
two halves separate means this file needs no Blender and runs anywhere.

For each job in the queue JSON:
  - resolve the input image (local path -> data URI, or a public URL)
  - POST it to Meshy's /openapi/v1/image-to-3d create endpoint
  - poll the task until SUCCEEDED / FAILED / CANCELED
  - download model_urls.glb
  - save to assets/3d/meshy/<tag>/<slug>.glb
  - append a manifest entry

Defaults target the new UNTEXTURED, low-poly T2 workflow (should_texture off,
a low target_polycount, triangle topology) so the output slots straight into
the vertex-color / Light3D / screen-space-shader pipeline. Every Meshy request
field is pass-through via a job's "params" object, so the exact model id (e.g.
the T2 model) and any new fields can be set from the queue without touching
this code.

Requirements:
  - MESHY_API_KEY env var, OR a key file at godot/tools/.meshy_key
  - Python 3.9+ (stdlib only — urllib, json, base64, pathlib)

Usage:
  python3 godot/tools/meshy_render.py godot/tools/meshy_queue.json
  python3 godot/tools/meshy_render.py queue.json --dry-run
  python3 godot/tools/meshy_render.py queue.json --limit 2 --only 'props_*'
  python3 godot/tools/meshy_render.py queue.json --overwrite

Queue format: a list, or {"jobs": [...]}. Each job:
  {
    "tag":   "props",                 // groups output under assets/3d/meshy/<tag>/
    "slug":  "diner_stool",           // output filename (slug.glb)
    "image": "art/refs/stool.png",    // local path (repo-relative ok) ...
    "image_url": "https://...",       // ... OR a public URL / data URI
    "params": {                       // pass-through to the Meshy request body
      "ai_model":         "meshy-5",  // set to the T2 model id you're trying
      "should_texture":   false,      // untextured T2 workflow
      "target_polycount": 6000,       // low-poly
      "topology":         "triangle",
      "symmetry_mode":    "auto"
    }
  }
"""

import argparse
import base64
import fnmatch
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # .../godot
TOOLS = REPO / "tools"
MESH_ROOT = REPO / "assets" / "3d" / "meshy"           # raw download staging
MANIFEST_PATH = MESH_ROOT / "manifest.json"
KEY_FILE = TOOLS / ".meshy_key"

MESHY_BASE = "https://api.meshy.ai"
CREATE_PATH = "/openapi/v1/image-to-3d"
TASK_PATH = "/openapi/v1/image-to-3d/{id}"

# Defaults for the untextured, low-poly T2 workflow. Any of these can be
# overridden per-job via "params"; unknown keys pass straight through, so new
# Meshy fields need no code change here.
DEFAULT_PARAMS = {
    "should_texture": False,
    "target_polycount": 6000,
    "topology": "triangle",
}

TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELED", "CANCELLED"}
POLL_INTERVAL = 6.0            # seconds between task polls
POLL_TIMEOUT = 60 * 20        # 20 minutes — image-to-3D can take several
SUBMIT_RETRIES = 4
SUBMIT_BACKOFF = 2.0
MAX_IMAGE_MB = 20

SLUG_RE = re.compile(r"[^a-z0-9._-]+")


# ── Auth ────────────────────────────────────────────────────────────────────

def get_api_key():
    k = os.environ.get("MESHY_API_KEY", "").strip()
    if k:
        return k
    if KEY_FILE.exists():
        k = KEY_FILE.read_text().strip().splitlines()[0].strip()
        if k:
            return k
    sys.exit(
        "Meshy API key not found.\n"
        "  Either:  export MESHY_API_KEY=msy_...\n"
        f"  Or:      echo 'msy_...' > {KEY_FILE.relative_to(REPO.parent)}\n"
        "           (the key file is gitignored.)"
    )


# ── Queue I/O ───────────────────────────────────────────────────────────────

def load_queue(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "jobs" in data:
        jobs = data["jobs"]
    elif isinstance(data, list):
        jobs = data
    else:
        sys.exit(f"queue file must be a list or {{\"jobs\": [...]}}; got {type(data).__name__}")
    if not isinstance(jobs, list):
        sys.exit("queue 'jobs' must be a list")
    return jobs


def load_manifest():
    if MANIFEST_PATH.exists():
        try:
            data = json.loads(MANIFEST_PATH.read_text())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return []


def write_manifest(entries):
    MESH_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(entries, indent=2) + "\n")


# ── Validation ──────────────────────────────────────────────────────────────

def slugify(s):
    s = (s or "").strip().lower().replace(" ", "_")
    s = SLUG_RE.sub("", s)
    return s[:80] or "untitled"


def validate_job(job, index):
    """Raise ValueError on first invalid field. Fills in defaults in place."""
    if not isinstance(job, dict):
        raise ValueError(f"job #{index}: must be an object")
    job.setdefault("tag", "untagged")
    job.setdefault("slug", slugify(f"job_{index:03d}"))
    if not job.get("image") and not job.get("image_url"):
        raise ValueError(
            f"job #{index}: requires either 'image' (local path) or "
            "'image_url' (public URL or data URI)"
        )
    params = job.get("params", {})
    if not isinstance(params, dict):
        raise ValueError(f"job #{index}: 'params' must be an object")
    # Merge defaults under the job's explicit params.
    merged = dict(DEFAULT_PARAMS)
    merged.update(params)
    job["params"] = merged
    return job


# ── Image handling ──────────────────────────────────────────────────────────

def image_to_data_uri(path):
    """Read a local image and return a data URI. Resolves relative paths
    against cwd then the repo so the queue JSON can live anywhere."""
    p = Path(path)
    if not p.is_absolute():
        for c in (Path.cwd() / p, REPO.parent / p, REPO / p):
            if c.exists():
                p = c
                break
    if not p.exists():
        raise FileNotFoundError(f"image not found: {path}")
    mime, _ = mimetypes.guess_type(p.name)
    if mime not in ("image/jpeg", "image/png"):
        # Meshy accepts jpg/jpeg/png. Guess png for unknowns; error on obvious
        # mismatches so we fail before spending credits.
        if mime is None:
            mime = "image/png"
        else:
            raise ValueError(f"{p.name}: Meshy supports jpg/jpeg/png, got {mime}")
    data = p.read_bytes()
    if len(data) > MAX_IMAGE_MB * 1024 * 1024:
        raise ValueError(f"image {p.name} is over {MAX_IMAGE_MB} MB")
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def resolve_image(job):
    if job.get("image_url"):
        return job["image_url"]
    return image_to_data_uri(job["image"])


# ── HTTP ────────────────────────────────────────────────────────────────────

def _request(method, path, body=None, api_key=None, timeout=60):
    url = f"{MESHY_BASE}{path}"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "replace")[:1000]
        except Exception:
            pass
        raise RuntimeError(f"Meshy HTTP {e.code} on {method} {path}: {detail}") from e


def submit_job(job, api_key):
    body = dict(job["params"])          # pass-through: ai_model, polycount, etc.
    body["image_url"] = resolve_image(job)
    delay = SUBMIT_BACKOFF
    last_err = None
    for attempt in range(SUBMIT_RETRIES):
        try:
            resp = _request("POST", CREATE_PATH, body=body, api_key=api_key)
            # Meshy returns {"result": "<task_id>"} on create.
            task_id = resp.get("result") or resp.get("id")
            if not task_id:
                raise RuntimeError(f"submit response missing task id: {resp}")
            return task_id
        except RuntimeError as e:
            msg = str(e)
            last_err = e
            if attempt < SUBMIT_RETRIES - 1 and ("429" in msg or " 50" in msg):
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise last_err  # unreachable


def poll_task(task_id, api_key, timeout=POLL_TIMEOUT):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        resp = _request("GET", TASK_PATH.format(id=task_id), api_key=api_key)
        status = resp.get("status", "UNKNOWN")
        prog = resp.get("progress")
        stamp = status if prog is None else f"{status} ({prog}%)"
        if stamp != last:
            print(f"    status: {stamp}", flush=True)
            last = stamp
        if status in TERMINAL_STATES:
            return resp
        time.sleep(POLL_INTERVAL)
    raise RuntimeError(f"task {task_id} did not finish within {timeout}s")


def model_glb_url(task):
    urls = task.get("model_urls") or task.get("model_url") or {}
    if isinstance(urls, str):
        return urls
    if isinstance(urls, dict):
        return urls.get("glb", "")
    return ""


def download_glb(url, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"Accept": "model/gltf-binary,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            with open(out_path, "wb") as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"download HTTP {e.code}: {e.reason}") from e


# ── Driver ──────────────────────────────────────────────────────────────────

def run_job(job, api_key, overwrite=False):
    out_dir = MESH_ROOT / slugify(job["tag"])
    out_path = out_dir / f"{slugify(job['slug'])}.glb"

    entry = {
        "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tag": job["tag"],
        "slug": job["slug"],
        "params": job["params"],
        "image": job.get("image", "") or job.get("image_url", ""),
        "output_path": str(out_path.relative_to(REPO.parent)),
        "task_id": None,
        "status": "PENDING",
        "error": None,
    }

    if out_path.exists() and not overwrite:
        entry["status"] = "SKIPPED"
        entry["error"] = f"output exists: {out_path.name} (pass --overwrite to redo)"
        return True, entry

    try:
        task_id = submit_job(job, api_key)
        entry["task_id"] = task_id
        print(f"    submitted task: {task_id}", flush=True)
        result = poll_task(task_id, api_key)
        entry["status"] = result.get("status", "UNKNOWN")
        if entry["status"] != "SUCCEEDED":
            entry["error"] = (result.get("task_error") or {}).get("message") \
                or json.dumps(result)[:300]
            return False, entry
        url = model_glb_url(result)
        if not url:
            entry["error"] = "succeeded task had no model_urls.glb"
            return False, entry
        print(f"    downloading: {url[:80]}...", flush=True)
        download_glb(url, out_path)
        size_kb = out_path.stat().st_size / 1024
        entry["file_size_kb"] = round(size_kb, 1)
        print(f"    saved: {out_path.relative_to(REPO.parent)}  ({size_kb:.1f} KB)",
              flush=True)
        return True, entry
    except Exception as e:
        entry["status"] = "ERROR"
        entry["error"] = str(e)[:500]
        return False, entry


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("queue", help="Path to the queue JSON.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate + print what would be submitted; no API calls.")
    ap.add_argument("--only", action="append", default=[],
                    help="Glob filter on job tag or slug. Repeatable.")
    ap.add_argument("--limit", type=int, help="Stop after this many jobs.")
    ap.add_argument("--overwrite", action="store_true",
                    help="Re-render even if the output GLB already exists.")
    args = ap.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        sys.exit(f"queue file not found: {queue_path}")
    jobs = load_queue(queue_path)
    if not jobs:
        sys.exit("queue is empty")

    for i, job in enumerate(jobs):
        try:
            validate_job(job, i)
        except (ValueError, FileNotFoundError) as e:
            sys.exit(f"validation failed: {e}")

    if args.only:
        def matches(job):
            return any(fnmatch.fnmatch(job.get("tag", ""), p)
                       or fnmatch.fnmatch(job.get("slug", ""), p) for p in args.only)
        jobs = [j for j in jobs if matches(j)]
        if not jobs:
            sys.exit(f"no jobs matched --only filters: {args.only}")

    if args.limit is not None:
        jobs = jobs[:args.limit]

    print(f"queue: {len(jobs)} job(s)  (Meshy bills credits per generation — "
          "confirm balance in the dashboard before a large run)", flush=True)

    if args.dry_run:
        for job in jobs:
            p = job["params"]
            print(f"  [DRY] {job['tag']}/{job['slug']}  "
                  f"model={p.get('ai_model', '(account default)')}  "
                  f"poly={p.get('target_polycount')}  "
                  f"textured={p.get('should_texture')}  "
                  f"topo={p.get('topology')}")
        return

    api_key = get_api_key()
    manifest = load_manifest()
    rendered = errored = skipped = 0
    for i, job in enumerate(jobs):
        print(f"\n[{i+1}/{len(jobs)}] {job['tag']}/{job['slug']}", flush=True)
        ok, entry = run_job(job, api_key, overwrite=args.overwrite)
        manifest.append(entry)
        write_manifest(manifest)   # flush per job so Ctrl-C keeps progress
        if entry["status"] == "SKIPPED":
            skipped += 1
        elif ok:
            rendered += 1
        else:
            errored += 1
            print(f"    ERROR: {entry['error']}", file=sys.stderr)

    print(f"\ndone: {rendered} rendered, {skipped} skipped, {errored} errored",
          flush=True)
    sys.exit(1 if errored else 0)


if __name__ == "__main__":
    main()
