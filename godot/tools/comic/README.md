# COMIC · Drift Wood / ROFLCOPTER pipeline (vol 10)

Turns strip scripts into comic strips. Two paths, in the order we
are using them:

1. **The concept run (now).** One prompt per strip describing the
   whole strip — layout, era style, every panel, the balloons, the
   signature — sent to an image generator (Runway or Google). You
   get actual comic strips back, lettered by the model. Judge the
   look here.
2. **The production pipeline (later, once the look is approved).**
   Per-panel art with no lettering, composited with real balloons
   and the margin mark; optionally staged in Blender with the Meshy
   hero GLBs (`heroes_vol10.json`) for consistent characters and
   sets. The hooks are in the schema (`stage`) and the tool
   (`prompts`, `stage`); the Blender renderer is not written yet.

```
strips/*.json  ──comic_tool.py──▶  out/strip_prompts.json  ──comic_render.py──▶  godot/assets/comic/vol10/<provider>/*.png
                       │                                                            + manifest.json
                       ├─▶ lore/drift_wood/scripts/*.md   (readable script sheets, committed)
                       ├─▶ out/prompts.json               (per-panel, unlettered — production)
                       └─▶ out/stage.json                 (Blender staging — production)
```

## Quick start (the concept run)

```bash
cd /home/deck/Downloads/modern-mythology && git pull origin main && cd godot/tools/comic && python3 comic_tool.py validate && python3 comic_tool.py strip-prompts && python3 comic_render.py --provider runway --dry-run
```

Then, with a key in place (`godot/tools/.runway_key`, the same file
`runway_render.py` uses; or `godot/tools/.google_key`):

```bash
cd /home/deck/Downloads/modern-mythology/godot/tools/comic && python3 comic_render.py --provider runway --only "dw_2001*" --variants 2
```

```bash
cd /home/deck/Downloads/modern-mythology/godot/tools/comic && python3 comic_render.py --provider google --model gemini-2.5-flash-image --only "dw_2014-12-21*"
```

Outputs land in `godot/assets/comic/vol10/<provider>/` with a
manifest. Nothing is overwritten unless `--overwrite`. Concept
renders made through the Runway MCP from a Claude session are saved
under `godot/assets/comic/vol10/concept/` with their own manifest.

## The inspector (browse + generate on your machine)

```bash
cd /home/deck/Downloads/modern-mythology && git pull origin main && python3 godot/tools/comic/comic_inspector.py --open
```

One stdlib script, no install. It serves `http://127.0.0.1:8765/`
over the run on disk:

- **STRIPS** — every strip, filterable by year / strip / format /
  tier / rendered / review; per strip the script sheet, the panels,
  the whole-strip prompt (lettered and unlettered, copyable), the
  references each provider would attach, every render on disk
  (`godot/assets/comic/vol10/{runway,google,concept}/`), and the
  raw JSON. `j`/`k` walk the list, `1`–`6` switch tabs, `/` searches.
- **GENERATE** (RENDERS tab) — provider, model, variants, seed,
  letter / references / draft-refs / overwrite / dry-run; it runs
  `comic_tool.py strip-prompts` then `comic_render.py` for that one
  strip, streams the log under JOBS, and the image appears in the
  gallery when it lands. Same outputs and manifests as the CLI.
  Keys as before: `godot/tools/.runway_key` / `.google_key` or the env.
- **Review** — mark a strip *ok* / *revise* with a note. It's written
  into the strip JSON as a `review` block (the validator ignores it,
  the md sheet shows it), so it travels with a commit and I see it.
- **SHEETS** — the 36 reference sheets with their status and renders;
  generate one, then approve it, and it becomes attachable.
- **REFS** — the registry, approve / reject / draft.

## The files

