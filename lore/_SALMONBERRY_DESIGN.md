# SALMONBERRY · DESIGN DOC

**Stick #21 · Oneironautics Inc. · Portland, OR · 1992**
**Made by:** Amelie Rocha, her most personal game, right after Fey
Faire (1990). The look bar is rich full-res painted illustration in
Oneironautics' field-guide-gouache house style, NOT flat vector —
and NOT our-timeline retro (per THE CORRECTION in the aesthetic
bible: slowsticks are sophisticated modern games from an alternate
timeline; no era-filter degradation).
**Genre stamp:** RPG / ADVENTURE · **Subtitle:** a year on the coast
**Preset:** `oneironautics` (field-guide gouache, `look_mode` 1)
**Status:** BUILT · playable_v1 (2026-07-22) — host + the year loop.
Full town overworld + the central arc are waved (see BUILD).

Read `_SLOWSTOCK_AUTHORING_PLAYBOOK.md`, `_SLOWSTICK_AESTHETIC_BIBLE.md`,
and `_SLOWSTICK_CATALOG_ROADMAP.md` (the canon lattice) before touching.

---

## The ask (user, 2026-07-22)

> "a slowstick game that's part adventure part rpg about living in a
> small rural coastal Oregon town in the 1960s."

## The pitch

The studio's most personal and most ambitious game: a year in the life
of a kid in the fictional cannery town of **Salmonberry, on the mid
Oregon coast, 1963–1964.** Part adventure (a walkable town, people with
stories, a mystery that runs the length of the year), part RPG (you
grow not by fighting but by LIVING — the aptitudes of a coastal life,
a web of bonds with the townsfolk, a naturalist's journal of the
coast). No combat. The stat that matters most is how well the town
knows you by June.

It is Oneironautics doing what Oneironautics does — the Oregon coast,
the tide, memory, a way of life ending — at full length for once.

## The frame · a year between two waves

The school year runs September 1963 to June 1964 (ten monthly chapters).
It is framed, without sensation, by the two events everyone from that
coast remembers:

- **November 22, 1963** — the Kennedy assassination. The distant world
  reaching a small town by radio; the cannery line goes quiet for an
  afternoon. A national "where were you," felt sideways.
- **March 27–28, 1964** — the Good Friday earthquake and the tsunami
  that ran the Oregon coast. The physical crisis the whole year has
  been quietly preparing you for: the night the water comes up the
  river, and what you have built — bonds, aptitudes, knowing the
  tide — is what lets you help save what can be saved.

Both are handled with the studio's restraint (the way Sweetgum handles
1976): felt through the town, never exploited. The year is warm and
small; the two events are the weather that passes through it.

## You

A grandchild sent to live with your **grandmother** in Salmonberry for
the year (a parent working away / recovering — kept vague, the classic
setup). The outsider's eye is the adventure engine: you arrive knowing
no one and spend the year becoming someone the town knows. Home base is
the grandmother's house at the edge of town, by the river mouth.

