# NARRATIVE STRUCTURE COMPASS

A unifying meta-system named in-fiction across multiple cards:

- **Fool**: header banner — `WELCOME TO RUST_CODE.BBS / GRAUSTARK_FRONTIER / ACTIVE NODES: 64`
- **High Priestess**: badge — `MODERN MYTHOLOGY · NARRATIVE STRUCTURE COMPASS (HIGH PRIESTESS Node)`
- **Fool**: console UI hints — `NOTEBOOK / INVENTORY / RESTART / weapon / shield`

The two names — RUST_CODE.BBS and NARRATIVE STRUCTURE COMPASS — refer
to the same layer. The BBS is the network metaphor; the COMPASS is the
navigation metaphor. They're the IN-FICTION names for what is, externally,
the project's chapter graph + arcana map.

## Concept

A radial graph view, navigable from the gallery, that shows:

- **Nodes** — every arcana the player has unlocked, painted as their
  card art at thumbnail resolution
- **Locked nodes** — present as silhouettes; reveal as the player
  encounters the arcana
- **Edges** — the `cross_references` graph from `puzzle_hooks/*.json`:
  - emperor ↔ empress (shared ram throne)
  - emperor ↔ magician (red steamboat foreshadowing)
  - empress ↔ aria-via-data-overlay (BIOMETRICS readouts on multiple cards)
  - magician ↔ priestess (infinity sigil / occult symbology shelf)
  - priestess ↔ fool (PRECIPICE DOOR label II; archive of the Fool's leap)
  - fool ↔ emperor (DEMOSCENE_VIBE.EXE label IV)
  - fool ↔ all (RUST_CODE.BBS = the whole compass)
- **Ring layout** — Major Arcana in the 22-position wheel (0 at top,
  clockwise to XXI). Chapter associations annotate the outer ring.
- **Center** — the COMPASS rose itself, animated from the Priestess
  card's badge graphic

## Player Affordances

- Click any unlocked node → opens its gallery card full-screen
- Click any edge → highlights the cipher / cross_reference that
  established it
- Toggle filters: **by-chapter**, **by-character**, **by-cipher-kind**
  (sigil / labeled_artifact / meta_inline / etc.)
- "Find link" mode: select two cards, the compass animates the shortest
  cross_reference path between them (lore-graph traversal)
- Lock-state legend in the corner

## Unlock Path

The compass itself is locked until:

```
vol5_meta_compass_unlocked = TRUE
```

which fires when the player either:

- Clicks the COMPASS badge on the High Priestess card (`pri_compass_badge`
  hotspot), OR
- Encounters the RUST_CODE.BBS header three times across different cards
  (`vol5_rust_code_bbs_known` accumulator)

## Implementation surface

- New composition / overlay type: `narrative_structure_compass`
  - Registered in `_index.json` with `type: "overlay"` (same new type
    introduced for tarot_synth)
- New scene: `godot/scenes/menu/CompassOverlay.gd`
  - Reads all `resources/puzzle_hooks/*.json` at open time
  - Builds the node + edge graph from `cross_references` fields
  - Layouts nodes on a radial wheel (22-position major arcana order)
  - Renders edges as glyph traces between nodes (using the ASCII wall
    aesthetic — text-as-line)
  - Color codes edges by `cipher_kind`
- New gallery index entry, gated on `vol5_meta_compass_unlocked`

## Data prerequisites already in place

- `puzzle_hooks/_README.md` schema
- Six cards seeded so far: emperor, empress, magician, high_priestess,
  fool, portrait_dante, portrait_nicola (+ frasier_face, elicia_face
  via cropping)
- Each card declares `cross_references` and `links_forward` — the graph
  is buildable from these today
- The compass overlay just renders what's already in JSON

## Open design questions for the next pass

- **Should the COMPASS be diegetic?** I.e., does Elicia have a literal
  printed compass in her bungalow that the player can examine in
  vol5_ch2 scenes, OR is it a player-only system view?
  → Recommendation: BOTH. The badge in her card is the diegetic prop.
     Clicking it opens the player-only system view but the in-fiction
     framing is "Elicia has been mapping this all along."
- **What about minor arcana, court cards?** The visible cards in
  Priestess's deck on the desk could be a separate "deck inventory"
  alongside the major arcana wheel.
- **Edge styling per cipher_kind?**
  - `sigil` → solid gold rule
  - `cross_card_link` → animated dotted stream
  - `meta_inline` → cyan w/ glitch
  - `recursive_artifact` → fractal repeating mini-card pattern
  - `system_banner` → text-line "ASCII wall" rendering
- **Compass as a synth-piece input?** Cards laid out on the wheel
  could be playable like the tarot_synth — strumming a chord around
  the wheel triggers note sequences. Would unify the two
  gallery-overlay pieces.

## Concept art tie-ins (per user)

The user noted they have been "toying with the COMPASS in a lot of
concept art." Next pass: bring those concepts in. Ideal drops:

- Visual reference of the compass rose itself (helps lock the layout)
- Any per-arcana node art (small icons specifically intended for the
  compass)
- Diegetic compass appearances in scenes (e.g., a tattoo, a ceiling
  fresco at the church in vol5_ch5_hierophant)
