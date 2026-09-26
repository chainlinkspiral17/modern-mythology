#!/usr/bin/env python3
"""comic_tool.py — the Drift Wood / ROFLCOPTER strip pipeline (vol 10).

Strip scripts live as JSON in godot/tools/comic/strips/ (schema in
README.md). This tool turns them into the things production needs:

  validate   check every strip against the schema + eras.json
  index      print (or write) the catalogue: per year / run / format / tier
  md         write readable script sheets (markdown) — one per strip plus
             an index — into lore/drift_wood/scripts/ so the writing is
             reviewable without running anything
  strip-prompts
             write ONE prompt per strip describing the whole strip as a single
             image (layout, era style, every panel, the balloons, the signature).
             This is the concept-run path: comic_render.py sends these to
             Runway or Google and you get actual comic strips back.
  refs       the tagged reference registry (references.json): list · sync
             (pick up rendered sheets / files that now exist) · add · approve ·
             reject · suggest <strips> (show what strip-prompts would attach).
             strip-prompts attaches up to 3 approved references per strip by
             cast / location / era / object tags, unless the strip JSON has a
             "references": {"use": [...], "exclude": [...], "auto": true} block.
  sheets     write one prompt per reference sheet (characters by era, era
             swatches, hero locations, objects) from style_sheets.json —
             the generation side of lore/drift_wood/style/.
  prompts    write an image-generation queue (JSON) — one job per panel:
             era prefix + panel prompt + era suffix, negative, size, seed.
             Consumed by comic_studio.html or any 2D generator runner.
  stage      write a Blender staging queue (JSON) for build_strip_panel.py:
             per panel, the locale GLB, the hero GLBs (the Meshy pipeline),
             positions/facings, the camera, and the era's Freestyle settings
  new        scaffold a new strip JSON from a few args

Stdlib only. Usage:

  python3 godot/tools/comic/comic_tool.py validate
  python3 godot/tools/comic/comic_tool.py index
  python3 godot/tools/comic/comic_tool.py md
  python3 godot/tools/comic/comic_tool.py prompts [--only "dw_2014*"] [--out out/prompts.json]
  python3 godot/tools/comic/comic_tool.py stage   [--only "dw_2014*"] [--out out/stage.json]
  python3 godot/tools/comic/comic_tool.py new --id dw_2001-10-09_lot_c --date 2001-10-09 \
          --format daily4 --era era1 --run 2 --title "Lot C"
"""
import argparse
import fnmatch
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
STRIPS = HERE / "strips"
OUT = HERE / "out"
ERAS_PATH = HERE / "eras.json"
HEROES_PATH = HERE / "heroes_vol10.json"
MD_OUT = REPO / "lore" / "drift_wood" / "scripts"

STRIP_NAMES = {"drift_wood", "rolfcoptr", "roflcopter"}
FORMATS = {"biweekly", "daily4", "daily3", "digest_cover", "special", "sunday", "page", "spread"}
TIERS = {"A", "B", "C"}
SELECTIONS = {"full", "part", "one", "index"}
ID_RE = re.compile(r"^(dw|rc|ro)_(\d{4})-(\d{2})-(\d{2})_[a-z0-9_]+$")


# ── loading ──────────────────────────────────────────────────────────────

def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_eras():
    return load_json(ERAS_PATH)


def load_heroes():
    return load_json(HEROES_PATH) if HEROES_PATH.exists() else {"heroes": {}}


def load_strips(only=None):
    strips = []
    for p in sorted(STRIPS.glob("*.json")):
        if only and not fnmatch.fnmatch(p.stem, only):
            continue
        try:
            d = load_json(p)
        except json.JSONDecodeError as e:
            print(f"✗ {p.name}: bad JSON — {e}", file=sys.stderr)
            continue
        d["_file"] = p.name
        strips.append(d)
    strips.sort(key=lambda s: (s.get("date", ""), s.get("id", "")))
    return strips


# ── validate ─────────────────────────────────────────────────────────────

