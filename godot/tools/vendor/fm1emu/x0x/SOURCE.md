# X0X browser emulator (vendored)

X0X is free FM-1 firmware by **Charles Vestal** — a ReBirth-style 909 / 808 / two 303s / break
slicer groovebox, a fork of Felucca — licensed **GPL-3.0-only** (full text: `LICENSE` here; upstream's
account of its parts and their origins is `LICENSING.md`; the Barlow Semi Condensed font rasterised into
it is SIL OFL 1.1, `LICENSES/Barlow-OFL.txt`).

| | |
| --- | --- |
| Upstream repository | <https://github.com/charlesvestal/fm1-x0x> |
| Source commit (main) | `6cffa408b5b95de2e41ff8b06be6c48084a95d2d` (2026-10-10), X0X 1.0.5 |
| Upstream built files from | the `gh-pages` branch, commit `225e01d0ec330abbde0409e51d14062d523d6598` ("Site for X0X 1.0.5 (from 6cffa40)"), `emu/` |
| Author's hosted emulator | <https://charlesvestal.github.io/fm1-x0x/emu/> |

## Files

- `x0x.wasm` (624 491 B, sha256 `c6c02b09522915a577a514f4bb8058701b45a9e53d59d6aa0a6ba9507bbdb00e`),
  `worklet.js` (4 714 B, identical to upstream `web/emu/worklet.js`) — **the unmodified upstream
  build**, kept for reference and for `pack.py`.
- `x0x_midi.wasm` (711 802 B, sha256 `bd6233b3b2c9452d9aa73df76112a2829807f8cfc4a006e68af8b5cfaea841df`) —
  **what the tools run**: the same upstream source commit plus `x0x_web_midi.patch`, which only *adds*
  two exports to `web/emu/x0x_web.c`: `web_midi(status, d1, d2)` (queues a USB-MIDI packet exactly as
  the host simulator's `midi` command does, `host/x0x_host.c:888-891`) and `web_sample_rate()`.
  Upstream's web build has no MIDI input at all (`plat_midi_in` reads a queue only the command-line
  simulator fills), so without the patch the DAW could not play or clock it.
  Built by `build_midi.sh` (clang + wasi-libc instead of Emscripten; this copy: Ubuntu clang 18.1.3,
  wasi-libc `165235bc467d5fa52d424f5d82587dfb76ed9d54`; rebuilding with those gives the same sha256). Checked against `x0x.wasm`: for the
  same boot and the same panel input over 6 s both render bit-identical audio and an identical screen.
- `x0x_wasm.js`, `x0x_worklet.js` — `x0x_midi.wasm` and `worklet.js` as classic-script wrappers
  (`window.FM1EMU.x0x.wasmB64` / `.workletSrc`) for `file://` pages. Generated; do not edit. The worklet
  runs verbatim; `fm1_emu.js` prepends a host adapter that routes `{type:'midi'}` messages to
  `web_midi` and schedules messages by AudioContext time.
- `x0x_web_midi.patch`, `build_midi.sh`, `font_from_wasm.py` — how `x0x_midi.wasm` is made.

These are redistributed under GPL-3.0-only. The complete corresponding source of `x0x.wasm` is the
upstream repository at the source commit above; of `x0x_midi.wasm`, that plus `x0x_web_midi.patch`,
`build_midi.sh` and `font_from_wasm.py` here.

## Rebuilding / updating

```bash
git clone https://github.com/charlesvestal/fm1-x0x && git -C fm1-x0x checkout 6cffa408b5b95de2e41ff8b06be6c48084a95d2d
git clone https://github.com/WebAssembly/wasi-libc && cmake -S wasi-libc -B wasi-libc/build -DCMAKE_C_COMPILER=clang -DCMAKE_AR=llvm-ar -DTARGET_TRIPLE=wasm32-wasip1 -DBUILTINS_LIB=EMPTY.a -DCMAKE_INSTALL_PREFIX=$PWD/sysroot && make -C wasi-libc/build -j8 install
godot/tools/vendor/fm1emu/x0x/build_midi.sh fm1-x0x sysroot && python3 -I godot/tools/vendor/fm1emu/pack.py x0x
```

(`EMPTY.a`: an empty archive, `llvm-ar rc EMPTY.a`; nothing here needs compiler-rt. wasi-sdk's
`share/wasi-sysroot` works as the sysroot too.) The font tables are lifted from the upstream
`x0x.wasm` by `font_from_wasm.py` because upstream renders them with Pillow + FreeType + libraqm; a
newer upstream build: `pack.py x0x --from PATH/TO/emu` refreshes `x0x.wasm` + `worklet.js` first.
If upstream adds its own MIDI input later, drop the patch and wrap `x0x.wasm` directly
(`pack.py x0x --wasm x0x.wasm`; set `rt` in `fm1_emu.js` to match).

## MIDI facts (from the source commit)

- Channels (`firmware/src/app/project.c:482`, `DEF[5] = {9, 10, 1, 2, 3}`, 0-based): **909 ch10, 808
  ch11, 303 A ch2, 303 B ch3, break ch4**; each part's channel can be changed on the device (GLO, stored
  per project, `project.c:487-488`).
- Notes (`firmware/src/app/engine.c:420-454`): the drum machines play GM drum notes (909: 36 38 41 45
  50 37 39 42 46 49 51; 808: 36 38 41 45 50 37 39 56 49 46 42 — `engine.c:436-437`); the 303s play
  notes, velocity >= 100 = accent, an overlapping note slides; the break plays slices on notes 36-43.
  No CCs.
- Realtime (`engine.c:426-429`): F8 clock, FA start, FB continue, FC stop. The sequencer follows an
  incoming clock at once and goes back to its own after 0.5 s without one (`seq/sequencer.c:447-454`).
- Sample rate 44 100 Hz (`host/x0x_host.c`, the I2S rate; the engine runs per 256-sample block).

M-VAVE and FM-1 are trademarks of their respective owners; TR-808, TR-909 and TB-303 are trademarks of
Roland Corporation. X0X is not affiliated with or endorsed by them; Modern Mythology is not affiliated
with X0X's author.
