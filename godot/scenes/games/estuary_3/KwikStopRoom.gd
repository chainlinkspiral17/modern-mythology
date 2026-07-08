extends Control
## Act 1 controller · one-room SCUMM interior + 12-night shift loop.
##
## Loads:  res://resources/games/vol7/estuary_3/act1_kwik_stop.json
##
## Contract with Estuary3Host:
##   - Host instantiates KwikStopRoom, then calls
##     `boot(host_state: Dictionary)` passing `night_index` and the
##     accumulated `register_tape` array. The room reads the current
##     night from host_state.night_index.
##   - When a night's fifteen turns complete, KwikStopRoom emits
##     `night_finished(summary: Dictionary)`. Host advances the
##     night_index, saves, and re-boots the room. Repeat until
##     night 12.
##   - On night 12 turn 14 the 2 AM customer opens the backroom
##     door. KwikStopRoom emits `act1_finished(register_tape: Array)`.
##     Host transitions to act2_estuary.
##
## This commit scaffolds the playable core: room render, verb-target
## composition, turn tick with pause, customer arrival + phone
## ring log lines, night intro/outro narration, backroom transition
## on night 12 turn 14. Deferred to follow-up commits: customer
## serving mini-game (turns processed, tip jar arithmetic), cooler
## restock sub-actions, radio tuning sub-actions with per-night
## program playback, register-tape rich rendering.
##
## F4-compliant via add_to_group("ui") on the root Control.

signal night_finished(summary: Dictionary)
signal act1_finished(register_tape: Array)
signal quit_to_shelf

const ACT1_JSON := "res://resources/games/vol7/estuary_3/act1_kwik_stop.json"

# Real-time seconds per in-fiction turn. 40s per _EXISTING_ design;
# adjustable at runtime via `set_turn_seconds` for playtesting.
const DEFAULT_TURN_SECONDS := 40.0

# Layout constants
const ROOM_W := 800
const ROOM_H := 460
const VERB_BAR_H := 42
const LOG_W := 320

const C_BG_ROOM   := Color(0.06, 0.09, 0.11)
const C_WALL      := Color(0.30, 0.36, 0.32)
const C_FLOOR     := Color(0.42, 0.38, 0.28)
const C_FLUOR     := Color(0.86, 0.90, 0.72, 0.20)     # overlay tint
const C_INTERACT  := Color(0.62, 0.55, 0.42, 0.95)
const C_INT_HOVER := Color(0.86, 0.78, 0.42, 1.00)
const C_ACCENT    := Color(0.78, 0.66, 0.29, 1.00)
const C_TXT       := Color(0.83, 0.79, 0.69, 1.00)
const C_TXT_DIM   := Color(0.50, 0.47, 0.38, 1.00)
const C_VERB_BG   := Color(0.10, 0.12, 0.14, 1.00)
const C_VERB_SEL  := Color(0.24, 0.28, 0.20, 1.00)

# Loaded data
var _def: Dictionary = {}
var _verbs: Array = []          # {id, label, hotkey}
var _interactables: Array = []  # {id, label, pos_xy, responses, sub_actions?, locked_until_night_12_turn_14?}
var _nights: Array = []
var _phone_rings: Dictionary = {}
var _customers_meta: Dictionary = {}

# Session state
var _night_index: int = 0
var _turn: int = 0                       # 0..15; 0 = "pre-turn 1", 15 = shift-end
var _selected_verb: String = ""
var _register_tape: Array = []           # accumulated across nights
var _turn_timer: float = 0.0
var _paused: bool = false
var _customers_arrived_this_turn: Array = []
var _pending_customer_queue: Array = []

# UI refs
var _log_box: RichTextLabel = null
var _turn_label: Label = null
var _night_label: Label = null
var _verb_buttons: Dictionary = {}
var _room_container: Control = null
var _pause_btn: Button = null
var _advance_btn: Button = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")
	set_process(true)
	_load_def()
	_build_ui()


func boot(host_state: Dictionary) -> void:
	_night_index = int(host_state.get("night_index", 0))
	_register_tape = host_state.get("register_tape", []) as Array
	AudioMgr.play_bgm("res://assets/audio/bgm/e3/act1_kwik_stop_hum.wav")
	_start_night()


# ─── Data load ───────────────────────────────────────────────────

