# Hero Studio (was: Hero GLB Uploader)

One page that walks a roster entry through the whole 3D pipeline:

```
roster prompt ──► concept image (Google Gemini/Imagen or Runway) ──► Meshy image-to-3D ──► GLB at the canonical path
                  + optional side/back views (multi-image-to-3d)              heroes/ · demons/ · props/
```

The page is a front-end for `godot/tools/meshy_pipeline.py`. The roster
of **every VN character, demon slot and hero prop** lives in
`godot/tools/meshy_roster.json` — that file is the single source of
truth for names, canonical filenames, speaker keys and prompts.

## Run it (Steam Deck)

Keys go in gitignored files next to the script (or env vars). Only the
providers you use need a key. Paste them interactively — this prompts
for each one with hidden input, saves it, and tests it:

```bash
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py keys
```

(Do not `echo 'msy_...'` a placeholder into the file — `doctor` will
call that out as "not a key".)

Or paste them in the page: **KEYS** (top right) saves each key to those
files and tests it with one cheap authenticated call. To check from the
terminal (where each key was found, masked, and whether the provider
accepts it):

```bash
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py doctor
```

Common reasons a key "doesn't work":

- **Wrong kind of key.** Google needs a *Gemini API* key from
  <https://aistudio.google.com/apikey> (starts with `AIza`), not a
  Google Cloud service-account JSON or an OAuth client. Runway needs a
  *dev API* key from <https://dev.runwayml.com> (`key_…`), not the
  web-app login. Meshy keys come from <https://www.meshy.ai/api>
  (`msy_…`).
- **Pasted with decoration.** Quotes, `export NAME=…`, a `Bearer `
  prefix, CRLF or a BOM are all stripped automatically now.
- **Env var shadows the file.** If `MESHY_API_KEY` (etc.) is exported in
  the shell that runs the server, it wins over the file; `doctor` shows
  which one is being used.
- **File in the wrong place.** The files live next to the script:
  `godot/tools/.google_key`, `.runway_key`, `.meshy_key` — relative to
  the repo root, not your home directory.
- **No credits / not enabled.** `doctor` reports the credit balance
  (Meshy, Runway) or a 4xx from the provider with the reason.

Start the runner and open the page:

```bash
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py serve
```

→ <http://127.0.0.1:8765/hero_uploader/>. Header dots show which keys
were found. Stdlib only, no pip installs.

## Where the prompts come from

Image generation is grounded in the story text. Each roster entry
carries `canon`: verbatim sentences from the scene scripts
(`godot/resources/scenes/vol*/*.json`), the gauntlet data and the lore
that describe how the character or object looks. When quotes exist
they ARE the description sent to the image model ("The story describes
Sam Miller like this: …"); the hand-written `prompt` is only a fallback
for entries the text never describes (the page marks those *no canon*),
or extra direction if you tick *append*. Runway's 1000-character
prompt cap is respected automatically (short preamble, quotes trimmed
at a sentence boundary).

To find candidate quotes for an entry from the text:

```bash
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_canon.py sam_miller
```

`meshy_canon.py --write` stores candidates for entries that have none;
it is a keyword heuristic and over-collects, so read what it found
before spending credits. `--report` lists who still has nothing.

## Workflow in the page

1. **Pick** a character / prop on the left (filter by kind, volume,
   state; search by name, slug, key or tag).
2. **Description from the text** — the canon quotes are shown (with
   their sources) and editable per run; the style preamble for the kind
   (A-pose, flat grey background, etc.) is added automatically. Expand
   *full prompt as sent* to see exactly what the runner will send,
   including the Runway character count.
3. **Generate image** — choose provider + model + aspect + how many
   candidates. Tick *side + back views* to also render a profile and a
   back view from the chosen front (Gemini image models or Runway with a
   reference; Imagen can't take references). Candidates appear as
   thumbnails; click one to make it the chosen `front.png` / `side.png`
   / `back.png`. *Upload my own image* uses a hand-picked reference
   instead.
4. **Make 3D** — Meshy settings (standard vs smart-topology, textured
   PBR vs draft, texture resolution, pose). *Use side + back* sends all
   chosen views to `multi-image-to-3d`. The GLB is downloaded straight to
   `godot/assets/3d/characters/heroes/<file>` (or `demons/`, `props/`)
   and shows up in the viewer.
5. **Install / commit** — you can still drag any `.glb` onto the drop
   zone to install it under the canonical name (from Mixamo, RPM, the
   Meshy web app…). The page prints the git command to paste.
6. **Batch** — *batch command for this filter* prints a one-line
   `meshy_pipeline.py run …` for every visible entry, for overnight runs.

Jobs run one at a time in the runner; the Jobs panel tails their logs.

## CLI equivalents

```bash
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py list
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py run frasier_temple --provider google --multiview --texture
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py run demon --provider runway --model gen4_image --no-texture
cd /home/deck/Downloads/modern-mythology && python3 godot/tools/meshy_pipeline.py run all --dry-run
```

Selectors: slugs, globs (`vol6_*`, `the_*`), `vol5`/`vol6`/`vol7`,
`hero`/`demon`/`prop`, `all`. `--dry-run` prints prompts and costs
without spending anything. Outputs that already exist are skipped
unless `--overwrite`.

Concept candidates land in `godot/assets/concept/meshy/<slug>/`
(gitignored, like the Runway videos — curate what you keep). The GLBs
are committed as before.

## Offline mode

Opened straight from `file://` (no runner) the page falls back to the
old behaviour: install a dropped GLB via the File System Access API
(Chromium) or download-with-canonical-name (Firefox). Load the roster
with the *load meshy_roster.json…* button since browsers block
`file://` fetches across folders.

## Adding a character or prop

Add an entry to `godot/tools/meshy_roster.json` (schema is in the
file's `_schema` block). If the VN should route a speaker to the new
model, add its `keys` to `PORTRAIT_3D_KEY_TO_GLB` in
`godot/scenes/game/CharLayer.gd`; a missing GLB falls through to the 2D
portrait ladder so listing early is safe. World spawns in
`build_graustark.py` (`HERO_GLB_PATHS`) remain a separate concern.

Known key collisions (`carl`, `wren`, `nate`, `ben`, `margaret` mean
different people in different volumes) are called out in the roster
`notes`; use the long slug (`carl_drummer`, `wren_vol6`) in scene JSON
when the 3D portrait is wanted.
