#!/usr/bin/env python3
"""comic_render.py — render Drift Wood / ROFLCOPTER strips as actual comic
strips with an image generator (the concept run).

Reads a strip-prompt queue (from `comic_tool.py strip-prompts`), sends each
job to a provider, downloads the image, and writes it plus a manifest to
godot/assets/comic/vol10/<provider>/<slug>.png. Mirrors runway_render.py's
conventions (stdlib only, key from env or key file, --dry-run, --only).

Providers:
  runway   Runway dev API text_to_image. --model picks the model (gen4_image
           by default; gen4_image_turbo, gemini_2.5_flash, or any id Runway
           lists today — unknown ids are passed through). Key:
           RUNWAYML_API_KEY or godot/tools/.runway_key.
  google   Google Gemini API. --model imagen-4.0-generate-001 (default),
           imagen-4.0-ultra-generate-001, imagen-4.0-fast-generate-001,
           gemini-2.5-flash-image (letters text; takes references), or any
           id. Key: GOOGLE_API_KEY / GEMINI_API_KEY or godot/tools/.google_key.

  --list-models prints what the runner knows. Every run is a NEW TAKE:
  an existing file is never skipped or overwritten; the next _t2, _t3…
  is written (use --take skip for the old behaviour, --overwrite to
  replace).

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
import mimetypes
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

# Models the runners know about. `--model` accepts ANY id, known or not — the
# id is passed straight through to the provider, so a model Runway or Google
# added after this file was written works without editing it; `known` here
# only drives the inspector's menu and the notes. Runway's dev API and its
# MCP use different ids for the same models (the MCP's nano-banana-pro is the
# dev API's gemini_2.5_flash family); the dev-API ids are the ones this
# runner sends. Check https://docs.dev.runwayml.com for the current list.
MODELS = {
    "runway": [
        {"id": "gen4_image", "label": "Gen-4 Image", "note": "Runway's own; up to 3 reference images with @tags; pixel ratios", "verified": True},
        {"id": "gen4_image_turbo", "label": "Gen-4 Image Turbo", "note": "faster/cheaper Gen-4; needs at least one reference image", "verified": True},
        {"id": "gemini_2.5_flash", "label": "Gemini 2.5 Flash Image (nano banana)", "note": "letters text well; references as @tags", "verified": True},
        {"id": "gemini_3_pro", "label": "Gemini 3 Pro Image (nano banana pro)", "note": "the concept run's model via the MCP; dev-API id may differ — edit if the API 400s", "verified": False},
        {"id": "gpt_image_2", "label": "GPT Image 2", "note": "strong lettering and layout; its own size list (learned on first use)", "verified": True},
        {"id": "seedream_5", "label": "Seedream 5", "note": "unverified id", "verified": False},
        {"id": "ideogram_4", "label": "Ideogram 4", "note": "typography-first; unverified id", "verified": False},
        {"id": "flux_2", "label": "FLUX 2", "note": "unverified id", "verified": False},
    ],
    "google": [
        {"id": "imagen-4.0-generate-001", "label": "Imagen 4", "note": "no reference images; negative prompt supported", "verified": True},
        {"id": "imagen-4.0-ultra-generate-001", "label": "Imagen 4 Ultra", "note": "higher fidelity, slower", "verified": True},
        {"id": "imagen-4.0-fast-generate-001", "label": "Imagen 4 Fast", "note": "cheap drafts", "verified": True},
        {"id": "gemini-2.5-flash-image", "label": "Gemini 2.5 Flash Image", "note": "letters text reliably; takes reference images inline", "verified": True},
        {"id": "gemini-3-pro-image-preview", "label": "Gemini 3 Pro Image (preview)", "note": "unverified id; try it", "verified": False},
    ],
}
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


# ── reference images ─────────────────────────────────────────────────────

def _ref_uris(job, limit=3):
    """Turn a job's reference_images (from comic_tool.py strip-prompts / sheets)
    into [{uri, tag}]. Local files become data URIs; URLs pass through; a
    Runway task id alone can't be resolved through the dev API (that's the
    MCP's referenceImages taskId), so it is skipped with a note."""
    out = []
    for r in (job.get("reference_images") or [])[:limit]:
        if isinstance(r, str):  # legacy: bare URL
            out.append({"uri": r, "tag": f"ref{len(out)+1}"}); continue
        tag = r.get("tag") or f"ref{len(out)+1}"
        f = r.get("file")
        if f and (REPO / f).exists():
            p = REPO / f
            mime = mimetypes.guess_type(str(p))[0] or "image/png"
            out.append({"uri": f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode(), "tag": tag})
        elif r.get("url"):
            out.append({"uri": r["url"], "tag": tag})
        elif r.get("runway_task_id"):
            print(f"  · ref {r.get('id')} is only a Runway task id ({r['runway_task_id']}); fetch its PNG to {f} to use it here")
        else:
            print(f"  · ref {r.get('id')} has no file yet ({f}); skipped")
    return out


