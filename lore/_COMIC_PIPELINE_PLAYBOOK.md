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

### 2026-09-26 · The backups · fifteen series outside the canon · 101 pages

The catalogue complete, the run got a second shelf: `bk_` ids, `strip:
"backup"`, a required `series` field, catalogued in
`lore/drift_wood/_BACKUPS.md`. Fifteen series: the three phantom graphic
novels (SLASH, THE LONG WAY BACK, CEDAR), a found Sunday (THE SINKHOLE),
four private experiments (THE FREQUENCY BENEATH, THE SCUMM STICK, THE
BACKWARD DIGEST, THE CARD IN THE DRAWER), and seven genre weeks (NOIR WEEK
II, THE HALLOWEEN ISSUE, RUST_CODE.BBS, THE POMEGRANATE HOUR, 3 AM, THE
RENDER WEEK, THE FRONTIER WEEK, POSTCARDS FROM THE OTHER TOWN). The
validator, sheets, inspector and render tool take them as strips; the
wiki's canon count excludes them.

- **One form, one device, per series.** SLASH is rain-hatched noir
  pages; the travelogue is a card in a drawer per stop; CEDAR is three
  wrong explanations and a notch; the frequency pages are graphs; the
  adventure has a verb bar; the digest reads backward; the drawer has one
  card per page; the dog wears the trench coat; the Halloween issue's
  horror is the spotting; the BBS gives the chorus handles; the talk show
  is recaps on a lobby TV. A device used once is closed to the others.
  This is what keeps twelve weird things from being one weird thing.
- **Other volumes are objects.** A boat registered in Graustark, a card
  in an evidence bag, a man smoothing his lapels at Table 14, four
  demons' names as handles, a host with a cassette deck, a bird that's
  the wrong color for a place, a waveform on a paperback, a machine in a
  pizza window, a yellow slicker. `image.notes` names the volume; the
  page never does; a reader of Vol 10 alone loses nothing.
- **The redundancy guard is a shingle overlap, minus the style prefix.**
  Six-word shingles of each backup prompt against every canon prompt,
  with the era prefix stripped first (it alone shares twenty shingles).
  What remains above five is stock phrasing ("a man in a maroon polo")
  or a declared quotation (the Hermit is the lamp on 101; the Star is the
  one lit tube). Anything else would be a page to rewrite. None was.
- **Backups may circle reserved facts; they may not land on them.** The
  Halloween sign spells a word into a blank balloon; the sinkhole Sunday's
  fourth page carries Wood's only note, "not mine. keep."; SLASH puts a
  port on a boat and a number on a cuff, never a name on the tavern.
