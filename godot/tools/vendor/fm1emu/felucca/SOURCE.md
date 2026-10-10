# Felucca browser emulator (vendored)

Felucca is free FM-1 firmware by **Leo Kuroshita (@kurogedelic), Hügelton Instruments**, licensed
**GPL-3.0-only** (full text: `LICENSE` here; the licences of the parts it ports — DaisySP and Rings
(MIT), msfa (Apache-2.0), the Inter Tight font rasterised into it (SIL OFL 1.1) — are in `LICENSES/`,
and upstream's own account of them is `LICENSING.md`).

The files here are **unmodified upstream builds**, redistributed under GPL-3.0-only. Their complete
corresponding source is the upstream repository at the source commit below.

| | |
| --- | --- |
| Upstream repository | <https://github.com/hugelton/Felucca> |
| Source commit (main) | `a4d7ca2e5d52a4c35e2468401f00d883cadbda03` (2026-10-10), Felucca 1.5.1 |
| Built files from | the `gh-pages` branch, commit `92d0634be3def39b7ae2a099a326d2cf8270453f` ("Felucca 1.5.1"), `webapp/try/` |
| Author's hosted emulator | <https://hugelton.github.io/Felucca/webapp/try/> |
| `felucca.wasm` | 741 214 B, sha256 `4e13d98f8af0e53656515011e6bf6f0b5b0ea3e462e9e4a05d83616e8a840223` |
| `worklet.js` | 6 238 B, upstream `web/emu/worklet.js` (identical in the source commit and on gh-pages) |
| The C API it exports | upstream `web/emu/felucca_web.c` (built by `web/emu/build.sh` with Emscripten) |

## Files

- `felucca.wasm`, `worklet.js` — the upstream build, byte for byte.
- `felucca_wasm.js`, `felucca_worklet.js` — the same two files as classic-script wrappers
  (`window.FM1EMU.felucca.wasmB64` / `.workletSrc`) so a `file://` page can load them without
  `fetch()`. Generated; do not edit. `fm1_emu.js` decodes the wasm and `addModule()`s the worklet text
  as a `data:` URL (a Blob URL is refused on `file://`), with a small host adapter prepended (scheduling, realtime MIDI, see below); the
  upstream worklet code runs unchanged after it.

## Rebuilding / updating

From upstream's own instructions (`web/emu/build.sh`): `./build.sh` once (generates `build/gen`), then
`web/emu/build.sh` with Emscripten (`emcc`) on the PATH → `build/emu/{felucca.wasm, worklet.js}`.
Or take the published build from the `gh-pages` branch (`webapp/try/`). Then:

```bash
python3 -I godot/tools/vendor/fm1emu/pack.py felucca --from PATH/TO/webapp/try
```

copies `felucca.wasm` + `worklet.js` in and regenerates the two wrappers. Update the commits above.

## MIDI facts (from the source commit)

- `web_midi(status, d1, d2)` takes channel messages only (`web/emu/felucca_web.c:390-395`); realtime
  bytes are dropped there. On the device, USB realtime goes into the same ring with CIN 0xF
  (`firmware/src/usb.c:821-824`, `midi_enqueue` at `usb.c:177`), and `seq.c:1278-1293` follows clock /
  start / continue / stop when MENU > MIDI > CLOCK is USB (`params.c:187`, default INT). `fm1_emu.js`'s
  adapter therefore queues a carrier message through `web_midi` and puts the realtime packet into its
  slot of that ring (`midi_in_q`, `MQ` 64 at `usb.c:169`) before the firmware reads it. The ring's
  address for this build is known (sha256 above); for any other build it is found once by a memory diff
  around two probe messages, which is then undone.
- Channels: MENU > MIDI > MIDI IN (`G_ROUTE`, default `CH1-4`, `params.c:204`): channels 1-4 play
  tracks 1-4, 5-16 are ignored (`seq.c:56-62`, `seq.c:1115-1123`, `params.c:51`). `SEL` plays every
  channel on the selected track; `CH5-8` … `CH13-16` move the block.
- CCs: the standard map, always on (`midi_control.c:208-220`): 5 glide, 7 level, 10 pan, 71 / 74 the
  engine's resonance / brightness, 72 release, 73 attack, 75 decay, 91 / 93 / 94 reverb / chorus / delay
  sends; 64 sustain; 123 all notes off (`midi_control.c:318`); plus MIDI LEARN.
- Sample rate: `web_sample_rate()` = 44 100 Hz (`felucca_web.c:486`).

M-VAVE and FM-1 are trademarks of their respective owners. Felucca is not affiliated with or endorsed
by them; Modern Mythology is not affiliated with Felucca's author.
