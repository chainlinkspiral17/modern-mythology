# EARTHMAN CHRONICLES — design doc

Slowstick #4 · **Astro-Cortex · 1985 · L. Rafayette Hubbard**.

Found in-fiction as a cartridge in Pirate Summer's slowstick
console (mess hall, 1994).  Andy Link boots it after Fey Faire.
The player of Earthman Chronicles is a specific human colonist
named REMBRANDT VONN, third-generation off-Earth, employed as a
courier for the Terran Communications Consortium.

Genre: **turn-based scifi CRPG** in the shape of Wizardry IV or
early Ultima · six-chapter story, party of four, real combat
depth, actual moral choices, actual endings.

Tone: **earnest 80s space opera at the surface, cult subtext
rising underneath**.  L. Rafayette Hubbard was a pulp scifi
writer who founded a specific spiritual practice called
CORTEXOLOGY in 1955 · this game is his adaptation of his own
BATTLEFIELD EARTH novel series filtered through his
Cortexology-adjacent 'Progression Ladder' framework.  Rocha ·
who did NOT play Fey Faire's author-role here · was a QA tester
at Astro-Cortex when this shipped.  The game is the studio's,
not hers.  Its complications are its own.

Cross-Oneironautics: Earthman Chronicles is the LEAST auto-
biographical of Rocha's Oneironautics catalog because IT ISN'T
HERS · she was junior staff, not creative lead.  But she signed
off on it, and her name appears in the credits, and there are
specific moments (a courier named ROCHA appears in Chapter 2, a
Portuguese folk tune plays in the Cortexology hymn scene) that
tell you she was in the room.

**The mystery**: this cartridge, in Pirate Summer's console, boots
with 220-Hz interference at specific moments · specifically when
CORTEXOLOGY doctrine is delivered on-screen.  Something at
Astro-Cortex disagreed with Hubbard.  Someone quietly hid
resistance in the ROM.  The player of Earthman Chronicles,
watching Hubbard's power fantasy · slowly realizes the game is
being told from a specific and hostile perspective.

## Elevator pitch

**A turn-based scifi CRPG where you slowly realize the game is
adapting a cult founder's power-fantasy · and you are one of
maybe five people who ever notice**.  Wizardry IV moral system,
Ultima IV character alignment, Battlefield Earth setting,
Cortexology-adjacent 'Progression Ladder' as an in-game
leveling mechanic.

You start as a courier.  You end as either the LIBERATOR of
Earth from Psychlo-adjacent aliens (the intended power fantasy)
OR the FIRST PERSON TO NOTICE what the game is · and get out.

## Setting

Year 3000.  Earth was conquered by the KREXAL a thousand years
ago (Rocha's Astro-Cortex renaming of the novel's Psychlos).
Humans live as slaves in the mines, ignorant of their history,
speaking a specific broken language called TERRIC.

The player is REMBRANDT VONN, a third-generation off-Earth
courier.  His family fled Earth generations ago and lives in the
DERELICT COLONIES on outer moons.  Rembrandt has been asked to
courier a specific data-crystal to a Krexal-controlled Earth
outpost.  He does not know what's on the crystal.  Neither do you.

Six chapters:

1. **THE OUTER RIM** · courier work · introduces combat, party,
   dialogue.  Ends with the crystal reveal.
2. **THE APPROACH** · crossing Krexal-controlled space.  Meet the
   party.  First moral choices.
3. **EARTH** · descent to the surface.  Meet the humans who don't
   know they're slaves.  Cult subtext begins to appear.
4. **THE MINES** · deep dive into Krexal mining operations.
   Cortexology doctrine appears as literal in-game curricula.
   The 220-Hz interference starts.
5. **THE ACADEMY** · Rembrandt is invited to the Krexal
   'Progression Academy' · an on-map dungeon that is also
   literally the Cortexology audit process rendered as gameplay.
6. **THE FINALE** · fight the Krexal warlord, or don't.  Every
   ending is on the table.

## Party of four

Rembrandt is always in the party.  Three more slots.  Recruits:

- **JETHER TAAL** · a Krexal defector · warrior-class · joins
  Chapter 1.  Massive damage, low speed, immune to Krexal
  standard weapons.  A specific line about "I saw what we did
  in the mines" delivered in Chapter 3 lands hard.
