extends Control
## ESTUARY (1) · the whole game · one fixed screen, twelve weeks.
##
## The estuary seen from the tide gate, slightly elevated, looking
## seaward.  No scrolling, no cuts, no second location.  The LEVER
## is diegetic — drawn on the gate housing at frame-left.  The week
## number is carved into the gate post.  That is the entire HUD.
##
## The heron is the readout: where she stands each week is the
## state of the estuary, rendered as behavior, never as number.
##
## Ines Rocha's coupled math (2001, her first job):
##   · FRY out-migrate in weeks 4–6 · passage = openness × tide luck.
##     Miss the window and the cohort is stranded for the game.
##   · SHRIMP score stability · every gate CHANGE costs bed density;
##     identical weeks regrow it.  The optimal shrimp summer touches
##     the lever twice.
##   · HERON eats whichever is abundant · max(fry, shrimp) rendered
##     as a standing position.  She never starves.  She just isn't
##     there one week.  That lands harder.
##
## Ostrom's score: a drone in D that gains a voice per species
## doing well.  The player mixes the soundtrack with the lever and
## is never told so.  AudioMgr is single-track, so the 8 stem
## combinations are pre-rendered (mix_d[f][s][h].wav).

signal quit
signal week_complete(state: Dictionary)
signal season_over(state: Dictionary, grades: Dictionary)

const SPRITE_DIR := "res://resources/games/vol7/estuary_1/sprites/"

# The six colors · total · everywhere
const C_WATER   := Color("2a3038")   # channel water (deep)
const C_FLAT    := Color("6a7a72")   # mudflat (exposed)
const C_SKY     := Color("a8b4a0")   # sky (always overcast)
const C_REED    := Color("4a5a3a")   # reed line
const C_HERON   := Color("b8c0c0")   # the heron
const C_GOLD    := Color("d8b048")   # tide-gold · earned

const OPENNESS := {"open": 1.0, "half": 0.5, "closed": 0.0}

# Screen bands (1280×720 · thirds: sky, water/flat, reed line)
const SKY_BOTTOM := 240
const FLAT_BOTTOM := 540
const REED_TOP := 540
const REED_BOTTOM := 620
const BANK_TOP := 620

var _state: Dictionary = {}
var _heron := SlowstockSprite.new()
var _heron_stance: String = "upright"   # upright · feeding · hunched · flight · absent
var _week_events: Dictionary = {}       # what happened when the week turned
var _notebook: Label = null
var _wait_btn: Button = null
var _lever_rects: Dictionary = {}       # "open"/"half"/"closed" → Rect2
var _season_done: bool = false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

	_notebook = Label.new()
	_notebook.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_notebook.offset_top = -76
	_notebook.offset_bottom = -24
	_notebook.offset_left = 40
	_notebook.offset_right = -260
	_notebook.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_notebook.add_theme_font_size_override("font_size", 16)
	_notebook.add_theme_color_override("font_color", C_HERON)
	add_child(_notebook)

	_wait_btn = Button.new()
	_wait_btn.text = "  · let the week pass ·  "
	_wait_btn.flat = true
	_wait_btn.add_theme_font_size_override("font_size", 14)
	_wait_btn.add_theme_color_override("font_color", C_FLAT)
	_wait_btn.add_theme_color_override("font_hover_color", C_GOLD)
	_wait_btn.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_wait_btn.position = Vector2(1040, 660)
	_wait_btn.pressed.connect(_advance_week)
	add_child(_wait_btn)

	# Lever click zones on the gate housing (drawn in _draw)
	_lever_rects = {
		"open":   Rect2(96, 336, 96, 40),
		"half":   Rect2(96, 380, 96, 40),
		"closed": Rect2(96, 424, 96, 40),
	}


func boot(state: Dictionary) -> void:
	_state = state
	if not _state.has("luck"):
		# Tide luck per week · rolled once per season and saved, so
		# a continued save replays the same weather.
		var luck: Array = []
		for i in range(12):
			luck.append(0.55 + randf() * 0.45)
		_state["luck"] = luck
	_recompute_presentation()
	_play_week_bgm()
	_set_notebook(_arrival_line())
	queue_redraw()


