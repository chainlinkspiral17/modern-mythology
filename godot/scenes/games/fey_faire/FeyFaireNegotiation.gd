extends Control
## Fey Faire · negotiation scene · data-driven for any fey.
##
## boot(state) requires state to include:
##   fey_id · id of the fey being negotiated with (must exist in
##            feys.json)
##   run_state · full host run state (recruits, keepsakes, quotes,
##               promises, court alignments · used for gating and
##               success rolls)
##
## Renders the fey's manifestation, portrait placeholder, and four
## negotiation branches: OFFER · PROMISE · THREATEN · RECITE.  Each
## opens a specific sub-panel with the fey's own data pulled from
## feys.json.
##
## Emits:
##   negotiation_complete(fey_id, outcome, mutations)
##     outcome · one of "recruited" | "rebuffed" | "hostile"
##     mutations · Dictionary of state changes to merge into
##                 run_state (recruits, court shifts, promises, etc.)
##   quit_to_shelf · escape hatch (BACK)
##
## F4-compliant via add_to_group("ui").

signal negotiation_complete(fey_id: String, outcome: String, mutations: Dictionary)
signal quit_to_shelf

const FEYS_PATH := "res://resources/games/vol7/fey_faire/feys.json"

# Rocha palette
const C_BG        := Color(0.157, 0.094, 0.173, 1.0)
const C_PANEL     := Color(0.455, 0.157, 0.282, 1.0)
const C_PANEL_DIM := Color(0.28, 0.10, 0.18, 1.0)
const C_CREAM     := Color(0.957, 0.878, 0.816, 1.0)
const C_ROSE      := Color(0.878, 0.722, 0.753, 1.0)
const C_MAUVE     := Color(0.784, 0.557, 0.643, 1.0)
const C_GOLD      := Color(0.973, 0.784, 0.282, 1.0)
const C_GOLD_DIM  := Color(0.541, 0.361, 0.157, 1.0)

# Court accent colors
const C_COURT_SEELIE   := Color(0.973, 0.784, 0.282, 1.0)
const C_COURT_UNSEELIE := Color(0.541, 0.361, 0.157, 1.0)
const C_COURT_WILDFEY  := Color(0.62, 0.82, 0.55, 1.0)

var _run_state: Dictionary = {}
var _fey_id: String = ""
var _fey: Dictionary = {}
var _feys_by_id: Dictionary = {}
var _mutations: Dictionary = {}
var _panel_root: Control = null


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_to_group("ui")


func boot(state: Dictionary) -> void:
	_run_state = state.get("run_state", state)
	_fey_id = String(state.get("fey_id", ""))
	_load_feys()
	_fey = _feys_by_id.get(_fey_id, {})
	if _fey.is_empty():
		push_warning("[FeyFaireNegotiation] unknown fey_id: " + _fey_id)
		# Fall back to the first fey · scaffold safety
		if not _feys_by_id.is_empty():
			var keys := _feys_by_id.keys()
			_fey_id = String(keys[0])
			_fey = _feys_by_id[_fey_id]
	_build_frame()
	_render_main_view()


func _load_feys() -> void:
	if not FileAccess.file_exists(FEYS_PATH): return
	var f := FileAccess.open(FEYS_PATH, FileAccess.READ)
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Dictionary:
		var feys_arr: Array = (parsed as Dictionary).get("feys", [])
		for entry_v in feys_arr:
			var entry: Dictionary = entry_v
			_feys_by_id[String(entry.get("id", ""))] = entry


func _build_frame() -> void:
	var bg := ColorRect.new()
	bg.color = C_BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	# Top header: fey name + court
	var court := String(_fey.get("court", "wildfey"))
	var court_color: Color = _court_color(court)

	var header_panel := ColorRect.new()
	header_panel.color = C_PANEL_DIM
	header_panel.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header_panel.offset_top = 20
	header_panel.offset_bottom = 68
	add_child(header_panel)

	var header_label := Label.new()
	header_label.text = "· " + String(_fey.get("name", "?")).to_upper() + " ·  " + court.to_upper() + " ·  TIER " + str(int(_fey.get("tier", 1)))
	header_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header_label.add_theme_font_size_override("font_size", 18)
	header_label.add_theme_color_override("font_color", court_color)
	header_label.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header_label.offset_top = 32
	header_label.offset_bottom = 56
	add_child(header_label)


func _court_color(court: String) -> Color:
	match court:
		"seelie":   return C_COURT_SEELIE
		"unseelie": return C_COURT_UNSEELIE
		"wildfey":  return C_COURT_WILDFEY
		_: return C_GOLD


