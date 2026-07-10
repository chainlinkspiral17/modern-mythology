extends Control
## BASILICA OF WIRES · the descent · first-person wireframe crawl.
##
## Black field, cyan structure lines, white for near geometry, and
## one reserved color — signal amber — for anything energized.
## The wireframe is a CHOICE: the mountain is one instrument, and
## you read an instrument from its diagram.
##
## THE TUNER IS THE VERB.  Q/E coarse (±25 Hz) · A/D fine (±5 Hz).
## Rooms and doors EXIST per band — a corridor at one frequency is
## a wall at another.  Standing-wave zones beat against your
## carried tune and shred COHERENCE — your sense of where you are.
## Coherence at zero: you wake at the last junction with the map
## violet.  No death.  Worse: unreliability.
##
## At exactly 220 Hz — and only there — the corridors hold still,
## the map repairs, and the violet drains out.  The game never
## says why.
##
## Controls: ↑ forward · ↓ back · ←/→ turn · TAB map · ESC out.
## The hum is live: two sine voices (the room's fundamental and
## your tune) beating against each other for real.

signal quit
signal descent_over(state: Dictionary)

const LEVELS_PATH := "res://resources/games/vol7/basilica_of_wires/levels.json"
const PROPS_PATH  := "res://resources/games/vol7/basilica_of_wires/props.json"

const C_DARK   := Color("000000")
const C_CYAN   := Color("38c8d8")
const C_WHITE  := Color("e8f4f8")
const C_AMBER  := Color("e8a830")
const C_VIOLET := Color("7a3868")

const BAND_TOL := 15.0
const SAFE_FREQ := 220.0
const SAFE_TOL := 2.0
const FREQ_MIN := 180.0
const FREQ_MAX := 520.0

# View geometry · three depths of trapezoid corridor
const VP := Rect2(240, 60, 800, 500)
const DEPTH_X := [0.0, 0.18, 0.32, 0.42]     # inset fractions per depth
const DEPTH_Y := [0.0, 0.22, 0.38, 0.48]

var _data: Dictionary = {}
var _props: Dictionary = {}
var _state: Dictionary = {}
var _level_i: int = 0                # 0-based
var _grid: Array = []                # array of row strings
var _px: int = 1
var _py: int = 1
var _dir: int = 1                    # 0 N · 1 E · 2 S · 3 W
var _freq: float = 440.0
var _coherence: float = 9.0
var _visited: Dictionary = {}        # "lvl:x:y" → true
var _scrambled: bool = false
var _last_junction: Vector2i = Vector2i(1, 1)
var _map_open: bool = false
var _msg: String = ""
var _message_room_reached: bool = false
var _echo_pending: float = -1.0

# The live hum
var _hum_player: AudioStreamPlayer = null
var _hum_playback: AudioStreamGeneratorPlayback = null
var _ph_room := 0.0
var _ph_tune := 0.0
var _ph_echo := 0.0
var _echo_t := -1.0
var _echo_freq := 0.0

const DIRS := [Vector2i(0, -1), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0)]


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_load_data()
	_hum_player = AudioStreamPlayer.new()
	_hum_player.bus = "Master"
	var gen := AudioStreamGenerator.new()
	gen.mix_rate = 44100.0
	gen.buffer_length = 0.1
	_hum_player.stream = gen
	_hum_player.volume_db = -14.0
	add_child(_hum_player)
	_hum_player.play()
	_hum_playback = _hum_player.get_stream_playback()
	set_process(true)


func boot(state: Dictionary) -> void:
	_state = state
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_bgm"):
		am.stop_bgm()   # the hum is the score
	_level_i = clampi(int(_state.get("level_i", 0)), 0, 8)
	_freq = float(_state.get("freq", 440.0))
	_coherence = float(_state.get("coherence", 9.0))
	_message_room_reached = bool(_state.get("message_room_reached", false))
	_enter_level(_level_i, true)