# ─── Weekly turn ─────────────────────────────────────────────────

func _advance_week() -> void:
	if _season_done:
		return
	var week: int = int(_state.get("week", 1))
	var gate: String = String(_state.get("gate", "closed"))
	var last_gate: String = String(_state.get("last_gate", gate))
	var openness: float = float(OPENNESS.get(gate, 0.0))
	var luck: float = float(_state["luck"][week - 1])
	var ev: Dictionary = {"week": week, "gate": gate}

	# FRY · out-migration window · weeks 4–6
	var fry_remaining: float = float(_state.get("fry_remaining", 9.0))
	var fry_out: float = float(_state.get("fry_out", 0.0))
	var passage: float = 0.0
	if week >= 4 and week <= 6:
		passage = fry_remaining * openness * luck * 0.8
		fry_remaining -= passage
		fry_out += passage
		ev["passage"] = passage
	if week == 6 and fry_remaining > 2.0:
		ev["stranded"] = true
	_state["fry_remaining"] = fry_remaining
	_state["fry_out"] = fry_out

	# SHRIMP · stability · change costs, sameness regrows
	var shrimp: float = float(_state.get("shrimp", 5.0))
	var changed: bool = gate != last_gate
	if changed:
		shrimp = maxf(0.0, shrimp - 2.0)
		ev["beds_hit"] = true
	else:
		shrimp = minf(10.0, shrimp + 1.0)
		if shrimp >= 7.0:
			ev["beds_rich"] = true
	_state["shrimp"] = shrimp

	# WATER · the channel wants exchange · stagnation costs
	var channel: float = float(_state.get("channel", 6.0))
	var closed_streak: int = int(_state.get("closed_streak", 0))
	closed_streak = closed_streak + 1 if gate == "closed" else 0
	if closed_streak >= 3:
		channel = maxf(0.0, channel - 1.0)
		ev["stagnant"] = true
	elif openness > 0.0:
		channel = minf(10.0, channel + 0.5)
	_state["channel"] = channel
	_state["closed_streak"] = closed_streak

	# HERON · max(fry, shrimp) rendered as a standing position
	var fry_presence: float = _fry_presence(week)
	var absent: bool = false
	if not bool(_state.get("heron_absent_used", false)):
		if changed and fry_presence < 3.0 and shrimp < 3.0:
			absent = true
			_state["heron_absent_used"] = true
			_state["heron_absent_week"] = week + 1
			ev["heron_absent"] = true
	ev["fry_presence"] = fry_presence

	_state["last_gate"] = gate
	var hist: Array = _state.get("gate_history", [])
	hist.append(gate)
	_state["gate_history"] = hist

	# Turn the page
	week += 1
	_state["week"] = week
	_week_events = ev

	if week > 12:
		_finish_season()
		return

	_recompute_presentation()
	_play_week_bgm()
	_set_notebook(_consequence_line(ev))
	if _heron_stance == "flight":
		_heron_call()
	week_complete.emit(_state)
	queue_redraw()


func _fry_presence(week: int) -> float:
	var fry_remaining: float = float(_state.get("fry_remaining", 9.0))
	var fry_out: float = float(_state.get("fry_out", 0.0))
	if week < 4:
		return fry_remaining * 0.5
	elif week <= 6:
		return fry_remaining * 0.4 + fry_out * 0.4
	else:
		return fry_out * 0.45


func _recompute_presentation() -> void:
	var week: int = int(_state.get("week", 1))
	var shrimp: float = float(_state.get("shrimp", 5.0))
	var fry_presence: float = _fry_presence(week)
	if week == int(_state.get("heron_absent_week", -1)):
		_heron_stance = "absent"
		return
	# The week after she was gone, she comes back on the wing.
	if week == int(_state.get("heron_absent_week", -1)) + 1 \
			and bool(_state.get("heron_absent_used", false)):
		_heron_stance = "flight"
		return
	var best: float = maxf(fry_presence, shrimp)
	if best < 3.0:
		_heron_stance = "hunched"
	elif shrimp >= fry_presence and shrimp >= 6.0:
		_heron_stance = "feeding"
	else:
		_heron_stance = "upright"


