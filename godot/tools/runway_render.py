#!/usr/bin/env python3
"""Render video clips via RunwayML's dev API and drop them where the rest
of the project expects them.

For each job in the queue JSON:
  - read the source image (local path or URL)
  - POST it to RunwayML's image_to_video endpoint
  - poll the task until it completes or fails
  - download the resulting MP4
  - save to assets/video/generated/<tag>/<slug>.mp4
  - append a manifest entry

The HTML companion (runway_studio.html) is the queue builder. This script
is the runner. They communicate via the queue JSON format documented in
runway_queue.example.json.

Requirements:
  - RUNWAYML_API_KEY env var, OR a key file at godot/tools/.runway_key
  - Python 3.9+ (uses stdlib only — urllib, json, base64, pathlib)

Usage:
  python3 godot/tools/runway_render.py godot/tools/runway_queue.json
  python3 godot/tools/runway_render.py queue.json --dry-run
  python3 godot/tools/runway_render.py queue.json --limit 2
  python3 godot/tools/runway_render.py queue.json --only "vol6_*"
  python3 godot/tools/runway_render.py queue.json --overwrite
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

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
VIDEO_ROOT = REPO / "assets" / "video" / "generated"
MANIFEST_PATH = VIDEO_ROOT / "manifest.json"
KEY_FILE = TOOLS / ".runway_key"

RUNWAY_BASE = "https://api.dev.runwayml.com/v1"
RUNWAY_API_VERSION = "2024-11-06"

DEFAULT_MODEL = "gen3a_turbo"
SUPPORTED_MODELS = {"gen3a_turbo", "gen4_turbo"}
SUPPORTED_DURATIONS = {5, 10}
SUPPORTED_RATIOS = {
    "1280:720", "720:1280",
    "1104:832", "832:1104",
    "960:960",
    "1584:672",
}
TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELLED"}
POLL_INTERVAL = 5.0           # seconds between task polls
POLL_TIMEOUT = 60 * 12        # 12 minutes — Turbo usually finishes in under 3
SUBMIT_RETRIES = 4
SUBMIT_BACKOFF = 2.0

SLUG_RE = re.compile(r"[^a-z0-9._-]+")


# ── Auth ────────────────────────────────────────────────────────────────────

def get_api_key():
    """Return the API key from RUNWAYML_API_KEY env var, falling back to
    a key file at godot/tools/.runway_key. Errors out with guidance."""
    k = os.environ.get("RUNWAYML_API_KEY", "").strip()
    if k:
        return k
    if KEY_FILE.exists():
        k = KEY_FILE.read_text().strip().splitlines()[0].strip()
        if k:
            return k
    sys.exit(
        "RunwayML API key not found.\n"
        "  Either:  export RUNWAYML_API_KEY=key_...\n"
        f"  Or:      echo 'key_...' > {KEY_FILE.relative_to(REPO.parent)}\n"
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
    VIDEO_ROOT.mkdir(parents=True, exist_ok=True)
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
    job.setdefault("model", DEFAULT_MODEL)
    job.setdefault("duration", 5)
    job.setdefault("ratio", "1280:720")
    job.setdefault("tag", "untagged")
    job.setdefault("slug", slugify(job.get("prompt_text") or f"job_{index:03d}"))
    if job["model"] not in SUPPORTED_MODELS:
        raise ValueError(
            f"job #{index}: model {job['model']!r} not in {sorted(SUPPORTED_MODELS)}"
        )
    if job["duration"] not in SUPPORTED_DURATIONS:
        raise ValueError(
            f"job #{index}: duration {job['duration']!r} not in {sorted(SUPPORTED_DURATIONS)}"
        )
    if job["ratio"] not in SUPPORTED_RATIOS:
        raise ValueError(
            f"job #{index}: ratio {job['ratio']!r} not in {sorted(SUPPORTED_RATIOS)}"
        )
    if not job.get("source_image") and not job.get("prompt_image"):
        raise ValueError(
            f"job #{index}: requires either 'source_image' (local path) or "
            "'prompt_image' (URL or data URI)"
        )
    return job


# ── Image handling ──────────────────────────────────────────────────────────

def image_to_data_uri(path):
    """Read a local image and return a data URI string. Resolves relative
    paths against the repo root so the queue JSON can live anywhere."""
    p = Path(path)
    if not p.is_absolute():
        # try relative to cwd, then relative to repo
        candidates = [Path.cwd() / p, REPO.parent / p, REPO / p]
        for c in candidates:
            if c.exists():
                p = c
                break
    if not p.exists():
        raise FileNotFoundError(f"source_image not found: {path}")
    mime, _ = mimetypes.guess_type(p.name)
    if mime is None:
        mime = "image/png"
    data = p.read_bytes()
    if len(data) > 16 * 1024 * 1024:
        raise ValueError(
            f"source_image {p.name} is {len(data)//1024//1024} MB; "
            "RunwayML limit is 16 MB before base64 encoding"
        )
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def resolve_prompt_image(job):
    """Return the value to pass as `promptImage` to the API.
    Accepts a local path in 'source_image' or a URL/data URI in 'prompt_image'."""
    if job.get("prompt_image"):
        return job["prompt_image"]
    return image_to_data_uri(job["source_image"])


# ── HTTP ────────────────────────────────────────────────────────────────────

def _request(method, path, body=None, api_key=None, timeout=60):
    url = f"{RUNWAY_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Runway-Version": RUNWAY_API_VERSION,
        "Accept": "application/json",
    }
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
        raise RuntimeError(f"Runway HTTP {e.code} on {method} {path}: {detail}") from e


def submit_job(job, api_key):
    body = {
        "promptImage": resolve_prompt_image(job),
        "model": job["model"],
        "ratio": job["ratio"],
        "duration": job["duration"],
    }
    if job.get("prompt_text"):
        body["promptText"] = job["prompt_text"]
    if job.get("seed") is not None:
        body["seed"] = int(job["seed"])

    # Retry on 429/5xx
    delay = SUBMIT_BACKOFF
    last_err = None
    for attempt in range(SUBMIT_RETRIES):
        try:
            resp = _request("POST", "/image_to_video", body=body, api_key=api_key)
            task_id = resp.get("id")
            if not task_id:
                raise RuntimeError(f"submit response missing id: {resp}")
            return task_id
        except RuntimeError as e:
            msg = str(e)
            last_err = e
            if attempt < SUBMIT_RETRIES - 1 and ("429" in msg or "50" in msg[:30]):
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise last_err  # unreachable


def poll_task(task_id, api_key, timeout=POLL_TIMEOUT):
    """Block until the task is in a terminal state. Return the final task dict."""
    deadline = time.time() + timeout
    last_status = None
    while time.time() < deadline:
        resp = _request("GET", f"/tasks/{task_id}", api_key=api_key)
        status = resp.get("status", "UNKNOWN")
        if status != last_status:
            print(f"    status: {status}", flush=True)
            last_status = status
        if status in TERMINAL_STATES:
            return resp
        time.sleep(POLL_INTERVAL)
    raise RuntimeError(f"task {task_id} did not finish within {timeout}s")


def download_video(url, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"Accept": "video/mp4"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            with open(out_path, "wb") as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"download HTTP {e.code}: {e.reason}") from e


# ── Cost estimate ───────────────────────────────────────────────────────────

# Approximate published credit costs as of late 2024 (in USD). These are
# rough — Runway adjusts them; the queue's cost estimate is for planning, not
# billing. Confirm in the dashboard before a large run.
COST_PER_SEC = {
    "gen3a_turbo": 0.05,
    "gen4_turbo":  0.10,
}

def estimate_cost(job):
    rate = COST_PER_SEC.get(job["model"], 0.05)
    return rate * float(job["duration"])


# ── Driver ──────────────────────────────────────────────────────────────────

def run_job(job, api_key, overwrite=False):
    """Run a single job. Returns (success: bool, manifest_entry: dict)."""
    out_dir = VIDEO_ROOT / slugify(job["tag"])
    out_path = out_dir / f"{slugify(job['slug'])}.mp4"

    entry = {
        "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tag": job["tag"],
        "slug": job["slug"],
        "model": job["model"],
        "ratio": job["ratio"],
        "duration": job["duration"],
        "seed": job.get("seed"),
        "prompt_text": job.get("prompt_text", ""),
        "source_image": job.get("source_image", ""),
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
            entry["error"] = result.get("failure") or json.dumps(result)[:300]
            return False, entry
        urls = result.get("output") or []
        if not urls:
            entry["error"] = "no output URLs in succeeded task"
            return False, entry
        print(f"    downloading: {urls[0]}", flush=True)
        download_video(urls[0], out_path)
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
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("queue", help="Path to the queue JSON (from runway_studio.html).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate the queue and print what would be submitted, "
                         "without calling the API or spending credits.")
    ap.add_argument("--only", action="append", default=[],
                    help="Glob filter on job tag or slug. Repeatable. "
                         "E.g. --only 'vol6_*' --only 'whispers_*'.")
    ap.add_argument("--limit", type=int,
                    help="Stop after this many submitted jobs.")
    ap.add_argument("--overwrite", action="store_true",
                    help="Re-render even if the output mp4 already exists.")
    args = ap.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        sys.exit(f"queue file not found: {queue_path}")
    jobs = load_queue(queue_path)
    if not jobs:
        sys.exit("queue is empty")

    # Validate up front. If any job is malformed, refuse to spend money.
    for i, job in enumerate(jobs):
        try:
            validate_job(job, i)
        except (ValueError, FileNotFoundError) as e:
            sys.exit(f"validation failed: {e}")

    # Apply --only filter
    if args.only:
        def matches(job):
            tag = job.get("tag", "")
            slug = job.get("slug", "")
            return any(fnmatch.fnmatch(tag, p) or fnmatch.fnmatch(slug, p)
                       for p in args.only)
        jobs = [j for j in jobs if matches(j)]
        if not jobs:
            sys.exit(f"no jobs matched --only filters: {args.only}")

    # Cost rollup
    total_cost = sum(estimate_cost(j) for j in jobs)
    print(f"queue: {len(jobs)} job(s)  ~${total_cost:.2f} estimated", flush=True)

    if args.dry_run:
        for i, job in enumerate(jobs):
            print(f"  [DRY] {job['tag']}/{job['slug']}  "
                  f"{job['model']}  {job['duration']}s  {job['ratio']}  "
                  f"~${estimate_cost(job):.2f}")
            if job.get("prompt_text"):
                preview = job["prompt_text"][:80].replace("\n", " ")
                print(f"         prompt: {preview!r}")
        return

    api_key = get_api_key()
    manifest = load_manifest()

    rendered = errored = skipped = 0
    for i, job in enumerate(jobs):
        tag = f"{job['tag']}/{job['slug']}"
        print(f"\n[{i+1}/{len(jobs)}] {tag}  {job['model']}  "
              f"{job['duration']}s  {job['ratio']}", flush=True)
        ok, entry = run_job(job, api_key, overwrite=args.overwrite)
        manifest.append(entry)
        write_manifest(manifest)  # flush after each job so a Ctrl-C doesn't lose progress

        if entry["status"] == "SKIPPED":
            skipped += 1
        elif ok:
            rendered += 1
        else:
            errored += 1
            print(f"    ERROR: {entry['error']}", file=sys.stderr)

        if args.limit and rendered >= args.limit:
            print(f"\nhit --limit {args.limit}, stopping", file=sys.stderr)
            break

    print(
        f"\nsummary: queued={len(jobs)} rendered={rendered} "
        f"skipped={skipped} errors={errored}",
        file=sys.stderr,
    )
    print(f"manifest: {MANIFEST_PATH.relative_to(REPO.parent)}", file=sys.stderr)


if __name__ == "__main__":
    main()
