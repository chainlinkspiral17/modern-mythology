extends Control
## TarotSynthOverlay — playable arcana instrument.
##
## Mirrors the HTML mock at godot/tools/tarot_synth.html. Cards laid
## out as a 3×8 grid, each clickable + keyboard-mapped. Below: a 4×16
## step sequencer. Transport at bottom (play/stop/clear + BPM + scale
## + root + master vol).
##
## Synthesis: AudioStreamGenerator pushes per-frame mixed sines/saws/
## squares/tri/noise with ADSR + filter approximation per preset. 22
## timbres, one per arcana — pulse_soft, pulse_arp, tri_chorus,
## bell_rich, saw_drive, etc. Designed to be hand-tuned to match the
## HTML's WebAudio version after iteration.
##
## Future puzzle-hook integration: certain played patterns can resolve
## to puzzle IDs via the resources/puzzle_hooks/ system (e.g. playing
## V, IV, III in sequence triggers vol5_aria_handshake unlock).

signal closed

const C_BG       := Color(0.02, 0.012, 0.016)
const C_INK      := Color(0.10, 0.078, 0.063)
const C_RULE     := Color(0.33, 0.20, 0.094)
const C_GOLD     := Color(0.85, 0.63, 0.38)
const C_GOLD_HI  := Color(1.0,  0.85, 0.59)
const C_SEPIA    := Color(0.54, 0.35, 0.15)
const C_BURGUNDY := Color(0.48, 0.12, 0.15)
const C_EMERALD  := Color(0.31, 0.63, 0.38)
const C_EM_HI    := Color(0.66, 0.91, 0.61)
const C_TEXT     := Color(0.78, 0.66, 0.47)
const C_TEXT_DIM := Color(0.48, 0.35, 0.16)

const SAMPLE_RATE := 44100
const BUFFER_LEN  := 0.05    # 50ms generator buffer

# ── Arcana table: matches HTML synth ──────────────────────────────
# [num, name, art_path, key, timbre, semitone_offset, row_color]
const ARCANA = [
	[ 0, "FOOL",         "res://assets/gallery/fool.png",
		KEY_1, "pulse_soft",     0,  "sepia"],
	[ 1, "MAGICIAN",     "res://assets/gallery/magician.png",
		KEY_2, "pulse_arp",      2,  "sepia"],
	[ 2, "PRIESTESS",    "res://assets/gallery/high_priestess.png",
		KEY_3, "tri_chorus",     3,  "sepia"],
	[ 3, "EMPRESS",      "res://assets/gallery/empress.png",
		KEY_4, "bell_rich",      5,  "sepia"],
	[ 4, "EMPEROR",      "res://assets/gallery/emperor.png",
		KEY_5, "saw_drive",      7,  "sepia"],
	[ 5, "HIEROPHANT",   "res://assets/gallery/hierophant.png",
		KEY_6, "organ_stack",    8,  "sepia"],
	[ 6, "LOVERS",       "",
		KEY_7, "duet_bell",     10,  "burgundy"],
	[ 7, "CHARIOT",      "",
		KEY_8, "saw_pulse",     12,  "burgundy"],
	[ 8, "STRENGTH",     "",
		KEY_Q, "rich_brass",    14,  "burgundy"],
	[ 9, "HERMIT",       "",
		KEY_W, "tri_lonely",    15,  "burgundy"],
	[10, "WHEEL",        "",
		KEY_E, "pulse_arp_fast",17,  "burgundy"],
	[11, "JUSTICE",      "",
		KEY_R, "bell_balanced", 19,  "burgundy"],
	[12, "HANGED",       "",
		KEY_T, "drone_low",     20,  "burgundy"],
	[13, "DEATH",        "",
		KEY_Y, "saw_decay",     22,  "burgundy"],
	[14, "TEMPERANCE",   "",
		KEY_U, "tri_flow",      24,  "emerald"],
	[15, "DEVIL",        "",
		KEY_I, "saw_distort",   26,  "emerald"],
	[16, "TOWER",        "",
		KEY_O, "noise_burst",   27,  "emerald"],
	[17, "STAR",         "",
		KEY_P, "bell_high",     29,  "emerald"],
	[18, "MOON",         "",
		KEY_A, "tri_warble",    31,  "emerald"],
	[19, "SUN",          "",
		KEY_S, "pulse_bright",  33,  "emerald"],
	[20, "JUDGEMENT",    "",
		KEY_D, "organ_choir",   34,  "emerald"],
	[21, "WORLD",        "",
		KEY_F, "rich_pad",      36,  "emerald"],
]

