# INSTRUMENT TOOLS PLAYBOOK — browser instruments + hardware controllers

How the `godot/tools/*.html` instruments (RIFFMASTER *, TAROT SYNTH,
AMBIENT SYNTH, FM-1 CONSOLE) talk to hardware: the PDP Riffmaster
guitar over the Gamepad API, and the M-VAVE FM-1 synth over Web MIDI.
Read before adding a new instrument tool, a new controller, or
touching `gamepad_input.js` / `midi_input.js` / `fm1_dx7.js`.

## Core rules

### Shared helpers, one per transport

- `gamepad_input.js` — HID gamepads. `GamepadInput` polls on rAF and
  emits `gamepadinput-*` window events. `mountGamepadOverlay` draws
  the bottom-right RIFFMASTER panel.
- `midi_input.js` — Web MIDI. `MidiInput` opens access, auto-picks
  the FM-1 ports, emits `midiinput-*` window events, and carries the
  OUT side (`noteOn/noteOff/cc/programChange/pitchBend/sendSysex`)
  plus the tool-facing echo helpers (`echoPluck`, `echoMono`,
  `echoRelease`). `mountMidiOverlay` draws the FM-1 · MIDI panel,
  placed left of the gamepad panel (`right: 300px`).
- `fm1_dx7.js` — DX7 single-voice VCED + parameter-change SysEx
  builders, and the 2-op → 6-op mapping used by RIFFMASTER FM.

A tool never talks to `navigator.getGamepads` or
`navigator.requestMIDIAccess` directly. Add behaviour to the helper,
not the tool.

### Event contract is window CustomEvents, not callbacks

Tools listen with `window.addEventListener('midiinput-note', …)`.
This keeps every tool's routing block a self-contained ~15 lines at
the bottom of its script, lets several listeners coexist (overlay +
tool + calibration), and means a helper upgrade never needs a tool
edit.

### Routing block shape (copy this)

```js
// ── FM-1 / MIDI routing ──────────────────────────────────────────
let _fromMidi = false;                        // only if the tool echoes
const mi = new MidiInput();
mi.start();
mountMidiOverlay(mi, { learnTargets: [{ id: 'vol', label: 'VOL', el: 'vol' }] });
window.addEventListener('midiinput-connected', ensureAudio);
window.addEventListener('midiinput-note', e => {
  if (!e.detail.on) return;
  ensureAudio();
  _fromMidi = true;
  try { pluck(e.detail.note, e.detail.vel); } finally { _fromMidi = false; }
});
```

Inside the tool's note function: `if (!_fromMidi) mi.echoPluck(midi,
vel, durMs);`. The guard matters — a note that came FROM the FM-1 is
already sounding on the FM-1; echoing it back doubles the voice.

### `const mi` at the bottom is fine

Routing blocks define `mi` after the functions that reference it.
That's safe: the whole inline script runs before any input event can
fire, so `mi` is initialised by the time `pluck()` calls it. Don't
"fix" this by hoisting — keeping routing at the bottom is the
convention.

### Learn targets share one namespace

CC learn is persisted in `localStorage.mm_midi_prefs.ccMap` keyed by
target id. Use `'vol'` for every tool's master volume so one learn
covers all of them; prefix tool-specific sliders (`fm.ratio`,
`strings.decay`). Entries with `el` auto-bind to that range input
and fire `input` + `change` events, so the tool's own slider
listeners run unchanged.

### Mono instruments use last-note priority

SYNTH and BASS keep a `midiHeld` stack: first key attacks, later
keys glide (legato), releasing to a still-held key glides back, last
release lets the envelope go. Mirrors how a fret hammer-on works on
those tools.

### Web MIDI facts that bit us

- Chrome / Edge only. Firefox has it behind a site-permission flow;
  Safari doesn't ship it. Same requirement as the Baud Girl
  installer, so an FM-1 owner already has a working browser.
- `requestMIDIAccess({sysex:true})` prompts separately; if denied we
  fall back to `{sysex:false}` so notes still work and the panel
  reads "no sysex". Patch push needs the SysEx grant.
- `file://` is a secure context in Chrome, so the tools work opened
  straight from disk. Serving over `http://localhost` also works.
- Ports can appear after page load (statechange) or vanish mid-
  session; `_pickPorts` re-runs on every statechange and keeps an
  explicitly chosen port if it's still present.

### FM-1 facts (from ip2k/mvave-fm1-open-firmware bench notes)

- Class-compliant USB-MIDI + UAC1 audio, VID:PID `4C4A:C755`. One
  bidirectional port: `FM-1` (macOS CoreMIDI), `FM-1 Midi`
  (Windows), sometimes a bare `USB Composite Device` in Chrome on
  macOS — hence the manual port picker.
- Updater mode re-enumerates as `ota-FM-1` (`4D4A:4155`). We detect
  that name and refuse to treat it as an instrument.
- Sends nothing unprompted: no clock, no active sensing, no reply to
  the universal identity request or a DX7 dump request. It DOES
  answer the vendor identity query `F0 00 32 45 00 00 00 40 7F F7`
  with a 41-byte reply: a 7-bit LSB-first bitstream that unpacks to
  a 34-byte block starting `00 59 11`, with `FM-1_0xx` at bytes
  6..30. Stock is 014/015; Baud Girl FM-1+VA builds are 020+.
  `MidiInput.identify()` / `fm1DecodeIdentity()` implement this.
- Stock engine is the Dexed / msfa core; firmware analysis says it
  accepts DX7 voice dumps and parameter changes with no read-back.
  So we can push, never verify except by ear.
