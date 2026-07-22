# SALMONBERRY · DESIGN DOC

**Stick #21 · Oneironautics Inc. · Portland, OR · 2006**
**Genre stamp:** RPG / ADVENTURE · **Subtitle:** a year on the coast
**Preset:** `oneironautics` (field-guide gouache, `look_mode` 1)
**Status:** BUILT · playable_v1 (2026-07-22) — host + the year loop.
Full town overworld + the central arc are waved (see BUILD).

Read `_SLOWSTOCK_AUTHORING_PLAYBOOK.md`, `_SLOWSTICK_AESTHETIC_BIBLE.md`,
and `_SLOWSTICK_CATALOG_ROADMAP.md` (the canon lattice) before touching.

---

## The ask (user, 2026-07-22)

> "a slowstick game that's part adventure part rpg about living in a
> small rural coastal Oregon town in the 1960s."

## The pitch

The studio's most personal and most ambitious game: a year in the life
of a kid in the fictional cannery town of **Salmonberry, on the mid
Oregon coast, 1963–1964.** Part adventure (a walkable town, people with
stories, a mystery that runs the length of the year), part RPG (you
grow not by fighting but by LIVING — the aptitudes of a coastal life,
a web of bonds with the townsfolk, a naturalist's journal of the
coast). No combat. The stat that matters most is how well the town
knows you by June.

It is Oneironautics doing what Oneironautics does — the Oregon coast,
the tide, memory, a way of life ending — at full length for once.

## The frame · a year between two waves

The school year runs September 1963 to June 1964 (ten monthly chapters).
It is framed, without sensation, by the two events everyone from that
coast remembers:

- **November 22, 1963** — the Kennedy assassination. The distant world
  reaching a small town by radio; the cannery line goes quiet for an
  afternoon. A national "where were you," felt sideways.
- **March 27–28, 1964** — the Good Friday earthquake and the tsunami
  that ran the Oregon coast. The physical crisis the whole year has
  been quietly preparing you for: the night the water comes up the
  river, and what you have built — bonds, aptitudes, knowing the
  tide — is what lets you help save what can be saved.

Both are handled with the studio's restraint (the way Sweetgum handles
1976): felt through the town, never exploited. The year is warm and
small; the two events are the weather that passes through it.

## You

A grandchild sent to live with your **grandmother** in Salmonberry for
the year (a parent working away / recovering — kept vague, the classic
setup). The outsider's eye is the adventure engine: you arrive knowing
no one and spend the year becoming someone the town knows. Home base is
the grandmother's house at the edge of town, by the river mouth.