# ── Scales — same as HTML ─────────────────────────────────────────
const SCALES = {
	"phrygian":  [0, 1, 3, 5, 7, 8, 10],
	"dorian":    [0, 2, 3, 5, 7, 9, 10],
	"locrian":   [0, 1, 3, 5, 6, 8, 10],
	"aeolian":   [0, 2, 3, 5, 7, 8, 10],
	"harmonic":  [0, 2, 3, 5, 7, 8, 11],
}

# Sequencer state
const SEQ_LANES := 4
const SEQ_STEPS := 16
var _pattern: Array = []   # [lane][step] = arcana_idx or -1

var _bpm: int = 92
var _scale_key: String = "phrygian"
var _root_midi: int = 33   # A1
var _master_vol: float = 0.6

var _playing: bool = false
var _cur_step: int = 0
var _step_accumulator: float = 0.0

var _selected_card: int = 4   # Emperor default

# Active voices for synthesis
class Voice:
	var midi: float
	var timbre: String
	var time: float = 0.0
	var dur: float
	var atk: float
	var dec_: float
	var sus: float
	var rel: float
	var velocity: float
	var detune: float
	var filt: float
	var voices: int = 1
	var harmonic: Array = [1.0]
	var arp: Array = [0]
	var transpose: int = 0
	var done: bool = false

var _voices: Array = []           # active Voice instances
var _gen: AudioStreamGenerator
var _gen_player: AudioStreamPlayer
var _playback: AudioStreamGeneratorPlayback

# UI references
var _cards: Array = []                    # Button per arcana
var _steps: Array = []                    # Button [lane][step]
var _now_playing_label: Label
var _step_display_label: Label
var _bpm_label: Label


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_init_pattern()
	_build_ui()
	_init_audio()
	set_process_input(true)
	set_process(true)


func _init_pattern() -> void:
	_pattern = []
	for L in SEQ_LANES:
		var lane: Array = []
		for s in SEQ_STEPS: lane.append(-1)
		_pattern.append(lane)


# ── AUDIO ────────────────────────────────────────────────────────
func _init_audio() -> void:
	_gen = AudioStreamGenerator.new()
	_gen.mix_rate = SAMPLE_RATE
	_gen.buffer_length = BUFFER_LEN
	_gen_player = AudioStreamPlayer.new()
	_gen_player.bus = "SFX"
	_gen_player.stream = _gen
	add_child(_gen_player)
	_gen_player.play()
	_playback = _gen_player.get_stream_playback()


func _process(_delta: float) -> void:
	if _playback == null: return
	var frames := _playback.get_frames_available()
	if frames <= 0: return
	for i in frames:
		var l_sample := 0.0
		var r_sample := 0.0
		var remaining: Array = []
		for v_any in _voices:
			var v: Voice = v_any
			if v.done: continue
			v.time += 1.0 / SAMPLE_RATE
			var s := _sample_voice(v)
			l_sample += s
			r_sample += s
			if v.time < v.dur + v.rel:
				remaining.append(v)
		_voices = remaining
		l_sample *= _master_vol
		r_sample *= _master_vol
		# Soft clip
		l_sample = clamp(l_sample, -0.95, 0.95)
		r_sample = clamp(r_sample, -0.95, 0.95)
		_playback.push_frame(Vector2(l_sample, r_sample))

	# Sequencer tick
	if _playing:
		var step_dt = 60.0 / float(_bpm) / 4.0   # 16th notes
		_step_accumulator += 1.0 / 60.0          # _process called ~60Hz
		if _step_accumulator >= step_dt:
			_step_accumulator -= step_dt
			_tick_sequencer()


