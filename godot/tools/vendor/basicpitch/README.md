# vendor/basicpitch — Spotify Basic Pitch for the file:// tool pages

[Basic Pitch](https://github.com/spotify/basic-pitch-ts) is Spotify's automatic music transcription model
(audio → polyphonic notes, any instrument; a small model, 742 KB of weights). It is vendored here so the browser tools can turn
an imported recording into notes for temporary sketch arrangements, with no server, no ES modules and no
network: the pages are opened from `file://` in Flatpak Chrome on the Deck, where `fetch()` of local files is
blocked.

The page-facing API lives in `godot/tools/transcribe_notes.js` (our code):

```js
// <script src="transcribe_notes.js"></script>   — loads the three files below on first use
await BasicPitchLite.ready();                        // → true / false (false: no backend could run the model)
const { notes, seconds, backend, ms } = await BasicPitchLite.transcribe(monoFloat32, sampleRate, {
  onProgress: f => {},      // 0…1
  onsetThreshold: 0.5, frameThreshold: 0.3, minNoteMs: 58, minFreq: null, maxFreq: null, melodiaTrick: true,
  signal,                   // optional AbortSignal
});
// notes: [{ t: start s, d: duration s, n: MIDI note (int), v: 0…1 }], sorted by t then n
```

## Files

| file | bytes | what |
|---|---|---|
| `basicpitch_tf.js` | 991 458 | one classic script (esbuild IIFE, minified): TensorFlow.js 4.22.0 core + converter + WebGL / WASM / CPU backends, and Basic Pitch 1.0.1's `src/inference.ts` + `src/toMidi.ts`. Defines `window.BasicPitchVendor = { tf, loadGraphModel, setWasmPaths, BasicPitch, outputToNotesPoly, noteFramesToTime, addPitchBendsToNoteEvents, versions }` |
| `basicpitch_model.js` | 1 154 314 | the model: `window.BASIC_PITCH_MODEL = { modelTopology, weightSpecs, weightData (base64 of the 742 392-byte weight shard), format, generatedBy, convertedBy, signature }` |
| `basicpitch_wasm.js` | 566 674 | `tfjs-backend-wasm-simd.wasm` (424 594 bytes) as base64: `window.BASIC_PITCH_WASM_SIMD` |
| `build.sh` | | rebuilds all three from npm (pinned versions inside) |
| `LICENSE` | | Apache License 2.0 (Basic Pitch, TensorFlow.js, long) |
| `NOTICE` | | every bundled component, its copyright, and the MIT / BSD texts (seedrandom, XNNPACK, pthreadpool, cpuinfo, FP16, FXdiv, Emscripten) |

2.7 MB in all, loaded once per page. The minified bundle by package: tfjs-backend-webgl 332 KB, tfjs-core
252 KB, tfjs-backend-wasm (JS) 139 KB, tfjs-converter 124 KB, tfjs-backend-cpu 119 KB, long 9 KB, seedrandom
7 KB, Basic Pitch 6 KB. The minimal tfjs packages replace the full `@tensorflow/tfjs` (no layers, no data);
the kernels of each backend are all registered — registering only the model's kernels would save a few hundred
KB but breaks silently the day a kernel is missing.

## How it loads (no fetch, no network)

- `transcribe_notes.js` adds `<script>` tags for `basicpitch_tf.js` and `basicpitch_model.js` (and
  `basicpitch_wasm.js` when the WASM backend is tried), resolved relative to its own `src`.
- The model goes in through `tf.io.fromMemory({ modelTopology, weightSpecs, weightData })` → `loadGraphModel`;
  the base64 is decoded to an `ArrayBuffer` on the page. `loadGraphModel(url)` would `fetch()` — never used.
- The WASM backend gets its binary as a `data:application/wasm;base64,…` URL through `setWasmPaths`: read
  from memory, no `.wasm` file is requested. Only the SIMD build is vendored, so the backend is tried only
  when `WASM_HAS_SIMD_SUPPORT` is true, with threads forced off (file:// pages are never cross-origin
  isolated; the threaded build would need SharedArrayBuffer).
- The `transcribe` test suite asserts the only requests are the page, `transcribe_notes.js` and these three
  files (`file:`), plus `data:`.

## Backends

`ready()` tries WebGL on a real GPU, then WASM (SIMD, one thread), then the plain-JS CPU backend. A software
WebGL renderer (SwiftShader in headless Chromium, llvmpipe) goes last. Each candidate must pass a warm-up: one
model window of a 440 Hz tone must peak at A4 (catches NaN / low-precision GPUs) — otherwise the next one is
tried and `BasicPitchLite.error` says why. `ready({ backend })` forces one (tests).

Measured in headless Chromium 141 in the cloud sandbox (4 vCPU, no GPU), 2026-10-16:

| backend | s of processing per s of audio | load + warm-up |
|---|---|---|
| WASM (SIMD) | 0.10–0.16 | 0.3–0.7 s |
| WebGL on SwiftShader | 0.9–1.2 | 5–7 s (shader compile) |
| CPU (plain JS) | 1.3–1.9 | 1.5 s |

A 180 s piece took 21.5 s on WASM. Not yet timed on the Deck's GPU (WebGL).

## Processing

- Input is resampled to 22 050 Hz with an `OfflineAudioContext` (Basic Pitch's rate), framed with
  `BasicPitch.prepareData`, and run one 2 s window at a time through `evaluateSingleFrame` / `unwrapOutput`
  — Basic Pitch's `evaluateModel`, but with every tensor disposed (the upstream loop leaks them) and a yield
  between windows.
- Notes: Basic Pitch's `outputToNotesPoly` (onset 0.5, frame 0.3, min length round(58 ms × 86.13) = 5 frames,
  inferred onsets on, melodia trick on, energy tolerance 11) and `noteFramesToTime`. That decoder is quadratic
  (180 s → 12 s of frozen page), so pieces over 38 s decode in 30 s segments with 4 s of context each side:
  a note belongs to the segment it starts in, and a note cut by a window end is stretched by the same key in
  the next segment's left context. On a 75 s test piece the segmented and whole-piece notes are identical.
- Pitch bends (`addPitchBendsToNoteEvents`) and MIDI file writing are not used (`@tonejs/midi` is stubbed).

## Rebuild

```bash
godot/tools/vendor/basicpitch/build.sh            # needs node + npm with registry access; prints sizes
godot/tools/tests/run_tests.sh transcribe
```

The output is deterministic (same versions → byte-identical files). `build.sh` pins: `@spotify/basic-pitch`
1.0.1, `@tensorflow/tfjs-core` / `-converter` / `-backend-webgl` / `-backend-wasm` / `-backend-cpu` 4.22.0,
esbuild 0.25.10. Basic Pitch 1.0.1 declares `@tensorflow/tfjs ^3.2.0`; it only uses core ops and
`loadGraphModel`, which 4.22.0 keeps, and the chained tensor methods (`t.slice()`, `t.reshape()`) are
registered by importing `register_all_chained_ops` — the modular core doesn't add them by itself.
