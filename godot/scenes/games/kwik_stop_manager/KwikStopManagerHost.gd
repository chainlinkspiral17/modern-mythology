extends Control
## KWIK STOP MANAGER · run controller · RANCH, 2002.
##
## The studio's debut and the manager-sim subgenre's first
## mainstream hit · built by the two designers who left
## Oneironautics over Estuary 1.  Structurally it IS Estuary 1
## with the score attached, and it knows it, and it puts the
## score top-right in gold to prove the point.
##
## Save file: user://kwik_stop_manager.save.json
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/kwik_stop_manager/manifest.json"
const WEEKS_PATH    := "res://resources/games/vol7/kwik_stop_manager/weeks.json"
const SAVE_PATH     := "user://kwik_stop_manager.save.json"
const WEEK_SCENE    := "res://scenes/games/kwik_stop_manager/KsmWeek.tscn"
const HERO_DIR      := "res://resources/games/vol7/kwik_stop_manager/hero_images/"

const C_CREAM := Color("f4f0e8")
const C_RED   := Color("c8442c")
const C_DARK  := Color("2a3038")
const C_GOLD  := Color("f0c040")
const C_SAGE  := Color("6a7a72")

var _manifest: Dictionary = {}
var _weeks_def: Dictionary = {}
var _run_state: Dictionary = {}
var _title_root: Node = null
var _child_scene: Node = null
var _ending_root: Node = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	SlowstickLook.apply(self, "ranch")
	# Studio control chrome (mirrors the look preset) — cascades
	# to every child scene; see StickTheme.gd.
	theme = preload("res://scenes/games/StickTheme.gd").make("ranch")
	_run_state = _fresh_state([])
	_load_data()
	_load_save_if_present()
	_build_title_screen()


func _fresh_state(summers: Array) -> Dictionary:
	var start: Dictionary = _weeks_def.get("start", {"cash": 300, "stock": 5, "morale": 5, "landlord": 5})
	return {
		"week_n":    1,
		"cash":      int(start.get("cash", 300)),
		"stock":     int(start.get("stock", 5)),
		"morale":    int(start.get("morale", 5)),
		"landlord":  int(start.get("landlord", 5)),
		"last_crew": [],
		"events_done": [],
		"staff_gone": [],
		"robbery_choice": "",
		"summers":   summers,
		"canon_vars": {},
		"lore_tokens_pending": []
	}


func _load_data() -> void:
	for pair in [[MANIFEST_PATH, "m"], [WEEKS_PATH, "w"]]:
		if not FileAccess.file_exists(String(pair[0])): continue
		var f := FileAccess.open(String(pair[0]), FileAccess.READ)
		var parsed: Variant = JSON.parse_string(f.get_as_text())
		f.close()
		if parsed is Dictionary:
			if String(pair[1]) == "m": _manifest = parsed
			else: _weeks_def = parsed


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
	_run_state = _fresh_state(_run_state.get("summers", []))
	_open_week()


func _clear_current_scene() -> void:
	for n in [_title_root, _child_scene, _ending_root]:
		if n != null and is_instance_valid(n):
			n.queue_free()
	_title_root = null
	_child_scene = null
	_ending_root = null


func _play_bgm(path: String) -> void:
	var am := get_node_or_null("/root/AudioMgr")
	if am != null and am.has_method("request_scene_bgm"):
		am.request_scene_bgm(path)


# ─── Title ───────────────────────────────────────────────────────