- Vendor SysEx header `00 32 45` is the firmware-update protocol.
  The identity query above is the ONLY message with that header the
  tools may send. Never send the upgrade command (`F0 22 24 35 7F
  F7`) or answer loader read requests (`00 32 41 41`) from these
  tools — that is a flasher, and there is no recovery for a bad
  write (one flash bank, no proven mask-ROM boot).
- Whether the knobs transmit CC (and on which numbers) is
  undocumented for both stock and Baud Girl firmware → MIDI-learn
  everywhere, never hard-coded CC numbers.

## Recent lessons

### 2026-10-01 — FM-1 hookup (first pass)

- Wired nine instruments (FM, SYNTH, BASS, DRUMS, STRINGS, ARP,
  LOOPER, DEMONS, TAROT SYNTH) plus a new FM-1 CONSOLE. THEREMIN,
  CHORDS, DRONES and AMBIENT are not wired: none has a natural
  key→pitch mapping (continuous pitch / progression walker / interval
  toggles / layer toggles). Decide a mapping before wiring, don't
  force one.
- The DX7 2-op → 6-op mapping (`dx7VoiceFromTwoOp`) is algorithm 1
  with OP3–6 silenced. Mod index 0..500 → modulator output level via
  a sqrt curve into 50..99; ms → EG rate via `99 - 22·log10(ms/5)`.
  Both are approximations tuned to keep preset *character*, not
  exact timbre. HARDWARE-UNVERIFIED as of this entry — first thing
  to test on the Deck is the "ALG 1 ONLY" parameter change in the
  console (the FM-1 screen redraws the algorithm if it took).
- The FM-1 CONSOLE asks the user which firmware is on the device and
  stores it in `localStorage.mm_fm1_firmware`. There is no way to
  read it back over MIDI, so self-report is the only option.

### 2026-10-01 — firmware install helper, not a flasher

- `fm1_flash.sh` wraps Baud Girl's web installer instead of flashing.
  Her FM-1+VA image only exists inside that installer, and the update
  protocol has documented unknowns (an obfuscated step-1 check,
  syscmds 33–36/48 unsafe to send). The script automates everything
  around the write: Desktop Mode, browser + Flatpak MIDI device
  access, FM-1 present and NOT behind a hub/dock (sysfs name has a
  `.`), Deck on AC, version read before/after, a logind sleep+idle
  lock for the browser's lifetime, and a dedicated browser profile so
  `flatpak run` blocks until the installer window closes.
- Post-flash states: `4c4a:c755` = booted; `4d4a:4155` = parked in
  the loader (resumable: re-run, her installer resumes); neither =
  stop, read docs/07 in the open-firmware repo.
- Raw-MIDI identity (`amidi`) is often blocked by PipeWire holding
  the port ("Device or resource busy"). The console's IDENTIFY goes
  through Chrome's ALSA-sequencer path and works alongside PipeWire.
- Correction to the first entry: firmware CAN be read back, via the
  vendor identity query. Patches still can't.
- Tested here against a fake sysfs tree and a synthetic reply only.
  The decoder was checked against the real reply prefix published in
  the open-firmware docs (unpacks to `00 59 11 … "FM-"`).

### 2026-10-01 — first hardware run on the Deck

- Identity query over `amidi` worked on real hardware first try
  (PipeWire did NOT hold the port): stock unit reads `FM-1_015`.
  Decoder confirmed.
- The Deck has ONE USB-C port. With the dock attached, the FM-1 sits
  behind the dock's hub (sysfs `1-1.1`, hub product `USB2.0 Hub`),
  and AC power comes through that same dock. Keyboard and mouse live
  on the dock too, so the user flashes THROUGH the dock (user
  decision). The hub check stays a warning, not a blocker. Reduce the
  risk instead: unplug every other USB device from the dock except
  the keyboard and mouse, keep the dock on AC, and don't touch the
  dock cable during the write. An interrupted write parks the synth
  in the loader, and re-running the script resumes it.
- The GO prompt was case-sensitive and a lowercase `go` quit. Now
  case-insensitive.

- The installer is at https://baudgirl.com/work/FM-1+VA/install, not
  the site root. Opening the root showed a page where "nothing
  happens". Chrome or Edge only: Firefox loses the FM-1 when it
  reboots into the loader mid-install.

- First real flash on the Deck succeeded: stock `FM-1_015` became
  Baud Girl `FM-1_093`, flashed through the dock hub on AC. The
  console's IDENTIFY read the new version while a raw `amidi` read
  was blocked by an open Chrome tab. Prefer IDENTIFY when Chrome is
  running.

### 2026-10-06 — Felucca and SLOOP firmwares

- Both are open source (GPL-3.0). Felucca is hugelton/Felucca by Leo
  Kuroshita (Hügelton). SLOOP is isod89/sloop-fm1 by 3dSam and is a
  Felucca fork. Read the repos' `web/EDITOR_PROTOCOL.md` and
  `firmware/src` before guessing anything about them.
- USB identity changes: both re-enumerate as `1209:0001` with the
  MIDI port and product named "Felucca" (SLOOP keeps the name on
  purpose). `1209:0001` is a shared pid.codes hobby ID, so the flash
  script only accepts it when the product or ALSA card id says
  Felucca. The updater loader stays `4d4a:4155`.
- Version: the vendor identity query still answers, with `FM-1_9XY`
  built from release X.Y (Felucca 1.0.x is `FM-1_910`, SLOOP 2.3 is
  `FM-1_923`). The ranges collide, so `fm1DecodeIdentity` calls 9xx
  "felucca family". The editor INFO request `F0 7D 46 4C 01 F7` is
  read-only and names them: "FELUCCA v1.0.3" or "FELUCCA SLOOP 2.3".
  Only send INFO when the port is named Felucca or the vendor reply
  was 9xx. Stock and Baud Girl never see it (browser-tested).
