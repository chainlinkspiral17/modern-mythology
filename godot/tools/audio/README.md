# slowstick_synth — audio tool

Stdlib-only Python soft-synth for the Modern Mythology project.
Renders authored compositions (JSON) or standard MIDI files to
WAV files Godot can load directly.

## In-fiction

The pipeline Marc Ostrom used at Oneironautics Inc. Portland to
render the loops on the Estuary series slowsticks. A small
soft-synth built around the same 3-oscillator saw + saw +
sub-triangle voice used inside the games' PDP Riffmaster
kids'-synth toy (see `godot/scripts/PDPRiffmaster.gd`), an ADSR
envelope, and a handful of authored instruments for the
different musical roles a slowstick score needs — lead / pad /
bass / arp / drone / fluorescent hum / rain.

## Out-of-fiction

- Pure Python, stdlib only (no numpy, scipy, pyogg, mido).
  Same discipline as `godot/tools/landscape_sim/estuary_one.py`.
- Deterministic. Same input → same output byte-for-byte.
- 16-bit mono 44.1 kHz WAV by default. Stereo, 24-bit, and
  arbitrary sample rate via flags.
- MIDI parser is a minimal built-in for Format 0/1 note-on /
  note-off / tempo / program-change events. Standard DAWs
  export to this fine.

## Three entry paths

### 1. compose · JSON → WAV

The primary authoring path. A composition is a JSON file with a
tempo, time sig, and a list of tracks; each track has an
instrument name and a list of notes (bar / beat / duration /
velocity / pitch by name or MIDI number).

```bash
python3 godot/tools/audio/slowstick_synth.py compose \
    godot/tools/audio/compositions/estuary_3_act4_beach_loop.json
```

Writes `estuary_3_act4_beach_loop.wav` next to the JSON. Pass an
explicit output path as the second argument:

```bash
python3 godot/tools/audio/slowstick_synth.py compose \
    godot/tools/audio/compositions/estuary_3_act4_beach_loop.json \
    godot/assets/audio/estuary_3/act4_loop.wav
```

### 2. midi · .mid → WAV

Compose in any DAW that can export a Type 0 or Type 1 SMF; pipe
it through the tool. GM program changes route to nearest-fit
slowstick instruments (basses → slowstick_bass, leads →
slowstick_lead, pads → slowstick_pad, synth effects →
ambient_drone).

```bash
python3 godot/tools/audio/slowstick_synth.py midi input.mid output.wav
```

### 3. sfx · named preset → WAV

Sfxr-style parameterized presets for game sfx. Currently
authored:

- **coin** — two-tone bright rise (Mario-adjacent)
- **hurt** — descending noise burst
- **jump** — upward square-wave chirp
- **blip** — short square blip
- **pickup** — soft two-tone lift
- **door_open** — creak + thunk
- **register_ding** — cash-register bell arpeggio
- **phone_ring** — two-tone twice
- **broom_sweep** — long-scrub noise
- **cooler_whoosh** — air-seal release
- **fluorescent_start** — zap-zap-hum bulb warmup
- **tide_pool_splash** — wet-slap plus tuned tail
- **stick_scratch** — Act 4 sand-scratch (each rhythm press)

```bash
# One preset
python3 godot/tools/audio/slowstick_synth.py sfx phone_ring \
    godot/assets/audio/sfx/phone_ring.wav

# All presets, batched into a directory
python3 godot/tools/audio/slowstick_synth.py sfx all \
    godot/assets/audio/sfx/
```

## Instruments

`slowstick_synth.py list` prints the currently-authored set.
Each instrument is a small Python function that takes
`(freq, seconds, sample_rate)` and returns a float sample list.
Add a new instrument by writing that function and registering it
in `INSTRUMENTS`.

Authored:

- **slowstick_lead** — 3-osc saw+saw+sub-triangle with a 6-cent
  detune, medium ADSR, 6.5 kHz LPF. Matches the in-game
  PDPRiffmaster voice.