def validate_strip(s, eras, heroes):
    errs = []
    sid = s.get("id", "<no id>")
    if not ID_RE.match(sid):
        errs.append(f"id '{sid}' must look like dw_YYYY-MM-DD_slug (dw|rc|ro)")
    if s.get("strip") not in STRIP_NAMES:
        errs.append(f"strip must be one of {sorted(STRIP_NAMES)}")
    if s.get("format") not in FORMATS:
        errs.append(f"format must be one of {sorted(FORMATS)}")
    if s.get("era") not in eras["eras"]:
        errs.append(f"era must be one of {sorted(eras['eras'])}")
    if s.get("tier") not in TIERS:
        errs.append("tier must be A, B or C")
    if s.get("selection", "full") not in SELECTIONS:
        errs.append(f"selection must be one of {sorted(SELECTIONS)}")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s.get("date", "")):
        errs.append("date must be YYYY-MM-DD")
    if sid.startswith("dw_") and s.get("strip") != "drift_wood":
        errs.append("dw_ ids are Drift Wood")
    if sid.startswith("ro_") and s.get("strip") != "roflcopter":
        errs.append("ro_ ids are ROFLCOPTER")
    mark = (s.get("margin") or {}).get("mark")
    if mark and mark not in eras["marks"]:
        errs.append(f"margin.mark '{mark}' not in eras.json marks")
    panels = s.get("panels") or []
    if not panels:
        errs.append("no panels")
    fmt = s.get("format")
    want = eras["formats"].get(fmt, {}).get("panels")
    if isinstance(want, int) and len(panels) != want:
        errs.append(f"format {fmt} wants {want} panels, has {len(panels)}")
    hero_ids = set(heroes.get("heroes", {}))
    for i, p in enumerate(panels, 1):
        if p.get("n") != i:
            errs.append(f"panel {i}: n should be {i}")
        if not p.get("composition"):
            errs.append(f"panel {i}: composition required")
        img = p.get("image") or {}
        if not img.get("prompt"):
            errs.append(f"panel {i}: image.prompt required (the generation note)")
        for c in p.get("characters") or []:
            cid = c.get("id")
            if hero_ids and cid and cid not in hero_ids and not cid.startswith("extra_"):
                errs.append(f"panel {i}: character '{cid}' not in heroes_vol10.json (prefix extra_ for one-offs)")
        for b in p.get("balloons") or []:
            if not b.get("who") or "text" not in b:
                errs.append(f"panel {i}: balloon needs who + text")
    # the rule: the author never appears
    for p in panels:
        for c in p.get("characters") or []:
            if (c.get("id") or "").startswith("arthur"):
                errs.append("the author is on the page — draw Wood, or the margin, or the gap (_AUTHORIAL_RULE.md)")
    return errs


def cmd_validate(args):
    eras, heroes = load_eras(), load_heroes()
    strips = load_strips(args.only)
    bad = 0
    ids = Counter(s.get("id") for s in strips)
    for s in strips:
        errs = validate_strip(s, eras, heroes)
        if ids[s.get("id")] > 1:
            errs.append("duplicate id")
        if errs:
            bad += 1
            print(f"✗ {s['_file']}")
            for e in errs:
                print(f"    - {e}")
    print(f"{len(strips) - bad}/{len(strips)} strips valid")
    return 1 if bad else 0


# ── index ────────────────────────────────────────────────────────────────

def cmd_index(args):
    strips = load_strips(args.only)
    by_year = defaultdict(list)
    for s in strips:
        by_year[s["date"][:4]].append(s)
    tiers = Counter(s.get("tier") for s in strips)
    fmts = Counter(s.get("format") for s in strips)
    print(f"{len(strips)} strips · tiers {dict(tiers)} · formats {dict(fmts)}")
    for y in sorted(by_year):
        print(f"\n{y}")
        for s in by_year[y]:
            print(f"  {s['date']}  {s['id']:<44} {s.get('format','?'):<12} {s.get('tier','?')}  {s.get('title','')}")
    return 0


# ── prompts (2D image generation) ────────────────────────────────────────

def compose_prompt(s, p, eras):
    era = eras["eras"][s["era"]]
    img = p.get("image") or {}
    prefix = era["prompt_prefix"]
    if s.get("format") in ("sunday", "page", "spread", "special") and era.get("prompt_prefix_sunday"):
        prefix = era["prompt_prefix_sunday"]
    if img.get("prefix_override"):
        prefix = img["prefix_override"]
    prompt = f"{prefix} {img.get('prompt','').strip()}{era['prompt_suffix']}"
    negative = era["negative"]
    if img.get("negative"):
        negative = f"{negative}, {img['negative']}"
    return re.sub(r"\s+", " ", prompt).strip(), negative