- Both are multitimbral. MidiInput now takes `{role}` (lead / bass /
  chords / drums). OUT channel 0 means auto, which resolves through
  `FM1_PROFILES`: Felucca lead 1, bass 2, chords 3, drums 4 (track 4
  needs its engine set to DRUM). SLOOP is 1 / 2 / 3 / drums on 10.
  Stock and Baud Girl stay on ch1. A fixed OUT channel in the console
  overrides auto for every tool.
- Both drum engines take General MIDI drum notes, so the drum tool's
  GM map works unchanged.
- Neither has a DX7 engine. `mi.dx7Ok()` blocks the console patch
  push, ALG 1 ONLY, and RIFFMASTER FM's push. Sounds are edited in
  each firmware's own web editor over its FL SysEx protocol. We don't
  speak that protocol yet, and it's the natural next integration.
- Recovery differs. SLOOP has a USB rescue (hold OCT− at power-on,
  then reinstall). Felucca's installer says a failed install that
  won't boot needs a Transporter dongle. Both installers ask for a
  direct cable, which conflicts with the Deck-through-dock setup, so
  the script warns harder for Felucca.
- Installers are hosted: hugelton.github.io/Felucca/ and
  isod89.github.io/sloop-fm1/. SLOOP's INSTALL-SLOOP.bat is
  Windows-only and not needed. `fm1_flash.sh --firmware
  baudgirl|felucca|sloop` picks one, or the script shows a menu.
- Tested against fake USB/ALSA trees and a fake Web MIDI port in
  headless Chromium (18 firmware × tool combinations). Not yet on
  hardware with either firmware.

### 2026-10-10 — the firmware scene, as a registry

- `godot/tools/fm1_firmwares.js` is now the single source of truth for
  every firmware: USB identity, identity ranges, INFO match, roles, DX7,
  installer, recovery. `midi_input.js` builds `FM1_PROFILES`, port hints
  and classification from it. The console's picker, the atlas page and
  `fm1_flash.sh` (python reads the JSON between the `FM1-JSON` markers)
  read it too. To add a firmware, add a JSON block (strict JSON); no code
  changes are needed.
- **Correction to the 2026-10-06 entry:** the Felucca family's default
  sounds (`TRK_DEF` in engines.c / ui.c) are track 1 bass, track 2
  pad / keys, track 3 lead (SLOOP: 808 BOOM / RHODES / LOFI FLUTE). The
  role map is lead 3, bass 1, chords 2. The first pass had lead 1 and
  bass 2, which sent bass lines into lead patches.
- Felucca forks all enumerate as `1209:0001`. Some keep the port name
  "Felucca" (SLOOP, SLOOP ALG), others rename it ("X0X FM-1", "Jangada",
  "Melodee"). Identity numbers collide: Jangada 0.9 and Felucca 0.9 are
  both FM-1_909, and SLOOP ALG FM-1_985 collides with a Doom port. The
  rules are:
  - The INFO string decides, matched against registry `info.match` in
    order, with specific forks listed first.
  - A unique port name decides when the editor is silent.
  - Anything else is "felucca-family": routing stays on ch1, no DX7.
- Never treat these as playable: FM-1_000 (USB rescue), `ota-…` / any
  "* Update" port (1209:0002), 4c4a:8057 WL80UBOOT. The flash script
  blocks on boot mode.
- Jangada and Melodee DO accept DX7 SysEx (live FM6 edits / banks), so
  `dx7: true` there. SLOOP's is editor-only.
- The editor INFO wait is 800 ms. Replies take 10–50 ms, and a long wait
  delayed port-name fallback past the tools' first paint.
- B-Boy Edition's repo is gone. fwradar.com was never readable from the
  sandbox, and Groove OS's USB / MIDI facts are unverified (closed
  source). Re-check those three before relying on them.

### 2026-10-10 — firmware emulators, FORGE, and the DAW

- Felucca 1.5.1 and X0X 1.0.5 run in the browser from their own
  WebAssembly builds (`fm1_emu.js`, `vendor/fm1emu/`). The wasm and
  worklet source ship as base64 classic-script wrappers, because file://
  blocks fetch. `pack.py` regenerates them byte-for-byte. Registry
  entries carry an `"emulator"` key.
- X0X's upstream web build has NO MIDI input: no `web_midi` export, and
  the queue is compiled out. The vendored `x0x_midi.wasm` is rebuilt from
  source plus a patch that adds only `web_midi` and `web_sample_rate`
  (clang 18 + wasi-libc). It gives bit-identical audio to upstream on the
  same panel input. Upstream `x0x.wasm` is kept beside it; see
  `SOURCE.md`.
- Felucca's `web_midi` drops realtime bytes. The adapter swaps them into
  the firmware's own USB-MIDI ring. The firmware follows clock only when
  its CLOCK page has CLK = USB (HOME, HOME, knob 3; saved with the
  project).
- Emulator channel maps, checked in source:
  - Felucca: ch1–4 are tracks 1–4; ch5–16 are ignored.
  - X0X: 909 ch10, 808 ch11, 303 A ch2, 303 B ch3, break ch4 (slices on
    notes 36–43). X0X has no CC support.
- The emulators must run at 44.1 kHz. At 48 kHz they still run but warn
  that pitch is 147 cents off, so the DAW opens its AudioContext at
  44.1 kHz.
- The vendored firmware is GPL-3.0, with its LICENSE files alongside.
  These are dev tools that don't ship with the game. Settle the repo's
  own licence before publishing the tools.
- Not hosted: Jangada (its build needs zig from ziglang.org), and Lunar
  Modulator (MIT, but a different `fm1w_*` API that needs its own
  adapter).
