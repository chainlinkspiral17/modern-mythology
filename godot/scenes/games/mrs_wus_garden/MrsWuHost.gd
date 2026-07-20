extends Control
## MRS. WU'S GARDEN · run controller · Oneironautics, October 2003.
##
## Ines Rocha solo, made in stolen evenings the same October she
## welded Estuary 3.  Set in Corvallis, fall 1995.  Six evenings,
## nine beds, three actions, and the frost is coming.
##
## Save file: user://mrs_wus_garden.save.json
## Uniform slowstock host contract · F4-compliant via "ui" group.

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/mrs_wus_garden/manifest.json"
const SAVE_PATH     := "user://mrs_wus_garden.save.json"
const GARDEN_SCENE  := "res://scenes/games/mrs_wus_garden/WuGarden.tscn"

# Field-guide gouache · dusk garden inks
const C_DUSK  := Color("2a3028")
const C_CREAM := Color("ece4d0")
const C_LEAF  := Color("8aa870")
const C_DIM   := Color("6a7460")

var _manifest: Dictionary = {}
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
	_load_manifest()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state() -> Dictionary:
	return {
		"evening": 1,
		"conditions": {},
		"missed": {},
		"covered": [],
		"dead": [],
		"sits": 0,
		"stories_heard": [],
		"last_tended": "",
		"visitor_seen": false,
		"melody_heard": false,
		"canon_vars": {},
		"lore_tokens_pending": []
	}


func _load_manifest() -> void:
	if not FileAccess.file_exists(MANIFEST_PATH): return
	var f := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		_manifest = parsed


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
	_open_garden()


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
		am.request_scene_bgm("res://assets/audio/bgm/hnn/autumn.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_DUSK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "oneironautics")

	var title := Label.new()
	title.text = "MRS. WU'S GARDEN"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	title.offset_top = -170
	title.offset_bottom = -110
	title.offset_left = -360
	title.offset_right = 360
	title.add_theme_font_size_override("font_size", 40)
	title.add_theme_color_override("font_color", C_CREAM)
	_title_root.add_child(title)

	var sub := Label.new()
	sub.text = "ONEIRONAUTICS · PORTLAND · OCTOBER 2003\nCorvallis, fall 1995 · nine beds · one fall · the frost is coming"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	sub.offset_top = -100
	sub.offset_bottom = -40
	sub.offset_left = -360
	sub.offset_right = 360
	sub.add_theme_font_size_override("font_size", 13)
	sub.add_theme_color_override("font_color", C_LEAF)
	_title_root.add_child(sub)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -240
	v.offset_right = 240
	v.offset_top = -10
	v.offset_bottom = 210
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var in_progress: bool = int(_run_state.get("evening", 1)) > 1

	var begin_btn := Button.new()
	begin_btn.text = "  TAKE THE GLOVES  " if not in_progress else "  BACK THROUGH THE GATE  "
	begin_btn.add_theme_font_size_override("font_size", 15)
	begin_btn.pressed.connect(func() -> void:
		if in_progress:
			_open_garden()
		else:
			start_new_run(false))
	v.add_child(begin_btn)

	if in_progress:
		var re_btn := Button.new()
		re_btn.text = "  start the fall over  "
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


func _open_garden() -> void:
	_clear_current_scene()
	_child_scene = load(GARDEN_SCENE).instantiate()
	_child_scene.quit.connect(_on_garden_quit)
	_child_scene.evening_done.connect(_on_evening_done)
	_child_scene.garden_over.connect(_on_garden_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_garden_quit() -> void:
	if _child_scene != null and _child_scene.get("_state") != null:
		_run_state = _child_scene.get("_state")
	_save_state()
	_build_title_screen()


func _on_evening_done(state: Dictionary) -> void:
	_run_state = state
	_save_state()


func _on_garden_over(state: Dictionary) -> void:
	_run_state = state
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("mrs_wus_garden_finished"):
		tokens.append("mrs_wus_garden_finished")
	# Nine of nine through the frost.
	var conditions: Dictionary = _run_state.get("conditions", {})
	var alive := 0
	for b in conditions.keys():
		if int(conditions[b]) >= 1:
			alive += 1
	if alive >= 9 and not tokens.has("wu_garden_all_beds_saved"):
		tokens.append("wu_garden_all_beds_saved")
	if bool(_run_state.get("melody_heard", false)) and not tokens.has("wu_garden_hummed_melody"):
		tokens.append("wu_garden_hummed_melody")
	if bool(_run_state.get("visitor_seen", false)) and not tokens.has("wu_garden_the_counselor_visited"):
		tokens.append("wu_garden_the_counselor_visited")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["wu_garden_beds_alive"] = alive
	canon["wu_garden_stories_heard"] = (_run_state.get("stories_heard", []) as Array).size()
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
