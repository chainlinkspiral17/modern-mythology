# Comic Pipeline Playbook

Lessons for authoring and rendering the Vol 10 strip run · Drift
Wood / ROFLCOPTER · the JSON scripts in `godot/tools/comic/strips/`,
the style sheets, the reference registry, and the render tools.

Companion to `_VOL10_WIKI.md` (the volume's lore entry point) and
`lore/drift_wood/_THE_COMPLETE_RUN.md` (the edition: what's in the
book, the arc catalogue with ●◐○ marks, the nine annual fixtures).
This playbook is about **how the scripts get written and kept
consistent**, not what the story is.

Read this before adding or editing any strip JSON, any style sheet,
or anything under `lore/drift_wood/scripts/`.

## Core rules

### The JSON is the strip; everything else is generated

`godot/tools/comic/strips/*.json` is the single source of truth.
`lore/drift_wood/scripts/*.md` and `_INDEX.md` are written by
`comic_tool.py md` and must never be hand-edited. Whole-strip
prompts, per-panel prompts, reference selection and stage jobs all
derive from the JSON. If a fact needs to change, change the JSON and
regenerate.

### The id carries the date; keep them equal

Ids are `dw_|rc_|ro_YYYY-MM-DD_slug`. The validator does **not**
check that the id's date matches the `date` field. One strip was
written with a 12-25 id and a 12-24 date and passed validation; the
index then sorted it wrong. When re-dating a strip, rename the file
and the id together.

### Arthur is never in a panel

The authorial rule is enforced mechanically: the validator rejects
any character id beginning with `arthur`. The character on the page
is **Wood** (`wood_17` / `wood_20` / `wood_26` / `wood_34` /
`wood_44`, by era). The author is felt through captions, margin
marks, what the strip refuses to draw, and the foreword/afterword.
Other people may *say* "Arthur" (the frame-shop owner, twice while
he works there and once in 2016; Maria once in 2013; his mother);
that is allowed and is tracked in `style/characters.md`.

### Check the objects timeline before writing a fixture

`lore/drift_wood/style/objects.md` holds the running counts and
states the fixtures depend on: which letters of SMALL WOOD LANES
are dark on each Dog Night, the crab-flyer count (1998 = the 14th
annual, so year − 1984 is the "annual" number and year − 1997 is
the flyer count on the wall), the lawn chair's occupant (empty from
Feb 2001; Chloe sits Jul 2008; Maria takes it Jul 2009), the lamp
(carried home May 2011), the hum line (motel panels from Sept 2011),
the box on the porch (Dec 2014 and Oct 2016). Get the number from
the table, not from memory. When a later strip contradicts an
earlier one, fix the later strip and cite the source strip id in
its `image.notes`.

### One art block per run, copied, not retyped

Every strip carries an `art` object (line / palette / paper). Copy
it from an existing strip of the same run so a run's strips are
byte-identical in style, and so a later global change is one
search-and-replace. The exceptions are deliberate: the Unprinted
Year's four strips each carry their own `art` describing how the
line drifts with no reader, and the 2000–2001 strips carry Arc 1's
hatching.

### Reserved facts are drawn around, never resolved by accident

The tavern's name, whether 2020 is 2020, the boy at the edge of the
1994 group photo, what ends up in the empty frame, which letters
are lit in 2020+: these are reserved in the wiki. A page may
*feature* a reserved thing only by hiding it in the drawing (glare
on the glass, the sign above the frame edge, an eroded date, a face
turned away). Say so in `image.notes` so a renderer doesn't invent
it.

### No lettering in prompts; "Letter after" in the notes

Image prompts end with the era's `prompt_suffix` (no text, no
balloons, no signature). Any text that must appear in a panel — a
sign, a lid, a check's memo line, a caption — is spelled out in
`image.notes` with the phrase "Letter after" so the lettering pass
knows what to set. Balloons are data for the lettering pass, not for
the image generator.

### Batch cycle, every time

