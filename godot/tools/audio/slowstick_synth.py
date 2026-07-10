#!/usr/bin/env python3
"""
slowstick_synth — audio tool for the Modern Mythology project.

In-fiction: the studio pipeline Marc Ostrom used at Oneironautics
Inc. to render loops for the Estuary 3 slowstick — a small
soft-synth with 3-oscillator saw+saw+sub-triangle voices matching
the in-game PDP Riffmaster's tone, an ADSR envelope, and a set of
authored instruments (lead / pad / bass / arp / drone / fluorescent
hum / rain).

Out-of-fiction: a pure-Python, stdlib-only renderer that turns
authored compositions into game-ready WAV files. No numpy, no
scipy, no external deps. Same discipline as
godot/tools/landscape_sim/estuary_one.py.

Three entry paths:

  1. compose   · JSON composition → WAV
                    slowstick_synth.py compose <in.json> [out.wav]

  2. midi      · standard .mid file → WAV
                    slowstick_synth.py midi <in.mid> [out.wav]
                 Uses mido if installed; falls back to a small
                 built-in MIDI parser (enough for single-track,
                 note-on/note-off events, program changes).

  3. sfx       · sfxr-style parameter preset → WAV
                    slowstick_synth.py sfx <preset_name> [out.wav]
                 Preset names: coin, hurt, jump, blip, pickup,
                 door_open, register_ding, phone_ring,
                 broom_sweep, cooler_whoosh, fluorescent_start,
                 tide_pool_splash, stick_scratch.

All three produce 16-bit mono 44.1kHz WAV files by default.
Stereo, 24-bit, and 48kHz can be requested via flags. See
--help.

Composition JSON schema:

    {
      "meta":  {"title": str, "composer": str, "notes": str?},
      "tempo_bpm": float,
      "time_sig":  [int, int],
      "sample_rate": int?,              // default 44100
      "loop_bars": int?,                // default = total bars in tracks
      "tracks": [
        {
          "instrument": str,            // one of INSTRUMENTS
          "gain":       float?,         // 0..1, default 0.7
          "notes": [
            {"pitch": int|str,          // MIDI number, or "C4", "F#3"
             "bar":   float,            // 1-based (bar 1 = start of track)
             "beat":  float,            // 1-based
             "dur":   float,            // in beats
             "vel":   float?}           // 0..1, default 0.8
          ]
        }
      ]
    }

Instrument names authored below in the INSTRUMENTS dict. Each is
a small parameter block; new ones are one dict away.
"""

import argparse
import json
import math
import os
import struct
import sys
from pathlib import Path


# ─── Constants ─────────────────────────────────────────────────────

SAMPLE_RATE_DEFAULT = 44100
MASTER_GAIN_DEFAULT = 0.28   # slightly hotter than the in-game
                             # PDPRiffmaster (0.18) because rendered
                             # WAVs won't sit on a mixed bus


# ─── Note utilities ────────────────────────────────────────────────

_NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3, 'E': 4,
    'F': 5, 'F#': 6, 'GB': 6, 'G': 7, 'G#': 8, 'AB': 8,
    'A': 9, 'A#': 10, 'BB': 10, 'B': 11, 'CB': 11,
}


def midi_of(pitch):
    """Accept int (already MIDI) or 'C4' / 'F#3' / 'Bb5' notation."""
    if isinstance(pitch, int):
        return pitch
    if isinstance(pitch, float):
        return int(pitch)
    s = str(pitch).strip().upper()
    # Split into note letter(s) and octave number
    i = 0
    while i < len(s) and (s[i].isalpha() or s[i] in '#B'):
        i += 1
    name = s[:i]
    octave = int(s[i:]) if i < len(s) else 4
    if name not in _NOTE_TO_SEMITONE:
        raise ValueError(f"unknown note name: {pitch}")
    return 12 * (octave + 1) + _NOTE_TO_SEMITONE[name]


