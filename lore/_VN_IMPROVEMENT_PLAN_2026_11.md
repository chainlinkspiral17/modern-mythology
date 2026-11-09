# THE VISUAL NOVEL · comprehensive improvement plan (2026-11-09)

The user (2026-11-09): "plan out a comprehensive improvement for the whole
of the visual novel, with the tasks still outstanding. Tweak the
psychedelic for each chapter as needed, create new visual effects that are
appropriate. Fix textures and scene geometry and portrait direction. Also,
art is very murky in the current scene renderer. Maybe find a way to lessen
its effect on imagery. Director is also not highlighting the art enough in
the scenes in close ups, etc."

Everything here is a numbered DRAFT (CLAUDE.md, THE DRAFTING PROGRAM). The
plan is ordered by what the user sees most: the pictures first, then the
camera, then the trip, then the sets and portraits. Each phase names its
gate — the audit or render that proves it — so no phase can pass on its
author's word.

---

## Why the art is murky (read 2026-11-09)

A generated picture (HeroArt) is a lit quad on a wall. Every 3D frame then
passes through, in order:

1. the room's light — a picture in a dim room is a dim picture;
2. the locale's own PostProcess (layer 50: ascii_render / demoscene_post /
   the mood's quads);
3. THE PAINTED PASS (`painted_scene.gdshader`, layer 90) — it flattens the
   frame into 4 px watercolour washes (wash 0.85), stepped layers,
   blotches, granulation, pooled rims and a paper tooth;
4. the TRIP (`trip_sync.gdshader` on the container): inked aura on edges,
   colour flow in the flats, hue drift, the beat's ripple.

Steps 2–4 treat the picture as any wall: its detail is washed into
regions, its lines inked over, its colours drifted. Nothing knew where the
pictures were on screen.

## Phase 1 · ART CLARITY — the pictures keep their own pixels (this pass)

- **The art mask.** A small second camera, inside the 3D view, renders only
  the pictures (a white twin of each HeroArt quad on its own render layer)
  in step with the main camera. Its texture is a global shader uniform
  (`art_mask`) with a strength (`art_keep`). The painted pass, the
  locale's PostProcess shaders and the trip read it and step back over the
  pictures: the picture keeps its own detail and colour, the room around
  it stays painted. The pictures are never wholly unpainted (a little wash
  and the paper tooth stay, so they sit in the world, not on it).
- **Pictures light themselves a little.** Every picture gets a soft
  emission from its own image (`ART_SELF_LIGHT`): a dim room no longer
  turns a poster to mud; a lit room is unchanged.
- **Gate:** render a stand-in picture in a dark room and a lit room, mask on
  and off (TripPaintTest `--art-mask 0/1`); the picture's edge detail
  (Laplacian energy) inside its rect recovers ≥ 60 % of the unpainted
  render's.

## Phase 2 · THE DIRECTOR FEATURES THE ART (this pass)

- **Art focus.** While the camera holds on a picture (a noticing shot, a
  stillness piece, an insert the art answers), `art_focus` rises: the
  picture is fully clear, the room around it softens a step further and
  darkens at the frame's edges — a rack focus without a lens. It eases in
  and out with the shot, never cuts.
- **Closeups and wides with art in frame.** When a picture fills a useful
  part of the frame (the mask's coverage), it keeps its clarity and gets a
  gentle lift; a closeup whose background holds a picture keeps that
  picture readable behind the face.
- **More noticing.** A line that names a picture by any of its object
  words, its name's nouns or its category ("the poster", "the painting",
  "the photograph") notices it; the cooldown drops from 6 to 4 lines; a
  room's most important picture (`inspect`) is offered once on arrival if
  the establishing frame holds it.
- **Gate:** the VnLineShot engine test over a chapter that names its
  pictures (every naming line shows the picture with focus up, the next
  line returns).

## Phase 3 · THE TRIP, chapter by chapter

- **Re-read the direction.** `trip_direction.json` was built from word
  counts. Read every chapter's level and register against its prose
  (vols 1–7, in order) and lock the ones a reading changes ("locked":
  true survives a rebuild). Priorities: the death and hospital chapters
  (plain), the vision and concert chapters (swelling), the domestic
  mornings, vol 7's cedars.