def panel_px(s, p, eras):
    fmt = eras["formats"].get(s.get("format"), {})
    if p.get("px"):
        return p["px"]
    w, h = fmt.get("px", [2000, 2000])
    n = fmt.get("panels")
    if isinstance(n, int) and n > 1 and s.get("format") in ("daily4", "daily3"):
        return [w // n, h]  # one square-ish panel of the strip
    if s.get("format") == "biweekly":
        return [w // 2, h // 2]
    return [w, h]


def cmd_prompts(args):
    eras = load_eras()
    strips = load_strips(args.only)
    jobs = []
    for s in strips:
        for p in s["panels"]:
            prompt, negative = compose_prompt(s, p, eras)
            jobs.append({
                "tag": "vol10",
                "strip_id": s["id"],
                "panel": p["n"],
                "slug": f"{s['id']}_p{p['n']}",
                "date": s["date"],
                "era": s["era"],
                "format": s["format"],
                "tier": s.get("tier"),
                "prompt": prompt,
                "negative": negative,
                "px": panel_px(s, p, eras),
                "seed": (p.get("image") or {}).get("seed"),
                "reference_images": (p.get("image") or {}).get("references", []),
                "notes": (p.get("image") or {}).get("notes", ""),
                "letter_after": {
                    "balloons": p.get("balloons", []),
                    "caption": p.get("caption", ""),
                    "sfx": p.get("sfx", ""),
                },
            })
    out = Path(args.out) if args.out else OUT / "prompts.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "_comment": "One job per panel. Generate the ART ONLY — lettering is composited afterwards (letter_after). Consumed by comic_studio.html or a runner.",
        "jobs": jobs}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(jobs)} prompt jobs → {out.relative_to(REPO)}")
    return 0


# ── references (tagged reference images, auto-selected per strip) ─────────

REFS_PATH = HERE / "references.json"


def load_refs():
    return load_json(REFS_PATH) if REFS_PATH.exists() else {"policy": {}, "references": []}


def save_refs(d):
    REFS_PATH.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _strip_terms(s):
    """Everything about a strip a reference tag could match: cast ids, location,
    era, arc, and lowercase words from props/composition."""
    words = set()
    for p in s.get("panels") or []:
        for pr in p.get("props") or []:
            words.update(w.strip(".,;:()\"'").lower() for w in pr.split())
        words.update(w.strip(".,;:()\"'").lower() for w in (p.get("composition") or "").split())
    return {"cast": set(s.get("cast") or []), "location": s.get("location") or "",
            "era": s.get("era"), "arc": s.get("arc") or "", "words": words, "id": s.get("id")}


def score_ref(ref, terms, weights):
    sc, why = 0, []
    tags = set(ref.get("tags") or [])
    for c in terms["cast"] & tags:
        sc += weights.get("character", 3); why.append(c)
    if terms["location"] and terms["location"] in tags:
        sc += weights.get("location", 2); why.append(terms["location"])
    if terms["era"] in tags:
        sc += weights.get("era", 1); why.append(terms["era"])
    if terms["arc"] and terms["arc"] in tags and ref.get("kind") == "strip":
        sc += weights.get("strip_same_arc", 1); why.append("same arc")
    GENERIC = {"strip", "character", "location", "era", "objects", "concept", "sheet", "mark", "logo"}
    for tg in tags:
        if tg in GENERIC or tg in terms["cast"] or tg.startswith(("dw_", "era", "extra_")):
            continue
        if " " in tg or tg.islower():
            # object keyword: match against the strip's words (multi-word tags need every word)
            if all(w in terms["words"] for w in tg.split()):
                sc += weights.get("object", 1); why.append(tg)
    if ref.get("id") == f"concept_{terms['id']}":
        sc = 0  # never use a strip's own earlier render as its reference
    return sc, why


def select_refs(s, refs, provider="runway", include_draft=False, verbose=False):
    """Return [(ref, score, why)] for a strip: the strip's explicit 'references'
    block wins; otherwise the top-N approved refs by tag relevance."""
    pol = refs.get("policy", {})
    weights = pol.get("weights", {})
    n = pol.get("max_refs", {}).get(provider, 3)
    by_id = {r["id"]: r for r in refs.get("references", [])}
    block = s.get("references") or {}
    chosen = []
    for rid in block.get("use") or []:
        r = by_id.get(rid)
        if r:
            chosen.append((r, 99, ["pinned"]))
    if block.get("auto", True) and len(chosen) < n:
        terms = _strip_terms(s)
        exclude = set(block.get("exclude") or []) | {c[0]["id"] for c in chosen}
        cands = []
        for r in refs.get("references", []):
            if r["id"] in exclude:
                continue
            ok = r.get("status") == "approved" or (include_draft and r.get("status") == "draft")
            if not ok or not (r.get("file") or r.get("url") or r.get("runway_task_id")):
                continue
            sc, why = score_ref(r, terms, weights)
            if sc > 0:
                cands.append((r, sc, why))
        order = {k: i for i, k in enumerate(pol.get("prefer_kinds", []))}
        cands.sort(key=lambda c: (-c[1], order.get(c[0]["kind"], 9), c[0]["id"]))
        chosen += cands[: n - len(chosen)]
    return chosen[:n]