def freq_of_midi(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


# ─── Oscillators ───────────────────────────────────────────────────

def osc_saw(phase):
    # phase in [0, 1); saw ramps -1 → +1 across the cycle
    return 2.0 * (phase - math.floor(phase + 0.5))


def osc_square(phase, duty=0.5):
    p = phase - math.floor(phase)
    return 1.0 if p < duty else -1.0


def osc_triangle(phase):
    p = phase - math.floor(phase)
    return 1.0 - 4.0 * abs(p - 0.5)


def osc_sine(phase):
    return math.sin(2.0 * math.pi * phase)


def osc_noise(rng_state):
    # 32-bit LCG · state passed in as [int], mutated in place
    rng_state[0] = (rng_state[0] * 1103515245 + 12345) & 0x7fffffff
    return ((rng_state[0] & 0xffff) / 32767.5) - 1.0


# ─── ADSR envelope ─────────────────────────────────────────────────

def adsr_gate(t, gate_time, atk, dec, sus, rel):
    """
    Returns the envelope value at absolute time `t`, given the gate
    is released at `gate_time`. Attack → Decay → Sustain → Release.
    All times in seconds; `sus` is the sustain LEVEL (0..1).
    """
    if t < 0:
        return 0.0
    if t < atk:
        return t / max(1e-6, atk)
    if t < atk + dec:
        return 1.0 - (1.0 - sus) * ((t - atk) / max(1e-6, dec))
    if t < gate_time:
        return sus
    r = t - gate_time
    if r < rel:
        return sus * (1.0 - r / max(1e-6, rel))
    return 0.0


# ─── Instruments ───────────────────────────────────────────────────
#
# Each instrument is a callable `(freq, seconds, sample_rate) →
# list[float]` producing a single note buffer. Instruments compose
# oscillator mixes + an ADSR shape.

def _pdp_riffmaster_voice(freq, seconds, sr,
                          atk, dec, sus, rel,
                          detune_cents=6.0,
                          sub_level=0.55,
                          filter_cutoff=None):
    """
    The PDPRiffmaster voice: saw + saw (detuned) + sub-triangle.
    Optional 1-pole lowpass filter for softer voices.
    """
    n = int(seconds * sr)
    out = [0.0] * n
    ph1 = 0.0
    ph2 = 0.0
    ph_sub = 0.0
    # Two saws detuned by ± half the cents amount
    det = detune_cents / 1200.0
    f1 = freq * (2.0 ** det)
    f2 = freq * (2.0 ** (-det))
    fsub = freq * 0.5
    dt = 1.0 / sr
    # 1-pole LPF state
    lpf_y = 0.0
    lpf_a = None
    if filter_cutoff is not None and filter_cutoff < 20000.0:
        rc = 1.0 / (2.0 * math.pi * filter_cutoff)
        lpf_a = dt / (rc + dt)
    gate_time = max(0.0, seconds - rel)
    for i in range(n):
        t = i * dt
        # oscillators
        s = 0.55 * osc_saw(ph1) + 0.55 * osc_saw(ph2) + sub_level * osc_triangle(ph_sub)
        # envelope
        e = adsr_gate(t, gate_time, atk, dec, sus, rel)
        s *= e
        # lpf
        if lpf_a is not None:
            lpf_y = lpf_y + lpf_a * (s - lpf_y)
            s = lpf_y
        out[i] = s
        ph1 += f1 * dt
        ph2 += f2 * dt
        ph_sub += fsub * dt
    return out


def instr_slowstick_lead(freq, seconds, sr):
    return _pdp_riffmaster_voice(freq, seconds, sr,
                                 atk=0.015, dec=0.120, sus=0.60, rel=0.450,
                                 detune_cents=6.0, sub_level=0.55,
                                 filter_cutoff=6500.0)


def instr_slowstick_pad(freq, seconds, sr):
    return _pdp_riffmaster_voice(freq, seconds, sr,
                                 atk=0.180, dec=0.220, sus=0.72, rel=1.200,
                                 detune_cents=14.0, sub_level=0.45,
                                 filter_cutoff=3200.0)


def instr_slowstick_bass(freq, seconds, sr):
    return _pdp_riffmaster_voice(freq, seconds, sr,
                                 atk=0.005, dec=0.090, sus=0.55, rel=0.320,
                                 detune_cents=3.0, sub_level=0.95,
                                 filter_cutoff=1800.0)


def instr_chiptune_arp(freq, seconds, sr):
    # Square-wave lead with a fast attack and short release.
    n = int(seconds * sr)
    out = [0.0] * n
    phase = 0.0
    dt = 1.0 / sr
    atk, dec, sus, rel = 0.005, 0.060, 0.40, 0.080
    gate_time = max(0.0, seconds - rel)
    for i in range(n):
        t = i * dt
        e = adsr_gate(t, gate_time, atk, dec, sus, rel)
        out[i] = osc_square(phase, duty=0.5) * 0.42 * e
        phase += freq * dt
    return out


def instr_ambient_drone(freq, seconds, sr):
    # Long-sustain pad with heavy detune, subtle LFO.
    n = int(seconds * sr)
    out = [0.0] * n
    ph1 = 0.0
    ph2 = 0.0
    ph3 = 0.0
    lfo_phase = 0.0
    dt = 1.0 / sr
    atk, dec, sus, rel = 0.900, 0.500, 0.85, 2.000
    gate_time = max(0.0, seconds - rel)
    for i in range(n):
        t = i * dt
        lfo = 1.0 + 0.008 * osc_sine(lfo_phase)   # tiny detune modulation
        f1 = freq * (2.0 ** (12.0 / 1200.0)) * lfo
        f2 = freq * lfo
        f3 = freq * (2.0 ** (-14.0 / 1200.0)) * lfo
        s = 0.45 * osc_sine(ph1) + 0.45 * osc_sine(ph2) + 0.30 * osc_sine(ph3)
        e = adsr_gate(t, gate_time, atk, dec, sus, rel)
        out[i] = s * e * 0.7
        ph1 += f1 * dt
        ph2 += f2 * dt
        ph3 += f3 * dt
        lfo_phase += 0.13 * dt   # 0.13 Hz LFO
    return out


def instr_fluorescent_hum(freq, seconds, sr):
    # The 59 Hz Kwik Stop fluorescent buzz. Ignore incoming freq
    # (per authorial intent — the hum is a fixture) but let the
    # note field pitch it slightly if the composer wants variance.
    base = 59.0 * (freq / freq_of_midi(midi_of('A2')))
    n = int(seconds * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph1 = 0.0
    ph3 = 0.0
    ph5 = 0.0
    for i in range(n):
        s = (0.55 * osc_sine(ph1)
             + 0.28 * osc_sine(ph3)
             + 0.14 * osc_sine(ph5))
        # subtle amplitude wobble to sit right in a mix
        wobble = 1.0 + 0.02 * math.sin(2.0 * math.pi * 0.35 * i * dt)
        out[i] = s * 0.16 * wobble
        ph1 += base * dt
        ph3 += (base * 3.0) * dt
        ph5 += (base * 5.0) * dt
    return out


def instr_rain(freq, seconds, sr):
    # Filtered noise, no pitch dependence. Use `freq` to shift the
    # filter cutoff — higher pitch = brighter rain.
    n = int(seconds * sr)
    out = [0.0] * n
    rng = [1103515245 ^ int(freq * 100)]
    dt = 1.0 / sr
    cutoff = max(800.0, min(6000.0, freq * 8.0))
    rc = 1.0 / (2.0 * math.pi * cutoff)
    a = dt / (rc + dt)
    y = 0.0
    for i in range(n):
        x = osc_noise(rng) * 0.7
        y = y + a * (x - y)
        out[i] = y
    return out


def instr_soft_sine(freq, seconds, sr):
    n = int(seconds * sr)
    out = [0.0] * n
    ph = 0.0
    dt = 1.0 / sr
    atk, dec, sus, rel = 0.008, 0.050, 0.80, 0.180
    gate_time = max(0.0, seconds - rel)
    for i in range(n):
        e = adsr_gate(i * dt, gate_time, atk, dec, sus, rel)
        out[i] = osc_sine(ph) * 0.45 * e
        ph += freq * dt
    return out


INSTRUMENTS = {
    'slowstick_lead':   instr_slowstick_lead,
    'slowstick_pad':    instr_slowstick_pad,
    'slowstick_bass':   instr_slowstick_bass,
    'chiptune_arp':     instr_chiptune_arp,
    'ambient_drone':    instr_ambient_drone,
    'fluorescent_hum':  instr_fluorescent_hum,
    'rain':             instr_rain,
    'soft_sine':        instr_soft_sine,
}


# ─── Composition renderer ──────────────────────────────────────────

def render_composition(comp, sample_rate=None):
    """
    comp: parsed JSON dict per the schema at the top of this file.
    Returns a mono float32-list mixdown in [-1, 1].
    """
    sr = int(sample_rate or comp.get('sample_rate', SAMPLE_RATE_DEFAULT))
    tempo = float(comp.get('tempo_bpm', 72.0))
    time_sig = comp.get('time_sig', [4, 4])
    beat_seconds = 60.0 / tempo
    bar_beats = int(time_sig[0])
    tracks = comp.get('tracks', [])

    # Determine total duration.
    total_beats = 0.0
    for t in tracks:
        for n in t.get('notes', []):
            end_beat = (float(n['bar']) - 1) * bar_beats \
                     + (float(n['beat']) - 1) \
                     + float(n['dur'])
            if end_beat > total_beats:
                total_beats = end_beat
    # Add a small tail for envelope releases.
    total_seconds = (total_beats + 1.0) * beat_seconds
    total_samples = int(total_seconds * sr) + int(0.5 * sr)
    mix = [0.0] * total_samples

    for t in tracks:
        inst_name = str(t.get('instrument', 'slowstick_lead'))
        if inst_name not in INSTRUMENTS:
            sys.stderr.write(f"[slowstick_synth] unknown instrument: "
                             f"{inst_name} — falling back to slowstick_lead\n")
            inst_name = 'slowstick_lead'
        instr = INSTRUMENTS[inst_name]
        gain = float(t.get('gain', 0.7))
        for n in t.get('notes', []):
            start_beat = (float(n['bar']) - 1) * bar_beats \
                       + (float(n['beat']) - 1)
            start_s = start_beat * beat_seconds
            dur_s = float(n['dur']) * beat_seconds
            vel = float(n.get('vel', 0.8))
            freq = freq_of_midi(midi_of(n['pitch']))
            buf = instr(freq, dur_s, sr)
            start_i = int(start_s * sr)
            for j, sample in enumerate(buf):
                idx = start_i + j
                if 0 <= idx < total_samples:
                    mix[idx] += sample * gain * vel

    # Normalize/soft-clip
    peak = max(1e-9, max(abs(s) for s in mix))
    scale = MASTER_GAIN_DEFAULT / max(MASTER_GAIN_DEFAULT, peak)
    for i in range(total_samples):
        v = mix[i] * scale
        # Soft-clip via tanh approximation
        v = math.tanh(v * 1.2)
        mix[i] = v * 0.92

    return mix, sr


# ─── SFX presets ───────────────────────────────────────────────────

def sfx_coin(sr):
    # Two-tone bright rise. Classic.
    out = []
    for pitch_midi, dur in [(76, 0.06), (83, 0.14)]:
        out.extend(instr_chiptune_arp(freq_of_midi(pitch_midi), dur, sr))
    return out


def sfx_hurt(sr):
    # Descending noise burst.
    n = int(0.18 * sr)
    out = [0.0] * n
    rng = [42]
    for i in range(n):
        env = 1.0 - i / n
        out[i] = osc_noise(rng) * 0.55 * env * env
    return out


def sfx_jump(sr):
    # Upward chirp.
    n = int(0.14 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    phase = 0.0
    for i in range(n):
        t = i * dt
        f = 220 + 600 * (t / (n * dt))
        env = math.pow(1.0 - t / (n * dt), 0.5)
        out[i] = osc_square(phase, 0.5) * 0.4 * env
        phase += f * dt
    return out


def sfx_blip(sr):
    # Short square blip.
    return instr_chiptune_arp(freq_of_midi(midi_of('E5')), 0.05, sr)


def sfx_pickup(sr):
    # Coin-adjacent, softer.
    out = []
    out.extend(instr_slowstick_lead(freq_of_midi(midi_of('G5')), 0.05, sr))
    out.extend(instr_slowstick_lead(freq_of_midi(midi_of('B5')), 0.10, sr))
    return out


def sfx_door_open(sr):
    # Wooden creak → thunk.
    n = int(0.45 * sr)
    out = [0.0] * n
    rng = [777]
    dt = 1.0 / sr
    for i in range(n):
        t = i * dt
        env = 1.0 - t / (n * dt)
        # Creak: filtered noise with slowly falling cutoff
        cutoff = 800 - 500 * (t / (n * dt))
        rc = 1.0 / (2.0 * math.pi * max(100.0, cutoff))
        a = dt / (rc + dt)
        y = osc_noise(rng) * 0.35 * env * env
        # A slight low-tone thunk near the end
        if t > 0.28:
            thunk_env = (t - 0.28) / (n * dt - 0.28)
            y += osc_sine((80.0) * t) * 0.3 * (1.0 - thunk_env)
        out[i] = y
    return out


def sfx_register_ding(sr):
    # Cash-register bell.
    out = []
    for pitch, dur, vel in [('D6', 0.10, 0.7), ('F#6', 0.08, 0.5), ('A6', 0.18, 0.6)]:
        out.extend(instr_soft_sine(freq_of_midi(midi_of(pitch)), dur, sr))
    return out


def sfx_phone_ring(sr):
    # Two-note ring, twice.
    seg = []
    for _ in range(2):
        seg.extend(instr_slowstick_lead(freq_of_midi(midi_of('B4')), 0.16, sr))
        seg.extend(instr_slowstick_lead(freq_of_midi(midi_of('E5')), 0.16, sr))
    # Silence tail
    seg.extend([0.0] * int(0.28 * sr))
    return seg


def sfx_broom_sweep(sr):
    # Long-scrub noise.
    n = int(0.55 * sr)
    out = [0.0] * n
    rng = [1234]
    dt = 1.0 / sr
    cutoff = 2200.0
    rc = 1.0 / (2.0 * math.pi * cutoff)
    a = dt / (rc + dt)
    y = 0.0
    for i in range(n):
        t = i * dt
        env = math.sin(math.pi * (t / (n * dt))) ** 0.6
        x = osc_noise(rng)
        y = y + a * (x - y)
        out[i] = y * 0.5 * env
    return out


def sfx_cooler_whoosh(sr):
    # Cooler-door air-seal release: low-cut noise burst.
    n = int(0.60 * sr)
    out = [0.0] * n
    rng = [999]
    dt = 1.0 / sr
    y_lp = 0.0
    y_hp = 0.0
    a_lp = dt / (1.0 / (2.0 * math.pi * 3200.0) + dt)
    a_hp = dt / (1.0 / (2.0 * math.pi * 220.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.pow(1.0 - t / (n * dt), 1.5)
        x = osc_noise(rng)
        y_lp = y_lp + a_lp * (x - y_lp)
        y_hp = y_lp - (y_lp - y_hp) * (1.0 - a_hp)
        out[i] = (y_lp - y_hp) * 0.7 * env
    return out


def sfx_fluorescent_start(sr):
    # The zap-zap-hum of a fluorescent bulb starting up.
    n = int(0.9 * sr)
    out = [0.0] * n
    rng = [55]
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        t = i * dt
        # Random zap bursts in the first 0.4s
        zap = 0.0
        if t < 0.4 and (i % max(1, int(sr * 0.02)) == 0):
            zap = 0.7 * (osc_noise(rng) * 0.5 + 0.5)
        # Hum ramps in after 0.35s
        hum_env = 0.0
        if t > 0.35:
            hum_env = min(1.0, (t - 0.35) / 0.35)
        hum = 0.28 * (osc_sine(ph) * 0.55 + osc_sine(ph * 3) * 0.28 + osc_sine(ph * 5) * 0.14)
        out[i] = zap * 0.25 + hum * hum_env
        ph += 59.0 * dt
    return out


def sfx_tide_pool_splash(sr):
    # A wet-slap plus a small resonant tail.
    n = int(0.35 * sr)
    out = [0.0] * n
    rng = [3141]
    dt = 1.0 / sr
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 8.0)
        splash = osc_noise(rng) * env * 0.6
        # Small tuned tail
        tail = osc_sine(120.0 * t) * math.exp(-t * 6.0) * 0.25
        out[i] = splash + tail
    return out


def sfx_stick_scratch(sr):
    # Wet-sand scratch: short filtered-noise burst with grain.
    n = int(0.18 * sr)
    out = [0.0] * n
    rng = [4242]
    dt = 1.0 / sr
    cutoff = 1600.0
    rc = 1.0 / (2.0 * math.pi * cutoff)
    a = dt / (rc + dt)
    y = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 12.0)
        x = osc_noise(rng)
        y = y + a * (x - y)
        out[i] = y * 0.55 * env
    return out


# ─── Wave A · UI SFX (added in the audit-follow-through commit) ────

def sfx_verb_select(sr):
    # SCUMM verb button click. Short soft chirp.
    return instr_chiptune_arp(freq_of_midi(midi_of('C6')), 0.035, sr)


def sfx_turn_tick(sr):
    # 40s Act 1 turn advance. A low woody click.
    n = int(0.05 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 60.0)
        out[i] = (0.5 * osc_triangle(ph) + 0.25 * osc_sine(ph * 2)) * env * 0.42
        ph += 90.0 * dt
    return out


def sfx_customer_bell(sr):
    # Store door bell when a customer arrives. Soft two-tone ding.
    return _concat(
        instr_soft_sine(freq_of_midi(midi_of('B5')), 0.06, sr),
        instr_soft_sine(freq_of_midi(midi_of('D6')), 0.12, sr),
    )


def sfx_control_click(sr):
    # Act 2 button click. Soft chirp.
    return instr_chiptune_arp(freq_of_midi(midi_of('G5')), 0.03, sr)


def sfx_season_settle(sr):
    # Act 2 SETTLE THE SEASON. Resolving three-note chord ascending.
    a = instr_soft_sine(freq_of_midi(midi_of('D4')), 0.28, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('F#4')), 0.28, sr)
    c = instr_soft_sine(freq_of_midi(midi_of('A4')), 0.28, sr)
    # Mix them in parallel (same start time).
    n = max(len(a), len(b), len(c))
    out = [0.0] * n
    for i in range(len(a)): out[i] += a[i] * 0.55
    for i in range(len(b)): out[i] += b[i] * 0.55
    for i in range(len(c)): out[i] += c[i] * 0.55
    return out


def sfx_tile_hover(sr):
    # Very quiet Act 3 tile hover. Short blip.
    n = int(0.025 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        env = 1.0 - i / n
        out[i] = osc_sine(ph) * 0.18 * env
        ph += 1400.0 * dt
    return out


def sfx_tile_enter(sr):
    # Act 3 location tile click. Two-tone rise.
    return _concat(
        instr_soft_sine(freq_of_midi(midi_of('E5')), 0.06, sr),
        instr_soft_sine(freq_of_midi(midi_of('A5')), 0.10, sr),
    )


def sfx_press_hit(sr):
    # Act 4 on-beat press. Warm click with a small tuned tail.
    n = int(0.08 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 30.0)
        click = (osc_sine(ph) * 0.55 + osc_triangle(ph * 2) * 0.30) * env
        out[i] = click * 0.42
        ph += 220.0 * dt
    return out


def sfx_press_miss(sr):
    # Act 4 out-of-window press. Small negative tick — muffled.
    n = int(0.05 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    rng = [8888]
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 800.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 45.0)
        x = osc_noise(rng) * 0.35 * env
        y = y + a * (x - y)
        out[i] = y * 0.5
    return out


def sfx_cartridge_hover(sr):
    # Shelf hover. Barely audible chirp.
    n = int(0.02 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        env = 1.0 - i / n
        out[i] = osc_sine(ph) * 0.14 * env
        ph += 2200.0 * dt
    return out


def sfx_cartridge_click(sr):
    # Shelf click on an unlocked cartridge. Two-tone crisp.
    return _concat(
        instr_chiptune_arp(freq_of_midi(midi_of('A5')), 0.04, sr),
        instr_chiptune_arp(freq_of_midi(midi_of('E6')), 0.06, sr),
    )


def sfx_boot(sr):
    # BOOT button. Cartridge-being-inserted click plus a small
    # power-on hum tail.
    n1 = int(0.06 * sr)
    click = [0.0] * n1
    dt = 1.0 / sr
    rng = [12345]
    for i in range(n1):
        t = i * dt
        env = math.exp(-t * 55.0)
        click[i] = (osc_noise(rng) * 0.55 + osc_square(t * 180.0, 0.4) * 0.3) * env * 0.45
    hum = instr_ambient_drone(freq_of_midi(midi_of('A3')), 0.35, sr)
    # Fade the hum in over its first 30ms so it's not slammed in.
    for i in range(min(int(0.03 * sr), len(hum))):
        hum[i] *= i / max(1, int(0.03 * sr))
    return _concat(click, hum)


def _concat(*arrs):
    out = []
    for a in arrs:
        out.extend(a)
    return out


# ─── Wave C · Community Planned demon-depth SFX ────────────────────

def sfx_tier_crossing_hungry(sr):
    # Warmth going wrong · a soft slowstick_pad chord bent slightly
    # sharp on the top voice.  ~700 ms.
    a = instr_slowstick_pad(freq_of_midi(midi_of('A3')), 0.60, sr)
    b = instr_slowstick_pad(freq_of_midi(midi_of('D4')), 0.60, sr)
    # A slight upward chirp overlay to bias the sense of "off"
    n = len(a)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 3.0)
        out[i] = (a[i] * 0.55 + b[i] * 0.55) + osc_sine(ph) * 0.10 * env
        f = 440.0 + 25.0 * t
        ph += f * dt
    return out


def sfx_tier_crossing_restless(sr):
    # Agitated · a bent minor-third rise with a small tremolo.
    a = instr_slowstick_lead(freq_of_midi(midi_of('D4')), 0.35, sr)
    b = instr_slowstick_lead(freq_of_midi(midi_of('F4')), 0.35, sr)
    # Slight tremolo amplitude wobble.
    n = len(a)
    out = [0.0] * n
    dt = 1.0 / sr
    for i in range(n):
        trem = 1.0 + 0.12 * math.sin(2.0 * math.pi * 7.0 * i * dt)
        out[i] = (a[i] * 0.5 + b[i] * 0.5) * trem
    return out


def sfx_tier_crossing_close(sr):
    # Alarming · a dissonant open-fifth-minus-a-half-step chord that
    # dies away over 1.2 s. This is the "one more dispatch" beat.
    a = instr_slowstick_pad(freq_of_midi(midi_of('C4')),   1.10, sr)
    b = instr_slowstick_pad(freq_of_midi(midi_of('F#4')),  1.10, sr)
    c = instr_slowstick_bass(freq_of_midi(midi_of('C3')),  1.10, sr)
    n = max(len(a), len(b), len(c))
    out = [0.0] * n
    for i in range(len(a)): out[i] += a[i] * 0.45
    for i in range(len(b)): out[i] += b[i] * 0.40
    for i in range(len(c)): out[i] += c[i] * 0.55
    return out


def sfx_tier_crossing_turned(sr):
    # The most dramatic of the four · a bright chime that snaps into
    # a low bent tone. The moment a demon actually turns.
    bell = instr_soft_sine(freq_of_midi(midi_of('E6')), 0.28, sr)
    snap_n = int(0.06 * sr)
    snap = [0.0] * snap_n
    rng = [64738]
    dt = 1.0 / sr
    for i in range(snap_n):
        env = math.exp(-i / snap_n * 12.0)
        snap[i] = osc_noise(rng) * 0.55 * env
    tail = instr_slowstick_bass(freq_of_midi(midi_of('E2')), 1.00, sr)
    return _concat(bell, snap, tail)


def sfx_basement_rite(sr):
    # Soft warm resolve · plagal cadence over the basement's warmth.
    a = instr_slowstick_pad(freq_of_midi(midi_of('F3')), 0.50, sr)
    b = instr_slowstick_pad(freq_of_midi(midi_of('A3')), 0.50, sr)
    c = instr_slowstick_pad(freq_of_midi(midi_of('C4')), 0.50, sr)
    n = max(len(a), len(b), len(c))
    part1 = [0.0] * n
    for i in range(len(a)): part1[i] += a[i] * 0.5
    for i in range(len(b)): part1[i] += b[i] * 0.5
    for i in range(len(c)): part1[i] += c[i] * 0.5
    d = instr_slowstick_pad(freq_of_midi(midi_of('E3')), 0.60, sr)
    e = instr_slowstick_pad(freq_of_midi(midi_of('G3')), 0.60, sr)
    f2 = instr_slowstick_pad(freq_of_midi(midi_of('C4')), 0.60, sr)
    n2 = max(len(d), len(e), len(f2))
    part2 = [0.0] * n2
    for i in range(len(d)): part2[i] += d[i] * 0.55
    for i in range(len(e)): part2[i] += e[i] * 0.55
    for i in range(len(f2)): part2[i] += f2[i] * 0.55
    return _concat(part1, part2)


def sfx_pair_warm(sr):
    # Two soft notes together · low+high partial, resolving.
    a = instr_soft_sine(freq_of_midi(midi_of('G4')), 0.20, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('C5')), 0.28, sr)
    n = max(len(a), len(b))
    out = [0.0] * n
    for i in range(len(a)): out[i] += a[i] * 0.55
    for i in range(len(b)): out[i] += b[i] * 0.55
    return out


def sfx_pair_loud(sr):
    # A small bright clash · two chirps a semitone apart hit together.
    a = instr_chiptune_arp(freq_of_midi(midi_of('G5')), 0.10, sr)
    b = instr_chiptune_arp(freq_of_midi(midi_of('G#5')), 0.10, sr)
    n = max(len(a), len(b))
    out = [0.0] * n
    for i in range(len(a)): out[i] += a[i] * 0.55
    for i in range(len(b)): out[i] += b[i] * 0.55
    return out


def sfx_pair_cold(sr):
    # A distant single tone, high and pure, brief · no resolution.
    return instr_soft_sine(freq_of_midi(midi_of('D6')), 0.16, sr)


def sfx_marker_set(sr):
    # A soft click + a very short hum tail. Two-part; sub-tri click.
    n1 = int(0.03 * sr)
    click = [0.0] * n1
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n1):
        t = i * dt
        env = math.exp(-t * 55.0)
        click[i] = osc_triangle(ph) * 0.45 * env
        ph += 320.0 * dt
    hum = instr_slowstick_pad(freq_of_midi(midi_of('A3')), 0.18, sr)
    return _concat(click, hum)


def sfx_marker_expire(sr):
    # A softer version of marker_set · lower pitch, longer decay.
    return instr_soft_sine(freq_of_midi(midi_of('E3')), 0.30, sr)


def sfx_quiet_week(sr):
    # A light warm two-tone rise. The human-recovery beat.
    return _concat(
        instr_soft_sine(freq_of_midi(midi_of('E5')), 0.14, sr),
        instr_soft_sine(freq_of_midi(midi_of('G5')), 0.18, sr),
    )


def sfx_roster_loud(sr):
    # A low grumbling chord · slowstick_bass with detuned overlays.
    a = instr_slowstick_bass(freq_of_midi(midi_of('E2')), 0.90, sr)
    b = instr_slowstick_bass(freq_of_midi(midi_of('F2')), 0.90, sr)
    c = instr_slowstick_pad(freq_of_midi(midi_of('C3')),  0.90, sr)
    n = max(len(a), len(b), len(c))
    out = [0.0] * n
    for i in range(len(a)): out[i] += a[i] * 0.55
    for i in range(len(b)): out[i] += b[i] * 0.45
    for i in range(len(c)): out[i] += c[i] * 0.40
    return out


def sfx_interlude_earned(sr):
    # A page-turn-like brush + a small bell. Two-part.
    rng = [4711]
    n1 = int(0.12 * sr)
    brush = [0.0] * n1
    dt = 1.0 / sr
    y = 0.0
    cutoff = 3500.0
    rc = 1.0 / (2.0 * math.pi * cutoff)
    a = dt / (rc + dt)
    for i in range(n1):
        t = i * dt
        env = math.sin(math.pi * (t / (n1 * dt))) ** 0.4
        x = osc_noise(rng) * 0.35 * env
        y = y + a * (x - y)
        brush[i] = y
    bell = instr_soft_sine(freq_of_midi(midi_of('C6')), 0.30, sr)
    return _concat(brush, bell)


def sfx_labor_day_arrival(sr):
    # A three-note arrival chime · softly ascending. The end-of-summer
    # marker.
    return _concat(
        instr_soft_sine(freq_of_midi(midi_of('C5')), 0.20, sr),
        instr_soft_sine(freq_of_midi(midi_of('E5')), 0.22, sr),
        instr_soft_sine(freq_of_midi(midi_of('G5')), 0.35, sr),
    )


# ─── Wave D · Gauntlet SFX ─────────────────────────────────────────

def sfx_card_flip(sr):
    # A brief upward brush · dry, no tail. 90ms.
    n = int(0.09 * sr)
    out = [0.0] * n
    rng = [8181]
    dt = 1.0 / sr
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 5200.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.pow(1.0 - t / (n * dt), 0.6)
        x = osc_noise(rng) * 0.55 * env
        y = y + a * (x - y)
        out[i] = y
    return out


def sfx_card_place(sr):
    # Softer thunk than door_open · card meeting felt · sub-tri body
    # plus a brief noise pop.
    n = int(0.10 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    rng = [9911]
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 28.0)
        thunk = osc_triangle(ph) * 0.45 * env
        pop = osc_noise(rng) * 0.18 * math.exp(-t * 80.0)
        out[i] = thunk + pop
        ph += 140.0 * dt
    return out


def sfx_hand_deal(sr):
    # Three card-flips staggered. Ends dry.
    a = sfx_card_flip(sr)
    b = sfx_card_flip(sr)
    c = sfx_card_flip(sr)
    # Small gaps of ~30ms between each.
    gap = int(0.03 * sr)
    silence = [0.0] * gap
    return _concat(a, silence, b, silence, c)


def sfx_threshold_cross(sr):
    # Named-threshold crossing beat · a bent-down single tone with a
    # brief bell overlay. Something is about to be true.
    n = int(0.60 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 3.0)
        # Slight downward glide from A4 to G4 over 400ms
        f = 440.0 - (440.0 - 392.0) * min(1.0, t / 0.4)
        out[i] = osc_sine(ph) * 0.42 * env
        ph += f * dt
    bell = instr_soft_sine(freq_of_midi(midi_of('E5')), 0.20, sr)
    for i in range(min(len(out), len(bell))):
        out[i] += bell[i] * 0.28
    return out


def sfx_visitor_arrive(sr):
    # A named visitor enters the locale · two-note lift plus a soft
    # slowstick_pad underlay. The room announces them.
    a = instr_soft_sine(freq_of_midi(midi_of('D5')), 0.16, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('A5')), 0.22, sr)
    pad = instr_slowstick_pad(freq_of_midi(midi_of('D3')), 0.45, sr)
    intro = _concat(a, b)
    n = max(len(intro), len(pad))
    out = [0.0] * n
    for i in range(len(intro)): out[i] += intro[i] * 0.55
    for i in range(len(pad)):   out[i] += pad[i] * 0.35
    return out