func _clear_panel() -> void:
	if _panel_root != null and is_instance_valid(_panel_root):
		_panel_root.queue_free()
	_panel_root = null


func _render_main_view() -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.offset_top = 80
	_panel_root.offset_bottom = -20
	_panel_root.offset_left = 40
	_panel_root.offset_right = -40
	add_child(_panel_root)

	# Two-column layout · left panel = manifestation description ·
	# right panel = negotiation options
	var h := HBoxContainer.new()
	h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	h.add_theme_constant_override("separation", 20)
	_panel_root.add_child(h)

	# LEFT · description
	var left := VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.add_theme_constant_override("separation", 8)
	h.add_child(left)

	var manif_panel := ColorRect.new()
	manif_panel.color = C_PANEL
	manif_panel.custom_minimum_size = Vector2(0, 4)
	manif_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.add_child(manif_panel)

	var left_content := VBoxContainer.new()
	left_content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	left_content.offset_left = 12
	left_content.offset_right = -12
	left_content.offset_top = 12
	left_content.offset_bottom = -12
	left_content.add_theme_constant_override("separation", 6)
	manif_panel.add_child(left_content)

	# Portrait · procedural from court/tier/id · authored override wins
	var portrait_row := HBoxContainer.new()
	portrait_row.add_theme_constant_override("separation", 10)
	left_content.add_child(portrait_row)

	var portrait_rect := TextureRect.new()
	portrait_rect.texture = FeyPortrait.texture(_fey, Vector2i(96, 120))
	portrait_rect.custom_minimum_size = Vector2(96, 120)
	portrait_rect.stretch_mode = TextureRect.STRETCH_KEEP
	portrait_row.add_child(portrait_rect)

	var portrait_caption := Label.new()
	portrait_caption.text = "· as they choose\n  to be seen ·"
	portrait_caption.add_theme_font_size_override("font_size", 13)
	portrait_caption.add_theme_color_override("font_color", C_GOLD_DIM)
	portrait_row.add_child(portrait_caption)

	var manif_header := Label.new()
	manif_header.text = "MANIFESTATION"
	manif_header.add_theme_font_size_override("font_size", 14)
	manif_header.add_theme_color_override("font_color", C_GOLD_DIM)
	left_content.add_child(manif_header)

	var manif_text := RichTextLabel.new()
	manif_text.bbcode_enabled = false
	manif_text.fit_content = true
	manif_text.text = String(_fey.get("manifestation", ""))
	manif_text.add_theme_font_size_override("normal_font_size", 15)
	manif_text.add_theme_color_override("default_color", C_CREAM)
	manif_text.custom_minimum_size = Vector2(0, 100)
	left_content.add_child(manif_text)

	var sep1 := Control.new()
	sep1.custom_minimum_size = Vector2(0, 6)
	left_content.add_child(sep1)

	var true_form_header := Label.new()
	true_form_header.text = "· if the glamour drops ·"
	true_form_header.add_theme_font_size_override("font_size", 14)
	true_form_header.add_theme_color_override("font_color", C_GOLD_DIM)
	left_content.add_child(true_form_header)

	var true_form_text := RichTextLabel.new()
	true_form_text.bbcode_enabled = false
	true_form_text.fit_content = true
	true_form_text.text = String(_fey.get("true_form", ""))
	true_form_text.add_theme_font_size_override("normal_font_size", 14)
	true_form_text.add_theme_color_override("default_color", C_ROSE)
	true_form_text.custom_minimum_size = Vector2(0, 60)
	left_content.add_child(true_form_text)

	var sep2 := Control.new()
	sep2.custom_minimum_size = Vector2(0, 6)
	left_content.add_child(sep2)

	var desc_header := Label.new()
	desc_header.text = "· disposition ·"
	desc_header.add_theme_font_size_override("font_size", 14)
	desc_header.add_theme_color_override("font_color", C_GOLD_DIM)
	left_content.add_child(desc_header)

	var desc_text := RichTextLabel.new()
	desc_text.bbcode_enabled = false
	desc_text.fit_content = true
	desc_text.text = String(_fey.get("description", ""))
	desc_text.add_theme_font_size_override("normal_font_size", 14)
	desc_text.add_theme_color_override("default_color", C_MAUVE)
	desc_text.custom_minimum_size = Vector2(0, 60)
	left_content.add_child(desc_text)

	# Combat quick-stats footer
	var stats: Dictionary = _fey.get("stats", {})
	var stats_lbl := Label.new()
	stats_lbl.text = "HP %s · SP %s · AP %s · speed %s · charm %s · wit %s · damage · %s · weak · %s" % [
		str(int(stats.get("hp", 0))),
		str(int(stats.get("sp", 0))),
		str(int(stats.get("ap", 0))),
		str(int(stats.get("speed", 0))),
		str(int(stats.get("charm", 0))),
		str(int(stats.get("wit", 0))),
		String(_fey.get("damage_type", "?")),
		String(_fey.get("weakness", "?"))
	]
	stats_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	stats_lbl.add_theme_font_size_override("font_size", 13)
	stats_lbl.add_theme_color_override("font_color", C_ROSE)
	left_content.add_child(stats_lbl)

	# RIGHT · negotiation branches
	var right := VBoxContainer.new()
	right.custom_minimum_size = Vector2(340, 0)
	right.size_flags_horizontal = Control.SIZE_SHRINK_END
	right.add_theme_constant_override("separation", 10)
	h.add_child(right)

	var right_header := Label.new()
	right_header.text = "· FOUR BRANCHES ·"
	right_header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	right_header.add_theme_font_size_override("font_size", 16)
	right_header.add_theme_color_override("font_color", C_GOLD)
	right.add_child(right_header)

	# Precomputed check · does the player HAVE the specific means
	# to attempt each branch?
	var can_offer: bool = true    # OFFER always attemptable (may fail)
	var can_promise: bool = true  # PROMISE always attemptable
	var can_threaten: bool = _player_knows_true_name()
	var can_recite: bool = _player_knows_recite_quote()

	_add_negotiation_button(right, "OFFER",
		String(_fey.get("prize", "")),
		can_offer, C_GOLD, _on_offer_pressed)

	_add_negotiation_button(right, "PROMISE",
		String(_fey.get("request", "")),
		can_promise, C_ROSE, _on_promise_pressed)

	_add_negotiation_button(right, "THREATEN",
		"invoke their true name",
		can_threaten, C_GOLD_DIM, _on_threaten_pressed)

	_add_negotiation_button(right, "RECITE",
		"quote " + String(_fey.get("favorite_play", "the right play")),
		can_recite, C_MAUVE, _on_recite_pressed)

	var sep3 := Control.new()
	sep3.custom_minimum_size = Vector2(0, 20)
	right.add_child(sep3)

	# Walk away / fight
	var walk := Button.new()
	walk.text = "  walk away  "
	walk.add_theme_font_size_override("font_size", 15)
	walk.pressed.connect(_on_walk_away)
	right.add_child(walk)

	var fight := Button.new()
	fight.text = "  fight instead  "
	fight.add_theme_font_size_override("font_size", 15)
	fight.pressed.connect(_on_fight_pressed)
	right.add_child(fight)

	var back := Button.new()
	back.text = "  ← back to shelf  "
	back.add_theme_font_size_override("font_size", 15)
	back.pressed.connect(_on_back)
	right.add_child(back)


