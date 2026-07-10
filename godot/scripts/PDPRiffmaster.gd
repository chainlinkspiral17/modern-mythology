# PDPRiffmaster.gd
# ════════════════════════════════════════════════════════════════
# IN-FICTION · the PDP Riffmaster — a kids' synth toy from the
# slowstick game ecosystem (vol 7 era). Big plastic buttons, eight
# notes plus a shift key for the upper octave, a single chunky tone
# that's secretly a 3-oscillator saw + saw + sub-triangle with an
# ADSR envelope.
#
# OUT-OF-FICTION · the in-game music input device. Drop this script
# on a Node child of any scene; the 1-8 row keys trigger notes,
# SHIFT pitches up an octave. Notes route through the master bus
# so MoodCycler's _audio_level auto-reactive plumbing picks them
# up — playing notes drives the visualizer in real time.
#
# Designed to FEEL like a toy (chunky, immediate) while being
# legibly "higher quality" than a sine beep — three oscillators
# stacked + the envelope shape lends the sound a polysynth body.
# ════════════════════════════════════════════════════════════════
extends Node

## Fired for every note the voice starts/stops, whether it came
## from the key row or from play_note()/release_note().  The
## Riffmaster Melody Club grades echoes and records the OPEN MIC
## loop through these.
signal note_on(semitones: int)
signal note_off(semitones: int)

## When false, the key row is ignored · replay-only contexts (the
## club playing a call, the Estuary 3 radio) drive the voice
## through play_note()/release_note() instead.
var input_enabled: bool = true

const SAMPLE_RATE: int = 44100
const ATTACK_T:  float = 0.015
const DECAY_T:   float = 0.120
const SUSTAIN_L: float = 0.60
const RELEASE_T: float = 0.450
const MASTER_GAIN: float = 0.18

# C-major scale on the row keys. SHIFT pitches up an octave.
const KEY_TO_SEMITONES: Dictionary = {
	KEY_1: 0, KEY_2: 2, KEY_3: 4, KEY_4: 5,
	KEY_5: 7, KEY_6: 9, KEY_7: 11, KEY_8: 12,
}
const BASE_FREQ: float = 261.626   # middle C

var _stream_player: AudioStreamPlayer
var _playback: AudioStreamGeneratorPlayback
var _voices: Dictionary = {}       # keycode -> voice dict
var _t_per_sample: float = 1.0 / float(SAMPLE_RATE)


func _ready() -> void:
	_stream_player = AudioStreamPlayer.new()
	_stream_player.bus = "Master"
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = float(SAMPLE_RATE)
	gen.buffer_length = 0.10
	_stream_player.stream = gen
	add_child(_stream_player)
	_stream_player.play()
	_playback = _stream_player.get_stream_playback()
	print("[PDPRiffmaster] online · keys 1-8 (Shift = octave up)")


## Attenuate the whole voice · the Estuary 3 radio plays the OPEN
## MIC loop faintly, one wall away.
func set_gain_db(db: float) -> void:
	if _stream_player != null:
		_stream_player.volume_db = db


func _unhandled_input(event: InputEvent) -> void:
	if not input_enabled:
		return
	if event is InputEventKey:
		var keycode: int = event.keycode
		if not KEY_TO_SEMITONES.has(keycode):
			return
		if event.pressed and not event.echo:
			var semitones: int = KEY_TO_SEMITONES[keycode]
			if event.shift_pressed:
				semitones += 12
			_start_voice(keycode, semitones)
		elif not event.pressed:
			_stop_voice(keycode)


## Programmatic playing · same voice, no keyboard.  Voices are
## keyed by semitone offset (negative space from real keycodes).
func play_note(semitones: int) -> void:
	_start_voice(-1000 - semitones, semitones)


func release_note(semitones: int) -> void:
	_stop_voice(-1000 - semitones)


func _start_voice(voice_key: int, semitones: int) -> void:
	var freq: float = BASE_FREQ * pow(2.0, float(semitones) / 12.0)
	_voices[voice_key] = {
		"freq":       freq,
		"semitones":  semitones,
		"phase":      0.0,
		"env_t":      0.0,
		"released":   false,
		"release_t":  0.0,
		"release_amp":0.0,
	}
	note_on.emit(semitones)


func _stop_voice(voice_key: int) -> void:
	if _voices.has(voice_key):
		var v: Dictionary = _voices[voice_key]
		if not v["released"]:
			v["released"] = true
			v["release_t"] = 0.0
			# Sample envelope at release time so the release tail
			# ramps down from whatever the envelope was actually at,
			# not from SUSTAIN_L (avoids clicks on fast keytaps).
			v["release_amp"] = _envelope_attack_phase(v["env_t"])
			note_off.emit(int(v.get("semitones", 0)))


func _envelope_attack_phase(env_t: float) -> float:
	if env_t < ATTACK_T:
		return env_t / ATTACK_T
	elif env_t < ATTACK_T + DECAY_T:
		return 1.0 - (1.0 - SUSTAIN_L) * ((env_t - ATTACK_T) / DECAY_T)
	return SUSTAIN_L


func _process(_delta: float) -> void:
	if _playback == null:
		return
	var frames: int = _playback.get_frames_available()
	if frames <= 0:
		return
	var buf: PackedVector2Array = PackedVector2Array()
	buf.resize(frames)
	var dead: Array = []
	for i in range(frames):
		var sample: float = 0.0
		for keycode in _voices.keys():
			var v: Dictionary = _voices[keycode]
			v["env_t"] += _t_per_sample
			var env: float
			if not v["released"]:
				env = _envelope_attack_phase(v["env_t"])
			else:
				v["release_t"] += _t_per_sample
				if v["release_t"] >= RELEASE_T:
					if not dead.has(keycode):
						dead.append(keycode)
					env = 0.0
				else:
					env = v["release_amp"] * (1.0 - v["release_t"] / RELEASE_T)
			# Multi-osc voice: saw + saw octave up (quieter) + sub-octave triangle.
			# Stacked harmonics give the "toy synth" body without being a sine beep.
			var phase: float = v["phase"]
			var p: float = fposmod(phase, 1.0)
			var saw: float = (p * 2.0 - 1.0) * 0.55
			var p2: float = fposmod(phase * 2.0, 1.0)
			var saw2: float = (p2 * 2.0 - 1.0) * 0.22
			var p_sub: float = fposmod(phase * 0.5, 1.0)
			var sub_tri: float = (abs(p_sub * 2.0 - 1.0) * 2.0 - 1.0) * 0.30
			sample += (saw + saw2 + sub_tri) * env
			v["phase"] += v["freq"] * _t_per_sample
		sample = clamp(sample * MASTER_GAIN, -1.0, 1.0)
		buf[i] = Vector2(sample, sample)
	_playback.push_buffer(buf)
	for k in dead:
		_voices.erase(k)