func _load_data() -> void:
	for pair in [[LEVELS_PATH, "l"], [PROPS_PATH, "p"]]:
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		if f == null: continue
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "l": _data = parsed
			else: _props = (parsed as Dictionary).get("props", {})


func _level() -> Dictionary:
	return (_data.get("levels", []))[_level_i]


func _enter_level(i: int, from_above: bool) -> void:
	_level_i = i
	_grid = _level().get("grid", [])
	# find entry: '@' on level 1, else 'U' (from above) or 'S' (from below)
	var want := "@" if i == 0 and from_above else ("U" if from_above else "S")
	for y in range(_grid.size()):
		var row := String(_grid[y])
		var x := row.find(want)
		if x >= 0:
			_px = x
			_py = y
			break
	_dir = 1
	_set_msg("LEVEL %d · %s · fundamental %d Hz" % [i + 1, String(_level().get("name", "")).to_upper(),
			int(_level().get("fundamental", 0))])
	_mark_visited()
	queue_redraw()


func _cell(x: int, y: int) -> String:
	if y < 0 or y >= _grid.size(): return "#"
	var row := String(_grid[y])
	if x < 0 or x >= row.length(): return "#"
	return row[x]


func _passable(c: String) -> bool:
	if c == "#": return false
	if c == "B":
		return absf(_freq - float(_level().get("fundamental", 400))) <= BAND_TOL
	if c == "M":
		return absf(_freq - SAFE_FREQ) <= SAFE_TOL
	return true


func _mark_visited() -> void:
	_visited["%d:%d:%d" % [_level_i, _px, _py]] = true
	# track junctions · a cell with 3+ open neighbors
	var open := 0
	for d in DIRS:
		if _passable(_cell(_px + d.x, _py + d.y)):
			open += 1
	if open >= 3:
		_last_junction = Vector2i(_px, _py)


# ─── Movement + the tuner ────────────────────────────────────────

func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if not (event is InputEventKey) or not event.pressed:
		return
	var kev: InputEventKey = event
	match kev.keycode:
		KEY_ESCAPE:
			if _map_open:
				_map_open = false
				queue_redraw()
			else:
				quit.emit()
			get_viewport().set_input_as_handled()
			return
		KEY_TAB:
			if not kev.echo:
				_map_open = not _map_open
				queue_redraw()
			return
	if kev.echo and kev.keycode in [KEY_UP, KEY_DOWN]:
		return
	match kev.keycode:
		KEY_LEFT:  _dir = (_dir + 3) % 4
		KEY_RIGHT: _dir = (_dir + 1) % 4
		KEY_UP:    _step(1)
		KEY_DOWN:  _step(-1)
		KEY_Q: _tune(-25.0)
		KEY_E: _tune(25.0)
		KEY_A: _tune(-5.0)
		KEY_D: _tune(5.0)
	queue_redraw()


func _tune(delta: float) -> void:
	_freq = clampf(_freq + delta, FREQ_MIN, FREQ_MAX)
	if absf(_freq - SAFE_FREQ) <= SAFE_TOL:
		if _scrambled:
			_scrambled = false
			_set_msg("the corridors hold still. the violet drains out of the map.")
		_coherence = minf(9.0, _coherence + 0.5)
	# the flooded cavity · the tune comes back wrong
	if _cell(_px, _py) == "4" or _near_landmark("4"):
		_echo_t = 0.0
		_echo_freq = _freq * 1.5


func _near_landmark(mark: String) -> bool:
	for d in DIRS:
		if _cell(_px + d.x, _py + d.y) == mark:
			return true
	return false


func _step(sign: int) -> void:
	var d: Vector2i = DIRS[_dir] * sign
	var nx := _px + d.x
	var ny := _py + d.y
	var c := _cell(nx, ny)
	if not _passable(c):
		if c == "B":
			_set_msg("a wall · at this frequency. (fundamental %d Hz)" % int(_level().get("fundamental", 0)))
		elif c == "M":
			_set_msg("a door with no handle. it is listening for an agreement.")
		return
	_px = nx
	_py = ny
	_mark_visited()
	_after_step(c)


