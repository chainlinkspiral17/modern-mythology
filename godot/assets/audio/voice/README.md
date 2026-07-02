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

# Whole volume
python3 tools/voice_manifest.py --vol 5 --format csv > vol5_all.csv
```

CSV columns: `scene_id, node_index, kind, char, file, text`. The
`file` column is the exact relative path the engine will look up.
`char` is `_narrator` for narration nodes.

**2a. Record yourself.** Drop files into the matching paths. Anything
Godot can import works — `.ogg` is smoothest.

**2b. Or render via ElevenLabs:**

```bash
export ELEVENLABS_API_KEY=sk_...                          # one-time

# Map characters to voice IDs (one-time)
$EDITOR tools/voice_map.json

# Dry-run to preview cost / coverage. No API calls.
python3 tools/elevenlabs_render.py vol5_ch0_booth6 --dry-run

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
Skips lines whose target file already exists unless `--overwrite`.
`_narrator` is used for every `narrate` node.

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