func _sample_voice(v: Voice) -> float:
	var sample: float = 0.0
	var harmonic_count: int = v.harmonic.size()
	var voice_count: int = max(1, v.voices)
	var arp_step: float = 0.08
	for arp_idx in v.arp.size():
		var arp_start = arp_idx * arp_step
		if v.time < arp_start: continue
		if v.time > arp_start + v.dur + v.rel: continue
		var local_t = v.time - arp_start
		var env := _adsr(local_t, v.atk, v.dec_, v.sus, v.rel, v.dur) * v.velocity
		if env <= 0.0: continue
		for harm in v.harmonic:
			for voice_n in voice_count:
				var det_cents = (float(voice_n) - float(voice_count - 1) * 0.5) * v.detune
				var freq = _midi_to_freq(v.midi + v.arp[arp_idx] + v.transpose) * harm \
							* pow(2.0, det_cents / 1200.0)
				var phase = freq * local_t * TAU
				sample += _waveform(v.timbre, phase, freq, local_t) \
							* env / float(harmonic_count * voice_count)
	return sample * 0.3


func _waveform(timbre: String, phase: float, freq: float, t: float) -> float:
	var s := 0.0
	match timbre:
		"noise_burst":
			s = (randf() * 2.0 - 1.0) * 0.7
		"saw_drive", "saw_decay", "saw_pulse", "saw_distort":
			s = fmod(phase / TAU, 1.0) * 2.0 - 1.0
			if timbre == "saw_drive" or timbre == "saw_distort":
				s = tanh(s * 2.5)
		"pulse_soft", "pulse_arp", "pulse_arp_fast", "pulse_bright":
			s = -1.0 if fmod(phase, TAU) < PI else 1.0
		"tri_chorus", "tri_lonely", "tri_flow", "tri_warble":
			var v = fmod(phase / TAU, 1.0)
			s = abs(v - 0.5) * 4.0 - 1.0
			if timbre == "tri_warble":
				s *= 1.0 + sin(t * TAU * 5.5) * 0.15
		"bell_rich", "bell_balanced", "bell_high", "duet_bell":
			s = sin(phase)
		"organ_stack", "organ_choir":
			s = sin(phase)
		"rich_brass", "rich_pad":
			s = fmod(phase / TAU, 1.0) * 2.0 - 1.0
		"drone_low":
			s = sin(phase)
		_:
			s = sin(phase)
	return s


func _adsr(t: float, atk: float, dec: float, sus: float, rel: float, dur: float) -> float:
	if t < 0.0: return 0.0
	if t < atk:
		return t / atk
	if t < atk + dec:
		var dt = (t - atk) / dec
		return 1.0 - dt * (1.0 - sus)
	if t < dur:
		return sus
	if t < dur + rel:
		return sus * (1.0 - (t - dur) / rel)
	return 0.0


func _midi_to_freq(midi: float) -> float:
	return 440.0 * pow(2.0, (midi - 69.0) / 12.0)


