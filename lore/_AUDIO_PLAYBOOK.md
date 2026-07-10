# Audio playbook

Hard-won rules for authoring, rendering, and wiring audio in the
Modern Mythology project. Companion to `godot/tools/audio/` (the
tool) and `godot/tools/audio/AUDIT.md` (the inventory).

## Core rules

### The audit is the map. Keep it up to date.

`godot/tools/audio/AUDIT.md` is the single source of truth for
what sound goes where. Every slot is tagged one of:

- `[existing]` · already in the repo pre-audio-arc
- `[preset]` · covered by a `slowstick_synth.py` SFX preset,
  rendered to disk
- `[rendered]` · a JSON composition rendered to a WAV
- `[compose]` · a BGM slot that needs authoring
- `[new]` · a preset needs to be added to `slowstick_synth.py`
- `[defer]` · authored intent captured, no wire-up yet

When you add or wire a sound, flip the tag in the same commit.
The tag mismatch is where audio drift begins.

### Two synthesis engines · Python + JS · always in sync.

`godot/tools/audio/slowstick_synth.py` is the reference. Every
preset there has a line-for-line JS twin in
`godot/tools/audio/importer.html` so a composer can drop a
`.mid` or `.json` into a browser tab and audition instantly
without touching the Deck. When you add a Python preset, port
it. When you can't (JS has different math semantics · e.g.
Python's negative modulo), leave a comment in both files.

### `SFXBank` is the ONE way to play short SFX.

`godot/autoload/SFXBank.gd` owns a small pool of
`AudioStreamPlayer` nodes and a preset-name → path map. Every
gameplay callsite goes through `SFXBank.play("preset_name")`.
This gives:

- **Overlapping playback** for bursts (verb select + customer
  bell + phone ring can all fire in the same second).
- **Once-warned missing files** so a mis-authored preset name
  doesn't spam the log.
- **Central volume control** via `Settings.sfx_vol`.

Do not `AudioMgr.play_sfx(path)` directly except from
`_audio_sfx()`-style legacy compat helpers that route through
the bank when a mapping exists.

### BGM belongs to `AudioMgr.play_bgm(path)`. Only one at a time.

BGM is exclusive · every controller that has a musical bed
calls `AudioMgr.play_bgm(...)` in its `boot()` or state-change
site. `AudioMgr` handles the cross-fade and format detection.
Don't try to play two BGMs at once · they'll collide on the
Music bus.

### Preset names are namespaced but flat.

Every preset name is a single string with no dot-nesting
(`tier_crossing_hungry`, not `cp.tier.crossing_hungry`). Files
live under `godot/assets/audio/sfx/<system>/<name>.wav` where
`<system>` is `e3` / `cp` / `gauntlet` / `ui`. The `SFXBank`
map handles the folder resolution; the callsite never touches
the folder.

### Composition-JSON is the authoring surface, not code.

A BGM loop lives at `godot/tools/audio/compositions/*.json` as
a tempo + tracks + notes structure. The Python tool renders it
to a WAV; Godot loads the WAV via `AudioMgr.play_bgm(...)`.
Don't hand-write raw WAV; don't try to synthesize live in
Godot. The Python round-trip is deterministic and diff-friendly.

### `_formant_voice` for anything word-shaped.

If the game needs a syllable that reads AS speech (the night-12
"sam." beat), use the 3-formant bandpass source-filter synth in
`_formant_voice()` inside `slowstick_synth.py`. Feed it three
formant breakpoints. Don't try to record TTS or fake vowels
with sine waves alone. The formant math is small (~40 lines);
the result is intelligible-enough with 30% static overlay.

## Recent lessons

### 2026-07-08 · closing the audit · 94-slot SFX arc from zero to 96/96

The audio arc landed nine wave-commits (A · C · D · gauntlet
wire-up · B · E · F · Wave B tail · Wave A itself). Went from
2 existing audio assets to 96 shipping slots · 82 SFX presets ·
12 rendered BGM compositions · every player-facing moment in
Estuary 3 and every state-change in CP has authored sound.

Lessons:

- **The audit is the plan.** Writing `AUDIT.md` first · listing
  every audio slot the game needs, keyed by act and moment ·
  turned the 96-slot commitment from "author until we run out
  of time" into "author until this file says green everywhere."
  Every wave-commit's diff was legible against the audit:
  which rows flipped from `[new]` to `[preset]`, which stayed.
  Without the audit we'd be discovering missing sounds in
  playtest for months.
- **Wave-based dev order gives huge leverage.** Wave A (10
  presets covering the six most-audibly-obvious UI moments)
  unblocked the entire loop's sense of "this game reacts to
  me." Wave B (BGM) came in second because a game with buttons
  clicking still feels dead if the music slot is silent. Wave
  C (CP demon-depth) came last of the gameplay waves because
  the CP demon economy was already legible without audio · the
  audio just added texture. Sequence by "how much dead silence
  is this wave removing?"