func _add_negotiation_button(parent: Node, action: String, subtitle: String, enabled: bool, color: Color, callback: Callable) -> void:
	var container := VBoxContainer.new()
	container.add_theme_constant_override("separation", 2)
	parent.add_child(container)

	var btn := Button.new()
	btn.text = "  " + action + "  "
	btn.add_theme_font_size_override("font_size", 16)
	btn.add_theme_color_override("font_color", color if enabled else C_PANEL_DIM)
	btn.disabled = not enabled
	btn.pressed.connect(callback)
	container.add_child(btn)

	var subtitle_lbl := Label.new()
	subtitle_lbl.text = "  · " + subtitle + " ·  " + ("" if enabled else "(unavailable)")
	subtitle_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	subtitle_lbl.add_theme_font_size_override("font_size", 13)
	subtitle_lbl.add_theme_color_override("font_color", C_CREAM if enabled else C_PANEL_DIM)
	container.add_child(subtitle_lbl)


func _player_knows_true_name() -> bool:
	# The player knows a fey's true name if it's in their run_state's
	# known_names list.  Scaffold: always false until a specific
	# keepsake or fey grants a true name.
	var known: Array = _run_state.get("known_names", [])
	return known.has(_fey_id)


func _player_knows_recite_quote() -> bool:
	# Similar · true if the player has at least one quote in the
	# quotes_learned list that lists this fey (or its court) as an
	# affinity.  Scaffold: assume the three starter quotes.
	var learned: Array = _run_state.get("quotes_learned", ["q_fools_mortals", "q_dreams_made_on", "q_bank_thyme"])
	# Any of the starter quotes at least allow attempting a RECITE
	return not learned.is_empty()


