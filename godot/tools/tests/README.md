# godot/tools tests

Headless checks for the browser tools (DAW, PATCH BANK, FORGE / DX7 / sampler engines, the FORGE preset library,
audio_kit DSP, finger controls) and the game's `AudioMgr` music layering.

```bash
godot/tools/tests/run_tests.sh                 # all offline suites, ~4 min
godot/tools/tests/run_tests.sh dsp engines     # some suites
TEST_NETWORK=1 godot/tools/tests/run_tests.sh patchbank_network   # real downloads from GitHub
TEST_SLOW=1    godot/tools/tests/run_tests.sh daw                 # + TEMP TRACKS with stems
GODOT=/path/to/Godot_v4.6-stable_linux.x86_64 godot/tools/tests/run_tests.sh godot_audiomgr
```

Needs `node` + `playwright` (`npm i -g playwright`) and a Chromium (`CHROME_PATH`, or playwright's).
In the cloud sandbox the browser must use `$HTTPS_PROXY` for network suites (the harness does that).

| suite | covers |
|---|---|
| `data` | firmware + PATCH BANK registries, composer determinism + mood mapping, MIDI file round trip |
| `dsp` | LUFS = ffmpeg ebur128, true peak (inter-sample), mastering, stems ⨉ limiter curve, worklets on file://, the vendored Ogg Vorbis encoder (no network, decodes back aligned + as loud, < 1.3 MB/min, loop cut), `AK.wav.decode` |
| `engines` | DX7 SysEx (0n dump header), bank round trip, DX7 tuning, sampler mapping / round robin / respread |
| `library` | FORGE instrument library (~25 s): every preset renders offline (finite, audible, ≤ limiter, pads sustain), distinct from its nearest neighbour, within ±8 dB of its category; every mod route / named macro resolves and the macros move the sound; the 29 original presets' data is unchanged; composer pools (role-fit, per-seed deterministic, varied, notes untouched); DAW KIT style pieces, old KIT maps kept, FORGE + PATCH pickers by CDP touch (≥ 36 px) |
| `touch` | relative sliders, clip drag + long-press delete, piano-roll tap / hold (real CDP touch events) |
| `daw` | compose, offline render, seamless loops, stems sum, undo/redo, MIDI export, TEMP TRACKS ordered / shaped by the director's briefs, TEMP TRACKS "straight into game (skip review)" → Ogg Vorbis in the game folder (MB/min printed; replaces an older .wav temp) |
| `daw_fx` | mixer inserts (every type renders; filter / EQ / drive move the sound the right way), sidechain ducking with the source muted, volume automation ramp, undo / redo reaching the audio graph |
| `daw_perf` | PERF tools (`daw_perf.js`): scale lock every mode, diatonic chords per degree + voicings, arp order / rate / octaves / gate / latch / free-run against the transport grid (±1 ms), the recording hook, groove + clip arp + probability live = offline, swing-only projects feed the devices the same events as the engine before PERF, STEP view + PERF panel by CDP touch, undo / redo, save / reload (~27 s) |
| `daw_rec` | recording (real-time transport, mock FM-1 MIDI + USB audio, ~30 s): count-in clicks + grace, punch in/out (MIDI replace / overdub), loop takes (MIDI per pass, overdub loop, audio slices sample-exact per pass), latency (CHECK-OUT `mm_fm1_latency_ms` pickup incl. from another tab, loopback calibration, ±2 ms alignment), take pick / undo / redo / delete / keep, save → reload, old projects unchanged, finger controls (punch drag, takes row, ≥ 36 px) |
| `audio_director` | AUDIO DIRECTOR (`audio_director.html`) on a shimmed game folder (~20 s): track statuses (missing / candidates / approved temp / real audio incl. a non-temp .wav), most-played ordering + filters, preview stem gains at intensity 0…1 = AudioMgr's layers + linear fades, A/B at the same position, PLAY AS SCENE (curve → attack / release → stems, lines), APPROVE encodes exactly `<src base>.temp.ogg` + `.stems/*.ogg` + `.stems.json` + `temp_approvals.json` (sample-exact lengths, MB/min thresholds, a seamless DAW take's loop → the manifest), real-audio refusal, two-tap replace / reject / revoke (older .wav temps and Ogg temps), SHRINK of older WAV temps, rejected seeds skipped, the DAW review staging + request round trip (new tab, then live over BroadcastChannel; notices by BroadcastChannel and `storage` event), creative direction (description → mood, instrument override, exact length in bars / seconds, parts + extra pads → tracks and stems), CDP touch on the main controls (≥ 36 px), the runtime instrument picker |
| `fm1_checkout` | the hardware check-out page against a mock FM-1 (`mocks/fm1_mock.js`): identity / INFO gating per firmware, part channels, DX7 dump bytes + FM-1+VA overwrite gate, 24 ppqn clock, round-trip latency, reload |
| `godot_audiomgr` | the real `AudioMgr.gd` in a throwaway project: .wav fallback, stems → AudioStreamSynchronized, intensity, missing-stem fallback, track ending mid-fade; Ogg temps (`.temp.ogg` found last, exact length, manifest loop + loop_offset imported and raw, a seamless loop with no restart / gap / click, Ogg stems all looping, real `.ogg` / `.wav` winning over a temp) |
| `godot_director` | the VN `MusicDirector.gd`: GDScript ↔ `music_direction.py` parity on real scenes, writing → intensity, choice / interlude / cg, cue sheets + beats + auto, leitmotif, locale track, silence, smoothing into AudioMgr, replay |
| `patchbank_network` | FluidR3 / DX7 ROM / tonejs / VSCO 2 CE instruments from GitHub, in tune, cached |

Rules: pages open from `file://` **without** `--allow-file-access-from-files` (that flag once hid
a Deck-breaking bug); any page error or console error fails the suite. Every bug fixed in these
tools should leave a test behind here.
