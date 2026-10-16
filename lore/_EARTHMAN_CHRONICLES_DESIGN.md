# EARTHMAN CHRONICLES — design doc

Slowstick #4 · **Astro-Cortex · 1985 · L. Rafayette Hubbard**.
Adapted from a manuscript Hubbard wrote in **1948** and never
published · a pulp planetary-romance titled **THE PROPHET OF
THE RED WORLD** that fictionalized his actual 1946 friendship-
and-betrayal with the rocket-fuel chemist and Thelemic
occultist **Jacob "Jack" Whiteside**.

Sister docs:
- `_EARTHMAN_STORY.md` · full chapter-by-chapter story
  treatment · both manuscript AND game versions in parallel ·
  character bibles · ending scripts
- `_EARTHMAN_MANUSCRIPT.md` · the manuscript itself as a
  scrapbook document · Rocha's copy · marginalia · corrections
  page · renders in-game as a 12-page keepsake

Found in-fiction as a cartridge in Pirate Summer's slowstick
console (mess hall, 1994).  Andy Link boots it after Fey Faire.

Genre: **turn-based scifi CRPG in the planetary-romance
tradition** · think John Carter of Mars filtered through 1970s
pulp mysticism · six chapters, 4-slot party, real combat depth,
real occult stakes, real endings.

Tone: **earnest pulp space opera at the surface, real occult
history rising underneath**.  This is Hubbard fictionalizing
Whiteside · but Whiteside was a real man who died in 1952, and
Hubbard's fictionalization was self-serving in specific ways,
and Astro-Cortex's QA team knew it, and Rocha (junior QA at
the time) helped hide COUNTER-COMMENTARY in the ROM.  The
manuscript's history is the game's real story.

Cross-Oneironautics: Earthman Chronicles is Rocha's ONLY
Oneironautics game where she wasn't creative lead · she was
a QA tester who kept her head down and did what she could.
Which included, allegedly, working with a specific senior
engineer at Astro-Cortex to encode CORRECTION TEXT into the
ROM · text that plays at 220 Hz under specific scenes, exactly
the frequency and technique used in Pirate Summer's Northwind
Harbor cartridge to redact a chapter.  Same act of quiet
resistance across both games.

## Elevator pitch

**A pulp John-Carter-style CRPG where you play a 1946 Caltech
rocket-fuel chemist / occultist thrown to an alien world · and
slowly discover the manuscript itself has been counter-forged by
people who knew you weren't who Hubbard said you were**.

Wizardry IV combat, Ultima IV moral system, planetary-romance
setting, real Thelemic-adjacent progression system, six endings
including one that breaks the fourth wall and dedicates the game
to a man who died in 1952.

## The historical hook (real & fictional)

**The real Jack Parsons** (1914-1952) was a self-taught rocket
chemist whose propellant work founded Caltech's Jet Propulsion
Laboratory.  He was also a devout Thelemite, ran occult rituals
at his Pasadena mansion, and in 1946 conducted the "Babalon
Working" · a ritual to summon a specific consort · with none
other than his friend L. Ron Hubbard as scribe.  Hubbard then
stole Parsons' girlfriend (Sara Northrup, whom Hubbard married)
and Parsons' savings via a yacht-purchase scheme, then left the
Pasadena scene forever.  Parsons died in a lab explosion in
1952.  He was 37.

**Rocha's fictional Hubbard**, in this game's fiction, wrote a
NOVEL in 1948 about the Parsons rite · fictionalized as
"Jack Whiteside", a Caltech chemist who accidentally opens a
gate during a rocket-fuel experiment and is thrown to an alien
world.  The novel was Hubbard's attempt to CLAIM the mystical
frame for himself · to rewrite Parsons as a lesser mystic who
needed Hubbard's guidance.  The manuscript was never published.

**Astro-Cortex in 1985** somehow obtained the manuscript · the
game's fiction is deliberately vague on how · and adapted it as
a slowstick CRPG.  Rocha and a colleague at Astro-Cortex
recognized the source (they'd read the Pendle biography that
was circulating in 1985 as a xeroxed sample) and quietly
counter-forged the ROM to include Parsons' actual voice.