- **A genre week gets one closing device and keeps it.** The western's
  ridge ends every strip with one more thing on it (a stump, a crow, a
  stake, a paddlewheel that can't be there, a card). The render week's
  bar fills and empties. The postcards give one word each and the words
  are the canon's sentences rearranged, ending on the one word the canon
  never says. The device is the week's plot; the plot is optional.
- **The backups quote the canon forward and backward.** The whistle's
  shape is drawn from a tape in 2013 before the Mill sequence draws it
  from memory in 2022; the box is drawn empty in 2012 with the dog alive;
  the lamp is USEd WITH beach in 2024, lit in 2027. The compare notes
  point both ways so the wiki can build the timeline either direction.

### 2026-09-26 · Deepening xvii–xviii · the catalogue complete · 1,255 → 1,378

The last two canon batches. Public: sixty-four fixture-week dailies for
2005–09 and 2017–19, three more 2010 reprint pairs, three 2015 rerun
Sundays (the sabbatical's dividers), six Sundays. Private: forty-seven
pages that bring every sequence to or past the catalogue's share (The
Route North to 30, Rooms to 24, An August to 20, The Boxes to 14, The
Tavern to 10). The run stands at 806 public and 572 private against the
plan's ~880 and ~560; every arc, fixture, Sunday quota and sequence the
catalogue names now has its scripts.

- **The canon is finished when the catalogue's rows are, not when a
  number is.** The plan's ~880 public pieces included covers and
  apparatus the strip files don't hold. Every ●, ◐ and ○ row, every
  fixture in every year the paper ran, and every sequence has its key
  pages; that is the stopping rule, and it is now met.
- **Reruns are dividers and should look like it.** The 2015 Landscapes,
  Again Sundays reproduce their 2008 originals tier for tier, with a
  RERUN note in the margin and the original's id in the notes. A rerun
  that improves on its original is a new strip and belongs to the
  sabbatical's wrong year.
- **An August borrows Vol 7 and never names it.** Mrs. Gable's seat,
  Static Truths, Board Lords in Wagner's building, Finn's radio at the
  pilings, Sal's machine in the pizza window, the yellow slicker: each
  is drawn as a thing the town has and the page doesn't explain. The
  note names the Vol 7 source so the wiki can cross-reference; the page
  never does. This is the model for anything beyond the canon.
- **Auto-shifting dates is safe for pages, not for fixtures.** The
  private helper now walks forward from a requested date to the first
  free one; a page's day matters less than its month. A public fixture
  daily must land on its calendar day, so that helper stays assertive.
- **What is beyond the canon is a separate strip.** Anything that is
  not Drift Wood, ROLFCOPTR or ROFLCOPTER as the catalogue defines them
  (the phantom graphic novels, the genre detours, the pages that quote
  the other volumes outright) gets its own id prefix and strip name so
  the inspector, the render tool and the wiki can keep the canon count
  clean.

### 2026-09-26 · Deepening xvi · fixture weeks · 1,219 → 1,255

Twenty-four public dailies: twelve single-daily fixtures in the thin years
(2001, 2002, 2003, 2013, 2016) each given a day before and a day after,
so the fixture reads as a short week the way the catalogue allows. Then
six Bird and six Mill pages, which put both sequences past their share;
the counts quoted in earlier entries for those two were low, and the
per-arc counter is now part of the post-check so the number on the page
is the number in the folder.

- **The day before a fixture is the fixture's reason.** Maria deciding to
  take the blank flyer; Gully filling the thermos and saying "the beach";
  the pup stopping at the alley a night early. The fixture strip stays
  as written; the before-strip supplies what it assumed.
- **The day after is the object the fixture leaves.** The napkin in a
  plastic sleeve, the fish on the step, the first dog's box found by the
  second dog, the unlettered Box 5 lid. An after-strip that adds a second
  joke instead of an object is the wrong strip.
- **Base each neighbor on the fixture strip itself**, not on the year's
  first daily: venue, era, art and mark come from the strip it flanks, so
  2001's Rain neighbors carry the frame-shop art and 2003's Dog Night
  neighbors carry the unprinted arc's source line.
- **Strangers say "Arthur"; Wood says "Wood".** The motel guest's
  checkout is the fifth stranger; the count in `characters.md` is now
  the owner ×5, the vet, Julian once, Maria once flat, and guests. Check
  the list before writing the word.

### 2026-09-26 · Deepening xv · the unsequenced pages reach their share · 1,168 → 1,219

Fifty-one unsequenced private pages, seven a year, on free Wednesdays and
Sundays. The private volume's unsequenced count is now 242 against the
catalogue's ~240; every sequence but The Bird and The Mill (38 and 34 of
40) is at or past its share. The corkboard drift check ran as a standard
post-check and flagged one false positive (the Florence weekly on
Gully's counter), which is the check working.

- **Pick dates from a computed free list, not from memory.** A one-line
  script printing the free Wednesdays and Sundays per year makes the
  date choice mechanical and the collision check redundant; the batch
  passed first time.
- **The small objects carry the years better than the people.** The rain
  gauge (three Januaries, its number never lettered), the thermos, the
  worn rail, the cracked seat, the pen's wear in three places twice, the
  blanket's corner becoming a hole. Each one is a clock the reader can
  read without a caption, which is what the private pages are for.
- **Every "three" has its two on the page.** Three coffee cans (2020,
  2025, 2026), the flag up three times, three Januaries of the gauge,
  the third mailbox flag with the envelope's corner. The compare note
  lists the earlier pages so the count is checkable.
- **The volume's end is a hard edge.** The book ends April 25, 2027; the
  free-date list after that is not free, it is after the book. No page is
  dated past the final page, whatever the boxes hold.

### 2026-09-26 · Deepening xiv · the missing public fixtures; two corkboards · 1,090 → 1,168

Eleven public fixtures the year-by-fixture table showed missing (Last
Bell 2001–03, the Fourth and Tourist Season 2002, and six of 2014's
nine), then sixty-seven private pages: fifty-nine unsequenced, four
Bird, four Mill. A grep for corkboard items by location caught four
strips putting Wood's garage board on Gully's wall; fixed before commit.

- **There are two corkboards, and they hold different things.** Wood's
  (bedroom 1998–2003, garage 2004–27) holds the yearbook photo lowest,
  the walk map, the Florence gull, the backward digest, the sticker
  upside down. Gully's (above the register, 2003–) holds the 2003 rough,
  lost-cat flyers, tide tables, tourist snapshots, the printout under
  page fourteen, the 61 MI postcard, the red-framed crab, TAKE-OUT ONLY.
  A page at Gully's that names the walk map is wrong. `objects.md` now
  says so in one sentence at the end of the corkboard section.
- **Audit by location and keyword, not by memory.** The four bad strips
  read fine on their own; only the query "items from list A at location
  B" found them. Add a location-keyword check to the batch post-checks
  whenever a batch touches a load-bearing object.
- **A fixture table per year finds the real gaps.** Matching arc names
  and id keywords against the nine fixtures per public year showed most
  years complete and the gaps concentrated in 2001–03 and 2014; the Run 1
  summers and the two sabbaticals are not gaps, since no paper ran.
- **Fixture dailies carry the counts in dialogue.** "Sixteen years."
  "Fifteen. I missed one." The 2010 sabbatical, the seventeenth corn, the
  uncle's chair empty since February 2001: each is a line a reader can
  check against the run, so the dialogue was checked against it first.

### 2026-09-26 · Deepening xiii · the short sequences to their share · 1,024 → 1,090

Sixty-six private pages. The Stone Head, The Dock, Spring, What People
Framed, From Behind, The Ridge and Absent each reached or nearly reached
their book share; The Bird and The Mill took five more each; the
unsequenced pages went to 131. Nothing failed the up-front check.

- **A sequence's late pages find what the strip drew first.** The stone
  head turns up in three strokes behind a dog in a 1999 daily; the mill is
  drawn once from the ridge where the glow will be. The private work is
  allowed to notice the public run, and the note names the strip so the
  render prompt can quote its shape without inventing a date.
- **Pairs and counts stay auditable.** Two cans then four; two rings and
  the bird in one; two leashes; three chairs then the stool. Each count
  is in the logline and the compare note, so a later page can be checked
  against it with grep rather than memory.
- **A person arrives as a part before a whole.** Chloe on the dock is
  boots, then hands with a pale ring band, then a figure from the side,
  then a small back through a window. The rule that held for Wood from
  2021 holds for anyone the private pages let in.
- **One page a volume may admit the device.** "The bird, not here" draws
  four empty places and says it looked; "The crab in the margin" is mostly
  margin. One each, unsequenced, and no more; the book's restraint is the
  point and a second such page would spend it.

### 2026-09-26 · Deepening xii · past a thousand · 961 → 1,024

Fifty-seven private pages and six Sundays. The private pages took the
unsequenced count to 105, The Bird to 32, The Mill to 30, and gave An
August, The Reading Room, The Boxes and The Tavern their next pages; the
Sundays filled 2004 and 2006 to twelve and thirteen. The queue-then-check
shape caught a duplicate date inside the batch itself (two pages on
2022-07-24) before a file was written.

- **Keep the batch script in the scratchpad, not only in the heredoc.**
  When the check fails the fix is one edit and a re-run, not a re-send of
  sixty pages. The Sunday half of the same command had already written
  its six files; independent halves should be independent scripts.
- **Two Rain pages a year is fine when they are different pages.** The
  Rain, 2024 (the jars) and the bird on the sill a week later are both
  January pages; the fixture and the sequence can share a month as long
  as they do not share a date or a subject.
- **The private volume's small canon is now dense enough to check
  against.** Two leashes, two cans, two tins, two mugs, two chairs, two
  keys: each pair has its first page and its second, and a note that
  names the other. New pages should look for the pair before inventing a
  third.
- **Sundays in a thin year go to the fixtures, not the arcs.** 2004 got a
  Bad Color flat, a seawall from the water and the first mailbox Sunday;
  2006 got nine flyers, Last Bell with the stick chorus and the logging
  road. The arcs in those years are already at their key weeks.

### 2026-09-26 · Deepening xi · the thin sequences and the private seasons · 904 → 961

Fifty-seven private pages: The Bird to 26, The Mill to 24, The Route
North to 20, Rooms He Never Saw to 18, and twenty-four unsequenced pages
spread four a year across 2021–2027. The batch queued every page, checked
all planned dates against the existing set and against each other, and
only then wrote files; nothing landed on disk before the check passed.

- **Queue, check, then write.** The page helper now appends to a list; a
  single assertion over the whole list runs before the first file is
  written. Last batch's abort-after-two-files cannot recur in this shape.
- **A sequence's device gets one page that turns it on itself.** The mill
  sequence's spotting becomes the saw's teeth; From Behind's rule becomes
  the empty coat on the hook; the Route North's empty reflection becomes
  the driver's empty mirror; the Rooms sequence ends by drawing the one
  room he did see as if invented. One such page per sequence, not more.
- **Unsequenced pages are the private work's dailies.** Four a year, on
  the objects the fixtures don't cover: the polo on the line, the tin
  rusting, the blanket washed, the odometer, the box lids. They carry the
  small canon (the pale rectangle where the rack was, the nail through the
  wall, the chair moved for the first time in eighteen years) that the
  sequences assume.
- **Reserved facts stay reserved even when a page is about them.** The
  bird sits on the letter of the tavern sign that would settle the name;
  the mill notice is drawn backward through glass; the boy at the fence
  has no character id. The note in `image.notes` says what the device is
  so the prompt says "not legible" rather than guessing.

### 2026-09-26 · Deepening x · the ROFLCOPTER sequences toward their book share · 852 → 904

Fifty-two private pages, chosen by comparing each sequence's written
count against its share in the catalogue's table (The Mill 6/40, The Bird
9/40, The Route North 7/30, Rooms 7/24, From Behind 8/20, Spring 6/20,
What People Framed 6/20, The Ridge 6/16, No Grid 6/12). The sequences
with the widest gap got the most pages.