def sfx_lore_token_reveal(sr):
    # Book-being-opened rustle + a warm bell. The scrapbook writes.
    rustle_n = int(0.14 * sr)
    rustle = [0.0] * rustle_n
    rng = [2727]
    dt = 1.0 / sr
    y = 0.0
    a_lp = dt / (1.0 / (2.0 * math.pi * 4000.0) + dt)
    for i in range(rustle_n):
        t = i * dt
        env = math.sin(math.pi * (t / (rustle_n * dt))) ** 0.4
        x = osc_noise(rng) * 0.32 * env
        y = y + a_lp * (x - y)
        rustle[i] = y
    bell = instr_soft_sine(freq_of_midi(midi_of('G5')), 0.34, sr)
    return _concat(rustle, bell)


def sfx_scrapbook_open(sr):
    # Longer rustle · leather-bound cover · settles into a two-note
    # chord.
    rustle_n = int(0.30 * sr)
    rustle = [0.0] * rustle_n
    rng = [3131]
    dt = 1.0 / sr
    y = 0.0
    a_lp = dt / (1.0 / (2.0 * math.pi * 2800.0) + dt)
    for i in range(rustle_n):
        t = i * dt
        env = math.sin(math.pi * (t / (rustle_n * dt))) ** 0.5
        x = osc_noise(rng) * 0.4 * env
        y = y + a_lp * (x - y)
        rustle[i] = y
    a = instr_soft_sine(freq_of_midi(midi_of('E4')), 0.42, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('B4')), 0.42, sr)
    n = max(len(a), len(b))
    chord = [0.0] * n
    for i in range(len(a)): chord[i] += a[i] * 0.5
    for i in range(len(b)): chord[i] += b[i] * 0.5
    return _concat(rustle, chord)


