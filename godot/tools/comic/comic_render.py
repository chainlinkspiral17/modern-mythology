#!/usr/bin/env python3
"""comic_render.py — render Drift Wood / ROFLCOPTER strips as actual comic
strips with an image generator (the concept run).

Reads a strip-prompt queue (from `comic_tool.py strip-prompts`), sends each
job to a provider, downloads the image, and writes it plus a manifest to
godot/assets/comic/vol10/<provider>/<slug>.png. Mirrors runway_render.py's
conventions (stdlib only, key from env or key file, --dry-run, --only).

Providers:
  runway   Runway text_to_image (gen4_image). Key: RUNWAYML_API_KEY or
           godot/tools/.runway_key (same file runway_render.py uses).
  google   Google Imagen via the Gemini API (imagen-4.0-generate-001 by
           default; --model gemini-2.5-flash-image switches to the Gemini
           image model, which letters text more reliably). Key:
           GOOGLE_API_KEY / GEMINI_API_KEY or godot/tools/.google_key.

Usage:
  python3 godot/tools/comic/comic_render.py --provider runway
  python3 godot/tools/comic/comic_render.py --provider google --only "dw_2014*"
  python3 godot/tools/comic/comic_render.py --provider runway --dry-run
  python3 godot/tools/comic/comic_render.py --provider google --model gemini-2.5-flash-image --limit 2
  python3 godot/tools/comic/comic_render.py --provider runway --queue godot/tools/comic/out/strip_prompts.json --variants 2

Endpoints are the providers' documented ones as of mid-2026; if a call 400s,
print the body (we do) and check the field names against the current docs
before changing anything else.
"""
import argparse
import base64
import fnmatch
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
TOOLS = HERE.parent
OUT_ROOT = REPO / "godot" / "assets" / "comic" / "vol10"
DEFAULT_QUEUE = HERE / "out" / "strip_prompts.json"

RUNWAY_BASE = "https://api.dev.runwayml.com/v1"
RUNWAY_API_VERSION = "2024-11-06"
RUNWAY_MODEL = "gen4_image"
RUNWAY_RATIOS = {"1920:1080", "1080:1920", "1024:1024", "1360:768", "1080:1080", "1168:880",
                 "1440:1080", "1080:1440", "1808:768", "2112:912", "1280:720", "720:1280",
                 "720:720", "960:720", "720:960", "1680:720"}
GOOGLE_BASE = "https://generativelanguage.googleapis.com/v1beta"
GOOGLE_IMAGEN = "imagen-4.0-generate-001"
GOOGLE_ASPECTS = {"1:1", "3:4", "4:3", "9:16", "16:9"}
POLL_INTERVAL = 4.0
POLL_TIMEOUT = 60 * 6
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED"}


# ── keys ─────────────────────────────────────────────────────────────────

def _key(env_names, key_file):
    for e in env_names:
        v = os.environ.get(e, "").strip()
        if v:
            return v
    p = TOOLS / key_file
    if p.exists():
        v = p.read_text().strip().splitlines()[0].strip()
        if v:
            return v
    sys.exit(f"✗ no API key: set {' or '.join(env_names)} or write it to {p}")