- FORGE (`forge_synth.js`) is the Phase Plant-style synth:
  - Structure: generators → three lanes of snap-ins, a mod matrix
    (`{src, dst, depth}` in knob space), and 8 macros.
  - 29 presets (105 since the 2026-10-11 library), with ids stable for the DAW. A DAW that schedules
    noteOn/noteOff pairs ahead delivers them out of time order, which
    broke mono last-note priority. Mono events now go through a
    time-sorted log that rewinds.
- Web Audio feedback delays can't go below 128 samples, so the comb
  filter is capped at 340 Hz and the flanger at 3–9 ms.

### 2026-10-10 — finger controls for the Deck touchscreen

- User ask: press and slide (up/down AND left/right) for knobs and
  sliders on the Deck's touchscreen. `touch_controls.js` is the shared
  answer. Include it after `audio_kit.js` in any tool page.
- Sliders: every `input[type=range]` is RELATIVE under a finger, so the
  value never jumps to where you pressed:
  - Up or right raises; 220 px of travel covers the full range.
  - A second finger down gives fine control (1/5 speed).
  - Double-tap resets to the slider's starting value (`data-default`
    overrides).
  - The mouse keeps the native behaviour.
  - The browser's own slider touch handling is stopped with a
    non-passive `touchstart` preventDefault. Pointer events still
    arrive.
- Knobs (FORGE, FM-1 emulator panel): drag amount = dx − dy, so right
  and up both turn clockwise. When fine mode toggles mid-drag, re-base
  the start point or the value jumps.
- Canvases: `TouchControls.gesture(el, {grab, move, end, tap, doubleTap,
  longPress, scroller})`.
  - If the press grabs nothing, the finger pans the scroll parent. The
    canvas needs `touch-action: none` (set by `gesture()`), or Chrome
    pans the page and cancels the pointer.
  - Long-press (550 ms) is the touch right-click: delete.
- `preventDefault` on a touch `pointerdown` suppresses the compatibility
  mouse events. Existing mousedown handlers then never double-fire, so
  the mouse and finger paths can live side by side.
- Hit zones that work for a mouse fail for a finger. A 1/16 note in an
  8-bar pattern is about 7 px wide, so a 16 px "edge = resize" zone ate
  every press and the note could never move. On a finger, edge-resize
  only applies to notes ≥ 18 px wide, on their last third. The roll also
  has ZOOM ±, and rows grow on `(any-pointer: coarse)`.
- Testing: headless Chromium with `hasTouch: true` plus CDP
  `Input.dispatchTouchEvent` (touchStart / touchMove / touchEnd)
  produces real `pointerType: 'touch'` events. Playwright's
  `touchscreen.tap` alone can't drag.

### 2026-10-11 — PATCH BANK, the sampler, the DX7 engine

- User ask: a patch bank library of publicly available patches and
  instruments.
- The catalog is `patch_sources.js`, generated by
  `patch_sources_build.py` from blob-less clones with pinned commits.
  Never hand-edit it; re-run the script.