def ref_tag_name(ref):
    """The @tag used in the prompt for a reference (Runway syntax)."""
    return re.sub(r"[^a-z0-9]+", "_", ref["id"].replace("sheet_", "").replace("concept_", "")).strip("_")[:24]


def cmd_refs(args):
    refs = load_refs()
    sub = args.refs_cmd
    if sub == "list":
        for r in refs["references"]:
            if args.status and r.get("status") != args.status:
                continue
            where = r.get("file") or r.get("url") or (f"runway:{r['runway_task_id']}" if r.get("runway_task_id") else "—")
            print(f"{r['status']:<9} {r['kind']:<10} {r['id']:<36} {where}")
            print(f"           tags: {', '.join(r.get('tags') or [])}")
        print(f"{len(refs['references'])} references")
        return 0
    if sub == "sync":
        # flip 'missing' → 'draft' when the file now exists; register rendered sheets from the manifest
        flipped = 0
        for r in refs["references"]:
            f = r.get("file")
            if f and (REPO / f).exists() and r.get("status") == "missing":
                r["status"] = "draft"; flipped += 1
        man = REPO / "godot" / "assets" / "comic" / "vol10" / "sheets" / "manifest.json"
        if man.exists():
            ids = {r["id"] for r in refs["references"]}
            for m in load_json(man).get("renders", []):
                if m["slug"] not in ids:
                    refs["references"].append({"id": m["slug"], "kind": m.get("kind", "sheet"), "tags": m.get("tags", []),
                                               "file": m["file"], "url": None, "runway_task_id": m.get("task_id"),
                                               "status": "draft", "source": "sheets render", "notes": ""})
        save_refs(refs)
        print(f"synced: {flipped} now present (draft)")
        return 0
    if sub == "add":
        rid = args.id or re.sub(r"[^a-z0-9]+", "_", Path(args.file).stem.lower())
        refs["references"] = [r for r in refs["references"] if r["id"] != rid]
        f = Path(args.file)
        try:
            rel = str(f.resolve().relative_to(REPO))
        except ValueError:
            rel = str(f)
        refs["references"].append({"id": rid, "kind": args.kind, "tags": args.tags.split(",") if args.tags else [],
                                   "file": rel if not args.file.startswith("http") else None,
                                   "url": args.file if args.file.startswith("http") else None, "runway_task_id": args.task,
                                   "status": "approved" if args.approve else "draft", "source": "manual", "notes": args.notes or ""})
        save_refs(refs)
        print(f"added {rid} ({'approved' if args.approve else 'draft'})")
        return 0
    if sub in ("approve", "reject"):
        hit = 0
        for r in refs["references"]:
            if fnmatch.fnmatch(r["id"], args.id):
                r["status"] = "approved" if sub == "approve" else "draft"; hit += 1
        save_refs(refs)
        print(f"{sub}d {hit}")
        return 0
    if sub == "suggest":
        strips = load_strips(args.only)
        for s in strips:
            picks = select_refs(s, refs, provider=args.provider, include_draft=args.include_draft)
            print(f"{s['id']}")
            for r, sc, why in picks:
                print(f"    {sc:>3}  @{ref_tag_name(r):<24} {r['id']:<34} [{r['status']}]  {', '.join(why)}")
            if not picks:
                print("    (no matching references — render and approve sheets, or pin with a 'references' block)")
        return 0
    return 1


# ── strip prompts (whole-strip generation: the concept run) ──────────────

RATIOS = {
    # format → (runway ratio, google aspect) for one image of the whole strip
    "daily4": ("2112:912", "16:9"),
    "daily3": ("1808:768", "16:9"),
    "biweekly": ("1168:880", "4:3"),
    "digest_cover": ("1080:1440", "3:4"),
    "special": ("1080:1440", "3:4"),
    "sunday": ("1080:1440", "3:4"),
    "page": ("1080:1440", "3:4"),
    "spread": ("1920:1080", "16:9"),
}

