# Scene authoring brief: Modern Mythology Vols I–IV (2010 book → Godot VN)

You are adapting part of Andy Link's restored 2010 book into scene JSON for the Godot visual novel. Andy's direction:

- **Faithful + added choices.** Keep the book's text. Add player choices at natural forks, but never cut canonical text.

## Inputs
- Restored text, one file per volume: `/home/claude/mm_src/final/vol1_faust.md`, `vol2_small_wood.md`, `vol3_earthman.md`, `vol4_back_matter.md`. Each page is preceded by `<!-- p.N -->`, where N is the PDF page index. Find your pages with `grep -n "<!-- p.N" file`.
  - `:::expansion … :::` blocks are new connective material. Adapt one only if your brief says so.
  - `> [[RECOVERED from page image]]` is a note; drop it.
- Style reference: existing scenes in `/home/claude/modern-mythology/godot/resources/scenes/vol1/` and `vol2/`. Read `vol1_ch2_park.json`, `vol1_ch4_waking.json`, `vol2_ch2_ghost.json` and `vol2_bf_hub.json` before writing.

## Output
- Scene files go in `/home/claude/modern-mythology/godot/resources/scenes/volN/<id>.json`, one JSON object per file:
```json
{ "id": "<same as filename stem>", "vol": N, "chapter": <int>, "type": "chapter" | "interlude", "title": "<display title>", "nodes": [ ... ] }
```
- Two spaces of indentation, UTF-8, real characters rather than \u escapes (`ensure_ascii=False`). Writing the JSON with a short Python script is the easiest way.
- Do NOT edit `index.json`, other agents' scenes, or existing scenes unless your brief says to. The coordinator wires the index.

## Node types (only these)
| t | fields | notes |
|---|---|---|
| `bg` | `src` | `assets/backgrounds/vol{N}_{slug}.jpg`. Set one at the start of each scene and on each location change. |
| `bgm` | `src` | `assets/audio/bgm/vol{N}_{slug}.mp3`. Reuse an existing track where one fits (Vol 1: vol1_ambient, vol1_dream_drone, vol1_club_thump, vol1_diner_ambient, vol1_drive_night; Vol 2: vol2_ambient, vol2_seagash_drone, vol2_rest_stop_wind). New tracks are fine: log them. |
| `interlude` | `text`, `sub`, `duration` | Title card at the start of a chapter or location change. `sub` is "Place · Time"; `duration` is 1800–2400. |
| `narrate` | `text` | Narration, stage directions, prose. |
| `say` | `char`, `expr`, `text` | Dialogue. `char` is the display name ("Faust", "The Writer", "Charlie"). `expr` defaults to "neutral"; also allowed: warm, sad, angry, amused, surprised, worried, tired. |
| `think` | `text` (`char` optional) | Interior monologue in first or close third person. |
| `show` / `hide` | `char`,`expr`,`pos` / `pos` | Portraits. `pos` is left, center or right. Use `show` only for recurring named characters (slug: lowercase, underscores, e.g. `faust`, `dickens_dean`). Begin each scene with `hide` on all three positions, as the existing scenes do. |
| `cg` | `src`, `caption` | Full-screen illustration: `assets/cg/vol{N}_{slug}.jpg`. |
| `choice` | `opts`, optional `prompt` | Each opt is `{"text": "...", "goto": <node index in this scene>}` or `{"text": "...", "scene": "<scene id>"}`. Optional gating: `"requires": "flag"` or `["f1","f2"]`, and `"hide_if": "flag"`. |
| `flag` | `key`, `val` | Set at scene end: `{"t":"flag","key":"vol{N}_<scene>_complete","val":true}`. |
| `jump` | `scene` | Go to the next scene. The last node of a linear scene is a `jump` (or `end` if your brief says so). |
| `end` | — | Ends the volume or demo. Use only where told. |