func _finish_season() -> void:
	_season_done = true
	var touches: int = int(_state.get("touches", 0))
	var grades := {
		"water":    _grade(float(_state.get("channel", 6.0)), [8.0, 6.0, 4.0]),
		"passage":  _grade(float(_state.get("fry_out", 0.0)), [6.75, 4.5, 2.25]),
		"patience": _patience_grade(touches),
		"touches":  touches,
	}
	season_over.emit(_state, grades)


func _grade(v: float, cuts: Array) -> String:
	if v >= float(cuts[0]): return "A"
	if v >= float(cuts[1]): return "B"
	if v >= float(cuts[2]): return "C"
	return "D"


func _patience_grade(touches: int) -> String:
	if touches <= 2: return "A"
	if touches <= 4: return "B"
	if touches <= 7: return "C"
	return "D"


# ─── The score · stems by state ─────────────────────────────────

func _play_week_bgm() -> void:
	var week: int = int(_state.get("week", 1))
	var suffix := ""
	if _fry_presence(week) >= 4.5:
		suffix += "f"
	if float(_state.get("shrimp", 5.0)) >= 5.0:
		suffix += "s"
	if _heron_stance == "upright" or _heron_stance == "feeding":
		suffix += "h"
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm("res://assets/audio/bgm/e1/mix_d%s.wav" % suffix)


func _heron_call() -> void:
	# Used at most twice per run · tracked in state.
	var calls: int = int(_state.get("heron_calls", 0))
	if calls >= 2:
		return
	_state["heron_calls"] = calls + 1
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play("creature_arrival_heron", 0.7)


# ─── The lever ───────────────────────────────────────────────────

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed \
			and event.button_index == MOUSE_BUTTON_LEFT:
		var mev: InputEventMouseButton = event
		for key in _lever_rects.keys():
			if (_lever_rects[key] as Rect2).has_point(mev.position):
				_set_gate(String(key))
				accept_event()
				return


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree() or _season_done:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		match kev.keycode:
			KEY_1: _set_gate("open")
			KEY_2: _set_gate("half")
			KEY_3: _set_gate("closed")
			KEY_SPACE, KEY_ENTER: _advance_week()
			KEY_ESCAPE:
				quit.emit()
				get_viewport().set_input_as_handled()


func _set_gate(setting: String) -> void:
	if _season_done:
		return
	var gate: String = String(_state.get("gate", "closed"))
	if setting == gate:
		return
	_state["gate"] = setting
	_state["touches"] = int(_state.get("touches", 0)) + 1
	var sb := get_node_or_null("/root/SFXBank")
	if sb != null and sb.has_method("play"):
		sb.play("tide_gate_toggle")
	queue_redraw()


# ─── Field notebook lines ────────────────────────────────────────

func _arrival_line() -> String:
	var week: int = int(_state.get("week", 1))
	if week == 1:
		return "wk 1 · took over the gate log from mr. tolonen · the lever takes three positions · the heron was here before me"
	return "wk %d · back at the gate · the log where I left it" % week


