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
var _hud_label: Label
var _hud_layer: CanvasLayer


func _ready() -> void:
	_stream_player = AudioStreamPlayer.new()
	_stream_player.bus = "Master"
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = float(SAMPLE_RATE)
	gen.buffer_length = 0.20
	_stream_player.stream = gen
	add_child(_stream_player)
	_stream_player.play()
	_playback = _stream_player.get_stream_playback()
	if _playback == null:
		push_error("[PDPRiffmaster] FAILED to get_stream_playback() — audio pipeline broken")
	else:
		print("[PDPRiffmaster] online · keys 1-8 (Shift = octave up) · playback ready")
	_spawn_hud()


func _spawn_hud() -> void:
	_hud_layer = CanvasLayer.new()
	_hud_layer.layer = 109
	_hud_layer.add_to_group("ui")
	add_child(_hud_layer)
	_hud_label = Label.new()
	_hud_label.offset_left = 16.0
	_hud_label.offset_top = 580.0
	_hud_label.offset_right = 1264.0
	_hud_label.offset_bottom = 626.0
	_hud_label.add_theme_font_size_override("font_size", 18)
	_hud_label.add_theme_color_override("font_color", Color(1.0, 0.86, 0.36, 1.0))
	_hud_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_hud_label.add_theme_constant_override("outline_size", 3)
	_hud_label.text = "RIFFMASTER · press 1-8 (Shift = +octave) · ready"
	_hud_layer.add_child(_hud_label)


func _input(event: InputEvent) -> void:
	# NOTE — switched from _unhandled_input to _input so the Riffmaster
	# gets the events BEFORE any UI / scene-level consumer can eat
	# them. Number row keys are easy to lose if any Control has focus.
	if event is InputEventKey:
		# Match either keycode or physical_keycode so non-QWERTY
		# layouts still hit the row keys at the same physical
		# positions.
		var k: int = event.keycode
		var pk: int = event.physical_keycode
		var keycode: int = k
		if not KEY_TO_SEMITONES.has(keycode) and KEY_TO_SEMITONES.has(pk):
			keycode = pk
		if not KEY_TO_SEMITONES.has(keycode):
			return
		if event.pressed and not event.echo:
			var semitones: int = KEY_TO_SEMITONES[keycode]
			if event.shift_pressed:
				semitones += 12
			var freq: float = BASE_FREQ * pow(2.0, float(semitones) / 12.0)
			_voices[keycode] = {
				"freq":       freq,
				"phase":      0.0,
				"env_t":      0.0,
				"released":   false,
				"release_t":  0.0,
				"release_amp":0.0,
			}
			print("[PDPRiffmaster] ▶ %s (key %d → %.1f Hz)" %
				  [_note_name(KEY_TO_SEMITONES[keycode] + (12 if event.shift_pressed else 0)),
				   keycode, freq])
		elif not event.pressed:
			if _voices.has(keycode):
				var v: Dictionary = _voices[keycode]
				if not v["released"]:
					v["released"] = true
					v["release_t"] = 0.0
					v["release_amp"] = _envelope_attack_phase(v["env_t"])


func _update_hud() -> void:
	if _hud_label == null:
		return
	if _voices.is_empty():
		_hud_label.text = "RIFFMASTER · press 1-8 (Shift = +octave) · idle"
		return
	var parts: Array[String] = []
	for k in _voices.keys():
		var v: Dictionary = _voices[k]
		var marker: String = "♬" if not v["released"] else "·"
		parts.append("%s %.0fHz" % [marker, v["freq"]])
	_hud_label.text = "RIFFMASTER · %s" % "  ".join(parts)


func _note_name(semitones: int) -> String:
	var names: Array = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
	var octave: int = 4 + int(semitones / 12)
	var n: int = ((semitones % 12) + 12) % 12
	return "%s%d" % [names[n], octave]


func _envelope_attack_phase(env_t: float) -> float:
	if env_t < ATTACK_T:
		return env_t / ATTACK_T
	elif env_t < ATTACK_T + DECAY_T:
		return 1.0 - (1.0 - SUSTAIN_L) * ((env_t - ATTACK_T) / DECAY_T)
	return SUSTAIN_L


func _process(_delta: float) -> void:
	_update_hud()
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
