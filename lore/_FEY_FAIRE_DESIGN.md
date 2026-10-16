# FEY FAIRE — master design doc

Slowstick #3 · **Oneironautics · 1990 · Amélie Rocha's first published game**.

Found in-fiction as a cartridge in Pirate Summer's slowstick console
(mess hall, 1994).  Andy Link, the player of the outer game, boots
Fey Faire from that console.  The player of Fey Faire is a teenager
named **YOUR NAME HERE** — the game asks on boot and remembers.

Sister docs:
- `_FEY_FAIRE_MECHANICS.md` · combat + death + checkpoints + progression
- `_FEY_FAIRE_FACTIONS.md` · Court hierarchies + player-standing tracking
- `_FEY_FAIRE_ROUTES.md` · route branching + mirror puzzles + endings

## Elevator pitch

**A first-person dark-urban-fantasy JRPG where combat is what
happens when a conversation fails.**  Shin Megami Tensei's talk-to-
demons negotiation, Disco Elysium's dialogue-density, Dark Souls's
punishing set-piece encounters and death-loop-until-checkpoint
progression.  Shakespeare-heavy, but not Shakespeare-limited.

No random encounters.  No leveling curve.  No grinding.  Every fight
is authored, every fight is hard, and every fight was avoidable if
you'd spoken to the right fey with the right item under the right
Court's protection.  Death drops you back at the Gate with your
recruited feys still remembering you, until you've earned a
checkpoint deeper in.

The player is a teenager who accepted six nights from Ondine at
the ring-toss booth.  Between now and closing night, they can go
anywhere the Faire's paths lead — through any of six mirrors into
Fairyland proper, into any of the Courts' politics, and toward
any of the possible endings.

Full first-person perspective throughout.  Both the Faire midway
and the Fairyland sub-realms use the same grid-crawl movement,
because the Faire IS a sub-realm — the player just doesn't know it
until Ondine tells them at the wheel-of-fortune scene on night 3.

## Aesthetic direction

**Persona 1 PSP · SMT: Devil Survivor · Etrian Odyssey Untold**
· hand-painted perspective backdrops per corridor cell, oversized
portraits (96×144) when a fey speaks, palette locked to Rocha's
cream-and-mauve-and-gold from the cart title card, and a subtle
CRT + chromatic-aberration filter on the Faire's Edison lights.

Deliberately NOT going for pure retro (which would look thin) or
modern indie-3D (which would break the slowstick fiction).  What
we're building is: **a hypothetical 1990 slowstick that ran on
hardware that didn't exist**.

Palette:
- Cream `#f4e0d0`, old rose `#e0b8c0`, mauve `#c88ea4`/`#a86088`
- Deep purple `#743c60`/`#4a2848`, black-plum `#28182c`
- Warm accent gold `#f8c848`/`#c89040`/`#8a5c30`/`#6a4028`
- Deep umber `#2a1408`
- Fairyland sub-realms MAY introduce their own tint but the base
  palette threads through every screen so the player always knows
  they're in Rocha's game.

## The Faire midway (single connected map, ~40 first-person cells)

Not divided into zones like Pirate Summer.  One large explorable
first-person grid, unfolding as you visit corners of it:

- **THE GATE** · Cricket (ticket-taker) · entry point.
- **THE MIDWAY** · a long central boulevard with named booths on
  either side.  Six named booth-vendors (see feys.json).
- **THE BIG TOP** · nightly Shakespeare shows, backstage accessible
  from night 4 (Oberon holds court there).
- **THE HALL OF MIRRORS** · six mirror-doors into Fairyland.
- **THE FUNHOUSE, THE CAROUSEL, THE COTTON-CANDY WAGON,
  THE BOOKSTALL, THE BAKERY, THE FORTUNE-TELLER'S TENT** · off-path
  attractions with their own fey and their own reasons.
- **THE PARKING LOT** · exit.  You can leave any time.  Coming
  back is not guaranteed to work.

## The six mirrors (Fairyland sub-realms)

Each mirror opens onto a different sub-realm.  You can visit them
in any order once you have the corresponding **key** (a specific
item earned from a specific fey).  See `_FEY_FAIRE_ROUTES.md` for
the full map.

