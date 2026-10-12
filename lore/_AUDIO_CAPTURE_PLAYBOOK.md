# AUDIO CAPTURE PLAYBOOK — tape, field recording, and getting sound into the game

How FIELD RECORDER, TAPE STUDIO and `field_ingest.py` record, process
and deliver audio, and how that audio reaches Godot. Read before
touching `godot/tools/audio_kit.js`, `field_recorder.html`,
`tape_studio.html`, `field_ingest.py`, `vendor/oggvorbis/`, or
`AudioMgr._load_audio`.

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
  It is real audio.
- or the real `.ogg` / `.mp3`, via `field_ingest.py fill --convert`
  (needs ffmpeg), or the DAW's BOUNCE → INTO GAME (Ogg).
- a **temp track**: `<src without extension>.temp.ogg`, the last
  fallback (see the next rule).

Lookup order in `AudioMgr._load_audio`: the src → `<base>.wav` →
`<base>.temp.ogg`. Real audio always wins over a temp.

As of 2026-10-10, 173 of 179 catalog tracks have no file. The "wanted"
list (`AK.game.wanted()`, `field_ingest.py wanted`) ranks them by how
much their brief reads like a field recording.

### Temp music goes into the game as small Ogg Vorbis

The user: "I don't want 20 meg minute or two long audio tracks, the
game will get bogged down." A 16-bit stereo WAV is 10.1 MB a minute
per file, and a temp with five stems was six of them.

- Everything the DAW / AUDIO DIRECTOR puts into the game as temp music
  is Ogg Vorbis, written by one function, `AK.game.writeMusic`:

  | File | What |
  |---|---|
  | `<base>.temp.ogg` | the mix, VBR q4: 0.93 MB/min on a 94 s DAW temp |
  | `<base>.stems/<part>.ogg` | stems, VBR q1: 0.19–0.58 MB/min each |
  | `<base>.stems.json` | always written, even with no stems: `temp: true`, `format: "ogg"`, `mix`, `loop`, `loop_offset`, `frames`, `bytes`, `quality` |
  | `<base>.temp.ogg.credits.txt` | only for non-free instruments |

- The `.temp` in the name keeps temp and real apart without reading
  the file. A temp manifest's stems never layer over real audio.
- The encoder is vendored: `godot/tools/vendor/oggvorbis/` holds
  wasm-media-encoders 0.7.0 (MIT; libvorbis/libogg BSD) as ONE classic
  script with the `.wasm` inside as base64, rebuilt by its `pack.py`.
  `AK.ogg` loads it with a `<script>` on first use and compiles it once.
  No network, works on file://. The UMD build's default fetches from
  unpkg: never use `createOggEncoder()`, only
  `createEncoder('audio/ogg', module)`.
- Encoding runs on the page at ~60× real time here (10 s in 0.17 s),
  in 4 s blocks with a `MessageChannel` yield between them (timers are
  throttled in background tabs). Show progress; APPROVE does.
- Review staging (`assets/audio/review/`) stays WAV: it is a working
  area, never shipped. APPROVE decodes the staged WAVs with
  `AK.wav.decode` (sample-exact; `decodeAudioData` resamples to the
  context rate and drops `smpl`) and encodes them one file at a time.
- Older temps are `<base>.wav` titled "(temp)": still recognised,
  revocable, and the AUDIO DIRECTOR's ⇣ SHRINK re-encodes them in place.
- FIELD RECORDER / TAPE STUDIO `.wav` and `field_ingest.py` are
  unchanged: that is real audio.

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

### `smpl` loop points ARE the in-game loop (WAV); the manifest is (Ogg)

Godot 4.6's `AudioStreamWAV.load_from_buffer` (the path AudioMgr uses
for files without an `.import` sidecar) reads `smpl` and sets
`loop_mode = LOOP_FORWARD` with our begin / end. This was verified
headless: a 2 s loop came back as `loop=0..95999`. A seamless loop made
in FIELD RECORDER (equal-power head→tail crossfade, `AK.dsp.loop`) or a
TAPE STUDIO print (an exact multiple of the loop length) therefore loops
in-game with no seam, and needs no import settings.

Ogg has no `smpl`. For an Ogg temp:

- the file is cut at the loop end (`smpl` end + 1), so **the loop end
  is the stream end**;
- the manifest carries `loop: true` and `loop_offset` (seconds, a
  quarter frame past the start so truncating or rounding both land on
  it);
- `AudioMgr._apply_ogg_loop` sets `AudioStreamOggVorbis.loop` /
  `loop_offset` on every Ogg the manifest names (its mix and stems),
  imported or loaded raw. Imported Oggs default to no loop.
- Verified headless (`godot_audiomgr`): Godot reads the exact length
  from the last granule; a 1.5 s temp with a 0.5 s offset loops with
  no restart, gap or click (sine-predictor residual 0.0055 vs 0.17 for
  a 20-frame offset error).
