# Voicelines

Voice playback is already wired in `GameEngine` + `AudioMgr`. Every
`narrate`, `say`, and `think` node optionally takes a `"voice"` key
pointing at an audio file. While a voice line is playing, the BGM
ducks to 32%; when it ends, auto-advance progresses to the next node.

## Drop-in convention

Audio files live at:

```
assets/audio/voice/<scene_id>/<NNN>.<ext>
```

- `scene_id` — the scene's `id` field (matches its JSON filename
  without the extension), e.g. `vol5_ch0_booth6`.
- `NNN` — zero-padded node index within the scene's `nodes` array.
- `ext` — one of `ogg` (preferred), `mp3`, or `wav`.

Example:

```
assets/audio/voice/vol5_ch0_booth6/014.ogg   ← Stranger's "Watch yourself…" line
assets/audio/voice/vol5_ch0_booth6/018.ogg   ← John's "He had not…" thought
```

## Workflow

**1. Generate a recording manifest for the scene(s) you're voicing:**

```bash
# Human-readable list of every voiceable line + its target filename
python3 tools/voice_manifest.py vol5_ch0_booth6

# CSV for handoff to a voice actor / DAW
python3 tools/voice_manifest.py vol5_ch0_* --format csv > vol5_ch0.csv

# Spoken lines only, skip narration
python3 tools/voice_manifest.py vol5_ch0_* --kind say think

# Whole volume, in index.json play order (best for a session)
python3 tools/voice_manifest.py --vol 1 --format csv > vol1_all.csv

# Meld scenes / the Vol 5 prelude (incl. Whispers from the Liminal)
python3 tools/voice_manifest.py 'meld_*'
python3 tools/voice_manifest.py 'vol5_prelude_arcana_*'

# Per-volume coverage: lines, wired, audio on disk, uncast characters
python3 tools/voice_manifest.py --coverage
```

Every `resources/scenes/vol*/*.json` with `id` + `nodes` counts as a
scene, so `meld_*` files are included. CSV columns: `scene_id,
node_index, kind, char, file, text, voice_key`. The `file` column is the
exact relative path the engine will look up; `voice_key` is the
`voice_map.json` key the line resolves to.

**Character keys.** Names are normalised the same way everywhere
(`tools/voice_common.py` `char_key()` = `voice_studio.html` `charKey()`):
lowercase, `(...)` suffix stripped, apostrophes dropped, other
punctuation → `_`. So `Dickens Dean` → `dickens_dean`,
`Olivia (alternate)` → `olivia`, `The Frog`/`the_frog` → `the_frog`.
Then `voice_map.json` applies `scene_aliases` (per-scene, e.g. the
vol1 dream "Woman" is Joan), `aliases`, and `_walkons` (shared generic
voices for one-liners). Multi-speaker lines (`Faust, Jacob, Wagner`) →
`_chorus`, which falls back to the first named speaker with a voice.

**Narrators.** Narration (and char-less `think` lines) resolves to
`_narrator_vol{N}` from the scene's `vol` field, or
`_narrator_whispers` for `vol5_prelude_arcana_ep*`. Lookup falls back
`_narrator_vol{N}` → `_narrator`; `_narrator_vol5` is an alias of
`_narrator`.

**2a. Record yourself.** Drop files into the matching paths. Anything
Godot can import works — `.ogg` is smoothest.

**2b. Or render via ElevenLabs:**

```bash
export ELEVENLABS_API_KEY=sk_...                          # one-time

# Map characters to voice IDs (one-time). Each entry has a "casting"
# brief to cast from.
$EDITOR tools/voice_map.json

# Dry-run: no API key, no ffmpeg, no network. Shows each line's voice
# key and flags keys that still lack a voice_id.
python3 tools/elevenlabs_render.py --vol 1 --dry-run

# Render a small test batch first
python3 tools/elevenlabs_render.py vol5_ch0_booth6 --limit 3

# Render the whole scene
python3 tools/elevenlabs_render.py vol5_ch0_booth6

# Spoken lines only (skip narration)
python3 tools/elevenlabs_render.py vol5_ch0_* --kind say think

# Re-render a single line (e.g. you tweaked voice_settings)
python3 tools/elevenlabs_render.py vol5_ch0_booth6 --node 14 --overwrite
```

The renderer reads `tools/voice_map.json` for the character → voice_id
mapping, calls ElevenLabs TTS (model `eleven_v3` by default,
configurable via `--model`), pipes PCM through local `ffmpeg` to
produce `.ogg`, and saves at `assets/audio/voice/<scene_id>/NNN.ogg`.
Skips lines that already have audio (`.ogg`, `.mp3` or `.wav`) unless
`--overwrite`. Narration uses the per-volume narrator described above;
a character with no `voice_map.json` entry at all falls back to the
narrator, but one with an empty `voice_id` is reported as missing.

`tools/voice_studio.html` can **Import voice_map.json** (ElevenLabs
panel) so the browser studio uses the same voice_ids, aliases and
narrator rules.

Requires the `ELEVENLABS_API_KEY` env var and `ffmpeg` on PATH.

**3. Wire the scene JSONs:**

```bash
# Preview what would change
python3 tools/wire_voicelines.py vol5_ch0_* --dry-run

# Actually inject "voice" keys into the matching nodes
python3 tools/wire_voicelines.py vol5_ch0_*

# Replace previously-wired voice keys
python3 tools/wire_voicelines.py vol5_ch0_* --overwrite
```

The tool walks `assets/audio/voice/<scene_id>/`, parses the numeric
filenames, and adds `"voice": "<path>"` to the matching node in the
scene JSON. Existing `voice` keys are kept by default — pass
`--overwrite` to replace them.

**4. Reimport in Godot.** Open the editor (or run `--editor --quit`
headless) once so Godot picks up the new audio. Play the scene; the
line auto-advances when the audio finishes.

## Shipping

Voice files are bundled with the project zip and the Core .pck like
any other asset. If voice grows large enough to bust the 30 MB ship
budget, split them out as a separate "voice" .pck via
`export_presets.cfg` and load it additively at boot with
`ProjectSettings.load_resource_pack("user://packs/mm_voice.pck")`.

## Audio settings

- Bus: `Voice`. Volume tracked by `Settings.voice_vol`.
- BGM auto-ducks to 32% while voice plays
  (`AudioMgr.DUCK_RATIO`, `DUCK_FADE`).
- Auto-advance waits on voice completion before moving to the next
  node (`GameEngine._process` checks `AudioMgr.is_voice_playing()`).
- Voice stops cleanly on scene-end, in-game menu open, and the
  player pressing Advance to manually skip.
