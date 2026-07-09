# FEY FAIRE — design doc

Slowstick #3 · **Oneironautics · 1990 · Amélie Rocha's first published game**.

Found in-fiction as a cartridge in Pirate Summer's slowstick console
(mess hall, 1994).  Andy Link, the player of the outer game, boots
Fey Faire from that console.  The player of Fey Faire is a teenager
named **YOUR NAME HERE** — the game asks on boot and remembers.

Genre: **dark urban fantasy JRPG** in the shape of Shin Megami
Tensei · turn-based combat, negotiation-first party building, Court
alignments that end the run differently.

Tone: **Shakespeare-dark, teen-forward**.  Not YA-safe.  The feys
speak in something that reads as verse when you scan it too fast.
The consequences are real — feys take memories, time, names, the
color from a specific object you own.  Nothing pauses to reassure
the player.  But it is also FUNNY, in the way A Midsummer Night's
Dream is funny.  Puck is here.  Puck is unhelpful.

Cross-Oneironautics: Fey Faire is Rocha's processing of the summer
of 1976 at Camp Sweetgum, which she was ten years old for.  Her
name appears in Pirate Summer's dialogue web (`amelie_rocha` is
one of the 14 campers · she is Rocha's daughter, playing the game
of her mother's youth 14 years later).  The music-box motif in
Fey Faire's title card and the Portuguese folk tune Wilson sings
share a bar of melody — one of the six chain facts in Pirate
Summer.  **Fey Faire's endings can seed lore tokens back into the
main-menu scrapbook**, unlocking Pirate Summer scrapbook entries.

---

## Premise

**The Fey Faire** is an urban carnival that appears in the player's
hometown for exactly six nights every seventeen years.  This time
it's parked on the empty lot behind the old strip mall on Route 6.
The player is a teenager (14-17) with a specific problem the game
learns from the boot questionnaire: a missing sibling, a dead
parent, a friend who moved away and won't answer letters, a
girlfriend who stopped speaking to them, a father who hits.  Only
the player can see the Faire.  Everyone else's eyes slide off it.

You walk in.  The girl at the ring-toss booth (**Ondine**, one of
the daughters of the Sea) has an offer that isn't quite a
question.  She offers you six nights.  Each night ends when you
either **leave the Faire** or **cross the Threshold** into the
Fairy Realm proper (a first-person dungeon crawl).

At the end of six nights the Faire packs up and leaves for another
seventeen years.  What you take home with you depends on the
Court that favored you.  What you give up · is up to you.

---

## Setting geography

### The Faire midway (top-down 2D, ~40×24 tiles per zone)

- **THE GATE** · painted plywood arches, mauve and cream stripes.
  A ticket-taker who is or is not the same person every night.
- **THE MIDWAY** · booths stretching down a gravel path lit by
  Edison bulbs strung between poles.  Six named booths:
  - the ring toss (Ondine)
  - the balloon-and-dart (a booth with too many prizes)
  - the coin-in-a-glass (a puck in an apron)
  - the fishbowl (a selkie who is running a fishbowl)
  - the milk bottles (a redcap being polite about it)
  - the wheel of fortune (the Erlking is spinning it, if that is his name here)
- **THE HALL OF MIRRORS** · a threshold.  Enter and you're in
  first-person.  Every mirror is a different door into Fairyland.
- **THE BIG TOP** · a tent striped in cream and mauve.  Every
  night at 9:47 PM a play is performed.  Six plays across six
  nights.  Titania stars in one.  Ariel in another.  The player,
  if they consent to it, in the sixth.
- **THE CAROUSEL** · music-box tune Rocha's mother used to sing.
  Sit on a horse and go nowhere for a while.  Optional negotiation
  target · the carousel operator is a fey.
- **THE FUNHOUSE** · not a fun house.
- **THE COTTON-CANDY WAGON** · the wagoneer is a Green Man in a
  paper hat.  Cotton candy is not made of sugar.

### Fairyland (first-person grid, Wizardry-style)

- Reached through the Hall of Mirrors.  Each mirror is a different
  entry point.  Six mirrors, six sub-realms.
- Sub-realms have different palettes and different courts patrolling.
- Combat is initiated by an encounter mid-corridor, screen swap to
  a stylized combat view.

---

## Combat system

**Turn-based, party of 4** (protagonist + up to 3 negotiated feys).
Not SMT's Press-Turn (too system-heavy for slowstick).  A simpler
**speed-order round-robin** where actions resolve highest-to-lowest
`speed`, with `crit` chance boosted when the target has a WEAKNESS
to your damage-type.