| file | what |
|---|---|
| `strips/*.json` | the scripts. One strip per file. Schema below. |
| `eras.json` | per-era style blocks (line, paper, palette, prompt prefix/suffix, negative, Blender Freestyle settings), the formats, the margin marks |
| `heroes_vol10.json` | the cast as Meshy hero slots with text-to-3D prompts, and the locale builds the sets will need — for the production pipeline |
| `comic_tool.py` | `validate` · `index` · `md` · `strip-prompts` · `sheets` · `prompts` · `stage` · `new` |
| `references.json` | the tagged reference-image registry and the auto-selection policy (see References below) |
| `style_sheets.json` | the reference-sheet queue (characters by era, era swatches, hero locations, objects); `comic_tool.py sheets` composes the prompts; the human guides are `lore/drift_wood/style/` |
| `comic_render.py` | the runner: `--provider runway` (gen4_image on the dev API) or `--provider google` (Imagen 4, or `--model gemini-2.5-flash-image`) |
| `comic_inspector.py` | the local page: browse every strip, sheet and reference with their renders; generate one at a time through the two scripts above; mark strips for revision |
| `out/` | generated queues (gitignored) |

## Strip schema (strips/*.json)

```jsonc
{
  "id": "dw_2001-10-09_lot_c",        // dw_ Drift Wood · rc_ the ROLFCOPTR parody · ro_ ROFLCOPTER
  "title": "Lot C",
  "strip": "drift_wood",              // drift_wood | rolfcoptr | roflcopter
  "date": "2001-10-09",               // the in-fiction run date
  "run": 2, "era": "era1",            // see eras.json
  "format": "daily4",                 // biweekly | daily4 | daily3 | digest_cover | special | sunday | page | spread
  "tier": "B",                        // A drawn · B scripted · C implied  (lore/drift_wood/_THE_COMPLETE_RUN.md)
  "selection": "full",                // full | part | one | index
  "venue": "...", "arc": "...", "source": "...", "logline": "...",
  "cast": ["wood_20", "security_guard"],   // ids from heroes_vol10.json (extra_* for one-offs)
  "location": "dw_newport_lot",
  "margin": {"signature": "A. Finch — Small Wood, OR", "mark": "gull", "note": ""},
  "panels": [
    {
      "n": 1, "shot": "wide", "name": "",            // name is used for Sunday tiers
      "composition": "what is in the panel, for a human",
      "characters": [{"id": "wood_20", "pose": "...", "expression": "...", "at": [0,0,0], "facing": "-Y"}],
      "props": ["..."],
      "balloons": [{"who": "WOOD", "text": "...", "kind": "small|sfx"}],
      "caption": "", "sfx": "",
      "image": {"prompt": "the generation note for THIS panel (no style words — eras.json adds them)",
                "negative": "", "notes": "", "seed": null, "references": []},
      "stage": null                                  // or {"locale": "dw_frame_shop", "camera": {...}, "sun": {...}}
    }
  ],
  "art": {"line": "", "palette": "", "paper": ""},   // overrides for this strip (the Sunday specs use these)
  "notes": ""
}
```

Rules the validator enforces: ids and dates well-formed; format
panel counts; marks from `eras.json`; every panel has a composition
and an image prompt; **no character id beginning `arthur`** — the
author is never on the page (`lore/drift_wood/_AUTHORIAL_RULE.md`).

## How the whole-strip prompt is built

`strip-prompts` composes, per strip:

> *layout sentence for the format* · **Style:** *era prefix* · **Title
> / logline** · **Panel 1:** *panel image prompt* + *"Wood says
> '…'"* · … · **margin:** *the signature and the mark*

Lettering is asked of the generator on purpose for the concept run.
`--no-letter` produces the same prompts with balloons stripped and
"no text" added, for the production path where lettering is
composited.

Long balloons garble. For the concept run pick strips with short
dialogue or none: `dw_2001-10-09_lot_c`, `dw_2003-05-23_the_rack`,
`dw_2005-03-16_one_sack`, `dw_2009-03-08_lanes` (silent Sunday),
`dw_2014-11-30_empty_chair` (silent), `dw_2020-12-27_last_sunday`.

## Providers

- **Runway (dev API).** `text_to_image`, model `gen4_image`, ratios
  from the strip format (`2112:912` for a daily row, `1080:1440` for
  a Sunday page). Key: `RUNWAYML_API_KEY` or `godot/tools/.runway_key`.
- **Google (Gemini API).** `imagen-4.0-generate-001:predict` by
  default; `--model gemini-2.5-flash-image` uses the Gemini image
  model, which letters text more reliably. Key: `GOOGLE_API_KEY` /
  `GEMINI_API_KEY` or `godot/tools/.google_key`.
- Both runners print the response body on a non-200 so field-name
  drift in the APIs is visible, not silent.

