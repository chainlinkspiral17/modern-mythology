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

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
