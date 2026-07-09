extends Control
## Fey Faire · run controller.
##
## Flow:
##   1. Title screen (this scene, on _ready) · NEW GAME / CONTINUE
##      / back to shelf
##   2. NEW GAME · boot questionnaire (FeyFaireQuestionnaire) · 11
##      questions · answers merged into _run_state.questionnaire
##   3. Questionnaire completes · load FeyFaireGate with state
##   4. Gate is currently a text-forward vignette · will grow into
##      the first-person midway renderer in a later commit
##
## Save file: user://fey_faire.save.json
## Contains: questionnaire answers, court alignments, recruited feys,
## keepsakes, promises, memory-mirror state.  Scaffold pass only
## persists questionnaire answers · everything else authored empty.
##
## Signals · matches Pirate Summer / Estuary 3 pattern:
##   quit_to_shelf · caller (SlowstockBoot) reopens shelf
##   finished(canon_vars, lore_tokens) · caller merges into
##     GauntletState + reopens shelf
##
## F4-compliant via add_to_group("ui").

signal quit_to_shelf
signal finished(canon_vars: Dictionary, lore_tokens: Array)

const MANIFEST_PATH := "res://resources/games/vol7/fey_faire/manifest.json"
const SAVE_PATH     := "user://fey_faire.save.json"
const QUESTIONNAIRE_SCENE := "res://scenes/games/fey_faire/FeyFaireQuestionnaire.tscn"
const GATE_SCENE          := "res://scenes/games/fey_faire/FeyFaireGate.tscn"

# Rocha's title-card palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)
const C_DEEP      := Color(0.455, 0.157, 0.282, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)

var _manifest: Dictionary = {}
var _run_state: Dictionary = {
	"questionnaire": {},         # answers keyed by storage id
	"night":         1,           # 1..6
	"court_seelie":  0,
	"court_unseelie":0,
	"court_wildfey": 0,
	"recruited_feys":[],
	"keepsakes":     [],
	"promises":      [],
	"memories_lost": 0,           # 0..6
	"canon_vars":    {},
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


# Matches Estuary3Host / PirateSummerHost signature so SlowstockBoot
# can call it uniformly.  manager_mode ignored · Fey Faire has no
# analogous mode.
func start_new_run(_manager_mode: bool = false) -> void:
	_run_state = {
		"questionnaire": {},
		"night":         1,
		"court_seelie":  0,
		"court_unseelie":0,
		"court_wildfey": 0,
		"recruited_feys":[],
		"keepsakes":     [],
		"promises":      [],
		"memories_lost": 0,
		"canon_vars":    {},
		"lore_tokens_pending": []
	}
	_open_questionnaire()


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

	# Cream + old rose horizontal bands
	var band_cream := ColorRect.new()
	band_cream.color = C_CREAM
	band_cream.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band_cream.offset_top = 0
	band_cream.offset_bottom = 200
	_title_root.add_child(band_cream)

	var band_rose := ColorRect.new()
	band_rose.color = C_ROSE
	band_rose.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	band_rose.offset_top = 200
	band_rose.offset_bottom = 380
	_title_root.add_child(band_rose)

	# Mauve tent-stripe hint
	for x in range(80, 1280, 100):
		var stripe := ColorRect.new()
		stripe.color = C_MAUVE
		stripe.set_anchors_preset(Control.PRESET_TOP_LEFT)
		stripe.position = Vector2(x, 60)
		stripe.size = Vector2(8, 320)
		_title_root.add_child(stripe)

	# Center dark plum panel
	var panel := ColorRect.new()
	panel.color = C_DEEP
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.offset_left = -340
	panel.offset_right = 340
	panel.offset_top = -120
	panel.offset_bottom = 260
	_title_root.add_child(panel)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.offset_left = -320
	v.offset_right = 320
	v.offset_top = -100
	v.offset_bottom = 240
	v.add_theme_constant_override("separation", 14)
	_title_root.add_child(v)

	var shelf: Dictionary = _manifest.get("shelf", {})

	var title := Label.new()
	title.text = String(shelf.get("label_title", "FEY FAIRE"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 28)
	title.add_theme_color_override("font_color", C_GOLD)
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
	meta.add_theme_color_override("font_color", C_ROSE)
	v.add_child(meta)

	var sep := Control.new()
	sep.custom_minimum_size = Vector2(0, 20)
	v.add_child(sep)

	# Menu
	var menu := VBoxContainer.new()
	menu.alignment = BoxContainer.ALIGNMENT_CENTER
	menu.add_theme_constant_override("separation", 6)
	v.add_child(menu)

	var new_game_btn := Button.new()
	new_game_btn.text = "  NEW GAME  "
	new_game_btn.add_theme_font_size_override("font_size", 13)
	new_game_btn.pressed.connect(func() -> void: start_new_run(false))
	menu.add_child(new_game_btn)

	if _has_save():
		var continue_btn := Button.new()
		continue_btn.text = "  CONTINUE  "
		continue_btn.add_theme_font_size_override("font_size", 13)
		continue_btn.pressed.connect(_on_continue_pressed)
		menu.add_child(continue_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back to shelf  "
	back_btn.pressed.connect(_on_back_to_shelf)
	menu.add_child(back_btn)

	var status_label := Label.new()
	status_label.text = "· scaffold pass · questionnaire → Gate playable · midway rendering pending ·"
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status_label.add_theme_font_size_override("font_size", 9)
	status_label.add_theme_color_override("font_color", C_GOLD_DIM)
	v.add_child(status_label)


func _has_save() -> bool:
	if not FileAccess.file_exists(SAVE_PATH): return false
	var q: Dictionary = _run_state.get("questionnaire", {})
	return not q.is_empty()


func _on_continue_pressed() -> void:
	# For the scaffold, continue re-enters Gate with the saved state
	_open_gate()


func _on_back_to_shelf() -> void:
	quit_to_shelf.emit()


func _open_questionnaire() -> void:
	_clear_current_scene()
	_child_scene = load(QUESTIONNAIRE_SCENE).instantiate()
	_child_scene.finished.connect(_on_questionnaire_finished)
	_child_scene.cancelled.connect(_on_questionnaire_cancelled)
	add_child(_child_scene)


func _on_questionnaire_finished(answers: Dictionary) -> void:
	_run_state["questionnaire"] = answers
	# Grant the boot inventory keepsake · scaffold: just record it
	var kp := String(answers.get("_granted_keepsake", ""))
	if kp != "":
		var arr: Array = _run_state.get("keepsakes", [])
		if not arr.has(kp): arr.append(kp)
		_run_state["keepsakes"] = arr
	_save_state()
	_open_gate()


func _on_questionnaire_cancelled() -> void:
	_build_title_screen()


func _open_gate() -> void:
	_clear_current_scene()
	_child_scene = load(GATE_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_gate_quit)
	add_child(_child_scene)
	# Pass state via boot(state) · matches Pirate Summer's callee shape
	if _child_scene.has_method("boot"):
		var state_for_gate: Dictionary = _run_state.get("questionnaire", {}).duplicate()
		state_for_gate["_run"] = _run_state
		_child_scene.call("boot", state_for_gate)


func _on_gate_quit() -> void:
	# For the scaffold, gate BACK returns to the title screen (not
	# directly to shelf) so the player can see CONTINUE.
	_build_title_screen()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			# Only the title screen escapes to the shelf.  Child scenes
			# handle their own escape.
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
