extends Control
## The Earthman Chronicles · run controller.
##
## Flow:
##   1. Title screen (this scene, on _ready) · NEW GAME /
##      CONTINUE / back to shelf
##   2. NEW GAME · opens EarthmanChapter1Intro
##   3. Chapter 1 completes · returns to title (Chapter 2 pending)
##
## Save file: user://earthman_chronicles.save.json
## Contains: chapter progress, class-focus, party disposition,
## Workings completed, Corrections found, run_state from choices.
##
## Signals · matches Pirate Summer / Estuary 3 / Fey Faire pattern:
##   quit_to_shelf · caller (SlowstockBoot) reopens shelf
##   finished(canon_vars, lore_tokens) · caller merges into
##     GauntletState + reopens shelf
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/earthman_chronicles/manifest.json"
const SAVE_PATH     := "user://earthman_chronicles.save.json"
const CH1_SCENE     := "res://scenes/games/earthman_chronicles/EarthmanChapter1Intro.tscn"
const CH2_SCENE     := "res://scenes/games/earthman_chronicles/EarthmanChapter2Approach.tscn"

# Astro-Cortex palette
const C_BG           := Color(0.094, 0.094, 0.157, 1.0)
const C_CORTEX       := Color(0.345, 0.188, 0.376, 1.0)
const C_AMBER        := Color(0.784, 0.376, 0.125, 1.0)
const C_GREEN        := Color(0.0, 0.753, 0.376, 1.0)
const C_RED          := Color(0.753, 0.125, 0.125, 1.0)
const C_CREAM        := Color(0.912, 0.816, 0.565, 1.0)
const C_WHITE        := Color(0.941, 0.941, 0.941, 1.0)
const C_GRAY         := Color(0.282, 0.282, 0.314, 1.0)

var _manifest: Dictionary = {}
var _run_state: Dictionary = {
	"chapter":             1,
	"class_focus":         "",       # chemistry | mysticism | synthesis
	"rafaton_disposition": 0,
	"workings_completed":  [],
	"corrections_found":   [],
	"party_disposition":   {},
	"party_members":       ["jack"],
	"party_alive":         {"jack": true},
	"choices_log":         [],
	"canon_vars":          {},
	"lore_tokens_pending": []
}
var _title_root: Node = null
var _child_scene: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
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
	_run_state = {
		"chapter":             1,
		"class_focus":         "",
		"rafaton_disposition": 0,
		"workings_completed":  [],
		"corrections_found":   [],
		"party_disposition":   {},
		"party_members":       ["jack"],
		"party_alive":         {"jack": true},
		"choices_log":         [],
		"canon_vars":          {},
		"lore_tokens_pending": []
	}
	_open_chapter_1()


func _clear_current_scene() -> void:
	if _title_root != null and is_instance_valid(_title_root):
		_title_root.queue_free()
		_title_root = null
	if _child_scene != null and is_instance_valid(_child_scene):
		_child_scene.queue_free()
		_child_scene = null


func _build_title_screen() -> void:
	_clear_current_scene()

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	# CRT scanlines
	for y in range(0, 720, 2):
		var scanline := ColorRect.new()
		scanline.color = Color(0.0, 0.0, 0.0, 0.15)
		scanline.set_anchors_preset(Control.PRESET_TOP_WIDE)
		scanline.position.y = y
		scanline.size = Vector2(2000, 1)
		_title_root.add_child(scanline)

	# Top HUD band
	var hud_top := ColorRect.new()
	hud_top.color = C_GRAY
	hud_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	hud_top.offset_top = 0
	hud_top.offset_bottom = 24
	_title_root.add_child(hud_top)

	var hud_top_text := Label.new()
	hud_top_text.text = "ASTRO-CORTEX SOFTWARE · CULVER CITY CA · REV 2"
	hud_top_text.set_anchors_preset(Control.PRESET_TOP_LEFT)
	hud_top_text.position = Vector2(12, 6)
	hud_top_text.add_theme_font_size_override("font_size", 10)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	_title_root.add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "MARCH 1985"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-140, 6)
	hud_top_right.add_theme_font_size_override("font_size", 10)
	hud_top_right.add_theme_color_override("font_color", C_AMBER)
	_title_root.add_child(hud_top_right)

	# Center panel
	var panel := ColorRect.new()
	panel.color = C_CORTEX
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -340
	panel.offset_right = 340
	panel.offset_top = -140
	panel.offset_bottom = 260
	_title_root.add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = -120
	v.offset_bottom = 240
	v.add_theme_constant_override("separation", 14)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "THE EARTHMAN CHRONICLES"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 26)
	title.add_theme_color_override("font_color", C_AMBER)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", ""))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 12)
	subtitle.add_theme_color_override("font_color", C_CREAM)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "%s · %s · %d" % [
		String(shelf.get("publisher", "")),
		String(shelf.get("publisher_locale", "")),
		int(shelf.get("release_year", 0))
	]
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 10)
	meta.add_theme_color_override("font_color", C_WHITE)
	v.add_child(meta)

	var hidden_status := Label.new()
	hidden_status.text = "· A LOST WORK · ADAPTED · MARCH 1985 ·"
	hidden_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hidden_status.add_theme_font_size_override("font_size", 10)
	hidden_status.add_theme_color_override("font_color", C_RED)
	v.add_child(hidden_status)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep)

	# Menu
	var new_game_btn := Button.new()
	new_game_btn.text = "  NEW GAME  "
	new_game_btn.add_theme_font_size_override("font_size", 13)
	new_game_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_game_btn)

	if _has_save():
		var continue_btn := Button.new()
		continue_btn.text = "  CONTINUE  "
		continue_btn.add_theme_font_size_override("font_size", 13)
		continue_btn.pressed.connect(_on_continue_pressed)
		v.add_child(continue_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var status_label := Label.new()
	status_label.text = "· Chapters 1-2 playable · Chapters 3-6 authored in data · pending ·"
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.add_theme_font_size_override("font_size", 9)
	status_label.add_theme_color_override("font_color", C_GREEN)
	v.add_child(status_label)


func _has_save() -> bool:
	if not FileAccess.file_exists(SAVE_PATH): return false
	return int(_run_state.get("chapter", 0)) >= 1 and String(_run_state.get("class_focus", "")) != ""


func _on_continue_pressed() -> void:
	# Continue routes based on saved chapter
	var ch: int = int(_run_state.get("chapter", 1))
	match ch:
		1: _open_chapter_1()
		2, 3, 4, 5, 6: _open_chapter_2()
		_: _open_chapter_1()


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


func _open_chapter_1() -> void:
	_clear_current_scene()
	_child_scene = load(CH1_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_child_back)
	_child_scene.chapter_complete.connect(_on_chapter_1_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_chapter_1_complete(state: Dictionary) -> void:
	_run_state = state
	_run_state["chapter"] = 2
	_save_state()
	# Auto-advance to Chapter 2
	_open_chapter_2()


func _open_chapter_2() -> void:
	_clear_current_scene()
	_child_scene = load(CH2_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_child_back)
	_child_scene.chapter_complete.connect(_on_chapter_2_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_chapter_2_complete(state: Dictionary) -> void:
	_run_state = state
	# Ch 2 ends · Chapter 3 (Talikan) is a follow-up commit
	_save_state()
	# Return to title so player sees CONTINUE and current progress
	_build_title_screen()


func _on_child_back() -> void:
	# Save whatever state the child collected before returning
	_save_state()
	_build_title_screen()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