- **Check every planned date before writing any file.** The batch aborted
  on its third page over a date the previous batch had used, leaving two
  files written. Listing the planned dates against the existing set first
  costs one command and turns an abort into a rename before anything is on
  disk. The abort is still the right behaviour; it just should not be the
  first check.
- **A sequence's last page changes hands, not subject.** The mill sequence
  ends on the same view as its first page with the Era I spotting dropped;
  From Behind ends on the hand-on-the-dog with no man above it; The Route
  North ends on the bag set down. Each ends by taking away the device the
  sequence was drawn with, which is what makes it an ending rather than a
  stop.
- **Two pages dated the same day are a collision, not a spread.** A "facing
  page" to an existing page still needs its own date; the book's facing is
  a layout note in `image.notes`, not a shared date. The Bird and Gully
  moved three days on.
- **Reserved facts get drawn around the same way each time.** Glare over a
  jersey number, a screen drawn blank, a sign above the frame, a figure at
  a distance: the device is named in `image.notes` so the render prompt
  says "no words legible" or "too far to read" rather than inventing.

### 2026-09-26 · Deepening viii and ix · the Sundays and the private seasons · 724 → 852

Two batches of breadth after every arc reached its key week: forty-one
Sundays (viii) then forty-one ROFLCOPTER pages and forty-six more Sundays
(ix). The thin years were found by counting Sundays per year, not by
rereading the catalogue; the ROFLCOPTER pages were found by walking the
nine fixtures through 2021–2027 and asking which had no private page yet.