LAYOUT_TEXT = {
    "daily4": "a four-panel newspaper comic strip, four equal panels in a single horizontal row with thin black gutters",
    "daily3": "a three-panel newspaper comic strip, three equal panels in a single horizontal row with thin black gutters",
    "biweekly": "a four-panel comic strip laid out as a two-by-two grid on a half page, thin black panel borders",
    "digest_cover": "a single-image zine cover, one drawing filling the page",
    "special": "a full-page comic in horizontal tiers stacked top to bottom",
    "sunday": "a full-page Sunday comic in horizontal tiers stacked top to bottom, each tier one wide panel",
    "page": "a single full-page comic drawing",
    "spread": "a two-page comic spread as one wide image",
}


def _balloon_text(p):
    out = []
    for b in p.get("balloons") or []:
        kind = b.get("kind", "")
        if kind == "sfx":
            out.append(f"on-screen text reads \"{b['text']}\"")
        elif kind == "small":
            out.append(f"{b['who'].title()} says, in a small balloon, \"{b['text']}\"")
        else:
            out.append(f"{b['who'].title()} says \"{b['text']}\"")
    if p.get("caption"):
        out.append(f"caption box: \"{p['caption']}\"")
    return ". ".join(out)


def compose_strip_prompt(s, eras, letter=True):
    """One prompt for the WHOLE strip as a single image: layout, era style,
    then each panel's content in order, with the dialogue if letter=True
    (the concept run lets the generator letter the balloons; the print
    pipeline will composite them instead)."""
    era = eras["eras"][s["era"]]
    fmt = s["format"]
    style = era["prompt_prefix"].rstrip(",")
    if fmt in ("sunday", "page", "spread", "special") and era.get("prompt_prefix_sunday"):
        style = era["prompt_prefix_sunday"].rstrip(",")
    n = len(s["panels"])
    unit = "tier" if fmt in ("sunday", "special") else "panel"
    parts = [f"{LAYOUT_TEXT.get(fmt, 'a comic strip')} ({n} {unit}s). Style: {style}."]
    if s.get("logline"):
        parts.append(f"Title of the strip: {s['strip'].replace('_', ' ').upper()}. The strip: {s['logline']}")
    for p in s["panels"]:
        seg = f"{unit.title()} {p['n']}: {(p.get('image') or {}).get('prompt') or p['composition']}"
        if letter:
            bt = _balloon_text(p)
            if bt:
                seg += f". {bt}"
            else:
                seg += ". No dialogue in this " + unit
        parts.append(seg + ".")
    m = s.get("margin") or {}
    if letter and m.get("signature"):
        mark = eras["marks"].get(m.get("mark", ""), "")
        parts.append(f"In the bottom right margin, tiny hand-lettered signature \"{m['signature']}\"" + (f" beside {mark}" if mark and m.get("mark") != "none" else "") + ".")
    if not letter:
        parts.append("No text, no lettering, no speech balloons, no signature; leave clean space in each panel where balloons would go.")
    prompt = " ".join(parts)
    negative = era["negative"]
    if not letter:
        negative += ", text, letters"
    else:
        negative = ", ".join(x for x in negative.split(", ") if x not in ("text", "letters", "signature"))
    return re.sub(r"\s+", " ", prompt).strip(), negative


def cmd_strip_prompts(args):
    eras = load_eras()
    strips = load_strips(args.only)
    letter = not args.no_letter
    jobs = []
    refs = load_refs() if not args.no_refs else {"policy": {}, "references": []}
    with_refs = 0
    for s in strips:
        prompt, negative = compose_strip_prompt(s, eras, letter=letter)
        rw, gg = RATIOS.get(s["format"], ("1024:1024", "1:1"))
        picks = select_refs(s, refs, provider=args.provider, include_draft=args.include_draft) if not args.no_refs else []
        ref_list = []
        if picks:
            with_refs += 1
            mentions = []
            for r, sc, why in picks:
                tag = ref_tag_name(r)
                ref_list.append({"tag": tag, "id": r["id"], "kind": r["kind"], "file": r.get("file"), "url": r.get("url"),
                                 "runway_task_id": r.get("runway_task_id"), "score": sc, "why": why})
                what = {"character": "the character", "location": "the setting", "era": "the drawing style", "objects": "the objects",
                        "strip": "a finished strip in this style", "concept": "the concept design"}.get(r["kind"], "reference")
                mentions.append(f"@{tag} for {what}")
            prompt = prompt + " Match the attached references: " + "; ".join(mentions) + "."
        jobs.append({
            "tag": "vol10", "slug": s["id"], "strip_id": s["id"], "title": s.get("title", ""),
            "date": s["date"], "era": s["era"], "format": s["format"], "tier": s.get("tier"),
            "prompt": prompt, "negative": negative,
            "runway_ratio": rw, "google_aspect": gg,
            "lettered": letter, "seed": s.get("seed"),
            "reference_images": ref_list,
        })
    out = Path(args.out) if args.out else OUT / ("strip_prompts.json" if letter else "strip_prompts_unlettered.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "_comment": "One job per STRIP — the whole strip as one image, for the concept run. Run with comic_render.py --provider runway|google.",
        "jobs": jobs}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(jobs)} strip prompts → {out.relative_to(REPO)}")
    return 0


