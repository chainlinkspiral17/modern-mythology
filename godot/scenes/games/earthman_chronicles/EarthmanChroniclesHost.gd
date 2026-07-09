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
const CH3_SCENE     := "res://scenes/games/earthman_chronicles/EarthmanChapter3Talikan.tscn"
const CH4_SCENE     := "res://scenes/games/earthman_chronicles/EarthmanChapter4Mines.tscn"
const CH5_SCENE     := "res://scenes/games/earthman_chronicles/EarthmanChapter5Academy.tscn"
const CH6_SCENE     := "res://scenes/games/earthman_chronicles/EarthmanChapter6Finale.tscn"
const CODEX_SCENE   := "res://scenes/games/earthman_chronicles/EarthmanCodex.tscn"
const TALIKAN_SCENE := "res://scenes/games/earthman_chronicles/EarthmanTalikanHub.tscn"

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
	"shenin":              36,       # pocket money · Rafaton's ritual stipend converts
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
	SlowstickLook.apply(self, "astro_cortex")
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
		"shenin":              36,
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
	_play_bgm("res://assets/audio/bgm/em/pasadena_ritual.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)


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
	hud_top_text.add_theme_font_size_override("font_size", 14)
	hud_top_text.add_theme_color_override("font_color", C_AMBER)
	_title_root.add_child(hud_top_text)

	var hud_top_right := Label.new()
	hud_top_right.text = "MARCH 1985"
	hud_top_right.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	hud_top_right.position = Vector2(-140, 6)
	hud_top_right.add_theme_font_size_override("font_size", 14)
	hud_top_right.add_theme_color_override("font_color", C_AMBER)
	_title_root.add_child(hud_top_right)

	# HeroImage · Astro-Cortex title card · above the panel
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/earthman_chronicles/hero_images/title_cortex_logo.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -320
		tex_rect.offset_bottom = -160
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

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
	subtitle.add_theme_font_size_override("font_size", 16)
	subtitle.add_theme_color_override("font_color", C_CREAM)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "%s · %s · %d" % [
		String(shelf.get("publisher", "")),
		String(shelf.get("publisher_locale", "")),
		int(shelf.get("release_year", 0))
	]
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 14)
	meta.add_theme_color_override("font_color", C_WHITE)
	v.add_child(meta)

	var hidden_status := Label.new()
	hidden_status.text = "· A LOST WORK · ADAPTED · MARCH 1985 ·"
	hidden_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hidden_status.add_theme_font_size_override("font_size", 14)
	hidden_status.add_theme_color_override("font_color", C_RED)
	v.add_child(hidden_status)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 12)
	v.add_child(sep)

	# Menu
	var new_game_btn := Button.new()
	new_game_btn.text = "  NEW GAME  "
	new_game_btn.add_theme_font_size_override("font_size", 17)
	new_game_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_game_btn)

	if _has_save():
		var continue_btn := Button.new()
		continue_btn.text = "  CONTINUE  "
		continue_btn.add_theme_font_size_override("font_size", 17)
		continue_btn.pressed.connect(_on_continue_pressed)
		v.add_child(continue_btn)

		var codex_btn := Button.new()
		codex_btn.text = "  JACK'S CODEX  "
		codex_btn.add_theme_font_size_override("font_size", 16)
		codex_btn.pressed.connect(_open_codex)
		v.add_child(codex_btn)

		# Talikan is only meaningful once chapter 3+
		if int(_run_state.get("chapter", 1)) >= 3:
			var talikan_btn := Button.new()
			talikan_btn.text = "  REVISIT TALIKAN  "
			talikan_btn.add_theme_font_size_override("font_size", 16)
			talikan_btn.pressed.connect(_open_talikan)
			v.add_child(talikan_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var status_label := Label.new()
	status_label.text = "· all 6 chapters playable · 6 endings authored · THE CORRECTION requires the five findable corrections ·"
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.add_theme_font_size_override("font_size", 13)
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
		2: _open_chapter_2()
		3: _open_chapter_3()
		4: _open_chapter_4()
		5: _open_chapter_5()
		6: _open_chapter_6()
		_: _open_chapter_1()


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()

func _play_bgm(path: String) -> void:
	# AudioMgr crossfades and dedupes same-src calls · guard for
	# scene-tests that boot without the autoload.
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)



func _open_chapter_1() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/em/pasadena_ritual.wav")
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
	_play_bgm("res://assets/audio/bgm/em/parsa_dunes.wav")
	_child_scene = load(CH2_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_child_back)
	_child_scene.chapter_complete.connect(_on_chapter_2_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_chapter_2_complete(state: Dictionary) -> void:
	_run_state = state
	_run_state["chapter"] = 3
	_save_state()
	_open_chapter_3()


func _open_chapter_3() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/em/talikan_silver.wav")
	_child_scene = load(CH3_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_child_back)
	_child_scene.chapter_complete.connect(_on_chapter_3_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_chapter_3_complete(state: Dictionary) -> void:
	_run_state = state
	_run_state["chapter"] = 4
	_save_state()
	_open_chapter_4()


func _open_chapter_4() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/em/parsa_dunes.wav")
	_child_scene = load(CH4_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_child_back)
	_child_scene.chapter_complete.connect(_on_chapter_4_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_chapter_4_complete(state: Dictionary) -> void:
	_run_state = state
	_run_state["chapter"] = 5
	_save_state()
	_open_chapter_5()


func _open_chapter_5() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/em/pasadena_ritual.wav")
	_child_scene = load(CH5_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_child_back)
	_child_scene.chapter_complete.connect(_on_chapter_5_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_chapter_5_complete(state: Dictionary) -> void:
	_run_state = state
	_run_state["chapter"] = 6
	_save_state()
	_open_chapter_6()


func _open_chapter_6() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/em/talikan_silver.wav")
	_child_scene = load(CH6_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_child_back)
	_child_scene.chapter_complete.connect(_on_chapter_6_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_chapter_6_complete(state: Dictionary) -> void:
	_run_state = state
	_save_state()
	_build_title_screen()


func _open_codex() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/em/talikan_silver.wav")
	_child_scene = load(CODEX_SCENE).instantiate()
	_child_scene.quit.connect(_build_title_screen)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _open_talikan() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/em/talikan_silver.wav")
	_child_scene = load(TALIKAN_SCENE).instantiate()
	_child_scene.quit.connect(_on_talikan_quit)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_talikan_quit() -> void:
	# Persist any state changes from the hub (bought items, learned facts)
	_save_state()
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