**The player** boots the game and plays what LOOKS like a
Hubbard power fantasy.  A player who plays carefully · listens
for the 220-Hz signal · finds hidden entries in the codex ·
learns to negotiate with a specific late-game NPC · unlocks the
TRUE ending, which is a specific dedication to Parsons' memory.

## Setting

**PASADENA · 1946** (Chapter 1 · single sub-zone)
Jack Whiteside's home laboratory.  A Craftsman house on
Orange Grove Boulevard.  The Parsonage.  The date is JANUARY
1946.  Jack is preparing a specific ritual.  The player's
first choices lock which VERSION of the ritual is attempted.

**PARSA** (Chapters 2-6 · red-tinted desert world)
A planet Hubbard invented in 1948, riffing off Barsoom.
- Two moons, one dying · casts a specific red-purple light
- A crumbling civilization descended from a magical-technological
  golden age
- Multiple sentient species (see species.json when drafted):
  the tall-and-blue KYRINDI · the four-armed rust-red DELVANNI ·
  the small quiet KELAIT (children-shaped, ancient) · the
  utterly-alien "SCARLET WOMAN" who is or isn't Babalon

**THE WORKING** · a mystical layer overlaid on Parsa · reachable
only through specific rituals · where Jack meets the actual
BABALON (or the entity he thinks is her) and confronts what he
did in Pasadena.

## Party of four

Jack always in the party.  Three more slots.

- **HEL VELLI** · a Delvanni warrior · Jack's "Tars Tarkas" ·
  joins Chapter 2 after Jack fights his tribal duel.  Four
  arms, four weapons, no small talk.  Slowly learns to like
  Jack.  Speaks Delvanni ceremonial phrases the player has to
  parse (deliberately not always subtitled).
- **SARA NAI** · a Kyrindi noblewoman · joins Chapter 3 · has
  been having dreams about a specific human man for years · in
  those dreams the man's name is JACK.  Loves Jack easily and
  fully.  In the fiction, she is not Sara Northrup · she IS
  the alien-consort Parsons was trying to summon.
- **THE SCARLET WOMAN** · joins Chapter 5 ONLY after specific
  choices · she is either Babalon-in-truth or a specific
  Delvanni priestess playing at being Babalon · never resolved
  in-game.  Her recruitment is the game's largest single
  branch.
- **ROCHA** · meta-character QA-tester · joins Chapter 4 only
  by talking to a specific NPC and asking a specific question ·
  she claims to be a "cartographer's assistant" · she has one
  scene where she says her real job (in an aside that the game
  frames as a hallucination).

4-slot cap.  Cannot dismiss recruits.  Party is the story · it
matters who's with you when.

## Combat

**Turn-based, tactical grid**.  5×3 cells.  Movement,
positioning, line-of-sight matter.  Different from Fey Faire's
free turn order · this game rewards planning + tactics.

### Classes
- **CHEMIST** (Jack) · precision-flame + psychic-adjacent
  ritual work · access to KREXAL propellant weapons + THELEMA
  RITUALS (see Progression Ladder below)
- **DELVANNI WARRIOR** (Hel) · four-arm melee · greatswords,
  spears, pole-arms all at once · no ranged options · massive
  damage · slow
- **KYRINDI NOBLE** (Sara) · caster · silvery-song magic ·
  charms, heals, unique to Sara
- **PRIESTESS** (Scarlet Woman) · dark-mirror caster · uses
  actual RITUAL WORKINGS in combat · her every skill has a
  cost (HP, SP, or a specific keepsake burned)
- **QA TESTER** (Rocha) · debug-toolkit · her every skill
  BREAKS the game's own rules · reveals enemy stats, skips
  cutscenes, forces specific outcomes · deliberately
  overpowered · Rocha knows what she is doing

