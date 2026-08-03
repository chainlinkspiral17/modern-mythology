# VN VISUAL AUDIT · 2026-08-02

Three parallel surveys (direction-grammar usage across all 245 scene
files · locale/lighting estate · character-presentation layer),
fused. Numbers are measured, not sampled. The creative inventory at
the bottom is ranked by visible-impact-per-effort and respects the
honest ceilings: no textures, screen-space shaders only, faces live
on the 2D portrait layer.

---

## PART 1 · WHAT IS ACTUALLY BROKEN (bugs, not gaps)

These are live defects a reader can see today, ranked by how many
minutes of the book they poison.

### 1.1 · The two Vol 7 leads wear the wrong art ★ WORST BUG IN THE VN
`CharLayer._find_in_gallery_index` does substring fuzzy matching as
the last resort before the procedural bust. Result:
- **`tem` — 945 lines, the most-speaking character in Vol 7 —
  renders `temperance.png`, the tarot card.**
- **`lena` — 626 lines — renders `so_lena_de_garden_gauntlet_board.png`,
  a 1000×600 location plate.**
- `per` (223 lines) → `emperor.png` · `em` (57) → `emperor.png` ·
  `man` → `hanged_man.png` · `judge` → `judgement.png` · `jo` →
  John's portrait.
Fix shape: minimum-key-length + word-boundary guard on the fuzzy
index (a 3-letter key must never substring-match), so all seven fall
through to their busts. Then Tier-2's bust overrides make the busts
good.

### 1.2 · Twelve black climaxes · Vol 7's `cg` nodes point at nothing
All 12 `cg` nodes in the game are in Vol 7 — the stick, the door,
the wall, the portal, the cabin, the epilogue gallery — and every
referenced `assets/cg/vol7_*.png` **does not exist**. `CgPanel`
presents a black screen with a caption and a settle-zoom on nothing.
These are the book's biggest authored visual moments, currently
rendered as a void. (The plate pipeline that made the 9 endpapers
and 23 gauntlet floors can produce these.)

### 1.3 · Vol 5's endpapers never rotate
Plate choice is `absi(chapter) % 3`, but Vol 5 chapters are Roman
numerals — `int("I")` is `0` — so 26 of 27 scenes show
`chapter_v5_0.png` and `chapter_v5_2.png` has never been seen by
anyone. Parse the numeral (or hash the string).

### 1.4 · The finale chapters are undirected and unhomed
13 real (non-stub) Vol 7 scenes — the ch6 + ch8 cluster: the
apology, the daughter, the vessel, Nate, the call, goodnight —
carry **zero** direction of any kind AND **no `bg` node**, so they
inherit whatever locale the previous scene left loaded. The emotional
crescendo of the entire three-volume book is the least-directed text
in it. (For scale: vol5 median direction ratio 0.206; these are 0.)

### 1.5 · Thirteen expression words silently do nothing
Authors used 21 expression tokens; the three expression tables
(tints / 3D moods / bust families) know 8 of them. `serious` — used
by 26 characters — plus `thinking, cold, worried, amused, softening,
hurt, considering, calculating, impressed, patient, thoughtful,
focused` all collapse to `neutral` without a warning. Map each to
the nearest family + tint; add unknown-token warnings.

### 1.6 · Vols 1-2 play over missing backgrounds (found by the gate, post-audit)
The surveys checked vols 5-7 (all-3D, clean). The new
`vn_asset_audit.py` gate's first run found the older estate: **~40
distinct 2D background JPEGs referenced by Vol 1-2 scenes do not
exist on disk** (`assets/backgrounds/vol1_*.jpg`, `vol2_*.jpg` —
the bar, the club, the dream sequences, all of Briar Falls), plus a
handful of vol1 scenes with no bg at all. Vols 3-4 are near-stubs.
Those volumes predate the 3D-locale era and largely play over black.
RESOLVED IN PART (2026-08-02, T2): all 39 missing backgrounds now
exist — gen_legacy_backgrounds.py renders them as flat-graphic
full-screen plates (calm centers for the portrait layer; vol1 warm-
dark urban, vol2 muted coastal-Americana). Legacy baseline dropped
81 -> 21; the remainder is old no-bg hub scenes, not missing art.