**The quiet meta-hook (mostly uncommented in-game):** the grandmother
sings. Her songs are the Portuguese folk melodies that thread the
entire catalog — Fey Faire's music box, Wilson's shanty, the Estuary
scores. Salmonberry is where those melodies were first heard; this is
the studio (Amélie Rocha's studio) making a game about the town those
songs came from. The catalog's whole soundtrack has a childhood, and
this is it. Stated only in the provenance + the true ending.

## Part RPG · you grow by living

**Six aptitudes**, raised by doing, never by fighting:

- **HANDS** — mending nets, fixing, the cannery line, carpentry.
- **SEA** — boats, tides, weather-sense, the bar, the bay.
- **WORD** — reading, letters, school, the library, the radio.
- **HEART** — talking, listening, earning trust.
- **WILD** — the woods, foraging, birds, the estuary edge.
- **GRIT** — cold, early mornings, hard work, staying with it.

**Bonds** — a relationship web of townsfolk (the Pirate Summer camper
web, aged up and slowed down). Each NPC has a bond level; deepening it
opens their stories, their help, and season-gated errands. The
grandmother is the deepest bond and the game's spine.

**A light economy** — chores and seasonal jobs earn a little money
(berry-picking in June, clamming on the minus tides, the cannery line
in the run, deliveries) and raise aptitudes. Money buys small things:
a library card, boots, a birthday gift, a bus ticket home.

**The journal** — a naturalist's "book of the coast" (birds, tides,
plants, weather signs, the town's own lore) is the collectible, the
direct descendant of Estuary 2's field journal and Estuary 1's report
card: the game grades the COAST you noticed, not you.

## Part adventure · the town and the thread

- **The town** (waved): a walkable Salmonberry — the harbor and the
  cannery, Main Street (store, café, library, church), the school, the
  grandmother's house at the river mouth, the beach, the north bluff,
  the woods and the estuary edge, the jetty and the bar. Reuses the
  Pirate Summer / Estuary 2 tile engine and walk cycles.
- **The through-thread** (waved): a mystery that runs the year — the
  boat that went out in the fall and did not come back, whose loss the
  town does not talk about, and which the grandmother knows more about
  than she says. Following it deepens specific bonds and the journal,
  and it resolves the same Good Friday night the water comes.
- **Seeds toward 1976** (the catalog's braided thread): a traveling
  show passes through in the summer of '64 — small, harmless, a Ferris
  wheel on the cannery lot — twelve years before the Faire that took
  Amélie's sister. Uncommented. `salmonberry_faire_seen`.

## Structure · ten months

Each month is a chapter: a **month card** (the month, a seasonal line,
and for November and March the real-history beat), then free choice —
pick an **activity** from the season's pool (work / explore / visit
someone / follow the thread). The choice passes the month; aptitudes,
bonds, money, and the journal move; a short outcome line lands. Some
activities gate on aptitude / bond / season / money.

This is the Estuary-1 "one meaningful choice per turn" loop grown a
second and third axis (bonds + journal), data-driven so the town can
expand without engine work. v1 ships this loop end to end; the waved
overworld later becomes the "explore" activities' destination.

## Endings · the register (who the town knows in June)

Resolved from how you spent the year (the Tideline-register pattern —
the ending emerges from your allocation, no win flag):

| register | condition | reads as |
|---|---|---|
| **THE HANDS** | high HANDS/SEA/GRIT + strong town bonds | you became useful; you belong here now |
| **THE LISTENER** | high HEART/WORD + deep bonds | you learned the town's stories; you are its memory |
| **THE KEEPER** | the journal near full | you noticed the coast; you kept it |
| **THE LEAVER** | thin bonds | you did your year and go home, changed but apart |
| **THE SONG** (true) | grandmother bond full + all her songs heard | you carry the melodies out; the catalog's whole soundtrack begins here |

Tokens: `salmonberry_finished` always; `salmonberry_hands` /
`salmonberry_listener` / `salmonberry_keeper` / `salmonberry_the_song`;
`salmonberry_faire_seen` (the 1976 seed); `salmonberry_the_wave`
(helped the night the water came). `canon_vars.salmonberry_result`.

## Canon lattice fit

- **Studio/year:** Oneironautics, 1992 — right after Fey Faire
  (1990). **Amélie Rocha's most personal game**, made while grieving
  the loss she never named: her grandmother's town, admitted once.
  (Retconned from 2006 on 2026-07-22 — the studio chronology and
  Rocha's arc demand the early-90s date.)
- **Setting era:** 1963–64 — earlier than any studio; this is a period
  piece, a memory reconstructed, not a contemporary game.
- **Coast geography:** the same fictional mid/south Oregon coast as
  Northwind Harbor (the harbor town, up the coast) and the Estuary
  games' estuary (downriver). Salmonberry can name the harbor town and
  the county seat in passing; do not contradict Northwind Harbor's
  established details.
- **Music:** the grandmother's melodies ARE the catalog's recurring
  Portuguese folk themes (canonized as Amélie's grandmother's in the
  roadmap). This game is their origin.
- **Unlock:** a late capstone — `unlocked_by_count_of_finished_min: 4`
  (surfaces once the player is invested in the shelf).
- **Shelf slot:** shelf 1, slot 7.
- **Provenance (Olaf):** *"Ines gave me this one herself. She said it
  was the only one that was true. I did not ask true about what."*

## BUILD

- **v1 (BUILT 2026-07-22):** host (contract, save, title, ending
  register) + `SalmonberryYear` data-driven month loop (aptitudes,
  bonds, money, journal, the Nov + Mar beats, five-register ending) +
  `activities.json` + `npcs.json`. The smallest complete version of the
  whole idea (the Estuary-1 discipline).
- **Wave A · the town overworld (DONE 2026-07 · v1):** walkable
  Salmonberry on the E2 MudflatWalk pattern (one Control, painted in
  _draw, SlowstockSprite kid walker — the rust coat Vovo had waiting).
  Eleven places on one screen (Vovo's house at the river mouth, Main
  Street: store/cafe/library/church, Estelle's gray house, the school,
  the woods band, the dock, the cannery on pilings, the beach path);
  the season repaints the palette as the year turns. A WALK INTO TOWN
  button on every month menu opens it as a child overlay (the
  combat-overlay pattern — the year loop never loses its place); E at
  a place lists that month's eligible activities THERE (same
  activities.json data, new `loc` field), choosing spends the month
  through the same _on_activity path; empty places give flavor lines.
  Bond warmth shows as a gold dot at a person's place. Deck-verify:
  walk feel, palette per season, place layout legibility.
- **Wave B · the boat that didn't come back (DONE 2026-07-22):** a
  bond-gated clue thread (estelle_light from sitting with Estelle;
  del_saw / iris_record / estelle_name surfaced by deepening those
  bonds), read back in the Book of the Coast. At 2+ clues it opens a
  fourth wave-night choice — go straight to Estelle, because you know —
  and it deepens the ending coda by how far you followed it. Also this
  pass: bonds now UNLOCK activities (`require_any` — e.g. Del's skiff
  via sea OR the del bond; boathouse-radio and county-records are
  bond-gated), and a Book-of-the-Coast viewer reads your journal +
  what you know.
- **Wave C · the wave** — the March '64 tsunami as a real, playable
  crisis: what you saved is what you'd built.
- **Wave D · deepen the roster (SHIPPED 2026-08-31):**
  - **Three new townsfolk** fill the cast's missing registers: JUNE
    (Manny's daughter, your own age — the peer bond an all-adult web
    lacked; the fort by the creek), MISS ALDER (the schoolteacher,
    first year, bonded via school_day), OPAL (the post office —
    letters home, the two-cent tax on having things to say).
  - **THE ERRAND SYSTEM** (errands.json + engine): 14 one-shot,
    bond-gated, season-windowed jobs — what deepening a friendship
    UNLOCKS. Same check/outcome vocabulary as activities plus
    errand:true (tracked in state.errands_done), require {bond,min},
    months = the window. At most two offered per week,
    soonest-closing first; a closing window says so. Caulking Del's
    skiff, the jetty light in the storm season, the Thanksgiving pie
    run, Boyd's smoke shed overnight, Estelle's attic, the pastéis
    with Vovo, the pageant, June's bluff dare, Opal's unclaimed
    parcel, the show with June, properly.
  - **The show is a three-beat June arc** ('76 seed): the posters go
    up (9,1) → the show (9,2) → the lot after (9,3, the ring of
    yellow grass). And the seed is EARNED now — salmonberry_faire_seen
    was granted unconditionally at year end (a bug); it now requires
    actually standing on that lot (travelling_show or june_show_day
    sets flag faire_seen; the host gates the token on it).
  - **A shipped bug the sim exposed:** JSON numbers parse as floats
    and Array.has(int) compares typed — [0.0,1.0].has(1) is FALSE —
    so every month-gated activity (clamming, the fall cannery line,
    berry picking, row the bay, storm watch) had NEVER appeared in
    the week menu since v2 shipped. SalmonberryTown already guarded
    both types; the Year now compares as ints.
  - **Day-one sim driver** (SalmonberryYearSim): plays the whole year
    through the real UI, errands-first, resting when worn, crisis
    skipped via the no-rescue path; asserts ≥3 errands, ≥1 event,
    bonds grew. First honest run: 4 errands, 10 events, register
    KEEPER (the deeper year changed the ending — the system does
    what it is for).
  - **Wave D+1 (SHIPPED same day) · June at the wave night +
    letters-home:** at june ≥ 3 she runs Good Friday with you — at
    the gate before you reach the road, +25 crisis speed, rescues
    at 0.8 work (four hands), and she OPENS the cannery route (her
    father's crew is on that pier; previously helped_boat-only).
    The resolution knows: "the night Manny's girl ran the water.
    She always corrects them: we." Letters-home is a counted
    thread now (activity `counter` vocab → state.counters); six or
    more letters shapes the coda — the leaver who almost stayed
    ("the last letter said more about the town than about coming
    home") vs. homesickness resolving into belonging ("more of it
    could wait until summer").
  - Deck-verify: errand pacing and window reachability for
    ruth/iris/boyd/estelle under normal play; June's crisis feel.
- **Wave E · audio + art (DONE 2026-07-22, core):** the year bed
  `coast.wav` IS the Rocha melody quoted from `hnn_one_melody` at its
  source; `harbor_bell` SFX for Good Friday; ambient one-shots wired
  into the loop (gull/surf/cannery/cafe/page/season); hero images
  (title + the five ending registers) + shelf spine. Remaining
  (optional): per-season BGM variants and standalone ambient loops.
- **Deck-verify:** loop pacing, aptitude/bond tuning, register
  thresholds, the tone of the two real events.

## Why it belongs

Every Oneironautics game is a piece of this one: Estuary is its tide,
Northwind its harbor, the Tideline its coast, the recurring melody its
grandmother. SALMONBERRY is the studio finally making the whole thing —
the town those games all remember, in the year it was still itself,
before the wave and the highway and everything after. Their magnum
opus, and, quietly, an origin story for the catalog's own soul.

---

## v2 · THE WEEK LOOP (built 2026-07-27 · the depth pass)

User verdict on v1: "make one choice a month, twelve times? Really?"
v1's month-menu is gone. The month is now FOUR WEEKS, each a real
decision inside interlocking systems (SalmonberryYear.gd v2):

- **Energy (0–10)** — every activity costs it (tagged per-activity
  in activities.json); hard labor costs more than a week gives back
  (+2/week sleep). Going in worn thin is −2 on the work and the
  text says so. "Keep to the house" restores 5 and touches Vovo's
  bond — rest is a real choice, not a skipped turn.
- **Weather** — rolled per week from per-month climate tables,
  deterministic from the save seed (no reroll-scumming). Storms
  close the bay (clamming/rowing disabled with the reason shown);
  minus tides supercharge the flats; rain taxes outdoor work unless
  you bought the slicker. The glass forecasts one week ahead —
  planning information, not trivia.
- **Money is owed, not just earned** — $2 board into the flour tin
  every month; an empty tin strains the household (strain counter +
  Vovo bond −1, and ≥3 strained months marks the year's coda).
- **Shown checks** — activities roll aptitude + luck(0–2, seeded) +
  weather/gear mods vs. the work's difficulty, breakdown printed
  ("sea 2 + luck 1 +2 minus tide vs. the work 2 — a strong week").
  Strong pays bonus money/aptitude; rough halves pay and teaches
  grit.
- **The general store** — clam gun, rain slicker, bicycle (+1
  weekly energy), guitar strings (songs double), field glasses.
  Gear changes what weeks can do; browsing doesn't spend the week.
- **Nine calendar events (events.json)** — one (month, week) slot
  each, gone if missed: the fall run's biggest day, the grange
  dance, the vigil, Christmas Eve, the lowest tide, THE BOAT OFF
  THE BAR (a stakes check — success sets helped_boat and a new wave
  -night option + coda line), rebuilding week, Salmonberry Sunday,
  the travelling show.
- **Bond decay** — friendships untouched for 8 weeks slip a point,
  with a line. Maintenance is play.

The wave night, the boat thread, the book, the town overlay, and
the five registers are unchanged — they just sit on 40 decisions
now instead of 10. Old v1 saves upgrade in place via boot()
defaults.

---

## WAVE C · THE NIGHT, PLAYED (built 2026-07-28)

March is no longer a menu. The bell rings and you are IN the
walkable town: eighteen seconds of slack while the water is out
(the bay drains to mud on screen), then the flood climbs the map
from the bay — the dock drowns first, so the boats are the first
hard choice — and every rescue roots you in place for real seconds
(a progress ring) while the water keeps coming. Reach targets and
press E:

- THE FLEET (dock, 6s) — gated on sea ≥3 or Del ≥2, same as ever.
- THE ONES THE FLEET FORGOT (cannery, 5s) — only if you went out
  for the Ida Rose in February.
- THE GRAY HOUSE (Estelle, 5s) — gated on the bond, the heart, or
  the thread; arriving WITH the thread knowledge upgrades the
  scene to the told_estelle ending.
- VOVO'S HOUSE — E ends the night up the hill, on your terms; if
  the water reaches her porch first, the night ends itself at a
  run.

The bicycle bought in October is 240 speed instead of 190 tonight
— the year's build is literally how fast you can run. Ineligible
targets explain themselves in fiction ("you don't know the bar
well enough to be more than in the way"). Multiple rescues are
possible with good routing; every one writes through the same
reward paths the old menu used, so registers, codas, and tokens
are unchanged. ESC does not work: "there is no putting this night
down."