### Damage types
- **Iron** — physical strike, effective against most feys
- **Bone** — physical strike, effective against Unseelie
- **Flame** — magical, effective against Wildfey (they hate order)
- **Song** — magical, effective against Seelie (they love flattery)
- **Salt** — magical, effective against everything from the sea
- **Word** — magical, quotes from Shakespeare are actual spells

### Stats
- `HP` current health
- `SP` spell points (spent on magic + negotiation offers)
- `AP` attention (a fey with 0 attention flees; below 3 they
  negotiate)
- `speed`, `strike`, `resist`, `charm`, `wit`

### Skills
- Every fey knows 2–4 skills · attacks, buffs, debuffs,
  status effects.
- Protagonist starts with `IRON STRIKE` (iron), `QUOTE` (Word · costs 2 SP,
  higher effect if you actually pick the right quote), `PLEAD` (opens negotiation).
- Learns more skills by leveling up + reading books at bookstalls.

### Statuses
- `charmed` — target attacks its own side for 2 rounds
- `dizzy` — halves speed
- `mused` — the target composes a poem instead of acting for a round
- `bewitched` — target's damage-type is randomly reassigned each turn
- `named` — target loses 20% HP each round while its true name is spoken

### Combat scene visuals
- Player party on the right, feys on the left (Dragon Quest orientation).
- HeroImage-scale portraits (~64x48) with 2-frame idle animations.
- Background is a HeroImage of the current sub-realm.
- No damage numbers · just descriptive text ("the Kelpie shudders",
  "Puck laughs off the strike", "Titania's crown cracks").

---

## Negotiation system (the SMT hook)

