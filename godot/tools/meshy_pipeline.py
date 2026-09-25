#!/usr/bin/env python3
"""Concept image → Meshy 3D pipeline for the VN cast and hero props.

Two stages per roster entry, run together or separately:

  image   Generate concept art from the roster prompt with Google
          (Gemini image models / Imagen) or Runway (gen4_image and the
          other text_to_image models). Optionally also a side + back
          view (multi-view) using the front image as a reference.
          Candidates land in  assets/concept/meshy/<slug>/ ; the chosen
          front view is copied to  <slug>/front.png .

  mesh    Send front.png (or front + side + back) to Meshy image-to-3d
          (multi-image-to-3d when several views exist), poll, download
          the GLB straight to the canonical path the game already
          expects:
              hero  → assets/3d/characters/heroes/<file>
              demon → assets/3d/characters/demons/<file>
              prop  → assets/3d/props/<file>

The roster (tools/meshy_roster.json) is the single source of truth for
who/what exists, the prompts, and the canonical filenames.  The HTML
front-end (tools/hero_uploader/index.html) is a viewer/queue builder on
top of this script; run `serve` to drive everything from the browser.

Requirements (stdlib only — urllib, json, base64, http.server):
  - MESHY_API_KEY       or  tools/.meshy_key      (msy_...)
  - GOOGLE_API_KEY      or  tools/.google_key     (AIza...)  [Google provider]
  - RUNWAYML_API_KEY    or  tools/.runway_key     (key_...)  [Runway provider]
  Key files are gitignored.  Only the providers you use need a key.

Usage:
  python3 godot/tools/meshy_pipeline.py list                     # roster + status
  python3 godot/tools/meshy_pipeline.py list --kind prop
  python3 godot/tools/meshy_pipeline.py image frasier_temple --provider google
  python3 godot/tools/meshy_pipeline.py image 'vol6_*' --provider runway --count 2
  python3 godot/tools/meshy_pipeline.py image frasier_temple --multiview
  python3 godot/tools/meshy_pipeline.py pick frasier_temple frasier_temple_google_gemini-2.5-flash-image_01.png
  python3 godot/tools/meshy_pipeline.py mesh frasier_temple --texture
  python3 godot/tools/meshy_pipeline.py run all --provider google --texture --dry-run
  python3 godot/tools/meshy_pipeline.py serve                    # http://127.0.0.1:8765/hero_uploader/

Selectors are roster slugs, globs on slug, `vol5`/`vol6`/`vol7`,
`hero`/`demon`/`prop`, or `all`.
"""

import argparse
import base64
import fnmatch
import json
import mimetypes
import os
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # godot/
TOOLS = REPO / "tools"
ROSTER_PATH = TOOLS / "meshy_roster.json"
CONCEPT_ROOT = REPO / "assets" / "concept" / "meshy"
MANIFEST_PATH = CONCEPT_ROOT / "manifest.json"
CHAR_ROOT = REPO / "assets" / "3d" / "characters"
OUT_DIRS = {
    "hero": CHAR_ROOT / "heroes",
    "demon": CHAR_ROOT / "demons",
    "prop": REPO / "assets" / "3d" / "props",
}
KEY_FILES = {
    "google": TOOLS / ".google_key",
    "runway": TOOLS / ".runway_key",
    "meshy": TOOLS / ".meshy_key",
}
KEY_ENVS = {
    "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "runway": ["RUNWAYML_API_KEY"],
    "meshy": ["MESHY_API_KEY"],
}

VIEWS = ("front", "side", "back")
SLUG_RE = re.compile(r"[^a-z0-9._-]+")

# ── Google (Gemini API) ─────────────────────────────────────────────────────
GOOGLE_BASE = "https://generativelanguage.googleapis.com/v1beta"
# family: "gemini" → models/<m>:generateContent (accepts reference images)
#         "imagen" → models/<m>:predict          (text only, no references)
GOOGLE_MODELS = {
    "gemini-2.5-flash-image":        "gemini",
    "gemini-3.1-flash-image":        "gemini",
    "gemini-3-pro-image-preview":    "gemini",
    "imagen-4.0-generate-001":       "imagen",
    "imagen-4.0-fast-generate-001":  "imagen",
    "imagen-4.0-ultra-generate-001": "imagen",
}
GOOGLE_DEFAULT_MODEL = "gemini-2.5-flash-image"
GOOGLE_ASPECTS = {"1:1", "3:4", "4:3", "9:16", "16:9", "2:3", "3:2", "4:5", "5:4", "21:9"}

# ── Runway (dev API) ────────────────────────────────────────────────────────
RUNWAY_BASE = "https://api.dev.runwayml.com/v1"
RUNWAY_API_VERSION = "2024-11-06"
# family decides which `ratio` strings the model accepts.
RUNWAY_MODELS = {
    "gen4_image":            "gen4",
    "gen4_image_turbo":      "gen4",     # requires 1-3 reference images
    "gemini_2.5_flash":      "gemini",
    "gemini_image3.1_flash": "gemini",
    "gemini_image3_pro":     "gemini",
    "gpt_image_2":           "gpt",
    "seedream5_pro":         "seedream",
    "seedream5_lite":        "seedream",
}
RUNWAY_DEFAULT_MODEL = "gen4_image"
# aspect (roster) → ratio (Runway) per family
RUNWAY_RATIOS = {
    "gen4":     {"1:1": "1024:1024", "3:4": "1080:1440", "4:3": "1440:1080",
                 "9:16": "1080:1920", "16:9": "1920:1080"},
    "gemini":   {"1:1": "1024:1024", "3:4": "896:1152", "4:3": "1152:896",
                 "9:16": "768:1344", "16:9": "1344:768", "2:3": "832:1248",
                 "3:2": "1248:832"},
    "gpt":      {"1:1": "1920:1920", "3:4": "1440:1920", "4:3": "1920:1440",
                 "9:16": "1088:1920", "16:9": "1920:1088"},
    "seedream": {"1:1": "1024:1024", "3:4": "1080:1440", "4:3": "1440:1080",
                 "9:16": "1080:1920", "16:9": "1920:1080"},
}
RUNWAY_REF_TAG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,15}$")

