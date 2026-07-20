# FEY FAIRE — mechanics

Combat, death, checkpoints, progression, resource economy.
See also `_FEY_FAIRE_DESIGN.md` for the master overview and
`_FEY_FAIRE_FACTIONS.md` for the standing / hierarchy layer.

## Core principle

**Combat is what happens when dialogue fails.**  Every fey the
player fights had a negotiation branch they could have taken.
Every negotiation is a puzzle solved with items, promises,
names, and quotes.  Combat is loud, expensive, and often the
worst outcome for both sides — the fey may spare you, take
something specific, and let you leave.

The player who FIGHTS everything is playing the game badly.
That's a valid failure state (the "Cruel Prince" bad ending).
The player who NEGOTIATES everything is playing the game well
but not perfectly — some feys will not negotiate with a
protagonist who has never spilled fey blood.

## Combat structure

### Party
- Protagonist + up to 3 recruited feys, 4 total.
- Cannot dismiss recruited feys except at the Bookstall (Bookstall
  is a specific ritual · costs the protagonist a memory).
- Party order matters · front row takes physical hits, back row
  takes magical hits.

### Turn structure
- Speed-order round-robin, highest speed goes first.
- Each combatant has ONE action per turn:
  - `STRIKE` — physical attack, damage type = combatant's damage_type
  - `CAST` — spend SP on a named skill
  - `USE` — consume an item from inventory
  - `TALK` — attempt in-combat negotiation (protagonist only)
  - `GUARD` — halve incoming damage this round
  - `FLEE` — attempt to leave combat, cost varies by fey
- No round-per-round consumable use.  Items burn a turn.

### Damage types (rock-paper-scissors triangle)
Six types, arranged so that each has one common weakness and one
common resistance:
- **Iron** — physical strike
  - weakness: no universal weakness (iron is what most feys fear)
  - most feys resist their damage type; iron cuts through
- **Bone** — physical strike (Unseelie signature)
  - beats: Wildfey, Seelie retinue
  - loses to: Song
- **Flame** — magical
  - beats: Wildfey, Green Man's court
  - loses to: Salt
- **Song** — magical (Seelie signature)
  - beats: Unseelie court
  - loses to: Iron
- **Salt** — magical
  - beats: sea-court (Ondine, Kelpie, Selkie, Nuckelavee)
  - loses to: Flame
- **Word** — magical (protagonist signature, Shakespeare-fed)
  - beats: fey of high `wit` (bosses, Puck, Mab)
  - loses to: no universal loss (Word is asymmetric)

### No level curve
- Nothing has an XP bar.
- Protagonist's stats improve ONLY through:
  - Recruiting more feys (party gets bigger + more skills available)
  - Learning more Shakespeare quotes (RECITE menu grows)
  - Buying / finding items (equipment slots: head, hand, pocket)
  - Court-favor buffs (see `_FEY_FAIRE_FACTIONS.md`)
- No stat inflation.  A first-hour fight and a night-6 boss fight
  both matter, both hit hard.

### Combat is HARD
- Every combat encounter is authored, tuned, and deadly.
- A basic tier-1 fight (Mustardseed enraged) can kill a fresh
  protagonist in three rounds.
- A tier-3 fight (Titania) can kill a full party in four rounds
  if the player fights without preparation.
- The design goal is: **the first time a player engages any fey
  in combat, they SHOULD lose** unless they've done substantial
  prep.  Prep means: recruit a fey with the right damage type,
  buy the right item, learn the right quote, get the right
  Court's blessing.

### Combat resolution
- Text-only descriptive combat log ("the Kelpie shudders",
  "Puck laughs off the strike").
- HP bars visible for both sides.
- No damage numbers.
- Status effects (charmed, dizzy, mused, bewitched, named) surface
  as descriptive text plus a small icon on the target's portrait.

## In-combat negotiation

The protagonist can attempt `TALK` on any turn.  Success chance is
based on the fey's current `AP`, their `charm` vs. protagonist's
`wit`, and any modifiers (fey's Court disposition, held promises,
completed favor).

When `TALK` succeeds mid-combat, combat pauses and negotiation
opens with the four branches (OFFER / PROMISE / THREATEN / RECITE).
See feys.json for each fey's negotiation data.