Any fey in combat can be negotiated with when its `AP` is below 3
(you've gotten its attention).  Enter negotiation by using `PLEAD`.
A negotiation is a **question-response tree** with 4 branches:

- **OFFER** — give the fey an item from your inventory.
- **PROMISE** — promise the fey a service (later reclaimed).
- **THREATEN** — invoke a specific true name you've learned.
- **RECITE** — quote Shakespeare that fits the fey's temperament.

Each fey has:
- A **prize** (what they can be bribed with)
- A **name** (which unlocks THREATEN)
- A **favorite play** (which unlocks RECITE)
- A **request** (what they want you to PROMISE)

Success recruits the fey to your party (up to 3 slots).  Failure
either dismisses them (they flee) or angers them (combat resumes,
now with a `charmed`-style debuff on you).

### Promises stack
Every unfulfilled promise gives -1 to future negotiation checks.
Promises are collected at the **CLOSING NIGHT** · the sixth night
· all at once.  You will not have enough of anything.  Choose.

---

## The fey roster (draft · 22 feys)

Each named, with a Court, a preferred damage type, a resistance,
and one signature ability.  Rank by tier · Tier 1 = midway
strolling, Tier 3 = boss-scale.

### Seelie Court (kind but capricious)
- **Peaseblossom** · Tier 1 · flower-fey · heals · loves compliments
- **Mustardseed** · Tier 1 · spice-fey · fire burst · loves gifts of pepper
- **Cobweb** · Tier 1 · silk-fey · binds targets · loves bookmarks
- **Moth** · Tier 1 · nightlight-fey · charm · loves candles
- **Ondine** · Tier 2 · water-sprite · salt magic · trades in memories
- **Ariel** · Tier 3 · air-sprite (Tempest) · storm caster · sings your name back at you
- **Titania** · Tier 3 boss · glamour magic · demands you accept a rose

### Unseelie Court (cruel but honorable)
- **Redcap** · Tier 2 · murderous highland fey · iron-strike · his cap is red for a reason
- **Sluagh** · Tier 3 · undead host · bone-strike · flies with the west wind
- **Erlking** · Tier 3 boss · hunter fey (Goethe) · pursues you
- **Nuckelavee** · Tier 2 · skinless sea-horse · plague-type
- **Baobhan Sìth** · Tier 2 · Scottish vampire-fey · charm
- **Oberon** · Tier 3 boss · court fey · has his own claim on Titania

### Wildfey (unbound, mercurial)
- **Puck / Robin Goodfellow** · Tier 2 · trickster · high speed, low HP
  · his signature ability is FOOL YOU (reassigns damage types randomly)
- **Kelpie** · Tier 2 · water-horse · drowns · trades in bones
- **Selkie** · Tier 2 · seal-form · shape-shifter · trades in seven-year promises
- **Boggart** · Tier 1 · house spirit gone wrong · petty debuffs
- **Green Man** · Tier 3 boss · vegetative · seasonal weakness cycle
- **Pooka** · Tier 2 · shape-shifter · adaptive resistance
- **Leanan Sidhe** · Tier 3 · fey muse who kills · trades brilliance for years
- **Queen Mab** · Tier 3 boss · dream-fey · fights you in dreams only
- **Caliban** · Tier 3 boss · dark physical brute (Tempest) · claims the island

Additional to draft: 6 Tier-1 filler feys (nixies, will-o'-wisps,
mushroom-folk, an actual named cricket) so encounter tables have
variety in the first two nights.

---

## Shakespeare integration

The **RECITE** action lets the protagonist speak a Shakespeare line
in combat/negotiation.  The player picks from a menu of memorized
quotes.  Correct-fey pairings do 2× damage or open negotiation
immediately.  Wrong pairings do 1× or backfire (the fey misquotes
back at you).

### Starting quote memory
Player begins with 3 quotes:
- "Lord, what fools these mortals be!" (Puck-friendly)
- "We are such stuff as dreams are made on" (Ariel-friendly)
- "I know a bank where the wild thyme blows" (Titania-friendly)

### Learning more quotes
- Reading playbills in the Big Top after each nightly performance
- Buying used paperbacks at THE BOOKSTALL (2 gold each · gold is
  earned by winning midway games).
- A "quote memory" cap tied to protagonist level (start 3, +1 per level).

### Boss scenes ARE Shakespeare scenes
Each Tier-3 boss encounter is a specific scene played out.
- **Titania** boss is Midsummer Act II Sc I · Oberon-Titania quarrel.
  You're inserting yourself as a third party.
- **Ariel** is Tempest V, freeing him from Prospero's service.
  You are or aren't Prospero here.
- **Oberon** is a duel over Titania · you're Titania's champion.
- **Caliban** is Tempest III · he offers to serve you as a new god.
- **Green Man** is a folk-tradition Mummer's play, not
  Shakespeare · deliberate genre-break to remind the player Fey
  Faire's fiction is bigger than one author.
- **Queen Mab** is a nightmare inside the protagonist's own
  bedroom · Mercutio's speech from R&J is the trigger to enter it.

---

## Alignment (three courts, three endings + variants)

Every negotiation, promise, and quote choice slides the protagonist
toward a court.  Track internally as three counters: `seelie`,
`unseelie`, `wildfey`.  Highest at closing night decides the
ending.

- **SEELIE ENDING** · a rose · you keep your name but you no
  longer remember the season your loss happened in.  The Faire's
  music will follow you.
- **UNSEELIE ENDING** · a red cap · you keep the seasons but
  your name is different now, and you have to relearn to answer
  to a new one you did not choose.
- **WILDFEY ENDING** · a stag's antler · you keep everything but
  you don't leave.  You are at the Faire when it packs up and
  travels.  Seventeen years pass in one night.  You come back
  older and the town has changed.
- **THREE HIDDEN ENDINGS** unlocked by specific promise-fulfilling
  behavior:
  - `bring_back_the_lost` — the protagonist's initial specific
    problem (sibling, parent, friend) is undone.  The Faire takes
    a proportional cost — usually the protagonist's best fey.
  - `refuse_the_faire` — the protagonist walks away on night one
    or two after understanding what the Faire is.  Short ending.
    Melancholic.  Nothing given, nothing taken.
  - `become_the_faire` — the protagonist chooses to *replace* the
    ticket-taker.  Now they are the fey at the gate.  Seventeen
    years later a new teen walks in.

---

## Structure — six nights

Each night is roughly:
- **Midway phase** · top-down exploration.  Booth-play,
  conversations, item-buying, small quests.
- **Threshold phase** · optionally cross into Fairyland (a specific
  mirror).  First-person dungeon crawl · random encounters · a
  boss at the end that seeds a Tier-3 fey recruit if beaten
  fairly, or destroyed if beaten meanly.
- **Return phase** · at midnight the Faire's lights dim.  You
  choose: rest at the Faire (safer, but a promise-obligation
  fires) or leave and return next night (safer for you, but the
  Faire evolves without you).

### Night 1 · WELCOME
Introduction.  Player meets Ondine.  Free samples of Faire life.
Cannot yet cross the threshold.  One boss NPC seen (Puck, at a
distance, misbehaving).

### Night 2 · THE FIRST MIRROR
Player is granted the Iron Key by a Redcap they beat at milk
bottles.  Iron Key opens Mirror 1 · the Rose Garden.  Titania
boss.  Optional recruit.

### Night 3 · THE SECOND MIRROR
Playbill for the night's show reveals The Tempest.  Mirror 2 ·
The Storm-Wracked Coast.  Ariel boss.

### Night 4 · THE INNER FAIRE
The midway has changed overnight.  A new booth (THE BAZAAR OF
NAMES) sells the true names of feys.  Threshold Mirror 3 ·
The Court Beneath.  Oberon boss.

### Night 5 · THE DEEP MIRROR
Threshold Mirror 4 · The Green.  Green Man boss.  Mirror 5 · The
Undertide.  Caliban boss.  Two dungeons available.  Difficulty
spike.  A quiet scene at 3am · the ticket-taker asks the
protagonist a question the player has to answer honestly.

### Night 6 · CLOSING NIGHT
The Big Top show is your name.  Queen Mab tries to keep you.
All unfulfilled promises come due.  Court alignment locks.  The
ending you get depends on your court alignment + which promises
you kept.

---

## Systems checklist for build

- [ ] Boot / naming screen (SlowstockShelf-style)
- [ ] Save state (three slots, like Pirate Summer)
- [ ] Faire midway zone renderer (adapt CampOverworld's tile system)
- [ ] Fairyland first-person renderer (new)
- [ ] Combat scene renderer (new · portrait + BG + action menu)
- [ ] Party manager (up to 3 recruited feys)
- [ ] Negotiation dialogue system (adapt Pirate Summer's dialogue box)
- [ ] Fey catalog (JSON, ~22 entries with skills/stats/prizes)
- [ ] Fey portraits (~22 × 32x48 pixelart)
- [ ] Fey combat sprites (~22 × 48x48 pixelart)
- [ ] Skill catalog (~40 skills, JSON)
- [ ] Shakespeare quote catalog (~30-50 quotes, tagged by court affinity)
- [ ] Court alignment tracker
- [ ] 6 sub-realm dungeons (first-person grids)
- [ ] 7 endings + variants
- [ ] Scrapbook (like Pirate Summer, with cross-Oneironautics tokens)
- [ ] BGM · Faire midway · Fairyland dungeon · combat · boss · Big Top show · ending
- [ ] SFX · combat hits · negotiation success · quote crit · booth
      games · mirror crossings

Rough scope: **3x Pirate Summer's build time**.  Faire midway
alone is Pirate Summer-sized; combat + first-person Fairyland
dungeons are on top.

---

## Cross-Oneironautics tie-ins (Rocha's autobiography)

- Every ending grants a **lore token** that appears in the
  SlowstockShelf scrapbook.  Tokens like `faire_1990_titania_recruited`,
  `faire_ended_wildfey`, `faire_offered_the_stag_antler`.
- Certain fact chains in Pirate Summer's dialogue web unlock only
  when specific Fey Faire tokens are present.  Example:
  Rocha's grandmother's Coimbra postcard (Pirate Summer) is
  narratively connected to Ondine's Portuguese lullaby (Fey Faire)
  — playing both games reveals it.
- The **1976 tie** · Fey Faire's protagonist's specific problem
  can be "a boy at summer camp who never came back."  If the
  player picks that option, an epilogue mentions his name:
  ANDREW.  This is Rocha processing the Camp Sweetgum incident.

---

## Palette + aesthetics

Match the title-card palette established in
`sprites/scenes/cart_fey_faire.json`:
- Cream `#f4e0d0`
- Old rose `#e0b8c0`
- Mauve `#c88ea4` and darker `#a86088`
- Deep purple `#743c60`, `#4a2848`
- Black-plum `#28182c`
- Warm accent gold `#f8c848`, `#c89040`, `#8a5c30`, `#6a4028`
- Deep umber `#2a1408`

Every zone stays in that palette.  Fairyland sub-realms may
INTRODUCE their own palette additions (Green Court has forest
greens; Undertide has teals) but the base cream+rose+mauve
should thread through every screen so the player always knows
they're in Rocha's game.

---

## What Fey Faire is NOT

- Not gorey.  Dread without splatter.
- Not preachy.  The feys aren't allegories.
- Not romantic.  The protagonist has a specific problem, but it
  is not "meeting the fairy prince."
- Not gambling-adjacent.  Booth games use skill checks, not RNG.
- Not a save-the-world plot.  The Faire will move on to the next
  town regardless of what the protagonist does.  This is a small
  personal story that happens to be set inside a fairy carnival.

---

## Open design questions

1. **Combat resolution**: descriptive text only vs. numeric damage?
   Text-only fits the slowstick tone but may confuse depth-first
   players.  RECOMMEND: text-only, with a HUD showing HP bars only.
2. **Death**: does the protagonist die?  RECOMMEND: no · reduced to
   0 HP means the fey take a specific memory from you and drop
   you back at the Gate.  Six memories tracked; losing all six
   ends the run early (a bad ending).
3. **New Game+**: after finishing once, does the player keep
   quotes, gold, or fey?  RECOMMEND: keep quotes only.  Fey and
   gold reset.  The Faire is different for a returning visitor.
4. **Combat music**: one loop or per-court variants?
   RECOMMEND: one loop, but with a bar swap per-court so it feels
   different without needing three separate tracks.

---

## Recent lessons — TEMPLATE

To be captured after each build session, per project
`_playbook` cadence.