# ── Meshy (OpenAPI v1) ──────────────────────────────────────────────────────
MESHY_BASE = "https://api.meshy.ai/openapi/v1"
MESHY_MODEL_TYPES = {"standard", "smart-topology"}
MESHY_TEXTURE_RES = {"2k", "4k", "8k"}
MESHY_POSES = {"a-pose", "t-pose"}
MESHY_TEST_KEY = "msy_dummy_api_key_for_test_mode_12345678"

TERMINAL_MESHY = {"SUCCEEDED", "FAILED", "CANCELED", "CANCELLED", "EXPIRED"}
TERMINAL_RUNWAY = {"SUCCEEDED", "FAILED", "CANCELLED"}

POLL_INTERVAL_IMAGE = 4.0
POLL_INTERVAL_MESH = 10.0
POLL_TIMEOUT_IMAGE = 60 * 8
POLL_TIMEOUT_MESH = 60 * 45          # textured image-to-3d can take a while
SUBMIT_RETRIES = 4
SUBMIT_BACKOFF = 2.0
MAX_REF_BYTES = 5 * 1024 * 1024      # Runway data-URI reference cap

# Rough planning numbers only (USD). Vendors move these; check dashboards
# before a big run.
COST_HINTS = {
    "google:gemini": 0.04,
    "google:imagen": 0.04,
    "runway": 0.08,
    "meshy:draft": 0.20,       # untextured image-to-3d
    "meshy:textured": 0.80,    # image-to-3d with texture + PBR
}


# ── Small utilities ─────────────────────────────────────────────────────────

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(s):
    s = (s or "").strip().lower().replace(" ", "_")
    s = SLUG_RE.sub("", s)
    return s[:80] or "untitled"


def get_api_key(provider, required=True):
    """Env var first, then the gitignored key file. Returns '' if missing
    and not required."""
    for env in KEY_ENVS[provider]:
        k = os.environ.get(env, "").strip()
        if k:
            return k
    kf = KEY_FILES[provider]
    if kf.exists():
        lines = kf.read_text().strip().splitlines()
        if lines and lines[0].strip():
            return lines[0].strip()
    if not required:
        return ""
    envs = " or ".join(KEY_ENVS[provider])
    sys.exit(
        f"{provider} API key not found.\n"
        f"  Either:  export {KEY_ENVS[provider][0]}=...\n"
        f"  Or:      echo '...' > {kf.relative_to(REPO.parent)}\n"
        f"           (env {envs}; the key file is gitignored.)"
    )


def data_uri(path_or_bytes, mime=None):
    if isinstance(path_or_bytes, (str, Path)):
        p = Path(path_or_bytes)
        data = p.read_bytes()
        if mime is None:
            mime, _ = mimetypes.guess_type(p.name)
    else:
        data = path_or_bytes
    mime = mime or "image/png"
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def http_json(method, url, body=None, headers=None, timeout=120):
    """JSON request → parsed JSON. Raises RuntimeError with the response
    body on HTTP errors so vendor messages reach the log."""
    hdrs = {"Accept": "application/json"}
    hdrs.update(headers or {})
    data = None
    if body is not None:
        hdrs["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "replace")[:1200]
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} on {method} {url}: {detail}") from e


def http_download(url, out_path, timeout=300):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            with open(out_path, "wb") as f:
                shutil.copyfileobj(resp, f, 64 * 1024)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"download HTTP {e.code}: {e.reason} ({url[:80]})") from e


def with_retries(fn, log, what):
    delay = SUBMIT_BACKOFF
    last = None
    for attempt in range(SUBMIT_RETRIES):
        try:
            return fn()
        except RuntimeError as e:
            msg = str(e)
            last = e
            retryable = ("HTTP 429" in msg) or ("HTTP 5" in msg)
            if retryable and attempt < SUBMIT_RETRIES - 1:
                log(f"    {what}: {msg[:120]} — retry in {delay:.0f}s")
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise last


# ── Roster ──────────────────────────────────────────────────────────────────

REQUIRED_ENTRY_KEYS = ("slug", "kind", "name", "file", "prompt")


def load_roster(path=ROSTER_PATH):
    if not path.exists():
        sys.exit(f"roster not found: {path}")
    data = json.loads(path.read_text())
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        sys.exit("roster has no 'entries' list")
    seen_slugs, seen_files = set(), {}
    for i, e in enumerate(entries):
        for k in REQUIRED_ENTRY_KEYS:
            if not e.get(k):
                sys.exit(f"roster entry #{i} missing '{k}': {json.dumps(e)[:120]}")
        if e["kind"] not in OUT_DIRS:
            sys.exit(f"roster entry {e['slug']}: kind {e['kind']!r} not in {sorted(OUT_DIRS)}")
        if e["slug"] in seen_slugs:
            sys.exit(f"roster: duplicate slug {e['slug']!r}")
        seen_slugs.add(e["slug"])
        key = (e["kind"], e["file"])
        if key in seen_files:
            sys.exit(f"roster: {e['slug']} and {seen_files[key]} both target {e['kind']}/{e['file']}")
        seen_files[key] = e["slug"]
        if not e["file"].endswith(".glb"):
            sys.exit(f"roster entry {e['slug']}: file must end in .glb")
        e.setdefault("vol", [])
        e.setdefault("keys", [e["slug"]])
        e.setdefault("aspect", "3:4" if e["kind"] != "prop" else "1:1")
        e.setdefault("pose", "a-pose" if e["kind"] != "prop" else None)
        e.setdefault("texture_prompt", "")
        e.setdefault("tag", "")
    data.setdefault("style", {})
    data.setdefault("defaults", {})
    return data


def select_entries(roster, selectors):
    entries = roster["entries"]
    if not selectors or "all" in selectors:
        return list(entries)
    out = []
    for e in entries:
        for s in selectors:
            s = s.strip()
            if s in OUT_DIRS and e["kind"] == s:
                out.append(e); break
            if re.fullmatch(r"vol\d+", s) and int(s[3:]) in e["vol"]:
                out.append(e); break
            if fnmatch.fnmatch(e["slug"], s) or fnmatch.fnmatch(e["file"], s):
                out.append(e); break
    return out


