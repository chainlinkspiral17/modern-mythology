extends Control
## MRS. WU'S GARDEN · the fall · one screen, nine beds, six evenings.
##
## Three actions an evening: TEND a bed (meet its need) or SIT on
## the porch (one story, keyed to the last bed you tended · sitting
## is mechanically "wasted" and is the entire point).  Evening 5 is
## the frost triage: four actions, nine beds, not enough sheets.
## Evening 6 is the walk-through and the ending.
##
## Beds carry a quiet 0-3 condition; the text describes it, no
## numbers shown.  Miss a bed two evenings running and it declines.
##
## Emits: quit · evening_done(state) · garden_over(state)

signal quit
signal evening_done(state: Dictionary)
signal garden_over(state: Dictionary)

const DATA_PATH := "res://resources/games/vol7/mrs_wus_garden/garden.json"

const C_DUSK   := Color("2a3028")
const C_PANEL  := Color("39412f")
const C_CREAM  := Color("ece4d0")
const C_LEAF   := Color("8aa870")
const C_GOLD   := Color("d8b878")
const C_DIM    := Color("6a7460")
const C_FROST  := Color("b8c8d8")
const C_GONE   := Color("54503f")

# condition → how the bed reads (no numbers shown, ever)
const COND_LINE := {
	0: "gone quiet",
	1: "struggling",
	2: "holding",
	3: "thriving",
}
const COND_COLOR := {
	0: C_GONE,
	1: Color("a89058"),
	2: C_LEAF,
	3: Color("a8cc80"),
}

var _state: Dictionary = {}
var _data: Dictionary = {}
var _beds: Array = []
var _actions_left: int = 3
var _tended_tonight: Array = []
var _grid: GridContainer = null
var _log_lbl: RichTextLabel = null
var _log_lines: Array = []
var _hdr_lbl: Label = null
var _actions_lbl: Label = null
var _sit_btn: Button = null
var _end_btn: Button = null
var _over: bool = false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	if f != null:
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			_data = parsed
			_beds = _data.get("beds", [])


func boot(state: Dictionary) -> void:
	_state = state
	# Seed conditions on a fresh fall · everything starts holding.
	var conditions: Dictionary = _state.get("conditions", {})
	if conditions.is_empty():
		for b_v in _beds:
			conditions[String((b_v as Dictionary)["id"])] = 2
		_state["conditions"] = conditions
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm("res://assets/audio/bgm/hnn/autumn.wav")
	_build_ui()
	_begin_evening()


# ─── UI skeleton ─────────────────────────────────────────────────

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = C_DUSK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	_hdr_lbl = Label.new()
	_hdr_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hdr_lbl.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_hdr_lbl.offset_top = 14
	_hdr_lbl.offset_bottom = 44
	_hdr_lbl.add_theme_font_size_override("font_size", 19)
	_hdr_lbl.add_theme_color_override("font_color", C_CREAM)
	add_child(_hdr_lbl)

	_actions_lbl = Label.new()
	_actions_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_actions_lbl.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_actions_lbl.offset_top = 46
	_actions_lbl.offset_bottom = 68
	_actions_lbl.add_theme_font_size_override("font_size", 13)
	_actions_lbl.add_theme_color_override("font_color", C_GOLD)
	add_child(_actions_lbl)

	_grid = GridContainer.new()
	_grid.columns = 3
	_grid.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_grid.offset_left = -430
	_grid.offset_right = 430
	_grid.offset_top = -180
	_grid.offset_bottom = 160
	_grid.add_theme_constant_override("h_separation", 10)
	_grid.add_theme_constant_override("v_separation", 8)
	add_child(_grid)

	# The porch row.
	var porch := HBoxContainer.new()
	porch.alignment = BoxContainer.ALIGNMENT_CENTER
	porch.add_theme_constant_override("separation", 20)
	porch.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	porch.offset_top = -156
	porch.offset_bottom = -120
	porch.offset_left = -300
	porch.offset_right = 300
	add_child(porch)

	_sit_btn = Button.new()
	_sit_btn.text = "  SIT · tea on the porch  "
	_sit_btn.add_theme_font_size_override("font_size", 14)
	_sit_btn.pressed.connect(_on_sit)
	porch.add_child(_sit_btn)

	_end_btn = Button.new()
	_end_btn.text = "  END THE EVENING  "
	_end_btn.add_theme_font_size_override("font_size", 14)
	_end_btn.pressed.connect(_on_end_evening)
	porch.add_child(_end_btn)

	# The evening narrating itself.
	var log_bg := ColorRect.new()
	log_bg.color = Color(0.08, 0.10, 0.07, 0.85)
	log_bg.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	log_bg.offset_left = 30
	log_bg.offset_right = -30
	log_bg.offset_top = -112
	log_bg.offset_bottom = -10
	add_child(log_bg)

	_log_lbl = RichTextLabel.new()
	_log_lbl.bbcode_enabled = false
	_log_lbl.scroll_active = false
	_log_lbl.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_log_lbl.offset_left = 44
	_log_lbl.offset_right = -44
	_log_lbl.offset_top = -106
	_log_lbl.offset_bottom = -14
	_log_lbl.add_theme_font_size_override("normal_font_size", 14)
	_log_lbl.add_theme_color_override("default_color", C_CREAM)
	_log_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_log_lbl)


