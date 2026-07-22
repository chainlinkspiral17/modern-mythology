# SPIDERDROPS 2 · THE LONG WIND · DESIGN DOC (PLAN)

**Proposed stick #20 · PDP Toys · Beaverton, OR · 1995**
**Genre stamp:** ARCADE / PHYSICS · **Subtitle:** "let go"
**Preset:** `pdp_toys` (`look_mode` 0, toy-bright)
**Status:** PLANNED · post-game sequel to Spiderdrops (#19). Not built.

Companion to `_SPIDERDROPS_DESIGN.md`. Read that first — this reuses
its Verlet engine and inverts its thesis.

---

## The ask (user, 2026-07-22)

> "plan for a post-game sequel as well."

A sequel to Spiderdrops, unlocked after you finish the first, that
carries your ending in and takes the idea somewhere new.

## The one-line pivot · from HOLD ON to LET GO

Spiderdrops is about **holding your ground**: the storm always wins,
and the game grades the shape of the web when it goes. It is a game
about impermanence that only ever lets you lose slowly and well.

THE LONG WIND is the other half of that idea. The storm is over. The
web cannot be held forever — so the spider **lets go on purpose** and
travels: it casts a thread into the wind and *balloons*, riding the
exact gusts that tore the old web apart, across the gaps, to a new
anchor, to build again. **The thing that destroyed you in game 1 is
the thing that carries you in game 2.** Grief becomes motion. The toy
box calls it "NOW YOU FLY!"; the design calls it moving on.

This is the same trick the catalog loves — Estuary 1's "responsible
without being told," Tideline's register, KSM's evicted axis — a bright
arcade surface over a true feeling underneath.

## Core loop · balloon → settle, leg after leg

A journey of N legs (say 7), each leg two phases:

### 1 · BALLOON (the new verb)
The spider releases silk into the wind and is lifted. This reuses the
gust-reading skill from game 1 — **the wind still arrives in
telegraphed waves**, but now you WANT the gust:

- Read the incoming gust (direction + strength arrow, same telegraph).
- **Cast** at the right moment and angle to catch it (a timing +
  aim input, not a mash).
- **Glide**: a light single-mass physics mode — the spider hangs from
  a silk line the wind drags, you pay out or reel in silk to rise/fall
  and steer, dodging blown debris and dense rain columns.
- **Land** on a far anchor (a branch, a wire, a fencepost). Miss, and
  you pay silk and drift back to the last anchor (no death spiral —
  the cost is silk and time, the realest currencies, per the loop).

### 2 · SETTLE (the reused engine)
On landing you spin a small resting web to refuel silk and steady
yourself before the next gust — a compressed version of the game-1
Verlet web (fewer nodes, no storm to survive, just enough to rest).
The old engine becomes the "campfire between crossings."

Two budgets return, re-roled: **silk** (spent to cast/steer, refilled
by settling) and **stamina** (spent to hold a hard glide against a
cross-gust). You triage across the whole journey, not one storm.

## Carries the register IN (the "ending as opening" rule)

Your Spiderdrops result (`canon_vars.spiderdrops_result`, read from
GauntletState) sets your starting condition — a sequel's best opening
is the previous ending, stated in mechanics the player already reads:

| game-1 register | game-2 opening |
|---|---|
| **WHOLE** (`spiderdrops_whole`) | full silk — you left on your own terms, well-provisioned |
| **HELD** | most of your silk — a little worn |
| **THE EIGHT-POINTED STAR** (`spiderdrops_star`) | you carry the star as a keepsake emblem; unlocks the true ending gate (see below) — the Order thread pays off |
| **THE STORM** (`spiderdrops_storm`) | almost no silk — the storm took everything; you leave with nothing but yourself. The hardest, most honest start. |

No save-format change: read the token/canon that already fires.

## Endings · arrival, the note game 1 refused

Where game 1 only ever ended in loss-shaped registers, game 2 lets you
**arrive** — its counter-thesis. Resolve by where the last leg lands:

- **A NEW TREE** — you crossed, you built again. The plain good ending:
  you can always move on.
- **STILL FLYING** — out of silk mid-journey, carried wherever the wind
  goes now. Not a loss — a different peace (you stopped steering).
- **UNDER THE EAVES** (true ending, gated on carrying `spiderdrops_star`
  in) — the last gust sets the spider down in the corner of a cabin by
  the water, out of the weather at last. Uncommented, it is *this*
  cabin — Olaf's, where the shelf is. The Order's figure rode the wind
  home. A frame-story tie the toy never admits to. Emits
  `spiderdrops_the_eaves`.

Tokens: `spiderdrops_2_finished` always; `spiderdrops_2_arrived`
(A NEW TREE), `spiderdrops_the_eaves` (true ending — a candidate
consumer for a Vol-7 cabin beat or an Almanac Order entry).

## Canon lattice fit

- **Studio/year:** PDP Toys, Beaverton, 1995 — two years after the
  first, PDP's "make the sequel brighter" instinct hiding a sadder
  game (uncredited R&D again).
- **Unlock:** post-game — a new `unlock_graph` wave
  `unlocked_by_any_of: [spiderdrops]`, OR shelf `hidden_until_token:
  spiderdrops_finished` so the slot literally doesn't exist until you
  finish the first. (Prefer the token-hide: "you cannot own the sequel
  before you finish the original," the Sweetgum pattern.)
- **Shelf slot:** beside Spiderdrops (shelf 0, slot 15 — the last
  open slot on the top shelf).
- **Provenance (Olaf):** same bargain bin, a year on. Draft note:
  *"The sequel to the spider game. This one you can win. I did not
  believe it the first time it happened."*

## Build notes (when built)

- **Reuse the Verlet engine for SETTLE**; author one new light physics
  mode for BALLOON (single mass + a wind-dragged silk line + steer by
  paying out/reeling silk). The gust/telegraph/wave system ports
  wholesale from `SpiderdropsWeb.gd`.
- Host is the Spiderdrops host shape (title/run/ending-register), plus
  a boot-time read of `spiderdrops_result` to set starting silk.
- Audio: reuse `wind_gust`/`thread_spin`/`thread_pluck`; add
  `silk_cast` (the balloon release) and a lighter, hopeful BGM
  variant of `storm.wav` (same key, wind turned tailwind).
- Art: title + 3 ending registers (a new tree / still flying / under
  the eaves) via HeroImage, same palette.
- Deck-verify: the glide feel is the whole game — cast timing, steer
  responsiveness, gust-catch window. Ship reasonable constants, tune
  on hardware.

## Why this is the right sequel

It is not "Spiderdrops but harder." It **completes** the first game's
statement: game 1 says nothing holds; game 2 says so you move, and the
wind that broke you carries you, and sometimes you get somewhere. Held
together, the two are one small myth about loss and going on — which
is the whole shelf's subject, sold in a blister pack.