# ── TRIGGER A CARD ────────────────────────────────────────────────
func _trigger_card(idx: int) -> void:
	if idx < 0 or idx >= ARCANA.size(): return
	var entry = ARCANA[idx]
	var timbre: String = entry[4]
	var semi: int = entry[5]
	var scale: Array = SCALES[_scale_key]
	var snapped := _scale_snap(_root_midi + semi, scale)
	var v := Voice.new()
	v.midi = float(snapped)
	v.timbre = timbre
	v.velocity = _master_vol
	# Preset params per timbre (subset of HTML — most important ones)
	var preset = _preset(timbre)
	v.atk = preset.atk; v.dec_ = preset.dec; v.sus = preset.sus
	v.rel = preset.rel; v.dur = preset.dur
	v.detune = preset.detune
	v.filt = preset.filt
	v.voices = preset.get("voices", 1)
	v.harmonic = preset.get("harmonic", [1.0])
	v.arp = preset.get("arp", [0])
	v.transpose = preset.get("transpose", 0)
	_voices.append(v)
	_selected_card = idx

	# Flash card
	if idx < _cards.size():
		var btn: Button = _cards[idx]
		var sb := StyleBoxFlat.new()
		sb.bg_color = C_GOLD_HI
		sb.border_color = C_GOLD_HI
		sb.set_border_width_all(2)
		btn.add_theme_stylebox_override("normal", sb)
		get_tree().create_timer(0.09).timeout.connect(func():
			btn.remove_theme_stylebox_override("normal"))

	_now_playing_label.text = "▶ %02d · %s · %s" % [entry[0], entry[1], timbre]


func _preset(timbre: String) -> Dictionary:
	# condensed ports from HTML
	var presets = {
		"pulse_soft":      {"atk":0.02,"dec":0.15,"sus":0.5,"rel":0.5,"dur":1.0,"detune":8,"filt":1800},
		"pulse_arp":       {"atk":0.005,"dec":0.08,"sus":0.0,"rel":0.2,"dur":0.5,"detune":4,"filt":3000,"arp":[0,7,12]},
		"tri_chorus":      {"atk":0.04,"dec":0.20,"sus":0.6,"rel":0.6,"dur":1.2,"detune":14,"filt":2400,"voices":3},
		"bell_rich":       {"atk":0.002,"dec":0.35,"sus":0.1,"rel":0.9,"dur":1.6,"detune":6,"filt":4800,"harmonic":[1.0,2.0,2.756,5.4]},
		"saw_drive":       {"atk":0.01,"dec":0.12,"sus":0.7,"rel":0.4,"dur":0.9,"detune":11,"filt":2200},
		"organ_stack":     {"atk":0.05,"dec":0.05,"sus":0.85,"rel":0.4,"dur":1.0,"detune":3,"filt":3200,"harmonic":[1.0,2.0,3.0,4.0]},
		"duet_bell":       {"atk":0.003,"dec":0.30,"sus":0.2,"rel":0.7,"dur":1.4,"detune":9,"filt":4200,"harmonic":[1.0,1.5,2.0]},
		"saw_pulse":       {"atk":0.01,"dec":0.10,"sus":0.6,"rel":0.25,"dur":0.6,"detune":7,"filt":2600},
		"rich_brass":      {"atk":0.06,"dec":0.10,"sus":0.8,"rel":0.4,"dur":1.2,"detune":13,"filt":2000,"voices":2},
		"tri_lonely":      {"atk":0.08,"dec":0.10,"sus":0.7,"rel":0.8,"dur":1.4,"detune":0,"filt":1400},
		"pulse_arp_fast":  {"atk":0.003,"dec":0.04,"sus":0.0,"rel":0.1,"dur":0.4,"detune":3,"filt":3400,"arp":[0,4,7,12,16]},
		"bell_balanced":   {"atk":0.002,"dec":0.4,"sus":0.05,"rel":1.0,"dur":1.8,"detune":5,"filt":5200,"harmonic":[1.0,2.0,3.0]},
		"drone_low":       {"atk":0.3,"dec":0.0,"sus":0.95,"rel":1.5,"dur":2.4,"detune":7,"filt":800,"transpose":-12},
		"saw_decay":       {"atk":0.005,"dec":0.6,"sus":0.0,"rel":0.4,"dur":1.2,"detune":17,"filt":1600},
		"tri_flow":        {"atk":0.10,"dec":0.10,"sus":0.7,"rel":0.6,"dur":1.2,"detune":6,"filt":2800,"voices":2},
		"saw_distort":     {"atk":0.005,"dec":0.10,"sus":0.7,"rel":0.4,"dur":0.9,"detune":22,"filt":3000,"voices":2},
		"noise_burst":     {"atk":0.001,"dec":0.20,"sus":0.0,"rel":0.15,"dur":0.5,"detune":0,"filt":1200},
		"bell_high":       {"atk":0.002,"dec":0.20,"sus":0.05,"rel":0.6,"dur":1.2,"detune":4,"filt":6000,"harmonic":[1.0,3.0,5.0]},
		"tri_warble":      {"atk":0.04,"dec":0.10,"sus":0.6,"rel":0.5,"dur":1.0,"detune":18,"filt":1600},
		"pulse_bright":    {"atk":0.005,"dec":0.05,"sus":0.7,"rel":0.3,"dur":0.8,"detune":6,"filt":4800},
		"organ_choir":     {"atk":0.08,"dec":0.05,"sus":0.9,"rel":0.6,"dur":1.4,"detune":10,"filt":2400,"harmonic":[1.0,2.0,3.0],"voices":3},
		"rich_pad":        {"atk":0.15,"dec":0.15,"sus":0.7,"rel":1.2,"dur":2.0,"detune":12,"filt":2200,"voices":3},
	}
	return presets.get(timbre, presets["pulse_soft"])


