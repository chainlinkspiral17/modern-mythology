# SLOWSTICK CATALOG ROADMAP

Full plans for the two early Estuary sticks (currently shelf stubs
with "playable acts deferred"), plus six imagined slowsticks that
fill the catalog's genre, era, and studio gaps — every one built
off established lore and aimed back at the meta-narrative.

Every stick below now has a FULL design doc (look · sound ·
playstyle · ambition · build): `_ESTUARY_1_DESIGN.md`,
`_ESTUARY_2_DESIGN.md`, `_NORTHWIND_HARBOR_DESIGN.md`,
`_BASILICA_OF_WIRES_DESIGN.md`, `_SWEETGUM_DESIGN.md`,
`_RIFFMASTER_MELODY_CLUB_DESIGN.md`, `_HANE_NO_NIWA_DESIGN.md`,
`_PATIENT_MISTER_GLASS_DESIGN.md`. This file remains the index
and the canon lattice; the per-stick docs carry the depth.

Read together with `_ESTUARY_3_DESIGN.md` (studio history),
`_SLOWSTOCK_AUTHORING_PLAYBOOK.md` (how to build any of these),
and the library stubs in `godot/resources/games/vol7/library/`.

---

## The canon lattice (fixed points · do not contradict)

**Studios**
- **Oneironautics Inc.**, Portland OR · active by 1988 (Northwind
  Harbor) · Fey Faire 1990 · Estuary 1 2001 · Estuary 2 2002 ·
  Pirate Summer 2002 · Estuary 3 + Mrs. Wu's Garden Oct 2003 ·
  The Tideline 2004 · Estuary 4 2005. Hardware: the Slowstick
  (Rev 2 by the late 80s).
- **Astro-Cortex Software**, Culver City CA · The Earthman
  Chronicles 1985 · staff: senior engineer J.F., junior QA
  A. (Amélie) Rocha.
- **RANCH**, San Francisco · founded on two ex-Oneironautics
  designers who left in 2000 · Kwik Stop Manager 2002 · Sam's
  Summer Shifts 2003 · made manager-sims commercial.
- **Meridian Heritage Interactive**, New Portland Arcology ·
  licensed the Oneironautics catalog 2041 · Tideline Survey 2048.

**People**
- **Amélie Rocha** (b. ~1965): Astro-Cortex QA 1985 (the
  Corrections, with J.F.), joined Oneironautics 1986 as a junior,
  Fey Faire creative lead 1990 at 25 — written while grieving a
  loss she never publicly named. Her older sister went into a
  traveling fairy carnival in **1976** and did not come out. The
  Portuguese folk melodies in Fey Faire's music box and Wilson's
  shanty are her grandmother's; she has put that grandmother into
  games for decades.