def sfx_scenario_unlock(sr):
    # CP → Gauntlet crossover fires · a rising four-note arpeggio.
    # Warmer than labor_day_arrival · signals a specific card unlocked.
    return _concat(
        instr_chiptune_arp(freq_of_midi(midi_of('C5')), 0.09, sr),
        instr_chiptune_arp(freq_of_midi(midi_of('E5')), 0.09, sr),
        instr_chiptune_arp(freq_of_midi(midi_of('G5')), 0.09, sr),
        instr_slowstick_lead(freq_of_midi(midi_of('C6')), 0.28, sr),
    )


def sfx_scenario_picker(sr):
    # Ctrl+F8 overlay open · a small rising two-tone flourish.
    return _concat(
        instr_chiptune_arp(freq_of_midi(midi_of('F5')), 0.06, sr),
        instr_chiptune_arp(freq_of_midi(midi_of('A5')), 0.10, sr),
    )


def sfx_win_chord(sr):
    # Scenario win · a resolving major chord with a soft-sine top.
    a = instr_slowstick_pad(freq_of_midi(midi_of('C4')), 0.85, sr)
    b = instr_slowstick_pad(freq_of_midi(midi_of('E4')), 0.85, sr)
    c = instr_slowstick_pad(freq_of_midi(midi_of('G4')), 0.85, sr)
    top = instr_soft_sine(freq_of_midi(midi_of('C5')), 0.85, sr)
    n = max(len(a), len(b), len(c), len(top))
    out = [0.0] * n
    for i in range(len(a)):   out[i] += a[i] * 0.4
    for i in range(len(b)):   out[i] += b[i] * 0.4
    for i in range(len(c)):   out[i] += c[i] * 0.4
    for i in range(len(top)): out[i] += top[i] * 0.35
    return out


def sfx_loss_thud(sr):
    # Named-loss condition · a low bent-down bass with a soft noise
    # tail. Not a fail-buzzer · a specific weight landing.
    n = int(0.55 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    rng = [5959]
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 4.5)
        # A2 down to E2 across 300ms
        f = 110.0 - (110.0 - 82.4) * min(1.0, t / 0.3)
        body = (osc_triangle(ph) * 0.55 + osc_sine(ph * 0.5) * 0.25) * env
        noise = osc_noise(rng) * 0.10 * math.exp(-t * 8.0)
        out[i] = body + noise
        ph += f * dt
    return out


# ─── Wave D · Shared UI SFX ────────────────────────────────────────

def sfx_menu_open(sr):
    # Modal opens · two-tone rise. Quicker than menu_close's fall.
    return _concat(
        instr_chiptune_arp(freq_of_midi(midi_of('E5')), 0.05, sr),
        instr_chiptune_arp(freq_of_midi(midi_of('G5')), 0.08, sr),
    )


def sfx_menu_close(sr):
    # Modal closes · two-tone fall.
    return _concat(
        instr_chiptune_arp(freq_of_midi(midi_of('G5')), 0.05, sr),
        instr_chiptune_arp(freq_of_midi(midi_of('E5')), 0.08, sr),
    )


def sfx_button_hover(sr):
    # Universal hover · very short, quiet.
    n = int(0.018 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        env = 1.0 - i / n
        out[i] = osc_sine(ph) * 0.12 * env
        ph += 2000.0 * dt
    return out


def sfx_button_click(sr):
    # Universal click · slightly deeper + louder than hover.
    n = int(0.03 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 45.0)
        out[i] = (osc_sine(ph) * 0.5 + osc_triangle(ph * 2) * 0.25) * env * 0.42
        ph += 1200.0 * dt
    return out


def sfx_save_confirm(sr):
    # Save-slot save confirm · rising two-note plus a small held tail.
    a = instr_soft_sine(freq_of_midi(midi_of('G5')), 0.10, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('C6')), 0.24, sr)
    return _concat(a, b)


def sfx_load_start(sr):
    # Save-slot load start · descending pair · anticipation.
    a = instr_soft_sine(freq_of_midi(midi_of('C6')), 0.08, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('G5')), 0.14, sr)
    return _concat(a, b)


def sfx_notification(sr):
    # Non-critical notification · light two-tone lift · sits below
    # save_confirm's brightness.
    a = instr_soft_sine(freq_of_midi(midi_of('D5')), 0.08, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('A5')), 0.12, sr)
    n = max(len(a), len(b))
    out = [0.0] * n
    for i in range(len(a)): out[i] += a[i] * 0.5
    for i in range(len(b)): out[i] += b[i] * 0.5
    return out


# ─── Wave E · deferred beats ───────────────────────────────────────
#
# The eight authored-but-not-yet-wired-up audio slots from the audit.
# Radio program beds (long ambient), the night-12 "sam." formant
# beat, the backroom transition, and Act 4's last two creature
# arrivals.


