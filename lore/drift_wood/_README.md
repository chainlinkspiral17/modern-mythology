# DRIFT WOOD / ROFLCOPTER · reference files

Per-artifact and per-character documents for vol 10, *ROFLCOPTR* —
the volume that begins as *Drift Wood*, Arthur Finch's strip in the
Small Wood High newspaper, 1997, and ends as *ROFLCOPTER*, the
private work, on a cedar log at the mouth of Alsea Bay in April
2027. Drift Wood is everything before the burnout; ROFLCOPTER is
the personal voyage after it.

The convention follows `planned_community/` and `milk_and_honey/`:
one file per artifact or person, lowercase snake_case, in-fiction
quotes in italics, reserved facts stated as reserved. The volume's
synthesizing wiki is `../_VOL10_WIKI.md`.

## current files

| file | what |
|---|---|
| `_SOURCE_BRIEF.md` | the user's September 2026 brief, transcribed in full. The root document; everything else is derived from it |
| `_AUTHORIAL_RULE.md` | **we don't see the author, but we feel him.** The governing rule: the volume is the strip; Wood is not Arthur; delusion and leak in the same panel; epiphanies are weather. Read first |
| `foreword_afterword.md` | the bookends — the only prose, the only place the author is seen; the ending (the work is published; the specter foreshadowed); who writes them; the foreshadowing index |
| `_CONCEPT_ART.md` | the September 2026 character/environment sheet, described, with where it departs from the brief |
| `_THE_COMPLETE_RUN.md` | **the edition and the full scope**: ~1,500 pages as a two-volume physical set (DRIFT WOOD · ROFLCOPTER) plus one digital edition; page budgets; the editor's-cut selection principle; the complete run roughed arc by arc, 1997–2027, with a selection mark on every arc, fixture and sequence; production phases |
| `style/` | **style guides**: `characters.md` (every figure by era and age, with model-sheet prompts), `eras.md` (line, paper, color, lettering, grid, the mark, the strip's own devices), `locations.md` (hero sets and how they change), `objects.md` (marks, the corner box, the crab flyer lineage, the corkboard inventory, the sign's letter deaths, cars, boxes, tools, clothes, food). Generation side: `godot/tools/comic/style_sheets.json` + `comic_tool.py sheets` |
| `scripts/` | generated, readable script sheets — one per strip JSON in `godot/tools/comic/strips/`, with the whole-strip prompt. Edit the JSON, run `comic_tool.py md`, commit both |
| `_SCOPE_AND_YEARS.md` | **scope** (the ~10,000-strip archive vs the ~200-unit book; three tiers of unit; drawing order) and **the years**, 1997–2027, one entry each: line, what the strip shows, what the reader infers, the units the book takes, the margin mark |
| `_ARC_OUTLINE.md` | the book as seven runs of strips between the bookends; proposed scene-id plan; the player-as-editor canon |
| `the_strip.md` | *Drift Wood* → *ROFLCOPTER* as an artifact: the names, the four eras, the motifs, the two fully-specified Sunday pages |
| `publication_history.md` | the five cadences (biweekly · weekday-daily · newspaper · sabbaticals · private), the 2006 meme incident, the 2018–2020 burnout, the personal voyage |
| `sample_strips.md` | drafted strips for every era, including the last public Sunday and the first private page |
| `arthur_finch.md` | Arthur "Woody" Finch — the author, never on the page; what the strip lets us infer |
| `chloe_sterling.md` | Chloe Sterling — as inferred from the strip's Chloe and (lean) the afterword |
| `todd_gulliver.md` | Todd "Gully" Gulliver — as inferred from the strip's Gully |
| `barnaby.md` | Barnaby, and Barnaby II — three silent Sundays and a margin mark |

## the tool

The strips are produced by `godot/tools/comic/` (README there):
scripts as JSON, whole-strip prompts for the concept run through
Runway or Google, per-panel and Blender/Meshy hooks for later.

## the shape

```
FOREWORD
  Drift Wood · 1997–2020     the public strip, in runs
  ROFLCOPTER · 2021–2027     the private pages
AFTERWORD
```

We don't see the author. Works within works. The strip is inside the retrospective, which is
inside the volume, which is inside the saga. Vol 2, *Small Wood
Volumes*, was a found notebook about the same town; vol 10 is a
found archive about the same town. The saga's continuity is felt,
not adhered to — the `_VOL10_WIKI.md` "Echoes" section lists what
is available to feel and does not require any of it.

## the eras, at a glance

| | years | the line | the paper |
|---|---|---|---|
| I | 1997–2003 | crow-quill and ballpoint, jagged, heavy black spotting | cardstock, xeroxed hard · biweekly, then weekday-daily |
| II | 2004–2011 | brush-pen, rubbery, blog-era minimal | bristol, muddy digital flats |
| III | 2012–2020 | razor-sharp brush and ink; Sundays wet-on-wet | 140 lb Arches cold-press on Sundays |
| IV | 2021–2027 | spare, knowing · *ROFLCOPTER*, private | muted ochre, slate blue, sea-foam · pages, no grid |

## reserved (mid-to-late acts)

Not yet drafted as files: the Driftwood Motel, Gully's Tackle &
Roast (as a place, not a person), Heceta Frame & Matting, the
garage apartment, the tavern (unnamed), *The Timberline*, the
phantom graphic novel (Box 4B), the retrospective and its editor,
Julian, Maria, Arthur's parents, the bird.

## tone

Damp. Observant. The dailies are fast — eight sentences of Arthur,
one of Todd. The Sundays are silent. The volume slows down every
fourth or fifth chapter to let the weather through. Nothing is
wasted unless you weren't looking.
