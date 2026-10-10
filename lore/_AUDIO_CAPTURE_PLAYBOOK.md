# AUDIO CAPTURE PLAYBOOK — tape, field recording, and getting sound into the game

How FIELD RECORDER, TAPE STUDIO and `field_ingest.py` record, process
and deliver audio, and how that audio reaches Godot. Read before
touching `godot/tools/audio_kit.js`, `field_recorder.html`,
`tape_studio.html`, `field_ingest.py`, or `AudioMgr._load_audio`.

## Core rules

### The music catalog is generated — never hand-edit it

`godot/resources/music_catalog.json` is exported from
`project/vn-music.jsx` by `tools/export_music_catalog.py`. A manual edit
is overwritten on the next export. Audio reaches a catalog track by
writing a file at the track's own `src` path, never by editing the
catalog:

- `<src without extension>.wav`. `AudioMgr._load_audio` falls back from
  a missing `.ogg` / `.mp3` to the same basename with `.wav`. This is
  what FIELD RECORDER, TAPE STUDIO and `field_ingest.py fill` write.
- or the real `.ogg` / `.mp3`, via `field_ingest.py fill --convert`
  (needs ffmpeg).

As of 2026-10-10, 173 of 179 catalog tracks have no file. The "wanted"
list (`AK.game.wanted()`, `field_ingest.py wanted`) ranks them by how
much their brief reads like a field recording.

### WAVs we write carry everything in chunks

`AK.wav.encode` writes:

- `fmt `
- `bext` (BWF: description, date, time, originator)
- `LIST/INFO` (INAM, ICMT, IKEY, ICRD, ISFT)
- `smpl` (one forward loop)
- `cue ` (markers)
- `mmjs` (our metadata as JSON: locale, tags, gps, forTrack…)
- `data`

`field_ingest.py` reads all of these plus recorder `iXML`.

### `smpl` loop points ARE the in-game loop

Godot 4.6's `AudioStreamWAV.load_from_buffer` (the path AudioMgr uses
for files without an `.import` sidecar) reads `smpl` and sets
`loop_mode = LOOP_FORWARD` with our begin / end. This was verified
headless: a 2 s loop came back as `loop=0..95999`. A seamless loop made
in FIELD RECORDER (equal-power head→tail crossfade, `AK.dsp.loop`) or a
TAPE STUDIO print (an exact multiple of the loop length) therefore loops
in-game with no seam, and needs no import settings.

### Raw input or nothing

`AK.inputs.open` turns off `echoCancellation`, `noiseSuppression` and
`autoGainControl`. Chrome's voice-call defaults pump, gate and EQ
ambience into mush. FIELD RECORDER's input hint warns if the browser
kept any of them on.

### Capture is always on