- **The fixtures run through the private years too.** Crab Derby, the
  Grunion Run, Last Bell, the Fourth, Tourist Season, the Rain, Dog Night,
  Christmas Eve each get an unsequenced page in most private years. They
  carry the counts (flyers = year − 1997; one chair 2023, two 2026; the lamp
  unlit 2025, lit 2027) and the sequence's rule for the year: absent in
  early 2021, a back after June 2021, a knee and a hand by 2024.
- **Cross-references get checked, not remembered.** Every "compare
  ro_2026-12-24" written in a note was grepped against the strip ids before
  the commit. Two batches ago a note pointed at a strip that had been
  renamed; the check is cheap and the wrong pointer would have survived into
  the sheets.
- **Sundays are counted per year before writing.** A year with six Sundays
  gets four or five; a year with eleven gets none. The catalogue's "12 of
  ~50" is the ceiling per year, not the target: the physical book's
  Sunday pages are shared across 2004–2020.
- **A Sunday helper asserts three things.** `weekday() == 6`, the date is
  not already used by a daily of the same strip, and the id's date equals
  the date field. All three have failed silently in earlier batches; the
  assertions now run before the file is written, so a bad date aborts the
  batch instead of landing in the repo.

### 2026-09-26 · Balloons cutting off text · the 1000-character chop

