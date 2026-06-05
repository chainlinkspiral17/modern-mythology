# Tarot Lore for Modern Mythology

How the classical Major Arcana relationships map onto the Graustark
cast, and how that informs cross-card gating decisions. This is a
working reference — not a generic tarot primer.

## Three traditional axes the project uses

### Axis A — Fool's Journey

The full Major Arcana read as one character's coming-of-age, with
each numbered card a station the Fool passes through. In Modern
Mythology this maps onto John Frank's vol5 arc most directly, but
because the deck is multi-POV, every card is *somebody's* station —
the Fool's Journey is fractured across the cast.

| #     | Card             | Project anchor              | Station        |
|-------|------------------|-----------------------------|----------------|
| 0     | The Fool         | John (D'Ambrosio's diner)   | The threshold  |
| I     | The Magician     | Frasier (Cathedral of Rust) | The will       |
| II    | The High Priestess| Elicia (gift shop/archive) | The mystery    |
| III   | The Empress      | Nicola + Aria (split POV)   | The body       |
| IV    | The Emperor      | Dante (sepia throne)        | The structure  |
| V     | The Hierophant   | (Acadian, Sunday sermons)   | The tradition  |
| VI    | The Lovers       | (Sanctuary on Cursed Ground)| The choice     |
| VII   | The Chariot      | TBD                         | The drive      |
| VIII  | Strength         | (gentle, the lion-tamer)    | The mastery    |
| IX    | The Hermit       | TBD                         | The retreat    |
| X     | Wheel of Fortune | TBD                         | The turn       |
| XI    | Justice          | Erica + Anna (dual POV)     | The reckoning  |
| XII   | The Hanged Man   | Natalie (Simon's apartment) | The surrender  |
| XIII  | Death            | (Ward C, Walpurgisnacht)    | The transform  |
| XIV   | Temperance       | Frank (Tuesday observation) | The integration|
| XV    | The Devil        | (Gumbo Limbo / Daigle's)    | The shadow     |
| XVI   | The Tower        | Evangeline (render queue)   | The break      |
| XVII  | The Star         | (Glass Skin, Christian Ice) | The hope       |
| XVIII | The Moon         | Natalie (sigils in static)  | The illusion   |
| XIX   | The Sun          | Frank (dust motes)          | The clarity    |
| XX    | Judgement        | (ensemble, dust notes)      | The calling    |
| XXI   | The World        | (Frog Knows Best)           | The cycle      |

### Axis B — Numerical mirror (n + (21−n) = 21)

Each card is paired with its complement across the Major Arcana
midpoint. These are the deepest classical pairings — the card's
"opposite number" is the one it argues with across the deck.

| Pair              | Tension                              |
|-------------------|--------------------------------------|
| Fool (0) ↔ World (XXI)         | beginning ↔ completion        |
| Magician (I) ↔ Judgement (XX)  | will ↔ awakening              |
| Priestess (II) ↔ Sun (XIX)     | inner light ↔ outer light     |
| Empress (III) ↔ Moon (XVIII)   | body ↔ illusion (Nicola↔Natalie naturally splits here) |
| Emperor (IV) ↔ Star (XVII)     | structure ↔ hope              |
| Hierophant (V) ↔ Tower (XVI)   | tradition ↔ revelation        |
| Lovers (VI) ↔ Devil (XV)       | union ↔ bondage               |
| Chariot (VII) ↔ Temperance (XIV)| drive ↔ moderation           |
| Strength (VIII) ↔ Death (XIII) | soft mastery ↔ hard ending    |
| Hermit (IX) ↔ Hanged Man (XII) | chosen solitude ↔ forced suspension |
| Wheel (X) ↔ Justice (XI)       | fate ↔ choice                 |

For Modern Mythology specifically, the Empress↔Moon mirror is doing
double work: both cards feature Natalie, but on opposite sides of
the body/sigil split. The Nicola/Aria dual-POV on Empress prefigures
Natalie's static-sigil interiority on Moon — same character archi-
tecture, different chapters.

### Axis C — Active / Receptive pairs

Adjacent cards that argue across a polarity rather than across the
midpoint. These are the local relationships that the diner-to-
workshop kind of cross-card gating naturally uses.

| Pair                  | Polarity                                     |
|-----------------------|----------------------------------------------|
| Fool ↔ Magician       | seeker ↔ the will the seeker assumes         |
| Magician ↔ Priestess  | conscious will ↔ unconscious archive (he draws, she reads) |
| Priestess ↔ Empress   | archive ↔ body (recorded ↔ lived)            |
| Empress ↔ Emperor     | nature ↔ structure (the throne both share)   |
| Emperor ↔ Hierophant  | secular order ↔ religious order              |
| Lovers ↔ Chariot      | choice ↔ commitment to motion                |
| Justice ↔ Hanged Man  | judgement passed ↔ suspended in judgement    |
| Death ↔ Temperance    | ending ↔ blending                            |
| Devil ↔ Tower         | bondage normalized ↔ bondage shattered       |
| Star ↔ Moon ↔ Sun     | hope · illusion · clarity (the night trio)   |
| Judgement ↔ World     | individual awakening ↔ collective closing    |

## Cross-card gating heuristic

When deciding whether two cards should have a dormant cross-card
hotspot pair, ask which axis the pair sits on:

- **Axis B (mirror)**: the gate should reveal a *reflection* — the
  same artifact seen from the opposite pole. Empress's HUD waveform
  ↔ Moon's static-sigil; Fool's diner ↔ World's frog-knows-best are
  the cleanest mirror gates.

- **Axis C (adjacency)**: the gate should reveal a *causal chain* —
  the act on one card leaves a trace on the next. Magician's
  soldering iron → Fool's demoscene engine boot is an adjacency gate
  (his will makes the seeker's footnote come alive). Magician's
  infinity → Priestess's book spine is also adjacency (he draws, she
  archives).

- **Axis A (journey)**: the gate should reveal a *station marker* —
  evidence that one figure is passing through the other's space.
  John's bindle showing up in Frasier's workshop is a journey gate
  (the Fool has been here before the chapter says so).

The COMPASS.md graph in this directory is the canonical edge list
the player ultimately gets to see. The current `cross_references`
maps in each hooks JSON are where each edge is declared.

## What's wired in code right now

These cross-card gates are LIVE in the discovery layer (clicking the
source side wakes the dormant hotspot on the target side):

| Source                              | Target                       | Axis |
|-------------------------------------|------------------------------|------|
| Magician.mag_steamboat              | Fool.fool_steamboat_echo     | A    |
| Magician.mag_steamboat              | Emperor.emp_steamboat_throne | C    |
| Fool.fool_demoscene_mod             | Magician.mag_demoscene_echo  | C    |
| Fool.fool_demoscene_mod             | Emperor.emp_demoscene_engine_marker | C    |
| Fool.fool_inner_card                | Priestess.pri_fool_archive   | A    |
| Magician.mag_infinity_sigil cipher  | Priestess.pri_infinity_glyph | C    |
| Magician.mag_crt_readout cipher     | Empress.ems_aria_handshake_marker | C    |

And these item-carry pairs are LIVE:

| Source (gives_item)         | Target (requires_item)         |
|-----------------------------|--------------------------------|
| Fool.fool_bindle            | Magician.mag_paint_can         |
| Magician.mag_soldering_iron | Fool.fool_demoscene_mod        |

## Reading order for new cards

When a new card lands, before adding its hotspot/cipher set:

1. Identify its number (n). Its mirror pair is XXI − n.
2. Read the existing hooks JSONs for both its adjacencies (n−1, n+1)
   and its mirror.
3. Propose 2 cross-card gates per axis (A, B, C) — not all six need
   to ship, but the design has them in mind.
4. Update the cross_references map in the new card's hooks AND
   reciprocally in the partner card's hooks.
5. Add the gated_by hotspot + matching cipher on whichever side
   makes diegetic sense (usually the *target* of the implication —
   the card that learns something new from the partner's revelation).