- Chrome's `decodeAudioData` does NOT trim the last page: an Ogg decodes
  up to ~1000 frames long at the end there. Never measure Ogg lengths
  in the browser.

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

### The DAW plays renders; the Deck can't run a whole song live

A busy generated song costs 0.7–1.15 cores of Web Audio. On the
Deck, that load makes Chrome silently lose its PipeWire output: the
context keeps running into a fake sink, and the meters still move.

- ▶ defaults to **PLAY: RENDER** (`E.playAuto` → `playRendered`):
  - the render streams back while it runs;
  - playback starts once the render will stay ahead;
  - the result is cached until the project changes.
- **LIVE** (LIGHT by default) is for keys and recording.
- Offline renders create notes one window ahead from `suspend()`
  callbacks. Never create every note before `startRendering`: the
  render cost goes quadratic.

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

### 2026-10-11 — offline render, mastering, stems, temp tracks

- User asked for temp tracks for the missing catalog music, made with
  the new features: offline bounce, loudness target, adaptive stems and
  undo. 173 of 179 catalog tracks have no audio.
- **LUFS meter bug:** the old `AK.dsp.lufs` built K-weighting from
  Web Audio biquads. A `BiquadFilterNode` highpass takes **Q in dB**,
  so the RLB stage barely cut the bass and bass-heavy mixes read
  3.6 LU loud. It's now plain JS with libebur128's coefficients and
  matches ffmpeg `ebur128` to 0.0–0.1 LU. Check any meter against
  ffmpeg before trusting it.
- **Mastering:** `AK.dsp.master(chs, sr, {lufs, truePeak, stems})`
  applies gain to the target, then a look-ahead limiter, then a
  4×-oversampled true-peak check, iterated.
  - Master to −1.5 dBTP: Vorbis encoding raised peaks ~0.2 dB
    (−1.0 → −0.8).
  - Game music target is −14 LUFS. The existing hand-made tracks sit at
    −12.5 LUFS and clip (+0.6 to +1.3 dBTP).
- **Stems must share the limiter.** Stems mastered with gain alone were
  5 dB quieter than the limited mix. `limitGain()` returns the
  limiter's gain curve. Apply the SAME curve × gain to every stem; they
  still sum exactly to the mastered mix, so the layered version plays
  as loud as the stereo one.
- **Offline render:** `E.renderOffline()` rebuilds FORGE, KIT,
  sampler, DX7 and basic devices inside an `OfflineAudioContext` from
  their live state; sampler AudioBuffers are reused across contexts.
  - About 2.7× real time in the sandbox.
  - Emulators and hardware still bounce in real time
    (`canRenderOffline()`).
  - Seamless loops: fold the tail past the loop end back onto the start
    instead of playing two passes.
- **Adaptive music contract with Godot:**
  - Files: `<src base>.stems.json` holds `{stems: [{name, role, file,
    layer}], mix, bpm, bars, lufs, credits}`.
  - Layers: pad 0, chords 0, bass 0.25, drums 0.5, lead 0.75.
  - AudioMgr builds an `AudioStreamSynchronized` and fades
    `set_sync_stream_volume` per frame (it applies live, verified by
    capture in headless 4.6). Call
    `AudioMgr.set_music_intensity(0..1, fade)`.
  - Any missing stem falls back to the mix.
  - Godot exports `.json` as a resource, so manifests ship.
- **Temp tracks:**
  - The game plays a track once, then the next, so short loop / bed
    forms are repeated to ≥ 90 s.
  - `moodFromText` now scores TONE words for mode and PACE words for
    tempo. It used to send almost everything to "ambient lydian".
  - Seeded per-track instrument pools keep two noir themes from sharing
    every instrument.
  - Headless runs shim `AK.game.exists/readText/write` to node fs
    (`page.exposeFunction`) to write straight into the repo. Then
    `music_encode.py` makes the catalog's real `.ogg` / `.mp3`.
- The temp tracks are placeholders, marked "(temp)" in their WAV / OGG
  titles and manifest. A real file at the same path replaces one;
  delete its `.stems.json` / `.stems/` with it.

### 2026-10-11 — music binaries live in Google Drive, not git

- User rule: "Don't put large music files in GitHub, put them in the
  Google Drive." The four temp tracks (19 MB with stems) were removed
  from the session branch history. Never commit generated or recorded
  audio.
- `.gitignore` covers `godot/assets/audio/**` `*.ogg *.mp3 *.wav
  *.flac`, `*.stems/`, `*.stems.json` and `*.credits.txt`. Audio that
  was already tracked (title theme, Vol 5 beds, voice lines) stays
  tracked until the user decides to migrate it.
- Drive mirrors the repo: `My Drive/ModernMythology/godot/assets/audio/`
  ⇄ `godot/assets/audio/`. This follows the existing convention of
  binaries git-ignored and sourced from Drive (see
  `assets/models/README.md`).