- **ELIZA KANG** · a Terran archivist · scholar-class · joins
  Chapter 2.  Support caster, reveals lore, translates.  Reads
  the crystal's contents in Chapter 3 · her reaction is the
  game's first genuinely dark moment.
- **VESH THE OLD** · a mine-slave gone free · rogue-class ·
  joins Chapter 3.  Can be recruited only if the player chose
  a specific dialogue in Chapter 2.  Highest speed in the game.
  Speaks in a broken TERRIC that the player has to slowly learn
  to parse (the game does NOT translate everything).
- **ROCHA** · a data-courier meeting on the Approach ·
  META-CHARACTER · joins Chapter 2 only if the player asks her
  correctly.  Rocha the QA-tester wrote herself in.  She has a
  small role.  She survives every ending.

At most 4 total in the party.  Cannot dismiss any recruits ·
they are here for narrative reasons, not just combat.  If the
player wants a fifth (a Krexal warlord's daughter or a
Cortexology auditor), the game asks them to KILL a party member
first.  Nobody in the party will accept this.

## Combat

**Turn-based, 4-slot party vs. 1-6 enemies.**  Grid-based combat
(unlike Fey Faire's freeform turn order · Earthman Chronicles is
tactical).  Each combatant occupies a specific cell in a small
5×3 tactical grid.  Movement, positioning, line-of-sight matter.

### Classes
- **COURIER** (Rembrandt) · balanced · access to KREXAL FIRE-
  ARMS + basic PSYCHIC skills · high wit, medium strike
- **WARRIOR** (Jether) · melee-only · greatswords and
  power-fists · low speed, massive damage
- **SCHOLAR** (Eliza) · caster · low HP, high SP · uses
  KREXAL RESEARCH SKILLS + PSYCHIC MASTERY
- **ROGUE** (Vesh) · stealth + damage · dual daggers,
  KREXAL-ISH SABOTAGE · highest speed
- **QA TESTER** (Rocha) · unique class · her skills DEBUG the
  fight · she can 'set a flag' that reveals enemy HP + weakness
  + intent · she can 'skip a cutscene' that would otherwise
  give an enemy an extra turn

### Damage types
- **KINETIC** · standard projectile weapons
- **ENERGY** · lasers, plasma, disruptor beams
- **PSYCHIC** · Cortexology-adjacent mind attacks (Rembrandt +
  Eliza)
- **CORROSIVE** · Krexal industrial weapons
- **SONIC** · rare · used by specific late-game bosses (and
  the 220-Hz interference)
- **TRUE** · Vesh's dagger types · ignores armor

### The Progression Ladder
Instead of XP + level-up, Earthman Chronicles uses the
Cortexology-adjacent PROGRESSION LADDER · nine tiers · each
tier requires the player to:
1. Complete a specific in-game questionnaire (SESSION)
2. Pay an in-game currency (COORDINATION CREDITS · earned
   by combat and quests)
3. Perform a specific in-game action (AUDIT another party
   member · a mechanic that reveals their private worries and
   converts them into buffs · but which they FIND WEIRD)

The ladder is authored so that:
- **Tiers 1-3** feel like normal RPG leveling · everyone does it
- **Tiers 4-5** the party members start commenting on how strange
  the sessions are
- **Tier 6** Eliza refuses to audit further.  Jether does one
  more audit and then quits the ladder.  Vesh never joined.
  Rocha never joined.
- **Tiers 7-9** are AUTHOR-INTENDED for Rembrandt only.  Reaching
  Tier 9 unlocks the LIBERATOR ending · but with a specific
  cost.

The player who FINISHES the Ladder gets the intended power
fantasy · Battlefield-Earth-style triumph.
The player who REFUSES the Ladder past Tier 5 gets what Rocha
would call the good ending.

## The mystery · Rocha's ROM interference

At specific moments during Chapter 4+, the game plays a 220-Hz
tone under the music.  These moments correlate with:
- Cortexology doctrine cutscenes
- Certain named enemies (KREXAL AUDITOR class)
- The exact rooms of the Progression Academy in Chapter 5