### Damage types
- **KINETIC** · Jack's propellant weapons
- **HEAT** · rocket-fuel-adjacent flame attacks
- **BLADE** · Delvanni melee
- **SONG** · Kyrindi voice magic
- **RITUAL** · Thelemic-adjacent working effects · rare, costly
- **TRUE** · Rocha's toolkit · ignores everything

### The Progression Ladder · THELEMIC WORKINGS
Instead of XP + level-up, Earthman Chronicles uses NINE
**WORKINGS** that Jack can perform.  Each Working is a specific
in-game ritual that costs specific components (found via
exploration and combat), requires Jack to fast for a specific
number of in-game days, and grants a specific power.

Rocha's team modeled these on ACTUAL Thelemic ritual structure
(readily available in Crowley's published books, so nothing
secret · but rendered with respect):

- **Working I · The Star Ruby** · defensive · protects one
  battle from panic effects
- **Working II · The Lesser Ritual of the Pentagram** ·
  banishing · dispels one hostile status effect from party
- **Working III · The Bornless One** · summoning · brings
  in one Delvanni ally-fey for one battle
- **Working IV · The Hymn of Pan** · self-buff · +2 all stats
  for one battle
- **Working V · The Mass of the Phoenix** · offensive · single-
  target massive Ritual damage · costs 1 HP permanent
- **Working VI · Liber Reguli** · alignment · locks Jack's path
  toward THELEMIC MASTER path · unlocks Chapter 5's Academy
- **Working VII · The Great Work** · summoning · brings in
  Sara-Nai's "true" form for one battle (she is briefly
  ELEMENTAL rather than Kyrindi) · this is a MOMENT
- **Working VIII · The Star Sapphire** · defensive · protects
  the party from one specific fatal blow
- **Working IX · The Babalon Working** · terminal · triggers
  the endgame · locks specific endings, unlocks others · this
  is the ACTUAL ritual Parsons attempted in 1946