def entry_dir(entry):
    return CONCEPT_ROOT / entry["slug"]


def entry_out_path(entry):
    return OUT_DIRS[entry["kind"]] / entry["file"]


def build_prompt(roster, entry, view="front"):
    """Style preamble (per kind) + entry prompt + view instruction."""
    style = roster["style"].get(entry["kind"], "")
    parts = [style.replace("{name}", entry["name"]).strip(), entry["prompt"].strip()]
    suffix = roster["style"].get("suffix", "").strip()
    if suffix:
        parts.append(suffix)
    if view == "side":
        parts.append(roster["style"].get(
            "view_side",
            "Same subject, identical design, colors and details as the reference "
            "image, now seen from the left side in strict profile (90 degrees), "
            "same pose, same plain background, whole subject in frame."))
    elif view == "back":
        parts.append(roster["style"].get(
            "view_back",
            "Same subject, identical design, colors and details as the reference "
            "image, now seen directly from behind (180 degrees), same pose, same "
            "plain background, whole subject in frame."))
    return "\n".join(p for p in parts if p)


def texture_prompt_for(entry):
    tp = (entry.get("texture_prompt") or entry["prompt"]).strip()
    return tp[:600]


# ── Manifest ────────────────────────────────────────────────────────────────

_manifest_lock = threading.Lock()


def load_manifest():
    if MANIFEST_PATH.exists():
        try:
            data = json.loads(MANIFEST_PATH.read_text())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return []


def append_manifest(entry):
    with _manifest_lock:
        m = load_manifest()
        m.append(entry)
        CONCEPT_ROOT.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(m, indent=2) + "\n")


def rel(p):
    try:
        return str(Path(p).relative_to(REPO.parent))
    except ValueError:
        return str(p)


# ── Google provider ─────────────────────────────────────────────────────────

def google_generate(prompt, aspect, model, api_key, refs=(), count=1, log=print):
    """Return a list of PNG/JPEG byte blobs. `refs` = list of image paths
    used as reference (Gemini image models only)."""
    family = GOOGLE_MODELS.get(model)
    if family is None:
        raise ValueError(f"unknown Google model {model!r}; known: {sorted(GOOGLE_MODELS)}")
    headers = {"x-goog-api-key": api_key}
    images = []
    if family == "imagen":
        if refs:
            log("    note: Imagen ignores reference images (use a gemini-* model for multi-view)")
        url = f"{GOOGLE_BASE}/models/{model}:predict"
        body = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": max(1, min(4, count)),
                "aspectRatio": aspect,
                "personGeneration": "allow_adult",
            },
        }
        resp = with_retries(lambda: http_json("POST", url, body, headers), log, "imagen")
        for p in resp.get("predictions", []):
            b64 = p.get("bytesBase64Encoded")
            if b64:
                images.append((base64.b64decode(b64), p.get("mimeType", "image/png")))
        if not images:
            raise RuntimeError(f"Imagen returned no images: {json.dumps(resp)[:400]}")
        return images

    url = f"{GOOGLE_BASE}/models/{model}:generateContent"
    parts = []
    for r in refs:
        p = Path(r)
        mime, _ = mimetypes.guess_type(p.name)
        parts.append({"inlineData": {"mimeType": mime or "image/png",
                                     "data": base64.b64encode(p.read_bytes()).decode("ascii")}})
    parts.append({"text": prompt})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect},
        },
    }
    for n in range(max(1, count)):
        resp = with_retries(lambda: http_json("POST", url, body, headers), log, "gemini")
        fb = resp.get("promptFeedback") or {}
        if fb.get("blockReason"):
            raise RuntimeError(f"Gemini blocked the prompt: {fb.get('blockReason')}")
        got = False
        for cand in resp.get("candidates", []):
            for part in (cand.get("content") or {}).get("parts", []):
                inline = part.get("inlineData")
                if inline and inline.get("data"):
                    images.append((base64.b64decode(inline["data"]),
                                   inline.get("mimeType", "image/png")))
                    got = True
        if not got:
            text = ""
            for cand in resp.get("candidates", []):
                for part in (cand.get("content") or {}).get("parts", []):
                    text += part.get("text", "")
                text += f" [finishReason={cand.get('finishReason')}]"
            raise RuntimeError(f"Gemini returned no image. {text[:400] or json.dumps(resp)[:400]}")
    return images


# ── Runway provider ─────────────────────────────────────────────────────────

def runway_ratio(model, aspect, explicit=None):
    if explicit:
        return explicit
    family = RUNWAY_MODELS.get(model)
    table = RUNWAY_RATIOS.get(family, RUNWAY_RATIOS["gen4"])
    if aspect not in table:
        raise ValueError(f"aspect {aspect!r} has no Runway ratio for {model}; "
                         f"use one of {sorted(table)} or pass --ratio")
    return table[aspect]