### 1.7 · Dead wiring (harmless today, misleading forever)
- 22 of 38 `PORTRAIT_3D_KEY_TO_GLB` entries point at GLBs that don't
  exist (kai, finn, tem, lena, wren, petra…). The demon's GLB dir
  contains only a README.
- 5 STYLE_PACKS name a `lighting` value that isn't a lighting preset
  (`cyberpunk_neon → neon_signage`, 4 others name MOODS).
- 2 camera presets (`diner_exterior_porch`, `kwik_stop_godseye`) and
  16 locale tscn are unreachable from any scene.
- `sam_miller_gnm.glb` sits on disk, shelved by comment, while Sam
  (368 lines) renders as a bust.

---

## PART 2 · THE SHAPE OF THE ESTATE (measured)

**Direction** · 2,177 directives over 15,125 text nodes. Vol 5 is
the reference (ratio 0.28); Vol 7 runs at half that (0.126). Shots
are healthy (1,544; establish/closeup/insert all live, drift used
tastefully on 60 specs). Beats: all four used, good spread. Kinetic
text: exactly one line per file that uses it — ceremonial, as
designed. **Panels: 23 uses ever, zero in Vol 7. Staging: Vol 5
only, 4 characters ever placed.**

**Looks** · 27 of 109 mood/pack names ever used. The used set is
exactly the direction-safe grade set from the playbook ban — the
sweep discipline held. But it means 37 moods + 45 packs are
authored, maintained, and invisible — including the entire
silent_film / lithograph / ink / noir families and 15 bespoke
per-locale packs (`dambrosios_3am` is cited in the playbook as the
canonical example and appears in no script).

**Locales** · 94 scenes, 78 wired, 62,073 lines of Blender builders.
- **Vantages: 71 of 74 GLB-backed locales have exactly ONE camera.**
  Only diner (3), centro (2), kwik_stop (2) offer choice. Every
  closeup/insert elsewhere is a synthesized punch-in from one
  standing position — this is the single biggest ceiling on the
  "3D comic" ambition.
- Lighting: uniform env/fog/glow boilerplate; SSAO nowhere;
  **SpotLight3D used once in the whole game** (the playbook's
  signage/entry spot rule is a dead letter). ~12 non-exempt locales
  sit below the three-light foundation (1 directional + 2 omni).
- Liminal: the proximity controller ships in 90 tscn but has a
  location_json in **4** — the "walls are thin" system is inert in
  87 rooms. (The four live ones are the right four; this is a
  coverage question, not drift. Cathedral's roster line is one
  station stale: 5 wip plinths, playbook says 4.)

**Characters** · 171 speaking keys. Authored art: **11** (6.4%),
all Vols 1/5/6. The entire Vol 7 cast — kai (663), finn (460), cale
(289), hans, roy, marina, marit, aud, petra — plus Vol 6's sam,
maya, jesse, diego, ben, bianca, eileen run on procedural busts; 36
keys have deterministic bust overrides, the rest are hash-faces.
`assets/characters/` — the per-expression PNG convention the
resolver searches first — contains ONE file. Accents: 6 characters;
everyone else shares the default parchment.

**Chrome** · 6 skins (3 variants) — genuinely differentiated, one of
the strongest layers. Chapter cards fire correctly; 68/74 have
plates; **Vols 1-4's 6 cards show flat black** (no plates exist).
Photo mode = hide-chrome + bars only: no screenshot, no free-cam.

---

## PART 3 · CREATIVE INVENTORY · ranked

### TIER 1 · REPAIRS (days, not weeks — every item finishes a thing readers already hit)
1. **Fuzzy-match guard + the seven victims re-bust** (1.1). One
   function + seven `_OVERRIDES` entries. Tem and Lena stop being
   tarot cards the same hour.