`AK.Capture` runs an AudioWorklet loaded from a Blob URL (works from
file://), with a ScriptProcessor fallback. It keeps a rolling pre-roll
ring, so REC can include up to 30 s from before the button press. Field
recording is mostly missed moments.

### One library, every tool

IndexedDB `mm_audio` has three stores:

| Store | Holds |
|---|---|
| `takes` | Metadata only, so listing stays cheap. |
| `pcm` | `Float32Array[]` per take, plus TAPE STUDIO's `tape:N` slots. |
| `kv` | The project and the linked folder handle. |

A `BroadcastChannel('mm_audio')` refreshes other open tool pages.
file:// pages share one origin in Chrome, so FIELD RECORDER sees TAPE
STUDIO prints and the reverse is true too (tested).

### Game folder via File System Access

`AK.game.link()` asks for the repo or `godot/` folder once. The handle
is kept in IndexedDB. After a restart, Chrome needs one click to
re-grant permission (the badge says so). Without it, every tool falls
back to downloads plus `field_ingest.py ingest ~/Downloads` (the JSON
sidecars carry locale and forTrack).

### Tape engine lives in a worklet

TAPE STUDIO's `mm-tape` processor owns the eight loop buffers. It plays
them, records into armed tracks sample-accurately, and makes the click.
Its rules:

- Recording writes at `pos − latency` (round-trip estimate from
  `baseLatency + outputLatency + track latency`, nudgeable).
- Overdub is `old × keep + in`, which gives the KEEP slider as tape-loop
  decay.
- Track FX are ordinary Web Audio nodes on its eight outputs.
- The click is a ninth output wired straight to the speakers, so it is
  never printed or resampled.

### MIDI clock is scheduled, not timed

Clock ticks go out with `output.send(bytes, timestamp)` from a 20 ms
look-ahead loop. The audio→performance clock mapping comes from
`ctx.getOutputTimestamp()`. 24 PPQN; Start at the tape's first frame
(after count-in), Stop on stop.

## Recent lessons

### 2026-10-10 — the recording suite (first pass)

- `AK.lib.put({id: undefined, …})` overwrote the generated id and
  IndexedDB rejected every first save silently. The status line only
  said "library save failed". Guard every keyPath field against
  `undefined` and test the save path end to end.
- `AudioStreamWAV.load_from_buffer` on a truncated file returns an
  EMPTY stream, not null. AudioMgr now treats `get_length() <= 0` as
  unreadable and caches the skip.
- The old raw-WAV branch assigned the file bytes to `.data`, so a
  dropped-in WAV played its header as 8-bit noise. It now uses
  `load_from_buffer`.
- Spectral gate: at 6 dB sensitivity white noise only dropped about 8 dB,
  because Rayleigh peaks kept the gate open. At 10 dB it drops about 15 dB
  with a 1 kHz tone untouched, so 10 is the default.
- Headless testing that worked:
  - Chromium with `--use-fake-device-for-media-stream
    --use-fake-ui-for-media-stream` for the mic.
  - OPFS (`navigator.storage.getDirectory()`) as a stand-in for the
    linked game folder.
  - The real Godot 4.6 binary on a scratch project (stub Settings,
    SaveSystem and SceneDataDB autoloads) for AudioMgr.
- Recorders write 24-bit and 32-bit float. `field_ingest.py` converts to
  16-bit with TPDF dither by default: smaller, and safe on every Godot
  build. `--keep-bits` opts out.
- Not done yet:
  - Latency is estimated, not measured (no loopback calibration).
  - The shredder is live-only. It is captured by PRINT and absent from
    STEMS.

### 2026-10-10 — DAW, and worklets on file://

- On a file:// page Chrome REFUSES a Blob-URL AudioWorklet module
  (`blob:null/…`, "Unable to load a worklet's module"), and data: URLs
  load. TAPE STUDIO shipped broken on the Deck because of this, and
  AK.Capture had silently fallen back to ScriptProcessor. Always load
  through `AK.addWorklet(ctx, src)`, which tries data: first and Blob
  second.
- Headless tests launched with `--allow-file-access-from-files` HID that
  bug. Run browser tests WITHOUT it: the Deck's Chrome doesn't have it.
- Top-level `const` / `class` in a classic script is script-scoped, not
  `window.X`. `audio_kit.js` (AK), `midi_input.js` (MidiInput) and
  `smf.js` are reached by bare name. `daw_engine.js` resolves globals
  through a small `G` getter that tries the bare name, then `window`.
- The DAW (`daw.html` + `daw_engine.js`, notes `{t,d,n,v}` at PPQ 96,
  the same as `seqgen.js` / `smf.js`):
  - Timing: a 25 ms timer schedules 120 ms ahead.
  - Bounces run in real time, because emulators and hardware can't
    render offline.
  - A loop bounce plays the region twice and keeps pass two, so tails
    wrap and the loop is exact-length and seamless. It is written with
    WAV loop points for Godot.
- KIT one-shots must release after their preset's attack + decay. A
  fixed 50 ms gate cut the kick's 0.5 s tail.
- Five generated parts at unity strips hit 0.999 into the limiter.
  Generated tracks start balanced (drums 0.62 … pad 0.36), leaving about
  1 dB of headroom.
- MIDI export puts drums on GM ch10 unless the track is routed to an
  emulator or hardware channel.

## TEMPLATE

```
### YYYY-MM-DD — <one-line summary>

- <lesson>
- <lesson>
```
