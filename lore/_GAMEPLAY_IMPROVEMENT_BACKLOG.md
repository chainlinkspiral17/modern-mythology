# Gameplay Improvement Backlog · Modern Mythology

Companion to `_PACKAGE_IMPROVEMENT_BACKLOG.md` (which covers scenes,
art, and presentation). THIS list is about the games AS GAMES:
mechanics, content depth, replayability, feedback loops, onboarding.
Compiled 2026-07-19 from a data audit: 22 arcana × 3–4 setups each,
CP's 8 demons / 6 humans / 21 problem templates, per-stick endings
and scrapbook coverage, the shelf unlock graph.

- **P1** — a player feels the gap in one session
- **P2** — depth/replayability; felt across a full playthrough
- **P3** — meta, polish, systems health

─────────────────────────────────────────────────────────────────────

## 1 · TAROT GAUNTLET

**P1 · ~~Achievements~~ DONE 2026-07-19** — registry 28 → 59: deck-clear (rewarding reversed unlock) + named-loss per Wave-2 arcana, septenary capstones, THE FULL DECK. Original note: The evaluator runs at
every win/loss, but only `fool/achievements.json` exists. Each arcana
wants 3–5 entries in the Fool's pattern — at least one per named loss
condition ("lose THIS specific way" achievements teach the systems
better than any tutorial) and one style-win per setup.

**P1 · ~~Reversed-mode content audit~~ CLEAN 2026-07-19** — every setup carries an authored epigraph_reversed. Original note: `_reversed_mode` mutates
difficulty (tighter turns, harder loss thresholds) and setups carry
`epigraph_upright` — AUDIT: does every setup also carry an authored
`epigraph_reversed` + reversed opening lines, or does reversed play
show upright text with harder numbers? A mode that changes numbers
but not words feels like a cheat toggle, not a reading.

**P2 · ~~Fourth setups~~ ALL 20 DONE 2026-07-19** — all fourteen Wave-2 arcana now have four scenarios (68 → 82 total). Wave-3D closed the six Wave-1 arcana with win/loss keys inherited verbatim from their bespoke schemas. Every arcana now has four scenarios (88 total). Original note: Lovers and
Chariot have 4 setups; everyone else has 3. The bookend pattern
(easy dawn intro → hard night finale) has room for one more mid-tier
scenario per arcana — 20 setups of content using only existing
machinery (scenario_visitors inline, time-of-day as difficulty).

**P2 · The Spread — cross-arcana runs.** Play three drawn arcana in
sequence with a small carryover (leftover composure/doubt, one held
card). The gauntlet is 22 disconnected scenarios today; a three-card
spread gives it a campaign shape and a reason to master weak arcana.
New host screen + carryover rules; scenarios unchanged.

**P2 · ~~Named-loss preview~~ DONE 2026-07-19** — the title card lists up to four finale titles ('ways this goes wrong'). Original note: The new arcana title
card has room for one line: the setup's named loss conditions ("Ways
this goes wrong: THE ROOM WALKS OUT · SHIFT ENDS BEHIND"). Losses as
pedagogy, surfaced before play instead of discovered after.

**P3 · Daily draw.** A one-tap "draw a card" entry that picks an
arcana+setup (optionally date-seeded so everyone gets the same daily).
Removes choice paralysis from a 70+-scenario menu.

**P3 · Post-run reading.** The end screen states win/loss; add three
lines of "the reading" — which turns swung it, the visitor who
mattered, the card never played. Data the engine already tracks,
rendered as tarot-flavored feedback.

## 2 · COMMUNITY PLANNED

**P1 · ~~Problem-template depth~~ PARTIAL 2026-07-19** — 21 → 29 with escalation chains into established templates; ~6 more to reach the 35 target. Original note: 21 templates across a 24-week
summer means repeats by mid-game. Target ~35: more W12+ escalations
so late-summer problems feel categorically worse, not just bigger
numbers. Template schema already supports it.

**P1 · ~~Demon evolution visibility~~ AUDITED CLEAN 2026-07-19** — evolution ticks per resolution, earned traits render in the dossier (checkmarks vs dimmed). Original note: `evolution_traits_catalog`
exists in agents.json — AUDIT: is evolution live in play, and can
the player SEE a demon's acquired traits (dossier trait chips)? A
hidden progression system might as well not exist.

**P2 · Between-spike events.** The W6/W12/W18 pressure curve is the
spine; add rare one-shot events between spikes (a resident
petition, a demon making an unprompted offer, a BBS thread going
hot) so mid-summer weeks aren't pure routing.

**P2 · Roster growth.** 6 humans / 8 demons staffs the campaign but
gives no roster decisions. 2–3 recruitable late-summer agents with
real tradeoffs (a brilliant human who refuses demon partners; a
demon whose evolution is fast but public) would make W12+ staffing
strategic.

**P2 · Post-campaign endless mode.** After the summer resolves,
reopen the board seasonless with scaling problem pressure — the
three-slot save keeps campaign saves untouched.