def runway_generate(prompt, aspect, model, api_key, refs=(), seed=None,
                    ratio=None, log=print):
    """Submit text_to_image, poll, download. `refs` = [(path, tag)]."""
    if model not in RUNWAY_MODELS:
        raise ValueError(f"unknown Runway model {model!r}; known: {sorted(RUNWAY_MODELS)}")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Runway-Version": RUNWAY_API_VERSION,
    }
    body = {
        "model": model,
        "promptText": prompt[:1000],
        "ratio": runway_ratio(model, aspect, ratio),
    }
    ref_list = []
    for path, tag in refs:
        data = Path(path).read_bytes()
        if len(data) > MAX_REF_BYTES:
            raise ValueError(f"reference {Path(path).name} is {len(data)//1024} KB; "
                             "Runway caps data-URI references at 5 MB")
        item = {"uri": data_uri(data, mimetypes.guess_type(str(path))[0] or "image/png")}
        if tag:
            if not RUNWAY_REF_TAG_RE.match(tag):
                raise ValueError(f"bad reference tag {tag!r} (3-16 chars, letter first, [A-Za-z0-9_])")
            item["tag"] = tag
        ref_list.append(item)
    if ref_list:
        body["referenceImages"] = ref_list[:3] if RUNWAY_MODELS[model] == "gen4" else ref_list
    elif model == "gen4_image_turbo":
        raise ValueError("gen4_image_turbo requires at least one reference image; use gen4_image")
    if seed is not None:
        body["seed"] = int(seed)

    resp = with_retries(lambda: http_json("POST", f"{RUNWAY_BASE}/text_to_image", body, headers),
                        log, "runway submit")
    task_id = resp.get("id")
    if not task_id:
        raise RuntimeError(f"Runway submit response missing id: {resp}")
    log(f"    runway task {task_id}")
    deadline = time.time() + POLL_TIMEOUT_IMAGE
    last = None
    while time.time() < deadline:
        t = http_json("GET", f"{RUNWAY_BASE}/tasks/{task_id}", headers=headers)
        status = t.get("status", "UNKNOWN")
        if status != last:
            log(f"    status: {status}")
            last = status
        if status in TERMINAL_RUNWAY:
            if status != "SUCCEEDED":
                raise RuntimeError(f"Runway task {status}: {t.get('failure') or t.get('failureCode') or json.dumps(t)[:300]}")
            urls = t.get("output") or []
            if not urls:
                raise RuntimeError("Runway succeeded with no output URLs")
            out = []
            for u in urls:
                req = urllib.request.Request(u, headers={"Accept": "*/*"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    mime = r.headers.get("Content-Type", "image/png").split(";")[0]
                    out.append((r.read(), mime))
            return out
        time.sleep(POLL_INTERVAL_IMAGE)
    raise RuntimeError(f"Runway task {task_id} did not finish within {POLL_TIMEOUT_IMAGE}s")


# ── Meshy provider ──────────────────────────────────────────────────────────

def meshy_submit(images, opts, api_key, log=print):
    """images: list of image paths (1 → image-to-3d, 2-4 → multi-image-to-3d).
    Returns (resource, task_id)."""
    headers = {"Authorization": f"Bearer {api_key}"}
    textured = bool(opts.get("texture"))
    body = {
        "should_texture": textured,
        "target_formats": ["glb"],
    }
    if len(images) == 1:
        resource = "image-to-3d"
        body["image_url"] = data_uri(images[0])
        body["model_type"] = opts.get("model_type") or "standard"
        if body["model_type"] == "smart-topology":
            body["target_polycount"] = int(opts.get("polycount") or 10000)
        if opts.get("ultra"):
            body["ultra_mode"] = True
        if opts.get("pose") in MESHY_POSES:
            body["pose_mode"] = opts["pose"]
        if opts.get("ai_model"):
            body["ai_model"] = opts["ai_model"]
        body["image_enhancement"] = opts.get("image_enhancement", True)
        body["remove_lighting"] = opts.get("remove_lighting", True)
    else:
        resource = "multi-image-to-3d"
        body["image_urls"] = [data_uri(p) for p in images[:4]]
        body["remove_lighting"] = opts.get("remove_lighting", True)
        if opts.get("ai_model"):
            body["ai_model"] = opts["ai_model"]
    if textured:
        body["enable_pbr"] = bool(opts.get("pbr", True))
        body["texture_resolution"] = opts.get("texture_resolution") or "4k"
        if opts.get("texture_prompt"):
            body["texture_prompt"] = opts["texture_prompt"][:600]
    resp = with_retries(lambda: http_json("POST", f"{MESHY_BASE}/{resource}", body, headers),
                        log, "meshy submit")
    task_id = resp.get("result") or resp.get("id")
    if not task_id:
        raise RuntimeError(f"Meshy submit response missing result id: {resp}")
    return resource, task_id


def meshy_poll(resource, task_id, api_key, log=print):
    headers = {"Authorization": f"Bearer {api_key}"}
    deadline = time.time() + POLL_TIMEOUT_MESH
    last = None
    while time.time() < deadline:
        t = http_json("GET", f"{MESHY_BASE}/{resource}/{task_id}", headers=headers)
        status = t.get("status", "UNKNOWN")
        prog = t.get("progress")
        key = (status, prog)
        if key != last:
            log(f"    status: {status}" + (f"  {prog}%" if prog is not None else ""))
            last = key
        if status in TERMINAL_MESHY:
            if status != "SUCCEEDED":
                err = (t.get("task_error") or {}).get("message") or json.dumps(t)[:300]
                raise RuntimeError(f"Meshy task {status}: {err}")
            return t
        time.sleep(POLL_INTERVAL_MESH)
    raise RuntimeError(f"Meshy task {task_id} did not finish within {POLL_TIMEOUT_MESH}s")


# ── Stages ──────────────────────────────────────────────────────────────────

def candidates_for(entry, view="front"):
    d = entry_dir(entry)
    if not d.exists():
        return []
    pat = f"{entry['slug']}_{view}_"
    return sorted(p for p in d.iterdir()
                  if p.is_file() and p.name.startswith(pat) and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))


def next_candidate_path(entry, view, provider, model):
    d = entry_dir(entry)
    d.mkdir(parents=True, exist_ok=True)
    stem = f"{entry['slug']}_{view}_{slugify(provider)}_{slugify(model)}"
    n = 1
    while True:
        p = d / f"{stem}_{n:02d}.png"
        if not p.exists():
            return p
        n += 1


def save_image(blob, mime, path):
    ext = {"image/jpeg": ".jpg", "image/webp": ".webp"}.get(mime, ".png")
    path = path.with_suffix(ext)
    path.write_bytes(blob)
    return path


def chosen_view_path(entry, view):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = entry_dir(entry) / f"{view}{ext}"
        if p.exists():
            return p
    return None


def set_chosen(entry, view, candidate):
    """Copy a candidate to <slug>/<view>.<ext> (the file the mesh stage uses)."""
    src = Path(candidate)
    if not src.is_absolute():
        src = entry_dir(entry) / src
    if not src.exists():
        raise FileNotFoundError(f"candidate not found: {candidate}")
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        old = entry_dir(entry) / f"{view}{ext}"
        if old.exists():
            old.unlink()
    dst = entry_dir(entry) / f"{view}{src.suffix.lower()}"
    shutil.copyfile(src, dst)
    return dst


def stage_image(roster, entry, opts, log=print):
    """Generate `count` front candidates (+ side/back if multiview). The first
    front candidate becomes front.png unless one is already chosen."""
    provider = opts.get("provider") or roster["defaults"].get("provider", "google")
    if provider == "google":
        model = opts.get("model") or roster["defaults"].get("google_model", GOOGLE_DEFAULT_MODEL)
    elif provider == "runway":
        model = opts.get("model") or roster["defaults"].get("runway_model", RUNWAY_DEFAULT_MODEL)
    else:
        raise ValueError(f"provider must be google or runway, got {provider!r}")
    count = max(1, int(opts.get("count") or 1))
    aspect = opts.get("aspect") or entry["aspect"]
    if aspect not in GOOGLE_ASPECTS:
        raise ValueError(f"aspect {aspect!r} not in {sorted(GOOGLE_ASPECTS)}")
    views = list(VIEWS) if opts.get("multiview") else ["front"]
    dry = bool(opts.get("dry_run"))
    saved = []

    front_prompt = build_prompt(roster, entry, "front")
    log(f"  image · {entry['slug']} · {provider}/{model} · {aspect} · x{count}"
        + (" · multiview" if len(views) > 1 else ""))
    if dry:
        log("    [DRY] prompt:\n      " + front_prompt.replace("\n", "\n      "))
        return saved

    api_key = get_api_key(provider)
    gen = google_generate if provider == "google" else runway_generate

    # front
    if provider == "google":
        blobs = gen(front_prompt, aspect, model, api_key, count=count, log=log)
    else:
        blobs = []
        for _ in range(count):
            blobs += gen(front_prompt, aspect, model, api_key, seed=opts.get("seed"),
                         ratio=opts.get("ratio"), log=log)
    for blob, mime in blobs:
        p = save_image(blob, mime, next_candidate_path(entry, "front", provider, model))
        saved.append(p)
        log(f"    saved {rel(p)}  ({len(blob)//1024} KB)")
    if saved and (opts.get("overwrite") or not chosen_view_path(entry, "front")):
        set_chosen(entry, "front", saved[0])
        log(f"    chosen front → {rel(entry_dir(entry) / 'front.png')}")

    # side / back, referencing the chosen front
    front = chosen_view_path(entry, "front")
    for view in views[1:]:
        if not front:
            break
        prompt = build_prompt(roster, entry, view)
        if provider == "google":
            if GOOGLE_MODELS.get(model) == "imagen":
                log(f"    skip {view}: Imagen cannot take a reference image; use a gemini-* model")
                continue
            blobs = gen(prompt, aspect, model, api_key, refs=[front], count=1, log=log)
        else:
            blobs = gen("@front " + prompt, aspect, model, api_key,
                        refs=[(front, "front")], seed=opts.get("seed"),
                        ratio=opts.get("ratio"), log=log)
        for blob, mime in blobs[:1]:
            p = save_image(blob, mime, next_candidate_path(entry, view, provider, model))
            saved.append(p)
            log(f"    saved {rel(p)}  ({len(blob)//1024} KB)")
            if opts.get("overwrite") or not chosen_view_path(entry, view):
                set_chosen(entry, view, p)

    append_manifest({
        "at": now_iso(), "stage": "image", "slug": entry["slug"], "kind": entry["kind"],
        "provider": provider, "model": model, "aspect": aspect,
        "views": views, "count": count, "prompt": front_prompt,
        "outputs": [rel(p) for p in saved],
    })
    return saved


def stage_mesh(roster, entry, opts, log=print):
    """Send the chosen view(s) to Meshy and install the GLB at the canonical path."""
    dry = bool(opts.get("dry_run"))
    out_path = entry_out_path(entry)
    explicit = opts.get("image")
    if explicit:
        images = [Path(explicit)]
    else:
        images = [p for p in (chosen_view_path(entry, v) for v in VIEWS) if p]
        if not opts.get("multiview"):
            images = images[:1]
    if not images:
        if dry:
            log(f"  mesh · {entry['slug']} · [DRY] would send {rel(entry_dir(entry) / 'front.png')} "
                f"(not generated yet) → {rel(out_path)}")
            return None
        raise FileNotFoundError(
            f"{entry['slug']}: no chosen concept image. Run the image stage first, "
            f"drop a file at {rel(entry_dir(entry) / 'front.png')}, or pass --image.")
    for p in images:
        if not p.exists():
            raise FileNotFoundError(f"image not found: {p}")

    mopts = {
        "texture": bool(opts.get("texture", roster["defaults"].get("texture", False))),
        "pbr": opts.get("pbr", roster["defaults"].get("pbr", True)),
        "texture_resolution": opts.get("texture_resolution") or roster["defaults"].get("texture_resolution", "4k"),
        "texture_prompt": texture_prompt_for(entry),
        "model_type": opts.get("model_type") or roster["defaults"].get("model_type", "standard"),
        "polycount": opts.get("polycount") or roster["defaults"].get("polycount", 10000),
        "ultra": bool(opts.get("ultra", False)),
        "pose": opts.get("pose") or entry.get("pose"),
        "ai_model": opts.get("ai_model") or roster["defaults"].get("meshy_ai_model"),
        "remove_lighting": opts.get("remove_lighting", True),
        "image_enhancement": opts.get("image_enhancement", True),
    }
    if mopts["model_type"] not in MESHY_MODEL_TYPES:
        raise ValueError(f"model_type {mopts['model_type']!r} not in {sorted(MESHY_MODEL_TYPES)}")
    if mopts["texture_resolution"] not in MESHY_TEXTURE_RES:
        raise ValueError(f"texture_resolution {mopts['texture_resolution']!r} not in {sorted(MESHY_TEXTURE_RES)}")
    if entry["kind"] == "prop":
        mopts["pose"] = None

    resource = "image-to-3d" if len(images) == 1 else "multi-image-to-3d"
    log(f"  mesh · {entry['slug']} · {resource} · {mopts['model_type']}"
        f" · {'textured ' + mopts['texture_resolution'] if mopts['texture'] else 'draft (untextured)'}"
        + (f" · {mopts['pose']}" if mopts['pose'] else "")
        + f" → {rel(out_path)}")
    log(f"    inputs: {', '.join(rel(p) for p in images)}")
    if out_path.exists() and not opts.get("overwrite"):
        log(f"    SKIP: {out_path.name} exists (pass --overwrite to regenerate)")
        return None
    if dry:
        log("    [DRY] would submit to Meshy")
        return None

    api_key = get_api_key("meshy")
    resource, task_id = meshy_submit(images, mopts, api_key, log=log)
    log(f"    meshy task {task_id}")
    result = meshy_poll(resource, task_id, api_key, log=log)
    glb_url = (result.get("model_urls") or {}).get("glb")
    if not glb_url:
        raise RuntimeError(f"Meshy succeeded but no GLB url: {json.dumps(result)[:300]}")
    tmp = out_path.with_suffix(".glb.part")
    http_download(glb_url, tmp)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    os.replace(tmp, out_path)
    size_kb = out_path.stat().st_size / 1024
    log(f"    installed {rel(out_path)}  ({size_kb:.0f} KB)")
    thumb = result.get("thumbnail_url")
    if thumb:
        try:
            http_download(thumb, entry_dir(entry) / "meshy_thumb.png")
        except Exception as e:  # thumbnail is a nicety
            log(f"    (thumbnail download failed: {e})")
    append_manifest({
        "at": now_iso(), "stage": "mesh", "slug": entry["slug"], "kind": entry["kind"],
        "resource": resource, "task_id": task_id, "inputs": [rel(p) for p in images],
        "options": {k: v for k, v in mopts.items() if k != "texture_prompt"},
        "output": rel(out_path), "file_size_kb": round(size_kb, 1),
    })
    return out_path


def estimate_cost(entries, opts, stages):
    total = 0.0
    provider = opts.get("provider") or "google"
    model = opts.get("model") or ""
    for _ in entries:
        if "image" in stages:
            n = max(1, int(opts.get("count") or 1)) + (2 if opts.get("multiview") else 0)
            if provider == "google":
                fam = GOOGLE_MODELS.get(model or GOOGLE_DEFAULT_MODEL, "gemini")
                total += n * COST_HINTS[f"google:{fam}"]
            else:
                total += n * COST_HINTS["runway"]
        if "mesh" in stages:
            total += COST_HINTS["meshy:textured" if opts.get("texture") else "meshy:draft"]
    return total


# ── Status (shared by `list` and the serve API) ─────────────────────────────

def entry_status(entry):
    out = entry_out_path(entry)
    d = entry_dir(entry)
    st = {
        "slug": entry["slug"],
        "glb_installed": out.exists(),
        "glb_size_kb": round(out.stat().st_size / 1024, 1) if out.exists() else None,
        "glb_path": rel(out),
        "chosen": {v: (rel(p) if p else None) for v, p in ((v, chosen_view_path(entry, v)) for v in VIEWS)},
        "candidates": {v: [rel(p) for p in candidates_for(entry, v)] for v in VIEWS},
        "meshy_thumb": rel(d / "meshy_thumb.png") if (d / "meshy_thumb.png").exists() else None,
    }
    return st


def cmd_list(roster, args):
    entries = select_entries(roster, args.selectors)
    if args.kind:
        entries = [e for e in entries if e["kind"] == args.kind]
    print(f"{'slug':28} {'kind':6} {'vol':8} {'img':4} {'glb':4}  file")
    for e in entries:
        st = entry_status(e)
        vols = ",".join(str(v) for v in e["vol"]) or "-"
        img = "✓" if st["chosen"]["front"] else ("·" if st["candidates"]["front"] else " ")
        glb = "✓" if st["glb_installed"] else " "
        print(f"{e['slug']:28} {e['kind']:6} {vols:8} {img:^4} {glb:^4}  {rel(entry_out_path(e))}")
    n_img = sum(1 for e in entries if chosen_view_path(e, "front"))
    n_glb = sum(1 for e in entries if entry_out_path(e).exists())
    print(f"\n{len(entries)} entries · {n_img} with a chosen concept image · {n_glb} GLBs installed")


# ── Serve mode ──────────────────────────────────────────────────────────────

class JobRunner:
    """Background jobs for the browser UI. One worker thread so vendor
    rate limits stay sane; each job keeps its own log."""

    def __init__(self, roster_path):
        self.roster_path = roster_path
        self.jobs = {}
        self.order = []
        self.lock = threading.Lock()
        self.queue = []
        self.cv = threading.Condition(self.lock)
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()

    def submit(self, action, slug, opts):
        jid = uuid.uuid4().hex[:10]
        job = {"id": jid, "action": action, "slug": slug, "opts": opts,
               "status": "queued", "log": [], "created": now_iso(), "error": None}
        with self.cv:
            self.jobs[jid] = job
            self.order.append(jid)
            self.queue.append(jid)
            self.cv.notify()
        return job

    def snapshot(self):
        with self.lock:
            return [dict(self.jobs[j], log=list(self.jobs[j]["log"])) for j in self.order[-50:]]

    def _loop(self):
        while True:
            with self.cv:
                while not self.queue:
                    self.cv.wait()
                jid = self.queue.pop(0)
                job = self.jobs[jid]
                job["status"] = "running"
            self._run(job)

    def _run(self, job):
        def log(msg):
            print(msg, flush=True)
            with self.lock:
                job["log"].append(msg)
        try:
            roster = load_roster(self.roster_path)   # re-read: prompts may have been edited
            entry = next((e for e in roster["entries"] if e["slug"] == job["slug"]), None)
            if entry is None:
                raise KeyError(f"unknown slug {job['slug']}")
            # per-job prompt override from the UI (does not rewrite the roster)
            if job["opts"].get("prompt"):
                entry = dict(entry, prompt=job["opts"]["prompt"])
            if job["opts"].get("texture_prompt"):
                entry = dict(entry, texture_prompt=job["opts"]["texture_prompt"])
            opts = dict(job["opts"])
            if job["action"] in ("image", "run"):
                stage_image(roster, entry, opts, log=log)
            if job["action"] in ("mesh", "run"):
                stage_mesh(roster, entry, opts, log=log)
            with self.lock:
                job["status"] = "done"
        except SystemExit as e:      # get_api_key() exits; surface it instead
            with self.lock:
                job["status"] = "error"
                job["error"] = str(e)
            log(f"ERROR: {e}")
        except Exception as e:
            with self.lock:
                job["status"] = "error"
                job["error"] = str(e)[:800]
            log(f"ERROR: {e}")


def make_handler(runner, roster_path):
    class Handler(SimpleHTTPRequestHandler):
        # Static: /hero_uploader/... and anything under godot/tools; plus
        # /assets/... mapped to godot/assets so the page can preview
        # concept images and installed GLBs from the same origin.
        def translate_path(self, path):
            path = urllib.parse.urlparse(path).path
            path = urllib.parse.unquote(path)
            if path.startswith("/assets/"):
                base = REPO / "assets"
                sub = path[len("/assets/"):]
            else:
                base = TOOLS
                sub = path.lstrip("/")
            full = (base / sub).resolve()
            if base.resolve() not in full.parents and full != base.resolve():
                return str(base / "__forbidden__")
            return str(full)

        def log_message(self, fmt, *args):
            if self.path.startswith("/api/jobs") or self.path.startswith("/api/roster"):
                return
            super().log_message(fmt, *args)

        def _json(self, obj, code=200):
            data = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _body(self):
            n = int(self.headers.get("Content-Length") or 0)
            return self.rfile.read(n) if n else b""

        def do_GET(self):
            p = urllib.parse.urlparse(self.path).path
            if p == "/api/roster":
                roster = load_roster(roster_path)
                for e in roster["entries"]:
                    e["status"] = entry_status(e)
                roster["keys"] = {k: bool(get_api_key(k, required=False)) for k in KEY_FILES}
                roster["providers"] = {
                    "google": {"models": list(GOOGLE_MODELS), "default": GOOGLE_DEFAULT_MODEL},
                    "runway": {"models": list(RUNWAY_MODELS), "default": RUNWAY_DEFAULT_MODEL},
                    "meshy": {"model_types": sorted(MESHY_MODEL_TYPES),
                              "texture_resolutions": sorted(MESHY_TEXTURE_RES),
                              "poses": sorted(MESHY_POSES)},
                }
                roster["aspects"] = sorted(GOOGLE_ASPECTS)
                roster["repo_root"] = str(REPO.parent)
                return self._json(roster)
            if p == "/api/jobs":
                return self._json({"jobs": runner.snapshot()})
            if p == "/api/prompt":
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                roster = load_roster(roster_path)
                slug = (q.get("slug") or [""])[0]
                e = next((e for e in roster["entries"] if e["slug"] == slug), None)
                if e is None:
                    return self._json({"error": "unknown slug"}, 404)
                return self._json({"front": build_prompt(roster, e, "front"),
                                   "side": build_prompt(roster, e, "side"),
                                   "back": build_prompt(roster, e, "back"),
                                   "texture": texture_prompt_for(e)})
            if p == "/" or p == "":
                self.send_response(302)
                self.send_header("Location", "/hero_uploader/")
                self.end_headers()
                return
            return super().do_GET()

        def do_POST(self):
            p = urllib.parse.urlparse(self.path).path
            roster = load_roster(roster_path)
            by_slug = {e["slug"]: e for e in roster["entries"]}
            if p == "/api/jobs":
                try:
                    req = json.loads(self._body().decode("utf-8") or "{}")
                except json.JSONDecodeError:
                    return self._json({"error": "bad json"}, 400)
                action = req.get("action")
                slug = req.get("slug")
                if action not in ("image", "mesh", "run") or slug not in by_slug:
                    return self._json({"error": "action must be image|mesh|run and slug must be in the roster"}, 400)
                job = runner.submit(action, slug, req.get("opts") or {})
                return self._json({"job": dict(job)})
            if p == "/api/pick":
                req = json.loads(self._body().decode("utf-8") or "{}")
                e = by_slug.get(req.get("slug"))
                view = req.get("view", "front")
                if e is None or view not in VIEWS:
                    return self._json({"error": "bad slug/view"}, 400)
                cand = req.get("candidate", "")
                # accept repo-relative paths from the status payload
                cand_path = (REPO.parent / cand) if cand.startswith("godot/") else Path(cand)
                try:
                    dst = set_chosen(e, view, cand_path)
                except FileNotFoundError as ex:
                    return self._json({"error": str(ex)}, 404)
                return self._json({"chosen": rel(dst)})
            if p.startswith("/api/upload/"):
                # Raw bytes in the body: /api/upload/<slug>/<view>  (image)
                #                        /api/upload/<slug>/glb     (model)
                parts = p.split("/")[3:]
                if len(parts) != 2 or parts[0] not in by_slug:
                    return self._json({"error": "use /api/upload/<slug>/<front|side|back|glb>"}, 400)
                e = by_slug[parts[0]]
                data = self._body()
                if not data:
                    return self._json({"error": "empty body"}, 400)
                if parts[1] == "glb":
                    out = entry_out_path(e)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(data)
                    return self._json({"installed": rel(out), "size_kb": round(len(data) / 1024, 1)})
                if parts[1] in VIEWS:
                    mime = self.headers.get("Content-Type", "image/png").split(";")[0]
                    cand = save_image(data, mime, next_candidate_path(e, parts[1], "upload", "manual"))
                    dst = set_chosen(e, parts[1], cand)
                    return self._json({"candidate": rel(cand), "chosen": rel(dst)})
                return self._json({"error": "bad target"}, 400)
            return self._json({"error": "not found"}, 404)

    return Handler


def cmd_serve(args):
    runner = JobRunner(ROSTER_PATH)
    handler = make_handler(runner, ROSTER_PATH)
    srv = ThreadingHTTPServer((args.host, args.port), handler)
    keys = {k: bool(get_api_key(k, required=False)) for k in KEY_FILES}
    print(f"Hero Studio  →  http://{args.host}:{args.port}/hero_uploader/")
    print("keys: " + "  ".join(f"{k}={'ok' if v else 'MISSING'}" for k, v in keys.items()))
    print("Ctrl-C to stop.", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


# ── CLI ─────────────────────────────────────────────────────────────────────

def add_image_opts(ap):
    ap.add_argument("--provider", choices=["google", "runway"],
                    help="image provider (default: roster defaults.provider, else google)")
    ap.add_argument("--model", help="provider model id (see GOOGLE_MODELS / RUNWAY_MODELS)")
    ap.add_argument("--count", type=int, default=1, help="front-view candidates per entry")
    ap.add_argument("--aspect", help="override roster aspect (1:1, 3:4, 9:16, ...)")
    ap.add_argument("--ratio", help="Runway only: explicit ratio string, e.g. 1080:1440")
    ap.add_argument("--seed", type=int, help="Runway only: seed for reproducible tweaks")
    ap.add_argument("--multiview", action="store_true",
                    help="also generate side + back views from the chosen front (feeds multi-image-to-3d)")


def add_mesh_opts(ap):
    ap.add_argument("--texture", action="store_true", help="textured output (PBR maps); the roster default")
    ap.add_argument("--no-texture", action="store_true", help="untextured draft mesh (cheaper; retexture later)")
    ap.add_argument("--no-pbr", action="store_true", help="with --texture: base color only")
    ap.add_argument("--texture-resolution", choices=sorted(MESHY_TEXTURE_RES))
    ap.add_argument("--model-type", choices=sorted(MESHY_MODEL_TYPES))
    ap.add_argument("--polycount", type=int, help="smart-topology target triangles (100-15000)")
    ap.add_argument("--ultra", action="store_true", help="standard mode: extra detail pass (costs more)")
    ap.add_argument("--pose", choices=sorted(MESHY_POSES), help="override roster pose")
    ap.add_argument("--ai-model", help="explicit Meshy ai_model (normally omitted → server latest)")
    ap.add_argument("--image", help="explicit concept image path (single entry only)")


def common_opts(ap):
    ap.add_argument("selectors", nargs="*", default=["all"],
                    help="slugs, globs, vol5/vol6/vol7, hero/demon/prop, or all")
    ap.add_argument("--dry-run", action="store_true", help="print what would happen; no API calls")
    ap.add_argument("--overwrite", action="store_true", help="redo even if outputs exist")
    ap.add_argument("--limit", type=int, help="stop after this many entries")


def opts_from_args(args):
    o = {k: v for k, v in vars(args).items() if v not in (None, False)}
    if getattr(args, "no_pbr", False):
        o["pbr"] = False
    if getattr(args, "no_texture", False):
        o["texture"] = False
    return o


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="show roster + status")
    p.add_argument("selectors", nargs="*", default=["all"])
    p.add_argument("--kind", choices=sorted(OUT_DIRS))

    p = sub.add_parser("image", help="generate concept images")
    common_opts(p); add_image_opts(p)

    p = sub.add_parser("pick", help="choose a candidate as the front/side/back view")
    p.add_argument("slug"); p.add_argument("candidate")
    p.add_argument("--view", choices=VIEWS, default="front")

    p = sub.add_parser("mesh", help="send chosen images to Meshy, install GLB")
    common_opts(p); add_mesh_opts(p)
    p.add_argument("--multiview", action="store_true",
                   help="send front+side+back (when present) to multi-image-to-3d")

    p = sub.add_parser("run", help="image then mesh")
    common_opts(p); add_image_opts(p); add_mesh_opts(p)

    p = sub.add_parser("serve", help="serve the browser UI + JSON API")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)

    args = ap.parse_args()
    if args.cmd == "serve":
        load_roster()  # validate early
        return cmd_serve(args)

    roster = load_roster()
    if args.cmd == "list":
        return cmd_list(roster, args)
    if args.cmd == "pick":
        e = next((e for e in roster["entries"] if e["slug"] == args.slug), None)
        if e is None:
            sys.exit(f"unknown slug {args.slug}")
        dst = set_chosen(e, args.view, args.candidate)
        print(f"chosen {args.view} → {rel(dst)}")
        return

    entries = select_entries(roster, args.selectors)
    if not entries:
        sys.exit(f"no roster entries match {args.selectors}")
    opts = opts_from_args(args)
    stages = {"image": ["image"], "mesh": ["mesh"], "run": ["image", "mesh"]}[args.cmd]
    if opts.get("image") and len(entries) != 1:
        sys.exit("--image applies to a single entry")
    est = estimate_cost(entries, opts, stages)
    print(f"{args.cmd}: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}  ~${est:.2f} estimated (rough)",
          flush=True)
    if not args.dry_run:
        # fail fast on missing keys before spending anything
        if "image" in stages:
            get_api_key(opts.get("provider") or roster["defaults"].get("provider", "google"))
        if "mesh" in stages:
            get_api_key("meshy")

    done = errors = 0
    for i, e in enumerate(entries):
        print(f"\n[{i+1}/{len(entries)}] {e['kind']}/{e['slug']} — {e['name']}", flush=True)
        try:
            if "image" in stages:
                stage_image(roster, e, opts)
            if "mesh" in stages:
                stage_mesh(roster, e, opts)
            done += 1
        except (RuntimeError, ValueError, FileNotFoundError, KeyError) as ex:
            errors += 1
            print(f"    ERROR: {ex}", file=sys.stderr, flush=True)
        if args.limit and done >= args.limit:
            print(f"\nhit --limit {args.limit}, stopping", file=sys.stderr)
            break
    print(f"\nsummary: selected={len(entries)} ok={done} errors={errors}", file=sys.stderr)
    print(f"manifest: {rel(MANIFEST_PATH)}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main() or 0)