# ── sheets (reference / model sheets) ────────────────────────────────────

SHEETS_PATH = HERE / "style_sheets.json"


def cmd_sheets(args):
    """One prompt per reference sheet: the era's style block + the sheet
    prompt from style_sheets.json (sources: lore/drift_wood/style/*.md)."""
    eras = load_eras()
    data = load_json(SHEETS_PATH)
    jobs = []
    for sh in data["sheets"]:
        if args.only and not fnmatch.fnmatch(sh["id"], args.only):
            continue
        era = eras["eras"][sh["era"]]
        style = era["prompt_prefix"].rstrip(",")
        prompt = (f"a clean reference sheet on white paper. Style: {style}. "
                  f"{sh['prompt']}. Neat hand-lettered labels are allowed on this sheet.")
        jobs.append({"tag": "vol10-sheets", "slug": sh["id"], "kind": sh["kind"], "era": sh["era"], "tags": sh.get("tags", []),
                     "prompt": re.sub(r"\s+", " ", prompt).strip(),
                     "negative": ", ".join(x for x in era["negative"].split(", ") if x not in ("text", "letters", "signature")),
                     "runway_ratio": {"16:9": "1920:1080", "3:4": "1080:1440"}.get(sh.get("ratio", "16:9"), "1920:1080"),
                     "google_aspect": sh.get("ratio", "16:9"), "lettered": True})
    out = Path(args.out) if args.out else OUT / "sheets.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"_comment": "Reference sheets. Render with comic_render.py --queue out/sheets.json.", "jobs": jobs}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(jobs)} sheet prompts → {out.relative_to(REPO)}")
    return 0


# ── stage (Blender / Meshy hero pipeline) ────────────────────────────────

def cmd_stage(args):
    eras, heroes = load_eras(), load_heroes()
    strips = load_strips(args.only)
    jobs = []
    skipped = 0
    for s in strips:
        era = eras["eras"][s["era"]]
        for p in s["panels"]:
            st = p.get("stage")
            if not st:
                skipped += 1
                continue
            hero_jobs = []
            for c in p.get("characters") or []:
                h = heroes.get("heroes", {}).get(c.get("id"))
                if not h:
                    continue
                hero_jobs.append({
                    "id": c["id"],
                    "glb": h["file"],
                    "at": c.get("at", [0.0, 0.0, 0.0]),
                    "facing": c.get("facing", "-Y"),
                    "pose": c.get("pose", ""),
                    "expression": c.get("expression", ""),
                })
            jobs.append({
                "slug": f"{s['id']}_p{p['n']}",
                "strip_id": s["id"],
                "panel": p["n"],
                "locale": st.get("locale"),
                "locale_glb": f"godot/assets/3d/locales/{st.get('locale')}.glb" if st.get("locale") else None,
                "camera": st.get("camera", {"pos": [0, -4, 1.6], "look_at": [0, 0, 1.2], "fov": 35}),
                "sun": st.get("sun", {"azimuth": 225, "elevation": 35, "energy": 3.0}),
                "heroes": hero_jobs,
                "props": st.get("props", []),
                "px": panel_px(s, p, eras),
                "freestyle": era["blender"],
                "composition_note": p.get("composition", ""),
            })
    out = Path(args.out) if args.out else OUT / "stage.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "_comment": "Blender staging queue for build_strip_panel.py. Coordinates are Blender Z-up meters in the locale's frame (see lore/_3D_MODELING_PLAYBOOK.md 'Coordinate frame'). Heroes are the Meshy GLBs in godot/assets/3d/characters/heroes/.",
        "jobs": jobs}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(jobs)} staging jobs → {out.relative_to(REPO)} ({skipped} panels had no stage block)")
    return 0


# ── md (readable script sheets) ──────────────────────────────────────────