**The quiet meta-hook (mostly uncommented in-game):** the grandmother
sings. Her songs are the Portuguese folk melodies that thread the
entire catalog — Fey Faire's music box, Wilson's shanty, the Estuary
scores. Salmonberry is where those melodies were first heard; this is
the studio (Amélie Rocha's studio) making a game about the town those
songs came from. The catalog's whole soundtrack has a childhood, and
this is it. Stated only in the provenance + the true ending.

## Part RPG · you grow by living

**Six aptitudes**, raised by doing, never by fighting:

- **HANDS** — mending nets, fixing, the cannery line, carpentry.
- **SEA** — boats, tides, weather-sense, the bar, the bay.
- **WORD** — reading, letters, school, the library, the radio.
- **HEART** — talking, listening, earning trust.
- **WILD** — the woods, foraging, birds, the estuary edge.
- **GRIT** — cold, early mornings, hard work, staying with it.

**Bonds** — a relationship web of townsfolk (the Pirate Summer camper
web, aged up and slowed down). Each NPC has a bond level; deepening it
opens their stories, their help, and season-gated errands. The
grandmother is the deepest bond and the game's spine.

**A light economy** — chores and seasonal jobs earn a little money
(berry-picking in June, clamming on the minus tides, the cannery line
in the run, deliveries) and raise aptitudes. Money buys small things:
a library card, boots, a birthday gift, a bus ticket home.

**The journal** — a naturalist's "book of the coast" (birds, tides,
plants, weather signs, the town's own lore) is the collectible, the
direct descendant of Estuary 2's field journal and Estuary 1's report
card: the game grades the COAST you noticed, not you.

## Part adventure · the town and the thread

- **The town** (waved): a walkable Salmonberry — the harbor and the
  cannery, Main Street (store, café, library, church), the school, the
  grandmother's house at the river mouth, the beach, the north bluff,
  the woods and the estuary edge, the jetty and the bar. Reuses the
  Pirate Summer / Estuary 2 tile engine and walk cycles.
- **The through-thread** (waved): a mystery that runs the year — the
  boat that went out in the fall and did not come back, whose loss the
  town does not talk about, and which the grandmother knows more about
  than she says. Following it deepens specific bonds and the journal,
  and it resolves the same Good Friday night the water comes.
- **Seeds toward 1976** (the catalog's braided thread): a traveling
  show passes through in the summer of '64 — small, harmless, a Ferris
  wheel on the cannery lot — twelve years before the Faire that took
  Amélie's sister. Uncommented. `salmonberry_faire_seen`.

## Structure · ten months

Each month is a chapter: a **month card** (the month, a seasonal line,
and for November and March the real-history beat), then free choice —
pick an **activity** from the season's pool (work / explore / visit
someone / follow the thread). The choice passes the month; aptitudes,
bonds, money, and the journal move; a short outcome line lands. Some
activities gate on aptitude / bond / season / money.

This is the Estuary-1 "one meaningful choice per turn" loop grown a
second and third axis (bonds + journal), data-driven so the town can
expand without engine work. v1 ships this loop end to end; the waved
overworld later becomes the "explore" activities' destination.

## Endings · the register (who the town knows in June)

Resolved from how you spent the year (the Tideline-register pattern —
the ending emerges from your allocation, no win flag):

| register | condition | reads as |
|---|---|---|
| **THE HANDS** | high HANDS/SEA/GRIT + strong town bonds | you became useful; you belong here now |
| **THE LISTENER** | high HEART/WORD + deep bonds | you learned the town's stories; you are its memory |
| **THE KEEPER** | the journal near full | you noticed the coast; you kept it |
| **THE LEAVER** | thin bonds | you did your year and go home, changed but apart |
| **THE SONG** (true) | grandmother bond full + all her songs heard | you carry the melodies out; the catalog's whole soundtrack begins here |

Tokens: `salmonberry_finished` always; `salmonberry_hands` /
`salmonberry_listener` / `salmonberry_keeper` / `salmonberry_the_song`;
`salmonberry_faire_seen` (the 1976 seed); `salmonberry_the_wave`
(helped the night the water came). `canon_vars.salmonberry_result`.

## Canon lattice fit

- **Studio/year:** Oneironautics, 2006 — after Estuary 4 (2005), the
  studio's late-career magnum opus. **Amélie Rocha's story** (her
  grandmother's town), **Ines Rocha's build** — the two Rochas' one
  full collaboration.
- **Setting era:** 1963–64 — earlier than any studio; this is a period
  piece, a memory reconstructed, not a contemporary game.
- **Coast geography:** the same fictional mid/south Oregon coast as
  Northwind Harbor (the harbor town, up the coast) and the Estuary
  games' estuary (downriver). Salmonberry can name the harbor town and
  the county seat in passing; do not contradict Northwind Harbor's
  established details.
- **Music:** the grandmother's melodies ARE the catalog's recurring
  Portuguese folk themes (canonized as Amélie's grandmother's in the
  roadmap). This game is their origin.
- **Unlock:** a late capstone — `unlocked_by_count_of_finished_min: 4`
  (surfaces once the player is invested in the shelf).
- **Shelf slot:** shelf 1, slot 7.
- **Provenance (Olaf):** *"Ines gave me this one herself. She said it
  was the only one that was true. I did not ask true about what."*

## BUILD

- **v1 (BUILT 2026-07-22):** host (contract, save, title, ending
  register) + `SalmonberryYear` data-driven month loop (aptitudes,
  bonds, money, journal, the Nov + Mar beats, five-register ending) +
  `activities.json` + `npcs.json`. The smallest complete version of the
  whole idea (the Estuary-1 discipline).
- **Wave A · the town overworld** — the walkable Salmonberry (PS/E2
  tile engine); "explore" activities open real locations with people to
  find and listen to.
- **Wave B · the boat that didn't come back** — the year-long mystery
  as a bond-gated thread resolving Good Friday night.
- **Wave C · the wave** — the March '64 tsunami as a real, playable
  crisis: what you saved is what you'd built.
- **Wave D · deepen the roster** — the full townsfolk cast, seasonal
  errands, the summer show ('76 seed).
- **Wave E · audio + art (DONE 2026-07-22, core):** the year bed
  `coast.wav` IS the Rocha melody quoted from `hnn_one_melody` at its
  source; `harbor_bell` SFX for Good Friday; ambient one-shots wired
  into the loop (gull/surf/cannery/cafe/page/season); hero images
  (title + the five ending registers) + shelf spine. Remaining
  (optional): per-season BGM variants and standalone ambient loops.
- **Deck-verify:** loop pacing, aptitude/bond tuning, register
  thresholds, the tone of the two real events.

## Why it belongs

Every Oneironautics game is a piece of this one: Estuary is its tide,
Northwind its harbor, the Tideline its coast, the recurring melody its
grandmother. SALMONBERRY is the studio finally making the whole thing —
the town those games all remember, in the year it was still itself,
before the wave and the highway and everything after. Their magnum
opus, and, quietly, an origin story for the catalog's own soul.
