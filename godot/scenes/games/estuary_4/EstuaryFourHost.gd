extends Control
## ESTUARY 4 · run controller · Oneironautics, 2005 · set 2016.
## The studio's course-correction: the archive, the water, the
## hunter, the king tide.  Reads The Tideline's canon (the filed
## register) back to the player when the token bus carries it.
##
## Save file: user://estuary_4.save.json
## Uniform slowstock host contract · F4-compliant via "ui" group.

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const SAVE_PATH      := "user://estuary_4.save.json"
const CAMPAIGN_SCENE := "res://scenes/games/estuary_4/EstuaryFour.tscn"

const C_WATER := Color("28343c")
const C_FOG   := Color("dce4e0")
const C_REED  := Color("7a8a5e")
const C_DIM   := Color("70807a")

var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "oneironautics")
	theme = preload("res://scenes/games/StickTheme.gd").make("oneironautics")
	_run_state = _fresh_state()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state() -> Dictionary:
	return {
		"chapter": 1,
		"plan": "",
		"calls": {},
		"cade_walked": false,
		"read_notebook": false,
		"canon_vars": {},
		"lore_tokens_pending": []
	}


func _load_save_if_present() -> void:
	if not FileAccess.file_exists(SAVE_PATH): return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var saved: Dictionary = parsed
		for k in saved.keys():
			_run_state[String(k)] = saved[k]


func _save_state() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null: return
	f.store_string(JSON.stringify(_run_state, "  "))
	f.close()


func start_new_run(_manager_mode: bool = false) -> void:
	_run_state = _fresh_state()
	_save_state()
	_open_campaign()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null


func _build_title_screen() -> void:
	_clear_current_scene()
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		# E1's base stem · the tide-gate drone the whole line grew from.
		am.request_scene_bgm("res://assets/audio/bgm/e1/mix_d.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_WATER
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "oneironautics")

	var title := Label.new()
	title.text = "ESTUARY 4"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	title.offset_top = -170
	title.offset_bottom = -110
	title.offset_left = -360
	title.offset_right = 360
	title.add_theme_font_size_override("font_size", 42)
	title.add_theme_color_override("font_color", C_FOG)
	_title_root.add_child(title)

	var sub := Label.new()
	sub.text = "ONEIRONAUTICS · PORTLAND · 2005 · set in the year 2016\nthe archive · the water · the hunter · the king tide"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	sub.offset_top = -100
	sub.offset_bottom = -40
	sub.offset_left = -380
	sub.offset_right = 380
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_REED)
	_title_root.add_child(sub)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -240
	v.offset_right = 240
	v.offset_top = -10
	v.offset_bottom = 210
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var in_progress: bool = int(_run_state.get("chapter", 1)) > 1 or String(_run_state.get("plan", "")) != ""

	var begin_btn := Button.new()
	begin_btn.text = "  TAKE THE ASSIGNMENT  " if not in_progress else "  BACK TO THE WATERSHED  "
	begin_btn.add_theme_font_size_override("font_size", 15)
	begin_btn.pressed.connect(func() -> void:
		if in_progress:
			_open_campaign()
		else:
			start_new_run(false))
	v.add_child(begin_btn)

	if in_progress:
		var re_btn := Button.new()
		re_btn.text = "  start the campaign over  "
		re_btn.flat = true
		re_btn.add_theme_font_size_override("font_size", 13)
		re_btn.pressed.connect(func() -> void: start_new_run(false))
		v.add_child(re_btn)

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


func _open_campaign() -> void:
	_clear_current_scene()
	_child_scene = load(CAMPAIGN_SCENE).instantiate()
	_child_scene.quit.connect(_on_campaign_quit)
	_child_scene.chapter_done.connect(_on_chapter_done)
	_child_scene.campaign_over.connect(_on_campaign_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_campaign_quit() -> void:
	if _child_scene != null and _child_scene.get("_state") != null:
		_run_state = _child_scene.get("_state")
	_save_state()
	_build_title_screen()


func _on_chapter_done(state: Dictionary) -> void:
	_run_state = state
	_save_state()


func _on_campaign_over(state: Dictionary) -> void:
	_run_state = state
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("estuary_4_finished"):
		tokens.append("estuary_4_finished")
	if bool(_run_state.get("read_notebook", false)) and not tokens.has("e4_read_the_2003_notebook"):
		tokens.append("e4_read_the_2003_notebook")
	if bool(_run_state.get("cade_walked", false)) and not tokens.has("e4_cade_walked_the_line"):
		tokens.append("e4_cade_walked_the_line")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["e4_plan"] = String(_run_state.get("plan", ""))
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
