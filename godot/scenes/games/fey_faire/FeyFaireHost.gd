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
const NEGOTIATION_SCENE   := "res://scenes/games/fey_faire/FeyFaireNegotiation.tscn"
const TRAILER_SCENE       := "res://scenes/games/fey_faire/FeyFaireTrailer.tscn"
const MIDWAY_SCENE        := "res://scenes/games/fey_faire/FeyFaireMidway.tscn"
const BIG_TOP_SCENE       := "res://scenes/games/fey_faire/FeyFaireBigTop.tscn"
const COMBAT_SCENE        := "res://scenes/games/fey_faire/FeyFaireCombat.tscn"

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
	if _child_scene.has_signal("negotiate_with_fey"):
		_child_scene.negotiate_with_fey.connect(_open_negotiation)
	if _child_scene.has_signal("visit_trailer"):
		_child_scene.visit_trailer.connect(_open_trailer)
	if _child_scene.has_signal("enter_midway"):
		_child_scene.enter_midway.connect(_open_midway)
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


func _open_trailer() -> void:
	_clear_current_scene()
	_child_scene = load(TRAILER_SCENE).instantiate()
	_child_scene.quit.connect(_open_gate)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _open_midway() -> void:
	_clear_current_scene()
	_child_scene = load(MIDWAY_SCENE).instantiate()
	_child_scene.quit.connect(_on_midway_quit)
	if _child_scene.has_signal("negotiate_with_fey"):
		_child_scene.negotiate_with_fey.connect(_open_negotiation_from_midway)
	if _child_scene.has_signal("enter_big_top"):
		_child_scene.enter_big_top.connect(_open_big_top)
	if _child_scene.has_signal("rest_at_booth"):
		_child_scene.rest_at_booth.connect(_on_rest_at_booth)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _open_big_top() -> void:
	_clear_current_scene()
	_child_scene = load(BIG_TOP_SCENE).instantiate()
	_child_scene.quit.connect(_open_midway)
	_child_scene.finished.connect(_on_big_top_finished)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", _run_state)


func _on_big_top_finished(rewards: Dictionary) -> void:
	var kp_id: String = String(rewards.get("keepsake_id", ""))
	if kp_id != "":
		var kp_list: Array = _run_state.get("keepsakes", [])
		if not kp_list.has(kp_id):
			kp_list.append(kp_id)
		_run_state["keepsakes"] = kp_list
	var q_id: String = String(rewards.get("quote_id", ""))
	if q_id != "":
		var q_list: Array = _run_state.get("unlocked_quotes", [])
		if not q_list.has(q_id):
			q_list.append(q_id)
		_run_state["unlocked_quotes"] = q_list
	# Mark that this night's show has been attended · gates REST advancement
	var attended: Array = _run_state.get("shows_attended", [])
	var n_attended: int = int(rewards.get("night_attended", int(_run_state.get("night", 1))))
	if not attended.has(n_attended):
		attended.append(n_attended)
	_run_state["shows_attended"] = attended
	_save_state()
	_open_midway()


func _on_rest_at_booth(fey_id: String) -> void:
	# Advance night · full restore · save
	var n: int = int(_run_state.get("night", 1))
	if n < 6:
		_run_state["night"] = n + 1
	# Track which fey hosted the rest for later flavor · not gameplay
	var hosts: Array = _run_state.get("rest_hosts", [])
	hosts.append({"fey_id": fey_id, "from_night": n})
	_run_state["rest_hosts"] = hosts
	_save_state()
	_open_midway()


func _on_midway_quit() -> void:
	# Midway may set _route_to_trailer flag when leaving via the
	# trailer-adjacent cell.  Otherwise return to Gate.
	if bool(_run_state.get("_route_to_trailer", false)):
		_run_state.erase("_route_to_trailer")
		_open_trailer()
	else:
		_open_gate()


func _open_negotiation_from_midway(fey_id: String) -> void:
	# Track that this negotiation came from midway so we return there
	_run_state["_negotiation_return_to_midway"] = true
	_open_negotiation(fey_id)


