# ROFLCOPTR · arc outline · prep

The brief specifies five arcs across thirty years, each with a
turning point, an aesthetic, and key strips. This file turns them
into a proposed **chapter shape** for the VN and a scene-id plan,
without writing any scenes. Nothing here is in `index.json`.

Working assumptions (change freely):

- **A chapter is an arc.** Vol 7 runs ~23 chapters of a single
  August; vol 10 runs thirty years. The right unit is the arc, not
  the day. Five arcs → five acts, with **interludes** between them
  carrying the years the brief summarizes rather than dramatizes.
- **The strip is on screen.** Each chapter contains its arc's key
  dailies and Sundays *as drawn* — CG nodes or a strip-panel
  presentation — and the days they were drawn on as VN scenes. The
  reader sees both the life and the record of it.
- **The retrospective frames it.** The 2027 editor's visit (Arc 5)
  can open the volume as a prologue and close it, so the whole
  thirty years is read as the archive being opened. Works within
  works. Optional; the linear read also works.

---

## Proposed structure

### Prologue · The Archive (autumn 2026)

The editor drives down from Seattle expecting a recluse. Arthur's
routine: morning shift at the Driftwood, afternoons at Gully's,
evening walk with Barnaby II. The garage. The boxes. *"Where is the
unreleased graphic novel?"* — held back for Act V; the prologue
ends at the first box opened. Era IV line.

- `vol10_ch0_driftwood_motel` · `vol10_ch0_gullys` ·
  `vol10_ch0_garage` · `vol10_ch0_first_box`

### Act I · "The Driftwood Ledger" (Autumn 2000, 4 weeks)

The scholarship turned down. Heceta Frame & Matting. Chloe's bags
packed. The fried-clam daily (Tue, week 2). The Greyhound Sunday
(week 4): red taillights around the bend of 101.

- `vol10_ch1_timberline` (flashback frame: 1997, the newsroom, the
  strip's first panel — optional cold open)
- `vol10_ch1_frame_shop` · `vol10_ch1_fried_clams` ·
  `vol10_ch1_chloe_packing` · `vol10_ch1_greyhound`
- Sunday CG: **The Greyhound Station** (five-tier).

**Interlude i · 2001–2005.** Box 4B's sixty pages. Barnaby found
behind the bowling alley (Nov 1999 — could sit at the head of Act I
instead). Arthur turns twenty-five. Father gets sick. Hours cut.
Told as a run of dailies, no dialogue scenes.

### Act II · "The 3:00 AM Protocol" (November 2006, 3 weeks)

Broke. Instant noodles. The 72-hour sprint. *"If they want garbage,
I will build them a cathedral of garbage."* R-O-L-F-C-O-P-T-R. The
509. Todd's printout from the Waldport muffler shop. Arthur's face
in the inkwell.

- `vol10_ch2_message_boards` · `vol10_ch2_sprint` ·
  `vol10_ch2_509` · `vol10_ch2_todd_printout` ·
  `vol10_ch2_banner_ads`
- Daily CG: **3:42 AM, the CRT** (four panels).

**Interlude ii · 2007–2013.** The cedar mill walk with Chloe (2008).
The travelogue draft. The Driftwood Motel night desk. The Subaru.
Era III's line arriving.

### Act III · "The Glass Pavilion" (July 2014, 3 weeks)

The drive north on a doughnut spare. The cedar-and-glass pavilion
on Puget Sound. Thrift-store wool suit, mothballs, sketchbook in
lap. The cocktail-hour daily (kombucha; *"Who's backing you?"*).
The dock at 11:30 PM: *"Someone has to make sure the fog doesn't
get stolen."* *"You're a coward, Arthur Finch."* *"I know."*

- `vol10_ch3_subaru_north` · `vol10_ch3_pavilion` ·
  `vol10_ch3_cocktail_hour` · `vol10_ch3_dock`
- Sunday CG: **The Dock, 11:30 PM** (four-tier panoramic).

### Act IV · "Low Tide at Alsea Bay" (Nov–Dec 2014, 5 weeks)

The steep gravel path Barnaby can't make. The table lowered to
floor height. The carry down the wooden steps. The county clinic.
Then the Silent Sunday Trilogy — three chapters that are almost
entirely CG, almost entirely without text:

- `vol10_ch4_gravel_path` · `vol10_ch4_table_lowered` ·
  `vol10_ch4_clinic`
- `vol10_ch4_the_carry` — Sunday 1, six wordless panels.
- `vol10_ch4_the_empty_chair` — Sunday 2, fully specified in
  `the_strip.md`. The volume's first CG to commission.
- `vol10_ch4_the_box` — Sunday 3, fully specified. The second.

**Interlude iii · 2015–2025.** The magical-realist timber allegory
(2016). Newport diner (2018). Chloe's divorce (2021). Era IV. Small
Wood turning into Airbnbs. The dock and the Rainier (2024). The
vol 7 summer (August 2025) passes in the background of the
dailies, unnamed.

### Act V · "The 30-Year Ledger" (Autumn 2026 – Spring 2027)

The editor, resumed from the prologue. Box 4B holding the rug down.
*"So... you wasted thirty years drawing a daily newspaper strip
about a small town?"* *"Ten thousand days of noticing things.
Nothing gets wasted unless you weren't looking."*

- `vol10_ch5_editor_returns` · `vol10_ch5_box_4b` ·
  `vol10_ch5_ten_thousand_days`
- `vol10_ch5_final_sunday` — the full-bleed April 2027 page. The
  chimney, the mug, the tide line, the sandpipers, the cedar branch
  floating out.
- `vol10_end`

### Epilogue · reserved

Whether the saga's far-horizon image (the feral child, the ceramic
frog, the ground where the riverboat was) is the last thing on
screen after the cedar branch. See `_VOL10_WIKI.md` → Reserved.

---

## The presentation question (for the engine, later)

Vol 10 is a comic strip inside a visual novel. Three ways to show
it, not exclusive:

1. **CG nodes** for the specified Sundays and key dailies, in the
   existing engine, with the `glitch` (or a new) skin. Cheapest.
   Already supported.
2. **An era-drifting skin.** The HUD and dialogue box change paper
   with the eras: xerox grain and ballpoint (I), CRT glow and muddy
   flats (II), Arches cold-press and watercolor bleed (III–IV). The
   main menu already assigns skins per volume; per-chapter skin
   would be new.
3. **A strip-panel presentation** for the dailies: the four-panel
   grid as the scene format, typewriter text inside balloons, the
   signature mark drawn at the end of each week. This is the
   player-canon candidate (the player draws the strip) and the
   largest engine lift.

Recommendation for prep: assume (1) for authoring; keep (2) and (3)
open until the first act is scripted and read.

## The player canon (reserved; sketch)

**The player draws the strip.** Each in-fiction week is a hand: the
player picks which noticed things become the four panels, which
week gets a Sunday landscape instead of a joke, and which mark
signs the page (gull, crab, flat stroke, three-legged scruff).
Choices are not win/lose. They decide what the retrospective
contains in 2027 — which is to say, what got noticed. The unlock
web is the archive.

## Not yet written

No scene JSON. No `index.json` entry. No bg or CG paths. No
`_ART_MANIFEST.md`. The next prep step after the user reads this
is a scene-id list agreed in this file, then `vol10_ch0_*` stubs.