func _on_offer_pressed() -> void:
	_render_offer_view()


func _on_promise_pressed() -> void:
	_render_promise_view()


func _on_threaten_pressed() -> void:
	_render_threaten_view()


func _on_recite_pressed() -> void:
	_render_recite_view()


func _render_offer_view() -> void:
	_render_branch_view(
		"OFFER",
		"You offer " + String(_fey.get("prize", "a gift")) + " to " + String(_fey.get("name", "the fey")) + ".",
		"if you have exactly the right prize, they will recruit",
		func() -> void:
			# Scaffold: OFFER succeeds if the player has the prize in
			# their keepsakes or their boot_inventory · always succeeds
			# for simplicity in this pass
			var kp: Array = _run_state.get("keepsakes", [])
			var has_related_kp: bool = kp.size() > 0
			if has_related_kp:
				_succeed_recruit("OFFER")
			else:
				_rebuff("OFFER · the specific item wasn't quite the one they wanted")
	)


func _render_promise_view() -> void:
	_render_branch_view(
		"PROMISE",
		"You promise: " + String(_fey.get("request", "a service")),
		"a fulfilled promise recruits · an unkept one costs you later",
		func() -> void:
			# Scaffold: PROMISE always accepted · added to promises list
			_succeed_recruit("PROMISE", {"promise_made": String(_fey.get("request", ""))})
	)


func _render_threaten_view() -> void:
	_render_branch_view(
		"THREATEN",
		"You speak the true name: '" + String(_fey.get("true_name", "?")) + "'",
		"the fey stiffens.  the name is powerful.",
		func() -> void:
			# Scaffold: threaten always recruits but adds hostility
			_succeed_recruit("THREATEN", {"disposition_delta": -1})
	)


func _render_recite_view() -> void:
	var play := String(_fey.get("favorite_play", ""))
	_render_branch_view(
		"RECITE",
		"You recite from " + (play if play != "" else "the right play") + ".",
		"a correct-fey match doubles the effect and often opens negotiation",
		func() -> void:
			# Scaffold: recite always succeeds if the fey has a
			# favorite_play (some don't, e.g. certain Wildfey)
			if play != "":
				_succeed_recruit("RECITE")
			else:
				_rebuff("RECITE · they do not respond to a written line")
	)


