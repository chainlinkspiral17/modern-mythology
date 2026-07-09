# ESTUARY 2 · DESIGN
### Oneironautics Inc. · 2002 · SIMULATION
### "the summer at the mudflats" · ~6 hours · witnessing as mechanic

Marc Ostrom's only lead credit. Ines Rocha, junior, did the
per-species population math. Sarah Delahaye drew a town's worth
of mud. Shipped in the Betamax case Olaf preferred.

---

## THE LOOK

Top-down walkable soft-sim — the Pirate Summer tile engine,
in-fiction the same 2002 team tech. One place: a tidal mudflat
with a channel, a boardwalk, four house-backs on the bluff, and
the county road where the surveyor's truck will eventually park.

Palette · mudflat neutrals that make small color events loud:

    #5a6058  wet mud        #8a8878  dry flat
    #3a4a52  channel        #a8a290  boardwalk plank
    #708468  pickleweed     #b8b4a4  overcast sky tone (tint layer)
    #d87838  survey stake   (the most saturated color in the game ·
                             appears in week 6 · every reviewer
                             mentioned the stakes)

The player sprite is deliberately generic — a coat and boots, no
face shown; E2 predates the studio naming its protagonists.
Twelve species sprites at two states each (E3 Act 2 icons are
these, canonically, four games on — reuse directly). Weather
tints the whole tile map per week: fog, rare sun, first-storm.

**Layout:** field-journal page as pause screen (the direct
ancestor of Pirate Summer's J-key journal — same ruled layout,
Delahaye's 3×5 headers). The crank radio is a 9-pixel prop on
the boardwalk rail.

**HeroImages:** the hearing room (folding chairs, a county seal)
· the three winter cards (dredged channel / the flat as known /
the half-channel with no comment) · the stakes at dawn.

## THE SOUND

Ostrom leading means the score leads. Twelve short pieces, one
per walk, all variations on one theme that the FIRST walk states
plainly and the last walk finally resolves. The crank radio
speaks the week's weather in formant-synth bursts (the audio
playbook's formant ceiling is canon: it sounds like a radio
doing its best, which is the charm). Weather drives the math;
players learn to hear a bad shrimp week coming in the vowels.

## THE PLAYSTYLE

**Twelve walks, June to September.** Each walk: free-roam the
flat until you choose to go home. Verbs: WALK, LOOK (hold to
observe), CRANK (radio), TALK (four neighbors).

- **Witnessing is mechanical.** LOOK at a species logs an
  observation. Observe the same species three walks running and
  its journal page ILLUMINATES — Delahaye draws it fully, the
  population math becomes visible on the page, and its theme
  stem joins that walk's music. Twelve pages is the collectible;
  nobody needs all twelve; completists learn the flat's whole
  clockwork.
- **Population math** (Ines's sheets): each species has a weekly
  curve driven by weather + tide + one keystone dependency (the
  shrimp feed the sculpin feed the heron; eelgrass shades the
  fry; the player affects NOTHING directly — E2 removes E1's
  lever on purpose, which contemporary reviews found either
  brave or inert).
- **The dredging subplot.** Week 6: orange stakes. The county
  wants the channel dredged for the marina upcoast. Four
  neighbors, each with a walk-in scene per week: RUTH (crabber,
  for it — her boat drafts too deep), COLE (retired county
  engineer, against, embarrassed to say why), MRS. AMES (owns
  the boardwalk, performatively neutral, counting), and JULES —
  early twenties, watching everything, twenty years before the
  Kwik Stop. A petition can be walked door to door. The studio's
  first NPC drama: stiff, earnest, four people deep, and visibly
  the rehearsal for Pirate Summer's fourteen-camper web.
- **The hearing** (week 10): a beat-scene. The player gets one
  statement, assembled from journal pages — the game quietly
  requires that you WITNESSED to have standing. Three endings:
  DREDGED (winter card: straight channel, journal pages fading
  at the edges) · BLOCKED (the flat as you knew it, and Ruth no
  longer waves) · THE COMPROMISE (half-dredge; the card refuses
  judgment; canonically this is Estuary 3's status quo — the
  tide gate downstream of this exact channel).

## THE AMBITION

- State the studio's second thesis: E1 was responsibility;
  E2 is WITNESS — you change nothing and it matters anyway,
  because standing at the hearing is made of looking.
- Be the visible missing link: E1's math + PS's people = E2.
  A player who plays 1→2→3 watches a studio learn.
- Seed Jules, Ruth's boat, and the half-channel into E3's town.
- Tokens out: `estuary_2_finished`, `estuary_2_hearing_<result>`
  (E3 Act 3 mill office references the '02 hearing), twelve
  `e2_journal_<species>` pages (E3 planner acknowledges).

## BUILD

The big reuse project: PS tile engine + walk cycles, E3 Act 2
species JSONs + curves, beat-scene for the hearing, journal from
PS J-panel. Twelve short compositions (theme + variations — one
authored melody, eleven arrangement passes). Schedule after E1
and Northwind Harbor.