def _formant_voice(seconds, sr, formants):
    """
    Very small formant synthesizer · a source pulse-train shaped
    by three resonant bandpass filters (crude two-pole IIRs). Takes
    a list of (t_frac, [f1, f2, f3], amp) breakpoints. Interpolates
    linearly between breakpoints.  Enough to make a syllable-shape
    that the ear reads as 'the player just heard a word'.

    Not intended to be intelligible.  The night-12 'sam.' beat
    lands because the game is asking it to.
    """
    n = int(seconds * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    src_ph = 0.0
    src_freq = 110.0    # source pitch (male-adjacent)
    # 3 bandpass filter states (2-pole IIR)
    y1 = [0.0, 0.0]; y2 = [0.0, 0.0]; y3 = [0.0, 0.0]

    def _bandpass_step(state, x, f, q):
        # Cheap second-order bandpass; f in Hz, q ≈ 8-20 for vowel.
        w = 2.0 * math.pi * f / sr
        r = math.exp(-w / max(1.0, q))
        y = (1.0 - r) * x + 2.0 * r * math.cos(w) * state[0] - r * r * state[1]
        state[1] = state[0]
        state[0] = y
        return y

    for i in range(n):
        t_frac = i / max(1, n - 1)
        # Interpolate formants
        f1_v, f2_v, f3_v = 700.0, 1200.0, 2500.0
        amp = 0.6
        for j in range(len(formants) - 1):
            t0 = formants[j][0]
            t1 = formants[j + 1][0]
            if t_frac <= t1:
                a_pt = (t_frac - t0) / max(1e-6, t1 - t0)
                f_a = formants[j][1]
                f_b = formants[j + 1][1]
                f1_v = f_a[0] + a_pt * (f_b[0] - f_a[0])
                f2_v = f_a[1] + a_pt * (f_b[1] - f_a[1])
                f3_v = f_a[2] + a_pt * (f_b[2] - f_a[2])
                amp = formants[j][2] + a_pt * (formants[j + 1][2] - formants[j][2])
                break
        # Source pulse-train (glottal).
        src_ph += src_freq * dt
        p = src_ph - math.floor(src_ph)
        src = 1.0 if p < 0.06 else -0.05        # thin pulse
        v1 = _bandpass_step(y1, src, f1_v, 10.0)
        v2 = _bandpass_step(y2, src, f2_v, 12.0)
        v3 = _bandpass_step(y3, src, f3_v, 14.0)
        out[i] = (v1 * 0.55 + v2 * 0.35 + v3 * 0.20) * amp
    return out


def sfx_radio_889_bed(sr):
    # NPR voice-under bed loop · 8 seconds. Simulated speech-cadence
    # without intelligible words: filtered noise pulses with a
    # 3-4 Hz speech-syllabic envelope + a subtle background hiss.
    seconds = 8.0
    n = int(seconds * sr)
    out = [0.0] * n
    rng_pulse = [7788]
    rng_hiss = [1122]
    dt = 1.0 / sr
    # LPF state for speech-shaped noise (male vocal band cut off
    # around 3.4 kHz)
    y_lp = 0.0
    a_lp = dt / (1.0 / (2.0 * math.pi * 2800.0) + dt)
    # HPF via subtraction — cut below 200 Hz
    y_hp = 0.0
    a_hp = dt / (1.0 / (2.0 * math.pi * 200.0) + dt)
    for i in range(n):
        t = i * dt
        # Syllabic envelope · ~3.4 Hz base with some jitter
        syl = 0.5 + 0.5 * math.sin(2.0 * math.pi * 3.4 * t)
        syl = math.pow(max(0.0, syl), 1.8)
        # Slight lull every 4-6s (space between sentences)
        pause = 1.0
        if 3.5 < t < 3.9: pause = 0.15
        if 6.6 < t < 6.9: pause = 0.20
        speech_src = osc_noise(rng_pulse) * 0.55 * syl * pause
        y_lp = y_lp + a_lp * (speech_src - y_lp)
        # Subtle floor hiss
        hiss = osc_noise(rng_hiss) * 0.05
        # HPF (subtract the very-low bass off the lp)
        y_hp = y_lp - (y_lp - y_hp) * (1.0 - a_hp)
        out[i] = (y_lp - y_hp) * 0.5 + hiss * 0.4
    return out


def sfx_radio_1150_bed(sr):
    # 1150 AM fishing-report loop · 6 seconds. AM-band feel: narrower
    # frequency, more compression, less high-end than 889 NPR.  A
    # slower syllabic rhythm (a fishing report speaker reads slower
    # than a morning-edition anchor).
    seconds = 6.0
    n = int(seconds * sr)
    out = [0.0] * n
    rng_pulse = [3344]
    rng_hiss = [5566]
    dt = 1.0 / sr
    y_lp = 0.0
    a_lp = dt / (1.0 / (2.0 * math.pi * 2200.0) + dt)   # narrower band
    y_hp = 0.0
    a_hp = dt / (1.0 / (2.0 * math.pi * 400.0) + dt)     # cut lows
    for i in range(n):
        t = i * dt
        syl = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.4 * t)
        syl = math.pow(max(0.0, syl), 2.2)
        # AM-radio compression · pretty flat
        speech_src = osc_noise(rng_pulse) * 0.55 * syl
        y_lp = y_lp + a_lp * (speech_src - y_lp)
        # Regular ~0.5s pause between "phrases" of the fishing report
        report_gate = 1.0
        phase = t - math.floor(t)
        if phase > 0.85: report_gate = 0.25
        y_hp = y_lp - (y_lp - y_hp) * (1.0 - a_hp)
        hiss = osc_noise(rng_hiss) * 0.06
        out[i] = ((y_lp - y_hp) * 0.55 + hiss * 0.5) * report_gate
    return out


def sfx_radio_1600_static_voice_night_5(sr):
    # Mostly static · a brief formant bloom at ~3s.  Word half-
    # heard.  Player is not certain they heard anything.
    seconds = 6.0
    n = int(seconds * sr)
    out = [0.0] * n
    rng = [1600]
    dt = 1.0 / sr
    # Six-second buffer of static
    for i in range(n):
        out[i] = osc_noise(rng) * 0.32
    # At around t=3.1s inject a ~0.6s formant syllable heavily
    # veiled by continuing static.
    voice = _formant_voice(0.6, sr, [
        (0.0,  [500.0, 1500.0, 2500.0], 0.0),
        (0.15, [550.0, 1400.0, 2500.0], 0.55),
        (0.55, [520.0, 1350.0, 2500.0], 0.55),
        (1.0,  [500.0, 1500.0, 2500.0], 0.0),
    ])
    offset = int(3.1 * sr)
    for i, v in enumerate(voice):
        if offset + i < n:
            # Half-buried under static.
            out[offset + i] = out[offset + i] * 0.55 + v * 0.35
    return out


def sfx_radio_1600_static_voice_night_12_sam(sr):
    # The game's most authored radio beat.  Static, then at 3.14s
    # a clear formant sequence approximating 'sam.' (three
    # segments: /s/ fricative, /æ/ vowel formants, /m/ nasal
    # closure), then static resumes.
    seconds = 6.0
    n = int(seconds * sr)
    out = [0.0] * n
    rng = [1612]
    for i in range(n):
        out[i] = osc_noise(rng) * 0.28
    # /s/ fricative burst · high-frequency filtered noise
    fric_dur = 0.20
    fric_n = int(fric_dur * sr)
    fric = [0.0] * fric_n
    rng_f = [777]
    dt = 1.0 / sr
    y_hp = 0.0
    a_hp = dt / (1.0 / (2.0 * math.pi * 5200.0) + dt)   # let highs through
    for i in range(fric_n):
        t = i * dt
        env = math.sin(math.pi * (t / fric_dur)) ** 0.5
        x = osc_noise(rng_f) * 0.6 * env
        y_hp = y_hp + a_hp * (x - y_hp)
        # HPF: subtract low-band to isolate high sibilance
        fric[i] = (x - y_hp) * 0.55
    # /æ/ vowel · low F1 (~660), high F2 (~1720), mid F3 (~2410)
    vowel_dur = 0.32
    vowel = _formant_voice(vowel_dur, sr, [
        (0.0,  [660.0, 1720.0, 2410.0], 0.0),
        (0.12, [700.0, 1780.0, 2450.0], 0.7),
        (0.60, [700.0, 1780.0, 2450.0], 0.7),
        (0.95, [640.0, 1680.0, 2400.0], 0.35),
        (1.0,  [640.0, 1680.0, 2400.0], 0.0),
    ])
    # /m/ nasal closure · low F1 (~250), narrow F2 (~1250)
    nasal_dur = 0.24
    nasal = _formant_voice(nasal_dur, sr, [
        (0.0,  [250.0, 1250.0, 2500.0], 0.0),
        (0.12, [280.0, 1300.0, 2500.0], 0.55),
        (0.75, [260.0, 1240.0, 2500.0], 0.45),
        (1.0,  [250.0, 1250.0, 2500.0], 0.0),
    ])
    # Splice at 3.14s.
    offset = int(3.14 * sr)
    pos = offset
    for i, v in enumerate(fric):
        if pos + i < n: out[pos + i] = out[pos + i] * 0.35 + v * 0.55
    pos += fric_n
    for i, v in enumerate(vowel):
        if pos + i < n: out[pos + i] = out[pos + i] * 0.30 + v * 0.75
    pos += int(vowel_dur * sr)
    for i, v in enumerate(nasal):
        if pos + i < n: out[pos + i] = out[pos + i] * 0.35 + v * 0.60
    return out


def sfx_2am_customer_stands_up(sr):
    # Chair scrape (mid-freq filtered noise, ~250ms) + three
    # measured footsteps (low thumps, 400ms apart).
    scrape_n = int(0.28 * sr)
    scrape = [0.0] * scrape_n
    rng = [2211]
    dt = 1.0 / sr
    y_lp = 0.0
    a_lp = dt / (1.0 / (2.0 * math.pi * 1400.0) + dt)
    for i in range(scrape_n):
        t = i * dt
        env = math.pow(1.0 - t / (scrape_n * dt), 0.7)
        x = osc_noise(rng) * 0.5 * env
        y_lp = y_lp + a_lp * (x - y_lp)
        scrape[i] = y_lp * 0.55
    # Silence gap.
    gap = [0.0] * int(0.18 * sr)
    # A single measured footstep · low sine thump.
    def _step():
        m = int(0.10 * sr)
        buf = [0.0] * m
        dt2 = 1.0 / sr
        ph = 0.0
        for i in range(m):
            t = i * dt2
            env = math.exp(-t * 38.0)
            buf[i] = (osc_sine(ph) * 0.55 + osc_triangle(ph * 2) * 0.20) * env * 0.42
            ph += 90.0 * dt2
        return buf
    step_a = _step()
    step_b = _step()
    step_c = _step()
    step_gap = [0.0] * int(0.30 * sr)
    return _concat(scrape, gap, step_a, step_gap, step_b, step_gap, step_c)


def sfx_creature_arrival_2am_customer(sr):
    # Wind on the dune ridge · 1.5s.  Filtered noise with a slow
    # amplitude modulation (2 Hz breath rhythm), quiet.
    seconds = 1.5
    n = int(seconds * sr)
    out = [0.0] * n
    rng = [3388]
    dt = 1.0 / sr
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 1600.0) + dt)
    for i in range(n):
        t = i * dt
        mod = 0.55 + 0.45 * math.sin(2.0 * math.pi * 2.0 * t + 1.2)
        x = osc_noise(rng) * 0.55
        y = y + a * (x - y)
        # Overall envelope: fade in over 200ms, hold, fade out over 400ms
        env = 1.0
        if t < 0.20:
            env = t / 0.20
        elif t > seconds - 0.40:
            env = max(0.0, (seconds - t) / 0.40)
        out[i] = y * mod * env * 0.55
    return out


# ─── Wave F · closing the remaining new rows ───────────────────────

