# SWEETGUM · DESIGN
### no publisher · zine-traded homebrew · 1996 · WAITING HORROR
### one night · August 14, 1976 · the watchman

Made by a survivor's kid on burned EEPROM, traded at Pacific
Northwest zine fairs, cease-and-desisted by Oneironautics' lawyers
in 1997 — the paper trail that proves the studio was researching
Camp Sweetgum (and knew the name Nika Voss) years before Pirate
Summer shipped in 2002 and decades before they admitted anything.
Olaf's copy was a gift from the author at a Portland zine fair.
His provenance note is one line: *"I asked her why. She said: so
it's someone's JOB to stay awake."*

**Unlock gate:** does not appear on the shelf until Pirate
Summer's core 1976 facts are discovered. The shelf slot before
then is simply not there — no locked placeholder. The stick
arrives in the collection the way knowledge does.

---

## THE LOOK

**Homebrew crude, faithfully.** Single phosphor green on black.
A deliberately mis-kerned bitmap font (author-drawn; two letters
are each other's mirror). The camp is an ASCII-adjacent line
diagram — eight stations, paths, the waterline — that would be
charmless if it weren't so evidently traced from somewhere real.
Players of Pirate Summer will recognize the geography instantly
and feel the floor tilt: it is the SAME camp, drawn by hand,
fourteen years earlier, in the year it mattered.

    #041104  dead screen      #46d84a  phosphor
    #1c5a20  phosphor dim     (three colors · that's all)

Intentional artifacts: a scanline tear on station 6's screen
(present in every copy · the author's burner did it · canon), and
the log page renders one character-width too narrow so long
entries wrap ugly. Do not fix these.

**HeroImages:** none. The game predates the concept, in-fiction
and in spirit. The diagram is the only picture.

## THE SOUND

Room tone and a wall clock. Footsteps on gravel rendered as soft
noise ticks. Crickets that stop being audible around 2 AM without
the player noticing when. Exactly THREE sounds out on the water
around 3 AM — rendered quiet, mixed lower than the clock, meant
to be argued about. No stinger. No music at all until 6 AM: four
notes as the sky line brightens, source unknown.

## THE PLAYSTYLE

**One night, real-time-ish: 9 PM to 6 AM in about forty
minutes.** You are the night watchman. The date is on the log
header. The game never mentions it again.

- **ROUNDS.** Eight stations (gate, mess, boathouse, cabins ×4,
  waterline). Walk the diagram, CHECK each padlock, mark the
  round. Rounds are due hourly; the game does not enforce this;
  the log simply shows the gaps.
- **THE LOG.** The core mechanic. A typed watch log — the player
  actually types entries, free text, timestamped. The template
  has fields: TIME · STATION · CONDITION. **The log persists
  across every run of the cartridge** — Sam's-save style — so
  the file becomes a palimpsest of every night every player ever
  stood this watch. Olaf's copy arrives with nineteen years of
  entries already in it, including the author's. (Authored
  content presented as accumulated saves.)
- **THE NIGHT.** Almost nothing happens, and the almost is the
  design: around 3 AM, three sounds on the water. A light on the
  island that the log template HAS NO FIELD FOR — the cursor
  simply won't file it under CONDITION, and the player's attempt
  to log it anyway (everyone tries) produces the game's only
  error message: `NOT A STATION.`
- **6 AM.** The sky line brightens. Four notes. The log closes
  itself with an entry the player didn't type: `06:00 · ALL ·
  QUIET`. Whether that is the game being kind or the game lying
  is the whole aftertaste.
- **Second playthrough:** one cabin door that was locked is
  unlocked. Inside is nothing but a made bed. The log gains a
  field it didn't have: NAMES. It is never filled. There is no
  third variation. The author said what she had.

No jump scares. No death. No antagonist on screen, ever. The
horror is structural: the player knows the date; the watchman
doesn't; the job is to stay awake at the edge of something that
history says happens anyway, and the game will not confirm
whether tonight is the night — because for the watchman, every
night was.

## THE AMBITION

- The bravest single scene in the catalog: horror as DUTY, dread
  without event, the slowstick ethos aimed at the one genre that
  supposedly can't survive it.
- Fix 1976 as the meta-narrative's load-bearing year from a
  THIRD angle (the Faire took a sister · the camp took campers ·
  the homebrew keeps the watch), by an outsider with no studio,
  which is exactly why hers is the version that feels true.
- Make the C&D lore playable: the shelf unlock mirrors the paper
  trail — you cannot own this stick before you know why it
  exists.
- Tokens out: `sweetgum_watch_stood`, `sweetgum_island_light_
  logged_attempt` (Pirate Summer's shortwave gains one new
  fragment; the federal-boats facts gain a line). Tokens in:
  gate on PS 1976 facts as above.

## BUILD

One scene + host. Real-time timers, the typed log widget (a
LineEdit + persistent JSON of entries — the palimpsest file
ships pre-seeded with authored entries), the diagram as a drawn
Control. Three colors, no sprites, no hero images, one 4-note
cue. Small build, heavy object. Do it in one sitting or not at
all.
