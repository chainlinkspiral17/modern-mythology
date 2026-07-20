extends Control
## THE TIDELINE · run controller · Oneironautics, 2004 — and, with
## `remake_mode` set by SlowstockBoot before add_child, TIDELINE
## SURVEY · Meridian Heritage, 2048: the same twelve stations
## rebuilt "faithfully," minus the two-line limit that was the
## game.  One engine, two carts, one argument.
##
## Save files: user://the_tideline.save.json /
##             user://tideline_survey_2048.save.json
## Uniform slowstock host contract · F4-compliant via "ui" group.

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const WALK_SCENE := "res://scenes/games/the_tideline/TidelineWalk.tscn"

# December-morning inks (original) · product chrome (remake)
const C_SEA    := Color("2c343a")
const C_FOG    := Color("dfe4e2")
const C_KELP   := Color("6a7a5e")
const C_DIM    := Color("74808a")
const C_MER_BG := Color("eef4f4")
const C_MER_TX := Color("30484a")

# Set by SlowstockBoot BEFORE add_child.
var remake_mode: bool = false

var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null


func _save_path() -> String:
	return "user://tideline_survey_2048.save.json" if remake_mode else "user://the_tideline.save.json"


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	var preset := "meridian" if remake_mode else "oneironautics"
	SlowstickLook.apply(self, preset)
	theme = preload("res://scenes/games/StickTheme.gd").make(preset)
	_run_state = _fresh_state()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state() -> Dictionary:
	return {
		"station": 0,
		"lines": [],            # [{station, obs_id, line, cat}]
		"watched_the_seal": false,
		"canon_vars": {},
		"lore_tokens_pending": []
	}


func _load_save_if_present() -> void:
	if not FileAccess.file_exists(_save_path()): return
	var f := FileAccess.open(_save_path(), FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var saved: Dictionary = parsed
		for k in saved.keys():
			_run_state[String(k)] = saved[k]


func _save_state() -> void:
	var f := FileAccess.open(_save_path(), FileAccess.WRITE)
	if f == null: return
	f.store_string(JSON.stringify(_run_state, "  "))
	f.close()


func start_new_run(_manager_mode: bool = false) -> void:
	_run_state = _fresh_state()
	_save_state()
	_open_walk()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null


func _build_title_screen() -> void:
	_clear_current_scene()
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_scene_bgm"):
		am.stop_scene_bgm()

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_MER_BG if remake_mode else C_SEA
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	if not remake_mode:
		preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "oneironautics")

	var title := Label.new()
	title.text = "TIDELINE SURVEY" if remake_mode else "THE TIDELINE"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	title.offset_top = -170
	title.offset_bottom = -110
	title.offset_left = -360
	title.offset_right = 360
	title.add_theme_font_size_override("font_size", 40)
	title.add_theme_color_override("font_color", C_MER_TX if remake_mode else C_FOG)
	_title_root.add_child(title)

	var sub := Label.new()
	if remake_mode:
		sub.text = "MERIDIAN HERITAGE INTERACTIVE · 2048\na faithful rebuild of the 2004 original · coverage 100% · nothing will be missed"
	else:
		sub.text = "ONEIRONAUTICS · PORTLAND · 2004\none king-tide morning · twelve stations · two lines each"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	sub.offset_top = -100
	sub.offset_bottom = -40
	sub.offset_left = -380
	sub.offset_right = 380
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", Color("6aa8a0") if remake_mode else C_KELP)
	_title_root.add_child(sub)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -240
	v.offset_right = 240
	v.offset_top = -10
	v.offset_bottom = 210
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var in_progress: bool = int(_run_state.get("station", 0)) > 0

	var begin_btn := Button.new()
	if remake_mode:
		begin_btn.text = "  BEGIN SURVEY  "
	else:
		begin_btn.text = "  TAKE THE NOTEBOOK  " if not in_progress else "  BACK TO THE BEACH  "
	begin_btn.add_theme_font_size_override("font_size", 15)
	begin_btn.pressed.connect(func() -> void:
		if in_progress and not remake_mode:
			_open_walk()
		else:
			start_new_run(false))
	v.add_child(begin_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.flat = true
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.add_theme_color_override("font_color", C_DIM)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	GamepadMgr.focus_first.call_deferred(v)


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


func _open_walk() -> void:
	_clear_current_scene()
	_child_scene = load(WALK_SCENE).instantiate()
	_child_scene.set("remake_mode", remake_mode)
	_child_scene.quit.connect(_on_walk_quit)
	_child_scene.station_done.connect(_on_station_done)
	_child_scene.walk_over.connect(_on_walk_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_walk_quit() -> void:
	if _child_scene != null and _child_scene.get("_state") != null:
		_run_state = _child_scene.get("_state")
	_save_state()
	_build_title_screen()


func _on_station_done(state: Dictionary) -> void:
	_run_state = state
	_save_state()


func _on_walk_over(state: Dictionary) -> void:
	_run_state = state
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if remake_mode:
		if not tokens.has("tideline_survey_2048_finished"):
			tokens.append("tideline_survey_2048_finished")
		if bool(_run_state.get("watched_the_seal", false)) and not tokens.has("tideline_2048_the_seal_still"):
			tokens.append("tideline_2048_the_seal_still")
		if OneironauticsTokens.has("the_tideline_finished") and not tokens.has("tideline_original_compared"):
			tokens.append("tideline_original_compared")
	else:
		if not tokens.has("the_tideline_finished"):
			tokens.append("the_tideline_finished")
		if (_run_state.get("lines", []) as Array).size() >= 22 and not tokens.has("tideline_full_notebook"):
			tokens.append("tideline_full_notebook")
		if bool(_run_state.get("watched_the_seal", false)) and not tokens.has("tideline_the_seal"):
			tokens.append("tideline_the_seal")
		if OneironauticsTokens.has("tideline_survey_2048_finished") and not tokens.has("tideline_original_compared"):
			tokens.append("tideline_original_compared")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["tideline_lines_recorded"] = (_run_state.get("lines", []) as Array).size()
	canon["tideline_remake"] = remake_mode
	_run_state["canon_vars"] = canon
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