def _http(url, method="GET", headers=None, body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ── runway ───────────────────────────────────────────────────────────────

def runway_generate(job, key, seed=None):
    ratio = job.get("runway_ratio", "1920:1080")
    if ratio not in RUNWAY_RATIOS:
        ratio = "1920:1080"
    body = {"model": RUNWAY_MODEL, "promptText": job["prompt"][:1000], "ratio": ratio}
    if seed is not None:
        body["seed"] = int(seed)
    refs = job.get("reference_images") or []
    if refs:
        body["referenceImages"] = [{"uri": r, "tag": f"ref{i+1}"} for i, r in enumerate(refs[:3])]
    h = {"Authorization": f"Bearer {key}", "X-Runway-Version": RUNWAY_API_VERSION}
    st, raw = _http(f"{RUNWAY_BASE}/text_to_image", "POST", h, body)
    if st not in (200, 201):
        raise RuntimeError(f"runway submit {st}: {raw[:400]!r}")
    task_id = json.loads(raw)["id"]
    t0 = time.time()
    while time.time() - t0 < POLL_TIMEOUT:
        time.sleep(POLL_INTERVAL)
        st, raw = _http(f"{RUNWAY_BASE}/tasks/{task_id}", "GET", h)
        if st != 200:
            raise RuntimeError(f"runway poll {st}: {raw[:400]!r}")
        d = json.loads(raw)
        if d.get("status") in TERMINAL:
            if d["status"] != "SUCCEEDED":
                raise RuntimeError(f"runway task {d['status']}: {d.get('failure') or d.get('failureCode')}")
            url = d["output"][0]
            st, img = _http(url, "GET", {}, None, timeout=300)
            if st != 200:
                raise RuntimeError(f"runway download {st}")
            return img, {"task_id": task_id, "ratio": ratio, "model": RUNWAY_MODEL}
    raise RuntimeError("runway poll timeout")


# ── google ───────────────────────────────────────────────────────────────

def google_generate(job, key, model, seed=None):
    aspect = job.get("google_aspect", "16:9")
    if aspect not in GOOGLE_ASPECTS:
        aspect = "16:9"
    h = {"x-goog-api-key": key}
    if model.startswith("imagen"):
        body = {"instances": [{"prompt": job["prompt"]}],
                "parameters": {"sampleCount": 1, "aspectRatio": aspect, "personGeneration": "allow_adult"}}
        if job.get("negative"):
            body["parameters"]["negativePrompt"] = job["negative"]
        if seed is not None:
            body["parameters"]["seed"] = int(seed)
        st, raw = _http(f"{GOOGLE_BASE}/models/{model}:predict", "POST", h, body, timeout=180)
        if st != 200:
            raise RuntimeError(f"google imagen {st}: {raw[:400]!r}")
        d = json.loads(raw)
        preds = d.get("predictions") or []
        if not preds:
            raise RuntimeError(f"google imagen: no predictions ({raw[:300]!r})")
        return base64.b64decode(preds[0]["bytesBase64Encoded"]), {"model": model, "aspect": aspect}
    # gemini image model
    text = job["prompt"]
    if job.get("negative"):
        text += f"\n\nAvoid: {job['negative']}."
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"],
                                 "imageConfig": {"aspectRatio": aspect}}}
    st, raw = _http(f"{GOOGLE_BASE}/models/{model}:generateContent", "POST", h, body, timeout=180)
    if st != 200:
        raise RuntimeError(f"google gemini {st}: {raw[:400]!r}")
    d = json.loads(raw)
    for c in d.get("candidates") or []:
        for part in (c.get("content") or {}).get("parts") or []:
            inl = part.get("inlineData") or part.get("inline_data")
            if inl and inl.get("data"):
                return base64.b64decode(inl["data"]), {"model": model, "aspect": aspect}
    raise RuntimeError(f"google gemini: no image in response ({raw[:300]!r})")


# ── main ─────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provider", choices=["runway", "google"], required=True)
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE))
    ap.add_argument("--model", help="google: imagen-4.0-generate-001 (default) or gemini-2.5-flash-image")
    ap.add_argument("--only", help="glob on slug")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--variants", type=int, default=1, help="renders per strip (different seeds)")
    ap.add_argument("--seed", type=int, help="base seed; variants add 1, 2, ...")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    q = json.loads(Path(args.queue).read_text(encoding="utf-8"))
    jobs = [j for j in q["jobs"] if not args.only or fnmatch.fnmatch(j["slug"], args.only)]
    if args.limit:
        jobs = jobs[:args.limit]
    model = args.model or (GOOGLE_IMAGEN if args.provider == "google" else RUNWAY_MODEL)
    out_dir = OUT_ROOT / args.provider
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_p = out_dir / "manifest.json"
    manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else {"renders": []}

    if args.dry_run:
        for j in jobs:
            print(f"— {j['slug']}  [{j.get('runway_ratio') if args.provider=='runway' else j.get('google_aspect')}]")
            print(f"   {j['prompt'][:300]}…")
        print(f"{len(jobs)} jobs (dry run)")
        return 0

    key = _key(["RUNWAYML_API_KEY"], ".runway_key") if args.provider == "runway" \
        else _key(["GOOGLE_API_KEY", "GEMINI_API_KEY"], ".google_key")

    done = fails = 0
    for j in jobs:
        for v in range(args.variants):
            suffix = f"_v{v+1}" if args.variants > 1 else ""
            out_p = out_dir / f"{j['slug']}{suffix}.png"
            if out_p.exists() and not args.overwrite:
                print(f"· {out_p.name} exists, skip")
                continue
            seed = (args.seed + v) if args.seed is not None else (j.get("seed") if v == 0 else None)
            print(f"→ {j['slug']}{suffix} via {args.provider}/{model} …", flush=True)
            try:
                if args.provider == "runway":
                    img, meta = runway_generate(j, key, seed)
                else:
                    img, meta = google_generate(j, key, model, seed)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print(f"  ✗ {e}")
                continue
            out_p.write_bytes(img)
            done += 1
            manifest["renders"].append({
                "slug": j["slug"], "file": str(out_p.relative_to(REPO)), "provider": args.provider,
                "strip_id": j.get("strip_id"), "date": j.get("date"), "format": j.get("format"),
                "lettered": j.get("lettered"), "seed": seed, "prompt": j["prompt"],
                "rendered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **meta})
            manifest_p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✓ {out_p.relative_to(REPO)} ({len(img)//1024} KB)")
    print(f"done: {done} rendered, {fails} failed → {out_dir.relative_to(REPO)}")
    return 1 if fails and not done else 0


if __name__ == "__main__":
    sys.exit(main())
