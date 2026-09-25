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

## The files

| file | what |
|---|---|
| `strips/*.json` | the scripts. One strip per file. Schema below. |
| `eras.json` | per-era style blocks (line, paper, palette, prompt prefix/suffix, negative, Blender Freestyle settings), the formats, the margin marks |
| `heroes_vol10.json` | the cast as Meshy hero slots with text-to-3D prompts, and the locale builds the sets will need — for the production pipeline |
| `comic_tool.py` | `validate` · `index` · `md` · `strip-prompts` · `prompts` · `stage` · `new` |
| `comic_render.py` | the runner: `--provider runway` (gen4_image on the dev API) or `--provider google` (Imagen 4, or `--model gemini-2.5-flash-image`) |
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