func _consequence_line(ev: Dictionary) -> String:
	var week: int = int(_state.get("week", 1))
	var w: int = int(ev.get("week", week - 1))
	if ev.has("heron_absent"):
		return "wk %d · no heron · checked twice · wrote nothing else today" % week
	if ev.has("stranded"):
		return "wk %d · the window closed with fry still above the gate · they will stay the season now · my doing" % week
	if _heron_stance == "flight":
		return "wk %d · she came back low over the reeds · did not look at me" % week
	if ev.has("passage") and float(ev.get("passage", 0.0)) >= 2.0:
		return "wk %d · fry moving at the ebb · counted more than hoped · gold on the water by the gate" % week
	if ev.has("passage") and float(ev.get("passage", 0.0)) > 0.0:
		return "wk %d · some fry through on the tide · fewer than the creek promised" % week
	if w >= 4 and w <= 6 and String(ev.get("gate", "")) == "closed":
		return "wk %d · fry schooling above the gate · the gate was closed · they waited" % week
	if ev.has("beds_rich"):
		return "wk %d · air-holes thick on the flat · the beds like being left alone · noted" % week
	if ev.has("beds_hit"):
		return "wk %d · worked the lever · the flat went quiet after · shrimp count down" % week
	if ev.has("stagnant"):
		return "wk %d · water going flat behind the gate · a smell to it · it wants the sea" % week
	match week:
		2:  return "wk 2 · overcast · gulls over the far flat · the estuary does not need me yet"
		3:  return "wk 3 · creek mouth silver at dusk · fry staging · the window is coming"
		7:  return "wk 7 · the window is over · what went, went"
		8:  return "wk 8 · rain all week · the gate post swollen · lever stiff"
		9:  return "wk 9 · counted stances not numbers · she tells me more than the log sheet does"
		10: return "wk 10 · a class from the school walked the dike · I showed them the gate · did not touch it"
		11: return "wk 11 · light through at the ebb for one hour · gold on the water · wrote it down"
		12: return "wk 12 · last week of the season · the estuary is what the summer made it"
		_:  return "wk %d · overcast · tide on schedule · the heron knows things I don't" % week


func _set_notebook(line: String) -> void:
	_notebook.text = line


# ─── The picture ─────────────────────────────────────────────────

func _hash(n: int) -> float:
	var x: int = (n * 2654435761) & 0x7FFFFFFF
	x = (x ^ (x >> 13)) * 1274126177 & 0x7FFFFFFF
	return float(x % 1000) / 1000.0


func _draw() -> void:
	var week: int = int(_state.get("week", 1))
	var luck: float = float(_state["luck"][clampi(week - 1, 0, 11)]) if _state.has("luck") else 0.7
	# Four tide states · the water line swaps which third is water
	var tide: int = clampi(int(luck * 4.0), 0, 3)
	var flat_top: int = [500, 460, 420, 380][tide]

	# Sky · always overcast
	draw_rect(Rect2(0, 0, 1280, SKY_BOTTOM), C_SKY)
	# Sea
	draw_rect(Rect2(0, SKY_BOTTOM, 1280, flat_top - SKY_BOTTOM), C_WATER)
	# Exposed flat
	draw_rect(Rect2(0, flat_top, 1280, FLAT_BOTTOM - flat_top), C_FLAT)
	# Channel ribbon through the flat · the deep keeps a line to the sea
	if flat_top < FLAT_BOTTOM:
		draw_rect(Rect2(560, flat_top, 120, FLAT_BOTTOM - flat_top), C_WATER)

	# Reed line
	draw_rect(Rect2(0, REED_TOP, 1280, REED_BOTTOM - REED_TOP), C_REED)
	for i in range(64):
		var rx: float = 8.0 + i * 20.0 + _hash(i) * 10.0
		var rh: float = 14.0 + _hash(i + 100) * 22.0
		draw_rect(Rect2(rx, REED_TOP - rh, 3, rh), C_REED)

	# Foreground bank · where the notebook rests
	draw_rect(Rect2(0, BANK_TOP, 1280, 720 - BANK_TOP), C_WATER)

	# Shimmer band · chum fry at the surface
	var fry_p: float = _fry_presence(week)
	var shimmer_n: int = int(fry_p * 9.0)
	for i in range(shimmer_n):
		var sx: float = 300.0 + _hash(week * 61 + i) * 800.0
		var sy: float = float(flat_top) - 8.0 - _hash(week * 97 + i) * 14.0
		draw_rect(Rect2(sx, sy, 3, 2), C_HERON)

	# Tide-gold · maybe forty pixels · earned
	var good_week: bool = float(_week_events.get("passage", 0.0)) >= 2.0 \
			or _week_events.has("beds_rich")
	if good_week:
		for i in range(20):
			var gx: float = 480.0 + _hash(week * 131 + i) * 400.0
			draw_rect(Rect2(gx, flat_top - 3, 2, 2), C_GOLD)

	# Mud shrimp air-holes on the exposed flat
	var shrimp: float = float(_state.get("shrimp", 5.0))
	var holes: int = int(shrimp * 8.0)
	if flat_top < FLAT_BOTTOM:
		for i in range(holes):
			var hx: float = 60.0 + _hash(week * 17 + i * 3) * 1140.0
			var hy: float = float(flat_top) + 12.0 + _hash(week * 29 + i * 7) * float(FLAT_BOTTOM - flat_top - 24)
			if hx > 555.0 and hx < 685.0:
				continue   # not in the channel
			draw_rect(Rect2(hx, hy, 2, 2), C_WATER)

	_draw_gate(week)
	_draw_heron(flat_top)