- `godot/tools/music_drive.sh setup | pull | push | status` drives
  rclone:
  - `setup` installs rclone to `~/.local/bin` (falling back to a pinned
    GitHub release) and links Google sign-in once.
  - Copies are `--update` only and never delete on either side.
  - In a sandbox, test with a `type=local` remote via
    `MM_DRIVE_REMOTE` / `MM_DRIVE_DIR`.
- The Drive connector can't carry audio: uploads go inline as base64
  in the tool call, so multi-MB files are impractical. Uploads happen
  from the user's machine (rclone). The connector is fine for folders
  and small text.
- `set -e` doesn't fire inside a function called from `a || b`. Give
  installers explicit `|| return 1` checks.

### 2026-10-11 — the test suite and what it caught on day one

- `godot/tools/tests/run_tests.sh` holds the headless checks that used
  to live in scratch folders. It has 7 suites (see its README) and runs
  in ~4 min offline.
  - Pages open from file:// without the allow-files flag.
  - Any console error fails a suite.
  - Network and slow paths are opt-in (`TEST_NETWORK`, `TEST_SLOW`).
- It found two real bugs the first time it ran:
  - **`AK.dsp.truePeak` was a sample-peak meter.** The browser resamples
    buffers with linear interpolation, which can't exceed the samples
    it joins. It's now a polyphase windowed-sinc 4× interpolator and
    matches ffmpeg (−2.58 vs −2.6 dBTP).
  - **AudioMgr cross-fade race.** If the playing track ended during the
    0.6 s fade-out to a new one, `_on_bgm_finished` restarted the old
    track and the queued `_pending_src` was dropped. The queued track
    now wins.
- The Godot suite builds a throwaway project from the REAL
  `AudioMgr.gd` plus stub autoloads (`tests/godot/`), with fixture WAVs
  written by node. Don't headless-import the real project for checks:
  it scatters `.uid` files and extracted textures that a sandbox can't
  `git clean`.
- `--check-only --script` doesn't load autoloads, so every autoload
  name reads as unknown. To compile-check game scripts, `load()` them
  from a `-s` SceneTree script inside the project.
- Rendering stems is N full offline renders. With FORGE devices that's
  ~5 min for a 95 s track in a CPU-shared sandbox. Keep slow paths out
  of the default run, and watch render time on the Deck.

### 2026-10-11 — mixer inserts, sidechain ducking, automation lanes

- **One strip builder for live and offline.** `_buildStrip()` builds
  every strip for live playback, `renderOffline` and `renderStems`.
  That is what keeps the realtime bounce and the offline render
  matching. At build time the envelope correlation was ≥ 0.89 for
  every insert; the compressor was lowest. Never add a feature to
  only one side.
- **Strip signal chain:**
  `in → inserts → post (sidechain tap) → duck → pan → vol → on → buses`.
- **Mixer inserts are FORGE's snap-ins.** `ForgeSynth.createEffect`
  provides them, so the DAW and FORGE share one implementation.
  `daw_fx.js` adds only what FORGE lacks:
  - low and high cut;
  - bitcrush;
  - noise gate;
  - the sidechain envelope follower.
- **Automation works on a copy.** It never writes into the project
  JSON. The project value is the knob, and it comes back on stop, so
  undo and save stay clean.
- **Strip AudioParams.** Schedule breakpoints plus a ramp to each
  look-ahead window's end. A loop wrap is a fresh `setValueAtTime`.
  Never call `cancelScheduledValues` at the wrap; it deletes the ramp
  that ends there.
- **Sidechain tap and stems.**
  - Tap the source after its inserts and before its fader, so a
    muted or soloed-away source still ducks.
  - In a stem whose source isn't rendering, build the source
    silently (its `on` gain is 0) so it still drives the duck.
- **Duck threshold.** The default is −10 dB with a 12 dB knee. At
  −30 dB the long FORGE kick held the duck shut and nothing pumped.
- **Look-ahead windows are fractional ticks.**
  `floor((t1 − 1 − cs) / len)` silently skipped the notes on the loop
  start when the window after the wrap was under one tick. Use an
  epsilon.
- **`applyMix()` must re-read each strip's mix object from the
  project.** Undo swaps mix objects, and strips that keep the old
  reference stop hearing edits.
- **Device-parameter automation is limited to FORGE macros, master
  gain and lane gains.** FORGE reads per-voice parameters at
  note-on. Route a macro to them in the mod matrix instead.
- **Tests stay offline.** The permanent `daw_fx` suite runs in about
  10 s on offline renders. Live-vs-offline matching was measured once
  at build time; realtime bounces are slow and occasionally slip in
  headless Chromium.

### 2026-10-11 — DAW recording: count-in, punch, loop takes, latency