write strips → `python3 comic_tool.py validate` → `python3
comic_tool.py md` → `git add -A godot/tools/comic lore/drift_wood`
→ commit with a heredoc (`git commit -F - <<'EOF'`; **no backticks
in `-m` strings** — the shell substitutes them and eats words) →
`git push -u origin <branch>`. The push prints a protected-ref
warning and still lands; verify with `git log --oneline -1
origin/<branch>`, not with the push's exit text.

### Deepen in this order

Fixtures first (the nine per year are the book's floor and the
continuity's skeleton), then the ◐ arcs (the key week of each),
then Sundays, then the Run 7 sequences and unsequenced pages. A
year with its fixtures in place can absorb any arc later; an arc
without the year's fixtures around it floats.

### Ages and births are arithmetic, not vibes

Wood and Chloe are born 1980 (17 in Sept 1997). Gully is a year
older. Barnaby: Nov 1999 – Nov 2014. Barnaby II: Dec 21, 2014 →.
Gully's daughter: b. 2010. Gully's son: b. spring 2013. The uncle
dies Feb 2001. The Datsun 1999–2011, the Legacy Sept 2012 →. When
a page says "fifty" check it against the year first.

## Recent lessons

### 2026-09-26 · Deepening v–vii · every arc at its key week; Vol. II at five a sequence · 578 → 724

Three more batches: the large ◐ arcs' key weeks and both Sunday
runs (Cedar, A Third of a Page), then the last small ◐ arcs, then
fifty-nine ROFLCOPTER pages. The arc-vs-catalogue diff now reports
no ● or ◐ arc below its key week.

- **The diff is the stopping rule.** When `want N` vs `have n`
  reports nothing under five, the pass is done; the remaining
  weight (Sundays to ~325, Vol. II to ~560) is breadth, not gaps,
  and should be scheduled as its own phase against the render
  budget, not written blind.
- **Re-date the fixture Sunday, not the holiday.** A Sunday-format
  strip on a weekday (the 2006 Fourth) is a validation hole; the
  check is one line (`weekday()!=6`) and now runs in every batch's
  post-check with the weekday-claim check and the collision check.
- **Running counts want a table before the strip.** The 2024 crab
  flyer count shipped one high because the arithmetic (year − 1997)
  was done in prose. Put the count in `objects.md` first; derive
  the strip's number from the table.
- **Vol. II subtracts what Vol. I accumulated.** The anniversary
  pages lose the man, the Dog Nights lose the caption, the first
  face drawn whole is Gully's, not Wood's. When a private page
  wants a figure, give it a hand, a knee, a back, a reflection, or
  the other person.
- **Give the strip's own future one leak, then close it.** Julian
  naming a Sunday he could have read is fine; naming one not yet
  drawn is a bug the first draft had. A stranger may know the past
  of the strip exactly; never its future.

### 2026-09-26 · Deepening iii and iv · the story arcs to full weeks · 442 → 578

The ● arcs were the gap: most had one strip standing for five to
twenty. Two batches filled every small ● arc to its week and the
four numbered arcs to their brief-specified shape (Arc 1: 18
dailies + 3 covers + the oversized Sunday; Arc 2: 13 dailies + 2
Sundays around the parody week; Arc 3: 14 dailies + 3 Sundays; Arc
4: the Steep Path, the Table Lowered, the Clinic, Between Sundays
and the week after The Box).

- **Run the arc-vs-catalogue diff first.** A twenty-line script that
  matches `_THE_COMPLETE_RUN.md`'s "want N dailies" against strips
  per arc found the gaps in one pass. Keep using it before every
  deepening batch; it is the map.
- **Anchor every week to the existing key strip's date.** The brief
  gives "Thursday, Week 2" loosely; the existing file's date is the
  truth. Build the week around it and check weekdays with
  `date.strftime` before commit; the batch that skipped this shipped
  two Fridays that were Saturdays.
- **Two parallel shell calls share one cwd.** A `cd ..` in the first
  call broke the second's relative paths and cost a full re-send of
  a 35-strip script. Every batch script starts with an absolute
  `cd`; never chain `cd ..` after a heredoc.
- **The wordless arcs stay wordless.** Arc 4's dailies carry no
  balloons except the vet's mouth; Two-Thirds never remarks on the
  size; Noir Week is captions only. When a beat wants a line, give
  it to Gully in one word or to the caption, not to Wood.
- **Strangers may say "Arthur"; friends don't.** The owner, the vet,
  Julian, the visitors with Washington plates. Gully, Chloe and
  Maria say "Woody" (Maria once "Arthur," flat, in 2013). The rule
  is now in characters.md; keep the count there current.

### 2026-09-26 · Deepening ii and the inspector · 404 → 442 scripts

Twenty-nine Sundays and ten dailies filled the half-marked arcs of
2014–2018 and gave Runs 3 and 6 two landscape Sundays a year. Then
`comic_inspector.py`: a local page over the run with generation.

- **Sundays are where a year's continuity is confessed.** The 2008
  mudflats Sunday now holds the composition 'The Carry' and the final
  page reuse; the 2006 seawall Sunday hints the glow three years
  before 'Lanes.' When a late page needs a rhyme, plant it in an
  earlier Sunday rather than a daily; the book's Sundays are read
  as a sequence of their own.
- **Check for date collisions before writing a batch.** Two strips
  landed on days that already had one (the scroll, the pitch
  meeting) and one Sunday preceded the daily it followed from. `ls
  strips | grep YYYY-MM` before the heredoc; a Sunday that
  continues an arc is dated the Sunday *after* the arc's key daily.
- **The inspector runs the CLI, it doesn't reimplement it.** Generate
  = `comic_tool.py strip-prompts --only <id>` then `comic_render.py
  --queue <that>`; the outputs and manifests are the CLI's. Any new
  option goes into the CLI first and the page just passes it through.
- **Review travels in the JSON.** The page writes a `review` block
  (status, note, date) into the strip file; the validator ignores
  it, `md` shows it, a commit carries it. That is the revision
  channel: the user marks, the next session reads `review.status ==
  "revise"` and rewrites.
- **Write strip files without a trailing newline.** The batch
  writers use `json.dump`; a writer that appends `\n` turns every
  touched strip into a one-line diff. Match the existing shape.

### 2026-09-26 · The deepening pass · 255 → 404 scripts

One session took the rough batch through the thin years: every
fixture for 2004–2020 (2010 excepted, on purpose), the ◐ arcs of
2001–2003 and 2012–2013, and the ROFLCOPTER sequences plus two
unsequenced pages a year.

- **The fixtures are where continuity is made or lost.** Nearly
  every reconciliation this session (the chair in 2013, the
  corkboard's first pin, Box 5's closing date, Chloe's age on the
  dock) was found by writing a fixture against the objects table.
  Write the table entry *before* the strip if the strip introduces
  a new running count.
- **Sundays for the ◐ arcs that live "in the background."** The
  Strip About Wage Labor never got its own dailies; it lives in
  the ink-only basement tier of 2013's Sundays. That pattern (a
  narrow third tier, different medium, recurring caption) is how a
  background arc gets on the page without a week of strips.
- **Private pages get no counts.** The public Dog Night always
  captioned the years; the ROFLCOPTER Dog Nights are uncaptioned.
  The anniversary pages lose the man entirely (a tray of corn), then
  get a hand back in 2026. Vol. II's rule is subtraction.
- **A page can be a third blank.** The Route North stops at the
  on-ramp and leaves the paper; the Ridge bleeds the glow to a bare
  edge. Say "bare paper" in the prompt or the generator fills it.

## TEMPLATE for new "Recent lessons" entry

```
### YYYY-MM-DD · <one-line title>

<one-paragraph situation>

- **<Bolded principle>.** <two-to-three-sentence explanation.>
- **<Bolded principle>.** <two-to-three-sentence explanation.>
- **<Bolded principle>.** <two-to-three-sentence explanation.>
```