func _after_step(c: String) -> void:
	var at_safe := absf(_freq - SAFE_FREQ) <= SAFE_TOL
	if c == "H":
		if at_safe:
			_set_msg("the standing wave parts around 220. you walk the null line.")
		else:
			_coherence -= 1.5
			_set_msg("interference. your tune beats against the room's. the map crawls at the edges.")
			if _coherence <= 3.0:
				_scrambled = true
			if _coherence <= 0.0:
				_wake_at_junction()
				return
	elif at_safe:
		_coherence = minf(9.0, _coherence + 0.34)
	match c:
		"S":
			if _level_i < 8:
				_enter_level(_level_i + 1, true)
				return
		"U":
			if _level_i > 0:
				_enter_level(_level_i - 1, false)
				return
			_exit_mountain()
			return
		"@":
			# The adit · stepping back onto it is the climb out.
			_exit_mountain()
			return
		"M":
			_reach_message_room()
			return
		"2", "3", "4", "5":
			var lm: Dictionary = _data.get("landmarks", {}).get(c, {})
			_set_msg(String(lm.get("name", "")) + " · " + String(lm.get("line", "")))
			if c == "4":
				_echo_t = 0.0
				_echo_freq = _freq * 1.5


func _wake_at_junction() -> void:
	_px = _last_junction.x
	_py = _last_junction.y
	_coherence = 3.0
	_scrambled = true
	_set_msg("— you wake at the last junction you trusted. the map is violet. no time seems to have passed, which is not the same as none passing.")


func _reach_message_room() -> void:
	_message_room_reached = true
	_state["message_room_reached"] = true
	OneironauticsTokens.add("basilica_message_room_reached")
	_map_open = false
	queue_redraw()
	_show_teletype()


func _show_teletype() -> void:
	var page: Dictionary = _data.get("message_room_page", {})
	var overlay := Panel.new()
	overlay.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	overlay.offset_left = -430
	overlay.offset_right = 430
	overlay.offset_top = -310
	overlay.offset_bottom = 310
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0.98)
	sb.border_color = C_AMBER
	sb.set_border_width_all(1)
	overlay.add_theme_stylebox_override("panel", sb)
	add_child(overlay)

	var col := VBoxContainer.new()
	col.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	col.offset_left = 24
	col.offset_right = -24
	col.offset_top = 18
	col.offset_bottom = -18
	col.add_theme_constant_override("separation", 10)
	overlay.add_child(col)

	var lines: Array = [String(page.get("header", "")), String(page.get("addressed", ""))]
	for a in page.get("annotations", []):
		lines.append(String(a))
	if OneironauticsTokens.has("earthman_correction_ending_seen"):
		lines.append(String(page.get("final_annotation_read", "")))
	else:
		lines.append(String(page.get("final_annotation_unread", "")))
	for line in lines:
		var l := Label.new()
		l.text = String(line)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.add_theme_font_size_override("font_size", 14)
		l.add_theme_color_override("font_color", C_AMBER)
		col.add_child(l)

	var b := Button.new()
	b.text = "  · begin the climb out ·  "
	b.flat = true
	b.add_theme_font_size_override("font_size", 14)
	b.add_theme_color_override("font_color", C_WHITE)
	b.pressed.connect(func() -> void:
		overlay.queue_free()
		_set_msg("nine levels of instrument between you and the daylight. it knows you now."))
	col.add_child(b)


func _exit_mountain() -> void:
	_state["coherence"] = _coherence
	_state["freq"] = _freq
	descent_over.emit(_state)


func _set_msg(t: String) -> void:
	_msg = t


# ─── The live hum · two sines beating for real ───────────────────