func _render_branch_view(title: String, prompt: String, note: String, on_confirm: Callable) -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_panel_root.offset_left = -280
	_panel_root.offset_right = 280
	_panel_root.offset_top = -120
	_panel_root.offset_bottom = 120
	add_child(_panel_root)

	var panel_bg := ColorRect.new()
	panel_bg.color = C_PANEL
	panel_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.add_child(panel_bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 20
	v.offset_right = -20
	v.offset_top = 20
	v.offset_bottom = -20
	v.add_theme_constant_override("separation", 10)
	_panel_root.add_child(v)

	var title_lbl := Label.new()
	title_lbl.text = "· " + title + " ·"
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.add_theme_font_size_override("font_size", 18)
	title_lbl.add_theme_color_override("font_color", C_GOLD)
	v.add_child(title_lbl)

	var prompt_lbl := RichTextLabel.new()
	prompt_lbl.bbcode_enabled = false
	prompt_lbl.fit_content = true
	prompt_lbl.text = prompt
	prompt_lbl.add_theme_font_size_override("normal_font_size", 15)
	prompt_lbl.add_theme_color_override("default_color", C_CREAM)
	prompt_lbl.custom_minimum_size = Vector2(0, 40)
	v.add_child(prompt_lbl)

	var note_lbl := Label.new()
	note_lbl.text = "· " + note + " ·"
	note_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	note_lbl.add_theme_font_size_override("font_size", 13)
	note_lbl.add_theme_color_override("font_color", C_ROSE)
	note_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(note_lbl)

	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	buttons.add_theme_constant_override("separation", 12)
	v.add_child(buttons)

	var confirm_btn := Button.new()
	confirm_btn.text = "  confirm  "
	confirm_btn.add_theme_font_size_override("font_size", 15)
	confirm_btn.pressed.connect(on_confirm)
	buttons.add_child(confirm_btn)

	var back_btn := Button.new()
	back_btn.text = "  ← back  "
	back_btn.add_theme_font_size_override("font_size", 15)
	back_btn.pressed.connect(_render_main_view)
	buttons.add_child(back_btn)


func _succeed_recruit(via: String, extra_mutations: Dictionary = {}) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("win_chord", 0.7)
	# Compute mutations to send back
	var muts := {
		"recruited_fey_id": _fey_id,
		"via": via,
	}
	# Merge extras
	for k in extra_mutations.keys():
		muts[String(k)] = extra_mutations[k]
	# Compute court shift · +2 seelie/unseelie/wildfey based on this
	# fey's court (simplified · the design doc has tier-scaled shifts)
	var court := String(_fey.get("court", "wildfey"))
	var court_key := "court_" + court
	muts[court_key + "_delta"] = 2
	# Named disposition · recruiting a fey means they like you.
	# Endings gate on titania/oberon/green_man/cricket dispositions,
	# and Helia's tail-flick reads per-fey disposition · feed both.
	muts[_fey_id + "_disposition_delta"] = 2
	# Court cache · the endings count unseelie recruits via this key.
	muts["fey_court_" + _fey_id] = court

	_render_result_view(
		String(_fey.get("name", "?")) + " · RECRUITED",
		"They have joined your party.  A checkpoint has opened at " + _short_manifestation() + ".",
		C_COURT_SEELIE if court == "seelie" else (C_COURT_UNSEELIE if court == "unseelie" else C_COURT_WILDFEY),
		func() -> void: negotiation_complete.emit(_fey_id, "recruited", muts)
	)


func _rebuff(reason: String) -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("pair_cold", 0.6)
	_render_result_view(
		String(_fey.get("name", "?")) + " · REBUFFED",
		reason + ".\n\nThey remain at their booth.  You may try again later.",
		C_ROSE,
		func() -> void: negotiation_complete.emit(_fey_id, "rebuffed", {})
	)


func _on_walk_away() -> void:
	negotiation_complete.emit(_fey_id, "walked_away", {})


func _on_fight_pressed() -> void:
	var sfx := get_node_or_null("/root/SFXBank")
	if sfx: sfx.play("loss_thud", 0.7)
	_render_result_view(
		String(_fey.get("name", "?")) + " · HOSTILE",
		"You have chosen combat.\n\n· they take a step back · their booth-shape flickers · you see the true form under it · the tent flaps close ·",
		C_COURT_UNSEELIE,
		func() -> void: negotiation_complete.emit(_fey_id, "hostile", {"combat_pending": true})
	)


func _render_result_view(title: String, body: String, tint: Color, on_dismiss: Callable) -> void:
	_clear_panel()
	_panel_root = Control.new()
	_panel_root.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_panel_root.offset_left = -260
	_panel_root.offset_right = 260
	_panel_root.offset_top = -100
	_panel_root.offset_bottom = 100
	add_child(_panel_root)

	var panel_bg := ColorRect.new()
	panel_bg.color = C_PANEL
	panel_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel_root.add_child(panel_bg)

	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 20
	v.offset_right = -20
	v.offset_top = 20
	v.offset_bottom = -20
	v.add_theme_constant_override("separation", 12)
	_panel_root.add_child(v)

	var title_lbl := Label.new()
	title_lbl.text = "· " + title + " ·"
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.add_theme_font_size_override("font_size", 18)
	title_lbl.add_theme_color_override("font_color", tint)
	v.add_child(title_lbl)

	var body_lbl := RichTextLabel.new()
	body_lbl.bbcode_enabled = false
	body_lbl.fit_content = true
	body_lbl.text = body
	body_lbl.add_theme_font_size_override("normal_font_size", 15)
	body_lbl.add_theme_color_override("default_color", C_CREAM)
	body_lbl.custom_minimum_size = Vector2(0, 60)
	v.add_child(body_lbl)

	var dismiss_btn := Button.new()
	dismiss_btn.text = "  continue  →  "
	dismiss_btn.add_theme_font_size_override("font_size", 15)
	dismiss_btn.pressed.connect(on_dismiss)
	v.add_child(dismiss_btn)


func _short_manifestation() -> String:
	var m: String = String(_fey.get("manifestation", ""))
	if m == "": return "their booth"
	# First sentence up to the first period.
	var idx: int = m.find(" · ")
	if idx < 0: idx = m.find(".")
	if idx <= 0: return m.substr(0, min(m.length(), 60))
	return m.substr(0, idx)


func _on_back() -> void:
	quit_to_shelf.emit()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		var kev: InputEventKey = event
		if kev.keycode == KEY_ESCAPE:
			_on_back()
			get_viewport().set_input_as_handled()