def sfx_radio_static(sr):
    # 200ms burst of pink-ish noise for tuning between stations.
    n = int(0.20 * sr)
    out = [0.0] * n
    rng = [1616]
    dt = 1.0 / sr
    y_lp = 0.0
    a_lp = dt / (1.0 / (2.0 * math.pi * 3500.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.sin(math.pi * (t / (n * dt))) ** 0.5
        x = osc_noise(rng) * 0.55
        y_lp = y_lp + a_lp * (x - y_lp)
        out[i] = y_lp * env * 0.7
    return out


def sfx_season_success(sr):
    # Act 2 season-success reveal · gentle chime, bright.
    return _concat(
        instr_soft_sine(freq_of_midi(midi_of('D5')), 0.10, sr),
        instr_soft_sine(freq_of_midi(midi_of('F#5')), 0.12, sr),
        instr_soft_sine(freq_of_midi(midi_of('A5')), 0.22, sr),
    )


def sfx_season_failure(sr):
    # Act 2 season-failure reveal · slightly bent low tone falling.
    n = int(0.55 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 3.0)
        # F3 down to E3 across 300ms
        f = 174.6 - (174.6 - 164.8) * min(1.0, t / 0.30)
        out[i] = (osc_sine(ph) * 0.6 + osc_triangle(ph * 0.5) * 0.25) * env * 0.42
        ph += f * dt
    return out


def sfx_tide_gate_toggle(sr):
    # Wet-metal ratchet · high-freq metallic clicks + water noise.
    n = int(0.40 * sr)
    out = [0.0] * n
    rng = [8121]
    dt = 1.0 / sr
    # Three ratchet ticks at 60ms, 140ms, 220ms
    tick_at = [int(0.06 * sr), int(0.14 * sr), int(0.22 * sr)]
    for start in tick_at:
        tick_n = int(0.02 * sr)
        for j in range(tick_n):
            idx = start + j
            if idx >= n: break
            t = j * dt
            env = math.exp(-t * 220.0)
            # metallic ping · a couple of high partials
            m = osc_sine(2400.0 * t) * 0.5 + osc_sine(3400.0 * t) * 0.35
            out[idx] += m * env * 0.55
    # Water flush · low-pass noise across the whole clip
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 1200.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.sin(math.pi * (t / (n * dt))) ** 0.6
        x = osc_noise(rng) * 0.45 * env
        y = y + a * (x - y)
        out[i] += y * 0.35
    return out


def sfx_wave_break(sr):
    # Season-transition foam · noise sweep from low → high → low.
    n = int(0.70 * sr)
    out = [0.0] * n
    rng = [9292]
    dt = 1.0 / sr
    y = 0.0
    for i in range(n):
        t = i * dt
        # Sweep cutoff: 400 → 3000 → 800 Hz across the clip
        p = t / (n * dt)
        cutoff = 400.0 + 2600.0 * (1.0 - abs(p - 0.4) / 0.6)
        rc = 1.0 / (2.0 * math.pi * max(200.0, cutoff))
        a = dt / (rc + dt)
        env = math.sin(math.pi * p) ** 0.7
        x = osc_noise(rng) * 0.6 * env
        y = y + a * (x - y)
        out[i] = y * 0.5
    return out


def sfx_gull_cry(sr):
    # Descending glide + a small noise burst.  Aggressive downward
    # pitch bend approximating a herring gull's characteristic cry.
    n = int(0.35 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    rng = [1717]
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 4.5)
        # C6 (1046) down to A5 (880) then E5 (659)
        p = t / (n * dt)
        if p < 0.3:
            f = 1046.0 - (1046.0 - 880.0) * (p / 0.3)
        else:
            f = 880.0 - (880.0 - 659.0) * ((p - 0.3) / 0.7)
        s = osc_saw(ph) * 0.35 + osc_sine(ph * 2.0) * 0.20
        noise = osc_noise(rng) * 0.10
        out[i] = (s + noise) * env * 0.55
        ph += f * dt
    return out


def sfx_heron_wingbeat(sr):
    # Whoosh-whoosh · two slow air-rush hits, 250ms apart.
    def _whoosh():
        m = int(0.18 * sr)
        buf = [0.0] * m
        rng = [3535]
        dt = 1.0 / sr
        for j in range(m):
            t = j * dt
            env = math.sin(math.pi * (t / (m * dt))) ** 0.8
            x = osc_noise(rng) * 0.55 * env
            # 300-Hz LPF band-limits the air
            buf[j] = x
        # LPF pass
        y = 0.0
        a = dt / (1.0 / (2.0 * math.pi * 1200.0) + dt)
        for j in range(m):
            y = y + a * (buf[j] - y)
            buf[j] = y * 0.6
        return buf
    a = _whoosh()
    gap = [0.0] * int(0.10 * sr)
    b = _whoosh()
    return _concat(a, gap, b)


def sfx_hotspot_look(sr):
    # Soft chirp · slightly warmer than verb_select · reveals an
    # observation.
    return instr_soft_sine(freq_of_midi(midi_of('A5')), 0.06, sr)


def sfx_hotspot_talk(sr):
    # Two-tone question · rising interval that suggests dialogue.
    return _concat(
        instr_soft_sine(freq_of_midi(midi_of('E5')), 0.05, sr),
        instr_soft_sine(freq_of_midi(midi_of('G5')), 0.09, sr),
    )


def sfx_hotspot_use(sr):
    # Mechanical click · sub-tri with a brief noise pop.
    n = int(0.06 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    rng = [4949]
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 60.0)
        out[i] = (osc_triangle(ph) * 0.4 + osc_noise(rng) * 0.20) * env * 0.45
        ph += 320.0 * dt
    return out


def sfx_clock_tick(sr):
    # Metronome tick · a short filtered noise pop.
    n = int(0.03 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    rng = [6767]
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 2000.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 90.0)
        x = osc_noise(rng) * 0.6 * env
        y = y + a * (x - y)
        out[i] = y * 0.55
    return out


def sfx_return_to_shop(sr):
    # Bell over the Kwik Stop's door on return · brighter than
    # customer_bell (which is night · this is dusk).  Two rings.
    a = instr_soft_sine(freq_of_midi(midi_of('E6')), 0.10, sr)
    b = instr_soft_sine(freq_of_midi(midi_of('B5')), 0.16, sr)
    gap = [0.0] * int(0.08 * sr)
    c = instr_soft_sine(freq_of_midi(midi_of('E6')), 0.08, sr)
    return _concat(a, b, gap, c)


def sfx_creature_arrival_heron(sr):
    # Wingbeat + a soft single-note trill.
    beat = sfx_heron_wingbeat(sr)
    note = instr_soft_sine(freq_of_midi(midi_of('B4')), 0.18, sr)
    n = max(len(beat), len(note))
    out = [0.0] * n
    for i in range(len(beat)): out[i] += beat[i] * 0.55
    for i in range(len(note)): out[i] += note[i] * 0.32
    return out


def sfx_creature_arrival_otter(sr):
    # Small water splash · brief noise burst + tuned pop.
    n = int(0.22 * sr)
    out = [0.0] * n
    rng = [2626]
    dt = 1.0 / sr
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 12.0)
        splash = osc_noise(rng) * env * 0.55
        # Small resonant tail
        tail = osc_sine(180.0 * t) * math.exp(-t * 10.0) * 0.20
        out[i] = splash + tail
    return out


def sfx_creature_arrival_crab(sr):
    # Two dry clicks · a crab's carapace on wet sand.
    def _click():
        m = int(0.02 * sr)
        buf = [0.0] * m
        rng = [8383]
        dt = 1.0 / sr
        y = 0.0
        a = dt / (1.0 / (2.0 * math.pi * 3000.0) + dt)
        for j in range(m):
            t = j * dt
            env = math.exp(-t * 200.0)
            x = osc_noise(rng) * 0.65 * env
            y = y + a * (x - y)
            buf[j] = (x - y) * 0.65
        return buf
    a = _click()
    gap = [0.0] * int(0.06 * sr)
    b = _click()
    return _concat(a, gap, b)


def sfx_creature_arrival_fry(sr):
    # Tiny high-freq water flicker · cutthroat fry in a tide pool.
    n = int(0.16 * sr)
    out = [0.0] * n
    rng = [1919]
    dt = 1.0 / sr
    y_hp = 0.0
    a_hp = dt / (1.0 / (2.0 * math.pi * 4200.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.sin(math.pi * (t / (n * dt))) ** 0.7
        x = osc_noise(rng) * 0.55 * env
        y_hp = y_hp + a_hp * (x - y_hp)
        out[i] = (x - y_hp) * 0.5
    return out


def sfx_tide_swallow(sr):
    # Slow whoosh · the tide reaches the drawing.  One-shot at end.
    n = int(1.20 * sr)
    out = [0.0] * n
    rng = [2020]
    dt = 1.0 / sr
    y = 0.0
    for i in range(n):
        t = i * dt
        p = t / (n * dt)
        # Rising cutoff · 300 → 2600 Hz, then a slight drop
        cutoff = 300.0 + 2300.0 * min(1.0, p * 1.4)
        rc = 1.0 / (2.0 * math.pi * max(200.0, cutoff))
        a = dt / (rc + dt)
        # Envelope: fade in, hold, gentle fade
        env = 0.0
        if p < 0.3:
            env = p / 0.3
        elif p < 0.75:
            env = 1.0
        else:
            env = max(0.0, (1.0 - p) / 0.25)
        x = osc_noise(rng) * 0.6 * env
        y = y + a * (x - y)
        out[i] = y * 0.65
    return out


def sfx_signing(sr):
    # Sam signs the drawing · a very short final stick-scratch,
    # softer than the running stick_scratch preset.
    n = int(0.14 * sr)
    out = [0.0] * n
    rng = [3939]
    dt = 1.0 / sr
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 1400.0) + dt)
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 14.0)
        x = osc_noise(rng) * 0.5 * env
        y = y + a * (x - y)
        out[i] = y * 0.45
    return out


def sfx_page_turn(sr):
    # Paper turn · a soft brief brush + a small crackle.
    n = int(0.35 * sr)
    out = [0.0] * n
    rng = [7373]
    dt = 1.0 / sr
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 2400.0) + dt)
    for i in range(n):
        t = i * dt
        # Two amplitude peaks: 0.05s brush, 0.20s crackle
        env = 0.0
        if t < 0.10:
            env = math.sin(math.pi * (t / 0.10)) ** 0.5 * 0.6
        elif 0.18 < t < 0.28:
            env = math.sin(math.pi * ((t - 0.18) / 0.10)) ** 0.5 * 0.4
        x = osc_noise(rng) * 0.55 * env
        y = y + a * (x - y)
        out[i] = y * 0.5
    return out


def sfx_unlock_chime(sr):
    # New shelf-wave unlocks · a bright ascending 3-note arpeggio
    # slightly slower than scenario_unlock's 4-note.
    return _concat(
        instr_soft_sine(freq_of_midi(midi_of('D5')), 0.14, sr),
        instr_soft_sine(freq_of_midi(midi_of('A5')), 0.14, sr),
        instr_soft_sine(freq_of_midi(midi_of('D6')), 0.42, sr),
    )


def sfx_creature_arrival_kid_on_bike(sr):
    # Bike gear-shift click · a sharp mechanical click, then
    # the freewheel tick-tick-tick of a bike coasting away.
    click_n = int(0.05 * sr)
    click = [0.0] * click_n
    rng = [4141]
    dt = 1.0 / sr
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 4000.0) + dt)
    for i in range(click_n):
        t = i * dt
        env = math.exp(-t * 70.0)
        x = osc_noise(rng) * 0.7 * env
        y = y + a * (x - y)
        click[i] = (x - y) * 0.6
    # Freewheel · a repeating filtered tick at ~10 Hz, fading out.
    fw_seconds = 1.4
    fw_n = int(fw_seconds * sr)
    fw = [0.0] * fw_n
    tick_rate = 10.0
    tick_dur = 0.008
    tick_samples = int(tick_dur * sr)
    for tick_i in range(int(fw_seconds * tick_rate)):
        start = int(tick_i / tick_rate * sr)
        env_base = math.exp(-(tick_i / tick_rate) * 1.2)
        for j in range(tick_samples):
            idx = start + j
            if idx >= fw_n: break
            t = j / tick_samples
            env = env_base * math.exp(-t * 200.0)
            fw[idx] += osc_sine(3500.0 * (j * dt)) * env * 0.32
    return _concat(click, fw)