func _draw_gate(week: int) -> void:
	# The tide gate at frame-left · housing, two posts, the lever.
	draw_rect(Rect2(60, 300, 24, 320), C_REED)     # near post
	draw_rect(Rect2(200, 320, 20, 300), C_REED)    # far post
	draw_rect(Rect2(60, 288, 160, 26), C_REED)     # crossbeam
	draw_rect(Rect2(64, 292, 152, 4), C_WATER)     # weathering line
	# Gate leaf position · openness read as how much leaf is raised
	var gate: String = String(_state.get("gate", "closed"))
	var gate_idx: int = ["open", "half", "closed"].find(gate)
	if gate_idx < 0:
		gate_idx = 2
	var leaf_h: int = [40, 110, 180][gate_idx]
	draw_rect(Rect2(88, 314, 108, leaf_h), C_WATER)
	draw_rect(Rect2(88, 314 + leaf_h - 4, 108, 4), C_HERON)  # wet lip

	# Lever quadrant on the housing · three notches
	draw_rect(Rect2(92, 332, 8, 136), C_WATER)
	var names := ["open", "half", "closed"]
	for i in range(3):
		var r: Rect2 = _lever_rects[names[i]]
		draw_rect(Rect2(r.position.x + 4, r.position.y + 16, 20, 6), C_WATER)
	# The handle · sits in the current notch
	var cur: Rect2 = _lever_rects[gate]
	draw_rect(Rect2(cur.position.x + 8, cur.position.y + 10, 76, 14), C_HERON)
	draw_rect(Rect2(cur.position.x + 76, cur.position.y + 6, 16, 22), C_HERON)

	# The week number · carved into the near post
	var font := get_theme_default_font()
	draw_string(font, Vector2(64, 356), "WK", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, C_WATER)
	draw_string(font, Vector2(64, 376), "%02d" % week, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, C_WATER)


func _draw_heron(flat_top: int) -> void:
	if _heron_stance == "absent":
		return
	var path: String = SPRITE_DIR + "heron_" + _heron_stance + ".json"
	if not _heron.load_from(path):
		return
	var tex: Texture2D = _heron.texture()
	if tex == null:
		return
	var size := Vector2(72, 96)   # 12×16 at 6×
	var pos: Vector2
	match _heron_stance:
		"upright":  pos = Vector2(268, float(flat_top) - size.y + 10.0)   # by the gate
		"feeding":  pos = Vector2(820, FLAT_BOTTOM - size.y - 6.0)        # far out on the flat
		"hunched":  pos = Vector2(960, float(flat_top) - size.y - 26.0)   # on the piling
		"flight":   pos = Vector2(700, 180)                               # over the reeds
		_:          pos = Vector2(268, float(flat_top) - size.y + 10.0)
	if _heron_stance == "hunched":
		# The piling she hunches on
		draw_rect(Rect2(pos.x + 28, flat_top - 30, 14, 90), C_REED)
	draw_texture_rect(tex, Rect2(pos, size), false)