func _scale_snap(semi: int, scale: Array) -> int:
	var oct: int = int(floor(semi / 12.0))
	var in_oct: int = semi - oct * 12
	var best: int = int(scale[0])
	var best_d: int = 999
	for s in scale:
		var d: int = int(abs(int(s) - in_oct))
		if d < best_d: best_d = d; best = int(s)
	return oct * 12 + best


# ── SEQUENCER ────────────────────────────────────────────────────
func _tick_sequencer() -> void:
	# clear prev cursor
	for L in SEQ_LANES:
		for s in SEQ_STEPS:
			_set_step_cursor(L, s, false)
	for L in SEQ_LANES:
		_set_step_cursor(L, _cur_step, true)
		var idx = _pattern[L][_cur_step]
		if idx >= 0:
			_trigger_card(idx)
	_step_display_label.text = "%02d / %d" % [_cur_step + 1, SEQ_STEPS]
	_cur_step = (_cur_step + 1) % SEQ_STEPS


func _set_step_cursor(L: int, s: int, on: bool) -> void:
	if L >= _steps.size() or s >= _steps[L].size(): return
	var btn: Button = _steps[L][s]
	var is_on = _pattern[L][s] >= 0
	var sb := StyleBoxFlat.new()
	if on:
		sb.bg_color = C_GOLD_HI
	elif is_on:
		sb.bg_color = C_SEPIA
	else:
		sb.bg_color = C_BG
	sb.border_color = C_RULE if not is_on else C_GOLD
	sb.set_border_width_all(1)
	btn.add_theme_stylebox_override("normal", sb)


func _toggle_step(L: int, s: int) -> void:
	if _pattern[L][s] < 0:
		_pattern[L][s] = _selected_card
	else:
		_pattern[L][s] = -1
	_set_step_cursor(L, s, false)