def sfx_calliope_drift(sr):
    # Fey Faire · a fragment of the carousel calliope heard from three
    # booths away.  Three soft vibrato notes (D5 F5 A5) with a slow
    # swell, as if the wind carried them over and then took them back.
    n = int(2.6 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    notes = [(587.33, 0.0, 0.8), (698.46, 0.7, 0.8), (880.0, 1.4, 1.1)]
    for freq, start, dur in notes:
        s0 = int(start * sr)
        dn = int(dur * sr)
        ph = 0.0
        for j in range(dn):
            idx = s0 + j
            if idx >= n: break
            t = j * dt
            env = math.sin(math.pi * min(1.0, t / dur)) ** 1.5
            vib = 1.0 + 0.008 * math.sin(2.0 * math.pi * 5.5 * t)
            ph += freq * vib * dt
            v = osc_sine(ph) * 0.7 + osc_sine(ph * 2.0) * 0.18
            out[idx] += v * env * 0.30
    # Wind swell under it
    rng = [4242]
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 500.0) + dt)
    for i in range(n):
        t = i * dt
        p_ = t / (n * dt)
        env = math.sin(math.pi * p_) ** 2.0
        x = osc_noise(rng) * 0.25 * env
        y = y + a * (x - y)
        out[i] += y * 0.22
    return out


def sfx_canvas_flap(sr):
    # Fey Faire · tent canvas taking the night wind.  Two soft
    # low-passed thumps with a fabric hiss tail.
    n = int(1.3 * sr)
    out = [0.0] * n
    rng = [7777]
    dt = 1.0 / sr
    y = 0.0
    a = dt / (1.0 / (2.0 * math.pi * 900.0) + dt)
    flaps = [0.05, 0.55]
    for i in range(n):
        t = i * dt
        env = 0.0
        for f0 in flaps:
            if t >= f0:
                env += math.exp(-(t - f0) * 9.0)
        x = osc_noise(rng) * min(1.0, env) * 0.6
        y = y + a * (x - y)
        out[i] = y * 0.55
    return out


def sfx_night_crowd(sr):
    # Fey Faire · the midway crowd from a distance.  Band-passed
    # murmur with a slow wobble and two faint laugh-blips.
    n = int(3.0 * sr)
    out = [0.0] * n
    rng = [1990]
    dt = 1.0 / sr
    y1 = 0.0
    y2 = 0.0
    a1 = dt / (1.0 / (2.0 * math.pi * 700.0) + dt)
    a2 = dt / (1.0 / (2.0 * math.pi * 180.0) + dt)
    for i in range(n):
        t = i * dt
        p_ = t / (n * dt)
        wob = 0.7 + 0.3 * math.sin(2.0 * math.pi * 0.35 * t + 1.2)
        env = math.sin(math.pi * p_) ** 0.8
        x = osc_noise(rng) * wob * env
        y1 = y1 + a1 * (x - y1)
        y2 = y2 + a2 * (y1 - y2)
        out[i] = (y1 - y2) * 0.5
    # Two faint laugh-blips
    for f0, freq in [(1.1, 740.0), (2.2, 620.0)]:
        s0 = int(f0 * sr)
        dn = int(0.12 * sr)
        ph = 0.0
        for j in range(dn):
            idx = s0 + j
            if idx >= n: break
            t = j * dt
            env = math.exp(-t * 30.0)
            ph += freq * dt
            out[idx] += osc_sine(ph) * env * 0.10
    return out



def sfx_parsa_wind(sr):
    # Earthman · dune wind with a grain of sand-hiss.  A long swell
    # that never quite peaks · the desert has nowhere to be.
    n = int(3.2 * sr)
    out = [0.0] * n
    rng = [8585]
    dt = 1.0 / sr
    y = 0.0
    for i in range(n):
        t = i * dt
        p_ = t / (n * dt)
        cutoff = 300.0 + 500.0 * math.sin(math.pi * p_) ** 2.0
        rc = 1.0 / (2.0 * math.pi * cutoff)
        a = dt / (rc + dt)
        env = math.sin(math.pi * p_) ** 1.2
        x = osc_noise(rng) * 0.6 * env
        y = y + a * (x - y)
        out[i] = y * 0.6
    return out