- **One clock for every recorded position: SCHEDULED context time** (`timeOf(tick)`).
  - MIDI notes are mapped back from their own event time stamps.
  - Audio is cut from a frame-stamped capture: a worklet posts `currentFrame` with each block.
  - The old `AK.Capture.begin()` + `currentTime` guess was off by the message delay.
  - The test shows the per-pass slices start exactly one loop length apart (±1 sample).
- **The master limiter looks ahead 6 ms.** A `DynamicsCompressorNode` delays everything on the
  master by 264 samples at 44.1 kHz. The click went straight to the speakers, so it flammed 6 ms
  ahead of the music. Hardware MIDI, timed to the undelayed clock, put the FM-1 6 ms ahead of the
  DAW's own synths.
  - `start()` measures the delay (`outDelay`, an impulse through an identical compressor offline).
  - The click bus and `HwDevice._send` are delayed by the same amount.
  - Offline renders and bounces still begin 6 ms late (unchanged). Compare onsets with
    `limiter: false`.
- **Three latency numbers, because three paths really differ** (header of `daw_engine.js`):
  - **FM-1 RETURN** = CHECK-OUT's `mm_fm1_latency_ms`; the DAW adds `outDelay` because it sends
    its MIDI that late. It applies to the FM-1's USB audio whether the DAW or the player's keys
    triggered it, so it follows the input, not the player.
  - **PLAY-ALONG INPUT** = LOOPBACK CALIBRATE. Its clicks run through the delayed click bus, so the
    reading already contains `outDelay` and is used as it stands.
  - **MIDI NOTES** need no round trip: event time stamp → `ctxAtPerf()` − `outDelay`. A manual
    nudge stays, normally 0.
  - Auto picks FM-1 RETURN when the input label looks like the FM-1.
  - Machine settings live in localStorage `mm_daw_latency`. A CHECK-OUT run in another tab reaches
    the DAW live through the `storage` event.
- **Stamp each event, don't read "now".** `midiinput-message` carries `ts` and fires before
  `midiinput-note`. The page hands it (and `KeyboardEvent.timeStamp`) to `E.stampInput()` in
  capture-phase window listeners. `recNow()` uses it only within the same dispatch (< 20 ms), so
  timer-driven notes (arpeggiator) fall back to the present. `liveNote` itself changed by one
  call site only.
- **Anchors move ~120 ms before a wrap sounds** (look-ahead). The engine keeps an anchor history
  `{ctx, tick, n}` per play / wrap. A note or a pass is placed by looking up the anchor in effect
  at its context time, never "the current anchor".
- **Takes are data, not a playback feature.**
  - `track.takes[]` holds one active take per (region, kind, layer). Activating a take swaps the
    region clip's `pid` or audio ref, so playback, render, MIDI export and undo needed no change.
  - Inactive MIDI takes are plain patterns no clip points at.
  - An empty recording restores the track's snapshot exactly.
  - A recording is one undo step: the page snapshots on `record-arm` and skips captures while
    recording.
- Bugs found on the way:
  - `BasicSynth.noteOff(n, when, immediate)` received the MIDI channel third, so every note was cut
    when scheduled; the fallback synth had been silent in playback and renders.
  - The piano roll's "1/16T" was 32 ticks (an eighth triplet). `DAW.GRIDS` now feeds GRID and QUANT
    (1/16T = 16, 1/8T = 32).
  - `E.load()` fires `'project'` before the page's `P` follows it, so UI sync read the old project.
  - `undoApply` never removed top-level keys added since the snapshot.
- **Headless testing:**
  - `fm1_mock.raw(bytes, ts)` sends MIDI with an exact time stamp.
  - A `DelayNode` off the click bus stands in for a loopback cable.
  - The real-time transport runs at 300 BPM so `daw_rec` stays at about 30 s.
  - `getOutputTimestamp` is stable to ±1–2 ms in headless Chromium but steps after an audio
    glitch, so a simulated performer works out its time stamp just before striking, as a person
    would.
  - The first FORGE offline render in a session differs from later ones (warm-up). Old-vs-new
    engine renders matched to −97.5 dB from the second render on.
- Not done:
  - Comping is whole-region only (no per-bar swipe).
  - REPLACE trims the old audio clips without fades.
  - OVERDUB LOOP stacks MIDI only; audio stays one take per pass.
  - LOOPBACK and the FM-1 RETURN + `outDelay` sum are unverified on the Deck's hardware.

### 2026-10-11 — review staging, the AUDIO DIRECTOR, and file:// messaging

- TEMP TRACKS writes candidate takes to
  `assets/audio/review/<track id>/<take id>/` (see
  `_MUSIC_DIRECTION_PLAYBOOK.md` §8). `audio_director.html` approves one
  into `<src base>.wav` plus stems and manifest. Staging is ignored by
  version control, excluded from `music_drive.sh`, and carries a
  `.gdignore` so Godot never imports or exports it.