`goto` takes a 0-based node index within the same file. After writing a file, re-check that every `goto` points at the node you intend. Off-by-one is the most common bug.

## Fidelity rules
1. **Keep the words.** Every sentence of the book in your range must appear in some node on every play path. Split prose into narrate beats of one to three sentences (≤ ~320 characters each), cut at sentence boundaries.
2. **Screenplay:** sluglines become an `interlude` (optionally also a `bg` change), not a narrate line. A character cue plus its lines becomes a `say`. Lineated verse dialogue can be joined into one `say` per thought, with light display punctuation added (commas, periods, an em dash where the line breaks mid-thought), as `vol1_ch2_park` does. Action lines become `narrate`.
3. **Prose with a first-person narrator** (Small Wood, Earthman's "Andy" passages, blog scraps) goes in `narrate`. Use `think` only for clearly interior lines.
4. **Spelling:** keep the author's voice, slang, deliberate lowercase (the 2006 blog scraps are all lowercase) and coinages. Fix only unambiguous typos that would read as engine bugs on screen ("recieved"→"received", "teh"→"the"). Never change wording.
5. **Poems** keep their line breaks: one `narrate` per stanza with `\n` between lines.
6. **Do not** add exposition, summaries or "meanwhile" lines. Do not explain the cosmology. No meta references to volume numbers in narration.

## Added choices (Andy asked for these)
- Use one or two per scene at most, and only at natural forks: which detail to look at, whose thread to follow first, whether to linger, which of two simultaneous moments to see. Every branch must rejoin, and all book text must still be reached. A branch may reorder the text but not drop it.
- A "linger/look closer" branch may show a short passage from the same page earlier or in a different framing. You may add at most one new line of narration per branch, and it must be strictly descriptive and in the book's register. Don't invent plot, backstory or new dialogue for named characters.
- Choice text is short, lowercase or sentence case, in the voice of the volume (see the Vol 2 Briar Falls hub).
- Gate nothing, except where your brief asks for a hub.

## Register per volume
- **Vol I, night-city Americana:** screenplay, dream logic, club and diner light.
- **Vol II, storybook folk:** Oregon-coast town history, a found notebook "By D.N. Dean", damp and slow.
- **Vol III, retro-future signal:** pulp SF (Jack Perkins, the time pod) interleaved with "Andy"'s contemporary threads (Caltech, Pasadena, his father). The `interlude` `sub` lines can carry a signal/terminal flavor ("transmission · 1944", "Pasadena · now").
- **Vol IV, xerox zine punk:** scraps, blog posts, screenplay and stories.

## Scene size & naming
- Aim for 40–160 nodes per scene, one location or beat each. Split long chapters into `_a`, `_b`, `_c` scenes chained by `jump`.
- Ids: `vol{N}_ch{K}_{slug}` for chapters (Vol IV uses its own scheme, given in your brief). Use lowercase with underscores. `chapter` holds K.
- Every scene: a `bg` near the top, `hide` ×3 before the first `show` or `say`, an `interlude` at its start, a `flag` near the end, then a `jump`.

## When you're done
1. Validate: `cd /home/claude/modern-mythology/godot && python3 tools/validate_scenes.py --quiet`. Your new files will warn as unindexed; that's expected. There must be no ERRORs in your files.
2. Run a coverage self-check: for each page in your range, confirm its sentences appear in your scenes. A quick script comparing 4-word shingles of the page text against your scenes' text is enough. Report any page under 90% coverage and fix it.
3. Write an asset worklist to `/home/claude/mm_src/scene_assets/<your-batch>.tsv` with columns `kind` (bg|cg|bgm|portrait), `path_or_slug`, `scene_ids`, `description`. The description is one line an artist could paint from: place, time of day, mood, era. Don't use proper-noun signage in descriptions.
4. Reply with: scene ids in play order (first and last), node count, the choices you added (one line each), coverage per page range, and anything you were unsure about. Keep the reply under 300 words.