- Licence decides the "in game" verdict, so check the repo's own
  LICENSE / README before adding a source:
  - **free:** CC0, GeneralUser GS, jRhodes3d ("music made with it is
    CC0").
  - **credit:** CC BY (FluidR3, Salamander, tonejs mixed).
  - **share-alike:** CC BY-SA (Musyng Kite, FatBoy).
  - **excluded:** non-commercial (Tone.js "casio") and unknown origin
    (Tone.js drum-samples).
- Nothing is vendored. Files come from raw.githubusercontent.com, which
  sends CORS *, so a file:// page can fetch them. They're cached in
  IndexedDB `mm_patches`, so after the first download everything works
  offline.
- github.io is blocked in the cloud sandbox (it works on the Deck), so
  every source must be a GitHub repo.
- Testing in the sandbox:
  - Headless Chromium does NOT use `$HTTPS_PROXY` on its own. Launch
    with `proxy: { server: process.env.HTTPS_PROXY }` and a context
    with `ignoreHTTPSErrors`.
  - The proxy throttles bursts (`ERR_TOO_MANY_RETRIES`).
    `PatchBank.fetchBytes` retries four times with back-off, which also
    covers Deck Wi-Fi drops.
- **FM-1 voice-push bug:** `dx7VoiceSysex` sent `F0 43 1n 00 01 1B`.
  Sub-status 1 is a PARAMETER CHANGE, so Dexed and the FM-1's Dexed core
  read it as "set param 1 = 27" and threw the voice away. A single-voice
  dump is `F0 43 0n …`. Confirmed in Dexed's PluginMidi.cpp. Still
  unconfirmed on the hardware.
- `dx7_synth.js` is ported from the Apache-2.0 msfa files. Checked
  against a native msfa build over 1088 voices: envelope correlation
  ≥ 0.98, level within 0.06 dB.
- Note-named sample folders (`sampler.js` `instrumentFromFiles`):
  - A "layer" with only a few notes (tonejs cello "F2 v2", "G2 v2") is a
    pair of alternate takes, not a velocity layer. Spread on its own it
    covered the whole keyboard at high velocity. Fold it in as round
    robin.
  - After decoding, `respread()` re-spreads key ranges across the files
    that loaded, so one failed download doesn't leave a hole.
- Loudness varies about 25 dB between sources (FluidR3 midi-js peaks
  near −25 dBFS). `normGain` aims a typical note at −9 dBFS. SF2 banks
  are left as voiced.
- Keep DAW defaults light. Meatbass pizz (eight `#include`d ensemble
  maps, 4584 zones) and Weresax "Sax" (four mic maps) took minutes. The
  per-style picks are one GeneralUser GS download plus jRhodes3d.
  Salamander is thinned to 4 velocity layers when loaded.
- Growlybass sounds an octave below the key, by design: its SFZ maps
  written bass pitch, like a real bass guitar. It's not a sampler bug.
- A session restart killed a background agent mid-task, but the files it
  had written were intact. Before re-delegating, check what's on disk:
  syntax, exports, then a real test.

### 2026-10-11 — FM-1 CHECK-OUT: verifying hardware facts with the user

- Hardware facts nobody has verified call for a guided check-out
  page (`fm1_checkout.html`), not more console buttons. Split every
  check into two kinds:
  - what the browser can measure: replies, dump bytes, clock timing,
    audio onset;
  - what only the user can hear or see, answered ✔ / ✘.

  Record both in one localStorage JSON (`mm_fm1_checkout`). COPY AS
  TEXT hands it back to Claude, so registry claims can be promoted
  from "documented" to "verified on the Deck".
- Every step adapts from `fm1_firmwares.js`:
  - part channels;
  - whether INFO SysEx is sent (only Felucca-family ports or 9xx
    version replies);
  - DX7 (N/A, editor, or push);
  - clock setup text.

  No firmware fact lives in the page itself.
- FM-1+VA overwrites the selected stored preset on a DX7 push. The
  page refuses to send until the user ticks the acknowledgement.
- Round-trip latency:
  1. Schedule note-ons with the DAW's `perfTime` mapping.
  2. Find the audio onset on the AudioContext frame clock with a
     frame-stamped probe worklet.

  The median then means exactly what the DAW's `latencyMs`
  alignment means. It is saved as `mm_fm1_latency_ms`. The DAW reads
  it as its FM-1 RETURN latency, at start and live when CHECK-OUT runs
  in another tab (see the audio playbook's recording lesson).
- Chrome's MediaStream chunking adds about 10 ms jitter steps on a
  real input. Keep the median, not the mean.
- `tests/mocks/fm1_mock.js` is a fake FM-1 (version / INFO replies,
  MIDI thru, a USB audio input gated N ms after each note-on). Use it
  for any new FM-1 tool test instead of writing another mock.
- Open items:
  - The page is unverified on real hardware.
  - The registry has no `cc` field yet, so X0X users just answer NO
    on the CC step.

### 2026-10-11 — DAW performance tools: scale lock, chords, arp, groove, STEP view

- `daw_perf.js` (global `DawPerf`) holds the per-track live chain:
  keys → scale lock → chord → arp → device. Settings live in
  `track.perf`, the project groove in `project.groove`. Everything is
  optional; a project without them takes the old code paths untouched.
  Theory comes from `seqgen.js` (`SCALES`, `deg2midi`, `rng`, `hash`).
  Never copy the scale tables.
- **Record what you hear.** Every note the chain plays goes through
  `engine.perfRecord(tr, n, vel, on, when, {generated})`:
  - arp steps are already on the grid, so they are recorded at their
    scheduled time;
  - chord / scale-locked notes follow the key, so they get exactly the
    timing a raw MIDI note gets: `recNow()`, the input event's own
    time stamp. Never `latencyMs`, which is the *audio* round trip.
    (Merge note: the PERF branch first used `when − latencyMs`. Once
    recording split latency into three numbers, that recorded chord
    notes about 13 ms early. The `daw_perf` hook test now pins this.)

  The recording code owns `recordMidi` and may replace the hook. With a
  chain on a hardware track, the processed notes go out to the synth,
  so set its local control off.
- **Arp clock.**
  - While the transport plays, steps come out of the engine's own
    look-ahead windows (`scheduleRange` → `Live.range`), so loops,
    tempo and groove follow for free.
  - A first key also catches up the steps between now and the
    scheduled horizon, after a 15 ms chord window.
  - Stopped, a 25 ms timer free-runs the arp at the project tempo from
    the first key.
  - The free → transport hand-over skips any step within half a step
    of the last one played.
- **Live = offline needs pure functions, not counters.**
  - The clip chain (`processNotes`) is a pure function of the pattern,
    cached per pattern and settings signature.
  - Step probability and humanize are keyed by (seed, track id,
    absolute tick, note), never by "how many notes so far".

  Live notes then matched offline to < 1e-6 s and the same velocities.
- **Proving "unchanged" needs the right oracle.** Chromium offline
  renders are not sample-reproducible, not even the old engine against
  itself:
  - a bare oscillator differs by about 1 float ULP (6e-8);
  - FORGE differs by about 1e-5, and also reaps voices on wall-clock
    `setTimeout`.

  So the suite compares the device event stream (every noteOn /
  noteOff: note, velocity, time, channel) against the engine from
  before PERF (`git show <commit that added daw_perf.js>^`), and holds
  the audio to that noise floor.
- **BasicSynth bug.** `noteOff(n, when, immediate)` received the
  engine's MIDI channel as `immediate`, so every note was cut the
  moment it was scheduled; basic-synth bounces were silent. The
  signature is now `(n, when, ch, immediate)`. When spying on a
  BasicSynth, ignore its own time-less retrigger `noteOff`.
- **STEP view.**
  - It draws the same pattern notes as the piano roll; a note shows in
    the step its start rounds to.
  - `pattern.steps` keeps the resolution; `note.p` is the step's
    probability.
  - Tap toggles a step, a vertical drag sets velocity, and long-press
    or right-click opens VEL / LEN / PROB.
  - Cells and panel buttons are ≥ 36 px on every pointer.
- Open items:
  - A note pushed ahead of the very first tick of a bounce (negative
    role offset or humanize) starts at 0 offline; live plays it early.
  - Arp latch, chord learn and the PERF chain are unverified with the
    FM-1 keys on the Deck.

### 2026-10-11 — firmware names are what the user calls them

- The user runs Baud Girl's firmware and reported it "isn't in the
  list". It was there all along, as `FM-1+VA`, which is the product
  name. The user knows it by its maker. The registry `name` is what
  every picker, chip and status line shows, so it now reads
  `Baud Girl FM-1+VA`. Name an entry so its owner would recognise it,
  maker included when that's how people refer to it.
- Vendor identity used to name a registry firmware by its raw version
  string (`FM-1_097`). `fm1MergeIdentity` now gives the registry name
  plus the version, e.g. `Baud Girl FM-1+VA (FM-1_097)`.
- The identified name is cached in localStorage (`mm_fm1_firmware`
  plus its name key). An old label stays until the next IDENTIFY or
  CONNECT.

### 2026-10-11 — "Midi Through Port-0" is never the FM-1

- On the Deck, the check-out asked the user "Is “Midi Through Port-0”
  your FM-1?" while the FM-1 was plugged in over USB-C. That port is
  the ALSA loopback Linux always creates. Chrome reached it through
  the same ALSA sequencer the FM-1 would use, so the sandbox was fine:
  Linux itself had no FM-1 MIDI device. Suspect, in order:
  1. the cable (charge-only USB-C);
  2. the synth not switched on;
  3. the dock.

  `cat /proc/asound/cards` on the host settles it.
- `midi_input.js` now ranks `MIDI_SYSTEM_PORT` (`/^midi through\b/i`)
  below every other port and never auto-picks it, in every tool. The
  check-out explains it in plain words instead of asking.
- The check-out's connect step re-rendered its card in `finally`. That
  erased every connect message: no port, permission denied, updater
  mode. The last message is now restored after the re-render. Tests
  should assert the words the user sees, not just check statuses.

### 2026-10-11 — first real CHECK-OUT: Baud Girl FM-1+VA (FM-1_093)

- First hardware-verified facts, stored in the registry's new
  `verified` / `cc` / `keys` fields. All of them came from the user's
  check-out on the Deck over USB-C:
  - the port is "FM-1 MIDI 1";
  - it answers the version query;
  - it plays USB notes on ch 1;
  - its keys send ch 1 at a **fixed velocity of 90**;
  - **CC 74 moves the sound; CC 71, 1 and 7 don't**;
  - **the knobs send no CC at all**.
- DX7 push, clock and audio latency are still `pending`. Never
  promote a fact from documentation to `verified` without a
  check-out (or equal) result.
- What the tools now do with these facts:
  - DAW CC lanes on a hardware FM-1 list the answered CCs first (✔)
    and mark ignored ones "no effect on …".
  - Knob LEARN says the knobs are silent and to use another
    controller.
  - The check-out treats "no knob CC" as a finding, not a FAIL (the
    check is optional now).
- Lesson: when a check's "no" is a legitimate property of a firmware,
  don't mark it required. The step showed FAIL for a synth that works
  fine.
- Fixed velocity 90 means takes recorded from the FM-1 keys have flat
  dynamics. Use the piano roll's HUMANIZE or the groove accents if a
  part needs them.

### 2026-10-11 — second CHECK-OUT pass: DX7 works; the audio input had no name

- **DX7 on Baud Girl FM-1+VA (FM-1_093) is verified.** The three
  single-voice dumps sounded as described, and an algorithm parameter
  change was heard at once and redrew the screen. The registry moved
  DX7 from `pending` to `facts`. Clock follow was skipped and is still
  pending.
- **The latency run measured 149.9 ms ± 0.4**, on an input whose name
  *and* device id were empty. Chrome hides both unless a capture is
  live or the permission was kept; "Allow this time" ends with the
  stream. The page opened the permission stream, stopped it, *then*
  enumerated, and got one blank entry. Opening a blank device id gives
  the system default input, which on the Deck may be the built-in mic
  hearing the FM-1's speaker. So that number is not trusted as the
  FM-1's USB round trip.
- Fixes:
  - `AK.inputs.list()` re-enumerates *while* a short permission stream
    is open whenever names are hidden. This applies to every tool that
    records.
  - The check-out fails "input found" for an unnamed pick and says why.
  - Test: the mock hides names on the first enumerate.
- Whatever the input was, ±0.4 ms jitter means a fixed buffer, so
  takes line up once it's measured. But 150 ms is far too late to
  *monitor* through the browser. Listen on the FM-1's own output while
  recording.
- `daw_rec`'s count-in check once landed at tick 193 instead of 192
  (+3.4 ms). MIDI event time → AudioContext time goes through
  `getOutputTimestamp()`, which jitters a few ms under load. Tests now
  allow ±1 tick / ±4 ms. Don't promise sub-tick MIDI placement.

### 2026-10-11 — third pass: telling USB audio from a mic when Chrome hides names

- On the Deck's Flatpak Chrome, input names stayed hidden even when
  the list was re-read during a live permission stream. Headless
  Chromium with auto-granted permissions always shows names (on
  `file://` too), so the real prompt couldn't be reproduced. The cause
  is unconfirmed.
- **Evidence beats names.** That run's quiet level was −∞ dBFS: exact
  digital silence between notes. A microphone (the first run read
  −71 dBFS) always has a noise floor, and USB audio from a synth does
  not. The check-out now passes an unnamed input on digital silence
  and fails it on a noise floor.
- It also reads the open stream's own track label, which Chrome often
  fills in when the device list is blank.
- `MediaDeviceInfo.label` is read-only, and the page is `"use strict"`.
  The first draft assigned to it and would have thrown on the Deck the
  moment Chrome gave a track label. The mock's streams have no tracks,
  so the tests couldn't catch it.
- The DAW's "Auto" latency picked FM-1 RETURN only for an FM-1-named
  input. An unnamed input now counts as the FM-1 when CHECK-OUT
  measured it and play-along was never calibrated.
- Verified: FM-1 USB audio on the Deck; round trip 142.9 ms
  (jitter 3.3 ms) in Flatpak Chrome, 149.9 ms in an earlier run. Takes
  align. Never monitor through the browser at this latency.

### 2026-10-11 — the instrument library: FORGE 29 → 105 presets, pools, KIT styles, finger browser

- User ask: "feels like more instruments and pads should be present."
  FORGE gained 76 presets: 19 pads (noir / tremolo / silver-screen
  strings, crypt + angel choirs, bowed glass, bowed saw blade, tape
  wobble, chapel organ, "Air · Nave", sub drone, motion and gated pads,
  FM frost…), 9 keys, 7 basses, 6 leads, a new `winds` category (7:
  FM brass, Harmon trumpet, flute, clarinet, sax, harmonica, horns),
  9 plucks / mallets / bells, 6 ambient textures + drones, 10 kit
  pieces, 3 fx. The 29 originals are byte-identical (their FNV
  fingerprints are pinned in `tests/library.test.js`).
- **Preset design rules that held:**
  - Macros start at 0 = the patch as voiced. Each macro adds one
    direction only. An effect a macro brings in sits in the lane at
    mix 0 (it still runs, so keep a lane to ~5 snap-ins).
  - Route only to real targets: `fx.<sid>.<p>` needs `p` in that
    snap-in's `mods`; `gen.<id>.fm` only on FM ops, `.cutoff` only on
    noise gens, `.morph` only on wavetables. `normalizeState` drops a
    bad route silently, so the library suite checks every one.
  - Pitched noise = a bandpass noise gen plus `note → gen.<id>.cutoff`
    at 0.5 (12000 ct × 0.5 / 60 st = exactly 100 ct per semitone).
    That is the bow friction, flute breath, wind and "Air · Nave".
  - The amp envelope can't be modulated. Tremolo is an LFO →
    `amp.level`; `rand → lfo.N.rate` keeps a chord's voices out of step.
  - A macro that raises a noise gen's level is not a "click": the amp
    envelope shapes it into a noise tail. Clicks are env3 routes.
  - Bandpass Q eats level: lower `nres` before reaching for gain.
    Reverb / delay / chorus mix also lowers the dry. Master gain stops
    at 1.5; a lane `gain` (up to 1.5) is the next stage.
  - Mono vs poly is part of the patch's job: a legato patch on a chord
    track plays one note. Composer pools: bass = mono / legato,
    chords + pad = poly (the suite checks).
- **Audit before trusting your ears (there are none in the sandbox):**
  render every preset offline at 16–22 kHz with a per-category
  pattern, then compare RMS over the active frames against the
  category's originals, peak, sustain at note-off, and a fingerprint
  (24 log bands + 16-point envelope + 10 ms modulation + spectral
  motion). The first pass caught pads 15 dB quiet (pitched-noise
  air), a wind bed 23 dB quiet, and near-twins (reese ≈ fat ladder,
  Harmon ≈ harmonica) — fixed by a different filter type and
  envelope, not by gain. All 105 renders take ~7 s in the suite.
- Peaks: as voiced ≤ 0.99. With all eight macros up a patch may lean
  on FORGE's soft limiter (0.98 ceiling; the waveshaper's oversampling
  overshoots to ~0.995), never past full scale.
- **To add a preset:** append to `FORGE_PRESETS` with a category from
  `PRESET_CATEGORIES` (a new category goes there and in the editor's
  select order), `tags` (DAW style ids first, then character words —
  they drive the browser's chips and search), 8 named macros on
  melodic patches. Run `run_tests.sh library`, then add it to
  `SeqGen.FORGE_POOLS` for the styles it suits. Never edit a shipped
  preset: copy it under a new id.
- **Composer:** `SeqGen.presetFor(style, role, seed)` picks the style's
  own preset or a pool alternate by `hash(seed:forge:role)`, outside
  the note RNG. A seed keeps its notes; its instruments changed once,
  with this library.
- **KIT:** `KIT_MAP` now has a real ride, crash, shaker, tambourine,
  cowbell, congas and clave (they used to be hats and the rim).
  `KIT_STYLES` swaps pieces per style: 808 kick for trap, felt kick
  for lo-fi, brushes for noir. A saved kit keeps its own map, and a kit
  is built straight from that map. Building the style's voices first
  and then swapping them shifted the seeded `Math.random` in
  daw_perf's old-engine comparison; that test now compares with a
  pre-library kit map, since the old engine can't build the new
  pieces.
- **PATCH BANK:** the builder only *looked* pinned: it cloned branch
  tips, so a re-run could move every source. `SOURCES[*].commit` now
  pins each source (`--update` reads the tips on purpose); the
  regenerated catalog is identical for the old 21 sources. Added
  VSCO 2 Community Edition (its `SFZ` branch, CC0, 75 programs: string
  sections, solo strings, brass, woodwinds, harp, organ, mallets,
  bells) and Karoryfer's Gogodze Phu (CC0 hand drums). Skipped Splendid
  Grand Piano: "public domain by AKAI" with no licence file.
  - VSCO WAVs are ~2 MB each: one articulation is 20–120 MB on first
    download. Only two are in `PATCH_POOLS` (noir cello, ambient harp);
    the rest of the widened pools are GeneralUser GS programs, which
    are one download.
  - VSCO maps piccolo and glockenspiel at written pitch, so they sound
    an octave or two off (like Growlybass). The network suite checks
    the flute instead.
- **Pickers by finger:** `ForgeSynth.mountBrowser` is the one browser:
  search, category chips, style chips, ≥ 44 px tiles, a tap loads and
  previews. The DAW's PRESET button and FORGE's ☰ BROWSE both use it;
  a FORGE device added from the menu opens it. The PATCH picker gained
  category chips and 40 px rows. Filters are remembered per browser
  (`mm_forge_browse`).
- Open items: nobody has listened to the new presets on the Deck yet
  (the numbers say balanced, not beautiful); CPU of 12-voice pads on
  the Deck is unmeasured. The heaviest is `choir_angel` at 10
  oscillators per voice, against `strings_ensemble`'s 9.

### 2026-10-13 — sound design in FORGE: ambience beds, transitions, hits (105 → 126 presets)

- Why: temp tracks are getting a sound-design layer — a "texture" part
  (one long held note per section), an "fx" part (risers into
  sections) and a "hit" part (one-shots on downbeats). The composer
  names presets by id, so these ids are a contract:
  - Beds (`ambient`, tag `texture`): `amb_vinyl` (two `vinyl` loops at
    different rates + surface noise + 33⅓ rpm rumble), `amb_tape_hiss`
    (cassette hiss, wow on the top end, dropouts), `amb_room_tone`
    (very low interior air + HVAC), `amb_fluor_hum` (60 / 120 Hz
    ballast + CRT hum, slight flicker), `amb_life_support` (low hum,
    air circulation, slow pump pulse), `amb_crickets`, `amb_cicadas`
    (bandpass noise × ring mod for the buzz, swells over ~7 s),
    `amb_surf` (noise swells every ~7–11 s), `amb_fire` (crackle loops
    over a soft roar), `amb_thunder` (rolls ~12–14 s apart over low
    rain), `amb_city` (far traffic, the odd distant horn),
    `amb_clock` (tick-tock, 1 a second, quiet room), `amb_forest_night`
    (pine wind, an owl every 10–13 s), `amb_modem` (dial-up handshake
    then data hiss).
  - Transitions (`fx`, tag `transition`): `fx_reverse_swell`,
    `fx_whoosh`, `fx_tape_stop`. Hits (`fx`, tag `hit`):
    `fx_sub_drop`, `fx_bell_hit`, `fx_wood_knock`, `fx_glass_ping`.
- **Beds are pitch-free.** Every generator is `mode: 'fixed'` or an
  unkeyed noise, and no route reads `note`. Whatever note the composer
  holds, C3 and C4 give the same audio (the suite checks this to
  0.0 dB).
- **Beds stay poly.** Mono / legato *kills* the old voice when a new
  note starts, so at a section boundary the bed would drop out and
  fade back in. Poly overlaps the old release with the new attack.
  The price: two held notes of a sample bed add up in phase, so a
  sample layer's level has to leave room for that (the library render
  holds two notes).
- **Events need a sample source.** Linear mod routes can't gate.
  S&H into a level makes random steps all the time, not an
  occasional event. So intermittent things are built-in generated
  sources: `crickets`, `fire`, `modem`, `owl`, `thunder`, `clock`,
  `horns`, `tapehiss` (dropouts). Each is written *circularly* (an
  event past the end wraps to the start), so a loop has no seam. Each
  has a `rate` cap (11–32 kHz) to keep memory small. The first event
  comes a few seconds in (owl 3.4 s, thunder 3.8 s) so a bed opens on
  its bed. Noise + LFOs still did the rest: surf (an S&H on the swell
  LFO's rate randomises the period), cicadas, wind, hums.
- **A transition can't know how long it is held.** The reverse swell
  is two linear ramps multiplied (amp attack × env1 → generator
  levels). The brightness keeps opening to 6 s, so a one-bar hold
  peaks lower than a four-bar hold. A short release makes the
  reverse-cymbal cut at note-off. The whoosh and tape stop are fixed
  ~1 s events from note-on, so start them a beat before the downbeat.
- **Tape stop = a product of ramps.** Pitch = −(saw LFO × env1): the
  retriggered saw rises linearly from 0, and env1 → `lfo.1.amount`
  scales it. So the fall is t², slow then plunging, like a slowing
  reel. env2 → `amp.level` −1 (with `velSens` 0) takes the level to
  exactly 0 at 1 s. Give those envelopes long releases. Otherwise
  note-off snaps the level route back before the amp release ends,
  and you hear a blip.
- **Flake found and fixed: the reverb IR cache was FIFO.** Every new
  `ForgeSynth` builds the default patch (reverb 1.8 s) before
  `loadPreset`. Once a page had used more than 16 reverbs, that IR
  kept getting evicted and rebuilt from fresh `Math.random` noise. So
  two seeded renders of the same preset drew different numbers, and
  `amb_surf` measured 1.1 dB apart at C3 and C4. `irFor` is now LRU
  (a hit moves the key to the back). Same seed, same cache, same
  audio.
- Listening by proxy: spectrograms from
  `ffmpeg -lavfi showspectrumpic` of offline renders (read as images)
  caught a steady 837 Hz line in the reverse cymbal (its "metal"
  squares were too low, now 1.4–3.2 kHz) and the tape stop's
  note-off blip. Levels relative to `amb_rain` (single held note
  ≈ −19 dB RMS): beds sit at about −21 to −33 dB (room tone and clock the
  quietest).
- Open items: not yet heard on the Deck. `seqgen.js` doesn't know
  these ids yet; the composer rewrite will wire texture / fx / hit
  parts to them.

## TEMPLATE

```
### YYYY-MM-DD — <one-line summary>

- <lesson>
- <lesson>
```
