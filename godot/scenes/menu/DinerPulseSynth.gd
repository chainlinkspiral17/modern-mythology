extends Control
## DinerPulseSynth — modular interactive toy Control.
##
## Sits inside the MusicPlayerOverlay's reserved 64px visualizer host
## (or anywhere else a Control fits). 8 horizontal cells; clicking a
## cell triggers a short sine-tone pulse and lights the cell up. When
## idle the cells breathe with offset LFO phases so the panel feels
## alive even with no input.
##
## Synthesizes tones on the fly by writing 16-bit PCM into an
## AudioStreamWAV per press — no source assets required. Tones share
## one AudioStreamPlayer so triggering a new cell cuts the previous
## (intentional, gives the toy a clean stab quality).

const CELL_COUNT  := 8
const TONE_DUR    := 0.55       # seconds per pulse
const SAMPLE_RATE := 22050.0
const ROOT_MIDI   := 57         # A3 — under most BGM, doesn't fight
const SCALE_SEMIS := [0, 2, 3, 5, 7, 8, 10, 12]   # natural minor + oct

var accent: Color = Color(0.78, 0.66, 0.29)
var dim:    Color = Color(0.45, 0.43, 0.36, 0.6)
var bg:     Color = Color(0.024, 0.020, 0.014, 0.97)

var _cell_rects: Array[Rect2] = []
var _cell_flash: PackedFloat32Array = PackedFloat32Array()   # 0..1 decay per cell
var _phase:      float = 0.0
var _player:     AudioStreamPlayer = null


func _ready() -> void:
	_cell_flash.resize(CELL_COUNT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_player = AudioStreamPlayer.new()
	_player.bus = "SFX"
	add_child(_player)
	resized.connect(_layout_cells)
	_layout_cells()
	set_process(true)
	# Watch for joypad input so Riffmaster (or any HID gamepad)
	# triggers cells. Buttons 0..7 → cells 0..7. Anything past 7 is
	# ignored. _unhandled_input catches buttons even when the overlay
	# doesn't have keyboard focus.
	set_process_unhandled_input(true)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventJoypadButton:
		var jb: InputEventJoypadButton = event
		if jb.pressed and jb.button_index >= 0 and jb.button_index < CELL_COUNT:
			_trigger_cell(jb.button_index)
			get_viewport().set_input_as_handled()


# ── Public API ───────────────────────────────────────────────────────
func set_colors(p_accent: Color, p_dim: Color, p_bg: Color) -> void:
	accent = p_accent
	dim    = p_dim
	bg     = p_bg
	queue_redraw()


# ── Layout ───────────────────────────────────────────────────────────
func _layout_cells() -> void:
	_cell_rects.clear()
	var s: Vector2 = size
	if s.x <= 0 or s.y <= 0:
		return
	var gap: float = 4.0
	var w: float = (s.x - gap * float(CELL_COUNT - 1)) / float(CELL_COUNT)
	for i in CELL_COUNT:
		_cell_rects.append(Rect2(float(i) * (w + gap), 0.0, w, s.y))
	queue_redraw()


# ── Input ────────────────────────────────────────────────────────────
func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb: InputEventMouseButton = event
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			var idx: int = _cell_at(mb.position)
			if idx >= 0:
				_trigger_cell(idx)


func _cell_at(p: Vector2) -> int:
	for i in _cell_rects.size():
		if _cell_rects[i].has_point(p):
			return i
	return -1


# ── Trigger ──────────────────────────────────────────────────────────
func _trigger_cell(idx: int) -> void:
	if idx < 0 or idx >= CELL_COUNT:
		return
	_cell_flash[idx] = 1.0
	queue_redraw()
	var midi: int = ROOT_MIDI + int(SCALE_SEMIS[idx])
	var freq: float = 440.0 * pow(2.0, float(midi - 69) / 12.0)
	_player.stream = _make_tone_stream(freq, TONE_DUR)
	_player.play()


func _make_tone_stream(freq: float, dur: float) -> AudioStreamWAV:
	var n: int = int(SAMPLE_RATE * dur)
	var data := PackedByteArray()
	data.resize(n * 2)
	# Triangle-shaped envelope feels softer than exponential here —
	# quick attack, gentle decay, clean tail so successive presses
	# don't overlap into noise.
	for i in n:
		var t: float = float(i) / SAMPLE_RATE
		var env: float
		if t < 0.02:
			env = t / 0.02
		else:
			env = maxf(0.0, 1.0 - (t - 0.02) / (dur - 0.02))
		# Soft bell — sine + slight 3rd harmonic so it reads as a
		# real instrument, not a beeper.
		var s: float = (sin(t * freq * TAU) * 0.75
					+ sin(t * freq * 3.0 * TAU) * 0.18) * env * 0.62
		var v: int = int(clampf(s, -1.0, 1.0) * 32700.0)
		data[i * 2]     = v & 0xff
		data[i * 2 + 1] = (v >> 8) & 0xff
	var wav := AudioStreamWAV.new()
	wav.format    = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate  = int(SAMPLE_RATE)
	wav.data      = data
	return wav


# ── Idle animation + draw ────────────────────────────────────────────
func _process(dt: float) -> void:
	_phase += dt
	# Decay flash values toward 0 so the cell lights fade after press.
	var dirty: bool = false
	for i in CELL_COUNT:
		if _cell_flash[i] > 0.0:
			_cell_flash[i] = maxf(0.0, _cell_flash[i] - dt * 2.5)
			dirty = true
	# Always redraw — the idle LFO breath is animated.
	queue_redraw()


func _draw() -> void:
	if _cell_rects.is_empty():
		return
	for i in CELL_COUNT:
		var r: Rect2 = _cell_rects[i]
		# Idle pulse — offset LFOs so the row reads as a quiet row
		# of diner counter lamps. Slow rate, low amplitude.
		var idle_phase: float = _phase * 0.7 + float(i) * 0.4
		var idle: float = 0.18 + 0.10 * (0.5 + 0.5 * sin(idle_phase))
		var flash: float = _cell_flash[i]
		var fill_alpha: float = clampf(idle + flash * 0.75, 0.0, 1.0)
		# Backing
		draw_rect(r, Color(dim.r, dim.g, dim.b, 0.18), true)
		# Active fill — vertical bar that rises with the pulse.
		var fill_h: float = r.size.y * (0.25 + 0.50 * (idle + flash))
		var fill_y: float = r.position.y + r.size.y - fill_h
		var fill_rect := Rect2(r.position.x, fill_y, r.size.x, fill_h)
		var col: Color = Color(accent.r, accent.g, accent.b, fill_alpha)
		draw_rect(fill_rect, col, true)
		# Border — brighter when flashing.
		var border_alpha: float = 0.35 + 0.55 * flash
		draw_rect(r, Color(accent.r, accent.g, accent.b, border_alpha), false, 1.0)
		# Cell label — tiny scale degree number.
		var ft := ThemeDB.fallback_font
		if ft != null:
			var n: int = int(SCALE_SEMIS[i])
			var label: String = str(i + 1)
			var lab_col := Color(accent.r, accent.g, accent.b, 0.55 + 0.35 * flash)
			draw_string(ft, Vector2(r.position.x + 4, r.position.y + 12),
				label, HORIZONTAL_ALIGNMENT_LEFT, -1, 9, lab_col)