func _load_def() -> void:
	if not FileAccess.file_exists(ACT1_JSON):
		push_warning("[KwikStopRoom] missing %s" % ACT1_JSON)
		return
	var f := FileAccess.open(ACT1_JSON, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		push_warning("[KwikStopRoom] %s not a JSON object" % ACT1_JSON)
		return
	_def = parsed
	_verbs = _def.get("verbs", [])
	_interactables = _def.get("interactables", [])
	_nights = _def.get("nights", [])
	_phone_rings = _def.get("phone_rings", {})
	_customers_meta = _def.get("customers", {})


# ─── UI build ────────────────────────────────────────────────────

func _build_ui() -> void:
	# Full-screen dark backdrop.
	var bg := ColorRect.new()
	bg.color = C_BG_ROOM
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Top status bar.
	var top := HBoxContainer.new()
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 16
	top.offset_right = -16
	top.offset_top = 8
	top.offset_bottom = 32
	top.add_theme_constant_override("separation", 16)
	add_child(top)

	_night_label = Label.new()
	_night_label.add_theme_font_size_override("font_size", 12)
	_night_label.add_theme_color_override("font_color", C_ACCENT)
	top.add_child(_night_label)

	_turn_label = Label.new()
	_turn_label.add_theme_font_size_override("font_size", 12)
	_turn_label.add_theme_color_override("font_color", C_TXT)
	top.add_child(_turn_label)

	# Spacer
	var s := Control.new()
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(s)

	_advance_btn = Button.new()
	_advance_btn.text = "  ADVANCE  "
	_advance_btn.pressed.connect(_on_advance_pressed)
	top.add_child(_advance_btn)

	_pause_btn = Button.new()
	_pause_btn.text = "  ⏸  "
	_pause_btn.toggle_mode = true
	_pause_btn.toggled.connect(func(p: bool) -> void:
		_paused = p
		_pause_btn.text = "  ▶  " if p else "  ⏸  ")
	top.add_child(_pause_btn)

	var quit := Button.new()
	quit.text = "  ✕  BACK  "
	quit.pressed.connect(func() -> void: quit_to_shelf.emit())
	top.add_child(quit)

	# Main layout: room on the left, log column on the right,
	# verb bar along the bottom of the room.
	var main := HBoxContainer.new()
	main.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	main.offset_left = 16
	main.offset_right = -16
	main.offset_top = 40
	main.offset_bottom = -8
	main.add_theme_constant_override("separation", 12)
	add_child(main)

	# Room + verb bar column
	var left := VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.size_flags_stretch_ratio = 2.5
	left.add_theme_constant_override("separation", 4)
	main.add_child(left)

	_room_container = Control.new()
	_room_container.custom_minimum_size = Vector2(ROOM_W, ROOM_H)
	_room_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_room_container.mouse_filter = Control.MOUSE_FILTER_PASS
	left.add_child(_room_container)
	_render_room()

	# Verb bar
	var verb_bar := HBoxContainer.new()
	verb_bar.custom_minimum_size = Vector2(0, VERB_BAR_H)
	verb_bar.add_theme_constant_override("separation", 4)
	left.add_child(verb_bar)
	for v_var in _verbs:
		var v: Dictionary = v_var
		var b := Button.new()
		b.text = " " + String(v["label"]).to_upper() + " "
		b.toggle_mode = true
		b.focus_mode = Control.FOCUS_NONE
		var sb := StyleBoxFlat.new()
		sb.bg_color = C_VERB_BG
		sb.border_color = C_TXT_DIM
		sb.set_border_width_all(1)
		b.add_theme_stylebox_override("normal", sb)
		var sb_hover := sb.duplicate()
		sb_hover.bg_color = C_VERB_SEL
		sb_hover.border_color = C_ACCENT
		b.add_theme_stylebox_override("pressed", sb_hover)
		b.add_theme_stylebox_override("hover", sb_hover)
		b.add_theme_color_override("font_color", C_TXT)
		b.add_theme_color_override("font_color_pressed", C_ACCENT)
		b.add_theme_font_size_override("font_size", 11)
		var vid: String = String(v["id"])
		b.pressed.connect(func() -> void: _select_verb(vid))
		verb_bar.add_child(b)
		_verb_buttons[vid] = b

	# Log column
	var right := VBoxContainer.new()
	right.custom_minimum_size = Vector2(LOG_W, 0)
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.size_flags_stretch_ratio = 1.0
	right.add_theme_constant_override("separation", 4)
	main.add_child(right)

	var log_hdr := Label.new()
	log_hdr.text = "REGISTER TAPE / SHIFT LOG"
	log_hdr.add_theme_font_size_override("font_size", 10)
	log_hdr.add_theme_color_override("font_color", C_ACCENT)
	right.add_child(log_hdr)

	_log_box = RichTextLabel.new()
	_log_box.bbcode_enabled = true
	_log_box.scroll_following = true
	_log_box.fit_content = false
	_log_box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_log_box.add_theme_font_size_override("normal_font_size", 10)
	_log_box.add_theme_color_override("default_color", C_TXT)
	right.add_child(_log_box)


func _render_room() -> void:
	# Clear
	for c in _room_container.get_children():
		c.queue_free()

	# Wall + floor bands
	var wall := ColorRect.new()
	wall.color = C_WALL
	wall.set_anchors_preset(Control.PRESET_TOP_WIDE)
	wall.offset_bottom = int(ROOM_H * 0.6)
	_room_container.add_child(wall)

	var floor := ColorRect.new()
	floor.color = C_FLOOR
	floor.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	floor.offset_top = -int(ROOM_H * 0.4)
	_room_container.add_child(floor)

	# Fluorescent tint overlay (a subtle warm haze across the wall).
	var haze := ColorRect.new()
	haze.color = C_FLUOR
	haze.set_anchors_preset(Control.PRESET_TOP_WIDE)
	haze.offset_bottom = int(ROOM_H * 0.35)
	_room_container.add_child(haze)

	# Interactables as clickable panels at pos_xy.
	for i_var in _interactables:
		var i: Dictionary = i_var
		var pos: Vector2 = _get_pos(i)
		var panel := Panel.new()
		panel.custom_minimum_size = Vector2(72, 40)
		panel.position = Vector2(pos.x - 36, pos.y - 20)
		panel.mouse_filter = Control.MOUSE_FILTER_STOP
		var sb := StyleBoxFlat.new()
		sb.bg_color = C_INTERACT
		sb.border_color = Color(C_INTERACT.r * 0.6, C_INTERACT.g * 0.6, C_INTERACT.b * 0.6, 1.0)
		sb.set_border_width_all(1)
		sb.set_corner_radius_all(3)
		panel.add_theme_stylebox_override("panel", sb)

		var lbl := Label.new()
		lbl.text = String(i.get("label", i["id"]))
		lbl.add_theme_font_size_override("font_size", 10)
		lbl.add_theme_color_override("font_color", Color(0.10, 0.09, 0.06, 1))
		lbl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		panel.add_child(lbl)

		var iid: String = String(i["id"])
		panel.mouse_entered.connect(func() -> void:
			sb.border_color = C_INT_HOVER)
		panel.mouse_exited.connect(func() -> void:
			sb.border_color = Color(C_INTERACT.r * 0.6, C_INTERACT.g * 0.6, C_INTERACT.b * 0.6, 1.0))
		panel.gui_input.connect(func(ev: InputEvent) -> void:
			if ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed:
				_on_interactable_click(iid))
		_room_container.add_child(panel)


func _get_pos(interactable: Dictionary) -> Vector2:
	var xy: Array = interactable.get("pos_xy", [ROOM_W / 2, ROOM_H / 2])
	# Author coords are 0..800 x 0..460 approx; render as-is scaled
	# to the room container's actual size at runtime. For now assume
	# the container is at least ROOM_W x ROOM_H.
	if xy.size() >= 2:
		return Vector2(float(xy[0]), float(xy[1]))
	return Vector2(ROOM_W / 2, ROOM_H / 2)


# ─── Session flow ────────────────────────────────────────────────

func _start_night() -> void:
	if _night_index < 0 or _night_index >= _nights.size():
		push_warning("[KwikStopRoom] night_index %d out of range" % _night_index)
		return
	_turn = 0
	_turn_timer = 0.0
	_paused = false
	_selected_verb = ""
	_customers_arrived_this_turn.clear()
	_pending_customer_queue.clear()
	var night: Dictionary = _nights[_night_index]
	_night_label.text = String(night.get("date_label", "Night %d" % (_night_index + 1)))
	_update_turn_label()
	# Print night intro.
	for line in night.get("intro_narration", []):
		_log_line(String(line), "#c8a842", true)
	_log_line("", "", false)
	# Print seasonal texture note if this is night 1 or a phase-change night.
	if _night_index == 0 or _night_index == 3 or _night_index == 7 or _night_index == 11:
		var seasonal: Array = _def.get("room", {}).get("seasonal_texture_notes", [])
		if _night_index / 3 < seasonal.size():
			_log_line("[i]" + String(seasonal[_night_index / 3]) + "[/i]", "#7c8480", false)
	_log_line("", "", false)
	# Radio program summary for this night (log-only, no tuning UI yet).
	var radio_programs: Array = _def.get("radio_programs", [])
	if _night_index < radio_programs.size():
		var rp: Dictionary = radio_programs[_night_index]
		_log_line("[i]radio tonight — 88.9: %s · 1150 AM: %s · 1600 AM: %s[/i]" % [
			String(rp.get("889_npr", "?")),
			String(rp.get("1150_fishing", "?")),
			String(rp.get("1600_static", "?"))
			], "#5c6a56", false)
		_log_line("", "", false)


func _tick_turn() -> void:
	_turn += 1
	_update_turn_label()
	_customers_arrived_this_turn.clear()
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("turn_tick", 0.55)
	# The 1600 AM static voice.  Fires at ~turn 7 (in-fiction 3:14
	# AM) on nights 5 and 12.  Night 12 is 'sam.'; night 5 is the
	# half-heard forerunner.
	if _turn == 7 and sfx:
		if _night_index == 4:
			sfx.play("radio_1600_static_voice_night_5", 0.75)
		elif _night_index == 11:
			sfx.play("radio_1600_static_voice_night_12_sam", 0.9)
	# Customer arrivals for this turn.
	var night: Dictionary = _nights[_night_index]
	for entry_var in night.get("customer_schedule", []):
		var entry: Dictionary = entry_var
		if int(entry.get("turn", -1)) == _turn:
			_handle_customer_arrival(entry)
	# Phone rings for this turn (three phone-ring pools each with per-
	# night bodies; only Jules/wrong-number-Ines/nobody carry bodies).
	_maybe_ring_phone()
	# Backroom transition trigger.
	if _night_index == 11 and _turn == 14:
		_fire_backroom_transition()
		return
	# End of shift.
	if _turn >= 15:
		_end_night()
		return


func _handle_customer_arrival(entry: Dictionary) -> void:
	var cust_id: String = String(entry.get("customer", ""))
	if cust_id == "" or cust_id == "TOURIST":
		# Turn-specific tourist beats live in def.tourists indexed by night.
		var tourist_entry := _find_tourist_for_night()
		if not tourist_entry.is_empty():
			_log_line("[b]A tourist arrives.[/b]  [i]%s[/i]" % String(tourist_entry.get("line", "")), "#a89860", false)
			_log_line("[color=#7c8480][i]%s[/i][/color]" % String(tourist_entry.get("notes", "")), "#7c8480", false)
			_register_tape.append({"night": _night_index + 1, "turn": _turn, "who": "tourist"})
		return
	# Special transition-triggering customer.
	if cust_id == "the_2am_customer_stands_up":
		_fire_backroom_transition()
		return
	var cust: Dictionary = _customers_meta.get(cust_id, {})
	var display: String = String(entry.get("customer", cust_id))
	if cust.has("display_name"):
		display = String(cust["display_name"])
	var line: String = String(entry.get("line_override", ""))
	if line == "":
		line = _pick_default_customer_line(cust_id)
	if line != "":
		_log_line("[b]%s:[/b]  '%s'" % [display, line], "#c8a842", false)
	else:
		_log_line("[i]%s enters.[/i]" % display, "#a89860", false)
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("customer_bell", 0.6)
	# Per-arrival narration flag (kid-on-a-bike, other-clerk, aandahl arcs).
	_maybe_fire_night_arc_beat(cust_id, entry)
	_register_tape.append({
		"night": _night_index + 1,
		"turn": _turn,
		"who": cust_id,
	})


func _pick_default_customer_line(cust_id: String) -> String:
	# The customers table has type-conditional default_wants but no
	# stock lines. Use minimal placeholders for the recurring types.
	match cust_id:
		"mr_aandahl":         return "Same as always, Sam."
		"the_trucker":        return "Just coffee and a six."
		"the_other_clerk":    return "You seen the moon tonight?"
		_:                    return ""


func _maybe_fire_night_arc_beat(cust_id: String, entry: Dictionary) -> void:
	var night: Dictionary = _nights[_night_index]
	# The night-specific set-piece text lives on the night dict as
	# keys like `kid_on_a_bike_speaks_first_time`, `aandahl_scratcher_
	# result_line`, `aandahl_lottery_landing`, `night_12_customer_note`.
	# Fire once per arrival on that night that matches the key stem.
	var stem_map := {
		"the_kid_on_a_bike":    ["kid_on_a_bike_speaks_first_time", "kid_on_a_bike_final_visit"],
		"mr_aandahl":           ["aandahl_scratcher_result_line", "aandahl_scratcher_check", "aandahl_scratcher_lottery_arc_note", "aandahl_lottery_landing"],
		"the_2am_customer":     ["backroom_transition_narration"],
	}
	if not stem_map.has(cust_id):
		return
	for key in stem_map[cust_id]:
		if night.has(key):
			_log_line("[i]%s[/i]" % String(night[key]), "#86b8b8", false)


func _find_tourist_for_night() -> Dictionary:
	for t_var in _def.get("tourists", []):
		var t: Dictionary = t_var
		if int(t.get("night", -1)) == _night_index + 1:
			return t
	return {}


func _maybe_ring_phone() -> void:
	# Determine which phone-pool fires on this night, if any, and
	# whether _turn matches an internal per-night ring schedule.
	# The JSON's phone_rings.<pool>.nights[] specifies which nights;
	# per the design intent, the ring fires around turns 3/6/9/13
	# depending on pool.
	var night_num: int = _night_index + 1
	for pool_key in ["manager_jules", "ines_wrong_number", "nobody_call"]:
		var pool: Dictionary = _phone_rings.get(pool_key, {})
		if not (pool.get("nights", []) as Array).has(night_num):
			continue
		# Fire on preset turn per pool convention.
		var target_turn: int = _phone_ring_turn(pool_key, night_num)
		if _turn != target_turn:
			continue
		var body_key: String = "night_%d_body" % night_num
		var body: String = String(pool.get(body_key, ""))
		if body == "":
			continue
		_log_line("[b]*** phone ***[/b]  [i]%s[/i]" % body, "#6a86b8", false)
		var sfx := get_node_or_null("/root/SFXBank")
		if sfx: sfx.play("phone_ring", 0.85)


func _phone_ring_turn(pool_key: String, night_num: int) -> int:
	# The JSON puts rings on turns 3 (Jules), 6 (Ines), 9 (nobody),
	# 13 (Jules again). Simpler mapping: Jules odd, Ines even, nobody
	# 3-cycle.
	match pool_key:
		"manager_jules":     return 3 if night_num % 2 == 1 else 13
		"ines_wrong_number": return 6
		"nobody_call":       return 9
		_:                   return -1


func _fire_backroom_transition() -> void:
	var night: Dictionary = _nights[_night_index]
	var text: String = String(night.get("backroom_transition_narration", ""))
	if text == "":
		text = "The 2 AM customer stands up. He walks past the counter. He opens the backroom door. The door was never locked."
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx:
		# Chair scrape + three footsteps as he stands and walks.
		sfx.play("2am_customer_stands_up", 0.85)
		# Backroom door opens after the walk · slight delay so the
		# footsteps play out first.
		get_tree().create_timer(1.5).timeout.connect(func() -> void:
			sfx.play("door_open", 0.85))
	_log_line("", "", false)
	_log_line("[b][color=#e8c060]═══ BACKROOM DOOR OPENED ═══[/color][/b]", "#e8c060", false)
	_log_line("[i]%s[/i]" % text, "#e8c060", false)
	_log_line("", "", false)
	_log_line("[b][color=#7cffb0]Act 2 · THE ESTUARY begins.[/color][/b]", "#7cffb0", false)
	_paused = true
	# Fire the transition signal after a beat.
	get_tree().create_timer(0.5).timeout.connect(func() -> void: act1_finished.emit(_register_tape))


func _end_night() -> void:
	# Print outro narration.
	var night: Dictionary = _nights[_night_index]
	var outro: String = String(night.get("outro_narration", ""))
	if outro != "":
		_log_line("", "", false)
		_log_line("[i]%s[/i]" % outro, "#a89860", false)
	_log_line("", "", false)
	# Print shift-end summary.
	var summary_template: String = String(_def.get("shift_end_summary_template", ""))
	var served: int = 0
	for entry_var in _register_tape:
		var entry: Dictionary = entry_var
		if int(entry.get("night", -1)) == _night_index + 1:
			served += 1
	_log_line("[b]SHIFT %d · CUSTOMERS SERVED: %d[/b]" % [_night_index + 1, served], "#c8a842", false)
	_log_line("", "", false)
	_paused = true
	# Show a "next night" button.
	if _night_index < 11:
		var next_btn := Button.new()
		next_btn.text = "  → NIGHT %d  " % (_night_index + 2)
		next_btn.pressed.connect(func() -> void:
			night_finished.emit({
				"night_completed": _night_index + 1,
				"register_tape": _register_tape.duplicate(),
			})
			_night_index += 1
			next_btn.queue_free()
			_start_night())
		next_btn.set_anchors_preset(Control.PRESET_CENTER)
		next_btn.position -= Vector2(60, 0)
		add_child(next_btn)


# ─── Verb-target composition ─────────────────────────────────────

func _select_verb(vid: String) -> void:
	_selected_verb = vid
	for k in _verb_buttons.keys():
		var b: Button = _verb_buttons[k]
		b.button_pressed = (String(k) == vid)
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("verb_select", 0.7)


func _on_interactable_click(iid: String) -> void:
	var target: Dictionary = _find_interactable(iid)
	if target.is_empty():
		return
	# The backroom door is locked until night 12 turn 14.
	if bool(target.get("locked_until_night_12_turn_14", false)):
		if not (_night_index == 11 and _turn >= 14):
			_log_line("[i]The backroom door is locked.[/i]", "#7c8480", false)
			return
	var verb: String = _selected_verb if _selected_verb != "" else "look"
	var responses: Dictionary = target.get("responses", {})
	var response: String = String(responses.get(verb, ""))
	if response == "":
		# Fall back to the LOOK response if the specific verb has none.
		response = String(responses.get("look", "You %s the %s." % [verb, String(target.get("label", iid))]))
	_log_line("[color=#7c8480]> %s the %s.[/color]" % [verb, String(target.get("label", iid))], "#7c8480", false)
	_log_line(response, "#c8c8c8", false)
	# Reset selected verb after use, SCUMM-style.
	_selected_verb = ""
	for k in _verb_buttons.keys():
		(_verb_buttons[k] as Button).button_pressed = false


func _find_interactable(iid: String) -> Dictionary:
	for i_var in _interactables:
		var i: Dictionary = i_var
		if String(i.get("id", "")) == iid:
			return i
	return {}


func _on_advance_pressed() -> void:
	_tick_turn()


# ─── Frame process ───────────────────────────────────────────────

var _turn_seconds: float = DEFAULT_TURN_SECONDS


func set_turn_seconds(v: float) -> void:
	_turn_seconds = max(1.0, v)


func _process(dt: float) -> void:
	if _paused: return
	if _turn >= 15: return
	_turn_timer += dt
	if _turn_timer >= _turn_seconds:
		_turn_timer = 0.0
		_tick_turn()


# ─── Utilities ───────────────────────────────────────────────────

func _log_line(text: String, color_hex: String, is_header: bool) -> void:
	if _log_box == null: return
	if text == "":
		_log_box.append_text("\n")
		return
	if color_hex != "":
		_log_box.append_text("[color=%s]%s[/color]\n" % [color_hex, text])
	else:
		_log_box.append_text(text + "\n")


func _update_turn_label() -> void:
	if _turn_label == null: return
	# Clock: 02:14 + turn * 12 min ≈ 3-hour shift over 15 turns.
	var minutes: int = 134 + _turn * 12
	var hh: int = int(minutes / 60)
	var mm: int = int(minutes % 60)
	_turn_label.text = "  turn %d / 15  ·  clock %02d:%02d" % [_turn, hh, mm]