- `music_drive.sh` now uses ordered `--filter` rules, because mixing
  `--exclude` with `--include` leaves the order to rclone. Checked with
  rclone 1.68.2 `ls`: staging is skipped, and the game audio, manifests
  and credits still sync.
- **Cross-page notices on file://:**
  - BroadcastChannel messages and localStorage `storage` events both
    cross between two file:// tool pages in headless Chromium. Both
    were tested, with the same uid on each.
  - OPFS does **not** work on file:// without
    `--allow-file-access-from-files` (SecurityError).
  - Shim the game folder with `exposeFunction` instead. The harness's
    `ctxInit` / `expose` options install the shim in pop-ups too.
- **Headless touch waits for a frame.** Once a pop-up took the
  foreground, every CDP touch on the opener took ~4 s, because a
  background page gets no frames. Close the pop-up or call
  `bringToFront()` before driving touch.
- `AK.game` gained `readFile`, `list`, `remove` and `copy`.
- **Exact length:** a length in seconds nudges the tempo
  (`bpm = bars × 240 / sec`) so whole bars land on it exactly.
  - The render folds the tail onto the head (`doBounce(true)`).
  - 7 s came out at exactly 308 700 frames.
  - The tempo may be fractional; the engine and SeqGen accept that.
- Taps can outrun decoding. Two quick take picks raced, and the older
  decode won. A pick sequence number now makes the latest pick win.

### 2026-10-11 — "the DAW crackles and stops after a few seconds" (Deck)

- **Measure before guessing.** An offline render of 8 bars, timed, gives
  the audio graph's cost as a fraction of one core. Live playback has
  to do the same work in real time, with less slack. On this
  2.7 GHz Xeon (roughly a Deck core):
  - songs measured 0.6–1.03 of a core after the library merge
    (0.45–0.68 before);
  - so on the Deck the audio thread runs out of time: it crackles,
    then audio stops.
  - Profiling per track, the **KIT cost 0.28–0.41** and a pad playing
    chords 0.25–0.36. The master chain and the empty graph cost
    0.01–0.02.
- **Every FORGE synth costs audio time even when silent.** Each one
  carries its preset's lanes and FX, typically two convolvers. The
  kit built one FORGE synth per map piece, about 14 after the library
  added cymbals and hand percussion, whether or not the song hit
  them. Pieces now build on first hit and are prepared (built and
  `init()`ed) from the song's drum notes before `play()` and offline
  renders, in map order. Kit cost dropped to 0.16–0.21 with the same
  sound.
- **Per-synth reverbs are 15–25% of a song's cost.** They are part of
  each preset's sound, so they were kept. Profile again before
  removing anything.
- **Buffer.** `mm_daw_buffer`: SMOOTH (default) = Chrome's `'playback'`
  buffer, about 23 ms base vs about 10 ms interactive. FAST =
  interactive, for playing live. Reload to switch.
  - A fixed 60 ms hint gave about 245 ms total output latency in
    headless Chrome, and the recording timing broke; don't go that
    big.
  - Flatpak Chrome's audio thread may lack real-time priority, so
    headroom matters.
- **Latency numbers carry the output latency they were measured
  with.**
  - CHECK-OUT saves `baseLatencyMs`/`outputLatencyMs` and now uses
    the DAW's buffer mode.
  - The DAW's loopback calibration stores `outMs`.
  - `audioComp()` adds `outMs(now) − outMs(at measurement)`, because
    hardware MIDI leaves when its audio is *heard* (`perfTime`).
- **Never trust one `getOutputTimestamp()` reading.** Steady state is
  rock-steady: one offset value over 400 readings, no drift. But for
  about 2 s after the context starts, readings jump by up to a buffer
  (18–23 ms with `'playback'`). `clockOffset()` takes the median of
  the last 9 distinct readings, and both `perfTime` and `ctxAtPerf`
  use it.
- `daw_perf`'s old-engine comparison failed 2 of 6 times on the
  untouched engine too. FORGE's run-to-run noise has a second mode of
  exactly 1.4e-4. Tolerance is now 3e-4, and events must still match
  exactly.

### 2026-10-11 — "every song stops after a second or two" — make the DAW report itself

- The cuts happened in the same place each time and in most songs, on
  the Deck only. Headless Chrome played every song continuously, with
  no errors. So the failure depends on that machine, and guessing
  stopped being useful.
- `scheduleRange` used to wrap each `noteOn` in a silent
  `try/catch` ("device mid-reload"). A device that failed on every
  note gave a song with *no sound and no error*. The other scheduling
  sections had no guard at all, so one exception killed the
  scheduler, and the song stopped once the ~120 ms look-ahead plus
  release tails ran out (a second or two).
