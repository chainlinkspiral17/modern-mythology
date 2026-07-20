# THE MAJOR ARCANA · CAMPAIGN · DESIGN
### the twenty-two, in order, as one journey — Fool to World
### STATUS: BUILT · playable_v1 (2026-07-20) · ladder + bookend + thread-spend edges all wired

Chosen new-design direction #2 (after the Almanac hub). Turns the 22
standalone TAROT GAUNTLET scenarios into a single ordered run with a
carried thread and an escalating antagonist. Pours its progress into
the Almanac's THE GAUNTLET chapter.

## THE PROBLEM IT SOLVES

The gauntlet has 22 gorgeous, self-contained arcana — but they're a
shelf of one-offs picked à la carte from the spread/gallery. Nothing
connects a win at The Fool to a loss at The Tower; nothing carries;
nothing builds. A tarot reading is a SEQUENCE (the Fool's Journey);
the game has the cards but not the journey.

## THE LOOP · the Fool's Journey

A new framing mode, **THE MAJOR ARCANA**, reached from the Main Menu
(or the spread screen). It presents the 22 in canonical order and
walks you through them:

1. **The ladder.** The 22 arcana as an ordered track, Fool (0) →
   World (XXI), each pinned to its canonical location (fool =
   D'Ambrosio's, magician = cathedral, … world = Frog Knows Best —
   the same one-location-per-arcana map the Almanac already uses).
   The next unplayed arcana is lit; cleared ones bear their result;
   later ones are shown but locked until you reach them.
2. **Play the card.** Selecting the active arcana launches the
   existing `TarotGauntletGame` with that arcana's SIGNATURE scenario
   (one authored entry-scenario per arcana; the other setups stay in
   free play). No new gauntlet code — the campaign is a launcher +
   bookend.
3. **The bookend.** On return, a short interstitial: the card turns,
   the Thread updates, and the antagonist gets his beat for this act.
   Then the ladder advances to the next arcana.

## THE CARRIED THREAD · what persists

**THE QUERENT'S THREAD** — one small pool of *insight* that survives
between arcana (stored in `GauntletState.state.campaign`). You earn
it by winning (+1) and by winning cleanly / to a Pomegranate-style
condition (+1 more). Before a later gauntlet you may SPEND thread for
one legal, additive edge — e.g. "read the room" (reveal one visitor's
want at start), "an extra breath" (+1 starting patience/turn), or
"the deck remembers" (start with one arcana-appropriate item). All of
these ride the gauntlet's existing `starting_state`; the campaign just
seeds it. Never a wall — thread only ever helps.

## THE ESCALATING ANTAGONIST · Dean rises

Dickens Dean (and the empty-stool demon he serves) already recur
across gauntlets. The campaign gives that a shape: **three acts**
(0-VII, VIII-XIV, XV-XXI) with rising *Dean pressure*. Each act's
bookend advances his presence — from a name in someone else's ledger,
to a suit at your table, to the thing across the felt in the final
arcana. Mechanically light: a per-act campaign modifier the later
gauntlets read (a themed pressure the setups already support via
their difficulty axis), plus authored interstitial prose. The World
(XXI) is the reckoning.

## PLUGS INTO THE ALMANAC

Every cleared arcana writes `campaign_arcana_<id>_cleared`; act
completion writes `campaign_act_<n>_closed`; the full run writes
`campaign_major_arcana_complete` (which, with the existing
`all_arcana` rule, lights THREAD · The Whole Reading). THE GAUNTLET
chapter of the Almanac becomes the campaign's progress spine — the
per-arcana entries there flip from `{arcana_won}` to the richer
campaign tokens.

## BUILD ORDER

1. `campaign_arcana.json` — the 22 in order: `{arcana, location,
   scenario, act, thread_award, dean_beat}`. Signature scenario per
   arcana chosen from the existing setups.
2. `GauntletState` campaign block + helpers: `campaign_progress()`,
   `campaign_advance(arcana, won, clean)`, `thread_balance()`,
   `spend_thread(edge)`. Persisted in the existing gauntlet save.
3. `MajorArcanaCampaign.gd/.tscn` — the ladder screen + the bookend
   interstitial. Launches `TarotGauntletGame` with the signature
   scenario and a `campaign_seed` (thread edge → starting_state).
4. `TarotGauntletGame` reads an optional `campaign_seed` at boot to
   apply the chosen thread edge + Dean pressure (additive only), and
   reports the result back so the campaign can advance.
5. Main Menu entry + Almanac THE GAUNTLET entries keyed to campaign
   tokens.

## HONEST CONSTRAINTS

- Rides the existing gauntlet — no second combat/board engine. The
  campaign is a launcher, a bookend, and a thin carried state.
- Free play stays: the à-la-carte spread/gallery keeps working; the
  campaign is an additional way in, not a replacement.
- Thread + Dean pressure are ADDITIVE seeds on `starting_state`; a
  campaign gauntlet is still a normal, winnable gauntlet.
- No new art pipeline (procedural + existing card/bust art).