- **Ines Rocha** (b. ~1980, Amélie's niece): first job = Estuary
  1's tide-gate math (2001), first credit = four campers + Wilson
  Ashe in Pirate Summer (2002), junior per-species math on
  Estuary 2, welded Estuary 3 in a Labor Day weekend (2003),
  Mrs. Wu's Garden solo same October, The Tideline solo 2004,
  pitched Estuary 4 (2005).
- **Marc Ostrom**: composer on everything Oneironautics; lead on
  Estuary 2; built the studio soft-synth around the PDP Riffmaster
  kids'-toy voice.
- **Sarah Delahaye**: pixel artist; every sprite in the early
  sticks. The 2001 studio was these three people.

**Threads the catalog keeps braiding**
1976 (the Faire, Camp Sweetgum, Nika Voss) · 220 Hz (Amélie's
ROM-resistance channel, born at Astro-Cortex) · the eight-pointed
star (the Order, leaking across publishers) · the Rocha melodies ·
the SAM VS SAM rivalry · Olaf's provenance notes · Tem reading the
shelf from 2048.

---

# PART I · ESTUARY 1 (Oneironautics, 2001) · full plan
### STATUS: BUILT · playable_v1 (2026-07) · host + EstuaryOneLoop,
### 8 stem-mix WAVs, 4 heron stances, report card + hidden Week 13,
### tokens emitted AND consumed (Jules line in E3 Act 2 · fifth-
### season grace beat in E3 Act 4)

**Genre stamp:** SIMULATION / SCHOOL LIBRARY ·
**Subtitle:** the very small first one · **Length:** ~2 hours

### The one-control thesis

The entire game is a single lever: the tide gate. Twelve weekly
turns. Each week you set the gate — OPEN, HALF, or CLOSED — and
watch what the estuary does about it. Three species respond on
coupled curves (Ines's actual first-job math, reconstructed):

- **CHUM FRY** want the gate open on the ebb · they are trying to
  leave · a closed gate in weeks 4–6 strands the out-migration.
- **MUD SHRIMP** want stability · every gate CHANGE costs them ·
  the best shrimp summer is the one where you barely touch it.
- **THE HERON** wants whatever eats well · she is the readout ·
  where she stands each week tells you what the water is doing
  before the numbers do.

There is no score. There is no failure state. The design document
(reconstructed) contains one sentence in Ostrom's hand: *"the
player should end the game knowing they were RESPONSIBLE for
something, without once being told they were."*

### Structure

- **Weeks 1–12**: gate choice → one screen of consequence · the
  heron moves · Delahaye's three sprites at four tide states ·
  one Ostrom drone that adds a voice per species doing well.
- **The report card**: the ending screen is a school-report-style
  card the game writes about your estuary — not about you. Grades
  for WATER, PASSAGE, PATIENCE. The PATIENCE grade counts how many
  weeks you resisted changing the gate. This is the screen the
  2001 school-library teachers loved and the 2001 reviewers
  called "a screensaver you're responsible for." Both were right.
- **Week 13 (hidden)**: exists only if the gate was touched two
  times or fewer all summer. One extra screen: the estuary at
  night, no UI, the drone with all three voices, and one line —
  *"it was doing this before you, too."* The seed of Estuary 3's
  fifth season, three games early.

### Why it underperformed (design-as-lore)

School-library run ~3,000, OPB pledge run ~2,000. No goals, no
fail state, one control — 2001 had no vocabulary for it. The two
designers who left for RANCH in 2000 had argued for a scoring
system and a park-ranger frame during the pilot; the refusal is
why they left, and the refusal is the studio. Kwik Stop Manager
is, structurally, Estuary 1 WITH the score attached — that is the
whole schism in one sentence.

### Cross-Oneironautics hooks
- The tide-gate toggle SFX already exists (`tide_gate_toggle`).
- Report card PATIENCE grade → lore token `estuary_1_patience_a`
  consumed by Estuary 3's Act 2 planner (a one-line acknowledgment
  from Jules).
- Week 13 seen → the fifth season in Estuary 3 opens one beat
  earlier.
- Tem's grandfather's loyalty ("he was an Estuary 1 person")
  finally means something the player has felt.

### Build notes
2-hour scope = one host + one loop scene (the Sam's Summer Shifts
shape, 12 weeks, one choice per week, meters hidden). Three
sprites + heron positions from existing E3 Act 2 species assets.
One composition. Smallest possible build; highest lore density
per line.

---

# PART II · ESTUARY 2 (Oneironautics, 2002) · full plan

**Genre stamp:** SIMULATION ·
**Subtitle:** the summer at the mudflats · **Length:** ~6 hours

### Ostrom's game

Marc Ostrom's only lead credit. Where E1 is one lever, E2 is one
PLACE: a walkable top-down mudflat (the Pirate Summer overworld
engine, reused backwards in time — in-fiction, PS 2002 and E2 2002
shared the same team tech). June to September in twelve walks.

- **Twelve species**, each with per-week population math (junior
  Ines's sheets) · you don't control them · you WITNESS them, and
  witnessing is mechanical: a species you observe three weeks
  running gets a page in the field journal; journal pages are the
  collectible.
- **The radio weather**: a hand-crank radio gives the week's
  weather in Ostrom's synth-voice bursts · weather drives the
  math · players learn to hear a bad week for the shrimp coming.
- **The dredging subplot**: mid-summer, surveyor stakes appear on
  the flat. The county wants the channel dredged. The studio's
  first-ever NPC drama — four neighbors, a petition, one hearing
  scene — earnest, a little stiff, visibly the rehearsal for
  Pirate Summer's camper web. Three endings: DREDGED (the winter
  card shows the channel straight and the journal pages fading) ·
  BLOCKED (the flat as you knew it, and a neighbor who no longer
  waves) · THE COMPROMISE (half the channel; the game refuses to
  tell you if it was enough; Estuary 3's tide gate is downstream
  of this exact channel — the compromise is E3's status quo).

### Cross hooks
- The field journal is the direct ancestor of Pirate Summer's
  J-key journal — same layout, Delahaye's same 3×5 headers.
- Ending choice → lore token consumed by Estuary 3 Act 3's mill
  office (one line about "the '02 hearing").
- One of the four neighbors is a young **Jules** — twenty years
  before running the Kwik Stop.

### Build notes
Reuse: PS tile engine + walk cycles, E3 Act 2 species JSONs (add
per-week curves), beat-scene for the hearing. The most build-heavy
plan in this doc; schedule after E1.

---

# PART III · SIX IMAGINED SLOWSTICKS

Gap analysis first. Current catalog covers: nature-sim, manager,
camp CRPG, dark-fantasy RPG, occult CRPG, meditation walk, survey.
Missing: **puzzle-adventure (canon-promised)** · **horror** ·
**music/instrument** · **epistolary** · **detective** ·
**dungeon crawl** · a **non-US studio** · a **homebrew/outsider
stick** · anything on the shelf that is an ABSENCE.

## 1 · NORTHWIND HARBOR (Oneironautics, 1988)

*Already half-canon: it is the third cart at Camp Sweetgum, and
Sam plays Chapter One the year it shipped.*

**Genre:** PUZZLE / ADVENTURE · the studio's first stick.
Seven chapters = seven early mornings in a fictional Oregon coast
fishing town. A boy walks his uncle's dog through the harbor at
5:47 AM, gathering small everyday objects (a glove, a receipt, a
key that fits nothing yet) that resolve into gentle chained
puzzles by chapter's end. No dialogue trees — the town talks AT
you while working, and listening is the mechanic: every puzzle's
hint was said aloud, once, by someone hauling a crate two screens
earlier. The dog (BOSUN) is the hint system; what he sniffs
matters.

**Meta-narrative:** the founding text of "slow." Amélie Rocha's
second credit (junior · she wrote the fish-cleaning station
dialogue). The harbor town is up the coast from the Stop-N-Go —
Sam's Summer Shifts' trucker drives through it. Chapter 7 ends at
a carnival poster on the cannery wall, dated 1976, half torn.
Amélie put it there. Nobody at the studio asked.

**Provenance:** Olaf's copy is the camp cart itself — he bought
the Sweetgum console lot at auction in 2011. Sam's 1988 save is
on it. Chapter One's save is Tem's most-examined object in Vol 7.

**Build:** beat-scene chapters + object-gathering = the Fey Faire
midway cell pattern with pockets. Cheap; high priority.

## 2 · BASILICA OF WIRES (Astro-Cortex, 1987)

**Genre:** FIRST-PERSON DUNGEON CRAWL / SIGNAL HORROR — the crawl
gap and the horror gap in one.

J.F.'s game — the Earthman senior engineer — made in the two years
after A. Rocha left for Portland. A broadcast engineer descends
into a cathedral-sized longwave transmitter built inside a
mountain in 1938 and never fully decommissioned. Wireframe
corridors of wire and porcelain. No monsters: the hazard is
SIGNAL — standing waves that scramble your map, rooms that only
exist while a given frequency is live. The tuner is your sword and
torch. At 220 Hz, and only at 220 Hz, the corridors hold still.

**Meta-narrative:** 220 Hz canonized as J.F. and Amélie's shared
channel — the Corrections were hidden AT it in 1985, and Basilica
is J.F. broadcasting INTO it after she left: the deepest room
contains a message addressed to no one, in QA annotation format.
An eight-pointed star is etched on the master breaker, uncommented
— the Order leaking into a second publisher's catalog. Astro-Cortex
folded in 1989; this was the last thing they shipped.

**Provenance:** THE ABSENCE ON THE SHELF. Olaf never found a copy
— fewer than 900 exist. The shelf slot holds his hand-labeled
EMPTY sleeve ("still looking · 30 yrs") — the stub renders as a
wanted poster. In 2048, Tem can find one listed at auction for
more than the cabin is worth. Whether Tem buys it is a Vol 7
present-day beat, not a slowstick beat.

**Build:** the one genuinely new engine ask (wireframe crawl).
Defer; ship the stub-as-absence immediately — the empty sleeve IS
content.

## 3 · SWEETGUM (no publisher · zine-traded homebrew, 1996)

**Genre:** WAITING HORROR / DOCUMENTARY — the horror gap, done the
slowstick way.

One night — August 14, 1976 — at Camp Sweetgum, played as the
night watchman. Real-time-ish: 9 PM to 6 AM in forty minutes.
Almost nothing happens. You walk rounds, check padlocks, log
entries in the watch book (typed live by the player — the log
persists between runs). The horror is structural: the player
knows the date. The game never says it. Around 3 AM there are
exactly three sounds out on the water, and a light on the island
that the log template has no field for.

Made by a survivor's kid on homebrew EEPROM, traded at zine
fairs, C&D'd by Oneironautics' lawyers in 1997 (the studio was
already quietly researching what became Pirate Summer — the C&D
is the paper trail proving they knew about Nika Voss earlier than
they ever admitted).

**Provenance:** Olaf's copy is a burned EEPROM in a hand-labeled
case, gifted by the author at a Portland zine fair. His provenance
note is one line: *"I asked her why. She said: so it's someone's
JOB to stay awake."*

**Build:** one scene, real-time timers, a typed log widget.
Small; enormously heavy. Gate it: unlocks only after Pirate
Summer's 1976 facts are discovered.

## 4 · RIFFMASTER MELODY CLUB (PDP Toys, 1991)

**Genre:** MUSIC / INSTRUMENT — the music gap, and canon
compression: the PDP Riffmaster kids' synth already exists in-repo
(`PDPRiffmaster.gd`), and slowstick_synth is documented as built
around its 3-oscillator voice.

The toy company's own slowstick: twelve "club meetings" that
teach the Riffmaster voice — saw, saw, sub-triangle, one envelope
— through call-and-response with four cartoon club members. The
final meeting is an open mic: the player's own loop, recorded to
the save file. In-fiction, Marc Ostrom moonlighted on it
(uncredited, contract) and kept the voice when he built
Oneironautics' audio pipeline — every Estuary score is played on
the instrument this children's stick teaches.

**Meta-narrative:** the Rosetta stick. A player who finishes it
can HEAR the whole catalog differently. Final club member's line:
"now every song you ever hear on this machine is partly yours."

**Provenance:** Tem's grandfather bought it for Tem's parent.
The save file still holds a loop recorded by a seven-year-old.

**Build:** the PDPRiffmaster scene already exists — wrap it in a
host with twelve lesson beats. Mostly done before starting.

## 5 · HANE NO NIWA · THE FEATHER GARDEN (Yumemi Denshi, Kyoto, 1993)

**Genre:** SHRINE-KEEPING / EPISTOLARY — the non-US studio and the
letters gap.

Japan's slowstick scene, canonized. You keep a neglected hilltop
shrine through four seasons: sweep, mend, leave offerings. The
core mechanic is CORRESPONDENCE — a yokai (never shown; feather
evidence suggests a tengu) answers your offerings with letters,
one per season, in the player's own offering-vocabulary. What you
give shapes what it can say.

**Meta-narrative:** Amélie Rocha corresponded with its designer,
Yumemi's founder **Sachiko Ono**, from 1991 — the letters are why
Fey Faire's roster reaches to kitsune, tengu, kappa, yuki-onna,
kodama: her half of a conversation across the Pacific about
whether the numinous localizes. Ono's half is this game; its
fourth letter contains one English sentence, uncommented: *"your
carnival is known here also."*

**Provenance:** Olaf's copy is the 1995 US grey import with a
photocopied fan translation folded in the case — annotated in two
hands. One of them is Amélie's.

**Build:** Talikan-hub pattern (locations + one action each) +
letter renderer (Codex manuscript-tab pattern). Moderate.

## 6 · THE PATIENT MISTER GLASS (RANCH, 2004)

**Genre:** SLOW DETECTIVE — the mystery gap, as RANCH's answer to
the question "what else does patience monetize?"

Fourteen evenings. One suspect: Mister Glass, retired ferry
clerk, suspected of a thirty-year-old embezzlement nobody else
remembers. You interview him for fifteen minutes a night in his
kitchen while he cooks. The mechanic is the SAME question asked
on different nights returning different answers — the
contradiction ledger builds the case, or builds his innocence, or
builds the third thing (the money went to something that will
make the player close the ledger themselves). RANCH's manager-sim
patience turned inward: the drawer you're counting is a man.

**Meta-narrative:** RANCH's ex-Oneironautics founders reaching
back toward the studio they left — reviewers called it "RANCH's
Estuary," and both studios hated that. The rivalry's détente:
Ines Rocha named it publicly as her favorite stick of 2004, the
year of her own Tideline. The ferry Glass clerked is the one
visible from Pirate Summer's north bluff.

**Provenance:** Olaf bought it new, finished it once, never
replayed: *"you don't reread a confession."*

**Build:** SSS week-loop shape with an interrogation ledger
(promise-reckoning UI, inverted). Cheap-to-moderate.

---

## Suggested order of construction

1. **Estuary 1** — smallest, deepest lore payout, one lever.
2. **Northwind Harbor** — canon-promised; the cart is already at
   camp; Chapter One must match Sam's save.
3. **Riffmaster Melody Club** — engine already in repo.
4. **The Patient Mister Glass** — SSS machinery reuse.
5. **Sweetgum** — small, but gate behind PS discoveries.
6. **Estuary 2** — the big tile-engine reuse project.
7. **Hane no Niwa** — moderate; letters system is new.
8. **Basilica of Wires** — stub-as-absence NOW (empty sleeve);
   the wireframe crawl whenever the engine appetite exists.

Every stick above should ship with: a library stub (schema per
README), cartridge sprite, one BGM composition, lore tokens in
and hooks out through OneironauticsTokens, and an Olaf provenance
note — the shelf is the frame story, and the note is where the
frame lives.