func _say(line: String) -> void:
	_log_lines.append(line)
	while _log_lines.size() > 4:
		_log_lines.pop_front()
	if _log_lbl != null:
		_log_lbl.text = "\n".join(PackedStringArray(_log_lines))


# ─── The evenings ────────────────────────────────────────────────

func _evening_def(n: int) -> Dictionary:
	for e_v in _data.get("evenings", []):
		if int((e_v as Dictionary).get("n", 0)) == n:
			return e_v
	return {}


func _begin_evening() -> void:
	var n: int = int(_state.get("evening", 1))
	if n >= 6:
		_run_aftermath()
		return
	_tended_tonight = []
	_actions_left = 4 if n == 5 else 3
	var e := _evening_def(n)
	_say(String(e.get("intro", "")))
	# The humming, before the melody resolves.
	if n >= 2 and not bool(_state.get("melody_heard", false)):
		_say(String((_data.get("melody", {}) as Dictionary).get("fragment", "")))
	# The visitor at the fence · gated on the cross-stick bus.
	var vis: Dictionary = _data.get("visitor", {})
	if n == int(vis.get("evening", 3)) and not bool(_state.get("visitor_seen", false)) \
			and OneironauticsTokens.has(String(vis.get("gate_token", ""))):
		_state["visitor_seen"] = true
		_say(String(vis.get("text", "")))
		var sfx := get_node_or_null("/root/SFXBank")
		if sfx: sfx.play("page_turn", 0.4)
	_render()
	GamepadMgr.focus_first.call_deferred(_grid)


func _need_tonight(bed: Dictionary) -> String:
	var n: int = int(_state.get("evening", 1))
	if n == 5:
		return "cover"
	var needs: Array = bed.get("needs", [])
	var idx: int = clampi(n - 1, 0, needs.size() - 1)
	return String(needs[idx]) if not needs.is_empty() else "look"


func _render() -> void:
	var n: int = int(_state.get("evening", 1))
	var e := _evening_def(n)
	_hdr_lbl.text = "· %s ·" % String(e.get("date", ""))
	if n == 5:
		_actions_lbl.text = "armloads of sheets left · %d" % _actions_left
	else:
		_actions_lbl.text = "evening actions left · %d" % _actions_left
	for c in _grid.get_children():
		c.queue_free()
	var conditions: Dictionary = _state.get("conditions", {})
	var covered: Array = _state.get("covered", [])
	for b_v in _beds:
		var bed: Dictionary = b_v
		var bid := String(bed["id"])
		var cond: int = int(conditions.get(bid, 2))
		var btn := Button.new()
		var need := _need_tonight(bed)
		var line := String(COND_LINE.get(cond, "holding"))
		if n == 5:
			var mark := "covered" if covered.has(bid) else ("wants a sheet" if not bool(bed.get("hardy", false)) else "hardy · may stand it")
			btn.text = "%s\n%s · %s" % [String(bed["name"]), line, mark]
		elif _tended_tonight.has(bid):
			btn.text = "%s\n%s · tended tonight" % [String(bed["name"]), line]
		else:
			btn.text = "%s\n%s · wants · %s" % [String(bed["name"]), line, need.replace("_", " ")]
		btn.custom_minimum_size = Vector2(275, 62)
		btn.add_theme_font_size_override("font_size", 13)
		btn.add_theme_color_override("font_color", COND_COLOR.get(cond, C_LEAF) if n != 5 else (C_FROST if covered.has(bid) else COND_COLOR.get(cond, C_LEAF)))
		btn.disabled = _actions_left <= 0 or (_tended_tonight.has(bid) and n != 5) or (n == 5 and covered.has(bid)) or cond <= 0
		btn.pressed.connect(_on_bed_pressed.bind(bid))
		_grid.add_child(btn)
	_sit_btn.disabled = _actions_left <= 0 or n == 5
	_sit_btn.visible = n != 5


