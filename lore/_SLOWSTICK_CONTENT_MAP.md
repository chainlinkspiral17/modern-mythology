# SLOWSTICK CONTENT MAP

Measured 2026-08-01 (`gd` = script files · `gdloc` = script lines ·
`jsonKB` = authored data). This is the living answer to "let's get
them all well made" — re-measure and update when a wave ships.

## THE BAR · what "well made" means here

A stick is DONE when it clears all six. Anything less is a wave.

1. **DEPTH FLOOR** (playbook rule) — 3 interlocking systems, ≥30
   decisions/run, visible checks, expiring scarcity, a build,
   textured failure.
2. **THE LOOP** (playbook rule) — loadout.json + earn/spend/carry
   wired; ≥1 flag per tier.
3. **FLAVOR DENSITY** — no reused line where the player will see the
   reuse. Rule of thumb: any beat hit ≥3 times/run needs ≥3 variants;
   any calendar unit (week/night/day) needs its own line.
4. **PRESENTATION** — SlowstickLook preset, per-studio chrome,
   authored hero art at the title + endings, readable palette
   (contrast ≥4.5:1 body text — measured, not eyeballed).
5. **LEGIBLE CHALLENGE** — where the player chooses to engage,
   the cost/risk is shown RELATIVE to their current strength
   (Fey Faire's five-pip read is the reference).
6. **MANUAL** — in `resources/manuals/`, reachable from the shelf.

## The measured table

| stick | gdloc | jsonKB | loop | verdict |
|---|---|---|---|---|
| fey_faire | 9470 | 457K | ✓ | **A** · Wave 3 shipped: loop wired |
| estuary_3 | 7823 | 212K | ✓ | **A** · Wave 3 shipped: loop wired |
| earthman_chronicles | 6302 | 311K | ✓ | **A** · Wave 3 shipped: loop wired |
| pirate_summer | 4689 | 1346K | ✓ | **A** · Wave 3 shipped: loop wired |
| sisters_wyrd | 2388 | 83K | ✓ | **B+** · loop reference · more encounters |
| salmonberry | 2118 | 58K | — | **B** · Wave 1 shipped: 40 week lines, 18×4 outcome variants, town life (presence/overheard/moments) |
| spiderdrops | 1372 | 31K | — | **B** · feel-complete · loop only |
| northwind_harbor | 1137 | 75K | — | **B** · data-rich · loop only |
| sams_summer_shifts | 994 | 6K | — | **C** · 6K data = thin runs |
| basilica_of_wires | 966 | 28K | ✓ | **B−** · Wave 2 shipped: 20 finds, 6 floor residents, WIRE loop + 7-item toolbelt |
| estuary_1 | 951 | 15K | — | **C+** · by-design austere |
| patient_mister_glass | 921 | 30K | — | **B−** |
| estuary_2 | 919 | 29K | — | **B−** |
| spiderdrops_2 | 904 | 20K | — | **B−** |
| hane_no_niwa | 874 | 26K | — | **B−** |
| mrs_wus_garden | 850 | 25K | — | **B−** |
| riffrocker_melody_club | 848 | 36K | — | **B−** |
| kwik_stop_manager | 789 | 21K | — | **B−** · Wave 4a: 16-incident weekly pool, seeded per summer |
| the_tideline | 731 | 30K | — | **B−** |
| estuary_4 | 713 | 14K | — | **B−** · re-verdict: working-season variety is SYSTEMIC (seeded tides + budget/morale), not data-thin |
| sweetgum | 678 | 14K | — | **B−** · Wave 4a: 3 micro-events/watch (18-pool), palimpsest 6→11 years |
| tideline_survey_2048 | (shares tideline) | 2K | — | **C** · no manual entry of its own (by design: tideline's covers it) |

Verdicts: **A** = clears depth, needs loop/flavor polish only.
**B** = solid run, one bar missing. **C** = playable but thin —
data volume can't sustain a second run. **D** = structurally empty.

## Build order · the waves

Sequenced by (user-reported pain) > (structural emptiness) >
(breadth). One wave = one commit arc, playbook lesson at the end.

### Wave 1 · SALMONBERRY ALIVE (user-reported twice)
"salmonberry is lifeless. add flavor text for every week, and every
choice." + "walking around versus picking from a list is
superficial." These are ONE fix, not two:
- `week_flavor.json` — 40 weeks × (town line + weather rider).
- Activity outcomes: per-season variants + rough/strong tier lines
  (engine: outcome selection in SalmonberryYear already tiers).
- **The town must do what a list cannot**: people physically AT
  places by month/weather (and absent elsewhere — presence is
  information), overheard lines in transit, route-only encounters,
  per-place state that changes week to week. Flavor text then
  describes a living place instead of decorating a menu.
- Loadout: currency = KEEPSAKES; flags open town routes/verbs.

### Wave 2 · BASILICA OF WIRES · fill the cathedral (user-flagged)
"basilica of wires is still just one short thing?" Correct: 10 grids,
5 props. The SUBFLOOR structure is good; the floors are vacant.
- Per-floor set pieces (3-5 each): stations, shrines, switching
  rooms, the choir's members.
- A denizen table + hazard verbs per floor (the flooded cavity
  should play differently from the catwalks).
- A resource loop: lamp-charge as expiring scarcity; the master
  breaker as a build target.
- Findable message-room pages (the lore is already written in
  levels.json's `door_lines` / pages — surface it as pickups).
- loadout.json: currency = WIRE; flags = doors/shortcuts.

### Wave 3 · THE LOOP ROLLOUT (order: biggest first)
fey_faire → estuary_3 → earthman_chronicles → pirate_summer →
northwind_harbor → spiderdrops/2 → the rest. Per stick: currency in
its own noun, 6-9 upgrades, ≥1 flag/tier, `finish_run` at every
ending, boot reads. ~2 call sites + 1 JSON each (engine done).

### Wave 4 · THIN-DATA THICKENING (the 6-18K tier)
sweetgum, sams_summer_shifts, kwik_stop_manager, estuary_4:
triple the encounter/variant pools so a second run reads new.
estuary_1 stays austere ON PURPOSE (one lever is the design) — it
gets variants for its twelve weeks, not new systems.

### Wave 5 · LEGIBLE-CHALLENGE SWEEP
Port the Fey Faire five-pip read pattern to every stick with an
engage/avoid decision: Wyrd encounters (grit/silver risk read),
Earthman combats, Pirate Summer dungeons, Basilica floors.

### Wave 6 · PRESENTATION AUDIT
Contrast-measure every stick's palette the way Earthman was fixed
(2.0:1 measured → 4.5:1 shipped). SlowstickLook preset + hero art
title/endings check across all 22.

## Standing rules while executing

- Verify with `gdparse` AND `gdinfer_check.py` (CLAUDE.md).
- Layout: containers only, no hand-placed pixels (2026-07-30 sweep:
  five screens broke the same way).
- Every wave ends with a Recent-lessons entry in
  `_SLOWSTOCK_AUTHORING_PLAYBOOK.md` and an update to THIS file's
  table (re-run the measurement script — it's in the git log of this
  file's first commit).
