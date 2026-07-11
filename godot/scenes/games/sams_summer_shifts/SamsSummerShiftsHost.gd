extends Control
## Sam's Summer Shifts · run controller · RANCH, 2003.
##
## The in-fiction "official" Sam · sequel to Kwik Stop Manager ·
## twelve weeks at the Hi-Way 30 Stop-N-Go outside Clatskanie, the
## summer after KSM.  Playable v1 is a twelve-week beat-sim: one
## scripted shift-beat per week, three meters (TILL · REGULARS ·
## NERVE), the week-6 armed-robbery anchor, three endings.
##
## Save file: user://sams_summer_shifts.save.json
##
## Signals · matches the uniform slowstock host contract:
##   quit_to_shelf · caller (SlowstockBoot) reopens shelf
##   finished(canon_vars, lore_tokens)
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/sams_summer_shifts/manifest.json"
const SAVE_PATH     := "user://sams_summer_shifts.save.json"
const LOOP_SCENE    := "res://scenes/games/sams_summer_shifts/SummerLoop.tscn"

# RANCH palette · red band + cream + summer yellow · nothing like
# Oneironautics' moody blues on purpose
const C_BG      := Color(0.055, 0.055, 0.055, 1.0)
const C_RED     := Color(0.910, 0.220, 0.282, 1.0)
const C_CREAM   := Color(0.957, 0.941, 0.910, 1.0)
const C_YELLOW  := Color(0.910, 0.784, 0.251, 1.0)
const C_GRAY    := Color(0.251, 0.251, 0.251, 1.0)
const C_DIM     := Color(0.60, 0.56, 0.50, 1.0)

var _manifest: Dictionary = {}
var _run_state: Dictionary = {
	"week":     1,      # 1..12
	"till":     3,      # 0..10 · drawer accuracy / register craft
	"regulars": 3,      # 0..10 · standing with the morning regulars
	"nerve":    3,      # 0..10 · Sam's steadiness · 0 = walks off
	"choices_log": [],
	"endings_seen": [],
	"canon_vars": {},
	"lore_tokens_pending": []
}
var _title_root: Node = null
var _child_scene: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "ranch")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("ranch")
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
	var seen: Array = _run_state.get("endings_seen", [])
	_run_state = {
		"week":     1,
		"till":     3,
		"regulars": 3,
		"nerve":    3,
		"choices_log": [],
		"endings_seen": seen,
		"canon_vars": {},
		"lore_tokens_pending": []
	}
	_open_loop()


func _clear_current_scene() -> void:
	if _title_root != null and is_instance_valid(_title_root):
		_title_root.queue_free()
		_title_root = null
	if _child_scene != null and is_instance_valid(_child_scene):
		_child_scene.queue_free()
		_child_scene = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("play_bgm"):
		am.play_bgm(path)


func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/sss/hiway_30.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	# RANCH red bands top and bottom · house style
	var band_top := ColorRect.new()
	band_top.color = C_RED
	band_top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band_top.offset_top = 0
	band_top.offset_bottom = 56
	_title_root.add_child(band_top)

	var ranch_lbl := Label.new()
	ranch_lbl.text = "RANCH · SAN FRANCISCO CA · SLOWBOX REV 2"
	ranch_lbl.set_anchors_preset(Control.PRESET_TOP_LEFT)
	ranch_lbl.position = Vector2(16, 18)
	ranch_lbl.add_theme_font_size_override("font_size", 15)
	ranch_lbl.add_theme_color_override("font_color", C_BG)
	_title_root.add_child(ranch_lbl)

	var band_bot := ColorRect.new()
	band_bot.color = C_RED
	band_bot.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	band_bot.offset_top = -32
	band_bot.offset_bottom = 0
	_title_root.add_child(band_bot)

	# Summer-yellow accent stripe
	var stripe := ColorRect.new()
	stripe.color = C_YELLOW
	stripe.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	stripe.offset_top = 56
	stripe.offset_bottom = 64
	_title_root.add_child(stripe)

	# HeroImage · the Stop-N-Go at golden hour
	var hero := HeroImage.new()
	if hero.load_from("res://resources/games/vol7/sams_summer_shifts/hero_images/stop_n_go.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -300
		tex_rect.offset_bottom = -120
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	# Title motion — studio character (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "ranch")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = -90
	v.offset_bottom = 250
	v.add_theme_constant_override("separation", 12)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "SAM'S SUMMER SHIFTS"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 30)
	title.add_theme_color_override("font_color", C_CREAM)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = String(shelf.get("label_subtitle", "twelve weeks · one register · keep your head"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 16)
	subtitle.add_theme_color_override("font_color", C_YELLOW)
	v.add_child(subtitle)

	var meta := Label.new()
	meta.text = "RANCH · 2003 · the official Sam"
	# Kwik Stop Manager cross-token · the sequel remembers your sign.
	if OneironauticsTokens.has("ksm_ending_crew"):
		meta.text += "  ·  last summer, the crew kept the store"
	elif OneironauticsTokens.has("ksm_ending_corporate"):
		meta.text += "  ·  last summer, the sign got new letters"
	elif OneironauticsTokens.has("ksm_ending_shuttered"):
		meta.text += "  ·  last summer, the store never reopened"
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.add_theme_font_size_override("font_size", 14)
	meta.add_theme_color_override("font_color", C_DIM)
	v.add_child(meta)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 16)
	v.add_child(sep)

	var new_btn := Button.new()
	new_btn.text = "  CLOCK IN · NEW SUMMER  "
	new_btn.add_theme_font_size_override("font_size", 17)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · WEEK " + str(int(_run_state.get("week", 1))) + "  "
		cont_btn.add_theme_font_size_override("font_size", 17)
		cont_btn.pressed.connect(_open_loop)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var seen: Array = _run_state.get("endings_seen", [])
	var status := Label.new()
	status.text = "· twelve weeks · three endings · " + str(seen.size()) + "/3 seen ·"
	status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status.add_theme_font_size_override("font_size", 13)
	status.add_theme_color_override("font_color", C_DIM)
	v.add_child(status)


func _has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH) and int(_run_state.get("week", 1)) > 1


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


func _open_loop() -> void:
	_clear_current_scene()
	_child_scene = load(LOOP_SCENE).instantiate()
	_child_scene.quit.connect(_on_loop_quit)
	_child_scene.week_complete.connect(_on_week_complete)
	_child_scene.summer_over.connect(_on_summer_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_loop_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_week_complete(state: Dictionary) -> void:
	_run_state = state
	_save_state()


func _on_summer_over(state: Dictionary, ending_id: String) -> void:
	_run_state = state
	var seen: Array = _run_state.get("endings_seen", [])
	if not seen.has(ending_id):
		seen.append(ending_id)
	_run_state["endings_seen"] = seen
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	if not tokens.has("sams_summer_shifts_finished"):
		tokens.append("sams_summer_shifts_finished")
	if not tokens.has("sam_vs_sam_rivalry_understood"):
		tokens.append("sam_vs_sam_rivalry_understood")
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["sams_summer_shifts_ending"] = ending_id
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
