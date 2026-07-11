extends Control
## BASILICA OF WIRES · run controller · Astro-Cortex Software, 1987.
##
## The studio's last stick before folding.  Written by J.F. in the
## two years after A. Rocha left for Portland.  Fewer than 900
## copies pressed.  Olaf never found one · the shelf carries his
## hand-labeled empty sleeve, and the cart itself only exists here
## after the Vol 7 present-day auction beat (SlowstockBoot owns
## that; this host assumes the cart is in the machine).
##
## Save file: user://basilica_of_wires.save.json
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/basilica_of_wires/manifest.json"
const LEVELS_PATH   := "res://resources/games/vol7/basilica_of_wires/levels.json"
const SAVE_PATH     := "user://basilica_of_wires.save.json"
const CRAWL_SCENE   := "res://scenes/games/basilica_of_wires/BasilicaCrawl.tscn"
const HERO_DIR      := "res://resources/games/vol7/basilica_of_wires/hero_images/"

const C_DARK  := Color("000000")
const C_CYAN  := Color("38c8d8")
const C_WHITE := Color("e8f4f8")
const C_AMBER := Color("e8a830")

var _manifest: Dictionary = {}
var _door_lines: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null
var _ending_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "astro_cortex")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("astro_cortex")
	_run_state = _fresh_state(0)
	_load_data()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state(descents: int) -> Dictionary:
	return {
		"level_i":    0,
		"freq":       440.0,
		"coherence":  9.0,
		"message_room_reached": false,
		"descents":   descents,
		"canon_vars": {},
		"lore_tokens_pending": []
	}


func _load_data() -> void:
	for pair in [[MANIFEST_PATH, "m"], [LEVELS_PATH, "l"]]:
		if not FileAccess.file_exists(String(pair[0])): continue
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "m": _manifest = parsed
			else: _door_lines = (parsed as Dictionary).get("door_lines", {})


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
	_run_state = _fresh_state(int(_run_state.get("descents", 0)))
	_open_crawl()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene, _ending_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null
	_ending_root = null


# ─── Title · the instrument, waiting ─────────────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_scene_bgm"):
		am.stop_scene_bgm()   # silence, then the hum

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "master_breaker.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -310
		tex_rect.offset_bottom = 140
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	# Title motion — studio character (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "astro_cortex")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = 130
	v.offset_bottom = 350
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var title := Label.new()
	title.text = "BASILICA OF WIRES"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 36)
	title.add_theme_color_override("font_color", C_CYAN)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "ASTRO-CORTEX SOFTWARE · 1987 · the transmitter under the mountain"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", C_WHITE)
	v.add_child(subtitle)

	var new_btn := Button.new()
	new_btn.text = "  DESCEND  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · LEVEL " + str(int(_run_state.get("level_i", 0)) + 1) + "  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(_open_crawl)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var descents: int = int(_run_state.get("descents", 0))
	if descents > 0:
		var status := Label.new()
		status.text = "· descents: %d · the instrument remembers ·" % descents
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_AMBER)
		v.add_child(status)


func _has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH) and int(_run_state.get("level_i", 0)) > 0


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── The descent ─────────────────────────────────────────────────

func _open_crawl() -> void:
	_clear_current_scene()
	_child_scene = load(CRAWL_SCENE).instantiate()
	_child_scene.quit.connect(_on_crawl_quit)
	_child_scene.descent_over.connect(_on_descent_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_crawl_quit() -> void:
	if _child_scene != null and _child_scene.get("_level_i") != null:
		_run_state["level_i"] = int(_child_scene.get("_level_i"))
		_run_state["freq"] = float(_child_scene.get("_freq"))
		_run_state["coherence"] = float(_child_scene.get("_coherence"))
	_save_state()
	_build_title_screen()


func _on_descent_over(state: Dictionary) -> void:
	_run_state = state
	_show_door()


# ─── The mountain door · one ending, three lines ─────────────────

func _show_door() -> void:
	_clear_current_scene()

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	var coherence: float = float(_run_state.get("coherence", 9.0))
	var key := "high" if coherence >= 7.0 else ("mid" if coherence >= 4.0 else "low")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -380
	v.offset_right = 380
	v.offset_top = -120
	v.offset_bottom = 160
	v.add_theme_constant_override("separation", 16)
	_ending_root.add_child(v)

	var hdr := Label.new()
	hdr.text = "· THE MOUNTAIN DOOR ·"
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 18)
	hdr.add_theme_color_override("font_color", C_AMBER)
	v.add_child(hdr)

	var body := Label.new()
	body.text = String(_door_lines.get(key, ""))
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", C_WHITE)
	v.add_child(body)

	if bool(_run_state.get("message_room_reached", false)):
		var mr := Label.new()
		mr.text = "the teletype page is folded in your coat. STATUS: carried."
		mr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		mr.add_theme_font_size_override("font_size", 13)
		mr.add_theme_color_override("font_color", C_AMBER)
		v.add_child(mr)

	var done := Button.new()
	done.text = "  · into the daylight ·  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(_finish_run)
	v.add_child(done)


func _finish_run() -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("basilica_of_wires_finished"):
		tokens.append("basilica_of_wires_finished")
	if bool(_run_state.get("message_room_reached", false)) \
			and not tokens.has("basilica_message_room_reached"):
		tokens.append("basilica_message_room_reached")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["basilica_message_room"] = bool(_run_state.get("message_room_reached", false))
	_run_state["canon_vars"] = canon
	_run_state["descents"] = int(_run_state.get("descents", 0)) + 1
	_run_state["level_i"] = 0
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
