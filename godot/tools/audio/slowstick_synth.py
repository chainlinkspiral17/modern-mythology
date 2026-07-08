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


SFX_PRESETS = {
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
