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

## TEMPLATE

```
### YYYY-MM-DD — <one-line summary>

- <lesson>
- <lesson>
```
