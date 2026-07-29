# IMPROVEMENT ROADMAP · recommended next work

**Updated 2026-07-22.** The living plan for continual improvement
across every pillar. Priorities reflect the user's standing verdicts:
**graphics and presentation are always the sore points; the visual
novel needs the most work.** Update this doc when an item ships or a
blocking decision lands; future sessions should read it alongside
CLAUDE.md's playbook list.

## North star

Every pillar reads as a finished, art-directed work: the VN as a
cinematic literary book, the slowsticks as "modern games through an
alt-reality prism" at a minimum early-90s 256-color SVGA bar
(Sierra/LucasArts), and all departments delivering in sync (the
producer discipline).

---

## The three gates (user-side; everything flows faster once these land)

1. **ART ROUTE** — the standing decision: hybrid (AI-painted sources +
   procedural), but no image key exists and no ArtCraft exports have
   landed. Options: (a) you drive ArtCraft/any generator and drop
   exports through `godot/tools/art/art_studio.html`; (b) drop a
   direct-API key (Flux/BFL, OpenAI images, or Gemini) at
   `godot/tools/art/.image_key` and Claude wires `scene_render.py`
   for batch generation; (c) both. **This gates the biggest visual
   wins in the whole project** (painted VN backgrounds/plates, the
   SVGA retrofit of all ~21 slowsticks, CP banners).
2. **MIXAMO SESSIONS** — `godot/HANDOFF_CHARACTER_MODELS.md` is a
   paint-by-numbers list of the 15 missing vol 6–7 character models.
   Engine side is done; each GLB dropped in upgrades a character from
   a 60×64 pixel bust to a lit 3D portrait, zero code. Lena first.
3. **DECK FEEL PASS** — one playthrough of a vol 5 chapter start-to-
   finish to tune the new presentation grammar (fade/hold/settle
   durations, typewriter pacing multipliers, portrait rise, choice
   plate look, reading-surface scrim 0.34, chapter whisper). Plus the
   standing slowstick verify list: Tideline parallax, diorama demo,
   per-studio shader modes, Spiderdrops/Long Wind/Salmonberry feel.

---

## Pillar backlogs (P0 = do next · P1 = soon · P2 = when reached)

### Visual novel (vols 5–7) — top priority

- **P0 · Character models wire-in + lighting tune** — as GLBs land
  from gate 2, tune `Portrait3D.CHARACTER_LIGHTING` per model.
  (Claude, same-day per model.)
- **P0 · Painted backgrounds/plates** (gate 1) — full-res painted VN
  art (the VN is the modern frame — NO era filter): chapter-card
  backing plates, CG art, locale PNG fallbacks for unbuilt GLB
  locales. Extend `art_studio.html`'s catalog with VN slots; hook
  plate display through the producer clock.
- **SHIPPED 2026-07 · Locale coverage report** —
  `python3 godot/tools/locale_coverage.py` (run on the Deck):
  cross-references the 78 GLB-requiring camera presets against the
  `3d:` story directives and the files on disk, prints the missing
  list in build-priority order with the exact `run_cathedral.sh`
  command per locale. Born from a real boot error
  (riverboat_interior.glb unbuilt).
- **P1 · Dialogue-surface iteration** — after the Deck look: scrim
  number, and the parked taste call on any further chrome.
- **SHIPPED 2026-07 · Kinetic text** — grammar documented in the
  direction playbook; first seeds in vol5_ch0. Ongoing: seed
  sparingly at the lines that turn.
- **P2 · Speaker-biased text columns** (`DialogueBox._anchor_to` dead
  intent) · letterbox on `establish~` shots · CharLayer
  resolution-relative positions. All taste/robustness, low urgency.

### Slowsticks (the shelf)

