# THE SISTERS WYRD · DESIGN
### Sagebrush Engineworks · Amarillo, TX · 1983 · HEXCRAWL RPG / DARK WESTERN
### seven scales of one territory · four witches on a compass that lies
### STATUS: BUILT · playable_v1 (2026-07) · host + WyrdHexcrawl,
### nested 7-scale hex navigation (ride/zoom), deterministic
### terrain from the address hash, encounter deck, four witch
### seats with PARLEY/DRAW/UNWEAVE, the eighth-point loom ending,
### sagebrush look preset, Morgan le Fey consumes the eighth point

The oldest playable cart on the shelf. Before Earthman (1985),
before anyone had agreed what a slowstick was FOR, a two-man
outfit in Amarillo — an ex-pinball-ROM programmer and his
sister, who painted paperback covers — shipped a dark western
about a territory that is secretly a weave. Dorothy by way of
the Gunslinger: a drifter with iron on the hip and a home hex
behind them, and four witches seated at the corners of a world
that repeats the deeper you look.

Olaf's copy: bought used in 1991. The previous owner's
hand-drawn hex maps are folded inside the case — careful,
complete, and wrong in exactly one hex. Olaf checked. He left a
note: *"the map is wrong where the world is. keep both."*

**The lattice fit:** 1983 · a fourth publisher · no contact with
Oneironautics or Astro-Cortex canon except one object — the
compass rose painted on the cart label has EIGHT points. The
game names four witches. The other four points are never
labeled, in the manual or anywhere. Wrongness by placement,
two years before the Order surfaces at Astro-Cortex. Nobody at
Sagebrush ever answered a letter about it.

---

## THE LOOK

Pulp-paperback cover inks — the sister's trade. A warm dust
field, heavy black linework, bone white, blood-brown, one
silver, and ONE violet reserved for the wyrd (anything woven:
witch-sign, the loom, the shimmer at high scales). The territory
is drawn as seven fat hexes — the one you ride and its six
neighbors — big as playing cards, terrain-inked like cover art,
not like a wargame.

    #c8a878  dust           #201410  linework black
    #e8dcc0  bone           #7a3020  blood-brown
    #b8bcc8  silver         #8a58a8  the wyrd (reserved)
    #4a5a3a  scrub green

At scales 5–7 the hexes SHIMMER: each big hex faintly shows its
seven children, and the children show theirs — the self-similar
weave, visible, unexplained. Players who zoom all the way out
and squint are seeing the game's whole theology.

**HeroImages:** the territory from the world hex (title) · the
compass card with eight points and four names · the loom · the
home hex porch at dusk.

## THE SOUND

A lonesome two-note figure over a low drone — leather, distance,
one string instrument the synth approximates without apology.
Each witch's seat pitches the same four-note SISTERS motif to
her corner (the motif is one melody rotated four ways; only a
player who deals with all four hears it assemble). The loom
plays all four rotations at once, quietly, in tune, which is the
most frightening thing the game does.

## THE PLAYSTYLE

**A hexcrawl at seven nested scales.** The world is one hex at
scale 7. Every hex contains seven hexes — a center and a ring —
down to scale 1, the ground, where boots touch dust.

- **RIDE** moves between the seven hexes of your current cluster
  (center touches all six; ring hexes touch their neighbors).
- **ZOOM IN** drops into the hex under you (scale −1). **ZOOM
  OUT** lifts you to the hex that contains you (+1). Distance is
  vertical: to cross the territory you ride up the scales, over,
  and back down. The address of any place is six digits deep.
  The manual calls this THE WEAVE and never explains further.
- **Terrain is the address.** Dust flats, bone flats, scrub,
  black mesa, salt pan, gallows wood, township — derived from
  where a hex sits in the weave, identically every run. The
  territory is not generated. It is WOVEN, and the loom does not
  change its mind.
- **The drifter carries three things:** GRIT (resolve · hitting
  zero folds the territory back to your porch, which is worse
  than dying), SILVER (blessed rounds and money · the same
  pouch, on purpose) and LORE (witch-knowledge · earned in
  encounters · spent on nothing · REQUIRED for unweaving).
- **Encounters** fire on low-scale riding: text beats in the
  paperback voice — a dry preacher, a salt peddler, bones that
  point wrong, a township that knows your name one hex early.
- **THE FOUR SISTERS** sit at the deep corners: NORTH [1·1·1·1·1·1],
  EAST [2·2·2·2·2·2], SOUTH [4·4·4·4·4·4], WEST [5·5·5·5·5·5] —
  four witches on a six-sided world under an eight-pointed
  compass; nothing agrees, and the disagreement is the weave.
  Each can be dealt with three ways: **PARLEY** (costs
  something she names) · **DRAW** (iron and silver · costs GRIT
  either way) · **UNWEAVE** (requires LORE · unmakes her thread
  without malice · the game's thesis verb).
- **Home** is the dead center, [0·0·0·0·0·0]. Ride home with all
  four sisters unwoven and the center opens into THE LOOM — the
  eighth-point scene, the four unlabeled points, and the one
  question the game asks out loud. Ride home with less and you
  hang up the iron anyway; the territory keeps.

## THE AMBITION

- Give the catalog its RPG pole and its oldest voice: the stick
  that proves "slow" existed before anyone named it — a
  hexcrawl where the crawl IS the contemplation.
- Make the nesting the theme: wyrd means fate means WEAVE; a
  self-similar world is a woven one; the map that repeats is the
  first clue and the last answer.
- Plant the eight-pointed compass in 1983 — the earliest Order
  object in the catalog, two years before Astro-Cortex, never
  commented, never explained by anyone at Sagebrush because
  (canon) the sister painted it from a dream and would not
  discuss it.
- Tokens out: `sisters_wyrd_finished`,
  `wyrd_all_four_unwoven`, `wyrd_eighth_point_seen` (Fey Faire:
  Morgan le Fey's fortune gains one line — she has seen these
  points before, in a desert that was a loom). Tokens in: none.
  It is 1983. Nothing on this shelf is older.

## BUILD

Host + one hexcrawl scene. Address = array of ring digits (0
center, 1–6 ring), scale = 7 − depth. Terrain/encounters
deterministic from an address hash · witch seats + home are
authored overrides. Encounter deck + witches as JSON. New
`sagebrush` look preset (paperback inks). Two compositions (the
territory · the loom) + the SISTERS motif rotated four ways.
Four heroes. The one genuinely new machinery is the nested
navigation, and it is ~60 lines once the address IS the world.