**P3 · Run ledger.** Three save slots exist; add a small compare
screen (weeks survived, tower brightness curve, problems resolved
per region) so replays have a target.

**Protected:** BBS thread-gating and the diegetic terminal stay
as designed.

## 3 · SLOWSTICKS — catalog-wide systems

**P1 · ~~Scrapbooks~~ DONE 2026-07-19** — ten scrapbook.json files, 45 entries keyed to tokens the hosts actually emit. Original note: The shelf's scrapbook
button convention (`scrapbook.json` per stick) is live, but only
Estuary 3 Manager Mode and Pirate Summer have one. estuary_1/2,
northwind, sweetgum, riffmaster, hane_no_niwa, glass, wyrd, sss, ksm
all finish into nothing. Even 6–10 tokens each (endings seen, the
secret found, the dog's name) makes finishing collect into
something. Cheapest full-catalog win on this list.

**P1 · Completion must visibly change the cabin.** Manifests carry
`lore_tokens_awarded_on_completion` — AUDIT which tokens are ever
CONSUMED (FF/EM's are, per the cross-Oneironautics pass). Rule:
every finished stick should change at least one observable thing —
a shelf remark, a cabin radio line, Pirate Summer chatter. Sticks
whose tokens go nowhere need one consumer each.

**P2 · ~~Unlock legibility~~ DONE 2026-07-19** — the locked line names the gate ('finish ESTUARY 3', 'finish 3 sticks (2 more)', 'continues from Vol 7's story'). Original note: The shelf says "LOCKED · finish another
stick to unlock" — say WHICH ("finish NORTHWIND HARBOR"), from the
unlock_graph. Mystery gating without direction is just friction.

**P3 · Shelf stats page.** Finished count renders; add per-stick
best-result lines (E1 best report card, PS ending reached, FF
endings seen ×/7) pulled from the saves the sticks already write.

## 4 · SLOWSTICKS — per-stick gameplay

**P2 · ~~estuary_1~~ DONE 2026-07-19** (the water word on the gate housing from pre-rolled luck; signed B±/C± grades so near-misses read). Original note: — the one-lever design is sacred; add weekly
FLAVOR variance (a storm week, an algae bloom) that shifts what the
lever means without adding controls. More report-card grades than
the current bands so near-misses read.

**P2 · ~~estuary_2~~ DONE 2026-07-19** (return-after-absence memory: species gone 3+ walks get acknowledged on return, illuminated pages get the quieter line). Original note: — twelve walks exist; add walk-to-walk memory
(something you passed on walk 3 has changed by walk 9). The genre
is noticing; give it more to notice.

**P2 · ~~northwind_harbor~~ DONE 2026-07-19** (Bosun pettable once per morning, persisted; four chapter-7 walk variants; nh_bosun_ritual token + scrapbook secret at six-of-seven). Original note: — seven mornings + the dog: let feeding /
ignoring the dog across mornings shift the final morning. One
variable, tracked, paid off.

**P2 · kwik_stop_manager + sams_summer_shifts — DONE 2026-07-19.**
KSM ending audit CLEAN (full endings system in the host; earlier
zero-count was a wrong-file grep). Modifiers + crossover guest
shipped: KSM rolls a REPAVE WEEK once per summer (weeks 3–7,
persisted in `_state.repave_week`) — traffic ×0.55 but +$95 flat
crew lunches, announced in the plan phase and itemized in the
ledger. SSS rolls a solo week once per summer (`solo_week`, never
weeks 1/6/12) — "RAY'S AT THE COAST" banner, till swings count
double. Crossover guest: Fair Weekend (week 9) gains a CAMP
SWEETGUM STAFF shirt buying a blue slushie + rock postcard, gated
on `OneironauticsTokens.has("pirate_summer_finished")`. Original
note: — shared Manager machinery: one new nightly modifier each
and one crossover guest (a Pirate Summer camper buying slushies
in SSS).

**P2 · ~~fey_faire~~ DONE 2026-07-19** — one status per Court in combat (seelie GLAMOUR dispelled by DEFEND, unseelie IRON-SICK from an affinity RECITE, wildfey OATHBOUND once per fight when any verse invokes the courtesies), status chips on the fey panel, and Court STANDING in words (unmet→beloved) atop the party roster. Bookstall-quote fey lists remain. Original note: — combat scaffold wants one status effect per
Court (glamour/iron-sick/oathbound) and visible Court reputation
(the factions data exists; surface a standing meter in the trailer).
Bookstall quotes should list which fey they've worked on.

**P2 · earthman_chronicles — DONE 2026-07-19.** Thar-Krai-Tam now
runs a scripted arena pattern in EarthmanCombat (`_boss_turn_thar`,
other bosses keep the generic loop): open-hand cuffs at reduced
damage while the blade stays sheathed, a TELEGRAPHED four-arm bind
(DEFEND on the telegraph turn slips it and opens him up ·
counter-hit ×1.5 · otherwise strike+6), the blade drawn after turn
3 as its own beat, and the overseer's bellow staggering the next
player strike −4 every 4th armed turn. Status chips on both HP
labels; Rocha's "he telegraphs the bind" analyze line is now a
tutorial, not flavor. Workings menu: performing over a live
objection now previews the exact cost inline ("regard N → N−1 · a
thing said aloud stays said") before the button is pressed.
Original note: — the tactical scaffold exists; pick ONE chapter
boss (the Mines' Thar-Krai-Tam) and make it a full arena fight as
the pattern-setter before spreading to the rest. Workings menu:
show consequence previews for consent violations.

**P2 · pirate_summer** — ~~NG+: knowing Wilson's secret / the 1976
cache from a prior run unlocks early dialogue options and a
day-one shortcut flag. The dialogue-web supports it; it's mostly
authoring gated lines.~~ DONE — a prior pirate ending
(`sam_and_wilson_have_the_map` or the absolved variant in
OneironauticsTokens) sets `_run_state.ng_plus` on Sunday boot and
grants the `ng_you_remember_this_summer` fact. Payoffs: a deja-vu
paragraph in the Sunday intro modal (points at the north bluff),
the Old Man brace-able solo on day one (NG+ counts as the third
pair of hands, with its own transient), 3 authored reactions
(Wilson / Bea / Nika), 4 fact-gated idle-chatter lines (idle
chatter now honors `conditions.requires_fact` like party chatter),
and 3 fact-gated party-chatter lines (Elias / Tessa / Ford).

**P3 · estuary_3 Manager Mode** — balance pass on buy-out ending
pacing (earliest achievable week vs the six endings' spread).

**P3 · sweetgum / patient_mister_glass / sisters_wyrd /
riffmaster / hane_no_niwa** — each is deliberately small; the
improvement is one extra secret each (a hidden night, a hidden
loop, a hidden room) rather than systems. Respect the minimalism.

## 5 · VN (vols 5–6) as a game

**P2 · Choice consequence surfacing — DONE 2026-07-19.** Audit
found: 3 choices total across both volumes (two of them cosmetic —
both options goto the same node), 22 flag-sets, ZERO flag-reads
(the engine had no conditional node). Shipped: GameEngine
`when_flag` / `when_not_flag` (+ optional `is` for value match) on
ANY node type — unset flag → node skips silently; choice opts can
now carry `flag`/`val` to be remembered without goto surgery.
Callbacks authored (3 per volume): vol5 — elicia_pick (A/B/C
Whispers episode, ch2) pays off in the ch19 café scene with three
espresso-quote variants; aria_named_by_nicola (ch3) pays off in
ch18 (named things come when called); nicola_has_dean_note (ch3)
pays off in ch20 (the order-pad note, kept). vol6 — the graciela
kitchen choice (now said_yes/sat_with_it) pays off in ch7's
safehouse phone call; the shift-change choice (asked_why/waited,
and its stranded node-16 answer line FIXED — both options went to
17, making Jen's key line unreachable) pays off in ch6's open;
sam_dream_charcoal_suit (ch3) pays off at the ch8 courthouse;
maya_has_envelope (ch2) pays off over the ch4 floorboard envelope.
Original note: — ChoiceMenu exists — AUDIT choice density per
volume and whether any choice sets a flag a LATER chapter reads.

**P2 · Chapter select + gallery.** Replay from the volume screen,
plus a gallery of panels/CGs seen (the panel JSONs double as the
gallery's data source). Standard VN meta the package now has the
art to justify.

**P3 · Reading stats.** Words read, panels found, chapters at each
mood — surfaced at volume end, Oneironautics-flavored.

## 6 · Cross-package systems

**P1 · ~~One profile screen~~ DONE 2026-07-19** — PROFILE panel on the main menu: VN slots, per-arcana W–L, achievements count, sticks finished, tokens held. Original note: Volumes read, gauntlet record per
arcana, sticks finished, lore tokens held — all tracked today,
visible nowhere together. One menu screen, read-only, no new state.

**P2 · Package-wide achievements surface.** The gauntlet evaluator +
global achievements.json is the seed; add CP and slowstick entries
and one viewer (the profile screen above hosts it).

**P3 · Accessibility pass.** Text-scale exists; add typewriter-speed
presets (incl. instant), hold-to-skip read text, an accent-palette
colorblind audit (the arcana hues and CP severity colors do double
duty as information), and Deck controller glyphs in every game's
hint text.

**P3 · Deck performance sweep.** SubViewport 3D bgs + post stacks
per locale: profile the worst three scenes on Deck; HEAVY_MOODS
already gates some cost — verify it fires on Deck hardware.

─────────────────────────────────────────────────────────────────────

## Suggested batch order

1. §1 P1 achievements ×21 + reversed-content audit (pure data
   authoring, engine untouched) + §3 P1 scrapbooks ×10.
2. §2 P1 CP template depth + evolution visibility audit.
3. §6 P1 profile screen (surfaces everything the rest builds).
4. §1 P2 fourth setups + named-loss preview; §4 P2 per-stick
   one-improvement-each wave.
5. §5 P2 choice callbacks + chapter select/gallery.
6. The Spread, CP endless, NG+ — the big replayability trio — as
   individual arcs with design notes first.