func _build_title_screen() -> void:
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/ksm/highway_summer.wav")

	_title_root = Control.new()
	_title_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_title_root)

	var bg := ColorRect.new()
	bg.color = C_CREAM
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title_root.add_child(bg)

	var band := ColorRect.new()
	band.color = C_RED
	band.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band.offset_bottom = 48
	_title_root.add_child(band)

	var ranch_lbl := Label.new()
	ranch_lbl.text = "RANCH · SAN FRANCISCO CA · SLOWBOX REV 2 · OUR FIRST GAME"
	ranch_lbl.position = Vector2(16, 12)
	ranch_lbl.add_theme_font_size_override("font_size", 13)
	ranch_lbl.add_theme_color_override("font_color", C_CREAM)
	_title_root.add_child(ranch_lbl)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "kwik_stop_101.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(800, 450))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -400
		tex_rect.offset_right = 400
		tex_rect.offset_top = -300
		tex_rect.offset_bottom = 150
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_title_root.add_child(tex_rect)

	# Title motion — studio character (menu motion playbook).
	preload("res://scenes/games/TitleMotion.gd").attach(_title_root, "ranch")

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -340
	v.offset_right = 340
	v.offset_top = 140
	v.offset_bottom = 350
	v.add_theme_constant_override("separation", 10)
	_title_root.add_child(v)

	var title := Label.new()
	title.text = "KWIK STOP MANAGER"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", C_RED)
	v.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "run the counter, watch the summer · twelve weeks · nine employees · one landlord"
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", C_DARK)
	v.add_child(subtitle)

	var new_btn := Button.new()
	new_btn.text = "  CLOCK IN · SUMMER 1998  "
	new_btn.add_theme_font_size_override("font_size", 14)
	new_btn.pressed.connect(func() -> void: start_new_run(false))
	v.add_child(new_btn)

	if _has_save():
		var cont_btn := Button.new()
		cont_btn.text = "  CONTINUE · WEEK " + str(int(_run_state.get("week_n", 1))) + "  "
		cont_btn.add_theme_font_size_override("font_size", 14)
		cont_btn.pressed.connect(_open_week)
		v.add_child(cont_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.add_theme_font_size_override("font_size", 13)
	back_btn.pressed.connect(_on_back_to_shelf)
	v.add_child(back_btn)

	var summers: Array = _run_state.get("summers", [])
	if summers.size() > 0:
		var status := Label.new()
		status.text = "· summers managed: %d · best sign: %s ·" % [summers.size(), String(summers[-1])]
		status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		status.add_theme_font_size_override("font_size", 12)
		status.add_theme_color_override("font_color", C_SAGE)
		v.add_child(status)


func _has_save() -> bool:
	var n: int = int(_run_state.get("week_n", 1))
	return FileAccess.file_exists(SAVE_PATH) and n > 1 and n <= 12


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


# ─── Weeks ───────────────────────────────────────────────────────

func _open_week() -> void:
	_clear_current_scene()
	_child_scene = load(WEEK_SCENE).instantiate()
	_child_scene.quit.connect(_on_week_quit)
	_child_scene.week_over.connect(_on_week_over)
	_child_scene.summer_over.connect(_on_summer_over)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_week_quit() -> void:
	_save_state()
	_build_title_screen()


func _on_week_over(state: Dictionary) -> void:
	_run_state = state
	_save_state()
	_open_week()


# ─── The fall reopening ──────────────────────────────────────────

func _on_summer_over(state: Dictionary) -> void:
	_run_state = state
	_clear_current_scene()
	_play_bgm("res://assets/audio/bgm/ksm/reopening.wav")

	var cash: int = int(_run_state.get("cash", 0))
	var morale: int = int(_run_state.get("morale", 5))
	var landlord: int = int(_run_state.get("landlord", 5))
	var endings: Dictionary = _weeks_def.get("endings", {})
	# Landlord is a second, independent pressure axis · it no longer
	# just feeds the score (where cash could outweigh it). Burn the
	# landlord and you lose the LEASE, whatever the number says — so
	# "win the score" and "keep the store" can pull apart. Legibly
	# telegraphed in the weekly report once it drops to the danger band.
	var key := "evicted" if landlord <= 1 \
		else ("crew" if morale >= 7 else ("corporate" if cash >= 900 else "shuttered"))
	var e: Dictionary = endings.get(key, {})
	_run_state["ending"] = key

	_ending_root = Control.new()
	_ending_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_ending_root)

	var bg := ColorRect.new()
	bg.color = C_DARK
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_ending_root.add_child(bg)

	var hero := HeroImage.new()
	if hero.load_from(HERO_DIR + "the_reopening.json"):
		var tex_rect := TextureRect.new()
		tex_rect.texture = hero.texture(Vector2i(640, 360))
		tex_rect.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		tex_rect.offset_left = -320
		tex_rect.offset_right = 320
		tex_rect.offset_top = -310
		tex_rect.offset_bottom = 50
		tex_rect.stretch_mode = TextureRect.STRETCH_KEEP
		_ending_root.add_child(tex_rect)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -400
	v.offset_right = 400
	v.offset_top = 70
	v.offset_bottom = 340
	v.add_theme_constant_override("separation", 12)
	_ending_root.add_child(v)

	var hdr := Label.new()
	hdr.text = "· THE FALL REOPENING · %s ·" % String(e.get("title", key.to_upper()))
	hdr.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hdr.add_theme_font_size_override("font_size", 18)
	hdr.add_theme_color_override("font_color", C_GOLD)
	v.add_child(hdr)

	var body := Label.new()
	body.text = String(e.get("text", ""))
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_theme_font_size_override("font_size", 14)
	body.add_theme_color_override("font_color", C_CREAM)
	v.add_child(body)

	var score := Label.new()
	score.text = "FINAL SCORE · %d" % (cash + morale * 40 + int(_run_state.get("landlord", 5)) * 25 + int(_run_state.get("stock", 0)) * 10)
	score.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score.add_theme_font_size_override("font_size", 20)
	score.add_theme_color_override("font_color", C_GOLD)
	v.add_child(score)

	var done := Button.new()
	done.text = "  · hang up the vest ·  "
	done.add_theme_font_size_override("font_size", 14)
	done.pressed.connect(func() -> void: _finish_run(key))
	v.add_child(done)


func _finish_run(ending: String) -> void:
	var tokens: Array = _run_state.get("lore_tokens_pending", [])
	for t in ["kwik_stop_manager_finished", "the_first_manager_sim", "olafs_taste_confirmed",
			"ksm_ending_" + ending]:
		if not tokens.has(t):
			tokens.append(t)
	_run_state["lore_tokens_pending"] = tokens
	OneironauticsTokens.add_many(tokens)
	var canon: Dictionary = _run_state.get("canon_vars", {})
	canon["ksm_ending"] = ending
	_run_state["canon_vars"] = canon
	var summers: Array = _run_state.get("summers", [])
	summers.append(ending)
	_run_state["summers"] = summers
	_run_state["week_n"] = 1
	_save_state()
	finished.emit(canon, tokens)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