def strip_to_md(s, eras):
    era = eras["eras"][s["era"]]
    fmt = eras["formats"].get(s["format"], {})
    m = s.get("margin") or {}
    lines = []
    lines.append(f"# {s.get('title', s['id'])}")
    lines.append("")
    lines.append(f"`{s['id']}` · **{s['strip'].replace('_', ' ').upper()}** · {s['date']} · "
                 f"{s['format']} ({fmt.get('layout', '')}) · run {s.get('run', '?')} · "
                 f"{era['name']} · tier {s.get('tier', '?')} · selection {s.get('selection', 'full')}")
    if s.get("venue"):
        lines.append(f"Venue: {s['venue']}" + (f" · arc: *{s['arc']}*" if s.get("arc") else ""))
    if s.get("logline"):
        lines.append("")
        lines.append(f"*{s['logline']}*")
    lines.append("")
    lines.append(f"**Line.** {s.get('art', {}).get('line') or era['line']}  ")
    lines.append(f"**Palette.** {s.get('art', {}).get('palette') or era['palette']}  ")
    lines.append(f"**Paper.** {s.get('art', {}).get('paper') or era['paper']}")
    if s.get("cast"):
        lines.append("")
        lines.append("Cast: " + ", ".join(f"`{c}`" for c in s["cast"]))
    lines.append("")
    lines.append("---")
    for p in s["panels"]:
        head = f"## Panel {p['n']}" if s["format"] not in ("sunday",) else f"## Tier {p['n']}"
        if p.get("name"):
            head += f" · {p['name']}"
        lines.append("")
        lines.append(head)
        lines.append("")
        if p.get("shot"):
            lines.append(f"*{p['shot']}.* {p['composition']}")
        else:
            lines.append(p["composition"])
        chars = p.get("characters") or []
        if chars:
            lines.append("")
            for c in chars:
                bits = [f"**{c['id']}**"]
                if c.get("pose"): bits.append(c["pose"])
                if c.get("expression"): bits.append(f"expression: {c['expression']}")
                lines.append("- " + " · ".join(bits))
        if p.get("props"):
            lines.append("")
            lines.append("Props: " + "; ".join(p["props"]))
        if p.get("balloons"):
            lines.append("")
            for b in p["balloons"]:
                kind = f" ({b['kind']})" if b.get("kind") else ""
                lines.append(f"> **{b['who']}**{kind}: {b['text']}")
        if p.get("caption"):
            lines.append("")
            lines.append(f"> *caption:* {p['caption']}")
        if p.get("sfx"):
            lines.append(f"> *sfx:* {p['sfx']}")
        img = p.get("image") or {}
        prompt, negative = compose_prompt(s, p, eras)
        lines.append("")
        lines.append("<details><summary>image generation</summary>")
        lines.append("")
        lines.append(f"**prompt.** {prompt}")
        lines.append("")
        lines.append(f"**negative.** {negative}")
        if img.get("notes"):
            lines.append("")
            lines.append(f"**notes.** {img['notes']}")
        if p.get("stage"):
            st = p["stage"]
            lines.append("")
            lines.append(f"**stage (Blender).** locale `{st.get('locale')}` · camera {st.get('camera')} · "
                         + ", ".join(f"{c['id']}@{c.get('at')} facing {c.get('facing','-Y')}" for c in chars if c.get("at")))
        lines.append("")
        lines.append("</details>")
    lines.append("")
    lines.append("---")
    lines.append("")
    sp, sneg = compose_strip_prompt(s, eras, letter=True)
    lines.append("<details><summary>whole-strip prompt (concept run)</summary>")
    lines.append("")
    lines.append(f"**prompt.** {sp}")
    lines.append("")
    lines.append(f"**negative.** {sneg}")
    lines.append("")
    lines.append("</details>")
    lines.append("")
    sig = m.get("signature", "")
    mark = m.get("mark", "")
    markdesc = eras["marks"].get(mark, "")
    lines.append(f"**Margin.** {sig}" + (f" · mark: *{mark}* — {markdesc}" if mark else ""))
    if m.get("note"):
        lines.append(f"  {m['note']}")
    if s.get("notes"):
        lines.append("")
        lines.append(f"*Notes.* {s['notes']}")
    if s.get("source"):
        lines.append("")
        lines.append(f"Source: {s['source']}")
    lines.append("")
    return "\n".join(lines)