- Now:
  - every section is guarded, and each fault goes to `E.fault()` →
    `E.diag`;
  - the scheduler logs stalls longer than the look-ahead;
  - the context's `statechange` / `sinkchange` are logged, and a
    suspended or interrupted context is resumed while the transport
    plays. Plugging in the FM-1 can make its USB audio the default
    output.
  - DIAG (transport) shows a ⚠ when something went wrong. COPY gives a
    text report: Chrome version, context state and latencies, output
    device, outputs, transport, every device (loaded? voices?), and
    the log.
- Rule: never swallow an exception in an audio path. Log it where the
  user can copy it.

### 2026-10-11 — first DIAG from the Deck: everything "fine", output silent

- The user's report showed:
  - transport playing at 64 s, context running, no errors, no
    stalls;
  - every synth with voices;
  - yet they heard less than a second of sound.

  So the scheduler, the context and the devices are fine and the
  OUTPUT is silent. That is the signature of NaN poisoning (a NaN
  reaching the limiter, a convolver or a feedback delay silences
  everything after it for good) or of audio leaving Chrome to the
  wrong place. Headless Chrome 141 plays the same presets cleanly,
  offline and live; the user runs Chrome 154.
- Counting `noteOn` calls is not checking audio. Tests and DIAG now
  read the actual output.
- Output watch (4× a second while playing):
  - It reads analysers on the master, the limiter, the output and
    every strip (`in` = the instrument, `on` = after its inserts).
    The strip taps exist before a fault, because a fresh analyser
    reads zeros.
  - On NaN it logs the first strip showing it, mutes that strip, and
    rebuilds the limiter and send buses (`_buildBuses`), so the rest
    plays on.
  - It logs "silent while voices play".
  - DIAG adds the output level history (rms per second).
- Test flake root causes (all predated these changes):
  - `daw_rec`: a fixed 300 ms wait for a cross-tab storage event on a
    cold browser. The failing assertion then skipped
    `other.close()`, which left the DAW behind another tab with no
    frames, so a later touch test failed too. Fix: wait for the
    condition, close in `finally`, `bringToFront`. The DAW also
    re-reads the CHECK-OUT value on focus / visibility, because
    Chromium can drop the storage event.
  - `library`: unseeded noise flipped thresholds. Renders are now
    seeded per preset.

### 2026-10-11 — the Deck drops Chrome's output under load: ▶ now plays a render

- Root cause of "plays for under a second, then silence":
  - DIAG showed output RMS 0.2–0.37 while nothing was heard.
  - `wpctl status` showed no Chrome output stream at all.
  - In AUDIO TEST every light row played and the heavy row (about
    0.78 of a core on the audio thread) stopped or never started.

  On the Deck, a heavy Web Audio load makes Chrome lose its PipeWire
  stream. Chrome then renders into a silent fake sink, the context
  keeps "running", and nothing tells the page. The RealtimeKit
  flatpak override didn't help.
- FORGE builds 20–40 nodes per voice, so a busy generated song costs
  0.7–1.15 cores live. LIGHT live sound (no unison, a shared reverb
  instead of per-patch reverb / delay / chorus) cuts only 25–30%,
  which is not enough. Don't try to make the whole song fit the
  real-time thread.
- **PLAY: RENDER is the default ▶.**
  - The loop or song is rendered offline, which never touches the
    real-time thread. The output streams back while rendering: a tap
    worklet posts 16384-frame blocks, and each block is scheduled as
    a buffer source on the frame grid.
  - Playback starts once the measured render rate says it will stay
    ahead. That is about 0.8 s here. If the render falls behind, the
    playhead holds back instead of glitching.
  - Loops stream the first pass, then play the folded loop.
  - The result is cached by the project JSON plus the region, so ▶
    with no edits is instant.
  - Streamed output equals the finished render to 6e-8, and that is
    tested. The live master's gain is undone with `1/vol` because the
    render already carries it.
  - LIVE stays available for keys and recording, and recording
    always plays live.
- **Offline renders were quadratic.** Every note of the song was
  created before `startRendering`, and every node in the graph costs
  every render quantum: 16 bars took 39 s and 32 bars 101 s. Notes
  now go in a 2 s window at a time from `suspend()` callbacks, one
  window ahead, which makes it linear: 32 bars take 34 s, about 1.8×
  real time. Exports and stems speed up too.
- Window order matters for reproducibility. FORGE draws from the
  page-wide `Math.random`, so the order across devices decides which
  random numbers each device gets.
  - Within a window, notes keep their old order.
  - The first two windows go in as one batch, so short renders call
    their devices exactly as before.
  - The `daw_perf` old-vs-new check caught this: the audio was
    0.35 off while each device's events were identical.
- `library` flake (existed before this change): `LIB.all` ran 8
  seeded renders at once, and each swapped the global `Math.random`.
  The seeds mixed, and amb_rain's macros-up peak hit 1.009 once.
  Seeded renders now run one at a time (19 s).
