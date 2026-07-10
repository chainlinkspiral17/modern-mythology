extends Control
## RIFFMASTER MELODY CLUB · run controller · PDP Toys, 1991.
##
## The kids'-synth company's own slowstick · twelve club meetings
## that teach the 3-oscillator voice the whole catalog is scored
## with.  Marc Ostrom moonlighted on it, uncredited.  The Rosetta
## stick.
##
## The title music is the save file: a loop recorded by a
## seven-year-old in 1991 (Tem's parent · authored content ·
## nobody in Vol 7 comments on it) — until the player records
## their own OPEN MIC loop, which becomes the title music of THIS
## CARTRIDGE forever after.
##
## Save file: user://riffmaster_melody_club.save.json
##
## Signals · uniform slowstock host contract:
##   quit_to_shelf · finished(canon_vars, lore_tokens)
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/riffmaster_melody_club/manifest.json"
const HEIRLOOM_PATH := "res://resources/games/vol7/riffmaster_melody_club/heirloom_loop.json"
const SAVE_PATH     := "user://riffmaster_melody_club.save.json"
const MEETING_SCENE := "res://scenes/games/riffmaster_melody_club/RiffmasterMeeting.tscn"
const HERO_DIR      := "res://resources/games/vol7/riffmaster_melody_club/hero_images/"

const C_WHITE  := Color("f4f4f0")
const C_RED    := Color("e83030")
const C_YELLOW := Color("f8c820")
const C_BLUE   := Color("2870d8")
const C_GREEN  := Color("30a848")
const C_KEY    := Color("282828")

var _manifest: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null
var _loop_player: RiffmasterLoopPlayer = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "pdp_toys")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("pdp_toys")
	_run_state = _fresh_state({}, [])
	_load_manifest()
	_load_save_if_present()
	_loop_player = RiffmasterLoopPlayer.new()
	add_child(_loop_player)
	_build_title_screen()


func _fresh_state(open_mic: Dictionary, meetings_attended: Array) -> Dictionary:
	return {
		"meeting_n":    1,
		"meetings_attended": meetings_attended,
		"open_mic_loop": open_mic,
		"canon_vars":   {},
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
	# A new run keeps the OPEN MIC loop · it is the cartridge's
	# title music forever after.  The heirloom is never touched.
	var open_mic: Dictionary = _run_state.get("open_mic_loop", {})
	_run_state = _fresh_state(open_mic, _run_state.get("meetings_attended", []))
	_open_meeting()


func _title_loop() -> Dictionary:
	var mine: Dictionary = _run_state.get("open_mic_loop", {})
	if not (mine.get("events", []) as Array).is_empty():
		return mine
	if FileAccess.file_exists(HEIRLOOM_PATH):
		var f := FileAccess.open(HEIRLOOM_PATH, FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			return parsed
	return {}


func _clear_current_scene() -> void:
	if _loop_player != null:
		_loop_player.stop()
	for n in [_title_root, _child_scene]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null


# ─── Title · white, bright, the loop playing ─────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	# Quiet whatever BGM the shelf left running · the save file IS
	# the title music here.
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("stop_bgm"):
		am.stop_bgm()
	var title_loop := _title_loop()
	if not title_loop.is_empty():
		_loop_player.play_loop(title_loop, true, 2.2)

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_WHITE
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "clubhouse_couch.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -320
		tex_rect.offset_bottom = 130
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = 60
	v.offset_bottom = 340
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "RIFFMASTER MELODY CLUB"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", C_RED)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "PDP TOYS · 1991 · no wrong notes. (some notes are jazz.)"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", C_BLUE)
	v.add_child(subtitle)

	# Whose loop is playing right now · the quietest heirloom
	var mine: Dictionary = _run_state.get("open_mic_loop", {})
	var loop_lbl := Label.new()
	if not (mine.get("events", []) as Array).is_empty():
		loop_lbl.text = "♪ now playing · YOUR open mic loop · side B"
	else:
		loop_lbl.text = "♪ now playing · SIDE A · four bars · recorded 1991, age seven"
	loop_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	loop_lbl.add_theme_font_size_override("font_size", 12)
	loop_lbl.add_theme_color_override("font_color", C_GREEN)
	v.add_child(loop_lbl)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 8)
	v.add_child(sep)

	var new_btn := Button.new()
	new_btn.text = "  JOIN THE CLUB · MEETING ONE  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · MEETING " + str(int(_run_state.get("meeting_n", 1))) + "  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(_open_meeting)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)


func _has_save() -> bool:
	var n: int = int(_run_state.get("meeting_n", 1))
	return FileAccess.file_exists(SAVE_PATH) and n > 1 and n <= 12


func _on_back_to_shelf() -> void:
	if _loop_player != null:
		_loop_player.stop()
	quit_to_shelf.emit()


# ─── Meetings ────────────────────────────────────────────────────

func _open_meeting() -> void:
	_clear_current_scene()
	_child_scene = load(MEETING_SCENE).instantiate()
	_child_scene.quit.connect(_on_meeting_quit)
	_child_scene.meeting_over.connect(_on_meeting_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_meeting_quit() -> void:
	# The only fail state is quitting, and the club says goodbye
	# kindly even then · the save keeps their seat warm.
	_save_state()
	_build_title_screen()


func _on_meeting_over(state: Dictionary) -> void:
	_run_state = state
	var n: int = int(_run_state.get("meeting_n", 1))
	var attended: Array = _run_state.get("meetings_attended", [])
	if not attended.has(n):
		attended.append(n)
	_run_state["meetings_attended"] = attended
	if n >= 12:
		_finish_run()
		return
	_run_state["meeting_n"] = n + 1
	_save_state()
	_open_meeting()


func _finish_run() -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("riffmaster_finished"):
		tokens.append("riffmaster_finished")
	var mine: Dictionary = _run_state.get("open_mic_loop", {})
	if not (mine.get("events", []) as Array).is_empty() \
			and not tokens.has("riffmaster_open_mic_recorded"):
		tokens.append("riffmaster_open_mic_recorded")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["riffmaster_club_graduate"] = true
	_run_state["canon_vars"] = canon
	_run_state["meeting_n"] = 1
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