func _process(_delta: float) -> void:
	if _hum_playback == null:
		return
	var frames: int = _hum_playback.get_frames_available()
	if frames <= 0:
		return
	var fund := float(_level().get("fundamental", 400)) if not _data.is_empty() and not _grid.is_empty() else 400.0
	var dt := 1.0 / 44100.0
	var buf := PackedVector2Array()
	buf.resize(frames)
	var echo_active := _echo_t >= 3.0 and _echo_t <= 5.0
	for i in range(frames):
		var s := sin(_ph_room * TAU) * 0.30 + sin(_ph_tune * TAU) * 0.22
		if echo_active:
			s += sin(_ph_echo * TAU) * 0.12
		_ph_room = fposmod(_ph_room + fund * dt, 1.0)
		_ph_tune = fposmod(_ph_tune + _freq * dt, 1.0)
		_ph_echo = fposmod(_ph_echo + _echo_freq * dt, 1.0)
		buf[i] = Vector2(s, s)
	_hum_playback.push_buffer(buf)
	if _echo_t >= 0.0:
		_echo_t += float(frames) * dt
		if _echo_t > 5.0:
			_echo_t = -1.0


# ─── The wireframe ───────────────────────────────────────────────

func _depth_rect(d: int) -> Rect2:
	var fx: float = DEPTH_X[d]
	var fy: float = DEPTH_Y[d]
	return Rect2(VP.position.x + VP.size.x * fx, VP.position.y + VP.size.y * fy,
			VP.size.x * (1.0 - 2.0 * fx), VP.size.y * (1.0 - 2.0 * fy))


func _draw() -> void:
	draw_rect(Rect2(0, 0, 1280, 720), C_DARK)
	if _grid.is_empty():
		return
	var font := get_theme_default_font()

	if _map_open:
		_draw_map(font)
	else:
		_draw_view()

	# The tuner · the entire HUD
	var at_safe := absf(_freq - SAFE_FREQ) <= SAFE_TOL
	draw_string(font, Vector2(70, 660), "TUNE  %d Hz" % int(_freq),
			HORIZONTAL_ALIGNMENT_LEFT, -1, 20, C_AMBER if at_safe else C_WHITE)
	draw_string(font, Vector2(70, 686), "Q/E coarse · A/D fine · TAB map",
			HORIZONTAL_ALIGNMENT_LEFT, -1, 12, C_CYAN)
	# coherence as a fraying line, not a number
	var coh_w := 240.0 * (_coherence / 9.0)
	draw_line(Vector2(900, 664), Vector2(900 + coh_w, 664), C_CYAN if _coherence > 3.0 else C_VIOLET, 2.0)
	if _coherence <= 3.0:
		for i in range(4):
			draw_line(Vector2(900 + coh_w + 8 + i * 12, 660 + (i % 2) * 8),
					Vector2(900 + coh_w + 14 + i * 12, 664), C_VIOLET, 1.0)
	if _msg != "":
		draw_string(font, Vector2(70, 40), _msg, HORIZONTAL_ALIGNMENT_LEFT, 1140, 14, C_CYAN)