def sfx_mine_drip(sr):
    # Earthman · three water drips in a deep stone space, each with
    # a small pitched bloom and a long dark tail.
    n = int(2.4 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    drips = [(0.1, 1180.0), (0.9, 990.0), (1.7, 1240.0)]
    for f0, freq in drips:
        s0 = int(f0 * sr)
        dn = int(0.5 * sr)
        ph = 0.0
        for j in range(dn):
            idx = s0 + j
            if idx >= n: break
            t = j * dt
            env = math.exp(-t * 14.0)
            bend = freq * (1.0 - 0.25 * min(1.0, t * 8.0))
            ph += bend * dt
            out[idx] += osc_sine(ph) * env * 0.4
    return out


def sfx_kyrindi_bell(sr):
    # Earthman · a single Kyrindi tower bell · A4 with a slightly
    # inharmonic partial (the silver-blue overtone) and a long decay.
    n = int(2.8 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph1 = 0.0
    ph2 = 0.0
    ph3 = 0.0
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 1.6)
        ph1 += 440.0 * dt
        ph2 += 440.0 * 2.76 * dt
        ph3 += 440.0 * 5.4 * dt
        v = osc_sine(ph1) * 0.55 + osc_sine(ph2) * 0.25 * math.exp(-t * 3.0) + osc_sine(ph3) * 0.10 * math.exp(-t * 6.0)
        out[i] = v * env * 0.5
    return out



# ── Northwind Harbor one-shots (1988 · almost no sound, so each counts) ──

def sfx_boat_horn(sr):
    # The loudest thing in the game.  A low two-tone air horn ·
    # fundamental around 110 Hz with a slightly detuned partner,
    # slow attack, long body, breathy noise floor.
    n = int(2.2 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph1 = 0.0
    ph2 = 0.0
    rng = [8819]
    for i in range(n):
        t = i * dt
        attack = min(1.0, t / 0.18)
        release = min(1.0, max(0.0, (2.2 - t) / 0.5))
        env = attack * release
        v = osc_saw(ph1) * 0.30 + osc_saw(ph2) * 0.26 + osc_sine(ph1 * 0.5) * 0.25
        breath = osc_noise(rng) * 0.05
        out[i] = (v + breath) * env * 0.6
        ph1 += 112.0 * dt
        ph2 += 118.5 * dt
    return out


def sfx_lamp_buzz(sr):
    # The sodium lamp catching · a flicker of starts, then the
    # steady 120 Hz ballast buzz Karl has known since '79.
    n = int(1.6 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    rng = [4141]
    for i in range(n):
        t = i * dt
        if t < 0.5:
            gate = 1.0 if (int(t * 22.0) % 3) != 1 else 0.15
            level = 0.5 * gate
        else:
            level = min(1.0, 0.5 + (t - 0.5) * 1.2)
        v = osc_square(ph, 0.5) * 0.16 + osc_sine(ph * 2.0) * 0.10
        grit = osc_noise(rng) * 0.03
        out[i] = (v + grit) * level * 0.55
        ph += 120.0 * dt
    return out


def sfx_water_slap(sr):
    # Water slapping a piling · a soft noise thump with a low sine
    # body and a short wet tail.
    n = int(0.5 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    rng = [2027]
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 9.0)
        tail = math.exp(-t * 3.0) * 0.3
        body = osc_sine(ph) * 0.4 * env
        wash = osc_noise(rng) * (0.30 * env + 0.08 * tail)
        out[i] = (body + wash) * 0.6
        ph += (90.0 - t * 60.0) * dt
    return out


def sfx_boot_plank(sr):
    # A boot on a dock plank · knock with a little wooden ring.
    n = int(0.22 * sr)
    out = [0.0] * n
    dt = 1.0 / sr
    ph = 0.0
    rng = [5511]
    for i in range(n):
        t = i * dt
        env = math.exp(-t * 26.0)
        knock = osc_sine(ph) * 0.5
        crack = osc_noise(rng) * 0.22 * math.exp(-t * 60.0)
        out[i] = (knock + crack) * env * 0.6
        ph += (180.0 - t * 220.0) * dt
    return out


SFX_PRESETS = {
    # Northwind Harbor one-shots
    'boat_horn':          sfx_boat_horn,
    'lamp_buzz':          sfx_lamp_buzz,
    'water_slap':         sfx_water_slap,
    'boot_plank':         sfx_boot_plank,
    # Earthman ambient one-shots
    'parsa_wind':         sfx_parsa_wind,
    'mine_drip':          sfx_mine_drip,
    'kyrindi_bell':       sfx_kyrindi_bell,
    # Fey Faire ambient one-shots
    'calliope_drift':     sfx_calliope_drift,
    'canvas_flap':        sfx_canvas_flap,
    'night_crowd':        sfx_night_crowd,
    # Original set
    'coin':               sfx_coin,
    'hurt':               sfx_hurt,
    'jump':               sfx_jump,
    'blip':               sfx_blip,
    'pickup':             sfx_pickup,
    'door_open':          sfx_door_open,
    'register_ding':      sfx_register_ding,
    'phone_ring':         sfx_phone_ring,
    'broom_sweep':        sfx_broom_sweep,
    'cooler_whoosh':      sfx_cooler_whoosh,
    'fluorescent_start':  sfx_fluorescent_start,
    'tide_pool_splash':   sfx_tide_pool_splash,
    'stick_scratch':      sfx_stick_scratch,
    # Wave A · UI
    'verb_select':        sfx_verb_select,
    'turn_tick':          sfx_turn_tick,
    'customer_bell':      sfx_customer_bell,
    'control_click':      sfx_control_click,
    'season_settle':      sfx_season_settle,
    'tile_hover':         sfx_tile_hover,
    'tile_enter':         sfx_tile_enter,
    'press_hit':          sfx_press_hit,
    'press_miss':         sfx_press_miss,
    'cartridge_hover':    sfx_cartridge_hover,
    'cartridge_click':    sfx_cartridge_click,
    'boot':               sfx_boot,
    # Wave C · Community Planned demon-depth
    'tier_crossing_hungry':   sfx_tier_crossing_hungry,
    'tier_crossing_restless': sfx_tier_crossing_restless,
    'tier_crossing_close':    sfx_tier_crossing_close,
    'tier_crossing_turned':   sfx_tier_crossing_turned,
    'basement_rite':          sfx_basement_rite,
    'pair_warm':              sfx_pair_warm,
    'pair_loud':              sfx_pair_loud,
    'pair_cold':              sfx_pair_cold,
    'marker_set':             sfx_marker_set,
    'marker_expire':          sfx_marker_expire,
    'quiet_week':             sfx_quiet_week,
    'roster_loud':            sfx_roster_loud,
    'interlude_earned':       sfx_interlude_earned,
    'labor_day_arrival':      sfx_labor_day_arrival,
    # Wave D · Gauntlet
    'card_flip':              sfx_card_flip,
    'card_place':             sfx_card_place,
    'hand_deal':              sfx_hand_deal,
    'threshold_cross':        sfx_threshold_cross,
    'visitor_arrive':         sfx_visitor_arrive,
    'lore_token_reveal':      sfx_lore_token_reveal,
    'scrapbook_open':         sfx_scrapbook_open,
    'scenario_unlock':        sfx_scenario_unlock,
    'scenario_picker':        sfx_scenario_picker,
    'win_chord':              sfx_win_chord,
    'loss_thud':              sfx_loss_thud,
    # Wave D · Shared UI
    'menu_open':              sfx_menu_open,
    'menu_close':             sfx_menu_close,
    'button_hover':           sfx_button_hover,
    'button_click':           sfx_button_click,
    'save_confirm':           sfx_save_confirm,
    'load_start':             sfx_load_start,
    'notification':           sfx_notification,
    # Wave E · deferred beats
    'radio_889_bed':                        sfx_radio_889_bed,
    'radio_1150_bed':                       sfx_radio_1150_bed,
    'radio_1600_static_voice_night_5':      sfx_radio_1600_static_voice_night_5,
    'radio_1600_static_voice_night_12_sam': sfx_radio_1600_static_voice_night_12_sam,
    '2am_customer_stands_up':               sfx_2am_customer_stands_up,
    'creature_arrival_2am_customer':        sfx_creature_arrival_2am_customer,
    'creature_arrival_kid_on_bike':         sfx_creature_arrival_kid_on_bike,
    # Wave F · closing set
    'radio_static':                sfx_radio_static,
    'season_success':              sfx_season_success,
    'season_failure':              sfx_season_failure,
    'tide_gate_toggle':            sfx_tide_gate_toggle,
    'wave_break':                  sfx_wave_break,
    'gull_cry':                    sfx_gull_cry,
    'heron_wingbeat':              sfx_heron_wingbeat,
    'hotspot_look':                sfx_hotspot_look,
    'hotspot_talk':                sfx_hotspot_talk,
    'hotspot_use':                 sfx_hotspot_use,
    'clock_tick':                  sfx_clock_tick,
    'return_to_shop':              sfx_return_to_shop,
    'creature_arrival_heron':      sfx_creature_arrival_heron,
    'creature_arrival_otter':      sfx_creature_arrival_otter,
    'creature_arrival_crab':       sfx_creature_arrival_crab,
    'creature_arrival_fry':        sfx_creature_arrival_fry,
    'tide_swallow':                sfx_tide_swallow,
    'signing':                     sfx_signing,
    'page_turn':                   sfx_page_turn,
    'unlock_chime':                sfx_unlock_chime,
}


# ─── MIDI parser (fallback · minimal) ──────────────────────────────

def parse_midi(path):
    """
    Minimal MIDI parser. Reads standard MIDI file · returns a
    composition-like dict. Format 0 or 1. Note-on / note-off /
    tempo / program-change. Ignores everything else.

    Enough for a composer to write a .mid in any DAW and pipe it
    through this tool.
    """
    with open(path, 'rb') as f:
        data = f.read()

    def read_int(off, n):
        return int.from_bytes(data[off:off + n], 'big'), off + n

    def read_vlq(off):
        v = 0
        while True:
            b = data[off]; off += 1
            v = (v << 7) | (b & 0x7f)
            if not (b & 0x80):
                return v, off

    # Header
    assert data[:4] == b'MThd', 'not a MIDI file'
    hdr_len, o = read_int(4, 4)
    fmt, o = read_int(o, 2)
    ntrks, o = read_int(o, 2)
    division, o = read_int(o, 2)
    ppqn = division & 0x7fff   # assume metric

    tempo_bpm = 120.0
    notes = []   # (start_ticks, dur_ticks, pitch, channel, velocity)
    active = {}   # (channel, pitch) → start_ticks
    prog_by_channel = {}   # channel → program

    for _ in range(ntrks):
        assert data[o:o + 4] == b'MTrk', 'expected MTrk'
        _tlen, o = read_int(o + 4, 4)
        t_ticks = 0
        running_status = None
        end = o + _tlen
        while o < end:
            delta, o = read_vlq(o)
            t_ticks += delta
            b = data[o]
            if b & 0x80:
                status = b; o += 1
                running_status = status
            else:
                status = running_status
            if status is None:
                o += 1; continue
            evt = status & 0xf0
            ch = status & 0x0f
            if evt == 0x90:   # note-on
                pitch = data[o]; o += 1
                vel = data[o]; o += 1
                if vel > 0:
                    active[(ch, pitch)] = (t_ticks, vel)
                else:
                    if (ch, pitch) in active:
                        st, v = active.pop((ch, pitch))
                        notes.append((st, t_ticks - st, pitch, ch, v))
            elif evt == 0x80:   # note-off
                pitch = data[o]; o += 1
                _vel = data[o]; o += 1
                if (ch, pitch) in active:
                    st, v = active.pop((ch, pitch))
                    notes.append((st, t_ticks - st, pitch, ch, v))
            elif evt == 0xc0:   # program change
                prog = data[o]; o += 1
                prog_by_channel[ch] = prog
            elif evt == 0xa0 or evt == 0xb0 or evt == 0xe0:
                o += 2
            elif evt == 0xd0:
                o += 1
            elif status == 0xff:   # meta
                mtype = data[o]; o += 1
                mlen, o = read_vlq(o)
                if mtype == 0x51 and mlen == 3:
                    us = int.from_bytes(data[o:o + 3], 'big')
                    tempo_bpm = 60_000_000.0 / us
                o += mlen
            elif status == 0xf0 or status == 0xf7:
                mlen, o = read_vlq(o)
                o += mlen
            else:
                o += 1

    # Convert (ticks) to (bar, beat, dur_beats). Assume 4/4.
    tracks_by_channel = {}
    for st, dur, pitch, ch, vel in notes:
        beat = st / ppqn + 1.0        # 1-based
        dur_beats = dur / ppqn
        bar = int((beat - 1.0) // 4) + 1
        beat_in_bar = ((beat - 1.0) % 4) + 1.0
        # Pick instrument by GM program family.
        prog = prog_by_channel.get(ch, 0)
        inst = _gm_program_to_instrument(prog)
        tracks_by_channel.setdefault(ch, {
            'instrument': inst, 'gain': 0.7, 'notes': []
        })
        tracks_by_channel[ch]['notes'].append({
            'pitch': int(pitch),
            'bar':   float(bar),
            'beat':  float(beat_in_bar),
            'dur':   float(dur_beats),
            'vel':   float(vel) / 127.0,
        })

    return {
        'meta': {'title': os.path.basename(path), 'source': 'midi'},
        'tempo_bpm': tempo_bpm,
        'time_sig':  [4, 4],
        'tracks':    list(tracks_by_channel.values()),
    }


def _gm_program_to_instrument(prog):
    # GM: 0-7 pianos, 32-39 basses, 40-47 strings, 80-87 leads,
    # 88-95 pads. Crude map to our instruments.
    if 32 <= prog <= 39:  return 'slowstick_bass'
    if 80 <= prog <= 87:  return 'slowstick_lead'
    if 88 <= prog <= 95:  return 'slowstick_pad'
    if 96 <= prog <= 103: return 'ambient_drone'
    if 112 <= prog <= 119: return 'fluorescent_hum'
    return 'slowstick_lead'


# ─── WAV writer ────────────────────────────────────────────────────

def write_wav(samples, sample_rate, path, stereo=False, bit_depth=16):
    if bit_depth not in (16, 24):
        raise ValueError('bit_depth must be 16 or 24')
    n_channels = 2 if stereo else 1
    byte_depth = bit_depth // 8
    frame_size = n_channels * byte_depth
    n_frames = len(samples)
    byte_rate = sample_rate * frame_size
    data_size = n_frames * frame_size
    # RIFF header
    with open(path, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('<H', 1))                # PCM
        f.write(struct.pack('<H', n_channels))
        f.write(struct.pack('<I', sample_rate))
        f.write(struct.pack('<I', byte_rate))
        f.write(struct.pack('<H', frame_size))
        f.write(struct.pack('<H', bit_depth))
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        # samples
        for s in samples:
            v = max(-1.0, min(1.0, s))
            if bit_depth == 16:
                iv = int(v * 32767)
                if stereo:
                    f.write(struct.pack('<hh', iv, iv))
                else:
                    f.write(struct.pack('<h', iv))
            else:
                iv = int(v * 8388607)
                b = iv.to_bytes(3, 'little', signed=True)
                if stereo:
                    f.write(b); f.write(b)
                else:
                    f.write(b)


# ─── CLI ───────────────────────────────────────────────────────────

def main(argv):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)

    ps_compose = sub.add_parser('compose', help='render a JSON composition to WAV')
    ps_compose.add_argument('input',  type=str)
    ps_compose.add_argument('output', type=str, nargs='?')
    ps_compose.add_argument('--stereo', action='store_true')
    ps_compose.add_argument('--bit-depth', type=int, default=16, choices=[16, 24])
    ps_compose.add_argument('--sample-rate', type=int, default=None)

    ps_midi = sub.add_parser('midi', help='render a .mid file to WAV')
    ps_midi.add_argument('input',  type=str)
    ps_midi.add_argument('output', type=str, nargs='?')
    ps_midi.add_argument('--stereo', action='store_true')
    ps_midi.add_argument('--bit-depth', type=int, default=16, choices=[16, 24])
    ps_midi.add_argument('--sample-rate', type=int, default=None)

    ps_sfx = sub.add_parser('sfx', help='render a named SFX preset to WAV')
    ps_sfx.add_argument('preset', type=str,
                        choices=sorted(SFX_PRESETS.keys()) + ['all'])
    ps_sfx.add_argument('output', type=str, nargs='?')

    ps_ls = sub.add_parser('list', help='list available instruments and SFX presets')

    args = p.parse_args(argv)

    if args.cmd == 'list':
        print("INSTRUMENTS:")
        for k in sorted(INSTRUMENTS.keys()):
            print(f"  {k}")
        print("\nSFX PRESETS:")
        for k in sorted(SFX_PRESETS.keys()):
            print(f"  {k}")
        return 0

    if args.cmd == 'compose':
        with open(args.input) as f:
            comp = json.load(f)
        mix, sr = render_composition(comp, sample_rate=args.sample_rate)
        out = args.output or Path(args.input).with_suffix('.wav')
        write_wav(mix, sr, out, stereo=args.stereo, bit_depth=args.bit_depth)
        print(f"wrote {out}  ({len(mix)/sr:.2f}s @ {sr}Hz)")
        return 0

    if args.cmd == 'midi':
        comp = parse_midi(args.input)
        mix, sr = render_composition(comp, sample_rate=args.sample_rate)
        out = args.output or Path(args.input).with_suffix('.wav')
        write_wav(mix, sr, out, stereo=args.stereo, bit_depth=args.bit_depth)
        print(f"wrote {out}  ({len(mix)/sr:.2f}s @ {sr}Hz · from midi)")
        return 0

    if args.cmd == 'sfx':
        sr = SAMPLE_RATE_DEFAULT
        if args.preset == 'all':
            outdir = Path(args.output or 'godot/tools/audio/sfx')
            outdir.mkdir(parents=True, exist_ok=True)
            for name in sorted(SFX_PRESETS.keys()):
                samples = SFX_PRESETS[name](sr)
                path = outdir / f"{name}.wav"
                write_wav(samples, sr, path)
                print(f"  {name}: {len(samples)/sr:.2f}s → {path}")
        else:
            samples = SFX_PRESETS[args.preset](sr)
            out = args.output or f"{args.preset}.wav"
            write_wav(samples, sr, out)
            print(f"wrote {out}  ({len(samples)/sr:.2f}s)")
        return 0

    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