2. **The twelve Vol 7 CG plates** (1.2). PIL pipeline exists
   (endpapers, floors). 1280×720, one per beat, in the deckle/laid
   language of the endpapers so they read as the same book. The
   single highest art-for-effort ratio available anywhere in the
   project.
3. **Direct the finale cluster** (1.4). 13 scenes × (one bg + one
   mood + 2-4 shots + one beat). Vol 5 grammar, applied where the
   book is loudest. Includes giving each a real locale home.
4. **Roman-numeral plate fix** (1.3) + **expression-token mapping**
   (1.5) + **dead-wiring sweep** (1.6: prune or fulfill the 22 GLB
   stubs, fix 5 pack lighting refs, decide sam_gnm in or out).
5. **A `vn_asset_audit.py` gate** so none of this regresses: cg srcs
   exist · every non-stub scene declares a bg · expression tokens
   known · pack lighting refs valid · fuzzy index never serves a
   sub-4-char key. Same pattern as gdinfer/contrast audits.

### TIER 2 · THE PRESENTATION LIFT (the "sore point" attacked directly)
6. **Bust-override pass for the top 20 unportrayed speakers** —
   kai, finn, tem, lena, cale, hans, roy, marina, sam, maya, jesse,
   diego, ben, bianca, eileen, per, marit, aud, wren, chief_miller.
   Deterministic features + an accent each (extends CHAR_ACCENTS
   6 → ~26, which also colors nameplates and underlines). This is
   the cheapest way to make the cast feel *cast*.
7. **Second-vantage pass on the ten most-visited locales.** Add 2-3
   authored `shot_closeup_*` / `shot_insert_*` markers each (survey
   with the layout oracle first, per playbook). Converts the comic
   grammar from synthesized punch-ins to authored framing where the
   reader spends most hours. Diner is the proof it works.
8. **Practicals + spots pass** on the 12 under-lit rooms and the
   signage/entry spots the playbook already prescribes (1 spot in
   the whole game today). Kelvin gels per the lighting playbook.
9. **Vol 7 panels** (currently zero): the ledger page, the patch
   note, Lena's letter, the tower diagram, the bus schedule.
   5-8 HeroImage panel JSONs; the machinery is idle and proven.
10. **Deliberate strata for the unused look families**: silent_film
    for the 1994 memories, lithograph for one D'Ambrosio interlude,
    substrate for the tower's POV — as INTERLUDE strata (the
    playbook's neon-1.0 scene-direction ban stands; these are
    one-scene events, entered clean, exited clean). Either use the
    families on purpose or archive them out of MoodCycler.
11. **Liminal coverage growth**: 3-5 new stations in Vol 6/7 rooms
    the fiction already marks as thin (Small Wood's tower room, the
    darkroom, the bindery back shelf), via the JSON-first process.

### TIER 3 · NEW CAPABILITY (bigger swings, user-gated)
12. **Photo mode v2**: F6 keeps chrome-hide + bars; add screenshot
    to `user://photos/` (the user photographs the game for a
    living), slow orbital drift cam, and letterbox toggle.
13. **Plates for Vols 1-4** (6 flat-black cards today) in each
    volume's skin language (literary marbling / signal phosphor /
    zine halftone).
14. **Staging: commit or retire.** Heroes exist for 7 characters;
    Vol 6/7 never stage anyone. Either a staging pass for the
    scenes where bodies-in-room matters (the kitchen, the meeting,
    the porch) or an honest playbook note that staging was a Vol 5
    experiment. A capability that exists but is never used reads as
    a bug to future sessions.
15. **Second direction sweep, vol6/7 low-ratio giants**:
    el_rancho (274 nodes @ 0.047), kwik_stop ch15 (292 @ 0.058),
    dawn, bianca, per — the five biggest×barest chapters after the
    finale cluster.

## Sequencing recommendation
T1 items 1-5 in one wave (they are all finishing moves), then T2.6
+ T2.7 as the visible-lift wave, then T2.8-11 as the craft wave.
T3 gated on user say-so per the roadmap convention.