- **P0 · DEPTH FLOOR sweep (2026-07-27 user verdict: "far too
  basic... I want depth of play")** — the authoring playbook now
  carries a six-point depth floor (three interlocking systems, ≥30
  decisions/run, visible checks, expiring scarcity, a build,
  textured failure). Audit result: roughly half the shelf is under
  it. Rebuild queue, worst-first by user impact:
  1. **SHIPPED 2026-07 · Salmonberry v2** — the week loop: 4 weeks
     per month (40 decisions), energy budget, deterministic weather
     + one-week forecast, board owed monthly, shown skill checks
     with strong/fair/rough tiers, the general store (5 gear items
     that change play), 9 one-week-only calendar events incl. a
     stakes rescue off the bar, bond decay. Deck-verify pending.
  2. **SHIPPED 2026-07 · Northwind Harbor full game** — 26
     optional kindness/errand chains (52 steps), each gated behind
     its own overheard hint; more morning than the 73 minutes
     allow; Bosun fetch at trust ≥3; horn summary + THE GOOD WEEK.
     All canon steps verbatim. Deck-verify pending.
  3. **SHIPPED 2026-07 · Estuary 4 · THE WORKING SEASON** — 13
     field weeks between the calls and the king tide: budget, crew
     morale, seeded tide windows, forecast storms with prep-or-pay,
     grant deadline, storm damage/repair; the king tide reads built
     quality per project. Deck-verify pending.
  4. **SHIPPED 2026-07 · Tideline / Spiderdrops 2 / Mrs Wu second
     systems** — Tideline: THE TIDE CLOCK (walking/recording/
     watching cost minutes; nine observations live in tide windows
     with authored gone/early ghost lines; the report reads your
     pace). SD2: airborne drops hang low near the churn (+silk,
     risk/reward) + gold thermal columns with free lift, each
     scrolling past exactly once. Mrs Wu: weather rewrites the
     evening's needs (wind = tie up TONIGHT, rain = slugs + free
     watering), the linen chest (frost sheets EARNED by spending
     drying-weather actions washing), the pumpkin boy covers a bed
     on frost night if you tended his twice. Deck-verify pending.
  5. Vignette tier, corrected and in progress:
     - **EXEMPT · Sweetgum** — the audit mislabeled it (truncated
       listing): SweetgumNight.gd (458 lines) delivers its design
       doc 1:1 — rounds, the typed palimpsest log, NOT A STATION,
       the 3 AM sounds, 06:00 QUIET, the NAMES field. Its design
       explicitly forbids expansion ("there is no third
       variation"); deliberate single-scene art objects are judged
       by their own doc, and this one passes.
     - **SHIPPED 2026-07 · Sam's Summer Shifts · THE SHIFT** — the
       "one scripted beat per week" pattern (the exact Salmonberry
       sin) fixed: every week opens at the register with a seeded
       customer queue — ring the right total from three (register
       craft feeds TILL; ≥80% right pays the drawer, <50% costs
       it), handle authored counter moments (Gus's dime, the
       out-of-county check, the unfinished mustache), Heritage
       week rings a longer line with tighter totals, the solo week
       doubles till swings, and week 6's third customer is not a
       customer. ~100 decisions per summer. Deck-verify pending.
     - **RE-AUDITED COMPLETE · Patient Mister Glass** — the deck
       is fully authored (39 rotation variants, trust/cooking/rain
       gates) and all nine ledger findings are wired to real
       variant pairs with unlock chains and three verdicts. The
       slow-detective design is implemented 1:1.
     - **RE-AUDITED COMPLETE · Riffrocker Melody Club** — twelve
       meetings × ~3 call-and-response phrases on the live 3-osc
       PD Riffrocker voice; meeting 12's open mic records YOUR
       take as the cartridge's title music forever. An instrument
       with a club around it, per its design.
     - **RE-AUDITED COMPLETE · Hane no Niwa** — 4 seasons × 9
       visits, four verbs with visible maintenance memory, a
       20-item offering economy, the letters system, fox
       expressions reading unshown upkeep. Passes on its own doc.
     THE DEPTH SWEEP IS CLOSED. Lesson captured in the authoring
     playbook: audit sticks by READING THEIR DATA, not by wc -l —
     the line-count audit mislabeled four of five in this tier.
- **SHIPPED 2026-07 · Sisters Wyrd readability triage** (user: "an
  eyesore") — focus dimming by distance from the drifter (the soup
  fix), label plates, position ring, styled choice buttons lifted
  clear of the log, log opacity/edge. Depth machinery was already
  in (task #175); re-verify feel on Deck after the readability pass.
- **SHIPPED 2026-07 · Earthman palette soften** (user: "hard on the
  eyes") — neon green/pure red/hot amber/stark white desaturated to
  sage/brick/soft amber/warm paper across all 10 scenes; ch2 rust
  glare dimmed.
- **P0 · SVGA retrofit pilot** (gate 1) — the approved direction:
  painted source → `svga_quantize` era filter → per-studio slots via
  `art_studio.html`. Pilot on Salmonberry (title + 5 endings), then
  sweep the catalog studio by studio. The old flat-vector HeroImage
  scenes remain only as fallbacks.
- **P1 · Estuary 4 thinness pass** — the last thinness-cluster stick
  still bare (art through the new pipeline + a BGM pass).
- **SHIPPED 2026-07 · Salmonberry Wave A: the town overworld (v1)**
  — walkable Salmonberry as the month interface (see the design doc).
  Next: Waves C (playable tsunami crisis) and D (full roster/errands);
  town v2 candidates: NPC figures at their places, month-gated
  weather/light, interior beats.
- **P1 · Mrs Wu BGM sign-off** — two composition scores are written
  and awaiting your ear before render/wire.
- **P2 · Spiderdrops 2-player pass-the-stick** (the box promised it)
  · wire the 3D diorama behind Basilica (pending z-order verify) ·
  roll HeroImage-2.0/parallax/diorama to more sticks (superseded in
  part by the SVGA retrofit — decide per stick).

### Community Planned (vol 6 inset)

- **P1 · Visual upgrade, re-planned for the new art bar** — the old
  pass-10 plan (region banner vignettes + agent busts) was authored
  for flat-vector; keep its structure (Small Wood's banner tracking
  tower-brightness is a great idea) but generate banners through the
  painted pipeline (gate 1). The `VnBustPortrait` agent-roster halves
  can proceed anytime (engine-side).

### Tarot Gauntlet (vol 5 inset)

- **P2 · Painted visitor/card plates** (gate 1) — the procedural
  bust fallback works; painted marquee-visitor plates would lift the
  most-seen screens. Low urgency after the recent look-table pass.

### Audio

- Healthy (96-slot audit green, every stick scored). **P2:**
  Salmonberry per-season bed variants · VN ambient choreography as a
  producer client · a Long Wind `silk_cast`-family ambient set.

### Cross-cutting / systems

- **SHIPPED 2026-07 · Producer beats + kinetic text** — `[beat:
  still|hit|chill|lift]` directive (sting + haptic + camera breath +
  letterbox pulse in one call, VnDirector-executed, locale-parked,
  drift-safe) and the native BBCode kinetic-text grammar documented;
  first seeds in vol5_ch0 (the bell · "the walls are thin"). Next:
  seed beats across vols 5-7's emphatic reveals as chapters are
  reread.
- **P2 · Screenshot mode** — F4 already hides HUD; a deliberate
  photo mode (letterbox + pause + no cursor) is ~30 lines and serves
  the user's clean-pictures habit.
- **Discipline reminders** — lesson-capture cadence per playbook;
  emit-and-consume tokens in the same commit; gdparse + JSON sweep
  before every push; scope commits (revert normalize_bank's unrelated
  WAV touches).

---

## Recommended sequence (next five arcs)

1. **Unblock gate 1** (your single highest-leverage act: a key or a
   first ArtCraft export) → Claude pilots painted VN plates + the
   Salmonberry SVGA set in one arc, both through the same tools.
2. **First Mixamo session** — Lena + Mrs. Gable + Petra (vol 7 core).
   Claude wires lighting per model as they land.
3. **Salmonberry town overworld** (Wave A) — the flagship gameplay
   build; no external dependencies, starts on your word.
4. **Producer beats + kinetic text** — one authoring-power arc that
   makes vols 5–7 more cinematic with zero new art.
5. **Estuary 4 thinness pass + CP visual upgrade** — sweep the two
   remaining thin spots with the by-then-proven art pipeline.

Items 3 and 4 are fully Claude-side and can proceed in any gap while
gates 1–2 wait.

---

## 2026-07-28 · FULL AUDIT + FIX WAVE (shipped same day)

Four pillar audits (VN, slowsticks, CP, gauntlet) → 48 ranked
findings → five fix waves, all landed. Highlights: the vol 7
index no longer hard-ends the book and its 19-scene expanded
ch6/ch7 rewrite is live · VN resume rebuilds the full scene state
and saves land on the line being read · the in-game menu closes on
ESC and autosaves on exit · gauntlet fullscreen no longer feeds
clicks to invisible controls, the authored inertia_max /
visitors_claimed_max difficulty knobs are honored at last, help
and goal lines are arcana-correct, DRIFT/UPKEEP auto-advance ·
CP enforces rest, explains every ineligibility, and fits 1280
with four regions · seven slowstick resume exploits closed ·
23 procedural floor plates under the gauntlet board (default ON
at 0.42 — pure material, nothing to misalign). Deck-verify the
lot on the next session.