def cmd_md(args):
    eras = load_eras()
    strips = load_strips(args.only)
    MD_OUT.mkdir(parents=True, exist_ok=True)
    index = ["# Drift Wood / ROFLCOPTER · scripts",
             "",
             "Generated by `godot/tools/comic/comic_tool.py md` from the strip JSONs in",
             "`godot/tools/comic/strips/`. Edit the JSON, not these files.",
             "",
             "| date | id | format | tier | title |",
             "|---|---|---|---|---|"]
    for s in strips:
        (MD_OUT / f"{s['id']}.md").write_text(strip_to_md(s, eras), encoding="utf-8")
        index.append(f"| {s['date']} | [`{s['id']}`]({s['id']}.md) | {s['format']} | {s.get('tier','')} | {s.get('title','')} |")
    (MD_OUT / "_INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"wrote {len(strips)} script sheets + _INDEX.md → {MD_OUT.relative_to(REPO)}")
    return 0


# ── new ──────────────────────────────────────────────────────────────────

def cmd_new(args):
    eras = load_eras()
    n = eras["formats"][args.format]["panels"]
    n = n if isinstance(n, int) else 1
    strip = "roflcopter" if args.id.startswith("ro_") else "rolfcoptr" if args.id.startswith("rc_") else "drift_wood"
    d = {
        "id": args.id, "title": args.title, "strip": strip, "date": args.date,
        "run": args.run, "era": args.era, "format": args.format, "tier": "B", "selection": "full",
        "venue": "", "arc": "", "source": "", "logline": "",
        "cast": [], "location": "",
        "margin": {"signature": "A. Finch — Small Wood, OR", "mark": "gull", "note": ""},
        "panels": [{"n": i + 1, "shot": "", "composition": "", "characters": [], "props": [],
                    "balloons": [], "caption": "", "sfx": "",
                    "image": {"prompt": "", "negative": "", "notes": ""},
                    "stage": None} for i in range(n)],
        "art": {"line": "", "palette": "", "paper": ""},
        "notes": "",
    }
    p = STRIPS / f"{args.id}.json"
    if p.exists():
        print(f"✗ {p.name} exists"); return 1
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"scaffolded {p.relative_to(REPO)}")
    return 0


# ── main ─────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("validate", cmd_validate), ("index", cmd_index), ("md", cmd_md),
                     ("prompts", cmd_prompts), ("stage", cmd_stage), ("strip-prompts", cmd_strip_prompts),
                     ("sheets", cmd_sheets)):
        sp = sub.add_parser(name)
        sp.add_argument("--only", help="glob on strip id, e.g. 'dw_2014*'")
        sp.add_argument("--out", help="output path (prompts/stage)")
        sp.add_argument("--no-letter", action="store_true", help="strip-prompts: art only, no balloons (for the print pipeline)")
        sp.add_argument("--no-refs", action="store_true", help="strip-prompts: don't attach reference images")
        sp.add_argument("--include-draft", action="store_true", help="strip-prompts/refs suggest: allow draft (unapproved) references")
        sp.add_argument("--provider", default="runway", choices=["runway", "google"], help="reference count limit per provider")
        sp.set_defaults(fn=fn)
    sp = sub.add_parser("refs", help="reference registry: list | sync | add | approve | reject | suggest")
    sp.add_argument("refs_cmd", choices=["list", "sync", "add", "approve", "reject", "suggest"])
    sp.add_argument("--status", help="list: filter by status")
    sp.add_argument("--file", help="add: local path or URL")
    sp.add_argument("--id", help="add/approve/reject: reference id (glob ok for approve/reject)")
    sp.add_argument("--kind", default="concept", choices=["character", "location", "era", "objects", "strip", "concept"])
    sp.add_argument("--tags", help="add: comma-separated tags (hero ids, dw_ location ids, era ids, object keywords)")
    sp.add_argument("--task", help="add: Runway task id (for MCP-hosted images)")
    sp.add_argument("--notes")
    sp.add_argument("--approve", action="store_true", help="add: mark approved immediately")
    sp.add_argument("--only", help="suggest: glob on strip id")
    sp.add_argument("--include-draft", action="store_true")
    sp.add_argument("--provider", default="runway", choices=["runway", "google"])
    sp.set_defaults(fn=cmd_refs)
    sp = sub.add_parser("new")
    sp.add_argument("--id", required=True)
    sp.add_argument("--date", required=True)
    sp.add_argument("--format", required=True, choices=sorted(FORMATS))
    sp.add_argument("--era", required=True)
    sp.add_argument("--run", required=True, type=int)
    sp.add_argument("--title", required=True)
    sp.set_defaults(fn=cmd_new)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
