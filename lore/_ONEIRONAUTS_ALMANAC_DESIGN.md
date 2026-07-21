# THE ONEIRONAUT'S ALMANAC · DESIGN
### the meta-layer that makes four pillars one work
### STATUS: BUILT · playable_v1 (2026-07-20)
### Reachable from Main Menu → "THE ALMANAC". Steps 1-4 of the build
### order below are done (AlmanacState + data + reader UI + menu entry).
### Step 5 (evaluate_unlocks wired into MainMenu + gauntlet + CP + slowstick boots · DONE) done; step 6
### (campaign + shelf pour content) are the remaining spokes.

User ask (2026-07-20): "new design to enhance the full package, from
visual novel to arcana games to community planned to slowsticks."
Chosen directions: **the Almanac** (this doc · the hub), the Major
Arcana campaign, and the slowstick collector's shelf. This doc is the
foundation the other two plug into.

## THE PROBLEM IT SOLVES

Four finished pillars — the Vol 5-6 VN, the TAROT GAUNTLET (22
arcana), Community Planned (grand-strategy inset), and the 18-stick
slowstock shelf — share a real spine: 13 autoloads + a flat
cross-pillar token store (`OneironauticsTokens`, ~40 files) and
`GauntletState` canon vars. But the connective tissue is lopsided:
slowstick↔slowstick and slowstick↔Fey-Faire are richly cross-wired;
the three BIG surfaces (VN, gauntlet, CP) barely acknowledge each
other. The package reads as an anthology, not one dream. The premise
is literally "the walls are thin here" — the Almanac makes that
STRUCTURAL, not just flavor.

## WHAT IT IS

A single top-level compendium — the pattern Fey Faire's Compendium
and Earthman's Codex already prove, lifted to wrap EVERYTHING. Reached
from the Main Menu ("THE ALMANAC"). Two jobs:

### 1 · THE LEDGER · one place that remembers everything you've dreamed

Aggregates discovery across all four pillars into named chapters, read
from data already written today (no new save format):

- **THE READING (VN)** — Vol 5-6 chapters reached / arcana drawn.
  Source: SaveSystem VN progress + the chapter→arcana map.
- **THE GAUNTLET** — arcana won/lost, by location, with the spread.
  Source: `GauntletState.state` (record_win/record_loss, total_wins,
  is_arcana_completed).
- **THE COUNTY (Community Planned)** — regions cleared, endings,
  Dean's Ledger entries. Source: CP save + canon vars.
- **THE SHELF (slowsticks)** — sticks played, endings seen, per-stick
  tokens. Source: the manifests + OneironauticsTokens by prefix.
- **THREADS** — the cross-Oneironautics chains that already fire
  (1976 incident, the Rocha melodies, Nika Voss, "for jack") shown as
  connective lines BETWEEN chapters, so the player SEES the weave.

Implementation: the Almanac owns one data file,
`resources/almanac/almanac.json` — a list of ENTRIES, each:
`{id, chapter, title, blurb, requires: [tokens/canon predicates]}`.
An entry renders lit when its `requires` are met (same "authored art
wins / else placeholder" discipline as the compendiums). The token
namespace is already prefix-organized (ksm_, fey_faire_, basilica_,
ps_, em_, estuary_1_ …) — chapters group by prefix + explicit map.

### 2 · CROSS-PILLAR UNLOCKS · the walls go thin

A small, data-driven rules table — `almanac_unlocks.json` — of the
form `{when: [token/canon predicate...], grant: <effect>}`. Evaluated
on Almanac open AND on each pillar's boot (cheap). Effects are
deliberately light-touch, always ADDITIVE (never gate base content):

- A GAUNTLET outcome seeds a CP starting condition
  (GauntletState already has `record_cp_scenario_unlock` — extend the
  idea: a won arcana drops an intel token CP reads at setup).
- A SLOWSTICK ending drops a clue token the VN's later chapters can
  surface as an optional aside (VN reads OneironauticsTokens.has()).
- A VN chapter read reveals a gauntlet visitor's extra line / a
  shelf cartridge's liner note.
- Completing an Almanac CHAPTER (all its entries lit) grants a
  cosmetic + a token other pillars can honor.

The contract is one-directional and idempotent: pillars WRITE tokens
as they already do; the Almanac and other pillars only READ. No pillar
depends on another being played — everything is a bonus that lights up
if you've been there.

## WHY THIS IS THE HUB

The Major Arcana campaign writes campaign-progress tokens the Almanac
surfaces as THE GAUNTLET chapter's spine; the collector's shelf IS the
Almanac's THE SHELF chapter deepened with the catalog lattice. Build
the Almanac's data contract first and the other two become content
poured into it, not new plumbing.

## BUILD ORDER

1. `AlmanacState` autoload (or static, like OneironauticsTokens):
   thin readers over the existing stores — `entry_is_lit(entry)`,
   `chapter_progress(chapter)`, `evaluate_unlocks()`.
2. `almanac.json` (entries) + `almanac_unlocks.json` (rules), seeded
   from the tokens/canon that ALREADY fire today (so it lights up on
   an existing save).
3. `Almanac.tscn/.gd` — the reader UI (chapter tabs → entry list →
   entry detail + THREADS view). F4-compliant, controller-nav,
   StickTheme chrome.
4. Main Menu entry.
5. Wire `evaluate_unlocks()` into each pillar's boot (one call).
6. Then: the campaign + shelf pour their content into chapters 2 & 4.

## HONEST CONSTRAINTS

- Read-only over existing data — no retro-active save migration.
- Cross-pillar effects are ADDITIVE only; a fresh player who touches
  one pillar never hits a wall referencing another.
- No new art pipeline — procedural placeholder tiles + the existing
  HeroImage/bust systems, per house rules.

## The Evidence Board (2026-07-20)

The Almanac's `almanac_unlocks.json` already assembles cross-stick
threads PASSIVELY — on Almanac-open, any rule whose two secret-tokens
both hold grants a thread token. The Evidence Board adds the
INTERACTIVE half of the same idea: the deduction VERB the meta-layer
lacked. The collector pins two DISCOVERED stick-secrets and holds them
against each other; if they form an authored connection, a thread
assembles. Modeled on the Patient Mister Glass contradiction ledger
(pin two answers to make a finding) — the deepest verb in the catalog,
promoted to the shelf level.

- Data: `godot/resources/almanac/evidence_board.json` — `secrets[]`
  (each a stick-secret keyed to its OneironauticsTokens flag) and
  `connections[]` (each a `pair` of two secret tokens + `fires` token
  + assembling text).
- UI: `godot/scenes/menu/EvidenceBoard.gd`, Almanac overlay pattern
  (static build, "ui" group, Esc close). Entry: MainMenu "THE EVIDENCE
  BOARD". Only DISCOVERED secrets show; undiscovered are a count, never
  a spoiler. Revealed connections persist via their `fires` token and
  light a matching THREADS entry in the Almanac.
- Canon rule (hard): connections ASSEMBLE, never RESOLVE. Each text
  NAMES the shared element (a year, a shape, a hand, a note) and the
  resonance, and stops. 1976 stays open; the eight-pointed star stays a
  shape; 'for jack' stays two words. The board proves the walls are
  thin; it never tells you what is on the other side.
- Distinct from the passive rules: the board's four connections use
  their own `evidence_*_assembled` tokens, so it never double-fires the
  automatic thread grants. Both systems can coexist on the same secret
  tokens.