def _ref_inline_parts(job, limit=4):
    """Gemini image model: reference images as inline_data parts, each preceded
    by a text part naming its @tag."""
    parts = []
    for r in (job.get("reference_images") or [])[:limit]:
        f = r.get("file") if isinstance(r, dict) else None
        if f and (REPO / f).exists():
            p = REPO / f
            mime = mimetypes.guess_type(str(p))[0] or "image/png"
            parts.append({"text": f"Reference @{r.get('tag')} ({r.get('kind', 'reference')}):"})
            parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(p.read_bytes()).decode()}})
    return parts


# ── runway ───────────────────────────────────────────────────────────────

RATIO_CACHE = HERE / "out" / "runway_ratios.json"


def _load_ratio_cache():
    try:
        return json.loads(RATIO_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _closest_ratio(want, allowed):
    """Pick the allowed 'W:H' whose aspect is nearest the wanted 'W:H'."""
    import math
    def asp(r):
        w, h = r.split(":"); return int(w) / int(h)
    target = asp(want)
    return min(allowed, key=lambda r: abs(math.log(asp(r) / target)))


def _allowed_from_400(raw):
    """Runway's validation error lists the values a field accepts; pull the
    'W:H' list out of it so we can retry with the closest one."""
    try:
        d = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    for issue in d.get("issues") or []:
        vals = issue.get("values") or issue.get("options") or []
        vals = [v for v in vals if isinstance(v, str) and ":" in v and v.replace(":", "").isdigit()]
        if vals:
            return vals
    return None


def runway_generate(job, key, model=RUNWAY_MODEL, seed=None):
    """Submit to text_to_image and poll. Ratios differ per model; the strip's
    ratio is tried first (or the cached closest for this model), and on a
    400 that lists the model's allowed sizes we pick the nearest and retry
    once, caching the list in out/runway_ratios.json."""
    want = job.get("runway_ratio", "1920:1080")
    cache = _load_ratio_cache()
    if model in cache and cache[model]:
        ratio = _closest_ratio(want, cache[model])
    elif model.startswith("gen4"):
        ratio = want if want in RUNWAY_RATIOS else "1920:1080"
    else:
        ratio = want
    h = {"Authorization": f"Bearer {key}", "X-Runway-Version": RUNWAY_API_VERSION}
    ref_payload = _ref_uris(job, limit=3)

    def submit(r):
        body = {"model": model, "promptText": job["prompt"][:1000], "ratio": r}
        if seed is not None:
            body["seed"] = int(seed)
        if ref_payload:
            body["referenceImages"] = ref_payload
        return _http(f"{RUNWAY_BASE}/text_to_image", "POST", h, body)

    st, raw = submit(ratio)
    if st == 400:
        allowed = _allowed_from_400(raw)
        if allowed and ratio not in allowed:
            cache[model] = allowed
            try:
                RATIO_CACHE.parent.mkdir(parents=True, exist_ok=True)
                RATIO_CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            except OSError:
                pass
            ratio = _closest_ratio(want, allowed)
            print(f"  · {model} doesn't take {want}; using its closest size {ratio} (list cached for next time)")
            st, raw = submit(ratio)
    if st not in (200, 201):
        raise RuntimeError(f"runway submit {st} (model {model}, ratio {ratio}): {raw[:400]!r}")
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
            return img, {"task_id": task_id, "ratio": ratio, "model": model}
    raise RuntimeError("runway poll timeout")


# ── google ───────────────────────────────────────────────────────────────

def google_generate(job, key, model, seed=None):
    aspect = job.get("google_aspect", "16:9")
    if aspect not in GOOGLE_ASPECTS:
        aspect = "16:9"
    h = {"x-goog-api-key": key}
    if model.startswith("imagen"):
        if job.get("reference_images"):
            print("  · imagen ignores reference images; use --model gemini-2.5-flash-image to apply them")
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
    parts = _ref_inline_parts(job) + [{"text": text}]
    body = {"contents": [{"parts": parts}],
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
    ap.add_argument("--provider", choices=["runway", "google"], help="required unless --list-models")
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE))
    ap.add_argument("--model", help="model id for either provider; any id is passed through (see --list-models)")
    ap.add_argument("--list-models", action="store_true", help="print the known model ids per provider and exit")
    ap.add_argument("--take", choices=["new", "skip"], default="new", help="new (default): if the file exists, write the next _t2/_t3… take; skip: leave existing files alone")
    ap.add_argument("--only", help="glob on slug")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--variants", type=int, default=1, help="renders per strip (different seeds)")
    ap.add_argument("--seed", type=int, help="base seed; variants add 1, 2, ...")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if not args.provider and not args.list_models:
        ap.error("--provider is required")
    if args.list_models:
        for prov, ms in MODELS.items():
            print(prov)
            for m in ms:
                print(f"  {m['id']:32s} {m['label']:36s} {'' if m['verified'] else '(unverified id) '}{m['note']}")
        print("any other id is passed through as given.")
        return 0

    q = json.loads(Path(args.queue).read_text(encoding="utf-8"))
    jobs = [j for j in q["jobs"] if not args.only or fnmatch.fnmatch(j["slug"], args.only)]
    if args.limit:
        jobs = jobs[:args.limit]
    model = args.model or (GOOGLE_IMAGEN if args.provider == "google" else RUNWAY_MODEL)
    is_sheets = any(j.get("tag") == "vol10-sheets" for j in q.get("jobs", []))
    out_dir = OUT_ROOT / ("sheets" if is_sheets else args.provider)
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
                if args.take == "skip":
                    print(f"· {out_p.name} exists, skip")
                    continue
                t = 2
                while (out_dir / f"{j['slug']}{suffix}_t{t}.png").exists():
                    t += 1
                out_p = out_dir / f"{j['slug']}{suffix}_t{t}.png"  # a new take, never a silent skip
            seed = (args.seed + v) if args.seed is not None else (j.get("seed") if v == 0 else None)
            print(f"→ {j['slug']}{suffix} via {args.provider}/{model} …", flush=True)
            try:
                if args.provider == "runway":
                    img, meta = runway_generate(j, key, model, seed)
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
                "kind": j.get("kind"), "tags": j.get("tags", []), "references": [r.get("id") for r in (j.get("reference_images") or []) if isinstance(r, dict)],
                "strip_id": j.get("strip_id"), "date": j.get("date"), "format": j.get("format"),
                "lettered": j.get("lettered"), "seed": seed, "take": out_p.stem.split("_t")[-1] if "_t" in out_p.stem[len(j["slug"]):] else "1", "prompt": j["prompt"],
                "rendered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **meta})
            manifest_p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  ✓ {out_p.relative_to(REPO)} ({len(img)//1024} KB)")
    print(f"done: {done} rendered, {fails} failed → {out_dir.relative_to(REPO)}")
    return 1 if fails and not done else 0


if __name__ == "__main__":
    sys.exit(main())