Party members REFUSE to participate in specific Workings:
- Hel refuses Working V (violence-cost he doesn't understand)
- Sara refuses Working IX (she knows what it summons)
- Rocha refuses ALL Workings past Working IV (she says "you
  don't have to do this, Jack") · her personal disposition
  drops if you continue

The Working structure is available in real Thelemic literature.
The game's fiction is that Hubbard's manuscript included them
verbatim, and Rocha's team decided to leave them in — not out
of Thelemic advocacy, but because Parsons believed them, and
Parsons was owed accuracy.

## The Manuscript Layer · Rocha's ROM resistance

At specific moments during Chapter 3+, the game plays a 220-Hz
tone under the music.  These correlate with:
- Hubbard's specific self-aggrandizing narration boxes
- Cutscenes where Jack Whiteside praises Hubbard-analog
  characters (a "Ronson" or "Rafton" NPC · variable name)
- The specific room in Chapter 5 where Jack is asked to
  DENOUNCE Parsons (the actual man, mentioned by full name)

A player who NOTICES the tone (either audibly · headphones
recommended · or via the specific in-game item that visualizes
it · Jack's spectrum analyzer, an easily-crafted piece of
lab-tech from Chapter 1) can find HIDDEN CONTENT:

- **The Pendle Pages** · six xeroxed excerpts from the George
  Pendle biography of Parsons that Rocha and colleagues used as
  their reference · these are REAL fair-use quotes from a
  published biography · rendered in-game as diary entries
- **The Correction** · a note in Rocha's own hand (imagined for
  the game) explaining what she did to the ROM and why
- **Sara's Real Name** · the reveal that Sara Northrup was Jack
  Parsons' actual partner, that Hubbard actually stole her,
  that the game's SARA NAI is a fictionalized recompense
- **The Explosion** · a video sequence · the actual Pasadena
  laboratory explosion that killed Parsons on June 17, 1952 ·
  rendered with respect and specifics

**The TRUE ending requires all six Correction items found.**

Cross-Oneironautics: the 220-Hz tone is the SAME tone that plays
under Northwind Harbor Chapter 2's damaged data on Sam's Pirate
Summer cart.  Same person or same team, twice.  Pirate Summer's
scrapbook chain fact `chain_astrocortex_hid_resistance_together`
unlocks when the player has played both games and noticed both.

## Endings

Six endings, mapped to Working-count + Correction-count + party
disposition:

1. **THE WARLORD OF PARSA** (Workings 1-7 completed · no
   Corrections found)
   The intended power fantasy.  Jack becomes king of the
   Delvanni.  Marries Sara Nai.  Rules Parsa.  A specific
   Hubbardish narration reads it as inspirational; a specific
   detail (Sara's hesitation at the coronation) reads as
   something else on the second look.

2. **RETURN TO EARTH** (Workings 1-6 completed · Working IX
   refused · some Corrections found)
   Jack wakes up in his laboratory.  He is holding a specific
   book.  The date is January 20, 1946.  The Working never
   happened.  Sara Northrup is on the porch (in this ending
   she IS the historical Sara).  Parsons lives another six
   years.  The player watches a montage.  Parsons still dies
   in the explosion.  It just happens later.

3. **BABALON COMES** (Working IX completed · Scarlet Woman
   recruited · few Corrections found)
   Jack completes the Working.  The universe changes.  We are
   shown a specific image: Los Angeles in 1946, from above,
   with a new star in the sky.  Then · a specific closed door.
   Cinematic.  Unresolved.  This is Hubbard's actual claim in
   his 1946 diary.

4. **REFUSED THE WORK** (Workings ≤ 4 · most Corrections found)
   Jack refuses to complete the ritual after Working IV.  He
   stays on Parsa.  Sara Nai stays with him.  They live in a
   specific city called TALIKAN, in a house they build
   together.  Jack dies of age at seventy.  Sara mourns him
   in a language the player has not learned.  A specific
   Delvanni funeral rite plays out.  This is Rocha's team's
   PREFERRED ending.

5. **THE CORRECTION** · aka THE MANUSCRIPT COMPLETES ITSELF
   (ALL 6 Corrections found · Workings ≤ 4)
   The TRUE ending.  The game breaks its own frame.  A specific
   screen shows what appears to be handwritten text (Rocha's
   own hand, rendered as pixel art):

   > "This game was adapted from a manuscript we found in a
   > box in the basement.  L. Rafayette Hubbard wrote it in
   > 1948 to make himself the hero of a story that wasn't
   > his.  The real hero was a man named John Whiteside
   > Parsons who died in his own laboratory on the seventeenth
   > of June nineteen-fifty-two.  He was thirty-seven.  He was
   > a chemist and a mystic.  He was ours before he was
   > Hubbard's ANYTHING.  This is the corrected version.  ·
   > A.R., QA, Astro-Cortex, March 1985."

   Then a specific still image of the actual Parsonage in
   Pasadena, in 1952, on June 18th.  Then black.  Then the
   credits · which include a specific dedication reading
   "For Jack."

6. **HUBBARD TAKES THE CREDIT** (Working IX completed · no
   Corrections found · Rocha never recruited)
   The worst ending.  Jack completes the Working.  A specific
   final cutscene shows Hubbard-in-game claiming Jack as his
   protégé.  The credits roll under a specific Hubbardish
   soliloquy.  Then a specific SCREEN CRACK effect · the ROM
   itself, damaged, playing an error message reading
   "PLEASE INSERT CORRECTED CARTRIDGE."  The player is being
   told they missed something.

## Aesthetic direction

**1985 Amiga + late-Ultima + Wasteland**.  Deep purples for
Parsa's night, rust-red for its deserts, silver-green for the
lab in Pasadena.  Hand-drawn perspective backdrops (like Fey
Faire) but colder and more textured.

Palette:
- Parsa desert `#7c3820` (rust) + `#a86038` (dune) + `#c88848` (sand-lit)
- Parsa sky `#583060` (purple-mauve) + `#382048` (deep dusk) + `#f4c848` (dying moon)
- Pasadena laboratory · `#28324a` (cool blue) + `#c8b478` (Craftsman wood) + `#484850` (steel)
- Ritual purple `#583060` (Working overlay tint · fired during ritual scenes)
- Terminal green `#00c060` (for hidden Correction content)
- Amber amiga `#c86020` (for HUD)
- Warning red `#c02020` (for 220-Hz interference)
- Cream `#e8d090` (readable text)

## The Corrections in detail

Six items · six specific historical facts about Parsons rendered
in the game's fiction:

1. **The Pasadena Fire** · a Pendle-biography excerpt about the
   actual 1952 lab explosion · found by exploring a hidden
   Chapter 5 room during a 220-Hz-marked scene
2. **Sara's Letter** · a note Sara Northrup allegedly wrote to
   Parsons in 1946 · found by talking to Sara Nai after
   Working VII (which briefly makes her human)
3. **The OTO Contract** · the actual document Parsons signed
   with the Ordo Templi Orientis · found in a Chapter 3 cell
   marked with a specific occult symbol the player would only
   recognize from the trailer's Bookcase (see below)
4. **The Autopsy Report** · the coroner's report on Parsons ·
   found in Chapter 6 by revisiting a specific room · rendered
   as pixel-art telegram
5. **Rocha's Signature** · Rocha's own signed statement about
   what she and her colleague did to the ROM · found by
   RECRUITING Rocha as a party member and asking her three
   specific questions
6. **The Dedication** · a hidden ending screen reachable only
   by having the other five Corrections in inventory when
   arriving at the Chapter 6 finale · reads "For Jack" and
   gives the date of his death

## Systems checklist

- [ ] Boot / character creation · Jack's specific backstory ·
      player picks emphasis (chemistry vs. mysticism · affects
      Working availability)
- [ ] Three-slot save
- [ ] Overworld tile renderer (adapt from Pirate Summer · larger
      tile density · red-purple palette)
- [ ] Tactical grid combat renderer (new · 5×3 grid · shared
      with Fey Faire's controller code if we build FF first)
- [ ] Party manager (4 slots, non-dismissable recruits)
- [ ] Parsan species catalog (`species.json` · Kyrindi, Delvanni,
      Kelait, Scarlet, and misc creatures)
- [ ] Weapon + armor + rocket-fuel item catalog (`equipment.json`)
- [ ] Working system tracker (9 workings, component tracking,
      party consent state)
- [ ] Dialogue system (adapted from Pirate Summer's web · with
      branching for the moral choices)
- [ ] 6 chapter zones (~4-8 sub-zones each)
- [ ] Six endings + specific epilogues
- [ ] BGM per chapter · plus specific tracks for Workings and
      the 220-Hz Correction moments
- [ ] SFX for combat, dialogue, quest triggers, ritual
- [ ] Correction Compendium (renders the 6 Corrections)
- [ ] Rocha-as-NPC's specific dialogue tree

**Rough scope**: **4× Pirate Summer's build time**.  The tactical
grid combat is the largest new system.  The Working structure
is a MEDIUM system.  The Corrections are the smallest but
narratively most important.

## The manuscript · in-game

The manuscript IS a scrapbook keepsake in Earthman Chronicles.
The player unlocks it by achieving the CORRECTION ending
(Ending 5).  Once unlocked, it appears in the main-menu
compendium and can be read at any time.  Twelve pages,
photocopied typescript with Rocha's blue-pen marginalia,
coffee stains, occasional editor-mark red-pen from other
Astro-Cortex staff.  See `_EARTHMAN_MANUSCRIPT.md` for the
full document.

The manuscript establishes the specific counterpoint between
what Hubbard wrote and what Astro-Cortex adapted.  Rocha's
marginalia is the game's most explicit editorial voice ·
players who read the manuscript understand what Rocha and
her colleagues did and why.

Cross-Oneironautics: the manuscript document is designed to
also be readable from Fey Faire's Trailer (Prospero's
Airstream).  On Andy Link's slowstick shelf, the manuscript
appears as a cross-game keepsake that persists once earned
in either game's compendium.  Reading it in one game unlocks
its cross-reference in the other.

## Content sensitivity

- **Parsons was real** and died young.  The game portrays him
  with respect.  His mysticism is rendered without mockery ·
  neither endorsed nor debunked · shown as HE believed it.
- **Hubbard is fictionalized** as L. Rafayette Hubbard.  His
  behavior in the manuscript (theft, betrayal) is drawn from
  the historical record but rendered as fictional.  Not
  actionable.
- **Cortexology** is used elsewhere in the Oneironautics
  fiction (see Pirate Summer console_carts.json) · here it's
  Hubbard's pre-Cortexology period, so it's not mentioned
  directly.  This game predates Cortexology's founding in the
  fictional Hubbard biography.
- **Thelemic content** is drawn from Crowley's published works,
  which are public domain / widely circulated.  Rendered
  without either endorsement or dismissal.  Rocha's team's
  attitude (in-fiction) is: Parsons believed this, and Parsons
  deserved to be represented as he saw himself.
- **The Babalon Working** is treated with specific care · the
  game does not "summon" anything real, it's a rendered
  ritual with specific in-game effect, and the option to
  REFUSE it is authored to be the most emotionally satisfying
  path.

## Cross-slowstick connections

- **Pirate Summer** · Northwind Harbor's Chapter 2 damaged
  data is the same 220-Hz technique · a specific chain fact
  `chain_astrocortex_hid_resistance_together` unlocks when
  the player has played both games.  Wu Kai's Y-solder theory
  in Pirate Summer specifically covers this technique.
- **Fey Faire** · Prospero (of Fey Faire's Trailer) had a
  friend at Astro-Cortex.  Playing Fey Faire and finding
  "Prospero's Journal Page 46" (Prospero's Bookcase keepsake)
  seeds a specific Earthman-Chronicles NPC who mentions
  Prospero by name.
- **Estuary 3** · a specific Kwik Stop customer in Manager
  Mode is named ROCHA in the customer pool · same Rocha,
  early in her career, buying frozen dinners.  Small cameo.

## What Earthman Chronicles is NOT

- Not anti-Hubbard specifically · it's about a SPECIFIC ACT of
  historical revisionism by a specific fictionalized author,
  not about the actual Hubbard's entire life
- Not endorsing Thelemic mysticism · the game renders Parsons'
  beliefs as HE held them, without judgment either way
- Not a horror game · the tone is earnest pulp · the horror
  is in the specific real fact that Parsons died young and
  Hubbard rewrote him
- Not longer than it needs to be · six chapters · tightly paced
  · the emotional payoff is the TRUE ending, and the game
  respects the player's time getting there
- Not without warmth · Sara Nai and Hel Velli are genuinely
  good company · Rocha's arrival is a specific joy · the
  Delvanni funeral rite in the REFUSED ending is one of the
  most beautiful scenes Rocha's team ever wrote

## Open design questions

1. **Age of the protagonist**: Parsons was 32 in 1946.  Should
   the game's Jack Whiteside be visibly 32 or a Hubbard-
   friendly younger fantasy?  RECOMMEND: 32, look tired, tired
   for his age.  Rendered with a specific care.
2. **Is Sara Nai actually Babalon?**  RECOMMEND: never resolved
   in-game.  Different endings imply different answers.
   Deliberately ambiguous.
3. **Is Rocha explicitly a QA tester who wrote the ROM, or an
   in-fiction figure?**  RECOMMEND: LATE-GAME REVEAL only ·
   she claims to be a cartographer for most of her party
   time, and her ROM-tester identity is only shown once, in
   one of two specific dialogues.
4. **Difficulty**: HARD?  RECOMMEND: yes · Wizardry IV-hard ·
   permadeath as a specific mechanic (see below).
5. **Permadeath?**  RECOMMEND: yes for party members ·
   they can die permanently in specific fights · if Sara dies,
   Working VII is unavailable and specific endings are locked
   · if Hel dies, the Delvanni will not accept Jack · if
   Rocha dies, the Corrections are unfindable · these are
   REAL stakes
6. **NG+?**  RECOMMEND: yes · keep Corrections and quotes
   between runs · so a completionist speed-run of the TRUE
   ending is achievable on NG+ but not first-play