func _find_bed(bid: String) -> Dictionary:
	for b_v in _beds:
		if String((b_v as Dictionary)["id"]) == bid:
			return b_v
	return {}


func _on_bed_pressed(bid: String) -> void:
	if _actions_left <= 0:
		return
	var n: int = int(_state.get("evening", 1))
	var bed := _find_bed(bid)
	var sfx := get_node_or_null("/root/SFXBank")
	if n == 5:
		# The triage · one armload of sheets per bed.
		var covered: Array = _state.get("covered", [])
		if not covered.has(bid):
			covered.append(bid)
			_state["covered"] = covered
			_actions_left -= 1
			if sfx: sfx.play("card_place", 0.5)
			_say("You sheet %s against the night, tucked at the corners the way she'd tie twine · like you might be wrong." % String(bed.get("name", bid)))
	else:
		var conditions: Dictionary = _state.get("conditions", {})
		conditions[bid] = clampi(int(conditions.get(bid, 2)) + 1, 0, 3)
		_state["conditions"] = conditions
		var missed: Dictionary = _state.get("missed", {})
		missed[bid] = 0
		_state["missed"] = missed
		_tended_tonight.append(bid)
		_state["last_tended"] = bid
		_actions_left -= 1
		var need := _need_tonight(bed)
		var need_line := String((_data.get("need_lines", {}) as Dictionary).get(need, ""))
		if sfx: sfx.play("coin" if need == "water" else "card_place", 0.35)
		_say("%s · %s." % [String(bed.get("name", bid)), need_line])
	_render()


func _on_sit() -> void:
	if _actions_left <= 0:
		return
	_actions_left -= 1
	_state["sits"] = int(_state.get("sits", 0)) + 1
	var last := String(_state.get("last_tended", ""))
	var heard: Array = _state.get("stories_heard", [])
	var bed := _find_bed(last)
	if not bed.is_empty() and not heard.has(last):
		heard.append(last)
		_state["stories_heard"] = heard
		_say(String(bed.get("story", "")))
	else:
		_say(String(_data.get("porch_default_story", "Tea, and the evening.")))
	# The third sit · the humming resolves.
	if int(_state.get("sits", 0)) >= 3 and not bool(_state.get("melody_heard", false)):
		_state["melody_heard"] = true
		_say(String((_data.get("melody", {}) as Dictionary).get("whole", "")))
		var am := get_node_or_null("/root/AudioMgr")
		if am != null and am.has_method("request_scene_bgm"):
			am.request_scene_bgm("res://assets/audio/bgm/hnn/one_melody.wav")
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("page_turn", 0.4)
	_render()