- **slowstick_pad** — same voice, wider detune (14 cents),
  longer attack + release, 3.2 kHz LPF. Slow chords.
- **slowstick_bass** — heavier sub-triangle (95%), tight
  attack, 1.8 kHz LPF.
- **chiptune_arp** — 50% square wave, fast attack, short
  release. NES-lead adjacent.
- **ambient_drone** — three detuned sines with a subtle
  0.13 Hz detune LFO. For long-held ambient underlays.
- **fluorescent_hum** — 59 Hz + 3rd + 5th harmonic. Kwik Stop.
- **rain** — noise → LPF whose cutoff scales with pitch.
- **soft_sine** — clean sine + ADSR. For bells and chimes.

## Composition schema

```json
{
  "meta":  {"title": "...", "composer": "..."},
  "tempo_bpm": 72,
  "time_sig":  [4, 4],
  "sample_rate": 44100,

  "tracks": [
    {
      "instrument": "slowstick_lead",
      "gain": 0.7,
      "notes": [
        {"pitch": "A4", "bar": 1, "beat": 1, "dur": 0.5, "vel": 0.8},
        {"pitch": 76,   "bar": 1, "beat": 2, "dur": 1.0}
      ]
    }
  ]
}
```

Rules:

- Bars are 1-based.
- Beats are 1-based within a bar.
- Durations are in beats.
- Pitch accepts either a MIDI number (int) or a note name
  (`"C4"`, `"F#3"`, `"Bb5"`). Middle C = C4 = 60.
- Velocity defaults to 0.8. Gain defaults to 0.7.

## Currently authored compositions

- **estuary_3_act4_beach_loop.json** — Marc Ostrom's 8-bar
  ambient loop for the Act 4 rhythm-drawing session. Sits at 72
  BPM to match `FifthSeasonBeach.gd`'s bar clock; the loop's
  downbeat lines up with the game's metronome pulse.
- **estuary_3_kwik_stop_hum.json** — the 59 Hz fluorescent buzz
  under every Kwik Stop night in Act 1. 16-bar loop with a
  barely-audible sigh at bar 15 (Marc signing his name).

## Adding a new composition

1. Copy an existing JSON file in `compositions/` as a
   starting template.
2. Author bars/beats/pitches. Godot's `AudioStreamPlayer` will
   loop the resulting WAV cleanly if the composition ends on a
   bar boundary.
3. Render: `python3 slowstick_synth.py compose <your.json>`.
4. Drop the WAV under `godot/assets/audio/` and reference it
   from an AudioStreamPlayer.

## Adding a new instrument

1. Write a function `(freq, seconds, sample_rate) → list[float]`
   in `slowstick_synth.py`.
2. Register it in the `INSTRUMENTS` dict at module scope.
3. Reference it by name in composition JSON.

## Testing

The tool's smoke tests live in `godot/tools/audio/tests/`
(deferred to a follow-up commit). For now:

```bash
python3 godot/tools/audio/slowstick_synth.py list
python3 godot/tools/audio/slowstick_synth.py sfx blip /tmp/blip.wav
```

If `list` prints and `blip.wav` plays a short square-wave chirp
in your player, the pipeline works.

## Deferred

- OGG Vorbis output. WAV works everywhere Godot works. OGG
  compression is nice-to-have; add via `subprocess` to
  `oggenc`/`ffmpeg` in a follow-up if repo size becomes a
  problem.
- Real MIDI parser with meta-track handling, sysex, controller
  events, pitch bend. The minimal built-in covers most DAW
  exports.
- Runtime AudioStreamGenerator playback of these compositions
  in Godot (i.e. no WAV file, generate on the fly). See
  PDPRiffmaster.gd for the pattern; a shared `SlowstockSynth.gd`
  autoload could grow from that.
- Effects · reverb, delay, chorus. All authored dry right now.
  A convolution reverb via a small impulse-response table is a
  natural next module.