- **New effects where the writing calls for them** (TripSync, no per-mesh
  shaders):
  - THE VOID — the substrate's holes (LocaleVoid: unlit black, starfield,
    a rim shimmer; shipped 2026-11-08 on the Sanderling patch). Next: the
    rim's colour from the scene's register; stars drifting on the beat.
  - MEMORY — a remembered scene (flashback cue) as a slightly overexposed
    print: lifted blacks, warm cast, soft halation on lights.
  - BROADCAST — the radio and TV scenes (WGUR, the editing suite): a
    slow scan-band of brightness and chroma offset on lit screens only,
    current-hardware clean (no retro cosplay: no scanline loops).
  - ART BREATH — a picture in focus breathes with the music: its
    clarity edge carries a faint aura of the register's hue (Phase 2's
    focus, set to the beat).
- **Gate:** trip_direction_audit (exists) + a per-volume contact sheet of
  each chapter's opening frame at its directed level.

## Phase 4 · SETS: textures and geometry

- **Done this week (passes 306–309):** 1,080 picture rows on their faces
  and facing out (hero_art_placement_audit --gate at 0); signs out of
  roofs (sign_roof_audit at 0); contents through boards (PIERCE) and
  details inside solids (BURIED) in prop_overlap_audit at 0; Meadowlark's
  lawns; the Sanderling void.
- **Outstanding:**
  - the 170 COVERED reads (most natural; the structural ones read one by
    one — the Caldwell porch's wall over the facade picture);
  - ~~the 14 DUPLICATE window pairs~~ — picked 2026-11-09 (pass 311: the
    Missing Link and the hospice split by time of day, the rest one each);
  - the Deck read of every rebuilt set WITH the installed pictures (this
    container has none): a contact sheet per preset, read against the
    audits;
  - the 21:9 frame: the side-band scan is clean (no void, no looking past
    walls); next, the markers' inserts at 21:9 (subjects that drift off
    the wider frame's centre).
- **Gate:** the full suite (`run_all_audits.sh`).

## Phase 5 · PORTRAIT DIRECTION

- **Shipped:** portraits ease between shots (Portrait3D `SHOT_EASE_S`); an
  idle cast member steps out after 6 lines (`PORTRAIT_IDLE_LINES`); the
  insert-quiet dim (0.32, eased).
- **Outstanding:** speaker-side staging (the speaker on the side the
  camera's eyeline favours, not the slot it entered on); a speaker's
  portrait held through a short reply instead of swapping; portraits
  stepping back while a picture is in focus (Phase 2's art focus: the cast
  dims as the picture rises); the band offsets read on the Steam Machine
  at 21:9.
- **Gate:** the VnLineShot engine test over a busy chapter, checking the
  CAST log for pops (a portrait in and out within 2 lines).

## Status (2026-11-09, end of the night)

- **Phase 1 — draft 1 shipped.** ArtMask + the four passes + self-light.
  Measured: picture edge detail 58 % → 91 % of the unpainted render (99 %
  under focus). Draft 2: the Deck read with the installed pictures; tune
  KEEP (0.78) and ART_SELF_LIGHT (0.22) per register if lit rooms bloom.
- **Phase 2 — draft 1 shipped.** art_focus on every art shot; ambient focus
  (0.35) when a picture is prominent; category words; cooldown 4. Engine-
  tested (vol6_ch1_bedroom 13 notices the window view). Draft 2: the arrival
  glance; a closeup that composes a picture behind the face on purpose.
- **Phase 3 — draft 2 shipped.** Draft 1: registers memory / broadcast /
  vigil; ART BREATH; the void on the beat. Draft 2 (pass 313): vol 7's and
  vol 6's flagged scenes read, 16 locks; the Bill-is-a-bill scorer bug. Draft
  3: the rest of vol 7 in full, then vol 5 → 1; MEMORY for named flashbacks.
- **Phase 4 — continuous.** All gates at zero except as noted in the roadmap.
- **Phase 5 — draft 2 shipped.** Draft 1: 76 flickering staging nodes retired
  in place (pops 55 → 39, jumps 36 → 32). Draft 2 (pass 312): portraits SLIDE
  between slots and a leaving portrait is held 2 lines (jumps 32 → 4, 43
  slides); `hide center` works on 3D sets. Draft 3: the 84 one-line
  appearances read by hand (portrait_motion_audit.py); speaker-side staging.

## Order of work

1. Phase 1 + Phase 2 (this pass: the renderer and the director).
2. Phase 3 chapter re-read, vol 7 → vol 1 (the user's current reading).
3. Phase 5 portrait staging.
4. Phase 4's outstanding reads, continuously, with every rebuild.