- **Small preset functions are the unit of authoring.** Every
  SFX preset is a ~10-30 line function that returns a
  `list[float]`. This shape is:  (a) trivially portable to JS
  for the importer, (b) trivially testable (pipe through
  `write_wav()` and open the file), (c) trivially auditable
  from the audit doc. Bigger units (multi-envelope samplers,
  patch-based synth voices) would sprawl. Fight the temptation.
- **Route legacy call sites through a central compat map.**
  `TarotGauntletGame._audio_sfx()` was already calling out to
  `_SFX[key] → AudioMgr.play_sfx(path)` at 12 sites. Adding an
  `_SFX_BANK_KEYS` compat map · one dict lookup at the head of
  `_audio_sfx` · picked up eight of those 12 sites for
  overlapping-pooled Wave-D playback with zero call-site
  changes. Never rewrite legacy call sites when a compat map
  works.
- **The importer.html is worth the porting cost.** JS port of
  the Python synth is ~1,000 lines and needs to be re-touched
  every wave. But: the composer can audition presets in a
  browser tab (Deck's Firefox works) with no `.wav` roundtrip.
  Any preset added to Python gets a JS twin in the same
  commit. The parity discipline is what keeps the two engines
  reconciled; a stale importer is a broken importer.
- **Formant synthesis is a small ceiling but a real one.** The
  night-12 "sam." beat took ~40 lines of source-filter synth
  and now the game has a distinctive human-speech-shaped beat
  that no other slowstick would try. When a sound genuinely
  wants to be a word, don't ambient-noise around it · do the
  math.

### 2026-07-08 · three-layer audio stack · BGM + ambient + SFX

Pirate Summer ships its audio in three cooperating layers.
Each layer answers a different question about the moment:

- **BGM** answers *what does this place feel like right now.*
  Six per-zone compositions (cabin_warmth, camp_daytime,
  alder_pond_water, caves_echo, campfire_evening,
  ghost_ship_forever · 42-90s loops), played via AudioMgr,
  swaps on zone-change.
- **Ambient** answers *what does the world do while you stand
  there.* Five one-shot loops (waves_lap, spruce_wind,
  campfire_crackle, ghost_moan, heron_call) fire every 15-45s
  on top of the BGM via a dedicated AudioStreamPlayer + a
  SceneTreeTimer that reschedules itself.
- **SFX** answers *what did you just do.* SFXBank presets from
  the existing library trigger on interactions (fact discovery,
  pickup, dialogue open, chatter appear, story beat, zone
  transition, day advance).

Lessons:

- **BGM is the room · Ambient is the world · SFX is the verb.**
  Once separated this way, mixing gets easy · BGM sits at
  base loudness, ambients duck slightly under it (~-12 to
  -14 dB), SFX one-shots peak briefly through everything.
  A single loud one-shot on top of a quiet room-tone reads
  as an event without breaking the atmosphere.
- **Author ambient loops as short compositions, not as one-off
  WAVs.** waves_lap.json is a 6-second rain-instrument note
  over a low drone.  ghost_moan.json is a 12-second D1 drone
  plus a fluorescent hum plus two soft-sine bells.  Each
  authored as a slowstick_synth JSON.  Regenerating them from
  edits is one command.  Compared to sourcing royalty-free
  WAVs, this discipline scales: the pipeline is the same as
  BGM, the review is the same as BGM, and the vibe is
  consistent with the rest of the game's sound.
- **Re-use existing SFX presets before authoring new ones.**
  Pirate Summer's SFX wire-up added zero new preset functions
  · it just wired existing register_ding, pickup, customer_
  bell, boot, season_settle, tile_hover, door_open into new
  trigger sites.  The estuary 3 audit pool was designed to
  be re-usable; use it before extending it.

### 2026-07-09 · ff/em roots · scoring two slowsticks in one wave

Fey Faire and Earthman Chronicles went from silent to fully scored
(6 BGM compositions, 6 ambient one-shots, 30+ SFX call sites) in
one session.

- **A slowstick's score is three layers, added in this order: BGM
  bed → moment SFX → ambient one-shots.** BGM via host-level
  `_play_bgm()` calls at scene-routing points (AudioMgr crossfades
  and dedupes, so calling on every route is safe). Moment SFX from
  the existing shared preset registry FIRST — win_chord /
  threshold_cross / basement_rite covered 18 moments with zero new
  WAVs. Only author new presets for sounds that are place-specific
  (calliope_drift, kyrindi_bell).
- **Ambient one-shot loops: self-terminating timer chains.** A
  `_schedule_ambient()` that plays a preset, then
  `create_timer(interval).timeout.connect(self)` — with an
  `_ambient_alive` flag flipped in `_exit_tree()`. SceneTreeTimers
  outlive freed nodes; without the flag the chain keeps firing
  into a dead scene.
- **Per-root SFXBank folders keep the registry auditable.** New
  games get their own root ("ff", "em") rather than piling into
  e3/. The PRESET_MAP stays the single registry the audit doc
  reads.
- **Cross-slowstick preset reuse is a lore tool.** Earthman's
  Working VII fires basement_rite — the same sting Community
  Planned uses for its basement rituals. Players who know both
  games hear the rhyme. Reuse on purpose, not just for thrift.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
