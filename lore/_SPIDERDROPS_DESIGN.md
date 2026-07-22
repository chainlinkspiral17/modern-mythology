# SPIDERDROPS · DESIGN DOC

**Stick #19 · PDP Toys · Beaverton, OR · 1993**
**Genre stamp:** ARCADE / PHYSICS PUZZLE
**Preset:** `pdp_toys` (toy-bright, catalog-clean, `look_mode` 0)
**Status:** BUILT · playable_v1 (2026-07-21)

Read `_SLOWSTOCK_AUTHORING_PLAYBOOK.md` (host/child contract) and
`_SLOWSTICK_AESTHETIC_BIBLE.md` (the pdp_toys preset) before touching
this stick.

---

## The pitch (user, 2026-07-21)

> "spiderdrops, a physics based puzzle platformer about a spider
> protecting its web in a storm, as water droplets pool and get
> bigger and debris blows into it. the spider has to manipulate the
> web and position for survival. maybe the gusts are waves."

A standard game experience — a real-time physics arcade toy — with
the modern-mythology twist buried where PDP's marketing never looked.

## The twist · a high-score toy that is secretly about impermanence

PDP Toys shipped SPIDERDROPS as a cute physics arcade game: keep the
spider's web up in a thunderstorm, chase a survival score. The blister
pack promised "REAL PHYSICS!" and a two-player pass-the-stick mode.

But the storm **always wins eventually.** There is no victory screen
that says you beat the weather. The design — like Estuary 1's "a
screensaver you are responsible for" — has a soul the box copy never
mentions: you are not playing to defeat the storm, you are playing to
decide **what shape the web is in when it goes**, and how long you can
hold it. The score is real; the score is not the point. This is the
RANCH/Oneironautics schism (score vs. responsibility) showing up,
uninvited, inside a Beaverton toy company's arcade cart.

**The Order leak.** An orb-weaver's web is built on eight radial
spokes. The eight-pointed star is the Order's sign (the Basilica
breaker, Sagebrush's compass). SPIDERDROPS never comments on it — but
one ending register is THE EIGHT-POINTED STAR: the capture spiral torn
away, only the eight structural spokes surviving the storm, the web
reduced to the Order's exact figure. PDP is the third publisher the
star has now leaked into, uncommented, the way it always leaks. Nobody
at PDP drew a compass. It is just what an orb web is when the storm
takes everything soft and leaves only the frame.

## Core loop · the verlet web

The web is a live Verlet particle system (see `SpiderdropsWeb.gd` — the
core mechanic earns the one new renderer, per the catalog lesson):

- **Nodes** — a center **hub**, 8 radial **spokes**, 4 concentric
  **rings**; the outermost ring is pinned **anchors** on the storm
  frame (branches at the screen edge). ~33 nodes, ~64 threads.
- **Threads** — springs solved by Jakobsen relaxation. **Spoke**
  threads are the structural radials; **spiral** threads are the soft
  capture web that breaks first. A thread stretched past its break
  ratio SNAPS; a node that loses every thread falls away.
- **Water** — rain pools on nodes and grows; water is mass. Heavy
  nodes sag, and sag is tension, and tension snaps threads. Pooled
  water is the slow killer.
- **Debris** — leaves and twigs blow in on the gusts and stick,
  adding mass + wind drag to whatever they land on.
- **Wind = waves.** The storm arrives in numbered GUSTS. Each gust is
  telegraphed: a lull, a hum, an arrow showing the incoming direction,
  then the gust hits from that direction, then a recovery lull (rain
  keeps pooling in the lull). Gusts escalate wave over wave. Reading
  the telegraph and preparing IS the game — the same telegraph→respond
  idiom the combat sticks graduated to a rule.

### The spider · four verbs

The player IS the spider, sitting on a node, moving along threads:

- **MOVE** (arrows / d-pad) — crawl to a connected node. The spider's
  weight transfers: sitting on a strained node makes it worse; sitting
  on a slack one is free. Position is survival.
- **PLUCK** (Space / A) — shed pooled water from the current node and
  its neighbors, and shake loose stuck debris. The realest verb
  against the slow drowning. Short cooldown.
- **BRACE** (hold Shift / hold RT) — anchor the current node (pins it)
  and stiffen its threads against the incoming gust. This is the
  DEFEND analog: brace the RIGHT node during the telegraphed gust and
  you save the most threads. Drains **stamina**; stamina refills in the
  lulls.