1. **The Rose Garden** · Titania's court (Seelie boss)
2. **The Storm-Wracked Coast** · Ariel's realm (Tempest)
3. **The Court Beneath** · Oberon's court (Unseelie boss)
4. **The Green** · Green Man's realm (Wildfey elder)
5. **The Undertide** · Caliban's island (Tempest)
6. **The Dream** · Queen Mab's bedroom-that-is-yours (Wildfey · dream-space)

## Structure — six nights, no forced pacing

Nights are narrative time, not gates.  A night advances when the
player REST at any booth (recruited fey required).  Nothing stops
you from spending three real-world hours in one in-game night if
you're exploring; nothing stops you from advancing to night 6 in
your first hour if you keep resting.  On night 6 the Faire packs
up and the ending fires.

Deaths do NOT advance nights.  Deaths are lateral · the player
loses SP + gold + one specific item + wakes up at a checkpoint.

Skilled players can finish in 3-4 nights.  A completionist run
takes all 6 and requires backtracking.  Neither is "the right way."

## Cross-Oneironautics tie-ins (Rocha's autobiography)

- Every ending grants **lore tokens** that appear in the
  SlowstockShelf scrapbook.
- Certain fact chains in Pirate Summer's dialogue web unlock only
  when specific Fey Faire tokens are present.
- The **1976 tie** · Fey Faire's boot-questionnaire option "a
  boy at summer camp who never came back" names ANDREW in the
  epilogue.  This is Rocha processing the Camp Sweetgum incident.
- The music-box tune Wilson hums in Pirate Summer is playable on
  the Carousel in Fey Faire.  Playing it there is a specific
  achievement that unlocks a Pirate Summer scrapbook chain fact.

## What Fey Faire is NOT

- Not gorey.  Dread without splatter.
- Not preachy.  The feys aren't allegories.
- Not romantic.
- Not gambling-adjacent.  Booth games use skill checks, not RNG.
- Not a save-the-world plot.  The Faire will move on to the next
  town regardless of what the protagonist does.
- Not level-curve JRPG.  See `_FEY_FAIRE_MECHANICS.md`.
- Not linear.  See `_FEY_FAIRE_ROUTES.md`.

## Systems checklist

- [ ] Boot / naming screen (SlowstockShelf-style)
- [ ] Three-slot save (like Pirate Summer)
- [ ] First-person grid renderer (new · corridor cell backdrops)
- [ ] Corridor backdrop authoring (HeroImage-scale 320×180 per cell,
      ~120 cells across the Faire + 6 sub-realms)
- [ ] Portrait renderer (96×144 fey portraits · 29 to author)
- [ ] Dialogue system (adapt Pirate Summer's dialogue web + tag
      by fey + branching on relationship state)
- [ ] Negotiation UI (OFFER / PROMISE / THREATEN / RECITE branches)
- [ ] Combat scene (turn-based, 4-slot party, HeroImage BG,
      portrait-scale combatants)
- [ ] Party manager (up to 3 recruited feys)
- [ ] Fey catalog (`feys.json` · SHIPPED · 29 entries)
- [ ] Skill catalog (`skills.json` · TODO · ~40 skills)
- [ ] Shakespeare quote catalog (`quotes.json` · TODO · ~30-50)
- [ ] Court hierarchy + standing tracker (`factions.json` · TODO)
- [ ] Mirror puzzle library (~6 mirror-gate puzzles + booth
      puzzles for every named vendor)
- [ ] Checkpoint system (per-recruit spawn nodes)
- [ ] Scrapbook (cross-Oneironautics tokens)
- [ ] BGM · Faire midway · six sub-realms · combat · boss ·
      Big Top show · endings
- [ ] SFX · steps · booth interactions · combat hits · negotiation
      success · quote crit · mirror crossings · deaths

**Rough scope**: **3× Pirate Summer's build time**, but the
authoring density is different — Pirate Summer had a lot of
plumbing per zone; Fey Faire has fewer zones but each is denser
with content.  Corridor backdrops + 29 fey portraits + skill
catalog + quote catalog + puzzle library is the bulk.