User feedback: rendered balloons kept cutting off text. The cause
was not the image model: the Runway runner truncated every prompt
to 1000 characters and 636 of 724 lettered prompts are longer, with
the dialogue at the end.

- **Never truncate a prompt that carries dialogue.** Shorten the
  style and the descriptions; keep every quoted line. The compact
  prompt (`compose_strip_prompt(..., compact=True)`) exists for
  models with short limits; the runner chooses it per model or on a
  400 about `promptText`.
- **Put the lettering contract in the prompt.** "Every balloon
  contains its complete text; size the balloon to the sentence;
  never cut a word; no other words." Image models letter what they
  are told to letter and pad or trim what they aren't.
- **Batch scripts shouldn't repeat the style prefix in every panel
  prompt.** It costs ~50 characters a panel; the compact composer
  now strips a shared prefix, but new batches should leave the
  era's style to the era block.

### 2026-09-26 · The render tool: model passthrough and new takes

User feedback: the model menu was inadequate (Runway has many more
than gen4), and a second generate on a strip did nothing.

- **Never skip silently on a repeat.** The runner refused to
  re-render a strip whose file existed unless `--overwrite` was set,
  and the inspector didn't set it. A second click looked like a
  broken tool. Every run is now a new take (`_t2`, `_t3`…) with the
  model and take recorded in the manifest; skipping is opt-in.
- **Pass the model through; don't gate it on a list.** `--model` was
  google-only and Runway was hardcoded to gen4_image. Both providers
  now send whatever id is given; a `MODELS` table with `verified`
  flags only fills the menu. Ids I couldn't confirm from the
  container (the dev API docs are egress-blocked here) are marked
  unverified in the UI, and the 400 body prints the id.
- **Runway's MCP ids are not the dev API's ids.** The concept run's
  `nano-banana-pro` is the MCP's name; the dev API spells the same
  family `gemini_2.5_flash` / a `gemini_3_pro` variant. Keep both
  spellings in the table's notes so the next session doesn't re-learn
  it.

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