## References · tagged, auto-selected, future-proof

`references.json` is the registry of reference images: model sheets,
era swatches, location sheets, object sheets, approved strips, and
concept art. Each entry carries **tags** — hero ids (`wood_34`),
location ids (`dw_garage`), era ids (`era3`), object keywords
(`produce box`, `lamp`) — a `file` (repo path) and/or `url` /
`runway_task_id`, and a `status`: `missing` (expected, not yet
rendered), `draft` (exists, unreviewed), `approved` (use it).

**Automatic selection.** `strip-prompts` scores every approved
reference against each strip — its `cast`, `location`, `era`, `arc`
and the words in its props and compositions — and attaches the top
three (Runway) or four (Google) as `reference_images`, adding
"Match the attached references: @wood_34 for the character; @garage
for the setting; …" to the prompt. A strip's own earlier render is
never used as its own reference. Weights and limits are in
`references.json` → `policy`.

**Manual selection.** A strip JSON can carry:

```jsonc
"references": {"use": ["sheet_wood_34", "sheet_loc_garage"], "exclude": ["concept_*"], "auto": true}
```

`use` pins; `exclude` blocks; `auto: false` turns off scoring for
that strip.

**Commands.**

```bash
cd /home/deck/Downloads/modern-mythology/godot/tools/comic && python3 comic_tool.py refs list
```

```bash
cd /home/deck/Downloads/modern-mythology/godot/tools/comic && python3 comic_tool.py refs suggest --only "dw_2014*"
```

```bash
cd /home/deck/Downloads/modern-mythology/godot/tools/comic && python3 comic_tool.py sheets && python3 comic_render.py --provider runway --queue out/sheets.json --only "sheet_wood_*" && python3 comic_tool.py refs sync && python3 comic_tool.py refs approve --id "sheet_wood_*"
```

```bash
cd /home/deck/Downloads/modern-mythology/godot/tools/comic && python3 comic_tool.py refs add --file lore/drift_wood/refs/sheet_01_wood.png --kind concept --tags "wood_44,the_bird,era4,dw_gullys" --approve
```

The loop: render sheets → `refs sync` (registers what now exists as
draft) → look → `refs approve` → from then on every `strip-prompts`
run attaches them where relevant. `refs suggest` shows the picks
before spending anything; `--include-draft` previews with
unreviewed sheets.

**How the renderers use them.** Runway (dev API): local files are
sent as data URIs with their `@tag`; URLs pass through; an entry
that is only a Runway task id (an MCP-hosted image) is skipped with
a note until its PNG is fetched. Google: `gemini-2.5-flash-image`
receives them as inline image parts; Imagen ignores references.
Sheet renders land in `godot/assets/comic/vol10/sheets/` with their
tags in the manifest, which is what `refs sync` reads.

**Future-proofing.** Tags are free strings, so new kinds (a pose
sheet, a lettering sample, a real photo of Alsea Bay) register
without code changes; `kind` and `prefer_kinds` order ties; the
Blender/Meshy path can register its rendered stills as `strip`
references the same way. Nothing in a strip JSON refers to a file —
only to ids and tags — so references can be re-rendered, replaced or
moved without touching the scripts.

## Adding a strip

```bash
cd /home/deck/Downloads/modern-mythology/godot/tools/comic && python3 comic_tool.py new --id dw_2002-06-07_corner_box --date 2002-06-07 --format digest_cover --era era1 --run 2 --title "The corner box"
```

Fill the JSON; the per-year content is in
`lore/drift_wood/_SCOPE_AND_YEARS.md` and the arc catalogue in
`lore/drift_wood/_THE_COMPLETE_RUN.md`. Run `validate`, then `md` to
regenerate the readable sheets, and commit both.

## Later · the production pipeline

- `prompts` gives per-panel, unlettered jobs; a compositor (the
  studio page, to be written) lays them into the format's grid on
  the era's paper and letters the balloons from `letter_after`.
- `stage` gives Blender jobs: locale GLB + hero GLBs + camera +
  the era's Freestyle line settings. `heroes_vol10.json` holds the
  Meshy prompts for every cast member at every age; install the
  GLBs with `godot/tools/hero_uploader/` (add the vol 10 rows when
  that phase starts). Coordinates follow the playbook's Blender
  Z-up frame.