The player who NOTICES the tone (either audibly · headphones
recommended · or via a specific in-game item that visualizes it)
can find HIDDEN CONTENT · specifically, entries in the KREXAL
COMPENDIUM that Astro-Cortex QA slipped in without Hubbard's
knowledge.  These entries include:
- A named QA tester's diary
- A specific critical review of Battlefield Earth's cult subtext
- A leaked memo from Astro-Cortex's editorial staff about a
  disagreement with Hubbard over Cortexology content
- Rocha's own note (dated 1985) saying "we did what we could"

**The GOOD ENDING requires the player to find enough of these
hidden entries.**

Cross-Oneironautics: the 220-Hz tone is the SAME tone that plays
under Northwind Harbor Chapter 2's damaged data on Sam's Pirate
Summer cart.  It's Y-solder redaction across BOTH games ·
same specific staff, same specific act of quiet resistance.

## Endings

Six endings, mapped to the player's ladder-tier + hidden-content
completion:

1. **LIBERATOR** (Ladder tier 9, no hidden content) · the
   intended power fantasy.  Rembrandt frees Earth.  Cortexology
   spreads across the galaxy.  A specific speech is delivered
   that reads as inspiring on first pass and as a specific
   kind of horror on second.
2. **FALLEN LIBERATOR** (Ladder tier 9, some hidden content) ·
   same as above but Rembrandt seems tired.  The final speech
   contains ad-libs Rembrandt did not intend to make.  Eliza
   is not present at the coronation.
3. **REFUSED THE LADDER** (Ladder stopped at tier 5-6, no
   hidden content) · Rembrandt gives up on the war and goes
   back to courier work.  Melancholic.  Earth stays enslaved.
   A quiet, sad life for Rembrandt.  This is the accidental
   'bad ending' that the game frames as bad but isn't.
4. **QUIET RESISTANCE** (Ladder ≤ 5, most hidden content
   found) · Rembrandt joins a specific underground resistance
   cell led by a QA-tester-fictionally-named-Rocha.  Cortex-
   ology is not defeated but is documented.  Earth stays
   enslaved but WITH KNOWLEDGE.  A somber victory.
5. **THE ROM READS BACK** (all hidden content found, Ladder
   stopped at tier 4 exactly) · the game breaks the fourth
   wall.  A specific screen tells the player: 'You are the
   fifth person to have played this game and understood it.'
   Displays the (fictional) names of the four before you (dated
   1985, 1988, 1994, 2007).  Rocha's name appears as a
   credit-signature.  Considered the TRUE ending.
6. **HUBBARD LAUGHS** (Ladder tier 9, actively RECRUITED an
   Auditor NPC to the party via a specific late-Chapter-4
   dialogue) · a specific hidden ending only findable via
   negotiation with a KREXAL AUDITOR.  Considered the WORST
   ending by the QA staff who quietly authored ROM resistance.
   A specific speech by Hubbard-in-game claims Rembrandt as
   his true heir.  Rembrandt looks miserable.

## Aesthetic direction

**Amiga / early DOS · Wasteland · Ultima IV · Bard's Tale**.

Specifically:
- **Top-down tile-based overworld** for planet-surface
  exploration · 32×32 tile sprites, but SPACE-OP palette
  (deep purples, alien greens, orange stars)
- **First-person tactical combat scene** on a 5×3 grid ·
  vector-line style enemy portraits (Ultima IV enemy sprite
  aesthetic)
- **HUD-heavy** · this is a serious CRPG · lots of stats
  visible always, cursor-hover for detail, F-key
  hotkey menus everywhere
- **CRT dark palette**  ·  the black is DEEP, the amber is
  amber, the green (dominant color) is 1985-arcade-monitor
- **NO cinematic cutscenes** · everything happens in the game
  view with text boxes at bottom · this is a slowstick 1985

Palette:
- Deep purple `#181828`
- Amiga amber `#c86020`
- Arcade green `#00c060`
- Krexal industrial gray `#484850`
- Cortex-purple `#583060` (for Cortexology-adjacent scenes)
- Warning red `#c02020` (for the 220-Hz moments)
- White text `#f0f0f0` (readable · big pixels)
- Warm terminal cream `#e8d090` (for hidden QA content)

