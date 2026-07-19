# Package Improvement Backlog · Modern Mythology

A living, whole-package list: every scene, every game, one document.
Compiled 2026-07-19 from a full repo audit (bg-reuse counts, gallery
inventory, manifest states, panel/pack/preset coverage). Priorities:

- **P1** — a player will notice within one session
- **P2** — quality ceiling raisers; noticeable across a playthrough
- **P3** — polish, consistency, pipeline health

Strike items as they land; move user-feedback items up a tier.

─────────────────────────────────────────────────────────────────────

## 1 · VN — sets & scenes (vols 5–6)

**P1 · ~~Finish the wrong-room sweep~~ DONE 2026-07-19.** 29 → 10 legit back-office segments; all repoints + seven builds shipped (ben_bedroom, coach_k_bedroom, kowalski_backyard, henderson_porch_front, gym_weight_room, equipment_shed, nightmare_cell). 27 `cosmic_comics_back_office`
segments remain in 17 scenes. Audited classification:

- LEGIT (it really is Rick's back office — leave, maybe re-verify the
  camera): ch12_cosmic ×5, ch21_cosmic ×2, ch4_speak_spell ×2,
  ch3_back_room (arrival at Cosmic's back door).
- REPOINT to existing presets (one-line fixes, live on pull):
  - ch22_inventory ("precision phase since two") → `centro_stockroom`
  - ch2_maya_bedroom (grandmother awake in the dark, interlude IS
    "Maya Daigle's Bedroom") → `maya_bedroom` or grandmother's room
  - ch3_coda (subdivision at night, water tower) → `louisiana_road`
  - ch17_porch "Elsewhere" (desk in a small office off a kitchen) →
    audit against houston_office / henderson_kitchen
  - ch23_sunday (grandmother's front porch, cicadas) → porch preset
    audit (miller_back_porch is the wrong house — decide reuse vs new)
- BUILD (new bespoke locales, same playbook as darkroom/garage):
  - `ben_bedroom` — ch23_sleep (Ben, the cat, the cracked door)
  - `kowalski_backyard` — ch7_ben_room (lawn, patio, Daisy, the
    butterfly; big emotional beat, deserves its set)
  - `henderson_porch_front` — ch7_henderson_driveway + ch14_live_oak
    + ch19_chains home beats (porch steps at night, kitchen light on
    for Jesse — one build covers 4+ segments)
  - `gym_weight_room` — ch13_two_a_days (basement weight room)
  - `equipment_shed` — ch19_depthchart (Coach Dale sorting)
  - Coach K's bedroom (ch19_chains) — could re-dress an existing
    bedroom build with the bed-variation rules rather than new geometry

**P2 · Audit the other big reuses.** `louisiana_road` (67 uses — many
are legit arrival beats per the playbook rule, but sweep for single-bg
scenes stuck on it), `lena_apartment` (14), `miller_back_porch` (16),
`school_field_evening` (10). Same method: dump narrates under each bg,
classify legit vs wrong.

**P2 · ~~Vol5 panels~~ DONE 2026-07-19** (napkin, model city, packing boxes, Q. PAUL, record player). Original note: The `[panel:]`
pipeline is proven in vol6 (4 panels). Vol5 climax candidates: the
Fool's diner reveal, the Magician's cathedral workbench, the Priestess
packing, the riverboat at dusk, the Devil's station. 4–6 panels.

**P2 · ~~More vol6 panels~~ DONE 2026-07-19** (foxhole flyer, Rick's notebook, corkboard sheet). Original note: Candidates: the Foxhole flyer (ch14), the
photograph pinned on the line (prelude callback at ch12), Maya's
evidence board, the bridge finally working (ch20 — could be abstract),
Rick's spiral notebook page.

**P3 · Per-chapter direction spot-fix loop.** The framework
(mood-per-cut, ray-verified cameras) is in place; remaining work is
playtest-driven: user flags a chapter that reads off → tune that one.

## 2 · VN — portraits & cast

**P1 · Per-character bust overrides from playtest.** AWAITING USER
NOTES — each is a one-line `_OVERRIDES` entry (the redhead-Sam
format). Whole cast is eligible; leads first.

**P2 · Hand-authored pixel portraits for the ~10 leads** (rundown
item 2, deferred until override notes land). Fey Faire's
authored-override-over-hash-fallback pattern, ported to
VnBustPortrait: authored 60×64 grids for Sam, Maya, Diego, Rick,
Graciela, the vol7 five; hash busts for everyone else.

**P2 · ~~Talk animation~~ DONE 2026-07-19** — 'talk' frame + active-speaker flap while the typewriter runs. Original note: Blink already works; add a 2-frame mouth
flap on the active speaker while the typewriter is running (same
cache-swap trick as blink — render a "talk" frame with open mouth).

**P3 · Bust engine v3 vocabulary** as needs arise: hair-behind-
shoulders back layer, per-outfit collar colors decoupled from accent,
hats, age "child", head-tilt idle variant.

**P3 · Hero GLB portrait consistency decision.** John/Frasier/etc.
render as 3D portraits, everyone else as busts — two art styles in
one dialogue. Either art-direct the GLB lighting to sit closer to the
bust palette, or standardize leads on authored busts (see P2) and
retire the 3D heads from dialogue slots.

**P3 · Gallery face art.** Only 13 `*_face.png` crops exist.
Mackenzie (CP) has none (phone portraits only) — crop or author one
so the CP board's real-art routing covers all four named agents.

## 3 · VN — presentation chrome

**P2 · ~~Extend nameplate chrome to terminal/paper skins~~ DONE 2026-07-19.** Original note: The accent
underline + speaker-change pop currently ship on the standard skin
only.

**P2 · Interlude cards.** The location/time interlude is plain text —
give it the accent treatment: thin rule, letter-spaced caps, maybe a
tiny HeroImage glyph per location family.

**P3 · Choice menu styling pass** to match the new chrome (accent
hover states, keyboard hints), and the unlock toast / HudBar
consistency check.

**P3 · Panel polish.** A "photo print" frame variant for panels that
are diegetic photographs (white border, slight rotation); panel
open/close SFX (see §7).

## 4 · Tarot Gauntlet

**P1 · ~~Arcana bookend cards~~ DONE 2026-07-19** — 22 procedural cards, title overlay + end-screen fallback (killed the dev-placeholder leak). Named-loss illustrations remain future work. Original note: All 22 arcana have setups and accent
hues; give each a HeroImage title card at gauntlet start + a win/loss
end card (the loss conditions are named — illustrate the named ones
over time, pedagogy per the design playbook).

**P2 · Visitor faces on the board.** Verify every visitor render path
goes through bust v2.1 (blink + expressions), not a stale v1 call;
demons get the fixed sickly-violet accent everywhere.

**P2 · Time-of-day light packs.** Difficulty axis is time-of-day;
make it VISIBLE — a per-setup mood/lighting recipe (dawn/noon/dusk/
night) applied to the gauntlet board chrome, not just implied by text.

**P3 · Board texture pass** — felt/wood grain via HeroImage noise ops
behind the card slots; card-flip micro-animation.

## 5 · Community Planned

**P1 · Verify pass 10 in play.** Region banners are generated + wired
(incl. the four small_wood tower-brightness variants swapping with
game state) — confirm on Deck, tune banner heights/crops if they sit
wrong in the folder panels.

**P2 · Mission-stage transitions.** Stage changes are text swaps —
add a short stinger: banner flash, accent wipe, one SFX (Wave C bank
already has demon-depth sounds to draw from).

**P2 · Dossier depth.** Demon dossiers could pass expression "angry"
to the bust for a harder face; add the sickly-violet accent border so
class reads at a glance in the modal too.

**P3 · Small Wood dread escalation.** As tower brightness rises, tint
the whole board chrome slightly (the banner already redraws — extend
the wash to panel borders). JSON stays data-truth; render-only.

**Protected:** BBS phosphor terminal is diegetic — do not restyle.

## 6 · Slowsticks (vol7)

**P1 · ~~Sync stale manifest metadata~~ DONE 2026-07-19.** Original note: fey_faire + earthman_chronicles
manifests still say "playable acts deferred" and pirate_summer says
"wave_b_playable" — all three are far past that. Whatever the shelf
UI shows from `status` is lying to the player.

**P2 · Aesthetic-bible audit per stick.** Sweep every playable stick
against `_SLOWSTICK_AESTHETIC_BIBLE`: SlowstickLook.apply() preset
present and per-studio, font floor 12 respected, no our-timeline
retro cosplay. The early sticks (estuary_1, northwind_harbor) were
built fast — most likely to drift.

**P2 · Art passes for the thin playable_v1 sticks — AUDIT NOTE 2026-07-19: sweetgum's zero-art is intentional ('Three colors. No sprites. No hero images.'). Audit per-stick before adding art; some minimalism is the studio voice.** Original note: estuary_1,
estuary_2, sweetgum, riffmaster_melody_club, hane_no_niwa,
patient_mister_glass, sisters_wyrd, basilica (empty sleeve is canon —
leave), sams_summer_shifts: each wants its title HeroImage, 1–2
mid-game images, and an ending card where missing. Audit first —
some already have them.

**P2 · ~~BGM coverage~~ AUDITED CLEAN 2026-07-19** — all ten newer sticks reference existing per-stick BGM dirs (e1/e2/nh/sg/hnn/pmg/sw/sss/ksm); riffmaster is diegetically scored through the PDP Riffmaster voice BY DESIGN. Original note: The Wave A–F audit hit
100% for its era; the sticks built after (estuary_1, northwind,
sweetgum, e2, hane_no_niwa, glass, riffmaster, wyrd) need a
composition sweep — silence check at boot, one bed per major scene.

**P3 · Fey Faire / Earthman presentation polish.** Combat and
negotiation are data-driven text — add accent color per Court/species,
portrait placement, beat SFX. Ending scenes: verify all endings have
art (FF has 7, EM has 6).

**P3 · Pirate Summer night/weather palette.** The time-tint overlay
exists; a rain day and a fog morning would make the six-day loop feel
less same-y. Also: cabin interiors share a template — bed-variation
rules apply there too.

## 7 · Audio

**P2 · ~~Moment SFX~~ DONE 2026-07-19** — page_turn/menu_close on panel open/close, blip on speaker change, card_flip/place on the gauntlet title card (existing presets, zero new assets). Original note: panel open/close (photo-swish
for prints, phone-buzz for the transport order is diegetic in-scene
already), speaker-change tick (very quiet), CP banner stage stinger.
All within slowstick_synth presets.

**P2 · Ambient bed coverage audit.** 72 entries vs ~71 presets — run
the coverage check again after the porch/bedroom/weight-room builds
land; every new locale ships its bed in the same commit (rule).

**P3 · Per-locale one-shot layers.** cicadas already bed the garage/
dock; single-shot events (garage door rattle, bindery bell — the
LOWER, MELLOWER bell is canon, dock truck air brakes for ch16's
truck arrival) tied to scene entry.

## 8 · Cross-cutting & pipeline health

**P1 · F4 sweep regression test.** New HUD members landed this arc
(speaker underline lives inside DialogueBox → safe; CP banners live
in panels → safe) — but run the playbook test: F4 at scene start,
wait for dynamic members, confirm nothing pops.

**P2 · Stale-GLB detector.** The #1 recurring failure ("I don't see
changes") is a stale Deck GLB. At boot, when a preset's tscn is newer
than its .glb mtime, print one warning line listing the build command.
Cheap, kills a whole class of confusion.

**P2 · Liminal drift-check + locale JSON coverage** for all new
locales (darkroom, graciela_bedroom, miller_office/garage, henderson_
garage, bindery, centro_stockroom + upcoming builds) — the runtime
checker warns on desync; make sure none of the new rooms warn.

**P3 · Contact-sheet CI habit.** Every procedural-art generator
(busts, banners, panels, sprites) has a previewer — one script that
renders ALL of them to a single sheet would make regressions visible
in one glance after any engine change.

**P3 · Preset hygiene.** `kwik_stop_godseye` is a debug preset in the
shipping table — harmless, but tag debug presets so a scene can't
accidentally use one.

─────────────────────────────────────────────────────────────────────

## Suggested batch order

1. Repoint-only wrong-room fixes (§1 P1 repoints — live on pull, no
   rebuild) + manifest status sync (§6 P1) + F4 regression test.
2. Build wave: ben_bedroom + kowalski_backyard + henderson_porch_front
   (+ weight room / shed if appetite) — one Deck rebuild.
3. Vol5 panel set + remaining vol6 panels.
4. Gauntlet bookend cards (22 title + named-loss cards, batched).
5. Per-character bust overrides as playtest notes arrive (continuous).
6. Slowstick art/BGM audit sweep, thinnest sticks first.
7. Talk-flap + chrome extensions + moment SFX.
