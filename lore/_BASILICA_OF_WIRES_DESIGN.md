# BASILICA OF WIRES · DESIGN
### Astro-Cortex Software · 1987 · SIGNAL HORROR / DUNGEON CRAWL
### the transmitter under the mountain · J.F. broadcasting into 220 Hz

Astro-Cortex's last stick before folding in 1989. Written by
J.F. — the Earthman senior engineer — in the two years after
A. Rocha left for Portland. Fewer than 900 copies pressed.
**Olaf never found one.** On the shelf it exists as his
hand-labeled empty sleeve: "still looking · 30 yrs."

---

## THE LOOK

**First-person wireframe crawl.** Black raster, cyan vector
lines, white for near geometry, and one reserved color — signal
amber — for anything energized. The 1987 fiction wants Elite /
Wizardry vectors; ours renders as Control-node line drawing (the
one genuinely new renderer in this catalog: a `WireframeView`
that draws a cell's walls/props from a small line-list JSON per
cell type).

    #000000  the dark          #38c8d8  structure cyan
    #e8f4f8  near-white        #e8a830  signal amber
    #7a3868  scramble violet   (map corruption only)

The place: a cathedral-sized longwave transmitter built into a
mountain in 1938 for a war it barely served, never fully
decommissioned. Galleries of porcelain insulators like organ
pipes, capacitor halls, a stair called the anode choir, catwalks
over resonant cavities. Everything is drawn as if the mountain
is one instrument, because it is.

**The map scrambles.** Standing waves corrupt your automap —
corridors you walked render displaced, in violet, until you
re-tune. The map is the health bar.

**HeroImages:** the empty sleeve / wanted poster (ships NOW as
the stub art) · the master breaker with the eight-pointed star
etched above it · the message room.

## THE SOUND

The whole game is mixed from sine waves and hum — the synth's
purest voices. Every room has a resonant pitch; navigation by
ear is real: the deeper you go, the lower the fundamental. At
exactly **220 Hz** — and only there — the corridors hold still,
the map repairs, and the violet drains out. The player's safe
frequency is the Corrections channel. The game never says so.

## THE PLAYSTYLE

**The tuner is the verb.** A dial (coarse + fine) replaces
sword and torch:

- Rooms and doors EXIST per band — a corridor at 400 Hz is a
  wall at 800. Progress = learning the building's chord chart.
- Standing-wave hazards: zones where your carried tune beats
  against the room's; the interference visibly shreds the map
  and (meter: COHERENCE) your sense of where you are. Coherence
  at zero = you wake at the last junction with the map violet.
  No death. Worse: unreliability.
- Nine descent levels. Landmarks: the insulator gallery, the
  choir, the half-flooded cavity where the tune comes back
  WRONG (three seconds late, a perfect fifth up — never
  explained), the master breaker with the star.
- **The message room** (level nine, findable only by holding
  220 Hz through the longest interference run in the game): a
  teletype page, in QA annotation format, addressed to no one.
  It is J.F.'s. It is not summarized here. It is the reason the
  game exists, and the player who reaches it will know both
  those things at once.

Run length ~4 hours. One ending. You climb back out; the game
counts your remaining coherence silently and prints one of three
final lines on the mountain door.

## THE AMBITION

- Canonize the ORIGIN of 220 Hz as a channel between two people:
  hidden AT it in 1985 (the Corrections, together), broadcast
  INTO it in 1987 (J.F., alone). Every later 220 Hz — Earthman's
  Observatory, Pirate Summer's shortwave — descends from this.
- Let the Order leak into a second publisher's catalog: the
  eight-pointed star on the breaker, uncommented, in a game with
  no occult story at all. Wrongness by placement.
- **The absence is the first deliverable.** Olaf's empty sleeve
  stub ships immediately — a wanted poster on the shelf, the
  only stick rendered as a hole. In 2048 Tem finds one at
  auction for more than the cabin is worth; whether to buy it
  is a Vol 7 present-day beat, outside this game.
- Tokens out: `basilica_message_room_reached` (Earthman Codex
  endpaper gains one additional line). Tokens in:
  `earthman_correction_ending_seen` changes the message room's
  final annotation from unread to read.

## BUILD

Two-phase. PHASE A (now): stub-as-absence — empty-sleeve sprite,
wanted-poster stub manifest, shelf renders it as the catalog's
one hole. PHASE B (when engine appetite exists): `WireframeView`
line renderer + cell JSONs + tuner input + coherence/map systems.
The only stick here that needs a new renderer; everything else
is data.