- **SPIN / repair** (S / X) — re-spin a snapped thread back onto the
  current node, or reinforce toward a nearby node. Costs **silk**; silk
  regenerates slowly. The only way to rebuild what the storm takes.

Two resources make the verbs a budget, not a mash: **silk** (repair)
and **stamina** (brace). Neither refills fast enough to do everything
every wave — you triage.

## Win / loss · the register, not a trophy

Survive all six gusts and the run resolves by the web's final SHAPE
(the Tideline-register pattern — the ending emerges from how you
allocated, not from a win flag):

| register | condition | reads as |
|---|---|---|
| **THE WEB HELD** | 7–8 spokes, spiral ≥ 60% | you kept it whole |
| **HELD** | survived, in between | tattered but standing |
| **THE EIGHT-POINTED STAR** | 7–8 spokes, spiral ≤ 20% | only the frame endured — the Order's figure, uncommented |
| **THE STORM** | hub lost or ≤ 2 spokes before the end | the honest ending — the storm was always going to win |

The storm always escalates; THE STORM is not a failure the game scolds
you for — it is the thesis stated plainly.

## Lore tokens

Emit-and-note now (readers-vs-writers: emit even without a consumer):

- `spiderdrops_finished` — always, on any completed run.
- `spiderdrops_whole` — THE WEB HELD.
- `spiderdrops_star` — THE EIGHT-POINTED STAR. **Joins the Order
  thread** (eight-pointed star across publishers); a future
  consumer (Basilica / Sisters Wyrd / an Almanac Order entry) can gate
  on it.
- `spiderdrops_storm` — THE STORM.

`canon_vars.spiderdrops_result` = the register string.

## Provenance (Olaf's note)

A mall blister-pack PDP cart, common and cheap — the kind that came
two-to-a-clamshell. Olaf's note:

> "A dollar in a bin at the Beaverton Fred Meyer. It is a toy. I have
> never once kept the web up to the end. I do not think you are
> supposed to."

## Canon lattice fit

- **Studio:** PDP Toys, Beaverton (already canon — made the Riffmaster
  kids' synth; the other PDP cart on the shelf). Uncredited R&D design,
  the way Ostrom moonlighted on the Riffmaster.
- **Year:** 1993 (Riffmaster 1991; PDP's physics-toy phase after).
- **Unlock:** surfaces once Tem has finished RIFFMASTER MELODY CLUB —
  "once you know PDP Toys made real games, the other PDP cart shows
  up." (Mirrors hane_no_niwa←fey_faire, patient_mister_glass←sams.)
- **Shelf slot:** shelf 0, slot 11.

## Build notes

- One host + one live core scene. The web sim is the catalog's one new
  renderer this build (Verlet + `_draw`); everything else is the
  standard host contract and data.
- Real-time, one-sitting (~5–8 min a storm), like Sweetgum — no
  mid-run save; the save holds best register + run count only.
- `pdp_toys` preset, `look_mode` 0 (clean/toy-bright). Font floor 12.
- Follow-ups (not in v1): BGM (a PDP arcade loop + storm bed) and SFX
  (thread pluck, snap, rain, gust) — author per the audio playbook
  before wiring; do not fake it.

## FOLLOW-UPS / BACKLOG

- DONE (2026-07-22): Audio — storm BGM (`bgm/spiderdrops/storm.wav`)
  + 5 SFX (pluck/snap/spin/gust/step, `sfx/sd/`), wired in SFXBank
  with rumble; Python + importer.html parity.
- DONE (2026-07-22): Hero art — title + 4 ending registers
  (whole/held/star/storm) + shelf spine; ending screen shows the
  register's hero.
- DONE (2026-07-22): Sequel PLAN — `_SPIDERDROPS_2_DESIGN.md`
  (THE LONG WIND, post-game, carries the register in).
- Two-player pass-the-stick mode (the box promised it) — a Manager/
  Counselor-style flag on the host, alternating storms, best-of.
- Deck-verify: physics stability at 60fps on the Deck, verb feel,
  telegraph readability, break-ratio + rain-rate tuning; audio mix +
  rumble feel; hero legibility over the ending text.
- DONE (2026-07-22): the sequel is BUILT — SPIDERDROPS 2 · THE LONG
  WIND (#20, `_SPIDERDROPS_2_DESIGN.md`). Post-game, carries the
  register in.