- The transport bar must stay one line at 1280 px. The PLAY mode
  button doubles as the render progress (`◔ 34%`) and the
  "EDIT ▶" hint, rather than adding a status span.

### 2026-10-11 — Chrome runs every offline render with a worklet on ONE thread

- On the Deck, ▶ in RENDER mode never started a 48-bar song. The
  single render ran slower than real time there, so the wait to get
  "far enough ahead" was minutes. LIVE (LIGHT) did play the credits
  song.
- Four parallel renders took 4× as long as one: Chrome renders every
  OfflineAudioContext that has `audioWorklet.addModule` on one shared
  worklet thread. Four plain contexts did run side by side. FORGE's
  `init()` always loaded its crush worklet and `DawFX.prepare` loaded
  the gate/duck worklets, so every DAW render was serialised.
- Fix:
  - `ForgeSynth({worklet:false})`: crush falls back to its waveshaper
    curve.
  - `renderOffline({worklets:false})` skips DawFX.
  - `holdTail` makes the tail cover notes held past the chunk end.
  - `clipAt` ends notes at the loop end.
- PLAY: RENDER now renders 4-bar chunks in parallel:
  - Chunk 1 streams through its tap worklet, so the first sound comes
    in about 0.85 s.
  - The rest render worklet-free beside it. They wait for chunk 1's
    first block, because their device setup on the main thread
    delayed it to 3.3 s.
  - A 32-bar song renders in 22 s, down from 34 s single and 101 s
    before windowing.
  - The ▶ start rule uses total throughput across chunks.
- Projects needing a worklet (gate inserts, ducking, PATCH BANK / DX7)
  fall back to the single streamed render (`chunkable()`).
- DIAG logs the render: first block, every quarter with its
  × real time, every 5 s while stuck, done.
- The AUDIO DIRECTOR got a **? HOW TO** guide after the user couldn't
  find how to approve. The flow needs ⌂ LINK GAME FOLDER first.

### 2026-10-11 — temp music goes into the game as Ogg Vorbis, not WAV

- The user: "The audio, especially for midi audio, needs to be small in
  size, I don't want 20 meg minute or two long audio tracks, the game
  will get bogged down." Approved temps were 16-bit WAV: 10.1 MB a
  minute per file, about 60 MB a minute with five stems.
- Now APPROVE, "straight into game (skip review)" and BOUNCE → INTO GAME
  write Ogg Vorbis through one function, `AK.game.writeMusic`. Measured
  on a 94 s generated temp (`TEST_SLOW=1 run_tests.sh daw` prints it):
  - mix (q4): 1.47 MB = 0.93 MB/min;
  - stems (q1): drums 0.58, bass 0.19, chords 0.44, lead 0.53,
    pad 0.47 MB/min;
  - the whole temp: 3.1 MB/min, down from 60.6 MB/min as six WAVs.
  - Encoding speed: 10 s of stereo in 0.17–0.19 s in headless Chromium
    here (~55× real time), so a 94 s temp with five stems is ~10 s.
    Not yet timed on the Deck.
- The encoder: wasm-media-encoders 0.7.0, vendored as one classic
  script with the `.wasm` as base64 (`vendor/oggvorbis/pack.py` rebuilds
  it from the npm tarball). Its UMD build fetches the wasm from unpkg by
  default; `createEncoder('audio/ogg', compiledModule)` never touches the
  network (the `dsp` suite asserts no non-file request).
- **Temp naming keeps temp and real apart:** `<base>.temp.ogg` is the
  last fallback in `_load_audio` (src → `.wav` → `.temp.ogg`), and a
  manifest with `temp: true` never layers its stems over a real src or a
  recorded `.wav`. The manifest is always written now, because it is
  where an Ogg's loop lives.
- **Loops:** the file is cut at the `smpl` end + 1, and the manifest's
  `loop_offset` sits a quarter frame past the start. `start / sr` in
  floating point can come back as start − ε; if Godot truncates
  seconds × rate to a frame, that is one frame short. The quarter frame
  covers truncation and rounding alike.
- **Chrome pads, Godot doesn't.** `decodeAudioData` returned 441 920
  frames for a 441 000-frame Ogg (no end trim from the last granule).
  Godot 4.6 and ffmpeg read the exact length. Don't use the browser to
  check Ogg lengths; the tests read the last page's granule position or
  ask Godot.
- **A sine at 882 Hz hid a wrong loop offset:** 50 frames is one whole
  cycle, so the seam test passed with the offset 50 frames off. A
  20-frame error gave a residual of 0.17 vs 0.0055. Pick test offsets
  that aren't whole periods of the test tone.
- `AK.wav.decode` reads staged WAVs sample-exact, keeping `smpl`.
  `decodeAudioData` would resample to the context's rate (48 kHz on
  many outputs) and drop the loop.