When `TALK` fails, the fey attacks that turn instead of doing
its scheduled action (which may HELP if the fey was queuing a
massive attack).

## Puzzle mechanics

Puzzles happen at three scales:

### Booth puzzles (small, gate a single fey's recruitment)
Every named booth has a puzzle to WIN that fey's recruit-track.
Examples:
- Cobweb's test-your-strength: swing TRUE (a rhythm-based timing
  puzzle) not hard.  Three tries per night.
- The Erlking's wheel: don't land on sectors 1, 3, 5, 7, 11, 13
  (which say specific bad things).  Player has SOME control by
  timing the spin-brake.  Landing on sector 16 (CHILD) triggers
  the Erlking boss encounter immediately.
- Puck's coin-in-a-glass: three rounds of a shell-game logic
  puzzle.  Puck cheats.  Solving it fairly recruits him.

### Mirror gate puzzles (medium, gate a Fairyland sub-realm)
Each of the six mirrors requires a specific puzzle solved BEFORE
you can cross.  See `_FEY_FAIRE_ROUTES.md` for detail.  In brief:
- Rose Garden mirror: assemble a bouquet of specific flowers
  (six named roses in a specific order) at Peaseblossom's booth.
- Storm-Wracked Coast mirror: recite a specific Tempest line to
  Ariel while the Ferris wheel is spinning.
- Court Beneath mirror: PROMISE something to a specific
  Unseelie fey (Redcap, Baobhan Sìth, or Sluagh) and DELIVER on
  it before crossing.
- The Green mirror: bring a real leaf from outside the Faire
  (this requires leaving the Faire and returning, which is a
  meaningful act).
- The Undertide mirror: win the strongman challenge (Caliban)
  fairly OR bribe him with a book.
- The Dream mirror: sleep at the sleep tent, which triggers a
  dream-scene negotiation with Queen Mab · she's the gate.

### Cross-fey puzzles (large, unlock ending paths)
Certain fey combinations produce ending-shaping puzzles.
Examples:
- The Titania-Oberon quarrel · if you recruit both, they will
  not be in your party together.  You must pick.  This choice
  locks Court alignment.
- The Sluagh's true name is the name of a dead relative.  If
  the boot questionnaire's dead-relative field is empty, the
  player cannot recruit the Sluagh without lying, and lying
  has consequences later.
- Recruiting the Ossory Wolf requires a Communion wafer,
  which is NOT available at the Faire.  The player must LEAVE
  the Faire and get one before night 5.

## Death and checkpoints

### Dying
- HP reaching 0 for the protagonist ends combat immediately.
- The party is dismissed to their manifestation booths (they
  are alive · they retreat).
- Protagonist wakes up at the current checkpoint (initially:
  the Gate).
- Lost on death:
  - All SP (drops to 0)
  - Half of gold
  - One specific inventory item chosen by the game (usually
    the most-recently-acquired non-plot item)
  - One "memory" (see below)