func _open_negotiation(fey_id: String) -> void:
	_clear_current_scene()
	_child_scene = load(NEGOTIATION_SCENE).instantiate()
	_child_scene.quit_to_shelf.connect(_on_gate_quit)
	_child_scene.negotiation_complete.connect(_on_negotiation_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", {
			"fey_id": fey_id,
			"run_state": _run_state
		})


func _on_negotiation_complete(fey_id: String, outcome: String, mutations: Dictionary) -> void:
	# Merge mutations into run state
	if outcome == "recruited":
		var recruited: Array = _run_state.get("recruited_feys", [])
		if not recruited.has(fey_id):
			recruited.append(fey_id)
		_run_state["recruited_feys"] = recruited
		# Add checkpoint · recruited fey creates spawn node at their
		# manifestation location
		var checkpoints: Array = _run_state.get("checkpoints", [])
		if not checkpoints.has(fey_id):
			checkpoints.append(fey_id)
		_run_state["checkpoints"] = checkpoints
	# Apply court shift deltas
	for k in mutations.keys():
		var key: String = String(k)
		if key.ends_with("_delta"):
			var base_key: String = key.substr(0, key.length() - 6)
			var cur: int = int(_run_state.get(base_key, 0))
			_run_state[base_key] = cur + int(mutations[k])
		elif key == "promise_made":
			var promises: Array = _run_state.get("promises", [])
			promises.append({
				"fey_id": fey_id,
				"promise": String(mutations[k]),
				"fulfilled": false
			})
			_run_state["promises"] = promises
	_save_state()
	# Combat path · negotiation ended hostile with combat_pending
	if outcome == "hostile" and bool(mutations.get("combat_pending", false)):
		_open_combat(fey_id)
		return
	# Return to whichever scene invoked the negotiation
	if bool(_run_state.get("_negotiation_return_to_midway", false)):
		_run_state.erase("_negotiation_return_to_midway")
		_open_midway()
	else:
		_open_gate()


func _open_combat(fey_id: String) -> void:
	_clear_current_scene()
	_child_scene = load(COMBAT_SCENE).instantiate()
	_child_scene.quit.connect(_on_combat_quit)
	_child_scene.combat_complete.connect(_on_combat_complete)
	add_child(_child_scene)
	if _child_scene.has_method("boot"):
		_child_scene.call("boot", {
			"fey_id": fey_id,
			"run_state": _run_state
		})


func _on_combat_quit() -> void:
	_open_gate()


func _on_combat_complete(fey_id: String, outcome: String, mutations: Dictionary) -> void:
	# Apply mutation deltas
	for k in mutations.keys():
		var key: String = String(k)
		if key.ends_with("_delta"):
			var base_key: String = key.substr(0, key.length() - 6)
			var cur: int = int(_run_state.get(base_key, 0))
			_run_state[base_key] = cur + int(mutations[k])
	# Victory outcomes
	if outcome == "victory":
		var vanquished: Array = _run_state.get("vanquished_feys", [])
		if not vanquished.has(fey_id):
			vanquished.append(fey_id)
		_run_state["vanquished_feys"] = vanquished
		# Vanquished still opens a checkpoint · a specific bare cell
		var checkpoints: Array = _run_state.get("checkpoints", [])
		if not checkpoints.has(fey_id):
			checkpoints.append(fey_id)
		_run_state["checkpoints"] = checkpoints
	# Loss · one memory lost · route back to Gate to represent respawn
	if outcome == "loss":
		var mirrors: Array = _run_state.get("memory_mirror_state", [])
		mirrors.append({"fey_id": fey_id, "cause": "combat_loss"})
		_run_state["memory_mirror_state"] = mirrors
	_save_state()
	# Parley routes back into negotiation with the same fey
	if outcome == "parley":
		_open_negotiation(fey_id)
		return
	# Otherwise return to whichever context invoked us
	if bool(_run_state.get("_negotiation_return_to_midway", false)):
		_run_state.erase("_negotiation_return_to_midway")
		_open_midway()
	else:
		_open_gate()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			# Only the title screen escapes to the shelf.  Child scenes
			# handle their own escape.
			if _title_root != null and _child_scene == null:
				_on_back_to_shelf()
				get_viewport().set_input_as_handled()