- Older WAV temps keep working (recognised, revocable) and
  ⇣ SHRINK WAV TEMPS → OGG converts them in place, moving the credits
  and recording `shrink` in `temp_approvals.json`.
- `music_encode.py` makes a `.wav` the REAL file; don't use it on a
  "(temp)" `.wav` any more: SHRINK keeps it a temp.
- `music_drive.sh` never deletes. After SHRINK the old `.wav` temps are
  still in Google Drive, and a `pull` brings them back, where they
  shadow the `.temp.ogg` (a `.wav` comes first). The AUDIO DIRECTOR then
  offers SHRINK again. `music_drive.sh tidy` removes them from Drive
  (see the 2026-10-12 tidy lesson).
- Seen once, not reproduced in four more runs: `daw`'s PLAY: RENDER
  test got its first sound after 6.6 s (its limit is 5 s). Nothing in
  this change touches that path; if it comes back, check machine load
  first.

### 2026-10-11 — the AUDIO DIRECTOR makes takes itself (temp_maker.js)

- The user's feedback: "this is not intuitive. can't I just render
  from the director and then listen to it there once it's done
  rendering?" Before this, MAKE TAKES opened a DAW tab, which then
  needed its own START tap and its own folder permission.
  - Takes looked like they "didn't save". Each take rendered 5 full
    stems serially, all on Chrome's one worklet thread, so on the Deck
    it ran many minutes.
  - Stems now render 2–3 at a time; see the chunked-render lesson for
    why that needs worklet-free contexts.
- `temp_maker.js` holds the whole take pipeline as functions over a
  `DAW.Engine`: compose, shape arrangement, arrangeTo, render (stems +
  mastering), writeTake, and writeTempToGame (Ogg).
  - The director loads the engine scripts plus temp_maker.
  - It starts one engine on the first MAKE TAKES tap; the
    AudioContext needs the gesture.
  - Requests queue, and progress shows under the button: composing →
    rendering stems k of n → saving.
  - Each take appears under TAKES as soon as it's written.
  - The DAW's TEMP TRACKS calls the same code. The DAW-side request
    plumbing (URL request, BroadcastChannel ack, gate) is gone.
- `temp_maker.render()` throws on failure. The DAW's `doBounce`
  swallowed errors, and makeTakes' `if (!lastBounce)` check couldn't
  catch it, so a failed render could write the previous take's audio.
- audio_kit.js declares `AK` with a top-level `const`. A classic
  script in another file can see it lexically, but `window.AK` is
  undefined, so shared modules must use `typeof AK`.
- The daw.html `'project'` handler now syncs `P = E.project` first.
  temp_maker swaps projects inside the engine, so the page's `P` can
  be stale when the event fires.
- The test harness launches Chromium with
  `--autoplay-policy=no-user-gesture-required`, so it can't catch an
  engine started outside a tap. Keep the director's engine start on
  the MAKE TAKES / ⟳ AGAIN click path.

### 2026-10-12 — APPROVE over a non-temp .wav: say what it is, move it aside on a second tap

- The user hit "REFUSED: …/vol1_ambient.wav is real audio (not a
  temp — a FIELD RECORDER / TAPE STUDIO take?). Move it away first".
  The tool gave no way to do that.
  - Likely source: a DAW BOUNCE → INTO GAME from before the Ogg change.
    Those are titled with the project name, not "(temp)", so they
    count as real.
- Never overwriting real audio is right; a dead end is not. Now:
  - The first tap describes the file from its own chunks: kind, title,
    originator, date, MB.
  - A second tap within 4 s moves the .wav, its credits, and a non-temp
    stems manifest + stems to `assets/audio/replaced/<name>.<stamp>…`.
    That folder has a .gdignore, so Godot ignores it, and
    music_drive.sh backs it up.
  - Then it approves. The approval history records `moved_aside`.
- Drive caveat: `music_drive.sh pull` never deletes, and Drive may
  still hold the old `<base>.wav`, so a pull brings it back.
  `music_drive.sh tidy` removes it.

### 2026-10-12 — "can't delete tracks I can't find on google drive": music_drive.sh tidy

- Asking the user to hand-delete replaced WAVs in Drive was a dead end:
  they couldn't find them (or had never pushed them).
- `music_drive.sh tidy` lists the Drive files this machine no longer
  has because the tools replaced them, and deletes only those after a
  y/N:
  - `<base>.wav` / `<base>.wav.credits.txt` when `<base>.temp.ogg` is
    here, or the .wav was moved to `replaced/`;
  - `<base>.stems/*.wav` when the Ogg temp or its manifest is here.
  - Anything else only in Drive (new on another machine) is listed and
    left alone. `--yes` skips the prompt.
- Tested against a stub rclone (listremotes / lsf / deletefile) on a
  scratch tree; there's no rclone in the cloud sandbox.

## TEMPLATE

```
### YYYY-MM-DD — <one-line summary>

- <lesson>
- <lesson>
```