# ── UI BUILD ─────────────────────────────────────────────────────
func _build_ui() -> void:
	# Full-rect dark backdrop
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(bg)

	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 6)
	root.offset_left = 16; root.offset_right = -16
	root.offset_top = 16; root.offset_bottom = -16
	add_child(root)

	# Header
	var header := HBoxContainer.new()
	header.add_theme_constant_override("separation", 16)
	var title := Label.new()
	title.text = "TAROT SYNTH · MAJOR ARCANA"
	title.add_theme_color_override("font_color", C_GOLD_HI)
	title.add_theme_font_size_override("font_size", 18)
	header.add_child(title)
	_now_playing_label = Label.new()
	_now_playing_label.text = "—"
	_now_playing_label.add_theme_color_override("font_color", C_EM_HI)
	_now_playing_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(_now_playing_label)
	var close := Button.new()
	close.text = "X"
	close.add_theme_color_override("font_color", C_GOLD_HI)
	close.pressed.connect(func(): closed.emit())
	header.add_child(close)
	root.add_child(header)

	# Card grid (3 rows × 8 cols = 24, last 2 blank)
	var grid := GridContainer.new()
	grid.columns = 8
	grid.add_theme_constant_override("h_separation", 4)
	grid.add_theme_constant_override("v_separation", 4)
	grid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	for i in 24:
		var b := Button.new()
		if i < ARCANA.size():
			var entry = ARCANA[i]
			b.text = "%02d\n%s\n[%s]" % [entry[0], entry[1],
										OS.get_keycode_string(entry[3])]
			b.add_theme_color_override("font_color", C_GOLD_HI)
			b.add_theme_font_size_override("font_size", 12)
			b.custom_minimum_size = Vector2(0, 80)
			b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			b.size_flags_vertical = Control.SIZE_EXPAND_FILL
			var card_idx := i
			b.pressed.connect(func(): _trigger_card(card_idx))
			# try to load art
			var art_path: String = entry[2]
			if art_path != "" and ResourceLoader.exists(art_path):
				var tex: Texture2D = load(art_path)
				if tex:
					var rect := TextureRect.new()
					rect.texture = tex
					rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
					rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
					rect.modulate = Color(1, 1, 1, 0.55)
					rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
					rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
					b.add_child(rect)
			_cards.append(b)
		else:
			b.text = "—"
			b.add_theme_color_override("font_color", C_TEXT_DIM)
			b.disabled = true
			_cards.append(null)
		grid.add_child(b)
	root.add_child(grid)

	# Sequencer
	var seq_box := HBoxContainer.new()
	seq_box.add_theme_constant_override("separation", 4)
	var lane_labels := VBoxContainer.new()
	lane_labels.add_theme_constant_override("separation", 2)
	for L in SEQ_LANES:
		var ll := Label.new()
		ll.text = "LANE %d" % (L + 1)
		ll.custom_minimum_size = Vector2(80, 0)
		ll.size_flags_vertical = Control.SIZE_EXPAND_FILL
		ll.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		ll.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		ll.add_theme_color_override("font_color", C_TEXT_DIM)
		ll.add_theme_font_size_override("font_size", 12)
		var sb := StyleBoxFlat.new()
		sb.bg_color = C_INK
		sb.border_color = C_RULE
		sb.set_border_width_all(1)
		ll.add_theme_stylebox_override("normal", sb)
		lane_labels.add_child(ll)
	seq_box.add_child(lane_labels)
	var lanes_box := VBoxContainer.new()
	lanes_box.add_theme_constant_override("separation", 2)
	lanes_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for L in SEQ_LANES:
		var lane_row := HBoxContainer.new()
		lane_row.add_theme_constant_override("separation", 2)
		lane_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var lane_steps: Array = []
		for s in SEQ_STEPS:
			var sb := Button.new()
			sb.custom_minimum_size = Vector2(0, 24)
			sb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			sb.text = ""
			var L_idx := L
			var s_idx := s
			sb.pressed.connect(func(): _toggle_step(L_idx, s_idx))
			lane_row.add_child(sb)
			lane_steps.append(sb)
			_set_step_cursor(L, s, false)
		lanes_box.add_child(lane_row)
		_steps.append(lane_steps)
	seq_box.add_child(lanes_box)
	root.add_child(seq_box)

	# Transport
	var transport := HBoxContainer.new()
	transport.add_theme_constant_override("separation", 8)
	var play_btn := Button.new()
	play_btn.text = "▶ PLAY"
	play_btn.add_theme_color_override("font_color", C_GOLD_HI)
	play_btn.pressed.connect(func():
		if _playing: _stop_loop()
		else: _start_loop())
	transport.add_child(play_btn)
	var stop_btn := Button.new()
	stop_btn.text = "■ STOP"
	stop_btn.add_theme_color_override("font_color", C_GOLD_HI)
	stop_btn.pressed.connect(_stop_loop)
	transport.add_child(stop_btn)
	var clear_btn := Button.new()
	clear_btn.text = "⌫ CLEAR"
	clear_btn.add_theme_color_override("font_color", C_GOLD_HI)
	clear_btn.pressed.connect(_clear_pattern)
	transport.add_child(clear_btn)

	var bpm_lbl := Label.new(); bpm_lbl.text = "BPM"
	bpm_lbl.add_theme_color_override("font_color", C_TEXT_DIM)
	transport.add_child(bpm_lbl)
	var bpm_slider := HSlider.new()
	bpm_slider.min_value = 40; bpm_slider.max_value = 200
	bpm_slider.value = _bpm
	bpm_slider.custom_minimum_size = Vector2(120, 0)
	bpm_slider.value_changed.connect(func(v):
		_bpm = int(v)
		_bpm_label.text = str(_bpm))
	transport.add_child(bpm_slider)
	_bpm_label = Label.new(); _bpm_label.text = str(_bpm)
	_bpm_label.add_theme_color_override("font_color", C_GOLD_HI)
	transport.add_child(_bpm_label)

	var scale_lbl := Label.new(); scale_lbl.text = "SCALE"
	scale_lbl.add_theme_color_override("font_color", C_TEXT_DIM)
	transport.add_child(scale_lbl)
	var scale_opt := OptionButton.new()
	for k in SCALES.keys(): scale_opt.add_item(k)
	scale_opt.item_selected.connect(func(i):
		_scale_key = SCALES.keys()[i])
	transport.add_child(scale_opt)

	var vol_lbl := Label.new(); vol_lbl.text = "VOL"
	vol_lbl.add_theme_color_override("font_color", C_TEXT_DIM)
	transport.add_child(vol_lbl)
	var vol_slider := HSlider.new()
	vol_slider.min_value = 0; vol_slider.max_value = 100
	vol_slider.value = int(_master_vol * 100)
	vol_slider.custom_minimum_size = Vector2(100, 0)
	vol_slider.value_changed.connect(func(v):
		_master_vol = float(v) / 100.0)
	transport.add_child(vol_slider)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	transport.add_child(spacer)

	_step_display_label = Label.new()
	_step_display_label.text = "— / 16"
	_step_display_label.add_theme_color_override("font_color", C_GOLD_HI)
	transport.add_child(_step_display_label)

	root.add_child(transport)


func _start_loop() -> void:
	_playing = true
	_cur_step = 0
	_step_accumulator = 0.0

func _stop_loop() -> void:
	_playing = false
	_cur_step = 0
	for L in SEQ_LANES:
		for s in SEQ_STEPS:
			_set_step_cursor(L, s, false)
	_step_display_label.text = "— / 16"

func _clear_pattern() -> void:
	for L in SEQ_LANES:
		for s in SEQ_STEPS:
			_pattern[L][s] = -1
			_set_step_cursor(L, s, false)


# ── INPUT ────────────────────────────────────────────────────────
func _input(event: InputEvent) -> void:
	if not visible: return
	if event is InputEventKey and event.pressed and not event.echo:
		var k = event.keycode
		if k == KEY_SPACE:
			if _playing: _stop_loop()
			else: _start_loop()
			get_viewport().set_input_as_handled()
			return
		if k == KEY_ESCAPE:
			closed.emit()
			get_viewport().set_input_as_handled()
			return
		for i in ARCANA.size():
			if ARCANA[i][3] == k:
				_trigger_card(i)
				get_viewport().set_input_as_handled()
				return


# Public API
func open() -> void:
	visible = true

func close() -> void:
	visible = false