- Retained on death:
  - Party recruits (they remember you)
  - Promises made and kept
  - Quotes learned
  - Court standing
  - Puzzle progress (booth games you've won stay won)

### Memories
The protagonist has SIX memories on boot, set by the boot
questionnaire (favorite song / favorite meal / a specific
holiday / an argument with a parent / a first kiss / a fear
you don't tell anyone).

Each death consumes ONE memory.  The lost memory is REPLACED
in-game with a blurred paraphrase ("... a song you used to
hum?").  This is diegetic and gets uncomfortable.

Losing all six memories triggers the **BAD ENDING · YOU
FORGET WHY YOU CAME** on your next death.  The Faire keeps you.

### Checkpoints
Every recruited fey creates a **checkpoint at their manifestation
location**.  So:
- Recruit the Boggart → die → wake up at the Lost-and-Found.
- Recruit Ariel → die → wake up at the Ferris wheel.
- Recruit Queen Mab → die → wake up in your bedroom-that-is-a-dream.
- Recruit Cricket → die → wake up at the Gate (already the default,
  but Cricket makes this cleaner).

On death, the game picks the checkpoint deepest in your route.
"Deepest" is measured by shortest-path from Gate along the
midway graph.  So recruits at the mirror-side of the midway are
better checkpoints than the ones near the Gate.

### The pacifist route problem
A player who negotiates every fight never dies (no risk).  BUT:
- Some fey will not negotiate on first encounter.  They want you
  to have proven yourself.  Proving yourself sometimes means
  drawing blood.  Not always.
- The tier-3 bosses can be fought or talked-down.  Talk-downs
  require specific prerequisites (usually a promise fulfilled).
- The pacifist ending is one of the seven possible endings and
  requires zero fey KOs.  A fey the player has knocked out but
  NOT killed still counts as a KO for this run.

## Resource economy

### Gold
- Earned by winning booth games (1-5 gold each).
- Earned by successful negotiations that end with fee-payment
  from the fey (rare, high-charm).
- Spent at the Bookstall (books teach quotes, 2 gold each) and
  the Bakery (fresh bread, 1 gold, small HP heal).
- Half your gold is lost on death.  Save at the Fortune-Teller
  (2 gold to stash gold safely).

### Skill points (SP)
- Rest to restore.
- Rest requires being at a booth of a recruited fey · they let
  you nap.  You lose 5 gold per rest (the fey collects a tip).
- Full HP + SP restore.  ADVANCES ONE NIGHT.

### Prizes (inventory)
- Non-consumable trade items.
- Some prizes are consumed by OFFER (giving to fey).
- Some are single-use combat items (a Communion wafer thrown
  at the Ossory Wolf finishes him if the player wanted the
  hostile route).

### Promises
- Not a stat.  Not a slot.  A LIST attached to the save.
- Every unfulfilled promise gives -1 to future negotiation checks
  with any fey.  ANY fey, not just the promise-holder — the
  fair-folk gossip.
- Promises come due at CLOSING NIGHT.  Every unfulfilled promise
  becomes a specific dramatic scene · the fey shows up to collect,
  and the player must either pay in full or take the
  consequence.  Consequences vary by fey and can lock endings.

## The RECITE mechanic (Shakespeare quotes)

- Player starts with 3 quotes (see design doc for the starter set).
- Quotes are learned by:
  - Watching a Big Top show (one quote per show, one per night)
  - Buying paperbacks at the Bookstall (2 gold each)
  - Certain successful negotiations grant the fey's favorite
    quote as a gift
- Quote memory is UNLIMITED · learn as many as you can find.
- Each quote has one or more **tagged fey affinities** (e.g.,
  "Puck-friendly", "Titania-friendly", "any-Seelie").
- Correct-fey pairing: RECITE deals 2× damage or opens
  negotiation immediately.
- Wrong-fey pairing: RECITE deals 1× damage or nothing.
- Very-wrong pairing (Puck-friendly quote to Oberon): the fey
  misquotes back at you, damaging YOUR protagonist.

## Balancing philosophy

- No difficulty settings.  This is Dark Souls.  Everyone plays
  the same game.
- The difficulty CURVE is flat but the LEARNING curve is steep.
  A player who dies six times fighting Kelpie at night 1 has
  learned enough (about Salt damage, about iron horseshoes,
  about promise-carrying) to beat every subsequent Kelpie-
  adjacent encounter.
- Every death should teach a specific lesson.  If the player
  dies TWICE in the same way, the game has failed to signal.
- Failure states are AUTHORED, not RNG.  A fey with high evade
  might dodge 40% of the time · that's a mechanical difficulty
  point.  A fey that ALWAYS crits doesn't exist here.

## Open questions

- **Save scumming**: three save slots · quicksave button?
  RECOMMEND: no quicksave.  Slot saves only, at specific
  save points (Fortune-Teller booth · costs 2 gold to save
  · deliberately friction).
- **Difficulty**: no difficulty settings, but should there be
  an accessibility mode (auto-recite highest-affinity quote)?
  RECOMMEND: yes · gated behind a "signed writer's memoir"
  item found in the Bookstall on any playthrough after your
  first.  Accessibility mode is thus DIEGETIC.
- **Combat music**: one loop per Court, adapted from the
  ambient music of that fey's manifestation?  RECOMMEND: yes.
  Titania's combat music is the House of Roses ambient with
  a percussion layer.

---

## THICKENING PASS · addendum (2026-07-19)

User read on the build: "most promise, but the gameplay is thin."
A full survey confirmed it: negotiation auto-succeeded via
interchangeable branches, THREATEN was dead code (key mismatch:
read `known_names`, Host writes `known_true_names`), RECITE
ignored what you'd actually learned (`quotes_learned` vs
`unlocked_quotes`), the combat damage triangle was displayed but
never applied, the party did nothing in combat, gold had no sink,
and death cost almost nothing. The pass, two waves, all riding
data that feys.json/quotes.json already carry:

**Wave 1 · negotiation gets teeth.** The four branches become
four different prices with four different failure shapes:
- OFFER · you procure the fey's exact prize on the midway ·
  costs 1+tier GOLD (the Faire sells everything). Gold's first
  real sink. Can't afford it, can't offer.
- PROMISE · a fey reads your ledger: three or more outstanding
  unkept promises and they refuse — booth locked for the night.
  Caps promise-spam at three, making the other verbs necessary.
- THREATEN · needs the true name (key fixed). Tier 4+ feys
  answer the name with violence — negotiation drops into combat.
  Lesser feys submit: recruited, but resentful (-1 disposition,
  +2 UNSEELIE court regardless of their own).
- RECITE · needs a quote whose play matches their favorite or
  whose affinities name them/their court (key fixed, reads
  unlocked_quotes). The wrong play fails: -1 disposition, booth
  locked. Makes the Bookstall strategic and show playbill quotes
  matter on the pacifist path.
- UNIVERSAL FAILURE COST · a failed branch locks that booth
  until the night advances. Time is the currency.

**Wave 2 · combat gets its triangle.** New runs choose an
IMPLEMENT after the questionnaire (cold iron nail · salt packet ·
tin whistle · hawthorn sprig = iron/salt/song/word). ATTACK
applies x1.5 vs weakness, x0.5 vs resistance — the triangle the
readout always advertised. A SECOND action lets one recruited fey
act once per combat (their recruit_gift: heals if it heals, else
strikes with their damage type through the same triangle) — the
party finally fights. Losing costs half your gold on top of the
memory. THREATEN-fail is the organic door into all of this.

Deferred (next passes): booth puzzles, the designed death
checkpoint economy, connecting the ~75 orphaned feys to booths,
mirror-gate puzzles, Titania/Oberon exclusivity.

## DEATH / CHECKPOINT ECONOMY · wired (2026-07-20)

The "Death and checkpoints" section above was fully specified but
never fired: combat set `memories_lost += 1` and halved gold, then
silently routed to the Gate. Checkpoints were APPENDED on every
recruit/vanquish and then read by nobody. Now the whole loop runs.

- **A specific memory cracks, and it is named.** Death consumes the
  six memories IN THE TRAILER'S MIRROR ORDER (bedroom → song → meal
  → holiday → parent-argument → first-kiss), keyed off
  `memories_lost` so the mirror wall and the death screen never
  disagree. `FeyFaireHost.MEMORY_SLOTS` pairs each with a diegetic
  blurred paraphrase ("... a song you used to hum ..."); the same
  paraphrases now show on the cracked mirror in the Trailer.
- **You wake at the DEEPEST checkpoint, not the Gate.** The Host
  reads `FeyFaireMidway.MIDWAY` via preload (no instantiation),
  BFS-scores every cell's distance from the Gate, maps each
  checkpoint fey to its booth cell, and respawns you at the deepest
  one by setting `midway_cell` before reopening the midway. Recruits
  and vanquishes both open checkpoints, so a deep run is protected —
  the mechanic the design promised.
- **The purse spills, a keepsake falls.** Half gold (kept) plus the
  most-recent non-protected keepsake drops from your pocket
  (`PROSPERO'S WORD` is protected — earned, not carried).
- **The sixth death is terminal.** When the last memory goes, the
  Host sets `forced_ending = "you_forget_why_you_came"`; the death
  screen's button reads "sit down in the empty lot" and routes
  straight to that ending (FeyFaireEndings.boot honors a forced
  ending, skipping the Night-6 gather beats).
- **A death interstitial teaches the lesson.** New scene
  `FeyFaireDeath` names every cost and what survived (party,
  promises, quotes, court standing) — death rewinds LOUDLY now, per
  the "every death should teach a specific lesson" rule.

Rides existing machinery: the checkpoints array (already tracked),
the combat "loss" outcome, `midway_cell` restore-on-boot, the
endings scene. One new interstitial scene, no save-format change
beyond the transient `_death_wake_cell`/`forced_ending` keys.

Deferred still: booth puzzles, mirror-gate puzzles,
Titania/Oberon exclusivity, gold sinks beyond quotes/OFFER.

## BOOTH PUZZLES · wired (2026-07-20)

Three of the midway's carnival booths are now real games you must
WIN to earn the approach — the cell descriptions always promised it
("swing TRUE", "keep your eye on it", the wheel nobody beats). One
data-driven scene (`FeyFairePuzzle`), three distinct verbs, none of
them luck (failure is authored, per the balancing philosophy):

- **Cobweb · SWING TRUE · timing.** TEST-YOUR-STRENGTH. A mallet
  marker sweeps a bar; strike (button or SPACE) while it crosses the
  true band, three times, the band shrinking each hit. One miss and
  the bell stays silent. The only real-time puzzle (`_process`).
- **Puck · COIN IN A GLASS · memory.** Three glasses, a coin under
  the middle, a fixed deterministic swap script you advance through
  one blur at a time; name the glass at the end. (Tracking, not RNG —
  the swaps are authored so a careful player always solves it.)
- **The Erlking · WHEEL OF FORTUNE · deduction.** Four clues (even ·
  not a power of two · digit-sum in {3,6,9} · under ten) resolve to
  exactly one safe sector of sixteen. Pick it. Picking sector 16
  (CHILD) is the worst loss — a colder fail line.

Wiring: the three MIDWAY cells gain a `puzzle` field; the midway
shows "play their game" instead of "approach the booth" until
`puzzle_solved_<fey>` is set, then "· their game: won ·". The Host
`_open_puzzle` routes the new `play_puzzle(fey_id, puzzle)` signal.
- WIN → +3 gold (booth games are a gold source), +2 disposition,
  `puzzle_solved_<fey>` (RETAINED ON DEATH — puzzle progress stays
  won), token `fey_faire_puzzle_won`, then straight into the
  negotiation the game earned.
- LOSE → the flap shuts for the night (booth_locks) and -1
  disposition, exactly like a failed negotiation.

Rides existing machinery: the special-booth button pattern (fortune/
bookstall), booth_locks, the disposition/token feeds. One new scene,
no save-format change beyond the per-fey solved flags.

Deferred still: mirror-gate puzzles, Titania/Oberon exclusivity,
gold sinks beyond quotes/OFFER/puzzles.

## THE SUNDERING · Titania/Oberon exclusivity + mirror-gate (2026-07-20)

The estranged king and queen were both freely recruitable, which
made the a_rose (needs titania_liked) and a_red_cap (needs
oberon_liked) endings a matter of doing both rather than choosing.
Now the choice is real, with a hidden third way behind a mirror.

- **The Sundering · default exclusivity.** Recruiting one royal sets
  `<partner>_barred` in the Host recruit path. The barred royal's
  midway booth shows "· sundered · you took Oberon, and this one will
  not look at you ·" with no approach button — no negotiation path
  reaches them. A permanent, run-level fork (persists across death;
  clears on a new run). Titania is seelie/Night-4, Oberon is
  unseelie/Night-5, so the fork also splits your court trajectory.
- **The mirror-gate · reconciliation.** The barred booth grows a
  "broker the peace · spend Prospero's Word" button ONLY if you have
  (a) walked Mirror 6 · THE DREAM (`mirrors_completed` has
  `mirror_6_dream` · the one realm where they are married) AND (b)
  still hold `prosperos_word` — the keepsake whose own flavor text
  says "spend it on a night when the choice is between two things you
  want." Brokering sets `royals_reconciled`, un-bars both, consumes
  the Word, fires `fey_faire_royals_reconciled`, and drops you into
  the second royal's negotiation. Both can then join · both boons,
  both dispositions, both courts lifted.
- **Why Prospero's Word.** It is granted when Prospero wakes (NG+),
  so reconciliation is a mastery path — the default first-run
  experience is the hard choice, and only a player who has gone deep
  (walked the dream, woken Prospero) can hold the whole court.

Rides existing machinery: the recruit mutation path, the midway
booth-render branch, `mirrors_completed`, the keepsake list, the
request_save signal. No new scene, no save-format change beyond the
`<royal>_barred` / `royals_reconciled` flags.

Deferred still: gold sinks beyond quotes/OFFER/puzzles.