func _draw_view() -> void:
	var fwd: Vector2i = DIRS[_dir]
	var right: Vector2i = DIRS[(_dir + 1) % 4]
	for d in range(3):
		var cx := _px + fwd.x * d
		var cy := _py + fwd.y * d
		var near := _depth_rect(d)
		var far := _depth_rect(d + 1)
		var col := C_WHITE if d == 0 else C_CYAN
		# left wall
		var lcell := _cell(cx - right.x, cy - right.y)
		if not _passable(lcell):
			var wall_col := _wall_color(lcell, col)
			draw_line(near.position, far.position, wall_col, 2.0)
			draw_line(Vector2(near.position.x, near.end.y), Vector2(far.position.x, far.end.y), wall_col, 2.0)
			draw_line(near.position, Vector2(near.position.x, near.end.y), wall_col, 2.0)
		else:
			draw_line(Vector2(far.position.x, near.position.y), far.position, C_CYAN, 1.0)
			draw_line(Vector2(far.position.x, near.end.y), Vector2(far.position.x, far.end.y), C_CYAN, 1.0)
		# right wall
		var rcell := _cell(cx + right.x, cy + right.y)
		if not _passable(rcell):
			var wall_col2 := _wall_color(rcell, col)
			draw_line(Vector2(near.end.x, near.position.y), Vector2(far.end.x, far.position.y), wall_col2, 2.0)
			draw_line(near.end, far.end, wall_col2, 2.0)
			draw_line(Vector2(near.end.x, near.position.y), near.end, wall_col2, 2.0)
		else:
			draw_line(Vector2(far.end.x, near.position.y), Vector2(far.end.x, far.position.y), C_CYAN, 1.0)
			draw_line(Vector2(far.end.x, near.end.y), far.end, C_CYAN, 1.0)
		# front wall / prop
		var fcell := _cell(cx + fwd.x, cy + fwd.y)
		if not _passable(fcell):
			var fcol := _wall_color(fcell, col)
			draw_rect(far, fcol, false, 2.0)
			if _props.has(fcell):
				_draw_prop(String(fcell), far)
			if fcell == "M":
				_draw_prop("M", far)
			break
		elif _props.has(fcell) and d == 0:
			pass   # landmark cell is open · its line prints on entry
	# floor line
	var base := _depth_rect(0)
	draw_line(Vector2(base.position.x, base.end.y), Vector2(base.end.x, base.end.y), C_CYAN, 1.0)


func _wall_color(c: String, base: Color) -> Color:
	if c == "B" or c == "M":
		return C_AMBER   # energized · exists per band
	return base


func _draw_prop(key: String, plane: Rect2) -> void:
	var prop: Dictionary = _props.get(key, {})
	var cols := [C_CYAN, C_WHITE, C_AMBER]
	for ln in prop.get("lines", []):
		var l: Array = ln
		var a := Vector2(plane.position.x + plane.size.x * float(l[0]),
				plane.position.y + plane.size.y * float(l[1]))
		var b := Vector2(plane.position.x + plane.size.x * float(l[2]),
				plane.position.y + plane.size.y * float(l[3]))
		draw_line(a, b, cols[clampi(int(l[4]), 0, 2)], 1.5)


func _draw_map(font: Font) -> void:
	draw_string(font, Vector2(440, 90), "AUTOMAP · LEVEL %d%s" % [_level_i + 1,
			" · CORRUPTED" if _scrambled else ""],
			HORIZONTAL_ALIGNMENT_LEFT, -1, 16, C_VIOLET if _scrambled else C_CYAN)
	var cell := 36.0
	var ox := 640.0 - (13.0 * cell) / 2.0
	var oy := 140.0
	for y in range(_grid.size()):
		for x in range(String(_grid[y]).length()):
			if not _visited.has("%d:%d:%d" % [_level_i, x, y]):
				continue
			var pos := Vector2(ox + x * cell, oy + y * cell)
			if _scrambled:
				# corridors you walked render displaced, in violet
				var h := (x * 7 + y * 13 + _level_i * 5) % 5
				pos += Vector2(float(h - 2) * 6.0, float((h * 3) % 5 - 2) * 6.0)
				draw_rect(Rect2(pos, Vector2(cell - 6, cell - 6)), C_VIOLET, false, 1.5)
			else:
				draw_rect(Rect2(pos, Vector2(cell - 6, cell - 6)), C_CYAN, false, 1.5)
			if x == _px and y == _py:
				draw_circle(pos + Vector2(cell / 2 - 3, cell / 2 - 3), 4.0, C_AMBER)
	draw_string(font, Vector2(440, 560), "the map is the health bar.",
			HORIZONTAL_ALIGNMENT_LEFT, -1, 12, C_CYAN)


func _exit_tree() -> void:
	if _hum_player != null:
		_hum_player.stop()
