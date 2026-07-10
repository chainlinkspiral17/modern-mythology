extends Control
## SWEETGUM · run controller · no publisher · 1996.
##
## Zine-traded homebrew on burned EEPROM.  One night, the
## watchman.  Cease-and-desisted by Oneironautics' lawyers in
## 1997 · the paper trail that proves the studio knew.
##
## The shelf slot does not exist until Pirate Summer's core 1976
## fact is discovered (hidden_until_token in shelf_layout) · you
## cannot own this stick before you know why it exists.
##
## Save file: user://sweetgum.save.json (nights stood · tokens).
## The LOG lives separately at user://sweetgum_log.json and is
## never reset · it is the cartridge.
##
## Signals · uniform slowstock host contract.

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/sweetgum/manifest.json"
const SAVE_PATH     := "user://sweetgum.save.json"
const NIGHT_SCENE   := "res://scenes/games/sweetgum/SweetgumNight.tscn"

const C_DARK := Color("041104")
const C_INK  := Color("46d84a")
const C_THIN := Color("1c5a20")

var _manifest: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "homebrew")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("homebrew")
	_run_state = {
		"nights_stood": 0,
		"island_attempted": false,
		"canon_vars": {},
		"lore_tokens_pending": []
	}
	_load_manifest()
	_load_save_if_present()
	_build_title_screen()


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
	_open_night()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null


func _build_title_screen() -> void:
	_clear_current_scene()
	# No music.  The room is the sound.
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_bgm"):
		am.stop_bgm()

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	# The author's letterform · mis-kerned on purpose · two letters
	# are each other's mirror (the M and W of a kid's one font).
	var title := Label.new()
	title.text = "S W EETG U M"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	title.offset_top = -160
	title.offset_bottom = -100
	title.offset_left = -320
	title.offset_right = 320
	title.add_theme_font_size_override("font_size", 42)
	title.add_theme_color_override("font_color", C_INK)
	_title_root.add_child(title)

	var sub := Label.new()
	sub.text = "one night · the watchman\n(no publisher. no warranty. no explanation.)"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	sub.offset_top = -90
	sub.offset_bottom = -30
	sub.offset_left = -320
	sub.offset_right = 320
	sub.add_theme_font_size_override("font_size", 14)
	sub.add_theme_color_override("font_color", C_THIN)
	_title_root.add_child(sub)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -220
	v.offset_right = 220
	v.offset_top = 0
	v.offset_bottom = 220
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var nights: int = int(_run_state.get("nights_stood", 0))

	var watch_btn := Button.new()
	watch_btn.flat = true
	watch_btn.text = "[ STAND THE WATCH ]" if nights == 0 else "[ STAND IT AGAIN ]"
	watch_btn.add_theme_font_size_override("font_size", 16)
	watch_btn.add_theme_color_override("font_color", C_INK)
	watch_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(watch_btn)

	var back_btn := Button.new()
	back_btn.flat = true
	back_btn.text = "[ back to shelf ]"
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.add_theme_color_override("font_color", C_THIN)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	if nights > 0:
		var status := Label.new()
		status.text = "the log remembers %d night(s) of yours. it remembers all of them." % nights
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_THIN)
		v.add_child(status)


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


func _open_night() -> void:
	_clear_current_scene()
	_child_scene = load(NIGHT_SCENE).instantiate()
	_child_scene.quit.connect(_on_night_quit)
	_child_scene.watch_over.connect(_on_watch_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_night_quit() -> void:
	# Quitting mid-watch leaves the log's gaps to speak for
	# themselves.  The night is not marked stood.
	_save_state()
	_build_title_screen()


func _on_watch_over(state: Dictionary) -> void:
	_run_state = state
	_run_state["nights_stood"] = int(_run_state.get("nights_stood", 0)) + 1
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("sweetgum_watch_stood"):
		tokens.append("sweetgum_watch_stood")
	if bool(_run_state.get("island_attempted", false)) \
			and not tokens.has("sweetgum_island_light_logged_attempt"):
		tokens.append("sweetgum_island_light_logged_attempt")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["sweetgum_nights_stood"] = int(_run_state.get("nights_stood", 0))
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
