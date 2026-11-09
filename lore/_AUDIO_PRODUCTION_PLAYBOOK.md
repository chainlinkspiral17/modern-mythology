# Audio Production Playbook

Rules for dialogue, SFX and music production · the Sound Studio
(`godot/tools/sound_studio.py`), the generation hooks
(`godot/tools/sound_gen.py`), and the data contract between them and
the game.

Read this before touching voice wiring, `music_catalog.json`,
`sfx_catalog.json`, the audio library layout, or any generation hook.

## Core rules

### A slot is the unit of work; the catalogs are the truth

Everything that needs audio is a **slot** with one fixed place the
game loads it from:

| Lane | Slot list (source of truth) | Game path |
|---|---|---|
| Dialogue | every `narrate` / `say` / `think` node with text, in `godot/resources/scenes/vol*/*.json` | `assets/audio/voice/<scene_id>/<NNN>.<ext>`, wired by the node's `"voice"` key |
| SFX | `godot/resources/sfx_catalog.json` | the entry's `src` |
| Music | `godot/resources/music_catalog.json` | the entry's `src` |

A slot is **outstanding** until a file exists at its game path (and,
for dialogue, the `voice` key points at it). `sound_studio.py
--status` prints the count; never hand-maintain a list of what's
missing.

### The library holds candidates; only assignments are committed

`audio_library/` (repo root, outside the Godot project) holds takes,
effects, tracks and scores. It is git-ignored except `scores/`.
**Assign** copies or transcodes one candidate to the slot's game
path. That copy, plus the scene JSON's `voice` key, is what gets
committed. Raw takes never enter git history.

Folder names do the linking: `takes/<scene_id>/NNN_*`,
`sfx/<slot_id>/*`, `music/<track_id>/*`, `scores/<track_id>/*`.

### NNN is the node index, so never insert nodes into a voiced scene

Voice files are named by the node's position in the scene's `nodes`
array. Inserting or deleting a node above a voiced line shifts every
later index: wired lines keep working (the `voice` key stores an
explicit path) but the take folders and any unwired files now point
at the wrong lines. Add SFX cues to a scene only after its dialogue
is locked, or append rather than insert.

### Godot plays ogg, mp3 and wav. Nothing else.

Browser mic recordings are webm/opus, which Godot cannot import (the
old `voice_studio.html` exported them anyway). The studio converts
mic takes to 16-bit mono WAV in the browser and transcodes anything
else through ffmpeg at assign time. Music and SFX slots have a fixed
extension because code and catalogs reference the full path; the
studio converts to match rather than editing the reference.

### Commit before `update.sh`

`update.sh` runs `git stash -u` before pulling. Untracked, *non-ignored*
files are stashed: that includes freshly assigned audio under
`godot/assets/audio/` and patched scene JSON. The library survives
(it is ignored). The studio's header shows an "uncommitted audio
changes" chip with the exact commit command; use it before updating.

### Music hooks: compose, render, generate are separate stages

- **Compose** produces a *score* (`mm-score/1` JSON, or a `.mid`).
  Claude via the API, any Claude Code session writing the file by
  hand, another LLM through a command hook, or a DAW export.
- **Render** turns a score into audio: the builtin synth, FluidSynth
  with a SoundFont, or a command (which may hand the sketch to an
  audio-to-audio model).
- **Generate** skips MIDI: a text-to-audio model returns finished
  audio (ElevenLabs music / SFX / speech, or any HTTP endpoint or
  command in `sound_providers.json`).

Keys are never written to `sound_providers.json`; reference them as
`${ENV_VAR}`. New outside models are added as config, not code.

### Honest ceiling of the builtin renderer

The builtin synth is additive / FM / Karplus-Strong voices plus
synthesised stand-ins for field recordings (noise bed, rain, cicadas,
hum, crackle), a convolution reverb and a loudness pass to the
canon's -16 LUFS. It produces a coherent, loopable ambient cue that
fits the project's restrained brief. It does not sound like sampled
instruments or a real room. For that, render the same `.mid` through
FluidSynth with a good SoundFont, realise it in a DAW, or use an
audio model. Say so rather than promising more.

## Recent lessons

### 2026-11-09 · Sound Studio + generation hooks built

First pass of a unified studio replacing the per-scene zip workflow
of `voice_studio.html` and the catalog-only `music_studio.html` for
assignment work. 15,726 voiceable lines (329 voiced), 179 catalog
tracks (6 with files), 18 SFX slots (1 with a file) at the time.

- **A model composing blind needs a mix report.** The first render of
  the worked example had the pad 14 dB over the piano and nothing in
  the output said so. `render` now prints per-track level relative to
  the loudest track; rebalance from that. A four-note pad chord sits
  about 12 dB above a single piano note at equal gain.
- **Scene files come in two encodings.** 55 of 312 scene JSONs were
  written with `ensure_ascii=True`, the rest with literal Unicode;
  some end in a newline, some don't. Patching a `voice` key must
  re-serialize in the file's own style (`dump_like`) or the diff
  rewrites every em dash in the chapter.
- **"Has a file" is not "done".** `vol1_ambient.mp3` is an 8 KB,
  two-second stub that every status report counted as finished. The
  studio flags music files under 48 KB as placeholders.
- **SFX slots that no script plays are invisible work.** Five of the
  seventeen prompts in `music_studio.html` (back, unlock, scene
  advance, choice appear, VN-side lore token) point at paths no code
  references, and `click.wav` exists but nothing plays it. The studio
  greps scripts for each `src` and labels the slot, so assigning a
  file isn't mistaken for hearing it in game.
- **mp3 is the library format, ogg the game format.** The user asked
  for mp3s and renders default to mp3; most catalog slots are `.ogg`,
  which also loops gaplessly where mp3 does not. Assign transcodes.
  For a seamless loop, render with `--format ogg` to skip the second
  lossy pass.
- **Untested against live services.** The Claude hook was verified
  against a mock of the Messages streaming API (request shape accepted
  by the SDK, score parsed and rendered); the ElevenLabs music and SFX
  endpoints were written from memory with the docs unreachable. Both
  are config in `sound_providers.json`; fix them there if a request
  is rejected.

## TEMPLATE for new "Recent lessons" entry

```
### YYYY-MM-DD · <one-line title>

<one-paragraph situation>

- **<Bolded principle>.** <two-to-three-sentence explanation.>
- **<Bolded principle>.** <two-to-three-sentence explanation.>
- **<Bolded principle>.** <two-to-three-sentence explanation.>
```