## Systems checklist

- [ ] Boot / character creation (Rembrandt's specific pre-set
      backstory + player-picked class emphasis)
- [ ] Three-slot save (like Pirate Summer / Fey Faire)
- [ ] Overworld tile renderer (adapt CampOverworld from
      Pirate Summer · larger tile density)
- [ ] Tactical grid combat renderer (new · 5×3 grid)
- [ ] Party manager (4 slots, non-dismissable recruits)
- [ ] Krexal + Terran species catalog (`species.json` · similar
      to feys.json but scifi-flavored)
- [ ] Weapon + armor + item catalog (`equipment.json`)
- [ ] Progression Ladder tracker (nine tiers, session-audit
      records, party consent tracker)
- [ ] Dialogue system (adapted from Pirate Summer's web · this
      one has actual branching)
- [ ] 6 chapter zones (~5-8 sub-zones each)
- [ ] Six endings + specific epilogues
- [ ] BGM per chapter · plus specific tracks for Cortex-
      ology scenes and the 220-Hz interference moments
- [ ] SFX for combat, dialogue, quest triggers
- [ ] Hidden content compendium (Krexal Compendium)
- [ ] Rocha's ROM entries (specific hand-authored diary text)

**Rough scope**: **4× Pirate Summer's build time**.  The tactical
grid combat is the largest new system.

## Cross-slowstick connections

- **Pirate Summer** · Northwind Harbor's Chapter 2 220-Hz tone
  is the SAME tone.  Playing both games and noticing gives you
  Pirate Summer scrapbook chain fact
  `chain_astrocortex_hid_resistance_together`.
- **Fey Faire** · a specific keepsake in Fey Faire (Prospero's
  Journal · Page 46) hints that Rocha's babysitter Prospero
  had a friend at Astro-Cortex.  If the player has found this
  keepsake in Fey Faire before playing Earthman Chronicles,
  a specific NPC in Chapter 2 says the name.
- **Estuary 3** · none directly (Estuary 3 predates the shared
  ROM-resistance thread).  But: a Kwik Stop customer in
  Estuary 3's Manager Mode named REMBRANDT can be identified
  as the same Rembrandt.  Cameo.

## Open design questions

1. **How much cult content is safe to render?** RECOMMEND: pastiche
   deep enough to be recognizable but with fictional names
   throughout · CORTEXOLOGY not Scientology · KREXAL not
   Psychlo · L. Rafayette not L. Ron.  Rocha's fictional Hubbard
   is a specific pulp-writer-with-cult, not a lawsuit target.
2. **How much of Chapter 5 (the Academy) is playable vs. cutscene?**
   RECOMMEND: mostly playable · this is the game's genuine
   dungeon crawl · Cortexology audits as room-shaped puzzles
   is a genuinely good mechanic if done with respect.
3. **Difficulty vs. Fey Faire?** RECOMMEND: HARD, but in a
   different way · Fey Faire is unforgiving-in-moments · Earthman
   Chronicles is grindy-in-attrition · you WILL run out of
   coordination credits before you finish the Ladder if you
   don't plan.  Multiple replays required.  Different discipline.
4. **Does the player need to have played Fey Faire first?**
   RECOMMEND: no.  Both are independent slowsticks that reward
   playing the other, but neither GATES the other.  Order of
   discovery is user-driven.

## What Earthman Chronicles is NOT

- Not a satire.  The game is EARNEST at surface · the cult
  subtext is quiet, discoverable, not lecturing.
- Not anti-Scientology (specifically).  It's about the specific
  mechanism by which entertainment products can smuggle
  ideology · Battlefield Earth is a case study, not a target.
- Not a power fantasy · although it pretends to be.  If you
  finish the Ladder without questioning, you get the power
  fantasy · Rocha's team included that ending deliberately as
  a control group.
- Not longer than it needs to be · six chapters, tightly
  paced.  Not a 60-hour CRPG.
- Not without humor · Rocha's fingerprints are in the levity ·
  Vesh's TERRIC misunderstandings, Rocha-as-NPC's specific
  QA jokes, Jether's slow warming to Earth culture.