func _on_end_evening() -> void:
	if _over:
		return
	var n: int = int(_state.get("evening", 1))
	if n == 5:
		_resolve_frost()
	else:
		# Neglect ticks · two evenings unmissed and a bed declines.
		var conditions: Dictionary = _state.get("conditions", {})
		var missed: Dictionary = _state.get("missed", {})
		for b_v in _beds:
			var bid := String((b_v as Dictionary)["id"])
			if _tended_tonight.has(bid) or int(conditions.get(bid, 2)) <= 0:
				continue
			missed[bid] = int(missed.get(bid, 0)) + 1
			if int(missed[bid]) >= 2:
				missed[bid] = 0
				conditions[bid] = maxi(0, int(conditions.get(bid, 2)) - 1)
				if int(conditions[bid]) == 0:
					_say("%s has gone quiet. Nobody says anything about it, which is how you know it was noticed." % String((b_v as Dictionary).get("name", bid)))
		_state["conditions"] = conditions
		_state["missed"] = missed
	_state["evening"] = n + 1
	evening_done.emit(_state)
	_begin_evening()


func _resolve_frost() -> void:
	var conditions: Dictionary = _state.get("conditions", {})
	var covered: Array = _state.get("covered", [])
	var dead: Array = _state.get("dead", [])
	for b_v in _beds:
		var bed: Dictionary = b_v
		var bid := String(bed["id"])
		if covered.has(bid):
			continue
		if bool(bed.get("hardy", false)) and int(conditions.get(bid, 2)) >= 2:
			continue
		conditions[bid] = maxi(0, int(conditions.get(bid, 2)) - 2)
		if int(conditions[bid]) <= 0 and not dead.has(bid):
			dead.append(bid)
	_state["conditions"] = conditions
	_state["dead"] = dead
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("season_settle", 0.6)


# ─── Evening 6 · the walk-through, and the ending ────────────────

func _run_aftermath() -> void:
	_over = true
	_grid.visible = false
	_sit_btn.visible = false
	_end_btn.visible = false
	var e := _evening_def(6)
	_hdr_lbl.text = "· %s ·" % String(e.get("date", ""))
	_actions_lbl.text = ""

	var conditions: Dictionary = _state.get("conditions", {})
	var covered: Array = _state.get("covered", [])
	var alive := 0
	var walk := PackedStringArray()
	walk.append(String(e.get("intro", "")))
	walk.append("")
	for b_v in _beds:
		var bed: Dictionary = b_v
		var bid := String(bed["id"])
		var cond: int = int(conditions.get(bid, 0))
		if cond >= 1:
			alive += 1
			if covered.has(bid):
				walk.append("· %s · stood the frost under its sheet · %s" % [String(bed["name"]), String(COND_LINE.get(cond, ""))])
			elif bool(bed.get("hardy", false)):
				walk.append("· %s · stood it bare, being what it is · %s" % [String(bed["name"]), String(COND_LINE.get(cond, ""))])
			else:
				walk.append("· %s · came through leaner · %s" % [String(bed["name"]), String(COND_LINE.get(cond, ""))])
		else:
			walk.append("· %s · black at the edges, gone at the crown · she touches it once and moves on" % String(bed["name"]))

	var stories: int = (_state.get("stories_heard", []) as Array).size()
	var sits: int = int(_state.get("sits", 0))
	var endings: Dictionary = _data.get("endings", {})
	var pick: Dictionary
	var eid := ""
	if alive >= 7 and stories >= 3:
		eid = "garden_goes_on"
	elif alive >= 4:
		eid = "half_slept"
	elif sits >= 3:
		eid = "good_neighbor_anyway"
	else:
		eid = "fliers_in_drawer"
	pick = endings.get(eid, {})
	var canon: Dictionary = _state.get("canon_vars", {})
	canon["wu_garden_ending"] = eid
	_state["canon_vars"] = canon

	var panel := VBoxContainer.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -420
	panel.offset_right = 420
	panel.offset_top = -220
	panel.offset_bottom = 220
	panel.add_theme_constant_override("separation", 10)
	add_child(panel)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.add_child(scroll)

	var body := Label.new()
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size = Vector2(820, 0)
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", C_CREAM)
	body.text = "\n".join(walk) + "\n\n· %s ·\n\n%s" % [String(pick.get("title", "")), String(pick.get("body", ""))]
	scroll.add_child(body)

	var done := Button.new()
	done.text = "  · return the plate ·  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: garden_over.emit(_state))
	panel.add_child(done)
	GamepadMgr.focus_first.call_deferred(panel)


func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			quit.emit()
			get_viewport().set_input_as_handled()
